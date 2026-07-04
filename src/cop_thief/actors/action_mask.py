"""Action mask builder — binary vector over the fixed action vocabulary.

The mask encodes which actions from ``candidate_actions`` are available.
Used as model input for neural actors and for action-space debugging.

Vocabulary (fixed 10 slots):
  indices 0-7  → directional moves N NE E SE S SW W NW
  index   8    → stay
  index   9    → forfeit
"""

from cop_thief.actors.base import ALL_ACTION_TOKENS

# Fixed-size direction+stay+forfeit vocabulary (no barriers in mask).
_VOCAB = ALL_ACTION_TOKENS  # 10 tokens: 8 directions + stay + forfeit
_VOCAB_SIZE = len(_VOCAB)
_TOKEN_INDEX: dict[str, int] = {tok: i for i, tok in enumerate(_VOCAB)}


def build_action_mask(observation: dict) -> list[int]:
    """Return a binary mask of length ``_VOCAB_SIZE`` for the observation.

    A ``1`` at position ``i`` means action ``_VOCAB[i]`` is a candidate.
    Barrier placements are not included in this fixed mask; they require
    a separate per-grid encoding handled by model-specific preprocessing.

    Args:
        observation: Observation dict from ``GameEngine.get_observation``.

    Returns:
        List of 0/1 integers of length equal to the fixed vocabulary size.
    """
    mask = [0] * _VOCAB_SIZE
    for token in observation.get("candidate_actions", []):
        idx = _TOKEN_INDEX.get(token)
        if idx is not None:
            mask[idx] = 1
    return mask


def vocab_size() -> int:
    """Return the fixed vocabulary size (number of mask slots)."""
    return _VOCAB_SIZE


def action_token_at(index: int) -> str:
    """Return the action token at the given mask index."""
    return _VOCAB[index]
