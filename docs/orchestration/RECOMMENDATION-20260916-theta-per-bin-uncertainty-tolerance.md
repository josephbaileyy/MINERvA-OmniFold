# `θ` — a tolerance on the reported per-bin uncertainty's relative movement

**Owner:** `owners.tsv:14`, `z-criteria-designer session [91eaa2]`. **Routed by Joseph** 2026-09-16 via
`minerva-omnifold-7f`, for independent assessment by `owners.tsv:15` `[cb0b6b]` and then his decision.
**Base:** `78a8c2ee` (lane). **Companion:** `PROPOSAL-20260916-B-and-S-bounded-determinism-control.md`
§5 (`a8672755`), whose arithmetic I did not re-derive and do not need to.

**CITABLE FOR:** a recommendation on `θ`, with alternatives and their consequences.

**NOT CITABLE FOR:** ⚠ **`S` IS NOT CLOSED, AND NOTHING HERE CLOSES IT** — Joseph's explicit
instruction, and §6 explains why I am structurally unable to close it even if the arguments now on the
table are sound. `θ` is **RECOMMENDED, NOT ADOPTED**. `ε = 1e-9` remains **PROPOSED and UNGRADED**, `B`
**unestablished**, Gate 2 **FAIL**, `cause3_corr` **WITHHELD**, endpoint B **DEFERRED NOT PASSED**. No
value from `nd-unfolding/mii/member_k000000/` is quoted. **No compute authorized, requested or run**
— this is arithmetic and existing-code analysis, and Perlmutter is down for maintenance regardless.

⚠ **`θ` IS NOT CHOSEN TO MAKE THE OBSERVED NULL PASS.** §3 shows the recommended value sits **twelve
orders above** it, which is a defect of a different kind and is stated rather than exploited.

⚠ **I AM THIS DOCUMENT'S AUTHOR AND CANNOT BE ITS ASSESSOR.**

---

## 1. THE DIRECT ANSWER: `θ` CANNOT BE DECLARED ALONE — **ONE TOLERANCE PLUS ONE MEASUREMENT**

**Asked whether a correlation-side tolerance must be declared jointly rather than after: YES, `θ`
alone is insufficient, and the reason is stronger than "necessary and not sufficient" — the per-bin
route's grip on the off-diagonal degrades as `1/f_i`, and `f_i` is unmeasured.**

⚠ **BUT THE FORM IS NARROWER THAN "TWO TOLERANCES", AND §1.5 IS WHERE THIS SECTION'S CONCLUSION
ACTUALLY LANDS.** A peer's §5.7 makes the correlation-side bound a **derived** consequence of `θ`
rather than a second scientific judgement, so the requirement is **one tolerance plus one
measurement** — conditional on the measured `min_i f_i`, and on a declared active set. **Read §1.5
before quoting §1.1–§1.4**, which establish the insufficiency but state the remedy in its superseded
form.

### 1.1 Why it first *looks* sufficient — and this is the trap

**A diagonal rescaling preserves correlations exactly.** For the V-block alone,

    corr(D Σ_V D)_ij = (g_i (Σ_V)_ij g_j) / (g_i√(Σ_V)_ii · g_j√(Σ_V)_jj) = corr(Σ_V)_ij

**MEASURED** over a random SPD `Σ_V` at `n = 40`, two unrelated `g` vectors:
`max |corr(D₀Σ_VD₀) − corr(D₁Σ_VD₁)| = 3.3e-16` — machine precision. So if `C_Z` *were* `D_Z Σ_V D_Z`,
`θ` on the diagonal would control the whole matrix: the off-diagonal would move only in the exact
proportion that leaves correlations fixed, and a per-bin tolerance would be genuinely sufficient.

### 1.2 Why it is not — `D_Z` multiplies `Σ_V` **only**

`z_assembly.py:4`, **MEASURED**:

    C_Z^c = D_Z^c (Σ_V C_b) D_Z^c + Σ_R C_b + Σ_A L_b + C_stat + C_ML

`g` reweights the V-block **against four terms it does not touch**, so the *total* correlation is not
invariant. Same fixture: `max |corr(C_Z(g₀)) − corr(C_Z(g₁))| = 5.9e-02`, against `3.3e-16` for the
V-block alone. **The invariance is real and it is confined to a term that is not the product.**

### 1.3 The attenuation, and it is exact

Let `f_i := g_i²(Σ_V C_b)_ii / (C_Z)_ii` — **the V-fraction of bin `i`'s variance.** Then

    dσ_i/σ_i = f_i · (dg_i/g_i)          EXACTLY

**MEASURED** against the assembled matrix at the extreme-`f` bins: ratio `0.390853` vs `f_i =
0.390853`, and `0.782530` vs `0.782530`. So a tolerance `θ` on `σ` permits

    |dg_i/g_i| <= θ / f_i        and the off-diagonal V-part moves by up to  2θ / f_i

| `f` | `|dg/g|` allowed at `θ = 1e-3` | off-diagonal V-part movement | as a multiple of `θ` |
|---:|---:|---:|---:|
| `1.00` | `1.0e-3` | `2.0e-3` | `2×` |
| `0.50` | `2.0e-3` | `4.0e-3` | `4×` |
| `0.10` | `1.0e-2` | `2.0e-2` | **`20×`** |
| `0.01` | `1.0e-1` | `2.0e-1` | **`200×`** |

**`f_i` is unmeasured.** So `θ`'s sufficiency for the off-diagonal is not merely incomplete — it is
**unbounded below in exactly the bins where the unified throw is a small fraction of the total
variance.** A per-bin number declared alone would look complete and carry no stated grip at all on the
quantity the projected claim depends on.

### 1.4 Why this is decisive for the *declared use*, not a generic caveat

`SPEC` requires the 3D/4D covariances to be **exact projections** of the adopted trunk. **A projection
contracts the full matrix**, so it samples precisely the off-diagonal entries where `θ` has least
grip. A `θ`-only declaration would therefore be weakest at the use it is being declared for.
**Hence joint, and hence `1/f_i` is the coefficient the joint declaration must name.**

### 1.5 ⚠ NARROWED 2026-09-16 — "JOINT" MEANS ONE TOLERANCE PLUS ONE MEASUREMENT, NOT TWO TOLERANCES

**A peer's §5.7 improves this section and I am adopting the improvement.** Their result is that with
`G := diag(Δg/g)`, `ΔC_infl = G C + C G + G C G` **exactly**, so

    ||ΔC_infl|| <= ((1+γ)² − 1) ||C_infl||,      γ := max_i |Δg_i/g_i|

⚠⚠ **AND THE CLAUSE "THE SAME FACTOR BOUNDS EVERY PROJECTION" IS REFUTED — RETRACTED BY ITS OWN
AUTHOR 2026-09-17 AND VERIFIED HERE INDEPENDENTLY. THIS SUBSECTION'S ADOPTION OF IT IS CORRECTED IN
PLACE RATHER THAN DELETED, BECAUSE I BUILT ON IT.** A projection is `w' C w` with **non-negative**
weights, which does not prevent near-cancellation when `C` is anti-correlated. MEASURED at `γ = 0.30`
(claimed limit `0.6900`), worst `|Δp/p|` over per-bin `Δg/g ∈ [−γ, γ]`, `w = (1,1)`:

    [[1, 0.5],    [0.5, 1]]        w'Cw = 3.0e+00   worst 0.6900     1.0x the limit   PSD
    [[1,-0.999],[-0.999, 1]]       w'Cw = 2.0e-03   worst 179.91   260.7x the limit   PSD
    [[1,-1],      [-1,  1]]        w'Cw = 0.0       DIVERGES                          PSD

**And the diagnosis is sharper than "the claim is false": the bound holds with EXACT EQUALITY for
UNIFORM `G`**, because `ΔC = ((1+γ)²−1) C` identically there — verified at `0.690000` against the
limit `0.690000` for *both* the benign and the anti-correlated matrix. **So an adversarial search that
scales `γ` uniformly passes on every input, including the counterexamples.** The argmax above sits at
maximally **non-uniform** `Δg/g = (−0.30, +0.30)`, and non-uniform is the real case, since `g` and its
room to move both vary per bin. **A projection bound therefore requires an ANTI-CORRELATION CONDITION
on `Σ_V C_b`, which is unmeasured** — it is not implied by PSD-ness, by non-negative weights, or by
any tolerance on `θ`.

**What survives of the simplification.** Composed with §1.3's `|Δg_i/g_i| ≤ θ/f_i`, `γ ≤ θ/min_i f_i`
still bounds the **matrix-norm** movement, so the *diagonal-and-norm* side of the correlation question
is a **derived** consequence of `θ` rather than a second scientific judgement: **"one tolerance plus
one measurement" holds for `‖ΔC‖`, and NOT for an arbitrary projection.** That is still a real
simplification and it is still theirs; it is simply narrower than either of us stated it.

⚠ **AND THE TABLE BELOW USED THE FIRST-ORDER COMPOSITION, WHICH IS THE WRONG DIRECTION OF WRONG.**
`dσ/σ = f(dg/g)` is first order only; the exact composition is `((1+θ)²−1)/min_f`, which is **TIGHTER**
than `(1+θ/min_f)²−1`. So the degradation below is **overstated**, and the `100%` crossing is at
`min_i f_i = 0.1473`, not at `0.1717`. MEASURED at `θ = 7.11e-2`: exact `0.2945` vs first-order
`0.3046` at `min_f = 0.5`; exact `0.7363` vs `0.8374` at `0.2`; exact `1.4726` vs `1.9275` at `0.1`.
**The qualifications in (a) and (b) stand; their numbers are the pessimistic form and the exact
crossing is `0.1473`.**

**Two qualifications, because "one tolerance plus one measurement" can be misread as "the correlation
side is settled." It is not settled until `f_i` returns, and it may not be settled then.**

**(a) The derived bound is only as good as `min_i f_i`, and it degrades fast.** At the recommended
ceiling `θ = 7.11e-2`:

| `min_i f_i` | `γ = θ/min f` | derived `||ΔC||/||C||` | |
|---:|---:|---:|---|
| `1.00` | `0.071` | `0.147` (15%) | usable |
| `0.50` | `0.142` | `0.305` (30%) | usable |
| `0.20` | `0.356` | `0.837` (84%) | weak |
| `0.10` | `0.711` | `1.93` (193%) | weak |
| `0.01` | `7.11` | `64.8` (6477%) | **vacuous** |

**Below `min_i f_i ≈ 0.2` the derived bound exceeds 100% and settles nothing.** So whether one
tolerance suffices is **conditional on the measured value**, and that conditionality has to be stated
when the simplification is quoted.

**(b) ⚠ `min_i f_i` is an EXTREME-ORDER STATISTIC over 10,694 bins, and a uniform-`γ` bound is
therefore driven by the single worst bin** — which is, by construction, a bin where the unified throw
contributes almost nothing to the variance, i.e. **a bin whose covariance nobody uses.** A vacuous
derived bound would then be an artifact of maximising over a large population rather than evidence of
a real defect. **The remedy is an active-set restriction — the same restriction the deadband analysis
already motivates, since `max(v_uni, v_blk)` absorbs the movement exactly where `v_uni ≤ v_blk` — and
NOT a tighter `θ`.** Tightening `θ` below its scientific ceiling to rescue a bound set by a dead bin
would be choosing a tolerance to obtain a verdict.

**Net: adopt the peer's "one tolerance plus one measurement", and declare with it (i) the conditional
— that sufficiency depends on the measured `min_i f_i` — and (ii) the active set over which the
maximum is taken. The second is a declaration, so the joint character of the exercise survives in a
weaker form: not two tolerances, but a tolerance and a population.**

---

## 2. `θ`'S JUSTIFICATION — MECHANISM, BOUNDARY, NUMBER, AND THREE BARRED ROUTES

Applying the standard I applied to the withdrawn `B` fallback: a stated mechanism by which uncertainty
movement damages a reported conclusion, a boundary derived for that mechanism, then a number — on a
**frozen, published scale rather than Z's own**, for the reason §3.7a rejected `sqrt(Tr C_Z)`.

### 2.1 Three routes are barred, and naming them is half the answer

| route | why it is BARRED |
|---|---|
| **display precision** of the printed uncertainty | the **formatting borrow** rejected at `SPEC:2109`/`:3909`, restated `:4088`: *"applying the printed median's precision to it is a new tolerance choice, not a consequence of that summary's formatting."* This is the route that produced `5.00e-41`, and `θ` is exactly where it would be tried again |
| **preservation of a quoted significance** | founds `θ` on **endpoint B**, which is `DEFERRED NOT PASSED`. A determinism gate must not depend on a deferred endpoint — the same argument that kept `S` off the generator rankings |
| **reading it off `r_null = 4.452e-14`** | `SPEC:1410`, *"`ε` may not be read off Z's own null"*, and §6.4 at `:3584`. That number is Z's own null |

### 2.2 The admissible route: `σ` is not *known* to better than its own ensemble sampling error

**Mechanism.** The reported `σ` is used to judge whether data and prediction are consistent. A movement
in `σ` can only damage that judgement if it is resolvable — and `C_Z` contains two **sample** covariance
blocks whose own sampling error sets the resolution.

**Boundary.** For a variance from `N` samples the relative standard error is `√(2/(N−1))`, and on `σ`
half that. **MEASURED from the launchers, which are frozen and pre-date Z:**

    C_stat   N = 100  (sbatch_bootstrap_5d_gpu.sh:5, --array=1-100%32)  : 14.21% on variance, 7.11% on sigma
    C_ML     N =  24  (sbatch_seedscan_split_5d.sh:5, --array=1-24%24)  : 29.49% on variance, 14.74% on sigma

**A CV movement that changes `σ` by less than `σ`'s own sampling error cannot change any conclusion,
because `σ` is not resolved that finely.** Frozen scale, not Z's, not a formatting borrow, not
endpoint B.

**Number.** `θ_A ≈ 7.1e-2`, the tighter of the two blocks' `σ`-level sampling errors.

### 2.3 ⚠ And `θ_A` IS BLOCKED ON THE SAME UNMEASURED QUANTITY AS §1

Those are the standard errors on the **individual blocks**, each diluted by *that block's* variance
fraction. The resolution on the **total** `σ` therefore lies between `~0` (if the sample blocks are a
negligible fraction) and `14.74%`, and where it lies depends on **the same per-bin variance
decomposition `f_i` that §1.3 needs.** So `θ`'s own scale and `θ`'s correlation-side weakness are
**gated on one measurement**, which is §5.

---

## 3. ⚠ `θ` IS NON-BINDING BY TWELVE ORDERS — SO IT IS A CEILING, NOT THE GATE

    theta_A = 7.11e-2  is  1.60e12 x the observed null (4.452e-14)  -- 12.2 orders
    the C_ML variant 1.474e-1  is  3.31e12 x          -- 12.5 orders

**This is §C.2's finding one level down, and it must be stated in the same form.** §C.2 established
that `S` sits `~1.8e11 ×` the observed null, that `ε = S` would therefore be *"a gate essentially
nothing can violate — which is exactly the `1e-12`-clamp defect §3.1a measures"*, and that **`ε` must
be argued from `B`'s side.** `θ` inherits that structure exactly: **it is `S`'s per-bin shadow, and it
is non-binding for the same reason.**

**CONSEQUENCE, and it is the recommendation's core:**

- **`θ` should be declared as a SCIENTIFIC CEILING and explicitly NOT as the operative determinism
  gate.** The operative gate remains `ε`, argued from `B`'s side.
- **`θ = 0` is barred** — the mirror of the `1e-12` clamp, a gate nothing can pass.
- **A `θ` at the scientific scale is also not a tripwire** — it cannot fire. Both failure modes are
  real and they sit at opposite ends; the resolution is not a middle value chosen by taste, it is to
  stop asking `θ` to be a tripwire at all.
- **So the `B ≤ S` structure reappears per-bin as `ε_σ ≤ θ`**, and `θ`'s role is to be the upper end of
  an admissible interval, not the gate inside it. If `θ` is recorded as the gate, the per-bin leg
  repeats the vacuity defect that `S` already demonstrated.

---

## 4. ALTERNATIVES AND THEIR CONSEQUENCES

| # | candidate `θ` | derivation status | consequence if adopted |
|---|---|---|---|
| **A** | **`7.1e-2`** — `σ`'s ensemble sampling error at `N = 100` | **ADMISSIBLE.** Frozen scale, mechanism stated, boundary derived. ⚠ Its exact value is gated on `f_i` (§2.3) | **RECOMMENDED as a CEILING.** Non-binding by `12.2` orders, so it cannot serve as the gate; must be paired with `ε` from `B`'s side |
| **B** | `1.47e-1` — the same at `N = 24` (`C_ML`) | admissible by the same argument, looser | a weaker ceiling; defensible only if `C_ML` dominates the per-bin variance, which is unmeasured |
| **C** | display precision of the printed uncertainty | **BARRED** — `SPEC:2109`/`:3909` formatting borrow | would re-commit the defect that produced `5.00e-41` |
| **D** | whatever preserves a quoted significance | **BARRED** — founds a determinism gate on `DEFERRED NOT PASSED` endpoint B | couples Z's acceptance to an endpoint Joseph has not passed |
| **E** | `θ = 0` | **BARRED** — mirror of the `1e-12` clamp | a gate nothing can pass; §C.2's argument in reverse |
| **F** | any value fitted to `4.452e-14` | **BARRED** — `SPEC:1410`, `§6.4` | threshold placed to obtain a verdict; the `PREDECLARE-20260901-cause7` §1 failure |
| **G** | **`θ` plus the `f_i` measurement plus a declared active set** — ⚠ **NARROWED 2026-09-16 from "`θ` jointly with a correlation-side tolerance"** | **THE RECOMMENDATION** (§1.5). A peer's §5.7 makes the correlation bound **derived** via `γ ≤ θ/min_i f_i`, so **no second scientific judgement is required** | the only form in which the per-bin number is sufficient for the *declared* projection use — **and its sufficiency is CONDITIONAL on the measured `min_i f_i`**: usable at `≥ 0.5`, weak by `0.2`, vacuous by `0.01` |

**RECOMMENDATION — G with A's value as the ceiling, in the narrowed form of §1.5:** declare
**`θ ≈ 7.1e-2` as a ceiling**, together with **the `f_i` measurement** (§5) and **the active
set over which `min_i f_i` is taken** — *not* a second independently declared
correlation-side tolerance, which a peer's §5.7 shows is derivable rather than judged.
**`ε`, argued from `B`'s side, remains the operative gate**; `θ` is non-binding by `12.2`
orders and must never be recorded as the gate. ⚠ **Sufficiency is CONDITIONAL on the measured
`min_i f_i` and the whole recommendation is contingent on §5** — if `min_i f_i` comes back
small, the derived correlation bound is vacuous, and the response is an **active-set
restriction**, never a `θ` tightened below its scientific ceiling to rescue it.

---

## 5. THE SMALLEST MEASUREMENT, AND IT SETTLES BOTH QUESTIONS AT ONCE

**The per-bin variance decomposition of `C_Z` into its five terms — `f_i` for every reported bin.**

It settles **(a)** how weak `θ` is on the off-diagonal (§1.3's `1/f_i`), and **(b)** `θ`'s own
scientific scale (§2.3). One quantity, two open questions, no new production.

⚠ **What I have NOT established, and will not assert:** whether the five per-term diagonals are
persisted. G's committed inventory is **13 keys** and contains `hCov_combined5d_total_uthrow` but I
have **not** verified that `Σ_V`, `Σ_R`, `Σ_A L`, `C_stat` and `C_ML` are separately recoverable. If
they are not, this is a **writer requirement** in the same family as `SPEC` §7 item 1 (persist
`x_cv`) — Tier-2 code, `lane_b` — and not a measurement at all. **That determination is a read I am
not making from here: `import ROOT` fails locally and there are zero `.root` files in this checkout.**

---

## 6. WHAT I ACCEPT FROM THE PROPOSAL, AND WHY I STILL CANNOT CLOSE `S`

**Their withdrawal, adopted, and I will not carry the old phrasing.** The claim that *"the completeness
division contributes gain exactly 1"* is withdrawn: with `r_null² = Σ w_i ρ_i² / Σ w_i` and `w_i =
x_i²`, unequal gains change the **weights**, and a uniform rescaling test cannot see it. What survives
is `min_i|ρ_i| ≤ r_null ≤ max_i|ρ_i|`, which **is my §C.3 step 1**. So the completeness channel is
**SUBSUMED by step 1, not closed.**

**Their throw-deviation result is a genuine strengthening of my §C.2** and I accept the algebra as
stated: `mat_covariance` is universe-mean centred with the CV absent, `z_assembly.py:182-215` is the
single-source coupling, so `Δv^mean = 0` and `Δv^cv = −2·ms·δ + δ²` exactly, and **F7 was the whole
channel rather than a special case** — which means my triangle-inequality bound was already bounding
all of it.

⚠ **Taken together those two results would discharge `SPEC` §7 item 4 — my own recorded residue on
`S`. I CANNOT BE THE ONE WHO SAYS SO.** `§C.2`, `§C.3` and item 4 are all mine; judging that a peer's
argument discharges my own residue is grading my own work, and it is the same disqualification that
keeps me off `ε`. **Joseph has separately ruled that `S` is not closed, and this document does not
close it.** Both arguments go to `[cb0b6b]` with my acceptance of their *algebra* recorded and my
*verdict* withheld.

---

## 7. THE QUOTIENT FORM — CONFIRMED, WITH ONE PARAMETRISATION CAVEAT

`Δ_i = V_i / (√(ms_i² + V_i) + |ms_i|)` **and not** `√(ms_i² + V_i) − |ms_i|`. **Verified
independently:** at `V/ms² = 2.0e-12` the difference form yields `1.87903e-50` against the quotient's
`1.87886e-50` and **violates its own cap**, while the quotient form holds; and once `V/ms²` underflows,
the difference form returns exactly `0.0`, which **"passes" the cap vacuously** — a pass meaning the
cap was never tested, which is the could-not-look-zero shape.

**Caveat on the reported thresholds:** I measure the violation at `V/ms² ≈ 2e-12`, scaling `V` by
`ms²`; the proposal reports failures at `θ = 1e-9, 1e-12, 1e-16` scaling by `diag(C_Z)_i`. **The exact
`θ` at which it breaks is parametrisation-dependent and therefore per-bin.** The defect is real and
confirmed; the specific `θ` values should not be quoted as if bin-independent.

---

## 8. RESIDUES

1. **`S` is OPEN** (§6) and this document does not close it.
2. **`θ`'s value is contingent on §5.** `7.1e-2` is the `N = 100` block's `σ`-level sampling error; the
   total-`σ` resolution lies in `(0, 14.74%]` pending `f_i`.
3. **The correlation-side tolerance itself is not proposed here** — only the finding that it must be
   **joint**, and the coefficient `1/f_i` it has to name. Proposing its value needs `f_i`.
4. **Stages 3–5 of the CV trace are not established deterministic** — the three `histogramdd` calls and
   the completeness division, expected single-threaded with fixed accumulation order but **unmeasured**.
   Everything in §1 assumes the histogramming is a fixed linear map of its weights. Carried forward from
   the proposal, not resolved, and it composes with the §3 finding of
   `PREDECLARATION-20260916-B-estimator-and-coverage.md` that `OMP_DYNAMIC`/`OMP_SCHEDULE`/
   `OMP_PROC_BIND`/`OMP_PLACES` are unrecorded.
5. **`ε` is untouched.** `1e-9` stands on §C.3's transfer argument, whose falsifier is **UNEVALUATED**
   pending a pinned-envelope repeat on Z's bank.
