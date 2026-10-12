# AUTHORIZATION 2026-10-12 — 2D closeout: Stage B diagnostics P4 (G1 census) and P5 (G2 miss-row weights), and the Stage C data copy

**Issued by** the paper-tighten lane under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md) §3. It
follows the sequencing option of the Stage B review (M7): the two diagnostics whose outcomes decide whether
the recipe is final run first; pilot items P0–P3 wait for a separate Stage C grant.

**CITABLE FOR:**
- P4: the instrumented event-loop census of reco-in/truth-out events (G1).
- P5: the dump-mode miss-row universe-weight diagnostic (G2).
- The CFS copy of the Stage C inputs named below.

**NOT CITABLE FOR:**
- P0–P3;
- any production, re-unfold of a quoted product, repair, adoption or publication change.

A G1 result that implicates the adopted central value `E_U` is reported to the director at once and
changes nothing by itself.

## Bounds

| item | value |
|---|---|
| executor | 2D closeout executor (2d closer) |
| P4 | ≤ 12 instrumented event loops, as priced in Stage B (0.9 node-h) |
| P5 | the G2 diagnostic, as priced (0.7–1.5 node-h) |
| ceiling | **≤ 3.0 charged CPU node-h in total** for P4+P5, retries and the 20 % reserve included; `sacct`-recomputed; counts toward the delegation's 700 node-h |
| per job | walltime < 12 h (expected ≤ 1 h), CPU only, shared/regular QOS, names `2dc_B4_<tag>` / `2dc_B5_<tag>` |
| code | the counter and the miss-row weighting option live in **diagnostic copies inside the stage package**, not as edits to the production driver or event loop on `main`. The production digests stay unchanged. Each patch has a reviewed diff and a no-op control (patch disabled reproduces the unpatched output) before its first job |
| namespace | `/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/` |
| outcomes | per item: MEASURED with its number, or INCONCLUSIVE; a scientific result is never a reason to retry |
| record | `docs/orchestration/state/2d-closeout/stageB/diagnostics/REPORT.md` and an update of the Stage B recipe's G1/G2 rows; fresh read-only verifier |
| data copy | the 10 active merged 5D files (~538 GB) and the two `.npz` evidence arrays, from `/pscratch` to CFS `m3246`, read-only source, sha256 re-measured at the destination. **First** read the CFS quota with the quota instrument. If free space after the copy would be below 3 TB, stop and report instead of copying |
| window | until the diagnostics report, or 2026-10-26 |
