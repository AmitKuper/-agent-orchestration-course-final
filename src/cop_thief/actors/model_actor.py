"""ModelActor — loads a trained model from the ModelBank and runs inference.

The actor is a stub: it falls back to RandomLegalActor until real model
loading is wired in Phase 9.  The inference interface is defined here so
the orchestrator can call it uniformly regardless of backend.
"""

from cop_thief.actors.action_mask import action_token_at, build_action_mask
from cop_thief.actors.base import Actor
from cop_thief.actors.model_bank import ModelBank, ModelMetadata
from cop_thief.actors.random_actor import RandomLegalActor, _parse_candidate
from cop_thief.game_engine.actions import Action


class ModelActor(Actor):
    """Actor backed by a trained model artifact from the ``ModelBank``.

    In Phase 3 this is a thin stub: it retrieves metadata from the bank,
    builds an action mask for the current observation, and delegates to
    ``RandomLegalActor`` until real inference is implemented in Phase 9.

    Subclass and override ``_infer`` to plug in any inference backend
    (ONNX, PyTorch, etc.) without touching the orchestration code.
    """

    def __init__(self, model_id: str, bank: ModelBank) -> None:
        """Bind the actor to a registered model.

        Args:
            model_id: Key in *bank* identifying the model to use.
            bank: The ``ModelBank`` holding model metadata.

        Raises:
            KeyError: If *model_id* is not in *bank*.
        """
        self._metadata: ModelMetadata = bank.get(model_id)
        self._fallback = RandomLegalActor()

    @property
    def metadata(self) -> ModelMetadata:
        """Expose model metadata for logging and reporting."""
        return self._metadata

    def _infer(self, mask: list[int], observation: dict) -> int | None:
        """Run model inference and return the chosen mask index, or None.

        Override in a subclass to provide real inference.  Returning None
        causes the actor to fall back to ``RandomLegalActor``.

        Args:
            mask: Binary action mask from ``build_action_mask``.
            observation: Full observation dict.

        Returns:
            Index into the mask vocabulary, or None to defer to fallback.
        """
        return None

    def get_action(self, observation: dict) -> Action:
        """Return an action from model inference (or random fallback).

        Builds the action mask, calls ``_infer``, then converts the chosen
        index to an ``Action``.  Falls back to ``RandomLegalActor`` when
        ``_infer`` returns None or selects a masked action.

        Args:
            observation: Observation dict from ``GameEngine.get_observation``.

        Returns:
            An ``Action`` valid for the current observation.
        """
        mask = build_action_mask(observation)
        chosen_index = self._infer(mask, observation)
        if chosen_index is not None and mask[chosen_index] == 1:
            return _parse_candidate(action_token_at(chosen_index))
        return self._fallback.get_action(observation)
