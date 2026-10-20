# Binding addendum 3: QOS fallback before the Perlmutter maintenance; the margin correction (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §3.

**CITABLE FOR:** the QOS rule up to the maintenance window, and the margin correction.
**NOT CITABLE FOR:** any result.

## 1. QOS before the maintenance window

Perlmutter is draining ahead of `maintenance_20261021` (2026-10-21 06:00 to 10-27 23:00 PDT). Phase-1 jobs on shared
have been pending for hours (Resources).

- **MP3-B** may run on debug, with the shared copy cancelled before the debug copy starts. The same applies to the
  ten-test margin receipt.
- **MP-5 and MP-1 jobs** not started on shared by 2026-10-20 16:00 PDT move to regular. Passes are packed several per
  node as concurrent processes where memory allows, and each shared copy is cancelled before its regular copy can start.
- **Anything unfinished at 2026-10-21 04:00 PDT** is cancelled cleanly and recorded as deferred to after the
  maintenance.
- **Ceiling:** everything stays within the phase-1 ceiling (35 CPU and 3 GPU node-h). The ledger records each job's
  QOS.

## 2. The margin correction

[`M2-AUDIT.md`](../2d-closeout/stageF/methods/M2-AUDIT.md) Q4e gives, for the three closest shape tests, margins of
2.8, 4.5 and 4.9 null SD, and at least 5.7 for the others. Those are distances of the observed statistic from the
**null median**, not from the **decision boundary**.

Under amendment 7's rule (`s5p_inference.holm_determined`), the measurement session found:
- NuWro shape is last in the Holm order, at threshold 0.05;
- it stays rejected only while k ≤ 69 of B = 1751, that is while T_shape > 8672.55;
- the frozen T_shape is 9660.01, so it is **1.11 null SD** from becoming undetermined.

The ten decision-boundary margins are being computed as a receipt for the session's phase-1 PR. When they land,
M2-AUDIT gets a correction note and the methods paper quotes the boundary margins.

[`SF1-SPEC.md`](../2d-closeout/stageF/methods/SF1-SPEC.md) §1 quotes the median margins as its rationale. Its design and
its acceptance rule (§4) are unaffected, because §4 recomputes each decision directly.
