.PHONY: dev migrate seed test lint

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

seed:
	python scripts/seeder/seed_missing_data.py

seed-dry:
	python scripts/seeder/seed_missing_data.py --dry-run

test:
	pytest tests/ -v

lint:
	ruff check app/ scripts/
	black app/ scripts/ --check

format:
	black app/ scripts/
	ruff check app/ scripts/ --fix

etl:
	python scripts/etl/etl_prod_to_analytics.py

etl-fix:
	python scripts/etl/fix_services_mapping.py
