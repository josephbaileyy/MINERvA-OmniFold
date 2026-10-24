#!/usr/bin/env python3
"""The H2 reporting definition (state/measurement-scoping/pv-ladder/H2-DEFINITION-DECLARATION.md): s5p's H2 cells with
the low-purity cells merged by a fixed, simulation-only rule (numpy only).

The rule (declaration §1), fixed before this script was first run:
  start  the 32 H2 cells (s5p_stage1_inspect.H2_EDGES), each a box;
  test   a box is low-purity if it is reported (s5p's support rule: expected reco signal and truth-selected weight both
         >= 1000) and its purity is below TAU = 0.1;
  merge  while a low-purity box exists: take the one of lowest purity (ties: lowest first H2 index); among the boxes it
         can join into a box (equal on four axes, complementary on the fifth), take the one whose union has the highest
         purity (ties: lowest axis, then lowest first H2 index); merge them and re-test. A low-purity box with no
         partner is kept and flagged;
  report the reported boxes after the merges, ordered by their lowest H2 index.
Purity, stability and support of a box are additive sums over its cells' reco and truth rows (s5p_stage1_inspect
.mc_properties); they come from a 32 x 32 reco-truth migration matrix of the simulation's rows. Inputs are the MC arrays
of the 5D npz and nothing else: the data arrays (measured, measured_weights) are never loaded, and no unfold product is.

Writes the definition (H2 cell -> reporting cell, the fine-cell map's sha256) with each step of the merge, and checks
that the 32 H2 cells' purity, stability, n_eff and reported flags reproduce s5p's Stage-1 receipt.

MEASURES: simulation response on H2 boxes. CANNOT AUTHORIZE: the definition (Joseph approves the estimand), any claim.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
import s5p_stage1_inspect as s1  # noqa: E402

TAU = 0.1
NPZ_SHA256 = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
MC_KEYS = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco")
N_H2 = 32


def bits(c):
    """The H2 cell's (pt, pz, eavail, q3, W) bin indices; cell = 16 i_pt + 8 i_pz + 4 i_E + 2 i_q3 + i_W."""
    return tuple((c >> (4 - k)) & 1 for k in range(5))


def box_of(cells):
    """The per-axis index sets of a set of H2 cells, or None if the cells are not a full box."""
    b = [sorted({bits(c)[k] for c in cells}) for k in range(5)]
    n = int(np.prod([len(x) for x in b]))
    return tuple(tuple(x) for x in b) if n == len(cells) else None


def joinable(a, b):
    """The axis along which boxes a and b (tuples of per-axis index sets) join into a box, or None."""
    diff = [k for k in range(5) if a[k] != b[k]]
    if len(diff) != 1:
        return None
    k = diff[0]
    return k if not set(a[k]) & set(b[k]) else None


class Stats:
    """Additive simulation sums per H2 cell, and the migration matrix, from which any union's figures follow."""

    def __init__(self, M, reco_all, truth_reco, truth_sel, sw2):
        self.M, self.reco_all, self.truth_reco, self.truth_sel, self.sw2 = M, reco_all, truth_reco, truth_sel, sw2

    def of(self, cells):
        u = np.asarray(sorted(cells))
        same = self.M[np.ix_(u, u)].sum()
        ra, tr, ts, s2 = (float(x[u].sum()) for x in (self.reco_all, self.truth_reco, self.truth_sel, self.sw2))
        return {"purity": same / ra if ra > 0 else 0.0, "stability": same / tr if tr > 0 else 0.0,
                "expected_reco_signal": ra, "truth_selected": ts, "mc_neff_truth": ts * ts / s2 if s2 > 0 else 0.0,
                "reported": bool(ra >= s1.SUPPORT_MIN and ts >= s1.SUPPORT_MIN)}


def stats_from_rows(d):
    cmap, n = s1.coarse_map(s1.H2_EDGES)
    ft, fr = s1.fine_index(d["MCgen"].astype(float)), s1.fine_index(d["MCreco"].astype(float))
    pr, pt = d["pass_reco"].astype(bool), d["pass_truth"].astype(bool)
    wt, wr = d["w_truth"].astype(float), d["w_reco"].astype(float)
    ct = np.where(ft >= 0, cmap[np.maximum(ft, 0)], -1)
    cr = np.where(fr >= 0, cmap[np.maximum(fr, 0)], -1)
    both = pr & pt & (ct >= 0) & (cr >= 0)
    M = np.bincount(ct[both] * n + cr[both], weights=wr[both], minlength=n * n).reshape(n, n)
    return Stats(M, s1.sums(cmap, n, fr, wr, pr), s1.sums(cmap, n, ft, wr, pt & pr), s1.sums(cmap, n, ft, wt, pt),
                 s1.sums(cmap, n, ft, wt * wt, pt))


def merge(stats, tau=TAU):
    """The declared merge, from the 32 single-cell boxes. Returns the final boxes (sorted cell lists) and the steps."""
    boxes = [[c] for c in range(N_H2)]
    steps, flagged = [], []
    while True:
        low = [(stats.of(b)["purity"], b[0], i) for i, b in enumerate(boxes)
               if stats.of(b)["reported"] and stats.of(b)["purity"] < tau and b[0] not in flagged]
        if not low:
            break
        p, _, i = min(low)
        a = boxes[i]
        ba = box_of(a)
        cand = []
        for j, b in enumerate(boxes):
            if j == i:
                continue
            k = joinable(ba, box_of(b))
            if k is not None:
                cand.append((-stats.of(a + b)["purity"], k, b[0], j))
        if not cand:
            flagged.append(a[0])
            steps.append({"box": a, "purity": p, "partner": None})
            continue
        q, k, _, j = min(cand)
        u = sorted(a + boxes[j])
        steps.append({"box": a, "purity": p, "partner": boxes[j], "axis": s1.AXES[k], "union": u, "union_purity": -q})
        boxes = [b for t, b in enumerate(boxes) if t not in (i, j)] + [u]
    return sorted(boxes, key=lambda b: b[0]), steps, flagged


def fine_map(boxes, reported):
    """Fine flat index -> reporting cell (-1 = not reported), and its sha256 as little-endian int32 bytes."""
    cmap, _ = s1.coarse_map(s1.H2_EDGES)
    lut = -np.ones(N_H2, np.int32)
    for r, b in enumerate([b for b in boxes if reported[tuple(b)]]):
        lut[b] = r
    m = lut[cmap].astype("<i4")
    return lut, m, hashlib.sha256(m.tobytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--stage1", type=Path, default=_HERE.parents[1] / "docs/orchestration/state/s5p/stage1/stage1_inspect.json")
    ap.add_argument("--skip-npz-sha256", action="store_true", help="the caller has checked the npz's sha256")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    if not a.skip_npz_sha256 and s1.sha256(a.npz) != NPZ_SHA256:
        raise SystemExit("[FAIL] the 5D npz's sha256 differs")
    z = np.load(a.npz, allow_pickle=True)
    stats = stats_from_rows({k: z[k] for k in MC_KEYS})
    S1 = json.loads(a.stage1.read_text())["mc"]["H2"]
    check = {}
    for key in ("purity", "stability", "mc_neff_truth", "expected_reco_signal", "truth_selected"):
        got = np.array([stats.of([c])[key] for c in range(N_H2)])
        want = np.asarray(S1[key], float)
        check[key] = float(np.max(np.abs(got - want) / np.where(want != 0, np.abs(want), 1.0)))
    rep = [stats.of([c])["reported"] for c in range(N_H2)]
    if rep != list(S1["reported"]) or max(check.values()) > 1e-9:
        raise SystemExit(f"[FAIL] the H2 cells do not reproduce the Stage-1 receipt: {check}")
    boxes, steps, flagged = merge(stats)
    st = {tuple(b): stats.of(b) for b in boxes}
    reported = {k: v["reported"] for k, v in st.items()}
    lut, m, msha = fine_map(boxes, reported)
    out = {"schema": "h2-definition/1", "tau": TAU, "simulation_only": True,
           "inputs": {"npz_sha256": NPZ_SHA256, "npz_keys_read": list(MC_KEYS),
                      "stage1_inspect_sha256": s1.sha256(a.stage1)},
           "code": {"h2_definition.py": s1.sha256(Path(__file__).resolve()),
                    "s5p_stage1_inspect.py": s1.sha256(Path(s1.__file__).resolve())},
           "stage1_reproduction_max_rel": check, "steps": steps, "flagged_no_partner": flagged,
           "reporting_cells": [{"id": int(lut[b[0]]), "h2_cells": b, "box": {s1.AXES[k]: [s1.H2_EDGES[s1.AXES[k]][i]
                                for i in (min(x), max(x) + 1)] for k, x in enumerate(box_of(b))}, **st[tuple(b)]}
                               for b in boxes if reported[tuple(b)]],
           "unreported_boxes": [b for b in boxes if not reported[tuple(b)]],
           "h2_to_reporting_cell": lut.tolist(), "fine_map_sha256_int32le": msha, "n_reporting_cells": int(lut.max() + 1)}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"[h2] Stage-1 reproduction max rel {max(check.values()):.2e}")
    for s in steps:
        print(f"[h2] box {s['box']} purity {s['purity']:.4f} -> "
              + (f"joins {s['partner']} along {s['axis']}: union {s['union']} purity {s['union_purity']:.4f}"
                 if s["partner"] else "no partner (flagged)"))
    for c in out["reporting_cells"]:
        print(f"[h2] R{c['id']:02d} {c['h2_cells']} purity {c['purity']:.3f} stability {c['stability']:.3f} "
              f"n_eff {c['mc_neff_truth']:.0f}")
    print(f"[h2] {out['n_reporting_cells']} reporting cells; unreported boxes {out['unreported_boxes']}; "
          f"fine map sha256 {msha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
