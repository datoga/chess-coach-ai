from tools.style_classifier import classify_style, classify_sub_profile

def test_activist():
    stats = {"avg_game_length": 28, "sacrifice_rate": 0.15, "initiative_moves_pct": 0.6}
    assert classify_style(stats) == "activist"

def test_theorist():
    stats = {"avg_game_length": 35, "sacrifice_rate": 0.02, "initiative_moves_pct": 0.3, "book_depth_avg": 18}
    assert classify_style(stats) == "theorist"

def test_defender():
    stats = {"avg_game_length": 45, "sacrifice_rate": 0.01, "initiative_moves_pct": 0.2}
    assert classify_style(stats) == "defender"

def test_precision_player():
    assert classify_sub_profile(15.0, 60.0) == "precision_player"

def test_chaos_specialist():
    assert classify_sub_profile(55.0, 20.0) == "chaos_specialist"

def test_balanced():
    assert classify_sub_profile(30.0, 35.0) == "balanced"
