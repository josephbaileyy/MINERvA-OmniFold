# DECISION 2026-10-25 — Joseph: approve F0, the re-grade of existing 5D fake-data products

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The fake-data plan is `state/measurement-paper/5d-community-20261024/FD-PLAN.md` (PR #352, merged at `a54a10be`).
  The director's rulings on it are in `FD-DIRECTOR-RULINGS.md` (PR #353, `9e84f797`).
- The director asked Joseph to approve **F0**: re-grading the 8,545 existing configuration (e) fake-data products on
  R00–R15 against S1's C_total.
  - The bias is graded at 18 truths, with the leave-own-vertex-out matrix for truths in a vertex family.
  - It runs on a login node at 0 node-h.
  - It also makes a 14.7 MB HPSS copy of the `f4` products, which have none.

Joseph's answer, verbatim:

> yes I approve F0

sha256 of the text plus a final newline begins `aabea44ba4ccc59a`.

## What is decided

1. **F0 is approved** as FD-PLAN §§3 and 5.2 describe it, with the rulings of FD-DIRECTOR-RULINGS.md.
   - **Cost:** 0 node-h, on a login node.
   - **Storage:** the HPSS copy of the 80 `f4` products, after control 0. Nothing is written to CFS.
2. **It runs through a declaration and a binding,** under the usual stop rule:
   - the measurement session declares the tool, its synthetic tests and the argv;
   - the director binds them.
3. **The report** prints counts with their denominators, by truth family. It prints no f, no absolute cell value and
   no f − g.

## Not approved here

- **Stage G**, which compares the data with generator predictions. It needs Joseph's own approval after F0 reports.
- **F1 (GENIE v3) and F1-W (a data-driven truth).** Joseph chooses F1's configuration.
- **Any cell merge**, any change to κ, and any claim or printed wording.

## Not changed

- No GPU and no premium QOS.
- Claims, KI-85, `\pubhold` and release text are Joseph's. Nothing is submitted, deposited or tagged.
- Publication needs Joseph's and Ben's review and MINERvA collaboration review, which is Joseph's act.
