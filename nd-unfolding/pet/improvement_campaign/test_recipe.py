"""Recipe serialization, validation, and the executed-optimizer check (no TensorFlow)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recipe import (ClippingSpec, EndpointSpec, EventSplitSpec, InitSpec, ModelSpec,  # noqa: E402
                    OptimizerSpec, RecipeError, RunConfig, ScheduleSpec, StepRecipe,
                    StoppingSpec, OURS_PET_PARAMS, historical_as_executed_step)
from run_unfold import verify_executed_optimizer  # noqa: E402


def _config(**changes):
    step = StepRecipe(optimizer=OptimizerSpec("adam", 1e-4), batch_size=512,
                      stopping=StoppingSpec(max_epochs=8))
    base = RunConfig(name="t", arm="ours", step1=step, step2=step, iterations=3,
                     model_step1=ModelSpec("ours_pet", OURS_PET_PARAMS),
                     model_step2=ModelSpec("ours_pet", OURS_PET_PARAMS),
                     events=EventSplitSpec("tuning", 100_000, 0, 20260920),
                     endpoint=EndpointSpec(0.35, 3.0))
    return base.replace(**changes)


def test_json_round_trip_preserves_the_hash():
    config = _config()
    again = RunConfig.from_json(config.to_json(indent=2))
    assert again == config
    assert again.content_hash() == config.content_hash()


def test_any_change_changes_the_hash():
    config = _config()
    other = config.replace(step2=StepRecipe(optimizer=OptimizerSpec("adam", 1e-4),
                                            batch_size=2048, stopping=StoppingSpec(8)))
    assert other.content_hash() != config.content_hash()


@pytest.mark.parametrize("bad", [
    lambda: OptimizerSpec("adam", 1e-4, weight_decay=0.01).validate(),
    lambda: ClippingSpec("global_norm").validate(),
    lambda: ScheduleSpec("constant", warmup_fraction=0.1).validate(),
    lambda: InitSpec(policy="pretrained").validate(),
    lambda: StepRecipe(OptimizerSpec("adam", 1e-4), 64, StoppingSpec(2),
                       clipping=ClippingSpec("global_norm_torch", 1.0)).validate(),
    lambda: _config(arm="theirs").validate(),
])
def test_unexecutable_recipes_are_refused(bad):
    with pytest.raises(RecipeError):
        bad()


def test_historical_step_declares_what_the_audit_measured():
    step = historical_as_executed_step(batch_size=2048, learning_rate=1e-4, epochs=8,
                                       annealed_rate=1e-5)
    step.validate()
    assert step.optimizer.family == "adam" and step.optimizer.weight_decay == 0
    assert step.clipping.kind == "none" and step.schedule.kind == "constant"
    assert step.stopping.patience is None and step.stopping.restore == "last"
    assert step.iteration_lr.base_rate(1e-4, 0) == 1e-4
    assert step.iteration_lr.base_rate(1e-4, 2) == 1e-5


def _declared(**kw):
    base = {"family": "adam", "base_learning_rate": 1e-4, "schedule": "constant",
            "clipping": "none", "max_norm": None, "weight_decay": 0.0, "beta_1": 0.9,
            "beta_2": 0.999, "epsilon": 1e-7, "total_steps": 10}
    base.update(kw)
    return base


def _executed(**kw):
    base = {"class": "Adam", "module": "keras", "schedule_class": None,
            "base_learning_rate": 1e-4, "warmup_steps": None, "max_steps": None,
            "keras_weight_decay": None, "torch_weight_decay": None, "global_clipnorm": None,
            "clipnorm": None, "torch_grad_clip": None, "beta_1": 0.9, "beta_2": 0.999,
            "epsilon": 1e-7, "iterations": 0, "is_horovod_wrapped": False}
    base.update(kw)
    return base


def test_the_historical_executed_optimizer_fails_his_declared_recipe():
    """The executed object the audit found (Horovod Adam, no decay/clip/schedule) is refused
    against his declared TorchAdamW recipe -- the check the historical driver never made."""
    declared = _declared(family="torch_adamw", schedule="warmup_cosine",
                         clipping="global_norm_torch", max_norm=1.0, weight_decay=0.01,
                         epsilon=1e-8, warmup_steps=1, total_steps=100)
    executed = _executed(module="horovod._keras", is_horovod_wrapped=True)
    problems = verify_executed_optimizer(executed, declared)
    assert any("class" in p for p in problems)
    assert any("weight decay" in p for p in problems)
    assert any("clip" in p for p in problems)
    assert any("schedule" in p for p in problems)
    assert any("Horovod" in p for p in problems)


def test_a_matching_optimizer_passes():
    assert verify_executed_optimizer(_executed(), _declared()) == []
    assert verify_executed_optimizer(_executed(iterations=3), _declared()) != []
