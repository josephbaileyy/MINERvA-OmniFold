# AUTHORIZATION 2026-10-12 — 2D closeout Stages A (remainder) and B: small diagnostic compute

**Issued by** the paper-tighten lane under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md) §3. That
section requires a committed record before any job of a stage is submitted; this is that record for
Stages A and B of [`PLAN-20261011-2d-closeout.md`](PLAN-20261011-2d-closeout.md).

**CITABLE FOR:** the bounds below, for read-only audit and diagnostic work by the 2D closeout executor
("2d closer") on Stage A's remaining items (selective-I/O receipt, the E_U candidate checklist) and on
Stage B's input and recipe assessment.

**NOT CITABLE FOR:**
- any production, covariance, statistical ensemble, universe sweep or re-unfold of data or MC for a quoted
  product;
- Stage C or later work;
- adoption, claims, a KI-85 lift or a publication change.

Stage C needs its own record, issued after Stage B's recipe passes review.

## Bounds

| item | value |
|---|---|
| executor | 2D closeout executor (2d closer session), directed by the paper-tighten lane |
| allowed without Slurm | login-node reads of committed and saved products, and small scripts writing only to the namespace below |
| Slurm allowance | **≤ 2.0 charged CPU node-h on m3246 in total**, recomputed from `sacct` for jobs named `2dc_AB_*`; counts toward the delegation's 700 node-h ceiling |
| per job | walltime ≤ 1 h; CPU only; QOS `shared` or `regular`; no premium, no GPU |
| purpose | diagnostic reductions or reads too large for a login node (e.g. reading saved weights, histograms, universe inputs); not new unfolds of quoted products |
| output namespace | `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/` only; nothing written to any product or publication path |
| job names | `2dc_AB_<tag>` |
| window | until the Stage B exit report, or 2026-10-26, whichever is first |
| attempts | a failed job may be retried once after a diagnosed infrastructure cause; a scientific result is never a reason to retry |
| recording | each job id, purpose, walltime and `sacct` charge in the stage REPORT (`docs/orchestration/state/2d-closeout/stageA|stageB/REPORT.md`) |
| reporting | to the paper-tighten lane before any job outside these bounds, and at each deliverable |

The executor's isolation, identity and review rules are those in the director's assignment, summarized in
the stage REPORTs. This record launches nothing.
