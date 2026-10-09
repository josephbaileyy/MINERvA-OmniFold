# Follow-ups to the PRD release-audit corrections: merge, preservation additions, G12, G11 (2026-10-08/09)

**CITABLE FOR:**
- the merge identities of PR #55 and the standalone note;
- the preservation additions (the W2 outputs on CFS, the HPSS second copies, the AnaTuple checksum sweep) and their
  receipts;
- the G12 reproduction of the release inputs from durable storage;
- the G11 build-time check;
- the remaining storage decision.

**NOT CITABLE FOR:**
- any physics number or frozen decision (none changed);
- a deposit, tag or submission;
- closing `OI-130`;
- any statement about convergence. The proxy-rate provenance (G6b) stays unresolved, and no refinement study was run.

| | |
|---|---|
| authority | Joseph, 2026-10-08 ("Proceed with closing out the correction pass and the following bounded follow-ups"). It authorizes: the #55 and standalone merges; the full AnaTuple checksum sweep on a DTN with controlled I/O; the W2 outputs to CFS; an HPSS second copy of the s5p archive and `z-cv.npz`; G12 as a reproduction task; G11 as a focused build-time check; one fresh read-only reviewer, with at most two cycles; a reviewed, unmerged PR for G11/G12. |
| not authorized, not done | copying the 0.99 TB of data AnaTuples; any quota request or external message (drafts only, §7); deletion; deposit; tag; submission |
| baseline | `origin/main` `b612ee3ac9b517c56e1153223576b7c3f5dcd32a` (the #55 merge); worktree `MINERvA-OmniFold-prd-followup-20261008`, branch `followup/prd-release-g11-g12-20261008` |
| coordination | Joseph first sent these instructions to another session (minerva-omnifold-13) by mistake. On being told, it stopped. It reported that it had merged, pushed and transferred nothing and run no cluster command; its read-only results at `49990f82` were used only as corroboration. |

## 1. Campaign-review choice (`CAMPAIGN-REVIEW-20260929.md` §1)

The review was read in full in this session before this follow-up began.

- **Decision answered:**
  - is the reviewed PR merged with its source identities intact;
  - are the authorized additions preserved and verified;
  - can the release inputs be regenerated from durable copies alone, and does a build check now bind the Sec. IV
    values?
- **Useful terminal outcomes:** a demonstrated blocker; a reproduction that is numerically equivalent but not
  byte-identical, stated precisely.
- **Owner and review:** owner, this session (Opus 5.5). Reviewer, one fresh read-only subagent at a fixed commit (§9).
  Its independence is per session, not per model.
- **Budget:**
  - no Slurm jobs;
  - transfer-node and login-node I/O only, measured in §3;
  - small login-node Python runs for G12 (about 90 s each, with no allocation charge);
  - at most two review/repair cycles.

## 2. Merge identities

| item | value |
|---|---|
| changes after the READY review | `git diff 4b9bd88e 49990f82` touches only the corrections record (+52/−3) and one `MANIFEST.tsv` line. Nothing under `docs/analysis-note` or the release paths. |
| PR #55 | merged with a **merge commit** (`gh pr merge 55 --merge --match-head-commit 49990f82…`), so no squash. The merge is **`b612ee3ac9b517c56e1153223576b7c3f5dcd32a`**, parents `fec438db` and `49990f82`. `git diff 49990f82 b612ee3a` is empty, so the merged tree equals the reviewed head's tree. |
| source identities kept | `f82e6db7` (the RC5 source), `35146cc1` (the RC6 source) and `4b9bd88e` (the reviewed commit) are all ancestors of `main` (`git merge-base --is-ancestor`) |
| standalone note | `main` fast-forwarded from `2357c6ca` to **`e1af61e3cc5d571be97e10f5e759ccf9afdabfd2`** (`git push origin origin/sync-prd-release-corrections-20261008:refs/heads/main`) |
| sources equal | `git archive b612ee3a docs/analysis-note` and `git archive` of standalone `main` match (`diff -rq`), apart from the standalone's own `.gitignore` and `AGENTS.md` |
| remote heads (`git ls-remote`, 2026-10-09 00:0x UTC) | `MINERvA-OmniFold` main = `b612ee3ac9b517c56e1153223576b7c3f5dcd32a`; `MINERvA-OmniFold-Analysis-Note` main = `e1af61e3cc5d571be97e10f5e759ccf9afdabfd2` |
| checks after the merge | the merge adds no change to the reviewed tree. The peer session's read-only run at `49990f82` (same tree) gave `build_all.sh` PASS at 123/9/10, `generate_manifest.py --check` OK, and 49 tests passing. This branch's own builds are in §8. |

## 3. Preservation additions

**Capacity, re-measured first:**
- CFS: `du -s --block-size=1G /global/cfs/cdirs/m3246/josephrb` = **1,561 GiB** (2026-10-09 00:08 UTC). The W2
  addition adds 33.8 GB, so about 1.59 TiB, under the 3 TB rule.
- HPSS: `hsi du` = 373,553,509,414 B (347.9 GiB, 54 files) against a 512 GiB quota. `hpssquota` failed on two login
  nodes (an `lfs quota` subprocess error), so the quota figure is the 2026-10-08 15:33 UTC `hpssquota` reading.

**W2 outputs to CFS** (`publication/release/preservation/preserve_w2_outputs_20261008.sh`, sha256 `9ed7954f…`):
- sources: `w2-recoil-20261006/w2b/{evloop,lateral,merged}`, the 32 GB the first pass excluded, plus the two small W2
  directories it had missed (`tables`, `unfold-run`);
- inventory, copy (`rsync -a`, root `/global/`) and destination re-hash: **53 files, 33,779,505,923 bytes; all 53
  destination files match the source inventory**;
- no symlinks;
- receipts: `W2-SOURCE-INVENTORY.tsv` (`0e5c0d1d…`), `W2-SHA256SUMS` (`a41a773c…`), `W2-VERIFY-RECEIPT.txt`
  (`3dae4337…`), in the CFS directory and in `publication/release/preservation/w2-addition/`.

**HPSS second copy** (`hpss_second_copy_20261008.sh`, `verify_tar_stream.py`; run from a login node):

| object | HPSS path | bytes | read-back verification |
|---|---|---:|---|
| s5p product archive (`htar -Hcrc`, with index) | `/home/j/josephrb/prd-release-preservation-20261008/s5p-archive-20261006.tar` (+ `.idx`, 5,472,032 B) | 2,324,167,680 | streamed back with `hsi get -`, and every member's sha256 computed: **10,614 of 10,614 listed files present with matching digests** (the 10,612 products, plus the archive's own `SHA256SUMS` and `files.txt` checked against their CFS copies); 0 missing, 0 mismatched, 0 unlisted; htar's consistency-check member reported and not counted |
| adopted `z-cv.npz` | `/home/j/josephrb/prd-release-preservation-20261008/z-cv.npz` | 890,500,272 | streamed back: sha256 **`3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`**, the VL142 digest |

The logs are in `publication/release/preservation/hpss/`. The verifier's first run failed: `str.removeprefix` doesn't
exist on the login node's Python 3.6. It was made compatible and re-run. The CFS sources were only read.

**AnaTuple checksum sweep:** §3a.

### 3a. AnaTuple checksum sweep (G4 identity)

**Script:** `publication/release/preservation/anatuple_checksum_sweep_20261008.sh` (sha256 at this commit in §8). It
read the exact committed inventory, `anatuple-inventory-20261008.tsv` (2,374 files, 11,523,656,218,592 B), and only
READ the AnaTuples on `/pscratch/sd/j/josephrb/minerva/minerva_large_files`.
- I/O control: two concurrent streams, each `nice -n 19 ionice -c3`.
- No Slurm job, and no scientific computation.
- Each file's size and mtime were checked against the inventory before and after hashing.

**Result:** **2,367 of 2,374 files hashed (11,500,206,670,698 B); 0 size/mtime mismatches; 0 duplicate paths.**
The manifest is `publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv` (sha256 `a2188312df17480033d8fd21f46d88ae381d672a39cfbc2262a650299db85175`),
with a copy in the CFS directory `anatuple-checksums-20261008/`.

**7 files remain unhashed: every one has its first stripe on OST 61 of pscratch.**

| file | bytes |
|---|---:|
| `Data/Playlist1E/MasterAnaDev_data_AnaTuple_run00016140_Playlist.root` | 374,633,636 |
| `Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016588_Playlist.root` | 537,535,407 |
| `Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016758_Playlist.root` | 806,358,789 |
| `Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00018720_Playlist.root` | 474,453,796 |
| `Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00019158_Playlist.root` | 281,673,869 |
| `Data/Playlist1M/MasterAnaDev_data_AnaTuple_run00019215_Playlist.root` | 561,298,681 |
| `MC/StandardMC/Playlist1O/MasterAnaDev_mc_AnaTuple_run00113376_Playlist.root` | 20,413,593,716 |
| **7 files (6 data, 1 simulation)** | **23,449,547,894** |

- **These 7 are all of the inventory's OST-61 files.** `lfs getstripe -i`, a metadata-only query, put the first
  stripe of each of the 2,374 files on an OST (`anatuple-ost.tsv`). Exactly 7 start on OST 61; 0 of them hashed.
  Every file on every other OST hashed.
- **The reads hang in the kernel, not in the script.**
  - The `stat` or the first read blocks in uninterruptible I/O (D state, wait channel `cl_sync_io_wait`), and
    `kill -9` does not end it.
  - A one-file probe per OST (`ostprobe.tsv`) ran a `stat` on one inventory file per first-stripe OST, 366 OSTs in
    all, at 2026-10-09 01:02 UTC.
    - Every probe returned at once, except two.
    - OST 61's never returned.
    - OST 60's returned only at 04:03 UTC. Its 3 files are hashed.
- **It is not one client.**
  - During runs 1–3 on `dtn01`, these files hung, or were skipped as known-hung.
  - All 7 then hung past their watchdogs in two dedicated retries: on `dtn01` at 04:17–05:04 UTC, and on login node
    `login05` at 05:06–05:53 UTC. The login node is a different Lustre client.
- **Nothing was forced.** The watchdog put each timed-out file in `DEFERRED.tsv` (`timeout_<s>s`) and moved on.
  Hung children are left in place (they cannot be killed); a late result from them is ignored.

**Run history** (all logs are in `anatuple-checksums/`):

| run | where | window (UTC, 2026-10-09) | outcome |
|---|---|---|---|
| 1 | `dtn01` | 00:08:04 → stalled | 800 hashed, then both streams blocked on hung objects. There was no watchdog yet. |
| 2 | `dtn01` | 01:04:34 → killed | 2 known-hung files skipped (`SKIP`); stalled again on another hung file. I stopped it and added the per-file watchdog. |
| 3 | `dtn01` | 01:17:53 → 04:13:38 | watchdog, 4 skipped files: 2,365 hashed, 0 mismatches, 6 deferral records |
| retry | `dtn01` | 04:17:08 → 05:04:29 | the 9 unhashed files: 2 more hashed (2,367); 7 timed out again |
| login retry | `login05` | 05:06:14 → 05:53:31 | the 7: all 7 timed out again (deferral records 14–20); 2,367 hashed, 0 mismatches |

- **Run 2 left a late hash.** Run 2's killed workers left a child that finished hashing
  `Data/Playlist1F/…run00016532…` after run 3 had placed that file on its skip list, so its digest entered the
  manifest without passing through run 3. It was re-hashed independently (`sha256sum` on `dtn01`, 2026-10-09
  04:17 UTC). The digest matched, `8056f9dd…`, so the manifest entry is kept.
- **A locale mismatch on the login node.** `join` there ran under a UTF-8 locale while `sort` used `C`, and printed
  "not sorted" warnings. The to-do set was still correct: 7 files, the same 7. The script now exports `LC_ALL=C`
  for the whole run (sha256 in §8). The DTN runs were under the POSIX locale, so unaffected.
- **Throughput:** run 3 hashed 1,457 files, 11.12 TB, in 2 h 56 min: about 1.05 GB/s aggregate over 2 streams. That is no
  faster than the single stream the corrections record measured (§6: about 0.85–1.1 GB/s). Why the second stream
  added nothing was not measured.

**What this does and does not establish.**
- It identifies 2,367 files of the analysed older production byte for byte. Any later copy, or a file MINERvA
  confirms it retains, can be checked against the manifest.
- It is **not** a copy. The files are still on purgeable scratch only (§7).
- The release (RC6) does not contain the manifest. The article's statement that the release records "names and
  sizes, but not checksums" therefore stays accurate, and is left unchanged; no new release is authorized.
- The 7 OST-61 files have names, sizes and mtimes (from the inventory) but no checksum. Hashing them needs OST 61 to
  serve reads again. A help-ticket draft is in the drafts file (C), not sent.

## 4. G12: the release inputs regenerated from durable storage

**Adapter: a reconstructed directory layout; no code change.**
- `publication/release/g12/reproduce_from_durable.sh` runs the **unchanged frozen extractor** (sha256 `6ff1d6df…`,
  the preserved copy) and the **frozen code**, reconstructed from git.
  - Git `e9372b75` reproduces the RC4 manifest's `s5p_joint` `2cd98235…`, `s5p_inference` `55239135…` and design
    `404446eb…`.
  - Git `51648245` carries the union deploy's identical modules.
  - The union design `f93bdb88…` comes from git `11a266c6`, and the archive holds an identical copy.
- The run happens inside a bubblewrap sandbox on a login node:
  - the whole host is read-only;
  - an **empty tmpfs covers the live campaign directory** `/pscratch/sd/j/josephrb/s5p-20260926`, so nothing on the
    purgeable original can be read;
  - the durable copies are bound at their original absolute paths: the CFS s5p archive (`runs/prod`, `stage3`,
    `gen5d*`, `recovery/recovery`), the CFS preservation directory (`runs/s2`, `runs/s3`, `runs/s3v`) and the
    git-derived deploys.
- The union reading's `recovery/union` was a directory of 8,600 links. It is rebuilt verbatim from the link list
  captured from the original (`recovery-union-links.tsv.gz`); every target lies in the archive's layout.
- The frozen design, code and receipt bytes are untouched, and their hashes are checked at run time.
- Environment: Python 3.11 venv with numpy 1.26.4 and scipy 1.16.3 (the RC4-tested Linux versions). The original
  user-site numpy is no longer present on the login nodes.

**Results** (`publication/release/g12/results/`: the run logs, `compare-*.txt`, `replay-summary.txt`, `blas-thread-digests.txt`, `venv-freeze.txt`):

| product | regenerated sha256 | release sha256 | arrays | manifest | replay against the recorded evaluation |
|---|---|---|---|---|---|
| frozen `inference_sufficient.npz` | `1e21009b…` | `7bd019c6…` | 25 of 52 exactly equal; the other 27 differ in the last bits: worst relative difference **2.7e-12** (in `S__MnvTune_v1`, a difference of near-equal quantities; 24,345 ULP); every other array ≤ 230 ULP | the same B values; 19 floating-point fields differ in the last digits (`shift/{a,bias_norm_W,magnitude,se}`); every path, label and code digest is equal | **`COMPARE: AGREE (0 differences)`** against `joint-evaluate.json` `b9604502…`: every p, k, B, decision, robustness label and power figure |
| recovery-union `inference_sufficient.npz` (run with the original manifest label, `recovery-union (a), report-only`) | `fd00a803…` | `6ffed091…` | 25 of 52 exactly equal; worst relative difference **2.9e-12** | the same 19 last-digit `shift` statistics; otherwise equal | **`AGREE (0 differences)`** against `resolved-evaluate.json` `8503eab8…` |
| `fig_arrays.npz` (exporter options pointing at durable copies; code root a clean fetch of `556d6dde`) | **`72394a2b…`** | **`72394a2b…`** | **19 of 19 exactly equal; npz byte-identical** | differs only in the 11 fields that record where the inputs were read from | — |

**Why the inference npz are not byte-identical:**
- **Not serialization.** The same writer reproduces `fig_arrays.npz` byte for byte, and the inference zips carry
  fixed 1980 timestamps.
- **The cause is BLAS summation order.** The same extraction, repeated with `OPENBLAS_NUM_THREADS` = 1, 2, 3, 4, 5,
  6 and 8 and the default, gave **eight different digests**.
  - The closest, at 4 threads, has 50 of 52 arrays exactly equal and a worst relative difference of 1.8e-14.
  - Two regenerations with different thread counts also differ from each other.
- The original run's thread configuration is not recorded (its log shows 238 % CPU), so byte identity is not
  achievable from the record.
- **Byte identity is therefore not claimed.** The numerical payloads agree to ≤ 3e-12 relative, and every recorded
  result reproduces exactly from the regenerated inputs.

## 5. G11: a build-time check of the Sec. IV printed values

`docs/analysis-note/check_sec4_receipts.py`, run by `build_all.sh` after the containment stage, checks 14 printed
values against their committed receipts at the printed precision:
- 6.87, 100, 91.2 and 0.679 (macros);
- 95.4, 0.674, 97.7/78.1, 4, below 0.3, 1, 1.4, 74 and 16–31 (prose literals);
- "about half" (20 of 42).

The receipts are `ki84-adopt-20261006/recompute_2d_budget.json`, `coverage-2d-20261005/interim_score.json`,
`ki84-rebuild-20261006/rescore_vl169_toys_vl170.json`, `s5c/d1/d1_summary.json`, `s5n/stage1/dev_receipt.json` and
`s5e/cand/assess_receipt.json`.

- **Fails closed:** a value that cannot be located, or a missing receipt key, fails.
- **Self-test:** each printed value is moved by one unit in its last digit, in the direction that must fail, and every
  perturbation is rejected (16, including the verbal phrase).
- **Tests:** `test_check_sec4_receipts.py` adds specific wrong values (0.664, 96.7, "below 0.2", 16–33) and a missing
  value; all are rejected. `test_build_all.py` stubs the stage the way it stubs containment.
- **Scope:** Sec. IV only. This is not a general framework. Sec. V's release-recomputable values are checked by
  `fig_numbers.py`.
- **Standalone repository:** it has no receipts, so the checker reports SKIP there; the canonical build enforces it.

## 6. Disposition update (the rows that change; corrections record §8 has the rest)

| gap | now | evidence |
|---|---|---|
| G4 AnaTuples | **identity: 2,367 of 2,374 files sha256-identified, 0 mismatches; 7 (all on pscratch OST 61) blocked by hung storage objects**; durable copy **not done (not authorized)**; recommendation and drafts in §7 | §3a, §7 |
| G9 single durable copies | **Fixed and verified.** The s5p archive and `z-cv.npz` now have HPSS copies, verified by stream read-back. | §3 |
| G11 Sec. IV literals | **Fixed and verified.** A build-time check, a self-test and tests. | §5 |
| G12 regeneration from durable storage | **Fixed and verified, with a precisely stated limit.** The inference inputs regenerate from durable copies with the unchanged extractor and reproduce every recorded result exactly; they are numerically equivalent (≤ 3e-12 relative), **not byte-identical** (BLAS thread order). The figure arrays are byte-identical. | §4 |
| G6b proxy rate | **Unchanged: unresolved provenance.** No study run, no convergence claim. | — |

## 7. Remaining storage decision

**Measured capacity:**
- CFS `du` = **1,593 GiB** (1.71 TB, decimal) at 2026-10-09 01:26 UTC, after the W2 addition, against the 3 TB rule.
- HPSS `hsi du` = **376,773,649,398 B** (350.9 GiB, 57 files) at 04:19 UTC after the second copies, and unchanged at
  05:55 UTC, against a 512 GiB quota: about 161 GiB free.

| part | size | fits where, today | recommendation |
|---|---|---|---|
| data AnaTuples + flux/parameter files (1,885 files) | 0.99 TB | CFS: 1.71 → 2.70 TB, under the 3 TB rule with about 0.3 TB left. HPSS: no (161 GiB free) | **Copy to CFS now**, verified against `ANATUPLE-SHA256.tsv`. It is the smaller, irreplaceable half of the event-level inputs and fits the existing rule. Today the copy could cover 1,879 of the 1,885 files: the 6 OST-61 data files (3.04 GB) cannot be read until NERSC repairs OST 61 (draft C), and they would be added then. **Not done: Joseph's go-ahead is required** ("Do not copy the ~0.99 TB data AnaTuples yet"). |
| simulation AnaTuples (489 files) | 10.53 TB | neither: it exceeds the CFS rule, and needs about 10 TiB more HPSS | **First ask MINERvA** whether this earlier production is retained under a version tag (draft B). If not, **request about 11 TiB of HPSS** (draft A) and archive with htar. Until then the MC remains purge-exposed. |

The drafts are in `DRAFT-20261008-anatuple-preservation-requests.md`. **None has been sent.**
- A: the HPSS request to NERSC.
- B: the retention question to MINERvA.
- C: a NERSC help ticket about the 7 unreadable OST-61 files. It is needed in every case: without it, no copy and no
  checksum can include those files.

The checksum manifest (§3a) is useful in every case. It identifies the analysed production exactly, so any future
copy, or MINERvA's answer, can be checked file by file.

## 8. Builds and standalone sync for this branch

{{BUILDS}}

## 9. Independent review

{{REVIEW}}
