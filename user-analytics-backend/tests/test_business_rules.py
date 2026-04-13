from app.services.business_rules import (
    build_trial_exception_summary,
    is_trial_extension,
)


def test_is_trial_extension_respects_grace_window() -> None:
    assert is_trial_extension(8, 7, grace_days=0) is True
    assert is_trial_extension(8, 7, grace_days=1) is False
    assert is_trial_extension(9, 7, grace_days=1) is True


def test_build_trial_exception_summary_computes_rates_and_status() -> None:
    summary = build_trial_exception_summary(
        total_trials=100,
        promotion_trials=7,
        trial_extensions=6,
    )

    assert summary["promotion_trials_pct"] == 7.0
    assert summary["trial_extensions_pct"] == 6.0
    assert summary["total_exception_events"] == 13
    assert summary["total_exception_events_pct"] == 13.0
    assert summary["status"] == "moderate_exception_pressure"
    assert summary["rules_version"] == "trial-exceptions-v1"
