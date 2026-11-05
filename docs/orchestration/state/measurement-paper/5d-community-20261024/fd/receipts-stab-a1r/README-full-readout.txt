Receipts of the FD-STAB (B4) FULL RUN and its READOUT, under FD-STAB-BINDING-2.md (#771, main a1c8bb30), at M_A1 =
cc54d86f7ac66c1346fa69e5894b2d2f000fb09c. Copied by limitation-resolver on 2026-11-05 with O_NOATIME reads from
$OUT = /pscratch/sd/j/josephrb/fd-stab-a1r-20261104 (the 375 task records as one O_NOATIME tar stream). Full sha256 of
every file: SHA256SUMS-full-readout.txt. The dry run's receipts are the files beside these (README.txt, #770).

full/
  DONE                    {"mode": "full", "tasks": 128, "ended": 128, "rc": 0, "job": "60837713"} (sha256 45765745...)
  SHA256SUMS              the job's own pin of its 280 products (sha256 e2c35e55...)
  sacct-60837713.txt      COMPLETED 0:0, TimeLimit 07:15:00, Elapsed 04:34:07 (16,447 s), 1 node: 4.5686 node-h.
                          Probe total 0.0203 (60826464, INVALID) + 0.2756 (60827080) + 4.5686 = 4.8645 of the 8.0 cap.
  fd_stab_full_60837713.out   the job's Slurm output; env.log the job's environment log
  connect-full.log/.done, submit-full.out, stab_full_a1r_submit.sh (64166c6b...): the connect as run on login31; it prints
                          "charged_node_h=0.2958 remainder_node_h=7.7042 gate_cap=7.2500 time_limit=07:15:00" and
                          "scontrol TimeLimit=07:15:00 (declared 07:15:00)"
  records/tasks/*.time    the 119 GNU time records of the tasks this job ran (all "Exit status: 0"); the other 9 are the
                          dry run's (dry/tasks/), skipped by the gate
  records/*.start, *.end  the 128 gate start and end epochs (the dry run's nine copied in by the job)

readout/
  first-attempt-stop/     the first readout (stab_readout_a1r.sh, e8c0530d...): rc 9 before the analyzer ran, "STOP:
                          deploy-full is not clean"; no record was written. deploy-full-ignored.txt lists the three
                          --ignored entries (2d-unfolding/, nd-unfolding/ and nd-unfolding/pv-ladder/ __pycache__/),
                          written by the full-run job while it ran; no tracked file changed (--untracked-files=no: 0).
                          The director's ruling (a): rerun from a fresh clone; deploy-full and readout/ left as they are.
  readout-2/              the rerun (stab_readout2_a1r.sh, c9086a33...) on login04, 10:18:05-10:18:44Z: a fresh clean
                          clone at M_A1 (deploy-readout), porcelain --ignored 0 before and 0 after, the 7 bound blobs
                          verified, then FD-STAB-DECLARATION.md §7's command: analyze rc 0. fd_stab.json (sha256
                          653356ae56087ea74621e61a60c829d63be9a9f15b0b35941e641b22f0be8ea3) is the probe's record;
                          readout.log, readout.done, clone.log.

A KNOWN PROPERTY OF THE BOUND JOB SCRIPT (the director, 2026-11-05; no change now): sbatch_fd_stab.sh (blob 9defbb44)
runs python3 without -B, so the job writes bytecode caches (__pycache__/) into its deploy while it runs. Its own
cleanliness check, `git status --porcelain --untracked-files=no`, does not see them; a later `--ignored` check does.

The record's reading is not stated here. The director reads it first, and adoption is Joseph's (binding 2 ruling 6).
