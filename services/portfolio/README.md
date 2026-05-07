# Portfolio Service

FastAPI-based portfolio management service for CryptoTrade Hub.

Handles user authentication, asset holdings, and P&L tracking.

## Local Development

```bash
docker compose up --build -d
poetry run alembic upgrade head
```

## API Docs

Available at `http://localhost:8001/docs` when running locally.
