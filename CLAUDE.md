# CLAUDE.md — DigMaco Analytics
## Project Context for AI Assistants

> This file is auto-loaded by Claude, Cursor,
> and GitHub Copilot to provide project context.
> Last updated: 2026-05-18

---

## PROJECT IDENTITY

```yaml
project_name: DigMaco Analytics
type: PFE — Final Year Project 2025/2026
school: POLYTECHNIQUE SOUSSE
company: DigMaco — Sousse, Tunisia
client: Tunisie Telecom
academic_year: 2025/2026

services:
  - ElJournal
  - Esports.tn
  - ttoons
  - Tawer

business_model: >
  Free trial 3 days → auto-renewal via USSD/SMS
  Transaction types: 1=new_sub 2=renewal 4=unsub

data_scope: September — October 2025 (historical)
temporal_anchor: MAX(event_datetime) not NOW()
```

---

## ARCHITECTURE
prod_db (PostgreSQL OLTP — READ ONLY)
hawala_db — tables:
subscribed_clients
transaction_histories
services
service_subscription_types
campaigns
↓
[ETL Python — etl_prod_to_analytics.py]
Extract → Transform → Load
Batch: 50,000 rows
UUID5 deterministic IDs
ON CONFLICT DO UPDATE (idempotent)
Mode demo: --demo --demo-users 50000
↓
analytics_db (PostgreSQL DWH)
Constellation schema
5 fact tables + 4 dimensions + 2 data marts
↓
FastAPI (port 8000)
19 routers found —
admin_import, analyticsOverview, auth, campaign_impact,
campaign_upload, churn_analysis, cross_service, management,
ml_churn, notes, nrr, platform_user, reports, retention,
segmentation, service, trialAnalytics, userActivity, users
JWT Auth: Admin / Analyst roles
asyncio.gather() for parallel queries
↓
React 19 + Vite (port 5173)
25 pages — listed below
44 hooks — listed below
Recharts + Tailwind CSS
Theme: CSS variables light/dark

---

## DATABASE SCHEMA — analytics_db

### Fact Tables
subscriptions (FACT)
id UUID PK
user_id UUID FK → users
service_id UUID FK → services
campaign_id UUID FK → campaigns (nullable)
subscription_start_date TIMESTAMP
subscription_end_date TIMESTAMP (nullable)
status VARCHAR
created_at TIMESTAMP

billing_events (FACT)
id UUID PK
subscription_id UUID FK → subscriptions
user_id UUID FK → users
service_id UUID FK → services
event_datetime TIMESTAMP
status VARCHAR
failure_reason TEXT (nullable)
retry_count INT
is_first_charge BOOL

unsubscriptions (FACT)
id UUID PK
subscription_id UUID FK → subscriptions
user_id UUID FK → users
service_id UUID FK → services
unsubscription_datetime TIMESTAMP
churn_type VARCHAR
churn_reason VARCHAR (nullable)
days_since_subscription INT (nullable)
last_billing_event_id UUID FK → billing_events (nullable)

sms_events (FACT)
id UUID PK
user_id UUID FK → users
campaign_id UUID FK → campaigns (nullable)
service_id UUID FK → services (nullable)
event_datetime TIMESTAMP
event_type VARCHAR
message_content TEXT (nullable)
direction VARCHAR
delivery_status VARCHAR (nullable)

user_activities (FACT)
id UUID PK
user_id UUID FK → users
service_id UUID FK → services
activity_datetime TIMESTAMP
activity_type VARCHAR
session_id VARCHAR (nullable)

### Dimension Tables
users
service_types
services
campaigns

### Data Marts
cohorts
report_history
(plus supporting ops tables: import_logs, analyst_notes, platform_users, platform_user_invites, refresh_tokens)

### Indexes
Indexes are defined both in model metadata and Alembic revisions.
Key migration files with index creation include:
- 4b9e2f7a1d3c_sms_events_hawala_lean_model_and_indexes.py
- 6c076db13bed_add_analytics_performance_indexes.py
- 85b71708c64d_add_performance_indexes_p0.py
- c1f4a2d9e8b1_extend_sms_events_for_otp_ussd_web_activation.py
- 9f4c2a1b7d10_add_refresh_tokens_table.py

Notable index families:
- billing_events: subscription/event_datetime/status/service/user composites
- subscriptions: service/date/status/user composites
- sms_events: event_datetime/event_type/service/user/channel/delivery composites + partial indexes
- cohorts: service/cohort_date
- refresh_tokens: token_hash, user_id

---

## API ENDPOINTS

Grouped by router.

admin_import.py (prefix `/admin/import`)
- POST `/csv`
- POST `/csv/confirm`
- POST `/database`
- GET `/history`
- GET `/history/{log_id}`
- GET `/schema/{table}`
- GET `/template/{table}`
- POST `/run-etl`
- GET `/run-etl/{log_id}/status`
- GET `/run-etl/{log_id}/log`
- POST `/run-etl/{log_id}/stop`
- GET `/etl-history`
Auth: required (admin for ETL ops)

analyticsOverview.py (prefix `/analytics`)
- GET `/summary`
- GET `/overview`
- GET `/status/diagnostics`
- POST `/cache/invalidate`
Auth: required

auth.py (prefix `/auth`)
- POST `/register`
- GET `/me`
- PATCH `/profile`
- POST `/profile/avatar`
- DELETE `/profile/avatar`
- POST `/invite`
- POST `/register-invite`
- POST `/register-invite/verify`
- POST `/login`
- POST `/refresh`
- POST `/logout`
- POST `/forgot-password`
- POST `/verify-reset-token`
- POST `/reset-password`
Auth: mixed (login/register/refresh/logout/public; profile/invite protected)

campaign_impact.py (prefix `/analytics/campaigns`)
- GET `/dashboard`
- GET `/list`
- GET `/overview`
- GET `/by-type`
- GET `/top`
- GET `/trend`
- GET `/kpis`
- GET `/performance`
- GET `/comparison`
- GET `/timeline`
Auth: required

campaign_upload.py (prefix `/admin/management/campaigns`)
- POST `/upload-targets`
Auth: admin

churn_analysis.py (prefix `/analytics/churn`)
- GET `/dashboard`
- GET `/kpis`
- GET `/reactivation/kpis`
- GET `/reactivation/by-service`
- GET `/trend`
- GET `/by-service`
- GET `/lifetime`
- GET `/retention`
Auth: required

cross_service.py (prefix `/analytics/cross-service`)
- GET `/overview`
- GET `/co-subscriptions`
- GET `/migrations`
- GET `/distribution`
- GET `/all`
Auth: required

management.py (prefix `/admin/management`)
- GET `/services`
- POST `/services`
- PUT `/services/{service_id}`
- DELETE `/services/{service_id}`
- GET `/campaigns`
- POST `/campaigns`
- PUT `/campaigns/{campaign_id}`
- DELETE `/campaigns/{campaign_id}`
Auth: admin

ml_churn.py (prefix `/ml/churn`)
- POST `/train`
- POST `/train/start`
- GET `/train/{job_id}/status`
- GET `/metrics`
- GET `/governance`
- GET `/scores`
- POST `/scores/recompute`
Auth: required/admin for train

notes.py (prefix `/notes`)
- POST ``
- GET ``
- GET `/{note_id}`
- PUT `/{note_id}`
- DELETE `/{note_id}`
- GET `/context`
Auth: required

nrr.py (mounted with `/analytics` prefix)
- GET `/analytics/nrr`
Auth: required

platform_user.py (mounted with `/platform-users` prefix)
- GET `/platform-users`
- GET `/platform-users/{user_id}`
- POST `/platform-users`
- PUT `/platform-users/{user_id}`
- PATCH `/platform-users/{user_id}/status`
- PATCH `/platform-users/{user_id}/role`
- DELETE `/platform-users/{user_id}`
Auth: admin

reports.py (prefix `/reports`)
- POST `/generate`
- GET `/status/{report_id}`
- GET `/history`
- GET `/download/{report_id}`
Auth: required

retention.py (prefix `/analytics`)
- POST `/retention/recompute`
- GET `/retention/kpis`
- GET `/retention/heatmap`
- GET `/retention/curve`
- GET `/retention/cohorts-list`
Auth: required/admin for recompute

segmentation.py (prefix `/analytics/segmentation`)
- GET `/kpis`
- GET `/clusters`
- GET `/profiles`
- POST `/train`
Auth: required

service.py (prefix `/services`)
- GET ``
Auth: required

trialAnalytics.py (prefix `/analytics`)
- GET `/trial/kpis`
- GET `/trial/timeline`
- GET `/trial/by-service`
- GET `/trial/users`
- GET `/trial/dropoff-by-day`
- GET `/trial/dropoff-causes`
- GET `/churn/breakdown`
Auth: required

userActivity.py (prefix `/analytics`)
- GET `/user-activity`
Auth: required

users.py (prefix `/users`)
- GET ``
- GET `/trial`
- GET `/{user_id}`
Auth: required

---

## DATA VOLUMES (from ETL logs and code)

```yaml
subscriptions:    1,172,575
users:              945,580
billing_events:     440,707
paying_users:        75,044
conversion_rate:       6.8%
churn_rate:            3.7%
high_risk_users:         302
demo_users:           50,000
```

---

## ML MODELS

### Churn Prediction
```yaml
algorithm: Logistic Regression
file: ml_models/churn_predictor.py
features:
  - days_since_last_activity
  - nb_activities_7d
  - nb_activities_30d
  - billing_failures_30d
  - days_since_first_charge
  - avg_retention_d7

split: train_test_split random_state=42
anti_leakage:
  ref_time: LEAST(start + 7d, NOW())
  label: churn in next 30 days after ref_time

metrics:
  roc_auc: available in computed metrics artifact
  pr_auc: available in computed metrics artifact
  threshold: dynamic optimal threshold selection (fallback 0.4)
```

### K-Means Segmentation
```yaml
algorithm: K-Means
file: ml_models/segmentation_trainer.py
k: 4
labels:
  - Trial Only
  - Occasional Users
  - Regular Loyals
  - Power Users
insight: rank_map built by cluster mean revenue
```

### Anomaly Detection
```yaml
algorithm: Z-Score + IsolationForest hybrid
file: ml_models/anomalies.py
thresholds:
  MEDIUM: z-score based
  HIGH: z-score based
  CRITICAL: z-score based
monitored_metrics:
  - DAU
  - churn_rate
  - revenue
  - renewals
direction: z>0 spike, z<0 drop
```

---

## ETL PIPELINE

### 9 Steps (in order)
Step 1: etl_service_types()
Source: service_subscription_types
Target: service_types
Step 2: etl_services()
Source: services
Target: services
Step 3: etl_users()
Source: subscribed_clients
Target: users
Step 4: etl_subscriptions()
Source: transaction_histories (type=1,2,4)
Target: subscriptions
Status map:
1→active  -1→cancelled
-2→billing_failed  0→pending
Step 5: etl_billing_events()
Source: transaction_histories
Target: billing_events
Status map:
0→pending  1→success
2→failed   3→cancelled
is_first_charge: first success per sub UUID
Step 6: etl_unsubscriptions()
Source: transaction_histories (type=4)
Target: unsubscriptions
Step 7: etl_user_activities()
Source: transaction_histories
Target: user_activities
Step 8: etl_sms_events()
Source: SMS-related hawala tables
Target: sms_events
Step 9: etl_cohorts() → compute_cohorts.py
Target: cohorts

### Key ETL Rules

UUID5 namespaces:
USER_NS = 1111...
SUB_NS = 2222...
BILLING_NS = 3333...
SERVICE_NS = 4444...
All statuses lowercase in analytics_db
ON CONFLICT DO UPDATE on all tables
Batch size: 50,000 rows
Retry: 3 attempts exponential backoff
Demo mode: `--limit` + `--dry-run`

---

## PERFORMANCE OPTIMIZATIONS APPLIED
Optimization              Before    After   Gain
────────────────────────────────────────────────
asyncio.gather /summary   present   present parallelized
Alembic indexes           present   expanded over revisions
Sargable queries          mixed     mixed (still some DATE())
Pool tuning               default   size=10 overflow=20
statement_timeout         none      10s set in DB engine

Non-sargable patterns fixed/remaining:
- Remaining in several routers/scripts: `DATE(col)` filters
- Remaining in training code: `NOW()` temporal anchors

---

## SECURITY

```yaml
auth: JWT HS256
expiry: 15m access token + 7d refresh cookie rotation
secret: SECRET_KEY env var (default fallback exists: change-me)
roles:
  Admin: full access + ETL + ML training
  Analyst: dashboards + IA + reports

critical_issue: secrets committed in .env currently
  DATABASE_URL: ***masked***
  PROD_CONN: ***masked***
  ANALYTICS_CONN: ***masked***
  SMTP_USER: ***masked***
  SMTP_PASSWORD: ***masked***
  GEMINI_API_KEY: ***masked***
```

---

## FRONTEND PAGES

- src/pages/auth/LoginPage.jsx → /login
- src/pages/auth/RegisterPage.jsx → /register
- src/pages/auth/ForgotPasswordPage.jsx → /forgot-password
- src/pages/auth/ResetPasswordPage.jsx → /reset-password
- src/pages/RootRedirect.jsx → /
- src/pages/dashboard/DashboardPage.jsx → /dashboard
- src/pages/UserActivityPage.jsx → /analytics/behaviors
- src/pages/dashboard/FreeTrialBehaviorPage.jsx → /analytics/trial
- src/pages/dashboard/RetentionPage.jsx → /analytics/retention
- src/pages/dashboard/CampaignImpactPage.jsx → /analytics/campaigns
- src/pages/dashboard/ChurnAnalysisPage.jsx → /analytics/churn
- src/pages/dashboard/AIChurnInsights.jsx → /analytics/churn-prediction
- src/pages/dashboard/CrossServiceBehaviorPage.jsx → /analytics/cross-service
- src/pages/dashboard/UserSegmentationPage.jsx → /analytics/segmentation
- src/pages/dashboard/AnomalyDetectionPage.jsx → /analytics/anomalies
- src/pages/SubscribersPage.jsx → /management/subscribers
- src/pages/admin/ReportGeneratorPage.jsx → /admin/reports
- src/pages/account/ProfileSettingsPage.jsx → /account/profile
- src/pages/NotesPage.jsx → /notes
- src/pages/admin/ImportDataPage.jsx → /admin/import (admin)
- src/pages/admin/ManagementPage.jsx → /admin/management (admin)
- src/pages/admin/SystemSettingsPage.jsx → /admin/settings (admin)
- src/pages/admin/RunAIModelsPage.jsx → /admin/run-ai-models (admin)
- src/pages/platform-users/PlatformUsersPage.jsx → /admin/users (admin)

---

## FRONTEND HOOKS

Hooks found (44):
useAnomalies, useCampaignComparison, useCampaignImpactDashboard, useCampaignKPIs,
useCampaignPerformance, useCampaignTimeline, useChurnBreakdown, useChurnCurve,
useChurnDashboard, useChurnKPIs, useChurnModelGovernance, useChurnPredictionMetrics,
useChurnPredictionScores, useChurnPredictionTrain, useChurnReasons, useCohortsTable,
useCrossService, useDashboardMetrics, useETLPipeline, useForgotPassword,
useImportData, useManagement, useNRR, useOverview, useReactivationByService,
useReactivationKPIs, useRetentionCurve, useRetentionHeatmap, useRetentionKPIs,
useRetentionRecompute, useRiskSegments, useSegmentationClusters, useSegmentationKPIs,
useSegmentationProfiles, useSegmentationTrain, useSubscribersKPIs, useTimeToChurn,
useToast, useTrialDropoffByDay, useTrialDropoffCauses, useTrialKPIs, useTrialUsers,
useUserActivity, useUsers.

---

## CSS THEME VARIABLES

```css
/* Dark theme */
--color-bg-primary: #0f172a;
--color-bg-card: #1e293b;
--color-bg-elevated: #263348;
--color-border: #334155;
--color-border-subtle: #1e293b;
--color-text-primary: #f1f5f9;
--color-text-secondary: #cbd5e1;
--color-text-muted: #94a3b8;
--color-text-disabled: #475569;
--color-primary: #3b82f6;
--color-primary-hover: #2563eb;
--color-primary-bg: rgba(59, 130, 246, 0.15);
--color-success: #22c55e;
--color-success-bg: rgba(34, 197, 94, 0.12);
--color-warning: #f97316;
--color-warning-bg: rgba(249, 115, 22, 0.12);
--color-danger: #ef4444;
--color-danger-bg: rgba(239, 68, 68, 0.12);
--color-info: #06b6d4;
--color-info-bg: rgba(6, 182, 212, 0.12);
--color-amber: #f59e0b;
--color-amber-bg: rgba(245, 158, 11, 0.12);
--color-purple: #a855f7;
--color-purple-bg: rgba(168, 85, 247, 0.12);
--color-card-shadow: none;
--color-topbar-blur: rgba(15, 23, 42, 0.8);

/* Light theme */
--color-bg-primary: #f8fafc;
--color-bg-card: #ffffff;
--color-bg-elevated: #f1f5f9;
--color-border: #e2e8f0;
--color-border-subtle: #f1f5f9;
--color-text-primary: #0f172a;
--color-text-secondary: #334155;
--color-text-muted: #64748b;
--color-text-disabled: #94a3b8;
--color-primary: #2563eb;
--color-primary-hover: #1d4ed8;
--color-primary-bg: rgba(37, 99, 235, 0.08);
--color-success: #16a34a;
--color-success-bg: rgba(22, 163, 74, 0.08);
--color-warning: #ea580c;
--color-warning-bg: rgba(234, 88, 12, 0.08);
--color-danger: #dc2626;
--color-danger-bg: rgba(220, 38, 38, 0.08);
--color-info: #0891b2;
--color-info-bg: rgba(8, 145, 178, 0.08);
--color-amber: #d97706;
--color-amber-bg: rgba(217, 119, 6, 0.08);
--color-purple: #9333ea;
--color-purple-bg: rgba(147, 51, 234, 0.08);
--color-card-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.05);
--color-topbar-blur: rgba(248, 250, 252, 0.85);
```

---

## PENDING ITEMS — PFE Checklist

RELEASE 1 — ETL & DWH
✅ Done   ETL pipeline 9 steps
✅ Done   analytics_db constellation schema
✅ Done   Demo dataset flow (`--limit`, `--dry-run`, 50K target)
⚠️ Check  compute_cohorts still contains noisy encoding/comments and NOW() usage
❌ Missing verify_billing_integrity.py (file not found at expected path)

RELEASE 2 — BI Platform
✅ Done   FastAPI multi-router platform (19 routers)
✅ Done   JWT auth Admin/Analyst + refresh token rotation
✅ Done   React dashboard/admin pages and routing
⚠️ Check  some queries still non-sargable (`DATE(col)` patterns)
❌ Missing comprehensive endpoint-level latency benchmark report

RELEASE 3 — AI Modules
✅ Done   Churn prediction module
✅ Done   K-Means segmentation trainer
✅ Done   Anomaly detection module
✅ Done   Report generator endpoints + PDF generation services
⚠️ Check  MCP architecture not explicitly implemented as dedicated MCP server
❌ Missing explicit model registry/versioning workflow across environments

ACADEMIC — PFE Report
⚠️ Check  pytest present but not comprehensive coverage
⚠️ Check  secrets present in `.env` committed in local workspace
❌ Missing full API documentation narrative beyond OpenAPI defaults

---

## REPORT GENERATOR — MCP Architecture

```yaml
status: partial
ai_provider: Google Gemini (via gemini_service.py)
template: report_template.html (missing), enterprise_report_template_service.py exists
pdf_engine: reportlab + weasyprint/xhtml2pdf dependencies present

mcp_tools_available:
  - not_started_as_explicit_mcp_server
  - current architecture uses internal service layer APIs

endpoints:
  POST /reports/generate
  GET  /reports/status/{id}
  GET  /reports/history
  GET  /reports/download/{id}

generation_steps: 5
polling_interval_ms: 2000
```

---

## KNOWN ISSUES & BUGS

CRITICAL
- Secrets exposed in `.env` (DB, SMTP, Gemini key)
File: user-analytics-backend/.env
Fix: rotate all keys and move to secure secret store.

WARNING
- `verify_billing_integrity.py` missing at expected location.
File: user-analytics-backend/scripts/verify_billing_integrity.py
Fix: add/restore script or update documentation path.

WARNING
- Non-sargable SQL patterns remain (`DATE(col)` filters, some `NOW()` usage in analytics logic).
Files: campaign_impact.py, anomalies.py, trialAnalytics.py, userActivity.py, churn_predictor.py (training anchor)
Fix: use timestamp bounds + temporal anchor helper.

WARNING
- Fallback `SECRET_KEY="change-me"` exists in code.
File: app/core/security.py
Fix: enforce non-default key in startup validation.

INFO
- Refresh-token cleanup startup error handled if migration not yet applied.
File: app/main.py

---

## USEFUL COMMANDS

```bash
# Start all services
docker compose up

# ETL — Demo mode (for defense)
cd user-analytics-backend
python scripts/etl/etl_prod_to_analytics.py --batch-size 50000 --limit 50000 --dry-run

# ETL — Production
python scripts/etl/etl_prod_to_analytics.py --batch-size 50000 --truncate-target

# Train ML model
curl -X POST http://localhost:8000/ml/churn/train

# Run anomaly detection
curl -X POST http://localhost:8000/anomalies/run-detection

# Alembic migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Frontend dev server
cd analytics-platform-front
npm run dev

# Backend dev server
cd user-analytics-backend
uvicorn app.main:app --reload --port 8000
```

---

## PFE REPORT CHAPTER MAPPING
Chapter 1 — Étude Préalable        → Context + Methodology
Key content:

DigMaco company presentation
USSD/SMS business model
Existing solutions critique
4 modules solution
Scrum + CRISP-DM hybrid methodology
Gantt + Release planning

Chapter 2 — Initialisation          → Requirements + Architecture
Key content:

Admin/Analyst actors
Functional/non-functional needs
Use case diagrams (global + refined)
Logical architecture (4 layers)
Physical architecture (Docker)
Deployment diagram

Chapter 3 — Release 1 ETL & DWH    → CRISP-DM phases 1-2
Key content:

prod_db exploration
9-step ETL pipeline
Constellation schema
Data quality findings
Temporal anchor solution

Chapter 4 — Release 2 BI Platform  → CRISP-DM deployment partial
Key content:

FastAPI routers
JWT auth
Performance optimizations
Dashboard modules
KPI formulas with SQL

Chapter 5 — Release 3 AI Modules   → CRISP-DM modeling+eval+deploy
Key content:

K-Means segmentation
Churn LR
Z-Score anomaly detection
Report generator + Gemini
Defense demo on 50K dataset


---

## AI ASSISTANT INSTRUCTIONS

When working on this codebase:

1. ALWAYS use lowercase for status values
   ('active', 'cancelled', 'success', 'failed')

2. NEVER use NOW() in analytics queries
   → use temporal anchor utilities when available

3. ALWAYS use sargable patterns
   → CAST(:date AS timestamp) not DATE(col)

4. ETL is idempotent via UUID5 + ON CONFLICT
   → safe to re-run at any time

5. Demo dataset target = 50K users
   → use for defense presentation

6. ML features are computed at ref_time controls
   → prevent leakage with explicit windows

7. Most API endpoints require JWT except public auth endpoints

8. Admin-only routes use require_admin on sensitive endpoints

9. asyncio parallel patterns are used in analytics aggregations

10. CSS variables should drive theming

---

*Generated automatically from codebase analysis.*
*Update this file after each sprint completion.*
