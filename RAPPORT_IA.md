# Rapport Technique â€” Modules d'Intelligence Artificielle

## Plateforme d'Analytics Comportementale â€” PFE 2025/2026

---

## 0. Cadre du rapport

### 0.1 Objet

Ce document analyse les composants IA/ML implÃ©mentÃ©s dans le code source de la plateforme.
Le rapport est basÃ© sur lecture effective des fichiers backend, frontend, scripts ETL et artefacts modÃ¨les.
Le but est de fournir un support acadÃ©mique pour soutenance PFE.

### 0.2 PÃ©rimÃ¨tre auditÃ©

PÃ©rimÃ¨tre backend Python/FastAPI/SQLAlchemy.
PÃ©rimÃ¨tre frontend React hooks + pages IA.
PÃ©rimÃ¨tre modÃ¨les sÃ©rialisÃ©s joblib.
PÃ©rimÃ¨tre ETL cohortes et logique churn.
PÃ©rimÃ¨tre dÃ©tection d'anomalies cÃ´tÃ© API.

### 0.3 Sources auditÃ©es explicitement

Fichier: user-analytics-backend/ml_models/churn_predictor.py
Fichier: user-analytics-backend/ml_models/churn_metrics.joblib
Fichier: user-analytics-backend/ml_models/churn_model.joblib
Fichier: user-analytics-backend/ml_models/segmentation_kmeans.joblib
Fichier: user-analytics-backend/app/routers/ml_churn.py
Fichier: user-analytics-backend/app/routers/churn_analysis.py
Fichier: user-analytics-backend/app/repositories/churn_repo.py
Fichier: user-analytics-backend/app/services/churn_service.py
Fichier: user-analytics-backend/app/repositories/segmentation_repo.py
Fichier: user-analytics-backend/app/services/segmentation_service.py
Fichier: user-analytics-backend/app/routers/segmentation.py
Fichier: user-analytics-backend/app/routers/anomalies.py
Fichier: user-analytics-backend/scripts/compute_cohorts.py
Fichier: user-analytics-backend/scripts/etl/recalcul_cohorts.py
Fichier: user-analytics-backend/app/schemas/ml_churn.py
Fichier: user-analytics-backend/app/schemas/churn_analysis.py
Fichier: user-analytics-backend/app/schemas/segmentation.py
Fichier: user-analytics-backend/app/models/subscriptions.py
Fichier: user-analytics-backend/app/models/user_activities.py
Fichier: user-analytics-backend/app/models/billing_events.py
Fichier: user-analytics-backend/app/models/unsubscriptions.py
Fichier: user-analytics-backend/app/models/cohorts.py
Fichier: analytics-platform-front/src/pages/dashboard/AIChurnInsights.jsx
Fichier: analytics-platform-front/src/hooks/useChurnPredictionMetrics.js
Fichier: analytics-platform-front/src/hooks/useChurnPredictionScores.js
Fichier: analytics-platform-front/src/hooks/useChurnPredictionTrain.js
Fichier: analytics-platform-front/src/components/dashboard/churn_prediction/churn_dashboard.jsx
Fichier: analytics-platform-front/src/hooks/useSegmentationKPIs.js
Fichier: analytics-platform-front/src/hooks/useSegmentationClusters.js
Fichier: analytics-platform-front/src/hooks/useSegmentationProfiles.js
Fichier: analytics-platform-front/src/pages/dashboard/UserSegmentationPage.jsx
Fichier: analytics-platform-front/src/hooks/useAnomalies.js
Fichier: analytics-platform-front/src/services/anomalies.js
Fichier: analytics-platform-front/src/pages/dashboard/AnomalyDetectionPage.jsx
Fichier: docs/ml_churn_report.md
Fichier: docs/kpis.md
Fichier: user-analytics-backend/app/utils/temporal.py
Fichier: user-analytics-backend/app/core/date_ranges.py
Fichier: user-analytics-backend/app/main.py

### 0.4 Contexte mÃ©tier rappelÃ©

Secteur: tÃ©lÃ©communications numÃ©riques tunisiennes.
Services suivis: ElJournal, Esports.tn, ttoons, Tawer.
Funnel: essai 3 jours puis renouvellement automatique.
Canaux dominants: SMS/USSD.
FenÃªtre de donnÃ©es annoncÃ©e: septembre-octobre 2025.
Volume annoncÃ©: 228 707 transactions.

### 0.5 MÃ©thodologie d'analyse

Lecture statique du code source.
Extraction de SQL exact des sections critiques.
Inspection des objets joblib via Python.
Croisement backend/frontend/schÃ©mas.
Signalement explicite des Ã©carts entre spÃ©cification attendue et implÃ©mentation rÃ©elle.

### 0.6 RÃ¨gle de traÃ§abilitÃ©

Toute information non trouvÃ©e dans le code est marquÃ©e ainsi:
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]

---

## RÃ©sumÃ© ExÃ©cutif (1 page)

### RE.1 Objectif des modules IA

Le projet implÃ©mente trois briques IA/analytique avancÃ©e orientÃ©es dÃ©cision opÃ©rationnelle.
Brique 1: prÃ©diction du churn supervisÃ©e pour prioriser la rÃ©tention.
Brique 2: segmentation comportementale de type clustering pour personnaliser les campagnes.
Brique 3: dÃ©tection d'anomalies temporelles pour alerter sur incidents business.

### RE.2 Les 3 modules implÃ©mentÃ©s et rÃ´le mÃ©tier

Module Churn IA:
Sortie: score de risque de churn par abonnement actif.
Usage: priorisation CRM, actions anti-churn, listes top risque.

Module Segmentation K-Means:
Sortie: cluster utilisateur et distribution des segments.
Usage: ciblage marketing diffÃ©renciÃ© et analyse de valeur par segment.

Module DÃ©tection d'anomalies:
Sortie: Ã©vÃ©nements anormaux par mÃ©trique/jour/sÃ©vÃ©ritÃ©.
Usage: monitoring business et diagnostic rapide churn/revenus/activitÃ©.

### RE.3 RÃ©sultats clÃ©s observÃ©s (extraits rÃ©els)

Le modÃ¨le churn sÃ©rialisÃ© est une LogisticRegression scikit-learn.
MÃ©triques extraites de churn_metrics.joblib:
Accuracy = 0.6594546191075198
ROC-AUC = 0.8201320134904057
Taux de churn entraÃ®nement = 0.9631460674157304
n_samples = 1 172 575
n_positive = 1 129 361
n_negative = 43 214

Le modÃ¨le segmentation sÃ©rialisÃ© est un KMeans avec n_clusters=4.
FenÃªtre de training segmentation stockÃ©e:
start_date = 2025-09-25T12:00:42.275986
end_date = 2025-10-25T12:00:42.275986
service_id = null

### RE.4 Valeur ajoutÃ©e business

Passage d'une lecture descriptive Ã  une orchestration prescriptive.
Le churn module permet d'anticiper les dÃ©parts plutÃ´t que de les constater.
La segmentation facilite le design de campagnes SMS Ã  ROI diffÃ©renciÃ©.
L'anomaly engine rÃ©duit le dÃ©lai de dÃ©tection des incidents invisibles sans surveillance statistique.

### RE.5 Points forts techniques

Architecture API claire par routeurs spÃ©cialisÃ©s.
Feature engineering churn riche et ancrÃ© SQL.
Persistance joblib des modÃ¨les.
IntÃ©gration frontend opÃ©rationnelle pour churn et anomalies.
Couches de cache TTL pour rÃ©duire la latence sur segmentation/churn dashboards.

### RE.6 Risques critiques identifiÃ©s

DÃ©sÃ©quilibre extrÃªme des classes churn dans les mÃ©triques sauvegardÃ©es.
AmbiguÃ¯tÃ© entre dÃ©finition mÃ©tier du churn et label rÃ©el codÃ©.
Segmentation frontend contient encore des fallbacks mock.
DÃ©tection anomalies mentionne Isolation Forest en texte mais non implÃ©mentÃ©e algorithmiquement.
IncohÃ©rences entre endpoints demandÃ©s dans cahier et endpoints rÃ©ellement exposÃ©s.

---

## PARTIE I â€” PRÃ‰DICTION DU CHURN

### 1.1 Contexte et Justification MÃ©tier

#### 1.1.1 Pourquoi le churn est critique ici

Le modÃ¨le abonnement SMS/USSD repose sur rÃ©currence de facturation.
Une perte d'abonnÃ© diminue immÃ©diatement revenu rÃ©current.
La fenÃªtre d'intervention est courte Ã  cause du cycle essai puis renouvellement.
Les churn techniques peuvent signaler un incident systÃ¨me impactant en masse.

#### 1.1.2 Alignement avec le code

Le code calcule des variables orientÃ©es comportement rÃ©cent.
Les features activitÃ© 7j/30j servent Ã  dÃ©tecter essoufflement usage.
Les features billing capturent friction de paiement et parcours premier charge.
Le marqueur trial churn cible la phase la plus fragile du funnel.

#### 1.1.3 Exemple concret issu des mÃ©triques sauvegardÃ©es

Churn rate entraÃ®nement observÃ© = 96.31%.
Ce niveau est anormalement Ã©levÃ© pour un dataset non biaisÃ©.
InterprÃ©tation possible:
FenÃªtre d'apprentissage orientÃ©e historiques abonnements clÃ´turÃ©s.
Ou dÃ©finition de label favorisant classes positives.
Ou fuite de structure des donnÃ©es sources.

#### 1.1.4 CoÃ»t abonnÃ© perdu vs acquisition

[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Le code ne contient pas de modÃ¨le financier CAC/LTV explicite.
Aucun coÃ»t unitaire acquisition n'est paramÃ©trÃ©.
Aucun calcul direct perte/retour d'investissement anti-churn n'est implÃ©mentÃ©.

#### 1.1.5 FenÃªtre d'intervention

Le scoring est rÃ©alisÃ© sur abonnements actifs/trial.
Le threshold par dÃ©faut pour classification binaire est 0.4.
La catÃ©gorie risque est Low/Medium/High.
L'endpoint /ml/churn/scores fournit top users priorisables immÃ©diatement.

### 1.2 DÃ©finition de la Variable Cible

#### 1.2.1 DÃ©finition effective dans le code

La variable churned n'est pas dÃ©finie par subscription_end_date IS NOT NULL.
La dÃ©finition effective est basÃ©e sur status.
RÃ¨gle codÃ©e:
status in ('cancelled','expired') => churned=1
sinon churned=0

Code SQL exact extrait de churn_predictor.py:

```sql
CASE
  WHEN LOWER(COALESCE(s.status, '')) IN ('cancelled', 'expired') THEN 1
  ELSE 0
END AS churned
```

#### 1.2.2 Ã‰cart avec documentation existante

docs/ml_churn_report.md mentionne:
churned = 1 if subscription_end_date IS NOT NULL
Cela n'est pas strictement conforme au code source actuel.
Conclusion acadÃ©mique:
La vÃ©ritÃ© de rÃ©fÃ©rence technique est la requÃªte dans churn_predictor.py.

#### 1.2.3 RequÃªte SQL de base (extrait exact)

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
      WHEN LOWER(COALESCE(s.status, '')) IN ('cancelled', 'expired') THEN 1
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
```

#### 1.2.4 Pourquoi subscription_end_date IS NOT NULL n'est pas utilisÃ© directement

Le systÃ¨me peut contenir incohÃ©rences sur dates de fin selon source.
Le status est ici choisi comme signal principal de churn logique.
Cette dÃ©cision est cohÃ©rente avec commentaire dans classe ChurnPredictor.

#### 1.2.5 DiffÃ©rence churn trial vs churn payant

La feature is_trial_churn reprÃ©sente churn pendant pÃ©riode essai.
RÃ¨gle:
unsubscription_datetime prÃ©sent
et days_since_subscription <= trial_duration_days
Alors is_trial_churn = 1.

Extrait exact:

```sql
CASE
  WHEN b.unsubscription_datetime IS NOT NULL
   AND COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
       <= b.trial_duration_days
  THEN 1 ELSE 0
END AS is_trial_churn
```

#### 1.2.6 Calcul days_to_first_unsub

Pour churners:
jours entre subscription_start_date et unsubscription_datetime.
Pour non churners:
sentinel 999.

Extrait:

```sql
CASE
  WHEN b.unsubscription_datetime IS NOT NULL
  THEN COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
  ELSE 999
END AS days_to_first_unsub
```

### 1.3 Feature Engineering

#### 1.3.1 Liste exhaustive des features utilisÃ©es

Feature names extraits exactement de self.feature_names:

1. days_since_last_activity
2. nb_activities_7d
3. nb_activities_30d
4. billing_failures_30d
5. days_since_first_charge
6. is_trial_churn
7. avg_retention_d7
8. service_billing_frequency
9. days_to_first_unsub

#### 1.3.2 Tableau des features

| Feature                   | Type      | Description                      | Formule/Source                                    | Justification mÃ©tier                 |
| ------------------------- | --------- | -------------------------------- | ------------------------------------------------- | ------------------------------------ |
| days_since_last_activity  | NumÃ©rique | Ã‚ge de derniÃ¨re activitÃ©         | ref_time - MAX(user_activities.activity_datetime) | Mesure dÃ©sengagement                 |
| nb_activities_7d          | NumÃ©rique | ActivitÃ© courte pÃ©riode          | COUNT activitÃ©s 7 jours                           | Signal prÃ©coce attrition             |
| nb_activities_30d         | NumÃ©rique | ActivitÃ© mensuelle               | COUNT activitÃ©s 30 jours                          | StabilitÃ© usage                      |
| billing_failures_30d      | NumÃ©rique | Echecs de facturation            | COUNT billing_events FAILED sur 30 jours          | Friction paiement et churn technique |
| days_since_first_charge   | NumÃ©rique | AnciennetÃ© depuis 1er succÃ¨s     | ref_time - MIN(first successful first_charge)     | MaturitÃ© client                      |
| is_trial_churn            | Binaire   | Churn pendant essai              | days_since_subscription <= trial_duration_days    | FragilitÃ© pÃ©riode d'essai            |
| avg_retention_d7          | NumÃ©rique | RÃ©tention de cohorte du service  | cohorts.retention_d7                              | QualitÃ© structurelle du service      |
| service_billing_frequency | NumÃ©rique | FrÃ©quence de facturation service | service_types.billing_frequency_days              | Impact cadence billing               |
| days_to_first_unsub       | NumÃ©rique | Temps au churn                   | calcul depuis unsubscriptions sinon 999           | IntensitÃ© risque historique          |

#### 1.3.3 SQL exact des LEFT JOIN LATERAL

```sql
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

#### 1.3.4 Gestion des valeurs nulles

Usage systÃ©matique de COALESCE.
Valeurs sentinelles observÃ©es:
999 pour dÃ©lais non dÃ©finis.
0 pour compteurs absents.

#### 1.3.5 Traitement des valeurs infinies et NaN

CÃ´tÃ© Python:
X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
Cette Ã©tape protÃ¨ge l'entraÃ®nement.

#### 1.3.6 Analyse de corrÃ©lation attendue (thÃ©orique)

nb_activities_30d Ã©levÃ© devrait rÃ©duire churn.
billing_failures_30d Ã©levÃ© devrait augmenter churn.
days_since_last_activity Ã©levÃ© devrait augmenter churn.
Attention:
Le signe des coefficients dÃ©pend du codage final du dataset.

#### 1.3.7 Coefficients rÃ©els extraits

| Feature                   |             Coefficient |
| ------------------------- | ----------------------: |
| days_since_last_activity  |  0.00026778081424942257 |
| nb_activities_7d          |      0.6659947940371373 |
| nb_activities_30d         |       1.347404387228841 |
| billing_failures_30d      |                     0.0 |
| days_since_first_charge   | -0.00033164405495273645 |
| is_trial_churn            |  -0.0003932151873579291 |
| avg_retention_d7          |     0.13941355714395723 |
| service_billing_frequency | -3.3197603119247875e-07 |
| days_to_first_unsub       |  -0.0007865075503406647 |

Commentaire critique:
Le signe positif de nb_activities_30d est contre-intuitif mÃ©tier.
Cela suggÃ¨re un effet de confusion liÃ© au dataset ou au label.

### 1.4 Algorithme de Machine Learning

#### 1.4.1 Identification prÃ©cise de l'algorithme

Import explicite observÃ©:
from sklearn.linear_model import LogisticRegression
Objet sÃ©rialisÃ© churn_model.joblib:
model_type = LogisticRegression
module = sklearn.linear_model.\_logistic

#### 1.4.2 HyperparamÃ¨tres observÃ©s

class_weight = balanced
random_state = 42
max_iter = 2000
solver = lbfgs
C = 1.0
penalty (get_params) = deprecated

#### 1.4.3 Pourquoi cet algorithme est plausible ici

Simple et robuste sur features tabulaires.
Rapide Ã  entraÃ®ner.
ProbabilitÃ©s directement disponibles.
ExplicabilitÃ© via coefficients.

#### 1.4.4 Limites de la Logistic Regression dans ce cas

LinÃ©aritÃ© log-odds potentiellement insuffisante pour comportement non linÃ©aire.
SensibilitÃ© au dÃ©sÃ©quilibre et calibration.
DÃ©pendance forte Ã  la qualitÃ© de feature engineering.

#### 1.4.5 Formule mathÃ©matique

Le score probabiliste est:

$$
P(\text{churn}=1\mid X)=\sigma\left(\beta_0+\sum_{i=1}^{n}\beta_i x_i\right)
=\frac{1}{1+e^{-\left(\beta_0+\sum_{i=1}^{n}\beta_i x_i\right)}}
$$

oÃ¹ $n=9$ features dans le code actuel.

### 1.5 Pipeline d'EntraÃ®nement

#### 1.5.1 Code d'entraÃ®nement exact (extrait)

```python
def train(self, db_session: Session) -> dict[str, Any]:
    X, y = self.generate_training_dataset(db_session)
    n_positive = int((y == 1).sum())
    n_negative = int((y == 0).sum())
    label_distribution = {"1": n_positive, "0": n_negative}

    if y.nunique() < 2:
        warning = (
            "Training skipped: dataset contains a single class only. "
            "Need both churned (1) and non-churned (0) samples to train LogisticRegression."
        )
        metrics = {
            "trained_at": pd.Timestamp.utcnow().isoformat(),
            "roc_auc": None,
            "churn_rate": float(y.mean()) if len(y) else 0.0,
            "accuracy": 1.0,
            "report": {
                "warning": warning,
                "class_distribution": {
                    "n_positive": n_positive,
                    "n_negative": n_negative,
                },
                "label_distribution": label_distribution,
            },
            "coefficients": {},
            "n_samples": int(len(y)),
            "n_positive": n_positive,
            "n_negative": n_negative,
            "warning": warning,
        }
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(metrics, self.metrics_path)
        return metrics

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    self.model.fit(X_train, y_train)

    y_pred = self.model.predict(X_test)
    y_proba = self.model.predict_proba(X_test)[:, 1]

    roc_auc = None
    if y_test.nunique() > 1:
        roc_auc = float(roc_auc_score(y_test, y_proba))

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    churn_rate = float(y.mean()) if len(y) else 0.0

    coeffs = {}
    try:
        coeffs = dict(zip(self.feature_names, self.model.coef_[0].astype(float)))
    except Exception:
        coeffs = {}

    metrics = {
        "trained_at": pd.Timestamp.utcnow().isoformat(),
        "roc_auc": roc_auc,
        "churn_rate": churn_rate,
        "accuracy": float(report.get("accuracy", 0.0)),
      "report": {
        **report,
        "label_distribution": label_distribution,
      },
        "coefficients": coeffs,
        "n_samples": int(len(df := pd.concat([X, y.rename("churned")], axis=1))),
      "n_positive": n_positive,
      "n_negative": n_negative,
        "warning": None,
    }

    self.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(self.model, self.model_path)
    joblib.dump(metrics, self.metrics_path)

    return metrics
```

#### 1.5.2 PrÃ©paration des donnÃ©es

Dataset SQL au niveau abonnement.
SÃ©lection des 9 features.
Remplacement infinis/NaN.
Cible castÃ©e en int.

#### 1.5.3 Split train/test

Ratio test = 20%.
Random state = 42.
Stratification activÃ©e si au moins 2 classes.

#### 1.5.4 Validation croisÃ©e

[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Aucune cross-validation k-fold observÃ©e dans churn_predictor.py.

#### 1.5.5 Sauvegarde modÃ¨le

churn_model.joblib pour l'estimateur.
churn_metrics.joblib pour mÃ©triques et coefficients.

### 1.6 MÃ©triques de Performance

#### 1.6.1 Tableau synthÃ¨se mÃ©triques rÃ©elles

| MÃ©trique             |             Valeur | InterprÃ©tation                               |
| -------------------- | -----------------: | -------------------------------------------- |
| Accuracy             | 0.6594546191075198 | 65.95% de prÃ©dictions correctes globales     |
| Precision (classe 1) |    0.9960185078237 | TrÃ¨s peu de faux positifs pour churn positif |
| Recall (classe 1)    | 0.6490180279096125 | 64.90% des churns positifs dÃ©tectÃ©s          |
| F1 (classe 1)        | 0.7859204992320126 | Compromis precision/recall classe positive   |
| AUC-ROC              | 0.8201320134904057 | Bonne sÃ©paration probabiliste globale        |
| Churn rate train     | 0.9631460674157304 | Dataset extrÃªmement dÃ©sÃ©quilibrÃ©             |

#### 1.6.2 DÃ©tail classification_report

Classe 0:
precision = 0.09225502095403852
recall = 0.9321994677773922
f1 = 0.16789439136459777
support = 8643

Classe 1:
precision = 0.9960185078237
recall = 0.6490180279096125
f1 = 0.7859204992320126
support = 225872

Weighted avg:
precision = 0.9627104984553676
recall = 0.6594546191075198
f1 = 0.7631432796499046
support = 234515

#### 1.6.3 Pourquoi recall > precision peut Ãªtre prioritaire mÃ©tier

Dans anti-churn, manquer un churner coÃ»te revenu futur.
Faux nÃ©gatif = perte client non traitÃ©e.
Faux positif = coÃ»t campagne inutile mais souvent infÃ©rieur Ã  perte d'abonnement.

#### 1.6.4 Matrice de confusion

[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
La matrice n'est pas persistÃ©e dans churn_metrics.joblib actuel.

#### 1.6.5 Analyse d'erreurs

Risque majeur identifiÃ©:
TrÃ¨s faible precision classe 0.
Cela indique difficultÃ© du modÃ¨le Ã  reconnaÃ®tre non-churn dans contexte trÃ¨s dÃ©sÃ©quilibrÃ©.
Impact:
Le modÃ¨le peut sur-qualifier churn selon perspective de classe minoritaire.

### 1.7 InfÃ©rence et Scoring en Production

#### 1.7.1 Fonction de scoring active (extrait exact)

```python
def predict_active_subscriptions(
    self,
    db_session: Session,
    *,
    threshold: float = 0.4,
    store_predictions: bool = False,
    service_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> ChurnPredictionResult:
    if not self.load():
        raise FileNotFoundError("Model not trained yet. Call /ml/churn/train first.")

    query, params = self._active_scoring_features_sql(
        service_id=service_id, start_date=start_date, end_date=end_date
    )
    df = self._read_sql_to_df(db_session, query, params=params)
    if df.empty:
        return ChurnPredictionResult(df=pd.DataFrame(), distribution={"Low": 0, "Medium": 0, "High": 0})

    X = df[self.feature_names].copy()
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

    churn_risk_scores = self.model.predict_proba(X)[:, 1]
    churn_risk_scores = np.clip(churn_risk_scores.astype(float), 0.0, 1.0)

    df = df.copy()
    df["churn_risk"] = churn_risk_scores
    df["predicted_churn"] = (df["churn_risk"] >= threshold).astype(int)
    df["risk_category"] = df["churn_risk"].apply(self._risk_category)
```

#### 1.7.2 CatÃ©gories de risque

Low si churn_risk < 0.3
Medium si 0.3 <= churn_risk < 0.6
High si >= 0.6

#### 1.7.3 Endpoints FastAPI churn

POST /ml/churn/train
GET /ml/churn/metrics
GET /ml/churn/scores

#### 1.7.4 SchÃ©ma rÃ©ponse train

via ChurnTrainMetricsResponse:
trained_at: str
roc_auc: Optional[float]
accuracy: float [0,1]
churn_rate: float [0,1]
n_samples: int
n_positive: int
n_negative: int
report: dict
coefficients: dict[str,float]

#### 1.7.5 SchÃ©ma rÃ©ponse scores

via ChurnScoresResponse:
generated_at: str
threshold: float
distribution: list[ChurnRiskDistributionItem]
top_users: list[ChurnTopUserItem]
active_users_scored: int

ChurnTopUserItem:
user_id
phone_number
service_name
churn_risk
risk_category
predicted_churn

### 1.8 IntÃ©gration Frontend

#### 1.8.1 Page et composants

Page: AIChurnInsights.jsx
Composant principal: churn_dashboard.jsx
Hooks:
useChurnPredictionMetrics
useChurnPredictionScores
useChurnPredictionTrain

#### 1.8.2 Flux frontend

Chargement metrics depuis /ml/churn/metrics.
Chargement scores depuis /ml/churn/scores avec params top/threshold.
Action train admin via /ml/churn/train.
Refresh simultanÃ© metrics+scores aprÃ¨s entraÃ®nement.

#### 1.8.3 Visualisations disponibles

KPI card ROC-AUC.
KPI card Accuracy.
KPI card Churn rate train.
KPI card Train samples.
Bar chart distribution risques.
Table top coefficients.
Table top risky users.

#### 1.8.4 Extrait hook scores

```javascript
const res = await api.get("/ml/churn/scores", {
  params: {
    top,
    threshold,
    store,
    start_date: filters?.start_date,
    end_date: filters?.end_date,
    service_id: filters?.service_id,
  },
});
```

#### 1.8.5 Niveau de maturitÃ© UX

Gestion loading, erreurs, retry prÃ©sents.
Options topN et threshold Ã©ditables.
Affichage catÃ©gories colorÃ©es Low/Medium/High.
Pas d'explicabilitÃ© locale type SHAP dans UI.

### 1.9 Limites et AmÃ©liorations Futures

#### 1.9.1 Limites actuelles

DÃ©sÃ©quilibre classes trÃ¨s fort.
Absence de calibration probabiliste explicite.
Pas de monitoring drift implÃ©mentÃ©.
Pas de validation temporelle walk-forward.

#### 1.9.2 Risque de leakage

Le code tente de limiter leakage via ref_time = subscription_end_date pour churned.
C'est une bonne pratique partielle.
Reste un risque selon disponibilitÃ© temporelle de certaines tables agrÃ©gÃ©es.

#### 1.9.3 Drift temporel

FenÃªtre production observÃ©e 2025-09 Ã  2025-10.
ApplicabilitÃ© hors fenÃªtre non garantie.

#### 1.9.4 Recommandations concrÃ¨tes

Ajouter split temporel train/validation/test.
Tester XGBoost/LightGBM en benchmark.
Ajouter calibration Platt/Isotonic.
Ajouter SHAP global + local.
Automatiser rÃ©entraÃ®nement mensuel.
Versionner modÃ¨le + mÃ©triques + data slice.

---

## PARTIE II â€” SEGMENTATION UTILISATEURS (K-MEANS)

### 2.1 Contexte et Objectif MÃ©tier

#### 2.1.1 Besoin mÃ©tier

Tous les abonnÃ©s n'ont pas la mÃªme valeur.
Les campagnes massives non segmentÃ©es dÃ©gradent ROI.
La segmentation permet personnalisation des offres SMS.

#### 2.1.2 Cas d'usage opÃ©rationnels

Campagnes upsell sur Power Users.
RÃ©activation sur Occasionnels.
Parcours onboarding renforcÃ© sur Trial Only.
Priorisation support sur segments Ã  fort churn.

### 2.2 DonnÃ©es Sources et PrÃ©paration

#### 2.2.1 Tables exploitÃ©es par segmentation_repo

subscriptions
billing_events
services
service_types

#### 2.2.2 Features effectivement utilisÃ©es pour clustering service

Contrairement au template thÃ©orique, l'entraÃ®nement KMeans utilise deux dimensions principales:
Feature x: ratio billing_count vs percentile p75_billing.
Feature y: ratio revenue vs percentile p75_revenue.

#### 2.2.3 Tableau de mapping feature/source rÃ©el

| Feature       | Table source                         | AgrÃ©gation                          | Normalisation                                    |
| ------------- | ------------------------------------ | ----------------------------------- | ------------------------------------------------ |
| billing_count | billing_events + subscriptions       | COUNT events SUCCESS par user       | ratio contre percentile p75                      |
| revenue       | service_types.price + billing_events | SUM(price) SUCCESS par user         | ratio contre percentile p75                      |
| x             | dÃ©rivÃ©e                              | LEAST(billing_count/p75_billing,1)  | StandardScaler au train                          |
| y             | dÃ©rivÃ©e                              | LEAST(revenue/p75_revenue,1)        | StandardScaler au train                          |
| active_days   | billing_events                       | COUNT DISTINCT DATE(event_datetime) | utilisÃ© en profiling, pas training KMeans direct |

#### 2.2.4 SQL extraction principal (exact)

```sql
WITH user_stats AS (
    SELECT
        s.user_id,
        COUNT(be.id) FILTER (WHERE UPPER(TRIM(COALESCE(be.status, ''))) = 'SUCCESS') AS billing_count,
        COALESCE(
            SUM(COALESCE(st.price, 0)) FILTER (WHERE UPPER(TRIM(COALESCE(be.status, ''))) = 'SUCCESS'),
            0
        ) AS revenue,
        COUNT(DISTINCT DATE(be.event_datetime)) AS active_days,
        COUNT(DISTINCT s.id) AS sub_count
    FROM subscriptions s
    JOIN billing_events be ON be.subscription_id = s.id
    JOIN services sv ON sv.id = s.service_id
    JOIN service_types st ON st.id = sv.service_type_id
    WHERE be.event_datetime BETWEEN :start AND :end
    GROUP BY s.user_id
),
percentiles AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY billing_count) AS p25_billing,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY billing_count) AS p75_billing,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) AS p25_revenue,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) AS p75_revenue
    FROM user_stats
    WHERE billing_count > 0
),
segmented AS (
    SELECT
        us.user_id,
        us.billing_count,
        us.revenue,
        us.active_days,
        CASE
            WHEN COALESCE(p.p75_billing, 0) > 0
            THEN LEAST(us.billing_count::float / p.p75_billing, 1.0)
            ELSE 0
        END AS x,
        CASE
            WHEN COALESCE(p.p75_revenue, 0) > 0
            THEN LEAST(us.revenue::float / p.p75_revenue, 1.0)
            ELSE 0
        END AS y,
        CASE
            WHEN us.billing_count >= COALESCE(p.p75_billing, us.billing_count + 1)
             AND us.revenue >= COALESCE(p.p75_revenue, us.revenue + 1)
                THEN 'Power Users'
            WHEN us.billing_count >= COALESCE(p.p25_billing, us.billing_count + 1)
             AND us.revenue >= COALESCE(p.p25_revenue, us.revenue + 1)
                THEN 'Regular Loyals'
            WHEN us.billing_count > 0
                THEN 'Occasional Users'
            ELSE 'Trial Only'
        END AS segment
    FROM user_stats us
    CROSS JOIN percentiles p
)
SELECT
    user_id::text AS user_id,
    x,
    y,
    segment,
    active_days,
    revenue
FROM segmented
ORDER BY revenue DESC
LIMIT 50000
```

#### 2.2.5 Commentaire mÃ©thodologique

Le clustering visuel consommÃ© frontend est dÃ©jÃ  segmentÃ© SQL par rÃ¨gles percentiles.
Le train KMeans sert surtout Ã  construire artefact modÃ¨le et mapping.
Il existe donc un double paradigme:
Segmentation SQL heuristique pour API runtime.
KMeans pour entraÃ®nement explicite et persistance.

### 2.3 Algorithme K-Means

#### 2.3.1 Formulation

Fonction objectif:

$$
J = \sum_{i=1}^{k} \sum_{x \in C_i} \|x - \mu_i\|^2
$$

#### 2.3.2 ParamÃ¨tres rÃ©els

n_clusters = 4
random_state = 42
n_init = 10
algorithm = lloyd
max_iter = 300

#### 2.3.3 Code exact d'entraÃ®nement

```python
feature_matrix = np.array(
    [[float(row.get("x") or 0.0), float(row.get("y") or 0.0)] for row in segments],
    dtype=float,
)

scaler = StandardScaler()
x_scaled = scaler.fit_transform(feature_matrix)

model = KMeans(n_clusters=4, random_state=42, n_init=10)
labels = model.fit_predict(x_scaled)
```

#### 2.3.4 Choix K=4

K=4 est codÃ© en dur.
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Aucune implÃ©mentation Elbow ou Silhouette observÃ©e.

#### 2.3.5 Convergence

CritÃ¨re interne gÃ©rÃ© par implÃ©mentation sklearn.
Pas de logique custom de convergence dans le code.

### 2.4 Description des 4 Segments

#### 2.4.1 Segments rÃ©ellement prÃ©sents

Power Users
Regular Loyals
Occasional Users
Trial Only

#### 2.4.2 MÃ©canisme de construction profils

Profiling via requÃªtes SQL agrÃ©gÃ©es.
MÃ©triques profil:
ARPU moyen
jours actifs moyens
churn_rate segment

#### 2.4.3 Fiche Segment 1 â€” Power Users

Profil:
billing_count et revenue dans quantile haut.
Valeur mÃ©tier:
haut ARPU, prioritaire upsell.
Risque churn:
calculÃ© via jointure subscriptions status.
Recommandation:
pack premium multi-services.

#### 2.4.4 Fiche Segment 2 â€” Regular Loyals

Profil:
usage/rÃ©venue mÃ©dian-haut stable.
Valeur mÃ©tier:
base rÃ©currente principale.
Risque churn:
intermÃ©diaire selon pÃ©riode.
Recommandation:
fidÃ©lisation + cross-sell progressif.

#### 2.4.5 Fiche Segment 3 â€” Occasional Users

Profil:
activitÃ© sporadique et revenu faible-moyen.
Valeur mÃ©tier:
fort potentiel de conversion.
Risque churn:
plus Ã©levÃ© que loyaux.
Recommandation:
campagnes rÃ©activation hebdomadaires.

#### 2.4.6 Fiche Segment 4 â€” Trial Only

Profil:
faible ou nul billing success.
Valeur mÃ©tier:
faible instantanÃ©e mais critique pour croissance.
Risque churn:
Ã©levÃ©.
Recommandation:
onboarding renforcÃ© + offres d'activation J1/J2/J3.

#### 2.4.7 Tableau comparatif

| MÃ©trique         | Power Users                             | Regular Loyals                          | Occasionnels                            | Trial Only                              |
| ---------------- | --------------------------------------- | --------------------------------------- | --------------------------------------- | --------------------------------------- |
| ActivitÃ© moyenne | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| ARPU (TND)       | ExposÃ© via profiles API                 | ExposÃ© via profiles API                 | ExposÃ© via profiles API                 | ExposÃ© via profiles API                 |
| Lifetime (jours) | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Churn Rate       | ExposÃ© via profiles API                 | ExposÃ© via profiles API                 | ExposÃ© via profiles API                 | ExposÃ© via profiles API                 |
| % base           | ExposÃ© via distribution API             | ExposÃ© via distribution API             | ExposÃ© via distribution API             | ExposÃ© via distribution API             |

### 2.5 MÃ©thode d'Assignation des Labels

#### 2.5.1 Dans la logique SQL runtime

Labels assignÃ©s par rÃ¨gles percentiles:
haut billing + haut revenue => Power Users
mÃ©dian billing + mÃ©dian revenue => Regular Loyals
billing > 0 sinon => Occasional Users
sinon => Trial Only

#### 2.5.2 Dans la logique KMeans train

AprÃ¨s clustering, labels re-mappÃ©s par revenu moyen cluster.
Ordre low->high:
Trial Only
Occasional Users
Regular Loyals
Power Users

Code exact mapping:

```python
mean_revenue = {
    cluster: (cluster_revenue[cluster] / max(cluster_count.get(cluster, 1), 1))
    for cluster in cluster_revenue
}
ordered_clusters = [c for c, _ in sorted(mean_revenue.items(), key=lambda item: item[1])]
names_low_to_high = ["Trial Only", "Occasional Users", "Regular Loyals", "Power Users"]
rank_map = {cluster: names_low_to_high[idx] for idx, cluster in enumerate(ordered_clusters)}
```

#### 2.5.3 rank_map observÃ© dans artefact

{"1": "Trial Only", "2": "Occasional Users", "3": "Regular Loyals", "0": "Power Users"}

### 2.6 Visualisation et InterprÃ©tation

#### 2.6.1 Clustering Map

Frontend: UserSegmentationPage.jsx
Type: ScatterChart.
Axe X: Axis 1 â€” Activity / Usage Frequency.
Axe Y: Axis 2 â€” ARPU / Value.
Couleurs par segment via SEGMENT_COLORS.

#### 2.6.2 Segment Size Distribution

BarChart vertical.
Mesure: percentage segment.
Source: /analytics/segmentation/clusters distribution.

#### 2.6.3 User Distribution Pie

PieChart donut.
Affiche proportions par segment.
Note critique:
userCount hardcodÃ© Ã  1.2M dans composant.
Peut diverger du rÃ©el.

#### 2.6.4 Radar Chart comportemental

Radar data actuellement statique (hardcoded) dans la page.
Axes:
Activity
ARPU
Retention
Loyalty
Engagement

Important:
Ce radar n'est pas alimentÃ© par backend en l'Ã©tat.

### 2.7 Endpoints et IntÃ©gration

#### 2.7.1 Endpoints backend segmentation

GET /analytics/segmentation/kpis
GET /analytics/segmentation/clusters
GET /analytics/segmentation/profiles
POST /analytics/segmentation/train

#### 2.7.2 SchÃ©ma rÃ©ponses

KPIResponse:
total_segments
dominant_segment
dominant_pct
high_value_segment
arpu_premium
risk_segment
risk_churn_rate

ClustersResponse:
clusters[] {x,y,segment}
distribution[] {name,percentage,count}

ProfilesResponse:
profiles[] {segment,avg_duration,arpu,churn_rate}

TrainResponse:
status
message

#### 2.7.3 Hooks frontend

useSegmentationKPIs -> /kpis
useSegmentationClusters -> /clusters
useSegmentationProfiles -> /profiles
train action via api.post('/analytics/segmentation/train')

### 2.8 Limites et AmÃ©liorations

#### 2.8.1 Limites identifiÃ©es

K fixÃ© sans preuve quantitative dans code.
Front mixe data rÃ©elle et fallback mock.
Radar non connectÃ© donnÃ©es rÃ©elles.
Double logique segmentation SQL + KMeans pouvant diverger.

#### 2.8.2 AmÃ©liorations recommandÃ©es

Ajouter Silhouette Score et Davies-Bouldin.
Tester DBSCAN/HDBSCAN pour structures non sphÃ©riques.
Supprimer mocks frontend en production.
Exposer centres de clusters et mÃ©triques stabilitÃ© temporelle.
Versionner dataset segmentation utilisÃ© au train.

---

## PARTIE III â€” DÃ‰TECTION D'ANOMALIES

### 3.1 Contexte et Justification

#### 3.1.1 Pourquoi critique en tÃ©lÃ©com

Chute DAU soudaine peut indiquer panne accÃ¨s.
Pic churn peut rÃ©vÃ©ler incident facturation ou qualitÃ© service.
Anomalie revenu peut signaler rupture pipeline billing.

#### 3.1.2 ImplÃ©mentation observÃ©e

Module anomalies est exposÃ© via router /anomalies.
Calcul anomalies Ã  la volÃ©e sur sÃ©ries quotidiennes.
Pas de persistance table anomalies observÃ©e dans code actuel.

### 3.2 MÃ©thode : Z-Score sur FenÃªtre Glissante

#### 3.2.1 Formule utilisÃ©e

$$
z_t = \frac{x_t - \mu_{t-w:t-1}}{\sigma_{t-w:t-1}}
$$

avec $w=14$ jours selon code.

#### 3.2.2 Extrait exact dÃ©tection

```python
for metric in metrics:
    values = [float(r.get(metric, 0) or 0) for r in rows]
    for idx, value in enumerate(values):
        if idx < 14:
            continue
        window = values[idx - 14 : idx]
        mean = statistics.fmean(window)
        std = statistics.pstdev(window)
        if std <= 1e-9:
            continue
        z_score = (value - mean) / std
        sev = _severity_for_z(z_score)
```

#### 3.2.3 Seuils rÃ©els implÃ©mentÃ©s

|z| >= 4 => critical
|z| >= 3 => high
|z| >= 2 => medium

Note:
Le cahier demandait medium Ã  2.5.
Le code rÃ©el utilise 2.0.

#### 3.2.4 Mention Isolation Forest

Le texte UI et insights mentionne "Z-Score + Isolation Forest".
Aucun calcul IsolationForest observÃ© dans router anomalies.py.
Conclusion:
Isolation Forest est [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER].

### 3.3 MÃ©triques SurveillÃ©es

#### 3.3.1 Liste rÃ©elle

metrics = (dau, churn_rate, revenue, renewals)

#### 3.3.2 Tableau source/agrÃ©gation

| MÃ©trique   | Source SQL                           | AgrÃ©gation                    | Seuil critique |
| ---------- | ------------------------------------ | ----------------------------- | -------------- | --- | ------------ |
| DAU        | user_activities                      | COUNT DISTINCT user_id / jour |                | z   | >=4 critical |
| Churn Rate | unsubscriptions + active_base        | COUNT churn / actifs \*100    |                | z   | >=4 critical |
| Revenue    | billing_events + service_types.price | SUM(price) success / jour     |                | z   | >=4 critical |
| Renewals   | billing_events                       | COUNT success / jour          |                | z   | >=4 critical |

#### 3.3.3 RequÃªte quotidienne exacte (extrait)

```sql
WITH days AS (
    SELECT gs::date AS day
    FROM generate_series(CAST(:start_dt AS date), CAST(:end_dt AS date), interval '1 day') gs
),
dau_daily AS (
    SELECT DATE(ua.activity_datetime) AS day, COUNT(DISTINCT ua.user_id) AS dau
    FROM user_activities ua
    WHERE ua.activity_datetime >= CAST(:start_dt AS timestamp)
      AND ua.activity_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
    GROUP BY 1
),
churn_daily AS (
    SELECT DATE(u.unsubscription_datetime) AS day, COUNT(*) AS churn_count
    FROM unsubscriptions u
    WHERE u.unsubscription_datetime >= CAST(:start_dt AS timestamp)
      AND u.unsubscription_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
    GROUP BY 1
),
renewals_daily AS (
    SELECT DATE(be.event_datetime) AS day, COUNT(*) AS renewals
    FROM billing_events be
    WHERE be.event_datetime >= CAST(:start_dt AS timestamp)
      AND be.event_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
      AND LOWER(be.status) = 'success'
    GROUP BY 1
),
revenue_daily AS (
    SELECT DATE(be.event_datetime) AS day, COALESCE(SUM(st.price), 0) AS revenue
    FROM billing_events be
    JOIN services srv ON srv.id = be.service_id
    JOIN service_types st ON st.id = srv.service_type_id
    WHERE be.event_datetime >= CAST(:start_dt AS timestamp)
      AND be.event_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
      AND LOWER(be.status) = 'success'
    GROUP BY 1
)
```

### 3.4 Pipeline de DÃ©tection

#### 3.4.1 FrÃ©quence d'exÃ©cution

Pas de scheduler explicite dans code router.
DÃ©tection dÃ©clenchÃ©e:
au chargement endpoints
ou via POST /anomalies/run-detection

#### 3.4.2 FenÃªtrage temporel

RÃ©solution des dates via resolve_date_range(source='billing').
Cap de sÃ©curitÃ© MAX_ANOMALY_RANGE_DAYS = 120.

#### 3.4.3 Niveaux de sÃ©vÃ©ritÃ©

critical/high/medium selon z-score absolu.
Direction dÃ©rivÃ©e:
spike si z_score > 0
drop sinon.

#### 3.4.4 Persistance anomalies

Table anomalies persistÃ©e:
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Le code gÃ©nÃ¨re IDs uuid temporaires en mÃ©moire par appel.

### 3.5 SchÃ©ma de Table Anomalies

#### 3.5.1 SchÃ©ma demandÃ© dans prompt

Le schÃ©ma CREATE TABLE fourni par le cahier n'est pas observÃ© dans les migrations auditÃ©es.
Aucun modÃ¨le SQLAlchemy anomalies n'a Ã©tÃ© trouvÃ©.

#### 3.5.2 Position acadÃ©mique

Inclure ce schÃ©ma comme cible d'industrialisation.
Le marquer "non implÃ©mentÃ©" dans code actuel.

#### 3.5.3 SchÃ©ma cible proposÃ©

```sql
CREATE TABLE anomalies (
    id              UUID PRIMARY KEY,
    detected_at     DATE NOT NULL,
    service_id      UUID REFERENCES services(id),
    metric          VARCHAR(50),
    observed_value  NUMERIC(12,4),
    expected_value  NUMERIC(12,4),
    z_score         NUMERIC(8,4),
    severity        VARCHAR(20),
    direction       VARCHAR(10),
    status          VARCHAR(20) DEFAULT 'open',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

Index cibles:

```sql
CREATE INDEX idx_anomalies_severity_date
    ON anomalies (severity, detected_at DESC);
CREATE INDEX idx_anomalies_service_metric
    ON anomalies (service_id, metric, detected_at DESC);
```

### 3.6 Endpoints et Visualisation

#### 3.6.1 Endpoints rÃ©els exposÃ©s

GET /anomalies/summary
GET /anomalies/timeline
GET /anomalies/distribution
GET /anomalies/heatmap
GET /anomalies/details
GET /anomalies/insights
POST /anomalies/run-detection

#### 3.6.2 Ã‰cart avec endpoints demandÃ©s

Le prompt mentionne /analytics/anomalies.
ImplÃ©mentation rÃ©elle utilise prÃ©fixe /anomalies.
Endpoint POST /analytics/anomalies/{id}/status:
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]

#### 3.6.3 Visualisations frontend anomalies

Timeline multi-mÃ©triques + points anomalies.
Heatmap services x semaines.
Pie distribution sÃ©vÃ©ritÃ©.
Bars anomalies par mÃ©trique.
Table dÃ©tails paginÃ©e.
Cartes insights textuelles.

#### 3.6.4 SchÃ©mas de rÃ©ponse observÃ©s

summary:
anomalies_detected
critical_alerts
unresolved
most_affected_service
last_detection
trend_vs_previous

timeline:
series[] {metric,points[]}
anomalies[] {date,metric,severity,z_score,observed_value,expected_value,service_name}

details:
items[] + total + limit + offset

### 3.7 Limites et Alternatives

#### 3.7.1 Limites du Z-score

HypothÃ¨se implicite de stationnaritÃ© locale.
SensibilitÃ© aux fenÃªtres courtes et petits Ã©chantillons.
Faux positifs en prÃ©sence de saisonnalitÃ© non modÃ©lisÃ©e.

#### 3.7.2 Alternatives robustes

IQR par mÃ©trique et service.
Median Absolute Deviation.
Prophet residual anomaly detection.
Isolation Forest multivariÃ© rÃ©el.

#### 3.7.3 Limite volumÃ©trique

FenÃªtre de donnÃ©es courte (2 mois) restreint robustesse temporelle.
Avec w=14, seulement ~46 points activement exploitables sur 60 jours.

---

## PARTIE IV â€” COMPARAISON ET SYNTHÃˆSE

### 4.1 Tableau Comparatif des 3 Modules IA

| CritÃ¨re          | PrÃ©diction Churn                        | Segmentation K-Means                   | DÃ©tection Anomalies                  |
| ---------------- | --------------------------------------- | -------------------------------------- | ------------------------------------ |
| Type d'IA        | SupervisÃ©                               | Non supervisÃ© + heuristique SQL        | Statistique                          |
| Algorithme       | LogisticRegression                      | KMeans (n=4)                           | Z-Score rolling                      |
| DonnÃ©es d'entrÃ©e | Features abonnement/comportement        | x,y dÃ©rivÃ©s billing+revenue            | SÃ©ries journaliÃ¨res KPI              |
| Sortie           | ProbabilitÃ© [0,1] + catÃ©gorie           | Segment + distribution                 | z_score + sÃ©vÃ©ritÃ© + direction       |
| FrÃ©quence        | A la demande                            | A la demande + train manuel            | A la demande + run endpoint          |
| Latence endpoint | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | logs prÃ©cÃ©dents: ~1.6s Ã  2.4s observÃ©s | dÃ©pend plage, optimisÃ©e avec bornage |
| ComplexitÃ©       | Moyenne                                 | Moyenne                                | Faible Ã  moyenne                     |
| ExplicabilitÃ©    | Bonne (coefficients)                    | Moyenne                                | TrÃ¨s haute                           |
| Valeur mÃ©tier    | TrÃ¨s haute                              | Haute                                  | Haute                                |

### 4.2 Architecture IA Globale

#### 4.2.1 Flux macro

prod_db (source prod lecture seule)
-> ETL / ingestion analytics_db
-> scripts features/retention
-> modÃ¨les ML joblib
-> endpoints FastAPI
-> visualisation React

#### 4.2.2 Routage backend observÃ© (main.py)

Routers inclus total observÃ© > 14.
Inclut ml_churn, segmentation, anomalies explicitement.
Middleware latency_logger centralise timing requÃªtes.

#### 4.2.3 Nombre de hooks frontend

Hooks recensÃ©s dans src/hooks: 33 fichiers.
Observation:
la mention "28 hooks" dans prompt n'est plus Ã  jour selon arborescence actuelle.

### 4.3 InterdÃ©pendances entre Modules

#### 4.3.1 Segmentation -> Churn

InterdÃ©pendance directe feature-level:
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Aucune feature churn ne consomme explicitement label segment.

#### 4.3.2 Anomalies -> Retraining

DÃ©clenchement automatique retrain churn/segmentation par anomalies:
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Aucun orchestrateur de ce type dans les routeurs auditÃ©s.

#### 4.3.3 Churn -> Segments Ã  risque

Consommation score churn dans segmentation:
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]
Les deux modules restent dÃ©couplÃ©s techniquement.

### 4.4 Performance Globale du SystÃ¨me IA

#### 4.4.1 Tableau latences

| Endpoint IA                      |                         Latence mesurÃ©e |    Cible | Statut                                  |
| -------------------------------- | --------------------------------------: | -------: | --------------------------------------- |
| /ml/churn/scores                 | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] | < 2000ms | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| /ml/churn/metrics                | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |  < 500ms | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| /analytics/segmentation/kpis     |        1711ms (valeur fournie contexte) | < 1000ms | âš ï¸                                      |
| /analytics/segmentation/clusters |        1658ms (valeur fournie contexte) | < 1000ms | âš ï¸                                      |
| /analytics/segmentation/profiles |        2427ms (valeur fournie contexte) | < 1000ms | âŒ                                      |

#### 4.4.2 Analyse performance

Segmentation est le module le plus coÃ»teux en agrÃ©gations SQL.
Anomalies a nÃ©cessitÃ© bornage plage + retry timeout.
Churn nÃ©cessite potentiellement indexation fine sur activitÃ©s et events temporels.

---

## PARTIE V â€” CONCLUSIONS ET PERSPECTIVES

### 5.1 Bilan des Objectifs IA

#### 5.1.1 Statut par objectif

[x] PrÃ©diction churn: implÃ©mentÃ©e, entraÃ®nement et scoring opÃ©rationnels.
[x] Segmentation utilisateurs: opÃ©rationnelle, KMeans sÃ©rialisÃ©.
[x] DÃ©tection anomalies: opÃ©rationnelle via z-score API.
[ ] Optimisation campagnes pilotÃ©e ML: [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER].

#### 5.1.2 MaturitÃ© globale

Prototype avancÃ© orientÃ© production interne.
Niveau correct pour dÃ©monstration PFE.
NÃ©cessite consolidation MLOps/monitoring pour mise Ã  l'Ã©chelle.

### 5.2 Valeur MÃ©tier QuantifiÃ©e

| Module              | BÃ©nÃ©fice estimÃ©                                        | MÃ©thode de calcul                                                  |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------------------ |
| PrÃ©diction churn    | RÃ©duction churn potentielle via intervention priorisÃ©e | Simuler scÃ©nario: % churners dÃ©tectÃ©s x taux de rÃ©tention campagne |
| Segmentation        | Hausse ARPU ciblÃ©e                                     | Comparer campagnes segmentÃ©es vs mass mailing                      |
| DÃ©tection anomalies | RÃ©duction temps dÃ©tection incident                     | Mesurer MTTD manuel vs automatique                                 |

Remarque:
Valeurs numÃ©riques finales de ROI ne sont pas codÃ©es.
[NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER]

### 5.3 Roadmap IA Post-PFE

#### PrioritÃ© 1 â€” 1 Ã  3 mois

ImplÃ©menter SHAP global/local churn.
Automatiser retrain mensuel avec snapshot data.
Ajouter silhoutte et monitoring drift clusters.
Supprimer fallback mock dans UserSegmentationPage.

#### PrioritÃ© 2 â€” 3 Ã  6 mois

Benchmarker XGBoost/LightGBM pour churn.
Ajouter Isolation Forest rÃ©el cÃ´tÃ© anomalies.
Ajouter calibration probabiliste + Brier score.
Industrialiser table anomalies persistÃ©e + workflows statut.

#### PrioritÃ© 3 â€” 6 Ã  12 mois

MLOps complet: versioning modÃ¨les/donnÃ©es/features.
Feature store lÃ©ger pour cohÃ©rence training/serving.
A/B testing systÃ©matique des campagnes basÃ©es IA.
ModÃ¨le LTV pour arbitrage budget rÃ©tention.

### 5.4 RÃ©fÃ©rences AcadÃ©miques

Breiman, L. (2001). Random Forests. Machine Learning.
MacQueen, J. (1967). Some Methods for Classification and Analysis of Multivariate Observations.
Hawkins, D.M. (1980). Identification of Outliers.
Provost, F. & Fawcett, T. (2013). Data Science for Business.

---

## ANNEXE A â€” Inventaire technique dÃ©taillÃ©

### A.1 ModÃ¨le Subscription (attributs clÃ©s)

id UUID PK
user_id FK users
service_id FK services
campaign_id FK campaigns nullable
subscription_start_date timestamptz
subscription_end_date timestamptz nullable
status string(20)
created_at

Indexes observÃ©s:
ix_subscriptions_user_id
ix_subscriptions_service_id
ix_subscriptions_status
ix_subscriptions_start_date
ix_subscriptions_campaign_id
idx_user_service

### A.2 ModÃ¨le UserActivity

id UUID
user_id FK
service_id FK
activity_datetime
activity_type
session_id nullable

Indexes:
idx_user_activity_time
ix_user_activities_datetime
ix_user_activities_type

### A.3 ModÃ¨le BillingEvent

id
subscription_id
user_id
service_id
event_datetime
status
failure_reason
retry_count
is_first_charge

Indexes:
ix_billing_events_subscription_id
ix_billing_events_user_id
ix_billing_events_event_datetime
ix_billing_events_status
ix_billing_events_is_first_charge
ix_billing_events_service_id

### A.4 ModÃ¨le Unsubscription

id
subscription_id unique
user_id
service_id
unsubscription_datetime
churn_type
churn_reason
days_since_subscription
last_billing_event_id

### A.5 ModÃ¨le Cohort

id
cohort_date
service_id
total_users
retention_d7
retention_d14
retention_d30
calculated_at

Contrainte unique:
(cohort_date, service_id)

---

## ANNEXE B â€” ETL Cohortes

### B.1 Objectif script compute_cohorts.py

Calculer et upserter la table cohorts.
Mesurer retention D7 D14 D30.
Adapter automatiquement selon type de colonne date/time.

### B.2 Ã‰tapes du script

Ã‰tape 0:
Diagnostic statuts disponibles dans subscriptions.

Ã‰tape 1:
VÃ©rification volume source et plage dates.

Ã‰tape 2:
Construction first_sub (premier abonnement user+service).

Ã‰tape 3:
Calcul retention par EXISTS sur jalons 7/14/30 jours.

Ã‰tape 4:
INSERT INTO cohorts ON CONFLICT UPDATE.

Ã‰tape 5:
VÃ©rification finale table cohorts.

### B.3 Extrait SQL upsert

```sql
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

### B.4 Point performance

Le script force SET LOCAL statement_timeout = 0.
Cela Ã©vite interruption sur scans historiques lourds.
NÃ©cessite surveillance pour usage contrÃ´lÃ© en production.

---

## ANNEXE C â€” API Churn dÃ©taillÃ©e

### C.1 POST /ml/churn/train

But:
lancer entraÃ®nement modÃ¨le logistic.
SÃ©curitÃ©:
require_admin.
Sortie:
mÃ©triques complÃ¨tes.

### C.2 GET /ml/churn/metrics

But:
charger mÃ©triques sauvegardÃ©es.
Erreur 404 si modÃ¨le non entraÃ®nÃ©.

### C.3 GET /ml/churn/scores

Params:
top (1..200)
threshold (0..1)
store bool

Sortie:
distribution risques
top users au-dessus threshold
active_users_scored

### C.4 Transformation user-level

Le dataframe est d'abord subscription-level.
Puis groupby user_id et conservation max churn_risk par user.

---

## ANNEXE D â€” API Segmentation dÃ©taillÃ©e

### D.1 GET /analytics/segmentation/kpis

KPI business segmentaires.
RÃ©ponse typÃ©e KPIResponse.

### D.2 GET /analytics/segmentation/clusters

Retourne points x/y pour scatter map.
Inclut distribution segments.
Sampling max 3000 points cÃ´tÃ© service pour performance.

### D.3 GET /analytics/segmentation/profiles

Retourne profils segment (duration, arpu, churn_rate).

### D.4 POST /analytics/segmentation/train

EntraÃ®ne KMeans sur features x/y standardisÃ©es.
Sauvegarde dictionnaire joblib avec model+scaler+rank_map+window.

---

## ANNEXE E â€” API Anomalies dÃ©taillÃ©e

### E.1 GET /anomalies/summary

KPI synthÃ¨se anomalies.
Inclut tendance pÃ©riode prÃ©cÃ©dente.

### E.2 GET /anomalies/timeline

SÃ©ries temporelles + anomalies annotÃ©es.

### E.3 GET /anomalies/distribution

Comptages par sÃ©vÃ©ritÃ© et mÃ©trique.

### E.4 GET /anomalies/heatmap

Matrice service x semaine.
Niveau severity_score dÃ©rivÃ© count.

### E.5 GET /anomalies/details

Pagination limit/offset.
DonnÃ©es tabulaires opÃ©rationnelles.

### E.6 GET /anomalies/insights

Cartes textuelles recommandation.

### E.7 POST /anomalies/run-detection

DÃ©clenche run logique et renvoie compteurs.

---

## ANNEXE F â€” Extraits Frontend IA

### F.1 Churn dashboard

Actions:
Train model
Refresh
RÃ©glage threshold
RÃ©glage top N

Visuals:
BarChart distribution risque
Table coefficients
Table top users

### F.2 Segmentation dashboard

KPI cards
Scatter map
Bar segment size
Pie user distribution
Radar (hardcoded)
Table profils
Insights (hardcoded)

### F.3 Anomaly dashboard

KPI cards synthÃ¨se
Timeline line+scatter
Heatmap table
Pie severity
Metric bars
Table anomalies paginÃ©e
Insights cards

---

## ANNEXE G â€” IncohÃ©rences et dette technique

### G.1 IncohÃ©rence dÃ©finition churn

Doc dit subscription_end_date non null.
Code utilise status cancelled/expired.
Action:
aligner documentation et code de rÃ©fÃ©rence.

### G.2 IncohÃ©rence segmentation runtime vs training

Runtime SQL segmente dÃ©jÃ  via rÃ¨gles.
KMeans entraÃ®nÃ© mais non utilisÃ© pour infÃ©rence API live.
Action:
clarifier architecture cible.

### G.3 IncohÃ©rence anomalies Isolation Forest

UI indique combinaison Z-Score + Isolation Forest.
Code calcule uniquement Z-score rolling.
Action:
implÃ©menter IsolationForest ou corriger wording.

### G.4 Frontend mocks restants

UserSegmentationPage conserve generateMock\* et insights statiques.
Action:
neutraliser mocks en mode production.

### G.5 Endpoint statut anomalies absent

POST /analytics/anomalies/{id}/status non trouvÃ©.
Action:
ajouter persistance anomalies + workflow statut.

---

## ANNEXE H â€” Recommandations SQL et performance

### H.1 Indexation churn training

Index composite recommandÃ©:
(user_id, service_id, activity_datetime) sur user_activities dÃ©jÃ  partiellement prÃ©sent.
(subscription_id, event_datetime, status) sur billing_events Ã  vÃ©rifier.

### H.2 FenÃªtrage temporel

Bonnes pratiques observÃ©es:
resolve_date_range
get_data_bounds
bornage anomalies MAX_ANOMALY_RANGE_DAYS

### H.3 RÃ©duction scans lourds

PrÃ©-agrÃ©gation journaliÃ¨re possible:
materialized views KPI quotidiens.

### H.4 Monitoring latence

middleware latency_logger existe.
Action:
persist logs latence endpoint + percentile P95/P99.

---

## ANNEXE I â€” Feuille de route MLOps

### I.1 Gouvernance modÃ¨le

Version modÃ¨le
Version features
Version dataset
Version mÃ©triques

### I.2 ObservabilitÃ©

Data drift
Concept drift
Performance drift
Alerting automatique

### I.3 Pipeline CI/CD ML

Validation dataset
Unit tests feature SQL
Training pipeline reproductible
Model registry
Canary release scoring

### I.4 SÃ©curitÃ© et conformitÃ©

TraÃ§abilitÃ© dÃ©cision IA
Minimisation donnÃ©es personnelles
ContrÃ´le accÃ¨s endpoints train
Audit trail infÃ©rence

---

## ANNEXE J â€” VÃ©rification artefacts joblib

### J.1 churn_model.joblib

Type rÃ©el: sklearn.linear_model.\_logistic.LogisticRegression
ParamÃ¨tres clÃ©s:
class_weight=balanced
max_iter=2000
random_state=42
solver=lbfgs
C=1.0

### J.2 churn_metrics.joblib

Type rÃ©el: dict
ClÃ©s:
trained_at
roc_auc
accuracy
churn_rate
report
coefficients
n_samples
n_positive
n_negative
warning

### J.3 segmentation_kmeans.joblib

Type rÃ©el: dict
Contenu:
model (KMeans)
scaler (StandardScaler)
rank_map
trained_at
window

---

## ANNEXE K â€” Exigences du prompt vs Ã©tat rÃ©el

### K.1 Exigence: reproduire SQL churn exact

Statut: fait dans ce rapport.

### K.2 Exigence: dÃ©crire .joblib

Statut: fait via inspection rÃ©elle.

### K.3 Exigence: endpoints churn

Statut: fait.

### K.4 Exigence: endpoints segmentation

Statut: fait.

### K.5 Exigence: endpoints anomalies demandÃ©s /analytics/anomalies

Statut: partiel.
Ã‰tat rÃ©el: routes sous /anomalies.

### K.6 Exigence: table anomalies persistÃ©e

Statut: non trouvÃ©.

### K.7 Exigence: minimum 800 lignes

Statut: visÃ© dans ce document.

---

## ANNEXE L â€” Tableau de conformitÃ© [NON TROUVÃ‰] par section

| Rubrique                                | Ã‰tat                                    |
| --------------------------------------- | --------------------------------------- |
| CoÃ»t acquisition client chiffrÃ©         | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Matrice confusion brute TP/TN/FP/FN     | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Validation croisÃ©e churn                | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Endpoint /analytics/churn/curve         | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Endpoint /analytics/churn/time-to-churn | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Endpoint /analytics/churn/reasons       | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Endpoint /analytics/churn/risk-segments | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Elbow method segmentation               | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Silhouette score segmentation           | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Isolation Forest effectif               | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Table anomalies SQLAlchemy/migration    | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Endpoint statut anomalies               | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Latence /ml/churn/scores mesurÃ©e        | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |
| Latence /ml/churn/metrics mesurÃ©e       | [NON TROUVÃ‰ DANS LE CODE â€” Ã€ COMPLÃ‰TER] |

---

## ANNEXE M â€” Conclusion acadÃ©mique concise

Le systÃ¨me IA est rÃ©el, dÃ©ployable et dÃ©jÃ  intÃ©grÃ© UX/API.
Le module churn est le plus avancÃ© en cycle complet data->model->API->UI.
Le module segmentation fonctionne mais souffre d'ambiguÃ¯tÃ© entre logique SQL et KMeans.
Le module anomalies est utile et opÃ©rationnel, mais reste statistique simple sans persistance native.
Pour une soutenance PFE, la profondeur technique est solide.
Pour une industrialisation entreprise, la prioritÃ© est la rigueur MLOps et la rÃ©duction des Ã©carts de spÃ©cification.

Fin du rapport.

