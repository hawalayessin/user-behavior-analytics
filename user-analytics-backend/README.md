# User Analytics Platform - PFE DigMaco

## Stack
- Backend: FastAPI + PostgreSQL + Alembic + SQLAlchemy
- Frontend: React + Vite
- ETL: Python scripts (prod_db -> analytics_db)

## Setup

### Backend
```bash
cp .env.example .env
pip install -e .
make migrate
make seed
make dev
```

### Frontend
```bash
cd user-analytics-frontend
cp .env.example .env
npm install
npm run dev
```

## Commandes utiles
| Commande | Action |
|----------|--------|
| make dev | Lancer FastAPI |
| make migrate | Appliquer migrations |
| make seed | Seeder la base analytics |
| make etl | ETL prod_db -> analytics |
| make test | Tests unitaires |
| make lint | Verifier le code |

