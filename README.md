# Banking Project

A modular banking application built with Python, FastAPI, and React. The project includes backend infrastructure, customer and credit application management, rule-based credit risk assessment, credit decisions, and an independent experimental machine learning pipeline.

## Features

- Customer management with personal and financial profiles
- Credit application creation and management
- Rule-based credit risk assessment
- Credit assessment history
- Credit decision management
- Dashboard with application and customer statistics
- REST API with interactive Swagger documentation
- Experimental machine learning pipeline for credit risk research
- Local model training, evaluation, and inference

## Tech Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2
- Pydantic v2
- Alembic
- PostgreSQL
- NumPy
- pandas
- scikit-learn
- joblib
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

The project follows a modular monolith architecture with separation of responsibilities.

```text
BankingProject/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   └── modules/
│   │       ├── credit_scoring/
│   │       └── dashboard/
│   ├── ml/
│   │   ├── data/
│   │   ├── inference/
│   │   ├── models/
│   │   ├── tests/
│   │   └── training/
│   ├── tests/
│   ├── requirements.txt
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

The backend contains the application API, business logic, database infrastructure, and an independent experimental ML module.

The frontend provides the user interface for customer management, credit applications, assessments, decisions, and dashboard functionality.

The ML pipeline is currently independent of the application scoring workflow.

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
- Linux (development environment)

### Backend Setup

From the repository root:

```bash
cd backend

python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
```

Configure `DATABASE_URL` in `backend/.env` to point to your PostgreSQL database.

Apply database migrations:

```bash
alembic -x target=main upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Backend documentation: [backend/README.md](backend/README.md)

### Frontend Setup

Open another terminal from the repository root:

```bash
cd frontend

npm install
npm run dev
```

Frontend development server:

http://localhost:5173

Frontend documentation: [frontend/README.md](frontend/README.md)

## API

- API base URL: http://127.0.0.1:8000
- API prefix: `/api/v1`
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health
- Database health: http://127.0.0.1:8000/api/v1/health/db

The database health endpoint requires a running PostgreSQL instance and a valid `DATABASE_URL`.

## Testing and Quality Checks

### Backend

Run from the `backend` directory:

```bash
ruff check .
ruff format --check .
pytest -v
```

### ML Inference Tests

Run from the repository root:

```bash
backend/.venv/bin/python -m pytest backend/ml/tests/test_predictor.py -v
```

The ML inference tests require the locally generated model artifact and evaluation metadata.

### Frontend

Run from the `frontend` directory:

```bash
npx tsc --noEmit
npm run lint
npm run build
```

## Scoring Engine

The application currently uses a demonstration rule-based assessment engine implemented in `AssessmentService`.

- Model name: `rule_based_demo`
- Model version: `1.0`
- Assessment results are calculated using predefined business rules and scoring thresholds.
- Probability of Default (PD) values are synthetic indicators and are not calibrated against historical default data.
- Estimated monthly payments use principal-only calculations and exclude interest.

The rule-based assessment remains the active scoring mechanism in the application workflow.

Assessment results must not be treated as production-grade credit risk predictions or used for real lending decisions.

## Experimental Machine Learning Pipeline

An independent experimental machine learning pipeline is implemented under `backend/ml/`.

The pipeline focuses on model training, evaluation, comparison, and local inference using historical credit data.

### Dataset

The experiment uses the Kaggle Give Me Some Credit dataset.

- Dataset size: 150,000 records.
- Target: `SeriousDlqin2yrs`.
- Target meaning: serious delinquency within two years.
- Input features: 8 numerical credit-history and financial indicators.

The dataset is split using stratified sampling:

| Split | Records | Percentage |
|---|---:|---:|
| Training | 90,000 | 60% |
| Validation | 30,000 | 20% |
| Test | 30,000 | 20% |

The raw dataset is stored locally at:

`backend/ml/data/raw/cs-training.csv`

Raw datasets are excluded from Git.

### Models

Two classification models are evaluated:

- Logistic Regression
- Random Forest

Model selection is based on validation PR-AUC. The classification threshold is selected using validation F1.

Random Forest was selected for the current experiment.

### Evaluation Results

Test-set metrics for the selected Random Forest model:

| Metric | Result |
|---|---:|
| ROC-AUC | 0.8584 |
| PR-AUC | 0.3879 |
| Precision | 0.4072 |
| Recall | 0.4618 |
| F1-score | 0.4328 |
| Classification threshold | 0.70 |

Test metrics were calculated using a model fitted on the training split only.

After model selection, the final model artifact was refitted using the combined training and validation data (120,000 records).

The model scores are not calibrated probabilities of default. The dataset target and population do not necessarily represent the outcomes or population of this application's credit products.

### Training

From the repository root, run:

```bash
backend/.venv/bin/python -m backend.ml.training.train
```

The training pipeline:

1. Validates the input dataset.
2. Creates stratified training, validation, and test splits.
3. Trains Logistic Regression and Random Forest candidates.
4. Selects the classification threshold using validation F1.
5. Selects the model using validation PR-AUC.
6. Evaluates candidates on the independent test split.
7. Refits the selected model on training and validation data.
8. Saves the model artifact and evaluation metadata.

### Inference

The local inference module is implemented under `backend/ml/inference/`.

Run its tests:

```bash
backend/.venv/bin/python -m pytest backend/ml/tests/test_predictor.py -v
```

The inference module validates input features and returns:

- Model name and version
- Historical-event score
- Classification threshold
- Binary prediction
- Probability calibration status

The returned score must not be interpreted as a calibrated probability of default.

### Model Artifacts

Generated artifacts are stored under `backend/ml/models/`.

- `comparison_metrics.json` — model comparison results, metadata, and evaluation metrics.
- `random_forest.joblib` — selected trained model artifact.

Raw datasets and generated model binaries are excluded from Git. Evaluation metadata is tracked in the repository.

The inference module requires the locally generated model artifact and metadata. It is not a deployed prediction service.

### Feature Compatibility Limitations

The experimental dataset does not map directly to the current application customer profile.

Only `MonthlyIncome` has a directly compatible field in the existing customer model.

The following features are not currently available in the application:

- Revolving credit utilization
- Historical delinquency indicators
- Number of open credit lines
- Number of real estate loans

Dataset `DebtRatio` is not equivalent to the application's debt-to-income ratio.

Missing credit-history features must not be replaced with arbitrary defaults or values derived from unrelated application fields.

The experimental model is not integrated into the REST API, database, or `AssessmentService`.

Integration would require suitable feature data, domain validation, and additional model evaluation.

## Development Status

The core MVP workflow is implemented:

- Customers
- Applications
- Credit assessments
- Credit decisions
- Dashboard

An independent experimental machine learning pipeline is also available for research and model evaluation. It does not affect application scoring or credit decisions.

Dedicated standalone Credit Scoring, Decisions, AI Assistant, and Settings pages are currently placeholders. Assessment and decision functionality is available through application details.

The project is intended for educational and demonstration purposes, not production banking operations. No model in this project should be used to make real lending decisions.
