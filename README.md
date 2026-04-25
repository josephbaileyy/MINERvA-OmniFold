# MINERvA 2D OmniFold Unfolding

Reproduction of the double-differential muon-neutrino CC-inclusive cross
section `d²σ / (dp_T dp_∥)` from MINERvA medium-energy data using the
**OmniFold** unbinned iterative-Bayesian unfolding technique
(arXiv:1911.09107, arXiv:2105.04448), benchmarked against the binned IBU
result published in arXiv:2106.16210.

This repository contains my analysis scripts, documentation, and the
specific edits I made to two upstream code packages (the MINERvA 101
tutorial framework and the RooUnfold-based `unbinned_unfolding` package).
Upstream code itself is **not** included — see
[Setup](#setup) for how to obtain it.

---

## Repository layout

```
MINERvA-unfolding/
├── 2d-unfolding/                          # My analysis code (tracked)
│   ├── unfold_2d_omnifold_unbinned.py     # main 2D unfolding driver
│   ├── plot_2d_*.py, compare_to_paper_*.py, diagnose_*.py …
│   ├── sbatch_*.sh                        # NERSC SLURM submission scripts
│   ├── 2D_OMNIFOLD_*.md, PLOT_GUIDE.md    # study status / run log / plotting notes
│   ├── *.json                             # small summary metadata from analyses
│   ├── binned_study/                      # standalone binned-OmniFold cross-check
│   ├── unbinned_1d_study/                 # 1D pT_µ closure study (precursor)
│   └── minerva_paper_anc/                 # ancillary files from arXiv:2106.16210
│
├── unbinned_unfolding/                    # RooUnfold fork (mostly upstream, gitignored)
│   └── python/omnifold.py                 # only my edits are tracked
│
├── MINERvA101/                            # MINERvA 101 tutorial clones (mostly gitignored)
│   └── MINERvA-101-Cross-Section/         # only my edits are tracked, see below
│
├── AGENTS.md                              # working notes / context for AI assistants
├── README.md                              # this file
└── .gitignore
```

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

I treat the tutorial as a **vendored dependency**: the entire `MINERvA101/`
tree is gitignored, and only the files I had to modify are re-added via
negation patterns in `.gitignore`. My edits in
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
> separate working copy I keep at
> `/pscratch/sd/j/josephrb/MINERvA101/MINERvA-101-Cross-Section/`.

### unbinned_unfolding (RooUnfold fork)

`unbinned_unfolding/` is a fork of RooUnfold that adds the
unbinned/multi-fold OmniFold implementation
(<https://gitlab.cern.ch/RooUnfold/RooUnfold> + the OmniFold authors'
extensions). The 2D unfolding driver in
`2d-unfolding/unfold_2d_omnifold_unbinned.py` imports
`unbinned_unfolding.python.omnifold` and uses its iterative reweighting
loop.

Like the tutorial, this is treated as a vendored dependency: the whole tree
is gitignored, and only my edits are tracked:

| File | What I changed |
|------|----------------|
| `python/omnifold.py` | Modifications to the iterative-reweight implementation |
| `python/omnifold_old.py` | Pre-edit snapshot kept for diff |

> **Note:** The upstream `.git/` directory was removed from this in-tree copy
> of `unbinned_unfolding/` for the same reason as above. The intact upstream
> clone lives at `/pscratch/sd/j/josephrb/MINERvA101/OmniFold/unbinned_unfolding/`
> for diff/pull purposes.

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
  `MINERvA101/UnfoldUtils/`, `MINERvA101/opt/`, `MINERvA101/OmniFold/` — clean
  upstream clones, no edits from me.
- `MINERvA101/MINERvA-101-Cross-Section/` *except* the specific files listed
  above.
- `unbinned_unfolding/` *except* `python/omnifold.py` and `python/omnifold_old.py`.

### Generated outputs (large, reproducible)

- `*.root` — event-loop output (per-playlist response matrices, OmniFold
  ntuples) and `hadd`-merged histograms. Individual files range from ~150 MB
  to ~1.8 GB. Total artifact volume is roughly 10 GB.
- `*.png`, `*.pdf` — plots produced by the `plot_*.py` and `diagnose_*.py`
  scripts. Reproduce by re-running the corresponding script.
- `*.out`, `*.err`, `*.log` — SLURM job logs.
- `build/`, `*.o`, `*.d`, `*.so`, `*.a` — compiler output.

### Caches

- `__pycache__/`, `*.pyc`, `.ipynb_checkpoints/` — Python and Jupyter scratch.

### Archived working trees

- `archive_pre_minos_fix/` (3.9 GB), `archive_2026-03-production-cleanup/`
  (375 MB) — historical snapshots of intermediate ROOT files kept locally
  for provenance, not relevant to the published analysis.
- `baseline_flux/`, `component_dump_*/`, `validate_*/`, `evloop_work_*/` —
  per-playlist scratch directories used during diagnostic runs.

### Papers / references

- `reference/Ruterbories_2106.16210v3.pdf`,
  `reference/Physics_191_PRL.pdf` — copies of published papers I refer to
  while working. Not redistributable from here; cite the arXiv/journal versions.

---

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
