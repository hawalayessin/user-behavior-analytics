"""Quick verification: render template + generate PDF with fallback data."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

from app.services.enterprise_report_ai import generate_rule_based_insights, resolve_ai_insights
from app.services.pdf_report_service import PDFReportService

# --- Test 1: Fallback covers all keys ---
fallback = generate_rule_based_insights({
    "active_users": 71672,
    "global_churn_rate": 3.7,
    "trial_churn_rate": 63.5,
    "retention_d30": 45.2,
    "retention_d7": 45.2,
    "campaign_roi": 3.5,
    "anomaly_score": 0.12,
    "conversion_rate": 6.8,
    "avg_lifetime_days": 28.4,
    "high_risk_users": 302,
    "total_campaigns": 12,
})
print(f"[TEST 1] Fallback keys: {len(fallback)}")
for k, v in fallback.items():
    status = "OK" if v and len(v) > 10 else "EMPTY!"
    print(f"  {k}: {status} ({len(v)} chars)")

assert len(fallback) >= 28, f"Expected 28+ keys, got {len(fallback)}"
assert all(v and len(v) > 10 for v in fallback.values()), "Some fallback values are empty!"
print("[TEST 1] PASSED: All 28 fallback keys populated\n")

# --- Test 2: resolve_ai_insights merges correctly ---
partial_gemini = {"ai_summary": "Gemini generated this summary.", "ai_churn_explanations": ""}
merged = resolve_ai_insights(partial_gemini, {
    "active_users": 71672, "global_churn_rate": 3.7, "conversion_rate": 6.8,
})
assert merged["ai_summary"] == "Gemini generated this summary.", "Gemini value not preserved"
assert merged["ai_churn_explanations"] != "", "Empty Gemini key not filled by fallback"
print("[TEST 2] PASSED: Merge logic correct\n")

# --- Test 3: Resolve with None (full fallback) ---
full_fallback = resolve_ai_insights(None, {"active_users": 5000, "global_churn_rate": 5.0})
assert len(full_fallback) >= 28
print("[TEST 3] PASSED: Full fallback with None gemini response\n")

# --- Test 4: PDF generation (with fallback, no Gemini) ---
svc = PDFReportService()
result = svc.generate_pdf(
    report_config={
        "language": "fr",
        "include_ai_insights": False,  # Skip Gemini, use fallback
        "period_start": "2025-09-01",
        "period_end": "2025-10-31",
        "services_included": ["ElJournal", "Esports.tn", "ttoons", "Tawer"],
        "generated_by_name": "Test User",
    },
    kpis={"active_users": 71672, "conversion_rate": 6.8, "churn_rate": 3.7, "retention_d7": 45.2, "arpu": 12.4, "high_risk_users": 302},
    churn_data={"global_churn_rate": 3.7, "trial_churn_rate": 63.5, "avg_lifetime_days": 28.4},
    segments={
        "power_users": {"pct": 2.2, "arpu": 24.5, "churn": 23.6, "label": "Power Users"},
        "regular_loyals": {"pct": 2.4, "arpu": 8.3, "churn": 23.2, "label": "Loyaux Reguliers"},
        "occasional": {"pct": 3.4, "arpu": 3.5, "churn": 21.8, "label": "Occasionnels"},
        "trial_only": {"pct": 92.1, "arpu": 0.0, "churn": 63.5, "label": "Trial Only"},
    },
    anomalies=[],
    campaign_data={"total_campaigns": 12, "avg_conversion_rate": 6.8, "avg_roi_per_user": 3.5},
)

print(f"[TEST 4] Report generated:")
print(f"  File: {result['filename']}")
print(f"  Size: {result['file_size_kb']} KB")
print(f"  AI source: {result['ai_source']}")
print(f"  AI fields used: {result['ai_used']}")
print(f"  Generation time: {result['generation_sec']}s")

assert result["file_size_kb"] > 0, "PDF file is empty!"
assert result["ai_source"] == "fallback", "Should be fallback when AI disabled"
print("[TEST 4] PASSED: PDF generated successfully\n")

print("=" * 50)
print("ALL TESTS PASSED!")
print(f"Report file: {result['file_path']}")
