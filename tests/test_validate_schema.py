from tools.validate_schema import validate

def test_valid_player_report():
    data = {"username": "test", "platform": "lichess", "ratings": {}, "style_archetype": "activist", "style_sub_profile": "balanced"}
    errors = validate(data, "player_report")
    assert errors == []

def test_missing_required_field():
    data = {"username": "test"}
    errors = validate(data, "player_report")
    assert len(errors) > 0
    assert any("platform" in e for e in errors)

def test_nonexistent_schema():
    errors = validate({}, "nonexistent")
    assert len(errors) == 1
    assert "not found" in errors[0]
