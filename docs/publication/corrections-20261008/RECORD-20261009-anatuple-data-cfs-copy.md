# Durable CFS copy of the analysed data AnaTuples (2026-10-09)

**CITABLE FOR:**
- the CFS copy of the analysed older-production data AnaTuples and their flux/parameter files;
- its verification against the committed checksum manifest;
- the merges of 2026-10-09 (PR #58, the audit branch, the standalone note sync).

**NOT CITABLE FOR:**
- any physics number (none changed);
- the simulation AnaTuples, which are not copied;
- the 7 OST-61 files, which are not copied and not hashed;
- a deposit, tag or submission.

| | |
|---|---|
| authority | Joseph, 2026-10-09 ("okay do that"), approving the revised recommendation: (1) merge PR #58; (2) merge the audit branch; (3) copy the data AnaTuples to CFS; (4) retry the 7 unhashed files about a day later and draft the NERSC ticket only if still needed |
| not authorized, not done | copying the simulation AnaTuples; any external message or quota request; deletion; deposit; tag; submission |
| baseline | `origin/main` `460631d1f93c2f0cbaab6ecffdf313121c431751`; branch `preserve/anatuple-data-cfs-20261009` |

## 1. Merges

| item | identity |
|---|---|
| PR #58 (G11, G12, preservation follow-ups) | merged with a merge commit (`--match-head-commit c1c7dc62…`) as **`33811d7db15f08fb0d83b6a8de18ffdb6a2e7b32`**, parents `f6dc46e6` (main) and `c1c7dc62` (the reviewed head plus its record-only commit) |
| pre-merge check | `main` had gained Joseph's commit `f6dc46e6`, which rewords `paper_body.tex`. The G11 checker passed on that text (14/14, self-test 17) before the merge. |
| audit branch `ea939701` | merged through PR #59: merge commit `2511f64a` (parents `33811d7d` and `ea939701`), a `MANIFEST.tsv` regeneration `6225ed00` (inbound-reference counts only), and the GitHub merge **`460631d1f93c2f0cbaab6ecffdf313121c431751`**. `ea939701` and `37825e61` keep their SHAs. |
| canonical build at `460631d1` | `build_all.sh` **`RESULT :: PASS`**, `tree=clean`; **`SEC4-RECEIPTS :: PASS (14/14)`**, self-test 17; 123 / 9 / 11 pages |
| standalone note `main` | **`ad3fb8000a8d373a796856bdbc4c050b9970fc30`**, a merge of `e9c3731b` (`main`, with Joseph's wording commits) and `de1461a0` (`sync-prd-followup-g11-20261008`). Every tracked file equals canonical `460631d1` `docs/analysis-note`, apart from `.gitignore` and `AGENTS.md`. Its build: rc 0, 123 / 9 / 11 pages, SEC4 SKIP by design. The `pdftotext` output of all 3 PDFs equals the canonical build's. |

## 2. The data copy

**Capacity, re-measured first:** `du -s --block-size=1G /global/cfs/cdirs/m3246/josephrb` = **1,593 GiB**
(2026-10-09 07:14–07:19 UTC). The copy adds 986,660,122,993 B (918.9 GiB), so about 2,512 GiB (2.70 TB). That is under
the 3 TB rule.

**Script:** `publication/release/preservation/copy_anatuple_data_20261009.sh` (sha256 `b6b765d5…`; the same bytes are
in the CFS directory `anatuple-checksums-20261008/`). It runs on `dtn01` in three steps:
- **list:** it selects every row of the committed manifest `ANATUPLE-SHA256.tsv` (`a2188312…`, the CFS copy checked
  before use) under `Data/`, `MATFluxAndReweightFiles/` or `MParamFiles/`. A file with no checksum is never touched,
  and that is what excludes the 6 data files on OST 61. The list is **1,879 files, 986,660,122,993 B**: 1,812 data,
  58 flux and 9 parameter files.
- **copy:** `rsync -a --files-from`, under `nice -n 19 ionice -c3`. The sources are only read.
- **verify:** `sha256sum --quiet --strict -c DATA-SHA256SUMS` in the destination, so every destination file is
  re-hashed against the manifest's digest, which was computed at the source.

It was tested first on `dtn01` with a fixture:
- the selected files were copied and verified;
- an unselected data file and an `MC/` file were not copied;
- a corrupted destination file was caught (rc 1);
- re-listing was refused.

**Result:** **all 1,879 destination files match the checksum manifest.**
- The copy ran 07:19:27 → 07:58:14 UTC, and `rsync` exited 0.
- The verification ran 07:58:14 → 08:24:09 UTC, printing `verify: all 1879 destination files match the checksum
  manifest`.
- The destination holds 1,879 data files with 986,660,122,993 B in total, equal to the list.
- `DATA-SHA256SUMS` (`9c33e2c6…`, 1,879 lines) is committed in `publication/release/preservation/anatuple-data/`,
  with the run log `copy-verify.txt`. An independent check confirms it is exactly the manifest's rows for the three
  trees.
- CFS after the copy: `du` = **2,512 GiB** (2.70 TB) at 09:51–09:56 UTC, under the 3 TB rule. About 280 GiB of the
  rule remains.

**Destination:** `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/anatuple-data-20261009/`. The
files sit at their paths relative to `minerva_large_files/`. The CFS `README.md` describes the copy, and a recovery
command is in the committed README.

**Permissions:** `rsync -a` kept the source owner, group and modes. The copied trees are group `josephrb`, not `m3246`,
so other m3246 members cannot read them. They were left as copied; changing that is Joseph's call.

## 3. What remains

- **The 6 data files on OST 61** (3.04 GB) and the 1 simulation file there.
  - A retry of the checksum sweep is scheduled for about 2026-10-10 09:07 local time, as a session-only job. The
    sweep resumes and tries only those 7 files.
  - If any of the 6 data files hash, the next step is to add them to this copy and verify them.
  - If they still hang, draft C (the NERSC ticket) is ready for Joseph to send.
- **The simulation AnaTuples** (488 hashed files, 10.5 TB): unchanged. Ask MINERvA first (draft B), else request
  HPSS space (draft A). Both are unsent.
