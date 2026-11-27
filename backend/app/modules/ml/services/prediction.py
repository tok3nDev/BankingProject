import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ml.inference.predictor import MODEL_DIR, CreditRiskPredictor

from app.core.config import settings


class ModelUnavailableError(Exception):
    pass


def get_model_dir() -> Path:
    return settings.ml_model_dir or MODEL_DIR


def read_model_metadata() -> dict[str, Any]:
    metadata_path = get_model_dir() / "comparison_metrics.json"

    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelUnavailableError("Model metadata is unavailable") from exc


def check_model_availability() -> dict[str, Any]:
    try:
        metadata = read_model_metadata()
        model_name = metadata["model_name"]
        model_version = metadata["model_version"]
        model_path = get_model_dir() / f"{model_name}.joblib"

        available = model_path.is_file()

        return {
            "status": "available" if available else "unavailable",
            "model_available": available,
            "metadata_available": True,
            "model_name": model_name,
            "model_version": model_version,
        }

    except (ModelUnavailableError, KeyError, TypeError):
        return {
            "status": "unavailable",
            "model_available": False,
            "metadata_available": False,
            "model_name": None,
            "model_version": None,
        }


@lru_cache(maxsize=2)
def get_predictor(model_dir: str) -> CreditRiskPredictor:
    try:
        return CreditRiskPredictor(model_dir=Path(model_dir))
    except Exception as exc:
        raise ModelUnavailableError("ML model could not be loaded") from exc


def make_prediction(features: dict[str, Any]) -> dict[str, Any]:
    model_dir = get_model_dir()

    predictor = get_predictor(str(model_dir))

    try:
        return predictor.predict_one(features)
    except (TypeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    except Exception as exc:
        raise ModelUnavailableError("ML prediction failed") from exc
