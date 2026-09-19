# DRAFT ADOPTION RECORD — `z-cv.npz` under the `SPEC` §6.4 exception

> ## ⚠ THIS RECORD ADOPTS NOTHING AS IT STANDS, AND IT IS BUILT SO THAT IT CANNOT
>
> The sentinel line in §1 is **deliberately negated**, so `run_m1_projection.sh`'s guard
> **refuses it** (`rc 3`). That is intentional: a draft a script would read as an executed
> adoption is not a draft. **The single act this record is waiting for is Joseph's**, and it is
> one line — see §7.
>
> **CLASS:** unsigned draft, prepared under Joseph's standing instruction to take the exception
> route *"to the point where only my ADOPT is missing."*
> **Not pushed. Not signed. Not executed.**

---

## 1. The adoption line

    ADOPTS-SHA256: DRAFT -- NOT SIGNED -- 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5

**Subject:** `uq_5d/z_pilot_20260916_a5/z-cv.npz`, **890,500,272** bytes, `variant: "cv"`,
re-measured 2026-09-17 and matching its receipt.

## 2. ⚠ WHAT IS BEING ADOPTED, AND THE DEFECT IT CARRIES, IN THE SAME PLACE

`DECISION-PACKET-20260918` §10.2 requires that *"the record must carry the `UNRESOLVED` status and
the predeclaration failure in the same place as the adoption, so the defect cannot be read
separately from the decision."* Accordingly, and not in an appendix:

- **`(cause 3, Z)`'s `M(i)` is `UNRESOLVED`**, `reject_conditions` **`4c`**, `branch = None`. The
  reason is a **predeclaration failure**; it is **permanent and applies to the criterion**.
  Adopting this product **does not regrade it**.
- **The product's own `scientific_acceptance` is `NON-PASSING` and its `adoptable` is `false`.**
  Those fields are computed, not asserted (`ad2af264`), and they stay as they are. This record does
  not change the artifact; it is a decision **about** the artifact.
- **`SPEC` §6.4 requires the null bound "fixed before production", and production has happened.**
  The derivation step is therefore **unperformable for this product by anyone** — which is why the
  route is an exception and not a repair.

## 3. The exception this rests on, and its exhaustion

`AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md`, **EXECUTED 2026-09-18** on
Joseph's ruling, after `P0` returned the like-for-like branch and `P2` was accordingly not spent.

> **The exception attaches to BYTES, not to a criterion.** It covers
> `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` **and nothing else.** Any
> other candidate — including any product of the two-member campaign preregistered at `44e09fd8` —
> gets `assessable = False` with **no exception available**. There is nothing here for a later lane
> to inherit.

## 4. The alternative evidence the amended requirement calls for

Stated as a checkable set, per §10.2:

1. **The retrospective scale-relative assessment** — `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖ =
   `4.452e-14`, reconstructed by `z_statistics.reconstruct_null_ratio` from the pilot's own
   persisted operands (`bridge.json`, `z-null-source.npz`, `sha256 2ac9d087…`), **recorded as an
   assessment carrying no grade token.** It is **4.5 orders below** the declared `ε = 1e-9`.
2. **Cause dispositions 1–7**, each at MET or explicitly dispositioned — `AUTHORIZATION-20260918`
   ruling 6, and C7 closed under
   `DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`.
3. **The C6 provenance declaration** of `DECISION-PACKET-20260918` §10.1, **including its three
   named unknowns**.
4. **The traceability statement** that the archived `C_stat` / `C_ML` **cannot self-attest**: their
   producing invocation is unrecorded, their `--cv` is inferred from two concordant era launchers,
   and their input binding rests on count, index coverage and timestamp ordering — **none of which
   is cryptographic** (§12.3, accepted as an explicit provenance risk).

## 5. Identity, measured and not inferred from a filename

| | |
|---|---|
| product | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz` |
| `sha256` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` |
| bytes | `890,500,272` |
| declared variant | **`cv`**, read from the product's own metadata and enforced by `project_cov_nd.py --expect-variant` |
| assembling revision | `fb9ec3560fd6d62295dffc81b5694c9e26667d5b` |
| producing job | `58454524`, `ExitCode 2:0` — **2 is this CLI's completion code for "construction ran, science NON-PASSING"**, not a failure |

⚠ **`SRC_COV` is enforced by VARIANT IN THE PROJECTOR, not by path in the launcher.** Joseph's
ruling: *"I will not perform ADOPT on an artifact whose identity rests on a filename."*

## 6. What this record does NOT do

It does not regrade `M(i)`, does not change any boundary, does not extend to any other digest, does
not authorize the analysis-note push, and does not by itself run the projection. It is one input to
`run_m1_projection.sh --run-class publication`, which additionally requires `MNV_ADOPTION_EXCEPTION`
to name the executed §6.4 amendment and `MNV_EXPECT_VARIANT=cv`.

## 7. THE ONE ACT THIS IS WAITING FOR

**Joseph, to adopt:** in §1, delete the four words that precede the digest, so the line reads the
sentinel key, a colon, and the 64 hex characters — nothing else. Then commit this record under his
own identity.

**Until that edit, `run_m1_projection.sh` refuses this file with `rc 3`** — asserted in both
directions by `nd-unfolding/tests/test_draft_adoption_record.py`: the draft as written is refused,
and the same bytes with only that edit applied are accepted. **Neither this lane nor any script
performs the edit**, which is the property that makes this a draft.

**Co-Authored-By: Claude Opus 5 (1M context)**
