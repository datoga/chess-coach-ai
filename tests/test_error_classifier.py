from tools.error_classifier import classify_error

def test_impulsive_error():
    result = classify_error(eval_loss_cp=150, time_spent=5, is_complex=True)
    assert result["classification"] == "tactical_miss"
    assert result["behavioral"] == "impulsive"

def test_paralysis_error():
    result = classify_error(eval_loss_cp=80, time_spent=900, is_complex=False)
    assert result["classification"] == "conceptual_weakness"
    assert result["behavioral"] == "paralysis"

def test_time_pressure_error():
    result = classify_error(eval_loss_cp=200, time_spent=2, is_complex=True, clock_remaining=15)
    assert result["classification"] == "time_pressure"

def test_pattern_recognition():
    result = classify_error(eval_loss_cp=120, time_spent=30, is_complex=True,
                           maia_agrees=True, maia_level_match="lower")
    assert result["classification"] == "pattern_recognition_failure"

def test_minor_inaccuracy():
    result = classify_error(eval_loss_cp=25, time_spent=60, is_complex=False)
    assert result["severity"] == "minor"

def test_critical_blunder():
    result = classify_error(eval_loss_cp=300, time_spent=5, is_complex=True)
    assert result["severity"] == "critical"
