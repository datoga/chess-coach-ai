"""Analyze clock time patterns from chess games."""
from typing import Optional

def calculate_time_per_move(clock_readings: list[float]) -> list[float]:
    return [clock_readings[i] - clock_readings[i + 1] for i in range(len(clock_readings) - 1)]

def detect_time_trouble(clock_readings: list[float], threshold_seconds: float = 60) -> dict:
    for i, clock in enumerate(clock_readings):
        if clock <= threshold_seconds:
            return {"in_time_trouble": True, "trouble_start_move": i, "remaining_at_trouble": clock}
    return {"in_time_trouble": False, "trouble_start_move": None, "remaining_at_trouble": None}

def find_clock_inflection_point(time_per_move: list[float], window: int = 3) -> Optional[int]:
    if len(time_per_move) < window * 2:
        return None
    for i in range(window, len(time_per_move) - window):
        avg_before = sum(time_per_move[i - window:i]) / window
        avg_after = sum(time_per_move[i:i + window]) / window
        if avg_before > 0 and avg_after / avg_before >= 4.0:
            return i
    return None

def classify_move_speed(seconds_spent: float, is_complex: bool = False) -> str:
    if seconds_spent < 10 and is_complex:
        return "impulsive"
    if seconds_spent > 600:
        return "paralysis"
    return "normal"
