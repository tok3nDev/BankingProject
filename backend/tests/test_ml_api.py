import json
from pathlib import Path

import pytest
from app.main import app
from app.modules.ml import api as ml_api
from app.modules.ml.services import prediction as prediction_service
from app.modules.ml.services.prediction import ModelUnavailableError
from fastapi.testclient import TestClient


@pytest.fixture
def ml_client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_payload():
    return {
        "RevolvingUtilizationOfUnsecuredLines": 0.5,
        "NumberOfTime30-59DaysPastDueNotWorse": 0,
        "DebtRatio": 0.3,
        "MonthlyIncome": 5000,
        "NumberOfOpenCreditLinesAndLoans": 8,
        "NumberOfTimes90DaysLate": 0,
        "NumberRealEstateLoansOrLines": 1,
        "NumberOfTime60-89DaysPastDueNotWorse": 0,
    }


def test_ml_health_returns_model_status(
    ml_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    metadata = {
        "model_name": "random_forest",
        "model_version": "2.1.0",
    }

    (tmp_path / "comparison_metrics.json").write_text(
        __import__("json").dumps(metadata),
        encoding="utf-8",
    )
    (tmp_path / "random_forest.joblib").touch()

    monkeypatch.setattr(
        prediction_service,
        "get_model_dir",
        lambda: tmp_path,
    )

    response = ml_client.get("/api/v1/ml/health")

    assert response.status_code == 200

    data = response.json()
    assert data["metadata_available"] is True
    assert data["model_name"] == "random_forest"
    assert data["model_version"] == "2.1.0"
    assert data["model_available"] is True


def test_ml_model_info_returns_metrics(
    ml_client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    metadata = {
        "model_name": "random_forest",
        "model_version": "2.1.0",
        "dataset": "Give Me Some Credit",
        "dataset_rows": 150000,
        "features": [
            "RevolvingUtilizationOfUnsecuredLines",
            "NumberOfTime30-59DaysPastDueNotWorse",
            "DebtRatio",
            "MonthlyIncome",
            "NumberOfOpenCreditLinesAndLoans",
            "NumberOfTimes90DaysLate",
            "NumberRealEstateLoansOrLines",
            "NumberOfTime60-89DaysPastDueNotWorse",
        ],
        "target": "SeriousDlqin2yrs",
        "selected_threshold": 0.7,
        "probability_calibrated": False,
        "results": {
            "random_forest": {
                "selected_threshold": 0.7,
                "validation": {
                    "roc_auc": 0.856,
                    "pr_auc": 0.374,
                    "precision": 0.403,
                    "recall": 0.448,
                    "f1": 0.424,
                },
                "test": {
                    "roc_auc": 0.858,
                    "pr_auc": 0.388,
                    "precision": 0.407,
                    "recall": 0.462,
                    "f1": 0.433,
                },
            },
            "logistic_regression": {
                "selected_threshold": 0.7,
                "validation": {
                    "roc_auc": 0.854,
                    "pr_auc": 0.347,
                    "precision": 0.357,
                    "recall": 0.511,
                    "f1": 0.420,
                },
                "test": {
                    "roc_auc": 0.854,
                    "pr_auc": 0.350,
                    "precision": 0.369,
                    "recall": 0.525,
                    "f1": 0.433,
                },
            },
        },
    }

    (tmp_path / "comparison_metrics.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        prediction_service,
        "get_model_dir",
        lambda: tmp_path,
    )

    response = ml_client.get("/api/v1/ml/model-info")

    assert response.status_code == 200

    data = response.json()
    assert data["model_name"] == "random_forest"
    assert data["model_version"] == "2.1.0"
    assert data["target"] == "SeriousDlqin2yrs"
    assert data["probability_calibrated"] is False
    assert data["selected_threshold"] == 0.7
    assert "logistic_regression" in data["results"]
    assert "random_forest" in data["results"]
    assert "roc_auc" in data["results"]["random_forest"]["test"]
    assert "pr_auc" in data["results"]["random_forest"]["test"]


def test_ml_predict_returns_prediction(
    ml_client: TestClient,
    valid_payload: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    expected = {
        "model_name": "random_forest",
        "model_version": "2.1.0",
        "historical_event_score": 0.42,
        "threshold": 0.7,
        "prediction": 0,
        "probability_calibrated": False,
        "target": "SeriousDlqin2yrs",
    }

    def fake_prediction(features: dict) -> dict:
        assert features == valid_payload
        return expected

    monkeypatch.setattr(ml_api.predictions, "make_prediction", fake_prediction)

    response = ml_client.post(
        "/api/v1/ml/predict",
        json=valid_payload,
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_ml_predict_accepts_missing_monthly_income(
    ml_client: TestClient,
    valid_payload: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    valid_payload["MonthlyIncome"] = None

    def fake_prediction(features: dict) -> dict:
        assert features["MonthlyIncome"] is None
        return {
            "model_name": "random_forest",
            "model_version": "2.1.0",
            "historical_event_score": 0.2,
            "threshold": 0.7,
            "prediction": 0,
            "probability_calibrated": False,
            "target": "SeriousDlqin2yrs",
        }

    monkeypatch.setattr(ml_api.predictions, "make_prediction", fake_prediction)

    response = ml_client.post(
        "/api/v1/ml/predict",
        json=valid_payload,
    )

    assert response.status_code == 200


def test_ml_predict_rejects_negative_feature(
    ml_client: TestClient,
    valid_payload: dict,
):
    valid_payload["DebtRatio"] = -1

    response = ml_client.post(
        "/api/v1/ml/predict",
        json=valid_payload,
    )

    assert response.status_code == 422


def test_ml_predict_rejects_boolean_feature(
    ml_client: TestClient,
    valid_payload: dict,
):
    valid_payload["MonthlyIncome"] = True

    response = ml_client.post(
        "/api/v1/ml/predict",
        json=valid_payload,
    )

    assert response.status_code == 422


def test_ml_predict_rejects_unexpected_feature(
    ml_client: TestClient,
    valid_payload: dict,
):
    valid_payload["age"] = 35

    response = ml_client.post(
        "/api/v1/ml/predict",
        json=valid_payload,
    )

    assert response.status_code == 422


def test_ml_predict_returns_503_when_model_unavailable(
    ml_client: TestClient,
    valid_payload: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    def unavailable_prediction(features: dict) -> dict:
        raise ModelUnavailableError("ML model could not be loaded")

    monkeypatch.setattr(
        ml_api.predictions,
        "make_prediction",
        unavailable_prediction,
    )

    response = ml_client.post(
        "/api/v1/ml/predict",
        json=valid_payload,
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "ML model could not be loaded"


def test_get_predictor_wraps_unexpected_load_error(
    monkeypatch: pytest.MonkeyPatch,
):
    def broken_predictor(*args, **kwargs):
        raise RuntimeError("Corrupt model artifact")

    monkeypatch.setattr(
        prediction_service,
        "CreditRiskPredictor",
        broken_predictor,
    )
    prediction_service.get_predictor.cache_clear()

    try:
        with pytest.raises(ModelUnavailableError):
            prediction_service.get_predictor("invalid-model-directory")
    finally:
        prediction_service.get_predictor.cache_clear()


def test_make_prediction_wraps_inference_error(
    monkeypatch: pytest.MonkeyPatch,
):
    class BrokenPredictor:
        def predict_one(self, features: dict) -> dict:
            raise RuntimeError("Inference failure")

    monkeypatch.setattr(
        prediction_service,
        "get_model_dir",
        lambda: "test-model-directory",
    )
    monkeypatch.setattr(
        prediction_service,
        "get_predictor",
        lambda model_dir: BrokenPredictor(),
    )

    with pytest.raises(ModelUnavailableError, match="ML prediction failed"):
        prediction_service.make_prediction({"feature": 1})
