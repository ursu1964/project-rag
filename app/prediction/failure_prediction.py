"""Failure prediction using simple statistical baselines."""

from __future__ import annotations

from typing import Iterable

from app.prediction.capacity_forecasting import (
    moving_average,
    predict_threshold_breach,
    trend_slope,
)


def predict_failure_risk(
    metric_values: Iterable[float],
    threshold: float = 0.8,
    periods: int = 5,
) -> dict:
    """Predict failure risk from metric trend and threshold breach likelihood."""
    values = [float(value) for value in metric_values]
    if not values:
        return {
            "risk_level": "low",
            "risk_score": 0.0,
            "moving_average": 0.0,
            "trend_slope": 0.0,
            "will_breach": False,
            "breach_period": None,
            "reason": "No metric history provided.",
        }

    breach = predict_threshold_breach(values, threshold=threshold, periods=periods)
    slope = trend_slope(values)
    average = moving_average(values)
    latest = values[-1]
    threshold_value = float(threshold)

    utilization_ratio = latest / threshold_value if threshold_value else latest
    slope_bonus = max(0.0, min(0.3, slope / threshold_value if threshold_value else slope))
    breach_bonus = 0.3 if breach["will_breach"] else 0.0
    risk_score = round(min(1.0, max(0.0, utilization_ratio * 0.5 + slope_bonus + breach_bonus)), 6)

    if risk_score >= 0.75:
        risk_level = "high"
    elif risk_score >= 0.45:
        risk_level = "medium"
    else:
        risk_level = "low"

    reason = (
        f"Latest value {latest} vs threshold {threshold_value}; "
        f"moving average {average}; slope {slope}; "
        f"breach predicted={breach['will_breach']}."
    )
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "moving_average": average,
        "trend_slope": slope,
        "will_breach": breach["will_breach"],
        "breach_period": breach["breach_period"],
        "forecast": breach["forecast"],
        "threshold": threshold_value,
        "reason": reason,
    }
