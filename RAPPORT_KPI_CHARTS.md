# Rapport Technique — KPIs, Graphiques et APIs (Version concise)

## Plateforme d'Analytics Comportementale — PFE 2025/2026

## Objectif

Ce document résume, de manière courte et exploitable, la définition métier de chaque KPI et de chaque graphique réellement utilisés par l'application, avec la logique SQL effective (router/service/repository) telle qu'implémentée dans le code.

## Méthode d'analyse

- Analyse complète des fichiers backend et frontend demandés.
- Corrélation route API -> service/repository -> hook React -> page.
- Priorité au SQL réel: requêtes inline dans les routers/repositories, ou logique SQL résumée depuis les fonctions repository quand le router délègue.

## Fichiers analysés (périmètre)

### Backend routers

- user-analytics-backend/app/routers/analyticsOverview.py
- user-analytics-backend/app/routers/userActivity.py
- user-analytics-backend/app/routers/churn_analysis.py
- user-analytics-backend/app/routers/retention.py
- user-analytics-backend/app/routers/trialAnalytics.py
- user-analytics-backend/app/routers/campaign_impact.py
- user-analytics-backend/app/routers/cross_service.py
- user-analytics-backend/app/routers/ml_churn.py
- user-analytics-backend/app/routers/service.py
- user-analytics-backend/app/routers/users.py
- user-analytics-backend/app/routers/auth.py
- user-analytics-backend/app/routers/management.py
- user-analytics-backend/app/routers/admin_import.py
- user-analytics-backend/app/routers/platform_user.py
- user-analytics-backend/app/routers/anomalies.py
- user-analytics-backend/app/routers/segmentation.py
- user-analytics-backend/app/routers/nrr.py

### Backend repositories/services/ML/utils/models

- user-analytics-backend/app/repositories/churn_repo.py
- user-analytics-backend/app/repositories/campaign_repo.py
- user-analytics-backend/app/repositories/nrr_repo.py
- user-analytics-backend/app/repositories/segmentation_repo.py
- user-analytics-backend/app/services/churn_service.py
- user-analytics-backend/app/services/campaign_service.py
- user-analytics-backend/app/services/nrr_service.py
- user-analytics-backend/app/services/segmentation_service.py
- user-analytics-backend/app/services/platform_user_service.py
- user-analytics-backend/ml_models/churn_predictor.py
- user-analytics-backend/app/utils/temporal.py
- user-analytics-backend/app/core/date_ranges.py
- user-analytics-backend/app/models/subscriptions.py
- user-analytics-backend/app/models/billing_events.py
- user-analytics-backend/app/models/user_activities.py
- user-analytics-backend/app/models/unsubscriptions.py
- user-analytics-backend/app/models/cohorts.py
- user-analytics-backend/app/models/users.py
- user-analytics-backend/app/models/services.py
- user-analytics-backend/app/models/campaigns.py
- user-analytics-backend/app/models/sms_events.py

### Frontend hooks/pages

- analytics-platform-front/src/hooks/useDashboardMetrics.js
- analytics-platform-front/src/hooks/useUserActivity.js
- analytics-platform-front/src/hooks/useChurnKPIs.js
- analytics-platform-front/src/hooks/useChurnDashboard.js
- analytics-platform-front/src/hooks/useChurnCurve.js
- analytics-platform-front/src/hooks/useChurnBreakdown.js
- analytics-platform-front/src/hooks/useChurnReasons.js
- analytics-platform-front/src/hooks/useTimeToChurn.js
- analytics-platform-front/src/hooks/useRiskSegments.js
- analytics-platform-front/src/hooks/useRetentionKPIs.js
- analytics-platform-front/src/hooks/useRetentionHeatmap.js
- analytics-platform-front/src/hooks/useRetentionCurve.js
- analytics-platform-front/src/hooks/useCohortsTable.js
- analytics-platform-front/src/hooks/useTrialKPIs.js
- analytics-platform-front/src/hooks/useTrialDropoffByDay.js
- analytics-platform-front/src/hooks/useTrialUsers.js
- analytics-platform-front/src/hooks/useCampaignKPIs.js
- analytics-platform-front/src/hooks/useCampaignPerformance.js
- analytics-platform-front/src/hooks/useCampaignTimeline.js
- analytics-platform-front/src/hooks/useCampaignImpactDashboard.js
- analytics-platform-front/src/hooks/useCampaignComparison.js
- analytics-platform-front/src/hooks/useCrossService.js
- analytics-platform-front/src/hooks/useChurnPredictionMetrics.js
- analytics-platform-front/src/hooks/useChurnPredictionScores.js
- analytics-platform-front/src/hooks/useChurnPredictionTrain.js
- analytics-platform-front/src/hooks/useSegmentationKPIs.js
- analytics-platform-front/src/hooks/useSegmentationClusters.js
- analytics-platform-front/src/hooks/useSegmentationProfiles.js
- analytics-platform-front/src/hooks/useUsers.js
- analytics-platform-front/src/hooks/useManagement.js
- analytics-platform-front/src/hooks/useImportData.js
- analytics-platform-front/src/pages/dashboard/DashboardPage.jsx
- analytics-platform-front/src/pages/UserActivityPage.jsx
- analytics-platform-front/src/pages/dashboard/ChurnAnalysisPage.jsx
- analytics-platform-front/src/pages/dashboard/RetentionPage.jsx
- analytics-platform-front/src/pages/dashboard/FreeTrialBehaviorPage.jsx
- analytics-platform-front/src/pages/dashboard/CampaignImpactPage.jsx
- analytics-platform-front/src/pages/dashboard/CrossServiceBehaviorPage.jsx
- analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx
- analytics-platform-front/src/pages/dashboard/UserSegmentationPage.jsx
- analytics-platform-front/src/pages/SubscribersPage.jsx

## Anchor temporel global (important)

La plateforme s'appuie sur la donnée disponible et pas sur une date système arbitraire. La borne est calculée via `get_data_bounds` et `get_data_anchor` dans `temporal.py`, puis les dates API sont clampées dans `date_ranges.py`.

Conséquence: les KPIs restent cohérents avec l'état réel des snapshots ETL.

## Endpoints: vue synthétique par domaine

### Overview

- GET /analytics/summary -> agrège users/subscriptions/churn/revenue/engagement/top services/SMS via blocs SQL dans analyticsOverview.py.
- GET /analytics/overview -> façade sur la même logique de synthèse.

### User Activity

- GET /analytics/user-activity -> KPI activité + tendances + heatmap + growth + inactivité + tableau par service.

### Churn

- GET /analytics/churn/dashboard -> service d'agrégation (churn_service.get_churn_dashboard) basé sur churn_repo.
- GET /analytics/churn/kpis -> global churn, monthly churn, avg lifetime, breakdown.
- GET /analytics/churn/trend -> série journalière churn/new.
- GET /analytics/churn/by-service -> churn par service.
- GET /analytics/churn/lifetime -> moyenne et distribution de durée de vie.
- GET /analytics/churn/retention -> cohortes de rétention.
- GET /analytics/churn/reactivation/kpis -> KPI de réactivation post churn.
- GET /analytics/churn/reactivation/by-service -> réactivation segmentée par service.

### Retention

- GET /analytics/retention/kpis
- GET /analytics/retention/heatmap
- GET /analytics/retention/curve
- GET /analytics/retention/cohorts-list

### Trial

- GET /analytics/trial/kpis
- GET /analytics/trial/timeline
- GET /analytics/trial/by-service
- GET /analytics/trial/users
- GET /analytics/trial/dropoff-by-day
- GET /analytics/trial/dropoff-causes

### Campaign

- GET /analytics/campaigns/dashboard
- GET /analytics/campaigns/list
- GET /analytics/campaigns/overview
- GET /analytics/campaigns/by-type
- GET /analytics/campaigns/top
- GET /analytics/campaigns/trend
- GET /analytics/campaigns/kpis
- GET /analytics/campaigns/performance
- GET /analytics/campaigns/comparison
- GET /analytics/campaigns/timeline

### Cross Service

- GET /analytics/cross-service/overview
- GET /analytics/cross-service/co-subscriptions
- GET /analytics/cross-service/migrations
- GET /analytics/cross-service/distribution
- GET /analytics/cross-service/all

### Segmentation

- GET /analytics/segmentation/kpis
- GET /analytics/segmentation/clusters
- GET /analytics/segmentation/profiles
- POST /analytics/segmentation/train

### ML Churn

- POST /ml/churn/train
- GET /ml/churn/metrics
- GET /ml/churn/governance
- GET /ml/churn/scores
- POST /ml/churn/scores/recompute

### Admin / Support

- Auth: /auth/login, /auth/refresh, /auth/me, /auth/register
- Users: /users
- Services: /services
- Management: CRUD services/campaigns côté admin
- Platform Users: endpoints CRUD + role/status
- Import admin: endpoints d'import CSV/ETL
- Anomalies: summary/timeline/distribution/heatmap/details/insights/run-detection

---

# SECTION 1 — KPIs (définition courte + logique SQL)

## A. Dashboard Overview (useDashboardMetrics / useOverview)

### KPI: Total Users

Définition: nombre total d'utilisateurs connus de la plateforme.
Logique SQL: `COUNT(*)` sur `users` dans `analyticsOverview._summary_users_block`.

### KPI: Active Users

Définition: utilisateurs actifs selon le statut profil.
Logique SQL: `COUNT(*) FILTER (WHERE status='active')` sur `users`.

### KPI: Inactive Users

Définition: utilisateurs inactifs selon le statut profil.
Logique SQL: `COUNT(*) FILTER (WHERE status='inactive')` sur `users`.

### KPI: New Users Last 30 Days

Définition: nouveaux inscrits sur la fenêtre glissante 30 jours.
Logique SQL: `COUNT(*) FILTER (WHERE created_at BETWEEN :last30_start_dt AND :last30_end_dt)`.

### KPI: Total Subscriptions (hors pending)

Définition: volume d'abonnements exploitables pour la conversion.
Logique SQL: `COUNT(*) FILTER (WHERE s.status != 'pending')` sur `subscriptions`.

### KPI: Active Subscriptions

Définition: abonnements en état actif.
Logique SQL: `COUNT(*) FILTER (WHERE s.status='active')` sur `subscriptions`.

### KPI: Billing Failed

Définition: abonnements en risque de churn pour cause de paiement.
Logique SQL: `COUNT(*) FILTER (WHERE s.status='billing_failed')`.

### KPI: Cancelled

Définition: abonnements explicitement annulés.
Logique SQL: `COUNT(*) FILTER (WHERE s.status='cancelled')`.

### KPI: Pending OTP

Définition: abonnements bloqués en attente OTP/validation.
Logique SQL: `COUNT(*) FILTER (WHERE s.status='pending')`.

### KPI: Conversion Rate Subscriptions

Définition: part d'abonnements actifs parmi les abonnements non pending.
Logique SQL: `active / NULLIF(total_non_pending,0)` avec `ROUND(...,1)`.

### KPI: DAU Today

Définition: utilisateurs uniques actifs sur 24h.
Logique SQL: `COUNT(DISTINCT user_id)` filtré sur fenêtre day dans `user_activities` (bloc engagement overview).

### KPI: WAU Current Week

Définition: utilisateurs uniques actifs sur 7 jours.
Logique SQL: `COUNT(DISTINCT user_id)` sur `usage_week_start_dt -> usage_week_end_dt`.

### KPI: MAU Current Month

Définition: utilisateurs uniques actifs sur la fenêtre mensuelle courante.
Logique SQL: `COUNT(DISTINCT user_id)` sur `usage_month_start_dt -> usage_month_end_dt`.

### KPI: Churn Rate Month (overview)

Définition: pourcentage de churn sur la période d'analyse du dashboard.
Logique SQL: CTE `active_start` + CTE `churn_rows`, puis `COUNT(churn_rows)/active_start` dans `analyticsOverview._summary_churn_block`.

### KPI: Voluntary / Technical Churn % (overview)

Définition: répartition des churns par type métier.
Logique SQL: `COUNT(*) FILTER (WHERE churn_type='VOLUNTARY'|'TECHNICAL') / COUNT(*)`.

### KPI: Dropoff Day1/2/3

Définition: churn précoce 1er, 2e et 3e jour après souscription.
Logique SQL: `COUNT(*) FILTER (WHERE days_since_subscription = 1|2|3)` dans `churn_rows`.

### KPI: Total Revenue

Définition: revenu total de facturation réussie.
Logique SQL: `SUM(service_types.price) FILTER (WHERE be.status='success')` en joignant `billing_events`, `subscriptions`, `services`, `service_types`.

### KPI: Success / Failed / Non-success Events

Définition: qualité de la chaîne de facturation.
Logique SQL: `COUNT(*) FILTER` par status `success`, `failed`, `failed|cancelled|pending`.

### KPI: Failed %

Définition: proportion d'échecs de paiement.
Logique SQL: `failed / NULLIF(total_events,0)`.

### KPI: MRR

Définition: revenu récurrent sur la fenêtre mensuelle courante.
Logique SQL: `SUM(price)` filtré `status='success'` + fenêtre `billing_month_start_dt -> billing_month_end_dt`.

### KPI: ARPU Current Month

Définition: revenu moyen par utilisateur payeur du mois.
Logique SQL: `SUM(revenue_success_month) / COUNT(DISTINCT user_id success_month)`.

### KPI: Top Services (count + churn rate)

Définition: classement services par volume avec santé churn.
Logique SQL: `GROUP BY srv.name` + agrégats de statuts et `cancelled/non_pending`.

### KPI: SMS OTP / Activation / Templates per Service

Définition: mesure du mix et de l'intensité templates SMS sur fenêtre courante vs précédente.
Logique SQL: CTE `anchor`, `cur`, `prev`, puis taux calculés dans `cur_rates`/`prev_rates`.

## B. User Activity (useUserActivity)

### KPI: DAU

Définition: utilisateurs uniques actifs le dernier jour de la fenêtre.
Logique SQL: `COUNT(DISTINCT user_id)` sur `activity_datetime in [end_dt, end_dt+1d)`.

### KPI: WAU

Définition: utilisateurs uniques actifs 7 jours glissants.
Logique SQL: `COUNT(DISTINCT user_id)` sur `[end_dt-7d, end_dt+1d)`.

### KPI: MAU

Définition: utilisateurs uniques actifs sur la fenêtre choisie.
Logique SQL: `COUNT(DISTINCT user_id)` sur `[start_dt, end_dt+1d)`.

### KPI: Stickiness

Définition: intensité d'usage quotidien rapportée au mensuel.
Logique SQL: calcul applicatif `round((DAU / MAU) * 100, 1)` à partir des KPI SQL.

### KPI: Inactive Count

Définition: utilisateurs sans activité sur 7 jours, hors churned/cancelled.
Logique SQL: `LEFT JOIN user_activities` récent puis `WHERE ua.user_id IS NULL`.

### KPI: Avg Lifetime Days

Définition: durée moyenne de vie abonnement.
Logique SQL: `AVG(EXTRACT(DAY FROM COALESCE(end, anchor)-start))` sur `subscriptions`.

## C. Churn (useChurnKPIs / useChurnDashboard)

### KPI: Global Churn Rate

Définition: part des abonnements churnés (cancelled/expired) sur le stock total.
Logique SQL: `COUNT(churned_ever) / COUNT(total_ever)` dans `churn_repo.get_global_churn_rate`.

### KPI: Monthly Churn Rate

Définition: churn de période sur base at-risk de période.
Logique SQL: CTE `unsubs` (`COUNT DISTINCT subscription_id`) / (`active_at_start + started_in_period`) dans `_compute_monthly_churn_metrics`.

### KPI: Period Churned

Définition: volume churn pendant la période filtrée.
Logique SQL: `COUNT(DISTINCT u.subscription_id)` sur `unsubscriptions` borné par période.

### KPI: Period Base (At-Risk)

Définition: base exposée au churn sur période.
Logique SQL: `active_at_start + started_in_period` (deux CTE sur `subscriptions`).

### KPI: Average Lifetime Days

Définition: ancienneté moyenne des abonnements churnés.
Logique SQL: `AVG(EXTRACT(epoch(end-start))/86400)` sur souscriptions ended.

### KPI: Voluntary vs Technical Churn

Définition: mix de churn volontaire vs technique.
Logique SQL: `COUNT(*) FILTER (WHERE churn_type='VOLUNTARY'|'TECHNICAL')` sur `unsubscriptions`.

### KPI: Trial vs Paid Churn

Définition: part de churn pendant essai versus après facturation.
Logique SQL: combine `user_activities churn_event` + `subscriptions` dédupliquées dans `get_trial_vs_paid_churn`.

### KPI: First Bill Churn

Définition: churn dans les 7 jours suivant première charge.
Logique SQL: sous-requête first charges (`billing_events is_first_charge success`) join `user_activities churn_event` avec fenêtre +7 jours.

### KPI: Reactivated Users

Définition: churnés qui se réabonnent ensuite au même service.
Logique SQL: CTE `churn_events` + CTE `reactivations` (`MIN(subscription_start_date) >= churn_date` et `s.id <> c.subscription_id`).

### KPI: Reactivation Rate

Définition: part des churnés qui reviennent.
Logique SQL: `COUNT(DISTINCT reactivated_users) / COUNT(DISTINCT churned_users)` avec `ROUND(...,2)`.

### KPI: Avg Days to Re-subscribe

Définition: délai moyen avant retour après churn.
Logique SQL: `AVG(EXTRACT(EPOCH FROM (resub_date - churn_date))/86400)`.

### KPI: Recovered Revenue

Définition: revenu généré après réactivation.
Logique SQL: `SUM(service_types.price)` des `billing_events success` après `resub_date`.

## D. Retention (useRetentionKPIs)

### KPI: Avg Retention D7

Définition: rétention moyenne à J+7 sur cohortes filtrées.
Logique SQL: `AVG(cohorts.retention_d7)`.

### KPI: Avg Retention D30

Définition: rétention moyenne à J+30.
Logique SQL: `AVG(cohorts.retention_d30)`.

### KPI: Best Cohort + Best D7

Définition: meilleure cohorte sur D7.
Logique SQL: `MAX(retention_d7)` et identification cohorte associée.

### KPI: At-Risk Cohorts

Définition: cohortes fragiles à faible rétention.
Logique SQL: comptage cohorte sous seuil métier (calculé côté router à partir des résultats cohorte).

### KPI: Total Cohorts

Définition: volume de cohortes dans le filtre.
Logique SQL: `COUNT(*)` sur `cohorts` filtrés.

## E. Trial Analytics (useTrialKPIs)

### KPI: Total Trials Started

Définition: essais démarrés sur la période.
Logique SQL: `COUNT(*)` sur `subscriptions` filtrées par start_date.

### KPI: Trial to Paid Conversion Rate

Définition: part des essais convertis en actif.
Logique SQL: agrégats par status (`active` vs total trial/pending/active/cancelled/expired) dans trialAnalytics.

### KPI: Average Trial Duration

Définition: durée moyenne observée des essais.
Logique SQL: différence date fin - date début sur souscriptions d'essai, agrégée.

### KPI: Day-3 Drop-off Rate

Définition: churn survenu dans les 3 premiers jours d'essai.
Logique SQL: `COUNT(churn <= 3 jours) / COUNT(total)` dans query dropoff.

### KPI: Trial-only Users

Définition: utilisateurs restés dans un usage essai sans passage payé.
Logique SQL: calcul via statuts et historique de souscription dans trial router.

### KPI: Trial Exception Pressure (business_exception_rules.status)

Définition: niveau de pression des exceptions au modèle standard (promotion + extension de trial).
Logique SQL: `promotion_trials` (join campaigns `campaign_type='promotion'`) + `trial_extensions` (durée observée > durée configurée service) dans `/analytics/trial/kpis`, puis classification dans `build_trial_exception_summary` (`controlled`, `moderate_exception_pressure`, `high_exception_pressure`).

### KPI: Promotion Trials %

Définition: part des essais initiés dans un contexte promotionnel.
Logique SQL: `COUNT(*) FILTER (WHERE c.campaign_type='promotion') / total_trials * 100`.

### KPI: Trial Extensions %

Définition: part des essais dont la durée observée dépasse la durée configurée (règles métiers exceptionnelles).
Logique SQL: `COUNT(*) FILTER (WHERE EXTRACT(DAY FROM end-start) > trial_duration_days) / total_trials * 100`.

### KPI: Total Exception Events %

Définition: intensité globale des écarts au modèle business standard trial -> renouvellement.
Logique SQL: `(promotion_trials + trial_extensions) / total_trials * 100`, puis seuils de statut dans `business_rules.py`.

### KPI: Early Drop-offs (D0-D3)

Définition: proportion des abandons trial qui surviennent dans les 3 premiers jours.
Logique SQL: `COUNT(*) FILTER (WHERE dropoff_days <= 3) / total_dropoffs * 100` sur `/analytics/trial/dropoff-causes`.

### KPI: Technical Share % / Voluntary Share %

Définition: ventilation causale des abandons trial entre friction technique/billing et opt-out volontaire.
Logique SQL: `COUNT(*) FILTER (WHERE churn_type='TECHNICAL'|'VOLUNTARY') / total_dropoffs * 100`.

## F. Campaign Impact (useCampaignKPIs / dashboard)

### KPI: Total Campaigns

Définition: nombre total de campagnes selon filtres.
Logique SQL: `COUNT(*)` sur CTE `filtered_campaigns`.

### KPI: Completed Campaigns

Définition: campagnes terminées.
Logique SQL: `SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END)`.

### KPI: Total Targeted

Définition: audience visée cumulée.
Logique SQL: `SUM(COALESCE(target_size,0))`.

### KPI: Subscriptions from Campaigns

Définition: souscriptions attribuées aux campagnes.
Logique SQL: CTE `campaign_subs` (match direct `campaign_id` + fallback fenêtre date/service), puis agrégation.

### KPI: Average Conversion Rate

Définition: efficacité moyenne des campagnes.
Logique SQL: `subscriptions / target_size` avec protection `NULLIF`.

### KPI: Campaign ROI

Définition: rendement des campagnes sur conversion/revenu.
Logique SQL: calcul à partir des revenus facturés post-campagne et du ciblage (campagne repo/service).

### KPI: Top Campaign

Définition: campagne ayant le plus d'acquisitions.
Logique SQL: `ORDER BY subscriptions DESC LIMIT`.

### KPI: Campaign Data Quality Score

Définition: score normalisé de fiabilité analytique des campagnes, utilisé pour qualifier l'interprétation KPI.
Logique SQL: score calculé dans `campaign_service.py` a partir des agrégats repository (`target_coverage_pct`, `sms_coverage_pct`, `delivery_success_pct`) avec formule `0.45*target_coverage + 0.25*min(sms_coverage,100) + 0.30*delivery_success`.

### KPI: Campaign Data Quality Status

Définition: niveau de confiance (`excellent`, `good`, `fair`, `poor`) dérivé du score qualité.
Logique SQL: règles de seuils sur `quality_score` dans `get_campaign_dashboard`.

## G. Cross Service (useCrossService)

### KPI: Multi-Service Users

Définition: utilisateurs abonnés à au moins deux services.
Logique SQL: CTE `filtered_subs` puis `COUNT(DISTINCT service_id) >= 2` par user.

### KPI: Multi-Service Rate

Définition: part des multi-services dans la base active analysée.
Logique SQL: `multi_users / total_users`.

### KPI: Top Service Combo

Définition: paire de services la plus fréquente.
Logique SQL: auto-join de services par user (`service_id < other_service_id`), groupement et tri descendant.

### KPI: Cross vs Mono Retention D30

Définition: comparaison de rétention 30 jours entre mono-service et multi-service.
Logique SQL: segmentation `segment in (mono,multi)` puis `retained_d30 / total`.

### KPI: ARPU Multi vs Mono

Définition: comparaison du revenu moyen par segment d'usage.
Logique SQL: agrégation revenu par segment (mono/multi) sur facturation succès.

### KPI: Migration Top-3 Concentration %

Définition: part des 3 principaux chemins de migration A->B sur l'ensemble des migrations observées.
Logique SQL: calcul post-agrégation des flux migration (`top3_users / total_migration_users * 100`) dans `/analytics/cross-service/migrations`.

## H. ML Churn (useChurnPredictionMetrics / useChurnPredictionScores)

### KPI: ROC-AUC

Définition: capacité du modèle à classer churn/non churn.
Logique SQL: dataset construit par SQL feature engineering, score calculé dans sklearn `roc_auc_score`.

### KPI: Accuracy

Définition: taux global de bonnes prédictions.
Logique SQL: dépend des features SQL puis `classification_report['accuracy']`.

### KPI: Training Churn Rate

Définition: proportion churn dans l'échantillon d'entraînement.
Logique SQL: label `churned` produit dans `_base_features_sql` puis moyenne de la cible.

### KPI: Risk Distribution (Low/Medium/High)

Définition: répartition des scores de risque sur la base active scorée.
Logique SQL: features extraites en SQL, puis seuils probas côté Python (`<0.3`, `<0.6`, sinon High).

### KPI: Governance Status

Définition: état global de robustesse du modèle (`stable`, `watch`, `retrain_required`).
Logique SQL: base features SQL réévaluées en scoring courant, comparaison au profil d'entraînement (`governance_report`) et règles d'alerte (cadence + drift).

### KPI: Days Since Training

Définition: âge du modèle depuis le dernier entraînement, utilisé pour déclencher recalibration/retrain.
Logique SQL: calcul temporel sur `trained_at` (métriques entraînement) vs horodatage courant.

### KPI: High Drift Features

Définition: nombre de features avec dérive forte entre profil train et profil courant.
Logique SQL: drift par feature via z-shift (`_compute_feature_drift`) après reconstruction des features actives via SQL.

### KPI: Brier Score

Définition: qualité de calibration probabiliste du modèle de churn (plus faible = mieux).
Logique SQL: issu de la phase d'entraînement (`_calibration_summary`) sur le jeu d'évaluation alimenté par features SQL.

### KPI: Expected Calibration Error (ECE)

Définition: écart moyen entre probabilité prédite et fréquence observée par bins de confiance.
Logique SQL: calculé dans `_calibration_summary` (bins calibrés) et exposé par `/ml/churn/governance`.

## I. Segmentation (useSegmentationKPIs)

### KPI: Total Segments

Définition: nombre de clusters actifs dans la segmentation.
Logique SQL: déterminé via segmentation_service/repository après calcul cluster.

### KPI: Dominant Segment + Dominant %

Définition: cluster majoritaire et son poids.
Logique SQL: agrégation des affectations de cluster par volume utilisateur.

### KPI: High Value Segment

Définition: segment avec ARPU moyen le plus élevé.
Logique SQL: comparaison `AVG(revenue)` par cluster.

### KPI: ARPU Premium

Définition: surperformance ARPU du segment premium vs moyenne globale.
Logique SQL: ratio d'ARPU cluster premium sur ARPU global.

### KPI: Risk Segment + Risk Churn Rate

Définition: segment ayant la probabilité de churn la plus forte.
Logique SQL: taux churn agrégé par cluster sur base historique.

---

# SECTION 2 — Charts (définition courte + logique SQL)

## A. Dashboard Overview

### Chart: Subscription Breakdown Pie

Définition: visualise la structure des statuts d'abonnement.
Logique SQL: agrégats `COUNT FILTER` par statut (`active`, `billing_failed`, `cancelled`, `pending`) dans overview summary.

### Chart: Churn Breakdown Pie

Définition: compare churn volontaire et technique.
Logique SQL: agrégats churn types sur `unsubscriptions` dans bloc churn overview / churn_repo breakdown.

### Chart: Dropoff Day 1/2/3 Bar

Définition: montre l'intensité du churn précoce.
Logique SQL: comptage `days_since_subscription = 1|2|3` dans CTE `churn_rows`.

### Chart: Top Services Bar

Définition: classement des services par volume et santé churn.
Logique SQL: `GROUP BY service_name` avec statuts et churn_rate_pct calculé.

### Panel: Insight Guide (Narrative Drill-down)

Définition: mode narratif pour transformer les KPI/charts en lecture décisionnelle orientée actions.
Logique SQL: réutilise les mêmes endpoints analytiques (overview/churn/trial/campaign); orchestration et priorisation des insights réalisées côté frontend.

## B. User Activity Page

### Chart: DAU Trend (LineChart)

Définition: évolution journalière des utilisateurs actifs.
Logique SQL: `SELECT DATE(activity_datetime), COUNT(DISTINCT user_id)` groupé par jour.
Axes: X=date, Y=dau.

### Chart: WAU/MAU Overlay (LineChart)

Définition: compare la dynamique hebdo et mensuelle en rolling.
Logique SQL: base journalière SQL puis rolling 7/30 jours côté code sur séries date.
Axes: X=date, Y=users.

### Chart: Activity Heatmap

Définition: distribution horaire et hebdomadaire de l'activité.
Logique SQL: `TO_CHAR(day) + EXTRACT(hour)` et `COUNT(*)` groupé jour/heure.
Axes: X=hour, Y=day, Valeur=count.

### Chart: User Growth

Définition: compare nouveaux utilisateurs et churnés par mois.
Logique SQL: CTE `months` + `new_users` + `churned_users`, puis left joins mensuels.
Axes: X=month, Y=count, séries=nouveaux/churnés.

### Chart: Inactivity Buckets

Définition: répartition des utilisateurs selon jours depuis dernière activité.
Logique SQL: `CASE WHEN EXTRACT(DAY FROM end_dt-last_activity_at)` dans buckets (1-7, 8-14, 15-30, 30+).
Axes: X=bucket, Y=count.

### Chart/Table: Service Activity Table

Définition: vue consolidée activité et stickiness par service.
Logique SQL: join `subscriptions + services + users + user_activities`, group by service.

## C. Churn Analysis Page

### Chart: Daily Churn vs New (LineChart)

Définition: met en regard churn et acquisitions journalières.
Logique SQL: deux séries SQL (`unsubscriptions` et `subscriptions.start`) fusionnées par date dans `get_churn_trend_daily`.
Axes: X=date, Y=count, séries=new_subs/churned.

### Chart: Churn Type Pie

Définition: part relative volontaire vs technique.
Logique SQL: `COUNT FILTER` par churn_type dans `get_churn_breakdown`.
Axes: portions=counts.

### Chart: Reactivation by Service (Horizontal Bar)

Définition: mesure les retours post-churn par service.
Logique SQL: CTE churn_events -> reactivations -> reactivated_by_service avec `GROUP BY service_id`.
Axes: X=reactivated_users, Y=service_name.

### Chart: Churn by Service (Horizontal Bar)

Définition: compare l'intensité du churn entre services.
Logique SQL: `COUNT(sub.id)` sur subscriptions churned, join services, group by service.
Axes: X=churned, Y=service_name.

### Chart: Lifetime Distribution

Définition: histogramme des durées de vie avant churn.
Logique SQL: buckets SQL 0-7, 8-30, 31-90, 91-180, 181+ via `COUNT FILTER`.
Axes: X=bucket, Y=count.

### Chart: Retention Cohort Table

Définition: compare D7/D14/D30 par cohorte.
Logique SQL: agrégats sur `cohorts` groupés par `cohort_date`.
Axes: lignes=cohorte, colonnes=retention rates.

## D. Retention Page

### Chart: Cohort Heatmap

Définition: lecture rapide des performances de rétention par cohorte et service.
Logique SQL: dataset `cohorts` filtré (service + période) dans endpoint heatmap.
Axes: X=service, Y=cohort_month, valeur=retention.

### Chart: Retention Curve

Définition: trajectoire de survie utilisateur par horizon temporel.
Logique SQL: agrégation des champs D1/D7/D14/D30/D60 dans endpoint curve.
Axes: X=day_bucket, Y=retention_pct, séries=service/cohorte.

### Chart: Cohorts Table

Définition: détail tabulaire pour audit précis.
Logique SQL: pagination + tri sur `cohorts-list` endpoint.

## E. Trial Behavior Page

### Chart: Trial Timeline

Définition: suit démarrages essais et conversions dans le temps.
Logique SQL: agrégations journalières sur souscriptions d'essai puis transitions vers actif.
Axes: X=date, Y=count/percent.

### Chart: Trial Dropoff by Day

Définition: identifie le jour de perte dominant pendant l'essai.
Logique SQL: distribution `days_since_subscription` sur churn des essais.
Axes: X=day, Y=dropoff_rate.

### Chart: Trial Users Table

Définition: liste des utilisateurs en essai avec statut de progression.
Logique SQL: endpoint trial users (pagination + filtres service/date).

### Panel: Drop-off Causal Narrative (Management Notes)

Définition: synthèse managériale textuelle des causes dominantes et de leur criticité opérationnelle.
Logique SQL: endpoint `/analytics/trial/dropoff-causes` (summary + causes + reasons), puis rendu frontend en notes actionnables (`management_notes`).

## F. Campaign Impact Page

### Chart: Campaign Performance

Définition: compare l'efficacité des campagnes individuellement.
Logique SQL: `campaign_repo.get_campaign_performance` (target, subscriptions, conversion, first charges).
Axes: X=campaign, Y=conversion/subscriptions.

### Chart: Campaign by Type

Définition: mesure l'impact par canal/type de campagne.
Logique SQL: `GROUP BY campaign_type` sur filtered_campaigns + attribution subscriptions.
Axes: X=campaign_type, Y=subscriptions/conversion.

### Chart: Campaign Trend

Définition: évolution mensuelle de l'effet campagnes.
Logique SQL: agrégat mensuel via `date_trunc('month', ...)`.
Axes: X=month, Y=campaign metrics.

### Chart: Top Campaigns

Définition: met en avant les campagnes les plus contributrices.
Logique SQL: tri décroissant sur acquisition/conversion et limite top N.

### Chart: Campaign Comparison

Définition: compare plusieurs campagnes sur les mêmes métriques.
Logique SQL: endpoint comparison (normalisation et agrégation par campagne).

### Chart: Campaign Timeline

Définition: visualise la temporalité envoi -> activation -> conversion.
Logique SQL: endpoint timeline, séries temporelles par événement campagne.

### Panel: Campaign Data Quality

Définition: vue de confiance analytique (score qualité, statut, couvertures et alertes) avant interprétation KPI.
Logique SQL: `campaign_service.get_campaign_dashboard` calcule `data_quality` à partir des agrégats repository (target, SMS, delivery).

## G. Cross-Service Page

### Chart: Co-subscription Matrix

Définition: détecte les associations fortes entre services.
Logique SQL: auto-join des souscriptions par user et pairing services.
Axes: X=service A, Y=service B, valeur=count.

### Chart: Migrations

Définition: montre les flux de passage d'un service vers un autre.
Logique SQL: endpoint migrations basé sur séquences de souscription utilisateur.
Axes: source -> target, valeur=flux.

### Table: Standardized A->B Journeys

Définition: normalisation des chemins de migration avec priorité, signal business et action recommandée.
Logique SQL: enrichissement backend dans `/analytics/cross-service/migrations` via `standardized_paths`, `summary` et `management_notes` après agrégation SQL des flux.

### Chart: Distribution (#services par user)

Définition: structure de profondeur d'adoption service.
Logique SQL: count distinct service_id par user puis histogramme.
Axes: X=nb_services, Y=users.

## H. AI Churn Insights

### Chart: Risk Distribution Pie/Bar

Définition: répartition du portefeuille par niveau de risque churn.
Logique SQL: features SQL + scoring ML, puis agrégation par catégorie Low/Medium/High.
Axes: catégories de risque, Y=count.

### Chart/Table: Top Risk Users

Définition: priorise les actions de rétention ciblées.
Logique SQL: tri décroissant sur probabilité `churn_risk` issue de LogisticRegression.

### Chart: Governance Drift Table

Définition: contrôle la dérive feature par feature (train mean vs current mean vs z-shift + sévérité).
Logique SQL: profil train stocké dans métriques + profil courant issu de `predict_active_subscriptions`; comparaison dans `governance_report` puis affichage tabulaire frontend.

### Chart/Card: Governance Protocol & Calibration Panel

Définition: synthèse exécutable du protocole d'évaluation, cadence de recalibration, Brier, ECE et alertes de retrain.
Logique SQL: exposition API `/ml/churn/governance`, alimentée par métriques d'entraînement + scoring courant + règles de décision gouvernance.

## I. Segmentation Page

### Chart: Cluster Scatter

Définition: visualise les segments sur un espace comportemental.
Logique SQL: extraction features (activité, revenu, churn proxy) puis projection par cluster.
Axes: X=feature 1, Y=feature 2, couleur=segment.

### Chart: Segment Profiles

Définition: compare ARPU, activité et churn entre segments.
Logique SQL: agrégation des métriques par cluster.
Axes: X=segment, Y=metric.

### Chart: Segment KPI Cards

Définition: synthèse exécutive du segment dominant/premium/risque.
Logique SQL: calcul des leaders par `COUNT`, `AVG(revenue)`, `AVG(churn)`.

---

# SECTION 3 — SQL ML: logique feature engineering (résumé exact)

Le pipeline `ChurnPredictor` construit un dataset subscription-level via CTE `base`, puis enrichit par LATERAL JOIN:

- last activity (`MAX(user_activities.activity_datetime)`),
- nb_activities_7d et 30d,
- billing_failures_30d,
- date première charge succès,
- flags d'essai/churn et variables sentinelles (999) si absence d'événement.

Ensuite:

- entraînement `LogisticRegression(class_weight='balanced', max_iter=2000)`,
- métriques `roc_auc`, `accuracy`, `classification_report`,
- scoring des abonnements actifs avec seuil configurable (`threshold`, défaut 0.4).

---

# SECTION 4 — Qualité SQL (synthèse utile)

## Points robustes

- Fenêtres temporelles majoritairement sargables (`col >= :start` et `col <= :end`).
- Usage massif de CTE pour lisibilité et séparation des bases/dérivés.
- Usage `NULLIF(...,0)` pour éviter divisions par zéro.

## Points à surveiller

- `LOWER(status)` dans certaines requêtes peut neutraliser un index BTREE simple sur status.
- `DATE(activity_datetime)` dans les agrégations peut coûter plus qu'un `date_trunc` avec index fonctionnel.
- Certaines métriques reposent sur règles métier (fallback) qui doivent rester documentées avec tests.

---

# SECTION 5 — Mapping rapide Front -> API

## Hooks principaux

- useDashboardMetrics/useOverview -> /analytics/summary
- useUserActivity -> /analytics/user-activity
- useChurnDashboard/useChurnKPIs -> /analytics/churn/\*
- useReactivationKPIs/useReactivationByService -> /analytics/churn/reactivation/\*
- useRetentionKPIs/useRetentionHeatmap/useRetentionCurve/useCohortsTable -> /analytics/retention/\*
- useTrialKPIs/useTrialDropoffByDay/useTrialUsers/useTrialDropoffCauses -> /analytics/trial/\*
- useCampaignImpactDashboard/useCampaignKPIs/useCampaignPerformance/useCampaignComparison/useCampaignTimeline -> /analytics/campaigns/\*
- useCrossService -> /analytics/cross-service/\*
- useChurnPredictionMetrics/useChurnPredictionScores/useChurnPredictionTrain/useChurnModelGovernance -> /ml/churn/\*
- useSegmentationKPIs/useSegmentationClusters/useSegmentationProfiles -> /analytics/segmentation/\*
- useUsers -> /users
- useManagement -> /admin/management/\*
- useImportData -> /admin/import/\*

## Pages principales

- DashboardPage: overview + engagement + revenue (NRR) + trial/churn synthèse
- UserActivityPage: activité détaillée
- ChurnAnalysisPage: churn + réactivation
- RetentionPage: cohortes/rétention
- FreeTrialBehaviorPage: tunnel essai
- CampaignImpactPage: efficacité campagne
- CrossServiceBehaviorPage: comportements multi-services
- AIChurnInsights: scoring churn ML
- UserSegmentationPage: profils segmentés
- SubscribersPage: vue abonnés/utilisateurs

---

# SECTION 6 — Conformité au Cahier des Charges (synthèse)

## Couverture fonctionnelle

- Activité & engagement (DAU/WAU/MAU, inactifs, lifetime): couvert via overview + user activity.
- Free trial (entrées, conversion, drop-off D1/D2/D3): couvert via trial KPIs + dropoff-by-day + users table.
- Causalité drop-off et raisons métier: couvert via `/analytics/trial/dropoff-causes` + `management_notes`.
- Subscription flow (churn, retention D7/D30, réactivation): couvert via churn + retention endpoints.
- Campaign impact (comparaison, conversion, timeline, top): couvert via dashboard campagnes et endpoints dédiés.
- Cross-service behavior (co-subscription, migrations A->B, distribution): couvert avec standardisation des chemins et priorités actionnables.
- AI/Advanced analytics: couvert via churn prediction, segmentation, anomalies, et gouvernance IA.
- Filtrage date/service/campaign: couvert sur les pages analytiques principales.
- Export management-ready: export CSV/Excel opérationnel sur trial users et reporting documentaire structuré.

## Conformité modèle business (trial -> renew)

- Les KPIs trial incluent explicitement les exceptions métier (`business_exception_rules`) pour éviter un biais d'interprétation.
- Les statuts trial/pending/active/cancelled/expired sont traités explicitement dans le calcul de conversion.
- Les extensions de trial sont détectées vis-a-vis de la durée configurée service, et non supposées uniformes.

## Limites explicitement documentées

- La qualité des causes dépend de la complétude `churn_type/churn_reason` dans `unsubscriptions`.
- Certaines visualisations utilisent des agrégations de service/repository; la logique SQL est résumée quand non inline.
- Les métriques IA sont robustes mais restent dépendantes de la fraîcheur ETL et des contrats de données amont.

---

# Conclusion

Le document a été volontairement raccourci pour la soutenance: chaque KPI et chaque chart est défini en 1-2 phrases avec sa logique SQL réelle et son ancrage backend. La chaîne complète est traçable de la page frontend jusqu'au SQL exécuté (direct ou via repository/service).
