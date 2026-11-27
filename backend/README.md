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
- NumPy
- pandas
- scikit-learn
- joblib

## Architecture

The backend follows a modular monolith architecture with separation of responsibilities.

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── db/
│   └── modules/
│       ├── credit_scoring/
│       │   ├── api/
│       │   ├── models/
│       │   ├── repositories/
│       │   ├── schemas/
│       │   └── services/
│       └── dashboard/
│           ├── api/
│           ├── schemas/
│           └── services/
├── ml/
│   ├── data/
│   │   └── raw/
│   ├── inference/
│   ├── models/
│   ├── tests/
│   └── training/
├── alembic/
├── tests/
└── requirements.txt
```

The `app/` directory contains the application API and business logic.

The independent `ml/` directory contains experimental model training, evaluation, and local inference code. It is not currently connected to the application assessment workflow.

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

python -m pip install --upgrade pip
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
DATABASE_URL=postgresql+psycopg://banking_user:YOUR_PASSWORD@localhost:5432/banking_db
TEST_DATABASE_URL=postgresql+psycopg://banking_user:YOUR_PASSWORD@localhost:5432/banking_test_db
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

The application currently uses a rule-based assessment engine implemented in `AssessmentService`.

It evaluates application and customer financial data, including:

- Monthly income
- Existing monthly debt payments
- Requested loan amount
- Loan term
- Employment information

The assessment produces a credit score, synthetic risk indicators, and assessment features.

Important limitations:

- The active application scoring engine is rule-based, not ML-based.
- Probability of Default (PD) is synthetic and not calibrated against historical default data.
- Estimated monthly payments exclude interest and use principal-only calculations.
- Assessment results are intended for demonstration and educational purposes.

A customer must have a complete financial profile before an assessment can be run.

The independent experimental ML pipeline does not replace or modify `AssessmentService`.

## Experimental Machine Learning Pipeline

The backend includes an independent experimental ML pipeline under `ml/`.

The experiment uses the Kaggle Give Me Some Credit dataset:

- Dataset size: 150,000 records.
- Target: `SeriousDlqin2yrs`.
- Target meaning: serious delinquency within two years.
- Input features: 8 numerical credit-history and financial indicators.
- Stratified train/validation/test split:
  - Training: 90,000 records (60%).
  - Validation: 30,000 records (20%).
  - Test: 30,000 records (20%).

The raw dataset must be placed at:

```text
ml/data/raw/cs-training.csv
```

The raw dataset is excluded from Git.

### Models and Evaluation

Two candidate models are evaluated:

- Logistic Regression
- Random Forest

Model selection is based on validation PR-AUC. The classification threshold is selected using validation F1.

Random Forest was selected for the current experiment.

Test-set metrics:

| Metric | Result |
|---|---:|
| ROC-AUC | 0.8584 |
| PR-AUC | 0.3879 |
| Precision | 0.4072 |
| Recall | 0.4618 |
| F1-score | 0.4328 |
| Selected threshold | 0.70 |

Test metrics were calculated using a model fitted on the training split only. After model selection, the final model artifact was refitted using the training and validation splits.

The model scores are not calibrated probabilities of default. The dataset target and population do not necessarily represent the outcomes or population of this application's credit products.

### Training

Run from the `backend` directory:

```bash
.venv/bin/python -m ml.training.train
```

The training script:

1. Validates the dataset.
2. Creates stratified training, validation, and test splits.
3. Trains Logistic Regression and Random Forest candidates.
4. Selects the classification threshold using validation F1.
5. Selects the model using validation PR-AUC.
6. Evaluates the selected candidate on the independent test split.
7. Refits the selected model on training and validation data.
8. Saves the model artifact and evaluation metadata.

### Inference

The local inference module is available under `ml/inference/`.

Run inference tests:

```bash
.venv/bin/python -m pytest ml/tests/test_predictor.py -v
```

The inference module validates input features and returns a historical-event score, classification threshold, and binary prediction.

The returned score is not a calibrated probability of default.

### Model Artifacts

Generated model artifacts are saved under `ml/models/`.

- `comparison_metrics.json` — model comparison results, metadata, and evaluation metrics.
- `random_forest.joblib` — selected trained model artifact.

Raw datasets and generated model binaries are excluded from Git. Evaluation metadata is tracked in the repository.

The inference module requires the locally generated model artifact and metadata. It is not a deployed prediction service.

### Feature Compatibility Limitations

The experimental dataset does not map directly to the current application customer profile.

Only `MonthlyIncome` has a directly compatible field in the current customer model.

The following dataset features are not currently available in the application:

- Revolving credit utilization.
- Historical delinquency indicators.
- Number of open credit lines.
- Number of real estate loans.

Dataset `DebtRatio` is not equivalent to the application's debt-to-income ratio. These features must not be substituted with unrelated application fields or arbitrary default values.

The experimental model is not integrated into the REST API, database, or `AssessmentService`.

Connecting this model to the application would require suitable feature data, domain validation, and additional model evaluation.

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

Run ML inference tests separately:

```bash
.venv/bin/python -m pytest ml/tests/test_predictor.py -v
```

The ML inference tests require the locally generated model artifact and metadata.

## Code Quality

Run Ruff checks:

```bash
ruff check .
ruff format --check .
```

## Scope and Limitations

The backend implements the core MVP API for customer management, credit applications, assessments, decisions, and dashboard statistics.

The experimental ML pipeline is a separate research component and does not affect application scoring or credit decisions.

The project is not a production banking system and does not provide validated credit risk predictions. No model in this project should be used to make real lending decisions.
