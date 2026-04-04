from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from app.repositories import churn_repo


class _FakeResult:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class _FakeDB:
    def __init__(self, row):
        self._row = row
        self.last_sql = ""
        self.last_params = None

    def execute(self, statement, params=None):
        self.last_sql = statement.text if hasattr(statement, "text") else str(statement)
        self.last_params = params
        return _FakeResult(self._row)


def test_monthly_churn_rate_anchor_window_positive_when_unsubs_exist():
    row = SimpleNamespace(
        unsub_count=12,
        active_count=120,
        churn_rate=10.0,
        period_start=datetime(2025, 10, 1, 0, 0, 0),
        period_end=datetime(2025, 10, 31, 23, 59, 59),
    )
    db = _FakeDB(row)

    payload = churn_repo.get_monthly_churn_rate(db)

    assert payload["rate"] > 0
    assert payload["churned"] == 12
    assert payload["total"] == 120
    assert "MAX(event_datetime)" in db.last_sql


def test_churn_breakdown_anchor_window_positive_when_unsubs_exist():
    row = SimpleNamespace(
        total_unsubs=20,
        voluntary=8,
        technical=12,
        voluntary_pct=40.0,
        technical_pct=60.0,
    )
    db = _FakeDB(row)

    payload = churn_repo.get_churn_breakdown(db)

    assert payload["total"] == 20
    assert payload["voluntary"]["count"] == 8
    assert payload["technical"]["count"] == 12
    assert "MAX(event_datetime)" in db.last_sql


def test_repository_does_not_use_now_or_current_date_for_churn_windows():
    repo_source = Path(__file__).resolve().parents[1] / "app" / "repositories" / "churn_repo.py"
    content = repo_source.read_text(encoding="utf-8").upper()

    assert "NOW()" not in content
    assert "CURRENT_DATE" not in content
    assert "CURRENT_TIMESTAMP" not in content


def test_frontend_all_time_hooks_do_not_build_dates_from_current_time():
    root = Path(__file__).resolve().parents[2]
    breakdown_hook = root / "analytics-platform-front" / "src" / "hooks" / "useChurnBreakdown.js"
    kpis_hook = root / "analytics-platform-front" / "src" / "hooks" / "useChurnKPIs.js"

    breakdown_src = breakdown_hook.read_text(encoding="utf-8")
    kpis_src = kpis_hook.read_text(encoding="utf-8")

    assert "new Date(" not in breakdown_src
    assert "new Date(" not in kpis_src
    assert "if (start_date && end_date)" in breakdown_src
    assert "if (start_date && end_date)" in kpis_src
