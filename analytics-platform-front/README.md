# DigMaco dashboard

React/Vite frontend of the [DigMaco Analytics PFE](../README.md), displaying
subscription activity, retention, churn, campaign analysis and generated reports.

Use Node.js 22+. Copy `.env.example` to `.env`, run `npm ci`, then `npm run dev`.
The default local backend target is http://127.0.0.1:8000. The Vite `/api` proxy
forwards requests to FastAPI; do not put backend secrets in VITE_* variables.

Run `npm run build` to verify compilation. Tests, architecture, database setup
and deployment limitations are documented in the repository root README.
