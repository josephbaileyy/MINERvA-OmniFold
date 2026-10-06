"""Print the report's tables from the committed machine-readable results (no hand transcription).

    pgc_tables.py --comparison results/comparison.json --dev results/dev_paired.json
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path

import numpy as np

PET = ("H2S1T24K5", "L128S1T24K4")
NAMES = {"E0": "E0 dev tilt, E_avail", "E1_low_acceptance": "E1 low acceptance",
         "E1_moderate": "E1 moderate", "E1_good": "E1 good", "E3": "E3 opposite tilt",
         "E4": "E4 E_avail × proton class, D4c p up", "E5": "E5 E_avail × q3, D3 +0.35"}


def ci(p):
    return f"{p['mean']:+.3f} [{p['ci95'][0]:.3f}, {p['ci95'][1]:.3f}]"


def endpoints(c):
    print("| endpoint (n) | H2S1T24 K5 | L128S1T24 K4 | GBDT k3 / **k7** / k10 | H2 − GBDT₇ [95 % CI] "
          "(bank bound; PET > GBDT) | L128 − GBDT₇ [95 % CI] (bank bound; PET > GBDT) |")
    print("|---|---|---|---|---|---|")
    for ep, name in NAMES.items():
        r = c["endpoints"][ep]
        s, p = r["summary"], r["paired"]
        n = s["GBDT@k7"]["n"]
        g = " / ".join(f"{s[f'GBDT@k{k}']['mean']:.3f}" for k in (3, 7, 10))
        cells = []
        for d in PET:
            q = p[f"{d} - GBDT@k7"]
            cells.append(f"{ci(q)} ({q['bank_effect_bound']:.3f}; {q['n_pet_higher']}/{q['n']})")
        print(f"| {name} ({n}) | {s['H2S1T24K5']['mean']:.3f} | {s['L128S1T24K4']['mean']:.3f} | {g} | "
              + " | ".join(cells) + " |")
    print()
    print("| endpoint | H2 − GBDT₃ | H2 − GBDT₁₀ | L128 − GBDT₃ | L128 − GBDT₁₀ |")
    print("|---|---|---|---|---|")
    for ep, name in NAMES.items():
        p = c["endpoints"][ep]["paired"]
        print(f"| {name} | " + " | ".join(ci(p[f"{d} - GBDT@k{k}"]) for d in PET for k in (3, 10))
              + " |")


def per_bin(c):
    print("| histogram | method | L1 of mean residual | mean per-draw L1 | Σ MSE ×10⁴ | bias² / spread ×10⁴ |")
    print("|---|---|---|---|---|---|")
    for ep in ("E0", "E4", "E5"):
        for m in ("H2S1T24K5", "L128S1T24K4", "GBDT@k7", "GBDT@k3", "GBDT@k10"):
            v = c["per_bin"][ep]["methods"][m]
            mean, mse = np.array(v["mean_signed_residual"]), np.array(v["mse"])
            b2 = float((mean ** 2).sum())
            print(f"| {ep} ({len(mean)} bins, n={v['n']}) | {m} | {v['l1_of_mean_residual']:.4f} | "
                  f"{v['mean_per_draw_l1']:.4f} | {mse.sum() * 1e4:.2f} | {b2 * 1e4:.2f} / "
                  f"{(mse.sum() - b2) * 1e4:.2f} |")


def rules(c):
    meth = ("H2S1T24K5", "L128S1T24K4", "GBDT@k7", "GBDT@k3", "GBDT@k10")
    r = c["rules"]
    for key in ("B2:D4d_n_down", "B2:null"):
        if key in r:
            print(f"**{key}** ({r[key]['quantity']}):", "; ".join(
                f"{m} {r[key]['summary'][m]['mean']:.4f} [{r[key]['summary'][m]['ci95'][0]:.4f}, "
                f"{r[key]['summary'][m]['ci95'][1]:.4f}]" for m in meth))
            print()
    if "B3" in r:
        print("**B3** null spurious L1 (E_avail; E_avail × proton; floor):", "; ".join(
            f"{m} {v['mean_eavail_spurious_l1']:.4f} / {v['mean_eavail_x_proton_spurious_l1']:.4f}"
            f" / {v['eavail_x_proton_null_floor']:.4f}" for m, v in r["B3"]["methods"].items()))
        print()
    if "B4" in r:
        for case, v in r["B4"]["cases"].items():
            print(f"**B4 E8 {case}**:", "; ".join(
                f"{m} {x['mean']:+.3f} (sd {x['sd']:.3f})" for m, x in v.items()),
                "| paired:", "; ".join(f"{k} {ci(p)}" for k, p in r["B4"]["paired"][case].items()))
        print()
    print("| library case (draws; natural histogram) | H2 mean R (moves away) | L128 | GBDT k7 | GBDT k3 | "
          "GBDT k10 | H2 − GBDT₇ | L128 − GBDT₇ |")
    print("|---|---|---|---|---|---|---|---|")
    tot = {m: [0, 0] for m in meth}
    for case, v in sorted(c["library"].items()):
        if "methods" not in v:
            print(f"| {case} | INCOMPLETE | | | | | | |")
            continue
        cells = []
        for m in meth:
            x = v["methods"][m]
            tot[m][0] += x["n_defined"]
            tot[m][1] += x["n_moves_away"]
            cells.append("undefined" if not x["n_defined"] else
                         f"{x['mean']:.3f} ({x['n_moves_away']}/{x['n_defined']})")
        pp = [ci(v["paired"][f"{d} - GBDT@k7"]) if f"{d} - GBDT@k7" in v["paired"] else "—"
              for d in PET]
        print(f"| {case} ({v['draws']}; {v['natural_histogram']}) | " + " | ".join(cells + pp) + " |")
    print("| **units with R < 0 / defined units** | " + " | ".join(
        f"**{tot[m][1]} / {tot[m][0]}**" for m in meth) + " | | |")
    print()
    print("weights:", json.dumps({m: {k: round(x, 3) if isinstance(x, float) else x
                                      for k, x in v.items()} for m, v in c["weights"].items()}))
    print("incomplete cases:", c["incomplete_cases"])
    print("cost:", c["gbdt_cost"])


def dev(d):
    print("| unit (E_avail injected L1) | E_avail R: H2 / L128 / GBDT k7 (mean ± sd, 3 seeds) | "
          "E_avail × p R: H2 / L128 / GBDT | E_avail × n R: H2 / L128 / GBDT |")
    print("|---|---|---|---|")
    for u in d["units"]:
        g = u["gbdt"]["truth4_species@k7"]
        inj = u["pet"]["H2S1T24"]["eavail_injected_l1"]
        e = (" / ".join(f"{u['pet'][x]['eavail_R']:.3f}" for x in ("H2S1T24", "L128S1T24"))
             + f" / {st.mean(g['eavail_R']):.3f} ± {st.stdev(g['eavail_R']):.3f}")
        if inj < 0.012:
            e = "below 3F: ratio not used"
        jp = (" / ".join(f"{u['pet'][x]['joint_p_R']:.3f}" for x in ("H2S1T24", "L128S1T24"))
              + f" / {st.mean(g['joint_p_R']):.3f}")
        jn = (" / ".join(f"{u['pet'][x]['joint_n_R']:.3f}" for x in ("H2S1T24", "L128S1T24"))
              + f" / {st.mean(g['joint_n_R']):.3f}")
        print(f"| {u['selection']} {u['case']} ({inj:.4f}) | {e} | {jp} | {jn} |")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--comparison", type=Path, required=True)
    ap.add_argument("--dev", type=Path, required=True)
    a = ap.parse_args(argv)
    c = json.loads(a.comparison.read_text())
    endpoints(c)
    print()
    per_bin(c)
    print()
    rules(c)
    print()
    dev(json.loads(a.dev.read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
