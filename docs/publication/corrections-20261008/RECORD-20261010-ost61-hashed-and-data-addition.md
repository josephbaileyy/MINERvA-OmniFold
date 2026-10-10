# The 7 OST-61 AnaTuples hashed, and the 6 data files added to the CFS copy (2026-10-10)

**CITABLE FOR:**
- the checksums of the 7 AnaTuples whose first stripe is on pscratch OST 61, which completes the manifest (2,374 of
  2,374 files);
- the addition of the 6 OST-61 data files to the CFS copy `anatuple-data-20261009/`, and its verification;
- the withdrawal of draft C (the NERSC ticket), which was never sent.

**NOT CITABLE FOR:**
- any physics number (none changed);
- a copy of the simulation AnaTuples (none was made; only their checksums exist);
- why OST 61 hung or why it recovered (neither was measured);
- a deposit, tag or submission.

| | |
|---|---|
| authority | Joseph, 2026-10-09 ("okay do that"): retry the 7 unhashed files about a day later, and draft the NERSC ticket only if they still hang. Joseph, 2026-10-10 ("go ahead"), approving the proposal to add the 6 data files to the CFS copy and record it on a branch with a PR. |
| not authorized, not done | copying the simulation AnaTuples; any external message or quota request; deletion; Slurm; deposit; tag; submission |
| baseline | `origin/main` `016265cceadbd0f38de31e7f4956377f3d3c5e82`; branch `preserve/anatuple-ost61-20261010` |

## 1. The hung reads had completed on their own

The first check on `dtn01` (2026-10-10 16:11 UTC), before the retry, showed:
- **No hung processes were left on `dtn01`.** `ps -u josephrb` listed only the login session itself. (`login05`,
  which ran one retry, was not checked.)
- **All 20 watchdog children from 2026-10-08/09 had finished.** The sweep script hashes each file in a child process.
  When a child outlives its watchdog, the worker defers the file and moves on, and ignores any late result. Each of
  the 20 children left behind did write its result in the end: 6 from run 3 and 7 from the retry, both on `dtn01`,
  and 7 from the retry on `login05` (matched by their start times to the run windows of the follow-up record §3a).
  Every result is an `H` line: the size and mtime matched the inventory before and after hashing.
- **They all finished within about two minutes**, 2026-10-09 18:30:57 → 18:33:00 UTC, on both clients, after
  13–17 h in uninterruptible I/O. `anatuple-checksums/late-results-20261009.tsv` lists each one: start, finish,
  worker file and result line.
- **The late digests agree with each other.** Each of the 7 files has 2 or 3 late results, all with the same digest.
- **One late result had reached the manifest's working file.** `SHA256.part` held 2,368 rows, one more than the
  committed manifest: run 16140, with the same digest as its 2 late results. Its mtime, 2026-10-09 18:30:57 UTC, is
  the second the first children finished. Which process appended it was not established.

## 2. The retry (2026-10-10)

**Script:** the committed sweep script (`a5c386dc…`, digest checked on `dtn01` before launch), on the committed
inventory. It resumed and tried the 6 files without a row in `SHA256.part`.

**Result:** `start 2026-10-10T16:12:24Z: 6 to hash, 2368 already done` → `end 2026-10-10T16:13:10Z: 2374 hashed, 0
mismatches, 20 deferral records` (`anatuple-checksums/sweep-retry2.txt`). `DEFERRED.tsv` is byte-identical to the
committed one, so no file was deferred.

**Independent check:** every one of the 7 files was re-hashed directly with `sha256sum` on `dtn01`, twice: at
16:28–16:35 UTC, and again at 20:13–20:14 UTC after the copy of §3. The committed receipt is the second pass
(`anatuple-checksums/rehash-ost61-20261010.txt`). Both include run 16140, which the retry did not hash because its
row was already present. Each digest equals the manifest row and every late result.

| file | bytes | sha256 |
|---|---:|---|
| `Data/Playlist1E/MasterAnaDev_data_AnaTuple_run00016140_Playlist.root` | 374,633,636 | `7e0955f9…` |
| `Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016588_Playlist.root` | 537,535,407 | `f9b397d8…` |
| `Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016758_Playlist.root` | 806,358,789 | `739fe4ea…` |
| `Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00018720_Playlist.root` | 474,453,796 | `4752b01c…` |
| `Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00019158_Playlist.root` | 281,673,869 | `43509953…` |
| `Data/Playlist1M/MasterAnaDev_data_AnaTuple_run00019215_Playlist.root` | 561,298,681 | `4734633f…` |
| `MC/StandardMC/Playlist1O/MasterAnaDev_mc_AnaTuple_run00113376_Playlist.root` | 20,413,593,716 | `493b0625…` |

**The manifest:** `publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv` is now the sweep's
regenerated file, sha256 `913e004d538c6d47932ba5a343d382d2a599be1c6f143ab64f49ccbd40bdf7b1`, 2,374 rows plus the
header. Against the previous `a2188312…`, the only change is the 7 rows above; no earlier row changed. The CFS copy
in `anatuple-checksums-20261008/` has the same digest.

**Draft C is withdrawn.** It asked NERSC to repair OST 61 so these files could be read; they now read normally. It
was never sent. The drafts file marks it withdrawn, and drafts A and B now say that all 2,374 files have checksums.

## 3. The 6 data files added to the CFS copy

**Script:** `publication/release/preservation/copy_anatuple_data_20261009.sh`, sha256 `bfa95102…`. Three steps were
added for files hashed after a list was made, so the 2026-10-09 list (`DATA-SHA256SUMS`, 1,879 rows) stays exactly as
made:
- **`add-list YYYYMMDD`:**
  - checks that every row of every earlier list is still in the manifest, with the same digest and path, and refuses
    if not;
  - selects the manifest rows under `Data/`, `MATFluxAndReweightFiles/` or `MParamFiles/` that no earlier list names;
  - writes them to `DATA-SHA256SUMS-ADD-YYYYMMDD`, and refuses to overwrite that file or to make an empty list.
- **`add-copy`:** `rsync -a --files-from` under `nice -n 19 ionice -c3`, as before.
- **`add-verify`:** `sha256sum --quiet --strict -c` of the added list in the destination.

The CFS directory holds the new version under the old name. The version that made the 2026-10-09 list (`b6b765d5…`)
is kept beside it as `copy_anatuple_data_20261009.sh.b6b765d5`.

**Fixture test on `dtn01` first** (13 cases, 0 failures):
- the original list, copy and verify still work;
- before any new row, `add-list` reports nothing to add (rc 6), and a malformed tag is refused (rc 2);
- with one newly hashed data file, one unhashed data file and one MC file, only the new data file is listed, copied
  and verified, and the original list still verifies;
- re-listing the same tag is refused (rc 5);
- a second addition with nothing new reports nothing to add, so the earlier added list counts as listed;
- a corrupted added file is caught (rc 1);
- a manifest whose digest for an already-listed file has changed is refused (rc 4) by the drift check itself, and
  no list is written.

**Capacity, re-measured first:** `du -s --block-size=1G /global/cfs/cdirs/m3246/josephrb` = **2,512 GiB**
(2026-10-10 20:01–20:07 UTC). The addition is 3,035,954,178 B (2.83 GiB).

**Result:** **all 6 added files match the checksum manifest**
(`publication/release/preservation/anatuple-data/add-copy-verify-20261010.txt`, the run log, which also records the
script and manifest digests).
- `add-list` at 20:07:40 UTC: 6 files, 3,035,954,178 B, written to `DATA-SHA256SUMS-ADD-20261010` (sha256
  `1018c4fa…`, committed in `anatuple-data/`). They are the 6 data files of §2; the MC file is not selected.
- `add-copy` 20:07:40 → 20:07:53 UTC, `rsync` rc 0; `add-verify` 20:07:53 → 20:07:57 UTC: `all 6 added destination
  files match the checksum manifest`.
- The 1,879 files of 2026-10-09 were not re-hashed. The drift check found every row of their list unchanged in the
  new manifest, and nothing wrote to their paths.
- **The whole copy, counted afterwards:** `anatuple-data-20261009/{Data,MATFluxAndReweightFiles,MParamFiles}` holds
  **1,885 regular files, 989,696,077,171 B**. The two lists together are byte-identical, once sorted, to the
  manifest's rows for those three trees (1,885 rows), so the copy now covers every data, flux and parameter file of
  the inventory.
- CFS after: `du` = **2,514 GiB** (20:07–20:13 UTC), under the 3 TB rule. About 280 GiB of the rule remains.
- The committed README (`publication/release/preservation/README-prd-release-preservation-20261008.md`) now describes
  the addition and its recovery command. Its CFS copy, `README.md`, was replaced with it: sha256 `1b259f98…` on both
  sides, checked after the upload. The replaced copy was the committed `a6cf9e56…`.

## 4. Where G4 stands

| part | files | state |
|---|---:|---|
| identity (sha256 manifest) | 2,374 of 2,374 | complete, 0 mismatches |
| data, flux and parameter files on CFS | 1,885 of 1,885 (989,696,077,171 B) | copied and verified |
| simulation AnaTuples | 489 (10.53 TB) | identified only; still on purgeable scratch. Drafts A (HPSS) and B (MINERvA retention) remain unsent, for Joseph to decide. |

**Housekeeping, left as is:** the 20 empty `.w.*` worker files and their 20 `.res` results remain in the CFS
directory `anatuple-checksums-20261008/`. The copied trees are group `josephrb`, as for the 2026-10-09 copy.
Nothing was deleted.
