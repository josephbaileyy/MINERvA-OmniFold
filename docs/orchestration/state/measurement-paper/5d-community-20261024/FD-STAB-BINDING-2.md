# BINDING 2: the B4 stabilisation probe's full run (director, 2026-11-05)

**Binds** the full run of [`FD-STAB-DECLARATION.md`](FD-STAB-DECLARATION.md) (sha256
`6c91c0ccbb8061c0dfe755f2283ecbf0f12ba001737876df09f8882eca4ca2b4`) under
[`FD-STAB-ADDENDUM-A1.md`](FD-STAB-ADDENDUM-A1.md) (sha256
`277f6c799aca808315ce519f427007b7dec5da0c514dc5d0c229841ec01e23b2`). Both are taken as they stand at
**M_A1 = `cc54d86f7ac66c1346fa69e5894b2d2f000fb09c`**.

**Under** [`FD-STAB-BINDING-1.md`](FD-STAB-BINDING-1.md) ruling 4 and [`FD-STAB-BINDING-1-A1.md`](FD-STAB-BINDING-1-A1.md)
ruling 5, with its Director's correction (#766).

**The code is unchanged since M_A1.** These are its blobs at M_A1, and they are the same at main:

| file | blob |
|---|---|
| `nd-unfolding/estimator_stability_probe.py` | `25179f9f704e61a920c9d0005283b4fcd357d825` |
| `nd-unfolding/sbatch_fd_stab.sh` | `9defbb44e99d0dcc538b7254ab998ba13feb354a` |
| `nd-unfolding/estimator_stability_analyze.py` | `0e4718902e1b156d340ba5a9848d522b5be0fc45` |
| `nd-unfolding/tests/test_estimator_stability_probe.py` | `22e211a20514f9a3c10145085f813c9f5f63f6f2` |
| `nd-unfolding/tests/estimator_stability_mutation.py` | `9ab35c9839fc38322c47fedf95b774ea25d8942f` |
| `…/5d-community-20261024/fd/stab/no-ratio.json` | `27947e1add4dd5fbda17a17020976fd30bea1061` |
| `…/5d-community-20261024/s1/PRESERVE-INVENTORY.sha256` | `dc2ac4e4f3098ce59a81fc043526d87b5c49ec77` |

Binding 1 ruling 6 asked for a test-only follow-up, the `./` spelling. It is `16250c9d8` and lies inside M_A1.

## The dry run's record

The receipts are committed in [`fd/receipts-stab-a1r/`](fd/receipts-stab-a1r/) (#770, merged at `fe9cd52b`). The
director re-hashed the five files the connect checks:

| file | sha256 |
|---|---|
| `pins/pins-check.json` (DTN, PASS, 2026-11-04T23:51:48Z) | `2e0a0b2100ac72a9b733e4cf3b4f2b5f76ff5e43bc94a4c1a8ef91ce451410f9` |
| `dry/DONE` (mode dry, 9 tasks, 9 ended, rc 0, job 60827080) | `ed98090ecfb32c6977256c57b5266183bcd77acf5dbdd5170d02422c4a61e504` |
| `dry/SHA256SUMS` (the 9 products) | `fb379aa50b03cfeb46b2eb178918d57fe73c0a05538d1b7f54358d33f96722a4` |
| `connect/queue.tsv` (128 tasks) | `d391858c1f5f2655f9fbc9d38beff29d9a4ae830ea7b3cf9365a2d2f4958bfeb` |
| `connect/dry.tsv` (9 tasks) | `afc36dc309afb494ae33c99d06467c63ce850a79e4a1dbfc7e326c24110f10b4` |

- **Job 60827080: COMPLETED 0:0.** TimeLimit was 00:45:00, as parsed and printed at submission. Elapsed was 992 s on
  1 node, so the charge is **0.2756 node-h**.
- **The truth control passed** (`dry/truth-control.json`):
  - C1: 0 of 32,849,103 rows differ;
  - C2: bitwise over 65,856 cells, max relative difference 0.0;
  - C3: descriptive, a half-sample MC-statistics difference by design (addendum §2).
- **The tasks:** all 9 exited 0. Walls were 7:07–10:23, and MaxRSS was at most 17.5 GB.
- **Job 60826464:** INVALID because of the director's error (correction item 4). It charged 73 s on 1 node, **0.0203
  node-h**.
- **The cap's remainder** is 8.0 − 0.0203 − 0.2756 = **7.7041 node-h**.
- **The gate's projection** for the full run is in `gate-projection/`. It comes from the bound `project()` at M_A1,
  run offline on the committed queue and the 18 dry start/end records:
  - **projected_node_h = 4.804**;
  - **b2_over_control = 0.990**, against the stop at 2.0.

## Rulings

1. **Step two is bound.** The full run is `sbatch_fd_stab.sh full <deploy> <M_A1> <OUT> 7.2500`, in the dry run's
   `$OUT` (`/pscratch/sd/j/josephrb/fd-stab-a1r-20261104`). The gate skips the 9 dry tasks and carries their
   timings, as §7 and the addendum require. Full mode takes no sixth argument: blob `9defbb44` reads the F0b product
   only in the dry run's truth control, at lines 22–31 and 51–60.
2. **The limit is `--time=07:15:00`, and the gate's cap argument is 7.2500.**
   - Correction item 2 sets the limit at the remainder, but at most `07:15:00`. The remainder is 7.70, so the limit
     is 07:15:00.
   - §7 sets both the gate's cap and Slurm's `--time` to "8.0 minus the dry run's charge", so that they agree. With
     the limit at 7.25 h, the gate is set to 7.25 too. A gate at 7.70 could launch a task that Slurm then kills,
     which would end INCOMPLETE rather than in a clean STOP.
   - The lower gate is stricter, and the total charge stays at most 8.0. The margin over the projection is 2.45
     node-h.
3. **The connect is `stab_full_a1r_submit.sh`,** sha256 `64166c6b01d9c44bd95136c2631245c1a4581aca7ba4b15d91d9eabd0c23adfb`.
   The director has diffed it against the approved dry submit. It refuses unless all of the following hold:
   - the five records above equal their receipts;
   - each of the 9 products matches;
   - all 9 dry tasks ended;
   - none of these exist: log-dry/STOP, log-dry/FAILED, log-full, or a queued probe job;
   - the pins record is PASS at M_A1 and **at most 48 h old**, or a fresh pins check comes first;
   - sacct shows 60826464 as TIMEOUT and 60827080 as COMPLETED, with a remainder of at least 7.25.

   If those hold, it then:
   - checks the iris half-balance;
   - makes a fresh clean clone at M_A1 into `deploy-full`, with the 7 blobs and both shas verified;
   - runs the environment pre-check;
   - submits from the plain login environment;
   - **cancels at once if scontrol's TimeLimit is not 07:15:00.**
4. **The cluster lane stays `limitation-resolver`.**
   - One ssh invocation, with `-o ControlPath=none`, checks the connect's sha and launches it.
   - The lane watches by job id, charges from sacct, and pins the products and the DONE or STOP.
   - REPRICE, INCOMPLETE and STOP come to the director unrepaired. A stopped full run is not resubmitted (§7, "After
     a stop").
5. **The readout.** After DONE, `estimator_stability_analyze.py` runs at M_A1 with the arguments in §7, on a login
   node, nice 19, with threads capped. Its record and the receipts come to the director before any reading is
   quoted.
6. **Unchanged:**
   - adopting a winner as the single final estimator is Joseph's separate decision (#714 item 2);
   - 1B's stage 1 waits for it;
   - the paper's rounding section stays as it is unless Joseph decides otherwise.

Nothing is submitted, deposited or tagged.
