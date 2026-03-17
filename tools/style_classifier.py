"""Classify chess playing style into archetypes and sub-profiles."""

def classify_style(stats: dict) -> str:
    sacrifice_rate = stats.get("sacrifice_rate", 0)
    initiative = stats.get("initiative_moves_pct", 0)
    avg_length = stats.get("avg_game_length", 35)
    book_depth = stats.get("book_depth_avg", 10)
    if sacrifice_rate > 0.08 and initiative > 0.45:
        return "activist"
    if book_depth > 14 and sacrifice_rate < 0.05:
        return "theorist"
    if avg_length > 40 and initiative < 0.3:
        return "defender"
    if initiative > 0.4:
        return "activist"
    return "theorist"

def classify_sub_profile(acpl_quiet: float, acpl_complex: float) -> str:
    ratio = acpl_quiet / acpl_complex if acpl_complex > 0 else 1.0
    if ratio < 0.5:
        return "precision_player"
    if ratio > 1.5:
        return "chaos_specialist"
    return "balanced"
