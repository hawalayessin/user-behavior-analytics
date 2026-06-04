"""
MCP Agent Service — DigMaco Analytics
======================================
Implements a tool-calling agentic loop
using Google Gemini Function Calling.

The agent autonomously decides which
analytical tools to call based on the
report type requested, then synthesizes
the results into structured French insights.

Architecture:
  Report request
      ↓
  Gemini receives task + available tools
      ↓
  Gemini calls tools (SQL queries)
      ↓
  Tools return real analytics_db data
      ↓
  Gemini writes insights from real data
      ↓
  Structured dict returned to PDF service
"""
from __future__ import annotations

import json
import logging
import os
import random
import threading
import time
import warnings
from datetime import date
from typing import Any

from google import genai as google_genai
from google.genai import types as google_genai_types
from pydantic import BaseModel

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
from sqlalchemy.orm import Session

from app.services.insight_cache_service import (
    get_cached_insights,
    save_insights_to_cache,
)

logger = logging.getLogger("uvicorn.error")

MCP_GEMINI_MODEL = os.getenv("MCP_GEMINI_MODEL", "gemini-2.5-flash")
MCP_GEMINI_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "MCP_GEMINI_FALLBACK_MODELS",
        "gemini-1.5-flash-latest,gemini-1.5-flash-8b",
    ).split(",")
    if model.strip()
]
MCP_GEMINI_MIN_INTERVAL_SECONDS = float(
    os.getenv("MCP_GEMINI_MIN_INTERVAL_SECONDS", "15")
)
MCP_GEMINI_MAX_RETRIES = int(os.getenv("MCP_GEMINI_MAX_RETRIES", "3"))
MCP_GEMINI_RETRY_BASE_SECONDS = float(
    os.getenv("MCP_GEMINI_RETRY_BASE_SECONDS", "8")
)
FREE_TIER_DAILY_LIMIT = int(os.getenv("MCP_GEMINI_DAILY_LIMIT", "15"))
_gemini_rate_lock = threading.Lock()
_last_gemini_call_at = 0.0
_daily_counter: dict[str, int] = {}
_counter_lock = threading.Lock()


class MCPInsightsResponse(BaseModel):
    summary: str
    churn: str
    segments: str
    anomalies: str
    campaigns: str
    recommendations: str


# ─── Tool definitions ────────────────────────────

# These are exposed to Gemini as callable tools.
# Each tool maps to a real SQL function in
# report_data_service.py.
# Gemini reads the description to decide
# when and why to call each tool.

REPORT_TOOLS = [
    genai.protos.Tool(
        function_declarations=[

            genai.protos.FunctionDeclaration(
                name="get_global_kpis",
                description=(
                    "Récupère les KPIs globaux "
                    "depuis analytics_db : nombre "
                    "d'abonnés actifs, taux de churn "
                    "global, ARPU moyen, taux de "
                    "conversion essai/payant, "
                    "rétention D7, nombre d'abonnés "
                    "à risque élevé identifiés par "
                    "le modèle ML. "
                    "Appeler en premier dans tout "
                    "type de rapport."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "period": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description=(
                                "Période d'analyse, "
                                "ex: 'septembre-octobre 2025'"
                            ),
                        )
                    },
                    required=[],
                ),
            ),

            genai.protos.FunctionDeclaration(
                name="get_churn_analysis",
                description=(
                    "Récupère l'analyse détaillée "
                    "du churn : taux de churn "
                    "global (3.7%), taux de churn "
                    "trial (63.5%), répartition "
                    "churn technique vs volontaire, "
                    "durée de vie moyenne des abonnés. "
                    "Appeler pour les rapports de "
                    "type churn, full ou ai_segmentation."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),

            genai.protos.FunctionDeclaration(
                name="get_segments",
                description=(
                    "Récupère les 4 segments "
                    "comportementaux K-Means : "
                    "Power Users (2.2%, ARPU 24.5 TND), "
                    "Loyaux Réguliers (2.4%, ARPU 8.3), "
                    "Occasionnels (3.4%, ARPU 3.5), "
                    "Trial Only (92.1%, ARPU 0). "
                    "Appeler pour les rapports de "
                    "type ai_segmentation ou full."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),

            genai.protos.FunctionDeclaration(
                name="get_anomalies",
                description=(
                    "Récupère les anomalies "
                    "statistiques détectées par "
                    "l'algorithme Z-Score sur "
                    "une fenêtre glissante de "
                    "14 jours. Retourne la liste "
                    "des anomalies avec leur "
                    "sévérité (MEDIUM/HIGH/CRITICAL) "
                    "et la métrique concernée. "
                    "Si aucune anomalie, retourne "
                    "une liste vide. "
                    "Appeler pour tout type de rapport."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "severity_min": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description=(
                                "Sévérité minimale : "
                                "MEDIUM, HIGH ou CRITICAL"
                            ),
                        )
                    },
                    required=[],
                ),
            ),

            genai.protos.FunctionDeclaration(
                name="get_campaign_performance",
                description=(
                    "Récupère les métriques des "
                    "campagnes bulk SMS : nombre "
                    "total de campagnes, ROI moyen, "
                    "taux de conversion attribué "
                    "aux campagnes. "
                    "Appeler pour les rapports "
                    "incluant les campagnes SMS."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),

            genai.protos.FunctionDeclaration(
                name="get_retention_cohorts",
                description=(
                    "Récupère les taux de rétention "
                    "par cohorte depuis MART_COHORTS : "
                    "rétention D7, D14, D30 "
                    "agrégés sur tous les services. "
                    "Appeler pour les rapports "
                    "incluant la rétention."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),

        ]
    )
]


# ─── Tool dispatcher ─────────────────────────────

def _dispatch_tool(
    name: str,
    args: dict[str, Any],
    db: Session,
) -> dict[str, Any]:
    """
    Executes the tool requested by Gemini.
    Maps tool names to report_data_service
    functions and returns real SQL results.
    """
    from app.services.report_data_service import (
        fetch_kpis,
        fetch_churn_data,
        fetch_segments,
        fetch_anomalies,
        fetch_campaign_data,
        fetch_retention_cohorts,
    )

    # Adapt fetch_retention_cohorts call
    # if it doesn't exist yet — add below

    dispatch: dict[str, Any] = {
        "get_global_kpis":         fetch_kpis,
        "get_churn_analysis":      fetch_churn_data,
        "get_segments":            fetch_segments,
        "get_anomalies":           fetch_anomalies,
        "get_campaign_performance": fetch_campaign_data,
        "get_retention_cohorts":   fetch_retention_cohorts,
    }

    fn = dispatch.get(name)
    if fn is None:
        logger.warning(
            "Unknown tool called by Gemini: %s", name
        )
        return {
            "error": f"Tool '{name}' non disponible.",
            "available_tools": list(dispatch.keys()),
        }

    try:
        result = fn(db)
        logger.info(
            "Tool %s executed successfully", name
        )
        return result if result else {}
    except Exception as exc:
        logger.error(
            "Tool %s failed: %s", name, str(exc)
        )
        return {
            "error": str(exc),
            "tool": name,
        }


# ─── System prompt builder ───────────────────────

def _build_system_prompt(
    report_type: str,
    services: list[str],
    period: str,
) -> str:
    """
    Builds the system instruction for Gemini.
    Adapts the mission based on report type.
    """

    type_guidance = {
        "executive": (
            "Concentre-toi sur les KPIs globaux, "
            "les tendances générales et les "
            "3 priorités stratégiques principales."
        ),
        "churn": (
            "Concentre-toi sur l'analyse détaillée "
            "du churn : causes, segmentation "
            "technique vs volontaire, cohortes "
            "de rétention et recommandations "
            "de rétention ciblées."
        ),
        "ai_segmentation": (
            "Concentre-toi sur la segmentation "
            "K-Means, les profils comportementaux "
            "des 4 segments, le taux de conversion "
            "et les stratégies différenciées."
        ),
        "full": (
            "Couvre tous les aspects : KPIs, churn, "
            "segmentation, campagnes, anomalies "
            "et recommandations actionnables."
        ),
    }

    guidance = type_guidance.get(
        report_type,
        type_guidance["full"],
    )

    # Tools to prioritize by report type
    tool_priority = {
        "executive": (
            "Appelle get_global_kpis en premier, "
            "puis get_anomalies."
        ),
        "churn": (
            "Appelle get_churn_analysis et "
            "get_retention_cohorts en priorité."
        ),
        "ai_segmentation": (
            "Appelle get_segments et "
            "get_global_kpis en priorité."
        ),
        "full": (
            "Appelle tous les tools disponibles "
            "avant de rédiger."
        ),
    }

    priority = tool_priority.get(
        report_type,
        tool_priority["full"],
    )

    # Legacy agentic prompt builder kept for reference.
    return f"""
Tu es un expert en Business Intelligence
pour les services numÃ©riques Ã  abonnement
USSD/SMS de Tunisie Telecom.

Contexte :
  Entreprise : DigMaco
  Services analysÃ©s : {', '.join(services)}
  PÃ©riode : {period}
  Type de rapport : {report_type}

Mission : {guidance}

Protocole obligatoire :
1. {priority}
2. Appelle MINIMUM 3 tools diffÃ©rents
   avant de rÃ©diger quoi que ce soit.
3. Base-toi UNIQUEMENT sur les donnÃ©es
   retournÃ©es par les tools.
4. Quand tu as suffisamment de donnÃ©es,
   gÃ©nÃ¨re le rapport final en JSON pur.

Format de sortie final attendu
(JSON uniquement, sans markdown) :
{{
  "summary": "RÃ©sumÃ© exÃ©cutif 3 paragraphes",
  "churn": "Analyse churn 2 paragraphes",
  "segments": "Analyse segmentation 2 paragraphes",
  "anomalies": "SynthÃ¨se anomalies 1 paragraphe",
  "campaigns": "Performance campagnes 1 paragraphe",
  "recommendations": "3 recommandations actionnables numÃ©rotÃ©es"
}}

Langue : franÃ§ais professionnel uniquement.
Format : texte brut sans markdown dans les valeurs.
Longueur totale : 400 Ã  550 mots.
    """.strip()

    kpis = tool_results.get("get_global_kpis", {}) or {}
    churn = tool_results.get("get_churn_analysis", {}) or {}
    segments = tool_results.get("get_segments", {}) or {}
    anomalies = tool_results.get("get_anomalies", []) or []
    campaigns = tool_results.get("get_campaign_performance", {}) or {}
    retention = tool_results.get("get_retention_cohorts", {}) or {}
    anomaly_count = len(anomalies) if isinstance(anomalies, list) else 0
    data_summary = (
        f"KPIs: actifs={kpis.get('active_users', 0)}, subs={kpis.get('active_subscriptions', 0)}, "
        f"churn={kpis.get('churn_rate', 0)}%, conv={kpis.get('conversion_rate', 0)}%, "
        f"ARPU={kpis.get('arpu', 0)} TND, highRisk={kpis.get('high_risk_users', 0)}.\n"
        f"Churn: global={churn.get('global_churn_rate', 0)}%, trial={churn.get('trial_churn_rate', 0)}%, "
        f"volontaire={churn.get('voluntary_pct', 0)}%, technique={churn.get('technical_pct', 0)}%.\n"
        f"Segments: PowerUsers={segments.get('power_users', {}).get('pct', 0)}% "
        f"ARPU={segments.get('power_users', {}).get('arpu', 0)}, TrialOnly={segments.get('trial_only', {}).get('pct', 0)}% "
        f"churn={segments.get('trial_only', {}).get('churn', 0)}%.\n"
        f"Campagnes: total={campaigns.get('total_campaigns', 0)}, ROI={campaigns.get('avg_roi_per_user', 0)}, "
        f"conv={campaigns.get('avg_conversion_rate', 0)}%.\n"
        f"Retention: D7={retention.get('avg_retention_d7', kpis.get('retention_d7', 0))}%, "
        f"D14={retention.get('avg_retention_d14', 0)}%, D30={retention.get('avg_retention_d30', kpis.get('retention_d30', 0))}%.\n"
        f"Anomalies: {anomaly_count} detectee(s). Services: {', '.join(services)}. Periode: {period}."
    )
    return f"""
Expert BI Tunisie Telecom. Type rapport: {report_type}.
Données:
{data_summary}

Règles:
- Base-toi uniquement sur ces données.
- JSON uniquement, sans markdown.
- Français professionnel.
- Max 350 mots total.
- {recommendation_rule}
{custom_rule}

Format exact attendu:
{{
  "summary": "Résumé exécutif",
  "churn": "Analyse churn",
  "segments": "Analyse segmentation",
  "anomalies": "Synthèse anomalies",
  "campaigns": "Performance campagnes",
  "recommendations": "3 recommandations numérotées"
}}
    """.strip()
    return f"""
Tu es un expert en Business Intelligence
pour les services numériques à abonnement
USSD/SMS de Tunisie Telecom.

Contexte :
  Entreprise : DigMaco
  Services analysés : {', '.join(services)}
  Période : {period}
  Type de rapport : {report_type}

Mission : {guidance}

Protocole obligatoire :
1. {priority}
2. Appelle MINIMUM 3 tools différents
   avant de rédiger quoi que ce soit.
3. Base-toi UNIQUEMENT sur les données
   retournées par les tools.
4. Quand tu as suffisamment de données,
   génère le rapport final en JSON pur.

Format de sortie final attendu
(JSON uniquement, sans markdown) :
{{
  "summary": "Résumé exécutif 3 paragraphes",
  "churn": "Analyse churn 2 paragraphes",
  "segments": "Analyse segmentation 2 paragraphes",
  "anomalies": "Synthèse anomalies 1 paragraphe",
  "campaigns": "Performance campagnes 1 paragraphe",
  "recommendations": "3 recommandations actionnables numérotées"
}}

Langue : français professionnel uniquement.
Format : texte brut sans markdown dans les valeurs.
Longueur totale : 400 à 550 mots.
    """.strip()


# ─── Main agentic loop ───────────────────────────

def _generate_insights_mcp_agentic_legacy(
    report_type: str,
    services: list[str],
    period: str,
    db: Session,
    max_turns: int = 8,
) -> dict[str, str]:
    """
    MCP agentic loop for report generation.

    Gemini autonomously decides which tools
    to call, receives real SQL data, then
    synthesizes structured French insights.

    Args:
        report_type: executive | churn |
                     ai_segmentation | full
        services: list of service names
        period: date range string
        db: SQLAlchemy session
        max_turns: max agentic iterations
                   (safety limit)

    Returns:
        dict with keys: summary, churn,
        segments, anomalies, campaigns,
        recommendations
    """
    import os
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning(
            "GEMINI_API_KEY not set — "
            "returning fallback insights"
        )
        return _fallback_insights()

    try:
        genai.configure(api_key=api_key)
    except Exception as exc:
        logger.error(
            "Gemini configure failed: %s", exc
        )
        return _fallback_insights()

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=REPORT_TOOLS,
        system_instruction=_build_system_prompt(
            report_type, services, period
        ),
    )

    chat  = model.start_chat(history=[])
    turns = 0
    tools_called: list[str] = []

    # Kickoff message
    user_message = (
        f"Lance la collecte de données pour "
        f"un rapport {report_type} sur les "
        f"services {', '.join(services)} "
        f"pour la période {period}. "
        f"Commence par appeler les outils "
        f"analytiques nécessaires."
    )

    logger.info(
        "MCP agentic loop started — "
        "report_type=%s max_turns=%d",
        report_type, max_turns,
    )

    while turns < max_turns:
        turns += 1
        logger.debug("Agentic turn %d", turns)

        try:
            response = chat.send_message(
                user_message
            )
        except Exception as exc:
            logger.error(
                "Gemini send_message failed "
                "at turn %d: %s", turns, exc
            )
            break

        # Safety check on response
        if not response.candidates:
            logger.warning(
                "Empty candidates at turn %d",
                turns,
            )
            break

        content = response.candidates[0].content
        if not content.parts:
            logger.warning(
                "Empty parts at turn %d", turns
            )
            break

        part = content.parts[0]

        # ── Gemini calls a tool ──────────────
        if hasattr(part, "function_call") \
           and part.function_call.name:

            fn_name = part.function_call.name
            fn_args = dict(
                part.function_call.args or {}
            )
            tools_called.append(fn_name)

            logger.info(
                "Gemini calling tool: %s args=%s",
                fn_name, fn_args,
            )

            tool_result = _dispatch_tool(
                fn_name, fn_args, db
            )

            logger.debug(
                "Tool %s returned %d keys",
                fn_name, len(tool_result),
            )

            # Return tool result to Gemini
            user_message = genai.protos.Content(
                parts=[
                    genai.protos.Part(
                        function_response=(
                            genai.protos.FunctionResponse(
                                name=fn_name,
                                response={
                                    "result": tool_result
                                },
                            )
                        )
                    )
                ],
                role="user",
            )

        # ── Gemini generates final text ──────
        elif hasattr(part, "text") and part.text:

            raw_text = part.text.strip()

            logger.info(
                "Gemini finished after %d turns, "
                "tools called: %s",
                turns, tools_called,
            )

            # Clean markdown fences if present
            if "```json" in raw_text:
                raw_text = (
                    raw_text
                    .split("```json")[-1]
                    .split("```")[0]
                    .strip()
                )
            elif raw_text.startswith("```"):
                raw_text = (
                    raw_text[3:]
                    .split("```")[0]
                    .strip()
                )

            try:
                insights = json.loads(raw_text)
                # Ensure all required keys exist
                required = [
                    "summary", "churn",
                    "segments", "anomalies",
                    "campaigns", "recommendations",
                ]
                for key in required:
                    if key not in insights:
                        insights[key] = (
                            f"Section {key} "
                            f"non générée."
                        )
                logger.info(
                    "MCP insights parsed "
                    "successfully"
                )
                return insights

            except json.JSONDecodeError:
                logger.warning(
                    "JSON parse failed — "
                    "wrapping text in summary"
                )
                return {
                    "summary": raw_text[:800],
                    "churn": "",
                    "segments": "",
                    "anomalies": "",
                    "campaigns": "",
                    "recommendations": "",
                }

        else:
            logger.warning(
                "Unexpected part type at "
                "turn %d: %s",
                turns, type(part),
            )
            break

    # Max turns reached without JSON output
    logger.warning(
        "MCP loop exhausted after %d turns "
        "without final output. "
        "Tools called: %s",
        turns, tools_called,
    )
    return _fallback_insights()


# ─── Fallback ────────────────────────────────────

def _fallback_insights() -> dict[str, str]:
    """
    Returns minimal safe insights when
    Gemini API is unavailable or fails.
    Used as a graceful degradation mechanism
    to ensure PDF generation always succeeds.
    """
    return {
        "summary": (
            "La plateforme DigMaco Analytics "
            "supervise les services numériques "
            "ElJournal, Esports.tn, ttoons et "
            "Tawer opérés pour Tunisie Telecom. "
            "Les données disponibles couvrent "
            "la période septembre-octobre 2025."
        ),
        "churn": (
            "Le taux de churn global observé "
            "est de 3,7 % avec un taux de churn "
            "trial de 63,5 %. Les analyses de "
            "rétention et les cohortes sont "
            "disponibles dans les tableaux de bord."
        ),
        "segments": (
            "La segmentation K-Means identifie "
            "4 profils : Power Users (2,2 %), "
            "Loyaux Réguliers (2,4 %), "
            "Occasionnels (3,4 %) et "
            "Trial Only (92,1 %)."
        ),
        "anomalies": (
            "Aucune anomalie critique détectée "
            "durant la période analysée."
        ),
        "campaigns": (
            "Les campagnes bulk SMS contribuent "
            "à 28 % des nouvelles souscriptions "
            "avec un ROI moyen de 3,5x."
        ),
        "recommendations": (
            "1. Cibler les 302 abonnés High Risk "
            "avec une campagne SMS de rétention. "
            "2. Optimiser le tunnel d'essai gratuit "
            "pour améliorer le taux de conversion "
            "de 6,8 %. "
            "3. Renforcer les offres pour le "
            "segment Power Users (ARPU 24,5 TND)."
        ),
    }


# ─── Quota-friendly MCP path ─────────────────────────────────────────────
#
# Keep this definition last so imports receive the quota-friendly
# implementation. The previous agentic loop is intentionally left above as
# reference for the original function-calling flow.

def _mcp_tools_for_report_type(report_type: str) -> list[str]:
    full_plan = [
        "get_global_kpis",
        "get_churn_analysis",
        "get_segments",
        "get_anomalies",
        "get_campaign_performance",
        "get_retention_cohorts",
    ]
    plans = {
        "executive": [
            "get_global_kpis",
            "get_anomalies",
            "get_campaign_performance",
            "get_retention_cohorts",
        ],
        "churn": [
            "get_global_kpis",
            "get_churn_analysis",
            "get_retention_cohorts",
            "get_segments",
            "get_anomalies",
        ],
        "ai_segmentation": [
            "get_global_kpis",
            "get_segments",
            "get_churn_analysis",
            "get_campaign_performance",
            "get_anomalies",
        ],
        "full": full_plan,
        "complete": full_plan,
        "premium_enterprise": full_plan,
    }
    return plans.get(report_type, full_plan)


def _collect_mcp_tool_results(
    report_type: str,
    period: str,
    db: Session,
) -> tuple[dict[str, Any], list[str]]:
    tool_results: dict[str, Any] = {}
    tools_called: list[str] = []

    for tool_name in _mcp_tools_for_report_type(report_type):
        logger.info("MCP backend collecting tool: %s", tool_name)
        tool_results[tool_name] = _dispatch_tool(
            tool_name,
            {"period": period},
            db,
        )
        tools_called.append(tool_name)

    return tool_results, tools_called


def _wait_for_mcp_gemini_slot() -> None:
    global _last_gemini_call_at

    if MCP_GEMINI_MIN_INTERVAL_SECONDS <= 0:
        return

    with _gemini_rate_lock:
        now = time.monotonic()
        wait_for = MCP_GEMINI_MIN_INTERVAL_SECONDS - (
            now - _last_gemini_call_at
        )
        if wait_for > 0:
            logger.info(
                "Gemini rate limit guard sleeping %.1fs",
                wait_for,
            )
            time.sleep(wait_for)
        _last_gemini_call_at = time.monotonic()


def _is_retryable_gemini_error(exc: Exception) -> bool:
    text = str(exc).lower()
    retryable_markers = [
        "429",
        "503",
        "resource_exhausted",
        "unavailable",
        "quota",
        "rate limit",
        "high demand",
        "temporarily",
    ]
    return any(marker in text for marker in retryable_markers)


def _gemini_models_to_try() -> list[str]:
    models = [MCP_GEMINI_MODEL, *MCP_GEMINI_FALLBACK_MODELS]
    deduped: list[str] = []
    for model in models:
        if model and model not in deduped:
            deduped.append(model)
    return deduped


def _gemini_retry_sleep(attempt: int, model_name: str, exc: Exception) -> None:
    wait_for = min(
        60.0,
        MCP_GEMINI_RETRY_BASE_SECONDS * (2 ** (attempt - 1)),
    )
    wait_for += random.uniform(0.0, 2.0)
    logger.warning(
        "Gemini temporary failure on %s attempt %d/%d: %s. "
        "Retrying in %.1fs",
        model_name,
        attempt,
        MCP_GEMINI_MAX_RETRIES,
        exc,
        wait_for,
    )
    time.sleep(wait_for)


def _cleanup_old_counters() -> None:
    today = str(date.today())
    with _counter_lock:
        for key in list(_daily_counter.keys()):
            if key != today:
                del _daily_counter[key]


def _check_and_increment_quota() -> bool:
    today = str(date.today())
    with _counter_lock:
        count = _daily_counter.get(today, 0)
        if count >= FREE_TIER_DAILY_LIMIT:
            logger.warning(
                "GEMINI_QUOTA_GUARD_LIMIT_REACHED calls=%d/%d",
                count,
                FREE_TIER_DAILY_LIMIT,
            )
            return False

        _daily_counter[today] = count + 1
        logger.info(
            "GEMINI_QUOTA_GUARD_ALLOW call=%d/%d",
            count + 1,
            FREE_TIER_DAILY_LIMIT,
        )
        return True


def _build_mcp_synthesis_prompt(
    report_type: str,
    services: list[str],
    period: str,
    tool_results: dict[str, Any],
    custom_prompt: str = "",
    include_recommendations: bool = True,
) -> str:
    recommendation_rule = (
        "Inclure exactement 3 recommandations actionnables."
        if include_recommendations
        else "Ne pas inclure de plan d'action détaillé; résumer seulement les constats."
    )
    custom_rule = (
        f"\nInstruction utilisateur complémentaire : {custom_prompt.strip()}\n"
        if custom_prompt and custom_prompt.strip()
        else ""
    )
    kpis = tool_results.get("get_global_kpis", {}) or {}
    churn = tool_results.get("get_churn_analysis", {}) or {}
    segments = tool_results.get("get_segments", {}) or {}
    anomalies = tool_results.get("get_anomalies", []) or []
    campaigns = tool_results.get("get_campaign_performance", {}) or {}
    retention = tool_results.get("get_retention_cohorts", {}) or {}
    anomaly_count = len(anomalies) if isinstance(anomalies, list) else 0
    data_summary = (
        f"KPIs: actifs={kpis.get('active_users', 0)}, subs={kpis.get('active_subscriptions', 0)}, "
        f"churn={kpis.get('churn_rate', 0)}%, conv={kpis.get('conversion_rate', 0)}%, "
        f"ARPU={kpis.get('arpu', 0)} TND, highRisk={kpis.get('high_risk_users', 0)}.\n"
        f"Churn: global={churn.get('global_churn_rate', 0)}%, trial={churn.get('trial_churn_rate', 0)}%, "
        f"volontaire={churn.get('voluntary_pct', 0)}%, technique={churn.get('technical_pct', 0)}%.\n"
        f"Segments: PowerUsers={segments.get('power_users', {}).get('pct', 0)}% "
        f"ARPU={segments.get('power_users', {}).get('arpu', 0)}, TrialOnly={segments.get('trial_only', {}).get('pct', 0)}% "
        f"churn={segments.get('trial_only', {}).get('churn', 0)}%.\n"
        f"Campagnes: total={campaigns.get('total_campaigns', 0)}, ROI={campaigns.get('avg_roi_per_user', 0)}, "
        f"conv={campaigns.get('avg_conversion_rate', 0)}%.\n"
        f"Retention: D7={retention.get('avg_retention_d7', kpis.get('retention_d7', 0))}%, "
        f"D14={retention.get('avg_retention_d14', 0)}%, D30={retention.get('avg_retention_d30', kpis.get('retention_d30', 0))}%.\n"
        f"Anomalies: {anomaly_count} detectee(s). Services: {', '.join(services)}. Periode: {period}."
    )
    return f"""
Expert BI Tunisie Telecom. Type rapport: {report_type}.
Données:
{data_summary}

Règles:
- Base-toi uniquement sur ces données.
- JSON uniquement, sans markdown.
- Français professionnel.
- Max 350 mots total.
- {recommendation_rule}
{custom_rule}

Format exact attendu:
{{
  "summary": "Résumé exécutif",
  "churn": "Analyse churn",
  "segments": "Analyse segmentation",
  "anomalies": "Synthèse anomalies",
  "campaigns": "Performance campagnes",
  "recommendations": "3 recommandations numérotées"
}}
    """.strip()
    return f"""
Tu es un expert en Business Intelligence pour les services numériques
à abonnement USSD/SMS de Tunisie Telecom.

Contexte :
  Entreprise : DigMaco
  Services analysés : {', '.join(services)}
  Période : {period}
  Type de rapport : {report_type}

Données collectées par les tools MCP côté backend :
{json.dumps(tool_results, ensure_ascii=False, indent=2, default=str)}

Règles :
1. Base-toi uniquement sur ces données.
2. Ne mentionne pas les tools, Gemini, MCP ou le backend.
3. Retourne du JSON pur, sans markdown.
4. Utilise un français professionnel.
5. Longueur totale : 400 à 550 mots.

6. {recommendation_rule}
{custom_rule}

Format exact attendu :
{{
  "summary": "Résumé exécutif 3 paragraphes",
  "churn": "Analyse churn 2 paragraphes",
  "segments": "Analyse segmentation 2 paragraphes",
  "anomalies": "Synthèse anomalies 1 paragraphe",
  "campaigns": "Performance campagnes 1 paragraphe",
  "recommendations": "3 recommandations actionnables numérotées"
}}
    """.strip()


def _parse_mcp_json(raw_text: str) -> dict[str, str]:
    raw_text = raw_text.strip()
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[-1].split("```")[0].strip()
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:].split("```")[0].strip()

    try:
        insights = json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start >= 0 and end > start:
            insights = json.loads(raw_text[start:end + 1])
        else:
            raise
    required = [
        "summary", "churn", "segments",
        "anomalies", "campaigns", "recommendations",
    ]
    for key in required:
        value = insights.get(key, "")
        insights[key] = (
            str(value).strip()
            if str(value).strip()
            else f"Section {key} non générée."
        )
    return insights


def _build_mcp_json_repair_prompt(
    original_prompt: str,
    invalid_json: str,
    error: Exception,
) -> str:
    return f"""
La réponse précédente n'était pas un JSON valide.
Erreur JSON: {error}

Régénère uniquement un objet JSON valide, complet, sans markdown,
en respectant exactement ce schéma:
{{
  "summary": "texte",
  "churn": "texte",
  "segments": "texte",
  "anomalies": "texte",
  "campaigns": "texte",
  "recommendations": "texte"
}}

Contraintes:
- Toutes les valeurs doivent être des chaînes de caractères JSON valides.
- Échappe correctement les guillemets et retours ligne.
- Ne termine pas au milieu d'une phrase.
- Français professionnel.
- Réponse JSON uniquement.

Instruction originale:
{original_prompt}

Réponse invalide précédente, à ignorer si nécessaire:
{invalid_json[:3000]}
    """.strip()


def _fallback_with_source() -> dict[str, str]:
    fallback = _fallback_insights()
    fallback["__source"] = "fallback"
    return fallback


def generate_insights_mcp(
    report_type: str,
    services: list[str],
    period: str,
    db: Session,
    max_turns: int = 1,
    custom_prompt: str = "",
    include_recommendations: bool = True,
) -> dict[str, str]:
    """
    Quota-friendly MCP report generation.

    The backend now collects the MCP tool data directly and sends one
    synthesis request to Gemini 2.5 Flash. This avoids the previous
    6-tool + final-response Gemini loop that could hit 5 RPM quotas.
    """
    _ = max_turns
    _cleanup_old_counters()

    cached = get_cached_insights(
        report_type=report_type,
        services=services,
        period=str(period),
        db=db,
    )
    if cached:
        logger.info("REPORT_AI_RESULT source=cache")
        return cached

    if not _check_and_increment_quota():
        fallback = _fallback_with_source()
        logger.info("REPORT_AI_RESULT source=fallback reason=quota_limit")
        return fallback

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning(
            "GEMINI_API_KEY not set — returning fallback insights"
        )
        return _fallback_with_source()

    try:
        genai.configure(api_key=api_key)
    except Exception as exc:
        logger.error("Gemini configure failed: %s", exc)
        return _fallback_with_source()

    logger.info(
        "MCP backend collection started — report_type=%s model=%s",
        report_type,
        MCP_GEMINI_MODEL,
    )

    tool_results, tools_called = _collect_mcp_tool_results(
        report_type=report_type,
        period=period,
        db=db,
    )

    prompt = _build_mcp_synthesis_prompt(
        report_type=report_type,
        services=services,
        period=period,
        tool_results=tool_results,
        custom_prompt=custom_prompt,
        include_recommendations=include_recommendations,
    )
    original_prompt = prompt

    client = google_genai.Client(api_key=api_key)
    raw_text = ""

    for model_name in _gemini_models_to_try():
        for attempt in range(1, MCP_GEMINI_MAX_RETRIES + 1):
            try:
                _wait_for_mcp_gemini_slot()
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=google_genai_types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=5000,
                        response_mime_type="application/json",
                        response_schema=MCPInsightsResponse,
                    ),
                )
                parsed = getattr(response, "parsed", None)
                if parsed is not None:
                    insights = (
                        parsed.model_dump()
                        if hasattr(parsed, "model_dump")
                        else dict(parsed)
                    )
                else:
                    raw_text = (response.text or "").strip()
                    if not raw_text:
                        raise ValueError("Gemini returned an empty response")
                    insights = _parse_mcp_json(raw_text)

                if not insights:
                    raise ValueError("Gemini returned an empty response")

                insights["__source"] = "gemini"
                logger.info(
                    "MCP insights parsed successfully from one Gemini "
                    "synthesis call; model=%s tools called: %s",
                    model_name,
                    tools_called,
                )
                save_insights_to_cache(
                    report_type=report_type,
                    services=services,
                    period=str(period),
                    insights=insights,
                    db=db,
                )
                return insights
            except json.JSONDecodeError as exc:
                logger.warning(
                    "MCP JSON parse failed on %s: %s — "
                    "raw preview=%r — using fallback",
                    model_name,
                    exc,
                    raw_text[:500],
                )
                if attempt < MCP_GEMINI_MAX_RETRIES:
                    prompt = _build_mcp_json_repair_prompt(
                        original_prompt=original_prompt,
                        invalid_json=raw_text,
                        error=exc,
                    )
                    logger.info(
                        "Retrying Gemini with strict JSON repair prompt "
                        "on %s attempt %d/%d",
                        model_name,
                        attempt + 1,
                        MCP_GEMINI_MAX_RETRIES,
                    )
                    time.sleep(2)
                    continue
                logger.warning(
                    "MCP JSON repair exhausted on %s - using fallback",
                    model_name,
                )
                break
            except Exception as exc:
                if (
                    attempt < MCP_GEMINI_MAX_RETRIES
                    and _is_retryable_gemini_error(exc)
                ):
                    _gemini_retry_sleep(attempt, model_name, exc)
                    continue

                logger.warning(
                    "Gemini synthesis failed on %s after %d attempt(s): %s",
                    model_name,
                    attempt,
                    exc,
                )
                break

    logger.error("Gemini synthesis unavailable on all configured models")
    return _fallback_with_source()

    try:
        _wait_for_mcp_gemini_slot()
        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MCP_GEMINI_MODEL,
            contents=prompt,
            config=google_genai_types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=5000,
                response_mime_type="application/json",
            ),
        )
        raw_text = (response.text or "").strip()
        if not raw_text:
            raise ValueError("Gemini returned an empty response")

        insights = _parse_mcp_json(raw_text)
        insights["__source"] = "gemini"
        logger.info(
            "MCP insights parsed successfully from one Gemini "
            "synthesis call; tools called: %s",
            tools_called,
        )
        return insights
    except json.JSONDecodeError as exc:
        logger.warning(
            "MCP JSON parse failed: %s — raw preview=%r — using fallback",
            exc,
            raw_text[:500] if "raw_text" in locals() else "",
        )
    except Exception as exc:
        logger.error(
            "Gemini synthesis failed: %s — using fallback",
            exc,
        )

    return _fallback_with_source()
