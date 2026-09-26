"""RunConfigs P2pre / P2scr: PET2-small at step 1 (pretrained / scratch), our truth PET at step 2.

Both are derived from the predecessor's frozen efficiency-corrected configuration C
(`improvement_campaign/phase_b/pet/configs/b2e4-M-K10-s1.json`, sha256 `0afffb7d...`, checked by
`final_design/dev/make_dev_configs.base_config`) by replacing exactly:

* `arm = "theirs"` and `model_step1 = ModelSpec("theirs_pet2_small")` -- the PET2-small spec the
  predecessor's A1 phase declared (V1-paper flags, 2,758,702 parameters);
* `step1` = the DECLARED PET2 step-1 recipe, built by the predecessor's own
  `recipe.intended_theirs_step1` from the historical constants (`training_recipe.HIS_REFERENCE_RUN`:
  TorchAdamW lr 1e-4, weight decay 0.01, torch global-norm clip 1.0, batch 2048; warmup fraction
  `HIS_WARMUP_FRACTION` = 0.004 of each fit + cosine; `torch_adamw.TORCH_DEFAULTS` betas/epsilon),
  with C's step-1 validation split (identical split policy) and a configurable epoch count and
  across-iteration rate (default: the declared recipe's constant base rate; `anneal` = C's 1e-5
  after the first iteration);
* `step1.init` = the pinned pretrained export (P2pre) or scratch (P2scr) -- the ONLY difference
  between the two;
* `feature_arm = "pdg_onehot"` (categorical truth PDG at step 2, as the compact hybrid H1);
* `iterations = K`.

Step 2 is C's step 2 byte for byte, except (a) `--step2-iteration-lr constant` / the S1 candidates
(`P2preS1`, `P2scrS1`), which take the leading compact design's truth-step policy (H2S1: the same
rate at every iteration, `make_dev_configs._constant_lr`), and (b) a reduced epoch count for smoke
tests only. Manifests carry an 8th column `runner` (final_design/jobs/design_lib.sh dispatches on
it) and config paths relative to `improvement_campaign/confirm/configs`.
The miss rule is the efficiency-corrected step 2 (`--step2-miss-mode efficiency_corrected` in the
manifest's driver arguments). Seeds follow the predecessor's per-replicate rule
(`freeze_runs.seed_for` / `reseed`), shared by P2pre and P2scr on one replicate.

    python make_pet2_configs.py --stage pet2dev --selections F:0:dev --iterations 6 \
        --manifest ../runs/pet2dev.tsv
    python make_pet2_configs.py --stage dev2P --candidates P2preS1 P2scrS1 --iterations 5 \
        --selections F:0:dev F:1:dev T:0:D1_m0.350 T:1:D1_m0.350 T:0:D4c_p_up T:1:D4c_p_up \
        T:0:D4d_n_up T:1:D4d_n_up --nonfinite-momentum zero --nonfinite-addinfo zero \
        --manifest ../runs/dev2P.tsv
    python make_pet2_configs.py --stage pet2smoke --selections F:0:dev --iterations 2 \
        --step1-epochs 2 --step2-epochs 2 --manifest ../runs/pet2smoke.tsv
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PET = STUDY.parent
CAMPAIGN = PET / "improvement_campaign"
COMP = PET / "configuration_comparison"
for _p in (STUDY / "dev", CAMPAIGN / "confirm", CAMPAIGN):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(COMP) not in sys.path:
    sys.path.append(str(COMP))

import freeze_runs  # noqa: E402
import make_dev_configs as mdc  # noqa: E402
from recipe import (InitSpec, IterationLRSpec, ModelSpec, RunConfig, StoppingSpec,  # noqa: E402
                    intended_theirs_step1)

EFF = "efficiency_corrected"
VARIANTS = {"P2pre": "pretrained", "P2scr": "scratch"}
# candidate -> (step-1 init variant, forced step-2 across-iteration rate or None = the CLI's)
CANDIDATES = {"P2pre": ("pretrained", None), "P2scr": ("scratch", None),
              "P2preS1": ("pretrained", "constant"), "P2scrS1": ("scratch", "constant")}
RUNNER = "final_design/pet2/run_pet2_replicate.py"


def _a1_constants() -> Any:
    """The A1 phase's pinned pretrained-state paths (`phase_a/make_configs.py`), not retyped."""
    spec = importlib.util.spec_from_file_location("_a1_make_configs",
                                                  CAMPAIGN / "phase_a" / "make_configs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pet2_recipe_constants() -> dict[str, Any]:
    """The declared PET2 recipe's numbers, read from the historical modules (TensorFlow import)."""
    a1 = _a1_constants()
    return {"his_run": dict(a1.tr.HIS_REFERENCE_RUN),
            "torch_defaults": dict(a1.torch_adamw.TORCH_DEFAULTS),
            "warmup_fraction": float(a1.tr.HIS_WARMUP_FRACTION),
            "state": a1.STATE, "manifest": a1.MANIFEST, "state_sha256": a1.STATE_SHA}


def pet2_config(base: RunConfig, variant: str, constants: dict[str, Any], *, iterations: int,
                step1_epochs: int | None = None, step2_epochs: int | None = None,
                step1_iteration_lr: str = "constant", step1_batch: int | None = None,
                step1_learning_rate: float | None = None,
                step2_iteration_lr: str = "anneal") -> RunConfig:
    if variant not in VARIANTS.values():
        raise ValueError(f"variant {variant!r}")
    init = (InitSpec(policy="pretrained", pretrained_state=constants["state"],
                     pretrained_manifest=constants["manifest"],
                     pretrained_state_sha256=constants["state_sha256"])
            if variant == "pretrained" else InitSpec(policy="scratch"))
    epochs = int(step1_epochs if step1_epochs is not None else base.step1.stopping.max_epochs)
    step1 = intended_theirs_step1(his_run=constants["his_run"],
                                  torch_defaults=constants["torch_defaults"],
                                  warmup_fraction=constants["warmup_fraction"], epochs=epochs,
                                  pretrained=init, seed=base.step1.seed)
    iteration_lr = {"constant": IterationLRSpec(),
                    "anneal": base.step1.iteration_lr}[step1_iteration_lr]
    step1 = dataclasses.replace(step1, validation=base.step1.validation, iteration_lr=iteration_lr,
                                predict_batch_size=base.step1.predict_batch_size)
    if step1_batch is not None:
        step1 = dataclasses.replace(step1, batch_size=int(step1_batch))
    if step1_learning_rate is not None:
        step1 = dataclasses.replace(step1, optimizer=dataclasses.replace(
            step1.optimizer, learning_rate=float(step1_learning_rate)))
    step2 = {"anneal": base.step2,                        # C's: 1e-5 after the first iteration
             "constant": mdc._constant_lr(base.step2)}[step2_iteration_lr]   # H2S1's policy
    if step2_epochs is not None:
        step2 = dataclasses.replace(step2, stopping=dataclasses.replace(
            step2.stopping, max_epochs=int(step2_epochs)))
    config = base.replace(arm="theirs", model_step1=ModelSpec("theirs_pet2_small"), step1=step1,
                          step2=step2, feature_arm="pdg_onehot", iterations=int(iterations))
    config.validate()
    return config


def build(stage: str, candidates: list[str], selections: list[tuple[str, int, str]],
          iterations: int, out_dir: Path, manifest: Path, nonfinite_momentum: str = "refuse",
          nonfinite_addinfo: str = "refuse", step2_iteration_lr: str = "anneal",
          **kw: Any) -> list[str]:
    base = mdc.base_config()
    constants = pet2_recipe_constants()
    cfg_dir = out_dir / stage
    cfg_dir.mkdir(parents=True, exist_ok=True)
    rows = ["# name\tconfig\tconfig_hash\tselection\tdistortion\treference_run\t"
            "extra_driver_args\trunner"]
    for pool, r, dist in selections:
        if r not in mdc.DRAWN.get(pool, ()):
            raise SystemExit(f"[pet2] {pool}:{r} was not drawn by the predecessor; refused")
        seed = freeze_runs.seed_for(pool, r)
        tag = "" if dist == "dev" else f"-{dist.replace('+', '_')}"
        for cand in candidates:
            variant, forced = CANDIDATES[cand]
            s2lr = forced or step2_iteration_lr
            cfg = pet2_config(base, variant, constants, iterations=iterations,
                              step2_iteration_lr=s2lr, **kw)
            name = f"{stage}-{cand}-{pool}{r}{tag}"
            extra = ", ".join(f"{k}={v}" for k, v in sorted(kw.items()) if v is not None)
            if s2lr != "anneal":
                extra = ", ".join(x for x in (extra, f"step2_iteration_lr={s2lr}") if x)
            note = (f"{stage}: {cand} = PET2-small {variant} at step 1 (declared PET2 "
                    f"recipe) + C's step 2 with pdg_onehot, efficiency-corrected misses, "
                    f"K={iterations}{'; ' + extra if extra else ''}; base C {mdc.BASE[2][:12]}; "
                    f"pool {pool} replicate {r} (predecessor-drawn), seed {seed}; generated by "
                    "final_design/pet2/make_pet2_configs.py")
            cfg = freeze_runs.reseed(cfg, seed, name, note)
            (cfg_dir / f"{name}.json").write_text(cfg.to_json(indent=1) + "\n")
            rel = f"../../../final_design/configs/{stage}/{name}.json"   # from confirm/configs
            flags = f"--step2-miss-mode {EFF}"
            if nonfinite_momentum != "refuse":
                flags += f" --nonfinite-momentum {nonfinite_momentum}"
            if nonfinite_addinfo != "refuse":
                flags += f" --nonfinite-addinfo {nonfinite_addinfo}"
            rows.append("\t".join([name, rel, cfg.content_hash(), f"{pool}:{r}", dist, "-",
                                   flags, RUNNER]))
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(rows) + "\n")
    return rows[1:]


def main(argv: Any = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--candidates", nargs="+", default=sorted(VARIANTS), choices=sorted(CANDIDATES))
    ap.add_argument("--selections", nargs="+", required=True, help="POOL:REP:DISTORTION")
    ap.add_argument("--iterations", type=int, default=6)
    ap.add_argument("--step1-epochs", type=int, default=None, help="default: C's step-1 epochs")
    ap.add_argument("--step2-epochs", type=int, default=None,
                    help="smoke tests only (default: C's step 2 unchanged)")
    ap.add_argument("--step1-iteration-lr", choices=("constant", "anneal"), default="constant")
    ap.add_argument("--step1-batch", type=int, default=None, help="default: 2048 (declared)")
    ap.add_argument("--step1-learning-rate", type=float, default=None,
                    help="default: 1e-4 (declared); a tuning opportunity applies to both variants")
    ap.add_argument("--step2-iteration-lr", choices=("anneal", "constant"), default="anneal",
                    help="truth-step rate across iterations for P2pre/P2scr: C's anneal (1e-5 "
                         "after the first) or constant (H2S1's policy); P2preS1/P2scrS1 are "
                         "always constant")
    ap.add_argument("--nonfinite-momentum", choices=("refuse", "zero"), default="refuse",
                    help="driver argument written to the manifest (theirs_rows policy)")
    ap.add_argument("--nonfinite-addinfo", choices=("refuse", "zero"), default="refuse",
                    help="driver argument written to the manifest (theirs_rows policy)")
    ap.add_argument("--out-dir", type=Path, default=STUDY / "configs")
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args(argv)
    sels = []
    for s in a.selections:
        pool, r, dist = s.split(":", 2)
        sels.append((pool, int(r), dist))
    rows = build(a.stage, a.candidates, sels, a.iterations, a.out_dir, a.manifest,
                 nonfinite_momentum=a.nonfinite_momentum,
                 nonfinite_addinfo=a.nonfinite_addinfo, step2_iteration_lr=a.step2_iteration_lr,
                 step1_epochs=a.step1_epochs, step2_epochs=a.step2_epochs,
                 step1_iteration_lr=a.step1_iteration_lr, step1_batch=a.step1_batch,
                 step1_learning_rate=a.step1_learning_rate)
    print(f"{len(rows)} runs -> {a.manifest}")
    for row in rows:
        print(row.split("\t")[0], row.split("\t")[2][:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
