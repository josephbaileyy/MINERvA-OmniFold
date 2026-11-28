# IBUB BINDING 1: the run (connect R, one job), at M″ (director, 2026-11-24)

**Authority:** Joseph via the director: Ben's (a), assigned to director-helper-3 on 2026-11-23. The declaration is
`IBUB-DECLARATION.md` revision 3, sha256 `3aaf07f12b2ebfc747220704d675b752490dc64d42013324f0a42ff45e345262`,
accepted by the director on 2026-11-23.

**Binds** connect R as merged to main in PR #1287 (merge `16c798f9cb239ba80672b941e6b9d6d20b61cad6`), at the read head
`a463cbf08290ac75d3de782be2c4fc15d70d5b15`, merged with `--match-head-commit`. The node clones
**M″ = `db8854e286f6ce4a976e0d603b43454674fc9129`**.

| file | sha256 |
|---|---|
| `fd/receipts-ibub/connect/ibub_run_connect.sh` | `503042750285daf08ab5cf1ca85c4b3b2db58a4ba5f6b961c3ece54c232e1d18` |
| `fd/receipts-ibub/connect/ibub_run_launch.sh` | `dc35049b8b225a79903fde72b53ee4fd046c6145adfb25c4daaeae473472f125` |
| `fd/receipts-ibub/connect/ibub_run_connect.template.sh` | `3224d2f0f97c4c1d1f7f6f6f981e963ffbc5ebd6bbff29ca171f4181aa7d1fcc` |
| `fd/receipts-ibub/connect/ibub_run_launch.template.sh` | `a87d8c8de2e1d9edd15e0d426de79076b8ddee8a2f992cf5e2a6e5b69f9906a8` |
| `fd/receipts-ibub/connect/gen_run_connect.py` | `baaaa8c41dd07099722a54c58bb41a8f66f02465d2d0b2cdabb648d0eb162c0b` |
| `fd/receipts-ibub/connect/overlap-run-db8854e28.txt` | `a7bc0dabb88da6e00036fbd32a784b5415d0c9bf7b3ee601c08a7243c9ebbcb1` |
| `2d-unfolding/ibub/jobs/ibub_job.sbatch` at M″ | `5e8e0abf0aa4e85907f00e568db1e8468face153655f4723db801504c05bfc55` |
| `2d-unfolding/ibub/ibub_unit.py` at M″ | `e8e5969f978107e45991164a16c84f1794694dee752cbf189eab00e3ddd54633` |
| `2d-unfolding/ibub/config.json` at M″ | `8f1900e43d20cbc7b6dabb73e0419314bd6c0456b485d13b91afa450ed6ddb2e` |
| `2d-unfolding/ibub/ibub_lanes.py` at M″ | `62591f998f6d3c907bcec460c9399a419755d8f041b40652f37066074b3ab85b` |
| `2d-unfolding/ibub/ibub_overlap.py` at M″ | `13316a39994057d21e72fe4243e89e6ba8b0fb6f65db54b6325947eff48e4e78` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. The five code files
are byte-identical at M″ and at the merge.

## What the director checked

- **The shas.** The director hashed each file above from `git show`, at the merge and at M″, and each equals the
  table. The launcher contains the connect's sha256 exactly once.
- **The regeneration.** In a fresh detached worktree at M″, `gen_run_connect.py db8854e28…` gives a connect whose
  sha256 is `50304275…`, byte for byte the committed one.
- **The delta after the last codex-school2 read.** The item-3 confirm read M′ = `1230e29a8` and found one blocker:
  the connect and the batch both wrote `$N/logs/scontrol-$jid.txt`. It also found `--error` unpinned. The director
  reviewed the fix directly, with no further codex round. The diff `1230e29a8..db8854e28` over the four changed code
  files has sha256 `5a2a024b…` and was rebuilt by the director from git. It touches only:
  - the batch's record, now `scontrol-batch-<id>.txt`, and the StdErr check (`in_sd`);
  - the connect's record, now `scontrol-connect-<id>.txt`, checked fresh and written under noclobber, with
    `--error` pinned beside `--output` in `$N/slurm`;
  - the tests and mutants for each ordering.

  No live reference to the old name remains. The connect's `records()` copies `logs/` by `find`, not by name.
- **The tests.** The director reran `test_ibub_job` at M″: 29 tests OK, porcelain empty. The lane's receipts at the
  head show 139 tests OK, 99/99 mutants killed, the stand-in at M″ 11/11 as expected, and the overlap check CLEAR
  (1,430 pairs, 0 hits).
- **No squeue.** The fences are sacct only.

## Rulings

1. **Connect R is bound** at M″ with the shas above. Any changed byte goes back to the director.
2. **The price:** one exclusive CPU node, regular QOS, `--time=11:29:00`, so at most 11.48 node-h. The declaration's
   cap is 11.5 node-h. Nothing reruns without the director.
   - The CPU-only rule is relaxed for every job (Joseph, 2026-11-24). IBUB stays on its CPU node on the merits: the
     code is bound, and the price and checks were made for that node.
   - The committed iris receipt (#1276, 2026-11-24T06:55Z) shows 630.4 CPU node-h left in m3246. This job's cap is
     under 2% of that, far below the half-balance threshold for Joseph.
<!-- absence-ok: preconditions checked fresh before the launch (acks, a valid certificate), not claims that a result does not exist -->
3. **Preconditions, all required, before the launcher runs:**
   - fresh "still true?" acks from cov2d, limitation-resolver and tier3-design, each given after this binding is
     merged;
   - a valid NERSC certificate for the connect's ssh. It is valid to 2026-11-25T01:36:35Z. The job itself runs
     regardless of the certificate, and if the readout falls after the expiry, Joseph renews it;
   - the director's GO, by message, naming this binding.
4. **Disjoint roots.** IBUB writes only `/pscratch/sd/j/josephrb/ibub-20261123`, `/dev/shm/ibub-connect` and the
   launcher's `/dev/shm/ibubc.<pid>.*`. These are disjoint from:
   - RPD-RECO P0's write roots (`rpd-reco-p0-20261123`, `/dev/shm/limres-rpd-flux1`). P0 is DONE, and its records are
     merged in #1273;
   - the d2s0 chain (`rpd-reco-d2s0-20261124`), whose STOP records are merged in #1284;
   - tier3-design's static root `q0study-20261124`.

   `cov2d-run-20261104` is read only, through O_NOATIME, and has no HPSS copy. Nothing is written to CFS.
5. **The readout (connect O) is not bound here.** It comes to the director as its own package, with its own confirm
   and binding, carrying codex-school2 read 3's items 1, 2 and 4 and `--job-m`. The director's rulings of
   2026-11-24 go into that package:
   - C-COMPLETE is graded per tune, as declared. The job-wide prerequisites come first, and the job's terminal state
     is disclosed, never a gate. This supersedes connect O precondition 2 in the connect README, which required the
     job's IBUB-DONE to read completion PASS;
   - the readout reads nothing until sacct shows the job terminal;
   - the allocation is re-checked from the batch's scontrol record;
   - every graded byte is inventoried by O_NOATIME sha256.
6. **Any STOP or guard refusal after contact is terminal.** It is reported, and nothing is resubmitted without the
   director's word. That includes the connect's post-sbatch STOP 5s, which leave the job running.
7. **Next:** the acks, GO, the launcher, then the job by sacct (never squeue) to its end, and a records PR.

**CITABLE FOR:** that IBUB's run was bound, and on what. **NOT CITABLE FOR:** any IBUB result, any note wording.
