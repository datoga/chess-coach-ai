"""Classify chess errors by cognitive origin and behavioral pattern."""
from typing import Optional

def classify_error(eval_loss_cp: float, time_spent: float, is_complex: bool = False,
                   clock_remaining: Optional[float] = None, maia_agrees: bool = False,
                   maia_level_match: Optional[str] = None) -> dict:
    # Severity
    if eval_loss_cp < 50:
        severity = "minor"
    elif eval_loss_cp < 150:
        severity = "important"
    else:
        severity = "critical"
    # Behavioral
    if time_spent < 10 and is_complex:
        behavioral = "impulsive"
    elif time_spent > 600:
        behavioral = "paralysis"
    else:
        behavioral = "normal"
    # Classification
    if clock_remaining is not None and clock_remaining < 30:
        classification = "time_pressure"
    elif maia_agrees and maia_level_match == "lower":
        classification = "pattern_recognition_failure"
    elif eval_loss_cp >= 100 and is_complex:
        classification = "tactical_miss"
    else:
        classification = "conceptual_weakness"
    return {"classification": classification, "severity": severity, "behavioral": behavioral,
            "eval_loss_cp": eval_loss_cp, "time_spent": time_spent}
