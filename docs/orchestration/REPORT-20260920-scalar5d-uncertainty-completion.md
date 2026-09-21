# REPORT 2026-09-20 — scalar-5D uncertainty deliverables: the completion report §7 requires

**CITABLE FOR:** what was delivered, the identities and receipts it rests on, both repository heads,
and the limitations that remain live.
**NOT CITABLE FOR:** publication readiness, any grade, or any claim that a limitation below has been
resolved. **This reports; it decides nothing.**

Required by [`DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`](DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md)
§7, which asks for *"the adopted source identity, projection receipts, build results, both
repository heads, and remaining disclosed limitations"* — and which forbids declaring completion
before the required deliverables are complete.

---

## 1. ⚠ WHAT IS AND IS NOT BEING DECLARED

**DECLARED COMPLETE: the required scalar-5D uncertainty deliverables** — an adopted covariance, its
verified projection with a paired central value, and synchronized note/primer/paper, all landed in
commits on both remotes.

**NOT DECLARED, and neither follows from the above:**

- **Not publication readiness.** The third lane says so of its own work — *"I do not certify
  publication readiness"* — and §1's completion is about the deliverable set, not about the physics
  being beyond question.
- **Not that the disclosed limitations are resolved.** §5 lists seven. Joseph's §7: *"Do not equate
  disclosure with measurement, or PM-1 acceptance with blanket validation."*
- **Not a significance.** The generator significance stays optional and outside this path, and the
  reason is measured: `s_proj = 6.145%` against a `5%` bound.
- **Not submission.** Reserved.

## 2. The adopted source, by identity

| | |
|---|---|
| path | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz` |
| `sha256` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` |
| bytes | `890,500,272` |
| variant | **`cv`**, read from the product's own metadata, enforced by `--expect-variant` (required, no default) |
| assembling revision | `fb9ec3560fd6d62295dffc81b5694c9e26667d5b` |
| producing job | `58454524`, `ExitCode 2:0` — this CLI's completion code for *construction ran, science NON-PASSING* |
| adopted | Joseph, 2026-09-20, **publication-under-exception**, under the executed byte-scoped §6.4 amendment |

**Hashed three times by three parties:** at construction; on the cluster immediately before the
adoption record was written; and by an independent third lane on 2026-09-20 that also repeated the
dense eigensolve. **The product's own fields are unchanged and stay so** — `NON-PASSING`,
`adoptable: false`. The exception is a decision about the bytes, not an edit to them, and it covers
**these bytes and nothing else**.

## 3. Projection receipts

| | |
|---|---|
| product | `/pscratch/sd/j/josephrb/z2m-products/PROJ/cov_5d_to_eavailW_publication.root` |
| `sha256` | `835828bf3e25bbd9f279088e5cc89b8b325d727446fec9fabbbc92fd7e71a54e`, `17,101` bytes |
| run class | `publication-under-exception`; job `58655509`, `COMPLETED 0:0`, 39 s |
| map | `5D (pt,pz,eavail,q3,W) → (E_avail,W)`, `M_shape [42, 10694]`, `M_content_sha256 64fec490…` |
| receipts | `state/PROJ-20260920-m1-publication-receipt.json`, `state/PROJ-20260920-binding-check.json` |

**Predeclared checks, declared before the run:** `src_cells_dropped = 0`; `max|C − Cᵀ| = 0.00e+00`;
PSD `min-eig 4.359e-92`, most-negative/max `2.93e-15`; `hRowIndex` readback `9eb9d216…`, 42 labels.
`rel` does not exist in this mode and nothing is reported for it.
⚠ **`n_empty` is not a declared check and nothing may cite it as one** — it is zero by construction
in `receiving-cells` mode.

**The pairing, which is the part that could have failed silently:** the **binding** leg is **digest
identity** — the projected source's `hXSecND_flat` and the note figure's are **byte-identical**,
`0f04abce…`. Numerical agreement corroborates (`max abs diff 5.220244e-54`, C-order) against an
F-order control three orders larger, so the row order is measured and not assumed. **Digest identity
is the claim; agreement is the corroboration**, because two arrays holding the same numbers does not
show they came from the same run.

## 4. Build results

Built from the shared source with `build_all.sh`, which forces the rebuild and requires every PDF to
postdate a marker stamped before the builds — so *"Nothing to do"* cannot stand in for a build.

| target | pages | this repository | standalone repository |
|---|---|---|---|
| `main_note.pdf` | **95** | built, marker check OK | built, marker check OK |
| `main_primer.pdf` | **7** | built, marker check OK | built, marker check OK |
| `main_paper.pdf` | **4** | built, marker check OK | built, marker check OK |

**Struck-value containment: `RESULT :: PASS`** in both, with its own self-test passing first
(9 of 11 positive cases discriminate; 4 negative controls reject). The note carries **10/10** struck
literals as a positive control; paper and primer carry **0 of 10**. Zero undefined control
sequences, zero LaTeX errors, zero unresolved references in all three logs.

**Verified in the rendered PDFs, not only in source:** the hadronic-response scope disclosure is
present in all three, and the withdrawn *"lower bound"* / *"floor rather than a ceiling"* wording
returns **zero** hits in all three.

## 5. Both repository heads

| repository | head | remote state |
|---|---|---|
| `MINERvA-OmniFold` | `29016531` | pushed; `git rev-list --left-right --count origin/main...main` = `0 0` |
| `MINERvA-OmniFold-Analysis-Note` | `aab82996d2cd2df0c66829ee7e7eb5bf276b3534` | pushed; `0 0` |

⚠ **This record's own commit advances the first head by one.** A head quoted inside the commit that
carries it cannot include itself; `29016531` is this record's **parent**. Re-measure rather than
quote either value if anything has moved. The 26 shared `.tex`/`.bib` files were byte-identical
between the two checkouts before the standalone build.

**Also on the remote, and part of the same closeout:** `main` is now the single discovery route for
the independent clause-(c) verification, merged at `ff0b6df0` after `OI-189` repaired the guard that
had refused it. `origin` carries `main` plus the **14** branches that hold commits `main` does not;
**66** names were deleted in a second pass, every tip verified an ancestor of `main` first and every
name→SHA recorded **before** deletion at
[`LEDGER-20260920-deleted-branch-names-to-sha.md`](LEDGER-20260920-deleted-branch-names-to-sha.md).

## 6. ⚠ THE LIMITATIONS THAT REMAIN LIVE — all seven, none resolved

**L1. `s_proj = 6.145%` against a `5%` bound.** `(cause 3, Z)`'s `M(ii)` graded **branch 5, NOT MET —
PER-BIN** on a fully valid campaign. It is **flat in `N`** — `6.04% ± 0.39%` at `N = 40/80/160`,
exponent `0.000`, against a resampling floor falling `20.91% → 7.57%` at exponent `1.467` — so it is
a property of the estimator and a larger ensemble would not reduce it. **This is why no significance
is quoted.**

**L2. The five seed-pinned bands are unprobed, and the direction is UNKNOWN.** They carry `26.0%` of
`√Tr C_Z` and contribute zero movement by construction. ⚠ **The *"lower bound"* reading was
WITHDRAWN 2026-09-20** on the third lane's `P1`: `s_proj` is a maximum over a functional set, not a
sum of nonnegative component magnitudes, so releasing them could move the total **either way**.
Newly open as a consequence: whether the `L1` FAIL survives *any* release of those bands. The FAIL
itself is unaffected — it was measured directly.

**L3. Cause 3 is predeclared and NOT computed for this digest.** `M(i)` `UNRESOLVED` on `4c`, a
permanent predeclaration failure. And **no declared boundary was evaluated in production** — all
seven measure `read_by_production: no`, because `z_validator.assess` has no caller outside tests. No
criterion may be described as *applied*, *satisfied*, *passed* or *met*.

**L4. PM-1: accepted by decision, with a historical-input provenance limitation.** The file-level
link between the tuple whose branches were measured and the tuple `combined_source` was built from
**cannot be made from the record** — neither endpoint is identified by path and digest. A source
comment documents intent and is not executable verification; the implementation trace covers only
the inspected implementation; repeated accounts of the tuple observation count as **one**
observation.

**L5. Weight-only implementation does not establish hadronic-response completeness.** It establishes
why the four bands sit outside the kinematic replacement, nothing more. The treatment may not be
called negligible, conservative, complete or deficient without evidence, and no limitation may be
claimed largest at high `E_avail` or `W` merely because those involve hadronic energy. The
collaborator question is **prepared and not sent**
([`QUESTION-20260920-…`](QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md)); silence
reopens nothing.

**L6. Clause (c) was satisfied in substance and violated in ORDER.** The independent verification
followed the adoption. **Ratified retrospectively, not cured.**

**L7. `V6`'s six items have no second-lane reproduction.** Ruled outside clause (c)'s scope, which
is not the same as verified. Anyone re-opening C2's `0.168`/`2.6739`, C4's jitter print, NULL's
`4.4311e-14`, the `read_by_production` census, `run_m1_projection.sh`'s historical `--run-class`
absence, or `58549890`'s control arms is reading **single-lane** evidence.

⚠ **And two scope facts about the verification that discharged `V2`:** it covered **two rows**, and
its own fresh-clone isolation was **not achieved** — the requested clone was absent, `RUN.sh` was
not executed, and it worked read-only against pinned revisions in the existing object database. It
declares both itself.

## 7. What was NOT done, named rather than left to inference

- **`LIVE-STATE.md` is not regenerated.** It is generated by `generate_live_state.py` from canonical
  `main` **on Perlmutter**, and its `Declared state` is authored prose the generator carries forward
  **verbatim** — regenerating updates a timestamp and a sha and revalidates nothing. Its blocker
  text still reads *"No scalar-5D covariance candidate is adopted"*, which §2 above contradicts.
  **Regenerating it from this machine is not possible and rewriting its prose by hand is not this
  record's act.** Named here so the staleness is a known open item and not a discovery.
- **No compute was launched**, no NERSC file written, no job submitted.
- **Nothing was sent to anyone.** The collaborator question exists as a repository artifact only.
- **Four merged branches were not deleted** — each is checked out in a live worktree, and git refuses
  the deletion for a reason that is not caution. See the deletion ledger.

**Co-Authored-By: Claude Opus 5 (1M context)**
