# 2D closeout Stage A: receiving and integrating the selective-I/O delivery

**CITABLE FOR:**
- the receipt of `impl/selective-io-20261010` at `9dfd8d6eae5a1f4a52b32f5032348744cb012c47`: its commits,
  receipts and reviews, as verified here;
- the integration checks re-run on the merged tree, the hash-binding delta and its power test;
- the routing of the four frozen packages that pin the old 2D driver (SB1, XR, XR Linux, speed) to their own
  commits.

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- a cluster, ROOT 6.28, real-file or trained-output run of `--branch-select derived` (none was made);
- a speedup of the in-driver port;
- adoption of the opt-in path for any production, or authority to change a launcher.

| field | content |
|---|---|
| `Owner` | 2D closeout executor (2d closer), directed by the paper-tighten lane under [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) |
| `Deliverable` | A-1 of the director's 2026-10-12 assignment: receive the selective-I/O delivery and integrate it by its REPORT's §10, in the manner of PR #91 (`7419fb37`) |
| `Branch` / `Base` | `closeout/stage-a-selective-io-20261012` / `origin/main` `46c410ae` (PR #94). The reviewed merge was `798f8340` on `7edb65fa` (PR #93); it was rebuilt on `46c410ae` with the review repairs (§8). PR #94 touched only Stage A records and catalog/manifest rows, so no check below depends on the base move |
| `Delivery` | `origin/impl/selective-io-20261010` = `9dfd8d6e`, merge base `3892e769`; its record is [`Q/selective-io/REPORT.md`](../../../next-preparation-20261009/selective-io/REPORT.md) (terminal PASS) |
| `Compute` | Local only (macOS, Python 3.13.7 + ROOT 6.36.00, numpy 2.4.4; Python 3.12 for the gates; a scratch venv with LightGBM 4.6.0 and scikit-learn 1.8.0 for the frozen XR suites). **No cluster contact, no Slurm job, 0 node-h** |
| `Reviewer` | §8 |

`Q` = `docs/orchestration/state/next-preparation-20261009`. `R` = this directory. The delivery's
package (`Q/selective-io/`) is merged unchanged; nothing under it was edited.

## 1. Answer

**Integrated, with one routing addition the delivery could not foresee.**
- The delivery's four commits, receipts and reviews check out (§2). The merge into `7edb65fa` is clean, and
  the driver it brings is the reviewed one: `6be77c51…`, unchanged since `a35b1a3f`.
- Every driver-adjacent suite the delivery ran passes on the merged tree with the delivery's own counts (§3).
- **Hash bindings: no delta.** The full resolved-binding status table is identical before and after the merge
  (172 rows; 167 OK, 5 known pre-existing). A planted stale driver pin is caught (MISMATCH, rc 1). No
  `verify_hash_bindings.py` constant moves (§4).
- **Frozen packages.** SB1 and XR (two-d-followup) pass at their own commits through the delivery's routing
  script. Two more packages pin the old driver and fail closed at the merged `HEAD`, by design:
  - **XR Linux**, integrated by PR #91 after the delivery was written (manifest OUT OF DATE; 16 failures and
    2 errors of 57). It passes at its own commit `4bde0670` (manifest current; 57 OK). A routing script is
    added at [`R/checks/frozen_xr_linux_check.sh`](checks/frozen_xr_linux_check.sh).
  - **speed** (`Q/speed`, `318d3e45`), which the delivery's caller population also missed (review MINOR-1):
    its `bench/pinned.py` refuses the new driver blob at import. It passes at its commit (11 OK).
  - The 2D reference's frozen-package sentence now names all four (§5).
- `MANIFEST.tsv` is regenerated from the staged index (§6). The CATALOG gains the delivery's outcome row.

## 2. Receipt: commits, receipts and reviews

| commit | author identity | content | checked |
|---|---|---|---|
| `a35b1a3f` | `selective-io-20261010` | driver, new test file, reference subsection | the only commit that touches the driver: `git diff a35b1a3f 9dfd8d6e -- 2d-unfolding/unfold_2d_omnifold_unbinned.py` is empty |
| `6486867f` | same | the record, checks, logs, proposals | the logs it cites are present; the counts in REPORT §7.1 equal the log lines |
| `446e2857` | same | repair batch 1 (F1–F6): tests, reference wording, routing script, mutation rerun, the first review verbatim | "driver unchanged" holds (empty driver diff, as above) |
| `9dfd8d6e` | same | delivery: the re-review verbatim, §13 terminal | wording only, as the REPORT says |

- **Driver digest at the delivered head:** `6be77c51805547bac2d864ce77c7bc636607cf43194bd2f4ad1a7c14db621257`,
  the value the REPORT and its frozen-refusal logs name.
- **Reviews:** `Q/selective-io/review/review-6486867f.md` (PASS WITH CHANGES; 0 MATERIAL, 3 MINOR, 4 NOTE) and
  `review/rereview-446e2857.md` (PASS). Same-model reviewer, as the REPORT discloses.
- **Receipts:** the REPORT's evidence is its logs and scripts under `Q/selective-io/logs` and `checks`. The
  rerun of §3 reproduces them on the merged tree.

## 3. Checks re-run on the merged tree

Runner: the delivery's `checks/run_suites.sh`, run from a scratch copy whose only change is its `TMPDIR`
line (the original names another session's scratch directory). Log: [`R/logs/suites-merged.txt`](logs/suites-merged.txt).
Tree: the merge before it was committed (the log header reads `head 7edb65fa … dirty-files 46`), driver
`6be77c51…`. The reviewer re-ran every row on the committed `798f8340` with identical results.

| check | result | delivery's count (REPORT §7.1) |
|---|---|---|
| `2d-unfolding/tests/test_selective_io.py` | 27 OK | 27 |
| `test_bootstrap_completeness_ki84.py` | 15 OK | 15 |
| `test_reported_cells.py` | 18 OK, 5 skipped (no matplotlib) | same |
| `test_final_rollup_full_refusal.py` | 3 OK | 3 |
| N2 `test_producer_provenance` / `test_n2_harness` / `test_producer_final_dependencies` | 26 / 22 OK / 5 skipped | same |
| `test_oi136_rooted_insert_ratchet` / `test_oi136_failopen_inventory_ratchet` | 10 / 7 OK | same |
| `test_flux_universe_fix` | 51 OK | 51 |
| `nd-unfolding/tests/test_hash_bindings.py` (3.12, pytest) | 33 passed | 33 |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT; receipt inventory 149 / `6a3787ea…` | (148 at the delivery's base; 149 since PR #91) |
| `verify_receipt_artifacts.py` | 0 missing; UNRESOLVED 66, pinned `49916d28…` unchanged | same |

## 4. Hash-binding delta: enumerated and power-tested

- **Enumeration.** [`R/checks/binding_table.py`](checks/binding_table.py) replays `verify_hash_bindings.py`'s own
  collection and dedupe (it calls the verifier's functions from the tree under test) and prints one row per
  resolved binding: path, pinned digest, source and status.
  - At `7edb65fa`: [`R/logs/bindings-at-7edb65fa.tsv`](logs/bindings-at-7edb65fa.tsv), 172 rows.
  - On the merged tree: [`R/logs/bindings-merged.tsv`](logs/bindings-merged.tsv), 172 rows.
  - `diff`: **empty**. The delta is zero bindings added, removed or changed in status.
- **Why the driver moves without a delta.** The only resolved bindings that name the driver are the two
  KNOWN pre-existing drifts (`negweight-hpss-durability-20260821.json` and `run_gate2_target_validator.sh`,
  both pinning `8ebe0277…`). `KNOWN_PREEXISTING` is keyed by the *pinned* digest, so it is unaffected by the
  live driver's bytes. The frozen SB1/XR/XR-Linux receipts and manifests name `3cc5adc7…` in forms the
  verifier does not resolve as bindings: `identity.executed[]` entries whose `path` is a run worktree on
  `/pscratch` that `localize()` does not strip, `{relpath: digest}` maps in `expected-code.json` and admission
  `modules`, and `driver`/`driver_digest` fields in `runs.json` (review NOTE-1; as
  `Q/xr-sb1-integration/REPORT.md` §8 condition 3 describes).
- **Power test.** In a scratch detached worktree at `7edb65fa`, the merged driver was copied in and one receipt
  `{"path": "2d-unfolding/unfold_2d_omnifold_unbinned.py", "sha256": "3cc5adc7…"}` was planted. The verifier
  printed `MISMATCH 2d-unfolding/unfold_2d_omnifold_unbinned.py want 3cc5adc7… got 6be77c51…` and
  `*** BINDINGS BROKEN ***`, rc 1 ([`R/logs/powertest-stale-driver-pin.txt`](logs/powertest-stale-driver-pin.txt)).
  The rc 1 has two causes: the planted receipt also changes the receipt inventory (149 → 150). The
  discriminating evidence is the `MISMATCH` line (review NOTE-2).
- **Instrument limit.** `binding_table.py` replays the verifier's `main()` loop (`verify_hash_bindings.py:899-924`)
  rather than importing it, so it could drift from a later verifier. At this tree it agrees with the
  verifier's own totals (172 resolved, 167 OK, 5 known).
  The worktree was restored (0 changed paths) and removed. So a resolved driver binding, had one existed,
  would have been caught.
- **Constants.** None moved. `RECEIPT_BINDING_COUNT`/`_SHA256` stay at 149 / `6a3787ea…`.

## 5. Frozen-package routing

Each package's bytes at the merged `HEAD` equal its frozen commit (`git diff --quiet <commit> HEAD -- <pkg>`).

| package | frozen at | at the merged `HEAD` | at its own commit | log |
|---|---|---|---|---|
| SB1 prep `Q/sb1-prep` | `d4335d3b` | refuses the new driver (delivery REPORT §7.2) | consistency / branch select / guarded / launch chain all OK, rc 0 | [`R/logs/frozen-sb1.txt`](logs/frozen-sb1.txt) |
| XR `Q/two-d-followup/xr` | `07428e5d` | manifest OUT OF DATE (delivery REPORT §7.2) | manifest current; 42 OK; rc 0 | [`R/logs/frozen-xr.txt`](logs/frozen-xr.txt) |
| **XR Linux** `Q/xr-linux/xr` | `4bde0670` (delivered head; the authorization's admission commit is `60bd68c0`, and `b17ca932` later changed `xr/tests/mutation.py`; the manifest is `5d2f5955…` at both) | `xr_admit.py manifest --check` rc 3 "OUT OF DATE"; `test_xr.py` 16 failures, 2 errors of 57 | manifest current; 57 OK | [`R/logs/xr-linux-at-merged-head.txt`](logs/xr-linux-at-merged-head.txt) (its header reads `37985acc`: it ran on the uncommitted first merge with the new driver; the reviewer reproduced it on `798f8340`), [`R/logs/xr-linux-at-4bde0670.txt`](logs/xr-linux-at-4bde0670.txt) |
| **speed** `Q/speed` | `318d3e45` | `bench/test_prototypes.py`: `RuntimeError … blob bf2d7b58… != pinned e19aeb6d…` at import | 11 OK, on synthetic trees of 20,000 rows (extra 0 and 192), smaller than the package's recorded 0.2–1 M rows | [`R/logs/frozen-speed.txt`](logs/frozen-speed.txt) |

- **The XR Linux addition.** The delivery predates PR #91, so its `frozen_package_checks.sh` knows only `sb1`
  and `xr`. The XR Linux REPORT (`Q/xr-linux/REPORT.md:90–92`) predicted this at-`HEAD` OUT OF DATE.
  `R/checks/frozen_xr_linux_check.sh [PYTHON]` applies the same routing to it:
  - it confirms the commit exists and that the package bytes at `HEAD` equal those at `4bde0670`;
  - it runs `manifest --check` and `test_xr.py` in a throwaway detached worktree there, then removes it.
  - **Pass branch:** rc 0 from this branch ([`R/logs/frozen-routing-xr-linux.txt`](logs/frozen-routing-xr-linux.txt)).
  - **Refusal branch:** rc 2 from a worktree at `ad786c68~1`, where the package does not exist
    ([`R/logs/frozen-routing-xr-linux-refusal.txt`](logs/frozen-routing-xr-linux-refusal.txt)). No worktree was left behind.
- **Routing to use after this merge.** Run the four packages' checks at their commits:
  `Q/selective-io/checks/frozen_package_checks.sh sb1|xr [PYTHON]`, `R/checks/frozen_xr_linux_check.sh [PYTHON]`,
  and, for speed, `SPEED_TREES=<dir> python3.13 -I bench/test_prototypes.py` from a detached worktree at
  `318d3e45` with trees from its `bench/make_synthetic_trees.py`. `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` now
  names all four.
  Keep the at-`HEAD` byte checks. No package, manifest or test is edited or repinned.

## 6. Catalog and manifest

- `CATALOG.md`: the delivery's proposed outcome line (REPORT §10 item 3), plus a pointer to this record.
- `MANIFEST-overrides.tsv`: `Q/selective-io/REPORT.md` already had its `MACHINE open` row. This record gets one.
- `MANIFEST.tsv`: regenerated from the staged index; `generate_manifest.py --check` OK at the commit.
- `docs/CURRENT_WORK.md` is generated and is not hand-edited.

## 7. What the merge changes for the 2D closeout

- **`main`'s driver digest moves** from `3cc5adc7…` (the bytes L0, L1 and every XR run executed) to
  `6be77c51…`. The default `--branch-select all` makes the same loader calls; its OmniFold inputs and outputs
  equal the old driver's in four modes through a stub helper (delivery REPORT §6). Trained outputs on the real
  file were not compared.
- **Stage C consequence (plan §4 Stage A).** "If the final producer differs from XR's producer, a small
  equivalence check must bridge them before a large ensemble starts." A Stage C package built on the new
  driver must name `6be77c51…` (or its successor) and must first show a default-path regeneration of L0's
  product within the frozen 1e-8 criterion. With `--branch-select derived`, it must also compare the
  `branchSelection` record with SB1's selections and its outputs with a matched default run (delivery REPORT
  §11). This record does not make that check.
- **N2.** `uq/coverage_fixed_truth/fixed_truth_toy.py` imports the driver directly, so any future N2 launch
  executes and records `6be77c51…` (or its successor), not `3cc5adc7…` (delivery REPORT §8; review NOTE-6).
- **Carried to the Stage C producer change:** the driver comment at `unfold_2d_omnifold_unbinned.py:26` cites
  Phys. Rev. D 106, 032001; the published 2D result is Phys. Rev. D 104, 092007. It is fixed with the next
  behavioural driver change, so the digest moves once (director's ruling, 2026-10-12).
- **Not applied (owners' items, delivery REPORT §10 item 4):** six live files cite driver line numbers
  without a commit. Lines after the import block move by +3 to +343. They are listed in the delivery REPORT
  and left to their owners.

## 8. Independent review

**Setup.** One fresh read-only reviewer, a general-purpose Claude Opus 5.5 session, in its own detached worktree
at `798f8340` (empty `git status` at start and end; removed). Local only. Budget: one review plus at most two
focused re-reviews (plan §5). **Same-model caveat:** owner and reviewer are Claude Opus 5.5 sessions; that is
not cross-provider independence (plan §5).

**Review of `798f8340`: PASS WITH CHANGES** (0 MATERIAL, 2 MINOR, 7 NOTE), preserved verbatim at
[`R/review/review-798f8340.md`](review/review-798f8340.md). It independently enumerated the bindings on both
parents and the merge (identical tables), re-ran every suite on the committed merge with the same counts,
exercised all exit codes of the new routing script, and classified all 86 `git grep 3cc5adc7` hits (no live
consumer pins the old digest).

**Repair batch 1 (cycle 1 of at most 2), applied when the merge was rebuilt on `46c410ae`:**

| finding | disposition |
|---|---|
| MINOR-1: the speed package pins the old driver blob and is unrouted | §1, §5 and CITABLE FOR now name four packages; speed run at `318d3e45` (11 OK) and at the merge (refuses), log added |
| MINOR-2: the 2D reference names only SB1 and XR | `2D_OMNIFOLD_REFERENCE.md` gains a paragraph naming XR Linux and speed and pointing here |
| NOTE-1: §4 misdescribed the unresolved pin forms | rewritten to the three actual forms |
| NOTE-2: power test's rc has two causes; `binding_table.py` re-implements the loop | both stated in §4 |
| NOTE-3: two logs labelled "merged" show other heads | §3 and §5 say what the headers say |
| NOTE-4: XR Linux admission vs delivered commit | noted in §5 |
| NOTE-5: routing script | no change required |
| NOTE-6: N2 consequence omitted | added to §7 |
| NOTE-7: undated driver-line citations | left to their owners, as before |

The rebuilt merge is wording, one new log and the reference paragraph on top of the reviewed content; it was
**not re-reviewed**. The reviewed commit `798f8340` stays reachable on `origin` as
`closeout/stage-a-selective-io-20261012-reviewed`.

## 9. Limits

- No ROOT 6.28, cluster, real-file or trained-output run of the opt-in path was made here or by the delivery.
- The suites ran on macOS with ROOT 6.36 and Python 3.13, not the cluster's `root_6_28`.
- The frozen XR suites ran with numpy 2.4.4, against the XR records' 2.4.6, as the delivery's did.
