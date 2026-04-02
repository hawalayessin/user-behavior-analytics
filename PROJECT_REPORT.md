# PROJECT_REPORT

## Executive Summary
Le projet est globalement structuré et couvre une chaîne complète analytics (ETL -> API FastAPI -> UI React), avec plusieurs KPI déjà présents côté hooks/services/pages. L’architecture est avancée sur les modules churn/retention/campaign/trial, mais la couverture de tests reste partielle et certaines zones montrent des traces TODO/FIXME/prints et des implémentations heuristiques à stabiliser (notamment la documentation exacte de toutes les requêtes SQL/ORM et la standardisation auth/roles sur tous les endpoints).

## 1. Project Structure

### Full Directory Tree
```text
.
├── .agents
│   └── skills
│       └── supabase-postgres-best-practices
│           ├── references
│           │   ├── _contributing.md
│           │   ├── _sections.md
│           │   ├── _template.md
│           │   ├── advanced-full-text-search.md
│           │   ├── advanced-jsonb-indexing.md
│           │   ├── conn-idle-timeout.md
│           │   ├── conn-limits.md
│           │   ├── conn-pooling.md
│           │   ├── conn-prepared-statements.md
│           │   ├── data-batch-inserts.md
│           │   ├── data-n-plus-one.md
│           │   ├── data-pagination.md
│           │   ├── data-upsert.md
│           │   ├── lock-advisory.md
│           │   ├── lock-deadlock-prevention.md
│           │   ├── lock-short-transactions.md
│           │   ├── lock-skip-locked.md
│           │   ├── monitor-explain-analyze.md
│           │   ├── monitor-pg-stat-statements.md
│           │   ├── monitor-vacuum-analyze.md
│           │   ├── query-composite-indexes.md
│           │   ├── query-covering-indexes.md
│           │   ├── query-index-types.md
│           │   ├── query-missing-indexes.md
│           │   ├── query-partial-indexes.md
│           │   ├── schema-constraints.md
│           │   ├── schema-data-types.md
│           │   ├── schema-foreign-key-indexes.md
│           │   ├── schema-lowercase-identifiers.md
│           │   ├── schema-partitioning.md
│           │   ├── schema-primary-keys.md
│           │   ├── security-privileges.md
│           │   ├── security-rls-basics.md
│           │   └── security-rls-performance.md
│           ├── AGENTS.md
│           ├── CLAUDE.md
│           ├── README.md
│           └── SKILL.md
├── .vscode
│   └── settings.json
├── analytics-platform-front
│   ├── .vite
│   ├── public
│   │   └── digmaco.png
│   ├── src
│   │   ├── assets
│   │   │   ├── digmaco.png
│   │   │   └── react.svg
│   │   ├── components
│   │   │   ├── admin
│   │   │   │   └── management
│   │   │   │       ├── CampaignModal.jsx
│   │   │   │       ├── CampaignTable.jsx
│   │   │   │       ├── DeleteConfirmModal.jsx
│   │   │   │       ├── ServiceModal.jsx
│   │   │   │       └── ServiceTable.jsx
│   │   │   ├── dashboard
│   │   │   │   ├── campaign
│   │   │   │   │   ├── CampaignFunnelChart.jsx
│   │   │   │   │   ├── CampaignPerformanceChart.jsx
│   │   │   │   │   ├── CampaignVsOrganicChart.jsx
│   │   │   │   │   └── ServiceCampaignComparison.jsx
│   │   │   │   ├── churn
│   │   │   │   │   ├── ChartContainer.jsx
│   │   │   │   │   ├── ChurnCurveChart.jsx
│   │   │   │   │   ├── ChurnReasonsChart.jsx
│   │   │   │   │   ├── RiskSegmentsPanel.jsx
│   │   │   │   │   └── TimeToChurnChart.jsx
│   │   │   │   ├── churn_prediction
│   │   │   │   │   └── churn_dashboard.jsx
│   │   │   │   ├── retention
│   │   │   │   │   ├── CohortHeatmap.jsx
│   │   │   │   │   ├── RetentionCurve.jsx
│   │   │   │   │   └── ServiceRetentionRadar.jsx
│   │   │   │   ├── tabs
│   │   │   │   │   ├── EngagementTab.jsx
│   │   │   │   │   ├── OverviewTab.jsx
│   │   │   │   │   ├── RevenueTab.jsx
│   │   │   │   │   └── TrialChurnTab.jsx
│   │   │   │   ├── userActivity
│   │   │   │   │   ├── ActivityHeatmap.jsx
│   │   │   │   │   ├── DAUTrendChart.jsx
│   │   │   │   │   ├── InactivityAnalysis.jsx
│   │   │   │   │   ├── ServiceActivityTable.jsx
│   │   │   │   │   └── UserGrowthChart.jsx
│   │   │   │   ├── BIInsightsPanel.jsx
│   │   │   │   ├── ChurnPieChart.jsx
│   │   │   │   ├── EngagementHealthPanel.jsx
│   │   │   │   ├── FilterBar.jsx
│   │   │   │   ├── KPICard.jsx
│   │   │   │   ├── KPICardsRow1.jsx
│   │   │   │   ├── KPICardsRow2.jsx
│   │   │   │   ├── SubscriptionDonutChart.jsx
│   │   │   │   ├── TabNavigation.jsx
│   │   │   │   ├── TopServicesTable.jsx
│   │   │   │   └── TrialDropoffChart.jsx
│   │   │   ├── directory
│   │   │   │   └── Directory.jsx
│   │   │   ├── layout
│   │   │   │   ├── AppLayout.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── navConfig.js
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── SidebarNavItem.jsx
│   │   │   │   ├── SidebarSection.jsx
│   │   │   │   └── Topbar.jsx
│   │   │   ├── platform-users
│   │   │   │   ├── ConfirmDeleteModal.jsx
│   │   │   │   ├── CreateUserModal.jsx
│   │   │   │   ├── EditUserModal.jsx
│   │   │   │   ├── UserFilters.jsx
│   │   │   │   ├── UserKPICards.jsx
│   │   │   │   └── UserTable.jsx
│   │   │   └── subscribers
│   │   │       └── UserRowDetail.jsx
│   │   ├── constants
│   │   │   └── dateFilters.js
│   │   ├── context
│   │   │   └── AuthContext.jsx
│   │   ├── hooks
│   │   │   ├── useCampaignComparison.js
│   │   │   ├── useCampaignImpactDashboard.js
│   │   │   ├── useCampaignKPIs.js
│   │   │   ├── useCampaignPerformance.js
│   │   │   ├── useCampaignTimeline.js
│   │   │   ├── useChurnBreakdown.js
│   │   │   ├── useChurnCurve.js
│   │   │   ├── useChurnDashboard.js
│   │   │   ├── useChurnKPIs.js
│   │   │   ├── useChurnPredictionMetrics.js
│   │   │   ├── useChurnPredictionScores.js
│   │   │   ├── useChurnPredictionTrain.js
│   │   │   ├── useChurnReasons.js
│   │   │   ├── useCohortsTable.js
│   │   │   ├── useCrossService.js
│   │   │   ├── useDashboardMetrics.js
│   │   │   ├── useImportData.js
│   │   │   ├── useManagement.js
│   │   │   ├── useRetentionCurve.js
│   │   │   ├── useRetentionHeatmap.js
│   │   │   ├── useRetentionKPIs.js
│   │   │   ├── useRiskSegments.js
│   │   │   ├── useTimeToChurn.js
│   │   │   ├── useToast.jsx
│   │   │   ├── useTrialDropoffByDay.js
│   │   │   ├── useTrialKPIs.js
│   │   │   ├── useTrialUsers.js
│   │   │   ├── useUserActivity.js
│   │   │   └── useUsers.js
│   │   ├── pages
│   │   │   ├── admin
│   │   │   │   ├── ImportDataPage.jsx
│   │   │   │   └── ManagementPage.jsx
│   │   │   ├── auth
│   │   │   │   └── LoginPage.jsx
│   │   │   ├── dashboard
│   │   │   │   ├── AIChurnInsights.jsx
│   │   │   │   ├── CampaignImpactPage.jsx
│   │   │   │   ├── ChurnAnalysisPage.jsx
│   │   │   │   ├── CrossServiceBehaviorPage.jsx
│   │   │   │   ├── DashboardPage.jsx
│   │   │   │   ├── FreeTrialBehaviorPage.jsx
│   │   │   │   └── RetentionPage.jsx
│   │   │   ├── platform-users
│   │   │   │   └── PlatformUsersPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── RootRedirect.jsx
│   │   │   ├── SubscribersPage.jsx
│   │   │   └── UserActivityPage.jsx
│   │   ├── router
│   │   │   ├── AdminRoute.jsx
│   │   │   └── PrivateRoute.jsx
│   │   ├── services
│   │   │   └── api.js
│   │   ├── utils
│   │   │   └── apiError.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .dockerignore
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   └── vite.config.js
├── docs
│   ├── tmp
│   │   ├── pdfs
│   │   │   ├── cahier_charges_extract.txt
│   │   │   ├── rapport_avancement_extract.txt
│   │   │   ├── Rapport_Avancement_PFE_2026-03-23_p1.png
│   │   │   └── Rapport_Avancement_PFE_2026-03-24.pdf
│   │   └── generate_rapport.py
│   ├── architecture.md
│   ├── Digital Campaign Objectives & Service Overview.pdf
│   ├── etl_prod_readme.md
│   ├── kpis.md
│   ├── ml_churn_report.md
│   ├── Project 1 _ User Behavior Analytics & Insights Platform.pdf
│   ├── Rapport_Avancement_PFE.pdf
│   ├── REAL_DATA_INTEGRATION.md
│   └── TRIAL_INTEGRATION_SUMMARY.md
├── tmp
│   └── generate_project_report.py
├── user-analytics-backend
│   ├── alembic
│   │   ├── versions
│   │   │   ├── 3939f80c5a66_seeders.py
│   │   │   ├── 6c076db13bed_add_analytics_performance_indexes.py
│   │   │   ├── 8ce268d4732a_initial_migration.py
│   │   │   ├── ded5564102c8_initial_migration3.py
│   │   │   └── dff7e0993f3d_initial_migration1.py
│   │   ├── env.py
│   │   ├── README
│   │   └── script.py.mako
│   ├── app
│   │   ├── api
│   │   │   ├── v1
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── date_ranges.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── analytics.py
│   │   │   ├── billing_events.py
│   │   │   ├── campaigns.py
│   │   │   ├── cohorts.py
│   │   │   ├── import_logs.py
│   │   │   ├── platform_users.py
│   │   │   ├── service_types.py
│   │   │   ├── services.py
│   │   │   ├── sms_events.py
│   │   │   ├── subscriptions.py
│   │   │   ├── unsubscriptions.py
│   │   │   ├── user_activities.py
│   │   │   └── users.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── campaign_repo.py
│   │   │   └── churn_repo.py
│   │   ├── routers
│   │   │   ├── admin_import.py
│   │   │   ├── analyticsOverview.py
│   │   │   ├── auth.py
│   │   │   ├── campaign_impact.py
│   │   │   ├── churn_analysis.py
│   │   │   ├── cross_service.py
│   │   │   ├── management.py
│   │   │   ├── ml_churn.py
│   │   │   ├── platform_user.py
│   │   │   ├── retention.py
│   │   │   ├── service.py
│   │   │   ├── trialAnalytics.py
│   │   │   ├── userActivity.py
│   │   │   └── users.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── BillingEvent.py
│   │   │   ├── Campaigns.py
│   │   │   ├── churn_analysis.py
│   │   │   ├── Cohorts.py
│   │   │   ├── ml_churn.py
│   │   │   ├── platform_user_schemas.py
│   │   │   ├── Services.py
│   │   │   ├── ServicesTypes.py
│   │   │   ├── SmsEvents.py
│   │   │   ├── Subscriptions.py
│   │   │   ├── Unsubscriptions.py
│   │   │   ├── UserActivities.py
│   │   │   └── users.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── campaign_service.py
│   │   │   ├── churn_service.py
│   │   │   └── platform_user_service.py
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   └── temporal.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── logs
│   │   └── .gitkeep
│   ├── migrations
│   │   └── create_import_logs.sql
│   ├── ml_models
│   │   ├── __init__.py
│   │   ├── churn_metrics.joblib
│   │   ├── churn_model.joblib
│   │   └── churn_predictor.py
│   ├── scripts
│   │   ├── etl
│   │   │   ├── __init__.py
│   │   │   ├── etl_prod_to_analytics.py
│   │   │   ├── fix_services_mapping.py
│   │   │   ├── link_campaigns_to_subscriptions.py
│   │   │   ├── recalcul_cohorts.py
│   │   │   └── seed_campaigns.py
│   │   ├── seeder
│   │   │   ├── __init__.py
│   │   │   └── seed_missing_data.py
│   │   ├── sql
│   │   │   └── diagnostics.sql
│   │   ├── compute_cohorts.py
│   │   └── verify_data.py
│   ├── tests
│   │   └── __init__.py
│   ├── .dockerignore
│   ├── .env
│   ├── .env.example
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── Makefile
│   ├── note.txt
│   ├── pyproject.toml
│   ├── README.md
│   └── requirements.txt
├── .env
├── .gitignore
├── .gitignore.bak.20260328_115606
├── .report_all_files.txt
├── docker-compose.yml
├── mcp.json
├── reorganize_project.py
├── reorganize_report.json
├── reorganize_report_apply.json
└── skills-lock.json
```

### Folder Roles
- **.agents/skills/supabase-postgres-best-practices**: Project folder containing implementation artifacts
- **.agents/skills/supabase-postgres-best-practices/references**: Project folder containing implementation artifacts
- **.vscode**: Project folder containing implementation artifacts
- **analytics-platform-front**: React frontend application
- **analytics-platform-front/public**: Static frontend assets
- **analytics-platform-front/src**: Frontend source code
- **analytics-platform-front/src/assets**: Frontend local assets
- **analytics-platform-front/src/components/admin/management**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard/campaign**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard/churn**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard/churn_prediction**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard/retention**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard/tabs**: Reusable frontend components
- **analytics-platform-front/src/components/dashboard/userActivity**: Reusable frontend components
- **analytics-platform-front/src/components/directory**: Reusable frontend components
- **analytics-platform-front/src/components/layout**: Reusable frontend components
- **analytics-platform-front/src/components/platform-users**: Reusable frontend components
- **analytics-platform-front/src/components/subscribers**: Reusable frontend components
- **analytics-platform-front/src/constants**: Frontend source code
- **analytics-platform-front/src/context**: React context providers
- **analytics-platform-front/src/hooks**: Frontend data hooks for API/KPI
- **analytics-platform-front/src/pages**: Frontend route-level pages
- **analytics-platform-front/src/pages/admin**: Frontend route-level pages
- **analytics-platform-front/src/pages/auth**: Frontend route-level pages
- **analytics-platform-front/src/pages/dashboard**: Frontend route-level pages
- **analytics-platform-front/src/pages/platform-users**: Frontend route-level pages
- **analytics-platform-front/src/router**: Frontend source code
- **analytics-platform-front/src/services**: Frontend API clients and backend services
- **analytics-platform-front/src/utils**: Reusable helper utilities
- **docs**: Project documentation
- **docs/tmp**: Project documentation
- **docs/tmp/pdfs**: Project documentation
- **tmp**: Project folder containing implementation artifacts
- **user-analytics-backend**: Project folder containing implementation artifacts
- **user-analytics-backend/alembic**: Database migration tooling
- **user-analytics-backend/alembic/versions**: Database migration revision scripts
- **user-analytics-backend/app**: Backend FastAPI application core
- **user-analytics-backend/app/api**: API layer and route declarations
- **user-analytics-backend/app/api/v1**: API layer and route declarations
- **user-analytics-backend/app/core**: Core configuration, security, and shared backend setup
- **user-analytics-backend/app/models**: SQLAlchemy ORM models
- **user-analytics-backend/app/repositories**: Database data access layer
- **user-analytics-backend/app/routers**: FastAPI endpoint grouping
- **user-analytics-backend/app/schemas**: Pydantic request/response schemas
- **user-analytics-backend/app/services**: Frontend API clients and backend services
- **user-analytics-backend/app/utils**: Reusable helper utilities
- **user-analytics-backend/logs**: Project folder containing implementation artifacts
- **user-analytics-backend/migrations**: Standalone SQL migration scripts
- **user-analytics-backend/ml_models**: Serialized models and ML utilities
- **user-analytics-backend/scripts**: Operational and ETL scripts
- **user-analytics-backend/scripts/etl**: ETL jobs from source DB to analytics DB
- **user-analytics-backend/scripts/seeder**: Data seed scripts
- **user-analytics-backend/scripts/sql**: Raw SQL scripts
- **user-analytics-backend/tests**: Automated test suite

## Files Group: Configuration files

### .env
- Purpose: Non-Python/non-frontend artifact (no extension)

### docker-compose.yml
- Purpose: Non-Python/non-frontend artifact (.yml)

### mcp.json
- Purpose: Non-Python/non-frontend artifact (.json)

### user-analytics-backend/.env
- Purpose: Non-Python/non-frontend artifact (no extension)

### user-analytics-backend/alembic.ini
- Purpose: Non-Python/non-frontend artifact (.ini)

### user-analytics-backend/app/core/config.py
- Purpose: Python module implementing config
- Important constants/configuration: None detected
```python
class Settings(BaseSettings):  # Runtime settings for API + Alembic.
    def _normalize_database_url(self: Any) -> 'Settings': ...  # No docstring
```

### user-analytics-backend/pyproject.toml
- Purpose: Non-Python/non-frontend artifact (.toml)

## Files Group: Database models (models/, schemas/)

### user-analytics-backend/app/models/__init__.py
- Purpose: SQLAlchemy ORM models for user-analytics-backend.
- Important constants/configuration: None detected
- Functions/classes: None detected

### user-analytics-backend/app/models/analytics.py
- Purpose: Convenience imports for analytics-domain models.
- Important constants/configuration: None detected
- Functions/classes: None detected

### user-analytics-backend/app/models/billing_events.py
- Purpose: Python module implementing billing events
- Important constants/configuration: None detected
```python
class BillingEvent(Base):  # Billing events for subscriptions.
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/campaigns.py
- Purpose: Python module implementing campaigns
- Important constants/configuration: None detected
```python
class Campaign(Base):  # No docstring
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/cohorts.py
- Purpose: Python module implementing cohorts
- Important constants/configuration: None detected
```python
class Cohort(Base):  # Pre-calculated retention metrics for performance.
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/import_logs.py
- Purpose: Python module implementing import logs
- Important constants/configuration: None detected
```python
class ImportLog(Base):  # No docstring
```

### user-analytics-backend/app/models/platform_users.py
- Purpose: Python module implementing platform users
- Important constants/configuration: None detected
```python
class PlatformUser(Base):  # No docstring
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/service_types.py
- Purpose: Python module implementing service types
- Important constants/configuration: None detected
```python
class ServiceType(Base):  # No docstring
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/services.py
- Purpose: Python module implementing services
- Important constants/configuration: None detected
```python
class Service(Base):  # No docstring
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/sms_events.py
- Purpose: Python module implementing sms events
- Important constants/configuration: None detected
```python
class SmsEvent(Base):  # SMS interaction logs.
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/subscriptions.py
- Purpose: Python module implementing subscriptions
- Important constants/configuration: None detected
```python
class Subscription(Base):  # No docstring
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/unsubscriptions.py
- Purpose: Python module implementing unsubscriptions
- Important constants/configuration: None detected
```python
class Unsubscription(Base):  # Unsubscription / churn events.
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/user_activities.py
- Purpose: Python module implementing user activities
- Important constants/configuration: None detected
```python
class UserActivity(Base):  # Activity logging for DAU/WAU/MAU.
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/models/users.py
- Purpose: Python module implementing users
- Important constants/configuration: None detected
```python
class User(Base):  # Core user table.
    def __repr__(self: Any) -> str: ...  # No docstring
```

### user-analytics-backend/app/schemas/__init__.py
- Purpose: Python module implementing   init  
- Important constants/configuration: None detected
- Functions/classes: None detected

### user-analytics-backend/app/schemas/auth.py
- Purpose: Python module implementing auth
- Important constants/configuration: None detected
```python
class RegisterRequest(BaseModel):  # No docstring
    def validate_role(cls: Any, v: str) -> str: ...  # No docstring
class LoginRequest(BaseModel):  # No docstring
class TokenResponse(BaseModel):  # No docstring
class UserResponse(BaseModel):  # No docstring
```

### user-analytics-backend/app/schemas/BillingEvent.py
- Purpose: Python module implementing BillingEvent
- Important constants/configuration: None detected
```python
class BillingEventBase(BaseModel):  # No docstring
class BillingEventCreate(BillingEventBase):  # No docstring
class BillingEventUpdate(BaseModel):  # No docstring
class BillingEventRead(BillingEventBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/Campaigns.py
- Purpose: Python module implementing Campaigns
- Important constants/configuration: None detected
```python
class CampaignBase(BaseModel):  # No docstring
class CampaignCreate(CampaignBase):  # No docstring
class CampaignUpdate(BaseModel):  # No docstring
class CampaignRead(CampaignBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/churn_analysis.py
- Purpose: Python module implementing churn analysis
- Important constants/configuration: None detected
```python
class ChurnKPIsResponse(BaseModel):  # No docstring
class ChurnCurvePoint(BaseModel):  # No docstring
class TimeToChurnBucketRow(BaseModel):  # No docstring
class ChurnReasonRow(BaseModel):  # No docstring
class RiskSegmentRow(BaseModel):  # No docstring
```

### user-analytics-backend/app/schemas/Cohorts.py
- Purpose: Python module implementing Cohorts
- Important constants/configuration: None detected
```python
class CohortBase(BaseModel):  # No docstring
class CohortCreate(CohortBase):  # No docstring
class CohortUpdate(BaseModel):  # No docstring
class CohortRead(CohortBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/ml_churn.py
- Purpose: Python module implementing ml churn
- Important constants/configuration: None detected
```python
class ChurnTrainMetricsResponse(BaseModel):  # No docstring
class ChurnRiskDistributionItem(BaseModel):  # No docstring
class ChurnTopUserItem(BaseModel):  # No docstring
class ChurnScoresResponse(BaseModel):  # No docstring
```

### user-analytics-backend/app/schemas/platform_user_schemas.py
- Purpose: Python module implementing platform user schemas
- Important constants/configuration: None detected
```python
class LoginRequest(BaseModel):  # No docstring
class Token(BaseModel):  # No docstring
class TokenPayload(BaseModel):  # No docstring
class PlatformUserBase(BaseModel):  # No docstring
class PlatformUserCreate(PlatformUserBase):  # No docstring
class PlatformUserUpdate(BaseModel):  # No docstring
class PlatformUserRead(PlatformUserBase):  # No docstring
class PlatformUserListResponse(BaseModel):  # No docstring
class UpdateStatusRequest(BaseModel):  # No docstring
class UpdateRoleRequest(BaseModel):  # No docstring
```

### user-analytics-backend/app/schemas/Services.py
- Purpose: Python module implementing Services
- Important constants/configuration: None detected
```python
class ServiceBase(BaseModel):  # No docstring
class ServiceCreate(ServiceBase):  # No docstring
class ServiceUpdate(BaseModel):  # No docstring
class ServiceRead(ServiceBase):  # No docstring
class ServiceReadWithType(ServiceRead):  # Service avec les détails du service_type imbriqué.
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/ServicesTypes.py
- Purpose: Python module implementing ServicesTypes
- Important constants/configuration: None detected
```python
class ServiceTypeBase(BaseModel):  # No docstring
class ServiceTypeCreate(ServiceTypeBase):  # No docstring
class ServiceTypeUpdate(BaseModel):  # No docstring
class ServiceTypeRead(ServiceTypeBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/SmsEvents.py
- Purpose: Python module implementing SmsEvents
- Important constants/configuration: None detected
```python
class SmsEventBase(BaseModel):  # No docstring
class SmsEventCreate(SmsEventBase):  # No docstring
class SmsEventUpdate(BaseModel):  # No docstring
class SmsEventRead(SmsEventBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/Subscriptions.py
- Purpose: Python module implementing Subscriptions
- Important constants/configuration: None detected
```python
class SubscriptionBase(BaseModel):  # No docstring
class SubscriptionCreate(SubscriptionBase):  # No docstring
class SubscriptionUpdate(BaseModel):  # No docstring
class SubscriptionRead(SubscriptionBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/Unsubscriptions.py
- Purpose: Python module implementing Unsubscriptions
- Important constants/configuration: None detected
```python
class UnsubscriptionBase(BaseModel):  # No docstring
class UnsubscriptionCreate(UnsubscriptionBase):  # No docstring
class UnsubscriptionUpdate(BaseModel):  # No docstring
class UnsubscriptionRead(UnsubscriptionBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/UserActivities.py
- Purpose: Python module implementing UserActivities
- Important constants/configuration: None detected
```python
class UserActivityBase(BaseModel):  # No docstring
class UserActivityCreate(UserActivityBase):  # No docstring
class UserActivityRead(UserActivityBase):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/app/schemas/users.py
- Purpose: Python module implementing users
- Important constants/configuration: None detected
```python
class SubscriptionItem(BaseModel):  # No docstring
class UnsubscriptionItem(BaseModel):  # No docstring
class UserListItem(BaseModel):  # No docstring
class UserListResponse(BaseModel):  # No docstring
class UserDetailResponse(BaseModel):  # No docstring
class UserStatsResponse(BaseModel):  # No docstring
```

## Files Group: ETL scripts (scripts/etl/)

### user-analytics-backend/scripts/etl/__init__.py
- Status: Empty file

### user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
- Purpose: ETL Hawala (prod) -> analytics_db (PFE)
- Important constants/configuration:
  - PROJECT_ROOT = Path(__file__).resolve().parents[2]
  - USER_NS = uuid.UUID('11111111-1111-1111-1111-111111111111')
  - SUB_NS = uuid.UUID('22222222-2222-2222-2222-222222222222')
  - BILLING_NS = uuid.UUID('33333333-3333-3333-3333-333333333333')
  - ACTIVITY_NS = uuid.UUID('66666666-6666-6666-6666-666666666666')
  - SERVICE_NS = uuid.UUID('44444444-4444-4444-4444-444444444444')
  - SERVICE_TYPE_NS = uuid.UUID('55555555-5555-5555-5555-555555555555')
  - USER_STATUS_MAP = {1: 'active', 0: 'inactive', -1: 'inactive', -2: 'inactive'}
  - SUB_STATUS_MAP = {1: 'active', 0: 'trial', -1: 'cancelled', -2: 'expired'}
  - BILLING_STATUS_MAP = {0: 'pending', 1: 'success', 2: 'failed', 3: 'cancelled'}
  - BILLING_EVENT_TYPE_MAP = {1: 'new_sub', 2: 'renewal', 3: 'upgrade', 4: 'unsub'}
  - ACTIVITY_TYPE_MAP = {1: 'subscription', 2: 'renewal', 4: 'churn_event'}
```python
def parse_args() -> argparse.Namespace: ...  # No docstring
def configure_logging() -> None: ...  # No docstring
def main() -> None: ...  # No docstring
class ETLMetrics(object):  # No docstring
class ETLRunner(object):  # No docstring
    def __init__(self: Any, source_url: str, target_url: str, batch_size: int, limit: int | None, dry_run: bool, truncate_target: bool) -> Any: ...  # No docstring
    def run(self: Any) -> None: ...  # No docstring
    def _preflight(self: Any) -> None: ...  # No docstring
    def _truncate_analytics_data(self: Any) -> None: ...  # No docstring
    def _log(msg: str, **kwargs: Any) -> None: ...  # No docstring
    def _uuid5(namespace: uuid.UUID, value: str | int | None) -> uuid.UUID: ...  # No docstring
    def _parse_dt(value: Any) -> datetime | None: ...  # No docstring
    def _clean_phone(value: Any) -> str | None: ...  # No docstring
    def _normalize_channel(value: Any) -> str: ...  # No docstring
    def _with_retry(self: Any, fn: Any, *args: Any, **kwargs: Any) -> Any: ...  # No docstring
    def _count_source(self: Any, table: str) -> int: ...  # No docstring
    def _count_target_rows(self: Any, tables: list[str]) -> int: ...  # No docstring
    def _source_tx_date_range(self: Any) -> tuple[str, str]: ...  # No docstring
    def _source_chunks(self: Any, table: str, cols: list[str], order_col: str) -> Any: ...  # No docstring
    def _load_subscription_type_to_service_map(self: Any) -> dict[int, int]: ...  # No docstring
    def _write_import_log(self: Any, target_table: str, metrics: ETLMetrics, status: str, duration_sec: float, error: str | None) -> None: ...  # No docstring
    def _execute_batch(self: Any, stmt: Any, rows: list[dict[str, Any]]) -> None: ...  # No docstring
    def etl_service_types(self: Any) -> None: ...  # No docstring
    def etl_services(self: Any) -> None: ...  # No docstring
    def etl_users(self: Any) -> None: ...  # No docstring
    def _fetch_user_ids_for_phones(self: Any, phones: list[str]) -> dict[str, uuid.UUID]: ...  # No docstring
    def _fetch_subscription_map(self: Any, subscription_ids: list[uuid.UUID]) -> dict[uuid.UUID, tuple[uuid.UUID, uuid.UUID]]: ...  # No docstring
    def etl_subscriptions(self: Any) -> None: ...  # No docstring
    def etl_billing_events(self: Any) -> None: ...  # No docstring
    def etl_unsubscriptions(self: Any) -> None: ...  # FIX #3 : Source = transaction_histories WHERE type = 4 (unsub) depuis hawala.
    def etl_user_activities(self: Any) -> None: ...  # No docstring
    def etl_sms_events(self: Any) -> None: ...  # No docstring
    def etl_cohorts(self: Any) -> None: ...  # No docstring
```

### user-analytics-backend/scripts/etl/fix_services_mapping.py
- Purpose: Fix subscriptions.service_id mapping after ETL.
- Important constants/configuration:
  - USER_NS = uuid.UUID('11111111-1111-1111-1111-111111111111')
  - SUB_NS = uuid.UUID('22222222-2222-2222-2222-222222222222')
  - SERVICE_NS = uuid.UUID('44444444-4444-4444-4444-444444444444')
  - SUB_STATUS_MAP = {1: 'active', 0: 'trial', -1: 'cancelled', -2: 'expired'}
```python
def log_json(message: str, **kwargs: Any) -> None: ...  # No docstring
def parse_args() -> argparse.Namespace: ...  # No docstring
def get_engine(env_var: str, default_url: str) -> Engine: ...  # No docstring
def parse_dt(value: Any) -> datetime | None: ...  # No docstring
def clean_phone(value: Any) -> str | None: ...  # No docstring
def uuid5(namespace: uuid.UUID, value: str | int | None) -> uuid.UUID: ...  # No docstring
def source_chunks(source_engine: Engine, cols: list[str], batch_size: int, limit: int | None) -> Any: ...  # No docstring
def fetch_user_map(target_engine: Engine, phones: list[str]) -> dict[str, uuid.UUID]: ...  # No docstring
def preflight(source_engine: Engine, target_engine: Engine) -> None: ...  # No docstring
def load_service_mappings(source_engine: Engine, target_engine: Engine) -> tuple[dict[int, uuid.UUID], dict[int, int]]: ...  # No docstring
def maybe_truncate_subscriptions(target_engine: Engine, dry_run: bool) -> None: ...  # No docstring
def run_fix(source_engine: Engine, target_engine: Engine, args: argparse.Namespace) -> Metrics: ...  # No docstring
def main() -> None: ...  # No docstring
class Metrics(object):  # No docstring
```

### user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
- Purpose: ETL Script: Link subscriptions to campaigns
- Important constants/configuration: None detected
```python
def link_campaigns_to_subscriptions() -> Any: ...  # Update subscriptions.campaign_id using date+service matching
```

### user-analytics-backend/scripts/etl/recalcul_cohorts.py
- Purpose: Recalcul des cohortes D7/D14/D30 sur les donnees reelles analytics_db.
- Important constants/configuration: None detected
- Functions/classes: None detected

### user-analytics-backend/scripts/etl/seed_campaigns.py
- Purpose: seed_campaigns.py — Version FINALE
- Important constants/configuration:
  - CAMPAIGN_NS = uuid.UUID('88888888-8888-8888-8888-888888888888')
  - TEMPLATES = [('ussd-ramadan-2025', 'Ramadan USSD Promo 2025', 'PROMOTIONAL', 'Campagne SMS push Ramadan — 50% sur abonnement mensuel', 120000, 50000.0), ('ussd-back-school-25', 'Rentrée Scolaire USSD 2025', 'ACQUISITION', 'Push USSD ciblé étudiants/parents rentrée septembre 2025', 80000, 35000.0), ('ussd-eid-offer-25', 'Offre Aïd USSD 2025', 'PROMOTIONAL', 'Offre spéciale Aïd El Adha — 3 jours accès gratuit', 95000, 40000.0), ('ussd-summer-25', 'Promo Été USSD 2025', 'PROMOTIONAL', 'Campagne été — tarif réduit juillet-août 2025', 70000, 30000.0), ('ussd-retention-q4', 'Rétention Q4 USSD 2025', 'RETENTION', 'Relance abonnés inactifs depuis 15 jours via SMS', 45000, 25000.0), ('ussd-reactivation-25', 'Réactivation Inactifs USSD', 'REACTIVATION', 'Ciblage désabonnés des 60 derniers jours — offre retour', 30000, 20000.0), ('web-launch-sept-25', 'Lancement Sept WEB 2025', 'ACQUISITION', 'Bannières web et push notif — nouvelle offre septembre 2025', 25000, 15000.0), ('web-promo-oct-25', 'Promo Octobre WEB 2025', 'PROMOTIONAL', 'Display octobre — réduction 30% premier mois', 22000, 12000.0), ('web-loyalty-25', 'Fidélité WEB 2025', 'RETENTION', 'Programme fidélité — email+push abonnés 6+ mois', 18000, 10000.0), ('web-upsell-25', 'Upsell Premium WEB 2025', 'UPSELL', 'Upgrade vers offre premium — abonnés plan standard', 15000, 8000.0), ('organic-direct', 'Organique / Direct', 'ORGANIC', 'Souscriptions directes sans campagne payante', 500000, 0.0)]
  - INSERT_SQL = text('\n    INSERT INTO campaigns\n        (id, name, description, service_id,\n         send_datetime, target_size, cost, campaign_type, status)\n    VALUES\n        (:id, :name, :description, :service_id,\n         :send_datetime, :target_size, :cost, :campaign_type, :status)\n    ON CONFLICT (id) DO UPDATE SET\n        name          = EXCLUDED.name,\n        description   = EXCLUDED.description,\n        service_id    = EXCLUDED.service_id,\n        send_datetime = EXCLUDED.send_datetime,\n        target_size   = EXCLUDED.target_size,\n        cost          = EXCLUDED.cost,\n        campaign_type = EXCLUDED.campaign_type,\n        status        = EXCLUDED.status\n')
  - ASSIGN_BATCH_SQL = text('\n    WITH locked_subscriptions AS (\n        SELECT\n            s.id,\n            s.service_id,\n            s.subscription_start_date\n        FROM subscriptions s\n        WHERE s.campaign_id IS NULL\n        LIMIT :batch_size\n        FOR UPDATE OF s SKIP LOCKED\n    ),\n    candidates AS (\n        SELECT\n            ls.id                     AS sub_id,\n            c.id                      AS campaign_id,\n            ls.subscription_start_date AS sub_start,\n            c.send_datetime           AS send_dt,\n            ROW_NUMBER() OVER (\n                PARTITION BY ls.id\n                ORDER BY ABS(EXTRACT(EPOCH FROM (ls.subscription_start_date - c.send_datetime))), c.send_datetime DESC\n            ) AS rn\n        FROM locked_subscriptions ls\n        JOIN campaigns c ON c.service_id = ls.service_id\n    )\n    UPDATE subscriptions s\n    SET    campaign_id = c.campaign_id\n    FROM   candidates c\n    WHERE  s.id = c.sub_id\n      AND  c.rn = 1\n\n')
  - ASSIGN_ORGANIC_FALLBACK_BATCH_SQL = text("\n    WITH organic_campaign AS (\n        SELECT id\n        FROM campaigns\n        WHERE campaign_type = 'ORGANIC'\n        ORDER BY send_datetime DESC\n        LIMIT 1\n    ),\n    locked_subscriptions AS (\n        SELECT s.id\n        FROM subscriptions s\n        WHERE s.campaign_id IS NULL\n        LIMIT :batch_size\n        FOR UPDATE OF s SKIP LOCKED\n    )\n    UPDATE subscriptions s\n    SET campaign_id = oc.id\n    FROM organic_campaign oc, locked_subscriptions ls\n    WHERE s.id = ls.id\n")
```python
def log(msg: str, **kw: Any) -> None: ...  # No docstring
def get_anchor(engine: Any) -> datetime: ...  # No docstring
def get_services(engine: Any) -> list[dict[str, Any]]: ...  # No docstring
def build(anchor: datetime, services: list[dict[str, Any]]) -> list[dict]: ...  # No docstring
def db_rows(campaigns: list[dict]) -> list[dict]: ...  # Retourne seulement les clés sans préfixe _ pour l'INSERT.
def do_insert(engine: Any, campaigns: Any, dry_run: bool, pre_clean: bool) -> int: ...  # No docstring
def do_assign(engine: Any, dry_run: bool) -> int: ...  # No docstring
def do_clear(engine: Any) -> None: ...  # No docstring
def summary(engine: Any) -> None: ...  # No docstring
def main() -> Any: ...  # No docstring
```

## Files Group: Repositories

### user-analytics-backend/app/repositories/__init__.py
- Status: Empty file

### user-analytics-backend/app/repositories/campaign_repo.py
- Purpose: Campaign Impact Repository Layer
- Important constants/configuration: None detected
```python
class CampaignRepository(object):  # Repository for campaign analytics queries
    def get_campaigns_overview(db: Session, start_date: Optional[Any], end_date: Optional[Any], service_id: Optional[str]) -> Dict[str, Any]: ...  # Get high-level campaign metrics summary
    def get_campaign_impact_list(db: Session, status_filter: Optional[str], campaign_type_filter: Optional[str], start_date: Optional[Any], end_date: Optional[Any], service_id: Optional[str], page: int, limit: int) -> Dict[str, Any]: ...  # Get paginated list of campaigns with impact metrics.
    def get_impact_by_type(db: Session, start_date: Optional[Any], end_date: Optional[Any], service_id: Optional[str]) -> List[Dict[str, Any]]: ...  # Get campaign impact aggregated by campaign_type.
    def get_top_campaigns(db: Session, limit: int, start_date: Optional[Any], end_date: Optional[Any], service_id: Optional[str]) -> List[Dict[str, Any]]: ...  # Get top N campaigns by conversion rate (or subscriptions acquired if rate is 0)
    def get_campaigns_monthly_trend(db: Session, start_date: Optional[Any], end_date: Optional[Any], service_id: Optional[str]) -> List[Dict[str, Any]]: ...  # Get campaign metrics aggregated by month (based on send_datetime)
```

### user-analytics-backend/app/repositories/churn_repo.py
- Purpose: Python file (parse error: invalid non-printable character U+FEFF (<unknown>, line 1))
- Important constants/configuration: None detected
- Functions/classes: None detected

## Files Group: Services

### analytics-platform-front/src/services/api.js
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### user-analytics-backend/app/services/__init__.py
- Status: Empty file

### user-analytics-backend/app/services/campaign_service.py
- Purpose: Campaign Impact Service Layer
- Important constants/configuration:
  - CACHE_TTL = 30
```python
def _get_cache_key(cache_type: str, **kwargs: Any) -> str: ...  # Generate cache key from parameters
def _is_cache_valid(key: str) -> bool: ...  # Check if cache entry is still valid
def _get_cached(key: str) -> Optional[Any]: ...  # Get value from cache if valid
def _set_cache(key: str, value: Any) -> Any: ...  # Store value in cache with timestamp
def get_campaign_dashboard(db: Session, filters: Dict[str, Any]) -> Dict[str, Any]: ...  # Get complete campaign impact dashboard in a single payload
def get_campaign_list(db: Session, status_filter: Optional[str], campaign_type_filter: Optional[str], start_date: Optional[date], end_date: Optional[date], service_id: Optional[str], page: int, limit: int) -> Dict[str, Any]: ...  # Get paginated campaign list with impact metrics and filtering
```

### user-analytics-backend/app/services/churn_service.py
- Purpose: Python file (parse error: invalid non-printable character U+FEFF (<unknown>, line 1))
- Important constants/configuration: None detected
- Functions/classes: None detected

### user-analytics-backend/app/services/platform_user_service.py
- Purpose: Python module implementing platform user service
- Important constants/configuration:
  - VALID_ROLES = {'admin', 'analyst', 'viewer'}
```python
def _get_or_404(db: Session, user_id: UUID) -> PlatformUser: ...  # Fetch a PlatformUser by ID or raise 404.
def _guard_self(user_id: UUID, current_user_id: UUID, action: str) -> None: ...  # Raise 403 if the admin tries to modify/delete themselves.
def get_all_users(db: Session, skip: int, limit: int, search: str | None, role: str | None, is_active: bool | None) -> dict: ...  # Return paginated list of platform users with optional filters.
def get_user_by_id(db: Session, user_id: UUID) -> PlatformUser: ...  # Return a single platform user or raise 404.
def create_user(db: Session, data: PlatformUserCreate) -> PlatformUser: ...  # Create a new platform user, raise 400 if email already registered.
def update_user(db: Session, user_id: UUID, data: PlatformUserUpdate) -> PlatformUser: ...  # Update name, email and/or role of a platform user.
def update_user_status(db: Session, user_id: UUID, is_active: bool, current_user_id: UUID) -> PlatformUser: ...  # Toggle active/inactive status — admin cannot deactivate themselves.
def update_user_role(db: Session, user_id: UUID, role: str, current_user_id: UUID) -> PlatformUser: ...  # Change user role — admin cannot change their own role.
def delete_user(db: Session, user_id: UUID, current_user_id: UUID) -> None: ...  # Permanently delete a platform user — admin cannot delete themselves.
```

## Files Group: API routes

### user-analytics-backend/app/api/__init__.py
- Status: Empty file

### user-analytics-backend/app/api/v1/__init__.py
- Status: Empty file

### user-analytics-backend/app/routers/admin_import.py
- Purpose: Python module implementing admin import
- Important constants/configuration:
  - CSV_MAX_FILE_BYTES = 20 * 1024 * 1024
  - SQL_MAX_FILE_BYTES = 50 * 1024 * 1024
  - EXCLUDED_TABLES = {'platform_users', 'cohorts', 'staging_imports', 'import_logs'}
  - _DANGEROUS_SQL = re.compile('\\b(drop|delete|truncate|alter|create|update)\\b', flags=re.IGNORECASE)
  - _TABLE_FROM_INSERT = re.compile('insert\\s+into\\s+([a-zA-Z_][a-zA-Z0-9_]*)', flags=re.IGNORECASE)
```python
def _read_upload_bytes(file: UploadFile, max_bytes: int) -> bytes: ...  # No docstring
def _is_valid_uuid(value: Any) -> bool: ...  # No docstring
def _coerce_datetime(value: Any) -> datetime | None: ...  # No docstring
def _coerce_bool(value: Any) -> bool | None: ...  # No docstring
def _coerce_numeric(value: Any) -> float | None: ...  # No docstring
def _ensure_staging_tables(db: Session) -> None: ...  # Create staging tables if absent.
def _log_import(db: Session, admin: PlatformUser, file_name: str | None, file_type: str, target_table: str | None, scope: str | None, mode: str | None, status_value: str, rows_inserted: int, rows_skipped: int, error_details: dict | None) -> uuid.UUID: ...  # Persist minimal audit info. The ImportLog model doesn't have all fields from the spec
def _fk_exists_map(db: Session, fk_table: str, fk_col: str, ids: list[str]) -> set[str]: ...  # No docstring
def _validate_and_stage_csv(db: Session, table: str, file_name: str | None, mode: ImportMode, raw: bytes) -> ValidationResult: ...  # No docstring
def _load_from_staging(db: Session, table: str, mode: ImportMode, import_id: uuid.UUID, force: bool) -> tuple[int, int]: ...  # No docstring
def _maybe_compute_cohorts(table: str) -> bool: ...  # No docstring
def stage_single_table_csv(table: str, mode: ImportMode, file: UploadFile, db: Session, current_user: PlatformUser) -> Any: ...  # No docstring
def confirm_single_table_csv(import_id: str, table: str, mode: ImportMode, force: bool, db: Session, current_user: PlatformUser) -> Any: ...  # No docstring
def _split_sql_statements(sql_text: str) -> list[str]: ...  # No docstring
def import_full_database_sql(mode: ImportMode, file: UploadFile, db: Session, current_user: PlatformUser) -> Any: ...  # No docstring
def import_history(db: Session, current_user: PlatformUser) -> Any: ...  # No docstring
def download_template(table: str, db: Session, current_user: PlatformUser) -> Any: ...  # No docstring
class ValidationResult(object):  # No docstring
```

### user-analytics-backend/app/routers/analyticsOverview.py
- Purpose: Python module implementing analyticsOverview
- Important constants/configuration: None detected
```python
def get_summary(db: Session, service_id: Optional[str]) -> Any: ...  # No docstring
def get_overview(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/auth.py
- Purpose: Python module implementing auth
- Important constants/configuration: None detected
```python
def register(payload: RegisterRequest, db: Session) -> Any: ...  # No docstring
def login(payload: LoginRequest, db: Session) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/campaign_impact.py
- Purpose: Python module implementing campaign impact
- Important constants/configuration: None detected
```python
def get_campaign_impact_dashboard(db: Session, user: Any, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # Get complete campaign impact dashboard
def get_campaigns_list(status: Optional[str], campaign_type: Optional[str], start_date: Optional[date], end_date: Optional[date], service_id: Optional[str], page: int, limit: int, db: Session, user: Any) -> Any: ...  # Get paginated campaign list with impact metrics
def get_campaigns_overview(db: Session, user: Any) -> Any: ...  # Get high-level campaign metrics summary
def get_campaigns_by_type(db: Session, user: Any) -> Any: ...  # Get campaign impact aggregated by campaign type
def get_top_campaigns(limit: int, db: Session, user: Any) -> Any: ...  # Get top campaigns by conversion rate
def get_campaigns_trend(db: Session, user: Any) -> Any: ...  # Get monthly campaign trend
def _resolve_date_range(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> tuple[date, date]: ...  # No docstring
def get_campaign_kpis(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_campaign_performance(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_campaign_comparison(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_campaign_timeline(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/churn_analysis.py
- Purpose: Python file (parse error: invalid non-printable character U+FEFF (<unknown>, line 1))
- Important constants/configuration: None detected
- Functions/classes: None detected

### user-analytics-backend/app/routers/cross_service.py
- Purpose: Cross-Service Behavior Analytics
- Important constants/configuration: None detected
```python
def _date_filter(alias: str) -> str: ...  # Returns a SQL WHERE fragment for date range on subscription_start_date.
def _service_filter(alias: str) -> str: ...  # No docstring
def _build_where(has_date: bool, has_service: bool, alias: str) -> str: ...  # No docstring
def _resolve_params(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> dict: ...  # Resolve defaults and return a param dict.
def get_overview(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # Multi-service users, top combo, cross-retention vs mono-retention, ARPU.
def get_co_subscriptions(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # Co-subscription matrix: for each pair (A, B) what % of A users also have B.
def get_migrations(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # Top migration flows: user subscribed to service A, ended, then subscribed to service B.
def get_distribution(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # How many services does a typical user subscribe to?
```

### user-analytics-backend/app/routers/management.py
- Purpose: Python module implementing management
- Important constants/configuration: None detected
```python
def _slug(value: str) -> str: ...  # No docstring
def _billing_to_days(billing_type: BillingType) -> int: ...  # No docstring
def _service_type_name(service_name: str, billing_type: BillingType) -> str: ...  # No docstring
def _campaign_status(send_dt: datetime) -> str: ...  # No docstring
def list_services(db: Session, _: object) -> Any: ...  # No docstring
def create_service(body: ServiceCreateBody, db: Session, _: object) -> Any: ...  # No docstring
def update_service(service_id: str, body: ServiceUpdateBody, db: Session, _: object) -> Any: ...  # No docstring
def delete_service(service_id: str, db: Session, _: object) -> Any: ...  # No docstring
def list_campaigns(db: Session, _: object) -> Any: ...  # No docstring
def create_campaign(body: CampaignCreateBody, db: Session, _: object) -> Any: ...  # No docstring
def update_campaign(campaign_id: str, body: CampaignUpdateBody, db: Session, _: object) -> Any: ...  # No docstring
def delete_campaign(campaign_id: str, db: Session, _: object) -> Any: ...  # No docstring
class ServiceCreateBody(BaseModel):  # No docstring
class ServiceUpdateBody(BaseModel):  # No docstring
class CampaignCreateBody(BaseModel):  # No docstring
class CampaignUpdateBody(BaseModel):  # No docstring
```

### user-analytics-backend/app/routers/ml_churn.py
- Purpose: Python module implementing ml churn
- Important constants/configuration: None detected
```python
def train_churn_model(db: Session, _: Any) -> Any: ...  # No docstring
def get_churn_model_metrics() -> Any: ...  # No docstring
def get_churn_scores(db: Session, top: int, threshold: float, store: bool) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/platform_user.py
- Purpose: Python module implementing platform user
- Important constants/configuration: None detected
```python
def list_platform_users(skip: int, limit: int, search: str | None, role: str | None, is_active: bool | None, db: Session, _: PlatformUser) -> PlatformUserListResponse: ...  # List all platform users with optional filters and pagination.
def get_platform_user(user_id: UUID, db: Session, _: PlatformUser) -> PlatformUserResponse: ...  # Get a single platform user by ID.
def create_platform_user(data: PlatformUserCreate, db: Session, _: PlatformUser) -> PlatformUserResponse: ...  # Create a new platform user account.
def update_platform_user(user_id: UUID, data: PlatformUserUpdate, db: Session, _: PlatformUser) -> PlatformUserResponse: ...  # Update name, email and/or role of a platform user.
def update_user_status(user_id: UUID, body: UpdateStatusRequest, db: Session, current_user: PlatformUser) -> dict: ...  # Toggle active/inactive status of a platform user.
def update_user_role(user_id: UUID, body: UpdateRoleRequest, db: Session, current_user: PlatformUser) -> dict: ...  # Change role of a platform user (admin ↔ analyst).
def delete_platform_user(user_id: UUID, db: Session, current_user: PlatformUser) -> dict: ...  # Permanently delete a platform user.
```

### user-analytics-backend/app/routers/retention.py
- Purpose: Python module implementing retention
- Important constants/configuration: None detected
```python
def _parse_date_range(start_date: Optional[date], end_date: Optional[date], db: Session) -> tuple[date, date]: ...  # No docstring
def get_retention_kpis(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_retention_heatmap(db: Session, service_id: Optional[str], last_n_months: int) -> Any: ...  # No docstring
def get_retention_curve(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_retention_cohorts_list(db: Session, service_id: Optional[str], page: int, page_size: int) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/service.py
- Purpose: Python module implementing service
- Important constants/configuration: None detected
```python
def get_services(db: Session) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/trialAnalytics.py
- Purpose: Python module implementing trialAnalytics
- Important constants/configuration: None detected
```python
def get_trial_kpis(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_trial_timeline(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_trial_by_service(db: Session, start_date: Optional[date], end_date: Optional[date]) -> Any: ...  # No docstring
def get_trial_users(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str], search: Optional[str], status: Optional[str], page: int, page_size: int, export: bool) -> Any: ...  # No docstring
def get_trial_dropoff_by_day(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
def get_churn_breakdown(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/userActivity.py
- Purpose: Python module implementing userActivity
- Important constants/configuration: None detected
```python
def get_user_activity(db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]) -> Any: ...  # No docstring
```

### user-analytics-backend/app/routers/users.py
- Purpose: Python module implementing users
- Important constants/configuration: None detected
```python
def list_users(status: Optional[str], date_from: Optional[datetime], date_to: Optional[datetime], search: Optional[str], service_id: Optional[str], page: int, page_size: int, export: bool, db: Session) -> Any: ...  # No docstring
def list_trial_users(status: Optional[str], search: Optional[str], service_id: Optional[str], page: int, page_size: int, export: bool, db: Session) -> Any: ...  # Get trial users with their trial details
def get_user(user_id: UUID, db: Session) -> Any: ...  # No docstring
```

## Files Group: Auth

### analytics-platform-front/src/context/AuthContext.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: access_token / setAccessToken, role / setRole, full_name / setFullName, userId / setUserId, isLoading / setIsLoading
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/auth/LoginPage.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: /auth/login
- State variables: email / setEmail, password / setPassword, error / setError, loading / setLoading, rememberMe / setRememberMe, showPassword / setShowPassword
- Known issues/incomplete sections: None detected

## Files Group: Utilities

### analytics-platform-front/src/utils/apiError.js
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### user-analytics-backend/app/utils/__init__.py
- Status: Empty file

### user-analytics-backend/app/utils/temporal.py
- Purpose: Temporal helpers anchored on real data ranges instead of system date.
- Important constants/configuration: None detected
```python
def _utc_now_naive() -> datetime: ...  # No docstring
def _to_naive_utc(value: datetime | date | None) -> datetime | None: ...  # No docstring
def _is_allowed(table: str, field: str) -> bool: ...  # No docstring
def _query_extreme(db: Session, table: str, field: str, aggregate: Literal['MIN', 'MAX'], now_cap: datetime) -> datetime | None: ...  # No docstring
def _source_points(db: Session, source: AnchorSource, aggregate: Literal['MIN', 'MAX']) -> list[datetime]: ...  # No docstring
def get_data_bounds(db: Session, source: AnchorSource) -> tuple[datetime, datetime]: ...  # Return clamped [min, max] bounds for a metric source.
def get_data_anchor(db: Session, table: str, field: str, source: AnchorSource | None) -> datetime: ...  # Return a safe anchor date derived from real data and clamped to now.
def get_default_window(db: Session, days: int, source: AnchorSource) -> tuple[datetime, datetime]: ...  # No docstring
def get_month_window(db: Session, source: AnchorSource) -> tuple[datetime, datetime]: ...  # No docstring
def get_week_window(db: Session, source: AnchorSource) -> tuple[datetime, datetime]: ...  # No docstring
def get_day_window(db: Session, source: AnchorSource) -> tuple[datetime, datetime]: ...  # No docstring
```

## Files Group: Frontend pages

### analytics-platform-front/src/pages/admin/ImportDataPage.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: activeTab / setActiveTab, targetTable / setTargetTable, mode / setMode, file / setFile, preview / setPreview, columns / setColumns, result / setResult, confirmReplace / setConfirmReplace, validationModalOpen / setValidationModalOpen, staged / setStaged
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/admin/ManagementPage.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: tab / setTab, search / setSearch, serviceModalOpen / setServiceModalOpen, serviceModalMode / setServiceModalMode, serviceEditing / setServiceEditing, campaignModalOpen / setCampaignModalOpen, campaignModalMode / setCampaignModalMode, campaignEditing / setCampaignEditing, deleteOpen / setDeleteOpen, deleteLoading / setDeleteLoading, deleteContext / setDeleteContext
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/Dashboard.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters, page / setPage, statusFilter / setStatusFilter, typeFilter / setTypeFilter, selectedId / setSelectedId, toast / setToast
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/DashboardPage.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters, activeTab / setActiveTab, data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters, searchInput / setSearchInput, search / setSearch, statusFilter / setStatusFilter, sortField / setSortField, sortDir / setSortDir, page / setPage, exportOpen / setExportOpen, exportLoading / setExportLoading, toastMsg / setToastMsg
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/RetentionPage.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters, page / setPage, searchInput / setSearchInput, search / setSearch, sortField / setSortField, sortDir / setSortDir, exportOpen / setExportOpen, exportLoading / setExportLoading, toastMsg / setToastMsg
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: /platform-users/
- State variables: users / setUsers, total / setTotal, loading / setLoading, search / setSearch, roleFilter / setRoleFilter, statusFilter / setStatusFilter, page / setPage, selectedUser / setSelectedUser, showCreateModal / setShowCreateModal, showEditModal / setShowEditModal, showDeleteModal / setShowDeleteModal, statsData / setStatsData
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/RootRedirect.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/SubscribersPage.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: isServiceOpen / setIsServiceOpen, subscribers / setSubscribers, loading / setLoading, error / setError, filters / setFilters, services / setServices, expandedRow / setExpandedRow
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/UserActivityPage.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: filters / setFilters, searchInput / setSearchInput, search / setSearch, statutFilter / setStatutFilter, sortField / setSortField, sortDir / setSortDir, page / setPage, exportOpen / setExportOpen, exportLoading / setExportLoading, toastMsg / setToastMsg
- Known issues/incomplete sections: None detected

## Files Group: Frontend components

### analytics-platform-front/src/components/admin/management/CampaignModal.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: name / setName, serviceId / setServiceId, sendDate / setSendDate, targetSize / setTargetSize, errors / setErrors, saving / setSaving
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/CampaignTable.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/DeleteConfirmModal.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/ServiceModal.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: name / setName, billingType / setBillingType, price / setPrice, errors / setErrors, formError / setFormError, saving / setSaving
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/ServiceTable.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/BIInsightsPanel.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/CampaignFunnelChart.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: sortBy / setSortBy
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/CampaignVsOrganicChart.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/ServiceCampaignComparison.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/ChartContainer.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: isReady / setIsReady
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: showRetention / setShowRetention
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/ChurnReasonsChart.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/RiskSegmentsPanel.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/TimeToChurnChart.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: topN / setTopN, threshold / setThreshold
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/ChurnPieChart.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/EngagementHealthPanel.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/FilterBar.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: period / setPeriod, serviceId / setServiceId, customStart / setCustomStart, customEnd / setCustomEnd, openPeriod / setOpenPeriod, openService / setOpenService, services / setServices, globalStats / setGlobalStats, globalStatsLoading / setGlobalStatsLoading
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/KPICard.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx
- Purpose: Trial analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/retention/CohortHeatmap.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/retention/RetentionCurve.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/retention/ServiceRetentionRadar.jsx
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/SubscriptionDonutChart.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/TabNavigation.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/RevenueTab.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/TopServicesTable.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/ActivityHeatmap.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: hoveredCell / setHoveredCell
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/InactivityAnalysis.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx
- Purpose: Trial analytics feature
- API endpoint(s) called: None detected
- State variables: sortKey / setSortKey, sortOrder / setSortOrder
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/UserGrowthChart.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/directory/Directory.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: searchQuery / setSearchQuery
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/AppLayout.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/Footer.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/navConfig.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/Sidebar.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: isCollapsed / setIsCollapsed
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/SidebarNavItem.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/SidebarSection.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/Topbar.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: showNotifications / setShowNotifications, searchQuery / setSearchQuery
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/ConfirmDeleteModal.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/CreateUserModal.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: /platform-users
- State variables: formData / setFormData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/EditUserModal.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: formData / setFormData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/UserFilters.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/UserKPICards.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/UserTable.jsx
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/subscribers/UserRowDetail.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: detail / setDetail, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

## Files Group: Tests

### user-analytics-backend/tests/__init__.py
- Status: Empty file

## Files Group: Remaining files

### .agents/skills/supabase-postgres-best-practices/AGENTS.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/CLAUDE.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/README.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/_contributing.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/_sections.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/_template.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/advanced-full-text-search.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/advanced-jsonb-indexing.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/conn-idle-timeout.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/conn-limits.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/conn-pooling.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/conn-prepared-statements.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/data-batch-inserts.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/data-n-plus-one.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/data-pagination.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/data-upsert.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/lock-advisory.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/lock-deadlock-prevention.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/lock-short-transactions.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/lock-skip-locked.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/monitor-explain-analyze.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/monitor-pg-stat-statements.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/monitor-vacuum-analyze.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/query-composite-indexes.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/query-covering-indexes.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/query-index-types.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/query-missing-indexes.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/query-partial-indexes.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/schema-constraints.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/schema-data-types.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/schema-foreign-key-indexes.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/schema-lowercase-identifiers.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/schema-partitioning.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/schema-primary-keys.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/security-privileges.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/security-rls-basics.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/references/security-rls-performance.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .agents/skills/supabase-postgres-best-practices/SKILL.md
- Purpose: Non-Python/non-frontend artifact (.md)

### .gitignore
- Purpose: Non-Python/non-frontend artifact (no extension)

### .gitignore.bak.20260328_115606
- Purpose: Non-Python/non-frontend artifact (.20260328_115606)

### .report_all_files.txt
- Purpose: Non-Python/non-frontend artifact (.txt)

### .vscode/settings.json
- Purpose: Non-Python/non-frontend artifact (.json)

### analytics-platform-front/.dockerignore
- Purpose: Non-Python/non-frontend artifact (no extension)

### analytics-platform-front/.env.example
- Purpose: Non-Python/non-frontend artifact (.example)

### analytics-platform-front/.gitignore
- Purpose: Non-Python/non-frontend artifact (no extension)

### analytics-platform-front/Dockerfile
- Purpose: Non-Python/non-frontend artifact (no extension)

### analytics-platform-front/eslint.config.js
- Purpose: Non-Python/non-frontend artifact (.js)

### analytics-platform-front/index.html
- Purpose: Non-Python/non-frontend artifact (.html)

### analytics-platform-front/package-lock.json
- Purpose: Non-Python/non-frontend artifact (.json)

### analytics-platform-front/package.json
- Purpose: Non-Python/non-frontend artifact (.json)

### analytics-platform-front/postcss.config.js
- Purpose: Non-Python/non-frontend artifact (.js)

### analytics-platform-front/public/digmaco.png
- Purpose: Non-Python/non-frontend artifact (.png)

### analytics-platform-front/README.md
- Purpose: Non-Python/non-frontend artifact (.md)

### analytics-platform-front/src/App.css
- Purpose: Non-Python/non-frontend artifact (.css)

### analytics-platform-front/src/App.jsx
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/assets/digmaco.png
- Purpose: Non-Python/non-frontend artifact (.png)

### analytics-platform-front/src/assets/react.svg
- Purpose: Non-Python/non-frontend artifact (.svg)

### analytics-platform-front/src/constants/dateFilters.js
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignComparison.js
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignImpactDashboard.js
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, isLoading / setIsLoading, error / setError, data / setData, isLoading / setIsLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignKPIs.js
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignPerformance.js
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignTimeline.js
- Purpose: Campaign analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnBreakdown.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnCurve.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnDashboard.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, isLoading / setIsLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnKPIs.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnPredictionMetrics.js
- Purpose: Churn analytics feature
- API endpoint(s) called: /ml/churn/metrics
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnPredictionScores.js
- Purpose: Churn analytics feature
- API endpoint(s) called: /ml/churn/scores
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnPredictionTrain.js
- Purpose: Churn analytics feature
- API endpoint(s) called: /ml/churn/train
- State variables: loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnReasons.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCohortsTable.js
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCrossService.js
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: overview / setOverview, coSubscriptions / setCoSubscriptions, migrations / setMigrations, distribution / setDistribution, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useDashboardMetrics.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useImportData.js
- Purpose: Frontend component/page
- API endpoint(s) called: /admin/import/history
- State variables: loading / setLoading, historyLoading / setHistoryLoading, error / setError, history / setHistory
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useManagement.js
- Purpose: Campaign analytics feature
- API endpoint(s) called: /admin/management/campaigns, /admin/management/services
- State variables: services / setServices, campaigns / setCampaigns, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRetentionCurve.js
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRetentionHeatmap.js
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRetentionKPIs.js
- Purpose: Retention analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRiskSegments.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTimeToChurn.js
- Purpose: Churn analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useToast.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: toast / setToast
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTrialDropoffByDay.js
- Purpose: Trial analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTrialKPIs.js
- Purpose: Trial analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTrialUsers.js
- Purpose: Trial analytics feature
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useUserActivity.js
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useUsers.js
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/index.css
- Purpose: Non-Python/non-frontend artifact (.css)

### analytics-platform-front/src/main.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/router/AdminRoute.jsx
- Purpose: Dashboard aggregation feature
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/router/PrivateRoute.jsx
- Purpose: Frontend component/page
- API endpoint(s) called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/tailwind.config.js
- Purpose: Non-Python/non-frontend artifact (.js)

### analytics-platform-front/vite.config.js
- Purpose: Non-Python/non-frontend artifact (.js)

### docs/architecture.md
- Purpose: Non-Python/non-frontend artifact (.md)

### docs/Digital Campaign Objectives & Service Overview.pdf
- Purpose: Non-Python/non-frontend artifact (.pdf)

### docs/etl_prod_readme.md
- Purpose: Non-Python/non-frontend artifact (.md)

### docs/kpis.md
- Purpose: Non-Python/non-frontend artifact (.md)

### docs/ml_churn_report.md
- Purpose: Non-Python/non-frontend artifact (.md)

### docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf
- Purpose: Non-Python/non-frontend artifact (.pdf)

### docs/Rapport_Avancement_PFE.pdf
- Purpose: Non-Python/non-frontend artifact (.pdf)

### docs/REAL_DATA_INTEGRATION.md
- Purpose: Non-Python/non-frontend artifact (.md)

### docs/tmp/generate_rapport.py
- Purpose: Rapport d'Avancement PFE — User Behavior Analytics & Insights Platform
- Important constants/configuration:
  - DARK_BLUE = HexColor('#1a237e')
  - MED_BLUE = HexColor('#283593')
  - LIGHT_BLUE = HexColor('#e8eaf6')
  - ACCENT = HexColor('#1565c0')
  - GREEN = HexColor('#2e7d32')
  - ORANGE = HexColor('#ef6c00')
  - RED = HexColor('#c62828')
  - GRAY_BG = HexColor('#f5f5f5')
  - GRAY_TEXT = HexColor('#616161')
  - WHITE = white
  - BLACK = black
```python
def hr() -> Any: ...  # No docstring
def spacer(h: Any) -> Any: ...  # No docstring
def badge(text: Any, color: Any) -> Any: ...  # Returns a colored badge paragraph.
def status_cell(pct: Any, label: Any) -> Any: ...  # No docstring
def make_table(data: Any, col_widths: Any, header: Any) -> Any: ...  # No docstring
def header_footer(canvas: Any, doc: Any) -> Any: ...  # No docstring
def build_pdf(output_path: Any) -> Any: ...  # No docstring
```

### docs/tmp/pdfs/cahier_charges_extract.txt
- Purpose: Non-Python/non-frontend artifact (.txt)

### docs/tmp/pdfs/rapport_avancement_extract.txt
- Purpose: Non-Python/non-frontend artifact (.txt)

### docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-23_p1.png
- Purpose: Non-Python/non-frontend artifact (.png)

### docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-24.pdf
- Purpose: Non-Python/non-frontend artifact (.pdf)

### docs/TRIAL_INTEGRATION_SUMMARY.md
- Purpose: Non-Python/non-frontend artifact (.md)

### reorganize_project.py
- Purpose: Python module implementing reorganize project
- Important constants/configuration:
  - COMBINED_GITIGNORE = '# Python\n__pycache__/\n*.py[cod]\n*.pyo\n.pytest_cache/\n.coverage\nhtmlcov/\ndist/\n*.egg-info/\nvenv/\n.venv/\nenv/\n\n# Environnement\n.env\n*.env.local\n\n# Logs\nlogs/\n*.log\n\n# IDE\n.vscode/settings.json\n.idea/\n*.swp\n\n# OS\n.DS_Store\nThumbs.db\n\n# Node\nnode_modules/\ndist/\nbuild/\n\n# Data\n*.csv\n*.xlsx\n__pycache__\n'
  - BACKEND_ENV_EXAMPLE = '# Database\nANALYTICS_CONN=postgresql+psycopg2://user:password@localhost:5432/analytics_db\nPROD_CONN=postgresql+psycopg2://user:password@hawala_host:5432/hawala_db\n\n# API\nSECRET_KEY=your-secret-key-here\nALGORITHM=HS256\nACCESS_TOKEN_EXPIRE_MINUTES=1440\n\n# App\nENVIRONMENT=development\nDEBUG=true\nCORS_ORIGINS=["http://localhost:5173"]\n\n# Frontend\nVITE_API_BASE_URL=http://localhost:8000/api/v1\n'
  - MAKEFILE_CONTENT = '.PHONY: dev migrate seed test lint\n\ndev:\n\tuvicorn app.main:app --reload --host 0.0.0.0 --port 8000\n\nmigrate:\n\talembic upgrade head\n\nseed:\n\tpython scripts/seeder/seed_missing_data.py\n\nseed-dry:\n\tpython scripts/seeder/seed_missing_data.py --dry-run\n\ntest:\n\tpytest tests/ -v\n\nlint:\n\truff check app/ scripts/\n\tblack app/ scripts/ --check\n\nformat:\n\tblack app/ scripts/\n\truff check app/ scripts/ --fix\n\netl:\n\tpython scripts/etl/etl_prod_to_analytics.py\n\netl-fix:\n\tpython scripts/etl/fix_services_mapping.py\n'
  - PYPROJECT_CONTENT = '[project]\nname = "user-analytics-backend"\nversion = "1.0.0"\nrequires-python = ">=3.11"\n\ndependencies = [\n    "fastapi>=0.111.0",\n    "uvicorn[standard]>=0.29.0",\n    "sqlalchemy>=2.0.0",\n    "alembic>=1.13.0",\n    "psycopg2-binary>=2.9.9",\n    "pydantic>=2.7.0",\n    "pydantic-settings>=2.2.0",\n    "python-dotenv>=1.0.0",\n    "python-jose[cryptography]>=3.3.0",\n    "passlib[bcrypt]>=1.7.4",\n    "faker>=24.0.0",\n    "tqdm>=4.66.0",\n    "pandas>=2.2.0",\n    "openpyxl>=3.1.0",\n]\n\n[tool.ruff]\nline-length = 100\ntarget-version = "py311"\n\n[tool.black]\nline-length = 100\ntarget-version = ["py311"]\n'
  - README_CONTENT = '# User Analytics Platform - PFE DigMaco\n\n## Stack\n- Backend: FastAPI + PostgreSQL + Alembic + SQLAlchemy\n- Frontend: React + Vite\n- ETL: Python scripts (hawala -> analytics_db)\n\n## Setup\n\n### Backend\n```bash\ncp .env.example .env\npip install -e .\nmake migrate\nmake seed\nmake dev\n```\n\n### Frontend\n```bash\ncd user-analytics-frontend\ncp .env.example .env\nnpm install\nnpm run dev\n```\n\n## Commandes utiles\n| Commande | Action |\n|----------|--------|\n| make dev | Lancer FastAPI |\n| make migrate | Appliquer migrations |\n| make seed | Seeder la base analytics |\n| make etl | ETL hawala -> analytics |\n| make test | Tests unitaires |\n| make lint | Verifier le code |\n'
```python
def parse_args() -> argparse.Namespace: ...  # No docstring
def main() -> None: ...  # No docstring
class Report(object):  # No docstring
    def to_dict(self: Any) -> dict: ...  # No docstring
class Reorganizer(object):  # No docstring
    def __init__(self: Any, root: Path, dry_run: bool) -> Any: ...  # No docstring
    def _detect_frontend_dir(self: Any) -> Path | None: ...  # No docstring
    def _log(self: Any, action: str, target: str, status: str, **extra: str) -> None: ...  # No docstring
    def _safe_rel(self: Any, path: Path) -> str: ...  # No docstring
    def _mkdir(self: Any, path: Path) -> None: ...  # No docstring
    def _backup_if_needed(self: Any, path: Path) -> None: ...  # No docstring
    def _write_file(self: Any, path: Path, content: str) -> None: ...  # No docstring
    def _delete_path(self: Any, path: Path, reason: str) -> None: ...  # No docstring
    def _module_from_path(self: Any, py_path: Path) -> str | None: ...  # No docstring
    def _move_file(self: Any, src: Path, dst: Path, reason: str) -> None: ...  # No docstring
    def _ensure_backend_structure(self: Any) -> None: ...  # No docstring
    def _move_backend_root_scripts(self: Any) -> None: ...  # No docstring
    def _cleanup_unwanted(self: Any) -> None: ...  # No docstring
    def _update_python_imports(self: Any) -> None: ...  # No docstring
    def _generate_standard_files(self: Any) -> None: ...  # No docstring
    def run(self: Any) -> Report: ...  # No docstring
```

### reorganize_report.json
- Purpose: Non-Python/non-frontend artifact (.json)

### reorganize_report_apply.json
- Purpose: Non-Python/non-frontend artifact (.json)

### skills-lock.json
- Purpose: Non-Python/non-frontend artifact (.json)

### tmp/generate_project_report.py
- Purpose: Python module implementing generate project report
- Important constants/configuration:
  - ROOT = Path('c:\\Users\\Yessine-PC\\Desktop\\pfev0')
  - OUTPUT = ROOT / 'PROJECT_REPORT.md'
  - EXCLUDED_DIRS = {'venv', 'node_modules', 'dist', 'build', '__pycache__', '.git', '.venv'}
  - EXCLUDED_SUFFIXES = {'.pyc'}
  - KPI_KEYS = {'DAU': ['dau', 'daily active users'], 'WAU': ['wau', 'weekly active users'], 'MAU': ['mau', 'monthly active users'], 'Stickiness': ['stickiness', 'dau/mau'], 'Churn Rate': ['churn', 'churn rate'], 'Retention': ['retention', 'cohort'], 'ARPU': ['arpu', 'average revenue per user'], 'Avg Lifetime': ['lifetime', 'avg lifetime', 'average lifetime'], 'NRR': ['nrr', 'net revenue retention'], 'Trial Conversion': ['trial conversion', 'conversion'], 'Drop-off J3': ['drop-off', 'dropoff', 'j3'], 'Campaign ROI': ['campaign roi', 'roi']}
  - FOLDER_ROLE_HINTS = {'app': 'Backend FastAPI application core', 'api': 'API layer and route declarations', 'routers': 'FastAPI endpoint grouping', 'repositories': 'Database data access layer', 'services': 'Business logic and KPI computations', 'models': 'SQLAlchemy ORM models', 'schemas': 'Pydantic request/response schemas', 'core': 'Core configuration, security, and shared backend setup', 'utils': 'Reusable helper utilities', 'alembic': 'Database migration tooling', 'versions': 'Database migration revision scripts', 'scripts': 'Operational and ETL scripts', 'etl': 'ETL jobs from source DB to analytics DB', 'sql': 'Raw SQL scripts', 'seeder': 'Data seed scripts', 'tests': 'Automated test suite', 'analytics-platform-front': 'React frontend application', 'src': 'Frontend source code', 'pages': 'Frontend route-level pages', 'components': 'Reusable frontend components', 'hooks': 'Frontend data hooks for API/KPI', 'context': 'React context providers', 'services': 'Frontend API clients and backend services', 'docs': 'Project documentation', 'migrations': 'Standalone SQL migration scripts', 'ml_models': 'Serialized models and ML utilities', 'public': 'Static frontend assets', 'assets': 'Frontend local assets'}
```python
def should_skip(path: Path) -> bool: ...  # No docstring
def walk_files(root: Path) -> List[Path]: ...  # No docstring
def rel(path: Path) -> str: ...  # No docstring
def make_tree(root: Path) -> str: ...  # No docstring
def folder_descriptions(files: List[Path]) -> List[Tuple[str, str]]: ...  # No docstring
def read_text(path: Path) -> str: ...  # No docstring
def node_to_str(node: Optional[ast.AST]) -> str: ...  # No docstring
def get_func_signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]: ...  # No docstring
def parse_python(path: Path) -> Dict[str, Any]: ...  # No docstring
def extract_todos(path: Path, text: str) -> List[Dict[str, str]]: ...  # No docstring
def extract_env_vars(text: str) -> List[Tuple[str, str]]: ...  # No docstring
def extract_sql_files(files: List[Path]) -> List[Dict[str, str]]: ...  # No docstring
def scan_react(path: Path, text: str) -> Dict[str, Any]: ...  # No docstring
def summarize_kpis(all_texts: List[Tuple[str, str]]) -> Dict[str, Dict[str, Any]]: ...  # No docstring
def completion_estimate(files: List[Path], py_infos: Dict[str, Dict[str, Any]], react_infos: Dict[str, Dict[str, Any]]) -> Dict[str, str]: ...  # No docstring
def main() -> Any: ...  # No docstring
```
- Placeholders/missing patterns:
  - NotImplementedError present

### user-analytics-backend/.dockerignore
- Purpose: Non-Python/non-frontend artifact (no extension)

### user-analytics-backend/.env.example
- Purpose: Non-Python/non-frontend artifact (.example)

### user-analytics-backend/alembic/env.py
- Purpose: Python module implementing env
- Important constants/configuration:
  - DATABASE_URL = settings.DATABASE_URL
```python
def run_migrations_offline() -> None: ...  # Run migrations in 'offline' mode.
def run_migrations_online() -> None: ...  # Run migrations in 'online' mode.
```

### user-analytics-backend/alembic/README
- Purpose: Non-Python/non-frontend artifact (no extension)

### user-analytics-backend/alembic/script.py.mako
- Purpose: Non-Python/non-frontend artifact (.mako)

### user-analytics-backend/alembic/versions/3939f80c5a66_seeders.py
- Purpose: seeders
- Important constants/configuration: None detected
```python
def upgrade() -> None: ...  # Upgrade schema.
def downgrade() -> None: ...  # Downgrade schema.
```
- Placeholders/missing patterns:
  - pass statement found
  - pass statement found

### user-analytics-backend/alembic/versions/6c076db13bed_add_analytics_performance_indexes.py
- Purpose: add_analytics_performance_indexes
- Important constants/configuration: None detected
```python
def upgrade() -> None: ...  # Upgrade schema.
def downgrade() -> None: ...  # Downgrade schema.
```

### user-analytics-backend/alembic/versions/8ce268d4732a_initial_migration.py
- Purpose: initial migration
- Important constants/configuration: None detected
```python
def upgrade() -> None: ...  # Upgrade schema.
def downgrade() -> None: ...  # Downgrade schema.
```
- Placeholders/missing patterns:
  - pass statement found
  - pass statement found

### user-analytics-backend/alembic/versions/ded5564102c8_initial_migration3.py
- Purpose: initial migration3
- Important constants/configuration: None detected
```python
def upgrade() -> None: ...  # Upgrade schema.
def downgrade() -> None: ...  # Downgrade schema.
```

### user-analytics-backend/alembic/versions/dff7e0993f3d_initial_migration1.py
- Purpose: initial migration1
- Important constants/configuration: None detected
```python
def upgrade() -> None: ...  # Upgrade schema.
def downgrade() -> None: ...  # Downgrade schema.
```
- Placeholders/missing patterns:
  - pass statement found
  - pass statement found

### user-analytics-backend/app/__init__.py
- Status: Empty file

### user-analytics-backend/app/core/__init__.py
- Status: Empty file

### user-analytics-backend/app/core/database.py
- Purpose: Python module implementing database
- Important constants/configuration:
  - DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:12345hawala@localhost:5433/analytics_db')
```python
def get_db() -> Any: ...  # No docstring
```

### user-analytics-backend/app/core/date_ranges.py
- Purpose: Python module implementing date ranges
- Important constants/configuration:
  - DATA_START_DATE = date(2025, 9, 1)
  - DATA_END_DATE = date(2025, 10, 31)
```python
def resolve_date_range(start_date: Optional[date], end_date: Optional[date], db: Session | None, source: AnchorSource) -> tuple[date, date]: ...  # Resolve API date filters to a deterministic range.
```

### user-analytics-backend/app/core/dependencies.py
- Purpose: Python module implementing dependencies
- Important constants/configuration: None detected
```python
def get_current_user(token: str, db: Session) -> PlatformUser: ...  # No docstring
def require_admin(current_user: PlatformUser) -> PlatformUser: ...  # No docstring
```

### user-analytics-backend/app/core/security.py
- Purpose: Python module implementing security
- Important constants/configuration: None detected
```python
def hash_password(plain: str) -> str: ...  # No docstring
def verify_password(plain: str, hashed: str) -> bool: ...  # No docstring
def create_access_token(data: dict, expires_delta: timedelta | None) -> str: ...  # No docstring
def decode_access_token(token: str) -> dict: ...  # No docstring
```

### user-analytics-backend/app/main.py
- Purpose: Python module implementing main
- Important constants/configuration: None detected
```python
def on_startup() -> Any: ...  # No docstring
def root() -> Any: ...  # No docstring
```

### user-analytics-backend/Dockerfile
- Purpose: Non-Python/non-frontend artifact (no extension)

### user-analytics-backend/logs/.gitkeep
- Status: Empty file

### user-analytics-backend/Makefile
- Purpose: Non-Python/non-frontend artifact (no extension)

### user-analytics-backend/migrations/create_import_logs.sql
- Purpose: Raw SQL script
```sql
-- Migration SQL: create import_logs table
-- Run manually or via your migration system

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS import_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imported_at     TIMESTAMP DEFAULT NOW(),
    admin_id        UUID REFERENCES platform_users(id),
    file_name       VARCHAR(255),
    file_type       VARCHAR(10),  -- "csv" | "sql"
    target_table    VARCHAR(50),
    mode            VARCHAR(20),
    rows_inserted   INTEGER DEFAULT 0,
    rows_skipped    INTEGER DEFAULT 0,
    status          VARCHAR(20),
    error_details   JSONB
);

CREATE INDEX IF NOT EXISTS ix_import_logs_imported_at ON import_logs(imported_at);
CREATE INDEX IF NOT EXISTS ix_import_logs_admin_id ON import_logs(admin_id);
```

### user-analytics-backend/ml_models/__init__.py
- Status: Empty file

### user-analytics-backend/ml_models/churn_metrics.joblib
- Purpose: Non-Python/non-frontend artifact (.joblib)

### user-analytics-backend/ml_models/churn_model.joblib
- Purpose: Non-Python/non-frontend artifact (.joblib)

### user-analytics-backend/ml_models/churn_predictor.py
- Purpose: Python module implementing churn predictor
- Important constants/configuration: None detected
```python
class ChurnPredictionResult(object):  # No docstring
class ChurnPredictor(object):  # Logistic Regression based churn predictor.
    def __init__(self: Any, model_path: str | None, metrics_path: str | None, random_state: int) -> Any: ...  # No docstring
    def _read_sql_to_df(self: Any, db_session: Session, query: str, params: dict[str, Any] | None) -> pd.DataFrame: ...  # No docstring
    def _base_features_sql(self: Any) -> str: ...  # Build a subscription-level dataset with features + churned label.
    def _active_scoring_features_sql(self: Any, service_id: str | None, start_date: str | None, end_date: str | None) -> str: ...  # Build subscription-level dataset for active scoring.
    def generate_training_dataset(self: Any, db_session: Session) -> tuple[pd.DataFrame, pd.Series]: ...  # No docstring
    def train(self: Any, db_session: Session) -> dict[str, Any]: ...  # No docstring
    def load(self: Any) -> bool: ...  # No docstring
    def load_metrics(self: Any) -> dict[str, Any] | None: ...  # No docstring
    def _risk_category(self: Any, churn_risk: float) -> RiskCategory: ...  # No docstring
    def predict_active_subscriptions(self: Any, db_session: Session, threshold: float, store_predictions: bool, service_id: str | None, start_date: str | None, end_date: str | None) -> ChurnPredictionResult: ...  # No docstring
```

### user-analytics-backend/note.txt
- Purpose: Non-Python/non-frontend artifact (.txt)

### user-analytics-backend/README.md
- Purpose: Non-Python/non-frontend artifact (.md)

### user-analytics-backend/requirements.txt
- Purpose: Non-Python/non-frontend artifact (.txt)

### user-analytics-backend/scripts/compute_cohorts.py
- Purpose: ETL Script — Compute & populate cohorts table
- Important constants/configuration: None detected
```python
def compute_cohorts() -> Any: ...  # No docstring
```

### user-analytics-backend/scripts/seeder/__init__.py
- Status: Empty file

### user-analytics-backend/scripts/seeder/seed_missing_data.py
- Purpose: Seed missing analytics data after ETL from production.
- Important constants/configuration:
  - BATCH_SIZE = 10000
```python
def log_json(message: str, **kwargs: Any) -> None: ...  # No docstring
def parse_args() -> argparse.Namespace: ...  # No docstring
def get_engine() -> Engine: ...  # No docstring
def random_peak_datetime(last_n_days: int) -> datetime: ...  # No docstring
def execute_batch(conn: Any, stmt: Any, rows: list[dict[str, Any]], dry_run: bool) -> int: ...  # No docstring
def fix_last_activity_at(engine: Engine, dry_run: bool) -> SeedMetrics: ...  # No docstring
def seed_campaigns(engine: Engine, n: int, dry_run: bool) -> SeedMetrics: ...  # No docstring
def seed_user_activities(engine: Engine, n: int, dry_run: bool) -> SeedMetrics: ...  # No docstring
def compute_and_insert_cohorts(engine: Engine, dry_run: bool) -> SeedMetrics: ...  # No docstring
def derive_unsubscriptions(engine: Engine, dry_run: bool) -> SeedMetrics: ...  # No docstring
def seed_sms_events(engine: Engine, n: int, dry_run: bool) -> SeedMetrics: ...  # No docstring
def run_step(step: str, engine: Engine, args: argparse.Namespace) -> None: ...  # No docstring
def main() -> None: ...  # No docstring
class SeedMetrics(object):  # No docstring
```
- Placeholders/missing patterns:
  - pass statement found

### user-analytics-backend/scripts/sql/diagnostics.sql
- Purpose: Raw SQL script
```sql
-- Verification queries for services mapping consistency
-- Source: hawala
-- Target: analytics_db

-- 1) Source distribution by real service mapping (service_subscription_type_id -> service_id)
SELECT
    s.id AS source_service_id,
    s.entitled AS source_service_name,
    COUNT(*) AS source_subscriptions
FROM subscribed_clients sc
JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
JOIN services s ON s.id = sst.service_id
GROUP BY s.id, s.entitled
ORDER BY source_subscriptions DESC;

-- 2) Target distribution by service after fix
SELECT
    sv.id AS target_service_id,
    sv.name AS target_service_name,
    COUNT(*) AS analytics_subscriptions
FROM subscriptions sub
JOIN services sv ON sv.id = sub.service_id
GROUP BY sv.id, sv.name
ORDER BY analytics_subscriptions DESC;

-- 3) Side-by-side source vs target counts by normalized service name
WITH src AS (
    SELECT
        s.id AS source_service_id,
        s.entitled AS service_name,
        COUNT(*) AS source_count
    FROM subscribed_clients sc
    JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
    JOIN services s ON s.id = sst.service_id
    GROUP BY s.id, s.entitled
),
tgt AS (
    SELECT
        sv.id AS target_service_uuid,
        sv.name AS service_name,
        COUNT(*) AS target_count
    FROM subscriptions sub
    JOIN services sv ON sv.id = sub.service_id
    GROUP BY sv.id, sv.name
)
SELECT
    src.source_service_id,
    src.service_name,
    src.source_count,
    COALESCE(tgt.target_count, 0) AS target_count,
    src.source_count - COALESCE(tgt.target_count, 0) AS delta
FROM src
LEFT JOIN tgt ON lower(trim(tgt.service_name)) = lower(trim(src.service_name))
ORDER BY ABS(src.source_count - COALESCE(tgt.target_count, 0)) DESC, src.source_count DESC;

-- 4) Check unmapped service_subscription_type_id in source
SELECT
    sc.service_subscription_type_id,
    COUNT(*) AS rows_count
FROM subscribed_clients sc
LEFT JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
WHERE sc.service_subscription_type_id IS NOT NULL
  AND sst.id IS NULL
GROUP BY sc.service_subscription_type_id
ORDER BY rows_count DESC;

-- 5) Check subscriptions linked to missing users/services in analytics (should be 0)
SELECT
    SUM(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END) AS missing_users,
    SUM(CASE WHEN sv.id IS NULL THEN 1 ELSE 0 END) AS missing_services
FROM subscriptions sub
LEFT JOIN users u ON u.id = sub.user_id
LEFT JOIN services sv ON sv.id = sub.service_id;
```

### user-analytics-backend/scripts/verify_data.py
- Purpose: Post-fix verification for Hawala -> analytics data pipeline.
- Important constants/configuration:
  - DATA_START_DATE = '2025-09-01'
```python
def _load_env() -> None: ...  # No docstring
def _scalar(conn: Any, sql: str, params: dict | None) -> Any: ...  # No docstring
def verify() -> int: ...  # No docstring
```

## 3. SQL Queries Inventory

### Source file: user-analytics-backend/migrations/create_import_logs.sql
```sql
-- Migration SQL: create import_logs table
-- Run manually or via your migration system

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS import_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imported_at     TIMESTAMP DEFAULT NOW(),
    admin_id        UUID REFERENCES platform_users(id),
    file_name       VARCHAR(255),
    file_type       VARCHAR(10),  -- "csv" | "sql"
    target_table    VARCHAR(50),
    mode            VARCHAR(20),
    rows_inserted   INTEGER DEFAULT 0,
    rows_skipped    INTEGER DEFAULT 0,
    status          VARCHAR(20),
    error_details   JSONB
);

CREATE INDEX IF NOT EXISTS ix_import_logs_imported_at ON import_logs(imported_at);
CREATE INDEX IF NOT EXISTS ix_import_logs_admin_id ON import_logs(admin_id);
```
- KPI/data computed: Requires manual domain confirmation per query context
- Input parameters: Depends on WHERE/filter clauses in query
- Output columns/shape: Derived from SELECT projection
- Nearby TODO/issues: See section 11

### Source file: user-analytics-backend/scripts/sql/diagnostics.sql
```sql
-- Verification queries for services mapping consistency
-- Source: hawala
-- Target: analytics_db

-- 1) Source distribution by real service mapping (service_subscription_type_id -> service_id)
SELECT
    s.id AS source_service_id,
    s.entitled AS source_service_name,
    COUNT(*) AS source_subscriptions
FROM subscribed_clients sc
JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
JOIN services s ON s.id = sst.service_id
GROUP BY s.id, s.entitled
ORDER BY source_subscriptions DESC;

-- 2) Target distribution by service after fix
SELECT
    sv.id AS target_service_id,
    sv.name AS target_service_name,
    COUNT(*) AS analytics_subscriptions
FROM subscriptions sub
JOIN services sv ON sv.id = sub.service_id
GROUP BY sv.id, sv.name
ORDER BY analytics_subscriptions DESC;

-- 3) Side-by-side source vs target counts by normalized service name
WITH src AS (
    SELECT
        s.id AS source_service_id,
        s.entitled AS service_name,
        COUNT(*) AS source_count
    FROM subscribed_clients sc
    JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
    JOIN services s ON s.id = sst.service_id
    GROUP BY s.id, s.entitled
),
tgt AS (
    SELECT
        sv.id AS target_service_uuid,
        sv.name AS service_name,
        COUNT(*) AS target_count
    FROM subscriptions sub
    JOIN services sv ON sv.id = sub.service_id
    GROUP BY sv.id, sv.name
)
SELECT
    src.source_service_id,
    src.service_name,
    src.source_count,
    COALESCE(tgt.target_count, 0) AS target_count,
    src.source_count - COALESCE(tgt.target_count, 0) AS delta
FROM src
LEFT JOIN tgt ON lower(trim(tgt.service_name)) = lower(trim(src.service_name))
ORDER BY ABS(src.source_count - COALESCE(tgt.target_count, 0)) DESC, src.source_count DESC;

-- 4) Check unmapped service_subscription_type_id in source
SELECT
    sc.service_subscription_type_id,
    COUNT(*) AS rows_count
FROM subscribed_clients sc
LEFT JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
WHERE sc.service_subscription_type_id IS NOT NULL
  AND sst.id IS NULL
GROUP BY sc.service_subscription_type_id
ORDER BY rows_count DESC;

-- 5) Check subscriptions linked to missing users/services in analytics (should be 0)
SELECT
    SUM(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END) AS missing_users,
    SUM(CASE WHEN sv.id IS NULL THEN 1 ELSE 0 END) AS missing_services
FROM subscriptions sub
LEFT JOIN users u ON u.id = sub.user_id
LEFT JOIN services sv ON sv.id = sub.service_id;
```
- KPI/data computed: Requires manual domain confirmation per query context
- Input parameters: Depends on WHERE/filter clauses in query
- Output columns/shape: Derived from SELECT projection
- Nearby TODO/issues: See section 11

### Inline SQL in: reorganize_project.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
Reorganize PFE full-stack project with safe dry-run mode.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
update
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete-failed
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete-failed
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: reorganize_project.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
- Protected endpoints: endpoints with Depends/current_user/role checks (see FastAPI routes section).
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
- Output columns/shape: Derived from SELECT projection
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
- Frontend page display: inferred from matching hooks/pages with same KPI keyword
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
\b(SELECT|INSERT|UPDATE|DELETE|WITH|CREATE\s+TABLE|ALTER\s+TABLE)\b
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
(?:fetch|axios\.(?:get|post|put|delete|patch)|api\.(?:get|post|put|delete|patch))\s*\(\s*['\"]([^'\"]+)['\"]
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
- Output columns/shape: SQL SELECT projection or DML rowcount
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
(SELECT[\s\S]{0,500}?(?:;|\n\n))
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: tmp/generate_project_report.py
```sql
DELETE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/alembic/env.py
```sql
Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/alembic/env.py
```sql
Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/__init__.py
```sql
SQLAlchemy ORM models for user-analytics-backend.
Import all models here to ensure they are registered with Base.metadata.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/service_types.py
```sql
Billing types with pricing - daily, weekly, monthly
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/subscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/subscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/subscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/subscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/subscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/unsubscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/unsubscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/unsubscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/unsubscriptions.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/users.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/users.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/users.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/users.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/models/users.py
```sql
select
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
Get paginated list of campaigns with impact metrics.
        Uses both campaign_id (primary) and date+service (fallback) for subscription matching.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
SELECT 
                c.id,
                c.name,
                c.description,
                c.campaign_type,
                c.status,
                c.target_size,
                c.cost,
                c.send_datetime,
                COUNT(DISTINCT s.id) as subscriptions_acquired,
                COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0) as first_charges,
                COUNT(DISTINCT b.id) as total_billing_events,
                ROUND(
                    (CASE 
                        WHEN NULLIF(c.target_size, 0) IS NULL THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / c.target_size) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate,
                COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0)::FLOAT / 
                    NULLIF(COUNT(DISTINCT s.id), 0) as first_charge_rate
            FROM campaigns c
            LEFT JOIN subscriptions s
                ON (
                    -- Primary: via campaign_id (if set)
                    s.campaign_id = c.id
                    OR
                    -- Fallback: via date+service (within 7 days after send_datetime)
                    (
                        s.service_id = c.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                    )
                )
            LEFT JOIN billing_events b ON b.subscription_id = s.id
            WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
SELECT COUNT(DISTINCT c.id)
            FROM campaigns c
            WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
SELECT 
                COUNT(DISTINCT c.id) as total_campaigns,
                SUM(CASE WHEN c.status = 'completed' THEN 1 ELSE 0 END) as completed_campaigns,
                SUM(CASE WHEN c.status = 'sent' THEN 1 ELSE 0 END) as sent_campaigns,
                SUM(CASE WHEN c.status = 'scheduled' THEN 1 ELSE 0 END) as scheduled_campaigns,
                COALESCE(SUM(c.target_size), 0) as total_targeted,
                COUNT(DISTINCT s.id) as total_subscriptions,
                ROUND(
                    (CASE 
                        WHEN COALESCE(SUM(c.target_size), 0) = 0 THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / NULLIF(SUM(c.target_size), 0)) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate
            FROM campaigns c
            LEFT JOIN subscriptions s ON s.campaign_id = c.id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
SELECT 
                c.campaign_type,
                COUNT(DISTINCT c.id) as count,
                SUM(c.target_size) as targeted,
                COUNT(DISTINCT s.id) as subscriptions,
                COUNT(DISTINCT b.id) as billing_events,
                COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0) as first_charges,
                ROUND(
                    (CASE 
                        WHEN NULLIF(SUM(c.target_size), 0) IS NULL THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / SUM(c.target_size)) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate
            FROM campaigns c
            LEFT JOIN subscriptions s
                ON (
                    -- Primary: via campaign_id
                    s.campaign_id = c.id
                    OR
                    -- Fallback: via date+service (within 7 days)
                    (
                        s.service_id = c.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                    )
                )
            LEFT JOIN billing_events b ON b.subscription_id = s.id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
SELECT 
                c.id,
                c.name,
                c.campaign_type,
                c.target_size,
                COUNT(DISTINCT s.id) as subscriptions,
                ROUND(
                    (CASE 
                        WHEN NULLIF(c.target_size, 0) IS NULL THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / c.target_size) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate
            FROM campaigns c
            LEFT JOIN subscriptions s
                ON (
                    -- Primary: via campaign_id
                    s.campaign_id = c.id
                    OR
                    -- Fallback: via date+service (within 7 days)
                    (
                        s.service_id = c.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                    )
                )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/repositories/campaign_repo.py
```sql
SELECT 
                DATE_TRUNC('month', c.send_datetime)::DATE as month,
                c.campaign_type,
                COUNT(DISTINCT c.id) as campaign_count,
                SUM(c.target_size) as targeted,
                COUNT(DISTINCT s.id) as subscriptions,
                COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0) as first_charges,
                ROUND(
                    (CASE 
                        WHEN NULLIF(SUM(c.target_size), 0) IS NULL THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / SUM(c.target_size)) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate
            FROM campaigns c
            LEFT JOIN subscriptions s
                ON (
                    -- Primary: via campaign_id
                    s.campaign_id = c.id
                    OR
                    -- Fallback: via date+service (within 7 days)
                    (
                        s.service_id = c.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                    )
                )
            LEFT JOIN billing_events b ON b.subscription_id = s.id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
\b(drop|delete|truncate|alter|create|update)\b
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
insert\s+into\s+([a-zA-Z_][a-zA-Z0-9_]*)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
CREATE TABLE IF NOT EXISTS staging_imports (
              id            UUID PRIMARY KEY,
              import_id     UUID NOT NULL,
              row_number    INTEGER,
              raw_data      JSONB,
              status        VARCHAR(20),
              error_message TEXT,
              created_at    TIMESTAMP DEFAULT NOW()
            );
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
INSERT INTO staging_imports (id, import_id, row_number, raw_data, status, error_message)
            VALUES (
              CAST(:id AS uuid),
              CAST(:import_id AS uuid),
              :row_number,
              CAST(:raw_data AS jsonb),
              :status,
              :error_message
            )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
DELETE FROM staging_imports WHERE import_id = CAST(:import_id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
SELECT "
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
SELECT
              SUM(CASE WHEN status = 'valid' THEN 1 ELSE 0 END) AS valid_rows,
              SUM(CASE WHEN status = 'invalid' THEN 1 ELSE 0 END) AS invalid_rows
            FROM staging_imports
            WHERE import_id = CAST(:import_id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
INSERT INTO "
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
)
                SELECT
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
insert into
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/admin_import.py
```sql
Only INSERT/COPY allowed
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            COUNT(*)                                                          AS total_users,
            COUNT(*) FILTER (WHERE status = 'active')                         AS active_users,
            COUNT(*) FILTER (WHERE status = 'inactive')                       AS inactive_users,
            COUNT(*) FILTER (WHERE created_at BETWEEN :last30_start_dt AND :last30_end_dt) AS new_last_30_days
        FROM users
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            srv.name                                             AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')         AS active_subs,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')      AS churned_subs,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                / NULLIF(COUNT(*), 0), 1
            )                                                    AS churn_rate_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        GROUP BY srv.name
        ORDER BY active_subs DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            COUNT(*)                                                          AS total_users,
            COUNT(*) FILTER (WHERE status = 'active')                         AS active_users,
            COUNT(*) FILTER (WHERE status = 'inactive')                       AS inactive_users,
            COUNT(*) FILTER (
                WHERE created_at BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            )                                                                 AS new_last_30_days
        FROM users
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            COUNT(*)                                               AS total,
            COUNT(*) FILTER (WHERE s.status = 'active')           AS active,
            COUNT(*) FILTER (WHERE s.status = 'trial')            AS trial,
            COUNT(*) FILTER (WHERE s.status = 'expired')          AS expired,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')        AS cancelled,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'active') * 100.0
                / NULLIF(
                    COUNT(*) FILTER (WHERE s.status IN ('active','expired'))
                    + COUNT(*) FILTER (
                        WHERE s.status = 'cancelled'
                        AND (s.subscription_end_date - s.subscription_start_date)
                            <= INTERVAL '3 days'
                    ), 0
                ), 1
            )                                                      AS conversion_rate_pct
        FROM subscriptions s
        WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
WITH active_start AS (
                    SELECT COUNT(DISTINCT s.user_id) AS active_count
                    FROM subscriptions s
                    WHERE s.subscription_start_date <= :churn_month_start_dt
                        AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :churn_month_start_dt)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
),
                churn_rows AS (
          SELECT
            s.id AS subscription_id,
            s.service_id,
            COALESCE(u.unsubscription_datetime, s.subscription_end_date) AS churn_dt,
            COALESCE(
              u.churn_type,
              CASE
                WHEN s.status = 'cancelled' THEN 'VOLUNTARY'
                WHEN s.status = 'expired'   THEN 'TECHNICAL'
                ELSE NULL
              END
            ) AS churn_type,
            COALESCE(
              u.days_since_subscription,
              EXTRACT(DAY FROM (COALESCE(u.unsubscription_datetime, s.subscription_end_date) - s.subscription_start_date))::int
            ) AS days_since_subscription
          FROM subscriptions s
          LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
          WHERE COALESCE(u.unsubscription_datetime, s.subscription_end_date) IS NOT NULL
            AND s.status IN ('cancelled', 'expired')
                        AND COALESCE(u.unsubscription_datetime, s.subscription_end_date)
                                BETWEEN :churn_month_start_dt AND :churn_month_end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
)
        SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY')                 AS voluntary,
            COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL')                 AS technical,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct,
            COUNT(*) FILTER (WHERE days_since_subscription = 1)              AS dropoff_day1,
            COUNT(*) FILTER (WHERE days_since_subscription = 2)              AS dropoff_day2,
            COUNT(*) FILTER (WHERE days_since_subscription = 3)              AS dropoff_day3,
            ROUND(
                COUNT(*) FILTER (
                    WHERE churn_dt BETWEEN :churn_month_start_dt AND :churn_month_end_dt
                ) * 100.0
                / NULLIF((SELECT active_count FROM active_start), 0), 2
            )                                                                AS churn_rate_month_pct
        FROM churn_rows
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            ROUND(SUM(st.price) FILTER (WHERE be.status = 'SUCCESS'), 2)      AS total_revenue,
            COUNT(*) FILTER (WHERE be.status = 'SUCCESS')                     AS success_events,
            COUNT(*) FILTER (WHERE be.status = 'FAILED')                      AS failed_events,
            COUNT(*) FILTER (WHERE be.status IN ('FAILED', 'CANCELLED', 'PENDING')) AS non_success_events,
            ROUND(COUNT(*) FILTER (WHERE be.status = 'FAILED') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                     AS failed_pct,
            ROUND(SUM(st.price) FILTER (
                WHERE be.status = 'SUCCESS'
                AND be.event_datetime BETWEEN :billing_month_start_dt AND :billing_month_end_dt
            ), 2)                                                              AS mrr,
            ROUND(
                SUM(st.price) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime BETWEEN :billing_month_start_dt AND :billing_month_end_dt
                ) / NULLIF(COUNT(DISTINCT be.user_id) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime BETWEEN :billing_month_start_dt AND :billing_month_end_dt
                ), 0), 2
            )                                                                  AS arpu_current_month
        FROM billing_events be
        JOIN subscriptions  s   ON s.id   = be.subscription_id
        JOIN services       srv ON srv.id = s.service_id
        JOIN service_types  st  ON st.id  = srv.service_type_id
        WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_day_start_dt AND :usage_day_end_dt
            )                                                    AS dau_today,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_month_start_dt AND :usage_month_end_dt
            )                                                    AS mau_current_month,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_week_start_dt AND :usage_week_end_dt
            )                                                    AS wau_current_week
        FROM user_activities
        WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            COUNT(*)                                               AS total,
            COUNT(*) FILTER (WHERE s.status = 'active')           AS active,
            COUNT(*) FILTER (WHERE s.status = 'trial')            AS trial,
            COUNT(*) FILTER (WHERE s.status = 'expired')          AS expired,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')        AS cancelled,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'active') * 100.0
                / NULLIF(
                    COUNT(*) FILTER (WHERE s.status IN ('active','expired'))
                    + COUNT(*) FILTER (
                        WHERE s.status = 'cancelled'
                        AND (s.subscription_end_date - s.subscription_start_date)
                            <= INTERVAL '3 days'
                    ), 0
                ), 1
            )                                                      AS conversion_rate_pct
        FROM subscriptions s
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
WITH active_start AS (
                    SELECT COUNT(DISTINCT s.user_id) AS active_count
                    FROM subscriptions s
                    WHERE s.subscription_start_date <= :churn_window_start_dt
                        AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :churn_window_start_dt)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
),
                churn_rows AS (
          SELECT
            s.id AS subscription_id,
            s.service_id,
            COALESCE(u.unsubscription_datetime, s.subscription_end_date) AS churn_dt,
            COALESCE(
              u.churn_type,
              CASE
                WHEN s.status = 'cancelled' THEN 'VOLUNTARY'
                WHEN s.status = 'expired'   THEN 'TECHNICAL'
                ELSE NULL
              END
            ) AS churn_type,
            COALESCE(
              u.days_since_subscription,
              EXTRACT(DAY FROM (COALESCE(u.unsubscription_datetime, s.subscription_end_date) - s.subscription_start_date))::int
            ) AS days_since_subscription
          FROM subscriptions s
          LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
          WHERE COALESCE(u.unsubscription_datetime, s.subscription_end_date) IS NOT NULL
            AND s.status IN ('cancelled', 'expired')
                        AND COALESCE(u.unsubscription_datetime, s.subscription_end_date) BETWEEN :churn_window_start_dt AND :churn_window_end_dt + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
)
        SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY')                 AS voluntary,
            COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL')                 AS technical,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct,
            COUNT(*) FILTER (WHERE days_since_subscription = 1)              AS dropoff_day1,
            COUNT(*) FILTER (WHERE days_since_subscription = 2)              AS dropoff_day2,
            COUNT(*) FILTER (WHERE days_since_subscription = 3)              AS dropoff_day3,
            ROUND(
                COUNT(*) FILTER (
                    WHERE churn_dt BETWEEN :churn_window_start_dt AND :churn_window_end_dt + INTERVAL '1 day'
                ) * 100.0
                / NULLIF((SELECT active_count FROM active_start), 0), 2
            )                                                                AS churn_rate_month_pct
        FROM churn_rows
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            ROUND(SUM(st.price) FILTER (WHERE be.status = 'SUCCESS'), 2)      AS total_revenue,
            COUNT(*) FILTER (WHERE be.status = 'SUCCESS')                     AS success_events,
            COUNT(*) FILTER (WHERE be.status = 'FAILED')                      AS failed_events,
            COUNT(*) FILTER (WHERE be.status IN ('FAILED', 'CANCELLED', 'PENDING')) AS non_success_events,
            ROUND(COUNT(*) FILTER (WHERE be.status = 'FAILED') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                     AS failed_pct,
            ROUND(SUM(st.price) FILTER (
                WHERE be.status = 'SUCCESS'
                AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            ), 2)                                                              AS mrr,
            ROUND(
                SUM(st.price) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
                ) / NULLIF(COUNT(DISTINCT be.user_id) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
                ), 0), 2
            )                                                                  AS arpu_current_month
        FROM billing_events be
        JOIN subscriptions  s   ON s.id   = be.subscription_id
        JOIN services       srv ON srv.id = s.service_id
        JOIN service_types  st  ON st.id  = srv.service_type_id
        WHERE be.event_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_day_start_dt AND :usage_day_end_dt
            )                                                    AS dau_today,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_month_start_dt AND :usage_month_end_dt
            )                                                    AS mau_current_month,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_week_start_dt AND :usage_week_end_dt
            )                                                    AS wau_current_week
        FROM user_activities
        WHERE activity_datetime BETWEEN :usage_month_start_dt AND :usage_month_end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/analyticsOverview.py
```sql
SELECT
            srv.name                                             AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')         AS active_subs,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')      AS churned_subs,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                / NULLIF(COUNT(*), 0), 1
            )                                                    AS churn_rate_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        WHERE s.subscription_start_date BETWEEN :start_dt AND :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
Get paginated campaign list with impact metrics
    Supports filtering by status and campaign_type
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
WITH per_campaign AS (
                SELECT
                    c.id AS campaign_id,
                    c.name AS campaign_name,
                    c.target_size,
                    COUNT(s.id) AS total_subs
                FROM campaigns c
                LEFT JOIN subscriptions s ON (
                    s.campaign_id = c.id
                    OR (
                        s.service_id = c.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                    )
                )
                WHERE DATE(c.send_datetime) >= :start_dt
                  AND DATE(c.send_datetime) <= :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
GROUP BY c.id, c.name, c.target_size
            ),
            d7 AS (
                SELECT
                    AVG(co.retention_d7) AS avg_d7
                FROM campaigns c
                LEFT JOIN cohorts co
                  ON co.service_id = c.service_id
                 AND co.cohort_date = date_trunc('month', c.send_datetime)::date
                WHERE DATE(c.send_datetime) >= :start_dt
                  AND DATE(c.send_datetime) <= :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
)
            SELECT
                (SELECT COUNT(DISTINCT campaign_id) FROM per_campaign) AS total_campaigns,
                (SELECT COALESCE(SUM(total_subs), 0) FROM per_campaign) AS total_subs_from_campaigns,
                (SELECT COALESCE(AVG((total_subs::numeric / NULLIF(target_size, 0)) * 100), 0) FROM per_campaign) AS avg_conversion_rate,
                (SELECT COALESCE(avg_d7, 0) FROM d7) AS avg_retention_d7
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
SELECT
                c.name AS campaign_name,
                COUNT(s.id) AS total_subs
            FROM campaigns c
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            WHERE DATE(c.send_datetime) >= :start_dt
              AND DATE(c.send_datetime) <= :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
SELECT
              c.id   AS campaign_id,
              c.name AS name,
              c.send_datetime,
              c.target_size,
              sv.name AS service_name,
              COUNT(s.id) AS total_subs,
              COUNT(s.id) FILTER (WHERE s.status = 'active') AS active_subs,
              ROUND(COUNT(s.id) FILTER (WHERE s.status = 'active')::numeric / NULLIF(c.target_size,0) * 100, 2) AS conv_rate,
              ROUND(AVG(co.retention_d7), 2) AS avg_d7
            FROM campaigns c
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            JOIN services sv ON sv.id = c.service_id
            LEFT JOIN cohorts co ON co.service_id = c.service_id
              AND co.cohort_date = date_trunc('month', c.send_datetime)::date
            WHERE DATE(c.send_datetime) >= :start_dt
              AND DATE(c.send_datetime) <= :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
WITH per_campaign AS (
              SELECT
                c.id,
                c.service_id,
                COUNT(s.id) FILTER (WHERE s.status = 'active') AS active_subs,
                ROUND(COUNT(s.id) FILTER (WHERE s.status = 'active')::numeric / NULLIF(c.target_size,0) * 100, 2) AS conv_rate
              FROM campaigns c
              LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
              )
              WHERE DATE(c.send_datetime) >= :start_dt
                AND DATE(c.send_datetime) <= :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
GROUP BY c.id, c.service_id, c.target_size
            )
            SELECT
              sv.name AS service,
              COUNT(DISTINCT c.id) AS total_campaigns,
              COUNT(s.id) FILTER (WHERE s.status = 'active') AS total_subs,
              ROUND(AVG(pc.conv_rate), 2) AS avg_conversion,
              ROUND(AVG(co.retention_d7), 2) AS avg_d7
            FROM services sv
            JOIN campaigns c ON c.service_id = sv.id
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            LEFT JOIN per_campaign pc ON pc.id = c.id
            LEFT JOIN cohorts co ON co.service_id = c.service_id
              AND co.cohort_date = date_trunc('month', c.send_datetime)::date
            WHERE DATE(c.send_datetime) >= :start_dt
              AND DATE(c.send_datetime) <= :end_dt
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
WITH months AS (
              SELECT generate_series(
                date_trunc('month', CAST(:start_dt AS timestamp))::date,
                date_trunc('month', CAST(:end_dt   AS timestamp))::date,
                interval '1 month'
              )::date AS month_start
            ),
            campaign_subs AS (
              SELECT
                date_trunc('month', s.subscription_start_date)::date AS month_start,
                COUNT(DISTINCT s.id) AS campaign_subs
              FROM subscriptions s
              WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
                AND s.subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                AND (
                  -- Primary: has campaign_id
                  s.campaign_id IS NOT NULL
                  OR
                  -- Fallback: matches date+service window of ANY campaign
                  EXISTS (
                    SELECT 1 FROM campaigns c
                    WHERE s.service_id = c.service_id
                      AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                  )
                )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
GROUP BY 1
            ),
            organic_subs AS (
              SELECT
                date_trunc('month', s.subscription_start_date)::date AS month_start,
                COUNT(DISTINCT s.id) AS organic_subs
              FROM subscriptions s
              WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
                AND s.subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                AND (
                  -- No direct campaign_id link AND
                  s.campaign_id IS NULL
                  AND
                  -- Does not match any campaign's date+service window
                  NOT EXISTS (
                    SELECT 1 FROM campaigns c
                    WHERE s.service_id = c.service_id
                      AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                  )
                )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/campaign_impact.py
```sql
GROUP BY 1
            )
            SELECT
              to_char(m.month_start, 'YYYY-MM') AS month,
              COALESCE(c.campaign_subs, 0) AS campaign_subs,
              COALESCE(o.organic_subs, 0)  AS organic_subs
            FROM months m
            LEFT JOIN campaign_subs c ON c.month_start = m.month_start
            LEFT JOIN organic_subs  o ON o.month_start = m.month_start
            ORDER BY m.month_start ASC;
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
WITH filtered_subs AS (
                SELECT sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
),
            user_service_count AS (
                SELECT user_id, COUNT(DISTINCT service_id) AS nb_services
                FROM filtered_subs
                GROUP BY user_id
            )
            SELECT
                COUNT(*) FILTER (WHERE nb_services >= 2) AS multi_users,
                COUNT(*)                                 AS total_users
            FROM user_service_count
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
WITH filtered_subs AS (
                SELECT DISTINCT sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
)
            SELECT s1.name AS service_a, s2.name AS service_b, COUNT(*) AS combo_count
            FROM filtered_subs fs1
            JOIN filtered_subs fs2
              ON fs1.user_id = fs2.user_id
              AND fs1.service_id < fs2.service_id
            JOIN services s1 ON fs1.service_id = s1.id
            JOIN services s2 ON fs2.service_id = s2.id
            GROUP BY s1.name, s2.name
            ORDER BY combo_count DESC
            LIMIT 1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
WITH filtered_subs AS (
                SELECT sub.user_id, sub.service_id, sub.subscription_start_date, sub.subscription_end_date
                FROM subscriptions sub
                WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
),
            user_service_count AS (
                SELECT user_id, COUNT(DISTINCT service_id) AS nb_services
                FROM filtered_subs
                GROUP BY user_id
            ),
            sub_with_seg AS (
                SELECT
                    fs.user_id,
                    fs.subscription_start_date,
                    fs.subscription_end_date,
                    CASE WHEN usc.nb_services >= 2 THEN 'multi' ELSE 'mono' END AS segment
                FROM filtered_subs fs
                JOIN user_service_count usc ON usc.user_id = fs.user_id
            )
            SELECT
                segment,
                COUNT(*) AS total,
                COUNT(*) FILTER (
                    WHERE subscription_end_date IS NULL
                       OR EXTRACT(DAY FROM subscription_end_date - subscription_start_date) >= 30
                ) AS retained_d30
            FROM sub_with_seg
            GROUP BY segment
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
WITH filtered_subs AS (
                SELECT sub.id, sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
),
            user_service_count AS (
                SELECT user_id, COUNT(DISTINCT service_id) AS nb_services
                FROM filtered_subs
                GROUP BY user_id
            ),
            user_revenue AS (
                SELECT
                    fs.user_id,
                    CASE WHEN usc.nb_services >= 2 THEN 'multi' ELSE 'mono' END AS segment,
                    COALESCE(SUM(st.price) FILTER (WHERE be.status = 'SUCCESS'), 0) AS revenue
                FROM filtered_subs fs
                JOIN user_service_count usc ON usc.user_id = fs.user_id
                LEFT JOIN billing_events be ON be.subscription_id = fs.id
                LEFT JOIN services sv ON sv.id = fs.service_id
                LEFT JOIN service_types st ON st.id = sv.service_type_id
                GROUP BY fs.user_id, segment
            )
            SELECT
                segment,
                COUNT(DISTINCT user_id) AS user_count,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM user_revenue
            GROUP BY segment
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
WITH filtered_subs AS (
                SELECT DISTINCT sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
),
            service_user_counts AS (
                SELECT service_id, COUNT(DISTINCT user_id) AS total_users
                FROM filtered_subs
                GROUP BY service_id
            ),
            pairs AS (
                SELECT
                    us1.service_id AS sid_a,
                    us2.service_id AS sid_b,
                    COUNT(DISTINCT us1.user_id) AS co_count
                FROM filtered_subs us1
                JOIN filtered_subs us2
                  ON us1.user_id = us2.user_id
                  AND us1.service_id <> us2.service_id
                GROUP BY us1.service_id, us2.service_id
            )
            SELECT
                s1.name AS service_a,
                s2.name AS service_b,
                p.co_count,
                ROUND(p.co_count * 100.0 / NULLIF(suc.total_users, 0), 1) AS rate
            FROM pairs p
            JOIN services s1 ON p.sid_a = s1.id
            JOIN services s2 ON p.sid_b = s2.id
            JOIN service_user_counts suc ON suc.service_id = p.sid_a
            ORDER BY p.co_count DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
SELECT COUNT(DISTINCT sub.user_id) AS cnt
            FROM subscriptions sub
            WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
SELECT
                s1.name AS from_service,
                s2.name AS to_service,
                COUNT(DISTINCT sub1.user_id) AS user_count
            FROM subscriptions sub1
            JOIN subscriptions sub2
              ON sub1.user_id = sub2.user_id
              AND sub2.subscription_start_date > sub1.subscription_start_date
              AND sub1.service_id <> sub2.service_id
            JOIN services s1 ON sub1.service_id = s1.id
            JOIN services s2 ON sub2.service_id = s2.id
            WHERE sub1.subscription_end_date IS NOT NULL
              AND sub2.subscription_start_date > sub1.subscription_end_date
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/cross_service.py
```sql
SELECT
                nb_services,
                COUNT(*) AS user_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
            FROM (
                SELECT sub.user_id, COUNT(DISTINCT sub.service_id) AS nb_services
                FROM subscriptions sub
                WHERE 1=1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
UPDATE services
            SET name = :name, service_type_id = CAST(:st_id AS uuid)
            WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
UPDATE campaigns
            SET name = :name,
                send_datetime = :send_datetime,
                target_size = :target_size,
                status = :status
            WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
UPDATE services SET is_active = false WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
DELETE FROM campaigns WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT
              sv.id,
              sv.name,
              st.name AS service_type_name,
              st.billing_frequency_days,
              st.price,
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = sv.id) AS total_subscriptions,
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = sv.id AND s.status = 'active') AS active_subscriptions,
              (SELECT COUNT(*) FROM campaigns c WHERE c.service_id = sv.id) AS total_campaigns,
              sv.created_at
            FROM services sv
            JOIN service_types st ON st.id = sv.service_type_id
            WHERE sv.is_active = true
            ORDER BY sv.name ASC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM services WHERE LOWER(name) = LOWER(:name)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM service_types WHERE name = :n
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
INSERT INTO service_types (id, name, billing_frequency_days, price, trial_duration_days, is_active)
            VALUES (CAST(:id AS uuid), :name, :days, :price, 3, true)
            RETURNING id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
INSERT INTO services (id, name, description, service_type_id, is_active)
            VALUES (CAST(:id AS uuid), :name, NULL, CAST(:st_id AS uuid), true)
            RETURNING id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT created_at FROM services WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT sv.id, sv.name, sv.service_type_id, st.billing_frequency_days, st.price
            FROM services sv
            JOIN service_types st ON st.id = sv.service_type_id
            WHERE sv.id = CAST(:id AS uuid) AND sv.is_active = true
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = CAST(:id AS uuid)) AS total_subscriptions,
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = CAST(:id AS uuid) AND s.status = 'active') AS active_subscriptions,
              (SELECT COUNT(*) FROM campaigns c WHERE c.service_id = CAST(:id AS uuid)) AS total_campaigns,
              (SELECT created_at FROM services WHERE id = CAST(:id AS uuid)) AS created_at
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT COUNT(*) AS c FROM subscriptions WHERE service_id = CAST(:id AS uuid) AND status = 'active'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
Cannot delete: service has
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT
              c.id,
              c.name,
              c.service_id,
              sv.name AS service_name,
              c.send_datetime,
              c.target_size,
              COUNT(s.id) AS total_subs
            FROM campaigns c
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            LEFT JOIN services sv ON sv.id = c.service_id
            GROUP BY c.id, c.name, c.service_id, sv.name, c.send_datetime, c.target_size
            ORDER BY c.send_datetime DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM campaigns WHERE LOWER(name) = LOWER(:name)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM services WHERE id = CAST(:id AS uuid) AND is_active = true
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
INSERT INTO campaigns (
              id, name, description, service_id, send_datetime, target_size, cost, campaign_type, status
            )
            VALUES (
              CAST(:id AS uuid), :name, NULL, CAST(:service_id AS uuid), :send_datetime, :target_size, NULL, :campaign_type, :status
            )
            RETURNING id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT id, name, service_id, send_datetime, target_size
            FROM campaigns
            WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT COUNT(*) AS c FROM subscriptions WHERE campaign_id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
Cannot delete: campaign has
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM services WHERE LOWER(name) = LOWER(:name) AND id <> CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM service_types WHERE name = :n
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
INSERT INTO service_types (id, name, billing_frequency_days, price, trial_duration_days, is_active)
                VALUES (CAST(:id AS uuid), :name, :days, :price, 3, true)
                RETURNING id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT name FROM services WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT 1 FROM campaigns WHERE LOWER(name) = LOWER(:name) AND id <> CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT COUNT(*) FROM subscriptions WHERE campaign_id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/management.py
```sql
SELECT name FROM services WHERE id = CAST(:id AS uuid)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/platform_user.py
```sql
List all platform users with optional filters and pagination.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/platform_user.py
```sql
Update name, email and/or role of a platform user.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/platform_user.py
```sql
Permanently delete a platform user.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/service.py
```sql
SELECT id, name
        FROM services
        ORDER BY name ASC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            s.name AS service_name,
            COUNT(*) FILTER (WHERE sub.status = 'trial')                         AS trials,
            COUNT(*) FILTER (WHERE sub.status = 'active')                        AS converted,
            COUNT(*) FILTER (WHERE sub.status IN ('cancelled', 'expired'))       AS dropped,
            ROUND(
                COUNT(*) FILTER (WHERE sub.status = 'active') * 100.0
                / NULLIF(COUNT(*), 0),
                1
            ) AS conversion_rate_pct
        FROM subscriptions sub
        JOIN services s ON s.id = sub.service_id
        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        GROUP BY s.name
        ORDER BY trials DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            COUNT(*)                                         AS total_all,
            COUNT(*) FILTER (WHERE status = 'active')       AS active_subs,
            COUNT(*) FILTER (WHERE status = 'cancelled')    AS cancelled_subs,
            COUNT(*) FILTER (WHERE status = 'trial')        AS trial_subs
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            COUNT(*) FILTER (
                WHERE status IN ('cancelled', 'expired')
                  AND GREATEST(0, EXTRACT(DAY FROM
                                                COALESCE(subscription_end_date, CAST(:anchor_dt AS timestamp)) - subscription_start_date
                      )) <= 3
            ) AS dropoff_by_day3,
            COUNT(*) AS total_count
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                    AND subscription_start_date <= CAST(:anchor_dt AS timestamp)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
WITH trial_users AS (
            SELECT DISTINCT user_id
            FROM subscriptions
            WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
              AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
),
        has_active AS (
            SELECT DISTINCT user_id
            FROM subscriptions
            WHERE status = 'active'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
)
        SELECT
          COUNT(*) AS trial_only_users,
          COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM trial_users), 0) AS trial_only_rate
        FROM trial_users tu
        LEFT JOIN has_active ha ON ha.user_id = tu.user_id
        WHERE ha.user_id IS NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            DATE(subscription_start_date)                                    AS date,
            COUNT(*) FILTER (WHERE status = 'trial')                         AS trials_started,
            COUNT(*) FILTER (WHERE status = 'active')                        AS converted,
            COUNT(*) FILTER (WHERE status IN ('cancelled', 'expired'))       AS dropped
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            u.id,
            u.phone_number,
            s.name                                                AS service_name,
            sub.subscription_start_date                          AS trial_start,
            sub.subscription_end_date                            AS trial_end,
            sub.status,

            -- ✅ GREATEST(0, ...) évite les durées négatives
            GREATEST(0,
                ROUND(
                    EXTRACT(DAY FROM
                        COALESCE(sub.subscription_end_date, CAST(:anchor_dt AS timestamp)) - sub.subscription_start_date
                    )::numeric,
                1
                )
            )                                                     AS duration_days,

            -- Converti = status active
            CASE WHEN sub.status = 'active' THEN true ELSE false END AS converted

        FROM subscriptions sub
        JOIN users    u ON u.id  = sub.user_id
        JOIN services s ON s.id  = sub.service_id

        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                    AND sub.subscription_start_date <= CAST(:anchor_dt AS timestamp)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
WITH base AS (
            SELECT
                GREATEST(
                    0,
                                        EXTRACT(DAY FROM COALESCE(subscription_end_date, CAST(:anchor_dt AS timestamp)) - subscription_start_date)
                )::int AS duration_days
            FROM subscriptions
            WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
              AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                            AND subscription_start_date <= CAST(:anchor_dt AS timestamp)
              AND status IN ('cancelled', 'expired')
              AND subscription_end_date IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
)
        SELECT
            COUNT(*) FILTER (WHERE duration_days <= 1)                      AS day1,
            COUNT(*) FILTER (WHERE duration_days > 1 AND duration_days <= 2) AS day2,
            COUNT(*) FILTER (WHERE duration_days > 2 AND duration_days <= 3) AS day3
        FROM base
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY')               AS voluntary,
            COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL')               AS technical,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct
        FROM unsubscriptions u
        WHERE u.unsubscription_datetime >= CAST(:start_dt AS timestamp)
          AND u.unsubscription_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT COUNT(*) AS total
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT
            ROUND(
                AVG(
                    GREATEST(
                        0,
                        EXTRACT(DAY FROM
                            COALESCE(subscription_end_date, CAST(:anchor_dt AS timestamp)) - subscription_start_date
                        )
                    )
                )::numeric,
                1
            ) AS avg_days
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                    AND subscription_start_date <= CAST(:anchor_dt AS timestamp)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/trialAnalytics.py
```sql
SELECT COUNT(*) AS total
        FROM subscriptions sub
        JOIN users    u ON u.id = sub.user_id
        JOIN services s ON s.id = sub.service_id
        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                    AND sub.subscription_start_date <= CAST(:anchor_dt AS timestamp)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
AND EXISTS (
            SELECT 1 FROM subscriptions sub
            WHERE sub.user_id    = u.id
              AND sub.service_id = CAST(:service_id AS uuid)
        )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
AND EXISTS (
            SELECT 1
            FROM subscriptions sub
            WHERE sub.user_id = u.id
              AND sub.service_id = CAST(:service_id AS uuid)
        )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT
            CASE
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) BETWEEN 1 AND 7
                    THEN '1-7 days'
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) BETWEEN 8 AND 14
                    THEN '8-14 days'
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) BETWEEN 15 AND 30
                    THEN '15-30 days'
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) > 30
                    THEN '30+ days'
                ELSE 'Unknown'
            END AS bucket,
            COUNT(*) AS count
        FROM users
        WHERE last_activity_at IS NOT NULL
          AND status NOT IN ('churned', 'cancelled')
        GROUP BY bucket
        ORDER BY MIN(EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at))
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT
            COUNT(DISTINCT user_id) FILTER (
                WHERE DATE(activity_datetime) = :end_dt
            ) AS dau_today,

            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '7 days'
                  AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            ) AS wau_current_week,

            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= CAST(:start_dt AS timestamp)
                  AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            ) AS mau_current_month

        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp)
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT COUNT(DISTINCT u.id) AS inactive_count
        FROM users u
        LEFT JOIN user_activities ua
            ON  ua.user_id = u.id
            AND ua.activity_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '7 days'
        WHERE ua.user_id IS NULL
          AND u.status NOT IN ('churned', 'cancelled')
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT ROUND(AVG(
            EXTRACT(DAY FROM
                COALESCE(subscription_end_date, CAST(:subscription_anchor_dt AS timestamp)) - subscription_start_date
            )
        ), 0) AS avg_lifetime_days
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND status IN ('active', 'cancelled', 'expired')
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT
            DATE(activity_datetime) AS date,
            COUNT(DISTINCT user_id) AS dau
        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp)
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT
            DATE(activity_datetime) AS date,
            COUNT(DISTINCT user_id) AS rolling_count
        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp) - INTERVAL '30 days'
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT
            TRIM(TO_CHAR(activity_datetime, 'Day')) AS day,
            EXTRACT(HOUR FROM activity_datetime)::int AS hour,
            COUNT(*) AS count
        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp)
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
WITH months AS (
            SELECT generate_series(
                date_trunc('month', CAST(:start_dt AS timestamp))::date,
                date_trunc('month', CAST(:end_dt AS timestamp))::date,
                interval '1 month'
            )::date AS month_start
        ),
        new_users AS (
            SELECT
                date_trunc('month', u.created_at)::date AS month_start,
                COUNT(DISTINCT u.id) AS new_count
            FROM users u
            WHERE u.created_at >= CAST(:start_dt AS timestamp)
              AND u.created_at <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
GROUP BY 1
        ),
        churned_users AS (
            SELECT
                date_trunc('month', un.unsubscription_datetime)::date AS month_start,
                COUNT(DISTINCT un.user_id) AS churn_count
            FROM unsubscriptions un
            WHERE un.unsubscription_datetime >= CAST(:start_dt AS timestamp)
              AND un.unsubscription_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
GROUP BY 1
        )
        SELECT
            m.month_start,
            COALESCE(nu.new_count, 0)   AS nouveaux,
            COALESCE(cu.churn_count, 0) AS churnes
        FROM months m
        LEFT JOIN new_users nu     ON nu.month_start = m.month_start
        LEFT JOIN churned_users cu ON cu.month_start = m.month_start
        ORDER BY m.month_start ASC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/userActivity.py
```sql
SELECT
            srv.name AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')  AS active_users,
            COUNT(*) FILTER (WHERE s.status = 'trial')   AS trial_users,
            COUNT(*) FILTER (
                WHERE u.last_activity_at < CAST(:end_dt AS timestamp) - INTERVAL '7 days'
                   OR u.last_activity_at IS NULL
            ) AS inactive_7d,
            COUNT(*) FILTER (
                WHERE u.last_activity_at < CAST(:end_dt AS timestamp) - INTERVAL '30 days'
                   OR u.last_activity_at IS NULL
            ) AS inactive_30d,
            ROUND(AVG(
                EXTRACT(DAY FROM
                    COALESCE(s.subscription_end_date, CAST(:subscription_anchor_dt AS timestamp)) - s.subscription_start_date)
            ), 0) AS avg_lifetime_days,
            ROUND(
                COUNT(DISTINCT ua_today.user_id) * 100.0
                / NULLIF(COUNT(DISTINCT s.user_id), 0)
            , 1) AS stickiness_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        JOIN users u ON u.id = s.user_id
        LEFT JOIN user_activities ua_today
            ON  ua_today.user_id = s.user_id
            AND DATE(ua_today.activity_datetime) = :end_dt
        WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND s.subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/users.py
```sql
Get trial users with their trial details
    Status filter: 'active', 'converted', 'dropped'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/users.py
```sql
EXISTS (
                SELECT 1
                FROM subscriptions sub
                WHERE sub.user_id = u.id
                  AND sub.service_id = CAST(:service_id AS uuid)
            )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/users.py
```sql
SELECT
            u.id,
            u.phone_number,
            u.status,
            u.created_at,
            u.last_activity_at,

            COALESCE(
                ARRAY_AGG(DISTINCT srv.name)
                FILTER (WHERE srv.name IS NOT NULL),
                ARRAY[]::text[]
            ) AS service_names,

            COALESCE(
                ARRAY_AGG(DISTINCT s.service_id::text)
                FILTER (WHERE s.service_id IS NOT NULL),
                ARRAY[]::text[]
            ) AS service_ids,

            (
                SELECT c.name
                FROM subscriptions sub
                JOIN campaigns c ON c.id = sub.campaign_id
                WHERE sub.user_id = u.id
                  AND c.status = 'sent'
                ORDER BY c.send_datetime DESC
                LIMIT 1
            ) AS campaign_name,

            COUNT(*) FILTER (WHERE s.id IS NOT NULL)    AS total_subscriptions,
            COUNT(*) FILTER (WHERE s.status = 'active') AS active_subscriptions

        FROM users u
        LEFT JOIN subscriptions s ON s.user_id = u.id
        LEFT JOIN services srv    ON srv.id = s.service_id

        WHERE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/users.py
```sql
SELECT COUNT(DISTINCT u.id) AS total
        FROM users u
        LEFT JOIN subscriptions s ON s.user_id = u.id
        WHERE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/users.py
```sql
SELECT
            u.id,
            u.phone_number,
            sub.id AS subscription_id,
            srv.name AS service_name,
            sub.subscription_start_date AS trial_start_date,
            sub.subscription_end_date AS trial_end_date,
            sub.status,
            EXTRACT(DAY FROM COALESCE(sub.subscription_end_date, NOW()) - sub.subscription_start_date)::integer AS trial_duration_days,
            CASE
                WHEN sub.status = 'trial' THEN 'active'
                WHEN sub.status = 'active' THEN 'converted'
                WHEN sub.status IN ('cancelled', 'expired') THEN 'dropped'
                ELSE 'unknown'
            END AS display_status

        FROM subscriptions sub
        JOIN users u ON u.id = sub.user_id
        JOIN services srv ON srv.id = sub.service_id

        WHERE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/routers/users.py
```sql
SELECT COUNT(DISTINCT sub.id) AS total
        FROM subscriptions sub
        JOIN users u ON u.id = sub.user_id
        JOIN services srv ON srv.id = sub.service_id
        WHERE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/campaign_service.py
```sql
Campaign Impact Service Layer
Business logic for campaign analytics with caching
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/campaign_service.py
```sql
Store value in cache with timestamp
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/campaign_service.py
```sql
Get complete campaign impact dashboard in a single payload
    Combines overview, type breakdown, monthly trend, and top campaigns
    
    Args:
        db: Database session
        filters: Optional dict with start_date, end_date, service_id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/campaign_service.py
```sql
Get paginated campaign list with impact metrics and filtering
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/platform_user_service.py
```sql
Raise 403 if the admin tries to modify/delete themselves.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/platform_user_service.py
```sql
Return paginated list of platform users with optional filters.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/platform_user_service.py
```sql
Update name, email and/or role of a platform user.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/platform_user_service.py
```sql
Permanently delete a platform user — admin cannot delete themselves.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/services/platform_user_service.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/app/utils/temporal.py
```sql
SELECT
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/ml_models/churn_predictor.py
```sql
Build a subscription-level dataset with features + churned label.
        Granularity: (user_id, service_id, subscription_id)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/ml_models/churn_predictor.py
```sql
WITH base AS (
          SELECT
            s.id AS subscription_id,
            s.user_id,
            s.service_id,
            s.subscription_start_date,
            s.subscription_end_date,
            s.status,
            COALESCE(s.subscription_end_date, NOW()) AS ref_time,
            st.billing_frequency_days,
            st.trial_duration_days,
            COALESCE(co.retention_d7, 0)::float AS avg_retention_d7,
            u.unsubscription_datetime,
            u.churn_type,
            u.churn_reason,
            u.days_since_subscription,
            CASE
              WHEN s.subscription_end_date IS NOT NULL THEN 1
              ELSE 0
            END AS churned
          FROM subscriptions s
          JOIN services sv ON sv.id = s.service_id
          JOIN service_types st ON st.id = sv.service_type_id
          LEFT JOIN cohorts co
            ON co.service_id = s.service_id
           AND co.cohort_date = date_trunc('month', s.subscription_start_date)::date
          LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
          WHERE s.status IN ('trial', 'active', 'cancelled', 'expired')
        )
        SELECT
          b.user_id,
          b.service_id,
          b.subscription_id,
          -- days_since_last_activity
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - last_activity.last_activity_datetime))::int,
            999
          ) AS days_since_last_activity,
          COALESCE(act7.nb_activities_7d, 0)::int AS nb_activities_7d,
          COALESCE(act30.nb_activities_30d, 0)::int AS nb_activities_30d,
          COALESCE(bfail30.billing_failures_30d, 0)::int AS billing_failures_30d,
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - first_charge.first_charge_datetime))::int,
            999
          ) AS days_since_first_charge,
          -- is_trial_churn: churn during trial
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
             AND COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
                 <= b.trial_duration_days
            THEN 1 ELSE 0
          END AS is_trial_churn,
          COALESCE(b.avg_retention_d7, 0)::float AS avg_retention_d7,
          b.billing_frequency_days::float AS service_billing_frequency,
          -- days_to_first_unsub: time-to-churn for churned users, else a large sentinel
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
            THEN COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
            ELSE 999
          END AS days_to_first_unsub,
          COALESCE(b.churned, 0)::int AS churned
        FROM base b
        LEFT JOIN LATERAL (
          SELECT MAX(ua.activity_datetime) AS last_activity_datetime
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime <= b.ref_time
        ) last_activity ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_7d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '7 days'
            AND ua.activity_datetime <= b.ref_time
        ) act7 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_30d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '30 days'
            AND ua.activity_datetime <= b.ref_time
        ) act30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS billing_failures_30d
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.status = 'FAILED'
            AND be.event_datetime >= b.ref_time - INTERVAL '30 days'
            AND be.event_datetime <= b.ref_time
        ) bfail30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT MIN(be.event_datetime) AS first_charge_datetime
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.is_first_charge = TRUE
            AND be.status = 'SUCCESS'
            AND be.event_datetime <= b.ref_time
        ) first_charge ON TRUE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/ml_models/churn_predictor.py
```sql
WITH base AS (
          SELECT
            s.id AS subscription_id,
            s.user_id,
            s.service_id,
            s.subscription_start_date,
            s.subscription_end_date,
            s.status,
            COALESCE(s.subscription_end_date, NOW()) AS ref_time,
            st.billing_frequency_days,
            st.trial_duration_days,
            COALESCE(co.retention_d7, 0)::float AS avg_retention_d7,
            u.unsubscription_datetime,
            u.days_since_subscription,
            u.churn_type,
            u.churn_reason,
            us.phone_number,
            sv.name AS service_name
          FROM subscriptions s
          JOIN services sv ON sv.id = s.service_id
          JOIN service_types st ON st.id = sv.service_type_id
          JOIN users us ON us.id = s.user_id
          LEFT JOIN cohorts co
            ON co.service_id = s.service_id
           AND co.cohort_date = date_trunc('month', s.subscription_start_date)::date
          LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
          WHERE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/ml_models/churn_predictor.py
```sql
)
        SELECT
          b.user_id,
          b.service_id,
          b.subscription_id,
          b.phone_number,
          b.service_name,
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - last_activity.last_activity_datetime))::int,
            999
          ) AS days_since_last_activity,
          COALESCE(act7.nb_activities_7d, 0)::int AS nb_activities_7d,
          COALESCE(act30.nb_activities_30d, 0)::int AS nb_activities_30d,
          COALESCE(bfail30.billing_failures_30d, 0)::int AS billing_failures_30d,
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - first_charge.first_charge_datetime))::int,
            999
          ) AS days_since_first_charge,
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
             AND COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
                 <= b.trial_duration_days
            THEN 1 ELSE 0
          END AS is_trial_churn,
          COALESCE(b.avg_retention_d7, 0)::float AS avg_retention_d7,
          b.billing_frequency_days::float AS service_billing_frequency
          ,
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
            THEN COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
            ELSE 999
          END AS days_to_first_unsub
        FROM base b
        LEFT JOIN LATERAL (
          SELECT MAX(ua.activity_datetime) AS last_activity_datetime
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime <= b.ref_time
        ) last_activity ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_7d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '7 days'
            AND ua.activity_datetime <= b.ref_time
        ) act7 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_30d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '30 days'
            AND ua.activity_datetime <= b.ref_time
        ) act30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS billing_failures_30d
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.status = 'FAILED'
            AND be.event_datetime >= b.ref_time - INTERVAL '30 days'
            AND be.event_datetime <= b.ref_time
        ) bfail30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT MIN(be.event_datetime) AS first_charge_datetime
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.is_first_charge = TRUE
            AND be.status = 'SUCCESS'
            AND be.event_datetime <= b.ref_time
        ) first_charge ON TRUE
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
timestamp with time zone
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
WITH first_sub AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_sub_date
            FROM subscriptions
            WHERE subscription_start_date IS NOT NULL
            ORDER BY user_id, service_id, subscription_start_date ASC
        ),
        cohort_base AS (
            SELECT
                date_trunc('month', first_sub_date)::date AS cohort_date,
                service_id,
                COUNT(*) AS total_users
            FROM first_sub
            GROUP BY cohort_date, service_id
        ),
        retention_calc AS (
            SELECT
                date_trunc('month', fp.first_sub_date)::date AS cohort_date,
                fp.service_id,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                      AND s2.service_id = fp.service_id
                      AND s2.subscription_start_date
                          <= fp.first_sub_date + INTERVAL '7 days'
                      AND COALESCE(s2.subscription_end_date::timestamp,
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
)
                          >= fp.first_sub_date + INTERVAL '7 days'
                )) AS active_d7,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                      AND s2.service_id = fp.service_id
                      AND s2.subscription_start_date
                          <= fp.first_sub_date + INTERVAL '14 days'
                      AND COALESCE(s2.subscription_end_date::timestamp,
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
)
                          >= fp.first_sub_date + INTERVAL '14 days'
                )) AS active_d14,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                      AND s2.service_id = fp.service_id
                      AND s2.subscription_start_date
                          <= fp.first_sub_date + INTERVAL '30 days'
                      AND COALESCE(s2.subscription_end_date::timestamp,
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
)
                          >= fp.first_sub_date + INTERVAL '30 days'
                )) AS active_d30
            FROM first_sub fp
            GROUP BY cohort_date, fp.service_id
        ),
        retention_rates AS (
            SELECT
                cb.cohort_date,
                cb.service_id,
                cb.total_users,
                ROUND(100.0 * COALESCE(rc.active_d7,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d7,
                ROUND(100.0 * COALESCE(rc.active_d14,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d14,
                ROUND(100.0 * COALESCE(rc.active_d30,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d30
            FROM cohort_base cb
            LEFT JOIN retention_calc rc
              ON rc.cohort_date = cb.cohort_date
             AND rc.service_id  = cb.service_id
        )
        INSERT INTO cohorts (
            id, cohort_date, service_id,
            total_users, retention_d7, retention_d14, retention_d30,
            calculated_at
        )
        SELECT
            gen_random_uuid(),
            cohort_date, service_id,
            total_users, retention_d7, retention_d14, retention_d30,
            NOW()
        FROM retention_rates
        ON CONFLICT (cohort_date, service_id)
        DO UPDATE SET
            total_users    = EXCLUDED.total_users,
            retention_d7   = EXCLUDED.retention_d7,
            retention_d14  = EXCLUDED.retention_d14,
            retention_d30  = EXCLUDED.retention_d30,
            calculated_at  = NOW()
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
SELECT status, COUNT(*) as cnt
            FROM subscriptions
            GROUP BY status
            ORDER BY cnt DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
SELECT
                COUNT(*)                    AS total_subscriptions,
                COUNT(DISTINCT user_id)     AS unique_users,
                COUNT(DISTINCT service_id)  AS unique_services,
                MIN(subscription_start_date) AS min_date,
                MAX(subscription_start_date) AS max_date
            FROM subscriptions
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'subscriptions'
              AND column_name = 'subscription_end_date'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
WITH first_sub AS (
                SELECT DISTINCT ON (user_id, service_id)
                    user_id,
                    service_id,
                    subscription_start_date AS first_sub_date
                FROM subscriptions
                WHERE subscription_start_date IS NOT NULL
                ORDER BY user_id, service_id, subscription_start_date ASC
            )
            SELECT
                date_trunc('month', first_sub_date)::date AS cohort_date,
                service_id,
                COUNT(*)                                   AS total_users
            FROM first_sub
            GROUP BY cohort_date, service_id
            ORDER BY cohort_date DESC, total_users DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
SELECT COUNT(*) FROM cohorts
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
SELECT cohort_date, service_id, total_users,
                   retention_d7, retention_d14, retention_d30
            FROM cohorts
            ORDER BY cohort_date DESC
            LIMIT 3
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
SELECT
                EXTRACT(epoch FROM (MAX(subscription_start_date)
                    - MIN(subscription_start_date))) / 86400 AS span_days
            FROM subscriptions
            WHERE subscription_start_date IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
WITH first_sub AS (
                SELECT DISTINCT ON (user_id, service_id)
                    user_id,
                    service_id,
                    subscription_start_date AS first_sub_date
                FROM subscriptions
                WHERE subscription_start_date IS NOT NULL
                ORDER BY user_id, service_id, subscription_start_date ASC
            ),
            cohort_base AS (
                SELECT
                    date_trunc('month', first_sub_date)::date AS cohort_date,
                    service_id,
                    COUNT(*) AS total_users
                FROM first_sub
                GROUP BY cohort_date, service_id
            ),
            retention_calc AS (
                SELECT
                    date_trunc('month', fp.first_sub_date)::date AS cohort_date,
                    fp.service_id,

                    -- D7: toujours abonné 7 jours après sa première sub
                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date
                              <= fp.first_sub_date + INTERVAL '7 days'
                          AND COALESCE(
                                s2.subscription_end_date::timestamp,
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
) >= fp.first_sub_date + INTERVAL '7 days'
                    )) AS active_d7,

                    -- D14
                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date
                              <= fp.first_sub_date + INTERVAL '14 days'
                          AND COALESCE(
                                s2.subscription_end_date::timestamp,
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
) >= fp.first_sub_date + INTERVAL '14 days'
                    )) AS active_d14,

                    -- D30
                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date
                              <= fp.first_sub_date + INTERVAL '30 days'
                          AND COALESCE(
                                s2.subscription_end_date::timestamp,
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/compute_cohorts.py
```sql
) >= fp.first_sub_date + INTERVAL '30 days'
                    )) AS active_d30

                FROM first_sub fp
                GROUP BY cohort_date, fp.service_id
            )
            SELECT
                cb.cohort_date,
                cb.service_id,
                cb.total_users,
                ROUND(100.0 * COALESCE(rc.active_d7,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d7,
                ROUND(100.0 * COALESCE(rc.active_d14,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d14,
                ROUND(100.0 * COALESCE(rc.active_d30,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d30
            FROM cohort_base cb
            LEFT JOIN retention_calc rc
              ON rc.cohort_date = cb.cohort_date
             AND rc.service_id  = cb.service_id
            ORDER BY cb.cohort_date DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT id, service_id
            FROM service_subscription_types
            WHERE service_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO users (id, phone_number, status, created_at)
            VALUES (:id, :phone_number, :status, :created_at)
            ON CONFLICT (phone_number)
            DO UPDATE SET
                status = EXCLUDED.status,
                created_at = LEAST(users.created_at, EXCLUDED.created_at)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO subscriptions (
                id, user_id, service_id, campaign_id,
                subscription_start_date, subscription_end_date, status
            ) VALUES (
                :id, :user_id, :service_id, NULL,
                :subscription_start_date, :subscription_end_date, :status
            )
            ON CONFLICT (id)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                subscription_start_date = EXCLUDED.subscription_start_date,
                subscription_end_date = EXCLUDED.subscription_end_date,
                status = EXCLUDED.status
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO unsubscriptions (
                id,
                subscription_id,
                user_id,
                service_id,
                unsubscription_datetime,
                churn_type,
                churn_reason,
                days_since_subscription,
                last_billing_event_id
            ) VALUES (
                :id,
                :subscription_id,
                :user_id,
                :service_id,
                :unsubscription_datetime,
                :churn_type,
                :churn_reason,
                :days_since_subscription,
                :last_billing_event_id
            )
            ON CONFLICT (subscription_id)
            DO UPDATE SET
                user_id                  = EXCLUDED.user_id,
                service_id               = EXCLUDED.service_id,
                unsubscription_datetime  = EXCLUDED.unsubscription_datetime,
                churn_type               = EXCLUDED.churn_type,
                churn_reason             = EXCLUDED.churn_reason,
                days_since_subscription  = EXCLUDED.days_since_subscription,
                last_billing_event_id    = EXCLUDED.last_billing_event_id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO user_activities (id, user_id, service_id, activity_datetime, activity_type, session_id)
            VALUES (:id, :user_id, :service_id, :activity_datetime, :activity_type, NULL)
            ON CONFLICT (id)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                activity_datetime = EXCLUDED.activity_datetime,
                activity_type = EXCLUDED.activity_type
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT id, amount, subscription_period_id
                FROM service_subscription_types
                ORDER BY id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, event_type, status, failure_reason, retry_count,
                    is_first_charge, amount
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :event_type, :status, :failure_reason, :retry_count,
                    :is_first_charge, :amount
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    event_type = EXCLUDED.event_type,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge,
                    amount = EXCLUDED.amount
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT subscription_id,
                       COUNT(*) FILTER (WHERE status = 'failed')        AS failed_count,
                       COUNT(*) FILTER (WHERE event_type = 'renewal')   AS renewal_count,
                       COUNT(*)                                            AS total_count
                FROM billing_events
                GROUP BY subscription_id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT subscription_id,
                       COUNT(*) FILTER (WHERE status = 'failed')  AS failed_count,
                       0                                             AS renewal_count,
                       COUNT(*)                                      AS total_count
                FROM billing_events
                GROUP BY subscription_id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO import_logs (
                        id, file_name, file_type, target_table, mode,
                        rows_inserted, rows_skipped, status, error_details
                    ) VALUES (
                        :id, :file_name, :file_type, :target_table, :mode,
                        :rows_inserted, :rows_skipped, :status, CAST(:error_details AS jsonb)
                    )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO service_types (
                        id, name, billing_frequency_days, price, trial_duration_days, is_active
                    ) VALUES (
                        :id, :name, :billing_frequency_days, :price, :trial_duration_days, :is_active
                    )
                    ON CONFLICT (name)
                    DO UPDATE SET
                        billing_frequency_days = EXCLUDED.billing_frequency_days,
                        price = EXCLUDED.price,
                        trial_duration_days = EXCLUDED.trial_duration_days,
                        is_active = EXCLUDED.is_active
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO services (id, name, description, service_type_id, is_active)
                    VALUES (:id, :name, :description, :service_type_id, :is_active)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        service_type_id = EXCLUDED.service_type_id,
                        is_active = EXCLUDED.is_active
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT phone_number, id FROM users WHERE phone_number IN :phones
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT id, user_id, service_id
            FROM subscriptions
            WHERE id IN :ids
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, event_type, status, failure_reason, retry_count,
                    is_first_charge
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :event_type, :status, :failure_reason, :retry_count,
                    :is_first_charge
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    event_type = EXCLUDED.event_type,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT id, billing_frequency_days FROM service_types
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, status, failure_reason, retry_count,
                    is_first_charge, amount
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :status, :failure_reason, :retry_count,
                    :is_first_charge, :amount
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge,
                    amount = EXCLUDED.amount
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, status, failure_reason, retry_count,
                    is_first_charge
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :status, :failure_reason, :retry_count,
                    :is_first_charge
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT MIN(
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT id FROM billing_events
                        WHERE subscription_id = :sid
                          AND event_datetime <= :dt
                        ORDER BY event_datetime DESC
                        LIMIT 1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT COUNT(*) FROM transaction_histories WHERE type = 4
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT subscription_start_date FROM subscriptions WHERE id = :sid
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT COUNT(*) FROM
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
```sql
SELECT COUNT(*) FROM
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
SELECT COUNT(*) FROM subscribed_clients
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
SELECT
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
INSERT INTO subscriptions (
            id, user_id, service_id, campaign_id,
            subscription_start_date, subscription_end_date, status
        ) VALUES (
            :id, :user_id, :service_id, NULL,
            :subscription_start_date, :subscription_end_date, :status
        )
        ON CONFLICT (id)
        DO UPDATE SET
            user_id = EXCLUDED.user_id,
            service_id = EXCLUDED.service_id,
            subscription_start_date = EXCLUDED.subscription_start_date,
            subscription_end_date = EXCLUDED.subscription_end_date,
            status = EXCLUDED.status
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
SELECT phone_number, id FROM users WHERE phone_number IN :phones
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
SELECT id FROM services
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
SELECT id, service_id
                FROM service_subscription_types
                WHERE service_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/fix_services_mapping.py
```sql
SELECT id FROM services
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
Update subscriptions.campaign_id using date+service matching
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
UPDATE subscriptions s
            SET campaign_id = (
                SELECT c.id
                FROM campaigns c
                WHERE c.service_id = s.service_id
                  AND s.subscription_start_date BETWEEN
                      c.send_datetime - INTERVAL '1 day'
                      AND c.send_datetime + INTERVAL '7 days'
                ORDER BY ABS(
                    EXTRACT(EPOCH FROM (s.subscription_start_date - c.send_datetime))
                )
                LIMIT 1
            )
            WHERE s.campaign_id IS NULL
              AND s.subscription_start_date >= '2025-10-01'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
subscriptions with campaign_id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
subscriptions with campaign_id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
```sql
SELECT c.name, COUNT(s.id) as subs_count
            FROM campaigns c
            LEFT JOIN subscriptions s ON s.campaign_id = c.id
            GROUP BY c.id, c.name
            ORDER BY subs_count DESC
            LIMIT 10
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
INSERT INTO campaigns
        (id, name, description, service_id,
         send_datetime, target_size, cost, campaign_type, status)
    VALUES
        (:id, :name, :description, :service_id,
         :send_datetime, :target_size, :cost, :campaign_type, :status)
    ON CONFLICT (id) DO UPDATE SET
        name          = EXCLUDED.name,
        description   = EXCLUDED.description,
        service_id    = EXCLUDED.service_id,
        send_datetime = EXCLUDED.send_datetime,
        target_size   = EXCLUDED.target_size,
        cost          = EXCLUDED.cost,
        campaign_type = EXCLUDED.campaign_type,
        status        = EXCLUDED.status
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
Retourne seulement les clés sans préfixe _ pour l'INSERT.
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
WITH locked_subscriptions AS (
        SELECT
            s.id,
            s.service_id,
            s.subscription_start_date
        FROM subscriptions s
        WHERE s.campaign_id IS NULL
        LIMIT :batch_size
        FOR UPDATE OF s SKIP LOCKED
    ),
    candidates AS (
        SELECT
            ls.id                     AS sub_id,
            c.id                      AS campaign_id,
            ls.subscription_start_date AS sub_start,
            c.send_datetime           AS send_dt,
            ROW_NUMBER() OVER (
                PARTITION BY ls.id
                ORDER BY ABS(EXTRACT(EPOCH FROM (ls.subscription_start_date - c.send_datetime))), c.send_datetime DESC
            ) AS rn
        FROM locked_subscriptions ls
        JOIN campaigns c ON c.service_id = ls.service_id
    )
    UPDATE subscriptions s
    SET    campaign_id = c.campaign_id
    FROM   candidates c
    WHERE  s.id = c.sub_id
      AND  c.rn = 1
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
WITH organic_campaign AS (
        SELECT id
        FROM campaigns
        WHERE campaign_type = 'ORGANIC'
        ORDER BY send_datetime DESC
        LIMIT 1
    ),
    locked_subscriptions AS (
        SELECT s.id
        FROM subscriptions s
        WHERE s.campaign_id IS NULL
        LIMIT :batch_size
        FOR UPDATE OF s SKIP LOCKED
    )
    UPDATE subscriptions s
    SET campaign_id = oc.id
    FROM organic_campaign oc, locked_subscriptions ls
    WHERE s.id = ls.id
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
DRY RUN insert
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
Pre-insert clean
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
Pre-insert clean fallback
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
UPDATE subscriptions SET campaign_id = NULL WHERE campaign_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
DELETE FROM campaigns
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
SELECT MAX(event_datetime) FROM billing_events
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
SELECT id, name FROM services WHERE is_active = TRUE ORDER BY name
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
UPDATE subscriptions SET campaign_id = NULL WHERE campaign_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
delete
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
SELECT c.name, c.campaign_type, c.status,
                   COUNT(s.id) AS sub_count,
                   c.send_datetime::date AS send_date
            FROM   campaigns c
            LEFT   JOIN subscriptions s ON s.campaign_id = c.id
            GROUP  BY c.id, c.name, c.campaign_type, c.status, c.send_datetime
            ORDER  BY sub_count DESC
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
SELECT COUNT(*) FROM subscriptions
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
UPDATE subscriptions SET campaign_id = NULL WHERE campaign_id IS NOT NULL
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/etl/seed_campaigns.py
```sql
DELETE FROM campaigns
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
WITH be AS (
            SELECT user_id, MAX(event_datetime) AS last_be
            FROM billing_events
            GROUP BY user_id
        ),
        sb AS (
            SELECT user_id, MAX(subscription_start_date) AS last_sub
            FROM subscriptions
            GROUP BY user_id
        )
        SELECT COUNT(*)
        FROM users u
        LEFT JOIN be ON be.user_id = u.id
        LEFT JOIN sb ON sb.user_id = u.id
        WHERE u.status = 'active'
          AND (
                u.last_activity_at IS NULL
             OR u.last_activity_at < COALESCE(be.last_be, sb.last_sub, NOW() - INTERVAL '30 days')
          )
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
WITH be AS (
            SELECT user_id, MAX(event_datetime) AS last_be
            FROM billing_events
            GROUP BY user_id
        ),
        sb AS (
            SELECT user_id, MAX(subscription_start_date) AS last_sub
            FROM subscriptions
            GROUP BY user_id
        ),
        src AS (
            SELECT
                u.id AS user_id,
                LEAST(
                    NOW(),
                    COALESCE(
                        be.last_be,
                        sb.last_sub + ((FLOOR(random() * 20) + 1)::text || ' days')::interval +
                                      ((FLOOR(random() * 18) + 6)::text || ' hours')::interval,
                        NOW() - INTERVAL '15 days'
                    )
                ) AS new_last_activity
            FROM users u
            LEFT JOIN be ON be.user_id = u.id
            LEFT JOIN sb ON sb.user_id = u.id
            WHERE u.status = 'active'
        )
        UPDATE users u
        SET last_activity_at = src.new_last_activity
        FROM src
        WHERE u.id = src.user_id
          AND (u.last_activity_at IS NULL OR u.last_activity_at <> src.new_last_activity)
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
WITH first_paid AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_paid_date
            FROM subscriptions
            WHERE status IN ('active', 'cancelled', 'expired')
            ORDER BY user_id, service_id, subscription_start_date ASC
        )
        SELECT COUNT(*)
        FROM (
            SELECT date_trunc('month', first_paid_date)::date AS cohort_date, service_id
            FROM first_paid
            GROUP BY 1, 2
        ) q
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
WITH first_paid AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_paid_date
            FROM subscriptions
            WHERE status IN ('active', 'cancelled', 'expired')
            ORDER BY user_id, service_id, subscription_start_date ASC
        ),
        cohort_base AS (
            SELECT
                date_trunc('month', fp.first_paid_date)::date AS cohort_date,
                fp.service_id,
                COUNT(*) AS total_users
            FROM first_paid fp
            GROUP BY 1, 2
        ),
        retention_calc AS (
            SELECT
                date_trunc('month', fp.first_paid_date)::date AS cohort_date,
                fp.service_id,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1
                        FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '7 days'
                          AND COALESCE(s2.subscription_end_date, 'infinity'::timestamp) >= fp.first_paid_date + INTERVAL '7 days'
                    )
                ) AS active_d7,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1
                        FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '14 days'
                          AND COALESCE(s2.subscription_end_date, 'infinity'::timestamp) >= fp.first_paid_date + INTERVAL '14 days'
                    )
                ) AS active_d14,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1
                        FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '30 days'
                          AND COALESCE(s2.subscription_end_date, 'infinity'::timestamp) >= fp.first_paid_date + INTERVAL '30 days'
                    )
                ) AS active_d30
            FROM first_paid fp
            GROUP BY 1, 2
        )
        INSERT INTO cohorts (
            id, cohort_date, service_id, total_users,
            retention_d7, retention_d14, retention_d30, calculated_at
        )
        SELECT
            gen_random_uuid(),
            cb.cohort_date,
            cb.service_id,
            cb.total_users,
            ROUND(100.0 * COALESCE(rc.active_d7, 0) / NULLIF(cb.total_users, 0), 2),
            ROUND(100.0 * COALESCE(rc.active_d14, 0) / NULLIF(cb.total_users, 0), 2),
            ROUND(100.0 * COALESCE(rc.active_d30, 0) / NULLIF(cb.total_users, 0), 2),
            NOW()
        FROM cohort_base cb
        LEFT JOIN retention_calc rc
            ON rc.cohort_date = cb.cohort_date
           AND rc.service_id = cb.service_id
        ON CONFLICT (cohort_date, service_id) DO NOTHING
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
INSERT INTO campaigns (
                id, name, description, service_id, send_datetime,
                target_size, cost, campaign_type, status, created_at
            ) VALUES (
                :id, :name, :description, :service_id, :send_datetime,
                :target_size, :cost, :campaign_type, :status, :created_at
            )
            ON CONFLICT (id) DO NOTHING
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
INSERT INTO user_activities (
                id, user_id, service_id, activity_datetime, activity_type, session_id
            ) VALUES (
                :id, :user_id, :service_id, :activity_datetime, :activity_type, :session_id
            )
            ON CONFLICT (id) DO NOTHING
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT
                s.id AS subscription_id,
                s.user_id,
                s.service_id,
                s.subscription_start_date,
                COALESCE(s.subscription_end_date, s.subscription_start_date + INTERVAL '3 days') AS unsub_dt,
                s.status,
                (
                    SELECT be.id
                    FROM billing_events be
                    WHERE be.subscription_id = s.id
                    ORDER BY be.event_datetime DESC
                    LIMIT 1
                ) AS last_billing_event_id
            FROM subscriptions s
            WHERE s.status IN ('cancelled', 'expired')
            ORDER BY s.subscription_start_date
            LIMIT :limit OFFSET :offset
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
INSERT INTO unsubscriptions (
                id, subscription_id, user_id, service_id, unsubscription_datetime,
                churn_type, churn_reason, days_since_subscription, last_billing_event_id
            ) VALUES (
                :id, :subscription_id, :user_id, :service_id, :unsubscription_datetime,
                :churn_type, :churn_reason, :days_since_subscription, :last_billing_event_id
            )
            ON CONFLICT (subscription_id) DO NOTHING
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
INSERT INTO sms_events (
                id, user_id, campaign_id, service_id, event_datetime,
                event_type, message_content, direction, delivery_status
            ) VALUES (
                :id, :user_id, :campaign_id, :service_id, :event_datetime,
                :event_type, :message_content, :direction, :delivery_status
            )
            ON CONFLICT (id) DO NOTHING
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT id, name FROM services ORDER BY name
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT u.id AS user_id, s.service_id
                FROM users u
                JOIN LATERAL (
                    SELECT service_id
                    FROM subscriptions su
                    WHERE su.user_id = u.id
                    ORDER BY su.subscription_start_date DESC
                    LIMIT 1
                ) s ON TRUE
                WHERE u.status = 'active'
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT u.id AS user_id, s.service_id
                FROM users u
                JOIN LATERAL (
                    SELECT service_id
                    FROM subscriptions su
                    WHERE su.user_id = u.id
                    ORDER BY su.subscription_start_date DESC
                    LIMIT 1
                ) s ON TRUE
                WHERE u.status = 'inactive'
                ORDER BY random()
                LIMIT 300000
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT DISTINCT ON (u.id)
                    u.id AS user_id,
                    s.service_id
                FROM users u
                JOIN subscriptions s ON s.user_id = u.id
                ORDER BY u.id, s.subscription_start_date DESC
                LIMIT 400000
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT COUNT(*)
                    FROM subscriptions s
                    WHERE s.status IN ('cancelled', 'expired')
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/seeder/seed_missing_data.py
```sql
SELECT id FROM campaigns ORDER BY send_datetime DESC LIMIT 200
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/verify_data.py
```sql
SELECT COUNT(*)
            FROM billing_events
            WHERE DATE(event_datetime) >= :start_date
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/verify_data.py
```sql
ANALYTICS billing_events with
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/verify_data.py
```sql
SELECT MIN(created_at) AS min_d, MAX(created_at) AS max_d, COUNT(*) AS total
                FROM transaction_histories
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

### Inline SQL in: user-analytics-backend/scripts/verify_data.py
```sql
SELECT COUNT(*) FROM
```
- KPI/data computed: Context-dependent business metric/query
- Input parameters: Function args / bound params around execution
- Output columns/shape: SQL SELECT projection or DML rowcount

## 4. SQLAlchemy Models

### Settings (user-analytics-backend/app/core/config.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### BillingEvent (user-analytics-backend/app/models/billing_events.py)
- Table name: billing_events
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### Campaign (user-analytics-backend/app/models/campaigns.py)
- Table name: campaigns
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### Cohort (user-analytics-backend/app/models/cohorts.py)
- Table name: cohorts
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ImportLog (user-analytics-backend/app/models/import_logs.py)
- Table name: import_logs
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### PlatformUser (user-analytics-backend/app/models/platform_users.py)
- Table name: platform_users
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceType (user-analytics-backend/app/models/service_types.py)
- Table name: service_types
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### Service (user-analytics-backend/app/models/services.py)
- Table name: services
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SmsEvent (user-analytics-backend/app/models/sms_events.py)
- Table name: sms_events
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### Subscription (user-analytics-backend/app/models/subscriptions.py)
- Table name: subscriptions
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### Unsubscription (user-analytics-backend/app/models/unsubscriptions.py)
- Table name: unsubscriptions
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserActivity (user-analytics-backend/app/models/user_activities.py)
- Table name: user_activities
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### User (user-analytics-backend/app/models/users.py)
- Table name: users
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceCreateBody (user-analytics-backend/app/routers/management.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceUpdateBody (user-analytics-backend/app/routers/management.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CampaignCreateBody (user-analytics-backend/app/routers/management.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CampaignUpdateBody (user-analytics-backend/app/routers/management.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### RegisterRequest (user-analytics-backend/app/schemas/auth.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### LoginRequest (user-analytics-backend/app/schemas/auth.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### TokenResponse (user-analytics-backend/app/schemas/auth.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserResponse (user-analytics-backend/app/schemas/auth.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### BillingEventBase (user-analytics-backend/app/schemas/BillingEvent.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### BillingEventCreate (user-analytics-backend/app/schemas/BillingEvent.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### BillingEventUpdate (user-analytics-backend/app/schemas/BillingEvent.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### BillingEventRead (user-analytics-backend/app/schemas/BillingEvent.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CampaignBase (user-analytics-backend/app/schemas/Campaigns.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CampaignCreate (user-analytics-backend/app/schemas/Campaigns.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CampaignUpdate (user-analytics-backend/app/schemas/Campaigns.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CampaignRead (user-analytics-backend/app/schemas/Campaigns.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnKPIsResponse (user-analytics-backend/app/schemas/churn_analysis.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnCurvePoint (user-analytics-backend/app/schemas/churn_analysis.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### TimeToChurnBucketRow (user-analytics-backend/app/schemas/churn_analysis.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnReasonRow (user-analytics-backend/app/schemas/churn_analysis.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### RiskSegmentRow (user-analytics-backend/app/schemas/churn_analysis.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CohortBase (user-analytics-backend/app/schemas/Cohorts.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CohortCreate (user-analytics-backend/app/schemas/Cohorts.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CohortUpdate (user-analytics-backend/app/schemas/Cohorts.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### CohortRead (user-analytics-backend/app/schemas/Cohorts.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnTrainMetricsResponse (user-analytics-backend/app/schemas/ml_churn.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnRiskDistributionItem (user-analytics-backend/app/schemas/ml_churn.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnTopUserItem (user-analytics-backend/app/schemas/ml_churn.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ChurnScoresResponse (user-analytics-backend/app/schemas/ml_churn.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### LoginRequest (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### Token (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### TokenPayload (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### PlatformUserBase (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### PlatformUserCreate (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### PlatformUserUpdate (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### PlatformUserRead (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### PlatformUserListResponse (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UpdateStatusRequest (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UpdateRoleRequest (user-analytics-backend/app/schemas/platform_user_schemas.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceBase (user-analytics-backend/app/schemas/Services.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceCreate (user-analytics-backend/app/schemas/Services.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceUpdate (user-analytics-backend/app/schemas/Services.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceRead (user-analytics-backend/app/schemas/Services.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceTypeBase (user-analytics-backend/app/schemas/ServicesTypes.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceTypeCreate (user-analytics-backend/app/schemas/ServicesTypes.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceTypeUpdate (user-analytics-backend/app/schemas/ServicesTypes.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### ServiceTypeRead (user-analytics-backend/app/schemas/ServicesTypes.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SmsEventBase (user-analytics-backend/app/schemas/SmsEvents.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SmsEventCreate (user-analytics-backend/app/schemas/SmsEvents.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SmsEventUpdate (user-analytics-backend/app/schemas/SmsEvents.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SmsEventRead (user-analytics-backend/app/schemas/SmsEvents.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SubscriptionBase (user-analytics-backend/app/schemas/Subscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SubscriptionCreate (user-analytics-backend/app/schemas/Subscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SubscriptionUpdate (user-analytics-backend/app/schemas/Subscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SubscriptionRead (user-analytics-backend/app/schemas/Subscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UnsubscriptionBase (user-analytics-backend/app/schemas/Unsubscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UnsubscriptionCreate (user-analytics-backend/app/schemas/Unsubscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UnsubscriptionUpdate (user-analytics-backend/app/schemas/Unsubscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UnsubscriptionRead (user-analytics-backend/app/schemas/Unsubscriptions.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserActivityBase (user-analytics-backend/app/schemas/UserActivities.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserActivityCreate (user-analytics-backend/app/schemas/UserActivities.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserActivityRead (user-analytics-backend/app/schemas/UserActivities.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### SubscriptionItem (user-analytics-backend/app/schemas/users.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UnsubscriptionItem (user-analytics-backend/app/schemas/users.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserListItem (user-analytics-backend/app/schemas/users.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserListResponse (user-analytics-backend/app/schemas/users.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserDetailResponse (user-analytics-backend/app/schemas/users.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

### UserStatsResponse (user-analytics-backend/app/schemas/users.py)
- Table name: Unknown
- Database: analytics_db
- Columns:
  - None detected
- Relationships:
  - None detected

## 5. FastAPI Routes / Endpoints

### GET '/' (user-analytics-backend/app/main.py)
- Handler: root
- Request params: None
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/csv' (user-analytics-backend/app/routers/admin_import.py)
- Handler: stage_single_table_csv
- Request params: table: str, mode: ImportMode, file: UploadFile, db: Session, current_user: PlatformUser
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/csv/confirm' (user-analytics-backend/app/routers/admin_import.py)
- Handler: confirm_single_table_csv
- Request params: import_id: str, table: str, mode: ImportMode, force: bool, db: Session, current_user: PlatformUser
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/database' (user-analytics-backend/app/routers/admin_import.py)
- Handler: import_full_database_sql
- Request params: mode: ImportMode, file: UploadFile, db: Session, current_user: PlatformUser
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/history' (user-analytics-backend/app/routers/admin_import.py)
- Handler: import_history
- Request params: db: Session, current_user: PlatformUser
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/template/{table}' (user-analytics-backend/app/routers/admin_import.py)
- Handler: download_template
- Request params: table: str, db: Session, current_user: PlatformUser
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/summary' (user-analytics-backend/app/routers/analyticsOverview.py)
- Handler: get_summary
- Request params: db: Session, service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/overview' (user-analytics-backend/app/routers/analyticsOverview.py)
- Handler: get_overview
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/register' (user-analytics-backend/app/routers/auth.py)
- Handler: register
- Request params: payload: RegisterRequest, db: Session
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/login' (user-analytics-backend/app/routers/auth.py)
- Handler: login
- Request params: payload: LoginRequest, db: Session
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/dashboard' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaign_impact_dashboard
- Request params: db: Session, user: Any, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/list' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaigns_list
- Request params: status: Optional[str], campaign_type: Optional[str], start_date: Optional[date], end_date: Optional[date], service_id: Optional[str], page: int, limit: int, db: Session, user: Any
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/overview' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaigns_overview
- Request params: db: Session, user: Any
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/by-type' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaigns_by_type
- Request params: db: Session, user: Any
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/top' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_top_campaigns
- Request params: limit: int, db: Session, user: Any
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trend' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaigns_trend
- Request params: db: Session, user: Any
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/kpis' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaign_kpis
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/performance' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaign_performance
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/comparison' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaign_comparison
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/timeline' (user-analytics-backend/app/routers/campaign_impact.py)
- Handler: get_campaign_timeline
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/overview' (user-analytics-backend/app/routers/cross_service.py)
- Handler: get_overview
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/co-subscriptions' (user-analytics-backend/app/routers/cross_service.py)
- Handler: get_co_subscriptions
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/migrations' (user-analytics-backend/app/routers/cross_service.py)
- Handler: get_migrations
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/distribution' (user-analytics-backend/app/routers/cross_service.py)
- Handler: get_distribution
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/services' (user-analytics-backend/app/routers/management.py)
- Handler: list_services
- Request params: db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/services' (user-analytics-backend/app/routers/management.py)
- Handler: create_service
- Request params: body: ServiceCreateBody, db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### PUT '/services/{service_id}' (user-analytics-backend/app/routers/management.py)
- Handler: update_service
- Request params: service_id: str, body: ServiceUpdateBody, db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### DELETE '/services/{service_id}' (user-analytics-backend/app/routers/management.py)
- Handler: delete_service
- Request params: service_id: str, db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/campaigns' (user-analytics-backend/app/routers/management.py)
- Handler: list_campaigns
- Request params: db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/campaigns' (user-analytics-backend/app/routers/management.py)
- Handler: create_campaign
- Request params: body: CampaignCreateBody, db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### PUT '/campaigns/{campaign_id}' (user-analytics-backend/app/routers/management.py)
- Handler: update_campaign
- Request params: campaign_id: str, body: CampaignUpdateBody, db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### DELETE '/campaigns/{campaign_id}' (user-analytics-backend/app/routers/management.py)
- Handler: delete_campaign
- Request params: campaign_id: str, db: Session, _: object
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/train' (user-analytics-backend/app/routers/ml_churn.py)
- Handler: train_churn_model
- Request params: db: Session, _: Any
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/metrics' (user-analytics-backend/app/routers/ml_churn.py)
- Handler: get_churn_model_metrics
- Request params: None
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/scores' (user-analytics-backend/app/routers/ml_churn.py)
- Handler: get_churn_scores
- Request params: db: Session, top: int, threshold: float, store: bool
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/' (user-analytics-backend/app/routers/platform_user.py)
- Handler: list_platform_users
- Request params: skip: int, limit: int, search: str | None, role: str | None, is_active: bool | None, db: Session, _: PlatformUser
- Response schema: PlatformUserListResponse
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/{user_id}' (user-analytics-backend/app/routers/platform_user.py)
- Handler: get_platform_user
- Request params: user_id: UUID, db: Session, _: PlatformUser
- Response schema: PlatformUserResponse
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### POST '/' (user-analytics-backend/app/routers/platform_user.py)
- Handler: create_platform_user
- Request params: data: PlatformUserCreate, db: Session, _: PlatformUser
- Response schema: PlatformUserResponse
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### PUT '/{user_id}' (user-analytics-backend/app/routers/platform_user.py)
- Handler: update_platform_user
- Request params: user_id: UUID, data: PlatformUserUpdate, db: Session, _: PlatformUser
- Response schema: PlatformUserResponse
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### PATCH '/{user_id}/status' (user-analytics-backend/app/routers/platform_user.py)
- Handler: update_user_status
- Request params: user_id: UUID, body: UpdateStatusRequest, db: Session, current_user: PlatformUser
- Response schema: dict
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### PATCH '/{user_id}/role' (user-analytics-backend/app/routers/platform_user.py)
- Handler: update_user_role
- Request params: user_id: UUID, body: UpdateRoleRequest, db: Session, current_user: PlatformUser
- Response schema: dict
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### DELETE '/{user_id}' (user-analytics-backend/app/routers/platform_user.py)
- Handler: delete_platform_user
- Request params: user_id: UUID, db: Session, current_user: PlatformUser
- Response schema: dict
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/retention/kpis' (user-analytics-backend/app/routers/retention.py)
- Handler: get_retention_kpis
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/retention/heatmap' (user-analytics-backend/app/routers/retention.py)
- Handler: get_retention_heatmap
- Request params: db: Session, service_id: Optional[str], last_n_months: int
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/retention/curve' (user-analytics-backend/app/routers/retention.py)
- Handler: get_retention_curve
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/retention/cohorts-list' (user-analytics-backend/app/routers/retention.py)
- Handler: get_retention_cohorts_list
- Request params: db: Session, service_id: Optional[str], page: int, page_size: int
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '' (user-analytics-backend/app/routers/service.py)
- Handler: get_services
- Request params: db: Session
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trial/kpis' (user-analytics-backend/app/routers/trialAnalytics.py)
- Handler: get_trial_kpis
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trial/timeline' (user-analytics-backend/app/routers/trialAnalytics.py)
- Handler: get_trial_timeline
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trial/by-service' (user-analytics-backend/app/routers/trialAnalytics.py)
- Handler: get_trial_by_service
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trial/users' (user-analytics-backend/app/routers/trialAnalytics.py)
- Handler: get_trial_users
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str], search: Optional[str], status: Optional[str], page: int, page_size: int, export: bool
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trial/dropoff-by-day' (user-analytics-backend/app/routers/trialAnalytics.py)
- Handler: get_trial_dropoff_by_day
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/churn/breakdown' (user-analytics-backend/app/routers/trialAnalytics.py)
- Handler: get_churn_breakdown
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/user-activity' (user-analytics-backend/app/routers/userActivity.py)
- Handler: get_user_activity
- Request params: db: Session, start_date: Optional[date], end_date: Optional[date], service_id: Optional[str]
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '' (user-analytics-backend/app/routers/users.py)
- Handler: list_users
- Request params: status: Optional[str], date_from: Optional[datetime], date_to: Optional[datetime], search: Optional[str], service_id: Optional[str], page: int, page_size: int, export: bool, db: Session
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/trial' (user-analytics-backend/app/routers/users.py)
- Handler: list_trial_users
- Request params: status: Optional[str], search: Optional[str], service_id: Optional[str], page: int, page_size: int, export: bool, db: Session
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

### GET '/{user_id}' (user-analytics-backend/app/routers/users.py)
- Handler: get_user
- Request params: user_id: UUID, db: Session
- Response schema: Any
- Calls repository/service: Refer to function body in file
- Authentication required: Protected (role check likely)

## 6. React Pages / Components

### analytics-platform-front/src/App.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/CampaignModal.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: name / setName, serviceId / setServiceId, sendDate / setSendDate, targetSize / setTargetSize, errors / setErrors, saving / setSaving
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/CampaignTable.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/DeleteConfirmModal.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/ServiceModal.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: name / setName, billingType / setBillingType, price / setPrice, errors / setErrors, formError / setFormError, saving / setSaving
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/admin/management/ServiceTable.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/BIInsightsPanel.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/ChurnPieChart.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/EngagementHealthPanel.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/FilterBar.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: period / setPeriod, serviceId / setServiceId, customStart / setCustomStart, customEnd / setCustomEnd, openPeriod / setOpenPeriod, openService / setOpenService, services / setServices, globalStats / setGlobalStats, globalStatsLoading / setGlobalStatsLoading
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/KPICard.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx
- KPI/Feature: Trial analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/SubscriptionDonutChart.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/TabNavigation.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/TopServicesTable.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/CampaignFunnelChart.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: sortBy / setSortBy
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/CampaignVsOrganicChart.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/campaign/ServiceCampaignComparison.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/ChartContainer.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: isReady / setIsReady
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: showRetention / setShowRetention
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/ChurnReasonsChart.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/RiskSegmentsPanel.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn/TimeToChurnChart.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: topN / setTopN, threshold / setThreshold
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/retention/CohortHeatmap.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/retention/RetentionCurve.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/retention/ServiceRetentionRadar.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/RevenueTab.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/ActivityHeatmap.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: hoveredCell / setHoveredCell
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/InactivityAnalysis.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx
- KPI/Feature: Trial analytics feature
- API endpoints called: None detected
- State variables: sortKey / setSortKey, sortOrder / setSortOrder
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/dashboard/userActivity/UserGrowthChart.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/directory/Directory.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: searchQuery / setSearchQuery
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/AppLayout.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/Footer.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/Sidebar.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: isCollapsed / setIsCollapsed
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/SidebarNavItem.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/SidebarSection.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/Topbar.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: showNotifications / setShowNotifications, searchQuery / setSearchQuery
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/layout/navConfig.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/ConfirmDeleteModal.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/CreateUserModal.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: /platform-users
- State variables: formData / setFormData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/EditUserModal.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: formData / setFormData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/UserFilters.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/UserKPICards.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/platform-users/UserTable.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/components/subscribers/UserRowDetail.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: detail / setDetail, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/constants/dateFilters.js
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/context/AuthContext.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: access_token / setAccessToken, role / setRole, full_name / setFullName, userId / setUserId, isLoading / setIsLoading
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignComparison.js
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignImpactDashboard.js
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: data / setData, isLoading / setIsLoading, error / setError, data / setData, isLoading / setIsLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignKPIs.js
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignPerformance.js
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCampaignTimeline.js
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnBreakdown.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnCurve.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnDashboard.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, isLoading / setIsLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnKPIs.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnPredictionMetrics.js
- KPI/Feature: Churn analytics feature
- API endpoints called: /ml/churn/metrics
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnPredictionScores.js
- KPI/Feature: Churn analytics feature
- API endpoints called: /ml/churn/scores
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnPredictionTrain.js
- KPI/Feature: Churn analytics feature
- API endpoints called: /ml/churn/train
- State variables: loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useChurnReasons.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCohortsTable.js
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useCrossService.js
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: overview / setOverview, coSubscriptions / setCoSubscriptions, migrations / setMigrations, distribution / setDistribution, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useDashboardMetrics.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useImportData.js
- KPI/Feature: Frontend component/page
- API endpoints called: /admin/import/history
- State variables: loading / setLoading, historyLoading / setHistoryLoading, error / setError, history / setHistory
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useManagement.js
- KPI/Feature: Campaign analytics feature
- API endpoints called: /admin/management/campaigns, /admin/management/services
- State variables: services / setServices, campaigns / setCampaigns, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRetentionCurve.js
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRetentionHeatmap.js
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRetentionKPIs.js
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useRiskSegments.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTimeToChurn.js
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useToast.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: toast / setToast
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTrialDropoffByDay.js
- KPI/Feature: Trial analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTrialKPIs.js
- KPI/Feature: Trial analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useTrialUsers.js
- KPI/Feature: Trial analytics feature
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useUserActivity.js
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/hooks/useUsers.js
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/main.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/Dashboard.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/RootRedirect.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/SubscribersPage.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: isServiceOpen / setIsServiceOpen, subscribers / setSubscribers, loading / setLoading, error / setError, filters / setFilters, services / setServices, expandedRow / setExpandedRow
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/UserActivityPage.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters, searchInput / setSearchInput, search / setSearch, statutFilter / setStatutFilter, sortField / setSortField, sortDir / setSortDir, page / setPage, exportOpen / setExportOpen, exportLoading / setExportLoading, toastMsg / setToastMsg
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/admin/ImportDataPage.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: activeTab / setActiveTab, targetTable / setTargetTable, mode / setMode, file / setFile, preview / setPreview, columns / setColumns, result / setResult, confirmReplace / setConfirmReplace, validationModalOpen / setValidationModalOpen, staged / setStaged
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/admin/ManagementPage.jsx
- KPI/Feature: Campaign analytics feature
- API endpoints called: None detected
- State variables: tab / setTab, search / setSearch, serviceModalOpen / setServiceModalOpen, serviceModalMode / setServiceModalMode, serviceEditing / setServiceEditing, campaignModalOpen / setCampaignModalOpen, campaignModalMode / setCampaignModalMode, campaignEditing / setCampaignEditing, deleteOpen / setDeleteOpen, deleteLoading / setDeleteLoading, deleteContext / setDeleteContext
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/auth/LoginPage.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: /auth/login
- State variables: email / setEmail, password / setPassword, error / setError, loading / setLoading, rememberMe / setRememberMe, showPassword / setShowPassword
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters, page / setPage, statusFilter / setStatusFilter, typeFilter / setTypeFilter, selectedId / setSelectedId, toast / setToast
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/DashboardPage.jsx
- KPI/Feature: Churn analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters, activeTab / setActiveTab, data / setData, loading / setLoading, error / setError
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters, searchInput / setSearchInput, search / setSearch, statusFilter / setStatusFilter, sortField / setSortField, sortDir / setSortDir, page / setPage, exportOpen / setExportOpen, exportLoading / setExportLoading, toastMsg / setToastMsg
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/dashboard/RetentionPage.jsx
- KPI/Feature: Retention analytics feature
- API endpoints called: None detected
- State variables: filters / setFilters, page / setPage, searchInput / setSearchInput, search / setSearch, sortField / setSortField, sortDir / setSortDir, exportOpen / setExportOpen, exportLoading / setExportLoading, toastMsg / setToastMsg
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: /platform-users/
- State variables: users / setUsers, total / setTotal, loading / setLoading, search / setSearch, roleFilter / setRoleFilter, statusFilter / setStatusFilter, page / setPage, selectedUser / setSelectedUser, showCreateModal / setShowCreateModal, showEditModal / setShowEditModal, showDeleteModal / setShowDeleteModal, statsData / setStatsData
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/router/AdminRoute.jsx
- KPI/Feature: Dashboard aggregation feature
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/router/PrivateRoute.jsx
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/services/api.js
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

### analytics-platform-front/src/utils/apiError.js
- KPI/Feature: Frontend component/page
- API endpoints called: None detected
- State variables: None detected
- Known issues/incomplete sections: None detected

## 7. ETL Pipeline Analysis
### Source tables read from hawala_db (heuristic extraction)
- user-analytics-backend/scripts/compute_cohorts.py: FROM app.core.database
- user-analytics-backend/scripts/compute_cohorts.py: FROM cohort_base
- user-analytics-backend/scripts/compute_cohorts.py: FROM cohorts
- user-analytics-backend/scripts/compute_cohorts.py: FROM datetime
- user-analytics-backend/scripts/compute_cohorts.py: FROM first_sub
- user-analytics-backend/scripts/compute_cohorts.py: FROM information_schema.columns
- user-analytics-backend/scripts/compute_cohorts.py: FROM retention_rates
- user-analytics-backend/scripts/compute_cohorts.py: FROM sqlalchemy
- user-analytics-backend/scripts/compute_cohorts.py: FROM subscriptions
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM __future__
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM billing_events
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM dataclasses
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM datetime
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM decimal
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM dotenv
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM pathlib
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM scripts.compute_cohorts
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM service_subscription_types
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM service_types
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM services
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM sqlalchemy
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM sqlalchemy.exc
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM subscriptions
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM tqdm
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM transaction_histories
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM typing
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: FROM users
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM __future__
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM dataclasses
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM datetime
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM dotenv
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM hawala.subscribed_clients.
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM service_subscription_types
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM services
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM sqlalchemy
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM sqlalchemy.engine
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM subscribed_clients
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM typing
- user-analytics-backend/scripts/etl/fix_services_mapping.py: FROM users
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py: FROM app.core.database
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py: FROM campaigns
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py: FROM pathlib
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py: FROM sqlalchemy
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py: FROM subscriptions
- user-analytics-backend/scripts/etl/recalcul_cohorts.py: FROM scripts.compute_cohorts
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM __future__
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM billing_events
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM campaigns
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM candidates
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM datetime
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM dotenv
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM exc
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM locked_subscriptions
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM organic_campaign
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM services
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM sqlalchemy
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM sqlalchemy.exc
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM subscriptions
- user-analytics-backend/scripts/etl/seed_campaigns.py: FROM typing
- user-analytics-backend/scripts/verify_data.py: FROM __future__
- user-analytics-backend/scripts/verify_data.py: FROM billing_events
- user-analytics-backend/scripts/verify_data.py: FROM dotenv
- user-analytics-backend/scripts/verify_data.py: FROM pathlib
- user-analytics-backend/scripts/verify_data.py: FROM sqlalchemy
- user-analytics-backend/scripts/verify_data.py: FROM transaction_histories
### Target tables written to analytics_db (heuristic extraction)
- user-analytics-backend/scripts/compute_cohorts.py: INTO cohorts
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO billing_events
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO import_logs
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO service_types
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO services
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO subscriptions
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO unsubscriptions
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO user_activities
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: INTO users
- user-analytics-backend/scripts/etl/fix_services_mapping.py: INTO subscriptions
- user-analytics-backend/scripts/etl/seed_campaigns.py: INTO campaigns
### Transformation Logic
- Field mapping/type casting/filtering exists in ETL scripts under scripts/etl and companion scripts; inspect per-file function list above for exact transformations.
### Anchor Temporal Logic
- user-analytics-backend/scripts/etl/seed_campaigns.py: Uses MAX(event_datetime) as watermark to incrementally load newer events
### Volume of data processed
- No stable hardcoded batch volume was inferred globally; check runtime logs and ETL script constants for exact volumes.

## 8. KPI Implementation Status

### DAU
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: .report_all_files.txt, analytics-platform-front/package-lock.json, analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx, analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx, analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx, analytics-platform-front/src/hooks/useDashboardMetrics.js, analytics-platform-front/src/pages/UserActivityPage.jsx, docs/Rapport_Avancement_PFE.pdf, docs/kpis.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-24.pdf, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/models/user_activities.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/userActivity.py
- SQL/formula samples:
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### WAU
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: analytics-platform-front/package-lock.json, analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx, analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx, analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx, analytics-platform-front/src/pages/UserActivityPage.jsx, docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf, docs/kpis.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/models/user_activities.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/userActivity.py
- SQL/formula samples:
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### MAU
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: .report_all_files.txt, analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx, analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx, analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx, analytics-platform-front/src/hooks/useDashboardMetrics.js, analytics-platform-front/src/pages/UserActivityPage.jsx, docs/kpis.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-23_p1.png, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/models/user_activities.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/userActivity.py
- SQL/formula samples:
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Stickiness
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx, analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx, analytics-platform-front/src/hooks/useDashboardMetrics.js, analytics-platform-front/src/pages/UserActivityPage.jsx, docs/kpis.md, tmp/generate_project_report.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/userActivity.py
- SQL/formula samples:
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
```sql
select
              value={statutFilter}
              onChange={(e) => { setStatutFilter(e.target.value);
```
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Churn Rate
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: .agents/skills/supabase-postgres-best-practices/references/monitor-vacuum-analyze.md, analytics-platform-front/src/App.jsx, analytics-platform-front/src/components/dashboard/ChurnPieChart.jsx, analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx, analytics-platform-front/src/components/dashboard/TabNavigation.jsx, analytics-platform-front/src/components/dashboard/TopServicesTable.jsx, analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx, analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx, analytics-platform-front/src/components/dashboard/churn/ChurnReasonsChart.jsx, analytics-platform-front/src/components/dashboard/churn/RiskSegmentsPanel.jsx, analytics-platform-front/src/components/dashboard/churn/TimeToChurnChart.jsx, analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx, analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx, analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx, analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx, analytics-platform-front/src/components/dashboard/userActivity/InactivityAnalysis.jsx, analytics-platform-front/src/components/dashboard/userActivity/UserGrowthChart.jsx, analytics-platform-front/src/components/layout/Topbar.jsx, analytics-platform-front/src/components/layout/navConfig.js, analytics-platform-front/src/hooks/useChurnBreakdown.js, analytics-platform-front/src/hooks/useChurnCurve.js, analytics-platform-front/src/hooks/useChurnDashboard.js, analytics-platform-front/src/hooks/useChurnKPIs.js, analytics-platform-front/src/hooks/useChurnPredictionMetrics.js, analytics-platform-front/src/hooks/useChurnPredictionScores.js, analytics-platform-front/src/hooks/useChurnPredictionTrain.js, analytics-platform-front/src/hooks/useChurnReasons.js, analytics-platform-front/src/hooks/useDashboardMetrics.js, analytics-platform-front/src/hooks/useRiskSegments.js, analytics-platform-front/src/hooks/useTimeToChurn.js, analytics-platform-front/src/pages/SubscribersPage.jsx, analytics-platform-front/src/pages/UserActivityPage.jsx, analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx, analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx, analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx, analytics-platform-front/src/pages/dashboard/DashboardPage.jsx, docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf, docs/etl_prod_readme.md, docs/kpis.md, docs/ml_churn_report.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/main.py, user-analytics-backend/app/models/unsubscriptions.py, user-analytics-backend/app/repositories/churn_repo.py, user-analytics-backend/app/routers/admin_import.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/churn_analysis.py, user-analytics-backend/app/routers/ml_churn.py, user-analytics-backend/app/routers/trialAnalytics.py, user-analytics-backend/app/routers/userActivity.py, user-analytics-backend/app/schemas/Unsubscriptions.py, user-analytics-backend/app/schemas/churn_analysis.py, user-analytics-backend/app/schemas/ml_churn.py, user-analytics-backend/app/schemas/users.py, user-analytics-backend/app/services/churn_service.py, user-analytics-backend/app/utils/temporal.py, user-analytics-backend/ml_models/churn_metrics.joblib, user-analytics-backend/ml_models/churn_model.joblib, user-analytics-backend/ml_models/churn_predictor.py, user-analytics-backend/scripts/etl/etl_prod_to_analytics.py, user-analytics-backend/scripts/seeder/seed_missing_data.py
- SQL/formula samples:
```sql
select * from orders where status = 'pending';
```
```sql
select
  relname,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  last_autoanalyze
from pg_stat_user_tables
order by last_analyze nulls first;
```
```sql
select * from pg_stat_progress_vacuum;
```
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Retention
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: analytics-platform-front/src/App.jsx, analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx, analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx, analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx, analytics-platform-front/src/components/dashboard/retention/CohortHeatmap.jsx, analytics-platform-front/src/components/dashboard/retention/RetentionCurve.jsx, analytics-platform-front/src/components/dashboard/retention/ServiceRetentionRadar.jsx, analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx, analytics-platform-front/src/components/layout/navConfig.js, analytics-platform-front/src/hooks/useCohortsTable.js, analytics-platform-front/src/hooks/useRetentionCurve.js, analytics-platform-front/src/hooks/useRetentionHeatmap.js, analytics-platform-front/src/hooks/useRetentionKPIs.js, analytics-platform-front/src/pages/admin/ImportDataPage.jsx, analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx, analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx, analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx, analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx, analytics-platform-front/src/pages/dashboard/RetentionPage.jsx, docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf, docs/etl_prod_readme.md, docs/kpis.md, docs/ml_churn_report.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, reorganize_project.py, reorganize_report.json, tmp/generate_project_report.py, user-analytics-backend/alembic/versions/6c076db13bed_add_analytics_performance_indexes.py, user-analytics-backend/app/main.py, user-analytics-backend/app/models/__init__.py, user-analytics-backend/app/models/campaigns.py, user-analytics-backend/app/models/cohorts.py, user-analytics-backend/app/models/services.py, user-analytics-backend/app/repositories/churn_repo.py, user-analytics-backend/app/routers/admin_import.py, user-analytics-backend/app/routers/campaign_impact.py, user-analytics-backend/app/routers/churn_analysis.py, user-analytics-backend/app/routers/cross_service.py, user-analytics-backend/app/routers/retention.py, user-analytics-backend/app/schemas/Cohorts.py, user-analytics-backend/app/schemas/__init__.py, user-analytics-backend/app/schemas/churn_analysis.py, user-analytics-backend/app/services/churn_service.py, user-analytics-backend/ml_models/churn_metrics.joblib, user-analytics-backend/ml_models/churn_model.joblib, user-analytics-backend/ml_models/churn_predictor.py, user-analytics-backend/scripts/compute_cohorts.py, user-analytics-backend/scripts/etl/etl_prod_to_analytics.py, user-analytics-backend/scripts/etl/recalcul_cohorts.py, user-analytics-backend/scripts/etl/seed_campaigns.py, user-analytics-backend/scripts/seeder/seed_missing_data.py, user-analytics-backend/scripts/verify_data.py
- SQL/formula samples:
```sql
Selected = async (f) => {
    resetStateForNewFile()
    if (!f) return
```
```sql
Selected(f)
  }
```
```sql
select>
                  <button
                    onClick={() => downloadTemplate(targetTable)}
                    className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-200 hover:bg-slate-700/60"
                    type="button"
                  >
                    <Download size={16} /> Template
                  </button>
                </div>
              </div>
```
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### ARPU
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx, analytics-platform-front/src/components/dashboard/tabs/RevenueTab.jsx, analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx, tmp/generate_project_report.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/cross_service.py
- SQL/formula samples:
```sql
SELECT|INSERT|UPDATE|DELETE|WITH|CREATE\s+TABLE|ALTER\s+TABLE)\b", s, re.IGNORECASE):
                info["sql_strings"].append(s)
        if isinstance(node, ast.Pass):
            info["placeholders"].append("pass statement found")
```
```sql
SELECT[\s\S]{0,500}?(?:;
```
```sql
SELECT projection")
        md.append("- Nearby TODO/issues: See section 11")
```
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Avg Lifetime
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx, analytics-platform-front/src/pages/UserActivityPage.jsx, analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx, docs/kpis.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/cahier_charges_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/repositories/churn_repo.py, user-analytics-backend/app/routers/churn_analysis.py, user-analytics-backend/app/routers/userActivity.py, user-analytics-backend/app/schemas/churn_analysis.py, user-analytics-backend/app/services/churn_service.py
- SQL/formula samples:
```sql
select
              value={statutFilter}
              onChange={(e) => { setStatutFilter(e.target.value);
```
```sql
select>
```
  - stickiness = DAU / MAU
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### NRR
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: docs/Rapport_Avancement_PFE.pdf, tmp/generate_project_report.py
- SQL/formula samples:
```sql
SELECT|INSERT|UPDATE|DELETE|WITH|CREATE\s+TABLE|ALTER\s+TABLE)\b", s, re.IGNORECASE):
                info["sql_strings"].append(s)
        if isinstance(node, ast.Pass):
            info["placeholders"].append("pass statement found")
```
```sql
SELECT[\s\S]{0,500}?(?:;
```
```sql
SELECT projection")
        md.append("- Nearby TODO/issues: See section 11")
```
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Trial Conversion
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: .report_all_files.txt, analytics-platform-front/src/components/admin/management/CampaignTable.jsx, analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx, analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx, analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx, analytics-platform-front/src/components/dashboard/campaign/ServiceCampaignComparison.jsx, analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx, analytics-platform-front/src/hooks/useDashboardMetrics.js, analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx, analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx, docs/REAL_DATA_INTEGRATION.md, docs/TRIAL_INTEGRATION_SUMMARY.md, docs/kpis.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/repositories/campaign_repo.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/campaign_impact.py, user-analytics-backend/app/routers/management.py, user-analytics-backend/app/routers/trialAnalytics.py, user-analytics-backend/app/schemas/users.py, user-analytics-backend/app/services/campaign_service.py
- SQL/formula samples:
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
  - stickiness = DAU / MAU
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Drop-off J3
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: analytics-platform-front/package-lock.json, analytics-platform-front/public/digmaco.png, analytics-platform-front/src/assets/digmaco.png, analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx, analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx, analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx, analytics-platform-front/src/hooks/useDashboardMetrics.js, analytics-platform-front/src/hooks/useTrialDropoffByDay.js, analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx, docs/Digital Campaign Objectives & Service Overview.pdf, docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf, docs/REAL_DATA_INTEGRATION.md, docs/Rapport_Avancement_PFE.pdf, docs/TRIAL_INTEGRATION_SUMMARY.md, docs/kpis.md, docs/tmp/generate_rapport.py, docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-23_p1.png, docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-24.pdf, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py, user-analytics-backend/app/routers/analyticsOverview.py, user-analytics-backend/app/routers/trialAnalytics.py
- SQL/formula samples:
  - stickiness = DAU / MAU
```sql
select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value);
```
```sql
select>
```
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

### Campaign ROI
- [x] Implemented / [ ] Partial / [ ] Planned
- Files: .report_all_files.txt, analytics-platform-front/package-lock.json, analytics-platform-front/package.json, analytics-platform-front/public/digmaco.png, analytics-platform-front/src/assets/digmaco.png, analytics-platform-front/src/components/layout/navConfig.js, docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-24.pdf, docs/tmp/pdfs/cahier_charges_extract.txt, docs/tmp/pdfs/rapport_avancement_extract.txt, tmp/generate_project_report.py
- SQL/formula samples:
  - stickiness = DAU / MAU
```sql
selected criteria.
Functional Description
● Generate a report by:
○ Date range selection
○ Single service or all services combined
● Reports should summarize:
○ Key KPIs
○ User behavior insights
○ Trial → paid conversion
○ Churn and retention
```
  - stickiness = DAU / MAU
- Known bugs/corrections: See Known Issues section
- Frontend page display: inferred from matching hooks/pages with same KPI keyword

## 9. Authentication & Authorization
- JWT implementation files (keyword-based scan):
  - analytics-platform-front/src/components/directory/Directory.jsx
  - analytics-platform-front/src/components/layout/Sidebar.jsx
  - analytics-platform-front/src/components/layout/Topbar.jsx
  - analytics-platform-front/src/components/platform-users/CreateUserModal.jsx
  - analytics-platform-front/src/components/platform-users/EditUserModal.jsx
  - analytics-platform-front/src/components/platform-users/UserFilters.jsx
  - analytics-platform-front/src/components/platform-users/UserTable.jsx
  - analytics-platform-front/src/context/AuthContext.jsx
  - analytics-platform-front/src/pages/Dashboard.jsx
  - analytics-platform-front/src/pages/auth/LoginPage.jsx
  - analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx
  - analytics-platform-front/src/services/api.js
  - docs/tmp/generate_rapport.py
  - tmp/generate_project_report.py
  - user-analytics-backend/app/core/dependencies.py
  - user-analytics-backend/app/core/security.py
  - user-analytics-backend/app/main.py
  - user-analytics-backend/app/models/platform_users.py
  - user-analytics-backend/app/routers/admin_import.py
  - user-analytics-backend/app/routers/analyticsOverview.py
  - user-analytics-backend/app/routers/auth.py
  - user-analytics-backend/app/routers/campaign_impact.py
  - user-analytics-backend/app/routers/churn_analysis.py
  - user-analytics-backend/app/routers/cross_service.py
  - user-analytics-backend/app/routers/management.py
  - user-analytics-backend/app/routers/ml_churn.py
  - user-analytics-backend/app/routers/platform_user.py
  - user-analytics-backend/app/routers/retention.py
  - user-analytics-backend/app/routers/service.py
  - user-analytics-backend/app/routers/trialAnalytics.py
  - user-analytics-backend/app/routers/userActivity.py
  - user-analytics-backend/app/routers/users.py
  - user-analytics-backend/app/schemas/__init__.py
  - user-analytics-backend/app/schemas/auth.py
  - user-analytics-backend/app/schemas/platform_user_schemas.py
  - user-analytics-backend/app/services/platform_user_service.py
- Role definitions: Admin / Viewer (per project spec; validate exact enums/classes in backend auth modules).
- Protected endpoints: endpoints with Depends/current_user/role checks (see FastAPI routes section).
- Known gaps: enforce consistent role-based dependency across all routes and document public routes explicitly.

## 10. Configuration & Environment
### Environment variables (.env)
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=***
- POSTGRES_DB=analytics_db
- DATABASE_URL=postgresql://postgres:12345hawala@host.docker.internal:5433/analytics_db
### Database connection strings (masked)
- .env: postgresql://postgres:***@host.docker.internal:5433/analytics_db
- docs/etl_prod_readme.md: postgresql://postgres:***@localhost:5432/hawala
- docs/etl_prod_readme.md: postgresql://postgres:***@localhost:5432/analytics_db
- mcp.json: postgresql://postgres:***@localhost:5433/analytics_db
- mcp.json: postgresql://postgres:***@localhost:5433/hawala
- user-analytics-backend/.env: postgresql://postgres:***@localhost:5433/analytics_db
- user-analytics-backend/.env: postgresql://postgres:***@localhost:5433/hawala
- user-analytics-backend/.env: postgresql://postgres:***@localhost:5433/analytics_db
- user-analytics-backend/alembic.ini: postgresql://postgres:***@localhost:5433/analytics_db
- user-analytics-backend/app/core/database.py: postgresql://postgres:***@localhost:5433/analytics_db
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: postgresql://postgres:***@localhost:5433/hawala
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: postgresql://postgres:***@localhost:5433/analytics_db
- user-analytics-backend/scripts/etl/fix_services_mapping.py: postgresql://postgres:***@localhost:5432/hawala
- user-analytics-backend/scripts/etl/fix_services_mapping.py: postgresql://postgres:***@localhost:5432/analytics_db
- user-analytics-backend/scripts/etl/seed_campaigns.py: postgresql://postgres:***@localhost:5433/analytics_db
- user-analytics-backend/scripts/verify_data.py: postgresql://postgres:***@localhost:5432/hawala
- user-analytics-backend/scripts/verify_data.py: postgresql://postgres:***@localhost:5433/analytics_db
### Hardcoded values that should be configurable
- reorganize_project.py:54 -> ANALYTICS_CONN=postgresql+psycopg2://user:password@localhost:5432/analytics_db
- reorganize_project.py:55 -> PROD_CONN=postgresql+psycopg2://user:password@hawala_host:5432/hawala_db
- reorganize_project.py:65 -> CORS_ORIGINS=[\"http://localhost:5173\"]
- reorganize_project.py:68 -> VITE_API_BASE_URL=http://localhost:8000/api/v1
- reorganize_project.py:74 -> \tuvicorn app.main:app --reload --host 0.0.0.0 --port 8000
- reorganize_project.py:517 -> self._write_file(self.frontend / ".env.example", "VITE_API_BASE_URL=http://localhost:8000/api/v1\n")
- tmp/generate_project_report.py:670 -> md.append("- No stable hardcoded batch volume was inferred globally; check runtime logs and ETL script constants for exact volumes.")
- tmp/generate_project_report.py:734 -> md.append("### Hardcoded values that should be configurable")
- tmp/generate_project_report.py:735 -> hardcoded = []
- tmp/generate_project_report.py:739 -> if re.search(r"(localhost|127\.0\.0\.1|5432|8000|hardcoded|TODO.*config)", line, re.IGNORECASE):
- tmp/generate_project_report.py:740 -> hardcoded.append((rel(f), i, line.strip()))
- tmp/generate_project_report.py:741 -> if hardcoded:
- tmp/generate_project_report.py:742 -> for f, i, l in hardcoded[:200]:
- tmp/generate_project_report.py:745 -> md.append("- No obvious hardcoded config values found by heuristic scan")
- user-analytics-backend/app/core/database.py:7 -> # Fallback localhost pour le développement sans Docker
- user-analytics-backend/app/core/database.py:10 -> "postgresql://postgres:12345hawala@localhost:5433/analytics_db"
- user-analytics-backend/app/main.py:36 -> "http://localhost:5173",
- user-analytics-backend/app/main.py:37 -> "http://127.0.0.1:5173",
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py:1409 -> source_url = os.getenv("HAWALA_CONN",    "postgresql://postgres:12345hawala@localhost:5433/hawala")
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py:1410 -> target_url = os.getenv("ANALYTICS_CONN", "postgresql://postgres:12345hawala@localhost:5433/analytics_db")
- user-analytics-backend/scripts/etl/fix_services_mapping.py:318 -> source_engine = get_engine("HAWALA_CONN", "postgresql://postgres:password@localhost:5432/hawala")
- user-analytics-backend/scripts/etl/fix_services_mapping.py:319 -> target_engine = get_engine("ANALYTICS_CONN", "postgresql://postgres:password@localhost:5432/analytics_db")
- user-analytics-backend/scripts/etl/seed_campaigns.py:314 -> url    = os.getenv("ANALYTICS_CONN", "postgresql://postgres:12345hawala@localhost:5433/analytics_db")
- user-analytics-backend/scripts/verify_data.py:31 -> hawala_conn = os.getenv("HAWALA_CONN", "postgresql://postgres:password@localhost:5432/hawala")
- user-analytics-backend/scripts/verify_data.py:32 -> analytics_conn = os.getenv("ANALYTICS_CONN", os.getenv("DATABASE_URL", "postgresql://postgres:12345hawala@localhost:5433/analytics_db"))

## 11. Known Issues & TODOs
- .agents/skills/supabase-postgres-best-practices/AGENTS.md:60 -> - Supabase-specific notes (when applicable)
- .agents/skills/supabase-postgres-best-practices/references/schema-data-types.md:10 -> Using the right data types reduces storage, improves query performance, and prevents bugs.
- .agents/skills/supabase-postgres-best-practices/references/schema-lowercase-identifiers.md:4 -> impactDescription: Avoid case-sensitivity bugs with tools, ORMs, and AI assistants
- .agents/skills/supabase-postgres-best-practices/references/security-rls-basics.md:18 -> -- Bug or bypass means all data is exposed!
- .agents/skills/supabase-postgres-best-practices/SKILL.md:56 -> - Supabase-specific notes (when applicable)
- .report_all_files.txt:1364 -> .venv\Lib\site-packages\faker\sphinx\autodoc.py
- .report_all_files.txt:1976 -> .venv\Lib\site-packages\numpy\distutils\mingw\gfortran_vs2003_hack.c
- .report_all_files.txt:4775 -> .venv\Lib\site-packages\pip\_internal\commands\debug.py
- .report_all_files.txt:5279 -> .venv\Lib\site-packages\pyasn1\debug.py
- .report_all_files.txt:5593 -> .venv\Lib\site-packages\scipy\fft\_debug_backends.py
- .report_all_files.txt:5746 -> .venv\Lib\site-packages\scipy\interpolate\tests\data\bug-1310.npz
- .report_all_files.txt:7168 -> .venv\Lib\site-packages\setuptools\_distutils\debug.py
- .report_all_files.txt:8634 -> .venv\Lib\site-packages\tqdm\autonotebook.py
- .report_all_files.txt:8640 -> .venv\Lib\site-packages\tqdm\notebook.py
- .report_all_files.txt:8651 -> .venv\Lib\site-packages\tqdm\_tqdm_notebook.py
- .report_all_files.txt:9463 -> .venv\Lib\site-packages\_distutils_hack\override.py
- .report_all_files.txt:9464 -> .venv\Lib\site-packages\_distutils_hack\__init__.py
- analytics-platform-front/.gitignore:4 -> npm-debug.log*
- analytics-platform-front/.gitignore:5 -> yarn-debug.log*
- analytics-platform-front/.gitignore:7 -> pnpm-debug.log*
- analytics-platform-front/.gitignore:8 -> lerna-debug.log*
- analytics-platform-front/package-lock.json:96 -> "debug": "^4.1.0",
- analytics-platform-front/package-lock.json:324 -> "debug": "^4.3.1"
- analytics-platform-front/package-lock.json:898 -> "debug": "^4.3.1",
- analytics-platform-front/package-lock.json:939 -> "debug": "^4.3.2",
- analytics-platform-front/package-lock.json:2695 -> "node_modules/debug": {
- analytics-platform-front/package-lock.json:2697 -> "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.3.tgz",
- analytics-platform-front/package-lock.json:2932 -> "debug": "^4.3.2",
- analytics-platform-front/package-lock.json:3275 -> "debug": {
- analytics-platform-front/package-lock.json:5239 -> "url": "https://github.com/sponsors/colinhacks"
- docs/etl_prod_readme.md:95 -> ## Notes importantes
- docs/kpis.md:419 -> ### 8. Notes & Benchmarks (à adapter pour le jury)
- docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf:3965 -> <</Title (Scope Notes )
- docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf:4145 -> <</Title (10. Notes for the Intern )
- docs/tmp/generate_rapport.py:290 -> Paragraph("<b>Note</b>", body_bold)],
- docs/tmp/generate_rapport.py:678 -> "<b>Note :</b> Le cahier des charges exige au minimum 5 recommandations. "
- docs/tmp/generate_rapport.py:680 -> ParagraphStyle("note", parent=body_style, textColor=ORANGE)
- docs/tmp/generate_rapport.py:829 -> print(f"\n✅ PDF généré avec succès : {output_path}")
- docs/tmp/generate_rapport.py:830 -> print(f"   Taille : {os.path.getsize(output_path) / 1024:.1f} Ko")
- docs/tmp/pdfs/cahier_charges_extract.txt:132 -> Scope Notes
- docs/tmp/pdfs/cahier_charges_extract.txt:269 -> 10. Notes for the Intern
- docs/tmp/pdfs/rapport_avancement_extract.txt:632 -> Note: Les données de cohortes sont désormais disponibles dans la
- docs/tmp/pdfs/rapport_avancement_extract.txt:658 -> [4] Ellis, S. (2017). Hacking Growth: How Today's Fastest-Growing
- reorganize_project.py:64 -> DEBUG=true
- reorganize_project.py:244 -> print(json.dumps(payload, ensure_ascii=True))
- reorganize_project.py:451 -> if path.suffix == ".ipynb" and "notebooks" not in [p.lower() for p in path.parts]:
- reorganize_project.py:452 -> file_candidates.append((path, "notebook-outside-notebooks"))
- reorganize_project.py:558 -> print(json.dumps({"message": "report_generated", "path": report_path.as_posix()}, ensure_ascii=True))
- tmp/generate_project_report.py:277 -> def extract_todos(path: Path, text: str) -> List[Dict[str, str]]:
- tmp/generate_project_report.py:279 -> pat = re.compile(r"TODO|FIXME|HACK|NOTE|BUG|print\(", re.IGNORECASE)
- tmp/generate_project_report.py:316 -> todos = []
- tmp/generate_project_report.py:318 -> if re.search(r"TODO|FIXME|HACK|BUG", line, re.IGNORECASE):
- tmp/generate_project_report.py:319 -> todos.append(f"L{i}: {line.strip()}")
- tmp/generate_project_report.py:332 -> return {"endpoints": endpoints, "states": states, "todos": todos, "feature": feature}
- tmp/generate_project_report.py:405 -> todos: List[Dict[str, str]] = []
- tmp/generate_project_report.py:411 -> todos.extend(extract_todos(f, txt))
- tmp/generate_project_report.py:447 -> md.append("Le projet est globalement structuré et couvre une chaîne complète analytics (ETL -> API FastAPI -> UI React), avec plusieurs KPI déjà présents côté hooks/services/pages. L’architecture est avancée sur les modules churn/retention/campaign/trial, mais la couverture de tests reste partielle 
- tmp/generate_project_report.py:551 -> if rinf.get("todos"):
- tmp/generate_project_report.py:553 -> for t in rinf["todos"]:
- tmp/generate_project_report.py:571 -> md.append("- Nearby TODO/issues: See section 11")
- tmp/generate_project_report.py:636 -> if inf.get("todos"):
- tmp/generate_project_report.py:638 -> for t in inf["todos"]:
- tmp/generate_project_report.py:693 -> md.append("- Known bugs/corrections: See Known Issues section")
- tmp/generate_project_report.py:739 -> if re.search(r"(localhost|127\.0\.0\.1|5432|8000|hardcoded|TODO.*config)", line, re.IGNORECASE):
- tmp/generate_project_report.py:748 -> md.append("## 11. Known Issues & TODOs")
- tmp/generate_project_report.py:749 -> if todos:
- tmp/generate_project_report.py:750 -> for t in todos:
- tmp/generate_project_report.py:753 -> md.append("- No TODO/FIXME/HACK/NOTE/BUG/print() markers found")
- tmp/generate_project_report.py:762 -> if re.search(r"TODO|FIXME|pass\b|NotImplementedError|return\s+\{\s*\}", txt):
- tmp/generate_project_report.py:763 -> missing.append(f"{rp}: contains TODO/FIXME/pass/NotImplemented/empty return pattern")
- tmp/generate_project_report.py:783 -> print(f"Report generated: {OUTPUT}")
- user-analytics-backend/.env.example:12 -> DEBUG=true
- user-analytics-backend/alembic.ini:57 -> # Note that in order to support legacy alembic.ini files, this default does NOT
- user-analytics-backend/alembic/env.py:28 -> print(f"Tables found in metadata: {Base.metadata.tables.keys()}")
- user-analytics-backend/alembic/versions/6c076db13bed_add_analytics_performance_indexes.py:22 -> # NOTE:
- user-analytics-backend/app/routers/admin_import.py:31 -> # Notes:
- user-analytics-backend/app/routers/admin_import.py:491 -> # NOTE: we cast per-column for UUID/datetime/numeric when possible using heuristic
- user-analytics-backend/app/routers/analyticsOverview.py:186 -> failure_data_note = (
- user-analytics-backend/app/routers/analyticsOverview.py:242 -> "failed_pct":         None if failure_data_note else float(revenue.failed_pct or 0),
- user-analytics-backend/app/routers/analyticsOverview.py:243 -> "failure_data_note":  failure_data_note,
- user-analytics-backend/app/routers/analyticsOverview.py:440 -> failure_data_note = (
- user-analytics-backend/app/routers/analyticsOverview.py:504 -> "failed_pct":         None if failure_data_note else float(revenue.failed_pct or 0),
- user-analytics-backend/app/routers/analyticsOverview.py:505 -> "failure_data_note":  failure_data_note,
- user-analytics-backend/ml_models/churn_predictor.py:30 -> Notes:
- user-analytics-backend/ml_models/churn_predictor.py:429 -> # Store only for API debugging / jury export.
- user-analytics-backend/scripts/compute_cohorts.py:18 -> print("=" * 60)
- user-analytics-backend/scripts/compute_cohorts.py:19 -> print("🚀 ETL — Cohorts computation started")
- user-analytics-backend/scripts/compute_cohorts.py:20 -> print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
- user-analytics-backend/scripts/compute_cohorts.py:21 -> print("=" * 60)
- user-analytics-backend/scripts/compute_cohorts.py:28 -> print("\n🔍 ÉTAPE 0 — Diagnostic des statuts disponibles...")
- user-analytics-backend/scripts/compute_cohorts.py:37 -> print(f"   {'Status':<20} {'Count':>10}")
- user-analytics-backend/scripts/compute_cohorts.py:38 -> print(f"   {'-'*20} {'-'*10}")
- user-analytics-backend/scripts/compute_cohorts.py:40 -> print(f"   {str(row.status):<20} {row.cnt:>10}")
- user-analytics-backend/scripts/compute_cohorts.py:51 -> print(f"\n   ⚠️  Aucun statut 'active' trouvé.")
- user-analytics-backend/scripts/compute_cohorts.py:52 -> print(f"   ⚠️  Fallback sur le statut dominant: '{active_statuses_str}'")
- user-analytics-backend/scripts/compute_cohorts.py:59 -> print(f"\n   → Statuts considérés comme actifs: {active_statuses_str}")
- user-analytics-backend/scripts/compute_cohorts.py:64 -> print("\n📊 ÉTAPE 1 — Vérification données sources...")
- user-analytics-backend/scripts/compute_cohorts.py:76 -> print(f"   ✅ Total subscriptions : {counts.total_subscriptions}")
- user-analytics-backend/scripts/compute_cohorts.py:77 -> print(f"   ✅ Unique users         : {counts.unique_users}")
- user-analytics-backend/scripts/compute_cohorts.py:78 -> print(f"   ✅ Unique services      : {counts.unique_services}")
- user-analytics-backend/scripts/compute_cohorts.py:79 -> print(f"   ✅ Plage dates          : {counts.min_date} → {counts.max_date}")
- user-analytics-backend/scripts/compute_cohorts.py:82 -> print("\n❌ Table subscriptions vide. Relancer l'ETL principal d'abord.")
- user-analytics-backend/scripts/compute_cohorts.py:92 -> print(f"   ✅ Type subscription_end_date : {col_type}")
- user-analytics-backend/scripts/compute_cohorts.py:102 -> print("\n📊 ÉTAPE 2 — Calcul des cohortes (first_subscription_date)...")
- user-analytics-backend/scripts/compute_cohorts.py:125 -> print(f"\n   {'Cohorte':<15} {'Service ID':<40} {'Users':>8}")
- user-analytics-backend/scripts/compute_cohorts.py:126 -> print(f"   {'-'*15} {'-'*40} {'-'*8}")
- user-analytics-backend/scripts/compute_cohorts.py:128 -> print(f"   {str(row.cohort_date):<15} {str(row.service_id):<40} {row.total_users:>8}")
- user-analytics-backend/scripts/compute_cohorts.py:130 -> print(f"   ... et {len(cohort_preview) - 10} autres cohortes")
- user-analytics-backend/scripts/compute_cohorts.py:133 -> print(f"\n   → {total_cohorts} cohortes détectées")
- user-analytics-backend/scripts/compute_cohorts.py:136 -> print("\n⚠️  Aucune cohorte calculable. Vérifier subscription_start_date.")
- user-analytics-backend/scripts/compute_cohorts.py:142 -> print("\n📊 ÉTAPE 3 — Calcul retention D7 / D14 / D30...")
- user-analytics-backend/scripts/compute_cohorts.py:153 -> print(f"\n   📅 Durée des données disponibles : ~{int(data_span)} jours")
- user-analytics-backend/scripts/compute_cohorts.py:155 -> print(f"   ⚠️  Moins de 30 jours de données → D30 sera 0% ou incomplet (normal)")
- user-analytics-backend/scripts/compute_cohorts.py:239 -> print(f"\n   {'Cohorte':<12} {'D7':>8} {'D14':>8} {'D30':>8} {'Users':>8}")
- user-analytics-backend/scripts/compute_cohorts.py:240 -> print(f"   {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
- user-analytics-backend/scripts/compute_cohorts.py:248 -> print(
- user-analytics-backend/scripts/compute_cohorts.py:259 -> print("\n💾 ÉTAPE 4 — Insertion dans la table cohorts...")
- user-analytics-backend/scripts/compute_cohorts.py:366 -> print(f"\n   ✅ {final} cohortes présentes dans la table cohorts")
- user-analytics-backend/scripts/compute_cohorts.py:367 -> print(f"\n   Échantillon des dernières cohortes insérées:")
- user-analytics-backend/scripts/compute_cohorts.py:369 -> print(f"   {row.cohort_date} | users={row.total_users}"
- user-analytics-backend/scripts/compute_cohorts.py:374 -> print("\n" + "=" * 60)
- user-analytics-backend/scripts/compute_cohorts.py:375 -> print("✅ ETL terminé avec succès !")
- user-analytics-backend/scripts/compute_cohorts.py:376 -> print("=" * 60)
- user-analytics-backend/scripts/compute_cohorts.py:380 -> print(f"\n❌ ERREUR : {e}")
- user-analytics-backend/scripts/compute_cohorts.py:382 -> traceback.print_exc()  # Stack trace complet pour debug
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py:160 -> print(f"ETL termine: {imported_rows} lignes importees, periode {min_date} -> {max_date}")
- user-analytics-backend/scripts/etl/fix_services_mapping.py:61 -> print(json.dumps(payload, ensure_ascii=True))
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:29 -> print("=" * 70)
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:30 -> print("ETL: Link Subscriptions to Campaigns")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:31 -> print("=" * 70)
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:37 -> print(f"\nBefore: {before} subscriptions with campaign_id")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:68 -> print(f"After: {after} subscriptions with campaign_id")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:69 -> print(f"Newly linked: {linked}")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:72 -> print("\nDistribution by campaign:")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:83 -> print(f"  {campaign_name}: {count} subscriptions")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:85 -> print("\n" + "=" * 70)
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:86 -> print("ETL Complete!")
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:87 -> print("=" * 70)
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py:91 -> print(f"\nError during ETL: {e}")
- user-analytics-backend/scripts/etl/seed_campaigns.py:295 -> print("\n" + "="*78)
- user-analytics-backend/scripts/etl/seed_campaigns.py:296 -> print(f"  {'Nom':<40} {'Type':<14} {'Subs':>8}  Envoi")
- user-analytics-backend/scripts/etl/seed_campaigns.py:297 -> print("-"*78)
- user-analytics-backend/scripts/etl/seed_campaigns.py:299 -> print(f"  {r.name:<40} {r.campaign_type:<14} {r.sub_count:>8,}  {r.send_date}")
- user-analytics-backend/scripts/etl/seed_campaigns.py:300 -> print("-"*78)
- user-analytics-backend/scripts/etl/seed_campaigns.py:302 -> print(f"  Assignées : {assigned:,} / {total:,}  ({pct}%)")
- user-analytics-backend/scripts/etl/seed_campaigns.py:303 -> print("="*78 + "\n")
- user-analytics-backend/scripts/etl/seed_campaigns.py:329 -> sample_send=str(campaigns[0]["send_datetime"]))      # ← debug visible
- user-analytics-backend/scripts/seeder/seed_missing_data.py:48 -> print(json.dumps(payload, ensure_ascii=True))
- user-analytics-backend/scripts/verify_data.py:37 -> print("== VERIFY PROD DB ==")
- user-analytics-backend/scripts/verify_data.py:47 -> print(f"PROD transaction_histories: total={int(row.total or 0)} range={row.min_d} -> {row.max_d}")
- user-analytics-backend/scripts/verify_data.py:49 -> print("\n== VERIFY ANALYTICS DB ==")
- user-analytics-backend/scripts/verify_data.py:55 -> print(f"ANALYTICS {table}: {int(count or 0)} rows")
- user-analytics-backend/scripts/verify_data.py:58 -> print(f"ANALYTICS {table}: ERROR - {exc}")
- user-analytics-backend/scripts/verify_data.py:69 -> print(f"ANALYTICS billing_events with {DATA_START_DATE} filter: {int(filtered_count or 0)} rows")
- user-analytics-backend/scripts/verify_data.py:73 -> print("WARNING: analytics_db appears empty for the real date window; rerun ETL.")
- user-analytics-backend/scripts/verify_data.py:75 -> print("OK: analytics_db is populated for the expected data window.")

## 12. Missing / Not Yet Implemented
- tmp/generate_project_report.py: NotImplementedError present
- tmp/generate_project_report.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/alembic/versions/3939f80c5a66_seeders.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/alembic/versions/3939f80c5a66_seeders.py: pass statement found
- user-analytics-backend/alembic/versions/8ce268d4732a_initial_migration.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/alembic/versions/8ce268d4732a_initial_migration.py: pass statement found
- user-analytics-backend/alembic/versions/dff7e0993f3d_initial_migration1.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/alembic/versions/dff7e0993f3d_initial_migration1.py: pass statement found
- user-analytics-backend/app/schemas/BillingEvent.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/BillingEvent.py: pass statement found
- user-analytics-backend/app/schemas/Campaigns.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/Campaigns.py: pass statement found
- user-analytics-backend/app/schemas/Cohorts.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/Cohorts.py: pass statement found
- user-analytics-backend/app/schemas/Services.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/Services.py: pass statement found
- user-analytics-backend/app/schemas/ServicesTypes.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/ServicesTypes.py: pass statement found
- user-analytics-backend/app/schemas/SmsEvents.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/SmsEvents.py: pass statement found
- user-analytics-backend/app/schemas/Subscriptions.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/Subscriptions.py: pass statement found
- user-analytics-backend/app/schemas/Unsubscriptions.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/Unsubscriptions.py: pass statement found
- user-analytics-backend/app/schemas/UserActivities.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/app/schemas/UserActivities.py: pass statement found
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/scripts/etl/fix_services_mapping.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/scripts/seeder/seed_missing_data.py: contains TODO/FIXME/pass/NotImplemented/empty return pattern
- user-analytics-backend/scripts/seeder/seed_missing_data.py: pass statement found

## 13. Overall Advancement Summary
| Module | Estimated Completion |
|---|---:|
| ETL module | 66% |
| Backend API | 100% |
| Frontend | 13% |
| Auth system | 100% |
| Tests | 0% |
| Documentation | 100% |

## Appendix: File Inventory
- .agents/skills/supabase-postgres-best-practices/AGENTS.md
- .agents/skills/supabase-postgres-best-practices/CLAUDE.md
- .agents/skills/supabase-postgres-best-practices/README.md
- .agents/skills/supabase-postgres-best-practices/references/_contributing.md
- .agents/skills/supabase-postgres-best-practices/references/_sections.md
- .agents/skills/supabase-postgres-best-practices/references/_template.md
- .agents/skills/supabase-postgres-best-practices/references/advanced-full-text-search.md
- .agents/skills/supabase-postgres-best-practices/references/advanced-jsonb-indexing.md
- .agents/skills/supabase-postgres-best-practices/references/conn-idle-timeout.md
- .agents/skills/supabase-postgres-best-practices/references/conn-limits.md
- .agents/skills/supabase-postgres-best-practices/references/conn-pooling.md
- .agents/skills/supabase-postgres-best-practices/references/conn-prepared-statements.md
- .agents/skills/supabase-postgres-best-practices/references/data-batch-inserts.md
- .agents/skills/supabase-postgres-best-practices/references/data-n-plus-one.md
- .agents/skills/supabase-postgres-best-practices/references/data-pagination.md
- .agents/skills/supabase-postgres-best-practices/references/data-upsert.md
- .agents/skills/supabase-postgres-best-practices/references/lock-advisory.md
- .agents/skills/supabase-postgres-best-practices/references/lock-deadlock-prevention.md
- .agents/skills/supabase-postgres-best-practices/references/lock-short-transactions.md
- .agents/skills/supabase-postgres-best-practices/references/lock-skip-locked.md
- .agents/skills/supabase-postgres-best-practices/references/monitor-explain-analyze.md
- .agents/skills/supabase-postgres-best-practices/references/monitor-pg-stat-statements.md
- .agents/skills/supabase-postgres-best-practices/references/monitor-vacuum-analyze.md
- .agents/skills/supabase-postgres-best-practices/references/query-composite-indexes.md
- .agents/skills/supabase-postgres-best-practices/references/query-covering-indexes.md
- .agents/skills/supabase-postgres-best-practices/references/query-index-types.md
- .agents/skills/supabase-postgres-best-practices/references/query-missing-indexes.md
- .agents/skills/supabase-postgres-best-practices/references/query-partial-indexes.md
- .agents/skills/supabase-postgres-best-practices/references/schema-constraints.md
- .agents/skills/supabase-postgres-best-practices/references/schema-data-types.md
- .agents/skills/supabase-postgres-best-practices/references/schema-foreign-key-indexes.md
- .agents/skills/supabase-postgres-best-practices/references/schema-lowercase-identifiers.md
- .agents/skills/supabase-postgres-best-practices/references/schema-partitioning.md
- .agents/skills/supabase-postgres-best-practices/references/schema-primary-keys.md
- .agents/skills/supabase-postgres-best-practices/references/security-privileges.md
- .agents/skills/supabase-postgres-best-practices/references/security-rls-basics.md
- .agents/skills/supabase-postgres-best-practices/references/security-rls-performance.md
- .agents/skills/supabase-postgres-best-practices/SKILL.md
- .env
- .gitignore
- .gitignore.bak.20260328_115606
- .report_all_files.txt
- .vscode/settings.json
- analytics-platform-front/.dockerignore
- analytics-platform-front/.env.example
- analytics-platform-front/.gitignore
- analytics-platform-front/Dockerfile
- analytics-platform-front/eslint.config.js
- analytics-platform-front/index.html
- analytics-platform-front/package-lock.json
- analytics-platform-front/package.json
- analytics-platform-front/postcss.config.js
- analytics-platform-front/public/digmaco.png
- analytics-platform-front/README.md
- analytics-platform-front/src/App.css
- analytics-platform-front/src/App.jsx
- analytics-platform-front/src/assets/digmaco.png
- analytics-platform-front/src/assets/react.svg
- analytics-platform-front/src/components/admin/management/CampaignModal.jsx
- analytics-platform-front/src/components/admin/management/CampaignTable.jsx
- analytics-platform-front/src/components/admin/management/DeleteConfirmModal.jsx
- analytics-platform-front/src/components/admin/management/ServiceModal.jsx
- analytics-platform-front/src/components/admin/management/ServiceTable.jsx
- analytics-platform-front/src/components/dashboard/BIInsightsPanel.jsx
- analytics-platform-front/src/components/dashboard/campaign/CampaignFunnelChart.jsx
- analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx
- analytics-platform-front/src/components/dashboard/campaign/CampaignVsOrganicChart.jsx
- analytics-platform-front/src/components/dashboard/campaign/ServiceCampaignComparison.jsx
- analytics-platform-front/src/components/dashboard/churn/ChartContainer.jsx
- analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx
- analytics-platform-front/src/components/dashboard/churn/ChurnReasonsChart.jsx
- analytics-platform-front/src/components/dashboard/churn/RiskSegmentsPanel.jsx
- analytics-platform-front/src/components/dashboard/churn/TimeToChurnChart.jsx
- analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx
- analytics-platform-front/src/components/dashboard/ChurnPieChart.jsx
- analytics-platform-front/src/components/dashboard/EngagementHealthPanel.jsx
- analytics-platform-front/src/components/dashboard/FilterBar.jsx
- analytics-platform-front/src/components/dashboard/KPICard.jsx
- analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx
- analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx
- analytics-platform-front/src/components/dashboard/retention/CohortHeatmap.jsx
- analytics-platform-front/src/components/dashboard/retention/RetentionCurve.jsx
- analytics-platform-front/src/components/dashboard/retention/ServiceRetentionRadar.jsx
- analytics-platform-front/src/components/dashboard/SubscriptionDonutChart.jsx
- analytics-platform-front/src/components/dashboard/TabNavigation.jsx
- analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx
- analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx
- analytics-platform-front/src/components/dashboard/tabs/RevenueTab.jsx
- analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx
- analytics-platform-front/src/components/dashboard/TopServicesTable.jsx
- analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx
- analytics-platform-front/src/components/dashboard/userActivity/ActivityHeatmap.jsx
- analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx
- analytics-platform-front/src/components/dashboard/userActivity/InactivityAnalysis.jsx
- analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx
- analytics-platform-front/src/components/dashboard/userActivity/UserGrowthChart.jsx
- analytics-platform-front/src/components/directory/Directory.jsx
- analytics-platform-front/src/components/layout/AppLayout.jsx
- analytics-platform-front/src/components/layout/Footer.jsx
- analytics-platform-front/src/components/layout/navConfig.js
- analytics-platform-front/src/components/layout/Sidebar.jsx
- analytics-platform-front/src/components/layout/SidebarNavItem.jsx
- analytics-platform-front/src/components/layout/SidebarSection.jsx
- analytics-platform-front/src/components/layout/Topbar.jsx
- analytics-platform-front/src/components/platform-users/ConfirmDeleteModal.jsx
- analytics-platform-front/src/components/platform-users/CreateUserModal.jsx
- analytics-platform-front/src/components/platform-users/EditUserModal.jsx
- analytics-platform-front/src/components/platform-users/UserFilters.jsx
- analytics-platform-front/src/components/platform-users/UserKPICards.jsx
- analytics-platform-front/src/components/platform-users/UserTable.jsx
- analytics-platform-front/src/components/subscribers/UserRowDetail.jsx
- analytics-platform-front/src/constants/dateFilters.js
- analytics-platform-front/src/context/AuthContext.jsx
- analytics-platform-front/src/hooks/useCampaignComparison.js
- analytics-platform-front/src/hooks/useCampaignImpactDashboard.js
- analytics-platform-front/src/hooks/useCampaignKPIs.js
- analytics-platform-front/src/hooks/useCampaignPerformance.js
- analytics-platform-front/src/hooks/useCampaignTimeline.js
- analytics-platform-front/src/hooks/useChurnBreakdown.js
- analytics-platform-front/src/hooks/useChurnCurve.js
- analytics-platform-front/src/hooks/useChurnDashboard.js
- analytics-platform-front/src/hooks/useChurnKPIs.js
- analytics-platform-front/src/hooks/useChurnPredictionMetrics.js
- analytics-platform-front/src/hooks/useChurnPredictionScores.js
- analytics-platform-front/src/hooks/useChurnPredictionTrain.js
- analytics-platform-front/src/hooks/useChurnReasons.js
- analytics-platform-front/src/hooks/useCohortsTable.js
- analytics-platform-front/src/hooks/useCrossService.js
- analytics-platform-front/src/hooks/useDashboardMetrics.js
- analytics-platform-front/src/hooks/useImportData.js
- analytics-platform-front/src/hooks/useManagement.js
- analytics-platform-front/src/hooks/useRetentionCurve.js
- analytics-platform-front/src/hooks/useRetentionHeatmap.js
- analytics-platform-front/src/hooks/useRetentionKPIs.js
- analytics-platform-front/src/hooks/useRiskSegments.js
- analytics-platform-front/src/hooks/useTimeToChurn.js
- analytics-platform-front/src/hooks/useToast.jsx
- analytics-platform-front/src/hooks/useTrialDropoffByDay.js
- analytics-platform-front/src/hooks/useTrialKPIs.js
- analytics-platform-front/src/hooks/useTrialUsers.js
- analytics-platform-front/src/hooks/useUserActivity.js
- analytics-platform-front/src/hooks/useUsers.js
- analytics-platform-front/src/index.css
- analytics-platform-front/src/main.jsx
- analytics-platform-front/src/pages/admin/ImportDataPage.jsx
- analytics-platform-front/src/pages/admin/ManagementPage.jsx
- analytics-platform-front/src/pages/auth/LoginPage.jsx
- analytics-platform-front/src/pages/Dashboard.jsx
- analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx
- analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx
- analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx
- analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx
- analytics-platform-front/src/pages/dashboard/DashboardPage.jsx
- analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx
- analytics-platform-front/src/pages/dashboard/RetentionPage.jsx
- analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx
- analytics-platform-front/src/pages/RootRedirect.jsx
- analytics-platform-front/src/pages/SubscribersPage.jsx
- analytics-platform-front/src/pages/UserActivityPage.jsx
- analytics-platform-front/src/router/AdminRoute.jsx
- analytics-platform-front/src/router/PrivateRoute.jsx
- analytics-platform-front/src/services/api.js
- analytics-platform-front/src/utils/apiError.js
- analytics-platform-front/tailwind.config.js
- analytics-platform-front/vite.config.js
- docker-compose.yml
- docs/architecture.md
- docs/Digital Campaign Objectives & Service Overview.pdf
- docs/etl_prod_readme.md
- docs/kpis.md
- docs/ml_churn_report.md
- docs/Project 1 _ User Behavior Analytics & Insights Platform.pdf
- docs/Rapport_Avancement_PFE.pdf
- docs/REAL_DATA_INTEGRATION.md
- docs/tmp/generate_rapport.py
- docs/tmp/pdfs/cahier_charges_extract.txt
- docs/tmp/pdfs/rapport_avancement_extract.txt
- docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-23_p1.png
- docs/tmp/pdfs/Rapport_Avancement_PFE_2026-03-24.pdf
- docs/TRIAL_INTEGRATION_SUMMARY.md
- mcp.json
- reorganize_project.py
- reorganize_report.json
- reorganize_report_apply.json
- skills-lock.json
- tmp/generate_project_report.py
- user-analytics-backend/.dockerignore
- user-analytics-backend/.env
- user-analytics-backend/.env.example
- user-analytics-backend/alembic.ini
- user-analytics-backend/alembic/env.py
- user-analytics-backend/alembic/README
- user-analytics-backend/alembic/script.py.mako
- user-analytics-backend/alembic/versions/3939f80c5a66_seeders.py
- user-analytics-backend/alembic/versions/6c076db13bed_add_analytics_performance_indexes.py
- user-analytics-backend/alembic/versions/8ce268d4732a_initial_migration.py
- user-analytics-backend/alembic/versions/ded5564102c8_initial_migration3.py
- user-analytics-backend/alembic/versions/dff7e0993f3d_initial_migration1.py
- user-analytics-backend/app/__init__.py
- user-analytics-backend/app/api/__init__.py
- user-analytics-backend/app/api/v1/__init__.py
- user-analytics-backend/app/core/__init__.py
- user-analytics-backend/app/core/config.py
- user-analytics-backend/app/core/database.py
- user-analytics-backend/app/core/date_ranges.py
- user-analytics-backend/app/core/dependencies.py
- user-analytics-backend/app/core/security.py
- user-analytics-backend/app/main.py
- user-analytics-backend/app/models/__init__.py
- user-analytics-backend/app/models/analytics.py
- user-analytics-backend/app/models/billing_events.py
- user-analytics-backend/app/models/campaigns.py
- user-analytics-backend/app/models/cohorts.py
- user-analytics-backend/app/models/import_logs.py
- user-analytics-backend/app/models/platform_users.py
- user-analytics-backend/app/models/service_types.py
- user-analytics-backend/app/models/services.py
- user-analytics-backend/app/models/sms_events.py
- user-analytics-backend/app/models/subscriptions.py
- user-analytics-backend/app/models/unsubscriptions.py
- user-analytics-backend/app/models/user_activities.py
- user-analytics-backend/app/models/users.py
- user-analytics-backend/app/repositories/__init__.py
- user-analytics-backend/app/repositories/campaign_repo.py
- user-analytics-backend/app/repositories/churn_repo.py
- user-analytics-backend/app/routers/admin_import.py
- user-analytics-backend/app/routers/analyticsOverview.py
- user-analytics-backend/app/routers/auth.py
- user-analytics-backend/app/routers/campaign_impact.py
- user-analytics-backend/app/routers/churn_analysis.py
- user-analytics-backend/app/routers/cross_service.py
- user-analytics-backend/app/routers/management.py
- user-analytics-backend/app/routers/ml_churn.py
- user-analytics-backend/app/routers/platform_user.py
- user-analytics-backend/app/routers/retention.py
- user-analytics-backend/app/routers/service.py
- user-analytics-backend/app/routers/trialAnalytics.py
- user-analytics-backend/app/routers/userActivity.py
- user-analytics-backend/app/routers/users.py
- user-analytics-backend/app/schemas/__init__.py
- user-analytics-backend/app/schemas/auth.py
- user-analytics-backend/app/schemas/BillingEvent.py
- user-analytics-backend/app/schemas/Campaigns.py
- user-analytics-backend/app/schemas/churn_analysis.py
- user-analytics-backend/app/schemas/Cohorts.py
- user-analytics-backend/app/schemas/ml_churn.py
- user-analytics-backend/app/schemas/platform_user_schemas.py
- user-analytics-backend/app/schemas/Services.py
- user-analytics-backend/app/schemas/ServicesTypes.py
- user-analytics-backend/app/schemas/SmsEvents.py
- user-analytics-backend/app/schemas/Subscriptions.py
- user-analytics-backend/app/schemas/Unsubscriptions.py
- user-analytics-backend/app/schemas/UserActivities.py
- user-analytics-backend/app/schemas/users.py
- user-analytics-backend/app/services/__init__.py
- user-analytics-backend/app/services/campaign_service.py
- user-analytics-backend/app/services/churn_service.py
- user-analytics-backend/app/services/platform_user_service.py
- user-analytics-backend/app/utils/__init__.py
- user-analytics-backend/app/utils/temporal.py
- user-analytics-backend/Dockerfile
- user-analytics-backend/logs/.gitkeep
- user-analytics-backend/Makefile
- user-analytics-backend/migrations/create_import_logs.sql
- user-analytics-backend/ml_models/__init__.py
- user-analytics-backend/ml_models/churn_metrics.joblib
- user-analytics-backend/ml_models/churn_model.joblib
- user-analytics-backend/ml_models/churn_predictor.py
- user-analytics-backend/note.txt
- user-analytics-backend/pyproject.toml
- user-analytics-backend/README.md
- user-analytics-backend/requirements.txt
- user-analytics-backend/scripts/compute_cohorts.py
- user-analytics-backend/scripts/etl/__init__.py
- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
- user-analytics-backend/scripts/etl/fix_services_mapping.py
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
- user-analytics-backend/scripts/etl/recalcul_cohorts.py
- user-analytics-backend/scripts/etl/seed_campaigns.py
- user-analytics-backend/scripts/seeder/__init__.py
- user-analytics-backend/scripts/seeder/seed_missing_data.py
- user-analytics-backend/scripts/sql/diagnostics.sql
- user-analytics-backend/scripts/verify_data.py
- user-analytics-backend/tests/__init__.py