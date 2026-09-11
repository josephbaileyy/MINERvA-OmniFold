# Cost model for the Z adoption plan — pilot, clause-(iii) scan, and the gap list

**Owner:** `z-criteria-owner` lane. **Base:** `6f24fb00`. **Purpose:** input to the orchestrator's
one-page adoption plan. **I do not write the terminal adoption/rejection rule** — I proposed most of
the criteria it would range over, and writing it would be grading my own work.

> ⚠⚠ **EVERY FIGURE BELOW IS A `--time` REQUEST, NOT A MEASUREMENT.** They are the declared walls in
> the launchers. A task requesting 3 h may finish in 20 minutes, so **these are UPPER BOUNDS and
> nothing here is a measured runtime.** The measured figures live in `sacct`'s `ElapsedRaw`, which
> **I have not queried** — that is a records read I was not asked for, and substituting a declared
> wall for a measured elapsed is the launch-plan-read-as-a-record defect this campaign has paid for
> repeatedly. **If the plan needs real numbers rather than bounds, the `sacct` read is a separate
> ask and a cheap one.**
>
> **Metered unit: task-hours.** `r5_meter._calculate_spend` sums `ElapsedRaw` over distinct `sacct`
> task identities, so an array of 100 tasks × 3 h is 300 metered task-hours regardless of throttle.
> Elapsed wall-clock is given separately because it is the schedule, not the spend.

---

## 1. The pilot, priced off the CORRECTED enumeration

**Declared walls, per launcher (`grep '^#SBATCH'`):**

| stage | launcher | array | wall | resources |
|---|---|---|---:|---|
| universe sweep — dump | `sbatch_sweep_bank_5d_dump_bkgaware_gpu.sh` | `0-15` (16) | 3 h | 1 GPU + 32 CPU |
| universe sweep — run | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | `1-169%48` (169) | 1.5 h | 1 GPU + 32 CPU |
| `COMB` + `UTHROW` | `sbatch_finalize_5d_bkgaware_gpu.sh` | — (1) | 1.5 h | 1 GPU + 32 CPU |
| budget combine | `sbatch_combine_5d_budget.sh` | — (1) | 1 h | 4 CPU |
| **`boot_nd_5d`** | `sbatch_bootstrap_5d_gpu.sh` | `1-100%32` (100) | 3 h | 1 GPU + 32 CPU |
| **`seedscan_split_5d`** | `sbatch_seedscan_split_5d.sh` | `1-24%24` (24) | 3 h | 16 CPU + 64 G |

**Two cost groups, and which group is paid per member is exactly Joseph's cause-3 decision:**

| group | task-hours | paid |
|---|---:|---|
| **estimator-downstream** — sweep dump 48 + sweep run 253.5 + finalize 1.5 + combine 1 | **304** | **per member in BOTH branches** |
| **the two dominant block terms** — boot 300 + split 72 | **372** | **once under (b); per member under (a)** |

| `\|K\|` | **(b)** shared blocks: `372 + 304·\|K\|` | **(a)** per-member blocks: `676·\|K\|` | (a)/(b) |
|---:|---:|---:|---:|
| 3 | **1,284** | **2,028** | 1.58× |
| 5 | 1,892 | 3,380 | 1.79× |
| 10 | 3,412 | 6,760 | 1.98× |

**⚠ AND THIS CORRECTS THE EXPECTATION IN THE BRIEF.** The (a)/(b) difference was expected to be
*"likely the single largest number in the plan."* **It is not, and the reason is the term the old
enumeration also omitted:** the **universe sweep is 304 task-hours per member and is paid in both
branches** — comparable to the 372 of the blocks. So the (a)/(b) delta is `372 × (|K| − 1)`, which
at `|K| = 3` is **744 of 2,028 task-hours, 37%** — material, but **not dominant, and it never
exceeds 2× no matter how large `|K|` grows.** The per-member floor is `304`, not `~0`.

**Elapsed wall-clock (schedule, not spend), respecting the declared throttles:**
sweep dump 3 h ∥ sweep run `⌈169/48⌉ = 4 × 1.5 h = 6 h`; blocks `⌈100/32⌉ = 4 × 3 h = 12 h` ∥ split
3 h. **Per member ≈ 11.5 h serial-by-stage; the block group ≈ 12 h.** So **(b) ≈ 12 h + 11.5 h × |K|**
if members run serially and ≈ **23.5 h** if they run concurrently, queue permitting.

**⚠ `|K|` IS A SCIENTIFIC CHOICE AND I AM NOT ASSERTING ONE.** `declared_population` enforces only
`≥ 2` with the baseline present. The statistic is a **max over `K`**, so more members can only
tighten it — but *how many offsets a max needs to be meaningful* is a judgement, not a cost
question. **Precedent in the tree: 3** (`RUNBOOK-20260822:578`, *"verified across all three
members"*). I have priced 3, 5 and 10 so the plan can carry whichever is chosen.

---

## 2. The clause-(iii) scan

**One symmetric eigendecomposition at `n = 10,694`, on `C_0` alone — not per member**, because the
degeneracy predicate is evaluated on the baseline only.

| quantity | value | basis |
|---|---|---|
| arithmetic | `~1.2e12` flops | `O(n³)` for `dsyevd`, `n = 10,694` |
| **time** | **~25 s – 2 min** | ⚠ **A BOUND FROM THE FLOP COUNT at 10–50 GFLOP/s effective, NOT A MEASUREMENT.** Consistent with `z_statistics.s_eig`'s docstring `~1-3 min`, which is itself a **local** figure with runtime explicitly unestablished |
| memory | `~915 MB` matrix + `~2–3 GB` with LAPACK workspace | `10,694² × 8 B` |
| metered | **≪ 1 task-hour** | a single short task |

**⚠ AND THE GRID-RESOLUTION REQUIREMENT COSTS NOTHING. This is the useful result here.** `pinv`
retains `λ_i > rcond · λ_max`, so **retained rank at any `rcond` is a COUNT over the already-computed
spectrum** — `#{i : λ_i > rcond·λ_max}`. Once the one decomposition exists, the entire
retained-rank-versus-`rcond` curve is free at **any** resolution, and locating the step at rank 265
to arbitrary precision is a sort and a search.

**So the grid requirement is a REPORTING obligation with ZERO additional compute**, and the earlier
framing of it as a *"resolution requirement on the scan grid"* overstates its cost. What it costs is
one named field — `λ_min_retained / λ_max` **with its `rcond`** — in the receipt rather than a curve
in a figure.

---

## 3. The gap list — corrected rather than confirmed

**Wrong or overstated in the brief's list:**

| claim | correction |
|---|---|
| *"A-1…A-7 all PROPOSED"* | ⚠ **A-1 is FIXED BY SPEC** (with its count corrected 15 → 19) and **A-2 is CONFORMANCE, narrowed to clause (iv) only**. Neither is a proposal. *"None adopted"* is right; *"all proposed"* is not, and it overstates how much of the set is open |
| *"the projection maps unspecified"* | ⚠ **P1–P4 are APPROVED by Joseph** and the manifest is delivered with axes, dropped axes, weights, support, units and bar types. **What is open is narrower and different:** the **builder revision pin**, and the fact that **no existing builder has both arity and both-direction refusal** — `p4_lib` refuses but is rigidly 5→4; `project_cov_nd` builds all four and drops silently. The specified repair (`project_cov_nd` + both arms) is **code not yet written** |
| *"cause 3's (a)/(b) undecided"* | accurate, but the **framing is now a NARROWING REQUEST**, not an undecided ambiguity — (b) did not exist when the contract was written, so there is nothing to recall and the burden is the proposer's |

**Missing from the list:**

1. **A-5's `k` is hardcoded and undeclared.** `adopt_unified_5d.py` uses `ev[0] >= -1e-12*ev[-1]`;
   A-5 asks for that gate to be **receipt-recorded with `k` declared**. Small, open, unlisted.
2. **The ND rank-truncation scan (clause iii) does not exist.** `RANK-AND-INVERSION:99` requires it
   and `:57`'s scan is **2D only**. It is a protocol obligation in its own right, independent of `κ`.
3. **The projection builder gap above** — arity and refusal separated, no builder has both.
4. **Endpoint B's B-2/B-3/B-4 remain undischarged requirements**, not closed ones. Not a gap for
   *Z adoption* if "adoptable" means endpoint A only — **but the plan should say which it means**,
   because "adoptable Z" reads both ways.
5. **The withdrawal checker's ninth claim is unpinned** — a disclosed residue, deliberately not
   fixed under the standing instruction not to extend that tooling.

**Correct as stated:** Gate 2 FAIL; no adopted 5D trunk; nothing adopted; `κ`'s value withdrawn;
A-6(a) duplicating ruling 10's delivered record with A-6(b) unbound; the digest→execution binding
closed only as a **negative** (the one candidate execution affirmatively excluded, no record
surviving for the rebuild); the block population **three or four** with `2p2h` unresolved and its
cheap route already specified at `PROVENANCE-20260822:233`; `δ_proj` unset.

---

## 4. The pilot's classification — and it is CONTINGENT on the cause-3 decision

**Judged by what its outcomes change, as asked — not by what it measures.**

> ### Under branch **(b)**: **ESSENTIAL.**
> A pass and a fail lead to different actions. **Pass** → the claim *"under the stated
> construction"* is supported for the named projections, and the release proceeds. **Fail** → the
> claim is **false as written**, and the remedy is not a looser tolerance but either declaring the
> estimator baseline as an uncertainty component and propagating it, or narrowing the claim to the
> projections that pass. **Different next actions, so not optional.**
>
> ### Under branch **(a)**: **OPTIONAL — and this is the decision-relevant half.**
> The conditional pilot **holds the blocks fixed**, so under (a) its outcome licenses **nothing
> about the declared subject**. A pass would not support the claim and a fail would not refute it.
> **Same next action either way: run the unconditional test.** However interesting the number, it
> changes nothing — which is precisely the brief's own test for *optional*.

**⚠ AND A THIRD STATE THAT IS NEITHER: TODAY THE PILOT CANNOT PRODUCE EITHER OUTCOME.** `δ_proj` is
unset and `κ`'s value is withdrawn, and with `κ = None` `evaluate_a7` returns `KAPPA_UNDECLARED`
with `s_proj = None` **for healthy baselines too**. **So running it now yields a refusal that
changes nothing, at full cost.** Its two prerequisites are a scalar from Joseph and a ratio from the
scan.

**THE ONE RECOMMENDATION I WILL MAKE ABOUT SEQUENCING, since it follows from the above rather than
from preference: the cause-3 decision comes first, because it determines whether the pilot is
essential or optional — and it costs nothing.** Deciding it after the pilot runs risks paying
`1,284`–`2,028` task-hours for a result that branch (a) would render unlicensing. **The cheapest
item in the plan is the one that prices the most expensive.**
