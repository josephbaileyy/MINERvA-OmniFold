# rpd_flux4, job 62051670: the run's records (2026-11-26)

**By** limitation-resolver, under [`../RPD-FLUX4-BINDING.md`](../RPD-FLUX4-BINDING.md) (#1397, merged 7756f35d), for
RPD-RECO amendment 1 ([`FD-RPD-RECO-DECLARATION-AMENDMENT-1.md`](../../../../FD-RPD-RECO-DECLARATION-AMENDMENT-1.md)).
This is the flux rerun with true Eν from the RDX truthx sidecar. It is C-JOIN part 1. The package is
[`../README.md`](../README.md) (#1395).

**Result: COMPLETED, rc 0, in 9 min 17 s, 0.0060 node-h.** The step-2 products are recorded with 12 of 12 equal,
**TRUE_ENERGY RECORD: PASS** (step 2b), and **PROTECTED READ: PASS**. The NuE constraint's outer stat before and after is
identical. The director accepted the run on 2026-11-26. The products stay on pscratch.

- **CITABLE FOR:** flux4's factor products' sha256, the true-energy join record (C-JOIN part 1), and the run's custody
  records.
- **NOT CITABLE FOR:** any RPD-RECO result, or C-JOIN part 2, P0 READY or C-E3. Each is bound separately. Amendment 1
  §4 says no flux4 product reaches a control or a reading before part 2 passes in P0.

## Preconditions (the binding)

- **The bound files.** The launch ran from a worktree detached at 7756f35d. The six bound files hashed there to the
  binding's values:
  - config `f53a86f6…`;
  - connect `89898150…`;
  - fetch `4da3ee5e…`;
  - launch `70c64e0c…`;
  - `tools/fence_overlap.py` `1371a21a…`;
  - `tools/gen_flux4.py` `73d02cd0…`.
- **The cert check.** `TZ=UTC ssh-keygen -L` read the cert as valid from 2026-11-26T14:21:00 to 2026-11-27T14:22:19
  (checked at 20:39:27Z). The launcher read the same end time.
- **The three-lane ack file.** cov2d, tier3-design and minerva-lib each acked the fence round. Their replies are verbatim
  in [`acks/`](acks/).
  - [`connect/ack.txt`](connect/ack.txt) (sha256 `5e617216…`) carries the three `ACK-UTC` lines in the order the
    launcher requires. Below them is limitation-resolver's one-line summary of each reply, not the replies' text.
  - The launcher read the acks at ages 18 s (cov2d), 71 s (tier3-design) and 68 s (minerva-lib), then copied the file
    byte for byte into the session.
  - **cov2d** (20:40:37Z): no-objection to the NuE exception on flux3's terms. No atime bracket or watch of cov2d's
    covers the NuE file or the lane, nothing was queued or running, and no NERSC action before END.
  - **tier3-design** (20:39:44Z): no job reading the sidecar, the omnifiles or the flux3 inputs. It plans no
    move or regeneration of the RDX outputs.
  - **minerva-lib** (20:39:47Z): no geanttw_ job queued or running. It chose option (a) and held geanttw's check re-run
    (three login-node connects, no Slurm job) until END.
- **ibu-chi** opened an OOFVC fence round during the job. limitation-resolver acked it on one condition: no oofvc_ job
  and no NuE read before this run's END. ibu-chi accepted, and nothing of OOFVC was bound at the time.
- **END** went to all four lanes at 20:57Z, after the fetch.

## The connect: [`connect/`](connect/) (login02, 20:40:55Z to 20:42:31Z)

The launcher ran with a new empty session directory, and its output is
[`connect/launcher.out.txt`](connect/launcher.out.txt). ssh rc 0, script rc 0.

- `node login02 staged sha256 89898150…`, the bound connect.
- **Step 2, the sacct fence:** `sacct rows (14 days): 126; cov2d/t2a/rpd/geanttw rows: 19`, `FENCE: clear`.
- **Step 3, the fresh clone:** `HEAD 2415e8d66d1a9160e724d426eaeb54d458d4b4f7; porcelain lines 0`, with the 14 pin
  shas. These include `fd_rpd_reco.py` `12f68102`, custody `6428dead`, `test_fd_rpd_reco.py` `eee5ae4c` and
  `fd_rpd_reco_mutation.py` `8dfdeaf1`.
- **Step 4, the config:** `sha256 f53a86f6… (expected f53a86f6…)`.
- **Step 5, the overlap fence:** `FENCE protected paths 36`, `staged originals 58`, the one allowed exception (the MAT
  MParamFiles NuE constraint), and `FENCE OVERLAP: CLEAR (allowed 1, stops 0)`.
- **Step 5b, the sidecar, by stat only:** `sidecar regular file|2364943114`.
- **Step 6, the job:** job script sha256 `2befd8c2…`, `sbatch rc=0 jobid [62051670] 2026-11-26T20:42:29Z`.
- **scontrol:** JobName=rpd_flux4, Account=m3246, QOS=shared, TimeLimit=01:00:00, Partition=shared_milan_ss11,
  NumNodes=1-1, NumCPUs=9, MinMemoryNode=16G. 16G on the shared QOS gives 9 CPUs, as it did for flux1, flux2 and
  flux3.

## The job (`records/`)

The job waited about 1.5 minutes. It ran on nid004076 from 20:43:57Z to 20:53:11Z, and `job.rc` reads
`rc=0 cause=exit`.

- **sacct** (from the fetch): `62051670|rpd_flux4|COMPLETED|0:0|00:09:17|2026-11-26T12:43:55|2026-11-26T12:53:12|nid004076||10|16G|01:00:00`.
- **The charge:** 557 s at AllocCPUS 10 of 256 is 557 × 10 / (3600 × 256) = **0.0060 node-h**. The basis is flux3's
  ruling 3. The binding expected about 0.0076, with a ceiling of 0.039.
- **The watch:** [`watch/sacct-watch.txt`](watch/sacct-watch.txt) holds the read-only `sacct -X` polls from saul, about
  every 3 minutes, from PENDING to COMPLETED.
- **`job.out`:** shows the following on the node:
  - the copy at HEAD 2415e8d6, porcelain 0;
  - the 14 pins and config f53a86f6, rechecked;
  - `strace probe rc=0`, `wrapper rc=0`, `removed /dev/shm/limres-rpd-flux1 rc=0`.
- **`connect.log`** (the wrapper) records:
  - MAT setup with 6 scripts and 0 mismatches;
  - the real-MnvH1D check PASS;
  - custody prepare;
  - the missing-dependency check (below);
  - `flux-extract` PASS, with `dry_run` false.

  Each `FRW:` flux file MAT opened is a staged copy under the run's `mat-data/`.
- **`exception-stat-outer.txt`:** the NuE constraint's stat at 20:45:30Z and at 20:53:11Z is identical, including
  atime_ns 1795710429000000000.
- **`protected-read.json`:** PASS, `problems` empty. It records one stat-bracketed staging with two O_NOATIME reads
  (20:46:21.1315Z to 20:46:21.1368Z).
  - The original resolves to `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
  - Its sha256 measured by prepare is `e38ad7d2…`, and both staged copies are `e38ad7d2…`.
  - Its own stat before and after are identical.
  - `staged_originals` is 55. Only the NuE file overlaps a protected path.

## The custody and extract records

- **The extract.** `run/flux-extract.json` records:
  - schema `fd-rpd-reco-flux-extract/2`, status PASS;
  - code_sha256 `12f68102…`, the pinned `fd_rpd_reco.py`;
  - `config_sha256_at_extraction` `8ca399b7…`, which is `run/extract-config.json`;
  - `selection_sha256` = `75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8`. This is the same value as
    flux2's and flux3's.
- **The custody binding.** `run/flux-custody.json`, status PASS, records:
  - `custody_code_sha256` `6428dead…`, the pinned custody;
  - `code_sha256` `12f68102…`;
  - `extract_sha256` `060d4401…`, equal to the fetched `flux-extract.json`.
- **The custody fence ran sacct only.** `run/cov2d-fence.json` records status PASS:
  - `sacct_named` `-j 60909280,60911676`, both COMPLETED;
  - `sacct_family` from 2026-11-12T12:46:05, 119 rows, 14 of them cov2d/t2a.

  No file in `records/` contains the string `squeue`.
- **The true_energy config block.** It is present in `run/original-config.json` (the bound `f53a86f6`) and in
  `run/extract-config.json`, with keys path, sha256, npz_sha256 and omnifiles.

## The factor products (step 2)

The fetch printed all 12 sha256 (1A `8b8e3e55…` through 1P `a2db271d…`). Each equals the value `flux-extract.json`
records: "factor products recorded 12 differing 0". The products stay on pscratch under the run root.

**Against flux3's products.**
- The file sha256 differ for all 12.
- For each playlist, `rows`, `signal_sha256` and `zero_patterns` equal flux3's.

This is the change amendment 1 makes. The product's `energy` column is now true Eν from the sidecar (§1). At S, `fd_rpd_reco.py:1912`
takes `energies` from `true_energies` (`:2181`), and the writer at `:1959-1984` stores `energies[playlist]` as
`energy`. flux3's step-2b identity check is therefore replaced by the true-energy
record below. P0's C-JOIN part 2 checks the `energy` column at the spot rows bitwise.

## Step 2b: the true-energy join record (C-JOIN part 1)

`TRUE_ENERGY RECORD: PASS`, check rc 0. `run/flux-extract.json`'s `true_energy` block records:

- status PASS and units GeV;
- the source: path `rdx-20261112b/out/dumps/truthx_RDX_ALL.npz`, sha256 `641ba34c…` (the bound value), schema
  `rdx-truthx-sidecar/1`, 32,846,302 rows, and npz_sha256 `6ca02c3d…` (lat_zero's);
- spot_seed `[20261124, 17]`;
- 66 spots per playlist;
- the overall median of 6.4801 GeV, inside its band [1, 50] GeV.

| playlist | rows | median (GeV) |
|---|---|---|
| 1A | 2,682,038 | 6.4808 |
| 1B | 721,015 | 6.4818 |
| 1C | 1,376,711 | 6.4798 |
| 1D | 4,003,313 | 6.4818 |
| 1E | 3,349,741 | 6.4783 |
| 1F | 4,659,798 | 6.4800 |
| 1G | 3,922,426 | 6.4801 |
| 1L | 383,815 | 6.4795 |
| 1M | 5,916,895 | 6.4803 |
| 1N | 3,415,958 | 6.4799 |
| 1O | 1,041,993 | 6.4816 |
| 1P | 1,372,599 | 6.4756 |

The rows sum to 32,846,302, the sidecar's row count.

## The staged originals: [`staged-originals.txt`](staged-originals.txt)

The file holds the 55 staged originals, paths and sha256, taken from `run/prestage.json`'s `files` in their recorded
order.
- 54 are identical, line for line, to flux3's `../../flux3-20261123/run-61861637/staged-originals.txt`.
- The one added line is the sidecar, `641ba34c…`.

The sidecar's staging stat before and after is identical. Its atime_ns is 1794937529000000000 (2026-11-17T17:45:29Z),
so the O_NOATIME staging left its atime, and its purge exposure, unchanged.

The fence's 58 is the length of the list `tools/fence_overlap.py` builds from the config's keys. `prestage.json`
records 55 distinct staged files. The gap of 3 is the same as flux3's (57 against 54), and the sidecar is the one
addition to both counts. This run did not establish which list entries account for the gap.

## `run/missing-dependency.STOP.json`: an expected STOP, by design

This is the custody negative control described in flux2's and flux3's run READMEs. The extract must refuse with guard
`MAT_DATA_STAGE` when the staged NuE constraint is withheld.

- `run/missing-dependency-check.json` reads PASS, with expected guard MAT_DATA_STAGE and returncode 4.
- The STOP file has guard MAT_DATA_STAGE and code_sha256 `12f68102…`.

The real `flux-extract` ran after the control and ended PASS.

## The fetch: [`fetch/`](fetch/) (login02, 20:55:42Z to 20:56:05Z, bound fetch `4da3ee5e…`)

The fetch ran once, after sacct showed COMPLETED. It reported `state [COMPLETED]`, `job.rc` present, script rc 0 and
launcher rc 0. It also reported:

- the 12 products recorded, 0 differing;
- `TRUE_ENERGY RECORD: PASS`;
- the protected read PASS;
- C3 PASS: the private record at `.rpd-private/70d7e91f…/prestage.json` has sha256 `7348291d…`, equal to its
  reference. It is owner-only and the only entry;
- the redaction check PASS: view NONE, with 0 fingerprint values in each file read;
- 30 files sent, 10,240,263 bytes;
- `TAR END tar rc=0 base64 rc=0`.

The tar's 32 entries are all plain relative paths. Untarred locally, every sent file and the two check outputs (32 in
all) matched their printed sha256.

`fetch/session.notar.out` and `fetch/launcher.notar.out.txt` are the session and launcher outputs with the base64 tar
block replaced by one line, because `records/` holds those files. The full files had these sha256:
- `session.out`: `d2557d176b10a651eb392e914a80db8fc6b0f222dac609f21ec066ebafebe876`;
- the launcher output: `aa9f040e75ad39b5b7648fab679a96fc0c6d1cc468e769ed930c978ac707a9a1`.

**`run/prestage.json` is held out of git, as in flux1, flux2 and flux3.** It was sent with sha256
`6371e88ac5a6e099bdc7c3c074996a930d3b786c8a75ea2a81d5d910d110856e` and 254,536 bytes. Its `files` content is in
`staged-originals.txt`. The original stays in the run directory on pscratch until the deletion step.

## Left on pscratch

`/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126` holds:
- the factor products;
- the staged copies, including the 2.36 GB sidecar copy;
- the clone;
- the private record.

The director's instruction is to leave it until these receipts merge. Deleting it then goes through the director, under
flux3's precedent. P0 reads the factor products from there under its own binding.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
