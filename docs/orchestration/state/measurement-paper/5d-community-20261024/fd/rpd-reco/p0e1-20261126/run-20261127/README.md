# rpd_p0 for e1, 2026-11-27 (login02): P0's records

**By** limitation-resolver, under [`../RPD-P0E1-BINDING.md`](../RPD-P0E1-BINDING.md) (#1407, merged 81ff0d93), for
RPD-RECO amendment 1 ([`FD-RPD-RECO-DECLARATION-AMENDMENT-1.md`](../../../../FD-RPD-RECO-DECLARATION-AMENDMENT-1.md)).
The package is [`../README.md`](../README.md) (#1406).

**Result: DONE, `p0.rc` = `rc=0 cause=exit`.**
- All four steps (`pins --dry-run`, `p0 --dry-run`, `pins`, `p0`) ended PASS under the supervisor. The chain took
  2 min 13 s, from 00:39:33Z to 00:41:46Z.
- **C-JOIN part 2: PASS** in both `p0 --dry-run` and `p0`, with 792 of 792 spot rows matched bitwise over the 12
  playlists.
- P-F holds. The in-place inputs and the retention stat PASS.
- The price is 0 node-h: login node only, no job.
- The director accepted the result on 2026-11-27.

- **CITABLE FOR:** that e1's P0 ran as bound and passed its checks, C-JOIN part 2 included; its step records and their
  contents, as records.
- **NOT CITABLE FOR:** any RPD-RECO result, C-E3, or note wording. The step records' own `does_not_license` list
  applies: which period or flux is correct; correction or exclusion; change to estimator or covariance; validation or
  coverage; removing the unknown-cause clause; paper use without Joseph's decision.

## Preconditions (the binding)

- **The bound files.** The launch ran from a worktree detached at 81ff0d93. All eight bound files and the runner (cut
  from the connect's heredoc, `f145f41f…`) hashed to the binding's values there.
- **The cert check.** `TZ=UTC ssh-keygen -L` at 00:36:02Z read the cert as valid to 2026-11-27T14:22:19, and the
  launcher read the same.
- **The three-lane ack file.** cov2d (00:36:15Z), tier3-design (00:36:20Z) and minerva-lib (00:36:30Z) each acked.
  Their replies are verbatim in [`acks/`](acks/) and under the three `ACK-UTC` lines of
  [`connect/ack.txt`](connect/ack.txt) (sha256 `8c893c87…`). The launcher read the acks at ages 36, 31 and 21 s
  and copied the file byte for byte into the session.
- **ibu-chi** was told before the connect, as default (b) requires. Its OOFVC dump-rest was live. It is disjoint: P0
  opens no NuE file and does not read production's omnifile.
- **END** went to all four lanes at about 00:49Z, after the fetch.

## The connect: [`connect/`](connect/) (login02, 00:36:51Z to 00:39:33Z)

ssh rc 0, script rc 0. The launcher's output is [`connect/launcher.out.txt`](connect/launcher.out.txt).

- `node login02 staged sha256 5016f378…`, the bound connect.
- **Step 2, the sacct fence:** `sacct rows (14 days): 124; cov2d/t2a/rpd/geanttw rows: 19`, `FENCE: clear`. The one
  unended line, `62063413_[6,8-11]|oofvc_dump|PENDING` (ibu-chi's OOFVC), is outside the fence's families, so it did
  not refuse.
- **Step 3, the clone:** `HEAD 2415e8d66d1a9160e724d426eaeb54d458d4b4f7; porcelain lines 0`, with the 14 pins equal,
  including reco `12f68102`, custody `6428dead`, test `eee5ae4c` and mutation `8dfdeaf1`.
- **Step 4, the config:** `sha256 f92d034d… (expected f92d034d…)`.
- **Step 5, the in-place inputs:** `P0 INPUTS: PASS (14 files, 0 bad)`. flux4's `flux-extract.json` `060d4401…`,
  `flux-custody.json` `819bb7b9…` and the 12 factor products each equal run-62051670's records, read with O_NOATIME
  ([`records/flux4-inputs.txt`](records/flux4-inputs.txt)).
- **Step 6, the retention record:** `P0 STAT: PASS (40 files, 0 missing or different)`
  ([`records/stat-p0.txt`](records/stat-p0.txt)).
  - The 24 dumps and three gen2thin files have S1's bytes and inodes.
  - The 12 RDX omnifiles and the true-energy sidecar have the size and inode the sidecar probe recorded on 2026-11-26.
    Their atimes are unchanged from it: the omnifiles 2026-11-17T05:08, the sidecar 2026-11-17T17:45:29Z.
  - The earliest purge exposure is 2026-12-30T11:38:24Z (`fd-rpd-20261103/dumps/lat_1A.npz`, atime
    2026-11-04T11:38:24Z; see the constraints below).
- **Step 7, the overlap fence:** `FENCE OVERLAP: CLEAR (allowed 1, stops 0)` over 70 staged originals: flux4's 58 plus
  the 12 omnifiles.
- **Step 8, the `/dev/shm` copy:** HEAD 2415e8d6, porcelain 0, the 14 pins again, config `f92d034d…`.
- **Step 9, the runner:** sha256 `f145f41f…`, pid 948104 on login02 since 00:39:33Z (start ticks 71014096).
  `/dev/shm/limres-rpd-flux1` was handed over.

## The run (`records/`)

[`records/runner.out`](records/runner.out) shows:
- the runner at nice 19;
- `handoff.ok`;
- one monotonic deadline, 7200 s from the handoff;
- each step's PASS line;
- `== P0 DONE 2026-11-27T00:41:45Z`;
- `removed /dev/shm/limres-rpd-flux1`.

The supervisor records (`records/sup-*.json`):

| step | worker rc | signal | deadline signalled | past deadline | leftover | group gone | peak RSS |
|---|---|---|---|---|---|---|---|
| pins-dry | 0 | none | no | no | no | yes | 23,957,504 B |
| p0-dry | 0 | none | no | no | no | yes | 1,465,544,704 B |
| pins | 0 | none | no | no | no | yes | 31,457,280 B |
| p0 | 0 | none | no | no | no | yes | 1,492,176,896 B |

**The RSS, against the package's price.** The largest peak is 1.492 GB, 19% of the 8e9 B cap. It is above the
1.232 GB the package README gave as an upper bound. That figure priced part 2's own arrays on macOS (numpy 1.26). It
did not include p0's other loads (0.143 GB in the old P0), or the node's Linux and numpy 2.2.6 overhead. The cap was
never near.

**The step records** (schema `fd-rpd-reco-step/1`; all status PASS; `code_sha256` `12f68102…`; `config_sha256`
`f92d034d…`; `run_class` `diagnostic`):
- `dry/pins.json` and `run/pins.json` carry `dry_run` true and false, with no predecessor;
- `dry/p0.json` and `run/p0.json` name, as `predecessor_sha256`, the sha256 of the pins record in their own directory;
- the two pins records are committed gzipped, as in P0's 11-24 receipts (the director's ruling of 2026-11-24):

| record | `.gz` sha256 (bytes) | decompressed sha256 (bytes) |
|---|---|---|
| `dry/pins.json` | `8c04d4c2f20eabb6ac76b216a667acf6fe1223ba07f687f6254c6bc7da40de61` (2,921) | `66ed29aab10cfd8786cf956d0452d63a1d5d16e75143b97a1faba1e5d7c1efec` (12,119) |
| `run/pins.json` | `7b7dedf76d6ccaf0be26d193ce4829f3585a7c81764a20ca1b6877d3d16a1b9c` (2,916) | `2a22bdbfc2af1891d2db13e1b49c4e53c063296002b3a2fd1e240850dad121a8` (12,103) |

The decompressed sha256s are the ones the fetch printed, and exactly the `predecessor_sha256` values the committed
`p0.json` records carry. [`tests/test_pins_gz.py`](tests/test_pins_gz.py) (P0's test, re-pinned) checks this, plus
reproducible recompression and a one-byte mutant. It passes: 4 passed
([`tests/test_pins_gz.out.txt`](tests/test_pins_gz.out.txt)).

## C-JOIN part 2 (amendment 1 section 4)

`run/p0.json` `result.C-JOIN.part2` reads `status: PASS`, and `dry/p0.json` carries the same block. For every
playlist, every spot row from flux4's pinned join record passed each of these checks:
- its (run, subrun, event) occurs exactly once in the omnifile's `mc_signal_reco`;
- `truthx_enu / 1000` equals the recorded Eν, bitwise;
- `float32(MC)` and `float32(MC_pz)` equal `lat_<PL>`'s MCgen, bitwise;
- the flux4 product's `energy` equals the recorded Eν, bitwise.

| playlist | spot rows | matched | omnifile sha256 (c2's pin) |
|---|---|---|---|
| 1A | 66 | 66 | `e042d191…` |
| 1B | 66 | 66 | `37b48412…` |
| 1C | 66 | 66 | `6f847510…` |
| 1D | 66 | 66 | `918b8a15…` |
| 1E | 66 | 66 | `4e9fc232…` |
| 1F | 66 | 66 | `844cb5e5…` |
| 1G | 66 | 66 | `a9337e7b…` |
| 1L | 66 | 66 | `7baadf10…` |
| 1M | 66 | 66 | `ef1cb741…` |
| 1N | 66 | 66 | `7a5c3853…` |
| 1O | 66 | 66 | `9562f0eb…` |
| 1P | 66 | 66 | `f6b6a137…` |

That is 792 of 792. `C-JOIN.part1` carries flux4's record:
- 32,846,302 sidecar rows;
- median 6.4801 GeV, inside its [1, 50] GeV band;
- sidecar `641ba34c…`;
- lat_zero `6ca02c3d…`.

Under the amendment's placement conditions, flux4's factors may now be used by the later steps.

## P0's other checks

- **P-F:** `pass` true and `generated_flux_premise` true, from the pinned FluxReweighter source at its git sha
  `35097b65…`.
- **The mass constants:** M_n 0.93956536 GeV and M_p 0.938272013 GeV, matching CVUniverse.
- **The environment:** omnifold_py310, python 3.10.19, numpy 2.2.6, scipy 1.15.3 and uproot 5.6.9, as the config
  expects.
- **Dry against run:** the two `p0` results are equal key by key, with two exceptions:
  - `spectra` differs only in three `extract_path_opened` leaves (`dry/staged/` against `run/staged/`);
  - `runtime_estimate` differs only in its timing measurements.

## A reading for the director: the runtime estimate

`run/p0.json`'s `result.runtime_estimate` is the bound code's planning estimate for the later steps. It reads the same
way as P0's 11-24 record:

| field | value |
|---|---|
| `exceeds_two_hours` | true |
| `needs_director_price` | true |
| `node_hours_authorized` | 0 |
| `planning_seconds_with_factor_10` | 59320.91 (the campaign total) |
| c0 | 56906.29 s |
| d2-predict | 2414.62 s |
| pins, p0, step0, d1, d2 | 0 s |
| `poisson_only_seconds` | 5932.09 |
| `timing_sample_draws` | 262,144 in 0.00946 s |

On 11-24 the values were c0 50689.22 s and d2-predict 2150.82 s, from a 262,144-draw sample timed at 0.00842 s. The
difference comes from that timing sample; the draw counts are the same. This is a reading of the record, not a P0 STOP.
d2-predict + step0 is priced with its own package.

## The fetch: [`fetch1/`](fetch1/) (login02, 00:47:48Z to 00:47:55Z, bound fetch `d52f3576…`)

Script rc 0, launcher rc 0. The fetch reported:
- `p0.rc: rc=0 cause=exit end=2026-11-27T00:41:46Z`, state DONE;
- `dry/staged: 55 files` and `run/staged: 55 files`, which stay on pscratch;
- 18 files sent, 588,565 bytes;
- `TAR END tar rc=0 base64 rc=0`.

The tar's 18 entries are all plain relative paths. Untarred locally, each matched its printed sha256. `records/` holds 16
of them plainly and the two pins records gzipped.

`fetch1/session.notar.out` and `fetch1/launcher.notar.out.txt` are the outputs with the base64 tar block replaced by one
line. The full files had these sha256:
- `session.out`: `b9836bedf6baca718c429f8e76403f8cbd87a3d3c6dd1fe2078fe405ba9ed4cc`;
- the launcher output: `6ded5e7c9588c610393ffa32a3f5c55777d5b1b0c35bc0670d242f8c5361a843`.

## Binding constraints for e1's later steps

1. **lat_zero.npz**, the RDX dump, has purge exposure from 2026-12-25T08:53:42Z. Copies are on HPSS (the CT
   `stage0-inputs.tar`) and on CFS (as `lat_w2b_rrzero.npz`).
2. **The S1 dumps** `fd-rpd-20261103/dumps/lat_*.npz` (24 files) have purge exposure from **2026-12-30T11:38:24Z**,
   the earliest atime in step 6 (the director, 2026-11-27). Every later e1 step reads them with O_NOATIME, so the clock
   does not reset.
   - Their HPSS copy is `/home/j/josephrb/mnv-at-risk-20261111/rpd_dumps.tar`: 24 files, 1,577,462,973 bytes, the same
     total as step 6's stat (`fd/retention-20261110/hpss-20261111/cluster/logs/archive.log.txt:55-65`).
   - That archive's checks: htar verify with 0 errors, md5 hashverify OK, and one file retrieved and matched. Its
     manifest equals `fd/rpd-reco/INPUTS.sha256` on all 24 paths.
   - No CFS copy was found in the records.

The e1 chain's 12-20 target falls before both.

## Left on pscratch, and removal through the director

`/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126` holds:
- the clone and the tools;
- the step records and the `.pgid` files;
- `dry/staged` and `run/staged`, 55 files each, which include 2 x 7,373,436,509 bytes of omnifile copies.

`/dev/shm/limres-rpd-flux1` on login02 was removed by the runner.

Post-receipt steps, through the director: remove P0's root (the omnifile copies first), and remove flux4's lane
`/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126`. Both wait until d2-predict + step0 no longer needs P0's records or
flux4's products in place.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
