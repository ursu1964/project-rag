"""Capacity forecasting using deterministic statistical baselines."""

from __future__ import annotations

from typing import Iterable


def moving_average(values: Iterable[float], window: int = 3) -> float:
    """Return the moving average for the last `window` values."""
    numbers = [float(value) for value in values]
    if not numbers:
        return 0.0
    bounded_window = max(1, min(int(window), len(numbers)))
    return round(sum(numbers[-bounded_window:]) / bounded_window, 6)


def trend_slope(values: Iterable[float]) -> float:
    """Return simple least-squares slope over sequential observations."""
    y = [float(value) for value in values]
    n = len(y)
    if n < 2:
        return 0.0
    x = list(range(n))
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    denominator = sum((item - mean_x) ** 2 for item in x)
    if denominator == 0:
        return 0.0
    numerator = sum((x[index] - mean_x) * (y[index] - mean_y) for index in range(n))
    return round(numerator / denominator, 6)


def forecast_capacity(values: Iterable[float], periods: int = 1, window: int = 3) -> dict:
    """Forecast capacity utilization with moving average plus trend slope."""
    numbers = [float(value) for value in values]
    if not numbers:
        return {"moving_average": 0.0, "trend_slope": 0.0, "forecast": []}

    average = moving_average(numbers, window)
    slope = trend_slope(numbers)
    horizon = max(1, int(periods))
    forecast = [round(max(0.0, average + slope * step), 6) for step in range(1, horizon + 1)]
    return {"moving_average": average, "trend_slope": slope, "forecast": forecast}


def predict_threshold_breach(values: Iterable[float], threshold: float, periods: int = 5) -> dict:
    """Predict whether a threshold will be breached within the forecast horizon."""
    forecast = forecast_capacity(values, periods=periods)
    threshold_value = float(threshold)
    breach_index = next((index for index, value in enumerate(forecast["forecast"], start=1) if value >= threshold_value), None)
    return {
        **forecast,
        "threshold": threshold_value,
        "will_breach": breach_index is not None,
        "breach_period": breach_index,
    }
