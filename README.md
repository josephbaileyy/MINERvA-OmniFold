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
| Build the note, primer or paper | `docs/analysis-note/` and [Deliverables](#deliverables) |
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
| **Scalar 4D/5D** `+ q3, W` | `nd-unfolding/` | `ND_OMNIFOLD_STATUS.md` | Extends the scalar feature set through `q3` and `W`. Central values and closures are complete; the **publication uncertainty product is the adopted scalar-5D covariance**, and covariance candidates carry explicit quarantine states — read the ledger, not a summary. |
| **Full-event: PET / FPS** | `nd-unfolding/pet/`, `nd-unfolding/uq_fps/` | `PET_UQ_REMEDIATION_STATUS.md` | Point-cloud (PET) and full-phase-space studies of low-level event representations. **Diagnostic and method-development work, not a publication uncertainty product** (ruled 2026-08-20). No full-event total covariance is adopted. |

The 1D binned $p_T^\mu$ study is a closed equivalence/debug cross-check, not a
publication result. Its workspace was retired from `main` on 2026-08-20 and is
recoverable in full from the pushed evidence tag:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/binned_study/README.md
```

---

## Repository layout

```
MINERvA-OmniFold/
├── AGENTS.md                              # scientific front door: states + evidence routes
├── CLAUDE.md                              # auto-loaded bootstrap for AI assistants
├── VALIDATION_LEDGER.md                   # every quotable number, with its evidence
├── KNOWN_ISSUES.md                        # read before changing code
├── LITERATURE_NOTES.md                    # external-paper notes
├── REMEDIATION_DELIVERABLES.md            # remediation-campaign deliverables
├── REMEDIATION_META_PROMPTS.md            #   and its prompt records
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
│   ├── PUBLICATION_COMPLETION_RUNBOOK.md, PREPUB_READINESS.md
│   ├── known-issues/, open-items/         #   long-form records behind the tables
│   └── orchestration/                     #   process plane: PLAYBOOK.md, CATALOG.md,
│                                          #   MANIFEST.tsv, LIVE-STATE.md, state/, receipts
│
├── lib/                                   # shared shell/python helpers (resume guard, backfill)
├── omnifold_nn/                           # NN OmniFold implementation + examples
├── unbinned_unfolding/                    # RooUnfold fork (mostly upstream, gitignored)
│   └── python/omnifold.py                 #   only the local edits are tracked
├── MINERvA101/                            # MINERvA 101 tutorial clones (mostly gitignored)
│   ├── MINERvA-101-Cross-Section/         #   only the local edits are tracked, see below
│   └── opt/                               #   installed binaries (runEventLoopOmniFold etc.)
│
├── setup_salloc_env.sh                    # self-locating env setup (repo root, not a subdir)
├── start_alloc.sh, alloc_run.sh           # interactive salloc helpers
├── technote_style.py                      # shared matplotlib style for note figures
├── .githooks/                             # pre-commit + commit-msg gates (enable per clone)
├── .agents/                               # agent-side assets
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

The [publication source map and completion plan](docs/analysis-note/README.md) identifies work that
can proceed while the scalar-5D covariance and response-robustness paths are active, without
pre-committing their scientific outcome.

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

Last verified against `80eeb441` on 2026-08-21: every path named above exists
at that commit, and the overlay tables match `git ls-files`.
