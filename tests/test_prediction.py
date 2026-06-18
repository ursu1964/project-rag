from app.agents.failure_prediction_agent import run
from app.prediction.capacity_forecasting import (
    moving_average,
    predict_threshold_breach,
    trend_slope,
)
from app.prediction.failure_prediction import predict_failure_risk


def test_moving_average():
    assert moving_average([1, 2, 3, 4], window=2) == 3.5


def test_trend_slope_positive():
    assert trend_slope([1, 2, 3]) == 1.0


def test_threshold_breach_prediction():
    result = predict_threshold_breach([60, 70, 80], threshold=90, periods=3)

    assert result["will_breach"] is True
    assert result["breach_period"] is not None


def test_predict_failure_risk_high():
    result = predict_failure_risk([0.7, 0.8, 0.9], threshold=0.85, periods=2)

    assert result["risk_level"] == "high"
    assert result["will_breach"] is True


def test_failure_prediction_agent():
    state = run({"metric_values": [0.1, 0.2, 0.3], "threshold": 0.5})

    assert "failure_prediction" in state
    assert state["failure_prediction"]["risk_score"] >= 0.0
