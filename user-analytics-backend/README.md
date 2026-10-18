# User Analytics Platform - PFE DigMaco

## Stack
- Backend: FastAPI + PostgreSQL + Alembic + SQLAlchemy
- Frontend: React + Vite
- ETL: Python scripts (prod_db -> analytics_db)

## Setup

### Backend
```bash
cp .env.example .env
pip install -r requirements-dev.txt
python scripts/init_demo_database.py --confirm-empty-demo

make dev
```

### Frontend
```bash
cd ../analytics-platform-front
cp .env.example .env
npm install
npm run dev
```

## Commandes utiles
| Commande | Action |
|----------|--------|
| make dev | Lancer FastAPI |
| python scripts/init_demo_database.py --confirm-empty-demo | Appliquer migrations |
|  | Seeder la base analytics |
| make etl | ETL prod_db -> analytics |
| make test | Tests unitaires |
| make lint | Verifier le code |


See the [root README](../README.md) for required secrets, isolated databases and CI.

The inherited migrations are not a fresh-database installer; see the root migration limitation.
