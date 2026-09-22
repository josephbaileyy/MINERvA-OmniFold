# RECORD 2026-09-20 — PROJ: the M1 publication projection, built and its pairing verified

**CITABLE FOR:** the product identity, the predeclared checks, and the binding pairing result.
**NOT CITABLE FOR** any grade or for the analysis-note push. Built under
[`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`](DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
and **carries that record's four measurements**.

Receipts: [`state/PROJ-20260920-m1-publication-receipt.json`](state/PROJ-20260920-m1-publication-receipt.json),
[`state/PROJ-20260920-binding-check.json`](state/PROJ-20260920-binding-check.json).

## 1. The product

| | |
|---|---|
| path | `/pscratch/sd/j/josephrb/z2m-products/PROJ/cov_5d_to_eavailW_publication.root` |
| `sha256` | **`835828bf3e25bbd9f279088e5cc89b8b325d727446fec9fabbbc92fd7e71a54e`** |
| bytes | `17,101` |
| run class | **`publication-under-exception`** |
| source | `3d7465f6…`, **variant declared `cv` AND measured `cv`** |
| map | `5D (pt,pz,eavail,q3,W) → (E_avail,W)`, `M_shape [42, 10694]`, `M_content_sha256 64fec490…` |
| job | `58655229` → **`58655509`**, `COMPLETED 0:0`, `39 s` |

**The source's own metadata is preserved unedited**: it still records `adoptable: false`. The
exception is a decision about the bytes, not an edit to them.

## 2. The predeclared checks, all of them

Declared in `OPERATIVE-SHEET` §4c **before** the run, mode `receiving-cells`:

| declared check | result |
|---|---|
| **`src_cells_dropped` must be `0`** — a source cell mapping outside the destination is discarded uncertainty | **`0`** |
| exact symmetry | `max|C − Cᵀ| = 0.00e+00` |
| PSD | **no negative eigenvalue** — `lambda_min = +4.359e-92` (**positive**, `n_negative = 0`), `lambda_min/lambda_max = 2.93e-15`, condition number `~3.4e14`. ⚠ **Read the correction below before quoting this row** |
| `hRowIndex` readback digest | **OK**, 42 labels, `9eb9d216…` |
| `rel` (CV reproduction) | **does not exist in this mode**, and nothing is reported for it |
| `n_empty` | **NOT a declared check.** The projector writes it (`0`); **nothing may cite it**, because it is zero by construction here |

Also recorded: `C_low (42,42)`, `sqrt-tr 4.4552e-39`, and **rank `36` of 42 AT THE PROJECTOR'S
HARDCODED RELATIVE CUTOFF `rc = 1e-12`** (`project_cov_nd.py:340`) — **never quotable bare.** The
source is rank-deficient and the projection inherits its ill-conditioning; that much is a property
of the object, and the integer is not.

> ## ⚠ CORRECTED 2026-09-21 — THE PSD LABEL AND THE RANK. NO MEASUREMENT MOVES.
>
> **1. `2.93e-15` is `lambda_min/lambda_max`, and `lambda_min` is POSITIVE.** Measured:
> `lambda_min = +4.359104e-92`, `lambda_max = 1.488215e-77`, `n_negative = 0`, condition number
> `~3.4e14`. The label *"most-negative/max"* asserts a negative eigenvalue this object does not
> have. It is correct one row up in `VALIDATION_LEDGER.md` `VL142`, whose trunk min genuinely is
> negative (`-1.6306079908811896e-90`, `abs(min)/max = 7.3147e-16`); it was carried down onto an
> object with a positive min. **Do not "fix" `VL142`.**
>
> **2. `n_negative = 0` proves less than a PSD row suggests.** The smallest eigenvalues sit at the
> float64 noise floor of a 10,694-term weighted sum, so **their sign is not meaningful**, and zero
> negatives is a statement about this computation — **not** a demonstration that the source's
> 5,214 negative directions were handled, and not a property guaranteed under a different mask,
> summation order or precision.
>
> **3. The rank integer is a property of the CUTOFF, not of the matrix.** Scan on the same
> projection: `rc 1e-6 → 26`, `1e-8 → 28`, `1e-10 → 32`, **`1e-12 → 36`**, `1e-14 → 41`, `0 → 42`;
> `numpy.linalg.matrix_rank`'s own default `n*eps = 9.33e-15` gives **41**. The 42 eigenvalues decay
> smoothly over ~15 orders with **no plateau**. **Do not substitute `41` for `36`** — that repeats
> the defect with a different constant.
>
> **4. What survives of *"a property of the object"*, and what does not.** That the source is
> rank-deficient and the projection inherits its ill-conditioning **is** a property of the object.
> The **integer** is not, and the clause was being used to license the bare integer beside it.
>
> **Provenance, stated precisely.** [`PLAN-20260918-scalar5d-publication-completion.md`](PLAN-20260918-scalar5d-publication-completion.md)
> §16.1a declares **TWO** withdrawals — the bare rank, and a separate *"`M C Mᵀ` averages the
> negative directions out"* mechanism claim — and supplies the scan and the `lambda_min` sign above.
> Points 1, 2 and 4 here are **consequences drawn from it**, not withdrawals §16.1a itself declared;
> it could not have withdrawn this document's wording, because §16.1a was committed at `e78a458a`
> (2026-09-18) and this text at `493e3f25` / `7257b255` (2026-09-20). ⚠ **Scope:** §16.1a scanned the
> **DIAGNOSTIC** product (`m1_eavailW_DIAGNOSTIC.root`, `17,120` B, job `58510024`). This run
> recorded the identical `lambda_min`, ratio, `sqrt-tr` and rank-at-`1e-12`, so the spectra agree at
> recorded precision, but **no independent cutoff scan on `835828bf…` exists.**


## 3. The BINDING pairing check, repeated against the publication product

`OPERATIVE-SHEET` §4: *"repeat (a) and (b) against the publication product when PROJ runs — (a),
the digest, is the binding one."*

| leg | result |
|---|---|
| **(a) BINDING — same source by DIGEST** | the projected source's `hXSecND_flat` and the figure's are **byte-identical**, `0f04abceccb5330b…` |
| (b) corroboration — `hCV_marginal` vs the figure's `hData2D`, **C-order** | `max abs diff` **`5.220244e-54`**, relative `1.7e-16`, sums `1.676366e-37` both |
| (b) control — **F-order** | `3.071941e-38`, **three orders larger** — so C-order is measured, not assumed |

**Both reproduce the diagnostic's recorded figures exactly.** The ordering matters and is kept:
numerical agreement shows two arrays hold the same numbers; **the digest is what shows they came
from the same run.**

## 4. ⚠ WHAT TRAVELS WITH THIS PRODUCT

The four measurements of the adoption record apply to everything quoted from it:

1. **`s_proj = 6.145%` against a `5%` bound** (`GRADE-20260920`, branch 5, fully valid campaign).
2. **That effect is flat in `N` at `6.04% ± 0.39%` over `N = 40–160`**, while the resampling floor
   falls (`p = 1.467` vs `p = 0.000`) — **a reproducible property of the estimator, not resolution
   noise.** The `± 0.39%` is scatter at **one** seed pair; the seed-pair width is **unmeasured**.
3. **Five bands are outside what the variation probes** — five seed-pinned bands carrying `26.0%`
   of `√Tr` contribute zero movement by construction, so their seed sensitivity is unprobed and
   the effect on the total when they also vary is **unmeasured**.
   ⚠ **CORRECTED 2026-09-20: this read *"It is a LOWER bound"*.** Withdrawn on the third-lane verification's finding `P1`
([`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md); withdrawal recorded at
[`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md)) —
   `s_proj` is a **maximum over a functional set**, not a sum of nonnegative component magnitudes,
   so releasing a held-fixed component can move the total the other way. The measurement stands;
   the direction of the unmeasured remainder does not.
4. **The seed also moves the central values**, by `≤ 6.02%` of their own quoted uncertainty on
   these 42 destinations (median `1.06%`), worst at **functional index 2 — the same one that failed
   `s_proj`**. Per individual 5D bin it reaches `49.8%` of `σ`; the projections do not, because
   aggregation suppresses it.

**C3 stays "predeclared, not computed"** for this digest, and `M(i)` stays `UNRESOLVED` on `4c`.

## 5. ⚠ A DEFECT FOUND BY RUNNING IT, recorded because it nearly cost the run

The first submission (`58653845`) **failed in 8 s**: `run_m1_projection.sh` never activated the
campaign environment, so `project_cov_nd.py` died importing ROOT. The launcher exists precisely so
that *"the eventual authorization is a SUBMISSION rather than new code written under time
pressure"*, and its own header names ROOT I/O as *"the UNMEASURED leg"* — which is the leg that
failed. Fixed at `926a92a4` by using the shared preflight chain, **activated after the refusals** so
they keep firing in a degraded environment, with a test asserting that ordering.

**Co-Authored-By: Claude Opus 5 (1M context)**
