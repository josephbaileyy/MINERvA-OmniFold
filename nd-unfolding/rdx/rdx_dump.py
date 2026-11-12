#!/usr/bin/env python3
"""RDX dump (RDX-DECLARATION.md rev 3 §2 C2, D6): s5p_input_dumps.py lateral, unchanged, then the truthx sidecar.

    rdx_dump.py --omnifile MERGED.root --playlists 1A=PL.root,1B=...  --sidecar truthx.npz  <s5p lateral args>

1. s5p_input_dumps.py lateral runs as it is (it wrote lat_zero.npz), so the main npz is that tool's output, byte for
   byte, and C-ALIGN-ALL compares it with lat_zero.npz.
2. The rows: a replica of unfold_nd_omnifold_unbinned.collect_signal_nd's kept-row walk (the finite-observable
   contract that drops the -9999 truth-sentinel rows, KNOWN_ISSUES 76; s5p_input_dumps.py:94-103) runs over the
   merged omnifile's mc_signal_reco in the same order, calling the same phase-space function on the same doubles,
   and returns the kept entry indices. The dump REFUSES unless the replica's MCgen (cast to float32), MCreco,
   pass_reco, pass_truth, w_truth and w_reco equal the written npz's bitwise: then the kept entries are the npz's
   rows, in its order.
3. The sidecar: truthx (float64, the omnifile's doubles uncast: y5), truthx_names and mc_id (int64: playlist index,
   run, subrun, event; x4) at exactly those entries, and meta naming the npz's sha256. The playlist index is the
   position in --playlists of the per-playlist omnifile whose mc_signal_reco holds the row's run; a run held by two
   playlists, or by none, refuses.

C-TRUTHX-NPZ (rdx_truthx_npz.py) then joins every row back to its per-playlist omnifile.

MEASURES: nothing; it re-expresses the event loop's outputs. CANNOT AUTHORIZE: any reading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
for _p in (str(_ND.parent / "2d-unfolding"), str(_ND), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import rdx_common as C  # noqa: E402

SCHEMA = C.SIDECAR_SCHEMA
TRUTHX = C.TRUTHX
IDS = C.IDS
MC_ID_NAMES = ("playlist_index", "run", "subrun", "event")
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
AXES = ("eavail", "q3", "W")


class DumpError(RuntimeError):
    """The sidecar's rows could not be shown to be the npz's rows."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def kept_walk(c: dict, ex_t: list, ex_r: list, bounds: tuple, pot_scale: float, in_ps) -> tuple[np.ndarray, dict]:
    """collect_signal_nd's kept-row walk (use_weights=True, no universes), on columns c read in tree order.
    Returns the kept entry indices and the arrays the collector would return for them."""
    pt_lo, pt_hi, pz_lo, pz_hi = bounds
    col = {k: np.asarray(v).tolist() for k, v in c.items()}
    n = len(col["MC"])
    ent, tpt, tpz, rpt, rpz, pr, ptr, wtl, wrl = [], [], [], [], [], [], [], [], []
    tex = [[] for _ in ex_t]
    rex = [[] for _ in ex_r]
    for i in range(n):
        a_pt, a_pz = float(col["MC"][i]), float(col["MC_pz"][i])
        b_pt, b_pz = float(col["sim"][i]), float(col["sim_pz"][i])
        passed = col["sim_pass"][i] != 0
        wt, wr = float(col["w_truth"][i]), float(col["w_reco"][i])
        if not (math.isfinite(wt) and math.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4):
            continue
        truth_vals = [float(col[nm][i]) for nm in ex_t]
        reco_vals = [float(col[nm][i]) for nm in ex_r]
        if not (math.isfinite(a_pt) and math.isfinite(a_pz) and all(math.isfinite(v) for v in truth_vals)):
            continue
        wt *= pot_scale
        wr *= pot_scale
        tru_ok = in_ps(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(b_pt) and math.isfinite(b_pz) and all(math.isfinite(v) for v in reco_vals)
                  and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru_ok or (passed and rec_ok)):
            continue
        sel = passed and rec_ok
        ent.append(i)
        tpt.append(a_pt)
        tpz.append(a_pz)
        rpt.append(b_pt if sel else -9999.0)
        rpz.append(b_pz if sel else -9999.0)
        for k in range(len(ex_t)):
            tex[k].append(truth_vals[k])
            rex[k].append(reco_vals[k] if sel else -9999.0)
        pr.append(sel)
        ptr.append(tru_ok)
        wtl.append(wt)
        wrl.append(wr)
    arrays = {"MCgen": np.column_stack([tpt, tpz, *tex]).astype(np.float32) if ent else np.zeros((0, 2 + len(ex_t)), np.float32),
              "MCreco": np.column_stack([rpt, rpz, *rex]).astype(np.float32) if ent else np.zeros((0, 2 + len(ex_r)), np.float32),
              "pass_reco": np.asarray(pr, bool), "pass_truth": np.asarray(ptr, bool),
              "w_truth": np.asarray(wtl), "w_reco": np.asarray(wrl)}
    return np.asarray(ent, np.int64), arrays


BORDER = 1e-12  # rad: rows this close to the muon-angle cut are decided by the reference function itself


def kept_walk_np(c: dict, ex_t: list, ex_r: list, bounds: tuple, pot_scale: float, in_ps, theta_max: float
                 ) -> tuple[np.ndarray, dict]:
    """kept_walk, vectorized (the director's ruling on z3, 2026-11-12). Every comparison and product is the loop's on
    the same float64 values; the one transcendental step, the muon-angle cut atan2(pt, pz) < theta_max, is taken with
    numpy and then re-decided by in_ps itself on every row within BORDER of the cut, so the kept set cannot differ
    from the loop's by a last-bit atan2 difference. kept_walk stays the reference; a test requires bitwise equality."""
    pt_lo, pt_hi, pz_lo, pz_hi = bounds
    f64 = lambda k: np.asarray(c[k], np.float64)  # noqa: E731
    a_pt, a_pz, b_pt, b_pz = f64("MC"), f64("MC_pz"), f64("sim"), f64("sim_pz")
    wt0, wr0 = f64("w_truth"), f64("w_reco")
    tv = [f64(nm) for nm in ex_t]
    rv = [f64(nm) for nm in ex_r]
    passed = np.asarray(c["sim_pass"]) != 0
    with np.errstate(invalid="ignore"):
        good_w = np.isfinite(wt0) & np.isfinite(wr0) & (wt0 >= 0) & (wt0 < 1e4) & (wr0 >= 0) & (wr0 < 1e4)
        t_fin = np.isfinite(a_pt) & np.isfinite(a_pz)
        for v in tv:
            t_fin &= np.isfinite(v)
        box_t = (pt_lo <= a_pt) & (a_pt <= pt_hi) & (pz_lo <= a_pz) & (a_pz <= pz_hi)
        ang = np.arctan2(a_pt, a_pz)
        tru = t_fin & box_t & (ang < theta_max)
        border = np.flatnonzero(t_fin & box_t & (np.abs(ang - theta_max) <= BORDER))
        for i in border.tolist():
            tru[i] = bool(in_ps(float(a_pt[i]), float(a_pz[i]), pt_lo, pt_hi, pz_lo, pz_hi))
        rec = np.isfinite(b_pt) & np.isfinite(b_pz)
        for v in rv:
            rec &= np.isfinite(v)
        rec &= (pt_lo <= b_pt) & (b_pt <= pt_hi) & (pz_lo <= b_pz) & (b_pz <= pz_hi)
    sel = passed & rec
    keep = good_w & t_fin & (tru | sel)
    ent = np.flatnonzero(keep).astype(np.int64)
    s_k = sel[keep]
    arrays = {"MCgen": np.column_stack([a_pt[keep], a_pz[keep], *[v[keep] for v in tv]]).astype(np.float32),
              "MCreco": np.column_stack([np.where(s_k, b_pt[keep], -9999.0), np.where(s_k, b_pz[keep], -9999.0),
                                         *[np.where(s_k, v[keep], -9999.0) for v in rv]]).astype(np.float32),
              "pass_reco": s_k.astype(bool), "pass_truth": tru[keep].astype(bool),
              "w_truth": wt0[keep] * pot_scale, "w_reco": wr0[keep] * pot_scale}
    return ent, arrays


def check_against_npz(arrays: dict, z) -> None:
    for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco"):
        a, b = np.asarray(arrays[k]), np.asarray(z[k])
        if a.shape != b.shape or a.dtype != b.dtype or not np.array_equal(a, b):
            raise DumpError(f"the replica's {k} is not the written npz's ({a.shape} {a.dtype} vs {b.shape} {b.dtype})")


def playlist_index(runs: np.ndarray, per_playlist_runs: list[np.ndarray]) -> np.ndarray:
    """The position of the playlist whose runs hold each row's run; a run in two playlists or in none refuses."""
    owner: dict[int, int] = {}
    for k, rr in enumerate(per_playlist_runs):
        for r in np.unique(rr).tolist():
            if r in owner:
                raise DumpError(f"run {r} appears in playlists {owner[r]} and {k}")
            owner[int(r)] = k
    out = np.empty(len(runs), np.int64)
    for i, r in enumerate(np.asarray(runs).tolist()):
        if int(r) not in owner:
            raise DumpError(f"row {i}: run {r} is in no per-playlist omnifile")
        out[i] = owner[int(r)]
    return out


def build(omnifile: Path, npz: Path, playlists: list[tuple[str, Path]], sidecar: Path, reader, bounds, pot_scale,
          in_ps, ex_t, ex_r, theta_max: float | None = None) -> dict:
    """theta_max given: the vectorized walk (the dump's path); None: the loop (the reference, as tests use it)."""
    if sidecar.exists():
        raise DumpError(f"refusing to overwrite {sidecar}")
    cols = ["MC", "MC_pz", "sim", "sim_pz", "sim_pass", "w_truth", "w_reco", *ex_t, *ex_r, *TRUTHX, *IDS]
    c = reader(omnifile, "mc_signal_reco", cols)
    if theta_max is None:
        ent, arrays = kept_walk(c, ex_t, ex_r, bounds, pot_scale, in_ps)
    else:
        ent, arrays = kept_walk_np(c, ex_t, ex_r, bounds, pot_scale, in_ps, theta_max)
    with np.load(npz, allow_pickle=True) as z:
        check_against_npz(arrays, z)
    tx = np.column_stack([np.asarray(c[nm], np.float64)[ent] for nm in TRUTHX])
    if not np.all(np.isfinite(tx)):
        raise DumpError("a kept row has a non-finite truthx value")
    ids = np.column_stack([np.asarray(c[nm], np.int64)[ent] for nm in IDS])
    per = [np.asarray(reader(p, "mc_signal_reco", ["truthx_run"])["truthx_run"], np.int64) for _, p in playlists]
    pl = playlist_index(ids[:, 0], per)
    mc_id = np.column_stack([pl, ids]).astype(np.int64)
    meta = {"schema": SCHEMA, "npz": str(npz), "npz_sha256": sha256(npz), "omnifile": str(omnifile),
            "playlists": [[name, str(p)] for name, p in playlists], "pot_scale": pot_scale, "rows": int(len(ent)),
            "truthx_dtype": "float64 (the omnifile's doubles, uncast)", "mc_id_names": list(MC_ID_NAMES),
            "row_check": "replica of collect_signal_nd's kept-row walk equals the npz's MCgen, MCreco, pass_reco, "
                         "pass_truth, w_truth and w_reco bitwise",
            "walk": "loop (reference)" if theta_max is None else "vectorized (kept_walk_np)",
            "code_sha256": {"rdx_dump.py": sha256(Path(__file__).resolve())}}
    np.savez(sidecar, truthx=tx, truthx_names=np.array(TRUTHX), mc_id=mc_id, mc_id_names=np.array(MC_ID_NAMES),
             meta=json.dumps(meta))
    meta["sidecar_sha256"] = sha256(sidecar)
    return meta


def root_reader(path: Path, tree: str, cols: list[str]) -> dict:
    import ROOT
    return {k: np.asarray(v) for k, v in ROOT.RDataFrame(tree, str(path)).AsNumpy(cols).items()}


def parse_playlists(spec: str) -> list[tuple[str, Path]]:
    out = []
    for item in spec.split(","):
        name, _, p = item.partition("=")
        out.append((name, Path(p)))
    if [n for n, _ in out] != list(PLAYLISTS):
        raise DumpError(f"--playlists must name {PLAYLISTS} in that order")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=False)
    ap.add_argument("--playlists", required=True)
    ap.add_argument("--sidecar", type=Path, required=True)
    a, rest = ap.parse_known_args(argv)
    if "--omnifile" not in rest or "--out" not in rest:
        raise DumpError("pass s5p_input_dumps.py lateral's --omnifile and --out")
    omnifile = Path(rest[rest.index("--omnifile") + 1])
    npz = Path(rest[rest.index("--out") + 1])
    playlists = parse_playlists(a.playlists)
    if a.sidecar.exists():
        raise DumpError(f"refusing to overwrite {a.sidecar}")
    import ROOT
    import s5p_input_dumps as D
    rc = D.main(["lateral", *rest])
    if rc != 0:
        raise DumpError(f"s5p_input_dumps.py lateral returned {rc}")
    u2d, und, extras, edges = D.setup()
    f = ROOT.TFile.Open(str(omnifile), "READ")
    _, _, pot_scale = u2d.get_pot_scales(f)
    f.Close()
    bounds = (edges[0][0], edges[0][-1], edges[1][0], edges[1][-1])
    ex_t = [und.EXTRA_AXES[x]["truth"] for x in AXES]
    ex_r = [und.EXTRA_AXES[x]["reco"] for x in AXES]
    meta = build(omnifile, npz, playlists, a.sidecar, root_reader, bounds, pot_scale, u2d.in_truth_phase_space,
                 ex_t, ex_r, theta_max=u2d.MAX_MUON_THETA_RAD)
    print(json.dumps({"sidecar": str(a.sidecar), "sidecar_sha256": meta["sidecar_sha256"], "rows": meta["rows"],
                      "npz_sha256": meta["npz_sha256"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
