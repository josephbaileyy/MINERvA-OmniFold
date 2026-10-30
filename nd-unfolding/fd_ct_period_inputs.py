#!/usr/bin/env python3
"""The cheap tier's 5B inputs (state/measurement-paper/5d-community-20261024/FD-CT-5B-DECLARATION.md): the per-period
5D inputs built from MP-1's zero per-playlist event loops, and the per-period (e) data unfolds on them. Three steps,
each a lane step of the committed tables (fd_f1_lane.py under s5c_array.sh), after the login-node flux staging:

    fd_ct_period_inputs.py stage-flux --out-dir <B>/flux
    fd_ct_period_inputs.py merge  --period P --loops-dir <MP-1 evloop/zero> --flux <B>/flux/runEventLoopMC_<P>.root \
                                  --out <B>/merged/runEventLoopOmniFold_5D_<P>_zero.root
    fd_ct_period_inputs.py check  --period P --merged ... --nn-npz ... --lat-npz ... --lat-bkg ... --flux ... \
                                  --truth-out ... --out <B>/inputs/check_<P>.json [--mp1-lat-npz ... --mp1-lat-bkg ...]
    fd_ct_period_inputs.py unfold --period P --receipt <B>/inputs/check_<P>.json --pairs=-:- --tag 5b_<P> --out <B>/unf/<P>

* ``stage-flux`` (login node, by submit_fd_ct.sh) copies the 2D period unfold's four flux files, committed at
  FLUX_REL, into <B>/flux, each at its pinned digest.
* ``merge``: the period's playlists, in production order (1A ... 1P, as MP-1 and W2b merged them), each required to be
  its pinned MP-1 zero loop, merged by ``2d-unfolding/uq/hadd_universes_full.py`` as MP-1 merged them
  (measurement-paper/phase1/mp1/mp1_s1_pipeline.sh, stage merge), so each period file carries its own POT. ALL is all
  twelve. It refuses (exit 5, the merge removed) unless the merge's data POT is the period flux file's
  DataPOTUsedForFluxWeighting, before any dump reads it, and writes ``<out>.json`` beside the merge.
* Between merge and check the lane runs ``nn_dump_inputs.py --axes eavail,q3,W --mcfile <period flux>`` (the period's
  npz) and ``s5p_input_dumps.py lateral --cv-npz <that npz> --mcfile <period flux>`` (the same npz again, in MP-1's
  lateral form, and its background dump with float64 coordinates, MP-1's form).
* ``check`` refuses (exit 5) unless the inputs hang together: the merge is the one its receipt names; the flux file is
  the period's pinned one; the lateral npz is array for array the nn_dump npz; the background dump names the lateral
  npz; and the merge's data POT is the flux file's DataPOTUsedForFluxWeighting. For ALL it RECORDS, key by key,
  whether the npz and the background arrays are bitwise MP-1's ``lat_zero.npz`` and ``lat_zero_bkg.npz``; the
  control (fd_ct_periods.py control) decides on that record. It then writes the period's MC truth with the unchanged
  ``s5p_mc_truth_pred.py``.
* ``unfold`` runs the unchanged ``s5p_numerics.py`` (config R, 5 iterations, real data, the given pairs) on the
  period's lateral npz and background dump, with the digests its check recorded.

Every step refuses to overwrite (exit 3) and refuses a pinned input with another digest (exit 4).

MEASURES: nothing; it re-expresses committed event-loop outputs and runs the existing unfold. CANNOT AUTHORIZE: any
reading, verdict or covariance; the readout is fd_ct_periods.py's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
DEPLOY = _ND.parent

PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
# the flux-file grouping of the 2D period unfold (state/2d-closeout/period-unfold-20261014/scripts/periods.py)
PERIODS = {"PA": PLAYLISTS[0:6], "PB": PLAYLISTS[6:9], "PC": PLAYLISTS[9:12], "ALL": PLAYLISTS}
# MP-1's zero per-playlist loops, $P/measurement-paper/phase1/mp1/s1/evloop/zero/ (sha256, login37, 2026-10-30)
ZERO_LOOPS = {
    "1A": "2745e38c45a50fa644e32913c6d8bc9763edc96e21b6d058cde4dbee6714c192",
    "1B": "a2b7e413f8ab727577eb70cf00881c9dedfaf3401c18e37c866f6dc296639948",
    "1C": "7985c0f1ae44d99be3bf180748c9553672bc8f107b512310c961d728d9c62d34",
    "1D": "52da8f2245be7f4529d6c24960fa56f3063db5368bf33e7640604d716742797d",
    "1E": "7f9293a6ce7a0aee7e9549b93d86b4d201bb0db9da088bace988403a7a0faea5",
    "1F": "7481c94751a5df774e1c18cd453e92322d789d5568785ed8c026f6ef15778b4e",
    "1G": "259aa1952e7586eb2f301ec7960f3003d4b995f7f59b36b32a68b47a31ca2821",
    "1L": "d2b4dafc61d1756554d1c7ff3085410faaa2266cd14a260175bc0e533fe2030c",
    "1M": "f80bb016e78701dde9faf5faf53d0d906430525abaafa753c1a051e2f860cb45",
    "1N": "9e9875ec37cd3354650d0c27a042389d86408f0ded08389f1c2ff38ca49e219c",
    "1O": "22064448cb42b960e8066882ce6a3dc0fc8a5650eb1fb70f82626222708e6237",
    "1P": "5efe83f95e9822ff0dbf0780668e187d4857fd97aade631ae6ba19bf917123a1",
}
# the 2D period unfold's flux files (its outputs/SHA256SUMS.inputs; build_flux.py, ALL bitwise the production flux
# d40aea69 by its verify_inputs.py), copied from /pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/flux and
# committed at FLUX_REL; stage-flux copies them into <B>/flux
FLUX_REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/flux"
FLUX = {
    "ALL": "e3dc9e63bc8db07ab545cee6d8b227cdaa7f8249c657cc1a60119020dd6a86de",
    "PA": "927f5af214b15935c1093b83c7e703730b8a5993b5e8f43f60a56eb8f07963fe",
    "PB": "c64637d58961c4681f83611ab79f057f741329398cde00df175fac28dad15f0d",
    "PC": "95c45a5f91f1fc356bfde74b463e1a24a70d698d8693a766773a6a37c3bdfafc",
}
# MP-1's zero chain (build_cresp.PRODUCTS["zero"]: unfold, its input npz, its background dump)
MP1_ZERO = {"unfold": "f1d5178a86c1aa417d477d205669b642c66760b7e8e65f98b426e1d9d950d195",
            "lat_npz": "6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f",
            "lat_bkg": "f09727d04521f77ba101a51eb77f6182305baaad8a342dc59b7a3d86cf37ea66"}
NPZ_KEYS = ("axes", "MCgen", "MCreco", "measured", "pass_reco", "pass_truth", "w_truth", "w_reco", "measured_weights",
            "denom_nd", "flux", "data_pot", "n_nucleons", "edges_0", "edges_1", "edges_2", "edges_3", "edges_4", "nedges")
BKG_KEYS = ("bkg_reco", "bkg_w", "bkg_nd")
POT_REL = 1e-12
FLUX_FLAT = 1e-14


class Refuse(Exception):
    def __init__(self, code: int, why: str):
        super().__init__(why)
        self.code = code


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def code_sha() -> dict:
    files = {"fd_ct_period_inputs.py": Path(__file__).resolve(),
             "hadd_universes_full.py": DEPLOY / "2d-unfolding/uq/hadd_universes_full.py",
             "nn_dump_inputs.py": _ND / "nn_dump_inputs.py", "s5p_input_dumps.py": _ND / "s5p_input_dumps.py",
             "s5p_mc_truth_pred.py": _ND / "s5p_mc_truth_pred.py", "s5p_numerics.py": _ND / "s5p_numerics.py"}
    return {k: sha256(p) for k, p in files.items() if p.is_file()}


def fresh(*paths: Path) -> None:
    for p in paths:
        if p.exists():
            raise Refuse(3, f"refusing to overwrite {p}")


def require(path: Path, want: str, what: str) -> str:
    got = sha256(path)
    if got != want:
        raise Refuse(4, f"{what} {path}: sha256 {got} != {want}")
    return got


def write_json(path: Path, obj: dict) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(obj, indent=1) + "\n")
    tmp.replace(path)


# ---------------------------------------------------------------- stage-flux


def run_stage_flux(a) -> int:
    """Copy the four committed period flux files into the run's own directory, each at its pinned digest."""
    dests = {P: a.out_dir / f"runEventLoopMC_{P}.root" for P in FLUX}
    fresh(a.out_dir)
    for P in FLUX:
        require(a.src_dir / dests[P].name, FLUX[P], f"{P} flux source")
    a.out_dir.mkdir(parents=True)
    for P, d in dests.items():
        shutil.copyfile(a.src_dir / d.name, d)
        require(d, FLUX[P], f"{P} flux copy")
        os.chmod(d, 0o440)
    print(json.dumps({"staged": {P: str(d) for P, d in dests.items()}}), flush=True)
    return 0


# ---------------------------------------------------------------- merge


def run_merge(a) -> int:
    receipt = a.out.with_name(a.out.name + ".json")
    partial = a.out.with_name(a.out.name + ".partial")
    fresh(a.out, receipt, partial)
    t0 = time.time()
    inputs = []
    for pl in PERIODS[a.period]:
        p = a.loops_dir / f"runEventLoopOmniFold_5D_{pl}_zero.root"
        inputs.append({"playlist": pl, "path": str(p), "sha256": require(p, ZERO_LOOPS[pl], f"zero loop {pl}")})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(DEPLOY / "2d-unfolding/uq/hadd_universes_full.py"), str(partial),
           *[i["path"] for i in inputs]]
    rc = subprocess.run(cmd).returncode
    if rc != 0 or not partial.is_file():
        partial.unlink(missing_ok=True)
        raise Refuse(6, f"hadd_universes_full.py exited {rc}")
    # the cheap POT check before any dump reads the merge (review L2); check repeats it on the dump
    require(a.flux, FLUX[a.period], f"{a.period} flux file")
    m_pot, f_pot = merged_data_pot(partial), flux_data_pot(a.flux)
    pot_rel = f_pot / m_pot - 1.0
    if abs(pot_rel) > POT_REL:
        partial.unlink()
        raise Refuse(5, f"the merge's dataPOTUsed is not the flux file's DataPOTUsedForFluxWeighting ({pot_rel:.3e})")
    partial.replace(a.out)
    os.chmod(a.out, 0o440)
    write_json(receipt, {"schema": "fd-ct-5b-merge/1", "period": a.period, "playlists": list(PERIODS[a.period]),
                         "flux_weighting_over_merge_data_pot_minus_1": pot_rel,
                         "inputs": inputs, "out": str(a.out), "out_sha256": sha256(a.out),
                         "out_bytes": a.out.stat().st_size, "code_sha256": code_sha(),
                         "seconds": round(time.time() - t0, 1)})
    print(json.dumps({"merged": str(a.out), "period": a.period, "n_inputs": len(inputs)}), flush=True)
    return 0


# ---------------------------------------------------------------- check


def merged_data_pot(path: Path) -> float:
    """The merge's dataPOTUsed, as the dumps read it (unfold_2d_omnifold_unbinned.get_pot_scales)."""
    for p in (str(DEPLOY / "2d-unfolding"), str(_ND)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import ROOT
    import unfold_2d_omnifold_unbinned as u2d

    f = ROOT.TFile.Open(str(path), "READ")
    data_pot, _, _ = u2d.get_pot_scales(f)
    f.Close()
    return float(data_pot)


def flux_data_pot(path: Path) -> float:
    """The flux file's DataPOTUsedForFluxWeighting (2D build_flux.py: the summed data POT of its playlists)."""
    import ROOT

    f = ROOT.TFile.Open(str(path), "READ")
    v = float(f.Get("DataPOTUsedForFluxWeighting").GetVal())
    f.Close()
    return v


def same_array(a, b) -> bool:
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if a.dtype.kind == "f":
        return bool(np.array_equal(a, b, equal_nan=True))
    return bool(np.array_equal(a, b))


def compare(p: Path, q: Path, keys) -> dict:
    """Key by key, whether the two npz files hold the same array (shape, dtype and values), one key at a time."""
    out = {}
    with np.load(p, allow_pickle=True) as x, np.load(q, allow_pickle=True) as y:
        files = (sorted(x.files), sorted(y.files))
        for k in keys:
            out[k] = bool(k in x.files and k in y.files and same_array(x[k], y[k]))
    out["_key_sets_equal"] = files[0] == files[1]
    return out


def run_check(a) -> int:
    fresh(a.out, a.truth_out)
    for d in (a.out.parent, a.truth_out.parent):
        d.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    is_all = a.period == "ALL"
    if is_all != (a.mp1_lat_npz is not None and a.mp1_lat_bkg is not None):
        raise Refuse(2, "--mp1-lat-npz and --mp1-lat-bkg are required for, and only for, ALL")
    mr = json.loads(a.merged.with_name(a.merged.name + ".json").read_text())
    problems = []
    merged_sha = sha256(a.merged)
    if (mr.get("period"), mr.get("out"), mr.get("out_sha256")) != (a.period, str(a.merged), merged_sha):
        problems.append("the merge is not the one its receipt names")
    flux_sha = require(a.flux, FLUX[a.period], f"{a.period} flux file")
    nn_sha, lat_sha, bkg_sha = sha256(a.nn_npz), sha256(a.lat_npz), sha256(a.lat_bkg)
    nn_vs_lat = compare(a.nn_npz, a.lat_npz, NPZ_KEYS)
    if not all(nn_vs_lat.values()):
        problems.append(f"the lateral npz is not the nn_dump npz: {sorted(k for k, v in nn_vs_lat.items() if not v)}")
    with np.load(a.lat_bkg, allow_pickle=False) as b:
        bmeta = json.loads(str(b["meta"]))
        bkg_dtype = str(b["bkg_reco"].dtype)
    if (bmeta.get("npz_sha256"), bmeta.get("omnifile")) != (lat_sha, str(a.merged)):
        problems.append("the background dump does not name this lateral npz and merge")
    with np.load(a.lat_npz, allow_pickle=True) as z:
        npz_pot = float(z["data_pot"])
        flux = np.asarray(z["flux"], float)
    # the integrated flux is one number per period written into every p_T bin; the 2D record's ALL bins differ in the
    # last digit (0.0006243343376851218 / ...219, inputs_verify.json), so constancy is to rounding
    spread = float(np.max(np.abs(flux / flux.mean() - 1.0)))
    m_pot, f_pot = merged_data_pot(a.merged), flux_data_pot(a.flux)
    pot = {"npz_over_merge_minus_1": npz_pot / m_pot - 1.0, "flux_weighting_over_merge_minus_1": f_pot / m_pot - 1.0}
    if abs(pot["npz_over_merge_minus_1"]) > POT_REL or abs(pot["flux_weighting_over_merge_minus_1"]) > POT_REL:
        problems.append(f"data POT: {pot}")
    if problems:
        raise Refuse(5, "; ".join(problems))
    rec = {"schema": "fd-ct-5b-inputs/1", "period": a.period, "playlists": list(PERIODS[a.period]),
           "files": {"merged": [str(a.merged), merged_sha], "flux": [str(a.flux), flux_sha],
                     "nn_npz": [str(a.nn_npz), nn_sha], "lat_npz": [str(a.lat_npz), lat_sha],
                     "lat_bkg": [str(a.lat_bkg), bkg_sha]},
           "nn_npz_equals_lat_npz": nn_vs_lat, "nn_npz_bytes_equal_lat_npz": nn_sha == lat_sha,
           "bkg_reco_dtype": bkg_dtype, "data_pot_checks": pot, "pot_rel_tolerance": POT_REL,
           "flux_rel_spread_over_pt": spread, "flux_constant_over_pt": bool(spread <= FLUX_FLAT),
           "data_pot": npz_pot}
    if is_all:
        require(a.mp1_lat_npz, MP1_ZERO["lat_npz"], "MP-1 lat_zero.npz")
        require(a.mp1_lat_bkg, MP1_ZERO["lat_bkg"], "MP-1 lat_zero_bkg.npz")
        rec["all_vs_mp1_zero"] = {"lat_npz": compare(a.lat_npz, a.mp1_lat_npz, NPZ_KEYS),
                                  "lat_bkg": compare(a.lat_bkg, a.mp1_lat_bkg, BKG_KEYS),
                                  "lat_npz_bytes_equal": lat_sha == MP1_ZERO["lat_npz"],
                                  "mp1_sha256": {"lat_npz": MP1_ZERO["lat_npz"], "lat_bkg": MP1_ZERO["lat_bkg"]}}
    rc = subprocess.run([sys.executable, str(_ND / "s5p_mc_truth_pred.py"), "--npz", str(a.lat_npz),
                         "--expect-npz-sha256", lat_sha, "--out", str(a.truth_out)]).returncode
    if rc != 0 or not a.truth_out.is_file():
        raise Refuse(6, f"s5p_mc_truth_pred.py exited {rc}")
    rec["files"]["truth"] = [str(a.truth_out), sha256(a.truth_out)]
    rec.update({"code_sha256": code_sha(), "seconds": round(time.time() - t0, 1)})
    write_json(a.out, rec)
    print(json.dumps({"checked": a.period, "receipt": str(a.out)}), flush=True)
    return 0


# ---------------------------------------------------------------- unfold


def unfold_products(out: Path, tag: str, pairs: str) -> list[Path]:
    """The products s5p_numerics.py writes for these pairs, by its own naming."""
    if str(_ND) not in sys.path:
        sys.path.insert(0, str(_ND))
    import s5p_numerics

    return [out / s5p_numerics.product_name(tag, b, j) for b, j in s5p_numerics.parse_pairs(pairs)]


def run_unfold(a) -> int:
    # s5p_numerics skips an existing product and exits 0; here an existing product refuses, so there is no resume
    targets = unfold_products(a.out, a.tag, a.pairs)
    fresh(*targets)
    rec = json.loads(a.receipt.read_text())
    if (rec.get("schema"), rec.get("period")) != ("fd-ct-5b-inputs/1", a.period):
        raise Refuse(4, f"{a.receipt} is not the {a.period} check receipt")
    lat, lat_sha = rec["files"]["lat_npz"]
    bkg, bkg_sha = rec["files"]["lat_bkg"]
    require(Path(lat), lat_sha, f"{a.period} lateral npz")
    require(Path(bkg), bkg_sha, f"{a.period} background dump")
    cmd = [sys.executable, str(_ND / "s5p_numerics.py"), "--npz", lat, "--bkg", bkg, "--expect-npz-sha256", lat_sha,
           "--expect-bkg-sha256", bkg_sha, "--config", "R", "--iters", "5", "--construction", "data",
           f"--pairs={a.pairs}", "--estimator-seed", str(a.estimator_seed), "--tag", a.tag, "--threads",
           str(a.threads), "--out", str(a.out)]
    rc = subprocess.run(cmd).returncode
    missing = [str(p) for p in targets if not p.is_file()]
    if rc == 0 and missing:
        raise Refuse(6, f"s5p_numerics.py exited 0 without {missing}")
    return rc


# ---------------------------------------------------------------- main


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage-flux")
    s.add_argument("--src-dir", type=Path, default=DEPLOY / FLUX_REL)
    s.add_argument("--out-dir", type=Path, required=True)
    m = sub.add_parser("merge")
    m.add_argument("--period", choices=sorted(PERIODS), required=True)
    m.add_argument("--loops-dir", type=Path, required=True)
    m.add_argument("--flux", type=Path, required=True)
    m.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("check")
    c.add_argument("--period", choices=sorted(PERIODS), required=True)
    for k in ("merged", "nn-npz", "lat-npz", "lat-bkg", "flux", "truth-out", "out"):
        c.add_argument(f"--{k}", type=Path, required=True)
    c.add_argument("--mp1-lat-npz", type=Path, default=None)
    c.add_argument("--mp1-lat-bkg", type=Path, default=None)
    u = sub.add_parser("unfold")
    u.add_argument("--period", choices=sorted(PERIODS), required=True)
    u.add_argument("--receipt", type=Path, required=True)
    u.add_argument("--pairs", required=True)
    u.add_argument("--estimator-seed", type=int, default=42)
    u.add_argument("--tag", required=True)
    u.add_argument("--threads", type=int, default=32)
    u.add_argument("--out", type=Path, required=True)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    try:
        return {"stage-flux": run_stage_flux, "merge": run_merge, "check": run_check, "unfold": run_unfold}[a.cmd](a)
    except Refuse as e:
        print(f"[5b-inputs] refusing: {e}", file=sys.stderr, flush=True)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
