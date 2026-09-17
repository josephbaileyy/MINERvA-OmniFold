# Cause-3 joint-baseline acceptance packet — completing §3.7b, for approval BEFORE members

**Owner:** `owners.tsv:14`, `z-criteria-designer session [91eaa2]`. **Authorized by Joseph** 2026-09-17
as a **design deliverable**. This lane **prepares**; `owners.tsv:15` `[cb0b6b]` **evaluates**.
**Base:** `d8f5ccd5` (lane). **Bounded inventory:** the audit at `ebba67ab`, rank 2 and the cause-3 row.

**CITABLE FOR:** a completed cause-3 acceptance design and an **approval recommendation**.

**NOT CITABLE FOR:** anything adopted or graded. **No compute, no member production, no cluster
access.** `cause3_agg`, `cause3_med`, `cause3_corr` remain **WITHHELD** in `Z_BOUNDARIES` and this
packet does not fill two of them (§3). Gate 2 **FAIL**, endpoint B **DEFERRED NOT PASSED**, full `S`
**OPEN**. No value from `nd-unfolding/mii/member_k000000/` is quoted. **Successful construction of
members would supply measurements, not adoption** — the audit's rank-2 action, carried verbatim.

⚠ **I AM THIS PACKET'S AUTHOR AND CANNOT BE ITS ASSESSOR.**

### Reconciliation against the four facts that post-date my holdings

| # | fact | what it changes here |
|---|---|---|
| **1** | `θ = 7.11e-2` **declined**, and **not** relabelled an established feasibility floor | **`θ` is used NOWHERE in this packet, as an input or a fallback.** §3.2 states the consequence: `cause3_agg` and `cause3_med` are blocked on the *same* unestablished quantity, which is a **finding**, not a request to reopen `θ` |
| **2** | `[B,S]` is **PROPOSED, not governing** — `SPEC:1552` titles §3.7 *"SPECIFIED BUT NOT COMPLETED, AND ENTIRELY PROPOSED"* (verified verbatim); the amendment finding is **withdrawn**, because one does not amend a proposal | **Nothing here is written as if `B ≤ S` governs cause 3.** The criteria below are stated in their own terms and do not inherit that structure |
| **3** | `ε = 1e-9` **not adopted** on the pre-dating transfer: *"a tolerance predating production does not, by its age alone, establish that its application to Z was fixed or scientifically justified beforehand"* | ⚠ **This declines the central argument of my `d8f5ccd5` §3.1, and the objection is sound in a way my argument did not meet.** My case was age **plus different subject** — but the objection is sharper than age: **the transfer ACT is itself new.** The number was fixed for standard-P4; *applying it to Z* was not fixed before Z's production, and nothing in the number's provenance supplies that. **I accept it, do not re-litigate it, and the null leg is the peer's.** Cause 3 below takes no dependency on it |
| **4** | the bounded inventory | read at `ebba67ab`: rank 2 is *"Cause-3 joint-baseline sensitivity has no approved full acceptance packet. Stable trace/diagonals alone cannot qualify a covariance used through correlations"*, with *"a member/design proposal exists, so the gap is not 'no design'"* — hence **complete, do not restart** |

**Boundary content cited from `z_contract.py` is identical on both forked blobs** (`24379afb40d2` main,
`80325ce5c788` pilot) per the peer's diff; line numbers below are from the **main** blob.

---

## 1. (a) THE INTENDED SCIENTIFIC LOSS — three distinct losses, and that is why there are three boundaries

**The question is what conclusion joint-baseline estimator-seed sensitivity threatens, and through
which quantity.** The estimator seed selects the LightGBM/OmniFold estimator's realization; a member
re-runs *every* leg at a shifted baseline, so `C_Z^(k)` is a different covariance built from the same
data. **The loss is that a published conclusion would be an artifact of the seed rather than of the
data.** But "a conclusion" is three different things, and they are not ordered by severity:

| loss | the conclusion at risk | the quantity that carries it | which boundary |
|---|---|---|---|
| **L1** | *"the uncertainty on this bin is X"* | `diag(C_Z)` — an aggregate over the reported support | `cause3_agg` |
| **L2** | *"this bin's uncertainty is X"*, bin by bin, where a **single** bin can carry a claim | per-bin `σ_i`, plus **how many bins may fail** | `cause3_med` |
| **L3** | *"data and prediction are (in)consistent"* | the **off-diagonal / correlation** structure, through the declared projections | `cause3_corr` |

⚠ **THE STRUCTURAL FACT THAT ORGANIZES THE WHOLE PACKET, and it is `cause3_corr`'s withheld reason
verbatim:** *"Both adopted statistics are functions of the diagonal alone, so a MET result on them
licenses nothing about `C_Z`'s off-diagonal structure."* **L3 is therefore not a refinement of L1/L2 —
it is disjoint from them, and no tightening of an aggregate or per-bin diagonal criterion can ever
reach it.** That is why three boundaries exist rather than one with a stricter number, and why §4's
criterion must be **constructed to be blind to the diagonal** rather than merely *also* cover it.

**And there is a fourth loss that no boundary currently names, which I add because it is the only one
that is DISCRETE:**

| **L4** | *"the CV-centered variant is additionally mandatory"* — a **binary** published choice of centering convention | `uq_math.f7_cv_centered_required`, whose operand is `‖mean_shift‖` | **none exists** |

**L4 is the cleanest loss in the set**, because a continuous movement either flips a binary outcome or
does not. §4.3 proposes a criterion for it **that requires no tolerance at all**.

---

## 2. (b) THE AGGREGATE STATISTIC, WITH ITS POPULATION

**FORM, inherited and not reinvented:** `f_agg`-shaped — *"a trace ratio against a **named**
denominator"* (`SPEC:1435`). Over the member set `{k}`:

    f_agg^(k) = | Tr C_Z^(k) - Tr C_Z^(0) | / Tr C_Z^(0)          MET iff max_k f_agg^(k) <= cause3_agg

**POPULATION, declared explicitly because this is the field the withdrawn number never carried:** the
**reported support**, `x_cv > 0` by the predicate (`unified_throw_cov.py:370-371`), **never a
hardcoded `10,694`**; both traces taken over the *same* support, and the receipt asserts that the two
supports are identical rather than assuming it. `k = 0` is the **archive** member (§5), so the
denominator is Z's own build and the ratio is dimensionless by construction.

⚠ **This statistic is a function of the diagonal.** Stated here rather than in a caveat, because a
`MET` on it is the thing most likely to be over-read: it bounds **L1 only**.

---

## 3. (c) PER-BIN MOVEMENT **AND** THE ACCEPTABLE FRACTION — one of the two numbers is DERIVED

`cause3_med`'s withheld reason requires *"a justified per-bin tolerance **AND** a justified coverage
fraction — two numbers, and both are scientific."* They are not symmetric, and treating them as two
free parameters is what stalled this boundary.

    per bin i:   m_i^(k) = | sigma_i^(k) - sigma_i^(0) | / sigma_i^(0)
    MET iff      fraction of bins with m_i^(k) > delta_bin  is <=  (1 - phi)  for every k

### 3.1 ⚠ THE COVERAGE FRACTION `φ` IS NOT A FREE PARAMETER — IT IS FIXED BY THE DECLARED MAP SUPPORT

**Derivation.** A bin's movement can damage a published conclusion **only if some published quantity
depends on that bin.** The published quantities are the declared projections (§4). Therefore:

- **On the union of the declared maps' supports** — every bin with non-zero weight in at least one
  declared map — **`φ = 1`: no exceedance is acceptable**, because each such bin enters a published
  number directly.
- **Off that union**, no declared publication quantity depends on the bin, so `m_i` is **unconstrained**
  and the bin is excluded from the population by declaration, not by convenience.

**So `φ` collapses from a judgement into a POPULATION DECLARATION**, which is exactly the form the
prospective-declaration rule wants, and it is **derivable the moment the map set is bound** — the work
the peer is completing as P1. **I state it parametrically and it needs no number from me.**

⚠ **P1 HAS SINCE LANDED — §9 BINDS THIS, and `φ = 1` survives by a DIFFERENT route than the one
argued here.** Read §9.1 before quoting this subsection.

⚠ **The margin caveat that the deadband correction taught, applied here:** the support union must be
declared **prospectively and with its margin**, because a weight that is *nearly* zero is a membership
question, and membership decided after seeing the members is a post-hoc population choice.

### 3.2 ⚠ `δ_bin` AND `cause3_agg` ARE BLOCKED ON ONE UNESTABLISHED QUANTITY, AND IT IS THE ONE JUST CLOSED

**This is a finding, not a deferral, and it is why I propose no number for either.**

`δ_bin` asks *"how much relative movement in a reported per-bin uncertainty is scientifically
acceptable."* **That is the same question `θ` asked**, and Joseph has closed it as unestablished, with
the explicit instruction not to relabel `θ`'s value a floor. `cause3_agg` asks the aggregate form of
the same question. Their withheld reasons already say this in the same words — `cause3_med`'s *"the
printed median's precision is a new tolerance choice, not a consequence of that summary's
formatting"*, and `cause3_agg`'s *"macro formatting does not establish how much estimator-baseline
sensitivity is scientifically acceptable, and the half-display-unit rule behind it is wrong in both
directions."*

⚠ **And the two withdrawn numbers and `θ`'s withdrawn candidate come from the SAME rule.** `θ`'s
`5.00e-41` was exactly half the last displayed digit of `values.tex:115`; `cause3_agg`'s `0.0861%` and
`cause3_med`'s `0.0374%` were *"format-derived"* by the *"half-display-unit rule"* the boundary calls
**wrong in both directions**. **Three withdrawn numbers, one rule.** Proposing a fourth from any
formatting source would be the fourth instance, and **inventing a non-formatting number with no
use-based derivation would be worse**, because it would carry no audit trail at all.

**What would establish them — named, not requested:** a use-based statement of how much reported
uncertainty movement changes a conclusion. **That is the closed question, and I do not reopen it.**
**Consequence for approval: `cause3_agg` and `cause3_med` are approvable as to FORM and POPULATION
and not as to VALUE** (§7).

---

## 4. (d) A CORRELATION-SENSITIVE CRITERION FOR THE INTENDED PROJECTIONS

**Stated parametrically over a map set `{M_p}` to be bound by P1, as requested.**

### 4.1 ⚠ THE STRUCTURAL REQUIREMENT FIRST: THE STATISTIC MUST BE BLIND TO THE DIAGONAL

**A correlation criterion that can be satisfied by diagonal stability is not a correlation criterion.**
The test is exact: require the statistic to be **invariant under positive diagonal rescaling**
`C → D C D`. **The projected correlation matrix satisfies this identically** — `R_ij = C_ij /
√(C_ii C_jj)` is unchanged when `C_ij → d_i d_j C_ij`, and I measured that invariance at `3.3e-16`
in the previous round. **A trace ratio and a per-bin `σ` ratio both FAIL it**, which is precisely why
§2 and §3 cannot reach L3.

    for each declared map M_p:   R_p^(k) = corr( M_p C_Z^(k) M_p' )
    criterion:                   max_k  || R_p^(k) - R_p^(0) ||_max  <=  tau_p

`‖·‖_max` is the largest absolute entrywise difference; the diagonal of `R` is identically `1`, so it
contributes nothing and the statistic carries **off-diagonal information only.**

### 4.2 ⚠ `τ_p` MUST BE DECLARED PER MAP AND MAY NOT BE DERIVED FROM A DIAGONAL TOLERANCE

**Measured last round and it applies directly here:** a projection `w' C w` with **non-negative**
weights can still **near-cancel** when `C` is anti-correlated, so a bounded change in `C` is an
unbounded *relative* change in the projected value — `179.91` against a `0.6900` limit, `260.7×`, all
PSD. **So no per-map tolerance follows from any diagonal criterion, and `τ_p` is a genuine
per-projection declaration.** The packet supplies the form and the invariance requirement; the values
attach to maps that do not yet exist here.

⚠ **P1 HAS SINCE LANDED: there is ONE map on the intended path, so this is ONE `τ_p`, not four — §9.2.**

**What `τ_p` needs, named:** for each map, the smallest change in that projection's correlation
structure that would change the consistency conclusion the map is published to support. **That is a
per-map scientific input and it is available once the maps are bound** — unlike §3.2's blocked
quantity, this one is not the closed question, because it is about a *conclusion flip* rather than
about an acceptable uncertainty movement.

### 4.3 THE L4 CRITERION, WHICH REQUIRES NO TOLERANCE AT ALL

    criterion:  f7_cv_centered_required( C_Z^(k) )  is IDENTICAL for every k in the member set.
    MET iff     the binary outcome does not vary across the member set.  NO tolerance parameter.

**This is adoptable as written.** The quantity is discrete, so there is no tolerance to justify and
nothing to tune — the same structural argument that made `B`'s boolean estimator immune to Gap 3.
**It is the one cause-3 criterion that can be approved as to form, population AND value today**, and
it protects a published choice — the centering convention — that no existing boundary covers.

---

## 5. (e) THE VARYING LEGS, THEIR DRAW SEEDS, AND THE MEMBER SET — BOUND, AND VL141's DESCRIPTION IS SUPERSEDED

**A member is one complete seven-arm production round at one integer `MNV_EST_SEED_OFFSET = k`**,
assembled through the standard-P4 lateral stages and **both** centering variants into a complete
`C_Z^(k)` (§3.7b item 1). **MEASURED here: 8 `sbatch_*` files name the variable — 7 apply it, 1
refuses it.**

| arm | launcher | baseline |
|---|---|---|
| 1 bootstrap | `sbatch_bootstrap_5d_gpu.sh:326` | `42 + ${MNV_EST_SEED_OFFSET:-0}` **(verified)** |
| 2 seed split | `sbatch_seedscan_split_5d.sh:307` | `42 + …` |
| 3 detector | `sbatch_unfold_5d_detector_bkgaware_gpu.sh:329` | `42 + …` |
| 4 sweep | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:318` | `42 + …` |
| 5 uthrow run | `sbatch_uthrow_run_5d_fast.sh:316` | `1000 + ${MNV_EST_SEED_OFFSET:-0}` **(verified)** |
| 6 uthrow block | `sbatch_uthrow_block_5d.sh:337` | `1000 + …` |
| 7 uthrow combine | `sbatch_uthrow_combine_5d_fast.sh:134` | `1000 + …` |
| — | `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh:165` | **REFUSES** it: *"must be unset for the estimator-seed scan"* **(verified)** — mechanical confirmation that the narrow scan is a different object |

**Module-level seed arguments, re-measured in this tree:** `bootstrap_nd.py:37` `--estimator-seed`
default `42`; `seedscan_split.py:51` default `42`; `sweep_bank_5d.py:358` **default `None`, required
for `--run`**, enforced in code not argparse; `unified_throw_cov.py:634` **`required=True`**.

### 5.1 ⚠ TWO OF VL141's LOAD-BEARING CLAIMS ARE SUPERSEDED — bind the code, not the description

The assignment says bind the actual leg set rather than the historical description. **Both of VL141's
sharpest claims have since been repaired, and a packet written from VL141 would understate the
apparatus:**

| VL141 (2026-08-17, at `91fc4e9`) | measured now |
|---|---|
| *"hardcoded at `sweep_bank_5d.py:252` with **no CLI flag**"* | **SUPERSEDED.** `sweep_bank_5d.py:358` exposes `--estimator-seed`, **no default**, required for `--run` — the comment at `:344-352` names it *"ITEM 1 of the gate-1 two-role seed split"* |
| *"**Nothing stamps** the sweep seed into its products … `analyze_universes_5d.py` has **zero** occurrences of `seed`, so the agreement … **is checked by nothing**"* | **SUPERSEDED.** `sweep_bank_5d.py:309-311` writes `estimator_seed`, `est_seed_offset_declared`, `est_seed_offset`; `analyze_universes_5d.py` has **8** `seed` occurrences and at `:137-166` **refuses a member assembled from mixed estimator seeds** — *"a member assembled from mixed estimator seeds is not a member of anything"* |

**What survives of VL141, and it is the part that matters:** *"any statement of the form 'the
candidate's estimator seed' must name the leg."* **The baseline is not one value — it is a 5-tuple
with two groups, `42` (arms 1–4) and `1000` (arms 5–7)**, and the heterogeneity is **deliberate**:
`sweep_bank_5d.py:354-356` records *"42 is this module's archive value — and it deliberately DIFFERS
from `unified_throw_cov.py`'s 1000. Each module's default-equivalent preserves ITS OWN prior
behaviour."*

### 5.2 THE FAMILY IS THE DIAGONAL, NOT A GRID — and the member set carries an ALIASING constraint

**§3.7b item 1's finding, carried:** one variable moves both groups by the same integer, so the
implemented family is the **diagonal `(42+k, 1000+k)`**. A 2-D grid would be a second variable and a
launcher change — **code, not compute** — and must be decided **before** the offsets are declared.

⚠ **And the member set is not any set of integers. MEASURED by calling `seed_offset_policy`:**

    forbidden DIFFERENCES for baselines {42, 1000}:  {-958, +958}
    k = 1..8        -> []  VALID              k in {0, 958}   -> COLLISION ('group42',958,'uthrow',0,1000)
    k = 0..4        -> []  VALID              k in {1, 959}   -> COLLISION at 1001
                                              k in {0, -958}  -> COLLISION at 42

An offset preserves the grouping, **but one group's seed at `k` can collide with the other group's at
`k'`** — the constraint is **pairwise over the grid**, not a forbidden single value. **DECLARED: the
member set must be validated by `check_offset_grid` returning empty, and the declaration records the
grid, not just its size.** A contiguous small grid such as `k = 0..4` is clean; `k = 0` **is the
archive** and costs nothing extra, which fixes the denominator of §2 and §3 at no cost.

⚠ **No arm is reusable across members** (§3.7b item 1's recorded cost finding, and it corrected that
lane's own first reading): arms 1 and 2 also take `42 + OFFSET` as their *estimator* seed, so **a
member is the whole round.** There is no cheap member, and any cost estimate that reuses `C_stat` or
`C_ML` across members is wrong.

---

## 6. FALSIFIERS AND THE EVIDENCE EACH CRITERION NEEDS

| criterion | explicit falsifier | evidence it needs |
|---|---|---|
| §2 `f_agg` | a member `k` with `f_agg^(k) > cause3_agg`, **or** two members whose reported supports differ — which falsifies the shared-population assumption rather than the boundary | `Tr C_Z^(k)` and the support predicate per member; **a value for `cause3_agg`** (§3.2, blocked) |
| §3 `m_i`/`φ` | any bin **inside** the declared map-support union with `m_i^(k) > δ_bin` | per-bin `σ_i^(k)`; **the declared map support** (P1) for `φ`; **a value for `δ_bin`** (§3.2, blocked) |
| §4.1–4.2 `R_p` | a map `p` and member `k` with `‖R_p^(k) − R_p^(0)‖_max > τ_p`. ⚠ **And a second, independent falsifier of the DESIGN:** if any proposed statistic is **not** invariant under `C → D C D`, it is not correlation-sensitive and must be replaced | the declared maps (P1); `M_p C_Z^(k) M_p'` per member; **per-map `τ_p`** |
| §4.3 L4 | the F7 branch outcome **differs** between any two members | `f7_cv_centered_required(C_Z^(k))` per member — **a boolean, nothing else** |

⚠ **A falsifier that applies to the packet as a whole:** if the member set fails
`check_offset_grid`, every statistic above is computed over an aliased family and **no outcome means
what it says.** That check is arithmetic, costs nothing, and must pass **before** any member is built.

---

## 7. APPROVAL RECOMMENDATION — what to approve now, and what not to

**RECOMMENDED FOR APPROVAL NOW:**

1. **§5's leg set, member definition, diagonal-family finding and offset-grid validity requirement** —
   all measured, no free parameters, and `k = 0` identified as the archive.
2. **§2's and §3's FORM and POPULATION** — the statistics, the `x_cv > 0` predicate, the shared-support
   assertion, and **§3.1's derivation that `φ` is fixed by the declared map support** rather than chosen.
3. **§4.1's structural requirement** — that any correlation criterion be invariant under positive
   diagonal rescaling, which disqualifies trace and per-bin `σ` statistics from ever serving as one.
4. **§4.3's L4 criterion in full — form, population and value** — because the protected quantity is
   discrete and the criterion has no tolerance parameter.

**NOT RECOMMENDED FOR APPROVAL, with the reason:**

5. **Values for `cause3_agg` and `cause3_med`'s `δ_bin`.** Blocked on the quantity Joseph closed
   (§3.2). **I propose no number**, and I flag that a fourth format-derived number would be the fourth
   instance of one rule.
6. **Values for `τ_p`.** Not blocked in principle — they need the bound map set (P1) and a per-map
   conclusion-flip input, which is a different question from the closed one (§4.2).

**MEMBER PRODUCTION IS NOT REQUESTED.** Per the audit's rank-2 action and Joseph's constraint,
approval of the design precedes any request, and **members would supply measurements, not adoption.**
No threshold anywhere in this packet is derived from observed pilot agreement; §3.2 and §4.2 name what
each missing value needs instead.

## 8. RESIDUES

1. **`cause3_agg` and `cause3_med` remain WITHHELD after this packet**, by design (§3.2). Only
   `cause3_corr` gains a complete *form*, and only L4 gains a complete criterion.
2. **L4 is a loss with no boundary in `Z_BOUNDARIES`.** If §4.3 is approved, a fourth boundary key is
   implied. **Creating it is not mine** — I name the gap.
3. **The map set is unbound**; §3.1's `φ` and §4.2's `τ_p` are parametric until P1 lands.
4. **The `[B,S]` framework is proposed and is not used here** (fact 2). Nothing in this packet depends
   on the null leg, `ε`, or `θ`.
5. **I have no cluster access** and no member exists; every number here is from code, from
   `seed_offset_policy` called directly, or from the spec.


---

## 9. ⚠ P1 LANDED — THE MAPS ARE BOUND, AND THE AGGREGATION DIRECTION IS MEASURED

Relayed from `minerva-omnifold-7f`, `PACKET-20260918-scalar5d-completion-inventory-and-null-route.md`
§4 at `52e83713`; maps from `project_cov_nd.py` at `ce72abbc`. **Axis order C-order throughout;
`pt` 14, `pz` 16, `eavail` 7, `q3` 7, `W` 6 → 65,856 dense, 10,694 reported.**

### 9.1 ONE MAP CONSUMES THE COVARIANCE, AND `φ = 1` SURVIVES BY A DIFFERENT ROUTE

**M1** keeps `(eavail, W)` → a **42**-bin destination, marginalizing `pt, pz, q3`. Measured from the
manuscript source rather than a status table, `main_paper.tex:49-51`: the localization claim *"is a
central-value result; its significance awaits adoption of a common five-dimensional covariance."*
**Exactly one published claim consumes `C_Z`, and it lives on M1's 42-bin plane**; M2/M3/M4 are
marginal anchors and diagnostics, and the reported central values consume the CV rather than `C_Z`.

⚠ **§3.1's derivation of `φ = 1` HOLDS, but my stated reason was the wrong one.** I argued it from a
*union over the declared maps' supports*. The correct route is simpler: **M1 drops the three axes that
would have restricted the population**, so every reported 5D bin lands in some `(E_avail, W)` cell.
**The population is the whole reported support, minus only those cells whose destination bin is
unreported** — one declaration, not a union over four partial supports. **The conclusion is
unchanged; the argument for it is replaced.**

**And §3.1's margin caveat lands exactly where the peer says it does, which is a real requirement:**
`project_cov_nd.py` offers **two** destination masks — `--dst-cv`'s own `CV > 0`, or the dense bins
receiving ≥ 1 source cell — and **on 42 bins they can differ materially.** **DECLARED REQUIREMENT:
M1's destination mask must be named prospectively, and the orphan set (`src_cells_dropped`, dropped at
weight zero) recorded with it.** Entries are the product of the **dropped** axes' widths
(`build_projection:87-90`); kept-axis widths are not applied, so the destination is a differential
density in its kept axes — which the receipt must state, because it is the same width-weighting trap
that makes unit weights wrong.

### 9.2 `τ_p` IS ONE DECLARATION, AND ITS INPUT IS NOW NAMEABLE AND IS NOT THE CLOSED QUESTION

With M1 alone on the intended path, §4.2's per-map `τ_p` is **a single `τ` on M1's 42 × 42 projected
correlation matrix** rather than four. **MEASURED, the consumer's corner is defined in code** —
`eavailW_covariance.py:547`: `corner = ((ea_e[:-1] >= 0.4)[:, None] & (w_e[:-1] >= 1.8)[None, :])` —
and the claim there is a data-versus-generator significance. **So `τ`'s input is "how much may the
reported significance move before the written claim changes."** That is a **publication-facing
judgement about a written claim**, not a reproducibility quantity, and it is therefore **a different
question from the one Joseph closed** — which is what §4.2 asserted and can now be shown rather than
asserted.

### 9.3 ⚠ THE AGGREGATION FACTOR — CORRECT CONCLUSION, AND I MEASURED BOTH DIRECTIONS THE OTHER WAY

Each `(E_avail, W)` destination cell receives up to **14 × 16 × 7 = 1,568** dense source cells
(verified arithmetic). The peer concludes that `δ_bin` is a weak proxy for the published quantity and
that **L3 is primary and L2 cannot substitute for it** — ⚠ **that conclusion is right and the measured
numbers strengthen it, but the mechanism attached to it has both directions reversed**, so it is
corrected here before it is inherited.

**MEASURED**, `N = 200` contributors, per-bin `δ = 1e-3` with **no** exceedance (`φ = 1`),
correlations held fixed and only `σ` moved:

| source correlation | movement pattern | `w'Cw` | dest `ΔV/V` | × `δ` |
|---|---|---:|---:|---:|
| positively correlated `ρ=+0.5` | **coherent** | `2.01e+04` | `2.00e-03` | **`2.0×`** |
| positively correlated `ρ=+0.5` | cancelling | `2.01e+04` | `4.98e-09` | `0.0×` |
| uncorrelated | **coherent** | `2.00e+02` | `2.00e-03` | **`2.0×`** |
| uncorrelated | cancelling | `2.00e+02` | `1.00e-06` | `0.0×` |
| **near-cancelling source** | **cancelling** | `2.00e-01` | `1.998e-01` | **`199.8×`** |

**So:** **coherent movement is the BENIGN case at exactly `2.0×`**, and the `2×` is not aggregation at
all — it is variance being quadratic in `σ`. **Aggregation AVERAGES a coherent move; it does not
amplify it, and `1,568` does not multiply it.** The blow-up is on **cancelling movement over a
near-cancelling source** — the near-cancellation channel. ⚠ **AN EARLIER VERSION OF THIS SENTENCE PUT
THAT BLOW-UP AT `≈ N ×` AND SAID `1,568` "ACTUALLY ATTACHES" TO IT. BOTH CLAUSES ARE WITHDRAWN AS
WRONG — see the correction immediately below, which supersedes them.** `1,568` does not attach to the
severity in **either** direction; the governing quantity is the cancellation ratio.

⚠ **AND MY OWN "`≈ N ×`" IS WRONG, CORRECTED 2026-09-18 — IT ATTACHES THE COUNT TO A QUANTITY IT
DOES NOT GOVERN, WHICH IS THE SHAPE I HAD JUST CORRECTED IN SOMEONE ELSE.** A peer re-measured and
got the factor **decreasing** with `N` in their construction (`2.0e6 → 1.23e5 → 5.05e3 → 639`) while
mine rose with it, and **the disagreement across constructions is itself the proof that `N` is not
the governing variable** — we differ by `25×` at the same `N = 200`. MEASURED here, and the trap is
visible in the two halves:

    (1) depth FIXED at 0.999, vary N:   N=2 -> 2.0x    N=10 -> 10.0x   N=200 -> 199.8x   N=1568 -> 1566.4x
    (2) N FIXED at 200, vary depth:     0.9 -> 1.8x    0.99 -> 19.8x   0.999 -> 199.8x   0.999999 -> 199999.8x

**Row (1) alone is a near-perfect linear fit to `N`, and it is spurious:** at fixed cancellation
depth `w'Cw` happens to scale linearly with `N` in that parametrisation, so the factor tracks `N` by
coincidence of the parametrisation. **Row (2) breaks it — `N` is fixed and the factor moves five
orders.** Nor is the factor a function of `w'Cw` alone (`factor × w'Cw` = `0.0999`, `39.96`,
`2456.2` across cases). **The governing quantity is the CANCELLATION RATIO — the aggregate absolute
scale over the projected variance — and `N` enters only through whatever it does to `w'Cw` in a given
construction.** ⚠ **So no `N`-dependent framing belongs in this packet, and `1,568` must not be
quoted as a severity factor in either direction.** It took varying `depth` at fixed `N` to see it; the
one-directional scan confirmed the wrong law cleanly.

**The corrected statement, which is stronger than "weak in both directions":** `δ_bin` **tightly
controls** the coherent channel — a factor of exactly `(1+δ)²−1`, derivable, needing no measurement,
and **invariant in `N` and in the source correlation structure** — and is **blind** to the cancelling
channel, where it is **non-conservative by a cancellation-governed and unbounded factor**. **So L2 is
not a weak diagnostic; it is an exact one on one channel and vacuous on the other.** That is a better
argument for L3's primacy than "weak proxy", and it also means **L2 should not be discarded** — it is
the only cheap control on the coherent channel.

### 9.4 TWO PRECONDITIONS ON M1 THAT ARE NOT MINE, CARRIED

1. ⚠ **`project_cov_nd.py` records ZERO digests. VERIFIED here: `grep -cE "sha256|hashlib|digest"`
   returns `0`, against `13` in `p4_project_4d.py`.** M1 — the one map `τ` binds — would be produced by
   the **uninstrumented** projector, while OI-129 is filed against the better-instrumented one. **The
   repair must land before M1 is ever produced**, since a retrofitted digest records only that a file
   has not changed since the retrofit. **Not mine; recorded as a precondition on `τ`'s object.**
2. **The existing `(E_avail, W)` consumer reads no 5D covariance**: it marginalizes 4D lateral bands to
   `E_avail` and spreads the variance over `W` by the CV shape — `eavailW_covariance.py:445-448`,
   *"flat-in-W fractional — documented approximation"* (VERIFIED). So adoption buys the deferred claim a
   **derived** correlation structure in place of an acknowledged approximation, **which makes a loose
   `τ` harder to defend, not easier** — the peer's point, and I agree with it. ⚠ One qualification:
   the same comment says *"superseded by the W-resolved sweep mode below"*, so whether the
   approximation is still the live path is a question about that mode's use, and I do not assert it.


---

## 10. THE FINGERPRINT-FIELD DISPOSITION — issued here, because cause 3's subject IS estimator seeds

`[cb0b6b]` measured a conflict on payload and it was routed to this lane as the only one holding both
halves. **Both records verified here:**

- **`docs/ESTIMATOR_REGISTRY.md:17-22`** — *"every covariance component must carry the identical
  estimator fingerprint as its central product (**reject on mismatch**)"*, over nine fields of which
  one is **estimator seed**. Row `:29` gives `omnifold-5d-lgbm` as **"5 iter, est seed 42"** and
  **"adopted mean-centered"**, describing the **central** product.
- **`sweep_bank_5d.py:354-356`** — *"42 is this module's archive value — and it **deliberately
  DIFFERS** from `unified_throw_cov.py`'s 1000 … **unifying them on one number is the instinct a later
  reader will have** and it silently re-seeds one of the two."*

**Read literally on the estimator-seed field, the rule is violated by a difference the source calls
deliberate and warns against repairing.** §5 already establishes the baseline is a 5-tuple in two
groups — `42` for arms 1–4, `1000` for arms 5–7.

### 10.1 ⚠ THE LITERAL READING IS REFUTED BY ITS OWN CONSEQUENCE, AND NO MECHANISM IS NEEDED TO SHOW IT

**Applied literally, "reject on mismatch" rejects every throw component at every offset `k` — including
`k = 0`.** And §5 establishes that **`k = 0` IS the archive and IS Z's own build.** So the literal
reading **rejects the very product the registry exists to describe**, at no `k` can it be satisfied,
and its only available repair — unifying the seeds — is the act the source names as the trap.

**A criterion that cannot be passed by any member of its own family is unsatisfiable by construction**
— the same defect class as the `1e-12` clamp (§3.1a) and as bitwise identity on the existing products.
**This argument uses no claim about how seeds propagate, so it stands independently of the mechanism in
§10.3.**

### 10.2 DISPOSITION

1. **The rule NEEDS AMENDING on the estimator-seed field.** It is not a payload defect and not a
   reading error; the field as written is unsatisfiable for a throw component.
2. **DO NOT UNIFY THE SEEDS.** `sweep_bank_5d.py:354-356` names that as the trap and it would silently
   re-seed one of the two archives. This is a prohibition, not a preference.
3. **The amendment I recommend:** the fingerprint's purpose is to prevent a covariance being assembled
   from a **differently computed** estimator. A seed does not change the estimator; it selects a
   **realization**. So the field should be checked as **within-family identity plus a declared
   inter-family map** — every component of a family carries the identical seed, and the family
   baselines and their relationship are *declared and recorded* rather than required equal. **Half of
   this is already implemented:** `analyze_universes_5d.py:137-166` refuses a member assembled from
   mixed estimator seeds, which is exactly the within-family leg.
4. **Pending the amendment, the mismatch is a DECLARED AND RECORDED heterogeneity, not a reject.**
5. ⚠ **AND WHETHER THE `42`/`1000` SPLIT IS SCIENTIFICALLY ACCEPTABLE IS NOT SETTLED BY THE AMENDMENT
   — NOR CAN CAUSE 3 SETTLE IT.** The split is **invariant under `k`**: `42+k` and `1000+k` move
   together, so it is a property of the architecture rather than of any member, and **the diagonal
   family cannot resolve it.** Resolving it needs the two groups varied **independently**, which §5.2
   already establishes is a 2-D grid — a second environment variable and a launcher change, **code, not
   compute** — and §5.2 says that decision must be made **before** the offsets are declared.
   **So this finding converts §5.2's grid-versus-diagonal question from a design option into an open
   scientific question with a named consumer.** That is the part for Joseph.

### 10.3 ⚠ A MECHANISM I DO NOT ASSERT, AND THE ARITHMETIC THAT FAILS TO CLOSE IT

Relayed and explicitly **not established** by its author: mean-centering subtracts the ensemble mean so
a common estimator offset cancels, while CV-centering does not, the CV sitting at the other seed.
**I neither assert nor repeat it as established.** VERIFIED only that the offered arithmetic **does not
close**: with mean-centered `5.8077e-38`, CV-centered `6.2367e-38` and mean shift `1.654e-38`,
`√(5.8077² + 1.654²) = 6.0386`, which is **3.18% short** of `6.2367`. **A near-miss is not a
derivation**, and the gap is far too large to attribute to rounding. So the quadrature identity
neither establishes nor refutes the mechanism, and it is cause 2's question.

**What it would change if it were established, stated so the dependency is visible:** **L4's
discreteness argument is unaffected** — the F7 outcome is binary whatever moves it — but **L4's
STAKES change**, because the two centerings would then differ partly for a seed reason rather than a
centering-physics reason. ⚠ **Note that row `:29` records the adopted product as "adopted
mean-centered"**, which is the centering for which the offered mechanism would predict cancellation —
so if the mechanism were established it would bear on the **CV-centered variant**, i.e. on exactly
the branch L4 decides. **That is a reason to keep L4 rather than a reason to discount it.**

### 10.4 TWO ENSEMBLES — A MEMBER-SET REQUIREMENT

Relayed: the chain carries **two distinct unified-throw ensembles** — the parent's `uthrow_source` is
the 2026-08-06 `full160` file, while the pilot's throw input is the 2026-09-14 precursor — so the
parent's upstream null `5.8223488501140625e-50` is **G's**, not the precursor's
`1.4301832847122437e-50`. **DECLARED REQUIREMENT, added to §5: a cause-3 member set must not mix
ensembles, and the declaration must name WHICH unified-throw ensemble every member is built on.** A
family that silently mixed them would vary the ensemble and the seed together, and no statistic in §2–§4
could separate the two.

### 10.5 THE RECEIPT CANNOT BOUND THE CANCELLING CHANNEL — WHICH FIXES `τ`'s EVALUABILITY

Relayed and it removes a route I had left open: for positive weights and a **positive-definite** `C`
the excursion would be bounded by `((1+δ)²−1) × λ_max/λ_min`, both ends being recorded. **But the
pilot records `λ_min = −1.2750516323643892e-90` with 5,214 negative eigenvalues, so `C_Z` is NOT
positive definite and no such bound exists.** And *"passes the PSD gate"* asserts
`λ_min ≥ −rtol·λ_max`, which is **arithmetic, not definiteness**, and supplies nothing here — the
gate-proves-it-did-the-work shape.

**Consequence for §4.2, and it is favourable:** what decides the cancelling channel is the **diagonal
of `M1 C_Z M1ᵀ`** — the M1 product the deferred claim already needs. **So `τ`'s evaluability and the
claim's production requirement coincide, and no separate study is owed for it.** Combined with §9.4's
digest precondition, that gives M1 a single ordered prerequisite: **instrument the projector, then
produce M1 once, and both `τ`'s criterion and the claim become evaluable from the same object.**
