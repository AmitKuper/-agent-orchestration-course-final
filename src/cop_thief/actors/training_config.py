"""Training hyperparameter configuration — loaded from config files only.

No hyperparameters are hard-coded here. All values come from the config dict
passed to ``TrainingConfig.from_dict()``.
"""

from dataclasses import dataclass


@dataclass
class TrainingConfig:
    """Hyperparameters for the PPO/self-play training loop."""

    num_episodes: int = 1000
    learning_rate: float = 3e-4
    discount_gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_epsilon: float = 0.2
    entropy_coef: float = 0.01
    value_coef: float = 0.5
    batch_size: int = 64
    num_epochs: int = 4
    max_grad_norm: float = 0.5
    save_every_n_episodes: int = 100
    eval_every_n_episodes: int = 50

    def validate(self) -> None:
        """Raise ValueError if any hyperparameter is out of valid range."""
        if self.num_episodes < 1:
            raise ValueError("num_episodes must be >= 1")
        if not (0 < self.learning_rate < 1):
            raise ValueError("learning_rate must be in (0, 1)")
        if not (0 < self.discount_gamma <= 1):
            raise ValueError("discount_gamma must be in (0, 1]")
        if self.batch_size < 1:
            raise ValueError("batch_size must be >= 1")

    @classmethod
    def from_dict(cls, d: dict) -> "TrainingConfig":
        """Build a ``TrainingConfig`` from a config dict.

        Args:
            d: Flat dict of hyperparameter overrides.

        Returns:
            A validated ``TrainingConfig``.
        """
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        cfg = cls(**known)
        cfg.validate()
        return cfg
