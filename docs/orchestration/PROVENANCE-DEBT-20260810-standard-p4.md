# Provenance debt: what the standard-P4 chain does NOT establish (2026-08-10)

**Status of this document.** A deliverable, not a footnote. It exists because the covariance product
is being validated under a **reduced standard** — as a fixed object, by direct audit — rather than
by a passing provenance pipeline. That is a deliberate change of approach, and the price of it is
that the gap has to be written down completely and in advance. **Declared debt is defensible; debt
discovered later is not.**

**Nothing here authorizes adoption.** The candidate carries `publication_gate_rejects_this: true`
throughout and `p4_adopt_standard.py` refuses it.

---

## 1. Why the standard was reduced

Five `standard-p4-verifier` passes on the provenance pipeline returned outstanding-defect counts of
**6 → 4 → 6 → 9 → 14**. In the last round, **three of six new defects were in guards written during
that same round to close other defects**. The audit target was code under active development, so the
surface grew every round and the process could not converge — it was generating work faster than it
consumed it.

The decision (Joseph, 2026-08-10) is to stop auditing the *pipeline* and audit the *product*:

> *Given this covariance and these ten endpoint ROOTs, is the covariance correct?*

That question is bounded, is about a fixed object, and is answerable. The pipeline question is
neither bounded nor converging. **The trade is explicit: we gain a decidable audit and we give up
the claim that the machinery which produced the object is itself verified.** This document is that
give-up, itemised.

## 2. What the product audit DOES establish

Properties checkable on the covariance and the ten endpoint ROOTs as they stand, independent of how
they were made:

- symmetry, positive semi-definiteness, eigenvalue diagnostics;
- exact block reconstruction — the total equals the sum of its recorded components;
- mask and bin-ordering consistency against the frozen central products;
- marginal identities (5D → 4D) and projection validity as recomputation identities;
- agreement of derived quantities with the same quantities computed by an independent route;
- endpoint content reproduction against the 2026-07-18 reference at a declared tolerance
  (per-bin 1e-9, integral 1e-11), 10/10, worst 1.83e-11 / 2.87e-12.

## 3. What it does NOT establish — the debt

### 3a. Open verifier defects, carried deliberately

From the repair-7 verdict (`20260810T012645Z-repair7-verdict.json`, BLOCK, 14 outstanding). Two
were fixed; the rest are debt.

| # | status | what remains unestablished |
|---|---|---|
| 1 | PARTIAL | Endpoint evidence: content comparison is real and discriminating, but verifier-crosscheck blockers are applied *after* consumable evidence is written, so a consumer can read evidence that a later check would have rejected. |
| **2** | **OPEN, deferred** | **Resume provenance binds only the unfold driver's blob.** Changes to `omnifold.py` or `xsec_nd.py` do not invalidate a resume, so a skipped endpoint may have been produced by different code than the manifest implies. |
| 3 | CLOSED | — |
| 4 | PARTIAL | The verifier's declared `review_scope` is trusted verbatim, and the fallback import graph omits executed shell dependencies. A narrow scope is not detected. |
| **5** | **OPEN, deferred** | **The token gate accepts symbolic revisions** (e.g. `HEAD`) and does not compare reviewed files against their working-tree bytes — only against the committed blob. |
| **6** | **OPEN, deferred** | **`C_syst` recomputation trusts the manifest's `candidate_keys`** and never verifies exact band-set equality or component identity. A manifest that omits a band yields a total that reconstructs perfectly from the bands it admits to. |
| **7** | **OPEN, deferred** | **The mutation harness is incomplete** — it retains detached/textual guards and lacks live positive and negative mutants. |
| 8 | PARTIAL | Sweep corpora omit `p4_check_verifier_token.py`; snapshots are count-and-name only. No CI exists to enforce regeneration (see §3d). |
| 9 | PARTIAL | The co-located P4 status file remains false, and no committed machine-readable products summary exists for job 56495756. |

Plus four unfixed new defects from the same verdict:

- the report-only cross-check emits NaN summaries on non-finite input beside zero threshold counts;
- a **projected** artifact does not inherit the self-declaring rejection marker — the projection
  manifest does not propagate it (the ROOT and its component manifest do carry it);
- `check_projection_validity`'s second leg is named "direct block sum" but recomputes by the same
  route (`M@C` then `@Mᵀ`) and shares `M`. **Verified independently: it is not a gate that cannot
  fire** — injecting a 50 %-wrong `project()` is caught at rel 3.3e-01 — so it catches an error in
  `project()` but not an error in `M` or a conceptual error about the projection. The *name*
  overclaims; the check is narrower than it sounds. Pattern B, not Pattern C.
- `TmpdirGuardItself` does not detect helper-mediated `TemporaryDirectory` use.

### 3b. The two things fixed, and precisely what they buy

- **Reachable 4D support.** Stage 6 can now execute. The projected product is defined on the 4825
  reported 4D bins the 5D support reaches; 5 bins (0.0000 % of the 4D total) are excluded and are
  recorded by global index in the projection manifest. **This does not establish that 4825 is the
  right support** — it establishes that the support is derived, recorded, and no longer silently
  asserted.
- **Manifest–receipt binding.** The non-adoptable marker can no longer be removed by handing the
  adopter an edited manifest. **This does not establish that the adopter is otherwise sound**; it
  closes one bypass of one safety property.

### 3c. Structural limits the audit cannot reach

- **The endpoints are not bit-reproducible** (KNOWN_ISSUES #24). Every provenance statement about
  them is a content statement at a tolerance, never an identity. A re-run that agrees to 1.8e-11 is
  the strongest available claim.
- **The integral leg of that tolerance is a discriminator with ~103× total dynamic range**, already
  sitting at 54.6 % of its coherent ceiling. It cannot be widened again without ceasing to
  discriminate. Breach response is pre-specified at `p4_lib.REPRO_RTOL_INTEGRAL`.
- **`hasTruthOnlyMisses` is misnamed at the writer** — a per-playlist flag summed by `hadd`. The
  reader is correct; the artifact is misleading to anyone who has not read the finding.
- **J36 is nine sites, not one**, and unrepaired. Its shape effect on the 2D analysis is **measured
  and bounded at ≤ 0.15 %** (VALIDATION_LEDGER 2026-08-09), so no 2D shape statement is at risk —
  but the defect is bounded, not corrected, and the bound is pre-unfolding, MC-signal-reco, and
  covers pT and p∥ only.
- **The 5D→4D marginal and the independent 4D unfold differ by a median 4.4 %** in shape (integrals
  agree to 0.56 %), with four candidate mechanisms excluded and none established. This is reported
  as an unexplained estimator dependence, not attributed.

### 3c-bis. The product auditor cannot touch the product

Recorded here because it is a limit on the *new* approach, discovered while setting it up, and it
would be dishonest to describe the product audit without it.

The covariance is **42.3 GB on NERSC scratch**. The `standard-p4-verifier` delegate runs in a
read-only sandbox on a laptop and has no access to that filesystem. So the audit cannot be
"delegate opens the product and checks it". The workable arrangement is:

1. the delegate **authors** the audit script, without my input on what it should compute;
2. I **execute it verbatim** on the cluster and capture the raw output;
3. the delegate **judges** the output.

**What this preserves:** the specification of the audit and the interpretation of its results are
independent of the implementing agent. That is the part that matters most, and it is the part the
pipeline audits were failing to protect.

**What this does NOT preserve:** I am in the execution path. A mis-run, a silently truncated output,
or a substituted input would not be visible to the delegate except through the output it is handed.
Mitigations, all partial: the script is authored by the delegate so I cannot shape what it looks
for; the delegate is instructed to require enough raw material in the output to detect an
inconsistent run (per `CONVENTION-receipt-ingredients.md`, a verdict-only output is unfalsifiable);
and the script and its stdout are both committed, so the pairing is auditable after the fact by
anyone who can reach the cluster.

**Residual risk, stated plainly: the product audit is independent in specification and judgement,
and NOT independent in execution.** Closing that would need either a delegate with cluster access
or a product small enough to transfer, and neither is available today.

### 3d. Enforcement debt

There is **no CI in this repository** — no `.github/workflows`, no `.gitlab-ci.yml`, no pre-commit,
no Makefile target (verified 2026-08-09 by `git ls-files`). Every guard described here binds an
author who runs `pytest`. **None binds a commit.** That is the single largest structural gap, and it
is why "the suite is green" is a statement about a machine and not about the repository.

## 4. The reduced standard, stated for the record

The covariance product is offered as: **an object whose internal consistency, mask/order
consistency, reconstruction identities and reproduction-against-reference have been checked
directly, produced by a pipeline whose provenance guarantees are incompletely verified and whose
open defects are enumerated in §3a.**

It is *not* offered as: a product of a verified chain.

Anyone quoting a number derived from it should cite this document alongside it. If that is not an
acceptable standard for publication, the correct response is to close §3a's open items — not to
restate the product's status more favourably.

## 5. Provenance of this document

Every claim above is either a direct quotation from a committed verifier verdict, a committed ledger
entry, or a measurement recorded in a committed finding. Per
`docs/orchestration/CONVENTION-receipt-ingredients.md`, the numbers here ship with their sources:

| claim | source |
|---|---|
| defect counts 6/4/6/9/14 | the five verdicts under `runs/standard-p4-verifier/` |
| 10/10 reproduction, 1.83e-11 / 2.87e-12 | `VALIDATION_LEDGER.md` 2026-08-09, evidence job 56532439 |
| integral leg 103.4× range, 54.6 % of ceiling | `p4_lib.py` `REPRO_RTOL_INTEGRAL` derivation |
| J36 ≤ 0.15 % shape | `VALIDATION_LEDGER.md` 2026-08-09, 12 per-playlist event-loop outputs |
| 4.4 % median estimator dependence | `FINDING-20260809-stage6-central-gate-cannot-pass.md` |
| 5 unreachable 4D bins, 0.0000 % | this round's projection manifest |
| no CI | `git ls-files`, 2026-08-09 |
