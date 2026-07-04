"""Unit tests for ModelBank and ModelMetadata."""

import pytest

from cop_thief.actors.model_bank import ModelBank, ModelMetadata


def _meta(model_id: str, role: str = "any", win_rate: float = 0.5) -> ModelMetadata:
    """Return a ModelMetadata fixture."""
    return ModelMetadata(
        model_id=model_id,
        version="0.1.0",
        role=role,
        win_rate=win_rate,
        artifact_path=f"models/{model_id}.onnx",
    )


def test_register_and_get():
    """Registered model is retrievable by id."""
    bank = ModelBank()
    bank.register(_meta("alpha"))
    assert bank.get("alpha").model_id == "alpha"


def test_get_unknown_raises():
    """Getting an unregistered model raises KeyError."""
    bank = ModelBank()
    with pytest.raises(KeyError, match="not found"):
        bank.get("nonexistent")


def test_list_models_returns_all():
    """list_models returns every registered model."""
    bank = ModelBank()
    bank.register(_meta("a"))
    bank.register(_meta("b"))
    assert len(bank.list_models()) == 2


def test_list_models_filter_by_role():
    """list_models(role='cop') returns only cop and 'any' models."""
    bank = ModelBank()
    bank.register(_meta("cop_model", role="cop"))
    bank.register(_meta("thief_model", role="thief"))
    bank.register(_meta("any_model", role="any"))
    cop_list = bank.list_models(role="cop")
    assert all(m.role in ("cop", "any") for m in cop_list)
    assert len(cop_list) == 2


def test_best_for_role_highest_win_rate():
    """best_for_role returns the model with the highest win_rate."""
    bank = ModelBank()
    bank.register(_meta("low", role="cop", win_rate=0.4))
    bank.register(_meta("high", role="cop", win_rate=0.8))
    best = bank.best_for_role("cop")
    assert best is not None
    assert best.model_id == "high"


def test_best_for_role_none_when_empty():
    """best_for_role returns None for an empty bank."""
    bank = ModelBank()
    assert bank.best_for_role("cop") is None


def test_register_overwrites_existing():
    """Re-registering the same model_id replaces the old entry."""
    bank = ModelBank()
    bank.register(_meta("m", win_rate=0.3))
    bank.register(_meta("m", win_rate=0.9))
    assert bank.get("m").win_rate == 0.9
