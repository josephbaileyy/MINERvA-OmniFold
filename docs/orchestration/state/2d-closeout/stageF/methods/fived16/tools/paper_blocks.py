"""Insert the paper's two FIVED16 blocks into paper_body.tex (scratch assembly script; the .tex is the source)."""
import sys

P = sys.argv[1]
V = lambda k: rf"\fvval{{{k}}}"
PRED = [("gcv", "label-gcv"), ("gmec", "label-gmec"), ("nuwro", "label-nuwro"), ("gibuu", "label-gibuu"),
        ("tune", "label-tune")]
TRUTHS = [("nominal", "simulation prior", "full"), ("A7_mnvtune", "Tune~v1, hybrid", "full"),
          ("A7_genie_cv", "GENIE CV, hybrid", "full"), ("A7_genie_mec", "GENIE + MEC, hybrid", "$-$GENIE + MEC"),
          ("W2", r"GENIE + MEC, $(\Eavail,W)$ shape", "$-$GENIE + MEC"), ("A7_nuwro", "NuWro, hybrid", "$-$NuWro"),
          ("W1", r"NuWro, $\Eavail$ shape", "$-$NuWro"), ("W3", r"NuWro, $(\pT,\pPar,\Eavail)$ shape", "$-$NuWro"),
          ("closure_nuwro", "NuWro, closure", "$-$NuWro"), ("stage0c_gibuu", r"GiBUU, $\Eavail$ shape", "$-$GiBUU"),
          ("A7_gibuu", "GiBUU, hybrid", "$-$GiBUU"), ("q3", r"synthetic $q_3$ tilt", "full")]

A = []
a = A.append
a("% FIVED16-BEGIN DECISION-20261027-joseph-5d-integration-then-second-scope-review.md item 2; every number is \\fvval{key} "
  "from values_fived16.tex (make_values_fived16.py, readouts pinned by sha256). The printed wording is Joseph's to approve.")
a(r"\subsection{A sixteen-cell five-observable measurement}")
a(r"\label{sec:result16}")
a(r"A five-observable cross section with total uncertainties is reported separately from those reporting "
  r"definitions: configuration~(e)'s data result on 16 cells, R00--R15. They come from the " + V("h2-nboxes")
  + r" boxes formed by one interior edge per axis ($\pT$ " + V("h2-mid-pt") + r", $\pPar$ " + V("h2-mid-pz")
  + r"~GeV/$c$, $\Eavail$ " + V("h2-mid-eavail") + r", $q_3$ " + V("h2-mid-q3") + r", $W$ " + V("h2-mid-W")
  + r"~GeV), of which the study's " + V("h2-nsupported") + r" coarser cells are the supported ones; each supported box "
  r"with purity below " + V("h2-tau") + r" is merged into a neighbour, " + V("h2-nunreported") + r" boxes remain "
  r"unreported, and every reported cell passes the support rule. Its model term differs from the study's envelope: "
  r"there, the largest shift of a cell over five generator-sized truth changes, added linearly to the half-width; "
  r"here, a covariance built from three generator shifts. The reported covariance is "
  r"$C_{\mathrm{total}}+C_{\mathrm{resp}}$. $C_{\mathrm{total}}$ sums the statistical, flux, interaction, detector, "
  r"lateral and normalization uncertainties of configuration~(e), a training-seed term measured to be zero, and "
  r"$C_{\mathrm{model}}$. $C_{\mathrm{model}}$ is built from the change in the unfolded data when the prior is "
  r"reweighted to GENIE + MEC, NuWro and GiBUU in turn; it is generator-shape model dependence, unscaled and not a "
  r"calibrated bound, and its coverage at truths held out of its construction has not been validated. $C_{\mathrm{resp}}$ is the response of "
  r"the result to a one-standard-deviation scale of the reconstructed recoil energy in the simulation, for protons, "
  r"mesons, electromagnetic and other deposits; it does not cover neutron or muon deposits, nor species, "
  r"energy-dependence or resolution effects beyond a scale, and it does not enter the generator tests of "
  r"Sec.~\ref{sec:joint} or the paper's other results. The median per-cell relative uncertainty is "
  + V("sigmed-C_total_resp") + r"\% (" + V("sigmed-C_total") + r"\% without $C_{\mathrm{resp}}$). The note gives the "
  r"cells, the central values and the per-group uncertainties, and \fvpending{the full covariance, once its export "
  r"lands}.")
a('% Search: coverage of C_model at held-out truths; validated intervals of the sixteen-cell result (nd-unfolding/pv-ladder/readouts/cmodel_5d.json labels.coverage: "coverage at held-out truths was not validated (DECISION-20261024-joseph-5d-community-standard-route.md item 3); the paper states this as a limitation"; FD-F0b-REPORT.md NOT CITABLE FOR coverage) @ 8b0f83fd')
a("")
a(r"To compare the estimator's bias with the reported covariance when the truth differs from the simulation, we "
  r"unfold pseudo-data at " + V("f0b-all-truths") + r" truths and compare the mean unfolded result with each truth on "
  r"the 16 cells through $\chi^2$ with 16 degrees of freedom. The truths are the simulation's prior; the five hybrid "
  r"truths of the generator tests of Sec.~\ref{sec:joint}, each a prediction on the fine grid; NuWro shape changes "
  r"in $\Eavail$ and in $(\pT,\pPar,\Eavail)$; a GENIE + MEC shape change in $(\Eavail,W)$; a GiBUU-to-GENIE $\Eavail$ "
  r"ratio; a noise-free closure at the NuWro shape; and a synthetic tilt of the $q_3$ distribution at fixed "
  r"$(\Eavail,W)$. A truth from a generator that contributes to $C_{\mathrm{model}}$ is compared with the covariance "
  r"without that generator's component, so that no such truth is compared with a covariance that includes its own "
  r"generator's component; " + V("f0b-nungraded") + r" further truths, whose offset correction failed its control, "
  r"are ungraded and given in the note. A truth is listed when $p<" + V("trig-p") + r"$ or when a cell has $|z|>" + V("trig-z")
  + r"$. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone.")
a("")
a(r"\begin{table*}[tb]")
a(r"  \caption{Fake-data tests on the sixteen cells: $\chi^2$ (16 degrees of freedom), $p$ and the cells with "
  r"$|z|>" + V("trig-z") + r"$, against $C_{\mathrm{total}}+C_{\mathrm{resp}}$ and against $C_{\mathrm{total}}$, "
  r"each without the truth's own generator component where the second column says so ($-$).}")
a(r"  \label{tab:fd16}")
a(r"  \centering\scriptsize\setlength{\tabcolsep}{3pt}")
a(r"  \begin{tabular}{@{}llrrlrrl@{}}")
a(r"    \toprule")
a(r"    & & \multicolumn{3}{c}{$C_{\mathrm{total}}+C_{\mathrm{resp}}$} & \multicolumn{3}{c}{$C_{\mathrm{total}}$} \\")
a(r"    \cmidrule(lr){3-5}\cmidrule(l){6-8}")
a(r"    Truth & Cov. & $\chi^2$ & $p$ & cells & $\chi^2$ & $p$ & cells \\")
a(r"    \midrule")
for n, d, c in TRUTHS:
    a(f"    {d} & {c} & " + V(f"f0b-{n}-chi2") + " & $" + V(f"f0b-{n}-p") + "$ & " + V(f"f0b-{n}-cells") + " & "
      + V(f"f0-{n}-chi2") + " & $" + V(f"f0-{n}-p") + "$ & " + V(f"f0-{n}-cells") + r" \\")
a(r"    \bottomrule")
a(r"  \end{tabular}")
a(r"\end{table*}")
a("")
a(r"Under the reported covariance, without the GiBUU component for the two GiBUU truths, the bias is listed at the "
  r"GiBUU $\Eavail$ shape (cell R06, $z="
  + V("f0b-stage0c_gibuu-zmax") + r"$), at the GiBUU hybrid truth ($p=" + V("f0b-A7_gibuu-p") + r"$; cells "
  + V("f0b-A7_gibuu-cells") + r") and at the synthetic $q_3$ tilt ($p=" + V("f0b-q3-p") + r"$): the reported "
  r"uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the $q_3$ tilt. At the other "
  + V("f0b-nunlisted") + r" truths neither criterion is met.")
a("% FIVED16-END")
a("")
B = []
b = B.append
b("% FIVED16-BEGIN the generator comparison on the sixteen cells (DECISION-20261026-joseph-5d-generator-comparison-presentation.md "
  "option 1; DECISION-20261027-joseph-chi2-table-format.md). The p-value question is in the wording packet for Joseph.")
b(r"\subsection{Comparison on the sixteen reported cells}")
b(r"\label{sec:gen16}")
b(r"Table~\ref{tab:gen16} compares the sixteen-cell result of Sec.~\ref{sec:result16} with five predictions through "
  r"$\chi^2$ against the reported covariance plus each prediction's finite-sample (diagonal) covariance $V_g$, with shape-only "
  r"$\chi^2$ beside it; no diagonal-only $\chi^2$ is formed. \fvpending{the ratio figure, prediction over data on "
  r"the sixteen cells, from the 5D measurement session} GiBUU's sample stops at $E_\nu=" + V("cmodel-gibuu-enu")
  + r"$~GeV, so it is compared on the " + "8" + r" cells with $\pPar<" + V("h2-mid-pz") + r"$~GeV/$c$ only. The reported "
  r"uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec.~\ref{sec:result16}). NuWro and GiBUU are on carbon, with no "
  r"correction to CH, and MINERvA Tune~v1 is the simulation's prior. Because $C_{\mathrm{model}}$ is built from "
  r"shifts toward GENIE + MEC, NuWro and GiBUU, each relative to GENIE CV, those comparisons use a covariance built in "
  r"part from the compared generator, and the GENIE CV comparison does through that reference.")
b("")
b(r"\begin{table}[tb]")
b(r"  \caption{$\chi^2$ and its number of degrees of freedom of each prediction against the sixteen-cell result, under "
  r"$C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$, with $V_g$ the prediction's finite-sample (diagonal) covariance; shape-only $\chi^2$ frees "
  r"the normalization.}")
b(r"  \label{tab:gen16}")
b(r"  \centering\scriptsize")
b(r"  \begin{tabular}{@{}lcc@{}}")
b(r"    \toprule")
b(r"    Prediction & $\chi^2$ and ndf & shape-only \\")
b(r"    \midrule")
for k, lab in PRED:
    b("    " + V(lab) + " & " + V(f"g-{k}-total-chi2int") + "/" + V(f"g-{k}-total-ndf") + " & "
      + V(f"g-{k}-shape_only-chi2int") + "/" + V(f"g-{k}-shape_only-ndf") + r" \\")
b(r"    \bottomrule")
b(r"  \end{tabular}")
b(r"\end{table}")
b("")
b(r"Weakening only the flux correlations by " + V("sens-alpha-pct") + r"\,\% lowers the $\chi^2$ of the 16-cell "
  r"predictions by " + V("sens-flux-fall-lo") + "--" + V("sens-flux-fall-hi") + r"\,\%. The same change to the "
  r"detector or lateral correlations lowers it by at most " + V("sens-detlat-fall-max") + r"\,\%. With the "
  r"correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps "
  r"$\chi^2\geq" + V("sens-joint-chi2-min") + r"$ for 16 degrees of freedom.")
b("% FIVED16-END")
b("")

t = open(P).read()
anchor1 = "\\section{What limits the estimator}\n"
anchor2 = "\\subsection{Hypotheses and calibration}\n"
assert t.count(anchor1) == 1 and t.count(anchor2) == 1 and "FIVED16-BEGIN" not in t
t = t.replace(anchor1, "\n".join(A) + "\n" + anchor1).replace(anchor2, "\n".join(B) + "\n" + anchor2)
open(P, "w").write(t)
print("inserted", len(A), "+", len(B), "lines")
