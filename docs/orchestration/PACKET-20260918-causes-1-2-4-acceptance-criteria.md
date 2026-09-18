# Acceptance criteria for causes 1, 2 and 4 — all three are TOLERANCE-FREE

**Owner:** `owners.tsv:14`, `z-criteria-designer session [91eaa2]`. **Authorized by Joseph** 2026-09-18
under the publication-completion goal (`PLAN-20260918-scalar5d-publication-completion.md`, `ecdb150f`).
This lane **prepares**; `owners.tsv:15` `[cb0b6b]` **evaluates**. **Base:** `9836a64f` (lane).

**CITABLE FOR:** acceptance criteria for `(cause 1, Z)`, `(cause 2, Z)`, `(cause 4, Z)`, with
falsifiers and required evidence.

**NOT CITABLE FOR:** anything adopted or graded. **Design only — no compute, no member production, no
cluster access.** Cause 3's `cause3_agg`, `cause3_med`, `cause3_corr` remain **WITHHELD** and nothing
here touches them. Gate 2 **FAIL**, endpoint B **DEFERRED NOT PASSED**, `S` **OPEN**. No value from
`nd-unfolding/mii/member_k000000/` is quoted.

⚠ **I AM THIS PACKET'S AUTHOR AND CANNOT BE ITS ASSESSOR.**

---

## 0. THE ORGANIZING RESULT — ALL THREE NEED NO TOLERANCE, SO NONE IS BLOCKED ON THE CLOSED QUESTION

**Measured against each cause's governing clause, not assumed:**

| cause | governing clause | why no tolerance exists |
|---|---|---|
| **1** | `SPEC` §6.2 `:3509-3527` | closure is **"irrespective of magnitude"** — so magnitude is *by ruling* not the criterion. What remains is **disclosure completeness**, a checklist with refusals |
| **2** | the **F7 branch**, `f7_cv_centered_required`, with `F7_FLOOR_MULTIPLE = 2.0` and a strict `>` | the branch is **binary** and its floor multiple is **already fixed in code**, not chosen. There is no free parameter to justify |
| **4** | `SPEC` `:1005-1019` four conditions + `:1237` receipt row | condition 3 requires the covariance content **not to change at all**, and all four conditions plus every refusal are **binary predicates** |

⚠ **CONSEQUENCE, AND IT IS THE POINT OF THE PACKET: none of these three can be blocked by the
unestablished quantity that closed `θ` and blocks `cause3_agg`/`δ_bin`**, because none of them asks
"how much movement is scientifically acceptable." **All three are approvable in full today** — form,
population *and* value — which is not true of any cause-3 boundary except L4.

**This is the fourth instance of one structural pattern** (after `B`'s boolean estimator, cause 3's L4,
and now these): **when the protected quantity is discrete, or closure is magnitude-independent, the
criterion has no knob — so Gap-3-style tuning is impossible by construction rather than by
restraint.** The three carried principles are used below and not re-derived:

1. **A criterion whose statistic cannot *see* the quantity it names is vacuous regardless of its
   tolerance** — used at §2.2 and §3.3.
2. **A population declaration replaces a judgement when the population is fixed by use rather than
   chosen** — used at §1.3 and §2.3.
3. **A criterion no member of its own family can pass is unsatisfiable by construction** — used at
   §1.4 and §3.4.

**And the narrowing that makes "what does this protect" answerable at all** is relayed and I rely on
it. ⚠ **CORRECTED 2026-09-18 on its author's re-run: the corpus is TWENTY-FOUR sources, not twenty**
— their original count came from a listing truncated by `head -20`, though the `*.tex` glob did cover
all 24, so the **sweep** was complete and only its **description** was wrong. The re-run also
**widened the vocabulary** (`p-value`, `confidence level`, `% CL`, `standard deviation`,
`statistically significant/compatible/consistent`, `excluded at`, `tension at/of`) and inspected all
four hits: a closure residual, two ensemble-precision statements, and `primer_body.tex:190`'s
explicitly **central-value** *"localized central-value difference"*. ⚠ **One hit was a SUBSTRING
FALSE POSITIVE** — `"tension of"` matched inside *"ex**tension of** the signal definition"* — and
that cuts both ways: **a pattern that finds a phantom will as happily miss a real one.** So the
ground now rests on better evidence than when §0 first relied on it:
across those 24 sources **no covariance-dependent claim is asserted**, `AGENTS.md:30`
quarantines the `(E_avail,W)` covariance itself, and `AGENTS.md:27` requires projection from the adopted
**selection-complete** trunk — VERIFIED, the row reads *"The quotable covariance must be projected from
the final adopted, selection-complete 5D trunk."* So **the claim set is one and the map set is one**,
which is the ground all three criteria below stand on.

---

## 1. `(cause 1, Z)` — ONE-SIDED ENDPOINTS: a DISCLOSURE-COMPLETENESS criterion

`SPEC` §6.2 **RULED**, verified verbatim: closure on *"a **complete, artifact-specific measurement**
plus the `RULING 1` disclosure, **irrespective of magnitude**, once **independently verified**."*

### 1.1 THE CRITERION

    MET iff  (a) the comparison of BOTH one-sided choices is complete per section 1.2,
             (b) the RULING 1 disclosure states what section 1.5 requires,
             (c) it has been INDEPENDENTLY VERIFIED  -- not self-verified,
        and  (d) no refusal in section 1.4 fires.
    There is NO magnitude threshold, and none is to be introduced: section 6.2 rules closure
    irrespective of magnitude, so a tolerance here would ADD a criterion the ruling removed.

### 1.2 THE COMPARISON DESIGN — what "complete" means

Both one-sided choices, against the **actual two-endpoint construction on Z's own bank**, and:

- **off-diagonals included.** A diagonal-only comparison is the §0 principle-1 failure: the statistic
  would not see the quantity the criterion names. **The comparison object is the full block, and the
  reported statistic must respond to an off-diagonal-only change** — the same sensitivity test cause
  3's §11 arrived at, reused rather than re-derived.
- **below-one tails included.** A one-sided choice replaces a `±` pair by one arm; the induced ratio can
  fall **below 1**, and truncating at 1 would silently make the comparison one-directional. **Report
  the signed distribution, not its magnitude.**
- **denominators stated per statistic.** Every ratio names its denominator and its population in the
  same sentence; this campaign's most-repeated defect class is a bare ratio.
- **Flux, three-universe 2p2h and normalization carried UNCHANGED**, and **explicitly accounted for** —
  §6.2 is explicit that they are already in both totals and that *"changing their construction is a
  proposed criterion extension, not merely filling missing arithmetic."*

### 1.3 THE NON-PAIR BANDS — a POPULATION DECLARATION, not an invention

§6.2: *"The three non-pair bands are accounted for explicitly and their endpoints are **NOT
invented**."* So the population splits by **construction**, not by choice — principle 2 applies and no
judgement is needed:

    population A : the two-endpoint bands        -> both one-sided choices compared
    population B : the THREE non-pair bands      -> ACCOUNTED FOR EXPLICITLY, endpoints NOT invented;
                                                    their contribution is REPORTED as unpaired, never
                                                    imputed
    The declaration names which bands are in B by NAME, prospectively, and the receipt asserts
    |A| + |B| equals the declared band total -- an exhaustiveness assertion, not an assumption.

### 1.4 REFUSALS — binary, and the third is principle 3

1. **Any `±` endpoint is invented for a non-pair band** → refuse. This is not a tolerance breach; it is
   a different measurement.
2. **Flux, 2p2h or normalization construction is changed** → refuse and route as a **criterion
   extension** requiring its own decision, which §6.2 says this specification does not make.
3. ⚠ **The comparison is self-verified** → refuse. §6.2 conditions closure on *independent*
   verification, so a criterion graded by its own producer **cannot be passed by any member of its own
   family** and would be unsatisfiable in the sense §0 principle 3 names.
4. **A reported ratio lacks its denominator or its population** → refuse.

### 1.5 WHAT THE NOTE MUST STATE — `OI-172`'s obligation, discharged by content not by reference

`RULING 1` (2026-09-01) found cause 1's magnitude *"material enough to need its own statement in the
note"* and did **not** close cause 1 **for G**; §6.2 records that G's cell is unchanged. So:

    The note must state, for Z: that the construction is two-endpoint; that both one-sided
    alternatives were measured and the measured spread between them; that THREE bands are
    non-pair and their endpoints were NOT invented; and that Flux, 2p2h and normalization
    are carried unchanged in both totals.
    ⚠ It must NOT state or imply that G's cell is closed. The two cells are separate and
    section 6.2 says so.

---

## 2. `(cause 2, Z)` — CV CENTERING. ⚠ THE CONTRADICTION IS NOT REAL, AND THAT CHANGES THE CRITERION

**I was asked to hold two facts together: `AGENTS.md:29`'s *"mean-centering alone is disqualified"* and
`ESTIMATOR_REGISTRY.md:29`'s *"adopted mean-centered"*, as *"the cause-2 question in its sharpest
available form."* ⚠ MEASURED: THEY DO NOT CONFLICT, AND THE WORD DOING THE WORK IS "ALONE."**

### 2.1 "MEAN-CENTERING ALONE IS DISQUALIFIED" **IS** THE F7 BRANCH OUTCOME

`FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md`, VERIFIED:

- `:16` — *"floor `sqrt(Tr C)/sqrt(N)`; **at the floor, mean-centering alone is acceptable; well above
  it**, the …"*
- `:52` — *"**pairing disqualifies mean-centering alone**, which is also `VALIDATION_LEDGER.md:404`'s
  own conclusion"*
- `:55` — *"So mean-centering alone is disqualified **for the CANDIDATE**, not only for the July
  artifact."*

**So the clause is not an independent ruling against a centering convention. It is the recorded
CONSEQUENCE of the F7 branch having fired** — the measured ratio sits well above the floor
(`5.3478 > 4.8288 > 4.510 > 2.0`, `FINDING:148`), so the CV-centered variant is *additionally
mandatory*, and mean-centering **without its CV-centered companion** is what is disqualified.

⚠ **And the registry satisfies exactly that.** Row `:29` records the mean-centered product **and the
CV-centered variant beside it** — `√tr 5.8077e-38`, *"CV-centered variant `6.2367e-38`"*, mean shift
`1.654e-38` separate. **Both records hold simultaneously. There is no contradiction to resolve, and
resolving a non-existent one would have produced a criterion protecting nothing** — which is why this
check came before the criterion.

### 2.2 SO CAUSE 2 IS NOT "WHICH VARIANT" — IT IS "RE-EVALUATE THE BRANCH FOR Z"

The ground for the choice already exists and is in code. What is missing is that **Z inherits nothing
from G**, so the branch must be evaluated on **Z's own** operands:

    MET iff  (a) f7_cv_centered_required is evaluated on Z's OWN v_uni/v_blk and N -- not inherited;
             (b) the POPULATION IDENTITY accompanying the ratio is stated (OI-186/188, RELAYED);
             (c) BOTH variants are carried whenever the branch returns True, and the receipt records
                 the ratio, the floor, F7_FLOOR_MULTIPLE and the strict-`>` comparison; and
             (d) no historical grade is reused as Z's.
    NO TOLERANCE: the branch is binary and F7_FLOOR_MULTIPLE = 2.0 is already fixed in code.

**Principle 1 applies to (b):** a ratio quoted without its population is a statistic that cannot be
checked against the object it names. `OI-186/188`'s requirement is relayed and I have not verified it;
it is marked as relayed and is a **required check**, not an assumption.

### 2.3 THE RELATIONSHIP TO CAUSE 3's L4, WHICH COMPOSES CLEANLY

**Cause 2 is the branch's VALUE for Z. L4 is the branch's STABILITY across the estimator-seed member
set.** They are the same quantity at two scopes and neither substitutes for the other:

    cause 2 :  f7_cv_centered_required(C_Z)          evaluated once, on Z's own population
    L4      :  that outcome IDENTICAL for every k     across the cause-3 member set

⚠ **And this retires a question I left open.** My cause-3 §10.3 asked whether an unestablished
seed/centering mechanism would change L4's *stakes*. §2.1 answers the adjacent half: the *disqualifying
clause* is the branch outcome, so **L4 protects the stability of a decision that is already ruled to be
load-bearing** — which is a stronger reason to keep L4 than the one I gave. The mechanism itself remains
unestablished and cause 2's criterion does not depend on it.

---

## 3. `(cause 4, Z)` — JITTER SUBTRACTION. ⚠ A "BOUND" IS THE WRONG INSTRUMENT

**I was asked for *"a print-only add-back comparison bound for Z."* ⚠ There is nothing to bound:
`SPEC:1007` condition 3 requires that adding the print *"does not change the covariance content"* —
not that it changes it by little.** A bound would presuppose a permitted change and would therefore
**weaken** the specification. The criterion is four binary conditions and a guard.

### 3.1 THE CRITERION — `SPEC:1005-1019`, verified verbatim

    MET iff all four hold:
      1. the QUANTITY is  jit_trace = float(np.sum((x_cv2 - base) ** 2)),  with x_cv2 a second
         CV unfold at SEED + 7, recovered from a0cdc019:232-252 and compared LINE FOR LINE;
      2. the OPERANDS are the new build's own -- both vectors' content digests in Z's receipt;
      3. adding it DOES NOT CHANGE the covariance content;
      4. the print is PRINT-ONLY, NEVER SUBTRACTED.
    plus: the SINGLE-DRAW nature stated with its seed named, and the `M` referent being the
    REPORTED RATIO per OI-173 RULING 2.

**The single-draw referent is RETAINED and multi-draw is not to be revived** — §6.5, on the reviewer's
directive, adopted by Joseph: *"the defect cause 4 names **is** a single-draw subtraction, so a
multi-draw `M` would measure something the defective construction never did."*

### 3.2 THE GUARD, AND WHY A ONE-TIME COMPARISON IS EXPLICITLY INSUFFICIENT

`SPEC:1010-1012`: the condition *"must be enforced by a **guard that fails** if the computed value ever
reaches the stored covariance, **not by a one-time comparison**."* **This is the
green-gate-that-proves-nothing shape named in the specification itself** — a passing comparison today
says nothing about the next edit, and *"a quantity in scope is one edit from being subtracted."*

⚠ **ONE CITATION AMBIGUITY, FLAGGED NOT RESOLVED:** `:1010` attaches the guard to **condition 3**
(*"Condition 3 must be enforced by a guard…"*) while the receipt row `:1237` attaches it to **condition
4** (*"condition 4 enforced by a guard"*). The two conditions are near-identical in content, so nothing
material turns on it — **but a guard implementer needs one answer, and I am not the one to pick.**
Routed.

### 3.3 REFUSALS — all binary, from `:1237`

1. the quantity **differs** from `a0cdc019:232-252`;
2. **operands borrowed** rather than the new build's own;
3. **covariance content changes**;
4. the value is **ever subtracted**;
5. `M` reported **against the stored covariance** rather than as the reported ratio.

**Principle 1 applies to refusal 3:** the check must be able to *see* a content change, so it is a
digest comparison on the stored object, not an inspection of the print.

### 3.4 TWO PROHIBITIONS CARRIED, AND WHY THEY ARE TEMPTING

- ⚠ **Do NOT subtract a scalar jitter estimate from its covariance.** `jit_trace` is a **one-sample
  estimate of a variance** (`:1014`) and a trace-like scalar; subtracting it from a matrix is
  dimensionally incoherent and is the act condition 4 exists to prevent.
- ⚠ **Do NOT reopen the historical log sweeps.** `OI-173`'s stamped-candidate referent and its
  permanent-unmeasurability disposition concern **that historical subject, not Z** — and by §0
  principle 3, importing a permanently-unmeasurable referent into Z's criterion would make Z's cell
  unsatisfiable by construction.

---

## 4. FALSIFIERS AND REQUIRED EVIDENCE

| cause | explicit falsifier | evidence needed |
|---|---|---|
| **1** | a completed comparison in which a non-pair band's contribution turns out to have been **imputed** rather than reported unpaired — which falsifies the population declaration, not the magnitude | the two-endpoint construction on Z's bank; both one-sided variants; the named non-pair band list; **independent** verification |
| **2** | `f7_cv_centered_required` evaluated on Z's own operands returns a **different** outcome from the inherited one, **or** the population accompanying the ratio is not statable | Z's own `v_uni`, `v_blk`, `N`; the `OI-186/188` population identity (**RELAYED, unverified here**) |
| **4** | the guard **fails to fire** under a deliberate mutation that routes `jit_trace` into the stored covariance — ⚠ **a guard that has never been made to fire is untested, not proven** | the recovered `a0cdc019:232-252` lines; both operand digests; the seed (`seed + 7`); a **mutation test** of the guard |

⚠ **A falsifier common to all three:** if the relayed narrowing is wrong — if any covariance-dependent
claim *is* asserted somewhere in the corpus — then §0's "one claim, one map" ground fails and all three
criteria need their populations restated. **That sweep is relayed and I did not run it.** ⚠ **UPDATE
2026-09-18: its author re-ran it on a widened vocabulary and it SURVIVED, with the corpus corrected
from 20 to 24 sources (§0). The falsifier therefore stands UNTRIPPED rather than unevaluated** — a
distinction this lane has been corrected on before, and the two are not the same status.

---

## 5. APPROVAL RECOMMENDATION

**RECOMMENDED FOR APPROVAL IN FULL — form, population AND value — for all three**, because all three
are tolerance-free (§0) and therefore carry no number that could be contaminated by a favourable
result:

1. **§1** cause 1's disclosure-completeness criterion, its comparison design, its population
   declaration and its four refusals, **with no magnitude threshold added.**
2. **§2** cause 2's branch-re-evaluation criterion, **on the finding that the front door and the
   registry do not conflict** (§2.1).
3. **§3** cause 4's four conditions, the guard requirement **with a mutation test**, and the two
   prohibitions.

**NOT RECOMMENDED:** nothing is withheld for want of a value. **Two items are routed rather than
decided:** §3.2's condition-3-vs-4 guard ambiguity, and §2.2(b)'s `OI-186/188` population-identity
requirement, which is relayed and unverified here.

## 6. RESIDUES

1. **`OI-186/188` and the twenty-source corpus sweep are RELAYED and unverified by me**; both are
   load-bearing for §2.2(b) and §0 respectively.
2. **§3.2's guard-condition ambiguity** is unresolved and is not mine to pick.
3. **Nothing here unblocks `cause3_agg` or `δ_bin`** — §0 explains why it does not need to.
4. **I did not re-derive the three carried principles**; they are cited to their cause-3 origin.
5. **The F7 mechanism from cause-3 §10.3 remains unestablished** and §2 does not depend on it.
