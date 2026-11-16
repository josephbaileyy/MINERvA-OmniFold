#!/usr/bin/env python3
"""RDX's connect-side path checks (RDX-DECLARATION.md §3; the director's ruling of 2026-11-12). Python 3.6.

    rdx_paths.py policy --config <policy-config.json> --read PATH [PATH ...]
        refuses (exit 3) if any read path is, or lies under, a cov2d_protected_paths entry of the pinned policy
        config, or RDX's own never-read list (of_inputs_5d.npz and its background dump, the 2D merged CV and $UNI,
        and the LL5D gate input roots cov2d named on 2026-11-12);
    rdx_paths.py atime PATH [PATH ...]
        prints size, mtime and atime (UTC) of each purge-exposed MP-1 input (S0's base_cv.root, S1's zero loops,
        lat_zero.npz and its background dump), by os.stat only, and refuses (exit 3) if one is missing.
    rdx_paths.py stage --dest DIR SRC SHA256 [SRC SHA256 ...]
        copies each source into DIR by os.open(O_RDONLY | O_NOATIME); refuses (exit 3) unless the copy's sha256 is
        the pin and the source's size, mtime and atime are unchanged, and never overwrites;
    rdx_paths.py manifest --root DIR --out FILE
        the sha256 of every file under DIR, each read by O_NOATIME (so a protected file in the tree, such as the NuE
        constraint file under MParamFiles/data, keeps its atime), written as "sha256  relative/path" lines.
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


def noatime_sha(src, dst=None):
    """sha256 and size of src read once by O_NOATIME (copied to dst if given); size, mtime and atime must not move."""
    import hashlib
    s0 = os.stat(src)
    h, n = hashlib.sha256(), 0
    fi = os.open(src, os.O_RDONLY | os.O_NOATIME)
    fo = open(dst, "xb") if dst else None
    try:
        while True:
            b = os.read(fi, 1 << 24)
            if not b:
                break
            h.update(b)
            n += len(b)
            if fo:
                fo.write(b)
    finally:
        os.close(fi)
        if fo:
            fo.close()
    s1 = os.stat(src)
    if (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) != (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns) or n != s0.st_size:
        raise ValueError("%s: size, mtime or atime moved, or %d bytes read of %d" % (src, n, s0.st_size))
    return h.hexdigest(), n


def stage(dest, pairs):
    os.makedirs(dest, exist_ok=True)
    rows = []
    for src, pin in pairs:
        dst = os.path.join(dest, os.path.basename(src))
        if os.path.exists(dst):
            raise ValueError("refusing to overwrite %s" % dst)
        sha, n = noatime_sha(src, dst)
        if sha != pin:
            os.remove(dst)
            return {"staged": rows, "failed": {"src": src, "sha256": sha, "pin": pin}, "verdict": "REFUSED"}
        os.chmod(dst, 0o444)
        rows.append({"src": src, "dst": dst, "bytes": n, "sha256": sha})
    return {"staged": rows, "verdict": "STAGED"}


def manifest(root, out):
    if os.path.exists(out):
        raise ValueError("refusing to overwrite %s" % out)
    lines = []
    for d, _, files in sorted(os.walk(root)):
        for f in sorted(files):
            p = os.path.join(d, f)
            if os.path.isfile(p) and not os.path.islink(p):
                lines.append("%s  %s" % (noatime_sha(p)[0], os.path.relpath(p, root)))
    with open(out, "x") as fh:
        fh.write("\n".join(lines) + "\n")
    return {"root": root, "files": len(lines), "out": out, "verdict": "PRESENT"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("policy")
    p.add_argument("--config", required=True)
    p.add_argument("--read", nargs="+", required=True)
    t = sub.add_parser("atime")
    t.add_argument("paths", nargs="+")
    g = sub.add_parser("stage")
    g.add_argument("--dest", required=True)
    g.add_argument("pairs", nargs="+")
    m = sub.add_parser("manifest")
    m.add_argument("--root", required=True)
    m.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "policy":
            rec = policy(a.config, a.read)
        elif a.cmd == "atime":
            rec = atime(a.paths)
        elif a.cmd == "stage":
            if len(a.pairs) % 2:
                raise ValueError("stage takes SRC SHA256 pairs")
            rec = stage(a.dest, list(zip(a.pairs[0::2], a.pairs[1::2])))
        else:
            rec = manifest(a.root, a.out)
    except (OSError, ValueError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(rec, indent=1))
    return 0 if rec["verdict"] in ("CLEAR", "PRESENT", "STAGED") else 3


if __name__ == "__main__":
    sys.exit(main())
