# BINDING: 1B gate-D diagnosis (director, 2026-11-01)

**Binds** [`FD-1B-DIAG-DECLARATION.md`](FD-1B-DIAG-DECLARATION.md), as merged in PR #626 at **M3 =
`ea2977613cd051dc3c2b321c7fad44f7a6d3ef2c`**.

**Under** `DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md` item 2 (Joseph: "Diagnose, then fork
(Recommended)").

## What the director checked

- **The head.** The PR head `f654de19` was checked before the merge. The independent read-only review is posted on
  the PR with dispositions. It found no blockers, and all 11 findings were fixed.
- **The tests.** At that head, `tests/test_fd_1b_diag.py` and `tests/test_fd_1b.py` ran locally (`-B`, own TMPDIR):
  79 passed.
- **The refactor.** `fd_1b_score.derivation_blocks` keeps gate D's computation and summation order: the fixed blocks
  first, then each band's raw block carried by diag(g). The run also refuses unless it reproduces the committed ρ bit
  for bit, with gate D's readout pinned in code at `e1838c0a…`. A changed computation therefore cannot pass silently.
- **The constants.** `K_MAX = 3` is at `fd_1b_diag.py:42`. The gate-D digest is at `:45`.
- **Nothing read.** Before this binding, nothing beyond gate D's committed readout was read: the declaration says so,
  and the lane confirmed it.

## Rulings

1. **K_MAX = 3 is bound.**
   - A cause that needs four or more of the 38 bands substituted is diffuse, not named.
   - The union rule (L1 passes only if the union of all minimal sets has at most K_MAX bands) is bound as written.
2. **The band scope, all 38 bands, is bound.**
   - The decision's fork names "named bands" without a group.
   - The flux group's failure was already public in #618, and the declaration discloses that it informed this scope.
   - A LOCALIZED verdict naming the flux band leads to a flux redesign in the amendment, as for any other band.
3. **L2 is bound as written.** It tests only the uncarried alternative, for all bands at once. A PASS reads "removing
   the carry closes the gap".
4. **The time-box and the failure rule (§3) are bound.**
   - The 24 h run from this binding's merge.
   - One rerun, only for a non-zero exit that writes no readout, after a message to the director giving the cause.
   - A second non-zero exit is a STOP.
5. **The fork (§4) is bound as written.**
   - LOCALIZED leads to an amendment with its own declaration, price and binding. Nothing here authorizes a toy
     redesign, a derivation rerun or any job.
   - Every other outcome stops 1B, with a report.
6. **The connect is authorized.**
   - **Scope:** D1 (a fresh clone detached at M3, with empty porcelain) and D2 (one run, `nice -n 19`), on a login
     node, 0 node-h.
   - **Outputs:** under `$B/deploy/diag`, `$B/score/diag.json` and `$B/logs/diag.log` only.
   - **Not allowed:** Slurm, CFS or HPSS, and edits to any existing checkout.
   - **Purge exposure:** the lane opens existing pscratch inputs as its step-0 practice allows (#622 §7), and changes
     no file's purge exposure.
7. **The report (D3)** gives:
   - the readouts;
   - L1 with its minimal sets, union and intersection;
   - L2;
   - the branch;
   - the time from this merge to the report.

   It proposes no repair beyond naming the branch.

## Fixed, unchanged

The [0.9, 1.1] window, inclusive. The tested matrix, C_total + C_resp (`b79556f0…`), without the run-period block.
Disclosure of the stopped attempt in every outcome. Nothing is submitted, deposited or tagged.
