# app/seeds/utils.py

import uuid
import random
from datetime import datetime, timedelta


# =====================================================
# UUID
# =====================================================

def uid() -> uuid.UUID:
    """Generate UUID v4."""
    return uuid.uuid4()


# =====================================================
# RANDOM DATE
# =====================================================

def rand_date(days_back_min: int = 1, days_back_max: int = 90) -> datetime:
    """Return random past datetime."""
    offset = random.randint(days_back_min, days_back_max)

    return datetime.utcnow() - timedelta(
        days=offset,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


# =====================================================
# WEIGHTED CHOICE
# =====================================================

def weighted_choice(choices: list, weights: list):
    """Shortcut for weighted random choice."""
    return random.choices(choices, weights=weights, k=1)[0]


# =====================================================
# PROGRESS BAR (FIX IMPORT ERROR)
# =====================================================

def print_progress(current: int, total: int, prefix="Generating"):
    """
    Lightweight progress indicator.
    Prevents console spam while showing progress.
    """
    percent = (current / total) * 100 if total else 0
    print(f"\r{prefix}: {current}/{total} ({percent:.1f}%)", end="")


# =====================================================
# GET OR CREATE (OPTIONAL)
# =====================================================

def get_or_create(db, model, filter_kwargs: dict, create_kwargs: dict):
    existing = db.query(model).filter_by(**filter_kwargs).first()

    if existing:
        return existing, False

    obj = model(**filter_kwargs, **create_kwargs)
    db.add(obj)
    return obj, True