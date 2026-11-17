"""The sentence pass on paper_body.tex, part 1: semicolons and ", so" (the director's rules of 2026-11-12: split
sentences and restructure; no new ", so", "; thus", em-dash chain or "X, not Y"). The B0 span and RS1's paragraph are
protected and are not touched; nor are the LISTED_CLAIMS anchors."""
import sys

p = sys.argv[1]
s = open(p).read()
R = [
    # section 1
    ("Reconstructed $W$ is fixed by the reconstructed $(\\pT,\\pPar,q_{3})$, so the five observables are unfolded simultaneously but are not independent.",
     "Because reconstructed $W$ is fixed by the reconstructed $(\\pT,\\pPar,q_{3})$, the five observables are unfolded simultaneously but are not independent."),
    ("illustrates the method and is not a measurement; the supplementary material gives it",
     "illustrates the method and is not a measurement. The supplementary material gives it"),
    # section 2
    ("the phase space of ref.~\\cite{MINERvA:2021owq}; the selection is given in",
     "the phase space of ref.~\\cite{MINERvA:2021owq}. The selection is given in"),
    ("was checked against that release; the check compares selected samples,",
     "was checked against that release. The check compares selected samples,"),
    ("No single published definition of $\\Eavail$ exists; the supplementary material compares",
     "No single published definition of $\\Eavail$ exists. The supplementary material compares"),
    ("Only reconstructed $W$ is fixed by the others; reconstructed $\\Eavail$ comes from",
     "Only reconstructed $W$ is fixed by the others. Reconstructed $\\Eavail$ comes from"),
    ("GiBUU~2019~\\cite{Buss:2011mx}; NuWro and GiBUU are generated on carbon.",
     "GiBUU~2019~\\cite{Buss:2011mx}. NuWro and GiBUU are generated on carbon."),
    # section 3.1
    ("Events that fail reconstruction enter as truth events without a reconstructed partner, so no separate efficiency correction is applied.",
     "Events that fail reconstruction enter as truth events without a reconstructed partner, and no separate efficiency correction is applied."),
    ("are the data and predicted background counts in that bin, so the classifier's target density is",
     "are the data and predicted background counts in that bin. The classifier's target density is then"),
    ("adds simulated background events with negative weight to the data, so that the target is $D(x)-B(x)$ pointwise.",
     "adds simulated background events with negative weight to the data, which makes the target $D(x)-B(x)$ pointwise."),
    # section 3.2
    ("refits the whole unfolding with its own rounding-level perturbation of the inputs, so the block includes the estimator's sensitivity",
     "refits the whole unfolding with its own rounding-level perturbation of the inputs. The block therefore includes the estimator's sensitivity"),
    ("data resampling with a fresh rounding perturbation in each replica; for the deterministic reported output, it adds",
     "data resampling with a fresh rounding perturbation in each replica. For the deterministic reported output, it adds"),
    ("and the truth denominator, take the universe's values, so the events without a reconstructed partner carry their universe weights too",
     "and the truth denominator, take the universe's values. The events without a reconstructed partner carry their universe weights too"),
    ("(section~\\ref{sec:fd16}; \\nsec{sec:fived16-pl})", "(section~\\ref{sec:fd16} and \\nsec{sec:fived16-pl})"),
    ("(\\fvval{cov2d-nseed-word} seed settings, so its size is poorly determined)", "(\\fvval{cov2d-nseed-word} seed settings, too few to determine its size well)"),
    ("by Cholesky decomposition and without truncation, so its number of degrees of freedom is the number of cells.",
     "by Cholesky decomposition and without truncation. Its number of degrees of freedom is then the number of cells."),
    # section 3.3
    ("The tilt's amplitude is a stress value set in advance; the generator differences do not set it",
     "The tilt's amplitude is a stress value set in advance, not by the generator differences") if False else
    ("The tilt's amplitude is a stress value set in advance; the generator differences do not set it",
     "The tilt's amplitude is a stress value set in advance. The generator differences do not set it"),
    ("were generated for these tests and held out of it; each enters as a gated, normalized shape deformation",
     "were generated for these tests and held out of it. Each enters as a gated, normalized shape deformation"),
    ("in which every Poisson draw is replaced by its mean; the comparison of the ensemble average with the baseline",
     "in which every Poisson draw is replaced by its mean. The comparison of the ensemble average with the baseline"),
    ("The bias is deterministic, so $p$ is a reference score and carries no calibrated probability.",
     "Because the bias is deterministic, $p$ is a reference score and carries no calibrated probability."),
    ("concerns the two-observable estimator; the truth-recovery and stability findings",
     "concerns the two-observable estimator. The truth-recovery and stability findings"),
    # section 4.1
    ("The two bands in figure~\\ref{fig:validation} are correlated, so their overlap is not a compatibility test.",
     "Because the two bands in figure~\\ref{fig:validation} are correlated, their overlap is not a compatibility test."),
    ("Here ndf $=205$ is the number of reported bins; no parameter is fitted.", "Here ndf $=205$ is the number of reported bins, and no parameter is fitted."),
    ("(\\sfig{S2}{fig:tension2d}; \\ssecc{S6}{supp:cov2d})", "(\\sfig{S2}{fig:tension2d} and \\ssecc{S6}{supp:cov2d})"),
    ("The mechanism of the shape difference has not been identified; a binned unfolding of the same inputs lies closer to the published shape.",
     "The mechanism of the shape difference has not been identified. A binned unfolding of the same inputs lies closer to the published shape."),
    ("and increases it in the other \\fvval{pp-kbar}; neither reading establishes", "and increases it in the other \\fvval{pp-kbar}. Neither reading establishes"),
    # section 4.2
    ("with thresholds from a null of exact agreement (\\ssec{S7}{supp:ibu}), so ``differ'' means that a difference is detectable at this noise level.",
     "with thresholds from a null of exact agreement (\\ssec{S7}{supp:ibu}). ``Differ'' therefore means that a difference is detectable at this noise level."),
    ("against \\fvval{c2c1-der} for the two-dimensional OmniFold result; the paired test above shows",
     "against \\fvval{c2c1-der} for the two-dimensional OmniFold result. The paired test above shows"),
    # section 4.4
    ("in each muon-kinematic quadrant; the benchmark does not test", "in each muon-kinematic quadrant. The benchmark does not test"),
    # section 5.1
    ("(\\nsec{sec:val-departure}); on the sixteen cells, the closures", "(\\nsec{sec:val-departure}). On the sixteen cells, the closures"),
    ("(20 pseudo-experiments; figure~\\ref{fig:deformation})", "(20 pseudo-experiments, figure~\\ref{fig:deformation})"),
    ("of the injected change; of the \\fvval{rec-g-n} supported cells", "of the injected change. Of the \\fvval{rec-g-n} supported cells"),
    ("above the nominal truth, so that the residual against the changed truth reaches", "above the nominal truth. The residual against the changed truth then reaches"),
    ("{\\percent}; a lower-capacity development variant with a 100-tree, 8-leaf refinement",
     "{\\percent}. A lower-capacity development variant with a 100-tree, 8-leaf refinement"),
    ("(figure~\\ref{fig:deformation}; \\nsec{sec:eavailw-adopted}); the median cell moves",
     "(figure~\\ref{fig:deformation} and \\nsec{sec:eavailw-adopted}). The median cell moves"),
    ("were not used while the estimator was chosen; the GiBUU-to-GENIE change, also shown, is a development truth.",
     "were not used while the estimator was chosen. The GiBUU-to-GENIE change, also shown, is a development truth."),
    # section 5.2
    ("are the simulation's own truth, so they are closure tests", "are the simulation's own truth, which makes them closure tests"),
    ("is not shown in the figure; it is given in table~\\ref{tab:fd16}.", "is not shown in the figure and is given in table~\\ref{tab:fd16}."),
    ("at truths held out of the analysis; they are not independent of each other", "at truths held out of the analysis. They are not independent of each other"),
    ("The simulated detector response is not varied in these tests; noise-free closures with a shifted recoil response",
     "The simulated detector response is not varied in these tests. Noise-free closures with a shifted recoil response"),
    ("and large next to its statistical block alone; it changes no grade", "and large next to its statistical block alone. It changes no grade"),
    ("where that departure is at least \\SI{1}{\\percent}; a cell is reported as not assessed",
     "where that departure is at least \\SI{1}{\\percent}. A cell is reported as not assessed"),
    # section 5.3
    ("in the same comparison; more iterations remove much of that residual", "in the same comparison. More iterations remove much of that residual"),
    ("(\\nsec{sec:gbdt-model-dependence}); these shifts measure", "(\\nsec{sec:gbdt-model-dependence}). These shifts measure"),
    ("\\fvcase{prr-pr3-ibu}{not}{does not}; this result concerns the mechanism", "\\fvcase{prr-pr3-ibu}{not}{does not}. This result concerns the mechanism"),
    ("to the implementation and to some of its settings; they identify no unique cause of it.", "to the implementation and to some of its settings, but they identify no unique cause of it."),
    # section 5.4
    ("contains the statistical, universe and normalization blocks; the model block", "contains the statistical, universe and normalization blocks. The model block"),
    # section 6.1
    ("and those of the lower-capacity variant by up to 2.5, so the estimator fails a data-stability requirement",
     "and those of the lower-capacity variant by up to 2.5. The estimator therefore fails a data-stability requirement"),
    ("No variant met the data-stability requirement, so we retained the estimator", "Because no variant met the data-stability requirement, we retained the estimator"),
    ("The decision follows that criterion; it does not weigh the stability gain against the bias.", "The decision follows that criterion and does not weigh the stability gain against the bias."),
    ("It was evaluated only on simulated pseudo-data, so its meeting the stability requirement is a statement about pseudo-data; the illustrative data output",
     "It was evaluated only on simulated pseudo-data, and its meeting the stability requirement is a statement about pseudo-data. The illustrative data output"),
    # section 6.2
    ("falls to a binomial threshold of that content; over-coverage is reported", "falls to a binomial threshold of that content. Over-coverage is reported"),
    ("as rebuilt at its truths; none grades the reported intervals at the data.", "as rebuilt at its truths, and none grades the reported intervals at the data."),
    ("with $C_{\\mathrm{model}}$ included; the run-period block was not drawn.", "with $C_{\\mathrm{model}}$ included. The run-period block was not drawn."),
    ("gives the counts against their thresholds; the nominal Gaussian content", "gives the counts against their thresholds. The nominal Gaussian content"),
    ("per degree of freedom; the spread part is", "per degree of freedom. The spread part is"),
    ("which cannot validate their treatment; a run continued or repaired after a check was seen is descriptive.",
     "which cannot validate their treatment. A run continued or repaired after a check was seen is descriptive."),
    ("by a decision made after that check was seen, so the results below are descriptive", "by a decision made after that check was seen. The results below are therefore descriptive"),
    ("\\fvval{ll5d-stop-what}; the test then ran with a repair, \\fvval{ll5d-repair}, chosen after that stop was seen, so the results below are descriptive",
     "\\fvval{ll5d-stop-what}. The test then ran with a repair, \\fvval{ll5d-repair}, chosen after that stop was seen. The results below are therefore descriptive"),
    ("(\\nsec{sec:fived16-fd}; \\ssecc{S8}{supp:tests})", "(\\nsec{sec:fived16-fd} and \\ssecc{S8}{supp:tests})"),
    # section 7
    ("at two tunes (section~\\ref{sec:ll5d}); its result does not validate", "at two tunes (section~\\ref{sec:ll5d}). Its result does not validate"),
    ("the sixteen-cell output is an illustration of the method; its limitations are listed", "the sixteen-cell output is an illustration of the method. Its limitations are listed"),
    ("as the retained fraction of the prior; here part of the prior is retained", "as the retained fraction of the prior. Here part of the prior is retained"),
    ("read in the covariance's eigenbasis; here the two-dimensional test flags", "read in the covariance's eigenbasis. Here the two-dimensional test flags"),
    ("as well as training seeds; here the result is bitwise independent", "as well as training seeds. Here the result is bitwise independent"),
    ("before and after unfolding; here a step between period groups", "before and after unfolding. Here a step between period groups"),
    ("whose mechanism is unidentified; it does not validate the five-observable distribution.", "whose mechanism is unidentified. It does not validate the five-observable distribution."),
    ("grade the estimator's bias under simulated truths; they do not identify", "grade the estimator's bias under simulated truths. They do not identify"),
    # section 7.1
    ("move opposite to it; the unfolded result retains part of its prior (section~\\ref{sec:prior}; table~\\ref{tab:outcomes}).",
     "move opposite to it. The unfolded result retains part of its prior (section~\\ref{sec:prior}, table~\\ref{tab:outcomes})."),
    ("(section~\\ref{sec:unfolding}); its effect on the result was not tested.", "(section~\\ref{sec:unfolding}). Its effect on the result was not tested."),
    ("under rounding-level changes of its inputs; an ensemble-averaged variant that meets it on the pseudo-data used to test stability is worse at one truth and is not adopted, so the instability of the data result itself is not mitigated",
     "under rounding-level changes of its inputs. An ensemble-averaged variant that meets it on the pseudo-data used to test stability is worse at one truth and is not adopted, and the instability of the data result itself is not mitigated"),
    ("for each reported quantity separately; simultaneous coverage of all of them is not graded.", "for each reported quantity separately. Simultaneous coverage of all of them is not graded."),
    ("(section~\\ref{sec:cov16}; \\nsec{sec:uq-2d-scope})", "(section~\\ref{sec:cov16} and \\nsec{sec:uq-2d-scope})"),
    ("of section~\\ref{sec:fd16}; the coverage tests vary it only", "of section~\\ref{sec:fd16}. The coverage tests vary it only"),
    ("All use simulated pseudo-data, so none tests the detector model against data.", "All use simulated pseudo-data, and none tests the detector model against data."),
]
n = 0
for a, b in R:
    assert s.count(a) == 1, (a[:90], s.count(a))
    s = s.replace(a, b)
    n += 1
# the draft-only \pubhold list: its items are separated by semicolons; they become full stops
i = s.index("\\pubhold{Where each record this paper relies on is published")
j = s.index("\n", i)
h = s[i:j]
h2 = h.replace(" only; record", " only. Record").replace(" only; records", " only. Records").replace("}; record \\holdrec", "}. Record \\holdrec").replace("}; records \\holdrec", "}. Records \\holdrec").replace("withholds; records", "withholds. Records")
s = s[:i] + h2 + s[j:]
open(p, "w").write(s)
print(n, "replacements; pubhold semicolons", h.count(";"), "->", h2.count(";"))
