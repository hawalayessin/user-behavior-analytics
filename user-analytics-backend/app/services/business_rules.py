"""Business rules for trial exceptions and governance summaries."""

from __future__ import annotations


def is_trial_extension(
    observed_trial_days: int | float,
    configured_trial_days: int | float,
    *,
    grace_days: int = 0,
) -> bool:
    """Return True when observed trial duration exceeds configured duration (+ optional grace)."""
    observed = max(float(observed_trial_days or 0), 0.0)
    configured = max(float(configured_trial_days or 0), 0.0)
    grace = max(int(grace_days or 0), 0)
    return observed > (configured + grace)


def build_trial_exception_summary(
    *,
    total_trials: int,
    promotion_trials: int,
    trial_extensions: int,
) -> dict[str, object]:
    """Build standardized exception-governance payload for trial/business model compliance."""
    total = max(int(total_trials or 0), 0)
    promo = max(int(promotion_trials or 0), 0)
    ext = max(int(trial_extensions or 0), 0)

    promo_pct = round((promo * 100.0 / total), 2) if total > 0 else 0.0
    ext_pct = round((ext * 100.0 / total), 2) if total > 0 else 0.0
    total_exceptions = promo + ext
    total_exceptions_pct = round((total_exceptions * 100.0 / total), 2) if total > 0 else 0.0

    if total_exceptions_pct >= 25:
        status = "high_exception_pressure"
    elif total_exceptions_pct >= 10:
        status = "moderate_exception_pressure"
    else:
        status = "controlled"

    return {
        "status": status,
        "promotion_trials": promo,
        "promotion_trials_pct": promo_pct,
        "trial_extensions": ext,
        "trial_extensions_pct": ext_pct,
        "total_exception_events": total_exceptions,
        "total_exception_events_pct": total_exceptions_pct,
        "rules_version": "trial-exceptions-v1",
    }
