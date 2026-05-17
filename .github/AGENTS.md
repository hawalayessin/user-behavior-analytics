# Agent Notes

## Project layout
- Frontend (Vite/React): analytics-platform-front/
- Backend (FastAPI): user-analytics-backend/
- Docs: docs/

## Common commands
- Frontend: `npm run dev`, `npm run build`, `npm run lint`, `npm run preview` (from analytics-platform-front/package.json)
- Backend: `make dev`, `make test`, `make lint`, `make format`, `make migrate`, `make seed`, `make etl` (from user-analytics-backend/Makefile)

## Containers / env
- Docker Compose defines backend, frontend, and redis only (no DB service): docker-compose.yml
- Frontend proxy target in compose: `VITE_PROXY_TARGET=http://analytics_backend:8000`

## Key docs
- Architecture overview: docs/architecture.md
- ETL guidance: docs/etl_prod_readme.md
- Backend setup: user-analytics-backend/README.md

## Known pitfalls
- docs/architecture.md mentions a Postgres container, but docker-compose.yml does not define one.
- docs/etl_prod_readme.md command examples omit script paths; prefer `make etl` from user-analytics-backend/Makefile.
- user-analytics-backend/README.md references a different frontend folder name; actual folder is analytics-platform-front/.
