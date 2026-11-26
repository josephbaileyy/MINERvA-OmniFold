# EVW2D BINDING 1: E_R's per-event weights, connect, post and fetch (one CPU node, cap 0.5 node-h); cleanup by its own GO (director, 2026-11-26)

**Authority:** Joseph, 2026-11-25. The v1 scope includes the 2D central weights
(`docs/orchestration/DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md`, #1326), and every weight file
goes on Zenodo in the same release (`DECISION-20261125c-…` §1). The declaration is `EVW2D-DECLARATION.md`, sha256
`c1b0164317c531fcc15cc769fec2cbdbe9ef955db816fc00a0d0865054c89d51`.

**Binds:**
- the code as merged in #1347 (`4d9147f9`);
- the launch set as merged in #1367 (`c86d345a`);
- the binding commit as merged in PR #1369 (merge `5702ddbda3e2cc7d49ad922472f1a59270a46c6e`, at the reviewed head `2a675578ef17ee3b4592ff837cbeeb3a33248835`).

The tool commit is **C = `462a0756f7eb20f3a99a4a05c3175ee5f3a7243b`**. The driver tree is M = `77d76cfc2d621f8faa010b75006811868494652a`.
The lane root is **`/pscratch/sd/j/josephrb/evw2d-20261126`**.

| file | sha256 |
|---|---|
| `2d-unfolding/evw2d/evw2d.py` | `6106b23a8b6c5cb9c27acd8480329f6bc180f5c90f9af3ba82a92c9507e64887` |
| `2d-unfolding/evw2d/sbatch_evw2d.sh` | `e56cbc296726dcebc1883c47786e8f36d691729ea2754ef1c64263c0f1bdf2ca` |
| `2d-unfolding/evw2d/config.json` | `bee02d38e8141a8780ba2c838007ebdd0663af1b195f3291ba71239e3f26e7ec` |
| `2d-unfolding/evw2d/references.npz` | `1b21458283c06531c9791efdc1e15f9d685d0733e398288a715768d61b612a03` |
| `launch/bound/evw2d_launch.sh` | `5030063c9a41415587df0642051b6af394b4e8ae966d8cfbde981f053c91cbec` |
| `launch/bound/evw2d_connect.sh` | `0fbc5cc452c9b12f15556f801e630a197e0b08e8654bef58bcd308d25dbd0cd6` |
| `launch/bound/evw2d_post.sh` | `f1d81c63750fbc2eda06bc154900159a617a6f917f12b7ae22dbc20400e4f491` |
| `launch/bound/evw2d_cleanup.sh` | `1fde6803a4e84ad18f5bfab88f56d5fd59b9dc8f2130447d5dee18b443c27cb7` |
| `launch/bound/PINS.txt` | `01960914b16c3e6529e386bf30667f9e720b16ab07b275d104055e194a993558` |
| `launch/fill_pins.sh` | `cf4daf9d9730d61127f57a52a555f2c25b31175b74faedaeea5e52147407c717` |

The `launch/` paths are under `docs/orchestration/state/2d-closeout/evw2d-20261124/`.

## What the director checked

- **C and the pins.** At C, config.json differs from the reviewed `5fdb4c3f` in exactly the four binding fields:
  `lane_root`, `driver_tree.root`, `staging.root` and `declaration_sha256`. evw2d.py, sbatch_evw2d.sh and the
  declaration at C are the reviewed bytes. Each bound launch script differs from its template only in the
  placeholder lines `fill_pins.sh` fills, and no placeholder is left. Each pin equals PINS.txt, hashed by command at
  main after the merge.
- **The scripts, read directly** (sbatch_evw2d.sh, evw2d_connect.sh and evw2d_cleanup.sh, plus the post's gates):
  - **The connect** claims the lane root by `mkdir` and stages the two inputs from CFS on the login node through
    `evw2d.py stage` (O_NOATIME copies, each checked against its pin; nothing is written to CFS). It runs a real
    O_NOATIME open on $SCRATCH, and a ROOT/RDataFrame read of the staged file through `/proc/self/fd/N`. It submits
    with `--hold` and releases only after scontrol shows one record, this job's, with TimeLimit 00:30:00, NumNodes `1`
    or `1-1`, and no array. A lost release reply is resolved by asking again, never by a blind cancel.
  - **The job** repeats the name, node and limit checks. Its first srun step prints only: it records
    `SLURM_JOB_NUM_NODES`, `SLURM_STEP_NUM_NODES`, `SLURM_STEP_ID` and the CPU affinity, and stops unless they are 1
    and 64. Then one 64-CPU step runs `evw2d.py run`.
  - **The post** requires sacct COMPLETED 0:0 on one node, an exact product set equal to its SHA256SUMS, and
    `evw2d.accepted()` bound to the config digest and the job. It publishes `post.pass` last, by rename.
  - **The cleanup** runs only on a matching `post.pass`. It removes exactly the two staged input copies, by their
    exact paths, through `evw2d.py cleanup`, with a deletions.tsv row each. It never removes products, anything
    under out/, or a directory.
- **The reads and checks, as the lane reported them:**
  - for the code: codex-school r1–r4, with confirmations 1–2, ending in "FIX 1 HOLDS", and Sonnet 5.5 r4 GO WITH
    CHANGES. Mutation killed 145/147, and both survivors were later killed by added tests. There are 113 tests;
  - for the launch set: codex-school r1 NO-GO and r1b–r1d each fixed, then r1e ALL HOLD. There are 72 tests, and
    the guards' mutants were 64/64 killed. Two test-only changes at the binding commit are disclosed.
  - One record-checks step (the registry fixtures) passed only on its own rerun, after the shared disk filled up.
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **Bound: connect, then post** (after sacct shows the job terminal), then the fetch of the post receipts. Each runs
   from `launch/bound/`. Any changed byte goes back to the director.
2. **The cleanup is bound but needs its own GO**, given only after the director has reviewed the post's PASS.
3. **The price: about 0.2–0.3 node-h, cap 0.5.** That is one regular CPU node for 30:00, `--no-requeue`, refused if
   0.5 is above half of m3246's balance.
4. **§7's "the launcher's temporaries stay inside the lane" is read as allowing** EVW5D's pattern: a private mktemp
   copy in /dev/shm on the login node, sha-checked there, and deleted by the launcher's wrapper at its exact path.
5. **The purge rule is recorded, not confirmed by command:** exposure is atime + 56 days
   (preservation-20261014/REPORT.md:88), and the post's stat lines record it.
<!-- absence-ok: preconditions checked fresh before each step (a valid certificate, the director's GO), not claims that a result does not exist -->
6. **Preconditions:** a valid NERSC certificate checked by command before each step, with the launcher's margins,
   and no use past expiry. The certificate expires at 2026-11-26T15:19:52Z. If the job is still queued then, the post
   waits for Joseph's renewal. The director's GO must name this binding.
7. **One connect.** Any STOP or refusal after contact is terminal, and nothing is rerun without the director.
8. **The record goes to the director first:** the post's PASS line, accepted(), the exactness gates, the sacct
   charge and the products' SHA256SUMS digest. The HPSS copy and the deposit fetch, if wanted, get a later binding.

**CITABLE FOR:** that EVW2D's run was bound, and on what. **NOT CITABLE FOR:** any weight, cross section, exactness
value, or note wording.
