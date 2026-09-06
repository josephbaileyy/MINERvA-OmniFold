# VOI 2026-09-06 — cause 3's `M(ii)` fixed-draw estimator-seed scan: the value of information

**CITABLE FOR:** the value-of-information analysis in §3–§6, the proposed execution fixes in §7 (as
**proposals requiring independent verification**, not as verified repairs), the design and cost in §8,
the meter status in §9, and the recommendation in §10.

**NOT CITABLE FOR:** any authorization to submit; any grade, discharge, adoption, count change, gate
movement, spending grant or publication claim. **This document is UNSIGNED. No signature is affixed
here and none may be inferred.** Signing is Joseph's act alone. **Gate 2 remains FAIL. CAND `1 of 7`,
QUOTED `0 of 7`.** No scalar-5D covariance is adopted. PET remains diagnostic under `R6`. No compute
was run to produce this document, and it alters no scientific criterion.

**Subject:** the run declared in `PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md` §6c,
whose launch authorization `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` `R4`
**SUSPENDED**.

---

## 0. NAMING — three distinct objects that this campaign has already conflated once

| name used here | what it is | authority | costed at |
|---|---|---|---|
| **the fixed-draw scan** | the subject of this packet: 12 CV unfolds at 12 estimator seeds, one fixed data/MC draw, on the **historical candidate** G's footing | `PREDECLARE-20260901-cause3-mii` §6c; suspended by `R4` | **`8.7` GPU task-h**, worst case `18`, `0.08` CPU task-h |
| **`JBC` — the joint-baseline composite measurement**, i.e. the **M(ii) member-scan family** | the scan that varies the sweep-side (`42`) and throw-side (`1000`) estimator baselines **jointly**, per `SCOREBOARD` §2c's `(B)`; driver `mii_seed_offset_driver.py` | **authorized as a family** by `DECISION-20260830-joseph-mii-family-and-leg6.md`, at a size that lane reconciled and Joseph did **not** separately confirm; **blocked on Gate 2 FAIL**. **Not proposed or requested by any clause below** | per complete seven-arm member round: **`54.90` GPU / `86.53` CPU** task-h at round-2 actuals (§5.3) |
| **`Z` — the complete scalar-5D successor** | a prospective seven-cause grading subject and possible adoption subject, **specification only** | `DECISION-20260906-joseph-authorizes-z-specification-only.md`, ruling label **`RZ`** | `71.5` GPU / `114` CPU task-h for one Z build (`SPEC-20260906-complete-scalar5d-successor-Z.md` §5.3) |

> **⚠ `JBC` IS NOT `Z`, AND `JBC`'s COST IS NOT `Z`'s COST.** An earlier draft of this packet used the
> letter `Z` for the joint-baseline composite scan. That letter now belongs to the complete scalar-5D
> successor under `RZ`, and the collision would attribute a `39.223`/`55.337`-per-seed scan price to a
> successor whose own costed build is `71.5` GPU / `114` CPU. **The two figures price different
> objects and neither may be quoted for the other.** `JBC` is used below and no single letter is.
>
> A third conflation is already on the record and is noted so it is not re-made: **rehearsal arm 2 is
> called *"seed split"* and is NOT this scan** — it is the ML-split replica arm at `8` CPU task-hours,
> whereas the fixed-draw scan is 12 **GPU** tasks (`SPEC-20260906` §5.4 and its surrounding note).

---

## 1. Authority, and what `R4` preserves

The governing decision is `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`, committed at
**`9ce59a59`**, author instant **`2026-09-02T15:44:27+02:00` = `2026-09-02T13:44:27Z`** — `R5`'s
accounting `t0`, read from the commit object. **`dae18f22` was a rename, not a new start:** its
diffstat is one path rename plus the `CATALOG`/`MANIFEST` rows a rename requires, and it changed no
ruling text. `R4`–`R5` are untouched by `RZ`, which states that `R1`–`R6` *"override it wherever they
conflict."*

**The `#11` plan is not an authority for anything here** and no clause below derives from it.

### 1.1 What `R4` PRESERVES — quoted, because the rest of this packet is bounded by it

> **LEAVES UNCHANGED:** §1's quantity, §2's footing falsifiers, §3's thresholds `f_agg <= 0.0415` and
> `f_med <= 0.0274` with their publication-precision derivation, §4's six branches and §5's limits —
> **the criterion is not retuned; only the purchase is gated.** `M(i)` remains satisfied.

**`R4` also settles the premise that the scan is worth grading at all:** *"the scan **does** change a
named decision — it grades cause 3's `M(ii)` for this candidate."* Rev. 1's *"changes nothing"* claim
was withdrawn before Joseph ruled.

**And `R4` fixes the gate at exactly two documents, no more:** *"The scan may be submitted only after
**both**: a value-of-information note signed by Joseph, and a **separate committed reauthorization**
naming the run. A VOI signature does not by itself revive compute authority."* **This packet is the
first of those two and adds no third.** Where §5 records a separate open question, that question
bounds what a result may later be *used for*; it is **not** a precondition on the narrow measurement,
and §10 does not treat it as one.

### 1.2 `R5`'s four values, carried forward unchanged

| `R5` field | value |
|---|---|
| stop date | **`2026-09-30`**, UTC, inclusive — fires at the first instant `now >= 2026-09-30T00:00:00Z` |
| GPU ceiling | **`500` GPU task-hours** |
| CPU ceiling | **`500` CPU task-hours** |
| accounting start | **`2026-09-02T13:44:27Z`** at `9ce59a59` |

No new cap option is proposed and no accounting reset is proposed.

---

## 2. What is being bought

Twelve replicas of the **background-aware CV unfold** at twelve estimator seeds and one fixed data/MC
draw, combined into `C_seed`, reduced to `m_seed = sqrt(Tr C_seed)` and two ratios:

```
f_agg = m_seed / 4.357790406860002e-38            MET iff <= 0.0415
f_med = median_i sqrt((C_seed)_ii) / sigma_i^cand  MET iff <= 0.0274
```

`f_agg`'s bound re-derives to `m_seed <= 1.808483018846901e-39 cm2/nucleon`, exactly the value §3
prints — the predeclaration's own arithmetic reproduces, checked here rather than assumed.

**The population is 12 CV unfolds, not 12 covariance constructions.** `§6c` fixes it: *"estimator seeds
`1..12`, CV unfold, no data draw"*, and the launcher's CV arm takes no draw parameter (§7.1). This
bounds every row of §3, so it is stated before the table.

---

## 3. THE VALUE-OF-INFORMATION TABLE — four consequence classes, kept separate

| # | consequence class | does the scan change it? | the binding evidence |
|---|---|---|---|
| **1** | **cause 3's `M` grade cell (CAND)** — `SCOREBOARD-20260817-quarantine-seven-causes.md:74`, currently `OPEN and NOT CURRENTLY MEASURABLE` | **YES — this is the purchase, and `R4` recognizes it.** Four of §4's six branches land a valid measurement; two land INCONCLUSIVE | `R4`: *"it grades cause 3's `M(ii)` for this candidate."* **A second change rides along free of compute:** the cell's own *"NOT CURRENTLY MEASURABLE"* is **stale twice over** — `§6b`'s preflight found the footing exists, and §7.5 verifies that the two-role `--seed` obstruction `SCOREBOARD` §2b rested on has since been **split in code**. Correcting a live board that asserts a false impossibility is the same defect class `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` §5 routed for the neighbouring `P-ii` cell |
| **2** | **cause 3's discharge (CAND)** | **NO, and not by any margin.** `M` is one leg of four | `CRITERIA-20260811` §0: *"All four must hold; any one failing leaves the cause OPEN."* At `SCOREBOARD:71-75` cause 3 carries **`C` = PARTIAL, "INAPPLICABLE to the dominant block"**; **`P-i` = PARTIAL**, its clause (i) *"the receipt records the seed value"* **NOT MET on both legs** (§2d); `P-ii` = OPEN as written (live state disputed — `OI-170` records a regrade to SATISFIED, the board still reads `OPEN`, and the no-fourth-token record §5 routes the cell as **unrepaired**; nothing below depends on which is right); `T` = MET. The board's operative `RULED 2026-08-17` — *"a cause carrying [an `INAPPLICABLE` leg] CANNOT discharge"* — stands, and no fourth token was added. **`P-i` is additionally unclosable for this artifact:** `OI-171` made it RUN-CARRIED and `OI-170`'s discharge note states the corollary — *"this supplies **no provenance to CAND or QUOTED**"* — because CAND predates every producer that writes the stamp |
| **3** | **adoption of a scalar-5D covariance** | **NO** | §5's four prohibitions: it cannot *"discharge cause 3 as a whole, close any other quarantine cause, change CAND/QUOTED counts, adopt a covariance, move Gate 1 or Gate 2, or touch `values.tex`"*, and *"does not add `C_seed` to the uncertainty budget."* `R4` preserves §5. Independently, `AGENTS.md` grades the corrected 5D candidates `QUARANTINED`, and `RZ` adopts nothing |
| **4** | **publication consequences** | **NO on submission. NO on the Letter as scoped. One possible disclosure that REQUIRES ITS OWN ASSESSMENT AND RULING** | `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md` half (a): the covariance gates *"one claim … and **not** the Letter as scoped"*, verified at `paper_body.tex:145-148`. `R5` makes the scoped Letter the default at the stop. **On the possible disclosure, stated as an open question and not as a consequence:** a valid measurement — at any magnitude — may or may not warrant its own statement in the note. **That is an editorial and publication assessment reserved for Joseph, and it is unruled for cause 3.** It is **not** inherited from cause 1: `DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` RULING 1 found *cause 1's* magnitude material enough to need its own note statement, and `R3` expressly *"creates **no** note obligation"* for cause 7's `M`. Neither ruling reaches cause 3, and this packet asserts no obligation on its behalf |

**One-line summary:** the scan buys **one grade token on one leg of one cause for one artifact**. Rows
2 and 3 are blocked by evidence that does not mention the estimator seed; row 4 opens a question rather
than settling one.

---

## 4. Row 1 priced honestly, within what `R4` preserves

`R4` preserves §3's two thresholds and §4's six branches, so **the branch a result lands in is already
fixed and is not re-openable here.** Four branches produce a valid measurement; §4 labels one of them
`MET` and three `NOT MET`.

**What is not fixed is what a `NOT MET` branch implies downstream, and that is a reading rather than a
gate.** Two committed sentences bear on it and no lane has composed them:

* `CRITERIA-20260811` §0: *"**M does not require the corrected number to be small.** A measured large
  difference discharges the cause just as well as a measured small one; what is forbidden is an
  unmeasured one."*
* `PREDECLARE-20260901-cause3-mii` §3/§4 make `MET` conditional on both ratios and label the three
  over-threshold branches `NOT MET`.

**Both are preserved by `R4` and neither is touched here.** The observation is only that a `NOT MET`
outcome will be a *measured* magnitude, which §0 treats as the thing the leg exists to produce, and
that how the two compose is a grading question for a lane `BEN-381` does not disqualify. **It does not
gate the measurement and §10 does not make it a prerequisite.** Recording it now matters for one
reason: settling it *after* a number exists would be measurability choosing the specification, which
`SCOREBOARD` §2c adopted a standing rule against.

---

## 5. THE SEPARATE QUESTION — substitution for the joint-baseline composite measurement

### 5.1 What is separate, and what is therefore NOT a prerequisite

`SCOREBOARD` §2c's `CONCEDED 2026-08-17` block adopted **`(B)`** — vary both estimator-seed baselines
jointly on the composite — as `M(ii)`'s specification, on a measured ground:
`a0cdc01:unified_throw_cov.py:225-227` records that the block units and `x_cv` *"share one seed, so
their jitter cancels"*, so the inter-leg estimator-noise covariance is set by whether the legs share a
seed, and `(A)`-shaped per-leg reasoning *"assumes zero covariance under precisely the condition that
creates it."* `VL141` consequence (b) independently records that `M(ii)` must vary both seeds.

`PREDECLARE-20260901-cause3-mii` §5 states the boundary in its own words: the fixed-draw scan *"does
not by itself resolve whether the candidate's two historical estimator-seed baselines (sweep-side
`42`, throw-side `1000`) must be varied jointly in a full composite-member scan… treating it as a
**substitute** for a full two-baseline composite scan would require a **separate ruling**."*

**Read exactly: the reserved ruling is about SUBSTITUTION, not about permission to measure.** `R4`
recognizes the narrow fixed-draw measurement as grading cause 3's `M(ii)` for this candidate, and `R4`
sets the gate at two documents. **So the substitution question does not gate the narrow measurement,
and this packet does not convert it into a third prerequisite.** What it does bound is the *later use*
of the result: absent that separate ruling, a fixed-draw magnitude may not be quoted as the
joint-baseline composite magnitude, and `SPEC-20260906` §7 item 3 already carries the scope fork as an
open question of its own.

### 5.2 `JBC` is not a hypothesis — it is the M(ii) member-scan family, authorized and partly built

**This is the correction that most changes the picture, and it runs against the earlier draft.** `(B)`
has a committed driver and an authorized family:

* **A driver exists.** `nd-unfolding/mii_seed_offset_driver.py:2` — *"Four-leg estimator-seed offset
  scan driver for M(ii) (spec **(B)**, option (ii) OFFSET)"* — and it is the only caller of the
  clean-offset predicate (`:222`, `:227`). Its `--offsets` grid is **required with no default**: the
  `1200` default was removed because *"an omitted or mistyped grid silently planned the wrong"* scan.
  So there is no committed grid, only a required argument.
* **The family is authorized.** `DECISION-20260830-joseph-mii-family-and-leg6.md` authorizes *"the
  **M(ii) member scan as a family**, superseding ruling 12's withholding"*. Its size — **50 members
  conditional on HPSS archiving, 46 as the floor** — is that lane's own reconciliation of two
  mutually exclusive options, expressly *"NOT separately confirmed"* by Joseph and open to challenge.
* **Three members already exist**, each stopped after legs 1–5: `nd-unfolding/mii/member_k000000`,
  `member_k001200`, `member_k002400`. **No member has ever completed end-to-end** — leg 6 has never
  run.
* **The binding constraint is Gate 2, not cost and not code.** That decision says so in its own
  words: *"**Gate 2 is FAIL** … The gate, not the family authorization, is the binding constraint,
  and no authorization from Joseph removes it — only the rehearsal work landing does."* Its ordering:
  **Gate 2 PASS → leg 6 on k=0 → one member verified end-to-end → family launch.**

**So `(B)` is neither unauthorized nor blocked on configurability (§7.5). It is blocked on Gate 2.**
And the `mii/` namespace of §7.3 is *this* grid's namespace, which is why depositing cause-3 products
in it is the objection it is.

### 5.3 The cost of `(B)`, with every population named — and what does NOT follow

**Three accountings exist in the tree and they cover DIFFERENT arm populations.** Naming the
population beside each figure is not pedantry here: this exact cell has already produced four wrong
cost numbers, every one of them by comparing across unlike populations.

| accounting | arm population | GPU task-h | CPU task-h | source |
|---|---|---:|---:|---|
| one complete seven-arm member round, **round-2 actuals** | all seven arms | **`54.90`** | **`86.53`** | `AMENDMENT-20260831-oi177` §5's R2 column, summed here by metered unit |
| the same round at its **ratified per-arm ceilings** | all seven arms | **`70`** | **`113`** | `AMENDMENT-20260831-oi177` §5; `R5` §1 quotes this pair |
| *"one additional estimator seed"* | **the `C_syst` sweep/detector arms only** — `23.840 + 14.2075 + 1.030 = 39.078`, plus `0.1458` | `39.223` | `55.337` | `SCOPE-20260818-gate1-seed-separation-two-keys.md` `:22`, `:340` — **derived at neither site** |

> **⚠ The third row is NOT a per-member cost and must never be summed with the first two.** It covers a
> narrower arm population, and `INDEX-retracted-and-superseded-values.md` carries the same pair with
> its arithmetic chain (`39.078 + 0.1458 = 39.2238`; `55.182 + 0.1550 = 55.337`) plus the warning
> *"⚠ DO NOT QUOTE `39.078` BARE — it is the GPU column only, and the CPU half is the LARGER one."*
> `SCOPE-20260818` states the pair twice and derives it at neither occurrence — verified, both are
> *"does NOT ask"* / *"NOT authorized here"* disclaimers. Any plan relying on them should re-derive
> them first.

**Unit statement, before any ratio.** On these arms each scheduler task holds **one** A100 — arm 3's
`13.76` A100-h over 19 tasks at 43.5 min reproduces as `13.78` task-hours — so the A100-hour and
GPU-task-hour columns coincide here. They diverge for any arm requesting more than one GPU per task,
and `R5` meters **task-hours**
(`DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`).

**What the numbers establish, stated no wider than the evidence:**

* **`R5` has already done this arithmetic on itself.** §1: *"A complete seven-arm k=0 rehearsal round
  is ratified at **70 GPU / 113 CPU** task-hours. `500/500` is therefore about **seven** GPU
  rehearsal-equivalents and **4.4** CPU ones, which four weeks cannot consume. **The date binds; the
  ceilings are a backstop.**"* Reproduced here: `500/70 = 7.14`, `500/113 = 4.42`.
* **The authorized family AS SIZED cannot complete inside one `R5` campaign.** At round-2 actuals, 46
  members is `2,525` GPU + `3,980` CPU task-hours and 50 is `2,745` + `4,326` — **5× to 9× either
  ceiling**. `R5` anticipates this rather than being surprised by it: continuation past the stop
  *"requires a fresh decision; continuation is **not** the default."*
* **It does NOT follow that no affordable `(B)` measurement exists, and this packet does not say so.**
  The family's size is an unconfirmed reconciliation; the per-seed figures are underived at their
  primary site and cover a narrower population; a reduced-member `(B)` design has been costed by
  nobody; and the operative blocker today is **Gate 2**, not affordability. **Whether an affordable
  `(B)` measurement exists is unmeasured**, and answering it is not this packet's subject.

## 6. What actually gates submission today

| gate | status |
|---|---|
| `R4` document 1 — a VOI note signed by Joseph | **this packet, UNSIGNED.** Joseph's act |
| `R4` document 2 — a separate committed reauthorization naming the run | **absent** |
| the campaign queue's fail-closed `R5` gate — a committed, Perlmutter-measured meter receipt | **absent** (§9). `ACCEPTANCE-20260905` §2: *"The queue admits no item at all until a receipt measured on Perlmutter is committed, and none is"* |
| §7's execution fixes — independently verified | **not verified.** Proposed by this lane, which measured them (§7) |

**The substitution question of §5.1 is deliberately not in this table.** It bounds later use, not
submission.

---

## 7. PROPOSED EXECUTION FIXES — measured by this lane, REQUIRING INDEPENDENT VERIFICATION

**Status of this whole section: PROPOSALS.** Every item was measured by this lane, so under `BEN-381`
this lane is not the one to certify or apply them. They are recorded so a verifier has something exact
to check, and **none may be treated as a verified repair or folded into a reauthorization until
independently re-measured.** Measured at HEAD `c71b319a` and at the deployment sha `7ac0edec`. They
concern the **execution declaration** only; §1's quantity, §2's falsifiers, §3's thresholds and §4's
branches are untouched, as `R4` requires.

### 7.1 `§6b`'s citations resolve at the DEPLOYMENT, not at `main` — favourable

`§6b` cites `sbatch_unfold_5d_detector_bkgaware_gpu.sh:278-279` (`OMNIFILE`/`FLUX_MC`) and `:294`
/`:308` (`--omnifile`/`--mcfile`). **At `main` those are `:323-324`, `:339`, `:353` — a +45-line drift.
At `7ac0edec` they are exactly `:278-279`, `:294`, `:308`.** So `§6b`'s preflight measured the **frozen
deployed tree**, the correct operand, and its favourable finding stands: the bkgaware arm reads ROOT
directly and `of_inputs_5d.npz` is not on the path. **Proposed:** record the sha beside the citations,
or the next reader re-checks them against `main`, finds them broken, and "corrects" a sound preflight.

`FREEZE-20260830-k0-deployment-7ac0edec.md` does not block this run — its rule prohibits *"checkout,
reset, fetch-and-merge, re-declaration, or branch repoint"* **in that directory**, and its own
NOT-CITABLE-FOR list names *"any M(ii) leg"*. What it does imply is that `MNV_CODE_ROOT` must be a
named clean sha and that `7ac0edec`, not `main`, is what §2's checks read against.

### 7.2 The declared seed set `1..12` and the launcher's `42 + k` construction

At `7ac0edec:284` the launcher computes `EST_SEED=$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))` and passes
`--seed ${EST_SEED}`; there is **no direct seed argument**. Three routes exist:

| route | seeds | vs §1's literal `1,...,12` | proposed reading of the consequence |
|---|---|---|---|
| hooked, `k = -41..-30` | `1..12` | **matches** | the only route that appears to satisfy §1 and §2 check 5; see §7.3–§7.4 |
| hooked, clean offsets `k >= 1118` | `1160..1171` | **mismatch** | §4 branch 2's readback falsifier would fire — **after** the spend |
| unhooked, `--seed` direct | `1..12` | matches | **two independent problems.** `seed_offset_policy.declared_offset` returns `(0, 0)` when the env is unset, and its docstring reads *"declared = 0 … NOTHING can be concluded about which scan member it is."* **And `mr_member_dir` returns `""` with no offset declared**, so all 12 replicas resolve the identical output path and `mr_skip_if_complete` skips 11 of them — §4 branch 2's digest-collision falsifier |

`§6c`'s sentence *"satisfied by passing only `--seed`"* selects the third route. Negative offsets are
supported: `lib_member_resume.sh:80` formats `member_kneg%06d`, and `mr_require_valid_offset` accepts
`^(0|-?[1-9][0-9]*)$` while refusing zero-padded values with the octal-divergence reason stated.

### 7.3 The hooked route writes into the `mii/` M(ii)-family namespace

`mr_member_root` composes `"${MII_CONTAINER}/member_k…"` with `MII_CONTAINER="${MII_CONTAINER:-mii}"`,
so the hooked route would create 12 member directories inside the **M(ii)-family member namespace** —
the k=0 rehearsal's *member axis*, a different object from cause 3's magnitude leg that happens to
share the name `M(ii)`. That namespace has required **three** per-instance dispositions, the last of
which (`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`) states it is *"**not** a standing
rule and **not** a precedent that pre-approves the next one"* and records the failure mode: markers
matching the offset mean `mr_skip_if_complete` *"does **not** fail on them — **it adopts them**."*

**Proposed:** set `MII_CONTAINER=cause3_mii_20260901`, a one-variable change that keeps hooked
provenance and touches no shared namespace.

### 7.4 The clean-offset predicate classifies these offsets dirty; nothing on this path enforces it

`seed_offset_policy.PER_UNIT_SEED_RANGES` gives `bootstrap replica seed = (1, 100)` and
`seedscan split seed = (1, 24)`. With the `g1` baseline `42`, offsets `-41..-30` yield estimator seeds
`1..12`, each inside **both** ranges, so `forbidden_offsets` flags every offset §7.2's viable route
needs; the module derives its clean region as `k >= 1118`. Two measurements bear on it:

1. **The predicate is not on this path.** `unfold_nd_omnifold_unbinned.py:1123-1126` imports
   `seed_offset_policy` for `declared_offset()` only — *"for STAMPING ONLY — never for behaviour"* —
   with this leg registered in `LEG_BASELINES` as `("g1", 42)`. Enforcement lives in
   `mii_seed_offset_driver.py:222,227`, a different arm. Nothing fails closed and nothing warns.
2. **The confound the predicate names has no site in this arm.** Its stated harm is that *"inside a
   single member, one unit's draw RNG and the estimator RNG are seeded identically."* A draw-free CV
   unfold contains no bootstrap replica and no seedscan split unit to collide with.

**Proposed:** if the hooked negative-offset route is adopted, record that reasoning as a pre-execution
finding, so twelve products stamped `est_seed_offset = -41..-30` do not sit against a committed policy
that calls those offsets dirty with no guard having spoken. **Point 2 is this lane's reading of the
predicate's scope and is exactly the kind of claim that needs an independent check** — it is not a
licence to relax the predicate anywhere.

### 7.5 The two-role `--seed` obstruction has been SPLIT in code — verified at HEAD

`SCOREBOARD` §2b (2026-08-17) grounded *"`M(ii)` cannot be configured on either leg"* on two readings:
`sweep_bank_5d.py`'s hardcoded literal with no seed flag, and `unified_throw_cov.py`'s *"exactly one
`--seed`"* doing double duty, which made *"estimator seed varied with the draw held fixed"*
unsatisfiable. **Both are false at HEAD `c71b319a`, measured here independently:**

| leg | at HEAD |
|---|---|
| sweep | `sweep_bank_5d.py:358` `--estimator-seed`; `add_argument` count **15**; `:344` comments *"This was the literal `seed=42`"*; `:309` writes `TParameter("estimator_seed")` |
| throw | `unified_throw_cov.py:630` `--draw-seed` and `:634` `--estimator-seed`, **both `required=True`**; `:269` `default_rng(args.draw_seed + gj)` drives the draw; `:569-570` write **both** keys |

**Consequences, both routed rather than applied.** `SCOREBOARD:74`'s *"NOT CURRENTLY MEASURABLE"* and
§2b's configurability ground are stale, which is §3 row 1's free rider; and `(B)`'s blocker moves from
**code** to **Gate 2 FAIL** (§5.2) — not to cost, and not to anything this packet asks for. **This lane took the measurement and therefore grades no cell**;
the same finding was reached independently by the `lane/y-cause7-spec-and-scope` lane at `d2a515e0`
(`SPEC-20260906` §2.3), which is corroboration from a second reading rather than a shared origin
counted twice.

---

## 8. THE DESIGN ACTUALLY COSTED, and its cost

**`12` replicas is minimal by ruling, not by choice.** §1 fixes the population at *"exactly 12"* and
`R4` preserves §1. Reducing it would re-open a criterion Joseph deliberately froze and would degrade
the `f_med` leg §3 calls *"independently binding"*. What follows is `§6c`'s design; the §7 rows marked
**PROPOSED** are not part of any authorized design until independently verified.

| element | value | basis |
|---|---|---|
| scientific replicas | **12** — estimator seeds `1..12`, CV unfold, no data draw | §1, §6c |
| scheduler tasks | **13** — a 12-task GPU array plus one CPU combine | §6c |
| per-replica basis | `det5dBKG` job `57753244`: mean **43.5 min**, min `41.9`, max `45.5`, n=19 | §6b/§6c — the same operation on the same footing |
| **expected GPU cost** | **≈ 8.7 GPU task-hours** | `12 × 43.5 min`, re-derived here |
| expected CPU combine | ≈ **0.08** CPU task-hours | §6c |
| walltime request | **`--time=01:30:00`** per GPU task | §6c |
| worst-case ceiling | **`18`** GPU task-hours | `12 × 1.5` |
| execution route | **PROPOSED** (§7.2–§7.4): hooked `MNV_EST_SEED_OFFSET = -41 … -30`, `MII_CONTAINER=cause3_mii_20260901`, code root `7ac0edec`, the §7.4 exemption recorded | requires independent verification |
| durability | **PROPOSED, and required by a standing condition:** preserve the output ROOT off scratch and commit its digest from the moment it exists | `OI-130` names this run: *"whatever the cause-3 M(ii) run produces must be tracked or preserved off scratch from the moment it exists."* `git check-ignore` puts the declared ROOT under `.gitignore:2:*.root`, so tracking is closed and off-scratch preservation is the only route |
| storage to budget | **≈ 0.92 GB**, or **≈ 1.83 GB** with `sumw2` — **derived, not measured** | `hCov_cause3_mii_seed_reported` is a `TH2D` on ~10,694-bin support: `(10694+2)^2 × 8 B = 915,235,328 B`. `§6c` declares task-hours and **no storage** |
| accounting | the run must produce the scheduler task identities the queue's `accounting` object requires, so its spend reaches a receipt | §9; `campaignctl` releases a reservation only against a committed receipt **listing the item's ids** |

**On `--time=01:30:00`: keep it.** Tightening it lowers the worst case but raises `TIMEOUT` risk, and
`R5` counts a `TIMEOUT` task **in full** — *"A failed task spends"* — while `§6c` voids its own
declaration on any resubmission. The `10%` figure `§6c` quotes is against a per-arm rehearsal envelope
that `§6c` itself says *"do not themselves authorize this new arm."*

**One naming correction to `§6c` that changes no number:** it cites the *"ratified arm-1 envelope of
`20` GPU task-hours"*, but its per-replica basis is **arm 3** (`det5dBKG`, detector) — the like-for-like
arm. Arm 1 is bootstrap. Both ceilings are `20 GPU` (`AMENDMENT-20260831-oi177` §5), so the arithmetic
is unaffected.

---

## 9. THE `R5` METER — implemented and reviewer-PASSED; NO OPERATIONAL RECEIPT, so measured headroom is unavailable

**This supersedes the "no working spend meter" reading of `DECISION-20260902` §4 item 6.** That was
true when the decision was written; Wave 1 built the instrument.

### 9.1 What exists

| component | status | evidence |
|---|---|---|
| `docs/orchestration/r5_meter.py` + `R5-METER.md` | **committed.** Implements §3 verbatim: `t0 = 2026-09-02T13:44:27Z`; task-hours over distinct task identities with step and array-bracket rows excluded; GPU identified by `AllocTRES gres/gpu=N` (typed or generic) with the partition prefix only as fallback; tasks straddling `t0` clipped, tasks ending at or before `t0` omitted; failed tasks counted in full; inclusive `>=`; OR trigger; UTC. A missing, malformed or **>24 h stale** receipt fails closed **as a stop** | `INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md` §"R5 — no operational meter" row, `a0bde16a`; 16 tests + 9 subtests on 3.11/3.12 |
| the receipt schema's `headroom` object | **committed**, with `gpu_task_hours`/`cpu_task_hours` validated for consistency against measured spend — so **remaining headroom is a receipt field**, readable directly once a receipt exists | `r5_meter.py` receipt validation, `headroom` keys |
| `campaignctl.py`'s fail-closed `R5` admission gate | **committed and reviewer-PASSED.** Headroom counts the receipt's spend **plus** this item's `maximum_cost` **plus** the `maximum_cost` of every other non-terminal compute item, under one atomic admission lock; missing / malformed / stale / fired / past-stop-date / headroom-exhausting each refuse with **exit 6**; the receipt must be a tracked path byte-identical to its HEAD blob | Wave 1 ledger rows `ef7882fc`, `9ee0d600`, `823e9c48`, `2692a67a`, `4c8667ca` |
| the reviewer verdict | **PASS**, zero live findings, on commit `7708c24c`, signed 2026-09-05 | `ACCEPTANCE-20260905-wave1-review-pass-and-closeout.md` §1 |

### 9.2 What does not exist, and what follows

**No operational receipt is committed.** Verified: `git ls-files docs/orchestration/state/` returns no
`r5-meter` path, and `docs/orchestration/state/r5-meter-receipt.json` is absent from the working tree.
The Wave 1 ledger states why — *"this host has no `sacct`, and a fabricated receipt would be a false
measurement; the first measurement is a Perlmutter act"* — and `ACCEPTANCE-20260905` §2 states the
operational consequence: *"The queue admits no item at all until a receipt measured on Perlmutter is
committed, and none is."*

**Therefore measured remaining headroom is NOT AVAILABLE today, and this packet does not compare `8.7`
or `18` against `500`.** An unused-ceiling comparison would assume the very quantity the instrument was
built to measure. What can be said:

* **The scan cannot be admitted today at all**, independently of its VOI — the queue is fail-closed on
  a receipt that does not exist. Committing a Perlmutter-measured receipt is therefore **upstream of
  submission** and is the step that converts a prospective cost into a headroom comparison.
* **Headroom is reserved, not merely spent.** Once staged, other compute items hold their
  `maximum_cost` against the same ceiling, so the scan's `18` competes with whatever else is
  non-terminal at that moment.
* **The best available prospective accounting is not this packet's.** `SPEC-20260906` §5.3 costs the
  campaign scenarios and places the fixed-draw scan inside them: one Z build `71.5` GPU / `114` CPU;
  plus an independent cold replay `143.0` / `228`; **plus this scan `151.8` / `228`**, and at the
  scan's declared worst case `161.1` / `228`. Those are **prospective**, not measured, and they belong
  to that lane's plan rather than to this one — quoted so the scan is read against a plan rather than
  against an empty ceiling.

### 9.3 The date, which binds

`R5`'s stop fires at the first instant `now >= 2026-09-30T00:00:00Z`: **24 days from 2026-09-06**,
`27.4` days from `t0`. `R5` states the pairing deliberately: *"The date binds; the ceilings are a
backstop."*

**A schedule claim that would materially shorten the window is not in committed evidence.**
`HANDOFF-20260902-k0-continuity.md:148` asserts a *"seven-day maintenance … reserved 16–23 September"*,
which would leave ~10 usable days before the 16th and ~7 after the 23rd. That file is **untracked, so
routing only**. A covering grep of committed `docs/` returns no September reservation; the only
committed one is `maintenance_20260819` (`2026-08-19T13:00Z → 2026-08-26T13:00Z`), which has passed.
**Re-measure with `scontrol show reservation` before relying on its presence or its absence** — this
packet asserts neither.

---

## 10. REASSESSMENT — buy now, defer, or skip

**Recommendation: DEFER.** Not skip: the gate change in §3 row 1 is real, `R4` recognizes it, `8.7`
GPU task-hours is small against any plausible headroom, and §7.5 removes the configurability ground
that made the cell look permanently stuck. Not buy-now: **three of the four gates in §6 are open, one
of them mechanically**, and the deferral is short and its unblockers are named.

### 10.1 Why not buy now

| ground | status |
|---|---|
| The queue is fail-closed with no committed meter receipt | **mechanical.** Submission is impossible today (§9.2), so "buy now" is not an available branch |
| The execution route in `§6c` selects the one option of three that fails a declared falsifier | **§7.2**, and the alternative route is a **proposal requiring independent verification** (§7) |
| Measured remaining headroom is unavailable | **§9.2.** A prospective `18` cannot be placed against a ceiling whose consumption is unmeasured |
| Two of `R4`'s own documents are absent | this packet is unsigned, and no reauthorization exists |

### 10.2 Why not skip

| ground | status |
|---|---|
| `R4` recognizes the narrow measurement as grading `M(ii)` for this candidate | it changes a named decision; the "changes nothing" claim is withdrawn |
| `M(ii)` is now **configurable** on both legs (§7.5) | the leg's blocked-in-principle reading is stale |
| The cost is small in the design actually costed | `8.7`, worst case `18`, `0.08` CPU |
| The board carries a false impossibility that the scan's own preflight already contradicts | §3 row 1's free rider, correctable without compute |
| **`(B)` is blocked on Gate 2 FAIL and its authorized family cannot complete inside one `R5` campaign** (§5.2–§5.3) | so the fixed-draw scan is the only cause-3 `M(ii)`-shaped measurement reachable before the stop. **This raises the narrow scan's value rather than lowering it** — and it is an argument for buying it once §6's gates clear, not for buying it today |

### 10.3 Does the scan inform `Z`'s specification? — asked because it bears on the timing

**As evidence: NO.** `CRITERIA` §0 requires `M` *"measured on X's own inputs"*, and this scan measures
G's ensemble. `(cause 3, Z)`'s `M` must be measured on Z's own ensemble, and `RZ` keeps Z's cells from
ever being combined with G's. `SPEC-20260906` §7 item 2 reaches the same answer and flags it as *"the
answer most likely to be got wrong."*

**As method and as a cost prior: YES — and that value is ALREADY BANKED, with nothing run.** What
transfers is the predeclared quantity (`m_seed`, `f_agg`, `f_med`), the six exhaustive branches, the
two thresholds with their publication-precision derivation, and the `≈8.7` GPU task-hour / 13-task
shape — all of it committed text, transferable now. **No measured value transfers, and none exists.**

**So the scan's value to `Z` does not decay with deferral**, which is the specific reason deferral is
cheap here rather than merely cautious.

### 10.4 The deferral, ordered

| order | step | cost | owner |
|---|---|---|---|
| 1 | Commit a Perlmutter-measured `R5` meter receipt (`r5_meter.py measure --write docs/orchestration/state/r5-meter-receipt.json`). It opens the queue, and its `headroom` field replaces every assumed-ceiling comparison | one `sacct` query; **no GPU/CPU task-hours** | whoever holds a Perlmutter session; the credential decision `ACCEPTANCE-20260905` §3 leaves open is Joseph's or the site owner's |
| 2 | Independently verify §7's proposed fixes and §7.5's measurements, by a lane that took none of them | on paper | a non-measuring lane (`BEN-381`) |
| 3 | Sign or decline this VOI note | Joseph's act | Joseph |
| 4 | If signed: a separate committed reauthorization naming the run, carrying the verified route from step 2 and its cost against the measured headroom from step 1 | on paper | the cause-3 lane |
| 5 | Submit the 13-task design in §8 | `≈8.7` GPU task-h, `18` worst case, `≈0.08` CPU, `≈0.92–1.83` GB | the cause-3 lane |

**Steps 1 and 2 are the whole deferral, they need no compute, and step 1 is required for any other
campaign compute as well** — so the deferral spends nothing that a submission would not have had to
spend first.

**If the substitution question of §5.1 is later ruled against the fixed-draw scan**, the correct
limitation is narrow: *cause 3's `M(ii)` has a measured fixed-draw magnitude that may not be quoted as
the joint-baseline composite magnitude; the `(B)` family that would supply that magnitude is authorized
but blocked on Gate 2, and as sized it exceeds `R5`'s ceilings by 5–9×.* **Not** *"no affordable
measurement exists"* — §5.3 does not support that, and no reduced-member `(B)` design has been costed
by anyone.

---

## 11. SIGNATURE BLOCK — to be completed by Joseph, and by nobody else

> **Joseph:** ______________________  date: __________

**This block is deliberately empty.** No lane may complete it, and an unsigned packet is not a weak
yes.

**Signing satisfies the FIRST of `R4`'s two prerequisites and authorizes no submission.** Signing does
not: discharge cause 3, grade any leg, change CAND `1 of 7` or QUOTED `0 of 7`, move Gate 1 or Gate 2,
adopt any covariance, add `C_seed` to any budget, touch `values.tex`, authorize submission of the
Letter, expire `FREEZE-20260830-k0-deployment-7ac0edec.md`, reopen `OI-126`, authorize `JBC` or any
construction of `Z`, change `R5`'s stop date or either ceiling, or reset the accounting start. It does
not verify §7's proposals, and it does not settle §5.1's substitution question.

---

## 12. Filing

Committed on the isolated branch `lane/cause3-voi-20260906` together with
`FINDING-20260906-cause3-scan-execution-composition.md`, which carries §7's discoveries in their own
record. **Not merged, and not to be self-merged.** `MANIFEST-overrides.tsv` re-sorts on write, so a
one-row addition is verified with a sorted diff rather than by reading the diff stat.
