# AUDIT 2026-08-19 — the analysis note against the committed record

**Lane D (verifier), read-only. TRANCHES 1 AND 2.** Commissioned after an outside reader found `ISSUE-57`
on a first pass through `docs/analysis-note/`, which nobody inside the repository had found. **The
inference that there are more is correct: nine findings, eight of them new.**

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
| 2 | **HIGH** | N | four dead `\gbdtFive*` values print as unmarked prose while the note's own `\dead{}` marker is used 19× elsewhere | `sec_systematics.tex:163,165,166,168` | `VALIDATION_LEDGER.md:916,940`; `INDEX-retracted-and-superseded-values.md` | **the note** |
| 4 | LOW | N | `CLM-012` cited as authority for the `niter=3` policy, which `CLM-012` does not state | `sec_pet.tex:55-56` | `CLAIMS.md` `CLM-012` | **the note** |
| **9** | LOW | N | *"production iteration count `n=5`"* and *"the campaign's pinned policy is `niter`=3"* stand unreconciled | `sec_method.tex:145-147`; `sec_pet.tex:55-56` | — | **neither — a scope hazard** |
| 5 | INFO | N | `CLM-010`/`CLM-012` carry live independence caveats; the note's use is narrower than the caveat's scope | `sec_pet.tex:55-56` | `CLAIMS.md`; `DETERMINATION-20260818-lanec-clm012-status-conflates-two-claims.md` | **probably neither** |

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

## 2. HIGH — four dead values print as unmarked prose, and the note's own strike mechanism is used 19 times elsewhere

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
is used **19 times** — 13 in `app_statmethods.tex`, 6 in `sec_pet.tex` — including a model treatment at
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

---

## What these tranches did NOT cover

Stated because an audit silent about its own reach reads as complete.

1. **Only `values.tex`'s 70 macros were traced.** The note's own header says numbers appearing exactly
   once *"are NOT macroized here … they stay inline at their single site"* — **so the inline numbers are
   the larger population and none of them was swept.** `app_statmethods.tex` alone carries dozens
   (`67.1%`, `3.5969`, `0.868`, `76.7`, `0.356`…). This is the biggest gap in tranche 1 and the obvious
   tranche 2.
2. **Tranche 2 READ `sec_method`, `sec_fps`, `paper_body` and `primer_body` in full**, and
   `sec_pet`/`sec_systematics`/`app_statmethods` in the relevant parts. **Still only grepped, not read:
   `sec_3d.tex`, `sec_eavailw.tex`, `sec_results.tex`, `sec_validation.tex`, `app_negweight.tex`,
   `sec_experiment.tex`, `sec_execsummary.tex`, `sec_intro.tex`, `sec_summary.tex`, `app_negweight.tex`,
   `app_landscape.tex`, `app_codebase.tex`.** `ISSUE-57`'s class is found by *reading*: the defect is a
   correct-sounding sentence about the wrong object and has no distinctive string. **The grep results for
   those files are evidence about the grep.**
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
6. **Two questions are open and are the owner's, not mine.** The 2D-vs-full-event scoping in §1c
   (which construction §`sec:bootstrap` describes), and `\petClosure`'s legacy status in §8. **Both are
   stated with what turns on each answer rather than resolved.**
7. **Figures were not audited.** Both builds include `pet_vs_gbdt_absolute` and `fps_pilot_compare_MEFHC`
   by filename; I compared the **captions** but did not check whether the underlying image files encode
   struck numbers. A plot axis labelled with a withdrawn value is finding 7's class and no text search
   reaches it.

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

- **Finding 6 is a one-sentence correction and it is the most consequential edit in this document.** The
  paper names LightGBM as *"the learners"*; the note says the central value is `exact` sklearn and that
  the estimator mismatch *"should be read as a stated property of the measurement."* **Naming the right
  backend and restoring one clause fixes it. Nothing has to be re-derived, re-run or adopted.**
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
  The note already contains its own remedy: `\dead{}` is defined once and used 19 times, correctly, on
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

**Findings 4, 9 and 5 are for the note's owner at leisure.**

**This lane filed nothing in `FINDINGS.md`, `KNOWN_ISSUES.md`, `OPEN_ITEMS.md`, `CLAIMS.md`,
`VALIDATION_LEDGER.md` or any control-plane source, created no id, and edited no file under
`docs/analysis-note/`. Everything above routes to the note's owner.**
