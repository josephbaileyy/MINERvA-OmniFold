<!-- Preserved verbatim from the reviewer's final message (2026-10-11T04:23Z). The only transport change: one `&lt;` that the relay
     escaped is restored to `<` in the quoted regex of section 1b. -->
# Review: XR/SB1 evidence integration, `b80c328a`

| field | value |
|---|---|
| Reviewer | Fresh, independent, read-only reviewer: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code subagent |
| Target | `integrate/xr-sb1-20261011` @ `b80c328ac4ef1f81651fc79d759667ddac81a9ac`, equal to `origin`'s copy at start and end. Base `origin/main` `ced3a8db5a8db544436c1f9cf635a8ce79ae73ad` |
| UTC start / end | 2026-10-11T04:09:10Z / 2026-10-11T04:23:21Z |
| Worktree | Own detached worktree `…/scratchpad/xs/reviewer/rv`. `git status --porcelain --ignored` showed **0 lines at start and 0 at end**. It was then removed: `git worktree list` shows no reviewer entry. Mid-review, an ignored `docs/orchestration/__pycache__/verify_hash_bindings.cpython-312.pyc` appeared. My own `python3 -I` import helper wrote it, because `-I` ignores `PYTHONDONTWRITEBYTECODE`. I deleted it before the end-status read. The power tests ran in two scratch `git clone --shared` copies, which were deleted afterwards. I wrote nothing in the canonical checkout or in the owner's worktree. Nothing was committed or pushed |
| Cluster reads | **Yes, read-only, on login23 via `ssh -o BatchMode=yes saul.nersc.gov`**, at 04:17:31Z and 04:17:44Z. They were `sha256sum` of 66 cluster files plus 4 more, one `ls`, one `sacct -X` and one `squeue --me`. No sbatch/srun/salloc/scancel; nothing was written on the cluster |
| Local compute | About 0.1 core-h, `OMP_NUM_THREADS=1`, at most one process at a time, scratch `TMPDIR` |

## Verdict: **PASS WITH CHANGES**

There are no MATERIAL findings. Three MINOR wording and record defects should be fixed; none blocks the merge. Every number and SHA I re-measured matches the record. That includes the merges, the renames, the evidence digests (re-hashed against the cluster), the binding delta, the receipt-checker blast radius, the charges and the gates.

## Findings

| id | severity | finding | operand / reproduction | disposition requested |
|---|---|---|---|---|
| R-1 | MINOR | The integration's link edit left a self-contradicting sentence in a lane record. `Q/sb1-run/REPORT.md:125-128` now says "The byte-identical copy is [`admission/admission.json`] … It is stored with `.txt` so that `verify_hash_bindings.py` … does not count it … would move `RECEIPT_BINDING_COUNT` from 144 to 145." The link was changed, but the sentence explaining the `.txt` suffix was not. No dated note sits at this location: the §6 note covers it only implicitly, and it says "nothing else in it changed". | `git diff f0fb8e8f b80c328a -- Q/sb1-run/REPORT.md`; `sed -n 118,132p` | Add a short dated integration note at :126, e.g. "superseded 2026-10-11: renamed to `.json` and enrolled, 144 → 148". Or keep the old link text and mark it historical. |
| R-2 | MINOR | The owner on KNOWN_ISSUES rows 92, 93 and 94 is "the 2D uncertainty owner". That role exists nowhere else in the repository: `git grep -i 'uncertainty owner'` hits only these three rows and the 2D follow-up's lower-case "the uncertainty owner" at :250. No CATALOG or dispatch row registers it, so in practice the rows are unowned. By contrast, KI-88 names Joseph and KI-91 names "the 2D lane". | `git grep -n -i 'uncertainty owner' -- '*.md'` | Name a registered owner, e.g. "Joseph (scientific owner); construction lane to be dispatched", or route the rows to an existing CATALOG owner row. |
| R-3 | MINOR | The `PATHLIKE` comment in `verify_receipt_artifacts.py:77-83`, and REPORT §4.3, describe the measured population as "every tracked receipt plus the two receipts that integration adds". Integration actually adds **30** scanned `.json` receipts: 27 renamed plus 3 recovered, taking the count from 451 to 481. The result itself holds over the true population. | My own old-vs-new regex diff over all 481 `state/**/*.json`, and over all 5,133 tracked `*.json*` files: exactly 3 files change in both. | Correct the wording to "all 481 receipts scanned on the integration tree (451 + 27 renamed + 3 recovered)". |
| N-1 | NOTE | The CATALOG SB1 row says "frozen benchmark PASS on one matched lateral pair". The one-pair scope belongs to the timed comparison (S2–S4/speedup). S1 also covered the vertical and CV patterns. The wording under-claims, it does not over-claim, and it does end "not a sweep or production speedup". REPORT §1 states it precisely. | `git diff f0fb8e8f b80c328a -- docs/orchestration/CATALOG.md` | Optional: "frozen benchmark PASS; the speedup is one matched lateral pair". |
| N-2 | NOTE | Three checks in §4.1 are stated in prose but appear in no tracked artifact: the 62nd file `sb1_operate.py` `f626997f…`, `scontrol-job.txt` `539a9d78…`, and the two `submissions.jsonl` files. I re-verified all four against the cluster, and they hold (see below). | Cluster `sha256sum` vs local `shasum` | Optional: append these rows to `evidence-map.tsv` or to a log. |
| N-3 | NOTE | The /256 argument (§6) uses the iris delta 2035.0 → 2036.1 (20:00Z–01:41Z). The five first-attempt `xr_*` jobs (22:45Z–00:24Z, 0.00135 node-h) also fall inside that window. This is negligible and does not change the conclusion: the expected Δ at /256 is 1.164, inside 1.1 ± 0.1, while /128 would give 2.33. | `sacct` Start/End vs SB1 §6 iris times | Optional disclosure. |
| N-4 | NOTE | §8 condition 3 says the binding gate is unaffected "because the frozen receipts bind the driver under their own worktree paths". That reason is incomplete. `sb1-prep/launch/ADMISSION-PROPOSAL.json` and both `manifest/expected-code.json` files name the repository-relative driver path at `3cc5adc7…`, but in a `{path: digest}` map form that `collect()` does not harvest. The measured claim itself (no MISMATCH, inventory unchanged) is reproduced. | `git grep 3cc5adc7`, plus the driver-edit probe below | Optional: state both reasons. |
| N-5 | NOTE | 37 tracked `*.jsonl` files carry sha256 pairs, the recovered `inventory.jsonl` among them. The gate globs `*.json` only. This is pre-existing gate scope (guard inventories), not a concealment by integration. | `git ls-files \| grep jsonl \| xargs grep -l sha256` | None for this integration. |

## What I verified, with the numbers reproduced

**1. Merge fidelity.**
- **Parents.** `65b11a35^2` = `8308ce35`; `f0fb8e8f^2` = `339e6ab0`; `b80c328a^` = `f0fb8e8f`.
- **First merge.** Re-running `git merge-tree --write-tree ced3a8db 8308ce35` gives tree `a5a2f497…`, identical to `65b11a35^{tree}`.
- **Second merge.** Re-running it gives exactly one conflict, `MANIFEST-overrides.tsv`, and the result differs from `f0fb8e8f` in that file only. The resolution is the union of both sides: the two XR LIVE rows and the SB1 LIVE row, verbatim.
- **Integration delta** (`git diff -M100% --name-status f0fb8e8f b80c328a`): 27 R100 (26 `evidence/` + 1 `admission/`), 12 A, 12 M.
  - All 27 renames are blob-identical (`rev-parse` compared pairwise).
  - The only lane files modified are the three lane REPORTs, each getting one dated note, plus the 2 SB1 link edits.
  - No `review/` file was touched.
- **Lane post-review deltas.** These are REPORT, log and verification files only:
  - `eb145ba6..88e8dc35`: 3 files;
  - `204805d8..8308ce35`: 2 files;
  - `767d0f08..339e6ab0`: 2 files.
- **Ancestry.** All nine cited pins are ancestors of HEAD.
- **PR #73 overlap.** It shares only `MANIFEST.tsv` with the lanes.

**1b. Receipt-artifact checker.**
- **Logic.** The new lookbehind `(?<![%\w./\-])` only removes matches that start right after `%`. A start inside a token was already subsumed by the token-start match, because `findall` scans left to right and the character class is closed. So this is a precision fix, not a weakening.
- **Blast radius.** It changes exactly 3 receipts:
  - `RECEIPT-20260830-k0-…`, which loses `A.out`;
  - `attempt-jobs.json`, which loses `j.err`/`j.out`;
  - `preflight-receipt.json`, which loses `j.err`/`j.out`.
- **Gate on the integration tree.** TRACKED 9 / MISSING 0 / OFF-AREA 28 / BY-PATH 7 / UNRESOLVED 66, digest `49916d28…` (pinned), rc 0. Tests: 29 passed.
- **Negative control** (old pattern restored in a scratch clone): 5 failed, including both new tests, and the gate shows MISSING 4 / OFF-AREA 29.

**2. Hash-binding enrollment.**
- **Inventory.** Computed with the gate's own `collect`/`localize`/`tracked_paths`/`receipt_inventory` from each tree's own gate file:
  - base: **144 / `f9dab8dd…`**;
  - target: **148 / `1b610bb3…`**;
  - delta: **4 ADDED, 0 removed, 0 repointed, all verify**.

  | added binding | sha256 | bound by (receipts) |
  |---|---|---|
  | `AUTHORIZATION-20261010-sb1.md` | `3beec1da` | 2 |
  | `AUTHORIZATION-20261010-xr.md` | `d368967b` | 1 |
  | `AUTHORIZATION-20261011-xr-recovery.md` | `25deb61b` | 1 |
  | `setup_salloc_env.sh` | `ea3c6998` | 17 (15 SB1 + 2 XR) |

- **Pre-existing drifts.** The 4 BAD rows are the same on base and target, and all are in `KNOWN_PREEXISTING`.
- **Gate and tests.** `verify_hash_bindings.py`: ALL BINDINGS INTACT, rc 0. `test_hash_bindings.py`: 33 passed.
- **My own power tests** (scratch clone), each followed by a restore to rc 0:
  - appending one byte to `AUTHORIZATION-20261010-xr.md`: `MISMATCH`, rc 1;
  - `git rm` of the recovered recovery admission: 147 / `e585c11d…`, INVENTORY CHANGED, rc 1;
  - renaming both SB1 admission copies back to `.json.txt`: 147 / `24031547…`, rc 1.
- **Other concealment.** Renaming the 4 other tracked `*.json.txt` files to `.json` leaves 148 / `1b610bb3…`, so no binding is concealed there.
- **Localize claims.** The preflight receipt has 10 pairs and 0 localize. UL has 8 pairs; only `setup_salloc_env.sh` localizes.

**3. Evidence preservation.**
- **Map.** `evidence-map.tsv` has 66 data rows (27 sb1-renamed, 35 sb1-unchanged, 4 xr-recovered). Each tracked file's sha256 equals its recorded digest, and every one is tracked.
- **Cluster re-hash.** Today's cluster sha256 of all 65 distinct cluster paths equals the map for **66/66 rows**.
- **Extra files.** `sb1-operator-2b35ba52/sb1_operate.py` = `f626997f…`, equal to the tracked copy. The cluster `submissions.jsonl` files (`12d08849…`, `4d673e7c…`) and `scontrol-job.txt` (`539a9d78…`) equal their tracked copies.
- **Recovered XR receipts.** These match the lane-recorded digests:
  - `ef8b49b3…` (`README.txt:15`);
  - `4563871f…`, `55ed2b9e…`, `65535693…` (`preflight-summary.txt:3-5`).

**4. Charges.**
- **Recomputed** with my own awk (billing/256 × ElapsedRaw/3600) from the tracked fresh psv:
  - SB1 **1.1627539063**;
  - XR first attempt **0.0013498264**;
  - PF **0.0009635417**;
  - XR cumulative **0.0023133681**;
  - remaining 6.3976866.
- **My own `sacct -X` at 04:17:44Z.** The same 12 jobs, with identical State/ExitCode/ElapsedRaw/AllocTRES. `squeue` was empty, and there was no `gres/gpu`.
- **Divisor.** /256 is supported: UL/SL show `billing=256,cpu=256,node=1`, and the iris delta fits /256 and excludes /128 (N-3).

**5. Shared registers.**
- **KNOWN_ISSUES 92–94.** Faithful to 2D follow-up A4 items 1, 2 and 5 and to E.4: 0.088 %; 0.879 / 6.3 % / 0.98 σ_ML / 0.68 vs 0.13 / 3.0e-7; eB/√D median 0.072, p84 0.125, max 0.30, 60 of 205 bins.
- **KI-88 annotation.** Faithful to A1/A5/§E.2 and to XR recovery §1/§6. The row stays OPEN with its ruling unchanged.
- **OI-136 append.** Faithful to XR recovery §6 and SB1 §7.6. The 64-thread figure is labelled an inference, and the append is not marked solved.
- **CATALOG.** It states that nothing adopts a measurement, narrows a claim, lifts KI-85, measures a transfer or authorizes compute. Every one of the brief's distinctions is explicit somewhere (SB1 PASS / S5 PASS-AT-TOLERANCE / S6 FAIL / one pair / inferred 64 threads / XR preflight FAIL / no fit / INCONCLUSIVE / unresolved readiness, transfer and coverage).
- **Restatements.** The SB1 figures restated in REPORT §1 match SB1 §7: 6.40e-13; 86.93 %; 2,604 / 888 s.

**6. Dispatch.**
- **Write sets.** The XR and selective-I/O write sets are disjoint. Only the XR owner gets a MANIFEST-overrides.tsv and CATALOG row, so the adjacent-row conflict seen in this merge cannot recur between the two lanes. `state/` documents need no override row (`needs_row` excludes `state/`).
- **Driver pin.** The driver blob `3cc5adc7…` equals the one named in the XR and SB1 manifests and in the preflight receipt.
- **One-line driver edit** (scratch clone):
  - `test_package_consistency` FAIL (`test_the_manifest_is_current`), rc 1;
  - `xr_admit.py manifest --check` "OUT OF DATE", rc 3;
  - binding gate rc 0 at 148 / `1b610bb3…` with no MISMATCH;
  - the OI-136 ratchets were also unaffected (17 passed).

  The three conditions are therefore justified.

**7. Gates, each rc 0 read directly rather than through a pipe.**
- `generate_manifest.py --check --at-sha b80c328a`: OK, 2202 rows.
- `control_plane_lint.py`: PASS.
- `live_doc_indexed.py --unrowed`: 0.
- `test_hash_bindings.py`: 33 passed.

**8. Forbidden edits.** None. The delta touches nothing under `docs/analysis-note/`, `publication/` or `nd-unfolding/`. It leaves untouched the driver, the pinned helper, the guard, `Q/sb1-prep/` (`git diff --quiet d4335d3b`) and `Q/two-d-followup/xr/` (`--quiet 07428e5d`). Manifest digests: `f060df81…` and `07a74b91…`; the original package at `06eae0fe` is `fbca1be8…`.

**9. REPORT numbers and SHAs.** Every head, pin, digest, count and charge listed above matches. PRs #74, #75 and #76 are drafts and #73 is merged (`gh pr list`).

## What I did not check

- **Lane science.** I did not re-review it. The lane reviews were reused, as the brief instructs.
- **Suites I did not run.** These include:
  - the XR suite (42) and the SB1 package suites;
  - the SB1 operator and N2 producer/harness tests;
  - the guard inventory, so I did not re-measure probe candidates 145 or fail-open `7aa29431…`.

  I did run the OI-136 ratchets once, on the driver-edited clone only.
- **Records I did not reproduce.** The fake-Slurm tripwire record, the owner's `tar` fetch, and the iris readings themselves.
- **§10 lane limitations.** These are restated limitations that I did not re-derive.
- **REPORT §9, §11 and §12.** These are pending by design.
