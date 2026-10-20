import { seed, scoped, dailySeries, overview, cohorts, mean, sum, pct, round, serviceFor, timestamp } from './model.js';

export function trial(params) {
  const rows = scoped(params);
  const active = rows.filter(u => u.trial_status === 'active').length;
  const converted = rows.filter(u => u.trial_status === 'converted').length;
  const dropped = rows.length - active - converted;
  return { total_trials: rows.length, conversion_rate: pct(converted, rows.length), avg_duration: 3, dropoff_j3: pct(dropped, rows.length), trial_only_users: active, trial_only_rate: pct(active, rows.length), active_trials: active, converted_trials: converted, cancelled_trials: dropped, dropped_trials: dropped };
}

export function churn(params) {
  const rows = scoped(params);
  const o = overview(params);
  const count = o.churn.total;
  const trend = dailySeries(params);
  return {
    meta: { period_start: params.start_date || seed.start_date, period_end: params.end_date || seed.end_date },
    kpis: {
      global_churn_rate: { rate: pct(count, rows.length), churned: count, total: rows.length },
      monthly_churn_rate: { rate: pct(count, rows.length), churned: count, total: rows.length },
      trial_churn: { rate: pct(count, rows.length), count, total: count },
      avg_lifetime_days: { avg_days: 27 },
      churn_breakdown: { voluntary: { rate: 75, count: Math.round(count * 0.75) }, technical: { rate: 25, count: count - Math.round(count * 0.75) } },
    },
    charts: {
      daily_trend: trend.map((d, i) => ({ date: d.date, churned: rows.filter(u => u.status === 'cancelled' && u.created_at.slice(0, 10) === d.date).length, new_subs: rows.filter(u => u.created_at.slice(0, 10) === d.date).length, voluntary: i % 3, technical: i % 2 })),
      churn_curve: Array.from({ length: 14 }, (_, i) => ({ day: i + 1, trial: round(100 * (1 - Math.exp(-i / 12))), paid: round(100 * (1 - Math.exp(-i / 35))) })),
      by_service: o.top_services.map(s => ({ service_name: s.name, churned: s.cancelled, churn_rate: s.churn_rate_pct, trial_churn: Math.round(s.cancelled * 0.6), paid_churn: Math.round(s.cancelled * 0.4) })),
      reasons: [{ reason: 'Low engagement', count: Math.round(count * 0.6), churn_type: 'VOLUNTARY' }, { reason: 'Billing issue', count: count - Math.round(count * 0.6), churn_type: 'TECHNICAL' }],
      time_to_churn: ['0-3 days', '4-7 days', '8-14 days', '15-30 days'].map((bucket, i) => ({ bucket, count: Math.max(0, count - i * 2), voluntary: Math.max(0, count - i * 3), technical: i })),
      lifetime_distribution: ['0-3 days', '4-7 days', '8-14 days', '15-30 days'].map((bucket, i) => ({ bucket, count: rows.filter(u => Math.min(3, Math.floor(u.activities / 8)) === i).length })),
    },
  };
}

export function campaigns(params) {
  const rows = seed.campaigns.filter(c => (!params.service_id || c.service_id === params.service_id) && (!params.start_date || c.end_date >= params.start_date) && (!params.end_date || c.start_date <= params.end_date));
  const items = rows.map(c => ({ ...c, campaign_name: c.name, service_name: serviceFor(c.service_id).name, status: 'completed', total_targeted: c.targeted, total_subscriptions: c.subscriptions, total_messages_sent: c.targeted, messages_sent: c.targeted, messages_delivered: c.delivered, conversion_rate: pct(c.subscriptions, c.targeted), conversion_rate_pct: pct(c.subscriptions, c.targeted), delivery_rate: pct(c.delivered, c.targeted), revenue: round(c.subscriptions * serviceFor(c.service_id).price), attributed_subscriptions: c.subscriptions }));
  const sent = sum(rows, 'targeted');
  const subs = sum(rows, 'subscriptions');
  return {
    campaigns: items,
    dashboard: {
      kpis: { total_campaigns: rows.length, active_campaigns: 0, total_targeted: sent, qualified_targeted: sent, total_messages_sent: sent, total_messages_delivered: sum(rows, 'delivered'), total_subscriptions: subs, avg_conversion_rate: pct(subs, sent), overall_conversion_rate: pct(subs, sent), conversion_rate: pct(subs, sent), subscriptions_per_1000_sms: sent ? round(subs / sent * 1000) : 0, total_revenue: round(sum(items, 'revenue')), attribution_window_days: 7 },
      data_quality: { quality_score: 96, quality_status: 'excellent', target_coverage_pct: 100, sms_coverage_pct: 100, delivery_success_pct: pct(sum(rows, 'delivered'), sent) },
      charts: { by_type: ['acquisition', 'retention', 'reactivation'].map(type => ({ campaign_type: type, total_campaigns: rows.filter(c => c.campaign_type === type).length, total_targeted: sum(rows.filter(c => c.campaign_type === type), 'targeted'), total_subscriptions: sum(rows.filter(c => c.campaign_type === type), 'subscriptions'), conversion_rate: pct(sum(rows.filter(c => c.campaign_type === type), 'subscriptions'), sum(rows.filter(c => c.campaign_type === type), 'targeted')) })), monthly_trend: items.map(c => ({ month: c.start_date.slice(0, 7), campaign_type: c.campaign_type, targeted: c.targeted, subscriptions: c.subscriptions, conversion_rate: c.conversion_rate, total_targeted: c.targeted, total_subscriptions: c.subscriptions })), top_campaigns: items },
    },
  };
}

export function crossService(params) {
  const rows = scoped(params);
  const services = seed.services.filter(s => !params.service_id || s.id === params.service_id);
  const count = Math.floor(rows.length * 0.25);
  return {
    overview: { multi_service_users: count, multi_service_rate: pct(count, rows.length), top_combo: { service_a: services[0]?.name || '-', service_b: services[1]?.name || '-', count: Math.floor(count * 0.6) }, cross_retention_rate: 68, mono_retention_rate: 43, arpu_multi: 14.9, arpu_mono: round(mean(rows, 'revenue')) },
    co_subscriptions: { matrix: services.flatMap((a, i) => services.map((b, j) => ({ service_a: a.name, service_b: b.name, co_count: i === j ? 0 : Math.floor(count / (1 + Math.abs(i - j))), rate: i === j ? 0 : round(25 / (1 + Math.abs(i - j))) }))) },
    migrations: { migrations: services.slice(0, -1).map((s, i) => ({ from_service: s.name, to_service: services[i + 1].name, user_count: Math.floor(count / (i + 2)), migration_rate: round(8 / (i + 1)) })) },
    distribution: { distribution: [1, 2].map(nb_services => ({ nb_services, user_count: nb_services === 1 ? rows.length - count : count, percentage: pct(nb_services === 1 ? rows.length - count : count, rows.length) })) },
  };
}

export function retention(params) {
  const data = cohorts(params);
  const best = [...data].sort((a, b) => b.d7 - a.d7)[0];
  return {
    kpis: { avg_retention_d7: round(mean(data, 'd7')), avg_retention_d30: round(mean(data, 'd30')), best_cohort: best?.cohort || null, best_cohort_d7: best?.d7 || 0, at_risk_count: data.filter(c => c.d7 < 30).length, total_cohorts: data.length },
    heatmap: { data },
    curve: { data: seed.services.filter(s => !params.service_id || s.id === params.service_id).map(s => ({ service: s.name, d0: 100, d7: round(mean(data.filter(c => c.service === s.name), 'd7')), d14: round(mean(data.filter(c => c.service === s.name), 'd14')), d30: round(mean(data.filter(c => c.service === s.name), 'd30')) })) },
  };
}

export function anomalies(params) {
  const services = seed.services.filter(s => !params.service_id || s.id === params.service_id);
  const items = services.flatMap((s, i) => [8, 20, 38].map((offset, j) => {
    const metric = ['dau', 'revenue', 'churn_rate'][j];
    return { id: `demo-anomaly-${i}-${j}`, date: new Date(Date.parse(seed.start_date) + offset * 86400000).toISOString().slice(0, 10), service_id: s.id, service_name: s.name, metric, severity: ['high', 'medium', 'critical'][j], observed_value: j === 2 ? 16 : 30 + i * 9, expected_value: j === 2 ? 8 : 18 + i * 7, z_score: 3.4 + i * 0.3, status: 'open', description: 'Illustrative deviation in synthetic data', direction: j === 1 ? 'positive' : 'negative' };
  })).filter(a => (!params.start_date || a.date >= params.start_date) && (!params.end_date || a.date <= params.end_date) && (!params.metrics || params.metrics.split(',').includes(a.metric)) && (!params.severity || params.severity.split(',').includes(a.severity)));
  return {
    items,
    summary: { anomalies_detected: items.length, critical_alerts: items.filter(a => a.severity === 'critical').length, unresolved: items.length, most_affected_service: { name: services[0]?.name || '-', anomaly_count: 3 }, last_detection: { run_at: timestamp, next_run: null }, trend_vs_previous: 2 },
    timeline: { series: ['dau', 'revenue', 'churn_rate'].map(metric => ({ metric, points: dailySeries(params).map(d => ({ date: d.date, value: d[metric] })) })), anomalies: items },
    distribution: { severity_distribution: Object.fromEntries(['critical', 'high', 'medium'].map(s => [s, items.filter(a => a.severity === s).length])), metric_distribution: Object.fromEntries(['dau', 'revenue', 'churn_rate', 'renewals'].map(m => [m, items.filter(a => a.metric === m).length])) },
    heatmap: { weeks: ['Sep W2', 'Sep W4', 'Oct W2'], services: services.map(s => ({ service_name: s.name, cells: ['Sep W2', 'Sep W4', 'Oct W2'].map((week, i) => ({ week, severity_score: i + 1, count: 1 })) })) },
    insights: { items: services.map((s, i) => ({ id: `insight-${i}`, title: `${s.name}: onboarding opportunity`, severity: 'medium', description: 'Synthetic activity suggests an opportunity to improve the welcome journey.', explanation: 'Compare engagement before and after the sample campaign.', recommended_action: 'Test a targeted welcome message.', recommendation: 'Test a targeted welcome message.', service_name: s.name, metric: 'dau', impact: 'Illustrative insight', confidence: 0.87 })) },
  };
}
