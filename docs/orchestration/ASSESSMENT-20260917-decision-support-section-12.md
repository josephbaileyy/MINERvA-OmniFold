# ASSESSMENT 2026-09-17 — `§12`'s corrected recommendation, against the recorded decisions

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Subject:** `DECISION-SUPPORT-20260916-…md`
**§12 only**, at `a14ff88b` on `origin/lane/z-assembly-pilot-20260914` (pushed, verified reachable).
**§11 not assessed**, per instruction. **Prior:** `E1`–`E12` / `B1`–`B9` at `923a321c`, applied at
`fdf5e510`.

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR:** the seven dispositions and the findings `G1`–`G4`; the measurements each rests on.

**NOT CITABLE FOR:** any grade, adoption, projection or authorization. **`S` IS NOT CLOSED AND
NOTHING HERE CLOSES IT** — full `S` stays **OPEN** and §7 item 4 stays open. `θ` is **RECOMMENDED,
NOT ADOPTED**. `ε = 1e-9` stays **PROPOSED and UNGRADED**; `B` unestablished; `A1` **OPEN**; Gate 2
**FAIL**; `cause3_corr` **WITHHELD**; endpoint B **DEFERRED NOT PASSED**. No compute was run, none
is authorized, and no cluster artifact was read by this lane.

## Dispositions

| # | claim | disposition |
|---|---|---|
| 1 | `78a8c2ee` delivers §4.4a items 4 and 5, so `B`'s estimator and repeat design are **UNRESOLVED, not absent**; and `B = 0` does not give `ε` | **CONFIRM** — reading is correct, verbatim at `:72-81` |
| 2a | *"`S` is non-binding"* withdrawn as unqualified; is it over-withdrawn? | **CONFIRM the withdrawal. NOT over-withdrawn** — and one attribution corrected (`G1`) |
| 2b | the boolean/magnitude distinction survives; only its stated REASON leaned on the withdrawn premise | **PARTLY REFUTE.** The distinction survives; **the BAR does not** (`G2`) |
| 3 | `ε` is a tolerance on `r_null`, not on the per-bin diagnostic | **CONFIRM** — with one note: the sharper bracket's lower leg is **vacuous on these products** |
| 4a | applying the estimator to two in-process executions is not a voiding population substitution | **REFUTE the generalization; CONFIRM the narrow conclusion** (`G3`) |
| 4b | nothing recorded licenses transferring a pinned result to these unpinned products | **CONFIRM** — measured |
| 5 | Alternative 1, gated on `f_i` plus an active-set population declaration | **Recommendation SURVIVES; the gating pair is INCOMPLETE** (`G4`) |
| 6 | `f_i` is not computable from the preserved products; (B) is a diagnostic read | **CONFIRM both, and the decomposition is right.** One flag: (B) is unpriced by §12.6's own rule |
| 7 | enforced-cap pricing: 3.00 per attempt, 9/12/18/90, `5.20×`, all `exit 0` | **CONFIRM every number and the basis choice; CORRECT the stated reason** |

---

## 1 — `78a8c2ee`'s two declarations. CONFIRM

`78a8c2ee42c71db1e300e4cfe3735554101bf8ce` does declare both:

- **item 4** at `:28-37`: `B = 0` *"asserted as a property of the PINNED DESIGN"*, boolean bitwise
  identity over the reported support, and `IF NOT IDENTICAL: B is UNDEFINED and route (i) is
  FALSIFIED` with `B` *"explicitly NOT set to the observed difference."*
- **item 5** at `:83-153`: the sampling model declared first (Model A, deterministic given the
  allocation), the objective over **allocation shapes**, `n = 3` minimum with `n = 4` to attribute,
  Model B retained only as a falsification branch — plus a receipt requirement (`≥2` distinct node
  names or item 2 is **NOT TESTED** and the run is **INCONCLUSIVE**) which is the right guard against
  a scheduler-supplied false pass.

**So *"UNRESOLVED, not absent"* is the correct word, and §11's request was for work already done.**

**The `§1.4` reading is correct and I confirm it verbatim:** `B = 0` *"does not give `ε`"*; a gate at
`ε = 0` is *"the mirror-image of the `1e-12`-clamp defect"*; and *"`ε = 1e-9` therefore continues to
stand or fall on §C.3's transfer argument alone."* That is consistent with this lane's own finding at
`fdf5e510` and with `SPEC:1410`.

**Boundary kept:** I confirm the **reading**, not the adequacy. `78a8c2ee` is another lane's artifact
whose own header says its author cannot assess it; its assessment has not been routed to me and this
request forbids grading. Whether a boolean estimator and an allocation-shape objective *discharge*
Gap 2 and Gap 3 is that assessment, and it stays open.

## 2a — the withdrawal is correct and is not over-withdrawn. CONFIRM

**What survives is exactly the channel-scoped claim:** `S` is non-binding **through the F7 channel**,
by a bound that is proven and normalizer-free, at `1.7957e11` / `2.0433e11` × the observed null — both
of which I reproduced from the quoted operands at `fdf5e510`. **Nothing survives that makes *full* `S`
non-binding**, because the throw-deviation and completeness channels are the remainder and
`SPEC:1662` describes the second as *"an amplification channel with no `n`-dependent bound."*

This is the same conclusion this lane reached independently two days earlier as `F2`, including the
scope repair (*"not binding THROUGH THE F7 CHANNEL"*). **The withdrawal is right, and it is not an
over-withdrawal: an unqualified claim was replaced by the qualified one that the evidence supports.**

### `G1` — the ground is misattributed. It is UNASSESSED, not WITHHELD

§12.5 item 3 (`:780`) reads *"`[cb0b6b]`'s **withheld** verdict on whether §7 item 4 is discharged."*
**This lane has withheld no such verdict.** Measured:

| | |
|---|---|
| this lane's ε/`B` assessment | `fdf5e510`, **2026-09-15** |
| `fb9fdec11c653d34c5f2ee16f9f68f6be837e6d8` | **2026-09-17 08:32:04** |
| `480bed76f9cef73b66bc1bb0bd471847d5f61ce2` | **2026-09-17 08:38:51** |

**Both artifacts postdate the assessment by two days, and neither has been routed to this lane as an
object.** So no verdict was formed and none was declined. §12.2 premise 1's own wording is accurate —
*"the **owner** withholds the verdict on their own residue and routes it to `[cb0b6b]`"* — and it is
§12.5 item 3 that converts a routing into a withholding by this lane.

**Why the word matters rather than being pedantry.** *Withheld* implies an assessor examined the
residue and declined to certify it, which is weak evidence **about the residue**. *Unassessed* is the
absence of any evidence either way. That is `SPEC:1744-1751`'s own distinction — a statement about
**evidence** versus a statement about **the world** — and premise 1's conclusion is safer under the
correct label, not weaker: an unassessed residue cannot support non-bindingness any more than a
withheld one can.

**This is not a request to route it now.** The instruction is explicit that nothing here may close
full `S`, and it does not.

## 2b — the distinction survives; the BAR does not. PARTLY REFUTE

**The claim is half right.** The boolean/magnitude distinction is definitional and survives: a
boolean reads no **value** off the null, the fallback read a **magnitude**. And route (i)'s
admissibility never depended on the fallback being barred.

**But §2.4 states its own load-bearing condition in terms** (`:235-237`):

> *"The fallback is barred by a COMPOSITION, and **neither clause bars it alone**. §C.2 and §2.1
> establish that `S` is non-binding, so `ε` must be argued from `B`'s side. `SPEC:1410` states that
> `ε` may not be read off Z's own null. … **§C.2 alone bars nothing; `:1410` alone bars only the
> direct reading. It is the composition that bars it.**"

Withdraw *"`S` is non-binding"* and the composition is gone. **So the fallback's status moves from
BARRED to UNRULED — not to admissible.** Its only remaining candidate ground is the §6.4 subject
question, and that question is unruled by every lane that has touched it: `SPEC:3140` says *"if the
control runs on Z's own bank, §6.4 is engaged and **needs a ruling**"*; `SPEC:1830` says the own-bank
horn *"needs Joseph's ruling rather than this lane's reading of §6.4"*; `78a8c2ee` residue 2 says
*"'§6.4 needs a ruling' is a ruling, and I do not issue it"*; and §12.1 records the owner declining it.

**A consequence worth stating: three things now turn on that one unruled question.** The fallback's
status, route (ii)'s `GATED` status (§2.4's own row cites `SPEC:3140` for it), and route (i)'s own
control — because route (i)'s arm-7 runs would execute on Z's bank too. **They should move together,
and §12 treats them as independent.**

### `G2` — the withdrawal has not reached the sites that STATE the rule

§12.2 withdraws the **premise** and never states what happens to the **conclusions the premise
carried**. Measured in the artifact at `a14ff88b`:

| site | still reads |
|---|---|
| `:226` | *"Route (i) is the only ADMISSIBLE route, **and the fallback is barred by composition**"* — a section heading |
| `:232` | route (iii) *"**EXHAUSTED** — §C.2: `S` is **vacuous**"* — the exact claim §12.2 premise 2 withdraws |
| `:233` | the fallback: *"**BARRED**"* |
| `:551` | *"declaring `B` from those is **BARRED by composition**: `S` is non-binding"* — §10, restated |

Occurrence counts in the one file: `non-binding` **7**, `EXHAUSTED` **3**, `barred` **7** — and an
incomplete withdrawal makes the count go **up**, which is the detector for this shape.

**The mitigation that exists, and why it is not sufficient.** The top banner (`:11-14`) names §2.1,
§2.4 and §10 and says *"read §12.2 first"* — which is the right instrument and is more than most
withdrawals in this corpus carry. **But §12.2 does not answer the question the pointer sends the
reader to ask.** A reader who follows it learns the premise is withdrawn and cannot learn whether the
fallback is still barred or whether route (iii) is still exhausted. §12.2 premise 2 does fix route
(iii) (*"UNFINISHED, not exhausted"*, `:697-699`); **nothing fixes the fallback's row.** One sentence
in §12.2 closes it, and it is the sentence this section supplies the content for, not the wording.

## 3 — `ε` is on `r_null`. CONFIRM, with the bracket's lower leg flagged

Correct, and it matches this lane's own reading: `ε` is declared against `r_null` (`z_statistics.py:52`,
`null_ratio`), and the per-bin maximum is the **implication route** proven at §C.3 step 1, never the
definition. §10.3's *"the statistic `ε` is defined on"* was wrong and the correction is right.

**The owner's sharper form `min_i|ρ_i| ≤ r_null ≤ max_i|ρ_i|` is correct** — `r_null` is the
`x_i²`-weighted RMS of `ρ`, so it lies between the min and max; I verified both legs.

**⚠ But on these products the lower leg is exactly vacuous.** §12.4 records that **11** support bins
agree **bitwise**, so `min_i|ρ_i| = 0` identically and the lower bound reduces to `0 ≤ r_null`. The
bracket is presented as an improvement on the one-sided bound and **half of it is inoperative on the
object at hand.** Recorded because a two-sided form invites the reading that both sides constrain.

## 4a — REFUTE the generalization, CONFIRM the narrow conclusion

**What I confirm.** The measurement is internally consistent and I re-derived what is re-derivable
without cluster access: the reported relative L2 `4.452000213758293e-14` agrees with the build's
`4.4520002137582904e-14` to a relative `6.66e-16` — about 3 ULP, consistent with a different
summation order, so *"15 significant figures"* is right. `max|d/x| = 1.7552716191735518e-12` is
`39.43 ×` `r_null`, consistent with the `x²` weighting, and satisfies the bracket. The
support-index-5723-vs-grid-index-31499 pair is the receipt's own two bases and is not a
disagreement. **The npz contents themselves I did not read — no cluster artifact was touched here —
so those figures are RELAYED, and the arithmetic on them is mine.**

**And I confirm the operative conclusion: route (i) cannot qualify the existing products.** That
holds via 4b — no transfer argument — and it does not need the generalization below.

### `G3` — the substitution runs in TWO directions and only one was priced

The estimator's declared population is `78a8c2ee` §1's *"the arm-7 runs of **§2**"* — i.e. `n`
**pinned** arm-7 runs across allocation shapes. It was applied to `x_cv` / `x_cv2` from **one
unpinned** run. That changes **two** axes:

| axis | direction of the substitution |
|---|---|
| **separate runs → in-process repeats** | the peer's axis. One process, one allocation, one seed — **stronger** on allocation control |
| **pinned → unpinned** | **not priced, and it runs the other way.** These products pinned **nothing** |

**The parenthetical that carries the inference is wrong: allocation shape is NOT the only thing route
(i) pins.** Route (i) pins **estimator parameters**. `z_reproducibility.Z_REPRO_KNOBS`
(`:127-138`, measured) declares `deterministic=True`, `force_row_wise=True`, `num_threads=1`, and
`num_threads`'s own justification reads: *"**the estimator parameter, NOT `OMP_NUM_THREADS`**, which
this repository has measured LightGBM to ignore. Thread count sets reduction order, so an unpinned
count makes the CV a property of the allocation."* Allocation shape is what item 5's **coverage
objective varies**; it is not the pin set.

**So the observed non-identity IS attributable to variables route (i) would pin** — all three knobs
were free in these executions. The a-fortiori step (*"Model A predicts they agree trivially. They do
not."*) requires the pair to have been pinned. It was not, so the step does not license *"the
non-identity is not attributable to allocation shape, which is the only thing route (i) pins."*

**And *"route (i) is FALSIFIED"* is the estimator's consequent applied outside its antecedent.**
Route (i)'s claim is that **pinning** delivers `B = 0`. It never claimed the unpinned configuration
is bitwise identical. Finding non-identity in an unpinned pair **confirms route (i)'s motivating
premise** rather than falsifying route (i). The defensible sentence is: *the predeclared estimator,
applied to operands outside its declared population, returns NOT IDENTICAL, so it cannot yield `B`
for these products.*

**A secondary leg, offered as an unmeasured gap and NOT as a cause.** *"Same-process is strictly
stronger than same-node"* is not established even on the allocation axis. `78a8c2ee` §3 measured
`OMP_DYNAMIC / OMP_SCHEDULE / OMP_PROC_BIND / OMP_PLACES` at **ZERO occurrences** in
`nd-unfolding/`; with `OMP_DYNAMIC` unset, per-region thread counts may differ **between calls inside
one process**, so a same-process pair does not dominate a same-node pair by construction. **I assert
no cause** — only that the domination claim is unmeasured, which is the subject's own standard.

**What `G3` does NOT do.** It does not rescue route (i), which remains blocked by the incomplete pin
set, the unruled §6.4 question and the missing transfer argument. **It does not disturb the
recommendation:** §12.4's grounds (b), (c) and (d) are independent of the a-fortiori, and ground (a)'s
operative half — *"cannot qualify them"* — holds via 4b.

## 4b — no transfer argument exists. CONFIRM

Measured across `docs/orchestration/*.md` and `nd-unfolding/*.md`: every occurrence of *"transfer
argument"* either (i) says one is **needed** and unchosen (`SPEC:1830`, Gap 2's transfer horn), or
(ii) refers to §C.3's standard-P4 → Z argument for `ε`, **whose own falsifier is UNEVALUATED**. **None
licenses pinned → unpinned**, and the two directions are not the same argument. This is the same
finding this lane recorded as `E11` at `923a321c` before any of these products existed.

## 5 — the recommendation survives; the gating pair is incomplete

**Alternative 1 is the right recommendation on the surviving grounds**, and §12.3's distinction
(*"observed agreement is not an established bound over an execution envelope"*) is correct and is the
right thing to state before the answer.

### `G4` — two decisions upstream of Alternative 1 are absent from §12.5

**(i) `θ` is RECOMMENDED, NOT ADOPTED — and its own document forbids the use §12 makes of it.**
`RECOMMENDATION-20260916-theta-…md` at `480bed76`: `:12` *"`θ` is **RECOMMENDED, NOT ADOPTED**"*, and
`:4` records that Joseph routed it *"for independent assessment by `owners.tsv:15` `[cb0b6b]` **and
then his decision**"* — **so my assessment is a precondition Joseph himself set, and it has not
happened.** It is not among §12.5's three items, yet Alternative 1's entire output is expressed in
`θ`: §12.5 item 1 tabulates the derived bound *"at `θ = 7.11e-2`"* and §12.7 prices Alternative 1's
deliverable in the same factor.

**And `:177-200` says in terms what that value may not be used as:** `θ_A = 7.11e-2` is
*"`1.60e12 ×` the observed null … 12.2 orders"*; it *"should be declared as a SCIENTIFIC CEILING and
explicitly **NOT** as the operative determinism gate"*; it is *"`S`'s per-bin shadow, and it is
non-binding for the same reason"*; and — **the sentence that decides this** — *"if `θ` is recorded as
the gate, the per-bin leg **repeats the vacuity defect that `S` already demonstrated**."* §12 applied
exactly that scope repair to `S` one level up and **did not carry it down to `θ`.** So the
`f_i` table's `min_f → 15% / 30% / 84% / 193%` figures are the worst-case consequence of a
**ceiling**, and §12.7's *"a bound on the consequence of **the recorded deviation**"* names a
different operand — the recorded deviation is `12` orders below `θ_A`.

**(ii) §5.7's condition (a) is dropped at every site that uses the result.**
`PROPOSAL-20260916-…md:441` states *"and the same factor bounds every projection"*, and `:459` states
the condition on it: *"The projected bound is relative to `‖P C_infl Pᵀ‖`, so it degrades if a
declared projection nearly annihilates the inflated block. The draws above used non-negative
contracting weights; a near-annihilating projection is not covered, and **the declared projection set
has not been checked.**"* **That condition appears in neither the `θ` document's §1.5, nor §12.4
consequence 4, nor §12.7's Alternative-1 cell** — all three say *"every projection"* unqualified.

**It is material, not decorative, and the `θ` document's own §1.4 says why:** `SPEC` requires the
3D/4D covariances to be **exact projections**, *"a projection contracts the full matrix, so it samples
precisely the off-diagonal entries where `θ` has least grip."* **So the one use the bound exists for
is the one whose condition has never been checked.** Checking the declared projection set against
§5.7(a) is **zero compute** and belongs in §12.5 as a fourth item.

### Is `(route choice, active-set population)` the right pair?

**Necessary, not sufficient.** Under Alternative 1 the pair is incomplete by `G4`: `θ`'s decision —
with the assessment Joseph made its precondition — and the §5.7(a) projection-set check both sit
upstream of the population declaration, which only begins to matter once `min_i f_i` is in hand **and**
a `θ` is adopted. **Under Alternative 1, `θ` is the actually-blocking decision, not the active set.**
Under Alternative 2 the blocking decision is the **§6.4 subject ruling**, which §12.7's Alternative-2
cell does correctly list, and which `G2` shows now also governs the fallback and route (ii).

## 6 — `f_i` is right, and (B) is a diagnostic read. CONFIRM, with one flag

**The decomposition is correct.** With `z_assembly.py:4`'s
`C_Z^c = D_Z(Σ_V C_b)D_Z + Σ_R C_b + Σ_A L_b + C_stat + C_ML` and `D_Z = diag(g)`, that term's
diagonal is `g_i²(Σ_V C_b)_ii`, so `f_i := g_i²(Σ_V C_b)_ii / (C_Z)_ii` **is** the V-fraction of bin
`i`'s variance, and `dσ_i/σ_i = f_i·(dg_i/g_i)` follows. **One qualification the sources already
carry:** that identity is first-order in `dg/g`; the exact statement is §5.7's
`ΔC_infl = ΓC + CΓ + ΓCΓ`, which absorbs the second order. Nothing turns on it at these magnitudes.

**"Not computable from the preserved products" is sound** given `z-cv.npz`'s seven arrays: `(C_Z)_ii`
and `g_i` are present and the vertical-band block-sum diagonal is not, so the numerator is missing.
**Closure (B) is a diagnostic read by its output** — it produces no covariance object, so it is not in
`SPEC` §5.8b's production block — and (A) as a standing writer requirement is worth doing regardless.

**⚠ FLAG: (B) is unpriced by §12.6's own rule.** §12.6 establishes that a request is priced at its
**enforced cap** rather than at historical elapsed, and then §12.7 prices Alternative 1 as *"one short
diagnostic attempt"* with no cap figure at all. If (B) runs under a launcher carrying a `--time`
directive, its declared maximum is that directive, not *"short"*. **The rule should reach the route
the document recommends**, which is the same shape as `G2`.

**Not verified by this lane:** the support ROOT's digest `9f7b2f55…`, its `41.44` GB size, and the
`~11.8` GB read estimate. Those are cluster facts, I read no cluster artifact, and they are RELAYED.

## 7 — CONFIRM every number and the basis; CORRECT the stated reason

**Measured here, and one check is sharper than the claim.** §12.6 says the directive line is
*"identical on `origin/main` and on this lane"*. **Line 4 IS byte-identical** across
`origin/main` and `a14ff88b` — I compared the line, not the file. ⚠ **The files are NOT identical**:
they differ by the Z-scoped requeue-refusal block, so the claim is true as scoped to `:4` and a reader
must not generalize it to the file.

| quantity | §12.6 | re-measured here |
|---|---|---|
| arm-7 enforced cap | `--time=03:00:00` | `:4` confirmed; `--ntasks=1`, so `3.00` task-h |
| Model A `n=3` / `n=4` | `9.00` / `12.00` | `9.00` / `12.00` |
| Model B `n=6` / `n=30` | `18.00` / `90.00` | `18.00` / `90.00` |
| predeclaration's figures | `1.73/2.31/3.46/17.29` | `n × 0.5764` exactly |
| ratio | `5.20×` | `5.205` |
| CPU headroom | `403.803889` | `403.8038888888889` from the committed receipt |
| `9.00` as a share | `2.23%` | `2.229%` |
| `r5_meter check --max-age-hours 24` | exit 0 | **exit 0**, run locally against the committed receipt |

**CORRECTION — the reason, not the number.** §12.6 (`:802-804`) writes *"R5 **meters wall-hours per
execution attempt**, **so** the declared maximum for one attempt is 3.00 CPU task-hours."* The
inference does not follow, because the meter does not charge reservations. `r5_meter.py:73`:
*"task-hours: sum of post-t0 **`ElapsedRaw`** over every execution attempt"* — **actual elapsed.**
Confirmed arithmetically: the historical `1,395` s attempt is `1395/3600 = 0.3875` task-h exactly. So
R5 would **charge** about `0.39`–`0.58` per attempt, not `3.00`.

**The right ground for `3.00` is the reservation rule, and it is stated directly in the governing
document:** `SPEC:3140` — *"**Reservation bound `3n` CPU task-h**"* — with §5.2's standing rule that
*"a request bounds an attempt, not a completion."* **Same numbers, correct authority.**

**And one population point that follows.** `9.00` is a **reservation**; `403.80` is a headroom
computed from **actual `ElapsedRaw`**. Comparing them is conservative and therefore safe for an
admission check, but they are different quantities and must be named as such in the same sentence.
Likewise *"`5.20×` the predeclaration's"* is **reservation versus expected actual** — not two
estimates of one quantity, so the predeclaration's figures were not superseded on their own axis;
they were replaced by a different axis, which is what the relayed ruling asked for. **§12.6's
conclusion — *"R5 is not what makes route (i) expensive"* — survives, and is stronger on the charge
basis than on the reservation basis.**

## Context checked, and one completeness note on it

The pilot outcome as relayed reproduces from `ND_OMNIFOLD_RUN_LOG.md` at `1b2873a8`: job `58454524`,
`ExitCode 2:0`, `ElapsedRaw 1037 s`, `nid004093`, producer `e09513d8` / assembling `fb9ec356`
distinct, `construction_status` **CHECKED**, `scientific_acceptance` **NON-PASSING**, `adoptable`
**false**, `input_kind` **real**.

⚠ **Two reject lists exist and the summary carries the shorter one.** At `:279-281` the run log
records `null.assessment` `verdict` **NOT ASSESSABLE** with `reject_conditions ["4c", "11"]`, while
*"the receipt's `outcome`"* records `["4c"]`. `SPEC:1267` condition **11** is *"The fixed-seed null key
is absent, **or its bound is not the scale-relative one §6.4 rules**"* — which is the condition that
names the **missing `ε`** directly. Quoting `4c` alone is accurate to the receipt and understates the
assessment's own record. Not a §12 defect; recorded so the shorter list does not become the one that
travels.

---

## What this assessment does not do

- It closes nothing. Full `S` stays **OPEN**; §7 item 4 is **UNASSESSED and unrouted to this lane**.
- It grades no artifact — not `78a8c2ee`, not the `θ` recommendation, not §5.7. Where those are cited
  it is to check §12's **use** of them against what they say.
- It supplies no mechanism, no route, no threshold and no number. `G2` and `G4` name missing sentences
  and a missing check; they do not write them. The recusal at `068436e5` stands.
- It authorizes nothing and ran no compute. Everything above is a repository read, arithmetic on
  quoted operands, or one local `r5_meter check`. **No cluster artifact was read**, so every figure
  sourced from `z-null.npz` or `z-cv.npz` is **RELAYED** and labelled so.
