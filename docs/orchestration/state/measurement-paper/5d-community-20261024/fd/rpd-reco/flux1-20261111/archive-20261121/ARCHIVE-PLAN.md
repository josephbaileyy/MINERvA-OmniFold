# Archive plan: RPD-RECO's flux connect 1 products to HPSS (tier3-design, 2026-11-21, DRAFT for the director; nothing runs)

**Under** Joseph's go of 2026-11-21 ("lets do them", as the director relayed it) to archive the run-period inputs:
the 24 dumps that expire around 12-30, and the 12 factor products that exist only on pscratch.

## 1. What is already archived: the 24 dumps

The 24 dumps are already on HPSS: group `rpd_dumps` of `/home/j/josephrb/mnv-at-risk-20261111/`, 24 files, 1,577,462,973 B.
- The archive is verified: htar `-Hcrc -Hverify=1`, `hashverify ... (md5) OK`, retrieve rc 0, and "group rpd_dumps PASS
  2026-11-11T02:53:18Z" (`fd/retention-20261110/hpss-20261111/cluster/logs/archive.log.txt:62-65`).
- `SHA256SUMS.rpd_dumps` equals `fd/rpd-reco/INPUTS.sha256` on all 24 paths (`hpss-20261111/README.md:74`).
- **No new copy is proposed.** Restore with `cd / && htar -xf /home/j/josephrb/mnv-at-risk-20261111/rpd_dumps.tar`.

## 2. What is not archived: the flux-connect-1 products

These are 13 files, 591,702,082 B, in `/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run/`. They were made by job
61206960 on 2026-11-13, after the 11-11 archive.

| file | bytes | sha256 (pin) |
|---|---:|---|
| flux-factors-1A.npz | 48,277,710 | `c1e8a8d4409cbc1a776070f8cd2a370c5e96c7e196e4a2f09ca3ea0e08d98d97` |
| flux-factors-1B.npz | 12,979,296 | `81f47d7872bf6e587053e7f7a152f59d6f802474d3768221a50522a90af4fb52` |
| flux-factors-1C.npz | 24,781,824 | `4c48513a1202e56041df7d19d4eb3f3e7c29893a28a15ddb7853726b70511e5e` |
| flux-factors-1D.npz | 72,060,660 | `9698326beee3ee6400ae4ab88e642b1ec36f723c8da113c79052008eb464bd0a` |
| flux-factors-1E.npz | 60,296,364 | `8179d743ffd8c616b68c42774a5de35cc6f2a36f953d710e52b75bdf6c2f35f3` |
| flux-factors-1F.npz | 83,877,390 | `63bfed31354af43fa75494268009d2dee5501f923ee5bf178c8b70f32d98082c` |
| flux-factors-1G.npz | 70,604,694 | `45bc479b03b43534b36ff5b4f2b9edfc45537c98d338c7c122c5f6c803fb38b4` |
| flux-factors-1L.npz | 6,909,696 | `a5e728830c92560a96233e5261981d0e38034b2edea23e45ce43a29dbfb5d4b1` |
| flux-factors-1M.npz | 106,505,136 | `7270690d1873181a2fc674ca9fb4414f9c00efbe86b333478959541638ace116` |
| flux-factors-1N.npz | 61,488,270 | `3806840598eaa1b75b7c7f66b3880c56ed94c9f71fa5bcd37c049f5d72eeb8aa` |
| flux-factors-1O.npz | 18,756,900 | `0090a6c671bcd750d2bf1227ede1ced84d29a4c32edcd1b8c55778f1d1063159` |
| flux-factors-1P.npz | 24,707,808 | `641e25557a4ef1659dea047bd115416a9839ee740169dfe340d9879942ed292a` |
| flux-extract.json | 456,334 | `f485554420af5a1933505b479dcaa6e978f504f9c9a0a4fdaae35af88e28a3a9` |

- **Sources of the pins:**
  - the factor digests come from `flux-extract.json`'s `factor_products` (the committed byte-identical copy,
    `../run-61206960/records/run/flux-extract.json`);
  - the json's own digest is that committed copy's sha256;
  - the sizes come from the 11-15 step-A inventory (`../delete-20261115/stepA/inventory/`).
- **These are exactly the files `../delete-20261115/NEEDS.txt` kept for P0.**

## 3. The kit: the LL5D hpss-u kit (RSN kit rev 2), list and target changed only

- **`hpss_flux1.template.sh`** is `fd/receipts-ll5d/hpss-u/hpss_ll5d_u.template.sh` as committed (`c525be7a…`; base of
  the launcher `32fc13bf…`) with five lines changed (`:45-50`):
  - `OUT=/pscratch/sd/j/josephrb/hpss-flux1-20261121`;
  - `H=/home/j/josephrb/mnv-rpd-reco-flux1-20261121`;
  - `W` (a fresh /dev/shm directory);
  - `GROUPS_IN_ORDER="flux1"`;
  - `N_ROWS=13`.
- **`hpss_flux1_launch.sh`** is the hpss-u launcher with OUT, H, the list and its sha256, and the script sha256
  changed. `make_hpss_script.py` is byte-identical (`d2f2a43a…`).
- **The list:** `hpss_flux1_list.tsv`, 13 rows of `flux1 <sha256> <path>` in the hpss-u format, built from the table
  above by a script, never typed.
- **What runs**, on a login node, never on dtn01:
  - an O_NOATIME stage of each file into /dev/shm, refusing unless its bytes equal the pin and its stat (size, mtime,
    atime) is unchanged across the copy;
  - `htar -Hcrc -Hverify=1 -cvf $H/flux1.tar`;
  - `hsi hashcreate` and `hsi hashverify` (the log must show "(md5) OK");
  - **every member retrieved and re-hashed against its pin** (the rev-2 kit's full retrieval);
  - `hsi ls -l $H` and hpssquota before and after.
- **Rules:**
  - the target must not exist beforehand;
  - HPSS had about 51.7 GiB free on 11-16, against about 0.6 GB here;
  - nothing is deleted on pscratch or HPSS;
  - nothing is written to CFS, and no Slurm job runs: 0 node-h.
- **Verification on the laptop after the fetch:** the run's SHA256SUMS against the 13 pins (`shasum -c`), the htar
  listing (13 members plus the manifest), and the retrieval log's 13 re-hash OKs.

## 4. Who runs it, fence, order

- **Proposed: tier3-design.**
- **Fence:** the read touches only `rpd-reco-flux-20261111/run/`. Acks from the director's fenced lanes, each under 15
  minutes old, then one connect on the director's go with a window epoch. The end message follows.
- **Order:**
  1. the director's review of the kit diffs and the list sha256;
  2. the go;
  3. the archive connect;
  4. the fetch of the logs;
  5. a receipt PR.
- **Timing:** independent of a+c and T3. These files' 8-week exposure starts about 2027-01-08 (arithmetic from
  2026-11-13). It can run first or last.

<!-- absence-ok: a plan for an unrun archive; statements about what is not archived are routed to the records named -->
