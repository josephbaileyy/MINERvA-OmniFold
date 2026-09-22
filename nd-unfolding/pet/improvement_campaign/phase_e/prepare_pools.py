"""Cache the per-event inputs of pools T (STRESS) and S (SCALE) for the Phase-E scalar work.

Reads ONLY signal-MC members of the closure inventory (`ALLOWED`); the real-data and background
members are never opened. Pool membership comes from `pools.npz`, checked against the committed
`pools/POOL_MANIFEST.json` (sha256 and every per-pool count); the identity sidecar and the
inventory are checked against the sha256s the manifest records.

Pool T cache (per event, pool order = ascending inventory row): identity, pass_reco, both weight
legs, the four truth and four reco scalars, the <= 12 stored reco-cluster energies (GeV, the
loader's MeV->GeV and non-finite->0), the D4 species counts among the <= 12 stored truth hadrons
(and how many slots are filled), the historical truth / reco (p_T, p_par) cell and the historical
region of the truth cell. Pool S cache: the same without tokens and species counts.

Also measured here, before anything is scored (all on pool T unless stated):
* the D3 standardization -- quartiles of true E_avail / true q3 over pool T (unweighted, as the
  historical tilt standardizes) -- written as `d3_standardization.json` for the registry;
* the D1 check -- pool-T quartiles of true E_avail beside the frozen development constants;
* the D5 check -- the committed generator tables rebuilt from the canonical ROOT files;
* the RecoQ3 inversion census (rows with no non-negative root) and E_avail vs stored-token sums;
* the part_gen truncation census and the fraction of pool T inside the 3D phase space.
"""
from __future__ import annotations

import argparse
import json
import time
import zipfile
from pathlib import Path
from typing import Any, Callable

import numpy as np

import common as cm
import distortions as dist
import replicates as rp

scm = cm.scm
ALLOWED = frozenset(scm.ALLOWED_NPZ_MEMBERS | {"part_gen"})
SCALAR_MEMBERS = ("truth_scalars", "reco_scalars", "pass_reco", "pass_truth", "w_truth", "w_reco")


def _refuse(name: str) -> None:
    if name not in ALLOWED:
        raise SystemExit(f"[prepare] refusing to open non-signal-MC member {name!r}")


def load_member_rows(npz: Path, name: str, rows: np.ndarray) -> np.ndarray:
    _refuse(name)
    with np.load(npz, allow_pickle=False) as handle:
        return np.asarray(handle[name][rows])


def stream_member(npz: Path, name: str, rows: np.ndarray,
                  reducer: Callable[[np.ndarray], Any], chunk_rows: int = 1_000_000) -> list:
    """Decompress one (large) member chunk by chunk and apply ``reducer`` to the requested rows
    (sorted, unique) of each chunk; never holds the member in memory."""
    _refuse(name)
    out = []
    with zipfile.ZipFile(npz) as z, z.open(f"{name}.npy") as f:
        version = np.lib.format.read_magic(f)
        reader = (np.lib.format.read_array_header_1_0 if version == (1, 0)
                  else np.lib.format.read_array_header_2_0)
        shape, fortran, dtype = reader(f)
        if fortran:
            raise SystemExit(f"[prepare] {name}: Fortran order not supported")
        row_bytes = int(np.prod(shape[1:])) * dtype.itemsize
        for start in range(0, shape[0], chunk_rows):
            n = min(chunk_rows, shape[0] - start)
            buf = bytearray()
            while len(buf) < n * row_bytes:
                piece = f.read(n * row_bytes - len(buf))
                if not piece:
                    raise SystemExit(f"[prepare] {name}: truncated member")
                buf.extend(piece)
            arr = np.frombuffer(bytes(buf), dtype=dtype).reshape((n,) + tuple(shape[1:]))
            lo, hi = np.searchsorted(rows, [start, start + n])
            if hi > lo:
                out.append(reducer(arr[rows[lo:hi] - start]))
    return out


def token_energy(arr: np.ndarray) -> np.ndarray:
    """part_reco[..., 0] MeV -> GeV, non-finite -> 0 (`fullevent_fps_dataloader._scale_clean`)."""
    return np.nan_to_num(arr[:, :, 0].astype(np.float32) / np.float32(1000.0),
                         nan=0.0, posinf=0.0, neginf=0.0)


def gen_counts(arr: np.ndarray) -> np.ndarray:
    counts = dist.count_species(arr[:, :, 4])
    filled = (np.nan_to_num(arr[:, :, 0]) > 0).sum(axis=1)
    return np.stack([counts["pipm"], counts["pi0"], counts["p"], counts["n"], filled],
                    axis=1).astype(np.int16)


def quartiles(x: np.ndarray) -> dict[str, float]:
    p25, p50, p75 = (float(v) for v in np.percentile(x, [25, 50, 75]))
    return {"p25": p25, "p50": p50, "p75": p75, "iqr": max(p75 - p25, 1e-12), "n": int(x.size)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--closure-npz", type=Path, required=True)
    ap.add_argument("--identity-sidecar", type=Path, required=True)
    ap.add_argument("--pools-npz", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--b1-populations", type=Path, required=True,
                    help="phase-B1 populations.npz (historical acceptance map and edges)")
    ap.add_argument("--d5-directory", type=Path, default=Path(dist.D5_DIR_DEFAULT))
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--skip-inventory-sha", action="store_true",
                    help="testing only: do not hash the (large) inventory")
    args = ap.parse_args()
    t0 = time.perf_counter()
    out = scm.refuse_historical_output(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    sources = cm.historical()
    cr = sources["cr"]
    manifest = json.loads(args.manifest.read_text())

    # ---- inputs, checked ------------------------------------------------------------------
    codes, pool_record = rp.load_pool_codes(args.pools_npz, args.manifest)
    sidecar_sha = scm.sha256_file(args.identity_sidecar)
    if sidecar_sha != manifest["inputs"]["identity_npz"]["sha256"]:
        raise SystemExit("[prepare] identity sidecar sha256 differs from the pool manifest")
    inv_sha = None if args.skip_inventory_sha else scm.sha256_file(args.closure_npz)
    if inv_sha is not None and inv_sha != manifest["inputs"]["truth_npz"]["sha256"]:
        raise SystemExit("[prepare] inventory sha256 differs from the pool manifest")
    b1_sha = scm.sha256_file(args.b1_populations)
    if b1_sha != cm.B1_POPULATIONS_SHA256:
        raise SystemExit("[prepare] B1 populations.npz sha256 differs from the committed one")
    with np.load(args.b1_populations, allow_pickle=False) as b1:
        acceptance = np.asarray(b1["map_acceptance"], float)
        edges_pt = np.asarray(b1["edges_pt"], float)
        edges_pz = np.asarray(b1["edges_pz"], float)
    with np.load(args.identity_sidecar, mmap_mode="r") as blob:
        identity_all = np.asarray(blob["sig_event_id"]).astype(np.int64)
    if identity_all.shape[0] != codes.size:
        raise SystemExit("[prepare] identity sidecar and pool codes disagree in length")

    rows = {p: rp.pool_rows(codes, p) for p in ("T", "S")}
    union = np.union1d(rows["T"], rows["S"])
    census: dict[str, Any] = {}

    # ---- scalar members for T and S --------------------------------------------------------
    scal = {name: load_member_rows(args.closure_npz, name, union) for name in SCALAR_MEMBERS}
    # ---- token energies and species counts for T (streamed) --------------------------------
    t_tok = time.perf_counter()
    tok = np.concatenate(stream_member(args.closure_npz, "part_reco", rows["T"], token_energy))
    gen = np.concatenate(stream_member(args.closure_npz, "part_gen", rows["T"], gen_counts))
    census["stream_seconds"] = time.perf_counter() - t_tok

    caches: dict[str, dict[str, np.ndarray]] = {}
    for pool in ("T", "S"):
        r = rows[pool]
        pos = np.searchsorted(union, r)
        pass_truth = scal["pass_truth"][pos].astype(bool)
        if not pass_truth.all():
            raise SystemExit(f"[prepare] pool {pool} holds rows without pass_truth")
        truth = scal["truth_scalars"][pos].astype(np.float64)
        reco = scal["reco_scalars"][pos].astype(np.float64)
        pr = scal["pass_reco"][pos].astype(bool)
        labels, tcell = cr.region_labels_for_events(truth[:, 0], truth[:, 1], edges_pt, edges_pz,
                                                    acceptance)
        rcell = cr.cell_index_of_events(reco[:, 0], reco[:, 1], edges_pt, edges_pz)
        c = {"rows": r, "identity": identity_all[r], "pass_reco": pr,
             "w_truth": scal["w_truth"][pos].astype(np.float64),
             "w_reco": scal["w_reco"][pos].astype(np.float64),
             "truth": truth, "reco": reco,
             "truth_cell": tcell.astype(np.int32), "reco_cell": rcell.astype(np.int32),
             "region": np.array([cm.REGION_CODES[x] for x in labels], dtype=np.int8)}
        if pool == "T":
            c["tok_E"] = tok
            for i, k in enumerate(("n_pipm", "n_pi0", "n_p", "n_n", "n_gen_filled")):
                c[k] = gen[:, i]
        caches[pool] = c
        census[pool] = {
            "rows": int(r.size), "pass_reco": int(pr.sum()),
            "sum_w_truth": float(c["w_truth"].sum()),
            "accepted_fraction": float(c["w_reco"][pr].sum() / c["w_truth"].sum()),
            "truth_q3_nonfinite": int((~np.isfinite(truth[:, 3])).sum()),
            "reco_nonfinite_on_pass_reco": int((~np.isfinite(reco[pr])).any(axis=1).sum()),
            "reco_sentinel_on_pass_reco": int((reco[pr] == -9999.0).any(axis=1).sum()),
            "truth_off_grid": int((tcell < 0).sum()),
            "reco_off_grid_on_pass_reco": int((rcell[pr] < 0).sum()),
            "region_counts": {k: int((c["region"] == v).sum()) for k, v in cm.REGION_CODES.items()},
        }
    del scal

    # ---- measurements on pool T ----------------------------------------------------------------
    T = caches["T"]
    pr = T["pass_reco"]
    e_true, q3_true = T["truth"][:, 2], T["truth"][:, 3]
    ratio = dist.eavail_over_q3(e_true, q3_true)
    finite = np.isfinite(ratio)
    d3 = {"schema": "phase-e-d3-standardization/1", "pool": "T",
          "definition": "quartiles of true E_avail / true q3 over pool T rows (unweighted, as "
                        "closure_powered_truth_reweight.clipped_exponential_tilt standardizes); "
                        "rows with q3 <= 0 or non-finite are excluded here and get weight 1",
          **quartiles(ratio[finite]), "excluded_rows": int((~finite).sum()),
          "pool_rows_sha256": rp.rows_digest(rows["T"]),
          "pools_npz_sha256": pool_record["pools_npz_sha256"],
          "inventory_sha256": inv_sha}
    d3["sha256"] = cm.canonical_sha({k: v for k, v in d3.items() if k != "sha256"})
    census["d1_check"] = {"frozen_p50": dist.D1_P50_GEV, "frozen_iqr": dist.D1_IQR_GEV,
                          "pool_T_true_eavail": quartiles(e_true[np.isfinite(e_true)])}
    q0, bad = dist.recoil_q0(T["reco"][pr, 0], T["reco"][pr, 1], T["reco"][pr, 3])
    toksum = T["tok_E"][pr].astype(np.float64).sum(axis=1)
    e_reco = T["reco"][pr, 2]
    has = toksum > 0
    census["reco_q3_inversion"] = {
        "pass_reco_rows": int(pr.sum()), "no_nonnegative_root": int(bad.sum()),
        "roundtrip_max_abs_dev_gev": float(np.abs(dist.reco_q3(T["reco"][pr, 0], T["reco"][pr, 1],
                                                               q0) - T["reco"][pr, 3])[~bad].max()),
        "q0_quantiles_gev": quartiles(q0),
        "q0_below_eavail_over_1p17": int((q0 < e_reco / 1.17 - 1e-6).sum())}
    census["eavail_vs_stored_tokens"] = {
        "rows_with_stored_energy": int(has.sum()), "rows_without": int((~has).sum()),
        "reco_eavail_over_token_sum_quantiles": quartiles(e_reco[has] / toksum[has]),
        "rows_with_12_tokens_stored": int(((T["tok_E"][pr] != 0).sum(axis=1) == 12).sum())}
    census["part_gen"] = {
        "rows_with_12_slots_filled": int((T["n_gen_filled"] == 12).sum()),
        "mean_counts": {k: float(T[k].mean()) for k in ("n_pipm", "n_pi0", "n_p", "n_n")},
        "count_histograms": {k: np.bincount(T[k].astype(np.int64), minlength=13).tolist()
                             for k in ("n_pipm", "n_pi0", "n_p", "n_n")}}
    table0 = json.loads(dist.D5_CALIBRATION.read_text())["tables"]["nuwro"]
    _w, inside = dist.generator_weight(T["truth"][:, 0], T["truth"][:, 1], e_true, table0)
    census["d5_3d_phase_space"] = {"inside": int(inside.sum()), "outside": int((~inside).sum()),
                                   "w_truth_fraction_inside":
                                       float(T["w_truth"][inside].sum() / T["w_truth"].sum())}

    # ---- D5 tables rebuilt from the canonical files ------------------------------------------
    import build_d5_calibration as b5
    rebuilt = b5.digests(b5.build(args.d5_directory))
    committed = b5.digests(json.loads(dist.D5_CALIBRATION.read_text()))
    census["d5_rebuild_check"] = {"directory": str(args.d5_directory), "rebuilt": rebuilt,
                                  "agrees": rebuilt == committed}
    if rebuilt != committed:
        raise SystemExit("[prepare] D5 tables rebuilt from the canonical files differ from the "
                         "committed calibration")

    # ---- write -------------------------------------------------------------------------------
    files = {}
    for pool, c in caches.items():
        path = out / f"pool{pool}.npz"
        np.savez(path, **c)
        files[pool] = {"path": str(path), "sha256": scm.sha256_file(path)}
    cm.write_json(out / "d3_standardization.json", d3, compact=False)
    record = {"schema": "phase-e-prepare/1", "commit": scm.repo_commit(),
              "historical_sources": historical_record(),
              "inputs": {"closure_npz": str(args.closure_npz), "closure_npz_sha256": inv_sha,
                         "identity_sidecar": str(args.identity_sidecar),
                         "identity_sidecar_sha256": sidecar_sha,
                         "b1_populations": str(args.b1_populations), "b1_populations_sha256": b1_sha,
                         "members_read": sorted(SCALAR_MEMBERS + ("part_reco", "part_gen"))},
              "pools": pool_record, "caches": files, "census": census, "d3_standardization": d3,
              "environment": cm.environment(), "seconds": time.perf_counter() - t0,
              "scope": "simulation-only Phase-E input cache; PET is diagnostic method development"}
    cm.write_json(out / "prepare.json", record, compact=False)
    print(f"[prepare] pools T={rows['T'].size} S={rows['S'].size}; D3 p50={d3['p50']:.5f} "
          f"iqr={d3['iqr']:.5f}; wrote {out} in {time.perf_counter() - t0:.0f}s")


def historical_record() -> Any:
    return getattr(cm.historical, "_verified", None)


if __name__ == "__main__":
    main()
