# DigMaco Analytics Activity Report

## 1. Project Overview
- Project name: DigMaco Analytics
- Tech stack detected:
  - Backend: FastAPI >=0.111.0, SQLAlchemy >=2.0, Alembic >=1.13, Pydantic >=2.7, python-jose, Redis >=5.2, psycopg2-binary
  - Frontend: React 19.2, Vite 7.3.1, React Router 7.13.1, React Query 5.96, Tailwind 3.4.19, MUI 7.3.9, Recharts 3.8, Axios 1.13.6
  - Database: PostgreSQL (from DATABASE_URL)
- Total number of API endpoints found: 101 (includes root /)
- Total number of pages/components found: 23 pages, 62 components
- Roles identified in codebase: admin, analyst, viewer

## 2. Role: ADMIN - Full Activity Report

### 2.1 Accessible Pages
- Dashboard - /dashboard, /dashboard-1 - main KPI overview and insights
- User Activity - /analytics/behaviors - engagement analytics and activity KPIs
- Free Trial Behavior - /analytics/trial - trial KPIs, dropoff, and trial user list
- Retention - /analytics/retention - cohort heatmap, curve, and recompute (admin action)
- Campaign Impact - /analytics/campaigns - campaign dashboard and list
- Churn Analysis - /analytics/churn - churn KPIs, trends, and reactivation
- Churn Prediction - /analytics/churn-prediction - ML churn scoring dashboard
- Cross-Service - /analytics/cross-service - multi-service behavior insights
- User Segmentation - /analytics/segmentation - segmentation KPIs and clusters
- Anomaly Detection - /analytics/anomalies - anomaly timeline and detection
- Subscribers - /management/subscribers - subscriber directory and KPIs
- Analyst Notes - /notes - create and manage analyst notes
- Profile Settings - /account/profile - profile, password, avatar
- Admin - Platform Users - /admin/users - invite, edit, deactivate, delete users
- Admin - Import Data - /admin/import - CSV/SQL import flows and history
- Admin - Management - /admin/management - CRUD services and campaigns
- Admin - System Settings - /admin/settings - local settings storage UI

### 2.2 Available Actions
| Feature Module | Actions Available | Endpoint(s) Used |
|---|---|---|
| Auth + Profile | View profile, update profile, upload/delete avatar | GET /auth/me, PATCH /auth/profile, POST /auth/profile/avatar, DELETE /auth/profile/avatar |
| Platform Users | Invite, view, edit, toggle status, change role, delete | POST /auth/invite, GET /platform-users/, GET /platform-users/{id}, PUT /platform-users/{id}, PATCH /platform-users/{id}/status, PATCH /platform-users/{id}/role, DELETE /platform-users/{id} |
| Services | List, create, update, deactivate | GET /admin/management/services, POST /admin/management/services, PUT /admin/management/services/{service_id}, DELETE /admin/management/services/{service_id} |
| Campaigns | List, create, update, delete | GET /admin/management/campaigns, POST /admin/management/campaigns, PUT /admin/management/campaigns/{campaign_id}, DELETE /admin/management/campaigns/{campaign_id} |
| Campaign Targets | Upload targets file | POST /admin/management/campaigns/upload-targets |
| Admin Import | Stage CSV, confirm CSV, import SQL, history, schema, templates | POST /admin/import/csv, POST /admin/import/csv/confirm, POST /admin/import/database, GET /admin/import/history, GET /admin/import/schema/{table}, GET /admin/import/template/{table} |
| Analytics Overview | View summary and overview | GET /analytics/summary, GET /analytics/overview |
| Analytics Diagnostics | View status diagnostics | GET /analytics/status/diagnostics |
| Cache Control | Invalidate analytics cache | POST /analytics/cache/invalidate |
| User Activity | View KPIs and trends | GET /analytics/user-activity |
| Trial Analytics | KPIs, timeline, by-service, users, dropoff by day, dropoff causes | GET /analytics/trial/kpis, /trial/timeline, /trial/by-service, /trial/users, /trial/dropoff-by-day, /trial/dropoff-causes |
| Retention | KPIs, heatmap, curve, cohorts list, recompute | GET /analytics/retention/kpis, /retention/heatmap, /retention/curve, /retention/cohorts-list, POST /analytics/retention/recompute |
| Campaign Impact | Dashboard, list, overview, by-type, top, trend, kpis, performance, comparison, timeline | GET /analytics/campaigns/* |
| Churn Analytics | Dashboard, KPIs, trend, by-service, lifetime, retention, reactivation | GET /analytics/churn/* |
| Cross-Service | Overview, co-subscriptions, migrations, distribution, all | GET /analytics/cross-service/* |
| Segmentation | KPIs, clusters, profiles, train | GET /analytics/segmentation/kpis, /clusters, /profiles, POST /analytics/segmentation/train |
| Anomalies | Summary, timeline, distribution, heatmap, details, insights, run detection | GET /anomalies/*, POST /anomalies/run-detection |
| ML Churn | Train model, view metrics, governance, scores, recompute scores | POST /ml/churn/train, GET /ml/churn/metrics, /ml/churn/governance, /ml/churn/scores, POST /ml/churn/scores/recompute |
| Analyst Notes | CRUD notes, context lookup | POST /notes, GET /notes, GET /notes/{id}, PUT /notes/{id}, DELETE /notes/{id}, GET /notes/context |
| NRR | View NRR KPI | GET /analytics/nrr |

### 2.3 Restricted Actions
- Admin cannot register via /auth/register (invite-only; 403 enforced)
- Admin cannot self-deactivate, self-delete, or change own role (service guards)

### 2.4 Admin-specific API Endpoints
- POST /auth/invite
- GET /analytics/status/diagnostics
- POST /analytics/cache/invalidate
- POST /analytics/retention/recompute
- POST /ml/churn/train
- POST /ml/churn/scores/recompute
- POST /admin/import/csv
- POST /admin/import/csv/confirm
- POST /admin/import/database
- GET /admin/import/history
- GET /admin/import/schema/{table}
- GET /admin/import/template/{table}
- GET /admin/management/services
- POST /admin/management/services
- PUT /admin/management/services/{service_id}
- DELETE /admin/management/services/{service_id}
- GET /admin/management/campaigns
- POST /admin/management/campaigns
- PUT /admin/management/campaigns/{campaign_id}
- DELETE /admin/management/campaigns/{campaign_id}
- POST /admin/management/campaigns/upload-targets
- GET /platform-users/
- GET /platform-users/{user_id}
- POST /platform-users/
- PUT /platform-users/{user_id}
- PATCH /platform-users/{user_id}/status
- PATCH /platform-users/{user_id}/role
- DELETE /platform-users/{user_id}

## 3. Role: ANALYST - Full Activity Report

### 3.1 Accessible Pages
- Dashboard - /dashboard, /dashboard-1 - main KPI overview and insights
- User Activity - /analytics/behaviors - engagement analytics and activity KPIs
- Free Trial Behavior - /analytics/trial - trial KPIs, dropoff, and trial user list
- Retention - /analytics/retention - cohort heatmap and curve
- Campaign Impact - /analytics/campaigns - campaign dashboard and list
- Churn Analysis - /analytics/churn - churn KPIs, trends, and reactivation
- Churn Prediction - /analytics/churn-prediction - ML churn scoring dashboard
- Cross-Service - /analytics/cross-service - multi-service behavior insights
- User Segmentation - /analytics/segmentation - segmentation KPIs and clusters
- Anomaly Detection - /analytics/anomalies - anomaly timeline and detection
- Subscribers - /management/subscribers - subscriber directory and KPIs
- Analyst Notes - /notes - create and manage own notes
- Profile Settings - /account/profile - profile, password, avatar

### 3.2 Available Actions
| Feature Module | Actions Available | Endpoint(s) Used |
|---|---|---|
| Auth + Profile | View profile, update profile, upload/delete avatar | GET /auth/me, PATCH /auth/profile, POST /auth/profile/avatar, DELETE /auth/profile/avatar |
| Dashboards | View overview KPIs and NRR | GET /analytics/overview, GET /analytics/nrr |
| User Activity | View KPIs, trends, heatmaps | GET /analytics/user-activity |
| Trial Analytics | KPIs, timeline, users, dropoff by day/causes | GET /analytics/trial/kpis, /trial/timeline, /trial/users, /trial/dropoff-by-day, /trial/dropoff-causes |
| Retention | KPIs, heatmap, curve, cohorts list | GET /analytics/retention/kpis, /retention/heatmap, /retention/curve, /retention/cohorts-list |
| Campaign Impact | Dashboard, list, overview, by-type, top, trend, kpis, performance, comparison, timeline | GET /analytics/campaigns/* |
| Churn Analytics | Dashboard, KPIs, trend, by-service, lifetime, retention, reactivation | GET /analytics/churn/* |
| Cross-Service | Overview, co-subscriptions, migrations, distribution, all | GET /analytics/cross-service/* |
| Segmentation | KPIs, clusters, profiles, train | GET /analytics/segmentation/kpis, /clusters, /profiles, POST /analytics/segmentation/train |
| Anomalies | Summary, timeline, distribution, heatmap, details, insights, run detection | GET /anomalies/*, POST /anomalies/run-detection |
| Analyst Notes | Create, read, update, delete own notes, context lookup | POST /notes, GET /notes, GET /notes/{id}, PUT /notes/{id}, DELETE /notes/{id}, GET /notes/context |
| Campaigns (read-only) | Service list and campaign list for filters | GET /services, GET /analytics/campaigns/list |

### 3.3 Restricted Actions
- Cannot access any /admin/* pages or endpoints
- Cannot invite users or manage platform users
- Cannot create, update, or delete services/campaigns
- Cannot upload campaign targets
- Cannot import CSV/SQL or download import templates
- Cannot recompute retention cohorts
- Cannot invalidate analytics cache or view diagnostics
- Cannot train churn model or recompute churn scores
- Analyst Notes: cannot view or edit other analysts' notes (enforced in note_service)

### 3.4 Analyst-specific API Endpoints
Analysts can access all endpoints that do not require require_admin. This includes:
- Auth profile: GET /auth/me, PATCH /auth/profile, POST /auth/profile/avatar, DELETE /auth/profile/avatar
- Public auth flows: POST /auth/login, POST /auth/register-invite, POST /auth/forgot-password, POST /auth/verify-reset-token, POST /auth/reset-password, POST /auth/register (returns 403)
- Analytics overview: GET /analytics/summary, GET /analytics/overview
- Users: GET /users, GET /users/trial, GET /users/{user_id}
- Services: GET /services
- User activity: GET /analytics/user-activity
- Trial analytics: GET /analytics/trial/kpis, /trial/timeline, /trial/by-service, /trial/users, /trial/dropoff-by-day, /trial/dropoff-causes
- Campaign impact: GET /analytics/campaigns/dashboard, /list, /overview, /by-type, /top, /trend, /kpis, /performance, /comparison, /timeline
- Churn analytics: GET /analytics/churn/dashboard, /kpis, /trend, /by-service, /lifetime, /retention, /reactivation/kpis, /reactivation/by-service, /breakdown
- Cross-service: GET /analytics/cross-service/overview, /co-subscriptions, /migrations, /distribution, /all
- Segmentation: GET /analytics/segmentation/kpis, /clusters, /profiles, POST /analytics/segmentation/train
- Anomalies: GET /anomalies/summary, /timeline, /distribution, /heatmap, /details, /insights; POST /anomalies/run-detection
- ML churn (read-only): GET /ml/churn/metrics, /governance, /scores
- NRR: GET /analytics/nrr
- Notes: POST /notes, GET /notes, GET /notes/{id}, PUT /notes/{id}, DELETE /notes/{id}, GET /notes/context
- Root: GET /

## 4. Shared Features (Both Roles)
- Analytics overview and NRR: GET /analytics/overview, GET /analytics/nrr
- Engagement and user activity: GET /analytics/user-activity
- Trial analytics: GET /analytics/trial/*
- Retention analytics (read-only): GET /analytics/retention/kpis, /retention/heatmap, /retention/curve, /retention/cohorts-list
- Campaign impact dashboard: GET /analytics/campaigns/*
- Churn analytics: GET /analytics/churn/* (except admin-only ML training)
- Cross-service analytics: GET /analytics/cross-service/*
- Segmentation analytics: GET /analytics/segmentation/kpis, /clusters, /profiles, POST /analytics/segmentation/train
- Anomaly detection: GET /anomalies/*, POST /anomalies/run-detection
- Analyst notes: /notes (role-scoped in service)
- Profile management: /auth/me, /auth/profile, /auth/profile/avatar

## 5. Access Control Matrix
| Feature / Action | Admin | Analyst |
|---|---|---|
| Trigger ETL pipeline | Not found | Not found |
| View ETL logs | Not found | Not found |
| Manage users | Yes | No |
| Assign roles | Yes | No |
| Manage services & campaigns | Yes | No |
| Upload campaign targets | Yes | No |
| Import CSV/SQL data | Yes | No |
| Recompute retention cohorts | Yes | No |
| Invalidate analytics cache | Yes | No |
| View status diagnostics | Yes | No |
| View all analyst notes | Yes | No (own only) |
| View own notes | Yes | Yes |
| Create analyst notes | Yes | Yes |
| Edit own notes | Yes | Yes |
| Edit any note | Yes | No |
| Delete any note | Yes | No |
| View dashboards | Yes | Yes |
| Access AI modules (anomalies, segmentation, churn prediction) | Yes | Yes |
| Train churn model | Yes | No |
| Recompute churn scores | Yes | No |
| Generate PDF reports | Not found | Not found |

## 6. Unprotected Endpoints (Security Audit)
| Method | Path | File | Risk Level |
|---|---|---|---|
| GET | / | [user-analytics-backend/app/main.py](user-analytics-backend/app/main.py) | Low |
| GET | /services | [user-analytics-backend/app/routers/service.py](user-analytics-backend/app/routers/service.py) | Medium |
| GET | /users | [user-analytics-backend/app/routers/users.py](user-analytics-backend/app/routers/users.py) | High |
| GET | /users/trial | [user-analytics-backend/app/routers/users.py](user-analytics-backend/app/routers/users.py) | High |
| GET | /users/{user_id} | [user-analytics-backend/app/routers/users.py](user-analytics-backend/app/routers/users.py) | High |
| GET | /analytics/summary | [user-analytics-backend/app/routers/analyticsOverview.py](user-analytics-backend/app/routers/analyticsOverview.py) | Medium |
| GET | /analytics/overview | [user-analytics-backend/app/routers/analyticsOverview.py](user-analytics-backend/app/routers/analyticsOverview.py) | Medium |
| GET | /analytics/user-activity | [user-analytics-backend/app/routers/userActivity.py](user-analytics-backend/app/routers/userActivity.py) | Medium |
| GET | /analytics/trial/kpis | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Medium |
| GET | /analytics/trial/timeline | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Medium |
| GET | /analytics/trial/by-service | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Medium |
| GET | /analytics/trial/users | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | High |
| GET | /analytics/trial/dropoff-by-day | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Medium |
| GET | /analytics/trial/dropoff-causes | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Medium |
| GET | /analytics/churn/breakdown | [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Medium |
| GET | /analytics/retention/kpis | [user-analytics-backend/app/routers/retention.py](user-analytics-backend/app/routers/retention.py) | Medium |
| GET | /analytics/retention/heatmap | [user-analytics-backend/app/routers/retention.py](user-analytics-backend/app/routers/retention.py) | Medium |
| GET | /analytics/retention/curve | [user-analytics-backend/app/routers/retention.py](user-analytics-backend/app/routers/retention.py) | Medium |
| GET | /analytics/retention/cohorts-list | [user-analytics-backend/app/routers/retention.py](user-analytics-backend/app/routers/retention.py) | Medium |
| GET | /analytics/campaigns/kpis | [user-analytics-backend/app/routers/campaign_impact.py](user-analytics-backend/app/routers/campaign_impact.py) | Medium |
| GET | /analytics/campaigns/performance | [user-analytics-backend/app/routers/campaign_impact.py](user-analytics-backend/app/routers/campaign_impact.py) | Medium |
| GET | /analytics/campaigns/comparison | [user-analytics-backend/app/routers/campaign_impact.py](user-analytics-backend/app/routers/campaign_impact.py) | Medium |
| GET | /analytics/campaigns/timeline | [user-analytics-backend/app/routers/campaign_impact.py](user-analytics-backend/app/routers/campaign_impact.py) | Medium |
| GET | /analytics/churn/dashboard | [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Medium |
| GET | /analytics/churn/kpis | [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Medium |
| GET | /analytics/churn/trend | [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Medium |
| GET | /analytics/churn/by-service | [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Medium |
| GET | /analytics/churn/lifetime | [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Medium |
| GET | /analytics/churn/retention | [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Medium |
| GET | /analytics/cross-service/overview | [user-analytics-backend/app/routers/cross_service.py](user-analytics-backend/app/routers/cross_service.py) | Medium |
| GET | /analytics/cross-service/co-subscriptions | [user-analytics-backend/app/routers/cross_service.py](user-analytics-backend/app/routers/cross_service.py) | Medium |
| GET | /analytics/cross-service/migrations | [user-analytics-backend/app/routers/cross_service.py](user-analytics-backend/app/routers/cross_service.py) | Medium |
| GET | /analytics/cross-service/distribution | [user-analytics-backend/app/routers/cross_service.py](user-analytics-backend/app/routers/cross_service.py) | Medium |
| GET | /analytics/cross-service/all | [user-analytics-backend/app/routers/cross_service.py](user-analytics-backend/app/routers/cross_service.py) | Medium |
| GET | /analytics/segmentation/kpis | [user-analytics-backend/app/routers/segmentation.py](user-analytics-backend/app/routers/segmentation.py) | Medium |
| GET | /analytics/segmentation/clusters | [user-analytics-backend/app/routers/segmentation.py](user-analytics-backend/app/routers/segmentation.py) | Medium |
| GET | /analytics/segmentation/profiles | [user-analytics-backend/app/routers/segmentation.py](user-analytics-backend/app/routers/segmentation.py) | Medium |
| POST | /analytics/segmentation/train | [user-analytics-backend/app/routers/segmentation.py](user-analytics-backend/app/routers/segmentation.py) | Medium |
| GET | /anomalies/summary | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| GET | /anomalies/timeline | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| GET | /anomalies/distribution | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| GET | /anomalies/heatmap | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| GET | /anomalies/details | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| GET | /anomalies/insights | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| POST | /anomalies/run-detection | [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Medium |
| GET | /ml/churn/metrics | [user-analytics-backend/app/routers/ml_churn.py](user-analytics-backend/app/routers/ml_churn.py) | Medium |
| GET | /ml/churn/governance | [user-analytics-backend/app/routers/ml_churn.py](user-analytics-backend/app/routers/ml_churn.py) | Medium |
| GET | /ml/churn/scores | [user-analytics-backend/app/routers/ml_churn.py](user-analytics-backend/app/routers/ml_churn.py) | Medium |
| POST | /auth/register | [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Low |
| POST | /auth/register-invite | [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Low |
| POST | /auth/login | [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Low |
| POST | /auth/forgot-password | [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Low |
| POST | /auth/verify-reset-token | [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Low |
| POST | /auth/reset-password | [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Low |

## 7. Missing Features / Gaps Detected
- [PARTIAL] Frontend hooks call missing churn endpoints: /analytics/churn/curve, /analytics/churn/reasons, /analytics/churn/time-to-churn, /analytics/churn/risk-segments (no routers found)
- [PARTIAL] PDF report generation: no backend endpoints or frontend handlers found
- [PARTIAL] Viewer role exists in PlatformUser model but no route-level guards or UI flows for viewer role
- [PARTIAL] System Settings page is localStorage-only (no backend persistence)

## 8. Implementation Summary

### Backend
| File | Purpose |
|---|---|
| [user-analytics-backend/app/main.py](user-analytics-backend/app/main.py) | FastAPI app setup, CORS, router registration, static file mount |
| [user-analytics-backend/app/core/dependencies.py](user-analytics-backend/app/core/dependencies.py) | get_current_user and require_admin guards |
| [user-analytics-backend/app/models/analyst_note.py](user-analytics-backend/app/models/analyst_note.py) | Analyst notes table model |
| [user-analytics-backend/app/models/analytics.py](user-analytics-backend/app/models/analytics.py) | Convenience exports for analytics models |
| [user-analytics-backend/app/models/billing_events.py](user-analytics-backend/app/models/billing_events.py) | BillingEvent model |
| [user-analytics-backend/app/models/campaigns.py](user-analytics-backend/app/models/campaigns.py) | Campaign model |
| [user-analytics-backend/app/models/cohorts.py](user-analytics-backend/app/models/cohorts.py) | Cohort model for retention |
| [user-analytics-backend/app/models/import_logs.py](user-analytics-backend/app/models/import_logs.py) | ImportLog audit model |
| [user-analytics-backend/app/models/platform_users.py](user-analytics-backend/app/models/platform_users.py) | PlatformUser auth model |
| [user-analytics-backend/app/models/platform_user_invites.py](user-analytics-backend/app/models/platform_user_invites.py) | Invitation tokens model |
| [user-analytics-backend/app/models/services.py](user-analytics-backend/app/models/services.py) | Service catalog model |
| [user-analytics-backend/app/models/service_types.py](user-analytics-backend/app/models/service_types.py) | ServiceType pricing/billing model |
| [user-analytics-backend/app/models/sms_events.py](user-analytics-backend/app/models/sms_events.py) | SmsEvent model |
| [user-analytics-backend/app/models/subscriptions.py](user-analytics-backend/app/models/subscriptions.py) | Subscription model |
| [user-analytics-backend/app/models/unsubscriptions.py](user-analytics-backend/app/models/unsubscriptions.py) | Unsubscription/churn model |
| [user-analytics-backend/app/models/users.py](user-analytics-backend/app/models/users.py) | User model |
| [user-analytics-backend/app/models/user_activities.py](user-analytics-backend/app/models/user_activities.py) | UserActivity model |
| [user-analytics-backend/app/models/__init__.py](user-analytics-backend/app/models/__init__.py) | Model registry for Base.metadata |
| [user-analytics-backend/app/routers/auth.py](user-analytics-backend/app/routers/auth.py) | Auth, profile, invites, reset password endpoints |
| [user-analytics-backend/app/routers/users.py](user-analytics-backend/app/routers/users.py) | Users list, trial users, and user detail endpoints |
| [user-analytics-backend/app/routers/service.py](user-analytics-backend/app/routers/service.py) | Service list endpoint |
| [user-analytics-backend/app/routers/analyticsOverview.py](user-analytics-backend/app/routers/analyticsOverview.py) | Overview, summary, diagnostics, cache invalidate endpoints |
| [user-analytics-backend/app/routers/userActivity.py](user-analytics-backend/app/routers/userActivity.py) | User activity analytics endpoint |
| [user-analytics-backend/app/routers/trialAnalytics.py](user-analytics-backend/app/routers/trialAnalytics.py) | Trial analytics endpoints and churn breakdown |
| [user-analytics-backend/app/routers/retention.py](user-analytics-backend/app/routers/retention.py) | Retention KPIs, heatmap, curve, cohorts, recompute |
| [user-analytics-backend/app/routers/campaign_impact.py](user-analytics-backend/app/routers/campaign_impact.py) | Campaign impact endpoints |
| [user-analytics-backend/app/routers/churn_analysis.py](user-analytics-backend/app/routers/churn_analysis.py) | Churn analytics endpoints |
| [user-analytics-backend/app/routers/cross_service.py](user-analytics-backend/app/routers/cross_service.py) | Cross-service analytics endpoints |
| [user-analytics-backend/app/routers/segmentation.py](user-analytics-backend/app/routers/segmentation.py) | Segmentation endpoints |
| [user-analytics-backend/app/routers/anomalies.py](user-analytics-backend/app/routers/anomalies.py) | Anomaly detection endpoints |
| [user-analytics-backend/app/routers/ml_churn.py](user-analytics-backend/app/routers/ml_churn.py) | Churn ML training and scoring endpoints |
| [user-analytics-backend/app/routers/nrr.py](user-analytics-backend/app/routers/nrr.py) | NRR KPI endpoint |
| [user-analytics-backend/app/routers/notes.py](user-analytics-backend/app/routers/notes.py) | Analyst notes CRUD endpoints |
| [user-analytics-backend/app/routers/platform_user.py](user-analytics-backend/app/routers/platform_user.py) | Platform user admin endpoints |
| [user-analytics-backend/app/routers/admin_import.py](user-analytics-backend/app/routers/admin_import.py) | Import CSV/SQL endpoints |
| [user-analytics-backend/app/routers/management.py](user-analytics-backend/app/routers/management.py) | Admin service and campaign management |
| [user-analytics-backend/app/routers/campaign_upload.py](user-analytics-backend/app/routers/campaign_upload.py) | Campaign targets upload endpoint |
| [user-analytics-backend/app/services/business_rules.py](user-analytics-backend/app/services/business_rules.py) | Trial exception rules utilities |
| [user-analytics-backend/app/services/campaign_service.py](user-analytics-backend/app/services/campaign_service.py) | Campaign dashboard/list orchestration |
| [user-analytics-backend/app/services/churn_service.py](user-analytics-backend/app/services/churn_service.py) | Churn dashboard aggregation |
| [user-analytics-backend/app/services/note_service.py](user-analytics-backend/app/services/note_service.py) | Analyst notes CRUD and access control |
| [user-analytics-backend/app/services/nrr_service.py](user-analytics-backend/app/services/nrr_service.py) | NRR service wrapper |
| [user-analytics-backend/app/services/platform_user_service.py](user-analytics-backend/app/services/platform_user_service.py) | Platform user admin logic |
| [user-analytics-backend/app/services/segmentation_service.py](user-analytics-backend/app/services/segmentation_service.py) | Segmentation cache and training logic |

### Frontend
| File | Purpose |
|---|---|
| [analytics-platform-front/src/App.jsx](analytics-platform-front/src/App.jsx) | Route map for public, private, and admin pages |
| [analytics-platform-front/src/router/AdminRoute.jsx](analytics-platform-front/src/router/AdminRoute.jsx) | Admin-only route guard |
| [analytics-platform-front/src/router/PrivateRoute.jsx](analytics-platform-front/src/router/PrivateRoute.jsx) | Authenticated route guard |
| [analytics-platform-front/src/context/AuthContext.jsx](analytics-platform-front/src/context/AuthContext.jsx) | Auth state, login/logout, role helpers |
| [analytics-platform-front/src/pages/Dashboard.jsx](analytics-platform-front/src/pages/Dashboard.jsx) | Basic welcome dashboard |
| [analytics-platform-front/src/pages/RootRedirect.jsx](analytics-platform-front/src/pages/RootRedirect.jsx) | Redirect to login or dashboard |
| [analytics-platform-front/src/pages/SubscribersPage.jsx](analytics-platform-front/src/pages/SubscribersPage.jsx) | Subscriber directory and KPIs |
| [analytics-platform-front/src/pages/UserActivityPage.jsx](analytics-platform-front/src/pages/UserActivityPage.jsx) | User activity analytics page |
| [analytics-platform-front/src/pages/NotesPage.jsx](analytics-platform-front/src/pages/NotesPage.jsx) | Analyst notes management page |
| [analytics-platform-front/src/pages/account/ProfileSettingsPage.jsx](analytics-platform-front/src/pages/account/ProfileSettingsPage.jsx) | Profile, password, and avatar settings |
| [analytics-platform-front/src/pages/admin/ImportDataPage.jsx](analytics-platform-front/src/pages/admin/ImportDataPage.jsx) | Admin import flows UI |
| [analytics-platform-front/src/pages/admin/ManagementPage.jsx](analytics-platform-front/src/pages/admin/ManagementPage.jsx) | Admin service and campaign management |
| [analytics-platform-front/src/pages/admin/SystemSettingsPage.jsx](analytics-platform-front/src/pages/admin/SystemSettingsPage.jsx) | Local-only system settings UI |
| [analytics-platform-front/src/pages/auth/LoginPage.jsx](analytics-platform-front/src/pages/auth/LoginPage.jsx) | Login page |
| [analytics-platform-front/src/pages/auth/RegisterPage.jsx](analytics-platform-front/src/pages/auth/RegisterPage.jsx) | Invite-based registration page |
| [analytics-platform-front/src/pages/auth/ForgotPasswordPage.jsx](analytics-platform-front/src/pages/auth/ForgotPasswordPage.jsx) | Password reset request page |
| [analytics-platform-front/src/pages/auth/ResetPasswordPage.jsx](analytics-platform-front/src/pages/auth/ResetPasswordPage.jsx) | Password reset form |
| [analytics-platform-front/src/pages/dashboard/DashboardPage.jsx](analytics-platform-front/src/pages/dashboard/DashboardPage.jsx) | Overview dashboard with tabs and insights |
| [analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx](analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx) | Trial analytics page |
| [analytics-platform-front/src/pages/dashboard/RetentionPage.jsx](analytics-platform-front/src/pages/dashboard/RetentionPage.jsx) | Retention analytics page |
| [analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx](analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx) | Campaign impact dashboard |
| [analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx](analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx) | Churn analysis dashboard |
| [analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx](analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx) | ML churn prediction dashboard wrapper |
| [analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx](analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx) | Cross-service behavior dashboard |
| [analytics-platform-front/src/pages/dashboard/UserSegmentationPage.jsx](analytics-platform-front/src/pages/dashboard/UserSegmentationPage.jsx) | User segmentation dashboard |
| [analytics-platform-front/src/pages/dashboard/AnomalyDetectionPage.jsx](analytics-platform-front/src/pages/dashboard/AnomalyDetectionPage.jsx) | Anomaly detection dashboard |
| [analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx](analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx) | Admin platform users page |
| [analytics-platform-front/src/components/layout/AppLayout.jsx](analytics-platform-front/src/components/layout/AppLayout.jsx) | App layout wrapper |
| [analytics-platform-front/src/components/layout/Footer.jsx](analytics-platform-front/src/components/layout/Footer.jsx) | Layout footer |
| [analytics-platform-front/src/components/layout/navConfig.js](analytics-platform-front/src/components/layout/navConfig.js) | Sidebar navigation config |
| [analytics-platform-front/src/components/layout/Sidebar.jsx](analytics-platform-front/src/components/layout/Sidebar.jsx) | Sidebar container |
| [analytics-platform-front/src/components/layout/SidebarNavItem.jsx](analytics-platform-front/src/components/layout/SidebarNavItem.jsx) | Sidebar item link |
| [analytics-platform-front/src/components/layout/SidebarSection.jsx](analytics-platform-front/src/components/layout/SidebarSection.jsx) | Sidebar section grouping |
| [analytics-platform-front/src/components/layout/ThemeToggle.jsx](analytics-platform-front/src/components/layout/ThemeToggle.jsx) | Theme toggle button |
| [analytics-platform-front/src/components/layout/Topbar.jsx](analytics-platform-front/src/components/layout/Topbar.jsx) | Top navigation bar |
| [analytics-platform-front/src/components/notes/NotePanel.jsx](analytics-platform-front/src/components/notes/NotePanel.jsx) | Note create/edit panel with global note toggle |
| [analytics-platform-front/src/components/notes/NotesList.jsx](analytics-platform-front/src/components/notes/NotesList.jsx) | Notes table with role-aware columns |
| [analytics-platform-front/src/components/notes/NoteIcon.jsx](analytics-platform-front/src/components/notes/NoteIcon.jsx) | Inline note indicator for charts |
| [analytics-platform-front/src/components/platform-users/ConfirmDeleteModal.jsx](analytics-platform-front/src/components/platform-users/ConfirmDeleteModal.jsx) | Delete confirmation modal |
| [analytics-platform-front/src/components/platform-users/CreateUserModal.jsx](analytics-platform-front/src/components/platform-users/CreateUserModal.jsx) | Create user modal (disabled by backend) |
| [analytics-platform-front/src/components/platform-users/EditUserModal.jsx](analytics-platform-front/src/components/platform-users/EditUserModal.jsx) | Edit user modal |
| [analytics-platform-front/src/components/platform-users/InviteUserModal.jsx](analytics-platform-front/src/components/platform-users/InviteUserModal.jsx) | Invite user modal |
| [analytics-platform-front/src/components/platform-users/UserFilters.jsx](analytics-platform-front/src/components/platform-users/UserFilters.jsx) | Filters for platform users table |
| [analytics-platform-front/src/components/platform-users/UserKPICards.jsx](analytics-platform-front/src/components/platform-users/UserKPICards.jsx) | KPI cards for platform users |
| [analytics-platform-front/src/components/platform-users/UserTable.jsx](analytics-platform-front/src/components/platform-users/UserTable.jsx) | Platform users table |
| [analytics-platform-front/src/components/subscribers/UserListSection.jsx](analytics-platform-front/src/components/subscribers/UserListSection.jsx) | Subscriber list section |
| [analytics-platform-front/src/components/subscribers/UserRowDetail.jsx](analytics-platform-front/src/components/subscribers/UserRowDetail.jsx) | Subscriber row detail panel |
| [analytics-platform-front/src/components/directory/Directory.jsx](analytics-platform-front/src/components/directory/Directory.jsx) | Directory UI component |
| [analytics-platform-front/src/components/nrr/NRRCard.jsx](analytics-platform-front/src/components/nrr/NRRCard.jsx) | NRR KPI card |
| [analytics-platform-front/src/components/admin/management/ServiceTable.jsx](analytics-platform-front/src/components/admin/management/ServiceTable.jsx) | Admin services table |
| [analytics-platform-front/src/components/admin/management/ServiceModal.jsx](analytics-platform-front/src/components/admin/management/ServiceModal.jsx) | Service create/edit modal |
| [analytics-platform-front/src/components/admin/management/CampaignTable.jsx](analytics-platform-front/src/components/admin/management/CampaignTable.jsx) | Admin campaigns table |
| [analytics-platform-front/src/components/admin/management/CampaignModal.jsx](analytics-platform-front/src/components/admin/management/CampaignModal.jsx) | Campaign create/edit modal |
| [analytics-platform-front/src/components/admin/management/DeleteConfirmModal.jsx](analytics-platform-front/src/components/admin/management/DeleteConfirmModal.jsx) | Admin delete confirmation modal |
| [analytics-platform-front/src/components/dashboard/BIInsightsPanel.jsx](analytics-platform-front/src/components/dashboard/BIInsightsPanel.jsx) | BI insight summary panel |
| [analytics-platform-front/src/components/dashboard/ChurnPieChart.jsx](analytics-platform-front/src/components/dashboard/ChurnPieChart.jsx) | Churn pie chart |
| [analytics-platform-front/src/components/dashboard/EngagementHealthPanel.jsx](analytics-platform-front/src/components/dashboard/EngagementHealthPanel.jsx) | Engagement health summary panel |
| [analytics-platform-front/src/components/dashboard/FilterBar.jsx](analytics-platform-front/src/components/dashboard/FilterBar.jsx) | Date and service filter bar |
| [analytics-platform-front/src/components/dashboard/KPICard.jsx](analytics-platform-front/src/components/dashboard/KPICard.jsx) | KPI card component |
| [analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx](analytics-platform-front/src/components/dashboard/KPICardsRow1.jsx) | Dashboard KPI row 1 |
| [analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx](analytics-platform-front/src/components/dashboard/KPICardsRow2.jsx) | Dashboard KPI row 2 |
| [analytics-platform-front/src/components/dashboard/KPICardsSMSRow.jsx](analytics-platform-front/src/components/dashboard/KPICardsSMSRow.jsx) | SMS KPI row |
| [analytics-platform-front/src/components/dashboard/SubscriptionDonutChart.jsx](analytics-platform-front/src/components/dashboard/SubscriptionDonutChart.jsx) | Subscription donut chart |
| [analytics-platform-front/src/components/dashboard/TabNavigation.jsx](analytics-platform-front/src/components/dashboard/TabNavigation.jsx) | Dashboard tab navigation |
| [analytics-platform-front/src/components/dashboard/TopServicesTable.jsx](analytics-platform-front/src/components/dashboard/TopServicesTable.jsx) | Top services table |
| [analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx](analytics-platform-front/src/components/dashboard/TrialDropoffChart.jsx) | Trial dropoff chart |
| [analytics-platform-front/src/components/dashboard/campaign/CampaignFunnelChart.jsx](analytics-platform-front/src/components/dashboard/campaign/CampaignFunnelChart.jsx) | Campaign funnel chart |
| [analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx](analytics-platform-front/src/components/dashboard/campaign/CampaignPerformanceChart.jsx) | Campaign performance chart |
| [analytics-platform-front/src/components/dashboard/campaign/CampaignVsOrganicChart.jsx](analytics-platform-front/src/components/dashboard/campaign/CampaignVsOrganicChart.jsx) | Campaign vs organic chart |
| [analytics-platform-front/src/components/dashboard/campaign/ServiceCampaignComparison.jsx](analytics-platform-front/src/components/dashboard/campaign/ServiceCampaignComparison.jsx) | Campaign comparison by service |
| [analytics-platform-front/src/components/dashboard/churn/ChartContainer.jsx](analytics-platform-front/src/components/dashboard/churn/ChartContainer.jsx) | Churn chart layout wrapper |
| [analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx](analytics-platform-front/src/components/dashboard/churn/ChurnCurveChart.jsx) | Churn curve chart |
| [analytics-platform-front/src/components/dashboard/churn/ChurnReasonsChart.jsx](analytics-platform-front/src/components/dashboard/churn/ChurnReasonsChart.jsx) | Churn reasons chart |
| [analytics-platform-front/src/components/dashboard/churn/RiskSegmentsPanel.jsx](analytics-platform-front/src/components/dashboard/churn/RiskSegmentsPanel.jsx) | Risk segments panel |
| [analytics-platform-front/src/components/dashboard/churn/TimeToChurnChart.jsx](analytics-platform-front/src/components/dashboard/churn/TimeToChurnChart.jsx) | Time-to-churn chart |
| [analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx](analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx) | Churn prediction dashboard component |
| [analytics-platform-front/src/components/dashboard/retention/CohortHeatmap.jsx](analytics-platform-front/src/components/dashboard/retention/CohortHeatmap.jsx) | Cohort heatmap chart |
| [analytics-platform-front/src/components/dashboard/retention/RetentionCurve.jsx](analytics-platform-front/src/components/dashboard/retention/RetentionCurve.jsx) | Retention curve chart |
| [analytics-platform-front/src/components/dashboard/retention/ServiceRetentionRadar.jsx](analytics-platform-front/src/components/dashboard/retention/ServiceRetentionRadar.jsx) | Retention radar chart |
| [analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx](analytics-platform-front/src/components/dashboard/tabs/OverviewTab.jsx) | Overview tab content |
| [analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx](analytics-platform-front/src/components/dashboard/tabs/EngagementTab.jsx) | Engagement tab content |
| [analytics-platform-front/src/components/dashboard/tabs/RevenueTab.jsx](analytics-platform-front/src/components/dashboard/tabs/RevenueTab.jsx) | Revenue tab content |
| [analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx](analytics-platform-front/src/components/dashboard/tabs/TrialChurnTab.jsx) | Trial and churn tab content |
| [analytics-platform-front/src/components/dashboard/userActivity/ActivityHeatmap.jsx](analytics-platform-front/src/components/dashboard/userActivity/ActivityHeatmap.jsx) | Activity heatmap chart |
| [analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx](analytics-platform-front/src/components/dashboard/userActivity/DAUTrendChart.jsx) | DAU trend chart |
| [analytics-platform-front/src/components/dashboard/userActivity/InactivityAnalysis.jsx](analytics-platform-front/src/components/dashboard/userActivity/InactivityAnalysis.jsx) | Inactivity analysis panel |
| [analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx](analytics-platform-front/src/components/dashboard/userActivity/ServiceActivityTable.jsx) | Service activity table |
| [analytics-platform-front/src/components/dashboard/userActivity/UserDistributionByServiceChart.jsx](analytics-platform-front/src/components/dashboard/userActivity/UserDistributionByServiceChart.jsx) | User distribution chart |
| [analytics-platform-front/src/components/dashboard/userActivity/UserGrowthChart.jsx](analytics-platform-front/src/components/dashboard/userActivity/UserGrowthChart.jsx) | User growth chart |
| [analytics-platform-front/src/services/api.js](analytics-platform-front/src/services/api.js) | Axios client and cache helpers |
| [analytics-platform-front/src/services/anomalies.js](analytics-platform-front/src/services/anomalies.js) | Anomalies API wrapper |
| [analytics-platform-front/src/hooks/useAnomalies.js](analytics-platform-front/src/hooks/useAnomalies.js) | Anomalies data orchestration hook |
| [analytics-platform-front/src/hooks/useCampaignComparison.js](analytics-platform-front/src/hooks/useCampaignComparison.js) | Campaign comparison hook |
| [analytics-platform-front/src/hooks/useCampaignImpactDashboard.js](analytics-platform-front/src/hooks/useCampaignImpactDashboard.js) | Campaign dashboard and list hooks |
| [analytics-platform-front/src/hooks/useCampaignKPIs.js](analytics-platform-front/src/hooks/useCampaignKPIs.js) | Campaign KPI hook |
| [analytics-platform-front/src/hooks/useCampaignPerformance.js](analytics-platform-front/src/hooks/useCampaignPerformance.js) | Campaign performance hook |
| [analytics-platform-front/src/hooks/useCampaignTimeline.js](analytics-platform-front/src/hooks/useCampaignTimeline.js) | Campaign timeline hook |
| [analytics-platform-front/src/hooks/useChurnBreakdown.js](analytics-platform-front/src/hooks/useChurnBreakdown.js) | Churn breakdown hook |
| [analytics-platform-front/src/hooks/useChurnCurve.js](analytics-platform-front/src/hooks/useChurnCurve.js) | Churn curve hook |
| [analytics-platform-front/src/hooks/useChurnDashboard.js](analytics-platform-front/src/hooks/useChurnDashboard.js) | Churn dashboard hook |
| [analytics-platform-front/src/hooks/useChurnKPIs.js](analytics-platform-front/src/hooks/useChurnKPIs.js) | Churn KPIs hook |
| [analytics-platform-front/src/hooks/useChurnModelGovernance.js](analytics-platform-front/src/hooks/useChurnModelGovernance.js) | Churn governance hook |
| [analytics-platform-front/src/hooks/useChurnPredictionMetrics.js](analytics-platform-front/src/hooks/useChurnPredictionMetrics.js) | Churn metrics hook |
| [analytics-platform-front/src/hooks/useChurnPredictionScores.js](analytics-platform-front/src/hooks/useChurnPredictionScores.js) | Churn scores hook |
| [analytics-platform-front/src/hooks/useChurnPredictionTrain.js](analytics-platform-front/src/hooks/useChurnPredictionTrain.js) | Churn training hook |
| [analytics-platform-front/src/hooks/useChurnReasons.js](analytics-platform-front/src/hooks/useChurnReasons.js) | Churn reasons hook |
| [analytics-platform-front/src/hooks/useCohortsTable.js](analytics-platform-front/src/hooks/useCohortsTable.js) | Cohorts list hook |
| [analytics-platform-front/src/hooks/useCrossService.js](analytics-platform-front/src/hooks/useCrossService.js) | Cross-service aggregation hook |
| [analytics-platform-front/src/hooks/useDashboardMetrics.js](analytics-platform-front/src/hooks/useDashboardMetrics.js) | Dashboard KPI derivation helper |
| [analytics-platform-front/src/hooks/useForgotPassword.js](analytics-platform-front/src/hooks/useForgotPassword.js) | Password reset hook |
| [analytics-platform-front/src/hooks/useImportData.js](analytics-platform-front/src/hooks/useImportData.js) | Admin import hook |
| [analytics-platform-front/src/hooks/useManagement.js](analytics-platform-front/src/hooks/useManagement.js) | Admin management hook |
| [analytics-platform-front/src/hooks/useNRR.js](analytics-platform-front/src/hooks/useNRR.js) | NRR hook |
| [analytics-platform-front/src/hooks/useOverview.js](analytics-platform-front/src/hooks/useOverview.js) | Overview analytics hook |
| [analytics-platform-front/src/hooks/useReactivationByService.js](analytics-platform-front/src/hooks/useReactivationByService.js) | Reactivation by service hook |
| [analytics-platform-front/src/hooks/useReactivationKPIs.js](analytics-platform-front/src/hooks/useReactivationKPIs.js) | Reactivation KPI hook |
| [analytics-platform-front/src/hooks/useRetentionCurve.js](analytics-platform-front/src/hooks/useRetentionCurve.js) | Retention curve hook |
| [analytics-platform-front/src/hooks/useRetentionHeatmap.js](analytics-platform-front/src/hooks/useRetentionHeatmap.js) | Retention heatmap hook |
| [analytics-platform-front/src/hooks/useRetentionKPIs.js](analytics-platform-front/src/hooks/useRetentionKPIs.js) | Retention KPI hook |
| [analytics-platform-front/src/hooks/useRetentionRecompute.js](analytics-platform-front/src/hooks/useRetentionRecompute.js) | Retention recompute hook |
| [analytics-platform-front/src/hooks/useRiskSegments.js](analytics-platform-front/src/hooks/useRiskSegments.js) | Risk segments hook |
| [analytics-platform-front/src/hooks/useSegmentationClusters.js](analytics-platform-front/src/hooks/useSegmentationClusters.js) | Segmentation clusters hook |
| [analytics-platform-front/src/hooks/useSegmentationKPIs.js](analytics-platform-front/src/hooks/useSegmentationKPIs.js) | Segmentation KPI hook |
| [analytics-platform-front/src/hooks/useSegmentationProfiles.js](analytics-platform-front/src/hooks/useSegmentationProfiles.js) | Segmentation profiles hook |
| [analytics-platform-front/src/hooks/useSubscribersKPIs.js](analytics-platform-front/src/hooks/useSubscribersKPIs.js) | Subscribers KPI hook |
| [analytics-platform-front/src/hooks/useTimeToChurn.js](analytics-platform-front/src/hooks/useTimeToChurn.js) | Time-to-churn hook |
| [analytics-platform-front/src/hooks/useTrialDropoffByDay.js](analytics-platform-front/src/hooks/useTrialDropoffByDay.js) | Trial dropoff by day hook |
| [analytics-platform-front/src/hooks/useTrialDropoffCauses.js](analytics-platform-front/src/hooks/useTrialDropoffCauses.js) | Trial dropoff causes hook |
| [analytics-platform-front/src/hooks/useTrialKPIs.js](analytics-platform-front/src/hooks/useTrialKPIs.js) | Trial KPI hook |
| [analytics-platform-front/src/hooks/useTrialUsers.js](analytics-platform-front/src/hooks/useTrialUsers.js) | Trial users list hook |
| [analytics-platform-front/src/hooks/useUserActivity.js](analytics-platform-front/src/hooks/useUserActivity.js) | User activity hook |
| [analytics-platform-front/src/hooks/useUsers.js](analytics-platform-front/src/hooks/useUsers.js) | Users list hook |
| [analytics-platform-front/src/hooks/useToast.jsx](analytics-platform-front/src/hooks/useToast.jsx) | Toast helper hook |
