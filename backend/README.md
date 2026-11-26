
# Banking Project — Backend

REST API for the Banking Project, built with FastAPI and PostgreSQL.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2
- Pydantic v2
- Alembic
- PostgreSQL
- pytest
- Ruff

## Architecture

The backend follows a modular monolith architecture with separation of responsibilities.

```text
app/
├── api/
├── core/
├── db/
└── modules/
    └── credit_scoring/
        ├── api/
        ├── models/
        ├── repositories/
        ├── schemas/
        └── services/
```

## Requirements

- Python 3.12
- PostgreSQL
- pip

## Installation

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a local environment file:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

| Variable | Description |
|---|---|
| `APP_NAME` | Application name |
| `APP_VERSION` | Application version |
| `ENVIRONMENT` | Runtime environment |
| `API_V1_PREFIX` | API version prefix |
| `DATABASE_URL` | PostgreSQL connection string |
| `OLLAMA_BASE_URL` | Ollama API endpoint |
| `OLLAMA_MODEL` | Ollama model name |

## Database Migrations

Apply migrations:

```bash
alembic upgrade head
```

Check current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## API Modules

| Module | Description |
|---|---|
| Customers | Customer management |
| Applications | Credit application management |
| Assessments | Credit risk assessment records |
| Decisions | Credit decision management |

API endpoints are grouped under `/api/v1`.

## Testing

Run the test suite:

```bash
pytest -v
```

## Code Quality

Check code with Ruff:

```bash
ruff check .
ruff format --check .
```

## Development Status

The backend is under active development. ML-based credit scoring integration and additional banking functionality are planned.
