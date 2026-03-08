from decimal import Decimal


# ── Volumétrie cible ──────────────────────────────────────
USER_COUNT     = 10_000
ACTIVITY_COUNT = 20_000
SMS_COUNT      = 5_000
BATCH_SIZE     = 500


# ── Distribution utilisateurs ─────────────────────────────
USER_STATUS_WEIGHTS = {
    "choices": ["active", "inactive"],
    "weights": [6, 94],
}


# ── Distribution subscriptions ────────────────────────────
# paid_active       → converti et paie        → status = active
# inactive_no_balance→ converti mais solde vide→ status = active
# trial_active      → essai en cours           → status = trial
# trial_expired     → essai fini sans payer    → status = expired
# churned_voluntary → désabo volontaire        → status = cancelled
# churned_technical → désabo technique         → status = cancelled
SUBSCRIPTION_SCENARIOS = {
    "choices": [
        "paid_active",
        "inactive_no_balance",
        "trial_active",
        "trial_expired",
        "churned_voluntary",
        "churned_technical",
    ],
    "weights": [6, 46, 8, 8, 20, 12],
    # Total = 100%
    # active    = 6+46 = 52%
    # trial     = 8%
    # expired   = 8%
    # cancelled = 20+12 = 32%
}

SUBSCRIPTION_RATIO = 0.85


# ── Téléphonie Tunisie (TT only) ──────────────────────────
TUNISIE_PREFIXES = [
    "+21690", "+21691", "+21692", "+21693", "+21694",
    "+21695", "+21696", "+21697", "+21698", "+21699",
]


# ── Churn reasons ─────────────────────────────────────────
CHURN_REASONS_VOLUNTARY = [
    "USER_STOP_SMS",
    "WEB_CANCELLATION",
    "NOT_INTERESTED",
    "TOO_EXPENSIVE",
    "CONTENT_QUALITY",
]

CHURN_REASONS_TECHNICAL = [
    "INSUFFICIENT_BALANCE",
    "BILLING_FAILURE_3X",
    "PHONE_INVALID",
    "CARRIER_BLOCK",
]

BILLING_FAILURES = [
    "Solde insuffisant",
    "Erreur opérateur",
    "Ligne bloquée",
    "Timeout réseau",
]


# ── Services réels ────────────────────────────────────────
SERVICES_DATA = [
    {
        "name": "ElJournal",
        "description": "Actualités personnalisées en temps réel",
        "type": "daily",
    },
    {
        "name": "Esports.tn",
        "description": "Plateforme de gaming compétitif avec récompenses (LoL, Valorant, TFT)",
        "type": "weekly",
    },
    {
        "name": "ttoons",
        "description": "Contenu éducatif et divertissant pour enfants",
        "type": "weekly",
    },
    {
        "name": "Tawer",
        "description": "Développement personnel avec Hamza El Balloumi",
        "type": "daily",
    },
]


# ── Service types ─────────────────────────────────────────
SERVICE_TYPES_DATA = [
    {
        "name": "daily",
        "billing_frequency_days": 1,
        "price": Decimal("1.00"),
        "trial_duration_days": 3,
    },
    {
        "name": "weekly",
        "billing_frequency_days": 7,
        "price": Decimal("5.00"),
        "trial_duration_days": 3,
    },
]


# ── Platform users ────────────────────────────────────────
PLATFORM_USERS_DATA = [
    {
        "email": "admin@analytics.tn",
        "password": "Admin@2026",
        "full_name": "Administrateur Principal",
        "role": "admin",
    },
    {
        "email": "data.analyst@analytics.tn",
        "password": "Analyst@2026",
        "full_name": "Data Analyst",
        "role": "analyst",
    },
    {
        "email": "manager@analytics.tn",
        "password": "Manager@2026",
        "full_name": "Product Manager",
        "role": "analyst",
    },
]


# ── Campaigns ─────────────────────────────────────────────
CAMPAIGNS_DATA = [
    {
        "name": "Ramadan 2025 - Tous Services",
        "description": "Campagne promotionnelle Ramadan 2025",
        "service_index": None,
        "send_datetime": "2025-03-20T10:00:00",
        "target_size": 15000,
        "cost": Decimal("525.00"),
        "campaign_type": "promotion",
        "status": "sent",
    },
    {
        "name": "Acquisition ElJournal - Janvier 2025",
        "description": "Croissance abonnés ElJournal début 2025",
        "service_index": 0,
        "send_datetime": "2025-01-10T09:00:00",
        "target_size": 8000,
        "cost": Decimal("280.00"),
        "campaign_type": "acquisition",
        "status": "sent",
    },
    {
        "name": "Retention Esports - Septembre 2025",
        "description": "Réengagement utilisateurs Esports.tn",
        "service_index": 1,
        "send_datetime": "2025-09-05T10:00:00",
        "target_size": 5000,
        "cost": Decimal("175.00"),
        "campaign_type": "retention",
        "status": "sent",
    },
    {
        "name": "Réactivation ttoons - Octobre 2025",
        "description": "Réactiver parents inactifs ttoons",
        "service_index": 2,
        "send_datetime": "2025-10-15T11:00:00",
        "target_size": 4000,
        "cost": Decimal("140.00"),
        "campaign_type": "reactivation",
        "status": "sent",
    },
    {
        "name": "Eid 2025 - Multi-services",
        "description": "Offre Eid El Fitr tous services",
        "service_index": None,
        "send_datetime": "2025-04-10T09:00:00",
        "target_size": 12000,
        "cost": Decimal("420.00"),
        "campaign_type": "promotion",
        "status": "sent",
    },
    {
        "name": "Acquisition Tawer - Novembre 2025",
        "description": "Lancement campagne Tawer mass market",
        "service_index": 3,
        "send_datetime": "2025-11-01T09:00:00",
        "target_size": 10000,
        "cost": Decimal("350.00"),
        "campaign_type": "acquisition",
        "status": "sent",
    },
    {
        "name": "Réactivation ElJournal - Décembre 2025",
        "description": "Réactiver 26k users inactifs solde insuffisant",
        "service_index": 0,
        "send_datetime": "2025-12-01T10:00:00",
        "target_size": 6000,
        "cost": Decimal("210.00"),
        "campaign_type": "reactivation",
        "status": "sent",
    },
]
