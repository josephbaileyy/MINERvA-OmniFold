#!/usr/bin/env python3
"""The "about fifteen-fold" of paper Sec. III: purity-method vs negative-weight nominal-truth bias, highest-W cells.

PRD release audit ea939701 (M03): the factor is stated in OUTCOME-20260925-s5n-stage1-development-fail.md:8 but no
receipt computes it. This re-reads the two committed receipts and prints the per-cell ratio
|purity mean_rel_pct| / |negweight mean_rel_pct| for every highest-W cell present in both. MEASURES: nothing new.

  python3 negweight_bias_ratio.py
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PURITY = ROOT / "docs/orchestration/state/s5c/d1/d1_summary.json"        # VL149, split_F2 worst cells
NEGW = ROOT / "docs/orchestration/state/s5n/stage1/dev_receipt.json"      # VL151, grid.C3_nominal.high_W


def main() -> int:
    pur = {c["name"]: c["mean_rel_pct"] for c in json.loads(PURITY.read_text())["groups"]["split_F2"]["worst"]}
    neg = {k: v["mean_rel_pct"] for k, v in json.loads(NEGW.read_text())["grid"]["C3_nominal"]["high_W"].items()}
    cells = sorted(set(pur) & set(neg), key=lambda s: int(s[2:]))
    ratios = {c: abs(pur[c]) / abs(neg[c]) for c in cells}
    for c in cells:
        print(f"{c}: purity {pur[c]:+.3f}%  negweight {neg[c]:+.3f}%  ratio {ratios[c]:.1f}")
    r = list(ratios.values())
    print(f"cells {len(r)}; ratio min {min(r):.1f}, median {statistics.median(r):.1f}, max {max(r):.1f}; "
          f"max|purity|/max|negweight| = {max(map(abs, (pur[c] for c in cells))) / max(map(abs, (neg[c] for c in cells))):.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
