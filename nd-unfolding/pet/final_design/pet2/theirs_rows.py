"""PET2-small step-1 inputs for an arbitrary sorted set of inventory rows (signal MC only).

The historical comparison gathered PET2's step-1 inputs (33 tokens `[d_eta, d_phi, log pT, log E]` +
PID + 5 `add_info` columns, packed 10 wide, and 16 event globals) for its two fixed closure halves,
with `configuration_comparison/materialize_theirs.materialize` over the identity join
`join_sig.npz` (inventory row -> built row -> (shard, row in shard)), once, into a cache
(`prematerialize_theirs.py`). A replicate run needs the same inputs for OTHER rows: the replicate's
prior rows (every row, reco-passing or not) and its pseudodata reco-passing rows. This module gathers
them by calling the historical `materialize` itself -- the token conversion
(`theirs_token_schema.convert_packed`) and the `!pass_reco` zeroing
(`theirs_loader_substitution.zero_non_reco`) are its own, not retyped -- with two changes of
logistics only:

* **one pass over the shards for all legs**: the rows of every leg are grouped by the shard that
  owns them and `materialize` is called on consecutive shard groups, so each shard is opened once in
  total (the historical cache opened every shard once per leg) and memory stays bounded by the group
  size, not by the leg size. Every per-row operation in `materialize` is element-wise, so the
  grouping cannot change a byte; `crosscheck` measures that against the historical caches;
* **fail-closed checks** before any shard is read: the rows must be sorted, unique and inside the
  inventory; the join must be the signal join of THIS inventory (row count, identity fields, full
  reco coverage, no positional fallback); every shard the join names must be a signal-MC shard
  (`<playlist>_MC/MasterAnaDev_mc_AnaTuple_*.theirs.npz`), so no data or background file can be
  opened; a requested reco-passing row without a built input is an error (the historical rule,
  raised by `materialize`); a non-finite value in a gathered reco-passing row is an error.

A row that fails reconstruction has no reconstructed object; it comes back all-zero, matched or
not, exactly as in the historical arm (and as the production loader zeroes our reco cloud).

    python theirs_rows.py crosscheck --cache <theirs-final.npz> --inputs-npz <G2 npz> \
        --join-dir <dir with join_sig.npz/json> --out <report.json>

Only signal-MC simulation is read. PET is diagnostic method development.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
PET = HERE.parents[1]
CAMPAIGN = PET / "improvement_campaign"
COMP = PET / "configuration_comparison"
# The campaign's `authorization_scope` must win over configuration_comparison's own module of the
# same name: the campaign directory goes first, the historical one LAST (only for the modules
# `materialize` imports lazily: `theirs_loader_substitution`, `theirs_token_schema`).
if str(CAMPAIGN) not in sys.path:
    sys.path.insert(0, str(CAMPAIGN))
import authorization_scope as scope  # noqa: E402

if str(COMP) not in sys.path:
    sys.path.append(str(COMP))
import materialize_theirs as mtz  # noqa: E402

SCHEMA = "pet-final-design-theirs-rows/1"
JOIN_DIR = Path("/pscratch/sd/j/josephrb/campaign-20260920/join")
INVENTORY_ROWS = 49_152_885
IDENTITY_FIELDS = ["mc_run", "mc_subrun", "mc_nthEvtInFile"]
TOKEN_CAP, PACKED_WIDTH, GLOBAL_WIDTH = 33, 10, 16
SIGNAL_SHARD = re.compile(r"/1[A-Z]_MC/MasterAnaDev_mc_AnaTuple_run\d+_Playlist\.theirs\.npz$")
GROUP_ROWS = 65_536


class JoinError(SystemExit):
    """The join or a requested row cannot supply PET2 inputs; nothing is gathered around it."""


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_array(a: Any) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def rows_digest(rows: np.ndarray) -> str:
    return sha256_array(np.asarray(rows, dtype=np.int64))


# ------------------------------------------------------------------------------------------- #
# The join
# ------------------------------------------------------------------------------------------- #
@dataclass
class TheirsIndex:
    files: list[str]
    row_index: np.ndarray          # (inventory rows,) built row or -1
    origin: np.ndarray             # (built rows, 2) shard, row in shard
    record: dict[str, Any] = field(default_factory=dict)


def check_signal_shards(files: Sequence[str]) -> None:
    """Every shard the join can open must be a signal-MC shard; refuse the whole join otherwise."""
    bad = [f for f in files if not SIGNAL_SHARD.search(str(f))]
    if bad:
        raise scope.ScopeViolation(
            f"{len(bad)} join shards are not signal-MC shards (first: {bad[:3]}); only simulation "
            "may be read")


def validate_report(report: Mapping[str, Any], inventory_rows: int) -> None:
    problems = []
    if report.get("stream") != "sig":
        problems.append(f"stream {report.get('stream')!r} is not 'sig'")
    if list(report.get("identity_fields", [])) != IDENTITY_FIELDS:
        problems.append(f"identity fields {report.get('identity_fields')} != {IDENTITY_FIELDS}")
    if int(report.get("inventory_rows", -1)) != int(inventory_rows):
        problems.append(f"join covers {report.get('inventory_rows')} rows, inventory has "
                        f"{inventory_rows}")
    if report.get("positional_fallback") != "never":
        problems.append("the join allowed a positional fallback")
    cov = report.get("reco_coverage") or {}
    if int(cov.get("pass_reco_unmatched", -1)) != 0:
        problems.append(f"join leaves {cov.get('pass_reco_unmatched')} pass_reco rows unmatched")
    if int(report.get("built_files", -1)) != len(report.get("files", [])):
        problems.append("built_files disagrees with the file list")
    if problems:
        raise JoinError(f"[theirs_rows] the join cannot be used: {problems}")


def load_index(join_dir: Path = JOIN_DIR, *, inventory_rows: int = INVENTORY_ROWS) -> TheirsIndex:
    join_dir = Path(join_dir)
    json_path, npz_path = join_dir / "join_sig.json", join_dir / "join_sig.npz"
    report = json.loads(json_path.read_text())
    validate_report(report, inventory_rows)
    files = [str(f) for f in report["files"]]
    check_signal_shards(files)
    with np.load(npz_path) as blob:
        row_index = np.asarray(blob["row_index"])
        origin = np.asarray(blob["origin"])
    if row_index.shape != (int(inventory_rows),):
        raise JoinError(f"[theirs_rows] row_index shape {row_index.shape} != ({inventory_rows},)")
    if origin.ndim != 2 or origin.shape[1] != 2 or origin.shape[0] != int(report["built_rows"]):
        raise JoinError(f"[theirs_rows] origin shape {origin.shape} disagrees with the report")
    if row_index.max() >= origin.shape[0] or origin[:, 0].max() >= len(files) \
            or origin.min() < 0:
        raise JoinError("[theirs_rows] the join points outside its own built rows or files")
    record = {"join_dir": str(join_dir), "join_sig_json_sha256": sha256_file(json_path),
              "join_sig_npz_sha256": sha256_file(npz_path), "files": len(files),
              "built_rows": int(origin.shape[0]), "inventory_rows": int(inventory_rows),
              "duplicate_built_keys": report.get("duplicate_built_keys"),
              "reco_coverage": report.get("reco_coverage"),
              "all_files_signal_mc": True}
    return TheirsIndex(files, row_index, origin, record)


def read_pass_reco(inputs_npz: Path) -> tuple[np.ndarray, str]:
    """The inventory's `pass_reco` for every row, through the signal-only view."""
    raw = np.load(inputs_npz, allow_pickle=False)
    view = scope.SignalOnlyNpz(raw)
    try:
        pass_reco = np.asarray(view["pass_reco"]).astype(bool)
    finally:
        view.close()
    return pass_reco, sha256_array(pass_reco)


# ------------------------------------------------------------------------------------------- #
# The gather
# ------------------------------------------------------------------------------------------- #
def check_rows(rows: Any, n_inventory: int, label: str) -> np.ndarray:
    rows = np.asarray(rows)
    if rows.ndim != 1 or not np.issubdtype(rows.dtype, np.integer):
        raise JoinError(f"[theirs_rows] {label} rows must be a 1-D integer array")
    rows = rows.astype(np.int64)
    if rows.size == 0:
        raise JoinError(f"[theirs_rows] {label}: no rows requested")
    if np.any(np.diff(rows) <= 0):
        raise JoinError(f"[theirs_rows] {label} rows are not sorted and unique")
    if rows[0] < 0 or rows[-1] >= n_inventory:
        raise JoinError(f"[theirs_rows] {label} rows fall outside the inventory "
                        f"(0..{n_inventory - 1})")
    return rows


def shard_groups(shard_of_row: np.ndarray, group_rows: int) -> list[np.ndarray]:
    """Positions of the requested rows, partitioned into groups of whole shards.

    Rows without a built input (shard -1: they fail reco and come back zero) go with the first
    group. Every shard's rows land in exactly one group, so each shard is opened once."""
    order = np.argsort(shard_of_row, kind="stable")
    shards = shard_of_row[order]
    cuts = np.flatnonzero(np.diff(shards)) + 1
    runs = np.split(order, cuts)
    groups: list[np.ndarray] = []
    current: list[np.ndarray] = []
    size, has_shard = 0, False
    for run in runs:
        if has_shard and size + run.size > group_rows:
            groups.append(np.concatenate(current))
            current, size, has_shard = [], 0, False
        current.append(run)
        size += run.size
        has_shard = has_shard or bool(shard_of_row[run[0]] >= 0)
    if current:
        groups.append(np.concatenate(current))
    return groups


def gather(index: TheirsIndex, rows: np.ndarray, pass_reco: np.ndarray, *,
           group_rows: int = GROUP_ROWS,
           materialize: Callable[..., dict[str, Any]] | None = None) -> dict[str, Any]:
    """Packed tokens `(n, 33, 10)` and globals `(n, 16)` for sorted `rows`, in that order."""
    materialize = mtz.materialize if materialize is None else materialize
    pass_reco = np.asarray(pass_reco, dtype=bool)
    if pass_reco.shape != index.row_index.shape:
        raise JoinError(f"[theirs_rows] pass_reco has {pass_reco.shape[0]} rows, the join "
                        f"{index.row_index.shape[0]}")
    rows = check_rows(rows, index.row_index.shape[0], "requested")
    selected = index.row_index[rows]
    reco_ok = pass_reco[rows]
    missing = int(((selected < 0) & reco_ok).sum())
    if missing:
        raise JoinError(f"[theirs_rows] {missing} of {int(reco_ok.sum())} requested pass_reco rows "
                        "have no built PET2 input; refusing (the join must be resolved first)")
    shard = np.where(selected >= 0, index.origin[np.where(selected >= 0, selected, 0), 0], -1)
    packed = np.zeros((rows.size, TOKEN_CAP, PACKED_WIDTH), dtype=np.float32)
    globals_ = np.zeros((rows.size, GLOBAL_WIDTH), dtype=np.float32)
    opened = 0
    t0 = time.perf_counter()
    for pos in shard_groups(shard, group_rows):
        out = materialize(index.files, index.row_index, index.origin, rows[pos], pass_reco,
                          cap=TOKEN_CAP, packed_width=PACKED_WIDTH, global_width=GLOBAL_WIDTH)
        if out["packed"].shape != (pos.size, TOKEN_CAP, PACKED_WIDTH) or \
                out["globals"].shape != (pos.size, GLOBAL_WIDTH):
            raise JoinError("[theirs_rows] materialize returned an unexpected shape")
        packed[pos] = out["packed"]
        globals_[pos] = out["globals"]
        opened += int(out["shards_opened"])
    needed = int(np.unique(shard[shard >= 0]).size)
    if opened != needed:
        raise JoinError(f"[theirs_rows] opened {opened} shards for {needed} needed")
    bad = int((~np.isfinite(packed[reco_ok])).sum() + (~np.isfinite(globals_[reco_ok])).sum())
    if bad:
        where = nonfinite_locations(index, rows, packed, globals_, selected)
        raise JoinError(f"[theirs_rows] {bad} non-finite values in gathered reco-passing rows: "
                        f"{json.dumps(where[:20])}")
    zero_rows = ~(packed.reshape(rows.size, -1).any(axis=1) | globals_.any(axis=1))
    record = {"rows": int(rows.size), "rows_sha256": rows_digest(rows),
              "pass_reco_rows": int(reco_ok.sum()), "rows_without_reco": int((~reco_ok).sum()),
              "unmatched_without_reco": int(((selected < 0) & ~reco_ok).sum()),
              "all_zero_rows": int(zero_rows.sum()),
              "all_zero_rows_with_reco": int((zero_rows & reco_ok).sum()),
              "nonzero_rows_without_reco": int((~zero_rows & ~reco_ok).sum()),
              "shards_opened": opened, "seconds": time.perf_counter() - t0,
              "packed_sha256": sha256_array(packed), "globals_sha256": sha256_array(globals_)}
    if record["nonzero_rows_without_reco"]:
        raise JoinError("[theirs_rows] a !pass_reco row carries PET2 content")
    return {"packed": packed, "globals": globals_, "record": record}


def nonfinite_locations(index: TheirsIndex, rows: np.ndarray, packed: np.ndarray,
                        globals_: np.ndarray, selected: np.ndarray) -> list[dict[str, Any]]:
    """Where each non-finite gathered value sits, with the value the shard STORES there."""
    out: list[dict[str, Any]] = []
    for block, arr in (("packed", packed), ("globals", globals_)):
        for hit in np.argwhere(~np.isfinite(arr))[:50]:
            i = int(hit[0])
            shard, local = (int(x) for x in index.origin[selected[i]])
            entry = {"block": block, "inventory_row": int(rows[i]), "position": hit.tolist(),
                     "gathered": repr(float(arr[tuple(hit)])), "shard": index.files[shard],
                     "row_in_shard": local}
            with np.load(index.files[shard]) as blob:
                if block == "globals":
                    entry["stored"] = repr(float(blob["globals"][local, hit[1]]))
                else:
                    tok, col = int(hit[1]), int(hit[2])
                    member, c = ("tokens", col) if col < 5 else ("add_info", col - 5)
                    entry["stored_member"] = member
                    entry["stored"] = repr(float(blob[member][local, tok, c]))
                    entry["stored_token"] = [repr(float(x)) for x in blob["tokens"][local, tok]]
                    entry["stored_add_info"] = [repr(float(x)) for x in blob["add_info"][local, tok]]
            out.append(entry)
    return out


def gather_legs(index: TheirsIndex, legs: Mapping[str, np.ndarray], pass_reco: np.ndarray,
                **kw: Any) -> dict[str, Any]:
    """Several sorted row sets in ONE pass over the shards (their union), split back per leg."""
    checked = {name: check_rows(r, index.row_index.shape[0], name) for name, r in legs.items()}
    union = np.unique(np.concatenate(list(checked.values())))
    blob = gather(index, union, pass_reco, **kw)
    out: dict[str, Any] = {"union": blob["record"], "legs": {}}
    for name, r in checked.items():
        pos = np.searchsorted(union, r)
        packed, glob = blob["packed"][pos], blob["globals"][pos]
        out[name] = {"packed": packed, "globals": glob}
        out["legs"][name] = {"rows": int(r.size), "rows_sha256": rows_digest(r),
                             "packed_sha256": sha256_array(packed),
                             "globals_sha256": sha256_array(glob)}
    return out


# ------------------------------------------------------------------------------------------- #
# A keyed per-replicate cache (the P2pre and P2scr runs of one replicate share their inputs)
# ------------------------------------------------------------------------------------------- #
def cache_key(index: TheirsIndex, pass_reco_sha256: str, legs: Mapping[str, np.ndarray]) -> str:
    payload = {"schema": SCHEMA, "join_sig_npz_sha256": index.record["join_sig_npz_sha256"],
               "join_sig_json_sha256": index.record["join_sig_json_sha256"],
               "pass_reco_sha256": pass_reco_sha256, "token_cap": TOKEN_CAP,
               "legs": {k: rows_digest(v) for k, v in sorted(legs.items())},
               "materialize_sha256": sha256_file(mtz.__file__),
               "this_module_sha256": sha256_file(__file__)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def gather_legs_cached(index: TheirsIndex, legs: Mapping[str, np.ndarray], pass_reco: np.ndarray,
                       pass_reco_sha256: str, cache: Path | None, **kw: Any) -> dict[str, Any]:
    key = cache_key(index, pass_reco_sha256, legs)
    if cache is not None and Path(cache).exists():
        with np.load(cache, allow_pickle=False) as blob:
            if str(blob["key"]) != key:
                raise JoinError(f"[theirs_rows] cache {cache} has another key; refusing")
            out: dict[str, Any] = {"legs": {}, "cache": {"path": str(cache), "key": key,
                                                         "reused": True}}
            for name, r in legs.items():
                if not np.array_equal(blob[f"{name}_rows"], np.asarray(r, np.int64)):
                    raise JoinError(f"[theirs_rows] cache rows of {name} differ")
                out[name] = {"packed": np.asarray(blob[f"{name}_packed"]),
                             "globals": np.asarray(blob[f"{name}_globals"])}
                out["legs"][name] = {"rows": int(len(r)), "rows_sha256": rows_digest(r),
                                     "packed_sha256": sha256_array(out[name]["packed"]),
                                     "globals_sha256": sha256_array(out[name]["globals"])}
            out["union"] = json.loads(str(blob["union_record"]))
        return out
    out = gather_legs(index, legs, pass_reco, **kw)
    out["cache"] = {"path": None if cache is None else str(cache), "key": key, "reused": False}
    if cache is not None:
        cache = Path(cache)
        cache.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache.with_name(cache.name + f".tmp{os.getpid()}.npz")
        arrays = {"key": np.array(key), "union_record": np.array(json.dumps(out["union"]))}
        for name, r in legs.items():
            arrays.update({f"{name}_rows": np.asarray(r, np.int64),
                           f"{name}_packed": out[name]["packed"],
                           f"{name}_globals": out[name]["globals"]})
        np.savez(tmp, **arrays)
        os.replace(tmp, cache)
    return out


# ------------------------------------------------------------------------------------------- #
# Crosscheck against the historical caches
# ------------------------------------------------------------------------------------------- #
def crosscheck(cache: Path, inputs_npz: Path, join_dir: Path, max_rows: int | None = None,
               seed: int = 0, inventory_rows: int = INVENTORY_ROWS,
               chunk_rows: int = 50_000) -> dict[str, Any]:
    """Byte-compare `gather` with a `prematerialize_theirs` cache on the rows it holds.

    The cache stores the pseudodata leg for `rows_a[s1_a]` and the prior leg for `rows_b`, in the
    historical order. Both legs are gathered here in ONE pass (their sorted union, as
    `gather_legs` does) and compared with the cache row by row in the cache's order, in chunks
    (bounded memory), with running digests over the whole leg."""
    t0 = time.perf_counter()
    index = load_index(join_dir, inventory_rows=inventory_rows)
    pass_reco, pass_sha = read_pass_reco(inputs_npz)
    blob = np.load(cache, mmap_mode="r")
    rows_a, s1_a, rows_b = (np.asarray(blob["rows_a"]), np.asarray(blob["s1_a"]).astype(bool),
                            np.asarray(blob["rows_b"]))
    legs_hist = {"pdata": (rows_a[s1_a], "pdata_packed", "pdata_globals"),
                 "prior": (rows_b, "prior_packed", "prior_globals")}
    rng = np.random.default_rng(seed)
    take = {}
    for name, (r, _, _) in legs_hist.items():
        idx = np.arange(r.size)
        if max_rows is not None and r.size > max_rows:
            idx = np.sort(rng.choice(r.size, max_rows, replace=False))
        take[name] = idx
    union = np.unique(np.concatenate([legs_hist[n][0][take[n]] for n in legs_hist]))
    got = gather(index, union, pass_reco)
    del pass_reco
    report: dict[str, Any] = {"schema": SCHEMA + "/crosscheck", "cache": str(cache),
                              "cache_sha256": sha256_file(cache), "cache_key": str(blob["key"]),
                              "join": index.record, "pass_reco_sha256": pass_sha,
                              "max_rows": max_rows, "union": got["record"], "legs": {}}
    for name, (r, kp, kg) in legs_hist.items():
        hist_rows = r[take[name]]
        if np.unique(hist_rows).size != hist_rows.size:
            raise JoinError(f"[theirs_rows] cache leg {name} repeats rows")
        pos = np.searchsorted(union, hist_rows)
        ref_p_all, ref_g_all = blob[kp], blob[kg]
        digests = {k: hashlib.sha256() for k in ("mine_p", "ref_p", "mine_g", "ref_g")}
        counts = {"packed_elements_differing": 0, "packed_rows_differing": 0,
                  "globals_elements_differing": 0}
        dtype_shape = {"packed": True, "globals": True}
        for lo in range(0, hist_rows.size, chunk_rows):
            sl = slice(lo, lo + chunk_rows)
            mine_p, mine_g = got["packed"][pos[sl]], got["globals"][pos[sl]]
            ref_p = np.asarray(ref_p_all[take[name][sl]])
            ref_g = np.asarray(ref_g_all[take[name][sl]])
            dtype_shape["packed"] &= bool(mine_p.dtype == ref_p.dtype
                                          and mine_p.shape == ref_p.shape)
            dtype_shape["globals"] &= bool(mine_g.dtype == ref_g.dtype
                                           and mine_g.shape == ref_g.shape)
            for key, arr in (("mine_p", mine_p), ("ref_p", ref_p), ("mine_g", mine_g),
                             ("ref_g", ref_g)):
                digests[key].update(np.ascontiguousarray(arr).tobytes())
            diff_p = ~((mine_p == ref_p) | (np.isnan(mine_p) & np.isnan(ref_p)))
            counts["packed_elements_differing"] += int(diff_p.sum())
            counts["packed_rows_differing"] += int(diff_p.reshape(diff_p.shape[0], -1)
                                                   .any(1).sum())
            counts["globals_elements_differing"] += int((mine_g != ref_g).sum())
        hexd = {k: v.hexdigest() for k, v in digests.items()}
        report["legs"][name] = {
            "rows_compared": int(hist_rows.size), "rows_in_cache_leg": int(r.size),
            "packed_dtype_shape_equal": dtype_shape["packed"],
            "globals_dtype_shape_equal": dtype_shape["globals"],
            "packed_bytes_equal": bool(dtype_shape["packed"] and hexd["mine_p"] == hexd["ref_p"]),
            "globals_bytes_equal": bool(dtype_shape["globals"]
                                        and hexd["mine_g"] == hexd["ref_g"]),
            **counts, "packed_sha256": hexd["mine_p"], "globals_sha256": hexd["mine_g"],
            "cache_packed_sha256": hexd["ref_p"], "cache_globals_sha256": hexd["ref_g"]}
    report["all_bytes_equal"] = all(v["packed_bytes_equal"] and v["globals_bytes_equal"]
                                    for v in report["legs"].values())
    report["seconds"] = time.perf_counter() - t0
    report["slurm_job_id"] = os.environ.get("SLURM_JOB_ID")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crosscheck", help="byte-compare with a historical theirs cache")
    c.add_argument("--cache", type=Path, required=True)
    c.add_argument("--inputs-npz", type=Path, required=True)
    c.add_argument("--join-dir", type=Path, default=JOIN_DIR)
    c.add_argument("--max-rows", type=int, default=None,
                   help="compare a random subset of this many rows per leg (default: all)")
    c.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                  npz_keys_read=["pass_reco"],
                                  input_paths=[a.inputs_npz, a.cache, a.join_dir])
    report = crosscheck(a.cache, a.inputs_npz, a.join_dir, a.max_rows)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({"all_bytes_equal": report["all_bytes_equal"],
                      "legs": {k: {kk: v[kk] for kk in ("rows_compared", "packed_bytes_equal",
                                                        "globals_bytes_equal")}
                               for k, v in report["legs"].items()},
                      "seconds": report["seconds"]}))
    return 0 if report["all_bytes_equal"] else 1


if __name__ == "__main__":
    sys.exit(main())
