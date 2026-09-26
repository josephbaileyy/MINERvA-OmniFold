"""Development-stage RunConfigs and run manifests for the PET final-design study (DEV bank only).

Each candidate is the predecessor's frozen efficiency-corrected configuration C
(`improvement_campaign/phase_b/pet/configs/b2e4-M-K10-s1.json`, sha256 `0afffb7d…`) with a declared,
minimal set of fields replaced; everything else is inherited byte-for-byte through `RunConfig`.
Seeds follow the predecessor's per-replicate rule (`freeze_runs.seed_for`), so a new candidate on
pool T replicate 0 shares events AND seeds with the committed predecessor run on the same
(pool, replicate, distortion): the contrast isolates the declared change.

Only predecessor replicate selections that were already drawn (family
`confirm-historical-size-v1`: P0-2, F0-11, S0, T0-1) are allowed here, so no development run can
touch a never-drawn row (the study's final bank FB) or pool R (reserve bank RB).

    python make_dev_configs.py --stage dev1 --candidates H1 H2 H2S1 CS1 --out-dir ../configs
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CAMPAIGN = STUDY.parent / "improvement_campaign"
for p in (CAMPAIGN, CAMPAIGN / "confirm"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from recipe import RunConfig  # noqa: E402
import freeze_runs  # noqa: E402

BASE = ("C", CAMPAIGN / "phase_b/pet/configs/b2e4-M-K10-s1.json",
        "0afffb7d4402a1dbb32f28397b53bd05c9378c21c907624fc75450dfaa35a9f2")
DRAWN = {"P": range(3), "F": range(12), "S": range(1), "T": range(2)}
EFF = "efficiency_corrected"


def _constant_lr(step: Any) -> Any:
    return dataclasses.replace(step, iteration_lr=dataclasses.replace(
        step.iteration_lr, kind="constant", later_learning_rate=None))


def _model(params: dict[str, Any]) -> Callable[[RunConfig], RunConfig]:
    def f(c: RunConfig) -> RunConfig:
        m = dict(c.model_step1.params)
        m.update(params)
        return c.replace(model_step1=dataclasses.replace(c.model_step1,
                                                         params=tuple(sorted(m.items()))))
    return f


def _epochs1(n: int) -> Callable[[RunConfig], RunConfig]:
    def f(c: RunConfig) -> RunConfig:
        return c.replace(step1=dataclasses.replace(
            c.step1, stopping=dataclasses.replace(c.step1.stopping, max_epochs=int(n))))
    return f


def _epochs2(n: int) -> Callable[[RunConfig], RunConfig]:
    def f(c: RunConfig) -> RunConfig:
        return c.replace(step2=dataclasses.replace(
            c.step2, stopping=dataclasses.replace(c.step2.stopping, max_epochs=int(n))))
    return f


# candidate id -> (description, transform of the base config, miss rule)
CANDIDATES: dict[str, tuple[str, Callable[[RunConfig], RunConfig], str]] = {
    "Cref": ("C as frozen by the predecessor (reference)", lambda c: c, EFF),
    "H1": ("C + categorical truth PDG (13-category one-hot)",
           lambda c: c.replace(feature_arm="pdg_onehot"), EFF),
    "H2": ("H1 + detector-only reco summaries at step 1",
           lambda c: c.replace(feature_arm="reco_summaries_pdg_onehot"), EFF),
    "H2S1": ("H2 with a constant learning rate at every iteration (no forced 1e-5), both steps",
             lambda c: c.replace(feature_arm="reco_summaries_pdg_onehot",
                                 step1=_constant_lr(c.step1), step2=_constant_lr(c.step2)), EFF),
    "CS1": ("C with a constant learning rate at every iteration (no forced 1e-5), both steps",
            lambda c: c.replace(step1=_constant_lr(c.step1), step2=_constant_lr(c.step2)), EFF),
    "CTLref": ("the predecessor's CTL recipe (carry-misses), reference",
               lambda c: c, "carry"),
    "L64H2": ("H2 with an enlarged step-1 PET (projection 64, 4 transformer layers, 4 heads)",
              lambda c: _model({"projection_dim": 64, "num_transformer": 4, "num_heads": 4})(
                  c.replace(feature_arm="reco_summaries_pdg_onehot")), EFF),
    "L128H2": ("H2 with an enlarged step-1 PET (projection 128, 4 transformer layers, 8 heads)",
               lambda c: _model({"projection_dim": 128, "num_transformer": 4, "num_heads": 8})(
                   c.replace(feature_arm="reco_summaries_pdg_onehot")), EFF),
    "L64S1": ("H2S1 with an enlarged step-1 PET (projection 64, 4 transformer layers, 4 heads)",
              lambda c: _model({"projection_dim": 64, "num_transformer": 4, "num_heads": 4})(
                  CANDIDATES["H2S1"][1](c)), EFF),
    "L128S1": ("H2S1 with an enlarged step-1 PET (projection 128, 4 transformer layers, 8 heads)",
               lambda c: _model({"projection_dim": 128, "num_transformer": 4, "num_heads": 8})(
                   CANDIDATES["H2S1"][1](c)), EFF),
    "H2S1E16": ("H2S1 with 16 epochs per fit at both steps (optimization-effort arm)",
                lambda c: _epochs2(16)(_epochs1(16)(CANDIDATES["H2S1"][1](c))), EFF),
    "L128H2E16": ("L128H2 with 16 step-1 epochs per fit (learning-curve arm)",
                  lambda c: _epochs1(16)(_model({"projection_dim": 128, "num_transformer": 4,
                                                 "num_heads": 8})(
                      c.replace(feature_arm="reco_summaries_pdg_onehot"))), EFF),
}


def base_config() -> RunConfig:
    _, path, sha = BASE
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != sha:
        raise SystemExit(f"[dev] base config {path} sha256 {got} != {sha}")
    return RunConfig.from_json(path.read_text())


def build(stage: str, candidates: list[str], selections: list[tuple[str, int, str]],
          iterations: int, out_dir: Path, manifest: Path) -> list[str]:
    base = base_config()
    cfg_dir = out_dir / stage
    cfg_dir.mkdir(parents=True, exist_ok=True)
    rows = ["# name\tconfig\tconfig_hash\tselection\tdistortion\treference_run\textra_driver_args"]
    for pool, r, dist in selections:
        if r not in DRAWN.get(pool, ()):
            raise SystemExit(f"[dev] {pool}:{r} was not drawn by the predecessor; refused "
                             "(could touch the final or reserve bank)")
        seed = freeze_runs.seed_for(pool, r)
        tag = "" if dist == "dev" else f"-{dist.replace('+', '_')}"
        for cand in candidates:
            desc, transform, miss = CANDIDATES[cand]
            cfg = transform(base).replace(iterations=int(iterations))
            name = f"{stage}-{cand}-{pool}{r}{tag}"
            note = (f"{stage}: {cand} = {desc}; base C {BASE[2][:12]}; pool {pool} replicate {r} "
                    f"(predecessor-drawn), seed {seed}; generated by final_design/dev/make_dev_configs.py")
            cfg = freeze_runs.reseed(cfg, seed, name, note)
            (cfg_dir / f"{name}.json").write_text(cfg.to_json(indent=1) + "\n")
            rel = f"../../../final_design/configs/{stage}/{name}.json"  # relative to confirm/configs/
            rows.append("\t".join([name, rel, cfg.content_hash(), f"{pool}:{r}", dist, "-",
                                   f"--step2-miss-mode {miss}"]))
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(rows) + "\n")
    return rows[1:]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--candidates", nargs="+", required=True, choices=sorted(CANDIDATES))
    ap.add_argument("--selections", nargs="+", required=True,
                    help="POOL:REP:DISTORTION, e.g. F:0:dev T:1:D4c_p_up")
    ap.add_argument("--iterations", type=int, default=6)
    ap.add_argument("--out-dir", type=Path, default=STUDY / "configs")
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args(argv)
    sels = []
    for s in a.selections:
        pool, r, dist = s.split(":", 2)
        sels.append((pool, int(r), dist))
    rows = build(a.stage, a.candidates, sels, a.iterations, a.out_dir, a.manifest)
    print(f"{len(rows)} runs -> {a.manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
