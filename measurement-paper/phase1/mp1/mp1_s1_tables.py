#!/usr/bin/env python3
"""MP1-A S1: write s5c_array task tables for the lateral dumps or the real-data unfolds of the given endpoints.

The lines repeat W2b's (publication/w2/w2b.py ``tables``) with this namespace's paths:
  dump    s5p_input_dumps.py lateral --omnifile <merged> --cv-npz <CV npz> --out lat_<v>.npz --out-bkg lat_<v>_bkg.npz
  unfold  s5p_numerics.py --npz/--bkg (with their sha256) --config R --iters 5 --construction data --pairs=-:-
          --tag mp1s1_<v> --threads 32 --out <NS>/unf          -> <NS>/unf/mp1s1_<v>_b-_j-.npz
    python3 mp1_s1_tables.py --ns <NS> --stage dump|unfold --variants v1,v2,... --out table.tsv
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

CV_NPZ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
PINS = {"dump": "c1cba7bfb214a82abde5580c72c9ef3c4704e73f", "unfold": "4e4b4f56bb0c4715dcf567829ac0449bfac745de"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ns", required=True)
    ap.add_argument("--stage", choices=("dump", "unfold"), required=True)
    ap.add_argument("--variants", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 2
    ns = a.ns
    lines = [f"# MP1-A S1 {a.stage} tasks (the W2b form); deploy {PINS[a.stage]}"]
    for v in a.variants.split(","):
        if a.stage == "dump":
            merged = Path(f"{ns}/merged/runEventLoopOmniFold_5D_MEFHC_{v}.root")
            if not merged.is_file():
                print(f"no merged omnifile {merged}", file=sys.stderr)
                return 3
            lines.append("\t".join([f"mp1s1_dump_{v}", "s5p_input_dumps.py", "lateral", "--omnifile", str(merged),
                                    "--cv-npz", CV_NPZ, "--out", f"{ns}/lateral/lat_{v}.npz",
                                    "--out-bkg", f"{ns}/lateral/lat_{v}_bkg.npz"]))
        else:
            npz, bkg = Path(f"{ns}/lateral/lat_{v}.npz"), Path(f"{ns}/lateral/lat_{v}_bkg.npz")
            if not (npz.is_file() and bkg.is_file()):
                print(f"no lateral dump for {v}", file=sys.stderr)
                return 3
            lines.append("\t".join([f"mp1s1_unfold_{v}", "s5p_numerics.py", "--npz", str(npz), "--bkg", str(bkg),
                                    "--expect-npz-sha256", sha256(npz), "--expect-bkg-sha256", sha256(bkg),
                                    "--config", "R", "--iters", "5", "--construction", "data", "--pairs=-:-",
                                    "--tag", f"mp1s1_{v}", "--threads", "32", "--out", f"{ns}/unf"]))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(lines) + "\n")
    print(f"{a.out}: {len(lines) - 1} tasks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
