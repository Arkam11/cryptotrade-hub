up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v

rebuild:
	docker compose up --build -d

migrate:
	cd services/portfolio && POSTGRES_HOST=localhost POSTGRES_PORT=5433 poetry run alembic upgrade head

migrate-status:
	cd services/portfolio && POSTGRES_HOST=localhost POSTGRES_PORT=5433 poetry run alembic current

test-portfolio:
	cd services/portfolio && poetry run pytest tests/ -v --cov=app --cov-report=term-missing

logs:
	docker compose logs -f

.PHONY: up down reset rebuild migrate migrate-status test-portfolio logs
