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

| order | # | repair | needs from Joseph |
|---|---|---|---|
| 1 | `PR-02` | **F-2(a)** — bind `setup_salloc_env.sh` and `lib/resume_guard.sh` in the `--pair` sets | **`PR-J5`**: can a file sourced *before* the preflight be bound at all? |
| 2 | `PR-03` | **F-7(a)** — pin the §7.0.13 preflight exclusion; three-arm mutation test | — |
| 3 | `PR-04` | **F-8(a)** — produce **P-5 and P-6**, which do not exist and were undisclosed | — |
| 4 | — | **refresh `k0r2/clean`**; re-assert porcelain 0 and `dr-xr-x---` | — |
| 5 | `PR-01` | **F-1(a)** — declare the submission sha; file A-2(a)–(g) against the refreshed tree | — |
| 6 | `PR-05` | **F-17(a)** — re-measure M-1…M-6 **at that sha** on the canonical checkout | — |

**ORDERING CORRECTION, made before anyone walked this — `PR-01` must run LAST of the five, not
first.** My first draft of this file said *"`PR-01` first and alone, because the other four are
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

**The order is therefore:** `PR-02` (needs `PR-J5`), `PR-03`, `PR-04` → **refresh `k0r2/clean` and
re-assert porcelain 0 + write protection** → `PR-01` declares the sha and files A-2(a)–(g) against
the refreshed tree → `PR-05` re-measures M-1…M-6 **at that sha** → fresh non-builder grades Gate 1.

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
