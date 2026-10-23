"""IBU-1: consolidate the per-seed products into the K = 5 functional tables (DECLARATION.md §6 evidence).

One compressed npz, float64, holding the reading rule's operands at K = 5 (the primary variant: P ``pur``, N
``fold``; DECLARATION IA-5). For each experiments unit ``<u>``: ``<u>__seeds``, ``<u>__F`` (seeds x 153),
``<u>__f_true`` and, where the product has its OmniFold comparator, ``<u>__f_of`` with ``<u>__of_seeds``. For
each bootstrap unit: ``<u>__F`` (replicas x 153). For each data unit: ``<u>__F`` (153). The secondary variants
and the oracle arrays stay in the products (pinned by SHA256SUMS) and are summarized in ``ibu1_read.json``, to keep
the file under the declared 10 MiB. ``source_sha256sums`` holds the sha256 of the products' SHA256SUMS. The 153
rows are in ``s5c_coverage.reported_functionals`` order, as in every product. Usage:

    python3 consolidate_k5.py --products DIR --sums SHA256SUMS --out k5_tables.npz
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

K = 5
PRIMARY = {"P": "F_pur", "N": "F_fold", "D_P": "F_pur", "D_N": "F_fold"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--sums", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    groups = defaultdict(list)
    for p in a.products.glob("*.npz"):
        m = re.match(r"^(?P<unit>.+?)(_s(?P<seed>\d+))?\.npz$", p.name)
        groups[m["unit"]].append((None if m["seed"] is None else int(m["seed"]), p))
    out = {"source_sha256sums": np.array(hashlib.sha256(a.sums.read_bytes()).hexdigest())}
    for unit, items in sorted(groups.items()):
        items.sort(key=lambda x: -1 if x[0] is None else x[0])
        rows = [np.load(p, allow_pickle=False) for _, p in items]
        ks = [int(k) for k in rows[0]["ks"]]
        i5 = ks.index(K)
        v = PRIMARY[unit] if unit in PRIMARY else PRIMARY[unit[0]]
        if items[0][0] is None:  # bootstrap (replicas, K, F) or data (K, F)
            z = rows[0]
            out[f"{unit}__F"] = z[v][:, i5, :] if z[v].ndim == 3 else z[v][i5]
            continue
        out[f"{unit}__seeds"] = np.array([s for s, _ in items])
        out[f"{unit}__F"] = np.array([z[v][i5] for z in rows])
        out[f"{unit}__f_true"] = np.array([z["f_true"] for z in rows])
        with_of = [(s, z) for (s, _), z in zip(items, rows) if "f_of" in z.files]
        if with_of:
            out[f"{unit}__of_seeds"] = np.array([s for s, _ in with_of])
            out[f"{unit}__f_of"] = np.array([z["f_of"] for _, z in with_of])
    np.savez_compressed(a.out, **out)
    print(json.dumps({"units": len(groups), "arrays": len(out), "bytes": a.out.stat().st_size}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
