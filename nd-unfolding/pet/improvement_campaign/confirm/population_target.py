"""The population-level target of a (pool, distortion): the distorted seven-bin truth E_avail
spectrum over EVERY event of the pool, aggregate and per historical region.

A replicate's like-for-like score uses its own pseudodata truth as the target (the historical
design). This file supplies the second target the confirmatory stage reports beside it -- what
the estimator is ultimately supposed to recover -- so the finite-sample distance between a
replicate's pseudodata and its population is visible. The spectra are `score_campaign._histogram`
of true E_avail, weighted `w_truth x d` with `d` the distortion's raw weight (its normalization
cancels in the normalized spectra); regions are the historical (pT, p||)-cell regions under the
historical acceptance map. Rows: the pool's rows (all truth-passing by construction), with finite
true E_avail.

Reads only signal-MC members (`truth_scalars`, `w_truth`, `pass_truth`; `part_gen` streamed for
the multiplicity distortions). Pools P and F are refused until the protocol's Amendment 2.

    population_target.py --pool S --distortion dev --inputs-npz ... --pools-npz ... --manifest ...
        --populations <B1 populations.npz> --output <json>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import replicate_inputs as ri  # noqa: E402
import authorization_scope as scope  # noqa: E402

SCHEMA = "pet-improvement-confirm-population-target/1"
MEMBERS = ("truth_scalars", "w_truth", "pass_truth")


def read_member_rows(npz: Path, name: str, rows: np.ndarray) -> np.ndarray:
    import numpy.lib.format as npf
    scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                  npz_keys_read=[name])
    with zipfile.ZipFile(str(npz)) as archive, archive.open(f"{name}.npy") as handle:
        return np.asarray(npf.read_array(handle, allow_pickle=False)[rows])


def species_counts(npz: Path, rows: np.ndarray) -> dict[str, np.ndarray]:
    """D4 species counts among the stored truth hadrons, streamed (part_gen is ~12 GB)."""
    import common as cm  # noqa: F401  (puts phase_b/scalar on the path)
    import prepare_pools as pp
    got = np.concatenate(pp.stream_member(npz, "part_gen", rows, pp.gen_counts))
    return {f"n_{k}": got[:, i] for i, k in enumerate(("pipm", "pi0", "p", "n"))}


def build(pool: str, distortion_name: str, *, inputs_npz: Path, pools_npz: Path,
          manifest: Path, populations: Path) -> dict:
    guard = ri.refuse_sealed_pool(pool)
    distortion = ri.get_distortion(distortion_name)
    codes, pool_record = ri.rp.load_pool_codes(pools_npz, manifest)
    rows = ri.rp.pool_rows(codes, pool)
    import common as cm
    sc = cm.historical()["sc"]
    truth = read_member_rows(inputs_npz, "truth_scalars", rows).astype(np.float64)
    w_truth = read_member_rows(inputs_npz, "w_truth", rows).astype(np.float64)
    pass_truth = read_member_rows(inputs_npz, "pass_truth", rows).astype(bool)
    if not pass_truth.all():
        raise SystemExit(f"[target] pool {pool} holds rows without pass_truth")
    keep = np.isfinite(truth[:, 2])
    mapping = {"pt": truth[:, 0], "ppar": truth[:, 1], "eavail": truth[:, 2], "q3": truth[:, 3]}
    if distortion.needs_species:
        mapping.update(species_counts(inputs_npz, rows))
    m = {k: v[keep] for k, v in mapping.items()}
    raw = np.asarray(distortion.raw(m), np.float64)
    region = ri.region_codes(ri.historical_cr(), m["pt"], m["ppar"], populations)
    w = w_truth[keep] * raw
    out = {"aggregate": sc._histogram(m["eavail"], w, cm.ENDPOINT_EDGES).tolist(),
           "undistorted_aggregate": sc._histogram(m["eavail"], w_truth[keep],
                                                  cm.ENDPOINT_EDGES).tolist(), "regions": {}}
    for name, code in cm.REGION_CODES.items():
        if code >= 0:
            sel = region == code
            out["regions"][name] = sc._histogram(m["eavail"][sel], w[sel],
                                                 cm.ENDPOINT_EDGES).tolist()
    return {"schema": SCHEMA, "pool": pool, "pool_guard": guard, "pools": pool_record,
            "pool_rows_sha256": ri.rp.rows_digest(rows), "n_rows": int(rows.size),
            "n_rows_nonfinite_eavail_dropped": int((~keep).sum()),
            "distortion": distortion.name, "distortion_record": distortion.record,
            "distortion_hash": distortion.content_hash(),
            "raw_weight_mean": float(raw.mean()), "edges": cm.ENDPOINT_EDGES.tolist(),
            "targets": out, "members_read": list(MEMBERS) + (["part_gen"] if
                                                             distortion.needs_species else []),
            "populations_sha256": ri.sha256_file(populations),
            "region_counts": {k: int((region == c).sum()) for k, c in cm.REGION_CODES.items()},
            "scope": "simulation only; PET is diagnostic method development"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--distortion", default=ri.DEV)
    ap.add_argument("--inputs-npz", type=Path, required=True)
    ap.add_argument("--pools-npz", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--populations", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = scope.refuse_historical_output(args.output)
    scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                  input_paths=[args.inputs_npz, args.pools_npz, args.manifest,
                                               args.populations])
    t0 = time.perf_counter()
    record = build(args.pool, args.distortion, inputs_npz=args.inputs_npz,
                   pools_npz=args.pools_npz, manifest=args.manifest,
                   populations=args.populations)
    record["seconds"] = time.perf_counter() - t0
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=1, allow_nan=False) + "\n")
    tmp.replace(out)
    print(f"[target] {args.pool}/{args.distortion}: {record['n_rows']} rows in "
          f"{record['seconds']:.0f}s -> {out}")


if __name__ == "__main__":
    main()
