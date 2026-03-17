from tools.time_analysis import (
    calculate_time_per_move, detect_time_trouble,
    find_clock_inflection_point, classify_move_speed,
)

def test_time_per_move():
    clocks = [300, 290, 270, 240, 200, 150]
    times = calculate_time_per_move(clocks)
    assert times == [10, 20, 30, 40, 50]

def test_detect_time_trouble():
    clocks = [300, 250, 200, 100, 30, 10, 5]
    result = detect_time_trouble(clocks, threshold_seconds=60)
    assert result["in_time_trouble"] is True
    assert result["trouble_start_move"] == 4

def test_no_time_trouble():
    clocks = [300, 280, 260, 240, 220]
    result = detect_time_trouble(clocks, threshold_seconds=60)
    assert result["in_time_trouble"] is False

def test_find_clock_inflection():
    times_per_move = [5, 5, 10, 10, 15, 20, 60, 80, 90]
    inflection = find_clock_inflection_point(times_per_move)
    assert inflection is not None
    assert inflection >= 5

def test_classify_move_speed():
    assert classify_move_speed(3, is_complex=True) == "impulsive"
    assert classify_move_speed(900, is_complex=False) == "paralysis"
    assert classify_move_speed(60, is_complex=True) == "normal"
