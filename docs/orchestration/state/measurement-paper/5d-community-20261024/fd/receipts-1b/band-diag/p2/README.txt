Band diagnosis, P2: the pilot (FD-1B-BAND-DIAGNOSIS-DECLARATION.md sections 4.3, 5 and 7; BINDING-1 rulings 2-5 and
addendum A1). Job 61014446 (fd1b_bdg_p2), one node (nid005738), 2026-11-09T00:13:09–00:40:34Z, elapsed 00:27:25
(1645 s), 0.457 node-h of the 1.5 reserved. Run by limitation-resolver.

RELEASE: the director's go of 2026-11-09 on bdg_p2_login.sh sha256 a59fba1791197ab7e2fc3da607f7b202c1d8af72e54e88af33b4b6b374581335,
and the director's pre-approved go on bdg_p2_post_login.sh sha256 e0b599b362023cc6536898432a67087991ee4fdc03029b2fe31b3e1dc6ad4b09.
Each node compared its digest before running it. The sshproxy certificate was renewed during this step: it is valid
from 2026-11-09T00:10:00Z to 2026-11-10T00:11:04Z (ssh-keygen -L, read locally).

RESULT: P2 PASSES, the inputs read EQUAL, and no source's stat moved.
- Section 4.3, the inputs step (records/p2/inputs.json, sha256 457b256a...): verdict EQUAL.
  - For each of the 8 detector universes, the signal rows (20,403,864) and the background rows (621,445) carry the
    same factor on both sides: n_differ 0 and max_rel_diff 0.0 in every case.
  - The descriptive HW shares are in the record. Out-of-window shares run from -0.0018 to 0.0149 (GEANT_Proton_1); the
    non-positive in-window share is 0 for every universe.
  - The inputs' digests: of_inputs_5d.npz 07fccc1a..., bkg_dump.npz 2addac8f..., pins 5adcd576... The step's own
    atime record lists no moved file.
- Section 7's pilot reading (records/p2/pilot.json): verdict PASS, rc 0.
  - The E and B rebuild controls are bitwise: rebuild_not_bitwise is [] over the 14 items. The new code's E for the 8
    detector universes and CV equals the staged derivation products, and its B for the 4 GEANT_Neutron/GEANT_Proton
    universes and CV equals Part 1's P3 products.
  - Walls PASS: max seconds_unfold 753.834 s (min 649.507) against the unit's 1,370 s; max peak RSS 19,256,560 KiB
    against 44,040,192 KiB.
- Section 5: the 73 sources were re-stat'd after the job (records/p2/logs/stat-post.txt). The result is byte-identical to
  P1's stat-before.txt (sha256 7986e2bf...), as was the re-stat at submission (stat-submit.txt, 00:12:05Z). The
  module's 8 per-lane atime records (records/unf/atime-*.json) list no moved file.
- 14 products in $W/unf, each listed with size and sha256 in post.out (section 6). The npz bytes stay on pscratch.

THE WINDOWS (to the second; job stamps from records/p2/logs/fd1b_bdg_p2_61014446.out, in UTC)
  deploy clone (the only copy made): 00:11:27–00:12:04Z (submit connect, p2.out)
  job start 00:13:09 (sacct); wrapper start 00:13:14.506
  thread probe step: rc 0 at 00:13:28.583
  read window opens: the inputs step starts at 00:13:28.588; inputs step rc 0 at 00:15:37.497
  unfolds: 00:15:37.503 to 00:40:33.871 (packer rc 0; read window closes)
  job end 00:40:34 (sacct)
  post connect: 00:44:00–00:44:04Z (post.out)
  Per step (sacct): the 8 lines ran 12:34 to 24:56 each. The two single-item lanes (lines 4 and 7) took 12:34 and 12:41;
  the two-item lanes took 22:24 to 24:56.

THE THREAD ENVIRONMENT
  The thread variables were unset in the submitting shell and in the job, and they are inherited through
  --export=ALL. The in-lane probe (records/p2/lanes/threadprobe-61014446.log) reads SLURM_CPUS_PER_TASK 32, affinity 32
  and openmp_default_num_threads [32, 32], status ok. That is Part 1's P2/P3 thread environment, as section 5 requires.

THE SUBMIT CONNECT (bdg_p2_login.sh; stdout p2.out, stderr p2.err, the banner only), login27, 00:11:26–00:12:07Z
  - iris: m3246 user 2422.8 of 10000.0, project 18340.4 of 20000.0. Remaining: 7577.2 user and 1659.6 project. The
    9.0 node-h cap is under half of each (3788.6, 829.8).
  - Fence (A1): only fd1b_bdg_*, ll5d_* and prr_* would have been allowed. squeue listed no job, both before anything
    was written and immediately before sbatch.
  - Deploy: a fresh clone at M = 83ac32fb into $W/deploy, HEAD equal, porcelain 0. The module (658ca918), the packer
    (b72aaa62), s5c_array.sh (dd95db5d), mnv_guarded_run.py (30162f57) and setup_salloc_env.sh (ea3c6998, blob
    b4a9c3f6) were gated on their sha256. The packer, s5c and setup bytes are Part 1's.
  - Tools, written and gated (in tools/): bdg_p2_wrapper.sh (d8b9ea68), Part 1's pfd_threadprobe.py unchanged
    (d9369712) and make_bdg_p2_tables.py (3ba4ad30). gen_p2.py generated the connect.
  - Tables (records/p2/tables/): tasks-p2-inputs.tsv, one line; tasks-p2.tsv, 8 lines. The generator imported the module
    from the deploy and confirmed that the 8 lines carry exactly its 14 pilot_items(): E at seed 42, eps 1, both, on CV
    and the 8 detector universes (2, 2, 2, 2, 1 per lane), and B the same on CV and the 4 GEANT_Neutron/GEANT_Proton
    universes (2, 2, 1).
  - sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --time=01:30:00 -J fd1b_bdg_p2: job
    61014446, TimeLimit read back 01:30:00.

THE POST CONNECT (bdg_p2_post_login.sh; stdout post.out, stderr post.err, the banner only), login27
  sacct for every step (all COMPLETED 0:0); the deploy still at M, clean; the inputs verdict; the pilot reading; the
  section 5 re-stat; the product list; and the records tar (45 files; each sha256 on the cluster equals its sha256 here).
  In the committed post.out, the base64 block is replaced by a one-line note giving the decoded tar's sha256
  (6ec927e2...) and the full stdout's (e965b48d...).

WHAT P3 NEEDS (BINDING-1 ruling 2 as addenda A1 and A2)
  - P2's E and B rebuild controls bitwise: met.
  - Section 4.3 EQUAL: met.
  - Walls PASS: met.
  - The re-stat identical: met.
  - Still to come: coverage-5b-audit to see this readout and the P3 table logic; A2 on main; the director's go.

FILES
  bdg_p2_login.sh, p2.out, p2.err, fence-mac.out, survey.txt
  bdg_p2_post_login.sh, post.out, post.err, fence-mac-post.out, survey-post.txt
  tools/: bdg_p2_wrapper.sh, make_bdg_p2_tables.py, pfd_threadprobe.py, gen_p2.py
  records/: p2/tables, p2/logs (the job output, submit records, stat-submit and stat-post), p2/lanes (thread probe,
    inputs and line logs, inventories), p2/inputs.json, p2/pilot.json, unf/atime-*.json
  Digests: SHA256SUMS.txt.
