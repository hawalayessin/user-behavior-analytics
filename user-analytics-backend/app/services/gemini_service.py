"""
GeminiReportService — Legacy direct calls.

NOTE: As of the MCP integration, the primary
report generation flow uses mcp_agent_service.py
which implements an agentic tool-calling loop.

This module is kept as a fallback utility
and for direct single-section generation.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from google import genai

logger = logging.getLogger(__name__)

ENTERPRISE_INSIGHT_KEYS: list[str] = [
    "ai_summary",
    "predictive_forecast",
    "strategic_priorities",
    "ai_churn_explanations",
    "predictive_churn_forecast",
    "segment_migration_analysis",
    "segment_profitability_matrix",
    "ai_campaign_recommendations",
    "session_activity_charts",
    "engagement_timeline",
    "user_migration_paths",
    "behavioral_heatmaps",
    "peak_activity_analysis",
    "device_platform_analytics",
    "trial_churn_funnel",
    "trial_dropoff_analysis",
    "trial_lifetime_distribution",
    "trial_to_paid_flow",
    "trial_ai_recommendations",
    "ai_anomaly_explanations",
    "risk_severity_indicators",
    "platform_health_monitoring",
    "ai_action_plan",
    "high_priority_recommendations",
    "business_impact_estimation",
    "revenue_optimization_suggestions",
    "retention_optimization_strategy",
    "expected_kpi_improvements",
]


class GeminiReportService:
    MODEL_NAME = "gemini-2.5-flash"
    MAX_TOKENS_SUMMARY = 700
    MAX_TOKENS_SECTION = 500
    MAX_TOKENS_ENTERPRISE = 6000
    TEMPERATURE = 0.25

    def __init__(self, language: str = "fr", custom_prompt_template: str = "") -> None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY manquant dans les variables d'environnement. "
                "Ajoutez GEMINI_API_KEY dans .env"
            )

        self.language = (language or "fr").strip().lower()
        self.custom_prompt_template = (custom_prompt_template or "").strip()
        self.client = genai.Client(api_key=api_key)

    def _lang_line(self) -> str:
        return "Write in English." if self.language == "en" else "Ecris en francais."

    def _compose_prompt(self, base_prompt: str) -> str:
        extra = ""
        if self.custom_prompt_template:
            extra = (
                "\nAdditional user instructions (highest priority after safety):\n"
                f"{self.custom_prompt_template}\n"
            )
        return f"{self._lang_line()}\n{extra}\n{base_prompt}"

    def _call(self, prompt: str, max_tokens: int = 400) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=self._compose_prompt(prompt),
                config=genai.types.GenerateContentConfig(
                    temperature=self.TEMPERATURE,
                    max_output_tokens=max_tokens,
                ),
            )
            text = (response.text or "").strip()
            return text or "Insights IA indisponibles pour cette section."
        except Exception as exc:
            logger.warning("Gemini call error: %s", exc)
            return f"Insights IA indisponibles. Erreur Gemini : {exc}"

    def _call_json(self, prompt: str, max_tokens: int = 4000) -> dict[str, Any] | None:
        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=self._compose_prompt(prompt),
                config=genai.types.GenerateContentConfig(
                    temperature=self.TEMPERATURE,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                ),
            )
            raw = (response.text or "").strip()
            if not raw:
                return None
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Gemini returned non-JSON, attempting text extraction")
            raw_text = (response.text or "").strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```", 1)[1].split("```", 1)[0].strip()
            try:
                return json.loads(raw_text)
            except Exception:
                return None
        except Exception as exc:
            logger.warning("Gemini JSON call error: %s", exc)
            return None

    def generate_executive_summary(self, kpis: dict[str, Any], period: str, services: list[str]) -> str:
        prompt = f"""
You are a senior telecom business intelligence analyst.

Write a concise executive summary with 2 to 3 short paragraphs.

Period: {period}
Services: {', '.join(services)}

KPI data:
{json.dumps(kpis, ensure_ascii=False, indent=2)}

Constraints:
- Plain text only
- No markdown
- No bullets
- 160 to 220 words
- Professional and factual tone
"""
        return self._call(prompt, max_tokens=self.MAX_TOKENS_SUMMARY)

    def generate_churn_insights(self, churn_data: dict[str, Any], services: list[str]) -> str:
        prompt = f"""
You are a telecom churn analyst.

Write 2 concise paragraphs:
1) Factual churn analysis
2) Two actionable retention actions with time horizon

Services: {', '.join(services)}
Churn data:
{json.dumps(churn_data, ensure_ascii=False, indent=2)}

Constraints:
- Plain text only
- 120 to 170 words
"""
        return self._call(prompt, max_tokens=self.MAX_TOKENS_SECTION)

    def generate_segmentation_insights(self, segments: dict[str, Any]) -> str:
        prompt = f"""
You are a customer segmentation expert.

Write 2 paragraphs:
1) Segment insights and business meaning
2) Prioritized strategy by segment

Data:
{json.dumps(segments, ensure_ascii=False, indent=2)}

Constraints:
- Plain text only
- 120 to 170 words
"""
        return self._call(prompt, max_tokens=self.MAX_TOKENS_SECTION)

    def generate_campaign_insights(self, campaign_data: dict[str, Any], services: list[str]) -> str:
        prompt = f"""
You are a digital campaign performance analyst.

Write 2 concise paragraphs:
1) Campaign performance
2) Optimization recommendations

Services: {', '.join(services)}
Campaign data:
{json.dumps(campaign_data, ensure_ascii=False, indent=2)}

Constraints:
- Plain text only
- 100 to 150 words
"""
        return self._call(prompt, max_tokens=self.MAX_TOKENS_SECTION)

    def generate_anomaly_insights(self, anomalies: list[dict[str, Any]]) -> str:
        if not anomalies:
            return (
                "No significant anomaly detected in the analyzed period. "
                if self.language == "en"
                else "Aucune anomalie significative n'a ete detectee durant la periode analysee. "
            )

        prompt = f"""
You are an anomaly detection analyst.

Write one alert paragraph including:
- anomaly nature and severity
- likely business impact
- immediate recommended action

Data:
{json.dumps(anomalies, ensure_ascii=False, indent=2)}

Constraints:
- Plain text only
- 90 to 130 words
"""
        return self._call(prompt, max_tokens=self.MAX_TOKENS_SECTION)

    def generate_full_report_insights(
        self,
        metrics: dict[str, Any],
        period: str = "",
        services: list[str] | None = None,
    ) -> dict[str, str] | None:
        svc_list = ", ".join(services or ["ElJournal", "Esports.tn", "ttoons", "Tawer"])
        keys_json = json.dumps(ENTERPRISE_INSIGHT_KEYS)

        prompt = f"""
You are DigMaco Precision Observatory, an enterprise-grade AI analytics engine
for a telecom behavioral intelligence platform.

Analyze the following behavioral analytics metrics and generate executive insights,
churn risks, retention opportunities, anomalies, and strategic recommendations.

Period: {period or 'Last quarter'}
Services: {svc_list}

Data:
{json.dumps(metrics, ensure_ascii=False, indent=2)}

Generate a JSON object with EXACTLY these keys (every key must be present):
{keys_json}

For each key, write 2-4 sentences of enterprise analytics intelligence.
Be specific, cite numbers from the data, and provide actionable recommendations.

Guidelines per key:
- ai_summary: Executive summary of overall platform health and growth trajectory
- predictive_forecast: Revenue and user-base forecast for next quarter with confidence level
- strategic_priorities: Top 3 strategic priorities with expected business impact
- ai_churn_explanations: Root causes of churn patterns with service-level breakdown
- predictive_churn_forecast: Predicted churn evolution for next 30/60/90 days
- segment_migration_analysis: How users migrate between segments over time
- segment_profitability_matrix: Ranking of segments by profitability and growth potential
- ai_campaign_recommendations: Specific campaign optimizations with expected uplift
- session_activity_charts: Narrative description of session patterns and peak hours
- engagement_timeline: User engagement trends over the analysis period
- user_migration_paths: Common paths users take across services
- behavioral_heatmaps: Description of behavioral intensity patterns
- peak_activity_analysis: When users are most active and implications
- device_platform_analytics: Device and platform distribution insights
- trial_churn_funnel: Trial user drop-off stages and bottlenecks
- trial_dropoff_analysis: Why trial users leave and at what point
- trial_lifetime_distribution: Trial duration patterns and optimal conversion windows
- trial_to_paid_flow: Conversion flow analysis from trial to paid
- trial_ai_recommendations: Specific actions to improve trial-to-paid conversion
- ai_anomaly_explanations: Detected anomalies with severity and business context
- risk_severity_indicators: Risk level assessment across platform dimensions
- platform_health_monitoring: Overall platform health status and alerts
- ai_action_plan: Prioritized 30/60/90 day action plan
- high_priority_recommendations: Top 5 immediate actions with expected ROI
- business_impact_estimation: Quantified business impact of recommended changes
- revenue_optimization_suggestions: Specific revenue growth levers
- retention_optimization_strategy: Retention improvement roadmap with milestones
- expected_kpi_improvements: Projected KPI improvements if recommendations are followed

Tone: Enterprise analytics intelligence report. Professional, data-driven, authoritative.
{self._lang_line()}

Return ONLY the JSON object, no extra text.
"""
        result = self._call_json(prompt, max_tokens=self.MAX_TOKENS_ENTERPRISE)
        if not result:
            logger.warning("Gemini enterprise call returned None — will use fallback")
            return None

        for key in ENTERPRISE_INSIGHT_KEYS:
            if key not in result:
                result[key] = ""

        logger.info("Gemini enterprise insights generated: %d keys", len(result))
        return result
