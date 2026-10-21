# InsightHub - User Behavior Analytics

**Live demo: [insighthub-demo.vercel.app](https://insighthub-demo.vercel.app)**

An analytics platform for SMS subscription services, built with React, Vite, FastAPI, PostgreSQL and Redis. It covers user activity, free-trial conversion, campaign impact, retention, churn prediction, segmentation, anomaly detection and reporting.

## Public Portfolio Demo

The deployed demo runs entirely in the browser with a small synthetic dataset: 160 fictional subscribers, four services and four campaigns. No production database, private phone numbers or external AI credentials are exposed. AI metrics and predictions are illustrative; imports, ETL, email and model training require the full backend.

- [Open the live demo](https://insighthub-demo.vercel.app)
- [Demo source and setup instructions](https://github.com/hawalayessin/user-behavior-analytics/tree/codex/portfolio-demo)
- [Small demo dataset](https://github.com/hawalayessin/user-behavior-analytics/blob/codex/portfolio-demo/analytics-platform-front/src/demo/data.json)

The demo supports service/date filters, subscriber search, pagination, adjustable risk thresholds, local analyst notes, theme switching and downloadable sample PDF reports.



For Vercel, use `analytics-platform-front` as the root directory. The demo branch includes the build and SPA routing configuration. Vercel production tracks `codex/portfolio-demo`.

## Full Backend

See [user-analytics-backend/README.md](user-analytics-backend/README.md) for the full FastAPI application setup.
