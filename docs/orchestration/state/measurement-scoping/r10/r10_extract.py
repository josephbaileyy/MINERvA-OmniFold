#!/usr/bin/env python3
"""R10 (ii): attach whole-event reco branches and the true neutrino energy to every row of ``of_inputs_5d.npz``.

The rows of ``of_inputs_5d.npz`` carry no event identity. MP-2 S1 (``measurement-paper/phase1/mp2/mp2_s1_dump.py``)
recovered it: the G2 full-phase-space ``mc_signal_reco`` rows inside the kinematic truth phase space, in playlist
order, equal ``MCgen`` bitwise, and each S1 row carries (mc_run, mc_subrun, mc_nthEvtInFile), the index of its
MasterAnaDev file in the playlist's MC manifest, and ``mc_incomingE``. This script reuses that alignment and adds the
reco tree. Per playlist:

  1. load the S1 rows (sha256 against MP-2's committed list) and the ``of_inputs_5d`` slice they cover;
  2. read the G2 rows (identity, truth and reco scalars, reco vertex) and select the kinematic truth phase space with
     S1's own ``in_ps`` (imported unchanged, digest-pinned);
  3. ADMISSION, before anything is joined: the selected count equals S1's; the identity equals S1's bitwise; every
     ``of_inputs_5d`` reco-passing row is G2-reco-passing; on those rows the G2 reco scalars, cast as ``nn_dump_inputs``
     casts them, equal ``MCreco`` bitwise;
  4. for each MasterAnaDev file the reco-passing rows point to, read the reco tree (``MasterAnaDev``): identity,
     ``vtx`` and the candidate branches; join each row by identity within its own file;
  5. JOIN CONTROLS: every reco-passing row joins; within a file an identity occurs at most once; the joined entry's
     ``vtx[0:3]`` equals the G2 reco vertex to ``vertex_tol_mm``.

Any failed admission or control: exit 7, and nothing is written. The output holds the raw branches in ``MCgen`` order,
NaN on rows that do not pass reco, and ``E_nu_MeV`` on every row. The derived variables C1-C4 are built in ``r10.py``.

Usage (omnifold_py310: uproot, awkward; no ROOT):
    python3 r10_extract.py --config config.json --out OUTDIR --nproc N [--playlists 1L]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCAL = ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W")
RECO = ("sim", "sim_pz", "sim_eavail", "sim_q3", "sim_W")
IDENT = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
VTX = ("vtx_reco_x", "vtx_reco_y", "vtx_reco_z")
ADMISSION_FAILED = 7  # distinct from mnv_guarded_run's own exit codes


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_pinned(path: Path, expect: str, name: str):
    got = sha256(path)
    if got != expect:
        raise SystemExit(f"refusing: {path} sha256 {got} is not the pinned {expect}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def cast(cols: dict) -> np.ndarray:
    """``nn_dump_inputs``' float32 cast, with the producer's non-finite -> -9999.0 (as MP-2 S1 restates it)."""
    return np.column_stack([np.where(np.isfinite(cols[c]), cols[c], -9999.0) for c in cols]).astype(np.float32)


def read_reco_tree(task):
    """One MasterAnaDev reco tree: identity keys, vtx and the candidate branches."""
    import uproot
    fn, branches, pack = task
    eid = sys.modules.get("r10_event_identity") or load_pinned(*pack, "r10_event_identity")
    t = uproot.open(fn)["MasterAnaDev"]
    a = t.arrays(list(IDENT) + ["vtx"] + list(branches), library="np")
    key = eid.pack_identity(a["mc_run"], a["mc_subrun"], a["mc_nthEvtInFile"])
    v = a["vtx"]
    vtx = (np.stack(v)[:, :3] if v.dtype == object else np.asarray(v)[:, :3]).astype(float) if len(v) else np.zeros((0, 3))
    return {"key": key, "vtx": vtx, **{b: np.asarray(a[b], float) for b in branches}, "n": int(t.num_entries)}


def join_rows(n: int, rows: np.ndarray, key: np.ndarray, fidx: np.ndarray, vtx_g2: np.ndarray, trees: dict,
              branches: list, tol_mm: float) -> tuple[dict, dict]:
    """Join each row in ``rows`` to the reco-tree entry with its identity ``key`` in its own file ``fidx``.

    Returns the branch values (NaN where not joined) and the join controls: every row joined, no identity repeated
    within a file, and the joined entry's vertex equal to the G2 reco vertex within ``tol_mm``."""
    out = {b: np.full(n, np.nan) for b in branches}
    found = np.zeros(n, bool)
    dup_all, dup_needed, worst = 0, 0, 0.0
    for i, tr in trees.items():
        order = np.argsort(tr["key"], kind="stable")
        ks = tr["key"][order]
        dup = ks[1:][ks[1:] == ks[:-1]]
        dup_all += int(dup.size)
        sel = rows[fidx[rows] == i]
        if ks.size == 0 or sel.size == 0:
            continue
        dup_needed += int(np.isin(key[sel], dup).sum())
        pos = np.clip(np.searchsorted(ks, key[sel]), 0, ks.size - 1)
        hit = ks[pos] == key[sel]
        ent, r = order[pos[hit]], sel[hit]
        found[r] = True
        if r.size:
            worst = max(worst, float(np.max(np.abs(tr["vtx"][ent] - vtx_g2[r]))))
        for b in branches:
            out[b][r] = tr[b][ent]
    ctl = {"rows_to_join": int(rows.size), "rows_joined": int(found[rows].sum()),
           "duplicate_keys_within_file_all": dup_all, "joined_rows_with_a_duplicated_key": dup_needed,
           "max_abs_vertex_diff_mm": worst}
    ctl["pass"] = ctl["rows_joined"] == ctl["rows_to_join"] and dup_needed == 0 and worst <= tol_mm
    return out, ctl


def playlist(p: str, cfg: dict, ev: dict, pool, pack) -> tuple[dict, dict]:
    import uproot
    t0 = time.time()
    eid = sys.modules["r10_event_identity"]
    s1m = sys.modules["r10_mp2_s1_dump"]
    src = cfg["inputs"]
    s1 = np.load(f"{src['s1_dir']}/s1_{p}.npz", allow_pickle=False)
    r0, n = int(s1["mcgen_row0"]), int(s1["n_rows"])
    pr = ev["pass_reco"][r0:r0 + n]
    mcreco = ev["MCreco"][r0:r0 + n]
    e0, e1 = ev["edges_0"], ev["edges_1"]
    g = uproot.open(f"{src['g2_dir']}/runEventLoopOmniFold_G2_FPS_{p}.root")["mc_signal_reco"].arrays(
        list(SCAL) + list(RECO) + list(IDENT) + list(VTX) + ["sim_pass"], library="np")
    ps, _ = s1m.in_ps(g["MC"], g["MC_pz"], e0[0], e0[-1], e1[0], e1[-1])
    g = {k: np.asarray(v)[ps] for k, v in g.items()}
    sim_pass = g["sim_pass"].astype(bool)
    adm = {"n_rows": n, "g2_in_ps": int(ps.sum()), "count_equal": int(ps.sum()) == n}
    adm["identity_equal_s1"] = adm["count_equal"] and all(np.array_equal(g[k], s1[k]) for k in IDENT)
    adm["truth_equal_s1"] = adm["count_equal"] and all(
        np.array_equal(g[k], s1[f"g2_{k}"], equal_nan=True) for k in SCAL)
    adm["truth_bitwise_mcgen"] = adm["count_equal"] and bool(np.array_equal(
        cast({c: g[c] for c in SCAL}), ev["MCgen"][r0:r0 + n]))
    adm["n_pass_reco"], adm["n_g2_pass_only"] = int(pr.sum()), int((sim_pass & ~pr).sum()) if adm["count_equal"] else -1
    adm["pass_reco_subset_of_g2"] = adm["count_equal"] and not bool(np.any(pr & ~sim_pass))
    adm["reco_bitwise_on_pass_rows"] = adm["count_equal"] and bool(
        np.array_equal(cast({c: g[c][pr] for c in RECO}), mcreco[pr]))
    adm["pass"] = all(adm[k] for k in ("count_equal", "identity_equal_s1", "truth_equal_s1", "truth_bitwise_mcgen",
                                         "pass_reco_subset_of_g2", "reco_bitwise_on_pass_rows"))
    adm["seconds_g2_and_admission"] = time.time() - t0
    if not adm["pass"]:
        return adm, {}
    man = Path(f"{src['manifests']}/{p}_MC.txt")
    adm["manifest_sha256_equals_s1"] = sha256(man) == ev["s1_manifest_sha256"][str(man)]
    if not adm["manifest_sha256_equals_s1"]:
        adm["pass"] = False
        return adm, {}
    files = [ln.strip() for ln in man.read_text().splitlines() if ln.strip()]
    fidx = np.asarray(s1["mad_file_index"], np.int64)
    rows = np.flatnonzero(pr)
    need = np.unique(fidx[rows])
    branches = cfg["branches"]
    trees = dict(zip(need.tolist(), pool.map(read_reco_tree, [(files[i], branches, pack) for i in need], chunksize=1)))
    key = eid.pack_identity(s1["mc_run"], s1["mc_subrun"], s1["mc_nthEvtInFile"])
    vtx_g2 = np.column_stack([g[c] for c in VTX]).astype(float)
    out, ctl = join_rows(n, rows, key, fidx, vtx_g2, trees, branches, float(cfg["controls"]["vertex_tol_mm"]))
    ctl.update({"files_read": int(need.size), "reco_entries_read": int(sum(t["n"] for t in trees.values()))})
    adm["join"] = ctl
    adm["pass"] = adm["pass"] and ctl["pass"]
    adm["seconds_total"] = time.time() - t0
    out["E_nu_MeV"] = np.asarray(s1["mc_incomingE"], float)
    out["mcgen_row0"] = r0
    return adm, out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=HERE / "config.json")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--nproc", type=int, default=32)
    ap.add_argument("--playlists", default=None, help="comma-separated subset (smoke job); default all twelve")
    a = ap.parse_args(argv)
    t0 = time.time()
    cfg = json.loads(a.config.read_text())["extract"]
    src = cfg["inputs"]
    rec = {"schema": "r10-extract/1", "argv": sys.argv, "host": os.uname().nodename,
           "slurm_job": os.environ.get("SLURM_JOB_ID"), "python": sys.version.split()[0],
           "numpy": np.__version__, "code": {"r10_extract.py": sha256(Path(__file__).resolve())},
           "inputs": {}, "playlists": {}}
    pack = (REPO / cfg["code"]["event_identity"]["path"], cfg["code"]["event_identity"]["sha256"])
    load_pinned(*pack, "r10_event_identity")
    load_pinned(REPO / cfg["code"]["mp2_s1_dump"]["path"], cfg["code"]["mp2_s1_dump"]["sha256"], "r10_mp2_s1_dump")
    import uproot
    rec["uproot"] = uproot.__version__
    # digests: the event file, MP-2's S1 files (its committed list) and the G2 files (their own receipts)
    s1_list = dict(reversed(ln.split()) for ln in (REPO / src["s1_sha256_list"]).read_text().splitlines() if ln.strip())
    pls = a.playlists.split(",") if a.playlists else cfg["playlists"]
    ctx = mp.get_context("fork")
    with ctx.Pool(a.nproc) as pool:
        checks = {src["of_inputs"]: cfg["of_inputs_sha256"]}
        for p in pls:
            checks[f"{src['s1_dir']}/s1_{p}.npz"] = next(v for k, v in s1_list.items() if k.endswith(f"s1_{p}.npz"))
            g2r = json.loads(Path(f"{src['g2_dir']}/G2_receipt_{p}.json").read_text())
            checks[f"{src['g2_dir']}/runEventLoopOmniFold_G2_FPS_{p}.root"] = g2r["final_root"]["sha256"]
        got = dict(zip(checks, pool.map(sha256, list(checks))))
        rec["inputs"] = {k: {"sha256": got[k], "expected": v, "match": got[k] == v} for k, v in checks.items()}
        rec["seconds_hash"] = time.time() - t0
        if not all(x["match"] for x in rec["inputs"].values()):
            return finish(rec, a.out, t0, ADMISSION_FAILED, None)
        z = np.load(src["of_inputs"], allow_pickle=False)
        s1r = json.loads((REPO / src["s1_receipt"]).read_text())
        ev = {"pass_reco": np.asarray(z["pass_reco"], bool), "MCreco": np.asarray(z["MCreco"]),
              "MCgen": np.asarray(z["MCgen"]),
              "edges_0": np.asarray(z["edges_0"], float), "edges_1": np.asarray(z["edges_1"], float),
              "s1_manifest_sha256": {k: v["sha256"] for k, v in s1r["inputs"].items() if k.endswith("_MC.txt")}}
        rec["seconds_hash_and_load"] = time.time() - t0
        n_rows = int(ev["pass_reco"].shape[0])
        cols = {b: np.full(n_rows, np.nan, np.float64) for b in cfg["branches"] + ["E_nu_MeV"]}
        covered = np.zeros(n_rows, bool)
        for p in pls:
            adm, out = playlist(p, cfg, ev, pool, pack)
            rec["playlists"][p] = adm
            print(p, json.dumps(adm), flush=True)
            if not adm["pass"]:
                return finish(rec, a.out, t0, ADMISSION_FAILED, None)
            r0 = out.pop("mcgen_row0")
            n = adm["n_rows"]
            for b, v in out.items():
                cols[b][r0:r0 + n] = v
            covered[r0:r0 + n] = True
    rec["rows"] = {"n_rows": n_rows, "covered": int(covered.sum()),
                   "complete": bool(covered.all()) if not a.playlists else None}
    return finish(rec, a.out, t0, 0, cols)


def finish(rec: dict, out: Path, t0: float, code: int, cols: dict | None) -> int:
    out.mkdir(parents=True, exist_ok=True)
    if cols is not None:
        tmp = out / f"r10_extra.partial-{os.getpid()}.npz"
        np.savez(tmp, **cols)
        os.replace(tmp, out / "r10_extra.npz")
        rec["output"] = {"file": str(out / "r10_extra.npz"), "sha256": sha256(out / "r10_extra.npz"),
                         "arrays": sorted(cols)}
    rec["exit"] = code
    rec["resources"] = {"wall_s": time.time() - t0,
                        "max_rss_kb_self": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        "max_rss_kb_children": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
    (out / "r10_extract_receipt.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    print("exit", code, flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
