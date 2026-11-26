# Banking Project — Backend

REST API for the Banking Project, built with FastAPI, SQLAlchemy, and PostgreSQL.

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
│   └── v1/
├── core/
├── db/
└── modules/
    ├── credit_scoring/
    │   ├── api/
    │   ├── models/
    │   ├── repositories/
    │   ├── schemas/
    │   └── services/
    └── dashboard/
        ├── api/
        ├── schemas/
        └── services/
```

## Requirements

- Python 3.12
- PostgreSQL
- pip

## Installation

From the project root:

```bash
cd backend

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Create a local environment file:

```bash
cp .env.example .env
```

Configure the database connection in `.env`.

| Variable | Description |
|---|---|
| `APP_NAME` | Application name |
| `APP_VERSION` | Application version |
| `ENVIRONMENT` | Runtime environment |
| `API_V1_PREFIX` | API version prefix |
| `DATABASE_URL` | Main PostgreSQL database connection |
| `TEST_DATABASE_URL` | Separate test database connection |
| `OLLAMA_BASE_URL` | Reserved Ollama API endpoint configuration |
| `OLLAMA_MODEL` | Reserved Ollama model configuration |

Ollama settings are reserved for future integration. The current credit assessment workflow does not call an Ollama model.

## Database Setup

The project uses two PostgreSQL databases:

- `banking_db` — main application database
- `banking_test_db` — test database

Configure both connection strings as needed. The test database must be separate from the main database.

Example:

```env
DATABASE_URL=postgresql+psycopg://banking_user:password@localhost:5432/banking_db
TEST_DATABASE_URL=postgresql+psycopg://banking_user:password@localhost:5432/banking_test_db
```

Create the databases and PostgreSQL role before applying migrations.

## Database Migrations

The Alembic environment requires an explicit database target. This prevents migrations from being applied to the wrong database.

Apply migrations to the main database:

```bash
alembic -x target=main upgrade head
```

Apply migrations to the test database:

```bash
alembic -x target=test upgrade head
```

Check the current migration:

```bash
alembic -x target=main current
```

View migration history:

```bash
alembic history
```

Do not run `alembic upgrade head` without specifying a target.

## Running the API

Start the development server from the `backend` directory:

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
| Customers | Customer profiles and financial information |
| Applications | Credit application management |
| Assessments | Credit risk assessment records and rule-based scoring |
| Decisions | Credit decision management and decision history |
| Dashboard | Aggregated application and customer statistics |

API endpoints are grouped under `/api/v1`.

## Credit Assessment

The current assessment engine uses predefined rule-based scoring logic.

It evaluates application and customer financial data, including:

- Monthly income
- Existing monthly debt payments
- Requested loan amount
- Loan term
- Employment information

The assessment produces a credit score, estimated risk indicators, and assessment features.

Important limitations:

- The scoring engine is not a trained machine learning model.
- Probability of Default (PD) is synthetic and not calibrated against historical default data.
- Estimated monthly payments exclude interest and use principal-only calculations.
- Assessment results are intended for demonstration and educational purposes.

A customer must have a complete financial profile before an assessment can be run.

## Decisions

The decision workflow supports:

- `approved`
- `rejected`
- `manual_review`

Final decisions (`approved` and `rejected`) update the corresponding application status. A final decision cannot be recorded more than once for the same application.

## Testing

Configure `TEST_DATABASE_URL` and apply test database migrations before running the test suite.

```bash
alembic -x target=test upgrade head
pytest -v
```

## Code Quality

Run Ruff checks:

```bash
ruff check .
ruff format --check .
```

## Scope and Limitations

The backend implements the core MVP API for customer management, credit applications, assessments, decisions, and dashboard statistics.

It is not a production banking system and does not provide validated credit risk predictions.
