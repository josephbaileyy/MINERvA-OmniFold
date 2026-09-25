"""Tabulate post-hoc per-iteration diagnostics by (case, estimator, k), mean over replicates.

Reads `<run>.posthoc.json` files written by `posthoc_iterations.py` for predecessor runs named
`<stage>-<est>-<rep>[-<case>]` and prints Markdown tables; `--json` writes the aggregate.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import sys
from pathlib import Path

import numpy as np

ROWS = [  # (label, path into an iteration record)
    ("det reco E_avail", ("step1_detector", "reco_eavail")),
    ("det n clusters", ("step1_detector", "reco_nclusters")),
    ("det cluster E sum", ("step1_detector", "reco_Esum_decile")),
    ("pull sel E_avail", ("pull_selected", "eavail")),
    ("push sel E_avail", ("push_selected", "eavail")),
    ("push miss E_avail", ("push_missed", "eavail")),
    ("push all E_avail", ("push_all", "eavail")),
    ("pull sel p-class", ("pull_selected", "class_p")),
    ("push sel p-class", ("push_selected", "class_p")),
    ("push miss p-class", ("push_missed", "class_p")),
    ("push all p-class", ("push_all", "class_p")),
    ("pull sel n-class", ("pull_selected", "class_n")),
    ("push sel n-class", ("push_selected", "class_n")),
    ("push miss n-class", ("push_missed", "class_n")),
    ("push all n-class", ("push_all", "class_n")),
    ("push all joint E x p", ("push_all", "joint_eavail_p")),
    ("push all joint E x n", ("push_all", "joint_eavail_n")),
    ("push all pi+- class", ("push_all", "class_pipm")),
]


def label(name: str) -> tuple[str, str, str]:
    parts = name.split("-")
    stage, est, rep = parts[0], parts[1], parts[2]
    case = "-".join(parts[3:]) if len(parts) > 3 else "dev"
    return stage, est, case


def get(rec: dict, path: tuple[str, str]) -> dict:
    return rec[path[0]][path[1]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ks", default="1,3,10")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    ks = [int(k) for k in a.ks.split(",")]
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    inj = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted({p for g in a.files for p in glob.glob(g)}):
        d = json.loads(Path(f).read_text())
        stage, est, case = label(d["run"])
        key = (stage if case == "dev" else "stress", case)
        for rec in d["iterations"]:
            if rec["k"] not in ks:
                continue
            for lab, path in ROWS:
                r = get(rec, path)
                agg[key][(est, rec["k"], lab)].append(
                    (r["recovery"], r["residual_l1"], r["injected_l1"]))
        for lab, path in ROWS:
            if path[0].startswith(("push", "pull")):
                inj[key][lab].append(d["oracle_block"][path[1]]["injected_l1"]
                                     if path[1] in d["oracle_block"] else None)
    out = {}
    for key in sorted(agg):
        ests = sorted({e for e, _, _ in agg[key]})
        cols = [(e, k) for e in ests for k in ks if any((e, k, l) in agg[key] for l, _ in ROWS)]
        print(f"\n### {key[0]} / {key[1]}\n")
        print("| quantity | " + " | ".join(f"{e} k={k}" for e, k in cols) + " |")
        print("|---|" + "---:|" * len(cols))
        for lab, _ in ROWS:
            cells = []
            for e, k in cols:
                v = agg[key].get((e, k, lab), [])
                rec_ = [x[0] for x in v if x[0] is not None]
                if rec_:
                    cells.append(f"{np.mean(rec_):+.3f}")
                elif v:
                    cells.append(f"res {np.mean([x[1] for x in v]):.4f}/inj {np.mean([x[2] for x in v]):.4f}")
                else:
                    cells.append("")
                out.setdefault("/".join(key), {}).setdefault(f"{e}@{k}", {})[lab] = {
                    "recovery_mean": float(np.mean(rec_)) if rec_ else None,
                    "recovery_each": rec_,
                    "residual_l1_mean": float(np.mean([x[1] for x in v])) if v else None,
                    "injected_l1_mean": float(np.mean([x[2] for x in v])) if v else None}
            print(f"| {lab} | " + " | ".join(cells) + " |")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
