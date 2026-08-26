from src.evaluate import ndcg_at_k, recall_at_k


def test_recall_at_k():
    relevant = {"P1": 3, "P2": 2}
    assert recall_at_k(["P1", "P9"], relevant, 2) == 0.5


def test_ndcg_perfect_ranking():
    relevant = {"P1": 3, "P2": 2, "P3": 1}
    assert round(ndcg_at_k(["P1", "P2", "P3"], relevant, 3), 6) == 1.0


def test_ndcg_rewards_better_order():
    relevant = {"P1": 3, "P2": 1}
    good = ndcg_at_k(["P1", "P2"], relevant, 2)
    bad = ndcg_at_k(["P2", "P1"], relevant, 2)
    assert good > bad
