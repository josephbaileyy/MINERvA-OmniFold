# IBUB connect R under BINDING 1: STOP 5 after sbatch, then job 61914825 cancelled

**By** `director-helper-3`. Connect R ran under the director's GO for IBUB BINDING 1 (#1288, merge `0117ccec`), with
launcher `dc35049b…` and connect `50304275…`, both extracted byte for byte from `0117ccec` and checked by `shasum`. It
ran on login38 with window end 1795570595 (2026-11-25T01:36:35Z, the certificate's expiry).

| step | record |
|---|---|
| launcher start | `launch-start-utc.txt`: 2026-11-24T14:35:22Z |
| connect start (its first `date -u`) | `connect-run.log.txt`: 2026-11-24T14:35:31Z, node login38, script sha256 `50304275…` |
| fences | cov2d rev 3 FENCE CLEAR (14 matching rows); the sacct fence clear, then clear again just before sbatch |
| clone, overlap, preflight, stage | HEAD `db8854e28`, clean, six ibub files OK; overlap CLEAR (1,430 pairs, 0 hits); preflight PASS; stage PASS |
| sbatch | `submitted 61914825 2026-11-24T14:37:08Z`; sacct listed `61914825\|ibub_run\|PENDING` |
| **STOP 5** | `scontrol does not show ibub_run / regular / 11:29:00 for 61914825` |
| records | `fetch-run.tar` sha256 `7e84a86269f79a76ff5c124f40e495fdd864f678fec76721e389224aebb02346` (51,200 bytes), equal to the log's line; RECORDS.SHA256SUMS holds for its 8 files (`records-check.txt`, empty under `--quiet`); `connect-run.done.txt` is 5; launcher rc 5 (`launcher.out.txt`) |
| the cancel | `scancel.out.txt`: one `scancel 61914825` at 2026-11-24T14:39:50Z, rc 0 (the director's ruling (a)) |
| sacct after it | `sacct-after-cancel.txt`, at 2026-11-24T14:40:01Z: `61914825\|ibub_run\|regular_1\|CANCELLED by 112498\|0:0\|None\|2026-11-24T06:39:50`. The job never started (Start None); State was classified in code, with no `-s` filter |

**The cause.** Perlmutter records `--qos=regular` as `QOS=regular_1`. The connect's scontrol record in the tar
(`logs/scontrol-connect-61914825.txt`, sha256 `38043908…`) shows `QOS=regular_1`, and every other checked field as
declared: JobName=ibub_run, TimeLimit=11:29:00, OverSubscribe=NO, StdOut and StdErr in `$N/slurm`. The connect and the
job both required `QOS=regular` exactly. Their stand-in and tests stubbed `QOS=regular`, a spelling the scheduler never
produces. COV2D's records show the same mapping, e.g. `receipts-cov2d/a2/bulk/complete/connect-complete-1.log.txt:78`.
The STOP worked as designed. At its start, the job's own allocation check would have refused (rc 2) before any unit.

**What follows (the director's rulings).** A new M‴ accepts QOS ∈ {regular, regular_1} exactly. Its fixtures follow
the real record, and it uses a fresh `$N`, `/pscratch/sd/j/josephrb/ibub-20261124`, under a new binding. The old
`$N`, `/pscratch/sd/j/josephrb/ibub-20261123` (its deploy, stage/ and logs), is left untouched. Removing it is
Joseph's call, and the director lists it for him.
