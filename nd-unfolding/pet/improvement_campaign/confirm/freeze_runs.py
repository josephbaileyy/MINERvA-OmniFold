"""Per-replicate RunConfigs and run manifests from the configurations frozen by PROTOCOL
amendment 2, generated mechanically.

Amendment 2: "each replicate replaces only the estimator seed (derived from the replicate id) and
the event rows". The frozen files are never edited. For (candidate, pool, replicate) this writes
the frozen config with exactly three things replaced -- `name`, `note`, and the seeds (each step's
`seed` and its validation-split `seed`), all set to `seed_for(pool, replicate)` -- and
`verify_generated` (called by `run_replicate.py --frozen-config`) re-derives that and refuses any
other difference. The seed is shared by CTL/A, B and C on one replicate (paired), and differs
between replicates and pools.

    freeze_runs.py --stage pilot --pool P --replicates 0 1 2
    freeze_runs.py --stage stress --pool T --replicates 0 1 --distortions D1_m0.350 ...
    freeze_runs.py --stage final --pool F --replicates 0 ... 11

CTL and A are ONE run (CTL scored at k = 3, A at k = 10).
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
if str(CAMPAIGN) not in sys.path:
    sys.path.insert(0, str(CAMPAIGN))
from recipe import RunConfig  # noqa: E402

FROZEN_DIR = "phase_b/pet/configs"      # relative to the campaign directory
CANDIDATES = {   # id -> (frozen file, sha256 recorded in amendment 2, step-2 miss rule)
    "CTL": ("b2e3-H-K10-s1.json",
            "bff1a6722a3099358b2eb23af76d743ffdbda2442b228ed657546809b5f38fe8", "carry"),
    "B": ("b2e5-C2-H-s1.json",
          "13dd2fbfd1f7d7d5c38c059b4d5a81cd01a4c3ddd504667d99dba6e07c3b524f", "carry"),
    "C": ("b2e4-M-K10-s1.json",
          "0afffb7d4402a1dbb32f28397b53bd05c9378c21c907624fc75450dfaa35a9f2",
          "efficiency_corrected"),
}
SEED_SALT = "pet-improvement-20260922-confirm-seed"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seed_for(pool: str, replicate: int) -> int:
    """The estimator seed of a replicate: sha256(salt/pool/replicate) -> [1, 2^31 - 1]."""
    h = hashlib.sha256(f"{SEED_SALT}/{pool}/{int(replicate)}".encode()).digest()
    return int.from_bytes(h[:4], "big") % (2 ** 31 - 1) + 1


def reseed(config: RunConfig, seed: int, name: str, note: str) -> RunConfig:
    def step(s: Any) -> Any:
        return dataclasses.replace(s, seed=int(seed),
                                   validation=dataclasses.replace(s.validation, seed=int(seed)))
    return config.replace(name=name, note=note, step1=step(config.step1),
                          step2=step(config.step2))


def load_frozen(candidate: str) -> tuple[RunConfig, Path, str]:
    fname, sha, _mode = CANDIDATES[candidate]
    path = CAMPAIGN / FROZEN_DIR / fname
    got = sha256_file(path)
    if got != sha:
        raise SystemExit(f"[freeze] {path} sha256 {got} != amendment 2's {sha}")
    return RunConfig.from_json(path.read_text()), path, sha


def verify_generated(config: RunConfig, frozen_path: Path, frozen_sha256: str | None
                     ) -> dict[str, Any]:
    """Refuse unless `config` == the frozen file with only name, note and seeds replaced."""
    got = sha256_file(frozen_path)
    if frozen_sha256 is not None and got != frozen_sha256:
        raise SystemExit(f"[freeze] frozen config {frozen_path} sha256 {got} != {frozen_sha256}")
    frozen = RunConfig.from_json(Path(frozen_path).read_text())
    seed = config.step1.seed
    seeds = {config.step1.seed, config.step1.validation.seed, config.step2.seed,
             config.step2.validation.seed}
    if len(seeds) != 1:
        raise SystemExit(f"[freeze] generated config carries several seeds {seeds}")
    expect = reseed(frozen, seed, config.name, config.note)
    if expect.content_hash() != config.content_hash():
        raise SystemExit("[freeze] the run config differs from the frozen config in more than "
                         "name, note and seed")
    return {"frozen_path": str(frozen_path), "frozen_sha256": got,
            "frozen_content_hash": frozen.content_hash(), "generated_content_hash":
            config.content_hash(), "seed": int(seed), "replaced": ["name", "note", "seeds"]}


def generate(stage: str, pool: str, replicates: list[int], distortions: list[str],
             candidates: list[str]) -> list[str]:
    out_dir = HERE / "configs" / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = ["# name\tconfig\tconfig_hash\tselection\tdistortion\treference_run\textra_driver_args"]
    for dist in distortions:
        tag = "" if dist == "dev" else f"-{dist.replace('+', '_')}"
        for r in replicates:
            seed = seed_for(pool, r)
            for cand in candidates:
                frozen, path, sha = load_frozen(cand)
                name = f"{stage}-{cand}-{pool}{r}{tag}"
                note = (f"{stage}: {cand} ({path.name}, sha256 {sha[:12]}) on pool {pool} "
                        f"replicate {r}, seed {seed}; generated by freeze_runs.py")
                config = reseed(frozen, seed, name, note)
                verify_generated(config, path, sha)
                (out_dir / f"{name}.json").write_text(config.to_json(indent=1) + "\n")
                extra = (f"--frozen-config {{C}}/{FROZEN_DIR}/{path.name} --frozen-sha256 {sha}"
                         f" --step2-miss-mode {CANDIDATES[cand][2]}")
                rows.append("\t".join([name, f"{stage}/{name}.json", config.content_hash(),
                                       f"{pool}:{r}", dist, "-", extra]))
    manifest = HERE / "runs" / f"{stage}.tsv"
    manifest.write_text("\n".join(rows) + "\n")
    return rows[1:]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--replicates", type=int, nargs="+", required=True)
    ap.add_argument("--distortions", nargs="+", default=["dev"])
    ap.add_argument("--candidates", nargs="+", default=list(CANDIDATES))
    args = ap.parse_args()
    for row in generate(args.stage, args.pool, args.replicates, args.distortions,
                        args.candidates):
        print(row.split("\t")[0])


if __name__ == "__main__":
    main()
