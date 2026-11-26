# S2R connect stand-ins (Debian, at M = 4017c0825)

`standin.sh` runs the real `s2r_submit.sh` (fa3fbaf7…) or `s2r_fetch.sh` (b5c9f5bc…) inside a Debian container
(`Dockerfile.txt`). `run_standins.sh` starts one container per variant.

**Stubs, and only these:**
- the scheduler tools (sacct, sbatch, scontrol, scancel; each logs its call);
- iris;
- git's clone URL, which becomes a `--shared` clone of the read-only host object store;
- the conda hook (activation sets PATH);
- sha256sum on stdin, for the planted inputs only.

The 3.7 GB of real inputs cannot be planted. Each planted `/pscratch` input instead holds the text
`STANDIN-PIN:<its pin>`, and the stub prints that pin. Every other sha256sum call is the real tool.

A squeue stub records any call; none was made. LightGBM's libgomp comes from scikit-learn's wheel, through
LD_LIBRARY_PATH.

**The filesystem.** `/pscratch` and `/tmp` are per-run Docker named volumes, ext4 on the VM's disk, removed after each
run. A first round bind-mounted host directories. macOS virtiofs moves atime on every read, so the connect's
stat-unmoved pins check STOPped the ok variant there, correctly. An earlier round's binds of /private/tmp landed on
colima's VM root disk and filled it. Neither is a property of the connects.

| variant | expected | result |
|---|---|---|
| submit-ok | rc 0, submitted | rc 0: completed (sbatch, then scontrol; rc 0) |
| submit-fence_running | BAIL, fence | rc 9: BAIL fence (sacct) not clear |
| submit-s2r_pending | BAIL, fence (s2r_) | rc 9: BAIL fence (sacct) not clear |
| submit-out_exists | BAIL, OUT exists | rc 9: BAIL /pscratch/sd/j/josephrb/s2r-20261124 exists |
| submit-low_balance | STOP, balance | rc 9: STOP: the cap 1.0 is above half the balance 1.5 |
| submit-pin_bad | STOP rc 4, pins | rc 4: STOP: the pins check did not pass (logs/pins.tsv) |
| submit-timelimit_bad | STOP rc 6, scancel | rc 6: STOP: TimeLimit 01:30:00 is not 01:00:00, or the job is an array (0); job 7000001 cancelled (rc 0) |
| submit-window_ended | BAIL, window | rc 9: BAIL the window ended (now 1795545080 > 1795545053) |
| fetch-ok | rc 0, tar sums OK | rc 0: completed (tar RECORDS.SHA256SUMS OK, 12 files) |
| fetch-not_completed | BAIL, not COMPLETED | rc 9: BAIL job 7000001 is 's2r_run\|RUNNING', not s2r_run\|COMPLETED |
| fetch-stop_present | BAIL, STOP present | rc 9: BAIL log/ has no clean DONE |
| fetch-sums_bad | STOP, product sums | rc 9: STOP: the products are not log/SHA256SUMS's |
| fetch-extra_product | STOP, 7 products | rc 9: STOP: runs/ does not hold exactly 6 products |
| fetch-no_readout | BAIL, no readout | rc 9: BAIL no readout |

**Every variant:**
- removed the /dev/shm copy of the script;
- made no squeue call;
- wrote nothing under /pscratch outside OUT after the planting. The only entry ever listed is OUT's parent directory, whose
  mtime changes when OUT is created.

In the submit ok variant:
- the bound digests and the declaration (16c7f5fb…) checked;
- `test_s2r.py` ran 58 OK;
- the pins check passed for all 8 inputs, with every stat unmoved;
- `s2r_probe.py limit` gave 1:00:00;
- the Slurm option variables left numbered 0;
- sbatch was called with `--time=01:00:00 --job-name=s2r_run … sbatch_s2r.sh <deploy> <M> <OUT>`;
- scontrol showed TimeLimit 01:00:00 and no array fields.

In the fetch ok variant, the tar's RECORDS.SHA256SUMS checked.
