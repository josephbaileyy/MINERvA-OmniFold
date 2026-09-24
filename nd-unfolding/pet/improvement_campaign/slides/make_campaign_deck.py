"""Render the PET improvement campaign's comparison deck from committed results. Nothing by hand.

    python make_campaign_deck.py [--out-dir DIR] [--confirm PATH] [--no-pdf]

Every measured or derived quantity on a slide goes through `Numbers`, which reads it from a
committed JSON file (or derives it from such fields by a named operation: mean, difference, ratio,
count...) and records where it came from. The records are written to `deck_numbers.json`;
`test_deck_numbers.py` re-reads every source field and recomputes every derivation. The claim
index `CLAIM_INDEX-deck.md` is written by the same run, so the deck and the index cannot drift.

What is NOT routed through `Numbers`: identifiers used as labels (iteration indices such as
k = 3 or K* = 10, run and case identifiers such as `D1_p0.350`, the sample-size axis values of
Phase D, which are the runs' own `prior_size`/`data_size` fields used as group keys), and the
dates in file names. Those name things; they are not results.

Sources read (paths relative to `nd-unfolding/pet/improvement_campaign/`):
  phase_a/receipts/{runtime_audit_theirs,historical_receipts}.json
  phase_b/scalar/results/{summary,reference_decomposition}.json
  phase_b/pet/results/summary.json and the per-run *.scores.json it indexes
  phase_d/results/scalar_scaling.json
  phase_e/results/{identifiability,references,reference_assessment,toy_reference}.json
  phase_f/results/aussie_ablation.json
  confirm/results/confirm_results.json            (optional; FINAL/STRESS sections optional)
  ../configuration_comparison/campaign_report.json (the preserved historical result, read only)

The confirmatory stage may not have finished. When `confirm_results.json` or its `final`
section is absent the deck renders a slide marked "confirmatory results pending"; PILOT numbers,
when present, are shown only under that label (the protocol reports them separately and never
lets them enter FINAL).

Scope, stated on the first and last frames: PET is diagnostic method development. Nothing in the
deck is a publication adoption, and nothing changes the historical comparison's verdict or
thresholds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent

HIST = "../configuration_comparison/campaign_report.json"
A_THEIRS = "phase_a/receipts/runtime_audit_theirs.json"
A_HIST = "phase_a/receipts/historical_receipts.json"
B1 = "phase_b/scalar/results/summary.json"
B1_DECOMP = "phase_b/scalar/results/reference_decomposition.json"
B2 = "phase_b/pet/results/summary.json"
B2_RUN = "phase_b/pet/results/{run}.scores.json"
D_SCALE = "phase_d/results/scalar_scaling.json"
E_IDENT = "phase_e/results/identifiability.json"
E_REFS = "phase_e/results/references.json"
E_ASSESS = "phase_e/results/reference_assessment.json"
E_TOY = "phase_e/results/toy_reference.json"
F_ABL = "phase_f/results/aussie_ablation.json"
CONFIRM = "confirm/results/confirm_results.json"

TEX_NAME = "campaign_comparison_v2.tex"
FIG_DIR = "figures_campaign"
REGIONS = ("low_acceptance", "moderate", "good")
KSTAR = 10

SCOPE = ("PET is diagnostic method development. Nothing here is a publication adoption, and "
         "nothing here changes the historical comparison's verdict or thresholds.")


# --------------------------------------------------------------------------- numbers
def render(value: Any, fmt: str) -> str:
    """One number (or flag) as it appears in the TeX. Shared with the test."""
    if fmt == "bool":
        return "yes" if value else "no"
    if fmt == "none":
        return "None" if value is None else str(value)
    if fmt == "int":
        if float(value) != round(float(value)):
            raise ValueError(f"{value!r} is not integer-valued")
        return _minus(str(int(round(float(value)))))
    if fmt == "sci":
        v = float(value)
        exp = math.floor(math.log10(abs(v)))
        mant = v / 10 ** exp
        mant_s = f"{mant:.0f}" if abs(mant - round(mant)) < 1e-6 else f"{mant:.1f}"
        return rf"\ensuremath{{{mant_s}\times10^{{{exp}}}}}"
    if fmt == "pct0":
        return f"{100 * float(value):.0f}\\,\\%"
    if fmt == "pct0floor":
        return f"{math.floor(100 * float(value)):.0f}\\,\\%"
    if fmt == "x1":
        return f"{float(value):.1f}\\ensuremath{{\\times}}"
    if fmt.startswith("+"):
        return _minus(f"{float(value):+.{int(fmt[1:])}f}")
    return _minus(f"{float(value):.{int(fmt)}f}")


def _minus(text: str) -> str:
    return r"\ensuremath{-}" + text[1:] if text.startswith("-") else text


OPS: dict[str, Callable[[list[float]], Any]] = {
    "field": lambda xs: xs[0],
    "mean": lambda xs: statistics.fmean(xs),
    "sd": lambda xs: statistics.stdev(xs),
    "diff": lambda xs: xs[0] - xs[1],
    "ratio": lambda xs: xs[0] / xs[1],
    "one_minus": lambda xs: 1.0 - xs[0],
    "one_minus_ratio": lambda xs: 1.0 - xs[0] / xs[1],
    "min": lambda xs: min(xs),
    "max": lambda xs: max(xs),
    "count": lambda xs: len(xs),
    "count_lt0": lambda xs: sum(1 for x in xs if x < 0),
    "count_gt0": lambda xs: sum(1 for x in xs if x > 0),
    "count_true": lambda xs: sum(1 for x in xs if x),
    "any_true": lambda xs: any(bool(x) for x in xs),
    "mean_abs": lambda xs: statistics.fmean(abs(x) for x in xs),
}


def fetch(doc: Any, path: list) -> Any:
    node = doc
    for key in path:
        node = node[key] if isinstance(node, dict) else node[int(key)]
    return node


class Sources:
    """Committed JSON files, loaded once, hashed for the provenance record."""

    def __init__(self, root: Path, overrides: dict[str, Path] | None = None):
        self.root = root
        self.overrides = overrides or {}
        self.docs: dict[str, Any] = {}
        self.sha: dict[str, str] = {}

    def path(self, rel: str) -> Path:
        return self.overrides.get(rel, self.root / rel)

    def exists(self, rel: str) -> bool:
        return self.path(rel).is_file()

    def load(self, rel: str) -> Any:
        if rel not in self.docs:
            raw = self.path(rel).read_bytes()
            self.sha[rel] = hashlib.sha256(raw).hexdigest()
            self.docs[rel] = json.loads(raw)
        return self.docs[rel]

    def get(self, rel: str, path: list) -> Any:
        return fetch(self.load(rel), path)


class Numbers:
    """Registry of every number that reaches the TeX, and where it came from."""

    def __init__(self, sources: Sources):
        self.src = sources
        self.entries: dict[str, dict[str, Any]] = {}

    def _resolve(self, inp: Any) -> Any:
        if isinstance(inp, str):
            return self.entries[inp]["value"]
        return self.src.get(inp[0], list(inp[1]))

    def add(self, nid: str, op: str, inputs: list, fmt: str, note: str = "") -> str:
        values = [self._resolve(i) for i in inputs]
        value = OPS[op](values)
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"{nid}: non-finite value")
        rec = {"id": nid, "op": op, "fmt": fmt, "value": value, "rendered": render(value, fmt),
               "inputs": [i if isinstance(i, str) else {"file": i[0], "path": list(i[1])}
                          for i in inputs]}
        if note:
            rec["note"] = note
        if nid in self.entries and self.entries[nid] != rec:
            raise ValueError(f"number id {nid!r} registered twice with different content")
        self.entries[nid] = rec
        return rec["rendered"]

    def f(self, nid: str, rel: str, path: list, fmt: str = "3", note: str = "") -> str:
        return self.add(nid, "field", [(rel, path)], fmt, note)

    def v(self, nid: str) -> Any:
        return self.entries[nid]["value"]

    def r(self, nid: str) -> str:
        return self.entries[nid]["rendered"]


# --------------------------------------------------------------------------- deck model
class Deck:
    def __init__(self, nums: Numbers):
        self.n = nums
        self.frames: list[str] = []
        self.claims: list[dict[str, Any]] = []
        self.main_count = 0
        self.in_appendix = False
        self.slide_titles: list[str] = []

    def frame(self, title: str, body: str, evidence: Iterable[str], options: str = "") -> None:
        ev = "; ".join(_tt(e) for e in evidence)
        self.slide_titles.append(title)
        if not self.in_appendix:
            self.main_count += 1
        opt = f"[{options}]" if options else ""
        self.frames.append(
            f"\\gdef\\evidencetext{{{ev}}}\n"
            f"\\begin{{frame}}{opt}{{{title}}}\n{body.strip()}\n\\end{{frame}}\n")

    def claim(self, text: str, ids: list[str]) -> None:
        for i in ids:
            if i not in self.n.entries:
                raise KeyError(f"claim cites unregistered number {i!r}")
        self.claims.append({"slide": len(self.slide_titles) + 1, "text": text, "ids": ids})

    def appendix(self) -> None:
        self.in_appendix = True
        self.frames.append("\\appendix\n\\gdef\\evidencetext{}\n"
                           "\\begin{frame}{Appendix}\\centering\\Large Backup\\end{frame}\n")
        self.slide_titles.append("Appendix")


def _tt(path: str) -> str:
    text = path.replace("_", r"\_").replace("#", r"\#").replace("{", r"\{").replace("}", r"\}")
    return r"\texttt{" + text + "}"


def esc(text: str) -> str:
    return (text.replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("&", r"\&")
            .replace("%", r"\%").replace("#", r"\#").replace("$", r"\$"))


def table(header: list[str], rows: list[list[str]], align: str, size: str = r"\small") -> str:
    lines = [f"{{{size}", r"\begin{tabular}{" + align + "}", r"\toprule",
             " & ".join(header) + r" \\", r"\midrule"]
    lines += [" & ".join(r) + r" \\" for r in rows]
    lines += [r"\bottomrule", r"\end{tabular}}"]
    return "\n".join(lines)


def fig(name: str, width: str = r"0.95\linewidth") -> str:
    return rf"\includegraphics[width={width}]{{{FIG_DIR}/{name}}}"


# --------------------------------------------------------------------------- styling
# One colour per estimator, everywhere. Okabe-Ito palette (colour-blind safe). The historical
# floor is always the vermillion dashed line.
STYLE = {
    "pet_H": dict(color="#0072B2", ls="-", marker="o", label="PET, historical recipe (H / CTL)"),
    "pet_C2": dict(color="#E69F00", ls="-", marker="s", label="PET + reco energy summaries (C2 / B)"),
    "pet_M": dict(color="#009E73", ls="-", marker="^", label="PET, efficiency-corrected step 2 (M / C)"),
    "ibu_carry": dict(color="#56B4E9", ls="--", marker="o", label="IBU, muon + reco $E_{avail}$, carry-misses"),
    "ibu_eff": dict(color="#009E73", ls="--", marker="^", label="IBU, muon + reco $E_{avail}$, eff.-corrected"),
    "ibu_muon": dict(color="#999999", ls="--", marker="x", label="IBU, muon only, carry-misses"),
    "gbdt_carry": dict(color="#56B4E9", ls=":", marker="D", label="GBDT OmniFold + reco $E_{avail}$, carry-misses"),
    "gbdt_eff": dict(color="#009E73", ls=":", marker="D", label="GBDT OmniFold, eff.-corrected"),
    "mlp_had": dict(color="#CC79A7", ls="-.", marker="v", label="MLP OmniFold + reco hadronic summaries"),
    "aussie0": dict(color="#8C564B", ls="-.", marker="P", label=r"AUSSIE, $\lambda=0$"),
    "oracle": dict(color="#000000", ls=(0, (1, 2)), marker="", label="oracle anchor (exact tilt)"),
    "hist_ours": dict(color="#000000", marker="*", label="historical ours"),
    "hist_theirs": dict(color="#CC79A7", marker="*", label="historical theirs"),
}
FLOOR_STYLE = dict(color="#D55E00", ls="--", lw=1.3)


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "legend.fontsize": 7.5,
                         "pdf.fonttype": 42, "svg.hashsalt": "deck"})
    return plt


def _floor(ax, floor: float, text: str) -> None:
    ax.axhline(floor, **FLOOR_STYLE, zorder=1)
    ax.annotate(text, xy=(1.0, floor), xycoords=("axes fraction", "data"), xytext=(-2, 3),
                textcoords="offset points", ha="right", va="bottom", color=FLOOR_STYLE["color"],
                fontsize=7.5)


def _save(fig_, out: Path) -> None:
    fig_.tight_layout()
    fig_.savefig(out, metadata={"CreationDate": None, "ModDate": None, "Creator": None,
                                "Producer": None})
    import matplotlib.pyplot as plt
    plt.close(fig_)


def _line(ax, xs, ys, key, lo=None, hi=None, **kw):
    st = STYLE[key]
    ax.plot(xs, ys, color=st["color"], ls=st.get("ls", "-"), marker=st.get("marker", "o"),
            ms=4, lw=1.5, label=kw.pop("label", st["label"]), **kw)
    if lo is not None:
        ax.fill_between(xs, lo, hi, color=st["color"], alpha=0.15, lw=0)


# --------------------------------------------------------------------------- helpers
def b2_run(src: Sources, run: str) -> str:
    return B2_RUN.format(run=run)


def b2_iter_index(src: Sources, run: str, k: int) -> int:
    its = src.get(b2_run(src, run), ["iterations"])
    for i, it in enumerate(its):
        if it["k"] == k:
            return i
    raise KeyError(f"{run}: no iteration with k={k}")


def ks_of(src: Sources, run: str) -> list[int]:
    return [it["k"] for it in src.get(b2_run(src, run), ["iterations"])]


# =========================================================================== slides
def slide_title(d: Deck, n: Numbers) -> None:
    d.frames.append("\\gdef\\evidencetext{}\n\\frame{\\titlepage}\n")
    d.slide_titles.append("title")
    d.main_count += 1


def slide_historical(d: Deck, n: Numbers) -> None:
    ours = n.f("hist.ours", HIST, ["absolute_adequacy", "arms", "ours", "mean_recovery"], "4")
    theirs = n.f("hist.theirs", HIST, ["absolute_adequacy", "arms", "theirs", "mean_recovery"], "4")
    ref = n.f("hist.reference", HIST, ["absolute_adequacy", "reference"], "4")
    frac = n.f("hist.frac", HIST, ["thresholds", "adequacy_fraction_of_reference"], "1")
    floor = n.f("hist.floor", HIST, ["absolute_adequacy", "floor"], "4")
    dm = n.f("hist.d", HIST, ["interval", "mean"], "4")
    lo = n.f("hist.ci_lo", HIST, ["interval", "ci_low"], "4")
    hi = n.f("hist.ci_hi", HIST, ["interval", "ci_high"], "4")
    npairs = n.f("hist.npairs", HIST, ["interval", "n_pairs"], "int")
    amp = n.f("hist.amplitude", HIST, ["endpoint", "amplitude"], "2")
    neg = n.add("hist.pairs_favour_theirs", "count_lt0",
                [(HIST, ["paired_differences", s]) for s in
                 n.src.get(HIST, ["paired_differences"])], "int")
    ni = n.f("hist.ni_delta", HIST, ["thresholds", "non_inferiority_delta"], "2")
    sw = n.f("hist.switch_delta", HIST, ["thresholds", "switching_delta"], "2")
    verdict = esc(n.src.get(HIST, ["verdict"]))
    rec = esc(n.src.get(HIST, ["recommendation"]))
    body = rf"""
The completed matched comparison injected a known truth $E_{{\mathrm{{avail}}}}$ tilt (amplitude {amp})
into simulated pseudodata and scored the seven-bin recovery of the injected displacement.
\begin{{center}}
{table(["arm", "mean recovery", "adequacy floor", "adequate"],
       [["our production PET", ours, floor, "no"],
        ["Gregor's pretrained PET2-small", theirs, floor, "no"]], "lrrc")}
\end{{center}}
Floor $= {frac}\times$ an acceptance reference {ref} built from $1-(1-a)^k$ at $k=3$.
Paired \texttt{{ours $-$ theirs}} $= {dm}$, 95\,\% interval $[{lo},\,{hi}]$, $n={npairs}$ seed pairs;
his arm scored better in {neg} of {npairs} pairs.
\begin{{block}}{{Verdict (preserved, unchanged by this campaign)}}
\texttt{{{verdict} / {rec}}}. Non-inferiority margin {ni} and switching margin {sw} are the historical
ones and are used unchanged for every like-for-like statement below.
\end{{block}}
\textbf{{This campaign asks:}} what caused the shortfall, what fixes it, whether more events help,
whether the adequacy reference is appropriate, and what limits remain."""
    d.claim("Historical recovery: ours, theirs, against the floor (fraction x reference)",
            ["hist.ours", "hist.theirs", "hist.floor", "hist.frac", "hist.reference"])
    d.claim("Historical paired difference and 95% interval over n pairs; his arm better in every pair",
            ["hist.d", "hist.ci_lo", "hist.ci_hi", "hist.npairs", "hist.pairs_favour_theirs"])
    d.claim("Historical margins used unchanged", ["hist.ni_delta", "hist.switch_delta"])
    d.frame("The question, and the historical result", body, [HIST])


def slide_audit(d: Deck, n: Numbers) -> None:
    opt = ["fits", 0, "optimizer_at_train_begin"]
    cls = esc(n.src.get(A_THEIRS, opt + ["class"]))
    mod = esc(n.src.get(A_THEIRS, opt + ["class_module"]))
    wd = n.f("a1.wd", A_THEIRS, opt + ["weight_decay"], "none")
    clip = n.f("a1.clipnorm", A_THEIRS, opt + ["global_clipnorm"], "none")
    sched = n.f("a1.is_schedule", A_THEIRS, opt + ["learning_rate_is_schedule"], "bool")
    eps = n.f("a1.epsilon", A_THEIRS, opt + ["config", "epsilon"], "sci")
    hvd = n.f("a1.horovod", A_THEIRS, opt + ["is_horovod_wrapped"], "bool")
    # pre-clip global gradient norms, every epoch of every captured fit
    fits = n.src.get(A_THEIRS, ["fits"])
    norm_paths, frac_paths = [], []
    for i, fit_ in enumerate(fits):
        for j, ep in enumerate(fit_["epochs"]):
            if ep.get("grad_global_norm_pre_clip"):
                norm_paths.append((A_THEIRS, ["fits", i, "epochs", j, "grad_global_norm_pre_clip", "max"]))
                frac_paths.append((A_THEIRS, ["fits", i, "epochs", j, "grad_global_norm_pre_clip", "frac_above_1"]))
    gmax = n.add("a1.gradnorm_max", "max", norm_paths, "0")
    gfrac = n.add("a1.clip_bind_frac", "min", frac_paths, "pct0")
    S = ["summary"]
    bt = n.f("a1.batch_theirs", A_HIST, S + ["final/theirs", "batch_size", 0], "int")
    bo = n.f("a1.batch_ours", A_HIST, S + ["final/ours", "batch_size", 0], "int")
    st = n.f("a1.steps_theirs", A_HIST, S + ["final/theirs", "num_steps_gen", 0], "int")
    so = n.f("a1.steps_ours", A_HIST, S + ["final/ours", "num_steps_gen", 0], "int")
    lt = n.f("a1.lr_theirs", A_HIST, S + ["final/theirs", "learning_rate_argument", 0], "sci")
    lo = n.f("a1.lr_ours", A_HIST, S + ["final/ours", "learning_rate_argument", 0], "sci")
    ratio = n.add("a1.update_ratio", "ratio", ["a1.steps_ours", "a1.steps_theirs"], "0")
    body = rf"""
Captured at runtime while the historical code ran unmodified through the guard (Phase A).
\begin{{columns}}[T]
\begin{{column}}{{0.5\linewidth}}
\textbf{{1. Gregor's declared optimizer never ran.}}\par\vspace{{2pt}}
{{\small Declared: TorchAdamW with weight decay, warmup/cosine schedule, global-norm clipping.\\
Executed at step 1: \texttt{{{cls}}} from \texttt{{{mod}}} (Horovod-wrapped: {hvd});
\texttt{{weight\_decay}} {wd}, \texttt{{global\_clipnorm}} {clip}, schedule object: {sched},
$\epsilon$ = {eps}.\\
The intended unit global-norm clip would have bound on {gfrac} of updates (pre-clip norms up to {gmax}).}}
\end{{column}}
\begin{{column}}{{0.48\linewidth}}
\textbf{{2. The ``identical'' step 2 was not identical.}}\par\vspace{{2pt}}
{{\small
{table(["step 2, final stage", "theirs", "ours"],
       [["batch size", bt, bo], ["engine steps at gen", st, so],
        ["iteration-0 learning rate", lt, lo]], "lrr", r"\footnotesize")}\par\vspace{{3pt}}
{ratio}$\times$ more optimizer updates per epoch for ours, and a different validation subset
(the engine cuts train/validation in batches).}}
\end{{column}}
\end{{columns}}
\vspace{{4pt}}
\begin{{alertblock}}{{Defects of fidelity, not established causes}}
These bias the between-arm comparison; they are not shown to cause the recovery shortfall.
The campaign therefore rebuilt the path with explicit per-step recipes; the repaired driver refuses
to train when the executed optimizer differs from the declared one.
\end{{alertblock}}"""
    d.claim("Executed optimizer for Gregor's arm: Horovod Keras Adam, no weight decay, no clipping, no schedule, epsilon",
            ["a1.wd", "a1.clipnorm", "a1.is_schedule", "a1.epsilon", "a1.horovod"])
    d.claim("Intended unit clip would have bound on this fraction of updates; max pre-clip norm",
            ["a1.clip_bind_frac", "a1.gradnorm_max"])
    d.claim("Step 2 batch, engine steps and iteration-0 learning rate differed between arms",
            ["a1.batch_theirs", "a1.batch_ours", "a1.steps_theirs", "a1.steps_ours",
             "a1.lr_theirs", "a1.lr_ours", "a1.update_ratio"])
    d.frame("What actually ran (Phase A audit)", body, [A_THEIRS, A_HIST])


def slide_scalar(d: Deck, n: Numbers, out: Path) -> None:
    ibu = lambda key, k, fld="aggregate": (B1, ["ibu", key, str(k), fld])
    omf = lambda key, k, fld="aggregate": (B1, ["omnifold", key, "by_iteration", str(k), fld, "mean"])
    rows_spec = [
        ("b1.ibu_muon_k3", "binned IBU, muon kinematics only", ibu("muon/carry_misses/engine", 3)),
        ("b1.ibu_eav_k3", r"binned IBU, muon + reco $E_{\mathrm{avail}}$", ibu("muon_eavail/carry_misses/engine", 3)),
        ("b1.gbdt_muon_k3", "GBDT OmniFold, muon only", omf("muon/hgb", 3)),
        ("b1.gbdt_eav_k3", r"GBDT OmniFold, + reco $E_{\mathrm{avail}}$", omf("muon_eavail/hgb", 3)),
        ("b1.mlp_had_k3", "MLP OmniFold, + all reco hadronic summaries", omf("muon_had/mlp", 3)),
    ]
    rows = []
    for nid, label, (rel, path) in rows_spec:
        rows.append([label, n.f(nid, rel, path)])
    rows.append([r"\textbf{historical PET, ours}", r"\textbf{" + n.add("hist.ours3", "field", [(HIST, ["absolute_adequacy", "arms", "ours", "mean_recovery"])], "3") + "}"])
    rows.append([r"\textbf{historical PET, Gregor's arm}", r"\textbf{" + n.add("hist.theirs3", "field", [(HIST, ["absolute_adequacy", "arms", "theirs", "mean_recovery"])], "3") + "}"])
    n.f("b1.ibu_eav_k10", *ibu("muon_eavail/carry_misses/engine", 10))
    n.f("b1.ibu_eav_best", B1, ["ibu", "muon_eavail/carry_misses/engine", "best", "aggregate"])
    n.f("b1.ibu_eav_best_k", B1, ["ibu", "muon_eavail/carry_misses/engine", "best", "iteration"], "int")
    n.f("b1.gbdt_eav_k20", *omf("muon_eavail/hgb", 20))
    n.f("b1.floor3", HIST, ["absolute_adequacy", "floor"], "3")
    n.f("b1.reproduction_checks", B1, ["reproduction", "n_checks"], "int")
    n.f("b1.reproduction_ok", B1, ["reproduction", "all_checks_agree"], "bool")

    # figure: recovery vs iteration
    plt = _plt()
    f, ax = plt.subplots(figsize=(5.0, 4.0))
    src = n.src
    ks_ibu = [k for k in (1, 2, 3, 4, 5, 10, 20)]
    for key, sk in (("muon_eavail/carry_misses/engine", "ibu_carry"),
                    ("muon_eavail/efficiency_corrected/engine", "ibu_eff"),
                    ("muon/carry_misses/engine", "ibu_muon")):
        _line(ax, ks_ibu, [src.get(B1, ["ibu", key, str(k), "aggregate"]) for k in ks_ibu], sk)
    ks = list(range(1, 21))
    for key, sk in (("muon_eavail/hgb", "gbdt_carry"), ("muon_had/mlp", "mlp_had")):
        m = [src.get(B1, ["omnifold", key, "by_iteration", str(k), "aggregate", "mean"]) for k in ks]
        lo_ = [src.get(B1, ["omnifold", key, "by_iteration", str(k), "aggregate", "min"]) for k in ks]
        hi_ = [src.get(B1, ["omnifold", key, "by_iteration", str(k), "aggregate", "max"]) for k in ks]
        _line(ax, ks, m, sk, lo_, hi_, markevery=[0, 2, 9, 19])
    for key, arm in (("hist_ours", "ours"), ("hist_theirs", "theirs")):
        ax.plot([3], [src.get(HIST, ["absolute_adequacy", "arms", arm, "mean_recovery"])],
                ls="", marker="*", ms=11, color=STYLE[key]["color"], label=STYLE[key]["label"], zorder=5)
    _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f}")
    ax.axvline(3, color="#bbbbbb", lw=0.8, zorder=0)
    ax.set_xlabel("iteration $k$")
    ax.set_ylabel("seven-bin $E_{avail}$ recovery")
    ax.set_xlim(0.5, 20.5)
    ax.set_ylim(0, 1)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=6.3)
    _save(f, out / FIG_DIR / "scalar_recovery_vs_k.pdf")

    body = rf"""
\begin{{columns}}[T]
\begin{{column}}{{0.52\linewidth}}
{{\small At $k=3$, on the same endpoint (DEV halves; the historical closure reproduced
bit-exactly, {n.r("b1.reproduction_checks")} checks agree: {n.r("b1.reproduction_ok")}):}}\par\vspace{{3pt}}
{table(["estimator", "recovery"], rows, "lr", r"\scriptsize")}\par\vspace{{4pt}}
{{\small \textbf{{No response-aware scalar estimator reaches the {n.r("b1.floor3")} floor at $k=3$.}}
The shortfall is not PET-specific. Recovery is still climbing: IBU reaches {n.r("b1.ibu_eav_k10")} at
$k=10$ and {n.r("b1.ibu_eav_best")} at $k={n.r("b1.ibu_eav_best_k")}$; GBDT {n.r("b1.gbdt_eav_k20")} at $k=20$.}}
\end{{column}}
\begin{{column}}{{0.46\linewidth}}
{fig("scalar_recovery_vs_k.pdf")}
\end{{column}}
\end{{columns}}"""
    for nid, label, _ in rows_spec:
        d.claim(f"k=3 recovery: {label}", [nid])
    d.claim("No response-aware scalar estimator reaches the floor at k=3", ["b1.floor3", "b1.ibu_eav_k3", "b1.mlp_had_k3"])
    d.claim("Recovery still climbing: IBU at k=10 and its best, GBDT at k=20",
            ["b1.ibu_eav_k10", "b1.ibu_eav_best", "b1.ibu_eav_best_k", "b1.gbdt_eav_k20"])
    d.claim("Historical closure reproduced bit-exactly", ["b1.reproduction_checks", "b1.reproduction_ok"])
    d.frame("Where recovery is lost (1): scalar references", body, [B1, HIST])


def _b2_seeds(run_base: str, seeds=(1, 2)) -> list[str]:
    return [f"{run_base}-s{s}" for s in seeds]


def _b2_mean(n: Numbers, nid: str, run_base: str, k: int, path: list, fmt: str = "3") -> str:
    inputs = []
    for run in _b2_seeds(run_base):
        i = b2_iter_index(n.src, run, k)
        inputs.append((b2_run(n.src, run), ["iterations", i] + path))
    return n.add(nid, "mean", inputs, fmt)


def _b2_paired(n: Numbers, nid: str, arm: str, base: str, k: int, fmt: str = "+3") -> str:
    per = []
    for s in (1, 2):
        a, b = f"{arm}-s{s}", f"{base}-s{s}"
        pid = f"{nid}.s{s}"
        n.add(pid, "diff", [(b2_run(n.src, a), ["iterations", b2_iter_index(n.src, a, k), "push", "recovery"]),
                            (b2_run(n.src, b), ["iterations", b2_iter_index(n.src, b, k), "push", "recovery"])], fmt)
        per.append(pid)
    return n.add(nid, "mean", per, fmt)


def slide_stepwise(d: Deck, n: Numbers, out: Path) -> None:
    H = "b2e3-H-K10"
    ks = (1, 3, 10)
    cols = {
        "push": ["push", "recovery"],
        "pull": ["pull", "recovery"],
        "reco": ["step1_detector_cumulative", "reco_eavail_7", "recovery"],
        "acc_pull": ["pulled_vs_pushed", "accepted", "pull", "recovery"],
        "acc": ["pulled_vs_pushed", "accepted", "push", "recovery"],
        "miss": ["pulled_vs_pushed", "misses", "push", "recovery"],
    }
    rows = []
    for k in ks:
        row = [str(k)]
        for c in ("push", "pull", "reco", "acc", "miss"):
            row.append(_b2_mean(n, f"b2.H.k{k}.{c}", H, k, cols[c]))
        _b2_mean(n, f"b2.H.k{k}.acc_pull", H, k, cols["acc_pull"])
        rows.append(row)
    # miss fraction of the truth sample
    run1 = f"{H}-s1"
    n.add("b2.miss_frac", "one_minus",
          [(b2_run(n.src, run1), ["iterations", 0, "pulled_vs_pushed", "truth_mass_fraction_accepted_B"])], "pct0")
    # truth-side PET, known tilt (best-validation epoch; best_val_epoch is 1-based)
    tru = {}
    for arm in ("T0", "T1", "T2"):
        paths = []
        for s in ("1", "2"):
            be = n.src.get(B2, ["truth_only", f"b2e2f-{arm}", s, "best_val_epoch"])
            paths.append((B2, ["truth_only", f"b2e2f-{arm}", s, "learnability_by_epoch", be - 1]))
        tru[arm] = n.add(f"b2.truth.{arm}", "mean", paths, "3",
                         note="learnability at each seed's best_val_epoch (1-based), mean over seeds")
        n.add(f"b2.truth.{arm}.sd", "sd", paths, "3")
    n.f("b1.truth_eavail", B1, ["truth_learnability", "eavail/hgb", "held_out_aggregate", "mean"])
    n.f("b1.truth_muon", B1, ["truth_learnability", "muon_truth/hgb", "held_out_aggregate", "mean"], "2")

    # figure: grouped bars at k = 1, 3, 10
    plt = _plt()
    f, ax = plt.subplots(figsize=(5.0, 3.6))
    series = [("reco", "step-1 reco $E_{avail}$ closure", "#999999"),
              ("acc_pull", "pull, accepted events", "#56B4E9"),
              ("acc", "step-2 push, accepted events", "#0072B2"),
              ("miss", "step-2 push, missed events", "#E69F00")]
    w = 0.2
    for j, (c, lab, col) in enumerate(series):
        xs = [i + (j - 1.5) * w for i in range(len(ks))]
        ys = [n.v(f"b2.H.k{k}.{c}") for k in ks]
        ax.bar(xs, ys, width=w, color=col, label=lab)
    tot = [n.v(f"b2.H.k{k}.push") for k in ks]
    ax.plot(range(len(ks)), tot, color=STYLE["pet_H"]["color"], marker="o", lw=1.2, ms=4,
            label="truth recovery, all events (the score)")
    _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f}")
    ax.set_xticks(range(len(ks)), [f"$k={k}$" for k in ks])
    ax.set_ylabel("fraction of displacement recovered")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=6.3)
    _save(f, out / FIG_DIR / "stepwise_closure.pdf")

    body = rf"""
\begin{{columns}}[T]
\begin{{column}}{{0.5\linewidth}}
{{\small \textbf{{The truth-side PET is not the bottleneck.}} Given the known tilt alone it learns it to
{tru["T0"]} (raw PDG codes), {tru["T1"]} (one-hot PDG), {tru["T2"]} (+ true $E_{{\mathrm{{avail}}}}$, $q_3$),
against {n.r("b1.truth_muon")} for any learner restricted to true muon $p_T, p_\parallel$
(and {n.r("b1.truth_eavail")} given true $E_{{\mathrm{{avail}}}}$).\par\vspace{{3pt}}
\textbf{{Step 1 is not either:}} the pull closes reco $E_{{\mathrm{{avail}}}}$ to {n.r("b2.H.k1.reco")} after one
iteration, {n.r("b2.H.k10.reco")} by $k=10$.\par\vspace{{3pt}}
\textbf{{The loss is in the misses and in stopping at $k=3$.}} Under carry-misses every missed event
({n.r("b2.miss_frac")} of the truth sample) enters step 2 with its previous weight; over accepted events
the pull holds {n.r("b2.H.k1.acc_pull")} at $k=1$, the push keeps {n.r("b2.H.k1.acc")}.}}
\end{{column}}
\begin{{column}}{{0.49\linewidth}}
{fig("stepwise_closure.pdf")}\\
{table(["$k$", "push", "pull", r"reco $E_{\mathrm{av}}$", "acc.", "missed"], rows, "rrrrrr", r"\scriptsize")}
\end{{column}}
\end{{columns}}"""
    d.claim("Truth-side PET learns the known tilt: raw PDG, one-hot PDG, with truth globals; vs muon-only learner",
            ["b2.truth.T0", "b2.truth.T1", "b2.truth.T2", "b1.truth_muon", "b1.truth_eavail"])
    d.claim("Step 1 closes reco E_avail after one iteration and by k=10", ["b2.H.k1.reco", "b2.H.k10.reco"])
    for k in ks:
        d.claim(f"Stepwise closure (historical recipe, K=10, 2 seeds) at k={k}: push, pull, reco, accepted, missed",
                [f"b2.H.k{k}.{c}" for c in ("push", "pull", "reco", "acc", "miss")])
    d.claim("Missed events are this share of the truth sample; accepted-event pull vs push at k=1",
            ["b2.miss_frac", "b2.H.k1.acc_pull", "b2.H.k1.acc"])
    d.frame("Where recovery is lost (2): step by step inside the unfolding", body,
            [B2, "phase_b/pet/results/b2e3-H-K10-s{1,2}.scores.json", B1])


def slide_levers(d: Deck, n: Numbers, out: Path) -> None:
    H, S1, S2, M = "b2e3-H-K10", "b2e4-S1-K10", "b2e4-S2-K10", "b2e4-M-K10"
    rk = lambda run, k: (B2, ["recovery_by_k", run, str(k), "mean"])
    rows = []
    lr = n.f("ax.lr_after0", A_HIST, ["summary", "final/theirs", "realized_lr_by_fit", 0, 2, 1], "sci",
             note="realized learning rate of the first fit at iteration 1")
    seeds = n.f("b2.H.k10.n", B2, ["recovery_by_k", H, "10", "n"], "int")
    spec = [(H, f"historical recipe (carry-misses, anneal to {lr}, last epoch)"),
            (S1, f"no forced {lr} after iteration 0"),
            (S2, "best-validation epoch handed on"),
            (M, r"\textbf{efficiency-corrected step 2}")]
    for run, label in spec:
        tag = run.split("-")[1]
        r3 = n.f(f"b2.{tag}.k3", *rk(run, 3))
        r10 = n.f(f"b2.{tag}.k10", *rk(run, 10))
        if run == H:
            dcell = "---"
        else:
            dcell = _b2_paired(n, f"b2.{tag}.dk10", run, H, 10)
            dcell += f" [{n.r(f'b2.{tag}.dk10.s1')}, {n.r(f'b2.{tag}.dk10.s2')}]"
        rows.append([label, r3, r10, dcell])
    for tag, run in (("H", H), ("M", M)):
        _b2_mean(n, f"b2.{tag}.k10.low", run, 10, ["push", "recovery_by_region", "low_acceptance"], "2")

    plt = _plt()
    f, ax = plt.subplots(figsize=(5.0, 3.2))
    for run, sk in ((H, "pet_H"), ("b2e5-C2-H", "pet_C2"), (M, "pet_M")):
        ks = sorted(int(k) for k, v in n.src.get(B2, ["recovery_by_k", run]).items() if v.get("n"))
        m = [n.src.get(B2, ["recovery_by_k", run, str(k), "mean"]) for k in ks]
        lo_ = [n.src.get(B2, ["recovery_by_k", run, str(k), "min"]) for k in ks]
        hi_ = [n.src.get(B2, ["recovery_by_k", run, str(k), "max"]) for k in ks]
        _line(ax, ks, m, sk, lo_, hi_)
    for key, arm in (("hist_ours", "ours"), ("hist_theirs", "theirs")):
        ax.plot([3], [n.src.get(HIST, ["absolute_adequacy", "arms", arm, "mean_recovery"])], ls="",
                marker="*", ms=11, color=STYLE[key]["color"], label=STYLE[key]["label"], zorder=5)
    _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f}")
    ax.axvline(3, color="#bbbbbb", lw=0.8, zorder=0)
    ax.set_xlabel("iteration $k$")
    ax.set_ylabel("seven-bin $E_{avail}$ recovery")
    ax.set_ylim(0, 1)
    ax.set_xlim(0.5, 10.5)
    ax.legend(loc="upper left", fontsize=6.5)
    _save(f, out / FIG_DIR / "pet_recovery_vs_k.pdf")

    body = rf"""
\begin{{columns}}[T]
\begin{{column}}{{0.52\linewidth}}
{{\small PET through the repaired driver, DEV halves, $K=10$, paired against the historical recipe
({seeds} seeds; the per-seed paired $\Delta$ in brackets):}}\par\vspace{{3pt}}
{table(["factor", "$k=3$", "$k=10$", r"paired $\Delta$, $k=10$"], rows, "p{3.2cm}rrl", r"\scriptsize")}\par\vspace{{4pt}}
{{\small \textbf{{Iterations and the miss rule are the two levers.}} Efficiency correction clears the
historical floor already at $k=3$ and lifts the low-acceptance region from {n.r("b2.H.k10.low")} to
{n.r("b2.M.k10.low")} at $k=10$. \textbf{{The schedule does not help}}: handing on the best-validation
epoch \emph{{hurts}}.}}
\end{{column}}
\begin{{column}}{{0.47\linewidth}}
{fig("pet_recovery_vs_k.pdf")}\\
{{\scriptsize Bands: min--max over seeds. Efficiency correction is a model-dependence choice; see
the robustness slides.}}
\end{{column}}
\end{{columns}}"""
    for run, label in spec:
        tag = run.split("-")[1]
        ids = [f"b2.{tag}.k3", f"b2.{tag}.k10"] + ([] if run == H else [f"b2.{tag}.dk10", f"b2.{tag}.dk10.s1", f"b2.{tag}.dk10.s2"])
        d.claim(f"PET lever at K=10: {label.replace('$', '')}", ids)
    d.claim("Efficiency correction lifts the low-acceptance region at k=10", ["b2.H.k10.low", "b2.M.k10.low"])
    d.frame("What improves it (1): iterations and the miss rule; the schedule does not", body,
            [B2, "phase_b/pet/results/b2e{3,4}-*-K10-s{1,2}.scores.json"])


def slide_features(d: Deck, n: Numbers) -> None:
    arms = [("C1", "C1 incumbent inputs"), ("C2", r"\textbf{C2 + reco energy summaries at step 1}"),
            ("C3", r"C3 + true $E_{\mathrm{avail}}$, $q_3$ at step 2"), ("C4", "C4 both")]
    rows = []
    seeds = n.f("b2.C1.k10.n", B2, ["recovery_by_k", "b2e5-C1-H", "10", "n"], "int")
    for arm, label in arms:
        run = f"b2e5-{arm}-H"
        r3 = n.f(f"b2.{arm}.k3", B2, ["recovery_by_k", run, "3", "mean"])
        r10 = n.f(f"b2.{arm}.k10", B2, ["recovery_by_k", run, "10", "mean"])
        if arm == "C1":
            rows.append([label, r3, r10, "---", "---"])
            continue
        d3 = _b2_paired(n, f"b2.{arm}.dk3", run, "b2e5-C1-H", 3)
        d10 = _b2_paired(n, f"b2.{arm}.dk10", run, "b2e5-C1-H", 10)
        rows.append([label, r3, r10,
                     f"{d3} [{n.r(f'b2.{arm}.dk3.s1')}, {n.r(f'b2.{arm}.dk3.s2')}]",
                     f"{d10} [{n.r(f'b2.{arm}.dk10.s1')}, {n.r(f'b2.{arm}.dk10.s2')}]"])
    for arm in ("C1", "C2", "C3", "C4"):
        _b2_mean(n, f"b2.{arm}.k10.acc", f"b2e5-{arm}-H", 10, ["pulled_vs_pushed", "accepted", "push", "recovery"], "2")
        _b2_mean(n, f"b2.{arm}.k10.miss", f"b2e5-{arm}-H", 10, ["pulled_vs_pushed", "misses", "push", "recovery"], "2")
    n.add("b2.feat.miss_min", "min", [f"b2.{a}.k10.miss" for a in ("C1", "C2", "C3", "C4")], "2")
    n.add("b2.feat.miss_max", "max", [f"b2.{a}.k10.miss" for a in ("C1", "C2", "C3", "C4")], "2")
    body = rf"""
{{\small Feature arms: carry-misses, one-hot PDG truth side, $K=10$, {seeds} seeds, paired against C1
(per-seed $\Delta$ in brackets).}}
\begin{{center}}
{table(["arm", "$k=3$", "$k=10$", r"paired $\Delta$, $k=3$", r"paired $\Delta$, $k=10$"], rows, "lrrll", r"\footnotesize")}
\end{{center}}
\begin{{itemize}}\small
\item \textbf{{Explicit reconstructed-energy summaries at the detector step are the one input change that pays}}:
they speed convergence and lift the accepted events' truth recovery to {n.r("b2.C2.k10.acc")} at $k=10$.
\item They do not help the missed events ({n.r("b2.feat.miss_min")}--{n.r("b2.feat.miss_max")} in every arm at $k=10$), so
under the engine's miss rule no feature arm reaches the floor at $k=3$.
\item Truth summaries add little: the truth side already extracts $E_{{\mathrm{{avail}}}}$ from the cloud.
\end{{itemize}}"""
    for arm, label in arms:
        ids = [f"b2.{arm}.k3", f"b2.{arm}.k10"]
        if arm != "C1":
            ids += [f"b2.{arm}.dk3", f"b2.{arm}.dk10"]
        d.claim(f"Feature arm {arm}: recovery at k=3, k=10, paired deltas vs C1", ids)
    d.claim("C2 lifts accepted-event truth recovery; misses stay low in every arm",
            ["b2.C2.k10.acc", "b2.feat.miss_min", "b2.feat.miss_max"])
    d.frame("What improves it (2): reconstructed-energy summaries at step 1", body,
            [B2, "phase_b/pet/results/b2e5-C{1..4}-H-s{1,2}.scores.json"])


def _group_runs(runs: list[dict], keyf) -> dict:
    g: dict[Any, list[int]] = defaultdict(list)
    for i, r in enumerate(runs):
        g[keyf(r)].append(i)
    return g


def slide_aussie(d: Deck, n: Numbers) -> None:
    runs = n.src.load(F_ABL)
    g = _group_runs(runs, lambda r: (r["method"], r["miss_handling"], r["k_or_lambda"]))
    spec = [("f.omf_carry50", ("OmniFold", "carry", 50), "scalar OmniFold (HGB)", "carry-misses (the engine's rule)", "$k=50$"),
            ("f.omf_eff50", ("OmniFold", "eff", 50), "scalar OmniFold (HGB)", "efficiency-corrected", "$k=50$"),
            ("f.aussie1000", ("AUSSIE", "lambda=1000", 1000), "AUSSIE", r"misses pinned to the prior ($\lambda=1000$)", "---"),
            ("f.aussie0", ("AUSSIE", "lambda=0", 0), "AUSSIE", r"unconstrained ($\lambda=0$)", "---")]
    rows = []
    for nid, key, est, miss, setting in spec:
        idx = g[key]
        val = n.add(nid, "mean", [(F_ABL, [i, "aggregate"]) for i in idx], "3")
        n.add(nid + ".n", "count", [(F_ABL, [i, "aggregate"]) for i in idx], "int")
        rows.append([est, miss, setting, val, n.r(nid + ".n")])
    n.add("f.gain_miss", "diff", ["f.aussie0", "f.aussie1000"], "+2")
    n.add("f.gain_miss_omf", "diff", ["f.omf_eff50", "f.omf_carry50"], "+2")
    n.add("f.edge", "diff", ["f.aussie0", "f.omf_eff50"], "+2")
    n.f("f.ibu_eff_peak", B1, ["ibu", "muon_eavail/efficiency_corrected/engine", "best", "aggregate"])
    n.f("f.ibu_eff_peak_k", B1, ["ibu", "muon_eavail/efficiency_corrected/engine", "best", "iteration"], "int")
    n.f("f.ibu_eff_k20", B1, ["ibu", "muon_eavail/efficiency_corrected/engine", "20", "aggregate"])
    n.f("f.ibu_eff_k20_low", B1, ["ibu", "muon_eavail/efficiency_corrected/engine", "20", "low_acceptance"])
    body = rf"""
{{\small A bounded scalar benchmark of AUSSIE (arXiv:2602.24282), the non-iterative replacement for
OmniFold's pull step. Its first, confounded result was dissected by ablation (DEV populations):}}
\begin{{center}}
{table(["estimator", "miss handling", "setting", "aggregate recovery", "seeds"], rows, "llcrr", r"\footnotesize")}
\end{{center}}
\begin{{itemize}}\small
\item \textbf{{Most of the apparent gain is miss handling}}: letting the learned ratio extrapolate to
events that fail reconstruction is worth {n.r("f.gain_miss")} (AUSSIE) and {n.r("f.gain_miss_omf")}
(OmniFold); AUSSIE keeps a modest edge ({n.r("f.edge")}) at matched miss handling.
\item A PET-backbone AUSSIE evaluation is \textbf{{not justified}} on this evidence.
\item Efficiency correction is not free: binned IBU with the acceptance division peaks at
{n.r("f.ibu_eff_peak")} ($k={n.r("f.ibu_eff_peak_k")}$) and is back to {n.r("f.ibu_eff_k20")} at $k=20$
with low-acceptance recovery {n.r("f.ibu_eff_k20_low")}. It needs a stopping rule and a variance statement.
\end{{itemize}}"""
    for nid, key, est, miss, setting in spec:
        d.claim(f"Phase F ablation: {est}, {miss.replace('$', '')}", [nid, nid + ".n"])
    d.claim("Miss handling is worth ~+0.20; AUSSIE edge at matched miss handling",
            ["f.gain_miss", "f.gain_miss_omf", "f.edge"])
    d.claim("Efficiency-corrected IBU peaks early then destabilizes",
            ["f.ibu_eff_peak", "f.ibu_eff_peak_k", "f.ibu_eff_k20", "f.ibu_eff_k20_low"])
    d.frame("What improves it (3): miss handling, not the non-iterative form", body, [F_ABL, B1])


def slide_scaling(d: Deck, n: Numbers, out: Path) -> None:
    runs = n.src.get(D_SCALE, ["runs"])
    g = _group_runs(runs, lambda r: (r["exp"], r["method"], r["miss_handling"], r["k_or_lambda"],
                                     r["prior_size"], r["data_size"]))
    prior_sizes = sorted({r["prior_size"] for r in runs if r["exp"] == "vary_prior"})
    data_sizes = sorted({r["data_size"] for r in runs if r["exp"] == "vary_data"})
    full_data = max(r["data_size"] for r in runs if r["exp"] == "vary_prior")
    full_prior = max(r["prior_size"] for r in runs if r["exp"] == "vary_data")
    lab = lambda s: f"{round(s / 1000)}k"
    series = [("carry3", "OmniFold carry-misses, $k=3$", ("OmniFold", "carry", 3), "gbdt_carry"),
              ("carry20", "OmniFold carry-misses, $k=20$", ("OmniFold", "carry", 20), "pet_H"),
              ("eff20", "OmniFold efficiency-corrected, $k=20$", ("OmniFold", "efficiency_corrected", 20), "gbdt_eff"),
              ("aussie0", r"AUSSIE, $\lambda=0$", ("AUSSIE", "lambda=0", 0), "aussie0")]
    rows = []
    for tag, label, (m, mh, k), _ in series:
        row = [label]
        for ps in prior_sizes:
            idx = g[("vary_prior", m, mh, k, ps, full_data)]
            row.append(n.add(f"d.prior.{tag}.{ps}", "mean", [(D_SCALE, ["runs", i, "aggregate"]) for i in idx], "3"))
            n.add(f"d.prior.{tag}.{ps}.sd", "sd", [(D_SCALE, ["runs", i, "aggregate"]) for i in idx], "3")
        rows.append(row)
    row = ["pseudodata size: carry-misses, $k=20$"]
    for ds in data_sizes:
        idx = g[("vary_data", "OmniFold", "carry", 20, full_prior, ds)]
        row.append(n.add(f"d.data.carry20.{ds}", "mean", [(D_SCALE, ["runs", i, "aggregate"]) for i in idx], "3"))
        n.add(f"d.data.carry20.{ds}.sd", "sd", [(D_SCALE, ["runs", i, "aggregate"]) for i in idx], "3")
    row += ["---"] * (len(prior_sizes) - len(data_sizes))
    rows.append(row)
    row = ["oracle anchor (exact tilt on that subset)"]
    for ps in prior_sizes:
        idx = g[("vary_prior", "OmniFold", "carry", 3, ps, full_data)]
        row.append(n.add(f"d.oracle.{ps}", "mean", [(D_SCALE, ["runs", i, "anchor_aggregate"]) for i in idx], "3"))
    rows.append(row)
    lo_ps, hi_ps = prior_sizes[0], prior_sizes[-1]
    n.add("d.gain_k3", "diff", [f"d.prior.carry3.{hi_ps}", f"d.prior.carry3.{lo_ps}"], "+3")
    n.add("d.gain_k20", "diff", [f"d.prior.carry20.{hi_ps}", f"d.prior.carry20.{lo_ps}"], "+3")
    n.add("d.miss_gain", "diff", [f"d.prior.eff20.{hi_ps}", f"d.prior.carry20.{hi_ps}"], "+2")
    n.add("d.data_n", "count", [(D_SCALE, ["runs", i, "aggregate"]) for i in range(len(runs))], "int")

    plt = _plt()
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.9), sharey=True, gridspec_kw={"width_ratios": [4, 3]})
    for tag, label, _, sk in series:
        ys = [n.v(f"d.prior.{tag}.{ps}") for ps in prior_sizes]
        es = [n.v(f"d.prior.{tag}.{ps}.sd") for ps in prior_sizes]
        st = STYLE[sk]
        a1.errorbar(prior_sizes, ys, yerr=es, color=st["color"], ls=st["ls"], marker=st["marker"], ms=4,
                    capsize=2, lw=1.4, label=label.replace(r"\lambda", r"\lambda"))
    a1.plot(prior_sizes, [n.v(f"d.oracle.{ps}") for ps in prior_sizes], color="#000000", ls=(0, (1, 2)),
            lw=1.2, label="oracle anchor")
    ys = [n.v(f"d.data.carry20.{ds}") for ds in data_sizes]
    es = [n.v(f"d.data.carry20.{ds}.sd") for ds in data_sizes]
    a2.errorbar(data_sizes, ys, yerr=es, color=STYLE["pet_H"]["color"], marker="o", ms=4, capsize=2,
                lw=1.4, label="carry-misses, $k=20$")
    for ax, xs, xl in ((a1, prior_sizes, "prior MC size (events)"), (a2, data_sizes, "pseudodata size (events)")):
        ax.set_xscale("log")
        ax.set_xticks(xs, [lab(x) for x in xs])
        ax.minorticks_off()
        ax.set_xlabel(xl)
        _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f}")
    a1.set_ylabel("aggregate recovery")
    a1.set_ylim(0, 1.05)
    a1.legend(loc="lower right", fontsize=6)
    a2.legend(loc="lower right", fontsize=6)
    _save(f, out / FIG_DIR / "scaling.pdf")

    hdr = ["axis (aggregate recovery)"] + [lab(p) for p in prior_sizes]
    body = rf"""
{{\small \textbf{{Development-stage evidence}} (scalar, DEV halves, {n.r("d.data_n")} runs, overlapping draws
per size, a per-subset oracle anchor). The confirmatory study on fresh pool-S draws is separate.}}\par\vspace{{2pt}}
\begin{{columns}}[T]
\begin{{column}}{{0.5\linewidth}}
{table(hdr, rows, "l" + "r" * len(prior_sizes), r"\scriptsize")}\par\vspace{{4pt}}
\begin{{itemize}}\scriptsize
\item Prior-MC statistics buy recovery in the historical miss mode ({n.r("d.gain_k3")} at $k=3$,
{n.r("d.gain_k20")} at $k=20$, {lab(lo_ps)}$\to${lab(hi_ps)}); beyond {lab(hi_ps)} is not measured.
\item Pseudodata statistics are not the binding constraint over this range.
\item Miss handling outweighs every statistical axis tested ({n.r("d.miss_gain")} at {lab(hi_ps)}).
\end{{itemize}}
\end{{column}}
\begin{{column}}{{0.49\linewidth}}
{fig("scaling.pdf")}\\
{{\scriptsize Error bars: sd over draws.}}
\end{{column}}
\end{{columns}}"""
    for tag, label, _, _ in series:
        d.claim(f"Phase D prior-size axis: {label.replace('$', '')}", [f"d.prior.{tag}.{ps}" for ps in prior_sizes])
    d.claim("Phase D pseudodata-size axis, carry-misses k=20", [f"d.data.carry20.{ds}" for ds in data_sizes])
    d.claim("Oracle anchor per prior size", [f"d.oracle.{ps}" for ps in prior_sizes])
    d.claim("Prior-MC gain in the historical miss mode; miss handling outweighs statistics",
            ["d.gain_k3", "d.gain_k20", "d.miss_gain"])
    d.frame("Does more data help? (Phase D, development stage)", body, [D_SCALE])


def slide_reference_decomp(d: Deck, n: Numbers, out: Path) -> None:
    curve = n.src.get(B1_DECOMP, ["curve"])
    i3 = next(i for i, c in enumerate(curve) if c["k"] == 3)
    ref = n.f("ref.cells", B1_DECOMP, ["curve", i3, "cells285"])
    scored = n.f("ref.marginal", B1_DECOMP, ["curve", i3, "marginal7_score"])
    halves = n.f("ref.halves", B1, ["ibu", "diag/carry_misses/engine", "3", "aggregate"])
    n.f("ref.floor", HIST, ["absolute_adequacy", "floor"], "3")
    ibu3 = n.f("ref.ibu_eav_k3", B1, ["ibu", "muon_eavail/carry_misses/engine", "3", "aggregate"])
    n.f("ref.eff_k2", B1, ["ibu", "muon_eavail/efficiency_corrected/engine", "2", "aggregate"])
    n.f("ref.low_ref", B1, ["ibu", "reference", "3", "low_acceptance"])
    n.f("ref.eff_k2_low", B1, ["ibu", "muon_eavail/efficiency_corrected/engine", "2", "low_acceptance"], "2")
    n.f("ref.accepted_ratio", B1, ["reproduction", "accepted_fraction", "ratio_f_A_tilted_over_f_B"], "4")

    plt = _plt()
    f, ax = plt.subplots(figsize=(4.8, 3.0))
    labels = ["historical reference\n(p$_T$, p$_\\parallel$ cells)", "reference model on the\nscored 7-bin spectrum",
              "same, on the actual halves\n(historical normalization)", "response-aware IBU\n(estimator, k=3)"]
    vals = [n.v("ref.cells"), n.v("ref.marginal"), n.v("ref.halves"), n.v("ref.ibu_eav_k3")]
    cols = ["#999999", "#999999", "#999999", STYLE["ibu_carry"]["color"]]
    bars = ax.bar(range(4), vals, color=cols, width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f} (= {n.v('hist.frac'):.1f} x reference)")
    ax.set_xticks(range(4), labels, fontsize=6.5)
    ax.set_ylabel("recovery at $k=3$")
    ax.set_ylim(0, 0.85)
    _save(f, out / FIG_DIR / "reference_decomposition.pdf")

    body = rf"""
\begin{{columns}}[T]
\begin{{column}}{{0.47\linewidth}}
{{\small The reference is $1-(1-a)^k$ at $k=3$ with a per-cell acceptance $a$; the floor is
{n.r("hist.frac")}$\times$ it.\par\vspace{{3pt}}
\textbf{{It is computed on a different quantity from the one scored.}} It is built on the
$(p_T, p_\parallel)$ cell displacement ({ref}); the score is the seven-bin $E_{{\mathrm{{avail}}}}$ marginal.
The model's own assumptions applied to the scored spectrum give {scored}; on the actual halves with the
historical pseudodata normalization, {halves}: \emph{{below the {n.r("ref.floor")} floor derived from it.}}\par\vspace{{3pt}}
\textbf{{It is not an attainability bound in either direction.}} Efficiency-corrected IBU exceeds it
({n.r("ref.eff_k2")} at $k=2$) and recovers the low-acceptance region (reference {n.r("ref.low_ref")}) at
{n.r("ref.eff_k2_low")}, but only by dividing by acceptance, which the engine's miss rule never does.\par\vspace{{3pt}}
The historical normalization assumes the accepted fraction is unchanged by the tilt; measured ratio
{n.r("ref.accepted_ratio")}.}}
\end{{column}}
\begin{{column}}{{0.52\linewidth}}
{fig("reference_decomposition.pdf")}
\end{{column}}
\end{{columns}}"""
    d.claim("Reference decomposition: cells, scored marginal, actual halves; below the floor",
            ["ref.cells", "ref.marginal", "ref.halves", "ref.floor"])
    d.claim("Efficiency-corrected IBU exceeds the reference and recovers low acceptance",
            ["ref.eff_k2", "ref.low_ref", "ref.eff_k2_low"])
    d.claim("Historical normalization assumes unchanged accepted fraction; measured ratio", ["ref.accepted_ratio"])
    d.frame("The adequacy reference (1): what it measures", body, [B1_DECOMP, B1, HIST])


def slide_reference_gap(d: Deck, n: Numbers) -> None:
    S = ["summary"]
    rc = n.src.get(E_ASSESS, ["reference_model", "curve", "iterations"])
    i3 = rc.index(3)
    n.f("e.ref_S", E_ASSESS, ["reference_model", "curve", "aggregate", i3], "4")
    n.f("e.ibu1x", E_ASSESS, S + ["muon_eavail/carry_misses", "1x", "k3", "mean"])
    n.f("e.ibu8x", E_ASSESS, S + ["muon_eavail/carry_misses", "8x", "k3", "mean"])
    n.f("e.diag1x", E_ASSESS, S + ["diag/carry_misses", "1x", "k3", "mean"])
    n.f("e.diag8x", E_ASSESS, S + ["diag/carry_misses", "8x", "k3", "mean"])
    vals = S + ["muon_eavail/carry_misses", "1x", "k3", "values"]
    n.add("e.reps_S", "count", [(E_ASSESS, vals + [i]) for i in range(len(n.src.get(E_ASSESS, vals)))], "int")
    n.add("e.gap", "diff", ["e.ref_S", "e.ibu1x"], "3")
    n.add("e.closed", "diff", ["e.ibu8x", "e.ibu1x"], "3")
    n.add("e.definitional_share", "one_minus_ratio", ["e.closed", "e.gap"], "pct0floor")
    T = "sigma_frac=0.00/"
    it3 = lambda key: (E_TOY, ["expected", T + key, "iterations", 2, "recovery"])
    for key, nid in (("reference_model", "toy.ref"), ("carry_misses", "toy.carry"),
                     ("carry_misses/rate_matched", "toy.rate"), ("efficiency_corrected", "toy.eff")):
        n.add(nid, "field", [it3(key)], "3", note="iterations[2] is iteration 3")
    n.add("toy.renorm", "diff", ["toy.ref", "toy.rate"], "3")
    n.add("toy.norm", "diff", ["toy.rate", "toy.carry"], "3")
    rows = [["historical reference model (rebuilt on pool S)", n.r("e.ref_S"), "---"],
            [r"response-aware IBU, $k=3$", n.r("e.ibu1x"), n.r("e.ibu8x")],
            [r"reference model realized on the scored object", n.r("e.diag1x"), n.r("e.diag8x")]]
    body = rf"""
{{\small \textbf{{The gap is definitional, not statistical}} (fresh pool-S events, {n.r("e.reps_S")} replicates per size):}}
\begin{{center}}
{table(["quantity at $k=3$", "historical size", r"8$\times$ the events"], rows, "lrr", r"\footnotesize")}
\end{{center}}
{{\small Eight times the statistics closes {n.r("e.closed")} of the {n.r("e.gap")} gap: at least
{n.r("e.definitional_share")} of it comes from what the reference assumes, not from sample size.\par\vspace{{4pt}}
\textbf{{A known-function toy}} (no smearing): $1-(1-a)^k$ at $k=3$ gives {n.r("toy.ref")}; the engine's miss rule
attains {n.r("toy.carry")} ({n.r("toy.renorm")} of the gap from the score's renormalization, {n.r("toy.norm")} from the
engine's normalization); efficiency correction reaches {n.r("toy.eff")}, above it. Neither a bound nor a match.}}
\begin{{block}}{{Prospective recommendation only (not adopted; changes no verdict)}}
\small A reference must be computed for the estimator's actual miss rule and normalization, on the scored
seven-bin spectrum, and a floor derived from it checked on a known-function toy before use. The historical
thresholds are retained unchanged for every like-for-like verdict in this campaign.
\end{{block}}"""
    d.claim("Pool S: rebuilt reference; response-aware IBU at 1x and 8x; reference model realized at 1x and 8x",
            ["e.ref_S", "e.ibu1x", "e.ibu8x", "e.diag1x", "e.diag8x"])
    d.claim("8x the events closes only a small part of the gap; definitional share",
            ["e.closed", "e.gap", "e.definitional_share"])
    d.claim("Toy: reference, carry-misses, decomposition, efficiency correction",
            ["toy.ref", "toy.carry", "toy.renorm", "toy.norm", "toy.eff"])
    d.frame("The adequacy reference (2): a definitional gap", body, [E_ASSESS, E_TOY])


def slide_identifiability(d: Deck, n: Numbers) -> None:
    dist = n.src.get(E_IDENT, ["distortions"])
    ratio_ids = []
    for name in sorted(dist):
        if not name.startswith("D") or not dist[name]["predeclared"]:
            continue
        rid = f"id.ratio.{name}"
        n.add(rid, "ratio", [(E_IDENT, ["distortions", name, "auc_minus_half"]),
                             (E_IDENT, ["distortions", name, "threshold_ess_scaled"])], "x1")
        n.f(f"id.dist.{name}", E_IDENT, ["distortions", name, "distinguishable_vs_scaled_null"], "bool")
        ratio_ids.append(rid)
    n.add("id.ratio_min", "min", ratio_ids, "x1")
    n.add("id.ratio_max", "max", ratio_ids, "x1")
    n.add("id.all_truth_dist", "count_true", [f"id.dist.{r[len('id.ratio.'):]}" for r in ratio_ids], "int")
    n.add("id.n_truth", "count", ratio_ids, "int")
    n.f("id.null_splits", E_IDENT, ["null", "splits"], "int")
    n.f("id.null_mean", E_IDENT, ["null", "mean"], "+4")
    n.f("id.null_lo", E_IDENT, ["null", "q2.5"], "+4")
    n.f("id.null_hi", E_IDENT, ["null", "q97.5"], "+4")
    rows = []
    for name in ("D4d_n_up", "D4d_n_down", "R1_x1.05", "R1_x0.95", "R2_x1.01", "R2_x0.99", "R3_s0.10"):
        a = n.f(f"id.auc.{name}", E_IDENT, ["distortions", name, "auc_minus_half"], "+4")
        t = n.f(f"id.thr.{name}", E_IDENT, ["distortions", name, "threshold_ess_scaled"], "4")
        f_ = n.f(f"id.dist.{name}", E_IDENT, ["distortions", name, "distinguishable_vs_scaled_null"], "bool")
        rows.append([_tt(name), a, t, f_])
    body = rf"""
{{\small A reco-level two-sample classifier at the historical pseudodata size; null from
{n.r("id.null_splits")} equal-model splits: mean {n.r("id.null_mean")}, 95\,\% band
[{n.r("id.null_lo")}, {n.r("id.null_hi")}]. Fresh pool-T events.}}\par\vspace{{4pt}}
\begin{{columns}}[T]
\begin{{column}}{{0.47\linewidth}}
\small \textbf{{Every predeclared truth distortion is distinguishable}} ({n.r("id.all_truth_dist")} of
{n.r("id.n_truth")}), by {n.r("id.ratio_min")} to {n.r("id.ratio_max")} its own ESS-scaled threshold.
The weakest is D4d (neutron multiplicity), the hidden-variable test.\par\vspace{{4pt}}
The $\pm5\,\%$ hadronic scale (R1) is distinguishable. The $\pm1\,\%$ muon scale (R2) sits at or below
threshold and the cluster smearing (R3) is not distinguishable: \textbf{{unprobed at this size, not harmless}}.
\end{{column}}
\begin{{column}}{{0.5\linewidth}}
{table(["case", r"AUC$-\frac{1}{2}$", "threshold", "disting."], rows, "lrrc", r"\footnotesize")}
\end{{column}}
\end{{columns}}"""
    d.claim("Classifier null band", ["id.null_splits", "id.null_mean", "id.null_lo", "id.null_hi"])
    d.claim("Every predeclared truth distortion distinguishable, by min..max times its threshold",
            ["id.all_truth_dist", "id.n_truth", "id.ratio_min", "id.ratio_max"])
    for name in ("D4d_n_up", "D4d_n_down", "R1_x1.05", "R1_x0.95", "R2_x1.01", "R2_x0.99", "R3_s0.10"):
        d.claim(f"Identifiability of {name}", [f"id.auc.{name}", f"id.thr.{name}", f"id.dist.{name}"])
    d.frame("Robustness (1): what the data can distinguish", body, [E_IDENT])


def _eref(n: Numbers, nid: str, case: str, est: str, stat: str = "mean", k: str = "k3", fmt: str = "3") -> str:
    return n.f(nid, E_REFS, ["across_replicates", case, est, k, stat], fmt)


def slide_tradeoff(d: Deck, n: Numbers, out: Path) -> None:
    cases = [("D1_p0.350", r"$E_{\mathrm{avail}}$ tilt $+$ (development point)"),
             ("D1_m0.350", r"$E_{\mathrm{avail}}$ tilt $-$"),
             ("D4a_pipm_up", r"$\pi^\pm$ multiplicity up"),
             ("D5_nuwro", "NuWro generator reweighting"),
             ("D2_bump_c0.3", r"bump in $E_{\mathrm{avail}}$"),
             ("D4c_p_up", "proton multiplicity up")]
    ests = [("ibu/carry_misses", "IBU, misses carried", "ibu_carry"),
            ("ibu/efficiency_corrected", "IBU, eff.-corrected", "ibu_eff"),
            ("gbdt_omnifold", "GBDT OmniFold (carried)", "gbdt_carry")]
    rows = []
    for case, label in cases:
        row = [_tt(case) + " " + label]
        for est, _, _ in ests:
            tag = est.split("/")[-1]
            m = _eref(n, f"e.{case}.{tag}.k3", case, est)
            _eref(n, f"e.{case}.{tag}.k3.sd", case, est, "sd")
            row.append(m + (r" $\pm$ " + n.r(f"e.{case}.{tag}.k3.sd") if case in ("D1_p0.350", "D5_nuwro") else ""))
        rows.append(row)
    plt = _plt()
    f, ax = plt.subplots(figsize=(5.6, 2.9))
    w = 0.26
    for j, (est, lab_, sk) in enumerate(ests):
        tag = est.split("/")[-1]
        xs = [i + (j - 1) * w for i in range(len(cases))]
        ys = [n.v(f"e.{c}.{tag}.k3") for c, _ in cases]
        es = [n.v(f"e.{c}.{tag}.k3.sd") for c, _ in cases]
        ax.bar(xs, ys, width=w, yerr=es, capsize=2, color=STYLE[sk]["color"], label=lab_,
               hatch=None if "carry" in sk else "//", edgecolor="white", lw=0)
    ax.axhline(0, color="#444444", lw=0.8)
    _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f}")
    ax.set_xticks(range(len(cases)), [c for c, _ in cases], fontsize=6.5, rotation=15)
    ax.set_ylabel("recovery at $k=3$")
    ax.legend(loc="upper right", fontsize=6.5, ncol=3, bbox_to_anchor=(1.0, 1.12))
    _save(f, out / FIG_DIR / "miss_tradeoff.pdf")
    n.add("e.reps", "count", [(E_REFS, ["across_replicates", "D1_p0.350", "ibu/carry_misses", "k3", "values", i])
                              for i in range(len(n.src.get(E_REFS, ["across_replicates", "D1_p0.350", "ibu/carry_misses", "k3", "values"])))], "int")
    n.f("e.D1.ibu_carry_b1", B1, ["ibu", "muon_eavail/carry_misses/engine", "3", "aggregate"])
    n.f("e.D1.gbdt_b1", B1, ["omnifold", "muon_eavail/hgb", "by_iteration", "3", "aggregate", "mean"])
    body = rf"""
\begin{{columns}}[T]
\begin{{column}}{{0.5\linewidth}}
{table(["distortion ($k=3$)", "IBU carried", "IBU eff.-corr.", "GBDT"], rows, "p{2.5cm}rrr", r"\scriptsize")}\par\vspace{{4pt}}
{{\scriptsize Mean over {n.r("e.reps")} replicates on fresh pool-T events ($\pm$ sd where shown). The development-point
yardsticks transfer: B1's {n.r("e.D1.ibu_carry_b1")} / {n.r("e.D1.gbdt_b1")} on the historical halves.}}
\end{{column}}
\begin{{column}}{{0.49\linewidth}}
{fig("miss_tradeoff.pdf")}
\end{{column}}
\end{{columns}}
\vspace{{2pt}}
{{\small \textbf{{Efficiency correction is far ahead when the distortion is a function of the variables the
unfolder sees, and it fails --- moves away from the target --- when the distortion changes the event mix
inside a truth bin}}, because it extrapolates an acceptance that no longer holds. Carry-misses is slower
but does not fail that way. Neither mode is dominant: \textbf{{the choice is a model-dependence choice and must
be stated as one.}}}}"""
    for case, label in cases:
        d.claim(f"Phase E k=3 recovery under {case} ({label.replace('$', '')}): IBU carried, eff.-corrected, GBDT",
                [f"e.{case}.carry_misses.k3", f"e.{case}.efficiency_corrected.k3", f"e.{case}.gbdt_omnifold.k3"])
    d.claim("Development-point yardsticks transfer from B1", ["e.D1.ibu_carry_b1", "e.D1.gbdt_b1"])
    d.frame("Robustness (2): the miss-handling trade-off", body, [E_REFS, B1])


def slide_hidden_response(d: Deck, n: Numbers) -> None:
    ests = [("ibu", "carry_misses"), ("ibu", "efficiency_corrected"), ("gbdt_omnifold", None)]

    def proj_inputs(case: str) -> list:
        out = []
        reps = n.src.get(E_REFS, ["cases", case, "replicates"])
        for r in sorted(reps, key=int):
            for top, sub in ests:
                base = ["cases", case, "replicates", r, top] + ([sub] if sub else []) + ["iterations"]
                its = n.src.get(E_REFS, base)
                i3 = next(i for i, it in enumerate(its) if it["iteration"] == 3)
                out.append((E_REFS, base + [i3, "overshoot_projection"]))
        return out
    d4d = proj_inputs("D4d_n_up") + proj_inputs("D4d_n_down")
    d1 = proj_inputs("D1_p0.350")
    n.add("h.d4d_wrong", "count_lt0", d4d, "int")
    n.add("h.d4d_cells", "count", d4d, "int")
    n.add("h.d1_right", "count_gt0", d1, "int")
    n.add("h.d1_cells", "count", d1, "int")
    # response scale: R1 x1.05 / x0.95 combined with the development tilt
    shift_ids = []
    rows = []
    for est, label in (("ibu/carry_misses", "IBU, misses carried"), ("gbdt_omnifold", "GBDT OmniFold")):
        tag = est.split("/")[-1]
        base = _eref(n, f"r.{tag}.base", "D1_p0.350", est)
        up = _eref(n, f"r.{tag}.up", "R1_x1.05+D1_p0.350", est)
        dn = _eref(n, f"r.{tag}.dn", "R1_x0.95+D1_p0.350", est)
        n.add(f"r.{tag}.dup", "diff", [f"r.{tag}.up", f"r.{tag}.base"], "+3")
        n.add(f"r.{tag}.ddn", "diff", [f"r.{tag}.dn", f"r.{tag}.base"], "+3")
        shift_ids += [f"r.{tag}.dup", f"r.{tag}.ddn"]
        rows.append([label, base, f"{up} ({n.r(f'r.{tag}.dup')})", f"{dn} ({n.r(f'r.{tag}.ddn')})"])
    n.add("r.mean_abs_shift", "mean_abs", shift_ids, "2")
    n.f("r.margin", HIST, ["thresholds", "non_inferiority_delta"], "2")
    n.add("r.shift_over_margin", "ratio", ["r.mean_abs_shift", "r.margin"], "x1")
    body = rf"""
\textbf{{Hidden variable (D4d: neutron multiplicity up/down, invisible in $E_{{\mathrm{{avail}}}}$, visible to the
detector).}} Every estimator ends farther from the target than the untouched prior: the projection on the injected
direction is negative (the wrong way) in {n.r("h.d4d_wrong")} of {n.r("h.d4d_cells")} estimator $\times$ replicate
cells at $k=3$ (development tilt: positive in {n.r("h.d1_right")} of {n.r("h.d1_cells")}). This is the
hidden-variable limit any unfolding in these observables carries. That efficiency correction fails
\emph{{specifically}} worse here is \textbf{{not established}} at this sample size.\par\vspace{{6pt}}
\textbf{{Detector response.}} A $\pm5\,\%$ hadronic energy-scale error (R1) combined with the development tilt:
\begin{{center}}
{table(["estimator ($k=3$)", "same response", r"R1 $\times$1.05 ($\Delta$)", r"R1 $\times$0.95 ($\Delta$)"], rows, "lrrr", r"\footnotesize")}
\end{{center}}
Shifts average {n.r("r.mean_abs_shift")} in magnitude, {n.r("r.shift_over_margin")} the historical {n.r("r.margin")}
non-inferiority margin. Same-response closure cannot see this: \textbf{{any candidate's recovery statement is
conditional on the simulated response.}}"""
    d.claim("D4d: wrong-way projection count vs development tilt", ["h.d4d_wrong", "h.d4d_cells", "h.d1_right", "h.d1_cells"])
    d.claim("R1 +/-5% hadronic scale shifts recovery by about 3x the non-inferiority margin",
            shift_ids + ["r.mean_abs_shift", "r.margin", "r.shift_over_margin", "r.carry_misses.base", "r.gbdt_omnifold.base"])
    d.frame("Robustness (3): hidden variable and response scale", body, [E_REFS, HIST])


# --------------------------------------------------------------------------- confirmatory
LABELS = ("CTL", "A", "B@3", f"B@{KSTAR}", "C@3", f"C@{KSTAR}")
LABEL_TEXT = {"CTL": "CTL (hist. recipe, $k=3$)", "A": f"A (same run, $K^*={KSTAR}$)",
              "B@3": "B (C2 inputs), $k=3$", f"B@{KSTAR}": f"B (C2 inputs), $K^*={KSTAR}$",
              "C@3": "C (eff.-corr.), $k=3$", f"C@{KSTAR}": f"C (eff.-corr.), $K^*={KSTAR}$"}


def _pilot_block(d: Deck, n: Numbers, out: Path, size: str = r"\scriptsize") -> str:
    obs = n.src.get(CONFIRM, ["pilot", "observations"])
    reps = sorted({int(r) for lab in obs.values() for r in lab})
    rows = []
    for lab in LABELS:
        row = [LABEL_TEXT[lab]]
        for rep in reps:
            if str(rep) in obs.get(lab, {}):
                row.append(n.f(f"p.{lab}.P{rep}", CONFIRM, ["pilot", "observations", lab, str(rep), "R"]))
            else:
                row.append("---")
        rows.append(row)
    orow = ["oracle anchor"]
    for rep in reps:
        orow.append(n.f(f"p.oracle.P{rep}", CONFIRM, ["pilot", "oracle", str(rep)]))
    rows.append(orow)
    n.f("p.n_final", CONFIRM, ["pilot", "sizing", "n_final"], "int")
    n.f("p.n_uncapped", CONFIRM, ["pilot", "sizing", "n_uncapped"], "int")
    d.claim("PILOT recovery per replicate (reported separately; never enters FINAL)",
            [f"p.{lab}.P{rep}" for lab in LABELS for rep in reps if str(rep) in obs.get(lab, {})])
    d.claim("FINAL sized from the PILOT", ["p.n_final", "p.n_uncapped"])
    # figure
    plt = _plt()
    f, ax = plt.subplots(figsize=(4.6, 2.6))
    colour = {"CTL": "pet_H", "A": "pet_H", "B@3": "pet_C2", f"B@{KSTAR}": "pet_C2", "C@3": "pet_M", f"C@{KSTAR}": "pet_M"}
    for x, lab in enumerate(LABELS):
        ys = [n.v(f"p.{lab}.P{rep}") for rep in reps if str(rep) in obs.get(lab, {})]
        st = STYLE[colour[lab]]
        ax.plot([x] * len(ys), ys, ls="", marker=st["marker"], color=st["color"], ms=5,
                mfc="none" if "3" in lab or lab == "CTL" else st["color"])
    _floor(ax, n.v("hist.floor"), f"historical floor {n.v('hist.floor'):.3f}")
    ax.set_xticks(range(len(LABELS)), [l.replace("@", " k=") for l in LABELS], fontsize=7)
    ax.set_ylabel("recovery (pilot replicate)")
    ax.set_ylim(0, 1)
    _save(f, out / FIG_DIR / "confirm_pilot.pdf")
    return table(["PILOT, pool P"] + [f"P{r}" for r in reps], rows, "l" + "r" * len(reps), size)


def slide_confirm(d: Deck, n: Numbers, out: Path) -> tuple[bool, bool]:
    has_file = n.src.exists(CONFIRM)
    doc = n.src.load(CONFIRM) if has_file else {}
    has_final = bool(doc.get("final"))
    has_stress = bool(doc.get("stress"))
    design = (r"Frozen before any fresh-pool row was read (protocol amendment 2): "
              r"\textbf{CTL} = historical recipe at $k=3$; \textbf{A} = the same run at $K^*=10$ (iterations alone); "
              r"\textbf{B} = C2 inputs at $K^*$ (carry-misses); \textbf{C} = efficiency-corrected step 2 at $K^*$. "
              r"Adequacy judged like-for-like at $k=3$ and at $K^*$ against the unchanged historical floors.")
    if not has_final:
        pilot = ""
        if has_file and doc.get("pilot"):
            pilot = rf"""
\begin{{columns}}[T]
\begin{{column}}{{0.55\linewidth}}
{_pilot_block(d, n, out)}\par\vspace{{2pt}}
{{\scriptsize FINAL sized from these at $n={n.r("p.n_final")}$ (uncapped {n.r("p.n_uncapped")}; capped by pool F).}}
\end{{column}}
\begin{{column}}{{0.43\linewidth}}
{fig("confirm_pilot.pdf")}
\end{{column}}
\end{{columns}}
{{\scriptsize \textbf{{PILOT observations are not confirmatory.}} They size FINAL and are reported separately;
they never enter the FINAL interval, and no decision is drawn from them.}}"""
        body = rf"""
\begin{{alertblock}}{{Confirmatory results pending}}
The FINAL comparison (fresh pool F, $n$ independent replicates) has not been harvested into
\texttt{{confirm\_results.json}}{"" if has_file else " (the file is absent)"}. No confirmatory decision,
superiority, non-inferiority or adequacy statement is made in this deck.
\end{{alertblock}}
{{\small {design}}}
{pilot}"""
        d.frame("The confirmatory result: pending", body, [CONFIRM])
        return has_final, has_stress
    dec = doc["final"]["decisions"]
    rows = []
    claim_ids = []
    for kk in (f"K={KSTAR}", "K=3"):
        block = dec["tests"].get(kk, {})
        est = block.get("superiority", {}).get("estimates", {})
        for c in ("A", "B", "C"):
            if c not in est:
                continue
            base = ["final", "decisions", "tests", kk]
            m = n.f(f"fin.{kk}.{c}.mean", CONFIRM, base + ["superiority", "estimates", c, "mean"], "+3")
            lo = n.f(f"fin.{kk}.{c}.lcb", CONFIRM, base + ["superiority", "estimates", c, "lower_95_one_sided"], "+3")
            nn = n.f(f"fin.{kk}.{c}.n", CONFIRM, base + ["superiority", "estimates", c, "n"], "int")
            cells = []
            for t in ("superiority", "non_inferiority", "switching"):
                cells.append(n.f(f"fin.{kk}.{c}.{t}", CONFIRM, base + [t, "holm", c, "reject_H0"], "bool"))
            claim_ids += [f"fin.{kk}.{c}.mean", f"fin.{kk}.{c}.lcb", f"fin.{kk}.{c}.n"] + [f"fin.{kk}.{c}.{t}" for t in ("superiority", "non_inferiority", "switching")]
            rows.append([f"{c} vs CTL, {kk.replace('K=', '$k=')}$", nn, m, lo] + cells)
    arows = []
    for lab, a in dec["adequacy"].items():
        base = ["final", "decisions", "adequacy", lab]
        ids = [n.f(f"fin.adq.{lab}.mean", CONFIRM, base + ["mean"]),
               n.f(f"fin.adq.{lab}.lcb", CONFIRM, base + ["lower_95"])]
        for r in REGIONS:
            ids.append(n.f(f"fin.adq.{lab}.{r}", CONFIRM, base + ["regions", r, "mean"]))
        ids.append(n.f(f"fin.adq.{lab}.adequate", CONFIRM, base + ["adequate"], "bool"))
        claim_ids += [f"fin.adq.{lab}.{x}" for x in ("mean", "lcb", *REGIONS, "adequate")]
        arows.append([LABEL_TEXT.get(lab, esc(lab))] + ids)
    n.f("fin.floor", CONFIRM, ["final", "decisions", "floors", "aggregate"], "3")
    body = rf"""
{{\scriptsize {design}}}\par\vspace{{3pt}}
{{\small Decision inequalities vs CTL, one-sided $\alpha=0.05$, Holm across A, B, C (``yes'' = null rejected):}}
\begin{{center}}
{table(["candidate", "$n$", "mean diff.", "lower 95\\,\\%", "superior", "non-inf.", "switch"], rows, "lrrrccc", r"\scriptsize")}
\end{{center}}
{{\small Adequacy against the historical floors, imported unchanged (aggregate floor {n.r("fin.floor")}):}}
\begin{{center}}
{table(["estimator", "mean", "lower 95\\,\\%", "low", "moderate", "good", "adequate"], arows, "lrrrrrc", r"\scriptsize")}
\end{{center}}"""
    d.claim("FINAL decision inequalities and adequacy (pool F)", claim_ids + ["fin.floor"])
    d.frame("The confirmatory result (FINAL, pool F)", body, [CONFIRM])
    return has_final, has_stress


def slide_stress(d: Deck, n: Numbers) -> None:
    st = n.src.get(CONFIRM, ["stress"])
    rows, ids = [], []
    for case in sorted(st):
        row = [_tt(case)]
        for lab in LABELS:
            cell = st[case].get(lab, {})
            if not cell:
                row.append("---")
                continue
            reps = sorted(cell, key=int)
            m = n.add(f"st.{case}.{lab}", "mean", [(CONFIRM, ["stress", case, lab, r, "R"]) for r in reps], "3")
            away = n.add(f"st.{case}.{lab}.away", "any_true",
                         [(CONFIRM, ["stress", case, lab, r, "moves_away", "replicate_target"]) for r in reps], "bool")
            ids += [f"st.{case}.{lab}", f"st.{case}.{lab}.away"]
            row.append(m + ("$^\\dagger$" if n.v(f"st.{case}.{lab}.away") else ""))
        rows.append(row)
    body = rf"""
{{\small PET stress set on fresh pool-T events (protocol amendment 2): mean recovery over replicates;
$^\dagger$ = the estimator ends farther from the target than the untouched prior on some replicate
(``moves away'' --- reported as \textbf{{not robust}} where the distortion is identifiable).}}
\begin{{center}}
{table(["case"] + [LABEL_TEXT[l] for l in LABELS], rows, "l" + "r" * len(LABELS), r"\tiny")}
\end{{center}}"""
    d.claim("PET stress set: mean recovery and moves-away flags per case and estimator", ids)
    d.frame("The confirmatory result (STRESS, pool T)", body, [CONFIRM])


def slide_cannot(d: Deck, n: Numbers) -> None:
    verdict = esc(n.src.get(HIST, ["verdict"]))
    rec = esc(n.src.get(HIST, ["recommendation"]))
    body = rf"""
\begin{{alertblock}}{{A terminal result of this campaign cannot authorize}}
\begin{{itemize}}
\item adoption of any estimator for publication;
\item a change to the historical comparison's verdict (\texttt{{{verdict} / {rec}}}, preserved) or to its thresholds;
\item $C_{{\mathrm{{stat}}}}$ / $C_{{\mathrm{{ML}}}}$ or any uncertainty product, any systematic, any central-value change,
any Gate-6 action;
\item any real-data unfolding.
\end{{itemize}}
\end{{alertblock}}
Recalibrated references and recommended configurations are \textbf{{prospective recommendations only}}.
Every result in this deck is from simulation: pseudodata built from signal Monte Carlo with a known
injected truth.\par\vspace{{6pt}}
\textbf{{Scope.}} {SCOPE}"""
    d.frame("What a terminal result cannot authorize", body, ["PROTOCOL-20260922.md \\S 1", HIST])


def slide_limits(d: Deck, n: Numbers, has_final: bool) -> None:
    n.f("lim.h4_sd", B2, ["recovery_by_k", "b2e1-H-K3", "3", "sd"], "2")
    n.f("lim.h4_n", B2, ["recovery_by_k", "b2e1-H-K3", "3", "n"], "int")
    n.f("lim.h4_mean", B2, ["recovery_by_k", "b2e1-H-K3", "3", "mean"], "3")
    conf = ("the FINAL decisions are on the previous slide; coverage runs only for a candidate adequate at "
            "$K^*$ that does not move away on any identifiable stress case"
            if has_final else
            "the FINAL comparison and the PET stress set are pending; until they land, every candidate statement "
            "above is development-stage evidence on the DEV halves")
    body = rf"""
\textbf{{Limitations}}
\begin{{itemize}}\small
\item DEV-stage PET results rest on {n.r("b2.H.k10.n")} seeds per arm. The repaired driver reproduces the historical recipe
({n.r("lim.h4_mean")} over {n.r("lim.h4_n")} seeds, sd {n.r("lim.h4_sd")}); effects below about that spread are
reported as unresolved, not as nulls.
\item Recovery statements are conditional on the simulated detector response (R1 moves them by more than the
margins) and cannot see hidden variables (D4d).
\item Efficiency correction needs a stopping rule and a variance statement, not only a mean recovery.
\item Coverage has not been run: protocol \S 7 reserves it for a candidate adequate or best-in-class on FINAL.
\end{{itemize}}
\textbf{{Next choice}}
\begin{{itemize}}\small
\item Confirmatory status: {conf}.
\item The miss rule is a model-dependence choice (carry-misses: slower, does not move away; efficiency
correction: faster, fails when the event mix inside a truth bin changes). Whichever is recommended must be
stated as that choice.
\item A reference computed for the estimator's own miss rule and normalization, on the scored spectrum, is a
prospective recommendation to be checked on a known-function toy before use.
\end{{itemize}}
{{\small {SCOPE}}}"""
    d.claim("Driver reproduces the historical recipe; spread sets the resolution",
            ["lim.h4_mean", "lim.h4_n", "lim.h4_sd"])
    d.frame("Limitations and the next choice", body, [B2, CONFIRM])


# --------------------------------------------------------------------------- appendix
def appx_audit_more(d: Deck, n: Numbers) -> None:
    S = ["summary"]
    ft = n.f("ax.fits_theirs", A_HIST, S + ["final/theirs", "fits"], "int")
    fo = n.f("ax.fits_ours", A_HIST, S + ["final/ours", "fits"], "int")
    lt = n.f("ax.last_theirs", A_HIST, S + ["final/theirs", "fits_whose_val_loss_argmin_is_last_epoch"], "int")
    lo = n.f("ax.last_ours", A_HIST, S + ["final/ours", "fits_whose_val_loss_argmin_is_last_epoch"], "int")
    ep = n.f("ax.epochs", A_HIST, S + ["final/ours", "epochs_run", 0], "int")
    lr = n.r("ax.lr_after0")
    pre = ["fits", 0, "at_first_optimizer_step", "pretrained"]
    eq = n.f("ax.pre_equal", A_THEIRS, pre + ["exactly_equal"], "int")
    tot = n.f("ax.pre_total", A_THEIRS, pre + ["tensors_in_state"], "int")
    body = rf"""
\begin{{itemize}}\small
\item Every fit after iteration 0 ran at a forced learning rate ({lr}), so the tuned rate governed iteration 0 only.
\item Early stopping was inert against {ep} epochs: each fit handed on its \textbf{{last-epoch}} weights, while the
validation-loss minimum was the last epoch in only {lt} of {ft} final-stage fits for his arm and {lo} of {fo} for ours.
\item Step 1 normalizes each class to a fixed total, discarding the physical class ratio.
\item The step-2 truth cloud feeds \textbf{{raw PDG codes}} as a continuous column into Dense layers and the $k$-NN features.
\item \textbf{{Not defective:}} his pretrained weights survive cloning exactly ({eq} of {tot} tensors at the first
optimizer step); his token features are the converted $\eta/\phi/\log p_T/\log E$ set.
\end{{itemize}}"""
    d.claim("Forced learning rate after iteration 0", ["ax.lr_after0"])
    d.claim("Last-epoch hand-on vs val-loss argmin", ["ax.fits_theirs", "ax.fits_ours", "ax.last_theirs", "ax.last_ours", "ax.epochs"])
    d.claim("Pretrained weights survive cloning exactly", ["ax.pre_equal", "ax.pre_total"])
    d.frame("Appendix: other executed facts (Phase A)", body, [A_HIST, A_THEIRS])


def appx_scaling_full(d: Deck, n: Numbers) -> None:
    runs = n.src.get(D_SCALE, ["runs"])
    g = _group_runs(runs, lambda r: (r["exp"], r["method"], r["miss_handling"], r["k_or_lambda"],
                                     r["prior_size"], r["data_size"]))
    prior_sizes = sorted({r["prior_size"] for r in runs if r["exp"] == "vary_prior"})
    full_data = max(r["data_size"] for r in runs if r["exp"] == "vary_prior")
    lab = lambda s: f"{round(s / 1000)}k"
    rows = []
    for tag, label, key in (("eff3", "OmniFold eff.-corrected, $k=3$", ("OmniFold", "efficiency_corrected", 3)),
                            ("aussie1000", r"AUSSIE, $\lambda=1000$ (misses pinned)", ("AUSSIE", "lambda=1000", 1000))):
        row = [label]
        for ps in prior_sizes:
            idx = g[("vary_prior", *key, ps, full_data)]
            m = n.add(f"d.prior.{tag}.{ps}", "mean", [(D_SCALE, ["runs", i, "aggregate"]) for i in idx], "3")
            s = n.add(f"d.prior.{tag}.{ps}.sd", "sd", [(D_SCALE, ["runs", i, "aggregate"]) for i in idx], "3")
            row.append(f"{m} $\\pm$ {s}")
        rows.append(row)
    for tag, label in (("carry3", "OmniFold carry-misses, $k=3$"), ("carry20", "OmniFold carry-misses, $k=20$"),
                       ("eff20", "OmniFold eff.-corrected, $k=20$"), ("aussie0", r"AUSSIE, $\lambda=0$")):
        rows.append([label] + [f"{n.r(f'd.prior.{tag}.{ps}')} $\\pm$ {n.r(f'd.prior.{tag}.{ps}.sd')}" for ps in prior_sizes])
    body = rf"""
{{\small Prior-MC size axis, mean $\pm$ sd over draws (Phase D, development stage):}}
\begin{{center}}
{table(["estimator"] + [lab(p) for p in prior_sizes], rows, "l" + "r" * len(prior_sizes), r"\scriptsize")}
\end{{center}}
{{\small The efficiency-corrected and AUSSIE curves are flat in prior size: the signature of an estimator limited
by its extrapolation assumption rather than by statistics.}}"""
    d.claim("Phase D full prior-size table (eff.-corrected k=3, AUSSIE lambda=1000)",
            [f"d.prior.{t}.{ps}" for t in ("eff3", "aussie1000") for ps in prior_sizes])
    d.frame("Appendix: Phase D, all prior-size curves", body, [D_SCALE])


def appx_phase_e_full(d: Deck, n: Numbers) -> None:
    across = n.src.get(E_REFS, ["across_replicates"])
    cases = [c for c in sorted(across) if n.src.get(E_REFS, ["cases", c, "predeclared"]) and not c.startswith("R")
             or c.startswith("R1_") and "+" in c]
    rows = []
    for case in cases:
        row = [_tt(case)]
        for est in ("ibu/carry_misses", "ibu/efficiency_corrected", "gbdt_omnifold"):
            tag = est.split("/")[-1]
            for k in ("k3", "k10"):
                row.append(n.f(f"ea.{case}.{tag}.{k}", E_REFS, ["across_replicates", case, est, k, "mean"], "2"))
        rows.append(row)
    body = rf"""
{{\small Predeclared truth distortions and R1 combined with the development tilt; mean recovery over {n.r("e.reps")} replicates,
fresh pool-T events.}}
\begin{{center}}
{table(["case", "IBU carried $k$=3", "$k$=10", "IBU eff. $k$=3", "$k$=10", "GBDT $k$=3", "$k$=10"], rows, "lrrrrrr", r"\tiny")}
\end{{center}}"""
    d.claim("Phase E full table (predeclared cases)", [f"ea.{c}.{e}.{k}" for c in cases
                                                       for e in ("carry_misses", "efficiency_corrected", "gbdt_omnifold")
                                                       for k in ("k3", "k10")])
    d.frame("Appendix: Phase E scalar yardsticks, all predeclared cases", body, [E_REFS])


def appx_pilot(d: Deck, n: Numbers, out: Path) -> None:
    block = _pilot_block(d, n, out, r"\footnotesize")
    body = rf"""
{{\small PILOT (pool P) --- reported separately; never enters the FINAL interval; sizes FINAL only.}}
\begin{{center}}
{block}
\end{{center}}
{{\small FINAL sized at $n={n.r("p.n_final")}$ (uncapped {n.r("p.n_uncapped")}).}}"""
    d.frame("Appendix: PILOT (not confirmatory)", body, [CONFIRM])


def appx_provenance(d: Deck, n: Numbers) -> None:
    rows = [[_tt(rel), r"\texttt{" + sha[:16] + "}"] for rel, sha in sorted(n.src.sha.items())
            if not rel.startswith("phase_b/pet/results/b2e")]
    runs = sorted(rel for rel in n.src.sha if rel.startswith("phase_b/pet/results/b2e"))
    body = rf"""
{{\small Every number in this deck is read from these committed files by
\texttt{{slides/make\_campaign\_deck.py}}; \texttt{{slides/deck\_numbers.json}} records the field (or derivation)
behind each, and \texttt{{slides/CLAIM\_INDEX-deck.md}} maps every claim to them. Paths relative to
\texttt{{nd-unfolding/pet/improvement\_campaign/}}; sha256 prefixes.}}
\begin{{center}}
{table(["file", "sha256"], rows, "ll", r"\tiny")}
\end{{center}}
{{\tiny Plus {len(runs)} per-run PET score files under \texttt{{phase\_b/pet/results/}} (hashes in
\texttt{{deck\_numbers.json}}).}}"""
    d.frame("Appendix: evidence files", body, ["slides/deck_numbers.json"])


# =========================================================================== assembly
PREAMBLE = r"""\documentclass[aspectratio=169,10pt]{beamer}
\usetheme{default}
\usecolortheme{dove}
\setbeamertemplate{navigation symbols}{}
\usepackage{booktabs}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\setbeamerfont{block body}{size=\small}
\def\evidencetext{}
\setbeamertemplate{footline}{%
  \leavevmode\hbox to \paperwidth{\hspace{0.4cm}\parbox[b]{0.86\paperwidth}{\raggedright\tiny\color{gray}%
  \ifx\evidencetext\empty\else Evidence: \evidencetext\fi}\hfill{\tiny\color{gray}\insertframenumber}\hspace{0.4cm}}\vspace{0.18cm}}
"""


def build(out: Path, confirm_override: Path | None, make_pdf: bool) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    (out / FIG_DIR).mkdir(exist_ok=True)
    overrides = {CONFIRM: confirm_override} if confirm_override else {}
    src = Sources(CAMPAIGN, overrides)
    n = Numbers(src)
    d = Deck(n)
    # historical numbers are needed by nearly every slide; register first
    slide_title(d, n)
    slide_historical(d, n)
    slide_audit(d, n)
    slide_scalar(d, n, out)
    slide_stepwise(d, n, out)
    slide_levers(d, n, out)
    slide_features(d, n)
    slide_aussie(d, n)
    slide_scaling(d, n, out)
    slide_reference_decomp(d, n, out)
    slide_reference_gap(d, n)
    slide_identifiability(d, n)
    slide_tradeoff(d, n, out)
    slide_hidden_response(d, n)
    has_final, has_stress = slide_confirm(d, n, out)
    if has_stress:
        slide_stress(d, n)
    slide_cannot(d, n)
    slide_limits(d, n, has_final)
    main_slides = d.main_count
    d.appendix()
    appx_audit_more(d, n)
    appx_scaling_full(d, n)
    appx_phase_e_full(d, n)
    if has_final and src.load(CONFIRM).get("pilot"):
        appx_pilot(d, n, out)
    appx_provenance(d, n)

    title = (r"\title{PET recovery: diagnosis and improvement campaign}" "\n"
             r"\subtitle{Campaign comparison deck, version 2 (generated from committed results)}" "\n"
             r"\author{PET improvement campaign}" "\n"
             r"\date{\parbox{0.8\linewidth}{\centering\small " + SCOPE + r"}}" "\n")
    tex = PREAMBLE + title + "\n\\begin{document}\n\n" + "\n".join(d.frames) + "\n\\end{document}\n"
    (out / TEX_NAME).write_text(tex)

    record = {
        "schema": "pet-campaign-deck-numbers/1",
        "generator": "slides/make_campaign_deck.py",
        "root": "nd-unfolding/pet/improvement_campaign",
        "confirm": {"file_present": src.exists(CONFIRM), "final_present": has_final,
                    "stress_present": has_stress},
        "main_slides": main_slides,
        "sources": {rel: src.sha[rel] for rel in sorted(src.sha)},
        "numbers": [n.entries[k] for k in sorted(n.entries)],
    }
    (out / "deck_numbers.json").write_text(json.dumps(record, indent=1, sort_keys=False) + "\n")
    (out / "CLAIM_INDEX-deck.md").write_text(claim_index(d, n, has_final))
    if make_pdf:
        compile_pdf(out)
    return record


def claim_index(d: Deck, n: Numbers, has_final: bool) -> str:
    def where(e: dict) -> str:
        parts = []
        for i in e["inputs"]:
            if isinstance(i, str):
                parts.append(f"= `{i}`")
            else:
                path = "".join(f"[{p!r}]" if isinstance(p, str) else f"[{p}]" for p in i["path"])
                parts.append(f"`{i['file']}` `{path}`")
        head = "" if e["op"] == "field" else f"**{e['op']}** of "
        if len(parts) > 4:
            parts = parts[:3] + [f"... ({len(e['inputs'])} inputs; full list in `deck_numbers.json`)"]
        return head + "; ".join(parts)

    lines = ["# Claim index — campaign comparison deck v2",
             "",
             "Generated by `make_campaign_deck.py` together with `campaign_comparison_v2.tex` and",
             "`deck_numbers.json`; do not edit by hand. Every claim in the deck, the numbers it rests on, and the",
             "committed field each number was read from (or the derivation over such fields). Paths are relative",
             "to `nd-unfolding/pet/improvement_campaign/`.",
             "",
             f"Confirmatory FINAL section present when generated: **{'yes' if has_final else 'no (pending slide rendered)'}**.",
             "",
             f"**Scope.** {SCOPE}",
             "",
             "| slide | claim | number id = rendered | source |",
             "|---:|---|---|---|"]
    for c in d.claims:
        for j, nid in enumerate(c["ids"]):
            e = n.entries[nid]
            rendered = (e["rendered"].replace(r"\ensuremath{-}", "−").replace(r"\ensuremath{\times}", "×")
                        .replace(r"\ensuremath", "").replace("\\,\\%", " %"))
            rendered = rendered.replace("$", "").replace("\\times", "×").replace("{", "").replace("}", "")
            lines.append(f"| {c['slide'] if j == 0 else ''} | {c['text'] if j == 0 else ''} | "
                         f"`{nid}` = {rendered} | {where(e)} |")
    return "\n".join(lines) + "\n"


def compile_pdf(out: Path) -> None:
    for _ in range(2):
        proc = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX_NAME],
                              cwd=out, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout[-4000:])
            raise RuntimeError("pdflatex failed")
    for ext in (".aux", ".log", ".nav", ".out", ".snm", ".toc", ".vrb"):
        p = out / TEX_NAME.replace(".tex", ext)
        if p.exists():
            p.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", type=Path, default=HERE)
    ap.add_argument("--confirm", type=Path, default=None,
                    help="alternative confirm_results.json (tests); default: the committed one if present")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()
    rec = build(args.out_dir.resolve(), args.confirm, not args.no_pdf)
    print(f"main slides: {rec['main_slides']}; numbers: {len(rec['numbers'])}; "
          f"confirm: {rec['confirm']}")


if __name__ == "__main__":
    main()
