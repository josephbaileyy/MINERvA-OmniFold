"""Write the RunConfig JSONs of task B2 (development-stage PET diagnostics and feature arms).

Every number the historical design froze is READ from it: the split seed, endpoint and the
incumbent's batch from `frozen_design`; epochs and the train fraction from `training_recipe`
(parsed, not imported, so this runs without TensorFlow); the selected iteration-0 rate from the
tuning selection the historical campaign wrote (`phase_a/receipts/historical_receipts.json`); the
forced later rate is the engine's `get_optimizer(min_learning_rate=1e-5)`, measured at runtime by
A1 (L1/L2 in `phase_a/INTENDED_VS_EXECUTED-20260922.md`).

Recipes (both OmniFold steps unless stated):

* ``H``  -- the historical as-executed `ours` recipe (`recipe.historical_as_executed_step`): Adam
  (0.9, 0.999, 1e-7), iteration-0 rate 4e-4 then 1e-5 forced, batch 512, 8 epochs, no stopping,
  LAST-epoch weights, row-level 20 % validation split, warm start across iterations.
* ``S1`` -- H with the iteration-0 rate kept at every iteration (no forced 1e-5).
* ``S2`` -- H handing on the best-validation-epoch weights instead of the last epoch's.
* ``S3`` -- H with twice the epochs (16) and patience 4 on the validation loss, last-epoch weights.

Seeds: a run's `seed` drives the step seeds and the validation split; seeds here are campaign
labels, NOT the historical estimator seeds (the historical global-RNG consumption is not
reproduced, A1).

Run as `python make_b2_configs.py` from anywhere; writes `configs/*.json` beside this file and
prints each config's content hash.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1]
PET = CAMPAIGN.parent
COMP = PET / "configuration_comparison"
sys.path[:0] = [str(CAMPAIGN), str(COMP)]

import frozen_design as fd  # noqa: E402
from recipe import (EndpointSpec, EventSplitSpec, IterationLRSpec, ModelSpec,  # noqa: E402
                    OURS_PET_PARAMS, RunConfig, StepRecipe, StoppingSpec,
                    historical_as_executed_step)

ANNEALED_RATE = 1e-5   # omnifold.py:376 get_optimizer(min_learning_rate=1e-5), measured by A1
CONFIG_DIR = HERE / "configs"


def training_recipe_constant(name: str) -> Any:
    """A module-level constant of `training_recipe.py`, read from its source (no TF import)."""
    tree = ast.parse((COMP / "training_recipe.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name
                                                for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(f"training_recipe.{name} not found")


def selected_rate(arm: str = "ours") -> float:
    receipts = CAMPAIGN / "phase_a" / "receipts" / "historical_receipts.json"
    chosen = json.loads(receipts.read_text())["tuning_selection"]["content"]["selected"]
    return float(chosen[arm]["learning_rate"])


EPOCHS = int(training_recipe_constant("EPOCHS"))
TRAIN_FRAC = float(training_recipe_constant("TRAIN_FRAC"))
TRAIN_EVENTS = int(training_recipe_constant("TRAIN_EVENTS"))


def h_step(seed: int) -> StepRecipe:
    step = historical_as_executed_step(batch_size=int(fd.OURS_INCUMBENT["batch_size"]),
                                       learning_rate=selected_rate("ours"), epochs=EPOCHS,
                                       annealed_rate=ANNEALED_RATE)
    validation = dataclasses.replace(step.validation, fraction=round(1 - TRAIN_FRAC, 12),
                                     seed=int(seed))
    return dataclasses.replace(step, validation=validation, seed=int(seed))


def schedule_variant(step: StepRecipe, variant: str) -> StepRecipe:
    """One schedule factor changed relative to H (exp. 4); combinations join with '+'."""
    for part in variant.split("+"):
        if part == "H":
            continue
        if part == "S1":
            step = dataclasses.replace(step, iteration_lr=IterationLRSpec("constant"))
        elif part == "S2":
            step = dataclasses.replace(step, stopping=dataclasses.replace(step.stopping,
                                                                          restore="best"))
        elif part == "S3":
            step = dataclasses.replace(step, stopping=dataclasses.replace(
                step.stopping, max_epochs=2 * EPOCHS, patience=4))
        else:
            raise ValueError(f"unknown schedule factor {part!r}")
    return step


def truth_only_step(seed: int, epochs: int) -> StepRecipe:
    """Exp. 2: the H step-2 fit at its iteration-0 rate, run `epochs` epochs with the
    best-validation epoch handed on. Epochs 1-8 are the historical 8-epoch fit (same seeds, same
    constant rate); the per-epoch evaluation records both."""
    step = h_step(seed)
    return dataclasses.replace(step, stopping=dataclasses.replace(
        step.stopping, max_epochs=int(epochs), restore="best"))


def run_config(name: str, *, seed: int, iterations: int, schedule: str = "H",
               feature_arm: str = "baseline", note: str = "", stage: str = "final",
               max_events: int | None = None, epochs: int | None = None,
               step2: StepRecipe | None = None) -> RunConfig:
    events = EventSplitSpec(stage=stage, max_events=int(max_events or TRAIN_EVENTS),
                            subsample_seed=0, split_seed=int(fd.SPLITS["split_seed"]))
    endpoint = EndpointSpec(amplitude=float(fd.ENDPOINT["amplitude"]),
                            clip=float(fd.ENDPOINT["clip"]))
    s1 = schedule_variant(h_step(seed), schedule)
    s2 = step2 or schedule_variant(h_step(seed), schedule)
    if epochs is not None:
        s1 = dataclasses.replace(s1, stopping=dataclasses.replace(s1.stopping,
                                                                  max_epochs=int(epochs)))
        s2 = dataclasses.replace(s2, stopping=dataclasses.replace(s2.stopping,
                                                                  max_epochs=int(epochs)))
    config = RunConfig(
        name=name, arm="ours", step1=s1, step2=s2,
        iterations=int(iterations),
        model_step1=ModelSpec("ours_pet", OURS_PET_PARAMS),
        model_step2=ModelSpec("ours_pet", OURS_PET_PARAMS),
        events=events, endpoint=endpoint, feature_arm=feature_arm, note=note)
    config.validate()
    return config


def experiment_1() -> dict[str, RunConfig]:
    """Driver faithfulness: H through the A1 driver, K = 3, seeds 1-4."""
    return {f"b2e1-H-K3-s{s}": run_config(f"b2e1-H-K3-s{s}", seed=s, iterations=3,
                                          note="B2 exp 1: historical as-executed ours recipe")
            for s in (1, 2, 3, 4)}


def dev() -> dict[str, RunConfig]:
    """Mechanics checks on the tuning stage (100k events): unfold 2 x 2 epochs, truth-only."""
    out = {"b2dev-unfold": run_config("b2dev-unfold", seed=1, iterations=2, stage="tuning",
                                      max_events=100_000, epochs=2, note="B2 mechanics check"),
           "b2dev-unfold-arm": run_config("b2dev-unfold-arm", seed=1, iterations=2,
                                          stage="tuning", max_events=100_000, epochs=2,
                                          feature_arm="reco_summaries_pdg_onehot_truthglobals",
                                          note="B2 mechanics check, all transforms")}
    for arm in ("baseline", "pdg_onehot_truthglobals"):
        name = f"b2dev-truth-{arm}"
        out[name] = run_config(name, seed=1, iterations=1, stage="tuning", max_events=100_000,
                               feature_arm=arm, step2=truth_only_step(1, 3),
                               note="B2 mechanics check, truth-only")
    return out


T_ARMS = {"T0": "baseline", "T1": "pdg_onehot", "T2": "pdg_onehot_truthglobals"}


def experiment_2() -> dict[str, RunConfig]:
    """Truth-only learnability of the KNOWN tilt, step 2 alone, 32 epochs, seeds 1-2."""
    out = {}
    for tag, arm in T_ARMS.items():
        for s in (1, 2):
            name = f"b2e2-{tag}-s{s}"
            out[name] = run_config(name, seed=s, iterations=1, feature_arm=arm,
                                   step2=truth_only_step(s, 4 * EPOCHS),
                                   note=f"B2 exp 2 {tag}: truth-only learnability ({arm})")
    return out


def experiment_3() -> dict[str, RunConfig]:
    """H at K = 10 (step-wise closure; also the reference arm of exp. 4), seeds 1-2."""
    return {f"b2e3-H-K10-s{s}": run_config(f"b2e3-H-K10-s{s}", seed=s, iterations=10,
                                           note="B2 exp 3 / exp 4 reference: H at K=10")
            for s in (1, 2)}


def experiment_4() -> dict[str, RunConfig]:
    """Schedule factors one at a time against H, K = 10, seeds 1-2."""
    out = {}
    for variant in ("S1", "S2", "S3"):
        for s in (1, 2):
            name = f"b2e4-{variant}-K10-s{s}"
            out[name] = run_config(name, seed=s, iterations=10, schedule=variant,
                                   note=f"B2 exp 4: schedule factor {variant} vs H")
    return out


PLANS = {"e1": experiment_1, "dev": dev, "e2": experiment_2, "e3": experiment_3,
         "e4": experiment_4}


def write(plans: list[str]) -> None:
    CONFIG_DIR.mkdir(exist_ok=True)
    for plan in plans:
        for name, config in PLANS[plan]().items():
            path = CONFIG_DIR / f"{name}.json"
            path.write_text(config.to_json(indent=1) + "\n")
            print(path.name, config.content_hash()[:16], config.iterations,
                  config.step1.stopping.max_epochs, config.step1.iteration_lr.kind,
                  config.step1.stopping.restore)


if __name__ == "__main__":
    write(sys.argv[1:] or sorted(PLANS))
