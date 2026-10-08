# MINERvA OmniFold — unbinned inclusive cross sections (2D → 5D, plus full-event studies)

Unbinned **OmniFold** measurements of MINERvA medium-energy forward-horn-current
(ME-FHC) inclusive charged-current $\nu_\mu$ cross sections.

The anchor is a reproduction of the published binned double-differential result
`d²σ / (dp_T dp_∥)` (Ruterbories *et al.*, Phys. Rev. D **104**, 092007,
arXiv:2106.16210); from there the analysis adds dimensions the binned method
cannot reach — `E_avail`, then `q3` and `W` — and separately studies low-level
event representations. See [Workstreams](#workstreams).

This repository contains the analysis scripts, the documentation and evidence
records that govern them, and the selected edits made to upstream code packages
(the MINERvA 101 tutorial framework and the RooUnfold-based
`unbinned_unfolding` package). Full upstream working trees and generated
outputs are **not** tracked; only overlay files are, so the analysis can be
rebuilt. See [Setup](#setup).

---

## Where to start

| If you want to | Read |
|---|---|
| Orient on the science, and be routed to the governing evidence | `AGENTS.md` — the front door, and the one file to read first |
| Quote a number | `VALIDATION_LEDGER.md`, then the product summary or receipt it cites |
| Know what is being worked on now | `docs/CURRENT_WORK.md`, then the exact row in `docs/OPEN_ITEMS.md` |
| Change code | `KNOWN_ISSUES.md`, the workstream's `*_STATUS.md`, and its callers/tests |
| Run a workstream | that workstream's `*_STATUS.md` / `*_REFERENCE.md` (below) |
| Find the record that governs a plan, decision, outcome or receipt | `docs/orchestration/CATALOG.md` (`## Current work`, `## Task routes`) |
| See what reads what across workstreams | [How the workstreams connect](#how-the-workstreams-connect) |
| Avoid repeating a closed study | [Closed approaches](#closed-approaches) |
| Tell a current instruction from a historical record | [Current versus historical documents](#current-versus-historical-documents) |
| Build the note, primer or paper | `docs/analysis-note/` and [Deliverables](#deliverables) |
| Check the article and its release package | `docs/publication/submission/PACKAGE-MANIFEST-20261006.md`; code in `publication/` |
| Reproduce the joint-5D generator inference | `reproduction/s5p/README.md` |
| Find a local checkout, a disk-use record, or a file removed from this machine | `docs/LOCAL_CHECKOUTS_AND_STORAGE.md` |
| Work here as an AI assistant | `CLAUDE.md` (bootstrap) → `AGENTS.md` (routes) |

**This README deliberately quotes no scientific result.** Central values,
uncertainties, closure numbers and their states live in `VALIDATION_LEDGER.md`
and in each workstream's `*_STATUS.md`, which are the artifacts that gates,
receipts and review actually cover. Nothing automated checks this file (see
[Maintenance](#maintenance)), so a number placed here would rot silently. Treat
it as orientation and a map, never as evidence.

---

## Workstreams

Each workstream keeps its own STATUS + RUN_LOG docs. The states below are
summaries of `AGENTS.md`; re-read the routed artifact before relying on one.

| Workstream | Directory | Status doc | Scope |
|---|---|---|---|
| **2D** `(p_T, p_∥)` | `2d-unfolding/` | `2D_OMNIFOLD_STUDY_STATUS.md`, `2D_OMNIFOLD_REFERENCE.md` | The production measurement and the reproduction of arXiv:2106.16210: central value, standalone uncertainty construction, closure and iteration controls. |
| **3D** `+ E_avail` | `3d-unfolding/` | `3D_OMNIFOLD_STATUS.md`, `README.md` | Adds available energy as a third axis, `d³σ / (dp_T dp_∥ dE_avail)`. Marginal normalization recovers 2D; there is no published 3D reference to compare against. |
| **Scalar 4D/5D** `+ q3, W` | `nd-unfolding/` (launcher router: `nd-unfolding/MANIFEST.md`) | `ND_OMNIFOLD_STATUS.md` | Extends the scalar feature set through `q3` and `W`. Central values and closures are complete. One scalar-5D covariance is adopted **under exception**, and measurements travel with it that are not caveats. The other covariance candidates are quarantined. Read the `AGENTS.md` row and the ledger, not a summary. |
| **Joint-5D generator inference** (s5p, `OI-193`) | `nd-unfolding/s5p_*.py`; generator predictions `3d-unfolding/genie/gen5d_*.py` | `docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md` | Tests five generator predictions against the 5D data, as hypothesis tests rather than as a measured cross section. The campaign is terminal. `reproduction/s5p/` replays it; `nd-unfolding/s5p_recompute.py` is the independent check. |
| **Full-event: PET / FPS** | `nd-unfolding/pet/` (start at its `README.md`), `nd-unfolding/uq_fps/` | `PET_UQ_REMEDIATION_STATUS.md` (the legacy DAG), `nd-unfolding/pet/README.md` (where each campaign ends) | Point-cloud (PET) and full-phase-space studies of low-level event representations. **Diagnostic and method-development work, not a publication uncertainty product** (ruled 2026-08-20). No full-event total covariance is adopted. |
| **Article and release** | `docs/analysis-note/main_paper.tex`, `publication/`, `docs/publication/` | `docs/publication/submission/PACKAGE-MANIFEST-20261006.md` | The PRD-class article, its release candidates, the replay and figure code, and the W1/W2 checks. Submission, deposit and tagging are Joseph's acts. |

The 1D binned $p_T^\mu$ study is a closed equivalence/debug cross-check, not a
publication result. Its workspace was retired from `main` on 2026-08-20 and is
recoverable in full from the pushed evidence tag:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/binned_study/README.md
```

---

## How the workstreams connect

The directories are not independent pipelines. A change to one of the hubs below reaches every
consumer listed with it, so read the consumer's tests before editing a hub. This was measured with
`git grep` over imports and `sys.path` insertions on 2026-10-07; re-run the grep rather than trusting
the list.

| Shared code | What it provides | Main consumers |
|---|---|---|
| `2d-unfolding/unfold_2d_omnifold_unbinned.py` | The OmniFold driver and helpers that the other drivers import (as `u2d`) | the 3D and N-D drivers, about 35 `nd-unfolding` scripts (including `s5c_*`, `s5p_input_dumps`, `project_cov_nd`), PET scripts, `2d-unfolding/uq/`, one `docs/analysis-note` figure script (`redraw_central_only.py`) |
| `2d-unfolding/compare_to_paper_fullcov.py` | Comparison to the published 2D result | 2D diagnostics and receipts, the 3D anchor check, `publication/release/figs/` |
| `3d-unfolding/xsec_3d.py`, `unfold_3d_omnifold_unbinned.py` | 3D extraction and projections | `3d-unfolding/genie/` (generator predictions) |
| `nd-unfolding/unfold_nd_omnifold_unbinned.py`, `xsec_nd.py` | N-D unfolding and cross-section extraction | `nd-unfolding` scripts, `pet/`, tests, `publication/release/figs/export_fig_arrays.py`, the analysis note |
| `nd-unfolding/s5p_joint.py`, `s5p_inference.py` (frozen at `4f5a613f`) | The joint-5D test statistic and inference | `publication/release/` (replay, extraction), `publication/w2/w2b.py`, `docs/publication/w1/repro/`, the s5p recovery records |
| `nd-unfolding/p4_lib.py`, `uq_math.py` | The pinned production configuration and covariance algebra | `p4_*`, `z_*`, `project_cov_nd`, `s5c_assemble`, `uq_fps`, tests, `docs/orchestration` checks |
| `nd-unfolding/omnifold_nn_core.py` | The scalar NN-vs-GBDT cross-check | `sweep_bank*`, `unified_throw*`, `s5c_unfold`, `s5e_trace`, `z_*_probe` |
| `omnifold_nn/` | The vendored `omnifold` package, used as the PET engine | `nd-unfolding/pet/` (see its `README.md`) |
| `unbinned_unfolding/python/omnifold.py` | The RooUnfold-fork reweighting loop | the 2D, 3D and N-D drivers, loaded from a hardcoded `/pscratch/...` path (the `OI-136` pattern; route new compute through `mnv_guarded_run.py`) |
| `technote_style.py`, `lib/` | Plot style; shell resume and backfill guards | about 50 plotters in 2D, 3D and N-D; the `2d-unfolding/sbatch_*.sh` launchers |

**Before changing the 2D driver.** One recorded ruling governs this file. Joseph ruled on 2026-08-23 to
leave its rooted `sys.path` insert (the `OI-136` hazard) unrepaired; the record is
`docs/orchestration/AUTHORIZATION-20260903-oi136-failopen-repair.md:41`. The ruling rests on two conditions:
- the insert stays inside `main()`;
- `unbinned_unfolding/python/omnifold.py` keeps its digest.

`nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` fails if either condition breaks, and the test says
the decision then goes back to Joseph.

The driver's sha256 pins (`docs/orchestration/verify_hash_bindings.py`, the Gate-2 launcher,
`docs/orchestration/state/s5p/gen5d/gen5d-build.json`) record the bytes that earlier runs executed. They are not an approval rule.
- The file was last edited by the `KNOWN_ISSUES.md` 84 fix (`bb4b0b6f`, 2026-10-05). `verify_hash_bindings.py`
  lists the receipt and launcher pins in `KNOWN_PREEXISTING` and edits neither. `gen5d-build.json` is a run
  record that this verifier does not check.
- After that edit the Gate-2 launcher refuses to run until it is re-pinned, and re-pinning it is that gate
  owner's decision (the comment above the driver's rows).

Otherwise follow the `AGENTS.md` "Change code" route.

Products flow in one direction, and each arrow is a recorded anchor or a pinned input:

```
2D central ──anchor──▶ 3D marginal ──anchor──▶ 4D ──anchor──▶ 5D central
5D trunk covariance 3d7465f6… ──projection──▶ (E_avail, W) 835828bf… (VL143); any quotable 3D/4D covariance must be projected from the trunk (AGENTS.md)
5D omnifiles + 3d-unfolding/genie/gen5d_* predictions ──▶ s5p joint inference ──▶ publication/release ──▶ article
tracked figures + values*.tex ──▶ docs/analysis-note/build_all.sh ──▶ note, primer, paper
```

`docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md` holds the older, more detailed invalidation rules. It
predates the PET demotion and the s5 campaigns, so check a rule there against the current records
before acting on it.

---

## Closed approaches

These studies reached a terminal verdict. Each verdict is quoted from its own record, which is the
authority; open that record before relying on a verdict, and do not restart a study without a new
authorization. Failed approaches stay recorded because their measurements constrain the next design.

| Approach | Verdict (record's own words) | Record |
|---|---|---|
| Scalar 5D, s5c (`OI-190`): coverage of candidate F2 | Tier-S coverage **FAIL (futility)**, independently reproduced | `docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md` |
| s5c development finding | the purity background method biases the highest-W cells by about −4% at nominal truth (development-level, in pseudo-experiments; not a real-data bias or a corrected central value) | `docs/orchestration/OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md` |
| s5n (`OI-191`): negweight-refined nominal | **STAGE1_FAIL** | `docs/orchestration/OUTCOME-20260925-s5n-stage1-development-fail.md` |
| s5e (`OI-192`): candidate R | **A_FAIL** (A3, numerical reproducibility floor on data); campaign **CLOSED** | `docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md` |
| s5p (`OI-193`): precision-measurement branch | **NOT ADMITTED** at the Stage-2 exit (amendment 4) | `docs/orchestration/RECORD-20260927-s5p-stage2-exit.md`; `DELIVERY-20261006-s5p-campaign-terminal.md` §1 |
| Scalar-5D model dependence from existing outputs | no bias–variance tradeoff established (same-analyst synthesis, no fresh independent review); next measurement **DEFERRED**, with reconsideration criteria in its `PROPOSAL.md` | `nd-unfolding/gbdt_model_dependence/README.md` (VL163) |
| Cause 3 two-member assessment (trunk `M1`, `s_proj`) | (B) ASSESSABLE **FAIL**, recorded once, no retry; cause 3 is **not** discharged and the seed sensitivity remains the principal open question (`AGENTS.md`) | `docs/orchestration/OUTCOME-20260920-cause3-two-member-assessable-FAIL.md` |
| Mean-centered 5D covariance | disqualified and refused in code (`project_cov_nd.py --expect-variant`) | `AGENTS.md`, quarantined-candidates row |
| PET central/statistical pairing (`OI-126`) | pairing **declined**; PET demoted to diagnostic (ruled 2026-08-20) | `docs/OPEN_ITEMS.md` `OI-126` |
| PET routing / object representation | **NO_PASS**; "keep family pooling as the production default" — "a practical development choice under an inconclusive accuracy result, not a finding that pooling is better" | `nd-unfolding/pet/direct_token_comparison/RECOMMENDATION-20260918.md` |
| PET final-design selection | **NO_ELIGIBLE_DESIGN**; nothing adopted (VL164–VL167) | `nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md` |
| Other PET campaigns (configuration, improvement, PET vs GBDT, generator diagnosis) | diagnostic; see where each ends | `nd-unfolding/pet/README.md` |
| Gregor PET2 / typed-object tokens (July) | retain the current estimator; **do not promote** (July assessment; typed-descriptor development continues, `nd-unfolding/pet/TYPED_DESCRIPTOR_STATUS.md`) | `git show evidence/gregor-pet2-rescued-delta-136889de:docs/GREGOR_PET2_OMNIFOLD_ASSESSMENT.md` |
| 2D statistical band `VL162` | fixed-truth coverage **FAIL-undercoverage** (VL169). Its completeness defect is fixed (`KNOWN_ISSUES.md` 84) and the band is replaced by `VL170`, which has **not** been coverage re-tested (`KNOWN_ISSUES.md` 85) | `docs/orchestration/OUTCOME-20261005-2d-fixed-truth-coverage-fail.md` |
| 1D binned `p_T` study | closed equivalence/debug cross-check | evidence tag, above |

Process failures (review loops, coordinator-as-authority, trusting generated quotes) are in
`docs/orchestration/CAMPAIGN-REVIEW-20260929.md` §4. Defects and traps live in `KNOWN_ISSUES.md`.

---

## Current versus historical documents

Most Markdown in this tree is a dated record of something that already happened. Use this key before
treating a document as an instruction.

| Kind | Current or historical | How to tell |
|---|---|---|
| `AGENTS.md`, `docs/CURRENT_WORK.md`, `docs/orchestration/CATALOG.md`, this README | current routers | they route; they are not evidence |
| `VALIDATION_LEDGER.md`, `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md` | current authorities; order is not chronological | the row, not the file, is the unit |
| `*_STATUS.md` | current, but banner-stacked by date | read the top banner and any correction note; older banners are history |
| `docs/orchestration/*` dated records (`HANDOFF-`, `PLAN-`, `OUTCOME-`, `DECISION-`, `RECORD-`, …) | historical once their event concludes | `docs/orchestration/MANIFEST.tsv` gives `class` (`LIVE`/`ARCHIVAL`/`MACHINE`/`DEAD`) and `event_status`; see `CONVENTION-document-retention.md` |
| `docs/orchestration/state/`, `runs/`, `receipts/` | machine records | open one exact file when a live document names it; never load wholesale |
| `docs/orchestration/LIVE-STATE.md` | a generated view that can be stale | it prints its own generation time; check freshness before use |
| Root `REMEDIATION_DELIVERABLES.md`, `REMEDIATION_META_PROMPTS.md` (July), `DESIGN-20260902-declarative-routing-register.md` | historical records kept at their cited paths | the REMEDIATION headers say "UNCOMMITTED working-tree" at HEAD `3e85589` (July); the DESIGN file is dated in its name |
| `docs/PREPUB_READINESS.md`, `docs/PUBLICATION_COMPLETION_RUNBOOK.md`, `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md` | retired (2026-06-09) or July-era instructions | the current publication path is in `docs/publication/` and the s5p records |
| Paths removed from `main` | historical, recoverable | `docs/POST_PUBLICATION_REORG_PLAN.md` and `CATALOG.md` list each family with its `evidence/*` tag; recover with `git show <tag>:<path>` |
| Local scratch, worktrees and out-of-repo archives | machine-local | `docs/LOCAL_CHECKOUTS_AND_STORAGE.md` |

---

## Repository layout

```
MINERvA-OmniFold/
├── AGENTS.md                              # scientific front door: states + evidence routes
├── CLAUDE.md                              # auto-loaded bootstrap for AI assistants
├── VALIDATION_LEDGER.md                   # every quotable number, with its evidence
├── KNOWN_ISSUES.md                        # read before changing code
├── LITERATURE_NOTES.md                    # external-paper notes
├── REMEDIATION_DELIVERABLES.md            # historical (July) remediation record
├── REMEDIATION_META_PROMPTS.md            #   and its prompt records (historical)
├── DESIGN-20260902-declarative-routing-register.md  # historical control-plane design record
│
├── 2d-unfolding/                          # 2D production measurement
│   ├── unfold_2d_omnifold_unbinned.py     #   main 2D unfolding driver
│   ├── plot_2d_*.py, compare_to_paper_*.py, diagnose_*.py …
│   ├── sbatch_evloop_array.sh             #   event-loop array (NERSC SLURM)
│   ├── sbatch_hadd_MEFHC.sh               #   per-playlist merge
│   ├── sbatch_unfold_2d_MEFHC*.sh         #   central unfold, universes, seedscan, bootstrap
│   ├── 2D_OMNIFOLD_STUDY_STATUS.md        #   status / running log
│   ├── 2D_OMNIFOLD_REFERENCE.md           #   invariants + current commands (2D and 3D)
│   ├── 2D_OMNIFOLD_RUN_LOG.md, PLOT_GUIDE.md
│   ├── unbinned_1d_study/                 #   1D pT_µ closure study (precursor)
│   ├── minerva_paper_anc/                 #   ancillary files from arXiv:2106.16210
│   └── playlist_manifests/                #   per-playlist Data/MC file lists
│
├── 3d-unfolding/                          # 3D E_avail extension
│   ├── unfold_3d_omnifold_unbinned.py     #   3D driver (imports the 2D helpers)
│   ├── xsec_3d.py                         #   xsec extraction + E_avail marginal + projections
│   ├── build_bootstrap_band_3d.py, plot_*.py
│   ├── sbatch_*_3d*.sh                    #   3D event loop / unfold / hadd / bootstrap
│   ├── uq_3d/                             #   3D uncertainty products
│   ├── genie/                             #   generator comparison inputs
│   └── 3D_OMNIFOLD_STATUS.md, 3D_OMNIFOLD_RUN_LOG.md, 3D_SYSTEMATIC_UQ_PLAN.md, README.md
│
├── nd-unfolding/                          # scalar 4D/5D + full-event (PET/FPS)
│   ├── mnv_guarded_run.py                 #   guarded entrypoint — route new compute here
│   ├── p4_lib.py                          #   pinned production configuration
│   ├── MANIFEST.md                        #   launcher router: current routes and retired launchers
│   ├── s5p_*.py, s5c_*.py, s5n_*.py, s5e_*.py  # scalar-5D campaign code (s5p: joint-5D inference)
│   ├── uq_4d/, uq_5d/, uq_fps/            #   uncertainty products per dimensionality
│   ├── pet/                               #   point-cloud (PET) study
│   ├── products/                          #   extracted products
│   ├── tests/                             #   the test suite that pins these contracts
│   └── ND_OMNIFOLD_STATUS.md, PET_UQ_REMEDIATION_STATUS.md, CORRECTED_UQ_PRODUCTION_STATUS.md, FPS_PILOT.md
│
├── docs/                                  # deliverables + governance
│   ├── analysis-note/                     #   LaTeX sources for all three builds (see Deliverables)
│   ├── CURRENT_WORK.md, CURRENT_WORK_BACKLOG.md
│   ├── OPEN_ITEMS.md                      #   the OI-* rows; the archive holds closed months
│   ├── ESTIMATOR_REGISTRY.md, EAVAIL_DEFINITION.md, HIGHER_DIM_OMNIFOLD_DESIGN.md
│   ├── PUBLICATION_COMPLETION_RUNBOOK.md, PREPUB_READINESS.md  # July-era / retired
│   ├── publication/                       #   article decision, claims, reviews, release and submission records
│   ├── LOCAL_CHECKOUTS_AND_STORAGE.md     #   local worktrees, scratch and out-of-repo archives
│   ├── known-issues/, open-items/         #   long-form records behind the tables
│   └── orchestration/                     #   process plane: PLAYBOOK.md, CATALOG.md,
│                                          #   MANIFEST.tsv, LIVE-STATE.md, state/, receipts
│
├── publication/                           # article code: release replay/verify, figures, W1/W2 checks
├── reproduction/s5p/                      # tiered replay of the joint-5D inference (README)
├── tools/developer/                       # opt-in code navigation and test runner (README)
├── lib/                                   # shared shell/python helpers (resume guard, backfill)
├── omnifold_nn/                           # NN OmniFold implementation + examples
├── unbinned_unfolding/                    # RooUnfold fork (mostly upstream, gitignored)
│   └── python/omnifold.py                 #   only the local edits are tracked
├── MINERvA101/                            # MINERvA 101 tutorial clones (mostly gitignored)
│   ├── MINERvA-101-Cross-Section/         #   only the local edits are tracked, see below
│   └── opt/                               #   installed binaries; local build only, absent in a clone
│
├── setup_salloc_env.sh                    # self-locating env setup (repo root, not a subdir)
├── start_alloc.sh, alloc_run.sh           # interactive salloc helpers
├── technote_style.py                      # shared matplotlib style for note figures
├── .githooks/                             # pre-commit + commit-msg gates (enable per clone)
├── .agents/skills/                        # vendored agent skills (README)
├── orchestration -> docs/orchestration    # symlink, kept for older paths
├── LICENSE, THIRD_PARTY_LICENSES.md
└── .gitignore, .gitattributes, .git-blame-ignore-revs
```

`MINERvA101/` and `unbinned_unfolding/` are siblings of the analysis
directories; `setup_salloc_env.sh` lives at the **repository root** and is
self-locating, so paths resolve wherever the repo is checked out.

---

## How this integrates with upstream

### MINERvA 101 tutorial

The MINERvA 101 cross-section tutorial
(<https://github.com/MinervaExpt/MINERvA-101-Cross-Section>) provides the
event-loop framework that reads MINERvA AnaTuples, applies cuts, fills response
matrices, and produces the migration histograms that downstream unfolding
consumes. It is built on top of MAT (the MINERvA analysis toolkit),
MAT-MINERvA, GENIEXSecExtract and UnfoldUtils, all shipped as siblings under
`MINERvA101/`.

The tutorial is treated as a **vendored dependency**: the full upstream
workspace can live locally under `MINERvA101/`, but the outer repository
gitignores that tree and re-adds only the modified files via negation patterns
in `.gitignore`. The tracked overlay is exactly:

| File | What changed |
|------|----------------|
| `runEventLoop.cpp` | Baseline event loop, modifications for production runs |
| `runEventLoopOmniFold.cpp` | New event-loop variant that emits the per-event ntuple OmniFold needs |
| `runEventLoopMod.cpp` | Intermediate variant kept for diff/debug |
| `runEventLoopOmniFold_OLD.cpp`, `_OLDEST.cpp` | Snapshots for reference |
| `event/CVUniverse.h` | `IsMinosMatchMuon()` patch |
| `util/Binning.h` | 2D `(p_T, p_∥)` binning matching arXiv:2106.16210 |
| `cuts/MaxPtMu.h` | New cut implementation |
| `ExtractCrossSection.cpp` | Cross-section extraction adjustments |
| `CMakeLists.txt` | Build wiring for the new sources |

The build system expects these files at their original locations inside the
tutorial tree, which is why negation patterns are used rather than a separate
`patches/` directory. The build directory
(`MINERvA101/MINERvA-101-Cross-Section/build/`) is gitignored.

> **Note:** the upstream `.git/` directory was removed from this in-tree copy of
> `MINERvA-101-Cross-Section/` so the outer repo can track the overlay files as
> plain files (git refuses to descend into nested repositories). To diff or pull
> from upstream, work from a fresh clone outside this repository.

### unbinned_unfolding (RooUnfold fork)

`unbinned_unfolding/` is a fork of RooUnfold that adds the unbinned/multi-fold
OmniFold implementation (<https://gitlab.cern.ch/RooUnfold/RooUnfold> plus the
OmniFold authors' extensions). `2d-unfolding/unfold_2d_omnifold_unbinned.py`
imports `unbinned_unfolding.python.omnifold` and uses its iterative-reweighting
loop. Like the tutorial, the full local tree is gitignored and only the edits
are tracked:

| File | What changed |
|------|----------------|
| `python/omnifold.py` | Modifications to the iterative-reweight implementation |
| `python/omnifold_old.py` | Pre-edit snapshot kept for diff |

> **Note:** the upstream `.git/` directory was removed from this in-tree copy
> for the same reason as above.

---

## Setup

To rebuild the analysis environment from a fresh clone:

1. **Clone the MINERvA 101 tutorial bundle** into `MINERvA101/`:
   ```bash
   cd MINERvA101
   git clone https://github.com/MinervaExpt/MINERvA-101-Cross-Section.git
   git clone https://github.com/MinervaExpt/MAT.git
   git clone https://github.com/MinervaExpt/MAT-MINERvA.git
   git clone https://github.com/MinervaExpt/GENIEXSecExtract.git
   git clone https://github.com/MinervaExpt/UnfoldUtils.git
   ```
   The modified files are already tracked at their canonical paths, so a
   `git checkout` after the clones restores the overlay.

2. **Clone the RooUnfold-based `unbinned_unfolding` package** into
   `unbinned_unfolding/` (sibling to `MINERvA101/`), then let the tracked
   `python/omnifold.py` overlay take effect.

3. **Build** the MAT stack and the cross-section tutorial — see the MINERvA 101
   wiki. The canonical event-loop binary lands in `MINERvA101/opt/bin/`.

4. **Source the environment**, from the repository root:
   ```bash
   source setup_salloc_env.sh
   ```
   Note that ROOT and TensorFlow live in **separate** environments here; no
   single interpreter has both, which constrains which steps can share a job.

5. **Run the event loop** to produce the OmniFold ntuples, then merge:
   ```bash
   sbatch 2d-unfolding/sbatch_evloop_array.sh
   sbatch 2d-unfolding/sbatch_hadd_MEFHC.sh
   ```

6. **Run the unfolding.** Commands are workstream-specific and change; take them
   from the status/reference docs rather than from this file:
   ```bash
   sbatch 2d-unfolding/sbatch_unfold_2d_MEFHC.sh                    # 2D central unfold
   sbatch 2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full.sh   # systematic universes
   sbatch 3d-unfolding/sbatch_unfold_3d.sh                          # 3D
   ```
   See `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` for the invariants that apply to
   every run (it covers 3D as well) and each `*_STATUS.md` for the running log.

7. **For 4D/5D and full-event work**, route new compute through the guarded
   entrypoint rather than calling drivers directly:
   ```bash
   python3 nd-unfolding/mnv_guarded_run.py …
   ```
   Direct invocation can pick up another checkout's modules while reporting
   every pinned file as current; the guard exists to prevent that.

---

## Deliverables

Three audience-tiered PDFs are built from one shared LaTeX source set in
`docs/analysis-note/`:

| Target | Driver | Audience |
|---|---|---|
| Internal analysis note | `main_note.tex` | full detail, including retracted values shown struck |
| Primer | `main_primer.tex` | short orientation |
| External paper | `main_paper.tex` | a distillation, not an extract |

Build instructions are in [`docs/analysis-note/README.md`](docs/analysis-note/README.md). The article's
state and remaining author actions are in `docs/publication/submission/PACKAGE-MANIFEST-20261006.md`.

```bash
cd docs/analysis-note && bash build_all.sh     # needs pdflatex + biber + python3
```

`build_all.sh` forces the rebuild, proves each PDF was written by that run, and
then runs `check_dead_containment.py`, which enforces that retracted (struck)
values reach the **note** build only and never the primer or paper. Every skip
in that stage is fatal by design: a containment pass over a stale PDF is worse
than no check. `test_build_all.py` is its test suite. Built PDFs are gitignored;
the tracked figure set lives in `docs/analysis-note/figures/`.

---

## Conventions

- **Enable the hooks per clone** — they are inert otherwise:
  ```bash
  git config core.hooksPath .githooks
  ```
  `pre-commit` runs the process-plane gates (findings/ledger/open-item id lints,
  receipt hash bindings, manifest and control-plane checks); `commit-msg`
  records what passed. Do not `--no-verify` past a red gate, and do not edit a
  digest to make one green.
- **Per-workstream STATUS + RUN_LOG.** Results are live only once their evidence
  and records land in a commit; a relayed or uncommitted result is not quotable.
- **Evidence tags.** Retired workspaces and frozen states are preserved as
  pushed `evidence/*` tags rather than deleted, so history stays recoverable.
- **Audit work is read-only** and runs in an isolated worktree.

---

## What is *not* included

Only source, scripts, documentation, records and small reference data are
tracked; `.gitignore` enforces the rest.

### Upstream code (not ours to redistribute)

- `MINERvA101/MAT/`, `MAT-MINERvA/`, `GENIEXSecExtract/`, `UnfoldUtils/`,
  `MINERvA101/opt/` — clean upstream clones and built binaries.
- `MINERvA101/MINERvA-101-Cross-Section/` *except* the overlay files listed above.
- `unbinned_unfolding/` *except* `python/omnifold.py` and `python/omnifold_old.py`.

### Generated outputs (large, reproducible)

- `*.root` — event-loop output (per-playlist response matrices, OmniFold
  ntuples) and merged histograms. Individual files reach the GB scale and the
  campaign's total scratch footprint is measured in TB, on `pscratch` rather
  than in git.
- `*.npz`, `*.h5`, `*.pkl` — covariance products, replica families, trained
  estimator weights.
- `*.png`, `*.pdf` — generated plots. **Exception:** figures under `docs/` are
  negated back in, because the note builds need them; nothing under
  `2d-unfolding/` is tracked as an image any more.
- `*.out`, `*.err`, `*.log` — SLURM job logs.
- `build/`, `*.o`, `*.d`, `*.so`, `*.a` — compiler output.
- `__pycache__/`, `*.pyc`, `.ipynb_checkpoints/` — caches.

### Working directories that exist only where the analysis runs

`2d-unfolding/baseline_flux/`, `component_dump_*/`, `evloop_work_*/`,
`validate_*/`, `mii/`, `weights/` — per-playlist and per-member scratch created
by the drivers. Gitignored; absence in a fresh clone is expected.

### Papers / references

Copies of published papers kept for working reference are gitignored. Cite the
arXiv or journal version; see [Reference](#reference).

---

## Licensing and attribution

The top-level `LICENSE` applies to the original analysis code and
documentation. It does not relicense upstream software, upstream-derived overlay
files, published-paper ancillary files, or external data products.

See `THIRD_PARTY_LICENSES.md` for upstream projects, local license status and
citation notes. Some upstream-derived overlay files come from local checkouts
that contained no license file, so provenance is documented explicitly rather
than claiming a blanket license for all contents.

---

## Reference

- **Paper being reproduced:** D. Ruterbories *et al.* (MINERvA Collaboration),
  *Measurement of inclusive charged-current $\nu_\mu$ cross sections as a
  function of muon kinematics at a mean neutrino energy of 6 GeV on
  hydrocarbon*, Phys. Rev. D **104**, 092007 (2021),
  arXiv:[2106.16210](https://arxiv.org/abs/2106.16210).
- **OmniFold:** A. Andreassen, P. T. Komiske, E. M. Metodiev, B. Nachman and
  J. Thaler, *OmniFold: A Method to Simultaneously Unfold All Observables*,
  Phys. Rev. Lett. **124**, 182001 (2020),
  arXiv:[1911.09107](https://arxiv.org/abs/1911.09107).
- **High-dimensional deconvolution:** A. Andreassen, P. T. Komiske,
  E. M. Metodiev, B. Nachman, A. Suresh and J. Thaler, *Scaffolding Simulations
  with Deep Learning for High-dimensional Deconvolution*, ICLR simDL workshop
  (2021), arXiv:[2105.04448](https://arxiv.org/abs/2105.04448).
- **MINERvA 101 tutorial:**
  <https://github.com/MinervaExpt/MINERvA-101-Cross-Section>.
- **RooUnfold-based unbinned unfolding:**
  <https://github.com/rymilton/unbinned_unfolding>.

Full bibliography: `docs/analysis-note/technote.bib`.

---

## Maintenance

**No automated check covers this file.** It is in no `docs/orchestration/MANIFEST.tsv`
row, no pre-commit gate, and no build; the note's containment checker is scoped
to `docs/analysis-note/`. Between 2026-06-14 and 2026-08-21 it went 1,938 commits without a
refresh, and misidentified the paper being reproduced for that entire window. Two
consequences, both deliberate:

1. **Nothing here is evidence.** Every claim about a result routes to
   `VALIDATION_LEDGER.md` or a `*_STATUS.md` instead of restating it.
2. **Refresh it by hand whenever the tree's shape changes** — a new workstream
   directory, a renamed deliverable, a retired workspace — and record what it
   was verified against.

Last verified on 2026-10-07: every tracked path in the layout tree exists at `5770db3b`
plus this change (`MINERvA101/opt/` is local-only by design); the overlay tables match
`git ls-files`, and the shared-code table was re-measured with `git grep`.
