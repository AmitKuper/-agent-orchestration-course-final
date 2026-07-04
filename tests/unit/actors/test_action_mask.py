"""Unit tests for action_mask module."""

from cop_thief.actors.action_mask import action_token_at, build_action_mask, vocab_size


def _obs(candidates: list[str]) -> dict:
    """Build a minimal observation dict with the given candidate actions."""
    return {"candidate_actions": candidates}


def test_vocab_size_is_ten():
    """Vocabulary must have exactly 10 slots: 8 directions + stay + forfeit."""
    assert vocab_size() == 10


def test_all_zeros_for_empty_candidates():
    """All-zero mask when no candidates."""
    mask = build_action_mask(_obs([]))
    assert mask == [0] * 10


def test_north_only_candidate():
    """Mask has 1 at N index, 0 elsewhere."""
    mask = build_action_mask(_obs(["N"]))
    assert mask[0] == 1
    assert sum(mask) == 1


def test_stay_sets_correct_slot():
    """'stay' candidate sets the slot at index 8."""
    mask = build_action_mask(_obs(["stay"]))
    assert mask[8] == 1
    assert sum(mask) == 1


def test_forfeit_sets_correct_slot():
    """'forfeit' candidate sets the slot at index 9."""
    mask = build_action_mask(_obs(["forfeit"]))
    assert mask[9] == 1
    assert sum(mask) == 1


def test_all_directions_plus_stay_forfeit():
    """All 10 candidates → all-ones mask."""
    all_tokens = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "stay", "forfeit"]
    mask = build_action_mask(_obs(all_tokens))
    assert mask == [1] * 10


def test_barrier_tokens_ignored_in_fixed_mask():
    """Barrier tokens (not in fixed vocabulary) are silently ignored."""
    mask = build_action_mask(_obs(["N", "barrier_2_3"]))
    assert mask[0] == 1
    assert sum(mask) == 1


def test_action_token_at_round_trips():
    """action_token_at(i) returns the token placed at slot i."""
    tokens = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "stay", "forfeit"]
    for i, tok in enumerate(tokens):
        assert action_token_at(i) == tok
