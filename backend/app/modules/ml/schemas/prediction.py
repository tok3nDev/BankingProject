from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    RevolvingUtilizationOfUnsecuredLines: float = Field(ge=0, allow_inf_nan=False)
    NumberOfTime30_59DaysPastDueNotWorse: float = Field(
        alias="NumberOfTime30-59DaysPastDueNotWorse",
        ge=0,
        allow_inf_nan=False,
    )
    DebtRatio: float = Field(ge=0, allow_inf_nan=False)
    MonthlyIncome: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    NumberOfOpenCreditLinesAndLoans: float = Field(ge=0, allow_inf_nan=False)
    NumberOfTimes90DaysLate: float = Field(ge=0, allow_inf_nan=False)
    NumberRealEstateLoansOrLines: float = Field(ge=0, allow_inf_nan=False)
    NumberOfTime60_89DaysPastDueNotWorse: float = Field(
        alias="NumberOfTime60-89DaysPastDueNotWorse",
        ge=0,
        allow_inf_nan=False,
    )

    @field_validator("*", mode="before")
    @classmethod
    def reject_boolean_values(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("Boolean values are not valid numeric features")
        return value


class PredictionResponse(BaseModel):
    model_name: str
    model_version: str
    historical_event_score: float
    threshold: float
    prediction: Literal[0, 1]
    probability_calibrated: Literal[False]
    target: str


class ModelMetrics(BaseModel):
    roc_auc: float = Field(ge=0, le=1, allow_inf_nan=False)
    pr_auc: float = Field(ge=0, le=1, allow_inf_nan=False)
    precision: float = Field(ge=0, le=1, allow_inf_nan=False)
    recall: float = Field(ge=0, le=1, allow_inf_nan=False)
    f1: float = Field(ge=0, le=1, allow_inf_nan=False)


class ModelResult(BaseModel):
    selected_threshold: float = Field(gt=0, lt=1, allow_inf_nan=False)
    validation: ModelMetrics
    test: ModelMetrics


class ModelInfoResponse(BaseModel):
    model_name: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    model_version: str = Field(min_length=1)
    dataset: str = Field(min_length=1)
    dataset_rows: int = Field(gt=0)
    features: list[str] = Field(min_length=1)
    target: str
    selected_threshold: float = Field(gt=0, lt=1, allow_inf_nan=False)
    probability_calibrated: Literal[False]
    results: dict[str, ModelResult]


class MLHealthResponse(BaseModel):
    status: Literal["available", "unavailable"]
    model_available: bool
    metadata_available: bool
    model_name: str | None = None
    model_version: str | None = None
