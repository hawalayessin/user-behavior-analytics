## KPI Catalog — User Behavior Analytics Platform

This document summarizes all implemented KPIs, their formulas, data sources, and API endpoints.

---

### 1. Daily / Weekly / Monthly Active Users (DAU / WAU / MAU)

- **Name**: Daily / Weekly / Monthly Active Users  
- **Endpoint**: `GET /analytics/user-activity`  
- **Source tables**: `user_activities`  
- **Granularity**: Daily (with rolling 7d / 30d windows)  
- **Filters**:
  - `start_date` (optional, ISO date)
  - `end_date` (optional, ISO date)
  - `service_id` (optional, UUID)
- **Response keys** (excerpt):
  - `kpis.dau_today`
  - `kpis.wau_current_week`
  - `kpis.mau_current_month`

**SQL logic (simplified):**

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
  AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day';
```

- **Derived KPI**: Stickiness = `dau_today / mau_current_month * 100`.

---

### 2. Average Subscription Lifetime (days)

- **Name**: Average Subscription Lifetime  
- **Endpoint**: `GET /analytics/user-activity`  
- **Source tables**: `subscriptions`  
- **Granularity**: Aggregated over selected period  
- **Filters**: same as section 1  
- **Response key**: `kpis.avg_lifetime_days`

**SQL logic (simplified):**

```sql
SELECT ROUND(AVG(
  EXTRACT(DAY FROM COALESCE(subscription_end_date, NOW()) - subscription_start_date)
), 0) AS avg_lifetime_days
FROM subscriptions
WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
  AND subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
  AND status IN ('active', 'cancelled', 'expired');
```

---

### 3. Inactive Users (7+ days)

- **Name**: Inactive Users (no activity in last 7 days)  
- **Endpoint**: `GET /analytics/user-activity`  
- **Source tables**: `users`, `user_activities`, `subscriptions`  
- **Granularity**: Aggregated count  
- **Filters**: `end_dt` inferred or provided; optional `service_id`  
- **Response key**: `kpis.inactive_count`

**SQL logic (simplified):**

```sql
SELECT COUNT(DISTINCT u.id) AS inactive_count
FROM users u
LEFT JOIN user_activities ua
  ON  ua.user_id = u.id
  AND ua.activity_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '7 days'
WHERE ua.user_id IS NULL
  AND u.status NOT IN ('churned', 'cancelled');
```

Additionally, inactivity **buckets** are exposed as:

```sql
SELECT
  CASE
    WHEN EXTRACT(DAY FROM NOW() - last_activity_at) BETWEEN 1 AND 7  THEN '1-7 days'
    WHEN EXTRACT(DAY FROM NOW() - last_activity_at) BETWEEN 8 AND 14 THEN '8-14 days'
    WHEN EXTRACT(DAY FROM NOW() - last_activity_at) BETWEEN 15 AND 30 THEN '15-30 days'
    WHEN EXTRACT(DAY FROM NOW() - last_activity_at) > 30            THEN '30+ days'
    ELSE 'Unknown'
  END AS bucket,
  COUNT(*) AS count
FROM users
WHERE last_activity_at IS NOT NULL
  AND status NOT IN ('churned', 'cancelled')
GROUP BY bucket;
```

---

### 4. Free Trial — Core KPIs

- **Endpoint**: `GET /analytics/trial/kpis`  
- **Source table**: `subscriptions`  
- **Filters**:
  - `start_date`, `end_date` (optional, ISO dates)
  - `service_id` (optional UUID)
- **Response keys**:
  - `total_trials`
  - `conversion_rate`
  - `avg_duration`
  - `dropoff_j3`
  - `trial_only_users`
  - `trial_only_rate`
  - `active_trials`
  - `cancelled_trials`

#### 4.1 Total Trials Started

```sql
SELECT COUNT(*) AS total
FROM subscriptions
WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
  AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day';
```

#### 4.2 Trial → Paid Conversion Rate

```sql
SELECT
  COUNT(*)                                         AS total_all,
  COUNT(*) FILTER (WHERE status = 'active')       AS active_subs,
  COUNT(*) FILTER (WHERE status = 'cancelled')    AS cancelled_subs,
  COUNT(*) FILTER (WHERE status = 'trial')        AS trial_subs
FROM subscriptions
WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
  AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day';
```

Formula: `conversion_rate = active_subs / total_all * 100`.

#### 4.3 Average Trial Duration (days)

```sql
SELECT ROUND(AVG(
  GREATEST(
    0,
    EXTRACT(DAY FROM COALESCE(subscription_end_date, NOW()) - subscription_start_date)
  )
)::numeric, 1) AS avg_days
FROM subscriptions
WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
  AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
  AND subscription_start_date <= NOW();
```

#### 4.4 Day 3 Drop-off Rate

```sql
WITH base AS (
  SELECT
    GREATEST(
      0,
      EXTRACT(DAY FROM COALESCE(subscription_end_date, NOW()) - subscription_start_date)
    )::int AS duration_days
  FROM subscriptions
  WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
    AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
    AND subscription_start_date <= NOW()
    AND status IN ('cancelled', 'expired')
    AND subscription_end_date IS NOT NULL
)
SELECT
  COUNT(*) FILTER (WHERE duration_days <= 1)                      AS day1,
  COUNT(*) FILTER (WHERE duration_days > 1 AND duration_days <= 2) AS day2,
  COUNT(*) FILTER (WHERE duration_days > 2 AND duration_days <= 3) AS day3
FROM base;
```

`dropoff_j3` = `% of cancelled/expired trials with duration_days ≤ 3`.

#### 4.5 Trial-only Users

Users who have at least one trial in period but **never** switched to an active subscription.

```sql
WITH trial_users AS (
  SELECT DISTINCT user_id
  FROM subscriptions
  WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
    AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
),
has_active AS (
  SELECT DISTINCT user_id
  FROM subscriptions
  WHERE status = 'active'
)
SELECT
  COUNT(*) AS trial_only_users,
  COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM trial_users), 0) AS trial_only_rate
FROM trial_users tu
LEFT JOIN has_active ha ON ha.user_id = tu.user_id
WHERE ha.user_id IS NULL;
```

---

### 5. Retention — Cohort KPIs

- **Endpoints**:
  - `GET /analytics/retention/kpis`
  - `GET /analytics/retention/heatmap`
  - `GET /analytics/retention/curve`
  - `GET /analytics/retention/cohorts-list`
- **Source tables**: `cohorts` (computed by ETL), `services`  
- **Key KPIs**:
  - `avg_retention_d7`, `avg_retention_d30`
  - `best_cohort`, `best_cohort_d7`
  - `at_risk_count` (cohorts with D7 < 30)

Example query for KPIs:

```sql
SELECT
  AVG(retention_d7)  AS avg_d7,
  AVG(retention_d30) AS avg_d30,
  COUNT(id)          AS total_cohorts
FROM cohorts
WHERE cohort_date BETWEEN :start_dt AND :end_dt;
```

Best cohort:

```sql
SELECT cohort_date, retention_d7
FROM cohorts
WHERE cohort_date BETWEEN :start_dt AND :end_dt
ORDER BY retention_d7 DESC NULLS LAST
LIMIT 1;
```

---

### 6. Campaign Impact KPIs

- **Endpoint**: `GET /analytics/campaigns/kpis`  
- **Source tables**: `campaigns`, `subscriptions`, `cohorts`  
- **Response keys**:
  - `total_campaigns`
  - `total_subs_from_campaigns`
  - `avg_conversion_rate`
  - `avg_retention_d7`
  - `top_campaign_name`, `top_campaign_subs`

Core query (excerpt):

```sql
WITH per_campaign AS (
  SELECT
    c.id AS campaign_id,
    c.name AS campaign_name,
    c.target_size,
    COUNT(s.id) AS total_subs
  FROM campaigns c
  LEFT JOIN subscriptions s ON s.campaign_id = c.id
  WHERE DATE(c.send_datetime) BETWEEN :start_dt AND :end_dt
  GROUP BY c.id, c.name, c.target_size
),
d7 AS (
  SELECT
    AVG(co.retention_d7) AS avg_d7
  FROM campaigns c
  LEFT JOIN cohorts co
    ON co.service_id = c.service_id
   AND co.cohort_date = date_trunc('month', c.send_datetime)::date
  WHERE DATE(c.send_datetime) BETWEEN :start_dt AND :end_dt
)
SELECT
  (SELECT COUNT(DISTINCT campaign_id) FROM per_campaign) AS total_campaigns,
  (SELECT COALESCE(SUM(total_subs), 0) FROM per_campaign) AS total_subs_from_campaigns,
  (SELECT COALESCE(AVG((total_subs::numeric / NULLIF(target_size, 0)) * 100), 0) FROM per_campaign) AS avg_conversion_rate,
  (SELECT COALESCE(avg_d7, 0) FROM d7) AS avg_retention_d7;
```

Conversion per campaign: `total_subs / target_size * 100`.

---

### 7. Churn Analysis KPIs

- **Endpoints**:
  - `GET /analytics/churn/kpis`
  - `GET /analytics/churn/curve`
  - `GET /analytics/churn/time-to-churn`
  - `GET /analytics/churn/reasons`
  - `GET /analytics/churn/risk-segments`
- **Source tables**: `subscriptions`, `services`, `service_types`, `unsubscriptions`, `billing_events`, `user_activities`

All KPIs are built on a common CTE:

```sql
WITH churn_facts AS (
  SELECT
    s.id AS subscription_id,
    s.user_id,
    s.service_id,
    sv.name AS service_name,
    st.billing_frequency_days,
    st.trial_duration_days,
    s.subscription_start_date,
    s.subscription_end_date,
    u.unsubscription_datetime,
    u.churn_type,
    u.churn_reason,
    u.days_since_subscription,
    be_first.event_datetime AS first_charge_date,
    EXTRACT(DAY FROM (u.unsubscription_datetime - s.subscription_start_date))::int AS days_to_churn,
    CASE
      WHEN u.unsubscription_datetime IS NULL THEN FALSE
      WHEN u.days_since_subscription <= st.trial_duration_days THEN TRUE
      ELSE FALSE
    END AS is_trial_churn,
    CASE
      WHEN u.unsubscription_datetime IS NOT NULL
           AND be_first.event_datetime IS NOT NULL
      THEN EXTRACT(DAY FROM (u.unsubscription_datetime - be_first.event_datetime))::int
      ELSE NULL
    END AS days_after_first_charge
  FROM subscriptions s
  JOIN services sv        ON sv.id = s.service_id
  JOIN service_types st   ON st.id = sv.service_type_id
  LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
  LEFT JOIN LATERAL (
    SELECT be.event_datetime
    FROM billing_events be
    WHERE be.subscription_id = s.id
      AND be.is_first_charge = TRUE
      AND be.status = 'SUCCESS'
    ORDER BY be.event_datetime ASC
    LIMIT 1
  ) be_first ON TRUE
)
```

#### 7.1 Global Churn Rate

Within a period `[start_dt, end_dt]`:

```sql
WITH active_start AS (
  SELECT COUNT(DISTINCT s.id) AS active_at_start
  FROM subscriptions s
  WHERE s.subscription_start_date < CAST(:start_dt AS timestamp) + INTERVAL '1 day'
    AND (s.subscription_end_date IS NULL OR s.subscription_end_date >= CAST(:start_dt AS timestamp))
),
churned_in_period AS (
  SELECT * FROM churn_facts cf
  WHERE cf.unsubscription_datetime IS NOT NULL
    AND DATE(cf.unsubscription_datetime) BETWEEN :start_dt AND :end_dt
)
SELECT
  (SELECT active_at_start FROM active_start) AS active_at_start,
  (SELECT COUNT(*) FROM churned_in_period)   AS churned_count;
```

Formula: `global_churn_rate = churned_count / active_at_start * 100` (borné à [0,100]).

#### 7.2 Average Time-to-Churn, Trial vs Paid, First-bill Churn

Computed from `churned_in_period`:

- `avg_lifetime_days = AVG(days_to_churn)` for churned users.  
- `trial_churn_pct = % of churn with is_trial_churn = TRUE`.  
- `first_bill_churn_rate = % churn with days_after_first_charge BETWEEN 0 AND 7 among churned with a valid first charge`.

#### 7.3 Voluntary vs Technical Churn

From same CTE:

```sql
SELECT
  100.0 * COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') / NULLIF(COUNT(*), 0) AS voluntary_pct,
  100.0 * COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') / NULLIF(COUNT(*), 0) AS technical_pct
FROM churned_in_period;
```

#### 7.4 Time-to-Churn Buckets

- Buckets: `"0-3 days"`, `"4-7 days"`, `"8-30 days"`, `"31-90 days"`, `"90+ days"`, `"Unknown"`  
- Grouped by `service_name`, `churn_type`, `bucket`.

#### 7.5 Churn Reasons Top 10

Grouped by `churn_type`, `churn_reason` (NULL/empty mapped to `"Unknown"`), ordered by count desc, limited to 10.

#### 7.6 Risk Segments (Rule-based)

Segments A–D defined via heuristics on `churn_facts`, `user_activities`, `billing_events`:

- **SEG_A**: Low activity ( <2 events last 7 days) + ≥1 failed billing in last 30 days.  
- **SEG_B**: Churn in <7 days for weekly-billed services.  
- **SEG_C**: Services where trial churn >30% of churn events.  
- **SEG_D**: Services with high first-bill failure rate (>20% failed first charges).

Each segment returns:
- `segment_id`, `label`, `description`, `affected_users`, `top_services[]`.

---

### 8. Notes & Benchmarks (à adapter pour le jury)

- **DAU/WAU/MAU & Stickiness**:
  - Benchmarks SaaS souvent: Stickiness (DAU/MAU) **20–30%** considéré correct, **>50%** excellent.
- **Trial → Paid Conversion**:
  - Beaucoup de services B2C visent **>20–30%** conversion depuis essai, selon la friction et le pricing.
- **D7 / D30 Retention**:
  - D7 > 40% et D30 > 20% sont des seuils raisonnables pour services de souscription SMS/B2C.
- **Churn Rate**:
  - Pour abonnements mensuels, un churn mensuel **<5%** est souvent jugé sain; hauts churns >10% nécessitent investigation.

Ces benchmarks doivent être comparés aux valeurs réelles extraites des endpoints ci-dessus pour bâtir la partie “findings” et “recommandations” du mémoire PFE.

