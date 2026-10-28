r"""usage: python3 -I apply_b1.py ANALYSIS_NOTE_DIR -- r19 batch b1, Secs. I-III (variant B; r19/outline.md and the
director's rulings; DECISION-20261028-joseph-r19-variant-b-and-moves.md).

The edits:
- Table I is folded into the text (Q1) and its label tab:findings goes; the two sentences that cite it change.
- K4: the scope paragraph's hybrid-null sentences go.
- K11: the roadmap is rewritten to the new order.
- O6, and the SHORTEN of Sec. II's convention checks (the W clamp fraction, the truth-W residual, the prediction
  checks).
- K2, K3 and K5: the GiBUU test domain, "the tests of Sec. VI", and "the joint tests use".
- K6: the precision study's pointer to the tests.
- The sixteen-cell paragraph is split: the cells stay in III; the covariance opens Sec. IV as IV A (sec:cov16), in its
  own FIVED16 block with its Search line.

Held byte-identical, as ruled:
- Sec. I's third paragraph, which holds K1's calibration sentences and waits for the director's ruling on N1;
- the limitations paragraph, whose sentences step (c) owns.

Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once. Every fact that leaves
prints in the note, at a row of r19/ledger.md."""
import re, sys

D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))

T1_START = "% Register round r18: the caption's limitation clause changed with the director's approval"
P = "paper_body.tex"
t = open(f"{D}/{P}", encoding="utf-8").read()

# Table I: the block from its comment line through \end{table}
i = t.find(T1_START); j = t.find("\\end{table}", i)
if t.count(T1_START) != 1 or j < 0 or "\\label{tab:findings}" not in t[i:j]:
    sys.exit("Table I block not found exactly once")
t = t[:i] + t[j + len("\\end{table}"):].lstrip("\n")

E = [
 ("roadmap comment",
  "% Register round r17 (S1): the roadmap (main results, Table I, the secondary application) follows the scope below.",
  "% Register round r17 (S1): the roadmap follows the scope below. Register round r19 (b1; director, Q1): Table I is folded into the text; each of its rows prints in its section (r19/ledger.md, T rows), and the sixteen-cell result leads the introduction (the contribution paragraph and the limitations paragraph)."),
 ("K4 comment", "% Scope, one paragraph.",
  "% Scope, one paragraph. Register round r19 (variant B, K4; DECISION-20261028-joseph-r19-variant-b-and-moves.md): the hybrid-null scope sentences left with the tests and print in the note's sec_joint.tex (r19/move-pass.md, K4 rows); the sources below were theirs."),
 ("K4",
  r"The generator tests are conditional tests of simulated hybrid null hypotheses, under which the cross section equals a prediction on every cell of a fine five-observable grid, with the MINERvA Tune~v1 composition below that grid, as defined in Sec.~\ref{sec:hypotheses}.  They are calibrated within the implemented simulation model, whose detector model has no calorimetric recoil-response uncertainty.  Under the assumptions of Sec.~\ref{sec:calibration}, their decision rule controls the familywise error rate of the ten decisions at 5\%, on average over the nuisance priors.  The rejections are not physical exclusions of the generators and provide no measurement uncertainty.",
  ""),
 ("K11 roadmap",
  r"Sections~\ref{sec:repro2d}--\ref{sec:limits} give the validation studies that support the result and Sec.~\ref{sec:result16} the result itself; Table~\ref{tab:findings} lists each finding with its test. As an application, Sec.~\ref{sec:joint} tests generator predictions that the published muon-kinematic measurement already disfavours~\cite{MINERvA:2021owq}. Section~\ref{sec:limitations} summarizes the principal limitations.  The companion analysis note~\cite{AnalysisNote2026} gives the full validation record, the construction of the uncertainties, and the joint tests, and is cited below by section.",
  r"Section~\ref{sec:data} describes the data, the simulation and the observables, and Sec.~\ref{sec:method} the unfolding and the reporting cells. Section~\ref{sec:validation} gives the uncertainties and the validation studies, from the reproduction of the published two-dimensional measurement to the fake-data tests of the sixteen-cell result, and Sec.~\ref{sec:result16} gives the result and its comparison with generator predictions. Section~\ref{sec:conclusions} discusses what limits the estimator, and Sec.~\ref{sec:limitations} summarizes the principal limitations. The companion analysis note~\cite{AnalysisNote2026} gives the full validation record, the construction of the uncertainties, and simulation-calibrated tests of the generator predictions with their assumptions, and is cited below by section."),
 ("O6", r"  Replacing it by the charged-pion mass would change no true-$\Eavail$ bin by more than \SI{1.05}{\percent}.", ""),
 ("II clamp", r"This relation is exact apart from the clamp at $W^{2}=0$, which applies to \SI{1.5}{\percent} of simulated events.",
  r"This relation is exact apart from a clamp at $W^{2}=0$."),
 ("II truth W",
  r"Truth $W$ is therefore fixed by $(\pT,\pPar,q_{3})$ only up to that event-by-event angle, of about \SI{1}{mrad}, and the choice of $M$.  The resulting residual in truth $W$ is within \SI{\pm2}{MeV} for 68\% of events.",
  r"Truth $W$ is therefore fixed by $(\pT,\pPar,q_{3})$ only up to that event-by-event angle and the choice of $M$."),
 ("II predictions",
  r"The predictions compute $W$ with the neutron mass for every event.  In each cell where this choice was evaluated, it changes their coarse-cell predictions by at most about one Monte Carlo standard error.  Its effect cannot be evaluated for GiBUU.  The predictions also measure $\pT$ about their own neutrino axis, which differs from the analysis truth $\pT$ by \SI{\pm4}{MeV} for 68\% of events.",
  r"The predictions compute $W$ with the neutron mass for every event and measure $\pT$ about their own neutrino axis."),
 ("K3", r"The NuWro and GiBUU comparisons contain a target difference of this kind, which the tests of Sec.~\ref{sec:joint} do not correct.",
  r"The NuWro and GiBUU comparisons contain a target difference of this kind, which is not corrected."),
 ("K2a", r"The generator tests use a coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ whose edges",
  r"The joint cells form a coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ whose edges"),
 ("K2b", r" For GiBUU, whose sample lacks high-energy neutrinos, the domain is the \jtNcellsGiBUU{} supported cells with $\pPar<\SI{6}{GeV/c}$.", ""),
 ("K5", r"The three- and four-observable central values, the sixteen-cell five-observable result (Sec.~\ref{sec:result16}) and the joint tests use the joint-test estimator, a deterministic LightGBM",
  r"The three- and four-observable central values and the sixteen-cell five-observable result (Sec.~\ref{sec:result16}) use the joint-test estimator, a deterministic LightGBM"),
 ("K5 tail", r"removes most of the bias of purity-based subtraction at nominal truth in the highest-$W$ cells (Sec.~\ref{sec:validation}).",
  r"removes most of the bias of purity-based subtraction at nominal truth in the highest-$W$ cells (Sec.~\ref{sec:validation}); the note's simulation-calibrated tests use the same estimator."),
 ("K5 Table II", r"precision study; generator tests} \\", r"precision study} \\"),
 ("K6", r"  It motivates the different route to inference of Sec.~\ref{sec:joint}: after a descriptive comparison of the central values, the generator predictions are tested as hypotheses.", ""),
 ("Discussion, Table I", r"with its covariance and generator comparison; Table~\ref{tab:findings} summarizes the validation findings.",
  r"with its covariance and generator comparison."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1:
        sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]

# the sixteen-cell paragraph: the cells stay in III, the covariance opens IV as IV A
SPLIT = "and every reported cell passes the support rule."
REST0 = r"Unlike the envelope of Sec.~\ref{sec:uncertainty-status}, its model term is a covariance built from three generator shifts. The reported covariance is $C_{\mathrm{total}}+C_{\mathrm{resp}}$."
if t.count(SPLIT) != 1 or t.count(REST0) != 1:
    sys.exit("sixteen-cell split anchors not found once")
a = t.index(SPLIT) + len(SPLIT)
e = t.index("\n", a)                                  # the end of the paragraph line
rest = t[a:e].strip()
assert rest.startswith(REST0), rest[:80]
SEARCH = t.index("\n% Search: coverage of C_model at held-out truths", e)  # its Search line follows the paragraph
s_end = t.index("\n", SEARCH + 1)
search_line = t[SEARCH + 1:s_end]
assert t[e:SEARCH] == "", repr(t[e:SEARCH])
t = t[:a] + t[e:SEARCH] + t[s_end:]                    # III keeps the cells; the Search line goes with the covariance
rest = rest.replace(REST0, r"The reported covariance of the sixteen-cell result is $C_{\mathrm{total}}+C_{\mathrm{resp}}$. Unlike the envelope of Sec.~\ref{sec:uncertainty-status}, its model term is a covariance built from three generator shifts.", 1)
IVA = ("\\subsection{The reported covariance}\n\\label{sec:cov16}\n\n"
       "% FIVED16-BEGIN (r19 b1: the reported covariance of the sixteen-cell result, split from the cells paragraph of Sec. III)\n"
       + rest + "\n" + search_line + "\n% FIVED16-END\n\n")
anchor = "\\section{Uncertainties and validation}\n\\label{sec:validation}\n\n"
k = t.index(anchor) + len(anchor)
nxt = t.index("\n\n", k) + 2                         # IV A follows the section's lead paragraph (the validation design)
t = t[:nxt] + IVA + t[nxt:]
t = re.sub(r"\n{3,}", "\n\n", t)
open(f"{D}/{P}", "w", encoding="utf-8").write(t)
print("b1 applied: %d edits, Table I folded, the sixteen-cell paragraph split" % len(E))
