# AUDIT 2026-08-19 — the analysis note against the committed record

**Lane D (verifier), read-only. TRANCHES 1–4, plus the pre-edit VERIFICATION BASELINE at §V.** Commissioned after an outside reader found `ISSUE-57` on
a first pass through `docs/analysis-note/`, which nobody inside the repository had found. **The inference
that there are more is correct: fourteen findings, thirteen of them new.**

**ROLE CHANGE.** Joseph authorised paper corrections and a push (`b8f74fbe`). **Lane B edits; this
lane verifies and does not edit.** §V records the pre-edit digests and the checks, committed before
any edit exists — a verification baseline written after the diff is not one.

> **TRANCHE 3 HEADLINE.** Finding 6 is worse than a label error — **the paper build prints
> $\chi^{2}=3.66$, which is the `exact`-GBT value, while naming LightGBM as the estimator, and the note
> records LightGBM as giving $2.65$.** The headline tension number in the external document does not
> belong to the estimator that document names. And the note's own `check_dead_containment.py` **passes
> while naming `\petGbdtGap` as a body it cannot cover** — `\petGbdtGap` is `9`, which is exactly the
> value finding 7 found printing unstruck in the paper build.
>
> **CORRECTION TO MY OWN TRANCHES 1 AND 2.** I wrote that `\dead{}` is *"used 19 times."* **That was a
> line count reported as an occurrence count** — `grep -c` counts matching lines. The checker, which
> parses braced bodies, reports **26 uses on those 19 lines.** The argument is unaffected (the count that
> matters is `sec_systematics.tex`'s **zero**), but a tally I published was the wrong unit.

> ### TRANCHE 2 CHANGED THE PRIORITY ORDER. READ §0 FIRST.
>
> **The build map inverts tranche 1's ranking.** Tranche 1's two `HIGH` findings are **note-build only**.
> The two findings that reach the **paper** build — the externally-facing one — are both new in tranche 2,
> and one of tranche 1's `MED` findings turns out to print in **all three** builds. **What is worst inside
> the collaboration is not what is worst outside it, and the two lists barely overlap.**

**Nothing under `docs/analysis-note/` was edited and nothing will be by this lane.** This is a routed
defect list for the note's owner, not a patch. No authority file was edited either. Measured at
`origin/main` after `git fetch && git rebase`; every quote below was read this turn from both sides.

**Severity key.** `HIGH` — the note asserts something the record contradicts, in publication text.
`MED` — a governance or traceability gap, not a wrong number. `LOW` — a citation that does not support
what it is attached to. Where I cannot tell which side is wrong I say so, because the remedy differs.

---

## Summary

**`builds` is the column to read first.** `N` = collaboration note, `P` = **paper (external)**, `Pr` = primer.

| # | sev | builds | what | note | authority | which side is wrong |
|---|---|---|---|---|---|---|
| **6** | **HIGH** | **P** | the paper names **LightGBM** as *"the learners"*; the note says the published central value is the **`exact` sklearn** backend, and that the mismatch is *"a stated property of the measurement"* | `paper_body.tex:47-48` | `sec_method.tex:135-141` | **the paper build** |
| **7** | **MED-HIGH** | **P** | the paper states the PET–GBDT **9 %** agreement as an unstruck inline literal; the note strikes that comparison as `niter`=2 legacy, and the paper's own quarantine sentence does not reach those grounds | `paper_body.tex:146`, caption `:161-166` | `sec_pet.tex:40-62`; `values.tex:65-74` | **the paper build** |
| 3 | **MED** | **N + P + Pr** | 16 of 70 `values.tex` macros have no `VALIDATION_LEDGER` row, against `CLAUDE.md`'s canonical-home rule — and three of them print in the paper and primer | `values.tex`, 16 lines listed | `CLAUDE.md` routing table | **neither — a gap** |
| **8** | **CANNOT TELL** | **P** | `\petClosure` prints twice in the paper build; `values.tex`'s PET block header calls the block *"NOT QUOTABLE … niter=2 legacy"* but only two of its three macros carry per-line legacy markers | `paper_body.tex:145,164` | `values.tex:65-74` | **unresolved — owner's call** |
| 1 | **HIGH** | N | the full-event `C_stat` bootstrap is described as **one** stream; the note says **two** elsewhere; the record specifies **three** | `app_statmethods.tex:1472-1476`, `:1479-1480` | `DETERMINATION-20260817-lanec-cstat-object-is-total-statistics.md:27,48` | **the note** |
| 2 | **HIGH** | N | four dead `\gbdtFive*` values print as unmarked prose while the note's own `\dead{}` marker is used 26× elsewhere | `sec_systematics.tex:163,165,166,168` | `VALIDATION_LEDGER.md:916,940`; `INDEX-retracted-and-superseded-values.md` | **the note** |
| 4 | LOW | N | `CLM-012` cited as authority for the `niter=3` policy, which `CLM-012` does not state | `sec_pet.tex:55-56` | `CLAIMS.md` `CLM-012` | **the note** |
| **9** | LOW | N | *"production iteration count `n=5`"* and *"the campaign's pinned policy is `niter`=3"* stand unreconciled | `sec_method.tex:145-147`; `sec_pet.tex:55-56` | — | **neither — a scope hazard** |
| 5 | INFO | N | `CLM-010`/`CLM-012` carry live independence caveats; the note's use is narrower than the caveat's scope | `sec_pet.tex:55-56` | `CLAIMS.md`; `DETERMINATION-20260818-lanec-clm012-status-conflates-two-claims.md` | **probably neither** |
| **12** | **MED-HIGH** | N | the note's own containment check **passes while naming `\petGbdtGap` as uncoverable**, and by construction cannot see a dead value that was never marked | `check_dead_containment.py` | its own output, run this turn | **neither — an instrument gap, currently occupied** |
| **11** | **MED** | N | three reviewer-comment macros render as visible `[GK: …]` text in the note PDF, and are **undefined in both external wrappers** — a latent build-breaker on the normal distillation operation | `main_note.tex:17-19`; 13 uses | — | **the note** |
| **13** | **CANNOT TELL** | N | `sec_validation`'s unstruck PET shape comparison may be the same 2M-event run whose absolute comparison `sec_pet` strikes | `sec_validation.tex:96-98,146-159` | `sec_pet.tex:47-62` | **unresolved — owner's call** |
| **14** | **LOW-MED** | **P + Pr** | both external builds omit the analysis's one binned step; no paper sentence is falsified, but the measurement's only binning dependence is absent from the document whose distinction is unbinnedness | `paper_body.tex`, `primer_body.tex` (0 hits) | `sec_method.tex:34-52` | **an omission — owner's call** |

---

## 0. THE BUILD MAP — measured, and it reorders the remedies

`main_*.tex` input lists, read this turn:

| build | inputs |
|---|---|
| **note** (`main_note.tex`) | `preamble`, `values`, **all 12 `sec_*`**, **all 4 `app_*`** |
| **paper** (`main_paper.tex`) | `preamble`, `values`, **`paper_body` and nothing else** |
| **primer** (`main_primer.tex`) | `preamble`, `values`, **`primer_body` and nothing else** |

**`values.tex` is input by all three — but defining a macro is not printing it**, and that distinction is
what the reach question turns on. Measured per build by enumerating which of the 70 macro names actually
appear:

```
paper_body.tex prints 12:  binsTen chiPaper fpsAbove fpsAnchor(x2) fpsSigma petClosure(x2)
                           pullRMS(x2) ratioTot sigTwoD sigTwoDpaper uqMedian uqPaper
primer_body.tex prints 3:  binsTen uqMedian uqPaper
```

**Neither external build prints any `\gbdtFive*`, `\petRatio`, `\petGbdtGap`, `\petTotal*` or
`\petFourMedian` macro**, and neither uses `\dead{}` at all (`grep` for the five dead-macro families
returns nothing in both; a `\\[a-zA-Z]+` control over the same file returns 92, so the search is live).

**Consequences, and they are the point of doing this before the read:**

1. **Findings 1, 2, 4, 5, 9 are note-only.** Serious, but internal — they reach collaborators, not
   readers outside it. Tranche 1 ranked 1 and 2 at the top; **on external exposure they are not.**
2. **Finding 3 reaches all three builds.** `\uqMedian`, `\uqPaper` and `\binsTen` print in the paper *and*
   the primer. So the one finding I rated `MED` is the only tranche-1 finding whose numbers face outward,
   and the gap it names — sourced to a designated-mutable `*_STATUS.md` rather than the ledger — applies
   to the **headline uncertainty budget in the external document.**
3. **The paper build has its own defects that the note build does not have**, because it is a
   re-written distillation rather than an extract. **Findings 6 and 7 exist only there.** An audit of the
   note that assumed the paper is a subset would have found neither.

**The structural cause, and it is worth stating once: `paper_body.tex:1-6`'s own header says it is a
*"selective, results-first publication-style distillation"* whose *"cross-checks are one-line"* and whose
full methodology *"live[s] in the companion analysis note."* A one-line compression of a caveated claim
is exactly where the caveat is dropped, and findings 6 and 7 are both that.**

---

## 1. HIGH — `ISSUE-57` confirmed, and it is wider than reported: the note gives THREE different stream counts for one object

### 1a. The reported defect, verified independently

`docs/analysis-note/app_statmethods.tex:1471-1476`, §`app:cstatlimit`, *"Construction, stated as a
method choice"*:

> The statistical covariance for the full-event extended-phase-space measurement is built from a $50$-member
> replica family. Each member repeats the whole analysis --- background-subtracted target construction,
> estimator training, and cross-section extraction --- on an independent $\mathrm{Poisson}(1)$ bootstrap of
> **the measured leg**, so that a member's target is the nominal target multiplied by that draw
> (\S\ref{app:poisson}).

`docs/orchestration/DETERMINATION-20260817-lanec-cstat-object-is-total-statistics.md`, quoting Gate 5 F7
at `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md:738-758`, *"For every replica, in this exact order"*:

> *"Enumerate complete, ordered **data, signal-MC, and background-MC** inventories before any training
> subset."* … *"Apply data factors to data weights, **signal factors everywhere signal MC is used**, and
> background factors to the negative background injection."*

and its own ruling at `:48`:

> **The `OI-126` row's *"a Poisson bootstrap of the measured leg"* misdescribes the construction, and the
> misdescription is against the DAG rather than against the spec.**

**Confirmed. Both quotes are as reported.** The determination's ruling is that three-stream resampling is
**specified**, not chosen — *"Signal-MC is named in three of the six steps."*

### 1b. NEW — a SECOND instance five lines later, in the same subsection

`:1479-1480`, which the report did not cover:

> A $\mathrm{Poisson}(1)$ bootstrap of **the measured sample** is the standard non-parametric stand-in for
> measured-statistics uncertainty…

**Same misdescription, different words, so a search-and-replace on the first will not find it.** It also
does load-bearing rhetorical work the first does not: it is the sentence that justifies the method by
appeal to standard practice, and the appeal only holds for the object it names.

### 1c. NEW, and the strongest part — the note contradicts ITSELF, twice over

Three descriptions of *"our bootstrap"* live in one file:

| site | streams | exact words |
|---|---|---|
| `app_statmethods.tex:143-160`, §`sec:bootstrap` | **TWO** | *"The combined data-statistical and MC-statistical variance"*; *"Draw per-event Poisson(1) factors $b^{\text{data},(k)}$ for every data event and $b^{\text{MC},(k)}$ for every MC event, using two independent sub-RNGs (a data RNG seeded from $k$, and an MC RNG seeded from $k+10^{7}$)"* |
| `app_statmethods.tex:861-864` | **TWO** | *"our bootstrap already draws independent Poisson($1$) multipliers on **both** data and MC per replica (\S\ref{sec:bootstrap})"* |
| `app_statmethods.tex:1472-1476`, §`app:cstatlimit` | **ONE** | *"a Poisson(1) bootstrap of **the measured leg**"* |
| the record — Gate 5 F7 | **THREE** | data, signal-MC, background-MC, coherent per inventory member |

**So the misdescription is not a stale draft inherited from an earlier object — it disagrees with the
note's own §`sec:bootstrap`, which the note elsewhere cites as the definition.** That matters for the
remedy: this is not "update one sentence to the current construction", it is "the note states two
different constructions for what a reader will take to be one procedure, and neither matches the DAG."

**The caveat, stated because it changes the remedy and I cannot settle it from documents.** §`sec:bootstrap`
and `:861-864` sit in the **2D demonstrator** material; §`app:cstatlimit` is explicitly the **full-event
extended-phase-space** measurement. **Two different pipelines may legitimately resample differently.** If
so, nothing at any of the three sites says so, and the shared phrase *"our bootstrap"* plus a `\S\ref`
from one to the other invites the reader to assume identity. **Either way the note needs an edit; which
edit depends on a fact only the pipeline's owner has.** What is *not* in doubt is `:1472-1476` and
`:1479-1480` against the full-event DAG — those are wrong on the determination's own ruling.

### 1d. NEW — the cross-reference cannot support the claim it is attached to

The measured-leg sentence ends `(\S\ref{app:poisson})`. Read, `app_statmethods.tex:1401-1428`
§`app:poisson` is the **multinomial → independent-Poisson limit theorem** and nothing else — binomial
marginals, the dropped $\sum n_i = N$ constraint, the $\mathcal{O}(1/\sqrt{N})$ error. **It contains no
statement about which legs are resampled.** The citation is real, resolvable, and about a different
question; a reader checking the measured-leg claim against it finds a correct derivation and no
contradiction, because the reference cannot disagree with the sentence it is attached to.

### 1e. Why this outranks a wording fix — the described object is now a SEPARATE declared product

`RULING-20260817-lanec-data-only-cstat-is-a-second-product.md:31-35` establishes two products, not one
object with two descriptions:

> | product | what varies | role |
> | **`C_stat^data`** | data factors only; signal and background factors **exactly 1** | **the published `σ_stat`** — field-comparable, not reducible by generating MC |
> | **`C_stat^total`** | all three, as Gate 5 F7 specifies | **existing, unchanged**, `GATE5_CSTAT_N50.npz` |

and at `:17`, Joseph's argument as the ruling records it: the total-statistics object is

> an error that is **~88% MC statistics by variance**

**So the note attaches the description of `C_stat^data` to the numbers of `C_stat^total`, and by the
record the two differ by the dominant term.** A reader takes the band at `:1496-1505` as a
field-comparable `σ_stat`; the record says that object is a different, not-yet-published product, and
that what the note is actually reporting is ~88% MC statistics. **That is a physics-interpretation defect,
not a wording one, and it is the reason I rate this above finding 2.**

**One thing I checked and it is NOT a contradiction, recorded so nobody re-raises it.** `:876-878` reports
*"the variance split $77\%$ data / $23\%$ MC"*. That is the **2D** split bootstrap, a different
measurement from the full-event family the ~88% describes. **The two are not in conflict.** The hazard is
comprehension, not arithmetic: a reader carrying 77/23 forward into §`app:cstatlimit` inverts the actual
composition, and nothing in the note warns them.

---

## 2. HIGH — four dead values print as unmarked prose, and the note's own strike mechanism is used 26 times elsewhere

**The values.** `docs/analysis-note/values.tex:57-60`:

```
\gbdtFiveBlockMedian  13.36      \gbdtFiveAdoptTrace  5.81e-38
\gbdtFiveMeanShift    1.65e-38   \gbdtFiveCVTrace     6.24e-38
```

**All four are consumed as prose in one continuous block**, `sec_systematics.tex:163` (block median),
`:165` (adopt trace), `:166` (mean shift), `:168` (CV trace) — verified this turn, and matching
`PROCEDURE-gbdtFive-macro-update.md:23-27`, which adds *"There is **no second consumption site anywhere
in the note.**"*

**The authority.** `VALIDATION_LEDGER.md:940-943`:

> **The corrected totals are ~9% SMALLER than the values currently in `values.tex`** (`\gbdtFiveAdoptTrace`
> 5.81e-38 → 5.26e-38; `\gbdtFiveCVTrace` 6.24e-38 → 5.66e-38).

and `INDEX-retracted-and-superseded-values.md`, the `\gbdtFive*` row:

> `docs/analysis-note/values.tex:57-60`, **all four unmarked**; and **all four print as prose** … dead on
> **two independent grounds** — the 2026-07-12 quarantine class *and* the J28 flux correction.
> **`\gbdtFiveMeanShift` moves UP 13.6% while the other three move DOWN ~9%, so no uniform scale factor
> patches them** and anyone assuming one gets the mean shift backwards.

**Still live at `origin/main` today** — I re-read all four macro lines and all four prose sites.

### What is new here is not the defect, it is that the note already has the fix and did not apply it

`preamble.tex:29` defines `\newcommand{\dead}[1]{\mbox{\textcolor{gray}{\sout{\ensuremath{#1}}}}}`, and it
is used **26 times, on 19 lines** — `app_statmethods.tex` and `sec_pet.tex` only, per the note's own
checker — including a model treatment at
`sec_pet.tex:91`, *"ratio is $\dead{\petRatio}$ --- **struck: `niter`$=$2 legacy**"*, and `:68-74`, which
explains *why* a struck value is struck and points at the retraction index. **`sec_systematics.tex`
contains zero uses of `\dead{}`.** So the note is not missing a mechanism, a vocabulary, or a precedent;
one dead family was struck and another was not, and the surviving one is the 5D covariance.

### The aggravating detail, which I have not seen recorded

`sec_systematics.tex:175-176`, **eight lines after the four dead numbers**, reads:

> \SI{0.09}{\percent} before the flux (J28) correction and \SI{0.18}{\percent} after it

**J28 is named, by name, in the same paragraph** — as a correction the passage has evidently accounted
for. A reader who notices J28 there has every reason to conclude the covariance quoted eight lines above
is post-J28. It is pre-J28, and J28 is one of the two grounds on which it is dead. **The paragraph is
more misleading than silence would be.**

**Which side is wrong: the note.** The record is self-consistent, knows the values are dead, has said so
in three places, and has written the update procedure. **Note that the procedure explicitly withholds
authorization** (`PROCEDURE…:5-9`, *"Nothing below authorizes an edit"*; the binding gate is the
2026-07-12 quarantine, *"of whose **seven** construction causes exactly **one** is discharged"*). **So the
remedy available today is to STRIKE, not to replace** — `\dead{}` needs no adopted replacement magnitude,
and `VALIDATION_LEDGER.md:916-921` warns that the corrected pair is **not a drop-in** anyway, differing
from the current values in two inputs, one of them silent (`--combined` passed vs not).

---

## 3. MED — 16 of 70 `values.tex` macros have no `VALIDATION_LEDGER` row

`CLAUDE.md`'s routing table names `VALIDATION_LEDGER.md` as the canonical home for *"Verified numbers
(anything technote-quoted)"*. Measured across all 70 `\newcommand` macros in `values.tex`, **16 have no
occurrence in `VALIDATION_LEDGER.md` at any rounding**:

```
:16  \sigTwoDpaper   3.039e-38     :63  \gbdtAiEstFrac  87.5        :115 \nwPctTot    -0.13
:18  \medianBinRatio 1.006         :84  \pcMiss         37.9        :118 \nwWorstBin  -12.6
:20  \binsTen        94.1          :94  \pcEavailMean   -6.4        :127 \nwStatRatio 0.982
:21  \binsTwenty     98.5          :112 \nwSigPur       3.0727e-38  :130 \nwSpWithin  141/148
:42  \uqMedian       6.87          :113 \nwSigNeg       3.0687e-38
:44  \fluxBand       4.99          :114 \nwRatioTot     0.9987
```

**They are NOT untraceable, and reporting them as such would have been wrong.** I widened the search to
the whole repository outside the note — 2,142 files — and **all 16 are found**, mostly in
`2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md` and `2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md`.
The headline uncertainty budget is a clean example: `\uqMedian` 6.87, `\uqPaper` 6.86 and `\fluxBand` 4.99
all sit at `2D_OMNIFOLD_STUDY_STATUS.md:101-107,127-128` (*"Flux 4.99 %"*; *"6.865 %"* as the block sum,
which rounds to the note's 6.87).

**So the finding is a governance gap, not a correctness one: the note's headline uncertainty budget is
sourced to a `*_STATUS.md`, which `CLAUDE.md` designates as *"Current state per workstream"*, not to the
ledger it designates for quoted numbers.** `*_STATUS.md` is by definition current-state and therefore
mutable; the ledger is the artifact that carries verification. A number quoted in publication text from a
status file has no verification record attached to it and nothing notices when the status file moves on.

**Method caveats, both of which bound this finding.** (i) The search was exact-string plus rounding
variants; a ledger row that renders the same quantity at a different precision would be missed, so **16 is
an upper bound on the gap.** I checked the two most load-bearing by hand (`grep -cE '6\.86[0-9]'` → 0 with
a `6\.8` control returning 1; `grep -cE '4\.99|4\.98'` → 0) and both are genuine. (ii) A string hit does
not prove the row is *about* that quantity, so I have not claimed the other 54 are properly ledgered —
only that these 16 are not.

---

## 4. LOW — `CLM-012` is cited as authority for a policy it does not state

`docs/analysis-note/sec_pet.tex:55-56`:

> The campaign's pinned policy is \texttt{niter}${}={}$3 (CLM-010, CLM-012, \textsc{frozen}), and
> full-event PET moved to it.

`CLAIMS.md`, the two rows, verbatim:

- **`CLM-010`** — *"The `niter` 2->3 switch is justified as REGULARIZATION, not merely as gate behaviour…"*
  **This is the niter claim and the citation is correct.**
- **`CLM-012`** — *"D2's `recovery >= 0.80` bar sits above what an estimator limited only by reco
  acceptance can reach, so most of the measured shortfall is specification rather than estimator
  quality."* **This says nothing about `niter`.**

`CLM-012` was *evaluated at* `k=3` — its `data/config hash` field reads `k=3, R=1.1240802949941018` — but
being evaluated at a configuration is not establishing it as policy. **The note is wrong here**, harmlessly
in substance (the policy is real and `CLM-010` establishes it) but not harmlessly in form: a reader who
follows the second citation to check the pinned policy finds a claim about an acceptance ceiling. One
citation doing the work of two reads as corroboration when it is not — the same shape the record calls out
elsewhere as corroboration-count-is-not-source-count.

Also minor: `\textsc{frozen}` is not one of `CLAIMS.md`'s allowed status values (`PROVED`,
`VERIFIED-NUMERIC`, `VERIFIED-CODE`, `CITED`, `ASSUMED`, `OPEN`, `REFUTED`). It reads as a claim state in
a parenthesis that otherwise contains claim ids. If it describes the *policy* rather than the claims, it
is fine and only ambiguous.

---

## 5. INFO — the two cited claims carry live independence caveats; the note's use is narrower

Recorded so the next reader does not have to re-derive that this is **probably not** a defect.

- **`CLM-010`**, status `VERIFIED-NUMERIC`, own evidence cell: *"the assembly of the two halves into one
  bias-variance statement is so far **single-source (this session)** and has NOT been independently
  checked."*
- **`CLM-012`**, status `VERIFIED-NUMERIC`, and its status is under active challenge:
  `DETERMINATION-20260818-lanec-clm012-status-conflates-two-claims.md` rules that *"the row states TWO
  claims of different strength"*, that Gate 1 is *"a REPLAY: the same route, twice"*, and that
  *"a route traversed twice is one route."*

**Neither caveat reaches what the note asserts.** The note cites them for *"the pinned policy is
`niter`=3"* — a governance fact — not for the bias-variance magnitude or the acceptance ceiling, which is
where the independence gaps sit. **Reported as INFO rather than as a defect**, and it would become one if
the note ever quotes `CLM-010`'s `3.8008% → 2.1876%` or `CLM-012`'s recovery numbers, which it does not.

---

## 6. HIGH, **PAPER BUILD** — the external document names the wrong estimator for the published central value

`docs/analysis-note/paper_body.tex:47-48`:

> We use gradient-boosted decision trees (**LightGBM**, 100 trees, 5 iterations) as the learners

`docs/analysis-note/sec_method.tex:135-141`, the note build's account of the same thing:

> **The published central value is produced with the `exact` backend** (sklearn `GradientBoosting`,
> single-threaded exact-split CART): the production launcher passes no `--estimator` flag and therefore
> takes the driver's default. **The uncertainty ensemble** --- the systematic universe sweep and the
> Poisson bootstrap --- **is produced with LightGBM** ($100$ trees, $8$ leaves, learning rate $0.1$ …),
> which both of those launchers request explicitly. *The central value and its covariance are therefore
> not estimator-matched*; … **but this should be read as a stated property of the measurement rather than
> an incidental configuration detail.**

**The paper build attributes the central value to the estimator that produced the covariance, and omits
the mismatch entirely.** `grep -niE 'exact|sklearn|GradientBoosting|estimator-matched|backend'` over
`paper_body.tex` returns two hits, neither of them the backend (`Histogramming` at `:50`, and `:154`'s
quarantine sentence). **The `exact` backend is never named in the external document.**

**Which side is wrong: the paper build.** The note's account is specific, sourced to launcher behaviour
(*"passes no `--estimator` flag"*), and internally consistent; the paper's is a one-line compression that
picked the wrong one of two. **And the omitted clause is the one the note explicitly says must not be
read as incidental** — a reader of the paper cannot know the central value and its uncertainty come from
different learners, which is a property of the measurement, not a detail of its bookkeeping.

Secondary, and much smaller: the paper's *"100 trees, 5 iterations"* fuses a learner hyper-parameter with
the OmniFold iteration count. `sec_method` gives LightGBM as *"100 trees, 8 leaves, learning rate 0.1"*
and `n=5` as the **unfold** iteration count. Compressed prose rather than a wrong number, but it makes
`5` look like a property of the learner.

---

## 7. MED-HIGH, **PAPER BUILD** — a struck number prints unstruck, as a literal, under a caveat that does not cover it

`paper_body.tex:145-147`:

> It yields an absolutely-normalized central value whose ordinary closure is internally consistent to
> $\sim\SI{\petClosure}{\percent}$ and which **agrees with the production result at the \SI{9}{\percent}
> level**

`sec_pet.tex:40-44`, the note build on the same comparison:

> \item \textbf{Cross-check vs GBDT} (**`niter`$=$2 legacy --- not a current number**; see the scope note
> below): on data, the PET absolute total was $\dead{\SI{2.796e-38}{cm^2/nucleon}}$ versus the GBDT
> $\dead{\SI{3.066e-38}{}}$, ratio $\dead{\petRatio}$, with per-axis median differences of
> $\dead{\SIrange{6.5}{9.9}{\percent}}$

followed at `:47-62` by a scope paragraph withdrawing all of it on **three mechanical grounds**: `niter`=2
against the pinned `niter`=3; the 2026-08-01 full-event schema change (*"a pre-08-01 PET total is a
different estimator, not a differently-trained one"*); and J21, *"unit measured weights and **no**
background subtraction."*

**In the note the whole comparison is struck and explained. In the paper the same comparison appears as
`9`, an inline literal, framed positively as agreement, with no strike and no scope note.**
`grep -niE 'niter|legacy|struck|withdraw|two-iteration|J21|background subtraction|2026-08-01'` over
`paper_body.tex` returns **nothing** (control: the file greps live, 92 hits for `\\[a-zA-Z]+`).

### The paper's caveat is real, and it does not reach this

I nearly reported "the paper has no caveat", and that would have been wrong. `paper_body.tex:151-157`
says:

> Those uncertainty products remain candidates until the selection-complete lateral replacement lands.
> **The historical recoil-PET covariance is also quarantined** … **Only central-value PET comparisons are
> used here**; the full-event estimator receives a fresh uncertainty budget.

**That caveat is correctly scoped to COVARIANCES, and the 9 % gap is a central-value comparison — so the
paper's own sentence licenses exactly the number that the note withdrew.** But the note did not withdraw
it on covariance grounds; it withdrew it on `niter`, estimator-definition and background-subtraction
grounds, **none of which the paper's sentence touches.** The caveat therefore reads as coverage while
leaving the actual defect uncovered, which is worse than an absent caveat because it stops the reader
looking further.

### The same figure, two captions, one struck and one not

Both builds include `pet_vs_gbdt_absolute`.

| build | caption, on the same figure |
|---|---|
| note, `sec_pet.tex:91-93` | *"The PET/GBDT total ratio is $\dead{\petRatio}$ --- **struck: `niter`$=$2 legacy, see the scope note in the text**"* |
| paper, `paper_body.tex:163-166` | *"…**the total offset also reflects the different training and feature contracts**."* |

**The note withdraws the difference; the paper explains it.** An explanation asserts the quantity is real
and attributes it; a strike asserts it should not be used. **These are opposite dispositions of one
number, in two documents built from one directory, and only the internal one is withdrawn.**

### The note's own bookkeeping records this as done, and it is not

`values.tex:65-71`, the PET block header, says of `\petRatio` and `\petGbdtGap`: **"Both are struck
wherever printed."** That is true of the two **macros**. It is false of the **value**: `9` reaches the
paper as a hardcoded literal, so the macro-level strike cannot touch it. **This is the retraction
index's own first rule — *"a retraction propagates by STRING MATCH"* — firing inside the note's own
bookkeeping, against a comment that asserts the coverage is complete.**

---

## 8. CANNOT TELL — `\petClosure` prints twice in the paper build and its legacy status is ambiguous

`values.tex:65-74`, verbatim structure:

```
% --- PET point-cloud track ---
% NOT QUOTABLE as current values -- niter=2 legacy.  [...six lines of grounds...]
\newcommand{\petRatio}{0.912}    % PET/GBDT absolute total ratio; niter=2 LEGACY, struck at use
\newcommand{\petClosure}{1}      % closure unbiased to ~this (%)
\newcommand{\petGbdtGap}{9}      % PET-vs-GBDT data-side gap (%); niter=2 LEGACY, struck at use
```

**The block header declares the block not quotable. Two of the three macros repeat it per line. The
middle one does not.** `\petClosure` prints at `paper_body.tex:145` and `:164` — the external build — and
at `sec_pet.tex:93`, where it sits *inside a caption whose other number is struck* and is itself not
struck.

**Two readings and I cannot choose between them from documents.** Either `\petClosure` is outside the
legacy class and its bare per-line comment is correct — in which case the block header over-reaches and
should be narrowed — or it is inside the class and has been printed unstruck three times, twice
externally. **The `niter`=2 grounds would apply to it if the closure came from the same two-iteration
run, and nothing in `values.tex`, `sec_pet.tex` or the retraction index says whether it did.**

**This is an owner's call, and it is worth making because of where the value prints.** The remedy differs
completely: narrowing a comment costs nothing; striking a number in the external build is finding 7's
class. **I am not guessing which.**

---

## 9. LOW — two iteration counts, both stated absolutely, never reconciled

- `sec_method.tex:145-147`: *"The production iteration count is $n=5$; doubling to $10$ moves the total
  cross section by \SI{0.026}{\percent}"*
- `sec_pet.tex:55-56`: *"The campaign's pinned policy is `niter`$=$3 (CLM-010, CLM-012, \textsc{frozen}),
  and full-event PET moved to it."*

**These are almost certainly different pipelines** — `n=5` is the 2D/scalar GBDT production, `niter`=3 is
the PET/full-event campaign, and `CLM-010`'s evidence is a PET B1 closure. **I am NOT reporting a
contradiction.** But *"the production iteration count"* and *"the campaign's pinned policy"* are both
written as though unique, in one document, ten pages apart, and neither says which measurement it
governs. **Same disposition as the 77/23-vs-88 item in finding 1: a comprehension hazard, not an
arithmetic one.** One clause of scope on each fixes it.

---

## 6 (UPGRADED IN TRANCHE 3) — the paper's headline $\chi^{2}$ belongs to the estimator it does not name

Tranche 1 reported finding 6 as a wrong label. **`sec_results.tex:151-155` makes it numerical:**

> A $\sim1$-unit methodological band comes from the GBDT estimator (**exact-GBT $\chiPaper$ vs HistGBT
> $2.70\pm0.04$ vs LightGBM $2.65$**; iteration count is negligible, $5\to10$ iters move it by $+0.01$).

and `sec_results.tex:170-171`, a source comment:

> % NOTE: the estimator-band value "exact-GBT 3.66" below is the same number as
> % the paper-covariance chi2 (`\chiPaper`); they coincide by construction.

**So `\chiPaper` = `3.66` IS the `exact`-GBT number, and the note records that LightGBM gives `2.65`.**
`paper_body.tex:65-68` prints `\chiPaper` as *"the residual indicative paper-covariance distance … per
bin"* and then adds *"it carries a $\sim1$-unit method-dependence band from the choice of GBDT
estimator"* — **eighteen lines after telling the reader the estimator is LightGBM.**

**A reader of the external document is told the analysis uses LightGBM and shown $3.66$; the note says
LightGBM gives $2.65$ and that $3.66$ is `exact`-GBT.** The gap is the whole width of the
method-dependence band the same paragraph mentions. **This is no longer a naming slip that a
one-word edit fixes cleanly — the fix must name `exact` and keep $3.66$, and the reader needs both
facts, which is precisely the pairing `sec_method` calls *"a stated property of the measurement."***

---

## 11. MED — three reviewer-comment macros print in the note PDF, and are undefined in both external builds

`main_note.tex:17-19` — **and nowhere else**, in particular **not in `preamble.tex`**:

```latex
\newcommand{\jrb}[1]{\textcolor{violet}{\textbf{[JRB: #1]}}}
\newcommand{\gk}[1]{\textcolor{orange}{\textbf{[GK: #1]}}}
\newcommand{\bpn}[1]{\textcolor{blue}{\textbf{[BPN: #1]}}}
```

**These render.** Thirteen uses across five section files, all note-build only:

```
\gk  6   sec_experiment:46,104   app_statmethods:14   sec_systematics:122,129   sec_results:5
\jrb 4   sec_systematics:122,129   sec_validation:37,75
\bpn 3   sec_pet:4   sec_validation:36,73
```

Two things about them are worth separating. **That an internal review draft carries visible reviewer
marks may well be deliberate, and I am not calling that a defect.** What is harder to defend:

- **`sec_pet.tex:4` is `\bpn{left off here}`** — a drafting bookmark, printing as bold blue
  *"[BPN: left off here]"* at the head of the PET section.
- **`sec_systematics.tex:122` and `:129` each carry a comment AND its answer, both left in:**
  `…$\sqrt{\mathrm{Tr}\,C}$ \gk{ $\sqrt{\mathrm{Tr}C}$} \jrb{Fixed!}` and `covariance matrix \gk{matrix}
  \jrb{Fixed!}`. **The correction was made and neither the request nor the acknowledgement was
  removed**, so the PDF reads *"…covariance matrix [GK: matrix] [JRB: Fixed!] has …"*.
- **`sec_systematics.tex:129` is also the `\gbdtAiEstTrace` line**, i.e. `OI-130`'s named instance —
  the macro whose backing artifact `uq_cov_ai1est_5d.root` `docs/OPEN_ITEMS.md:155` records as
  *"untracked and gitignored on purgeable scratch."* **Not re-filed here; cited so the two are visible
  as the same line.**

### The latent build-breaker, which is the actionable half

`main_paper.tex` and `main_primer.tex` input `preamble`, `values` and their body **and define none of
these three macros** (`grep` for `gk}`/`jrb}` in both wrappers and in `preamble.tex` returns nothing).
**So a single `\gk{}` reaching `paper_body.tex` fails the paper build with `Undefined control
sequence`.**

**And the operation that would do it is the normal one.** `paper_body.tex` is a *distillation* fed by
the section files; moving or adapting a commented paragraph into it is the routine act. **The macros
that are safe to use are defined in the shared preamble; the ones that break an external build are
defined in the note wrapper — and nothing marks the difference at the point of use.** Moving the three
definitions into `preamble.tex` as no-ops for the outward builds would remove the trap without changing
any rendering.

---

## 12. MED-HIGH — the note's own containment check passes, and names the gap that finding 7 lives in

`docs/analysis-note/check_dead_containment.py` is a serious instrument and this is not a complaint about
its quality. Its docstring: *"Assert that struck (retracted) values reach the NOTE build and no other."*
It checks both directions, refuses to be vacuous, derives struck values from source rather than
hardcoding them, strips TeX comments before matching, and carries a **power test** that requires every
positive case to fail against the pre-2026-08-12 pattern. Run this turn:

```
python3 check_dead_containment.py --self-test        ->  SELF-TEST :: PASS   (9 of 11 discriminate)
python3 check_dead_containment.py --source-only      ->  RESULT :: PASS
  ok   note: 26 \dead{} uses across sec_pet.tex, app_statmethods.tex
  ok   paper: clean, 0 \dead{} in a 4-file closure
  ok   primer: clean, 0 \dead{} in a 4-file closure
  ok   PDF stage does NOT cover 2 \dead{} bod(ies) -- no decimal literal to search for, so only
       the source check guards these: \approx\!70\% ; \sim\SI{\petGbdtGap}{\percent}
```

**Read the fourth line. The check names `\petGbdtGap` — by name — as one of two bodies its PDF stage
cannot cover. `\petGbdtGap` is `9`. `9` is exactly the literal finding 7 found printing unstruck at
`paper_body.tex:146`.**

**The exclusion is deliberate and correct.** `NUM_RE = r"\d+\.\d+"`, with the reason in the source: *"a
bare integer collides with page numbers, bin counts and years in a rendered PDF, so searching for it
would produce false failures."* **That judgement is right.** The consequence is that the one struck
quantity whose value is a bare integer is the one the PDF stage cannot see — **and it is occupied.** The
source comment distinguishes *occupied* from *latent* elsewhere in the file, twice, deliberately; **this
gap is not marked either way, and it is occupied.**

### The second blind spot, and it is structural rather than a trade-off

**The check's universe is the set of `\dead{}` bodies.** It answers *"do marked values escape?"* It
cannot answer *"is every dead value marked?"*, because **an unmarked value is not in its input at all.**
**Finding 2 — four values dead on two grounds, never wrapped in `\dead{}` — is invisible to it by
construction**, and the check reports `PASS` with `sec_systematics.tex` never appearing in its output,
because that file has no `\dead{}` uses to enumerate.

**This is a fixture-derived-from-the-rule shape: the instrument can only see what an author already
flagged, so it is exactly blind to the failure of flagging.** Closing it needs a different input — the
retraction index's dead-value list checked *into* the note, rather than the note's marks checked
outward. `INDEX-retracted-and-superseded-values.md` already maintains that list, and already names
`values.tex:57-60` and the four prose sites.

**Neither gap is a reason to weaken the check.** Both are reasons its `PASS` should not be read as
*"the note's retractions are contained"* — it means *"the marks that exist do not escape, except for two
bodies it told you about."*

---

## 13. CANNOT TELL — an unstruck PET shape comparison that may be the struck run

`sec_validation.tex:96-98` and its figure caption at `:146-159`, **neither struck**:

> the PET unfold reproduces the scalar shape to a median \SIrange{2.3}{3.9}{\percent} per bin …
> Shape-only comparison (**PET on a 2M-event subsample**), not an independent physics result.

`sec_pet.tex:54-55`, the scope note for the **struck** comparison:

> **The PET run used a 2M-event, *two*-iteration training.**

**Different quantities, and I checked that first: `sec_validation` compares *area-normalized shapes*
(figure `pet_vs_gbdt`), `sec_pet` compares *absolute totals* (figure `pet_vs_gbdt_absolute`) — two
distinct files, two distinct claims.** So this is not the struck number reappearing.

**What I cannot establish is whether it is the same RUN.** The shared *"2M-event"* descriptor is
suggestive and is not proof. If it is the same run, two of `sec_pet`'s three withdrawal grounds reach it
— `niter`=2 against the pinned 3, and the 2026-08-01 estimator change, which `sec_pet` says makes a
pre-08-01 PET total *"a different estimator, not a differently-trained one"* — while the third (J21, no
background subtraction) plausibly does not bite an area-normalized shape. `sec_pet`'s scope paragraph
is explicitly scoped to *"every struck figure in item 3 above"*, so it does not cover `sec_validation`
either way. **Owner's call; the cheap resolution is one line in `sec_validation`'s caption stating the
iteration count, which the caption already almost does by naming the sample size.**

---

## 14. LOW-MED, **PAPER + PRIMER** — the external builds omit the analysis's one binned step

`sec_method.tex:34-52` and `:55-56`, the note build:

> **Background subtraction (the one binned step).** … each data event in reco bin $b$ is weighted by
> $w_{\mathrm{pur}}(b)$ … an ${\sim}\SI{3}{\percent}$ effect overall …
> **This correction is, deliberately, the one place the analysis binning enters before the final
> histogramming.**

`grep -niE 'negative.weight|negweight|purity|background'` over **`paper_body.tex` returns nothing, and
over `primer_body.tex` returns nothing.** Control: both files grep live (92 and 60+ hits for
`\\[a-zA-Z]+`). **Neither external build mentions background subtraction at all.**

**No sentence in the paper is falsified by this, and I want that stated plainly rather than buried.**
The paper's binning claims are careful and remain true: it says iterative Bayesian unfolding *"on a
binned migration matrix"* scales poorly (`:10-12`), and that histogramming happens *"in any declared
reporting binning"* (`:51`). The purity weight is a **reco-space** correction, not a reporting binning,
so it contradicts nothing written.

**What it does is remove the measurement's only binning dependence from the document whose stated
methodological distinction is unbinnedness.** A reader of the external paper cannot learn that the
analysis has a binned step at all, or that it is a ~3 % effect, or that the note devotes an appendix and
a `CLM-009`-backed reduction proof to eliminating it. **This is an omission with an editorial and a
physics component, and it is the note owner's call, not mine** — I am reporting the asymmetry, not
prescribing that the paper must carry it.

It is, though, the same **prose-versus-boundary** mechanism as findings 6 and 7: the honest
qualification exists, in `sec_method` and `app_negweight`, and **both are note-build only.**

---

## CHECKED AND CLEARED — recorded because a near-miss is worth as much as a hit

Three things looked like findings and are not. Recorded so the next reader does not re-derive them, and
because two of them would have been false `HIGH`s in the **external** build.

1. **`\fpsAnchor` `0.57` vs the anchor determination's `0.573 %` — COINCIDENCE.** `\fpsAnchor` prints
   twice in the paper build, and
   `DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:896` carries `0.573 %`. Two
   quantities agreeing to two significant figures, one of them in the external document, is exactly the
   shape of a copied value. **It is not one.** `VALIDATION_LEDGER.md:1266-1269` sources it exactly,
   including the cell count: *"FPS MEFHC battery (2026-06-10, job 54244120) — anchor gate PASS … median
   $|\Delta|$ **0.57 % (185 cells)**"*, against the note's *"median deviation 0.57 % over all 185 reported
   cells."* The determination's `0.573 %` is *"the sqrt-trace shift between two CVs … a two-artifact
   difference"* — an uncertainty quantity, not an agreement one — **and its "anchor" is the $j=0$ member
   of a 50-member MII family, a different sense of the word entirely.** Two different quantities, two
   different senses of one noun, one shared rounding.
2. **`sec_fps.tex` is clean against the ledger** on every value I could check: `0.9994` integral,
   `1.0013` per-cell median, `0.57 %`/185 cells, `\fpsSigma` `4.502e-38`, `\fpsAbove` `46`, and the
   acceptance triple `66.4 / 22.3 / 11.3` all reproduce `VALIDATION_LEDGER.md:1266-1272` exactly. Its
   containment diagnostic even carries the *"probes the statistical closure-toy stream, not the full
   adopted band"* hedge that `values.tex:26-28` asks for. **A section can pass.**
3. **`sec_method`'s acceptance treatment agrees with `CLM-011`.** The note says the miss regressor is
   *"the native OmniFold acceptance treatment, **with no separate efficiency correction**"* (`:22-24`),
   and `paper_body.tex:45-46` repeats it. `CLM-011`, `VERIFIED-CODE`: *"The extended-FPS cross section
   must NOT be divided by a reco efficiency."* **Consistent in both builds.**
4. **THE FIGURE IMAGES ARE CLEAN — measured, and the caution about rendering did not bind.** All **52**
   figures are **vector PDFs** with extractable text, `pdftotext` is available, and **none is
   image-only**, so no rendering was required and nothing here is a guess:

   ```
   PDFs 52 | text-extracted 52 | EMPTY (image-only, NOT CHECKED) 0 | failed 0
   POSITIVE CONTROL: 1382 decimal literals seen across extracted figure text
   ```
   Searched for thirteen struck/dead literals — the two struck PET absolutes, `\petRatio`, the struck
   `6.5`/`9.9` range, all four `\gbdtFive*`, the three `QUARANTINED` `\petTotal*`/`\petFourMedian`
   values, and the struck `5.0467`. **Twelve are absent from every figure.** The single hit, `9.9` in
   `MEFHC_5iter_xsec_paper_pz_slices.pdf`, is a substring of a $\chi^{2}$ annotation reading
   `2/n = 6119.9/10` — **a digit collision, not the struck range.** *If any figure had extracted empty I
   would have reported it as unchecked rather than clean; the check distinguishes those, because an
   empty extraction and a clean one are the same bytes.*
5. **The Ascencio quarantine DID propagate to the paper build — and this sharpens finding 7 rather than
   softening it.** `values.tex:50-51` records *"Ascencio covariance metrics removed 2026-07-12:
   historical 4D covariance quarantined."* Both builds carry the caveat, and **the paper's is the more
   explicit of the two**: `sec_3d.tex:387-391` says *"Only the central-value comparison is used; the
   uncertainty-derived annotations in the panel do not use the corrected 4D covariance"*, while
   `paper_body.tex:111-114` says they *"do not use a corrected 4D covariance **and are not
   interpreted**."*

   **So the paper build is not uniformly careless, which is what makes finding 7 a specific omission
   rather than a general property — and the contrast identifies the mechanism.** The Ascencio caveat
   lives in **prose inside a figure caption**, and survived the rewrite because rewriting a caption
   carries its sentences along. The PET withdrawal lives in a **macro** (`\dead{\petRatio}`) and in a
   **scope paragraph in a section file with no paper counterpart**, and neither survives.
   **Generalisable: a caveat carried in prose survives a distillation; a caveat carried in markup or in
   a neighbouring section does not.** That is the same standard as *does the document already have the
   mechanism* — applied to whether the mechanism can cross a document boundary.
7. **`app_negweight.tex` NAMES ITS OWN THIRD-BACKEND LIMITATION, unprompted, and it is the best-hedged
   passage I have read in the note.** I went in expecting a finding: `sec_method.tex:64-68` claims the
   unbinned route *"reproduces the binned correction to \SI{\nwPctTot}{\percent} … and its systematic
   and statistical covariances to within \SI{2}{\percent}"*, and `values.tex:107-111` records that the
   `nw*` 2D totals are the **`hist`** estimator while the central value is `exact` and the covariance
   `lgbm` — a third backend, unflagged in `sec_method`. **`app_negweight.tex:57-62` flags it itself:**

   > Note that `\texttt{hist}` is neither the backend of the production central value (`\texttt{exact}`)
   > nor of its covariance ensemble (`\texttt{lgbm}`); see \S\ref{sec:method}. **This validation
   > therefore establishes the equivalence on a third backend, and its transfer to the production
   > configuration is an assumption rather than a demonstration.**

   **That is exactly the caveat I was going to file, written better than I would have written it.** No
   finding. *(The reach question does apply and is answered: neither external build mentions the
   subtraction at all — §14.)*
8. **`sec_eavailw.tex` is clean.** The `(\Eavail,W)` comparison is explicitly *"made at central-value
   level because no corrected covariance has been adopted for the $(\Eavail,W)$ projection"*, matching
   `values.tex:52-54`'s *"(Eavail,W) significances removed 2026-07-12: historical covariance
   quarantined. Reintroduce macros only from a committed corrected-covariance ledger entry."*
   **The macros stay removed and the prose does not reintroduce a significance.** `\eavailMargin`
   `0.11` prints beside its own operand (*"5D/4D total $=1.0011$"*), so unlike the `\ratioTot`/`1.1`
   pair below it is self-checking.
6. **`sec_results`, `sec_fps`, `sec_execsummary` and `sec_3d` pass on everything I could check**, and
   several are notably careful: `sec_results` hedges its covariance distances four separate times
   (*"indicative"*, *"descriptive scale, not an independent-result pull"*, *"neither is a calibrated
   goodness-of-fit"*, *"none of these coordinates is a calibrated independent-result goodness-of-fit
   statistic"*), and `sec_validation` declines to quote a 2D coverage number and says why. **Sections
   can pass, and four of them do.**

   One coupling worth a glance rather than a finding: `sec_results.tex:59` writes *"reproduces the
   published one to \SI{1.1}{\percent} (ratio $\ratioTot$)"*, where `1.1` is `\ratioTot` `1.011` minus
   one, hardcoded. **A derived quantity beside its operand does not string-match the operand** — the
   retraction index's own first write-time rule — so a future change to `\ratioTot` silently leaves
   `1.1` behind. Same shape at `paper_body.tex:60`.

---

## What these tranches did NOT cover

Stated because an audit silent about its own reach reads as complete.

1. **Only `values.tex`'s 70 macros were traced.** The note's own header says numbers appearing exactly
   once *"are NOT macroized here … they stay inline at their single site"* — **so the inline numbers are
   the larger population and none of them was swept.** `app_statmethods.tex` alone carries dozens
   (`67.1%`, `3.5969`, `0.868`, `76.7`, `0.356`…). This is the biggest gap in tranche 1 and the obvious
   tranche 2.
2. **READ in full across tranches 2–3:** `sec_method`, `sec_fps`, `sec_results`, `sec_validation`,
   `sec_execsummary`, `paper_body`, `primer_body`, `check_dead_containment.py`; `sec_3d`, `sec_pet`,
   `sec_systematics`, `app_statmethods` in the relevant parts. **Still only grepped, not read:
   `sec_experiment.tex`, `sec_intro.tex`, `sec_summary.tex`, `app_landscape.tex`, `app_codebase.tex`**
   — and `sec_3d`'s and `app_statmethods`' unread remainders. **Tranche 4 added `app_negweight` and
   `sec_eavailw`**, both of which cleared.
   `ISSUE-57`'s class is found by *reading*: the defect is a correct-sounding sentence about the wrong
   object and has no distinctive string. **The grep results for those files are evidence about the
   grep.** With `app_negweight` now read, the largest unread block is `sec_experiment.tex` (170 lines),
   which carries the selection definition two `\gk{}` review questions are about.
3. ~~**The three builds may differ** … I did not check whether a defective passage reaches all three.~~
   **DONE in tranche 2 — §0, and it changed the ranking.** Note that §0 measures reach by *macro name and
   figure*; a claim compressed into different words in `paper_body`, as findings 6 and 7 both are, is
   invisible to that method and was found by reading. **So §0's per-build macro lists are complete and
   its implicit "therefore the paper is clean of the rest" is NOT** — the paper must be read for
   *restatements*, not only searched for shared tokens.
4. **`KNOWN_ISSUES.md` was in the corpus for the numeric sweep but was not read against the note's
   methodological claims.**
5. **No cluster access.** `ssh` exits 255 under `maintenance_20260819`, so nothing was re-derived from a
   product; every authority above is a committed file.
6. **Three questions are open and are the owner's, not mine.** The 2D-vs-full-event scoping in §1c
   (which construction §`sec:bootstrap` describes), `\petClosure`'s legacy status in §8, and whether
   `sec_validation`'s PET shape comparison is the struck run in §13. **All three are stated with what
   turns on each answer rather than resolved.**
7. ~~**Figures were not audited** … no text search reaches it.~~ **DONE in tranche 3 — cleared item 4,
   and the caution about rendering did not bind: all 52 figures are vector PDFs with extractable text,
   none image-only, and twelve of thirteen struck literals are absent from all of them.** The residual
   limit is real and narrower: **the search covers TEXT in the vector stream.** A struck value baked
   into a rasterised inset, or one visible only as an unlabelled bar height, is still unreachable — but
   nothing in this figure set is rasterised, so that limit is currently unoccupied.
8. **The check I ran is the note's own, in `--source-only` mode**, because no PDFs are built in this
   worktree. Its strict mode requires the built PDFs and would have run the render-side comparison too.
   **So §12's `PASS` is the source stage only**, which is exactly the distinction the script's own
   `--source-only` help text insists on, and I am repeating it rather than quoting the bare `PASS`.

---

## V. VERIFICATION BASELINE — recorded BEFORE lane B's edits exist

**Role change, 2026-08-19.** Joseph authorised paper corrections and a push
(`AUTHORIZATION-20260819-analysis-note-paper-corrections-and-push.md`, `b8f74fbe`). **Lane B edits;
this lane verifies and does not edit.** The party that verifies is not the party that built.

**A verification baseline is worthless if it is written after the diff**, so this section is committed
at `origin/main` `b8f74fbe`, with **no analysis-note edit yet present** — `git log -- docs/analysis-note/`
tops out at `7d884da3`, which predates the authorization.

### Pre-edit digests, whole subtree

```
948986d8 app_codebase.tex   0bffc6c6 app_landscape.tex  267f88c3 app_negweight.tex
202539de app_statmethods.tex 50a11039 build_all.sh      edf7ccfe check_dead_containment.py
ef4c5348 figures/           fe73058d main_note.tex      940d4a5d main_paper.tex
ef1712b0 main_primer.tex    2721bf5d make_figures.sh    d4a73c8e paper_body.tex
ec107e9b preamble.tex       e792718b primer_body.tex    d254628e sec_3d.tex
78f4b23c sec_eavailw.tex    eec162b8 sec_execsummary.tex 99046172 sec_experiment.tex
14d94dfa sec_fps.tex        e3930330 sec_intro.tex      34482869 sec_method.tex
e49048ed sec_pet.tex        43f52e4a sec_results.tex    f361449a sec_summary.tex
f24ae59e sec_systematics.tex 6816d716 sec_validation.tex 927c4c94 technote.bib
dcaa8c90 values.tex
```

**Any blob that changes and is not `paper_body.tex` is a question**, not automatically a defect — the
receipt's clause 5 permits *"captions, cross-references, or shared prose required for those corrections
to render coherently"*, and clause 1 permits shared source. But it must be **asked**, which is what a
recorded digest set makes possible and a post-hoc read does not.

### The two target sites, verbatim, pre-edit

```
paper_body.tex:47-48
  We use gradient-boosted decision trees (LightGBM, 100 trees, 5 iterations) as the
  learners; the higher-dimensional unfolds simply append feature columns

paper_body.tex:145-147
  closure is internally consistent to $\sim\SI{\petClosure}{\percent}$ and which
  agrees with the production result at the \SI{9}{\percent} level
  (Fig.~\ref{fig:ppet}).

paper_body.tex:163-166  (caption, fig:ppet)
  closure validates the extraction machinery to $\sim\SI{\petClosure}{\percent}$
  but does not test omitted muon dependence; the total offset also reflects the
  different training and feature contracts.
```

### What I will check, written before I can see the answer

1. **Does the estimator edit fix finding 6 *as upgraded*?** Naming `exact` is necessary and **not
   sufficient**: the paper prints `\chiPaper` = `3.66`, which is the `exact`-GBT value, and the note
   records LightGBM at `2.65`. **An edit that names `exact` but drops or garbles the
   not-estimator-matched clause leaves the reader without the pairing `sec_method` calls *"a stated
   property of the measurement."*** All three facts, or the finding is not discharged.
2. **Does the PET edit fix finding 7 on the RIGHT GROUNDS?** The note withdraws that comparison on
   `niter`=2, the 2026-08-01 estimator change, and J21 — **not** on covariance grounds. The paper's
   existing `:151-157` quarantine sentence is covariance-scoped and already licenses the number. **An
   edit that leans on that sentence rather than on the legacy grounds re-creates the defect in new
   words.**
3. **Is `\petClosure` untouched?** Receipt clause 3 and the boundaries forbid answering a `CANNOT-TELL`
   before the PET/spec owner adjudicates. **`\petClosure` prints at `:145` and `:164`, inside both
   target regions.** An edit that quietly disposes of it while fixing its neighbours would exceed the
   authorization — and it is the easiest such overreach to commit by accident, because the two sites
   are one sentence apart.
4. **Did anything change that no finding asked for?** Answered by diffing against the digests above.
5. **Any NEW inconsistency with the record**, including with findings 1–14 of this document.
6. **Do the five out-of-scope items remain untouched?** `\petClosure` (3 above), the measured-leg
   self-contradiction (finding 1, note-only, lane C), the unmarked `\gbdtFive*` (finding 2, note-only),
   the ledger-traceability gap (finding 3 — **and the remedy is a LEDGER ENTRY; editing the prose would
   hide the gap rather than close it**), and `\bpn`/`\gk`/`\jrb` (finding 11). **Their absence from the
   diff is compliance, not oversight, and I will not report it as a miss.**

### One thing I am NOT verifying, and why it matters that someone did

The mediator found `build_all.sh` exiting 0 with `latexmk` reporting *"Nothing to do"* for all three
targets and **nothing recompiling** — so `check_dead_containment.py`'s PDF stage had been validating
PDFs dated 2026-08-11 and 2026-08-15, for over a week, while reporting `PASS`. Fixed with `latexmk -g`
per target; all three now carry current mtimes and the containment check passes on **fresh** PDFs.

**This is the same class as §12 and it is worse, because §12's gap was disclosed in the tool's own
output and this one was not: a green build proved nothing about current source.** It also means
**§12's `PASS`, which I ran `--source-only`, was the only honest reading available in this worktree**
— the strict mode I could not run was, at that moment, reading week-old PDFs. **I did not find this and
I am not claiming it.** Recorded because the gate this lane will verify against is now real, and was
not before, and a reader of §12 needs to know which regime each `PASS` came from.

---

## VR. VERIFICATION RESULT — lane B's `8fd842af` against §V. **PASS**, with one residual question

**Verified by this lane, which did not edit.** Checked against the §V digests recorded before the edit
existed. `8fd842af`, author `Claude (lane B)`, **one file, 24 insertions / 10 deletions.**

| §V check | result |
|---|---|
| 1. estimator edit fixes finding 6 **as upgraded** — all three facts | **PASS** |
| 2. PET edit uses the **legacy** grounds, not covariance | **PASS**, and it added the direction |
| 3. `\petClosure` untouched | **PASS** — 2 occurrences, byte-identical construct, both sites |
| 4. nothing changed that no finding asked for | **PASS** — 1 of 28 blobs differs |
| 5. no new inconsistency with the record or findings 1–14 | **PASS**, one observation below |
| 6. the five out-of-scope items untouched | **PASS** — by digest, not by inspection |

### Check 4, first, because it is the one only a pre-recorded baseline can answer

`git ls-tree` over `docs/analysis-note/` at `8fd842af`, compared to §V line by line: **exactly one blob
differs, `paper_body.tex` `d4a73c8e` → `f91f74d3`. The other 27 are byte-identical**, including
`values.tex`, `sec_pet.tex`, `sec_method.tex`, `preamble.tex`, all three drivers, `build_all.sh`,
`check_dead_containment.py` and `figures/`. **Nothing was changed that no finding asked for, and this
is a measurement rather than a reading of the diff.**

### Checks 1 and 2 — the substance, and B's two new claims are the note's own words

Both edits add material, so both add claims that need sources. **Neither is B's derivation:**

| B's new text | source, verbatim |
|---|---|
| *"100 trees, depth-3 capacity, 5 iterations … LightGBM at matched capacity ($\texttt{num\_leaves}=8=2^{3}$)"* | `sec_method.tex:156-160`: *"100 trees, learning rate $0.1$, and depth-3 capacity are the sklearn `GradientBoosting` defaults, and the production LightGBM backend is configured to the matched capacity ($\texttt{num\_leaves}=8=2^{3}$)"* |
| *"which biases PET high, so the underlying gap is \emph{larger} than the withdrawn figure"* | `sec_pet.tex:62-66`: *"At this analysis's ${\sim}\SI{3}{\percent}$ background scale, leaving background in biases PET high, so the underlying gap is \emph{larger} than the struck value, by an amount that is a first-order estimate and deliberately not quoted."* |

The `$\texttt{num\_leaves}=8=2^{3}$` token is **byte-identical** to `sec_method.tex`'s, which compiles.

**Two things B got right that I would flag if they were absent.** It carried the direction across
**without** the magnitude, matching the note's *"deliberately not quoted"*; and it dropped the
*"~3 % background scale"* qualifier, which is correct here because the direction does not depend on the
scale, only the magnitude does — and the paper never states that scale (**finding 14**), so importing it
would have introduced an unexplained number.

**Finding 6 is discharged on all three facts:** `exact` named for the central value with its sklearn
identity, LightGBM named for the uncertainty ensemble, `\chiPaper` **kept**, the clause restored as
*"so the central value and its covariance are \emph{not} estimator-matched"*, and — beyond what I asked
— the band's operands made explicit as *"(exact-GBT $\chiPaper$ versus LightGBM $2.65$)"*, so a reader
can now check the "$\sim$1 unit" instead of taking it. **Finding 7 is discharged on the right grounds:**
all three are the legacy ones, none is covariance, and `:156-157` was **narrowed** to *"Neither a PET
central-value comparison nor a recoil-PET covariance is used here"* rather than leaned on — necessary,
because after the removal the old sentence would have been false.

### Mechanical checks, run independently rather than accepted

```
\petClosure                  pre 2  post 2      \SI{\petClosure}{\percent}  pre 2  post 2
\SI{9}{\percent}             pre 1  post 0      \petGbdtGap                 pre 0  post 0
\dead{} uses                 pre 0  post 0      \gk{} \jrb{} \bpn{}         pre 0  post 0
braces                       pre 107/107 balanced   post 111/111 balanced
inline $                     pre 90 even            post 96 even
macros new in post: NONE     macros removed: NONE
```

**B's own static figures reproduce exactly (111/111 and 96).** A `\dead{}` count of 0 is not a
formality — see below.

### The judgement call: **B is right, and it was FORCED, not merely persuasive**

The mediator asked whether the strike would have been better than removal. **No — and the reason is
stronger than B's own argument.** B argued that a greyed strikethrough advertises internal bookkeeping
to a reader with no note to consult. True, but the repository has already decided this in writing, in
the very instrument that enforces containment. `check_dead_containment.py:6-7`:

> `\dead{}` … renders a retracted value struck-through and grey. **Strike-not-erase is right for an
> internal audit trail and wrong for anything outward-facing.**

and its fail condition, `:331-335`, makes it executable: any non-note driver whose closure contains
even one `\dead{}` use is a **failure** — *"struck retracted values would render in an outward-facing
PDF."* **A strike in `paper_body.tex` would have turned the build gate red.** Removal was not the better
of two permitted options; **it was the only one consistent with the invariant the note enforces.**

> **AND THAT CORRECTS MY OWN FRAMING, which I am fixing in terms rather than quietly.** In tranches 2
> and 3 I wrote that the paper build *"inputs the shared preamble, so `\dead{}` is available to it and
> used zero times"*, and offered that as an instance of the equipped-to-mark standard — as though the
> zero were a missed opportunity. **For the paper build it is the enforced invariant.** The
> equipped-to-mark standard still holds exactly where I first applied it — **finding 2,
> `sec_systematics.tex`, note build, where striking is right and is what the neighbouring files do** —
> but it does **not** transfer to the outward builds, and I extended it there without checking. **The
> mechanism a document is equipped with is not automatically the mechanism it is permitted to use, and
> `check_dead_containment.py` had written that distinction down before I generalised past it.**

### Check 5 — one observation and one residual question, neither blocking

**Observation, and it sharpens finding 14 rather than answering it.** The paper now contains the phrase
*"unit measured weights and no background subtraction"* — its **first and only** mention of background
subtraction, correctly, as a property of the withdrawn PET run. **So the external build now presupposes
a background-subtraction step that it still never describes.** B's sentence is right and the gap is
pre-existing; finding 14 is unchanged in substance and slightly sharper in form.

**RESIDUAL QUESTION — the only thing in this pass I would put to the owner.** The text now says
*"Neither a PET central-value comparison nor a recoil-PET covariance is **used** here"*, while the paper
**still displays `pet_vs_gbdt_absolute`**, which *is* a PET-vs-GBDT central-value comparison, plotted.
The caption carries the weight: *"The total offset shown is a two-iteration legacy result, withdrawn as
a current comparison (see text) and not quoted here as a level of agreement."*

**I think this holds — *used* is not *shown*, and the caption is explicit — and B anticipated it
(*"necessary because the figure still shows the legacy data"*).** But it is the one place a careful
external reader could press: a figure given a full-width panel is arguably in use. **Two cheap
resolutions, both the owner's call and neither required by the receipt:** say *"shown for completeness,
not used"* in the text, or drop the figure from the paper build. **This does not block the push.** I
raise it because "the text withdraws it and the figure still shows it" is the same *disposition
mismatch on one artifact* that produced finding 7 — now much smaller, and moved from a number to a
plot.

**Nit, no render effect:** the new `:158` source line is over-long
(*"…re-extracted under the pinned configuration. Because the muon is used only for selection and"*).
Cosmetic only.

### What I did NOT verify

**No LaTeX was run by this lane.** B states its own verification is static-only and that the compile is
the mediator's; **that is the correct split and I am not reporting its absence as a gap.** My checks are
static too — a balanced brace count is not a successful compile. **The push should wait on the forced
`latexmk -g` and a containment run on fresh PDFs**, which the mediator has in flight, and B's point is
worth repeating at the gate: `paper_body.tex` is `\input` by `main_paper.tex` alone, so **exactly one
product legitimately rebuilds, and two skipping must not read as "all three passed."**

**Verdict: the edit does what the findings asked, on the grounds they asked, and nothing else.**

---

## Routing

> **CORRECTION TO TRANCHE 1, kept visible rather than merged away.** Tranche 1's routing section opened
> *"Findings 1 and 2 are the ones that reach outside the collaboration."* **That was wrong, and §0
> measures it: both are note-build only.** I wrote it before checking the build map, on the assumption
> that a defect in the biggest document is the most exposed defect. **The mediator was right that this
> question reorders rather than annotates.**

**Order by exposure, then by cost.**

**Tier 1 — reaches the external paper build.** Findings **6**, **7**, **8**, and the paper/primer half of
**3**.

- **Finding 6 is the most consequential item here and tranche 3 made it worse, not smaller.** It is not
  a naming slip: the paper prints $\chi^{2}=3.66$, which the note records as the `exact`-GBT value,
  while naming LightGBM as the estimator — and the note records LightGBM as `2.65`. **The headline
  tension number in the external document does not belong to the estimator that document names.** The
  edit still needs nothing re-derived, re-run or adopted — name `exact`, keep `3.66`, restore the
  not-estimator-matched clause — but *"one word"* understated it and I am correcting that here.
- **Finding 7 needs the note's remedy applied to a document that does not have it.** `\dead{}` is
  defined in `preamble.tex`, which the paper build **does** input — so the strike macro is already
  available in the paper and is used there zero times. The `9` is a literal, so a macro sweep cannot
  reach it; it has to be struck or dropped by hand. **Sequencing note: finding 7's caption problem and
  finding 6 are in the same figure's neighbourhood and should be fixed in one pass.**
- **Finding 8 is a question, not an edit.** Ask the PET owner whether `\petClosure` came from the
  `niter`=2 run. **One answer disposes of three print sites, two of them external.**
- **Finding 3's external half** — `\uqMedian`, `\uqPaper`, `\binsTen` print in the paper and primer with
  no ledger row. Cheapest fix is a ledger entry citing `2D_OMNIFOLD_STUDY_STATUS.md:101-107`, not a
  change to the note.

**Tier 2 — collaboration note only.** Findings **1**, **2**, **4**, **9**, and **5** as INFO.

- **Finding 2 remains the cheapest real risk reduction inside the note, and the reason generalises.**
  The note already contains its own remedy: `\dead{}` is defined once and used 26 times, correctly, on
  a *different* dead family, and `sec_systematics.tex` — where the surviving dead family prints — uses it
  zero times. **A defect the document is already equipped to mark is categorically more actionable than
  one needing new machinery, because it needs no new number, no adoption and no authorization.**
  `PROCEDURE-gbdtFive-macro-update.md` is explicit that replacement is neither authorized nor a drop-in;
  **striking sidesteps all of that.** *(Generalised at the mediator's request; it is also the test that
  found finding 7, where the paper build has `\dead{}` available via the shared preamble and never uses
  it.)*
- **Finding 1 needs a decision, not an edit**, and it is the largest open question here. Whether
  §`sec:bootstrap`'s two-stream description is correct for the 2D pipeline while the full-event one is
  three-stream is a fact about the code. **Owner: the lane that owns
  `SPEC-20260814-gate5-cstat-construction-v1.md`.** What turns on it: if the pipelines genuinely differ,
  the remedy is a scope clause at three sites; if they do not, one of the two passages is simply wrong
  and an argument in the note (`:861-864` rebutting a missing-MC-term objection) rests on it.

**Tier 2 additions from tranche 3.**

- **Finding 12 is the one to act on structurally**, and it costs nothing to state: `check_dead_containment.py`'s
  `PASS` means *"the marks that exist do not escape, except two bodies it named"* — not *"the note's
  retractions are contained."* **Its own output already names `\petGbdtGap`; nobody read that line
  against `paper_body.tex`.** The cheap improvement is not to the check but to its *input*: it currently
  asks *"do marked values escape?"*, and the complementary question *"is every value on
  `INDEX-retracted-and-superseded-values.md` marked?"* would have caught finding 2 and is answerable
  from a list that already exists.
- **Finding 11's build-breaker half is a three-line move** — put `\bpn`/`\gk`/`\jrb` in `preamble.tex`
  (as no-ops for the outward builds if wanted) so the routine act of migrating a paragraph into
  `paper_body.tex` cannot fail an external build. The visible-reviewer-marks half is the owner's
  editorial call, except `\bpn{left off here}` and the two `[GK: …] [JRB: Fixed!]` pairs, which are
  simply residue.
- **Finding 13 needs one clause in a caption**, and the caption already nearly supplies it.

**Findings 4, 9 and 5 are for the note's owner at leisure.**

**This lane filed nothing in `FINDINGS.md`, `KNOWN_ISSUES.md`, `OPEN_ITEMS.md`, `CLAIMS.md`,
`VALIDATION_LEDGER.md` or any control-plane source, created no id, and edited no file under
`docs/analysis-note/`. Everything above routes to the note's owner.**
