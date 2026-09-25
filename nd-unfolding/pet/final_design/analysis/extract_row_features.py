"""Extract the per-row simulation features of a few run directories into one small `.npz`.

`row_features.npz` (`../diagnostics/build_row_features.py`) holds every inventory row (49,152,885;
1.2 GB). The scorer needs only the prior and pseudodata rows of the runs it scores, so this writes
`rows` (sorted, unique inventory row indices) plus the requested columns at those rows. The
scorer (`score_design.RowFeatures`) accepts either the full file (indexed by row) or such an
extract (looked up by `rows`, refusing a row that is absent).

    python extract_row_features.py --row-features row_features.npz --runs RUN [RUN ...] --out x.npz
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

DEFAULT_COLUMNS = ("tr_n_p", "tr_n_n", "tr_n_pipm", "tr_n_pi0", "tr_n_other", "tr_n_valid",
                   "rc_n_valid", "rc_E_sum")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--row-features", type=Path, required=True)
    ap.add_argument("--runs", nargs="+", type=Path, required=True)
    ap.add_argument("--columns", nargs="+", default=list(DEFAULT_COLUMNS))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    rows = []
    for run in a.runs:
        with np.load(run / "replicate_arrays.npz") as A:
            rows += [A["prior_rows"], A["pseudo_rows"]]
    rows = np.unique(np.concatenate(rows).astype(np.int64))
    src = np.load(a.row_features, mmap_mode="r")
    out = {"rows": rows}
    for c in a.columns:
        out[c] = np.asarray(src[c][rows])
    np.savez(a.out, **out)
    receipt = {"source": str(a.row_features), "runs": [str(r) for r in a.runs],
               "rows": int(rows.size), "columns": a.columns, "output_sha256": sha256(a.out)}
    a.out.with_suffix(".receipt.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
