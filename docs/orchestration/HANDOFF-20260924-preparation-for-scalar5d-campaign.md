# HANDOFF 2026-09-24 — preparation for the scalar-5D reportable-uncertainty and inference campaign

**CITABLE FOR:** what the 2026-09-24 preservation pass preserved, measured and simplified; the exact
identities of the two preserved drafts; the dependencies the next session inherits.
**NOT CITABLE FOR:** activation of the scientific plan, any scientific result, adoption, or
publication readiness. It repeats no research history: follow the routes.

Authorization: [`AUTHORIZATION-20260924-preservation-and-simplification-pass.md`](AUTHORIZATION-20260924-preservation-and-simplification-pass.md).
Evidence and inventories: [`RECOVERY-MANIFEST-20260924-preparation-epoch.md`](RECOVERY-MANIFEST-20260924-preparation-epoch.md).
Current scalar-5D routes: `CATALOG.md` → `## Current work` → *Scalar-5D — the current entry route*.

## 1. The three status fields

| field | value |
|---|---|
| `preservation_status` | **PARTIAL.** Both repositories are tagged, bundled, checksummed and restore-tested; the adopted scalar-5D bytes and every reporting product have a checksum-verified durable copy (three restore-tested). **Nine external objects (47.7 GiB) remain sole-copy on `/pscratch`**, so full preservation is not certified. |
| `simplification_status` | **ONE FAMILY DONE, ONE RETAINED.** F1 done: the router's scalar-5D sections moved verbatim to a declared continuation, and one compact entry route replaced them (router 4,097 → 1,305 lines). F2 not executed: its precondition failed (§5). No file was removed from `main`. |
| `campaign_preparation_status` | **READY FOR ACTIVATION, WITH INHERITED DEPENDENCIES.** Inputs re-hash to their manifest; the protected-receipt and routing checks are green except the render probe (D9); the scalar test subset passes apart from the two known multiprocessing failures; all three document builds pass. §6 lists what remains, including one open census question (D11), and none of it is publication readiness. |

## 2. Evidence epoch

| | monorepo | standalone note repository |
|---|---|---|
| tag → commit | `evidence/preparation-2026-09-24-bf34a12c` → `bf34a12cff9a2f06f0a3f1c516628085565eef60` | `evidence/preparation-2026-09-24-a11b7055` → `a11b70556cea4e23b4db7881a8033c8dd2632563` |
| bundle sha256 | `31aba79ca6a345f82bb1f9cf55c15871fbc2ea66a9b0bd0eabcca9b77f743d5b` | `36e294ae458929ce078372d3bff44f4acd12be0c69fbe74a26e92a28c21cc5e1` |

Epoch directory, sealed by `SHA256SUMS` (itself `7431f87f…`, resealed 2026-09-25T03:35Z after the review), at
`/Users/josephbailey/local-research/evidence-epochs/preparation-2026-09-24-bf34a12c/` and
`/global/homes/j/josephrb/evidence/repository-epochs/preparation-2026-09-24-bf34a12c/`.
**Recovery tests executed:** fresh GitHub clone; clone from the local bundle with no network; clone
from the NERSC bundle copy on a login node; note repository by clone and by bundle. Each detached at
its tag with the expected commit; each monorepo test also restored both drafts' blobs, and the note
repository's two clones had identical trees. 19 cited commits exist only in the
bundle (4 anchored at `refs/preserved/preparation-20260924/`); nothing local-only was pushed.

## 3. External-artifact coverage

48 of 57 inventoried objects have a durable copy: 46 at
`…/preparation-2026-09-24-bf34a12c/trunk-baseline/` in NERSC global home (all sha256-equal to the
originals) and 2 inputs in HPSS `mnv-quoted-products-20260812` (md5 equal). **Restore-tested:**
`z-cv.npz` `3d7465f6…` and the `(E_avail,W)` projection `835828bf…` from the home copy, and the
`parent` input `4f168e83…` from HPSS tape. **Sole-copy on `/pscratch`, no durable copy:** inputs
`active` (42.3 GB), `throw`, `stat`, `ml`; `z-mean.npz`; the graded pair `361090f9…`/`7e4636a3…` and
their `z-mean.npz`. Recovering the adopted bytes does not need them; **rebuilding the trunk from its
manifest, or recomputing `M1` from the graded bytes, does.** No object was scientifically re-verified.

## 4. The preserved drafts — verify these before recording any approval

| path | Git blob | first committed |
|---|---|---|
| `docs/orchestration/PLAN-scalar5d-reportable-uncertainties-and-inference.md` | `8b0617b6e044a55a9b5870b46e5d90a15a6ced7a` | `bf34a12cff9a2f06f0a3f1c516628085565eef60` |
| `docs/orchestration/DRAFT-preservation-and-stabilization-session-prompts.md` | `cf3c2e858d4526ad356e604af9bc6100e6cc7e9f` | `bf34a12cff9a2f06f0a3f1c516628085565eef60` |

**The plan is NOT ACTIVATED.** Only Joseph's actual sending of the draft's *Complete estimator goal
prompt* activates it; the approval wording inside both documents is draft text. Compare what you
were given with the preserved bytes:

```bash
git hash-object <attached-plan>    # must print 8b0617b6e044a55a9b5870b46e5d90a15a6ced7a
git hash-object <attached-draft>   # must print cf3c2e858d4526ad356e604af9bc6100e6cc7e9f
git rev-parse evidence/preparation-2026-09-24-bf34a12c:docs/orchestration/PLAN-scalar5d-reportable-uncertainties-and-inference.md
```

A mismatch blocks activation of the disputed version only (plan §1); record it before any edit.

## 5. Routes kept, the family moved, and historical lookup

- **Moved (F1):** nine scalar-5D sections of `CATALOG.md`, verbatim, to
  [`CATALOG-ARCHIVE-scalar5d.md`](CATALOG-ARCHIVE-scalar5d.md), declared by a `CATALOG-CONTINUES`
  marker so every pointer row still indexes its document. No link target and no indexed basename was
  lost (291 → 293 and 323 → 324). The withdrawal check's two pinned quotations moved with their text.
- **Kept `LIVE` (F2 not executed):** `HANDOFF-20260921-gbdt-remaining.md`,
  `HANDOFF-20260922-gbdt-cold-start.md` and `REPORT-20260922-review-residue.md`. A read-only sweep
  of every item they list found five open items tracked nowhere else (§6, D10 and D11). Archiving them would
  have hidden those items, so they stay until each has a tracker.
- **Not removed:** every removal candidate had a code, test or probe consumer (manifest §3).
- **Lookup:** `git show evidence/preparation-2026-09-24-bf34a12c:<path>`, and
  `git grep '<identifier>' evidence/preparation-2026-09-24-bf34a12c --`.

Documentation counts, tracked tree: before (at the tag) **2,399 files / 555 Markdown / 143,468
Markdown lines**; after (with this file) **2,404 files / 559 Markdown / 143,862 Markdown lines**. The router shrank; the total barely moved,
because nothing was deleted.

## 6. Readiness and dependencies

**Measured ready:**

| area | evidence |
|---|---|
| inputs | all 8 trunk-manifest inputs, `z-cv.npz`, both projections and the graded pair re-hash to their recorded digests (manifest §2) |
| import paths | `nd-unfolding/mnv_guarded_run.py` present. Scalar test subset (`test_z_*`, projection, boundary, baseline-overwrite, OI-136 containment, guarded-run): **1323 passed, 13 skipped, 2 failed**. The 2 are the multiprocessing tests handoff-0921 §4c already lists; here they fail on `AF_UNIX path too long` from the long TMPDIR |
| protected receipts | `verify_hash_bindings.py`, `live_doc_indexed.py`, `generate_manifest.py --check`, `control_plane_lint.py`, withdrawal completeness all exit 0. P4 token `20260924T010110Z-known-issues-51-61-62-verdict.json` → `TOKEN-OK` at the preparation head (code_rev `036f507e`, 23 paths) |
| builds | `build_all.sh` PASS at `8cffde7b` (note 106 pp, primer 7, paper 4; containment strict PASS). The standalone note repository's 97 shared files are byte-identical to `docs/analysis-note/` |
| cluster | `generate_live_state.py --check-freshness` FRESH on the deployed checkout (`32e403b8`) at 2026-09-25T03:10Z; `squeue --me` shows only PET `pv1-*` jobs (34), none running from the deployed checkout |

**Unmet requirements.** *Class*: B = baseline recovery, C = campaign inputs/runtime, D = deliverable.

| # | class | unmet requirement | evidence | owner | blocked action | next closure check | independent work that can proceed |
|---|---|---|---|---|---|---|---|
| D1 | C | **The plan is not activated** | §4; authorization §3 | Joseph | every plan phase after the cold start | Joseph's actual message, recorded with blob `8b0617b6…` and commit | read-only reading of plan §1 routes |
| D2 | C | **`R5` stops the seven-cause discharge campaign on 2026-09-30 (UTC) or at 500 GPU / 500 CPU task-hours**; *"continuing past the stop requires a fresh decision"*. The plan's supersession list does not name `R5` | `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` `R5`; re-bound for the scalar path as *"Unchanged and binding"*, with per-submission admission via `nd-unfolding/r5_meter.py`, by `AUTHORIZATION-20260918-d-resource-required-deliverable-path.md` §1; plan §2 | Joseph, via the activation's scoped supersession mapping | any compute the mapping cannot place outside `R5` and the D-RESOURCE clause | the mapping plan §2 requires, naming `R5`, the D-RESOURCE clause and `r5_meter.py` admission explicitly | costing, contract drafting |
| D3 | B | four rebuild inputs, `z-mean.npz` and the graded pair have no durable copy (47.7 GiB) | manifest §2 *The gaps* | Joseph / storage (an `OI-131`-type storage decision) | a trunk rebuild or `M1` recomputation after any loss on `/pscratch` | `sha256sum` against the manifest digests; `hsi ls` of a new archive | everything that reads the preserved adopted bytes |
| D4 | C | the ten adopted endpoint receipts are `SUPERSEDED-BY-CODE-DRIFT`; re-producing the endpoints is reserved, and re-unfolding would invalidate `3d7465f6…` | `OUTCOME-20260922-ten-adopted-receipts-superseded-by-code-drift.md` | Joseph | any baseline `run_p4_unfold_std.sh` run (the `e2632ac7` guard refuses it) | a recorded ruling | fresh member-scoped builds in a new namespace |
| D5 | C | the L2 pair fails `footing_ok` (different code revisions); the same-commit rebuild was declined, and two predeclared invalidating conditions are undischarged | `OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md`; `REPORT-20260922-review-residue.md` §3 | the next campaign, once activated (plan §2 would authorize fresh paired rebuilds) | citing the released-lateral `s_proj` against the bound | a paired rebuild at one revision | none needed from this pass |
| D6 | C | the deployed cluster checkout is at `32e403b8`, behind `origin/main`, with two regenerated tracked files modified and many untracked files. It is shared. None of the 34 queued or running jobs uses it as its working directory: all are PET `pv1-*` jobs under `/pscratch/sd/j/josephrb/pet-improvement-20260922/checkouts/{d01a04a9,6b18e09d}` (`scontrol` `WorkDir`, 2026-09-25T03:20Z) | `nersc-worktrees.txt`, `nersc-jobs.txt` in the epoch | shared; the PET lane owns those jobs | moving or redeploying that checkout without re-checking | `git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold rev-parse HEAD`; `squeue --me` plus each job's `WorkDir` | use a detached worktree (handoff-0922 §7) |
| D7 | D | shipping the Appendix F package, the hadronic-response question, and adoption of the 3D projection or any figure built from it are reserved | `docs/analysis-note/release-package-20260922/README.md`; `QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md`; `OUTCOME-20260922-3d-covariance-projected-from-the-adopted-trunk.md` | Joseph | those outward or adoption acts | a recorded ruling | the 3D `declared-dst-cv` variant and 3D cutoff scan (REPORT-20260922 §3) |
| D8 | C | the shared main checkout cannot `git pull` until its two untracked draft copies (identical to the blobs above) are removed | manifest §1 | whoever next updates that checkout | pulling in `/Users/josephbailey/local-research/MINERvA-OmniFold` | `git hash-object` equals the blob, then remove and pull | all work in other worktrees |
| D9 | D | **F1 did not meet its frozen gate** *"the render/table probes stay green"*: `probe-20260922-render-checks.py` exits 1 with 61 inline-marker leaks in `CATALOG-ARCHIVE-scalar5d.md`. Accepted because they are pre-existing — the same 61 texts parse as leaks in the full pre-move router, the new router has 0 — and the probe scopes by lines added since `177af61b`, which every line of a new file is. Consequence: `probes/probe-20260922-seven-gates.sh` (which runs this probe and prints *DO NOT COMMIT*) is red on every run on `main` | F1 commit message; review finding 4 | router maintainer; the frozen probe's owner (loop ended at `c496135f`) | trusting a bare red from `seven-gates.sh` | `probe-20260922-render-checks.py --since 8cffde7b` exits 0 (measured); or reformat the 61 markers in a render-only commit | all |
| D10 | C | four of those five open items, tracked only in the two dated handoffs or in code: the scrontab supervision net (handoff-0921 §4f; cluster state not measured), the 12 unexplained launchers (§4e; a test comment only), the two multiprocessing tests (§4c), the `27.395%` vs `37.885%` PET empty-cloud discrepancy (handoff-0922 §9.4, PET-adjacent) (the boundary census, handoff-0922 §6, is D11) | the cited sections | unassigned; route to `KNOWN_ISSUES.md` with the KNOWN_ISSUES peer session | archiving those handoffs | each item has a tracker row | all |
| D11 | C | **The boundary census is not re-measured.** `boundary_readership.py` prints `read_by_production: no` for all seven, but its own docstring rests on *`assess` having no caller outside `tests/`*, which is false: `z_grade.py:616` and `z_build.py:762` call `z_validator.assess`, which reads `boundary(lg.boundary_key).value` (`z_validator.py:311-320`) for `cause3_agg`, `cause3_med` and `cause3_corr`. So the instrument cannot see those runtime reads, and the `no` in `OPERATIVE-SHEET-scalar5d.md` §1 and in `AGENTS.md`'s adopted-trunk row is unconfirmed for them | handoff-0922 §6; review finding 1 | the OPERATIVE-SHEET owner; the next campaign before it quotes the census | describing any cause-3 criterion as never computed in production, or as *applied* | a readership measure that follows `assess()`'s dynamic `boundary_key` reads, plus whether `z_grade` ran on the adopted digest | all |

## 7. Review, heads and the next action

Independent review: **one review, one repair cycle.** A read-only reviewer worked in a detached
worktree at `0c985da1` (its `git status --porcelain` was empty afterward) and reported 1 HIGH, 3 MEDIUM
and 7 LOW findings. All were accepted and repaired in the commit that follows `0c985da1`: the HIGH
(the boundary census had been reported as re-measured by an instrument that cannot see `assess()`'s
reads) is now D11; the MEDIUMs are the scalar-5D *next action* route, D2's D-RESOURCE clause, and
F1's unmet render-probe gate (D9, manifest §3 execution record); the LOWs corrected a bundle byte
count, the baseline-copy record, checksum coverage wording, section and consumer counts, and route
details. The reviewer independently re-ran a bundle recovery, re-hashed six originals, re-verified all
46 baseline copies and confirmed the F1 move verbatim, with no finding on draft preservation,
scientific claims, ledgers or hash-bound files. No second repair cycle was used.

Heads observed while writing (UTC): monorepo `origin/main` = `bf34a12c` at 2026-09-25T02:36Z,
before this pass's later commits; note `origin/main` = `a11b7055` at 02:37Z. The final report gives
the pushed heads that contain this file.

**Next action:** Joseph gives the scientific session this handoff and the two drafts. That session
checks the blobs (§4). If Joseph sends the estimator prompt, it records that activation with blob
`8b0617b6…` and commit `bf34a12c…`, writes the scoped supersession mapping (naming `R5`, D2), and
starts plan §1's cold start and §3's budget receipt. It should not repeat this archive or restart a
cleanup campaign.
