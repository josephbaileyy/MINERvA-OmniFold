# AUDIT 2026-08-19 — the analysis note against the committed record

**Lane D (verifier), read-only. TRANCHE 1.** Commissioned after an outside reader found `ISSUE-57` on a
first pass through `docs/analysis-note/`, which nobody inside the repository had found. **The inference
that there are more is correct: this tranche has five, of which four are new.**

**Nothing under `docs/analysis-note/` was edited and nothing will be by this lane.** This is a routed
defect list for the note's owner, not a patch. No authority file was edited either. Measured at
`origin/main` after `git fetch && git rebase`; every quote below was read this turn from both sides.

**Severity key.** `HIGH` — the note asserts something the record contradicts, in publication text.
`MED` — a governance or traceability gap, not a wrong number. `LOW` — a citation that does not support
what it is attached to. Where I cannot tell which side is wrong I say so, because the remedy differs.

---

## Summary

| # | severity | what | note | authority | which side is wrong |
|---|---|---|---|---|---|
| 1 | **HIGH** | the full-event `C_stat` bootstrap is described as **one** stream; the note says **two** elsewhere; the record specifies **three** | `app_statmethods.tex:1472-1476`, `:1479-1480` | `DETERMINATION-20260817-lanec-cstat-object-is-total-statistics.md:27,48` | **the note** |
| 2 | **HIGH** | four dead `\gbdtFive*` values print as unmarked prose while the note's own `\dead{}` marker is used 19× elsewhere | `sec_systematics.tex:163,165,166,168` | `VALIDATION_LEDGER.md:916,940`; `INDEX-retracted-and-superseded-values.md` | **the note** |
| 3 | **MED** | 16 of 70 `values.tex` macros have no `VALIDATION_LEDGER` row, against `CLAUDE.md`'s canonical-home rule | `values.tex`, 16 lines listed | `CLAUDE.md` routing table | **neither — a gap** |
| 4 | **LOW** | `CLM-012` cited as authority for the `niter=3` policy, which `CLM-012` does not state | `sec_pet.tex:55-56` | `CLAIMS.md` `CLM-012` | **the note** |
| 5 | **INFO** | `CLM-010`/`CLM-012` carry live independence caveats; the note's use is narrower than the caveat's scope | `sec_pet.tex:55-56` | `CLAIMS.md`; `DETERMINATION-20260818-lanec-clm012-status-conflates-two-claims.md` | **probably neither** |

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

## What this tranche did NOT cover

Stated because an audit silent about its own reach reads as complete.

1. **Only `values.tex`'s 70 macros were traced.** The note's own header says numbers appearing exactly
   once *"are NOT macroized here … they stay inline at their single site"* — **so the inline numbers are
   the larger population and none of them was swept.** `app_statmethods.tex` alone carries dozens
   (`67.1%`, `3.5969`, `0.868`, `76.7`, `0.356`…). This is the biggest gap in tranche 1 and the obvious
   tranche 2.
2. **`sec_3d.tex`, `sec_eavailw.tex`, `sec_fps.tex`, `sec_method.tex`, `sec_results.tex`,
   `sec_validation.tex`, `app_negweight.tex`, `paper_body.tex`, `primer_body.tex` were not read for
   axis-1 object descriptions** — only searched for specific retired strings. `ISSUE-57`'s class is found
   by *reading*, not grepping, because the defect is a correct-sounding sentence about the wrong object.
   **A grep sweep cannot find another `ISSUE-57`.**
3. **The three builds may differ.** `main_note.tex`, `main_paper.tex` and `main_primer.tex` include
   different subsets; I did not check whether a defective passage reaches all three. A defect in the
   `paper` build is worse than the same defect in `note`.
4. **`KNOWN_ISSUES.md` was in the corpus for the numeric sweep but was not read against the note's
   methodological claims.**
5. **No cluster access.** `ssh` exits 255 under `maintenance_20260819`, so nothing was re-derived from a
   product; every authority above is a committed file.
6. **The 2D-vs-full-event scoping question in 1c is open** and only the pipeline's owner can close it.

---

## Routing

**Findings 1 and 2 are the ones that reach outside the collaboration**, and they differ in what they need:

- **Finding 2 can be discharged today without any new number.** `\dead{}` already exists and is already
  used correctly elsewhere in the note. Striking four macro uses requires no adopted replacement, and
  `PROCEDURE-gbdtFive-macro-update.md` is explicit that replacement is neither authorized nor a drop-in.
  **This is the cheapest real risk reduction available in the note.**
- **Finding 1 needs a decision, not an edit.** Whether §`sec:bootstrap`'s two-stream description is
  correct for the 2D pipeline while the full-event one is three-stream is a fact about the code, and the
  remedy for §`app:cstatlimit` differs depending on the answer. **Owner: the lane that owns
  `SPEC-20260814-gate5-cstat-construction-v1.md`.**

Findings 3, 4 and 5 are for the note's owner at leisure. **This lane filed nothing in `FINDINGS.md`,
`KNOWN_ISSUES.md`, `OPEN_ITEMS.md` or `CLAIMS.md`, and edited no file under `docs/analysis-note/`.**
