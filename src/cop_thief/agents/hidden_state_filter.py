"""Hidden-state filter — strips fields that must not reach the LLM prompt.

The observation dict from ``GameEngine.get_observation`` is already actor-scoped
(it never contains the opponent's hidden position). This module provides an extra
safety layer that explicitly removes any field whose name is on the deny-list,
and validates the filtered result before it is forwarded to the LLM.

Fields allowed in LLM prompts:
- actor, own_position, opponent_position, opponent_visible
- visible_barriers, visible_crumbtrails
- turn_counter, thief_actions_completed, round_index
- game_over, winner, win_reason
- candidate_actions, barriers_remaining
"""

_ALLOWED_FIELDS = frozenset({
    "actor",
    "own_position",
    "opponent_position",
    "opponent_visible",
    "visible_barriers",
    "visible_crumbtrails",
    "turn_counter",
    "thief_actions_completed",
    "round_index",
    "game_over",
    "winner",
    "win_reason",
    "candidate_actions",
    "barriers_remaining",
})


def filter_observation(observation: dict) -> dict:
    """Return a copy of *observation* with all non-allowed fields removed.

    Args:
        observation: The actor-scoped observation dict from the game engine.

    Returns:
        A new dict containing only fields in ``_ALLOWED_FIELDS``.
    """
    return {k: v for k, v in observation.items() if k in _ALLOWED_FIELDS}


def assert_no_hidden_state(filtered: dict) -> None:
    """Raise AssertionError if *filtered* contains any non-allowed field.

    Use in tests to verify that the filter is applied before LLM calls.

    Args:
        filtered: The dict that will be embedded in an LLM prompt.
    """
    illegal = set(filtered) - _ALLOWED_FIELDS
    if illegal:
        raise AssertionError(f"Hidden state detected in LLM prompt: {illegal}")
