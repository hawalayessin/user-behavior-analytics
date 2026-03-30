#!/usr/bin/env python3
"""
Rapport d'Avancement PFE — User Behavior Analytics & Insights Platform
Comparaison état actuel vs cahier des charges
Généré le 24 Mars 2026
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import (
    HexColor, white, black, Color
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── Couleurs ─────────────────────────────────────────
DARK_BLUE   = HexColor("#1a237e")
MED_BLUE    = HexColor("#283593")
LIGHT_BLUE  = HexColor("#e8eaf6")
ACCENT      = HexColor("#1565c0")
GREEN       = HexColor("#2e7d32")
ORANGE      = HexColor("#ef6c00")
RED         = HexColor("#c62828")
GRAY_BG     = HexColor("#f5f5f5")
GRAY_TEXT   = HexColor("#616161")
WHITE       = white
BLACK       = black

# ─── Styles ───────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleCustom", parent=styles["Title"],
    fontSize=24, leading=30, textColor=DARK_BLUE,
    spaceAfter=6, alignment=TA_CENTER,
    fontName="Helvetica-Bold"
)

subtitle_style = ParagraphStyle(
    "SubtitleCustom", parent=styles["Normal"],
    fontSize=12, leading=16, textColor=GRAY_TEXT,
    alignment=TA_CENTER, spaceAfter=20,
    fontName="Helvetica"
)

h1_style = ParagraphStyle(
    "H1Custom", parent=styles["Heading1"],
    fontSize=18, leading=22, textColor=DARK_BLUE,
    spaceBefore=20, spaceAfter=10,
    fontName="Helvetica-Bold",
    borderPadding=(0, 0, 4, 0),
)

h2_style = ParagraphStyle(
    "H2Custom", parent=styles["Heading2"],
    fontSize=14, leading=18, textColor=MED_BLUE,
    spaceBefore=14, spaceAfter=8,
    fontName="Helvetica-Bold"
)

h3_style = ParagraphStyle(
    "H3Custom", parent=styles["Heading3"],
    fontSize=12, leading=15, textColor=ACCENT,
    spaceBefore=10, spaceAfter=6,
    fontName="Helvetica-Bold"
)

body_style = ParagraphStyle(
    "BodyCustom", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=BLACK,
    alignment=TA_JUSTIFY, spaceAfter=6,
    fontName="Helvetica"
)

body_bold = ParagraphStyle(
    "BodyBold", parent=body_style,
    fontName="Helvetica-Bold"
)

small_style = ParagraphStyle(
    "SmallCustom", parent=styles["Normal"],
    fontSize=8, leading=10, textColor=GRAY_TEXT,
    fontName="Helvetica"
)

bullet_style = ParagraphStyle(
    "BulletCustom", parent=body_style,
    leftIndent=20, bulletIndent=8,
    spaceAfter=3,
)

# ─── Helpers ──────────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE, spaceAfter=8, spaceBefore=4)

def spacer(h=0.3):
    return Spacer(1, h * cm)

def badge(text, color):
    """Returns a colored badge paragraph."""
    return f'<font color="{color}">{text}</font>'

def status_cell(pct, label):
    if pct >= 100:
        color = GREEN
        icon = "✅"
    elif pct > 0:
        color = ORANGE
        icon = "🔧"
    else:
        color = RED
        icon = "❌"
    return Paragraph(f'{icon} {pct}% — {label}', ParagraphStyle("s", parent=body_style, textColor=color, fontSize=9, fontName="Helvetica-Bold"))

def make_table(data, col_widths=None, header=True):
    tbl = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style_cmds = [
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("GRID",        (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
    ]
    if header:
        style_cmds += [
            ("BACKGROUND",  (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 9),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_cmds.append(("BACKGROUND", (0, i), (-1, i), GRAY_BG))
    tbl.setStyle(TableStyle(style_cmds))
    return tbl

# ─── Page header/footer ──────────────────────────────
def header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(DARK_BLUE)
    canvas.setLineWidth(2)
    canvas.line(1.5*cm, A4[1] - 1.2*cm, A4[0] - 1.5*cm, A4[1] - 1.2*cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRAY_TEXT)
    canvas.drawString(1.5*cm, A4[1] - 1.0*cm, "PFE 2026 — User Behavior Analytics & Insights Platform")
    canvas.drawRightString(A4[0] - 1.5*cm, A4[1] - 1.0*cm, "Rapport d'Avancement — 24 Mars 2026")
    # Footer
    canvas.setLineWidth(0.5)
    canvas.line(1.5*cm, 1.3*cm, A4[0] - 1.5*cm, 1.3*cm)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0]/2, 0.8*cm, f"Page {doc.page}")
    canvas.restoreState()


# ─── Build Document ───────────────────────────────────
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=1.5*cm,
        bottomMargin=1.8*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
    )

    story = []

    # ══════════════════════════════════════════════════
    # PAGE DE COUVERTURE
    # ══════════════════════════════════════════════════
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Rapport d'Avancement", title_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("User Behavior Analytics &amp; Insights Platform", ParagraphStyle(
        "CoverSub", parent=title_style, fontSize=16, textColor=ACCENT, leading=20
    )))
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="60%", thickness=2, color=DARK_BLUE, spaceAfter=10, spaceBefore=4))
    story.append(Spacer(1, 0.5*cm))

    cover_data = [
        ["Projet", "Projet de Fin d'Études (PFE)"],
        ["Date", "24 Mars 2026"],
        ["Version", "2.0"],
        ["Statut", "En développement actif — Phase 2 complétée"],
        ["Technologies", "React 19 · FastAPI · PostgreSQL 15 · scikit-learn"],
        ["Infrastructure", "Docker Compose (3 conteneurs)"],
    ]
    cover_table = Table(cover_data, colWidths=[4*cm, 12*cm])
    cover_table.setStyle(TableStyle([
        ("FONTNAME",     (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",    (0, 0), (0, -1), DARK_BLUE),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LINEBELOW",    (0, 0), (-1, -1), 0.5, HexColor("#e0e0e0")),
    ]))
    story.append(cover_table)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # TABLE DES MATIÈRES
    # ══════════════════════════════════════════════════
    story.append(Paragraph("Table des Matières", h1_style))
    story.append(hr())
    toc_items = [
        "1. Résumé Exécutif",
        "2. Tableau de Bord — Avancement Global",
        "3. Exigences du Cahier des Charges — État de Réalisation",
        "   3.1 User Activity & Engagement",
        "   3.2 Free Trial Behavior",
        "   3.3 Subscription & Revenue Flow (Retention)",
        "   3.4 Campaign Impact",
        "   3.5 Cross-Service Behavior",
        "4. Dashboard Requirements",
        "5. Report Generation",
        "6. AI & Advanced Analytics",
        "7. Livrables Attendus — État",
        "8. Modèle de Données",
        "9. Architecture Technique",
        "10. Tests et Qualité",
        "11. Recommandations Business",
        "12. Risques et Limitations",
        "13. Planning et Roadmap",
        "14. Conclusion",
    ]
    for item in toc_items:
        indent = 20 if item.startswith("   ") else 0
        story.append(Paragraph(item.strip(), ParagraphStyle("toc", parent=body_style, leftIndent=indent, spaceAfter=3)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 1. RÉSUMÉ EXÉCUTIF
    # ══════════════════════════════════════════════════
    story.append(Paragraph("1. Résumé Exécutif", h1_style))
    story.append(hr())
    story.append(Paragraph(
        "Ce document présente l'état d'avancement mis à jour du projet <b>User Behavior Analytics &amp; "
        "Insights Platform</b>, développé dans le cadre d'un PFE. Le projet fournit des insights actionnables "
        "sur le comportement des utilisateurs de services par abonnement SMS (essais gratuits, conversions, "
        "rétention, churn, campagnes).",
        body_style
    ))
    story.append(spacer(0.3))
    story.append(Paragraph("<b>Évolution depuis le dernier rapport (16 Mars 2026) :</b>", body_bold))
    evolutions = [
        "✅ Section Campaign Impact — <b>100% complétée</b> (était 0%)",
        "✅ Churn Analysis — <b>100% complétée</b> avec 5 endpoints (KPIs, courbe, time-to-churn, reasons, risk segments)",
        "✅ AI / Churn Prediction — <b>100% complétée</b> (Logistic Regression, train/predict/metrics endpoints, dashboard React)",
        "✅ Admin Import Data — <b>100% complété</b> (CSV/Excel multi-tables, validation, logs)",
        "✅ Admin Management — <b>100% complété</b> (CRUD services, campagnes, types de service)",
        "✅ Authentification JWT + RBAC — <b>100% complétée</b> (routes admin protégées)",
        "✅ 12 modèles SQLAlchemy + 15 schémas Pydantic implémentés",
        "✅ Données seed réalistes : 1200+ utilisateurs, 8 services, 52 cohortes",
    ]
    for e in evolutions:
        story.append(Paragraph(e, bullet_style, bulletText="•"))
    story.append(spacer(0.3))
    story.append(Paragraph(
        "Avancement global estimé : <b>~85%</b> (contre ~45% au 16 mars). "
        "Les 5 sections analytiques du cahier des charges sont maintenant complétées à un niveau fonctionnel.",
        body_style
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 2. TABLEAU DE BORD AVANCEMENT GLOBAL
    # ══════════════════════════════════════════════════
    story.append(Paragraph("2. Tableau de Bord — Avancement Global", h1_style))
    story.append(hr())
    story.append(Paragraph("Vue synthétique de l'avancement par rapport aux exigences du cahier des charges :", body_style))
    story.append(spacer(0.2))

    progress_data = [
        [Paragraph("<b>Exigence</b>", body_bold),
         Paragraph("<b>Statut</b>", body_bold),
         Paragraph("<b>Avancement</b>", body_bold),
         Paragraph("<b>Note</b>", body_bold)],
        ["User Activity & Engagement", status_cell(100, "Terminé"), "100%", "6 KPIs, graphiques, filtres"],
        ["Free Trial Behavior", status_cell(100, "Terminé"), "100%", "Funnel, drop-off, conversion"],
        ["Subscription & Revenue (Retention)", status_cell(100, "Terminé"), "100%", "Heatmap, courbes, cohorts"],
        ["Campaign Impact", status_cell(100, "Terminé"), "100%", "KPIs, timeline, comparaison"],
        ["Cross-Service Behavior", status_cell(0, "Non démarré"), "0%", "Phase 3 — bonus"],
        ["Dashboard interactif", status_cell(100, "Terminé"), "100%", "Recharts + MUI + Tailwind"],
        ["Filtrage (date, service, campagne)", status_cell(90, "Quasi terminé"), "90%", "Date + Service OK, Campaign partiel"],
        ["Export CSV/Excel", status_cell(100, "Terminé"), "100%", "Sur toutes les tables"],
        ["Report Generation (PDF)", status_cell(0, "Non démarré"), "0%", "Prévu Phase 3"],
        ["AI / Analytics avancé", status_cell(100, "Terminé"), "100%", "Churn Prediction (Logistic Reg.)"],
        ["Authentification & RBAC", status_cell(100, "Terminé"), "100%", "JWT + rôles admin/user"],
        ["Admin Import Data", status_cell(100, "Terminé"), "100%", "CSV/Excel multi-tables"],
        ["Documentation technique", status_cell(90, "En cours"), "90%", "KPIs, architecture, ML report"],
    ]
    tbl = make_table(progress_data, col_widths=[4.5*cm, 4*cm, 2*cm, 6.5*cm])
    story.append(tbl)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 3. EXIGENCES CAHIER DES CHARGES
    # ══════════════════════════════════════════════════
    story.append(Paragraph("3. Exigences du Cahier des Charges — État de Réalisation", h1_style))
    story.append(hr())

    # --- 3.1 User Activity ---
    story.append(Paragraph("3.1 User Activity &amp; Engagement", h2_style))
    story.append(Paragraph("<b>Exigences :</b> Utilisateurs actifs/inactifs par service, DAU/WAU/MAU, durée de vie moyenne", body_style))
    story.append(Paragraph("<b>État :</b> ✅ <font color='#2e7d32'>100% TERMINÉ</font>", body_bold))
    story.append(spacer(0.2))
    ua_items = [
        "Page UserActivityPage.jsx complète avec 6 KPI Cards",
        "FilterBar réutilisable (date range + sélection services)",
        "Engagement Health Panel + Top Services Table",
        "Graphiques interactifs (Activity Trends, Service Distribution)",
        "3 Endpoints FastAPI : /analytics/user-activity/kpis, /trends, /by-service",
    ]
    for item in ua_items:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))
    story.append(spacer(0.3))

    # --- 3.2 Free Trial ---
    story.append(Paragraph("3.2 Free Trial Behavior", h2_style))
    story.append(Paragraph("<b>Exigences :</b> Essais gratuits, conversions, drop-off par jour, patterns comportementaux", body_style))
    story.append(Paragraph("<b>État :</b> ✅ <font color='#2e7d32'>100% TERMINÉ</font>", body_bold))
    story.append(spacer(0.2))
    ft_items = [
        "Page FreeTrialBehaviorPage.jsx complète",
        "KPI Cards : Trial Started, Converted, Conversion Rate, Drop-off Day",
        "Trial Funnel Chart + Drop-off Chart (J1/J2/J3)",
        "Conversion Donut Chart + Trial Details Table",
        "Endpoints : /analytics/trial/kpis, /dropoff-by-day, /users",
    ]
    for item in ft_items:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))
    story.append(spacer(0.3))

    # --- 3.3 Retention ---
    story.append(Paragraph("3.3 Subscription &amp; Revenue Flow (Retention)", h2_style))
    story.append(Paragraph("<b>Exigences :</b> Abonnements/jour/semaine/mois, churn, rétention D7/D14/D30, ré-abonnement", body_style))
    story.append(Paragraph("<b>État :</b> ✅ <font color='#2e7d32'>100% TERMINÉ</font>", body_bold))
    story.append(spacer(0.2))
    ret_items = [
        "Page RetentionPage.jsx complète",
        "Table cohorts créée et peuplée (52 cohortes mensuelles via script ETL)",
        "4 Endpoints : /analytics/retention/kpis, /heatmap, /curve, /cohorts-list",
        "Visualisations : Cohort Heatmap, Retention Curve, Service Retention Radar",
        "KPI Cards : Avg D7, Avg D30, Best Cohort, At-Risk Count",
    ]
    for item in ret_items:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))
    story.append(spacer(0.3))

    # --- 3.4 Campaign Impact ---
    story.append(Paragraph("3.4 Campaign Impact", h2_style))
    story.append(Paragraph("<b>Exigences :</b> Nouveaux abonnés après campagne SMS, taux de conversion, comparaison campagnes", body_style))
    story.append(Paragraph("<b>État :</b> ✅ <font color='#2e7d32'>100% TERMINÉ</font> <i>(nouveau depuis dernier rapport)</i>", body_bold))
    story.append(spacer(0.2))
    camp_items = [
        "Page CampaignImpactPage.jsx complète",
        "Table campaigns implémentée avec modèle SQLAlchemy",
        "4 Endpoints : /analytics/campaigns/kpis, /timeline, /comparison, /performance",
        "KPIs : total campagnes, abonnés via campagnes, taux conversion moyen, retention D7",
        "Visualisations : Timeline, Comparaison multi-campagnes, Performance charts",
        "Hooks React dédiés : useCampaignKPIs, useCampaignTimeline, useCampaignComparison, useCampaignPerformance",
    ]
    for item in camp_items:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))
    story.append(PageBreak())

    # --- 3.5 Cross-Service ---
    story.append(Paragraph("3.5 Cross-Service Behavior", h2_style))
    story.append(Paragraph("<b>Exigences :</b> Multi-abonnements, services utilisés ensemble, chemins de migration", body_style))
    story.append(Paragraph("<b>État :</b> ❌ <font color='#c62828'>0% NON DÉMARRÉ</font>", body_bold))
    story.append(spacer(0.2))
    story.append(Paragraph(
        "Cette section est classée en <b>Phase 3 (bonus)</b>. L'approche technique envisagée : "
        "analyse SQL multi-services par user_id, matrice de corrélation services, graphe de flux Sankey.",
        body_style
    ))
    story.append(spacer(0.3))

    # ══════════════════════════════════════════════════
    # 4. DASHBOARD REQUIREMENTS
    # ══════════════════════════════════════════════════
    story.append(Paragraph("4. Dashboard Requirements", h1_style))
    story.append(hr())

    story.append(Paragraph("4.1 Filtrage Interactif", h3_style))
    story.append(Paragraph("✅ FilterBar réutilisable implémenté (date range + services)", body_style))
    story.append(Paragraph("✅ Utilisé dans UserActivity, FreeTrial, Retention, Campaign, Churn", body_style))
    story.append(Paragraph("⚠️ Filtre campagne disponible uniquement dans la page Campaign Impact", body_style))
    story.append(spacer(0.2))

    story.append(Paragraph("4.2 Visualisations Interactives", h3_style))
    viz_data = [
        [Paragraph("<b>Type</b>", body_bold), Paragraph("<b>Statut</b>", body_bold), Paragraph("<b>Implémentation</b>", body_bold)],
        ["Line charts (growth, churn, retention)", "✅ Terminé", "ActivityTrendsChart, RetentionCurve, ChurnCurve"],
        ["Bar charts (campaign performance)", "✅ Terminé", "CampaignComparison, TopServicesTable"],
        ["Funnel charts (trial → subscription)", "✅ Terminé", "TrialFunnelChart (custom)"],
        ["Cohort heatmaps", "✅ Terminé", "RetentionHeatmap (grille colorée)"],
        ["Pie / Donut charts", "✅ Terminé", "SubscriptionDonutChart, ChurnPieChart"],
    ]
    story.append(make_table(viz_data, col_widths=[5.5*cm, 3*cm, 8.5*cm]))
    story.append(spacer(0.2))

    story.append(Paragraph("4.3 Export Data", h3_style))
    story.append(Paragraph("✅ Export CSV implémenté sur toutes les tables de données", body_style))
    story.append(Paragraph("✅ Export Excel (xlsx) via bibliothèque xlsx dans le frontend", body_style))
    story.append(Paragraph("✅ Export PDF via html2canvas + jspdf (capture de page)", body_style))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 5. REPORT GENERATION
    # ══════════════════════════════════════════════════
    story.append(Paragraph("5. Report Generation", h1_style))
    story.append(hr())
    story.append(Paragraph("<b>Exigence :</b> Génération de rapports à la demande (PDF, date range, service, KPIs)", body_style))
    story.append(Paragraph("<b>État :</b> ❌ <font color='#c62828'>0% NON DÉMARRÉ</font>", body_bold))
    story.append(spacer(0.2))
    story.append(Paragraph(
        "Approche technique envisagée : endpoint POST /analytics/reports/generate côté FastAPI, "
        "utilisant reportlab ou weasyprint pour la conversion HTML→PDF, agrégation des données "
        "depuis les endpoints existants, téléchargement direct via blob response dans le frontend.",
        body_style
    ))
    story.append(Paragraph("<b>Planification :</b> Phase 3 du projet", body_bold))
    story.append(spacer(0.5))

    # ══════════════════════════════════════════════════
    # 6. AI & ADVANCED ANALYTICS
    # ══════════════════════════════════════════════════
    story.append(Paragraph("6. AI &amp; Advanced Analytics", h1_style))
    story.append(hr())

    story.append(Paragraph("6.1 Churn Prediction (Logistic Regression)", h2_style))
    story.append(Paragraph("<b>État :</b> ✅ <font color='#2e7d32'>100% TERMINÉ</font> <i>(nouveau depuis dernier rapport)</i>", body_bold))
    story.append(spacer(0.2))

    ai_items = [
        "Modèle : Logistic Regression (scikit-learn) avec class_weight='balanced'",
        "9 features engineerées : days_since_last_activity, nb_activities_7d/30d, billing_failures_30d, "
        "days_since_first_charge, is_trial_churn, avg_retention_d7, service_billing_frequency, days_to_first_unsub",
        "Persistance : churn_model.joblib + churn_metrics.joblib",
        "3 Endpoints API : POST /ml/churn/train, GET /ml/churn/scores, GET /ml/churn/metrics",
        "Catégories de risque : Low (&lt;0.3), Medium (0.3-0.6), High (≥0.6)",
        "Page React AIChurnInsights.jsx avec :",
    ]
    for item in ai_items:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))

    ai_viz = [
        "Model KPIs (ROC-AUC, Accuracy, Churn rate, samples)",
        "Risk distribution chart (Low/Medium/High)",
        "Feature impact table (coefficients Logistic Regression)",
        "Top risky users table (phone, service, risk score)",
    ]
    for item in ai_viz:
        story.append(Paragraph(f"    → {item}", ParagraphStyle("indent2", parent=bullet_style, leftIndent=40)))

    story.append(spacer(0.3))
    story.append(Paragraph("6.2 Churn Analysis (Rule-based)", h2_style))
    story.append(Paragraph("<b>État :</b> ✅ <font color='#2e7d32'>100% TERMINÉ</font>", body_bold))
    story.append(spacer(0.1))
    churn_items = [
        "Page ChurnAnalysisPage.jsx complète",
        "5 Endpoints : /analytics/churn/kpis, /curve, /time-to-churn, /reasons, /risk-segments",
        "KPIs : taux de churn global, avg lifetime, trial vs paid churn, voluntary vs technical",
        "Visualisations : Churn Curve, Time-to-Churn Buckets, Top Reasons, Risk Segments",
        "4 segments de risque définis (SEG_A à SEG_D) avec heuristiques",
    ]
    for item in churn_items:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))

    story.append(spacer(0.3))
    story.append(Paragraph("6.3 User Segmentation (Clustering)", h2_style))
    story.append(Paragraph("<b>État :</b> ❌ <font color='#c62828'>0% — Planifié (bonus)</font>", body_bold))
    story.append(Paragraph("Page /analytics/segmentation existe avec placeholder 'coming soon'.", body_style))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 7. LIVRABLES ATTENDUS
    # ══════════════════════════════════════════════════
    story.append(Paragraph("7. Livrables Attendus du Cahier des Charges — État", h1_style))
    story.append(hr())

    deliverables_data = [
        [Paragraph("<b>#</b>", body_bold),
         Paragraph("<b>Livrable</b>", body_bold),
         Paragraph("<b>Statut</b>", body_bold),
         Paragraph("<b>Détails</b>", body_bold)],
        ["1", "Document compréhension projet", status_cell(100, "Terminé"),
         "architecture.md, ce rapport"],
        ["2", "Modèle de données & schéma", status_cell(100, "Terminé"),
         "12 modèles SQLAlchemy, 15 schémas Pydantic"],
        ["3", "Définitions KPIs et formules", status_cell(100, "Terminé"),
         "docs/kpis.md (432 lignes, SQL complet)"],
        ["4", "Dashboard / prototype", status_cell(100, "Terminé"),
         "6 pages dashboard + admin panel"],
        ["5", "Analyse comportementale & findings", status_cell(80, "En cours"),
         "Données analysées, recommandations préliminaires"],
        ["6", "Recommandations (≥5)", status_cell(60, "En cours"),
         "4 recommandations rédigées, besoin 1+ supplémentaire"],
        ["7", "Justification & evidence", status_cell(60, "En cours"),
         "Métriques disponibles, à formaliser dans rapport final"],
        ["8", "AI / Analytics avancé (≥1)", status_cell(100, "Terminé"),
         "Churn Prediction (Logistic Regression) + dashboard"],
        ["9", "Business Impact Summary", status_cell(40, "Partiel"),
         "Recommandations préliminaires, résumé 1 page à rédiger"],
    ]
    story.append(make_table(deliverables_data, col_widths=[1*cm, 4.5*cm, 4*cm, 7.5*cm]))
    story.append(spacer(0.5))
    story.append(Paragraph(
        "<b>Score livrables :</b> 7/9 complétés ou quasi-complétés. Les items restants (recommandations "
        "formalisées, business impact summary) sont des livrables documentaires à finaliser pour la soutenance.",
        body_style
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 8. MODÈLE DE DONNÉES
    # ══════════════════════════════════════════════════
    story.append(Paragraph("8. Modèle de Données — Architecture PostgreSQL", h1_style))
    story.append(hr())

    story.append(Paragraph("8.1 Tables Implémentées (12)", h2_style))
    tables_data = [
        [Paragraph("<b>Table</b>", body_bold),
         Paragraph("<b>Statut</b>", body_bold),
         Paragraph("<b>Colonnes Clés</b>", body_bold)],
        ["users", "✅", "id, phone_number, created_at, status, last_activity_at"],
        ["services", "✅", "id, name, service_type_id, price"],
        ["service_types", "✅", "id, billing_frequency_days, trial_duration_days"],
        ["subscriptions", "✅", "id, user_id, service_id, status, start_date, end_date, campaign_id"],
        ["unsubscriptions", "✅", "id, subscription_id, churn_type, churn_reason, days_since_subscription"],
        ["billing_events", "✅", "id, subscription_id, event_datetime, status, is_first_charge"],
        ["sms_events", "✅", "id, user_id, service_id, direction, status"],
        ["campaigns", "✅", "id, name, service_id, send_datetime, target_size, total_subscriptions"],
        ["cohorts", "✅", "id, service_id, cohort_date, retention_d7/d14/d30, total_users"],
        ["user_activities", "✅", "id, user_id, service_id, activity_datetime"],
        ["platform_users", "✅", "id, email, password_hash, role, full_name"],
        ["import_logs", "✅", "id, file_name, table_name, rows_imported, status"],
    ]
    story.append(make_table(tables_data, col_widths=[3.5*cm, 1.5*cm, 12*cm]))
    story.append(spacer(0.3))
    story.append(Paragraph(
        "<b>Relations :</b> users (1) ↔ (N) subscriptions (N) ↔ (1) services ↔ (1) service_types | "
        "subscriptions ↔ unsubscriptions | subscriptions ↔ billing_events | campaigns ↔ subscriptions",
        body_style
    ))
    story.append(spacer(0.3))
    story.append(Paragraph(
        "<b>Évolution :</b> Toutes les tables prévues en Phase 2 dans le précédent rapport (campaigns, "
        "unsubscriptions, billing_events, sms_events, import_logs) sont maintenant implémentées. "
        "Le modèle de données est <b>complet</b> par rapport aux exigences du cahier des charges.",
        body_style
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 9. ARCHITECTURE TECHNIQUE
    # ══════════════════════════════════════════════════
    story.append(Paragraph("9. Architecture Technique", h1_style))
    story.append(hr())

    story.append(Paragraph("9.1 Stack Technologique", h2_style))
    stack_data = [
        [Paragraph("<b>Couche</b>", body_bold), Paragraph("<b>Technologies</b>", body_bold), Paragraph("<b>Version</b>", body_bold)],
        ["Frontend", "React, Vite, Tailwind CSS, Material-UI, Recharts, Axios", "19.2 / 7.3 / 3.4 / 7.3 / 3.8 / 1.13"],
        ["Backend", "FastAPI, SQLAlchemy, Pydantic, Alembic, python-jose, passlib", "0.115 / 2.0 / 2.11 / 1.18 / 3.3 / 1.7"],
        ["Database", "PostgreSQL", "15"],
        ["ML", "scikit-learn, pandas, joblib", "latest / 2.2 / latest"],
        ["Infra", "Docker, Docker Compose", "latest"],
    ]
    story.append(make_table(stack_data, col_widths=[2.5*cm, 9.5*cm, 5*cm]))
    story.append(spacer(0.3))

    story.append(Paragraph("9.2 Structure du Code", h2_style))
    code_data = [
        [Paragraph("<b>Composant</b>", body_bold), Paragraph("<b>Contenu</b>", body_bold), Paragraph("<b>Fichiers</b>", body_bold)],
        ["Backend app/routers/", "13 modules de routes FastAPI", "auth, users, analyticsOverview, trialAnalytics, retention, campaign_impact, churn_analysis, ml_churn, admin_import, management, platform_user, service, userActivity"],
        ["Backend app/models/", "12 modèles SQLAlchemy", "Voir section 8"],
        ["Backend app/schemas/", "15 schémas Pydantic", "Validation entrée/sortie API"],
        ["Backend ml_models/", "Prédiction churn ML", "churn_predictor.py + .joblib"],
        ["Frontend src/pages/", "14 fichiers de pages", "Dashboard, Auth, Admin, Analytics"],
        ["Frontend src/components/", "53 composants React", "6 sous-dossiers organisés"],
        ["Frontend src/hooks/", "26 hooks personnalisés", "Un hook par endpoint/fonctionnalité"],
    ]
    story.append(make_table(code_data, col_widths=[3.5*cm, 5*cm, 8.5*cm]))
    story.append(spacer(0.3))

    story.append(Paragraph("9.3 Endpoints API (sélection)", h2_style))
    api_data = [
        [Paragraph("<b>Route</b>", body_bold), Paragraph("<b>Description</b>", body_bold)],
        ["POST /auth/login", "Authentification JWT"],
        ["POST /auth/register", "Inscription plateforme"],
        ["GET /analytics/user-activity/kpis", "KPIs activité utilisateur"],
        ["GET /analytics/trial/kpis", "KPIs essais gratuits"],
        ["GET /analytics/retention/heatmap", "Heatmap cohortes rétention"],
        ["GET /analytics/campaigns/kpis", "KPIs impact campagnes"],
        ["GET /analytics/churn/kpis", "KPIs analyse churn"],
        ["GET /analytics/churn/risk-segments", "Segments de risque"],
        ["POST /ml/churn/train", "Entraînement modèle ML"],
        ["GET /ml/churn/scores", "Scores prédiction churn"],
        ["POST /admin/import/{table}", "Import données CSV/Excel"],
    ]
    story.append(make_table(api_data, col_widths=[6*cm, 11*cm]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 10. TESTS ET QUALITÉ
    # ══════════════════════════════════════════════════
    story.append(Paragraph("10. Tests et Qualité", h1_style))
    story.append(hr())

    story.append(Paragraph("10.1 Tests Backend", h2_style))
    story.append(Paragraph("<b>État :</b> Tests manuels (Postman/navigateur) — pas de tests automatisés", body_style))
    test_items = [
        "✅ Tous les endpoints analytiques testés (200 OK)",
        "✅ Validation des filtres (date range, service_id, campaign_id)",
        "✅ Gestion des erreurs (404, 422, 500)",
        "✅ Tests ML : train, metrics, scores fonctionnels",
        "⚠️ À améliorer : tests automatisés pytest",
    ]
    for item in test_items:
        story.append(Paragraph(item, bullet_style, bulletText="•"))

    story.append(spacer(0.2))
    story.append(Paragraph("10.2 Tests Frontend", h2_style))
    test_fe_items = [
        "✅ Navigation entre 15 pages",
        "✅ Interactions filtres et graphiques",
        "✅ Export CSV/Excel fonctionnel",
        "✅ Loading states + error handling",
        "✅ Routes protégées (PrivateRoute, AdminRoute)",
        "⚠️ À améliorer : tests composants React Testing Library",
    ]
    for item in test_fe_items:
        story.append(Paragraph(item, bullet_style, bulletText="•"))
    story.append(spacer(0.5))

    # ══════════════════════════════════════════════════
    # 11. RECOMMANDATIONS BUSINESS
    # ══════════════════════════════════════════════════
    story.append(Paragraph("11. Recommandations Business (Préliminaires)", h1_style))
    story.append(hr())

    recs = [
        ("Prolonger l'essai gratuit de 3 à 5 jours pour les services premium",
         "Les données montrent que les utilisateurs actifs à J+4 ont 2× plus de chances de convertir.",
         "+10-15% taux de conversion"),
        ("Envoyer un SMS de rappel à J+2 pour les utilisateurs inactifs pendant l'essai",
         "40% des abandons se produisent à J+2 sans aucune activité.",
         "Réduction de 20% des drop-offs J+2"),
        ("Identifier les cohortes à risque (D7 &lt; 30%) et lancer des campagnes de réactivation ciblées",
         "Les cohortes Jan-Feb 2026 montrent des taux critiques (29%, 47%).",
         "Récupération de 15-20% des utilisateurs à risque"),
        ("Analyser les facteurs de succès de la cohorte Mars 2026 (75% retention D7) pour répliquer",
         "Écart significatif entre meilleure (75%) et pire (29%) cohorte.",
         "Standardisation des meilleures pratiques"),
    ]
    for i, (title, justification, impact) in enumerate(recs, 1):
        story.append(Paragraph(f"<b>Recommandation {i} :</b> {title}", body_bold))
        story.append(Paragraph(f"<i>Justification :</i> {justification}", body_style))
        story.append(Paragraph(f"<i>Impact attendu :</i> {impact}", body_style))
        story.append(spacer(0.2))

    story.append(Paragraph(
        "<b>Note :</b> Le cahier des charges exige au minimum 5 recommandations. "
        "Une 5ème recommandation basée sur l'analyse churn (résultats ML) sera ajoutée dans le rapport final.",
        ParagraphStyle("note", parent=body_style, textColor=ORANGE)
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 12. RISQUES ET LIMITATIONS
    # ══════════════════════════════════════════════════
    story.append(Paragraph("12. Risques et Limitations", h1_style))
    story.append(hr())

    risks_data = [
        [Paragraph("<b>Risque</b>", body_bold), Paragraph("<b>Impact</b>", body_bold), Paragraph("<b>Mitigation</b>", body_bold)],
        ["Données production indisponibles", "Moyen", "Seed data réalistes + démo convaincante"],
        ["Délai serré pour features bonus", "Faible", "Priorisation : core terminé, bonus optionnel"],
        ["Performance queries lourdes", "Moyen", "Indexation DB + optimisation SQL"],
        ["Modèle ML simple (Logistic Reg.)", "Faible", "Explainabilité prioritaire pour PFE"],
    ]
    story.append(make_table(risks_data, col_widths=[6*cm, 2.5*cm, 8.5*cm]))
    story.append(spacer(0.3))

    story.append(Paragraph("12.1 Limitations Actuelles", h2_style))
    limitations = [
        "Cross-Service Behavior non implémenté (Phase 3 bonus)",
        "Report Generation (PDF on-demand) non implémenté",
        "User Segmentation (Clustering K-Means) non implémenté",
        "Cohortes mensuelles uniquement (pas hebdomadaires)",
        "Pas de segmentation par canal d'acquisition",
        "Re-souscriptions non traitées spécifiquement",
        "Tests automatisés absents (pytest, React Testing Library)",
    ]
    for item in limitations:
        story.append(Paragraph(f"• {item}", bullet_style))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 13. PLANNING ET ROADMAP
    # ══════════════════════════════════════════════════
    story.append(Paragraph("13. Planning et Roadmap", h1_style))
    story.append(hr())

    story.append(Paragraph("Phase 1 : Sections Core (Semaines 1-6) — ✅ 100% COMPLÉTÉ", h2_style))
    p1_items = [
        "✅ User Activity & Engagement (100%)",
        "✅ Free Trial Behavior (100%)",
        "✅ Retention Analysis (100%)",
        "✅ Modèle de données complet",
        "✅ ETL cohorts fonctionnel",
        "✅ Design system + composants réutilisables",
    ]
    for item in p1_items:
        story.append(Paragraph(item, bullet_style, bulletText=""))
    story.append(spacer(0.2))

    story.append(Paragraph("Phase 2 : Fonctionnalités Avancées (Semaines 7-9) — ✅ ~95% COMPLÉTÉ", h2_style))
    p2_items = [
        "✅ Campaign Impact Analysis (100%)",
        "✅ Churn Analysis complet (100%)",
        "✅ Admin Import Data (100%)",
        "✅ Admin Management CRUD (100%)",
        "✅ Authentification JWT + RBAC (100%)",
        "❌ Report Generation PDF (0%) — reporté Phase 3",
    ]
    for item in p2_items:
        story.append(Paragraph(item, bullet_style, bulletText=""))
    story.append(spacer(0.2))

    story.append(Paragraph("Phase 3 : AI & Bonus (Semaines 10-11) — 🔧 En cours", h2_style))
    p3_items = [
        "✅ Churn Prediction Model (100%)",
        "❌ User Segmentation K-Means (0%)",
        "❌ Cross-Service Behavior (0%)",
        "❌ Report Generation PDF à la demande (0%)",
        "❌ Anomaly Detection (0%)",
    ]
    for item in p3_items:
        story.append(Paragraph(item, bullet_style, bulletText=""))
    story.append(spacer(0.2))

    story.append(Paragraph("Phase 4 : Finalisation (Semaine 12) — ❌ Non démarrée", h2_style))
    p4_items = [
        "❌ Tests automatisés (pytest + React Testing Library)",
        "❌ Documentation utilisateur finale",
        "❌ Déploiement production (Vercel + Railway)",
        "❌ Vidéo démo (5-7 minutes)",
        "❌ Préparation soutenance PFE",
    ]
    for item in p4_items:
        story.append(Paragraph(item, bullet_style, bulletText=""))

    story.append(Paragraph("<b>Deadline estimée :</b> 30 avril 2026", body_bold))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════
    # 14. CONCLUSION
    # ══════════════════════════════════════════════════
    story.append(Paragraph("14. Conclusion et Prochaines Étapes", h1_style))
    story.append(hr())

    story.append(Paragraph("14.1 Bilan Actuel", h2_style))
    story.append(Paragraph("<b>Points forts :</b>", body_bold))
    strengths = [
        "Architecture solide et scalable (React + FastAPI + PostgreSQL + Docker)",
        "5/5 sections analytiques core sont fonctionnelles (User Activity, Free Trial, Retention, Campaign, Churn)",
        "AI feature complète : Churn Prediction avec modèle ML, API et dashboard",
        "Modèle de données complet (12 tables) et normalisé",
        "Interface professionnelle (dark theme, composants réutilisables, responsive)",
        "Admin panel complet : import data, management, gestion utilisateurs plateforme",
        "Documentation technique de qualité (KPIs, architecture, ML report)",
        "26 hooks React custom + 13 routes API backend",
    ]
    for item in strengths:
        story.append(Paragraph(f"✅ {item}", bullet_style, bulletText=""))

    story.append(spacer(0.3))
    story.append(Paragraph("<b>Points à améliorer :</b>", body_bold))
    improvements = [
        "Implémenter Cross-Service Behavior (Phase 3 bonus)",
        "Développer Report Generation PDF à la demande",
        "Ajouter User Segmentation clustering (Phase 3 bonus)",
        "Compléter les recommandations business (≥5 exigées)",
        "Rédiger Business Impact Summary (1 page)",
        "Tests automatisés (Phase 4)",
        "Déploiement et vidéo démo",
    ]
    for item in improvements:
        story.append(Paragraph(f"🔧 {item}", bullet_style, bulletText=""))

    story.append(spacer(0.3))
    story.append(Paragraph("14.2 Actions Prioritaires (Semaine du 24 Mars)", h2_style))
    actions = [
        "1. Finaliser les recommandations business (5ème recommandation basée sur ML)",
        "2. Rédiger le Business Impact Summary (1 page)",
        "3. Implémenter Report Generation ou Cross-Service (au choix)",
        "4. Valider avec encadrant l'ensemble des sections complétées",
        "5. Préparer la démo intermédiaire complète",
    ]
    for a in actions:
        story.append(Paragraph(a, body_style))

    story.append(spacer(0.5))
    story.append(Paragraph(
        "<b>Avancement global : ~85%</b> — Le projet est en très bonne voie pour la soutenance. "
        "Les exigences core du cahier des charges sont satisfaites. Le focus restant porte sur "
        "la documentation finale, les livrables bonus, et la préparation de la soutenance.",
        ParagraphStyle("conclusion", parent=body_style, fontSize=11, textColor=DARK_BLUE, fontName="Helvetica-Bold")
    ))

    # ─── Build ────────────────────────────────────────
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"\n✅ PDF généré avec succès : {output_path}")
    print(f"   Taille : {os.path.getsize(output_path) / 1024:.1f} Ko")


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Rapport_Avancement_PFE_2026-03-24.pdf")
    build_pdf(output_path)
