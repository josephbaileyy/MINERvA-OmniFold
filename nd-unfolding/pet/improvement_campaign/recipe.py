import dataclasses
import hashlib
import json
from typing import Any, Dict, Optional

@dataclasses.dataclass(frozen=True)
class OptimizerRecipe:
    family: str  # "Adam", "AdamW", "TorchAdamW"
    learning_rate: float
    weight_decay: float = 0.0
    beta_1: float = 0.9
    beta_2: float = 0.999
    epsilon: float = 1e-7
    global_clipnorm: Optional[float] = None
    warmup_steps: int = 0
    cosine_decay_steps: int = 0

@dataclasses.dataclass(frozen=True)
class StepRecipe:
    optimizer: OptimizerRecipe
    batch_size: int
    epochs: int
    patience: int
    early_stopping_monitor: str = "val_loss"
    validation_fraction: float = 0.2
    pretrained_weights: Optional[str] = None
    reinitialize_heads: bool = False
    model_seed: int = 42

@dataclasses.dataclass(frozen=True)
class RunRecipe:
    step1: StepRecipe
    step2: StepRecipe
    iterations: int
    arm_id: str
    event_split_seed: int

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

