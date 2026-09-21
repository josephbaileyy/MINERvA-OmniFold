# PREREGISTER 2026-09-11 — acceptance criteria for the precursor repairs (b)-(g) and admission
# accounting, fixed BEFORE the implementation exists

**CITABLE FOR:** the criteria `P1`-`P18` in §3, the baseline verification in §2, and the recusal
boundary in §4.
**NOT CITABLE FOR:** any approval, any launch, any adoption, any grade, or any statement that a repair
satisfies anything — **no repair existed when this was written.** `R4` suspended; Gate 2 FAIL; endpoint
B requested-but-unvalidated and not authorized for execution.

**Why this record exists, and why it is dated before the work.** This lane is the designated independent
end-to-end reviewer for repairs it did not author. The requester briefed it **before** the
implementation was written precisely so the verdict is not spent reviewing a remedy this lane helped
shape (`offering-a-remedy-spends-my-next-verdict`). **Fixing the yardstick now is what makes the later
review checkable**: a criterion written after reading an implementation cannot be shown not to have
been fitted to it. **No remedy is proposed anywhere in this document** — every item below states a
property to be demonstrated, not a way to achieve it.

**Subject state at authorship:** repairs (b)-(g) and the admission accounting **DO NOT EXIST**. The
implementation owner is working in an isolated worktree and has not reported.

## 1. The five areas, as routed

Named by the requester: (1) mutation controls must **reach** the guard they target; (2) population
validation must check **identities and coverage, not counts**; (3) the shared namespace must be
enforced by a **refusal**, and `mii/` likewise; (4) admission accounting must **reuse** `r5_meter.py`,
bound charged spend **plus maximum remaining exposure including queued and retries**, and not depend on
the naive-`--starttime` basis; (5) **positive controls** — a healthy input each guard passes silently.

## 2. Baseline, verified rather than accepted

`main` locally at **`77a4af38`**, parent `6f24fb00`.

- **⚠ `origin/main` is still `6f24fb00`. The landing is NOT PUSHED.** Measured after an explicit
  `git fetch origin`: `main` is **1 ahead, 0 behind** `origin/main`. The briefing states *"`main` moved
  `6f24fb00` -> `77a4af38`"*, which is true of **this shared local checkout only**. Any session or
  reviewer fetching `origin` sees none of it, and the project rule is that a result is live only once
  its evidence lands in a commit **that is reachable**. This is `a-hold-on-shared-main-is-not-a-hold`
  in the other direction — pushed-ness is a branch property and must be measured, not inferred from a
  landing narrative. **Recorded as an operational finding, not a defect in the work.**
- **The `--no-verify` disclosure CHECKS OUT.** `da1da9f4` is present as an object in this repo and is
  reachable from **no ref** (`for-each-ref --contains` returns nothing). `da1da9f4` and `77a4af38` have
  **byte-identical trees** — both `1447639b4ea3c450268e038db3a4aaf4414ed1e3` — the same parent
  `6f24fb00`, and the same subject. So the two differ in commit identity only, exactly as disclosed.
  The requester asked for this to be checked because it was the one asserting it; it holds.
- **The landed set is exactly the minimal self-consistent one** — 4 paths: `M
  docs/orchestration/MANIFEST-overrides.tsv`, `A docs/orchestration/state/probe-z-projected-stability-20260910.py`,
  `A nd-unfolding/tests/test_z_build_path.py`, `A nd-unfolding/z_build_path.py`.
- **"Code-only is not self-consistent" is CONFIRMED at the mechanism.**
  `test_z_build_path.py` `SANCTIONED` carries five keys, one of which is
  `probe-z-projected-stability-20260910.py`, and
  `test_every_sanctioned_exclusion_still_exists` asserts each key `assertIn(name, present)` with the
  message *"remove it rather than leaving it to silence nothing"*. A code-only landing therefore leaves
  that assertion red. The reasoning is sound and the remedy chosen was the minimal one.
- **365 tests CONFIRMED**, re-run here with `TMPDIR` set: `test_z_build_path` **90 OK**,
  `test_z_contract` **57 OK (1 skip)**, `test_z_assembly` **58 OK**, `test_z_validator` **136 OK**,
  `test_z_build` **24 OK (2 skips)** = **365**.
- **The landed suite already self-reports a power arm**, which bounds what §3's `P1`-`P4` must add
  rather than duplicate: *"50 refusal points parsed … 43 behaviours demonstrated by name — a DIFFERENT
  set, not a one-to-one cover"*, *"3130 .py files scanned; `s_proj(` appears in 15"*, and *"all 43
  detectors demonstrated on a rejecting mutation."* **Note the 43-of-50 gap is disclosed with a
  reason** — it is not a hidden shortfall.

## 3. The criteria — `P1`-`P18`

### Area 1 — a mutation control must REACH its guard

- **`P1` — Reach, demonstrated per mutation, not per suite.** For each repair's mutation control, the
  record must show the mutated input **arrived at the targeted guard**, not that the suite went red.
  A digest, schema or argument check that refuses the mutation **first, with the same exit status**,
  tests that earlier check. The BEN-450 precedent is the standard: `3be8c052` exists because a ROOT
  stub could not distinguish WRITTEN from BUILT, so deleting `hmask.Write()` left the suite green.
- **`P2` — Distinguishable failure.** A mutation's failure must be distinguishable from an
  infrastructure refusal by something other than exit status — the guard's own message, or a direct
  call to the unit (`a-mutation-test-can-be-refused-before-it-reaches-the-guard`).
- **`P3` — UNKILLED is reported, not absorbed.** Any refusal point with no killing mutation must be
  listed **by name with its reason**, as the landed suite already does for its 7. An undisclosed
  shortfall is the defect; a disclosed one is a scope statement.
- **`P4` — The fixture may not be derived from the rule it tests.** Fixtures must be built from the
  **producer's** own objects/metadata. A fixture derived from the predicate cannot disagree with it
  (`a-fixture-derived-from-the-rule-cannot-disagree-with-it`).

### Area 2 — identities and coverage, not counts

- **`P5` — The declared set is enumerated, and the assertion is over identities.** Completion must be
  asserted against the **declared id set**, with the missing ids **named** on failure. A count
  comparison is insufficient and `--expected-ids` **does not currently exist in any of the four
  launchers** (measured: zero occurrences) — so the repair must not cite it as pre-existing.
- **`P6` — Both directions.** The validator must fail on a **short** population *and* on an
  **unexpected/extra** id. A one-directional check waves the other through
  (`a-filter-needs-a-test-in-the-direction-it-acts`).
- **`P7` — Every arm, named.** All four arms must be covered — dump `0-7`, block `0-20`, run `0-39`,
  combine. The block population is presently asserted by **nothing** (a bare
  `--block-slabs '…/block5d_*.npz'` glob), and the dump population by nothing.
- **`P8` — A glob is not a population.** Wherever a glob selects inputs, the count and identity of
  matches must be checked against the declared set **before** consumption, and a mismatch must refuse.
- **`P9` — The population must be non-empty by construction.** A validator that passes because its
  population is empty is a gate that cannot fail (`BEN-032`/`BEN-025`,
  `a-criterions-declared-population-can-be-empty`). Every Σ in a derived population must be expanded.

### Area 3 — refusal, not reliance on undeclaredness

- **`P10` — Non-emptiness refuses.** The run must **refuse to start** if its output namespace is
  non-empty, distinguishing **absent** from **empty** explicitly. All five namespaces measured
  non-fresh (8, 36, 40, 160 npz and 374 bank files). A `count == 0` test that cannot tell absent from
  empty does not satisfy this.
- **`P11` — Writer and reader agree, proven on the UNDECLARED path.** The namespace the block leg
  writes and the one the combine reads must be shown identical **for an undeclared run**, which is the
  precursor's own case and the branch where the mismatch is currently **silent** rather than loud.
- **`P12` — `mii/` is a refusal.** Exclusion of `mii/` must be enforced by a check that **fires**, not
  by `MNV_EST_SEED_OFFSET` happening to be unset. It must not rest on `mr_declared()`, whose single
  predicate means both *"member of K"* and *"build your own blocks."*
- **`P13` — `sys.path[0]` is named per entrypoint.** Every entrypoint must state what owns
  `sys.path[0]`. Four mechanisms compete for one slot — a Python `insert`, a `cd` plus bare
  `python3 f.py`, `-m`, and `PYTHONPATH` — and `sbatch_uthrow_dump_5d.sh:12-14` currently achieves the
  OI-136 defect **by `cd`**, invisible to a search for the repaired insert idiom. A guard-marker parity
  check across sibling launchers must show **no row of zeros**.

### Area 4 — admission accounting

- **`P14` — Reuse, do not reimplement.** The accounting must **call** `r5_meter.py`. A retyped rule is
  a second implementation and will diverge (`a-rule-retyped-is-a-second-implementation`).
- **`P15` — The bound is charged spend PLUS maximum remaining exposure of every admitted task,
  including queued and retries.** `r5_meter` charges **elapsed-so-far** and does count RUNNING
  attempts (fixture-proven: 3.0 h from 1.0 COMPLETED + 2.0 RUNNING; PENDING skipped), so a spend-only
  check leaves the in-flight commitment unbounded — up to `40 × 6 h = 240` CPU task-h at `%40`.
  **Retries must be included: R5 counts a failed task in full.**
- **`P16` — Explicit UTC, and a test that would fail on the naive basis.** The query must not depend on
  a naive `--starttime`, which `sacct` parses in the host zone (uniformly PDT) and which under-reads
  spend. A test must exist that **fails** if the naive basis is reintroduced.
- **`P17` — R5's running-at-the-stop rule is PRESERVED.** *"Jobs running at the stop run to completion,
  spend counted; no new submission after the stop"* is the ruling's design. A repair that terminates
  running jobs to hold a ceiling **contradicts R5** and must be refused. **The cap must bind at
  ADMISSION**, which is the only place it can bind without violating the rule — and note the worst-case
  total measured at `109.84` CPU task-h against the proposed `100` cap, `48` h of it in the unmeasured
  dump arm.

### Area 5 — positive controls

- **`P18` — Each guard passes a healthy input SILENTLY, and the control is the same call path.** Every
  guard needs an arm proving it does **not** fire on correct input, so a guard that refuses everything
  is detectable; and the healthy arm must traverse the **same** entry point as the firing arm, or it
  proves the wrong thing (`a-guard-that-fires-on-every-correct-run-is-not-a-guard`,
  `a-power-test-proves-power-in-its-fixtures-language`).

## 4. Scope, recusal, and the donor question

**This lane authored none of the repairs and proposes none.** `P1`-`P18` are **properties to be
demonstrated**; how to satisfy them is the owner's. If this lane is later asked to supply a fix, it
must say so on the artifact and a replacement reviewer must be routed **before** the fix is written.

**The donor question is flagged as instructed, and this lane will treat any silent resolution of it as
a finding.** The requester has measured that `z_assembly.py` contains **no donor binding at all** and
that `z_build_path.py` binds only the `C_stat`/`C_ML` block source, and has returned *which* donor
supplies a band to Joseph rather than letting implementation choose. **A choice of donor appearing in
code without a committed decision is a decision taken by implementation**, which is the shape
`measurability-must-not-choose-the-specification` names: the cheap branch assumes away the hard term.
**This lane does not adjudicate the donor question and will not answer it.**

**Carried disqualifications, unchanged:** recused from **grading** any leg (`BEN-381`); disqualified on
clause (d)/`A-4`'s tolerance (Part E §E.1, Part H §H.3); declared partial self-confirmation on §2.1a(b),
§3.1's inertness paragraph, `A-2`'s narrowing and `F7`'s row wording.

## 5. What this record did not do

It approved nothing, launched nothing, submitted nothing, implemented nothing, and graded nothing. It
read `main` at `77a4af38` and `origin/main` at `6f24fb00`, ran the five Z suites locally (**365 OK**)
and the `r5_meter` fixture. **No repair existed to assess.** The decisions are Joseph's.
