# Independent review: next-preparation integration (`2a394cd1`)

- **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh read-only Claude Code subagent. It did not write any of the work under review. It is not cross-provider independent.
- **Fixed commit:** `2a394cd1fff0dd6033086fd986f83b44a123cdbb` on `integrate/next-preparation-20261009`. Base: `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269`.
- **Time:** 2026-10-10T03:36:11Z to 03:50:33Z (UTC).
- **CPU:** about 0.15 core-h, at most 2 threads per command (2 only for the build). Peak RAM was well under 1 GiB. Scratch was under 0.1 GiB, plus the worktree.
- **Worktree:** a detached worktree at `scratchpad/review-wt`.
  - At the start, `git status --porcelain --untracked-files=all` was empty.
  - At the end, the same command was still empty, and HEAD was still `2a394cd1`. `--ignored` showed 41 entries, all gitignored: `__pycache__`, `.pytest_cache` and the LaTeX build products/PDFs under `docs/analysis-note/`.
  - The mutation clone (`git clone --shared`, in scratch) had 0 changes after I restored it. I deleted it, then removed the worktree with `git worktree remove --force`. `worktree list` no longer shows it.
- **Boundaries kept:** I touched no other worktree and used no cluster, GPU, training or Slurm. In the canonical repo the only commands were `git -C … worktree add/remove`. I read the standalone note repo with `rev-parse`/`ls-tree`/`log` only.

## Verdict: **PASS WITH CHANGES**

I found no MATERIAL defect:
- Assembly is exact.
- The manifest is generated from source.
- R1 and R2 are correct, within scope and each tested in both directions.
- The guard × structure dependency is really exercised on the real files.
- Every suite matches §4.4 with 0 skips.
- The registers do not mark OI-136 solved or KI-90 closed.
- The publication sources are equivalent, and the build passes at the fixed commit.

Three MINOR items should be fixed before merge. F1 is a wrong resource figure. F2 makes KI-89 and KI-90 claim the change has landed on `main`, which is not yet true at the fixed commit. F3 is the §7 routing table: it drops conditions from the lane reports and from the 10-09 ruling. None of them makes the integration's code or test claims false.

## Findings

| id | severity | file:line | finding | evidence | suggested repair |
|---|---|---|---|---|---|
| F1 | MINOR | `Q/integration/REPORT.md` §10, "tracked bytes added by this session ≈ 40 KiB" | The resource figure is about 3.6× low. | Summed over `dd73de73..2a394cd1`: new files total 98,879 B (REPORT 26,159; `logs/` 57,053; new test 8,995; `checks/` ≈ 6.7 k). Modified files grow by 48,707 B net, of which `MANIFEST.tsv` is +39,578. Total ≈ 147.6 kB ≈ **144 KiB**. | Re-measure and correct the §10 row (the PET lane made the same kind of correction in `d9a460c6`). |
| F2 | MINOR | `KNOWN_ISSUES.md:79` (row 89 status, "Landed on `main` through the next-preparation integration") and `:80` (row 90, "landed on `main` through the next-preparation integration") | At the fixed commit these words are not true. The rows sit on an unmerged integration branch, and §9 delivery is still "Pending review". The guard lane's proposed text (guard REPORT §7) said "not yet on `main`". If the merge is declined or changed, a shared register states a false fact. | `git log` puts 2a394cd1 on `integrate/next-preparation-20261009`. REPORT §9 says "Pending review". | Say "delivered by the next-preparation integration (PR …)" with no tense claim. Or add the merge commit in the delivery step, after the merge exists. |
| F3 | MINOR | `Q/integration/REPORT.md` §7 table; `CATALOG.md` next-session rows | The routing preconditions are weaker than their sources in three places. **(a) sb1-prep** drops speed's relevance condition. Speed REPORT:22 and §15 say SB1 "only matters if option (b) 'measure the transfer' or option (c)'s matched seed-1 sweep is to be priced; it changes nothing for keep-and-disclose or N2". The 10-09 ruling does not authorize transfer measurements, so a reader of §7 or CATALOG does not learn that this session has no current consumer. **(b) two-d-path** lists the transfer, re-quote, central change, N2 and KI-85 lift as "each Joseph's decision". The ruling (closeout §11) says they are **not authorized**. The row also omits "change scientific gates, or reopen terminal campaigns". **(c) d-id** omits gbdt §14's "0 Slurm, one owner and one fresh reviewer" and the §10.3 endpoint-scope question. No text grants authority, so this is fidelity, not a scope violation. | Speed REPORT lines 22 and 470–472; closeout REPORT §11 quote; gbdt REPORT lines 23 and 571–577. | Add the three missing clauses to §7, plus a one-clause pointer from each CATALOG row. |
| F4 | NOTE | `2d-unfolding/uq/coverage_fixed_truth/n2/harness.py:94-102` (R2) | `Path.resolve()` follows symlinks, and an absolute `rel` replaces `top`. Two inputs that the old string test refused are now admitted: an **absolute path inside the checkout**, and a committed path such as `elsewhere/foo.md` that is a **symlink to a canonical** `docs/orchestration/AUTHORIZATION-…` record. In both, the admission record's stated `path` is not the file checked. This is not an authority bypass: the checked target must be a committed `AUTHORIZATION-`/`DECISION-` file under `docs/orchestration/` with the stated digest. All the stricter cases behave correctly: `..` escapes, an empty path, a directory, and a symlink inside `docs/orchestration/` pointing elsewhere. Nothing that legitimately passed before fails now. | A probe subclassing `Harness`, run in a scratch clone, printed: `absolute-inside` rc=0; `dot-inside` (`docs/orchestration/./sub/../AUTH…`) rc=0; `empty` rc=3; `dir-only` rc=3; `symlink-in-docs-to-elsewhere` rc=3; `symlink-elsewhere-to-canonical` rc=0 "admission holds". | If the stated path should be the checked path: refuse an absolute `rel`, and require `norm == posixpath.normpath(rel)`, or refuse when any component is a symlink. Add these two cases to the R2 test. Otherwise accept the current behaviour as recorded. |
| F5 | NOTE | `Q/integration/REPORT.md` §3 table (gbdt row) and distinction 2 | (a) The table calls #7 and #8 "the cost repairs". In gbdt REPORT §11, #8 is a branch-B declarability and tie-order rule, not a cost repair. (b) "The lane's own table shows the dependence. At 24, 120 or 300 replicates … 5.7×, 28× or 71×." These multiples are in `pet/results/design_cost.json` (`events.inventory_multiples_for_independent_validation`: 5.664 / 28.32 / 70.80), not in a table in pet REPORT. The numbers themselves are right. | `grep` of pet REPORT finds none of 5.66, 28.3 or 70.8. They are found in the JSON. | Reword: "#7 (cost) and #8 (branch-B rule)", and "the lane's `design_cost.json`". |
| F6 | NOTE | `Q/integration/REPORT.md` §4.2, "HEAD, which must contain `b19b5e91`" | The code requirement is `21c97390`, which changed `fixed_truth_toy.py` to `8bd28807…`. `b19b5e91` adds only a test. The statement is harmless because `b19b5e91` descends from `21c97390`, but it names the wrong reason. | `git show --stat b19b5e91` shows a test-only change. | Name `21c97390` (or "the integration head"). |
| F7 | NOTE | §6, "blob-identical" | The blob claim holds. However, `docs/analysis-note/test_build_all.py` is mode 100755 in the canonical repo and 100644 in the standalone. This predates the integration: the base pair `5ac9706a`/`ad3fb800` shows the same. | `ls-tree` mode tally: canonical 119×100644 + 1×100755; standalone 122×100644. | Optional. Mention it, or align the mode in a later sync. |

## What I verified (commands and results)

1. **Assembly.**
   - All six lane heads are ancestors of `2a394cd1` (`merge-base --is-ancestor`).
   - Each lane's changed-path set vs `5ac9706a`, excluding `MANIFEST.tsv`:

     | lane | paths |
     |---|---|
     | publication | 20 |
     | guard | 41 |
     | structure | 29 |
     | speed | 46 |
     | gbdt | 9 |
     | pet | 8 |

     Together that is 153 unique paths with no overlap (`uniq -d` empty). The sets are disjoint, as §2 says.
   - Every path is blob-identical to its lane head at the merged tree `dd73de73`, with 0 differences.
   - At `2a394cd1` exactly 7 paths differ from their lane head, all changed by the owner. Each is in scope:
     - `KNOWN_ISSUES.md`: only rows 89 and 90 change; row 88 is byte-identical to the publication head.
     - `CATALOG.md` and `MANIFEST-overrides.tsv`: append-only, 0 removed lines.
     - `fixed_truth_toy.py` (R1) and `n2/harness.py` (R2).
     - `test_n2_harness.py` and `test_producer_provenance.py`: additions only.
   - Paths outside every lane's set are only:
     - the new test;
     - `docs/OPEN_ITEMS.md`;
     - `source-record-inventory.tsv`;
     - `MANIFEST.tsv`;
     - the `Q/integration/` subtree.
   - The guard core, `n2/execution.py`, `omnifold.py` and the 2D driver are byte-identical between `dd73de73` and `2a394cd1`. The pinned `omnifold.py`, the driver and `toy_design.py` are unchanged versus the base as well.
2. **Manifest and lint.**
   - `generate_manifest.py --check --at-sha HEAD`: OK. `--check`: OK, tree=clean. Both give rows=1950 and `unused_overrides=3`, which are the three not-yet-existing registered report paths.
   - `live_doc_indexed.py --unrowed`: 0 unrowed.
   - `control_plane_lint.py`: CONTROL-PLANE PASS.
3. **R1 and R2.**
   - I read both diffs. Each is minimal and within scope. `main()` catches `ProvenanceRefusal` and exits with `REFUSAL_EXIT`. R1's test loops over all three loaded modules.
   - Reverting R1 in a shared clone: the R1 test went **red** (FAILED, failures=3, with a ValueError traceback).
   - Reverting R2: the R2 test went **red** (failures=2: the `..`-elsewhere case admitted with rc 0; the outside case refused with the wrong message).
   - After restoring each, the clone had 0 changes. My edge probes are under F4.
4. **Guard × structure.**
   - `finalize` sweeps imported modules generically. Imports: `analyze_uq.py` imports only `technote_style` and `reported_cells`; `reported_cells` imports numpy and ROOT.
   - The new test copies the real `analyze_uq.py`, `reported_cells.py` and `technote_style.py` from REPO, runs them under `mnv_guarded_run.py --require-provenance`, and asserts:
     - the executed set equals the stated set;
     - `reported_cells` was loaded by `import`, with the real digest;
     - the median equals `per_bin_ratios`.
   - So the positive control is not vacuous. The owner's 6/6 mutation log agrees.
   - §4.2 digests recomputed with `git show 2a394cd1:<path> | shasum -a 256`. All 10 match:
     - `f396cf82…`
     - `f0f29ca1…`
     - `2ddf7c9f…`
     - `95be4ff7…`
     - `65c577a8…`
     - `f35dacc6…`
     - `8bd28807…`
     - `f37d4d99…`
     - `3cc5adc7…`
     - `e96234124a31…`
   - Other cross-lane checks:
     - None of `analyze_uq.py`, `_ours_only_chi2.py` or `final_rollup_full.sh` at base digests is referenced anywhere outside `Q/`.
     - `analyze_universes.py` is pinned only at revision `_REV_901F` in `test_hash_bindings.py` and in a talk JSON, which is revision-scoped, and that suite passes.
     - No committed record pins the guard-head digests of `fixed_truth_toy.py` or `harness.py`.
     - The inventory reports 0 unlisted sites and 0 adjacent shapes.
5. **Tests.** Every count comes from the runner's output; 0 skips in every suite.

   | suite | interpreter | result |
   |---|---|---|
   | producer (`test_producer*.py`) | venv313 + PyROOT | Ran 31, OK, 37 s |
   | harness (`test_n2*.py`) | python3 | Ran 22, OK, 99 s |
   | OI-136 ratchets (both files) | python3 | Ran 17, OK |
   | `test_reported_cells.py` | venv313 + PyROOT | 18 passed |
   | `test_final_rollup_full_refusal.py` | python3 | 3 passed |
   | `test_coverage_fixed_truth.py` | python3 | 20 passed |
   | `test_hash_bindings.py` | python3 | 33 passed |
   | KI-84 (`-W error::ResourceWarning`) | venv313 + PyROOT | Ran 15, OK |

   `verify_hash_bindings.py` printed ALL BINDINGS INTACT. This matches every row of report §4.4.
6. **Registers.**
   - I re-ran `guard/inventory.py`:
     - head `2a394cd1`, dirty_tracked False;
     - ast_sites 17, rooted_listed 17, ast_unlisted [];
     - fail-open 16 with digest `7aa2943198612b5e904d37c2d75f3ac9b0fe33cabeb69bcddd7a7e87fc334aa9`, matching the ratchet's digest;
     - probe candidates 144; ast_only = `gate2_target_runtime.py`; adjacent 0.
   - The listed classes are frozen_record 7, receipt_bound 5, probe 3, twod 1, pet 1. That fits "10 older exceptions = 3 probe + 2D arm + 5 receipt-bound + gate2" and 17 = 10 + 7.
   - The OI-136 change is a pure insertion of 1,672 characters, plus the `updated` date 2026-08-20 → 2026-10-09. It ends "**This row is not solved.**" and lists the remaining exceptions, the unmeasured `.sh`/`MNV_REPO`/gate6 families, the three unguarded launchers and the hook gap.
   - KI-90 stays **OPEN** and names both unpatched consumers and structure §5.
   - KI-89 records the three unchanged launchers and the strict KI-85 set. The cited `AUTHORIZATION-20260903-oi136-failopen-repair.md` exists.
   - Only F2 (tense) is wrong.
7. **Synthesis numbers.**
   - **GBDT.** `results.json` `diagnostic_cost`: subtotal 3.01809 / 6.03618, verification 1.0. (3.018+1)/0.8 = **5.0226** and (6.036+1)/0.8 = **8.7952**, equal to `admitted_core_hours_range`. `python3 -I reduce_saved_outputs.py --out <scratch>/r.json` took 24.4 s on one thread and was **cmp IDENTICAL**, sha256 `483ca827…`. The gbdt REPORT §11/§13 label the branch-B route post-review and INCONCLUSIVE for review, as §3 says. §3 does not admit D-ID.
   - **PET** (`design_cost.json`):
     - rows per data-size experiment 11,600,000, with 9.6 M pseudo-truth FORECAST + 2 M prior ASSUMPTION;
     - multiples 5.664 / 28.32 / 70.80 at 24 / 120 / 300;
     - 101.0 at 428, 127.2 at 539, 225.4 at 955;
     - full procedure per-decision 142,349–150,004 and joint 238,008–245,663 A100-h;
     - E1 look-1 at 2 M: 574.9 A100-h.
     All are quoted correctly.
   - **Speed.** REPORT row 227: 3,182 A100-h, 720 DEV + 1,080 RB; 1,609 at 2× (≈ 1.6 k); 1.4 % of the GPU balance (795.5 node-h of 55,107). Its source is `cost_fb_look1-20260930.json` (`costs.py:30`). P05 is 530/927/1,853 and ≈ 125 with prototype 1. All match.
   - No frozen numerical record is rewritten. Apart from the wording in F5, I found no overclaim.
8. **Publication.**
   - `ls-tree -r` at `2a394cd1:docs/analysis-note/` against standalone `6a7fa2f2…` (= `sync-publication-correction-20261009`, one commit ahead of `ad3fb800`): 120/120 blob-identical. The standalone has 2 extra files (`.gitignore`, `AGENTS.md`). The base pair gives the same result. Mode: see F7.
   - `build_all.sh` at `2a394cd1` (50 s wall) reported:
     - `RESULT :: PASS :: head=2a394cd1… tree=clean`;
     - SELF-TEST PASS (17 perturbations);
     - SEC4-RECEIPTS PASS (14/14);
     - pages 123 / 9 / 11.
   - In the `pdftotext` output:
     - no `??` in any of the three PDFs;
     - "pinned seeds" occurs 0 times in all three;
     - the paper has "unpinned seed" (1);
     - the note has "was None" and "not a demonstration that the quoted uncertainty is wrong";
     - the primer has "have not been re-tested";
     - "seed-ensemble mean" is absent, and the three remaining `0.28` hits are unrelated quantities.
   - The `11c753b7` delta is one clause ("vary the GBDT seed (seeds 1--10)") and it renders.
   - "Not publication-ready" is preserved in `CLAIMS-20261005` (line 146) and in `PACKAGE-MANIFEST-20261006` (lines 8–13). I found no readiness claim.
9. **Registration.**
   - `MANIFEST-overrides.tsv` gains 4 `MACHINE open` rows: integration, two-d-path, sb1-prep and d-id.
   - `CATALOG.md` routes the integration report and the three next reports, each with one owner per subtree. It states "Registration grants no compute, experiment or adoption authority". No authority is granted.
   - The preconditions are faithful except for F3.
10. **Other.**
    - Report §4.3 control and mutant log: `all_controls_pass: true`, caught 6/6, no skips.
    - The owner's build log was taken at `b19b5e91`, but `docs/analysis-note/` is unchanged from there to `2a394cd1`, and my build at `2a394cd1` reproduces it.
    - I found no unreviewed delta silently treated as reviewed. §1 and §3 list each lane's post-review delta and label it "unreviewed".

**Measured vs inferred.** Everything above is measured except two judgements. One is F4's "not an authority bypass", which is reasoning about the downstream digest and HEAD checks; the probe did not attempt a bypass. The other is F2's "would be false if the merge fails", which is conditional by nature.
