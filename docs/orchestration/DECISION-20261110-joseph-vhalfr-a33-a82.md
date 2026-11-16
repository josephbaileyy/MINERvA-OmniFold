# DECISION 2026-11-10 — Joseph: V-HALF-R Amendment 1's open items: no fixed q3 edge for C7 (landmarks printed), and the three new tilts as the reserved confirming set

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **Amendment 1** (`state/2d-closeout/valid-region-20261107/v-half-r/AMENDMENT-1.md`, PR #1043 at `7c3c8ec0e`) left two
  items for Joseph: A3.3, whether C7 (E_avail, q3) keeps a fixed q3 edge (0.8 GeV, 1.2 GeV or none), and A8.2, the
  reserved-truth list.
- **An independent consult** at Joseph's request (codex-school `gpt-6.1-sol`, high, read-only;
  [`v-half-r/consult-sol-a1-20261110/`](state/2d-closeout/valid-region-20261107/v-half-r/consult-sol-a1-20261110/))
  recommended a fixed 1.2 GeV edge as a momentum-transfer landmark. It said neither edge separates processes. For
  A8.2 it recommended option (a), with "not confirmed" and "untested" rules.
  <!-- absence-ok: "untested" names an outcome class of the confirmation step, not a claim that a result does not exist -->
- **Joseph asked** whether the published analyses' q3 limits were arbitrary and not physically motivated. The
  director's answer: the limits plausibly reflect each analysis's beam energy, reach and resolution, though the papers'
  stated motivation was not checked. A fixed edge would buy only comparability, which C6 already supplies for the
  published two-dimensional result. It would also raise the chance that C7 ends with no reportable binning. The
  director recommended no fixed edge, with the landmarks printed.

## Joseph's answers, verbatim

On A3.3, after the first question:

> can you ask a sol session again

(sha256 of the text plus a final newline begins `4066c5a884e93e0f`). After the consult:

> could it be that their bin choice was arbitrary, not physically motivated, and we shouldn't follow it?

(`f7b1f28a9b4df289`). Then:

> No edge, landmarks printed (Recommended)

(`d9436bf2d3d070f4`). On A8.2, first:

> ask sol about this too

(`36d831a574e88169`), and after the consult:

> Option (a) + rules (Recommended)

(`fb1dc08f3c3a4c44`).

## What is decided

1. **A3.3: C7 keeps no fixed q3 edge.** Its binning is set by min(purity, diagonal fraction) ≥ 0.5, the floor and
   A3.1's no-strips rule alone. The record prints where C7's final q3 edges fall relative to 0.8 and 1.2 GeV, the
   published low-recoil landmarks, as a description only. No edge is added or moved after the binning is seen.
2. **A8.2: option (a).**
   - The three new synthetic tilts, along p_T, p_∥ and W, are the confirming set.
   - G18 and AR23 are run as a disclosed descriptive extra. Their sixteen-cell grades are already known, and their
     results cannot rescue a failed tilt.
   - **"Not confirmed":** any frozen bin that fails, or is unresolved, at an applicable confirming tilt; or missing
     departure information.
   - **"Untested":** a bin with no applicable reserved departure. It is not counted as a pass.
  <!-- absence-ok: "untested" names an outcome class of the confirmation step, not a claim that a result does not exist -->
   - **C6 and C7 must each confirm separately.** No rebinning follows the confirmation read.
   - **Frozen before any tilt is generated:** each tilt's standardization population (global or within cells), its
     normalization and its domain.
   - **The confirmation is reported as limited to the tested truths.** The tilts are a substantial stress at amplitude
     0.3 on a standardized coordinate. They are not a realistic generator envelope.
3. **The amendment goes to coverage-5b-audit** with these two items settled, then to the director's binding. The study
   runs only after Tier 3 reports.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the two choices and their rules.
- **Not citable for:** the published analyses' q3 limits, beyond what the repository records; any V-HALF-R result.

Nothing is submitted, deposited or tagged.
