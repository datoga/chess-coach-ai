from tools.opening_classifier import classify_opening, load_openings_db

def test_load_openings_db():
    db = load_openings_db()
    assert len(db) > 100

def test_classify_sicilian():
    result = classify_opening("1. e4 c5")
    assert result["eco"].startswith("B")
    assert "Sicilian" in result["name"]

def test_classify_queens_gambit():
    result = classify_opening("1. d4 d5 2. c4")
    assert result["eco"].startswith("D")

def test_classify_unknown():
    result = classify_opening("1. a4 a5 2. b4")
    # Should return something reasonable, even if just A00
    assert "eco" in result
