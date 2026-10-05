"""Render the PET final-design study deck from committed results. Nothing by hand.

    python make_final_deck.py [--out-dir DIR] [--no-pdf]

Reuses the predecessor deck's machinery (`improvement_campaign/slides/make_campaign_deck.py`:
`Sources`, `Numbers`, `Deck`, `render`, `table`, styling): every measured or derived number on a slide
is registered with the committed JSON field (or derivation) it came from, written to
`deck_numbers.json`, and re-checked by `test_final_deck_numbers.py`; `CLAIM_INDEX-deck.md` is written by
the same run. Identifiers (candidate ids, iteration counts k, case ids) and protocol constants (floors,
margins, thresholds) are labels, not results.

Sources (relative to `nd-unfolding/pet/final_design/`):
  banks/BANK_MANIFEST.json; results/predecessor_posthoc/*.posthoc.json; results/step2int/*.posthoc.json;
  dev/DEV_TABLES-20260927.json (dev/summarize_dev.py), dev/SCREENS-20260927.json (dev/apply_finalist_rule.py
  --n2), sizing/n2_all-20260927.json (dev/n2_table.py), resources/cost_t24-20260927.json, sizing/sizing_*-20260927.json;
  scalar/results/SCALAR_AUSSIE_MATCHED-20260925.json; results/final/decision_look*.json and
  results/final/coverage_*.json (rendered as "pending" while absent).

Scope, first and last frames: PET is diagnostic method development; nothing here is a publication
adoption, and no historical threshold, verdict or the predecessor's disposition changes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PRED = STUDY.parent / "improvement_campaign" / "slides"
sys.path.insert(0, str(PRED))
import make_campaign_deck as base  # noqa: E402  (predecessor machinery, imported unchanged)
from make_campaign_deck import Deck, Numbers, Sources, table  # noqa: E402

TEX_NAME = "final_design_deck.tex"
FIG_DIR = "figures"
SCOPE = ("PET is diagnostic method development. Nothing here is a publication adoption; no historical "
         "threshold, verdict or the predecessor campaign's disposition changes; simulation only.")
BANKS = "banks/BANK_MANIFEST.json"
DEVT = "dev/DEV_TABLES-20260927.json"
SCR = "dev/SCREENS-20260927-3d.json"
N2T = "sizing/n2_all-20260927-3d.json"
COST = "resources/cost_t24-20260927.json"
SZF = "sizing/sizing_final-20260927.json"
SZL = "sizing/sizing_library-20260927.json"
AUS = "scalar/results/SCALAR_AUSSIE_MATCHED-20260925.json"
PP = "results/predecessor_posthoc/{run}.posthoc.json"
S2 = "results/step2int/{run}.posthoc.json"
DEC = "results/final/decision_look1.json"
B1D = "results/final/b1_dependence_look1.json"
FBC = "resources/cost_fb_look1-20260930.json"
COV = "results/final/coverage_dev/coverage_H2S1T24K5.json"
FIN = "results/final/coverage_dev/decision_final.json"
CURVE_DESIGNS = ("C", "H1", "H2", "H2S1", "H2S1T24", "L128S1", "L128S1T24", "P2preA1", "P2scrS1")
COLORS = {"C": "#009E73", "H1": "#999999", "H2": "#E69F00", "H2S1": "#0072B2", "H2S1E16": "#56B4E9",
          "L128S1": "#CC79A7", "L128S1E16": "#D55E00", "P2preS1": "#000000", "P2scrS1": "#8C564B",
          "CTL": "#1F4E79", "B": "#F0E442", "H2S1T24": "#0B3D91", "L128S1T24": "#882255",
          "P2preA1": "#444444"}


def fig(name: str, width: str = r"0.95\linewidth") -> str:
    return rf"\includegraphics[width={width}]{{{FIG_DIR}/{name}}}"


# ------------------------------------------------------------------------------------------ slides
def s_title(d: Deck) -> None:
    d.frames.append("\\gdef\\evidencetext{}\n\\frame{\\titlepage}\n")


def s_question(d: Deck) -> None:
    body = r"""
\begin{itemize}\small
\item Select one complete PET design (detector/truth representations, model and initialization, recipe,
  miss rule, iteration count, uncertainty procedure) among a declared, tested family --- or conclude
  ``no eligible design'' / ``unresolved'' with the discriminating evidence.
\item The smaller network is preferred \emph{only} if non-inferior (simultaneous one-sided 95\,\%, margin
  $-0.02$ on the primary recovery, plus frozen regional/topology margins) \emph{and} at least $2\times$
  cheaper in measured total cost; otherwise the stronger larger/pretrained design.
\item Numeric decision table frozen before any successor run (\texttt{PROTOCOL-20260925.md}); final
  inference conditional on frozen event banks; final-bank runs blinded until an explicit UNBLIND
  amendment.
\end{itemize}"""
    d.frame("Question, preference and decision rule", body, ["PROTOCOL-20260925.md"])


def s_capacity(d: Deck, n: Numbers) -> None:
    dev = n.f("bank_dev", BANKS, ["banks", "DEV", "count"], "int")
    fb = n.f("bank_fb", BANKS, ["banks", "FB", "count"], "int")
    rb = n.f("bank_rb", BANKS, ["banks", "RB", "count"], "int")
    rows = [["DEV (exposed)", dev, "development; every prior"],
            ["FB (never drawn)", fb, "final pseudodata; sealed except listed runs"],
            ["RB (pool R, never opened)", rb, "reserve; sealed"]]
    body = table(["bank", "rows", "use"], rows, "lrl") + r"""

\vspace{0.3cm}\small Only $\approx 3.4$ historical-size replicates of never-drawn events exist and no further
same-model simulation: final replicates are independent random subsets \emph{given the banks}; the bank's own
offset is reported beside every contrast."""
    d.frame("Fresh-event capacity and independence", body, [BANKS, "CAPACITY-20260925.md"])
    d.claim("Bank sizes", ["bank_dev", "bank_fb", "bank_rb"])


def _pp(est: str, rep: str, case: str) -> str:
    return PP.format(run=f"stress-{est}-{rep}-{case}")


def s_diagnostics(d: Deck, n: Numbers) -> None:
    ids = []
    for case, lab in (("D4c_p_up", "4c"), ("D4d_n_up", "4d")):
        ids.append(n.add(f"inj_{lab}", "mean", [(_pp("C", r, case), ["iterations", 2, "eavail_vs_pseudodata",
                                                                      "injected_l1"]) for r in ("T0", "T1")], "3"))
    n.add("inj_dev", "mean", [(PP.format(run=f"final-C-F{r}"), ["iterations", 2, "eavail_vs_pseudodata",
                                                                  "injected_l1"]) for r in range(12)], "3")
    rows = []
    for est in ("CTL", "C", "B"):
        cells = [est]
        for k in (1, 3, 10):
            cells.append(n.add(f"det_esum_{est}_k{k}", "mean",
                               [(_pp(est, r, "D4c_p_up"), ["iterations", k - 1, "step1_detector",
                                                           "reco_Esum_decile", "recovery"])
                                for r in ("T0", "T1")], "+2"))
        for k in (1, 3, 10):
            cells.append(n.add(f"pull_p_{est}_k{k}", "mean",
                               [(_pp(est, r, "D4c_p_up"), ["iterations", k - 1, "pull_selected", "class_p",
                                                           "recovery"]) for r in ("T0", "T1")], "+2"))
        rows.append(cells)
    body = (r"\small Injected $E_\mathrm{avail}$ L1: tilt " + n.r("inj_dev") + r", protons$\times1.3$ "
            + n.r("inj_4c") + r", neutrons$\times1.3$ " + n.r("inj_4d")
            + r" --- the multiplicity cases barely move the scored marginal.\par\vspace{0.2cm}"
            + table(["", r"det.\ $\Sigma E$ $k{=}1$", "$k{=}3$", "$k{=}10$", r"pull $p$-class $k{=}1$",
                     "$k{=}3$", "$k{=}10$"], rows, "lrrrrrr")
            + r"\par\vspace{0.2cm}\small Protons$\times1.3$ (2 replicates): the baseline detector step (CTL, C) mis-closes "
              r"the cluster-energy distribution and transmits almost no proton-content change to the pull; with reco "
              r"summaries (B) both are transmitted. Development evidence.")
    d.frame("Where the multiplicity failure sits: the detector step", body,
            ["results/predecessor_posthoc/", "DIAGNOSTICS-20260925.md"])
    d.claim("Injection sizes and detector-step transmission",
            ["inj_dev", "inj_4c", "inj_4d", "det_esum_C_k3", "pull_p_C_k3", "pull_p_B_k10"])


def s_learnability(d: Deck, n: Numbers) -> None:
    rows = []
    for arm, lab in (("baseline", "raw PDG"), ("pdg_onehot", "one-hot PDG"),
                     ("pdg_onehot_counts", "one-hot + counts"), ("pdg_onehot-eff-E24", "one-hot, 24 epochs")):
        run = f"A-{arm}-eff-T0-D4c" if "E24" not in arm else "A-pdg_onehot-eff-E24-T0-D4c"
        sel = n.f(f"learn_psel_{arm}", S2.format(run=run), ["iterations", 0, "push_selected", "class_p",
                                                             "recovery"], "2")
        mis = n.f(f"learn_pmiss_{arm}", S2.format(run=run), ["iterations", 0, "push_missed", "class_p",
                                                              "recovery"], "2")
        nsel = n.f(f"learn_nsel_{arm}", S2.format(run=run), ["iterations", 0, "push_selected", "class_n",
                                                              "recovery"], "2")
        rows.append([lab, sel, mis, nsel])
    cpull = n.f("pullfit_C", S2.format(run="B-Cpull1-pdg_onehot-eff-T0-D4c"),
                ["iterations", 0, "push_all", "joint_eavail_p", "recovery"], "3")
    bpull = n.f("pullfit_B", S2.format(run="B-Bpull1-pdg_onehot-eff-T0-D4c"),
                ["iterations", 0, "push_all", "joint_eavail_p", "recovery"], "3")
    body = (table(["truth arm (step 2 on the exact weights)", "p-class sel.", "p-class missed",
                   "n-class sel."], rows, "lrrr")
            + r"\par\vspace{0.25cm}\small Given C's real iteration-1 pull, the one-hot truth step recovers "
            + cpull + r" of the joint $E_\mathrm{avail}\times$proton change; given B's, " + bpull
            + r". The truth step learns and extrapolates what it receives; the loss is upstream.")
    d.frame("Truth-step learnability (bounded interventions)", body, ["results/step2int/",
                                                                       "DIAGNOSTICS-20260925.md"])
    d.claim("Learnability and projection", ["learn_psel_pdg_onehot", "learn_pmiss_pdg_onehot",
                                            "learn_nsel_baseline", "pullfit_C", "pullfit_B"])


def _curve(src: Sources, label: str, cand: str, ks: list[int]) -> list[Any]:
    t = src.load(DEVT)
    cell = t.get(label, {}).get(cand)
    return [None if cell is None else cell.get(str(k), {}).get("mean") for k in ks]


def s_devscreen(d: Deck, n: Numbers, out: Path) -> None:
    plt = base._plt()
    ks = [1, 2, 3, 4, 5, 6]
    panels = (("dev tilt R (F reps)", "development tilt $R$", 0.60, "screen 0.60"),
              ("D4c topo (E x p) R", r"protons$\times$1.3: joint $E\times p$ recovery", 0.25, "screen 0.25"),
              ("D4d E_avail res L1", r"neutrons$\times$1.3: $E_\mathrm{avail}$ residual L1", 0.021, "screen 0.021"))
    fig_, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    for ax, (lab, ylab, th, tlab) in zip(axes, panels):
        for c in CURVE_DESIGNS:
            ys = _curve(d.n.src, lab, c, ks)
            pts = [(k, y) for k, y in zip(ks, ys) if y is not None]
            if pts:
                ax.plot(*zip(*pts), marker="o", ms=3, lw=1.3, color=COLORS[c], label=c)
        ax.axhline(th, **base.FLOOR_STYLE)
        ax.set_xlabel("iteration $k$")
        ax.set_title(ylab, fontsize=8.5)
    axes[0].legend(fontsize=6.5, ncol=2)
    base._save(fig_, out / FIG_DIR / "dev_screen.pdf")
    ids = []
    for c, k in (("H2S1", 5), ("C", 3), ("H2", 3)):
        n.f(f"dev_{c}_k{k}", DEVT, ["dev tilt R (F reps)", c, str(k), "mean"], "3")
        ids.append(f"dev_{c}_k{k}")
    n.f("d4d_H2_k3", DEVT, ["D4d E_avail res L1", "H2", "3", "mean"], "3")
    n.f("d4d_H2S1_k5", DEVT, ["D4d E_avail res L1", "H2S1", "5", "mean"], "3")
    n.f("topo_H2S1_k5", DEVT, ["D4c topo (E x p) R", "H2S1", "5", "mean"], "3")
    ids += ["d4d_H2_k3", "d4d_H2S1_k5", "topo_H2S1_k5"]
    body = fig("dev_screen.pdf") + (
        r"\par\small Reco summaries lift the tilt (H2S1 $k{=}5$: " + n.r("dev_H2S1_k5") + r"; C $k{=}3$: "
        + n.r("dev_C_k3") + r"); the forced-1e-5 schedule fails the neutron screen (H2 $k{=}3$: "
        + n.r("d4d_H2_k3") + r") while the constant rate passes (H2S1 $k{=}5$: " + n.r("d4d_H2S1_k5")
        + r", topology " + n.r("topo_H2S1_k5") + r"). Development evidence, 2 draws per case.")
    d.frame("Development screen (DEV bank)", body, [DEVT, "DEVELOPMENT-20260926.md"])
    d.claim("Development screen", ids)


def s_screens(d: Deck, n: Numbers) -> None:
    doc = d.n.src.load(SCR)
    scr = doc["designs"]
    rows = []
    for c in ("H2S1T24", "H2S1", "H2S1E16", "CS1", "L128S1T24", "L128S1", "L128S1E16", "L64S1", "P2preS1",
              "P2preA1", "P2scrS1"):
        if c not in scr:
            continue
        r = scr[c]
        kst = r["Kstar"]
        dv = n.f(f"scr_dev_{c}", SCR, ["designs", c, "dev_tilt_at_Kstar"], "3") if kst is not None else "---"
        n1 = (r.get("S-N1_at_Kstar") or {}).get("status") or "---"
        n2 = r.get("S-N2_at_Kstar") or {}
        n2s = n.f(f"scr_n2_{c}", SCR, ["designs", c, "S-N2_at_Kstar", "sd"], "3") if n2.get("sd") is not None else "---"
        rows.append([c, "---" if kst is None else str(kst), dv, n1, n2s])
    comp, large = doc["packages"]["compact"], doc["packages"]["large"]
    body = table(["design", "$K^*$", r"dev.\ tilt at $K^*$", "S-N1", r"seed sd (S-N2 $\le 0.05$)"], rows,
                 "llrlr", r"\scriptsize") + (
        r"\par\vspace{0.2cm}\small Rule committed before the recoveries it ranks were inspected, with addenda "
        r"(completeness, S-N1, S-N2); finalists: compact " + base.esc(comp["finalist"]) + r" $K{=}" + str(comp["K"])
        + r"$, large " + base.esc(large["finalist"]) + r" $K{=}" + str(large["K"]) + r"$ (Amendments 3c, 3d).")
    d.frame("Finalist rule applied mechanically", body, [SCR, "dev/FINALIST_RULE-20260926.md"])
    d.claim("Finalist screens", [k for k in n.entries if k.startswith(("scr_dev_", "scr_n2_"))])


def s_repro(d: Deck, n: Numbers) -> None:
    ids = []
    rows = []
    for c in ("H2S1", "L128S1", "L64S1", "CS1", "H2S1E16", "L128S1E16", "H2S1T24", "L128S1T24"):
        t = d.n.src.load(N2T)
        if c not in t:
            continue
        v = n.f(f"n2_{c}", N2T, [c, "pooled_within_draw_sd"], "3")
        ids.append(f"n2_{c}")
        rows.append([c, "8 epochs" if c in ("H2S1", "L128S1", "L64S1", "CS1") else
                     ("16 epochs (both steps)" if "E16" in c else "24 epochs"), str(t[c]["k"]), v,
                     "pass" if t[c]["pooled_within_draw_sd"] <= 0.05 else "fail"])
    body = table(["design", "truth step", "$k$", r"seed sd of $R_{E0}$", r"N2 ($\le 0.05$)"], rows, "llrrl",
                 r"\scriptsize") + (
        r"\par\vspace{0.2cm}\small DEV draws 0--1 $\times$ 4 estimator seeds at fixed events. The spread sits in "
        r"the truth step (the detector step varies little with the seed); a 24-epoch truth step repairs it "
        r"(Amendment 3b).")
    d.frame("Reproducibility repair (single-unfolding seed spread)", body, [N2T, "PROTOCOL-20260925.md (3b)"])
    d.claim("Reproducibility", ids)


def s_finalists(d: Deck, n: Numbers) -> None:
    cs = n.f("cost_H2S1T24", COST, ["candidates", "H2S1T24", "median"], "2")
    cl = n.f("cost_L128S1T24", COST, ["candidates", "L128S1T24", "median"], "2")
    nf = n.f("n_F", SZF, ["n_F"], "int")
    ne0 = n.f("n_E0_ni", SZF, ["contrasts", "6.5 E0 (H2S1T24 - L128S1T24)", "n_for_power"], "int")
    nl = n.f("n_lib", SZL, ["n_F"], "int")
    body = (r"\small\begin{itemize}"
            r"\item Compact \textbf{H2S1T24} ($K{=}5$) and large \textbf{L128S1T24} ($K{=}4$): detector reco "
            r"summaries, categorical truth PDG, constant rate, 24-epoch truth step; step-1 PET 47\,k vs 0.97\,M "
            r"parameters. Anchors CTL and C at $k{=}3$."
            r"\item Cost per unfolding (charged A100-h, declared packing): " + cs + r" (compact) vs " + cl +
            r" (large): the smaller network is not cheaper, so the cost-based preference cannot apply."
            r"\item Independent sizing: $n_F = " + nf + r"$ (capped; $E_0$ non-inferiority between the finalists "
            r"would need " + ne0 + r" draws --- a quantified limit); D4c/D3 draws " + nl + r"."
            r"\item Final bank: FINAL, 21-case library and coverage run blinded until the UNBLIND amendment."
            r"\end{itemize}")
    d.frame("Frozen finalists and final-stage design", body, [COST, SZF, SZL, "PROTOCOL-20260925.md (3c--3f)"])
    d.claim("Finalists, cost and sizing", ["cost_H2S1T24", "cost_L128S1T24", "n_F", "n_E0_ni", "n_lib"])


def s_aussie(d: Deck, n: Numbers) -> None:
    dec = d.n.src.load(AUS)["decision"]
    rows = []
    for key in list(dec)[:4]:
        a, o = dec[key]["aussie"], dec[key]["omnifold"]
        rows.append([base.esc(dec[key]["pair"]),
                     n.f(f"aus_mv_{key}", AUS, ["decision", key, "aussie", "moves_away"], "int"),
                     n.f(f"of_mv_{key}", AUS, ["decision", key, "omnifold", "moves_away"], "int"),
                     n.f(f"aus_worst_{key}", AUS, ["decision", key, "aussie", "worst_case_mean_R"], "+3"),
                     n.f(f"of_worst_{key}", AUS, ["decision", key, "omnifold", "worst_case_mean_R"], "+3")])
    body = table(["matched pair", "AUSSIE moves-away", "OmniFold", "AUSSIE worst $R$", "OmniFold"],
                 rows, "lrrrr", r"\scriptsize") + (
        r"\par\vspace{0.2cm}\small Bounded matched stress test (same inputs, miss handling, data and tuning "
        r"opportunity): AUSSIE loses on robustness and stability; it does not advance to a PET backbone.")
    d.frame("Algorithmic alternative: AUSSIE (scalar, matched)", body,
            [AUS, "scalar/SCALAR_AUSSIE_MATCHED-20260925.md"])


def _status(e: dict) -> str:
    """Eligibility status with the rules behind it: failed for INELIGIBLE, not yet assessed for INCOMPLETE."""
    why = e.get("failed") or e.get("incomplete") or []
    if not why:
        return e["status"]
    return f"{e['status']} ({why[0]}--{why[-1]})" if len(why) > 2 else f"{e['status']} ({', '.join(why)})"


def s_final(d: Deck, n: Numbers) -> None:
    if not d.n.src.exists(DEC):
        d.frame("Final bank results", r"\centering\Large Pending --- final-bank runs are blinded until the "
                r"UNBLIND amendment.", ["PROTOCOL-20260925.md (Amendments 2, 2c)"])
        return
    fin = (("H2S1T24K5", "H2S1T24", "h"), ("L128S1T24K4", "L128S1T24", "l"))

    def v(c, rule, i, key, tag, fmt="3"):
        return n.f(f"look1_{tag}_{rule}_{i}_{key}", DEC, ["eligibility", c, "verdicts", rule, "parts", i, key], fmt)

    def est_lb(c, rule, i, tag):
        return v(c, rule, i, "estimate", tag) + " (" + v(c, rule, i, "lb", tag) + ")"

    rows = [["$E_0$ development tilt (U1)"] + [est_lb(c, "U1", 0, t) for c, _, t in fin],
            ["moderate / good region (U2b)"] + [v(c, "U2b", 0, "estimate", t) + " / " + v(c, "U2b", 2, "estimate", t)
                                               for c, _, t in fin],
            ["$E_3$ opposite tilt (U3)"] + [est_lb(c, "U3", 0, t) for c, _, t in fin],
            ["$E_4$ proton topology (U4)"] + [est_lb(c, "U4", 0, t) for c, _, t in fin],
            ["$E_5$ $E_\\mathrm{avail}\\times q_3$ (U5)"] + [est_lb(c, "U5", 0, t) for c, _, t in fin],
            ["N2 seed sd ($\\le 0.05$)"] + [v(c, "N2", 0, "estimate", t) for c, _, t in fin],
            ["gain over CTL in $R_{E_0}$"] + [n.f(f"look1_{t}_switch", DEC, ["switching_vs_reference", c, "t", "mean"], "+3")
                                                + " (" + n.f(f"look1_{t}_switch_lb", DEC, ["switching_vs_reference", c, "t", "lb"], "3") + ")"
                                                for c, _, t in fin],
            ["cost per unfolding (A100-h)"] + [n.f(f"look1_{t}_cost", FBC, ["candidates", cid, "median"], "2")
                                               for _, cid, t in fin],
            ["status (rules)"] + [base.esc(_status(d.n.src.load(DEC)["eligibility"][c])) for c, _, _ in fin]]
    body = table(["look 1 (mean, simultaneous LB)", "H2S1T24 $K{=}5$", "L128S1T24 $K{=}4$"], rows, "lrr",
                 r"\scriptsize") + (
        r"\par\vspace{0.15cm}\small Ranking: " + base.esc(str(d.n.src.load(DEC)["ranking"].get("outcome"))) +
        r". No look 2 (no sequential rule returned CONTINUE). Coverage of H2S1T24 runs blinded.")
    d.frame("Look 1: finalists on the final bank", body, [DEC, FBC])
    d.claim("Look-1 endpoints and cost", sorted(k for k in n.entries if k.startswith("look1_")))

    b2 = lambda c, t, key: n.f(f"b2_{t}_{key}", DEC, ["eligibility", c, "verdicts", "B2", "numbers", "D4d_n_down",
                                                     "residual_minus_injected", key], "4")
    cp = lambda c, t, key, fmt="3": n.f(f"b1dep_{t}_{key}", B1D, ["candidates", c, "common_panel", key], fmt)
    body = (r"\small\begin{itemize}"
            r"\item \textbf{B2} (D4d n down, mean residual $-$ injected $E_\mathrm{avail}$ L1, limit 0.010, a point rule): "
            r"H2S1T24 " + b2("H2S1T24K5", "h", "mean") + r" [" + b2("H2S1T24K5", "h", "lb") + ", " +
            b2("H2S1T24K5", "h", "ub") + r"] PASS; L128S1T24 " + b2("L128S1T24K4", "l", "mean") + r" [" +
            b2("L128S1T24K4", "l", "lb") + ", " + b2("L128S1T24K4", "l", "ub") + r"] FAIL. "
            r"\textbf{Point-decided, statistically unresolved}: both intervals cross the limit; the difference is not "
            r"resolved by this comparison. Not evidence that the compact design is more robust, nor that the two are "
            r"equivalent."
            r"\item \textbf{B1} PASSes under its frozen independence-based bound. Under within-draw dependence the "
            r"evidence is insufficient to establish a per-unit failure probability $\le 0.10$: on the common panel "
            r"(FB0--7) H2S1T24 has " + cp("H2S1T24K5", "h", "draws_with_a_failure", "int") + "/" +
            cp("H2S1T24K5", "h", "n_draws", "int") + r" draws with a failure (CP upper " +
            cp("H2S1T24K5", "h", "cp_upper_draw_any_failure") + r"), L128S1T24 " +
            cp("L128S1T24K4", "l", "draws_with_a_failure", "int") + "/" + cp("L128S1T24K4", "l", "n_draws", "int") +
            r"; with none the bound would be " + cp("H2S1T24K5", "h", "cp_upper_if_no_draw_failed") +
            r". This does not show the probability exceeds 0.10."
            r"\item Like-for-like and FB-population recoveries agree on the designated endpoints (report \S6, report only)."
            r"\end{itemize}")
    d.frame("Look 1: what the verdict does and does not show", body,
            [DEC, B1D, "results/final/population_look1.json"])
    d.claim("B2 point decision and B1 dependence", sorted(k for k in n.entries if k.startswith(("b2_", "b1dep_"))))


def s_coverage(d: Deck, n: Numbers) -> None:
    if not d.n.src.exists(COV):
        d.frame("Uncertainty calibration", r"\centering\Large Pending --- coverage runs blinded.",
                ["PROTOCOL-20260925.md (Amendment 5)"])
        return
    cov = d.n.src.load(COV)["rules"]

    def part(rule, i, key, fmt="3"):
        return n.f(f"cov_{rule}_{i}_{key}", COV, ["rules", rule, "parts", i, key], fmt)

    ratios = [cov["C4"]["parts"][i]["estimate"] / cov["C4"]["parts"][i]["threshold"] for i in range(1, 7)]
    lo = n.add("cov_C4_ratio_min", "ratio", [(COV, ["rules", "C4", "parts", 1 + ratios.index(min(ratios)), "estimate"]),
                                             (COV, ["rules", "C4", "parts", 1 + ratios.index(min(ratios)), "threshold"])], "2")
    hi = n.add("cov_C4_ratio_max", "ratio", [(COV, ["rules", "C4", "parts", 1 + ratios.index(max(ratios)), "estimate"]),
                                             (COV, ["rules", "C4", "parts", 1 + ratios.index(max(ratios)), "threshold"])], "2")
    rows = [["C1 pooled 95\\,\\% (LB $\\ge$0.90, point $\\le$0.99)", part("C1", 1, "estimate") + " (LB " + part("C1", 0, "lb") + ")",
             "unresolved"],
            ["C1 pooled 68\\,\\% (LB $\\ge$0.60, point $\\le$0.80)", part("C1", 3, "estimate") + " (LB " + part("C1", 2, "lb") + ")",
             "decisive"],
            ["\\textbf{C1} (both levels)", "", base.esc(cov["C1"]["verdict"])],
            ["C2 every bin 95\\,\\% $\\ge$ 0.85", "all bins pass", base.esc(cov["C2"]["verdict"])],
            ["C3 moderate / good 95\\,\\% LB $\\ge$ 0.85", part("C3", 0, "lb") + " / " + part("C3", 1, "lb"), base.esc(cov["C3"]["verdict"])],
            ["C4 half-width / limit, bins 1--6 ($\\le$1)", lo + "--" + hi, base.esc(cov["C4"]["verdict"])],
            ["C5 D4c up", "skipped after decisive C1--C4 FAIL", "---"]]
    body = table(["H2S1T24 $K{=}5$, B = 6, 120 replicates", "measured", "verdict"], rows, "llr", r"\scriptsize") + (
        r"\par\vspace{0.15cm}\small In aggregate the six-member interval is \textbf{too wide}; the same against the "
        r"FB population target. Not uniformly conservative: the low-acceptance region \textbf{under-covers} (68\,\%: " +
        n.f("cov_low_68", COV, ["regions", "low_acceptance", "levels", "0.68", "pooled", "point"], "2") + r", 95\,\%: " +
        n.f("cov_low_95", COV, ["regions", "low_acceptance", "levels", "0.95", "pooled", "point"], "2") +
        r"), a region no rule gates. Mechanism not established.")
    d.frame("Uncertainty calibration: coverage of H2S1T24", body, [COV])
    d.claim("Coverage C1-C4", sorted(k for k in n.entries if k.startswith("cov_")))


def s_terminal(d: Deck, n: Numbers) -> None:
    if not d.n.src.exists(FIN):
        return
    fin = d.n.src.load(FIN)
    rows = [[base.esc(c), base.esc(_status(e))] for c, e in fin["eligibility"].items()
            if c in ("H2S1T24K5", "L128S1T24K4")]
    body = (r"\centering\Large\textbf{" + base.esc(str(fin["ranking"].get("outcome"))) + r"}\par\vspace{0.3cm}" +
            table(["finalist", "status (rules)"], rows, "ll", r"\small") + r"\raggedright\par\vspace{0.3cm}\small"
            r"\begin{itemize}\item No design selected and no default named (the default must itself be eligible)."
            r"\item Supported: H2S1T24's point estimator passes every accuracy, robustness and stability rule; its "
            r"interval procedure fails calibration (too wide in aggregate; under-covers at low acceptance). "
            r"Not supported: a ranking of the finalists."
            r"\item Remaining route (owner decision): \S11 repair --- interval calibrated on DEV, re-validated on the "
            r"sealed RB bank.\end{itemize}")
    d.frame("Terminal outcome (frozen rules)", body, [FIN, "DECISION_RECORD-pet-final-design.md"])


CMP = ("nd-unfolding/pet/configuration_comparison/CONFIGURATION_COMPARISON-20260918.md (Gregor's minerva-ml pinned "
       "at fc9a099; sections cited as cmp)")
# what each tested design changes, and which of its parts come from Gregor's work (the pinned configuration
# comparison's borrow recommendations: per-family/whole-event energy sums 4, aggregate overflow 6, type embedding 2,
# one capacity step 7; his paper backbone, checkpoint, typed tokens and recipe for the PET2 arms)
ARCH = [
    ("H1", "C + categorical truth PDG (13-way one-hot)", "type encoding (cmp 2), padding kept distinct; truth step is ours"),
    ("H2", "H1 + reco summaries at step 1", "whole-event energy sums + overflow (cmp 4, 6; not per-family)"),
    ("CS1", "C + constant rate", "---"),
    ("H2S1", "H2 + constant rate", "as H2"),
    ("H2S1E16", "H2S1, 16 epochs", "as H2"),
    ("L64H2", "H2, step-1 PET width 64", "as H2 + one capacity step (cmp 7)"),
    ("L128H2", "H2, step-1 PET width 128", "as H2 + one capacity step (cmp 7)"),
    ("L64S1", "H2S1, width 64", "as L64H2"),
    ("L128S1", "H2S1, width 128", "as L128H2"),
    ("L128S1E16", "L128S1, 16 epochs", "as L128H2"),
    ("P2preS1", "PET2-small at step 1, pretrained", "his backbone, checkpoint, 33-token typed inputs, recipe"),
    ("P2scrS1", "PET2-small, random init", "as P2preS1 without the checkpoint"),
    ("P2preA1", "P2preS1, annealed step-1 rate", "as P2preS1"),
    ("P2scrA1", "P2scrS1, annealed step-1 rate", "as P2scrS1"),
    ("H2S1T24", "H2S1, 24-epoch truth step (finalist)", "as H2"),
    ("L128S1T24", "L128S1, 24-epoch truth step (finalist)", "as L128H2"),
]


def _why_dev(n: Numbers, c: str, r: dict) -> str:
    """The development screen a design failed, from the committed screen table and the rule's own thresholds."""
    sys.path.insert(0, str(STUDY / "dev"))
    from apply_finalist_rule import SCREENS
    if r.get("Kstar") is None:
        rows = [x for x in r["rows"] if x["status"] != "incomplete"]
        if not rows:
            return "incomplete (not run to a decision)"

        def fails(x, sc):
            v, (_, op, thr) = x["values"][sc][0], SCREENS[sc]
            return v is not None and (v < thr if op == ">=" else v > thr)
        always = [sc for sc in SCREENS if all(fails(x, sc) for x in rows)]
        if not always:
            return "no $k$ passes all four screens"
        sc = always[0]
        op = SCREENS[sc][1]
        best = (max if op == ">=" else min)(range(len(rows)), key=lambda i: rows[i]["values"][sc][0])
        i = r["rows"].index(rows[best])
        v = n.f(f"arch_{c}_{sc}", SCR, ["designs", c, "rows", i, "values", sc, 0], "3")
        return (f"{sc} fails at every $k$ (best {v}; need {'$\\ge$' if op == '>=' else '$\\le$'}"
                f" {SCREENS[sc][2]})")
    if (r.get("S-N1_at_Kstar") or {}).get("status") == "fail":
        return f"S-N1 step-1 weight tail at $K^*={r['Kstar']}$"
    sd = (r.get("S-N2_at_Kstar") or {}).get("sd")
    if sd is not None and sd > 0.05:
        return "S-N2 seed sd " + n.f(f"arch_{c}_n2", SCR, ["designs", c, "S-N2_at_Kstar", "sd"], "3") + " $> 0.05$"
    return None


def s_architectures(d: Deck, n: Numbers) -> None:
    scr = d.n.src.load(SCR)["designs"]
    fin = d.n.src.load(FIN)["eligibility"] if d.n.src.exists(FIN) else {}
    final_why = {"H2S1T24": ("H2S1T24K5", "final bank: coverage C1, C4 FAIL"),
                 "L128S1T24": ("L128S1T24K4", "final bank: B2 FAIL (point-decided)")}
    rows = []
    for c, change, gregor in ARCH:
        if c in final_why and final_why[c][0] in fin:
            why = final_why[c][1] + " --- " + base.esc(_status(fin[final_why[c][0]]))
        else:
            why = _why_dev(n, c, scr[c]) or "passed every development screen"
        rows.append([base.esc(c), change, gregor, why])
    body = table(["design", "change", "from Gregor's work", "why it did not pass"], rows, "llll", r"\tiny") + (
        r"\par\vspace{0.1cm}\tiny Also closed: the step-2 ensemble fallback (H2S1X4, L128S1X4; entry condition never met) and "
        r"AUSSIE (bounded matched scalar test). Anchors/controls (CTL, C, B) are not selectable. "
        r"Development screens: S-U1 tilt, S-U3 opposite tilt, S-U4 proton topology, S-B2 D4d residual; then S-N1, S-N2. "
        r"Gregor-derived parts follow the pinned comparison (cmp sections); the truth-step design is the study's own.")
    d.frame("Architectures tested, what came from Gregor's work, and why none passed", body,
            [SCR, FIN, "DEVELOPMENT-20260926.md", CMP])
    d.claim("Architecture table", sorted(k for k in n.entries if k.startswith("arch_")))


def s_cannot(d: Deck) -> None:
    body = r"""\small\begin{itemize}
\item No publication adoption; no real-data unfolding; no \texttt{C\_stat}/\texttt{C\_ML}; no Gate-6 work;
  \texttt{OI-126} not reopened; the scalar-5D covariance unchanged; no note/primer/paper change.
\item Historical thresholds and verdicts (\texttt{NEITHER\_ELIGIBLE / NO\_SELECTION}) and the predecessor's
  disposition are unchanged.
\item Scope of any selection: signal-only simulation, the inventory's simulated detector response, the study's
  event scale, conditional on the frozen banks; generator dependence beyond histogram reweightings is unprobed.
\end{itemize}"""
    d.frame("What this study cannot authorize", body, ["docs/orchestration/AUTHORIZATION-20260925-pet-final-design.md"])


PREAMBLE = base.PREAMBLE


def build(out: Path, make_pdf: bool) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    (out / FIG_DIR).mkdir(exist_ok=True)
    src = Sources(STUDY)
    n = Numbers(src)
    d = Deck(n)
    s_title(d)
    s_question(d)
    s_capacity(d, n)
    s_diagnostics(d, n)
    s_learnability(d, n)
    s_devscreen(d, n, out)
    s_repro(d, n)
    s_screens(d, n)
    s_aussie(d, n)
    s_finalists(d, n)
    s_final(d, n)
    s_coverage(d, n)
    s_terminal(d, n)
    s_architectures(d, n)
    s_cannot(d)
    title = (r"\title{PET final-design selection study}" "\n"
             r"\subtitle{Study deck (generated from committed results)}" "\n"
             r"\author{PET final-design study}" "\n"
             r"\date{\parbox{0.8\linewidth}{\centering\small " + SCOPE + r"}}" "\n")
    tex = PREAMBLE + title + "\n\\begin{document}\n\n" + "\n".join(d.frames) + "\n\\end{document}\n"
    (out / TEX_NAME).write_text(tex)
    record = {"schema": "pet-final-design-deck-numbers/1", "generator": "slides/make_final_deck.py",
              "root": "nd-unfolding/pet/final_design", "main_slides": d.main_count,
              "sources": {rel: src.sha[rel] for rel in sorted(src.sha)},
              "numbers": [n.entries[k] for k in sorted(n.entries)]}
    (out / "deck_numbers.json").write_text(json.dumps(record, indent=1) + "\n")
    lines = ["# Claim index — PET final-design study deck", "",
             "Generated by `make_final_deck.py` with the TeX and `deck_numbers.json`; do not edit by hand.",
             "Paths relative to `nd-unfolding/pet/final_design/`.", "", f"**Scope.** {SCOPE}", "",
             "| slide | claim | number id = rendered |", "|---:|---|---|"]
    for c in d.claims:
        for j, nid in enumerate(c["ids"]):
            r = n.entries[nid]["rendered"].replace(r"\ensuremath{-}", "−")
            lines.append(f"| {c['slide'] if j == 0 else ''} | {c['text'] if j == 0 else ''} | `{nid}` = {r} |")
    (out / "CLAIM_INDEX-deck.md").write_text("\n".join(lines) + "\n")
    if make_pdf:
        base.TEX_NAME = TEX_NAME
        base.compile_pdf(out)
    return record


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", type=Path, default=HERE)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    rec = build(a.out_dir.resolve(), not a.no_pdf)
    print(f"main slides: {rec['main_slides']}; numbers: {len(rec['numbers'])}")


if __name__ == "__main__":
    main()
