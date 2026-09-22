"""Write the RunConfig JSONs of the A1 runtime check and cost measurement.

Every number the historical design froze is READ from it: the split seed and endpoint from
`frozen_design`, his reference run, warmup fraction and epochs from `training_recipe`, torch's
AdamW defaults from `torch_adamw`, and the per-arm selected learning rate from the tuning
selection the campaign itself wrote (`receipts/historical_receipts.json` -> tuning_selection).

The two arms share ONE explicit step-2 recipe (the incumbent as executed: Adam at our selected
rate, 1e-5 after the first iteration, batch 512) -- the truth side is held fixed while step 1 varies.
His step 1 is his DECLARED recipe (TorchAdamW + warmup/cosine + torch clip, pretrained).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
COMP = CAMPAIGN.parent / "configuration_comparison"
sys.path[:0] = [str(CAMPAIGN), str(COMP)]

import frozen_design as fd  # noqa: E402
from keras_backend import select_keras_backend  # noqa: E402

select_keras_backend()
import torch_adamw  # noqa: E402
import training_recipe as tr  # noqa: E402
from recipe import (EndpointSpec, EventSplitSpec, InitSpec, IterationLRSpec, ModelSpec,  # noqa: E402
                    OURS_PET_PARAMS, OptimizerSpec, RunConfig, StepRecipe, StoppingSpec,
                    ValidationSpec, intended_theirs_step1)

STATE = "/pscratch/sd/j/josephrb/pet-checkpoints-20260919/pretrained_state_s.npz"
MANIFEST = "/pscratch/sd/j/josephrb/pet-checkpoints-20260919/PRETRAINED_STATE_MANIFEST.json"
STATE_SHA = fd.PINNED_HASHES["pretrained_state_npz"]
ANNEALED_RATE = 1e-5   # omnifold.py:376 get_optimizer(min_learning_rate=1e-5), measured in L1/L2


def selected_rates() -> dict[str, float]:
    selection = json.loads((HERE / "receipts" / "historical_receipts.json").read_text())
    chosen = selection["tuning_selection"]["content"]["selected"]
    return {arm: float(chosen[arm]["learning_rate"]) for arm in ("ours", "theirs")}


def configs(stage: str, max_events: int, iterations: int, epochs: int, tag: str):
    rates = selected_rates()
    events = EventSplitSpec(stage=stage, max_events=max_events, subsample_seed=0,
                            split_seed=int(fd.SPLITS["split_seed"]))
    endpoint = EndpointSpec(amplitude=float(fd.ENDPOINT["amplitude"]),
                            clip=float(fd.ENDPOINT["clip"]))
    shared_step2 = StepRecipe(
        optimizer=OptimizerSpec("adam", rates["ours"]), batch_size=fd.OURS_INCUMBENT["batch_size"],
        stopping=StoppingSpec(max_epochs=epochs, restore="best"),
        validation=ValidationSpec(fraction=round(1 - tr.TRAIN_FRAC, 12), unit="event", seed=2),
        iteration_lr=IterationLRSpec("anneal_after_first", ANNEALED_RATE), seed=2)
    ours_step1 = StepRecipe(
        optimizer=OptimizerSpec("adam", rates["ours"]), batch_size=fd.OURS_INCUMBENT["batch_size"],
        stopping=StoppingSpec(max_epochs=epochs, restore="best"),
        validation=ValidationSpec(fraction=round(1 - tr.TRAIN_FRAC, 12), unit="event", seed=1),
        iteration_lr=IterationLRSpec("anneal_after_first", ANNEALED_RATE), seed=1)
    pretrained = InitSpec(policy="pretrained", pretrained_state=STATE,
                          pretrained_manifest=MANIFEST, pretrained_state_sha256=STATE_SHA)
    theirs_step1 = intended_theirs_step1(
        his_run=tr.HIS_REFERENCE_RUN, torch_defaults=torch_adamw.TORCH_DEFAULTS,
        warmup_fraction=tr.HIS_WARMUP_FRACTION, epochs=epochs, pretrained=pretrained, seed=1)
    theirs_step1 = StepRecipe(**{**theirs_step1.__dict__, "validation": ours_step1.validation})
    common = dict(iterations=iterations, events=events, endpoint=endpoint,
                  model_step2=ModelSpec("ours_pet", OURS_PET_PARAMS))
    out = {
        "ours": RunConfig(name=f"A1-{tag}-ours", arm="ours", step1=ours_step1,
                          step2=shared_step2, model_step1=ModelSpec("ours_pet", OURS_PET_PARAMS),
                          note="incumbent recipe made explicit per step", **common),
        "theirs": RunConfig(name=f"A1-{tag}-theirs", arm="theirs", step1=theirs_step1,
                            step2=shared_step2, model_step1=ModelSpec("theirs_pet2_small"),
                            note="his DECLARED step-1 recipe; step 2 shared with ours", **common),
    }
    for config in out.values():
        config.validate()
    return out


if __name__ == "__main__":
    plans = {"check": ("tuning", 100_000, 2, 2), "cost": ("final", 2_000_000, 1, 1)}
    for tag, (stage, events, iterations, epochs) in plans.items():
        for arm, config in configs(stage, events, iterations, epochs, tag).items():
            path = HERE / "configs" / f"{tag}_{arm}.json"
            path.write_text(config.to_json(indent=1) + "\n")
            print(path.name, config.content_hash()[:16], config.step1.optimizer.family,
                  config.step1.batch_size, config.step2.batch_size)
