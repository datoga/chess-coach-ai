from tools.wellness_tracker import WellnessTracker

def test_from_manual():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=7, sleep_quality="good",
                                 energy_level=8, last_meal_hours_ago=1, hydration="adequate")
    assert state["sleep_hours"] == 7
    assert state["hrv"] is None

def test_from_wearable_not_implemented():
    tracker = WellnessTracker()
    try:
        tracker.from_wearable(device="oura")
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass

def test_calculate_modifier_low_sleep():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=4, sleep_quality="poor",
                                 energy_level=3, last_meal_hours_ago=5, hydration="low")
    modifier = tracker.calculate_intensity_modifier(state)
    assert modifier <= 0.6

def test_calculate_modifier_good_state():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=8, sleep_quality="good",
                                 energy_level=9, last_meal_hours_ago=1, hydration="adequate")
    modifier = tracker.calculate_intensity_modifier(state)
    assert modifier >= 0.9

def test_generate_alerts():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=4, sleep_quality="poor",
                                 energy_level=3, last_meal_hours_ago=6, hydration="low")
    alerts = tracker.generate_alerts(state)
    assert len(alerts) >= 2

def test_no_alerts_good_state():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=8, sleep_quality="good",
                                 energy_level=8, last_meal_hours_ago=1, hydration="adequate")
    alerts = tracker.generate_alerts(state)
    assert len(alerts) == 0
