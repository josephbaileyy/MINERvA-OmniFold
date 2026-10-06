"""Print the report's tables from the committed results (no hand transcription).

    python gd_tables.py --diagnosis results/diagnosis.json --gbdt results/gbdt_reproduction.json
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path

CASES = ("dev", "D5_nuwro", "D5p_nuwro", "D5_gibuu")
LABEL = {"dev": "dev tilt", "D5_nuwro": "NuWro", "D5p_nuwro": "NuWro′", "D5_gibuu": "GiBUU"}
FIN = ("H2S1T24K5", "L128S1T24K4")
K_PET = {"H2S1T24K5": 5, "L128S1T24K4": 4}


def ms(vals, nd=3):
    v = [x for x in vals if x is not None]
    if not v:
        return "—"
    return f"{st.fmean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"


def f(s, nd=3):
    return "—" if not s else (f"{s['mean']:.{nd}f} ± {s['sd']:.{nd}f}" if s.get("sd") is not None else f"{s['mean']:.{nd}f}")


def gb(units, case):
    return [u for u in units if u["unit"].startswith(case + "|") and u["control_c_c"]["pass"]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--diagnosis", type=Path, required=True)
    ap.add_argument("--gbdt", type=Path, required=True)
    a = ap.parse_args(argv)
    D = json.loads(a.diagnosis.read_text())
    S = D["summary"]
    G = json.loads(a.gbdt.read_text())["units"]
    print(f"Controls: PET runs excluded {D['excluded']}; GBDT units failing C-c "
          f"{[u['unit'] for u in G if not u['control_c_c']['pass']]}; GBDT max |dR| "
          f"{max(u['control_c_c']['max_abs_diff'] for u in G):.1e}\n")

    print("### T1. E_avail recovery and movement fraction m (mean ± sd over 8 draws)\n")
    print("| case | oracle R | H2 R | L128 R | GBDT k7 R | m oracle | m H2 | m L128 | m GBDT k7 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in CASES:
        h, l = S[f"H2S1T24K5|{c}"], S[f"L128S1T24K4|{c}"]
        print(f"| {LABEL[c]} | {f(h['oracle_R'])} | {f(h['pet_R_K'])} | {f(l['pet_R_K'])} | {f(h['gbdt_R_k7'])} | "
              f"{f(h['Q1_m']['oracle'])} | {f(h['Q1_m']['pet'])} | {f(l['Q1_m']['pet'])} | {f(h['Q1_m']['gbdt_k7'])} |")

    print("\n### T2. E_avail recovery by acceptance region\n")
    print("| case | region | H2 | L128 | GBDT k7 |")
    print("|---|---|---|---|---|")
    for c in CASES:
        for rg in ("low_acceptance", "moderate", "good"):
            h, l = S[f"H2S1T24K5|{c}"]["Q1_region_R"][rg], S[f"L128S1T24K4|{c}"]["Q1_region_R"][rg]
            print(f"| {LABEL[c]} | {rg} | {f(h['pet'])} | {f(l['pet'])} | {f(h['gbdt_k7'])} |")

    print("\n### T3. Step decomposition at the operating point (PET at K; GBDT at k = 7)\n")
    print("| case | method | detector-level R (reco E_avail, step 1) | truth-space R, reco-passing rows (step 1) "
          "| final R, all truth-passing rows (step 2) | weight slope (log push on log oracle) |")
    print("|---|---|---|---|---|---|")
    for c in CASES:
        for d in FIN:
            q = S[f"{d}|{c}"]["Q3"][str(K_PET[d])]
            print(f"| {LABEL[c]} | {d[:-2]} K{K_PET[d]} | {f(q['step1_reco_R'])} | {f(q['step1_truth_R'])} | "
                  f"{f(q['step2_R'])} | {f(q['step2_slope'])} |")
        u = gb(G, c)
        k7 = [x["Q3"]["per_k"][6] for x in u]
        print(f"| {LABEL[c]} | GBDT k7 | {ms([x['step1_reco_R'] for x in k7])} | {ms([x['step1_truth_R'] for x in k7])} | "
              f"{ms([x['step2_R'] for x in k7])} | {ms([x['step2_weights']['slope'] for x in k7])} |")
        print(f"| {LABEL[c]} | oracle | — | {f(S[f'H2S1T24K5|{c}']['Q3_oracle_step1_truth_R'])} | "
              f"{f(S[f'H2S1T24K5|{c}']['oracle_R'])} | 1 |")

    print("\n### T3c. Where the PET-GBDT gap arises (GBDT minus PET, in R)\n")
    print("| case | finalist | gap after step 1 (truth space, reco-passing rows) | final gap | added at step 2 |")
    print("|---|---|---|---|---|")
    for c in CASES[1:]:
        u = gb(G, c)
        g1 = st.fmean(x["Q3"]["per_k"][6]["step1_truth_R"] for x in u)
        g2 = st.fmean(x["Q3"]["per_k"][6]["step2_R"] for x in u)
        for d in FIN:
            q = S[f"{d}|{c}"]["Q3"][str(K_PET[d])]
            p1, p2 = q["step1_truth_R"]["mean"], q["step2_R"]["mean"]
            print(f"| {LABEL[c]} | {d[:-2]} | {g1 - p1:+.3f} | {g2 - p2:+.3f} | {(g2 - p2) - (g1 - p1):+.3f} |")

    print("\n### T3b. Detector-level closure in the reco muon marginals at the operating point "
          "(ADDITION after T3; not in the frozen plan)\n")
    print("| case | injected L1 reco p_T / p_∥ (H2 runs) | H2 p_T | H2 p_∥ | L128 p_T | L128 p_∥ | GBDT k7 p_T | GBDT k7 p_∥ |")
    print("|---|---|---|---|---|---|---|---|")
    for c in CASES:
        h, l = S[f"H2S1T24K5|{c}"]["Q3"]["5"], S[f"L128S1T24K4|{c}"]["Q3"]["4"]
        runs = [D["runs"][n] for n in D["runs"] if n.startswith("S4F-H2S1T24K5-" if c == "dev" else "S4S-H2S1T24K5-")
                and (c == "dev" or n.endswith("-" + c))]
        inj = lambda v: ms([x["Q3"]["reco_muon_injected_l1"][v] for x in runs], 4)
        u = gb(G, c)
        k7 = [x["Q3"]["per_k"][6] for x in u]
        print(f"| {LABEL[c]} | {inj('pt')} / {inj('ppar')} | {f(h['step1_reco_pt_R'])} | {f(h['step1_reco_ppar_R'])} | "
              f"{f(l['step1_reco_pt_R'])} | {f(l['step1_reco_ppar_R'])} | {ms([x['step1_reco_pt_R'] for x in k7])} | "
              f"{ms([x['step1_reco_ppar_R'] for x in k7])} |")

    print("\n### T4. Other truth variables at the operating point: R (movement m)\n")
    print("| case | method | p_T | p_∥ | D5 3D cells |")
    print("|---|---|---|---|---|")
    for c in CASES:
        for d in FIN:
            q = S[f"{d}|{c}"]["Q2"]
            print(f"| {LABEL[c]} | {d[:-2]} | " + " | ".join(f"{f(q[h]['pet_R'])} ({f(q[h]['pet_m'], 2)})"
                                                         for h in ("pt", "ppar", "d5_3d")) + " |")
        u = gb(G, c)
        print(f"| {LABEL[c]} | GBDT k7 | " + " | ".join(
            f"{ms([x['Q2'][h]['R'] for x in u])} ({ms([x['Q2'][h]['m'] for x in u], 2)})" for h in ("pt", "ppar", "d5_3d"))
            + " |")
        o = S[f"H2S1T24K5|{c}"]["Q2"]
        print(f"| {LABEL[c]} | oracle | " + " | ".join(f"{f(o[h]['oracle_R'])}" for h in ("pt", "ppar", "d5_3d")) + " |")

    print("\n### T5. Convergence: final R by iteration\n")
    print("| case | method | " + " | ".join(f"k={k}" for k in range(1, 11)) + " |")
    print("|---|---|" + "---|" * 10)
    for c in CASES:
        for d in FIN:
            q = S[f"{d}|{c}"]["Q3"]
            print(f"| {LABEL[c]} | {d[:-2]} | " + " | ".join(
                f"{q[str(k)]['step2_R']['mean']:.3f}" if str(k) in q else "" for k in range(1, 11)) + " |")
        u = gb(G, c)
        print(f"| {LABEL[c]} | GBDT | " + " | ".join(
            f"{st.fmean(x['Q3']['per_k'][k - 1]['step2_R'] for x in u):.3f}" for k in range(1, 11)) + " |")

    print("\n### T6. Design dependence on DEV (D5 NuWro R, two draws; committed tables)\n")
    q5 = D["Q5"]
    print("| PET design | " + " | ".join(f"k={k}" for k in range(2, 7)) + " |")
    print("|---|" + "---|" * 5)
    for des, v in q5["pet_dev_D5_nuwro_R_by_k"].items():
        print(f"| {des} | " + " | ".join(f"{v[str(k)]:.3f}" if str(k) in v else "" for k in range(2, 7)) + " |")
    print("\n| scalar method (matched study) | mean R |")
    print("|---|---|")
    for k, v in q5["scalar_matched_D5_nuwro_mean_R"].items():
        print(f"| {k} | {'—' if v is None else f'{v:.3f}'} |")
    print(f"\ncost: PET reductions {D['cost']['cpu_core_hours']:.3f} CPU core-h; "
          f"GBDT reproduction {json.loads(a.gbdt.read_text())['cost']['cpu_core_hours']:.3f} charged core-h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
