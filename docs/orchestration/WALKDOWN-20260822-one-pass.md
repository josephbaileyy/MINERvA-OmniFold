# ONE-PASS WALKDOWN — 2026-08-22

**CITABLE FOR:** the ORDER of the remaining publication work, and which step blocks which.

**NOT CITABLE FOR:** any physics number, any state, any authorization. Every factual field lives in
`PUBLICATION-READINESS-20260822.md` (as amended) and is re-measured there, not here. **This file is
an ORDERING, deliberately thin, so that it cannot drift into a second source of state.**

**Built** 2026-08-22 by the close-out lane at `b7f11fde`, after an independent peer review whose four
objections were all accepted (`PUBLICATION-READINESS-20260822.md` § AMENDMENT 1).

**Why a walkdown and not a longer list.** Joseph asked to walk one list once. The readiness document
is the *inventory*; it is 1 300 lines because every row carries the command that measured it. This is
the *route through it*. Read them together: a step here is a pointer, and the pointer wins.

---

## STATUS — GATE 1 GRADED 2026-08-23 AND IT DOES NOT PASS

**16 PASS / 2 FAIL / 0 NOT-EVALUABLE**, by a fresh non-builder
(`GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md`). Failing `F-2(a)` and `F-17(a)`.
**The k=0 rehearsal is NOT launched; `PR-J1` does not become operative; Gate 2 cannot be graded.**

**The decisive finding invalidates the shape of Step 1, not just two of its rows.** Every
repo-relative shell file below `setup_salloc_env.sh` is **ABSENT from the declared code root**, so
every launcher aborts at the activator with exit 1 — **`PR-02`'s gate passes and is the last thing
that happens.** The builder lane re-measured every decisive claim and **contradicted none**
(`CONFIRMATION-20260823-builder-response-to-gate1-round4.md`).

**So Steps 1.1–1.5b are DONE-BUT-VOID rather than done.** They are correct work on a tree that
cannot run. `PR-01`'s declaration is **true and void** and expires on the repair; `P-5` is
incomplete; `M-5` is the `F-17(a)` FAIL. The table below is kept as the record of what was built.

**THE NEXT STEP IS A JOSEPH DESIGN DECISION, not a repair this lane may take.** The minimal fix needs
a **third root, `MNV_ENV_ROOT`**, mandatory with no default, plus a **digest-bound environment
manifest** verified before the source (git structurally cannot bind those bytes), a fail-closed
`PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH` scrub, and the `_mr_lib` check moved above the source in all
eight. That is the same class as ruling 17's two-root split. **Do not add `set -u`** — a documented
job kill.

---

## STATUS — 2026-08-22, THE BUILD PASS (superseded above, kept as the record)

**Every already-authorized step is DONE. What remains is Joseph-only or a fresh non-builder.**

| step | item | state |
|---|---|---|
| 0 | cause-3 scope | **RULED** — ruling 24, `X`-specific, 2D not reopened |
| 1.1 | `PR-03` / F-7(a) — pin the preflight exclusion | **DONE** `b49bc360` |
| 1.2 | `PR-02` / F-2(a) — verify before source | **DONE** `6113a34d` — **FIRST HOP ONLY** |
| 1.3 | refresh `k0r2/clean` | **DONE** — `de040d9b` → `6113a34d`, ff, A-2(g) re-applied and re-verified |
| 1.4 | `PR-01` / F-1(a) — declare the sha | **DONE** — 775 files, `cc004894…`, A-2(a)–(g) all MET |
| 1.5a | `PR-04` / F-8(a) — P-5 and P-6 | **DONE** — 8 entrypoints / 14 invocations; one child, WRAPPED |
| 1.5b | `PR-05` / F-17(a) — M-1…M-6 | **DONE** — four moved, two stale in the builder's favour |
| 1.6 | **grade Gate 1** | **BLOCKED — FRESH NON-BUILDER.** This lane built 1.1–1.5 |
| 5 | `PR-06` — commit the P3S packet | **DONE** — packet committed; three tracked files were also STALE |
| 5 | two stale canonical rows | **DONE** — ledger corrected; the runbook is `immutable=yes` and was NOT edited |

**GATE 1 IS NOT CLOSED, and must not be recorded closed**, per Joseph 2026-08-22: the
**transitive environment trust boundary** must be settled *and* passed by a fresh non-builder.
`setup_salloc_env.sh` sources two **untracked** scripts that activate conda and ROOT/MINERvA101; no
git-based check can bind them.

### What is left, and who owns it

| owner | item |
|---|---|
| **fresh non-builder** | grade Gate 1 (1.6); settle the transitive trust boundary |
| **Joseph** | `PR-J1` (confirm k=0 once Gate 1 passes — already conditionally granted by ruling 12); `PR-J3` sizing; `PR-J2`/`OI-75`; `PR-J8`; `PR-J9` (**split it first**); `PR-J10` |
| **gated** | the k=0 rehearsal (step 3) — needs Gate 1 **and** `PR-J1` |

### Two items deliberately NOT started, with reasons

- **Cause 3's `P-i` and `P-ii`** — cheap, no compute, and identified in ruling 24 as independent of
  the family. **Not started because they edit production estimator code**
  (`analyze_universes_5d.py` needs a new write site), which would move the `.py` count and
  **invalidate the sha declared today**. They belong after the k=0 rehearsal, or before a fresh
  declaration — not between the two.
- **The specification-side checklist/linter** — endorsed in its narrow form (18 Gate-1 rows, explicit
  P-5/P-6 subrows, three mutation tests). **Not started because this lane is the builder**, and the
  builder authoring the artifact the grader grades against is the conflict the fresh-non-builder rule
  exists to prevent. It should be written by the grading lane.

---

## THE SHAPE, IN ONE PARAGRAPH

There are **two independent tracks** and they do not block each other. **Track A** is execution
integrity: five Gate-1 repairs, then a k=0 rehearsal — all of it authorized in principle already, and
useful no matter how the physics scope lands. **Track B** is a scope question that decides whether
the 50-member M(ii) family exists at all — roughly 2 000 GPU-hours and 2.17 TiB, or nothing. **Track B
is one ruling and Track A is weeks of work, so Track B should be asked first even though Track A can
start immediately.** The failure mode to avoid is finishing Track A and then discovering Track B
deleted its purpose.

---

## STEP 0 — JOSEPH, AND IT GATES THE LARGEST SINGLE COST ON THE BOARD

**Ask.** *Is cause 3 (estimator-seed variation) scoped to `X`, the scalar-5D GBDT covariance, only —
or to any training-seed-variation covariance the collaboration publishes?*

**Why it is now the top of the list, and why it was not yesterday.** Measuring §0 falsifier (c)
against the LaTeX build graph showed the **paper** already quotes no 5D covariance magnitude
(`sec_systematics.tex` is reached from `main_note.tex` only; `paper_body.tex` has zero `\input`).
So "narrow the scope" is not a decision for the paper — it is the state at HEAD. But the same read
found `paper_body.tex:58-60`: the finalized **2D** budget *"combines … ML (training-seed variation)"*
covariance. **That is cause 3's subject matter in a published artifact, and nobody has written down
whether cause 3 reaches it** (`PR-X3`).

- If cause 3 is **`X`-only** → the quarantine branch is note-scoped, and `PR-J3`'s family sizing is a
  real but bounded question.
- If cause 3 reaches **any published training-seed covariance** → the finalized 2D result is inside
  the quarantine, and **the branch does not collapse by scoping at all.** This would be the single
  largest change to the readiness document.

**What this step is NOT.** It is not permission to declare cause 3 `N/A` to avoid its cost. The
cause-5 precedent supplies the *route* for a per-(cause × artifact) `N/A` and **its reasoning runs
adverse** — `VL66` turned on a construction-path trace showing PET weights are **not inputs** to `X`,
whereas cause 3 concerns `X`'s **own** estimator. A fresh construction-path argument is required, and
*"nothing enforces the gate in code"* is an enforcement defect, not an argument.

**Cost to answer.** One artifact-side sentence of the form `VL66` already wrote.

---

## STEP 1 — LANE, STARTS NOW, BLOCKS ON NOTHING IN STEP 0

The five Gate-1 round-4 repairs. Gate 1 currently **DOES NOT PASS: 13 PASS / 5 FAIL / 0 NOT-EVALUABLE.**
All five are inside rulings 18–22 and need no new authorization.

**The order below is a topological sort of the dependency edges the readiness list already records,
not a hand-written sequence.** The edges, quoted: `PR-04` *"Blocked by PR-01"*; `PR-05` *"Blocked by
PR-01"*; `PR-01` *"falsified by … any change to `k0r2/clean`; any `.py`/`.sh` add or delete"*; `PR-02`
*"plus one Joseph decision"* (`PR-J5`); `PR-03` blocked by nothing. **All five block Gate 1.**

| order | # | repair | blocked by | cluster? |
|---|---|---|---|---|
| 1 | `PR-03` | **F-7(a)** — pin the §7.0.13 preflight exclusion; three-arm mutation test | **DONE 2026-08-22, `b49bc360` on `build-k0-execution-integrity`** | no |
| 2 | `PR-02` | **F-2(a)** — bind `setup_salloc_env.sh` and `lib/resume_guard.sh` in the `--pair` sets | **`PR-J5`** (Joseph) | no |
| 3 | — | **refresh `k0r2/clean`**; re-assert porcelain 0 and `dr-xr-x---` | `PR-02` (it edits executing bytes) | **write** |
| 4 | `PR-01` | **F-1(a)** — declare the submission sha; file A-2(a)–(g) against the refreshed tree | the refresh | read |
| 5a | `PR-04` | **F-8(a)** — produce **P-5 and P-6**, which do not exist and were undisclosed | `PR-01` | no |
| 5b | `PR-05` | **F-17(a)** — re-measure M-1…M-6 **at that sha** | `PR-01` | read |
| 6 | — | **fresh non-builder grades Gate 1** | 5a and 5b | — |

**`PR-04` and `PR-05` are independent of each other** and are the only pair that can run in parallel.

**`PR-03` was the only repair that could begin before Joseph answers anything, and it is DONE** —
`b49bc360`, pushed. Three artifacts: `nd-unfolding/mnv_preflight_exclusions.json` (schema
`mnv_preflight_exclusions/1`), `nd-unfolding/mnv_preflight_census.py` (enumerate first, classify
second; exits 0/2/3), and 13 test arms. Measured by **two independent instruments before either was
written down**: 8 launchers, **30 non-comment `python3` invocations = 14 guarded + 16
declared-preflight + 0 unclassified**, plus **9 commented-out `python3` lines**. Ruling 21's 14/30
boundary reproduces for a fourth time, and **a test asserts 14, 30 and 16 for the first time.** Suite:
13 new arms pass, 127 pass across the four coupled modules.

> **It moved the file count, exactly as the ordering predicted:** 773 → **775** tracked `.py`/`.sh`.
> `PR-01` must be taken after this and after the refresh. No committed manifest record went stale in
> the meantime — `SRCMAN_RECORD` has no default and is generated from `MNV_CODE_ROOT` at deploy time.

**Everything else in Step 1 now waits on `PR-J5`**, which is a small question sitting in front of the
whole remaining queue. **Ask it in the same message as Step 0** so the lane is not idle behind the
cheap one.

**ORDERING CORRECTION, made before anyone walked this — `PR-01` runs FOURTH, and my first draft had
it first.** (It is not "last" either: `PR-04` and `PR-05` both depend on it.) My first draft said *"`PR-01` first and alone, because the other four are
measured against that sha."* **That is wrong and it would have produced a false declaration.**

- The tree that actually executes is the frozen deploy at `/pscratch/sd/j/josephrb/k0r2/clean`,
  `de040d9b`, porcelain 0, `dr-xr-x---`. `PR-01` declares **that** sha.
- **`PR-02` edits the eight launchers themselves** — it adds `--pair` arguments to
  `sbatch_bootstrap_5d_gpu.sh`, `sbatch_seedscan_split_5d.sh`,
  `sbatch_unfold_5d_detector_bkgaware_gpu.sh`, `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh`,
  `sbatch_uthrow_run_5d_fast.sh`, `sbatch_uthrow_block_5d.sh`,
  `sbatch_uthrow_combine_5d_fast.sh`, `sbatch_finalize_5d_bkgaware_gpu.sh`. **Those are executing
  bytes.** They must reach `k0r2/clean`, and `PR-01`'s own expiry clause says *"falsified by … any
  change to `k0r2/clean`; any `.py`/`.sh` add or delete (moves `file_count`)."*
- So declaring first would pin a sha that `PR-02` then invalidates — **`measure after the rebase, not
  before`**, in its exact classic form.

**And the same draft put `PR-04` third, which is wrong for a second reason:** the readiness list
records `PR-04` as *"Blocked by PR-01"* outright, because both of its artifacts are defined *"at the
pinned sha"*. So does `PR-05`. **Three of the five repairs sit downstream of a declaration my draft
had scheduled first.** The corrected order is the table above.

`PR-01` remains correctly described in the readiness list as *"blocked by nothing"* — nothing
**blocks** it. What it needs is to be **last**, which is a different property, and this file is where
that belongs.

**`PR-04` carries the round's own lesson.** P-5 and P-6 being absent *and undisclosed* is the same
shape as round 1's P-4. A mechanism that does not exist must be reported as **NOT-EVALUABLE**, never
folded into a green count — and a green arm with no repository imports is indistinguishable from a
clean run, so `"checked": guard.checked if guard is not None else 0` makes the containment-path zero a
**default, not a measurement**.

**`PR-05` is SELF-FALSIFYING** — its M-2 is a name intersection over 717 untracked files that the
k=0 run itself perturbs. It is last in the order above, and it must be **re-run immediately before
Gate 1 is graded**, not inherited from the first run.

**Cluster steps, corrected.** The readiness list calls `PR-05` *"the only one of the five that needs
the cluster"*. With the refresh inserted that is no longer true: **steps 4, 5 and 6 all touch
`saul.nersc.gov`** — the refresh writes to `k0r2/clean`, and `PR-01` and `PR-05` read it. Only the
refresh is a write, and **no job is submitted anywhere in Step 1.**

**Grading rule, unchanged:** the grader is a **fresh non-builder**. This lane built the repairs and is
disqualified from grading them.

---

## STEP 2 — JOSEPH, CHEAP, AND IT IS A CONFIRMATION NOT AN AUTHORIZATION

`PR-J1`. Ruling 12 **already conditionally authorized** exactly one member, `MNV_EST_SEED_OFFSET=0`,
through its stage-1 verdict — *not operative* until a fresh non-builder records a clean Gate-1 PASS.
So when Step 1 goes green this is a confirmation, not a fresh ask. Also decide **`PR-J5`** here if it
has not already unblocked `PR-02`.

---

## STEP 3 — LANE. THE k=0 REHEARSAL

Ruling 14: the first complete member **IS** the Slurm rehearsal — a production submission, not a stub
test. Per `PLAN-20260822-oneMember-mii-staged.md`: ~53.6 A100-h, 47.1 CPU-h, 47.7 GB.

**Two things this run does NOT do, both previously claimed and both wrong:**
1. **It does not reconcile 151 vs 2 680 A100-h.** Those count different populations (50 Gate-5 PET
   `C_stat` replicas vs 50 M(ii) members); no member measurement can reconcile them. That section of
   the plan is **withdrawn**.
2. **It does not discharge cause 3.** *"It buys the magnitude recorded UNRESOLVED … measured is not
   acceptable. This authorization funds an operand, not a conclusion."*

What it **does** buy: a real per-member unit cost and footprint, which is the operand Step 4 needs.

**Prepare the Gate-2 reviewer and the post-rehearsal decision packet BEFORE submitting**, so the
post-run review is not selected by the builder after the fact. That is the whole point of the
two-gate split (8 pure pre, 10 SPLIT, 0 pure post).

---

## STEP 4 — JOSEPH. FAMILY SIZING, AND IT IS A POLICY CALL

`PR-J3`, and **only if Step 0 left the branch alive.** Re-measure first: the margin is 0.159 TiB, so
**163 GiB of unrelated churn flips the answer**, and Step 3 itself moves it.

**Framed correctly** (peer review, accepted): 46 members clear the **lane-authored ~90% operational
line**; 50 do not. That line is **unsourced, single-lane, same-day, and enforced by nothing in code**.
The quota is **soft 20.00 TiB / hard 30.00 TiB**, and the projected 18.16 TiB is **60.6% of hard** —
the filesystem would not block it. It is a serious operational warning about a **soft** limit, not an
impossibility. Both escape routes are closed: HPSS holds four more members, and `MVFINAL_j` has no
producer, reader or deleter.

**The only lever that scales** is funding `MVFINAL_j`: the 41.44 GB intermediate is **86.8%** of the
per-member footprint, and releasing it collapses the family to ~0.29 TiB. **That is taskable to a lane
today and it is the highest-leverage engineering item on the board** — it converts Step 4 from a
sizing compromise into a non-question. Consider dispatching it during Step 1.

---

## STEP 5 — THE REST, WHICH IS ORDINARY AND SHOULD NOT BE SEQUENCED BEHIND THE ABOVE

Run in parallel with Steps 1–4; none touches the critical path.

- **`PR-06`** — commit the P3S standard lateral packet. **It is BUILT and validated, NOT committed,
  NOT adopted** (stages 4–6 ran 2026-08-16; stage 5 PASS on 11 gates; lateral block moves −0.03%;
  `p4_adopt_standard.py` has never run). **This is the item most likely to be lost to a `/pscratch`
  purge rather than to a decision — it should not wait for anything.**
- **Two stale canonical rows** contradicting it: `VALIDATION_LEDGER.md:733` and
  `RUNBOOK-20260807-gbdt-closeout.md:38` both say the P3S lateral is "NOT BUILT".
- **Twelve canonical records measured stale** — `PUBLICATION-READINESS` §9.
- **The specification-side checklist/linter** Joseph endorsed in its narrower form: 18 Gate-1 rows,
  explicit P-5/P-6 subrows, three decisive mutation tests. **Not a general framework.**
- **`PR-J2` (`OI-75`)**, **`PR-J8` (`OI-31`)**, **`PR-J9`** (which **bundles several distinct
  questions** and should be split before it is asked), **`PR-J10`**, **`PR-J12`**.

---

## WHAT WOULD MAKE THIS WALKDOWN WRONG

- **Step 0 ruling either way.** It re-orders everything below it.
- **Any commit**, for the same reason the readiness document says so: its fields are sha-bound.
- **A `/pscratch` purge**, which moves `PR-06` from "not committed" to "lost" without touching a file
  in this repo.
- **Treating a heading count as an ask count.** There are 12 `PR-J*` headings and **8 fresh asks plus
  1 confirmation**, with `PR-J9` still to be split. Do not size work from the heading count.
