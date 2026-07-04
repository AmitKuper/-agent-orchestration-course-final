"""ModelBank — metadata registry for trained model artifacts.

Model weights live under ``models/`` (git-ignored).  The bank stores only
metadata so the registry can be committed without committing binary artifacts.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelMetadata:
    """Metadata for one trained model artifact."""

    model_id: str
    version: str
    role: str  # "cop" | "thief" | "any"
    win_rate: float
    artifact_path: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def artifact_exists(self) -> bool:
        """Return True if the model file exists on disk."""
        return Path(self.artifact_path).exists()


class ModelBank:
    """In-memory registry of known model artifacts.

    Models are registered at startup or programmatically via ``register``.
    The bank does not load model weights — that is ``ModelActor``'s job.
    """

    def __init__(self) -> None:
        """Initialise an empty registry."""
        self._registry: dict[str, ModelMetadata] = {}

    def register(self, metadata: ModelMetadata) -> None:
        """Add or replace a model entry in the registry.

        Args:
            metadata: Fully populated ``ModelMetadata`` for the model.
        """
        self._registry[metadata.model_id] = metadata

    def get(self, model_id: str) -> ModelMetadata:
        """Return metadata for *model_id*.

        Raises:
            KeyError: If *model_id* is not registered.
        """
        if model_id not in self._registry:
            raise KeyError(f"Model '{model_id}' not found in ModelBank.")
        return self._registry[model_id]

    def list_models(self, role: str | None = None) -> list[ModelMetadata]:
        """Return all registered models, optionally filtered by *role*.

        Args:
            role: If provided, only models whose ``role`` matches (or is "any").

        Returns:
            Sorted list of ``ModelMetadata`` by ``model_id``.
        """
        models = list(self._registry.values())
        if role is not None:
            models = [m for m in models if m.role in (role, "any")]
        return sorted(models, key=lambda m: m.model_id)

    def best_for_role(self, role: str) -> ModelMetadata | None:
        """Return the highest-win-rate registered model for *role*, or None."""
        candidates = self.list_models(role=role)
        if not candidates:
            return None
        return max(candidates, key=lambda m: m.win_rate)
