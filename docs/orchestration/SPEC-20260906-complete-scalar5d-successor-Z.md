# SPECIFICATION 2026-09-06 — the complete scalar-5D successor **Z**: scientific contract, cause
# dispositions, terminal criteria, dependency analysis, and a costed execution proposal
# **rev. 17 — round 2 of the `D1`–`D4` review. `min(achievable, acceptable)` is WITHDRAWN: it used a
# feasibility floor as an upper bound, which §3.6a had already forbidden. `B ≤ S` replaces it, the
# control is revised on three gaps, and the product it was priced against was `15×` too large.**

**CITABLE FOR:** §1's contract, §2's seven cause dispositions, §3's terminal criteria, §4's dependency
table, §5's cost arithmetic **with its stated uncertainty**, and §6's rulings with their authority.

**§3.7 AND §5.8 ARE PROPOSALS, NOT CRITERIA.** They are citable as *the packet put to Joseph* and as
*this lane's measurements*; they are **NOT** citable as an adopted statistic, an adopted denominator, an
adopted precision target, an adopted boundary, or an approved cost. §6.6 requires the four to be
approved **together**, and §6.7 lists what is still his to decide.

**NOT CITABLE FOR:** any construction, any authorization to construct, any implementation, any compute,
any grade on any leg, any discharge, any adoption, any count, any gate movement, any spend, any
`SCOREBOARD` cell, or any publication claim. **Gate 2 remains FAIL. Counts hold at CAND `1 of 7`,
QUOTED `0 of 7` — this record moves no count.** No scalar-5D covariance is adopted. `(cause 7, G)`
remains permanently OPEN under `R1`. Y remains cause-7-only and unconstructed under `R2`; **Z is not Y
renamed and nothing here widens Y**. PET remains diagnostic under `R6`. `R5`'s accounting start,
ceilings and stop date are preserved exactly. **`CRITERIA` §0's three-token vocabulary is NOT extended
— see §6.1.**

**Status: SPECIFICATION ONLY.** `RZ(iv)`: this *"authorizes no implementation, construction, compute,
grading, adoption, or publication change"*. **All seven of Z's prospective cells are unopened and
ungraded here**, and this document opens none.

**`BEN-381` DISQUALIFIES THIS LANE FROM GRADING THE LEGS THIS CONTRACT DEFINES.** It drafted them and it
re-measured the evidence they rest on. The grading lane must be one that took none of the deciding
measurements. That separation is `R2`'s pattern and it carries forward.

## 0.0o What changed in rev. 17

Rev. 16 was `23f9dad5`. **Round 2 of the contract review accepted rev. 16's threshold withdrawals,
persisted null operands, correlation limitation, conditional `D3` and generalized leg-set branches — and
found the REPLACEMENT `D4` proposal not yet passable.** Rev. 17 implements that round.

**⚠ PROVENANCE, STATED PRECISELY BECAUSE REV. 16'S LINE DOES NOT TRANSFER.** Rev. 16 records *"Joseph has
approved the findings"*, and for that round he did. **This round arrived relayed WITHOUT an approval
statement.** So rev. 17 separates two kinds of change: **corrections of this lane's own errors, which
need no approval and are made unconditionally**, and **dispositions, which are recorded as the
REVIEWER'S and remain pending.** Nothing below is adopted.

| # | rev. 16 said | rev. 17 does |
|---|---|---|
| 1 | the null's bound is `min(achievable, acceptable)` | **⚠ ACCEPTANCE-BLOCKING, AND WITHDRAWN.** An observed reproducibility floor is not an acceptance tolerance, and a minimum turns it into one mechanically. **Worse: §3.6a says the floor bounds `ε` from BELOW; `min` used it as an upper bound** — rev. 16 inverted a constraint written two sections earlier, while quoting the paragraph that states it. Replaced by **`B` (operating-error bound, with assumptions and confidence) and `S` (independently justified scientific cap), the precondition `B ≤ S`, and `ε` argued WITHIN `[B, S]`**. If `B > S` the finding is that **the execution envelope is not demonstrated adequate** — not a tolerance to adopt |
| 2 | the control: `8` invocations, two arms, `≈11.6` GPU task-h, *"the only route"* | **all four claims corrected.** *"Only route"* **withdrawn** — the review did not establish it, this lane asserted it; three routes are now named, and **pinning LightGBM's `num_threads`/`deterministic`/`force_row_wise` is Tier-2 code that could make `B` a design property rather than a measurement**. **Gap 1:** a within-envelope null does **not** measure a between-envelope shift — both arms can reproduce perfectly while their CVs differ; a cross-arm `r_cross` is required if portability is the claim, and rev. 16's own persistence requirement is what makes it available. **Gap 2:** `4` repeats had no justification; a coverage/confidence objective, the sampling assumptions and a **predeclared** estimator are required, and **two arms do not prevent tuning**. **And the subject engages §6.4** — a control on Z's own bank reads the bound off Z's nulls |
| 3 | the control costs `≈11.6` **GPU** task-h for *"`2` CV unfolds"* per invocation | **⚠ BOTH OPERANDS WRONG, AND THIS DOCUMENT HAD ALREADY RECORDED THE CORRECTION.** An invocation is a whole `do_combine` — bank load, slab load, three `10,694²` assemblies — not two unfolds; and the combine is a **CPU** job (`sbatch_uthrow_combine_5d_fast.sh:4`, `--constraint=cpu --cpus-per-task=16 --mem=90G --time=03:00:00`). §0.0's rev.-2 correction row 10 already says *"`--null` runs in the **CPU** combine step; the `43.5`-min basis is a **GPU** arm-3 per-task time."* **Rev. 16 priced a new row off exactly that basis.** Cost is now **UNPRICED**, with a `3n` CPU task-h reservation bound |
| 4 | the persistence costs `1.05` MB *"against a `≈41` GB product"* | **⚠ WRONG BY `15×`, and the right number was in this document's own digest table.** The **throw product** holds **three** `10,694²` `TH2D`s = `2.74` GB derived, against `2.668` GB **measured** at §5.9's `uthrow` row. `41` GB is the **45-component** band family (`13 V + 5 A + 27 R` × `0.915` GB = `41.17` GB) and G's `combined_source` (`41.44` GB measured) — **a different object, conflated.** The fraction moves `2.6e-5 → 3.9e-4`; **the conclusion is unchanged and the operand was still wrong** |
| 5 | §3.7d's correlation legs cost *"zero production"* and *"the cost is validator code"* | **corrected: no additional MEMBERS is not FREE.** Priced per member — `s_proj` and `s_corr` **seconds** with **zero incremental I/O** (the diagonal legs already materialize the matrix via `np.frombuffer`), `s_eig` **`≈1`–`3` min** and `≈1.8` GB, measured by timing `eigvalsh` at four sizes here and scaling by `n³`. At `N = 5`, `s_eig` alone is `5`–`15` min. **Tier 2 runtime, not `R5`** |
| 6 | *"erring in both directions at `12.5%` each"*, unqualified in every summary | **the sampling model now travels with the number.** `12.5%` is exact **for a value uniform in its decade and a change uniform on `[0, one display unit)`** — a synthetic model, not a statement about rounding comparisons generally. The full statement in §3.7b item 4A always carried it; the summaries did not |
| 7 | §3.7 *"This section completes them"*; receipts say the graded quantities *"did not move"* | **both corrected.** §3.7 completes neither criterion — it supplies no acceptance number. And **with a positive tolerance the claim is *"did not exceed their declared movement limits"***, never *"did not move"*; four sites fixed |
| 8 | `D2` framed as waiting on *"two numbers"* from Joseph | **corrected.** `D1` and `D2` need **justified tolerances and scope**, which is scientific work — not a number Joseph supplies |

**Nothing is adopted and nothing moved.** §§1–2's dispositions, §1.3a–d, §6.1–6.5, the four rulings and
the pin all stand. Counts, gates and cells are untouched.

## 0.0n What changed in rev. 16

Rev. 15 was `eff4c6c1`. **A contract review of `D1`–`D4` — which the earlier PASS did not cover — found
`D1`, `D2` and `D4` not ready for adoption as written and `D3` supportable conditionally. Joseph
approved the findings; rev. 16 implements them.** The assembly algebra and the existing rulings are
**not** reopened.

| # | rev. 15 proposed | rev. 16 does |
|---|---|---|
| 1 | `D1`: adopt `s_agg ≤ 0.0861%` and `s_med ≤ 0.0374%`, derived from macro formatting | **THRESHOLDS WITHDRAWN as acceptance criteria; statistics and direct normalization RETAINED.** Formatting does not establish how much sensitivity is scientifically acceptable — and the rule behind the numbers is **factually wrong**: half a display unit neither guarantees nor is required for an unchanged printed value, erring in **both** directions at **`12.5%`** each **under the stated synthetic model** — a value uniform in its decade and a change uniform on `[0, one display unit)` — derived exactly and checked on `200,000` pairs. **The rate belongs to that model, not to rounding comparisons in general; the failure in both directions does not.** If literal display invariance is wanted, **rounding equality** is exact and needs no `δ` |
| 2 | — | **NEW §3.7d: every proposed gate is BLIND TO CORRELATIONS.** `I₂` and `[[1,0.9],[0.9,1]]` give identical trace and identical per-bin statistics — both legs return **exactly `0.0`** — while the sd of their sum and difference move by **`+37.8%`** and **`−68.4%`**. **And it is live, not hypothetical:** `project_cov_nd.py:2-11` marginalizes the assembled covariance as `M C Mᵀ`, which is exactly the functional both legs miss. Three candidate legs are specified; **none is adopted** |
| 3 | `D2`: adopt option (i), the model-dependent third leg | **NOT ADOPTED.** *"A missing data release does not prevent specifying a scientifically motivated per-bin tolerance"* — rev. 7–15 answered a **formatting** question in the slot a **scientific** one belonged in. The distribution stays a **diagnostic** pending *"what movement, in what fraction of bins, and why"* |
| 4 | `D4`: adopt `ε = n_iters · n_rep · eps = 1.1873e-11` | **`ε` WITHHELD; normalizer RETAINED.** It is a **summation bound over a computation that is not a summation** — measured against `unified_throw_cov_5d.py:47-89`, the chain is LightGBM fitting, three **event-level** accumulations and five divisions, so **`n_rep` counts OUTPUT BINS while every accumulation runs over EVENTS**. Underneath: the module's own docstring calls the estimator *"**nearly** deterministic in `seed` alone"*, no thread or determinism flag is pinned, and G's measured null is **not zero** — a **reproducibility** question, not a rounding one |
| 5 | `D4`: `11b` reconstructs `‖x_cv‖` from the production ROOT's `hXSecND_flat` | **OPERAND CORRECTED.** The numerator compares two **internally** re-unfolded CVs; a separately produced denominator **presumes the determinism the null tests**, and `adopt_unified_5d.py:116-121` checks **cardinality only**. **Remedy: persist `x_cv`, `x_cv2` and the predicate — `1.05` MB against the throw product** (⚠ rev. 17: **`2.668` GB measured**, not the `≈41` GB rev. 16 wrote — see §0.0o row 4). `11b` restated, **`11c`** added as a conditional cross-check |
| 6 | `D3`: the diagonal, **unconditionally**, because the launchers implement it | **CONDITIONAL YES to a small diagonal diagnostic.** An implementation is not a justification. **No grid is required.** And **`N = 5` is a planning proposal, not demonstrated capacity** — `219.6` GPU / `346.1` CPU task-hours before campaign costs and contingencies |
| 7 | branch table hardcoded to two legs | **RESTATED OVER A DECLARED LEG SET `L`** (§3.7b item 5). Rev. 7–15's MET branch would have **ignored any third leg** — values right, scope wrong. Fixed before a third leg exists |
| 8 | *"a sample standard deviation is inadmissible"*; *"if it entered the budget, quadrature would become correct"* | **both withdrawn** as the review's nonblocking corrections. A finite declared population does not make SD inadmissible — this packet itself uses a finite-set covariance; **the maximum is right because the CLAIM is universally quantified**. And **budget adoption alone would not establish independence**, so quadrature's burden does not lift |

**What this costs: nothing, and it removes one Tier-3 prerequisite.** Every remedy above is validator or
writer code (Tier 2) or a scope statement. `PM-6`'s bounded read is **no longer needed for `D4`**. The
one new compute item is the **determinism control — `≈11.6` GPU task-h, returned as a bounded proposal
and NOT run** (§3.7a). **⚠ SUPERSEDED IN REV. 17 AND LEFT IN PLACE: that price is withdrawn** (wrong
operation, wrong partition — §0.0o row 3), the control is revised on three gaps, and it is no longer the
only route.

**Nothing is adopted and nothing moved.** §§1–2's dispositions, §1.3a–d, §6.1–6.5, the four rulings and
the pin all stand. Counts, gates and cells are untouched.

## 0.0m What changed in rev. 15

Rev. 14 was `55e1ebcb`. **Three changes on instruction, and no general rewrite.**

| # | rev. 14 left | rev. 15 does |
|---|---|---|
| 1 | one readiness list answering *"ready for an implementation authorization?"*, which named **unwritten code** and **pre-launch reviews** as prerequisites | **⚠ CIRCULAR, and not fixable by editing the list.** An implementation authorization **is** permission to write that code; a pre-launch review gates a **launch**. §6.7 now separates **specification acceptance**, **implementation authorization** and **production authorization**, each with its own prerequisites. **Consequence: most of Z's code is authorizable today at zero compute** — only the null's `ε` and the cause-3 acceptance code wait, and each on its own decision |
| 2 | `D1`–`D5` framed but scattered across §3.7, §5 and §6.7 | **new §6.8, a decision sheet** — one row per decision, five fields each (recommended choice, why, claim supported, cost, remaining uncertainty), **pointing at the existing packets and proposing nothing new** |
| 3 | the meter repair *"expected within days"*; `D5` open; the waker accruing at *"≈`0.05`–`0.07`/day"* | **new §5.6b.** The repair **landed** at `72bcd2f6` on `main` (**not an ancestor of this tip**): attempts are summed, `sacct -X -D`, an attempt is `(JobID, Start)`, schema `2`, v1 receipts refused. **`D5` is RESOLVED** in the direction §5.9 flagged. **§7 item 19's first remedy is TAKEN**, its second **declined and referred to Joseph**. And the cadence figure was **wrong by an order of magnitude** — `≈0.65`–`0.69`/day, `≈28`–`29` task-hours by the stop. **`N` is `4`–`5` under all four readings; re-derived, not assumed** |

**Nothing is adopted and nothing moved.** §§1–5's measurements, §3.7's two packets, the four rulings
and the pin all stand. **A recommendation in §6.8 is not an adoption.**

## 0.0l What changed in rev. 14

Rev. 13 was `a95a6862`. **One correction, and it is the same failure rev. 13 catalogued, committed by
rev. 13 itself.**

| # | rev. 13 left | rev. 14 does |
|---|---|---|
| 1 | *"why `python3` and not `sed`"*, which reads as **any** `sed` normalizer being unsafe on macOS | **narrowed to what was measured.** `sed 's/^> //'` — the line as it was actually sent — returns **`1`, correct**, on BSD and GNU alike. Only the **`\?` generalization, which is this lane's**, returns `0`. **Over-scoping a real defect is a false alarm on a correct command** — the shape rev. 13 had just catalogued, one level up |
| 2 | the defect's owner described loosely | **named.** The working line was the preflight session's; the breaking `\?` was this lane's, **and this lane told that session the opposite before measuring.** A false accusation against a peer is not something a record should leave standing |
| 3 | *"`python3` because `sed` is unsafe"* | **`python3` for a better reason, measured:** the record holds **4 bare `>` lines**, so the obvious hardening of `s/^> //` is exactly the unportable construct. `python3` removes the class rather than one instance |

**Nothing else moved. The pin does not move** — the invariant still holds at `9c1230fa`, and §5.6a,
§5.8, §6.7's five decisions and §7's nineteen items are unchanged.

## 0.0k What changed in rev. 13

Rev. 12 was `3241833d`. **The check rev. 12 published is defective in the dangerous direction, and this
lane's own verification had been passing for a reason unrelated to the text.**

| # | rev. 12 left | rev. 13 does |
|---|---|---|
| 1 | §5.9's check greps each clause **contiguously** out of the raw file | **it produces a FALSE ABSENT.** The §2 limits clause wraps across a `> ` blockquote continuation, so a contiguous `grep -F` fails on the newline and the marker. **Measured here at `9c1230fa`: naive reports `1 of 7` ABSENT, normalized reports `0`.** The check now carries the normalization step |
| 2 | the check's failure direction was unstated | **stated, because it is the whole risk.** A false ABSENT on *this* invariant reads as *"the authorization no longer quotes Joseph's limits"* — the worst false alarm this document can raise, and one that would move the pin and start a hunt for a finding that does not exist |
| 3 | rev. 12 reported the invariant holding at two later tips | **and it held for a reason that was partly luck, which is recorded.** This lane's probe string had been **pre-truncated at exactly the wrap point** (`"…no automatic retries or"`), so it passed three tips in a row **without ever exercising the wrap**. A probe shortened to avoid a hazard does not test past it |
| 4 | — | **and the first draft of THIS revision published a broken remedy, caught by running it.** Its `sed 's/…>[[:space:]]\?//'` **does not strip the marker on macOS** — BSD basic regex does not read `\?` as optional — so the check returned `0` on a clause that is present, while GNU `sed` on Perlmutter would have accepted it. **Replaced by a `python3` normalizer, tested in both directions:** `1` on the wrapping clause, `0` on a fabricated absent one. **⚠ REV. 14 NARROWS THIS AND CORRECTS ITS OWNER — see §0.0l; the broken `\?` was this lane's generalization, not the line it generalized** |

**The pin does not move.** Re-measured at `9c1230fa`: the evidence directory diff against `1422569c` is
**empty**, all seven clauses are present under normalization, and the full diff is confined to the
authorization record. **Nothing else moved** — §5.6a, §5.8, §6.7's five decisions and §7's nineteen
items are unchanged.

## 0.0j What changed in rev. 12

Rev. 11 was `8d643fd8`. **A structural fix to one citation, and no new substance.**

**The problem, which is this document's own and recurring.** §5.9 pinned an off-branch citation at
`1422569c` and described the branch by **counting** its commits. That count has now been wrong twice in
three revisions — rev. 10 said *"six"* and named four; rev. 11 enumerated six and the branch is now at
**seven** — and it will keep going stale, because the cited branch is **actively advancing** while this
document is not its author. **Chasing a tip is churn, and a stale count in a section about provenance is
worse than churn.**

**The fix: state the pin as an INVARIANT and name the command that tests it**, rather than as a
snapshot that decays. §5.9 now says what the pin depends on — the evidence directory unchanged, and the
seven quoted clauses present — gives the two-line check, and records the result at the two later tips
this lane has actually run it against (`d7dd2f1c`, `6b439466`: **all seven present in both, evidence
directory untouched in both**). **A further commit on that branch does not require a revision here; it
requires re-running the check.**

**Nothing else moved.** §5.6a, §5.8, §6.7's five decisions and §7's nineteen items are unchanged.

## 0.0i What changed in rev. 11

Rev. 10 was `9b9708af`. **One measurement, taken in this checkout, that sharpens §5.6a's warning from
carelessness to procedure.**

| # | rev. 10 left | rev. 11 does |
|---|---|---|
| 1 | §5.6a: *"nobody should perform it by running the repaired tool once to see whether it works"* | **too weak, and the real hazard is the opposite of carelessness.** `R5-METER.md:12-16` is a copy-pasteable block that writes to **the gate's exact path**, introduced as *"atomically refresh the default receipt"*. Measured here: that path is **not gitignored** (`git check-ignore` exits 1) and **150 tracked `.json` files already sit in the same directory**. So the residual step is **one ordinary `git add`** — and the runbook's own closing disclaimer covers **authorization** while saying nothing about **admission**, which is the exact gap |
| 2 | §5.9 said *"six commits"* but named four | **all six enumerated**, including `7eccccdc` and `4c30c089`, whose subject line is what sent this lane to `R5-METER.md`. **The measurement is this lane's own, in this checkout** |

**No substance moved** and nothing is approved. §5.6a's three radius bounds, §5.8's figures, §5.9's
measurements and §6.7's five decisions are all unchanged.

## 0.0h What changed in rev. 10

Rev. 9 was `b043148d`. **No review finding, and no new operational measurement. One defect in this
document's citations, found while checking a supersession the preflight session reported.**

| # | rev. 9 left | rev. 10 does |
|---|---|---|
| 1 | §5.9's off-branch evidence described as **"COMMITTED"** | **⚠ COMMITTED AND UNPUSHED — measured here with a positive control.** `git ls-remote origin 'refs/heads/lane/*'` returns exactly two rows, `lane/cause3-voi-20260906` and `lane/y-cause7-spec-and-scope`; **`lane/pm-root-inspection-20260906` is absent.** So all four shas this document cites off-branch resolve **in this local repository only**. §5.9's provenance block now says so |
| 2 | the citation pinned at `1422569c` | **it STAYS at `1422569c`, and the reason is measured rather than assumed.** `d7dd2f1c` is now the branch tip; its diff touches **only** `AUTHORIZATION-20260906-pm-root-inspection.md`, and **all seven clauses this document quotes from that record are byte-identical across the two revisions** (substring-checked in both). Citing an unpushed *newer* sha would add nothing and resolve no better |

**Why this is worth a revision on its own.** *"Committed"* and *"pushed"* are different branch
properties, and this document has been treating the first as if it implied the second since rev. 8 —
in a §5.9 whose entire discipline is labelling where each claim came from. **A citation nobody else can
fetch is a definite description with a hexadecimal costume**, and §7 item 18 records what would resolve
it. **This lane does not push another lane's branch**, and would not push this one in particular: it
carries an authorization Joseph has not ruled on.

**No substance moved.** The measurements in §5.9, §5.9a–c, §5.6a, §5.8 and §7 are unchanged, and the
five decisions in §6.7 are unchanged.

## 0.0g What changed in rev. 9

Rev. 8 was `cbac8621`. **No review finding. A citation correction the preflight session asked for, and
one addition that belongs in a Z cost proposal rather than in an operational packet.**

| # | rev. 8 left | rev. 9 does |
|---|---|---|
| 1 | §5.9 cited the evidence at `cd41ff41` | **moved to `1422569c`, which supersedes it.** `cd41ff41`'s `README.md` carries **two known errors** — *"four earlier jobs"* in the waker lineage where there are **five, six with the live one**, and the array negative result stated **without its covering-search boundary**. **Verified here:** the diff is `README.md` + `DIGESTS.txt` only, and **only `README.md`'s digest moves** — both receipts, all four raw dumps and `R5-PREFLIGHT-EVIDENCE.md` are byte-identical. **Citing a revision with a known miscount is exactly what §5.9's RELAYED / RE-VERIFIED split exists to prevent** |
| 2 | §5.6 said admission is *"shut by choice"*, attributing the choice to the preflight session | **the attribution was wrong and understated the evidence.** It is shut by **Joseph's own instruction** — *"Label the existing R5 receipt explicitly as incomplete… do not present it as valid admission evidence"* — and committing it to the gate's path **is** that presentation |
| 3 | §4 row 3 treats the meter receipt as a missing prerequisite | **new §5.6a names what committing it DOES.** The gate is resolved **per queue, not per item**, so one commit removes a refusal for **every** compute item at once — for **24 hours**. **Running the repaired meter arms nothing; committing its output is the act** |
| 4 | §7 item 17 said the inspection *"is covered by"* an authorization | **sharpened.** Joseph authorized the **inspection**, quoted with its limits; what he has **not** ruled on is the **one-off accounting exception** that would let it be admitted, which he expressly reserved to himself |

**Nothing is approved, no ruling is reopened, the assembly algebra is unchanged, and the two lanes stay
separate** — `lane/pm-root-inspection-20260906` is **not** merged here, because it carries an
authorization Joseph has not yet ruled on and a Z revision must not lend that the look of a settled
record.

## 0.0f What changed in rev. 8

Rev. 7 was `641c6812`. **No review finding; a second read-only evidence packet from the
operational-preflight session, folded in with the same RELAYED / RE-VERIFIED HERE discipline.** Nothing
is approved, no ruling is reopened, and the assembly algebra is unchanged.

| # | rev. 7 left | rev. 8 does |
|---|---|---|
| 1 | §6.7 readiness item 5: *"a schedule nobody has checked"*, called **the one constraint no decision can relax** | **MEASURED and it goes the other way.** One complete seven-arm round spans **`37.5` h** end to end (376 tasks, `2026-08-30T21:29:20` → `2026-09-01T10:58:02`), so `4`–`5` rounds fit **inside either block** of the split window without straddling the outage. **Downgraded from a blocker to a caveat**, because it is **one realization at one week's queue depth** — §5.9c |
| 2 | the cause-4 second CV unfold: **UNRESOLVED**, needing a CPU-partition time | **bounded: `≤ 0.5764` CPU task-h.** `--null` runs inside `uthrow5d_combF` (`sbatch_uthrow_combine_5d_fast.sh:339`, `:2`), measured three times at `1,395`/`1,526`/`2,075` s on `shared_milan_ss11` — **CPU, never GPU**, which is exactly what rev. 2 got wrong |
| 3 | `D5` quoted `12.5903` CPU task-h as a fixed figure | **it moves**: `12.5903` at `08:59Z`, `12.606389` at `09:20Z`, growing `≈0.05`–`0.07`/day plus hangs. Every percentage taken against it now carries its **measurement instant** |
| 4 | §1.3: the mask and row-order digests *"must be read from G"*; §4 row 7 inferred G *"plausibly carries `hRowIndex5D`"* | **⚠ RE-VERIFIED HERE AND REFUTED. G's committed key inventory is 13 keys and contains NEITHER `hRowIndex5D` NOR `hXSecND_flat`** (`receipt_candidate_stamps_5d.json`, `A1_candidate_meancentered.all_keys`). **So `PM-4` as written has no referent** and §1.3's invariant is assertable only through the producer route — §1.3d |

**The rev. 7 inference was labelled an inference and it resolved against me.** That is the process
working, and it is the second time in two revisions that a `PM-*` row rested on something the tree
already answered (§5.9a was the first). **The difference is that this one was flagged; that one was
asserted.**

## 0.0e What changed in rev. 7

Rev. 6 was `f98cce8a`. **No review finding drove this revision** — it executes the three completion
items rev. 6 declared outstanding, on Joseph's instruction to complete the specification work only.
**Nothing here reopens the assembly algebra, and nothing here approves a criterion.**

| # | rev. 6 left | rev. 7 does |
|---|---|---|
| 1 | `(cause 3, Z)`'s joint-baseline statistic and acceptance rule named as a schema (§3.6b) | **§3.7b** gives the whole packet: member, population, two statistics, both denominators, the precision target, both boundaries, and the branch map. **The member turned out to be MEASURED, not a design choice** — exactly seven production launchers apply one shared `MNV_EST_SEED_OFFSET`, and the eighth refuses it |
| 2 | the null bound's normalizer, units and `ε` named as a schema (§3.6a) | **§3.7a** fixes the normalizer with both alternatives rejected on the record, derives `ε` from a precision control and checks it against three sensitivity channels, and adds the auditability requirement §3.6a did not anticipate |
| 3 | five cost rows with no spend estimate, three with no figure at all | **§5.8** re-casts the census into **production / artifact replay / conditional / contingency**, and **sizes two of the three unpriced build rows** from local timings on the real `10,694` dimension. One remains unresolved and two await the preflight session's `sacct` read |
| 4 | §6.6: the boundary-form question *"is not ready to be decided today"* | **§6.7** puts it, because the packet §6.6 required now exists. **Five decisions are named and none is taken here** |
| 5 | §5.6's meter gap, `PM-2`, and the assemblies' cost, all open | **§5.9** relays a read-only evidence packet from the **operational-preflight session** and marks every item RELAYED or RE-VERIFIED HERE. A genuine meter receipt now parses live `sacct` and is deliberately **uncommitted**; the assemblies gain a **measured upper bound** of `0.5231` CPU task-h; and a **7-day outage inside the `R5` window** cuts the usable schedule to `16 d 15 h` in two blocks |
| 6 | **⚠ two statements in rev. 1–6 were FALSE** — §1.1's *"no digest for `combined_source` is recorded anywhere in the tree"* and §4 row 5's *"using S's digest as G's is the substitution `PM-2` exists to prevent"* | **corrected in place, §5.9a.** G's **own** build receipt, in this checkout, in G's own directory, records the digest four days before S read the file. **An absence asserted without a covering search** — the same shape as rev. 1's missed decision record, and recorded as this lane's failure rather than repaired quietly |

**One consequence a reader must not miss:** under the direct relative-change model rev. 5 adopted as the
default, Z's cause-3 boundaries come out **48× and 73× tighter** than the narrow scan's predeclared
`4.15%` / `2.74%`. That is arithmetic, not a preference (§3.7b), and it is the substance of the decision
§6.7 puts to Joseph.

## 0.0d What changed in rev. 6

Rev. 5 was `4e43940b`. Review round 5 found **no new substantive contract finding** and confirmed that
rev. 5 resolved the acceptance-model correction and correctly defers the boundary approval. Two
non-blocking remnants, **both mine**:

| # | rev. 5 left | rev. 6 does | whose call |
|---|---|---|---|
| 1 | §7 item 3 still called the prior one that *"understates a Z member"* — the same directional claim §5.4 had just withdrawn | replaced with **"a prior measured on a different subject"**. **And the rev.-4 changelog row 5 carried it too**; that row is marked superseded in place rather than rewritten, per this tree's convention | **reviewer** |
| 2 | rev. 5's assembly-row edit inserted **literal newlines inside a Markdown table row**, splitting it across three physical lines and breaking the table | row rejoined onto one line. **A covering check over the whole file** — every line starting with `\|` must end with `\|` — found **exactly one** such row and **none remaining** after the repair, so this was the only instance across all six revisions | **reviewer** |

**Confirmed still outstanding, and they are now the whole of the remaining work:** the joint-baseline
statistic and acceptance rule, the normalized null bound and its justification, and complete costing.
**These prevent implementation readiness; none of them requires reopening the assembly algebra or the
settled rulings.**

## 0.0c What changed in rev. 5

Rev. 4 was `9e65d3ae`. Review round 4 found **no new assembly-algebra defect** and confirmed rev. 4's
substantive fixes. Two corrections remain, and **both are mine**: three withdrawn cost claims survived in
operative text, and one sentence overstated what the narrow scan established.

| # | rev. 4 said | rev. 5 says | whose call |
|---|---|---|---|
| 1a | the assembly row ends *"`< 4.0` is all it licenses"* | **removed** — it contradicted the row's own new `PROPOSED, UNVERIFIED` label. A request that was never exceeded measures nothing, and the 4-hour figure covered four operations of which only two are Z's | **reviewer** |
| 1b | §5.4: *"a Z member costs more per member"*; the prior *"understates a Z member"* | **withdrawn.** A prior measured on a **different subject** supports **no direction** — extra work pushes one way, reuse and execution conditions the other | **reviewer** |
| 1c | §7 item 5: *"four unpriced cost rows, which is why the subtotal is a floor"* | **replaced by §5.2's per-subtotal census** — five omitted from the spend estimate, three from the proposed reservation, two campaign-level items in neither. *"Floor"* withdrawn | **reviewer** |
| 2 | §3.6d: an independent contribution *"being added to the budget… is exactly what `C_seed` is for the narrow scan"* | **WRONG, and it contradicted this document's own §1.3a.** `PREDECLARE-20260901-cause3-mii` §5: *"It does not add `C_seed` to the uncertainty budget."* Quadrature is the **conditional model that motivated** the narrow scan's thresholds — not a demonstration of independence, and not budget inclusion. **It was never demonstrated even where it was used** | **reviewer** |
| 3 | §3.6d listed three boundary cases neutrally | **direct relative change is now the DEFAULT** for §6.3's assembled-covariance subject, per the reviewer's standing recommendation, with the burden of demonstration on any proposal to use quadrature | **reviewer, adopted** |
| 4 | §6.6's boundary-form item said only *what* is open | **adds HOW it must be put:** the statistic, denominator, precision target and boundary are approved **together**, never a formula detached from them. **So it is not ready to decide today** | **reviewer, adopted** |

**Confirmed by the reviewer as correctly declared and still outstanding:** the exact joint-baseline
statistic and acceptance rule, the normalized null bound and its justification, and complete costing.

## 0.0b What changed in rev. 4

Rev. 3 was `736fe39a`. Review round 3 returned one implementation-contract finding with two parts, two
production corrections and one non-blocking correction. **All are upheld, and all four are rev. 3
defects — including one where rev. 3's own reasoning was traced and found not to hold.** No ruling is
reopened and the assembly algebra is unchanged.

| # | rev. 3 said | rev. 4 says | whose call |
|---|---|---|---|
| 1 | §3.6a/§3.6b: derive the boundary with `S/U ≤ sqrt(2δ + δ²)` | **The quadrature model does not transfer, and rev. 3 ported it twice.** That formula assumes an **omitted independent contribution added in quadrature**; neither a difference of two CV vectors nor variation among assembled covariances satisfies that model. New **§3.6d** splits the derivation by what the statistic *is* relative to `U`, keeps `δ` as the part that genuinely transfers, and imposes the ordering rule: **statistic first, boundary second** — which rev. 3 inverted. A reproducibility floor is also demoted: it measures **achievable** repeatability, not **acceptable** error | **reviewer** |
| 1b | §3.6b item 2: cross-section-vector spread or covariance-entry spread, freely chosen | **§6.3 already fixed the subject as the ASSEMBLED covariance**, and rev. 3 reopened it. Vector spread cannot replace it without a demonstrated equivalence or the **substitution ruling §6.3 reserves** | **reviewer** |
| 1c | §3.6c: *"proposes no criterion change"* | **too categorical, withdrawn.** Completing §3.6 requires substantive scientific choices, and **if the surviving boundary is not the quadrature rule, that is itself a criterion question** for the `RZ(v)` carve-out. Surfaced, not decided | **reviewer** |
| 2 | run the `g ≡ 1` mutation *"separately for each variant"* to catch a reused `g^mean` | **It cannot, and the trace is short:** against a `g ≡ 1` producer, a reuse-faulty validator reconstructs the true `g^mean ≠ 1` and **rejects on both variants** — right answer, wrong reason, fault survives. §3.4 now carries a **distinct** `g^cv ← g^mean` mutation on operands where the two must differ (`v_blk=1`, `v_uni=4`, `mean_shift=1` → `g^mean = 2`, `g^cv = √5`), **and** requires the `g ≡ 1` fixture to make `g ≡ 1` wrong, since `g[i] = 1` is legitimate wherever `v_uni[i] ≤ v_blk[i]` | **reviewer** |
| 3 | historical costs are *"lower bounds of unknown tightness"*; the partial sum is *"a floor"* | **withdrawn, both.** Extra work does not prove a future run costs more — reuse and different execution conditions can move it down. They are **priors from a different subject**, and the extrapolations are conditional on those prior costs | **reviewer** |
| 4 | the 4-hour J28 request gives `< 4.0` for Z's assemblies | **a time limit bounds an ATTEMPT, not a completion.** Relabelled **PROPOSED, UNVERIFIED**, as is the combine's `1.0` | **reviewer** |
| 5 | *"four required rows"* unpriced, with shifting membership | **enumerated per subtotal:** the spend estimate omits **five** rows (including the combine and assemblies, whose spend is *unmeasured*); the proposed reservation omits **three**; two campaign-level items are in neither | **reviewer** |

**Upheld from rev. 3:** the `g`-reconstruction requirement itself, the elapsed-time accounting fix, the S
correction and the `BEN-381` correction.

## 0.0a What changed in rev. 3

Rev. 2 was `e15eb475`. A second round of the same independent contract review returned two
implementation-blocking findings, three production findings and two non-blocking corrections. **All
seven were re-measured here and all seven are upheld. Four were rev. 2 defects, and one of those was
introduced BY rev. 2's own fix.**

| # | rev. 2 said | rev. 3 says | whose call |
|---|---|---|---|
| 1 | §1.3b's four new inflation gates | **They are jointly satisfiable by an UNINFLATED object.** `g ≡ 1` passes the closure identity (`0 == 0`), `g >= 1`, the zero-denominator rule and PSD. A **fifth gate** now requires the validator to **independently reconstruct `g^c` from the throw operands, per variant** — §1.3b. **This hole was introduced by rev. 2's own fix**, which is why it is recorded rather than patched | **reviewer** |
| 2 | §6.3/§6.4 rule the quantity and the form; §7 notes the rest is open | **Named as open is not enough — three outcome classes are not executable criteria.** New **§3.6** gives both a completion schema: the null's normalizer/units/`ε`-derivation/presence rule, and cause 3's member definition, statistic, two-leg normalization, the `S/U ≤ sqrt(2δ+δ²)` boundary derivation, and the three classes mapped onto the six branches. **No ruling is reopened** | **reviewer** |
| 3 | §5.2a: *"the metered cost is the wall request, not the runtime"* | **FALSE, and rev. 2 introduced it.** `R5` meters **`ElapsedRaw` — actual elapsed** (`r5_meter.py:49-58`, `:165-174`, `:277`). A job requesting 90 min and exiting at 48 charges `≈0.80`. The observed `3.00` was a **hold that stayed allocated to timeout**. §5.2 now carries **spend** and **reservation** as separate columns | **reviewer** |
| 4 | `73.0` / `≤118.0` for one build | **relabelled a PRICED SUBTOTAL, not an upper bound**, and four required rows are marked unpriced. The J28 line is narrowed to **the two assemblies only** (its rescale is J28-only; its throw combine **is arm 7**). The cause-4 jitter unfold is a **SECOND** unfold at `seed + 7`, distinct from `--null`'s same-seed one, so arm 7's headroom is not evidence about it | **reviewer** |
| 5 | `54.90`/`86.53` per member; the family is *"out of reach"* | **a historical seven-arm PRIOR** — *"understating a Z member"*, **which rev. 5 withdrew: see §0.0c row 1b; a prior measured on a different subject supports no direction.** The extrapolation bounds **the historical design**, not Z's — Z's has no design, therefore no cost, therefore no affordability verdict | **reviewer** |
| 6 | §1.4c: S lacks *"§1.3a's entire vertical term"* | **overstated, and contradicted by this lane's own partition measurement** — all 13 `VERT_BANDS` are inside S's 40 `retained_bands`. S has the **uninflated** components; it lacks **`D_Z` and the inflated term** | **reviewer** |
| 7 | §7: the cause-3 design is *"not this lane's"* under `BEN-381` | **withdrawn.** `BEN-381` bars grading your own design, **not producing one**. Route the grading independently; do not manufacture a drafting prerequisite | **reviewer** |

**Upheld from rev. 2:** the cause-1 non-pair treatment, the cause-5 disposal, the seed-configurability
correction, the projection-guard correction, and the withdrawal of mandatory replay doubling.

## 0.0 What changed in rev. 2, so a reader of rev. 1 is not silently overtaken

Rev. 1 was `d2a515e0`. An independent contract review (detached checkout
`/private/tmp/z-contract-review.POIDb8`, read-only, no compute, no files edited) returned three
implementation-blocking findings, a set of cost corrections, and four non-blocking factual corrections.
**Every one was re-measured at this base before being applied. The reviewer is upheld on all of them,
and five were rev. 1 defects of mine.** Joseph then ruled on the decisions the review put to him (§6).

| # | rev. 1 said | rev. 2 says | whose call it was |
|---|---|---|---|
| 1 | §1.3: the unified-throw inflation is *"inside"* `C_syst(Z)` | **§1.3a now carries the explicit algebra** — `D_Z`, the 13-band vertical set `V`, its operands, zero-denominator handling and both centering variants, transferred from `adopt_unified_5d.py:1-27` | **reviewer.** *"Inside"* is not an implementation contract |
| 2 | §2.1: Z's cause-1 `M` *"must include all three excluded bands"* | **WITHDRAWN.** `Flux` (N=100), `2p2h` (N=3) and `__Normalization_flat` have **no ±pair**, so the one-sided counterfactual is undefined for them; the census carries them **unchanged in both totals**, where they cancel. Including them means **inventing endpoints** — a criterion extension, not arithmetic | **reviewer.** I read a definitional boundary as an omission |
| 3 | §2.6: the bidirectional coverage guard is *"an unrepaired instance of cause 6 in current code"* | **WITHDRAWN — stale.** Both projectors guard both directions at this base, and they differ **deliberately** in fail-closed-ness | **reviewer** |
| 4 | §2.6: *"Z must break that reuse"* of `C_stat`/`C_ML` | **WITHDRAWN as an inference.** The finalize launcher proves **reuse**, not **incompleteness**; fresh replica generation needs a stated scientific rationale, which this lane does not have | **reviewer** |
| 5 | §6.1 Route A: *"define a fourth token"* | **WITHDRAWN — already ruled against, in a record in this tree that I did not open.** `DECISION-20260902-joseph-rules-no-fourth-grade-token.md`. Route B was always the only route, and it is now ruled (§6.1) | **my miss**, surfaced by the review's cause-5 framing |
| 6 | §1.3: the Y closure *"would fail on every correct Z"* | softened — it is **not an identity for Z**, and other differences **could cancel**, so it may pass **accidentally**. That is worse than failing | **reviewer** |
| 7 | §§2.3/3.1: the fixed-seed null alternates *"exactly zero"* and *"≤ tol"* | reconciled, and the implemented tolerance is measured and found **vacuous on this scale** (§3.1a). Joseph has ruled a scale-relative bound (§6.4) | **reviewer** |
| 8 | §5: `71.5`/`113`, and a replay that doubles to `143`/`226` | **corrected throughout** — the P4 figure is a runtime prior, not R5 spend; assembly, both variants and the combine were missing; the replay doubling is withdrawn as mandatory | **reviewer** |
| 9 | §5.4: the cause-3 scope fork is *"≈4.5× on GPU"* | **WITHDRAWN — mixes three populations.** Replaced by the complete-member accounting | **reviewer** |
| 10 | §5.2: the cause-4 extra unfold at `0.73` **GPU** task-hours | **WITHDRAWN — my own population mix.** `--null` runs in the **CPU** combine step; the `43.5`-min basis is a **GPU** arm-3 per-task time. Re-treated in §5.2 | **found here**, applying the reviewer's own rule to a line the reviewer did not name |

**Upheld from rev. 1, re-verified by the reviewer independently:** the S marker correction (§1.4), the
cause-3 seed-split supersession (§2.3), and that Y's lateral closure is not Z's (§1.3c).

## 0.1 Authority and subject, bound by digest and re-measured at this base

| role | artifact | sha256, **recomputed at this base** |
|---|---|---|
| **the ruling this drafts against** | `docs/orchestration/DECISION-20260906-joseph-authorizes-z-specification-only.md` (`RZ`) | `304179df3905337d0ecd22af8a7416ed6aca5d7e050f89999667b57a6d251904` |
| **the prompt, subordinate to it** | `docs/orchestration/PROMPTS-20260906-z-specification-session.md` | `69b86539ed4c36ca1c527f17d943bac9f12081ffdd40e95bdaa9b9a814491688` |
| **controlling above both** | `docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` (`R1`–`R6`) | `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064` |
| **the grade vocabulary, ruled CLOSED — and rev. 1 missed it** | `docs/orchestration/DECISION-20260902-joseph-rules-no-fourth-grade-token.md` | `e59df9557e6ec1d21b845d7647c0038662c490713d8a43b2f72cd60bd34dc477` |
| **the question `RZ` answers** | `docs/orchestration/PACKET-20260905-full-scalar5d-successor-scope-question.md` | `fe46d64f04b7a34246275fc09b52b6c1db76d47756b9b6731f7c329b0fcd7de8` |
| **method reused, limits inherited** | `docs/orchestration/PREDECLARE-20260905-cause7-only-successor-Y.md` | `6bcb01581287d63010c9dee8d93e930f9da36eba2eacb1990c30a70d5c80f369` |
| **the `C`/`P`/`M`/`T` legs for cause 7** | `docs/orchestration/PREDECLARE-20260901-cause7-discharge-criteria.md` | `572c0825a926329dfaa5bfdfe37f8e277954def1b62f46c34a47ac12ab3f2c2b` |

**Base of every measurement in this file: `d2a515e0`** (rev. 1's tip), branch
`lane/y-cause7-spec-and-scope`. **Every `file:line` citation carries its symbol name beside it**, because
a line number in a growing file decays (`CRITERIA` §4.4; `SCOREBOARD` `POINTER 3`) — rev. 1 propagated
four decayed citations and corrected them before landing.

**One off-branch pair is cited and is NOT an ancestor of this tip:**
`VOI-20260906-cause3-mii-estimator-seed-scan.md` and
`FINDING-20260906-cause3-scan-execution-composition.md` at **`47494dbe`**, branch
`lane/cause3-voi-20260906` (ancestry measured: **not an ancestor**). They are cited for cause-3 cost
populations (§5.4), and they corroborate §2.3's seed-split finding by an independent route.

## 0.2 The rulings — authority, quoted rather than summarized

Joseph, 2026-09-06, on the contract review's recommendations, in his own turn to this lane:

> *"Can you correct these issues? Follow the recommendations for decisions from me."*

**Asked explicitly** — because in this repository an authorization is itself an evidence artifact, and
"RULED" is not a wording choice — whether the decisions the review framed as questions for him were to
be recorded as **his rulings** or left open in a carve-out, he selected: **record them as his rulings.**
That selection was made from an option list this lane wrote, and is recorded as such so a later reader
can weigh it; the sentence above is his own text.

**The recommendation text is the REVIEWER's; the adoption is HIS.** Both are recorded, and §6 quotes the
recommendations rather than paraphrasing them. This is `DECISION-20260902` §1's own pattern: *"The
framing under each ruling is this lane's and remains open to challenge on its merits; the adoption of
the conclusions is his."*

**What the rulings do NOT do:** they construct nothing, run nothing, grade no leg, discharge no cause,
move no count and no gate, and adopt nothing. **They do not extend `CRITERIA` §0's vocabulary.** They do
not retroactively regrade G.

## 0.3 What Z is, in one paragraph, so it is not read as something larger

Z is **one new scalar-5D covariance artifact on G's grid**, built at a new pinned revision, named under
`RZ(i)` as a **prospective** grading subject for **all seven** quarantine causes and a **possible**
adoption subject. Both hedges are Joseph's and both are load-bearing. Z **does not exist**: its output
paths, receipt schema and version, and producing revision are all undefined (§1.6). Z is **not** G
repaired — G's bytes are immutable and `RETAINED` under `R1`. Z is **not** Y widened — Y is cause-7-only
under `R2` and stays there. Z is **not** S promoted — §1.4. Z's seven cells are **new**; they overwrite,
reuse and retire nothing, and they may **never** be combined with G's or Y's grades, in either direction
(`RZ(iii)`). §3.4 states the limits without hedging.

---

# 1. THE SCIENTIFIC CONTRACT — deliverable `RZ(v)(a)`

## 1.1 Artifact identities — path plus digest, no definite descriptions

**`*.root` is `.gitignore`d, so no ROOT below is in this checkout**; ROOT digests are quoted from
committed receipts and labelled as such, never as this lane's own file reads.

| name | identity | role for Z | where measured |
|---|---|---|---|
| **G** | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root`, sha256 `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`, job `56720356`, **10,694** reported bins of the **65,856**-bin grid | **required, digest-bound `parent_candidate`**; the **`M`-leg comparison baseline for every one of Z's seven cells**. **NOT an operand of Z's construction** — §1.3 | `R1`; `PREDECLARE-20260901-cause7` §0 |
| **G.combined_source** | **⚠ CORRECTED IN REV. 7 — §5.9a.** `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root`, sha256 **`9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a`**, `41,436,632,945` B, mtime `2026-07-14T20:59:17Z` — recorded by **G's own build receipt**, `STAMPED_HASH_RECEIPT.slurm-56720356.json`. **Rev. 1–6 said *"name only; no digest is recorded anywhere in the tree"*. That was FALSE** — an absence asserted without a covering search, about a file in G's own directory in this checkout | the support-limited lateral family Z replaces five bands of, **and the file the 13 vertical per-band covariances are read from** (§1.3a) | `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json:28-30`, key `combined_source` |
| **G.uthrow_source** | `unified_throw_cov_5d_fluxfix_20260806_full160.root` | the throw ROOT G's inflation was derived from. **Z derives its own** — §1.3a | same receipt, `:32-34`, key `uthrow_source` |
| **G.centering** | `mean-centered` | Z's **primary** variant inherits it; the CV-centered variant is the F7 sibling, not a replacement | same receipt, `:24-26`, key `centering_convention` |
| **G total √Tr** | `5.269625166386846e-38` | the `M`-leg denominator for aggregate comparisons | `DECISION-20260831` §5 |
| **block-sum footing** | `4.357790406860002e-38` | byte-identical between G and X; the footing every arm is matched on. **G / blocksum = `1.2092`, which is the inflation's whole effect at trace level** | `DECISION-20260831` §5; ratio computed here |
| **S** | `nd-unfolding/active_universe_5d/standard/candidate/std_final5_candidate.root`, sha256 `950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263`, **42,326,607,877 B**, Slurm `57128458` step `.1`, 2026-08-16 | **component donor only**, each donated band **re-digested into Z's receipt**. **Supplies no inflation** — §1.4c | `p4_standard_validation.json`; `state/RECEIPT-20260816-p4-standard-stages456.json` |
| **S.component_manifest** | `nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json`, sha256 **`269232245870632884d6e589ac8d7aa9ba7fb4e07d0860e077cbd98fe6de04b5`** — **recomputed by this lane, MATCHING the `component_manifest_sha256` its sibling receipt records** | the bound inventory of what S may donate: 45 `all_syst_bands`, 40 `retained_bands`, 5 `replaced_lateral_bands`, per-band `component_content_hash` for all 45 | this lane |
| **S.support_family** | `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root`, sha256 `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` | **the same PATH G's receipt names as `combined_source`** — a candidate answer to `PM-2`, **but not an answer**: S read it 2026-08-16, G was built 2026-08-12, and nothing binds the two reads to the same bytes | `std_component_manifest.json` |
| **S.stat_cov / S.ml_cov** | `uq_cov_stat_5d.root:hCov_stat5d_reported` sha256 `6580016fa7136e6f98867707f4d48557350b26a91773d0c300be20113c2c6934`; `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported` sha256 `27b2e456f80e15d8a5c4da1bcd3b01a201b80385341af68614c85b6b7f8f5374` | Z's candidate `C_stat` and `C_ML` inputs. **Whether Z reuses or regenerates them is an open scientific question, not a settled requirement** — §2.6 | same manifest |
| **F** | `uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`, **266** bins, job `56431823` | **not evidence for Z**; `266 ≠ 10,694` | `OI-5`, `VL68`, `CRITERIA` §4.1 |
| **J** | the July `uq_universe_5d_covariance_combined_bkgaware_uthrow{,_cvcentered}.root` pair quoted by `values.tex` | **not evidence for Z**; wrong parent digest, every named stamp `ABSENT` | `DECISION-20260831` §1; `SCOREBOARD` §1 |
| **Y** | **specified, unconstructed.** Constructing it requires `D-Y-CONSTRUCT` (`R2(iv)`), which does not exist | **not a prerequisite for Z** — §4 row 1 | `PREDECLARE-20260905`; `R2(iv)` |
| **Z** | **PATHS, RECEIPT SCHEMA/VERSION, AND PRODUCING REVISION DO NOT EXIST.** §1.6 | the object specified here | this record |

## 1.2 The constants that must be imported rather than retyped

- `GRID_NBINS = 65856` — `nd-unfolding/p4_lib.py:22`, the `14×16×7×7×6` `(p_T, p_∥, E_avail, q3, W)` grid.
- `BANDS` — `p4_lib.py:18-19`, *"Canonical standard lateral inventory (exactly these; order fixed)"*:
  `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS`.
- `ENDPOINTS = (0, 1)`, `N_ENDPOINTS = len(BANDS) * len(ENDPOINTS)` — `p4_lib.py:20-21`, value `10`.
- `NONZERO_MIGRATION_BANDS = {BeamAngleX, BeamAngleY}`,
  `ZERO_MIGRATION_BANDS = {MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS}` — `p4_lib.py:64-65`.
- **`VERT_BANDS` — NEW IN REV. 2**, `nd-unfolding/adopt_unified_5d.py:42-43`: the **13** vertical bands
  the 5D unified throw covers (12 knob bands + `Flux`) — `2p2h`, `CCQEPauliSupViaKF`, `FrAbs_pi`,
  `FrElas_N`, `HighQ2`, `LowQ2`, `MaCCQE`, `MaRES`, `MFP_N`, `MvRES`, `Rvn2pi`, `Rvp2pi`, `Flux`.
  §1.3a cannot be written without it.
- **`F7_FLOOR_MULTIPLE = 2.0` — NEW IN REV. 2**, `nd-unfolding/uq_math.py:138`, with the predicate
  `f7_cv_centered_required` at `:160-169` and a **strict `>`** boundary. §2.2.

**Z's producing code must import every one of these, never restate them.** A retyped list is a second
implementation of a rule that already has one, and this repository already carries a **conflicting**
lateral inventory: `nd-unfolding/pet_lateral_correction.py:42-43` defines `LATERAL` with **six** entries,
adding `MinosEfficiency`. **The reported-bin count is a PREDICATE, not a literal:** `10,694` is the count
of bins with candidate CV > 0; select by predicate, then **assert** against G's, never hardcode.

## 1.3 Z's construction, stated as algebra rather than as prose

**Z holds the central value fixed.** All seven causes are *covariance construction* causes; the scalar
4D/5D central values are `VALIDATED`. So Z is built on **G's central value**, therefore on **G's reported
mask and row ordering**, as a **declared invariant with a guard**:

    mask_digest(Z) == mask_digest(G)        row_order_digest(Z) == row_order_digest(G)

Both must be **read from G** before construction (`PM-4`, §4) and re-asserted by Z's validator. A Z whose
mask differs makes every `M`-leg comparison in §2 ill-posed, because the two sides would be distributions
over different populations.

### 1.3d ⚠ THE INVARIANT STANDS; ITS EVIDENCE ROUTE DOES NOT — NEW IN REV. 8

**"Read from G" has no referent, and this is measured, not relayed.** `receipt_candidate_stamps_5d.json`
records G's complete key inventory under `A1_candidate_meancentered.all_keys` — **13 keys**, listed here
because a count is not an inventory:

    centering_convention, combined_source, fixed_seed_null_norm_checked,
    hCov_combined5d_total_uthrow, hInflation_g, joint_mean_shift_norm_checked,
    n_throws_checked, sqrt_tr_new, sqrt_tr_old, upstream_fixed_seed_null_norm,
    upstream_joint_mean_shift_norm, upstream_n_throws, uthrow_source

**Neither `hRowIndex5D` nor `hXSecND_flat` is among them**, and the same is true of
`A2_candidate_cvcentered` (13 keys) and the positive control. **So G stores no row-index array and no CV
vector**, and §1.3's two digests cannot be *read* from G at all.

**Rev. 2–7's §4 row 7 inferred the opposite and said so honestly** — *"`row_index_basis` warns that
'builds before [2026-08-10] lack it'; G is 2026-08-12, so it plausibly carries `hRowIndex5D`, but that is
an inference, not a read."* **The inference is now refuted.** What carries `hRowIndex5D` is the
**2026-08-16 rebuild**, which `RECEIPT-20260816-hrowindex4d-readback.json:83` records as having *"49 keys
including `hRowIndex5D`"* against *"the audited Aug-9 object [which] had 47 and no row-index array"*.
That is **S's** lineage, not G's — which is precisely why §1.1 lists `row_index_sha256` under **S** and
why §4 row 7 warned against borrowing it.

**What changes, and what does not.**

- **The invariant is UNCHANGED and still required.** `mask_digest(Z) == mask_digest(G)` and
  `row_order_digest(Z) == row_order_digest(G)` remain declared invariants and §3.3 condition 1 remains a
  reject condition. **A guard whose operand cannot be obtained is a guard that cannot fire**, which is
  this repository's catalogued failure shape — so the route must be fixed, not the requirement dropped.
- **The route becomes the PRODUCER, not the product.** G's reported mask is determined by the predicate
  `x_cv > 0` over the **production CV** (`hXSecND_flat`), and its row order by the C-order flatten of the
  `14×16×7×7×6` grid. Both are properties of the inputs G was built from, so the digests are
  **reconstructible** — from the production ROOT `sbatch_adopt_stamped_footing.sh:29` supplies, which
  **G's own hash receipt does not bind** (§5.9a records the four files it does bind, and this is not one).
- **This is the same object `11b` already points at** (§3.7a). One production ROOT, bound by path and
  digest in Z's receipt, closes the null's denominator **and** the mask/row-order route together.
- **`PM-4`'s PHRASING needs amending and that is not this lane's act.** *"G's mask digest and row-order
  digest, read from G"* names a read nobody can perform. Whoever owns §4's row should restate it as
  *"reconstructed from G's production-CV input, whose identity must first be bound"* — and the binding
  gap is the finding, not the reconstruction.

### 1.3a The composition, with the inflation given its explicit place

**This subsection is the reviewer's first implementation-blocking finding, discharged.** Rev. 1 said the
inflation was *"inside"* `C_syst(Z)` without saying which components change; that is not an
implementation contract. The construction below is **transferred from `adopt_unified_5d.py:1-27`**, which
already specifies it for G, and is restated here as Z's requirement.

Partition Z's systematic bands into three **disjoint** sets:

- **`V`** — the **13** vertical bands the unified throw covers, exactly `adopt_unified_5d.VERT_BANDS`.
- **`A`** — the **5** selection-complete active lateral bands, exactly `p4_lib.BANDS`.
- **`R`** — **every other systematic band** in the support family: the 4 weight-only detector-lateral
  bands (`MinosEfficiency`, `GEANT_Neutron`, `GEANT_Pion`, `GEANT_Proton`) plus the remaining
  non-vertical bands. `|V| + |A| + |R|` must equal the support family's band count, and the three sets
  must be **verified disjoint and exhaustive at build time**, not assumed.

**The partition is well-defined and the gate is satisfiable — measured, on the one committed 5D band
inventory that exists.** Against `std_component_manifest.json`'s 45 `all_syst_bands`:
**`|V| = 13`, `|A| = 5`, `|R| = 27`, summing to `45`**; `V` is a subset of the 40 `retained_bands`;
`V` and `A` are disjoint; the union is exactly `all_syst_bands`; and `R` holds all four weight-only
detector-lateral bands. **That measurement is against S's family read, not G's** — `R` is defined as
a complement, so it is only as good as the family list it complements, and `PM-5` (§4 row 8) is the
read that closes it on G's own `combined_source`.

Then, for each centering variant `c ∈ {mean-centered, cv-centered}`:

    C_Z^c  =  D_Z^c · ( Σ_{b∈V} C_b ) · D_Z^c   +   Σ_{b∈R} C_b   +   Σ_{b∈A} L_b   +   C_stat   +   C_ML

`D_Z^c = diag(g^c)` is the **per-bin unified/block sigma inflation**, *transferred* rather than swapped
in — for the reason `adopt_unified_5d.py:6-11` gives: with `n_throws ≪ bins`, `C_unified` is a low-rank
noisy estimate of the full matrix and *"swapping the whole matrix in directly breaks
positive-definiteness"*. The transfer is PSD by construction.

    v_uni^c[i] =  clip(diag(C_unified)[i], 0, ∞)          ( + mean_shift[i]^2  when c = cv-centered )
    v_blk[i]   =  clip(diag(C_blocksum)[i], 0, ∞)
    g^c[i]     =  sqrt( max( v_uni^c[i], v_blk[i] ) ) / sqrt( v_blk[i] )          >= 1
    g^c[i]     =  1                                        wherever  sqrt(v_blk[i]) == 0

**Operands, each named.** `C_unified` and `C_blocksum` are read **diagonals only** from **Z's own** throw
ROOT (`adopt_unified_5d.py:89-90`, via `_diag`); `mean_shift` is `hJointMeanShift` from the same file
(`:93-96`). `Σ_{b∈V} C_b` is read from **Z's own** `combined_source` as `hCov_universe5d_<band>` for each
of the 13 (`:129-141`) — **the same sweep estimator as the rest of `C_syst`**, which is exactly why the
transfer is PSD rather than a matrix substitution.

**Six properties a Z receipt must state and a Z validator must check:**

1. **Each vertical component appears exactly once**, inflated, inside `D_Z (Σ_V C_b) D_Z`. It does
   **not** also appear in `R`.
2. **The full throw covariance `C_unified` is NOT a budget block.** Only its **diagonal** is used, and
   only to form `g`. A Z that adds `C_unified` to the sum has double-counted the vertical systematics.
3. **`C_seed`, if measured (§2.3), is a DIAGNOSTIC and is NOT a budget block either** —
   `PREDECLARE-20260901-cause3-mii` §5's own limit, *"It does not add `C_seed` to the uncertainty
   budget"*, restated here because §1.3a is precisely where an extra block gets added by accident.
4. **`R` and `A` are never inflated.** The throw does not cover them (`adopt_unified_5d.py:19-20`), and
   `max()` never under-covers the block baseline.
5. **Zero denominator is `g = 1`, not a division.** `adopt_unified_5d.py:108-113` masks on `sb > 0`. A
   bin with zero block variance is left alone; it must not become `NaN`, `inf`, or be silently dropped.
6. **Both centering variants are produced, always, to distinct explicitly-passed `--out` paths.** F7
   requires the shift reported *either way* (§2.2). `adopt_unified_5d.py:79-80` **defaults** `--out` and
   opens it `RECREATE`, so a defaulted `--out` is a destructive-overwrite hazard — which is why
   `sbatch_j28_adopt_5d.sh:111,113` passes it explicitly, twice.

### 1.3b The identity set Z's writer and validator must EACH independently recompute

The existing standard-P4 gates verify a **block sum**. Z is an **inflated** object, so the gate set must
be **extended** — and the extension is the part that does not exist today.

| identity | tolerance | status at this base |
|---|---|---|
| `Σ active-5 == L_active(Z)` | rel `1e-9` | **exists** — `active_total_eq_sum5` |
| band set is exactly the support family's | exact set | **exists** — `band_set_completeness_vs_support_family` |
| exactly five active bands, ten ± endpoints | exact | **exists** — `exact_5_active_bands` |
| symmetry and PSD | exact / eigenvalue | **exists** — `symmetric_psd` |
| `C_syst^blocksum == Σ_V + Σ_R + Σ_A` (the **uninflated** sum) | rel `1e-9` | **exists** — `c_syst_recomputed_from_components` |
| `C_Z^blocksum == C_syst^blocksum + C_stat + C_ML` | rel `1e-9` | **exists** — `full_total_identity_recomputed` |
| **`V`, `R`, `A` pairwise disjoint AND exhaustive over the family** | exact set | **DOES NOT EXIST** |
| **`C_Z^c − C_Z^blocksum == (g^c_i g^c_j − 1) · (Σ_V C_b)_{ij}`** | rel `1e-9` | **DOES NOT EXIST.** This is the inflation's closure identity and the one gate that can catch a double-counted or mis-scoped vertical set |
| **`g^c >= 1` everywhere, finite, and `== 1` exactly where `v_blk == 0`** | exact | **DOES NOT EXIST** |
| **PSD of the INFLATED object**, not only of the block sum | eigenvalue | **partial** — `adopt_unified_5d.py:150-165` checks `ev[0] >= -1e-12·ev[-1]` on the adopted matrix, but outside the P4 gate list, so no receipt records it as a gate |
| **`g^c` INDEPENDENTLY RECONSTRUCTED from the throw operands and compared elementwise to the `g` the producer recorded — separately for EACH variant** | exact, or a stated float tolerance | **DOES NOT EXIST, and without it the four gates above are jointly satisfiable by an UNINFLATED object** |

**⚠ THE RECONSTRUCTION GATE IS NOT ONE MORE CHECK; IT IS WHAT MAKES THE OTHER FOUR CAPABLE OF
FAILING.** Rev. 2's first gate set was reviewed and found jointly vacuous in the direction that matters.
**Set `g^c ≡ 1` everywhere and emit the block sum**, and every one of them passes:

| gate | value at `g ≡ 1` | verdict |
|---|---|---|
| `C_Z^c − C_Z^blocksum == (g_i g_j − 1)(Σ_V C_b)_{ij}` | `0 == 0` | **passes, trivially** |
| `g^c >= 1` everywhere, finite | `1 >= 1` | **passes** |
| `g^c == 1` exactly where `v_blk == 0` | true everywhere, so true there | **passes** |
| PSD of the inflated object | it is the block sum, already PSD | **passes** |

**So a Z that silently discarded the whole inflation would clear the gate set and ship as an inflated
object.** That is this repository's own catalogued shape — a guard whose green state is reachable
without the work being done (`CORPUS-20260811-gates-that-cannot-fail-sweep.md`) — and it was introduced
by rev. 2's own new gates, which is why it is recorded here rather than quietly patched.

**The requirement, stated so it cannot be satisfied by reading a recorded value back:** the validator
recomputes `g^c` **from the throw operands themselves** — `diag(C_unified)`, `diag(C_blocksum)`, and
`hJointMeanShift` for the CV-centered variant — by §1.3a's formula, **for each variant separately**, and
compares elementwise against the `g^c` the producer wrote. Reading the producer's `hInflation_g` and
checking it against itself is not this gate. **Both variants must be reconstructed independently**,
because `g^mean` and `g^cv` differ only through the `+ mean_shift²` term and a validator that reconstructs
one and reuses it for the other cannot detect a dropped shift — which is cause 2's defect arriving inside
cause 3's machinery.

`1e-9` is the existing standard-P4 relative closure tolerance (`p4_build_components.py:140-171`). **It is
a numerical closure tolerance and may not be reported as an `M`-leg materiality threshold**
(`PREDECLARE-20260901-cause7` §1 `C`(4)).

### 1.3c The place Y's method does NOT carry over

Y's closure is `C_Y − C_G == L_active − L_support`, exact because Y changes **only** the lateral block and
`C_G` is literally the minuend. **Z has no such identity**: Z rebuilds the inflation, the centering, and
possibly the statistical block, so `C_Z − C_G` is a sum of independent differences.

**Rev. 1 said such an assertion "would fail on every correct Z". That is too strong and is withdrawn:**
the other differences **could cancel**, so the assertion might **pass**. That is the worse case, because
a check that can pass for the wrong reason certifies nothing. The requirement is §1.3b's component
identities, and **`C_Z − C_G` is a reported difference, never a closure condition** — see §2.7 for the
matching distinction on cause 7's magnitude.

## 1.4 S is not Z's starting point — and the ground usually given for that does not reproduce

**The conclusion holds. One of the two reasons routinely given for it is stale.** The reviewer confirms
this correction reproduces independently, and adds the right qualification: *"This removes the claimed
marker refusal; it does not establish scientific adoptability or supply inflation."*

### 1.4a The measurement

`PROMPTS-20260906` §2(a), `PACKET-20260905` §6.2, `PREDECLARE-20260905` §1 and `SCOREBOARD` §5 all state
that S *"carries `publication_gate_rejects_this: true`"* and that *"`p4_adopt_standard.py` refuses it
outright"*. Measured against the committed candidate packet:

| claim | measurement | verdict |
|---|---|---|
| S's component manifest carries the marker `true` | `std_component_manifest.json` — key **absent** | **does not reproduce** |
| S's validation receipt carries the marker `true` | `p4_standard_validation.json` — key **absent**; records `"result": "PASS"` over **11 gates**, `full_total_identity_relerr = 4.6027194117555535e-14` | **does not reproduce** |
| S's projection manifest carries the marker | `std_proj4d_candidate_projmanifest.json` — `publication_gate_rejects_this: **false**`, `non_adoptable_marker_key_present_in_parent: **false**` | **carries the marker FALSE** |
| the `true` marker exists somewhere | `nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json:324` — the **FPS purity-control** manifest | **a different artifact** |
| `fps_build_control_manifest.py:202-204` *dies* if the gate fails to reject | true; its operand is *"the purity-control manifest"* (`die_evidence_blocked`, `:203`) | **true of FPS, not of S** |
| `p4_adopt_standard.py` refuses S outright | `result == "PASS"` ✓; `gates` a list ✓; `band_set_completeness_vs_support_family in gates` ✓; `component_manifest_sha256` present and **recomputed to match** ✓; `require_adoptable(prov)` passes on an absent key; `val.get(NON_ADOPTABLE_KEY)` absent | **does not reproduce as stated** |

### 1.4b Why the claim exists, dated — it was true, of a different S

The pre-2026-08-16 candidate was built by allocation `56636802` *"explicitly non-adoptable
(`P4_NON_ADOPTABLE=1`, verifier token unset)"* (`P4_STANDARD_STATUS.md:77`) — the switch
`p4_lib.stamp_non_adoptable` (`p4_lib.py:677-690`) reads. Its digest was `602bbcf2…`. Run `57128458`
rewrote it to `950f8cb1…` **under the repair-11 PASS token**. **`VALIDATION_LEDGER` `VL68` already
carries the 2026-08-22 correction** — *"The cause-7 verdict in this cell is UNCHANGED and still correct:
built is not adopted. `p4_adopt_standard.py` has never run… Only the *build* clause was stale."* The
broader conclusion is `VL68`'s, not this lane's.

### 1.4c The durable ground — three reasons, the third new in rev. 2

1. **S is a block-sum object; G is an inflated one, and Z must be inflated.** S's receipt records
   `sqrt_tr_full = 4.3576e-38` against the block-sum footing `4.357790406860002e-38` — ratio **`0.99996`**.
   G's total is `5.269625166386846e-38`, **`1.2092×`** the block sum. Substituting S's total for G's is
   forbidden outright by `PREDECLARE-20260901-cause7` §1 `C`(3).
2. **S addresses one cause of seven.** `replaced_lateral_bands` is exactly `p4_lib.BANDS`;
   `retained_bands` is the other 40, read from the same support family. That is **cause 7 and nothing
   else**.
3. **NEW — S cannot donate the component Z most needs.** `D_Z` is derived from **Z's own throw ROOT's**
   `C_unified`/`C_blocksum` diagonals, and **S has no throw arm**. **Stated precisely, because rev. 2
   overstated it and this lane's own partition measurement contradicts the overstatement:** S *does*
   contain the **uninflated** vertical components — all 13 `VERT_BANDS` are inside its 40
   `retained_bands`, verified above. What S lacks is **`D_Z` itself and therefore the inflated term**.
   So S can donate a vertical band's *content*; it cannot donate the operator that makes Z's vertical
   block what G's is, and no re-digesting of S's components supplies one.

**S may donate**, and this is real reusable evidence: the 45 per-band `component_content_hash` values,
`reported_mask_hash = 74374b1af0795c3eb077c9ef0ee6ef3cfa4d7b7b3df63bd4f392d7db80eb136a`,
`row_index_sha256 = 61746918371fb9a99f69b8e657f98e0796ae9efd63e21a89346fbb620a596f08` under key
`hRowIndex5D`, and the five active-band traces. **Every donated component is re-digested into Z's receipt
at Z's build time.**

## 1.5 Receipt schema — written LAST, identifying the exact Z it describes

Versioned, per `PREDECLARE-20260901-cause7` §1 `P`, extended from Y's §3 to seven causes and to §1.3a:

- **Z:** path, byte size, sha256, reported-bin count, **mask digest**, **row-order digest**, producing
  job/run **and step**, and **which centering variant this file is**.
- **Parent:** G's exact path and **full** sha256 as `parent_candidate`; G's committed `combined_source`
  **name and the digest of the support-family ROOT actually read** (`PM-2`).
- **Code identity:** pinned producing revision **plus executable import-closure digests, bound to the
  run**. *A clean implementation at an unpinned revision is not `C`.*
- **The inflation block — new in rev. 2:** `V`/`R`/`A` membership as read from the imported constants;
  the disjointness and exhaustiveness results; the throw ROOT's path and digest; `g` as a histogram plus
  `min`, `median`, `max`, the count of bins `> 1`, and **the count of bins where `v_blk == 0` and `g` was
  pinned to 1**; the measured residual of §1.3b's inflation closure identity; **the elementwise
  result of the independent `g^c` reconstruction, reported separately for each variant, with the
  operand digests it was rebuilt from**; and `sqrt_tr` before and after inflation.
- **Per cause, a named block** carrying its own operands — cause 1's counterfactual **with its scope
  statement** (§2.1); cause 2's F7 operands **with `k` and its source**; cause 3's `estimator_seed` and
  `draw_seed` at **both** legs; cause 4's re-added print value, seed and both operand digests; cause 5's
  path trace; cause 6's projection operator digest and **both** coverage censuses; cause 7's five removed
  support keys, ten endpoints with **migration censuses and declared policies**, and five active digests.
- **Closure:** measured operands and residuals for **every** identity in §1.3b; symmetry; PSD **of the
  inflated object**.
- **The negative statement, verbatim:** *F's 266-bin receipt, S's whole-file PASS, and any receipt about
  G are not evidence that Z was produced. Where S supplies a component, that component's digest is
  rebound into this receipt at Z's build time.*

- **⚠ THE NULL BLOCK — NEW IN REV. 16, and it is a WRITER change, not just a receipt field.** Z's
  throw product persists **`x_cv`, `x_cv2` and the support predicate's result** on the full grid
  (`1.05` MB against a **`2.668` GB** product — ⚠ corrected in rev. 17 from `≈41` GB, which is a
  different object), and the receipt records `n_rep` **as recomputed by the
  validator from the persisted predicate**, `‖x_cv‖`, `‖x_cv2 − x_cv‖`, the reconstructed `r_null`, and
  the per-bin diagnostic with its argmax bin. Where an external cross-check against a named production
  ROOT is reported at all, it carries that ROOT's **path, sha256 and key** and the **elementwise**
  identity result — or the literal **`UNRESOLVED`** (§3.3 `11b`, `11c`).
- **⚠ THE CAUSE-3 BLOCK GAINS ITS LEG SET — NEW IN REV. 16.** The declared binding leg set **`L`**, each
  leg's **class** (`aggregate` or `per-bin`), each `s_ℓ`, each `δ_ℓ`, and — on any unfavourable outcome
  — **the exact failing subset `F` by name**, from which the `R4` branch label is derived rather than
  reported in its place (§3.7b item 5). Where `L` contains no correlation-sensitive leg, the receipt
  carries §3.7d's scope statement **verbatim**.

**The two fields whose absence has cost this campaign before:** the per-endpoint migration census and
declared policy, and the import-closure digest bound to the run. A declared-zero band measuring nonzero
migration, **or the reverse**, must **abort**.

## 1.6 What does not exist yet

1. **Z's output paths** — one per centering variant, under a Z-specific directory, never a rewrite of
   G's or S's path. **`p4_build_components.py:180` opens `--out` with `RECREATE`** and
   `adopt_unified_5d.py:79-80` **defaults** `--out`, so Z's paths must not collide with any existing
   candidate and `--out` must always be passed explicitly.
2. **Z's receipt schema and version** — §1.5's field set, versioned, written **last**.
3. **Z's producing revision** — pinned commit plus import-closure digests bound to the run.
4. **Z's validator** — the standard-P4 validator covers the block-sum identities; **§1.3b's five
   inflation gates do not exist**, and without the fifth — the independent `g^c` reconstruction — the
   other four are satisfied by an uninflated object. The six non-cause-7 causes have no Z-side validator
   at all.
5. **Z's test-contract fixtures** — §3.3.

---

# 2. CAUSE DISPOSITIONS — all seven, each argued, none inherited — deliverable `RZ(v)(b)`

**The governing rule:** discharge is a property of a **(cause × artifact)** pair (`CRITERIA` §0). **Z
inherits nothing from G.** Every cell below is `OPEN` for Z by construction, including the two settled
for G. Each row states **what Z would have to do differently, and what evidence would show it** — not a
prediction and not a grade. Leg states quoted for G are read from `SCOREBOARD-20260817`'s CAND column and
its `POINTER 4`; where a later record supersedes the board, that record is named.

## 2.1 Cause 1 — one-sided endpoint interpolation

**G:** `C` MET, `P` MET, **`M` MEASURED, not MET**, `T` MET. Cause 1 does not close, ruled 2026-09-01
(`DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` `RULING 1`): the `+3.1%`/`+5.9%` √Tr difference
with a `1.7–2.0×` median per-band ratio is **material enough to need its own statement in the note**.

**RULED for Z, 2026-09-06 (§6.2): measure-and-disclose closure, irrespective of magnitude, once
independently verified.**

**What Z must do differently: nothing in the construction.** Every `C_syst` builder on G's path already
forms band covariances via `uq_math.mat_covariance` over both endpoints. The ruled obstruction was never
the construction; it was `M`'s materiality plus the disclosure obligation.

**⚠ REV. 1 WAS WRONG ABOUT THE THREE NON-PAIR BANDS, AND THE CORRECTION IS THE POINT OF THIS ROW.**
Rev. 1 said Z's cause-1 `M` *"must include all three excluded bands"*, reading `RULING 1`'s third ground
as an omission to be filled. Measured in the producing receipt,
`nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json`:

> `:744` `"counterfactual_scope": "N==2 pair bands only. Flux (N=100), 2p2h (N=3) and
> __Normalization_flat are carried UNCHANGED in both totals."`
> `:738` `"scope_note": "Totals differ ONLY through the pair bands; Flux, 2p2h and the norm band are
> byte-identical contributions in both."`
> `:753` `"excluded_reason": "N != 2, so there is no '+1 sigma endpoint'; carried unchanged in both
> totals"`

**So they are not missing from the measurement — they are outside its domain, and they cancel.** The
one-sided form is `diag(outer(x_ep − CV))`, which requires a ±pair; for `N ≠ 2` there is no
`+1σ endpoint` to take. **Constructing a counterfactual for them means inventing endpoints that do not
exist, which is a criterion EXTENSION and not arithmetic** — and it would be a proposal for §6, not a
requirement of this contract. **Rev. 1's requirement is withdrawn.**

**What Z's cause-1 `M` must do, as ruled:**

1. **Both one-sided choices, for the actual ± pairs.** The receipt already computes them —
   `:746` `"one_sided": "... computed for BOTH ep in {0,1}"` — and reports
   `ratio_one_sided_ep0_over_as_built` and `ratio_one_sided_ep1_over_as_built` per band. Z reports both,
   per band, on Z's own bank.
2. **Off-diagonal effects.** The census is `"diagonal_only": true`, which is exactly `RULING 1`'s third
   ground. Z compares off-diagonal structure as well as diagonals.
3. **Denominator qualifications stated.** Every ratio names its denominator and the population it is
   over; a per-band ratio and a √Tr ratio are different objects and must not share a sentence without
   both denominators named.
4. **The non-pair bands accounted for EXPLICITLY, without inventing endpoints.** Z's receipt states, for
   `Flux` (N=100), `2p2h` (N=3) and `__Normalization_flat`, that they are carried unchanged in both
   totals, with their band count `N` and their contribution to each total — so a reader can see they
   cancel rather than infer it.
5. **The sign report.** `RULING 1`'s second ground: the effect **changes sign** — `MaCCQE` ep0 `0.6377`
   and `MaRES` ep1 `0.6111` are *understated*. Z reports the ratio distribution **with its below-1 tail**,
   because a consumer assuming conservatism is wrong on those bands.
6. **Independent verification** of the measurement, by a lane `BEN-381` does not disqualify. This is the
   ruling's own condition and it is what "measure-and-disclose" rests on.

**And the disclosure.** `RULING 1` created a note obligation for cause 1. Under §6.2 that obligation is
part of Z's closure condition, **and writing the note text remains a publication act outside `RZ(iv)`** —
so `(cause 1, Z)` cannot be *graded* closed until the disclosure exists, and this specification does not
write it.

**Evidence that would show it:** Z's own bank, built both ways, per band, distribution plus off-diagonal,
with `uq_math.require_truth_ratio_bank` PASS and the scope statement in Z's receipt.

## 2.2 Cause 2 — CV centering

**G:** all four legs MET, and it is the **one** cause discharged — *"`1 of 7` (cause 2, Joseph,
2026-08-12, **candidate only**)"*. **That discharge was BY DECISION**, which the board's counts table
records separately from *"causes with four METs"*, which is **`0`**. That precedent matters for §6.1.

**What Z must do differently: nothing in the construction, everything in the evidence.** `RZ(iii)`
applies with full force: **Z cannot borrow G's cause-2 discharge.** `P` is a statement about *which
bytes*, and Z's bytes are new.

**Cheapest of the seven, for a stated reason: cause 2's `M` criterion is predeclared, mechanical, and —
new in rev. 2 — its factor is PINNED IN CODE.** The reviewer's directive is *"Pin F7's existing factor
rather than leave ≫ executable by interpretation"*, and the factor exists:

- `uq_math.F7_FLOOR_MULTIPLE = 2.0` (`nd-unfolding/uq_math.py:138`);
- `mean_shift_sampling_floor(sqrt_trace, n_throws) = sqrt_trace / sqrt(n_throws)` (`:141-149`);
- `f7_cv_centered_required(...)` returns `mean_shift_over_floor(...) > k` — a **strict** inequality
  (`:160-169`), with the boundary pinned by a test asserting `2.0 × floor` is False and
  `2.000001 × floor` is True (`tests/test_uq_remediation.py:407-413`).

**Z's contract therefore says `k = uq_math.F7_FLOOR_MULTIPLE`, imported and not retyped, strict `>`.**
The module's own comment is preserved as part of the contract: `2.0` is *"a CODIFICATION, NOT A REPO
DECISION"*, chosen so a shift at `1.0×` is unambiguously below and the measured `4.69×` unambiguously
above, and *"deliberately not tuned to sit just under 4.69x"*. On G it measured `4.83×` after the flux
correction.

**And the rule's other half, which the predicate's own docstring insists on:** `False` does **not** mean
the shift may be dropped. F7 requires the shift **reported either way**; `False` only means the
CV-centered variant is not *additionally mandatory*. §1.3a property 6 requires both variants regardless,
so for Z the predicate's value is **reported**, not branched on.

**One discrepancy this lane will not resolve.** `CRITERIA` §2 cause 2 states `T` is *"Absent, and this is
cause 2's only real gap"*; `SCOREBOARD` grades cause 2's `T` **MET** (`f7_cv_centered_required`, N3/N4).
The two control documents disagree; the board is later and is the board. Reconciling them is a third
document's act.

**Evidence that would show it:** Z's own `hJointMeanShift` and `joint_mean_shift_norm`; both centering
variants as separate files with `--out` passed explicitly; the floor with `N` stated; `k` and its source;
and the F7 predicate's value recomputed on Z's ensemble.

## 2.3 Cause 3 — varying estimator seeds

**G:** `C` PARTIAL (*"INAPPLICABLE to the dominant block"*), `P-i` PARTIAL, `P-ii` OPEN **with its
premise measured FALSE at HEAD** (`POINTER 4`), **`M` OPEN and "NOT CURRENTLY MEASURABLE"**, `T` MET.

**RULED for Z, 2026-09-06 (§6.3): the quantity is the JOINT-BASELINE variation of the assembled
covariance; the narrow fixed-draw scan is DIAGNOSTIC for Z unless substitution is separately ruled; the
existing 46/50-member family is NOT assumed to be the necessary design; and favourable, unfavourable and
inconclusive outcomes are specified BEFORE measurement.**

**⚠ THE BOARD'S §2b IS SUPERSEDED AT THIS BASE.** `SCOREBOARD` §2b (2026-08-17) records that `M(ii)`
*"cannot be configured on either leg"*. **Both halves are false at `d2a515e0`:**

| §2b's finding | measured |
|---|---|
| sweep leg: seed is a literal, no flag, 14 `add_argument` | `sweep_bank_5d.py:358` **`--estimator-seed`**; `add_argument` count is **15**; `:344` comments *"This was the literal `seed=42`"*; `:309` writes `TParameter("estimator_seed")` |
| throw leg: one `--seed`, two roles, varying is unsatisfiable | `unified_throw_cov.py:630` **`--draw-seed`** and `:634` **`--estimator-seed`**, **both `required=True`**; `:269` `rng = np.random.default_rng(args.draw_seed + gj)` drives the draw while `args.estimator_seed` drives `_xsec_for_weights`; `:569-570` writes **both** keys |
| `do_combine` guards one seed | `:477-479` refuses a mixed **estimator** seed **and** `:483-485` refuses an incoherent **draw** seed |

**Landed `3dd5e66e`, 2026-08-18T01:16:55−04:00** (*"GATE 1 BUILT: `unified_throw_cov.py`'s dual-role
`--seed` is split into required `--draw-seed` and `--estimator-seed`"*), verified an ancestor of this
base — **one day after** §2b was written, so §2b was correct when written. Corroborated independently by
`VOI-20260906` §7.5 at the off-branch `47494dbe`.

**The reviewer's qualification is right and is adopted:** *"Configurable code does not repair historical
provenance or settle composite-scan scope."* The split makes the composite **buildable**; it settles
nothing about G's provenance and nothing about which quantity closes the leg.

**What Z must do differently.**

- **`C`:** extend the guard to the dominant block. §2b's surviving finding is that *"the single-seed
  property of the dominant block holds by hardcoding and is checked by nothing"*. `sweep_bank_5d.py` now
  **stamps** its seed, which is `P`; **refusing** a mixed-seed `C_syst` slab is still new code.
- **`P`:** Z's receipt records the seed **value** at both legs. The write sites exist at this base
  (`sweep_bank_5d.py:309`; `analyze_universes_5d.py:273-277`, the `_identity` write loop;
  `unified_throw_cov.py:569-570`; and `mii_adopt_unified_5d_stamped.py:168`'s `LEG_IDENTITY_KEYS`, which
  `POINTER 4` cites as a write site and which at this base is the key **tuple** those writes use). **A
  new build at current HEAD writes them** — structurally the same route as cause 4's: the capability
  landed after G's bytes existed.
- **`M(i)`:** the fixed-seed null, under §6.4's ruled scale-relative bound — see §3.1a.
- **`M(ii)`:** **the joint-baseline composite quantity on Z**, per §6.3 — the variation of the
  **assembled** `C_Z` when the sweep-side and throw-side estimator baselines are varied **jointly**, not
  the fixed-draw 12-seed scan. The design (how many members, which offsets) is **open and must be
  specified**; §6.3 explicitly does not adopt the 46/50-member family as necessary. Costed in §5.4.

**The three outcome classes must be predeclared, per §6.3.** `PREDECLARE-20260901-cause3-mii` §4's six
branches are the model and `R4` preserves them: two INCONCLUSIVE (wrong footing; vacuous seed variation),
one favourable, three unfavourable. **A valid large result is not automatically MET** — the branch
structure is what makes the leg falsifiable, and Z's must be written before Z's measurement, not after.

## 2.4 Cause 4 — scalar jitter subtraction

**G:** `C` MET, `P` MET, **`M` OPEN — AND IT CANNOT BECOME `MET`**, `T` MET. The ground is **structural,
not a search** (`DECISION-20260902-joseph-applies-oi173-cause4-m.md` §5, superseding `SCOREBOARD` §3's
empty search at `:670`): no **committed** revision of `unified_throw_cov.py` carries both the
jitter-floor print and the flux fix `081ae4ac`.

**Re-measured at this base:** ancestry of `081ae4ac` in `a0cdc019` → **false** (the print revision,
2026-06-08T16:24:23−07:00, **predates** the flux fix, 2026-07-31T23:53:54−04:00); ancestry of `081ae4ac`
in this base → **true**; `unified_throw_cov.py` carries **one** `jitter` occurrence, a **comment** at
`:476`, and `jit_trace` **zero** times. **This measurement is narrow and is labelled narrow:** it
establishes that those two revisions do not coexist and that the current file carries no print, not that
no committed revision anywhere carries both. The broader conclusion is
`DECISION-20260902-joseph-applies-oi173-cause4-m.md` §4's, whose cell text carries *"committed"*
deliberately.

**What Z must do differently: build at a NEW revision that re-adds the print on top of current HEAD.**
This base descends from `081ae4ac`, so such a revision carries **both**. G can never benefit; Z's would.

**`OI-173` `RULING 2` fixes the referent:** `M` is specified **against the class of object the defect
actually reached — the reported ratio — NOT against the stored covariance.**

**Packet §5's three verification conditions, plus a fourth this lane adds because §5's third needs a
mechanism:**

1. the re-added print computes **the same quantity** the retired code printed —
   `jit_trace = float(np.sum((x_cv2 − base) ** 2))`, `x_cv2` a second CV unfold at `seed + 7`, recovered
   from `a0cdc019:232-252` and compared line for line;
2. its **operands are the new build's own** — both vectors' content digests in Z's receipt;
3. adding it **does not change the covariance content**;
4. **the print is print-only, never subtracted.** Cause 4's `C` leg is *"no subtraction term anywhere on
   the path"*; a quantity in scope is one edit from being subtracted. Condition 3 must be enforced by a
   **guard that fails** if the computed value ever reaches the stored covariance, not by a one-time
   comparison.

**The single-draw referent is RETAINED.** `jit_trace` is a **one-sample estimate of a variance** — the
recovered comment writes it as `E‖x_cv2 − x_cv1‖² = 2 Σ_bin σ_jit²` and a single evaluation is one draw
(`SCOREBOARD` §3). **For Z this is materially better than for G:** Z's printed value is *the* realization
Z's own construction would have subtracted, contemporaneous with the build. It is still one draw, and
Z's receipt states so with its seed named. **Rev. 1 floated requiring `n > 1` draws; that is withdrawn
(§6.5) on the reviewer's directive, adopted by Joseph** — the defect cause 4 names *is* a single-draw
subtraction, so a multi-draw `M` would measure something the defective construction never did.

## 2.5 Cause 5 — frozen PET weights

**G:** **`N/A` ON ITS MERITS**, established 2026-08-17, declaration landed in `VL66` at `d1c5f90`.

**RULED for Z, 2026-09-06 (§6.1): an artifact-specific "INAPPLICABLE, DISPOSED BY DECISION" outcome is
authorized for `(cause 5, Z)`, after the complete trace and the falsifier check — without four
artificial METs, without extending `CRITERIA` §0's vocabulary, and distinguished from a mechanical
four-MET discharge.**

**What Z must do first: re-run the trace on Z's own path.** `VL66`'s declaration carries its own scope,
stated by the declarer so it could be falsified: *"the trace covered the bank build (`sweep_bank_5d.py`),
the three block producers, and the background source. It did **NOT** exhaustively audit
`analyze_universes_5d.py` or `adopt_unified_5d.py` for every input."* And it names the falsifier: *"a
PET-derived product consumed by either of those two modules."*

**Z's path is a superset of the traced one** — it adds a lateral-replacement chain, and `D_Z`'s transfer
runs through `adopt_unified_5d.py`, **one of the two modules `VL66` did not audit**. So the trace must be
re-run over **every module Z invokes**. This is a **static read**, not compute — cheap, but neither free
nor inherited. **And not by cause 5's owner:** `VL66` records that `OI-3`'s owner cell reads *"PET /
cause 5 owner"*, so the non-transferability claim is the owning lane's own and *"is not itself the
outside-lane evidence"*; the outside evidence is the `sweep_bank_5d.py` trace and *"it stands alone"*.

**Why a ruling was needed, and why the remedy rev. 1 proposed was the wrong one.** `CRITERIA` §3:246
defines the vocabulary as `MET` / `OPEN` / `UNRESOLVED` and states *"a cause is discharged only with four
METs"*. `SCOREBOARD` §7b put the question and it was **RULED 2026-08-17, the conservative branch**: a leg
graded outside those three *"can never discharge, however sound the reasoning for its inapplicability."*
So a cause-5 `N/A` blocks a mechanical seven-MET Z. **Rev. 1 offered "define a fourth token" as a route.
That route was already closed** — `DECISION-20260902-joseph-rules-no-fourth-grade-token.md`
(`e59df955…`), Joseph, *"okay I also agree"*: **`CRITERIA-20260811` §0's vocabulary stands unchanged; no
token is added for the permanently-unmeetable state.** That record is in this tree and rev. 1 did not
open it. §6.1 records the correction and the ruling that replaces it.

## 2.6 Cause 6 — incomplete statistical projection

**G:** `C` PARTIAL, **`P` OPEN — *"no product rebuilt at all"***, `M` OPEN, `T` MET.

**⚠ TWO REV. 1 CLAIMS ARE WITHDRAWN HERE. Both were the reviewer's findings and both reproduce.**

### 2.6a WITHDRAWN — the bidirectional coverage guard is not missing

`CRITERIA` §2 cause 6 `C` says *"`build_projection_M` checks 5D→4D coverage and **never** 4D→5D"* and
calls it *"an unrepaired instance of cause 6 in current code"*. Rev. 1 carried that forward as a Z
requirement. **Measured at this base, it is stale, and BOTH projectors guard both directions:**

- **`p4_lib.build_projection_M` (`:1353`) — FAIL-CLOSED both ways.** The construction loop requires every
  reported HIGH bin to land in a reported LOW bin (`:1380`), and an explicit second block at
  `:1394-1395` — `empty = np.nonzero(~M.any(axis=1))[0]; require(empty.size == 0, ...)` — fails on any reported LOW bin
  no HIGH bin reaches. Its comment is dated **2026-08-09, BEN-064** and names the exact masking defect
  `CRITERIA` describes: *"an error that is loudest about the least important thing is worse than no
  error, because it redirects the investigation."*
- **`p4_lib.reachable_low_mask` (`:1322`) — the contract correction, 2026-08-10.** The projection's low
  support is *"not 'the 4D reported mask'; it is 'the part of the 4D reported mask the 5D support
  reaches'"*, **derived** rather than assumed, with the bidirectional check *"left exactly as it is — it
  becomes a genuine invariant that must never fire in production rather than a thing the caller argues
  with."* The 5 dropped bins hold `3.00e-46 .. 2.09e-44`, *"0.0000% of the 4D total; that is a fact about
  these products, not a licence"*, and the caller records indices and count.
- **`eavailW_covariance.py:407-432` — guarded both ways and DELIBERATELY NOT fail-closed.** Added
  2026-08-11 for quarantine cause 6, with the reason stated in the code: the `(E_avail, W)` plane is
  kinematically constrained (`W² = M² + 2·M·E_avail − Q²`), *"so some cells are physically unreachable
  and an empty row here can be correct, where in a 5D→4D marginal it cannot be. Aborting would make a
  legitimate geometry unrunnable. So: count it, name it, and put it in the output."* The value is
  single-sourced in `ew_coverage_report` (`:55-68`) and propagated to the ROOT by `write_ew_outputs`
  (`:71`), so a propagation test has something to bind to.

**Z's requirement is therefore NOT "repair the guard". It is: preserve the asymmetry, and prove it.**
Z's contract requires the P4 projector to stay **fail-closed** and the `(E_avail,W)` projector to stay
**count-and-report**, with both censuses in Z's receipt. **A Z that "fixes" the `(E_avail,W)` projector
into fail-closed would break a legitimate geometry** — the opposite error, and the one this correction
exists to prevent.

### 2.6b WITHDRAWN — reuse of `C_stat`/`C_ML` is not evidence of incompleteness

Rev. 1 read `sbatch_finalize_5d_bkgaware_gpu.sh:8-10` — *"C_stat/C_ML are #13-invariant → reuse existing
`uq_cov_stat_5d.root` / `uq_cov_mlsplit_5d.root`"* — as proof that Z must regenerate them. **The reviewer
is right that this does not follow:** the launcher proves **reuse**, and reuse of an invariant input is
not incompleteness. **Fresh scalar replica generation needs a stated scientific rationale, and this lane
does not have one.**

**And the sentence rev. 1 leaned on is PET-scoped.** `CRITERIA` §2 cause 6 grounds the cause on
*"`docs/OPEN_ITEMS.md:62-63`: 'Rerun the five-axis statistical replicas and project the full covariance
as `M C_5D Mᵀ` before rebuilding `(E_avail,W)` significances'"*. **At this base `:62-63` carries an
unrelated ID-collision note.** Measured: the archived form is at `docs/OPEN_ITEMS-ARCHIVE-2026-08.md:76`,
and the **live home is `OI-4`** — owner *"C (PET)"*, route `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`,
prerequisite *"the full-event nominal and coherent ensemble"*. **Cite it by id, never by line.** The scope
consequence the decay hid: the sentence `CRITERIA` applies to the 5D GBDT covariance now lives in a
PET-scoped row. **This lane flags that and does not reconcile it.**

### 2.6c What Z's cause-6 disposition actually is

1. **`P` is the real gap, and it is about a PRODUCT, not an ensemble.** *"No product rebuilt at all"*
   means no `(E_avail,W)` covariance has been rebuilt since the fix (`KNOWN_ISSUES.md:357`), and the same
   script's J28 flux site is code-fixed with **no number produced** (`KNOWN_ISSUES.md:338-349`). Z closes
   this by **producing** `C_low = M C_Z Mᵀ` via `uq_math.project_covariance`, with a receipt naming
   **both** the operator and the corrected `C_5D` input. *"Never sum standard deviations across
   marginalized cells"* — the comment is at `eavailW_covariance.py:392-395` at this base and the call is
   `project_covariance(C5stat, Mew)` at `:441` (`CRITERIA` §2 cites the pre-drift range `:316-341`).
2. **`C` is the coverage contract of §2.6a, preserved and evidenced**, plus the exactness of the map.
3. **`M`:** √Tr and per-bin median of the marginalized covariance under (i) summed standard deviations
   and (ii) `M C Mᵀ`, on **identical** inputs, plus the orphan-bin count **in each direction** and the
   fraction of √Tr they carry.
4. **The ensemble question is OPEN and is named as open.** Whether Z reuses S's `stat_cov`/`ml_cov`
   digests or regenerates the replicas is a **scientific** decision requiring a rationale — for example,
   a measured incompatibility between those inputs' footing and Z's. **This specification does not
   decide it**, and §5 prices both.
5. **A scope question, stated rather than decided.** `6a` (the operator) is a property of a projection
   *from* the trunk; `6b` (the ensemble) is a property of the trunk. Whether `(cause 6, Z)` is graded on
   both is a scoping call the grading lane should make **explicitly** rather than inherit.

**A recorded cross-check that must not be read as a gate.** `RECEIPT-20260816` surfaces it deliberately:
between the marginal and the independent 4D routes, **3,009 of 4,825 bins differ by more than 3%**,
median `4.4%`, max `72.9%`, integrals agreeing to `0.56%`. The receipt states it *"bears on the
marginalization-vs-direct question, NOT on the projection identity (`3.76e-16`)"*.

## 2.7 Cause 7 — CV-support-limited lateral selection

**G:** **permanently OPEN** under `R1`, an immutable historical cell. **Z cannot change that.**

**What Z must do differently:** `PREDECLARE-20260905`'s replacement algebra applied to a **full rebuild**.
`L_support` is exactly the five-band sum over `p4_lib.BANDS` read from the support family; `L_active`
exactly the corresponding five selection-complete mean-centered MAT endpoint covariances on Z's mask and
row order; support keys `hCov_universe5d_<band>`, active keys `p4_lib.candidate_band_key(band)`.

**⚠ THE COUNTERFACTUAL AND THE AGGREGATE DIFFERENCE ARE TWO DIFFERENT OBJECTS, and rev. 2 separates them
on the reviewer's directive.** For Y they coincide, because the lateral swap is Y's only change. **For Z
they do not:**

- **The lateral counterfactual** — `Σ_A L_active` against `Σ_A L_support` on Z's own inputs — is
  `(cause 7, Z)`'s `M`. It isolates the defect cause 7 names.
- **`C_Z − C_G`** is an aggregate difference that **also contains** the inflation, the centering, the
  statistical block and every other cause's change. **It is a reported number and it is NOT cause 7's
  magnitude.** Reporting it in cause 7's cell would attribute six causes' worth of movement to one.

Z's receipt reports both, each labelled with **what it is a difference of**, and cause 7's `M` cites only
the first.

**The five-of-nine scope limit is inherited in full, and so is its pre-condition.**
`nd-unfolding/uq_5d/detector_universes.txt` enumerates **nine** detector lateral bands (18 lines = 9
bands × 2 endpoints): the five kinematic ones plus `MinosEfficiency`, `GEANT_Neutron`, `GEANT_Pion`,
`GEANT_Proton`. Z replaces five of nine; the other four sit in `R` (§1.3a). The justification is that
they are **weight-only** — `VALIDATION_LEDGER.md:788-791` and `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:239-241`
both say so. **But the ledger sentence sits in the FPS row** (job `56431823`, the 266-bin chain), so it is
a **2D/FPS-side claim**, and `PM-1` — re-measuring it on G's own `combined_source` — is a Z pre-condition
exactly as it is Y's. **The `2D_OMNIFOLD_REFERENCE.md` sentence is not a second measurement**; both
describe the same kinematic/weight-only split.

**A measured expectation, and the prohibition attached to it.** S's committed `support_comparison` records
`sqrt_tr_active = 1.4742855148740122e-38` against `sqrt_tr_support = 1.474709838719496e-38`, ratio
**`0.9997122662137712`** — the five-band lateral block moves **−0.0288%** on the 5D grid. F's 266-bin
replacement moved **+10.96%** (`VL69`–`VL71`), per-bin σ ratio min `0.7897`, median `1.0071`, max `1.4402`
(`VL74`). **Prohibited:** citing either as Z's `M`, or as a reason Z's `M` need not be measured.
**Permitted:** sizing the run, and noting that the two differ **in sign and by two orders of magnitude** —
which is itself why the 5D number cannot be inferred from the FPS one, and why §3.3's fixtures must be
**bidirectional**. The S ratio carries `support_ratio_is_diagnostic_not_bounded` in its own receipt, and
`p4_lib.py:1309-1318`'s helper *"deliberately bounds nothing"*.

---

# 3. TERMINAL CRITERIA — deliverable `RZ(v)(c)`

**`RZ(ii)`: seven distinct assessment cells.** What a completed Z assessment looks like **per cell**, and
what a **failed** one looks like. **It opens no cell. It grades nothing.**

**And, per `RZ(ii)` as §6.1 reads it: `RZ` requires seven ASSESSMENTS, not seven favourable results.** A
Z with six METs and one `INAPPLICABLE — disposed by decision` is a **complete** assessment under §6.1,
not a failed one.

## 3.1 The fixed-seed null contract, stated once so §§2.3 and 3.2 cannot contradict it

### 3.1a The measurement, and why the implemented bound is not a bound

Rev. 1 alternated *"exactly zero"* and *"≤ tol"*. The implementation is
`nd-unfolding/unified_throw_cov.py:509-520`, with the tolerance at `:517`:

```
# Fixed-seed null: this must be exactly zero (within floating tolerance).
null_norm = float(np.linalg.norm(x_cv2 - base))
tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)
if null_norm > tol: raise SystemExit("[FAIL] CV re-unfold is non-deterministic ...")
```

**So the contract is "exactly zero within a floating tolerance", and the two phrasings are not in
conflict — but the tolerance as written is vacuous on this scale.** `base` is a cross-section vector:
per-bin values are order `1e-39` over 10,694 reported bins, so `‖base‖` is order `1e-37` — **far below
`1.0`**. Therefore `max(‖base‖, 1.0)` evaluates to `1.0` and `tol` is an **absolute `1e-12`**, roughly
`10^25` times `‖base‖`. **It is not a relative determinism bound; it is a bound that essentially nothing
can violate.**

**This does not mean G's null is bad.** The measured value on G is `5.8223e-50`, i.e. `1.31e-12` of the
sqrt-trace (`CRITERIA` §2 cause 4) — genuinely tiny *relative* to the scale. **The defect is in the
guard, not in the product**, and it is the `T`-leg shape this campaign already knows: a check that cannot
fail.

### 3.1b What Z's contract requires

**Ordinary correction, no decision needed:** acknowledge the floating tolerance rather than claiming
literal zero; require the key **present** (absence must fail, never pass vacuously) and both operands
**finite**; and state the **units and normalization** of every quantity in the comparison.

**RULED, 2026-09-06 (§6.4): Z uses a SCALE-RELATIVE null bound, fixed before production**, with the
numerical value justified by precision and sensitivity controls established **before** implementation and
**not** selected from a favourable production result. **This does not retrospectively regrade G.**

**The ruling fixes the FORM; the normalizer and the numerical value are still undefined.** §3.6a lists
exactly what completes it, and until it is complete `(cause 3, Z)`'s `M(i)` cannot be graded.

## 3.2 Per-cell completion and per-cell failure

A cell is `(cause n, Z)`. Under `CRITERIA` §0 each carries four legs `C`/`P`/`M`/`T`, all four must hold,
and `UNRESOLVED` is a permitted per-leg verdict that must not be re-read as the nearer of PASS/FAIL.

| cell | **complete** looks like | **failed** looks like |
|---|---|---|
| **(1, Z)** | both one-sided choices per ± pair, **off-diagonal included**, denominators named, the three non-pair bands accounted for **without invented endpoints**, the below-1 tail reported, `require_truth_ratio_bank` PASS, **independently verified**, and the `RULING 1` disclosure written | the counterfactual is diagonal-only; a denominator is unnamed; a ± endpoint is invented for a non-pair band; the below-1 tail is dropped; the measuring lane also grades it |
| **(2, Z)** | `hJointMeanShift` and `joint_mean_shift_norm` present; the floor `√Tr/√N` with `N` stated; `k = uq_math.F7_FLOOR_MULTIPLE` **imported**, strict `>`, value reported; **both** centering variants emitted as separate files with explicit `--out` | a mean-centered-only product; the shift folded into the variance; `k` retyped or left as *"≫"*; `--out` defaulted |
| **(3, Z)** | `estimator_seed` **and** `draw_seed` stamped at **both** legs; a mixed-seed `C_syst` slab **refused**, not merely unstamped; the null under §3.1b's scale-relative bound with the key **present**; `M(ii)` measured as the **joint-baseline** quantity under a predeclared three-class outcome rule | any leg unstamped; the null key **absent**; `M(ii)` substituted by the narrow fixed-draw scan **without** the substitution being separately ruled; `M(ii)` inferred from `\gbdtAiEstTrace`, which `FOOTING-20260817` established cannot serve on footing; outcome classes written after the result |
| **(4, Z)** | the re-added print's value, **seed** and both operand digests; §2.4's four conditions met, condition 4 enforced by a **guard**; the `M` referent is the **reported ratio** per `OI-173` `RULING 2`; the single-draw nature stated | the quantity differs from `a0cdc019:232-252`; operands borrowed; covariance content changes; the value is ever **subtracted**; `M` reported against the stored covariance |
| **(5, Z)** | the trace re-run over **every** module Z invokes — **including `adopt_unified_5d.py`, which `VL66` did not audit and which `D_Z` runs through** — by a lane that does not own cause 5, with the falsifier restated; then **`INAPPLICABLE — disposed by decision`** under §6.1 | the trace is inherited from `VL66`; a module Z introduces is unaudited; the owning lane's own statement is counted as outside corroboration; **or four METs are manufactured to avoid the token problem** |
| **(6, Z)** | `C_low = M C_Z Mᵀ` **produced**, with a receipt naming operator and input; the P4 projector **fail-closed** and the `(E_avail,W)` projector **count-and-report**, both censuses recorded; `M` under both routes; the reuse-vs-regenerate decision made **with a stated rationale** | the projection sums standard deviations or is diagonal-only; the `(E_avail,W)` projector is "fixed" into fail-closed, breaking a legitimate geometry; the `3.76e-16` identity is quoted as if it settled the marginal-vs-direct route question; replicas regenerated with no rationale |
| **(7, Z)** | five-band inventory exact both sides; ten ± endpoints each with migration census and declared policy; §1.3b's identities within `1e-9`; `PM-1` clearing the five-band scope on G's own `combined_source`; `M` reported as the **lateral counterfactual**, with `C_Z − C_G` reported **separately and labelled** | any band missing, extra, duplicated, one-sided, or on the wrong grid; a declared-zero band measuring nonzero migration **or the reverse**, noted rather than aborting; a whole-S total substituted; `C_Z − C_G` cited as cause 7's magnitude |

## 3.3 Reject-Z conditions — the specification's falsifiers

**Z is rejected outright, before any cell is graded, if any of these holds:**

1. `mask_digest(Z) != mask_digest(G)` or `row_order_digest(Z) != row_order_digest(G)`. **⚠ The
   condition stands; its operand cannot be READ from G — §1.3d. Both digests must be reconstructed from
   G's production-CV input, and that input's identity must be bound before this condition can fire.**
2. Any §1.3b identity fails outside relative `1e-9` — **including the four that do not exist yet**.
3. `V`, `R`, `A` are not pairwise disjoint, or do not exhaust the support family's band set.
4. Any `g^c[i] < 1`, or non-finite, or `≠ 1` where `v_blk[i] == 0`.
4b. **`g^c` does not reproduce when reconstructed independently** from `diag(C_unified)`,
    `diag(C_blocksum)` and `hJointMeanShift` by §1.3a's formula, **for each variant separately and each
    from its own operands**. Two distinct failures are covered and neither implies the other: an
    **uninflated** object (`g ≡ 1`), which conditions 2, 4, 6 and the closure identity all admit; and a
    **dropped shift** (`g^cv` equal to `g^mean`), which survives the first mutation entirely — §3.4(ii).
4c. The run proceeds against a fixed-seed null bound or a `(cause 3, Z)` outcome rule that **§3.6 still
    lists as incomplete**. An un-derived boundary is not a criterion, and grading against one is the
    failure §3.6 exists to prevent.
5. `C_unified` appears as a budget block rather than through its diagonal, or `C_seed` appears as a
   budget block at all.
6. Symmetry or PSD fails **on the inflated object**.
7. The parent digest recorded is not G's `4f168e83…`.
8. A band list was **retyped** rather than imported from `p4_lib.BANDS` / `adopt_unified_5d.VERT_BANDS`.
9. Any endpoint lacks a selection-migration census, or contradicts `p4_lib.py:64-65`'s declared policy.
10. The producing revision is unpinned, or import-closure digests are not bound to the run.
11. The fixed-seed null key is **absent**, or its bound is not the scale-relative one §6.4 rules.
11b. **⚠ RESTATED IN REV. 16 — the requirement stands, its OPERAND was wrong.** The null RATIO cannot
    be **independently reconstructed from the persisted `x_cv`, `x_cv2` and support predicate in Z's own
    throw product**. The throw writer does **not** persist them today (`unified_throw_cov.py:540-579`,
    measured; the vector is computed at `:369-371` and dropped at `:586`), so **Z's writer must**, at
    `1.05` MB against a **`2.668` GB** product (⚠ rev. 17; rev. 16 wrote `≈41` GB, which is the
    45-component band family, not the throw product). Without it the validator can only read the producer's own
    number back and compare it with itself — the shape §1.3b rejected for `g`. **Rev. 7–15 sourced the
    denominator from the production ROOT's `hXSecND_flat` instead; that is a different object from a
    different job, and it PRESUMES the determinism the null tests** (§3.7a).
11c. **NEW IN REV. 16, and conditional by construction.** An **external** cross-check of `‖x_cv‖`
    against a named production ROOT's `hXSecND_flat` is reported as agreement **only** where that
    vector's identity with the persisted `x_cv` has been established **elementwise**. It is never a
    substitute for `11b`. Where identity is not established the field is **`UNRESOLVED`** — never
    omitted, and never a cardinality check standing in for an identity
    (`adopt_unified_5d.py:116-121` asserts `x.size == n` **only**, measured: not the mask, not the
    values).
12. `PM-1` shows the five-band scope does not cover cause 7's defect class on G's own `combined_source`.
13. The receipt reports `C_Z − C_G == L_active − L_support` as an identity (§1.3c), or cites `C_Z − C_G`
    as cause 7's magnitude (§2.7).
14. Only one centering variant was produced, or `--out` was defaulted for either.
15. Z's tally is presented combined with G's or Y's grades, in either direction (`RZ(iii)`).

**A large `M` on any cause is NOT a reject condition.** `R3` settled that for cause 7; `CRITERIA` §0
states it framework-wide — *"M does not require the corrected number to be small… what is forbidden is an
unmeasured one."* **Cause 1 is the one place a magnitude stopped a cause**, and it did so by a separate
ruling creating a disclosure obligation, not by a threshold — and §6.2 now closes that route for Z.

## 3.4 The test contract — power-tested in both required directions, per cell

`CRITERIA` §0's `T` leg requires a guard that fails when the defect is reintroduced **and** when the
guarded object disappears.

- **Direction 1 — defect reintroduced.** Per cause: substitute the one-sided form (1); emit
  mean-centered-only above the floor (2); feed a mixed-seed slab (3); **subtract** the jitter value (4);
  introduce a PET-derived input to a module Z invokes (5); replace `M` by its diagonal (6); substitute
  CV-support-limited bands for the active endpoints (7). **Plus, for §1.3a:** move a vertical band from
  `V` into `R`; add `C_unified` as a block; feed a `v_blk == 0` bin and check `g` is pinned to 1 rather
  than `inf`; **and TWO DISTINCT INFLATION MUTATIONS, which rev. 3 wrongly collapsed into one:**

  **(i) `g^c ≡ 1` everywhere, emitting the block sum as though it were inflated.** This passes the
  closure identity, `g >= 1`, the zero-denominator rule and PSD, so **only the reconstruction gate can
  fail it**. **The fixture must make `g ≡ 1` WRONG**, which is not automatic: `g[i] = 1` is the *correct*
  answer wherever `v_uni[i] <= v_blk[i]`, because `max()` then returns `v_blk[i]`. So the fixture must
  carry bins with `v_uni > v_blk` and the test must assert the reconstructed `g` exceeds 1 on them —
  otherwise the mutation is indistinguishable from legitimate input and the test passes vacuously.

  **(ii) `g^cv ← g^mean` — the dropped-shift mutation, and it is NOT reachable by (i).** Rev. 3 claimed
  running (i) *"separately for each variant"* would catch a validator that reconstructs `g^mean` and
  reuses it for `g^cv`. **It does not.** Traced: against a producer emitting `g ≡ 1`, that faulty
  validator reconstructs the true `g^mean ≠ 1` and compares it to `1` on **both** variants, so it
  **rejects twice** — correct behaviour, for the wrong reason, and the reuse fault survives.

  The discriminating mutation is a **producer** that emits `g^cv = g^mean`, i.e. drops the
  `+ mean_shift²` term, on operands for which the two must differ. **Worked fixture:** `v_blk = 1`,
  `v_uni = 4`, `mean_shift = 1` gives `g^mean = sqrt(max(4,1))/sqrt(1) = 2` and
  `g^cv = sqrt(max(4+1,1))/sqrt(1) = sqrt(5) ≈ 2.2360680`. A correct validator reconstructs `g^cv`
  **including** the shift term and fails; the reuse-faulty validator reconstructs `g^mean`, compares it
  to the producer's `g^mean`, and **passes**. That is the only mutation in this contract that separates
  the two validators, and a `T` leg without it has not tested the CV-centered reconstruction at all. Each must fail **specifically**, even when dimensions, PSD, total trace and internal sums
  still pass.
- **Direction 2 — guarded object disappears.** Delete or rename, one at a time: an active endpoint; an
  active-band object; a migration census/policy; G's parent digest; `fixed_seed_null_norm`; a seed stamp;
  the throw ROOT; `hJointMeanShift`; the projection operator. Each must **fail**, never skip, never
  reduce a band count, never read absence as zero.
- **Positive control** passes with exactly five ± endpoint pairs, the exact G parent digest, G's exact
  mask and row order, both centering variants, and every §1.3b identity within `1e-9`.
- **Artifact-confusion controls must fail:** F (wrong 266-bin grid), J (wrong parent digest), a whole S
  total (no inflation, and changes more than the lateral block), and **G itself**.
- **Two things that do not satisfy `T`:** a source-string assertion, and a test of
  `check_support_comparison` alone — that helper *"deliberately bounds nothing"* (`p4_lib.py:1309-1318`).
- **One thing that does not satisfy `T` and is new in rev. 2:** a fixed-seed-null test written against
  the **current** `tol` formula, which §3.1a measures as unable to fail on this scale.
- **Fixture provenance.** Build fixtures from the **producer's** own objects and metadata. A fixture
  derived from the predicate cannot disagree with it.
- **Mutation discipline.** Each mutation must be shown to **reach** the guard it targets. A digest check
  that refuses a mutated input first, with the same exit status, tests the digest check and not the
  guard; call the unit directly where that is a risk.

## 3.5 What a completed, seven-cell Z assessment could and could NOT establish

**A Z with all seven cells complete and favourable would establish exactly one thing:** that the seven
quarantine causes are disposed **for the artifact Z**, as a self-contained tally. Nothing else.

It would **not**: move any of G's cells (`RZ(ii)`; `(cause 7, G)` stays permanently OPEN under `R1`);
move Y's cell or widen Y; move the CAND or QUOTED counts (`RZ(iii)` — CAND stays `1 of 7`, QUOTED
`0 of 7`); move **Gate 2**, which remains FAIL on six independently sufficient NOT-DISCHARGED clauses
(`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`, exercised at `327bc105`); **adopt Z**
(`RZ(i)` names a *possible* adoption subject; adoption is a separate decision and is Joseph's); license a
projection (3D/4D covariances must be exact projections from an **adopted** trunk); touch `values.tex`,
any publication claim, or `R5`'s scoped-Letter default; or **authorize its own construction** (`RZ(iv)`;
`R5`'s ceilings remain *"a prohibition and an accounting boundary … NOT authorization to spend up to"*).

## 3.6 The two terminal criteria that are NOT YET EXECUTABLE, and exactly what completes each

**⚠ REV. 7 CLAIMED TO COMPLETE THIS SECTION; REV. 16 WITHDRAWS THAT CLAIM.** §3.6 remains as written
because it is the **schema §3.7 answers against**, and a completion is only checkable against the
requirement it claims to meet. §3.6's requirements are not relaxed by §3.7 and none of them is dropped.
**After the contract review of `D1`–`D4`, §3.7 answers §3.6a's items 1, 2 and 4 and §3.6b's items 1, 2,
3 and 5 — and supplies NO NUMBER for either criterion**: the null's `ε` is withheld and both cause-3
boundaries are withdrawn. **So both criteria are still NOT YET EXECUTABLE, exactly as this heading
says.**

**⚠ AND §3.6a ITEM 3 ALREADY SAID WHY, WHICH IS THE uncomfortable part and is recorded rather than
smoothed over.** It required *"(i) state which reported quantity a non-deterministic CV could move, and
through what mechanism; (ii) derive the boundary appropriate to that relationship; only then (iii)
attach a number"* — and it warned in terms that *"a measured process-to-process floor… tells you what
repeatability is **achievable**; it does not tell you what error is **scientifically acceptable**."*
**Rev. 7 attached a number whose derivation was neither.** The schema was right and the completion
walked past it; **the requirement did not need changing, only obeying.**

**Neither is wrongly decided and neither reopens a ruling.** §6.3 and §6.4 fix the *quantity* and the
*form*; what is missing is the statistic, the normalization and the boundary that turn a named class into
something a run can be graded against. **Three named outcome classes are not yet executable criteria**,
and this section says precisely what a complete definition must contain — so the next lane completes a
schema rather than inventing one, and so the gap is visible rather than discovered at grading time.

**Both must be completed BEFORE the implementation they govern**, for the reason
`PREDECLARE-20260901-cause3-mii` §3 gives about its own thresholds: *"a threshold chosen to make the
eventual number pass is not a criterion."*

### 3.6a The fixed-seed null bound (§6.4 fixes the form; four things remain)

1. **Name the normalizer, explicitly.** The measured quantity is `‖x_cv2 − x_cv‖` in
   `cm²/nucleon`-scaled units, so the scale-relative form the ruling requires is a **dimensionless
   ratio**. The obvious candidate is `‖x_cv2 − x_cv‖ / ‖x_cv‖` — which is what
   `unified_throw_cov.py:517`'s `1e-12 * ‖base‖` was reaching for **before** `max(…, 1.0)` clamped it to
   an absolute floor (§3.1a). **It must be written down and defended, not inferred from the broken
   expression.** Alternatives that must be considered and rejected on the record if not chosen: a per-bin
   maximum relative deviation, and normalization by `sqrt(Tr C_Z)`.
2. **State units on both sides** and assert the ratio is dimensionless in the receipt.
3. **Fix `ε` from a control established BEFORE implementation — but derive it for the RIGHT MODEL, which
   is not the one rev. 3 offered.** Rev. 3 named the publication-precision rule
   `S/U ≤ sqrt(2δ + δ²)` as an admissible derivation. **It is not admissible here as written**, and §3.6d
   says why: that formula assumes `S` is an **independent uncertainty added in quadrature** to a reported
   `U`, and the null is **a difference between two central-value vectors**, not an added variance
   contribution. So the order of work is: **(i)** state which reported quantity a non-deterministic CV
   could move, **and through what mechanism**; **(ii)** derive the boundary appropriate to *that*
   relationship; only then **(iii)** attach a number.
   **And a reproducibility floor is not a substitute for step (ii).** A measured process-to-process floor
   on the target hardware tells you what repeatability is **achievable**; it does not tell you what error
   is **scientifically acceptable**, and the two coincide only by accident. It may bound `ε` from below as
   a feasibility constraint; it cannot justify `ε`.
   **`ε` may not be read off Z's own null.** §6.4 is explicit.
4. **Require presence and finiteness.** The key must be **present** — absence must fail, never pass
   vacuously (`CRITERIA` §2 cause 4's null-as-absent shape, PB2) — and both operands finite. A failure
   **aborts**; it is not recorded as a note.

**What is already determined and needs no further decision:** the bound is scale-relative, it is fixed
before production, it is not chosen from a favourable result, and **none of this retrospectively regrades
G** (§6.4).

### 3.6b `(cause 3, Z)`'s joint-baseline magnitude (§6.3 fixes the quantity; five things remain)

1. **The member definition.** What exactly one member is — this lane's reading is *a complete assembled
   `C_Z` produced at a distinct joint `(sweep-baseline, throw-baseline)` estimator-offset pair*, the
   sweep side varying from `42` and the throw side from `1000` — **and the offset set itself**. §6.3
   leaves the design open, so this is the design.
2. **The statistic — and §6.3 has ALREADY FIXED ITS SUBJECT, which rev. 3 wrongly reopened.** §6.3 rules
   the quantity to be *"the variation of the **assembled** covariance `C_Z`"*. Rev. 3 offered
   per-member **cross-section vectors** and per-member **covariance entries** as a free choice between
   equals. **They are not equals under the ruling:** the assembled covariance is the ruled subject, and
   the narrow scan's `C_seed` — a covariance over *vectors* (`PREDECLARE-20260901-cause3-mii` §1) —
   **cannot replace it** without either a demonstrated equivalence or the **substitution ruling §6.3
   expressly reserves**. What remains open is the statistic's *form over the ruled subject*: how spread
   among assembled matrices is reduced to a number. **Name it; state why; state its dimension; and if the
   answer drifts toward vector spread, that is a substitution question, not a drafting choice.**
3. **The normalization — two legs, and the second must bind independently.** An aggregate leg
   (`f_agg`-shaped, a trace ratio against a **named** denominator) and a per-bin leg (`f_med`-shaped),
   because — the predeclaration's own reason, which transfers unchanged — *"the same trace can be diffuse
   or concentrated, so the per-bin leg is independently binding."* Both denominators named in the same
   sentence as their numerators.
4. **The boundaries, DERIVED for the right model — and rev. 3 mandated the WRONG derivation.** Rev. 3
   said to *"use the rule `PREDECLARE-20260901-cause3-mii` §3 already established"*,
   `S/U ≤ sqrt(2δ + δ²)`. **That rule does not transfer to this statistic**, for the reason §3.6d gives:
   it is derived for an **omitted independent contribution added in quadrature**, and variation among
   **assembled covariance matrices** is a change *in* `U`, not an independent `S` added to it. **Applying
   it here would import an additivity model nobody has demonstrated.**

   What **does** transfer is `δ` itself — `(half the last printed unit) / (the printed value)`, measured
   on **Z's own** reported quantities at **Z's own** declared precision. What must be derived per
   statistic is the **map from the statistic to `(U' − U)/U`**. §3.6d gives the two cases and the rule
   for choosing between them.

   **And the candidate's `4.15%` / `2.74%` may NOT be carried across in any case** — the predeclaration
   says *"if the printed precision changes before execution, these numerical thresholds are void and must
   be redeclared before the run."* Z's precision is measured first, then the boundary derived.
5. **The three classes mapped onto branches, with the falsifiers named.** §6.3's favourable /
   unfavourable / inconclusive map onto the six-branch structure `R4` preserves: **inconclusive** covers
   wrong footing and *vacuous variation* — a readback whose seed set or fixed-draw identity does not match
   the declaration, where **a zero spread is evidence the knob never reached the estimator, not a
   favourable result**; **favourable** requires *both* legs inside their boundaries; **unfavourable**
   splits by which leg exceeded. **A valid large result is not automatically MET**, and boundary equality
   is favourable only if the conditions are written `<=`.

**And one thing that must NOT be imported:** `F7_FLOOR_MULTIPLE = 2.0` has **no principled role** here.
The predeclaration's §3 states why and the reason transfers verbatim: F7 compares an ensemble mean shift
with a finite-`N` sampling floor, whereas this measures the covariance generated by changing estimator
seeds, and `sqrt(Tr C)/sqrt(N)` *"would import systematic covariance into an estimator-noise test."*

### 3.6d The acceptance mathematics, stated once because BOTH criteria above depend on it

**The publication-precision idea is sound and it is the right family of criterion. The specific formula
is not portable, and rev. 3 ported it twice.** Written out, the original derivation
(`PREDECLARE-20260901-cause3-mii` §3) is:

> an **omitted independent contribution** `S` added to a reported uncertainty `U` gives
> `U' = sqrt(U² + S²)`; requiring `U' − U` below half the last printed unit yields
> `S/U ≤ sqrt(2δ + δ²)`.

**Every step past `δ` depends on the quadrature model, and quadrature is an assumption about the
statistic — not a property of publication precision.** It is the model under which the statistic *would
be* an independent variance contribution added to a reported `U`.

**⚠ AND THAT IS A CONDITIONAL, WHICH REV. 4 STATED AS A FACT ABOUT THE NARROW SCAN. Corrected here,
because the overstatement contradicts this document's own §1.3a.** Rev. 4 wrote that an independent
contribution *"being added to the budget"* is *"exactly what `C_seed` is for the narrow scan."* **It is
not, and the predeclaration forbids it:** `PREDECLARE-20260901-cause3-mii` §5 states *"It does not add
`C_seed` to the uncertainty budget. A magnitude measurement and budget adoption are different
decisions."* §1.3a property 3 of this very document quotes that same line. **Quadrature is the
CONDITIONAL MODEL that motivated the narrow scan's thresholds** — *if such a contribution were added,
how large could it be before it moved a printed value* — and it is **not** a demonstration that `C_seed`
is independent, nor a claim that it enters any budget.

The model does **not** automatically hold for a difference between two CV vectors (§3.6a) or for
variation among assembled covariance matrices (§3.6b) — and, as the paragraph above shows, it was never
*demonstrated* even where it was used.

**So the derivation splits, and the split is what must be written down:**

| what the statistic IS, relative to the reported `U` | the boundary that follows |
|---|---|
| a **directly measured change in `U` itself** — **the DEFAULT for §6.3's assembled-covariance subject** | `\|U' − U\| / U ≤ δ` — no quadrature step, because nothing is being added |
| an **omitted independent contribution** added in quadrature | `S/U ≤ sqrt(2δ + δ²)` — **available only after independent additivity is DEMONSTRATED for the statistic in hand**, never by analogy with the narrow scan, which did not demonstrate it either |
| **neither** | derive it, and state the model in the same sentence as the number |

**The default is the reviewer's standing recommendation and this lane adopts it:** *use direct relative
change when the chosen statistic measures change in the reported uncertainty itself; use quadrature only
after demonstrating independent additivity.* Since §6.3's ruled subject is the **assembled covariance**,
a change *in* `U` is what the statistic will measure unless someone shows otherwise — so the burden sits
on any proposal to use quadrature, not on the direct form.

`δ = (half the last printed unit) / (the printed value)` is common to all three and is the part that
genuinely transfers.

**The ordering rule this imposes, and it is the reviewer's:** *first* define the statistic and its
relationship to the affected reported quantity; *then* derive its boundary. Rev. 3 inverted that for
cause 3 — it mandated the quadrature boundary in item 4 while item 2 still left the statistic open — and
an acceptance boundary chosen before its statistic is a number in search of a meaning.

**Naming units and re-measuring printed precision does not establish applicability.** Both are
necessary; neither is the additivity argument.

**⚠ AND NEITHER IS BUDGET ADOPTION — NEW IN REV. 16, from the contract review's nonblocking list.**
Rev. 4–15 wrote in two places that *if* baseline variation were ever adopted into the uncertainty
budget, quadrature *"would become correct"*. **Withdrawn.** Quadrature needs **independence**, and a
contribution can be adopted into a budget while remaining correlated with what is already there.
**Adoption is a decision about inclusion; independence is a property of the statistic**, and only the
second licenses the quadrature step. **So the burden this section places on quadrature does not lift
after a budget-adoption decision** — it lifts only after independent additivity is demonstrated for the
statistic in hand, which is what the table above already required and what the two withdrawn sentences
quietly offered a way around.

### 3.6c What this section does not do

It does not reopen §6.3 or §6.4, and it takes no decision reserved to Joseph. It converts two
ruled-but-incomplete criteria into **named schemas with named derivations**, and records that until they
are completed the corresponding cells cannot be graded — a statement about readiness, not about the
rulings.

**But rev. 3's claim that it "proposes no criterion change" was too categorical, and it is withdrawn.**
Completing §3.6a and §3.6b requires **substantive scientific choices** — which reported quantity the null
could move and by what mechanism; how spread among assembled covariances is reduced to a number; and
which of §3.6d's boundary models applies. **Those are not clerical.** Two consequences follow and both
are stated rather than absorbed:

1. **If the acceptance boundary that survives §3.6d is NOT the predeclared quadrature rule** — and for
   the assembled-covariance subject §3.6d says it will not be — **then Z's cause-3 acceptance
   mathematics differs in form from the narrow scan's.** That is a **criterion question**, it belongs in
   the `RZ(v)` carve-out, and it must be surfaced to Joseph explicitly rather than settled inside a
   completion schema. This record surfaces it; it does not decide it.
2. **If completing §3.6b's statistic drifts from the assembled covariance toward cross-section-vector
   spread**, that is the **substitution** §6.3 reserved — not a drafting choice — and it needs either a
   demonstrated equivalence or a separate ruling.

## 3.7 THE TWO CRITERIA — ⚠ SPECIFIED BUT NOT COMPLETED, AND ENTIRELY PROPOSED

**Rev. 7–15 titled this section *"THE TWO CRITERIA, COMPLETED"*. After the contract review of `D1`–`D4`
that title is false and it is corrected rather than qualified in a footnote.** What §3.7 supplies is
**statistics, normalizations, operands, receipt requirements, falsifiers and outcome branches**. What it
does **not** supply, after rev. 16, is **any acceptance number**: the null's `ε` is withheld and both
cause-3 boundaries are withdrawn. **§3.6 therefore still lists both criteria as incomplete, and §3.3
condition `4c` still bites** — a run against an underived boundary is itself a reject condition. That is
the mechanism that makes this state safe, and it is why the correction is a retitling rather than an
alarm.

**§3.6 says what would complete each criterion. ⚠ REV. 17: THIS SECTION COMPLETES NEITHER, and rev.
7–16's *"this section completes them"* is withdrawn as an operative remnant.** It supplies statistics,
normalizations, operands, receipt requirements, falsifiers and outcome branches, **and no acceptance
number for either criterion**. It approves nothing.
§6.6 requires the statistic, its denominator, the precision target and the boundary to be approved
**together as one packet**, and `BEN-381` bars this lane from grading what it drafts. What changes here
is only that the packet now exists and can be put; §6.7 puts it.

**Every quantity below carries its evidence class, and a figure without one is an error in this
document.** **MEASURED** — re-measured in this checkout at this base, with `file:line` or a digest.
**TRANSFERRED** — measured on a different subject and carried here conditionally, direction of the
difference **not** established. **DERIVED** — arithmetic on the two above, no new information.
**UNRESOLVED** — named, with the exact act that closes it.

### 3.7a The fixed-seed null bound — §3.6a's four items, THREE ANSWERED AND ONE WITHHELD IN REV. 16

#### Item 1 — the normalizer, with both named alternatives rejected on the record

**CHOSEN.** The graded quantity is the dimensionless ratio

    r_null  =  || x_cv2 - x_cv ||_2  /  || x_cv ||_2

both norms taken over the **reported support** (`x_cv > 0`, `unified_throw_cov.py:370-371`, the
predicate — never a hardcoded `10,694`). Three reasons, and the first is the one that matters:

1. **Both sides are the same object.** Numerator and denominator are L2 norms of the *same*
   cross-section vector in the *same* units over the *same* population, so the ratio is dimensionless by
   construction and a receipt can assert it rather than assume it.
2. **⚠ REV. 16 WITHDRAWS THIS REASON.** Rev. 7–15 wrote *"it is the quantity the error model
   actually bounds — item 3."* **There is no error model after rev. 16** (item 3), so the reason has
   nothing to stand on and is struck rather than reworded. **Reasons 1 and 3 are untouched, and they
   are what the review's *"keep scale-relative normalization"* rests on** — the normalizer is chosen
   because both sides are the same object and because it is what the implementation was reaching for,
   neither of which depends on a bound existing.
3. **It is what the implementation was reaching for.** `unified_throw_cov.py:517` is
   `tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)` (**MEASURED**, at this base). The operand
   `‖base‖` is right; the `max(…, 1.0)` clamp is the whole defect (§3.1a). **The repair is to delete a
   clamp, not to invent a scale.**

**REJECTED — normalization by `sqrt(Tr C_Z)`.** It divides a **central-value** difference by an
**uncertainty** scale. Two consequences, either one fatal: **(a)** a Z with a larger covariance would be
permitted a *less* deterministic CV, which inverts what a determinism check means; **(b)** it makes
`M(i)` depend on the very object `M(i)` is a precondition for.

**And this rejection has a live consequence, so it is stated rather than left implicit.** The campaign's
quoted relative figure — *"the measured fixed-seed null on this product is `5.8223e-50`, i.e. `1.31e-12`
of the sqrt-trace"* (`CRITERIA-20260811` `:196-201`) — uses exactly this rejected kind of denominator.
**Which one, identified by arithmetic rather than by assumption**, because *"the sqrt-trace"* is a
definite description and this document names three:

| denominator | ratio | 3 s.f. | is it the quoted figure? |
|---|---:|---:|---|
| the **unified throw's** `4.443674e-38`, the value that same passage is discussing | `1.31026e-12` | `1.31e-12` | **YES** |
| the **block-sum** footing `4.357790406860002e-38` | `1.33608e-12` | `1.34e-12` | no |
| **G's total** `5.269625166386846e-38` | `1.10489e-12` | `1.10e-12` | no |

**A first draft of this subsection asserted the block-sum footing. It is wrong, and the correction is
recorded rather than absorbed** — the passage's own neighbouring sentence names `4.443674e-38`, so the
answer was in the operand all along. **The substantive point survives and is sharpened:** the quoted
figure is normalized by an *uncertainty* scale — a **third** one, distinct from both footings this
document otherwise uses — while `r_null` is normalized by the **central-value** norm. **Z's number will
differ, and the two must never be set side by side.** Different denominators over different populations
is this campaign's most-repeated error class, and it just caught this paragraph.

**REJECTED as the gate, RETAINED as a reported diagnostic — the per-bin maximum relative deviation
`max_i |Δx_i| / x_i`.** The support predicate is `x_cv > 0`, which admits bins arbitrarily close to
zero, so the statistic is dominated by the least significant bins and would fire on every correct run —
the mirror image of the catalogued gate-that-cannot-fail, and just as useless. Worse, **no boundary can
be derived for it**: a floating-point reduction's forward error is bounded relative to the sum of the
magnitudes it accumulates, **not** relative to a possibly-cancelling per-bin result, so item 3's model
says nothing about it. §3.6d forbids attaching a number to a statistic with no derivation, so it is
**reported with its argmax bin index** — which is what makes concentration visible — and it is **not** a
gate.

#### Item 2 — units, asserted rather than assumed

Numerator and denominator are both `cm²/nucleon`-scaled L2 norms over the reported support; `r_null` is
**dimensionless**. The receipt states the unit of each operand **and** asserts the ratio's
dimensionlessness as a field, because §3.6a's requirement is a written assertion, not a fact the reader
is expected to reconstruct.

#### Item 3 — ⚠ `ε` IS WITHHELD IN REV. 16. The formula bounded a summation the estimator does not perform

**THE FINDING IS THE CONTRACT REVIEW'S AND JOSEPH HAS APPROVED IT.** Rev. 7–15 proposed
`ε = n_iters · n_rep · float64.eps = 1.1873e-11` and called it *"imported rather than chosen"*.
**Importing the operands does not establish the error model, and the operands are the wrong ones.**
`n_rep · eps` is the worst-case forward error of **one length-`n` floating-point accumulation**. The
computation this bound is asked to govern is not one.

**MEASURED, at this base, by reading the kernel that actually runs.** In the 5D path
`unified_throw_cov_5d.py:89` installs `_xsec_for_weights_5d` into the base module, so **both** operands
of the null — `x_cv` at `unified_throw_cov.py:369` and `x_cv2` at `:514` — are produced by
`_xsec_for_weights_5d` (`unified_throw_cov_5d.py:47-84`). That function is:

| step | what it is | what `n_rep · eps` says about it |
|---|---|---|
| `omnifold_loop(…, kind="lgbm", iters, seed)` (`:59-62`) | `n_iters` rounds of **LightGBM classifier fitting** and event reweighting | **nothing.** A gradient-boosted tree fit is not a reduction |
| `np.histogramdd(sample, …, weights=w_push * wt_sig[m])` (`:66`) | accumulation over **events**, one sum per occupied bin | the length of each sum is that bin's **event occupancy** — **not `n_rep`** |
| `np.histogramdd(…, weights=wt_sig[m])` (`:67`) and `np.histogramdd(td_cols, …, weights=wt_td)` (`:76-77`) | two more event-level accumulations | same |
| `completeness[nz] = of_in[nz] / denom_nd[nz]` (`:78-80`) | an elementwise **division** by a quantity that can be small | **nothing**, and it is an amplification channel with no `n`-dependent bound |
| `extract_cross_section_nd(unfold_nd, completeness, flux, pot, nucleons, edges)` (`:81-83`) | division by completeness, flux, POT, nucleon count and bin volume | **nothing** |

**So the operand error is exact and it is this lane's catalogued one: `n_rep` counts OUTPUT BINS, while
every accumulation in the chain runs over EVENTS.** The number that would appear in a summation bound
for a single bin is its occupancy; `10694` is the count of bins the answer is *reported in*. The formula
was right about `eps`, right about the shape of a forward-error bound, and **wrong about the object**.

**And `n_iters` as an amplification allowance is asserted, not demonstrated.** Nothing shows that one
iteration compounds at most one reduction's worth of error, and the divisions above can amplify by
factors the iteration count does not track. **A conservative-sounding multiplier is still a chosen one
if its conservatism is not derived.**

**A third point from the review, and it is independent of both:** a bound on evaluating the **final
norm** — which is the one thing `n_rep` genuinely indexes — would bound the arithmetic of computing
`‖x_cv2 − x_cv‖` from two given vectors. **It would not bound the difference between the two vectors**,
which is the whole quantity.

#### ⚠ AND THE DEEPER REASON, MEASURED HERE: this is a reproducibility question, not a rounding question

**The estimator is not claimed deterministic — by its own module.** `omnifold_nn_core.py:203-204`:
*"LightGBM at these settings is otherwise **nearly** deterministic in `seed` alone."* **The word is the
author's.** And `make_estimators` (`:143-148`) constructs
`LGBMClassifier(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)` with `random_state` set
from the seed and **nothing else pinned** — no `num_threads`/`n_jobs`, no `deterministic`, no
`force_row_wise`/`force_col_wise`. **Thread count and reduction order are therefore properties of the
allocation, not of the seed** (**MEASURED**: the four keyword arguments above are the complete set).

**The observation agrees.** G's committed null is `5.8223488501140625e-50` — **not zero**. If the
re-unfold were bit-identical the difference would be exactly `0.0`. It is not, so **something in this
chain is run-to-run non-deterministic in-process at a small but nonzero scale**, and this record does
not claim to know which step (that would be a mechanism asserted without a command run against it —
this campaign's catalogued failure, and the reason it is not asserted here).

**That is what makes the whole `ε` construction the wrong instrument.** The quantity being bounded is
the **empirical reproducibility floor of a specific algorithm in a specific execution envelope**, not
the rounding error of a length-`n` sum. A model of the first is what `§6.4`'s *"precision control"*
needs, and this document did not have one.

#### What survives, what is withheld, and what is now required

| | |
|---|---|
| **SURVIVES — the normalizer** | `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` over the reported support. Item 1's argument is untouched: numerator and denominator are the same object, and `sqrt(Tr C_Z)` and the per-bin max stay rejected on the record. **The review's recommendation is explicit — *"keep scale-relative normalization"*** |
| **SURVIVES — §6.4's requirement** | the bound must be scale-relative and fixed before production. Unchanged; not reopened |
| **SURVIVES — the sensitivity controls** | the three channels and their `5.00e-41` tightest evaluated limit stand as what they always were: **candidate inputs to `S` below**, never a derivation of what is achievable |
| **WITHHELD** | **`ε = n_iters · n_rep · eps`, and the number `1.1873e-11` with it.** Not adopted, not proposed, and not to be cited from this document as a criterion |
| **WITHHELD with it** | the `8.9×` margin claim, which was `ε` divided by a transferred figure. With `ε` gone the margin has no numerator |
| **REQUIRED** | the two-quantity structure immediately below, which **replaces rev. 16's `min(achievable, acceptable)`** |

#### ⚠ REV. 17 — `min(achievable, acceptable)` IS WITHDRAWN. It inverted a constraint this document had already stated correctly

**Rev. 16 wrote that the bound is *"the SMALLER of what the computation can achieve and what the science
can tolerate."* That is the same mistake §3.6 warned against, wearing a formula, and the contract review
is right to call it acceptance-blocking.** An observed reproducibility floor is **not** an acceptance
tolerance, and taking a minimum turns it into one mechanically — which is precisely the step §3.6a
forbids: *"a measured process-to-process floor… tells you what repeatability is **achievable**; it does
not tell you what error is **scientifically acceptable**… It may bound `ε` from **below** as a
feasibility constraint; it cannot justify `ε`."*

**`min` uses that floor as an UPPER bound. §3.6a says it is a LOWER one. Rev. 16 inverted the direction
of a constraint written two sections earlier in its own document**, and did it while quoting the
paragraph that says so.

**Both branches of the minimum fail, and each fails in a shape this repository has catalogued:**

| case | what `min` would set | what actually happens |
|---|---|---|
| `B < S` — the envelope is comfortably inside the science's tolerance | `ε = B`, the **feasibility floor** | the gate sits at the floor, so **correct runs fail** at whatever rate `B`'s coverage leaves. A guard that fires on correct runs |
| `B > S` — the envelope is **not good enough** | `ε = S` | **every** correct run fails, because the computation cannot achieve `S`. And the real finding — *the envelope is inadequate* — is silently converted into a threshold nobody can meet |

**THE DEFENSIBLE STRUCTURE, and it is the review's:**

    B  =  an OPERATING-ERROR BOUND on this algorithm in this execution envelope,
          with its assumptions and its confidence stated.
    S  =  an INDEPENDENTLY JUSTIFIED SCIENTIFIC CAP on how much CV movement is tolerable.

    REQUIRE   B <= S.
    Then      epsilon is JUSTIFIED WITHIN [B, S]  --  argued, never taken as an endpoint.

**Three things follow, and each is a change in what the failure of this criterion would MEAN:**

1. **`B ≤ S` is a precondition, not an arithmetic step.** If it fails, **the proposed execution envelope
   is not demonstrated adequate** — that is a finding about the envelope, and the responses to it are to
   change the envelope, revisit `S`, or stop. **It is not a tolerance to adopt.**
2. **`B` and `S` are established by different work and neither substitutes for the other.** `B` is
   measured or designed (below); `S` is argued from what the covariance is used for — the same argument
   `D1`'s thresholds now wait on, which is why §3.7a and §3.7b are not independent questions.
3. **`ε` is argued inside the interval.** Where in `[B, S]` it sits is a judgement about how much margin
   to leave against an envelope that will requeue, run at different thread counts and outlive this
   specification. **A number read off either endpoint is not that judgement.**

**JOSEPH'S QUESTION, RECORDED VERBATIM AS THE THING THAT MUST BE ANSWERED:** *"What reproducibility
tolerance is justified for this exact algorithm and execution envelope, subject to an independently
justified scientific sensitivity limit?"* **Read against the structure above, that question already has
the right shape — `B`, then `S`, then a tolerance justified subject to both — and rev. 16 answered it
with a minimum.**

#### The bounded experiment that could establish `B` — PROPOSED, NOT RUN, AND ⚠ REVISED IN REV. 17

**Rev. 16 called this *"the only route to a defensible `ε`."* That claim is WITHDRAWN — the review did
not establish it, and this lane asserted it.** Three routes are named below and none is privileged.
Rev. 16's version of the control also had three gaps, all three now stated rather than repaired away.

##### ⚠ GAP 1 — a within-envelope null does not measure a between-envelope shift

**The most serious of the three, because rev. 16's two-arm design looked like it addressed portability
and does not.** `r_null` compares two re-unfolds **inside one process**. Run the control at two thread
counts and you get **two within-envelope nulls**, and *both can be essentially zero while the two arms'
CVs differ from each other*. Reproducibility within an envelope and agreement across envelopes are
**two different quantities**, and rev. 16 measured the first while claiming the second.

**The fix is a second statistic, and rev. 16's own persistence requirement is what makes it available:**

    r_cross  =  || x_cv^(A) - x_cv^(B) ||  /  || x_cv^(A) ||      [ A, B two declared envelopes ]

Because Z's writer now persists `x_cv` (§3.7a's auditability requirement), the cross-arm vectors exist
to be compared. **Which statistic the control needs is decided by the claim:** if the claim is *"Z
reproduces within a fixed envelope"*, `r_null` alone; if it is *"Z's CV is portable across the envelopes
a requeueing campaign will actually see"*, `r_cross` is required and `r_null` does not substitute.

##### ⚠ GAP 2 — `4` repeats had no justification, and two arms do not prevent tuning

**Rev. 16 wrote that `4` is *"the smallest count from which a tail is arguable at all"*. That is not a
justification, it is a shrug with a number attached, and it is withdrawn.** What a sampling design needs
before it is proposable:

| | |
|---|---|
| **the objective** | what is `B` — a maximum over repeats? a one-sided upper tolerance bound at a stated **coverage** and **confidence**? These are different quantities and they need different counts |
| **the sampling assumptions** | are repeats independent? Repeats **inside one job** share a node, a library load and a page cache; repeats **across jobs** do not. **An i.i.d. assumption over the first is unlikely to hold, and the design must say which it makes** |
| **what prevents tuning** | **not the arm count — rev. 16 implied it was.** What prevents it is **predeclaring the estimator of `B`, the repeat count and the envelopes BEFORE any run, and committing not to revise them afterwards.** Two arms observed and then summarized however the numbers fall is a threshold tuned to its own data |
| **the subject** | **⚠ AND THIS ENGAGES §6.4 DIRECTLY.** If the control runs on **Z's own bank**, its nulls are Z's nulls, and §6.4 forbids reading the bound off them. If it runs on a **different** bank, it is a **transfer** and needs a transfer argument. **Neither is chosen here; both must be, and the first needs Joseph's ruling rather than this lane's reading of §6.4** |

##### ⚠ GAP 3 — the cost was priced against the wrong operation on the wrong partition

**Rev. 16 priced `8` invocations at `≈1.45` GPU task-h each for `≈11.6` GPU task-h. Both halves are
wrong, and this document had already recorded the correction once.**

| what rev. 16 assumed | measured, at this base |
|---|---|
| an invocation is *"`2` CV unfolds"* | **it is not.** `do_combine` (`unified_throw_cov.py:363`ff) loads the bank, globs and loads every throw slab, assembles `C_uni`, `C_block` and `C_cross` and writes three `10,694²` `TH2D`s. The `--null` block at `:513-523` is **one step inside that**, and an invocation charges the whole combine |
| the partition is GPU, at the `43.5`-min arm-3 per-task prior | **the combine is a CPU job.** `sbatch_uthrow_combine_5d_fast.sh:4` is `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G --time=03:00:00`, and its own header (`:9`) says *"`--null` repeats CV at the identical seed and must be zero"* |

**⚠ AND THIS IS A REPEAT OF A CORRECTION ALREADY IN THIS DOCUMENT, WHICH IS THE PART WORTH RECORDING.**
§0.0's rev.-2 correction row 10 reads: *"`--null` runs in the **CPU** combine step; the `43.5`-min basis
is a **GPU** arm-3 per-task time"* — found by this lane, applying the reviewer's own rule to a line the
reviewer had not named. **Rev. 16 then priced a new row off exactly that basis.** §5.2 leaves the
cause-4 second CV unfold **unpriced** for this same reason, and §7 items 5 and 13 name the missing
measurement. The correction was made, recorded, and not carried.

**SO THE COST IS UNPRICED, and that is the honest entry:**

- **spend — UNRESOLVED.** No CV-unfold time on the **CPU** partition exists in this tree (§7 item 13),
  and the combine's own arm has no recorded actual either (§5.2's combine row: `grep` over `RUNS.tsv`
  returns **0** rows against a positive control). **Two unmeasured terms, not one.**
- **reservation bound — `3` h per invocation** at the launcher's own `--time=03:00:00`, `--ntasks=1`, so
  `n` invocations reserve `3n` CPU task-h. **A request bounds an attempt, not a completion** (§5.2's
  standing rule), and `n` is undetermined until Gap 2 is answered.
- **a GPU control is admissible but is not this one.** The review says so explicitly: *"A separately
  proposed GPU control is possible, but its execution path, envelope and complete cost must be stated."*
  **This document states none of the three for a GPU path, so it does not propose one.**

##### The three routes to `B`, none privileged

| route | what it costs | what it would give |
|---|---|---|
| **(i) PIN THE ENVELOPE IN CODE, and make `B` a design property rather than a measurement.** `make_estimators` (`omnifold_nn_core.py:143-148`) sets `random_state` and **nothing else**; LightGBM exposes `num_threads`, `deterministic` and `force_row_wise`/`force_col_wise` | **Tier 2 — code, no compute.** Whether pinning them makes two re-unfolds bit-identical **here** is untested, and testing it is itself cheap | potentially the strongest outcome: a `B` that is **argued from the configuration** rather than sampled, and an envelope that no longer varies with the allocation |
| **(ii) the control above**, with all three gaps answered | unpriced (above) | a measured `B` with a declared envelope, coverage and confidence |
| **(iii) ESTABLISH `S` FIRST.** If the scientific cap is loose enough that **any** plausible `B` sits below it, `B ≤ S` is discharged without measuring `B` precisely | **zero compute.** It is an argument, and it is the same argument `D1` waits on | `B ≤ S` satisfied by bounding, with `ε` then argued from `S`'s side |

**Route (i) deserves the first look and this record says why rather than ranking it silently:** it is the
only one that can *reduce* the quantity instead of *measuring* it, it costs no compute, and it addresses
Gap 1 at the source — an envelope that is pinned does not have a between-envelope shift to bound.
**It is named, not recommended as a decision.**

**No authorization is sought here and none is implied.** `D-RESOURCE` does not exist, §4 row 3's gate is
shut, and no row above is in §5.8b's production block.

#### Item 4 — presence, finiteness, and the abort rule

`fixed_seed_null_checked` must be **present and `1`**; `fixed_seed_null_norm` must be **present and
finite**; `‖x_cv‖` must be **present, finite and strictly positive** (a zero denominator is an abort,
never a pinned ratio — the opposite of §1.3a's `g = 1` rule, because here a zero denominator means the
CV is empty). **Any failure ABORTS the run**; none of them is recorded as a note. The writer already
distinguishes *"checked and zero"* from *"not checked"* (`unified_throw_cov.py:553-563`, **MEASURED**),
and Z inherits that and fails closed on `checked == 0`.

#### ⚠ One requirement §3.6a did not anticipate — and REV. 16 CORRECTS THE OPERAND IT PROPOSED

**The requirement is right and the route rev. 7–15 gave it was wrong.** Both halves are stated, because
the requirement survives and the route does not.

**THE REQUIREMENT, unchanged and re-measured at this base.** `unified_throw_cov.py:540-579` writes
`C_unified`, `C_blocksum`, `C_cross`, `hJointMeanShift`, the two seeds, the offset provenance and
`fixed_seed_null_norm` — **and it does not write `x_cv`.** The vector is computed at `:369-371`, carried
in the return dict as `x_cv_reported` at `:586`, and **dropped**. So the denominator of the ratio this
criterion grades is not recoverable from the product the criterion grades, and a validator could only
read the producer's own number back and compare it with itself — the exact shape §1.3b rejected for `g`.

**THE ROUTE REV. 7–15 PROPOSED — recompute `‖x_cv‖` from the production ROOT's `hXSecND_flat` — IS AN
OPERAND MISMATCH, AND THE REVIEW IS RIGHT.** Measured here, four ways, each independent:

1. **The numerator's two operands are produced in-process by the same estimator.** `x_cv` (`:369`) and
   `x_cv2` (`:514`) both call `_xsec_for_weights`, which in the 5D path **is** `_xsec_for_weights_5d`
   (`unified_throw_cov_5d.py:89`). `hXSecND_flat` is written by **a different job**. Dividing an
   in-process difference by a separate production's norm mixes two populations in one ratio — this
   campaign's most-repeated error class, caught in the same subsection that already records it catching
   this document once.
2. **The adopter checks CARDINALITY, not identity, and not even the mask.** `adopt_unified_5d.py:116-121`
   opens the production ROOT, reads `hXSecND_flat`, applies `xfull > 0`, and asserts
   `x.size == n`. **Two different supports of the same size pass it.** The review says *"checks
   dimensions, not vector identity"*; measured, it is weaker still — it does not check the **mask**.
3. **The key name is a definite description with more than one producer.** `hXSecND_flat` is written by
   `sweep_bank.py:271` into *"the sweep's own"* product as well as by the standard-P4 chain
   (`run_p4_unfold_std.sh:65` validates it at **`65856`** bins). And it lives on the **65,856 grid**
   while every covariance lives on the **10,694 support** (`mii_anchor_comparator.py:869`,
   **MEASURED**). *"The production ROOT's `hXSecND_flat`"* therefore needs a path and a digest before it
   names anything — which this document's own catalogued rule already says.
4. **⚠ AND THE SHARPEST ONE: the external denominator PRESUMES THE ANSWER.** The null asks whether the
   CV re-unfold reproduces. Taking the denominator from a separately produced CV assumes those two
   productions agree at the norm level — which is the same determinism property, one level up.
   **A file hash cannot resolve this.** It binds the production ROOT's bytes; it says nothing about
   whether that vector equals the throw run's internal `x_cv`.

**THE REMEDY THE REVIEW PRESCRIBES — *"persist the actual null-reference vector and support"* — and it
is cheap enough that nothing else needs weighing.** The producer already holds both:

- **persist `x_cv` on the full grid** — `65,856` float64 = **`527` kB** — together with the **support
  predicate's result** (`rep`), so `n_rep` is derived by the validator rather than trusted;
- **persist `x_cv2` on the same grid** — another **`527` kB** — so the **numerator** is independently
  reconstructible too, not just the denominator;
- **total `1.05` MB against the throw product, and ⚠ REV. 17 CORRECTS THE OPERAND REV. 16 USED.** Three
  `10,694²` `TH2D`s are **`2.74` GB** (**DERIVED**: `3 × 10694² × 8` B), and the measured size of the
  existing `uthrow` product is **`2,668,021,041` B = `2.668` GB** (**MEASURED**, §5.9's digest table —
  the right number was already in this document). **Rev. 16 wrote `≈41` GB, which is a different
  object**: the **45-component** band family (`13 V + 5 A + 27 R` at `0.915` GB each = `41.17` GB) and
  G's `combined_source` (`41,436,632,945` B = `41.44` GB, §1.1). **The fraction is `3.9e-4`, not
  `2.6e-5`** — still negligible, **and the conclusion surviving does not make the operand right.** It is
  this lane's catalogued failure: the check was correct about the wrong object.

Then the validator recomputes `rep`, `n_rep`, `‖x_cv‖`, `‖x_cv2 − x_cv‖` and `r_null` **from the
persisted vectors**, and the producer's recorded scalar is checked **against** that reconstruction
rather than serving as its input.

**§3.3'S REJECT CONDITIONS CHANGE ACCORDINGLY — `11b` IS RESTATED AND `11c` IS NEW:**

- **`11b` (restated).** *The null ratio cannot be independently reconstructed **from the persisted
  `x_cv`, `x_cv2` and support predicate in Z's own throw product**.* This is the operand the numerator is
  actually taken over.
- **`11c` (new, and CONDITIONAL BY CONSTRUCTION).** *An external cross-check against a named production
  ROOT's `hXSecND_flat` is reported **only** where that vector's identity with the persisted `x_cv` has
  been **established elementwise**, and it is never a substitute for `11b`.* Where identity is not
  established the field is written **`UNRESOLVED`**, never omitted and never silently approximated.

**This does not close `PM-6` and does not pretend to.** `‖x_cv‖` for **G** remains unmeasured — G's
product does not persist the vector either, which is the same defect observed from the other side — and
§7 item 17's binding of G's production-CV input is still what `PM-4` waits on. **What changes is that
Z's own null becomes auditable from Z's own product, which is the only thing a forward requirement can
deliver.**

#### What §3.7a does NOT do

It does not regrade G — §6.4 says so and this is a forward requirement. It does not change the measured
`5.8223488501140625e-50`. It does not claim the current guard is *wrong about G's product*: §3.1a's
finding is that the guard cannot fail, not that the product is bad. **And it is not approved:** the
normalizer, the persistence requirement and the two reject conditions are all in §6.7's packet.

**⚠ AND AFTER REV. 16 IT DOES NOT SUPPLY A NUMBER AT ALL.** `ε` is withheld, so §3.7a completes three of
§3.6a's four items and **leaves the third open with a named route**. That is a smaller claim than rev.
7–15 made and it is the accurate one: **§3.6a is no longer answered, and §3.3 condition `4c` therefore
still bites** — a run against an underived bound is itself a reject condition, which is the mechanism
that makes this state safe rather than merely disclosed.

### 3.7b `(cause 3, Z)`'s joint-baseline acceptance packet — §3.6b's five items, FOUR ANSWERED AND THE BOUNDARIES WITHDRAWN IN REV. 16

#### Item 1 — the member, and it is MEASURED rather than designed

**§3.6b called this *"the design"*. It is not: the mechanism already exists in the launchers, and this
lane found it by reading them rather than by proposing one.** Exactly **seven** production launchers
apply one shared environment variable, and its default reproduces the archive:

| arm | launcher, `file:line` | baseline it offsets |
|---|---|---|
| 1 bootstrap | `sbatch_bootstrap_5d_gpu.sh:326` | `42 + ${MNV_EST_SEED_OFFSET:-0}` |
| 2 seed split | `sbatch_seedscan_split_5d.sh:307` | `42 + …` |
| 3 detector | `sbatch_unfold_5d_detector_bkgaware_gpu.sh:329` | `42 + …` |
| 4 sweep | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:318` | `42 + …` |
| 5 uthrow run | `sbatch_uthrow_run_5d_fast.sh:316` | `1000 + …` |
| 6 uthrow block | `sbatch_uthrow_block_5d.sh:337` | `1000 + …` |
| 7 uthrow combine | `sbatch_uthrow_combine_5d_fast.sh:134` | `1000 + …` |

**An eighth file names the variable and REFUSES it:** `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh:164-165`
fails with *"MNV_EST_SEED_OFFSET must be unset for the estimator-seed scan"*. **That is an independent
mechanical confirmation of §6.3's ruling** — the narrow fixed-draw scan is a *different object* from the
joint-baseline family, and the code already refuses to conflate them.

**So a member is:** one complete seven-arm production round at one integer value of
`MNV_EST_SEED_OFFSET = k`, assembled through the standard-P4 lateral stages and both centering variants
into a complete `C_Z^(k)`. **`k = 0` reproduces the archive's seeds — and that is arithmetic plus a
measurement, not the launcher comment's say-so.** Each hook's comment claims it, but the check is that
`42 + 0` and `1000 + 0` equal the values the **unhooked** sibling launchers hardcode:
`sbatch_sweep_bank_5d_run.sh:17` passes `--estimator-seed 42` and `sbatch_uthrow_run_5d.sh:22` passes
`--estimator-seed 1000` (**MEASURED**). So **Z's own build is member `k = 0`** and costs nothing extra.

**Two consequences, and the second is a cost finding.**

1. **The implemented family is the DIAGONAL `(42+k, 1000+k)`, not a 2-D grid.** One variable moves both
   sides by the same integer. §6.3's word is *"jointly"*, which the diagonal satisfies; if a **grid** —
   sweep and throw offset independently — is what is wanted, that is a **second environment variable and
   a launcher change**, i.e. **code, not compute**, and it must be decided before the offsets are
   declared. §6.7 puts it.
2. **No arm can be reused across members, so there is no cheap member.** This lane's first reading was
   that arms 1 and 2 produce `C_stat` and `C_ML` and could be held fixed, cutting a member's cost. **That
   reading was wrong and the launchers refute it:** both take `42 + OFFSET` as their *estimator* seed. A
   member is the whole round. **The error is recorded rather than quietly dropped**, because it is this
   lane's recurring one — an unchecked number that favoured the argument being made.

#### The population, stated before the statistic because it determines which statistic is admissible

**The population is the FINITE DECLARED OFFSET SET `K = {0, k₁, …, k_{N−1}}`, predeclared in full before
the first task, and no inference is made to a distribution over offsets.** This is not a convenience;
it is `PREDECLARE-20260901-cause3-mii` §1's own position — *"The population is the finite declared set,
not an inferred distribution"* — and it transfers because the same thing is true here: nobody has a
model of the offset population, and `N` will be small (below).

**⚠ THE REASON REV. 7–15 GAVE FOR THE MAXIMUM WAS WRONG, AND THE REVIEW CORRECTS IT.** Rev. 7–15 wrote
that with a finite declared population *"a sample standard deviation is **inadmissible**"*. **It is
not.** A standard deviation over a finite declared set is a perfectly well-defined descriptive statistic
of that set — and **this very packet computes a finite-set covariance from a finite declared throw
ensemble**, so a blanket inadmissibility rule would strike out the object being graded. **The claim is
withdrawn.**

**The maximum is right for a different and better reason: it is the statistic the CLAIM requires.** The
claim `D1` supports is *"**no** declared offset moves the printed value **beyond its declared
limit**"* (⚠ verb corrected in rev. 17) — a statement quantified over
**every** member of `K`. **A universally quantified claim is graded by the extremum, not by a spread**;
an SD can be small while one member is far out, and the claim would be false with the gate green. **The
statistic follows from the quantifier in the sentence, not from the finiteness of the set.**

The SD and the full per-member table are **reported** as descriptive summaries; they grade nothing.

#### Item 2 — the two statistics, over §6.3's ruled subject

Both are taken over the **assembled** covariance `C_Z`, which §6.3 fixes and §3.6b item 2 records that
rev. 3 wrongly reopened. Both are dimensionless; both denominators are Z's **own as-built `k = 0`**
member, named in the same sentence as their numerators.

    s_agg   =  max_{k in K}  | sqrt(Tr C_Z^(k)) - sqrt(Tr C_Z^(0)) |  /  sqrt(Tr C_Z^(0))

    q^(k)   =  median_{i in support}  ( sigma_i^(k) / x_i )        [ the printed per-bin quantity ]
    s_med   =  max_{k in K}  | q^(k) - q^(0) |  /  q^(0)

`σ_i^(k) = sqrt((C_Z^(k))_ii)`; `x_i` is the reported CV, **held fixed at `k = 0`** — the central value
is not a covariance-construction quantity and §1.3 fixes it, so varying it here would measure a
different thing.

**Both are EXACT, and that is the point.** Each is the relative change in a quantity that is itself
printed, so neither needs a model connecting a statistic to a reported number. §3.6d's ordering rule —
statistic first, boundary second — is satisfied by construction.

**Reported beside them, gating nothing:** the per-member table of `√Tr C_Z^(k)` and `q^(k)`; the sample
SD of each; and **the per-bin movement distribution** `m_i = max_k |σ_i^(k) − σ_i^(0)| / σ_i^(0)` with
its median, `p90`, `max` and argmax bin.

#### Item 3 — ⚠ OPTION (i) IS NOT RECOMMENDED IN REV. 16; the per-bin distribution stays a DIAGNOSTIC

§3.6b requires two legs and requires the second to **bind independently**, on the predeclaration's
reason: *"the same trace can be diffuse or concentrated, so the per-bin leg is independently binding."*
`s_agg` and `s_med` are the two legs, and they can disagree — a trace can hold still while the per-bin
median moves, and the converse. **(And §3.7d, new in rev. 16, shows that both together still miss a
third thing: correlations. That is a separate requirement, not a variant of this one.)**

**THE PER-BIN LEG HAS A GAP, AND REV. 7–15 MISDIAGNOSED WHAT KIND OF GAP IT IS.** `s_med` is the
movement of a **printed median**, so it is an aggregate. A criterion that binds on **individual bins**
would need a per-bin tolerance — and rev. 7–15 reasoned: the note prints no per-bin uncertainty, no data
release exists, therefore the only available closure is to borrow the printed median's format.

**⚠ THAT REASONING IS REJECTED, AND THE REVIEW'S SENTENCE IS THE CORRECTION: *"A missing data release
does not prevent specifying a scientifically motivated per-bin tolerance."*** The two are unrelated.
A per-bin tolerance is a statement about **how much movement matters**; a data release is a statement
about **how movement would be displayed**. **Rev. 7–15 answered a formatting question because that was
the one this checkout could answer** — the same failure item 4 (B) records, in the same packet, one
subsection apart. **`median_i(m_i)` is a legitimate descriptive statistic; applying the printed median's
precision to it is a new tolerance choice, not a consequence of that summary's formatting.**

**THE DISPOSITION, per the review and approved:**

| | |
|---|---|
| **NOT ADOPTED** | option (i) — the model-dependent third leg at `δ_med`. **Disclosing the uniform-movement assumption does not justify it**, and rev. 7–15 recommended it essentially because its assumption was disclosed |
| **RETAINED** | the **per-bin movement distribution** `m_i = max_k \|σ_i^(k) − σ_i^(0)\| / σ_i^(0)`, reported with its `median`, `p90`, `max` and **argmax bin index** — which is what makes concentration visible. **A diagnostic, gating nothing, pending an answer** |
| **THE ANSWER IT WAITS ON — JOSEPH'S QUESTION, VERBATIM** | *"What per-bin movement is acceptable, in what fraction of bins, and why?"* **Note the shape of it: a tolerance AND a coverage fraction.** A per-bin criterion has two numbers, and rev. 7–15's option (i) had one — a median is the `50%` fraction chosen by default rather than by argument |
| **AND IF A THIRD BINDING LEG IS EVER ADOPTED** | **the outcome branches must incorporate its failure.** Rev. 7–15's branch table checks exactly two legs, so adopting a third would have left a MET branch that ignores it. **Fixed structurally in item 5 below**, before any third leg exists |

**Until that question is answered the two exact legs are the gates and the distribution is reported.**
That is a weaker contract than the narrow scan's, and this record says so plainly rather than claiming
parity — **and it is now weaker in a second, named way as well: §3.7d.**

#### Item 4 — ⚠ THE THRESHOLDS ARE WITHDRAWN AS ACCEPTANCE CRITERIA IN REV. 16, AND THE RULE BEHIND THEM WAS FACTUALLY WRONG

**Two separate things are wrong with rev. 7–15's item 4, and only the second was flagged. Both are
corrected here.** The statistics and the direct normalization **survive** — the review's recommendation
is explicit that they do. What does not survive is the claim that a number derived from **macro
formatting** is a **scientific acceptance criterion**.

##### (A) ⚠ A FACTUAL ERROR: half a display unit does NOT guarantee an unchanged printed value

**The review's counterexample, re-measured here rather than accepted:** at three significant figures,
`1.234 → 1.236` prints `1.23 → 1.24`, and the change `0.002` is **below** the half-unit `0.005`.
**Confirmed.**

**And it fails in the other direction too, which the review did not need to say and this document does,
because a one-directional check is this lane's catalogued blind spot.** `1.2251 → 1.2349` changes by
`0.0098` — **nearly twice** the half-unit — and prints `1.23 → 1.23`, unchanged. **Confirmed by the same
measurement.**

**So `|U′ − U| ≤ u/2` is NEITHER NECESSARY NOR SUFFICIENT for display invariance.** The reason is
one sentence: **a rounding boundary is a property of where the mantissa sits, and a bound on the change
does not know where it sits.**

**How often it disagrees, derived and then checked.** For a value uniform within its decade and a change
uniform on `[0, u)`, the position within the rounding bin is uniform and independent of the change, so
`P(change < u/2 AND the print moves) = ∫₀^{1/2} d·dd = 1/8` and
`P(change > u/2 AND the print holds) = ∫_{1/2}^{1} (1−d)·dd = 1/8` — **exactly `12.5%` in each
direction** (**DERIVED**). A `200,000`-pair simulation at 3 s.f. returns `12.5%` and `12.4%`
(**MEASURED**). **The rule is wrong about one pair in four, split evenly between waving a change
through and flagging one that never happened.**

**What `δ = (half the last printed unit)/(the printed value)` actually is:** a **scale** — the order of
magnitude at which the printed representation stops resolving. It is a reasonable thing to quote. **It
is not a criterion, and rev. 7–15 used it as one.**

##### (B) THE LARGER FINDING: formatting cannot answer the question that was asked

**JOSEPH'S QUESTION, RECORDED VERBATIM:** *"Is acceptance intended to protect only these displayed
summaries, or scientifically relevant uses of the assembled covariance?"*

**Choosing three or four significant figures does not establish how much estimator-baseline sensitivity
is scientifically acceptable.** And the two macros the format was read off are **defined and never
printed** (measured, §3.7b's own positive control) — so rev. 7–15 derived an acceptance level from the
formatting of numbers that **appear nowhere**, and then called the result a precision target. **Unused
historical macro formatting supplies neither a scientific justification nor a downstream sensitivity
assessment.** That is the review's sentence and it is exactly right.

**⚠ AND THE FAILURE HAS A NAME THIS LANE ALREADY CARRIES: measurability chose the specification.** The
formatting question was the one that could be answered with a `grep` in this checkout. The scientific
question — *how much movement matters* — could not be, so the document answered the cheap one and
presented it in the slot the hard one belonged in. **A `48×` tightening arrived at by that route is not
conservative; it is unmoored, and it happens to point the safe way.**

##### (C) WHAT IS WITHDRAWN, WHAT IS RETAINED, AND WHAT IS REQUIRED

| | |
|---|---|
| **RETAINED — the two statistics** | `s_agg` and `s_med`, each the maximum relative change over the declared offset set. Item 2 is untouched |
| **RETAINED — the direct normalization** | `\|U′ − U\| / U`, not quadrature. §3.6d's argument stands and is **strengthened** below, not weakened |
| **RETAINED — as a quoted scale only** | `δ_agg = 8.6059e-4` and `δ_med = 3.7425e-4` at the format prior. They may be reported as *"the resolution of the historical printed format"*. **They may not be cited as acceptance boundaries, from this document or anywhere downstream of it** |
| **WITHDRAWN** | **`s_agg ≤ 0.0861%` and `s_med ≤ 0.0374%` as scientific acceptance criteria.** Not adopted, not proposed, not a default |
| **REQUIRED — (1)** | a **use-based justification**: how much estimator-baseline sensitivity is scientifically acceptable for the assembled covariance, and **why**, stated before any number |
| **REQUIRED — (2)** | an **explicit disposition of correlation sensitivity** — §3.7d, new in rev. 16, because neither statistic can see it |

##### (D) IF LITERAL DISPLAY INVARIANCE IS WHAT IS INTENDED, THERE IS AN EXACT TEST AND IT NEEDS NO `δ`

**The review's third recommendation, and it is worth stating precisely because it is strictly better
than the rule it replaces.** If the claim to be supported really is *"the printed value does not
change"*, then **test rounding equality**:

    for every k in K:   fmt(U^(k), p)  ==  fmt(U^(0), p)          [ p = the declared precision ]

**Exact. Computable. No threshold, no `δ`, no model, and it cannot be wrong in either direction —
because it evaluates the predicate the claim names, instead of a bound that correlates with it.**

**And its two properties must be stated in the same breath, or it becomes the next mistake:**

- **It is discontinuous.** A pair straddling a rounding boundary fails at arbitrarily small movement.
- **It is origin-dependent.** The *same physical stability* passes or fails depending on where the
  mantissa happens to sit — which is what makes it a **display** criterion.

**So it answers *"does the printed number move?"* exactly, and it answers *"is the covariance stable?"*
not at all.** Both may be wanted; they are two claims and they need two criteria. **This lane proposes
neither as the answer** — that is `D1`, and the question above is the one that decides it.

##### (E) THE `48×`/`73×` CONTRAST, AND WHAT IT IS NOW A CLAIM ABOUT

Re-derived here from the predeclaration's own numbers, unchanged and still exact:
`δ = 0.005/5.81 → sqrt(2δ+δ²) = 4.1496%` and `δ = 0.005/13.36 → 2.7361%`, reproducing the predeclared
`4.15%` and `2.74%` — which is also how the two printed quantities behind those thresholds were
identified.

**What that arithmetic shows and all it shows: over the SAME `δ`, quadrature is `48.2×` and `73.1×`
looser than the direct form.** It is a statement about **two formulas**, not about the right acceptance
level. **Rev. 7–15 let it read as though the tighter number were therefore the correct one. It is not:
both are `δ`-derived, and `δ` is now withdrawn as a criterion, so the contrast survives as a reason to
be careful about formula choice and as nothing else.**

**⚠ AND ONE CORRECTION TO THE FORMULA ARGUMENT ITSELF, from the review's nonblocking list.** Rev. 4–15
wrote that *if* Joseph decided baseline variation should enter the budget, *"quadrature would become
correct."* **That is wrong and it is withdrawn.** Quadrature needs **independence**, and **budget
adoption alone does not establish independence** — a contribution can be adopted into a budget and still
be correlated with what is already in it. So the direct form's standing is **stronger** than rev. 4–15
claimed: quadrature is unavailable under the operative rulings (`PREDECLARE-20260901-cause3-mii` §5,
§1.3a property 3), **and** it would remain unavailable after a budget-adoption decision until
independence were separately demonstrated. **The burden §3.6d places on quadrature does not move.**

##### (F) THE PRECISION TARGET IS STILL A DECLARATION, AND IT IS NOW A SMALLER PART OF THE QUESTION

Unchanged and re-measured: `values.tex:113` `\gbdtFiveAdoptTrace = 5.81e-38` is **three significant
figures**, `values.tex:111` `\gbdtFiveBlockMedian = 13.36` **%** is **four**; **both macros are defined
and never used**, against a positive control in which `\uqMedian` / `\sigTwoD` / `\ratioTot` appear in
**six** files; and the values in them are J's, which are quarantined (§1.1; QUOTED `0 of 7`).
`PREDECLARE-20260901-cause3-mii`'s own rule governs any number that is ever derived from a format:
*"if the printed precision changes before execution, these numerical thresholds are void and must be
redeclared before the run."*

**Joseph must still declare the precision at which Z's two quantities will be reported** — it is needed
for the rounding-equality test in (D) and for any reported `δ`. **But it is no longer the thing that
sets acceptance**, and rev. 7–15 was wrong to present it that way.

#### Item 5 — the branches, mapped onto `R4`'s six — ⚠ RESTATED IN REV. 16 OVER A LEG SET, NOT A HARDCODED PAIR

**THE DEFECT THE REVIEW FOUND, fixed structurally rather than by editing a number.** Rev. 7–15 wrote
branch 3 as *"**both** `s_agg ≤ δ_agg` **and** `s_med ≤ δ_med`"* and branches 4–6 as the three failure
combinations of that pair. **The pair was hardcoded.** So the moment any third binding leg were adopted
— item 3's per-bin leg, or §3.7d's correlation leg — **the MET branch would have ignored it and returned
MET on a failing criterion.** Values right, scope wrong, and a review reading the numbers would pass it:
this repository's catalogued *universal-claim-implemented-as-the-diff* shape. **Fixed here, before any
third leg exists, because that is the only time it is cheap.**

**THE FIX.** Let **`L`** be the **declared binding leg set**, fixed in the predeclaration before the
first task and written into the receipt. Today `L = {agg, med}`; `D1`, `D2` and §3.7d may each add to
it, and **nothing below has to change when they do.**

Evaluated in order; a validity failure dominates every numerical branch.

1. **INCONCLUSIVE / WRONG FOOTING.** Any member fails §2-style footing agreement; the mask or row-order
   digest differs between members; a member's `V`/`R`/`A` partition differs; any `C_Z^(k)` fails a
   §1.3b identity; `x_i` is not held fixed at `k = 0`. **Report no magnitude.**
2. **INCONCLUSIVE / VACUOUS BASELINE VARIATION.** The read-back `est_seed_offset` set is not exactly `K`;
   `est_seed_offset_declared` is `0` on any member (the two-key rule at `unified_throw_cov.py:571-574`
   exists precisely so a baseline that never reached the estimator is readable rather than inferable);
   any two members' product digests collide; any member is missing or non-finite. **A zero spread here is
   evidence the knob never reached the estimator, NOT a favourable result.** This is the execution
   falsifier.
3. **MET.** All validity checks pass and **every leg in `L` passes its declared boundary** — written
   `∀ ℓ ∈ L : s_ℓ ≤ δ_ℓ`, never as an enumeration. Grades only `(cause 3, Z)`'s `M(ii)` and authorizes
   nothing.
4. **NOT MET — AGGREGATE.** Valid, and `F = { ℓ ∈ L : s_ℓ > δ_ℓ }` contains **only** aggregate-class legs.
5. **NOT MET — PER-BIN.** Valid, and `F` contains **only** per-bin-class legs.
6. **NOT MET — MIXED.** Valid, `F` is non-empty and spans more than one class.

**⚠ THE MAPPING IS A CLASSIFICATION, AND THE RECEIPT CARRIES THE SUBSET ITSELF.** `R4`'s six branches
are a **reporting vocabulary** and are not reopened here. But with `|L| > 2` there are `2^|L| − 1`
non-empty failing subsets and only three NOT-MET labels, so a label **loses information**. Therefore:
**the receipt records `L`, every `s_ℓ`, every `δ_ℓ`, and the exact failing subset `F` by name**, and the
branch label is **derived** from `F` by the class rule above rather than reported in place of it.
**Each leg declares its class — `aggregate` or `per-bin` — in the predeclaration**, so the derivation is
mechanical; §3.7d's correlation leg, if adopted, would need its class declared with it.

**A valid large result is NOT a reject condition** (§3.3) — it is branches 4–6, an informative
unfavourable outcome. Non-finite values are branch 1 or 2, never a comparison that happens to return
false. **`F7_FLOOR_MULTIPLE = 2.0` has no role here** and §3.6b's reason transfers unchanged.

**Two limits that must survive into the receipt, in `PREDECLARE` §5's style — and rev. 16 adds a third:**

- **MET means no offset in `K` moved a graded quantity BEYOND ITS DECLARED LIMIT** — ⚠ rev. 17 corrects
  rev. 7–16's *"moved the graded quantities"*, which with a positive `δ_ℓ` claims more than the legs
  test. It is a statement about the declared set,
  not about offsets outside it, and at the `N` §5.8 prices it is **weak evidence of stability** while an
  unfavourable result is **strong evidence of sensitivity**. The asymmetry is real and the receipt
  states it.
- **It measures the diagonal `(42+k, 1000+k)`.** It does not measure sweep-only or throw-only variation,
  their interaction, or any offset off the diagonal.
- **⚠ NEW IN REV. 16 — it is blind to correlations unless `L` contains a leg that is not.** With
  `L = {agg, med}`, a MET result says nothing about `C_Z`'s off-diagonal structure and does **not**
  license the assembled covariance for marginalization, projection or coverage validation. **§3.7d
  states this in full and it must travel with the grade, not sit in a specification the grader may not
  open.**

#### What `N` can be — ⚠ A PLANNING ESTIMATE IN REV. 16, NOT A DEMONSTRATED CAPACITY

**Rev. 7–15 wrote *"the ruled quantity is AFFORDABLE inside `R5` at `N = 4` to `5`."* The review is
right that this overstates what the arithmetic below can establish, and the claim is corrected.** Every
input is a **prior transferred from a different subject**, the CPU column carries a **measured `±58.7%`**
single-arm swing, and §5.2's omitted rows are still outside the sum. **What follows is a planning
estimate. It bounds nothing, and `N = 5` is a proposal rather than a capacity.**

**DERIVED**, from §5.2's spend estimate and the per-arm round-2 actuals, at **TRANSFERRED** per-member
costs measured on a historical seven-arm round rather than a Z member:

| | GPU task-h | CPU task-h | max additional members under `R5` | **`N` total** |
|---|---:|---:|---:|---:|
| one Z build (member `k = 0`) | `55.70` | `86.53` | — | — |
| remaining under `R5` `500`/`500` | `444.30` | `413.47` | — | — |
| per additional member, nominal | `54.90` | `86.53` | GPU `8.09`, **CPU `4.78`** | **`5`** |
| per additional member, arm 5 at its measured `+58.7%` swing | `54.90` | `115.36` | GPU `8.09`, **CPU `3.58`** | **`4`** |

**So the PLANNING ESTIMATE puts `N = 4` to `5` total members inside `R5` at `86.5%` of the CPU
ceiling** — with `R5` §3 charging every failed and retried task in full, and with §5.2's omitted rows
still outside the arithmetic. **The historical `46`/`50`-member design is `5.1×`–`8.7×` over**, and that
comparison is a ratio of two estimates rather than a capacity claim. **The estimate admits no middle**:
the CPU column is the binding one, and it is the column §5.7 measures as carrying at least a `±60%`
single-arm swing. **⚠ REV. 16: none of this DEMONSTRATES capacity.** Every input is a prior transferred
from a different subject, the swing is measured and its direction is not, and the campaign costs and
contingencies §5.8d–e name are outside the sum. **`N = 5` is a proposal to be authorized, never a
headroom that has been shown to exist.**

**That is the design answer §6.3 left open, and it is not this lane's to accept.** A four-or-five-member
maximum-deviation measurement is a real, predeclarable, falsifiable measurement — and it is a **weak**
one, in the specific and stateable sense above. §6.7 puts the choice.

### 3.7d ⚠ EVERY PROPOSED GATE IS BLIND TO CORRELATIONS — NEW IN REV. 16, AND IT IS A REQUIREMENT, NOT A CAVEAT

**This is the contract review's finding and it is the one that reaches furthest, because it is not about
a number — it is about what the two statistics can see at all.** Joseph has approved that it be
dispositioned explicitly.

#### The finding, measured exactly

`s_agg` reads `Tr C_Z`. `s_med` reads `diag(C_Z)`. **Both are functions of the diagonal alone.** Two
covariance matrices with identical diagonals and completely different correlation structure are
**indistinguishable** to both:

| | `√Tr` | per-bin `σ` | median `σ` | **sd of the SUM** | **sd of the DIFFERENCE** |
|---|---:|---|---:|---:|---:|
| `I₂` | `1.414214` | `[1, 1]` | `1.0000` | `1.414214` | `1.414214` |
| `[[1, 0.9], [0.9, 1]]` | `1.414214` | `[1, 1]` | `1.0000` | **`1.949359`** | **`0.447214`** |
| **relative change** | **`0.0`** | — | **`0.0`** | **`+37.8%`** | **`−68.4%`** |

**MEASURED** (`numpy`, at this base). **Both proposed statistics return exactly zero — they pass at any
boundary, including the withdrawn `0.0861%` — while two ordinary derived quantities move by `38%` and
`68%`.** No choice of `δ` fixes this; the statistics do not contain the information.

#### ⚠ AND IT IS LIVE FOR Z, NOT HYPOTHETICAL — the tree already consumes `C_Z` this way

**This is the part that turns a textbook objection into a specification defect, and it is measured in
this checkout.** `project_cov_nd.py:2-11` exists to compute

    C_low  =  M C_high Mᵀ            [ "P7 covariance marginalization" ]

where `M`'s nonzero entries are *"the product of the bin widths of the DROPPED axes, grouped into the
destination bin"* — **a width-weighted SUM over cells**. Marginalizing the assembled 5D covariance onto
4D, or onto `(E_avail, W)`, is **exactly the `uᵀ C u` functional the table above breaks**, and the
module names two already-validated instances of it: `eavail_generator_significance.py:83-89` (4D →
`E_avail`) and `eavailW_covariance.py:290-304` (5D → `(E_avail, W)`). `coverage_valid_nd.py:20` consumes
a `C` against a CV for coverage validation, which is another off-diagonal-sensitive use.

**So a `(cause 3, Z)` MET result under rev. 7–15's packet would have licensed nothing about the
marginals this repository actually builds from the object it graded.** The gates would have been green
and the projected 4D uncertainty could have moved by tens of percent. **That is a stability claim the
criterion cannot support, made about the exact use the code base has.**

#### The disposition is Joseph's, and both admissible answers are named

**JOSEPH'S QUESTION, RECORDED VERBATIM:** *"Is acceptance intended to protect only these displayed
summaries, or scientifically relevant uses of the assembled covariance?"*

**Answer (a) — NARROW THE CLAIM, and write the narrowing where the result is read.** Acceptance protects
the two displayed summaries and nothing else. Then the receipt must carry, in `PREDECLARE` §5's style
and not in a footnote: *"A MET result on `(cause 3, Z)` states that two displayed scalar summaries did
not exceed their declared movement limits. It is **not** evidence that `C_Z`'s correlation structure is
stable, and it does **not** license the assembled covariance for marginalization, projection, coverage
validation or any other off-diagonal-sensitive use."* **⚠ REV. 17 CORRECTS THE VERB.** With a positive
tolerance, *"did not move"* claims something the criterion does not test — the legs bound movement, they
do not detect its absence — and the wrong verb in a receipt is how a bounded result becomes an
unbounded one downstream. **Costs nothing. It is a scope statement — and it is only honest if it
travels with the grade.**

**Answer (b) — ADD A CORRELATION-SENSITIVE LEG.** Three candidates, in ascending order of how much they
assume. **None is derived here, and none has a boundary**, because §3.6d's ordering rule forbids
attaching a number to a statistic before the use-based justification exists:

| candidate statistic | what it sees | what it needs (⚠ priced below in rev. 17 — *"no new members"* is not *"free"*) |
|---|---|---|
| **`s_proj` — the maximum relative change in `√(uᵀ C_Z u)` over a PREDECLARED set of linear functionals `u`** | exactly the quantity the marginalizations compute | the functionals **already exist as code**: the rows of `project_cov_nd.py`'s `M`, plus the all-ones vector. **No new production members** |
| `s_corr` — the relative Frobenius change in the **correlation** matrix `D^{-1} C_Z D^{-1}` | correlation structure with the diagonal divided out, so it cannot be satisfied by the diagonal | one extra matrix per member; arithmetic only |
| `s_eig` — the relative change in the leading eigenvalue | the dominant mode | one `10,694²` eigensolve per member; **the most expensive of the three and the least interpretable** |

**`s_proj` is the one this lane would put first if asked**, because its functionals are the ones the
repository actually applies and because a predeclared functional set keeps it a falsifiable measurement
rather than a search. **It is not recommended here as a decision** — that is `D1`.

#### What this costs — ⚠ CORRECTED IN REV. 17: no additional MEMBERS is not the same as FREE

**Rev. 16 wrote *"zero production, under every option"* and *"the cost is validator code"*. The first
clause is true and the second hides an execution cost, which the contract review is right to name.**
None of the three candidates adds a member, an unfold or a throw — **and evaluating them is arithmetic
on `10,694²` matrices, which is not nothing.** Priced here, per member:

| candidate | incremental I/O | arithmetic | figure |
|---|---|---|---|
| **`s_proj`** | **zero.** The two exact legs already materialize the full matrix — `adopt_unified_5d.py:46-49` reads a `TH2D` through `np.frombuffer`, not bin by bin — so `C_Z^(k)` is already resident when `s_agg` and `s_med` are computed | `M C Mᵀ` with **sparse** `M` (each source cell maps to one destination, `project_cov_nd.py:2-11`) is `O(nnz(C))` = `1.14e8` operations | **seconds** (**DERIVED**) |
| **`s_corr`** | **zero**, same reason | one elementwise divide and one Frobenius norm over `1.14e8` elements, plus `0.92` GB for the second matrix | **seconds**, plus `≈0.9` GB resident (**DERIVED**) |
| **`s_eig`** | **zero**, same reason | one `eigvalsh` on `10,694²`, `O(n³)` ≈ `4e12` flops | **`≈1`–`3` minutes** per member and `≈1.8` GB working memory (**MEASURED-AND-EXTRAPOLATED**: `numpy.linalg.eigvalsh` timed here at `n = 500`/`1000`/`1500`/`2000` and scaled by `n³`; the extrapolation spans `1.1`–`2.7` min across those four anchors, which is the width of the estimate and is reported rather than averaged away) |

**And `s_eig` may be nearly free for a reason worth checking rather than assuming.** §5.2's
inflated-object validation row states that **PSD on the inflated object is an `eigvalsh` on `10,694²`**.
**If** the validator checks PSD that way, the full spectrum is already computed and the leading
eigenvalue is a byproduct. **If** it checks PSD by Cholesky — cheaper, and a reasonable implementation
choice — it is not. **That row is `unpriced` in §5.2, so this is a conditional and not a saving**, and
§5.8f's rule applies: an opportunity is recorded as an opportunity.

**Where these costs live: Tier 2 validator runtime, not `R5`.** §5.8's local timings already put the
validation arithmetic at minutes on a laptop-class machine at the real dimension, and these rows are of
that kind. **They are execution costs and they are named; they are not a production authorization
question.** The `N`-fold multiplication matters though — at `N = 5`, `s_eig` alone is `5`–`15` minutes,
and it is the one candidate whose cost is not negligible.

**And what this section does not do:** it does not reopen §6.3's ruled quantity — the subject is still
the assembled covariance `C_Z`. It adds a **second way of reading** that same object, which is what makes
it admissible without a new ruling. **§3.6b's own reason already pointed here** — *"the same trace can be
diffuse or concentrated"* — and rev. 7–15 answered that with a per-bin leg, which is still the diagonal.
**Concentration across bins and correlation between them are different objects, and the packet had a leg
for only one of them.**

### 3.7c What §3.7 does not do

It approves nothing, opens no cell, grades no leg and takes no decision reserved to Joseph. It does not
reopen `§6.3`'s quantity, `§6.4`'s form, `R4`'s suspension, or the assembly algebra. It proposes no
change to `CRITERIA` §0's vocabulary. It does not authorize the offsets it names, the control read it
names, or any run. **`BEN-381` applies to it in full:** this lane drafted these criteria and re-measured
the evidence under them, so it grades nothing under them.

**And it does not pretend to be complete where it is not — and after rev. 16 it is less complete than
rev. 7–15 claimed, which is stated here rather than left to a reader to notice.** What is UNRESOLVED,
each with its closure named:

| unresolved | what closes it | new in rev. 16? |
|---|---|---|
| the fixed-seed null's **numeric bound** — `ε` withheld | **`B ≤ S`, then `ε` argued within `[B, S]`** (⚠ rev. 17 — rev. 16's `min` is withdrawn). `B` by any of §3.7a's three routes, the cheapest of which is **code, not compute**; `S` by the same use-based argument `D1` waits on | **yes** |
| the cause-3 **acceptance boundaries** — both withdrawn | a **use-based** justification of how much sensitivity is acceptable | **yes** |
| the **correlation disposition** | narrow the claim in the receipt, or adopt one of §3.7d's three candidate legs | **yes** |
| the per-bin **tolerance and coverage fraction** | Joseph's answer to *"what movement, in what fraction of bins, and why"* | restated |
| the printed **precision** Z reports at | a declaration; still needed, for the rounding-equality test and for any quoted `δ` | restated |
| the printed-total **sensitivity channel** | the 5D bin volumes | no |
| `‖x_cv‖` for **G** | a bounded read; **no longer needed for `D4`**, and never was for Z's own product once `x_cv` is persisted | narrowed |

**`§3.7` therefore supplies statistics, normalizations, operands, receipt requirements and falsifiers —
and NO acceptance numbers.** That is the accurate description of it, and §3.3 condition `4c` is what
makes the state safe: **a run against an underived boundary is itself a reject condition.**
---

# 4. DEPENDENCY ANALYSIS — deliverable `RZ(v)(d)`

**The three questions are answered separately for every candidate, and one answer is never allowed to
stand in for another** (`PROMPTS` §2.1): **necessary** — would Z's specification or construction be
*unsound* without it? **applicable** — is the thing it measures a property *Z would share*, or a property
of the artifact it was measured on? **reusable now** — can Z take the evidence *without anyone spending
compute*, because it is already committed or is a measurement rather than a build?

**Nothing in this table creates authority.** Items carrying suspended or absent authorization are flagged
`⚠ AUTH`; naming one a prerequisite does **not** authorize it.

| # | candidate prerequisite | **necessary?** | **applicable?** | **reusable now?** |
|---|---|---|---|---|
| 1 | **A standalone Y construction** (`⚠ AUTH`: needs `D-Y-CONSTRUCT`, `R2(iv)`, which **does not exist**) | **NO.** Y is cause-7-only and built by a different algebra — a lateral-only swap with `C_G` as minuend (§1.3c). Z's cause-7 evidence must be measured on Z's own construction | **as METHOD only.** Y's artifact-identity discipline, receipt field set, migration-census requirement and bidirectional test contract are reused in §1.5 and §3.4. Y's *measurements* are not: Y's `M` is `C_Y` vs `C_G`, an object Z does not build | **method: YES, zero compute.** **product: N/A** — it does not exist and constructing it is unauthorized |
| 2 | **The historical-candidate cause-3 fixed-draw seed scan** (`⚠ AUTH`: `R4` **SUSPENDS** it; needs **both** `D-C3-VOI` and `D-C3-RUN`) | **NO for Z**, and §6.3 now settles why: Z's `M(ii)` is the **joint-baseline** quantity on Z's own assembled covariance, and the narrow scan is **diagnostic** for Z unless substitution is separately ruled | **NO as evidence; YES as method and cost prior.** What transfers is the predeclared quantity form, the six exhaustive branches, the thresholds `f_agg ≤ 0.0415` / `f_med ≤ 0.0274` and the 13-task shape. No measured value transfers | **method and thresholds: YES, committed.** **a measured value: NO — none exists.** `R4`: no `nd-unfolding/uq_5d/cause3_mii_20260901/`, no receipt; the run never launched |
| 3 | **The first `r5_meter` accounting receipt measured on Perlmutter** | **YES — a TIER-3 prerequisite only** (§6.7). It gates production, **not** specification acceptance and **not** permission to implement | **YES.** It measures the campaign's spend against `R5`, a property of any Z campaign | **NO — it does not exist**, re-measured at this base. **⚠ AND REV. 1–14's *"a query plus a commit, not a build"* UNDERSTATES IT** — committing it **arms compute admission queue-wide** (§5.6a), and the **meter repair has since landed** (§5.6b), which converts the documented command's output from a visibly-wrong receipt into an honestly armable one |
| 4 | **`PM-1`** — the nine-vs-five weight-only band census on **G's own `combined_source`** | **YES.** If any of the four weight-only bands carries selection-dependent support in the 5D chain, Z's five-band scope is **incomplete for cause 7** and this specification must be amended | **YES** — a property of the support family Z reads | **NO.** The tree's claim is the **FPS-side** row `VALIDATION_LEDGER.md:788-791`, corroborated by `2D_OMNIFOLD_REFERENCE.md:239-241` — the same split, not a second measurement. A cluster read |
| 5 | **`PM-2`** — G's `combined_source` sha256, **read from the file** | **YES.** Without it Z's parent chain has a definite description where it needs a digest | **YES** | **⚠ CORRECTED IN REV. 7 — §5.9a. YES, ALREADY IN THE TREE.** G's **own** build receipt `STAMPED_HASH_RECEIPT.slurm-56720356.json` records the full path and `9f7b2f55…` at `2026-08-12T05:46:19Z`, **four days before S read the file**; S's manifest is a second, differently-originated **agreeing** measurement. **Rev. 2–6's *"using S's digest as G's is the substitution `PM-2` exists to prevent"* is FALSE and is withdrawn.** What survives is a *timing* qualification, not a missing digest: the launcher hashes after building, and the `mtime_ns 2026-07-14` field is what closes the gap — hence §1.5's new **open-time stamping** requirement |
| 6 | **`PM-3`** — availability, provenance and **grid/footing compatibility** of the ten selection-complete endpoints | **YES.** They are `L_active`'s inputs | **YES** | **PARTLY, and rev. 2 narrows what the evidence shows.** `RECEIPT-20260816` records all 20 stage-1/2 tags **SKIPPED** as of 2026-08-16 and `DETERMINATION-20260811` records the samples *"Gate-3 promoted… since 2026-07-20"*. **Historical SKIPs establish neither present availability nor mandatory retraining** — the reviewer's formulation. A cluster `ls` plus digest and footing check; a **rebuild is priced only if that check fails** (§5.5) |
| 7 | **`PM-4`** — G's mask digest and row-order digest, read from G | **YES.** §1.3's invariant is unassertable without them, and without it every `M` comparison is over two populations | **YES** | **⚠ CORRECTED IN REV. 8 — §1.3d. NOT MERELY UNREAD: UNREADABLE AS PHRASED.** G's committed key inventory is **13 keys** and holds **neither `hRowIndex5D` nor `hXSecND_flat`** (`receipt_candidate_stamps_5d.json`, re-verified here), so *"read from G"* has no referent. **Rev. 2–7's *"G is 2026-08-12, so it plausibly carries `hRowIndex5D`"* was flagged as an inference and is now REFUTED** — the 49-key object carrying it is the **2026-08-16 rebuild**, i.e. S's lineage. The digests are **reconstructible** from G's production-CV input, whose identity **G's own hash receipt does not bind**. That binding gap is the row's real content, and the row's phrasing needs amending by its owner |
| 8 | **`PM-5` (NEW in rev. 2)** — the `V`/`R`/`A` partition measured against G's own `combined_source` band inventory | **YES.** §1.3a's disjointness-and-exhaustiveness gate cannot be written against an unmeasured family | **YES** | **PARTLY.** `VERT_BANDS` (13) and `p4_lib.BANDS` (5) are committed constants; S's manifest gives 45 `all_syst_bands`. **But that is S's family read, not G's**, and `R`'s membership is a *complement*, so it is only as good as the family list. A cluster read closes it |
| 9 | **The cause-4 jitter-print re-add**, with §2.4's four conditions | **YES.** The only route by which `(cause 4, Z)`'s `M` can be anything but permanently unmeetable | **YES — the property Z has and G cannot.** The obstruction is a property of the committed history, and this base descends from `081ae4ac` | **NO — code that does not exist.** The *specification* of what to re-add **is** reusable: `a0cdc019:232-252`, recovered and committed |
| 10 | **The FIVE inflation gates of §1.3b**, including the **`g`-reconstruction** gate | **YES, and the fifth is what makes the other four capable of failing** — `g ≡ 1` satisfies all four (§1.3b) | **YES** | **NO — new code.** `adopt_unified_5d.py` *computes* `g` and writes `hInflation_g`; **nothing recomputes it from the throw operands and compares**, and reading the producer's own value back is not this gate |
| 11 | **Extending the cause-3 seed guard to the dominant block** | **YES** for `(cause 3, Z)`'s `C`. Today *"the single-seed property of the dominant block holds by hardcoding and is checked by nothing"* | **YES** | **NO — new code.** But **half already landed**: `sweep_bank_5d.py:358`'s flag and `:309`'s stamp exist. What remains is the *refusal*, not the *stamp* |
| 12 | **The cause-3 throw-leg seed/draw separation** | **NO — already done.** `unified_throw_cov.py:630/:634`, both `required=True`; `:477-479` and `:483-485` refuse mixed estimator and incoherent draw seeds | **YES** | **YES, zero compute.** Landed `3dd5e66e`, 2026-08-18, an ancestor. **`SCOREBOARD` §2b's *"unsatisfiable"* is superseded** |
| 13 | **A bidirectional projection-coverage repair** | **NO — WITHDRAWN, it already exists** (§2.6a). `p4_lib.build_projection_M:1353` is fail-closed both ways (BEN-064, 2026-08-09) with `reachable_low_mask:1322` as the contract correction (2026-08-10); `eavailW_covariance.py:407-432` is guarded and **deliberately not** fail-closed | **YES** | **YES, zero compute.** What Z needs instead is to **preserve the asymmetry and evidence both censuses** |
| 14 | **The standard-P4 validator's 11 gates as Z's cause-7 `C`/`T` machinery** | **NO as a prerequisite; YES as reuse** | **YES for the BLOCK-SUM identities**, already PASSed on a 10,694-bin object (`full_total_identity_relerr = 4.6e-14`). **NOT for the inflated object** — §1.3b's five gates are outside its scope | **YES for what it covers, zero compute.** What is **not** reusable is the *verdict*: S's PASS is evidence about S — **nor the coverage**: `RECEIPT-20260816`'s stage 5 measured the **block-sum** gates, so it prices and validates none of §1.3b's five additional ones (§5.2) |
| 15 | **The cause-5 construction-path re-trace on Z's own path** | **YES** for `(cause 5, Z)`, and §6.1 makes it the **precondition of the ruled disposal** | **PARTLY.** The *reasoning* transfers; the *coverage* does not — Z's path is a superset and runs through `adopt_unified_5d.py`, which `VL66` did not audit | **YES, zero compute** — a static read. **But not by cause 5's owner**, per `VL66`'s own weighting caveat |
| 16 | **Cause 1's completed magnitude measurement** (both one-sided choices, off-diagonal, non-pair bands accounted) | **YES** for `(cause 1, Z)`'s `M`, and §6.2 fixes its form | **YES** — a property of the bank Z rebuilds | **NO.** A measurement on Z's own bank. **No unfold**: the census reads `uq_5d/universe_sweep_bkgaware/…` outputs, so the marginal cost is post-processing, not GPU — but **off-diagonal means full `10,694²` per band**, which is a real memory/CPU cost this lane has not sized |
| 17 | **Cause 1's disclosure** (`RULING 1`'s note obligation) | **YES**, and §6.2 makes it part of closure | **YES** | **NO** — and writing it is a **publication act outside `RZ(iv)`** |
| 18 | **A vocabulary decision on `N/A`** | **NO — CLOSED.** `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` (`e59df955…`): no fourth token. **Rev. 1 proposed one; that was a miss** | n/a | n/a. §6.1's per-cell disposal is the route, and it needs no `§0` change |
| 19 | **`D-RESOURCE`** — an exact resource authorization naming a Z run (`R5`) | **YES** for construction; **NO** for this specification | **YES** | **NO — it does not exist.** `R5`'s ceilings are *"NOT authorization to spend up to"* them |
| 20 | **Two independent pre-launch reviews** (`PLAN-20260905` #17) | **YES** for a construction Z's grade can rest on. Worker agreement is not independence | **YES** | **NO.** The prompts are committed and reusable as method; the reviews are not done |
| 21 | **An independent ARTIFACT REPLAY from digest-bound artifacts** (`PLAN` #19) | **YES**, and rev. 2 narrows what it is: *"cold checkout, no producer helpers"* means **no producer code paths**, **not** retraining | **YES** | **NO**, but it is **not a second production campaign** — §5.3. Rev. 1's automatic doubling is withdrawn |
| 22 | **A grading lane `BEN-381` does not disqualify** | **YES.** This lane is disqualified by drafting; the cause-4 measuring lanes by `DECISION-20260902-…-oi173` §3 | **YES** | **YES, zero compute** — a routing act |

## 4.1 The two authorization facts, stated so no dependency claim launders them

1. **Constructing Y requires `D-Y-CONSTRUCT` (`R2(iv)`). It does not exist.** This analysis finds Y is
   **not** a Z prerequisite (row 1). If a later plan asserts one, the assertion does not create authority.
2. **The cause-3 narrow scan requires BOTH `D-C3-VOI` and `D-C3-RUN` (`R4`), and its launch authorization
   is SUSPENDED.** This analysis finds it is **not** a Z prerequisite (row 2), and §6.3 makes it
   diagnostic for Z. **A Z schedule that assumes it will run is asserting a decision Joseph has not
   taken.** The reviewer's related point is adopted: **substitution is not a third prerequisite for the
   historical narrow scan** — permission to *measure* and permission to *substitute* are different acts,
   and the off-branch `VOI-20260906` at `47494dbe` distinguishes them correctly.

**The honest converse, as a finding rather than a plan:** this analysis does **not** find that Z needs
either suspended item. What Z needs and does not have are rows 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17,
19, 20, 21 — of which **row 19 is Joseph's decision, not work**, and **row 3 is the fail-closed gate on
every row that costs compute**.

---

# 5. COSTED EXECUTION PROPOSAL — deliverable `RZ(v)(e)`

**An estimate for a decision. Not a bid, not a request, not an authorization.** `RZ(iv)` withholds
compute; `R5`'s ceilings are a prohibition, not a budget to spend.

## 5.1 The anchor, and what it is an anchor for

**The only ratified anchor is a complete seven-arm k=0 rehearsal round at `70` GPU / `113` CPU
task-hours** (`AMENDMENT-20260831-oi177` §5, ratified 2026-09-01 — *"I sign"*), against `R5`'s `500`/`500`.
The reviewer confirms it is a valid ratified ceiling anchor. Three things about it:

- **`70`/`113` is the RATIFIED CEILING SUM, not a measured actual.** Summing §5's own columns:
  **round 1 = `54.80` GPU / `66.80` CPU; round 2 = `54.90` GPU / `86.53` CPU.** Using the ceiling is the
  conservative choice and this proposal uses it; a reader comparing to an actual compares to `~55` GPU /
  `67–87` CPU.
- **`k=0` is a MEMBER INDEX, not a reduced-iteration configuration** —
  `PROPOSAL-20260830-forward-only-rehearsal.md`: *"k=0 is the anchor and the only member with an archive
  comparand."* So the anchor is a **full-scale** seven-arm production round, which is what makes it
  transferable to Z at all.
- **Arm 2 "seed split" is the ML-split replica arm, not any estimator-seed scan.** Measured:
  `sbatch_seedscan_split_5d.sh:300` writes `seedscan_split_5d/res_split_<id>.npz`, and
  `sbatch_combine_5d_budget.sh:16-17` turns that glob into `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported`
  — **`C_ML`**. Conflating it with a cause-3 scan on the shared word *"seed"* double-counts one and omits
  the other. The off-branch `VOI-20260906` records the same collision independently.

## 5.2 One Z build — a PRICED SUBTOTAL, not a complete upper bound

**Read the header literally, and do not repair it into a bound.** Rev. 2 presented `73.0`/`≤118.0` as
though it bounded a build; rev. 3 called the remainder *"a floor with a decimal point"*. **Both are
withdrawn.** A subtotal that omits required work is **neither a ceiling nor a floor** — it is a partial
sum, and the omitted rows could move a real campaign in either direction, as could reuse and different
execution conditions. **The two subtotals below omit DIFFERENT rows, enumerated under each**, and neither
is a bound on spend.

**Two columns, because rev. 2 collapsed them and §5.2a shows they are different questions.** `R5` meters
**actual elapsed** (`ElapsedRaw`), so *spend* is the runtime; the *requested walltime* is a reservation
bound and what a breach is measured against. They are not interchangeable.

| item | **expected spend** GPU / CPU task-h | **reservation bound** GPU / CPU task-h | basis, and how firm |
|---|---|---|---|
| seven-arm production round | `54.90` / `86.53` | **`70` / `113`** | spend = round-2 measured actuals; bound = the **ratified ceilings** `20+20+30` / `8+60+40+5`. Contains arm 1 (the statistical replica ensemble) and arm 2 (the ML-split ensemble) |
| standard-P4 lateral stages 3–6 | **`0.80`** / 0 | **`3.00`** / 0 | **corrected twice — §5.2a.** Spend = the step's measured `00:47:58` for a job that exits; `3.00` is what the observed **hold-style** dispatch actually charged, retained as a hazard to design out. Assumes stages 1–2 skip, **conditional on `PM-3`** |
| statistical + ML **combine** | **unmeasured** | 0 / **`1.0` PROPOSED, UNVERIFIED** | `sbatch_combine_5d_budget.sh`, **not one of the seven arms**. `--time=01:00:00` is a *request*, and **a time limit bounds an ATTEMPT, not a successful completion** — it says the job is killed at one hour, not that the work finishes inside it. **No actual is recorded**: `grep` over `RUNS.tsv` for `budget5d`/`combine_5d_budget` returns **0** rows against a positive control on the same file |
| **the two assemblies only** (`adopt_unified_5d.py` ×2) | **unmeasured** | 0 / **`4.0` PROPOSED, UNVERIFIED** | **narrowed in rev. 3, relabelled in rev. 4.** The 4-hour figure is a *historical request*, so it **bounds an attempt, not a completion**, and it is not a derived `< 4 h` completion bound for Z's assemblies — it can motivate a **proposed** reservation and nothing more. **No completion bound is licensed by it** — the 4-hour request covered all four of that launcher's operations, of which only these two are Z's, and a request that was never exceeded is not a measurement of what these two need. Rev. 2 charged the whole 4-hour `sbatch_j28_adopt_5d.sh`. **Three of its four operations are not Z's:** `rescale_flux_universes.py` (`:74`) is a **J28-only historical repair** Z never runs; `unified_throw_cov_5d.py --combine … --null` (`:94`) **is arm 7**, already counted above; the slab union is symlinks. **Only `:111` and `:113` are additional**, and the 4-hour request covered all four together, so it licenses **no completion bound for these two at all** |
| **cause-4 jitter counterfactual — a SECOND CV unfold** | **unpriced** | **unpriced** | **corrected in rev. 3, and rev. 2 had the wrong operand.** `--null`'s unfold uses `args.estimator_seed` (`unified_throw_cov.py:514-515`) — the **same** seed. The jitter counterfactual uses **`args.seed + 7`** (`a0cdc019:233-234`). **They are two different unfolds**, so re-adding the print adds one *on top of* the one arm 7 already runs. **Arm 7's historical headroom is evidence about the existing unfold and says nothing about the additional one** |
| cause-1 counterfactual, incl. off-diagonal | **unpriced** | **unpriced** | post-processing of `uq_5d/universe_sweep_bkgaware/…` (`receipt_cause1_endpoint_census_5d.json`, `inputs.glob`) — **no unfold**. Off-diagonal means full `10,694²` per band; unsized |
| **Z's INFLATED-OBJECT validation** | **unpriced** | **unpriced** | **new row in rev. 3.** `RECEIPT-20260816`'s stage 5 covers the **block-sum** gates and is inside the stages 3–6 line. **§1.3b's five additional gates are not** — in particular the `g`-reconstruction gate recomputes `g^c` per variant over the reported support, and PSD on the inflated object is an `eigvalsh` on `10,694²`. Unsized |
| **PARTIAL SUM** | **`55.70` / `86.53`** | **`73.0` / `118.0`** | **`11.1%` / `17.3%` of `R5` for the spend estimate; `14.6%` / `23.6%` for the proposed reservation.** **Neither is a bound. Each omits a different set of rows — enumerated immediately below** |

**The omissions, listed per subtotal rather than as one moving count, because rev. 3 gave three different
numbers with three different memberships.**

- **The expected-spend partial sum (`55.70` / `86.53`) omits FIVE rows:** the statistical+ML combine
  (**unmeasured** — a request is not a spend estimate), the two assemblies (**unmeasured**, same reason),
  the cause-4 second CV unfold, the cause-1 off-diagonal counterfactual, and Z's inflated-object
  validation.
- **The proposed-reservation partial sum (`73.0` / `118.0`) omits THREE rows:** the cause-4 second CV
  unfold, the cause-1 off-diagonal counterfactual, and Z's inflated-object validation. It *includes* the
  combine and the assemblies, at **proposed, unverified** request-derived figures.
- **Campaign-level items are in neither, by construction:** the artifact replay (§5.3) and
  `(cause 3, Z)`'s ruled measurement (§5.4), the latter having no design and therefore no cost.

**So the honest one-line answer is:** a Z build's *estimated* spend on the rows that have one is `≈56`
GPU / `≈87` CPU task-hours, with a **proposed** reservation of `73` / `118`; **five rows have no spend
estimate, three have no figure at all, and one campaign-level item has no design.** None of that makes
either partial sum a bound in either direction.

### 5.2a The scheduler-accounting correction, because it changed the number

Rev. 1 priced stages 3–6 at `0.80` GPU task-hours from step `57128458.1`'s `00:47:58`. **That is a
runtime prior, not R5 spend, and the reviewer is right to separate them:**

- `r5_meter._calculate_spend` (`docs/orchestration/r5_meter.py:277`) sums `ElapsedRaw` over **distinct
  task identities**, with step rows excluded by `_parse_sacct_dump` (asserted by
  `test_steps_extern_and_array_bracket_rows_are_excluded`). **So R5 meters the parent task, not the
  step.**
- The parent's own record: `RECEIPT-20260816-p4-standard-stages456.json` `job_later_TIMED_OUT` —
  *"2026-08-16T18:37:31 after 03:00:03, AFTER this chain completed"*. **Metered, that instance is `3.00`
  task-hours, not `0.80`.**
- **And it predates `t0` (`2026-09-02T13:44:27Z`), so it contributes nothing to actual R5 consumption.**
  It is a prior for planning, and nothing else.

**⚠ AND REV. 2'S OWN CONCLUSION FROM THAT WAS FALSE. Corrected here on the second review.** Rev. 2
wrote *"the metered cost of this step is the wall request, not the runtime."* **It is neither — it is the
parent task's ACTUAL elapsed time.** Measured: `SACCT_FIELDS` (`r5_meter.py:49-58`) requests
**`ElapsedRaw`** and **not** `Timelimit`; `_parse_elapsed` (`:165-174`) parses that value directly and
`_calculate_spend` (`:277`) sums it. **A task that requests 90 minutes and exits after 48 contributes
`≈0.80` task-hours, not `1.5`.**

**So why did the observed instance meter `3.00`?** Because the parent **stayed allocated until its
timeout** — it was a `claude-hold` allocation, and the receipt says so: the job timed out at `03:00:03`
*"AFTER this chain completed"*. The hold, not the wall request, is what charged three hours.

**The correct rule, and it separates two numbers rev. 2 conflated:**

- **actual elapsed → SPEND.** A right-sized Z job that exits when its work is done meters near the
  runtime, `≈0.80` task-hours on this evidence.
- **requested walltime → a RESERVATION or MAXIMUM-COST bound**, useful for a ceiling and for what a
  breach would be measured against, and **not** a charge.

**Neither `0.80` nor `3.00` is automatically the future charge.** §5.2 now carries both columns, and the
`3.00` figure is retained only as *what a hold-style dispatch actually cost*, which is a real hazard to
design out rather than a price to plan on.

**Rev. 1 also stated this backwards in its own §5.6.** It described `RUNS.tsv:321`'s allocation-level
`node_h=6.00` as a `7.5×` error against `0.80`. Under `R5`'s unit the **allocation-level view is the
closer one**, and the step-level figure was the misleading one. Corrected here.

## 5.3 The campaign, not the build

| scenario | GPU task-h | CPU task-h | vs. `R5` 500/500 |
|---|---:|---:|---|
| one Z build, **spend estimate** (5 rows omitted, §5.2) | `55.70` | `86.53` | `11.1%` / `17.3%` |
| one Z build, **proposed reservation** (3 rows omitted, §5.2) | `73.0` | `118.0` | `14.6%` / `23.6%` |
| **+ independent ARTIFACT REPLAY** | **not a production round** | **not a production round** | see below |
| + optional independent **regeneration**, if separately proposed and authorized | `111.4` – `146.0` | `173.1` – `236.0` | `22.3–29.2%` / `34.6–47.2%` |

**Every figure in this table inherits §5.2's per-column omission census**, which lists five omitted rows
for the spend estimate and three for the proposed reservation. **On top of those, two campaign-level
items are in neither:** the artifact replay below, which is unsized, and `(cause 3, Z)`'s ruled
measurement (§5.4), which has no design and therefore no cost. **Nothing here bounds a Z campaign in
either direction.**

**Rev. 1's automatic doubling to `143`/`226` is WITHDRAWN.** The reviewer's correction: *"price
independent reconstruction from digest-bound artifacts separately. 'Cold checkout, no producer helpers'
does not require retraining."* `PLAN-20260905` #19 asks for an independent replay; **replaying the
identities from Z's digest-bound components is verification work, not a second production campaign.** Its
cost is reading and recomputing `10,694²` matrices from committed digests — CPU, bounded by the same
shape as the combine and the assembly, and **this lane has not sized it**. A second full regeneration
**may be proposed** and is priced above, but **it is not a mandatory replay cost** and rev. 1 was wrong
to treat it as one.

**Time, measured rather than recalled.** At `2026-09-05T22:46Z` the `R5` stop (`2026-09-30T00:00:00Z`,
inclusive) was **24 days 1 hour** away; `3 days 9 hours` had elapsed since `t0 = 2026-09-02T13:44:27Z`
(`9ce59a59`). **The date binds and the ceilings are the backstop** — `DECISION-20260902` §1's own reading
of the pairing Joseph selected. Nothing here reopens it.

## 5.4 Cause 3's magnitude, priced against the RULED quantity

**Rev. 1 claimed a "`≈4.5×` scope fork". That is WITHDRAWN: it divided two figures with different
populations.** The three figures in play, each with its own scope:

| figure | what it actually prices | population |
|---|---|---|
| `8.7` GPU (worst `18`), `0.08` CPU | **12 CV unfolds** at 12 estimator seeds, one fixed data/MC draw, **on G's footing** | the narrow fixed-draw scan |
| `39.223` GPU / `55.337` CPU | **one additional estimator seed on the `C_syst` sweep/detector arms only** — `23.840 + 14.2075 + 1.030 = 39.078`, plus `0.1458` (`SCOPE-20260818-gate1-seed-separation-two-keys.md` `:22`, `:340`, **derived at neither site**) | a partial-arm increment |
| **`54.90` GPU / `86.53` CPU** | **one complete seven-arm member round**, round-2 actuals | **the joint-baseline composite — the quantity §6.3 rules for Z** |

**No ratio among these three is a scope comparison.** The off-branch `VOI-20260906` at `47494dbe`
identifies the same trap and records that its own earlier use of the letter `Z` for the composite scan
would *"attribute a `39.223`/`55.337`-per-seed scan price"* to the wrong object.

**What §6.3's ruled quantity would cost, at the design that is NOT assumed.** A joint-baseline composite
is measured over **members**, each a complete seven-arm round:

- at the historical family sizes, `46 × (54.90, 86.53) = **2,525** GPU + **3,980** CPU`, and
  `50 × … = **2,745** + **4,326**` — **5× to 9× over `R5`'s `500`/`500`**;
- **§6.3 explicitly does not adopt 46/50 as the necessary design.**

**⚠ AND `54.90`/`86.53` IS A HISTORICAL SEVEN-ARM PRIOR, NOT A MEASURED Z-MEMBER PRICE — rev. 2 blurred
that and rev. 3 separates it.** A **Z** member is not a historical seven-arm round: it additionally
carries the **active lateral components** (§2.7), the **final inflated assembly in both variants**
(§1.3a), and Z's **inflated-object validation** (§1.3b) — the three rows §5.2 marks unpriced. **So the
per-member figure is a PRIOR from a different subject, not a bound in either direction**, and every
product of it inherits that. **Rev. 3 called it a "lower bound of unknown tightness"; that is withdrawn.**
Additional work does not prove a future Z run costs *more*: execution conditions differ, and reuse —
skipped endpoint stages, cached slabs, a warmer footing — can move a real run the other way. The
extrapolations below are useful **conditional on those prior costs** and on nothing else.

**What the extrapolation does and does not establish.** It establishes that **the historical 46–50-member
design exceeds `R5`'s ceilings by 5×–9×** — a fact about that design, at prior costs. **It does not
establish the cost of Z's design, and therefore not its affordability either**, because §6.3 leaves the
design open, and the prior used here was measured on a **different subject** — a historical seven-arm
member with neither the active lateral components, nor both assemblies, nor the inflated-object
validation. **Rev. 4 said a Z member "costs more"; that is withdrawn too.** A different subject supports
no direction: the extra work pushes one way, and reuse and execution conditions can push the other.

**⚠ SUPERSEDED IN PART BY REV. 7 — §3.7b.** *"No design"* was right about what §6.3 left open and wrong
about what the tree already contained: **the member is implemented**, as one shared
`MNV_EST_SEED_OFFSET` across exactly seven launchers, so what was open was `N` and the offset set, not
the member. With the member measured, the **planning estimate** puts **`N = 4`–`5` total at `86.5%` of
the CPU ceiling** (**⚠ rev. 16: an estimate, not a demonstrated capacity** — §3.7b), so there is now a
costing where this paragraph says there is none. **The
per-member prior and its "different subject" caveat are unchanged and still govern.** Read the sentence
below as rev. 3's, superseded:

**So the honest statement is:** `(cause 3, Z)`'s `M(ii)` as ruled has **no design, therefore no cost,
therefore no affordability verdict**; and the one design that *has* been sized — the historical family —
**exceeds `R5` by 5×–9× at prior costs measured on a different subject.** Whether a Z member is dearer
or cheaper than that prior is **not established in either direction**. That is a finding for Joseph, not
a plan (§7 item 3).

## 5.5 Conditional and unpriced items, named rather than absorbed

**⚠ SUPERSEDED IN PART BY REV. 7 — §5.8 is the current census and §5.8a is the delta.** Three of the
items below are no longer unsized: the cause-1 off-diagonal counterfactual (`≈0.03` CPU task-h), Z's
inflated-object validation (`≈0.07`), and the two assemblies (`≤ 0.5231`, a **measured upper bound**).
The list is kept as written because §5.8 is a completion of it, not a replacement.

- **Endpoint rebuild.** Priced **only if** `PM-3`'s availability, provenance or compatibility checks
  fail. **Historical SKIPs establish neither present availability nor mandatory retraining**, so a
  rebuild is neither assumed nor pre-costed here.
- **Cause-1 off-diagonal counterfactual** — §5.2, unsized.
- **The cause-4 jitter counterfactual's SECOND CV unfold** — §5.2, unsized, and **distinct from the
  same-seed `--null` unfold arm 7 already runs**. Arm 7's headroom is evidence about the existing
  operation and does not establish that the additional one fits.
- **Z's inflated-object validation** — §5.2, unsized. The historical P4 chain covers its **block-sum**
  gates; §1.3b's five additional gates, including the `g` reconstruction over the reported support and
  an `eigvalsh` on `10,694²`, are **not** in that measurement.
- **The two assemblies alone** — §5.2. The 4-hour J28 request bounds them **together with** a J28-only
  rescale Z never runs and a throw combine already counted as arm 7.
- **Artifact replay** — §5.3, unsized.
- **The five inflation gates of §1.3b and the cause-3 dominant-block refusal** — code, not compute.
- **A joint-baseline design for `(cause 3, Z)`** — §5.4.

## 5.6 The meter gap, named in the proposal as the brief requires

**The instrument is built and admission is fail-closed. The ceilings have never been measured against
the scheduler.** Measured at this base:

- `docs/orchestration/r5_meter.py` exists (27,357 B) and encodes `R5` exactly: `T0_UTC_TEXT =
  "2026-09-02T13:44:27Z"` (`:33`), `STOP_DATE_UTC_TEXT = "2026-09-30T00:00:00Z"` (`:37`),
  `GPU_TASK_HOURS_CEILING = CPU_TASK_HOURS_CEILING = 500.0` (`:41-42`), task-hours with t0 clipping.
- `docs/orchestration/campaignctl.py` exists (204,141 B); admission is fail-closed.
- **`docs/orchestration/state/r5-meter-receipt.json` DOES NOT EXIST.** Measured, not recalled. The
  reviewer confirms: *"No operational meter receipt is committed at either reviewed revision."*
  **⚠ STILL TRUE AT THIS BASE, AND NOW FOR A DIFFERENT REASON — §5.9, §5.6a.** A genuine receipt has
  been **produced** against live Perlmutter `sacct` and deliberately **not committed**.
  **⚠ REV. 8 ATTRIBUTED THAT CHOICE TO THE PREFLIGHT SESSION. IT IS JOSEPH'S INSTRUCTION, WHICH IS
  STRONGER EVIDENCE, AND THE CORRECTION IS RECORDED RATHER THAN ABSORBED.** Quoted from
  `AUTHORIZATION-20260906-pm-root-inspection.md` §2 (`1422569c`, off-branch): *"Label the existing R5
  receipt explicitly as incomplete because it omits requeue expenditure; do not present it as valid
  admission evidence."* **Committing it to `docs/orchestration/state/r5-meter-receipt.json` IS that
  presentation** — that path is the gate's input and nothing else reads it. **So the gate holds by
  instruction, not by absence and not by a lane's discretion.**
- `test_r5_meter.py`: **18 tests, all passing** — **on three checked-in fixtures**
  (`test_fixtures_r5_meter/{mixed,perlmutter_regular_gpu,rows_vs_identities}.sacct`) that are
  **hand-authored, not captured** (job ids `50000`/`60000`, task names `task-0`,
  `reviewer-regular-gpu`). **The parser is tested; the deployment is not**, and a fixture authored beside
  its parser cannot disagree with it.
- `_sacct_argv()` (`:380-392`) requests `JobID,JobName,State,ElapsedRaw,Partition,Start,End,AllocTRES`
  for the current user from t0 to now. **Whether real Perlmutter `sacct` output parses cleanly through
  it is unmeasured.** **⚠ ANSWERED IN REV. 7 — IT DOES** (§5.9 item 1, relayed). **And two new defects
  arrived with the answer:** `_sacct_argv()` carries **no `--duplicates`**, so a requeued task is
  counted once against `R5` §3's *"retried tasks count in full"* (`D5`, `12.59` CPU task-h of measured
  gap); and `sacct` **refuses spans over 30 days**, so this query stops working on
  `2026-10-02T13:44:27Z` — `2 d 13 h 44 m` after the `R5` stop (§5.9b).
- **No unattended execution is configured** (`ACCEPTANCE-20260905`; the credential decision is Joseph's
  or the site owner's).

**Consequence:** *"The queue admits no item at all until a receipt measured on Perlmutter is committed,
and none is."* **A first receipt is a prerequisite to any Z campaign and is itself an uncosted item** —
a login-node `sacct` query plus a commit, so its **task-hour** cost is ≈0, but its credential and
authorization cost is not this lane's to price. **Do not infer the meter is deployment-ready.**

**And the other production prerequisites, per the reviewer:** measured headroom, compatible input
identities (`PM-2`, `PM-3`, `PM-5`), and an explicit run authorization (`D-RESOURCE`). None exists.

### 5.6a THE OPENING ACT, NAMED — NEW IN REV. 9, because §4 row 3 makes it Z's first prerequisite

**§4 row 3 says a Z campaign needs the first `r5_meter` receipt, and calls it *"a login-node `sacct`
query plus a commit, not a build"*. That is true about the effort and misleading about the
consequence.** Measured against `campaignctl.py` at this base:

| the act | what it does |
|---|---|
| **running** the meter, repaired or not | **nothing.** No gate reads a process's output |
| **writing** the receipt to an untracked file, or editing it after committing | **still refused** — `committed_file_identity` (`:3055-3077`) rejects an untracked path **and** a working-tree edit that no longer byte-matches the committed blob |
| **committing** a receipt to `docs/orchestration/state/r5-meter-receipt.json` at `HEAD` | **removes a QUEUE-WIDE refusal.** `committed_r5_receipt(queue)` (`:3080-3111`) takes **only the queue** — no item — and `r5_refusal_reason` (`:3330-3341`) consults it for **every** compute item. One commit clears that reason for **all of them at once** |

**Three things bound the blast radius and none of them makes the act small.**

1. **It expires.** `R5_MAX_AGE = 24 hours` (`:292`, checked at `:3355-3360`), with a `60`-second
   future-skew bound (`:296`) — so admission re-closes a day later unless a fresh receipt is committed.
   **The act is repeatable and expiring, not permanent.**
2. **Other refusals survive it.** Non-canonical state, `fired.any`, the stop date and the spend
   ceilings are all still checked. **Committing the receipt admits nothing by itself; it removes one of
   several reasons to refuse.**
3. **A known bypass exists and is on the record as REFUSED.** A `--kind read-only` item skips the R5
   gate entirely, because `r5_refusal_reason` is called only under `if item["kind"] == "compute"`. The
   preflight session named it in `AUTHORIZATION-20260906-pm-root-inspection.md` §3.5 and rejected it.
   **It is recorded here for the same reason it was recorded there: an available evasion that nobody
   has written down is an undiscovered one.**

**The operational sentence, which is the point of this subsection:** the integration lane's meter
repair is expected within days, and **landing the repair does not open the gate.** The opening act is a
`git commit` of a receipt to one tracked path. That is a queue-wide decision with its own weight, and
under Joseph's standing instruction the receipt that exists today may not be presented as admission
evidence at all (§5.6). **This lane names the act; it does not propose taking it, and `RZ(iv)` would
not let it.**

**⚠ AND THE ACT IS PRESCRIBED, NOT MERELY AVAILABLE — NEW IN REV. 11, measured in this checkout.**
Rev. 9 wrote *"nobody should perform it by running the repaired tool once to see whether it works"*,
which frames the hazard as carelessness. **It is the opposite: the documented procedure performs the
first half of it.** `docs/orchestration/R5-METER.md:12-16` carries a copy-pasteable block, introduced
by *"On Perlmutter, query accounting in UTC and atomically refresh the default receipt"*:

```bash
python3 docs/orchestration/r5_meter.py measure \
  --write docs/orchestration/state/r5-meter-receipt.json
```

**That is the gate's exact path**, written by the runbook's own recommended invocation. Three
measurements make the remaining distance one command:

| measured | result |
|---|---|
| is the gate path gitignored? | **NO** — `git check-ignore -v docs/orchestration/state/r5-meter-receipt.json` exits **1** |
| do its siblings get committed? | **YES, as the norm** — `git ls-files docs/orchestration/state/` counts **150** tracked `.json` files |
| does the runbook warn about admission? | **NO.** Its closing line is *"The meter authorizes nothing. R5 is a prohibition and an accounting boundary; every run still needs its own declaration and authorization."* **True about AUTHORIZATION and silent about ADMISSION** — and admission is what that path controls |

**So the sequence that arms the queue is: follow the runbook, then `git add`.** Neither step looks like
a decision. A `git add -A`, a routine *"commit the state directory"*, or any hook that stages generated
state completes it, and **§5.6a's whole point is that the second step is the one with the queue-wide
consequence while the first is the one anybody would do.** The runbook's disclaimer will not stop it,
because it disclaims a different thing.

**Stated as a requirement rather than a worry, since this document is a specification:** before any Z
campaign, either the runbook's default `--write` target must stop being the gate path, or the gate path
must stop being an ordinary tracked-by-default file — **and which of those is right is not this lane's
call.** It is named in §7 item 19 and belongs to the meter's owner.

### 5.6b THE METER REPAIR HAS LANDED — operational dependencies updated, NEW IN REV. 15

**Measured, not relayed.** The repair is on `main` at **`72bcd2f6`**, branch
`r5-accounting-requeue-repair-20260906`. **Ancestry: NOT an ancestor of this tip** — the merge base is
`c71b319a`, so **this document's `r5_meter.py` is the pre-repair one** and every `file:line` in §5.6
and §5.2a describes the landed-then version. Seven commits, of which four matter here.

| what changed | effect on this document |
|---|---|
| **`e055490c` — the metered unit is an EXECUTION ATTEMPT, not a job id.** `sacct` is now queried `-X -D`; a requeued job's `952` attempts were being counted as one | **`D5` IS RESOLVED, in the direction §5.9 flagged.** Attempts are summed |
| **`71bfa298` — an attempt is `(JobID, Start)`, not `(JobID, End)`.** Keying on `End` charged one execution twice | a defect **introduced and caught inside the repair**; `End` is deliberately excluded because two rows differing only in `End` are far more likely two *observations* of one execution |
| **`852b26ab` — the runbook's own example became a live arming act, so it moved** | **§7 item 19's first remedy is TAKEN** — see below |
| **`45008564` — a requeued producer's reservation must still release** | `campaignctl` compares declared ids against `metered_task_ids` and never against `attempts_by_task_id`, so an item cannot become releasable because its job requeued |

**Receipt schema is now `2`, and a version-1 receipt is REFUSED rather than migrated** — it counted at
most one attempt per job id, which under-counts every requeued job, and an under-count against a
prohibition is the fail-**open** direction. Both `r5_meter.py` and `campaignctl.py` refuse it.

#### What this changes for Z, item by item

1. **`D5` is off the decision sheet.** `R5` §3's *"distinct task identities"* is read as excluding the
   several **representations** of one execution, not as collapsing several **executions** of one job
   id — with §3's *"counted in full"* and *"a failed task spends"* settling the tie, and under-counting
   named as the unrecoverable direction. **The alternative reading is named and isolated in one
   function** (`_sum_charged_seconds`), so a contrary ruling stays cheap. **That remains Joseph's to
   overturn; this document simply stops carrying it as an open decision.**
2. **§7 item 19's first remedy is TAKEN, and its second is now a DECISION rather than a finding.**
   `R5-METER.md` no longer defaults `--write`, its verification examples write to a scratch path or
   nothing at all, the word *"refresh"* is gone, and a dedicated section states that committing to the
   state path **opens compute admission queue-wide**. The disclaimer this document flagged is now
   marked in the runbook itself as a statement about **authorization** that is **silent about
   admission**. **The second remedy — untracking or ignoring the gate path — was deliberately DECLINED
   and referred to the decision owner**, because it would change how admission can ever be armed. So
   item 19 is half closed by code and half open as Joseph's call.
3. **⚠ THE REPAIR MAKES THE HAZARD WORSE BEFORE IT MAKES IT BETTER, and the finding says so.** Before
   it, the documented command produced the visibly-wrong `0.0016667` receipt, which a reader would
   likely catch. After it, the same command produces a **valid, complete, honestly armable** receipt.
   *"The repair converts a dud into live ammunition, which is why the runbook could not be left as it
   was."* **§5.6a's warning is therefore more load-bearing after the repair, not less.**
4. **Admission is STILL SHUT.** `docs/orchestration/state/r5-meter-receipt.json` **does not exist** —
   re-measured at this base. §4 row 3 stands unchanged as a Tier-3 prerequisite, and committing a
   receipt is a deliberate act, not a step.
5. **The 30-day `sacct` window is now dated and owned** (`FINDING-20260906-r5-meter-undercounted-requeue-attempts.md`
   §7). The span reaches 30 days at **`2026-10-02T13:44:27Z`**, which is **after** the `R5` stop, so the
   meter covers the whole campaign window. **The live constraint is narrower than §5.9b said:** `R5` §3
   lets jobs running at the stop finish with their spend counted, so **that final measurement must be
   taken before that instant**, or it needs `sacct -j <jobid>`.

#### The waker accrual, corrected by an order of magnitude — and `N` survives it

**§5.9 item 14 and `D5` carried `≈0.05`–`0.07` CPU task-h/day. That figure is WRONG and its author
withdrew it**: it scaled a 21-minute delta instead of measuring whole days, and averaged across a day
containing an `8.6`-hour hang. **A rate taken from a window containing an outlier is not a rate.**
Re-derived per calendar day, ordinary cadence is **`≈0.65`–`0.69` CPU task-h/day** (`2026-09-04`:
`0.652778`; `2026-09-05`: `0.690556`; `2026-09-03`'s `10.263611` is the hang, excluded as an outlier).

**Projected to the `R5` stop from the `09:20Z` measurement — `23.61` days — that is `15.3`–`16.3`
further CPU task-hours, for a waker total of `≈28`–`29` by the stop**, against `12.606389` measured so
far. Roughly ten times what this document previously implied.

**`N` does not move. Re-derived here under four readings:**

| ceiling reading | CPU left after one Z build | additional members | **`N` total** |
|---|---:|---:|---:|
| nominal `500`, waker ignored | `413.47` | `4` / `3` | **`5` / `4`** |
| less the measured `12.606389` | `400.86` | `4` / `3` | **`5` / `4`** |
| less the accrual projected to the stop | `384.57` | `4` / `3` | **`5` / `4`** |
| …plus one more `8.6` h hang | `375.94` | `4` / `3` | **`5` / `4`** |

*(each pair is the nominal `86.53` member and the `115.36` member carrying arm 5's measured `+58.7%`
swing)*

**So the affordability finding is robust to a tenfold error in a term this document had wrong**, which
is worth stating precisely because it is the kind of coincidence that should be checked rather than
assumed. The reason is structural: the waker is `≈6%` of one member's CPU cost, and `N` is an integer
floor.

## 5.7 The uncertainty on all of the above

1. **No Z arm has ever run.** Every figure is transferred from a different product's arms, and a **Z**
   member additionally carries the active lateral components, both assemblies and the inflated-object
   validation. **That makes the transferred figures PRIORS FROM A DIFFERENT SUBJECT — not bounds in
   either direction.** Rev. 3 called them lower bounds; withdrawn, because reuse and different execution
   conditions can move a real run down as well as up. Every extrapolation here is conditional on the
   prior costs it was built from. This dominates and no arithmetic reduces it.
2. **CPU-partition arms are demonstrably not reproducible across scheduler regimes.** `AMENDMENT` §3c/§3e
   establish it and the measurement is stark: arm 5 went `30.94 → 49.11` between rounds, **+58.7% on one
   arm**, and the amendment says *"a third run may exceed them."* **Treat the CPU column as carrying at
   least a ±60% single-arm swing.**
3. **The reservation column is built from WALL REQUESTS, which `R5` does not charge.** `R5` meters
   **actual elapsed** (§5.2a), so the right-hand column bounds a reservation and over-states a well-sized
   campaign; the left-hand column is the spend estimate, and **two of its rows are `unmeasured` rather
   than measured**. Do not read either column as a charge.
3b. **Each subtotal omits a DIFFERENT set of rows, enumerated per column in §5.2.** Neither is a bound:
    the spend column is an estimate with five rows missing, and the reservation column is a proposed
    reservation with three rows missing — **and a reservation is not a floor on spend either**, since
    `R5` charges actual elapsed (§5.2a).
4. **Failed and retried tasks count in full** under `R5` §3, including `FAILED`, `CANCELLED` and
   `TIMEOUT`. A single failed pass spends its full elapsed time and produces no Z.
5. **Two build lines are unsized** (§5.5), and `(cause 3, Z)`'s ruled quantity has **no design and
   therefore no cost** (§5.4).

## 5.8 THE CENSUS BY CATEGORY — NEW IN REV. 7

**§5.2's census is organized by *which subtotal omits what*. This one is organized by *what kind of cost
it is*, because the four kinds are authorized differently and must not be summed into one number.**
Nothing here is a bid, a request or an authorization; `RZ(iv)` withholds compute and `R5`'s ceilings
remain *"a prohibition and an accounting boundary … NOT authorization to spend up to"*.

**Evidence classes are the same four §3.7 uses**, and they are the point of this section:

- **MEASURED** — a number this lane produced, with the machine or the `file:line` named.
- **TRANSFERRED** — measured on a different subject or different hardware. **Direction not established.**
- **DERIVED** — arithmetic on those.
- **UNRESOLVED** — no figure, with the exact act that would produce one.

### 5.8a What rev. 7 moved, stated first so the census is readable as a delta

§5.2's spend estimate omitted **five** rows. After this revision:

| row | rev. 6 | **rev. 7** |
|---|---|---|
| cause-1 off-diagonal counterfactual | unpriced | **≈ `0.03` CPU task-h** — DERIVED from local timings on the real `10,694` dimension |
| Z's inflated-object validation | unpriced | **≈ `0.07` CPU task-h** — same |
| cause-4 second CV unfold | unpriced | **`≤ 0.5764` CPU task-h — a MEASURED UPPER BOUND** added in rev. 8, off `uthrow5d_combF` on `shared_milan_ss11` (§5.9 item 13). **CPU confirmed, which is the specific thing rev. 2 got wrong** |
| statistical + ML combine | unmeasured | **STILL UNMEASURED, and now a COVERED absence** — no `budget5d`/`combine_5d_budget` row exists in retained accounting `2026-07-01`→now (`3,994` rows, coverage verified), and the 4D analogue was CANCELLED at `0` s (§5.9 item 5) |
| the two assemblies | unmeasured | **`≤ 0.5231` CPU task-h — a MEASURED UPPER BOUND** on the pair, from `j28_adopt_5d` `56429334` (§5.9 item 4). Replaces `4.0 PROPOSED, UNVERIFIED` |

**Two of five are estimated, TWO are bounded above by measurements, and one is a covered absence.
Rev. 8 leaves no row in this table without a figure or a stated reason for having none** — the combine
is the only one still `unmeasured`, and it is unmeasured because **no accounting row for it exists in
any dimension**, which is a covered absence rather than a gap. The `4.0` and `1.0` reservation figures rev. 4 labelled
**PROPOSED, UNVERIFIED** are now settled in opposite directions: the assemblies come in at **`≤ 0.5231`,
an eighth of the proposal**, and the combine has no accounting at all rather than a low one. The two new figures are small enough that they do not move `55.70`/`86.53`
materially — **which is itself the finding.** Rev. 3 flagged them as an unsized hazard on the strength
of the `10,694²` dimension; measured, the dimension costs **minutes and gigabytes, not hours and
terabytes**, and the binding constraint on both rows is **memory (~2–3 GB peak), not time.**

**The sizing basis, named on both sides because it is a hardware transfer.** Measured on this machine —
macOS `arm64`, numpy `1.26.4` on `openblas64`, single process:

| operation at `n = 10,694` | measured / extrapolated | how |
|---|---:|---|
| full `n²` outer product | `0.269` s | MEASURED at `n = 10,694` |
| in-place `n²` add | `0.286` s | MEASURED at `n = 10,694` |
| band covariance `ZᵀZ/N`, `N ∈ {2, 3, 100}` | `0.45`–`0.62` s | MEASURED at `n = 10,694` |
| `numpy.linalg.eigvalsh` | **`113` s** | EXTRAPOLATED cubically from `n = 5000` (`11.53` s); the constant `t/n³` converges from above — `1.28e-10`, `1.07e-10`, `9.72e-11`, `9.23e-11` at `n = 2000…5000` |
| peak memory, eigenvalues only | **`1.83` GB** | MEASURED as one extra matrix copy at `n = 4000` (`123` MB delta against a `128` MB matrix); `jobz='N'` LAPACK workspace is `O(n)` |

**The transfer is to AMD `EPYC` CPU nodes with a different BLAS, and its DIRECTION IS NOT
ESTABLISHED** — more cores could make it faster, a slower single core could make it slower. **What
survives the transfer is the order of magnitude**, and that is all these two rows are claimed to.

### 5.8b PRODUCTION — building Z once

The cost of the artifact itself. Authorized by `D-RESOURCE`, which **does not exist** (§4 row 19).

| item | GPU task-h | CPU task-h | class |
|---|---:|---:|---|
| seven-arm production round (member `k = 0`) | `54.90` | `86.53` | **TRANSFERRED** — round-2 actuals, `AMENDMENT` §3d |
| standard-P4 lateral stages 3–6 | `0.80` | 0 | **TRANSFERRED**, conditional on `PM-3`; §5.2a |
| statistical + ML combine | — | **UNRESOLVED** | one `sacct` read; a `--time` request is not a spend estimate |
| the two `adopt_unified_5d.py` assemblies | — | **`≤ 0.5231`** | **MEASURED UPPER BOUND, relayed** — `j28_adopt_5d` `56429334` COMPLETED in `1,883` s and the pair is a subset of its four operations (§5.9 item 4). **No point estimate is licensed** |
| cause-1 counterfactual **incl. off-diagonal** | — | `≈ 0.03` | **DERIVED** — `44` as-built + `42`+`42` one-sided band covariances at `≈0.5` s, plus accumulation |
| Z's inflated-object validation, **both variants** | — | `≈ 0.07` | **DERIVED** — `2 ×` (`13` band reads + closure residual + symmetry + `eigvalsh` at `113` s) |
| cause-4 jitter counterfactual — a **second** CV unfold | — | **`≤ 0.5764`** | **MEASURED UPPER BOUND, relayed — NEW IN REV. 8.** `--null` runs inside `uthrow5d_combF` (`sbatch_uthrow_combine_5d_fast.sh:339` passes `--null`, `:2` names the job — **verified here**), which is `shared_milan_ss11`, **CPU**: `2,075` / `1,526` / `1,395` s. That job is combine arithmetic **plus one CV unfold**, so **one unfold ≤ the whole job** — the same subset-of-a-completed-job logic as the assemblies. **It bounds the increment and does not estimate it** |
| **partial sum of the SPEND ESTIMATES only** | **`55.70`** | **`86.63`** | **not a bound in either direction.** The assemblies' `≤ 0.5231` is an **upper bound, not a spend estimate**, so it is deliberately NOT summed here; **two rows — the combine and the cause-4 second unfold — have no figure at all** |

### 5.8c ARTIFACT REPLAY — verifying Z from digest-bound components

`PLAN-20260905` #19, §4 row 21. **Not a second production campaign** — rev. 1's automatic doubling stays
withdrawn — and *"cold checkout, no producer helpers"* means no producer code paths, **not** retraining.

| term | figure | class |
|---|---|---|
| arithmetic — re-read `≈45` component matrices, re-sum, re-check §1.3b's identities, `eigvalsh` both variants | `≈ 0.07` CPU task-h | **DERIVED**, same basis as §5.8b |
| I/O — `≈41` GB if each component is a full `10,694²` `TH2D`, which is how `hCov_universe5d_<band>` is read (`adopt_unified_5d.py:130-141`). **⚠ REV. 17: THIS `41` GB IS CORRECT AND IS NOT THE THROW PRODUCT.** It is the **45-component** family — `13 V + 5 A + 27 R` at `0.915` GB each = `41.17` GB, against G's `combined_source` at `41.44` GB measured. The **throw product** is three such matrices, `2.67` GB. Rev. 16 conflated them; the two figures are annotated here so nobody re-derives the same error from this row | **UNRESOLVED** | needs a measured read rate on the storage the components sit on |
| digest recomputation over the component files | **UNRESOLVED** | same read rate |
| **total** | **not established** | the arithmetic term is small; the I/O term is the whole question and nobody has measured it |

**Do not read the small arithmetic term as a small replay.** A replay whose dominant term is unmeasured
is unpriced, and §5.3's *"this lane has not sized it"* stands for the sum.

### 5.8d CONDITIONAL WORK — priced only if a named precondition resolves a particular way

**None of these is part of a Z build. Each is named with its trigger, so nothing is silently absorbed.**

| item | trigger | figure | class |
|---|---|---|---|
| **the joint-baseline campaign** (§3.7b) | Joseph approves the packet **and** authorizes a design at `N` | `3`–`4` additional members at `54.90`/`86.53` each → **`164.7`–`219.6` GPU / `259.6`–`346.1` CPU** | **DERIVED** on **TRANSFERRED** per-member costs |
| a **2-D grid** instead of the implemented diagonal | Joseph rules `"jointly"` means a grid | **code, not compute** — a second environment variable and a launcher change | **MEASURED** (one shared `MNV_EST_SEED_OFFSET`, §3.7b) |
| **`PM-6`** — `‖x_cv‖` for G. **⚠ REV. 16: NO LONGER A `D4` PREREQUISITE** — `11b` is restated over vectors **Z's own writer persists**, so Z's denominator never leaves Z's product | it would now answer a narrower question — **G's** null ratio under §3.7a's normalizer, which G's product cannot supply either | **≈ 0 task-h** — a bounded read of `hXSecND_flat` | **MEASURED** that the key exists (`adopt_unified_5d.py:116-120`) |
| a standalone **null-determinism control run**. **⚠ REV. 17 REVISES IT AGAIN AND UNPRICES IT.** Rev. 16 called it *"the only route"* to a defensible bound; **withdrawn** — §3.7a names three routes and the cheapest is **code, not compute** (pin `num_threads`/`deterministic`/`force_row_wise`) | §6.4 requires the bound fixed **before** production, so arm 7's own `--null` is too late — **and if the control runs on Z's own bank, §6.4 is engaged and needs a ruling.** Three gaps must be answered first: a within-envelope null does **not** measure a between-envelope shift; the repeat count needs a coverage/confidence objective and its sampling assumptions; and the estimator of `B` must be **predeclared**, because two arms do not prevent tuning | **UNPRICED. ⚠ REV. 16'S `≈11.6` GPU TASK-H IS WITHDRAWN — wrong operation, wrong partition.** An invocation is a whole `do_combine` (bank load, slab load, three `10,694²` assemblies), not *"`2` CV unfolds"*; and the combine is **CPU** — `sbatch_uthrow_combine_5d_fast.sh:4`, `--qos=shared --constraint=cpu --cpus-per-task=16 --mem=90G --time=03:00:00`. **Reservation bound `3n` CPU task-h**; spend **UNRESOLVED**, the same missing measurement §5.2 leaves the cause-4 second unfold unpriced for | **§0.0's rev.-2 correction row 10 already recorded that `--null` runs in the CPU combine step and the `43.5`-min basis is a GPU arm-3 time. Rev. 16 priced a new row off it anyway** |
| **endpoint rebuild** | **only if** `PM-3`'s availability/provenance/compatibility check **fails** | unpriced, deliberately | historical SKIPs establish neither present availability nor mandatory retraining |
| cause-1's **disclosure** and cause-5's **path re-trace** | closure conditions | **0 task-h** — a publication act and a static read | §6.2, §6.1 |
| the **five inflation gates**, the **cause-3 dominant-block refusal**, and the **`r_null` reconstruction** | required for `C`/`T` | **code, not compute** | §1.3b, §4 rows 10–11, §3.7a |
| **⚠ NEW IN REV. 16 — persisting `x_cv`, `x_cv2` and the support predicate** in Z's throw product | `11b`'s operand; required for `C`/`T` whatever `D4` decides | **code, not compute** — `1.05` MB of product, **`3.9e-4`** of the `2.668` GB throw product (⚠ rev. 17: rev. 16 divided by `41` GB, a different object) | **MEASURED** product size (§5.9); **DERIVED** fraction (§3.7a) |
| **⚠ NEW IN REV. 16 — a correlation-sensitive leg** (`s_proj`, `s_corr` or `s_eig`) | Joseph answers §3.7d's disposition with *"add a leg"* rather than *"narrow the claim"* | **NO PRODUCTION.** `s_proj`'s functionals already exist as code (`project_cov_nd.py`); `s_corr` is one matrix per member; `s_eig` is one `10,694²` eigensolve per member | **MEASURED** that both statistics are diagonal-only (§3.7d) |

### 5.8e CONTINGENCIES — what the estimates do not carry

**These are not line items. They are reasons every figure above can be wrong in the unfavourable
direction, and `R5` charges them in full.**

1. **The CPU column carries at least a `±60%` single-arm swing.** **MEASURED across two complete
   populations:** arm 5 went `30.94 → 49.11`, **`+58.7%`**, and `AMENDMENT` §3c/§3e attribute it to
   on-node contention that *burns* CPU, not to queue waiting. Applied to a member this alone moves
   `N` from `5` to `4` (§3.7b).
2. **Failed, cancelled and timed-out tasks count in full** under `R5` §3. A `374`-task round with any
   failures costs more than a clean one and produces the same one Z.
3. **Arm 4 holds its ceiling with only `12.4%` headroom on a rising trend** (`AMENDMENT` §3d), and this
   document proposes raising no ceiling.
4. **A hold-style dispatch charges to its timeout.** The observed `03:00:03` instance metered `3.00`
   task-hours for `00:47:58` of work (§5.2a). That is a hazard to design out, not a price to plan on —
   and it is a *design* hazard, so it is inside this lane's reach and not the scheduler's fault.
5. **Every per-member and per-arm figure is a prior from a different subject.** No Z arm has ever run.
   §5.7 item 1 governs and nothing in §5.8 weakens it.
6. **⚠ NEW IN REV. 7 — a 7-day full-system outage sits inside the `R5` window, and the usable
   scheduling window is `16 d 15 h` in two blocks, not `24` days** (§5.9b). §5.3's *"24 days 1 hour"*
   measured the calendar. **This may bind harder than the ceiling** for a `4`–`5`-round campaign and
   nobody had asked the question.
7. **⚠ NEW IN REV. 7 — array launches that abort produce nothing and still charge.** Three of eight
   `det5dBKG` launches aborted at `4`–`75` s (§5.9 item 7). `R5` §3 charges them in full.
8. **⚠ NEW IN REV. 7 — the ceiling itself is contested by `12.59` CPU task-h and the gap grows.**
   `D5`. It does not move `N`, and it does move the headroom every other figure is quoted against.

### 5.8f One named cost-reduction opportunity, recorded as an opportunity and NOT as a saving

**MEASURED.** `unified_throw_cov.py:544-549` writes `C_unified`, `C_blocksum` and `C_cross` with nested
Python loops — `3 × 10,694² ≈ 3.4e8` `SetBinContent` calls — and `unified_throw_cov_5d.py`'s header
records that *"do_throws, do_blockunits, do_combine, the jitter null — is inherited unchanged"*, so that
is what arm 7 executes. **The repository already contains the fast form:** `adopt_unified_5d.py:58-59`'s
`_write_th2`, whose docstring is *"Fast dense TH2D write via the writable ROOT buffer (avoids 1e8
SetBinContent calls)"*, and the matching reader `_th2` at `:46-49` uses `np.frombuffer` rather than a
loop.

**No saving is claimed.** Arm 7's measured round-2 actual is `0.58` CPU task-h in total, so the
opportunity is bounded above by a small number, and **this lane has not measured PyROOT's
`SetBinContent` rate** — the local environment has no ROOT (`perlmutter-root-tf-env-split`). It is
recorded because a reader pricing arm 7 for a `4`–`5`-member campaign should know the writer has a
faster form sitting beside it, and because **adopting it would be a code change requiring its own
byte-level equivalence check**, not a free win.
## 5.9 RELAYED OPERATIONAL EVIDENCE — NEW IN REV. 7, AND ITS PROVENANCE IS PART OF IT

**This subsection is NOT this lane's measurement.** It relays two read-only evidence packets produced by
the **operational-preflight session** (`preflight [e11e6d]`, live read-only SSH to Perlmutter, login31
pinned).

**⚠ THE EVIDENCE IS COMMITTED, NOT ON THIS BRANCH, AND THE CITATION MOVED IN REV. 9 — cite
`1422569c`.** Branch **`lane/pm-root-inspection-20260906`**; chain measured here, child to parent:
`1422569c → cd41ff41 → 21b3d567 → 641c6812`, so **this document's rev. 7 is their root and none of them
is an ancestor of this tip.**

**Rev. 8 cited `cd41ff41` and that revision has two known errors in its `README.md`**, both self-reported
by the preflight session: it says *"four earlier jobs"* in the `cron` waker lineage where there are
**five, six counting the live waker `57712764`** (`57275989`, 9 attempts, was dropped in transcription);
and it states the array negative result **without its covering-search boundary** — that sweep is three
**discontiguous** queries totalling `≈28` days with absences of `22` and `3` days, not the contiguous
span the observed `Start` range invites, because `sacct` selects on **runtime overlap** and observed
days overstate what the search reached for.

**Verified here rather than taken on trust:** `git diff cd41ff41 1422569c` touches **`README.md` and
`DIGESTS.txt` only**, `26` insertions / `5` deletions, and inside `DIGESTS.txt` **exactly one line
changes — `README.md`'s own hash.** Both `r5-meter-receipt-INCOMPLETE-*.json`, all four raw `.psv`
dumps and `R5-PREFLIGHT-EVIDENCE.md` are **byte-identical across the two revisions**, so every
digest-bound citation below is unaffected and only the prose moved. **The second of those two errors is
an uncovered inference from absence — the same class as §5.9a — and it was caught by its own author.**

**⚠ THE BRANCH IS ACTIVELY ADVANCING AND THE CITATION DELIBERATELY DOES NOT FOLLOW IT. REV. 12 STATES
THE PIN AS AN INVARIANT INSTEAD OF A SNAPSHOT, BECAUSE THE SNAPSHOT WENT STALE TWICE.** Rev. 10 said
*"six commits"* and named four; rev. 11 enumerated six; the tip was `6b439466`, **seven**, before rev. 12
was written. **A count of someone else's branch is a field this document cannot keep true**, and a
decaying count inside a provenance section is the wrong kind of precision.

**THE PIN: `1422569c`. THE INVARIANT IT RESTS ON, and it is two conditions, not a date:**

1. **The evidence directory is unchanged** — `docs/orchestration/state/preflight-20260906-r5/` — so
   every digest-bound claim in the table above still reads off the bytes this document read.
2. **The seven clauses quoted from `AUTHORIZATION-20260906-pm-root-inspection.md` in §5.6, §5.6a and §7
   item 17 are present**: §1's *"I authorize one CPU-only interactive allocation…"*; §2's
   *"maximum 30 minutes, no GPUs, no automatic retries or…"*; *"do not present it as valid admission
   evidence"*; *"for my separate approval"*; §4's *"This lane will not act on it without his explicit
   approval"* and *"No arming of admission"*; and §3.5's *"`r5_refusal_reason` is called only under…"*.

**THE CHECK, so nobody has to take this on trust or re-derive it — and the normalization step is not
optional, for the reason immediately below:**

```
git diff --stat 1422569c <tip> -- docs/orchestration/state/preflight-20260906-r5/   # must be empty

git show <tip>:docs/orchestration/AUTHORIZATION-20260906-pm-root-inspection.md \
  | python3 -c "import re,sys; print(re.sub(r'\s+',' ',re.sub(r'(?m)^\s*>\s?','',sys.stdin.read())))" \
  | grep -c "<clause>"                                                             # once per clause, expect 1
```

**Why `python3`, stated narrowly in rev. 14 because rev. 13 over-scoped it and the over-scoping was the
same failure one level up.** Rev. 13 wrote *"why `python3` and not `sed`"*, which reads as *any* `sed`
normalizer being unsafe here. **It is not, and a reader acting on that would replace a working command
or distrust a correct green.** Measured on this machine (`uname -s` → `Darwin`, `sed --version` →
`sed: illegal option`, so BSD), against `9c1230fa`, `grep -cF` on the wrapping clause:

| variant | result |
|---|---|
| **A** — `sed 's/^> //'`, one literal prefix, **as the preflight session actually sent it** | **`1`, correct.** BSD and GNU treat it identically |
| **B** — `sed 's/^[[:space:]]*>[[:space:]]\?//'`, **this lane's generalization of A** | **`0`, a false ABSENT** — BSD basic regex does not read `\?` as an optional quantifier |
| **C** — negative control, variant A against a fabricated clause | **`0`, correct** |

**So the divergence belongs to `\?`, and `\?` is this lane's.** Rev. 13 reported the defect accurately
and described its owner loosely; **the working line was the preflight session's and the breaking
generalization was mine**, and this lane also said so the wrong way round in a message to that session
before measuring. The correction is recorded here because a false accusation against a peer is exactly
the sort of thing a record should not leave standing.

**And the generalization was MOTIVATED, which is why `python3` is still the right answer.** Measured:
the record contains **4 bare `>` lines** with no trailing space, which variant A leaves in place as a
stray token — harmless only because **none of the seven quoted clauses crosses one**. So A is correct
*for these seven clauses at this formatting*, and the obvious hardening against the fifth `>` line
someone adds mid-clause is precisely the unportable one. **`python3` removes the class instead of
documenting one instance**, and the control plane is `python3` everywhere else. Both directions of the
replacement were tested: `1` on the wrapping clause, `0` on a fabricated clause that is genuinely
absent.

**⚠ WITHOUT THE NORMALIZATION THE CHECK TESTS THE LINE-WRAPPING, NOT THE TEXT — and rev. 12 published
it that way.** The §2 limits clause is wrapped across a blockquote continuation in the record:

```
> *"Limits: one CPU node, one inspection task, maximum 30 minutes, no GPUs, no automatic retries or
> requeues. Release the allocation immediately when finished. …
```

so a contiguous `grep -F` for that sentence fails on the newline **and** on the `> ` marker.
**Measured here at `9c1230fa`: the naive form reports `1 of 7` ABSENT; the normalized form reports
`0`.** Any clause long enough to wrap is exposed, and an editor reflowing that file would expose more
without changing a word.

**The failure direction is what makes this worth a revision rather than a footnote.** A false ABSENT on
*this* invariant reads as **"the authorization no longer quotes Joseph's limits"** — the worst false
alarm this document can raise. It would move the pin and start a search for a finding that does not
exist, and it would do so **on a correct branch**, which is this repository's catalogued
guard-that-fires-on-every-correct-run shape pointed the other way.

**⚠ AND THIS LANE'S OWN VERIFICATION HAD BEEN GREEN FOR THE WRONG REASON, WHICH IS RECORDED RATHER THAN
QUIETLY FIXED.** The probe string used at rev. 10, 11 and 12 was **pre-truncated at exactly the wrap
point** — `"…no automatic retries or"` — so it passed three tips in a row **without ever crossing the
break it would have failed on**. **A probe shortened to avoid a hazard does not test past it**, and
three green runs said nothing about the clause this document actually quotes.

**RESULT, re-measured at the most recent tip this lane has run it against, `9c1230fa`: condition 1's
diff is EMPTY, and all seven clauses are present under normalization**, the full diff being confined to
the authorization record. **The invariant has held at every tip checked. The check is the authority, not
the list of tips** — a register of shas is the count-shaped field rev. 12 removed. **A further commit on
that branch needs the check re-run, not a revision here**; if either condition fails, the pin moves and
the failure is the finding.

**One of those later commits was itself a finding for this document, and the mechanism is worth
recording because it is repeatable.** `4c30c089` — *"name the command that arms the gate: it is the one
`R5-METER.md` tells you to run"* — is what sent this lane to that runbook, and §5.6a was wrong until it
did. **It reached this document only because rev. 11 audited rev. 10's own count and enumerated what it
had merely tallied.** Reading a cited branch beats counting it; **the measurements in §5.6a are then
this lane's own, taken in this checkout, and are MEASURED rather than RELAYED.** **This document still cites
`1422569c`, and the ground is measured, not assumed:** `git diff 1422569c d7dd2f1c` touches **only**
`AUTHORIZATION-20260906-pm-root-inspection.md`, the evidence directory is untouched, and **all seven
clauses quoted from that record in §5.6, §5.6a and §7 item 17 are present byte-identically in BOTH
revisions** (substring-checked in each). The six removed lines are an *"alternative if there is no
hurry"* paragraph this document never cited.

**⚠ AND THE WHOLE BRANCH IS COMMITTED BUT UNPUSHED, WHICH IS A DEFECT IN THIS DOCUMENT'S CITATIONS
RATHER THAN IN THE EVIDENCE.** Measured here, with a positive control because a zero-row query is not a
measurement on its own: `git ls-remote origin 'refs/heads/lane/*'` returns **exactly two** rows —
`lane/cause3-voi-20260906` at `47494dbe` and `lane/y-cause7-spec-and-scope` at this document's own tip —
and `refs/heads/lane/pm-root-inspection-20260906` is **absent**, while the same command spelled the same
way resolves the control. **So `21b3d567`, `cd41ff41`, `1422569c` and `d7dd2f1c` exist in this local
repository and nowhere a reader can fetch.** Rev. 8 and rev. 9 wrote *"COMMITTED"* and let it read as
*"available"*; **committed and pushed are different branch properties and this document conflated
them.** Read every off-branch sha below as **locally resolvable only** until §7 item 18 closes.
**This lane does not push another lane's branch**, and would not push this one in particular — it
carries an authorization Joseph has not ruled on, and publishing it would give an undecided proposal
the reach of a settled record.

`1422569c` carries
`docs/orchestration/state/preflight-20260906-r5/` — `R5-PREFLIGHT-EVIDENCE.md`, `DIGESTS.txt`, four raw
`sacct` `.psv` dumps, and two receipts named
**`r5-meter-receipt-INCOMPLETE-{live,fromfile}.json`** — plus
`AUTHORIZATION-20260906-pm-root-inspection.md` and `PREDECLARATION-20260906-pm-root-inspection.md`.
**Note the filenames: the incompleteness is carried in the identifier, not only in the prose.**

**Nothing from it is committed AT THIS BASE, this record commits none of it, and
`docs/orchestration/state/r5-meter-receipt.json` — the path `campaignctl` admission turns on — still does
not exist.** Two sessions shared this worktree while both packets were produced, so the RELAYED /
RE-VERIFIED HERE split below is a statement about **who measured what**, not about who typed it.

**Two of its claims were re-verified HERE, against files in this checkout, before anything downstream
was changed. The rest is relayed and labelled as such** — a peer's report is not a measurement I took,
and the distinction is load-bearing in this campaign.

| # | claim | status here |
|---|---|---|
| 1 | a genuine `r5_meter` receipt now parses real Perlmutter `sacct`; spend `0.0` GPU / `0.0016667` CPU task-h, one task, all flags false | **RELAYED.** §5.6's *"whether real Perlmutter `sacct` output parses cleanly through it is unmeasured"* is answered — **by a receipt that is NOT COMMITTED**, so §4 row 3 still gates every compute row |
| 2 | that receipt **undercounts**: the one in-window task is a self-requeueing waker with `Restarts=1990`, and `--duplicates` gives **953 instances, `12.5903` CPU task-h** on the same window | **RE-VERIFIED HERE.** `r5_meter.py:380-392` `_sacct_argv()` carries no `--duplicates`, and `_parse_sacct_dump` keys on job id alone — `:270` raises *"conflicting rows for task identity"*. **So `--duplicates` is not a drop-in fix, and the gap is a SPECIFICATION question against `R5` §3's *"retried tasks count in full"*.** `D5` |
| 3 | `57128458`'s parent metered `ElapsedRaw = 10,803` s against a `10,800` s request — elapsed **exceeds** the wall request, which a request cannot do | **RELAYED, and it settles §5.2a on the scheduler's own record.** The `3.00` was a hold that stayed allocated, not a wall-request charge |
| 4 | `j28_adopt_5d` = `56429334`, COMPLETED, **`1,883` s = `0.5231` CPU task-h**, `shared_milan_ss11`, against a `4:00:00` request | **RELAYED. It replaces the assemblies' `4.0 PROPOSED, UNVERIFIED` with a MEASURED UPPER BOUND on the pair** — the two assemblies are a subset of that job's four operations, and the job completed, so the pair took **≤ `0.5231`**. Direction established, for once, because a subset of a completed job is bounded by it. **It licenses no point estimate** |
| 5 | no `budget5d` / `combine_5d_budget` row exists anywhere in retained accounting (`2026-07-01` → now, `3,994` rows, coverage verified); the 4D analogue `budget4dCc` was CANCELLED at `0` s | **RELAYED. `unmeasured` stays and is now a covered absence rather than an uncovered one** |
| 6 | `det5dBKG` `57753244` is `shared_gpu_ss11`, **a100** — n=19, min `2,511` s, median `2,605` s, max `2,730` s, sum `13.7617` GPU task-h | **RELAYED, and it confirms §5.2's standing warning that the `43.5`-min figure is a GPU time.** The distribution is tight on the full-length arrays |
| 7 | across eight `det5dBKG` array launches, **three aborted at 4–75 s and produced nothing**, and the 126-task mean is `27.56` min — *"a number describing no run that happened"* | **RELAYED, and it is a contingency, not a price** — §5.8e item 2. The aborted arrays' elapsed still counts under `R5` §3 |
| 8 | G's own committed key list is **13 keys and contains no CV vector and no norm** | **RELAYED, and it independently supports §3.7a's auditability requirement** without depending on a ROOT read |
| 9 | **`PM-2` is dischargeable, and two statements in THIS document are false** | **RE-VERIFIED HERE — see §5.9a.** Both corrected in place |
| 10 | `PM-1`, `PM-4`, `PM-5` and `PM-3`'s grid/footing arm are **BLOCKED**: they need to open a ROOT, and on the login node `uproot` is absent from both interpreters while PyROOT segfaults on import in the project conda env | **RELAYED.** A `TKey` listing is a header read, not a `41` GB scan, so these are cheap once unblocked — but **installing `uproot` changes the environment rather than reading it**, and the preflight session correctly declined. **`PM-3`'s availability arm IS discharged**: all ten endpoints present in `universe_sweep_bkgaware/`, all dated `2026-07-14`. **Trap recorded: a second, non-bkgaware set of the same ten filenames sits in `universe_sweep/` dated `2026-06-12` — pin the DIRECTORY, not the filename** |
| 11 | a **7-day full-system outage** `maintenance_20260916` sits inside the `R5` window; and `sacct` refuses queries spanning more than 30 days | **RELAYED; the arithmetic is RE-DERIVED HERE — §5.9b** |
| 12 | **NEW IN REV. 8** — the k=0 round-2 campaign spans **`37.5` h** end to end, at `54.90` GPU / `86.77` CPU task-hours over the same window | **RELAYED — §5.9c.** The GPU figure reproduces §5.2's `54.90` **exactly** by a different route. **It releases §6.7 item 5 from blocker to caveat, and the caveat is that this is ONE realization** |
| 13 | **NEW IN REV. 8** — `uthrow5d_combF` is `shared_milan_ss11`, **CPU, never GPU**: `2,075` / `1,526` / `1,395` s against 3–4 h requests | **RELAYED, and the IDENTITY is the load-bearing part — §5.8b.** `uthrow5d_combF` is `unified_throw_cov_5d --combine`, i.e. **arm 7, already inside the seven-arm round**. It is **NOT** `sbatch_combine_5d_budget.sh` / `budget5d`, which still has no accounting row in any dimension |
| 14 | **NEW IN REV. 8** — the requeue-inclusive figure **moves**: `12.5903` CPU task-h at `08:59Z`, `12.606389` at `09:20Z`, `≈0.05`–`0.07`/day plus hangs, still exactly one distinct job id in the window | **RELAYED — `D5`. ⚠ THE CADENCE IS WRONG BY AN ORDER OF MAGNITUDE and its author withdrew it: `≈0.65`–`0.69`/day, not `0.05`–`0.07` — §5.6b.** The two dated totals stand; the RATE does not. Any percentage taken against it must carry its **measurement instant** |
| 15 | **NEW IN REV. 8** — `PM-4` cannot be discharged as written; the declared ROOT inspection is **authorized by Joseph and committed, and campaignctl still cannot admit it** on four independent grounds | **RE-VERIFIED HERE for the key inventory — §1.3d.** The blocker was returned to Joseph rather than worked around, and **nothing was installed** — the `uproot` question stays his |

### 5.9c THE WALL CLOCK, MEASURED — NEW IN REV. 8, and it releases §6.7's item 5

**RELAYED.** The k=0 round-2 campaign, bounded by time from the first `sbatch` at
`2026-08-30T20:47:32Z`:

| | |
|---|---|
| tasks in the window | **376** (this document's arm-membership view gives 374; the two extra are the time-bound's, not a new population) |
| first task start → last task end | `2026-08-30T21:29:20` → `2026-09-01T10:58:02` |
| **end-to-end wall-clock span** | **`1 d 13 h 28 m 42 s` ≈ `37.5` hours** |
| task-hours over the same window | `54.90` GPU / `86.77` CPU |

**The task-hours corroborate this document's anchor rather than replacing it.** `54.90` GPU is
`54.90` — exact agreement with §5.2's round-2 figure, arrived at by a different route (a time window
versus arm membership). CPU is `86.77` against `86.53`, a `0.24` task-h difference the preflight session
attributes to the two extra in-window tasks. **§5.2's numbers stand; treat this as an independent
confirmation, not as a new number**, and do not mix the two CPU figures in one sentence — they are over
different populations.

**Against §5.9b's split window, `≈1.56` days per round gives:**

| block | length | rounds that fit |
|---|---|---:|
| **A** — now → outage start | `10 d 3 h 50 m` | `≈6.5` |
| **B** — outage end → `R5` stop | `6 d 11 h` | `≈4.1` |

**So a `4`–`5`-member campaign fits the wall clock inside EITHER block, without straddling the outage.**
§6.7's readiness item 5 — *"the one constraint no decision can relax"* — is **released from blocker to
caveat**.

**⚠ AND THE CAVEAT IS THE PART TO CARRY, IN THE PREFLIGHT SESSION'S OWN WORDS.** `37.5` h is **one
observed end-to-end span under the queue conditions of 2026-08-30**, already inclusive of whatever queue
wait those 376 tasks met. **It is one sample, not a distribution.** A busier machine — or the pre-outage
rush in the days before `2026-09-16`, which is exactly when a campaign would run — could move it
substantially, and nothing in the record bounds that. **The correct sentence is *"fits, on one measured
round at that week's queue depth"*, and this document does not write the shorter one.** It is also the
same volatility §5.7 item 2 already measures on the CPU column: `+58.7%` on one arm between two rounds.

### 5.9a ⚠ TWO FALSE STATEMENTS IN THIS DOCUMENT, CORRECTED — and the failure is mine and familiar

**RE-VERIFIED IN THIS CHECKOUT**, `nd-unfolding/uq_5d/readopt_20260811_footing/STAMPED_HASH_RECEIPT.slurm-56720356.json`
— `job_id 56720356`, `created_at_utc 2026-08-12T05:46:19+00:00`, `schema stamped-footing-candidate-receipt-v1`:

| key | path recorded | sha256 | size | mtime, re-derived from `mtime_ns` |
|---|---|---|---|---|
| `combined_bkgaware` | **full path** `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` | `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` | `41436632945` | **`2026-07-14T20:59:17Z`** |
| `uthrow` | `nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` | `4cb02ae767c887b5fc43554a8f2c4a1821d25fdf547aeeeedbe8b3d57f8b4281` | `2668021041` | `2026-08-07T00:38:46Z` |
| `A1_stamped_meancentered` | G itself | `4f168e83…` (matches §1.1) | `892170881` | `2026-08-12T05:43:34Z` |

**So §1.1's `G.combined_source` row — *"name only; no digest for it is recorded anywhere in the tree"* —
is FALSE, and §4 row 5's *"using S's digest as G's is the substitution `PM-2` exists to prevent"* is
FALSE.** G's own build receipt records that digest **four days before S read the file**, and S's
manifest is a second, differently-originated, agreeing measurement rather than a substitution.

**The failure class is one this lane has already been burned by and it is recorded rather than quietly
repaired.** *"Nowhere in the tree"* is an inference from absence asserted **without a covering search**,
about a file sitting in **G's own directory in this very checkout**. It is the same shape as rev. 1's
missed `no-fourth-grade-token` record. **A claim of absence needs the search that would have found it,
stated beside the claim.**

**What survives, and it is a real requirement on Z rather than a caveat.** The launcher hashes **after
building**, so the digest binds the bytes at `05:46:19`, not by direct observation the bytes read at
`05:43:34`. The gap closes on the same receipt's `mtime_ns = 2026-07-14T20:59:17Z`, which predates the
job — and the preflight session reports `ctime == mtime` on the cluster today, `ctime` being the field
userspace cannot set, which excludes `cp -p` / `touch -r` / `rsync --times`. **Irreducible residual:**
`/pscratch` is purgeable, a restore could reconstruct metadata, and the chain runs partly backwards from
a later digest.

**REQUIREMENT ON Z'S RECEIPT (§1.5), and it is the durable lesson:** stamp
`path + sha256 + size + mtime_ns + inode + device` **at OPEN time, not at job end.** G's receipt gets
four of six fields, at the wrong instant. **`PM-2`'s disposition is not this lane's to take** — it is a
`SCOREBOARD`/`OPEN_ITEMS` act by whoever owns the row — but the evidence for discharging it now exists
and this record says so.

### 5.9b THE SCHEDULE, WHICH MAY BIND HARDER THAN THE CEILING — arithmetic re-derived here

**RELAYED:** `maintenance_20260916`, `2026-09-16T13:00Z → 2026-09-23T13:00Z`, **5,248 nodes**,
`MAINT,IGNORE_JOBS`. **RE-DERIVED HERE** from `2026-09-06T09:10Z`:

| span | duration |
|---|---|
| to the `R5` stop `2026-09-30T00:00:00Z` | `23 d 14 h 50 m` |
| **block A** — now → outage start | `10 d 3 h 50 m` |
| the outage | `7 d 0 h 0 m` |
| **block B** — outage end → `R5` stop | `6 d 11 h 0 m` |
| **USABLE SCHEDULING WINDOW** | **`16 d 14 h 50 m`, in two blocks** |

**§5.3's *"24 days 1 hour"* measured the calendar, not the schedule.** A `4`–`5`-member joint-baseline
campaign is `4`–`5` complete rounds of **374 tasks each**, and `AMENDMENT` §3c records that one arm's
tail *"ran at two-way concurrency on `Reason=Resources` for eleven hours"* in a single round. **Whether
four or five such rounds fit into a `10`-day and a `6.5`-day block is not established here, and it is a
question nobody had asked** — the ceiling arithmetic in §3.7b assumes only that the task-hours fit, not
that the wall-clock does.

**And the meter itself expires inside the same window.** `sacct` refuses spans over 30 days (measured by
the preflight session's bisection: 30 d accepted, 31 d rejected; the limit is on **span**, not lookback).
`_sacct_argv()` queries `t0 → now`, so **the meter can measure the complete `R5` window only until
`2026-10-02T13:44:27Z`** — `2 d 13 h 44 m` after the stop (re-derived here). After that the live query
fails and, admission being fail-closed, `campaignctl` closes. **Neither fact is in §5.6.**

---

# 6. THE RULINGS — taken 2026-09-06 on the contract review's recommendations

**These are DECIDED, not proposed.** §0.2 records the authority and how it was given. **The
recommendation text is the REVIEWER's, quoted verbatim; the adoption is Joseph's.** §§1–5 already
incorporate them; this section is where they are recorded so a citation has one home.

**None of them extends `CRITERIA` §0's vocabulary, and none regrades G.**

## 6.1 `(cause 5, Z)` — an artifact-specific "INAPPLICABLE, DISPOSED BY DECISION" outcome is authorized

**The question put:** *"Can independently demonstrated absence of PET-derived inputs terminally dispose
of (cause 5, Z) without four artificial METs?"*

**The recommendation, adopted:**

> *"Authorize an artifact-specific 'inapplicable, disposed by decision' outcome after the complete trace
> and falsifier check. Preserve historical cells and distinguish this from mechanical four-MET discharge.
> RZ requires seven assessments, not seven favourable results."*

**RULED.** `(cause 5, Z)` may be terminally disposed as **`INAPPLICABLE — disposed by decision`**, on
these conditions, all of which are part of the outcome and none of which this record discharges:

1. the **complete construction-path trace** over every module Z invokes — including
   `adopt_unified_5d.py`, which `VL66` did not audit and which `D_Z` runs through (§2.5);
2. the **falsifier check** — no PET-derived product consumed by any module on Z's path;
3. performed by a lane that does **not** own cause 5, per `VL66`'s own weighting caveat;
4. recorded as **distinct from a mechanical four-MET discharge**, with the distinction visible in the
   cell rather than inferable from it;
5. **G's and Y's historical cells untouched.**

**Why this needed a ruling, and why rev. 1's proposed route was wrong.** `CRITERIA` §3:246 admits only
`MET`/`OPEN`/`UNRESOLVED` and discharges only on four METs; `SCOREBOARD` §7b **RULED 2026-08-17** that a
leg outside those three *"can never discharge."* So a cause-5 `N/A` blocks a mechanical seven-MET Z.
**Rev. 1 offered "define a fourth token." That route was already closed on 2026-09-02** —
`DECISION-20260902-joseph-rules-no-fourth-grade-token.md` (`e59df9557e6ec1d21b845d7647c0038662c490713d8a43b2f72cd60bd34dc477`),
Joseph, *"okay I also agree"*: *"`CRITERIA-20260811` §0's vocabulary — `MET` / `OPEN` / `UNRESOLVED`,
discharge on four `MET`s — STANDS UNCHANGED. No token is added for the *permanently unmeetable*
state."* **That record is in this tree and rev. 1 did not open it.** The miss is recorded here rather
than quietly repaired.

**This ruling does NOT reopen it.** It adds no token. It is a **per-cell decision**, and the framework
already distinguishes that from a mechanical discharge: cause 2's CAND cell is *"discharged **by
decision**"* (Joseph, 2026-08-12) while the board's counts table keeps *"causes with four METs"* at
**`0`**. `RZ(ii)` asks for seven **assessments**; a complete assessment whose honest outcome is
"inapplicable" is an assessment, not a gap.

## 6.2 `(cause 1, Z)` — measure-and-disclose closure, irrespective of magnitude

**The question put:** *"Does a complete, artifact-specific measurement plus the required disclosure
permit closure for Z irrespective of magnitude, and what counterfactual applies to non-pair bands?"*

**The recommendation, adopted:**

> *"Permit measure-and-disclose closure once independently verified. Compare both one-sided choices for
> actual ± pairs, including off-diagonal effects and denominator qualifications. Explicitly account for
> the other bands without inventing ± endpoints. The original receipt already includes Flux,
> three-universe 2p2h and normalization unchanged in both totals; changing their construction is a
> proposed criterion extension, not merely filling missing arithmetic."*

**RULED.** `(cause 1, Z)` closes on a **complete, artifact-specific measurement plus the `RULING 1`
disclosure**, **irrespective of magnitude**, once **independently verified**. The measurement's form is
§2.1's six requirements. **The three non-pair bands are accounted for explicitly and their endpoints are
NOT invented**; any change to their construction is a **criterion extension** requiring its own decision,
and this specification does not make one.

**Consistency with `RULING 1`, stated because it is the obvious challenge.** `RULING 1` (2026-09-01)
found cause 1's magnitude *"material enough to need its own statement in the note"* and therefore did not
close cause 1 **for G**. This ruling does not disturb that: G's cell is unchanged, and the note obligation
is not waived — it becomes part of **Z's** closure condition. What is settled is the question `RULING 1`
left open: **that for a new artifact, a complete measurement plus the disclosure suffices, and magnitude
alone does not block.** Writing the disclosure remains a publication act outside `RZ(iv)`.

## 6.3 `(cause 3, Z)` — the joint-baseline quantity, with the narrow scan diagnostic

**The question put:** *"What quantity and outcome rule closes Z's estimator-seed magnitude leg: the
narrow fixed-draw measurement, or variation of the assembled covariance with estimator baselines varied
jointly?"*

**The recommendation, adopted:**

> *"Retain the joint-baseline quantity for a claim about composite Z; do not assume the existing
> 46/50-member family is the necessary measurement design. Treat the narrow scan as diagnostic unless
> substitution is explicitly ruled. Specify favourable, unfavourable and inconclusive outcomes before
> measurement."*

**RULED**, in four parts:

1. **The quantity** for `(cause 3, Z)`'s `M(ii)` is the variation of the **assembled** covariance `C_Z`
   when the sweep-side and throw-side estimator baselines are varied **jointly** — `SCOREBOARD` §2c's
   `(B)`, applied to Z.
2. **The design is open.** The existing 46/50-member family is **not** assumed to be the necessary
   measurement design. §5.4 prices it at 5×–9× over `R5` precisely so that the design question is put
   before the money is.
3. **The narrow fixed-draw scan is DIAGNOSTIC for Z**, not `M(ii)`, **unless substitution is explicitly
   ruled** — which this record does not do. That preserves
   `PREDECLARE-20260901-cause3-mii` §5's own reservation: *"treating it as a substitute for a full
   two-baseline composite scan would require a separate ruling."*
4. **Three outcome classes — favourable, unfavourable, inconclusive — are specified BEFORE measurement**,
   on §4's six-branch model, which `R4` preserves. **A valid large result is not automatically MET.**

**This ruling touches neither `R4` nor the narrow scan's own criterion.** `R4`'s suspension stands;
§1's quantity, §2's footing falsifiers, §3's thresholds `f_agg ≤ 0.0415` / `f_med ≤ 0.0274` and §4's six
branches are preserved exactly. **And permission to measure is not permission to substitute** —
substitution is **not** a third prerequisite for the historical narrow scan, and nothing here adds one.

## 6.4 A scale-relative fixed-seed null bound for Z, fixed before production

**The question put:** *"Should Z use a scale-relative null bound, fixed before production?"*

**The recommendation, adopted:**

> *"Yes, with the numerical bound justified by precision and sensitivity controls before implementation
> — not selected from a favourable production result. This does not retrospectively regrade G."*

**RULED.** Z's fixed-seed null uses a **scale-relative** bound, **fixed before production**, with its
numerical value justified by **precision and sensitivity controls established before implementation** and
**not** chosen from a favourable production result.

**The measured defect this replaces** is §3.1a: `unified_throw_cov.py:517`'s
`tol = 1e-12 * max(‖base‖, 1.0)` evaluates to an **absolute `1e-12`** on a cross-section vector whose norm
is order `1e-37`, so it is roughly `10^25` times the scale it is meant to bound. **It is not a relative
determinism bound.** Choosing Z's bound after seeing Z's null would be a threshold placed to obtain a
verdict — the failure `PREDECLARE-20260901-cause7` §1 `M` and `uq_math.py:128-137` both name.

**This does not retrospectively regrade G**, and it is not a finding that G's null is bad: G's measured
value is `5.8223e-50`, `1.31e-12` of the sqrt-trace — genuinely small *relative* to the scale. **The
defect is in the guard, not in the product.**

## 6.5 WITHDRAWN — the multi-draw cause-4 proposal

Rev. 1 §6.2 asked whether `(cause 4, Z)`'s `M` should require `n > 1` jitter draws. **Withdrawn**, on the
review's directive, adopted: *"Keep cause 4's single-draw referent; requiring multiple draws would be a
separate, optional criterion change."*

The reason is the one rev. 1 gave against its own proposal: **the defect cause 4 names *is* a single-draw
subtraction**, so a multi-draw `M` measures something the defective construction never did. §2.4 retains
the single draw, with its seed named and its one-sample nature stated in the receipt. **Anyone who wants
the multi-draw variant should raise it as a separate, optional criterion change; it is not part of this
contract and nothing in §§1–5 depends on it.**

## 6.6 What remains a criterion question and is NOT ruled here

- **⚠ NEW IN REV. 4, and it is the one most likely to be needed: whether Z's cause-3 acceptance
  boundary may take a DIFFERENT FORM from the narrow scan's.** §3.6d establishes that the predeclared
  `S/U ≤ sqrt(2δ + δ²)` rule assumes an omitted **independent contribution added in quadrature**, and
  that variation among **assembled covariances** — §6.3's ruled subject — is a change *in* `U` rather
  than an `S` added to it, pointing instead at `|U' − U| / U ≤ δ`. **Adopting a different boundary form
  is a criterion question, not a completion detail**, and it is surfaced here for Joseph's separate
  decision. §6.3's *quantity* is unaffected either way; only the acceptance mathematics is at issue.
  **HOW THIS ONE MUST BE PUT, and it is a constraint on the packet rather than on the answer.** The
  reviewer's standing recommendation, adopted: **approve the concrete statistic, its denominator, the
  precision target and the boundary TOGETHER — never a formula detached from those definitions.** A
  boundary approved in the abstract would be an authorization over an object nobody has defined, and
  §3.6d's whole finding is that the formula's validity depends on what the statistic is. **So this item
  is not ready to be decided today**, and nothing here asks for a decision: it is ready when §3.6b's
  definitions exist and can be put to Joseph as one package.
  **⚠ SUPERSEDED IN REV. 7 — THE PACKAGE NOW EXISTS.** §3.7b supplies the statistic, its denominator,
  the precision target and the boundary as one packet, so the condition this bullet set is met and
  **§6.7 puts it.** The constraint itself is unchanged and is honoured: the four are put together, and
  no formula is offered detached from its definitions.
- **Whether the three non-pair bands' construction should change** (§6.2) — a criterion extension nobody
  has proposed and this lane does not.
- **Whether the narrow fixed-draw scan may SUBSTITUTE for the joint-baseline quantity** (§6.3) — reserved,
  by `PREDECLARE-20260901-cause3-mii` §5's own terms.
- **Whether `(cause 6, Z)` is graded on `6a` as well as `6b`** (§2.6c item 5) — a scoping call for the
  grading lane, to be made explicitly rather than inherited.
- **Whether Z regenerates or reuses `C_stat`/`C_ML`** (§2.6b) — a **scientific** decision needing a
  stated rationale, not a criterion change.
- **Reconciling `CRITERIA` §0's declared-three-against-used-seven vocabulary** — named by
  `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` §3 as *"the better-motivated change"* **if**
  §0 is ever opened. It is not opened here.

## 6.7 WHAT IS NOW READY TO BE PUT TO JOSEPH — NEW IN REV. 7, AND NOTHING HERE IS DECIDED

**§6.6 said the boundary-form question *"is not ready to be decided today"*, on one condition: the
statistic, the denominator, the precision target and the boundary must be approved TOGETHER. That
condition is now met.** §3.7 supplies all four for both criteria. This section states the decisions and
takes none of them. **`BEN-381` bars this lane from grading these legs, and §0.2's pattern governs: the
framing below is this lane's and open to challenge on its merits; any adoption is Joseph's.**

**Five decisions. `D1` and `D4` are packets and must be answered as packets — a boundary approved apart
from its statistic would authorize a number over an object nobody has defined.** `D5` arrived with the
operational evidence packet (§5.9) and is **not part of Z's contract**; it is here because it moves the
ceiling every figure in §3.7b and §5.8 is quoted against.

### `D1` — the `(cause 3, Z)` acceptance packet (§3.7b)

**⚠ REVIEWED IN REV. 16 AND NOT READY FOR ADOPTION AS WRITTEN. `D1a` and `D1b` stand; `D1d`'s FORM
stands; `D1c`'s numbers are WITHDRAWN as acceptance criteria, and a correlation disposition is added.
§6.8 carries the disposition; the table below is rev. 7's and is kept unedited as the record of what was
proposed.**

| part | what is proposed | what it turns on |
|---|---|---|
| **D1a** the two statistics | `s_agg` = max over the declared offset set of the relative change in `√Tr C_Z`; `s_med` = the same for the printed per-bin median `median_i(σ_i/x_i)` | the **max** rather than a sample SD, because the population is the finite declared offset set and no distributional inference is made — `PREDECLARE-20260901-cause3-mii` §1's own position |
| **D1b** the denominators | Z's **own as-built `k = 0` member**: `√Tr C_Z^(0)` and `q^(0)` | both named beside their numerators; both statistics exact, so no model connects them to a printed number |
| **D1c** the **precision target** | declare that Z's aggregate is reported to **3 significant figures** and its per-bin median to **4**, matching the existing macro format | **this is a declaration, not a measurement.** Both macros are defined and **never printed** (measured, with a positive control), and their values are J's, quarantined. Nobody can measure Z's `δ` until this is declared |
| **D1d** the **boundary form** | **direct relative change**, `s ≤ δ` | at the format prior this is **`0.0861%`** and **`0.0374%`**, i.e. **`48.2×` and `73.1×` tighter** than the narrow scan's `4.15%` / `2.74%` |

**`D1d` is the substantive one, and it is not a choice between formulas.** Quadrature would be correct
if baseline variation were **an omitted independent contribution added to the budget**. Under the
operative rulings it is not and may not be — `PREDECLARE-20260901-cause3-mii` §5 (*"It does not add
`C_seed` to the uncertainty budget. A magnitude measurement and budget adoption are different
decisions"*) and §1.3a property 3. **So the question is: is baseline variation a stability requirement
on a number Z reports, or a candidate budget component?** The first is the direct model; the second is a
budget-adoption decision this record neither makes nor invites.

### `D2` — the per-bin leg's precision target (§3.7b item 3)

**⚠ REVIEWED IN REV. 16. OPTION (i) IS NO LONGER RECOMMENDED, and the framing below is itself the
error:** the absence of a data release does not make this a formatting question. **The tolerance and the
coverage fraction are scientific choices** — §6.8 `D2`. The three answers are kept unedited as the record
of what was proposed.

**The note prints no per-bin uncertainty, so no per-bin `δ` exists to derive.** Three answers, and the
gap is real under all of them:

1. **Recommended.** Add a **third, model-dependent leg** — `median_i(m_i) ≤ δ_med` under a stated
   uniform-movement model — so the per-bin distribution binds, with the model written in the same
   sentence as the number.
2. Derive a per-bin `δ` from a **data release with a declared precision**. None exists in this tree, and
   creating one is a publication act outside `RZ(iv)`.
3. **Report the per-bin distribution and gate only the two exact legs.** Honest, and weaker than the
   narrow scan's contract — which §3.7b states rather than disguises.

### `D3` — the joint-baseline design: `N`, the offset set, and diagonal-or-grid (§3.7b)

**⚠ REVIEWED IN REV. 16 AND SUPPORTABLE CONDITIONALLY — the only one of the four. A conditional yes to a
small diagonal diagnostic; NO grid is required; and `N = 5` is a planning proposal, not demonstrated
capacity. §6.8 `D3` carries the four prerequisites.**

**The member is measured, not designed** — one shared `MNV_EST_SEED_OFFSET`, seven launchers, and an
eighth that refuses it. What remains is genuinely a choice:

- **`N` and the offset set.** **A planning estimate** — *not* a demonstrated capacity (**⚠ corrected in
  rev. 16**) — puts **`N = 4`–`5` total** inside `R5` at **`86.5%` of the CPU ceiling**, against a
  historical `46`/`50`-member design at **`5.1×`–`8.7×` over**. The estimate admits no middle.
  **Four additional members are nominal priors of `219.6` GPU / `346.1` CPU task-hours, before
  applicable campaign costs and contingencies.** **A four-or-five-member maximum-deviation result is weak evidence of stability and
  strong evidence of sensitivity** — the asymmetry is real, and whether it is worth the ceiling is
  Joseph's call, not an arithmetic one.
- **Diagonal or grid.** The launchers implement the **diagonal** `(42+k, 1000+k)`. If §6.3's
  *"jointly"* means a 2-D grid, that is **a second environment variable and a launcher change — code,
  not compute** — and it must be settled **before** the offsets are declared, not after.
- **Nothing here authorizes a run.** `D-RESOURCE` does not exist, `R5`'s ceilings are a prohibition, and
  §4 row 3's meter receipt gates every row that costs compute.

### `D4` — the fixed-seed null packet (§3.7a)

**⚠ REVIEWED IN REV. 16 AND NOT READY FOR ADOPTION AS WRITTEN. `D4a` stands. `D4b`'s `ε` is WITHHELD;
`D4c`'s operand is CORRECTED and split into `11b`/`11c`; `D4d` gains the persisted vectors. §6.8 carries
the disposition; the table below is rev. 7's and is kept unedited as the record of what was proposed —
including the sentence beneath it, which called this the least contentious of the four.**

| part | what is proposed |
|---|---|
| **D4a** normalizer | `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖`, both over the reported support; `sqrt(Tr C_Z)` and the per-bin max **rejected on the record**, the second retained as a reported diagnostic |
| **D4b** `ε` | `ε = n_iters · n_rep · numpy.finfo(float64).eps`, a **formula with imported operands**, `= 1.1873e-11` at Z's expected shape. A precision control; the sensitivity controls are reported beside it and are `~8` orders looser |
| **D4c** reject condition | new **`11b`** in §3.3 — the ratio must be **independently reconstructible**, with `‖x_cv‖` recomputed by the validator from the production ROOT's `hXSecND_flat` |
| **D4d** receipt fields | the production ROOT's path, sha256 and key; the recomputed `‖x_cv‖` and `n_rep`; the per-bin diagnostic with its argmax bin |

**`D4` is the least contentious of the four** — it changes a clamp into a formula and adds an
auditability requirement — but it is still a criterion and this lane may not adopt it.

### The readiness verdict — RECLASSIFIED IN REV. 15 INTO THREE AUTHORIZATIONS

**Rev. 7–14 answered one question — *"is the contract ready for an implementation authorization?"* —
with one list, and the list was wrong in a way that could not be fixed by editing it.** It named
*"code that does not exist"* and *"two independent pre-launch reviews"* as things standing between here
and permission to implement. **Neither can be.** An implementation authorization **is** permission to
write that code, so requiring the code first is circular; and a pre-launch review reviews something
before it is **launched**, which is a production question. Conflating the three put a compute-side
prerequisite in front of a zero-compute act and made the specification look further from usable than it
is.

**Three authorizations, in order. Each has its own prerequisites and none inherits the next one's.**

#### Tier 1 — SPECIFICATION ACCEPTANCE: accepting §§1–5 as Z's contract

| | |
|---|---|
| **what it permits** | citing this document as the contract Z is built and graded against |
| **what it costs** | nothing |
| **prerequisites** | none outstanding. Five independent contract-review rounds are closed; §§1–4 and §5's census carry their own evidence classes |
| **status** | **READY. The act is Joseph's and nobody else's** |

**§7's nineteen items are not prerequisites for this tier — they are its content.** A specification
that names its gaps, each with the act that closes it, is complete **as a specification**; one that
hides them is not. Accepting §§1–5 accepts those nineteen as the declared state of knowledge.

#### Tier 2 — IMPLEMENTATION AUTHORIZATION: permission to write Z's producer, validator and tests

| | |
|---|---|
| **what it permits** | writing code and fixtures. **No compute, no scheduler, no artifact** |
| **what it costs** | **zero task-hours.** §5.8's local timings put the validation arithmetic at minutes on a laptop-class machine at the real `10,694` dimension |
| **prerequisites** | Tier 1, plus — **for the two parts that depend on them** — the open items on `D1`–`D4` |
| **status** | **READY for most of the work today; two parts wait, and rev. 16 changed WHAT they wait on** |

**Most of the implementation is unblocked by the specification alone.** §1.3b's five inflation gates,
the `g^c` reconstruction, §3.4's mutation set, the cause-3 dominant-block refusal, the cause-4 jitter
re-add, the `V`/`R`/`A` partition gate, Z's receipt schema and the whole validator skeleton are all
specified to the file-and-line and need no decision. **None of that is touched by the contract review of
`D1`–`D4`**, which reopened neither the assembly algebra nor any ruling.

**⚠ AND REV. 16 MOVES WORK INTO THIS TIER RATHER THAN OUT OF IT.** Three of the review's remedies are
pure code and are **newly specified and newly authorizable**:

- **persist `x_cv`, `x_cv2` and the support predicate** in Z's throw product (`1.05` MB; §3.7a) — this
  is the fix for `11b`'s operand and it is a writer change, not a decision;
- **`11b` restated and `11c` added** (§3.3), both implementable now;
- **the outcome branches over a declared leg set `L`** (§3.7b item 5), which must be written this way
  **before** any third leg exists, not after.

**Exactly two parts still wait — and the review changed their character, which is stated plainly rather
than absorbed:**

| part | rev. 15 said it waited on | rev. 16: what it actually waits on |
|---|---|---|
| the fixed-seed null check's **numeric bound** | `D4` — *"a decision"* | **`D4`, plus specification work that does not exist yet.** `ε` is withheld; **`B ≤ S` must be established and `ε` argued within `[B, S]`** (⚠ rev. 17). **And one route to `B` is itself Tier-2 work that could be done today** — pinning `num_threads`/`deterministic`/`force_row_wise` in `make_estimators`, which costs no compute. **The normalizer, the persistence and the reject conditions are unblocked and can be written now** — only the constant is blocked |
| the **cause-3 acceptance code** | `D1`, and `D2` for its per-bin leg | **`D1` and `D2`, plus a use-based justification and a correlation disposition.** The **statistics** are unblocked and can be written today — `s_agg`, `s_med`, the per-bin distribution, the leg-set machinery. **Only the boundaries are blocked**, and §3.7d's candidate legs are specified enough to write behind a flag |

**The honest summary: in both cases the STATISTIC is authorizable and the NUMBER is not.** That is a
better position than rev. 15 described, not a worse one — code that computes a statistic and refuses to
grade without a declared boundary is exactly what §3.3 condition `4c` already requires.

**Not prerequisites at this tier, stated because rev. 7–14 listed them and they do not belong:** the
code itself; the two independent pre-launch reviews (`PLAN-20260905` #17), which gate a **launch**;
`D-RESOURCE`; the committed meter receipt; and `D3`'s member count, which prices a campaign and
constrains no line of code.

**One real qualification.** §3.4 requires fixtures built from the **producer's own** objects, and some
of those are cluster-resident. **The code can be written now; a few fixtures need the `PM-*` reads,
which are reads and not runs** — and those reads are themselves blocked only by a ROOT-capable
environment (§7 item 1).

#### Tier 3 — PRODUCTION AUTHORIZATION: permission to build Z

| | |
|---|---|
| **what it permits** | spending against `R5` to produce the artifact |
| **what it costs** | §5.8b's production block, and `D3`'s campaign on top if taken |
| **prerequisites** | everything below, and here the code legitimately **is** one |
| **status** | **NOT READY, and no single act makes it ready** |

1. **Tier 2 discharged and the code written**, including Z's validator and the five inflation gates.
   At this tier the code is a prerequisite because a run without a validator produces an ungradable
   artifact.
2. **The two independent pre-launch reviews** (`PLAN-20260905` #17). Worker agreement is not
   independence.
3. **`D-RESOURCE`** — an exact resource authorization naming a Z run. It does not exist (§4 row 19),
   and `R5`'s ceilings are *"NOT authorization to spend up to"* them.
4. **A committed `r5_meter` receipt** — and per §5.6b that is now a deliberate, queue-wide arming act
   rather than a clerical step.
5. **The `PM-*` reads** — `PM-1`, `PM-4`, `PM-5` and `PM-3`'s grid arm, plus §7 item 17's binding of
   G's production-CV input, on which `PM-4` and reject condition **`1`** fail together. **⚠ NARROWED IN
   REV. 16:** `11b` no longer depends on that binding — it is restated over vectors **Z's own writer
   persists** — and **`PM-6` is no longer a prerequisite at all**, because `D4`'s denominator no longer
   comes from outside Z's product. Reject condition `1`'s mask and row-order digests still need it.
6. **`D3`**, if the joint-baseline campaign is taken: `N`, the offset set, and diagonal-or-grid.

**The schedule is a caveat at this tier, not a prerequisite** (§5.9c): `4`–`5` rounds fit inside either
block of the split window on one measured realization, and one realization is what that is.

#### What this reclassification does and does not change

**It moves nothing.** No gate, no count, no grade, no cell. **It changes only the question each
prerequisite is an answer to**, and the consequence is that **`RZ(v)`'s five deliverables are complete
and Tier 2 is reachable today for most of Z's code** — which the previous single list obscured by
counting production prerequisites against a zero-compute act.
### `D5` — ⚠ RESOLVED IN REV. 15 BY THE LANDED REPAIR (§5.6b). Retained as written, for the record

**The repair adopts the attempt-summing reading**, which is the direction §5.9 flagged: `sacct -X -D`,
an attempt is `(JobID, Start)`, and every attempt of one job id is charged. **`D5` is therefore off
§6.8's sheet.** The alternative reading is named in the finding and isolated in one function, so
Joseph can still overturn it cheaply. The text below is rev. 9's and is kept unedited.

**`R5` §3 says retried tasks count in full. The meter, as landed, does not count them.** Measured on the
same window: **`0.0016667` CPU task-h deduplicated, `12.5903` with `--duplicates` at `2026-09-06T08:59Z`**
— 953 instances of one self-requeueing waker, of which a single `8 h 37 m` hang dominates and the other
948 sum to `≈2.96` h. **⚠ AND IT MOVES: `12.606389` at `09:20Z`, twenty-one minutes later.** It grows
`≈0.05`–`0.07` CPU task-h/day from the waker's ordinary cadence, plus whatever the next hang adds.
**⚠ THAT RATE IS WRONG BY AN ORDER OF MAGNITUDE AND IS WITHDRAWN — §5.6b: `≈0.65`–`0.69`/day, giving
`≈28`–`29` CPU task-hours by the `R5` stop. `N` is unaffected, re-derived under four readings.**
**Every percentage taken against this reading must carry its measurement instant** — a bare `12.59` is
already stale. The **scope** was complete at both instants: exactly one distinct job id in the `R5`
window. **And `--duplicates` cannot simply be switched on:** `_parse_sacct_dump` keys on job id alone and
raises *"conflicting rows for task identity"* when fed the duplicated dump (`r5_meter.py:270`,
re-verified here).

**This record does not adjudicate it and it is not in Z's contract.** It is surfaced because the
question *"how much of `R5` is left"* has two measured answers `12.59` CPU task-h apart, the gap grows
while the waker runs, and every figure in §3.7b and §5.8 is quoted against the ceiling. **It does not
move `N`:** re-derived here, the estimated member count is `4`–`5` under **both** readings
(`413.47` or `400.88` CPU task-h remaining after one build, against `86.53` or `115.36` per member).


## 6.8 DECISION SHEET `D1`–`D4` — ⚠ REWRITTEN IN REV. 16 AFTER THE CONTRACT REVIEW OF THESE FOUR

**Rev. 15's sheet recommended adopting `D1`, `D2` and `D4` as written. A contract review of the four
numerical proposals — the earlier PASS did not cover them — found that `D1`, `D2` and `D4` are NOT ready
for adoption as written, and that `D3` is supportable conditionally. Joseph has approved those findings,
and this sheet implements them.** The assembly algebra and the existing rulings are **not** reopened;
§§1–2, §1.3a–d, §6.1–6.5 and the pin are untouched.

**What changed, in one line: three format-and-arithmetic-derived numbers are gone, and what replaces
each is not another number but a stated scientific question.**

---

### `D1` — the `(cause 3, Z)` acceptance packet → **§3.7b**, **§3.7d**

| field | |
|---|---|
| **STATUS** | **NOT READY FOR ADOPTION AS WRITTEN.** Adopt the **statistics and normalization**; do **not** adopt the thresholds |
| **RECOMMENDED — adopt** | `s_agg` and `s_med` as defined (§3.7b item 2); denominators **Z's own as-built `k = 0` member**; boundary **form** direct, `s ≤ δ`, never quadrature; the maximum over the declared set |
| **RECOMMENDED — do NOT adopt** | **`δ_agg = 0.0861%` and `δ_med = 0.0374%` as acceptance criteria.** Withdrawn (§3.7b item 4C). They may be quoted as the historical printed format's resolution and as nothing else |
| **WHY the statistics stand** | each is the relative change in a quantity that is itself reported, so no model connects it to a printed number; §3.6d's ordering rule is satisfied by construction. **Why the direct form stands, and now more firmly:** quadrature needs **independence**, and — correcting rev. 4–15 — **budget adoption alone would not establish it**, so the direct form is not merely the currently-permitted choice but the one whose alternative carries an undischarged burden |
| **WHY the thresholds fall** | **(1)** choosing 3 or 4 significant figures does not establish how much estimator-baseline sensitivity is scientifically acceptable, and the macros the format came from are **defined and never printed**; **(2)** the rule behind them is **factually wrong** — half a display unit neither guarantees nor is required for an unchanged printed value, and it errs in **both** directions, at **`12.5%`** each **under the synthetic sampling model stated in §3.7b item 4A** (value uniform in its decade, change uniform on `[0, u)`); **the bidirectional failure is general, the rate is the model's**; **(3)** neither statistic can see correlations (§3.7d) |
| **CLAIM SUPPORTED** | with the statistics alone and no boundary: **none yet** — a statistic without a justified boundary measures but does not accept. Once a boundary exists: *"no declared estimator-baseline offset moves `√Tr C_Z` or the printed per-bin median by more than the declared tolerance."* **Never a statement about `C_Z`'s correlation structure** unless §3.7d's leg is added |
| **COST** | **zero production, in both directions.** Withdrawing the thresholds costs nothing; supplying a justified one costs nothing; §3.7d's legs add **no production members** — but ⚠ rev. 17: *"no new members"* is not *"free"*. Priced per member: `s_proj` and `s_corr` **seconds** at zero incremental I/O, `s_eig` **`≈1`–`3` min** and `≈1.8` GB (§3.7d). Tier-2 runtime, not `R5` |
| **WHAT IS NOW REQUIRED** | **(a)** a **use-based justification**: how much sensitivity is scientifically acceptable, and why, stated before the number; **(b)** an explicit **disposition of correlation sensitivity** — narrow the claim in the receipt, or add a leg (§3.7d names three candidates); **(c)** if literal display invariance is what is wanted, use **rounding equality**, which is exact and needs no `δ` (§3.7b item 4D) |
| **JOSEPH'S QUESTION** | *"Is acceptance intended to protect only these displayed summaries, or scientifically relevant uses of the assembled covariance?"* |
| **REMAINING UNCERTAINTY** | the question above is **not** one this lane can answer from the tree — it is a judgement about what the measurement is for. And the evidence stays **asymmetric**: at any affordable `N`, an unfavourable result is strong and a favourable one is weak |

---

### `D2` — the per-bin leg's tolerance → **§3.7b item 3**

| field | |
|---|---|
| **STATUS** | **NOT READY FOR ADOPTION AS WRITTEN.** Rev. 15 recommended option (i); **that recommendation is withdrawn** |
| **RECOMMENDED** | **keep the per-bin movement distribution as a reported diagnostic** — `median`, `p90`, `max`, argmax bin — gating nothing, pending the question below. Do **not** adopt the model-dependent third leg |
| **WHY** | `median_i(m_i)` is a legitimate descriptive statistic; **applying the printed median's precision to it is a new tolerance choice, not a consequence of that summary's formatting**. And rev. 7–15's ground was invalid: **a missing data release does not prevent specifying a scientifically motivated per-bin tolerance** — the two are unrelated questions. **Disclosing the uniform-movement assumption does not justify it** |
| **CLAIM SUPPORTED** | as a diagnostic: *"here is how per-bin uncertainty moved, and where it moved most."* **It accepts nothing**, which is the honest state |
| **COST** | **none.** It is computed from data the two exact legs already require |
| **JOSEPH'S QUESTION** | *"What per-bin movement is acceptable, in what fraction of bins, and why?"* — and **⚠ rev. 17 corrects rev. 16's framing of it as *"two numbers"*.** It is a **justified tolerance and a justified scope**, which is scientific work and not a value Joseph supplies on request; the two numbers are its **output**. Rev. 7–15's option (i) supplied one and let the median fix the other at `50%` by default rather than by argument |
| **CONSEQUENCE IF A THIRD LEG IS ADOPTED** | **the outcome branches must incorporate its failure.** Rev. 7–15's MET branch checked exactly two legs. **Already fixed structurally** — §3.7b item 5 is now written over a declared leg set `L`, so any third leg binds without a further edit |
| **REMAINING UNCERTAINTY** | a per-bin criterion also inherits §3.7d: bin-by-bin movement and between-bin correlation are different objects, and answering this question does not answer that one |

---

### `D3` — the joint-baseline design: `N`, the offsets, diagonal-or-grid → **§3.7b items 1 and "What `N` can be"**

| field | |
|---|---|
| **STATUS** | **SUPPORTABLE CONDITIONALLY** — the only one of the four that is. **Production-only**; nothing here is needed for Tier 2 |
| **RECOMMENDED** | **a conditional yes to a SMALL DIAGONAL DIAGNOSTIC**, and explicitly **not** an unconditional design endorsement. **No grid is required** — the review does not ask for one, so the grid question is closed as *not required* rather than answered |
| **WHY the endorsement is conditional** | rev. 15 recommended the diagonal *"unconditionally"* on the ground that **the launchers implement it**. **That is not a scientific ground** — an implementation is not a justification, and the review says so. The diagonal is what the code supports and what a small diagnostic can therefore use; that makes it **available**, not **right** |
| **CLAIM SUPPORTED** | *"`N − 1` counterfactual baselines on the implemented diagonal did not move Z's graded quantities."* Not a claim about the offset population, not a stability result, and — see `D1` — not a claim about correlations |
| **COST** | four additional members imply **nominal priors of `219.6` GPU / `346.1` CPU task-hours** (`4 × 54.90`, `4 × 86.53`), **before applicable campaign costs and contingencies**. **`N = 5` is a PLANNING PROPOSAL, NOT DEMONSTRATED CAPACITY** — rev. 7–15's *"affordable at `N = 4`–`5`"* overstated what an estimate can establish, and the phrasing is corrected wherever it appears |
| **PREREQUISITES, all four** | **(1)** resolve `D1` and `D2` — a design graded by a criterion that does not exist yet is a run in search of a rule; **(2)** declare the offsets **and their consequences**; **(3)** obtain **current attempt-meter accounting** (§5.6b: the metered unit changed, so every percentage in §5 is quoted against a denominator that has moved); **(4)** a **separate run authorization** — `D-RESOURCE`, which does not exist |
| **JOSEPH'S QUESTION** | *"Would an unfavourable result on a predeclared diagonal set change a named decision enough to justify its cost?"* — **and it is the prior question.** If the answer is no, `N` does not need choosing |
| **REMAINING UNCERTAINTY** | the per-member cost is a **prior from a different subject** with a **measured `±58.7%`** single-arm swing and no established direction; the wall clock is **one realization** at one week's queue depth |

---

### `D4` — the fixed-seed null packet → **§3.7a**

| field | |
|---|---|
| **STATUS** | **NOT READY FOR ADOPTION AS WRITTEN.** Adopt the **normalizer**; the **`ε` and the reconstruction operand are both withheld** |
| **RECOMMENDED — adopt** | `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` over the reported support, with `sqrt(Tr C_Z)` and the per-bin max rejected on the record. **The review is explicit: keep scale-relative normalization** |
| **RECOMMENDED — withhold** | **`ε = n_iters · n_rep · float64.eps` and the value `1.1873e-11`**, and with them the `8.9×` margin claim |
| **WHY `ε` falls** | it is a **summation bound applied to something that is not a summation**. Measured against the kernel that runs (`unified_throw_cov_5d.py:47-89`): the chain is LightGBM fitting × `n_iters`, three **event-level** accumulations, a completeness **division**, and four more divisions. **`n_rep` counts OUTPUT BINS while every accumulation runs over EVENTS** — the operand is simply wrong. `n_iters` as an amplification allowance is asserted, not demonstrated. And a bound on evaluating the **final norm** would not bound the **difference between two re-unfolds**. **Underneath all three: the estimator is not claimed deterministic even by its own module** — `omnifold_nn_core.py:203-204` says *"nearly deterministic in `seed` alone"*, `make_estimators` pins `random_state` and **no** thread or determinism flag, and G's measured null is **not zero**. This is a **reproducibility** question, not a rounding one |
| **WHY the operand of `11b` also falls** | the numerator compares **two internally re-unfolded CVs**; rev. 7–15's denominator came from a **separately produced ROOT**. `adopt_unified_5d.py:116-121` checks **cardinality only** — not the mask, not the values — and **a file hash cannot resolve identity**. Worse, a separately produced CV as denominator **presumes the determinism the null is testing**. **Remedy, and it is cheap: persist `x_cv`, `x_cv2` and the support predicate in Z's own product — `1.05` MB against the `2.668` GB throw product, a fraction of `3.9e-4`** (⚠ rev. 17 corrects rev. 16's `≈41` GB / `2.6e-5`, which divided by the 45-component band family instead).** `11b` is restated over the persisted vectors; the external route becomes `11c`, conditional on elementwise identity |
| **CLAIM SUPPORTED** | with the normalizer and no `ε`: *"here is Z's CV reproducibility, on a scale-relative measure, reconstructible from Z's own product."* **A measurement, not yet an acceptance** |
| **COST** | **zero** for the normalizer, the persistence and the restated reject conditions — all Tier 2. **`PM-6`'s bounded read is no longer needed for `D4`**, which **removes** a Tier-3 prerequisite. **⚠ REV. 17 WITHDRAWS THE CONTROL'S PRICE.** Rev. 16's *"`≈11.6` GPU task-h, `8` invocations"* priced the wrong operation on the wrong partition: an invocation is a whole `do_combine`, and the combine is a **CPU** job (`sbatch_uthrow_combine_5d_fast.sh:4`). **Spend is UNRESOLVED** — no CPU-partition CV-unfold time exists and the combine arm has no recorded actual either. **Reservation bound `3n` CPU task-h** at the launcher's own `--time`, with `n` undetermined until the sampling design exists |
| **⚠ NEW IN REV. 17 — THE BOUND'S STRUCTURE** | rev. 16's `min(achievable, acceptable)` is **withdrawn**: it used a feasibility floor as an **upper** bound where §3.6a says it bounds `ε` from **below**. Replaced by **`B` with its assumptions and confidence, `S` independently justified, the precondition `B ≤ S`, and `ε` argued within `[B, S]`**. **If `B > S`, the finding is that the execution envelope is not demonstrated adequate — not a tolerance** |
| **⚠ NEW IN REV. 17 — THREE ROUTES TO `B`, none privileged** | rev. 16's *"the only route"* is **withdrawn**; the review did not establish it. **(i) pin the envelope in code** — `make_estimators` sets `random_state` and no `num_threads`/`deterministic`/`force_row_wise`; **Tier 2, no compute**, and the only route that *reduces* the quantity rather than measuring it. **(ii) the revised control**, with all three gaps answered. **(iii) establish `S` first**, and discharge `B ≤ S` by bounding |
| **JOSEPH'S QUESTION** | *"What reproducibility tolerance is justified for this exact algorithm and execution envelope, subject to an independently justified scientific sensitivity limit?"* — **and the structure above is the shape of that question**, which rev. 16 answered with a minimum |
| **REMAINING UNCERTAINTY** | **neither `B` nor `S` is established**, and rev. 17 adds a third gap rev. 16 hid: **a within-envelope null does not measure a between-envelope shift**, so two arms of `r_null` can both be ~zero while the arms' CVs differ. A cross-arm `r_cross` is required if portability is the claim. **And the control's subject engages §6.4** — run on Z's own bank, its nulls are Z's nulls |

---

**`D5` is not on this sheet because it is RESOLVED — §5.6b.** The landed meter repair adopts the
attempt-summing reading, which is the direction §5.9 flagged.

**Nothing on this sheet is adopted by this document.** `BEN-381` bars this lane from grading legs it
drafted, and a recommendation is not an adoption. **What rev. 16 does is smaller than rev. 15 claimed to
do, and it is the point: three numbers that could have been adopted are no longer available to be
adopted by accident.**

---

# 7. WHAT THIS LANE COULD NOT ESTABLISH, AND WHAT IT WOULD TAKE

1. **⚠ SUPERSEDED IN PART BY REV. 7 — §5.9 items 9–10.** **`PM-1`, `PM-2`, `PM-3`, `PM-4`, `PM-5`.**
   Rev. 1–6 called all five *"reads of cluster-resident ROOTs this checkout does not carry"*. **Two of
   those were wrong about the ACT required.** Now: **`PM-2` is answered from a COMMITTED RECEIPT in this
   checkout** — no cluster read, no ROOT (§5.9a). **`PM-3`'s availability arm is discharged** by a
   directory listing (ten endpoints, `universe_sweep_bkgaware/`, all `2026-07-14`). **`PM-1`, `PM-4`,
   `PM-5` and `PM-3`'s grid/footing arm remain open and are now BLOCKED for a NAMED reason:** they need
   to open a ROOT, and on the login node `uproot` is absent from both interpreters while PyROOT
   segfaults on import in the project conda env. **What it would take:** a ROOT-capable environment — the
   campaign env, not a bare interpreter. Each is then a `TKey` header listing, not a `41` GB scan.
   **Installing `uproot` would CHANGE the environment rather than read it, and that is not an evidence
   errand.**
2. **⚠ ANSWERED IN REV. 7 — AND THE PREMISE WAS FALSE.** Rev. 1–6 asked *"whether S's
   `support_family_sha256` is G's `combined_source` digest"*, on the ground that *"nothing binds
   them"*. **Something does, and it is committed in G's own directory:**
   `STAMPED_HASH_RECEIPT.slurm-56720356.json` records `9f7b2f55…` for the full path at
   `2026-08-12T05:46:19Z`, **four days before S's read**, so the two are **independent agreeing
   measurements** rather than one substituted for the other (§5.9a). **What survives is narrower and
   real:** the launcher hashes **after** building, so the digest binds the bytes at job end rather than
   at open — which is why §1.5 now requires `path + sha256 + size + mtime_ns + inode + device` stamped
   **at open time**.
3. **⚠ LARGELY ANSWERED IN REV. 7 — read §3.7b first; what survives is stated at the end of this item.**
   **A measurement design for `(cause 3, Z)`'s ruled joint-baseline quantity — and, with it, the
   statistic, normalization and boundaries §3.6b schematizes — and, per §3.6d, an acceptance boundary
   whose FORM may not be the predeclared quadrature rule, which is itself a carve-out question (§6.6).**
   §6.3 fixes the *quantity* and explicitly
   does not fix the *design*; §5.4 shows the historical family size is **5×–9× over `R5`** at a
   per-member prior **measured on a different subject**, so the design is the whole question. **What it
   would take:** a measurement-design proposal
   with a scientific rationale for its member count and offsets — not arithmetic. **Rev. 2 said this was
   "not this lane's" because `BEN-381` would disqualify the drafter from grading the leg. That is a
   misreading and is withdrawn:** `BEN-381` bars a lane from **grading its own design**, not from
   **producing** one. This lane may design it; the **grading** must be routed to a lane that took none of
   the deciding measurements. Manufacturing a drafting prerequisite out of a grading separation would add
   a blocker the rule does not create.
   **WHAT REV. 7 ESTABLISHED:** the member is **measured, not designed** — one shared
   `MNV_EST_SEED_OFFSET` across exactly seven launchers, with an eighth refusing it; the statistic,
   both denominators and both boundaries are specified in §3.7b; and the affordable `N` is **`4`–`5`**
   against a historical design at `5.1×`–`8.7×` over `R5`. **WHAT SURVIVES AS UNESTABLISHED:** the
   printed precision Z will be reported at, which is Joseph's declaration and not a measurement
   (§6.7 D1c); whether *"jointly"* means the implemented diagonal or a 2-D grid (§6.7 D3); and whether
   a four-or-five-member maximum-deviation measurement is worth `86.5%` of the CPU ceiling.
   **⚠ REV. 16 REOPENS PART OF WHAT REV. 7 CLOSED, and says so rather than leaving the "LARGELY
   ANSWERED" banner to mislead.** The **statistics** and their normalization survive review; **the
   boundaries do not** — they are withdrawn as acceptance criteria (§3.7b item 4), so *"both boundaries
   are specified"* above is **no longer true** and the design question now depends on items 20 and 21
   below. **`N = 4`–`5` is a planning estimate, not a demonstrated capacity**, and the *"affordable"*
   framing is corrected. **The grid question is closed as NOT REQUIRED** rather than answered.
4. **⚠ ANSWERED IN REV. 7 — §3.7a; what survives is `‖x_cv‖` itself, named as `PM-6` below.**
   **The normalizer and the numerical value of §6.4's scale-relative null bound.** The ruling fixes the
   *form* and forbids choosing the value from a result. **§3.6a names the four things that complete it**
   — the normalizer with its rejected alternatives on the record, units, the `ε` derivation, and the
   presence/finiteness rule. **Rev. 4 corrects what that derivation may be:** the quadrature rule is
   **not** admissible here as written (§3.6d), and a hardware reproducibility floor bounds what is
   **achievable** rather than what is **acceptable**, so it can constrain `ε` but cannot justify it.
   **What it would take:** a stated mechanism by which a non-deterministic CV moves a reported quantity,
   then a boundary derived for that mechanism, then a number.
   **REV. 7 SUPPLIES ALL THREE:** three mechanisms, two of them evaluated; a precision control
   `ε = n_iters · n_rep · eps` that binds over the sensitivity controls by seven orders in the one
   unmeasured quantity; and the value `1.1873e-11` at Z's expected shape. **It is PROPOSED** (§6.7 D4).
   **⚠ REV. 16 WITHDRAWS THE THIRD OF THOSE THREE, so this item is OPEN AGAIN and more precisely than
   before.** The precision control was a **summation bound over a computation that is not a summation**,
   and `n_rep` counts **output bins** while every accumulation in the chain runs over **events**
   (§3.7a item 3, measured against `unified_throw_cov_5d.py:47-89`). The **mechanisms** rev. 7 supplied
   and the **normalizer** stand; **the number does not**. **What it would take is now item 22 below**,
   and it is two arguments, not one: a reproducibility model for this algorithm and envelope, and an
   independently justified sensitivity limit. The bound is the **smaller** of the two.
5. **⚠ PARTLY CLOSED IN REV. 7 — §5.8a is the delta; two of five rows are now estimated, three are
   still open.** **The unpriced cost rows (§5.2), enumerated there PER SUBTOTAL — five omitted from the
   spend estimate, three from the proposed reservation, and two campaign-level items in neither. Neither
   partial sum is a bound in either direction**; rev. 3's *"floor"* is withdrawn. The cause-1 off-diagonal
   counterfactual; the **second** CV unfold the cause-4 jitter counterfactual adds at `seed + 7`, distinct
   from `--null`'s same-seed one; Z's **inflated-object validation**, which the historical P4 chain's
   block-sum stage 5 does not cover; and the artifact replay. None needs an unfold except the cause-4
   one. **What it would take:** a memory/wall-clock estimate against the `10,694`-bin dimension for
   three of them, and one measured CV-unfold time **on the CPU partition where `--null` actually runs**
   for the fourth — the GPU arm-3 figure rev. 2 used is not commensurable.
6. **Whether real Perlmutter `sacct` output parses through `r5_meter._parse_sacct_dump`.** 18 tests pass
   on hand-authored fixtures, and a fixture written beside its parser cannot disagree with it. **What it
   would take:** one login-node `sacct` capture — the same act as §4 row 3.
7. **Two control-document discrepancies, left standing.** `CRITERIA` vs `SCOREBOARD` on cause 4's `M`
   (`UNRESOLVED` vs `OPEN`), already filed by `DECISION-20260902-…-oi173` §6 as *"a finding owned by
   neither lane"*; and on cause 2's `T` (*"absent"* vs `MET`) (§2.2). **What it would take:** an owner
   for the two control documents.
8. **Whether `CRITERIA` §2 cause 6's *"unrepaired instance in current code"* should now be amended.**
   §2.6a measures it stale on both projectors. **This lane does not edit `CRITERIA`**; the finding is
   surfaced for its owner.
9. **RESOLVED during rev. 1 drafting, kept because it changed §5.** The cause-6 statistical **ensemble**
   is arm 1 (`sbatch_bootstrap_5d_gpu.sh:313` → `boot_nd_5d/res_boot_*.npz`, consumed by
   `sbatch_combine_5d_budget.sh:14-15` at `--expected-ids 1-100 --tag stat5d`) and **is** inside the
   seven-arm anchor; the **combine** is not, and is priced separately. **Still unestablished:** whether
   that `≤1.0` is representative. `grep` over `RUNS.tsv` for `budget5d` and `combine_5d_budget` returns
   **0** rows against a positive control on the same file (`57128458` → `:321`), so the ledger carries no
   accounting for it. **What it would take:** one `sacct` read.

10. **`PM-6` — `‖x_cv‖` for G, and with it G's null ratio under §3.7a's chosen normalizer.** The key
    exists (`hXSecND_flat`, `adopt_unified_5d.py:116-120`) but the throw writer does not persist the
    vector (`unified_throw_cov.py:540-579`), so the ratio is not reconstructible from the throw product
    alone. **What it would take:** one bounded cluster read — requested from the operational-preflight
    session at this revision.
    **⚠ NARROWED IN REV. 16, AND IT IS NO LONGER A `D4` PREREQUISITE.** The `8.9×` margin it was to
    convert into a measurement was `ε` divided by a transferred figure, and **`ε` is withheld**, so the
    margin has no numerator to measure. And Z's own null no longer needs an external denominator at all:
    `11b` is restated over vectors **Z's writer persists** (§3.7a). **What survives is a narrower,
    genuinely open question about G** — G's product does not persist its `x_cv` either, so G's null ratio
    under §3.7a's normalizer remains unreconstructible from G's product. That is a statement about G's
    auditability, not a blocker on Z.
11. **The printed-total sensitivity channel.** `values.tex:29-31` records that *"THE TOTAL IS AN
    INTEGRAL, NOT A SUM OF BIN CONTENTS"* and that the bin-area Jacobian is required; the 5D bin volumes
    are not in this checkout. **What it would take:** the 5D edge arrays. **It would have to be eight
    orders tighter than both evaluated channels to change §3.7a's conclusion.**
12. **⚠ RESTATED IN REV. 16 — it is a per-bin TOLERANCE, not a per-bin PRECISION TARGET, and rev. 7–15
    asked the wrong question.** The note prints no per-bin uncertainty (measured, with a positive
    control) — **but that is a fact about display, and it does not prevent specifying a scientifically
    motivated per-bin tolerance.** Rev. 7–15 reasoned from the missing data release to a formatting
    borrow, and the review rejects the inference: *"applying the printed median's precision to it is a
    new tolerance choice, not a consequence of that summary's formatting."* **What it would take:** an
    answer to *"what per-bin movement is acceptable, in what fraction of bins, and why"* — **two
    numbers.** Rev. 7–15's option (i) supplied one and let the median fix the other at `50%` by default.
    **Until then the per-bin distribution is a reported diagnostic and gates nothing**, and Z's per-bin
    contract is weaker than the narrow scan's — which §3.7b says rather than claiming parity.
13. **A measured CV-unfold time on the CPU partition**, for the cause-4 counterfactual's second unfold.
    The `43.5`-minute figure is a **GPU** arm-3 per-task time and rev. 2 already priced this row off it
    once, wrongly. **What it would take:** one `sacct` read of the combine arm's partition and runtime —
    also requested from the preflight session.
14. **A measured read rate for the artifact replay's I/O term** (`≈41` GB — the **45-component** family,
    **not** the `2.67` GB throw product; the two were conflated in rev. 16 and are separated in §5.8c —
    if each component is a full
    `10,694²` `TH2D`). Its arithmetic term is `≈0.07` CPU task-h; **the I/O term is the whole question**
    and the sum is not established (§5.8c).
15. **⚠ RESOLVED IN REV. 15 BY THE LANDED REPAIR — §5.6b.** The metered unit is now an **execution
    attempt**, `sacct` is queried `-X -D`, and every attempt of one job id is charged, which is the
    reading this item asked for. **What survives is not a gap but a rate correction:** the waker's
    ordinary cadence is `≈0.65`–`0.69` CPU task-h/day, not the `0.05`–`0.07` this document carried, for
    `≈28`–`29` by the stop. **`N` is `4`–`5` under every reading.** The item as written follows.
    **How much of `R5` is actually left — two measured answers `12.59` CPU task-h apart.** The landed
    meter deduplicates requeued instances (`_sacct_argv()` carries no `--duplicates`; `_parse_sacct_dump`
    keys on job id and raises on the duplicated dump — **re-verified here** at `r5_meter.py:380-392` and
    `:270`), while `R5` §3 says *"retried tasks count in full"*. **What it would take:** a ruling on
    which reading `R5` means, then a parser keyed on `(job id, submit time)` rather than job id alone.
    **`D5`. It does not move `N`; it moves the denominator of every percentage in §5.**
16. **⚠ ANSWERED IN REV. 8, AND THE ANSWER IS ONE SAMPLE.** Rev. 7 asked whether `4`–`5` complete
    rounds fit the wall clock, and named the `sacct` span read that would settle it. **It was taken:
    `37.5` h per round, so they fit inside either block** (§5.9c). **What remains unestablished is the
    DISTRIBUTION.** That span is one realization at the queue depth of `2026-08-30`; a campaign would
    run into the pre-outage rush before `2026-09-16`, and nothing in the record bounds queue behaviour
    then. **What it would take:** spans from two or more complete rounds — of which the tree holds
    exactly one, since round 1 and round 2 are the only complete populations and only round 2's window
    was read.
17. **A binding for G's production-CV input — the one object §1.3d and `11b` both now depend on.**
    `sbatch_adopt_stamped_footing.sh:29` supplies it by default and **G's own hash receipt does not bind
    it** (that receipt binds four files, and this is not one — §5.9a). Without it the mask and
    row-order digests cannot be reconstructed and `‖x_cv‖` cannot be recomputed, so **`PM-4` and `11b`
    fail together on the same missing identity**. **What it would take:** the production ROOT's path and
    sha256, bound to G's build. **Two different things are needed and rev. 8 ran them together.** The
    **inspection itself is authorized** — Joseph, 2026-09-06, quoted with its limits in
    `AUTHORIZATION-20260906-pm-root-inspection.md` §1-§2 (one CPU node, one task, ≤ 30 min, no GPU, no
    requeue). What does **not** exist is a way to **admit** it: §3 of that record measures four
    independent blockers, and §4's **one-off accounting exception** — the narrowest thing that would
    clear them — is a **proposal Joseph expressly reserved to himself** (*"return the precise blocker
    and any proposed one-off accounting exception for my separate approval — do not bypass them"*) and
    **has not been ruled on**. So the read is authorized and unadmittable, which is a different state
    from unauthorized.

18. **The off-branch evidence this document rests on is UNPUSHED, so §5.9's and §7's citations to it
    resolve on one machine only.** Measured with a positive control (§5.9): the remote carries exactly
    two `lane/*` refs and `lane/pm-root-inspection-20260906` is not among them. Everything in §5.9 that
    is **RELAYED** therefore has a citation a reader outside this machine cannot follow — the
    **RE-VERIFIED HERE** items are unaffected, because their evidence is in this checkout. **What it
    would take:** a push by that branch's owner. **It is not this lane's act**, and it should not happen
    before Joseph rules on the authorization record's §4, since pushing would publish an undecided
    accounting exception. **The right reading until then is that §5.9's relayed measurements are
    attested but not yet independently fetchable**, which is weaker than this document said in rev. 8
    and rev. 9 and is stated here rather than left to a reader to discover.

19. **The meter runbook's default `--write` target is the admission gate's input path, and that path is
    an ordinary tracked-by-default file.** Measured (§5.6a): `R5-METER.md:12-16` writes to
    `docs/orchestration/state/r5-meter-receipt.json`; `git check-ignore` exits **1** on it; **150**
    tracked `.json` files already sit in that directory; and the runbook disclaims **authorization**
    while saying nothing about **admission**. So *follow the runbook, then `git add`* arms the queue,
    and neither step looks like a decision. **What it would take:** either the runbook's default target
    moves off the gate path, or the gate path stops being tracked-by-default. **Which is right is the
    meter owner's call, not this lane's**, and this record proposes neither.
    **⚠ HALF CLOSED IN REV. 15 — §5.6b.** The **first** remedy is **TAKEN**: `--write` now has no
    default, the verification examples write to a scratch path or nothing, *"refresh"* is gone, and the
    runbook carries a dedicated section saying that committing to the state path opens admission
    queue-wide, with its own disclaimer marked as silent about admission. The **second** — untracking or
    ignoring the gate path — was **deliberately DECLINED and referred to the decision owner**, because
    it changes how admission can ever be armed. **So this item is now a live decision for Joseph rather
    than an open finding, and the hazard is LARGER than when it was written:** after the repair the
    documented command produces a valid, armable receipt where before it produced a visibly wrong one.

20. **⚠ NEW IN REV. 16 — A USE-BASED JUSTIFICATION FOR CAUSE-3 ACCEPTANCE, which is the thing rev. 7–15
    substituted a format for.** *"How much estimator-baseline sensitivity is scientifically acceptable,
    and why?"* Rev. 7–15 answered *"three significant figures"* — a fact about `values.tex` macros that
    are **defined and never printed** — and derived `0.0861%` / `0.0374%` from it. **The numbers are
    withdrawn** (§3.7b item 4C). **What it would take:** a statement of what the assembled covariance is
    used for and how much movement in it changes a downstream conclusion. **It is not a measurement and
    this checkout cannot supply it**; it is the judgement `D1` asks for, and it must precede any number
    rather than follow one. **Joseph's question:** *"Is acceptance intended to protect only these
    displayed summaries, or scientifically relevant uses of the assembled covariance?"*
21. **⚠ NEW IN REV. 16 — AN EXPLICIT CORRELATION-SENSITIVITY DISPOSITION, and it is the finding with the
    longest reach.** Both proposed statistics are functions of the **diagonal alone**, so they return
    **exactly `0.0`** on a pair of matrices whose sum and difference uncertainties differ by `+37.8%`
    and `−68.4%` (measured, §3.7d). **It is live rather than hypothetical:** `project_cov_nd.py:2-11`
    marginalizes the assembled covariance as `M C Mᵀ`, and `eavailW_covariance.py:290-304` and
    `eavail_generator_significance.py:83-89` are named instances of the same map. **What it would take:**
    either a scope statement carried **with the grade** — a MET result does not license the covariance
    for off-diagonal-sensitive use — or a leg that can see correlations. §3.7d specifies three
    candidates; **`s_proj` costs no production**, because its functionals already exist as code. **None
    is adopted, and none has a boundary**, since a boundary needs item 20 first.
22. **⚠ RESTATED IN REV. 17 — A JUSTIFIED BOUND FOR Z'S FIXED-SEED NULL, AND REV. 16 GOT THE RELATION
    BETWEEN ITS TWO HALVES WRONG.** Rev. 16 wrote that the bound is `min(achievable, acceptable)`.
    **Withdrawn as acceptance-blocking**: an observed reproducibility floor is not an acceptance
    tolerance, and §3.6a — in this document, two sections earlier — says such a floor *"may bound `ε`
    from **below** as a feasibility constraint; it cannot justify `ε`."* **`min` used it as an upper
    bound.** The defensible structure is **`B`** (an operating-error bound with stated assumptions and
    confidence), **`S`** (an independently justified scientific cap), the **precondition `B ≤ S`**, and
    `ε` **argued within `[B, S]`**. **If `B > S` the finding is that the execution envelope is not
    demonstrated adequate**, which is a conclusion about the envelope and not a threshold.
    **WHAT IT WOULD TAKE — three routes, none privileged, and rev. 16's *"the only route"* withdrawn:**
    **(i)** **pin the envelope in code** — `make_estimators` (`omnifold_nn_core.py:143-148`) sets
    `random_state` and no `num_threads`, `deterministic` or `force_row_wise`; **Tier 2, zero compute**,
    and the only route that *reduces* the quantity rather than sampling it; **(ii)** the control in
    §3.7a with all three of its gaps answered — a cross-arm `r_cross` (a within-envelope null does
    **not** measure a between-envelope shift), a declared coverage/confidence objective with its
    sampling assumptions, and a **predeclared** estimator of `B`, since two arms do not prevent tuning;
    **(iii)** establish `S` first and discharge `B ≤ S` by bounding. **Its cost is UNPRICED** — rev. 16's
    `≈11.6` GPU task-h priced the wrong operation on the wrong partition (§5.8d). **And the control's
    subject engages `§6.4`**: run on Z's own bank, its nulls are Z's nulls; run on another bank, it is a
    transfer needing an argument. **That is Joseph's ruling, not this lane's reading.**
    **Joseph's question:** *"What reproducibility tolerance is justified for this exact algorithm and
    execution envelope, subject to an independently justified scientific sensitivity limit?"*
23. **⚠ NEW IN REV. 16 — WHETHER A PRODUCTION ROOT'S `hXSecND_flat` IS ELEMENTWISE IDENTICAL TO A THROW
    RUN'S INTERNAL `x_cv`. This is `11c`'s precondition and nothing in the tree establishes it.**
    Measured: `adopt_unified_5d.py:116-121` asserts `x.size == n` and **nothing else** — not the mask,
    not the values; the key is written by at least two producers (`sweep_bank.py:271` and the standard-P4
    chain, `run_p4_unfold_std.sh:65`); and it lives on the **65,856 grid** while every covariance lives
    on the **10,694 support** (`mii_anchor_comparator.py:869`). **A file hash cannot close this** — it
    binds bytes, not equality between two productions' vectors. **What it would take:** an elementwise
    comparison inside one job that holds both. **Until then `11c` reports `UNRESOLVED`, which is why it
    was written as conditional rather than as a check.**
24. **⚠ NEW IN REV. 16 — WHICH STEP MAKES THE CV RE-UNFOLD NON-DETERMINISTIC IN-PROCESS.** G's committed
    null is `5.8223488501140625e-50`, which is **not zero**, so two same-seed re-unfolds in one process
    do not agree bit-for-bit. **This record does not name the cause**, because naming a mechanism no
    command has been run against is this campaign's catalogued way of retiring a real defect with a
    plausible story. **What is measured** is only that nothing pins it: `make_estimators`
    (`omnifold_nn_core.py:143-148`) sets `random_state` and **no** `num_threads`, `n_jobs`,
    `deterministic` or `force_row_wise`, and the module's own docstring (`:203-204`) says LightGBM at
    these settings is *"**nearly** deterministic in `seed` alone."* **What it would take:** item 22's
    control with its thread-count arm, which separates envelope-dependent from envelope-independent
    variation without anyone having to guess first.

---

# 8. WHAT THIS RECORD DOES NOT DO

It constructs nothing, implements nothing, launches nothing, spends nothing, grades no leg, discharges no
cause, adopts no artifact, moves no count and no gate, opens no `SCOREBOARD` cell, licenses no
projection, touches no publication claim and no `values.tex`, authorizes no submission, closes no `OI-*`,
and writes no scheduler state.

**It does not extend `CRITERIA` §0's grade vocabulary.**
`DECISION-20260902-joseph-rules-no-fourth-grade-token.md` stands; §6.1 is a per-cell decision on cause 2's
own precedent and adds no token. It does not retrospectively regrade G on any leg — §6.4 in particular is
a forward requirement on Z and explicitly not a re-grade.

It does not widen Y, does not rename Y as Z, and does not create Z's cells — `RZ(ii)` constrains a future
assessment and does not create one. It does not combine Z's prospective grades with G's or Y's in any
direction. It does not promote S, does not find S adoptable, and leaves `VL68`'s *"built is not adopted"*
standing unchanged. It does not reopen `R5`: the accounting start `2026-09-02T13:44:27Z` (`9ce59a59`),
both `500` task-hour ceilings and the `2026-09-30` stop are preserved exactly, and no new cap, accounting
start or extension is proposed. It is **not** `D-C3-VOI` and **not** `D-C3-RUN`; `R4`'s suspension stands
and §6.3 does not touch it. It does not authorize the historical narrow scan, and it does not rule
substitution. It does not alter PET's diagnostic status under `R6`; Gate 6 stays BLOCKED under its five
prohibition keys.

It does not perform `RZ` §5's owner applications, and it does not edit `CRITERIA`, `SCOREBOARD`, `MAP`,
`OPEN_ITEMS`, `VALIDATION_LEDGER`, `PLAN-20260905`, either 2026-09-06 decision record, or anything on the
off-branch `lane/cause3-voi-20260906`.

It regenerates no state: `OI-73`'s hold stands and `generate_live_state.py --check-freshness` reports
STALE at this base by design.

**§3.7 AND §5.8 ADOPT NOTHING.** They are proposals. No statistic, denominator, precision target,
boundary, reject condition, offset set, member count, cost figure or `ε` in them is approved by this
record, and §6.7 exists precisely so that no reader can mistake a completed specification for an
accepted one. **The contract is NOT ready for an implementation authorization**, and §6.7 lists what
would make it ready.

**And it does not grade the legs it defines.** `BEN-381`; see the header. That applies to the four
rulings too: they fix criteria and outcomes, and the lane that drafted them grades nothing under them.
