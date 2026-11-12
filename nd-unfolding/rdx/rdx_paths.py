#!/usr/bin/env python3
"""RDX's connect-side path checks (RDX-DECLARATION.md §3; the director's ruling of 2026-11-12). Python 3.6.

    rdx_paths.py policy --config <policy-config.json> --read PATH [PATH ...]
        refuses (exit 3) if any read path is, or lies under, a cov2d_protected_paths entry of the pinned policy
        config, or RDX's own never-read list (of_inputs_5d.npz and its background dump, the 2D merged CV and $UNI,
        and the LL5D gate input roots cov2d named on 2026-11-12);
    rdx_paths.py atime PATH [PATH ...]
        prints size, mtime and atime (UTC) of each purge-exposed MP-1 input (S0's base_cv.root, S1's zero loops,
        lat_zero.npz and its background dump), by os.stat only, and refuses (exit 3) if one is missing.
Exit 0 clear, 3 refused, 2 unusable input.
"""
import argparse
import json
import os
import sys
import time

NEVER_READ = (
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
    "/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz",
    "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root",
    "/pscratch/sd/j/josephrb/cov2d-inputs-20261104",
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root",
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware",
    "/pscratch/sd/j/josephrb/fd-f1-20261027/f1b3/prep",
    "/pscratch/sd/j/josephrb/fd-1b-inv-20261101/i0/in",
)


def under(path, root):
    p, r = os.path.normpath(path), os.path.normpath(root)
    return p == r or p.startswith(r.rstrip("/") + "/")


def policy(config_path, reads):
    with open(config_path) as fh:
        cfg = json.load(fh)
    protected = list(cfg.get("cov2d_protected_paths") or [])
    if not protected:
        raise ValueError("the policy config has no cov2d_protected_paths")
    hits = []
    for r in reads:
        for root in protected + list(NEVER_READ):
            if under(r, root):
                hits.append({"read": r, "protected": root})
    return {"protected": protected, "never_read": list(NEVER_READ), "reads": list(reads), "hits": hits,
            "verdict": "CLEAR" if not hits else "REFUSED"}


def atime(paths):
    rows, missing = [], []
    for p in paths:
        try:
            st = os.stat(p)
        except OSError:
            missing.append(p)
            continue
        fmt = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))  # noqa: E731
        rows.append({"path": p, "bytes": st.st_size, "mtime": fmt(st.st_mtime), "atime": fmt(st.st_atime)})
    return {"files": rows, "missing": missing, "verdict": "PRESENT" if not missing else "MISSING"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("policy")
    p.add_argument("--config", required=True)
    p.add_argument("--read", nargs="+", required=True)
    t = sub.add_parser("atime")
    t.add_argument("paths", nargs="+")
    a = ap.parse_args(argv)
    try:
        rec = policy(a.config, a.read) if a.cmd == "policy" else atime(a.paths)
    except (OSError, ValueError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(rec, indent=1))
    return 0 if rec["verdict"] in ("CLEAR", "PRESENT") else 3


if __name__ == "__main__":
    sys.exit(main())
