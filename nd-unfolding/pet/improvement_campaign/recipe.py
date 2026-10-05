"""Explicit, hashed per-step training recipes for the PET improvement campaign.

The historical comparison declared one recipe per arm and executed another (see
`phase_a/INTENDED_VS_EXECUTED-20260922.md`): the engine took ONE batch size and ONE learning rate
for both OmniFold steps, built its own Adam, annealed every later iteration to 1e-5, and ran an
early-stopping rule that could not fire. Here every OmniFold step carries its own frozen
`StepRecipe`, and `run_unfold.py` builds the optimizer, schedule, clipping, batches, split,
initialization and stopping from it and nothing else, then verifies the EXECUTED objects against it.

Everything is a frozen dataclass so a recipe cannot drift after it is hashed, and `RunConfig`
serializes to canonical JSON whose sha256 is the run's identity. This module imports no
TensorFlow, so configurations can be written, hashed and tested anywhere.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

SCHEMA = "pet-improvement-run-config-v1"

OPTIMIZER_FAMILIES = ("adam", "adamw", "torch_adamw")
SCHEDULE_KINDS = ("constant", "warmup_cosine")
CLIPPING_KINDS = ("none", "global_norm", "global_norm_torch")
RESTORE_POLICIES = ("last", "best")
SPLIT_UNITS = ("row", "event")
INIT_POLICIES = ("scratch", "pretrained")
ACROSS_ITERATIONS = ("warm_start", "reinitialize")
ITERATION_LR_KINDS = ("constant", "anneal_after_first")
MODEL_KINDS = ("ours_pet", "theirs_pet2_small")


class RecipeError(ValueError):
    """A recipe that cannot be executed as written."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RecipeError(message)


@dataclass(frozen=True)
class OptimizerSpec:
    family: str
    learning_rate: float
    beta_1: float = 0.9
    beta_2: float = 0.999
    epsilon: float = 1e-7
    weight_decay: float = 0.0

    def validate(self) -> None:
        _require(self.family in OPTIMIZER_FAMILIES, f"optimizer family {self.family!r}")
        _require(self.learning_rate > 0, "learning_rate must be positive")
        _require(self.weight_decay >= 0, "weight_decay must be >= 0")
        _require(self.family != "adam" or self.weight_decay == 0,
                 "plain Adam has no decoupled weight decay; use adamw or torch_adamw")


@dataclass(frozen=True)
class ScheduleSpec:
    """Within-fit learning-rate schedule. Total steps = epochs x updates per epoch, derived at
    run time from the step's own batch and rows and recorded."""
    kind: str = "constant"
    warmup_fraction: float = 0.0

    def validate(self) -> None:
        _require(self.kind in SCHEDULE_KINDS, f"schedule kind {self.kind!r}")
        _require(0 <= self.warmup_fraction < 1, "warmup_fraction must be in [0, 1)")
        _require(self.kind == "warmup_cosine" or self.warmup_fraction == 0,
                 "a constant schedule has no warmup")


@dataclass(frozen=True)
class ClippingSpec:
    """`global_norm` is Keras `global_clipnorm`; `global_norm_torch` is torch's
    `clip_grad_norm_` (divides by norm + 1e-6), available only with `torch_adamw`."""
    kind: str = "none"
    max_norm: float | None = None

    def validate(self) -> None:
        _require(self.kind in CLIPPING_KINDS, f"clipping kind {self.kind!r}")
        _require((self.kind == "none") == (self.max_norm is None),
                 "max_norm must be set exactly when clipping is enabled")
        _require(self.max_norm is None or self.max_norm > 0, "max_norm must be positive")


@dataclass(frozen=True)
class StoppingSpec:
    """`patience=None` trains exactly `max_epochs`. `restore` says which weights leave the fit:
    the last epoch's, or the best-monitored epoch's -- applied by the driver itself, so it does
    not depend on whether a Keras callback happened to fire."""
    max_epochs: int
    patience: int | None = None
    min_delta: float = 0.0
    monitor: str = "val_loss"
    restore: str = "last"

    def validate(self) -> None:
        _require(self.max_epochs >= 1, "max_epochs must be >= 1")
        _require(self.patience is None or self.patience >= 1, "patience must be >= 1")
        _require(self.restore in RESTORE_POLICIES, f"restore {self.restore!r}")
        _require(self.monitor == "val_loss", "only val_loss is monitored")


@dataclass(frozen=True)
class ValidationSpec:
    """Held-out rows, drawn with their OWN seeded generator (not the global NumPy state), so the
    split of one step cannot depend on what another step or arm consumed. `unit='event'` keeps
    the two copies of a step-2 event (label 0 and label 1) on the same side."""
    fraction: float = 0.2
    unit: str = "event"
    seed: int = 0
    fixed_across_iterations: bool = True

    def validate(self) -> None:
        _require(0 < self.fraction < 1, "validation fraction must be in (0, 1)")
        _require(self.unit in SPLIT_UNITS, f"validation unit {self.unit!r}")


@dataclass(frozen=True)
class InitSpec:
    policy: str = "scratch"
    across_iterations: str = "warm_start"
    pretrained_state: str | None = None
    pretrained_manifest: str | None = None
    pretrained_state_sha256: str | None = None

    def validate(self) -> None:
        _require(self.policy in INIT_POLICIES, f"init policy {self.policy!r}")
        _require(self.across_iterations in ACROSS_ITERATIONS,
                 f"across_iterations {self.across_iterations!r}")
        if self.policy == "pretrained":
            _require(bool(self.pretrained_state and self.pretrained_state_sha256),
                     "a pretrained init needs the state path and its sha256")
        else:
            _require(self.pretrained_state is None, "scratch init must not name a state")


@dataclass(frozen=True)
class IterationLRSpec:
    """How the base rate changes across OmniFold iterations. `anneal_after_first` reproduces the
    adopted production anneal (every fit after the first at `later_learning_rate`)."""
    kind: str = "constant"
    later_learning_rate: float | None = None

    def validate(self) -> None:
        _require(self.kind in ITERATION_LR_KINDS, f"iteration lr kind {self.kind!r}")
        _require((self.kind == "anneal_after_first") == (self.later_learning_rate is not None),
                 "later_learning_rate is set exactly for anneal_after_first")

    def base_rate(self, first_rate: float, iteration: int) -> float:
        if self.kind == "anneal_after_first" and iteration > 0:
            return float(self.later_learning_rate)
        return float(first_rate)


@dataclass(frozen=True)
class StepRecipe:
    optimizer: OptimizerSpec
    batch_size: int
    stopping: StoppingSpec
    schedule: ScheduleSpec = field(default_factory=ScheduleSpec)
    clipping: ClippingSpec = field(default_factory=ClippingSpec)
    validation: ValidationSpec = field(default_factory=ValidationSpec)
    init: InitSpec = field(default_factory=InitSpec)
    iteration_lr: IterationLRSpec = field(default_factory=IterationLRSpec)
    seed: int = 0
    predict_batch_size: int = 4096

    def validate(self) -> None:
        for part in (self.optimizer, self.stopping, self.schedule, self.clipping,
                     self.validation, self.init, self.iteration_lr):
            part.validate()
        _require(self.batch_size >= 1, "batch_size must be >= 1")
        _require(self.clipping.kind != "global_norm_torch" or
                 self.optimizer.family == "torch_adamw",
                 "torch-style clipping is implemented by ClippedTorchAdamW only")
        _require(self.clipping.kind != "global_norm" or self.optimizer.family != "torch_adamw",
                 "TorchAdamW clips the torch way; use global_norm_torch")


@dataclass(frozen=True)
class ModelSpec:
    """Architecture by name. `params` is a sorted tuple of (name, value) so it stays hashable."""
    kind: str
    params: tuple = ()

    def validate(self) -> None:
        _require(self.kind in MODEL_KINDS, f"model kind {self.kind!r}")

    def kwargs(self) -> dict[str, Any]:
        return {k: (tuple(v) if isinstance(v, list) else v) for k, v in self.params}


@dataclass(frozen=True)
class EventSplitSpec:
    """Which events: the historical stage split (identity-hashed) and the two disjoint halves."""
    stage: str
    max_events: int
    subsample_seed: int
    split_seed: int
    half_size: int | None = None

    def validate(self) -> None:
        _require(self.stage in ("tuning", "pilot", "final"), f"stage {self.stage!r}")
        _require(self.max_events > 0, "max_events must be positive")


@dataclass(frozen=True)
class EndpointSpec:
    """The injected truth tilt (pseudo-data construction)."""
    amplitude: float
    clip: float


@dataclass(frozen=True)
class RunConfig:
    name: str
    arm: str
    step1: StepRecipe
    step2: StepRecipe
    iterations: int
    model_step1: ModelSpec
    model_step2: ModelSpec
    events: EventSplitSpec
    endpoint: EndpointSpec
    feature_arm: str = "baseline"
    note: str = ""
    schema: str = SCHEMA

    def validate(self) -> None:
        _require(self.arm in ("ours", "theirs"), f"arm {self.arm!r} (input representation)")
        _require(self.iterations >= 1, "iterations must be >= 1")
        self.step1.validate()
        self.step2.validate()
        self.model_step1.validate()
        self.model_step2.validate()
        self.events.validate()
        _require(self.model_step2.kind == "ours_pet",
                 "step 2 runs the truth-side PET; his vocabulary has no truth analogue")
        _require((self.arm == "theirs") == (self.model_step1.kind == "theirs_pet2_small"),
                 "the theirs arm is his PET2 on his tokens; ours is our PET on our cloud")
        _require(self.step2.init.policy == "scratch", "the truth-side PET has no pretrained state")

    # ---- serialization ------------------------------------------------------------------ #
    def to_dict(self) -> dict[str, Any]:
        return _plain(dataclasses.asdict(self))

    def to_json(self, indent: int | None = None) -> str:
        if indent is None:
            return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return json.dumps(self.to_dict(), sort_keys=True, indent=indent)

    def content_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunConfig":
        if data.get("schema") != SCHEMA:
            raise RecipeError(f"schema {data.get('schema')!r} is not {SCHEMA!r}")
        d = dict(data)
        d["step1"] = _step_from(d["step1"])
        d["step2"] = _step_from(d["step2"])
        d["model_step1"] = _model_from(d["model_step1"])
        d["model_step2"] = _model_from(d["model_step2"])
        d["events"] = EventSplitSpec(**d["events"])
        d["endpoint"] = EndpointSpec(**d["endpoint"])
        config = cls(**d)
        config.validate()
        return config

    @classmethod
    def from_json(cls, text: str) -> "RunConfig":
        return cls.from_dict(json.loads(text))

    def replace(self, **changes: Any) -> "RunConfig":
        return dataclasses.replace(self, **changes)


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _model_from(d: dict[str, Any]) -> ModelSpec:
    params = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in d.get("params", ()))
    return ModelSpec(kind=d["kind"], params=tuple(sorted(params)))


def _step_from(d: dict[str, Any]) -> StepRecipe:
    return StepRecipe(
        optimizer=OptimizerSpec(**d["optimizer"]), batch_size=d["batch_size"],
        stopping=StoppingSpec(**d["stopping"]), schedule=ScheduleSpec(**d["schedule"]),
        clipping=ClippingSpec(**d["clipping"]), validation=ValidationSpec(**d["validation"]),
        init=InitSpec(**d["init"]), iteration_lr=IterationLRSpec(**d["iteration_lr"]),
        seed=d["seed"], predict_batch_size=d["predict_batch_size"])


def model_params(**kwargs: Any) -> tuple:
    return tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in kwargs.items()))


# ---------------------------------------------------------------------------------------------- #
# Named recipes. Numbers that the historical design froze are READ from it (`frozen_design`,
# `training_recipe`), passed in by the caller that has those modules loaded, never retyped here.
# ---------------------------------------------------------------------------------------------- #
OURS_PET_PARAMS = model_params(num_transformer=2, num_heads=2, projection_dim=32, local=True, K=3)


def historical_as_executed_step(*, batch_size: int, learning_rate: float, epochs: int,
                                annealed_rate: float, pretrained: InitSpec | None = None
                                ) -> StepRecipe:
    """What the historical engine ACTUALLY ran for one step (runtime audit, job 58742195).

    Horovod-wrapped Keras Adam (0.9, 0.999, 1e-7), constant rate, no clipping, no decay, fresh
    optimizer per fit, `epochs` fixed with an inert early-stopping rule (the last epoch's weights
    leave the fit), every fit after the first at `annealed_rate`, row-level 20 % split, warm start.
    The validation split's global-RNG coupling is not reproduced: it is seeded here.
    """
    return StepRecipe(
        optimizer=OptimizerSpec(family="adam", learning_rate=learning_rate),
        batch_size=batch_size,
        stopping=StoppingSpec(max_epochs=epochs, patience=None, restore="last"),
        validation=ValidationSpec(fraction=0.2, unit="row"),
        init=pretrained or InitSpec(),
        iteration_lr=IterationLRSpec(kind="anneal_after_first",
                                     later_learning_rate=annealed_rate))


def intended_theirs_step1(*, his_run: dict[str, Any], torch_defaults: dict[str, Any],
                          warmup_fraction: float, epochs: int, pretrained: InitSpec,
                          seed: int = 0) -> StepRecipe:
    """His declared step-1 recipe: TorchAdamW + warmup/cosine + torch global-norm clip.

    `his_run` is `training_recipe.HIS_REFERENCE_RUN`, `torch_defaults` is
    `torch_adamw.TORCH_DEFAULTS`, `warmup_fraction` is `training_recipe.HIS_WARMUP_FRACTION`.
    """
    return StepRecipe(
        optimizer=OptimizerSpec(family="torch_adamw", learning_rate=his_run["learning_rate"],
                                beta_1=torch_defaults["beta_1"], beta_2=torch_defaults["beta_2"],
                                epsilon=torch_defaults["epsilon"],
                                weight_decay=his_run["weight_decay"]),
        batch_size=his_run["batch_size"],
        stopping=StoppingSpec(max_epochs=epochs),
        schedule=ScheduleSpec(kind="warmup_cosine", warmup_fraction=warmup_fraction),
        clipping=ClippingSpec(kind="global_norm_torch", max_norm=his_run["grad_clip"]),
        init=pretrained, seed=seed)
