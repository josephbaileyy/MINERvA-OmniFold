# AUTHORIZATION 2026-08-19 — discharge the adjudicated PSD wording in `sec_systematics.tex`

**Joseph, verbatim and complete, given directly in his own session:**

> I authorize it

Given in reply to a specific request: authorize the qualified PSD wording, which the repository's
own procedure prescribes verbatim and which the currently-published note violates. This receipt is
committed and pushed before the publication text changes.

## What is authorized

Correct `sec_systematics.tex:171`, which currently reads **"Both were positive semidefinite"**.
`PROCEDURE-gbdtFive-macro-update.md`'s row for that sentence carries an amendment — *"MEASUREMENT NOW
EXISTS AND THE WORDING IS ADJUDICATED (2026-08-17, lane B; mediator confirmed with amendment)"* —
which prescribes **"PSD to machine precision" WITH THE RATIO ALONGSIDE — NEVER BARE "PSD"**, and
states the obligation is **dischargeable by wording, not by a new computation**. Quoting the existing
ledger ratio is therefore permitted and no magnitude is adopted or computed.

Why bare wording is forbidden, all three measured in the row rather than argued: the campaign's PSD
gate is RELATIVE (`min_eig >= -1e-9 * max_eig`, `BEN-044`) and `−3.2e-16` clears it by ~10⁶; no
consumer bites, since a covering grep finds ZERO `cholesky` calls and every inversion-shaped consumer
uses `pinv`, which truncates such a mode; but the bare word is falsifiable in one line, because a
matrix at the real covariance scale with that ratio makes `np.linalg.cholesky` raise. And
`VALIDATION_LEDGER.md:1322` already reserves **"PSD exact (0 negative eigenvalues)"** for a
genuinely-zero case, so bare "PSD" collides with it and reads as the stronger claim.

## THE CONSTRAINT THAT MUST GOVERN THE EDIT, discovered while pinning the operands

**`VL16` and `VL17` DO NOT MEASURE THE MATRICES THE NOTE JUST STRUCK.** Measured from
`VALIDATION_LEDGER.md:187-188`: `VL16` (A1 bkgaware, mean-centered) is `sqrt_tr_old 4.3578e-38 ->
sqrt_tr_new 5.2696e-38`, PSD most-neg/max `−3.19e-16`; `VL17` (A2 bkgaware, CV-centered) is
`-> 5.6743e-38`, `−3.23e-16`. The struck pair is `\gbdtFiveAdoptTrace` **5.81e-38** and
`\gbdtFiveCVTrace` **6.24e-38**. Those are different products: `VL16`/`VL17` are the J28 bkgaware
re-roll, the struck pair is the superseded original.

So appending the two ratios to a past-tense sentence about the superseded matrices would attach
new-product measurements to old ones — the exact inheritance error the procedure row exists to
prevent, running backwards. The row states the PSD claim is **"a property of the new matrices"**.

**THE EDIT MUST NOT ATTACH `VL16`/`VL17` TO THE STRUCK MATRICES.** Whoever lands it must first decide
which matrices the sentence is about, and say so in the sentence:
- if it is about the SUPERSEDED pair, there is no PSD measurement for them in the ledger, so the
  claim cannot be qualified and must be dropped or explicitly marked unmeasured — NOT decorated with
  another product's ratio; or
- if it is about the NEW products, the sentence must name them as such, in the tense that makes that
  true, with `VL16`/`VL17` cited and each ratio attached to its own construction — `−3.19e-16` to the
  mean-centered arm and `−3.23e-16` to the CV-centered arm, in that pairing and not swapped.
Either resolution discharges the row. Guessing between them does not.

## Boundaries

Does not adopt, supply or change any covariance, trace, uncertainty or central value; does not alter
the four `\dead{}` strikes or any other sentence; does not touch `paper_body.tex`,
`primer_body.tex`, `values.tex`, `check_dead_containment.py`, `build_all.sh` or any figure; does not
authorize compute, deletion, repinning, pinned-file changes, embargo lifting, the 41.44 GB
intermediate, a `C_stat`/P5A pairing, or an `OI-126` resolution. The `\dead{}` count in
`sec_systematics.tex` must be 4 before and after.

Pre-push gate as before: `build_all.sh`, which forces the rebuild and proves each PDF postdates a
marker stamped before the builds, then containment with both halves and never `--source-only`.
