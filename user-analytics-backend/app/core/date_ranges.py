from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.utils.temporal import AnchorSource, get_data_bounds

# Known data window for Hawala production snapshots loaded into analytics.
DATA_START_DATE = date(2025, 9, 1)
DATA_END_DATE = date(2025, 10, 31)


def resolve_date_range(
    start_date: Optional[date],
    end_date: Optional[date],
    *,
    db: Session | None = None,
    source: AnchorSource = "analytics",
) -> tuple[date, date]:
    """Resolve API date filters to a deterministic range.

    - Defaults are derived from actual table bounds for the requested source.
    - User-provided filters are clamped to available data range.
    - End date can never exceed the latest available non-future data.
    """
    if db is not None:
        data_start_dt, data_end_dt = get_data_bounds(db, source=source)
        data_start = data_start_dt.date()
        data_end = data_end_dt.date()
    else:
        data_start = DATA_START_DATE
        data_end = DATA_END_DATE

    end_dt = end_date or data_end
    start_dt = start_date or data_start

    if end_dt > data_end:
        end_dt = data_end
    if start_dt < data_start:
        start_dt = data_start

    if start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    if start_dt < data_start:
        start_dt = data_start
    if end_dt > data_end:
        end_dt = data_end
    if start_dt > end_dt:
        start_dt = end_dt

    return start_dt, end_dt
