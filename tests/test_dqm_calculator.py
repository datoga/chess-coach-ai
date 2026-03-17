from tools.dqm_calculator import calculate_dqm, calculate_acpl, MAX_ACPL_BY_LEVEL

def test_perfect_play():
    eval_diffs = [0, 0, 0, 0, 0]
    dqm = calculate_dqm(eval_diffs, rating=1500)
    assert dqm == 1.0

def test_terrible_play():
    eval_diffs = [200, 300, 250, 400, 500]
    dqm = calculate_dqm(eval_diffs, rating=1500)
    assert dqm < 0.2

def test_acpl():
    eval_diffs = [10, 20, 30, 40, 50]
    acpl = calculate_acpl(eval_diffs)
    assert acpl == 30.0

def test_dqm_level_relative():
    eval_diffs = [50, 50, 50]
    dqm_1200 = calculate_dqm(eval_diffs, rating=1200)
    dqm_2000 = calculate_dqm(eval_diffs, rating=2000)
    assert dqm_1200 > dqm_2000

def test_max_acpl_levels():
    assert MAX_ACPL_BY_LEVEL[1000] > MAX_ACPL_BY_LEVEL[2000]

def test_empty_diffs():
    assert calculate_acpl([]) == 0.0
    assert calculate_dqm([], rating=1500) == 1.0
