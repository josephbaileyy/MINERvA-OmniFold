#!/usr/bin/env python3
"""Apply the REAL-row fixes of the agy triage (triage-01-03/04-05/06-09.md), each old_str once, all or none."""
import sys, pathlib
N = pathlib.Path(sys.argv[1]) / 'docs/analysis-note'
FIX = [
 # triage-01-03
 ('sec_systematics.tex', 'Detector and interaction-model systematics use the July universe sweep', 'Detector and model systematics use the July universe sweep'),
 ('sec_systematics.tex', 'The band sum omits the nonresonant single-pion band Rvp1pi', 'The band sum omits the nonresonant-pion band Rvp1pi'),
 ('sec_systematics.tex', 'for the duplicated single-pion band, below', 'for the duplicated pion band, below'),
 ('sec_systematics.tex', 'Second, the two nonresonant single-pion bands, Rvn1pi and Rvp1pi, encode', 'Second, the two bands Rvn1pi and Rvp1pi encode'),
 ('sec_systematics.tex', 'the neutral-current elastic band EtaNCEL and the neutral-current resonant normalization band NormNCRES', 'EtaNCEL and NormNCRES'),
 ('sec_systematics.tex', 'by perturbing all reweightable interaction-model bands and the flux universes', 'by perturbing all reweightable bands and the flux universes'),
 ('sec_systematics.tex', 'a cell set to one by the statistical-noise gate', 'a noise-gated cell'),
 ('sec_3d.tex', 'and charged-pion total energy in the \\texttt{minerva-ml} implementation (App.~\\ref{sec:pet}).', 'and charged-pion total energy in the \\texttt{minerva-ml} implementation (App.~\\ref{sec:pet}). We therefore do not claim that our definition matches ``the published definition.\'\''),
 ('sec_3d.tex', 'For this injection the configuration-(a) estimator recovers the feature. The recovery is shown for configuration~(a) only', 'For this injection the configuration-(a) estimator neither removes the injected feature nor creates a spurious one. That result is shown for configuration~(a) only'),
 # triage-04-05
 ('sec_3d.tex', "samples were generated for this analysis, and MINERvA Tune~v1 is the analysis simulation's truth with its full tune weight;", "samples were generated and processed for this analysis, and MINERvA Tune~v1 was extracted from the analysis simulation's truth with its full tune weight;"),
 ('sec_3d.tex', 'all reweightable interaction-model bands and the flux universes (the unified throw', 'every reweightable band and the flux multisim (the unified throw'),
 ('sec_eavailw.tex', 'The analysis distinguishes the five classifier inputs', 'The companion journal article distinguishes the five classifier inputs'),
 ('sec_eavailw.tex', 'The corner cell $\\Eavail>\\SI{3}{GeV}$, $W>\\SI{3}{GeV}$ holds the largest share, \\SI{22}{\\percent}.', 'The largest cell, the corner $\\Eavail>\\SI{3}{GeV}$, $W>\\SI{3}{GeV}$, holds \\SI{22}{\\percent}.'),
 ('sec_eavailw.tex', 'made with these data (the look-elsewhere effect).', 'made with these data.'),
 ('sec_5d.tex', 'so their smaller residuals are not an improvement in precision on an unchanged quantity.', 'so their smaller residuals and spread are not an improvement in precision on an unchanged quantity.'),
 ('sec_5d.tex', '(every input coordinate moved within half a single-precision rounding unit, values on bin edges kept)', '(uniform input perturbations within half a single-precision unit in the last place that keep the fine-grid membership fixed)'),
 # triage-06-09
 ('sec_joint.tex', 'Measured with the fixed metric $V$ before any observed statistic', 'Measured with $V$ fixed before any observed statistic'),
 ('sec_joint.tex', 'That bound was measured with the fixed metric $V$ before any observed statistic', 'That bound was measured with $V$ fixed before any observed statistic'),
 ('sec_joint.tex', 'proxy significance $a/\\mathrm{se}$ of', 'proxy $a/\\mathrm{se}$ of'),
 ('sec_joint.tex', 'with a median relative shift $|D|/f$ of', 'with a median $|D|/f$ of'),
 ('app_statmethods.tex', 'the GENIE parameters $M_{A}^{\\mathrm{RES}}$, $M_{V}^{\\mathrm{RES}}$ and $M_{A}^{\\mathrm{CCQE}}$', 'the GENIE parameters \\texttt{MaRES}, \\texttt{MvRES} and \\texttt{MaCCQE}'),
 ('app_statmethods.tex', '$M_{A}^{\\mathrm{RES}}$ (MaRES) & $0.627\\%$', 'MaRES & $0.627\\%$'),
 ('app_statmethods.tex', '$M_{V}^{\\mathrm{RES}}$ (MvRES) & $0.362\\%$', 'MvRES & $0.362\\%$'),
 ('app_statmethods.tex', '$M_{A}^{\\mathrm{CCQE}}$ (MaCCQE) & $0.336\\%$', 'MaCCQE & $0.336\\%$'),
 ('app_statmethods.tex', "We therefore attribute $\\sim1$ $\\chi^{2}$-unit of the exact-split cross-check's tension to OmniFold's implicit regularization", "This is direct evidence that $\\sim1$ $\\chi^{2}$-unit of the exact-split cross-check's tension is due to OmniFold's implicit regularization"),
 ('app_statmethods_nd.tex', 'The reporting convention for an N-D $\\chi^{2}$ is to state, where it is quoted,', 'Every N-D $\\chi^{2}$ must state, where it is quoted,'),
 ('app_response_mismatch.tex', 'That amplitude remains to be specified from a documented hadronic-response variation or an explicit quantitative assumption;', 'A documented hadronic-response variation or an explicit quantitative assumption should justify that amplitude;'),
 ('app_response_mismatch.tex', 'a separate uncertainty component, rather than inclusion in a non-closure error.', 'an uncertainty component, and would not be absorbed silently into a non-closure error.'),
 # my own sweeps: dropped \pageref (writer brief: keep every \ref) and the restated joint-test conditions
 ('sec_summary.tex', 'stated with their scopes in the executive summary, the body', 'stated with their scopes in the executive summary (p.~\\pageref{sec:execsummary}), the body'),
 ('sec_summary.tex', 'The executive summary lists the principal limitations, each with', 'The executive summary lists the principal limitations (p.~\\pageref{sec:execsummary-limitations}), each with'),
 ('sec_joint.tex', 'They are numbered (i)--(vi) as in the test specification and fall into three kinds.', 'They are restated here in the terms of this note, numbered (i)--(vi) as in the test specification, and fall into three kinds.'),
]
txt = {}
bad = []
for f, o, n in FIX:
    t = txt.setdefault(f, (N / f).read_text())
    c = t.count(o)
    if c != 1: bad.append((f, c, o[:80]))
    else: txt[f] = t.replace(o, n)
if bad:
    for b in bad: print('NOT ONCE', b)
    sys.exit(1)
for f, t in txt.items(): (N / f).write_text(t)
print(f'applied {len(FIX)} fixes to {len(txt)} files')
