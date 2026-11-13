#!/usr/bin/env python3
r"""Build the S8 index restructure's clause inventory (the director's ruling, 2026-11-13).

usage: make_inventory.py <worktree> <out.tsv>

One row per clause of every cell of the former tables S11 (tab:tests-spec) and S12 (tab:tests-result), each mapped to
where it now prints: the new index (tab:tests) or the test's home section, as file:line. Each locator is a substring
that must occur exactly once in the comment-free lines of its file, so the line is found, not typed. "moved" means the
clause was added there by this restructure, "already" that the home section printed it before, "index" that the index
row carries it."""
import sys
from pathlib import Path

wt = Path(sys.argv[1])
SB = "docs/analysis-note/supplemental_body.tex"
PB = "docs/analysis-note/paper_body.tex"

R = []   # (test, old table, old column, clause, how, file, locator)
def add(test, tab, col, clause, how, loc, f=SB):
    R.append((test, tab, col, clause, how, f, loc))

IX = "index"
# ---- test 1
L1 = r"The benchmark compares the two-dimensional estimator's result on the data"
add("1", "S11", "Estimator", "2D", "moved", L1)
add("1", "S11", "Truth(s)", "the data", "moved", L1)
add("1", "S11", "Simulation", "the full simulation", "moved", r"unfolded with the full simulation, with the published result")
add("1", "S11", "What is varied", "--- (comparison with the published result)", "moved", r"unfolded with the full simulation, with the published result")
add("1", "S11", "Repetitions", r"covariance from \fvval{cov2d-nuniv} universes in \fvval{cov2d-nunivbands} bands plus the normalization", "moved", r"Its covariance is built from \fvval{cov2d-nuniv} universes in \fvval{cov2d-nunivbands} bands plus the normalization")
add("1", "S11", "Repetitions", r"\fvval{cov2d-nstat} bootstrap replicas", "moved", r"\fvval{cov2d-nstat} bootstrap replicas")
add("1", "S11", "Repetitions", r"\fvval{cov2d-nperiod-word} period groups", "moved", r"\fvval{cov2d-nperiod-word} period groups")
add("1", "S11", "Repetitions", r"\fvval{cov2d-nseed-word} seed settings", "moved", r"\fvval{cov2d-nseed-word} seed settings")
I1 = r"1. Two-dimensional benchmark & ratio of integrated cross sections"
add("1", "S12", "Statistic", "ratio of integrated cross sections, 2D to published", IX, I1)
add("1", "S12", "Statistic", r"$\chi^2/\mathrm{ndf}$ against the published result under its covariance (ndf $=205$)", IX, r"against the published result under its covariance (ndf $=205$). Descriptive, no threshold")
add("1", "S12", "Threshold", "none (descriptive)", IX, r"Descriptive, no threshold & ratio")
add("1", "S12", "Result", r"ratio $\ratioTot$, $\chi^2/\mathrm{ndf}=\chiPaper$", IX, r"& ratio $\ratioTot$, $\chi^2/\mathrm{ndf}=\chiPaper$ & \ref{supp:cov2d-bench}")
# ---- test 2
L2 = r"The closure test of the paper's \psec{sec:closure} unfolds pseudo-data with the reported estimator"
add("2", "S11", "Estimator", "the estimator", "moved", L2)
add("2", "S11", "Truth(s)", "the simulation's prior", "moved", r"with the reported estimator at the simulation's prior and at changed truths")
add("2", "S11", "Truth(s)", r"GiBUU-to-GENIE and NuWro $\Eavail$ shapes", "moved", r"The changed truths are the GiBUU-to-GENIE and NuWro $\Eavail$ shapes")
add("2", "S11", "Truth(s)", r"a GENIE + MEC $(\Eavail,W)$ shape", "moved", r"shapes, a GENIE + MEC $(\Eavail,W)$ shape, a NuWro $(\pT,\pPar,\Eavail)$ shape and the $q_3$ tilt (section~\ref{supp:q3tilt})")
add("2", "S11", "Truth(s)", r"a NuWro $(\pT,\pPar,\Eavail)$ shape", "moved", r"a NuWro $(\pT,\pPar,\Eavail)$ shape and the $q_3$ tilt (section~\ref{supp:q3tilt})")
add("2", "S11", "Truth(s)", r"the $q_3$ tilt", "moved", r"and the $q_3$ tilt (section~\ref{supp:q3tilt})")
add("2", "S11", "Simulation", "half split", "moved", r"There are \fvval{s5e-nom-n} pseudo-experiments at the prior")
add("2", "S11", "What is varied", "the truth", "moved", r"at the simulation's prior and at changed truths")
add("2", "S11", "Repetitions", r"\fvval{s5e-nom-n} at the prior", "moved", r"\fvval{s5e-nom-n} pseudo-experiments at the prior")
add("2", "S11", "Repetitions", r"\fvval{s5e-shape-n} at each changed truth", "moved", r"\fvval{s5e-shape-n} at each changed truth")
I2 = r"2. Closure and truth changes & $|t|$ of the mean residual"
add("2", "S12", "Statistic", r"$|t|$ of the mean residual of each of \fvval{s5e-nquant} quantities", IX, I2)
add("2", "S12", "Statistic", r"and the largest $(\Eavail,W)$ residual", IX, r"quantities, and the largest $(\Eavail,W)$ residual. At the prior")
add("2", "S12", "Threshold", r"at the prior, no $|t|>\fvval{s5e-tcrit}$", IX, r"At the prior, no $|t|>\fvval{s5e-tcrit}$")
add("2", "S12", "Threshold", "changed truths descriptive", IX, r"Changed truths descriptive & prior:")
add("2", "S12", "Result", r"prior: largest $|t|=\fvval{s5e-nom-tmax}$", IX, r"prior: largest $|t|=\fvval{s5e-nom-tmax}$")
add("2", "S12", "Result", r"largest $(\Eavail,W)$ residual \SI{\fvval{s5e-nom-ewmax}}{\percent}", IX, r"\SI{\fvval{s5e-nom-ewmax}}{\percent}")
add("2", "S12", "Result", r"changed truths: largest residual \SIrange{lo}{hi} (three shapes, over all cells, including unsupported ones)", IX, r"(three shapes, over all cells, including unsupported ones)")
add("2", "S12", "Result", r"\SI{\fvval{s5e-q3-ewmax}}{\percent} ($q_3$ tilt)", IX, r"\SI{\fvval{s5e-q3-ewmax}}{\percent} ($q_3$ tilt)")
add("2", "S12", "Result", r"\SI{\fvval{s5e-gibuu-ewmax}}{\percent} (GiBUU-to-GENIE $\Eavail$)", IX, r"\SI{\fvval{s5e-gibuu-ewmax}}{\percent} (GiBUU-to-GENIE $\Eavail$)")
# ---- test 3a
add("3a", "S11", "Estimator", "the estimator", "already", r"truths and unfolded with configuration~(e)")
add("3a", "S11", "Truth(s)", r"the \fvval{f0b-all-truths} graded truths", "already", r"Pseudo-data are generated at \fvval{f0b-all-truths} truths")
add("3a", "S11", "Simulation", "half split", "moved", r"The pseudo-data of every truth use the half split.")
add("3a", "S11", "What is varied", "the truth", "already", r"compare the estimator's bias at truths other than the simulation")
add("3a", "S11", "Repetitions", r"\fvval{f0b-nominal-n} at the prior", "moved", r"There are \fvval{f0b-nominal-n} pseudo-experiments at the prior")
add("3a", "S11", "Repetitions", r"\fvval{f0b-W1-n} at each of four shape changes and the $q_3$ tilt", "moved", r"\fvval{f0b-W1-n} at each of four shape changes and the $q_3$ tilt")
add("3a", "S11", "Repetitions", r"\fvval{f0b-A7_gibuu-n} at each of five hybrids", "moved", r"\fvval{f0b-A7_gibuu-n} at each of five hybrids")
add("3a", "S11", "Repetitions", "one noise-free closure", "moved", r"five hybrids, and one noise-free closure.")
add("3a", "S12", "Statistic", r"$\chi^2_{16}$ of the mean bias", IX, r"3a. Fake-data bias & $\chi^2_{16}$ of the mean bias")
add("3a", "S12", "Statistic", r"against the reported covariance, without the truth's own $C_{\mathrm{model}}$ component, plus the noise of the mean", "moved", r"The mean bias is compared with the reported covariance, without the truth's own $C_{\mathrm{model}}$ component, plus the noise of the mean.")
add("3a", "S12", "Statistic", r"the per-cell $z$", IX, r"of the mean bias, and the per-cell $z$. Flagged")
add("3a", "S12", "Threshold", r"flagged if $p<\fvval{trig-p}$ or any $|z|>\fvval{trig-z}$", IX, r"Flagged if $p<\fvval{trig-p}$ or any $|z|>\fvval{trig-z}$ & flagged")
add("3a", "S12", "Result", r"flagged: the GiBUU hybrid truth and the $q_3$ tilt", IX, r"& flagged: the GiBUU hybrid truth and the $q_3$ tilt &")
# ---- test 3b
add("3b", "S11", "Estimator", "the estimator", "moved", r"Their pseudo-data use the half split and are unfolded with configuration~(e).")
add("3b", "S11", "Truth(s)", r"\fvval{f1-tune-g18} (\fvval{f1-tune-g18-short}), \fvval{f1-tune-ar23} (\fvval{f1-tune-ar23-short})", "moved", r"The two tunes are \fvval{f1-tune-g18} (\fvval{f1-tune-g18-short}) and \fvval{f1-tune-ar23} (\fvval{f1-tune-ar23-short})")
add("3b", "S11", "Simulation", "half split", "moved", r"Their pseudo-data use the half split")
add("3b", "S11", "What is varied", "the truth", "already", r"Two truths are held out of the analysis")
add("3b", "S11", "Repetitions", r"\fvval{f1-n} at each, and a noise-free closure", "already", r"At each tune, \fvval{f1-n} Poisson pseudo-experiments on half the simulation and a noise-free closure")
add("3b", "S12", "Statistic", "as 3a, against the full reported covariance", IX, r"3b. Held-out tunes & as 3a, against the full reported covariance")
add("3b", "S12", "Threshold", "as 3a", IX, r"3b. Held-out tunes & as 3a, against the full reported covariance")
add("3b", "S12", "Result", r"$\chi^2$ at the two tunes, for 16 degrees of freedom, none flagged", IX, r"for 16 degrees of freedom, none flagged & \ref{supp:study-fd}")
# ---- test 4
L4 = r"\paragraph{The study's design.} At the GiBUU hybrid truth and the $q_3$ tilt"
add("4", "S11", "Estimator", "the estimator", "moved", r"the study varies one setting of the five-observable estimator at a time")
add("4", "S11", "Estimator", "IBU", "already", r"for the five-observable estimator and for IBU at five iterations")
add("4", "S11", "Truth(s)", r"the GiBUU hybrid truth and the $q_3$ tilt", "moved", L4)
add("4", "S11", "Simulation", "half split, noise-free", "moved", r"Each level gives one noise-free unfold at each truth, on a half split")
add("4", "S11", "Simulation", "four more splits for the noise floor", "moved", r"four more splits give the noise floor")
add("4", "S11", "What is varied", "for the estimator, one factor at a time", "moved", r"the study varies one setting of the five-observable estimator at a time")
add("4", "S11", "What is varied", r"iterations (\fvval{prr-nlev-iter} levels)", "moved", r"These are its iterations (\fvval{prr-nlev-iter} levels)")
add("4", "S11", "What is varied", r"capacity (\fvval{prr-nlev-cap})", "moved", r"capacity (\fvval{prr-nlev-cap})")
add("4", "S11", "What is varied", r"training statistics (\fvval{prr-nlev-stat})", "moved", r"training statistics (\fvval{prr-nlev-stat})")
add("4", "S11", "What is varied", r"observables (\fvval{prr-nlev-obs})", "moved", r"observables (\fvval{prr-nlev-obs})")
add("4", "S11", "What is varied", "For IBU, its iterations", "moved", r"For IBU the study varies the iterations.")
add("4", "S11", "Repetitions", "one noise-free unfold per level and truth", "moved", r"Each level gives one noise-free unfold at each truth")
add("4", "S12", "Statistic", r"retained fraction $\rho$", IX, r"4. Prior retention & retained fraction $\rho$.")
add("4", "S12", "Statistic", r"(section~\ref{supp:prr}): its definition's section", IX, r"& \ref{supp:study-prr} (\psec{sec:prr}, table~\ref*{P-tab:prr16})")
add("4", "S12", "Threshold", r"a level changes $\rho$ if it moves it by at least $\max(\fvval{prr-floor},\,\fvval{prr-tq}\,s)$, with $s$ the paired difference's spread over five splits", IX, r"A level changes $\rho$ if it moves it by at least $\max(\fvval{prr-floor},\,\fvval{prr-tq}\,s)$, with $s$ the paired difference's spread over five splits &")
add("4", "S12", "Result", r"\fvgroup{prr}{...} (reduced settings' class, no detected change, higher settings' bound), unchanged", IX, r"& \fvgroup{prr}{a reduced setting (\fvval{prr-pr1-reduced-kinds}) raises $\rho$")
add("4", "S12", "Result", r"IBU at five iterations: $\rho<0$ at both truths, an overshoot along the prior-to-truth direction", IX, r"IBU at five iterations: $\rho<0$ at both truths, an overshoot along the prior-to-truth direction & \ref{supp:study-prr}")
add("4", "S12", "Result", r"(the paper's table~\ref*{P-tab:prr16})", IX, r"(\psec{sec:prr}, table~\ref*{P-tab:prr16})")
# ---- test 5
add("5", "S11", "Estimator", "the estimator against IBU-5", IX, r"sixteen cells (the estimator against IBU-5)")
add("5", "S11", "Estimator", "2D against IBU-10", IX, r"Two dimensions (2D against IBU-10, and the estimator on the 2D inputs)")
add("5", "S11", "Estimator", "the estimator on the 2D inputs", IX, r"Two dimensions (2D against IBU-10, and the estimator on the 2D inputs)")
add("5", "S11", "Truth(s)", "the data", "moved", r"In each, both sides unfold the data with")
add("5", "S11", "Simulation", "the same simulation, template and weight-only universes on both sides", "moved", r"In each, both sides unfold the data with the same simulation, background template and weight-only systematic universes.")
add("5", "S11", "What is varied", "the unfolding algorithm", "already", r"The paper makes three comparisons with binned iterative Bayesian unfolding (IBU).")
add("5", "S11", "Repetitions", r"\fvval{ibu16-nrep} paired replicas", IX, r"on \fvval{ibu16-nrep} paired replicas")
add("5", "S11", "Repetitions", "and the paired universes (sixteen cells)", "already", r"each systematic universe is paired with the five-observable estimator's product")
add("5", "S11", "Repetitions", r"\fvval{c2c1-nrep} paired replicas (2D against IBU-10)", IX, r"$T_\delta$ on \fvval{c2c1-nrep} and \fvval{c1-nrep} paired replicas")
add("5", "S11", "Repetitions", r"\fvval{c1-nrep} (the estimator on the 2D inputs)", IX, r"$T_\delta$ on \fvval{c2c1-nrep} and \fvval{c1-nrep} paired replicas")
add("5", "S12", "Statistic", r"$T=\Delta^{\top}C_\Delta^{-1}\Delta$ (sixteen cells)", IX, r"$T=\Delta^{\top}C_\Delta^{-1}\Delta$ on")
add("5", "S12", "Statistic", r"$T_\delta$ (two dimensions)", IX, r"$T_\delta$ on \fvval{c2c1-nrep}")
add("5", "S12", "Statistic", "with a rank-truncated pseudo-inverse", "already", r"with $C_\delta^{+}$ the pseudo-inverse truncated to the")
add("5", "S12", "Threshold", r"sixteen cells: the null's 95th and 99.7th percentiles, \fvval{ibu16-q95} and \fvval{ibu16-q997}", IX, r"against the null's 95th and 99.7th percentiles, \fvval{ibu16-q95} and \fvval{ibu16-q997}")
add("5", "S12", "Threshold", "Two dimensions: the leave-one-out null's 95th percentile and maximum", IX, r"against the leave-one-out null's 95th percentile and maximum & sixteen cells")
add("5", "S12", "Result", r"sixteen cells: $T=\fvval{ibu16-T}$, differ", IX, r"& sixteen cells: $T=\fvval{ibu16-T}$, differ.")
add("5", "S12", "Result", r"2D IBU: $T_\delta=\fvval{c2c1-T}$ against a maximum of \fvval{c2c1-max}, differ", IX, r"2D IBU: $T_\delta=\fvval{c2c1-T}$ against a maximum of \fvval{c2c1-max}, differ.")
add("5", "S12", "Result", r"The estimator in 2D: \fvval{c1-T} against \fvval{c1-q95}, no difference detected", IX, r"The estimator in 2D: \fvval{c1-T} against \fvval{c1-q95}, no difference detected")
# ---- test 6
L6 = r"It uses the estimator's bias $b_c$ from test 3a and the departure $d_c$ from test 4's noise-free split"
add("6", "S11", "Estimator", "the estimator", "moved", L6)
add("6", "S11", "Truth(s)", r"the \fvval{f0b-all-truths} graded truths, where $|d_c|\geq\SI{1}{\percent}$", "moved", r"It applies at each of the \fvval{f0b-all-truths} graded truths where $|d_c|\geq\SI{1}{\percent}$.")
add("6", "S11", "Simulation", "bias from 3a", "moved", r"bias $b_c$ from test 3a")
add("6", "S11", "Simulation", "departure from 4's noise-free split", "moved", r"the departure $d_c$ from test 4's noise-free split")
add("6", "S11", "What is varied", "the truth", "moved", r"It applies at each of the \fvval{f0b-all-truths} graded truths")
add("6", "S11", "Repetitions", "as 3a", "moved", r"bias $b_c$ from test 3a")
add("6", "S11", "Repetitions", "with the departure's noise from five splits", "moved", r"with the departure's noise from five splits.")
add("6", "S12", "Statistic", r"$|b_c|$ against $0.5\,|d_c|$ at each applicable truth", IX, r"6. Bias-half rule & $|b_c|$ against $0.5\,|d_c|$ at each applicable truth.")
add("6", "S12", "Threshold", "a cell passes if it meets the bound at every applicable truth", IX, r"A cell passes if it meets the bound at every applicable truth.")
add("6", "S12", "Threshold", "and is unresolved if its class at a truth changes within the noise band", IX, r"It is unresolved if its class at a truth changes within the noise band")
add("6", "S12", "Result", r"\fvgroup{vhalf}{...} (pass, fail, not assessed, unresolved), unchanged", IX, r"\fvgroup{vhalf}{\fvval{vhalf-n-valid} of 16 pass, \fvval{vhalf-n-notvalid} fail, \fvval{vhalf-n-notassessed} not assessed")
# ---- test 7
add("7", "S11", "Estimator", "the estimator", "moved", r"The reported estimator is tested on the data, under two perturbations.")
add("7", "S11", "Estimator", "Variants: cross-fitting and two tree regularizations", "moved", r"Its variants, cross-fitting and two tree regularizations, are tested in simulation")
add("7", "S11", "Estimator", r"Ensemble: the average of \fvval{ens1-n} fits", "moved", r"The ensemble average of \fvval{ens1-n} fits is tested there")
add("7", "S11", "Truth(s)", "the data (estimator)", "moved", r"The reported estimator is tested on the data, under two perturbations.")
add("7", "S11", "Truth(s)", r"a GiBUU-to-GENIE $\Eavail$ shape in simulation (variants, ensemble)", "moved", r"are tested in simulation at a GiBUU-to-GENIE $\Eavail$ shape")
add("7", "S11", "Simulation", "half split for the simulated input", "moved", r"The simulated input is drawn from one half of the simulation and unfolded with the other half.")
add("7", "S11", "What is varied", "rounding-level perturbations of the inputs", "moved", r"perturbs the inputs at the rounding level.")
add("7", "S11", "Repetitions", "two perturbations of the data", "moved", r"on the data, under two perturbations.")
add("7", "S11", "Repetitions", r"\fvval{stab-npairs} disjoint perturbation pairs (variants)", "moved", r"on \fvval{stab-npairs} disjoint perturbation pairs.")
add("7", "S11", "Repetitions", r"\fvval{ens1-pairs} pairs (ensemble)", "moved", r"on \fvval{ens1-pairs} pairs.")
add("7", "S12", "Statistic", r"median and maximum, over \fvval{s5e-nquant} quantities, of the shift in statistical standard deviations", IX, r"7. Stability & median and maximum, over \fvval{s5e-nquant} quantities, of the shift in statistical standard deviations.")
add("7", "S12", "Threshold", r"median $\leq\fvval{ens1-bar-median}$, maximum $\leq\fvval{ens1-bar-max}$", IX, r"Median $\leq\fvval{ens1-bar-median}$, maximum $\leq\fvval{ens1-bar-max}$")
add("7", "S12", "Result", r"estimator on the data: median and maximum, fails", IX, r"& estimator on the data: \fvval{s5e-round-median} and \fvval{s5e-round-max}, fails.")
add("7", "S12", "Result", "No variant passes", IX, r"fails. No variant passes.")
add("7", "S12", "Result", r"Ensemble: median and maximum, passes, but is worse in bias at one of \fvval{ens1-ntruths} truths, and it does not replace the reported estimator", IX, r"but is worse in bias at one of \fvval{ens1-ntruths} truths, and it does not replace the reported estimator &")
# ---- test 8
add("8", "S11", "Estimator", "2D", "moved", r"The two-dimensional test unfolds its pseudo-data with the 2D estimator")
add("8", "S11", "Truth(s)", r"\fvval{f1-tune-g18-short}, \fvval{f1-tune-ar23-short}", "already", r"Truths & \fvval{f1-tune-g18-short} and \fvval{f1-tune-ar23-short}, each as its gated reweighting")
add("8", "S11", "Simulation", "pseudo-experiments drawn from the full simulation's universes, unfolded with the nominal simulation", "moved", r"The pseudo-experiments are drawn from the full simulation's universes. The pseudo-data are unfolded once with the nominal simulation")
add("8", "S11", "What is varied", "systematic universes, Poisson counts, lateral signs, normalization", "already", r"a sign for each lateral band, and a Gaussian normalization factor")
add("8", "S11", "Repetitions", r"\fvval{cov2d-ntoys} per tune", "already", r"Pseudo-experiments & \fvval{null-ntoys} per tune & \fvval{null-ntoys} per tune, shared by two variants")
add("8", "S12", "Statistic", r"per cell, the count of errors with $|e_c|\leq\sigma_c$, and jointly, the count with $\chi^2\leq F^{-1}_{\chi^2_n}(P_0)$", IX, r"8. Two-dimensional coverage & per cell, the count of errors with $|e_c|\leq\sigma_c$")
add("8", "S12", "Threshold", r"one-sided binomial against the draw-matched null: $\fvval{null-alpha}/205$ per cell, \fvval{null-alpha} jointly", IX, r"One-sided binomial against the draw-matched null: $\fvval{null-alpha}/205$ per cell, \fvval{null-alpha} jointly")
add("8", "S12", "Result", r"under-covers at both tunes: no pseudo-experiment of \fvval{cov2d-ntoys} in the joint region at either tune", IX, r"under-covers at both tunes: no pseudo-experiment of \fvval{cov2d-ntoys} lies in the joint region at either tune")
add("8", "S12", "Result", "Flagged cells at each tune (counts and cell lists)", IX, r"Flagged cells: \fvval{cov2d-nflags-ar23} at \fvval{f1-tune-ar23-short}")
# ---- test 9
add("9", "S11", "Estimator", "the estimator", "moved", r"Its estimator, simulation, variations, statistic and thresholds were specified as the second test's")
add("9", "S11", "Truth(s)", r"\fvval{f1-tune-g18-short}, \fvval{f1-tune-ar23-short} and a plug-in truth", "moved", r"at each of the two tunes and at a plug-in truth")
add("9", "S11", "Simulation", "as 10", "moved", r"Its estimator, simulation, variations, statistic and thresholds were specified as the second test's")
add("9", "S11", "What is varied", "as 10", "moved", r"Its estimator, simulation, variations, statistic and thresholds were specified as the second test's")
add("9", "S11", "Repetitions", r"\fvval{fd1b-ntoys} per truth", "moved", r"with \fvval{fd1b-ntoys} pseudo-experiments at each of the two tunes")
add("9", "S12", "Statistic+Threshold", "Statistic and threshold as 10", IX, r"9. First five-observable coverage & as 10 &")
add("9", "S12", "Result", "No coverage result: ... (the paper's section 6.2 sentence), unchanged", IX, r"& as 10 & No coverage result: a preliminary check")
# ---- test 10
add("10", "S11", "Estimator", "the estimator", "moved", r"and the second five-observable test with the estimator.")
add("10", "S11", "Truth(s)", r"\fvval{f1-tune-g18-short}, \fvval{f1-tune-ar23-short}", "already", r"Truths & \fvval{f1-tune-g18-short} and \fvval{f1-tune-ar23-short}, each as its gated reweighting")
add("10", "S11", "Simulation", "as 8, with the nominal simulation resampled", "already", r"the simulation and background template resampled with each pseudo-experiment")
add("10", "S11", "What is varied", "as 8, in two variants, without and with the GEANT4 neutron and proton bands", "already", r"Primary variant: without the GEANT4 neutron and proton bands. Second variant: every band")
add("10", "S11", "Repetitions", r"\fvval{null-ntoys} per tune, shared by the variants", "already", r"\fvval{null-ntoys} per tune, shared by two variants")
add("10", "S12", "Statistic", "as 8, on the sixteen cells", IX, r"10. Second five-observable coverage & as 8, on the sixteen cells")
add("10", "S12", "Threshold", r"as 8, with $\fvval{null-alpha}/16$ per cell", IX, r"with $\fvval{null-alpha}/16$ per cell & \fvgroupalt{ll5d}")
add("10", "S12", "Result", r"\fvgroupalt{ll5d}{pending}{\fvgroup{ll5d}{...}} with every \fvcase arm, unchanged", IX, r"& \fvgroupalt{ll5d}{pending}{\fvgroup{ll5d}{\fvcase{ll5d-campaign}{graded}")
# ---- pointers into the two tables
add("-", "S8 text", "introduction", r"Table~\ref{tab:tests-spec} specifies ..., and table~\ref{tab:tests-result} gives ... (repointed)", IX, r"Table~\ref{tab:tests} gives each headline test's statistic, criterion and reading")
add("-", "S10 text", "first paragraph", r"table~\ref{tab:tests-result} (test 6) (repointed)", IX, r"and in table~\ref{tab:tests} (test 6).")

lines = {}
def strip(l):
    import re
    return re.sub(r"(?<!\\)%.*$", "", l)
out = ["id\ttest\told_table\told_column\tclause\thow\tnow_prints_at\tlocator"]
bad = []
for n, (test, tab, col, clause, how, f, loc) in enumerate(R, 1):
    if f not in lines:
        lines[f] = [strip(l) for l in (wt / f).read_text().split("\n")]
    hits = [i + 1 for i, l in enumerate(lines[f]) if loc in l]
    tot = sum(l.count(loc) for l in lines[f])
    if tot != 1:
        bad.append(f"C{n:03d} {loc[:70]!r}: found {tot} times")
        where = "?"
    else:
        where = f"{Path(f).name}:{hits[0]}"
    out.append("\t".join([f"C{n:03d}", test, tab, col, clause, how, where, loc]))
Path(sys.argv[2]).write_text("\n".join(out) + "\n")
print(f"INVENTORY :: {len(R)} clauses; {sum(r[4]=='index' for r in R)} in the index, {sum(r[4]=='moved' for r in R)} moved to a home section, {sum(r[4]=='already' for r in R)} already printed there")
if bad:
    print("UNRESOLVED\n  " + "\n  ".join(bad)); sys.exit(1)
