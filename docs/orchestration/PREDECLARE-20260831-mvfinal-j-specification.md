# PREDECLARE 2026-08-31 — open `MVFINAL_j` specification rulings

**THIS SPECIFIES NOTHING AND IMPLEMENTS NOTHING.** It presents six open rulings for Joseph to sign
one at a time. An unsigned option is not a decision, and a signature on one ruling does not imply an
answer to any other ruling.

**THIS CHANGES NO GATE, ADOPTS NOTHING, DISCHARGES NOTHING, AND AUTHORIZES NO COMPUTE OR
DELETION.** Counts remain **CAND 1 of 7 / QUOTED 0 of 7**. Gate 2 remains **FAIL**. No
`MVFINAL_j` producer, reader, validator, ensemble builder, or deleter is created here.

## Why a specification ruling is needed before code

The staged plan records the current implementation boundary verbatim:

> **The 41.44 GB combined intermediate is NOT deleted** — §11g gates deletion on `MVFINAL_j`, and
> `MVFINAL_j` has **no producer, reader or deleter anywhere in the tree** (five occurrences across
> two files, all prose). So the protection is procedural. Nothing in this plan deletes anything.

— `docs/orchestration/PLAN-20260822-oneMember-mii-staged.md:68-71`. The five executable-tree
occurrences remain comments, a warning, a test docstring, and a test assertion; none produces, reads,
validates, or deletes an artifact.

Section 11g nevertheless makes that nonexistent object the condition for an irreversible act:

> **DELETION IS GATED, and the gate is §10c's invariant running the other way: NOTHING IS DELETED
> WITHOUT A POSITIVE DECLARATION EITHER.** No member's intermediate may be removed until that
> member's `MVFINAL_j` exists and validates. **Nothing accepted without a stamp; nothing deleted
> without one.** A failed member keeps its intermediate.

— `docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:661-664`.

Nothing here runs soon. The later order is recorded as:

> Gate 2 PASS → leg 6 on k=0 → one member verified end-to-end → family launch at the size above.
> Anyone reading this row as permission to submit today has read it wrong.

— `docs/orchestration/DECISION-20260830-joseph-mii-family-and-leg6.md:66-69`. The same decision says
Gate 2 is FAIL and is the binding constraint (`:47-55`). This document only makes the missing
specification questions visible before that order can reach `MVFINAL_j`.

## How to use the ruling blocks

For each ruling, Joseph may check exactly one listed option, write a replacement in **Other**, and
sign that ruling alone. Options deliberately say what becomes true; they are not findings. Any
unchecked ruling remains open.

## R1 — where do `v_u` and `v_b` live?

### The two sides

The determination requires both operands to ship:

> **So §14's winner mask is ALREADY A SHIPPED PRODUCT and B should not build it. What is genuinely
> missing is `vb`** — with which `g` recovers `vu` wherever `vu` won — **plus `vu` itself in the
> CENSORED region `g == 1`, where `g` says only `vu ≤ vb` and the distance to the kink is
> unrecoverable.**
>
> **That is exactly the "by how much" half §14 identified, and it is now the ONLY half.** Ship `vb`
> and `vu`; note in the receipt that `g` is the mask and is redundant with them wherever `g > 1`.

— `docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:2473-2478`.

The complete `ADOPTED_UTHROW` key table contains neither operand. Its key-bearing lines are quoted
below verbatim; comments are omitted but no entry is omitted:

```python
ADOPTED_UTHROW = {
    "hCov_combined5d_total_uthrow": PAYLOAD,
    "hInflation_g": PAYLOAD,
    "sqrt_tr_old": PAYLOAD, "sqrt_tr_new": PAYLOAD,
    "upstream_fixed_seed_null_norm": PAYLOAD,
    "upstream_joint_mean_shift_norm": PAYLOAD,
    "upstream_n_throws": CONFIGURATION,
    "fixed_seed_null_norm_checked": CONFIGURATION,
    "joint_mean_shift_norm_checked": CONFIGURATION,
    "n_throws_checked": CONFIGURATION,
    "centering_convention": CONFIGURATION,
    "uthrow_source": CONFIGURATION, "combined_source": CONFIGURATION,
    "est_seed_offset": PROVENANCE, "est_seed_offset_declared": PROVENANCE,
    "upstream_estimator_seed_g1": PROVENANCE, "upstream_estimator_seed_g2": PROVENANCE,
    "upstream_estimator_seed_g1_checked": CONFIGURATION,
    "upstream_estimator_seed_g2_checked": CONFIGURATION,
    "hDiagCombinedOld": PAYLOAD,
    "hDiagCombinedOldRaw": PAYLOAD,
}
```

— `nd-unfolding/mii_root_payload_classes.py:204-260`. A direct name search over those lines finds no
`v_u`, `v_b`, `vu`, or `vb` key.

### What turns on the answer

The ruling chooses whether the operands are ingredients of the member receipt, payload keys carried
by each adopted ROOT, or both. That determines which artifact is independently sufficient, which
reader/verifier owns the invariant, and whether an existing digest binding must be superseded.

### The price, stated plainly

- **Receipt-only can be implemented without changing any currently digest-pinned file.** A new
  `MVFINAL_j` producer can read the closed inputs selected later and place the two arrays in the
  receipt. No such producer exists today, so its new source and tests have no pre-existing digest pin.
- **Editing `nd-unfolding/adopt_unified_5d.py` to write the ROOT keys does incur a supersession
  chain.** The active BEN-106 receipt names that implementation and binds SHA-256
  `e1260e8d…` (`docs/orchestration/state/ben106-stamp-verify-active-56695424.json:17-22`), and
  `assert_pinned_writer_is_intact` refuses changed bytes and says to re-issue or retire the owning
  receipt (`nd-unfolding/mii_adopt_unified_5d_stamped.py:218-245`). The live file still hashes to the
  bound digest.
- **The binary price claim has a third route and therefore does not hold without a qualification.**
  `mii_adopt_unified_5d_stamped.py` already runs the pinned writer unchanged, reopens its output
  `UPDATE`, and writes additional ROOT keys (`:717-762`, called at `:767-811`).

  > **CORRECTED 2026-08-31, and the original undercount is left above rather than rewritten.** This
  > bullet first said the wrapper's SHA-256 `e5bc51a4…` "occurs in two later grading reports", and the
  > orchestrator's summary of it went further and said **zero** sha256-adjacent references. Both are
  > wrong. The count was produced by a grep scoped to `*.json` under `nd-unfolding/` and
  > `docs/orchestration/state/` and then reported as though unscoped. **Measured over `*.md` and
  > `*.json` across `docs/` and `nd-unfolding/`, the digest is recorded in FOUR records:**
  > `GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md` (an identity table listing it beside
  > `adopt_unified_5d.py`'s `e1260e8d…`), `RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md:336` (named
  > as a `CHILD_GUARD` tree binding), and the two `20260826-stackgrade` verdicts.
  > `VERDICT-20260821-clausec-rerun-production-dimension.md` additionally tracks the wrapper across two
  > EARLIER digests. Found by the `claude-school` k=0 lane; re-measured here before this correction.
  >
  > **THE DISTINCTION THAT ACTUALLY DECIDES R1-C IS ENFORCED PIN versus RECORDED OBSERVATION, and the
  > conclusion survives.** None of those four is executable. `PINNED_WRITER` is bound to
  > `adopt_unified_5d.py` alone (`nd-unfolding/mii_adopt_unified_5d_stamped.py:152`), and
  > `assert_pinned_writer_is_intact` (`:218`, called at `:767`) reads that digest FROM THE RECEIPT
  > rather than from a literal — its docstring says a literal "would be a second binding that can
  > drift from the first". **No code compares the wrapper's own bytes**, so editing it refuses nothing
  > at run time and triggers no supersession chain. What it does cost is **four verdict and receipt
  > records that would become stale descriptions of a moved file**, which is a documentation debt to
  > schedule, not a gate to clear. R1-C's price is therefore NOT "zero references" — it is **no
  > enforced pin cost, plus four records to re-issue or annotate.**

  A 2026-08-31 run of `python3 docs/orchestration/verify_hash_bindings.py` exits 0, and a search of the
  verifier's JSON/shell inputs finds no current-wrapper binding. This is consistent with the
  repository's own path inventory saying only `adopt_unified_5d.py` is pinned among this path's files
  (`docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md:88-102`). Extending that
  wrapper is therefore a ROOT-schema option that does **not** edit a currently digest-pinned file,
  although it still changes the adopted-artifact contract and needs its own tests and read-back
  evidence.

### Options for Joseph

- [ ] **R1-A — receipt only.** `MVFINAL_j` carries `v_u` and `v_b`; adopted ROOT keys do not change.
- [ ] **R1-B — canonical writer ROOT keys.** The adopted ROOT carries both arrays; authorize the
      `adopt_unified_5d.py` supersession chain explicitly.
- [ ] **R1-C — wrapper-added ROOT keys.** Keep the pinned writer byte-identical; extend the post-write
      wrapper and adopted-payload table to carry and verify both arrays.
- [ ] **R1-D — both receipt and ROOT.** Accept duplication and require the verifier to prove equality.
- [ ] **Other:** _________________________________________________________________

**Drafting-lane view:** no option is recommended. The evidence establishes the cost difference and
the wrapper route, but it does not decide whether portability of the adopted ROOT outweighs duplicate
schema and verification ownership.

**Joseph signature for R1:** ____________________  **Date:** ____________________

## R2 — which dimension governs the deletion rationale?

### The two sides

Section 11g reasons from a full-grid-sized matrix:

> The 41 GB is a handful of `65856²` `TH2D`s — **one such matrix is `34.7 GB` on its own** — derived
> from 188 universe files totalling **`26.9 MB`**. **Retaining the inputs and discarding the
> intermediate is a ~1,500× compression of the reproducibility requirement**, and rebuilding it is
> the analyzer's CPU time, not a GPU member.

— `docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:655-659`.

The implemented payload contract distinguishes the full grid from reported support:

```python
#: THE GRID, WHICH IS *NOT* THE SIZE OF ANY ARTIFACT. 65,856 is the full 5D (pt,pz,Eavail,q3,W) grid.
#: Every matrix and per-bin array in these products is on the REPORTED SUPPORT -- the `cv > 0` mask,
#: measured by lane D against the real archive at 10,694, and 10694/65856 = 16.24%.
#:     "34.7 GB matrix"         -> 10694^2 x 8 B = 0.915 GB     (I was 37.9x over)
```

— verbatim from comments at `nd-unfolding/mii_root_payload_classes.py:128-138`; the constants are
`FLAT_NBINS = 65856` and `REPORTED_NBINS = 10694` at `:142-144`. The matrix-size premise is high by
about **38×**.

### What turns on the answer

The measured combined intermediate can still be 41.44 GB because it contains multiple objects; the
0.915 GB correction is to the size of each covariance, not a fresh inventory of the whole ROOT file.
The correction therefore destroys 11g's quoted single-matrix and ~1,500× arithmetic, but does not by
itself prove either that the measured 41.44 GB total should be retained or that it should be deleted.
Joseph's ruling determines whether deletion remains an authorized design goal and what evidence must
replace the invalid storage rationale.

### Options for Joseph

- [ ] **R2-A — keep the deletion gate, replace its rationale.** Use 10,694² for covariance sizing and
      require a measured per-key inventory plus rebuild-cost statement before enabling deletion.
- [ ] **R2-B — suspend deletion design.** Retain every member intermediate until a corrected storage
      and reproducibility analysis is signed.
- [ ] **R2-C — retain intermediates permanently.** `MVFINAL_j` may validate admission, but never
      authorizes deletion.
- [ ] **Other:** _________________________________________________________________

**Drafting-lane view:** no retention option follows from the dimension correction alone. The old
34.7 GB-per-matrix and ~1,500× rationale must not be reused under any option.

**Joseph signature for R2:** ____________________  **Date:** ____________________

## R3 — which member namespace governs?

### The two sides

The historical specification says:

> **Each member gets one immutable root keyed by BOTH member and offset** —
> `mii/member_00_k_00000/`, `member_01_k_01200/`. Every producer, log, combine, receipt and
> done-marker stays below it.

— `evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/SPEC-20260818-mii-submission-topology.md:20-24`.

The later determination says:

> ## 5. RULED — the member directory is **OFFSET-KEYED**, `member_k001200/`. **B's form, and my
> `member_00/` is withdrawn**

and then:

> **The spec's `member_00_k_00000/` — carrying BOTH — is refused as the worst of the three:** it
> embeds two fields that can contradict *in the name itself*, so a mismatch becomes a thing a reader
> must adjudicate rather than a thing that cannot happen. **The plan records `index ↔ offset ↔
> directory`; that is where the index belongs.**

— `docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:173-184,195-197`.

### What turns on the answer

Every receipt path, closed input path, ensemble member reference, resume rule, and deletion target
needs one namespace invariant. “Later” is not itself a durable supersession relation. The ruling must
say both which path governs and whether the historical specification is superseded or merely an older
record that still needs an explicit conflict annotation.

### Options for Joseph

- [ ] **R3-A — later determination governs and supersedes the historical namespace clause.** Only
      `mii/member_kNNNNNN/` is valid; annotate the historical specification as superseded on this point.
- [ ] **R3-B — later determination governs but the historical specification remains unmodified
      history.** Add a routed correction outside the frozen evidence artifact.
- [ ] **R3-C — both remain governing.** Treat the namespace as unresolved and block implementation
      until a replacement topology is signed.
- [ ] **Other:** _________________________________________________________________

**Drafting-lane view — recommendation, not finding:** choose R3-A. The later source explicitly says
“RULED,” “withdrawn,” and “refused”; the remaining uncertainty is documentary supersession, not the
strength of its language.

**Joseph signature for R3:** ____________________  **Date:** ____________________

## R4 — what does the ensemble receipt require at 46 members?

### The two sides

The `MVFINAL_j` determination requires an exact cardinality:

> **RULED: 50 member receipts, each digest-bound over its member's products; ONE ensemble receipt
> that binds all 50 by digest and carries the predeclared spread metrics.** **The ensemble receipt is
> the citable artifact; the member receipts are its INGREDIENTS.**

— `docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:2422-2424`.

The later family decision records a conditional reconciliation:

> **This lane's reconciliation, which Joseph has NOT separately confirmed and which any lane may
> challenge:** the family is authorized at **50 members conditional on archiving to HPSS as members
> complete**, with **46 as the floor** if archiving is not in place when the family is launched. The
> reading is that (3) was the fuller intent and (2) was its fallback, not that both hold at once.
> **If that reading is wrong, this row is the defect and Joseph's correction governs.**

— `docs/orchestration/DECISION-20260830-joseph-mii-family-and-leg6.md:25-36`.

### What turns on the answer

The ruling fixes ensemble completeness, the schema's member-count fields, whether a 46-member object
can be citable at all, and whether later arrival of members 47–50 revises one receipt or creates a
second receipt. Without it, a verifier cannot distinguish a complete 46-member fallback from an
incomplete 50-member family.

### Options for Joseph

- [ ] **R4-A — exactly 50.** At 46, member receipts may exist but no complete or citable ensemble
      receipt exists.
- [ ] **R4-B — authorized actual size, 46 through 50.** The ensemble receipt carries `target_n = 50`,
      `floor_n = 46`, `actual_n`, and the condition selecting the actual size; 46 can be complete.
- [ ] **R4-C — two immutable ensemble receipts.** A complete 46-member fallback may be issued; a later
      50-member ensemble is a distinct successor and never overwrites the first.
- [ ] **R4-D — no 46-member interpretation until separately confirmed.** Treat the unconfirmed
      reconciliation as non-operative for receipt design.
- [ ] **Other:** _________________________________________________________________

**Drafting-lane view:** no option is recommended because the only source for 46 as a floor labels its
own reconciliation unconfirmed.

**Joseph signature for R4:** ____________________  **Date:** ____________________

## R5 — does Gate 2 precede leg 6 and `MVFINAL_j`?

### The two sides

The publication-readiness DAG places leg 6 and `MVFINAL_j` first:

> `[F] leg 6 (fin5dBKG) -> MVFINAL_j  the two adopted roots; MVFINAL_j has no implementation today`
>
> `      |`
>
> `      v`
>
> `[G] GATE 2                         post-rehearsal (b) halves + F-1(b) manifest digest at both ends`

— `docs/orchestration/PUBLICATION-READINESS-20260822.md:236-243`.

The later decision reverses that edge:

> **Gate 2 is FAIL.** The review contract holds that until it passes, the rehearsal's products stay
> *"not adopted, not consumed by anything outside the seven rehearsal jobs, not quoted, and no
> further member is authorized."* Leg 6 would be an eighth job consuming those products. **The gate,
> not the family authorization, is the binding constraint, and no authorization from Joseph removes
> it** — only the rehearsal work landing does.

and:

> Gate 2 PASS → leg 6 on k=0 → one member verified end-to-end → family launch at the size above.

— `docs/orchestration/DECISION-20260830-joseph-mii-family-and-leg6.md:47-55,66-69`.

### What turns on the answer

The answer controls the executable DAG and whether any future operator can treat the readiness chart
as permission to run leg 6 while Gate 2 is FAIL. It also determines whether the older chart needs a
stale/superseded annotation or remains a separate publication condition that must be reconciled.

### Options for Joseph

- [ ] **R5-A — the 2026-08-30 order governs; the readiness DAG is stale.** Annotate or replace the old
      `[F] → [G]` edge with Gate 2 PASS → leg 6 → verified member → family.
- [ ] **R5-B — the two documents govern different gates.** No execution may occur until a new document
      explicitly reconciles both orders.
- [ ] **R5-C — the readiness DAG governs.** Amend or supersede the 2026-08-30 decision before any run.
- [ ] **Other:** _________________________________________________________________

**Drafting-lane view — recommendation, not ruling:** choose R5-A. The later decision calls Gate 2 the
binding constraint and gives an explicit order; no evidence found that the readiness DAG defines a
separate exception.

**Joseph signature for R5:** ____________________  **Date:** ____________________

## R6 — is the retained-array sizing enumeration superseded?

### The two sides

The enumeration says:

> Costing, confirmed both ways: `diag_comb + vb + vu` = 3 × 65,856 doubles = **1.58 MB**, 0.035 % of a
> retained member, a **26,219 : 1** trade against 41.44 GB.

— `docs/orchestration/ENUMERATION-20260818-mii-root-payload-three-classes.md:431-432`.

The determination corrects it:

> ```
> diag_comb + R4's vb + vu  =  3 x 10,694 doubles  =  256,656 B  =  250.6 KiB
> against the 4.46 GB retained member : 0.00575 %
> against the 41.44 GB released       : 161,461 : 1
>
>   [CORRECTED 2026-08-18: first written as 3 x 65,856 = 1.58 MB, which is 6.16x too big.
>    `adopt_unified_5d.py:110,120-121` settles it: n = vu.size and `assert x.size == n` where
>    x = xfull[xfull > 0], so every one of these arrays is on the REPORTED-BIN set, not the grid.]
> ```

— `docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:688-700`.
The executable size table agrees: `hInflation_g`, `hDiagCombinedOld`, and
`hDiagCombinedOldRaw` each have `REPORTED_NBINS = 10694`
(`nd-unfolding/mii_root_payload_classes.py:142-175`).

### What turns on the answer

The choice determines which document future implementers may size arrays from, whether the
enumeration receives an explicit supersession annotation, and whether receipt validation asserts
10,694 elements or waits for a fresh read from each input. It does not decide R1's storage location.

### Options for Joseph

- [ ] **R6-A — superseded in fact and annotate it in text.** The 65,856 sizing sentence is explicitly
      retired; 10,694 governs the current schema.
- [ ] **R6-B — preserve the enumeration unchanged as history, but route every implementation to the
      correction.** The 10,694 contract still governs.
- [ ] **R6-C — require run-time derivation only.** Do not put either dimension in the receipt schema;
      derive it from the selected ROOT objects and assert cross-object equality.
- [ ] **Other:** _________________________________________________________________

**Drafting-lane view — recommendation, not ruling:** choose R6-A, while still deriving and checking
the dimension at run time. Two later sources independently carry 10,694 and the enumeration still
presents 65,856 as “confirmed both ways.”

**Joseph signature for R6:** ____________________  **Date:** ____________________

## Schema gaps outside R1–R6

None of the six rulings completes the artifact contract. The following six gaps must be closed before
code exists.

| # | Open schema gap | What must become explicit | Owner after R1–R6 |
|---|---|---|---|
| S1 | Member-receipt filename, path, format, schema, and field list | One canonical basename and namespace; serialization; schema version; required, optional, and forbidden fields; units and array encoding; canonicalization for digesting | **Drafting task.** Draft after R1, R3, and R6; Joseph need not choose spellings unless the draft exposes a substantive fork. |
| S2 | Exact closed input-file set | An enumerated, no-glob list of every member product and upstream ingredient bound by path, identity, and content digest; whether both adopted roots are required; what absence or an extra file means | **Joseph ruling.** This defines what “complete member” means and what can survive deletion; a drafter must not infer it from current directory contents. |
| S3 | ROOT key names for `v_u` and `v_b` | Exact case-sensitive names, ROOT classes, lengths, titles/semantics, centering convention, and equality relation to `hInflation_g` | **Drafting task.** Draft only if R1 selects a ROOT-bearing option; otherwise record the keys as deliberately absent. |
| S4 | Executable definition of “validates” | The exact command, accepted arguments, zero-success/nonzero-refusal exit contract, checks performed, emitted receipt/result, and behavior on missing, extra, stale, mismatched, recovered, or non-finite content | **Joseph ruling on acceptance semantics; drafting task on command spelling.** Section 11g currently gates irreversible deletion on a predicate with no executable definition. |
| S5 | Deleter and atomicity | Exact target allow-list; archive exclusion; same-member proof; TOCTOU handling; whether validation and deletion share one process/lock; interruption behavior; idempotence; audit record; recovery/retention policy | **Separate Joseph ruling and reviewed implementation step.** Receipt production must not silently enable deletion. Atomicity details can be drafted, but activation is not a drafting choice. |
| S6 | Ensemble-receipt filename, format, schema, and field list | Canonical location; schema version; ordered member-digest set; actual/target/floor cardinalities as R4 permits; spread metrics and their ingredients; successor semantics; citable verifier entry point | **Drafting task.** Draft after R4 fixes cardinality and mutability. |

Classification: **six gaps total**. S2, S4's acceptance semantics, and S5's deletion activation require
Joseph rulings; S1, S3, and S6 are drafting tasks after their prerequisite rulings. S4's command name
and S5's implementation mechanics are subsequent drafting work, not permission to choose the
predicate or enable deletion.

## Costed implementation boundary — estimate only

**Delegate design estimate, not a measurement:** about **7 files** and **600–900 gross lines of code**
for a member-receipt producer and validator, ensemble receipt and verifier support, integration, tests,
and documentation. Writing and unit-testing that code needs **no cluster time**. This estimate does not
authorize the work and does not estimate a later production smoke test.

**Delegate design judgment, not a ruling:** landing the receipt producer must not enable irreversible
deletion. The deleter, its atomicity contract, and the switch that makes a successful validation
deletable should land only as a **separate reviewed step** after the receipt path has independent test
evidence. That separation keeps a new declaration capability from acquiring a destructive side effect
in the same review.

## Signature summary

| Ruling | Signed option | Joseph initials | Date |
|---|---|---|---|
| R1 — `v_u` / `v_b` location |  |  |  |
| R2 — dimensions and deletion rationale |  |  |  |
| R3 — namespace precedence |  |  |  |
| R4 — 46/50 ensemble cardinality |  |  |  |
| R5 — Gate 2 / leg 6 order |  |  |  |
| R6 — retained-array sizing supersession |  |  |  |

Until a row is signed, it remains open. A signed row authorizes only the specification choice written
in that row; it does not implement code, launch compute, move Gate 2, adopt a covariance, discharge a
criterion, or authorize deletion.
