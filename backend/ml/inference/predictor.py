from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ML_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ML_ROOT / "models"

OPTIONAL_FEATURES = {"MonthlyIncome"}


class CreditRiskPredictor:
    """Predict historical two-year serious delinquency scores."""

    def __init__(
        self,
        model_dir: Path | str = MODEL_DIR,
    ) -> None:
        self.model_dir = Path(model_dir)

        metadata_path = self.model_dir / "comparison_metrics.json"

        if not metadata_path.is_file():
            raise FileNotFoundError(metadata_path)

        self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        if not isinstance(self.metadata, dict):
            raise ValueError("Model metadata must be a JSON object")

        required_metadata = {
            "model_name",
            "model_version",
            "features",
            "target",
            "selected_threshold",
            "probability_calibrated",
        }

        missing_metadata = required_metadata - set(self.metadata)

        if missing_metadata:
            raise ValueError(f"Missing metadata fields: {sorted(missing_metadata)}")

        model_name = self.metadata["model_name"]
        model_version = self.metadata["model_version"]

        if not isinstance(model_name, str) or not re.fullmatch(
            r"[a-zA-Z0-9_-]+", model_name
        ):
            raise ValueError("Invalid model name")

        if not isinstance(model_version, str) or not model_version.strip():
            raise ValueError("Invalid model version")

        self.features = self.metadata["features"]

        if (
            not isinstance(self.features, list)
            or not self.features
            or not all(isinstance(f, str) for f in self.features)
            or len(self.features) != len(set(self.features))
        ):
            raise ValueError("Invalid feature metadata")

        if self.metadata["target"] != "SeriousDlqin2yrs":
            raise ValueError("Unexpected model target")

        self.threshold = float(self.metadata["selected_threshold"])

        if not np.isfinite(self.threshold) or not 0 < self.threshold < 1:
            raise ValueError("Invalid classification threshold")

        if self.metadata["probability_calibrated"] is not False:
            raise ValueError("This predictor expects an explicitly uncalibrated model")

        model_path = self.model_dir / f"{model_name}.joblib"

        if not model_path.is_file():
            raise FileNotFoundError(model_path)

        self.model = joblib.load(model_path)

        if list(self.model.classes_) != [0, 1]:
            raise ValueError("Unexpected model classes")

        if hasattr(self.model, "n_features_in_"):
            if self.model.n_features_in_ != len(self.features):
                raise ValueError("Model feature count mismatch")

    def _prepare_input(
        self,
        values: Mapping[str, Any],
    ) -> pd.DataFrame:
        if not isinstance(values, Mapping):
            raise TypeError("Input must be a feature mapping")

        missing = set(self.features) - set(values)
        unexpected = set(values) - set(self.features)

        if missing:
            raise ValueError(f"Missing features: {sorted(missing)}")

        if unexpected:
            raise ValueError(f"Unexpected features: {sorted(unexpected)}")

        normalized = {}

        for feature in self.features:
            value = values[feature]

            if value is None:
                if feature not in OPTIONAL_FEATURES:
                    raise ValueError(f"Missing value is not allowed for {feature}")

                normalized[feature] = np.nan
                continue

            if isinstance(value, bool):
                raise ValueError(f"Boolean value is invalid for {feature}")

            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Feature {feature} must be numeric") from exc

            if not np.isfinite(numeric_value):
                raise ValueError(f"Feature {feature} must be finite")

            if numeric_value < 0:
                raise ValueError(f"Feature {feature} cannot be negative")

            normalized[feature] = numeric_value

        return pd.DataFrame(
            [[normalized[feature] for feature in self.features]],
            columns=self.features,
        )

    def predict_one(
        self,
        values: Mapping[str, Any],
    ) -> dict[str, Any]:
        sample = self._prepare_input(values)

        probabilities = self.model.predict_proba(sample)

        if probabilities.shape != (1, 2):
            raise RuntimeError("Unexpected model probability output")

        event_score = float(probabilities[0, 1])

        if not np.isfinite(event_score) or not 0 <= event_score <= 1:
            raise RuntimeError("Model returned an invalid score")

        prediction = int(event_score >= self.threshold)

        return {
            "model_name": self.metadata["model_name"],
            "model_version": self.metadata["model_version"],
            "historical_event_score": event_score,
            "threshold": self.threshold,
            "prediction": prediction,
            "probability_calibrated": False,
            "target": self.metadata["target"],
        }
