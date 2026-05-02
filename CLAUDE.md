# CLAUDE.md â€” Contexte Complet du Projet pour Agent de Code (DigMaco)

## 1. IdentitÃ© du Projet et RÃ©alitÃ© Actuelle

### 1.1 RÃ©sumÃ© du projet

- Nom du projet : DigMaco Analytics Platform (nom dÃ©duit du contexte du dÃ©pÃ´t et des documents).
- Racine monorepo : pfev0.
- Dossier frontend : analytics-platform-front.
- Dossier backend : user-analytics-backend.
- Dossier documentation : docs.
- Stade actuel : implÃ©mentation avancÃ©e avec durcissement progressif (performance, robustesse, cohÃ©rence mÃ©tier).
- PortÃ©e : tableaux analytiques abonnements/churn/campagnes/rÃ©tention/segmentation/anomalies + administration.

### 1.2 Contexte mÃ©tier

- MarchÃ© cible : Tunisie.
- Domaine : analytics dâ€™abonnements, BI opÃ©rationnelle.
- Mode opÃ©ratoire : pipeline historique en batch (pas dâ€™ingestion streaming temps rÃ©el observÃ©e dans le code).
- Source de donnÃ©es : base de production prod_db (source externe).
- Base destination analytics : PostgreSQL (schÃ©ma analytique exploitÃ© par lâ€™API).

### 1.3 Style dâ€™architecture actuel

- Type : application web full-stack (React + FastAPI).
- Backend : style routeur -> service -> repository, avec SQL analytique important.
- Frontend : application React orientÃ©e routes, avec hooks spÃ©cialisÃ©s de rÃ©cupÃ©ration de donnÃ©es.
- Cache : Redis cÃ´tÃ© backend (cache endpoint/bloc).
- ETL : scripts Python batch pour extraction, normalisation, et chargement.

### 1.4 Ã‰tat de complÃ©tion (observÃ© dans le code)

- APIs backend majeures implÃ©mentÃ©es : oui.
- Dashboards frontend majeurs implÃ©mentÃ©s : oui.
- Authentification + rÃ´les : oui.
- Scripts ETL : oui.
- Migrations Alembic : oui.
- ML churn (entraÃ®nement + scoring) : oui.
- Segmentation : oui.
- Anomaly detection : oui.
- Pipeline CI/CD complet dans le dÃ©pÃ´t : Ã  vÃ©rifier en environnement.

### 1.5 Estimation de complÃ©tion (factuelle, code-based)

- Le socle fonctionnel principal est prÃ©sent.
- Plusieurs modules montrent des itÃ©rations de tuning (timeouts SQL, bornes de dates, fallback, cache versionnÃ©).
- Estimation de complÃ©tion fonctionnelle : ~90-95%.
- MaturitÃ© de production : Ã©levÃ©e en couverture fonctionnelle, moyenne-haute en hardening opÃ©rationnel.

### 1.6 Positionnement sur la phrase â€œ95% complet et prÃªt prodâ€

- Le code supporte une forte complÃ©tude fonctionnelle.
- La â€œprÃªt prodâ€ stricte (SLO, observabilitÃ©, runbooks, CI/CD exhaustive) nÃ©cessite des validations hors dÃ©pÃ´t.

## 2. Vue dâ€™Ensemble Architecture (As-Is)

### 2.1 SchÃ©ma dâ€™architecture implÃ©mentÃ©

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    SOURCE EXTERNE (prod_db PROD)                            â”‚
â”‚      [Tables source consommÃ©es par les scripts ETL]                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚
                                â”‚ ETL batch (Python)
                                â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                user-analytics-backend/scripts/etl                          â”‚
â”‚  etl_prod_to_analytics.py, fix_services_mapping.py,                        â”‚
â”‚  recalcul_cohorts.py, link_campaigns_to_subscriptions.py, seed_campaigns.pyâ”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚
                                â”‚ insert/upsert donnÃ©es normalisÃ©es
                                â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   PostgreSQL analytics DB                                   â”‚
â”‚ users, subscriptions, billing_events, unsubscriptions, campaigns,          â”‚
â”‚ sms_events, user_activities, cohorts, services, service_types,             â”‚
â”‚ platform_users, import_logs, campaign_targets, etc.                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚
                                â”‚ SQLAlchemy + SQL analytique
                                â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                 FastAPI backend (app/)                                      â”‚
â”‚ Routes /analytics/*, /auth/*, /admin/*, /users, /services, /ml/*          â”‚
â”‚ Services + repositories + couche cache Redis                                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚
                                â”‚ HTTP JSON
                                â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                 React frontend (analytics-platform-front)                   â”‚
â”‚ Pages + hooks, routes privÃ©es et admin                                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 2.2 Indicateurs de couverture (scan dÃ©pÃ´t)

- Fichiers Python backend : 75.
- Routeurs backend : 18.
- Pages frontend : 20.
- Hooks frontend : 42.
- Migrations Alembic : 11.
- Artefacts ML prÃ©sents :
- ml_models/churn_model.joblib.
- ml_models/churn_metrics.joblib.
- ml_models/segmentation_kmeans.joblib.

### 2.3 Indicateurs de volumÃ©trie

- Comptes exacts de lignes en base live : Ã  vÃ©rifier en environnement (requÃªtes SQL nÃ©cessaires).
- La structure du code indique un usage orientÃ© gros volumes analytiques.

### 2.4 ExÃ©cution et runtime

- Frontend dev : Vite (5173 documentÃ©).
- Backend : FastAPI/Uvicorn.
- Redis : prÃ©sent dans docker-compose.
- PostgreSQL local docker-compose : Ã  vÃ©rifier selon environnement cible.

## 3. Couche DonnÃ©es â€” Source de VÃ©ritÃ©

### 3.1 Moteur et outillage

- Base : PostgreSQL.
- ORM : SQLAlchemy.
- Migrations : Alembic.
- Driver : psycopg2-binary.

### 3.2 RÃ©fÃ©rence tables principales

| Table              | RÃ´le                  | Colonnes clÃ©s                                                                                | Origine   |
| ------------------ | --------------------- | -------------------------------------------------------------------------------------------- | --------- |
| users              | utilisateurs finaux   | id, phone_number, status, created_at, last_activity_at                                       | ETL + app |
| service_types      | cadence/prix          | id, name, billing_frequency_days, trial_duration_days, price                                 | ETL/admin |
| services           | catalogue services    | id, name, service_type_id, is_active                                                         | ETL/admin |
| campaigns          | mÃ©tadonnÃ©es campagnes | id, name, service_id, send_datetime, target_size, campaign_type, status                      | ETL/admin |
| subscriptions      | cycle abonnement      | id, user_id, service_id, campaign_id, subscription_start_date, subscription_end_date, status | ETL       |
| billing_events     | Ã©vÃ©nements billing    | id, subscription_id, user_id, service_id, event_datetime, status, is_first_charge            | ETL       |
| unsubscriptions    | churn events          | id, subscription_id, user_id, service_id, unsubscription_datetime, churn_type, churn_reason  | ETL       |
| user_activities    | activitÃ© usage        | id, user_id, service_id, activity_datetime, activity_type, session_id                        | ETL       |
| sms_events         | Ã©vÃ©nements SMS        | id, user_id, campaign_id, service_id, event_datetime, event_type, direction                  | ETL       |
| cohorts            | agrÃ©gats rÃ©tention    | id, cohort_date, service_id, total_users, retention_d7, retention_d14, retention_d30         | script    |
| platform_users     | comptes plateforme    | id, email, password_hash, role, is_active, reset_token                                       | app       |
| import_logs        | audit imports admin   | id, admin_id, file_name, file_type, target_table, rows_inserted, status                      | app       |
| campaign_targets   | cibles de campagne    | id, campaign_id, phone_number, segment, region                                               | app admin |
| churn_scores_cache | snapshot score churn  | user_id, churn_risk, risk_category, generated_at                                             | runtime   |
| staging_imports    | staging import CSV    | id, import_id, row_number, raw_data, status, error_message                                   | runtime   |

### 3.3 Comptes de lignes

- users, subscriptions, billing_events, unsubscriptions, user_activities, sms_events, campaigns : Ã  vÃ©rifier en base dÃ©ployÃ©e.
- cohorts : dÃ©pend du dernier recalcul effectuÃ©.

### 3.4 Normalisation statuts observÃ©e

- Actif : active/subscribed/iscrit/inscrit/1 -> subscribed.
- Risque billing : billing_failed et variantes/-2 -> billing_failed.
- RÃ©siliÃ© : cancelled/expired/unsubscribed/desinscrit/-1 -> unsubscribed.
- OTP/trial incomplet : pending/trial/otp_pending/0 -> otp_incomplete.
- Sinon : unknown.

### 3.5 Garde-fous qualitÃ© de donnÃ©es

- Validation UUID sur plusieurs endpoints.
- RÃ©solution centralisÃ©e des bornes via resolve_date_range.
- Retry avec timeout local ajustÃ© pour requÃªtes lourdes.
- Validation imports : colonnes requises, enums, clÃ©s Ã©trangÃ¨res, doublons.

### 3.6 Relations clÃ©s

- services.service_type_id -> service_types.id.
- subscriptions.user_id -> users.id.
- subscriptions.service_id -> services.id.
- subscriptions.campaign_id -> campaigns.id.
- billing_events.subscription_id -> subscriptions.id.
- unsubscriptions.subscription_id -> subscriptions.id.
- sms_events.user_id/service_id/campaign_id -> users/services/campaigns.
- cohorts.service_id -> services.id.
- import_logs.admin_id -> platform_users.id.
- campaign_targets.campaign_id -> campaigns.id.

## 4. Pipeline ETL (Batch Historique)

### 4.1 Scripts ETL principaux

- scripts/etl/etl_prod_to_analytics.py.
- scripts/etl/fix_services_mapping.py.
- scripts/etl/recalcul_cohorts.py.
- scripts/etl/link_campaigns_to_subscriptions.py.
- scripts/etl/seed_campaigns.py.
- scripts/compute_cohorts.py.
- scripts/verify_data.py.
- scripts/seeder/seed_missing_data.py.

### 4.2 SÃ©quence dâ€™exÃ©cution observÃ©e

- Connexion source + destination.
- Lecture batch des donnÃ©es source.
- Normalisation statuts/champs.
- IDs dÃ©terministes UUID5.
- Insert/upsert tables analytiques.
- Post-traitements de liaison campagne-abonnement.
- Recalcul cohortes.
- VÃ©rifications cohÃ©rence.

### 4.3 StratÃ©gie IDs dÃ©terministes

- Utilisation UUID5 namespace pour stabilitÃ© des reruns ETL.
- Objectif : Ã©viter doublons logiques inter-runs.

### 4.4 Gestion temporelle

- FenÃªtres via app/core/date_ranges.py.
- Ancres temporelles via app/utils/temporal.py.
- Bornes fallback prÃ©sentes si bornes DB indisponibles.

### 4.5 SÃ©mantique trial/churn

- Logique majoritairement calculÃ©e cÃ´tÃ© SQL analytics.
- SpÃ©cification exhaustive de toutes exceptions mÃ©tier ETL : Ã  vÃ©rifier avec documentation mÃ©tier externe.

### 4.6 Performance et fiabilitÃ© ETL

- Traitement batch.
- Utilitaires de correction/recalcul dÃ©diÃ©s.
- Orchestrateur/scheduler de prod explicitement versionnÃ© dans ce dÃ©pÃ´t : Ã  vÃ©rifier.

### 4.7 DonnÃ©es de dÃ©monstration

- Outils de seeding prÃ©sents.
- Pipeline â€œdemo DBâ€ complet reproductible avec contraintes strictes : Ã  vÃ©rifier.

## 5. Surface API Backend (Carte ComplÃ¨te)

### 5.1 Composition backend

- Framework : FastAPI.
- Routeurs : 18.
- Services : 6.
- Repositories : 4.
- SchÃ©mas : 16+ modules.

### 5.2 Inventaire routeurs/prefixes

- auth.py -> /auth.
- users.py -> /users.
- service.py -> /services.
- analyticsOverview.py -> /analytics.
- userActivity.py -> /analytics.
- trialAnalytics.py -> /analytics.
- retention.py -> /analytics.
- campaign_impact.py -> /analytics/campaigns.
- churn_analysis.py -> /analytics/churn.
- cross_service.py -> /analytics/cross-service.
- segmentation.py -> /analytics/segmentation.
- anomalies.py -> /anomalies.
- ml_churn.py -> /ml/churn.
- nrr.py -> /nrr (montÃ© sous /analytics/nrr dans main).
- platform_user.py -> /platform-users.
- management.py -> /admin/management.
- admin_import.py -> /admin/import.
- campaign_upload.py -> /admin/management/campaigns.

### 5.3 Matrice endpoints (mÃ©thode + chemin)

- POST /auth/register.
- POST /auth/login.
- POST /auth/forgot-password.
- POST /auth/verify-reset-token.
- POST /auth/reset-password.

- GET /services.

- GET /users.
- GET /users/trial.
- GET /users/{user_id}.

- GET /analytics/summary.
- GET /analytics/overview.
- GET /analytics/status/diagnostics.
- POST /analytics/cache/invalidate.

- GET /analytics/user-activity.

- GET /analytics/trial/kpis.
- GET /analytics/trial/timeline.
- GET /analytics/trial/by-service.
- GET /analytics/trial/users.
- GET /analytics/trial/dropoff-by-day.
- GET /analytics/trial/dropoff-causes.
- GET /analytics/churn/breakdown.

- POST /analytics/retention/recompute.
- GET /analytics/retention/kpis.
- GET /analytics/retention/heatmap.
- GET /analytics/retention/curve.
- GET /analytics/retention/cohorts-list.

- GET /analytics/campaigns/dashboard.
- GET /analytics/campaigns/list.
- GET /analytics/campaigns/overview.
- GET /analytics/campaigns/by-type.
- GET /analytics/campaigns/top.
- GET /analytics/campaigns/trend.
- GET /analytics/campaigns/kpis.
- GET /analytics/campaigns/performance.
- GET /analytics/campaigns/comparison.
- GET /analytics/campaigns/timeline.

- GET /analytics/churn/dashboard.
- GET /analytics/churn/kpis.
- GET /analytics/churn/reactivation/kpis.
- GET /analytics/churn/reactivation/by-service.
- GET /analytics/churn/trend.
- GET /analytics/churn/by-service.
- GET /analytics/churn/lifetime.
- GET /analytics/churn/retention.

- GET /analytics/cross-service/overview.
- GET /analytics/cross-service/co-subscriptions.
- GET /analytics/cross-service/migrations.
- GET /analytics/cross-service/distribution.
- GET /analytics/cross-service/all.

- GET /analytics/segmentation/kpis.
- GET /analytics/segmentation/clusters.
- GET /analytics/segmentation/profiles.
- POST /analytics/segmentation/train.

- GET /anomalies/summary.
- GET /anomalies/timeline.
- GET /anomalies/distribution.
- GET /anomalies/heatmap.
- GET /anomalies/details.
- GET /anomalies/insights.
- POST /anomalies/run-detection.

- POST /ml/churn/train.
- GET /ml/churn/metrics.
- GET /ml/churn/governance.
- GET /ml/churn/scores.
- POST /ml/churn/scores/recompute.

- GET /analytics/nrr.

- GET /platform-users/.
- GET /platform-users/{user_id}.
- POST /platform-users/.
- PUT /platform-users/{user_id}.
- PATCH /platform-users/{user_id}/status.
- PATCH /platform-users/{user_id}/role.
- DELETE /platform-users/{user_id}.

- GET /admin/management/services.
- POST /admin/management/services.
- PUT /admin/management/services/{service_id}.
- DELETE /admin/management/services/{service_id}.
- GET /admin/management/campaigns.
- POST /admin/management/campaigns.
- PUT /admin/management/campaigns/{campaign_id}.
- DELETE /admin/management/campaigns/{campaign_id}.
- POST /admin/management/campaigns/upload-targets.

- POST /admin/import/csv.
- POST /admin/import/csv/confirm.
- POST /admin/import/database.
- GET /admin/import/history.
- GET /admin/import/schema/{table}.
- GET /admin/import/template/{table}.

### 5.4 Async / parallÃ©lisation

- /analytics/summary : asyncio.gather + ThreadPoolExecutor.
- churn_analysis : exÃ©cution en pool sur certains calculs.
- cross-service/all : calcul section par section avec fallback isolÃ©.

### 5.5 Timeouts / contrÃ´le latence

- Timeout statement global DB : 10000ms.
- Timeout SQL churn ML : CHURN_SQL_TIMEOUT_MS (120000 par dÃ©faut dans modÃ¨le).
- Retry local en cas de statement timeout dans plusieurs routeurs.

### 5.6 Auth / autorisation

- JWT via python-jose.
- Hash mots de passe via passlib bcrypt.
- IncohÃ©rence potentielle TTL token : constant sÃ©curitÃ© vs settings.
- DÃ©pendances de garde : get_current_user, require_admin.

### 5.7 Cache

- Couche Redis via app/core/cache.py.
- ClÃ©s versionnÃ©es (vX) sur endpoints analytiques.
- TTL spÃ©cifiques par domaine (overview, retention, campaign, churn, cross-service, segmentation, user-activity, ML).

## 6. Application Frontend (Pages, Hooks, Routes, Guards)

### 6.1 Stack frontend

- react 19.2.0.
- react-dom 19.2.0.
- react-router-dom 7.13.1 (usage de composants style v6 dans App.jsx).
- vite 7.3.1.
- tailwindcss 3.4.19.
- axios 1.11.0.
- recharts 3.2.1.
- @tanstack/react-query 5.90.2.
- @mui/material 7.3.4.

### 6.2 Plan de routes frontend

- /, /login, /forgot-password, /reset-password.
- /dashboard, /dashboard-1.
- /analytics/behaviors.
- /analytics/trial.
- /analytics/retention.
- /analytics/campaigns.
- /analytics/churn.
- /analytics/churn-prediction.
- /analytics/cross-service.
- /analytics/segmentation.
- /analytics/anomalies.
- /management/subscribers.
- /admin/users.
- /admin/import.
- /admin/management.
- /admin/settings.

### 6.3 Inventaire pages (20)

- src/pages/Dashboard.jsx.
- src/pages/RootRedirect.jsx.
- src/pages/SubscribersPage.jsx.
- src/pages/UserActivityPage.jsx.
- src/pages/admin/SystemSettingsPage.jsx.
- src/pages/admin/ManagementPage.jsx.
- src/pages/admin/ImportDataPage.jsx.
- src/pages/auth/LoginPage.jsx.
- src/pages/auth/ForgotPasswordPage.jsx.
- src/pages/auth/ResetPasswordPage.jsx.
- src/pages/platform-users/PlatformUsersPage.jsx.
- src/pages/dashboard/DashboardPage.jsx.
- src/pages/dashboard/RetentionPage.jsx.
- src/pages/dashboard/FreeTrialBehaviorPage.jsx.
- src/pages/dashboard/CampaignImpactPage.jsx.
- src/pages/dashboard/ChurnAnalysisPage.jsx.
- src/pages/dashboard/AIChurnInsights.jsx.
- src/pages/dashboard/CrossServiceBehaviorPage.jsx.
- src/pages/dashboard/UserSegmentationPage.jsx.
- src/pages/dashboard/AnomalyDetectionPage.jsx.

### 6.4 Inventaire hooks (42) et endpoints

- useAnomalies.js -> wrapper service anomalies.
- useCampaignComparison.js -> /analytics/campaigns/comparison.
- useCampaignImpactDashboard.js -> /analytics/campaigns/dashboard, /analytics/campaigns/list.
- useCampaignKPIs.js -> /analytics/campaigns/kpis.
- useCampaignPerformance.js -> /analytics/campaigns/performance.
- useCampaignTimeline.js -> /analytics/campaigns/timeline.
- useChurnBreakdown.js -> /analytics/churn/breakdown.
- useChurnCurve.js -> /analytics/churn/curve.
- useChurnDashboard.js -> /analytics/churn/dashboard.
- useChurnKPIs.js -> /analytics/churn/kpis.
- useChurnModelGovernance.js -> /ml/churn/governance.
- useChurnPredictionMetrics.js -> /ml/churn/metrics.
- useChurnPredictionScores.js -> /ml/churn/scores.
- useChurnPredictionTrain.js -> /ml/churn/train.
- useChurnReasons.js -> /analytics/churn/reasons.
- useCohortsTable.js -> /analytics/retention/cohorts-list.
- useCrossService.js -> /analytics/cross-service/all.
- useDashboardMetrics.js -> endpoint exact Ã  vÃ©rifier.
- useForgotPassword.js -> /auth/forgot-password, /auth/verify-reset-token, /auth/reset-password.
- useImportData.js -> /admin/import/history, /admin/import/schema/{table}, /admin/import/template/{table}, /admin/import/csv, /admin/import/csv/confirm, /admin/import/database.
- useManagement.js -> CRUD services/campaigns + upload-targets.
- useNRR.js -> /analytics/nrr.
- useOverview.js -> /analytics/overview.
- useReactivationByService.js -> /analytics/churn/reactivation/by-service.
- useReactivationKPIs.js -> /analytics/churn/reactivation/kpis.
- useRetentionCurve.js -> /analytics/retention/curve.
- useRetentionHeatmap.js -> /analytics/retention/heatmap.
- useRetentionKPIs.js -> /analytics/retention/kpis.
- useRetentionRecompute.js -> /analytics/retention/recompute.
- useRiskSegments.js -> /analytics/churn/risk-segments.
- useSegmentationClusters.js -> /analytics/segmentation/clusters.
- useSegmentationKPIs.js -> /analytics/segmentation/kpis.
- useSegmentationProfiles.js -> /analytics/segmentation/profiles.
- useSubscribersKPIs.js -> /analytics/overview.
- useTimeToChurn.js -> /analytics/churn/time-to-churn.
- useToast.jsx -> helper UI local.
- useTrialDropoffByDay.js -> /analytics/trial/dropoff-by-day.
- useTrialDropoffCauses.js -> /analytics/trial/dropoff-causes.
- useTrialKPIs.js -> /analytics/trial/kpis.
- useTrialUsers.js -> /api/users/trial (proxy frontend).
- useUserActivity.js -> /analytics/user-activity.
- useUsers.js -> helper getUsersPage (users API).

### 6.5 Guards et contrÃ´le accÃ¨s

- PrivateRoute : session authentifiÃ©e requise.
- AdminRoute : rÃ´le admin requis.
- AuthContext : token + rÃ´le + Ã©tat auth.

### 6.6 ThÃ¨me et UX

- ThemeContext prÃ©sent.
- Tailwind config prÃ©sent.
- CSS global prÃ©sent.
- Table des design tokens complÃ¨te et normalisÃ©e : Ã  vÃ©rifier.

## 7. Moteurs ML et Analytics

### 7.1 Churn predictor

- Fichier : ml_models/churn_predictor.py.
- ModÃ¨le : LogisticRegression.
- class_weight : balanced.
- max_iter : 2000.
- random_state : 42.
- Nombre features : 9.

### 7.2 Features churn utilisÃ©es

- days_since_last_activity.
- nb_activities_7d.
- nb_activities_30d.
- billing_failures_30d.
- days_since_first_charge.
- is_trial_churn.
- avg_retention_d7.
- service_billing_frequency.
- days_to_first_unsub.

### 7.3 Outputs ML churn

- ModÃ¨le : churn_model.joblib.
- MÃ©triques : churn_metrics.joblib.
- Endpoint gouvernance : /ml/churn/governance.
- Endpoint scores : /ml/churn/scores.
- Table snapshot : churn_scores_cache.

### 7.4 Segmentation

- Routeur : /analytics/segmentation/\*.
- Service : segmentation_service.py.
- Repository : segmentation_repo.py.
- Artefact : segmentation_kmeans.joblib.

### 7.5 Anomalies

- Routeur : /anomalies/\*.
- MÃ©thode : rolling z-score (fenÃªtre 14 jours).
- MÃ©triques : dau, churn_rate, revenue, renewals.
- SÃ©vÃ©ritÃ©s : critical/high/medium.
- Cap fenÃªtre endpoint : 120 jours.

### 7.6 Gouvernance et calibration

- Brier score + ECE bins implÃ©mentÃ©s.
- Calcul drift features prÃ©sent.
- Payload gouvernance enregistrÃ© dans mÃ©triques.

## 8. Migrations DB et Indexation

### 8.1 Inventaire migrations (11)

- 8ce2685abdcf_init_analytics_schema.py.
- dff7e8f3a1b2_add_platform_users.py.
- ded5566fe73f_add_campaign_fields.py.
- 3939f475629f_normalize_status_fields.py.
- 6c076db13bed_add_analytics_performance_indexes.py.
- 85b71708c64d_add_performance_indexes_p0.py.
- c1f4a2d9e8b1_extend_sms_events_for_otp_ussd_web_activation.py.
- 4b9e2f7a1d3c_sms_events_hawala_lean_model_and_indexes.py.
- b7e2c4f91a10_add_campaign_targets_table.py.
- f1a2b3c4d5e6_add_import_logs_table.py.
- a1b2c3d4e5f6_add_password_reset_fields.py.

### 8.2 Index notables observÃ©s

- ix_platform_users_reset_token.
- idx_billing_events_datetime_status.
- idx_billing_events_service_datetime.
- idx_billing_events_user_datetime.
- idx_subscriptions_end_date.
- idx_subscriptions_status_end_date.
- idx_subscriptions_service_start_date.
- idx_user_activities_service_id.
- idx_user_activities_datetime_type.
- idx_user_activities_service_datetime.
- idx_cohorts_service_id.
- idx_cohorts_service_cohort_date.
- idx_sms_events_event_type_event_datetime.
- idx_sms_events_source_system.
- idx_sms_events_metadata_gin.
- idx_ct_campaign.
- idx_ct_phone.
- idx_subscriptions_status_service_end_partial.
- idx_subscriptions_service_end.
- idx_subscriptions_service_start_user.
- idx_billing_events_sub_success_dt.
- idx_billing_events_sub_failed_dt.
- idx_campaigns_service_send_datetime.
- idx_users_status_last_activity.
- idx_user_activities_service_user_dt.

### 8.3 Observations stratÃ©gie index

- Travail important sur filtres date + service.
- Index partiels sur billing success/failed.
- CrÃ©ation concurrente utilisÃ©e dans migration performance P0.

### 8.4 Migrations de normalisation

- Harmonisation statuts : prÃ©sente.
- Ã‰volution champs campagnes : prÃ©sente.
- Champs reset password : prÃ©sents.

## 9. SÃ©curitÃ©, Auth et ContrÃ´les Admin

### 9.1 Authentification

- Login gÃ©nÃ¨re JWT bearer.
- Claims incluent user id + rÃ´le.
- Mots de passe hashÃ©s (passlib).
- Flow reset : forgot -> verify token -> reset + invalidation token.

### 9.2 Autorisation

- DÃ©pendance get_current_user pour routes authentifiÃ©es.
- DÃ©pendance require_admin pour routes admin.

### 9.3 Points sensibles sÃ©curitÃ©

- IncohÃ©rence potentielle TTL access token.
- Configuration SMTP rÃ©elle Ã  valider.
- Rate limit auth endpoints explicite : Ã  vÃ©rifier.

### 9.4 Protections import admin

- Blocage mots-clÃ©s SQL dangereux.
- Autorisation uniquement INSERT/COPY dans import SQL.
- CSV chargÃ© via staging + validation.
- Historique import persistant (import_logs).

## 10. Configuration et Environnement

### 10.1 DÃ©pendances backend observÃ©es

- fastapi==0.115.0.
- uvicorn[standard]==0.30.6.
- sqlalchemy==2.0.34.
- psycopg2-binary==2.9.9.
- alembic==1.13.2.
- pydantic==2.8.2.
- pydantic-settings==2.4.0.
- python-jose[cryptography]==3.3.0.
- passlib[bcrypt]==1.7.4.
- redis==5.0.8.
- pandas==2.2.2.
- numpy==1.26.4.
- scikit-learn==1.5.1.
- joblib==1.4.2.

### 10.2 DÃ©pendances frontend observÃ©es

- react 19.2.0.
- react-dom 19.2.0.
- react-router-dom 7.13.1.
- axios 1.11.0.
- recharts 3.2.1.
- @tanstack/react-query 5.90.2.
- vite 7.3.1.
- tailwindcss 3.4.19.
- @mui/material 7.3.4.
- jspdf 3.0.3.
- html2canvas 1.4.1.
- xlsx 0.18.5.

### 10.3 ParamÃ¨tres backend clÃ©s

- DATABASE_URL (normalisation postgres:// -> postgresql://).
- REDIS_URL.
- CACHE_DEFAULT_TTL_SECONDS + TTL spÃ©cifiques modules.
- DB_POOL_SIZE=10.
- DB_MAX_OVERFLOW=20.
- DB_STATEMENT_TIMEOUT_MS=10000.
- CHURN_SQL_TIMEOUT_MS=120000 (module ML).

### 10.4 Docker / compose

- backend : prÃ©sent.
- frontend : prÃ©sent.
- redis : prÃ©sent.
- postgres local compose racine : Ã  vÃ©rifier selon cible.

### 10.5 Exemples dâ€™environnement

- backend .env.example prÃ©sent.
- frontend .env.example prÃ©sent.
- README backend/frontend prÃ©sents.

## 11. Performance, ScalabilitÃ©, FiabilitÃ©

### 11.1 ContrÃ´les performance backend

- Pool DB paramÃ©trable.
- Timeout statement global.
- Retry local sur requÃªtes lourdes.
- Cache key versioning utilisÃ©.

### 11.2 Patterns de requÃªtes

- SQL analytique important (CTE, agrÃ©gations, joins latÃ©raux).
- Filtres date/service propagÃ©s.

### 11.3 ParallÃ©lisation

- /analytics/summary parallÃ©lisÃ©.
- cross-service/all rÃ©silient par section.

### 11.4 FiabilitÃ© et fallback

- Fallback payload sur sections en erreur.
- Validation UUID/dates cÃ´tÃ© endpoints.
- Import admin avec mode force (skip invalides).

### 11.5 Risques techniques connus

- HÃ©tÃ©rogÃ©nÃ©itÃ© de statuts Ã  maintenir cohÃ©rente.
- Chevauchement legacy de certains chemins churn/trial.
- Risque confusion TTL token.
- FenÃªtres temporelles larges encore coÃ»teuses sur certains endpoints.

## 12. Documentation et ArtÃ©facts de Connaissance

### 12.1 Docs clÃ©s observÃ©es

- docs/architecture.md.
- docs/etl_prod_readme.md.
- docs/kpis.md.
- docs/ml_churn_report.md.
- docs/REAL_DATA_INTEGRATION.md.
- docs/TRIAL_INTEGRATION_SUMMARY.md.
- user-analytics-backend/README.md.
- analytics-platform-front/README.md.
- rapports racine RAPPORT\_\*.md.

### 12.2 Alignement docs/code

- Les grands domaines analytics dÃ©crits sont implÃ©mentÃ©s.
- Les scripts ETL supportent les flux dÃ©crits.
- La doc churn ML est globalement alignÃ©e avec le code.
- DÃ©rives possibles : nomenclature endpoint/compteurs selon date de mise Ã  jour docs.

### 12.3 Points de validation recommandÃ©s

- Comptes de lignes rÃ©els en base prod.
- Valeur effective TTL token en prod.
- Politique dâ€™invalidation cache en exploitation.
- Plans dâ€™exÃ©cution SQL endpoints lourds.

## 13. Notes de Handoff Pratiques

### 13.1 Lecture prioritaire pour onboarding rapide

- user-analytics-backend/app/main.py.
- user-analytics-backend/app/core/config.py.
- user-analytics-backend/app/core/database.py.
- user-analytics-backend/app/core/date_ranges.py.
- user-analytics-backend/app/utils/temporal.py.
- Routeurs : analyticsOverview.py, trialAnalytics.py, campaign_impact.py, churn_analysis.py, cross_service.py, retention.py.
- ModÃ¨les + migrations : app/models/_ et alembic/versions/_.
- Front : analytics-platform-front/src/App.jsx, services/api.js, hooks/\*.

### 13.2 StratÃ©gie de changement sÃ»re

- Garder la normalisation de statuts uniforme.
- RÃ©utiliser resolve_date_range pour toute nouvelle API filtrÃ©e par date.
- Ã‰tendre service/repository pour SQL non trivial.
- Ajouter index via migration pour nouveaux filtres coÃ»teux.
- Maintenir versionnement des clÃ©s cache lors changement de shape.
- Conserver garde require_admin sur routes sensibles.

### 13.3 HiÃ©rarchie des sources de vÃ©ritÃ©

- Comportement runtime : code backend.
- SchÃ©ma : modÃ¨les + migrations Alembic.
- Comportement frontend : hooks + routes App.jsx.
- Documentation : secondaire (peut Ãªtre en retard).

### 13.4 Inconnues explicites Ã  valider

- VolumÃ©trie exacte prod par table.
- SLA/latence endpoint par endpoint.
- Scheduler ETL prod.
- CI/CD et environnements exacts.
- Stack observabilitÃ© complÃ¨te (mÃ©triques/traces/alerting).
- SMTP provider et policy rÃ©elle reset password.
- TTL token rÃ©ellement appliquÃ© en prod.

### 13.5 RÃ©sumÃ© final factuel

- Backend et frontend sont fortement implÃ©mentÃ©s.
- ETL, analytics, ML churn, segmentation, anomalies, import admin et RBAC sont prÃ©sents.
- Le projet est apte Ã  une phase de hardening et optimisation continue.

---

## Annexe A â€” Couverture Endpoints Ã‰tendue

- GET /analytics/summary : KPI macro ancrÃ©s.
- GET /analytics/overview : payload dashboard filtrÃ©.
- GET /analytics/status/diagnostics : distributions statuts bruts/normalisÃ©s.
- POST /analytics/cache/invalidate : invalidation cache analytics.

- GET /analytics/user-activity : activitÃ©, inactivitÃ©, score engagement.

- GET /analytics/trial/kpis.
- GET /analytics/trial/timeline.
- GET /analytics/trial/by-service.
- GET /analytics/trial/users.
- GET /analytics/trial/dropoff-by-day.
- GET /analytics/trial/dropoff-causes.

- GET /analytics/retention/kpis.
- GET /analytics/retention/heatmap.
- GET /analytics/retention/curve.
- GET /analytics/retention/cohorts-list.
- POST /analytics/retention/recompute.

- GET /analytics/campaigns/dashboard.
- GET /analytics/campaigns/list.
- GET /analytics/campaigns/overview.
- GET /analytics/campaigns/by-type.
- GET /analytics/campaigns/top.
- GET /analytics/campaigns/trend.
- GET /analytics/campaigns/kpis.
- GET /analytics/campaigns/performance.
- GET /analytics/campaigns/comparison.
- GET /analytics/campaigns/timeline.

- GET /analytics/churn/dashboard.
- GET /analytics/churn/kpis.
- GET /analytics/churn/reactivation/kpis.
- GET /analytics/churn/reactivation/by-service.
- GET /analytics/churn/trend.
- GET /analytics/churn/by-service.
- GET /analytics/churn/lifetime.
- GET /analytics/churn/retention.
- GET /analytics/churn/breakdown.

- GET /analytics/cross-service/overview.
- GET /analytics/cross-service/co-subscriptions.
- GET /analytics/cross-service/migrations.
- GET /analytics/cross-service/distribution.
- GET /analytics/cross-service/all.

- GET /analytics/segmentation/kpis.
- GET /analytics/segmentation/clusters.
- GET /analytics/segmentation/profiles.
- POST /analytics/segmentation/train.

- GET /anomalies/summary.
- GET /anomalies/timeline.
- GET /anomalies/distribution.
- GET /anomalies/heatmap.
- GET /anomalies/details.
- GET /anomalies/insights.
- POST /anomalies/run-detection.

- POST /ml/churn/train.
- GET /ml/churn/metrics.
- GET /ml/churn/governance.
- GET /ml/churn/scores.
- POST /ml/churn/scores/recompute.

- GET /analytics/nrr.
- GET /services.
- GET /users.
- GET /users/trial.
- GET /users/{id}.

- GET /platform-users/.
- GET /platform-users/{id}.
- POST /platform-users/.
- PUT /platform-users/{id}.
- PATCH /platform-users/{id}/status.
- PATCH /platform-users/{id}/role.
- DELETE /platform-users/{id}.

- GET /admin/management/services.
- POST /admin/management/services.
- PUT /admin/management/services/{id}.
- DELETE /admin/management/services/{id}.
- GET /admin/management/campaigns.
- POST /admin/management/campaigns.
- PUT /admin/management/campaigns/{id}.
- DELETE /admin/management/campaigns/{id}.
- POST /admin/management/campaigns/upload-targets.

- POST /admin/import/csv.
- POST /admin/import/csv/confirm.
- POST /admin/import/database.
- GET /admin/import/history.
- GET /admin/import/schema/{table}.
- GET /admin/import/template/{table}.

## Annexe B â€” Couverture Hooks Ã‰tendue

- useOverview.
- useUserActivity.
- useTrialKPIs.
- useTrialDropoffByDay.
- useTrialDropoffCauses.
- useTrialUsers.
- useRetentionKPIs.
- useRetentionHeatmap.
- useRetentionCurve.
- useCohortsTable.
- useRetentionRecompute.

- useCampaignImpactDashboard.
- useCampaignKPIs.
- useCampaignPerformance.
- useCampaignComparison.
- useCampaignTimeline.

- useChurnDashboard.
- useChurnKPIs.
- useChurnBreakdown.
- useChurnReasons.
- useTimeToChurn.
- useRiskSegments.
- useReactivationKPIs.
- useReactivationByService.

- useCrossService.

- useSegmentationKPIs.
- useSegmentationClusters.
- useSegmentationProfiles.

- useAnomalies.

- useChurnPredictionTrain.
- useChurnPredictionMetrics.
- useChurnPredictionScores.
- useChurnModelGovernance.

- useSubscribersKPIs.
- useUsers.
- useDashboardMetrics (dÃ©tail endpoint Ã  vÃ©rifier).

- useManagement.
- useImportData.

- useForgotPassword.
- useToast.

## Annexe C â€” Checklist OpÃ©rationnelle Agent Suivant

- VÃ©rifier commande de dÃ©marrage backend et variables env.
- VÃ©rifier base URL API frontend/proxy.
- VÃ©rifier disponibilitÃ© Redis.
- VÃ©rifier rÃ©vision Alembic courante.
- VÃ©rifier recompute retention en environnement dÃ©ployÃ©.
- VÃ©rifier fraÃ®cheur artefacts ML.
- Tester import CSV en staging dâ€™abord.
- VÃ©rifier rÃ´les admin avant opÃ©rations management/import.
- VÃ©rifier cap plage anomalies cÃ´tÃ© dashboard.
- VÃ©rifier hypothÃ¨ses NRR avec Ã©quipe finance.
- VÃ©rifier hypothÃ¨ses attribution campagnes.
- VÃ©rifier cohÃ©rence churn_type sur toute la chaÃ®ne.
- VÃ©rifier valeur TTL token effective.
- VÃ©rifier prÃ©sence index en prod (pg_indexes).
- VÃ©rifier mapping services source->analytics post ETL.

## Annexe D â€” Marqueurs de VÃ©rification

- Style retenu : â€œÃ  vÃ©rifierâ€ ou â€œÃ  vÃ©rifier en environnementâ€.
- UtilisÃ© pour ce qui nâ€™est pas directement observable dans le code du dÃ©pÃ´t.

## Annexe E â€” Carte de Navigation Minimale

- Backend root : user-analytics-backend/app.
- Core : user-analytics-backend/app/core.
- Routers : user-analytics-backend/app/routers.
- Models : user-analytics-backend/app/models.
- Repositories : user-analytics-backend/app/repositories.
- Services : user-analytics-backend/app/services.
- Schemas : user-analytics-backend/app/schemas.
- ETL : user-analytics-backend/scripts/etl.
- Migrations : user-analytics-backend/alembic/versions.
- ML : user-analytics-backend/ml_models.
- Front root : analytics-platform-front/src.
- Hooks : analytics-platform-front/src/hooks.
- Pages : analytics-platform-front/src/pages.
- Guards routes : analytics-platform-front/src/router.
- Services front : analytics-platform-front/src/services.

## Annexe F â€” Statut de Couverture du Document

- Section 1 : oui.
- Section 2 : oui.
- Section 3 : oui.
- Section 4 : oui.
- Section 5 : oui.
- Section 6 : oui.
- Section 7 : oui.
- Section 8 : oui.
- Section 9 : oui.
- Section 10 : oui.
- Section 11 : oui.
- Section 12 : oui.
- Section 13 : oui.
- Annexes de handoff : oui.

