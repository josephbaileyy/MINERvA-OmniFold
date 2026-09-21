# ASSESSMENT 2026-09-15 — `ε = 1e-9` as proposed, and `B`

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Requirements applied:** `E1`–`E12` and
`B1`–`B9`, committed at `923a321c` **before** this lane opened the proposal.

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR:** the two verdicts and the findings `F1`–`F4`; the measurements each rests on; and
the record that the requirements pre-date the reading.

**NOT CITABLE FOR:** adoption of anything. A grade of `B` — **there is no `B` to grade.** Any claim
that `ε = 1e-9` is refuted — **it is not.** Any authorization. Any claim that a Z covariance
exists; none has been constructed. `A1` stays **OPEN**, `ε` stays **PROPOSED and UNGRADED**, Gate 2
stays **FAIL**.

## THE TWO VERDICTS

| | |
|---|---|
| **`ε = 1e-9`** | **UNGRADEABLE AS AN `ε`.** Its three steps are sound and I confirmed all three independently, one of them more strongly than the proposal claims for itself. What they establish is a **feasibility floor**, which is the exact role `SPEC:1406-1409` assigns to a reproducibility floor while saying *"it cannot justify `ε`."* Taking that floor as the value is admissible only if the floor is `B`, and it is not `B` — the proposal says so itself. **Not a block, not a refutation, and not a criticism of the number** |
| **`B`** | **NOTHING TO GRADE — no justification exists.** And the evidence leg of the shape relayed to me would not meet `B1`, `B2`, `B5` or `B7`, on the ground of the requirement list **the proposing lane has already adopted** (`Z_CONSTRUCTION_PLAN.md:501-506`, items 1 and 2) rather than any list of mine |

**Both are complete answers, not deferrals.** The routing message said an ungradeable-as-it-stands
finding would be more useful than a qualified grade; that is what both of these are.

## Routing, and what in it is hearsay to me

The assignment reached me **relayed by a peer session**, not from Joseph. Every *"Joseph has
assigned"*, *"Joseph was explicit"* and *"accountability assigned"* statement in it is therefore
**hearsay to this lane** and is labelled so here. What I verified myself:

- **`owners.tsv:15`** reads `z-independent-assessor | Z criteria independent assessment |
  z-independent-assessor session [cb0b6b] | Joseph | assigned` — identical at `main` `9dba1194` and
  at `df0a8603`. The `display_name` is as relayed. **⚠ The `accountable_holder` names session
  `[cb0b6b]`, and this session is `d93bf047`.** No mapping between the two exists anywhere in the
  repository (searched: one hit, the row itself), and this lane's 52 commits carry no
  `Claude-Session` trailer, so **the row cannot be resolved to a session from the artifacts.** I
  proceed on the **owner_id**, which is a role; the session label is unverifiable and is not relied
  on. A reader who needs the identity settled must get it from Joseph.
- **`SPEC:2538` row 22** does disqualify the drafting lane by its own terms: *"This lane is
  disqualified by drafting."* So the routing away from the proposing lane is sound, and it is sound
  independently of who I am.

## Base

| object | sha / blob | note |
|---|---|---|
| `SPEC-20260906-…-successor-Z.md` | blob `296511ab601e44545d7ed3904811a74ee14b3094` | rev. 21; **byte-identical** at `9dba1194`, `8a42f8ea`, `df0a8603` |
| `RECOMMENDATION-20260910-…` §C | `8a42f8ea` | the proposal, read without touching the criteria worktree |
| `DECISION-SUPPORT-20260916-…` | `df0a8603` | routing record; its own base is `12250ba2` |
| `p4_lib.py` | blob `4f7e2133c0a9ac537c1a6ad241c4d82abb1cdc09` | **identical at all four shas** |
| `z_statistics.py` | blob `eb4edb3329232e4d55bdcef6cf0925d0ea3bb4b2` | **identical at all four shas** |

---

# PART 1 — `ε = 1e-9`

## The three steps, checked

**STEP 1 — PROVEN. CONFIRMED, and confirmed against the implementation rather than the algebra.**
The claim is `r_null ≤ max_i |Δ_i/x_i|` on the reported support. I checked it in **exact rational
arithmetic** — no floating point in the comparison — over `3,998` random draws constructed to
contain zeros and negative bins, calling the real `z_statistics.support_mask` (`:49`, `x > 0.0`):
**0 violations.** Four adversarial cases aimed at the bound, including one that puts a `700%`
deviation in a bin the predicate excludes: **0 violations.** The bound is **tight**, attained with
equality under a uniform relative deviation, and slack by `1/sqrt(3)` when one bin carries
everything.

The load-bearing detail is not the algebra, it is that `null_ratio` (`z_statistics.py:52`) masks
**both** operands with the same predicate — `a, b = x1[m], x2[m]`, then `denom = ‖a‖` and
`num = ‖b − a‖` (`:71-79`). Had the numerator been formed over the full vector and the denominator
over the support, step 1's inequality would fail. It does not.

*My first probe reported 36 violations at ratio `1.000001`. Those were my own construction's
rounding — `x2 = x + d` at `d/x ≈ 1e-9` recovers `d` with relative error `eps/1e-9 ≈ 2.2e-7` — not
the mathematics. The exact-arithmetic rerun is the measurement; the float one is not reported as a
result.*

**STEP 2 — EMPIRICAL. CONFIRMED, and its authority is STRONGER than the proposal claims.**
`REPRO_RTOL_PER_BIN = 1e-9` is at `p4_lib.py:93`; the statistic is at `:214`
(`rel = np.max(np.abs(a[m] - b[m]) / np.abs(b[m]))`); `REPRO_MEASURED_FLOOR` with
`worst_rel_bin = 1.9e-11`, job `56471429`, `n_reported_bins_pooled = 106940` is at `:196-202`.
Margin **`52.63×`**, reproduced by calling the module. The anti-tuning reasoning is in the source.

**The proposal calls it *"Joseph's own declared number"* and sources that to the code comment. It
is corroborated by something better, which this lane measured:** `REPRO_RTOL_PER_BIN` enters the
tree at **`5d617da8`, author `Joseph Bailey`, 2026-08-08**, *"Withdraw the sign argument, declare
the reproducibility tolerance, and log both findings"*, and the later widening at `57075066` is
his too. So the constant is a **human scientific declaration with git-verifiable authorship**, made
for another purpose, before this lane existed. `E8` is met squarely, and the one-day gap between
the comment's *"set by Joseph 2026-08-07"* and the commit date is the ordinary
ruling-versus-recording distinction, not a defect.

**STEP 3 — the judgement. This is where the assessment turns, and it is not about the numeral.**
Step 3 argues: adopt `1e-9` so Z's null gate is *"no stricter than the reproduction standard already
declared for this estimator chain, so it cannot fail a run meeting that standard."*

**Read exactly, that is an argument that `ε` must be AT LEAST this large.** It is a constraint from
below — do not fail runs that meet the accepted standard — and `SPEC:1406-1409` names that role and
that direction in terms: a measured floor *"may bound `ε` from below as a feasibility constraint;
it cannot justify `ε`."* Rev. 16 was found acceptance-blocking for inverting this direction; the
proposal does not invert it, but it does **take the lower bound as the value.**

`SPEC:1764-1769` permits exactly that — `ε = B` is admissible *"where the claim being supported is
about reproducibility itself"* — and §C.2 argues, correctly in my view, that this is that case.
**So the whole verdict reduces to one question: is the transferred `1e-9` a `B`?**

It is not, and the proposal's own last row says so — *"it does not establish `B`"* — with §C.4
measuring why. Against `E2`: no coverage, no confidence, no stated assumptions; it is a **gate
setting sized at ~52× one observed floor**, not a derived upper bound on error. Against `E11`: a
different subject and a different comparison, with the proposal itself recording *"direction not
established."* Against `B6`/§C.4: the envelope it would bound is **not pinned** — exactly one
launcher of eleven pins a literal `OMP_NUM_THREADS` and it is not arm 7, which is where the null
operands are computed.

**Hence `E1` fails, and `SPEC:1257` reject condition `4c` is the governing consequence:** *"An
un-derived boundary is not a criterion, and grading against one is the failure §3.6 exists to
prevent."* An `ε` adopted here would be adopted against a missing endpoint, and `4c` makes running
against it a REJECT. **That is the reason this is ungradeable rather than merely incomplete.**

## `F1` — NEW. There is a THIRD transfer limit, and it is the one that reaches Gap 1

§C.3 names two limits on the transfer (different subject; different comparison). **A third is
visible in the constant's own declaration and neither §C.3 nor `DECISION-SUPPORT` §2.2 carries it
into the `ε` argument:**

- `REPRO_MEASURED_FLOOR` records **`"conc_new": 6, "conc_reference": 4`** (`p4_lib.py:197`). The
  `1.9e-11` floor is a comparison **between two different concurrencies** — a between-envelope
  measurement.
- The tolerance's margin was sized for that: *"roughly two orders above the measured floor **so a
  CONC change does not force a re-derivation**"* (`p4_lib.py:89-90`).

**This cuts both ways and I report both.** In the proposal's favour: the imported number is the
right *kind* of quantity for a requeueing campaign, which is more than §C.3 claims for it —
`SPEC:1802-1818` (Gap 1) and §C.5 both say `r_null` **cannot** measure a between-envelope shift, and
the source constant was set against one. **Against it:** a tolerance sized for a cross-concurrency
comparison, applied to a **within-one-process** null, is loose by a further factor nobody has
bounded, on top of the `52×`. `E12` is about matching envelope scope to the claim, and this
mismatch runs in the direction of a weaker gate.

`DECISION-SUPPORT` §2.3 shows the lane knows `56471429` is a concurrency pair — it corrects an
earlier reading that *"attached the concurrency-pair caveat to the wrong number."* **The finding is
not that the fact is unknown; it is that it is not carried into the argument where it changes what
kind of quantity `1e-9` is.**

## `F2` — NEW, and it is the concrete threat. BOTH endpoints are missing, not one

Every statement of the position — §C.2, `DECISION-SUPPORT` §2.1, and the routing message — treats
`S` as loose and therefore **not binding**, and derives from that the routing conclusion *"`ε` must
be argued from `B`'s side."* **That conclusion rests on a bound covering one channel of at least
three.**

- The proven `|‖ms'‖ − ‖ms‖| ≤ ‖dx‖` bound and the `1.7957e11` / `2.0433e11` factors are the **F7
  branch's** cap. I reproduced both from the quoted operands.
- The uncovered channels are the throw deviations and the completeness division. **`SPEC:1662`
  describes the second in terms:** an elementwise division *"by a quantity that can be small"* and
  *"an amplification channel with no `n`-dependent bound."*
- So `ε ≤ S` — the **upper** endpoint of `E1`'s interval — **is also not demonstrated.** It is not
  merely that `S` is loose; `S` over the quantity `ε` gates does not exist, and the channel nobody
  has bounded is the one the governing document flags as unbounded in principle.

**What follows is a scope repair, not a refutation.** The defensible sentence is *"`S` is not
binding **through the F7 channel**."* §C.2 does state the gap in the adjacent paragraph — but the
unqualified sentence is the one that travelled: it is the stated reason `B` was given accountability
and the reason `ε` is argued from `B`'s side at all. If an uncovered channel's cap turned out tight,
`S` could be binding after all and the routing would change. **`§7` item 4 — *"arithmetic + one code
read"* — is upstream of more than it looks.**

## `F3` — NEW. The consistency check §C.3 left UNRESOLVED is now answerable, and the answer matters

§C.3 asked whether the gate would pass an actual null and had to stop: *"`‖x_cv‖` is not persisted …
so G's `r_null` is UNRESOLVED and I am not quoting one."* **For G that is still true. But a
Z-family subject now carries the operands**, and the routing record itself reports them
(`DECISION-SUPPORT` §3, from the 2026-09-15 bridge record, product sha256 `09a029ed…`):

```
cv_norm  = 3.2124510692799616e-37      num_norm = 1.4301832847122437e-50
r_null   = 4.4520002137582904e-14      (num/den reproduces it exactly -- re-divided here)
n_cv_bins_total 65856 = n_cv_support 10694 + n_cv_genuine_zero 55162,  n_cv_negative 0
```

**`ε / r_null = 2.246e4`.** §C.2's own disqualifying standard is that an `ε` from the scientific
side *"is a gate essentially nothing can violate — which is exactly the `1e-12`-clamp defect §3.1a
measures."* That standard, applied to §C.3's own number, gives four orders of magnitude rather than
eleven — much better, and **not obviously a tripwire either.** Whether `2.2e4` of headroom is
acceptable for a determinism-and-provenance tripwire is a scientific judgement, and it is
**precisely the judgement `B` is supposed to inform.** Nobody has made this comparison.

**Three limits on this observation, and they are not softeners:** it is the **precursor's** null,
not Z's; it is **one** observation, from an **unpinned**, **within-process** execution, so it is
not a floor and not a bound; and `SPEC:1410` forbids reading `ε` off Z's own null. **It cannot set
`ε`, and I am not proposing that it should.** It bears only on the proposed `ε`'s discriminating
power, which §C.2 made a criterion.

*And it supplies the one thing §C.3 says is missing about the transfer.* The source chain's floor
`1.9e-11` sits **`427×` above** the target family's observed within-process null `4.452e-14`.
Populations named on both sides: standard-P4 5D chain / cross-concurrency / per-bin max, versus
Z-precursor / within-process / L2 ratio. Two different statistics on two different subjects, so it
is weak evidence — but it is evidence, and it runs toward the transfer being **generous**, which is
the direction that makes the gate weak rather than unsafe.

## `F4` — the falsifier is UNEVALUABLE, not merely unevaluated

The routing message's point (a) holds, and is stronger than stated. The falsifier reads *"if
pinned-envelope repeats of the full CV chain show a floor above about `2e-11` for Z's bank."* **Both
of its operands are unbuilt:** no pinned envelope exists (§C.4, measured — one literal pin in
eleven launchers, not arm 7), and no Z bank exists. So the falsifier yields **no evidence in either
direction today**, and cannot until after the object it gates is built.

**The withdrawal of `B_loose` is correct and I confirmed it independently.** `1.831e-11` is
`INTEGRAL_LEG_COHERENT_CEILING` at `p4_lib.py:158`, described at `:115` as *"the fully COHERENT
ceiling"* — a **different** figure from job `56471429`'s `worst_rel_bin = 1.9e-11`. It is from the
standard-P4 chain, which is the **source** side of the transfer, so placing it beside the
falsifier's `2e-11` tests the transfer against itself. `p4_lib.py:138-141` also warns that the
related margin *"is **NOT slack** … already sits at 54.6% of the coherent ceiling"*. I reproduce
`54.61×` for `1e-9 / 1.831e-11` and `52.63×` for `1e-9 / 1.9e-11`; **the two are not
interchangeable and the proposal is right to use the second.**

## What I checked and did NOT fault — recorded so it is not rediscovered as a finding

- **The mask mismatch between the two statistics is harmless, and empirically void.**
  `check_reproducibility` masks on `|b| > 0` (`p4_lib.py:212`); `support_mask` masks on `x > 0`. The
  p4 mask is a **superset**, so its max runs over more bins and the inequality chain
  `r_null ≤ max_rep ≤ max_p4` still holds — the direction is safe. And on the one Z-family product
  that carries the predicate, `n_cv_negative = 0`, so the two masks **coincide** there. I looked for
  a finding here and there is none.
- **`sqrt(Tr C)` is correctly rejected as the denominator**, and §C.1's second ground is real: three
  committed sqrt-traces exist for one null, a `20.9%` spread for the same measured number.
- **The `52.63×`, `54.61×`, `1.7957e11`, `2.0433e11` and `65856 = 10694 + 55162` figures all
  reproduce** from the quoted operands.
- **§C.2's `S` argument is a genuine proven bound within its channel**, and §C.2's refusal to assert
  a mechanism for the other two channels is the right refusal, not a gap in candour.

## What would make `ε` gradeable

Nothing in this document. `E1` needs a `B`; `F2` says the upper endpoint needs `§7` item 4. Those
are two named, zero-compute acts owned elsewhere, and **naming the route to either would be this
lane supplying the design it would then be asked to review.** I name the requirement and stop.

---

# PART 2 — `B`

## Verdict: nothing to grade

No justification for `B` exists. §C.4 is the strongest statement in the corpus that route (i)
**cannot be claimed today**, it is measured rather than argued, and this lane confirms its two
load-bearing measurements: exactly one `.sh` in the family pins a literal `OMP_NUM_THREADS` and it
is not arm 7; and `make_estimators` pins `random_state` and nothing else.

## The shape relayed to me, against `B1`–`B9`

The relayed proposal is *"route (i), pin the LightGBM knobs and arm 7's threads … evidence is arm 7
twice on the same slabs, pinned vs unpinned, `x_cv` compared elementwise; cost ≤ 0.58 CPU
task-hours, unauthorized."* **That evidence leg is `Z_CONSTRUCTION_PLAN` §4.5** (`:528-552`), and
the finding below is the subject's own, not mine:

| req | verdict on the shape as relayed |
|---|---|
| **`B1`** upper bound with assumptions and confidence | **NOT MET.** Two executions compared elementwise yield **one observation**, not a bound with coverage or confidence. §4.5 itself claims only what it delivers: *"What it measures: the CV-unfold's **sensitivity to the envelope**"* |
| **`B2`** envelope of the bound = envelope of the evidence | **NOT MET, and this is the sharpest point.** *Pinned vs unpinned* compares **across** the pinning boundary. That is the **divergence pinning causes** — which §C.4 says *"must be declared with Z's build"* and is a **scientific act** — and it is **not** reproducibility **within** the pinned envelope. `Z_CONSTRUCTION_PLAN:501-506` items 1 and 2 say it directly: repeats must be of the **full chain** and must **span different allocations**, because *"repeats on one node … test in-process determinism, which is the easy half."* §4.4a's own closing line is the consequence: *"If item 1 or 2 fails … route (i) does not deliver a design property at all"* |
| **`B3`** subject named and disposed against §6.4 | **UNRESOLVED.** *"The same slabs"* does not name the bank. `SPEC:1830` says both horns must be chosen and that the own-bank horn *"needs Joseph's ruling rather than this lane's reading of §6.4"* |
| **`B4`** sampling assumptions stated | **NOT STATED.** `SPEC:1828` — repeats inside one job share a node, a library load and a page cache; the design must say which assumption it makes |
| **`B5`** predeclared estimator, repeat count, envelopes | **NOT MET.** *"Compared elementwise"* is a comparison, not an **estimator of `B`**. `SPEC:1829` is explicit that predeclaring these three, and committing not to revise them, is what prevents tuning |
| **`B6`** a design-property claim covers only the pinned configuration | **MET in §C.4**, which adopts `z_reproducibility`'s caveat verbatim rather than softening it |
| **`B7`** bit-identity is not `B` | **NOT MET, and the baseline is on the wrong arm.** The relayed falsifier baseline — `operands_bitwise_identical: False` at relative L2 `4.452e-14` — refutes the **stronger** claim and supplies no value for `B`; and it is the **PRECURSOR's** observation, which ran **unpinned**. So it says nothing about whether the **pinned** chain is bit-identical, which is the claim route (i) rests on. **The routing message names this trap itself and is right to** |
| **`B8`** cost priced against the right operation and partition | **ONE FLAG, not a finding.** `≤ 0.58` is the largest of three historical `uthrow5d_combF` runs, which `SPEC:1832-1886` marks **TRANSFERRED** — *"neither this bank nor this slab count."* §4.5 reads *"one **additional** arm-7 invocation"*, i.e. the unpinned arm is an existing product. **Which invocations the figure counts should be stated**, because if the unpinned arm is the precursor's run then `B2` bites harder — that arm's thread environment was never recorded |
| **`B9`** no assumed authorization | **MET.** The message says *"unauthorized"* and *"I hold no authorization to give you any."* Correct, and `SPEC:1901` agrees: `D-RESOURCE` does not exist |

**So `B` is not merely unbuilt — the evidence described would answer a different question.** That is
a finding about the **relayed shape**, and the designer may send something else; it is not a grade
of §4.5, which is honest about what it measures, nor of §C.4, which is the reason route (i) is not
claimable.

## The boundary I am keeping

`Z_CONSTRUCTION_PLAN` §4.4a is cited above as the ground for `B1`/`B2`/`B7`. **That is not this lane
supplying a design:** §4.4a is the *proposing* lane's own list, and §C.4 already adopts it — *"I add
nothing to that list; I confirm it."* Checking a proposal against a requirement set its author has
adopted is assessment. **Naming which of route (i), (ii) or (iii) to take, or how many repeats to
run, would be design, and I do not.** The partial recusal declared at `068436e5` stands.

## A naming hazard, filed

At least **four** live objects wear the letter `B`: `SPEC` §3.7a's operating-error bound (this
part); publication **Endpoint B** (DEFERRED NOT PASSED); the `cstat` / `lane_b` owner rows; and
`Z_CONSTRUCTION_PLAN` §1.1's *"B's footing"*, which that section **already disambiguates into three
further senses** and resolves to the throw-ensemble basis. The routing message puts two of them in
one sentence. This document writes **"§3.7a's `B`"** wherever the bound is meant.

---

## What this assessment does not do

- It adopts nothing, authorizes nothing, and grades no cell. `A1` stays OPEN.
- It does not refute `ε = 1e-9`. The number may well survive a derivation; what is missing is the
  derivation, and `SPEC:1257` `4c` is why that gap is disqualifying rather than cosmetic.
- It runs no compute and required none. Everything above is a read, arithmetic on quoted operands,
  or a local exact-arithmetic probe.
- It does not resolve the proposing lane's open questions 3–7, or the `z_reproducibility.py:412-415`
  stale-margin defect `DECISION-SUPPORT` §2.3 routes to `lane_b` / `standard_p4`. Those are not mine.
- It does not settle who `[cb0b6b]` is.
