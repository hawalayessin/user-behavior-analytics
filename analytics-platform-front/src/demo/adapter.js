import { AxiosError } from 'axios';
import { seed, scoped, subscribers, overview, activity, segmentation, cohorts, paginate, round, timestamp } from './model.js';
import { trial, churn, campaigns, crossService, retention, anomalies } from './analytics.js';

export const demoUser = { id: 'demo-admin', user_id: 'demo-admin', email: 'visitor@example.com', full_name: 'Portfolio Visitor', role: 'admin', is_active: true, created_at: timestamp, last_login_at: timestamp, avatar_url: null };
const session = { ...demoUser, access_token: 'portfolio-demo-session', token_type: 'bearer' };
const load = (key, fallback) => {
  try { return JSON.parse(sessionStorage.getItem(key)) || fallback; } catch { return fallback; }
};
let notes = load('insighthub:demo:notes', structuredClone(seed.notes));
let reports = load('insighthub:demo:reports', []);
const save = () => {
  sessionStorage.setItem('insighthub:demo:notes', JSON.stringify(notes));
  sessionStorage.setItem('insighthub:demo:reports', JSON.stringify(reports));
};
const fail = (status, detail) => { const e = new Error(detail); e.status = status; throw e; };
const metrics = {
  trained_at: timestamp, roc_auc: 0.91, pr_auc: 0.78, accuracy: 0.88, balanced_accuracy: 0.86,
  churn_rate: 0.2, n_samples: 160, n_positive: 32, n_negative: 128, precision: 0.81, recall: 0.83,
  coefficients: { days_since_last_activity: 0.84, nb_activities_7d: -0.56, nb_activities_30d: -0.43, billing_failures_30d: 0.72, days_since_first_charge: -0.19, avg_retention_d7: -0.61 }, report: {},
};

function userList(params, trialOnly = false) {
  let rows = scoped(params).filter(u => (!params.search || `${u.phone_number} ${u.full_name}`.toLowerCase().includes(params.search.toLowerCase())) && (!params.status || ['all', 'Tous'].includes(params.status) || (trialOnly ? u.trial_status : u.status) === params.status));
  rows = [...rows].sort((a, b) => b.created_at.localeCompare(a.created_at) || b.id.localeCompare(a.id));
  if (String(params.export) === 'true') return { data: rows, total: rows.length };
  if (params.cursor_id) rows = rows.slice(Math.max(0, rows.findIndex(u => u.id === params.cursor_id) + 1));
  const result = paginate(rows, params);
  const last = result.data.at(-1);
  return { ...result, has_more: result.data.length < rows.length, next_cursor: last && result.data.length < rows.length ? { id: last.id, created_at: last.created_at } : null };
}

async function pdfReport(report) {
  const { jsPDF } = await import('jspdf');
  const pdf = new jsPDF();
  const o = overview({ start_date: report.period_start, end_date: report.period_end });
  pdf.setFontSize(24); pdf.text('InsightHub | Portfolio Demo', 18, 25);
  pdf.setFontSize(11); pdf.text('Synthetic data. Illustrative AI insights. No live model training.', 18, 36);
  pdf.text(`Period: ${report.period_start} to ${report.period_end}`, 18, 46);
  pdf.setFontSize(16); pdf.text('Analytics Overview', 18, 65); pdf.setFontSize(12);
  [`Subscribers: ${o.users.total}`, `Active subscriptions: ${o.subscriptions.active}`, `Monthly recurring revenue: ${o.revenue.mrr} TND`, `Churn rate: ${o.churn.churn_rate_month_pct}%`, `Trial conversion: ${o.subscriptions.conversion_rate_pct}%`].forEach((line, i) => pdf.text(line, 18, 80 + i * 10));
  pdf.text('Services', 18, 145);
  o.top_services.forEach((s, i) => pdf.text(`${s.name}: ${s.total} subscribers, ${s.active_subs} active`, 18, 158 + i * 10));
  pdf.text('Illustrative recommendation', 18, 215);
  pdf.text(pdf.splitTextToSize('Focus onboarding reminders on occasional users. Compare campaign conversion by service and monitor retention before scaling.', 170), 18, 228);
  return pdf.output('blob');
}

export async function resolveDemoRequest(url, method = 'get', body = null, query = {}) {
  const parsed = new URL(url, 'https://demo.invalid');
  const path = parsed.pathname.replace(/^\/api(?=\/)/, '').replace(/\/$/, '');
  const params = { ...Object.fromEntries(parsed.searchParams), ...(query instanceof URLSearchParams ? Object.fromEntries(query) : query) };
  const verb = method.toLowerCase();
  const payload = typeof body === 'string' ? JSON.parse(body || '{}') : body || {};
  if (['/auth/login', '/auth/refresh'].includes(path)) return session;
  if (path === '/auth/logout') return { message: 'Signed out' };
  if (path === '/auth/me') return demoUser;
  if (path === '/notes') {
    if (verb === 'post') {
      const note = { ...payload, id: `demo-note-${Date.now()}`, analyst_id: demoUser.id, analyst_name: demoUser.full_name, created_at: new Date().toISOString(), updated_at: new Date().toISOString() };
      notes = [note, ...notes]; save(); return note;
    }
    return notes.filter(n => (!params.service_id || n.service_id === params.service_id) && (!params.metric || n.metric === params.metric));
  }
  if (path.startsWith('/notes/') && ['put', 'delete'].includes(verb)) {
    const id = path.split('/').at(-1);
    notes = verb === 'delete' ? notes.filter(n => n.id !== id) : notes.map(n => n.id === id ? { ...n, ...payload, updated_at: new Date().toISOString() } : n);
    save(); return notes.find(n => n.id === id) || { message: 'Deleted from this demo session' };
  }
  if (path === '/reports/generate' && verb === 'post') {
    const id = `demo-report-${Date.now()}`;
    reports = [{ ...payload, id, report_id: id, status: 'success', progress_pct: 100, current_step: 'Demo PDF ready', created_at: new Date().toISOString(), filename: `${id}.pdf`, file_size: 4096, ai_model: 'Illustrative demo insights' }, ...reports].slice(0, 20);
    save(); return { report_id: id };
  }
  if (path === '/reports/history') return reports;
  if (path.startsWith('/reports/status/')) return reports.find(r => r.id === path.split('/').at(-1)) || fail(404, 'Demo report not found');
  if (path.startsWith('/reports/download/')) return pdfReport(reports.find(r => r.id === path.split('/').at(-1)) || fail(404, 'Demo report not found'));
  if (verb !== 'get') fail(403, 'Portfolio demo: this action requires the full backend. No import, email or model training is performed.');
  if (['/services', '/admin/management/services'].includes(path)) return seed.services;
  if (path === '/admin/management/campaigns') return campaigns({}).campaigns;
  if (path === '/notifications/anomalies') return { notifications: [], unread_count: 0 };
  if (['/analytics/overview', '/analytics/summary'].includes(path)) return overview(params);
  if (path === '/analytics/user-activity') return activity(params);
  if (path === '/analytics/nrr') {
    const o = overview(params);
    return { nrr_percent: 108.2, revenue_start: o.revenue.mrr, revenue_current: round(o.revenue.mrr * 1.082), revenue_renewed: round(o.revenue.mrr * 0.95), revenue_churned: round(o.revenue.mrr * 0.05), revenue_expansion: round(o.revenue.mrr * 0.132), period_label: 'September - October 2025 (demo)', calculated_at: timestamp, is_available: o.users.total > 0 };
  }
  if (['/users', '/users/trial'].includes(path)) return userList(params, path.endsWith('/trial'));
  if (/^\/users\/[^/]+\/detail$/.test(path)) {
    const u = subscribers.find(u => u.id === path.split('/')[2]) || fail(404, 'Demo subscriber not found');
    return { user: u, subscriptions: [{ ...u, service: u.services[0], start_date: u.created_at, since_days: 30, total_paid: u.revenue, is_trial: u.status === 'trial' }], activities: [{ activity_type: u.activity_type, activity_date: u.last_activity_at, service_name: u.service_name }], billing_events: [], unsubscriptions: [], sms_events: [] };
  }
  if (path.startsWith('/analytics/segmentation/')) return segmentation(params)[path.split('/').at(-1)] || fail(404, 'Unknown demo segmentation endpoint');
  if (path === '/analytics/trial/kpis') return trial(params);
  if (path === '/analytics/trial/dropoff-by-day') return { day1: 4, day2: 3, day3: 2 };
  if (path === '/analytics/trial/dropoff-causes') return { summary: { total_dropoffs: 9, early_dropoffs_3d: 9, early_dropoff_rate_pct: 100, technical_dropoffs: 3, technical_share_pct: 33.3, voluntary_dropoffs: 6, voluntary_share_pct: 66.7 }, cause_breakdown: [{ cause: 'Low engagement', count: 6, pct: 66.7 }, { cause: 'Billing issue', count: 3, pct: 33.3 }], top_reasons: [{ reason: 'No activity during trial', count: 6 }], management_notes: ['Illustrative finding: introduce a welcome reminder before trial expiration.'] };
  if (path === '/analytics/churn/dashboard') return churn(params);
  if (path.includes('/reactivation/kpis')) return { reactivation_rate: 18.5, reactivated_users: 8, eligible_users: 43 };
  if (path.includes('/reactivation/by-service')) return seed.services.map((s, i) => ({ service_name: s.name, reactivated_users: i + 1, reactivation_rate: 12 + i * 4 }));
  if (path.startsWith('/analytics/retention/')) {
    const key = path.split('/').at(-1);
    return key === 'cohorts-list' ? paginate(cohorts(params), params) : retention(params)[key] || fail(404, 'Unknown demo retention endpoint');
  }
  if (path === '/analytics/cross-service/all') return crossService(params);
  if (path === '/analytics/campaigns/dashboard') return campaigns(params).dashboard;
  if (path === '/analytics/campaigns/list') {
    const result = paginate(campaigns(params).campaigns, params);
    return { ...result, campaigns: result.data, limit: result.page_size, pages: result.total_pages };
  }
  if (/^\/analytics\/campaigns\/[^/]+$/.test(path)) return campaigns({}).campaigns.find(c => c.id === path.split('/').at(-1)) || fail(404, 'Demo campaign not found');
  if (path === '/ml/churn/metrics') return metrics;
  if (path === '/ml/churn/governance') return { trained_at: timestamp, evaluation_protocol: 'Synthetic portfolio illustration; no live training', retrain_required: false, days_since_training: 0, calibration: { brier_score: 0.082, ece: 0.043 }, drift: { features: Object.keys(metrics.coefficients).map(feature => ({ feature, train_mean: 12, current_mean: 12.4, z_shift: 0.08, severity: 'low' })) }, learning_curve: [30, 60, 90, 120, 160].map((n, i) => ({ train_size: n, train_score: round(0.95 - i * 0.008, 3), val_score: round(0.85 + i * 0.015, 3), train_score_std: 0.01, val_score_std: 0.015 })), overfitting_diagnosis: { detected: false, message: 'Illustrative learning curve from synthetic data' } };
  if (path === '/ml/churn/scores') {
    const rows = scoped(params).filter(u => ['active', 'billing_failed'].includes(u.status));
    const threshold = Number(params.threshold ?? 0.4);
    const risky = rows.filter(u => u.churn_risk >= threshold).sort((a, b) => b.churn_risk - a.churn_risk);
    const result = paginate(risky, params);
    return { ...result, generated_at: timestamp, threshold, top_users: result.data.map(u => ({ ...u, predicted_churn: Number(u.churn_risk >= threshold) })), active_users_scored: rows.length, distribution: ['Low', 'Medium', 'High'].map(risk_category => ({ risk_category, count: rows.filter(u => u.risk_category === risk_category).length })) };
  }
  if (path.startsWith('/anomalies/')) {
    const data = anomalies(params);
    const key = path.split('/').at(-1);
    if (key === 'details') return { items: data.items.slice(Number(params.offset || 0), Number(params.offset || 0) + Number(params.limit || 10)), total: data.items.length };
    return data[key] || fail(404, 'Unknown demo anomaly endpoint');
  }
  if (path === '/platform-users') return { items: [demoUser], users: [demoUser], data: [demoUser], total: 1, page: 1, stats: { total: 1, active: 1, inactive: 0, admins: 1, analysts: 0 } };
  if (['/admin/import/history', '/admin/import/etl-history'].includes(path)) return [];
  if (path.startsWith('/admin/import/schema/')) return { columns: [], required_columns: [] };
  if (path === '/analytics/status/diagnostics') return { status: 'demo', database: 'Synthetic JSON dataset', total_users: seed.subscriber_count };
  fail(404, `This endpoint is not available in the portfolio demo: ${path}`);
}

export async function demoAdapter(config) {
  try {
    const data = await resolveDemoRequest(config.url, config.method, config.data, config.params);
    return { data, status: 200, statusText: 'OK', headers: {}, config, request: null };
  } catch (cause) {
    const response = { data: { detail: cause.message }, status: cause.status || 500, statusText: 'Demo request failed', headers: {}, config };
    throw new AxiosError(cause.message, AxiosError.ERR_BAD_REQUEST, config, null, response);
  }
}

export function installDemoRuntime() {
  if (!sessionStorage.getItem('insighthub:demo:started')) {
    sessionStorage.removeItem('digmaco:get-cache:v1');
    sessionStorage.setItem('digmaco_access_token', session.access_token);
    localStorage.setItem('role', demoUser.role);
    localStorage.setItem('full_name', demoUser.full_name);
    localStorage.setItem('user_id', demoUser.id);
    localStorage.setItem('digmaco-theme', 'dark');
    sessionStorage.setItem('insighthub:demo:started', 'true');
  }
  const nativeFetch = window.fetch.bind(window);
  // Reports use fetch; only same-origin API requests enter the demo resolver.
  window.fetch = async (input, init = {}) => {
    const url = new URL(input instanceof Request ? input.url : input, window.location.href);
    if (url.origin !== window.location.origin || !url.pathname.startsWith('/api/')) return nativeFetch(input, init);
    try {
      const data = await resolveDemoRequest(url.href, init.method || 'get', init.body);
      return data instanceof Blob ? new Response(data, { headers: { 'Content-Type': data.type } }) : Response.json(data);
    } catch (cause) {
      return Response.json({ detail: cause.message }, { status: cause.status || 500 });
    }
  };
}
