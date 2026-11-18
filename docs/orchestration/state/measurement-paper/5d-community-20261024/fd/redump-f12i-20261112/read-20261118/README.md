# RDX read, 2026-11-18 (receipt)

**By** session tier3-design, under RDX-BINDING-1 addendum J7 (rulings 2–3). The outcome is
`docs/orchestration/OUTCOME-20261118-rdx-widened-regressor.md`: **LICENSED**. The fetch and the read cost 0 node-h.

## Files

| file | what it is |
|---|---|
| `rdx_readout.json` | the bound reader's output, sha256 `0f5158f46656283455659d9120f7ec731ac3cfb10b13e54860546515dce189f8`. Written by `nd-unfolding/rdx/rdx_read.py` at M_RDXR `9de8ef0d` in a clean clone on the laptop (Python 3.12.2, numpy 1.26.4), from the fetched products and logs only |
| `run.txt` | the reader's console line and exit status (0) |
| `fetch-manifest.json` | the fetch's own manifest (`rdx_fetch_remote.py` 89ea886d at main `ee6a774c`). It records each of the 32 files' sha256, bytes and stat before and after its O_NOATIME read, plus both sacct fence reads (147 rows, clear) |
| `fetch-launch.txt` | the launcher's log: login27, 2026-11-18T19:19:28Z, ssh rc 0, unpack rc 0 (32 files), and the tar's sha256 `585473096f3880a5…` |
| `stop-a-launch.txt` | the first attempt (18:40:48Z, main `3068cd63`). It stopped at its own fence with exit 9, because sacct rejected `-s CF`. Nothing was read. Fixed in rev 3 (#1223) |
| `stop-b-launch.txt` | the second attempt (19:15:17Z, main `ee6a774c`). ssh exited 255 before the remote started. Nothing was read |
| `probe.txt` | the director's one connectivity probe after stop b: saul answered as login34 and the hop as login27, both rc 0 |

The fetched products and logs are not committed. They live on the laptop at `/Users/josephbailey/rdx-fetch-20261118c/`,
and the products' sha256 are the ones their own jobs printed (receipts #1208 and #1214). `rdx_readout.json`'s `inputs`
block re-records them. cov2d acked each connect (`cov2d-ack-rdx-fetch-20261118`, `-b`, `-c`) and received an END after
each.
