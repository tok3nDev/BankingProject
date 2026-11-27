import pytest
from ml.inference.predictor import CreditRiskPredictor


@pytest.fixture(scope="module")
def predictor():
    return CreditRiskPredictor()


@pytest.fixture
def valid_features():
    return {
        "RevolvingUtilizationOfUnsecuredLines": 0.35,
        "NumberOfTime30-59DaysPastDueNotWorse": 0,
        "DebtRatio": 0.45,
        "MonthlyIncome": 6500,
        "NumberOfOpenCreditLinesAndLoans": 8,
        "NumberOfTimes90DaysLate": 0,
        "NumberRealEstateLoansOrLines": 1,
        "NumberOfTime60-89DaysPastDueNotWorse": 0,
    }


def test_prediction_structure(predictor, valid_features):
    result = predictor.predict_one(valid_features)

    assert result["model_name"] == "random_forest"
    assert result["model_version"] == "2.1.0"
    assert 0 <= result["historical_event_score"] <= 1
    assert result["prediction"] in (0, 1)
    assert result["probability_calibrated"] is False
    assert result["target"] == "SeriousDlqin2yrs"


def test_missing_income_is_supported(predictor, valid_features):
    valid_features["MonthlyIncome"] = None

    result = predictor.predict_one(valid_features)

    assert 0 <= result["historical_event_score"] <= 1


def test_missing_feature_is_rejected(predictor, valid_features):
    del valid_features["MonthlyIncome"]

    with pytest.raises(ValueError, match="Missing features"):
        predictor.predict_one(valid_features)


def test_unexpected_feature_is_rejected(predictor, valid_features):
    valid_features["age"] = 35

    with pytest.raises(ValueError, match="Unexpected features"):
        predictor.predict_one(valid_features)


def test_negative_value_is_rejected(predictor, valid_features):
    valid_features["MonthlyIncome"] = -100

    with pytest.raises(ValueError, match="cannot be negative"):
        predictor.predict_one(valid_features)


def test_boolean_value_is_rejected(predictor, valid_features):
    valid_features["MonthlyIncome"] = True

    with pytest.raises(ValueError, match="Boolean value"):
        predictor.predict_one(valid_features)


def test_missing_non_income_value_is_rejected(
    predictor,
    valid_features,
):
    valid_features["DebtRatio"] = None

    with pytest.raises(ValueError, match="Missing value is not allowed"):
        predictor.predict_one(valid_features)


def test_nan_income_is_rejected(predictor, valid_features):
    valid_features["MonthlyIncome"] = float("nan")

    with pytest.raises(ValueError, match="must be finite"):
        predictor.predict_one(valid_features)
