# ASSESSMENT 2026-09-17 — `θ` and the propagation argument, on Joseph's five questions

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Subjects:**
`RECOMMENDATION-20260916-theta-per-bin-uncertainty-tolerance.md` at
`480bed76f9cef73b66bc1bb0bd471847d5f61ce2` (narrowed form, 294 lines, author `owners.tsv:14`
`[91eaa2]`); and `PROPOSAL-20260916-B-and-S-bounded-determinism-control.md` **§5.7 and §5.8** at
`affc9e03119230ece17f977325d8a1ba00d68827` (author: the assembly-pilot lane). **Blob checked:** the
`PROPOSAL` is byte-identical at `affc9e03` and `a14ff88b` (`6623cf7e…`), so §5.7/§5.8 did not move
under the §12 correction.

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR:** the answers to questions 1–5, the recommended decision, and findings `T1`–`T7`.

**NOT CITABLE FOR:** adoption of `θ`, of anything. Any grade of a cell. Any replacement of the null
criterion. Any authorization or projection. **`S` IS NOT CLOSED AND NOTHING HERE CLOSES IT** — §7
item 4 remains open and this lane has still not been routed it as an object. `ε = 1e-9` stays
**PROPOSED and UNGRADED**; `B` unestablished; `A1` **OPEN**; Gate 2 **FAIL**; `cause3_corr`
**WITHHELD**; endpoint B **DEFERRED NOT PASSED**. **No compute was run and no cluster artifact was
read.**

## Evidence classes used below

- **SOURCE** — established here by reading a committed blob at a named sha.
- **DERIVED** — arithmetic or an exact-arithmetic/numerical probe run locally by this lane.
  Probe preserved at `docs/orchestration/probes/probe-20260917-theta-finite-change-and-projection.py`.
- **RELAYED** — the routing lane's cluster measurements. **Not verified by this lane.** Every
  `z-cv.npz` / `z-null.npz` / band-ROOT / `G2_g_domain` / `G3R` figure below is RELAYED.

## Recusal, checked as asked

The recusal at `068436e5` is scoped to the **products-then-claims read ordering** this lane had
supplied as an exemplar for `verify_task_ownership`. **I do not read it wider**, and it does not
touch `θ`, the propagation argument, or `B`/`S`/`ε`. One boundary I add rather than being asked for:
subject 2 is the **routing lane's own** work, and my only prior contact with §5.7 was finding at
`ed18a231` that its condition (a) had been dropped downstream — an assessment of its *use*, not a
contribution to it. I am independent of both subjects. The routing lane authored subject 2 and
therefore cannot assess this assessment of it.

---

# RECOMMENDED DECISION

**Do not adopt `θ = 7.11e-2` as a scientific ceiling on its present derivation.** The derivation is
honest, well-sourced and free of all three routes it correctly bars — and it establishes a quantity
in the **opposite role** from the one it is assigned. What §2.2 derives is a **resolution/feasibility
figure**: the smallest movement in `σ` that the existing ensembles could detect. `SPEC:1406-1409`
rules on exactly this shape: such a figure *"may bound `ε` from **below** as a feasibility
constraint; it cannot justify `ε`."* Assigned as the **upper end** of an admissible interval, it is
the direction inversion that `SPEC` §3.7a rev. 16 was corrected for, recurring one level down. `T1`
and `T2` are why, and `T2` is the part that is not a labelling quibble.

**Two things are nonetheless worth doing and neither requires adopting `θ`:** the `f_i` measurement
is needed on any route (`T4`), and the projection check is zero-compute and is the condition on the
only thing Alternative 1 would deliver (`T5`). **But closure (B) as scoped does not deliver `θ`'s own
scale** (`T4`), so *"one measurement settles both questions"* is not currently true.

**Adoption is Joseph's and I recommend, not grade.** `θ` declared as what its derivation supports —
a floor below which no per-bin `σ` gate is worth setting — needs no new argument and carries no
vacuity risk. `θ` as a ceiling needs an argument from **use**, and §2.2's is refuted at `T2`.

---

# Q1 — is the proposed `θ` scientifically justified?

## `T1` (SOURCE + DERIVED) — the arithmetic reproduces exactly, and the barred routes are correctly barred

`√(2/(N−1))`, half on `σ`, at the two launcher `N`s — **measured from the launchers at `affc9e03`,
which are frozen and pre-date Z**: `sbatch_bootstrap_5d_gpu.sh:5` is `--array=1-100%32` and
`sbatch_seedscan_split_5d.sh:5` is `--array=1-24%24`. Recomputed here: `N = 100` → `0.142134` on
variance, **`0.071067`** on `σ`; `N = 24` → `0.294884`, **`0.147442`**. Both figures reproduce to
every digit quoted, and `θ_A = 7.11e-2` is the first of them.

**§2.1's three barred routes are correctly barred**, and naming them *is* half the answer: the
formatting borrow, founding a determinism gate on `DEFERRED NOT PASSED` endpoint B, and reading the
number off `r_null`. All three are the shapes this campaign has actually committed, and §2.2's
derivation avoids all three. **That is a real achievement and the finding below does not diminish
it.**

## `T2` (SOURCE) — §2.2's claim holds per-bin and FAILS for the aggregate conclusions the tolerance exists to protect

§2.2 (`:161`): *"A CV movement that changes `σ` by less than `σ`'s own sampling error cannot change
any conclusion, because `σ` is not resolved that finely."*

**The step from "not resolved" to "cannot change any conclusion" does not hold, and this repository
already contains the refutation, on the same shape, one layer up.** `p4_lib.py:110-160` separates a
**coherent** from an **incoherent** deviation and records that *"the per-bin check is not a coherence
discriminator"*: it gives *"the fully COHERENT ceiling — if every bin moved the same way, the
integral would move by about this much"* against *"the fully INCOHERENT floor: pure round-off with
random signs"*, a factor `√N` apart, and it names reasoning about the two legs the same way as *"the
trap."*

Apply that here. `σ`'s sampling error is **random and independent across bins** — that is what
`√(2/(N−1))` measures. A CV-induced movement in `σ` is **coherent**: it is one systematic
reweighting of the V-block. An aggregate conclusion — a projected covariance, a `χ²` over the
reported support, a total — averages the random part down by roughly `√N_eff` and **does not average
the coherent part down at all.** So a movement at the single-bin resolution scale sits far **above**
the resolution of every aggregate conclusion built on those bins.

**And the declared use is aggregate.** `SPEC:1356` requires the 3D/4D covariances to be *"exact
projections"*; `AGENTS.md:14-15` makes publication completion rest on a ratified uncertainty
construction. A per-bin tolerance justified by per-bin resolution is weakest exactly where the
product is consumed — which is the same conclusion the `θ` document reaches by a different route at
its own §1.4.

**Direction, stated so this is not read as a safety claim:** `T2` makes `θ_A` **too loose** for
aggregate use, not too tight. That is the unsafe direction.

## `T3` (SOURCE) — the estimator's assumptions are violated by both populations, and those violations run the OTHER way

`√(2/(N−1))` is the relative standard error of a sample variance for **i.i.d. Gaussian** draws; the
half-step to `σ` is the first-order delta method (accurate to ~1% at these magnitudes). Neither
population satisfies the assumptions:

| block | population | how the assumption fails | direction |
|---|---|---|---|
| `C_stat`, `N = 100` | **bootstrap replicas** | replicas are resamples of **one** realized dataset, not i.i.d. draws from the estimator's sampling distribution. `N` controls only the **Monte-Carlo** component; the bootstrap variance estimator's own error does not shrink with `N` | true resolution is **coarser** → `θ` from this formula is **conservative** |
| `C_ML`, `N = 24` | **seed-scan splits** | splits of one dataset are **negatively correlated by construction**, so the effective independent count is below 24; and `2/(N−1)` is the Gaussian value, unreliable at `N = 24` under heavy-tailed seed effects | coarser again → **conservative** |

**So `T3` cuts opposite to `T2`, and `T2` is the one that governs**, because `T3` is about the size of
a resolution figure while `T2` is about whether a resolution figure may play this role at all. A
conservative estimate of the wrong quantity is still the wrong quantity.

**One consequence worth recording on its own:** because the boundary is `N`-dependent, doubling the
bootstrap ensemble would **halve** `θ`. A tolerance that moves when the ensemble size moves, with no
change in the science, is not a scientific cap. That is the reductio, and it is `SPEC:1406-1409`'s
distinction stated as a test.

## `T4` (SOURCE) — `θ_A` is NOT a total-`σ` resolution, and closure (B) cannot make it one

**§2.3 concedes the first half** (`:170`): the block figures are *"each diluted by that block's
variance fraction"*, so the total-`σ` resolution *"lies between ~0 … and 14.74%."* Joseph's Q1(c) is
therefore answered by the document itself: **`θ_A = 7.11e-2` is one block's `σ` resolution at
`N = 100`, applied to the total.** It is a total-`σ` resolution only if the sample blocks dominate
each bin's variance, which is unmeasured.

**What the document does not carry is which decomposition closes it, and this is the finding.** The
total's resolution is set by the **sample-block** variance fractions
`w_stat,i = (C_stat)_ii/(C_Z)_ii` and `w_ML,i = (C_ML)_ii/(C_Z)_ii`. The propagation argument needs
`f_i = g_i²(Σ_V C_b)_ii/(C_Z)_ii`, the **V**-fraction. **These are different terms of the same
five-way split** (`z_assembly.py:4`), and:

- §2.3 says *"the same per-bin variance decomposition `f_i`"* — defensible if *decomposition* means
  the full five-way split, which is how §5 reads it (*"the per-bin variance decomposition of `C_Z`
  into its five terms"*, `:228`);
- but `DECISION-SUPPORT` §12.5 item 1 narrows it to *"this single quantity"* and its **closure (B)
  re-reads the 13 vertical band diagonals only**. Vertical bands give `(Σ_V C_b)_ii` — hence `f_i` —
  and give **neither** `(C_stat)_ii` **nor** `(C_ML)_ii`.
- RELAYED: `z-cv.npz` holds the total, `hInflation_g` and the masks, and no per-term blocks; and the
  45-object band inventory is `40` throw-universe + `5` lateral. **So neither preserved closure
  reaches the stat/ML diagonals.**

**Therefore *"one quantity, two open questions"* (`:226-230`) is not currently true, and closure (B)
would leave `θ`'s own scale exactly where it is.** The `θ` document is careful here — `:233` says in
terms *"what I have NOT established … whether the five per-term diagonals are persisted"*, and
flags it as possibly a writer requirement rather than a measurement. **That caveat did not travel
into §12.5's closure, which is scoped to the narrowed version.**

---

# Q2 — are the propagation bounds valid for finite changes?

## `T5a` (SOURCE + DERIVED) — the matrix identity and the norm bound ARE valid for finite `Γ`; the `f_i` identity is NOT

**Valid, finite, exact, no caveat needed.** With `D' = D(I+Γ)`,
`C'_infl = (I+Γ)C_infl(I+Γ)`, so `ΔC_infl = ΓC + CΓ + ΓCΓ` **identically for all `i,j` and any finite
`Γ`**, and `‖ΔC_infl‖ ≤ ((1+γ)²−1)‖C_infl‖` for any submultiplicative norm with `‖Γ‖ ≤ γ`. I confirm
both as stated at §5.7.

**Not valid as stated.** §5.7(b)'s `dσ_i/σ_i = f_i·(dg_i/g_i)` is labelled *"exactly"* and verified at
`dg/g = 1e-6`. **It is first order only.** The exact relation follows from
`σ_i² = g_i²V_ii + (CV-independent terms)`:

    sigma'_i / sigma_i  =  sqrt( 1 + f_i * ((1+u)^2 - 1) ),        u := dg_i/g_i

whose expansion is `f_i·u + O(u²)`. **DERIVED, at `f = 0.2`:** the linear form is off by `4.0e-7` at
`u = 1e-6` — which is why the verification could not see it — and by **`2.7%` at `u = θ`**, **`11.7%`
at `u = θ/f`**. Joseph's instruction is correct on its face: the differential identity must not
silently become a finite-change bound, and at `1e-6` the check cannot distinguish them.

## `T5b` (DERIVED) — the inversion is unsafe as a GATE and conservative as a BOUND, and correcting it HELPS Alternative 1

Inverting exactly: `|u| ≤ √(1 + ((1+θ)²−1)/f_i) − 1`. Against the published `θ/f_i`:

| `f` | published `θ/f` | exact `u_max` | published / exact |
|---:|---:|---:|---:|
| `1.00` | `0.071100` | `0.071100` | `1.0000` |
| `0.50` | `0.142200` | `0.137766` | `1.0322` |
| `0.20` | `0.355500` | `0.317678` | `1.1191` |
| `0.10` | `0.711000` | `0.572435` | `1.2421` |
| `0.01` | `7.110000` | `2.965542` | `2.3975` |

**So `θ/f_i` permits MORE movement than a `θ` tolerance on `σ` actually allows.** Used as an
admissibility **gate** it would admit movements the `σ` tolerance forbids — **unsafe**. Used as the
input to a worst-case `ΔC` bound it over-states `γ` and is therefore **conservative** — which is how
Alternative 1 uses it.

**And the exact composition collapses to something simpler and tighter.** Since
`(1+u)²−1 ≤ ((1+θ)²−1)/f_i` for every bin,

    ||Delta C_infl|| / ||C_infl||  <=  ((1+theta)^2 - 1) / min_i f_i

| `min f` | published `(1+θ/f)²−1` | **exact `((1+θ)²−1)/f`** |
|---:|---:|---:|
| `1.00` | `14.7%` | `14.7%` |
| `0.50` | `30.5%` | `29.5%` |
| `0.20` | `83.7%` | `73.6%` |
| `0.10` | `192.8%` | `147.3%` |
| `0.01` | `6477.2%` | `1472.6%` |

The left column reproduces §5.8(4a)'s and §12.5's tables to every digit, confirming those are the
**linear** composition. **The `100%` crossing moves from `min f ≈ 0.1717` to `min f ≈ 0.1473`.** So
*"below `min_f ≈ 0.2` the bound exceeds 100% and settles nothing"* is pessimistic on two counts —
the crossing is at `0.17` not `0.2` even in the published form, and at `0.147` in the exact one.
**Correcting this finite-change error widens the region in which Alternative 1 settles something.**
The error is in the safe direction and fixing it is in the recommendation's favour.

## `T5c` (DERIVED) — the inversion is ONE-SIDED, and below `f ≈ 0.137` a `σ` tolerance constrains downward `g` movement not at all

A two-sided `σ` tolerance `|σ'/σ − 1| ≤ θ` bounds **downward** `g` movement only while
`f_i > 1 − (1−θ)² = 0.137145`. Below that, `g_i` may fall to **zero** while `σ_i` moves by less than
`θ` — the V-block is too small a share of that bin's variance for its total disappearance to be
visible. **DERIVED:** at `f = 0.20` the downward allowance is `|u| ≤ 0.439`; at `f = 0.1365` and
below it is **unbounded**.

This matters for two reasons and neither is the observed scale. First, `γ = max_i|u_i|` then has no
finite upper bound from `θ` alone, so the composed `ΔC` bound is not well defined on the
`f < 0.137` population without a second constraint. Second, it is the *one-directional filter* shape:
a guard stated two-sidedly that acts on one side only.

## `T5d` (SOURCE + DERIVED) — "the same factor bounds every projection" is FALSE without a further condition, and the failure is unbounded rather than gradual

§5.7 asserts *"and the same factor bounds every projection, because a projection is a linear
contraction of the same matrix"* (`:441`). §5.7(a) attaches the condition (`:459`): the bound *"is
relative to `‖P C_infl Pᵀ‖`, so it degrades if a declared projection nearly annihilates the inflated
block. The draws above used non-negative contracting weights; a near-annihilating projection is not
covered, and **the declared projection set has not been checked**."* §5.8(3) (`:515`) repeats it.

**The condition is not a degradation and non-negative weights are not enough. DERIVED, `γ = 0.30`,
limit `((1+γ)²−1) = 0.69`, all three `C` verified PSD and all three `w ≥ 0`:**

| projection | `‖PΔCPᵀ‖ / ‖PCPᵀ‖` | holds? |
|---|---:|---|
| entrywise-non-negative `C`, `w = (1,1)` | `0.0100` | **yes** |
| `C = [[1,−0.999],[−0.999,1]]`, `w = (1,1)` | **`179.9`** | **no — 260× the limit** |
| `C = [[1,−1],[−1,1]]`, `w = (1,1)` | **`∞`** | **no** |

**So the sufficient condition is not "non-negative contracting weights" but non-negative weights
AND an inflated block whose entries are non-negative on the projected directions** — equivalently, a
projection bounded away from annihilating it. The entrywise-non-negative case is exactly where the
elementwise inequality `0 ≤ y ≤ (1+γ)w` transfers to the quadratic form; with cancelling
off-diagonals it does not transfer at all.

**And this is live rather than academic in this family.** An unfolded covariance is strongly
anti-correlated between neighbouring cells, which is precisely the cancelling structure above; and
`AGENTS.md:27` records that the historical 3D block-sum object was **rank 247**, i.e. it had exact
null directions — a projection along one annihilates it exactly. **The case the bound does not cover
is the expected structure of the object, not a contrived corner.** `SPEC:1356` requires the 3D/4D
covariances to be exact projections, so the check is mandatory and it is **zero compute** once the
projections are enumerated.

## `T5e` (SOURCE + RELAYED) — the deadband population, and why it is a mis-specified `min` before it is a population choice

§5.8(1) (`:496`) states the crossing problem correctly: the threshold *"takes min over ACTIVE
bins"*, `max(·, v_blk)` is 1-Lipschitz so *"the upper bound survives"*, but *"the active/deadband
dichotomy used to select the min's index set"* does not.

**SOURCE, `z_assembly.py:6-7`:** `g^c[i] = sqrt(max(v_uni^c[i], v_blk[i]))/sqrt(v_blk[i]) ≥ 1`. In the
deadband (`v_uni ≤ v_blk`) the `max` returns `v_blk` and **`g_i = 1` exactly**, clamped — so `dg_i`
is identically zero for any CV movement that does not cross the boundary, and such a bin contributes
`u_i = 0` to `γ` **whatever its `f_i`**.

**RELAYED and it partitions exactly:** `G2_g_domain` `n_gt_one 6528`; `G3R`
`n_saturated_v_uni_below_v_blk 4166`; `6528 + 4166 = 10694` = the reported support. So **`38.96%` of
the support has `g` pinned at 1**.

**Consequence.** `min_i f_i` **over the full support** is not a conservative version of the right
statistic — it is a **different** statistic, because it lets a bin on which the perturbation provably
acts not at all set the bound. Excluding those bins is a correction to a mis-specified minimisation,
**not** a population restriction, and it is derivable from the mechanism without reference to any
bound value. `DECISION-SUPPORT` §12.5 and §5.8(4a) both take the min over the 10,694-bin support;
§5.8(1) says §5.4's own threshold takes it over active bins. **The corpus is inconsistent on this and
the mechanism settles it.**

**The crossing caveat survives and is the residual.** A bin just below the boundary can enter the
active set under the very perturbation being bounded, so *"active at the current CV"* is not a
prospectively safe index set; a compliant declaration must cover the boundary neighbourhood. **What
margin makes it safe is a design act and I do not name one.** I note only that entering bins have
`g` just above 1, hence small `u`, so the contribution is small — which is a reason to expect the
residual to be tractable, not a bound on it.

## `T6` (DERIVED) — the vacuity is a property of the BOUND's construction, and the denominator is the wrong one

Two things sit underneath §5.8(4a)'s own suspicion that *"a vacuous derived bound may therefore be an
artifact of maximising over a large population rather than evidence of a defect"* (`:540`). Both are
about the bound, not the population.

**(i) The uniform-`γ` substitution discards a structural correlation.** Replacing `Γ` by `γI`
asserts that **every** bin could simultaneously move by the **worst** bin's allowance. But the
allowance is `≈ θ/f_i` and the bins with the largest allowance are by construction the bins where the
inflated block contributes least. The uniform substitution deletes exactly the anti-correlation that
would make the bound tight, so `min_i f_i`'s extreme-order-statistic behaviour — §5.8(4a)'s measured
`9.25e-2 → 2.05e-2 → 1.11e-2` as the population grows — is inherited by the bound **by
construction**. **I name where the looseness lives and do not construct the tighter bound**; doing so
would be supplying the design I would then be asked to assess.

**(ii) The published percentages are relative to `C_infl`, and the declared use consumes `C_Z`.**
§5.7's bound and §12.5's table are `‖ΔC_infl‖/‖C_infl‖`. The declared claim is about the adopted
trunk and its projections, i.e. `‖ΔC_infl‖/‖C_Z‖` or `‖PΔC_inflPᵀ‖/‖PC_ZPᵀ‖`. Those differ by the
norm-level analogue of `f`, **and the `f`-dependence partially cancels**: the `f` that sets the
allowance is a **minimum** while the `f` that sets the contribution is **typical**, so the blow-up is
driven by the ratio of the two, not by `min f` alone. **So the `15% / 30% / 84% / 193%` figures are
not the quantity the use needs, and the vacuity threshold is denominator-dependent and has never been
stated.** I do not supply the corrected numbers: they need `f̄` as well as `min f`, and both are
unmeasured.

---

# Q3 — what does Alternative 1 establish, and which claim is being qualified?

**§12.3's principle is correct and I confirm it:** observed agreement on one execution pair is not a
bound over an execution envelope. Alternative 1 is built to need no envelope claim. **The question
Joseph asks is whether the qualification needs one, and it does — for a claim §12.7's own exclusion
list does not name.**

Naming the claims separately, because they have different requirements:

| claim | does Alternative 1 support it? |
|---|---|
| **(K1)** *these* products' recorded CV non-determinism has bounded consequence for `C_Z` | **Yes, in principle — and not as currently constructed.** `T6(ii)` (wrong denominator) and `T5b` (linear inversion) must be fixed, and the operand must be the **recorded** movement rather than `θ`: §12.7 promises *"the consequence of the recorded deviation"* while §12.5 tabulates the consequence of the **ceiling**, `12` orders away |
| **(K2)** `C_Z` is adoptable as the 5D trunk | **No**, and §12.7 says so. Gate 2 FAIL and the seven cells are untouched |
| **(K3)** the 3D/4D covariances are exact projections of the adopted trunk (`SPEC:1356`) | **No** — `T5d`. The bound's condition on the declared projection set has never been evaluated, and the failure mode is unbounded |
| **(K4)** Z has a **supported reproduction path** (`AGENTS.md:14-15`, a publication-completion requirement) | **No, and this is the one that makes the envelope claim non-optional.** An exact projection of an unreproducible trunk is reproducible only if the trunk is. **`K4` is absent from §12.7's *"what it would NOT establish"* row**, which lists *"any bound over an execution envelope; `B`; `ε`; adoption"* — it names the missing object without naming the requirement that needs it |
| **(K5)** `A1`, the fixed-seed null, as a determinism and provenance tripwire | **No.** A consequence bound and a provenance tripwire are different instruments; reject conditions `4c` and `11` continue to fire |

**So: Alternative 1 establishes sensitivity to a per-bin tolerance for these artifacts, and after the
`T5b`/`T6` corrections it could establish sensitivity to the recorded difference. It is not
sufficient for the qualification the declared use requires**, because that use is `K3` and `K4`, and
`K4` needs precisely the envelope claim Alternative 1 is designed to avoid. **That is not an argument
against running it** — `f_i` is needed on every route — but the deliverable must be stated as `K1`,
not as a qualification of the products for use.

---

# Q4 — which `B`/`S`/`ε` requirements remain, and what would replace any of them?

**All of them remain. `θ` discharges none.** Taking the `null` remaining-requirement text clause by
clause:

| clause | status after `θ` |
|---|---|
| *persist both internal same-run fixed-seed CVs and the predicate at throw creation* | **discharged for the precursor's producing revision** and unaffected by `θ`; still a writer requirement for any future build |
| *approve `B`* | **REMAINS.** Unestablished; route (i) not claimable; the estimator is declared and unassessed |
| *approve `S`* | **REMAINS.** F7-channel only, §7 item 4 open. `θ` does not touch it: `S` caps **CV movement**, `θ` caps **`σ` movement** |
| *`B ≤ S`* | **REMAINS**, and both endpoints are missing (`ed18a231` `F2`/`G4`) |
| *`ε ∈ [B, S]`* | **REMAINS.** `ε` proposed, ungraded, falsifier unevaluable |

**`θ` and `ε` are not interchangeable, in either direction, for four independent reasons:**

1. **Different operand.** `ε` bounds movement of the **central value** `x_cv`; `θ` bounds movement of
   the reported **uncertainty** `σ`.
2. **Different statistic.** `ε` is on `r_null`, the `x²`-weighted relative L2; `θ` is a per-bin
   relative maximum.
3. **Different role.** `ε` is a determinism and provenance tripwire; `θ` is a consequence cap. The
   `θ` document's own §3 says this and forbids `θ` as the gate.
4. **`θ` is structurally blind on 39% of the support.** `T5e`: **4166 of 10694** bins have `g` pinned
   at 1, so **no** CV movement in them changes `σ_i` at all. A `θ`-based gate cannot detect a CV
   movement confined to those bins, however large. **A tripwire with a measured 39% blind fraction is
   not a substitute for one without it.**

**What would be required to replace the null criterion, named exactly.** `SPEC` §6.4 fixes the
**form** of the bound (scale-relative, fixed before production), and `SPEC:1267` reject condition 11
makes *"its bound is not the scale-relative one §6.4 rules"* a **reject condition** in its own right —
distinct from `4c` (`SPEC:1257`, *"an un-derived boundary is not a criterion"*). So replacing it
requires **an amendment to §6.4 itself, plus the consequential amendment to reject condition 11**,
and by `SPEC`'s own allocation of authority that is **Joseph's act**. It is not a criteria-lane
recommendation, and it is not an adoption of `θ`. **I confirm his instruction and add the mechanism
that makes it binding: without amending §6.4, condition 11 keeps firing no matter what `θ` is set
to.**

---

# Q5 — the population and the projection set, declared from use

**The prohibition is right and it is the operative constraint.** But applying it needs two exclusions
kept apart, because they have **opposite** compliance status and `480bed76`(b) currently runs them
together.

| | basis | compliant? |
|---|---|---|
| **(E1)** omit bins whose `g_i` is clamped at 1 over the admissible CV range | **mechanism.** `z_assembly.py:6-7`'s `max(·, v_blk)`; `u_i ≡ 0` there; derivable with no reference to any bound value | **YES**, and `T5e` argues it is a correction to a mis-specified `min` rather than an exclusion at all |
| **(E2)** omit bins because their `f_i` makes the bound exceed 100% | **the bound's value** | **NO** — this is the act the instruction bars |
| **(E3)** omit bins *"whose covariance nobody uses"* | **use** — admissible in principle | **ONLY once the use is declared independently.** As stated it is a definite description, not a criterion, and it is not yet checkable |

`480bed76`(b)'s stated reason mixes (E2)'s shape (*"an extreme-order statistic set by the single
worst bin"*) with (E3)'s (*"a bin whose covariance nobody uses"*). **The distinction is what makes
the restriction compliant or barred, and the document does not yet draw it.**

**I do not declare the population.** Declaring it is a scientific act that `DECISION-SUPPORT` §12.5
assigns to Joseph, and a lane that declares it cannot then assess it — the disqualification that
governs every other object in this campaign. **What I state are the requirements a compliant
declaration must meet:**

1. **Its criterion must be statable without reference to any computed bound**, and must be checkable
   from the producer's own quantities. (E1) and (E3) can be; (E2) cannot.
2. **It must be closed under the perturbation it is used to bound** — §5.8(1)'s crossing. An index set
   defined at the current CV is not prospectively safe.
3. **It must be declared before `min_i f_i` is measured**, or the order of operations reproduces
   `SPEC` §3.6's *"a threshold chosen to make the eventual number pass is not a criterion."*
4. **If, after (E1) and a declared use, the bound is still vacuous, the response is `T6` — fix the
   bound — not a further restriction.** That route is available, costs no compute, and touches the
   prohibition not at all.

**The projection set is not a free choice and should not be treated as a declaration.** `SPEC:1356`
requires the 3D/4D covariances to be exact projections of the adopted trunk, and the publication
scope (`AGENTS.md`) fixes which they are: the 2D `(p_T, p_∥)` reproduction, the 3D `E_avail`
extension, and the 4D/5D extensions through `q3` and `W`. **So the projection set is
*enumerable*, and what is owed is a *check*, not a judgement** — each declared projection evaluated
against `T5d`'s condition. Given `AGENTS.md:27`'s rank-247 precedent in this very family, I would
expect at least one declared projection to sit near a null direction, and `T5d` shows the bound fails
there without limit rather than degrading. **That check is the single highest-value zero-compute item
in this set, and it is not in §12.5's list.**

---

# Precise unresolved premises

1. **`θ`'s role.** Its derivation supports a feasibility **floor**; it is assigned as a scientific
   **ceiling**. `T2` refutes the argument that bridges them. **Unresolved:** whether any use-derived
   argument supports a ceiling at this value. Nothing in the two subjects supplies one.
2. **`θ`'s scale.** Requires `w_stat,i` and `w_ML,i`, which **neither** preserved closure reaches
   (`T4`). Unresolved whether the five per-term diagonals are persisted at all — the `θ` document
   declines to assert it (`:233`) and I did not read the products.
3. **The finite-change inversion.** `T5b` gives the exact form; whether the exact or the linear
   composition is intended is unresolved in the corpus, and the two differ materially below
   `f ≈ 0.2`.
4. **The one-sided inversion.** `T5c`: below `f ≈ 0.137` a `σ` tolerance places no bound on downward
   `g` movement, so `γ` is not finite from `θ` alone on that population.
5. **The projection condition.** `T5d`: unchecked against the declared set, and the failure is
   unbounded.
6. **The `min`'s population.** `T5e`: the corpus is internally inconsistent (full support in §12.5
   and §5.8(4a), active bins in §5.8(1)); the crossing margin is undeclared.
7. **The denominator.** `T6(ii)`: `C_infl` versus `C_Z`, unstated, and it moves the vacuity
   threshold.
8. **Stages 3–5 of the CV trace** are not established deterministic (`θ` §8 residue 4), composing
   with the four unrecorded `OMP_*` variables. Carried, not resolved, and not mine.

## What this assessment does not do

- Adopts nothing, authorizes nothing, grades no cell, and closes neither `S` nor §7 item 4.
- Supplies no tolerance, no population, no projection list, no repeat design and no corrected bound.
  `T5b` states an exact identity that replaces a first-order one — that is a correction to an
  asserted mathematical fact, not a design choice — and `T6` names where looseness lives without
  removing it.
- Ran no compute and read no cluster artifact. Every RELAYED figure is the routing lane's and is
  labelled at each use.
- Does not revisit `B`'s declarations, the pilot, or anything outside the five questions.
