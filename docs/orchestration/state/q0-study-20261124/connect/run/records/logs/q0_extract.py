#!/usr/bin/env python3
"""The q0 study's extract (PLAN.md section 2), once, on a Perlmutter login node under the director's GO for its sha.

From the 5D CV omnifile's `mc_signal_reco` tree ONLY (the `data` tree and every "measured" key are never opened), for
the rows with sim_pass true: the reco muon (pT, p||), E_avail, q3 and W, the CV weight w_reco, truth q3 and W, and q0
recovered in float64 from (pT, p||, reco q3) by inverting RecoQ3 (CVUniverse.h:208-219), exactly as M4-W did
(m4-w/probe_omni.py:62-77; M4-W-RECORD.md:104). Every read is O_NOATIME; the file's atime is checked before and after.

STOPs (no npz written): the omnifile's sha256 is not the pin (rc 3); a named branch is missing (rc 3); the passing count
is not 20,498,013 (rc 3); the omnifile's atime changed (rc 4); the recovery control fails, max |W - W(q0)| > 1e-6 GeV over
rows with q0_status 0 and W^2 >= 0 (rc 5). A refused precondition (output exists, no O_NOATIME) is rc 9.

    q0_extract.py --omni FILE --out DIR        (DIR must exist and be empty; writes q0_extract.npz and q0_extract.json)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np

OMNI_SHA = "b6d2651cfdbc52790cc7ed6032f2062a3e0ea50c12d63725beba29098dd5175a"   # s5c/contract.json cv_omnifile
TREE = "mc_signal_reco"
BRANCHES = ["sim", "sim_pz", "sim_eavail", "sim_q3", "sim_W", "sim_pass", "w_reco", "MC", "MC_pz", "MC_q3", "MC_W"]
EXPECTED_PASS = 20498013          # step0-treecheck-transcript.txt:9; M4-W-RECORD.md:108
M_N, M_P = 939.56536, 938.272013  # MeV, m4-w/common.py:4-5
M_BAR = (1.5 * M_N + M_P) / 2.5   # m4-w/common.py:6
M_MU = 105.6583                   # MeV, MinervaUnits::M_mu (m4-w/common.py:7)
RECOVERY_TOL_GEV = 1e-6
NOATIME = getattr(os, "O_NOATIME", None)
ALLOW_PLAIN_READ = False          # tests only (macOS has no O_NOATIME); the node run never sets it


class Stop(Exception):
    def __init__(self, rc: int, msg: str):
        super().__init__(msg)
        self.rc = rc


def flags() -> int:
    if NOATIME is None:
        if ALLOW_PLAIN_READ:
            return os.O_RDONLY
        raise Stop(9, "O_NOATIME is not available here")
    return os.O_RDONLY | NOATIME


def sha256_noatime(path: str) -> str:
    h = hashlib.sha256()
    fd = os.open(path, flags())
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                return h.hexdigest()
            h.update(b)
    finally:
        os.close(fd)


def recover_q0(pt, pz, q3):
    """q0 (MeV) from reco (pT, p||, q3) in MeV, inverting RecoQ3; returns (q0, status) with status 0 recovered,
    1 RecoQ3's Q^2 clamp fired (so q3 = q0, and q0 := q3), 2 a non-finite input or output (probe_omni.py:68-75)."""
    pt, pz, q3 = (np.asarray(a, np.float64) for a in (pt, pz, q3))
    emu = np.sqrt(pt * pt + pz * pz + M_MU ** 2)
    a = emu - pz
    c = 2.0 * emu * a - M_MU ** 2
    with np.errstate(invalid="ignore"):
        q0 = -a + np.sqrt(a * a - c + q3 * q3)
        Q2 = 2.0 * (emu + q0) * a - M_MU ** 2
    clamp = ~(Q2 >= 0)
    q0 = np.where(clamp, q3, q0)
    status = np.where(clamp, 1, 0).astype(np.int8)
    bad = ~(np.isfinite(pt) & np.isfinite(pz) & np.isfinite(q3) & np.isfinite(q0))
    status[bad] = 2
    return q0, status


def w_from_q0(q0, q3):
    """Reco W (MeV) from q0 and q3 (probe_omni.py:76-77): sqrt(max(0, (M_bar + q0)^2 - q3^2)); also W^2 < 0."""
    w2 = (M_BAR + q0) ** 2 - q3 * q3
    return np.sqrt(np.maximum(w2, 0.0)), w2 < 0


def in_truth_ps(pt, pz):
    """probe_omni.py:13-14 (u2d.in_truth_phase_space), GeV, inclusive bounds, atan2 < 20 deg."""
    with np.errstate(invalid="ignore"):
        return (pt >= 0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60) & (np.arctan2(pt, pz) < np.radians(20.0))


def extract(omni: str, out: Path, expected_pass: int = EXPECTED_PASS, omni_sha: str = OMNI_SHA) -> dict:
    import uproot
    rec = {"schema": "q0-extract/1", "host": os.uname().nodename, "start_utc": time.strftime("%FT%TZ", time.gmtime()),
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "omni": omni, "tree": TREE,
           "python": sys.version.split()[0], "numpy": np.__version__, "uproot": uproot.__version__}
    st0 = os.stat(omni)
    rec["omni_stat_before"] = {"size": st0.st_size, "atime_ns": st0.st_atime_ns, "mtime_ns": st0.st_mtime_ns}
    got = sha256_noatime(omni)
    rec["omni_sha256"] = got
    if got != omni_sha:
        raise Stop(3, f"omnifile sha256 {got} is not the pin {omni_sha}")
    with os.fdopen(os.open(omni, flags()), "rb") as fh:
        f = uproot.open(fh, object_cache=None, array_cache=None)
        t = f[TREE]
        have = set(t.keys())
        missing = [b for b in BRANCHES if b not in have]
        if missing:
            raise Stop(3, f"branches missing from {TREE}: {missing}")
        a = t.arrays(BRANCHES, library="np")
    st1 = os.stat(omni)
    rec["omni_stat_after"] = {"size": st1.st_size, "atime_ns": st1.st_atime_ns, "mtime_ns": st1.st_mtime_ns}
    if st1.st_atime_ns != st0.st_atime_ns:
        raise Stop(4, "the omnifile's atime changed")
    rec["n_entries"] = int(a["sim_pass"].size)
    sel = np.asarray(a["sim_pass"]) != 0
    rec["n_pass"] = int(sel.sum())
    if rec["n_pass"] != expected_pass:
        raise Stop(3, f"passing rows {rec['n_pass']} != {expected_pass}")
    col = {k: np.asarray(a[k], np.float64)[sel] for k in BRANCHES if k != "sim_pass"}
    del a
    pt, pz, q3, W = (col[k] * 1000.0 for k in ("sim", "sim_pz", "sim_q3", "sim_W"))   # MeV
    q0, status = recover_q0(pt, pz, q3)
    Wq0, w2neg = w_from_q0(q0, q3)
    ctl = (status == 0) & ~w2neg & np.isfinite(W)
    resid = np.abs(W[ctl] - Wq0[ctl]) / 1000.0                     # GeV
    rec["recovery_control"] = {"rows": int(ctl.sum()), "max_abs_resid_GeV": float(resid.max()) if resid.size else None,
                               "tol_GeV": RECOVERY_TOL_GEV, "n_W2_negative": int(w2neg.sum())}
    if not resid.size or float(resid.max()) > RECOVERY_TOL_GEV:
        raise Stop(5, f"recovery control failed: {rec['recovery_control']}")
    rec["q0_status_counts"] = {str(k): int((status == k).sum()) for k in (0, 1, 2)}
    rec["n_q0_le_0"] = int((q0 <= 0).sum())
    cols = {"pt": col["sim"], "pz": col["sim_pz"], "eavail": col["sim_eavail"], "q3": col["sim_q3"], "W": col["sim_W"],
            "q0": q0 / 1000.0, "w_reco": col["w_reco"], "q3_true": col["MC_q3"], "W_true": col["MC_W"]}
    arrays = {k: np.asarray(v, np.float32) for k, v in cols.items()}
    arrays["q0_status"] = status
    arrays["in_truth_ps"] = in_truth_ps(col["MC"], col["MC_pz"]).astype(np.int8)
    npz = out / "q0_extract.npz"
    np.savez(npz, **arrays)
    rec["npz_sha256"] = hashlib.sha256(npz.read_bytes()).hexdigest()
    rec["npz_bytes"] = npz.stat().st_size
    rec["columns"] = {k: str(v.dtype) for k, v in arrays.items()}
    rec["peak_rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1024 if sys.platform != "darwin" else 1))
    rec["end_utc"] = time.strftime("%FT%TZ", time.gmtime())
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--omni", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if not args.out.is_dir() or any(args.out.iterdir()):
        print(f"REFUSED: {args.out} is not an existing empty directory", file=sys.stderr)
        return 9
    try:
        rec = extract(args.omni, args.out)
    except Stop as e:
        print(f"STOP rc {e.rc}: {e}", file=sys.stderr)
        for p in (args.out / "q0_extract.npz",):
            if p.exists():
                p.unlink()
        return e.rc
    (args.out / "q0_extract.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("n_pass", "q0_status_counts", "recovery_control", "npz_sha256", "npz_bytes")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
