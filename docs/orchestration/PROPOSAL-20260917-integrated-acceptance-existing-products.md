# Integrated acceptance proposal — the EXISTING products and their supported reproduction path

**Owner:** `owners.tsv:14`, `z-criteria-designer session [91eaa2]`. **Assigned by Joseph** 2026-09-17,
relayed by `minerva-omnifold-7f`. **I prepare; `owners.tsv:15` `z-independent-assessor [cb0b6b]`
evaluates** under the existing review authorization. **Base:** `480bed76` (lane).

**CITABLE FOR:** one integrated acceptance recommendation, decision-ready, against Joseph's five
requirements plus the routed `S` propagation work.

**NOT CITABLE FOR:** anything adopted. **`θ = 7.11e-2` is CLOSED AS NOT ADOPTED** on its proposed
derivation, and Joseph **declined** to relabel it an established feasibility floor — my §3's own
fallback reading and the assessor's *"declared as a FLOOR it needs no new argument"* are **both
declined**, and there is **no further `θ`-development cycle** here. **Full `S` is OPEN.** Gate 2
**FAIL**, `cause3_corr` **WITHHELD**, endpoint B **DEFERRED NOT PASSED**. No value from
`nd-unfolding/mii/member_k000000/` is quoted. **No new compute is authorized, requested or run**; the
completed precursor and pilot stay **CLOSED** and all products **preserved**.

⚠ **`78a8c2ee`'s `B` declarations STAND AS WRITTEN and are NOT recreated here.** §2 states the one
thing that follows from them for *these* products, which is a limit on their scope, not a revision.

⚠ **I AM THIS PROPOSAL'S AUTHOR AND CANNOT BE ITS ASSESSOR.** §6 is prepared, not graded — including
the part that would discharge my own residue.

⚠ **ALL PRODUCT MEASUREMENTS BELOW ARE RELAYED** from `minerva-omnifold-7f`. **I have no cluster
access**: `import ROOT` fails here and there are zero `.root` files in this checkout. Every relayed
number is marked **RELAYED** at its first use and none is re-derived.

---

## 0. WHAT I MAY NOT BUILD ON — five corrections, all verified here before use

**Four of the assessment's factual claims are corrected at `67528132` §16.2. I reproduced each rather
than accepting it, and all four hold:**

| # | the refuted claim | verified correction |
|---|---|---|
| **(a)** | *"doubling the ensemble would halve `θ`"* | **√-scaling.** `0.071067` at `N=100` → `0.050125` at `N=200` is `√(99/199) = 0.7053`, a **29.5%** reduction; halving needs **`N = 397`** (reproduced exactly). **The sharper point is theirs and it is worse for the formula:** for a *bootstrap* ensemble `N` controls only the Monte-Carlo component, so raising `N` lowers the **formula** while the resolution retains an `N`-independent floor. **The formula is severed from the quantity it names** |
| **(b)** | aggregate `√N_eff` suppression | needs per-bin `σ` **estimation** errors independent. **RELAYED as measured: `+0.815`** correlation when `N` members resample one realized dataset. The coherent/incoherent gap's **sign** survives (`p4_lib.py:141` is the repository's own statement); its **magnitude is not `√10694`** and no replacement is asserted |
| **(c)** | *"clamped bins contribute `u = 0` whatever their `f`"* | holds **at the current CV only.** `g'` uses the same `max(v_uni, v_blk)`, so a bin just below the boundary can **cross** under the perturbation being bounded. 1-Lipschitz bounds the **movement** across a crossing; it does **not** fix **membership**. So excluding clamped bins needs a **declared margin** and **is** a population choice under the prospective-declaration rule |
| **(d)** | *"unbounded downward `g` movement"* | **REFUTED BY CONSTRUCTION, verified in code:** `z_assembly.py:6` `g = √max(v_uni,v_blk)/√v_blk >= 1`; `z_contract.py:39` *"§1.3a property: `g >= 1` exactly, by construction"*; `z_contract.py:84` `G_FLOOR = 1.0`; `gate_g_domain` (`:126-132`) requires `g >= 1`, finite, and **exactly** 1 where `v_blk == 0`. So `g' >= 1` too, worst downward `u = 1/g − 1 >= −0.9434` at the RELAYED `g_max = 17.653141714565614`, and `>= 0` on clamped bins, which sit **at** the floor. **`γ` is finite from the construction alone, no tolerance required.** The `f <= 0.1371` σ-insensitivity threshold is arithmetically right; **the inference from it is not** |

**And a fifth, which is a correction to MY OWN committed §1.5 — `480bed76` is amended in this same
change rather than left standing.** The peer's §5.7 clause *"the same factor bounds every
projection"* is **retracted by its author and REFUTED here independently.** At `γ = 0.30` (claimed
limit `0.6900`), worst `|Δp/p|` over per-bin `Δg/g ∈ [−γ,γ]` with `w = (1,1)`:

    [[1, 0.5],  [0.5, 1]]      w'Cw = 3.0e+00   worst   0.6900      1.0x   PSD
    [[1,-0.999],[-0.999,1]]    w'Cw = 2.0e-03   worst 179.91      260.7x   PSD
    [[1,-1],    [-1,  1]]      w'Cw = 0.0       DIVERGES                   PSD

⚠ **The diagnosis is sharper than "false": the bound holds with EXACT EQUALITY for UNIFORM `G`**,
because `ΔC = ((1+γ)²−1)C` identically there — `0.690000` against `0.690000` for *both* the benign and
the anti-correlated matrix. **An adversarial search that scales `γ` uniformly therefore passes on
every input, including the counterexamples**, which is why 300 draws found nothing. The argmax is at
maximally **non-uniform** `Δg/g = (−0.30, +0.30)`, and non-uniform is the real case. **A projection
bound needs an ANTI-CORRELATION CONDITION on `Σ_V C_b`, unmeasured, and not implied by PSD-ness or by
non-negative weights.** Also corrected there: my table used the **first-order** composition, so it
**overstated** the degradation — the exact form `((1+θ)²−1)/min_f` is tighter and crosses `100%` at
`min_i f_i = 0.1473`, not `0.1717`.

---

## 1. REQUIREMENT 1 — THE REQUIRED PROPERTY, ITS ENVELOPE, AND WHY

**RECOMMENDED: numerical agreement within a tolerance that PRE-DATES the observation, over a
WITHIN-RUN envelope. NOT bitwise identity.** Three reasons, and the third is the one that decides it.

**(i) The contract already chose numerical agreement.** §6.4 rules the bound **scale-relative**, and
reject condition 11 (`SPEC:1267`) fires if *"its bound is not the scale-relative one §6.4 rules."*
**Bitwise identity is not a scale-relative bound — it is not a bound at all**, so a bitwise criterion
would itself violate condition 11. The open question was never *which kind*; it was *which value*.

**(ii) Bitwise identity is the gate-that-cannot-pass, here measured.** **RELAYED: 10,683 of 10,694
support bins differ bitwise** between the two persisted same-run CV executions. A criterion that fails
on every correct run in the existing envelope is the mirror image of the `1e-12`-clamp defect §3.1a
measures — the defect §6.4 exists to repair. §3.7a's stated purpose for the null is a **determinism
and provenance tripwire**; a tripwire that always fires conveys nothing.

**(iii) ⚠ THE DECIDING REASON, AND IT CONSTRAINS THE VALUE MORE THAN THE KIND.** `r_null =
4.4520002137582904e-14` is **already measured** on these products (RELAYED). §6.4 requires the value
*"not chosen from a favourable production result"*, and `SPEC:1406-1409` adds that a floor *"may bound
`ε` from below as a feasibility constraint; it cannot justify `ε`."* **Therefore no `ε` selected today
can legitimately grade these products** — the observation is already in hand, so any fresh choice is a
threshold placed to obtain a verdict (`PREDECLARE-20260901-cause7` §1). **The only admissible `ε` is
one that already existed, for another purpose, before the observation.**

**THE ENVELOPE, stated narrowly because that is what the evidence covers: WITHIN-RUN — two in-process
CV re-unfolds inside one `do_combine`.** The between-envelope property is **not** claimed (`SPEC:3140`
gap 1: *"a within-envelope null does not measure a between-envelope shift"*).

---

## 2. REQUIREMENT 2 — DOES IT QUALIFY THE EXISTING CONFIGURATION?

**ANSWER: YES for the within-run property, with no regeneration; NO for the between-envelope
property, which no available evidence establishes; and bitwise identity is refuted outright.**

### 2.1 The existing products meet an already-declared standard, with margin

`REPRO_RTOL_PER_BIN = 1e-9` — `p4_lib.py:93`, **declared by Joseph 2026-08-07** for the standard-P4
chain, and never widened (`p4_lib.py:109` records *"DO NOT WIDEN THE INTEGRAL LEG AGAIN"* for the
other leg; the per-bin leg has been `1e-9` since). Against the RELAYED observations:

    observed max|Delta/x|   1.7552716191735518e-12  (support-idx 5723 = grid-idx 31499)
    declared tolerance      1e-9
    MARGIN                  569.7x

    r_null                  4.4520002137582904e-14
    r_null vs 1e-9          2.246e4 x margin

**§C.3 step 1 is a PROVEN bound and it holds on these products:** `r_null <= max_i|ρ_i|`, i.e.
`4.452e-14 <= 1.755e-12`, a factor `39.4` — the `x²`-weighted RMS sitting far below the per-bin max, as
the proof requires.

⚠ **But the lower half of that sandwich is destroyed on these products, and it must be said:** 11 bins
agree bitwise, so **`min_i|ρ_i| = 0` identically.** `min|ρ| <= r_null <= max|ρ|` retains **only its
upper half** here. Nothing in the recommendation uses the lower half; the retracted completeness-gain
argument did.

### 2.2 Why this is a transfer that runs in the conservative direction

The transfer's stated limits are *different subject* (standard-P4 chain) and *different comparison*
(two full re-unfold products versus two in-process re-unfolds). **The comparison difference runs in our
favour, measurably:** standard-P4's figure is a **cross-envelope** one (`worst_rel_bin = 1.9e-11`,
`p4_lib.py:202`, job `56471429`, CONC 6 vs 4), and Z's within-process observation is **`10.8×`
smaller**. A tolerance that the *harder* comparison satisfies is a fortiori appropriate for the easier
one. **This licenses nothing between-envelope** — it is an argument about which direction the
transfer's slack points, not a substitute for gap 1.

### 2.3 ⚠ THE TWO QUESTIONS ARE DISJOINT, AND THIS IS WHERE BOTH PROHIBITIONS BITE

Joseph's prohibitions are (α) do not assume regeneration is necessary, and (β) do not assume a pinned
experiment qualifies the existing precursor. **They compose into a structural fact neither states
alone:**

- **`78a8c2ee`'s `B = 0`, verified by a boolean bitwise test, FAILS on these products** — 10,683 of
  10,694 bins differ. That declaration was scoped to the **pinned design** and it does not transfer.
  **This is a limit on my own declaration and I state it plainly rather than let it be inferred.**
- **A pinned experiment, if run, would qualify the PINNED configuration** — a different configuration
  from the one that produced the existing products. **It would say nothing about whether these
  products are reproducible**, because they were produced unpinned.

**So: either the existing products are accepted on a within-run numerical criterion, or they are not
accepted at all. Regeneration under pinning does not rescue them — it replaces them.** That is the
choice, and framing it as "run the pinned experiment and then decide" would be a category error.

---

## 3. REQUIREMENT 3 — `B`, `S`, `ε` AGAINST THE ACTUAL CLAIMS, AND THE PRECISE AMENDMENT

### 3.1 ⚠ THE RECOMMENDED ROUTE NEEDS **NO** CONTRACT AMENDMENT, AND THAT IS ITS STRONGEST PROPERTY

The relayed standing is that replacing the null criterion needs *"a `SPEC` §6.4 amendment PLUS the
consequential reject-condition-11 amendment (`SPEC:1267`), without which 11 keeps firing whatever `θ`
is set to."* **That is correct for a `θ`-based replacement. The recommended route does not replace the
null criterion — it SATISFIES it**, clause by clause:

| §6.4 clause | the transferred `ε = 1e-9` on `r_null` |
|---|---|
| **scale-relative** | ✓ `r_null` is a dimensionless ratio of norms of the same object over the same population |
| **fixed before production** | ✓ `2026-08-07`, before Z existed |
| **justified by controls established before implementation** | ✓ the standard-P4 measured spread, `2026-08-07/08`, before this lane existed |
| **not chosen from a favourable production result** | ✓ declared for a **different subject** — so it cannot have been chosen to make Z's null pass, and this holds independently of any date |

**Condition 11 therefore does not fire**: the key is present and its bound *is* the scale-relative one
§6.4 rules. **No §6.4 amendment and no condition-11 amendment are required on this route.** The two
amendments are needed only for the `θ` route, **which is now closed** — so the closure of `θ` removes
the amendment requirement rather than creating one.

### 3.2 `B` — unestablished, and NOT required for this route. The distinction is the SPEC's own

The `[B, S]` structure would require `B`, and **`B` is not established for the existing envelope, nor
can it be from the available evidence**: `n = 1` pair, within-envelope, and `B`'s estimator was not
predeclared for it — `SPEC:3140`'s three gaps, all live.

**But `ε` on this route is not being justified by `B`.** It is justified by a pre-dating transfer.
`SPEC:1406-1409` draws exactly this line: a floor *"may bound `ε` from below as a **feasibility
constraint**; it cannot justify `ε`."* So the observed `1.755e-12` does the **feasibility** work — it
shows an error below `ε` is attainable in this envelope on this occasion — while the **justification**
comes from the transfer. **Feasibility and justification are separate roles for separate evidence, and
the SPEC assigns them separately.** That is why the route survives `B` being unestablished, and it is
the precise reason `θ`'s closure as *"a resolution, not a scientific cap"* does not damage it.

⚠ **What is NOT claimed:** that `B <= S` is demonstrated. It is not. Per §3.7a rev. 19 that is a
statement about **evidence**, not about the world — and the recommendation does not need it, because
`ε` is not argued from inside `[B, S]`.

### 3.3 `S` and `θ` — what the closure leaves standing

`θ` is closed as not adopted, and **not** relabelled a floor; its statistical assumptions and scope
remain unestablished. **The narrow conclusion retained is that its derivation yields a RESOLUTION, not
a scientific cap.** All five clauses of the `null` remaining-requirement stand; `θ` discharges none;
and **RELAYED: `θ` is structurally blind on 4,166 of 10,694 bins**, which on its own would disqualify
it as the operative criterion regardless of value. `S` remains **F7-channel-only** with the §7 item 4
residue — §6.

---

## 4. REQUIREMENT 4 — MINIMUM EVIDENCE, AND WHAT EACH OUTCOME DECIDES

**Two checks. Both are reads. Neither is new compute.**

| | check | what each outcome decides |
|---|---|---|
| **E1** | **Independent reconstruction of `r_null`** from the persisted `x_cv`, `x_cv2` and support predicate in Z's own throw product — `SPEC` reject condition **11b** (`:1267+`) | **RECONSTRUCTS →** condition 11b is satisfied and, with §3.1, the null criterion is met on a pre-dating tolerance: **the existing products are acceptable on the within-run property.** **DOES NOT →** 11b fires, and the products cannot be accepted on this or any route until the operands are persisted (Tier-2 writer work, `lane_b`, `SPEC` §7 item 1) |
| **E2** | **The precursor's production date against `2026-08-07`**, a receipt read | **PRECURSOR LATER →** the tolerance provably pre-dates the observation, and §3.1's fourth clause holds on dates as well as on subject. **PRECURSOR EARLIER →** the subject argument still carries §3.1 alone (a tolerance declared for standard-P4 cannot have been chosen to pass Z), but the date argument is unavailable and **should not be asserted** |

**E1 is the binding one.** RELAYED evidence indicates the operands *are* persisted — the bitwise
comparison was performed on persisted vectors, and that capability is reported as having landed at
`e09513d8`, absent at `923e1323`. **Whether the specific existing products carry them is a relayed
fact I cannot verify, and it is exactly what E1 must settle.**

### 4.1 ⚠ WHAT IS **NOT** REQUIRED ON THIS ROUTE — and this corrects a claim of mine as well

**`f_i` is NOT mandatory here.** Joseph's constraint is explicit and I accept it: no diagnostic may be
described as mandatory on every route without the connection being shown. `f_i` bears on the
**projection** claim's correlation side (§5), **not** on the null criterion, which is what acceptance
of these products turns on. My own §1.5 and §5 framed it as the operative dependency for `θ`;
**with `θ` closed, that dependency closes with it.**

**And `f_i` would not close `θ`'s scale even if it were measured** — the total-`σ` resolution is set by
the **sample-block fractions** `w_stat,i` and `w_ML,i`, not by the V-fraction, and a vertical-band
re-read reaches neither. **That is the peer's correction and it also refutes my §2.3**, which said
`θ`'s scale and its correlation weakness were *"gated on one measurement."* They are gated on **two
different** ones, and `θ`'s is not `f_i`.

---

## 5. REQUIREMENT 5 — ARTIFACT PROJECTION vs UPSTREAM ESTIMATOR, DEFINITION vs NUMERICAL

**Three distinct acts, with three different access requirements. Conflating them is what made the
projection question look like a tolerance question.**

| | act | access | status |
|---|---|---|---|
| **P1** | **DEFINITION check of the projections.** The set is **enumerated**, not declared — `SPEC:1356` (*"3D/4D covariances must be exact projections from an adopted trunk"*) plus the publication scope. So for each 3D/4D covariance the publication will quote, verify its **definition** is an exact contraction of the trunk | **code read only.** No matrices, no cluster, no compute | **OWED, CHEAP, AND NOT YET DONE.** This is the one piece of the projection question that is available today |
| **P2** | **NUMERICAL check of the projections** against the anti-correlation condition of §0 | **matrix access** — and it is a *different* act, because §5.7's uniform factor is refuted, so a numerical bound now requires measuring anti-correlation in `Σ_V C_b` | **BLOCKED on access**, and its *criterion* is not yet derived |
| **P3** | **UPSTREAM ESTIMATOR reproducibility** — the fixed-seed null | as §4 | **§1–§4** |

**P1 and P3 are independent and P3 does not imply P1.** A product can satisfy the null perfectly and
still quote a 3D covariance that is not an exact contraction — that is a definition defect, invisible
to any tolerance. **Conversely P1 passing says nothing about reproducibility.** The acceptance
recommendation in §2 covers **P3 only**, and **P1 must be discharged separately before any projection
is licensed.**

---

## 6. THE ROUTED `S` WORK — PREPARED, NOT GRADED

Joseph routed the outstanding `S` propagation work into this package: the proposal's §5.8 three
unresolved conditions plus the §7-item-4 residue. ⚠ **I prepare what settles each and what each
outcome decides. I do not issue the verdict** — §C.2, §C.3 and item 4 are mine, and `[cb0b6b]`
evaluates, which is the division Joseph stated for this package.

| condition | what settles it | what each outcome decides |
|---|---|---|
| **deadband boundary crossings** | a **declared margin** around `v_uni = v_blk`, plus the population declaration §0(c) shows is required. 1-Lipschitz already bounds the movement **across** a crossing, so the movement side needs nothing further | **margin declared prospectively →** the clamped-bin exclusion becomes a legitimate population choice and the movement bound holds through crossings. **not declared →** the exclusion is a post-hoc population choice and the bound's population is undefined |
| **F7 branch changes** | the branch moves with `ms`; the `1.8e11` figure makes a change remote **at the observed scale** but is **not** a bound at a declared tolerance | **a bound at a declared tolerance →** the F7 channel closes. **otherwise →** it remains argued-at-the-observed-scale, which is not the same claim |
| **propagation to the declared projections** | **P1** above for the definitions; **P2** for the numbers. §0's refutation means the structural argument no longer carries the numerical one | **P1 passes →** the definitions are exact contractions. **P2 unavailable →** the numerical propagation claim is **not** made rather than assumed |
| **§7 item 4 residue** (throw deviations + completeness division) | the peer's two results: `Δv^mean = 0`, `Δv^cv = −2·ms·δ + δ²` exactly with F7 as the **whole** channel; and `min|ρ| <= r_null <= max|ρ|` subsuming the completeness channel into §C.3 step 1 | **if sound → item 4 is discharged and `S` extends beyond F7-only.** ⚠ **I accept the algebra and withhold the verdict**, because the residue is mine. **`[cb0b6b]` decides.** ⚠ And note §2.1: `min|ρ| = 0` identically on these products, so the subsumption rests on the **upper** bound alone |

**`S` is OPEN and this document does not close it.** What it does is put each condition next to the
thing that would settle it, so the settlement is a decision rather than another deferral.

---

## 7. THE RECOMMENDATION, IN ONE PLACE

1. **Require numerical agreement, not bitwise identity**, over a **within-run** envelope (§1).
2. **Adopt `ε = 1e-9` on `r_null` by transfer** from `p4_lib.py:93` — the only value that pre-dates
   the observation and was declared for another subject (§1(iii), §3.1). **Margin on the existing
   products: `569.7×` per-bin, `2.2e4×` on `r_null`.**
3. **Accept the existing products for the within-run property**, subject to **E1** (§4). **Do not
   claim the between-envelope property**, and **do not regenerate** to obtain it unless that property
   is separately required — a pinned run replaces these products rather than qualifying them (§2.3).
4. **No contract amendment is required on this route** (§3.1). `B` remains unestablished and is **not
   needed**, because feasibility and justification are separate roles (§3.2).
5. **Discharge P1 now** — it is a code read, it is owed, and it is independent of everything above
   (§5).
6. **`S` stays OPEN** with each condition placed against its settling evidence (§6); `θ` stays
   **closed as not adopted** and is **not** relabelled a floor (§3.3).

## 8. RESIDUES

1. **Every product number here is RELAYED** and none is re-derived; I have no cluster access. E1 and
   E2 are the two reads that would make the recommendation self-supporting.
2. **`B` for the existing envelope cannot be established from `n = 1` within-envelope evidence**
   (§3.2). Recorded as a limit, not a defect.
3. **The anti-correlation condition on `Σ_V C_b` is unmeasured** and no projection numerical bound
   exists without it (§0, §5 P2).
4. **Stages 3–5 of the CV trace are not established deterministic**, and
   `OMP_DYNAMIC`/`OMP_SCHEDULE`/`OMP_PROC_BIND`/`OMP_PLACES` are unrecorded (`78a8c2ee` §3). Both
   carried forward; neither blocks §7 item 3, which is a within-run claim about a product that already
   exists.
5. **`4,166 of 10,694` bins and the `+0.815` estimation-error correlation are RELAYED**, load-bearing
   for `θ`'s disqualification, and not independently verified here.
