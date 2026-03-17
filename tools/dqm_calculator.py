"""Decision Quality Metric — normalized, level-relative quality score."""

MAX_ACPL_BY_LEVEL = {
    800: 200, 1000: 150, 1200: 120, 1400: 95,
    1500: 85, 1600: 75, 1800: 60, 2000: 45,
    2200: 35, 2400: 25, 2600: 18, 2800: 12,
}

def _get_max_acpl(rating: int) -> float:
    levels = sorted(MAX_ACPL_BY_LEVEL.keys())
    if rating <= levels[0]:
        return MAX_ACPL_BY_LEVEL[levels[0]]
    if rating >= levels[-1]:
        return MAX_ACPL_BY_LEVEL[levels[-1]]
    for i in range(len(levels) - 1):
        if levels[i] <= rating <= levels[i + 1]:
            lo, hi = levels[i], levels[i + 1]
            ratio = (rating - lo) / (hi - lo)
            return MAX_ACPL_BY_LEVEL[lo] + ratio * (MAX_ACPL_BY_LEVEL[hi] - MAX_ACPL_BY_LEVEL[lo])
    return MAX_ACPL_BY_LEVEL[1500]

def calculate_acpl(eval_diffs_cp: list[float]) -> float:
    if not eval_diffs_cp:
        return 0.0
    return sum(abs(d) for d in eval_diffs_cp) / len(eval_diffs_cp)

def calculate_dqm(eval_diffs_cp: list[float], rating: int = 1500) -> float:
    acpl = calculate_acpl(eval_diffs_cp)
    max_acpl = _get_max_acpl(rating)
    dqm = max(0.0, min(1.0, 1.0 - (acpl / max_acpl)))
    return round(dqm, 3)
