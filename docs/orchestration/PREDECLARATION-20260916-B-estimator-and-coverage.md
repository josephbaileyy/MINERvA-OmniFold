# PREDECLARATION — `B`'s estimator and the repeat-count coverage objective

**Owner:** `owners.tsv:14`, `z-criteria-designer session [91eaa2]`. **Assignment:** accountability for
`B`'s justification, `DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md` §2.3, committed
`df0a8603`, verified in the record rather than accepted on relay. **Base:** `f5d609ae` (lane).

**CITABLE FOR:** `Z_CONSTRUCTION_PLAN` §4.4a **item 4** (a predeclared estimator of `B`) and **item
5** (a coverage/confidence objective for the repeat count), which are zero-compute, are judgement,
and **gate** the arm-7 evidence.

**NOT CITABLE FOR:** anything adopted. `B` is **not declared** here — its *estimator* is. `ε = 1e-9`
remains **PROPOSED and UNGRADED**. Gate 2 remains **FAIL**, `cause3_corr` remains **WITHHELD**,
endpoint B remains **DEFERRED NOT PASSED**. No value from `nd-unfolding/mii/member_k000000/` is
quoted. **No compute is authorized by this document, none is requested, and none has been run.**

⚠ **I AM THIS PREDECLARATION'S AUTHOR AND THEREFORE CANNOT BE ITS ASSESSOR** — that is
`owners.tsv:15`, `z-independent-assessor session [cb0b6b]`.

⚠ **THE INDEPENDENCE RESIDUAL, ON THE FACE OF THE DOCUMENT RATHER THAN IN A FOOTNOTE.** I refused
`B` twice on the ground that `S` must be independent of it; the record assigned it anyway. Route (i)
genuinely weakens the objection, because a pin is a **design act** rather than a judgement — but
**item 4 is a judgement**, and I am making it while owning `S`. **The objection is reduced, not
removed.** `[cb0b6b]` should read §1 knowing that.

---

## 1. ITEM 4 — the predeclared estimator of `B`

**DECLARED, before any observation: `B = 0`, asserted as a property of the PINNED DESIGN, verified
by a BOOLEAN test. No observed magnitude enters `B`.**

    ESTIMATOR   Let the arm-7 runs of §2 produce persisted CV vectors x_1 ... x_n.
                IDENTICAL := for all i, j:  x_i and x_j are BITWISE equal, elementwise,
                             over the reported support (the `x_cv > 0` predicate, never a
                             hardcoded 10,694).
                IF IDENTICAL:      B = 0.
                IF NOT IDENTICAL:  B is UNDEFINED and route (i) is FALSIFIED.
                                   B is explicitly NOT set to the observed difference.

### 1.1 Why this discharges Gap 3 *by construction*

§3.7a Gap 3 is *"the estimator of `B` must be **predeclared**, because two arms do not prevent
tuning."* The complaint is that an estimator chosen after seeing the numbers can be steered. **This
estimator has no knob to steer**: its range is `{0, undefined}`, and it is not a function of any
observed magnitude. There is nothing to tune, so the gap closes structurally rather than by promising
restraint.

### 1.2 ⚠ Why this is admissible where the withdrawn fallback was BARRED — the load-bearing distinction

A peer's earlier fallback would have declared `B` from the precursor's two persisted executions.
**That was barred, and the composition is recorded at
`DECISION-SUPPORT-20260916...md` §2.4:** `S` is non-binding, so `ε` must be argued from `B`'s side;
`SPEC:1410` says *"`ε` may not be read off Z's own null"*; therefore `B` taken from Z's own null puts
`ε` there too, with one indirection.

**A boolean does not read a VALUE off the null.** The fallback read a **magnitude**. This estimator
reads only *identical / not identical*. **That is the whole difference between route (i) and the
barred route, and it is why item 4 must stay boolean even if a number is available and tempting.**
If a future revision replaces `IDENTICAL` with a tolerance, or records the observed difference *as*
`B`, it re-enters the prohibition — so that substitution is named here as the thing to refuse.

### 1.3 The design intent is already written in the launcher, not invented here

`sbatch_uthrow_combine_5d_fast.sh:9` (arm 7, where the null operands are computed):

> *"`--null` repeats CV at the identical seed and **must be zero** (no jitter subtraction)."*

**MEASURED.** So `B = 0` makes explicit a claim the production launcher already asserts. I am not
proposing a new standard; I am declaring the estimator for a property the code already claims and
nothing has verified.

### 1.4 ⚠ What `B = 0` does NOT deliver, stated because it is the tempting inference

`B = 0` gives `B ≤ S` trivially for any non-negative `S`, so §1894's requirement is satisfied. **It
does not give `ε`.** A gate at `ε = 0` fails on any nonzero deviation whatever, which is the
mirror-image of the `1e-12`-clamp defect §3.1a measures; and `ε` may not be read off Z's own null, so
no positive `ε` follows from these observations either. **`ε = 1e-9` therefore continues to stand or
fall on §C.3's transfer argument alone, unaffected by this predeclaration** — its own falsifier
remains **UNEVALUATED** pending a pinned-envelope repeat on Z's bank.

---

## 2. ITEM 5 — the coverage objective, and it is over ALLOCATION SHAPES, not repeat count

§3.7a Gap 2 is *"the repeat count needs a coverage/confidence objective and its sampling
assumptions."* **The sampling assumption is the part that has been missing, and it decides everything
else**, so it is declared first.

### 2.1 Two models, and a design that does not name its model cannot justify its `n`

| | **MODEL A — deterministic given the allocation** | **MODEL B — stochastic per run** |
|---|---|---|
| mechanism | thread count and reduction order are **properties of the allocation** (§3.7a's own words), so two runs in the *same* shape agree trivially and only *different* shapes test anything | some per-run source flips independently with probability `p` |
| what `n` buys | **nothing by itself** — distinct allocation shapes are the currency | confidence against `p ≥ p0` |
| minimum | **3**, and 4 to attribute | **6 to rule out a coin flip** at 95% |

**DECLARED: the design assumes MODEL A**, because it is the mechanism `§3.7a` names and the one route
(i) claims to remove. **Model B is retained as a falsification branch**, not as the basis for `n`:
if the runs are not identical, Model A is refuted and the required `n` jumps to Model B's scale,
which is a finding about cost and not a licence to keep sampling.

MEASURED at 95% confidence, `n ≥ 1 + ln(α)/ln(1−p0)`, priced at the measured per-invocation maximum
`0.5764` CPU task-h (`uthrow5d_combF`, `SPEC` §5.9 row 13, the three recorded runs being
`0.3875 / 0.4239 / 0.5764`):

    Model B, rule out p >= 0.50 :  6 runs,  3.46 CPU task-h
             rule out p >= 0.30 : 10 runs,  5.76
             rule out p >= 0.20 : 15 runs,  8.65
             rule out p >= 0.10 : 30 runs, 17.29

**That asymmetry is the argument for declaring the model up front**: six runs to exclude a coin flip
is already six times the cost of the Model-A design, and thirty to exclude `p ≥ 0.1`. **This is Gap
2's complaint about "4 repeats had no justification" made quantitative** — `4` is not justifiable
under either model, being more than Model A needs and far less than Model B needs.

### 2.2 The Model-A minimum, and why 2 runs is not it

A peer's corrected minimum was *"≥2 pinned repeats spanning different allocations."* **Two runs
detect a failure but cannot attribute it**, and attribution is required because item 2 and item 1 of
§4.4a have different consequences — item 1 failing means the chain is not deterministic at all, item
2 failing means it is deterministic *within* a shape and not *across* shapes.

    DECLARED MINIMUM, Model A:
      A1, A2   two runs on the SAME node          -> tests item 1 (same-shape determinism)
      B1       one run on a DIFFERENT node        -> tests item 2 (cross-shape determinism)
      n = 3    reservation bound 1.73 CPU task-h
      n = 4    add B2, so a single-run anomaly on B is separable   2.31 CPU task-h
    One UNPINNED run is additional and OPTIONAL -- it measures pinning's EFFECT, which is a
    different question from whether a residual survives pinning, and conflating those two is
    the defect that left this lane's other falsifier UNEVALUATED.

### 2.3 ⚠ The receipt requirement, because "different allocations" is requested and not controlled

Arm 7 runs `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G`
(`sbatch_uthrow_combine_5d_fast.sh:4`, MEASURED). **`--qos=shared` means the node is not exclusive**,
and `--constraint=cpu` selects one partition, so the scheduler may place every run on the same node
type and **may place two "different" allocations on the same physical node.**

    DECLARED, and it must be verifiable from the receipt rather than assumed:
      record per run: node name, CPU model, effective thread count, and the 5 thread-count
        variables' values AS SEEN BY THE PROCESS (not as written in the launcher).
      REQUIRE  >= 2 DISTINCT node names across the n runs. If the scheduler returns fewer,
               item 2 is NOT TESTED and the run is INCONCLUSIVE -- not a pass.
      REPORT   whether the CPU models differed. If they did not, the cross-microarchitecture
               arm is UNEVALUATED, stated as such and not folded into a pass.

**That last line is applied from this lane's own catalogued error:** a falsifier whose quantity was
never measured was reported as passing. An arm that the scheduler declines to provide is
**unevaluated**, and a design that cannot distinguish "tested and clean" from "not tested" reproduces
the defect it exists to close.

---

## 3. ⚠ A MEASURED OBSTACLE TO ROUTE (i) THAT NO DOCUMENT YET NAMES: THE PIN SET IS INCOMPLETE

§4.4a item 3 requires that *"a bound argued from 'the configuration is pinned' must enumerate **every
source of run-to-run variation it pins**."* Every pin set proposed so far — including item 3's own
five variables and a peer's three LightGBM knobs — pins **thread COUNTS only**.

**MEASURED, `grep -rn "OMP_DYNAMIC\|OMP_SCHEDULE\|OMP_PROC_BIND\|OMP_PLACES" nd-unfolding/`:
ZERO occurrences.** Not in arm 7, and **not in `sbatch_uthrow_run_5d_fast.sh:122-123` either**, which
is the arm everyone has been treating as the pinned reference and which sets
`OMP_NUM_THREADS=32 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
VECLIB_MAXIMUM_THREADS=2` — five variables, all counts.

**Thread count is necessary and not sufficient for reduction-order determinism.** With
`OMP_DYNAMIC`, `OMP_SCHEDULE`, `OMP_PROC_BIND` and `OMP_PLACES` all unset, their values are whatever
the runtime defaults to. ⚠ **I do not assert what those defaults are** — that would be an unmeasured
mechanism claim, and this campaign has a catalogued instance of publishing one. **The point is
weaker and sufficient: they are unrecorded.** A bound whose premise is "the configuration is fixed"
cannot rest on runtime defaults that appear nowhere in the tree and are not captured in any receipt.

**CONSEQUENCE for item 4, and it is why this sits in a predeclaration rather than a note:** if the
`n` runs come back **not** identical, the falsification branch of §1 fires — but with these four
variables unpinned, *"route (i) is falsified"* would be **ambiguous** between "the design cannot be
pinned" and "the design was never fully pinned." **So either they are set before the runs, or their
process-visible values are captured in the receipt of every run.** §2.3's receipt requirement is
written to cover the second option; the first is a `lane_b` code change and is not mine to make.

---

## 4. RESIDUES

1. **`ε` is untouched by all of the above** (§1.4). `1e-9` stands on §C.3's transfer argument, whose
   own falsifier is **UNEVALUATED** pending a pinned-envelope repeat on Z's bank.
2. **Whether the arm-7 runs may use Z's own bank is unresolved and is not mine.** `SPEC:3140`: *"if
   the control runs on Z's own bank, §6.4 is engaged and needs a ruling."* §1's estimator is boolean
   and so reads no value off the null, which is why I believe the prohibition is not engaged — **but
   "§6.4 needs a ruling" is a ruling, and I do not issue it.**
3. **The `1 of 11` / `1 of 10` population question is open and is a DEFINITION**: whether an archived
   harness under `docs/orchestration/runs/` belongs in a population characterising **production
   launchers**. Under the stated criterion it does. The load-bearing fact is unchanged either way —
   **arm 7 pins none.**
4. **I have not written items 1, 2, 3, 5 or 6 of §4.4a**, only the estimator and the coverage
   objective. Items 1–3 are code and belong to `lane_b`; item 6 is `S`'s side and is already recorded
   as F7-channel-only with §7 item 4 as its remainder.
5. **Nothing here is a launch request.** The prices are reservation bounds derived from three
   historical measurements, transferred, on a different bank — the same transfer caveat that applies
   to every other figure in this family.
