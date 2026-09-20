"""Gather his tokens for the two closure legs ONCE, not once per task.

MEASURED, job 58599158: his arm spent 15.5 minutes between process start and
its first training step, while ours -- which builds the same loaders from the
same dump -- took 75 seconds to the same point and 144 seconds in total. The
difference is the gather.

It repeats identically in every task. The subsample seed, the subsample size,
the split seed and the half size are all frozen, so `imc`, half A and half B
are the SAME rows in all 32 runs; only the estimator seed varies. Paying the
gather 32 times buys nothing, and at full scale each payment reads most of the
65 GB of built inputs, so the campaign would do roughly two terabytes of reads
to produce one answer.

This writes the two legs once. The driver memory-maps the result and checks the
key, so a cache built for a different split cannot be silently consumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import frozen_design as fd


def cache_key(*, inputs_npz: Path, subsample_seed: int, max_events: int,
              split_seed: int, half_size: int) -> str:
    """Everything the gathered rows depend on. Not the estimator seed, which
    is the only thing that varies across the campaign."""
    payload = json.dumps({
        "inputs": Path(inputs_npz).name,
        "subsample_seed": int(subsample_seed),
        "max_events": int(max_events),
        "split_seed": int(split_seed),
        "half_size": int(half_size),
        "token_cap": int(fd.THEIRS_COMPLETE["token_cap"]),
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def build(*, inputs_npz: Path, theirs_index: Path, out: Path,
          subsample_seed: int, max_events: int, split_seed: int,
          half_size: int) -> dict[str, Any]:
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    import closure_powered_truth_reweight as cp
    import fullevent_fps_dataloader as ffd
    import materialize_theirs as mtz

    _data, mc, imc, _cr, _cg, _meta = ffd.build_fullevent_loaders(
        str(inputs_npz), max_events=max_events, seed=subsample_seed,
        bkg_mode="mc-only")
    if _data is not None:
        raise SystemExit("[prematerialize] mc-only returned a measured loader")
    imc = np.asarray(imc)
    pr = np.asarray(mc.pass_reco).astype(bool)
    pg = np.asarray(mc.pass_gen).astype(bool)

    ia, ib = cp.deterministic_halves(np.asarray(mc.reco).shape[0],
                                     half=half_size, seed=split_seed)
    s1_a = pr[ia] & pg[ia]

    with np.load(inputs_npz, mmap_mode="r") as target:
        sig_pass_reco = np.asarray(target["pass_reco"]).astype(bool)

    index = np.load(Path(theirs_index) / "join_sig.npz")
    report = json.loads((Path(theirs_index) / "join_sig.json").read_text())

    def gather(rows):
        return mtz.materialize(report["files"], index["row_index"],
                               index["origin"], np.asarray(rows), sig_pass_reco)

    pdata = gather(imc[ia][s1_a])
    prior = gather(imc[ib])

    key = cache_key(inputs_npz=inputs_npz, subsample_seed=subsample_seed,
                    max_events=max_events, split_seed=split_seed,
                    half_size=half_size)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out,
             pdata_packed=pdata["packed"], pdata_globals=pdata["globals"],
             prior_packed=prior["packed"], prior_globals=prior["globals"],
             rows_a=imc[ia].astype(np.int64), rows_b=imc[ib].astype(np.int64),
             s1_a=s1_a, key=np.array(key))
    return {
        "key": key, "path": str(out),
        "pdata_rows": int(pdata["packed"].shape[0]),
        "prior_rows": int(prior["packed"].shape[0]),
        "shards_opened": int(pdata["shards_opened"] + prior["shards_opened"]),
        "reading": ("gathered once; every campaign task uses these same rows "
                    "because only the estimator seed varies across the campaign"),
    }


def load(path: Path, *, expected_key: str) -> dict[str, Any]:
    """Memory-map the cache, refusing one built for a different split."""
    blob = np.load(path, mmap_mode="r")
    got = str(np.asarray(blob["key"]))
    if got != expected_key:
        raise SystemExit(
            f"[prematerialize] cache key {got[:12]} != expected "
            f"{expected_key[:12]}. This cache was built for a different "
            "subsample, split or token cap; consuming it would gather one "
            "run's rows into another run's legs")
    return blob


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs-npz", type=Path, required=True)
    parser.add_argument("--theirs-index", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--subsample-seed", type=int, required=True)
    parser.add_argument("--max-events", type=int, required=True)
    parser.add_argument("--split-seed", type=int,
                        default=int(fd.SPLITS["split_seed"]))
    parser.add_argument("--half-size", type=int, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    info = build(inputs_npz=args.inputs_npz, theirs_index=args.theirs_index,
                 out=args.out, subsample_seed=args.subsample_seed,
                 max_events=args.max_events, split_seed=args.split_seed,
                 half_size=args.half_size)
    print(json.dumps(info, indent=2))
    if args.report:
        args.report.write_text(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
