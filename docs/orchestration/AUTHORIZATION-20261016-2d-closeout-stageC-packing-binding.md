# AUTHORIZATION 2026-10-16 — 2D closeout: step-2 binding of the Stage C packed submission path

**Issued by** the paper-tighten lane, as director, under Joseph's compute delegation. This is step 2 of
[`AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md`](AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md)
(the build-step record). With this record on `origin/main`, the 2d closer may deploy the bound package, migrate the
pending shared jobs, and submit packs through the gate, following DESIGN §14.4.

**CITABLE FOR:**
- the packed package and the digests every pack runs under;
- the director's acceptance of the three points the DESIGN §14.3 asks the binding to accept explicitly;
- the accepted departure from the build-step record §4.1 on the worst case.

**NOT CITABLE FOR:**
- a higher ceiling. It stays at 100.0 node-h, and committed grant ceilings under the delegation stay at 132.0 of 700;
- any change to analysis, rollup or driver code, or to any job's physics configuration. These are byte-identical;
- any result;
- re-running a FAILED member, or clearing a pack-level STOP. Each needs its own director record (§3).

## 1. Binding

| item | value |
|---|---|
| package commit | `c873cc22630f8c5b2736c1ca98b455c52db0e5d6` (PR #138). The director merged it as `bea0cc47`; `git diff c873cc22 bea0cc47 -- docs/orchestration/state/2d-closeout/stageC/production` is empty |
| manifest | `manifest.json` (31 files), sha256 `77c6676b808708f55edf8a07d13ebd6cf56b2d8cf44a46e04669bfc59d88f6c7` |
| pack dispatcher | `sbatch_pack.sh` `2908a7bf16ec8788944aadeb5cfac4237ca72f4a32c54b1ed2b71a15f9a623ca` |
| member runner | `sbatch_prod.sh` `ad9b12f3c51f03af68d6da181826bbc591c26cefaf3c19d845427221f4e70bf9`, pinned as `MEMBER_SHA` |
| gate | `launch.py` `a6a9a60adc8394059c8edbf93c225b6639c28d4f6d72a55e65308c5ae298c405` (`CEILING = 100.0`, `PREFIX = "2dc_P_"`, `PACK_PREFIX = "2dc_P_K"`) |
| deployer | `deploy_repo_k.sh` `49619cc576246903195f4dd93288e7c2b302a3a5109c3cd1d9bd9371682dd0e6` |
| unchanged from the 2026-10-15 binding | `jobs.tsv` `c4f1b708…`, `analyze_prod.py` `f9e0d8f2…`, `s5_rollup.py` `6c437004…`, the production driver, `driver_p1.py` and `omnifold.py` |

## 2. Director's review

These were re-measured by the director at `c873cc22` in a detached worktree, on 2026-10-16:
- **Digests.** All eight digests above match the closer's report.
- **Scope.** The package diff against its base `53cdc8a4` touches 16 files, all under
  `state/2d-closeout/stageC/production/`. None of them overlaps the files changed on `main` since that base.
- **Tests.** `python3 evidence/smoke/test_launch.py` with an explicit `TMPDIR`: **RAN 89, FAILED 0**, exit 0.
- **Dispatcher (`sbatch_pack.sh`), read in full.** Before any step starts, it refuses unless all of these hold:
  - both pins match;
  - every member is exactly one `jobs.tsv` row, with no repeats;
  - all members are of one class, and fit the node by count and by summed memory ≤ 515,100 MB;
  - the arguments equal the launcher's record;
  - QOS ∈ {regular, regular_0, regular_1}, NumCPUs 256, AllocTRES billing 256, and TimeLimit equals the members' cap.

  Each member runs as its own `srun --exact` step. Its rc is recorded when it ends, and one member failing does not
  stop the others.
- **Deadline.** `launch.py` `deadline_arg()` gives every pack `--deadline=2026-10-20T23:00:00` PDT (06:00Z). It
  refuses between that time and the end of maintenance.
- **Smoke pack 59860260**, re-measured with `TZ=UTC sacct`:
  - QOS `regular_1`, 19:03:09–19:13:43Z, COMPLETED, ElapsedRaw 634;
  - charge 0.1761 node-h against its cap of 0.85.

  The closer reports these, and the director did not re-run them:
  - members rc 0 and step COMPLETED;
  - provenance PASS 4/4;
  - pilot `joint_01–04` reproduced to ≤ 1.33e-12.
- **Review.** The closer reports three fresh read-only verifier rounds: 3 MATERIAL at `8ea086eb`, 1 at `2b3678b8`,
  and APPROVE with 0 MATERIAL at `e8cc50b0`. The four MINORs were fixed in `c873cc22`, without code changes. Per
  DESIGN §14.6, the verifier mapped requirements 1–7 of the build-step record §4 to `file:line`.
  - **Limit:** the verifier and the executor are the same model, so their blind spots may be correlated.

## 3. Rulings

1. **Worst case: departure accepted.** The build-step record §4.1 required the total enforced worst case not to
   exceed 117.8583 "plus any rounding the closer itemizes". The packed plan's worst case is **118.1083**, and at most
   **118.7458** (DESIGN §14.1). The excess is not rounding. It is structural and itemized:
   - +0.25 for the single S4U row, which runs alone on a node;
   - up to +0.6375 for empty CV tail slots, if some CV rows started on the shared QOS before migration.

   The director accepts this. The gate still enforces 100.0 at every submission. The excess is at most 0.89 node-h,
   and the measured smoke charge is about a fifth of its cap. Retry packs are charged a whole node at the
   re-projected cap and sit outside this plan, as before.
2. **R2: a pack-level STOP is global. Accepted.**
   - A pack that ran but never wrote its `#pack` line halts every launcher action until a director record clears it.
   - This is fail-closed, as grant §3 requires.
   - Accepted cost: one transient node failure stops production until the director rules.
   - The closer reports any STOP to the director at once, with the pack's `sacct` row and status file.
3. **R3: FAILED members cannot be re-run from this package. Accepted.**
   - Re-running a FAILED member, including one whose `srun` step could not be created after `#pack`, needs a
     director record, a new package commit and a re-binding.
   - The grant's rule still applies: any failure other than walltime needs a diagnosed infrastructure cause.
4. **R4: navigation refusals are not stops. Accepted.** Only these three refusals are navigation:
   - "submit <earlier batch> before <batch>";
   - "no rows owed a first submission (or only a held partial pack)";
   - "no deadline-cancelled retry owed".

   Every other refusal stays a stop, under the 2026-10-15 binding §3.
5. **Migration.** It follows DESIGN §14.4, in this order:
   - deploy;
   - `migrate` dry run, then `--execute`;
   - a `sacct` check that every cancelled job shows CANCELLED, ElapsedRaw 0, Start=None;
   - then G2, and S1a … S4b in the frozen order.

   Shared jobs that have started keep their attempts. The migrate transcripts and the `sacct` check go in the
   production REPORT.
6. **Watch items.** These go to the director when they happen, not at the REPORT:
   - **G2 packs.** Their expected charges are shared-QOS estimates, not packed measurements. Report the first G2
     packs' ElapsedRaw against their caps.
   - **CV packs.** Report any CV pack over 2,000 s, about 3× the smoke pack.
   - **Deadline.** Report any pack removed by the Deadline.

## 4. Unchanged

These 2026-10-15 binding conditions all stay in force:
- `driver_p1` reaches `main` through its own PR before Stage F adoption;
- the S5 ROOT rollup goes to CFS;
- a running job that straddles maintenance (13:00Z 2026-10-21) is a stop, reported and not cancelled;
- a pscratch purge is a stop;
- running past 2026-11-15 needs a prior record.
