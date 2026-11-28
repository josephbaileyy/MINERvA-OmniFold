# IBUB BINDING 2: the run (connect R, one job), at M‴, with the QOS fix and a fresh namespace (director, 2026-11-24)

**Supersedes** IBUB BINDING 1 (`IBUB-BINDING-1.md`, #1288). Under binding 1, connect R STOPped with rc 5 after sbatch,
because Perlmutter records `--qos=regular` as `QOS=regular_1` and the connect required `regular` exactly. Job
61914825 was cancelled before it started (Start None), on the director's ruling. The records are on main in #1289
(merge `25367f3c`, `fetch-run.tar` sha256 `7e84a86269f79a76ff5c124f40e495fdd864f678fec76721e389224aebb02346`).

**Authority:** as for binding 1. The declaration is `IBUB-DECLARATION.md` revision 3, sha256
`3aaf07f12b2ebfc747220704d675b752490dc64d42013324f0a42ff45e345262`, unchanged.

**Binds** connect R as merged to main in PR #1292 (merge `3b1fcecd734ce496fda054d2289586f394045ba3`), at the read head
`625282b3815c26ee5c25e7495098a406a899d7af`, merged with `--match-head-commit`. The node clones
**M‴ = `d12c4f2a38a53001eb92bbefc8b2dc6001f034dc`**. The namespace is **`/pscratch/sd/j/josephrb/ibub-20261124`**.

| file | sha256 |
|---|---|
| `fd/receipts-ibub/connect/ibub_run_connect.sh` | `f73494a6699584cd66c1dbf28c010e38f811a555f8e1d92a418d500699c3dc85` |
| `fd/receipts-ibub/connect/ibub_run_launch.sh` | `668ff3f6409383863ac530924e376200da286c5f01c5ba4add5fe73ab08e3642` |
| `fd/receipts-ibub/connect/ibub_run_connect.template.sh` | `70ab88cac2672df3ff94cfe4ccacc44d1ed65fe210d70a8c78a4d172bcb1b427` |
| `fd/receipts-ibub/connect/ibub_run_launch.template.sh` | `998cc6edc74ccdd300e4f34dcf4887cd4631452dc85cad51e9f35db3d25d9173` |
| `fd/receipts-ibub/connect/gen_run_connect.py` | `baaaa8c41dd07099722a54c58bb41a8f66f02465d2d0b2cdabb648d0eb162c0b` |
| `fd/receipts-ibub/connect/overlap-run-d12c4f2a3.txt` | `a7bc0dabb88da6e00036fbd32a784b5415d0c9bf7b3ee601c08a7243c9ebbcb1` |
| `2d-unfolding/ibub/jobs/ibub_job.sbatch` at M‴ | `ab0d7387e7b63605f5091342eea2b1a976b39dda7263b31099309e85c6195518` |
| `2d-unfolding/ibub/ibub_unit.py` at M‴ | `e8e5969f978107e45991164a16c84f1794694dee752cbf189eab00e3ddd54633` |
| `2d-unfolding/ibub/config.json` at M‴ | `bf0838c67ac5c3c0ce375ca7083623d3b44c8007d7de06d30e59ac9f7a02143b` |
| `2d-unfolding/ibub/ibub_lanes.py` at M‴ | `62591f998f6d3c907bcec460c9399a419755d8f041b40652f37066074b3ab85b` |
| `2d-unfolding/ibub/ibub_overlap.py` at M‴ | `507767798ed13edd7c896b0955fcf4090e5dfc0307e0067d9684df2d30c78928` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. The five code files
are byte-identical at M‴ and at the merge.

## What the director checked

- **The shas.** The director hashed each file above from `git show`, at the merge and at M‴, and each equals the
  table. The launcher contains the connect's sha256 exactly once. Neither the connect nor the launcher names the old
  namespace `ibub-20261123`.
- **The regeneration.** In a fresh detached worktree at M‴, `gen_run_connect.py d12c4f2a3…` gives a connect whose
  sha256 is `f73494a6…`, byte for byte the committed one.
- **The delta from M″** (`db8854e28`, binding 1). The director reviewed it directly, with no codex round. The diff
  over the eight changed code paths has sha256 `69afb745…`, rebuilt by the director from git. It touches only:
  - the QOS check, in the job and in the connect, which now accept exactly the set {regular, regular_1}. Anything
    else refuses, and the message names the value and the set;
  - the namespace, `ibub-20261123` → `ibub-20261124`, in the job, the config, the overlap check and both templates;
  - the fixtures. The stubs default to Perlmutter's `QOS=regular_1`, cited to
    `receipts-cov2d/a2/bulk/complete/connect-complete-1.log.txt:78`;
  - the tests and mutants. They cover `regular` accepted, refusals of `regular_2`, `debug`, `regular1` and an empty
    value, and mutants restoring the exact match or widening to `regular*` on each side.

  The PR's diff against main touches only these paths and receipts.
- **The tests.** The director reran `test_ibub_job` at M‴: 31 tests OK. The lane's receipts show 141 tests OK, 103/103
  mutants killed, the stand-in at M‴ 13/13 as expected (`ok` and `qos_regular` rc 0, `qos_other` rc 5), and the
  overlap check CLEAR (1,430 pairs, 0 hits).
- **The other scheduler values.** The connect README tabulates each exactly-matched scheduler field against a real
  committed record. The stated residual: no committed record shows OverSubscribe or AllocTRES on a RUNNING exclusive
  node. If either differs, the job refuses with rc 2 before any unit and names the value.

## Rulings

1. **Connect R is bound** at M‴ with the shas above. Any changed byte goes back to the director.
2. **The price is unchanged:** one exclusive CPU node, regular QOS, `--time=11:29:00`, so at most 11.48 node-h, under
   the declaration's cap of 11.5. Job 61914825 never started and was charged nothing. IBUB stays on CPU, as ruled in
   binding 1.
<!-- absence-ok: preconditions checked fresh before the launch (acks, the old namespace's removal, a valid certificate), not claims that a result does not exist -->
3. **Preconditions, all required, before the launcher runs:**
   - fresh "still true?" acks from cov2d, limitation-resolver and tier3-design, each given after this binding is
     merged, naming the new namespace;
   - the removal of the old namespace `ibub-20261123` has either ended (rc 0 and ENOENT) or not started. It must not
     run while this job is unended, and its own sacct check refuses then. Joseph authorized the removal directly to the
     director on 2026-11-24;
   - a valid NERSC certificate for the connect's ssh, valid to 2026-11-25T01:36:35Z. The job runs regardless of the
     certificate. If the readout falls after the expiry, Joseph renews it;
   - the director's GO, by message, naming this binding.
4. **Disjoint roots.** IBUB writes only `/pscratch/sd/j/josephrb/ibub-20261124`, `/dev/shm/ibub-connect` and the
   launcher's `/dev/shm/ibubc.<pid>.*`. As in binding 1, these are disjoint from RPD-RECO's roots, from tier3-design's
   static roots, and from the planned `s2r-20261124`. `cov2d-run-20261104` is read only, through O_NOATIME. Nothing is
   written to CFS.
5. **The readout (connect O) is not bound here.** The rulings of binding 1, ruling 5, carry over unchanged. The
   readout's `allocation_ok` uses the same QOS set.
6. **Any STOP or guard refusal after contact is terminal.** It is reported, and nothing is resubmitted without the
   director's word.
7. **Next:** the acks, then GO, the launcher, the job by sacct (never squeue) to its end, and a records PR.

**CITABLE FOR:** that IBUB's run was bound at M‴, and on what. **NOT CITABLE FOR:** any IBUB result, any note wording.
