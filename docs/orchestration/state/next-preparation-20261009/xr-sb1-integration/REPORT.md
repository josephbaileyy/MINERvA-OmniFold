# XR/SB1 evidence integration: the 2D follow-up, XR recovery and SB1 records on `main`

**CITABLE FOR:**
- which delivered heads were integrated, and how;
- the preservation and hash-binding enrollment of their receipts;
- the recomputed scheduler charges;
- the shared-register dispositions;
- one narrow false-positive repair in the receipt-artifact check (§4.3);
- the ownership boundary for the next XR and selective-I/O work.

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- an adoption, re-quote, narrowed claim, KI-85 lift, transfer measurement or changed gate;
- a production or whole-sweep speedup;
- compute, deployment or production-driver authority.

| field | content |
|---|---|
| `Lane` | integration (the only writer of shared status, catalogs, manifests and binding-inventory enrollment for this action) |
| `Decision` | Are these records accurate, durably preserved and safe to integrate, and is there a clear ownership boundary for XR completion and selective-I/O implementation? |
| `Branch` / `Base` | `integrate/xr-sb1-20261011` / `origin/main` `ced3a8db5a8db544436c1f9cf635a8ce79ae73ad` (PR #73) |
| `Incoming heads` | `prep/two-d-followup-20261010` `88e8dc3587c7f743eefa6809dfc11bb85b907073` (PR #74); `prep/xr-recovery-20261011` `8308ce35d52d0d458f0b0998c880374f1082c3e9` (PR #76, contains #74); `run/sb1-20261010` `339e6ab02799bb4a188a855c74585a6486600cf9` (PR #75) |
| `Owner / reviewer` | One owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code. One fresh read-only reviewer (§9). The campaign review's suggested Astra High reviewer is not available in this session |
| `Review budget` | One initial review; at most two focused repair/re-review cycles |
| `Terminal` | PASS, FAIL or INCONCLUSIVE (§12) |
| `Budget` | 6 active h including review and delivery; 3 local core-h; 2 threads; 8 GiB; 3 GiB new scratch; 20 MiB tracked evidence; no cluster job, GPU or training |

`Q` = `docs/orchestration/state/next-preparation-20261009`. `I` = `Q/xr-sb1-integration` (this record).

## 1. Answer

**Yes, with the limits in §10.**
- The three records match their scheduler operands and their independent reviews.
- Their post-review edits are documentary only.
- Every receipt they named is now tracked, either at its delivered bytes or recovered from the cluster at its recorded digest.
- Their bindings are enrolled in the inventory, with the delta enumerated and power-tested.
- The next XR and selective-I/O work have disjoint write sets, and §8 records the boundary.

The scientific state carried onto `main` is unchanged by integration:

| record | outcome as delivered and reviewed |
|---|---|
| SB1 (`Q/sb1-run/`) | **Frozen benchmark PASS** (P, S1, NC, S2, S3, S4). **S5 PASS-AT-TOLERANCE** (max relative difference 6.40e-13 < 1e-8; not byte-identical). **S6 profiling coverage FAIL** (86.93 % < 90 %). S5 and S6 enter no verdict by rule. The measured speedup is **one matched lateral pair** (`Muon_Energy_MINOS:0`, UL 2,604 s vs SL 888 s). Under the guard's `lscpu` refusal, both timed runs very probably trained with **64 LightGBM threads, not 128** (an inference; §7.6 of that record). Independent verification: RESULT VERIFIED: PASS |
| 2D follow-up (`Q/two-d-followup/`) | Task A method **PASS**: the SD/SM calibration supports conditional width agreement only; the original objective has **no feasible route under current inputs**. XR's first attempt was **refused at start** by the package's own allocation check, so every comparison is INCONCLUSIVE |
| XR recovery (`Q/xr-recovery/`) | Admission **PASS**. In-allocation **preflight FAIL** (threadpoolctl → `/sbin/ldconfig` refused by the OI-136 guard). **No scientific fit ran**, and every reproduction comparison and the negative control is **INCONCLUSIVE** |
| still unresolved | publication readiness; the covariance transfer between estimators (KNOWN_ISSUES 88); coverage of the statistical band (KNOWN_ISSUES 85, deferred) |

## 2. Baseline and assembly

- **Refs at start** (2026-10-11T03:39Z, `git fetch --prune`):
  - `origin/main` `ced3a8db`;
  - the three heads above, each equal to the stated SHA;
  - open PRs #74, #75 and #76, all drafts.
  - `main` had moved past the lanes' base `016265cc` by PR #73 (AnaTuple preservation), which touches no file the lanes touch except `MANIFEST.tsv`.
- **Worktree:** isolated, at `MINERvA-OmniFold-xr-sb1-integration-20261011`. The canonical checkout's untracked files were left alone.
- **Assembly:** two `--no-ff` merges.
  - `8308ce35` merged with no conflict. It carries `88e8dc35`, so the 2D follow-up arrives through it.
  - `339e6ab0` had one conflict, in `MANIFEST-overrides.tsv`: two adjacent new authorization rows. Both sides were kept verbatim.
  - Every incoming head is an ancestor of the branch. So are the pinned commits the records cite: `06eae0fe`, `b838fc02`, `07428e5d`, `9ec77fa1`, `d4335d3b` and `2b35ba52`.

## 3. Incoming changes, reviews and post-review edits

| lane | reviews (preserved verbatim in the lane's `review/`) | last reviewed commit | post-review delta |
|---|---|---|---|
| 2D follow-up | admission review at `8378ec23`; re-review at `06eae0fe` (ADMIT); final verification at `eb145ba6` (method PASS; deployment FAIL confirmed; CONFIRMED WITH DISCREPANCIES) | `eb145ba6` | `88e8dc35`: `REPORT.md`, `logs/xr-deploy.txt` and the verification file only (F-2..F-8 wording and record items) |
| XR recovery | admission review at `57b7403c` (ADMIT WITH CHANGES); re-review at `07428e5d` (ADMIT); final verification at `204805d8` (preflight FAIL confirmed; CONFIRMED WITH DISCREPANCIES) | `204805d8` | `8308ce35`: `REPORT.md` and the verification file only (V-1..V-4) |
| SB1 run | admission review at `f7135d31` (ADMIT WITH CONDITIONS); final verification at `4cab15aa` (RESULT VERIFIED: PASS; record REPAIR NEEDED); re-review at `767d0f08` (REPAIRS ACCEPTED) | `767d0f08` | `339e6ab0`: `REPORT.md` and the re-review file only (R1..R3 wording) |

What integration checked, and the result:
- **The post-review deltas.** For each delta the diff stat and the word-level changes were read. No package, launcher, criterion, number in a criterion, or verdict changed after the last review.
- **Frozen packages.** They are byte-identical on the integration tree to their package commits:
  - `Q/sb1-prep` = `d4335d3b` (manifest `f060df81…`);
  - `Q/two-d-followup/xr` = `07428e5d` (manifest `07a74b91…`).
- **The original XR package.** The XR recovery repaired it in place, under its amendment. Its first admitted bytes are preserved in history at `06eae0fe` (manifest `fbca1be8…`), which is reachable from this branch and is what `AUTHORIZATION-20261010-xr.md` binds.
- **Failed attempts.** These are kept unchanged:
  - the five refused `xr_*` jobs and the failed preflight, with their logs, sacct and ledgers;
  - the comparators' INCONCLUSIVE outputs.
- **Historical text.** Every review file is unchanged. In three lane reports, integration added one dated, attributed note each (§4.4).

## 4. Evidence preservation and hash-binding enrollment

### 4.1 Recovered and re-checked bytes

The cluster originals were fetched read-only from login23 with `tar -cf -` over ssh, at 2026-10-11T03:42Z, and hashed locally. No cluster file was written. The evidence map is `I/evidence-map.tsv`: 66 rows, **66 MATCH, 0 DIFF**.

- **SB1.** All 61 rows of the lane's `evidence/SHA256-MAP.txt` equal the fresh cluster bytes and the tracked bytes. The 62nd cluster file, `sb1-operator-2b35ba52/sb1_operate.py`, equals the tracked `Q/sb1-run/operator/sb1_operate.py` (`f626997f…`).
- **XR.** The four receipts the lanes held off the tree are recovered at exactly their recorded digests:

  | cluster file | sha256 | recorded in |
  |---|---|---|
  | `xr-two-d-followup-20261010/admission.json` | `ef8b49b3…` | `Q/two-d-followup/results/xr/README.txt` |
  | `xr-recovery-20261011/admission.json` | `4563871f…` | `Q/xr-recovery/results/preflight-summary.txt` |
  | `xr-recovery-20261011/PF/a1/preflight-receipt.json` | `55ed2b9e…` | same |
  | `xr-recovery-20261011/PF/a1/inventory.jsonl` | `65535693…` | same |

  They are tracked under `I/recovered/`, mirroring their cluster paths.
- **Already tracked.** The preflight's `scontrol-job.txt` (`539a9d78…`) and both `submissions.jsonl` files are `cmp`-identical to their tracked copies.
- **Not tracked by design.** The ten 2D-attempt and two PF Slurm `.out`/`.err` files are kept as digested concatenations in the lanes' `joblogs.txt` (the repository ignores `*.out`/`*.err`).

### 4.2 Enrollment

The reviewed procedure is the one `verify_hash_bindings.py` documents: enumerate the delta before the constant moves; every added binding must verify and be power-tested; the update goes in the same commit as the receipts.

1. **SB1.** Its 27 `*.json.txt` files were renamed to `*.json` with `git mv`, bytes unchanged. That is 26 under `evidence/`, plus the second admission copy under `admission/`.
2. **XR.** The four recovered receipts were added.
3. **Measurement.** `receipt_inventory()` rows were taken with the gate's own `collect`, `localize` and `tracked_paths`:
   - `origin/main`: **144** / `f9dab8dd…`;
   - the integration tree: **148** / `1b610bb3…`;
   - **4 ADDED, 0 removed or repointed, all OK.**

   | added binding | sha256 | bound by |
   |---|---|---|
   | `docs/orchestration/AUTHORIZATION-20261010-sb1.md` | `3beec1da…` | SB1's two admission copies |
   | `docs/orchestration/AUTHORIZATION-20261010-xr.md` | `d368967b…` | the first XR admission |
   | `docs/orchestration/AUTHORIZATION-20261011-xr-recovery.md` | `25deb61b…` | the recovery admission |
   | `setup_salloc_env.sh` | `ea3c6998…` | 15 SB1 receipts and both XR admissions |

4. **Power test.** It ran in a scratch `git clone --shared` with the bumped constants:
   - baseline: rc 0;
   - one hex digit flipped in each binding's receipt: each gives `MISMATCH <path>` and rc 1;
   - after restore: rc 0.
5. **Constants.** `RECEIPT_BINDING_COUNT` and `RECEIPT_BINDING_SHA256` were moved to 148 / `1b610bb3…`, with the enumerated delta in the comment above them. No check was weakened, and no exemption or fixture marker was added.

Supporting files:
- **`logs/binding-delta.txt`:** the row dumps, the contributing receipts and the power test.
- **Other `.json.txt` files.** The other four tracked `*.json.txt` files in the repository were renamed in the scratch clone; the inventory stayed at 148 / `1b610bb3…`, so none of them hides a binding.
- **The preflight receipt** adds no row. `localize()` resolves none of its 10 pairs: they name the frozen worktree, the outroot, the inputs, or repository-relative paths that `localize()` does not resolve.
  - The same holds for the SB1 receipts' module and output pairs. Of UL's 8 pairs, only the canonical `setup_salloc_env.sh` localizes.
  - So the gate verifies these receipts' environment binding only. Their module digests are verified by the packages' own admission tooling, not by this gate (§10).

### 4.3 A false positive in the receipt-artifact check, repaired narrowly

Tracking the receipts as `.json` brought them under `verify_receipt_artifacts.py` (pre-commit), which refused the commit with 4 MISSING bare citations: `j.out` and `j.err` in SB1's `operator-record/attempt-jobs.json` and in the recovered XR `preflight-receipt.json`.

- **Cause.** These are the tails of the Slurm filename patterns `%x_%j.out` and `slurm-%j.err`, which name no file. The checker's `PATHLIKE` started a match right after the `%`. The real job logs are cited by their resolved names (`slurm-59655414.out`, the `sb1_*_<id>.out` files) and are unaffected.
- **Repair.** A match may no longer start immediately after `%` or inside a path token (`(?<![%\w./\-])`). No state, threshold or pinned inventory changed.
- **Measured blast radius.** Over every tracked receipt under `state/` plus the two added here, exactly three receipts' extracted citations change, all of them Slurm patterns:
  - the two above, which lose their false MISSING;
  - `RECEIPT-20260830-k0-7ac0edec-legs-1-5-submission.json`, which loses an OFF-AREA `A.out` from `boot5dG_%a_%A.out`.
- **Counts.** Before: TRACKED 9, MISSING 4, OFF-AREA 29, BY-PATH 7, UNRESOLVED 66. After: 9 / 0 / 28 / 7 / 66. The pinned UNRESOLVED digest `49916d28…` is unchanged.
- **Tests, both directions** (`docs/orchestration/test_verify_receipt_artifacts.py`). A pattern yields no citation, and a real resolved log name beside a pattern is still extracted and still MISSING when untracked. Both fail under the old pattern (negative control) and pass under the fix (29 passed).
- **Log.** `logs/receipt-artifacts.txt`.

### 4.4 Notes added to lane records (dated and attributed; nothing else in them changed)

- **`Q/sb1-run/REPORT.md` §6 "Evidence".** The note records the rename and points to the map. Two links that named `.json.txt` now name the `.json` files. `evidence/SHA256-MAP.txt` is kept as delivered, so its `tracked_path` column names the pre-rename paths.
- **`Q/xr-recovery/REPORT.md` §11** and **`Q/two-d-followup/REPORT.md` B7.** Each note records that the held receipts are recovered, tracked and enrolled.

## 5. Shared registers and navigation

- **`KNOWN_ISSUES.md` 88** gets a dated annotation:
  - the SD/SM calibration supports conditional width agreement only;
  - the objective has no feasible route under current inputs;
  - XR answered nothing, and no fit ran;
  - the transfer stays unmeasured, coverage untested, and publication readiness unresolved.

  The row stays OPEN, and its owner and the keep-and-disclose ruling are unchanged.
- **`KNOWN_ISSUES.md` 92–94 (new, OPEN, owner named).** These register the 2D follow-up's verified construction findings (its A4 items 1, 2 and 5), as its §E.4 proposed:
  - **92 (LOW):** Rvn1pi/Rvp1pi are one shift counted twice in `C_U`;
  - **93 (MEDIUM):** the adopted May sweep's universes used a different MC truth input from their matched CV;
  - **94 (MEDIUM):** the background-template statistics exceed 10 % of the data's Poisson error in 60 of 205 reco bins.

  No product, band, number or adoption changes. Any construction change is Joseph's decision.
- **`OPEN_ITEMS.md` OI-136** gets a dated observation append, not marked solved, with no guard change:
  - XR: threadpoolctl → `ldconfig`;
  - SB1: LightGBM → loky → `lscpu`, and the inferred 64-thread fallback;
  - the `*.py.record` classification proposal.
- **`CATALOG.md`:**
  - outcome lines for the 2D follow-up and SB1 rows;
  - a new routing row for the XR recovery record;
  - a paragraph routing to this record;
  - the 2026-10-11 table of next owned reports (§8).
- **`MANIFEST-overrides.tsv`:** `MACHINE open` rows for `Q/xr-recovery/REPORT.md` (it had none), this record, `Q/xr-linux/REPORT.md` and `Q/selective-io/REPORT.md`.
- **`MANIFEST.tsv`:** regenerated once from source after all edits (§7).
- **Not changed:**
  - `AGENTS.md`, where no scientific state changed;
  - `CURRENT_WORK.md`, which is generated from the control-plane register, and no OI-backed work item exists for these lanes;
  - every publication source, the estimator, the pinned helper and the guard.

## 6. Resource totals, recomputed from scheduler operands

- **Fresh read.** `sacct -X` for the user since 2026-10-09, read-only at 2026-10-11T03:47:51Z on login23 (`logs/sacct-fresh-20261011T034751Z.psv`): exactly **12 jobs**. They are SB1's six, the 2D follow-up's five `xr_*`, and the recovery's one `xrr_PF_a1`.
- **Queue.** `squeue --me -t all` is empty.
- **Method.** `checks/recompute_charges.py` computes ElapsedRaw/3600 × billing/256 exactly, from the fresh rows, and compares each row with the lanes' tracked psv files. Output: `logs/charges.txt`.

| record | jobs | recomputed charged CPU node-h | reported | tracked rows equal to fresh |
|---|---|---|---|---|
| SB1 | 6, all `COMPLETED 0:0` | **1.16275391** | 1.162754 | 6/6 |
| XR, first attempt | 5, all `FAILED 3:0` | **0.00134983** | 0.0013498264 | 5/5 |
| XR recovery preflight | 1, `FAILED 1:0`, 74 s, billing 12 | **0.00096354** | 0.0009635417 | 1/1 |
| XR cumulative | 6 | **0.00231337** of 6.4 | 0.0023133681 | |
| GPU allocations | | **0** | 0 | |

- **The divisor.** A regular node bills 256: SB1 UL/SL show `billing=256,cpu=256,node=1`. iris's change for the SB1 window (2035.0 → 2036.1, SB1 record §6) fits /256 (1.16) and excludes /128 (2.33).
- **Local resources.** The lanes' local resource figures are self-reported (CPU-time sums and wall clocks) and are not recomputable from scheduler operands.

## 7. Checks

All checks ran on the integration tree:
- fake Slurm only, with tripwire stubs for `sbatch`, `scancel`, `squeue`, `sacct`, `scontrol`, `srun` and `salloc` first on `PATH`;
- `OMP_NUM_THREADS=1`;
- a scratch `TMPDIR`;
- at most two processes at a time.

| check | interpreter | result |
|---|---|---|
| XR package suite `Q/two-d-followup/xr/tests/test_xr.py` | Python 3.13.7, ROOT 6.36, scikit-learn 1.8.0, LightGBM 4.6.0, numpy 2.4.6 (the XR lane's test environment, used read-only) | **42 OK, 0 skipped** (175 s) |
| SB1 operator `Q/sb1-run/operator/test_sb1_operate.py` | Python 3.12 | **5 OK** |
| SB1 package suites `Q/sb1-prep/tests/` | Python 3.13.7, ROOT 6.36 | **16 / 10 / 29 / 7 OK** (branch select, guarded, launch chain, consistency), 0 skipped |
| N2 producer provenance / N2 harness | 3.13 + ROOT / 3.12 | **31 / 22 OK** |
| OI-136 ratchets; guard inventory | 3.12 | **17 OK**. AST rooted 17, 0 unlisted. Fail-open 16 (`7aa29431…`, unchanged). Probe candidates 145 (144 at the previous integration; the added file is no fail-open) |
| `verify_hash_bindings.py` | 3.12 | **ALL BINDINGS INTACT**, inventory 148 / `1b610bb3…`, rc 0 |
| `nd-unfolding/tests/test_hash_bindings.py` | 3.12 | **33 passed** |
| `verify_receipt_artifacts.py`; `test_verify_receipt_artifacts.py` | 3.12 | 0 missing (TRACKED 9, OFF-AREA 28, BY-PATH 7, UNRESOLVED 66 pinned, unchanged); **29 passed** (§4.3) |
| `control_plane_lint.py` | 3.12 | PASS, after `--write` regenerated `control-plane/source-record-inventory.tsv`. Only OI-136's row digest moved, from the dated append |
| `live_doc_indexed.py --unrowed` | 3.12 | 0 tracked docs without an overrides row |
| `generate_manifest.py --check --at-sha HEAD` | 3.12 | after the regeneration, at the committed head (§9 lists the head reviewed) |
| frozen packages | git | `git diff --quiet d4335d3b HEAD -- Q/sb1-prep` and `07428e5d HEAD -- Q/two-d-followup/xr` both hold; `manifest --check` of the XR package rc 0 |
| tripwire | | **0 hits**: no real `sbatch`, `scancel`, `squeue`, `sacct`, `scontrol`, `srun` or `salloc` was invoked by any suite |

The only cluster contact was read-only, from login23: the `tar` reads of §4.1, and one `sacct`/`squeue` read (§6). No job was submitted or cancelled, and nothing was written on the cluster.

## 8. Dispatch and ownership

Registered in `CATALOG.md` (2026-10-11 table) and `MANIFEST-overrides.tsv`. Neither lane is launched. Registration grants no compute, experiment, adoption, claim-scope or production-driver authority; each lane's scope and budget come from its own dispatch.

| report | owner | writes | does not write |
|---|---|---|---|
| `Q/xr-linux/REPORT.md` | XR owner | a new XR package under `Q/xr-linux/`; one dedicated `docs/orchestration/AUTHORIZATION-*` amendment, plus the one override row and one routing row the LIVE-index gate requires for that record | the frozen `Q/two-d-followup/xr/` package (`06eae0fe`/`07428e5d`), the earlier outroots, `Q/two-d-followup/`, `Q/xr-recovery/`; the guard, the helper, the driver |
| `Q/selective-io/REPORT.md` | selective-I/O owner | the narrowly scoped, opt-in selective-read change to the supported 2D driver (`2d-unfolding/unfold_2d_omnifold_unbinned.py`) and its tests | the pinned OmniFold helper, the guard, the estimator, the default all-branch behaviour; `Q/sb1-prep/`, `Q/sb1-run/` |
| shared surfaces | integration | `KNOWN_ISSUES.md`, `OPEN_ITEMS.md`, `CATALOG.md` (except the scoped rows above), `MANIFEST.tsv`, `MANIFEST-overrides.tsv`, the binding-inventory constants in `verify_hash_bindings.py` | lane subtrees |

Inputs each lane starts from:
- **XR:** `Q/xr-recovery/REPORT.md` §9, its six reopening requirements.
  - Remove the child launch from `check_environment` without widening the guard.
  - Exercise the whole PF path and the end-to-end fixture tests on Linux under the guard.
  - Audit the fit path.
  - One new preflight and window.
  - A new package, manifest and outroot, with an independent admission review that carries N-1.
  - Keep the comparisons, the 1e-8 criterion, the control, the references and the release order unchanged.
  - Budget arithmetic: 6.4 − 0.0023134 = 6.3977 node-h remain under the cumulative cap, if Joseph amends the grant again.
- **Selective I/O:** `Q/sb1-run/REPORT.md` §10, the recommended action.
  - Port prototype 1's derived-branch selection into the four loaders as an opt-in path that refuses on any active/derived mismatch.
  - Use the J1 controls as regression tests.
  - Also read §11 items 2 and 6: the ROOT 6.28 test portability, and the explicit-`n_jobs` remedy that belongs to the helper's owner, not to this lane.

**Can they start concurrently? Yes, under three conditions, each measured or derived here:**
1. **Disjoint writes.** The two write sets above share no path. Shared surfaces stay with integration.
2. **XR pins the driver it is testing.** X0 asks whether *today's* driver regenerates the quoted exact central. That driver is the blob `3cc5adc7…` on `main` now, the one `07428e5d`'s manifest and the preflight receipt name.
   - The XR owner's package must keep naming that blob, either from a base commit before any selective-I/O merge or as an execution-only record copy, as XR already does for `d1bc8813`.
   - It must not silently adopt a modified driver.
   - The selective-I/O lane must not merge a driver change into an XR package.
3. **A driver change has a known blast radius on frozen packages.** Measured in a scratch clone, appending one comment line to the driver:
   - turns the committed `Q/sb1-prep/tests/test_package_consistency.py::Plan.test_the_manifest_is_current` red;
   - makes `Q/two-d-followup/xr/xr_admit.py manifest --check` report `OUT OF DATE` (rc 3).

   Both packages are immutable and correctly pinned to their commits, so this is expected, not a defect of either lane. It does not move the receipt-binding inventory or raise a MISMATCH: the frozen receipts bind the driver under their own worktree paths.

   The selective-I/O owner must not edit those packages or their tests. How their at-HEAD consistency checks are treated once the driver changes (for example, checked at their package commit) is decided by integration when that lane is merged.

Cluster coexistence follows the SB1/XR precedent: separate worktrees and outroots, and job identification by WorkDir, never by name. Neither lane may move the canonical checkout while the other has pending jobs.

## 9. Review

Pending: one fresh read-only reviewer, at the fixed head named here after the review.

## 10. Residual limitations

- **The XR fit path has never run in an allocation.** No reproduction question (X0, X0′, X1, L0, L1) is answered, and the negative control is unexercised.
- **Open review items.**
  - XR N-1 (MINOR, not repaired): a ledger header lacking `State`/`JobName` crashes, rc 1, instead of exiting 6.
  - XR N-2 (NOTE): a forged environment would pass the gate.
  - 2D F-1 (MATERIAL, recorded): its reviews missed the `TRES` defect.
- **SB1 limits.**
  - The 64-thread training is an inference: the receipts do not record the trainer's thread count, and `environment.packages` is null.
  - The 4× sacct MaxRSS difference is unexplained.
  - The rerun envelope is unmeasured.
  - J1's vertical timings are not a matched pair.
  - One fixture test (`test_branch_select.py:128`) is not portable to ROOT 6.28; the run path is unaffected.
- **SB1's operator record.** The sacct-derived figure is the one of record. H1's in-job charge undercounts H1 by 9 s × 2/256.
- **Gate coverage of frozen receipts.** The receipt-binding gate verifies only the canonical-checkout binding (`setup_salloc_env.sh`) of the SB1 and XR receipts. Their executed-module, input and output pairs name frozen worktrees, outroots or repository-relative paths that `localize()` does not resolve. Those digests were checked by each package's admission and strict-identity tooling at run time and by the lanes' reviewers, not by this gate.
- **Evidence durability.** The integration tracks every receipt the lanes named. The cluster outroots and worktrees remain on purgeable `/pscratch`, as the lanes left them. Only the tracked copies are durable; the 171-GB input and the full CFS inputs are not copied.
- **Post-verification corrections.** The lanes' corrections are not re-reviewed by their own reviewers (none remained). This integration's reviewer read them as part of the delta.
- **Local resources.** The lanes' local resource figures are self-reported.

## 11. Resources (this integration)

Pending; filled at delivery.

## 12. Terminal

Pending review.
