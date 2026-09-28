"""Completeness manifest for the UNBLIND amendment (Amendment 2c item 9): every look-1 row of the released FB
manifests that enter decisions is COMPLETE, with its receipt digest. Reads only status files and receipt bytes
(sha256 of the file; no field is parsed), so it opens no final-bank quantity. Exit 1 if any row is not COMPLETE.

    python completeness_manifest.py --root /pscratch/.../pet-final-design-20260925 \
        --manifest s4f_a3:s4f s4f_a3e:s4f s4s_a3:s4s s4s_a3e_n40:s4s --out COMPLETENESS-look1.tsv
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, required=True, help="study area with the stage output dirs")
    ap.add_argument("--manifest", nargs="+", required=True, metavar="STEM:OUTDIR")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    lines = ["# manifest\trow\tstatus\treceipt_sha256"]
    missing = 0
    for spec in a.manifest:
        stem, out = spec.split(":")
        mpath = RUNS / f"{stem}.tsv"
        msha = hashlib.sha256(mpath.read_bytes()).hexdigest()
        lines.append(f"# {stem}.tsv sha256 {msha}")
        for line in mpath.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            name = line.split("\t")[0]
            d = a.root / out / name
            st = (d / "status.txt").read_text().strip() if (d / "status.txt").exists() else "MISSING"
            rc = d / "receipt.json"
            dig = hashlib.sha256(rc.read_bytes()).hexdigest() if rc.exists() else "-"
            if st != "COMPLETE":
                missing += 1
            lines.append(f"{stem}\t{name}\t{st}\t{dig}")
    a.out.write_text("\n".join(lines) + "\n")
    n = sum(1 for x in lines if not x.startswith("#"))
    print(f"{n} rows, {missing} not COMPLETE -> {a.out}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
