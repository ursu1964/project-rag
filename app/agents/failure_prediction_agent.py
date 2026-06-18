"""Agent wrapper for simple statistical failure prediction."""

from __future__ import annotations

from app.prediction.failure_prediction import predict_failure_risk


def run(state: dict) -> dict:
    """Predict failure risk from state metric history."""
    values = state.get("metric_values") or state.get("capacity_history") or state.get("values") or []
    threshold = float(state.get("threshold", 0.8))
    periods = int(state.get("periods", 5))
    prediction = predict_failure_risk(values, threshold=threshold, periods=periods)
    return {**state, "failure_prediction": prediction}
