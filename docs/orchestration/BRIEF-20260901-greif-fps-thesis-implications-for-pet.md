# BRIEF — `arXiv:2608.28449` (Greif thesis): what the ATLAS full-phase-space measurement changes for PET/FPS

**Filed 2026-09-01. Repo claims measured at `HEAD = b7612e6adf67a459e4c86b927355140645da214a`.**

**Source.** Kevin Greif, *A High- and Variable-Dimensional Measurement of the Z+jets Differential
Cross Section with the ATLAS Experiment and Artificial Intelligence*, PhD thesis, UC Irvine,
submitted 28 Aug 2026. 313 pages. hep-ex. The ATLAS Z(→μμ)+jets cross section unfolded differential
in the full phase space of every final-state charged particle: minimum 6, **maximum 843**, mean 150
dimensions per event, 140.1 fb⁻¹, 247k selected data events.

**This is a literature brief. It adopts nothing, moves no gate, touches no estimator, covariance or
published number, and authorizes no compute.** Everything below is a statement about an external
document or about repo files at the sha above.

---

## 0. READ THIS BEFORE CITING ANY NUMBER FROM IT

**CITABLE FOR:** method, construction, prescription, and the qualitative results.

**NOT CITABLE FOR:** approved ATLAS numbers. §6.1 (p. 172) states verbatim: *"The analysis is
currently in ATLAS review and the paper is expected to be published in September of 2026. A
conference note summarizing the results of the analysis was recently released. Where possible,
approved plots taken from this conference note are used. The rest of the plots should be considered
a work in progress."* Figures 6.19–6.22 carry **ATLAS Internal** and 6.23–6.24 **ATLAS Simulation
Internal** watermarks — those are *not* approved. If a number from this thesis is to appear in our
note, cite the conference note or wait for the paper. A thesis is not an ATLAS result.

---

## 1. Bottom line, in order of how much it changes the PET picture

**(a) ATLAS benchmarked ParT against PET head-to-head for OmniFold and chose ParT — but PET was not
beaten decisively, and the comparison criterion is the transferable part.**

**(b) Their network-initialization uncertainty is structurally the `C_ML` object Gate 6 is blocked
on, and their construction makes the central/spread pairing coherent by definition rather than by
argument.**

**(c) ML noise is *engineered down*, not merely measured. Pretraining took their ensemble from 100
members to 10 and is described as the difference between publishable and not.**

**(d) The core FPS motivation — that a full-event unfold is less exposed to hidden variables — was
tested and DID NOT HOLD. This is the finding most likely to affect how PET is written up.**

---

## 2. ParT vs PET, measured by ATLAS (§6.3.1, pp. 183–184)

They considered four set-processing architectures for the OmniFold likelihood-ratio trainings:
**ParT** (Particle Transformer), **PET** (Point-Edge Transformer), **L-GATr** (Lorentz-equivariant),
and **LundNet** (graph over a Cambridge–Aachen clustering tree). Their characterization of PET, and
it is a fair one: *"PET is a similar model to ParT, with the primary distinction being that PET uses
local graph attention embeddings in place of ParT's pairwise features."*

The verdict, quoted:

> *"In general ParT and PET produce similar unfolding results, but ParT has overall better
> performance especially in the `Nch` observable. Notably PET is more accurate in the `mj2`
> observable. ParT is additionally slightly faster to train than PET, so is taken to be the best
> general purpose transformer architecture."*

**What this is and is not.** It is not a refutation of PET. It is one collaboration's ranking on one
final state, with a split decision — PET behind on charged multiplicity, ahead on sub-leading jet
mass — settled on general-purpose grounds plus training speed.

**The transferable part is the criterion, not the winner.** They ranked architectures by **the method
bias in the unfolded observables** (their Figures 6.5, 6.6), not by classifier AUC or validation loss.
Ranking a likelihood-ratio estimator by its classification metric measures the wrong object: the
quantity that reaches the cross section is the reweighting, and a better-separating classifier can
produce a worse unfold. **Action for this lane: check whether any PET-vs-alternative comparison in
our tree is decided on a classifier metric rather than on unfolded-observable bias.** If it is, the
comparison does not answer the question it is being used to answer.

**Also note L-GATr.** They state that *prior to this work, no uses of equivariant networks for
likelihood-ratio estimation tasks were documented* — so they tested one. If PET is ever revisited
against alternatives here, that is a live and cheap-to-name option, not an exotic one.

**A scope warning that runs the other way.** §5.6.3 of the same thesis endorses boosted decision
trees as likelihood-ratio estimators — but explicitly for *"low- and fixed-dimensional
measurements."* That sentence is being used by the scalar-5D lane
([`BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md`](BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md) §1),
where it applies. **It does not reach the full-event case**, where this same author uses transformers
throughout. If it turns up in PET-side prose it is a scope error.

---

## 3. Their `C_ML` (§6.4.2, p. 214) — and why their nominal cannot sit outside its own family

Their prescription, complete:

- **Ten independent OmniFold runs**, differing in the seed that initializes network weights and
  orders the training examples.
- **The central value is the event-by-event MEAN of the unfolded weights over the ten runs.**
- **The uncertainty is the standard deviation of the BIN COUNTS across the ten runs.**
- **Per-member binning is done for the NOMINAL ONLY.** For every systematic variation, only the mean
  weights are used. This is what makes the full grid affordable.

**The structural point.** Because the reported central value *is* the ensemble mean, the nominal
cannot lie outside its own seed ensemble. That is not a result they had to defend; it is a property
of the construction. Compare with how a single-seed nominal paired against a separately-generated
family behaves: the offset between the two is then a real quantity that has to be explained, and it
is exactly the class of object that has caused trouble here.

**Do not over-read this into `OI-126`.** Their seed ensemble is not a bootstrap family, and the
`OI-126` anomaly is about a *bootstrap* family. §8 below states precisely what this thesis does and
does not settle. The lesson available here is narrow and real: *if the reported central value is
defined as the ensemble mean over the same family that supplies the spread, one whole class of
"nominal sits outside its family" question is closed by construction rather than by investigation.*

**Cross-reference.** `LITERATURE_NOTES.md`'s ensemble-mean audit finding already recommends promoting
the ensemble mean to the central value on T2K / Practical Guide grounds. This is a third, independent,
LHC-scale instance of the same convention — and it extends it with the systematics rule above, which
that finding does not carry.

---

## 4. Pretraining: the ensemble size is a consequence, not a constant (§6.3.2)

The number that matters: **the 2024 Multifold round used 100-member ensembles; this measurement uses
10.** The reduction was bought, not assumed.

Mechanism: ten ParT models are pretrained **per level** (detector and particle) on an auxiliary
**MC-versus-MC** classification task — MG5+Py8 vs Sherpa, ~14M events, dedicated partitions to keep
the unfolding partitions clean. Each OmniFold step-1 training starts from one of the ten detector-level
checkpoints and each step-2 from one of the ten particle-level ones. Ten distinct pretrained starting
points, deliberately, *"to avoid biasing the measurement by relying on the representations learned by
a single pretrained starting point."*

Effect, as they report it: the run-to-run Wasserstein spread drops markedly (Fig. 6.12), the method
bias drops *"dramatically … especially in the tails of the distribution where the statistics are most
limited"* (Fig. 6.13), and the initialization uncertainty drops modestly. Their assessment is blunt:
*"The method bias produced by Omnifold without the pretraining is likely too large to make a
publishable measurement in these particular observables."* And: *"It was only after including the
pretraining step that the method bias produced by the full-phase-space unfolding was close to the
method bias produced by Multifold and IBU."*

**Why this is the most actionable item in the brief.** It reframes `C_ML` from a quantity to be
measured into a quantity to be *reduced first*. Their justification for pretraining is the same
condition we are in: 247k selected data events against a 1.6M-parameter model is *"an order of
magnitude less training data than is typically advised."* The step-1 trainings are the data-limited
ones; step 2 is not. They also make the general claim that data-limited likelihood-ratio estimation,
not jet tagging, is the application that most rewards HEP foundation models (§4.4).

**This brief does not propose running it.** Pretraining PET on an auxiliary MC-vs-MC task is new
compute, and new compute goes through the named-decision route.

---

## 5. The FPS motivation was tested and did not hold (§6.4.1 pp. 212, §6.5.2)

This is the item to read most carefully, because it cuts against the usual argument for full-event
input.

They state the expectation plainly and then refute it:

> *"a possible advantage of a high-dimensional unfolding is that it is less sensitive to hidden
> variables since it is differential in more observables. … However this does not account for hidden
> variables that are not constrained by the detector altogether … These are hidden variables even for
> a full-phase-space unfolding."*

And on measuring it: *"naively an Omnifold based measurement should be less sensitive to hidden
variables and have smaller hidden variable uncertainties, but this expectation is not borne out in
this measurement."* Their hidden-variable uncertainties came out **slightly larger** than the
one-dimensional IBU baseline's, worst in the substructure observables.

Two causes they identify:

1. **OmniFold is data-limited in the tails**, because the step-1 networks train on data. IBU bins over
   low-statistics regions; the unbinned unfold cannot, since the binning is applied only afterwards.
   *"Omnifold simply provides a less accurate unfolding in the tails … due to the limited data."*
2. **High dimensionality only helps against hidden variables that the detector constrains.** Their
   dominant one — the truth charged-hadron fractions (π/K/p/other) — is unconstrained at detector
   level under the pion mass assumption. Figure 6.20 shows the unfolding returns the prior **exactly**
   for it: no shift at all. A dedicated *hadron composition* uncertainty had to be invented to cover it,
   and it dominates the leading-jet-mass budget.

**Net (§6.5.3):** against their own 24-observable Multifold round, full phase space cost *"almost no
reduction in precision."* Not a gain — an approximate tie, purchased with the pretraining of §4.

**Consequence for how PET is written up.** If any PET/FPS text in our tree argues that full-event
input *reduces* hidden-variable exposure, this is a published-track counterexample from the largest
such measurement in existence. The defensible version of the argument is the one they actually make
in §5.3.1 and §6.7: full phase space buys **flexibility and information preservation** — the result
is a dataset projectable onto any observable without redoing the analysis — not accuracy. That
framing is entirely compatible with PET being diagnostic and method-development here (AGENTS.md,
Joseph's 2026-08-20 ruling); it just means the *reason* has to be flexibility, not hidden-variable
immunity.

---

## 6. Two instruments worth copying

**(a) The hidden-variable uncertainty construction (§6.4.1).** Reweight the *alternative* generator's
**particle level** to match the nominal generator's **particle level**, in a set of observables that
are all functions of the phase space the unfold already sees. What survives that reweighting differs
only in variables the unfold does *not* see. Then swap that sample in as the unfolding MC and take the
difference. Clean, and it isolates the intended quantity instead of conflating it with prior shape.

**(b) `OmniSequential` (§6.4, pp. 208–209).** A deliberately **non-ML** reweighter: Scott's-rule
binning (log binning above skewness 2), pick the observable with the worst χ² pull
`z = (χ² − ndof)/√(2·ndof)`, Gaussian-kernel fit of the target/source ratio, reweight, repeat until
every observable has `z < 2`. Its stated purpose is *"to avoid over-reliance on ML based likelihood
ratio estimation techniques,"* and it is what builds both of their unfolding uncertainties. The
principle generalizes past their implementation: **do not estimate an ML method's bias with the same
ML machinery whose bias you are estimating.** Worth checking whether any of our unfolding-uncertainty
constructions are circular in that sense.

---

## 7. The validation instrument and the release protocol (§6.5.1, §6.7)

Their closure test is a **binned χ² goodness-of-fit against the pseudodata truth using the full
covariance**, run across 26 observables, reported as a p-value per observable. It *"allows the method
bias and uncertainty model to be **jointly assessed**"* — one statistic, both objects.

Three construction details that are easy to get wrong:

- **Experimental systematics are EXCLUDED from Σ for this test**, because their nuisance parameters
  are held at nominal in the pseudodata. Including uncertainties that were not varied in the
  pseudodata would be a silent free pass.
- **Gaussian-kernel smoothing is applied to the hidden-variable uncertainty before it fills Σ** — it
  is built from an independent particle-level sample and fluctuates — **except** in the jet-mass
  observables, where the uncertainty has a genuinely sharp shape that smoothing distorted. A
  documented exception, not a blanket rule.
- **Per-bin overshoot is tolerated when the correlated χ² passes.** In `mj1` the method bias exceeds
  the total uncertainty in a few bins, yet p ≈ 0.26. The covariance-aware statistic is the arbiter;
  the bin-by-bin eyeball is not.

Their outcome: all 26 observables clear p > 0.05, minimum 0.0556 (sub-leading track-jet mass).
*(Spot-checked: five of Table 6.3's p-values recomputed from its own χ² and DoF reproduce to four
decimals, so the table is at least internally consistent.)*

**The release protocol is the part with no analogue here.** The public unbinned spectra are to ship
with two binding usage requirements (§6.7): **(i)** at least **5,000 effective events** in every bin
of any histogram a user constructs from the particle-level sample; **(ii)** the user **must re-run the
pseudodata measurement and compute a χ²/p-value in their own binning and phase space**. Their reason:
*"the unfolded spectra contain truth-level information … that is not constrained at detector level.
Observables sensitive to such hidden variables will fail this check, indicating that the observables
cannot be constrained with this measurement."*

That is the honest answer to a problem PET/FPS shares: an unbinned product's observable space is
unbounded, so it cannot be certified once. They do not certify it once — **they ship the test as an
obligation on the consumer.** `LITERATURE_NOTES.md` currently files binning-independent GoF as an
open problem, which it remains; this is a practical route around it rather than a solution to it.

---

## 8. What this thesis does NOT settle

**It does not solve `OI-126`, and should not be cited as bearing on it.** The bootstrap gets one
paragraph and **five mentions in 313 pages** (§6.4, p. 208): Poisson(λ=1) multiplication of event
weights, 100 replicas for the data statistical uncertainty, 25 for the MC training-set statistical
uncertainty, and *"the final uncertainty is then the variance in the result produced by this ensemble
of bootstraps."* There is **no** treatment of a nominal-to-bootstrap-mean offset, no centering
discussion, and no diagnostic for a nominal sitting outside its bootstrap family. They quote the
spread and never use the offset. That is a construction in which the question does not surface — not
an answer to it.

**Nobody in this space is doing a coverage study, including them.** The string `coverag` appears
**once** in the extracted text of the whole thesis, and it is about detector acceptance in the forward
region — not statistical coverage. *(Scope: a case-insensitive search over the `pdftotext -layout`
extraction of the full PDF; text rendered inside figure images would not be captured, though body
text is.)* Their own statement (§6.5.1) is that *"running sufficient bootstraps to observe this is
computationally infeasible"*, so they use the asymptotic χ² and a p-value instead.

**This does not make the coverage demand on `C_stat` wrong.** It calibrates it: that demand is a
standard *above* current field practice, not a baseline this project is failing to clear. Useful to
know before more effort is spent treating it as a gap relative to the literature.

**Two problems they name as open (§6.7):** acceptance effects in unbinned unfolding when the event
selection involves jets — *"methods … have been proposed but have not yet been applied in a real
analysis"* — and cost: **~25,000 transformer fine-tunings, ~400,000 A100 GPU-hours**, as stated.

---

## 9. What this brief does not do

It proposes no code change, no re-run, no adoption, no gate movement, and no compute. Items in §2
(comparison criterion), §5 (how PET is motivated in prose) and §6 (circularity check) are things this
lane can *look at* in existing artifacts without running anything. Item §4 (pretraining) is new
compute and is not authorized by this document.
