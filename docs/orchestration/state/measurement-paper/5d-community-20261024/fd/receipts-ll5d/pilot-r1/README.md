# LL5D ll5d_pilot (job 61181899): the step ended rc 4 and walls printed `verdict=REPRICE`; 10 of the 13 pilot items ran (2026-11-12)

**By** the `cov2d` session, under LL5D BINDING 3 and its addendum A1b.1 (M_A1b.1 `4231b14d…`). The director's go was
given in the gap before E96D's rerun:
- `connect-pilot.sh` `177f4f4d…`: the fill of cov2d's draft `014849f1`, diff `pilot-fill-vs-014849f1.diff.txt`;
- `launch-ll5d.sh` `d4155c14…`: a `pilot` case and its fence's `/^cov2d/` correction, diff `launch-vs-b86004df.diff.txt`.

The watcher was `watch-gates2h.sh` `8042e2b6…`, which accepts PENDING; diff `watch2h-vs-2g.diff.txt`.

- **The step's own result:**
  - sacct reads FAILED, ExitCode 4:0, Elapsed 00:30:19 (1,819 s), on nid004886;
  - the job log reads `walls rc=4` and `LL5D-WALLS verdict=REPRICE`;
  - `walls.json`'s `why` is `missing ll5d_g18_toy_minus2_4751000.npz`;
  - the job log also reads `controls rc=0`, `LL5D-CONTROLS verdict=PASS failed=[]`, and `clipcheck rc=0`,
    `LL5D-CLIPCHECK verdict=PROCEED`;
  - the job's exit status is walls' rc.
- **Routing:** reported to the director unrepaired. Nothing was relaunched or changed.
- **CANNOT AUTHORIZE:** a rerun, a repair, or the bulk.

## What ran

- `pilot-lanes.tsv` lists ll5d_b.PILOT's 13 items in 11 rows over 8 lanes. Lanes 0, 4 and 5 carry two rows each.
- The 8 lanes each ended rc 0. In each of lanes 0, 4 and 5, only the first row was unfolded:
  `lanes/lane{0,4,5}.out.txt` each hold one product line and one `rc=` line.
- **Not run:**

  | lane | row not run |
  |---|---|
  | 0 | `ar23 stat 1` |
  | 4 | `g18 toy minus2_4751000` |
  | 5 | `g18 toy all_4751000` |

- **The code path:** the lane loop in the job script (`connect-pilot.sh:138-149` at `177f4f4d…`, written into
  `sbatch-ll5d-pilot.sh`) is
  `while IFS=$'\t' read -r l t r its; do … srun … ; done < <(grep -v '^#' "$W/pilot-lanes.tsv")`. The `srun` inside the
  loop has no `< /dev/null`, and srun forwards its standard input to the task. So the loop's input was consumed after
  the first srun in each lane. Lanes 6 and 7 hold their two items in one row (`minus2,all`) and ran both.
- `connect-bulk.sh:222-227`, cov2d's bulk draft, has the same loop.

## The walls

From `walls.json`, `seconds_unfold` per product:

| product | seconds_unfold | peak RSS (KiB) |
|---|---:|---:|
| data_control setA_b1 | 670.171 | 24,705,520 |
| data_control MaRES_0 | 683.652 | 18,457,680 |
| data_control Flux_0 | 678.584 | 18,531,940 |
| data_control GEANT_Pion_0 | 681.768 | 18,485,924 |
| g18 central T | 821.209 | 19,805,072 |
| ar23 central T | 824.648 | 19,700,852 |
| g18 clipmean minus2 | 900.908 | 21,188,048 |
| g18 clipmean all | 878.016 | 21,372,252 |
| ar23 clipmean minus2 | 894.711 | 21,245,944 |
| ar23 clipmean all | 869.281 | 21,367,664 |

Section 9's per-item unit is 1,062 s.

## The outputs

- **The step's three records are NOT committed:** `walls.json`
  (`8adbe3486aadc26958fee81839138c388ad2e1e595876a1677f21c05c51991f6`), `controls.json`
  (`4de74e01a89771f59dcc2fd34c994d9575c0d24f437ace7eee173e4509f338fe`) and `clipcheck.json`
  (`575c3421065eb0818a4f1911af172e0b15428d3f256956ad94c0e4fc6034e583`).
  - `walls.json` names the products by bare filename, so `verify_receipt_artifacts.py` would report them MISSING.
  - The other two carry path and `_sha256` key pairs, which the hash-binding gate would collect as new live bindings.
  - This follows the director's choice for such records (#687, as in `../gate-g18/`). The sha256 values are the job's
    own lines in `ll5d_pilot_61181899.out.txt`, and copies whose sha256 matches are in the lane's working directory. Their
    three `.out` files are committed.
- **Their decisive fields, as written:**
  - `walls.json`: `verdict` REPRICE, `why` "missing ll5d_g18_toy_minus2_4751000.npz", every `rows` entry in the table
    above, `atime.moved` [].
  - `controls.json`: `verdict` PASS and `failed` []. Each of `setA_b1`, `MaRES_0`, `Flux_0` and `GEANT_Pion_0` reads
    `equal` True, `elements_differing` 0, `max_abs_difference` 0.0, shape [65856] on both sides, dtype `<f8` on both
    sides. `atime.moved` [].
  - `clipcheck.json`: `verdict` PROCEED, `delta_star` 0.667, `cells_at_or_above_delta_star` [] for each of `g18/all`,
    `g18/minus2`, `ar23/all` and `ar23/minus2`, `atime.moved` []. Its `sigma` field reads "S1's reported (fd_data_product
    C_total_plus_C_resp), a proxy for C_T".
- **The 10 products** in `/pscratch/sd/j/josephrb/ll5d-unfolds-r1/` are listed by sha256 in the job log and are not
  committed (the repository ignores `*.npz`).
- **The sealed clip-prep files** were read only inside `ll5d_b.read_clip_prep`: the connect log reads
  `clip_prep_sha256_matches=True` for both truths. They were not fetched.
- **The fetched files** match the node's sha256 (login34, 2026-11-12T19:02:08Z). `node-sha256.txt` lists 29 files,
  all OK. 26 of them are committed here; the three JSON records are listed by sha256 only. The `.log`/`.out` files carry a `.txt`
  suffix here.

## The run

- **The launch:**
  - `fence host=login02 utc=2026-11-12T18:27:30Z`: squeue empty, no cov2d job unended (`fence.txt`);
  - the staged connect's node sha256 matched the local file and the go (`staged_sha.txt`);
  - launched at 18:27:49Z (`launch.txt`, `launch-stdout.txt`);
  - the `/dev/shm` copy was removed, with `rm -f` rc 0 and the closing `ls` finding nothing (`removal.log.txt`).
- **The connect** (`connect-pilot.log.txt`):
  - `balance_node_h=1443.6 half=721.8 cap=148.0`;
  - `projection charged=45.609 held=0.000 this=1.0 total=46.609 cap=148.0`;
  - both gate records read verdict PASS, with clip-prep digests matching;
  - the deploy had porcelain 0 at `4231b14d…`, with all 22 bound blobs OK;
  - atime-pre: 1146 files at 18:28:46Z;
  - TimeLimit=01:00:00.
- **The job** (`ll5d_pilot_61181899.out.txt`): it started at 18:30:40Z and the closing line reads
  `end=2026-11-12T19:00:58Z`.
- **Cost:** 0.505 node-h (1,819 s on one node).

## Atimes

- atime-post was taken stat-only at 2026-11-12T19:03:34Z on login11, by `atime-post-2.sh` (`e75bebe9…`). Its `find` is
  the connect's own atime-pre `find` without the closing redirect.
- It is identical to `atime-pre.tsv` (`diff` rc 0), so 0 of 1146 files moved.

## The watchers

`watcher-exits.txt` holds each watcher's own output:
- `watch-gates2g` exited on PENDING at 18:29:22Z;
- `watch-gates2e` exited at 18:30:00Z (`RES-GONE`, its maintenance reservation poll);
- `watch-gates2h` exited at 19:01:39Z on the FAILED state.

`watch.log.txt` holds the shared log's lines for 61181899. The first is 18:29:22Z, and the job read RUNNING from
18:31:13Z.

## Files

`README.md`, `atime-post-2.sh`, `atime-post.raw.txt`, `atime-post.tsv`, `atime-pre.tsv`, `bound.sha256`,
`clipcheck.out.txt`, `connect-pilot.log.txt`, `connect-pilot.sh`, `controls.out.txt`, `env-job.log.txt`, `fence.txt`, `launch-ll5d.sh`, `launch-stdout.txt`, `launch-vs-b86004df.diff.txt`,
`launch.txt`, `lanes/lane{0-7}.out.txt`, `lanes/lane{0-7}.time`, `ll5d_pilot_61181899.out.txt`, `node-sha256.txt`,
`pilot-fill-vs-014849f1.diff.txt`, `pilot-lanes.tsv`, `removal.log.txt`, `sbatch-ll5d-pilot.sh`, `staged_sha.txt`,
`walls.out.txt`, `watch-gates2h.sh`, `watch.log.txt`, `watch2h-vs-2g.diff.txt`, `watcher-exits.txt`.
