# ML Churn Prediction Report (Logistic Regression)

## 1) Objective

Predict the probability that a subscription will churn, using a supervised machine learning model trained on historical subscription and user behavior data.  
The model is integrated into the backend API and visualized in the React dashboard `AI Churn Prediction`.

## 2) Data Sources (Existing Tables)

The model uses the following tables already present in the project:

- `subscriptions`: `(id, user_id, service_id, subscription_start_date, subscription_end_date, status)`
- `unsubscriptions`: `(subscription_id, unsubscription_datetime, churn_type)`
- `billing_events`: `(subscription_id, event_datetime, status, is_first_charge)`
- `user_activities`: `(user_id, service_id, activity_datetime)`
- `services`: `(id, name, service_type_id)`
- `service_types`: `(id, billing_frequency_days, trial_duration_days)`
- `cohorts`: `(service_id, cohort_date, retention_d7, retention_d14, retention_d30)`

## 3) Label Definition (Churned)

At subscription level, the binary target is:

`churned = 1  if subscription_end_date IS NOT NULL`
`churned = 0  otherwise`

This matches the intended definition used by the code in `ml_models/churn_predictor.py`.

## 4) Feature Engineering

Model granularity: **subscription-level rows** identified by `(user_id, service_id, subscription_id)`.

### 4.1 Reference time (“ref_time”)

To avoid leakage:

- if the subscription is churned → `ref_time = subscription_end_date`
- otherwise → `ref_time = NOW()`

All “last activity” and “last 7/30 days” computations are relative to `ref_time`.

### 4.2 Features (user_features)

The following numeric features are used:

1. `days_since_last_activity`
  Days between `ref_time` and the most recent `user_activities.activity_datetime` (same user + service, <= `ref_time`).  
   Sentinel value: `999` if no activity exists.
2. `nb_activities_7d`
  Count of activities in the window `[ref_time - 7 days, ref_time]`.
3. `nb_activities_30d`
  Count of activities in the window `[ref_time - 30 days, ref_time]`.
4. `billing_failures_30d`
  Count of `billing_events` with `status='FAILED'` in the window `[ref_time - 30 days, ref_time]`.
5. `days_since_first_charge`
  Days between `ref_time` and the earliest successful first-charge (`billing_events.is_first_charge=TRUE AND status='SUCCESS'`).  
   Sentinel value: `999` if missing.
6. `is_trial_churn`
  `1` if churn occurred during the trial duration, else `0`.
7. `avg_retention_d7`
  `retention_d7` from `cohorts`, matched by:
   `cohorts.cohort_date = date_trunc('month', subscription_start_date)`
   (coalesced to `0` when missing).
8. `service_billing_frequency`
  `service_types.billing_frequency_days` (daily/weekly/monthly encoded as days).
9. `days_to_first_unsub`
  Number of days from `subscription_start_date` to churn event (`unsubscriptions`), else sentinel `999`.

## 5) Model

Algorithm: **Logistic Regression** (scikit-learn) with:

- `class_weight='balanced'` to handle class imbalance between churned/non-churned.
- `max_iter=2000` for convergence.

The code is located at:

- `user-analytics-backend/ml_models/churn_predictor.py`

The trained model and metrics are persisted using `joblib` in the same `ml_models/` folder:

- `churn_model.joblib`
- `churn_metrics.joblib`

## 6) Training & Evaluation

Training split:

- `train_test_split(test_size=0.2, random_state=42, stratify=...)`

Metrics:

- `ROC-AUC` when both classes exist in the test set.
- `accuracy` and full `classification_report` (precision/recall/F1) returned by the API.

Evaluation output is exposed by:

- `GET /ml/churn/metrics`

Training is triggered by (admin only):

- `POST /ml/churn/train`

## 7) Risk Scoring & Dashboard Interpretation

For each **active subscription** (where `subscription_end_date IS NULL`), the model outputs:

- `churn_risk = P(churned=1)`

Risk categories (used in the dashboard) are computed via probability thresholds:

- `Low`: churn_risk < 0.3
- `Medium`: 0.3 <= churn_risk < 0.6
- `High`: churn_risk >= 0.6

An optional threshold is also applied to produce a binary `predicted_churn`:

- `predicted_churn = 1` if `churn_risk >= threshold` (default `0.4`)

Predictions are exposed by:

- `GET /ml/churn/scores`

## 8) Visualizations in the PFE Jury UI

The React dashboard `AI Churn Prediction` shows:

1. Model KPIs:
  - ROC-AUC
  - Accuracy
  - Churn rate in training
  - Train samples (n)
2. Risk distribution chart:
  - counts of Low/Medium/High among scored users (max risk per user).
3. Feature impact table:
  - top logistic regression coefficients by absolute magnitude (from training metrics).
4. Top risky users table:
  - phone number + service name + risk score + predicted churn flag.

## 9) Limitations (Explain to the jury)

- Logistic Regression provides explainability but may underfit complex churn dynamics.
- The model assumes the chosen features capture churn signals; quality depends on data completeness
(activities, billing events, first charge markers, cohorts).
- “ref_time” is used to reduce leakage, but feature drift can still occur over time.

## 10) Recommended Next Steps

- Add regularization tuning for Logistic Regression (C parameter).
- Add more time-aware features (e.g., trends over time rather than only counts).
- Evaluate calibration (reliability curves) and use better probability calibration if needed.
- Store and compare prediction snapshots over time for monitoring.

