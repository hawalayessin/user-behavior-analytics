# Rapport Technique — Modules d'Intelligence Artificielle

## Plateforme d'Analytics Comportementale — PFE 2025/2026

---

## 0. Cadre du rapport

### 0.1 Objet

Ce document analyse les composants IA/ML implémentés dans le code source de la plateforme.
Le rapport est basé sur lecture effective des fichiers backend, frontend, scripts ETL et artefacts modèles.
Le but est de fournir un support académique pour soutenance PFE.

### 0.2 Périmètre audité

Périmètre backend Python/FastAPI/SQLAlchemy.
Périmètre frontend React hooks + pages IA.
Périmètre modèles sérialisés joblib.
Périmètre ETL cohortes et logique churn.
Périmètre détection d'anomalies côté API.

### 0.3 Sources auditées explicitement

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

### 0.4 Contexte métier rappelé

Secteur: télécommunications numériques tunisiennes.
Services suivis: ElJournal, Esports.tn, ttoons, Tawer.
Funnel: essai 3 jours puis renouvellement automatique.
Canaux dominants: SMS/USSD.
Fenêtre de données annoncée: septembre-octobre 2025.
Volume annoncé: 228 707 transactions.

### 0.5 Méthodologie d'analyse

Lecture statique du code source.
Extraction de SQL exact des sections critiques.
Inspection des objets joblib via Python.
Croisement backend/frontend/schémas.
Signalement explicite des écarts entre spécification attendue et implémentation réelle.

### 0.6 Règle de traçabilité

Toute information non trouvée dans le code est marquée ainsi:
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]

---

## Résumé Exécutif (1 page)

### RE.1 Objectif des modules IA

Le projet implémente trois briques IA/analytique avancée orientées décision opérationnelle.
Brique 1: prédiction du churn supervisée pour prioriser la rétention.
Brique 2: segmentation comportementale de type clustering pour personnaliser les campagnes.
Brique 3: détection d'anomalies temporelles pour alerter sur incidents business.

### RE.2 Les 3 modules implémentés et rôle métier

Module Churn IA:
Sortie: score de risque de churn par abonnement actif.
Usage: priorisation CRM, actions anti-churn, listes top risque.

Module Segmentation K-Means:
Sortie: cluster utilisateur et distribution des segments.
Usage: ciblage marketing différencié et analyse de valeur par segment.

Module Détection d'anomalies:
Sortie: événements anormaux par métrique/jour/sévérité.
Usage: monitoring business et diagnostic rapide churn/revenus/activité.

### RE.3 Résultats clés observés (extraits réels)

Le modèle churn sérialisé est une LogisticRegression scikit-learn.
Métriques extraites de churn_metrics.joblib:
Accuracy = 0.6594546191075198
ROC-AUC = 0.8201320134904057
Taux de churn entraînement = 0.9631460674157304
n_samples = 1 172 575
n_positive = 1 129 361
n_negative = 43 214

Le modèle segmentation sérialisé est un KMeans avec n_clusters=4.
Fenêtre de training segmentation stockée:
start_date = 2025-09-25T12:00:42.275986
end_date = 2025-10-25T12:00:42.275986
service_id = null

### RE.4 Valeur ajoutée business

Passage d'une lecture descriptive à une orchestration prescriptive.
Le churn module permet d'anticiper les départs plutôt que de les constater.
La segmentation facilite le design de campagnes SMS à ROI différencié.
L'anomaly engine réduit le délai de détection des incidents invisibles sans surveillance statistique.

### RE.5 Points forts techniques

Architecture API claire par routeurs spécialisés.
Feature engineering churn riche et ancré SQL.
Persistance joblib des modèles.
Intégration frontend opérationnelle pour churn et anomalies.
Couches de cache TTL pour réduire la latence sur segmentation/churn dashboards.

### RE.6 Risques critiques identifiés

Déséquilibre extrême des classes churn dans les métriques sauvegardées.
Ambiguïté entre définition métier du churn et label réel codé.
Segmentation frontend contient encore des fallbacks mock.
Détection anomalies mentionne Isolation Forest en texte mais non implémentée algorithmiquement.
Incohérences entre endpoints demandés dans cahier et endpoints réellement exposés.

---

## PARTIE I — PRÉDICTION DU CHURN

### 1.1 Contexte et Justification Métier

#### 1.1.1 Pourquoi le churn est critique ici

Le modèle abonnement SMS/USSD repose sur récurrence de facturation.
Une perte d'abonné diminue immédiatement revenu récurrent.
La fenêtre d'intervention est courte à cause du cycle essai puis renouvellement.
Les churn techniques peuvent signaler un incident système impactant en masse.

#### 1.1.2 Alignement avec le code

Le code calcule des variables orientées comportement récent.
Les features activité 7j/30j servent à détecter essoufflement usage.
Les features billing capturent friction de paiement et parcours premier charge.
Le marqueur trial churn cible la phase la plus fragile du funnel.

#### 1.1.3 Exemple concret issu des métriques sauvegardées

Churn rate entraînement observé = 96.31%.
Ce niveau est anormalement élevé pour un dataset non biaisé.
Interprétation possible:
Fenêtre d'apprentissage orientée historiques abonnements clôturés.
Ou définition de label favorisant classes positives.
Ou fuite de structure des données sources.

#### 1.1.4 Coût abonné perdu vs acquisition

[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Le code ne contient pas de modèle financier CAC/LTV explicite.
Aucun coût unitaire acquisition n'est paramétré.
Aucun calcul direct perte/retour d'investissement anti-churn n'est implémenté.

#### 1.1.5 Fenêtre d'intervention

Le scoring est réalisé sur abonnements actifs/trial.
Le threshold par défaut pour classification binaire est 0.4.
La catégorie risque est Low/Medium/High.
L'endpoint /ml/churn/scores fournit top users priorisables immédiatement.

### 1.2 Définition de la Variable Cible

#### 1.2.1 Définition effective dans le code

La variable churned n'est pas définie par subscription_end_date IS NOT NULL.
La définition effective est basée sur status.
Règle codée:
status in ('cancelled','expired') => churned=1
sinon churned=0

Code SQL exact extrait de churn_predictor.py:

```sql
CASE
  WHEN LOWER(COALESCE(s.status, '')) IN ('cancelled', 'expired') THEN 1
  ELSE 0
END AS churned
```

#### 1.2.2 Écart avec documentation existante

docs/ml_churn_report.md mentionne:
churned = 1 if subscription_end_date IS NOT NULL
Cela n'est pas strictement conforme au code source actuel.
Conclusion académique:
La vérité de référence technique est la requête dans churn_predictor.py.

#### 1.2.3 Requête SQL de base (extrait exact)

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

#### 1.2.4 Pourquoi subscription_end_date IS NOT NULL n'est pas utilisé directement

Le système peut contenir incohérences sur dates de fin selon source.
Le status est ici choisi comme signal principal de churn logique.
Cette décision est cohérente avec commentaire dans classe ChurnPredictor.

#### 1.2.5 Différence churn trial vs churn payant

La feature is_trial_churn représente churn pendant période essai.
Règle:
unsubscription_datetime présent
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

#### 1.3.1 Liste exhaustive des features utilisées

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

| Feature                   | Type      | Description                      | Formule/Source                                    | Justification métier                 |
| ------------------------- | --------- | -------------------------------- | ------------------------------------------------- | ------------------------------------ |
| days_since_last_activity  | Numérique | Âge de dernière activité         | ref_time - MAX(user_activities.activity_datetime) | Mesure désengagement                 |
| nb_activities_7d          | Numérique | Activité courte période          | COUNT activités 7 jours                           | Signal précoce attrition             |
| nb_activities_30d         | Numérique | Activité mensuelle               | COUNT activités 30 jours                          | Stabilité usage                      |
| billing_failures_30d      | Numérique | Echecs de facturation            | COUNT billing_events FAILED sur 30 jours          | Friction paiement et churn technique |
| days_since_first_charge   | Numérique | Ancienneté depuis 1er succès     | ref_time - MIN(first successful first_charge)     | Maturité client                      |
| is_trial_churn            | Binaire   | Churn pendant essai              | days_since_subscription <= trial_duration_days    | Fragilité période d'essai            |
| avg_retention_d7          | Numérique | Rétention de cohorte du service  | cohorts.retention_d7                              | Qualité structurelle du service      |
| service_billing_frequency | Numérique | Fréquence de facturation service | service_types.billing_frequency_days              | Impact cadence billing               |
| days_to_first_unsub       | Numérique | Temps au churn                   | calcul depuis unsubscriptions sinon 999           | Intensité risque historique          |

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

Usage systématique de COALESCE.
Valeurs sentinelles observées:
999 pour délais non définis.
0 pour compteurs absents.

#### 1.3.5 Traitement des valeurs infinies et NaN

Côté Python:
X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
Cette étape protège l'entraînement.

#### 1.3.6 Analyse de corrélation attendue (théorique)

nb_activities_30d élevé devrait réduire churn.
billing_failures_30d élevé devrait augmenter churn.
days_since_last_activity élevé devrait augmenter churn.
Attention:
Le signe des coefficients dépend du codage final du dataset.

#### 1.3.7 Coefficients réels extraits

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
Le signe positif de nb_activities_30d est contre-intuitif métier.
Cela suggère un effet de confusion lié au dataset ou au label.

### 1.4 Algorithme de Machine Learning

#### 1.4.1 Identification précise de l'algorithme

Import explicite observé:
from sklearn.linear_model import LogisticRegression
Objet sérialisé churn_model.joblib:
model_type = LogisticRegression
module = sklearn.linear_model.\_logistic

#### 1.4.2 Hyperparamètres observés

class_weight = balanced
random_state = 42
max_iter = 2000
solver = lbfgs
C = 1.0
penalty (get_params) = deprecated

#### 1.4.3 Pourquoi cet algorithme est plausible ici

Simple et robuste sur features tabulaires.
Rapide à entraîner.
Probabilités directement disponibles.
Explicabilité via coefficients.

#### 1.4.4 Limites de la Logistic Regression dans ce cas

Linéarité log-odds potentiellement insuffisante pour comportement non linéaire.
Sensibilité au déséquilibre et calibration.
Dépendance forte à la qualité de feature engineering.

#### 1.4.5 Formule mathématique

Le score probabiliste est:

$$
P(\text{churn}=1\mid X)=\sigma\left(\beta_0+\sum_{i=1}^{n}\beta_i x_i\right)
=\frac{1}{1+e^{-\left(\beta_0+\sum_{i=1}^{n}\beta_i x_i\right)}}
$$

où $n=9$ features dans le code actuel.

### 1.5 Pipeline d'Entraînement

#### 1.5.1 Code d'entraînement exact (extrait)

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

#### 1.5.2 Préparation des données

Dataset SQL au niveau abonnement.
Sélection des 9 features.
Remplacement infinis/NaN.
Cible castée en int.

#### 1.5.3 Split train/test

Ratio test = 20%.
Random state = 42.
Stratification activée si au moins 2 classes.

#### 1.5.4 Validation croisée

[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Aucune cross-validation k-fold observée dans churn_predictor.py.

#### 1.5.5 Sauvegarde modèle

churn_model.joblib pour l'estimateur.
churn_metrics.joblib pour métriques et coefficients.

### 1.6 Métriques de Performance

#### 1.6.1 Tableau synthèse métriques réelles

| Métrique             |             Valeur | Interprétation                               |
| -------------------- | -----------------: | -------------------------------------------- |
| Accuracy             | 0.6594546191075198 | 65.95% de prédictions correctes globales     |
| Precision (classe 1) |    0.9960185078237 | Très peu de faux positifs pour churn positif |
| Recall (classe 1)    | 0.6490180279096125 | 64.90% des churns positifs détectés          |
| F1 (classe 1)        | 0.7859204992320126 | Compromis precision/recall classe positive   |
| AUC-ROC              | 0.8201320134904057 | Bonne séparation probabiliste globale        |
| Churn rate train     | 0.9631460674157304 | Dataset extrêmement déséquilibré             |

#### 1.6.2 Détail classification_report

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

#### 1.6.3 Pourquoi recall > precision peut être prioritaire métier

Dans anti-churn, manquer un churner coûte revenu futur.
Faux négatif = perte client non traitée.
Faux positif = coût campagne inutile mais souvent inférieur à perte d'abonnement.

#### 1.6.4 Matrice de confusion

[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
La matrice n'est pas persistée dans churn_metrics.joblib actuel.

#### 1.6.5 Analyse d'erreurs

Risque majeur identifié:
Très faible precision classe 0.
Cela indique difficulté du modèle à reconnaître non-churn dans contexte très déséquilibré.
Impact:
Le modèle peut sur-qualifier churn selon perspective de classe minoritaire.

### 1.7 Inférence et Scoring en Production

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

#### 1.7.2 Catégories de risque

Low si churn_risk < 0.3
Medium si 0.3 <= churn_risk < 0.6
High si >= 0.6

#### 1.7.3 Endpoints FastAPI churn

POST /ml/churn/train
GET /ml/churn/metrics
GET /ml/churn/scores

#### 1.7.4 Schéma réponse train

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

#### 1.7.5 Schéma réponse scores

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

### 1.8 Intégration Frontend

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
Refresh simultané metrics+scores après entraînement.

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

#### 1.8.5 Niveau de maturité UX

Gestion loading, erreurs, retry présents.
Options topN et threshold éditables.
Affichage catégories colorées Low/Medium/High.
Pas d'explicabilité locale type SHAP dans UI.

### 1.9 Limites et Améliorations Futures

#### 1.9.1 Limites actuelles

Déséquilibre classes très fort.
Absence de calibration probabiliste explicite.
Pas de monitoring drift implémenté.
Pas de validation temporelle walk-forward.

#### 1.9.2 Risque de leakage

Le code tente de limiter leakage via ref_time = subscription_end_date pour churned.
C'est une bonne pratique partielle.
Reste un risque selon disponibilité temporelle de certaines tables agrégées.

#### 1.9.3 Drift temporel

Fenêtre production observée 2025-09 à 2025-10.
Applicabilité hors fenêtre non garantie.

#### 1.9.4 Recommandations concrètes

Ajouter split temporel train/validation/test.
Tester XGBoost/LightGBM en benchmark.
Ajouter calibration Platt/Isotonic.
Ajouter SHAP global + local.
Automatiser réentraînement mensuel.
Versionner modèle + métriques + data slice.

---

## PARTIE II — SEGMENTATION UTILISATEURS (K-MEANS)

### 2.1 Contexte et Objectif Métier

#### 2.1.1 Besoin métier

Tous les abonnés n'ont pas la même valeur.
Les campagnes massives non segmentées dégradent ROI.
La segmentation permet personnalisation des offres SMS.

#### 2.1.2 Cas d'usage opérationnels

Campagnes upsell sur Power Users.
Réactivation sur Occasionnels.
Parcours onboarding renforcé sur Trial Only.
Priorisation support sur segments à fort churn.

### 2.2 Données Sources et Préparation

#### 2.2.1 Tables exploitées par segmentation_repo

subscriptions
billing_events
services
service_types

#### 2.2.2 Features effectivement utilisées pour clustering service

Contrairement au template théorique, l'entraînement KMeans utilise deux dimensions principales:
Feature x: ratio billing_count vs percentile p75_billing.
Feature y: ratio revenue vs percentile p75_revenue.

#### 2.2.3 Tableau de mapping feature/source réel

| Feature       | Table source                         | Agrégation                          | Normalisation                                    |
| ------------- | ------------------------------------ | ----------------------------------- | ------------------------------------------------ |
| billing_count | billing_events + subscriptions       | COUNT events SUCCESS par user       | ratio contre percentile p75                      |
| revenue       | service_types.price + billing_events | SUM(price) SUCCESS par user         | ratio contre percentile p75                      |
| x             | dérivée                              | LEAST(billing_count/p75_billing,1)  | StandardScaler au train                          |
| y             | dérivée                              | LEAST(revenue/p75_revenue,1)        | StandardScaler au train                          |
| active_days   | billing_events                       | COUNT DISTINCT DATE(event_datetime) | utilisé en profiling, pas training KMeans direct |

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

#### 2.2.5 Commentaire méthodologique

Le clustering visuel consommé frontend est déjà segmenté SQL par règles percentiles.
Le train KMeans sert surtout à construire artefact modèle et mapping.
Il existe donc un double paradigme:
Segmentation SQL heuristique pour API runtime.
KMeans pour entraînement explicite et persistance.

### 2.3 Algorithme K-Means

#### 2.3.1 Formulation

Fonction objectif:

$$
J = \sum_{i=1}^{k} \sum_{x \in C_i} \|x - \mu_i\|^2
$$

#### 2.3.2 Paramètres réels

n_clusters = 4
random_state = 42
n_init = 10
algorithm = lloyd
max_iter = 300

#### 2.3.3 Code exact d'entraînement

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

K=4 est codé en dur.
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Aucune implémentation Elbow ou Silhouette observée.

#### 2.3.5 Convergence

Critère interne géré par implémentation sklearn.
Pas de logique custom de convergence dans le code.

### 2.4 Description des 4 Segments

#### 2.4.1 Segments réellement présents

Power Users
Regular Loyals
Occasional Users
Trial Only

#### 2.4.2 Mécanisme de construction profils

Profiling via requêtes SQL agrégées.
Métriques profil:
ARPU moyen
jours actifs moyens
churn_rate segment

#### 2.4.3 Fiche Segment 1 — Power Users

Profil:
billing_count et revenue dans quantile haut.
Valeur métier:
haut ARPU, prioritaire upsell.
Risque churn:
calculé via jointure subscriptions status.
Recommandation:
pack premium multi-services.

#### 2.4.4 Fiche Segment 2 — Regular Loyals

Profil:
usage/révenue médian-haut stable.
Valeur métier:
base récurrente principale.
Risque churn:
intermédiaire selon période.
Recommandation:
fidélisation + cross-sell progressif.

#### 2.4.5 Fiche Segment 3 — Occasional Users

Profil:
activité sporadique et revenu faible-moyen.
Valeur métier:
fort potentiel de conversion.
Risque churn:
plus élevé que loyaux.
Recommandation:
campagnes réactivation hebdomadaires.

#### 2.4.6 Fiche Segment 4 — Trial Only

Profil:
faible ou nul billing success.
Valeur métier:
faible instantanée mais critique pour croissance.
Risque churn:
élevé.
Recommandation:
onboarding renforcé + offres d'activation J1/J2/J3.

#### 2.4.7 Tableau comparatif

| Métrique         | Power Users                             | Regular Loyals                          | Occasionnels                            | Trial Only                              |
| ---------------- | --------------------------------------- | --------------------------------------- | --------------------------------------- | --------------------------------------- |
| Activité moyenne | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| ARPU (TND)       | Exposé via profiles API                 | Exposé via profiles API                 | Exposé via profiles API                 | Exposé via profiles API                 |
| Lifetime (jours) | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Churn Rate       | Exposé via profiles API                 | Exposé via profiles API                 | Exposé via profiles API                 | Exposé via profiles API                 |
| % base           | Exposé via distribution API             | Exposé via distribution API             | Exposé via distribution API             | Exposé via distribution API             |

### 2.5 Méthode d'Assignation des Labels

#### 2.5.1 Dans la logique SQL runtime

Labels assignés par règles percentiles:
haut billing + haut revenue => Power Users
médian billing + médian revenue => Regular Loyals
billing > 0 sinon => Occasional Users
sinon => Trial Only

#### 2.5.2 Dans la logique KMeans train

Après clustering, labels re-mappés par revenu moyen cluster.
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

#### 2.5.3 rank_map observé dans artefact

{"1": "Trial Only", "2": "Occasional Users", "3": "Regular Loyals", "0": "Power Users"}

### 2.6 Visualisation et Interprétation

#### 2.6.1 Clustering Map

Frontend: UserSegmentationPage.jsx
Type: ScatterChart.
Axe X: Axis 1 — Activity / Usage Frequency.
Axe Y: Axis 2 — ARPU / Value.
Couleurs par segment via SEGMENT_COLORS.

#### 2.6.2 Segment Size Distribution

BarChart vertical.
Mesure: percentage segment.
Source: /analytics/segmentation/clusters distribution.

#### 2.6.3 User Distribution Pie

PieChart donut.
Affiche proportions par segment.
Note critique:
userCount hardcodé à 1.2M dans composant.
Peut diverger du réel.

#### 2.6.4 Radar Chart comportemental

Radar data actuellement statique (hardcoded) dans la page.
Axes:
Activity
ARPU
Retention
Loyalty
Engagement

Important:
Ce radar n'est pas alimenté par backend en l'état.

### 2.7 Endpoints et Intégration

#### 2.7.1 Endpoints backend segmentation

GET /analytics/segmentation/kpis
GET /analytics/segmentation/clusters
GET /analytics/segmentation/profiles
POST /analytics/segmentation/train

#### 2.7.2 Schéma réponses

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

### 2.8 Limites et Améliorations

#### 2.8.1 Limites identifiées

K fixé sans preuve quantitative dans code.
Front mixe data réelle et fallback mock.
Radar non connecté données réelles.
Double logique segmentation SQL + KMeans pouvant diverger.

#### 2.8.2 Améliorations recommandées

Ajouter Silhouette Score et Davies-Bouldin.
Tester DBSCAN/HDBSCAN pour structures non sphériques.
Supprimer mocks frontend en production.
Exposer centres de clusters et métriques stabilité temporelle.
Versionner dataset segmentation utilisé au train.

---

## PARTIE III — DÉTECTION D'ANOMALIES

### 3.1 Contexte et Justification

#### 3.1.1 Pourquoi critique en télécom

Chute DAU soudaine peut indiquer panne accès.
Pic churn peut révéler incident facturation ou qualité service.
Anomalie revenu peut signaler rupture pipeline billing.

#### 3.1.2 Implémentation observée

Module anomalies est exposé via router /anomalies.
Calcul anomalies à la volée sur séries quotidiennes.
Pas de persistance table anomalies observée dans code actuel.

### 3.2 Méthode : Z-Score sur Fenêtre Glissante

#### 3.2.1 Formule utilisée

$$
z_t = \frac{x_t - \mu_{t-w:t-1}}{\sigma_{t-w:t-1}}
$$

avec $w=14$ jours selon code.

#### 3.2.2 Extrait exact détection

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

#### 3.2.3 Seuils réels implémentés

|z| >= 4 => critical
|z| >= 3 => high
|z| >= 2 => medium

Note:
Le cahier demandait medium à 2.5.
Le code réel utilise 2.0.

#### 3.2.4 Mention Isolation Forest

Le texte UI et insights mentionne "Z-Score + Isolation Forest".
Aucun calcul IsolationForest observé dans router anomalies.py.
Conclusion:
Isolation Forest est [NON TROUVÉ DANS LE CODE — À COMPLÉTER].

### 3.3 Métriques Surveillées

#### 3.3.1 Liste réelle

metrics = (dau, churn_rate, revenue, renewals)

#### 3.3.2 Tableau source/agrégation

| Métrique   | Source SQL                           | Agrégation                    | Seuil critique |
| ---------- | ------------------------------------ | ----------------------------- | -------------- | --- | ------------ |
| DAU        | user_activities                      | COUNT DISTINCT user_id / jour |                | z   | >=4 critical |
| Churn Rate | unsubscriptions + active_base        | COUNT churn / actifs \*100    |                | z   | >=4 critical |
| Revenue    | billing_events + service_types.price | SUM(price) success / jour     |                | z   | >=4 critical |
| Renewals   | billing_events                       | COUNT success / jour          |                | z   | >=4 critical |

#### 3.3.3 Requête quotidienne exacte (extrait)

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

### 3.4 Pipeline de Détection

#### 3.4.1 Fréquence d'exécution

Pas de scheduler explicite dans code router.
Détection déclenchée:
au chargement endpoints
ou via POST /anomalies/run-detection

#### 3.4.2 Fenêtrage temporel

Résolution des dates via resolve_date_range(source='billing').
Cap de sécurité MAX_ANOMALY_RANGE_DAYS = 120.

#### 3.4.3 Niveaux de sévérité

critical/high/medium selon z-score absolu.
Direction dérivée:
spike si z_score > 0
drop sinon.

#### 3.4.4 Persistance anomalies

Table anomalies persistée:
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Le code génère IDs uuid temporaires en mémoire par appel.

### 3.5 Schéma de Table Anomalies

#### 3.5.1 Schéma demandé dans prompt

Le schéma CREATE TABLE fourni par le cahier n'est pas observé dans les migrations auditées.
Aucun modèle SQLAlchemy anomalies n'a été trouvé.

#### 3.5.2 Position académique

Inclure ce schéma comme cible d'industrialisation.
Le marquer "non implémenté" dans code actuel.

#### 3.5.3 Schéma cible proposé

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

#### 3.6.1 Endpoints réels exposés

GET /anomalies/summary
GET /anomalies/timeline
GET /anomalies/distribution
GET /anomalies/heatmap
GET /anomalies/details
GET /anomalies/insights
POST /anomalies/run-detection

#### 3.6.2 Écart avec endpoints demandés

Le prompt mentionne /analytics/anomalies.
Implémentation réelle utilise préfixe /anomalies.
Endpoint POST /analytics/anomalies/{id}/status:
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]

#### 3.6.3 Visualisations frontend anomalies

Timeline multi-métriques + points anomalies.
Heatmap services x semaines.
Pie distribution sévérité.
Bars anomalies par métrique.
Table détails paginée.
Cartes insights textuelles.

#### 3.6.4 Schémas de réponse observés

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

Hypothèse implicite de stationnarité locale.
Sensibilité aux fenêtres courtes et petits échantillons.
Faux positifs en présence de saisonnalité non modélisée.

#### 3.7.2 Alternatives robustes

IQR par métrique et service.
Median Absolute Deviation.
Prophet residual anomaly detection.
Isolation Forest multivarié réel.

#### 3.7.3 Limite volumétrique

Fenêtre de données courte (2 mois) restreint robustesse temporelle.
Avec w=14, seulement ~46 points activement exploitables sur 60 jours.

---

## PARTIE IV — COMPARAISON ET SYNTHÈSE

### 4.1 Tableau Comparatif des 3 Modules IA

| Critère          | Prédiction Churn                        | Segmentation K-Means                   | Détection Anomalies                  |
| ---------------- | --------------------------------------- | -------------------------------------- | ------------------------------------ |
| Type d'IA        | Supervisé                               | Non supervisé + heuristique SQL        | Statistique                          |
| Algorithme       | LogisticRegression                      | KMeans (n=4)                           | Z-Score rolling                      |
| Données d'entrée | Features abonnement/comportement        | x,y dérivés billing+revenue            | Séries journalières KPI              |
| Sortie           | Probabilité [0,1] + catégorie           | Segment + distribution                 | z_score + sévérité + direction       |
| Fréquence        | A la demande                            | A la demande + train manuel            | A la demande + run endpoint          |
| Latence endpoint | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | logs précédents: ~1.6s à 2.4s observés | dépend plage, optimisée avec bornage |
| Complexité       | Moyenne                                 | Moyenne                                | Faible à moyenne                     |
| Explicabilité    | Bonne (coefficients)                    | Moyenne                                | Très haute                           |
| Valeur métier    | Très haute                              | Haute                                  | Haute                                |

### 4.2 Architecture IA Globale

#### 4.2.1 Flux macro

hawala_db (source prod lecture seule)
-> ETL / ingestion analytics_db
-> scripts features/retention
-> modèles ML joblib
-> endpoints FastAPI
-> visualisation React

#### 4.2.2 Routage backend observé (main.py)

Routers inclus total observé > 14.
Inclut ml_churn, segmentation, anomalies explicitement.
Middleware latency_logger centralise timing requêtes.

#### 4.2.3 Nombre de hooks frontend

Hooks recensés dans src/hooks: 33 fichiers.
Observation:
la mention "28 hooks" dans prompt n'est plus à jour selon arborescence actuelle.

### 4.3 Interdépendances entre Modules

#### 4.3.1 Segmentation -> Churn

Interdépendance directe feature-level:
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Aucune feature churn ne consomme explicitement label segment.

#### 4.3.2 Anomalies -> Retraining

Déclenchement automatique retrain churn/segmentation par anomalies:
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Aucun orchestrateur de ce type dans les routeurs audités.

#### 4.3.3 Churn -> Segments à risque

Consommation score churn dans segmentation:
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]
Les deux modules restent découplés techniquement.

### 4.4 Performance Globale du Système IA

#### 4.4.1 Tableau latences

| Endpoint IA                      |                         Latence mesurée |    Cible | Statut                                  |
| -------------------------------- | --------------------------------------: | -------: | --------------------------------------- |
| /ml/churn/scores                 | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] | < 2000ms | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| /ml/churn/metrics                | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |  < 500ms | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| /analytics/segmentation/kpis     |        1711ms (valeur fournie contexte) | < 1000ms | ⚠️                                      |
| /analytics/segmentation/clusters |        1658ms (valeur fournie contexte) | < 1000ms | ⚠️                                      |
| /analytics/segmentation/profiles |        2427ms (valeur fournie contexte) | < 1000ms | ❌                                      |

#### 4.4.2 Analyse performance

Segmentation est le module le plus coûteux en agrégations SQL.
Anomalies a nécessité bornage plage + retry timeout.
Churn nécessite potentiellement indexation fine sur activités et events temporels.

---

## PARTIE V — CONCLUSIONS ET PERSPECTIVES

### 5.1 Bilan des Objectifs IA

#### 5.1.1 Statut par objectif

[x] Prédiction churn: implémentée, entraînement et scoring opérationnels.
[x] Segmentation utilisateurs: opérationnelle, KMeans sérialisé.
[x] Détection anomalies: opérationnelle via z-score API.
[ ] Optimisation campagnes pilotée ML: [NON TROUVÉ DANS LE CODE — À COMPLÉTER].

#### 5.1.2 Maturité globale

Prototype avancé orienté production interne.
Niveau correct pour démonstration PFE.
Nécessite consolidation MLOps/monitoring pour mise à l'échelle.

### 5.2 Valeur Métier Quantifiée

| Module              | Bénéfice estimé                                        | Méthode de calcul                                                  |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------------------ |
| Prédiction churn    | Réduction churn potentielle via intervention priorisée | Simuler scénario: % churners détectés x taux de rétention campagne |
| Segmentation        | Hausse ARPU ciblée                                     | Comparer campagnes segmentées vs mass mailing                      |
| Détection anomalies | Réduction temps détection incident                     | Mesurer MTTD manuel vs automatique                                 |

Remarque:
Valeurs numériques finales de ROI ne sont pas codées.
[NON TROUVÉ DANS LE CODE — À COMPLÉTER]

### 5.3 Roadmap IA Post-PFE

#### Priorité 1 — 1 à 3 mois

Implémenter SHAP global/local churn.
Automatiser retrain mensuel avec snapshot data.
Ajouter silhoutte et monitoring drift clusters.
Supprimer fallback mock dans UserSegmentationPage.

#### Priorité 2 — 3 à 6 mois

Benchmarker XGBoost/LightGBM pour churn.
Ajouter Isolation Forest réel côté anomalies.
Ajouter calibration probabiliste + Brier score.
Industrialiser table anomalies persistée + workflows statut.

#### Priorité 3 — 6 à 12 mois

MLOps complet: versioning modèles/données/features.
Feature store léger pour cohérence training/serving.
A/B testing systématique des campagnes basées IA.
Modèle LTV pour arbitrage budget rétention.

### 5.4 Références Académiques

Breiman, L. (2001). Random Forests. Machine Learning.
MacQueen, J. (1967). Some Methods for Classification and Analysis of Multivariate Observations.
Hawkins, D.M. (1980). Identification of Outliers.
Provost, F. & Fawcett, T. (2013). Data Science for Business.

---

## ANNEXE A — Inventaire technique détaillé

### A.1 Modèle Subscription (attributs clés)

id UUID PK
user_id FK users
service_id FK services
campaign_id FK campaigns nullable
subscription_start_date timestamptz
subscription_end_date timestamptz nullable
status string(20)
created_at

Indexes observés:
ix_subscriptions_user_id
ix_subscriptions_service_id
ix_subscriptions_status
ix_subscriptions_start_date
ix_subscriptions_campaign_id
idx_user_service

### A.2 Modèle UserActivity

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

### A.3 Modèle BillingEvent

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

### A.4 Modèle Unsubscription

id
subscription_id unique
user_id
service_id
unsubscription_datetime
churn_type
churn_reason
days_since_subscription
last_billing_event_id

### A.5 Modèle Cohort

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

## ANNEXE B — ETL Cohortes

### B.1 Objectif script compute_cohorts.py

Calculer et upserter la table cohorts.
Mesurer retention D7 D14 D30.
Adapter automatiquement selon type de colonne date/time.

### B.2 Étapes du script

Étape 0:
Diagnostic statuts disponibles dans subscriptions.

Étape 1:
Vérification volume source et plage dates.

Étape 2:
Construction first_sub (premier abonnement user+service).

Étape 3:
Calcul retention par EXISTS sur jalons 7/14/30 jours.

Étape 4:
INSERT INTO cohorts ON CONFLICT UPDATE.

Étape 5:
Vérification finale table cohorts.

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
Cela évite interruption sur scans historiques lourds.
Nécessite surveillance pour usage contrôlé en production.

---

## ANNEXE C — API Churn détaillée

### C.1 POST /ml/churn/train

But:
lancer entraînement modèle logistic.
Sécurité:
require_admin.
Sortie:
métriques complètes.

### C.2 GET /ml/churn/metrics

But:
charger métriques sauvegardées.
Erreur 404 si modèle non entraîné.

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

## ANNEXE D — API Segmentation détaillée

### D.1 GET /analytics/segmentation/kpis

KPI business segmentaires.
Réponse typée KPIResponse.

### D.2 GET /analytics/segmentation/clusters

Retourne points x/y pour scatter map.
Inclut distribution segments.
Sampling max 3000 points côté service pour performance.

### D.3 GET /analytics/segmentation/profiles

Retourne profils segment (duration, arpu, churn_rate).

### D.4 POST /analytics/segmentation/train

Entraîne KMeans sur features x/y standardisées.
Sauvegarde dictionnaire joblib avec model+scaler+rank_map+window.

---

## ANNEXE E — API Anomalies détaillée

### E.1 GET /anomalies/summary

KPI synthèse anomalies.
Inclut tendance période précédente.

### E.2 GET /anomalies/timeline

Séries temporelles + anomalies annotées.

### E.3 GET /anomalies/distribution

Comptages par sévérité et métrique.

### E.4 GET /anomalies/heatmap

Matrice service x semaine.
Niveau severity_score dérivé count.

### E.5 GET /anomalies/details

Pagination limit/offset.
Données tabulaires opérationnelles.

### E.6 GET /anomalies/insights

Cartes textuelles recommandation.

### E.7 POST /anomalies/run-detection

Déclenche run logique et renvoie compteurs.

---

## ANNEXE F — Extraits Frontend IA

### F.1 Churn dashboard

Actions:
Train model
Refresh
Réglage threshold
Réglage top N

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

KPI cards synthèse
Timeline line+scatter
Heatmap table
Pie severity
Metric bars
Table anomalies paginée
Insights cards

---

## ANNEXE G — Incohérences et dette technique

### G.1 Incohérence définition churn

Doc dit subscription_end_date non null.
Code utilise status cancelled/expired.
Action:
aligner documentation et code de référence.

### G.2 Incohérence segmentation runtime vs training

Runtime SQL segmente déjà via règles.
KMeans entraîné mais non utilisé pour inférence API live.
Action:
clarifier architecture cible.

### G.3 Incohérence anomalies Isolation Forest

UI indique combinaison Z-Score + Isolation Forest.
Code calcule uniquement Z-score rolling.
Action:
implémenter IsolationForest ou corriger wording.

### G.4 Frontend mocks restants

UserSegmentationPage conserve generateMock\* et insights statiques.
Action:
neutraliser mocks en mode production.

### G.5 Endpoint statut anomalies absent

POST /analytics/anomalies/{id}/status non trouvé.
Action:
ajouter persistance anomalies + workflow statut.

---

## ANNEXE H — Recommandations SQL et performance

### H.1 Indexation churn training

Index composite recommandé:
(user_id, service_id, activity_datetime) sur user_activities déjà partiellement présent.
(subscription_id, event_datetime, status) sur billing_events à vérifier.

### H.2 Fenêtrage temporel

Bonnes pratiques observées:
resolve_date_range
get_data_bounds
bornage anomalies MAX_ANOMALY_RANGE_DAYS

### H.3 Réduction scans lourds

Pré-agrégation journalière possible:
materialized views KPI quotidiens.

### H.4 Monitoring latence

middleware latency_logger existe.
Action:
persist logs latence endpoint + percentile P95/P99.

---

## ANNEXE I — Feuille de route MLOps

### I.1 Gouvernance modèle

Version modèle
Version features
Version dataset
Version métriques

### I.2 Observabilité

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

### I.4 Sécurité et conformité

Traçabilité décision IA
Minimisation données personnelles
Contrôle accès endpoints train
Audit trail inférence

---

## ANNEXE J — Vérification artefacts joblib

### J.1 churn_model.joblib

Type réel: sklearn.linear_model.\_logistic.LogisticRegression
Paramètres clés:
class_weight=balanced
max_iter=2000
random_state=42
solver=lbfgs
C=1.0

### J.2 churn_metrics.joblib

Type réel: dict
Clés:
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

Type réel: dict
Contenu:
model (KMeans)
scaler (StandardScaler)
rank_map
trained_at
window

---

## ANNEXE K — Exigences du prompt vs état réel

### K.1 Exigence: reproduire SQL churn exact

Statut: fait dans ce rapport.

### K.2 Exigence: décrire .joblib

Statut: fait via inspection réelle.

### K.3 Exigence: endpoints churn

Statut: fait.

### K.4 Exigence: endpoints segmentation

Statut: fait.

### K.5 Exigence: endpoints anomalies demandés /analytics/anomalies

Statut: partiel.
État réel: routes sous /anomalies.

### K.6 Exigence: table anomalies persistée

Statut: non trouvé.

### K.7 Exigence: minimum 800 lignes

Statut: visé dans ce document.

---

## ANNEXE L — Tableau de conformité [NON TROUVÉ] par section

| Rubrique                                | État                                    |
| --------------------------------------- | --------------------------------------- |
| Coût acquisition client chiffré         | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Matrice confusion brute TP/TN/FP/FN     | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Validation croisée churn                | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Endpoint /analytics/churn/curve         | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Endpoint /analytics/churn/time-to-churn | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Endpoint /analytics/churn/reasons       | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Endpoint /analytics/churn/risk-segments | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Elbow method segmentation               | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Silhouette score segmentation           | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Isolation Forest effectif               | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Table anomalies SQLAlchemy/migration    | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Endpoint statut anomalies               | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Latence /ml/churn/scores mesurée        | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |
| Latence /ml/churn/metrics mesurée       | [NON TROUVÉ DANS LE CODE — À COMPLÉTER] |

---

## ANNEXE M — Conclusion académique concise

Le système IA est réel, déployable et déjà intégré UX/API.
Le module churn est le plus avancé en cycle complet data->model->API->UI.
Le module segmentation fonctionne mais souffre d'ambiguïté entre logique SQL et KMeans.
Le module anomalies est utile et opérationnel, mais reste statistique simple sans persistance native.
Pour une soutenance PFE, la profondeur technique est solide.
Pour une industrialisation entreprise, la priorité est la rigueur MLOps et la réduction des écarts de spécification.

Fin du rapport.
