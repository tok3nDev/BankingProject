from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, RobustScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "cs-training.csv"
MODEL_DIR = ROOT / "models"

TARGET = "SeriousDlqin2yrs"

FEATURES = [
    "RevolvingUtilizationOfUnsecuredLines",
    "NumberOfTime30-59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60-89DaysPastDueNotWorse",
]

RANDOM_STATE = 42
MODEL_VERSION = "2.1.0"
THRESHOLDS = [round(x * 0.05, 2) for x in range(2, 19)]


def log_transform(values: np.ndarray) -> np.ndarray:
    return np.log1p(values)


def build_logistic_pipeline() -> Pipeline:
    numeric_features = [feature for feature in FEATURES if feature != "MonthlyIncome"]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("log_transform", FunctionTransformer(log_transform)),
            ("scaler", RobustScaler()),
        ]
    )

    income_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median", add_indicator=True),
            ),
            ("log_transform", FunctionTransformer(log_transform)),
            ("scaler", RobustScaler()),
        ]
    )

    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("income", income_pipeline, ["MonthlyIncome"]),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def build_random_forest_pipeline() -> Pipeline:
    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                SimpleImputer(strategy="median"),
                FEATURES,
            )
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=14,
                    min_samples_leaf=10,
                    class_weight="balanced_subsample",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate(
    model: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    threshold: float,
) -> dict:
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    return {
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "pr_auc": float(average_precision_score(y, probabilities)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(y, predictions, labels=[0, 1]).tolist(),
    }


def select_threshold(
    model: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
) -> dict:
    probabilities = model.predict_proba(X)[:, 1]
    results = []

    for threshold in THRESHOLDS:
        predictions = (probabilities >= threshold).astype(int)

        results.append(
            {
                "threshold": threshold,
                "precision": float(precision_score(y, predictions, zero_division=0)),
                "recall": float(recall_score(y, predictions, zero_division=0)),
                "f1": float(f1_score(y, predictions, zero_division=0)),
            }
        )

    best = max(results, key=lambda item: item["f1"])

    return {
        "selected": best,
        "all_thresholds": results,
        "selection_metric": "validation_f1",
    }


def validate_dataset(df: pd.DataFrame) -> None:
    required_columns = FEATURES + [TARGET]
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing dataset columns: {missing_columns}")

    X = df[FEATURES]
    y = df[TARGET]

    if X.isna().all().any():
        raise ValueError("A feature contains only missing values")

    values = X.to_numpy(dtype=float)

    if np.isinf(values).any():
        raise ValueError("Infinite values detected in features")

    if X.lt(0).any().any():
        raise ValueError("Negative values detected in features")

    if y.isna().any():
        raise ValueError("Target contains missing values")

    if not set(y.unique()).issubset({0, 1}):
        raise ValueError("Target must contain only 0 and 1")

    if y.nunique() != 2:
        raise ValueError("Target must contain both classes")


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(DATA_PATH)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    validate_dataset(df)

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        stratify=y_train_val,
        random_state=RANDOM_STATE,
    )

    print("Dataset:", len(df))
    print("Train:", len(X_train))
    print("Validation:", len(X_val))
    print("Test:", len(X_test))

    models = {
        "logistic_regression": build_logistic_pipeline(),
        "random_forest": build_random_forest_pipeline(),
    }

    results = {}
    candidates = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")

        model.fit(X_train, y_train)

        threshold_result = select_threshold(
            model,
            X_val,
            y_val,
        )

        selected_threshold = threshold_result["selected"]["threshold"]

        validation_metrics = evaluate(
            model,
            X_val,
            y_val,
            selected_threshold,
        )

        test_metrics = evaluate(
            model,
            X_test,
            y_test,
            selected_threshold,
        )

        results[name] = {
            "selected_threshold": selected_threshold,
            "threshold_selection": threshold_result,
            "validation": validation_metrics,
            "test": test_metrics,
        }

        candidates[name] = model

        print("Validation:", validation_metrics)
        print("Selected threshold:", selected_threshold)
        print("Test:", test_metrics)

    # Model selection uses validation PR-AUC only.
    best_name = max(
        results,
        key=lambda name: results[name]["validation"]["pr_auc"],
    )

    best_model = candidates[best_name]
    selected_threshold = results[best_name]["selected_threshold"]

    # Refit the selected model on Train + Validation.
    # The independent Test split is not used for fitting.
    print(f"\nRefitting {best_name} on Train + Validation...")

    best_model.fit(X_train_val, y_train_val)

    model_path = MODEL_DIR / f"{best_name}.joblib"
    joblib.dump(best_model, model_path)

    metadata = {
        "model_name": best_name,
        "model_version": MODEL_VERSION,
        "dataset": "Give Me Some Credit",
        "dataset_rows": len(df),
        "features": FEATURES,
        "target": TARGET,
        "random_state": RANDOM_STATE,
        "split": {
            "train": len(X_train),
            "validation": len(X_val),
            "test": len(X_test),
            "final_fit": len(X_train_val),
        },
        "selection_metric": "validation_pr_auc",
        "threshold_selection_metric": "validation_f1",
        "selected_threshold": selected_threshold,
        "probability_calibrated": False,
        "final_model_fit": "train_plus_validation",
        "test_metrics_source": "model_fitted_on_train_only",
        "results": results,
        "trained_at": datetime.now(UTC).isoformat(),
    }

    with (MODEL_DIR / "comparison_metrics.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metadata, file, indent=2)

    print("\n=== MODEL SELECTION ===")
    print("Selected:", best_name)
    print("Final fit rows:", len(X_train_val))
    print("Threshold:", selected_threshold)
    print("Saved:", model_path)
    print("Metadata: comparison_metrics.json")


if __name__ == "__main__":
    main()
