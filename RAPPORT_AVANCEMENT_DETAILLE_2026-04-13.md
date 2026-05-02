    # Rapport d'avancement detaille

    Projet: User Behavior Analytics & Insights Platform
    Date: 13/04/2026
    Perimetre d'analyse: cahier de charge + objectifs campaign + audit du codebase frontend/backend/etl/ml.

    ## 1. Resume executif

    Le projet est fonctionnel sur le coeur analytique et couvre la majorite des besoins metier:

    - pipeline ETL -> base analytics -> API FastAPI -> dashboard React
    - modules principaux disponibles: Activity, Trial, Retention, Churn, Campaign, Cross-service, Segmentation, Anomalies
    - filtres date/service largement disponibles et cache applicatif en place
    - couche AI deja exploitable (churn prediction + segmentation + anomaly detection)

    Estimation d'avancement global (au 13/04/2026): 84%
    Reste a consolider: 16%

    Le reste se concentre surtout sur:

    - generation de rapport management on-demand (PDF) integree au produit
    - standardisation evidence -> recommandations business
    - durcissement QA/observabilite/performance en charge

    ## 2. Methode d'evaluation

    L'evaluation est basee sur:

    1. Conformite fonctionnelle au cahier de charge.
    2. Evidence de livraison dans le code (routers, services, hooks, pages, scripts ETL/ML).
    3. Niveau de production readiness (cache, securite, tests, operation).
    4. Capacite decisionnelle (insight + recommandations + reporting).

    ## 3. Cartographie fonctionnelle livree (codebase)

    ### 3.1 Backend API

    - Architecture FastAPI modulaire avec routers dedies:
    - overview/activity/trial/retention/campaign/churn/cross-service/segmentation/anomalies/ml
    - Inclusion des routers et boot applicatif centralises dans app/main.py
    - Caching backend present sur plusieurs endpoints via decorators et payload keys versionnees
    - RBAC present sur endpoints admin (require_admin) et auth JWT

    ### 3.2 Frontend Dashboard

    - Routing dashboard complet (App.jsx) avec pages par domaine analytique
    - Pages metier disponibles:
    - Dashboard global
    - User Activity
    - Free Trial Behavior
    - Retention
    - Campaign Impact
    - Churn + AI churn
    - Cross-Service
    - Segmentation
    - Anomaly Detection
    - Export utilisateurs/trial/campaign disponible cote UI (CSV/XLSX selon pages)

    ### 3.3 Donnees & ETL

    - ETL PROD -> analytics documente et operationnel
    - Mapping prod_db -> analytics explicite (users/subscriptions/billing/services/service_types)
    - Scripts de recalcul cohortes et linkage campaign/subscriptions
    - Script de backfill ROI campaign ajoute pour combler les manques source sur campaign_targets/sms_events

    ### 3.4 AI / ML

    - Churn predictor base Logistic Regression, features SQL riches, scoring, snapshot cache SQL
    - Segmentation KMeans avec entrainement, profils, clusters, KPIs
    - Detection d'anomalies par z-score glissant sur plusieurs metriques (DAU, churn_rate, revenue, renewals)

    ## 4. Evaluation detaillee vs cahier de charge

    ### 4.1 User Activity & Engagement

    Statut: 100% (module complete)

    - Couvre actifs/inactifs, DAU/WAU/MAU, stickiness, lifetime, tendances
    - Filtres date/service et vues analytiques disponibles
    - Correctif applique: Engagement Score officiel ajoute (formule explicite + seuils high/medium/low) et expose dans API + UI
    - KPI de doublon retires du tab Engagement (deja presents dans User Activity) et remplaces par KPI engagement metier
    - Graphiques du tab Engagement relies a des donnees reelles (trend DAU + moyenne glissante 7j, engagement par service)

    ### 4.2 Free Trial Behavior

    Statut: 90%

    - KPIs trial->paid, drop-off, trial-only users, timeline, users list
    - Export de donnees present
    - Point restant: enrichir l'explication causale du drop-off (raison business/systematique) dans un rapport management standard

    ### 4.3 Subscription & Revenue Flow

    Statut: 86%

    - Churn, retention cohortes (D7/D14/D30), reactivation et revenus couverts
    - NRR et blocs revenue deja exposes
    - Point restant: harmoniser une couche de narration executive multi-service

    ### 4.4 Campaign Impact

    Statut: 100% (finalise)

    - Dashboard campaign dynamique, comparaison, tendances, top campaigns
    - KPI ROI campaign enrichis (messages sent/delivered + subs per 1000 SMS)
    - Standardisation qualite des donnees campaign implementee via score qualite unifie (coverage ciblage/SMS/livraison) par periode/service
    - Controle qualite visible dans le dashboard Campaign Impact avec statut (excellent/good/fair/poor) et indicateurs de couverture

    ### 4.5 Cross-Service Behavior

    Statut: 100% (finalise)

    - Co-subscriptions, overview multi-service, signaux de migration/parcours
    - Parcours A->B standardises integres au reporting management (priorite, signal business, action recommandee)
    - Notes management ajoutees (concentration top chemins, priorisation playbooks retention/cross-sell, suivi impact mensuel)

    ### 4.6 Dashboard Requirements

    Statut: 100% (finalise)

    - Filtres date/service/campaign largement presents
    - Visualisations variees (line/bar/charts/cohort/table)
    - Export disponible
    - Mode drill-down narratif (Insight Guide) implemente dans le dashboard overview avec narration contextualisee par onglet
    - Interpretable par managers non techniques: lecture KPI -> interpretation business -> action recommandee

    ### 4.7 Report Generation (nouvelle exigence explicite)

    Statut: 58% (partiellement implemente)

    - Existant:
    - scripts de generation de rapport PDF (hors parcours produit utilisateur)
    - exports tabulaires depuis UI
    - Manquant:
    - endpoint/app workflow "Generate report" on-demand par plage date + service/all
    - template de rapport management versionne et unifie
    - orchestration async et monitoring de generation

    ### 4.8 AI & Advanced Analytics

    Statut: 100% (finalise)

    - Segmentation, churn prediction, anomaly detection operationnels
    - Gouvernance modele implementee (monitoring derive par feature avec severite low/medium/high)
    - Calibration periodique formalisee (Brier score, ECE, bins de calibration, cadence de recalibration)
    - Protocole d'evaluation stable versionne (split stratifie fixe, seuil par defaut, recommandations d'exploitation)

    ## 5. Conformite au modele business (trial -> renew -> churn)

    Niveau global: Excellent (100%)

    - Le flux trial/paid/churn est bien reflete dans les KPIs et requetes
    - Les cycles de billing sont pris en compte via service_types
    - Les contraintes telecom et le contexte SMS-first sont pris en compte dans les modules campaign/billing
    - Couche de regles metier explicites et testees implementee:
    - promotions detectees via rattachement campagne type "promotion"
    - extensions trial detectees via depassement trial_duration_days (service_types)
    - synthese standardisee exposee dans /analytics/trial/kpis -> business_exception_rules (status, ratios, version)
    - tests unitaires dedies passes (tests/test_business_rules.py)

    ## 6. Points forts constates

    1. Couverture fonctionnelle large et coherentement structuree.
    2. Bonne separation des couches backend (router/service/repository) sur modules critiques.
    3. Caching present (backend + frontend) avec versioning applique sur modules sensibles.
    4. Stack AI deja exploitable en demonstration et en usage analytique.
    5. ETL reel disponible, avec scripts de remediation data quand la source est incomplete.

    ## 7. Ecarts et risques principaux

    1. Reporting management integre produit non finalise.
    2. Qualite/volumetrie campaign source heterogene selon periodes (risque d'interpretation KPI).
    3. Couverture de tests encore limitee face a la surface fonctionnelle (tests backend presents mais extension requise).
    4. Gouvernance ML partielle (drift, calibration, explainability standardisee).
    5. Quelques divergences de comportement cache/environnement (front local vs docker/proxy) deja observees.

    ## 8. Livrables obligatoires: statut

    1. Comprendre et formaliser le projet: OK (90%)
    2. Data model/schema/relations: OK (85%)
    3. Definitions KPI et formules: OK (85%)
    4. Dashboard/prototype: OK (90%)
    5. Behavioral analysis & findings: OK (82%)
    6. Recommandations actionnables: Partiel (75%)
    7. Justification/evidence de chaque reco: Partiel (72%)
    8. AI/advanced analytics: OK (83%)
    9. Business impact summary one-page: Partiel (68%)

    ## 9. Perspectives court terme (0 a 6 semaines)

    ### Priorite P0 (Semaine 1-2)

    1. Implementer un module de generation de rapport on-demand dans le produit:

    - endpoint backend: POST /reports/generate
    - params: start_date, end_date, service_id|all, format (pdf)
    - sortie: url de telechargement + metadata (generated_at, scope)

    2. Ajouter un bouton "Generate Report" dans les pages Dashboard/Campaign/Trial avec suivi du statut.
    3. Verrouiller un template standard (Executive Summary + KPI + Insights + Recommendations + Limits).

    ### Priorite P1 (Semaine 2-4)

    1. Renforcer la qualite campaign data:

    - controles de coherence cibles/envoyes/livres/conversions
    - checklist de validation post-ETL

    2. Ajouter 15-20 tests backend supplementaires sur KPI critiques:

    - trial conversion
    - churn/retention
    - campaign ROI
    - filtres date/service

    3. Ajouter un jeu de tests E2E minimum sur 3 parcours metier (dashboard, trial, campaign).

    ### Priorite P2 (Semaine 4-6)

    1. Standardiser 5 recommandations business evidence-based dans un bloc dedie.
    2. Ajouter un Service Health Score et User Engagement Score documentes.
    3. Finaliser un one-pager business impact multi-service.

    ## 10. Perspectives long terme (2 a 12 mois)

    ### Axe A - Industrialisation Data/Analytics

    1. Mettre en place un data quality framework (freshness, completeness, consistency, validity) avec alertes.
    2. Introduire un data contract par source (operator feeds, campaign logs, billing).
    3. Evoluer vers orchestration ETL planifiee (scheduler + retries + observabilite centralisee).

    ### Axe B - Decision Intelligence

    1. Passer d'un dashboard descriptif a un copilote decisionnel:

    - recommandations priorisees par impact
    - simulation "what-if" campagne/pricing/frequence

    2. Ajouter attribution campagne plus robuste (time-decay, multi-touch simple, holdout tests).
    3. Ajouter benchmark inter-services (scorecard executive mensuelle).

    ### Axe C - MLOps pragmatique

    1. Tracking de performance modele dans le temps (AUC, recall, precision, drift).
    2. Retraining cadence automatique et seuils de rollback modele.
    3. Explainability standardisee dans l'UI (drivers churn par segment/service).

    ### Axe D - Produit & Adoption

    1. Role-based reporting packs (Management / Product / Marketing / Ops).
    2. Workflows collaboratifs (commentaires insight, assignation actions, suivi outcomes).
    3. Catalogue KPI officiel versionne (source of truth gouvernance).

    ## 11. Roadmap cible de finalisation

    ### Jalons

    - J+15: report generation on-demand en beta + template management v1
    - J+30: QA KPI critique + campaign data controls + reco evidence pack
    - J+45: business impact summary v1 + health/engagement scores
    - J+60: stabilisation release et demo finale orientee decision

    ### KPI de pilotage projet

    1. Couverture exigences cahier de charge >= 95%
    2. Taux de tests critiques passants >= 98%
    3. Temps de generation rapport PDF < 20s (service unique) et < 60s (all services)
    4. Ecart KPI entre reruns < 1% hors nouvelles donnees

    ## 12. Conclusion

    Le projet est solide, coherent et deja utile pour la decision metier.
    La priorite n'est plus de "creer des ecrans", mais de transformer l'existant en systeme decisionnel industrialise:

    - reporting management integre,
    - preuves/recommandations standardisees,
    - qualite data/ML durable.

    Verdict:

    - Etat actuel: Bon a tres bon
    - Risque: Modere et maitrisable
    - Perspective: forte valeur business a court terme si la couche reporting + evidence est finalisee rapidement.

    ## 13. Addendum 13/04/2026 - Verification base prod (raisons de drop-off)

    Verification effectuee directement en SQL sur la connexion analytics configuree (host=localhost, db=analytics_db).

    Resultats constates:

    - total_dropoffs: 677906
    - early_dropoffs_3d: 435118
    - technical_dropoffs: 0
    - voluntary_dropoffs: 677906
    - rows_with_reason: 677906
    - top_reasons: `voluntary` uniquement

    Interpretation:

    1. Le pipeline data fournit actuellement une raison de churn non granulaire (`voluntary`) pour la quasi-totalite des cas.
    2. La part technique est a 0 dans les donnees disponibles; l'analyse causale 4.2 est donc correcte structurellement, mais limitee par la qualite detaillee de la source reason.
    3. Le bloc "Top Reported Reasons" du dashboard et du reporting management doit etre interprete comme un indicateur de qualite de saisie des raisons, pas encore comme une taxonomie business fine.

    Actions recommandees (documentation + reporting):

    1. Documenter officiellement dans le catalogue KPI que `churn_reason` est actuellement a granularite faible.
    2. Ajouter dans le rapport management une note systematique: "Reason granularity limited in current source (dominant value: voluntary)".
    3. Planifier un enrichissement ETL pour normaliser les raisons metier (ex: prix, valeur percue, support, qualite reseau, echec paiement, autre) avec mapping versionne.

