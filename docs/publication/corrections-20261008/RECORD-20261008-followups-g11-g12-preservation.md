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
  addition adds 33.8 GB, so about 1,593 GiB (1.56 TiB, 1.71 TB), under the 3 TB rule.
- HPSS: `hsi du` = 373,553,509,414 B (347.9 GiB, 54 files) against a 512 GiB quota. `hpssquota` failed on two login
  nodes (an `lfs quota` subprocess error), so the quota figure is the 2026-10-08 15:33 UTC `hpssquota` reading.

**W2 outputs to CFS** (`publication/release/preservation/preserve_w2_outputs_20261008.sh`). The run used `9ed7954f…`,
the copy in the CFS directory. Review cycle 1 then added a 64-hex digest check and `sha256sum --strict`, giving
`8ce7eba7…`, the committed version. The committed `W2-SHA256SUMS` lines are all well formed, 53 of 53:
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

**Script:** `publication/release/preservation/anatuple_checksum_sweep_20261008.sh`.
- Run 3 and both retries ran `cfb8fe01…`, the version committed in `ebf17439`. Its `dtn01` copy has that digest and
  an mtime of 01:17:34 UTC, 19 s before run 3 started.
- Runs 1 and 2 ran earlier, uncommitted versions. Run 2's added `SKIP`. The nearest committed version is
  `8c92c184`'s (`45592de6…`), committed at 01:13 UTC, after both had started.
- After the runs, two changes were made:
  - `d18fc276…` added the `LC_ALL=C` line;
  - review cycle 1 made a read that yields no valid 64-hex digest go to `MISMATCH.tsv` (`read_failed`) instead of
    being recorded as hashed. That gives `a5c386dc…`, the committed version and the copy now in the CFS directory.
- The fix was tested on a login node with a `sha256sum` shim that fails for one file. That file went to
  `MISMATCH.tsv`, the other hashed correctly, and a resume retried and hashed it.
- The committed manifest was not affected by the defect: all 2,367 digests are valid 64-hex, and 7 were re-hashed
  independently by the reviewer.

The sweep read the exact committed inventory, `anatuple-inventory-20261008.tsv` (2,374 files,
11,523,656,218,592 B). It only READ the AnaTuples on `/pscratch/sd/j/josephrb/minerva/minerva_large_files`.
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
  - At about 06:10 UTC, 17 such `stat` processes remained on `dtn01` (wait channel `cl_sync_io_wait`), every one on an
    OST-61 file. `login05` could not be reached to check.
  - The CFS directory holds 20 empty `.w.*` worker files from the timed-out files. Nothing was deleted (deletion is
    not authorized). They are harmless to a resume, which reads only `SHA256.part`.

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
  for the whole run. The DTN runs were under the POSIX locale, so unaffected.
- **Throughput:** run 3 hashed 1,456 files, 11.12 TB, in 2 h 56 min (1,462 to hash, less 6 deferred; the run-2
  late hash of 16532 landed in the same span): about 1.05 GB/s aggregate over 2 streams. That is no
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
- The frozen design, code and receipt bytes are untouched.
  - Before running, the script checks the extractor (`6ff1d6df…`) and the union design (`f93bdb88…`) digests, and
    refuses on a mismatch.
  - The code and design digests (`2cd98235…`, `55239135…`, `404446eb…`) are not checked before the run. The
    extractor records them in the output manifest, and the comparison finds them equal to the release manifest's.
- Environment: Python 3.11 venv with numpy 1.26.4 and scipy 1.16.3 (the RC4-tested Linux versions). The original
  user-site numpy is no longer present on the login nodes.

**Results** (`publication/release/g12/results/`: the run logs, `compare-*.txt`, `replay-summary.txt`,
`blas-thread-digests.txt`, `replay-json-diff-frozen.txt`, `venv-freeze.txt`):
- **The comparison tool was fixed in review cycle 1** (`compare_sufficient.py` `5c369d30…`). Its "last bits" verdict
  had tolerated integer, boolean and shape differences and changed counts. It now requires every differing array to be
  float, with equal dtype and shape and a relative difference below 1e-9, and every other manifest difference to be a
  `/nulls/*/shift/*` float within the same bound. `test_compare_sufficient.py` fails on the old tool for 6 such cases
  and passes on the new one.
- **The fixed tool was re-run on the cluster outputs.** Its `compare-frozen.txt`, `compare-union.txt` and
  `compare-figs.txt` are byte-identical to the first run's.
- **`replay-summary.txt` was re-run in cycle 1** (login23, 06:27 UTC; all three replays `AGREE (0 differences)`). The
  first run's third block was garbled, for a reason not determined. `blas-thread-digests.txt` was rewritten with
  labels: its first version ended with an unlabeled CPU line from the default run.

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
  - The closest, at 4 threads, has 50 of 52 arrays exactly equal and a worst relative difference of 1.81e-14
    (`results/compare-frozen-blas4.txt`; every thread count is compared in `compare-frozen-blas*.txt`).
  - Two regenerations with different thread counts also differ from each other.
- The original run's thread configuration is not recorded (its log shows 238 % CPU), so byte identity is not
  achievable from the record.
- **Byte identity is therefore not claimed.** The numerical payloads agree to ≤ 3e-12 relative.
- **What "reproduces" means here.** The replay comparator (relative tolerance 1e-12) reports 0 differences.
  - Leaf by leaf, the regenerated frozen `replay.json` equals the release's in 623 of 632 leaves: every p-value, k, B,
    decision, label and power figure.
  - The other 9 are the observed test statistics `T_shape_obs` and `T_total_obs`, which differ by ≤ 5.1e-15 relative
    (`results/replay-json-diff-frozen.txt`, made by `replay_json_diff.py`).

## 5. G11: a build-time check of the Sec. IV printed values

`docs/analysis-note/check_sec4_receipts.py`, run by `build_all.sh` after the containment stage, checks 14 printed
values against their committed receipts at the printed precision:
- 6.87, 100, 91.2 and 0.679 (macros);
- 95.4, 0.674, 97.7/78.1, 4, below 0.3, 1, 1.4, 74 and 16–31 (prose literals);
- "about half" (20 of 42).

The receipts are `ki84-adopt-20261006/recompute_2d_budget.json`, `coverage-2d-20261005/interim_score.json`,
`ki84-rebuild-20261006/rescore_vl169_toys_vl170.json`, `s5c/d1/d1_summary.json`, `s5n/stage1/dev_receipt.json` and
`s5e/cand/assess_receipt.json`.

- **Fails closed:**
  - a value that cannot be located, or a missing receipt key, fails;
  - LaTeX comments are removed before matching (review cycle 1), so a sentence kept only in a `%` comment counts as
    missing;
  - in the canonical layout, a missing receipts directory is a FAIL, not a SKIP (review cycle 1);
  - a "below X" value must be true and tight to one unit (review cycle 1), so "below 0.9" for 0.24 fails.
- **Self-test:** each printed value is moved by one unit in its last digit, in the direction that must fail (both
  directions for "below"), and every perturbation is rejected: 17, including the verbal phrase. There were 16
  before review cycle 1 added the upward "below" case.
- **Tests:**
  - `test_check_sec4_receipts.py` adds specific wrong values (0.664, 96.7, "below 0.2", "below 0.9", 16–33), a
    missing value and a commented-out value, and all are rejected. It also runs the checker in a canonical layout
    without receipts (FAIL) and in a standalone layout (SKIP).
  - `test_build_all.py` stubs the stage the way it stubs containment. Since review cycle 1 it also proves that a
    failing check or self-test stops the build before the page counts: a mutant `build_all.sh` that ignores the
    check's exit status fails that test.
- **Log reading:** the containment stage prints its `RESULT :: PASS` line before this stage runs. A build's verdict
  is its exit status, not that line.
- **Scope:** Sec. IV only. This is not a general framework. Sec. V's release-recomputable values are checked by
  `fig_numbers.py`.
- **Standalone repository:** it has no receipts, so the checker reports SKIP there; the canonical build enforces it.

## 6. Disposition update (the rows that change; corrections record §8 has the rest)

| gap | now | evidence |
|---|---|---|
| G4 AnaTuples | **identity: 2,367 of 2,374 files sha256-identified, 0 mismatches; 7 (all on pscratch OST 61) blocked by hung storage objects**; durable copy **not done (not authorized)**; recommendation and drafts in §7 | §3a, §7 |
| G9 single durable copies | **Fixed and verified.** The s5p archive and `z-cv.npz` now have HPSS copies, verified by stream read-back. | §3 |
| G11 Sec. IV literals | **Fixed and verified.** A build-time check, a self-test and tests. | §5 |
| G12 regeneration from durable storage | **Fixed and verified, with a precisely stated limit.** The inference inputs regenerate from durable copies with the unchanged extractor and reproduce every recorded p-value, B, decision and power figure exactly (9 observed statistics differ by ≤ 5.1e-15 relative); they are numerically equivalent (≤ 3e-12 relative), **not byte-identical** (BLAS thread order). The figure arrays are byte-identical. | §4 |
| G6b proxy rate | **Unchanged: unresolved provenance.** No study run, no convergence claim. | — |

## 7. Remaining storage decision

**Measured capacity:**
- CFS `du` = **1,593 GiB** (1.71 TB, decimal) at 2026-10-09 01:26 UTC after the W2 addition, and the same at
  05:55–06:00 UTC after the sweep, against the 3 TB rule.
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

`origin/main` `ad2716d8` was merged into this branch as `56752a4d`. It brought PR #56, the editorial pass, which
another session merged during this work, and its record PR #57. They share no files with this branch.
- Since then, Joseph has pushed four article-wording commits to both `main`s, ending at `91517331` / `8ecda9e`. They
  touch only `main_paper.tex` and `paper_body.tex`, which this branch does not change, so they were not merged in.
- The G11 checker passes on that newest article text: 14/14, self-test 17.

| check | result |
|---|---|
| canonical `build_all.sh` at `fc0b6e32` (review cycle 1) | **`RESULT :: PASS`**, `tree=clean`, `mode=strict`; **`SEC4-RECEIPTS :: PASS (14/14)`**, `SELF-TEST :: PASS (17 perturbations rejected)`; 123 / 9 / 11 pages. Earlier, at `56752a4d`, it also passed (self-test 16, before cycle 1). |
| tests at `fc0b6e32` | `test_compare_sufficient.py`, `test_check_sec4_receipts.py` and `test_build_all.py`: **63 passed** |
| `generate_manifest.py --at-sha <head> --check` | OK |
| standalone `MINERvA-OmniFold-Analysis-Note` | branch **`sync-prd-followup-g11-20261008`** = **`2f4a6eeff20eadfe70d6f66549c093c8ce4e19e4`**: `0bc07fa9` adds the 4 G11 files on `main` `657d5bd3`, and `2f4a6eef` syncs cycle 1. Every tracked file equals canonical `fc0b6e32` `docs/analysis-note`, apart from `.gitignore` and `AGENTS.md` (`diff -rq`). `build_all.sh`: rc 0, 123 / 9 / 11 pages, with the SEC4 stage reporting SKIP (no receipts there, by design). 43 tests passed, 9 skipped (the receipt tests). The `pdftotext` output of all 3 PDFs equals the canonical build's. **Not merged into the standalone `main`.** |
| preservation script digests | `anatuple_checksum_sweep_20261008.sh` `a5c386dc…` (committed, and in the CFS directory); `preserve_w2_outputs_20261008.sh` `8ce7eba7…` committed (the run used `9ed7954f…`, kept in CFS); `hpss_second_copy_20261008.sh` `a14883f1…`; `verify_tar_stream.py` `64a29996…`. The CFS `README.md` = `50950e66…`, the committed README. |

## 9. Independent review

**Reviewer:** one fresh, read-only subagent (Opus 5.5; independent by session, not by model). It worked in a
detached worktree at the fixed commit and could make cluster reads only, writing nothing outside its own home
scratch directory. Its worktree was clean afterwards (`git status --short` empty).

**Cycle 1, at `e90afb31`: `VERDICT: READY`** (no blocker, no major).
- **Independently reproduced:**
  - G11: the checker, self-test and tests. Five or more of the printed values were re-derived from the receipts with
    the reviewer's own code, including C1/C2 from the raw toys. A wrong value fails the build.
  - G12: all compares re-run on the cluster, matching the committed outputs; the 8 BLAS digests; the sandbox
    masking (all 8,600 link targets under bound durable paths).
  - Preservation: 4 AnaTuple and 3 W2 spot re-hashes match. The committed manifest equals the CFS copy. Inventory
    minus manifest is exactly the 7 OST-61 rows. `verify.txt` matches. The HPSS arithmetic is exact.
  - The drafts are not sent, G6b stays unresolved, and nothing claims byte identity.
- **9 minor findings, all fixed in `fc0b6e32`:**
  1. the `compare_sufficient` last-bits verdict was too permissive;
  2. the SKIP in the canonical layout without receipts;
  3. LaTeX comments were not stripped;
  4. a loose "below" bound passed;
  5. a failed read was recordable as hashed (sweep and W2 scripts);
  6. the TiB slip;
  7. the run-3 count was off by one;
  8. the 4-thread result had no artifact;
  9. the run-time-check wording.
- **6 notes, handled:**
  - the garbled replay summary was re-run;
  - "reproduces" was made exact with a `replay.json` leaf diff;
  - a build test now covers a failing SEC4 stage;
  - the `RESULT :: PASS` ordering is noted in §5;
  - the stale `.w.*` files are noted, not deleted;
  - there are no receipts for the `du` readings and D-state observations. Their outputs are quoted in this record
    and the HPSS arithmetic checks; this stays a limitation.

{{REVIEW_CYCLE2}}
