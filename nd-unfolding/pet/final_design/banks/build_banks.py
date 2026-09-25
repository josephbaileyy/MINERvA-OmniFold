"""Freeze the event banks of the PET final-design study (PROTOCOL-20260925 section 3).

Every inventory row that passes truth is assigned to exactly one bank:

* **FB** (final bank): rows of predecessor pools P, F, S, T that no scored predecessor draw ever
  selected (they entered only whole-pool aggregate target spectra);
* **RB** (reserve bank): predecessor pool R, never opened by any predecessor code;
* **DEV**: every other truth-passing row (the historical comparison's 2M subsample, the rows every
  scored predecessor draw consumed).

"Scored predecessor draws" are reconstructed here, exactly, with the predecessor's own draw
algorithm (`improvement_campaign/phase_e/replicates.py`: the same salts, hashes, orderings and
slicing as `draw_replicates`, only with the hashing spread over worker processes). The draw plan
(`DRAW_PLAN`) is the one declared by the study orchestrator; every reconstructed draw is checked
against the row digests (`replicates.rows_digest`) recorded in the predecessor's committed
receipts (`confirm/results/**.json`) and Phase E records (`phase_e/results/*.json`). The build
refuses (writes nothing) if any recorded digest differs from its reconstruction, if a committed
record names a draw the plan does not reconstruct (the plan would then not cover every consumed
row), or if a bank count differs from the declared expectation.

Outputs in `--out-dir`: `banks.npz` (`bank_code` int8 per inventory row: -1 not truth-passing,
0 DEV, 1 FB, 2 RB; and the sorted int64 row arrays `rows_DEV`, `rows_FB`, `rows_RB`) and
`BANK_MANIFEST.json` (counts, sorted-row sha256 per bank, input sha256s, code commit, the
per-draw digest checks). Nothing here reads event content beyond `pass_truth` (through
`authorization_scope.SignalOnlyNpz`); no real data. PET is diagnostic method development.

    build_banks.py --inventory G2_FPS_MEFHC_P12.npz --identity-sidecar ...identity.npz
        --pools-npz .../pools.npz --out-dir .../impl-runner/banks [--workers 4]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PET = STUDY.parent
REPO = PET.parents[1]
CAMPAIGN = PET / "improvement_campaign"
for _p in (CAMPAIGN / "phase_e", CAMPAIGN):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import replicates as rp  # noqa: E402

SCHEMA = "pet-final-design-bank-manifest/1"
POOL_MANIFEST = CAMPAIGN / "pools" / "POOL_MANIFEST.json"
RECORD_DIRS = (CAMPAIGN / "confirm" / "results", CAMPAIGN / "phase_e" / "results")
# The historical comparison's loader subsample (its 2M rows are DEV by definition): the events
# block of the predecessor's frozen configuration C, read, never retyped.
FROZEN_C = (CAMPAIGN / "phase_b" / "pet" / "configs" / "b2e4-M-K10-s1.json",
            "0afffb7d4402a1dbb32f28397b53bd05c9378c21c907624fc75450dfaa35a9f2")

BANK_CODES = {"DEV": 0, "FB": 1, "RB": 2}
NO_BANK = -1
HP, HD = 600_130, 600_111          # historical prior / pseudodata sizes
HIST = "confirm-historical-size-v1"
# (pool, family, n_prior, n_pseudo, disjoint, replicates): every scored predecessor draw.
DRAW_PLAN: tuple = (
    ("P", HIST, HP, HD, True, tuple(range(3))),
    ("F", HIST, HP, HD, True, tuple(range(12))),
    ("S", HIST, HP, HD, True, (0,)),
    ("S", "E1-assessment-1x", HP, HD, True, tuple(range(3))),
    ("S", "E1-assessment-8x", 8 * HP, 8 * HD, False, tuple(range(3))),
    ("T", HIST, HP, HD, True, tuple(range(2))),
    ("T", "E1-identifiability", HD, HD, True, (0,)),
    ("T", "E1-identifiability-null", HD, HD, False, tuple(range(20))),
    ("T", "E1-references", HP, HD, True, tuple(range(3))),
)
FB_POOLS = ("P", "F", "S", "T")
RB_POOL = "R"
# The declared expectation (study orchestrator's consumption audit, 2026-09-25).
EXPECTED = {"FB": 2_646_891, "RB": 1_414_846,
            "FB_by_pool": {"P": 172_677, "F": 680_794, "S": 1_690_695, "T": 102_725}}
# Two rows of the historical 2M subsample that the pool builder did not exclude and that
# predecessor draws selected; they must end up in DEV.
KNOWN_HISTORICAL_ROWS_IN_POOLS = (35_796_924, 35_824_188)


# ------------------------------------------------------------------------------------------- #
# Hashing, spread over forked workers (bit-identical to replicates.uniform_hash)
# ------------------------------------------------------------------------------------------- #
_IDENTITY: np.ndarray | None = None


def _hash_chunk(task: tuple[np.ndarray, int]) -> np.ndarray:
    rows, seed = task
    return rp.uniform_hash(_IDENTITY[rows], seed)


class Hasher:
    """`uniform_hash(identity[rows], seed)` for inventory rows, optionally in worker processes
    (fork: the workers share the identity array). The result does not depend on `workers`."""

    def __init__(self, identity: np.ndarray, workers: int = 1, min_parallel: int = 200_000):
        global _IDENTITY
        _IDENTITY = np.ascontiguousarray(identity, dtype=np.int64)
        self.identity = _IDENTITY
        self.workers = max(1, int(workers))
        self.min_parallel = int(min_parallel)
        self.pool = (mp.get_context("fork").Pool(self.workers) if self.workers > 1 else None)
        self.n_hashed = 0

    def __call__(self, rows: np.ndarray, seed: int) -> np.ndarray:
        rows = np.asarray(rows, dtype=np.int64)
        self.n_hashed += int(rows.size)
        if self.pool is None or rows.size < self.min_parallel:
            return rp.uniform_hash(self.identity[rows], seed)
        parts = np.array_split(rows, self.workers * 4)
        return np.concatenate(self.pool.map(_hash_chunk, [(p, int(seed)) for p in parts]))

    def close(self) -> None:
        if self.pool is not None:
            self.pool.close()
            self.pool.join()
            self.pool = None


def draw_family(design: rp.ReplicateDesign, replicates: Iterable[int], rows: np.ndarray,
                hasher: Callable[[np.ndarray, int], np.ndarray]
                ) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """`replicates.draw_replicates(design, replicates, rows, identity[rows])` (no exclusion),
    step for step; returns {replicate: (prior_rows, pseudo_rows)} in u_r order."""
    rows = np.asarray(rows, dtype=np.int64)
    reps = sorted({int(r) for r in replicates})
    if design.block > rows.size:
        raise SystemExit(f"[banks] {design.family}: one replicate needs {design.block} rows, "
                         f"{rows.size} available")
    if design.disjoint:
        cap = design.capacity(rows.size)
        if reps and reps[-1] >= cap:
            raise SystemExit(f"[banks] {design.family}: replicate {reps[-1]} exceeds the "
                             f"disjoint capacity {cap}")
        family_order = rp._order(hasher(rows, rp.seed_from_salt(design.family_salt())), rows)
    out = {}
    for r in reps:
        seed_r = rp.seed_from_salt(design.replicate_salt(r))
        if design.disjoint:
            pos = family_order[r * design.block:(r + 1) * design.block]
        else:
            pos = rp._order(hasher(rows, seed_r), rows)[:design.block]
        pos = pos[rp._order(hasher(rows[pos], seed_r), rows[pos])]
        out[r] = (rows[pos[:design.n_prior]], rows[pos[design.n_prior:]])
    return out


# ------------------------------------------------------------------------------------------- #
# The predecessor's committed draw records
# ------------------------------------------------------------------------------------------- #
def _walk_draw_records(node: Any, found: list[dict[str, Any]]) -> None:
    if isinstance(node, dict):
        design = node.get("design")
        if (isinstance(design, dict) and {"pool", "family"} <= set(design)
                and isinstance(node.get("replicate"), int)
                and "prior_rows_sha256" in node and "pseudo_rows_sha256" in node):
            found.append({"pool": design["pool"], "family": design["family"],
                          "replicate": int(node["replicate"]),
                          "n_prior": design.get("n_prior"), "n_pseudo": design.get("n_pseudo"),
                          "disjoint": design.get("disjoint"),
                          "prior": node["prior_rows_sha256"],
                          "pseudo": node["pseudo_rows_sha256"]})
            return
        for value in node.values():
            _walk_draw_records(value, found)
    elif isinstance(node, list):
        for value in node:
            _walk_draw_records(value, found)


def committed_draw_records(record_dirs: Sequence[Path] = RECORD_DIRS, base: Path = REPO
                           ) -> dict[str, list[dict[str, Any]]]:
    """Every (pool/family/replicate) row-digest record in the committed predecessor JSONs:
    {key: [{source, prior, pseudo, n_prior, n_pseudo, disjoint}, ...]} (one entry per distinct
    (source, digests) pair)."""
    out: dict[str, list[dict[str, Any]]] = {}
    for directory in record_dirs:
        for path in sorted(Path(directory).rglob("*.json")):
            text = path.read_text()
            if "prior_rows_sha256" not in text:
                continue
            found: list[dict[str, Any]] = []
            _walk_draw_records(json.loads(text), found)
            try:
                source = str(path.resolve().relative_to(Path(base).resolve()))
            except ValueError:
                source = str(path)
            for rec in found:
                key = f"{rec['pool']}/{rec['family']}/{rec['replicate']}"
                entry = {"source": source, "prior": rec["prior"], "pseudo": rec["pseudo"],
                         "n_prior": rec["n_prior"], "n_pseudo": rec["n_pseudo"],
                         "disjoint": rec["disjoint"]}
                if entry not in out.setdefault(key, []):
                    out[key].append(entry)
    return out


def check_digests(reconstructed: Mapping[str, dict[str, Any]],
                  records: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Compare every reconstructed draw with every committed record of it; refuse a record the
    plan does not reconstruct."""
    per_key = {}
    for key, rec in sorted(reconstructed.items()):
        entries = records.get(key, [])
        mism = [e for e in entries
                if (e["prior"], e["pseudo"]) != (rec["prior_rows_sha256"], rec["pseudo_rows_sha256"])
                or (e["n_prior"], e["n_pseudo"], e["disjoint"])
                != (rec["n_prior"], rec["n_pseudo"], rec["disjoint"])]
        status = "MISMATCH" if mism else ("match" if entries else "no committed record")
        per_key[key] = {"status": status, "n_records": len(entries),
                        "sources": sorted({e["source"] for e in entries}),
                        "mismatching_sources": sorted({e["source"] for e in mism})}
    unplanned = sorted(set(records) - set(reconstructed))
    summary = {
        "n_reconstructed": len(reconstructed),
        "n_match": sum(v["status"] == "match" for v in per_key.values()),
        "n_mismatch": sum(v["status"] == "MISMATCH" for v in per_key.values()),
        "no_committed_record": sorted(k for k, v in per_key.items()
                                      if v["status"] == "no committed record"),
        "records_not_in_plan": unplanned,
        "n_record_files_scanned_with_digests": len({s for v in records.values() for s in
                                                    (e["source"] for e in v)}),
    }
    summary["ok"] = summary["n_mismatch"] == 0 and not unplanned
    return {"summary": summary, "per_draw": per_key}


# ------------------------------------------------------------------------------------------- #
# Inputs
# ------------------------------------------------------------------------------------------- #
def sha256_file(path: Path | str) -> str:
    return rp.sha256_file(path)


def read_pass_truth(inventory: Path) -> np.ndarray:
    """`pass_truth` only, through the campaign's signal-only view of the inventory."""
    raw = np.load(inventory, allow_pickle=False)
    view = scope.SignalOnlyNpz(raw)
    try:
        out = np.asarray(view["pass_truth"]).astype(bool)
        keys = list(view.keys_read)
    finally:
        view.close()
    if keys != ["pass_truth"]:
        raise SystemExit(f"[banks] read unexpected inventory members {keys}")
    return out


def historical_load_rows(n_rows: int, frozen: tuple[Path, str] = FROZEN_C
                         ) -> tuple[np.ndarray, dict[str, Any]]:
    """The historical loader's subsample (`build_fullevent_loaders`: sort(default_rng(seed)
    .choice(N, min(max_events, N), replace=False))), with the events block of frozen C."""
    path, want = frozen
    got = sha256_file(path)
    if got != want:
        raise SystemExit(f"[banks] frozen config {path} sha256 {got} != {want}")
    events = json.loads(Path(path).read_text())["events"]
    need = min(int(events["max_events"]), int(n_rows))
    imc = np.sort(np.random.default_rng(int(events["subsample_seed"]))
                  .choice(int(n_rows), need, replace=False)).astype(np.int64)
    return imc, {"source": str(path.relative_to(REPO)) if REPO in path.parents else str(path),
                 "source_sha256": got, "max_events": int(events["max_events"]),
                 "subsample_seed": int(events["subsample_seed"]), "n_rows": int(imc.size)}


def code_state(repo: Path = REPO) -> dict[str, Any]:
    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    status = git("status", "--porcelain")
    return {"commit": git("rev-parse", "HEAD") or None, "clean": status == "",
            "dirty_paths": status.splitlines()[:50]}


# ------------------------------------------------------------------------------------------- #
# The build
# ------------------------------------------------------------------------------------------- #
def build(*, codes: np.ndarray, identity: np.ndarray, pass_truth: np.ndarray,
          plan: Sequence[tuple] = DRAW_PLAN, workers: int = 1,
          historical_rows: np.ndarray | None = None,
          known_historical_rows: Sequence[int] | None = KNOWN_HISTORICAL_ROWS_IN_POOLS,
          log: Callable[[str], None] = print) -> tuple[np.ndarray, dict[str, Any]]:
    """Bank code per inventory row and the build record (no digest check, no I/O)."""
    t0 = time.time()
    codes = np.asarray(codes, dtype=np.int8)
    pass_truth = np.asarray(pass_truth, dtype=bool)
    n = int(codes.size)
    if identity.shape[0] != n or pass_truth.size != n:
        raise SystemExit("[banks] pool codes, identity and pass_truth disagree in length")
    in_pool = codes >= 0
    if bool((in_pool & ~pass_truth).any()):
        raise SystemExit("[banks] a pool row does not pass truth")
    drawn = np.zeros(n, dtype=bool)
    known = (np.zeros(0, np.int64) if known_historical_rows is None
             else np.asarray(known_historical_rows, dtype=np.int64))
    known_hits: dict[int, list[str]] = {int(r): [] for r in known}
    reconstructed: dict[str, dict[str, Any]] = {}
    family_union: dict[str, int] = {}
    hasher = Hasher(identity, workers)
    try:
        for pool, family, n_prior, n_pseudo, disjoint, reps in plan:
            rows = rp.pool_rows(codes, pool)
            design = rp.ReplicateDesign(pool, family, int(n_prior), int(n_pseudo), bool(disjoint))
            got = draw_family(design, reps, rows, hasher)
            fmask = np.zeros(n, dtype=bool)
            for r, (prior, pseudo) in got.items():
                if np.intersect1d(prior, pseudo).size:
                    raise AssertionError(f"{pool}/{family}/{r}: prior and pseudodata share rows")
                reconstructed[f"{pool}/{family}/{r}"] = {
                    "n_prior": int(prior.size), "n_pseudo": int(pseudo.size),
                    "disjoint": bool(disjoint),
                    "prior_rows_sha256": rp.rows_digest(prior),
                    "pseudo_rows_sha256": rp.rows_digest(pseudo)}
                fmask[prior] = True
                fmask[pseudo] = True
                for row in known:
                    for side, arr in (("prior", prior), ("pseudo", pseudo)):
                        if row in arr:
                            known_hits[int(row)].append(f"{pool}/{family}/{r}:{side}")
            family_union[f"{pool}/{family}"] = int(fmask.sum())
            drawn |= fmask
            log(f"[banks] {pool} {family} r{list(reps)[0]}-{list(reps)[-1]}: union "
                f"{int(fmask.sum())} rows ({time.time() - t0:.0f}s)")
        n_hashed = hasher.n_hashed
    finally:
        hasher.close()
    if bool((drawn & ~in_pool).any()):
        raise AssertionError("a reconstructed draw left its pool")
    fb = in_pool & ~drawn & np.isin(codes, [rp.POOL_CODES[p] for p in FB_POOLS])
    rb = codes == rp.POOL_CODES[RB_POOL]
    if bool((rb & drawn).any()):
        raise SystemExit("[banks] a reconstructed draw touches pool R")
    bank = np.full(n, NO_BANK, dtype=np.int8)
    bank[pass_truth] = BANK_CODES["DEV"]
    bank[fb] = BANK_CODES["FB"]
    bank[rb] = BANK_CODES["RB"]
    counts = {name: int((bank == code).sum()) for name, code in BANK_CODES.items()}
    counts["not_truth_passing"] = int((bank == NO_BANK).sum())
    fb_by_pool = {p: int((fb & (codes == rp.POOL_CODES[p])).sum()) for p in FB_POOLS}
    record: dict[str, Any] = {
        "counts": counts, "FB_by_pool": fb_by_pool,
        "pool_usage": {p: {"pool_rows": int((codes == rp.POOL_CODES[p]).sum()),
                           "drawn_union": int((drawn & (codes == rp.POOL_CODES[p])).sum())}
                       for p in FB_POOLS},
        "family_union_rows": family_union, "reconstructed": reconstructed,
        "n_rows_hashed": int(n_hashed), "build_seconds": time.time() - t0,
        "workers": int(workers)}
    if historical_rows is not None:
        hr = np.asarray(historical_rows, dtype=np.int64)
        hr_truth = hr[pass_truth[hr]]
        in_pools = hr[in_pool[hr]]
        record["historical_subsample"] = {
            "n_rows": int(hr.size), "n_truth_passing": int(hr_truth.size),
            "n_truth_passing_not_DEV": int((bank[hr_truth] != BANK_CODES["DEV"]).sum()),
            "rows_in_predecessor_pools": [int(r) for r in in_pools],
            "rows_in_pools_pool": {str(int(r)): next(k for k, v in rp.POOL_CODES.items()
                                                     if v == codes[r]) for r in in_pools},
            "rows_in_pools_drawn": {str(int(r)): bool(drawn[r]) for r in in_pools}}
        if record["historical_subsample"]["n_truth_passing_not_DEV"]:
            raise SystemExit("[banks] a truth-passing row of the historical subsample is not DEV")
    if known_historical_rows is not None:
        record["known_historical_rows_in_pools"] = {
            str(int(r)): {"bank": next((k for k, v in BANK_CODES.items() if v == bank[r]), None),
                          "pool": next((k for k, v in rp.POOL_CODES.items() if v == codes[r]),
                                       None),
                          "drawn": bool(drawn[r]), "drawn_by": known_hits[int(r)]}
            for r in known}
        bad = [int(r) for r in known if bank[r] != BANK_CODES["DEV"]]
        if bad:
            raise SystemExit(f"[banks] historical-2M rows {bad} are not in DEV")
    return bank, record


def check_expected(record: Mapping[str, Any], expected: Mapping[str, Any] | None) -> dict:
    if expected is None:
        return {"checked": False}
    got = {"FB": record["counts"]["FB"], "RB": record["counts"]["RB"],
           "FB_by_pool": record["FB_by_pool"]}
    ok = got == dict(expected)
    if not ok:
        raise SystemExit(f"[banks] bank counts {got} differ from the declared expectation "
                         f"{dict(expected)}; nothing written")
    return {"checked": True, "expected": dict(expected), "equal": True}


def write_outputs(out_dir: Path, bank: np.ndarray, manifest: dict[str, Any]) -> dict[str, str]:
    out_dir = scope.refuse_historical_output(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    npz, man = out_dir / "banks.npz", out_dir / "BANK_MANIFEST.json"
    for p in (npz, man):
        if p.exists():
            raise SystemExit(f"[banks] {p} exists; banks are frozen once (remove it by hand to "
                             "rebuild deliberately)")
    arrays = {"bank_code": bank}
    for name, code in BANK_CODES.items():
        arrays[f"rows_{name}"] = np.flatnonzero(bank == code).astype(np.int64)
    tmp = out_dir / "banks.tmp.npz"
    np.savez(tmp, **arrays)
    os.replace(tmp, npz)
    manifest["output"] = {"banks_npz": str(npz), "banks_npz_sha256": sha256_file(npz),
                          "bank_code_sha256": hashlib.sha256(bank.tobytes()).hexdigest(),
                          "bank_code_dtype": str(bank.dtype), "n_inventory_rows": int(bank.size),
                          "codes": {**BANK_CODES, "not_truth_passing": NO_BANK}}
    manifest["banks"] = {name: {"code": code, "count": int(arrays[f"rows_{name}"].size),
                                "sorted_rows_sha256": rp.rows_digest(arrays[f"rows_{name}"])}
                         for name, code in BANK_CODES.items()}
    tmpm = man.with_suffix(".json.tmp")
    tmpm.write_text(json.dumps(manifest, indent=1, sort_keys=False) + "\n")
    os.replace(tmpm, man)
    return {"banks_npz": str(npz), "manifest": str(man)}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--identity-sidecar", type=Path, required=True)
    ap.add_argument("--pools-npz", type=Path, required=True)
    ap.add_argument("--pool-manifest", type=Path, default=POOL_MANIFEST)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--workers", type=int,
                    default=int(os.environ.get("SLURM_CPUS_PER_TASK", "1")))
    ap.add_argument("--no-expectations", action="store_true",
                    help="skip the declared-count and known-row checks (synthetic tests only)")
    args = ap.parse_args(argv)
    t0 = time.time()
    scope.refuse_historical_output(args.out_dir)
    scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                  npz_keys_read=["pass_truth"],
                                  input_paths=[args.inventory, args.identity_sidecar,
                                               args.pools_npz])
    codes, pool_record = rp.load_pool_codes(args.pools_npz, args.pool_manifest)
    pool_manifest = json.loads(args.pool_manifest.read_text())
    sidecar_sha = sha256_file(args.identity_sidecar)
    if sidecar_sha != pool_manifest["inputs"]["identity_npz"]["sha256"]:
        raise SystemExit("[banks] identity sidecar sha256 differs from the pool manifest")
    inventory_sha = sha256_file(args.inventory)
    if inventory_sha != pool_manifest["inputs"]["truth_npz"]["sha256"]:
        raise SystemExit("[banks] inventory sha256 differs from the pool manifest")
    with np.load(args.identity_sidecar) as blob:
        identity = np.asarray(blob["sig_event_id"]).astype(np.int64)
    pass_truth = read_pass_truth(args.inventory)
    hist_rows, hist_record = historical_load_rows(codes.size)
    records = committed_draw_records()
    bank, build_record = build(
        codes=codes, identity=identity, pass_truth=pass_truth, plan=DRAW_PLAN,
        workers=args.workers, historical_rows=hist_rows,
        known_historical_rows=None if args.no_expectations else KNOWN_HISTORICAL_ROWS_IN_POOLS)
    checks = check_digests(build_record["reconstructed"], records)
    if not checks["summary"]["ok"]:
        raise SystemExit(f"[banks] digest check failed; nothing written: {checks['summary']}")
    expected = check_expected(build_record, None if args.no_expectations else EXPECTED)
    manifest = {
        "schema": SCHEMA, "protocol": "nd-unfolding/pet/final_design/PROTOCOL-20260925.md §3",
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "code": {**code_state(), "script": str(Path(__file__).resolve().relative_to(REPO))
                 if REPO in Path(__file__).resolve().parents else str(Path(__file__)),
                 "script_sha256": sha256_file(Path(__file__).resolve()),
                 "replicates_py_sha256": sha256_file(Path(rp.__file__).resolve())},
        "inputs": {"inventory": str(args.inventory), "inventory_sha256": inventory_sha,
                   "inventory_members_read": ["pass_truth"],
                   "identity_sidecar": str(args.identity_sidecar),
                   "identity_sidecar_sha256": sidecar_sha,
                   "pools": pool_record, "pool_manifest_sha256": sha256_file(args.pool_manifest)},
        "definitions": {
            "FB": "rows of predecessor pools P, F, S, T selected by no reconstructed draw",
            "RB": "predecessor pool R", "DEV": "every other pass_truth row",
            "not_truth_passing": "bank code -1 (never drawn by the study)"},
        "draw_plan": [{"pool": p, "family": f, "n_prior": a, "n_pseudo": b, "disjoint": d,
                       "replicates": list(r)} for p, f, a, b, d, r in DRAW_PLAN],
        "salt": rp.SALT,
        "counts": build_record["counts"], "FB_by_pool": build_record["FB_by_pool"],
        "expected_counts_check": expected,
        "pool_usage": build_record["pool_usage"],
        "family_union_rows": build_record["family_union_rows"],
        "historical_subsample": {**hist_record, **build_record.get("historical_subsample", {})},
        "known_historical_rows_in_pools": build_record.get("known_historical_rows_in_pools"),
        "digest_check": checks, "reconstructed_draws": build_record["reconstructed"],
        "n_rows_hashed": build_record["n_rows_hashed"], "workers": args.workers,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "measured_leg_is_real_data": False,
    }
    manifest["seconds"] = time.time() - t0
    paths = write_outputs(args.out_dir, bank, manifest)
    print(json.dumps({"outputs": paths, "counts": manifest["counts"],
                      "digest_check": checks["summary"],
                      "seconds": manifest["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
