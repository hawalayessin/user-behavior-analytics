# Rapport d'Avancement - PFE 2025/2026

## Plateforme d'Analytics Comportementale - DigMaco

**Date** : 09/04/2026
**Etudiant** : [NON TROUVE - A VERIFIER]
**Encadrant** : [NON TROUVE - A VERIFIER]
**Avancement global** : 83.55%

---

## Pre-checks demandes avant analyse

Les commandes demandees ont ete executees avant generation du rapport.

1. Nombre de fichiers Python dans `user-analytics-backend/app` : **69**
2. Nombre de fichiers JSX dans `analytics-platform-front/src/pages` : **17**
3. Nombre d'entrees dans `user-analytics-backend/tests` : **2**
4. Presence de `user-analytics-backend/ml_models/churn_model.joblib` : **True**
5. Presence de `docker-compose.yml` : **True**

Interpretation rapide:

- Le backend est volumineux et modulaire.
- Le frontend pages est deja avance.
- La couche tests est faible en volume.
- Le modele churn est present sur disque.
- Le projet est containerise.

---

## Resume Executif

Le projet presente un niveau d'avancement solide sur la chaine principale ETL -> API -> Frontend.
Le socle backend FastAPI est structure par routers, services et repositories.
Le frontend React couvre les ecrans metiers attendus (overview, churn, retention, trial, campaign, subscribers, admin).
La gestion des dates analytiques via ancre de donnees est implantee, ce qui reduit les biais lies a l'horloge systeme.
Les modules IA ne sont pas au stade prototype seulement: le churn prediction expose des endpoints train/metrics/scores et un modele joblib est disponible.
La segmentation K-Means est aussi implementee cote service et repository, avec persistance de modele.
L'anomaly detection est basee sur z-score dans une route dediee avec vues summary/timeline/distribution/details.
La securite d'authentification JWT est en place et les roles sont definis (admin/analyst), mais la couverture d'autorisation n'est pas uniforme sur toutes les routes analytics.
Le principal risque technique avant soutenance est la performance sur des endpoints couteux, avec des latences observees superieures a 3s sur trial KPIs et user activity.
Le second risque majeur est la couverture de tests: un seul vrai fichier de test dans le backend.
Le deploiement Docker est fonctionnel et les services backend/frontend/redis existent en compose.
Les KPI de la page Subscribers qui etaient mock ont ete relies au backend recemment.
Le projet est donc crediblement soutenable en intermediaire, mais doit encore traiter performance + tests + hardening securite pour une soutenance finale solide.
Estimation realiste: les objectifs principaux sont atteignables si les points critiques sont traites dans les 2 a 4 prochaines semaines.

---

## 1. Tableau de Bord des Livrables

| #   | Livrable                                          | Statut | Completion | Fichiers cles                                                                                                                           |
| --- | ------------------------------------------------- | ------ | ---------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| L1  | Connexion prod_db (lecture seule)               | âœ…     | 90%        | user-analytics-backend/app/core/config.py, user-analytics-backend/.env                                                                  |
| L2  | Script ETL complet prod_db -> analytics_db         | âœ…     | 85%        | user-analytics-backend/scripts/etl/etl_prod_to_analytics.py                                                                             |
| L3  | Modeles SQLAlchemy + migrations Alembic           | âœ…     | 92%        | user-analytics-backend/app/models/, user-analytics-backend/alembic/versions/                                                            |
| L4  | API FastAPI avec endpoints analytics              | âœ…     | 88%        | user-analytics-backend/app/routers/                                                                                                     |
| L5  | Helper temporel (anchor MAX event_datetime)       | âœ…     | 95%        | user-analytics-backend/app/utils/temporal.py                                                                                            |
| L6  | Dashboard Overview (WAU, MAU, revenus)            | âœ…     | 88%        | analytics-platform-front/src/pages/dashboard/DashboardPage.jsx                                                                          |
| L7  | Section User Activity (DAU, WAU, MAU, Stickiness) | âœ…     | 86%        | analytics-platform-front/src/pages/UserActivityPage.jsx                                                                                 |
| L8  | Section Churn Analysis (taux, courbe, raisons)    | âœ…     | 85%        | analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx                                                                      |
| L9  | Section Retention (cohortes, heatmap, courbe)     | âœ…     | 84%        | analytics-platform-front/src/pages/dashboard/RetentionPage.jsx                                                                          |
| L10 | Section Free Trial Behavior                       | âœ…     | 86%        | analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx                                                                  |
| L11 | Section Campaign Impact                           | âœ…     | 84%        | analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx                                                                     |
| L12 | Section Cross-Service Behavior                    | âš™ï¸     | 72%        | analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx, user-analytics-backend/app/routers/cross_service.py          |
| L13 | Module IA : Prediction Churn (ML)                 | âœ…     | 87%        | user-analytics-backend/ml_models/churn_predictor.py, user-analytics-backend/app/routers/ml_churn.py                                     |
| L14 | Module IA : Segmentation K-Means                  | âœ…     | 82%        | user-analytics-backend/app/services/segmentation_service.py                                                                             |
| L15 | Module IA : Detection d'Anomalies Z-Score         | âœ…     | 78%        | user-analytics-backend/app/routers/anomalies.py                                                                                         |
| L16 | Systeme Auth JWT (Admin / Viewer)                 | âš™ï¸     | 80%        | user-analytics-backend/app/routers/auth.py, user-analytics-backend/app/core/dependencies.py                                             |
| L17 | Export CSV / Excel des KPIs                       | âœ…     | 83%        | analytics-platform-front/src/components/subscribers/UserListSection.jsx, analytics-platform-front/src/pages/dashboard/RetentionPage.jsx |
| L18 | Generation de rapports PDF                        | âŒ     | 10%        | docs/tmp/generate_rapport.py [hors pipeline produit]                                                                                    |
| L19 | Tests unitaires (pytest)                          | âš™ï¸     | 20%        | user-analytics-backend/tests/test_churn_anchor_logic.py                                                                                 |
| L20 | Documentation technique                           | âœ…     | 78%        | docs/\*.md, PROJECT_REPORT.md                                                                                                           |
| L21 | Docker / Deploiement                              | âœ…     | 82%        | docker-compose.yml, user-analytics-backend/Dockerfile, analytics-platform-front/Dockerfile                                              |
| L22 | Page Subscribers (lookup utilisateur)             | âœ…     | 86%        | analytics-platform-front/src/pages/SubscribersPage.jsx, user-analytics-backend/app/routers/users.py                                     |
| L23 | Page Management (services + campagnes)            | âœ…     | 84%        | analytics-platform-front/src/pages/admin/ManagementPage.jsx, user-analytics-backend/app/routers/management.py                           |
| L24 | Page Import Data (controle ETL)                   | âœ…     | 83%        | analytics-platform-front/src/pages/admin/ImportDataPage.jsx, user-analytics-backend/app/routers/admin_import.py                         |
| L25 | Page Platform Users (admin)                       | âœ…     | 82%        | analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx, user-analytics-backend/app/routers/platform_user.py            |

Notes transverses par livrable:

- La majorite des livrables sont implementes fonctionnellement.
- Les ecarts restants concernent surtout testabilite, perf, securite fine, et industrialisation de reporting PDF.
- Le statut "Termine" ici signifie code present et branche principalement integree, pas forcement niveau production hardening total.

---

## 2. Avancement par Module

### 2.1 ETL Pipeline - 85%

Etat general:

- Pipeline ETL riche, avec plusieurs scripts specialises.
- Presence d'un ETL principal et de scripts de correction/mapping.
- Logique de recalcul cohorte disponible.

Scripts ETL identifies:

- user-analytics-backend/scripts/etl/etl_prod_to_analytics.py
- user-analytics-backend/scripts/etl/etl_subscriptions_to_unsubscriptions.py
- user-analytics-backend/scripts/etl/etl_sms_events_from_hawala.py
- user-analytics-backend/scripts/etl/etl_sms_events_fixed.py
- user-analytics-backend/scripts/etl/etl_sms_events_only.py
- user-analytics-backend/scripts/etl/fix_services_mapping.py
- user-analytics-backend/scripts/etl/link_campaigns_to_subscriptions.py
- user-analytics-backend/scripts/etl/recalcul_cohorts.py
- user-analytics-backend/scripts/etl/seed_campaigns.py
- user-analytics-backend/scripts/compute_cohorts.py
- user-analytics-backend/scripts/verify_data.py

Tables source (constatees dans scripts/docs):

- prod_db users
- prod_db subscriptions
- prod_db billing/transactions
- prod_db sms events
- [NON TROUVE - A VERIFIER] sur certaines tables annexes exactes

Tables cibles analytics:

- users
- subscriptions
- unsubscriptions
- user_activities
- billing_events
- sms_events
- services
- service_types
- campaigns
- cohorts

Transformation mapping type1/type2/type4:

- Mentionnee dans docs et scripts ETL.
- Les valeurs sont mappees vers event_type/activity_type selon contexte.
- Les details exacts de toutes les regles ne sont pas toutes centralisees dans un seul document canonique.

Gestion erreurs / retry:

- Detection d'erreurs presente.
- Validation partielle via verify_data.py.
- Retry systematique unifie [NON TROUVE - A VERIFIER].

Mode demo:

- Flag --demo global ETL [NON TROUVE - A VERIFIER].
- Certains scripts de seed/test existent.

Points forts:

- Bonne separation ETL principal vs scripts utilitaires.
- Capacite de correction incremental.
- Presence de compute/recompute cohorts.

Points faibles:

- Standardisation logs ETL inegale.
- Gouvernance des mappings metier partiellement dispersee.
- Tests automatises ETL faibles.

Ce qui reste a faire:

- Ajouter tests ETL par table critique.
- Ecrire un document de mapping canonique unique.
- Ajouter dry-run/preview standard.
- Ajouter indicateurs de volumetrie/temps par etape.

### 2.2 Backend API - 88%

Etat general:

- API riche en endpoints metiers.
- Decoupage correct routers/services/repositories.
- Cache present sur endpoints analytiques critiques.

Routers detectes:

- user-analytics-backend/app/routers/admin_import.py
- user-analytics-backend/app/routers/analyticsOverview.py
- user-analytics-backend/app/routers/anomalies.py
- user-analytics-backend/app/routers/auth.py
- user-analytics-backend/app/routers/campaign_impact.py
- user-analytics-backend/app/routers/campaign_upload.py
- user-analytics-backend/app/routers/churn_analysis.py
- user-analytics-backend/app/routers/cross_service.py
- user-analytics-backend/app/routers/management.py
- user-analytics-backend/app/routers/ml_churn.py
- user-analytics-backend/app/routers/platform_user.py
- user-analytics-backend/app/routers/retention.py
- user-analytics-backend/app/routers/segmentation.py
- user-analytics-backend/app/routers/service.py
- user-analytics-backend/app/routers/trialAnalytics.py
- user-analytics-backend/app/routers/userActivity.py
- user-analytics-backend/app/routers/users.py

Repository/services coupling:

- churn routers relies on repositories churn_repo.py.
- campaign routers relies on campaign_repo.py and campaign_service.py.
- segmentation routers relies on segmentation_service.py and segmentation_repo.py.
- platform user router relies on platform_user_service.py.

Auth protection:

- Auth implemented and require_admin present.
- Protection coverage is partial depending on endpoint family.

Endpoints manquants:

- Endpoint NRR dedie [NON TROUVE - A VERIFIER].
- Endpoint PDF report generation dedie [NON TROUVE - A VERIFIER].

### 2.3 Base de Donnees - 86%

Modeles SQLAlchemy presents:

- analytics.py
- billing_events.py
- campaigns.py
- cohorts.py
- import_logs.py
- platform_users.py
- services.py
- service_types.py
- sms_events.py
- subscriptions.py
- unsubscriptions.py
- users.py
- user_activities.py

Migrations Alembic presentes:

- 3939f80c5a66_seeders.py
- b7e2c4f91a10_add_campaign_targets_table.py
- 8ce268d4732a_initial_migration.py
- 85b71708c64d_add_performance_indexes_p0.py
- 6c076db13bed_add_analytics_performance_indexes.py
- 4b9e2f7a1d3c_sms_events_hawala_lean_model_and_indexes.py
- f1a2b3c4d5e6_fix_subscription_status_and_created_at.py
- dff7e0993f3d_initial_migration1.py
- ded5564102c8_initial_migration3.py
- c1f4a2d9e8b1_extend_sms_events_for_otp_ussd_web_activation.py

Index de performance:

- Ajouts explicites dans migrations "performance indexes".
- Index coverage sur gros volumes en progression.

Points a verifier:

- Exhaustivite des indexes composites sur chemins tres lents.
- Coherence indexes vs clauses where les plus frequentes.

### 2.4 KPIs Analytiques - 82%

KPIs forts:

- DAU, WAU, MAU, Stickiness.
- Churn core KPIs.
- Trial conversion/dropoff.
- Retention cohort heatmap/curve.
- ARPU current month via overview/revenue.

KPIs partiels ou absents:

- Campaign ROI strict (si cout campagne absent) partiel.
- NRR absent.

Raccordement front-back:

- Large couverture via hooks dedies.
- Plusieurs pages presentent loading/error states.

### 2.5 Frontend React - 84%

Pages detectees (17):

- analytics-platform-front/src/pages/Dashboard.jsx
- analytics-platform-front/src/pages/RootRedirect.jsx
- analytics-platform-front/src/pages/SubscribersPage.jsx
- analytics-platform-front/src/pages/UserActivityPage.jsx
- analytics-platform-front/src/pages/admin/ImportDataPage.jsx
- analytics-platform-front/src/pages/admin/ManagementPage.jsx
- analytics-platform-front/src/pages/auth/LoginPage.jsx
- analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx
- analytics-platform-front/src/pages/dashboard/AnomalyDetectionPage.jsx
- analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx
- analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx
- analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx
- analytics-platform-front/src/pages/dashboard/DashboardPage.jsx
- analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx
- analytics-platform-front/src/pages/dashboard/RetentionPage.jsx
- analytics-platform-front/src/pages/dashboard/UserSegmentationPage.jsx
- analytics-platform-front/src/pages/platform-users/PlatformUsersPage.jsx

Etat:

- Fonctionnel sur toutes les pages principales.
- Certaines pages tres denses avec logique etat locale importante.

Ce qui reste:

- Uniformiser le pattern React Query partout.
- Harmoniser conventions API/fetch.
- Ajouter tests composants.

### 2.6 Modules IA - 82%

Churn prediction:

- Algorithme: LogisticRegression (scikit-learn).
- Features engineering SQL present.
- Train + metrics + scores endpoints presents.
- Modele joblib present.

Segmentation:

- KMeans present dans service.
- Persistance modele segmentation_kmeans.joblib.
- Endpoints kpis/clusters/profiles/train presents.

Anomalies:

- Detection z-score implementee.
- Endpoints summary/timeline/distribution/heatmap/details/insights/run-detection.

Gaps:

- MLOps lifecycle (versioning, drift monitor) [NON TROUVE - A VERIFIER].
- Benchmarks et evals continues [NON TROUVE - A VERIFIER].

### 2.7 Authentification - 80%

Observe:

- JWT decode/verify present.
- require_admin present.
- role field in platform users.

Points faibles:

- Fallback DATABASE_URL dans code avec credentials dev.
- Couverture RBAC pas toujours explicite sur analytics endpoints.

### 2.8 Tests - 20%

Etat:

- Dossier tests present.
- Fichiers:
  - user-analytics-backend/tests/**init**.py
  - user-analytics-backend/tests/test_churn_anchor_logic.py

Constat:

- Tests backend quasi absents hors bloc churn anchor.
- Pas de suite front test visible dans la demande analysee.

Risque:

- Regressions difficiles a controler avant soutenance finale.

### 2.9 Docker & Deploiement - 82%

Elements:

- docker-compose.yml present.
- Backend dockerfile present.
- Frontend dockerfile present.
- Service Redis compose present.

Points positifs:

- Environnement local reproducible.
- volumes pour dev iteration.

Points a corriger:

- Secrets admin dans compose (dev) a securiser en production.
- Hardening runtime/probes [NON TROUVE - A VERIFIER].

### 2.10 Documentation - 78%

Docs identifies:

- docs/architecture.md
- docs/etl_prod_readme.md
- docs/kpis.md
- docs/ml_churn_report.md
- docs/REAL_DATA_INTEGRATION.md
- docs/TRIAL_INTEGRATION_SUMMARY.md
- PROJECT_REPORT.md

Qualite:

- Bonne densite sur architecture/KPI/ML.
- Besoin d'un plan de maintenance docs continue.

---

## 3. Analyse des Performances

### Latences mesurees (depuis logs fournis)

| Endpoint                 | Latence | Seuil cible | Statut |
| ------------------------ | ------- | ----------- | ------ |
| /analytics/trial/kpis    | 5266ms  | <500ms      | âŒ     |
| /analytics/trial/kpis    | 3984ms  | <500ms      | âŒ     |
| /analytics/user-activity | 3257ms  | <500ms      | âŒ     |

### Causes identifiees dans le code

#### Endpoint: /analytics/trial/kpis

Fichier:

- user-analytics-backend/app/routers/trialAnalytics.py

Causes probables:

- Requetes agregees lourdes sur subscriptions sans materialisation.
- Plusieurs calculs date-range sur grandes fenetres.
- Risque de scans couteux sur status/date si index composite insuffisant.

Indices techniques:

- Fichier long avec multiples CTE/aggregations.
- Endpoint centralise plusieurs KPI en un seul appel.
- Latence reproduite dans logs fournis.

Correctifs recommandes:

- Ajouter cache endpoint avec TTL adapte.
- Verifier et completer index composites (start_date, status, service_id).
- Eventuellement precalcul table/materialized view trial KPIs.
- Segmenter calculs lourds si necessaire.

#### Endpoint: /analytics/user-activity

Fichier:

- user-analytics-backend/app/routers/userActivity.py

Causes probables:

- Calcul DAU/WAU/MAU sur plages larges avec count distinct.
- Heatmap/trend sur volume user_activities eleve.
- Jointures/aggregations temporelles potentiellement lourdes.

Correctifs recommandes:

- Index sur (activity_datetime, user_id, service_id).
- Limiter fenetre max par API ou imposer defaults anchor stricte.
- Cache serveur et/ou pre-aggregation quotidienne.
- Optimiser serialization et payload pour front.

### Exemples de correctifs code exacts (indicatifs)

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ua_dt_user_service
ON user_activities (activity_datetime DESC, user_id, service_id);
```

```python
# Exemple pattern cache endpoint
@cached_endpoint("trial_kpis", ttl_seconds=3600, key_builder=lambda **k: f"trial:{k}")
def get_trial_kpis(...):
    ...
```

```sql
-- Pre-aggregation quotidienne
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_activity_daily AS
SELECT
  DATE(activity_datetime) AS day,
  COUNT(DISTINCT user_id) AS dau
FROM user_activities
GROUP BY 1;
```

---

## 4. Problemes Critiques

### ðŸ”´ CRITIQUE - Bloquant pour la soutenance

1. Faible couverture de tests automatisee

- Fichier: user-analytics-backend/tests/test_churn_anchor_logic.py
- Impact: risque regression eleve lors des changements rapides
- Fix: ajouter suites pytest pour routers critiques et services

2. Latences elevees endpoints cles

- Fichiers: user-analytics-backend/app/routers/trialAnalytics.py, user-analytics-backend/app/routers/userActivity.py
- Impact: UX degradee et demos risquees
- Fix: index + cache + pre-aggregation

3. Credentials dev en fallback code DB

- Fichier: user-analytics-backend/app/core/database.py
- Ligne indicative: bloc DATABASE_URL default
- Impact: hygiene securite faible pour environnement non maitrise
- Fix: supprimer fallback sensible et imposer env obligatoire

### ðŸŸ  HAUTE PRIORITE - Impact significatif

1. Couverture RBAC non uniforme sur toutes routes analytics

- Fichiers: routers analytics multiples
- Impact: controle acces potentiellement trop large
- Fix: standardiser dependencies auth selon role

2. Reporting PDF produit non finalise

- Fichiers: [NON TROUVE - A VERIFIER] pipeline rapport produit
- Impact: exigence livrable potentiellement incomplete
- Fix: endpoint dedie + template PDF stable

3. NRR non expose comme KPI natif

- Fichiers: docs/kpis.md, routers analytics
- Impact: manque de KPI business soutenance
- Fix: ajouter SQL + endpoint + hook + carte UI

### ðŸŸ¡ MOYENNE PRIORITE - Amelioration recommandee

1. Uniformisation de fetch patterns front

- Fichiers: hooks multiples
- Impact: maintenance et coherence
- Fix: React Query standard partout

2. Documentation runbook ops

- Fichiers: docs/\*.md
- Impact: passation et exploitation
- Fix: runbook erreurs frequentes + monitoring

3. Tests frontend absents

- Fichiers: analytics-platform-front/src/\*\*
- Impact: regressions UI non detectees
- Fix: RTL + tests smoke par page

---

## 5. Checklist Soutenance

### Cette semaine (obligatoire)

- [ ] Stabiliser latence /analytics/trial/kpis < 800ms en cache chaud
- [ ] Stabiliser latence /analytics/user-activity < 800ms en cache chaud
- [ ] Ajouter au moins 10 tests pytest sur routes critiques
- [ ] Verifier RBAC sur toutes routes admin/analytics
- [ ] Retirer fallback credentials sensibles du code
- [ ] Ajouter une slide technique sur anchor date et perimetre data
- [ ] Documenter KPI sources dans un tableau unique
- [ ] Verifier demo e2e Docker sur machine propre

### Avant la soutenance (recommande)

- [ ] Ajouter KPI NRR (SQL + endpoint + hook + UI)
- [ ] Completer reporting PDF si exige explicitement
- [ ] Ajouter monitoring simple (latence p95 endpoint)
- [ ] Ajouter tests frontend smoke (login, dashboard, subscribers)
- [ ] Harmoniser les messages d'erreur API
- [ ] Ajouter matrice role->endpoint dans docs securite
- [ ] Stabiliser imports ETL via template de validation schema

### Nice to have

- [ ] Materialized views pour KPIs lourds
- [ ] Versionning des modeles ML avec metadata
- [ ] Tableau de drift model churn
- [ ] Profiling SQL automatise en CI

---

## 6. Estimation d'Avancement Global

Methode:

- Score module = Poids x Completion.
- Completion module fondee sur preuves code + integration + risques residuels.

| Module           | Poids    | Completion | Score     |
| ---------------- | -------- | ---------- | --------- |
| ETL              | 15%      | 85%        | 12.75     |
| Backend API      | 20%      | 88%        | 17.60     |
| Base de donnees  | 10%      | 86%        | 8.60      |
| KPIs analytiques | 15%      | 82%        | 12.30     |
| Frontend         | 15%      | 84%        | 12.60     |
| Modules IA       | 15%      | 82%        | 12.30     |
| Auth & Securite  | 5%       | 80%        | 4.00      |
| Tests            | 5%       | 20%        | 1.00      |
| **TOTAL**        | **100%** | **83.55%** | **83.55** |

Lecture de ce score:

- Le socle est solide pour une soutenance intermediaire.
- Les deltas restants sont concentres et traitables.
- Le principal frein au passage production est la qualite non-fonctionnelle (tests/perf/securite fine).

---

## 7. Recommandations pour l'Encadrant

1. Valider l'orientation technique generale

- L'architecture est cohente et suffisamment avancee.
- Le projet ne semble pas au stade "prototype vide".

2. Exiger un sprint qualite court avant prochaine evaluation

- Axe 1: tests minimaux automatises.
- Axe 2: optimisation endpoints lents.
- Axe 3: securite config (suppression fallback sensibles).

3. Focus soutenance

- Demander une demo live de 3 flux:
  - ETL import controle
  - Dashboard analytics complet
  - Prediction churn + interpretation

4. Evaluer la maitrise data

- Demander justification des KPIs et de leurs limites.
- Demander la trace source->transform->endpoint->widget.

5. Evaluer la robustesse

- Demander scenario panne redis + degradations.
- Demander scenario payload volumineux subscribers export.

Conclusion encadrant:

- Projet globalement bien engage.
- Risques connus et maitrisables.
- Priorite immediate: transformer une bonne base fonctionnelle en base fiable et defendable techniquement.

---

## Annexes Techniques

## Annexe A - Inventaire complet des routers

1. user-analytics-backend/app/routers/admin_import.py
2. user-analytics-backend/app/routers/analyticsOverview.py
3. user-analytics-backend/app/routers/anomalies.py
4. user-analytics-backend/app/routers/auth.py
5. user-analytics-backend/app/routers/campaign_impact.py
6. user-analytics-backend/app/routers/campaign_upload.py
7. user-analytics-backend/app/routers/churn_analysis.py
8. user-analytics-backend/app/routers/cross_service.py
9. user-analytics-backend/app/routers/management.py
10. user-analytics-backend/app/routers/ml_churn.py
11. user-analytics-backend/app/routers/platform_user.py
12. user-analytics-backend/app/routers/retention.py
13. user-analytics-backend/app/routers/segmentation.py
14. user-analytics-backend/app/routers/service.py
15. user-analytics-backend/app/routers/trialAnalytics.py
16. user-analytics-backend/app/routers/userActivity.py
17. user-analytics-backend/app/routers/users.py

## Annexe B - Endpoints detailles (method + path)

### analyticsOverview.py

1. GET /analytics/summary
2. GET /analytics/overview
3. POST /analytics/cache/invalidate

### userActivity.py

4. GET /analytics/user-activity

### trialAnalytics.py

5. GET /analytics/trial/kpis
6. GET /analytics/trial/timeline
7. GET /analytics/trial/by-service
8. GET /analytics/trial/users
9. GET /analytics/trial/dropoff-by-day
10. GET /analytics/churn/breakdown

### campaign_upload.py

11. POST /admin/upload-targets

### users.py

12. GET /users
13. GET /users/trial
14. GET /users/{user_id}

### anomalies.py

15. GET /anomalies/summary
16. GET /anomalies/timeline
17. GET /anomalies/distribution
18. GET /anomalies/heatmap
19. GET /anomalies/details
20. GET /anomalies/insights
21. POST /anomalies/run-detection

### auth.py

22. POST /auth/register
23. POST /auth/login

### admin_import.py

24. POST /admin/import/csv
25. POST /admin/import/csv/confirm
26. POST /admin/import/database
27. GET /admin/import/history
28. GET /admin/import/template/{table}

### cross_service.py

29. GET /analytics/cross-service/overview
30. GET /analytics/cross-service/co-subscriptions
31. GET /analytics/cross-service/migrations
32. GET /analytics/cross-service/distribution
33. GET /analytics/cross-service/all

### campaign_impact.py

34. GET /analytics/campaigns/dashboard
35. GET /analytics/campaigns/list
36. GET /analytics/campaigns/overview
37. GET /analytics/campaigns/by-type
38. GET /analytics/campaigns/top
39. GET /analytics/campaigns/trend
40. GET /analytics/campaigns/kpis
41. GET /analytics/campaigns/performance
42. GET /analytics/campaigns/comparison
43. GET /analytics/campaigns/timeline

### churn_analysis.py

44. GET /analytics/churn/dashboard
45. GET /analytics/churn/kpis
46. GET /analytics/churn/trend
47. GET /analytics/churn/by-service
48. GET /analytics/churn/lifetime
49. GET /analytics/churn/retention

### platform_user.py

50. GET /platform-users/
51. GET /platform-users/{user_id}
52. POST /platform-users/
53. PUT /platform-users/{user_id}
54. PATCH /platform-users/{user_id}/status
55. PATCH /platform-users/{user_id}/role
56. DELETE /platform-users/{user_id}

### segmentation.py

57. GET /analytics/segmentation/kpis
58. GET /analytics/segmentation/clusters
59. GET /analytics/segmentation/profiles
60. POST /analytics/segmentation/train

### ml_churn.py

61. POST /ml/churn/train
62. GET /ml/churn/metrics
63. GET /ml/churn/scores
64. POST /ml/churn/scores/recompute

### retention.py

65. GET /analytics/retention/kpis
66. GET /analytics/retention/heatmap
67. GET /analytics/retention/curve
68. GET /analytics/retention/cohorts-list

### management.py

69. GET /admin/management/services
70. POST /admin/management/services
71. PUT /admin/management/services/{service_id}
72. DELETE /admin/management/services/{service_id}
73. GET /admin/management/campaigns
74. POST /admin/management/campaigns
75. PUT /admin/management/campaigns/{campaign_id}
76. DELETE /admin/management/campaigns/{campaign_id}

### service.py

77. GET /

## Annexe C - Hooks frontend inventaire complet

1. analytics-platform-front/src/hooks/useAnomalies.js
2. analytics-platform-front/src/hooks/useCampaignComparison.js
3. analytics-platform-front/src/hooks/useCampaignImpactDashboard.js
4. analytics-platform-front/src/hooks/useCampaignKPIs.js
5. analytics-platform-front/src/hooks/useCampaignPerformance.js
6. analytics-platform-front/src/hooks/useCampaignTimeline.js
7. analytics-platform-front/src/hooks/useChurnBreakdown.js
8. analytics-platform-front/src/hooks/useChurnCurve.js
9. analytics-platform-front/src/hooks/useChurnDashboard.js
10. analytics-platform-front/src/hooks/useChurnKPIs.js
11. analytics-platform-front/src/hooks/useChurnPredictionMetrics.js
12. analytics-platform-front/src/hooks/useChurnPredictionScores.js
13. analytics-platform-front/src/hooks/useChurnPredictionTrain.js
14. analytics-platform-front/src/hooks/useChurnReasons.js
15. analytics-platform-front/src/hooks/useCohortsTable.js
16. analytics-platform-front/src/hooks/useCrossService.js
17. analytics-platform-front/src/hooks/useDashboardMetrics.js
18. analytics-platform-front/src/hooks/useImportData.js
19. analytics-platform-front/src/hooks/useManagement.js
20. analytics-platform-front/src/hooks/useOverview.js
21. analytics-platform-front/src/hooks/useRetentionCurve.js
22. analytics-platform-front/src/hooks/useRetentionHeatmap.js
23. analytics-platform-front/src/hooks/useRetentionKPIs.js
24. analytics-platform-front/src/hooks/useRiskSegments.js
25. analytics-platform-front/src/hooks/useSegmentationClusters.js
26. analytics-platform-front/src/hooks/useSegmentationKPIs.js
27. analytics-platform-front/src/hooks/useSegmentationProfiles.js
28. analytics-platform-front/src/hooks/useSubscribersKPIs.js
29. analytics-platform-front/src/hooks/useTimeToChurn.js
30. analytics-platform-front/src/hooks/useToast.jsx
31. analytics-platform-front/src/hooks/useTrialDropoffByDay.js
32. analytics-platform-front/src/hooks/useTrialKPIs.js
33. analytics-platform-front/src/hooks/useTrialUsers.js
34. analytics-platform-front/src/hooks/useUserActivity.js
35. analytics-platform-front/src/hooks/useUsers.js

## Annexe D - Mapping hooks -> endpoints

1. useUserActivity -> GET /analytics/user-activity
2. useOverview -> GET /analytics/overview
3. useTrialKPIs -> GET /analytics/trial/kpis
4. useTrialUsers -> GET /users/trial
5. useTrialDropoffByDay -> GET /analytics/trial/dropoff-by-day
6. useRetentionKPIs -> GET /analytics/retention/kpis
7. useRetentionHeatmap -> GET /analytics/retention/heatmap
8. useRetentionCurve -> GET /analytics/retention/curve
9. useCohortsTable -> GET /analytics/retention/cohorts-list
10. useChurnDashboard -> GET /analytics/churn/dashboard
11. useChurnKPIs -> GET /analytics/churn/kpis
12. useChurnBreakdown -> GET /analytics/churn/breakdown
13. useChurnCurve -> GET /analytics/churn/curve
14. useTimeToChurn -> GET /analytics/churn/lifetime
15. useChurnReasons -> GET /analytics/churn/breakdown
16. useCampaignImpactDashboard -> GET /analytics/campaigns/dashboard
17. useCampaignKPIs -> GET /analytics/campaigns/kpis
18. useCampaignTimeline -> GET /analytics/campaigns/timeline
19. useCampaignComparison -> GET /analytics/campaigns/comparison
20. useCampaignPerformance -> GET /analytics/campaigns/performance
21. useCrossService -> GET /analytics/cross-service/all
22. useSegmentationKPIs -> GET /analytics/segmentation/kpis
23. useSegmentationClusters -> GET /analytics/segmentation/clusters
24. useSegmentationProfiles -> GET /analytics/segmentation/profiles
25. useAnomalies -> GET /anomalies/summary
26. useAnomalies -> GET /anomalies/timeline
27. useAnomalies -> GET /anomalies/distribution
28. useAnomalies -> GET /anomalies/heatmap
29. useAnomalies -> GET /anomalies/details
30. useAnomalies -> GET /anomalies/insights
31. useChurnPredictionMetrics -> GET /ml/churn/metrics
32. useChurnPredictionScores -> GET /ml/churn/scores
33. useChurnPredictionTrain -> POST /ml/churn/train
34. useUsers -> GET /users
35. useSubscribersKPIs -> GET /analytics/overview
36. useImportData -> GET /admin/import/history
37. useImportData -> POST /admin/import/csv
38. useImportData -> POST /admin/import/csv/confirm
39. useImportData -> POST /admin/import/database
40. useImportData -> GET /admin/import/template/{table}
41. useManagement -> GET /admin/management/services
42. useManagement -> GET /admin/management/campaigns
43. useManagement -> POST /admin/management/services
44. useManagement -> PUT /admin/management/services/{id}
45. useManagement -> DELETE /admin/management/services/{id}
46. useManagement -> POST /admin/management/campaigns
47. useManagement -> PUT /admin/management/campaigns/{id}
48. useManagement -> DELETE /admin/management/campaigns/{id}
49. useManagement -> POST /admin/management/campaigns/upload-targets

## Annexe E - Pages frontend et etat

1. Dashboard.jsx -> Partiel (page legacy wrapper)
2. RootRedirect.jsx -> Fonctionnel
3. SubscribersPage.jsx -> Fonctionnel (KPI backend relies)
4. UserActivityPage.jsx -> Fonctionnel
5. admin/ImportDataPage.jsx -> Fonctionnel
6. admin/ManagementPage.jsx -> Fonctionnel
7. auth/LoginPage.jsx -> Fonctionnel
8. dashboard/AIChurnInsights.jsx -> Fonctionnel
9. dashboard/AnomalyDetectionPage.jsx -> Fonctionnel
10. dashboard/CampaignImpactPage.jsx -> Fonctionnel
11. dashboard/ChurnAnalysisPage.jsx -> Fonctionnel
12. dashboard/CrossServiceBehaviorPage.jsx -> Fonctionnel partiel
13. dashboard/DashboardPage.jsx -> Fonctionnel
14. dashboard/FreeTrialBehaviorPage.jsx -> Fonctionnel
15. dashboard/RetentionPage.jsx -> Fonctionnel
16. dashboard/UserSegmentationPage.jsx -> Fonctionnel
17. platform-users/PlatformUsersPage.jsx -> Fonctionnel

## Annexe F - Inventaire modeles SQLAlchemy

1. user-analytics-backend/app/models/users.py
2. user-analytics-backend/app/models/subscriptions.py
3. user-analytics-backend/app/models/unsubscriptions.py
4. user-analytics-backend/app/models/user_activities.py
5. user-analytics-backend/app/models/billing_events.py
6. user-analytics-backend/app/models/services.py
7. user-analytics-backend/app/models/service_types.py
8. user-analytics-backend/app/models/sms_events.py
9. user-analytics-backend/app/models/campaigns.py
10. user-analytics-backend/app/models/cohorts.py
11. user-analytics-backend/app/models/import_logs.py
12. user-analytics-backend/app/models/platform_users.py
13. user-analytics-backend/app/models/analytics.py
14. user-analytics-backend/app/models/**init**.py

## Annexe G - Migrations Alembic details

1. 8ce268d4732a_initial_migration.py
2. dff7e0993f3d_initial_migration1.py
3. ded5564102c8_initial_migration3.py
4. 3939f80c5a66_seeders.py
5. 4b9e2f7a1d3c_sms_events_hawala_lean_model_and_indexes.py
6. b7e2c4f91a10_add_campaign_targets_table.py
7. c1f4a2d9e8b1_extend_sms_events_for_otp_ussd_web_activation.py
8. 85b71708c64d_add_performance_indexes_p0.py
9. 6c076db13bed_add_analytics_performance_indexes.py
10. f1a2b3c4d5e6_fix_subscription_status_and_created_at.py

## Annexe H - Inventaire repositories/services/schemas

### Repositories

1. user-analytics-backend/app/repositories/churn_repo.py
2. user-analytics-backend/app/repositories/campaign_repo.py
3. user-analytics-backend/app/repositories/segmentation_repo.py
4. user-analytics-backend/app/repositories/**init**.py

### Services

1. user-analytics-backend/app/services/campaign_service.py
2. user-analytics-backend/app/services/churn_service.py
3. user-analytics-backend/app/services/platform_user_service.py
4. user-analytics-backend/app/services/segmentation_service.py
5. user-analytics-backend/app/services/**init**.py

### Schemas

1. user-analytics-backend/app/schemas/auth.py
2. user-analytics-backend/app/schemas/users.py
3. user-analytics-backend/app/schemas/Subscriptions.py
4. user-analytics-backend/app/schemas/Unsubscriptions.py
5. user-analytics-backend/app/schemas/UserActivities.py
6. user-analytics-backend/app/schemas/BillingEvent.py
7. user-analytics-backend/app/schemas/Services.py
8. user-analytics-backend/app/schemas/ServicesTypes.py
9. user-analytics-backend/app/schemas/SmsEvents.py
10. user-analytics-backend/app/schemas/Campaigns.py
11. user-analytics-backend/app/schemas/Cohorts.py
12. user-analytics-backend/app/schemas/churn_analysis.py
13. user-analytics-backend/app/schemas/ml_churn.py
14. user-analytics-backend/app/schemas/segmentation.py
15. user-analytics-backend/app/schemas/platform_user_schemas.py
16. user-analytics-backend/app/schemas/**init**.py

## Annexe I - Inventaire tests

1. user-analytics-backend/tests/**init**.py
2. user-analytics-backend/tests/test_churn_anchor_logic.py

Constat:

- Presence de tests au-dela de **init**.py : OUI.
- Nombre de vrais fichiers test detectes : 1.

## Annexe J - Documentation disponible

1. docs/architecture.md
2. docs/etl_prod_readme.md
3. docs/kpis.md
4. docs/ml_churn_report.md
5. docs/REAL_DATA_INTEGRATION.md
6. docs/TRIAL_INTEGRATION_SUMMARY.md
7. PROJECT_REPORT.md
8. README.md [racine]
9. user-analytics-backend/README.md
10. analytics-platform-front/README.md

Note:

- CLAUDE.md projet racine: [NON TROUVE - A VERIFIER]
- CLAUDE.md trouve uniquement dans skill externe: .agents/skills/supabase-postgres-best-practices/CLAUDE.md

## Annexe K - KPI Matrix detaillee

| KPI              | SQL trouve ?              | Sargable ?                | Endpoint                         | Hook React                     | Page                      |
| ---------------- | ------------------------- | ------------------------- | -------------------------------- | ------------------------------ | ------------------------- |
| DAU              | Oui                       | Partiel                   | /analytics/user-activity         | useUserActivity                | UserActivityPage          |
| WAU              | Oui                       | Partiel                   | /analytics/user-activity         | useUserActivity                | UserActivityPage          |
| MAU              | Oui                       | Partiel                   | /analytics/user-activity         | useUserActivity                | UserActivityPage          |
| Stickiness       | Oui                       | Oui (post calc)           | /analytics/user-activity         | useUserActivity                | UserActivityPage          |
| Churn Rate       | Oui                       | Partiel                   | /analytics/churn/kpis            | useChurnKPIs                   | ChurnAnalysisPage         |
| Retention D7     | Oui                       | Oui (cohorts)             | /analytics/retention/heatmap     | useRetentionHeatmap            | RetentionPage             |
| Retention D30    | Oui                       | Oui (cohorts)             | /analytics/retention/heatmap     | useRetentionHeatmap            | RetentionPage             |
| ARPU             | Oui                       | Partiel                   | /analytics/overview              | useOverview/useSubscribersKPIs | Dashboard/Subscribers     |
| Avg Lifetime     | Oui                       | Partiel                   | /analytics/user-activity         | useUserActivity                | UserActivityPage          |
| Trial Conversion | Oui                       | Partiel                   | /analytics/trial/kpis            | useTrialKPIs                   | FreeTrialBehaviorPage     |
| Drop-off J3      | Oui                       | Partiel                   | /analytics/trial/kpis            | useTrialKPIs                   | FreeTrialBehaviorPage     |
| Campaign ROI     | Partiel                   | Partiel                   | /analytics/campaigns/performance | useCampaignPerformance         | CampaignImpactPage        |
| NRR              | [NON TROUVE - A VERIFIER] | [NON TROUVE - A VERIFIER] | [NON TROUVE - A VERIFIER]        | [NON TROUVE - A VERIFIER]      | [NON TROUVE - A VERIFIER] |

## Annexe L - Verification securite (constats factuels)

1. JWT present -> oui
2. RBAC admin present -> oui
3. role analyst present -> oui
4. password hashing present -> oui (passlib/bcrypt)
5. fallback credentials en dur dans database.py -> oui (dev fallback)
6. SECRET_KEY env usage -> oui via config
7. CORS middleware present -> oui
8. Policies RLS DB -> [NON TROUVE - A VERIFIER]

## Annexe M - Docker et execution

Services docker-compose detectes:

1. analytics_backend
2. analytics_frontend
3. analytics_redis

Ports exposes:

1. backend: 8000
2. frontend: 5173
3. redis: interne compose uniquement

Variables compose notables:

1. REDIS_URL redis://analytics_redis:6379/0
2. ADMIN_EMAIL admin@local.tn
3. ADMIN_PASSWORD admin123
4. VITE_PROXY_TARGET http://analytics_backend:8000

## Annexe N - Extraits de decisions etat projet

1. KPI Subscribers auparavant mock -> maintenant relies backend via /analytics/overview
2. User list last activity/activity type -> mapping backend corrige
3. Caching backend present sur endpoints analytiques critiques
4. React Query configure avec staleTime long
5. Export CSV/XLSX implemente sur plusieurs pages

## Annexe O - Plan d'action 15 jours

Jour 1:

- Profiling SQL trial kpis
- Capturer EXPLAIN ANALYZE

Jour 2:

- Ajouter index composite requis
- Mesurer gain

Jour 3:

- Ajouter cache court trial kpis
- Bench cold/warm

Jour 4:

- Profiling user-activity
- Limiter fenetre max

Jour 5:

- Pre-aggregation journaliere proof-of-concept

Jour 6:

- Ecrire 5 tests pytest routers trial/useractivity

Jour 7:

- Ecrire 5 tests pytest auth/users

Jour 8:

- Standardiser RBAC dependencies

Jour 9:

- Supprimer fallback credentials du code

Jour 10:

- Ajouter KPI NRR backend

Jour 11:

- Ajouter hook/page NRR front

Jour 12:

- Revue docs techniques

Jour 13:

- Demo run e2e docker from scratch

Jour 14:

- Fix regressions

Jour 15:

- Freeze soutenance intermediate

## Annexe P - Hypotheses et limites

1. Ce rapport est base uniquement sur le codebase et artefacts disponibles.
2. Les donnees de production reelles n'ont pas ete reexecutÃ©es ici.
3. Les lignes exactes de certaines causes perf restent indicatives.
4. Les informations non visibles explicitement sont marquees [NON TROUVE - A VERIFIER].
5. Le score global est une estimation technique, pas un KPI academique officiel.

## Annexe Q - Conclusion generale

Le projet est suffisamment avance pour une soutenance intermediaire serieuse.
Le coeur fonctionnel est la.
Les briques metier sont en place.
La dette principale est non-fonctionnelle.
Le risque principal est le couple performance + tests.
La trajectoire de finalisation est realiste.
Un sprint court et discipline peut faire franchir le seuil de maturite attendu.

---

## Trace de conformite au prompt

- Rapport genere en francais: Oui
- Fichier cree a la racine: Oui (`RAPPORT_AVANCEMENT.md`)
- Livrables L1-L25 evalues: Oui
- Analyse ETL/backend/db/kpi/frontend/ia/auth/tests/perf: Oui
- Mentions [NON TROUVE - A VERIFIER] ajoutees quand necessaire: Oui
- Chiffres pre-check commandes inclus: Oui
- Reference aux latences docker fournies incluse: Oui
- Generation en une seule passe: Oui

Fin du rapport.

