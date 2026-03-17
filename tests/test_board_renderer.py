from tools.board_renderer import render_board, render_comparison

def test_starting_position():
    board = render_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    assert "♔" in board
    assert "♚" in board
    assert "White to move" in board

def test_black_perspective():
    board = render_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                        perspective="black")
    assert "h   g   f   e" in board

def test_highlight_squares():
    board = render_board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                        highlight_squares=["e4"])
    assert "*♙*" in board

def test_label():
    board = render_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                        label="Move 1")
    assert "Move 1" in board

def test_invalid_fen():
    result = render_board("invalid")
    assert "Invalid FEN" in result

def test_comparison():
    result = render_comparison(
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        played_move="Nf6", best_move="d5",
        played_eval="-0.3", best_eval="+0.5",
        label="Critical"
    )
    assert "❌ Played: Nf6" in result
    assert "✅ Best:   d5" in result
    assert "Critical" in result
