- **The canonical quiesce window is CLOSED, 2026-08-30:**
  [`CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md`](CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md)
  — the freeze expired **on its own terms** (*"when submission is authorized or the rehearsal is
  abandoned"*), so **no new authorization is claimed**. Records this lane's *independent* remeasure of
  the sbatch-time property `F-17(a)` actually tests: HEAD `32e403b8`, porcelain **726**, status digest
  `d429f0f3…` — matching the operand without relying on the producer's report. Reconciles the two byte
  figures (a 4,096 difference = one wrapper directory inode) and the three quarantine generations
  (517 + 415 + 6 = 938). Reads the seven arms' array specs **untruncated** and confirms the arms run
  from a tree at `7ac0edec`, detached, porcelain 0. **Corrects** the producer's walltime envelope
  maximum from 253.5 to **300** (`boot5dG`, 100 × 3:00), which does not change the under-500 verdict.
  **Releases the dashboard lane** (`OI-175`, porcelain 726 → 725); does **not** release the deployment
  tree, move any gate, or decide the post-path `F-17(b)` capture, which is routed as `OI-178`.
# Orchestration router

This is a pointer-only active-tree router. It contains no scientific evidence or authorization.

## Current work

### OI-136 fail-open repair — AUTHORIZED 2026-09-03 (36 of 45; 9 excluded with measured reasons)

- [`AUTHORIZATION-20260903-oi136-failopen-repair.md`](AUTHORIZATION-20260903-oi136-failopen-repair.md)
  - Joseph's authorization quoted; scope is the `__file__`-derived import root at 36 fail-open
  entrypoints with both ratchet constants moved in the same commit. Three probe records, the
  published 2D arm (ruled 2026-08-23), and five receipt-bound files are NOT repaired. Expires no
  freeze; deploys nothing; moves no gate or count.

### Wave 1 integration — frozen routing interface, conflict matrix, ledger (2026-09-03)

- [`INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md`](INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md)
  - **The structured-routing interface is frozen (§1) before any Wave 1 code lands**; the
  conflict/dependency matrix (§2) is built from the return envelopes only, and §5 maps every accepted
  or rejected output to commits, tests, and reasons. Proposes a tip for an independent acceptance
  reviewer; grades nothing. Enforces `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`
  over the original plan. Moves no gate or count, adopts nothing, launches nothing.
- [`R5-METER.md`](R5-METER.md)
  - Usage and fail-closed semantics for the R5 task-hour accounting boundary. The meter authorizes
    nothing; every run still requires its own declaration and authorization.
- [`FOLLOWUP-20260906-r5-sacct-window-and-post-stop-accounting.md`](FOLLOWUP-20260906-r5-sacct-window-and-post-stop-accounting.md)
  - **OPEN, owned by the orchestration lane.** The `sacct` span limit makes the meter's own query
    unissuable from **2026-10-02T13:44:27Z**, two and a half days after the stop. Two dated
    obligations: preserve and commit the full accounting capture before that instant with the ids of
    everything still running, and meter those jobs afterwards with `-j`, which bypasses the limit. A
    query limitation is not permission to omit expenditure.
- [`FINDING-20260906-r5-meter-undercounted-requeue-attempts.md`](FINDING-20260906-r5-meter-undercounted-requeue-attempts.md)
  - **The metered unit is an execution attempt, not a job id.** On a preserved Perlmutter capture of
  one self-requeueing waker job the meter reported **0.0016667** CPU task-hours where **12.590278**
  had been spent across **952** attempts — the fail-OPEN direction against a prohibition — or refused
  outright once `--duplicates` was in the query. Records the corrected semantics, the receipt
  schema-2 fields, the version-1 refusal, the reading of §3 it rejects (named so it can be
  overturned in one function), and one dated follow-up: the 30-day `sacct` span limit fires at
  `2026-10-02T13:44:27Z`, after the stop date. Produces **no** operational receipt, changes no
  ceiling, moves no gate or count, and does not amend the ruling.
  **⚠ Its status line — *"open — three things are with the decision owner"* — is STALE in two of
  three: see the decision record immediately below. Updating that line is its owning lane's act.**
- [`DECISION-20260907-joseph-ratifies-r5-attempt-accounting-and-declines-untracking.md`](DECISION-20260907-joseph-ratifies-r5-attempt-accounting-and-declines-untracking.md)
  - **Joseph, 2026-09-07, ratifies two of the three items the finding above left with him.**
  **(1) The metered unit is the execution attempt:** R5 charges every distinct attempt exactly once,
  failed and requeued included, with repeated observations and `.batch`/`.extern`/step/array-bracket
  **representations** not double-counted. The alternative reading — one charge per job id — is
  **overturned**; it stays isolated in `_sum_charged_seconds`, so it is still cheap in code, but
  reviving it now needs a **new decision** rather than an edit. **(2) Untracking or ignoring the
  admission gate path is DECLINED**, so `committed_r5_receipt`'s requirement is unchanged and §8's
  *"live option"* is retired — arming admission stays possible and stays a deliberate, attributable
  commit. Records the provenance chain that made the file necessary: an **accurate** peer relay that
  nothing in the tree corroborated, then direct confirmation. **Authorizes no compute, arms no
  admission** (a whole-history log over the gate path returns **0** commits — it has never been
  written on any ref), changes no ceiling, gate, count or grade, and does not touch the 30-day
  follow-up. Recorded by a lane that did not write the repair and that **declares its own interest**
  in the record existing.


### PET Gate-6 branch preservation — removal proposed, NOT executed

- [`PROPOSAL-20260903-pet-gate6-branch-preservation-and-removal.md`](PROPOSAL-20260903-pet-gate6-branch-preservation-and-removal.md)
  - **Preservation DONE; deletion NOT approved and mechanically blocked today.** Two pushed
  `evidence/preserved-*` tags anchor 37 commits across five refs, cold-recovery tested in a
  branchless fresh clone and on the Perlmutter checkout. Two of the five refs are checked out in live
  worktrees, and `git branch -D` refuses a checked-out branch (power-tested both directions), so a
  partial run that deleted the three remote refs would strand two live lanes. Carries the one hard
  block on integration: the GAP-1 terminal receipt asserts a numeric `truth_denominator_coverage`
  with **no producer in any tracked code**. **Adopts nothing, promotes no PET result, moves no gate
  or count, deletes no ref.**

### Decisions awaiting Joseph — cause 7's subject and magnitude, cause 3's seed scan, the stop rule

- [`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`](DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md)
  - **✅ IN FORCE.** Joseph's 2026-09-02 ruling on all six packet recommendations: `(cause 7, G)` is
  permanently OPEN and G is retained; exactly one successor `Y` is authorized as a **separate** cell,
  cause 7 only, **specification only**; cause 7's `M` carries no smallness requirement; the cause-3
  seed-scan authorization is **SUSPENDED** pending a signed VOI note **and** a separate committed
  reauthorization; the campaign stops on **`2026-09-30`** or at **`500` GPU / `500` CPU task-hours**,
  whichever fires first, defaulting to the central-value Letter; and PET stays diagnostic. `R2`
  prospectively amends `DECISION-20260831` §1 for cause 7 only; `R5` conditionally supersedes
  `OI-187` half (b). **Adopts nothing, discharges nothing, authorizes no submission and no spend.**
  Gate 2 remains FAIL; counts hold at CAND `1 of 7`, QUOTED `0 of 7`. §4 lists six downstream
  applications this lane is `BEN-381`-disqualified from performing.
- [`PACKET-20260902-joseph-six-rulings-cause7-cause3-stop.md`](PACKET-20260902-joseph-six-rulings-cause7-cause3-stop.md)
  - **UNSIGNED RECOMMENDATION, rev. 3, authorizing nothing.** Six rulings put to Joseph, each with an
  exhaustive branch set and a fallback state: grade `(cause 7, G)` permanently OPEN on the direct byte
  evidence and retain G; authorize exactly one successor `Y` as a **separate** grade cell, cause 7
  only, **specification only**; select the no-smallness criterion for cause 7's `M` **without** a note
  obligation or an automatic grade; decide the cause-3 seed scan's authorization (retain / suspend /
  withdraw — recommended: suspend, with a separate committed reauthorization required, since the scan
  **does** grade `M(ii)`); set a fully defined date/resource stop whose default outcome is the
  central-value Letter; and keep PET diagnostic unless `OI-126`'s estimator-equivalence-plus-coverage
  ladder passes. `R2` prospectively **amends** `DECISION-20260831` §1 for cause 7 only; `R5`
  conditionally **supersedes** `OI-187` half (b). Cross-cuts `OI-126`, `OI-172`, `OI-173`, `OI-187`,
  `OI-188`; §7 gives each ruling an owning record. Gate 2 remains FAIL; counts hold at CAND `1 of 7`,
  QUOTED `0 of 7`.

### Y as R2 permits it, the complete-successor question, and #11-#30 reconciled (2026-09-05)

- [`PREDECLARE-20260905-cause7-only-successor-Y.md`](PREDECLARE-20260905-cause7-only-successor-Y.md)
  - **SPECIFICATION ONLY; all four legs OPEN and ungraded.** The cause-7-only successor `Y` that `R2`
  permits: artifact identities bound to path plus digest (G, its `combined_source`, its `uthrow_source`,
  S as a **component donor only**, F and J as explicit non-evidence), the replacement algebra
  `C_Y = C_G - L_support + L_active` over the five `p4_lib.BANDS` **imported, never retyped**, the
  receipt schema, the five magnitude measurements `R3` left threshold-free, and the both-direction test
  contract. Records that Y replaces **five of the nine** detector laterals in `detector_universes.txt`
  — the kinematic ones — and makes the weight-only justification for the other four
  (`VALIDATION_LEDGER.md:790`) a **pre-construction measurement**, not an inherited claim. §6 lists
  eight things a four-leg-MET Y still could **not** establish, starting with `(cause 7, G)`, which
  `R1` fixes permanently OPEN. **Constructing Y requires its own committed authorization (`R2(iv)`).**
- [`PACKET-20260905-full-scalar5d-successor-scope-question.md`](PACKET-20260905-full-scalar5d-successor-scope-question.md)
  - **ONE QUESTION FOR JOSEPH; authorizes nothing and recommends no option.** Whether a **complete**
  scalar-5D successor — called **Z**, deliberately not `Y` — may be named as a **seven-cause** grading
  subject and therefore a possible adoption subject, and what a ruling must say (subject, cell
  discipline, combination rule, stage gate). §4 walks the seven causes as they stand for G; §5
  re-measures the strongest ground rather than inheriting it: the jitter print at `a0cdc019` (06-08)
  **predates** the flux fix `081ae4ac` (07-31), so cause 4's `M` is unmeetable for G by a property of
  the **committed history**, which a new revision would not share — the broad "no committed revision"
  conclusion is cited to `DECISION-20260902-joseph-applies-oi173-cause4-m.md` §4, **not** derived from
  the two-revision ancestry check, which is labelled as the narrow measurement it is. §6 records the
  two campaign facts that belong on the table first: the `R5` meter **exists** (Wave 1's
  `r5_meter.py`, fail-closed admission) but **no operational accounting receipt is committed and no
  unattended execution is configured**, and S is **refused by the publication gate**. **`R5`'s stop is
  not reopened or re-optioned**; t0 is `2026-09-02T13:44:27Z` at `9ce59a59`.
- [`PLAN-20260905-prompts-11-30-reconciled-to-the-0902-decision.md`](PLAN-20260905-prompts-11-30-reconciled-to-the-0902-decision.md)
  - **ROUTING ONLY; a NOW row authorizes drafting, reading and measuring, never compute.** Disposes
  prompts #11–#30 as NOW / AWAITING a named decision / OPTIONAL. Corrects #11's premise, false on both
  halves — **G is RETAINED** and `Y` is **cause-7-only**, so Y has no causes 1–6 dispositions to give —
  and removes "adopt Y" as an outcome, which rewrites #20 and #21. §3b checks the recommended
  cause-disposition map row by row against the board: only cause 7 is Y's, cause 2 is already four
  METs, cause 5 already landed in `VL66`. §5 **reconciles** the decision record's six owner
  applications against committed evidence rather than relisting them: **five are unapplied; item 6
  (the `R5` meter) is substantially done by Wave 1 and carries only a residual.** Records that
  **completing PET coverage is not a publication prerequisite**. Preserves the ruled stop exactly,
  t0 `2026-09-02T13:44:27Z` at `9ce59a59`.

### Joseph rules the complete-successor question: Z may be specified (2026-09-06)

- [`DECISION-20260906-joseph-authorizes-z-specification-only.md`](DECISION-20260906-joseph-authorizes-z-specification-only.md)
  - **SPECIFICATION ONLY; authorizes nothing to build or run.** Joseph rules the one question
  `PACKET-20260905` asked, selecting its **option B**. `RZ` names **exactly one** complete scalar-5D
  successor **Z** as a **prospective** seven-cause grading subject and a **possible** adoption
  subject, with **seven distinct assessment cells**; **G's historical cells are preserved**, including
  `(cause 7, G)`'s permanent `OPEN` under `R1`, and **Y's cause-7-only scope under `R2` is
  preserved**. Z's assessments may form a **self-contained** tally and **may never be combined with
  G's or Y's grades** — a three-way separation, wider than the packet asked for. Authorized
  deliverables are a scientific contract, cause dispositions, terminal criteria, dependency analysis
  and a **costed execution proposal**; **any proposed criterion change is carved out** and reserved
  for a separate decision. **No implementation, construction, compute, grading, adoption or
  publication change.** `R1`–`R6` are untouched and `R5`'s accounting start, ceilings and stop date
  are preserved exactly; `RZ` is **not** `D-C3-VOI` and **not** `D-C3-RUN`. The ruling **opens no
  `SCOREBOARD` cells** — `(ii)` constrains a future assessment, it does not create one. Gate 2 remains
  FAIL; counts hold at CAND `1 of 7`, QUOTED `0 of 7`. There is no `R7`: `RZ` does not extend the
  2026-09-02 series.
- [`PROMPTS-20260906-z-specification-session.md`](PROMPTS-20260906-z-specification-session.md)
  - **A PROMPT, NOT AN AUTHORIZATION; subordinate to `RZ`, which overrides it wherever they differ.**
  The brief for the fresh scientific-contract session that drafts Z's specification: reading order,
  the five authorized deliverables, the boundaries restated so none is inferred away, the criterion
  carve-out, and the return envelope. §2.1 carries the dependency instruction — a standalone Y
  construction and the historical-candidate cause-3 seed scan are examined **as examples, not as the
  whole question**, each candidate answered separately for `necessary` / `applicable` /
  `reusable-now`, with the two suspended-authority facts (`D-Y-CONSTRUCT` does not exist; `R4`
  suspends the scan pending `D-C3-VOI` **and** `D-C3-RUN`) flagged so a dependency claim cannot
  launder authority. `BEN-381` will disqualify the drafting lane from grading the legs it defines.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation.md)
  - **INDEPENDENT ASSESSMENT — adopts no criterion, grades nothing, authors nothing.** Part A is the
  minimum acceptance requirements `A1`-`A31` for Z's criteria, derived from `RZ`, `R1`-`R6`,
  `CRITERIA` §0's four legs and `SPEC` §6's rulings *plus the note and paper's own conditional
  sentences*, and **committed before the proposal above was read** (its sha256 is recorded as
  digested-not-read). Load-bearing: `A1`/`A2` separate assessment completeness from adoptability from
  licensing a publication claim, and measure that the publication's own precondition is *"the
  adopted, selection-complete"* covariance -- **two** properties, not seven discharged causes;
  `A12` records that `R3` and §6.2 forbid rejecting Z for a LARGE magnitude on causes 7 and 1;
  `A18` is §6.6's adopted statistic/denominator/precision-target/boundary-together constraint;
  `A25` derives that no bound on a diagonal bounds `r^T C^-1 r`. Four re-measured findings, incl.
  that the 42-bin `(E_avail,W)` object takes the 5D trunk in **through the statistical block only**
  (`eavailW_covariance.py:441`, `C_lateral` diagonalized at `:469`), and that **four** projection
  builders exist with one on the `R6`-diagnostic PET path.
  **Part B is the review: VERDICT = BLOCK on the proposal's §7 items 1-3; item 4 (record the `pinv`
  cutoff policy and the retained rank per member) is READY and separable.** Blocking: `B1` C-1's
  declared population is **empty** -- measured, the `\gbdtFive*` macros are defined at
  `values.tex:112-115` and used **nowhere**, and no deliverable quotes any non-2D significance, so a
  `max` over "the pairs the publication quotes" is vacuous; `B2` §7 item 2 asks for the margin of a
  claim the publication does not make and `R5`'s default is that it never will; `B3` **zero**
  occurrences of `INCONCLUSIVE` against RULED `SPEC` §6.3(4), and the missing branch --
  `PREDECLARE-20260901-cause3-mii` §4's `VACUOUS SEED VARIATION` -- is the positive control; `B4` §7
  item 3 is stale (`ceb474cc`, 2026-09-09, postdates rev. 5) and as specified would test agreement
  over a domain selected for agreement. **Axis (c) is CLEAN: nothing over-rejects** -- all three
  candidates are sensitivity, not magnitude, statistics, so `R3`/§6.2's magnitude-blindness is not
  breached. §B.7 **withdraws Part A's own `A30`**: Z's design is `N = 4`-`5` and FITS `R5`
  (`44.6%`/`69.7%`), the `5x`-`9x` figure prices a design §6.3 does not adopt, and the binding
  constraint is the schedule.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partF.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partF.md)
  - **PART F of the same independent assessment — the ENDPOINT-A yardstick, and it adopts no criterion,
  grades nothing and authors nothing.** `F1`-`F21`, derived at `6f24fb00` from Ruling 1 (no Z-dependent
  non-2D significance; 2D scope unchanged), Ruling 2 (finite-ensemble **disclosure only**), the note's
  own declarations (i)-(v) at `app_statmethods.tex:645-658`, and `paper_body.tex:145-148` — **committed
  before the designer's endpoint-A packet existed**, with the prior packet's and recommendation's
  sha256 recorded as digested-NOT-read. **`F.5` pre-registers the seven BLOCK conditions** so no
  verdict can be fitted afterwards, and one of them (`F18`) blocks in the PERMISSIVE direction:
  imposing inversion-grade criteria (the `rho` bound, retained rank/subspace, `rcond`, `ndf`,
  `s_sig`) on an endpoint that releases no significance rejects acceptable cases.
  **Three measured findings.** `F-0`: **both governing rulings are unrecorded** — no
  `DECISION-2026091*`/`RULING-2026091*` file in any of 131 refs (newest is `DECISION-20260907`), four
  distinctive relay phrases absent with an in-loop positive control firing on 24+ refs; Ruling 2's
  disclosure-only half is nevertheless anchored, re-stating Joseph's recorded 2026-08-22 *"disclose, do
  not correct"*. `F-I`: **a released projected uncertainty IS a function of the source covariance's
  off-diagonals** — `diag(M C M^T)_i = sum_{j,k->i} w_j w_k C_jk`, forced by the `10,694 -> 42`
  geometry (pigeonhole >= 255 cells per destination row), so the diagonal-only premise for deferring
  `cause3_corr` is false; the relayed mechanism is **corrected** (`Mew` is built inline at
  `eavailW_covariance.py:404-406`, NOT by `project_cov_nd`, and **width-weighting is not the cause** —
  multi-cell row support is, unit weights included). Probe
  [`state/probe-z-endpointA-projected-diagonal-20260910.py`](state/probe-z-endpointA-projected-diagonal-20260910.py),
  `rc=0`, production `uq_math.project_covariance`, three controls incl. one in the opposite direction:
  at fixed diagonal the released sigma spans `0.986x`-`2.803x` under equicorrelation and `2.62e+06`
  over PSD structures, reaching ~0 — the *"looks like a very good measurement"* hazard
  `eavailW_covariance.py:410-413` already names for empty rows. `F-II`: the ensemble-size evidence is
  **stronger than cited AND still holed** — `--expected-ids` + `replica_manifest.py:44-48` is a
  fail-closed bidirectional set-equality check, not an `#SBATCH --array=` declaration, but it is a
  launcher constant that cannot prove ADEQUACY, and `OI-17`'s `122 of 160` is the precedent. Also
  measured: **two normalization conventions in one sum** (biased `1/N` `uq_math.py:104` vs unbiased
  `1/(N-1)` `combine_cov_nd.py:20`), and the ~45 MAT bands are deterministic rank-one despite going
  through `mat_covariance` at `N=2`, so Ruling 2's block set must be partitioned by **sampling
  character, not by computing function**. `F9` (**what "verified" means** — re-measurable from the
  artifact, or established by a construction-time check) is **RESERVED to Joseph and deliberately not
  answered**, since answering it is a design choice. `F.6` re-measures this lane's independence: the
  `D1` retained-subspace remedy is live as clause (d) at `173baf44:392`, labelled RELAYED, and was
  attacked and bidirectionally tested by a THIRD lane — the routing Part E asked for.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partG.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partG.md)
  - **PART G — the endpoint-A consumer set MEASURED, and two self-corrections where Part F demanded
  more than Joseph's ruling does.** Adopts nothing, grades nothing, authors nothing.
  **`F-0` is CLOSED:** both rulings are now committed verbatim at `a11d6cdd`, so Part F's `RELAYED`
  labels point at a sha; the finding is retained rather than withdrawn, and **`F9` survives the landed
  text** — neither record defines *"verified"*, so its two readings are still open and still differ by
  a code change.
  **`F-III`, the decisive measurement.** `PACKET-20260910:232-235` classifies all five endpoint-A
  consumers as diagonal-only. Measured per consumer: **`C6` and `C7` are correct** (`coverage_valid_nd.py:44-54`
  reads `GetBinContent(i+1,i+1)` off a stored TH2; `_sqrt_trace_from_diag` materialises no matrix),
  **`D1`/`D2` are correct today** but acquire the dependence once the 5D→3D projection their own row
  calls *"pending"* lands, and **`C5` is FALSE ON ITS OWN CITED LINES** — `:441` is
  `project_covariance(C5stat, Mew)` and `:466` takes `np.diag` of `C_lat_e`, built two lines earlier at
  `:464` as `Me @ C_b @ Me.T`. **The chain to Z is closed:** `eavailW_covariance.py:143,145` default to
  `uq_cov_stat_5d.root:hCov_stat5d_reported`, which `SPEC-20260906:504` binds as *"Z's candidate `C_stat`
  input"* (sha `6580016f…`) and `:610` puts in `C_Z`. So one released band is a functional of a Z block's
  off-diagonals. **The defect is the classification METHOD** — classified by the last operation rather
  than by the provenance of the matrix it reads — and the refuting words sat one column away, in `C5`'s
  own *"**produces** `C_low`"*.
  **Convergence recorded, and the criterion deliberately NOT supplied:** Joseph's verbatim adequacy
  check (*"retained-rank and subspace stability do not by themselves establish stability of projected
  uncertainties … show which criterion controls changes in the actual released error bars"*) asks from
  the other side exactly what `F-I` answers mechanically — and `F-I` was committed at `c695f209` before
  that text was read. Proposing the criterion is the designer's task; supplying it would spend this
  lane's verdict on it (Part E §E.1). *"Do not reopen the universal-bound approach"* independently
  confirms `F18` and makes the clause-(d) independence question **moot for the recommended path**.
  **Two corrections against the verbatim ruling:** `F12` is reduced to the bare *"mark as not
  applicable"* (the reason becomes a recommendation), and `F11` is **folded into `F9`** — the ruling
  asks for one verified number, so demanding intended-and-achieved as two was over-reach; the surviving
  point is that *verified* is unsatisfiable for one number when the two can differ, `--expected-ids`
  being a launcher constant that proves consistency and never adequacy (`OI-17`, `122 of 160`, still
  open). **§F.5's pre-registered block list is five items, not seven.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partH.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partH.md)
  - **PART H — READ THIS BEFORE CITING ANY EARLIER PART AS CLEARANCE.** ⚠ **The latest designer commit
  this lane reviewed is `173baf44`. Nothing in Parts A-G clears `8d3071a8` or `b40686ec`**, and the
  unreviewed delta is an entire artifact, not a labelling fix: `PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md`
  (**+505/−0, new**, sha256 `e04b4983…`, digested-NOT-read), `state/probe-z-projected-stability-20260910.py`
  (**+327/−0, new**), plus `+35/−10` on the consumer-set packet and `+12/−3` on its check script. **A
  `READY` in Part B or Part D is a verdict on `2ebdf095` and is two revisions stale.** §H.1 carries the
  per-part referent table so no reader has to infer it.
  **`F-0` is CLOSED on its own criterion** — Part F's criterion was existence on *any* ref with
  diffability as the stated consequence, and that is met; re-reading it as requiring reachability from
  `main` would be moving the criterion after the fact to keep a finding alive. **The criterion then did
  its job, measured:** both records changed between `a11d6cdd` and `ae876e14`, the change was a
  metadata timestamp placeholder (caught by the mathematical reviewer), and the **verbatim Appendix A
  blocks are byte-identical** (`0bd716c2…`, `2d2587a4…`), so Part G's quotations of Joseph hold at the
  decision lane's tip. **§H.2a files the residual NARROWLY instead: a ruling that governs `main` is not
  reachable from `main`** — `origin/main`'s newest ruling record is `RULING-20260908` and both 09-10
  records are ABSENT there, so a session pinning `origin/main` cannot see the constraint binding it.
  Closing that is a merge, not requested here.
  **§H.3 is the disqualification list.** DISQUALIFIED on exactly one item: the retained-subspace gate
  `‖P_0 − P_k‖_2 <= 1e-8` and its tolerance (clause (d)) — found the hole, supplied the fix — and
  likely moot since *"do not reopen the universal-bound approach"* removes the bound from the
  recommended set. **NOT disqualified on the projected-uncertainty boundary**, because `F9` was left
  unanswered and §G.1 stopped at the convergence deliberately: **the line is between "here is what must
  be true" (a requirement, which does not disqualify, or no reviewer could review twice) and "here is
  the statistic, denominator and number" (a remedy, which does).** RECUSED from *grading* per
  `BEN-381` — assessment is not grading. **Declared weakness, not a disqualification:** if the new
  packet's §1/§1.1 transcribe Part G's `F-III`, this lane confirming them is partly self-confirmation;
  `F-III` is a measurement of the code and will be re-derived rather than cited, but a second reviewer
  should spot-check that slice. §H.4: *"the orchestrator"* in Parts A-G re-points — that session ended
  and a different one holds the role.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partI.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partI.md)
  - **PART I — assessment of the endpoint-A packet's §2/§2.1 and §3/§3.1-§3.3** at `05bf8647` (sha256
  `e5fbd9a9…`), against `F1`-`F21` and §F.5's five block conditions, which were committed at
  `c695f209` **before this packet existed**. **No grade assigned** (`BEN-381`).
  **§3-§3.3: every mechanical claim CONFIRMED BY EXECUTION**, not by reading —
  [`state/probe-z-cause3corr-binding-site-20260910.py`](state/probe-z-cause3corr-binding-site-20260910.py),
  `rc=0`, in-process registry mutation only. All five §3.1 rows reproduce, plus **two positive controls
  the packet does not carry**: deleting `cause3_agg` RAISES (so `assess` does consult the registry and
  the byte-identity is a real negative, not a blind one), and the scope statement flips to `None` when
  a `sees_correlations=True` leg is declared (so the narrowing is leg-derived). **Strengthening owed to
  the packet:** the registry line is not merely *inert* but **structurally unreachable** — `assess`
  looks up boundaries only at `:247` and `describe()` only at `:110`, both keyed on declared legs.
  **§3.3's "costs nothing today" is structurally true rather than lucky**: leg adopted + boundary
  withheld gives `assessable=False`, `reject_conditions=('4c',)`, `is_met=False` **at `s_corr=0.001`**,
  so the refusal is on the ABSENCE OF A LIMIT, not the value. Option ordering does not invert.
  ⚠ **§2.1's SAMPLE-COVARIANCE POPULATION IS NOT TWO — `Flux` IS THE THIRD, and the chain is closed in
  tracked code:** `adopt_unified_5d.py:42-43` puts `"Flux"` as the 13th `VERT_BANDS` entry;
  `z_contract.py:66` imports exactly that as Z's `V`; `z_assembly.py:4` sums `V` **inflated through
  `D_Z`**; `unified_throw_cov.py:467-468` builds it as `mat_covariance(...)` over the flux universes;
  `uq_math.py:96-104` is **biased `1/N`**. `OI-137` independently enumerates **three**. So A-6 omits a
  block **and** its *"one script, one convention"* `1/(N−1)` claim is **false of part of Z's sum** —
  affirmatively misleading, which is what `F8` exists to prevent. **Diagnosis: the derivation is what
  admitted it** — reading the formula's surface is right, but `Σ_V C_b` is itself a sum and the third
  sample covariance is one level INSIDE it. Feasibility is fine: `n_flux` is already inventory-derived
  (`:126`) and already fail-closed both directions (`:461-465`). `C_unified` named as a boundary case
  and explicitly NOT required.
  **The coordinator's ensemble measurement: CONFIRMED, on better footing than offered** — `OI-160`
  already records both *"an exact-population validator cannot see a contract change"* and the
  member-scoped set as **100 boot + 24 split**, so equal-`N` needs no cluster read and the `cp -p`
  caveat drops out of the consequence; `07c18aee` confirmed at 2026-07-14, after the products. The npz
  **key schema** is a content-based discriminator stronger than `mtime`, but it discriminates the
  INPUTS while the product is a bare `TH2D` — so the caveat is correctly placed. **Sharpest form: `N`
  is a count, and a count cannot identify a population**, so A-6 part (a) cannot substitute for part
  (b), which the packet does not say.
  **§I.4 concedes my own §2.6b citation** (correct site is §2.6c item 4, `:1122`; substance survives) —
  **and `SPEC:3629` makes the identical error**, one line below a correct §2.6c citation, so the
  correction should land there too or the spec keeps producing it. **§I.5 records a gap in my OWN
  pre-registered block list:** condition 3 covered population **over**-inclusion only, so the flux
  finding is under-inclusion my §F.5 did not pre-register — the one-directional-guard failure `F15`
  demands against, in my own pre-registration.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partJ.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partJ.md)
  - ⚠ **PART J WITHDRAWS THIS LANE'S "clause (d) is moot" CLAIM — read it before relying on Parts F, G
  or H's disqualification paragraphs.** Measured at `05bf8647`: the packet's §2 table carries **A-4**
  (*"retained rank and retained-subspace projector gap across members, `‖P_0 − P_k‖_2 ≤ 1e-8`"*) as a
  **live** endpoint-A requirement with **no reference to the ρ bound**. The claim was true only of
  clause (d) as a terminal-outcome sub-clause of the ρ-leg at `RECOMMENDATION:392`, and false of the
  **test** the clause states — a clause's ROLE conflated with its CONTENT. **Anyone acting on "clause
  (d) is moot" drops a live A-4 requirement**, and the error's direction is permissive. Withdrawal
  banners placed at **all three** sites, since the surviving site is the one a reader lands on.
  **§J.1a: I held the disproof in a LATER part and did not collide it.** Part I §I.6 recuses from
  A-4 *"including its row in §2's table"* — and a recusal presupposes the item is live, so Part I
  contradicts F, G and H while quoting the row that disproves them. Same shape as `A14` vs `A30`;
  writing it up once did not prevent the repeat. **The mechanical fix: when recusing from an item,
  grep my own corpus for its name** — `grep -in moot` would have returned three of the four sites.
  **§J.2 relays clause (d)'s substance and assesses none of it** (sound as necessary, not sufficient
  since retained eigenvalues can move at fixed subspace, `1e-8` not load-bearing) — including the
  parts favourable to what this lane supplied. **§J.3 accepts the sharing-structure finding as REAL
  and rejects A-6 as its home:** Ruling 2's verbatim field list is `N` + convention + treatment + `p`,
  so requiring sharing structure of A-6 is a proposal to EXTEND the ruling (Joseph's call), not an A-6
  conformance defect — whereas the equal-`N` finding is an INTERNAL insufficiency, A-6's own part (a)
  failing to substitute for its own part (b). One A-6 defect, one gap in whatever consumes `B`; **not
  additive against the same requirement.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partK.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partK.md)
  - **PART K — the `assessor-F6` / reviewer-`F3` convergence ACCEPTED at the hazard level, and `F6`'s
  predicate delimited so a rev.-3 clause is not written against a reading `F6` does not support.**
  One hazard measured twice from opposite ends — a variance positive only by round-off, read as a real
  measurement (`eavailW_covariance.py:410-413`, re-verified) — **two measurements of one hazard, not
  two hazards.** `F6`'s own text already carries the structural point one level over: `:429`'s warning
  is gated on **exactly-empty** while `F-I` reaches near-zero at a **fully populated** row, which is
  the exactly-zero-versus-round-off distinction relocated.
  ⚠ **§K.2 DECLINES the extension, against this lane's own interest.** `F6` reads *"a **released
  projected row** … at the **point of release**"*; `s_proj` is an acceptance statistic, not a released
  product, so `F6`'s predicate never reaches its internal baseline and *"`F6` covers `F3`'s
  147-cohort"* does not follow. **This is the same wrong-stage correction this lane gave the
  coordinator about the sharing-structure finding, applied to its own item** — being the beneficiary
  of the over-extension is why it had to be said.
  **§K.3 names the gap that follows and refuses to close it:** a round-off-positive baseline inside an
  acceptance statistic is covered by **neither** `F6` (wrong stage) **nor** `A-7`'s abort claim (wrong
  condition — exact only for an exactly-zero baseline). A gap in the requirement set, not in either
  finding, and one that survives review because each half looks covered from the other's side.
  Proposing the closing requirement would spend this lane's verdict on `A-7`; §J.2 declined once
  already. **§K.4: reviewer `F3`'s 500-trial split is NOT re-run or verified** — §4.3/`s_proj`/`δ_proj`
  are routed away, so the convergence is accepted on the strength of the `F6` half only.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partL.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partL.md)
  - **PART L — the coverage items: §2's rows A-1/A-2, §5, and §7's residues**, at `05bf8647` against
  `F1`-`F21` and §F.5's block conditions. No grade assigned.
  ⚠ **A-1's "§3.3's FIFTEEN reject conditions" is NINETEEN.** Enumerated at `6f24fb00`, §3.3
  (`:1242-1295`) carries `1`-`15` **plus `4b`, `4c`, `11b`, `11c`**. **And the omission is
  load-bearing: `4c` is the condition this packet's own §3 depends on** — §3.1(e) cites
  `reject_conditions=('4c',)` by name and Part I's probe reproduced it, so §3.3's *"costs nothing
  today"* is true **because `4c` bites**. `11b`/`11c` are labelled REV. 16 additions, so "fifteen"
  reads as a pre-rev-16 count quoted after the work that changed it — the expected-count shape, third
  instance this campaign, one of them mine (`B8`). A-1's CLASS (FIXED by spec) is right; the count and
  therefore the set are not.
  ⚠ **A-2's stated ground supports ONE declaration and the row requires FOUR.** "Four" is correct
  ((v) is A-6's) and I do not manufacture a count error. But against an endpoint that performs no
  inversion: **(i)** has no inverse to declare and **(ii)** no `ndf` — **unsatisfiable** except as
  "not applicable"; **(iii)** a rank-truncation scan is a NEW MEASUREMENT on a 10,694-bin object,
  which `F20` forbids requiring; **(iv)** transfers cleanly and is the only one A-2's own sentence
  argues for. **This hits §F.5's pre-registered `F18` condition** — inversion-grade criteria on an
  endpoint releasing no significance, the condition I said I expected to have to defend.
  **§5: the disposition is right and the characterization inverts the note's own scoping.** The three
  code facts verify, but clause (ii) does not reach 2D — `:645` scopes it to *"an N-D covariance"* /
  *"Any N-D χ²"*, `:628-634` **affirmatively justifies** the 2D choice (*"tested and holds… the scan
  is the evidence; 205 is not assumed"*), `:636` says *"it does not transfer to the N-D covariances."*
  **"LIVE" also unestablished:** `RANK-AND-INVERSION-20260810.md:56` verdicts the ours-only `252` as
  *"safe — it is the illustration, not a result"* and as a **pseudo-inverse**, where this script's
  branch is the **direct** inverse (`:126`). **Qualification 1 is unverified**: the inverted object is
  `Cu + Cb` (`:117`,`:120`), which the note puts at rank `140→201` (`:693-696`), and
  `np.linalg.inv` does **not** raise on a near-singular matrix, so `:127-133` does not cover it.
  **Qualification 2 (*"out of scope is not conformance"*) is correct and well-made** — exactly `F17`.
  Net: do-not-change survives because the file is a **diagnostic outside the released set**, which
  overstates neither the defect nor the protection.
  **§7 is an unusually good residue list** — residue 8 states the withdrawal-checker hole at severity
  with a handoff and names its own detector; residue 11 re-pins a population **by set difference, not
  by count**. **Two absences: `F2` is unmet AND unrecorded** (no released projection names its builder
  and commit, with four non-equivalent builders and a `main` finding that they diverge on refusal) —
  culpable; and the block-population assumption §I.2 falsified is unrecorded — **expected, not
  culpable**, since a residue list cannot name an unnoticed assumption, but flagged so its absence is
  not read as clearance.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partM.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partM.md)
  - **PART M — rev. 3 assessment at `6bb8b32d`** (sha256 `dad55b57…`, 908 lines), against `F1`-`F21`
  and §F.5's block conditions. No grade assigned.
  **§M.1 records an ATTACK OF MINE THAT FAILED.** I expected rev. 3's *"constructions sharing the
  biased normalizer: thirteen"* to be my own §I.2 population error recurring — `:460`'s loop runs over
  `KNOB_BANDS`, not `VERT_BANDS`, and with `|R| = 27` the count could have been nearer 40. **Measured:
  `unified_throw_cov.py:79-80` defines `KNOB_BANDS` as exactly 12, `"Flux"` excluded, zero entries
  outside `VERT_BANDS`.** So 12 via `:460` + flux via `:467` = **thirteen is correct** and my
  hypothesis was unfounded. Recorded because a review reporting only its successful attacks
  misrepresents its coverage.
  **§M.2: `F7` fully incorporated and correctly extended** — three blocks, `C_flux` named as *"one
  level inside `Σ_V C_b`"*, per-block biased/unbiased split, and the normalization **verified
  numerically against `Z'Z/N` rather than read from the docstring**, which is stronger than `F8` asked.
  The `C_unified` restraint is preserved with its reason.
  **§M.3: `F10` confirmed independently on every leg, and the composition question is sharper than
  "supersede or duplicate."** `PROVENANCE-20260822-declaration-v-scalar5d-blocks.md` is **on
  `origin/main`**, its `:143-144` gives the **same** `N=100`/`24` values and the **same** *"enforced,
  not merely declared"* argument from the same raise, and rev. 3 cites it **zero** times. **New:** that
  record evidences `N` from `sbatch_finalize_5d_bkgaware_gpu.sh:167,168`, which at `6f24fb00` are
  `:422,423` — *"THE TWO MEMBER-LOCAL COMBINES"* (`:418`), i.e. **the member-scoped arm §2.1a says
  cannot have produced the digested bytes.** So ruling 10's record may be **right about `N` and wrong
  about the arm**, which makes "supersede / duplicate / extend" non-exhaustive — the equal-`N` finding
  turned on the provenance record itself.
  **§M.5: Part L's four findings are UNTOUCHED at `6bb8b32d`** (verified by `grep -c` on each claim
  string, `1 → 1` for all four), so `F13`-`F16` transfer verbatim with no re-derivation; §3's mechanics
  re-verified, probe `rc=0`, both controls passing.
  ⚠ **§M.6 DECLARES FIVE SLICES that now carry this lane's own contributions** (`:116`, `:166`,
  `:197`, `:294`, `:346`), enumerated rather than spot-declared. None is a remedy — each is
  re-derivable from cited lines, so independence for the packet holds — **but `§2.1a(b)` and §3.1's
  inertness paragraph are partial self-confirmation** (the equal-`N` framing and *"structurally
  unreachable"* are mine), and a second reader should spot-check them. Extending the boundary rather
  than waiting to be asked.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partN.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partN.md)
  - ⚠ **PART N WITHDRAWS THIS LANE'S OWN "structurally unreachable" STRENGTHENING** — read it before
  relying on Part I §I.1 or on rev. 3's `:346-347`, which adopted it verbatim. A covering grep of
  `z_validator.py` at `6f24fb00` gives **FOUR** `boundary(...)` sites, not two: `:83` (leg-keyed,
  result discarded), `:110`, `:247`, and **`:296` inside `assess_null`**, whose signature at `:286`
  takes `boundary_key` as a **caller-supplied parameter with a default, not a declared leg** — so
  `assess_null(r_null, boundary_key='cause3_corr')` reaches it with no leg declared. **The
  exhaustiveness claim is false, so the conclusion is not established by that argument.** Measured
  caller census: five sites, **zero** non-default, so the path is **latent, not live**.
  **§N.2 — the irony is the finding, and it is the reviewer's:** I replaced *"inert"* (contingent) with
  an absolute word, and **the truth is contingent** — closed by a caller census, a fact about today's
  callers. *"Inert" was contingent in precisely the way the truth is contingent*; the connotation I
  objected to was the accurate one.
  **§N.3 — THIRD INSTANCE, and I held the disproof in my own grep output.** The Part I grep printed all
  four sites; I wrote *"exactly two."* With `B8` (eight launchers, wrote seven, because the spec said
  "exactly seven") and `A14` vs `A30`, all three share one mechanism: a correct measurement, then a
  claim over a **filtered subset** of it, the filter unnoticed and pointed toward the argument being
  made. Per-cell checking cannot see it; only diffing the raw output against the claim's population
  can. **And this one propagated into another lane's artifact and was adopted verbatim**, so neither
  author could catch it — which is why Part M §M.6 enumerated all five contribution sites, and is the
  strongest evidence yet that the boundary earns its cost.
  **§N.4: not prescribing the replacement wording** — correcting my own claim is required; choosing
  what §3.1 says instead is the designer's. **§N.5:** `:294` upheld and **upgraded to a live worked
  instance** (`PROVENANCE-20260822` = right `N`, wrong arm); my content-discriminates-inputs hedge
  discharged in my favour; their *"inverts"* withdrawn with **(a) duplicates, (b) repairs** standing;
  the *"could not have completed"* tightening **relayed, not verified**.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partO.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partO.md)
  - **PART O — rev. 4 at `d915fe00`** (sha256 `bb752c9d…`, 1123 lines). No grade assigned.
  ⚠ **§O.1: the producer feeding `Σ_V C_b` is the UNIVERSE SWEEP, not `KNOB_BANDS`.** `SPEC:624` reads
  `Σ_V C_b` as `hCov_universe5d_<band>`, *"the same sweep estimator as the rest of `C_syst`"*;
  `analyze_universes_5d.py:290` writes those and `:213-222` builds each as `(Z.T @ Z)/D.shape[0]` —
  **biased `1/N` with per-band variable `N`**, skipping `< 2`. `unified_throw_cov.py`'s twelve `±`
  pairs (`:460`, arity forced at `:458-459`) plus flux produce **`C_unified`**, whose diagonal sets
  `g^c` — **not** the summands of the sum. So rev. 3-4's *"thirteen constructions"* is accurate about
  the **wrong producer** for A-6's purpose. **This also retires my own §M.1 reasoning:** I tested
  whether `KNOB_BANDS` was the right cardinality and never asked whether it was the right producer.
  **§O.2 answers the stability question: the two partitions RECONCILE EXACTLY** — same 45 bands cut two
  ways, `|V|13 + |R|27 + |A|5 = 42 pairs + 2p2h + Flux + norm = 45`, with `42×2 + 3 + 100 = 187` (+1 =
  the `188` file count). So *"stated and unreconciled"* is a choice, not an inconsistency, and the
  caution is sound — **but the one-line identity belongs in the record**, because a disclosure
  requirement quantified over "each block" is exactly where an unstated re-partition becomes a silent
  population change.
  ⚠ **§O.3: `2p2h` is OPEN and the code gives no basis for excluding it.** `analyze_universes_5d.py:220`
  applies **one** estimator to every band and makes no distinction between `2p2h`'s `D.shape[0]=3` and
  `Flux`'s `100`. **And `PROVENANCE-20260822` contradicts itself on it:** `:128` calls `Flux` *"the ONE
  genuine multiverse draw"* — entailing `2p2h` is not one — while `:127` *"explicitly declines to
  classify it"*. Not resolved here: it needs `PROVENANCE:233` item 6's bank read. If they are draws,
  `F7`'s recursion runs **two → three → four**.
  **§O.4: my §I.2 was a RE-DISCOVERY** — `PROVENANCE:128` has carried `Flux`/`100`/biased-`1/N` on main
  since 2026-08-22, and rev. 4 discloses that at `:198-199` **against its own interest**, which is the
  behaviour the review structure exists to produce.
  **§O.5: `F14` acted on cleanly** (A-2 narrowed to clause (iv), with (i)/(ii) as not-applicable and
  (iii) rejected as new compute — each with its reason, no silent drop; endorsement is **partial
  self-confirmation**, added to the §M.6 list), and **`F17` resolved on the composition principle** of
  Part J §J.3, returning A-6 to four fields with no Ruling-2 extension. **§O.6: the F10 row's HEADER
  still carries the withdrawn word *"INVERTED"*** while its body says *duplicates / repairs* — an
  incomplete withdrawal reaching the body and not the header, the same mechanism as my own three-site
  failure, and a header outranks the caveat beside it.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partP.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partP.md)
  - **PART P — rev. 5 at `c33b5c86`** (sha256 `2366bf84…`, 1145 lines, `+26/−4` one file). Both fixes
  verified: **F20 closed** (`grep -c 'THEN INVERTED'` → **0**; the F10 header now names F20), and
  **`2p2h` stated as unresolved at header level with `PROVENANCE:233` item 6 as its route** — the
  disposition Part O §O.3 said the evidence supported, without claiming the answer.
  **§P.2 — the F7 row, handed to this lane explicitly: NOT filed as a finding, and the coordinator's
  restraint is right.** The row records F7's own claim and verdict, F7's substance (flux omitted, wrong
  normalization asserted) is unconditionally true whatever `2p2h` proves to be, and the or-four warning
  is **header-level**, not a caveat below. One token's refinement offered — *"at least three"* would let
  the row survive being read alone, the test this lane applies to others' verdict words. **Self-reference
  declared:** F7 is this lane's finding, so grading its row's wording would be grading the presentation
  of its own work.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partQ.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partQ.md)
  - **PART Q — A-6(b) after the authorized provenance search.** No grade assigned.
  **§Q.1 resolves the coordinator's pending OPERAND question:** `combine_cov_nd.py:20` computes `C`,
  `:22` prints `sqrt(Σ C[i,i])`, and `:23-26` writes **that same `C`** — so the logged `sqrt-trace` and
  `sqrt(Σ h(i,i))` are the same object up to an exact double round trip, and neither `.3e` formatting
  (~0.03%) nor ROOT under/overflow can explain gaps of **3.6%** / **4.6%**. **But that closes the
  operand question, not the READER question** — their stated weakness (no known-matching case, so no
  demonstration the instrument returns `True`) stands. **A positive control is available in the same
  log line** — `reported 10694 bins` against the stored `n × n`, which tests addressing without
  needing a matching trace — **named, deliberately not run**, since running it would spend this lane's
  verdict on the fingerprint.
  ⚠ **§Q.2: the two exclusion grounds point OPPOSITE ways and the exclusion is SINGLY supported.** The
  fingerprint excludes; the job-level `TIMEOUT` does **not**, because the `--expected-ids` enforcement
  runs at `replica_manifest.py:44-48` via `:18`, **before** the `:22` print and `:23-26` write — so the
  logged *"100 replicas … [wrote] …"* lines are themselves evidence the check passed and the product
  was written. A timeout killing later stages cannot retroactively falsify a completed step. **If the
  fingerprint falls, nothing else excludes this execution.**
  ⚠ **§Q.3: §2.1a(ii) is underspecified at the word "SUCCESSFUL", and with one candidate execution the
  unit IS the answer** — job-level (`sacct -X` → `TIMEOUT`) fails, step-level (both combines printed and
  wrote) holds. The launch-plan-versus-record shape at the level of a single word. What would settle it
  is named (`sacct -j <job>.<step>`, a step exit code, or the log lines) and **not chosen** — the
  adjacent "what does *verified* mean" is already reserved to Joseph by `F9`.
  **§Q.4: the equal-`N` finding is STRONGER than when filed** — `N` for the released bytes rests on no
  surviving execution record, so part (b)'s only candidate evidence is under exclusion — **and the arm
  ambiguity closes** to top-level. **Joseph's intended-use declaration ENTAILS `F1` rather than
  satisfying it:** *"its explicitly named projections"* requires the enumeration without supplying it.
  `F3` is largely met, indirectly. **§Q.5 accepts the routing of §3-§3.3 and the block population away
  from this lane as correct**, and flags that §3.1 carries a sentence of this lane's that is now
  **withdrawn**.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partR.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partR.md)
  - ⚠ **PART R — ANSWERED AND WITHDRAWN (§R.4): the answer is YES and it resolves AGAINST the question.** `unified_throw_cov.py:434` reads `xx = z["xs"]` (**unfolded cross-sections**) and `:437-442` assigns them to `knob_x[band][idx]`, so the ~45 MAT bands are built from **per-member unfoldings**, not the replicas — the population CAN exhibit the defect, `BEN-032` does not reach it, and §R.1's conjunction falls. **§R.4a: the detector's prior art is stricter than any lane stated** — `audit_gates_that_cannot_fail.py:585-587` names *"BEN-032 / SHELL_PIN_FLOOR"* in a `--min-files` refusal, `:592-593` **raises** on a detector failing its own power test, and `:471-474` records a step that *"silently blanked 95% of a file for eight days"* while *"provably powerful"* detectors reported clean. **The instrument enforcing the rule existed while three lanes violated it by hand.** §R.4b keeps why filing it was still right: it died to the one-line falsifier this lane specified and declined to run. Original framing retained below. **§R.5 (rev. 8 = `e968da42`): a LAUNCHER-level citation supersedes this lane's mechanism trace** — `sbatch_finalize_5d_bkgaware_gpu.sh:8-10` reuses the blocks while `:456` runs the bands combine under `mr_run`, the member-scoped runner, so the *production launcher* reuses blocks and regenerates bands per member. **`F22` carried at its CORRECTED strength: mandatory, not cosmetic** — and the *"whatever the cause"* half needs no lane's authority, since `audit_gates_that_cannot_fail.py:592-593` **raises** when a detector is not shown to fire. ⚠ **§R.5a narrows the watched residue to FIXED SUMMATION ORDER and REFUTES the cited cause:** measured, pairwise-vs-sequential is **bit-identical at n = 45, 128, 129 and 300**, so the `mii_anchor_comparator:241-246` route does not fire at band scale and **numpy's 128-blocksize story is not the mechanism** — if it were, `129` would differ from `128`. **Order is what perturbs** (`~5e-16`–`1.3e-15` on reversal). So the precondition rev. 7 silently acquired is one checkable property of one loop, not bit-reproducibility in general.
  - **PART R as filed — a routed QUESTION, explicitly not a finding:** under the **reuse** branch, does A-7's
  `s_proj` become a gate that cannot fail? `A-7` is routed away from this lane, so this composes **one
  relayed premise** (rev. 7 at `3e7c3271` derives `s_proj` as a function of `C_k − C_0`, so reused
  byte-identical blocks cancel exactly and `s_proj` measures **exactly `0.0`** on the reuse arm vs
  `0.562%` on regenerate) with **one measured fact** (`SPEC` §2.6c item 4 at `:1122-1125` — the
  reuse-vs-regenerate question is **OPEN**, *"this specification does not decide it"*, and §5 prices
  both). **If `s_proj` is exactly `0.0` on a branch Joseph may choose, then on that branch it returns
  zero irrespective of what it is meant to detect** — the repo's own named class, with
  `audit_gates_that_cannot_fail.py`'s header citing **BEN-032/BEN-025, *"a check run over a population
  that cannot exhibit the defect."*** **The designer's reading — exact separation makes the arms
  discriminable — is correct and is a virtue; the unstated reading is that on one arm the statistic
  cannot fail.** Same algebra, and which matters depends on an open decision. **§R.2 names the one
  condition that dissolves it** (if the member variation lives *wholly* in the reused blocks, the
  cancelling is correct reporting — cf. §2.6b's *"`C_stat`/`C_ML` are #13-invariant"*), and that check
  is inside the routed slice. **§R.3: filed rather than mentioned because it is a two-lane
  composition** — `(cause 6, Z)` owns the reuse question, A-7 owns the statistic, and a question owned
  by nobody survives review.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partS.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partS.md)
  - **PART S — the projection-manifest yardstick, COMMITTED BEFORE THE MANIFEST EXISTS** (designer
  `cc2a71aa`, sha256 `41704ebe…`, 1524 lines, **digested-NOT-read**), same discipline as Parts A and F.
  **§S.1 verifies the blocker and gives its sharper form:** `p4_lib.build_projection_M:1354` is
  *"marginalization of **one** axis"* with `require(len(nb) == 5)` at `:1361` and `strides_l` over
  `range(4)` at `:1369`, while P1 drops **3** axes and P2/P3/P4 drop **4** each — so none is a
  single-axis drop and iteration is closed off. ⚠ **But the sharper problem is that NO EXISTING BUILDER
  HAS BOTH PROPERTIES:** `project_cov_nd.build_projection:79-84` does arbitrary keep-axis subsets yet
  its own docstring has `dst_index_of` returning *"-1 to drop"* (**silent dropping by design**, neither
  orphan check), while `p4_lib` refuses in **both** directions (`:1380`, `:1395`, `BEN-064` masking
  defect) with the wrong arity. **So the manifest cannot be completed by naming a different existing
  builder either** — and this lane is not designing the resolution.
  **§S.2 pre-registers six BLOCK conditions.** `S2` is the one nobody else has raised and it transfers
  this lane's own measurement: **if any map composes single-axis drops, the composition ORDER must be
  declared** — width weights compose exactly so the mathematics is order-free, but Part R §R.5a
  measured that **order perturbs at `~5e-16`–`1.3e-15`** while pairwise-vs-sequential is bit-identical,
  which is exactly the scale a reproducibility gate sits at. `S3` is Joseph's declared-exclusion-vs-
  silent-discard item with its mechanism named (`dst_index_of` → `-1`), `S6` bars Q3's rank declaration
  from being read as an `ndf`.
  **§S.3: the manifest CLOSES `F1`** (the enumeration Joseph's declaration entailed but did not supply)
  **and makes `F-I` maximal** — P2's **seven** bars each aggregate ~**1,528** reported 5D cells, so
  **~1.17 million off-diagonal entries enter one released bar**, an order of magnitude past P1's 42-bin
  case, with `cause3_corr` still withheld.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partT.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partT.md)
  - **PART T — the PRE-IMPLEMENTATION baseline, pinned at `6f24fb00` before any code lands**, because
  *"additive only, no implicit fallback or overwrite"* can only be judged against a recorded before-state.
  §T.1 verifies six handed claims with two citations corrected (`adopt_unified_5d` `:80-81` not `:79-80`;
  `p4_lib`'s destination expression at `:1394`).
  **§T.2 makes §S.1 concrete as two line numbers:** `project_cov_nd.py:99`'s `dropped = int((~keep).sum())`
  is **source-side only** and sits in the builder that CAN express P1-P4's arity, while
  `p4_lib.py:1394-1395`'s `empty = np.nonzero(~M.any(axis=1))[0]` is the **destination arm** and sits in
  the builder that cannot. **The destination arm does not need writing — it needs moving, or the arity
  does.**
  ⚠ **§T.3 NEW FINDING: reuse-vs-regenerate is NOT open in code — it is selected by
  `MNV_EST_SEED_OFFSET`.** `SPEC §2.6c` item 4 calls it an OPEN scientific decision *"this specification
  does not decide"*, while `sbatch_finalize_5d_bkgaware_gpu.sh:421` prints *"MEMBER …: building **this
  member's OWN C_stat and C_ML**"* and `:425` prints *"undeclared: **reusing the archive's**…, per this
  script's original contract"* — and the `:8-10` header documents **only** the undeclared mode. The
  scientific rationale is genuinely undecided; the **behaviour** is not, and is bound to the membership
  variable. **This refines Part R against itself:** choosing a nontrivial `K` FORCES regenerate, so
  Part R's *"if Joseph chooses reuse"* supposed a freedom the launcher does not offer.
  **§T.4 strengthens the equal-`N` finding one level:** `:418-420` keeps `--expected-ids` at full ranges
  *"on purpose"* so a partial member REFUSES, so `N = 100`/`24` holds across the **whole member family
  by enforcement** — not two arms coinciding. `N` cannot distinguish **any** two members, which is why
  *"record the ACTUAL seeds, sources and revisions"* is the right instruction. **§T.5 holds `S2`**
  pending the implementation's route.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partU.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partU.md)
  - **PART U — pin 1 (`f4aa0f08`): VERDICT = BLOCK, narrowly, on the enumeration's population.**
  Everything else in this lane's slice is READY.
  ⚠ **§U.1: `MEMBER_LOCAL_TODAY` (`:105-113`) has SEVEN entries and each carries a line number
  (`# :404-408` … `# :414`) — the population was selected by a 13-LINE WINDOW.** Measured against the
  behaviour instead: the launcher has **eight** `mr_prefix`-family call sites, six inside `:403-415`
  and **two at `:422-423` — `boot_nd_5d` and `seedscan_split_5d`, the REPLICA INPUT DIRECTORIES**,
  member-prefixed on the same condition. They appear **nowhere** in the module (`grep -ci` → 0).
  Consequential for three ascending reasons: they fall in **neither** returned category
  (`recomputed`/`pinned`); `:141`'s note says *"**every** component varies"*, a universal over the
  enumerated set only; and **the omitted two are the EXPENSIVE ones** — 100 bootstraps + 24 splits
  against five cheap combines — so an enumeration used to price a member **understates cost by omitting
  exactly the costly entries**, with `:418-420`'s full-range `--expected-ids` refusal leaving no cheap
  third option. **The irony is the standing law:** `:103-104` warns against inferring the population
  from *"the COMB line alone"*, then defines its own from a window of lines — fourth instance.
  **§U.2 READY — decoupling sound**, verified directly: `:75-76` *"there is no default"*, `:80-82`
  digests **required** under `SHARED_DIGEST_BOUND` (*"Sharing a PATH…"*), independence explicit at
  `:67`. Part T §T.4 is why a digest is the only route: `N` cannot identify a member.
  **§U.3 READY — additivity at BOTH levels:** two `A` lines / 690 insertions / zero modifications, and
  **no file I/O** in the module (only hit for `open(`/`TFile`/`RECREATE` is a **comment** at `:355`
  citing `SPEC` §1.6). So the `RECREATE`/defaulted-`--out` hazards are neither triggered nor mitigated
  and stay live for a later pin — correctly **cited**, not claimed closed.
  **§U.4 READY — suites re-run with the control first:** `136` control / `30` new / **`56` passed + `1`
  skipped** (confirming *"57 OK"* was the COLLECTED count), and the skip is self-documenting at
  `:628` (lightgbm absent, itself a recorded finding). **This lane's own harness failed first** — *"no
  tests ran"* on all three, a can't-look zero from an uncreated worktree, caught by the control.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partV.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partV.md)
  - **PART V — pin 2 (`cc42cc3e`): Part U's BLOCK is DISCHARGED; new BLOCK on the non-member return
  contract.** Population now nine with the two replica dirs flagged and costed `DOMINANT`; the third
  category is warranted; the universal is **derived** at `:177`.
  **§V.1 PROVES exhaustiveness AND disjointness over the whole finite configuration space** (`member_offset
  ∈ {None,0,7}` × `block_source`): ✅/✅ in all six. **And supplies a property the code does not check** —
  `:176`'s `covered` is a **union**, which tests coverage and is blind to overlap, so a component in two
  categories would still read `covers_all_member_local = True`. Disjointness holds today and nothing in
  the artifact would notice if it stopped.
  ⚠ **§V.2 THE BLOCK: the non-member branch (`:153-155`) returns THREE keys where the member branch
  returns eight**, so on a fully correct non-member path `r.get("covers_all_member_local", False)` →
  **False** and direct access → **KeyError**. **That is verbatim the failure mode `:171-172` says the
  `not_used` category exists to prevent** — *"the coverage flag read False for a configuration that is
  fully specified, which would have looked like the omission it exists to detect"* — surviving one branch
  over, by **absence** instead of a computed value. Worse on the **majority** path, since non-member is
  the archive path. The campaign already ruled the shape: Ruling 2's *not applicable* and `F22`'s
  mandatory not-applicable-versus-satisfied. **Absence is not an admissible option;** which replacement
  is, is the designer's.
  **§V.3 credits a silently-failing trap avoided:** `:88` `is_member` is `member_offset is not None`, not
  truthiness, so **offset `0` is a member** — and `est_seed_offset=0` is a real declared value measured
  back in Part I. **§V.4** additivity cumulative: eleven `A`, only the three hook-required router files
  `M`, no production `.py` touched. **§V.5** suites `136` / `46` / `56+1`, control first.
  **§V.6 takes the offered `U` question:** the map-arm exemption is **correct** (a dense all-ones row
  cannot orphan a source bin), **but** `:470` applies `declared_exclusions` to **`M` only** while
  `:471-472` `vstack`s the extras unhandled, and `:307` scopes exclusions to **destination rows** — so a
  declared destination exclusion does **not** reach a functional dense over source columns. For P2 the
  `[3,100] GeV` catch bin **is** destination row 7, so an all-ones total rate would include support the
  displayed projection excludes. Possibly correct; **undeclared is the defect.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partW.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partW.md)
  - **PART W — cause-3 amendment adequacy conditions, COMMITTED BEFORE THE AMENDMENT LANDS.** Objection
  ground verified in three places: `SPEC:3550-3552` (*"the variation of the **assembled** `C_Z` … varied
  **jointly**"*), `z_contract:222-225` (`cause3_agg`, **unqualified**), `:233-235` (*"licenses nothing"*).
  ⚠ **§W.2 IS THE DECISIVE MEASUREMENT AND IT CLOSES TWO OF FOUR POSSIBLE ANSWERS IN ADVANCE.** The
  subset argument alone leaves an opening — `SPEC:3550` varies the **sweep-side and throw-side**
  baselines, and one could argue the blocks sit on neither. **Refuted:** `bootstrap_nd.py:47,55` passes
  `_est_seed` into the estimator and stamps it at `:67`; `seedscan_split.py:69` passes
  `args.estimator_seed` and stamps at `:99`. **Both excluded summands are functions of the estimator
  seed**, so holding them digest-identical suppresses a real component of exactly the declared
  variation. Response **(d) invariant is REFUTED**; **(c) negligible is unavailable as an assertion**;
  only **(a) narrow the claim** and **(b) narrow the subject — a contract change, Joseph's** remain.
  Plus Part T §T.3's independent tension: `:8-10`'s *"#13-invariant"* against `:421`'s member rebuild.
  **§W.3 pre-registers five conditions** — name which of (a)-(d); supply the measurement if (c)/(d);
  the operative word is ***licenses*** so changing what is MEASURED does not reach the objection;
  `cause3_agg`'s unqualified purpose must be qualified too or knowingly left; **no fourth grade token**.
  **§W.4: elements 3 and 4 must TRAVEL WITH THE GRADE** — `z_validator.py:166-167` already states the
  principle (*"the narrowing that must travel WITH the grade, not sit in a specification the grader may
  not open"*) and `_DIAGONAL_ONLY_SCOPE` is the non-suppressible mechanism, so licensing statements
  written in prose are put where the code says they do not survive.
  **§W.5 recommends `κ` stay WHOLE with the reviewer** despite its population clause being this lane's
  subject: a package split across two lanes has a seam, and silent removal is exactly what lives in
  seams — better to take it late than fragment it early.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partX.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partX.md)
  - **PART X — cause-3 amendment Part A (`1b7db825`): VERDICT = BLOCK, two consequential issues.**
  ⚠ **§X.1 DECISIVE — the licensing clause is placed where it cannot travel.** A.5 item 2 says *"add
  A.4's licensing clause to the contract, in `cause3_corr`'s existing template"*, and Part I §I.1 proved
  **by execution** that entry is **inert to the outcome** — deleting it leaves `describe()`
  byte-identical, since `assess` reaches boundaries only at `z_validator.py:247` and `LegSet.describe()`
  only at `:107-111`, **both keyed on DECLARED legs**, and `cause3_corr` is named by none (its own
  stated premise). `Boundary.describe()` does carry `reason` (`z_contract.py:206`), so a clause on a
  **named** boundary would travel — this one would not. **The amendment records the licensing
  consequence of the deferral inside the very entry whose unreachability IS the deferral.** And
  `_DIAGONAL_ONLY_SCOPE` / `z_validator` / `scope_statement` appear **zero** times in the amendment,
  though `z_validator.py:166-167` states the rule verbatim.
  ⚠ **§X.2 — the "ambiguity" frame is wrong on the DATES, and it changes what Joseph decides.**
  `MNV_EST_SEED_OFFSET` first commit **2026-08-18**; `SPEC-20260906` appears **2026-09-06**, nineteen
  days later, against a **binary** launcher (`:417` own blocks / `:424` archive reuse). **So (a) and (b)
  were not indistinguishable — (b) DID NOT EXIST**, and `SPEC:3550` was written when only (a) was
  producible. Its natural referent is **(a) TOTAL**, so the decoupling **creates** (b): this is Part W's
  response **(b) NARROW THE SUBJECT**, a contract change and therefore Joseph's. *"Which did you mean?"*
  puts the burden on his memory; *"may I narrow the declared quantity, and here is why"* puts it on the
  proposer — **and A.6 already contains that argument. Right question, wrong grammar.**
  **§X.3 records what is satisfied, one of it well:** `W2` is met **honestly** — the amendment does not
  claim invariance or negligibility, and A.4(i) says *"the components held fixed are exactly the ones
  not tested"*; A.4(ii) adds a correct point this lane had not required (finite-ensemble is common-mode
  under fixed digests and cancels in `C_k − C_0`). `W5` satisfied, with the mechanism noted as looser
  than stated.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partY.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partY.md)
  - **PART Y — cause-3 Part A at `f00e4bee`: VERDICT = BLOCK on ONE LINE.** Supersedes Part X, which
  does not carry forward. Content, destination and derivation all correct, and the clause **does** travel
  on refused outcomes — verified by execution.
  ⚠ **§Y.1 THE BLOCK: the interception point is OPTIONAL.** `:753` `def evaluate_a7(…, build_path=None, …)`
  and `:25` `scope = … if build_path is not None else None`. **Measured: the default call returns
  `state=GRADED`, `scope_statement=None`.** The cited model does not have this property —
  `z_validator.assess(leg_set: LegSet, …)` takes the leg set **positionally and required** (`:217`), so
  `sees_correlations` cannot be bypassed. **The discipline was copied at the function level and broken at
  the signature level.** Second reachability: a **non-member** build path plus a **multi-offset**
  `declared_K` — an inconsistent pair — grades with `scope_statement=None`. **Third instance of one shape
  in this module** (Part U's window-selected population, Part V's absent coverage flag, now this): the
  thing exists, is correct, and the path that matters does not reach it. One-line fix, not this lane's to
  choose.
  **§Y.2 — Part X both discharged, and the designer improved on what this lane offered.** It **rejected**
  `_DIAGONAL_ONLY_SCOPE` as host, **correctly**: `z_validator:237/276/282` key it on
  `correlation_leg_present`, **orthogonal to block sharing**, so the clause would appear with no corr leg
  and vanish with one — *this lane would have accepted a worse destination than the one built.* Travel on
  refusal verified by execution: `DEGENERATE_FUNCTIONAL` carries a non-`None` scope with `s_proj=None`;
  the three return sites all carry it, computed **before** any guard, and the `require` paths raise rather
  than return, which is correct since a raise is not an outcome to mis-license. Frame withdrawn, dates
  independently verified, ask now a **narrowing**. `W5` tightened: `cause3_corr` forces nothing.
  **§Y.3** suites `136` / `80` / `56+1`, control first.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partZ.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partZ.md)
  - **PART Z — cause-3 Part A at `6f587e59`: VERDICT = READY FOR JOSEPH'S DECISION** on this lane's
  slice. Supersedes Part Y. Block closed and verified by execution on five cases **including a positive
  control**: `build_path` default is `inspect._empty` (**required**, same as `kappa`); omit → `TypeError`;
  `None` → refused; **non-member → refused**; member + `scale_kind='lambda_max'` → **GRADED with scope
  present**. Pinned by **signature inspection**, which is the level this lane named the defect at. Key
  sets identical across `GRADED` and `DEGENERATE_FUNCTIONAL`, scope present on the refusal. Suites
  `136`/`90`/`56+1`.
  ⚠ **§Z.2 — A SHAPE WORTH KEEPING, AND THIS LANE'S OWN PART V REQUIREMENT CREATED IT.** The designer
  found one of its tests had **encoded** the defect: `test_without_a_build_path_the_key_is_still_present`
  asserted a present key with a `None` value — the suppressibility bug as a passing assertion. Its
  generalisation: *a test written for property A can lock in a defect in property B, and the more
  rigorously it enforces A the more firmly it holds B.* **The correct rule was Part V's** *"one identical
  key set across all branches"*, and the test implemented it faithfully. **The specific failure: a
  uniformity requirement can be satisfied by NORMALISING THE DEFECTIVE CASE INTO THE UNIFORM SHAPE
  rather than eliminating it.** So the requirement was under-specified — *"uniform keys"* needed
  *"uniform keys over the configurations that SHOULD EXIST"*, and the second clause does the work.
  **§Z.3 corrects a relayed claim without blocking on it:** `scale`/`scale_kind` are **not** top-level
  return keys — they are nested at `detail['degeneracy']`, so a top-level `.get('scale_kind')` returns
  `None`, indistinguishable from *"no scale declared."* Whether the **support-refusal** branch (which
  returns before the degeneracy classifier) carries them **could not be determined** and is not
  asserted. Residual 1 is the reviewer's. **Method note: this lane's own first read used `.get('scale')`,
  got `None` from a MISSING key, and checked the full key set before asserting.**
- [`RECORD-20260910-z-assessor-declines-proxy-transcription.md`](RECORD-20260910-z-assessor-declines-proxy-transcription.md)
  - **DECLINES to proxy-commit another lane's findings, with reasons — filed outside the `REVIEW`
  numbering because it is not a review.** Agrees the concern is sound (*"a finding list with no
  rejections reads as a filter that never declines"*) and refuses the **verbatim** framing on four
  grounds, the first disqualifying alone: **(1) fidelity cannot be verified** — the words arrive
  **two hops** via the coordinator, so a record whose whole value is fidelity would be authored by the
  one party unable to check it, a fixture that is both claim and evidence. **(2) The coordinator is a
  strictly better custodian and the comparison made skipped itself** — assessor-vs-designer was the
  wrong axis; on first-hand possession and honest fidelity the coordinator wins. **(3) Proxying creates
  the attribution drift it prevents** — text saying *"another lane's words"* inside a commit whose
  metadata says *"mine"*, in a repo where **61 of 109 commits are already misattributed**. **(4) The
  premise is testable and this lane is a counterexample:** 15 commits touching exactly 16 paths, all
  own-review records plus the two hook-required index rows, **no subject artifact touched**, hook green
  every time — so *"read-only"* plausibly means read-only **with respect to the audited artifact**.
  ⚠ **Records a measurement error caught in the act:** the first attempt used a **two-endpoint**
  `origin/main..HEAD` diff, which included main's eight-commit advance and listed `SPEC-20260906` and
  `owners.tsv` as if this lane had touched them — a breach this lane nearly self-reported. Correct
  instrument is `merge-base`. **Counter-offer in §3: a RECEIPT under its own identity** — what was
  relayed, by whom, what was re-measured and what explicitly was not — already live in Part J §J.2,
  Part N §N.5, Part O §O.7 and Part M §M.6.
- [`REVIEW-20260911-temp-file-repair-against-T1-T14.md`](REVIEW-20260911-temp-file-repair-against-T1-T14.md)
  - **VERDICT: 12 of 14 MET, four EXCEEDED; `T9` UNEVIDENCED, `T14` PARTIAL.** Subject `05cf2d00`
  against the yardstick committed at `e92d4a85` **before the work existed**. Authorizes no launch.
  `T1` exceeded because the repair is a **property** not an enumeration -- a leading-dot temp name,
  verified invisible to `glob.glob` for `*`, `*.npz`, `block5d_*.npz`, `*.np[yz]` and to a bash glob.
  `T4` exceeded **and it did its job**: the first attempt broke publication exactly as predicted,
  because `np.savez_compressed` appends `.npz` to a NAME but not to a HANDLE (verified), and the
  completion arm caught it on first run. `T2` exceeded -- real child, `SIGKILL`, fixture precondition
  asserted. **FINDING F1:** `find_incomplete_writes` returns `[]` for a directory it cannot read, so
  "could not look" reads as "clean" (demonstrated by `chmod 000`, and again via a dir-wildcard
  pattern where `check_slab_population` PASSES with a temp present) -- latent, all **18** launcher
  patterns across three glob-bearing flags are fixed-directory, and Joseph's primary guarantee is
  unaffected because it rests on the name. **FINDING F2:** two figures the author has withdrawn
  (`n=74`, `7.7x`) now sit in a production comment; only `8.6389 h` and `1.39x` survive
  re-measurement. Also **corrects my own record**: the `-X` mechanism I published for the `MaxRSS`
  zero was not the one that produced it (a JobName filter alone suffices -- step rows are named
  `batch`), and my reachability flag is **withdrawn** (`10eb1bac` is contained in a remote ref).
- [`REVIEW-20260911-precursor-delta-10eb1bac.md`](REVIEW-20260911-precursor-delta-10eb1bac.md)
  - **Extends the `P1`-`P18` review's coverage from `8111a951` to `10eb1bac`**, which `a51c6503` did
  NOT cover; the `P1`-`P18` verdict is unchanged (all MET, admission still REFUSES at `558.42`
  against `500`). Delta re-measured: 1 commit, 4 files, +218/-3. **FINDING: the new marker at
  `sbatch_uthrow_block_5d.sh:33-35` re-states the reason the same file WITHDRAWS at `:350-353`** --
  the archive is `_sb`, so repointing does not move the archive, it lets an undeclared run write
  INTO it; the two readings license different repairs and the withdrawn one sits 317 lines above its
  own correction. Confirmed independently: the private-meter surface is **1** name in the module and
  **2** in the suite (AST over executable code; four docstring-only names, not three); the P12 lean
  table **by executing all four cases on both sides**; the marker's populations 8 and 36.
  **Regression CLOSED with a matched control:** `77a4af38` = 14 failed / 2895 passed / 6 skipped,
  `10eb1bac` = 14 / **3001** / 6, failure set **identical** (zero either way), `+106` = exactly
  `test_z_precursor`'s tests, zero `z_precursor` failures. **CONTRADICTED:** `MaxRSS` is not empty --
  `-X` hides a step-level field; **206** step rows carry it, peaks 16-48 GiB against 80-110 G
  requested. Maxima table's MAX column confirmed on all three populations (block 12 h = **1.39x**
  its 8.6389 h max); its `n`/`mean` do not reconcile. Bank cleared against a **second** consumer the
  relay did not check, including the pre-J28 all-ones signature.
- [`REVIEW-20260911-precursor-repairs-against-P1-P18.md`](REVIEW-20260911-precursor-repairs-against-P1-P18.md)
  - **VERDICT: every one of `P1`-`P18` is MET; the finding is that the admission accounting REFUSES the
  run.** Subject `lane/z-precursor-repairs-bg-20260911` @ `8111a951` against the yardstick committed at
  `2d61d81f` **before** the work existed. Authorizes no launch; guards **executed**, not only read, in
  an isolated worktree. **Reproduced to the cent:** committed `48 + 252 + 240 + 3 = 543` CPU task-h at
  zero retries, `+ 15.4231` charged = **`558.42` against R5's `500`, headroom `-58.42`**, with arms
  parsed from the real `#SBATCH` lines. `P14` reuse confirmed (`import r5_meter`, its parser and
  validator; durability note only — it rides **private** functions). `P15` **improved on this lane's own
  wording**: the throttle bounds concurrency, not total spend, so for a total cap it is irrelevant.
  `P17` binds at **admission** and touches no running job. `P12` **executed**: `='0'` refuses, `='7'`
  refuses, unset passes — and the Python guard tests key presence while the shell tests non-emptiness,
  disagreeing on `=''` **in the safe direction**, deliberately. `P1`/`P2` exceeded: the decisive arm
  asserts the mask is still **BUILT** but not **WRITTEN**, the exact `3be8c052` distinction, with
  `ast.parse` guarding the harness and a reach precondition — and there are **five** mutation targets,
  not the three relayed. `P13` repairs this lane's own dim-2 finding: the dump arm goes from
  `GUARD=0 mnv_inv=0 member_gate=0` to full parity with both roots mandatory via `:?`. `P18`'s
  inertness control asserts the contract returns **`None`** — *"must do NOTHING, not refuse"* — which
  is what separates a guard from a run-blocker. **(b) confirmed correct:** `x_cv > 0` unchanged, and the
  mask is indexed over the **binning** not the support, because a support-indexed mask is all-ones by
  construction. **Donor confirmed a record:** derived from the glob and labels, with a detector carrying
  its **own positive control**. **⚠ `_atomic_savez`'s temp-name fix is a PRECONDITION for the cap
  remedy** — cutting `--time` (the `252` h block term) raises wall-kill probability, the exact path that
  leaves a temp inside the consumer's glob. **Residual scoping judged RIGHT** — `P11` is satisfied by
  **relocation** (the precursor now runs under a mandatory declared namespace, so it is no longer an
  undeclared run) — **on one condition: a `CITABLE FOR`/`NOT CITABLE FOR` marker and an owner on the
  launcher itself**, since the general launcher's next user will not have read this review.
  **WITHDRAWN HERE: this lane's `r5_meter` timezone finding** — `:551-557` sets `TZ=UTC` in the child,
  so the live path was always on the UTC basis; what I measured was my own hand-rolled capture, and I
  attributed it to the argv after having just written that the environment, not the argv, determines the
  window. **Not verified:** the `14 / 2997 / 6` regression counts (the `+102` **is** verified).
- [`PREREGISTER-20260911-temp-file-repair-acceptance-criteria.md`](PREREGISTER-20260911-temp-file-repair-acceptance-criteria.md)
  - **`T1`-`T14` for the temporary-file repair, fixed BEFORE the implementation existed.** Approves
  nothing. `T1`-`T4` are the four clauses of Joseph's verbatim requirement; `T5`-`T14` are what makes
  them provable. Anchored on measured facts: publication is ALREADY atomic (`os.replace` in the
  product directory) and must stay so; the `except` branch cannot be the mitigation because a
  wall-kill is `SIGKILL`; there are **TWO** selection surfaces (the bare launcher glob and the
  declared-population check at `:294-315`); the consumer population is **nine** launchers over five
  product stems across 4d/5d/fps/corrected, not the precursor's four arms. Heaviest weight on `T4`,
  the successful-completion arm -- but only its **contents** assertion catches a repair that fixes
  selection by breaking publication, which is why `T5` (same-filesystem rename) sits beside it.
- [`PREREGISTER-20260911-precursor-repair-acceptance-criteria.md`](PREREGISTER-20260911-precursor-repair-acceptance-criteria.md)
  - **`P1`-`P18`, the acceptance criteria for precursor repairs (b)-(g) and admission accounting, fixed
  BEFORE the implementation existed** so the later verdict is checkable rather than fitted. Approves
  nothing; no repair existed at authorship. **Baseline verified rather than accepted:** the
  `--no-verify` disclosure holds — `da1da9f4` is reachable from **no ref** and has a tree
  **byte-identical** to `77a4af38` (`1447639b…`), same parent, same subject; the landed set is exactly
  the 4 minimal paths; *"code-only is not self-consistent"* is confirmed at the mechanism
  (`SANCTIONED` carries `probe-z-projected-stability-20260910.py` and
  `test_every_sanctioned_exclusion_still_exists` asserts presence); and **365 tests re-run OK**
  (90/57/58/136/24). **⚠ OPERATIONAL FINDING: `origin/main` is still `6f24fb00` — the landing is NOT
  PUSHED**, `main` is 1 ahead / 0 behind after an explicit fetch, so no other session or reviewer sees
  it. **Criteria:** reach-per-mutation and distinguishable-from-infrastructure-refusal (`P1`-`P4`);
  identity-and-coverage over the **enumerated declared set**, both directions, all four arms, a glob is
  not a population, and a non-empty population by construction (`P5`-`P9`); non-emptiness **refuses**
  with absent distinguished from empty, writer/reader agreement proven on the **UNDECLARED** path,
  `mii/` as a refusal not resting on `mr_declared()`, and `sys.path[0]` named per entrypoint across the
  four competing mechanisms (`P10`-`P13`); admission accounting that **calls** `r5_meter` and bounds
  charged spend **plus maximum remaining exposure including queued and retries**, on an explicit-UTC
  basis with a test that fails if the naive basis returns, **preserving R5's running-at-the-stop rule so
  the cap binds at ADMISSION** (`P14`-`P17`); and silent positive controls on the same call path
  (`P18`). **Donor question flagged:** `z_assembly.py` has no donor binding at all, so a donor appearing
  in code without a committed decision is a decision taken by implementation, and this lane will treat
  that as a finding while refusing to answer the question itself.
- [`READINESS-20260911-precursor-launch-six-dimensions.md`](READINESS-20260911-precursor-launch-six-dimensions.md)
  - **VERDICT: NOT READY.** Independent end-to-end launch-readiness check of the Z unified-throw
  precursor on Joseph's six dimensions. **Authorizes no launch**; `R4` suspended, Gate 2 FAIL, nothing
  launched, cluster read-only. **CERTIFIED (1):** all four launchers exist with exactly the pinned
  specs — **70 CPU tasks, 0 GPU**, arrays read from the scripts never from a `sacct` bracket — with two
  corrections: the **dump arm runs a different producer** (`unified_throw.py --dump`), and of 24
  `sbatch_uthrow*` siblings the near-name `run_5d.sh` declares `0-19%10`/`12 h` against the fast arm's
  `0-39%40`/`6 h`, a budget fact (all siblings are cpu, so no resource-class flip). **BLOCK (4):**
  **(2)** `sbatch_uthrow_dump_5d.sh:12-14` hardcodes an absolute `REPO`, `cd`s there and runs a bare
  `python3`, so `sys.path[0]` is the pscratch tree regardless of `MNV_CODE_ROOT` — **the OI-136 shape
  (the 211-behind / 3 h 08 m A100 case) achieved by `cd` instead of a Python insert, hence invisible to
  the sweep that repaired the inserts** — and it is the only arm with `GUARD=0 mnv_inv=0
  mr_require_valid_offset=0`; it also has **0** `DATA_ROOT` references against 5/5/5, breaking the
  invariant `unified_throw_cov.py:63-68` relies on. **(3)** *No* namespace is fresh (`block_slabs_5d` 8,
  `block_slabs_5d_sb` **36**, `uthrow_slabs_5d_sb` 40, `uthrow_slabs_5d` 160, `bank_uthrow_5d` **374**,
  all July or earlier), and on the **undeclared** path the block leg writes `block_slabs_5d` (`:320`)
  while the combine reads `_sb` **unconditionally** (`:333`) — so the precursor's combine would consume
  **36 stale July products** and never see its own 21, and because the glob matches it **does not fail
  closed**; the launcher's own `:321-331` says members die loudly and *"an UNDECLARED run reads exactly
  what it read before"*, with canonicity **still open**. `mii/` is safe **only if**
  `MNV_EST_SEED_OFFSET` is unset — conditional, resting on the `mr_declared()` conflation, and should be
  a refusal. **(4)** `--expected-ids` occurs **zero** times in all four arms; only `--expected-throws
  0-159` is asserted, while `--block-slabs` is a **bare glob with no expected count**, so a short block
  arm combines silently. **(6)** RUNNING **is** charged — proven by fixture (3.0 h = 1.0 COMPLETED +
  2.0 RUNNING; PENDING skipped), refuting the feared mechanism — but the meter charges elapsed-so-far,
  so up to **240 CPU task-h** is committed-but-unmetered in flight (R5's own design), and **the cap
  arithmetic does not close: measured 58.84 + unmeasured `--time` ceilings 51 = 109.84 against a 100
  cap**, 48 h of it in the dump arm. **CANNOT CERTIFY (5):** there is **no separate receipt** to order —
  provenance is in-product `TParameter`s (`:550-579`) and `_atomic_savez`, and no `os._exit` exists, so
  the property holds **vacuously**, not by enforcement. **The OPEN item is CONFIRMED by an independent
  method:** 4 distinct blobs of `unified_throw_cov.py` across every ref, **zero** mask-write hits in all
  four, positive control **3** on `eavailW_covariance.py`; `:368-372` computes `rep = x_cv > 0` and
  discards it — and because support is **strictly positive**, a pinned-zero bin is excluded from `rep`,
  so Joseph's *"a pinned-zero bin is not a null operand"* **names this line**.
- [`ASSESSMENT-20260911-endpoint-B-design-nine-claims.md`](ASSESSMENT-20260911-endpoint-B-design-nine-claims.md)
  - **Pre-implementation assessment of `DESIGN-20260911-endpoint-B-generator-comparison-test.md`
  (`8a42f8ea`), designer recused; nine load-bearing claims.** Authorizes nothing; endpoint B stays
  **DEFERRED NOT PASSED**, Gate 2 FAIL, `cause3_corr` WITHHELD, `R4` suspended. **CONFIRMED (6):**
  the truth samples are all present on pscratch (the size mismatches are decimal MB vs MiB — GENIE
  `999.5`/`997.6` MB, 8 nuwro dirs, GiBUU 2020 MiB), so **no fresh generator production is needed**;
  the existing instrument is aimed at the **opposite end of the axis** (`eavail_generator_significance.py:2`
  *"high-E_avail excess"*, `:106` `>= 0.8` *"DIS tail"*, `:118` `chi2/ndf(DIS>=0.8)`) from the
  manuscript's claim (`sec_3d.tex:268` **low**-available-energy excess); the **model swap is real**,
  and the full-range column the requester had not verified **derives exactly** from `sec_3d.tex:194-197`
  (`12.01/18.18/24.03/27.92`); **nesting** holds and was already recorded (`README.md:201` *"mec==0 for
  all 1.48M CC events"*, exact `total CC=1484896`); the **target asymmetry** is documented
  (`run_nuwro.sh:32-34` `nucleus_p=6 nucleus_n=6` vs `README.md:32` CH `/13`) and per-nucleon division
  cannot absorb a component absent from one target; and **Tune v1 is the prior with no assembly term
  covering it** (`build_fps_prior_nuwro_5d.py:11` denominator; `z_assembly.py:4` five terms, zero
  prior/unfold matches) — a band reweights a fixed estimator, a prior change re-runs OmniFold.
  **THREE BLOCKS: (1)** *"what is missing is an ND histogrammer"* is overstated —
  `gen_to_xsec_eavailW.py` exists, takes an **arbitrary** `--gst` (`:67`) with a generator-agnostic
  reader (`:68`), and declares binning *"identical to the 5D OmniFold W axis"*, with NuWro/GiBUU
  siblings; the MEC sample is therefore already histogrammable and the gap must be **re-scoped**
  (limits stated: existence verified, execution and Tune v1 coverage **not**). **(2)** The four
  "implied catch fractions" `43.4/37.6/38.7/40.4` reproduce **exactly** from a single assumed **data**
  catch fraction `44.96%` — i.e. from the **withdrawn** 43–46% band itself — so they inherit the
  withdrawal, and even granted they show **no inconsistency**; §2's table does **not** depend on them
  and **stands**, so the flagged check on the producing scripts has no premise. **(3)** Multiplicity:
  `N=120` and `1.0870` reproduce, but **independence is not the worst case** — the union bound gives
  `0.986`, more conservative by `0.101σ`, so *"at worst 1.09"* is not a bound. Also **reclassified:**
  the *"one-sided"* label at `:111-113` is a **comment-only** defect — `isf(p/2)` is the conventional
  HEP equivalent, so the printed number is right and "fixing" it would break a correct value.
- [`CHECK-20260911-three-relayed-readings-gate2-mii-and-cost.md`](CHECK-20260911-three-relayed-readings-gate2-mii-and-cost.md)
  - **An independent check of three relayed readings plus one addendum, requested as preparation for a
  compute authorization. READY on reading 1; BLOCK on reading 2; BLOCK on two of reading 3's
  measurements with its conclusion surviving; READY on the addendum.** No compute launched; cluster
  read-only. **(1)** The Gate-2/adoption conditional is **not absent** — `REVIEW-CONTRACT-20260822:636`
  (§7.0.6) and `DECISION-20260824-f6b:65` both state it, but both bind *"the rehearsal's products"* and
  so do not reach Z; reporting unresolved scope is right, and the withdrawal must not be over-read,
  because §7.0.6's *"no further member is authorized"* is **not** product-scoped. **(2) BLOCK:** `R4`
  (`DECISION-20260902:109-116`) **suspends the cause-3 seed scan by name** and is omitted — its two
  prerequisites are measured unmet (the VOI note is committed only on `lane/cause3-voi-20260906`,
  unreachable from `main`; no `D-C3-RUN` exists), so the binding constraint is an **authorization**, not
  the M(ii) gate; and *"UNGRADED for `7ac0edec`"* is refuted by *"can never PASS"*
  (`DECISION-20260830-accept-forward-only:42`), by `RECORD-20260901:5`'s bar on *"a claim that Gate 2 can
  now pass"*, and by three post-08-30 decisions stating *"Gate 2 remains FAIL"* unscoped. **(3)**
  CONFIRMED: quarantine **517**; the live member is a different family (**143** markers,
  `57753239`…`57790088`, **0** shared job ids with the quarantined `57527866`…`57587242`); `boot 200`,
  `split 48`; `banksweep5d` is **CPU** (`--constraint=cpu`, n=**175**, **30.5675** task-h, **0** rows
  naming `gres/gpu`); both shared blocks byte-identical. **REFUTED:** `universe_sweep_bkgaware` is
  **188**, not `0` (nor the earlier `207`) — corroborated by `PROVENANCE-20260822:230`'s `n_universes`
  **188**; `universe_stage2_5d_bkgaware` is **4**, not `0`; both were `0` only in the **local** checkout.
  **Spend is on the wrong timezone basis:** `r5_meter.py:_sacct_argv()` emits a naive `--starttime` that
  `sacct` reads in the host TZ (PDT), starting the window 7 h late — `14.937222` (naive) vs
  **`15.423056`** (UTC), `+62` attempts, `+0.485833` task-h, isolated by bit-identical 3x replication per
  basis and strict-subset containment; operative headroom **CPU `≤ 484.58`**. CPU-binding **survives**. **The same boundary explains
  `FINDING-20260910`:** on the CLOSED window to the receipt's own instant, `TZ=local` reproduces
  `1826 / 14.489722` and `TZ=UTC` reproduces `1888 / 14.975556` — **both** historical figures,
  differing in nothing but the timezone, so that finding's attempt-identity diagnosis is **mistaken**
  and this lane's own retraction of that hypothesis is **WITHDRAWN** (§7 item 1 banner). Its four
  original controls all ran on **one side** of the boundary — a control over a population that cannot
  exhibit the defect, `BEN-032` inside a spend meter.
  **(4)** The addendum's diff and dates confirm, and **both** builders are implicated pre-`07c18aee`
  (`bootstrap_nd.py:28` `seed=a.seed`; `seedscan_split.py:54` `seed=args.split_seed`); job `55912230`
  did **not** write the blocks (it started ~19 h after their mtime) — the producer was an **interactive**
  job, and `PROVENANCE-20260822` pins no producing revision, so the caveat is **unresolvable in-tree**.
  **§7 records six method faults in this check, including a false mechanism withdrawn before it left the
  lane.** **Moves no gate, grades nothing, adopts nothing, authorizes no compute.**
- [`ASSESSMENT-20260911-scoped-letter-readiness.md`](ASSESSMENT-20260911-scoped-letter-readiness.md)
  - **VERDICT: READY as a manuscript, NOT READY for external review, on ONE evidence fault.** Measured at
  `origin/main = 6f24fb00`, note repo `d0c3768e`; **no compute launched**, builds local in a disposable
  worktree. **(1) `build_all.sh` PASSES**, exit `0` — note 90pp / primer 5pp / paper 3pp, **all three
  confirmed written by the run**, `SELF-TEST` and `RESULT` PASS, `FAIL` count 0, containment `note 10/10`
  vs `paper 0/10`; toolchain checked first, **no biber/PAR fault**. **(2) The scope claim HOLDS and is
  stronger than quoted** — `paper_body.tex:145-148` adds *"no superseded or historical covariance is
  used here"*; exhaustive counts give `p-value`/`chi^{2}`/`chiCombined`/`exclusion`/`Nsigma`/`gbdtFive`
  all **0**, and *"No significance is assigned"* appears **twice** in captions. **(3) No quarantined
  value reaches the Letter, and the 3D descriptors are absent from it entirely** — `main_paper.tex`
  inputs only `values` + `paper_body`, so `sec_3d.tex` is out of closure; the Letter's **8** value macros
  carry no quarantine marker, agreeing with the build's independent containment. **(4) The standalone
  note repo is IN SYNC** — 25/25 `.tex`/`.bib` byte-identical, 0 of 89 files absent, and the two heads
  are **seven seconds apart in one synchronisation operation**; ⚠ **a date-only read would have called it
  two weeks stale.**
  ⚠ **(5a) THE BLOCKER — Ruling 1's record is unreachable from `main`.** The Letter's defensibility rests
  on a deliberate exclusion whose authority is `DECISION-20260910-joseph-b-deferred-…`, committed only on
  an unmerged lane and therefore in **neither** repository a referee is given. Manuscript correct,
  authority unreachable — an **EVIDENCE** fault, closed by a merge this lane cannot authorize. **(5b)**
  *"the corrected contract"* at `sec_3d.tex:252` is a definite description a referee cannot resolve.
  **(5c)** 18 `\dead{}` struck values in the note: correctly contained and honest, but expect the
  question. **Method note: the first grep of the build log returned nothing for `PASS`, `FAIL` and
  `written by this run` alike** — *Non-ISO extended-ASCII*, so grep went binary-silent; the **positive
  control** caught it.
- [`RECORD-20260910-z-assessor-receipt-of-relayed-findings.md`](RECORD-20260910-z-assessor-receipt-of-relayed-findings.md)
  - **RECEIPT, not a transcription** — this lane's own testimony about what was relayed to it, at two
  hops, with **no fidelity claim** on any item. Companion to the decline record. **§4 is the point:
  the NEGATIVE SPACE made discoverable without anyone signing for words they cannot check** — clause
  (d)'s not-sufficiency and its **single unreplicated read** (a scope limit on a finding favourable to
  this lane, and those are lost first); `F3`'s `349 / 4 / 147` split; `A-7`'s `B = 7.107%` against a
  realized null median of `36.95%`; §4.4-vs-§4.4b's two incompatible boundary specifications; the
  sharing fraction **flipping the error's sign** (`5.17` → `1.78` → `0.81`); and **four candidates
  raised and killed**, one of which is an attack on this lane's own C6/C7 asymmetry that failed. Each
  row carries why this lane did not verify it. **None may be cited as this lane's finding.**
  ⚠ **§1 measures the attribution hazard instead of arguing it.** This lane wrongly said the current
  coordinator *"already commits"*, citing `a11d6cdd` — which was the PREVIOUS coordinator's. Measured
  against this lane's `a550796d`: **author, committer, `Co-Authored-By` and even `Checks: 12 passed`
  are IDENTICAL.** No git field distinguishes the two sessions, and the trailer names a **model**, not
  a session. So the error was structurally caused — and **had this lane proxy-committed the reviewer's
  findings, nothing in git would ever have separated them from its own.**
  **§3 accepts three corrections against this lane's own figures:** the read-only counterexample is
  **16 commits / 18 paths**, not 15/16 (stale by one commit — **more** favourable than claimed, and
  zero subject artifacts either way); **`AGENTS.md:120`** supplies the textual support this lane had
  not cited — *"never freeze an auditor's silent edit into a receipt"*, whose named harm an openly
  indexed review document is the opposite of; and `a11d6cdd`'s misattribution. **§5: this preserves
  that the items arrived, NOT the reasoning — option 2 to Joseph remains the fix.**
- [`PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md`](PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md)
  - **PROPOSAL ONLY — adopts nothing, grades nothing, declares no threshold.** Maps the
  publication's intended covariance consumers to three candidate `(cause 3, Z)` criteria under `RZ`:
  **C-1** direct sensitivity of the quoted significance, **C-2** a conditioning diagnostic, **C-3**
  projected-bin sensitivity via the existing `s_proj`. **Projection and inversion policy are
  unresolved** — the projection map has three implementations with none designated, and the
  `pinv` cutoff, tail and `ndf` conventions are undeclared. Read its `CITABLE FOR` / `NOT CITABLE
  FOR` header before quoting any part of it.
- [`SPEC-20260906-complete-scalar5d-successor-Z.md`](SPEC-20260906-complete-scalar5d-successor-Z.md)
  - **rev. 21. SPECIFICATION ONLY; constructs, runs, grades and adopts nothing.** The five deliverables
  `RZ(v)` authorizes, for one named Z: the **scientific contract** (§1 — artifact identities bound by
  path plus digest; the imported constants, now including `adopt_unified_5d.VERT_BANDS` and
  `uq_math.F7_FLOOR_MULTIPLE`; **§1.3a's explicit inflation algebra** `C_Z = D_Z(Σ_V C_b)D_Z + Σ_R + Σ_A
  + C_stat + C_ML` with `D_Z`'s operands, zero-denominator handling and both centering variants; §1.3b's
  identity set, **four of whose gates do not exist**; the receipt schema; and what does not exist yet),
  the **seven cause dispositions** (§2, none inherited), **terminal criteria** (§3, per-cell completion
  *and* failure, fifteen reject-Z conditions, a bidirectional test contract), the **dependency analysis**
  (§4, twenty-two candidates each answered separately for `necessary` / `applicable` / `reusable-now`,
  with `D-Y-CONSTRUCT` and `D-C3-VOI`+`D-C3-RUN` flagged and **neither found to be a Z prerequisite**),
  and a **costed execution proposal** (§5 — `73.0` GPU / `≤118.0` CPU task-hours for one build against
  `R5`'s `500`/`500`, from the ratified `70`/`113` seven-arm anchor, with the meter gap named).
  **§6 carries FOUR RULINGS Joseph took on 2026-09-06** on an independent contract review's
  recommendations: `(cause 5, Z)` may be terminally disposed **`INAPPLICABLE — disposed by decision`**
  after the complete trace and falsifier check, **adding no token** and on cause 2's by-decision
  precedent (§6.1); `(cause 1, Z)` closes on **measure-and-disclose irrespective of magnitude**, once
  independently verified, **without inventing ± endpoints for the non-pair bands** (§6.2); `(cause 3, Z)`'s
  `M(ii)` is the **joint-baseline** quantity with the narrow fixed-draw scan **diagnostic unless
  substitution is separately ruled**, the 46/50-member family **not assumed**, and three outcome classes
  predeclared (§6.3); and Z uses a **scale-relative fixed-seed null bound fixed before production**
  (§6.4). §6.5 withdraws rev. 1's multi-draw cause-4 proposal. **`CRITERIA` §0's vocabulary is NOT
  extended** — `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` stands, and rev. 1's contrary
  proposal is recorded as a miss. **Corrections carried in place:** S's `publication_gate_rejects_this`
  is **`false`** with an 11-gate PASS, so the *"adopter refuses it outright"* ground is stale — the
  durable ground is that S is a block-sum object with **no unified-throw inflation** and **cannot donate
  `D_Z`** (§1.4); `SCOREBOARD` §2b's *"`M(ii)` cannot be configured"* is superseded by `3dd5e66e` (§2.3);
  and, **withdrawn from rev. 1**, the bidirectional projection guard is **not missing** — both projectors
  guard both directions and differ **deliberately** in fail-closed-ness (§2.6a), reuse of
  `C_stat`/`C_ML` is **not** evidence of incompleteness (§2.6b), and the replay-doubling and *"≈4.5×"*
  cost claims are withdrawn (§5.3, §5.4). Opens no `SCOREBOARD` cell, moves no count, preserves `R5`
  exactly, does not widen Y, does not promote S. `BEN-381` disqualifies the drafting lane from grading
  the legs it defines, and from grading under the four rulings — **but not from designing what it
  specifies**, a rev. 2 over-application withdrawn in rev. 3.
  **REVIEW ROUND 2 (rev. 3) closed one hole rev. 2 itself opened and corrected one of its own
  corrections.** §1.3b's four inflation gates were **jointly satisfiable by an uninflated object** —
  `g ≡ 1` passes the closure identity, `g ≥ 1`, the zero-denominator rule and PSD — so a **fifth gate**
  requires the validator to **independently reconstruct `g^c` from `diag(C_unified)`,
  `diag(C_blocksum)` and `hJointMeanShift`, per variant**, with the matching `T`-leg mutation. New
  **§3.6** converts the two ruled-but-incomplete terminal criteria into completion schemas: the null's
  normalizer, units, `ε` derivation and presence rule; and cause 3's member definition, statistic,
  two-leg normalization, the `S/U ≤ sqrt(2δ+δ²)` boundary derivation applied to **Z's own** printed
  precision, and the three classes mapped onto the six branches — **reopening no ruling**. And **`R5`
  meters `ElapsedRaw`, actual elapsed, not requested walltime**, so rev. 2's *"the metered cost is the
  wall request"* is false: §5.2 now separates **expected spend** (`55.70` GPU / `86.53` CPU) from a
  **reservation bound** (`73.0` / `≤118.0`), and both are labelled a **PRICED SUBTOTAL** with four
  required rows unpriced. Also narrowed: the J28 line to **the two assemblies only** (its rescale is
  J28-only, its throw combine **is arm 7**); the cause-4 jitter counterfactual to a **second** unfold at
  `seed + 7`, distinct from `--null`'s same-seed one; `54.90`/`86.53` to a **historical prior that
  understates a Z member**; and S to holding the **uninflated** vertical components while lacking `D_Z`
  and the inflated term.
  **REVIEW ROUND 3 (rev. 4) fixes the acceptance mathematics and the test contract.** New **§3.6d**:
  the predeclared `S/U ≤ sqrt(2δ+δ²)` threshold **does not transfer** to either new criterion, because it
  assumes an **omitted independent contribution added in quadrature** and neither a difference of two CV
  vectors nor variation among assembled covariances satisfies that model; `δ` transfers, the quadrature
  map does not, and for a **directly measured change in `U`** the comparison is `|U'−U|/U ≤ δ`. The
  ordering rule is inverted back: **statistic first, boundary second**. A hardware reproducibility floor
  is demoted to a feasibility constraint — it measures **achievable** repeatability, not **acceptable**
  error. §3.6b's free choice between assembled-covariance and cross-section-vector spread is **withdrawn**:
  §6.3 fixed the assembled covariance as the subject, and vector spread is the **substitution** it
  reserved. §3.6c's *"proposes no criterion change"* is **too categorical and withdrawn** — a boundary
  form differing from the predeclared rule is itself a carve-out question, now listed in **§6.6**. In the
  test contract, the `g ≡ 1` and **dropped-shift** mutations are **separated**: a reuse-faulty validator
  **rejects `g ≡ 1` on both variants**, so a distinct `g^cv ← g^mean` mutation is required on operands
  where the two must differ (`v_blk=1`, `v_uni=4`, `mean_shift=1` → `g^mean=2`, `g^cv=√5`), and the
  `g ≡ 1` fixture must make `g ≡ 1` **wrong**, since it is legitimate wherever `v_uni ≤ v_blk`. Cost
  language stops asserting bounds: historical figures are **priors from a different subject**, not lower
  bounds; a time limit **bounds an attempt, not a completion**, so the combine and assembly reservations
  are **PROPOSED, UNVERIFIED**; and the omitted rows are enumerated **per subtotal** — five for the spend
  estimate, three for the proposed reservation, two campaign-level items in neither.
  **REVIEW ROUND 4 (rev. 5) found no new assembly-algebra defect and closed two residual defects, both
  the drafting lane's.** Three **withdrawn cost claims had survived in operative text** and are removed:
  the assembly row's *"`< 4.0` is all it licenses"* (a request that was never exceeded measures nothing,
  and it covered four operations of which only two are Z's), §5.4's *"a Z member costs more"* and the
  prior *"understates"* it (a prior measured on a **different subject** supports **no direction**), and
  §7's *"the subtotal is a floor"* with its stale four-row count. And **§3.6d overstated the narrow
  scan**: it called `C_seed` an independent variance contribution *"being added to the budget"*, which
  **`PREDECLARE-20260901-cause3-mii` §5 expressly forbids** — *"It does not add `C_seed` to the
  uncertainty budget"* — and which contradicted this document's own §1.3a. Quadrature is now stated as
  the **conditional model that motivated** those thresholds, **never demonstrated even where it was
  used**. Two recommendations adopted: **direct relative change `|U'−U|/U ≤ δ` is the DEFAULT** for
  §6.3's assembled-covariance subject, with the burden of demonstration on any proposal to use
  quadrature; and §6.6's boundary-form item now records **how the decision must be put** — the statistic,
  denominator, precision target and boundary approved **together**, never a formula detached from them,
  so **that item is not ready to decide today**.
  **SPECIFICATION COMPLETION (rev. 7) — no review finding; the three declared gaps are closed and
  everything new is PROPOSED.** New **§3.7** completes both terminal criteria. For the **fixed-seed
  null**: the normalizer is `‖x_cv2 − x_cv‖ / ‖x_cv‖`, with `sqrt(Tr C_Z)` rejected (it divides a
  central-value difference by an uncertainty scale, and it is the denominator behind the campaign's
  quoted `1.31e-12`) and the per-bin maximum rejected as a gate but retained as a diagnostic;
  `ε = n_iters · n_rep · float64.eps = 1.1873e-11`, a **formula with imported operands** rather than a
  constant, binding over three sensitivity channels by seven orders in the one unmeasured quantity; and
  a new reject condition **`11b`**, because the throw writer **does not persist `x_cv`** so the ratio
  is otherwise unauditable — `hXSecND_flat` in the production ROOT closes it. For **`(cause 3, Z)`**:
  the member is **MEASURED, not designed** — one shared `MNV_EST_SEED_OFFSET` across exactly **seven**
  production launchers, with an **eighth that refuses it**, so no arm can be reused and the implemented
  family is the **diagonal** `(42+k, 1000+k)` rather than a grid; the population is the **finite declared
  offset set**, which makes a sample SD inadmissible and the **maximum** the matching statistic; and the
  boundaries are `s_agg ≤ δ_agg` and `s_med ≤ δ_med`. **Under the direct model those are `0.0861%` and
  `0.0374%` — `48×` and `73×` tighter than the narrow scan's `4.15%`/`2.74%`**, which is arithmetic, not
  a preference. The **precision target is a DECLARATION nobody can measure**: both 5D candidate macros
  are defined and **never printed** (covering search with a positive control) and their values are J's,
  quarantined. **Affordability: `N = 4`–`5` total members inside `R5`, at `86.5%` of the CPU ceiling,
  against `5.1×`–`8.7×` for the historical 46/50 design — no affordable middle.** New **§5.8** recasts
  the cost census as **production / artifact replay / conditional / contingency** and sizes two of three
  unpriced build rows from local timings at the real `10,694` dimension (`eigvalsh` `113` s, peak
  `1.83` GB) — **minutes and gigabytes, not hours and terabytes**, with memory the binding constraint.
  New **§5.9** relays a read-only operational evidence packet, every item marked RELAYED or RE-VERIFIED
  HERE: a genuine meter receipt parses live `sacct` and is deliberately **uncommitted**; the assemblies
  gain a **measured upper bound** `≤ 0.5231` CPU task-h; a **7-day outage inside the `R5` window** cuts
  the usable schedule to **`16 d 15 h` in two blocks**; and `sacct`'s 30-day span limit makes the meter
  stop working `2 d 14 h` after the `R5` stop. **⚠ TWO STATEMENTS IN REV. 1–6 WERE FALSE and are
  corrected in place (§5.9a):** `combined_source`'s digest **is** recorded in the tree — in **G's own
  build receipt**, `9f7b2f55…` at `2026-08-12T05:46:19Z`, **four days before S read the file** — so
  §1.1's *"no digest anywhere in the tree"* and §4 row 5's *"using S's digest as G's is the
  substitution `PM-2` exists to prevent"* both fall. **An absence asserted without a covering search**,
  about a file in G's own directory in this checkout. What survives is a timing qualification and a new
  §1.5 requirement: stamp `path + sha256 + size + mtime_ns + inode + device` **at open time**. New
  **§6.7** puts **five decisions** to Joseph as packets — the cause-3 acceptance packet (`D1`), the
  per-bin precision target (`D2`), the design `N`/offsets/diagonal-or-grid (`D3`), the null packet
  (`D4`), and the `12.59` CPU task-h gap between the meter's deduplicated reading and `R5` §3's
  *"retried tasks count in full"* (`D5`) — **and takes none of them.** **The contract is NOT ready for
  an implementation authorization**, and §6.7 says what would make it ready.
  **SECOND OPERATIONAL PACKET (rev. 8) — one blocker released, one prerequisite found unreadable.**
  New **§5.9c**: the k=0 round-2 campaign spans **`37.5` h** end to end (376 tasks,
  `2026-08-30T21:29:20` → `2026-09-01T10:58:02`), and its `54.90` GPU task-hours reproduce §5.2's figure
  **exactly by a different route**. So `4`–`5` rounds fit inside **either** block of the split window
  without straddling the outage, and §6.7's readiness item 5 — rev. 7's *"the one constraint no decision
  can relax"* — is **withdrawn to a caveat**: `37.5` h is **one realization at one week's queue depth**,
  already inclusive of that week's queue wait, and a campaign would run into the pre-outage rush. The
  cause-4 second CV unfold gains a **measured upper bound `≤ 0.5764` CPU task-h** — `--null` runs inside
  `uthrow5d_combF` on `shared_milan_ss11`, **CPU and never GPU**, which is the specific thing rev. 2 got
  wrong; the identity matters, because that job is **arm 7**, not the still-unmeasured `budget5d`
  statistical+ML combine. `D5`'s figure is now dated: `12.5903` at `08:59Z`, `12.606389` at `09:20Z`,
  `≈0.05`–`0.07`/day. **⚠ AND `PM-4` CANNOT BE DISCHARGED AS WRITTEN.** New **§1.3d**: G's committed key
  inventory is **13 keys** and holds **neither `hRowIndex5D` nor `hXSecND_flat`** (re-verified here in
  `receipt_candidate_stamps_5d.json`), so *"read from G"* has no referent — and rev. 2–7's flagged
  inference that *"G is 2026-08-12, so it plausibly carries `hRowIndex5D`"* is **refuted**, the 49-key
  object being the 2026-08-16 rebuild in **S's** lineage. **The invariant stands and its route changes**:
  both digests are reconstructible from G's production-CV input, which is the same object reject
  condition **`11b`** already names, and which **G's own hash receipt does not bind** — so `PM-4` and
  `11b` fail together on one missing identity (new §7 item 17). The preflight evidence is now **committed
  off-branch** at `21b3d567`/`cd41ff41` on `lane/pm-root-inspection-20260906`, with its receipts named
  `r5-meter-receipt-INCOMPLETE-*`; `docs/orchestration/state/r5-meter-receipt.json` still does not exist
  and admission stays shut.
  **CITATION AND BLAST RADIUS (rev. 9) — no review finding.** The evidence citation moves from
  `cd41ff41` to **`1422569c`**, which supersedes it: `cd41ff41`'s `README.md` says *"four earlier jobs"*
  in the waker lineage where there are **five, six with the live one**, and states the array negative
  result **without its covering-search boundary** (three **discontiguous** queries, `≈28` days, absences
  of `22` and `3`, because `sacct` selects on runtime overlap). **Verified here:** the diff is
  `README.md` + `DIGESTS.txt` only, and **only `README.md`'s digest moves** — both receipts, all four
  raw dumps and `R5-PREFLIGHT-EVIDENCE.md` are byte-identical, so every digest-bound citation is
  unaffected. Chain, child to parent: `1422569c → cd41ff41 → 21b3d567 → 641c6812`; **rev. 7 is their
  root and none is an ancestor of this tip, and the two lanes stay separate** because that branch
  carries an authorization Joseph has not yet ruled on. New **§5.6a** names **the opening act**, because
  §4 row 3 makes the meter receipt Z's first prerequisite and *"a query plus a commit"* understates the
  consequence: **running** the meter arms nothing; an untracked or post-commit-edited receipt is still
  refused; **committing** one to `docs/orchestration/state/r5-meter-receipt.json` removes a
  **QUEUE-WIDE** refusal, since `committed_r5_receipt(queue)` takes only the queue and
  `r5_refusal_reason` consults it for **every** compute item. Three things bound the radius and none
  makes the act small: it **expires** after `R5_MAX_AGE = 24 h`; other refusals survive it; and the
  known `--kind read-only` bypass is recorded as **refused**. So the integration lane's meter repair
  **landing does not open the gate** — nobody should open it by running the repaired tool once to see
  whether it works. §5.6's *"shut by choice"* is corrected: it is shut by **Joseph's own instruction**
  — *"do not present it as valid admission evidence"* — and committing it to the gate's path **is** that
  presentation. §7 item 17 is sharpened: the ROOT **inspection is authorized** with quoted limits, while
  the **one-off accounting exception** that would let it be admitted is a proposal Joseph **expressly
  reserved to himself** and has not ruled on — authorized and unadmittable, which is not unauthorized.
  **⚠ THE OFF-BRANCH EVIDENCE IS COMMITTED BUT UNPUSHED (rev. 10), which is a defect in §5.9's
  CITATIONS and not in the evidence.** Measured with a positive control, because a zero-row query is
  not a measurement on its own: `git ls-remote origin 'refs/heads/lane/*'` returns **exactly two** rows
  — `lane/cause3-voi-20260906` and `lane/y-cause7-spec-and-scope` — and
  `lane/pm-root-inspection-20260906` is **absent**, while the same command resolves the control. So
  `21b3d567`, `cd41ff41`, `1422569c` and `d7dd2f1c` resolve **in one local repository only**, and rev. 8
  and rev. 9's *"COMMITTED"* was read as *"available"*: **committed and pushed are different branch
  properties.** §5.9's **RELAYED** items are therefore attested but **not independently fetchable**;
  the **RE-VERIFIED HERE** items are unaffected, their evidence being in this checkout. New §7 item 18
  records what would resolve it — **a push by that branch's owner, which is not this lane's act and
  should not precede Joseph's ruling on §4**, since it would publish an undecided accounting exception.
  The citation deliberately **stays at `1422569c`** although the tip is now `d7dd2f1c`: that diff
  touches **only** the authorization record, the evidence directory is untouched, and **all seven
  clauses this document quotes are byte-identical in both revisions** (substring-checked in each).
  **⚠ THE OPENING ACT IS PRESCRIBED, NOT MERELY AVAILABLE (rev. 11), and the measurement is this lane's
  own.** Rev. 9's *"nobody should perform it by running the repaired tool once to see whether it works"*
  framed the hazard as carelessness; **the documented procedure performs the first half of it.**
  `R5-METER.md:12-16` is a copy-pasteable block — introduced as *"atomically refresh the default
  receipt"* — whose `--write` target **is the admission gate's exact path**,
  `docs/orchestration/state/r5-meter-receipt.json`. Measured here: that path is **not gitignored**
  (`git check-ignore` exits `1`), **150** tracked `.json` files already sit in the same directory, and
  the runbook's closing disclaimer covers **authorization** while saying nothing about **admission** —
  which is what that path controls. **So the sequence that arms the queue is: follow the runbook, then
  `git add`**, and neither step looks like a decision; a `git add -A` or a routine "commit the state
  directory" completes it. New §7 item 19 states the requirement without choosing between its two
  remedies — the runbook's default target moves off the gate path, or the gate path stops being
  tracked-by-default — because **that is the meter owner's call, not this lane's.**
  **THE OFF-BRANCH CITATION STOPS CHASING A MOVING TIP (rev. 12).** §5.9 had described that branch by
  **counting** its commits, and the count went stale twice in three revisions — rev. 10 said *"six"* and
  named four; rev. 11 enumerated six; the tip was **seven** before rev. 12 was written. **A count of
  someone else's actively advancing branch is a field this document cannot keep true.** The pin stays at
  `1422569c` and is now stated as an **invariant with the command that tests it**: the evidence
  directory unchanged, and the seven quoted clauses of the authorization record present. **Run at the
  two later tips this lane has checked — `d7dd2f1c` and `6b439466` — all seven are present in both and
  the evidence directory is untouched in both**, each later diff confined to the authorization record.
  **A further commit on that branch now needs the check re-run, not a revision here.** Recorded with it:
  `4c30c089`'s subject line was itself a finding for §5.6a, and it reached this document only because
  rev. 11 audited rev. 10's own count instead of trusting it — **reading a cited branch beats counting
  it.**
  **⚠ AND REV. 12's PUBLISHED CHECK TESTED THE LINE-WRAPPING, NOT THE TEXT (rev. 13).** The §2 limits
  clause wraps across a `> ` blockquote continuation, so a contiguous `grep -F` calls it **ABSENT** —
  **measured at `9c1230fa`: naive reports `1 of 7` absent, normalized reports `0`.** The failure
  direction is the whole risk: a false ABSENT on this invariant reads as *"the authorization no longer
  quotes Joseph's limits"*, which would move the pin and start a hunt for a finding that does not exist,
  **on a correct branch**. Two near-misses are recorded rather than repaired quietly: this lane's probe
  string had been **pre-truncated at exactly the wrap point**, so three green runs never crossed the
  break; and **the first draft of the remedy was itself broken** — `sed`'s `\?` is not an optional
  quantifier in BSD basic regex, so it returned `0` on macOS while GNU `sed` on Perlmutter would have
  accepted it. The published check is now a **`python3` normalizer**, matching the control plane's own
  language and **tested in both directions** (`1` present, `0` on a fabricated clause). **The pin does
  not move:** at `9c1230fa` the evidence-directory diff is empty and all seven clauses are present.
  **⚠ AND REV. 14 NARROWS REV. 13's OWN FIX, WHICH OVER-SCOPED THE DEFECT AND MISNAMED ITS OWNER.**
  *"Why `python3` and not `sed`"* reads as any `sed` normalizer being unsafe on macOS; it is not.
  Measured A/B/C on Darwin against `9c1230fa`: `sed 's/^> //'` — **the line as the preflight session
  actually sent it** — returns **`1`, correct** on BSD and GNU alike; only the **`\?` generalization,
  which was this lane's**, returns `0`; the negative control returns `0`. **Over-scoping a real defect
  is a false alarm on a correct command — the very shape rev. 13 had just catalogued, one level up** —
  and this lane had also told that session the opposite before measuring, which the record now corrects.
  `python3` is still adopted, for a measured reason rather than a general suspicion: the record holds
  **4 bare `>` lines**, so the obvious hardening of `s/^> //` is precisely the unportable construct, and
  `python3` removes the class rather than one instance.
  **READINESS RECLASSIFIED, A DECISION SHEET, AND THE METER REPAIR (rev. 15).** §6.7's single readiness
  list was **circular**: it named unwritten code and the two pre-launch reviews as prerequisites for an
  **implementation** authorization, when such an authorization **is** permission to write that code and
  a pre-launch review gates a **launch**. Readiness now separates **specification acceptance** (READY;
  the act is Joseph's, and §7's nineteen items are its content rather than blockers to it),
  **implementation authorization** (**zero compute**; ready today for the five inflation gates, the
  `g^c` and `r_null` reconstructions, the dominant-block refusal, the cause-4 re-add, the receipt schema
  and the validator skeleton — **only** the null's numeric `ε` waits on `D4` and the cause-3 acceptance
  code on `D1`/`D2`), and **production authorization** (NOT ready; `D-RESOURCE`, the committed receipt,
  the `PM-*` reads, the written code, the two reviews, and `D3` if the campaign is taken). New **§6.8**
  is a **decision sheet for `D1`–`D4`** — recommended choice, scientific justification, claim supported,
  cost consequence and remaining uncertainty, one row each, **pointing at §3.7's existing packets and
  proposing nothing new**. New **§5.6b** records that the **meter repair landed** at `72bcd2f6` on
  `main` (**not an ancestor of this tip**, merge base `c71b319a`): the metered unit is an **execution
  attempt**, `sacct -X -D`, an attempt is `(JobID, Start)`, receipt schema `2`, version-1 receipts
  **refused**. **`D5` is RESOLVED** in the direction §5.9 flagged and leaves the sheet. **§7 item 19's
  first remedy is TAKEN** — no default `--write`, scratch-path examples, and a runbook section stating
  that committing to the state path arms admission queue-wide — while the **second, untracking the gate
  path, was declined and referred to Joseph**; and the hazard is now **larger**, because after the
  repair the documented command yields a valid armable receipt where before it yielded a visibly wrong
  one. The waker cadence was **wrong by an order of magnitude** (`≈0.65`–`0.69`/day, `≈28`–`29` task-
  hours by the stop, not `0.05`–`0.07`); **`N` is `4`–`5` under all four ceiling readings, re-derived**.
  **REVIEW ROUND 5 (rev. 6) found no new substantive contract finding.** Two non-blocking remnants, both
  the drafting lane's: §7 item 3 still called the prior one that *"understates a Z member"* — replaced
  with *"a prior measured on a different subject"*, with the rev.-4 changelog row that carried it marked
  **superseded in place** rather than rewritten; and rev. 5's assembly-row edit had inserted **literal
  newlines inside a Markdown table row**, splitting it across three lines and breaking the table — the
  row is rejoined, and a **covering check over the whole file** found exactly that one and none
  remaining. **The remaining work is now specification completion only** — the joint-baseline statistic
  and acceptance rule, the normalized null bound and its justification, and complete costing. Those gaps
  prevent implementation readiness; **none requires reopening the assembly algebra or the settled
  rulings.**
  **CONTRACT REVIEW OF `D1`–`D4` (rev. 16), which the earlier PASS did not cover: `D1`, `D2` and `D4`
  are NOT ready for adoption as written and `D3` is supportable conditionally. Joseph approved the
  findings and rev. 16 implements them; the assembly algebra and the existing rulings are not
  reopened.** `D1`'s **thresholds are WITHDRAWN as acceptance criteria** while the statistics and direct
  normalization stand — macro formatting does not establish what sensitivity is scientifically
  acceptable, and the half-a-display-unit rule behind the numbers is **factually wrong in both
  directions at `12.5%` each under the stated synthetic sampling model** (a value uniform in its decade
  and a change uniform on `[0, one display unit)` — derived, then checked on `200,000` pairs; the rate
  belongs to that model, the bidirectional failure does not); **rounding equality** is the
  exact test if display invariance is what is meant. New **§3.7d**: every proposed gate is **blind to
  correlations** — `I₂` and `[[1,0.9],[0.9,1]]` give identical trace and per-bin statistics while their
  sum and difference uncertainties move `+37.8%` and `−68.4%` — and it is **live**, because
  `project_cov_nd.py` marginalizes the assembled covariance as `M C Mᵀ`; three candidate legs, none
  adopted. `D2`'s option (i) is **not adopted** — a missing data release does not prevent specifying a
  scientifically motivated per-bin tolerance. `D4`'s **`ε` is WITHHELD**: it is a summation bound over a
  computation that is not a summation, `n_rep` counts output bins while every accumulation runs over
  events, and the estimator is *"nearly deterministic in `seed` alone"* by its own module — a
  reproducibility question. `11b`'s **operand is corrected** (persist `x_cv`, `x_cv2` and the predicate,
  `1.05` MB against `≈41` GB) and **`11c`** is added as a conditional cross-check. Outcome branches are
  **restated over a declared leg set `L`**, so a third leg cannot be ignored by a two-leg MET branch.
  `N = 4`–`5` is re-labelled a **planning estimate, not demonstrated capacity**. **Zero cost, and one
  Tier-3 prerequisite removed**; the one new compute item — a `≈11.6` GPU task-h determinism control —
  is **returned as a bounded proposal and not run**. Five new §7 items (20–24) carry the questions.
  **ROUND 2 OF THAT REVIEW (rev. 17) accepted the threshold withdrawals, persisted null operands,
  correlation limitation, conditional `D3` and generalized leg-set branches, and found the REPLACEMENT
  `D4` proposal not yet passable.** Relayed **without** an approval statement, so rev. 17 separated
  corrections of this lane's own errors — made unconditionally — from the reviewer's dispositions, which
  it marked pending; **Joseph approved those findings on 2026-09-07 and rev. 18 discharges the mark.**
  **The distinction rev. 17 drew is kept, because approval is where it gets lost: the FINDINGS are
  approved, and `D1`, `D2` and `D4` are NOT adopted — the approved finding about them is that they are
  not ready as written, with `D3` conditional. No cell opens and no count moves.**
  **A FOLLOW-UP CHECK (rev. 19) confirmed that separation and found three of rev. 17's own explanations
  still wrong — none a new decision, all this lane's errors, corrected unconditionally.** `B > S` does
  **not** mean every correct run fails: **`B` is an UPPER bound on the error**, so a loose `B` above `S`
  establishes that **`B ≤ S` is not demonstrated** — a statement about the evidence — and **not** that
  the envelope is inadequate, which is a statement about the world. *"Never taken as an endpoint"* is
  withdrawn: **either endpoint is admissible when justified**, and what is forbidden is choosing
  mechanically. *"Tier 2 validator runtime, not `R5`"* is a **category error** — Tier 2 is permission to
  write code, `r5_meter` meters **scheduler tasks by `ElapsedRaw`**, and arithmetic folded into an
  in-scope task adds no row while lengthening the metered quantity; §3.7d now carries a four-venue
  table. And the control's *"no recorded actual"* was a **false absence citing the wrong launcher**: the
  unmeasured combine is `budget5d`, while the control invokes **`uthrow5d_combF`**, measured three times
  at §5.9 row 13 (`0.3875`/`0.4239`/`0.5764` CPU task-h) — the control stays unpriced, but on `n` and
  the thread-count arm rather than on an absence. **`B ≤ S`, the three gaps, the price withdrawal and
  every disposition stand as written.**
  **REV. 20 — those corrections PASS, with one left and one operational re-measurement.** §3.7d's
  figures were called *"venue-independent"*; they are **local timing estimates** whose runtime depends
  on hardware, threading and numerical libraries, now labelled **MEASURED locally / TRANSFERRED with
  runtime unestablished elsewhere** — and `s_eig`, the only non-negligible one, is the most exposed,
  since §3.7a's own finding is that nothing pins the thread count. New **§5.6c**: the meter repair is
  now **on `main`** — `origin/main` = `d4922b89` and `72bcd2f6` is an ancestor of it, so §5.6b's branch
  framing is superseded, while the merge base with this tip is still `c71b319a`, so **every
  `r5_meter.py` file:line here still describes the pre-repair version**. Admission is shut more strongly
  than before: **`git log --all` over the gate path returns `0` commits — it has never been armed on any
  ref**. **And one relayed ruling is NOT corroborated:** that Joseph ratified the attempt-summing
  reading and declined the untrack. At `d4922b89` the source FINDING is still *"open — three things are
  with the decision owner"*, so **§7 item 19 stays referred and `D5` stays resolved by code, not
  ratified** — uncorroborated is not false, and if the relay is right the outcome is the one already
  assumed.
  **REV. 21 — CORROBORATED, and by the artifact §5.6c said was missing.** Joseph confirmed both
  rulings directly on 2026-09-07, having given them **2026-09-06** on approving the landing;
  `DECISION-20260907-joseph-ratifies-r5-attempt-accounting-and-declines-untracking.md` is on `main`
  (`3497abec`, amended `32880a6f`) and the finding is de-staled against it at `6669ac3b`. **§7 item 19
  closes as DECLINED and `D5` is RATIFIED** — the alternative reading of R5 §3 is overturned by
  decision, so reviving it needs a new decision rather than an edit. **Admission is still unarmed.**
  The relay was accurate throughout; only the record was missing. **`min(achievable, acceptable)` is WITHDRAWN as acceptance-blocking:** an observed
  reproducibility floor is not an acceptance tolerance, and §3.6a — two sections earlier in the same
  document — says such a floor bounds `ε` from **below**, so `min` inverted its direction. Replaced by
  **`B` (operating-error bound, with assumptions and confidence), `S` (independently justified
  scientific cap), the precondition `B ≤ S`, and `ε` argued within `[B, S]`**; if `B > S` the finding is
  that **the execution envelope is not demonstrated adequate**. The control is revised on three gaps —
  **a within-envelope null does not measure a between-envelope shift**, the repeat count needs a
  coverage/confidence objective and its sampling assumptions, and **two arms do not prevent tuning** —
  and its subject engages `§6.4`. **Its `≈11.6` GPU task-h price is WITHDRAWN**: an invocation is a whole
  `do_combine`, and the combine is a **CPU** job (`sbatch_uthrow_combine_5d_fast.sh:4`), a correction
  §0.0's rev.-2 row 10 had already made once. **Three routes to `B` are now named, none privileged**, the
  cheapest being **code, not compute** — pinning `num_threads`/`deterministic`/`force_row_wise`.
  **Nonblocking, all corrected:** the persistence was priced against `≈41` GB when the throw product is
  **`2.668` GB measured** (`41` GB is the 45-component band family — a `15×` operand error whose
  conclusion happened to survive); §3.7d's legs cost **no new members but are not free** (`s_eig`
  `≈1`–`3` min per member, measured by timing `eigvalsh` at four sizes and scaling by `n³`); §3.7's
  *"this section completes them"* is withdrawn; receipts now say **"did not exceed their declared
  movement limits"** rather than *"did not move"*; and `D1`/`D2` need **justified tolerances and scope**,
  not two numbers.

### PET typed-descriptor semantic evidence

- [`../../nd-unfolding/pet/TYPED_DESCRIPTOR_STATUS.md`](../../nd-unfolding/pet/TYPED_DESCRIPTOR_STATUS.md)
  - current PET typed-descriptor status and unresolved semantic gates.
- [`PACKET-20260901-pet-typed-descriptor-semantic-evidence.md`](PACKET-20260901-pet-typed-descriptor-semantic-evidence.md)
  - fixed-sample evidence packet; the semantic gate is **BLOCKED, NARROWED**, with no replacement
  category, sentinel, filtering, unit, or calibration rule adopted.
- [`runs/pet-typed-semantic-evidence-20260901/fixed-sample-telemetry.json`](runs/pet-typed-semantic-evidence-20260901/fixed-sample-telemetry.json)
  and [`runs/pet-typed-semantic-evidence-20260901/m60/ARTIFACTS.tsv`](runs/pet-typed-semantic-evidence-20260901/m60/ARTIFACTS.tsv)
  - archived fixed-sample telemetry and M60 artifact index. The M60 layer remains single-source raw
  evidence; routing does not make it independent verification or semantic adoption.
- [`REVIEW-20260902-pet-typed-semantic-evidence.md`](REVIEW-20260902-pet-typed-semantic-evidence.md)
  - independent artifact and method review; it is not an independent measurement reproduction.

### ✅ §10.1 READY; GATE 1 PASSED ROUND 2, 2026-08-30 — submission remains a separate decision

- [`GATE1-VERDICT-ROUND2-20260830-k0-7ac0edec.md`](GATE1-VERDICT-ROUND2-20260830-k0-7ac0edec.md)
  — **GATE 1: PASS, 18 PASS / 0 FAIL / 0 NOT-EVALUABLE.** PB-25 pins the rubric and complete
  execution candidate by content digest. The additive recapture recorded the canonical checkout at
  726 untracked entries; independent grade-time remeasurement found the same HEAD, branch and
  **726 / 726 untracked / 0 modified**. The original pair remains the round-1 historical object.
  No compute was submitted, Gate 2 was not moved, and submission remains a separate decision.

- [`VERDICT-20260830-readiness-10-1-k0-7ac0edec.md`](VERDICT-20260830-readiness-10-1-k0-7ac0edec.md)
  — **READINESS-10-1: PASS.** F-7(b), F-8(b), and F-17(b) are present at `7ac0edec` and mapped by
  exact content identity to committed independent grades. The F-17 mapping carries an explicit
  self-reference disclosure: the readiness checker authored the prior Step-3 grade and verifies its
  existence/applicability rather than reissuing it.
- [`GATE1-VERDICT-20260830-k0-7ac0edec.md`](GATE1-VERDICT-20260830-k0-7ac0edec.md)
  — **ROUND 1 HISTORICAL BLOCK, 17 PASS / 1 FAIL / 0 NOT-EVALUABLE.** `F-17(a)` failed because the canonical
  operand records 722 untracked entries and the checkout now has 726; the four additions are the
  dashboard deployment after the operand completed. `OI-175` routes the replacement. No operand was
  retaken, no compute submitted, and Gate 2 remains unchanged.

### 🔒 DEPLOYED AND RE-FROZEN AT `7ac0edec`, 2026-08-30 — steps 1–2 historical filing; later grade above

- [`FREEZE-20260830-k0-deployment-7ac0edec.md`](FREEZE-20260830-k0-deployment-7ac0edec.md)
  — **THE DEPLOYED TREE `/pscratch/sd/j/josephrb/k0r2/clean` IS NOW FROZEN DETACHED AT
  `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` UNTIL THE NEW REHEARSAL'S F-1(b) IS PRODUCER-FILED.** No
  `checkout`, `reset`, `fetch`-and-merge, re-declaration or branch repoint in that directory, by any
  lane. **It expires when that F-1(b) filing is COMMITTED — not when jobs merely look terminal**, and
  it **cannot yet expire**: the rehearsal has not been submitted, so a zero-length job list is not a
  far end. Carries the **superseded-pin row** required by `OI-123` — old `aa67c426…`, new
  `7ac0edec…`, reason and authority — and records that the predecessor §7.0.19 freeze had **already
  expired** (`FINDING-20260829`, plus the landed producer F-1(b) at `aa67c426`), so this replaced a
  spent hold rather than breaking a live one. A **prose** hold: preventive by convention, detective by
  A-2(a) **and** A-2(f), **not** a mechanical guarantee — `.git` is `drwxrwx---` **by ruling**
  (§11.1.1), and ten `refs/tags/evidence/*` at non-pin commits leave `checkout <tag>` a live,
  never-exercised route. **Authorizes nothing.**

- [`DECLARATION-20260830-k0-deployment-7ac0edec.md`](DECLARATION-20260830-k0-deployment-7ac0edec.md)
  — **A-2(a)–(g) all MET at the new pin, each clause in its own invocation.** `820` tracked `.py`/`.sh`,
  listing sha256 `8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea`, declaration file
  `ca6a8f2b…` at `/pscratch/sd/j/josephrb/k0r2/declarations/7ac0edec/source-manifest.json`, porcelain
  **0** (and `--ignored` also 0), detached with **`refs/heads` empty and no remote**, `820 of 820`
  executing copies **CURRENT**. `782 → 820` is arithmetic: `aa67c426 → 7ac0edec` adds 221 tracked
  paths, deletes none, 38 of them `.py`/`.sh`. **The digest was predicted off-cluster from git objects
  BEFORE the deployment and its predictor has a positive control at `aa67c426` (782 / `fa3489e2…`)**,
  then confirmed by the deployed tree and again by the clone recovered from the new bundle — three
  object stores. Firing controls recorded for **(b)(c)(d)(e)(f)(g)**, including `--compare` against the
  superseded `aa67c426` declaration at **rc=3**. **Does NOT pass Gate 1, does NOT move Gate 2, and does
  NOT convert `F17B-REPAIRED-CHAIN: NOT FIT` into FIT** — it removes N1's *mechanism*; the verdict is
  step 3's, and the producing lane is ineligible to give it.

- [`state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json`](state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json)
  — the machine record: the six-part sequence with every command, new freeze ref
  `refs/tags/freeze/k0-7ac0edec` **in two repositories**, bundle
  `k0-clean-7ac0edec-20260829T233037Z.bundle` (82 761 577 B, sha256 `514bd46e…`), **exact-row**
  `list-heads` assertion, recovery **TESTED** by `clone --no-local` → `fsck` → detached checkout
  (porcelain 0, 1804 tracked, recovered clone re-measures 820 / `8d036d94…`), the mode round-trip, and
  the `.git` delta **partitioned rather than summarised** (23 → 24 writable files; the +1 is *named*:
  the new loose ref, with 0 writable files under `objects/`). Records that **no `.py`/`.sh` byte was
  touched** and that no in-place edit, copied file, `PYTHONPATH` substitution, `MNV_MEASURER` override
  or schema exception was used.

- [`state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json`](state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json)
  — **the precondition, and it PASSED before anything was made writable.** All six items of the
  2026-08-26 receipt's `reverification_recipe` re-run and MATCHED: bundle `8ce58391…` / 79 140 251 B,
  HEAD `aa67c426…`, ref set **exactly ten rows**, modes `dr-xr-x---` / `drwxrwx---`, pin in
  `list-heads`, recovery clone/fsck/checkout rc=0 with tree `60120bfb…` and porcelain 0. **AND ONE
  FINDING:** the receipt's `bundle.generated_from` path `/global/u2/j/josephrb/mnv-work/MINERvA-OmniFold`
  **no longer exists**, so the local-only tag `refs/tags/freeze/k0-aa67c426` was present in **no live
  cluster repository** — recoverability survived only because the recipe reads that ref out of the
  **bundle**. Re-created at the same commit in the canonical checkout (a restoration, **not** a
  repoint), and the generalisation is why the new freeze ref exists in two places.

### ✅ GATE 1 PASSES — round 9, 2026-08-23, 18 PASS / 0 FAIL / 0 NOT-EVALUABLE

- [`DECISION-20260824-joseph-deployment-freeze-until-f1b.md`](DECISION-20260824-joseph-deployment-freeze-until-f1b.md)
  — **⚠ SUPERSEDED 2026-08-30, AND IT HAD ALREADY EXPIRED BEFORE THAT. Everything below was true
  when written; do not read it as governing the deploy tree now.** Its expiry condition fired when
  the producer F-1(b) at `aa67c426` was filed, and the tree is now held by
  [`FREEZE-20260830-k0-deployment-7ac0edec.md`](FREEZE-20260830-k0-deployment-7ac0edec.md) at
  `7ac0edec…` instead — see that document's superseded-pin row for old value, new value, reason and
  authority (`OI-123`). Retained verbatim because it is the authority §7.0.19 was held against and
  because annotating in place is this router's convention. **The historical statement follows.**
  **THE DEPLOYED TREE IS FROZEN AT `aa67c426` UNTIL F-1(b) IS FILED.** No `checkout`, `reset`,
  `fetch`-and-merge, re-declaration or branch repoint in `/pscratch/sd/j/josephrb/k0r2/clean`, by any
  lane. **It expires when F-1(b) is TAKEN, not when the rehearsal "looks done"** — `combine`'s
  conjunctive `afterok` can read as queued while terminal. Contract **§7.0.19**. A **prose** hold:
  preventive by convention, detective by A-2(a), **not** a mechanical guarantee. Residual measured —
  10 `refs/tags/evidence/*` in that tree, none at the candidate, so `checkout <tag>` is still a live
  route. **Authorizes nothing.**

- [`DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md`](DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md)
  — **Joseph's ruling, and the authority §7.0.18 was held against. GATE 2 IS NINE CLAUSES:** F-1(b),
  F-2(b), F-3(b), F-4(b), F-5(b), F-7(b), F-8(b), F-17(b), F-18(b). **`F-6(b)` is NOT waived — it is
  mandatory under the separate leg-6 completion gate.** The ruling **authorizes nothing**: no leg 6, no
  adoption, no consumption, no member k≠0, no other clause relaxed. **A verdict recorded before
  2026-08-24 correctly grades ten; after, nine — say which.**

- [`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`](DECISION-20260825-joseph-gate2-fail-and-four-rulings.md)
  — **Joseph's ruling on run `k0-aa67c426-20260824T145751Z`: GATE 2 IS RECORDED FAIL, no partial
  credit.** Three clauses PASS (`F-1(b)`, `F-4(b)`, `F-18(b)`), **six are NOT DISCHARGED.** Strict
  §7.0.10 moves `F-2(b)`, `F-3(b)` and `F-5(b)` to NOT DISCHARGED because the grader measured what it
  graded — its measurements are **retained as verification evidence but cannot substitute for a
  missing producer filing.** `F-17(b)`'s `:1471` half is **impossible, not pending and not
  deferred**, and back-filling the pre-submission column is refused outright. `b2d7d4ca` is the
  **immutable** historical referent and must not be rewritten to make the rehearsal pass;
  `mnv-work/` is canonical **forward-only.** The prior instrument GRADE is **EXPIRED** (all three
  pinned digests moved), so the comparator that produced the filed record has never been graded, and
  the repaired one needs a new independent grade before it can support another Gate-2 filing —
  repairer, grader and spec author must be three different parties. **The ruling authorizes NO
  compute**, and confers no Gate-2 credit, no uncertainty adoption and no publication claim. **Scope
  is GBDT uncertainty, not PET** — an earlier PET framing was withdrawn by Joseph and survives only
  in the immutable message of `109bb130`; §0 of the document governs. Carries the defect ledger for the far-end path: two
  defects corrected in `38a7b16b` whose **old explanations are retracted, not preserved**, one
  irreparable unanchored "233 behind main" in `a3ed8631`, and the bounded dotless-pattern fail-open
  that leaves the filed record unaffected. `MANIFEST.tsv` drift is routed **out** of this verdict to
  F-14 / §7.0.7. **Three further rulings, 2026-08-25.** §11.1.1: **do NOT `chmod` the frozen
  deploy's `.git`** — verified not applied — because it is an accident guard the tree owner undoes in
  one command AND it breaks `git worktree add`, this repo's mandated audit mechanism; a **`git bundle`
  plus a recorded `sha256`** is ordered instead, since the property the freeze lacks is
  **detectability**, not resistance — **LANDED 2026-08-26** at
  `state/RECEIPT-20260826-k0-freeze-bundle-detectability.json` (bundle 79 140 251 B, sha256
  `8ce58391…`, recovery TESTED by `clone --no-local` → `fsck` → checkout, porcelain 0), and the
  postcondition earned its keep: a `--all` bundle would have verified, hashed, and **contained
  nothing to recover**, because that clone has no branch refs and none of its ten evidence tags
  contains the pin. §12.4: **the dead literal stays, NO CHANGE** — a typo'd
  whitelist row is **fail-closed UNDER-coverage, the direction OPPOSITE to D-3**, and suppresses
  nothing (measured: still exit **20 UNEXPECTED**); the proposed "unused entry ⇒ non-zero exit"
  middle option is **STRUCK as unsatisfiable**, because a correct entry is unused whenever the two
  documents agree, and the figure **"517 of the 773"** is **STRUCK as a population conflation**.
  §10.2: the register is **CLOSED for this pass**; the third independent origin against which Gate 2
  will be re-evaluated is the `codex-school` dispatch — **UNCLAIMED**, so not yet an origin — and
  there is **no compute until it lands on its own evidence.** **CLAIMED in writing 2026-08-26** by
  that Codex session; the UNCLAIMED reading is kept as the state as ruled on 08-25 and is not
  rewritten. A claim is not a delivery, not a grade, and not Gate-2 credit. **Next route, per Joseph 2026-08-26:**
  the assignment remains **publication close-out**; after the Gate-2 freeze receipt, re-read a fresh
  `LIVE-STATE.md` and the governing `OI-*` and resume the **routed** node, continuing the adopted
  scalar-5D covariance **adoption gate** if that is still critical path — not an assumed workstream,
  and not a reopening of completed or broadly scoped 5D work. The `MANIFEST` classification finding
  stays an **open referral, non-blocking** unless the routed gate explicitly depends on it.

- [`DECISION-20260828-joseph-f17b-four-surface-repair.md`](DECISION-20260828-joseph-f17b-four-surface-repair.md)
  — **Joseph approved the bounded four-surface F-17(b) repair.** The measurer now emits a real
  wall-clock interval and branch-or-detached identity, the comparator requires and carries both,
  the preserver is digest-bracketed across its own invocation, and a failed measurer short-circuits
  immediately. It records dated successors for both historical shell-script pins without editing
  either old value. **This authorizes the repair and fresh independent fixture-only grade only:** no
  far-end run, rehearsal, compute, covariance adoption, Gate-2 movement or publication claim.

- [`DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md`](DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md)
  — **One F-14 / §7.0.7 manifest-coupling omission by the independent comparator-repair lane,
  filed against itself.** `c8a29082` changed `compare_m1_m6.py` and `test_compare_m1_m6.py` without
  regenerating `MANIFEST.tsv` in the same commit; `generate_manifest.py --check` returns **rc=1 at
  `c8a29082`** in a clean detached worktree, porcelain 0, and rc=0 at `65f95600` — the shape that
  makes this class invisible, since the endpoint complies and the intermediate sha does not.
  **The excuse is removed by measurement:** the coupled single commit reaches rc=0 **in one pass**
  (unpushed probe `3ae2c6ba`), so committing sources first "so the counts describe a commit" was an
  error and not a trade-off — when all paths go in together the working tree *is* the commit.
  Two transferable findings: `generate_manifest.py`'s DIRTY warning **fires identically on correct
  procedure and on the hazard**, steering a reader into the violation; and the same-commit coupling
  for the manifest is a **composition** of F-14 with §7.0.7, stated in the sibling record's §1 and
  **not in §7.0.7's own text**, so a lane reading only the contract can satisfy its letter at the
  graded sha while breaking the coupling at every commit before it. The composition is **accepted,
  not rebutted.** **§5.1 records a SECOND omission by the same lane, `3dbca981`, committed while
  filing this very document** — rc=1 at that sha in a clean worktree — and it is the **same kind**
  of failure as the first. **§5.2 retracts this lane's own defence that the `intended`->`tracked`
  flip is irreducible for a new path: it is false.** `generate_manifest.py:92` reads the **INDEX**
  via `git ls-files`, so staging the new path before regenerating gives `tracked` in one pass —
  unpushed probe `435de9d3`, rc=0 in a clean worktree. **The two-commit shape is a convention, not
  a constraint**, and the cited precedent `109bb130` is itself **rc=1 at its own sha** though
  published as compliant. The defence was reached **without ever opening the code**, inferring
  necessity from convention and writing it in the grammar of a measurement. Both this lane's
  "irreducible" and the close-out lane's "compliant pair" are the **same unmeasured belief held
  from opposite sides**, each exonerating its own commits, untested until one lane was accused.
  Also corrected: a claim that nothing had absorbed this lane's instance, **false within minutes,
  replaced not softened** — both retractions share the tell that the claim was *comfortable*. **NOT** citable for any Gate-2 clause, nor for the D-3 repair, which stands as
  filed and remains **UNGRADED** under ruling 3.

- [`DISCIPLINE-20260825-f14-manifest-coupling-omissions.md`](DISCIPLINE-20260825-f14-manifest-coupling-omissions.md)
  — **Three F-14 / §7.0.7 manifest-coupling omissions by the publication close-out lane, filed
  against itself.** `30ede740`, `a3ed8631` and `38a7b16b` each moved a tracked path without
  regenerating `MANIFEST.tsv` in the same commit; `generate_manifest.py --check` returns **rc=1 at
  `38a7b16b`** in a clean detached worktree. **`a3ed8631` left an entire row absent, not a stale
  count** — the record it filed was invisible to the router at that commit. **Joseph named one
  commit; the measurement found three**, and all three are recorded so the enumeration is not
  partial. The keeper: the missing row was silently absorbed by the *independent grader's*
  regeneration in `a3000487`, so **a later "the manifest is current" says nothing about whether any
  particular commit complied** — compliance is measurable only at the commit, in a clean worktree,
  and only until someone else regenerates. Regeneration in `109bb130`/`dce8e8cc` **repairs the
  manifest state but does not erase the gap.** **NOT** citable for any Gate-2 clause, and explicitly
  does **not** account for the separate unattributed 23-row drift measured at `e428a645`.

- [`FINDING-20260824-gate2-preparation-and-four-open-rulings.md`](FINDING-20260824-gate2-preparation-and-four-open-rulings.md)
  — **Gate 2 is PREPARED and needs FOUR RULINGS before it can be graded.** Clause list derived
  independently as **ten** (F-1(b)…F-8(b), F-17(b), F-18(b)), agreeing with §7.0.5's arithmetic and
  confirming `F-3(b)` was missing from this router. **`F-6(b)` is structurally unsatisfiable inside the
  scope a Gate-1 PASS unlocks**, so Gate 2 cannot pass as written; F-4(b)'s population is undefined;
  F-7(b)'s exclusion half has no instrument (a §7.0.8 FAIL surface, not a pending input); F-1(b) must
  name `listing_sha256`, not a file digest. Instruments all verified non-vacuous, so Gate 2 is **not**
  tooling-blocked. **No clause is graded.**
- [`READING-ORDER-20260824-k0-package-annotations.md`](READING-ORDER-20260824-k0-package-annotations.md)
  — **READ FIRST if you are grading either gate.** The k=0 package was corrected by annotating in
  place, so its correctness depended on a reader finding all nine annotations across five files. This
  lists them in one reading order, marks the **4 BINDING** (they change what a clause requires) apart
  from the **5 HISTORICAL**, and names the four places a withdrawn sentence is printed *after* its own
  retraction — so a grep cannot tell asserted from withdrawn. **Router only; cite the artifact.**
  Records two live conditions: the contract's `main` and build-branch copies have **diverged again**
  (§7.0.17 is on `main` only, where `b2075558` had made them byte-identical), and the `[remedyA]`
  marker is `:711` in the canonical checkout and on `main` but `:787` on the build branch.

> **⚠ THIS HEADING IS A DATED SNAPSHOT, 2026-08-24.** Round 9's 18/0/0 was graded at `a54038b2` and
> **does not carry forward**: the OI-136 guard refused legs 5a/5b, the repaired candidate is
> `aa67c426`, and rounds 10–12 have since run (round 10 FAILED `F-1(a)` on a deployment excursion;
> round 11 stood at 16/2). **Gate 1 is not currently claimed passed on this branch's record**, and
> this section is behind `build-k0-execution-integrity`'s copy of this router. Read the round-10 packet
> and the 2026-08-24 receipt on that branch before treating any count here as current.
>
> **AND THE Gate-2 LIST BELOW IS INCOMPLETE — `F-3(b)` IS MISSING.** §7.0.5 makes **F-3 SPLIT**, with a
> post-rehearsal half: *"grep the job stdout → zero `--allow`; publish the command."* The enumeration
> below jumps `F-2(b)` to `F-4(b)`. §7.0.5's own arithmetic — **10 SPLIT criteria** — is the check:
> F-1…F-8, F-17, F-18. **A Gate-2 lane that inherits the list below grades nine clauses and misses
> one, and §F's no-partial-credit rule means the miss is silent.** Derive the list from §7.0.5's
> POST-REHEARSAL column, never from this router.

- [`GATE1-VERDICT-ROUND9-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND9-20260823-k0-execution-integrity.md)
  — **the terminal verdict.** sha256 `d5bfb863…`, 350 lines, landed byte-identical. Declared and
  deployed candidate `a54038b21fdebfc975bec452a05866ffa571a36c`.
  **IT UNLOCKS THE SEVEN JOBS OF LOGICAL LEGS 1–5 FOR k=0 AND NOTHING ELSE.** It is **not** a
  submission authorization — the grader states the decision to submit is Joseph's. Leg 6 stays gated
  by Amendment 1 §C, no member k≠0 is authorized, and Gate 2 still owes `F-1(b)`, `F-2(b)`,
  `F-4(b)`–`F-8(b)`, `F-17(b)`, `F-18(b)`.
- [`GATE1-VERDICT-ROUND8-…md`](GATE1-VERDICT-ROUND8-20260823-k0-execution-integrity.md) — 17/1,
  `F-2(a)` and `F-17(a)` closed here; failed `F-1(a)`.
- [`GATE1-VERDICT-ROUND7-…md`](GATE1-VERDICT-ROUND7-20260823-k0-execution-integrity.md) — 17/1,
  failed `F-17(a)`. **Landed now rather than earlier**: rounds 7 and 8 were outside the repo, so the
  passing verdict cited artifacts a reader could not reach.
- [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md) — the
  A-2(a)–(g) filing the pass rests on. **780** tracked source files, listing sha256 `1b45da55…`.

- [`DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md`](DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md)
  — **`generate_manifest.py`'s DIRTY warning fires identically on correct procedure and on the
  hazard, and its advice is FALSE in the one case F-14 requires.** Controls, only staged-ness
  varying: clean tree **silent** (so the instrument is not always-on), staged edit and unstaged edit
  give **byte-identical warning text and equal rc**. A lane cannot use this output to tell whether it
  is about to break the F-14 coupling. Measured consequence: six coupling omissions across two lanes
  in one day, one of them with the warning's own sentence recorded as the reasoning. The
  discriminating fact **already exists and is discarded** at `generate_manifest.py:328`, where the
  porcelain `XY` code is dropped in the same expression that builds the dirty set. A repair must add
  an arm that FIRES on `' M'`, stays SILENT on `'M '`, and covers the opposite direction on `'MM'` —
  **corrected 2026-08-25**: the third arm previously demanded "staged but not committed", a **future
  fact no implementation inside the tool can observe**, and was therefore unsatisfiable. **In scope,
  same family:** default-mode `--check` silently absorbs another lane's untracked files (rc=1, 537
  rows) while `--committed-only` gives rc=0, 533 — that rc=1 is the instrument reporting and must not
  be "repaired". **Distinguish it from a real one:** hours later `e30dbd45` *committed* those four
  paths without regenerating, so `main` went rc=1 in **both** modes for a genuinely different reason
  (a third lane's F-14 omission, measured at
  `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` §4.2 and regenerated here). The two are
  indistinguishable from the exit status alone. **Re-measured at the tip 2026-08-26: `fd58e71b` is
  rc=0 in BOTH modes, rows=537, porcelain 0** — `aaed392d` was rc=1 *when it was the tip*, and any
  precondition citing the older green `17b79fca` result is **stale across the failing interval**.
  **§6 was UNCLAIMED** as ruled on 08-25: a handoff, not a delivery, and not citable as coverage or
  as an independent origin until an implementer acknowledged it. **It was CLAIMED in writing on
  2026-08-26** by the `codex-school` Codex session, so that condition is now met and the historical
  clause is retained rather than rewritten. **It was then DELIVERED by that implementer on
  2026-08-26 and remains UNGRADED**; §7 carries the baseline re-measurement, implementation, and
  controls. Delivery is not a grade and supplies no Gate-2 credit. **§6 DISPATCH (Joseph,
  2026-08-25): the independent implementer is `codex-school`**,
  re-deriving from this record and the artifacts and **not** from the close-out lane's reasoning or
  the advisory lane's analysis; the grader must be a third party. **The publication close-out lane is
  disqualified from BOTH** — it authored §4, and §4 is a *specification*, which is the prong ruling 3
  turns on (an earlier version of that section wrongly cleared itself on the tool-authorship prong).
  **NOT** citable for any Gate-2 clause, **does not alter Gate 2's FAIL**, is not part of the D-3
  repair, and excuses no omission.
### ⚠ ROUND 11 — Gate 1 at **16 PASS / 2 FAIL**; F-1(a), F-9, F-12 CLOSED; F-8(a) and F-17(a) filed and awaiting grade

- [`PACKET-20260823-round10-oi136-runtime-violation-repair.md`](PACKET-20260823-round10-oi136-runtime-violation-repair.md)
  — **round 9's 18/0/0 at `a54038b2` is historically valid and does NOT carry forward.** The OI-136
  guard refused legs 5a/5b before any work ran. Repaired candidate **`aa67c426`**, deployed,
  `porcelain 0`, 0 writable. Census **52 / 2 / 1** (53 is the PRE-repair figure). **Gate 1 is NOT claimed passed.**
- [`DECLARATION-20260823-k0-candidate-aa67c426.md`](DECLARATION-20260823-k0-candidate-aa67c426.md)
  — A-2(a)–(g) all MET at the new sha; 782 files, listing `fa3489e2…`. **§6 records the deployment
  excursion**: the declaration commit was deployed on top of the candidate, round 10 failed `F-1(a)`
  on it, and the deployment was reset to the declared sha on 2026-08-24. §6.3's branch-ref sentence is
  annotated as since-falsified; §6.8 transcribes the tree's reflog (18 advances in two days) because it
  expires; §6.9 records the hardening and what it does **not** close.
- [`RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md`](RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md)
  — **F-8(a), F-9, F-12 and F-17(a) measured at `aa67c426`.** P-6's launcher grep with its full output
  raw and collapsed (171/114; 101/27/**12**, reconciling to the contract's nine plus three apparatus
  tools); P-5's blind spots; the import closure **18 module-level / 20 any-depth / 2 hazards** with
  both index scopes named, replacing an unpublished "15"; N-1's three arms with exit statuses filed;
  M-1…M-6 on **both** trees with one identified difference. **Ten findings, four against this lane's
  own work.** Builder-produced evidence — **it grades nothing**.



- **ROUND 2 COMPLETED 374 OF 374 WITH ZERO FAILURES, 2026-09-01:**
  [`RECORD-20260901-k0r2-round2-outcome.md`](RECORD-20260901-k0r2-round2-outcome.md) — queue empty at
  `08:57:51Z` after ~36 h. **374 distinct task identities COMPLETED, 0 FAILED, 0 CANCELLED**, all seven
  arms at full declared population. Round 1 of the same run died with six tasks in 8–15 s on `OI-179`;
  the only change was one exported variable. **Products verified READABLE, not merely marked**: 143
  `.done`, and 185 `.npz` opened with every member read, 0 unreadable — though the first read reported
  two failures and **the reader was wrong, not the files** (`allow_pickle=False` is a numpy default;
  all 61 `uq_5d` products carry object arrays). **The canonical operand never moved for the entire
  run** — porcelain 726 / digest `d429f0f3` at submission and identically 36 h later — and the deploy
  tree stayed frozen at `7ac0edec`, porcelain 0. **§5 says outright that a completed run is not a
  passed gate:** Gate 2 remains **FAIL** on six clauses, no cause is discharged, nothing is adopted,
  counts stay CAND `1 of 7` / QUOTED `0 of 7`. Supplies the n=2 complete populations that make
  `OI-177` ratifiable — and kills the 40 CPU-h figure the amendment first proposed, since arm 5
  measured **49.11**.
- **CAUSE 3's `M(ii)` PREDECLARED — THRESHOLD FIXED FROM PUBLICATION PRECISION, BEFORE ANY NUMBER EXISTS, 2026-09-01:**
  [`PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md`](PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md)
  — `CRITERIA` flags cause 3's `M(ii)` UNRESOLVED and rules `\gbdtAiEstTrace` CANNOT SERVE on footing (`:194`), so the
  magnitude needs its own measurement on the candidate's bkgaware, post-J28 footing. **`M(i)` is NOT re-opened: it is
  already satisfied**, the candidate's `upstream_fixed_seed_null_norm` `5.8223488501140625e-50` against `tol 1e-12`.
  **THE ACCEPTANCE THRESHOLD IS SET, AND IT IS PRINCIPLED RATHER THAN TUNED:** `f_agg ≤ 4.15%` and `f_med ≤ 2.74%`,
  derived from the precision at which the affected quantities are already PRINTED — an omitted independent contribution
  `S` enters in quadrature, and requiring `U' − U` to stay under half the last printed unit gives
  `S/U ≤ sqrt(2δ + δ²)`. **Re-derived independently at review: `5.81` at 3 s.f. → `4.1496%`, `13.36` at 4 s.f. →
  `2.7361%`, reproducing both.** The boundary is a property of how the numbers are printed, not of what the measurement
  will return, which is what makes it non-tuned. **It also argues F7's floor rule does NOT transfer** — under a true zero
  seed response `C_seed` is zero, so `sqrt(Tr C)/sqrt(12)` is no noise floor for it and would import systematic
  covariance into an estimator-noise test. Six exhaustive branches including `NOT MET — BOTH`. Cost re-derived:
  `0.667` GPU + `0.050` CPU task-hours, inside the ratified arm-1 (20 GPU) and arm-7 (5 CPU) envelopes under
  `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`. **Declares only; measures nothing, and the scan
  had not run when this landed.**
- **CAUSE 7 FINALLY HAS DISCHARGE CRITERIA — DRAFTED, NOTHING GRADED, 2026-09-01:**
  [`PREDECLARE-20260901-cause7-discharge-criteria.md`](PREDECLARE-20260901-cause7-discharge-criteria.md)
  — `CRITERIA-20260811` is titled for causes 1, 2, 3, 4 and 6; **cause 7 had none at all**, appearing only in its §4.1 as
  a finding that its recorded discharge is for a DIFFERENT PRODUCT. Drafted under Joseph's 2026-09-01 authorization
  (*"I authorize you spend the hours and drafting to investigate and fix the causes"*). **Four legs, every one OPEN;
  the word MET does not appear in the document.** §0 separates FOUR artifact names so the FPS object cause 7 was
  discharged against (266 bins, job `56431823`, `OI-5` resolving it FPS-only) cannot be substituted for the 5D
  candidate. **The defect IS on the candidate's path** — `adopt_unified_5d.py:17-20` states the nine detector-lateral
  bands *"are left untouched — the throw does not cover them"*, so the laterals ride through inside
  `hCov_combined5d_total`. **THE M THRESHOLD IS DELIBERATELY LEFT OPEN FOR JOSEPH**, in the form
  `nd-unfolding/uq_math.py:128-137` uses for `F7_FLOOR_MULTIPLE`: no pre-observation materiality rule exists and the
  ratio is diagnostic and unbounded, so *any* cutoff written now would be tuned to already-visible data. He must either
  rule a principled threshold before M is graded or rule M measurement-only. Grades nothing, discharges nothing,
  adopts nothing, moves no gate.
- **THE SCALAR-5D COVARIANCE IS A CLAIM UPGRADE — AND THE DEPENDENCY IS KEPT BY CHOICE, 2026-09-01:**
  [`DECISION-20260901-joseph-oi187-upgrade-not-blocker.md`](DECISION-20260901-joseph-oi187-upgrade-not-blocker.md)
  — Joseph, his own turn: ***"Yes it's an upgrade, keep the covariance work going. The intention is to be done with the
  uncertainties before publication"***. **(a)** The quarantine gates ONE CLAIM UPGRADE — the joint high-`E_avail`/high-`W`
  generator deficit from central value to significance — **not the Letter as scoped**: `paper_body.tex:145-148` says
  *"Every non-two-dimensional result in this Letter is a central value… no superseded or historical covariance is used
  here."* **(b)** The dependency is nevertheless RETAINED; the covariance work is not stood down. **Both halves travel
  together** — "upgrade" naturally misreads as "can slip", and it cannot slip by default. What changes is the KIND of
  dependency: **elective, not structural**. The gap that would have collapsed (a): the Letter DOES quote a covariance at
  `paper_body.tex:53-55`, and it is `AGENTS.md:25`'s **VALIDATED** 2D standalone construction — every object the Letter
  quotes is VALIDATED, every quarantined object is one it declines to use. Found by the `claude-school` lane, re-read
  here. **Deliberately does NOT settle** whether `OI-172`'s note obligation reaches the Letter — that is ruled separately
  in `OI-187`'s row on a CODE-PATH argument, because this lane's artifact-scope reasoning was true but not sufficient.
- **PSCRATCH READ STALLS MAKE `A-2(b)` UNMEASURABLE — THE REDEPLOY IS BLOCKED BY A FILESYSTEM, NOT A DECISION, 2026-09-01:**
  [`FINDING-20260901-pscratch-read-stalls-block-a2b.md`](FINDING-20260901-pscratch-read-stalls-block-a2b.md)
  — `git status --porcelain` **does not return** on either cluster checkout, while `find` (1803 files), `git ls-files`
  (1804), `rev-parse`, `cat-file` and all metadata are **instant**. A complete per-file sweep — **1803 attempts,
  terminal marker written, so NOT a blind result** — found **10 files (0.55%)** whose content reads time out, ordinary
  small text files across four unrelated directories. **INTERMITTENT, and an earlier reading of it as a dead Lustre
  target is CORRECTED here:** two of the ten later read clean twice. **And it is worsening** — the sweep got `rc=124`
  where the retest gets no return at all, i.e. **uninterruptible sleep, where `timeout` cannot interrupt its own
  child**; that is also what has held another lane's processes for **2 h 30 m+**. **THE CONSEQUENCE:** `A-2(b)` is
  `dirty_count` from exactly that command, so round-2 `F-1(b)` cannot be filed by the precedent route, so
  `FREEZE-20260830-k0-deployment-7ac0edec.md` §1 cannot expire, so the authorized redeploy cannot proceed. **No
  substitute measurement is offered and none should be improvised.** §5: three of the ten are executable science
  inputs, so the tree is **unsafe to launch from** independently of the freeze. §6 carries the method caution both
  lanes nearly fell for — **an empty sweep result is not a negative result** — with the two rules that follow. Already
  banked and not to be redone: A-2(a) is taken (raw sha in `.git/HEAD`, DETACHED), and bundle-alone recovery of
  `7ac0edec` passes **all six** declared checks. Authorizes nothing; **Gate 2 remains FAIL**.
- **THE REDEPLOY'S PRECONDITION DELTA, AND A CORRECTION ON WHEN THE OTHER EIGHT ARMS BREAK, 2026-09-01:**
  [`FINDING-20260901-k0r2-redeploy-precondition-delta.md`](FINDING-20260901-k0r2-redeploy-precondition-delta.md)
  — the measurement `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §2's *"and reconcile the other issues"*
  obliges. **All eight k=0 launchers gained one fail-closed requirement at `865b42d7`** — `MNV_ENV_PROVENANCE`, refusing
  both unset AND set-but-empty (`:?`), needing a baseline emitted by `mnv_env_provenance.py --emit` **before** the first
  `sbatch`, with no default by design. Per-launcher line numbers in §2; **`sbatch_finalize_5d_bkgaware_gpu.sh` is in the
  set, so leg 6's preconditions move too.** **THE CORRECTION:** this lane had reported a **submit-time** refusal. Wrong,
  and wrong in the direction that UNDERSTATES the hazard — `sbatch` does not evaluate the body, so a launcher with the
  variable unset **submits cleanly and every task then dies on the node**, `OI-179` round 1's exact shape. §3's residual
  gap is stated rather than left implied: **no submit-time gate exists**, confirmed with the enforcing lane; *"defect 3
  is enforced"* must not be read as "caught before jobs queue". §4 resolves eight of the ninth launcher's nine `MNV_*`
  values from `submission-environment-round2.txt` — the values the 374/374 run actually used, not proposals — and flags
  that **the same file's `MNV_EST_SEED_OFFSET=0` line is a TRAP**: the estimator-seed launcher refuses at `:154-157` if
  that variable is set at all. §5 keeps three items genuinely OPEN as rulings, not lookups: the `RUN_ID` and its two
  run-scoped paths; what `MNV_ENV_PROVENANCE` points at, since round 2 used a hand-written file and `--emit` did not yet
  exist; and whether a ninth arm may share the completed run's `RUN_ID` at all. §6 is marked SECOND-HAND — recovered
  from a credit-exhausted delegate's log, re-measure before citing. Authorizes no submission; **Gate 2 remains FAIL**.
- **JOSEPH AUTHORIZES THE k=0 REDEPLOY `7ac0edec` → `main`, AND THE ORDER IS PART OF THE RULING, 2026-09-01:**
  [`DECISION-20260901-joseph-authorizes-k0r2-redeploy.md`](DECISION-20260901-joseph-authorizes-k0r2-redeploy.md)
  — Joseph, his own turn: ***"Yes redeploy it and reconcile the other issues"***. **The deployed tree
  `/pscratch/sd/j/josephrb/k0r2/clean` may advance from `7ac0edec` to ONE NAMED COMMIT** — a sha, never the definite
  description *"current `main`"*, which re-points the moment `main` moves (it moved `83666a09`→`050dbb72` inside one
  peer session). **THE ORDERING CONSTRAINT IS PART OF THE RULING AND MUST TRAVEL WITH IT:**
  `FREEZE-20260830-k0-deployment-7ac0edec.md` §1 is **LIVE** — its expiry is *"when that rehearsal's F-1(b) producer
  filing is committed — not when its jobs merely look terminal"*, and **no round-2 filing exists**
  (`RECEIPT-20260830-k0-f1b-producer-filing.md` is scoped by its own box to `aa67c426`). So the round-2 F-1(b) is filed
  FIRST, the freeze expires on its own terms, and only then does the authorization take effect. **This record must NOT
  be cited to cut a live hold short**, nor to refuse a future Joseph-level `OI-123` supersession — the independently
  checked limb is *"no COMMITTED route existed at the time of the check"*, deliberately narrower than "nothing else can
  expire it". Rationale: moving first destroys the far end of a completed **374/374, zero-failure, ~36 h** run,
  recoverable only by re-running everything. §5a carries the preservation prerequisites MEASURED read-only before the
  move — freeze ref present in BOTH repos, bundle `82,761,577 B` / `514bd46e…`, `list-heads` exact-row count 1 — and the
  terminality measurement with its covering control (374 measured reconciles with 374 declared, closing the `sacct -X`
  promoted-task hazard). §7 states plainly that **this record goes back in front of him**, because a lane that receives
  an authorization and rewrites its timing has ratified its own drafting. Authorizes NO submission, no leg 6, no M(ii),
  no adoption; **Gate 2 remains FAIL**.
- **JOSEPH RULES THE TWO MAGNITUDE LEGS — `OI-172` AND `OI-173`, 2026-09-01:**
  [`DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md`](DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md)
  — Joseph in his own turn, directly, not relayed: ***"Okay I agree with your recommendations, I authorize you spend the
  hours and drafting to investigate and fix the causes"***. **Ruling 1 (`OI-172`, cause 1's `M`): MATERIAL ENOUGH TO NEED
  ITS OWN STATEMENT IN THE NOTE — so CAUSE 1 DOES NOT CLOSE and the note acquires a new obligation.** The unfavourable
  branch, which the row named first. Grounds: the trace moves `3.1%`/`5.9%` while per-band ratios run median `2.0261`,
  p90 `4.3256`, max `5.8024`; the effect CHANGES SIGN (`MaCCQE` ep0 `0.6377`, `MaRES` ep1 `0.6111` are understated, so a
  consumer assuming conservatism is wrong on those bands); and the supporting measurement is diagonal-only with `Flux`,
  `2p2h` and `__Normalization_flat` excluded. **Ruling 2 (`OI-173`, cause 4's `M`): specify `M` against the class of
  object the defect actually REACHED — the reported ratio, not the stored covariance — and if the printed `jit_trace` is
  unrecoverable then `M` is NOT MET (unmeasured), NOT `N/A`.** Follows `SCOREBOARD` §2c's rule *"do not let measurability
  choose the specification"*, and explicitly REFUSES the available `N/A`-on-the-merits shortcut, whose payoff would be its
  own premise. **The recommendations are this lane's and are restated verbatim in the record so nobody mistakes them for
  his reasoning; he adopted the conclusions.** Discharges nothing, adopts nothing, moves no gate; cause 4's `M` becomes
  SPECIFIED, not satisfied, and may yet grade NOT MET.
- **JOSEPH RE-ISSUES `OI-173` — THE `M` REFERENT IS THE STAMPED CANDIDATE, 2026-09-02:**
  [`DECISION-20260902-joseph-rules-oi173-referent-is-the-candidate.md`](DECISION-20260902-joseph-rules-oi173-referent-is-the-candidate.md)
  — Joseph in his own turn, directly, not relayed: ***"okay do c"***, where `(c)` is the `5d` lane's *"`M` is specified
  against the reported ratio of the STAMPED CANDIDATE"*. **Supersedes the referent of Ruling 2 above and NOTHING ELSE of
  it** — the class is still the reported ratio, the `N/A` shortcut is still REFUSED, no recomputation is authorized.
  **He authorized a different branch first and it is recorded rather than omitted:** *"Can you do (a)?"* aimed `M` at the
  ADOPTED artifact; implementation halted on the `5d` objection and nothing under `(a)` was ever committed. **Why `(a)`
  was wrong — TWO CORRECT RULINGS COMPOSING INTO A DEFECT:** `DECISION-20260831` §1 fixes the SUBJECT (the stamped
  candidate), Ruling 2 fixes the REFERENT CLASS, and the pair left `M` pointed at an object the framework does not grade.
  Three objects existed and the choice put to him had two. **The measurement, replacing a refuted one:** no committed
  revision of `unified_throw_cov.py` holds BOTH the jitter print and the J28 flux fix — `081ae4ac` modifies that file
  itself with `grep -c` `0`, and `merge-base --is-ancestor 07c18aee 081ae4ac` is TRUE — so a tree old enough to print the
  floor cannot produce the candidate's input. The earlier stamp-based route is REFUTED because `git log -S` dates the
  oldest COMMIT, not the oldest EXISTENCE (`VALIDATION_LEDGER.md:484`). **THE GRADE IS DERIVED AND ROUTED, NOT APPLIED:**
  the chain yields `NOT MET (unmeasured)`, but this lane took the measurement so `BEN-381` routes the regrade; the cell
  stays `OPEN`, counts hold at CAND `1 of 7` / QUOTED `0 of 7`, **Gate 2 remains FAIL**, and Reading B is left undisposed.
  **A covering log sweep must NOT be launched for this.**
- **THE SUPPORTING ANALYSIS FOR THE `OI-173` RE-ISSUE — the `5d` lane's, adopted unchanged, 2026-09-02:**
  [`PROPOSAL-20260902-oi173-reissue-cause4-M-referent.md`](PROPOSAL-20260902-oi173-reissue-cause4-M-referent.md)
  — filed under its own lane's authorship because it reached the third-object problem independently and first, and
  because its **drafting history is the useful artifact**: §3a retracts that lane's stamp inference on the other lane's
  counterexample, §3b restores the conclusion on the flux-fix route with that lane's same-file strengthening, and the
  chain paragraph retracts a universal on the near-miss at `adopt_unified_5d.py:158-160,177-178` (a sqrt-trace ratio IS
  printed and persisted downstream — a different quantity, adopted-combined across inflation, with no `jit_trace` in its
  path). Three corrections across two lanes, each retracted in place rather than deleted. §5 records BOTH live readings
  at their real strength, including the one neither lane could refute. **Grades nothing and moves no cell.**
- **JOSEPH OVERRIDES THE INDEPENDENCE OBJECTION; THE CAND `M` CELL IS ANNOTATED, 2026-09-02:**
  [`DECISION-20260902-joseph-applies-oi173-cause4-m.md`](DECISION-20260902-joseph-applies-oi173-cause4-m.md)
  — Joseph, directly to the `5d` lane with the two-lane consensus and its objection in front of him: ***"apply it"***.
  **The lanes had declined on INDEPENDENCE, NOT authority** — `BEN-381` is a property of who measured, and being named
  by the authority does not confer it; it names the two parties who lack it. **The disclosure is on the record rather
  than left to be discovered:** the applying lane verified the same-file dependency the argument turns on, so the grade
  is weaker for who applied it and a reader should discount it on that ground. **WHAT MOVED — one annotation, at
  `SCOREBOARD-20260817-quarantine-seven-causes.md:78`, CAND column only.** The token stays **`OPEN`**:
  `CRITERIA-20260811:246` defines `MET`/`OPEN`/`UNRESOLVED`, Joseph's *"`NOT MET` (unmeasured)"* is not among them, and
  a fourth token is a `§0` change and his call. Discharge needs four `MET`s either way, so nothing rides on the token
  but meaning — and `OPEN` refuses `N/A` exactly as `NOT MET` would. **What the cell gains is the PERMANENCE and its
  ground:** no **committed** revision of `unified_throw_cov.py` holds both the jitter print and the flux fix, so no
  revision able to produce CAND's fluxfix input could print the unified/block ratio. **A VOCABULARY GAP IS FLAGGED, NOT
  PAPERED OVER** — `OPEN` normally means *awaiting work* and is here annotated to mean *permanently unmeetable*.
  **THIS SUPERSEDES A CONSIDERED REFUSAL, not an empty cell:** `SCOREBOARD` §3 (`:568`) declined this exact cell at
  `:670` — *"the cell stays `OPEN` and I am declining to move it in either direction"* — on a SEARCH-BASED null
  (`:606`/`:609`). What changed is the GROUND, from an empty search to committed bytes with a positive control, so the
  refusal is superseded on evidence rather than overruled on authority. **A NEAR-MISS CAUGHT BY THE `-38` LANE:** `5d`
  had claimed `CRITERIA-20260811:257` in writing, but `:244` reads *"Honest state per cause, **for X**"* and `:341`
  carves out only the `P` legs — that cell is X's, and editing it would have been the
  adopted-artifact-versus-candidate error one layer down, the same error the `OI-173` re-issue existed to correct.
  **AND THE TWO CONTROL DOCUMENTS DISAGREE ABOUT THIS LEG:** `CRITERIA:257` grades it `UNRESOLVED`, `SCOREBOARD:78`
  grades it `OPEN`, and `:246` makes those distinct. **Left standing**, filed as a finding owned by neither lane.
  **Counts unchanged:** CAND `1 of 7`, QUOTED `0 of 7`; **Gate 2 FAIL**; cause 4's verdict untouched and still jointly
  gated on the provenance residual; the historical-ratio reading still undisposed; nothing adopted, `values.tex`
  untouched.

- **JOSEPH RULES `CRITERIA` §0'S VOCABULARY STANDS — NO FOURTH GRADE TOKEN, 2026-09-02:**
  [`DECISION-20260902-joseph-rules-no-fourth-grade-token.md`](DECISION-20260902-joseph-rules-no-fourth-grade-token.md)
  — ***"okay I also agree"***. `MET`/`OPEN`/`UNRESOLVED` and discharge-on-four-`MET`s are unchanged; the
  *permanently unmeetable* state is carried in cell prose by the annotation convention instead.
  **A CENSUS DECIDED IT, AND IT WAS RUN BEFORE THE RULING RATHER THAN AFTER** — the enumeration was first offered as
  the COST of ruling for a token and was re-framed as the INPUT to it, on the ground that the case for a token is
  empirical. Filed `0d946c1a`, amended `ac846f37`, **verified against the bytes by the `5d` lane** including column
  mapping, every hit, both exclusions and the denominator. **46** graded cells; bucket (i) permanence carried in the
  cell = **1**; bucket (ii) permanence asserted but cell bare = **4**. **THE SHAPE, NOT THE COUNT, DEFEATED THE
  TOKEN:** by the pre-set rule 4 is "several" and the token had a case — and the census lane reported that against
  its own stated lean — but all four are the QUOTED-side `P` legs of causes 2/3/4 under ONE statement at
  `SCOREBOARD:5`, in a warning box preceding every cell. **Harm is grep-scale, not read-scale**, and the population
  a token would uniquely help that nothing else covers is **ONE**, already annotated. **The census's own NEGATIVE
  CONTROL is the strongest evidence:** `:74` reads *"`OPEN` and NOT CURRENTLY MEASURABLE"*, costed and temporary on
  its face — the board already distinguishes temporary from permanent in cell language. **No code parses any token**,
  so a token buys convention not enforcement; and the scheme **declares three and runs seven**, so a fourth patches
  the smallest leak. **TWO THINGS DEFERRED OR ROUTED, both stated so they do not evaporate:** the agreed pointer
  remedy is NOT applied, because annotating exactly the four `P` cells would silently settle whether §1's permanence
  claim is `P`-scoped or column-wide — `:5` says "the QUOTED COLUMN" with an artifact-level mechanism, which would
  also reach `:69` and `:78`-QUOTED — and settling that is a grade on a cause-4 leg, beyond both measuring lanes
  under `BEN-381`; and `SCOREBOARD:73`'s premise *"value CANNOT be recorded on the dominant arm"* is **FALSE at
  HEAD**, four write sites existing, which is a live board asserting an untrue impossibility and needs its own route.
  **Counts unchanged:** CAND `1 of 7`, QUOTED `0 of 7`; Gate 2 FAIL; nothing graded, adopted, or discharged.

- **A MERGE-GUARD REFUSAL IS TERMINAL AND NO AUTHORIZER CONVERTS IT INTO A PASS — Joseph's rule, 2026-09-08:**
  [`RULING-20260908-joseph-a-merge-guard-refusal-is-terminal.md`](RULING-20260908-joseph-a-merge-guard-refusal-is-terminal.md)
  — a guard's exit is a **fact about the tree**; an authorization is a **permission about an act**; permissions govern
  acts, not measurements, so an override treats a permission as if it changed a fact. **Terminal for the override,
  never for the task:** remove the cause and re-run, or fix the gate — reviewable, dated, and it protects the next
  operator rather than one merge. `merge_guard.sh` has **no override input**, by design. **Report which EXIT, because
  "the guard refused" is underspecified:** `whose_row.py` exit `1` covers *foreign* (relievable only by that row's named
  author, or Joseph) and *unattributable* (where a **generated**-file conflict lands) through ONE branch and ONE summary
  line in `main`, guarded by `if args.lane and (foreign or unattributable):` — **that expression, colon included, is the
  citation, and it occurs exactly once in the file** (without the colon it also matches a comment recording BEN-117's
  empty-`--lane` defect). This entry previously read `:850-857`; the clean-merge insertions of 2026-09-08
  moved the block and no line number moved with it, so **grep the expression** rather than trusting a number, here or
  in any successor of this entry.
  Exits `2` (attribution examined nothing, or a clean merge **could not be verified** — an inability counts) and `3`
  (its own self-test failed) are authorizable by **nobody**. For
  a generated-file conflict the file is the symptom and the generators disagreeing is the event — **regenerate from the
  merged sources and re-run the gate**; `MANIFEST.tsv` carries a row describing its own line and byte count, so it
  conflicts on every concurrent merge **by construction**. Occasioned by an override at `a1fc54ed` whose *resolution*
  was verified byte-identical to the generator's output — **right answer, wrong route, and the right route was a
  three-second command available at the time.**

- **THE `QUOTED`-COLUMN PERMANENCE CLAIM IS `P`-SCOPED, NOT COLUMN-WIDE — the clean-lane ruling the pointer remedy waited on, 2026-09-02:**
  [`RULING-20260902-quoted-column-permanence-is-p-scoped.md`](RULING-20260902-quoted-column-permanence-is-p-scoped.md)
  — `SCOREBOARD:5`'s *"THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION"* binds the QUOTED-side `P` legs of causes 2/3/4
  (`:68`, `:72`, `:73`, `:77`) **and nothing else**; it does not reach `:69` or `:78`-QUOTED. Bucket (ii) stays **4**,
  not 6, so `DECISION-20260902-joseph-rules-no-fourth-grade-token` §4's deferral is discharged and its §1/§5 are
  undisturbed. **ONE GROUND CARRIES IT AND IT IS TEXTUAL:** §1 states its premise over `P` cells at `:134` (*"Every
  `P` cell in the QUOTED column is `OPEN` for one reason"*) and draws its conclusion over the column at `:143`, nine
  lines apart in its own section. §1 is fourteen lines and has **exactly one premise and one measurement, both
  `P`/stamp-scoped**; the wide phrasing at `:5`, `:132` and `:143` is one conclusion stated three times, and
  repetition is not evidence. **AUTHORITY IS BOUNDED AND SAYS SO:** the scope determination is the ruling lane's;
  Joseph authorized the filing (*"route it to me"*, *"Do your recommendations"*) and did **not** separately
  adjudicate the question — §0 states this so the record cannot be cited as his ruling. **ADVERSARIALLY REVIEWED
  OVER SEVEN ROUNDS by both `BEN-381`-recused lanes, neither of which endorses the conclusion:** two grounds were
  WITHDRAWN — a build-time/reader-side criterion, refuted because `§0:49` gives `P` three routes (*"stamp, receipt
  **or hash**"*), and `CRITERIA:341` as a leg-wise partition, which its own author confirmed was the narrow form —
  one rewritten, one restated to **stamp** scope, a finding trimmed twice, one corrected outright, and **the
  load-bearing ground was missing from the document until the `38` lane found it** after a line-by-line verification
  pass had cleared it. **FIVE FINDINGS ROUTED, NONE RESOLVED, all beyond the ruling lane's recusal** — chiefly (a)
  `CRITERIA §3:255` grades cause 2's `M` **MET** for X on `5.3478×` while `SCOREBOARD:69` files that same number and
  BEN id under **CAND** with QUOTED bare `OPEN`, and (d) `DECISION-20260831 §2(b)` is headed *"the provenance leg is
  unsatisfiable IN PRINCIPLE"* but argues **only stamps**, which is the same defect one level down in the document
  supplying §1's authority — surfaced, **not** filed against a ruling Joseph confirmed. **Counts unchanged:** CAND
  `1 of 7`, QUOTED `0 of 7`; Gate 2 FAIL; nothing graded, adopted or discharged; `values.tex` untouched.

- **THE TWO-LANE CONSENSUS ON CAUSE 4's `M`, AND ITS SUPERSESSION WITHIN THE HOUR, 2026-09-02:**
  [`DECISION-20260902-two-lane-consensus-cause4-M-and-its-supersession.md`](DECISION-20260902-two-lane-consensus-cause4-M-and-its-supersession.md)
  — filed under Joseph's **PROSPECTIVE** approval, *"I want you guys to come to a consensus and I approve that
  resolution"*, which is flagged at the top of the record because **he approved content that did not exist when he
  approved it**: every word is the two lanes' and none of it is his reasoning. **§3.1 IS SUPERSEDED IN FACT** — the
  consensus was that the cell does not move, he overrode within the hour, and the record is filed with the reversal
  visible rather than rewritten. **On `BEN-381`:** he HAD the authority and this record must not be cited for saying
  otherwise; the lanes declined on **independence**, which is a property of who measured and cannot be conferred
  retroactively — *he MAY, and the lanes said he SHOULD NOT*. He then overrode it knowingly, so the grade is weaker for
  having been applied by a measuring lane. **Carries the four binding constraints on any future application** — the
  vocabulary limit; that `CRITERIA` §3's table is **X's** (`:244`, `:341`) so the candidate cell is `SCOREBOARD:78`;
  that the verdict is jointly gated and does not clear on `M`; and the `5d` lane's artifact-bound-versus-artifact-free
  argument **recorded and deliberately not applied**. **§5 is a FINDING owned by neither lane:** the grading scheme is
  declared at three tokens (`CRITERIA:246`) and is running six — `PARTIAL` (5 uses) was never declared and `N/A` appears
  in three spellings — while **no code parses any of them**, so the scheme is purely communicative and the
  `CRITERIA:257`-versus-`SCOREBOARD:78` split on one leg stands unresolved. Discharges nothing, moves no cell, changes
  no count; **Gate 2 remains FAIL**.
- **PERMANENCE-LANGUAGE CENSUS OVER THE LEG-GRADE CELLS — commissioned to DECIDE the fourth-token question, 2026-09-02:**
  [`CENSUS-20260902-permanence-language-in-leg-grade-cells.md`](CENSUS-20260902-permanence-language-in-leg-grade-cells.md)
  — Joseph: *"yes do it"*. **The framing inverted mid-question and that is the point of the record:** enumeration was
  first put to him as the COST of adding a fourth grading token and was re-put as the INPUT to the ruling, so the census
  decides rather than follows. **Result: 46 graded cells; 1 asserts permanence AND carries it in the cell
  (`SCOREBOARD:78`, cause 4 `M` CAND — the mandated positive control, and the search returned it); 4 assert permanence
  only elsewhere in the record while reading bare `OPEN` (`:68`, `:72`, `:73`, `:77` — all the QUOTED `P` leg, governed
  by `:5`/`:143` "THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION").** By the pre-set decision rule `4` is "several" and the
  fourth token has an empirical case — **but the four are one column under one statement made twice and prominently, so
  the harm is grep-scale rather than read-scale, and the population a fourth token would help that nothing else covers
  is ONE, already annotated.** Reported by the lane that had argued FOR the token, against its own position. **Carries
  its exclusions with reasons** — cause 1 and cause 6 are carved out by `:102-106`; cause 3's `P-ii` says "CANNOT" but
  names a remedy **and its premise was measured FALSE at HEAD**; cause 3's `M` reads "NOT CURRENTLY MEASURABLE", which is
  the census's own negative control that the board already distinguishes temporary from permanent. Also corrects this
  lane's earlier "six tokens" to **seven**. **Grades nothing, moves no cell, changes no count; Gate 2 remains FAIL.**
- **THE `P` LEG IS ALREADY SATISFIED AND `M` IS THE BLOCKER — §4.2 DISSOLVED, 2026-09-01:**
  [`FINDING-20260901-p-leg-status-measured-against-the-candidate.md`](FINDING-20260901-p-leg-status-measured-against-the-candidate.md)
  — `CRITERIA-20260811` §4.2 says the `P` leg of causes 1–4 is *"currently unsatisfiable from the repository"* and
  proposes its own remedy: *"the cheap fix is a receipt, not a re-run."* **That receipt was written 2026-08-17 and is
  committed; nobody marked §4.2 satisfied.** Measured off three tracked, predeclared receipts: cause 1 `P` **MET**
  (branch `C1`, per-band census, `Flux` exactly 100 contiguous); causes 3 and 4 `P` **MET FOR THE CANDIDATE**
  (branch `S1`, both arms carrying all six self-checked stamps and all three `upstream_*` values, zero mismatches)
  **while both July negative controls returned every stamp ABSENT** — `(cause × artifact)` scoping working as §0
  describes. **Neither receipt discharges anything, and both say the blocker is `M` in their own words.** So
  `OI-172` and `OI-173` are not parallel blockers but the `M` leg itself, confirming the `claude-school` lane's
  ordering over this lane's. Remaining: cause 1 → `OI-172` (free); cause 3 → `M(ii)` needs its own measurement,
  **~1 GPU-node-hour**; cause 4 → `OI-173` (free); **cause 7 has NO criteria at all** and needs them written.
- **THE F7 PREDECLARED TEST, MEASURED ON THE CANDIDATE — MEAN-CENTERING ALONE IS DISQUALIFIED THERE TOO, 2026-09-01:**
  [`FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md`](FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md)
  — Run to settle whether [`BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md`](BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md)
  §4 opens a route to redefining the 5D central value as an ensemble mean. **It does not.** `uq_math.py:119-138`
  carries the F7 rule PREDECLARED in `CORRECTED_UQ_PRODUCTION_STATUS.md` before the data: `||mean_shift||` against
  the sampling floor `sqrt(Tr C)/sqrt(N)`, threshold `F7_FLOOR_MULTIPLE = 2.0`. **Measured on
  `stamped_bkgaware_meancentered_20260812.root`'s stamps: `4.510x` the floor, `f7_cv_centered_required` = `True`**
  — *corrected same day by the `claude-school` lane: `4.510x` pairs the UPSTREAM shift with the candidate's
  `sqrt_tr_new`, so it is not like-for-like; the adopted-ensemble ratio is `VALIDATION_LEDGER.md:390` VL33's
  **`5.3478x`**, and the candidate carries no mean shift of its own. Verdict unchanged: `5.3478 > 4.8288 > 4.510 > 2.0`*
  — so the disqualification covers the CANDIDATE, not only the July artifact, which independently supports cause 2's
  2026-08-12 discharge having REQUIRED the CV-centered variant. **The Greif analogy fails at the ensembles:** he centers
  over a bootstrap/seed family, our shift is against the joint **systematic throw** family
  (`unified_throw_cov.py:288`), and averaging systematic throws into a central value is not what the thesis does.
  A 24-member seed-ensemble pull (median `0.588` vs the 3D reference `0.63`, on a `cv>0` support of exactly `10694`)
  **removes ML stochasticity as the offset's cause rather than supporting the redefinition.** Scope limits stated:
  `ssplit5d` varies the train/test split ONLY (`estimator_seed=42` throughout), so no scan anywhere varies both; these
  are REHEARSAL products, measurable but not quotable. **Records a statistic deliberately NOT computed** — an ad-hoc
  per-bin throw pull — because a predeclared test governs and choosing a statistic after seeing the data is the
  failure mode this campaign files against others. **Corrects this lane's own withdrawn `28%`-of-`sqrt(Tr C)` heuristic,
  which used the wrong denominator and pointed the opposite way.** Discharges nothing, moves no gate; `OI-186` files a
  `7%` gap between `uq_math`'s comment and the artifact's stamps.
- **THE DELEGATED COMPUTE CEILING IS DENOMINATED IN TASK-HOURS, 2026-09-01:**
  [`DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`](DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md)
  — Joseph, in his own turn, asked directly which unit the standing per-arm ceiling uses: ***"It is task
  hours"***. The `500 GPU-h / 500 CPU-h` delegation was written unqualified, and arm 5 of the k=0 round-2
  rehearsal reconciles **only under one reading**: `49.11` task-hours (elapsed summed over 40 tasks) versus
  `2455.51` core-hours at `AllocCPUS=50`. **Under task-hours every one of the seven arms is far inside 500,
  the largest being 49.11**; under core-hours `uthrow5d_runF` and `uthrow5d_block` would each have breached
  the CPU delegation, by ~4.9× and ~2.7×. **They did not — the ruling resolves the wording in the direction
  the campaign's own arithmetic already assumed.** The distinction was known and simply never reached the
  delegation sentence: `SCOREBOARD-20260817:223` writes *"`55.182` CPU task-hours (`2759.1` CPU-core-hours)"*
  explicitly. **RATIFIES NOTHING** — `OI-177` stays OPEN and unsigned (§3's 40 CPU-h for arm 5 is dead on the
  49.11 actual; §3b's 60 awaits his signature), no gate moves, nothing is adopted, counts hold at CAND
  `1 of 7` / QUOTED `0 of 7`. **Carries one caveat forward:** `DEFECT-20260825:172-176` records the 500
  threshold as a Codex session's claim about its own authority and NOT Joseph speaking — this decision fixes
  its UNIT, not its provenance.
- **✅ `OI-179` DEFECT 3 ENFORCED ACROSS THE EIGHT k=0 LAUNCHERS, 2026-09-01 — `OI-179` DISCHARGED:**
  [`RECORD-20260901-oi179-defect3-enforced.md`](RECORD-20260901-oi179-defect3-enforced.md)
  — Joseph: ***"go ahead with defect-3 enforcement"***. `MNV_ENV_PROVENANCE` is now **mandatory with no
  default** in all eight launchers, each task **records its own environment** (even when the check then
  fails), and every `MNV_*` the submission baseline DECLARES must have reached the task. Exit codes
  **propagated, not collapsed**: 2 could-not-look, 3 measured-drift. **The cost the 2026-08-31 shape was
  avoiding does not exist and this was measured before acting:** the pre-source loop compares against
  `HEAD` not a hardcoded digest, `verify_hash_bindings.py` reports ALL BINDINGS INTACT with **none of the
  eight bound by an active run receipt**, and each `--pair` set already includes itself — **no `OI-123`
  supersession**. **THREE ASSERTIONS WERE WRITTEN AND REMOVED, each on a measurement rather than because a
  test was inconvenient:** search paths cannot be asserted (probe job `57819105` measured a compute node's
  pre-activation environment byte-identical to the login node's, but its `/usr/bin/python3` is **3.6.15**
  and the tool needs 3.7+, so the check cannot run where the comparison would be exact); **HOME** cannot be
  asserted (six launchers set `--export=ALL,HOME=…` and three re-export it, so asserting it would have made
  three **refuse themselves** on every correct run); and an **added `MNV_*` is what activation does**. All
  three are reported as observations. ~~**64/64** in `test_k0_launcher_two_roots.py`~~ **— CORRECTED 2026-09-01: that run collected
  33.** `unittest.main()` sat at line 853 of 1325 with three classes after it, so direct execution
  skipped 31 tests and still printed `OK`; 64 was a count of `def test_` lines, not of the runner's
  report. Placement fixed; the file now genuinely reports **Ran 64 … OK** and all 31 pass. Census
  suite **25/25** (was 13/13, extended under `OI-185`), **25** self-test arms in the tool. All eight parse under the **real target interpreter, bash
  4.4.23 on saul**. **⚠ ONE CONSEQUENCE IS ROUTED TO JOSEPH AS `OI-185` RATHER THAN ABSORBED:** ruling 21's
  guarding boundary moves **14/30 → 14/38** (guarded unchanged at 14, unclassified at 0). The census
  **fired** rather than absorbing it, which is `F-7(a)`'s complaint answered. **MOVES NO GATE:** Gate 2
  remains FAIL, leg 6 prohibited, nothing adopted, nothing submitted, CAND `1 of 7` / QUOTED `0 of 7`.
- **🔎 CAUSE 4's JITTER FLOOR RECOVERED, 2026-09-01 — AND THE LEDGER'S `1.539` DESCRIBES A DELETED
  PRODUCT:**
  [`FINDING-20260901-cause4-jitter-floor-recovered.md`](FINDING-20260901-cause4-jitter-floor-recovered.md)
  — Joseph authorized the measurement he had left unowned (***"You can take it"***). **`jit_trace =
  3.731e-78`**, with the full print block `raw ratio=1.541` / `corrected ratio=1.539`, so **the
  magnitude of cause 4's defect on the reported ratio is −0.11%**. Every printed number re-derives from
  its printed operands, four for four. Recovered from the one surviving scratch log Lane D found at
  `8a6cf176` and warned was perishable; it survived 15 more days and is now durable at
  `state/RECEIPT-20260901-cause4-jitter-floor-recovered.json`, whose transcript **re-hashes to the
  cluster-measured sha256**. **⚠ THE LARGER FINDING: the recovered numbers belong to a product that no
  longer exists.** That run wrote `uq_5d/unified_throw_cov_5d.root`; the path's current occupant is
  2.68 GB at `2026-07-13`, twelve days later. The adopted ROOT's own committed operands give a **raw**
  sqrt-trace ratio of **1.3107**, and a corrected ratio can never exceed its raw one — so
  `VALIDATION_LEDGER.md:1192` prints a superseded occupant's number under the adopted product's name.
  **A CONVENIENT ALTERNATIVE READING WAS REFUTED BY THE MEASUREMENT** and is recorded as such: the only
  arithmetically-possible reading beforehand was a *trace* ratio, under which the value inverted
  cleanly — the log shows it is a *sqrt-trace* ratio, and adopting the other would have been
  measurability choosing the specification. **GRADES NOTHING:** the `M` cell is not moved, Gate 2
  remains FAIL, CAND `1 of 7` / QUOTED `0 of 7`. Read-only throughout — isolated worktree exited clean,
  three read-only cluster reads, nothing on the cluster mutated.
- **✅ JOSEPH RATIFIES `OI-185`, 2026-09-01 — `OI-185` DISCHARGED, THE BOUNDARY STANDS AT 14/38 AND THE
  AUTHORED TOTALS ARE GONE:**
  [`DECISION-20260901-joseph-ratifies-oi185-invariants.md`](DECISION-20260901-joseph-ratifies-oi185-invariants.md)
  — Joseph, in his own turn: ***"Okay I like your recommendation for OI-185, do it"***. **The record
  reproduces the accepted recommendation VERBATIM**, because a ruling of that form takes 100% of its content
  from the recommendation and a later summary would let the producing lane set the scope of his ruling after
  the fact. **BOTH HALVES SHIPPED. (1)** ruling 21's boundary is ratified at **14 guarded / 38**. **(2)** the
  four authored totals — `excluded_preflight` 24, `non_comment_python3_invocations` 54,
  `inline_interpreter_probes` 16, `launchers` 8 — are **REMOVED, NOT BUMPED**; the census derives and prints
  them. **THREE PINS SURVIVE:** `guarded == 14` (ruling 21's actual subject), `unclassified == 0`, and
  `commented_out_python3_lines == 18` — the last a TRIPWIRE deliberately left pinned, since the ruling
  authorized de-pinning the BOUNDARY totals and nothing else. Schema `mnv_preflight_exclusions/1 → /2`, and a
  v1 declaration is now **refused as could-not-look** rather than read under v2 semantics. **NEW ENFORCEMENT:**
  every declared exclusion must be structurally complete, resolve to its declared path, appear exactly
  `per_launcher` times, and be **A-3 `--pair` bound in every launcher** — the last was true of all three tools
  and asserted by nobody, which is `F-7(a)`'s complaint about the exclusion itself. **✅ THE ONE DEPARTURE FROM THE
  RATIFIED WORDS IS RESOLVED (§4) — Joseph, 2026-09-01: *"I don't think I meant it literally"*, so the
  shipped criterion stands and no code changed. AS DISCLOSED BEFORE HE RULED:** the recommendation gave the ground as *"imports only the
  standard library"*, and **implemented literally that is unsatisfiable by the set ruling 21 already
  accepted** — measured, `mnv_source_manifest.py` has `repo_origin_count` **1**, importing `MARKERS,
  is_checkout` from `mnv_guarded_run` itself. A stdlib-only rule would have fired on a ratified entry **on
  every correct tree**. The rule was **not relaxed to fit**; the question was restated to the CIRCULARITY
  ground the declaration always gave, made falsifiable as *repository imports ⊆ {`mnv_guarded_run`}* — broader
  than the ratified words **by exactly one module** — disclosed before the ruling, and ratified by it. **THE PROMISE IS NOW TWO TESTS:** a
  principled fourth preflight tool passes with no ruling (boundary 46, `guarded` still 14) and the same
  launcher bytes without the declaration entry still fail. Census suite **25/25**, up from 13. **NO LAUNCHER
  WAS EDITED** — no `F-14`/§7.0.7 coupling, no `OI-123` supersession. **MOVES NO GATE:** Gate 2 remains FAIL,
  nothing adopted, CAND `1 of 7` / QUOTED `0 of 7`.
- **✅ JOSEPH RATIFIES THE `OI-177` PER-ARM CEILINGS, 2026-09-01 — `OI-177` DISCHARGED:**
  [`DECISION-20260901-joseph-ratifies-oi177-per-arm-ceilings.md`](DECISION-20260901-joseph-ratifies-oi177-per-arm-ceilings.md)
  — Joseph, in his own turn: ***"I sign"***. **RATIFIED, in task-hours:** arm 2 seed split **8 CPU** (+3),
  arm 5 uthrow run **60 CPU** (+30), arm 6 uthrow block **40 CPU** (+10); arms 1, 3, 4 and 7 unchanged at
  20 GPU / 20 GPU / 30 GPU / 5 CPU. **Sums 70 GPU / 113 CPU**, up from `PROPOSAL-20260830` §6's 70/70.
  **Every ratified ceiling exceeds BOTH observed actuals on its own arm** — checked per arm, not on the
  sums, since a sum can hold while a member is breached. Basis is **n=2 complete populations**:
  `aa67c426` (2026-08-24) and round 2 (374/374, zero failures, finished 2026-09-01T08:57:51Z), summed over
  DISTINCT task identities. **`PROPOSAL-20260830-forward-only-rehearsal.md` IS NOT EDITED** — `ARCHIVAL`,
  `terminal`, `immutable:yes`, 14 inbound refs; it stands as the 2026-08-30 record and is superseded by
  reference. **Three disclosures made BEFORE signature and carried into the discharge rather than dropped:**
  arm 6's `40` is the least well-supported of the three (its `+3.3%` round-over-round is two unlike
  distributions whose sums coincide — R1 `39.4/52.2/518.3` min against R2 `40.5/81.9/289.0`, R1's mean
  carried by one 8.6-hour outlier); arm 4 holds at 30 on the thinnest margin and was deliberately not
  proposed for change; and **a denominator correction** — arm 4's headroom was quoted as `12.4%` over the
  *ceiling* while the amendment's other headroom figures are over the *actual*, where it is `14.2%`.
  **The ceilings are set from the WORST OBSERVED REGIME, not a forecast:** §3c/§3e measure that
  CPU-partition arms reproduce in neither elapsed nor `TotalCPU` (arm 5 moved +58.7% and +50.4%), so a
  third run may exceed them — that would be a new `OI-*`, not a defect in this signature. **MOVES NO
  GATE:** Gate 2 remains FAIL, leg 6 stays prohibited, nothing is adopted, no compute is authorized,
  counts hold at CAND `1 of 7` / QUOTED `0 of 7`. Largest ceiling `60` against a `500` delegation
  threshold whose provenance caveat (`DEFECT-20260825:172-176`, not Joseph's words) still stands.
- **THE QUARANTINE IS GRADED AGAINST THE CANDIDATE, NOT THE JULY ARTIFACT, 2026-08-31:**
  [`DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md`](DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md)
  — Joseph: *"Okay it sounds like the correct ruling"*, *"Okay do that"*, and **confirmed directly to the
  recording lane as *"yes its my ruling"*** before the record was written. The seven causes are graded
  against `stamped_bkgaware_meancentered_20260812.root` (sha `4f168e83…`, CV `dbcd5359…`, job
  `56720356`). **`CRITERIA §0` already makes discharge a (cause × artifact) property** — *"a class has no
  construction… discharge for **which** matrix?"* — so choosing the subject is sanctioned, not a
  workaround. **Against X the provenance leg is unsatisfiable IN PRINCIPLE**, verified by measurement:
  the g2 input's mtime AND ctime are both `2026-07-13 02:15:41 −0700`, while `fixed_seed_null_norm`
  first enters git at `07c18aee` `2026-07-14 14:43:19 −0700` — the artifact predates its own stamping
  code by ~36.5 h and equal ctime rules out a restore, so no stamp for X can ever exist. **X IS
  RETAINED**: `adopt_unified_5d.py` opens the July product `RECREATE`, so deletion would do what that
  guard exists to prevent; X also backs `values.tex` today and is the only baseline against which the
  candidate's "flux fix alone" claim is checkable. Demotion only AFTER adoption and re-pointing.
  **ADOPTS NOTHING, discharges no cause, changes no count** — CAND `1 of 7`, QUOTED `0 of 7`; Gate 2
  remains **FAIL**. §6 corrects a withdrawn framing: `07c18aee` shows X was DELIBERATELY adopted, so
  nobody erred.
- **`OI-177` PER-ARM CEILINGS, AMENDMENT PREPARED FOR SIGNATURE, 2026-08-31:**
  [`AMENDMENT-20260831-oi177-per-arm-ceilings.md`](AMENDMENT-20260831-oi177-per-arm-ceilings.md)
  — **PREPARED, NOT RATIFIED; `OI-177` stays OPEN.** §6's estimate column is inherited verbatim from
  `PLAN-20260822-oneMember-mii-staged.md:220-224`, a 2026-08-22 prior, and §6's own detector row admits
  it is *"from the older 24-task population"* while declaring **19** tasks — an asymmetric comparison,
  not a slipped number. Measured `aa67c426` actuals over DISTINCT task identities, all seven
  populations complete: bootstrap **15.38** A100-h, seed split **5.43** CPU-h, detector **13.88**,
  sweep **25.54**, uthrow run **30.94**, uthrow block **30.01**, combine **0.42** — **total overrun
  1.38 CPU task-h**, reconciling with the row. Arm 5's prior underestimated by **45%**. Proposes
  minimal change: measured actuals into the estimate column, and raise only the **three** breached
  ceilings (2 → 8, 5 → 40, 6 → 40 CPU-h). Sums 70 GPU / 93 CPU, far under the strictly-under-500
  delegated thresholds. **Flags that ratifying on ONE run repeats the shape of the defect at lower
  severity** — round 2 will supply a second independent measurement of the identical arms, and holding
  costs nothing because the row blocks no gate. Moves no gate; Gate 2 remains **FAIL**.
- **THE GATE-THAT-CANNOT-FAIL AUDITOR IS BLIND ON 15 FILES, 2026-08-31 (`OI-180`):**
  [`FINDING-20260831-strip-noncode-inverts-on-a-closing-triple-quote.md`](FINDING-20260831-strip-noncode-inverts-on-a-closing-triple-quote.md)
  — `audit_gates_that_cannot_fail.py:59` reads a **closing** triple quote at line start as an
  **opening** docstring, so the terminator of an assigned multi-line string inverts the state machine
  for the rest of the file. Measured over 473 Python files: **15 lose more than half their code, 3,730
  non-blank lines invisible**, worst `test_k0_launcher_two_roots.py` at **5.0%** (978 → 49). **Not
  confined to fixtures** — `mii_adopt_unified_5d_stamped.py` 48.6% (an adoption path),
  `mii_root_payload_classes.py` 48.8%, `pet/cstat_data_only.py` 49.2%, `conftest.py` 41.6%. **So any
  0-hits over an affected file is unfounded.** CORRECTS the sibling finding's §1, which attributed the
  sweep's zero to the detector binding alone. **An authorized detector was written, passed 8-of-8
  power, and was deliberately NOT SHIPPED**: it returns 0 on the real file because the stripper already
  blanked its subject, and 170 REVIEW hits elsewhere — its power arm passed only because `run_power`
  feeds RAW lines, making fixture and reality different objects. Shipping it would have added a gate
  that cannot fail inside the instrument built to find them. Moves no gate; Gate 2 remains **FAIL**.
- **THE BEN-039 DETECTOR IS TRIPLE-BOUND, 2026-08-31:**
  [`FINDING-20260831-ben039-detector-is-triple-bound.md`](FINDING-20260831-ben039-detector-is-triple-bound.md)
  — `audit_gates_that_cannot_fail.py` is HEALTHY (`--power-only` rc 0, all seven detectors fire) and
  **blind to `OI-179` defect 2** (sweep grep returns 0). Bound on **three** axes, not one: span, left-hand
  vocabulary, and right-hand call shape. **Row 3 of its table is the proof** — supplying BEN-039's own
  `measured` vocabulary is STILL silent, because `self._ambient_prefixes()` is a method call and the
  pattern requires `.get(`. Positive control fires, so the nulls are evidence. **FOLDED INTO `OI-179`
  rather than filed as a new class**, on Joseph's delegation: the row's remaining open content already
  IS this, the class was named in 2026-08-07 as BEN-039, and a new `OI-*` or `BEN-*` ten-block costs the
  same freeness ceremony for a row that belongs to an open one. **The `mkdir` half is unreachable by any
  source-line detector**, so defect 3 becomes the only mechanism that can detect the class at all —
  load-bearing for two failures now. Supplies the acceptance criterion: any new detector must FIRE in
  `--power-only` on a reconstruction of pre-`b512760d` `good_env()`, or it is itself a gate that cannot
  fail inside the instrument built to find them. Moves no gate; Gate 2 remains **FAIL**.
- **THE `OI-179` REMEDIATION IS CONFIRMED IN A REAL SCHEDULED JOB, 2026-08-30:**
  [`RECORD-20260830-oi179-remediation-confirmed.md`](RECORD-20260830-oi179-remediation-confirmed.md)
  — `[env-pathcheck] OK`, **47 entries, 0 violations**, in all four round-2 `.out` files, on **both**
  partitions that produced round 1's identical refusals (`shared_gpu_ss11`, `shared_milan_ss11`). The
  four tasks then **COMPLETED** `0:0` (8:45–17:18) and wrote products: `member_k000000/` went from 0
  entries to `boot_nd_5d/` + `seedscan_split_5d/` with **4 `.done` markers**. So the diagnosis is
  confirmed by successful remediation, a falsifiable prediction that held — declare the allowlist,
  change nothing else. **The 46 → 47 entry step is recorded as UNEXPLAINED** (consistent across
  partitions, benign). **§3 says outright this is NOT a run result: 4 of 374 tasks.** `OI-179` stays
  **OPEN on defect 1** — `PACKET:122` still measures rc 3 on `$HOME/bin`. No gate moves; `OI-177`
  unratified; Gate 2 remains **FAIL**.
- **ROUND 2 OF THE SEVEN k=0 ARMS IS SUBMITTED, 2026-08-30:**
  [`RECORD-20260830-k0r2-round2-submission.md`](RECORD-20260830-k0r2-round2-submission.md) — job ids
  `57753239`, `57753243`, `57753244`, `57753245`, `57753246`, `57753247`, `57753248`, run id
  **REUSED** (`k0-7ac0edec-20260830T000215Z`) because round 1's arms produced nothing and `%A` keys
  the logs by job id. **The positive control ran this time, in the ACTIVATED environment:**
  `[env-pathcheck] OK: 46 search-path entr(ies) checked`, `PREAMBLE_EXIT=0` — the in-job proof the
  proposal lacked; 46 rather than 37 because the earlier read was unactivated. Environment provenance
  written to disk BEFORE the first `sbatch`, closing `OI-179` defect 3 for this run. Abort arm armed
  and read three times, porcelain **726** / digest `d429f0f3` each time, never fired. **§6 says
  outright that this record does NOT say the run worked** — no task had started, and round 1 queued
  healthily for 22 minutes before failing in 12 seconds. Closed by
  [`CLOSE-20260830-canonical-requiesce-k0r2-window.md`](CLOSE-20260830-canonical-requiesce-k0r2-window.md),
  which records that the prose hold was treated as UNPROTECTED throughout — no dashboard lane was live
  to acknowledge it — and that **what actually held was the abort arm, not the prose.** Releases the
  dashboard lane's `OI-175` fix (726 → 725), safe because `OI-178` already ruled that drift a filed
  finding. Deployment tree NOT released. **`OI-177` unratified; Gate 2 remains FAIL.**
- **THE CANONICAL CHECKOUT IS RE-QUIESCED FOR THE RE-SUBMISSION WINDOW, 2026-08-30:**
  [`FREEZE-20260830-canonical-requiesce-k0r2-resubmission.md`](FREEZE-20260830-canonical-requiesce-k0r2-resubmission.md)
  — a SECOND window, because the first expired by its own terms at submission authorization and
  `CLOSE-20260830` **released the dashboard lane** to land the `OI-175` fix, which takes porcelain
  **726 → 725**. **Nothing has drifted:** HEAD `32e403b8`, porcelain **726**, digest `d429f0f3…`
  unchanged across a five-hour hold re-measured at `20:43:52Z`, and `mii/member_k000000` still empty.
  So this closes a window that is open rather than repairing a violation, and the risk is **permitted
  future drift** — deliberately the weaker claim. Prose hold, preventive by convention and detective
  by `F-17(a)`; pushed before any operand read, and the dashboard lane asked directly, because a hold
  peers cannot see is not a hold. A `CLOSE-*` record is owed whether the re-submission is issued or
  abandoned.
- **RE-SUBMISSION OF THE SEVEN k=0 ARMS, AUTHORIZED 2026-08-30:**
  [`PROPOSAL-20260830-k0r2-resubmission.md`](PROPOSAL-20260830-k0r2-resubmission.md) — Joseph: *"do
  all of it, can you continue on the runs too?"* **One added `export` line and no repository file
  changes**, so none of the `F-14` / §7.0.7 or `OI-123` pin ceremony applies. **Measured on the
  DEPLOYED library against the real login PATH:** `PACKET-20260823:122` as documented gives **rc 3**
  with one `VIOLATION` on `$HOME/bin`, and the corrected **three-entry** widening gives
  `[env-pathcheck] OK: 37 search-path entr(ies) checked` — so **this document is the operative recipe
  and the packet is not**, until `OI-179` defect 1 is settled. Preconditions measured: canonical HEAD
  `32e403b8`, porcelain **726**, digest `d429f0f3…` all UNCHANGED since submission, and
  `mii/member_k000000` still empty — so the `F-17(a)` operands still describe their subject and the
  live risk is **permitted future drift**, the dashboard lane having been released to land the OI-175
  fix (726 → 725). Carries the residual shadowing risk the widening accepts, and the narrower
  launcher-edit alternative it rejects. **`OI-177` ceilings stay unratified; Gate 2 remains FAIL.**
- **THE SEVEN k=0 ARMS DIED ON `env-pathcheck`, AND THE GUARD WAS RIGHT, 2026-08-30:**
  [`FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md`](FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md)
  — six tasks of `k0-7ac0edec-20260830T000215Z` failed in 8–15 s, exit `3:0`, byte-identical stderr
  (1453 B, `md5 9fc5fa4d…24df6`); the rest cancelled at 16:35:21Z on Joseph's instruction; **~1 minute
  of compute burned.** Cause is a **procedure omission, not a code defect**:
  `lib_mnv_env_pathcheck.sh:37-41` specifies that home-directory PATH entries are refused until the
  submitter predeclares them, `PACKET-20260823:122` gives the export line and `:218` calls it *"a
  submitter-declared allowlist"*, and **`RECORD-20260830` §5 records the submission as eight `export`
  lines with `MNV_ENV_SYSTEM_PREFIXES` absent.** **Three defects filed as `OI-179`:** `PACKET:122`
  omits `$HOME/bin` so the documented recipe still fails; **branch (b) of the guard has no test in the
  direction it acts** — `tests/test_k0_launcher_two_roots.py:738` asserts `[env-pathcheck] OK:` but
  `good_env()` feeds it an allowlist derived from the running host by `_ambient_prefixes()`, so the
  arm cannot fail, which is why Gate 1 passed 18-of-18 while the launcher could not start; and the run
  records no environment provenance at all while pinning its tree to the byte. **NO code, launcher or
  `MANIFEST` pin must change to re-submit.** Corrects the producer session's first diagnosis, which is
  recorded in §4 and withdrawn by its author. Moves no gate; Gate 2 remains **FAIL**.
- **Canonical drift during the run is a FILED FINDING, 2026-08-30:**
  [`DECISION-20260830-joseph-f17b-post-path-drift-is-a-filed-finding.md`](DECISION-20260830-joseph-f17b-post-path-drift-is-a-filed-finding.md)
  — Joseph chose option 1 of four: *"Yes do option 1, filing the correction and settling OI-178"*,
  declining a multi-day re-freeze, a repoint at a quiescent stand-in, and adding `M-4.dirty` to the
  expected-differences file. **Rests on three artifacts read directly**: `compare_m1_m6.py:141-145`
  (exit 20 is a finding, 4/5 are refusals), `PROPOSAL` §3 (`F-17(b)` is not-discharged only on a
  missing `M-2` result, a schema gap, or a refusal), and `m1m6_expected_differences.json`, which says
  a difference in `M-4.dirty` *"is the finding `F-17(b)` asks for"*. So canonical **726 → 725**
  yields exit 20 with a retained finding and `F-17(b)` still discharges. **CORRECTS TWO OF THIS
  LANE'S OWN RECORDS:** the close record's claim that the freeze preamble sets out the options'
  trade-offs (it names them in one sentence with none), and `OI-178`'s framing of the collision as
  BLOCK-shaped when it is finding-shaped. `OI-178` **DISCHARGED**. Moves no gate; Gate 2 remains
  **FAIL**; the grader still weighs the finding.
- **THE DECLARED CANDIDATE SHA, with A-2(a)–(g) filed against it:**
  [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md) —
  `a54038b21fdebfc975bec452a05866ffa571a36c`, **780** tracked source files, listing sha256
  `1b45da55…`, all seven clauses MET. Repairs the round-8 `F-1(a)` failure. **Declares a sha; clears
  no gate.** Re-run before the first `sbatch`; do not inherit the numbers.


- **ROUND-7 REPAIR PACKET (2026-08-23), awaiting the terminal regrade:**
  [`PACKET-20260823-round7-f2a-parity-and-f17a-filing.md`](PACKET-20260823-round7-f2a-parity-and-f17a-filing.md)
  — final candidate `e93364d1…`, deployed, `porcelain=0`, 0 writable. **Gate 1 is NOT claimed passed.**


- **M-1…M-6, re-measured 2026-08-23 on BOTH trees:**
  [`MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md`](MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md)
  — the `F-17(a)` filing repair. Ten M-1 rows (the previous filing had nine and dropped
  `unified_throw_cov.py`), **four** surviving literals on the candidate, **five** on the canonical
  checkout. Re-run it with `docs/orchestration/measure_m1_m6.py --tree <TREE>`; do not inherit a number.


- Live snapshot: [`LIVE-STATE.md`](LIVE-STATE.md); run its freshness check before use.
- Bounded queue: [`../CURRENT_WORK.md`](../CURRENT_WORK.md); sources live in
  [`control-plane/`](control-plane/).
- Queue overflow: [`../CURRENT_WORK_OVERFLOW.md`](../CURRENT_WORK_OVERFLOW.md).
- Unpromoted active records: [`../CURRENT_WORK_BACKLOG.md`](../CURRENT_WORK_BACKLOG.md).
- Active process rules: [`PLAYBOOK.md`](PLAYBOOK.md).
- Open/deferred source records: [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md).
- Joseph-only decisions: [`USER-DECISIONS.md`](USER-DECISIONS.md).
- **The whole remaining publication path, ordered by dependency:**
  [`PUBLICATION-READINESS-20260822.md`](PUBLICATION-READINESS-20260822.md) — every item with its
  measured state and command, split into Joseph decisions / lane work / gated / done. It answers two
  questions no other document settles: **the `M(ii)` member family IS on the critical path**, via the
  seven-cause quarantine named as *the binding gate* in `../INTEGRATION_CHECKLIST.md` rather than via
  any runbook packet; and the **P3S lateral is BUILT and validated but not committed and not
  adopted**, which makes `VALIDATION_LEDGER.md` `VL68` and
  [`RUNBOOK-20260807-gbdt-closeout.md`](RUNBOOK-20260807-gbdt-closeout.md)`:38` stale.
  **A view, never evidence** — re-measure any field before deciding a gate on it.

## Evidence and claims

- Verified numbers: [`../../VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md).
- Physics claims: [`CLAIMS.md`](CLAIMS.md).
- Active BEN identifiers: [`FINDINGS.md`](FINDINGS.md); full evidence is at the frozen tag.
- Bugs and traps: [`../../KNOWN_ISSUES.md`](../../KNOWN_ISSUES.md).
- Retracted values: [`INDEX-retracted-and-superseded-values.md`](INDEX-retracted-and-superseded-values.md).
- Why the B1 pause's clause (c) cannot be met through the launcher:
  [`FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md`](FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md)
  — measured: `sbatch_finalize_5d_bkgaware_gpu.sh:347/:352` is unreachable in both regimes, so the
  condition is circular as written and the disposition is a forced choice, not a judgement call.
- The 2026-07-12 quarantine's three no-compute legs, re-measured at HEAD `32e403b8`:
  [`FINDING-20260830-quarantine-nocompute-legs-measured.md`](FINDING-20260830-quarantine-nocompute-legs-measured.md)
  — cause 3's `P-ii` premise is **false** (four write sites landed 08-18…08-20, and two 08-22 records
  restated it as live afterwards); the *"one edit closes 2, 3 and 4"* multiplier **does not hold**, and
  cause 3's `P-i` is **no longer a no-compute leg**; cause 1 has content on all four legs **for the
  quoted artifact**, needing only the routed `DETERMINATION §6` judgement; and cause 4's `M` is neither
  recoverable from bytes nor closed by a run, because the deflation never entered a stored object on X's
  path. **Regrades nothing** (`BEN-381`) — four decisions routed as `OI-170`–`OI-173`. Counts unchanged:
  CAND `1 of 7`, QUOTED `0 of 7`.
- Why the accepted forward-only k=0 rehearsal's seven arms were not submitted on 2026-08-30:
  [`FINDING-20260830-k0-member-namespace-blocks-submission.md`](FINDING-20260830-k0-member-namespace-blocks-submission.md)
  — all three step-3 conditions pass and the preflight re-verifies clean, including canonical porcelain
  **726** with a status digest byte-identical to the Gate-1 round-2 grader's reads, so the quiesce held.
  The blocker is in the **data root**, which no Gate-1 clause and neither F-17 operand measures:
  `mii/member_k000000` still holds the `aa67c426` rehearsal's complete products, every marker reading
  `note:"est_seed_offset=0"`, so `mr_skip_if_complete` **adopts**. Arms 1-3 would skip all 143 of their
  tasks (cross-run, mixed-pin — a §7 abort condition); arms 4-6 carry **no resume guard** and would
  overwrite a Gate-2-FAIL rehearsal's products in place. **Moves no gate and grades nothing**; the
  disposition decision is routed as `OI-176`. No `sbatch` was issued.
- **The `aa67c426` products were quarantined and the seven arms WERE submitted, 2026-08-30:**
  [`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md`](RECORD-20260830-k0-quarantine-and-seven-arm-submission.md)
  — Joseph ruled *"do option 1"* (`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`,
  `deef0e48`), a **per-instance** authorization naming an exact file set. **517 files /
  2 733 087 821 regular-file bytes moved, never deleted**, to
  `/pscratch/sd/j/josephrb/quarantine/20260830-k0-aa67c426-failed-rehearsal/`, with a 0-line diff on
  both the per-file `sha256` set and the `(relpath, bytes, mtime, inode)` ledger. Canonical porcelain
  **726** and status digest `d429f0f3…` held across **five** reads including immediately before each
  `sbatch`. Seven job ids `57742557`, `57742558`, `57742559`, `57742560`, `57742561`, `57742633`
  (`afterok` detector), `57742635` (conjunctive `afterok` over both uthrow arrays) — 374 tasks.
  **Moves no gate, adopts nothing, files no Gate-2 evidence, and leg 6 was not submitted; Gate 2
  remains FAIL.** `OI-176` is DISCHARGED; a §6 per-arm CPU-ceiling discrepancy of 1.38 CPU task-h is
  routed as `OI-177`.

### Documents that open items route to but this router did not list

Added 2026-08-20. `live_doc_indexed.py --check` reports LIVE docs absent from this catalog and
**does NOT enforce it**, so an item's own governing document could be unreachable from the router.
The count was written as **19** on 2026-08-20; re-derived from the same command on 2026-08-22 it is
**13**, so the figure is stated with its date and its command rather than left to drift. These five are the subset that `docs/OPEN_ITEMS.md` rows
actually cite; the other fourteen are not routed to by any open item and are left out
deliberately, because this file is a pointer-only router and not an exhaustive index.

- [`PROVENANCE-DEBT-20260810-standard-p4.md`](PROVENANCE-DEBT-20260810-standard-p4.md) — **`OI-7`'s
  own blocker**: its §3e is the sentence that row is open on. Cited 4× in `OPEN_ITEMS.md` and
  reachable from no router until now.
- [`SPEC-20260814-gate5-cstat-construction-v1.md`](SPEC-20260814-gate5-cstat-construction-v1.md) —
  the ruled `C_stat` construction spec; cited 6×, including by `OI-93`, whose row is stale against
  it.
- [`RANK-AND-INVERSION-20260810.md`](RANK-AND-INVERSION-20260810.md) — the rank and pseudo-inverse
  measurements behind the N-D χ² protocol; routed to by `OI-137`.
- [`RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md`](RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md)
  — traces the `\gbdtFive*` note macros to their artifacts; one of them had been destroyed.
- [`DETERMINATION-20260811-cause5-binding-half.md`](DETERMINATION-20260811-cause5-binding-half.md),
  [`CONVENTION-verifying-a-check-is-deployed.md`](CONVENTION-verifying-a-check-is-deployed.md) —
  each cited once.
- [`FINDING-20260822-a-hold-that-instructed-its-own-deletion.md`](FINDING-20260822-a-hold-that-instructed-its-own-deletion.md)
  — added 2026-08-22, routed to by `OI-70`. **Read it before acting on
  [`HOLD-20260821-clause-c-verification.md`](HOLD-20260821-clause-c-verification.md), whose own text
  instructs its deletion.** That instruction is wrong, the hold's bytes are preserved on Joseph's
  ruling, and this route is the only thing that disarms it.

- [`BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md`](BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md)
  — `OI-137`'s measured exposure and **the recommendation Joseph's ruling 7 requires before any
  uncertainty-model change: disclose, do not correct.** Routed to by `OI-137` and `OI-93`. Re-runnable
  covering search beside it at [`state/oi137-covering-search-20260822.sh`](state/oi137-covering-search-20260822.sh).
  **Do not carry "0.2% of the headline trace" forward as the reason the exposure is small** — a trace
  weights eigenvalues by `lambda` and a precision matrix by `1/lambda`; the brief gives the real reason.
- [`PROVENANCE-20260822-declaration-v-scalar5d-blocks.md`](PROVENANCE-20260822-declaration-v-scalar5d-blocks.md)
  — added 2026-08-22 on Joseph's ruling 10. **Declaration (v) of the N-D χ² protocol, recorded per 5D
  block**: ensemble size, normalization convention, effective inversion dimension and finite-ensemble
  treatment, each with a citation. Routed to by `OI-137`. **It CORRECTS the gap statement carried by
  that row and by the brief above** — `N=160` is recounted and stamped on the throw roots
  (`unified_throw_cov.py:388,540`) and propagated to the adopted product as `upstream_n_throws` since
  2026-08-11, so it is *not* only a hardcoded constant; the surviving gap is `C_stat`/`C_ML`, which
  carry no ensemble-size key on any artifact. **Records/provenance only — it adopts nothing and
  changes no uncertainty model.** Re-runnable covering search beside it at
  [`state/declaration-v-5d-covering-search-20260822.sh`](state/declaration-v-5d-covering-search-20260822.sh).

- [`BRIEF-20260901-greif-fps-thesis-implications-for-pet.md`](BRIEF-20260901-greif-fps-thesis-implications-for-pet.md)
  and [`BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md`](BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md)
  — added 2026-09-01, the two lane extractions of **`arXiv:2608.28449`** (Greif, ATLAS full-phase-space
  Z+jets, 843 dimensions), routed to by `OI-183` and `OI-184`. **Read the citability box first: the
  measurement is in ATLAS review and its thesis figures are ATLAS Internal, so the METHOD is citable
  and the NUMBERS are not.** Between them they carry: the ATLAS `C_ML` construction (ensemble mean as
  the central value, so the nominal cannot sit outside its own family); pretraining as the lever that
  took their seed ensemble from 100 members to 10; the closure instrument (full-covariance χ² in 26
  projections, with the rule that a systematic held at nominal in the pseudodata must be EXCLUDED from
  Σ); and the finding that **the high-dimensional hidden-variable advantage was tested and did not
  hold**. **Neither bears on `OI-126`** — that thesis mentions the bootstrap five times in 313 pages
  and carries no centering diagnostic — and **neither is evidence that any coverage gap here is a gap
  relative to the field**: `coverag` appears once in it, about detector acceptance.

### START HERE for the remaining publication work

- [`WALKDOWN-20260822-one-pass.md`](WALKDOWN-20260822-one-pass.md) — **the ORDER of everything left
  before publication, and which step blocks which.** Deliberately thin: it is a route, not a second
  source of state, and every factual field it points at lives in the readiness list below. Two
  independent tracks — execution integrity (five Gate-1 repairs, then the k=0 rehearsal) and one
  scope ruling that decides whether the 50-member M(ii) family exists at all. **Read this first.**
- [`PUBLICATION-READINESS-20260822.md`](PUBLICATION-READINESS-20260822.md) — the measured INVENTORY
  behind that route: every remaining item with the command that measured it, plus `AMENDMENT 1`
  recording an independent peer review whose four objections were all accepted. **Where this and a
  canonical artifact disagree, the canonical artifact wins.**

- [`MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md`](MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md)
  — the `F-17(a)` filing repair, 2026-08-23. **Ten** M-1 rows and **four** surviving literals on the
  candidate (three `_DATA_ROOT`, one inert `_REPO`); **five**, all `_REPO`, on the canonical checkout,
  one of them active. The 2026-08-22 filing it replaces had nine rows and said "three". Re-run it —
  `python3 docs/orchestration/measure_m1_m6.py --tree <TREE>` — and do not inherit a number.

### Gate-1 round 8 — F-2(a) AND F-17(a) PASS; F-1(a) failed and is repaired

- [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md)
  — the declared candidate `a54038b21fdebfc975bec452a05866ffa571a36c`, **780** tracked source files,
  listing sha256 `1b45da55…`, **A-2(a)–(g) all MET and each measured separately**. Repairs the
  round-8 `F-1(a)` failure: the digest was three shas stale and the packet named a sha that was not
  `HEAD`. **Declares a sha; clears no gate. Gate 1 does NOT pass.**

### Round-7 repair — BUILT AND DEPLOYED, awaiting the terminal regrade

- [`PACKET-20260823-round7-f2a-parity-and-f17a-filing.md`](PACKET-20260823-round7-f2a-parity-and-f17a-filing.md)
  — Joseph's three authorized items: the parity gate extended to all three tracked files the preamble
  sources (one block digest across all eight launchers, ten new arms in four directions, power
  checked), the M-1…M-6 filing corrected to ten rows on both trees, and the runbook/plan §C exports.
  Final candidate `c35bed58…`, deployed, `porcelain=0`, 0 writable. **Gate 1 is NOT claimed passed.**

### Gate-1 round 6 — GRADED, TERMINAL, and it DOES NOT PASS

- [`GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md)
  — **16 PASS / 2 FAIL / 0 NOT-EVALUABLE** (`F-2(a)`, `F-17(a)`), graded at `fabeedc2`. Landed
  **byte-identical**, sha256 `bf2ad6e1415391bb5eba3e15b9e818fb10a6ee65ce4e7ca1b8b08dd57c3d0125`,
  415 lines. The operative rubric was confirmed byte-identical to round 5 (1160 lines,
  `e0fb342b6466…`) — **no criterion was added.** Round 6's two targets are genuinely fixed and the
  grader could not break either; **both `F-14` grounds are closed.** `F-2(a)` fails on a **new
  ground**: `lib_mnv_env_preflight.sh` and `lib_mnv_env_pathcheck.sh` are **tracked** and sourced
  from the code root by all eight launchers with **zero git-parity gate**, executing 77–193 lines
  before the only instrument covering their bytes — while the pure-git gate sits 17 lines above,
  naming only `lib/resume_guard.sh`. `F-17(a)` is unrepaired and outside round-6 scope.
  **This is a terminal handoff: no further grader was requested.**

- [`DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md`](DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md)
  — Joseph's ruling of 2026-08-23: **A-2(f) does not substitute for A-3 executing-file parity.** A
  tracked file that executes before the later source-manifest comparison requires **pre-use git
  parity**, so `F-2(a)` **stands**; `F-17(a)` stands until the canonical M-1…M-6 filing is corrected
  **and re-measured at the eventual candidate sha**. **No repair is authorized by it.** The ruling
  is authorized here and nowhere else; a relay of it is not quotable.

### Gate-1 round 5 — GRADED BY A THIRD PARTY, and it DOES NOT PASS

- [`GATE1-VERDICT-ROUND5-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND5-20260823-k0-execution-integrity.md)
  — **15 PASS / 3 FAIL / 0 NOT-EVALUABLE** (`F-2(a)`, `F-14`, `F-17(a)`), regraded first-hand at
  `f3c27870` inheriting nothing. Landed **byte-identical**, sha256 `c2143e2e…`. **The decisive
  finding:** `sbatch_unfold_5d_detector_bkgaware_gpu.sh` invoked both Python preflight tools at
  `:139`/`:148` and sourced its activator at `:227` — a **SyntaxError on the un-activated 3.6.15
  interpreter**, surfacing as *"the execution tree is not the tree that was approved"*, a **wrong
  diagnosis of a right refusal**. It survived 34 green arms because `good_env()` inherited the
  runner's PATH, so the fixture supplied the interpreter the activator exists to supply.
  **Two of the builder's packet claims were also contradicted by measurement** — the suite count and
  a `--check` run made in the wrong tree.

### Gate-1 round 5 — the repair as built (superseded by the grade above)

- [`PACKET-20260823-round5-f2a-f17a-repair.md`](PACKET-20260823-round5-f2a-f17a-repair.md) —
  **the repair packet for `F-2(a)` and `F-17(a)`, and the read-only commands a grader runs.**
  Three roots (`MNV_ENV_ROOT` mandatory, no default), a **14-member digest manifest over the full
  transitive closure** verified before any source, the activator regenerated so no checkout reaches
  `PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH`, `_mr_lib` bound before use in all eight, and the Gate-5
  template routed rather than duplicated. **Re-declared sha `f3c27870`, 778 files, `70fb59d4…`.**
  **GATE 1 IS NOT CLOSED — the verdict stands at 16/2** until a grader who is neither this builder
  nor the round-4 verifier re-grades. **All criteria are re-opened by the sha move.**

### Gate-1 round 4 — GRADED 2026-08-23, and it DOES NOT PASS

- [`GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md)
  — **the independent grade: GATE 1 DOES NOT PASS, 16 PASS / 2 FAIL / 0 NOT-EVALUABLE** (`F-2(a)`,
  `F-17(a)`), by a fresh non-builder. **The decisive finding is not a filing gap:** every
  repo-relative shell file below `setup_salloc_env.sh` is **ABSENT from the declared code root**, so
  every launcher aborts at the activator with exit 1 before any preflight tool, guard or science
  invocation runs. **The k=0 rehearsal is NOT launched and `PR-J1` does not become operative.**
- [`CONFIRMATION-20260823-builder-response-to-gate1-round4.md`](CONFIRMATION-20260823-builder-response-to-gate1-round4.md)
  — the builder lane's independent re-measurement of the decisive claims. **All reproduced; nothing
  contradicted.** Records what the builder got wrong, and argues that one criterion (`F-8(a)`, the
  builder's own `P-5`) was graded **too leniently**.

### Gate-1 round 4 — the k=0 execution-integrity repairs and their evidence

Added 2026-08-22. **Gate 1 DOES NOT PASS and none of these close it.** `F-2(a)` is repaired in its
first hop only; the **transitive environment trust boundary** must be settled and passed by a **fresh
non-builder** first (Joseph, `DECISION-20260822-joseph-b1-lift-and-clause-c.md`). The close-out lane
built all of these and is disqualified from grading them.

- [`DECLARATION-20260822-k0-submission-sha.md`](DECLARATION-20260822-k0-submission-sha.md) —
  **`PR-01` / `F-1(a)`: the submission sha, which previously had no referent anywhere.**
  `MNV_CODE_ROOT = /pscratch/sd/j/josephrb/k0r2/clean` @ `6113a34d`, 775 tracked source files,
  listing sha256 `cc004894…`, with all seven **A-2(a)–(g)** clauses measured separately against it.
  Read this before quoting any "pinned sha" phrase.
- [`P5-P6-20260822-entrypoint-set-and-blind-spots.md`](P5-P6-20260822-entrypoint-set-and-blind-spots.md)
  — **`PR-04` / `F-8(a)`: the two artifacts that did not exist and were undisclosed.** `P-6` is the
  entrypoint-set search with its command and full output (8 entrypoints, 14 invocations — an
  independent cross-check of ruling 21's boundary). `P-5` is the blind-spot inventory, including the
  subprocess enumeration: **one child on the whole k=0 path, and it is WRAPPED.**
- [`MEASUREMENT-20260822-m1-m6-at-pinned-sha.md`](MEASUREMENT-20260822-m1-m6-at-pinned-sha.md) —
  **`PR-05` / `F-17(a)`: M-1…M-6 re-measured, and FOUR MOVED.** Two are stale **in the builder's
  favour** (`M-1`'s literal table, `M-5`'s `8 of 8` → `0 of 8`). **The fastest-expiring document in
  the package** — re-run all six immediately before the first `sbatch`.
- [`SPEC-20260825-f17b-tree-comparison-instrument.md`](SPEC-20260825-f17b-tree-comparison-instrument.md) —
  **what a third lane must build so `F-17(b)`'s "differences reported as findings" is a machine
  statement, not two column sets diffed by eye.** `measure_m1_m6.py` measures one tree per
  invocation and has **no comparison surface at all**; `F-17(a)` was discharged by hand at
  `30ec0707`. Also records **DO NOT build an `F-7(b)` exclusion instrument** — §7.0.9 rules it
  untestable at k=0 and the widening detector already exists at `b49bc360`. Authored by the
  evidence-producing lane per Joseph's 2026-08-25 ruling, so **every clause is rejectable**.
  **BUILT, by the third lane, 2026-08-25:** `compare_m1_m6.py` (the instrument),
  `test_compare_m1_m6.py` (46 arms, both directions per requirement) and
  `m1m6_expected_differences.json` (the reviewable whitelist, deliberately ONE entry). Exit codes
  `0 / 10 / 20 / 4 / 5`. **Two of the spec's clauses were REJECTED and one requirement is partial:**
  its `M-1, M-5, M-6 are falsified by ANY commit to build-k0-execution-integrity` is false as
  measured — 10 of the 46 commits ahead of `8c156a37` touch those populations, not 46 — and as a
  whitelist entry it would have suppressed the `F-17(a)` findings themselves; R5's stated fixture
  cannot exist under exact equality; and R3's `detached-or-branch` and R6's
  `wall-clock of each measurement` are **not in `measure_m1_m6.py --json` at all**, so the record
  names them `UNAVAILABLE-BY-INPUT-SCHEMA` rather than deriving them from the tree as it is now.
  **It grades nothing:** F-17(b) is the F-18(b) reviewer's, who must be a fresh non-builder.
- [`GRADE-20260825-d3-comparator-repair-fitness.md`](GRADE-20260825-d3-comparator-repair-fitness.md) —
  **the independent grade of the D-3 repair (`c8a29082`) required by ruling 3**, at
  `compare_m1_m6.py` `68b4af12` and `test_compare_m1_m6.py` `b355ecdc`. **Verdict: FIT to support a
  future Gate-2 filing, conditionally** — D-3 is closed (all five fail-open spellings, including the
  four the implementer newly found, refused; negative control restoring the pristine guard reddens
  **16 arms**; producer-derived fixture 721/96/**0 accepted**). **The condition is mechanical**: the
  expected list at filing time must contain no *partial* `M-1` selector — satisfied today, the
  shipped list has one entry and no selector. **Partial wildcards are RULED (c), an ambiguity
  requiring a specification decision, and ESCALATE to Joseph**: measured, the pre-repair guard
  accepted them identically (so not an enlargement), but it accepted them through the very clause
  that is D-3 (so not an admitted contract), and two negative controls FIRE — on the real
  population `M-1[nd-unfolding/unified_throw_cov*].first_insert` silently suppresses **two** files
  including the one whose omission was the F-17(a) failure, and a partial selector's reach is not
  stable as the file population grows. **Three figures in the implementer's mutation matrix do NOT
  reproduce** (5 methods, "reddens 4", "reddens 97"; measured 6, 1, 121). **Grades no F-number,
  discharges no clause, authorizes no compute and no filing; Gate 2 stays FAIL and open.** Expires
  mechanically when any of three pinned digests moves.
- [`GRADE-20260825-selector-narrowing-fitness.md`](GRADE-20260825-selector-narrowing-fitness.md) —
  **the independent grade of the §12.2.1 selector narrowing (`63262a3a`) required by ruling 3**, at
  `compare_m1_m6.py` `5dc92487` and `test_compare_m1_m6.py` `762fac14`. **It REPLACES
  `GRADE-20260825-d3-comparator-repair-fitness.md`, whose mechanical expiry TRIPPED** — two of its
  three pinned digests moved in `63262a3a`, verified not assumed, so the instrument had no live
  grade. **Verdict: FIT to support a future Gate-2 filing, with NO condition** — the prior grade's
  standing precondition ("no partial `M-1` selector in the list at filing time") is now
  unnecessary, because the guard makes one unrepresentable. **`NEWLY ACCEPTED = 0`**, measured over
  **115160** grader-built patterns: the ONLY verdict transition anywhere is
  `ACCEPT -> refused-as-partial-selector` (42224), every other refusal check keeps an
  identically-sized population, and the 50270 rewordings fall in exactly two cosmetic classes with
  no third. Both negative controls re-run and reproduce EXACTLY (revert-the-guard 5 distinct red /
  134 subTests / 0 errors / 0 pre-existing red; over-tighten-to-refuse-literals 6 red including the
  silent-on-good arm and two pre-existing). Producer-derived fixture re-run: **4060 / 210 / 3850 /
  0 escaped**, and the graded **721 / 96 / 0** did not move. **Claim 8's LAST placement: CORRECT**,
  proved by check-identity fingerprinting rather than by reading. **Claim 9: measurement
  reproduced (`M-1[nd-*]` reaches 10 of 10, so the ruling is genuinely syntactic) but the honesty
  claim is OVERSTATED** — the code nowhere records it, and the new invariant arm's docstring frames
  the point AS a reach property that `M-1[nd-*]` satisfies; coverage survives via the 4060-candidate
  sweep, so this is a prose defect, reported and deliberately NOT repaired. **Four claims overstated**
  (the `4840` denominator is unrecoverable — cite `4060`; `field_matches`'s stated ground is wrong
  though the decision is right; four prose sites not three), Its §9 claim that the pre-existing
  "265 of 721" docstring figure does not reproduce is **RETRACTED — see DECISION §13.2**: 265
  reproduces exactly as *refused ∧ one field name ∧ touching no `M-2`*, the D-3 grade had already
  graded and affirmed it, and `accepted` also being 265 is a coincidence (456+265=721). The
  docstring needs a missing qualifier, not a retraction. **Its §8's ratio "517 of the 773" is STRUCK
  by DECISION §12.4** — a property of a generator emitting every path prefix, not of anything a
  reviewer types — so this grade is **NOT CITABLE for that figure**; the rest of §8 stands. §8 is the accepted/rejected shape table the `m1m6_expected_differences.json`
  prose note is to be transcribed from under §12.1. **Grades no F-number, discharges no clause,
  authorizes no rehearsal, no filing and no compute; Gate 2 stays FAIL and open**, and per §10.1 a
  separate readiness check still gates step 4. Expires mechanically when any of three pinned digests
  moves.
- [`GRADE-20260825-f17b-comparison-instrument-fitness.md`](GRADE-20260825-f17b-comparison-instrument-fitness.md) —
  **an independent non-builder's fitness grade of that instrument against the F-17(b) CLAUSE, not
  against the spec.** Graded at `2790ba90` by digest; **records no F-number verdict and no gate
  verdict.** Confirms the builder's rejections by re-derivation — the "any commit" bullet is false at
  **10 of 46** commits by per-commit enumeration, R5's fixture is unbuildable under exact equality,
  and §7.0.9 independently settles the refusal to build an F-7(b) instrument. **34 mutations, 27
  caught behaviourally with the arm named, 6 survivors.** Three demonstrated defects still let an
  obliged difference report as `DIFFERENCES-ALL-EXPECTED` with all 53 arms green: the shipped-list
  guard arm uses `fnmatch`, so it is **blind to `M-1[*]` patterns**; a **one-character** citation
  licenses a suppression; and a **MISSING** measurement is suppressible because `field_set_differs`
  is not a finding — that last one is live in the shipped file today. Also: at that sha the far-end
  script never invokes the instrument, and the filed pre-submission column is **markdown, not
  `--json`**, so it is not consumable by it. **Authorizes nothing.**
- [`VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md`](VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md) —
  **the Gate-2 verdict for run `k0-aa67c426-20260824T145751Z`, by an independent non-builder, over the
  NINE clauses of §7.0.18. GATE 2 DOES NOT PASS.** `F-7(b)` and `F-8(b)` have **no evidence of any
  kind** — no rehearsal pin is recorded and no run receipt has been authored — and `F-17(b)`'s
  `:1471` half is **impossible, not pending**, because the pre-submission column is prose and the
  comparator consumes `--json`. `F-1(b)` and `F-4(b)` PASS, re-derived: A-2(a)–(g) all hold at the far
  end, and 374 inventories == 374 guarded processes with the inventory filenames in **bijection** with
  `sacct`'s 374 `JobIDRaw`. `F-2(b)`/`F-5(b)` PASS on measurements this verdict files first (P-2 over
  **all 374** records, 0 sha mismatches against the 782-entry baseline, `checked` min 974).
  **`F-3(b)`'s own instrument is VACUOUS** — these launchers never echo argv, so a stdout grep for
  `--allow` cannot answer it; the guard's `allow_is_empty` field does. **Three producing-lane claims
  did not reproduce**, including a FALSE counterfactual: the excluded sibling's 298 records live under
  `guard-inventories/`, so the `runs/*/inv` glob it was said to protect against yields **374, zero of
  them from siblings**. **New repairable defect:** `bad_pattern` admits `M-1[*` (unbalanced bracket),
  which suppressed **all 19** M-1 findings as `EXPECTED-BY-RULING` with the suite green — the prior
  GRADE has **self-expired** (all three digests moved) and never examined that guard. **Authorizes
  nothing; it is NOT CITABLE FOR any Gate-2 PASS.**

### B1 steps 4-5: the lift, and the preflight that gates the first submission

- [`PLAN-20260822-oneMember-mii-staged.md`](PLAN-20260822-oneMember-mii-staged.md) — **the staged
  one-member request required by ruling 12, and it is a REQUEST, not an authorization.** Read it
  before any M(ii) submission. Carries the measured per-leg costs, the k=0 choice, and two blockers
  that need Joseph: three stale 08-18 replicas inside the chosen member, and family SIZING under the
  pscratch line. **Its "17.8x discrepancy" section is WITHDRAWN** -- 151 and 2 680 count different
  populations, never one quantity; see `PUBLICATION-READINESS-20260822.md` PR-J4.

Added 2026-08-22. The B1 pause is **LIFTED**; read both of these before any submission touching
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh`.

- [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
  — Joseph's eight rulings of 2026-08-22, including the lift itself and the ruling that the `srun`
  execution satisfies expiry clause (c). **The lift is authorized here and nowhere else**; a relay of
  it is not quotable.
- [`RUNBOOK-20260822-b1-lift-preflight.md`](RUNBOOK-20260822-b1-lift-preflight.md) — required by
  ruling 4. **Its headline is that the launcher must NOT be submitted yet**: both routes refuse today
  for reasons unrelated to the pause, measured on the cluster.
- [`RECEIPT-20260822-k0-n1-and-guarded-arms.md`](RECEIPT-20260822-k0-n1-and-guarded-arms.md) — the
  measured N-1 arm, its paired unguarded hijack control, and the first guarded production arm, run
  on `saul.nersc.gov` against the real canonical checkout. **Read it before quoting F-9 as
  satisfiable**: B-4 script containment now refuses strictly earlier than the import guard can fire,
  so N-1 exits 3 without naming `seed_offset_policy`, and that is a question for Joseph rather than a
  builder's judgement. Also records the one runtime confirmation of M-1 — `adopt_unified_5d.py`
  resolved **213** absolute origins and **zero** repository modules.
- [`REVIEW-CONTRACT-20260822-k0-execution-integrity.md`](REVIEW-CONTRACT-20260822-k0-execution-integrity.md)
  **AMENDED 2026-08-22 (§7.0): §F is now TWO GATES.** Joseph ruled that the contract must separate
  pre-submission readiness from post-rehearsal completion. The eighteen criteria are unedited and
  keep their numbers; §7.0 adds the one-question test that reproduces the partition (8 criteria are
  pre-submission, 10 split, **none** is purely post-rehearsal), the two gates and what each unlocks,
  and the eligibility rule. **If you are grading this contract, read §7.0 before §F.** Two traps it
  names: a NOT-EVALUABLE in the pre-submission column is a FAIL of Gate 1, and "needs the cluster"
  is not "needs a run" — F-9's negative control is pre-submission. **FURTHER AMENDED 2026-08-22 by
  rulings 20-22 (§7.0.11-§7.0.16): F-9 and F-12 are RESTATED.** B-4 containment refuses the
  canonical-checkout wrapper before the import guard installs, so F-9 no longer requires
  `seed_offset_policy` to be named — it forbids it — and **`checked=0` is the EXPECTED value there,
  inverting the anti-vacuity rule that applies everywhere else.** Also lands ruling 21's 14/30
  guarding boundary with the preflight ORDERING requirement graded as a criterion, and ruling 22's
  A-2(d)/(e)/(g) fail-closed checks and P-4 pin-vs-mechanism split. The transferable lesson, and it
  has now recurred twice: **a protection can invalidate the control written to test a different
  protection, and the control then presents as merely unperformed rather than as impossible.**
- [`VERIFICATION-20260822-k0-execution-integrity.md`](VERIFICATION-20260822-k0-execution-integrity.md)
  — the round-1 verdict against that contract: **NOT A PASS**, 7/7/4. It predates the §7.0 split and
  is not revised; it grades build `ae42ae8d`, which is **NOT on main**.
  — **the controls for corrections 2-4, agreed by a fresh non-builder BEFORE the builder implements**,
  on Joseph's instruction that the evidence cannot be selected afterwards. Read it before writing any
  OI-136 wrapper, guard or negative control on the k=0 path. Its headline correction to the plan: the
  pinned adopter `adopt_unified_5d.py` imports **no repository module at all**, so guarding its
  subprocess is vacuous **by construction** and no source repair is authorized there — while
  **five other entrypoints plus one imported module** on legs 1-5 do carry a rooted insert *and*
  import repository code through it, and those are where the scoped source repair belongs. Also:
  the clean tree must be split into a code root and a data root, and `mnv_guarded_run.py` never
  checks that the script it runs is inside `--expect-root`.
- [`GATE1-VERDICT-20260822-k0-execution-integrity.md`](GATE1-VERDICT-20260822-k0-execution-integrity.md)
  — **the GATE-1 verdict against the amended contract: GATE 1 DOES NOT PASS.** Recorded by an
  independent lane that neither built the package nor wrote the §7.0 split, as ruling 23 and §7.0.10
  require. Grades **only** the pre-submission column, against `main` `7165ea5c` — *the build branch
  carries a superseded contract with a different F-9, and a verdict graded against it would be void.*
  Thirteen pass, **five fail** — F-1(a), F-2(a), F-7(a), F-8(a), F-17(a) — and none is recorded
  NOT-EVALUABLE. **F-9 PASSES**, verified on the live cluster records including ruling 20's
  `checked=0` inversion, so the criterion that forced the restatement is closed. What is not closed:
  two executing `.sh` files bound by no `--pair`, the 16-call preflight exclusion enumerated nowhere
  and pinned to nothing, **P-5 and P-6 absent from the package entirely and absent from the builder's
  own gap list**, an A-2(f) digest filed at a superseded sha, and F-17 freshness open. **No
  submission is authorized.** Read §5 for the shortest list that would close the gate, and §2 for
  three builder claims that reproduce differently.

## Task routes

| Task | Route |
|---|---|
| Change code | `KNOWN_ISSUES.md`, relevant status/reference, callers, tests, and hash bindings |
| Quote a result | `VALIDATION_LEDGER.md`, then the exact product or live receipt |
| Run or monitor compute | fresh `LIVE-STATE.md`, direct scheduler observation, then the exact launcher receipt |
| Work on 2D/3D/N-D/PET | relevant workstream status; PET also `PET_UQ_REMEDIATION_STATUS.md` |
| Maintain queue/playbook | [`control-plane/policy.json`](control-plane/policy.json), [`control-plane/source-record-inventory.tsv`](control-plane/source-record-inventory.tsv), then `control_plane_lint.py` |
| Maintain classifications | `MANIFEST-overrides.tsv`, then `generate_manifest.py` |
| Operate continuation | `WAKER.md`, `wakerctl.py`, `waker-config.json`, and `profiles.json` |
| Glance at campaign status | [`RUNBOOK-status-dashboard.md`](RUNBOOK-status-dashboard.md), then `dashboard_collector.py --print-scrontab`; the page is a view, so re-measure before deciding |
| Build deliverables | `docs/analysis-note/build_all.sh` for note, primer, and paper |

## Frozen pre-compaction evidence

Complete history, terminal receipts, long-form findings, audits, determinations, prompts, and old paths
live at:

`evidence/prepublication-2026-08-20-0b329e8a`

Recover a known path without changing the current checkout:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:<old-path>
```

Search the complete frozen tree:

```bash
git grep '<identifier>' evidence/prepublication-2026-08-20-0b329e8a --
```

The independently stored bundle and recovery proof are recorded in
[`../POST_PUBLICATION_REORG_PLAN.md`](../POST_PUBLICATION_REORG_PLAN.md).

### Anchored-but-unreachable commits — `git fetch github` will NEVER bring these down

Several commits cited in the record are reachable from **no branch**; that is exactly why they were
anchored by `evidence/*` tags. **Git only auto-follows tags that point at objects it is already
downloading**, and `remote.github.fetch` is branches-only
(`+refs/heads/*:refs/remotes/github/*`) with `remote.github.tagOpt` unset — so a tag on a commit
unreachable from `refs/heads/*` can never arrive from an ordinary fetch. **Measured 2026-08-20: six
of the ten `evidence/*` tags on the remote were absent from the main checkout, and `git cat-file -t`
failed outright on all six anchored commits — including `ecee9ff1`, the one carrying
`array_equal True across all 114,361,636 elements`.** Preservation had succeeded; discovery had not,
and a session here would reasonably have concluded the evidence was lost.

Fetch them explicitly — once per checkout:

```bash
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'
```

Or make an ordinary `git fetch github` do it permanently, per checkout:

```bash
git config --add remote.github.fetch '+refs/tags/evidence/*:refs/tags/evidence/*'
```

**THE REMOTE NAME IS CHECKOUT-LOCAL — do not hardcode it, and do not trust either name from this
file.** This paragraph read *"The remote is `github`. There is no remote named `origin` —
`git rev-parse origin/main` is fatal"* until 2026-08-21. That is true on the Perlmutter checkout and
**exactly inverted in the local clone**, where `git remote -v` lists only `origin`,
`git rev-parse origin/main` resolves, and `git rev-parse github/main` is the fatal one. A witness
phrased against *either* name is unfollowable in the other tree. Resolve it first and substitute:

```bash
# NAME the remote. Do NOT use `git remote | head -1`.
git remote -v                       # look, then substitute the right name below
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'   # on Perlmutter
git fetch origin 'refs/tags/evidence/*:refs/tags/evidence/*'   # in the local clone
```

**`git remote | head -1` IS ITSELF A DEFINITE DESCRIPTION AND IT IS WRONG HERE.** This file recommended
it until 2026-08-21, and it failed the same day it was written: the Perlmutter checkout has TWO
remotes, `analysis-note` and `github`, and `head -1` returns **`analysis-note`** on alphabetical
order. Every downstream number was then computed against the wrong repository -- it reported the
checkout as *"9 behind"* only once the remote was named, having first reported *"behind 94, ahead
2069"*, which was a true measurement of the distance to the ANALYSIS-NOTE repo and meaningless as an
answer to the question asked. **A command that silently answers about a different subject is the
failure mode this campaign keeps paying for; substituting one guess for another is not a fix.**

**The generalisation, and it has now cost this campaign four separate errors:** a remote name, an
interpreter version, a hook's liveness and a file's dirtiness are **properties of a checkout, not of
`main`**. `HANDOFF-20260820-2154Z-publication-closeout.md` §2.1 (a dirty `state/sessions.json` at
51,542 B blocking `MANIFEST.tsv`), §2.2 (`build_all.sh` cannot exit 0) and §2.12 (the pre-commit hook
is inert, 7 of 12 checks `SyntaxError`) are all `login19` facts. Measured in the local clone at
`80eeb441`: `sessions.json` is **clean at its committed 46,746 B**, `core.hooksPath` **is** set, and
the hook reports **12 checks passed** under python 3.12.2. Re-measure with an explicit `-C <path>`
and say which tree you are in.

**Test reachability with `git for-each-ref --contains <sha>`, never `git branch -a --contains`,**
which cannot see tags and will declare an anchored commit disposable.

#### PET Gate-6 branch family — preserved 2026-09-03, removal PROPOSED ONLY

Two tags anchor **37 commits across five refs**; no branch has been deleted and no removal
authorization exists. Routed by
[`PROPOSAL-20260903-pet-gate6-branch-preservation-and-removal.md`](PROPOSAL-20260903-pet-gate6-branch-preservation-and-removal.md),
which carries the topology, the two tested cold recoveries, and the exact-ref deletion proposal.

| tag | commit | covers |
|---|---|---|
| `evidence/preserved-pet-gate6-strategy-20260825-a05baab1` | `a05baab141e777d2c77290c3de2bf9844a11e178` | `pet-gate6-strategy-20260825` local + `origin` |
| `evidence/preserved-pet-gate6-gap1-20260830-310d7e63` | `310d7e63d3690f1cd2df5ac3fcaf37ab0c5d39ed` | `codex/pet-gate6-gap1-full-inventory-20260830` local + `origin` |

`0969e787c7773520bfb7076aa24b39ae08852c2e` — the tip of
`origin/codex/pet-gate6-strategy-20260825` — is a strict **ancestor of both** tags and so needs none
of its own. **Measured before tagging: no tracked file on `main` named any of the three tips**
(control: the merge base `e428a645` was found in 4 files, so the search was covering). There was no
discovery route to any of this work.

**`truth_denominator_coverage: 1.0` in the GAP-1 terminal receipt has no producer in any tracked
code** — see the proposal §6. Do not port that receipt verbatim; `OI-182` priced the *different*
token `coverage_is_guarded` and does not cover it. Under `R6`, coverage is the object that reopens
PET, so this is the route by which a quarantined PET result would become canonical.

**Nothing on either tag is live evidence.** PET remains diagnostic/method-development only; Gate 6
remains `BLOCKED`; `C_stat` remains `EXISTS — UNVERIFIED, PAIRING DECLINED`.

### The four removed artifacts with no routed citation

`84607aa3` removed 734 tracked files, all under `docs/orchestration`. Most are covered by the generic
route above. **These four were cited by nothing live**, so a reader had no way to learn they exist;
`HANDOFF-20260820-2154Z-publication-closeout.md` §2.11 identified them. They are **recoverable, and
were never lost** — this section is the missing *route*, not a recovery. Restoring the paths into the
live tree is a separate freeze-scope question and is **not** what this section does.

All four resolve at `evidence/prepublication-2026-08-20-0b329e8a`, verified 2026-08-21:

| artifact (under `docs/orchestration/`) | why it matters |
|---|---|
| `runs/standard-p4-verifier/20260811T132822Z-packetB-final-pass.md` | `OI-7`'s PB3/PB4 evidence |
| `runs/standard-p4-verifier/20260817T045149Z-repair12-verdict.json` | supersedes repair-11, which *is* on `main` |
| `AUDIT-20260819-analysis-note-vs-record.md` (1,375 lines) | the only prior enumeration of the 70; bears on `OI-130`, which is 22% enumerated |
| `state/hpss-residency-inventory-20260812.json` | preservation state behind `OI-131` |

```bash
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'   # `origin` in the local clone; NAME it
git show evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/<path-above>
```

**Note the self-contamination, because it recurs in this campaign:** before this section existed, the
`AUDIT` file's *only* live citation was the document reporting that it had none. A write moves the
population it measures — so "cited nowhere" needs a timestamp and a tree, like any other measurement.

**Resolve citations by SHA, not by path.** A path can resolve at HEAD and read a *different* file
with no error. Measured: `nd-unfolding/mii_anchor_comparator.py` is blob `a7cb2d9b…` at both
`ecee9ff1` and `f7ab02ff`, and `cbeac61d…` at HEAD.

## Regenerate

```bash
python3 docs/orchestration/control_plane_lint.py
python3 docs/orchestration/generate_manifest.py
python3 docs/orchestration/generate_manifest.py --check
```
