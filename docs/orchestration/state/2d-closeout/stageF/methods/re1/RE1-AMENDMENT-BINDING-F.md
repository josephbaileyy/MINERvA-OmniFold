# RE-1 run 2 binding addendum: the figure jobs after F1 timed out (2026-10-22)

**By** the paper-tighten lane, as director, under
[`RE1-AMENDMENT-DECLARATION.md`](RE1-AMENDMENT-DECLARATION.md) §6 ("a job beyond its limit ... is never resubmitted
without the director") and [`RE1-AMENDMENT-BINDING.md`](RE1-AMENDMENT-BINDING.md).

**Facts re-measured by the director** (`sacct -X -j 60143725`): `re1-f1`, debug, TIMEOUT, ElapsedRaw 672 against a
0:11:00 limit, billing 256 → 0.1867 CPU node-h. The re-1 lane reports that K3 ran for six producers (five bitwise
equal; `eavail_marginal_vs_paper_pull_full` failed on panel geometry only) and that the conversion steps conv3, conv4
and `re1_f_numbers` did not run. The cause is the wall time of four serial producers (2.0–2.6 min each), not the
declared code.

## Rulings

1. **F1b is approved as proposed:** debug, limit 0:10:00, only F1's unfinished steps (conv3, conv4,
   `re1_f_numbers`), unchanged, from a new sbatch that sources the same environment. Committed on the lane's branch
   before submission.
2. **F2 runs the four producers serially, not concurrently,** with the declared F limit of 0:22:00. Running them in
   parallel would change the launcher and could let the producers race on shared matplotlib or ROOT caches, for a
   saving of minutes. At 2.6 min each, four serial producers fit with margin. The F-R1 redraw copies are committed with
   their diffs before F2, as bound.
3. **`fig:eavail-marg`** is "not regenerated" (K3 failed). Its χ² may be computed from P3 by the same producer and
   reported as a number, labelled: the producer's printed values reproduced at K3 (pull mean 0.16, rms 0.83,
   χ²/ndf 4.98, computed 4.981), but its figure did not.
4. **Charge.** F's worst case becomes 0.1867 + 0.167 (F1b) + 0.367 (F2) ≤ 0.72 CPU node-h, against the 0.367
   declared for F. That is a deviation the report states. Run 2 stays within its 6.0 cap.
5. **No further resubmission** of F1b or F2 without the director. The report states why F1's limit was 0:11 against
   the declared 0:22.
