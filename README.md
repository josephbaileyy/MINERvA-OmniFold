# MINERvA 2D OmniFold Unfolding

Reproduction of the double-differential muon-neutrino CC-inclusive cross
section `d²σ / (dp_T dp_∥)` from MINERvA medium-energy data using the
**OmniFold** unbinned iterative-Bayesian unfolding technique
(arXiv:1911.09107, arXiv:2105.04448), benchmarked against the binned IBU
result published in arXiv:2106.16210.

This repository contains my analysis scripts, documentation, and the
selected edits I made to upstream code packages used by the analysis (the
MINERvA 101 tutorial framework and the RooUnfold-based
`unbinned_unfolding` package). Full upstream working trees and generated
outputs are **not** part of the public repository; only selected overlay files
are tracked so the analysis can be rebuilt. See [Setup](#setup) for how to
obtain the upstream packages.

---

## Repository layout

```
MINERvA-OmniFold/
├── 2d-unfolding/                          # My analysis code (tracked)
│   ├── unfold_2d_omnifold_unbinned.py     # main 2D unfolding driver
│   ├── plot_2d_*.py, compare_to_paper_*.py, diagnose_*.py …
│   ├── sbatch_*.sh                        # NERSC SLURM submission scripts
│   ├── 2D_OMNIFOLD_*.md, PLOT_GUIDE.md    # study status / run log / plotting notes
│   ├── *.json                             # small summary metadata from analyses
│   ├── *.png                              # current production plots (tracked)
│   ├── binned_study/                      # standalone binned-OmniFold cross-check
│   ├── unbinned_1d_study/                 # 1D pT_µ closure study (precursor)
│   ├── minerva_paper_anc/                 # ancillary files from arXiv:2106.16210
│   ├── playlist_manifests/                # per-playlist Data/MC file lists
│   ├── baseline_flux/                     # per-playlist baseline flux ROOTs (gitignored)
│   └── reference/                         # reference papers (Ruterbories PDF)
│
├── unbinned_unfolding/                    # RooUnfold fork (mostly upstream, gitignored)
│   ├── build/                             # in-tree cmake build (gitignored)
│   └── python/omnifold.py                 # only my edits are tracked
│
├── MINERvA101/                            # MINERvA 101 tutorial clones (mostly gitignored)
│   ├── MINERvA-101-Cross-Section/         # only my edits are tracked, see below
│   └── opt/                               # installed binaries (runEventLoopOmniFold etc.)
│
├── setup_salloc_env.sh                    # self-locating env setup (sources all the above)
├── start_alloc.sh                         # interactive salloc helper
├── AGENTS.md                              # working notes / context for AI assistants
├── LICENSE                                # license for my original code/docs
├── THIRD_PARTY_LICENSES.md                # upstream attribution and license notes
├── README.md                              # this file
└── .gitignore
```

The layout keeps `MINERvA101/` and `unbinned_unfolding/` as siblings of
`2d-unfolding/`; `setup_salloc_env.sh` is self-locating, so all paths
resolve relative to wherever the repo is checked out.

---

## How this integrates with upstream

### MINERvA 101 tutorial

The MINERvA 101 cross-section tutorial
(<https://github.com/MinervaExpt/MINERvA-101-Cross-Section>) provides the
event-loop framework that reads MINERvA AnaTuples, applies cuts, fills
response matrices, and produces the migration histograms that downstream
unfolding consumes. The tutorial is built on top of MAT (the MINERvA
analysis toolkit), MAT-MINERvA, GENIEXSecExtract, and UnfoldUtils, all
shipped as siblings under `MINERvA101/`.

I treat the tutorial as a **vendored dependency**: the full upstream
workspace can live locally under `MINERvA101/`, but the outer repository
gitignores that tree and re-adds only the files I had to modify via negation
patterns in `.gitignore`. My edits in
`MINERvA101/MINERvA-101-Cross-Section/`:

| File | What I changed |
|------|----------------|
| `runEventLoop.cpp` | Baseline event loop, modifications for production runs |
| `runEventLoopOmniFold.cpp` | New event loop variant that emits the per-event ntuple OmniFold needs |
| `runEventLoopMod.cpp` | Intermediate variant kept for diff/debug |
| `runEventLoopOmniFold_OLD.cpp`, `_OLDEST.cpp` | Snapshots for reference |
| `event/CVUniverse.h` | Added `IsMinosMatchMuon()` patch (2026-04-25) |
| `util/Binning.h` | 2D `(p_T, p_∥)` binning to match arXiv:2106.16210 |
| `cuts/MaxPtMu.h` | New cut implementation |
| `ExtractCrossSection.cpp` | Cross-section extraction adjustments |
| `CMakeLists.txt` | Build wiring for the new sources |

The build system expects these files in their original locations inside the
tutorial tree, which is why the negation-pattern approach is used rather
than copying them to a separate `patches/` directory. The build directory
(`MINERvA101/MINERvA-101-Cross-Section/build/`) is gitignored.

> **Note:** The upstream `.git/` directory was removed from this in-tree copy
> of `MINERvA-101-Cross-Section/` so the outer repo can track the negation
> patterns as plain files (git refuses to descend into nested repositories).
> To diff or pull from upstream, work from a fresh clone or from the
> separate pristine working copy outside this repository.

### unbinned_unfolding (RooUnfold fork)

`unbinned_unfolding/` is a fork of RooUnfold that adds the
unbinned/multi-fold OmniFold implementation
(<https://gitlab.cern.ch/RooUnfold/RooUnfold> + the OmniFold authors'
extensions). The 2D unfolding driver in
`2d-unfolding/unfold_2d_omnifold_unbinned.py` imports
`unbinned_unfolding.python.omnifold` and uses its iterative reweighting
loop.

Like the tutorial, this is treated as a vendored dependency: the full local
tree is gitignored, and only my edits are tracked:

| File | What I changed |
|------|----------------|
| `python/omnifold.py` | Modifications to the iterative-reweight implementation |
| `python/omnifold_old.py` | Pre-edit snapshot kept for diff |

> **Note:** The upstream `.git/` directory was removed from this in-tree copy
> of `unbinned_unfolding/` for the same reason as above. The intact upstream
> clone used for diff/pull work should live outside this repository.

---

## Setup

To rebuild the analysis environment from a fresh clone of this repo:

1. **Clone the MINERvA 101 tutorial bundle** into `MINERvA101/`:
   ```bash
   cd MINERvA101
   git clone https://github.com/MinervaExpt/MINERvA-101-Cross-Section.git
   git clone https://github.com/MinervaExpt/MAT.git
   git clone https://github.com/MinervaExpt/MAT-MINERvA.git
   git clone https://github.com/MinervaExpt/GENIEXSecExtract.git
   git clone https://github.com/MinervaExpt/UnfoldUtils.git
   ```
   Then overlay my modified files (they're already tracked by this repo at
   their canonical paths, so a `git checkout` after the clones is enough).

2. **Clone the RooUnfold-based unbinned_unfolding package** into
   `unbinned_unfolding/` (sibling to `MINERvA101/`), then let the tracked
   `python/omnifold.py` overlay take effect.

3. **Build** the MAT stack and the cross-section tutorial — see the MINERvA
   101 wiki for instructions
   (<https://cdcvs.fnal.gov/redmine/projects/minerva-101/wiki>).
   The canonical event-loop binary lands in `MINERvA101/opt/bin/`.

4. **Run the event loop** to produce the OmniFold ntuples
   (`runEventLoopOmniFold` per playlist) — `2d-unfolding/sbatch_evloop_array.sh`
   is the NERSC SLURM template I use.

5. **Run the 2D unfolding**:
   ```bash
   sbatch 2d-unfolding/sbatch_unfold_2d_fullstats.sh
   ```
   See `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` for current commands and
   `2D_OMNIFOLD_STUDY_STATUS.md` for the running log.

---

## What is *not* included in this repo

By design, only my source code, scripts, documentation, and a handful of
small reference text files are tracked. Several categories of file are
deliberately excluded; the `.gitignore` enforces this.

### Upstream code (not mine to redistribute)

- `MINERvA101/MAT/`, `MINERvA101/MAT-MINERvA/`, `MINERvA101/GENIEXSecExtract/`,
  `MINERvA101/UnfoldUtils/`, `MINERvA101/opt/` — clean upstream clones / built
  binaries, no edits from me.
- `MINERvA101/MINERvA-101-Cross-Section/` *except* the specific files listed
  above.
- `unbinned_unfolding/` *except* `python/omnifold.py` and `python/omnifold_old.py`.

### Generated outputs (large, reproducible)

- `*.root` — event-loop output (per-playlist response matrices, OmniFold
  ntuples) and `hadd`-merged histograms. Individual files range from ~150 MB
  to ~1.8 GB. Total artifact volume is roughly 10 GB.
- `*.pdf` — generated plots. The current production `*.png` files in
  `2d-unfolding/` are tracked; plots produced ad-hoc by `plot_*.py` /
  `diagnose_*.py` are gitignored unless explicitly added.
- `*.out`, `*.err`, `*.log` — SLURM job logs.
- `build/`, `*.o`, `*.d`, `*.so`, `*.a` — compiler output.

### Caches

- `__pycache__/`, `*.pyc`, `.ipynb_checkpoints/` — Python and Jupyter scratch.

### Archived working trees

- Historical snapshots of intermediate ROOT files (3.9 GB
  `archive_pre_minos_fix/`, 375 MB `archive_2026-03-production-cleanup/`,
  83 MB `component_dump_1A/`) live outside this repo at
  `/pscratch/sd/j/josephrb/MINERvA101/Documents/` for provenance only;
  they are not relevant to the published analysis.
- `2d-unfolding/baseline_flux/`, `component_dump_*/`, `validate_*/`,
  `evloop_work_*/` — per-playlist scratch directories used during
  diagnostic runs (gitignored).

### Papers / references

- `reference/Ruterbories_2106.16210v3.pdf`,
  `reference/Physics_191_PRL.pdf` — copies of published papers I refer to
  while working. Not redistributable from here; cite the arXiv/journal versions.

---

## Licensing and attribution

The top-level `LICENSE` applies to my original analysis code and
documentation. It does not relicense upstream software, selected
upstream-derived overlay files, published-paper ancillary files, or external
data products.

See `THIRD_PARTY_LICENSES.md` for the upstream projects, local license status,
and citation notes. In particular, some upstream-derived overlay files come
from local checkouts that did not contain a license file, so the repository
documents their provenance explicitly rather than claiming a blanket license
for all contents.

## Reference

- Paper being reproduced: A. Bercellie et al. (MINERvA),
  *Simultaneous Measurement of Muon Neutrino νμ Charged-Current Single π+
  Production in CH …*, Phys. Rev. Lett. 127, 081801 (2021),
  arXiv:[2106.16210](https://arxiv.org/abs/2106.16210).
- OmniFold: A. Andreassen et al., *OmniFold: A Method to Simultaneously
  Unfold All Observables*, Phys. Rev. Lett. 124, 182001 (2020),
  arXiv:[1911.09107](https://arxiv.org/abs/1911.09107).
- MINERvA 101 tutorial:
  <https://github.com/MinervaExpt/MINERvA-101-Cross-Section>.
- RooUnfold-based unbinned unfolding implementation:
  <https://github.com/rymilton/unbinned_unfolding>.
