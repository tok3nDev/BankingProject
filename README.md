# Banking Project

A modular banking application for customer management, credit applications, credit risk assessment, and decision management.

The project implements an MVP credit workflow using a FastAPI backend and a React frontend.

## Features

- Customer management with personal and financial profiles
- Credit application creation and management
- Rule-based credit risk assessment
- Credit assessment history
- Credit decision management
- Dashboard with application and customer statistics
- REST API with interactive Swagger documentation

## Tech Stack

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2
- Pydantic v2
- Alembic
- PostgreSQL
- pytest
- Ruff

### Frontend
- React 19
- TypeScript 6
- Vite
- Tailwind CSS 4
- React Router 7
- TanStack Query 5
- Axios
- Recharts
- Lucide React
- shadcn/ui components

## Architecture

The project follows a modular monolith architecture.

```text
BankingProject/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   └── modules/
│   ├── tests/
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── lib/
│   │   └── types/
│   └── README.md
└── README.md
```

## MVP Workflow

1. Create a customer and provide their financial profile.
2. Create a credit application for that customer.
3. Open the application details.
4. Run a credit assessment.
5. Review the assessment result.
6. Record a credit decision.
7. Review the application status and decision history.
8. Monitor overall statistics on the dashboard.

Customer financial information can be updated through the customer profile.

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL
- Node.js
- npm

### Backend Setup

```bash
cd backend

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Configure `DATABASE_URL` in `backend/.env` to point to your PostgreSQL database.

Apply migrations:

```bash
alembic -x target=main upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Backend documentation: [backend/README.md](backend/README.md)

### Frontend Setup

Open another terminal:

```bash
cd frontend

npm install
npm run dev
```

Frontend development server: http://localhost:5173

Frontend documentation: [frontend/README.md](frontend/README.md)

## API

- API base URL: http://127.0.0.1:8000
- API prefix: `/api/v1`
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Testing and Quality Checks

Backend:

```bash
cd backend
ruff check .
ruff format --check .
pytest -v
```

Frontend:

```bash
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

## Scoring Engine Limitations

The current scoring implementation is a demonstration rule-based assessment system.

- It uses predefined business rules and scoring thresholds.
- It is not a trained or validated machine learning model.
- Probability of Default (PD) values are synthetic indicators and are not calibrated against historical default data.
- Estimated monthly payments use principal-only calculations and exclude interest.
- Assessment results must not be treated as production-grade credit risk predictions or used for real lending decisions.

Machine learning integration and model validation are outside the current MVP scope.

## Development Status

The core MVP workflow is implemented:

- Customers
- Applications
- Credit assessments
- Credit decisions
- Dashboard

Dedicated standalone Credit Scoring, Decisions, AI Assistant, and Settings pages are currently placeholders. Assessment and decision functionality is available through application details.

The project is intended for educational and demonstration purposes, not production banking operations.
