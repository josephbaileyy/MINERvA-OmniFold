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
    vals = list(vals)
    v = [x for x in vals if x is not None]
    if not v:
        return f"undefined ({len(vals)}/{len(vals)})"
    return f"{st.fmean(v):.{nd}f} ± {st.stdev(v):.{nd}f}" if len(v) > 1 else f"{v[0]:.{nd}f}"


def f(s, nd=3):
    if s and s.get("mean") is None:
        return f"undefined ({s.get('n_undefined', 0)}/{s.get('n_undefined', 0)})"
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
    print("| case | oracle R | H2 R | L128 R | GBDT k7 R | m oracle | m H2 | m L128 | m GBDT k7 | orth H2 | orth L128 | orth GBDT k7 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in CASES:
        h, l = S[f"H2S1T24K5|{c}"], S[f"L128S1T24K4|{c}"]
        print(f"| {LABEL[c]} | {f(h['oracle_R'])} | {f(h['pet_R_K'])} | {f(l['pet_R_K'])} | {f(h['gbdt_R_k7'])} | "
              f"{f(h['Q1_m']['oracle'])} | {f(h['Q1_m']['pet'])} | {f(l['Q1_m']['pet'])} | {f(h['Q1_m']['gbdt_k7'])} | "
              f"{f(h['Q1_orth']['pet'])} | {f(l['Q1_orth']['pet'])} | {f(h['Q1_orth']['gbdt_k7'])} |")
    print("\north = |moved − m·injected| / |injected|: movement in the wrong direction.")

    print("\n### T1b. Mean signed residual per E_avail bin (unfolded − target, unit-normalized; ×10³)\n")
    print("| case | method | " + " | ".join(f"bin {i}" for i in range(7)) + " |")
    print("|---|---|" + "---|" * 7)
    for c in CASES:
        for d in FIN:
            rs = [x for n, x in D["runs"].items() if n.startswith(("S4F-" if c == "dev" else "S4S-") + d + "-")
                  and (n.endswith("-" + c) if c != "dev" else "-D" not in n[len("S4F-" + d):])]
            vec = [st.fmean(x["Q1"]["eavail"]["signed_residual_per_bin"][i] for x in rs) for i in range(7)]
            print(f"| {LABEL[c]} | {d[:-2]} | " + " | ".join(f"{1e3 * v:+.1f}" for v in vec) + " |")
        u = gb(G, c)
        vec = [st.fmean(x["Q1"]["eavail"]["signed_residual_per_bin"][i] for x in u) for i in range(7)]
        print(f"| {LABEL[c]} | GBDT k7 | " + " | ".join(f"{1e3 * v:+.1f}" for v in vec) + " |")

    print("\n### T2. E_avail recovery by acceptance region\n")
    print("| case | region | H2 R | L128 R | GBDT k7 R | draws with R < 0: H2 / L128 / GBDT | m H2 | m L128 | m GBDT k7 |")
    print("|---|---|---|---|---|---|---|---|---|")

    def runs_of(d, c):
        return [x for n, x in D["runs"].items() if n.startswith(("S4F-" if c == "dev" else "S4S-") + d + "-")
                and (n.endswith("-" + c) if c != "dev" else "-D" not in n[len("S4F-" + d):])]
    for c in CASES:
        u = gb(G, c)
        for rg in ("low_acceptance", "moderate", "good"):
            h, l = S[f"H2S1T24K5|{c}"]["Q1_region_R"][rg], S[f"L128S1T24K4|{c}"]["Q1_region_R"][rg]
            neg = lambda xs: sum(1 for x in xs if x is not None and x < 0)
            nh = neg(x["Q1"][rg]["R"] for x in runs_of("H2S1T24K5", c))
            nl = neg(x["Q1"][rg]["R"] for x in runs_of("L128S1T24K4", c))
            ng = neg(x["Q1"][rg]["R"] for x in u)
            mh = ms([x["Q1"][rg]["m"] for x in runs_of("H2S1T24K5", c)])
            ml = ms([x["Q1"][rg]["m"] for x in runs_of("L128S1T24K4", c)])
            mg = ms([x["Q1"][rg]["m"] for x in u])
            print(f"| {LABEL[c]} | {rg} | {f(h['pet'])} | {f(l['pet'])} | {f(h['gbdt_k7'])} | {nh}/8 / {nl}/8 / {ng}/8 | "
                  f"{mh} | {ml} | {mg} |")

    print("\n### T3. Step decomposition at the operating point (PET at K; GBDT at k = 7)\n")
    print("| case | method | detector-level R (reco E_avail, step 1) | truth-space R, reco-passing rows (step 1) "
          "| final R, all truth-passing rows (step 2) | weight slope (log push on log oracle) | weight r |")
    print("|---|---|---|---|---|---|---|")
    for c in CASES:
        for d in FIN:
            q = S[f"{d}|{c}"]["Q3"][str(K_PET[d])]
            print(f"| {LABEL[c]} | {d[:-2]} K{K_PET[d]} | {f(q['step1_reco_R'])} | {f(q['step1_truth_R'])} | "
                  f"{f(q['step2_R'])} | {f(q['step2_slope'])} | "
                  f"{ms([x['Q3']['per_k'][K_PET[d] - 1]['step2_weights']['r'] for x in runs_of(d, c)])} |")
        u = gb(G, c)
        k7 = [x["Q3"]["per_k"][6] for x in u]
        print(f"| {LABEL[c]} | GBDT k7 | {ms([x['step1_reco_R'] for x in k7])} | {ms([x['step1_truth_R'] for x in k7])} | "
              f"{ms([x['step2_R'] for x in k7])} | {ms([x['step2_weights']['slope'] for x in k7])} | "
              f"{ms([x['step2_weights']['r'] for x in k7])} |")
        orr = ms([x["Q3"]["oracle_step1_reco_R"] for x in runs_of("H2S1T24K5", c)])
        print(f"| {LABEL[c]} | oracle | {orr} | {f(S[f'H2S1T24K5|{c}']['Q3_oracle_step1_truth_R'])} | "
              f"{f(S[f'H2S1T24K5|{c}']['oracle_R'])} | 1 | 1 |")
    print("\nThe weights are weighted by the prior's w_truth over truth-passing rows (`gd_analyze.weight_agreement`).")

    print("\n### T3c. Final recovery split by reconstruction status (step 2; review finding 4)\n")
    print("Each R is normalized to its own population's injected change, so the columns are not additive shares "
          "of the final gap.\n")
    print("| case | method | step-1 truth-space R, reconstructed rows | final R, reconstructed rows | final R, "
          "non-reconstructed rows | oracle, non-reconstructed rows |")
    print("|---|---|---|---|---|---|")
    for c in CASES:
        orc = ms([x["Q3"]["oracle_step2_R_missed"] for x in runs_of("H2S1T24K5", c)])
        for d in FIN:
            kk = K_PET[d] - 1
            rs = runs_of(d, c)
            print(f"| {LABEL[c]} | {d[:-2]} | {ms([x['Q3']['per_k'][kk]['step1_truth_R'] for x in rs])} | "
                  f"{ms([x['Q3']['per_k'][kk]['step2_R_accepted'] for x in rs])} | "
                  f"{ms([x['Q3']['per_k'][kk]['step2_R_missed'] for x in rs])} | {orc} |")
        k7 = [x["Q3"]["per_k"][6] for x in gb(G, c)]
        print(f"| {LABEL[c]} | GBDT k7 | {ms([x['step1_truth_R'] for x in k7])} | {ms([x['step2_R_accepted'] for x in k7])} | "
              f"{ms([x['step2_R_missed'] for x in k7])} | {orc} |")

    print("\n### T3e. The non-reconstructed rows by iteration (final R)\n")
    print("| case | method | " + " | ".join(f"k={k}" for k in range(1, 8)) + " |")
    print("|---|---|" + "---|" * 7)
    for c in CASES:
        for d in FIN:
            rs = runs_of(d, c)
            print(f"| {LABEL[c]} | {d[:-2]} | " + " | ".join(
                ms([x["Q3"]["per_k"][k - 1]["step2_R_missed"] for x in rs]).split(" ±")[0] if k <= K_PET[d] else ""
                for k in range(1, 8)) + " |")
        u = gb(G, c)
        print(f"| {LABEL[c]} | GBDT | " + " | ".join(
            ms([x["Q3"]["per_k"][k - 1]["step2_R_missed"] for x in u]).split(" ±")[0] for k in range(1, 8)) + " |")

    print("\n### T3b. Detector-level closure in the reco muon marginals at the operating point "
          "(ADDITION after T3; not in the frozen plan)\n")
    print("| case | injected L1 reco p_T / p_∥ (H2 runs), and / floor | H2 p_T | H2 p_∥ | L128 p_T | L128 p_∥ | GBDT k7 p_T | GBDT k7 p_∥ |")
    print("|---|---|---|---|---|---|---|---|")
    for c in CASES:
        h, l = S[f"H2S1T24K5|{c}"]["Q3"]["5"], S[f"L128S1T24K4|{c}"]["Q3"]["4"]
        runs = [D["runs"][n] for n in D["runs"] if n.startswith("S4F-H2S1T24K5-" if c == "dev" else "S4S-H2S1T24K5-")
                and (c == "dev" or n.endswith("-" + c))]
        inj = lambda v: (ms([x["Q3"]["reco_muon_injected_l1"][v] for x in runs], 4) + " (" +
                         ms([x["Q3"]["reco_muon_injected_over_floor"][v] for x in runs], 1) + "×)")
        u = gb(G, c)
        k7 = [x["Q3"]["per_k"][6] for x in u]
        print(f"| {LABEL[c]} | {inj('pt')} / {inj('ppar')} | {f(h['step1_reco_pt_R'])} | {f(h['step1_reco_ppar_R'])} | "
              f"{f(l['step1_reco_pt_R'])} | {f(l['step1_reco_ppar_R'])} | {ms([x['step1_reco_pt_R'] for x in k7])} | "
              f"{ms([x['step1_reco_ppar_R'] for x in k7])} |")

    print("\n### T4. Other truth variables at the operating point: R (movement m)\n")
    print("R is undefined where the injected change is below the scorer's floor, 0.012 × √(nbins/7).\n")
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
        rs = runs_of("H2S1T24K5", c)
        print(f"| {LABEL[c]} | injected / floor | " + " | ".join(
            ms([x["Q2"][h]["injected_over_floor"] for x in rs], 1) + "×" for h in ("pt", "ppar", "d5_3d")) + " |")

    print("\n### T5. Convergence: final R by iteration\n")
    print("| case | method | " + " | ".join(f"k={k}" for k in range(1, 11)) + " |")
    print("|---|---|" + "---|" * 10)
    for c in CASES:
        for d in FIN:
            q = S[f"{d}|{c}"]["Q3"]
            print(f"| {LABEL[c]} | {d[:-2]} | " + " | ".join(
                f"{q[str(k)]['step2_R']['mean']:.3f}" if str(k) in q else "" for k in range(1, 11)) + " |")
        gq = S[f"H2S1T24K5|{c}"]["Q4_gbdt_R_by_k"]                     # committed GBDT R, k = 1..10
        print(f"| {LABEL[c]} | GBDT | " + " | ".join(f"{gq[str(k)]['mean']:.3f}" for k in range(1, 11)) + " |")

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
