# InsightHub - User Behavior Analytics

An analytics platform for SMS subscription services: engagement, free-trial conversion, campaign performance, cohort retention, churn, cross-service behavior, and illustrative AI dashboards.

## Portfolio Demo

**Live demo: [insighthub-demo.vercel.app](https://insighthub-demo.vercel.app)**

The deployable demo source is on [`codex/portfolio-demo`](https://github.com/hawalayessin/user-behavior-analytics/tree/codex/portfolio-demo). This branch captures the current frontend and adds the isolated demo mode; the full backend remains available in the repository.

The public demo uses a small, synthetic dataset and runs entirely in the browser. No production database, private phone numbers, Redis instance, or external AI credentials are required.

- Dataset: [`analytics-platform-front/src/demo/data.json`](analytics-platform-front/src/demo/data.json), about 3 KB.
- 160 deterministic fictional subscriber records, four services, and four sample campaigns for September-October 2025.
- Interactive service/date filters, subscriber search, pagination, risk thresholds, theme switching, local analyst notes, and downloadable sample PDF reports.
- AI metrics, risk scores, anomalies, and cross-service scenarios are illustrative. The public demo does not train models, run ETL, send emails, or import files.
- Notes and generated-report history are stored only in the current browser session.

### Run the Demo

```sh
git switch codex/portfolio-demo
cd analytics-platform-front
npm ci
npm run dev:demo
```

### Build and Deploy

```sh
cd analytics-platform-front
npm run build:demo
npm run preview
```

For Vercel, select `analytics-platform-front` as the project root. The checked-in `vercel.json` builds the demo and enables direct links to React routes. See [Vercel's Vite documentation](https://vercel.com/docs/frameworks/frontend/vite).

`VITE_DEMO_MODE=true` is defined in `.env.demo`; ordinary `npm run dev` and `npm run build` continue to use the real FastAPI backend. Never put database credentials or secret API keys in `VITE_*` variables.

## Full Application

- Frontend: React, Vite, TanStack Query, Recharts, Tailwind CSS.
- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis.
- Analytics/ML: retention and campaign analytics, churn scoring, segmentation, anomaly detection, reporting.

Backend setup: [`user-analytics-backend/README.md`](user-analytics-backend/README.md).

## Demo Verification

The Python scripts in `tools/` require Playwright and its Chromium browser. Start the demo on port 5174 before running:

```sh
python tools/verify_demo.py http://127.0.0.1:5174
python tools/test_demo_interactions.py
```

These cover page rendering, service/date filtering, empty ranges, search, cursor and risk pagination, local notes, blocked backend-only operations, and PDF generation/download.
