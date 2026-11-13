# RPD-RECO flux connect 1: the run, job 61206960 (2026-11-13)

**By** the limitation-resolver lane, on the director's go of 2026-11-13 under RPD-RECO-BINDING-2 (flux connect 1 at
M_F1 678b1ddc). The go named these shas:
- connect `34694c0d`;
- launcher `8354aece`;
- fetch `dfade48a`;
- job `4198103b`;
- config `cde8d029`.

The bound was shared QOS, at most 0.094 node-h, finished before cov2d's `atime-around.sh pre` (about 04:30Z), or held
if it could not be done by about 04:00Z. The code and its tests are in [`../README.md`](../README.md) (revision 4).

**Result: COMPLETED, rc 0, in 4 min 13 s.**
- `flux-extract` PASS, with 12 factor products, one per playlist (1A–1G, 1L–1P). Each product's sha256 equals the one
  `flux-extract.json` records. The products stay on pscratch and are not sent (F1).
- Protected read PASS. The NuE constraint's stat is equal before and after, in all five fields.
- C3 PASS and the redaction check PASS.
- The job removed its `/dev/shm` directory.

## Before the connect (all on 2026-11-13, UTC)

| step | time | result |
|---|---|---|
| shas | 01:41Z | Each of connect, launcher, fetch and config was taken from `main`'s bytes and matched the go. The job script, extracted from the connect's heredoc, is `4198103b…`. `cov2d_fence.sh` is `16a2a5cd…`. |
| certificate | 01:40Z | Valid from 2026-11-12T18:26:00 to 2026-11-13T18:27:04 (`ssh-keygen -L`, read only). |
| survey | 01:41:51Z | [`survey/`](survey/). login05, 06, 08, 09 and 10 answered, and the root was absent on each. login07 printed nothing. login06 had the lowest load (31). |
| announcement | before 01:42Z | rpd_flux1 was announced to cov2d and director-helper-2, and both acknowledged. cov2d's pre waits until sacct shows rpd_flux1 ended. helper-2 confirmed the job reads none of E96D's three inputs (see "Staged originals"). |
| fence | 01:42:12Z | [`fence/`](fence/). `cov2d_fence.sh` gave FENCE CLEAR. The queue held only E96D's `e96data_full` 61202343, PENDING. |

## The connect (login06, 01:42:26Z to 01:43:03Z): [`connect/`](connect/)

- **Clone:** at `763ab4dd`, porcelain 0, and all 11 pins equal.
- **Config:** `cde8d029…`.
- **Overlap fence** (`fence_overlap.py`, `baa76309…`): 30 protected paths and 57 staged originals. CLEAR, with 1
  allowed (the NuE constraint) and 0 stops.
- **Job:** script `4198103b…`, then `sbatch`. It gave job 61206960 at 01:43:03Z.
- **scontrol:** `JobName=rpd_flux1`, `TimeLimit=03:00:00`, `QOS=shared`, `Account=m3246`, `MinMemoryNode=16G`. The
  partition is `shared_milan_ss11`.

**CPUs: Slurm allotted 9 to 10 CPUs for the 16G request, while the 0.094 node-h bound assumed 4.**
- scontrol showed `NumCPUs=9` while the job was pending.
- The job's environment had `SLURM_CPUS_PER_TASK=9` and `SLURM_JOB_CPUS_PER_NODE=10`.
- sacct's AllocCPUS is 10.

At 10 of 256 CPU threads, a full 3 h would have cost about 0.117 node-h, which is over the bound. The 04:00Z hard stop
(approved by the director) capped it below the bound. The job took 253 s, about 0.0027 node-h at 10/256. Even if the
whole node were charged, it would be about 0.070 node-h. **A later rerun of this job needs its bound re-priced at the
allotted CPUs first** (director, 2026-11-13).

## The job (nid004089): [`records/`](records/)

sacct gives:

    61206960|rpd_flux1|COMPLETED|0:0|00:04:13|2026-11-12T17:56:02|2026-11-12T18:00:15|nid004089||10|16G|03:00:00

Perlmutter prints local time (PST). In UTC that is 01:56:02Z to 02:00:15Z.

`job-host.txt` and `job.rc` record start 01:56:05Z, end 02:00:14Z, `rc=0 cause=exit`.

`job.out` shows the job's own steps:
- the 11 pins rechecked on the `/dev/shm` copy;
- config `cde8d029…`;
- strace probe rc 0;
- the pgid check: wrapper pid 20565 equals its process group;
- wrapper rc 0;
- `removed /dev/shm/limres-rpd-flux1 rc=0`.

`connect.log` records #848's wrapper, in order:
1. MAT setup: 6 scripts, 0 mismatches, exit 0.
2. The real-MnvH1D check: PASS, worker exit 0.
3. Custody `prepare`.
4. The missing-dependency check: PASS. `run/missing-dependency-check.json` withholds the staged NuE copy and expects
   `MAT_DATA_STAGE`. The child stopped with exactly that guard (rc 4), and its trace check passed.
   `run/missing-dependency.STOP.json` is that control's expected STOP record. The run did not stop there.
5. `flux-extract`: `{"dry_run": false, "status": "PASS"}`. FluxReweighter opened only the staged flux files under
   `run/mat-data`.
6. `trace-check`.

`run/cov2d-fence.json`, custody's own COV2D fence: PASS. Its squeue showed only 61202343 (PENDING) and 61206960 itself.

## The protected read (cov2d's condition): `records/protected-read.json`

| field | value |
|---|---|
| exception as listed | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` |
| resolved | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` |
| staging window | 2026-11-13T01:58:22.004832Z to 01:58:22.010592Z |
| stat_before = stat_after | device 3592384858, inode 882722362129162055, bytes 25403, mtime_ns 1630424966000000000 (2021-08-31T15:49:26Z), atime_ns 1793891894000000000 (2026-11-05T15:18:14Z) |
| sha256, prepare's and both staged copies' | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` |
| staged originals overlapping a protected path | that file only |

`records/exception-stat-outer.txt` shows the same five fields at 01:57:16Z, before the wrapper, and at 02:00:14Z,
after it. The atime did not move. These were sent to cov2d at 02:06Z, before its pre.

## Staged originals: [`staged-originals.txt`](staged-originals.txt)

The list holds 54 originals with their sha256, taken from the `files` of `run/prestage.json` as the fetch sent it. By
directory:
- 24 dumps from `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps`;
- 14 MAT flux and reweight files from `minerva_large_files/MATFluxAndReweightFiles`;
- the NuE constraint;
- 10 MAT and setup files under `/pscratch/sd/j/josephrb/MINERvA-OmniFold`;
- 5 files from the job's `/dev/shm` repository copy.

Search: `grep -E 's5p-20260926|of_inputs_5d|bkg_dump|data_b-' staged-originals.txt` returns nothing (rc 1).
<!-- absence-ok: a grep over the committed list, stated with its command -->
So none of E96D's three inputs was staged. Those inputs are `of_inputs_5d.npz`, `bkg_dump.npz`, and
`s5p-20260926/runs/s2/num/data/data_b-_j-.npz`, the last per helper-2. The first two are among cov2d's protected
paths, which the overlap fence cleared.

The fence counted 57 originals before the run, and prepare staged 54. This receipt does not establish which three
make the difference. The fence computes the MAT originals from prologue 5's recorded prefixes, and the job takes its
prefixes from the pinned setup at run time (f2 in [`../README.md`](../README.md) section 7). The protected read is the
post-run backstop over the 54 originals prepare actually listed, and it PASSed.

**`run/prestage.json` is held out of git.** It was sent, with sha256
`99528ac8e1d2cc918cde01db73f0ba946e7ff3b473ce09fc614e24615772d3b7` and 249,294 bytes. Its `dump_listing` names other
files in the dump directory bare (`nn_1A.npz` to `nn_1P.npz`), and the receipt-artifact hook reads those names as
missing deliverables. The lanes' rule for such a record is to keep it out of git and list it by sha256. The original stays
in the run directory on pscratch until the post-merge deletion. `staged-originals.txt` carries its `files` content.

## The fetch (login06): [`fetch1/`](fetch1/), [`fetch2/`](fetch2/)

| fetch | time | result |
|---|---|---|
| `fetch1` | 01:44:07Z | NOT FINISHED (PENDING), rc 10, nothing written |
| `fetch2` | 02:04:14Z to 02:04:32Z | rc 0 |

`fetch2` reported:
- 12 products recorded, 0 differing;
- protected read PASS;
- C3 PASS;
- redaction check PASS: view NONE, and 0 fingerprint values in each of the 31 files it read;
- 30 files sent, 10,090,961 bytes.

The sent files, untarred, are `records/`, except `run/prestage.json` (see "Staged originals"). `c3-check.txt` and `redaction-check.txt` were written by the fetch itself.

`fetch2/session.notar.out` is the session output with its base64 tar block replaced by one line, because `records/`
holds those files. The full `session.out` had sha256 `fc8d505890de9339204b8df32ab98543c21cd7e4c73b9fadee028e9965fdcd41`
(13,752,087 bytes).

[`poll.out`](poll.out) is the Mac-side poll that ran the two fetches.

## Left on pscratch

The root `/pscratch/sd/j/josephrb/rpd-reco-flux-20261111` stays in place: the 12 factor products, the staged copies,
the clone and the private record. They are deleted after this receipt merges, by a separate connect under a ledger
row.

Nothing is submitted, deposited or tagged.
<!-- absence-ok: the document's own status line -->
