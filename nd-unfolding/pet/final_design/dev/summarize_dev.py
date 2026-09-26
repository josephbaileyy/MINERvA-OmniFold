"""Development-stage table (DEV bank) from post-hoc JSONs, for DEVELOPMENT-*.md. Development evidence.

Reads `<run>.posthoc.json` (diagnostics/posthoc_iterations.py) for the predecessor's FINAL/STRESS
runs and the study's development stages, groups by (candidate, case) over the predecessor-drawn
selections (F0-F11 development tilt; T0-T1 stress cases), and reports per iteration k:

* `E0`/case `R`  -- E_avail recovery against the replicate's own pseudodata truth (the predecessor
  scorer's quantity; the analyzer asserts it reproduces each run's scores.json to 1e-9);
* `D4c topo`     -- joint E_avail x truncated-cloud proton class recovery against the oracle;
* `D4d Eres`     -- E_avail residual L1 against the pseudodata truth under the neutron case (the
  protocol's B2 quantity: tolerance = injected L1 + 0.010);
* `D4d topo`     -- joint E_avail x neutron class recovery against the oracle.

    python summarize_dev.py --root <dir with posthoc2/ dev1/ dev2L/ ...> --ks 2,3,4,6 \
        --json out.json --markdown out.md
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

import numpy as np

SOURCES = {  # candidate -> glob template relative to --root ({st} = final|stress, {sel})
    "CTL": "posthoc2/{st}-CTL-{sel}", "C": "posthoc2/{st}-C-{sel}", "B": "posthoc2/{st}-B-{sel}",
    "H1": "dev1/dev1-H1-{sel}", "H2": "dev1/dev1-H2-{sel}", "H2S1": "dev1/dev1-H2S1-{sel}",
    "CS1": "dev1/dev1-CS1-{sel}", "L64H2": "dev2L/dev2L-L64H2-{sel}",
    "L128H2": "dev2L/dev2L-L128H2-{sel}", "L128H2E16": "dev2L/dev2L-L128H2E16-{sel}",
    "L64S1": "dev2S/dev2S-L64S1-{sel}", "L128S1": "dev2S/dev2S-L128S1-{sel}",
    "H2S1E16": "dev2S/dev2S-H2S1E16-{sel}", "L128S1E16": "dev2T/dev2T-L128S1E16-{sel}",
    "P2pre": "dev2P/dev2P-P2pre-{sel}", "P2scr": "dev2P/dev2P-P2scr-{sel}",
}
ROWS = [  # (label, selection glob, path into an iteration record, field)
    ("dev tilt R (F reps)", "F*", ("eavail_vs_pseudodata",), "recovery"),
    ("D1 -0.35 R", "T*-D1_m0.350", ("eavail_vs_pseudodata",), "recovery"),
    ("D1 +0.35 R (T reps)", "T*-D1_p0.350", ("eavail_vs_pseudodata",), "recovery"),
    ("D2 bump R", "T*-D2_bump_c0.3", ("eavail_vs_pseudodata",), "recovery"),
    ("D4c topo (E x p) R", "T*-D4c_p_up", ("push_all", "joint_eavail_p"), "recovery"),
    ("D4c E_avail res L1", "T*-D4c_p_up", ("eavail_vs_pseudodata",), "residual_l1"),
    ("D4d E_avail res L1", "T*-D4d_n_up", ("eavail_vs_pseudodata",), "residual_l1"),
    ("D4d topo (E x n) R", "T*-D4d_n_up", ("push_all", "joint_eavail_n"), "recovery"),
    ("D5 NuWro R", "T*-D5_nuwro", ("eavail_vs_pseudodata",), "recovery"),
    ("R1x1.05 + D1 +0.35 R", "T*-R1_x1.05_D1_p0.350", ("eavail_vs_pseudodata",), "recovery"),
]


def value(d: dict, k: int, path: tuple, field: str) -> float:
    if len(d["iterations"]) < k:
        return math.nan
    r = d["iterations"][k - 1]
    for p in path:
        r = r[p]
    return math.nan if r[field] is None else float(r[field])


def collect(root: Path, ks: list[int]) -> dict:
    out: dict = {}
    for label, sel, path, field in ROWS:
        st = "final" if sel.startswith("F") else "stress"
        for cand, tmpl in SOURCES.items():
            files = sorted(glob.glob(str(root / (tmpl.format(st=st, sel=sel) + ".posthoc.json"))))
            if not files:
                continue
            runs = [json.loads(Path(f).read_text()) for f in files]
            cell = {}
            for k in ks:
                v = np.array([value(d, k, path, field) for d in runs])
                v = v[~np.isnan(v)]
                cell[str(k)] = {"mean": float(v.mean()) if v.size else None, "n": int(v.size),
                                "values": [round(float(x), 6) for x in v],
                                "runs": [d["run"] for d in runs if len(d["iterations"]) >= k]}
            out.setdefault(label, {})[cand] = cell
    return out


def markdown(tab: dict, ks: list[int]) -> str:
    lines = []
    for label, cands in tab.items():
        lines.append(f"\n**{label}**\n")
        lines.append("| candidate | " + " | ".join(f"k = {k}" for k in ks) + " |")
        lines.append("|---|" + "---:|" * len(ks))
        for cand, cell in cands.items():
            cs = []
            for k in ks:
                c = cell[str(k)]
                cs.append("—" if c["mean"] is None else f"{c['mean']:+.3f} ({c['n']})")
            lines.append(f"| {cand} | " + " | ".join(cs) + " |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--ks", default="2,3,4,6")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--markdown", type=Path)
    a = ap.parse_args(argv)
    ks = [int(x) for x in a.ks.split(",")]
    tab = collect(a.root, ks)
    md = markdown(tab, ks)
    if a.json:
        a.json.write_text(json.dumps(tab, indent=1))
    if a.markdown:
        a.markdown.write_text(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
