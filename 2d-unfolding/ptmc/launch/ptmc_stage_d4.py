#!/usr/bin/env python3
"""PTMC: stage the D4 baseline products (PTMC-DECLARATION.md section 1), each copied once through O_NOATIME by
REF-C2C1's own copy_noatime under its read_guards, with its sha256 taken in the same pass, into a new directory.

A product whose source is cleanly absent (no directory entry) is recorded as absent. The scorer then decides between
"B unavailable" and STOP (section 3.3). Every product under units/ is optional, so a cleanly absent units/ directory
records each of them as absent; the REF root, read-2/ and read-2/inputs/ (which hold the mandatory products) must exist.
- The mandatory products, the publication (000) and E_R's central (001), must be present.
- A present source that cannot be copied is a failure: exit 5, with no manifest, never an absence. That covers a
  permission or I/O error, a symlink, a non-regular file, a parent directory that is not a real directory, or a file
  that changes between its lstat and its copy (its inode, size or mtime).

  python3 ptmc_stage_d4.py --tree DEPLOY --out NEW_DIR
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

REF = Path("/pscratch/sd/j/josephrb/ref-c2c1-20261106")
N = 200
MANDATORY = ("000_cov_ptpl_minerva_inclusive_6GeV.root", "001_xsec.root")


def products(ref: Path) -> list[tuple[Path, str]]:
    out = [(ref / "units" / "c2_central.npz", "c2_central.npz")]
    out += [(ref / "units" / f"c2_replica_b{b}.npz", f"c2_replica_b{b}.npz") for b in range(1, N + 1)]
    out += [(ref / "read-2" / "inputs" / "000_cov_ptpl_minerva_inclusive_6GeV.root",
             "000_cov_ptpl_minerva_inclusive_6GeV.root")]
    out += [(ref / "read-2" / "inputs" / f"{k:03d}_xsec.root", f"{k:03d}_xsec.root") for k in range(1, N + 2)]
    return out


def main(argv=None, ref: Path = REF) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(a.tree / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1 as C
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    a.out.mkdir(parents=True)
    manifest = {"schema": "ptmc-d4-stage/2", "ref_root": str(ref), "copied": {}, "absent": []}
    # every parent directory on the way is a real directory (a symlinked parent fails; codex r1 #8). units/ holds only
    # optional products: its clean absence (ENOENT) is an absence of each of them (confirm read B13)
    absent_dirs = set()
    for d in (ref, ref / "units", ref / "read-2", ref / "read-2" / "inputs"):
        try:
            if not stat.S_ISDIR(os.lstat(d).st_mode):
                print(f"FAIL: {d} is not a real directory", file=sys.stderr)
                return 5
        except FileNotFoundError as e:
            if d != ref / "units":
                print(f"FAIL: lstat {d}: {e}", file=sys.stderr)
                return 5
            absent_dirs.add(d)
        except OSError as e:
            print(f"FAIL: lstat {d}: {e}", file=sys.stderr)
            return 5

    def ident(st):
        return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, stat.S_IFMT(st.st_mode))
    with C.read_guards(C.PROTECTED, (a.out,), (a.out,)):
        for src, name in products(ref):
            if src.parent in absent_dirs:
                manifest["absent"].append(str(src))
                continue
            try:
                st = os.lstat(src)
            except FileNotFoundError:
                if name in MANDATORY:
                    print(f"FAIL: the mandatory {src} is absent", file=sys.stderr)
                    return 5
                manifest["absent"].append(str(src))
                continue
            except OSError as e:
                print(f"FAIL: lstat {src}: {e}", file=sys.stderr)
                return 5
            if not stat.S_ISREG(st.st_mode):
                print(f"FAIL: {src} is not a regular file", file=sys.stderr)
                return 5
            try:
                digest = C.copy_noatime(src, a.out / name)
                after = os.lstat(src)
            except (OSError, C.GateFailure) as e:
                print(f"FAIL: copy {src}: {e}", file=sys.stderr)
                return 5
            if ident(after) != ident(st) or (a.out / name).stat().st_size != st.st_size:
                print(f"FAIL: {src} changed during its copy", file=sys.stderr)
                return 5
            manifest["copied"][name] = {"src": str(src), "sha256": digest, "bytes": st.st_size}
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"staged {len(manifest['copied'])} products, {len(manifest['absent'])} absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
