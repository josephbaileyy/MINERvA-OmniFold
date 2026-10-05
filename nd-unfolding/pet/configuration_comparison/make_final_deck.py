"""Render the final comparison deck from `campaign_report.json`. Nothing by hand.

Every number on a slide is read from the report, and the component comparison is
EXTRACTED from `CONFIGURATION_COMPARISON-20260918.md` rather than retyped: that
document is the pinned twelve-category comparison and a second copy of it in
slide form would be a second thing to keep true.

The deck states its own scope on the first frame and the last. PET is diagnostic
method development; a deck that reads like an adoption proposal would be wrong
about what it is even if every number in it were right.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
COMPARISON = HERE / "CONFIGURATION_COMPARISON-20260918.md"
EXPECTED_CATEGORIES = 12


def tex_escape(text: str) -> str:
    """Markdown fragment to LaTeX. Code, bold and italic survive; specials escape.

    Emphasis is resolved RECURSIVELY. `**a *b* c**` is ordinary markdown and the
    first version of this matched bold with `[^*]+`, which silently declined the
    whole span -- the row reached pdflatex with its asterisks intact and failed
    two hundred lines into a log.
    """
    spans: list[str] = []

    def stash(fmt: str, recurse: bool):
        def repl(match: re.Match) -> str:
            inner = match.group(1)
            spans.append(fmt % (tex_escape(inner) if recurse
                                else _escape_plain(inner)))
            return f"\0{len(spans) - 1}\0"
        return repl

    # Code spans first, so `**` inside backticks stays literal.
    text = re.sub(r"`([^`]+)`", stash(r"\texttt{%s}", False), text)
    text = re.sub(r"\*\*(.+?)\*\*", stash(r"\textbf{%s}", True), text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", stash(r"\emph{%s}", True), text)
    text = _escape_plain(text)
    return re.sub(r"\0(\d+)\0", lambda m: spans[int(m.group(1))], text)


# LaTeX specials, then every non-ASCII character this project's prose actually
# uses. Anything NOT in the map raises: pdflatex cannot set it and would fail
# deep in a log, so a new character is added here deliberately rather than
# discovered by a broken build.
_SPECIALS = (
    ("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
    ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
    ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
)
_UNICODE = {
    0x00a0: "~", 0x00b0: r"$^\circ$", 0x00b1: r"$\pm$", 0x00b7: r"$\cdot$",
    0x00d7: r"$\times$", 0x2009: r"\,", 0x2013: "--", 0x2014: "---",
    0x2018: "`", 0x2019: "'", 0x201c: "``", 0x201d: "''", 0x2026: r"\ldots{}",
    0x2192: r"$\to$", 0x2212: "$-$", 0x2229: r"$\cap$", 0x2208: r"$\in$",
    0x2209: r"$\notin$", 0x2248: r"$\approx$", 0x2264: r"$\leq$",
    0x2265: r"$\geq$",
    0x03b1: r"$\alpha$", 0x03b2: r"$\beta$", 0x03b3: r"$\gamma$",
    0x0393: r"$\Gamma$", 0x03b4: r"$\delta$", 0x03b7: r"$\eta$",
    0x03bc: r"$\mu$", 0x03c0: r"$\pi$", 0x03c3: r"$\sigma$",
    0x03c4: r"$\tau$", 0x03c6: r"$\varphi$", 0x03d5: r"$\phi$",
    0x03bd: r"$\nu$", 0x03bb: r"$\lambda$", 0x03a3: r"$\Sigma$",
}


def _escape_plain(text: str) -> str:
    for src, dst in _SPECIALS:
        text = text.replace(src, dst)
    out = []
    unmapped = []
    for char in text:
        code = ord(char)
        if code < 128:
            out.append(char)
        elif code in _UNICODE:
            out.append(_UNICODE[code])
        else:
            unmapped.append((char, hex(code)))
    if unmapped:
        raise ValueError(
            f"unmapped non-ASCII {unmapped} in {text!r}. pdflatex cannot set "
            "these; add them to _UNICODE deliberately"
        )
    return "".join(out)


def component_comparison(path: Path = COMPARISON) -> list[dict[str, str]]:
    """The twelve categories and their recommendations, read from the pinned doc.

    Exactly `EXPECTED_CATEGORIES` must be found. A silent 11 would drop a
    component from a comparison the deck calls complete, and "complete" is the
    word the deliverable uses.
    """
    text = path.read_text()
    headings = [(m.start(), int(m.group(1)), m.group(2).strip())
                for m in re.finditer(r"^## (\d+)\. (.+)$", text, re.M)]
    rows = []
    for index, (start, number, title) in enumerate(headings):
        if not 1 <= number <= EXPECTED_CATEGORIES:
            continue
        end = headings[index + 1][0] if index + 1 < len(headings) else len(text)
        block = text[start:end]
        rec = re.search(r"^\| \*\*recommendation\*\* \| (.+?) \|\s*$", block, re.M)
        if rec is None:
            raise ValueError(f"category {number} ({title}) has no recommendation row")
        rows.append({"number": str(number), "title": title,
                     "recommendation": rec.group(1).strip()})
    if len(rows) != EXPECTED_CATEGORIES:
        raise ValueError(
            f"found {len(rows)} categories in {path.name}, expected "
            f"{EXPECTED_CATEGORIES}. A deck that calls the comparison complete "
            "cannot be built from a partial read of it"
        )
    return rows


# --------------------------------------------------------------------------- #
def _headline(report: dict[str, Any]) -> tuple[str, str]:
    """The one sentence the deck exists to deliver, and its qualification."""
    verdict, rec = report["verdict"], report["recommendation"]
    if rec == "NO_SELECTION":
        return ("No adequate arm.",
                "Neither configuration cleared the predeclared safeguards, so "
                "this comparison recommends neither. That is a result, not a "
                "failure to produce one.")
    arm = "our incumbent" if rec == "ADOPT_OURS" else "Gregor's pretrained PET2-small"
    if report.get("retained_ours_though_theirs_scored_better"):
        return (f"Keep {arm}, though his arm scored better.",
                "His configuration recovered more of the injected displacement. "
                "Ours is retained because the difference did not reach the "
                "predeclared switching threshold. "
                "\\textbf{Non-inferiority is not superiority.}")
    if verdict == "INCONCLUSIVE":
        return ("Inconclusive at the predeclared margin.",
                "The interval does not separate the arms at the frozen "
                "$\\delta$, and the margin was not widened to obtain a decision.")
    return (f"Recommend {arm}.",
            f"Verdict \\texttt{{{_escape_plain(verdict)}}} under the rule frozen "
            "before any comparative result existed.")


def build_tex(report: dict[str, Any], categories: list[dict[str, str]]) -> str:
    interval = report["interval"]
    adequacy = report["absolute_adequacy"]
    band = report["low_acceptance"]
    scope = report["scope"]
    prov = report.get("provenance", {})
    # Computed HERE, not inside the f-string: `{{}}` in an f-string EXPRESSION is
    # a set containing an empty dict, not an empty dict, and it raises at render
    # time rather than at import.
    # Does the interval actually resolve the margin it is judged against?
    # The pilot said 74 pairs were needed for a half-width within delta and
    # the design runs 8, so the honest statement is that the comparison
    # resolves DIRECTION but not non-inferiority to delta. A reader should not
    # have to divide two numbers on the slide to find that out.
    half_width = float(interval["half_width"])
    delta = float(report["thresholds"]["non_inferiority_delta"])
    resolves_delta = half_width <= delta
    precision_note = (
        "The interval is narrower than $\\delta$, so non-inferiority is "
        "resolvable at the frozen margin."
        if resolves_delta else
        f"\\textbf{{The interval is wider than $\\delta$}} "
        f"({half_width:.4f} against {delta}). This comparison resolves the "
        "DIRECTION of the difference, not non-inferiority at the frozen "
        "margin; the margin was not widened to change that.")
    off_grid_pct = 100.0 * (
        report.get("regional_coverage", {}).get("off_grid_truth_fraction") or 0.0)
    closure_sha = str(prov.get("closure_npz", {}).get("sha256", "---"))
    headline, qualification = _headline(report)

    def num(value, digits=4, signed=False):
        if value is None:
            return "---"
        return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"

    regional_rows = "\n".join(
        rf"{tex_escape(name)} & {num(report['mean_recovery_by_region']['ours'][name])} & "
        rf"{num(report['mean_recovery_by_region']['theirs'][name])} & "
        rf"{num(report['regional_safeguard']['floor_by_region'][name])} \\"
        for name in report["regional_safeguard"]["scoreable_regions"])

    category_rows = "\n".join(
        rf"{row['number']} & {tex_escape(row['title'])} & "
        rf"{tex_escape(row['recommendation'])} \\" for row in categories)

    per_seed = "\n".join(
        rf"{seed} & {num(value, signed=True)} \\"
        for seed, value in sorted(report["paired_differences"].items(),
                                  key=lambda kv: int(kv[0])))

    return rf"""\documentclass[aspectratio=169,10pt]{{beamer}}
\usetheme{{default}}
\usecolortheme{{dove}}
\setbeamertemplate{{navigation symbols}}{{}}
\setbeamertemplate{{footline}}[frame number]
\usepackage{{booktabs}}
\usepackage[T1]{{fontenc}}
\setbeamerfont{{block body}}{{size=\small}}

\title{{Matched pretrained comparison: result}}
\subtitle{{Our incumbent PET vs.\ Gregor's complete pretrained PET2-small}}
\author{{PET configuration-comparison lane}}
\date{{\today}}

\begin{{document}}
\frame{{\titlepage}}

\begin{{frame}}{{Result}}
\begin{{block}}{{{tex_escape(headline)}}}
{qualification}
\end{{block}}
Matched paired effect, \texttt{{ours $-$ theirs}}, on the predeclared seven-bin
$E_{{\mathrm{{avail}}}}$ recovery:
\[
  \bar{{d}} = {num(interval['mean'], signed=True)}, \qquad
  \text{{95\% CI}} = [{num(interval['ci_low'], signed=True)},\,
  {num(interval['ci_high'], signed=True)}], \qquad
  n = {interval['n_pairs']}\ \text{{pairs}}.
\]
Non-inferiority margin $\delta = {report['thresholds']['non_inferiority_delta']}$,
switching threshold $\delta_{{\mathrm{{switch}}}} =
{report['thresholds']['switching_delta']}$, both frozen before any comparative
result existed.
\vfill
{precision_note}
\vfill
\footnotesize The pilot observations are \textbf{{excluded}}:
{tex_escape(report['pilot_exclusion_reason'])}.
\end{{frame}}

\begin{{frame}}{{What this measures, and what it cannot}}
\begin{{block}}{{The arms differ at step 1 only}}
{tex_escape(scope['step1_reco'])}
\end{{block}}
\begin{{block}}{{Step 2 is identical}}
{tex_escape(scope['step2_gen'])}
\end{{block}}
\begin{{alertblock}}{{The limit this imposes}}
{tex_escape(scope['what_it_cannot_speak_to'])}
\end{{alertblock}}
\end{{frame}}

\begin{{frame}}{{Absolute adequacy, asked of each arm alone}}
\begin{{center}}
\begin{{tabular}}{{lrrc}}
\toprule
arm & mean recovery & floor & adequate \\
\midrule
ours & {num(adequacy['arms']['ours']['mean_recovery'])} &
  {num(adequacy['floor'])} &
  {'yes' if adequacy['arms']['ours']['adequate'] else r'\textbf{no}'} \\
theirs & {num(adequacy['arms']['theirs']['mean_recovery'])} &
  {num(adequacy['floor'])} &
  {'yes' if adequacy['arms']['theirs']['adequate'] else r'\textbf{no}'} \\
\bottomrule
\end{{tabular}}
\end{{center}}
The floor is ${report['thresholds']['adequacy_fraction_of_reference']}\times$ the
applicable reference ({num(adequacy['reference'])}).
\vfill
\footnotesize An arm failing this is ineligible, and one arm's failure does not
disqualify the other: eligibility is asked of each arm on its own.
\end{{frame}}

\begin{{frame}}{{Regional safeguard, on the reporting cells}}
\begin{{center}}\small
\begin{{tabular}}{{lrrr}}
\toprule
region & ours & theirs & floor \\
\midrule
{regional_rows}
\bottomrule
\end{{tabular}}
\end{{center}}
Regions are defined on the $(p_T, p_\parallel)$ reporting cells, never by
stratifying the seven marginal bins. Each floor is
${report['thresholds']['regional_fraction_of_regional_reference']}\times$
\emph{{that region's own}} reference.
\vfill
\footnotesize Safeguard coverage: events whose $(p_T, p_\parallel)$ falls off the
reporting grid are in the aggregate score but in no region ---
{num(off_grid_pct, 2)}\%
of truth mass.
\end{{frame}}

\begin{{frame}}{{Low-acceptance events: retained, reported separately}}
\begin{{center}}
\begin{{tabular}}{{lr}}
\toprule
truth mass fraction & {num(band['truth_mass_fraction'])} \\
injected displacement share & {num(band['injected_displacement_share'])} \\
mean recovery, ours & {num(band['mean_recovery_by_arm']['ours'])} \\
mean recovery, theirs & {num(band['mean_recovery_by_arm']['theirs'])} \\
\bottomrule
\end{{tabular}}
\end{{center}}
\begin{{block}}{{Scope of any recommendation here}}
{tex_escape(band['reading'])}.
\end{{block}}
\end{{frame}}

\begin{{frame}}{{Stability across seeds}}
\begin{{center}}\small
\begin{{tabular}}{{lr}}
\toprule
seed & $d = $ ours $-$ theirs \\
\midrule
{per_seed}
\midrule
mean & {num(interval['mean'], signed=True)} \\
s.d. & {num(interval['sd'])} \\
\bottomrule
\end{{tabular}}
\end{{center}}
\end{{frame}}

\begin{{frame}}{{Component comparison: evidence and preference kept apart}}
\framesubtitle{{The twelve pinned categories, read from
\texttt{{CONFIGURATION\_COMPARISON-20260918.md}}}}
\begin{{center}}\tiny
\begin{{tabular}}{{p{{0.2cm}}p{{3.4cm}}p{{9.4cm}}}}
\toprule
\# & category & recommendation \\
\midrule
{category_rows}
\bottomrule
\end{{tabular}}
\end{{center}}
\end{{frame}}

\begin{{frame}}{{Provenance}}
\begin{{center}}\small
\begin{{tabular}}{{ll}}
\toprule
commit & \texttt{{{tex_escape(str(prov.get('commit', 'unknown'))[:12])}}} \\
campaign directory & \texttt{{{tex_escape(str(prov.get('campaign_dir', '---')))}}} \\
closure inputs & \texttt{{{tex_escape(closure_sha[:16])}}} \\
truth rows scored & {prov.get('truth_rows_scored', '---')} \\
aggregate reference & {num(prov.get('aggregate_reference'))} \\
\bottomrule
\end{{tabular}}
\end{{center}}
\end{{frame}}

\begin{{frame}}{{Scope}}
\begin{{alertblock}}{{What this is not}}
PET remains diagnostic method development. This deck is \textbf{{not}} a
publication adoption, a covariance construction, a systematic, a central-value
change, or a Gate-6 action, and it discharges no open item.
\end{{alertblock}}
Three differences from Gregor's configuration are \textbf{{declared, not
eliminated}}: muon presence via \texttt{{muon\_E > 0}} rather than the MINOS
match, \texttt{{prong\_dEdXMean}} substituted for the absent
\texttt{{prong\_part\_dEdXMean}}, and a proportional cap split that is ours
rather than his. Any reading of the result carries them.
\end{{frame}}

\end{{document}}
"""


def claim_index(report: dict[str, Any]) -> str:
    interval = report["interval"]
    prov = report.get("provenance", {})
    return f"""# Claim-to-evidence index: final comparison

Every claim the deck makes, and the artifact that settles it. Generated with the
deck from the same report, so the two cannot drift.

| claim | evidence |
|---|---|
| paired effect {interval['mean']:+.4f}, CI [{interval['ci_low']:+.4f}, {interval['ci_high']:+.4f}], n={interval['n_pairs']} | `campaign_report.json` -> `interval`; computed by `score_campaign.t_interval`, whose quantiles are checked against published tables in `test_score_campaign.py` |
| the pilot is excluded from that interval | `campaign_report.json` -> `pilot_excluded`; enforced by `score_campaign.score_campaign`, which raises if pilot rows are passed as campaign scores |
| absolute adequacy per arm | `campaign_report.json` -> `absolute_adequacy`; floor is `THRESHOLDS["adequacy_fraction_of_reference"]` x the reference in `provenance.aggregate_reference` |
| regional floors are per region | `campaign_report.json` -> `regional_safeguard.floor_by_region`; references from `characterize_regions.regional_reference` |
| regions are cells, not marginal bins | `characterize_regions.region_labels_for_events`, tested against `np.histogram2d` in `test_regions.py` |
| safeguard coverage | `campaign_report.json` -> `regional_coverage.off_grid_truth_fraction` |
| low-acceptance mass, displacement and per-arm recovery | `campaign_report.json` -> `low_acceptance` |
| step 2 is identical across arms | `frozen_design.STEP_SCOPE`; `run_arm_evaluation.evaluate` builds `model_gen` from `OURS_INCUMBENT` for both arms |
| the three declared differences | `build_theirs_inputs.DECLARED_DIFFERENCES`, with tests in `test_build_theirs_inputs.py` |
| the twelve-category component comparison | `CONFIGURATION_COMPARISON-20260918.md`; extracted by `make_final_deck.component_comparison`, which fails unless exactly 12 are found |
| verdict and recommendation | `selection_rule.decide`, applied in `score_campaign.score_campaign` with thresholds from `frozen_design.THRESHOLDS` |
| provenance | commit `{str(prov.get('commit', 'unknown'))[:12]}`, closure sha256 `{str(prov.get('closure_npz', {}).get('sha256', 'unknown'))[:16]}`, {prov.get('truth_rows_scored', '?')} truth rows |

**Scope.** PET is diagnostic method development. Nothing indexed here is a
publication adoption, a covariance, a systematic, a central-value change or a
Gate-6 action.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=HERE / "slides")
    parser.add_argument("--stem", default="final_comparison")
    parser.add_argument("--no-compile", action="store_true")
    args = parser.parse_args()

    report = json.loads(args.report.read_text())
    args.outdir.mkdir(parents=True, exist_ok=True)
    tex_path = args.outdir / f"{args.stem}.tex"
    tex_path.write_text(build_tex(report, component_comparison()))
    index_path = args.outdir.parent / f"CLAIM_EVIDENCE_INDEX-{args.stem}.md"
    index_path.write_text(claim_index(report))
    print(f"[deck] wrote {tex_path}")
    print(f"[deck] wrote {index_path}")

    if args.no_compile:
        return 0
    for _ in range(2):
        done = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             f"{args.stem}.tex"],
            cwd=args.outdir, capture_output=True, text=True)
        if done.returncode != 0:
            sys.stderr.write(done.stdout[-4000:])
            raise SystemExit(f"[deck] pdflatex failed for {tex_path}")
    pdf = args.outdir / f"{args.stem}.pdf"
    print(f"[deck] rendered {pdf} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
