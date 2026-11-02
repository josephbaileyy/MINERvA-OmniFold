"""The stop report's section 3 tables, from connect 34's committed n1_attrib.json (descriptive only).
Run from this directory: python3 summarize_attrib.py ../connect34/n1_attrib.json > summarize_attrib.out

The small-CV split at |a_CV| = 0.01 is coverage-5b-audit's choice (review of connect 34, round 2), made after the
attribution was read; it describes the rows and decides nothing."""
import hashlib
import json
import statistics as st
import sys
from pathlib import Path

SPLIT = 0.01
path = Path(sys.argv[1])
raw = path.read_bytes()
r = json.loads(raw)
print(f"source {path.name} sha256 {hashlib.sha256(raw).hexdigest()}")
print(f"bound {r['bound']} n_draws {r['n_draws']} mismatches {r['mismatches']} atime_moved {r['atime']['moved']}")
for k, v in r["arrays"].items():
    d = v["declared"]
    print(f"\n== {k}: all_draws_rows_above {v['all_draws_rows_above']} declared rows_above {d['rows_above']} max {d['max']}")
    print(f"|a_CV|, all non-zero rows: {v['a_cv_abs_all_nonzero_rows']}")
    if not v.get("rows"):
        continue
    print(f"|a_CV|, rows above: {v['a_cv_abs_rows_above']}  rows above with a_CV = 0: {v['rows_above_cv_zero']}")
    for name, sel in (("small-CV (|a_CV| < 0.01)", lambda x: abs(x["a_cv"]) < SPLIT),
                      ("ordinary (|a_CV| >= 0.01)", lambda x: abs(x["a_cv"]) >= SPLIT)):
        rows = [x for x in v["rows"] if sel(x)]
        if not rows:
            print(f"  {name}: 0 rows")
            continue
        w = [x["worst"] for x in rows]
        top = [x["top"][0][1] for x in rows]
        n1 = [x["n_universes_r_gt_1"] for x in rows]
        print(f"  {name}: {len(rows)} rows; worst median {st.median(w):.2f} max {max(w):.2f}; largest r median "
              f"{st.median(top):.2f} max {max(top):.2f}; n(r>1) median {st.median(n1)} range {min(n1)}-{max(n1)}")
    print(f"largest-r band: {v['largest_r_band']}")
    print(f"second-r band: {v['second_r_band']}")
    n_pairs = len({f"{x['top'][0][0].rpartition('_')[0]}+{x['top'][1][0].rpartition('_')[0]}" for x in v["rows"]})
    print(f"top 10 of {n_pairs} pairs: {v['top_pairs']}")
    print(f"worst truth: {v['worst_truth']}")
    big = {b: x for b, x in v["band_max_r_on_rows_above"].items() if x["max"] > 2}
    print(f"bands with R_b > 2 on some row above (max, rows R_b>10, rows R_b>2): "
          f"{ {b: (round(x['max'], 2), x['rows_gt_10'], x['rows_gt_2']) for b, x in big.items()} }")
