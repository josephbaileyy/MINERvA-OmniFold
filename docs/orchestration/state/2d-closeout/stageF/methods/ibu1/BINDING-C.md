# IBU-1 binding addendum: job C (2026-10-22)

**By** the paper-tighten lane, as director. **Binds** the validation lane's resubmission proposal (`LEDGER-NOTES.md`,
PR #261, merged at `e0b07ed0`) under [`DECLARATION.md`](DECLARATION.md) §6 and [`BINDING.md`](BINDING.md).

**Facts re-measured by the director** (`sacct -X`, 2026-10-22):
- 60130813 ibu1_A COMPLETED, ElapsedRaw 248, billing 256 → 0.0689 CPU node-h;
- 60130899 ibu1_B1 TIMEOUT, ElapsedRaw 1155, billing 256 → 0.3208;
- 60130900 ibu1_B2 CANCELLED while pending, ElapsedRaw 0 → 0.
- Charged so far 0.3897 CPU node-h. These match `LEDGER.tsv`.

## Rulings

1. **One job C over task lines 3–123 is approved.** For B1's unfinished lines it is their one permitted re-run
   (DECLARATION §6, "once more in one job"). For B2's lines it is their first run. As the lane proposed, lines that do
   not finish in C get no further run, and their units are INCOMPLETE.
2. **B1's completed per-seed products are kept.** They were written atomically (`.partial-<pid>.tmp` then `os.replace`;
   no partial file remains), by the bound code at `7ea30e3d`, and which seeds completed depends only on launch order,
   not on any outcome. Conditions:
   - the report lists every product by the job that wrote it (B1 or C);
   - every kept product passes the same meta checks as C's (code sha, seed, truth, config, input digests);
   - **control K-B1:** one kept seed from each partial line (N_nominal_val, N_gibuu) is recomputed by the bound code
     in a scratch directory and compared bitwise with the kept product before the report. A mismatch voids every B1
     product of that line, which then counts as not run. The cost is inside the grant (debug QOS is allowed).
3. **Time limit 1:26:00, not 1:06:00.** The proposal's base projection (52.4 min) rests on an unmeasured P-replica
   rate, and its own pessimistic sensitivity case is 69.1 min, above the proposed 1:06 limit. The bootstraps keep no
   checkpoint, so a limit hit loses them entirely. The binding projection is therefore the pessimistic case, 69.1 min,
   and 1.25 × 69.1 min = 86 min is both the limit and the stop-and-report threshold. It stays inside the
   declaration's 1:30.
4. **Charge.** At billing 256 on one node, 1:26 is at most 1.43 CPU node-h, so the worst case in total is
   0.39 + 1.43 = 1.82 CPU node-h: within the B cap of 3.0, the declared worst case of 3.5 and the grant of 10.
5. **Unchanged:** deploy and pin `7ea30e3d`, the launcher, 2 CPUs / 11G per step, 1 node, regular QOS, the seeds,
   truths, gates and reading rule.

Submit as proposed, with `--time=01:26:00`. Ledger C in `LEDGER.tsv`.
