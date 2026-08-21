# DECISION BRIEF — `OI-71`: may `VL100`'s recovery be technote-quoted while `G4` is unmeasured?

**For:** Joseph. **By:** lane C (PET), on the mediator's dispatch, 2026-08-19, at `a3c91e04`.
**This is a BRIEF, NOT A DETERMINATION.** It decides nothing, and §4 is a recommendation you can discard
while keeping §1–§3. `OI-71` is `WAITING-USER` with owner `joseph`; the input it needs is your choice, and
the closure artifact it needs is a committed determination that follows from it.

> **THE DECISION IN ONE LINE.** `VL100 = 0.512603276` is a twice-reproduced recovery that clears its PRIMARY
> criterion even under an adversarial shape correction, measured at the **closure** configuration
> (`56552326`); recovery at the **promoted** configuration has never been measured, cannot be measured
> read-only at any effort, and cannot be measured at all right now. **So: quote it with that limitation
> stated (A), decline to quote it (B), or measure first and quote nothing until then (C).**

**THE OPTION SET IS THREE, AND I CHECKED WHETHER IT WAS TWO.** Placement variants — appendix, footnote,
"diagnostic only" — are **not** separate options: they differ in where the sentence sits, not in what is
claimed, so they collapse into (A). (C) is separate from (B) only because it creates work; if you decline
the work, (C) *becomes* (B).

---

## 0. IS IT ALREADY DECIDED BY A COMMITTED ARTIFACT? — **NO, AND THE NEAREST ARTIFACT DECLINES ON PURPOSE**

The best outcome would have been finding this already ruled. It is not, and the relevant file says so in
its own words. `AUTHORIZATION-20260813-gate4-estimator-disposition.md:496-500`:

> *"that note scopes the non-quotability to not authorizing engine edits or promotion. **Whether `VL100`'s
> recovery may itself be technote-quoted is a question the receipt raises and does not answer** — and it is
> the PET lane's to answer, not Session A's."*

The promotion receipt is the same shape: `p3f-pet-gate4-nominal-promotion-56563761.json:102` lists among
things **not** claimed *"That `OI-23` is discharged … the closure artifact declares `quotable: False`, which
is the PET lane's question."* **Two artifacts route the question here and neither answers it.**

### 0a. CROSS-CHECK REQUESTED: the "zero `RULING-*`/`DETERMINATION-*` name `OI-71`" mapping is **CONFIRMED**, and I extended it to the harder case

- **Literal, with a word boundary so `OI-710`-style strings cannot inflate it:**
  `grep -rnE 'OI-71([^0-9]|$)'` over `docs/orchestration/`, filtered to `RULING-*`/`DETERMINATION-*` →
  **zero hits**, across **30** such files.
- **The failure mode the mapping could not cover — a determination that rules the subject WITHOUT naming
  the id.** Searched the decision-class files (`RULING-*`, `DETERMINATION-*`, `AUTHORIZATION-*`) by
  **subject** instead: `VL100|0\.512603276|recovery_evaluated|quotab` → **14 files**, every one read down to
  the hit. **None rules it.** The two that could plausibly have: `AUTHORIZATION-20260813…` explicitly
  declines (quoted above), and `DETERMINATION-20260817-pet-ten-items-state-and-oi126-shape.md` — a PET-lane
  determination over ten items — **does not cover `OI-71`**; the ids it names are
  `OI-12, 41, 57, 58, 60, 61, 62, 64, 65, 82, 90, 96, 126`.
- ⚠ **One false-positive class worth recording, because it would mislead the next searcher:** `quotab`
  matches **"quotable cells"**, a statement about *bins*, not about evidence admissibility. That is the only
  hit in the PET ten-items determination. **Two different senses of the word live in this repo.**

**Limits of my search, so it can be falsified:** it covers `docs/orchestration/` at `a3c91e04` and only the
three decision-class filename prefixes. A determination recorded under a different prefix, inside
`FINDINGS.md`, or in a receipt JSON would be missed — and a determination that names neither the id nor any
of my four subject terms is unreachable by any string search.

---

## 1. THE DECISION — THREE OPTIONS

### (A) QUOTE `VL100`, WITH `G4` STATED AS AN EXPLICIT LIMITATION

| | |
|---|---|
| **Becomes quotable** | `VL100 = 0.512603276`, its PASS margin `+0.018020876` against PRIMARY `≥ 0.494582400`, and its survival of both shape corrections — **all attributed to the closure configuration `56552326`.** |
| **Stays unquotable** | Any sentence asserting or implying that recovery holds **at the promoted artifact**. Any use of the closure as reassurance about the nominal's fold-forward deficit (see §3). |
| **New work** | One technote paragraph plus the committed determination that closes `OI-71`. **No cluster. No compute.** Also discharges the residual transferred here from `OI-23` (`OPEN_ITEMS.md:91`). |
| **Load-bearing assumption** | `OI-23`'s configuration equivalence — **an argument that the two configurations would score alike, not a measurement that they do.** This is the whole of what (A) rests on and §2 states it as assumed. |

### (B) DECLINE TO QUOTE `VL100`

| | |
|---|---|
| **Becomes quotable** | Nothing new. |
| **Stays unquotable** | `VL100` in every form, including the margin and the adversarial-correction result. |
| **New work** | **None in the technote — verified, not assumed: `docs/analysis-note/` contains no occurrence of `0.512603276` or of `VL100`.** So nothing is retracted and no build changes. The determination itself is the only artifact. |
| **Cost** | Discards a twice-reproduced measurement that clears its criterion, to avoid stating a limitation. `OI-23`'s transferred residual is closed by ruling rather than by evidence. |

### (C) MEASURE RECOVERY AT THE PROMOTED CONFIGURATION FIRST, QUOTE NOTHING UNTIL THEN

**The measurement, named:** a recovery evaluation at the promoted nominal `56563761` — i.e. an injected
truth reweight with a tilt and an A/B split, scored the way `VL98`–`VL100` were scored at the closure.

**This is a NEW RUN, not a re-analysis, and three separate things block it:**
1. **The promoted nominal has neither tilt nor A/B split** (`OPEN_ITEMS.md:64`), so recovery is undefined on
   the existing artifact. There is nothing on disk to re-score. **This is why `G4` is "not determinable
   read-only at any effort" — it is a missing experiment, not a missing calculation.**
2. **It needs the cluster, which is unreachable.** `ssh saul.nersc.gov hostname` → **rc=255**, read unpiped,
   this turn. Nominal maintenance window to **`2026-08-26T13:00Z`** — and per the run receipt's own wording
   that end is **an outer bound, not a prediction**.
3. **It needs a fresh authorization from you regardless of the cluster:** the promotion receipt's
   `scope_PROMOTED_IS_NOT_PROCEED.NOT_authorized` lists *"any recovery run"*.

**Consequence:** (C) cannot start today, and choosing it is choosing to leave `OI-71` open for at least a
week. **I have not costed it**, because the 2026-08-15 precedent is that a costed instrument's claim to close
`G4` did not survive contact — `PROPOSAL-20260815-…` was costed at 11.7 GPU-h to "close `G4`", ran (~5.9
GPU-h per arm, both arms `0:0`), and **did not close it**, because it measured at the closure configuration
too. **A cost estimate for (C) from me would be the same class of claim.**

---

## 2. MEASURED versus ASSUMED

**MEASURED — cited, not restated in new numbers where the ledger forbids it (`BEN-227`/`BEN-228`):**

| Fact | Where |
|---|---|
| `VL100 = 0.512603276`, PRIMARY `≥ 0.494582400`, **PASS by `0.018020876`** | `VALIDATION_LEDGER.md:1828` |
| Reproduced **twice** independently (persisted spectra; per-event `weights_push`), `d = 0.000e+00` | `VALIDATION_LEDGER.md:1849` ff; `state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json` |
| Survives a **well-posed** shape correction (margin `+0.016557`) and an **adversarial** one (`+0.014491`); needs **`2.8×`** the measured amplitude to break | same receipt; `OPEN_ITEMS.md:64` (4)(d) |
| `G1` physics ground **mis-targeted**: manifest's `weights_path` is the **pre-anneal** arm (`58f664cd…`, `lr_policy` key absent) while `VL100` is the **annealed** arm (`559a1020…`) | `BEN-312`, `FINDING-20260815-the-quarantine-measured-a-different-run.md` |
| `G2` label **not independent** of `G1`; `G3` provenance hygiene **clean** (14 pins pass) | `OPEN_ITEMS.md:64` GROUNDS block |
| **`recovery_evaluated` remains `False` at the promoted configuration** | `state/p3f-pet-gate4-nominal-promotion-56563761.json:101` |
| The closure's fold-forward ratio is `1.011418` against the nominal's `0.736746` | `OPEN_ITEMS.md:64` (4)(e); `BEN-360` |
| The instrumented closure **ran**, both arms complete | `AUTHORIZATION-20260815-foldforward-closure-run.md`; `state/RECEIPT-foldforward-instrumented-closure-20260815.json` |
| **`docs/analysis-note/` quotes neither `VL100` nor `0.512603276`** | measured this turn: **79 files, 23 of them `.tex`/`.md`**, zero hits for either string. Stated with its extent because a null is a claim about the search — the control that it reaches content is that `recovery` *does* hit (`app_negweight.tex`). |

**ASSUMED — and (A) rests on exactly one of these:**

1. **THE LOAD-BEARING ONE: that the closure and promoted configurations would score alike on recovery.**
   `OI-23` establishes configuration *equivalence* across 12 shared dimensions plus LR policy
   (`OPEN_ITEMS.md:91`) — **an argument, not a measurement of recovery at the promoted artifact.** If you
   choose (A), this is what the technote is standing on, and it should be named there rather than implied.
2. That the two shape corrections in (4)(d) bracket the realistic range of the correction. The adversarial
   one is drawn from the run where the deficit actually lives, which is the strongest available form of this,
   but it is a bracketing argument.
3. That `G3`'s one residual — `hash:nominal-weights` pins the **pre-anneal** file, inherited from `G1` —
   does not disturb `G3`'s CLEAN status. Recorded as residual in the GROUNDS block, not re-derived by me.

---

## 3. WHAT NO OPTION CHANGES — the bound, so this cannot be read as bigger than it is

- **`VL100`'s value.** `0.512603276` is unchanged under every option, and unchanged by the 2026-08-14
  falsification, which was **scope-corrected to mis-targeted, not falsified** (`BEN-312`). No option
  re-opens the arithmetic.
- **`G1`, `G2`, `G3` stay DETERMINED.** This decision is about `G4` alone. `OI-71`'s remaining content is one
  ground, not four — *"the four quotability grounds"* was **a count with no members** (`BEN-313`).
- **The nominal extraction's 34% deficit is untouched in magnitude** by all three options. Only its per-cell
  *structure* is explained. That needs a corrected **nominal** run, not a corrected closure, and it is
  **not** part of `OI-71`.
- **The closure remains SILENT about the deficit failure mode, not reassuring about it** — its fold-forward
  is near unity where the nominal's is not (§2). **No option converts silence into evidence, and (A) must not
  be written in a way that reads as if it did.** This is upstream of whether the margin clears.
- **`OI-125` stays narrowed, not closed** (`BEN-360`: the recorder captures the push at consumption, the
  nominal at end of run, so the like-for-like scalar is still a reconstruction).
- **The promoted artifact is not re-promoted, re-graded or disturbed.** This is an evidence-admissibility
  decision, not a promotion decision.
- **Nothing currently published is retracted under any option**, because the note quotes nothing here yet.

---

## 4. RECOMMENDATION — **MINE, AND SEPARABLE FROM EVERYTHING ABOVE**

**I recommend (A): quote it, with `G4` stated.** Take §1–§3 and reject this section if you disagree; nothing
above depends on it.

**Why.** The only surviving objection to `VL100` is an **absence of a measurement**, not a defect in one.
`G1`–`G3` are determined; the number is reproduced twice; it clears PRIMARY even under a correction built
from the run where the deficit lives, needing `2.8×` the measured amplitude to break. Against that, (B)
discards a measurement that has survived everything actually run at it, in order to avoid writing one
limiting sentence — and a technote can carry a limiting sentence. (C) buys the one thing that would settle
it, but cannot start today and, on the 2026-08-15 precedent, is the kind of instrument whose claim to close
`G4` should be distrusted until it has.

**Two conditions I would attach, because (A) done carelessly is worse than (B).**
1. **Attribute the number to the closure configuration in the same sentence that quotes it**, and state that
   recovery at the promoted configuration is unmeasured with `OI-23`'s equivalence as the named bridge. A
   bare `0.512603276` in the note re-creates precisely the drift this row was filed over.
2. **Do not let the closure's clean fold-forward do any work.** It is near unity where the nominal's is not,
   so it is silent about the deficit. If the note cites recovery *and* the deficit in the same passage, they
   must not be allowed to appear to support each other.

**The strongest argument against my recommendation, stated because you should have it:** quoting a recovery
from a run whose every artifact is prefixed `NONQUOTABLE-DIAGNOSTIC.` with `quotable: False` will look wrong
to any later reader who has not read `G2`'s determination that the label's scope is engine edits and
promotion. **That is a presentation cost, not a physics one — but it is real, and it argues for (A) being
written with its provenance visible rather than tidied away.**

---

*Filed by lane C. §0a's searches and the `analysis-note` null are measurements taken this turn at
`a3c91e04`; every other number is cited to the ledger, a receipt, or the `OI-71` row and was not
re-derived by me. **I did not run, submit, or cost any compute, and I did not touch `docs/OPEN_ITEMS.md`,
the ledger, or any receipt.** Per this repo's own rule, a null is a claim about the search: §0a's is bounded
in the paragraph that states it.*
