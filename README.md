
# Banking Project

A modular banking application with a credit scoring system.

## Tech Stack

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Pydantic v2

### Frontend
- React 19
- TypeScript
- Vite
- Tailwind CSS 4
- React Router
- TanStack Query
- shadcn/ui

## Project Structure

```text
BankingProject/
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── data/
│   └── tests/
├── frontend/
│   └── src/
└── README.md
```

## Backend Setup

Requirements:
- Python 3.12
- PostgreSQL

```bash
cd backend

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Configure `DATABASE_URL` in `.env`, then run migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend development server: http://localhost:5173

## Quality Checks

Backend:

```bash
ruff check .
ruff format --check .
pytest -v
```

Frontend:

```bash
npm run lint
npm run build
```

## Current Scope

- Customer management
- Credit application management
- Credit scoring infrastructure
- Assessment and decision management
- REST API
- Dark minimal frontend interface

## Project Status

Under active development. Some frontend sections and ML-based scoring functionality are not yet implemented.
