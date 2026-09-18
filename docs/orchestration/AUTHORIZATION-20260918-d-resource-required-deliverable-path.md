# `D-RESOURCE` — STANDING AUTHORIZATION, the required scalar-5D deliverable path

**This is the record `SPEC` §4 row 19 names and says does not exist** (*"`D-RESOURCE` — an exact
resource authorization naming a Z run (`R5`)… **NO — it does not exist**"*), cited again at
`SPEC:1901`, `:2814`, `:3103`, `:3707`, `:3813`, and required by `D3`'s fourth prerequisite. It
exists now. **Authority: Joseph, 2026-09-18, in his own turn.**

**CITABLE FOR:** the objective, the compute posture, and the nine rulings below.
**NOT CITABLE FOR:** adoption, publication submission, any optional claim, or any threshold not
stated here.

---

## 0. THE OBJECTIVE — written here so no lane re-derives it from a packet

> An **adopted scalar-5D covariance**; the **required verified projections with correctly paired
> central values**; **synchronized note / primer / paper**. **Submission is Joseph's act.**

Every ruling below serves that and nothing else.

## 1. COMPUTE POSTURE

**Pre-approved for anything on the required deliverable path** (the §2 blocker table of
`DECISION-PACKET-20260918-scalar5d-publication-blockers.md`): **run it, record it, report
afterward. Do not pause to ask for an allocation on that path.**

**Optional work still requires a separate ask.** This is deliberately not a blanket approval.

Unchanged and binding: `R5`'s ceilings (`500` GPU / `500` CPU task-hours, `t0 2026-09-02T13:44:27Z`,
stop `2026-09-30`); per-submission accounting and admission via `r5_meter.py`; reservations priced as
**enforced cap × tasks**, never a measured actual; one corrective resubmission per stage after a
diagnosed defect, verified repair and fresh admission; automatic requeue disabled.

## 2. THE RULINGS

| # | ruling |
|---|---|
| **1** | **SCOPE AMENDMENT — APPROVED.** The required deliverable set **excludes the generator significance**; the significance is a separate, later, **optional** claim. `main_paper.tex:49-51` already defers it. Deferred with it and **not** on the required path: `y_gen`, `N`σ, the 12-cell χ², the retained-subspace rule, `rcond`, any pseudoinverse, the first-order statistic, and the conclusion-flip `τ`. |
| **2** | **CAMPAIGN — `k₁` DECLINED. The `158.25` GPU / `262.00` CPU reservation is NOT approved and is RELEASED.** Nothing required needs `N`, and `N` is what that campaign buys. **Not to be re-proposed as part of the required path.** |
| **3** | **`SPEC` §3.7d — RULING (b). ADD `s_proj`.** Answer (a) withholds the licence for marginalization and projection, and projections are a required deliverable, so (a) was never available. **It stays a requirement, not a caveat.** |
| **4** | **FUNCTIONAL SET — APPROVED:** the rows of `project_cov_nd.py`'s `M`, plus the all-ones vector. It **dissolves** the region question rather than answering it. The earlier corner-integral criterion is a strictly weaker special case. |
| **5** | **δ = 5% — APPROVED.** `δ_proj = δ_med = δ_agg = 5%`, a **direct movement bound, never quadrature**. Ground: a drift below the `~5.6%` precision the 160-throw ensemble already imposes on `σ` is not resolvable against the number it would modify; at `10%` the arbitrary seed would be `1.78×` the ensemble's own smearing. **Coverage:** 100% on bins entering a quoted projection, **≥99%** on the full reported support, **every failing bin enumerated in the receipt and never absorbed.** |
| **6** | **CAUSES — C1, C2, C4, C5, C6, C7 APPROVED as recommended; R5 approved as documentation and verification with no recomputation.** Detail in §3. |
| **7** | **§6.4 NULL ROUTE — P0 first; P2 not before P0 returns; the exception is APPROVED AS DRAFTED AND HELD, not executed.** Order: **P0 → if needed P2 → only if bitwise identity is unreachable, the exception.** |
| **8** | **PINNING — RESERVED, reaffirmed.** Do **not** apply `deterministic` / `force_row_wise` / `num_threads` to `make_estimators`. A material estimator change. **Not to be routed around because the null row is live.** |
| **9** | **ORDER FIXED:** C1–C7 complete → NULL resolved → **ADOPT (Joseph's act)** → PROJ re-run on the adopted trunk with `--run-class publication` → DOCS re-verified. **No step waits on anything optional.** |

**Throughout: no assembly of incomplete members. 20 of 21 block tasks is not a member.**

## 3. THE CAUSE DISPOSITIONS, as ruled

- **C1** — tolerance-free **disclosure**, `≈0.03` CPU task-h. On the required path, so authorized.
- **C2** — wording is *"inherits a tolerance with a stated derivation and an owner"*, **not**
  *"not chosen"*. Create `cause2_f7_margin` **withheld**; the margin comes back to Joseph.
- **C4** — amend `SPEC:1237` from *"condition 4"* to *"condition 3"*, then the print.
- **C5** — **closed as not-falsified, scoped to the 15 traced modules.**
- **C6** — **REUSE**, with the accepted risk named: **"inputs consistent but unproven."** Both
  withdrawals stand: observed inventory is not proven producing inputs, and **absence of a scheduler
  record is not proof of interactive execution** — the honest statement is that the producing act has
  no scheduler record I could find. Regeneration would not recover this object's provenance.
- **C7** — **closed as sufficient**, on the twice-measured 45-band partition.
- **R5** — amend `ESTIMATOR_REGISTRY:29` to the **consumed** file and record **both** `√tr`.

## 4. ANSWER TO THE QUESTION BACK (§8) — and P0 IS ALREADY DONE

**P0 was executed at `1405caad`, before this exchange.** Source only, zero compute, no payload. I am
reporting it rather than re-running it.

**P0's RESULT — the unfavourable branch of its two outcomes:**

> **The pair IS like-for-like.** `unified_throw_cov.py:846` takes `base = x_cv[rep]`; `:1011` calls
> `_xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters, args.estimator_seed)` — **identical
> arguments, same function, same process.** There is no argument difference for the deviation to come
> from, so `4.452e-14` is **genuine within-process nondeterminism**. The launcher's *"--null repeats
> CV at the identical seed and must be zero"* is **not mis-stated — it is VIOLATED.**
>
> **And the guard cannot fire.** `:1019`'s `tol = 1e-12 * max(‖base‖, 1.0)` clamps to an **absolute**
> `1e-12` against an absolute difference norm on a vector of order `1e-37`: **slack `2.25e38×`.** The
> check that exists to refuse a non-deterministic re-unfold **cannot fail on this object**, which is
> why a violated assertion reached production unremarked.
>
> **What P0 does NOT establish:** any cause. It establishes that the pair is like-for-like, the
> deviation is therefore real, and the guard cannot see it.

**IS P0 SELF-CONTAINED? YES.** It read preserved receipts and source only. **It does not depend on
`58524334` in any way** — that probe is *downstream* of P0, not an input to it, and P0 completed
before the probe was written.

**BUT THE NULL RULING IS NOT SELF-CONTAINED, AND MY TABLE DID NOT SHOW IT.** The dependency, drawn:

    NULL ruling
      |
      +-- route 1: a tolerance `epsilon`        -> CLOSED, all five candidate routes (packet 2.1)
      |
      +-- route 2: BITWISE IDENTITY
            |
            +-- is the deviation real?          -> P0.  SELF-CONTAINED. DONE: yes, and the guard is blind.
            |
            +-- is bitwise identity REACHABLE?  -> 58524334.  THE UNDISCLOSED EDGE.
                  |
                  +-- within one process, real bank, historical config -> MEASURED: NO.
                  |     r_null = 4.4311e-14 reproduces the historical 4.4520e-14 (ratio 0.9953);
                  |     first observed checkpoint divergence at call 0, 3.27e-16 relative.
                  +-- across allocations -> P2 would have tested this. See below.

**So: P0 is self-contained; the NULL *ruling* depends on `58524334` for route 2.** That edge is now
in the record.

**`58524334` HAS COMPLETED** — `ExitCode 0:0`, `2184 s`, `0.607` CPU task-h actual against a `2.00`
reservation.

**CONSEQUENCE FOR P2, following the ordering rule itself.** P2 tests determinism **across
allocations**. Non-identity is now measured **within a single process on the real bank**. Spending
`9.00`–`12.00` CPU task-h on the wider envelope while the narrower one already fails measures the
wrong thing, and a *"not identical"* result would be uninterpretable — **which is exactly the
reasoning P0 produced, and it still holds.** **Recommendation: P2 is not needed.** Not requested.

**WHAT THAT LEAVES.** Under the configuration space permitted here — pinning reserved — **bitwise
identity is unreachable without a material estimator change that is Joseph's.** That is the precise
statement, and it is the condition the order names for the exception becoming live. **Pinning is not
proposed as the remedy and §8 is not routed around.**

⚠ **Not established by any of the above:** a mechanism. `58524334` does not separate thread
scheduling from memory layout, library dispatch, or reduction order, and call 0 is the first
*observed* checkpoint rather than the first arithmetic difference.

## 5. THE PROPAGATION TEST — the defect was real, one layer further on

**The question:** does `publication-under-exception` propagate into the output metadata of the M1
projection, or only the source's?

1. **Into M1's own output: YES.** `project_cov_nd.py` writes `runClass`, `runClassStatus` and
   `acceptanceQuestion` as objects **inside the ROOT product**, so the token is in the file and
   survives a rename. Asserted by test.
2. **A DEFECT WAS FOUND AND FIXED.** `_source_metadata` returned `{}` for **every non-npz source**,
   so a projection *of* a projection lost everything: the `adoptable: false` guard did not fire, the
   receipt's `src_metadata` was empty, and a marker-carrying product could be re-declared at higher
   standing. It now reads the ROOT markers back, and a **standing rule** refuses any derived product
   that claims more standing than its source (`diagnostic 0 < UNDECLARED 1 < candidate 2 <
   publication-under-exception 3 < publication 4`). A marker-free ROOT file returns `{}` and is
   unconstrained, so no pre-existing caller breaks.
3. ⚠ **THE SPECIFIC CHAIN NAMED DOES NOT GO THROUGH THIS PROJECTOR, and the real gap was at the
   CONSUMER.** `project_cov_nd.py` requires a source on the 5D `AXIS_EDGES` grid with an
   `hXSecND_flat` CV; M1's output is a 42-cell object with `hCV_marginal`. So M1 → 2D/3D is not a
   path here. **The gap was in `rank6_significance.py`, which never read the covariance's class at
   all** — its `status` was the hardcoded string *"CANDIDATE — nothing here is approved"*, referring
   to **itself**, never to its input. A significance computed from an excepted covariance would have
   produced a receipt with **no trace of the exception**. That is *"a downstream consumer sees a
   clean covariance"*, located. **Closed:** the consumer now reads `runClass`, records
   `input_run_class` in its receipt, derives its `status` from it, and **refuses (`rc 8`)** to present
   an unqualified result from a non-`publication` input unless the caller acknowledges it
   explicitly — a criterion, liftable by declaration, not a prohibition. **An absent class counts as
   unacknowledged: absence of a claim is not a claim of adoptability.**

**74 tests across the three suites. Mutation-verified both halves:** restoring `_source_metadata`'s
blindness fails the read-back test; disabling the consumer's refusal fails two.
⚠ Adding `rc 8` broke **all 15** existing consumer tests at once — the guard-fires-on-every-correct-run
signature — but the guard is right and the fixtures were making an unqualified claim by omission.
**Defaulting the field to `publication` would have asserted adoptability by omission**, which is the
defect `rc 8` exists to stop. The fixtures now declare their class.

## 6. RELEASED

The `158.25` GPU / `262.00` CPU one-additional-member reservation is **released**. It was never
submitted, so nothing is cancelled; it is struck from the required path and will not be re-proposed
there.

## 7. STATE: **BLOCKED ON JOSEPH'S DECISIONS** — recorded here so the open set is not re-derived

Per the standing grant: *"If only my decisions remain, mark the goal blocked and stop the repeated
status loop."* **This is that marking.** §0's objective is **not met**: the trunk is **not adopted**,
so the required projections are not yet quoted from an adopted object and the documents are not yet
synchronized against one.

**What blocks it is not evidence, compute, or implementation.** No required measurement is missing
that I am authorized to take, `R5` headroom is `~403` CPU task-hours against a required path that
needs `~2`, and every consumer change is landed and tested. **The gate is ruling 9's `ADOPT`, which
is Joseph's act by reservation** — and the goal says so in its own words: *"Submission is my act."*

### 7.1 CLOSED, with receipts

| | outcome |
|---|---|
| `D-RESOURCE` | **this record**, `75ee2c45` — the objective no longer lives only in a packet |
| C1 | `58530433` — P leg **MET** (42 pair bands, no missing endpoint, flux exactly 100 contiguous); M leg **MEASURED**, incl. the sign-depends-on-band-size finding |
| C2 | margin **brought**: `shift/(k·floor) = 2.6739`, recommended margin `0.168`; boundary **withheld** |
| C5 · C6 · C7 · R5 | ruled in §3 and executed |
| §6.4 **P0** | **done at `1405caad`**, self-contained; and `58524334` measured its outcome |
| propagation test | defect found and fixed at `rank6_significance.py` |
| DOCS | green **with proof it did the work**; 26/26 sources byte-identical at `3c3e9f2` |

**RUNNING:** `58531919` (C4's jitter print) — `PENDING|Priority`, elapsed `0`. It is a **disclosure
print**, so it gates no ruling below.

### 7.2 ⚠ TWO RULINGS COMPOSE INTO A GAP — C3 cannot be evaluated, and ruling 2 is why

**Ruling 6 dispositions C1, C2, C4, C5, C6, C7. C3 is not in that list**, and its boundaries
(`cause3_agg`, `cause3_med`, `cause3_med_coverage`, `cause3_corr`) are **declared with provenance but
unevaluated**. That is not an omission I can repair by working harder:

> All three legs measure **movement across members**. `k=0` archived is the only member. **Ruling 2
> declined `k₁`, which was the only additional member on offer** — so there is no second point, and
> **the maximum over a one-element set of differences is not defined.**

**This is a consequence of Joseph's own ruling 2, not a defect in it** — ruling 2's ground was that
nothing required needs `N`, which remains true. But it means **C3's criterion is structurally
unevaluable on the required path as scoped.** The disposition is therefore a real choice, not a
measurement: *adopt with C3 declared-and-unevaluated, and say so in the note*, or *reopen exactly one
member*. **Recommendation: the former** — the criterion's value is that it is predeclared and binds
future members; a declared-unevaluated stability criterion disclosed as such is honest, whereas
buying one member to produce a single difference would license a stability claim one comparison
cannot support, which is the limitation I stated when the campaign was proposed.

### 7.3 ⚠ RULING 5'S COVERAGE CLAUSE DOES NOT LITERALLY REACH `s_proj`

Ruling 5 sets coverage *"100% on **bins** entering a quoted projection, ≥99% on the full reported
support"*. **`s_proj`'s population is not bins — it is the functionals of ruling 4** (the rows of
`M`, plus all-ones). So the clause is expressed over a different population than the leg ruling 3
added, and there is **no `cause3_corr_coverage` key** to carry it.

**Recommended reading: coverage `1.0` over the functional set** — every member of ruling 4's set
*is* a quoted projection, so ruling 5's **first** clause, not its `≥99%` fallback, is the applicable
one. **This is a reading of two approved rulings, not a quotation of either**, so it is recorded as a
recommendation and **no key is declared.**

### 7.4 OPEN — **all five are Joseph's**, each with exactly what it gates

| # | decision | gates | my recommendation |
|---|---|---|---|
| **1** | **§6.4 route.** P0 is done and **returned non-identity**: first divergence at **call 0** (`3.27e-16`), endpoint not identical, `r_null 4.4311e-14` vs historical `4.4520e-14` (ratio `0.9953`). Ruling 7's order asks for P2 next *if needed*, and the exception *only if bitwise identity is unreachable*. | **NULL → ADOPT** | **Bitwise identity is unreachable**: divergence at call 0 with threading excluded at its tested scope means no thread or ordering control reaches it. P2 would re-measure a reproduction I have already reproduced to `0.995`. **Release the held exception.** |
| **2** | **C3 declared-but-unevaluated** — may a trunk be adopted on it? | **ADOPT** | **Yes**, per §7.2, disclosed in the note. |
| **3** | **`s_proj`'s reporting class.** I recorded **`per-bin`**. | the receipt's shape | **`per-bin`** — it is a max over a finite enumerated set, and its failures must be enumerable, which the aggregate class cannot express. |
| **4** | **`cause2_f7_margin`** | C2's boolean counting as *performed* | **`0.168`**; measured `2.6739` clears it by `2.29×`. |
| **5** | **`s_proj` coverage** | the receipt's shape | **`1.0`** per §7.3. |

**Not open, and not to be re-litigated by any lane:** ruling 5's `δ = 5%` is **APPROVED**; ruling 2's
campaign is **DECLINED and RELEASED**; ruling 8's pinning is **RESERVED**.

### 7.5 WHAT FIRES THE MOMENT THOSE LAND — no further ask, no further diagnostic

1. **NULL** — record the §6.4 disposition per decision 1. No compute.
2. **ADOPT** — **Joseph's act, and it is now exactly one line.** See §8: the record must carry a
   declarative `ADOPTS-SHA256` line naming the measured digest of the covariance being projected.
   **The launcher emits that line for you:** run it once, it refuses, and its refusal prints
   `declare:  ADOPTS-SHA256: <measured>`. Copy that into the adoption record. The consumer route
   stays **digest-bound, not a flag** — the candidate keeps `adoptable:false` and its historical
   rejection stands.
3. **PROJ** — **one** `project_cov_nd.py --run-class publication` M1 run (`5D→(E_avail,W)`, 42 cells).
   `≈0.03` CPU task-h, pre-approved under §1, fresh admission first.
4. **DOCS** — re-verify note/primer/paper against the adopted trunk, with the marker guard.

**Then the objective is met except for submission, which is Joseph's act.**


## 8. THE ADOPTION GATE WAS SATISFIABLE BY DOCUMENTS THAT ADOPT NOTHING — measured and repaired

**Joseph named this failure and my first repair only fixed half of it.** His words were *"the
launcher's keyword search does not enforce digest identity"*; I added `rc 1b`, a `grep -F` for the
measured digest, and left `rc 1`'s `grep -qiE "adopt(ed|s|ion)"` in place. **The conjunction of two
loose searches over one file is still not a decision about that file**, for a structural reason: a
**receipt naturally contains the digest**, and any document **discussing** adoption naturally
contains the word.

**Measured against this repo, three documents passed BOTH checks** for the `z-cv` digest
`3d7465f6…`:

| document | what it is |
|---|---|
| `NAVIGATION-20260917-z-pilot-outcome-route.md` | a **pure routing document** |
| `PLAN-20260918-scalar5d-publication-completion.md` | a plan |
| `DECISION-PACKET-20260918-scalar5d-publication-blockers.md` | the packet, which **says of itself** *"A record that authorizes nothing in particular authorizes everything"* |

So `MNV_ADOPTION_RECORD=<the routing document>` would have been **accepted**, and the packet would
have satisfied the gate it describes.

**Requiring the word and the digest on ONE line is not sufficient either** —
`VERDICT-20260821-expiry-c-real-path-present-seed.md:57` already co-locates *"adopt segment"* with a
64-hex digest in running prose. **The record must therefore carry a declarative sentinel that prose
does not emit by accident**, with the digest on that line:

```
ADOPTS-SHA256: <64 hex of the covariance being projected>
```

**Zero documents in the repo match it today**, which is correct — nothing is adopted yet. A negated
or deferred sentinel (`nothing`, `not`, `pending`, `proposed`, `draft`, `held`, `withheld`, `never`)
is **refused**, because the repo's idiom for declining is literally *"adopts nothing"* and §6.4's
exception is held *"as drafted, not executed"*.

**Both directions are tested** (`tests/test_run_m1_projection_refusals.py`, 20 passing). The pair
that matters: one test asserts the **old** predicate *did* admit all three documents — so the repair
is demonstrably not decorative — and another asserts the **new** one refuses each. A third scans
`docs/**.md` for live declarations and **requires a real 64-hex on the sentinel line**, because
scanning for the bare prefix is the mistake I have made three times in this campaign: a substring
ban that trips on the documentation explaining it. Its companion proves the scan would still catch a
real declaration and correctly skips a `<placeholder>` template.

**This changes no scientific content and adopts nothing.** It is the engineering repair of the guard
Joseph pointed at, and it makes `ADOPT` a well-defined single act instead of an underdetermined one.

⚠ **One detail I did not resolve and am not guessing at:** which artifact is `SRC_COV`. The
navigation record digests `z-cv.npz`, `z-mean.npz` and `z-null.npz`; I have not established which
the projector consumes as the covariance. **It does not block the act** — the launcher measures
`sha256sum "$SRC_COV"` itself and prints the line to declare — but a lane must not transcribe a
digest from the navigation record on the assumption that it is the covariance.

## 9. DELEGATION OF THE REQUIRED ROWS, and the SPEC freeze — Joseph, 2026-09-18

**The reason he gave, in his own words:** *"You have been blocked on me for every criterion while
barred from grading your own legs, so waiting has been turning into audit rounds. That is my design
fault, not your discipline."*

> **DEFAULT-PROCEED on the twelve required rows.** *"Execute any row in the §2 table and report
> after; do not await my word on them."*
>
> **THREE ACTS STAY RESERVED, unchanged:** **ADOPT**, **any material change to the estimator**, and
> **anything outward-facing**. *"Everything else on that table is yours."*

**Set under this delegation, 2026-09-18** — each is a row of the §2 table and none is a reserved act:

| boundary / choice | value | why it was mine to set |
|---|---|---|
| `cause2_f7_margin` | **`0.168`** | a boundary, not an adoption |
| `cause3_corr_coverage` | **`1.0`** | ruling 5's coverage clause is written over **bins**; `s_proj`'s population is **functionals**, so the clause never reached the leg and it had no coverage number at all |
| `s_proj` reporting class | **`per-bin`** | a max over a finite enumerated set whose failures must be enumerable |
| C3's disposition | **declared-and-unevaluated, disclosed** | ruling 2 declined the only additional member, so the max over a one-element set of differences is undefined — a choice, not a measurement |

`null_epsilon` **remains the one withheld boundary.** The §6.4 route makes it moot for the required
path rather than resolving it, so it stays withheld rather than being quietly satisfied.

### 9.1 THE SPEC IS FROZEN AT REV. 22

> *"No rev. 23. Extract a one-page operative sheet … and treat the SPEC as historical. No new
> 'what changed in rev. N' sections, no packet superseding a packet. Results go to the ledger;
> corrections go inline where the error is. The revision narration has become a drift source and it
> is costing more than it protects."*

The operative sheet is [`OPERATIVE-SHEET-scalar5d.md`](OPERATIVE-SHEET-scalar5d.md). **It is an
extract, not a new authority** — every number in it is already declared in code or ruled above, and
where it and a canonical artifact disagree, the canonical artifact wins.

### 9.2 THE STOPPING RULE STANDS

> *"Name the blocked deliverable before any repair round."* Joseph's assessment of the round that
> produced it: *"this round's audit was correctly scoped and caught a wrong published uncertainty."*

And the correction he made to my framing, recorded because it was mine to get wrong: I wrote that
*"had you ruled on the five decisions first, we'd have burned a cycle discovering this."* **That
made his not-yet-ruling a benefit of my own audit, and it is not.** The gate was equally repairable
after the rulings; the rulings are what move the required path.

## 10. THE 18 SUITE FAILURES — do any touch projection, adoption or covariance?

**Asked and answered plainly: three of the eighteen touch that path — by INVENTORY, not by logic.
None is a defect in projection, adoption or covariance behaviour.** Not being fixed; this is the
gated post-publication cleanup and Joseph did not ask for a repair.

The eighteen are **identical** to a full baseline run at `bd77ad5f^` (set difference empty in both
directions; totals reconcile at `+11`, exactly the tests added). They fall into four groups:

| group | n | what they actually are |
|---|---|---|
| macOS `/var` vs `/private/var` | 3 | the symlink defeats a `resolve()` comparison; would pass on Linux |
| cluster-path absence | 1 | needs `/pscratch/.../omnifold/dataloader.py`; local-only |
| harness environment | 1 | `NameError: __file__ is not defined` in a mutation harness |
| **drifted inventory counters / snapshots** | **13** | counts needing `--update`, e.g. `347 != 374` shell files, `132 != 129` fields, `204 != 198` launchers |

**The three that touch this path, and how:**

1. **`test_p4_token_gate_scope_and_rev`** — `19 != 18`; the measured surface now includes
   `nd-unfolding/project_cov_nd.py`. **A count, not a behaviour.** It fails identically at baseline,
   so the drift predates today.
2. **`test_uq_remediation::SubstitutionFenceS1`** — `204 != 198` launchers, and the delta includes
   **`nd-unfolding/lib_r5_admission.sh`, which this campaign added.** So this one **is** downstream
   of our own work, though it predates today's commits. It needs a launcher classified as hooked,
   fenced, or out of scope — inventory, not logic.
3. **`test_hash_bindings::test_every_longform_finding_is_indexed`** — **21 `FINDING-*.md` documents
   are absent from the `FINDINGS.md` index and therefore invisible to a new session**, and three of
   them are squarely ours: `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`,
   `FINDING-20260901-cause4-jitter-floor-recovered.md`,
   `FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md`.

⚠ **Item 3 is the same failure mode Joseph named about `MEMORY.md`, one layer out:** the finding
exists, the index does not carry it, so a cold session re-derives it by auditing. **That is a live
cause of the circularity, not a stale counter** — recorded here so the cleanup knows which of the
thirteen is not merely cosmetic.
