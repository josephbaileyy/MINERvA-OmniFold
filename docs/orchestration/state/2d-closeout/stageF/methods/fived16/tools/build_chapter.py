"""Assemble sec_fived16.tex (the note's chapter on the sixteen-cell result). Prose is one line per paragraph; every number
is \\fvval{key} from values_fived16.tex. Run once; the .tex is the committed source, this script is scratch."""
import sys

OUT = sys.argv[1]
V = lambda k: rf"\fvval{{{k}}}"
CELLS = [f"R{i:02d}" for i in range(16)]
AX = [("pt", r"$\pT$"), ("pz", r"$\pPar$"), ("eavail", r"$\Eavail$"), ("q3", r"$q_3$"), ("W", r"$W$")]
PRED = [("gcv", "label-gcv"), ("gmec", "label-gmec"), ("nuwro", "label-nuwro"), ("gibuu", "label-gibuu"),
        ("tune", "label-tune")]
# graded truths in the order of the fake-data table, with their descriptions (FD-PLAN §1; DRAFT §2.2)
TRUTHS = [("nominal", "simulation prior (MINERvA Tune~v1)", "full"),
          ("A7_mnvtune", "MINERvA Tune~v1, hybrid", "full"),
          ("A7_genie_cv", "GENIE CV, hybrid", "full"),
          ("A7_genie_mec", "GENIE + MEC, hybrid", "$-$GENIE + MEC"),
          ("W2", r"GENIE + MEC, $(\Eavail,W)$ shape (W2)", "$-$GENIE + MEC"),
          ("A7_nuwro", "NuWro, hybrid", "$-$NuWro"),
          ("W1", r"NuWro, $\Eavail$ shape (W1)", "$-$NuWro"),
          ("W3", r"NuWro, $(\pT,\pPar,\Eavail)$ shape (W3)", "$-$NuWro"),
          ("closure_nuwro", "NuWro, closure (noise-free)", "$-$NuWro"),
          ("stage0c_gibuu", r"GiBUU, $\Eavail$ shape", "$-$GiBUU"),
          ("A7_gibuu", "GiBUU, hybrid", "$-$GiBUU"),
          ("q3", r"synthetic $q_3$ tilt", "full")]

L = []
P = L.append

P(r"\section{The sixteen-cell five-observable measurement}")
P(r"\label{sec:fived16}")
P("% DECISION-20261027-joseph-5d-integration-then-second-scope-review.md item 2. Every number is \\fvval{key} from "
  "values_fived16.tex, which make_values_fived16.py generates from the readouts it pins by sha256 (S1, CRESP, F0, "
  "F0b, G, G-DIAG, G-FOLLOWUP, G-SENS2 and the H2 definition). The readouts are NOT CITABLE FOR an interpretation, "
  "coverage or a claim; this section reports their numbers, each beside its matrix.")
P("")
P(r"This section gives a five-dimensional cross-section result with total uncertainties: the data result of "
  r"configuration~(e) (\S\ref{sec:method-config}) on " + "16" + r" cells, R00--R15, with the reported covariance "
  r"$C_{\mathrm{total}}+C_{\mathrm{resp}}$. It is a separate product from the configuration-(a) five-dimensional "
  r"central value of Secs.~\ref{sec:eavailw} and~\ref{sec:5d} and from the five-axis covariance used with that central "
  r"value (\S\ref{sec:eavailw-adopted}). Statements in those sections about that central value and that covariance "
  r"do not describe this result, and statements here do not describe them. The section gives the cells and the "
  r"result (\S\ref{sec:fived16-result}), the covariance and what it is built from (\S\ref{sec:fived16-cov}), the "
  r"fake-data tests of the estimator's bias against the covariance (\S\ref{sec:fived16-fd}) and the comparison "
  r"with generator predictions (\S\ref{sec:fived16-gen}).")
P("")

# ---- result
P(r"\subsection{Cells and result}")
P(r"\label{sec:fived16-result}")
P(r"The cells are those of the H2 grid of \S\ref{sec:gbdt-model-dependence} after a purity merge. H2 divides each "
  r"axis once, giving " + V("h2-nboxes") + r" boxes, with edges $\pT=(" + V("h2-edges-pt") + r")$, $\pPar=("
  + V("h2-edges-pz") + r")$, $\Eavail=(" + V("h2-edges-eavail") + r")$, $q_3=(" + V("h2-edges-q3") + r")$ and $W=("
  + V("h2-edges-W") + r")$, in the units of App.~\ref{sec:gbdt-diagnostic-definitions}; " + V("h2-nsupported")
  + r" of them pass that appendix's support rule. Each supported box whose purity is below $\tau=" + V("h2-tau")
  + r"$ is merged into a neighbour, in " + V("h2-nmerge") + r" declared steps; " + V("h2-nabsorbed")
  + r" unsupported box is absorbed into R09 by these merges, the other " + V("h2-nunreported")
  + r" remain unreported, and each of the 16 resulting cells passes the support rule. Table~\ref{tab:fived16-cells} "
  r"gives each cell's box, its cell-integrated cross section $f$ and its relative uncertainty.")
P("")
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{The sixteen reported cells: boxes ($\pT$, $\pPar$ and $q_3$ in GeV/$c$; $\Eavail$ and $W$ in GeV), cell-integrated cross section $f$ in units of $" + V("f-unit")
  + r"\,\si{cm^2/nucleon}$, and per-cell relative $\sigma$ (\%) under $C_{\mathrm{total}}$, under "
  r"$C_{\mathrm{resp}}$ alone and under the reported $C_{\mathrm{total}}+C_{\mathrm{resp}}$ "
  r"(\S\ref{sec:fived16-cov}).}")
P(r"\label{tab:fived16-cells}")
P(r"\begin{tabular}{@{}l" + "c" * 5 + "r" * 4 + r"@{}}")
P(r"\toprule")
P(r"cell & " + " & ".join(a for _, a in AX) + r" & $f$ & $C_{\mathrm{total}}$ & $C_{\mathrm{resp}}$ & "
  r"$C_{\mathrm{total}}+C_{\mathrm{resp}}$ \\")
P(r"\midrule")
for c in CELLS:
    P(c + " & " + " & ".join(V(f"box-{c}-{k}") for k, _ in AX) + " & " + V(f"f-{c}") + " & "
      + V(f"sig-C_total-{c}") + " & " + V(f"sig-C_resp-{c}") + " & " + V(f"sig-C_total_resp-{c}") + r" \\")
P(r"\midrule")
P(r"median & \multicolumn{6}{c}{} & " + V("sigmed-C_total") + " & " + V("sigmed-C_resp") + " & "
  + V("sigmed-C_total_resp") + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"\end{table}")
P("")

# ---- covariance
P(r"\subsection{The reported covariance}")
P(r"\label{sec:fived16-cov}")
P(r"The reported covariance is $C_{\mathrm{total}}+C_{\mathrm{resp}}$, with $C_{\mathrm{total}}=C_{\mathrm{e}}+"
  r"C_{\mathrm{model}}$. $C_{\mathrm{e}}$ sums the statistical bootstrap of configuration~(e), the flux universes "
  r"weighted by the neutrino--electron and inverse-muon-decay constraint, the interaction and detector bands, the "
  r"lateral bands, the normalization and the training-seed block. The training-seed block was measured and is zero "
  r"in every cell: with full-sample binning and deterministic training, the unfolds at the other seeds are bitwise "
  r"equal to the central one. Table~\ref{tab:fived16-groups} gives each group's per-cell relative $\sigma$.")
P("")
P(r"$C_{\mathrm{model}}$ is built from the change in the unfolded data when the prior is reweighted to each of three "
  r"generators, GENIE + MEC, NuWro and GiBUU: each vertex is that relative shift of the data result, and "
  r"$C_{\mathrm{model}}$ is the sum of their outer products, unscaled. It is generator-shape model dependence, not a "
  r"calibrated bound. Its coverage at truths held out of its construction has not been validated. GiBUU's shape is "
  r"applied only below $\pPar=" + V("cmodel-gibuu-pz-max") + r"$~GeV/$c$, above which the prior is unchanged; between "
  r"$\pPar=" + V("cmodel-gibuu-pz-lack") + r"$ and " + V("cmodel-gibuu-pz-max") + r"~GeV/$c$ GiBUU's sample lacks the "
  r"part above $E_\nu=" + V("cmodel-gibuu-enu") + r"$~GeV, " + V("cmodel-gibuu-lack-lo") + "--" + V("cmodel-gibuu-lack-hi")
  + r"\% of the cross section there. GiBUU's vertex carries " + V("cmodel-trace-gibuu") + r" of $C_{\mathrm{model}}$'s "
  r"trace, NuWro's " + V("cmodel-trace-nuwro") + r" and GENIE + MEC's " + V("cmodel-trace-genie_mec") + r". In every "
  r"cell, " + V("cmodel-step-lo") + "--" + V("cmodel-step-hi") + r"\% of the prior weight lies beside a step in the "
  r"reweighting ratio larger than " + V("cmodel-step-r") + r" drawn by the noise gate or a cut, and the shifts "
  r"enter as measured.")
P('% Search: coverage of C_model at held-out truths; validated intervals of the sixteen-cell result (nd-unfolding/pv-ladder/readouts/cmodel_5d.json labels.coverage: "coverage at held-out truths was not validated (DECISION-20261024-joseph-5d-community-standard-route.md item 3); the paper states this as a limitation"; FD-F0b-REPORT.md NOT CITABLE FOR coverage) @ 8b0f83fd')
P("")
P(r"$C_{\mathrm{resp}}$ is the response of configuration~(e)'s data result to a one-standard-deviation scale of the "
  r"simulation's reconstructed recoil energy, for protons, mesons, electromagnetic deposits and other deposits "
  r"separately, summed over the four. It does not cover neutron or muon deposits, the effects of particle species, "
  r"energy dependence and resolution beyond a scale, the null distributions of the "
  r"joint tests, the configuration-(a) products or the two-, three- and four-dimensional results. A cross-talk term, "
  r"reported beside $C_{\mathrm{resp}}$ and not summed into it, has a median per-cell relative $\sigma$ of "
  + V("sigmed-C_resp_xtalk") + r"\%. Its median per-cell relative $\sigma$ is " + V("sigmed-C_resp")
  + r"\%, and adding it raises the total's $\sigma$ by a factor of " + V("sigratio-min") + "--" + V("sigratio-max")
  + r" (median " + V("sigratio-med") + r"). Of the trace of $(C_{\mathrm{total}}+C_{\mathrm{resp}})/f f^{T}$, "
  r"$C_{\mathrm{total}}$ carries " + V("trace-resp-C_total") + r" and the four response species " + V("trace-resp-C_resp_proton")
  + ", " + V("trace-resp-C_resp_meson") + ", " + V("trace-resp-C_resp_em") + " and " + V("trace-resp-C_resp_other") + r".")
P("")
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{Per-cell relative $\sigma$ (\%) of the covariance groups. $C_{\mathrm{e}}$ is the sum of the first six "
  r"groups and the training-seed block (zero in every cell); $C_{\mathrm{total}}=C_{\mathrm{e}}+C_{\mathrm{model}}$. "
  r"The response species of $C_{\mathrm{resp}}$ are in the last four columns.}")
P(r"\label{tab:fived16-groups}")
GRP = [("stat", "stat."), ("flux", "flux"), ("interaction", "interaction"), ("detector", "detector"),
       ("lateral", "lateral"), ("normalization", "norm."), ("C_e", r"$C_{\mathrm{e}}$"),
       ("C_model", r"$C_{\mathrm{model}}$"), ("C_resp_proton", "p"), ("C_resp_meson", "meson"), ("C_resp_em", "EM"),
       ("C_resp_other", "other")]
P(r"\scriptsize\setlength{\tabcolsep}{3pt} \resizebox{\textwidth}{!}{")
P(r"\begin{tabular}{@{}l" + "r" * len(GRP) + r"@{}}")
P(r"\toprule")
P("cell & " + " & ".join(n for _, n in GRP) + r" \\")
P(r"\midrule")
for c in CELLS:
    P(c + " & " + " & ".join(V(f"sig-{k}-{c}") for k, _ in GRP) + r" \\")
P(r"\midrule")
P("median & " + " & ".join(V(f"sigmed-{k}") for k, _ in GRP) + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"}")
P(r"\end{table}")
P("")
P(r"The full covariance and correlation matrices are \fvpending{the declared export of $C_{\mathrm{e}}$, "
  r"$C_{\mathrm{model}}$, $C_{\mathrm{resp}}$ and $C_{\mathrm{total}}+C_{\mathrm{resp}}$ with the correlation matrix "
  r"and the cell boxes, from the 5D measurement session}.")
P("")

# ---- fake data
P(r"\subsection{Fake-data tests of the estimator's bias}")
P(r"\label{sec:fived16-fd}")
P(r"The fake-data tests ask how the estimator's bias at a truth different from the simulation compares with the "
  r"reported covariance. Pseudo-data are generated at " + V("f0b-all-truths") + r" graded truths and unfolded with "
  r"configuration~(e), and the mean unfolded result is compared with each truth on the 16 cells, through $\chi^2$ "
  r"with 16 degrees of freedom and the per-cell pull $z$. The truths are the simulation's prior; the five hybrid "
  r"truths of the generator tests (Sec.~\ref{sec:joint5d}), each a prediction on the fine grid; the historical "
  r"shapes W1, W2 and W3 of \S\ref{sec:gbdt-model-dependence}; a GiBUU-to-GENIE $\Eavail$ shape; a noise-free closure "
  r"at the NuWro shape; and a synthetic tilt of the $q_3$ distribution at fixed $(\Eavail,W)$. A truth from a "
  r"generator that contributes a vertex to $C_{\mathrm{model}}$ is compared with the covariance without that vertex, "
  r"so that no such truth is compared with a covariance that contains its own generator's shift. A truth is listed when "
  r"$p<" + V("trig-p") + r"$, or when a cell has $|z|>" + V("trig-z") + r"$. These are not held-out truths, and the "
  r"detector response is not probed. Table~\ref{tab:fived16-fd} gives each "
  r"truth under the reported covariance and, beside it, under $C_{\mathrm{total}}$ alone.")
P("")
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{Fake-data tests on the sixteen cells: $\chi^2$ (16 degrees of freedom), $p$ and the cells with $|z|>"
  + V("trig-z") + r"$ of the bias of the mean against the reported $C_{\mathrm{total}}+C_{\mathrm{resp}}$, and "
  r"against $C_{\mathrm{total}}$ alone, each without the truth's own generator vertex where the second column says "
  r"so ($-$). $n$ is the number of pseudo-experiments.}")
P(r"\label{tab:fived16-fd}")
P(r"\scriptsize\setlength{\tabcolsep}{3pt} \resizebox{\textwidth}{!}{")
P(r"\begin{tabular}{@{}llr" + "rrl" * 2 + r"@{}}")
P(r"\toprule")
P(r"truth & covariance & $n$ & \multicolumn{3}{c}{$C_{\mathrm{total}}+C_{\mathrm{resp}}$} & "
  r"\multicolumn{3}{c}{$C_{\mathrm{total}}$} \\")
P(r" & & & $\chi^2$ & $p$ & cells & $\chi^2$ & $p$ & cells \\")
P(r"\midrule")
for name, desc, cov in TRUTHS:
    P(f"{desc} & {cov} & " + V(f"f0b-{name}-n") + " & " + V(f"f0b-{name}-chi2") + " & $" + V(f"f0b-{name}-p") + "$ & "
      + V(f"f0b-{name}-cells") + " & " + V(f"f0-{name}-chi2") + " & $" + V(f"f0-{name}-p") + "$ & "
      + V(f"f0-{name}-cells") + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"}")
P(r"\end{table}")
P("")
P(r"Measured against the reported covariance, without the vertex of the truth's own generator where one exists, "
  + V("f0b-nlisted") + r" truths are listed: the GiBUU $\Eavail$ shape, by its cell "
  r"R06 ($z=" + V("f0b-stage0c_gibuu-zmax") + r"$); the GiBUU hybrid truth, by $p$ and by its cells "
  + V("f0b-A7_gibuu-cells") + r"; and the $q_3$ tilt, by $p$ ($p=" + V("f0b-q3-p") + r"$). The reported uncertainty "
  r"does not cover the fake-data bias at these GiBUU-like truths or at the $q_3$ tilt. At the other "
  + V("f0b-nunlisted") + r" truths neither trigger fires.")
P("")
P(r"The counts are read by group, never pooled. The vertex-family truths are the " + "8" + r" from GENIE + MEC, NuWro "
  r"or GiBUU, each compared without its vertex; the non-vertex truths are the GENIE CV hybrid and the $q_3$ tilt; the "
  r"prior truths are the simulation prior and the Tune~v1 hybrid. Under the reported covariance, the vertex-family truths have "
  + V("f0b-grp-vertex-family-zcells") + r" of " + V("f0b-grp-vertex-family-cells") + r" cells with $|z|>"
  + V("trig-z") + r"$ (Gaussian reference " + V("f0b-grp-vertex-family-refcells") + r") and "
  + V("f0b-grp-vertex-family-ptruths") + r" of " + V("f0b-grp-vertex-family-truths") + r" truths with $p<"
  + V("trig-p") + r"$ (reference " + V("f0b-grp-vertex-family-reftruths") + r"); the non-vertex truths "
  + V("f0b-grp-non-vertex-zcells") + r" of " + V("f0b-grp-non-vertex-cells") + r" and " + V("f0b-grp-non-vertex-ptruths")
  + r" of " + V("f0b-grp-non-vertex-truths") + r"; and the prior truths " + V("f0b-grp-prior-zcells") + r" of "
  + V("f0b-grp-prior-cells") + r" and " + V("f0b-grp-prior-ptruths") + r" of " + V("f0b-grp-prior-truths")
  + r". The references are context only, because the bias is deterministic.")
P("")
P(r"Controls " + V("f0b-controls-passed") + r" passed. The offset control, which compares two hybrid truths' offset "
  r"corrections, failed ($\chi^2=" + V("f0b-control7-chi2") + r"$ for 16 degrees of freedom). As declared, the six "
  r"power alternatives built on that correction are therefore descriptive and ungraded; Table~\ref{tab:fived16-fdvar} "
  r"gives them, with the two descriptive variants of each graded truth.")
P("")
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{Descriptive fake-data numbers, none of them a grade. In-sample: against $C_{\mathrm{total}}+C_{\mathrm{resp}}$ "
  r"including the truth's own vertex, which is not evidence (--- where the grade already uses the full matrix). Model-only: against the statistical block and "
  r"$C_{\mathrm{model}}$ without the own vertex, dropping the interaction, flux, detector, lateral and normalization "
  r"blocks, so a lower bound on $C_{\mathrm{model}}$'s reach. Power alternatives: the NuWro $(\pT,\pPar,\Eavail)$ shape "
  r"(P1), a NuWro $q_3$ shape at fixed $(\Eavail,W)$ (P2) and the GENIE + MEC $(\Eavail,W)$ shape (P3), each on the "
  r"Tune~v1 truth (r) and on the GENIE CV truth (g), ungraded because the offset control failed.}")
P(r"\label{tab:fived16-fdvar}")
P(r"\scriptsize\setlength{\tabcolsep}{3pt}")
P(r"\begin{tabular}{@{}lrrr@{\qquad}lrrr@{}}")
P(r"\toprule")
P(r"truth & \multicolumn{2}{c}{in-sample $\chi^2$, $p$} & model-only $\chi^2$ & power alternative & $n$ & $\chi^2$ & $p$ \\")
P(r"\midrule")
POW = ["P1r", "P2r", "P3r", "P1g", "P2g", "P3g"]
for i, (name, desc, cov) in enumerate(TRUTHS):
    insample = ("--- & ---" if cov == "full" else      # graded against the full matrix: no in-sample variant
                V(f"f0b-{name}-in_sample-chi2") + " & $" + V(f"f0b-{name}-in_sample-p") + "$")
    left = desc + " & " + insample + " & " + V(f"f0b-{name}-model_only-chi2")
    right = (" & " + POW[i] + " & " + V(f"f0b-{POW[i]}-n") + " & " + V(f"f0b-{POW[i]}-chi2") + " & $"
             + V(f"f0b-{POW[i]}-p") + "$") if i < len(POW) else " & & & &"
    P(left + right + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"\end{table}")
P("")

# ---- generator comparison
P(r"\subsection{Comparison with generator predictions}")
P(r"\label{sec:fived16-gen}")
P(r"Table~\ref{tab:fived16-gen} compares the result with five predictions through $\chi^2$ against the reported "
  r"covariance plus each prediction's finite-sample (diagonal) covariance $V_g$, $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$, with "
  r"its number of degrees of freedom, and through the shape-only $\chi^2$, which frees the normalization. No "
  r"diagonal-only $\chi^2$ is formed. GiBUU's sample has no events above $E_\nu=" + V("cmodel-gibuu-enu")
  + r"$~GeV, so it is compared on the " + "8" + r" cells below $\pPar=" + V("h2-mid-pz")
  + r"$~GeV/$c$ only, and no value is formed on the other " + "8" + r". The NuWro and GiBUU predictions are on a carbon target, "
  r"with no correction to CH. MINERvA Tune~v1 is the simulation's prior, not an independent prediction. Each "
  r"$C_{\mathrm{model}}$ vertex is a data shift unfolded with a prior reweighted by one generator's ratio to GENIE CV, "
  r"so the GENIE + MEC, NuWro and GiBUU comparisons each use a covariance built in part from the compared "
  r"generator, and the GENIE CV comparison does through the ratios' reference.")
P("")
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{$\chi^2$ with its number of degrees of freedom, against $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$, "
  r"with the shape-only $\chi^2$ beside it.}")
P(r"\label{tab:fived16-gen}")
P(r"\begin{tabular}{@{}lcc@{}}")
P(r"\toprule")
P(r"prediction & $\chi^2$ and ndf & shape-only \\")
P(r"\midrule")
for k, lab in PRED:
    P(V(lab) + " & " + V(f"g-{k}-total-chi2") + "/" + V(f"g-{k}-total-ndf") + " & " + V(f"g-{k}-shape_only-chi2") + "/"
      + V(f"g-{k}-shape_only-ndf") + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"\end{table}")
P("")
P(r"The variant without the response block, against $C_{\mathrm{total}}+V_g$, gives $\chi^2$ of "
  + ", ".join(V(f"g-{k}-nocresp-chi2") + "/" + V(f"g-{k}-total-ndf") for k, _ in PRED[:-1]) + " and "
  + V(f"g-{PRED[-1][0]}-nocresp-chi2") + "/" + V(f"g-{PRED[-1][0]}-total-ndf") + r", in the order of "
  r"Table~\ref{tab:fived16-gen}. Table~\ref{tab:fived16-pulls} gives each cell's pull and $(g-f)/f$.")
P("")
GIBUU_CELLS = {"R00", "R01", "R02", "R03", "R08", "R09", "R10", "R11"}
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{Per-cell pull $(f-g)/\sigma$ against $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$ and $(g-f)/f$ (\%) for each "
  r"prediction; GiBUU on its eight cells only.}")
P(r"\label{tab:fived16-pulls}")
P(r"\scriptsize\setlength{\tabcolsep}{3pt} \resizebox{\textwidth}{!}{")
P(r"\begin{tabular}{@{}l" + "rr" * len(PRED) + r"@{}}")
P(r"\toprule")
P(r"cell & " + " & ".join(r"\multicolumn{2}{c}{" + V(lab) + "}" for _, lab in PRED) + r" \\")
P(r" & " + " & ".join(r"pull & $(g-f)/f$" for _ in PRED) + r" \\")
P(r"\midrule")
for c in CELLS:
    cols = []
    for k, _ in PRED:
        if k == "gibuu" and c not in GIBUU_CELLS:
            cols.append(r"--- & ---")
        else:
            cols.append(V(f"g-{k}-pull-{c}") + " & " + V(f"g-{k}-gf-{c}"))
    P(c + " & " + " & ".join(cols) + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"}")
P(r"\end{table}")
P("")
P(r"The fake-data tests list the GiBUU-like truths under the reported covariance (\S\ref{sec:fived16-fd}), so the "
  r"GiBUU comparison carries that limitation.")
P("")
P(r"Weakening only the flux correlations by " + V("sens-alpha-pct") + r"\,\% lowers the $\chi^2$ of the 16-cell "
  r"predictions by " + V("sens-flux-fall-lo") + "--" + V("sens-flux-fall-hi") + r"\,\%. The same change to the "
  r"detector or lateral correlations lowers it by at most " + V("sens-detlat-fall-max") + r"\,\%. With the "
  r"correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps "
  r"$\chi^2\geq" + V("sens-joint-chi2-min") + r"$ for 16 degrees of freedom. Table~\ref{tab:fived16-sens} gives each "
  r"group's sensitivity, GiBUU's eight-cell values included. These are descriptive sensitivities of the reported "
  r"$\chi^2$, not alternative results: one group's correlations are shrunk toward the diagonal by a fraction "
  r"$\alpha$ of the way, with its variances kept.")
P("")
FAM = [("interaction", "interaction"), ("flux", "flux"), ("detector", "detector"), ("lateral", "lateral"),
       ("c_e_systematic", "the four together")]
ALPHAS = ["0", "0.1", "0.25", "0.5", "1"]
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{$\chi^2$ against $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$ with one group's correlations shrunk by "
  r"$\alpha$ toward the diagonal ($\alpha$ of the declared grid; the first column is the reported $\chi^2$). Degrees of "
  r"freedom as in Table~\ref{tab:fived16-gen}.}")
P(r"\label{tab:fived16-sens}")
P(r"\begin{tabular}{@{}ll" + "r" * len(ALPHAS) + r"@{}}")
P(r"\toprule")
P(r"group & prediction & " + " & ".join(r"$\alpha=\fvval{sens-alpha-" + a.replace(".", "p") + "}$" for a in ALPHAS) + r" \\")
P(r"\midrule")
for fam, fname in FAM:
    for i, (k, lab) in enumerate(PRED):
        P((fname if i == 0 else "") + " & " + V(lab) + " & "
          + " & ".join(V(f"sens-{fam}-{k}-a{a}") for a in ALPHAS) + r" \\")
    P(r"\addlinespace")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"\end{table}")
P("")
P(r"The $\chi^2$ can be decomposed along the eigenmodes of each prediction's matrix (Table~\ref{tab:fived16-diag}). "
  r"The decomposition is a breakdown, not an alternative result; a mode is that matrix's own, and its dominant block "
  r"is the covariance group with the largest share of its variance. \fvpending{the figure of the cell-contrast modes "
  r"that carry the $\chi^2$, with each prediction's distance along them, from the 5D measurement session}")
P("")
P(r"\begin{table}[htbp]")
P(r"\centering\footnotesize")
P(r"\caption{Eigenmode breakdown of the reported $\chi^2$: the fewest modes, in $\chi^2$ order, carrying "
  + V("diag-fractions") + r"\,\% of it, and the top mode's share of the $\chi^2$, its relative $\sigma$ and its dominant block.}")
P(r"\label{tab:fived16-diag}")
P(r"\begin{tabular}{@{}lcccrrl@{}}")
P(r"\toprule")
P(r"prediction & \multicolumn{3}{c}{modes for " + V("diag-fractions") + r"\,\%} & top mode (\% of $\chi^2$) & $\sigma$ (\%) & block \\")
P(r"\midrule")
for k, lab in PRED:
    b = f"diag-{k}-reported"
    P(V(lab) + " & " + V(f"{b}-modes50") + " & " + V(f"{b}-modes90") + " & " + V(f"{b}-modes99") + " & "
      + V(f"{b}-top-share") + " & " + V(f"{b}-top-sigma") + " & " + V(f"{b}-top-block") + r" \\")
P(r"\bottomrule")
P(r"\end{tabular}")
P(r"\end{table}")
P("")
P(r"Cell R04 ($\pT<" + V("h2-mid-pt") + r"$, $\pPar\geq" + V("h2-mid-pz")
  + r"$, $\Eavail<" + V("h2-mid-eavail") + r"$, $q_3<" + V("h2-mid-q3") + r"$) has the "
  r"smallest relative $\sigma$ of the sixteen, " + V("r04-sigma-total") + r"\,\%, of which flux is the largest "
  r"group at " + V("r04-sigma-flux") + r"\,\%. Under the flux block alone its correlation with the "
  + V("r04-ncorr") + r" cells that load with it in the top modes is " + V("r04-corrflux-min") + "--"
  + V("r04-corrflux-max") + r"; under the reported covariance it is " + V("r04-corr-min") + "--" + V("r04-corr-max")
  + r".")
P("")
open(OUT, "w").write("\n".join(L) + "\n")
print("wrote", OUT, len(L), "lines")
