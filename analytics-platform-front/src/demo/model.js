import seed from './data.json';

export { seed };
export const round = (n, digits = 1) => Number(n.toFixed(digits));
export const pct = (n, total) => total ? round(100 * n / total) : 0;
export const sum = (rows, field) => rows.reduce((n, row) => n + Number(row[field] || 0), 0);
export const mean = (rows, field) => rows.length ? sum(rows, field) / rows.length : 0;
export const timestamp = seed.end_date + 'T12:00:00Z';
export const serviceFor = (id) => seed.services.find(s => s.id === id);
export const riskCategory = (risk) => risk >= 0.6 ? 'High' : risk >= 0.4 ? 'Medium' : 'Low';

let state = seed.seed;
const random = () => {
  state = (state * 1664525 + 1013904223) >>> 0;
  return state / 4294967296;
};

// Fixed seed keeps the public demo reproducible across browsers and builds.
export const subscribers = Array.from({ length: seed.subscriber_count }, (_, i) => {
  const service = seed.services[i % seed.services.length];
  const draw = random();
  let cumulative = 0;
  const segment = seed.segments.find(s => (cumulative += s.weight) > draw) || seed.segments.at(-1);
  const churnRisk = round(Math.min(0.97, Math.max(0.02, segment.risk + (random() - 0.5) * 0.24)), 2);
  const status = segment.name === 'Trial Only' ? 'trial' : random() < 0.15 ? 'cancelled' : random() < 0.12 ? 'billing_failed' : 'active';
  const joinedDay = Math.floor(random() * 61);
  const created = new Date(Date.parse(seed.start_date) + joinedDay * 86400000).toISOString();
  const activities = Math.max(0, segment.activity + Math.round(random() * 6 - 3));
  return {
    id: `demo-user-${i + 1}`, user_id: `demo-user-${i + 1}`,
    phone_number: `DEMO-${String(i + 1).padStart(4, '0')}`,
    full_name: `Demo Subscriber ${i + 1}`, service_id: service.id, service_name: service.name,
    services: [{ id: service.id, name: service.name }], status, segment: segment.name,
    created_at: created, trial_start_date: created, trial_end_date: new Date(Date.parse(created) + 3 * 86400000).toISOString(),
    trial_status: status === 'trial' ? 'active' : status === 'cancelled' ? 'dropped' : 'converted',
    last_activity_at: new Date(Date.parse(timestamp) - Math.max(0, 30 - activities) * 86400000).toISOString(),
    activity_type: 'service_access', activities, churn_risk: churnRisk, risk_category: riskCategory(churnRisk),
    predicted_churn: Number(churnRisk >= 0.4), revenue: status === 'trial' ? 0 : service.price,
    channel: i % 3 ? 'ussd' : 'web',
  };
});

export function scoped(params = {}) {
  return subscribers.filter(u =>
    (!params.service_id || u.service_id === params.service_id) &&
    (!params.start_date || u.created_at.slice(0, 10) >= params.start_date) &&
    (!params.end_date || u.created_at.slice(0, 10) <= params.end_date)
  );
}

export function paginate(rows, params = {}) {
  const page = Math.max(1, Number(params.page) || 1);
  const pageSize = Math.min(200, Math.max(1, Number(params.page_size || params.limit) || 10));
  return { data: rows.slice((page - 1) * pageSize, page * pageSize), total: rows.length, page, page_size: pageSize, total_pages: Math.ceil(rows.length / pageSize) };
}

export function dailySeries(params = {}) {
  const rows = scoped(params);
  const start = Math.max(Date.parse(params.start_date || seed.start_date), Date.parse(seed.start_date));
  const end = Math.min(Date.parse(params.end_date || seed.end_date), Date.parse(seed.end_date));
  const length = Math.max(0, Math.min(61, Math.floor((end - start) / 86400000) + 1));
  return Array.from({ length }, (_, i) => {
    const date = new Date(start + i * 86400000).toISOString().slice(0, 10);
    const population = rows.filter(u => u.created_at.slice(0, 10) <= date).length;
    const dau = Math.round(population * (0.26 + 0.1 * Math.sin(i * 0.45) + i / 1400));
    return { date, dau, wau: Math.min(population, dau * 3), mau: population, moving_avg_7d: Math.round(population * 0.27), churn_rate: round(6 + 2 * Math.cos(i * 0.3)), revenue: round(dau * 2.4), renewals: Math.round(dau * 0.45) };
  });
}

export function overview(params = {}) {
  const rows = scoped(params);
  const active = rows.filter(u => u.status === 'active');
  const cancelled = rows.filter(u => u.status === 'cancelled');
  const failed = rows.filter(u => u.status === 'billing_failed');
  const trial = rows.filter(u => u.status === 'trial');
  const trend = dailySeries(params);
  const count = rows.length;
  return {
    generated_at: timestamp, data_anchor: seed.end_date, usage_data_anchor: seed.end_date,
    filters_applied: { start_date: params.start_date || seed.start_date, end_date: params.end_date || seed.end_date, service_id: params.service_id || null },
    users: { total: count, active: active.length, inactive: count - active.length, new_last_30_days: rows.filter(u => u.created_at >= '2025-10-01').length, channel_counts: { web: rows.filter(u => u.channel === 'web').length, ussd: rows.filter(u => u.channel === 'ussd').length, unknown: 0 } },
    subscriptions: { total: count, total_with_pending: count, active: active.length, billing_failed: failed.length, cancelled: cancelled.length, pending: trial.length, active_users: active.length, at_risk_users: failed.length, new_last_30_days: rows.filter(u => u.created_at >= '2025-10-01').length, trial: trial.length, expired: cancelled.length, conversion_rate_pct: pct(active.length + failed.length, count) },
    churn: { total: cancelled.length, voluntary: cancelled.length, technical: 0, voluntary_pct: cancelled.length ? 100 : 0, technical_pct: 0, churn_rate_month_pct: pct(cancelled.length, count), churn_rate_month_base: count, dropoff: { day1: 3, day2: 2, day3: 1 } },
    revenue: { total_revenue: round(sum(rows, 'revenue')), mrr: round(sum(active, 'revenue')), arpu_current_month: round(mean(active, 'revenue')), billing_success: active.length, billing_failed: failed.length, failed_pct: pct(failed.length, count) },
    engagement: { dau_today: trend.at(-1)?.dau || 0, wau_current_week: trend.at(-1)?.wau || 0, mau_current_month: count, max_dau_period: Math.max(0, ...trend.map(x => x.dau)), avg_dau_period: round(mean(trend, 'dau')), active_7d_users: active.length, inactivity_rate_pct: pct(count - active.length, count), inactive_7d_count: count - active.length, engagement_score: count ? 73 : 0, engagement_level: count ? 'HIGH' : 'LOW', stickiness_pct: pct(trend.at(-1)?.dau || 0, count), trend },
    sms: { total_services: seed.services.length, total_templates: 12, templates_per_service: 3, otp_templates_pct: 35, activation_templates_pct: 65, otp_rate_trend_pct: 4, activation_rate_trend_pct: 7 },
    top_services: seed.services.filter(s => !params.service_id || s.id === params.service_id).map(s => {
      const members = rows.filter(u => u.service_id === s.id);
      const cancelled = members.filter(u => u.status === 'cancelled').length;
      return { name: s.name, total: members.length, active_subs: members.filter(u => u.status === 'active').length, active_users: members.filter(u => u.status === 'active').length, billing_failed: members.filter(u => u.status === 'billing_failed').length, cancelled, churned_subs: cancelled, churn_rate_pct: pct(cancelled, members.length) };
    }),
  };
}

export function activity(params) {
  const o = overview(params);
  const rows = scoped(params);
  return {
    data_anchor: seed.end_date, kpi_anchor: timestamp, kpi_mode: 'period', filters_applied: o.filters_applied,
    kpis: { ...o.engagement, avg_wau_period: round(mean(dailySeries(params), 'wau')), avg_mau_period: round(mean(dailySeries(params), 'mau')), period_stickiness_pct: o.engagement.stickiness_pct, scoped_users_count: rows.length, active_users_period: rows.length, inactive_count: o.users.inactive, avg_lifetime_days: round(mean(rows, 'activities') * 2) },
    dau_trend: dailySeries(params),
    activity_heatmap: Array.from({ length: 7 * 24 }, (_, i) => ({ day: Math.floor(i / 24), hour: i % 24, count: Math.round(rows.length * (0.01 + 0.04 * Math.max(0, Math.sin((i % 24 - 8) / 5)))) })),
    user_growth: ['2025-09', '2025-10'].map(month => ({ month, nouveaux: rows.filter(u => u.created_at.startsWith(month)).length, 'churn\u00e9s': rows.filter(u => u.created_at.startsWith(month) && u.status === 'cancelled').length })),
    by_service: o.top_services.map(s => ({ ...s, service_name: s.name, subscriptions: s.total, trial_users: rows.filter(u => u.service_name === s.name && u.status === 'trial').length, inactive_7d: s.total - s.active_users, inactive_30d: s.cancelled, avg_lifetime_days: 24, stickiness_pct: 32 })),
    inactivity_buckets: ['1-7 days', '8-14 days', '15-30 days', '30+ days'].map((bucket, i) => ({ bucket, count: rows.filter(u => Math.min(3, Math.floor((30 - u.activities) / 8)) === i).length })),
  };
}

export function segmentation(params) {
  const rows = scoped(params);
  const distribution = seed.segments.map(s => {
    const members = rows.filter(u => u.segment === s.name);
    return { name: s.name, count: members.length, percentage: pct(members.length, rows.length) };
  });
  const dominant = [...distribution].sort((a, b) => b.count - a.count)[0];
  return {
    kpis: { total_segments: distribution.filter(d => d.count).length, dominant_segment: dominant?.name || 'None', dominant_pct: dominant?.percentage || 0, high_value_segment: 'Power Users', arpu_premium: 32, risk_segment: 'Trial Only', risk_churn_rate: 78 },
    clusters: { distribution, clusters: rows.map(u => ({ x: u.activities, y: u.revenue * (1 - u.churn_risk), segment: u.segment })) },
    profiles: { profiles: seed.segments.map(s => ({ segment: s.name, avg_duration: `${s.activity}d`, active_days_30d: s.activity, activity_ratio_30d: round(s.activity / 30 * 100), arpu: round(mean(rows.filter(u => u.segment === s.name), 'revenue')), churn_rate: s.risk * 100 })) },
  };
}

export function cohorts(params) {
  const rows = scoped(params);
  return ['2025-09', '2025-10'].flatMap((month, index) => seed.services.filter(s => !params.service_id || s.id === params.service_id).map((s, i) => {
    const members = rows.filter(u => u.service_id === s.id && u.created_at.startsWith(month));
    const d7 = members.length ? 42 + i * 6 + index * 3 : 0;
    return { cohort: month, cohort_date: month + '-01', service: s.name, service_name: s.name, total_users: members.length, d0: members.length ? 100 : 0, d7, d14: round(d7 * 0.78), d30: round(d7 * 0.56), retention_d7: d7, retention_d14: round(d7 * 0.78), retention_d30: round(d7 * 0.56), health: 'good' };
  }));
}
