# geanttw P2–P3: the design amendment (DRAFT, 2026-11-27)

This amends `../DECLARATION.md` §4 (P2, P3), §5, §6 and §7 for P2 and P3. It records the director's rulings D1–D4
of 2026-11-27 and the director's terms for P3's slim omnifiles. Where this file and the declaration differ, this
file governs P2–P3. P0's record (`../receipts-p0/`) is unchanged. **Nothing here runs before GEANTTW-BINDING-P2P3
and a GO for each step.**

## A1. The key: entry order (D1)

D1 (`d1/`) read the production universe dump's header only. Neither MC tree carries `mc_run`, `mc_subrun` or
`mc_nthEvtInFile`, and each has 32,849,103 entries. Under the director's ruling, **rows are joined on entry
order**, and P2 runs without `MNV101_DUMP_POINTCLOUD`, as P0 did.

**Why entry order can hold.** The production dump `UOMNI` was built by `hadd` of the 12 per-playlist files, in the
order 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P (`2d-unfolding/sbatch_hadd_MEFHC_universes_full.sh:32-43`). hadd
concatenates each tree in input order. P2's per-playlist dumps are concatenated in the same order. **C2 is what
makes the join trustworthy:** every non-target branch must be bitwise equal on that order.

**The 1L offset**, for the C2 pre-check, is the sum of 1A–1G's entries per tree. It comes from the per-playlist
files' headers, `2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root`. These files are not on cov2d's 36-path
list, where only the merged file is entry 7. They are still disclosed in the (C) request, and read like D1: header
only, through an O_NOATIME file object, with atime checked before and after. **C4 (`c4/`) settled it:** all 12 files are
present, and their entry counts sum exactly to UOMNI's in all four trees. 1L's slice is rows [20,716,792, 21,100,640)
of both MC trees, which is 383,848 rows, the count of P0's 1L dumps. For data it is [2,778,489, 2,828,361), and for
mc_background [407,731, 415,551).

## A2. P2, the event loop

- **The run.** The patched build (`prefix-pat`, from P0's build) runs on the 11 playlists other than 1L. 1L's P0
  output is reused, since C0 passed (P0 PASS, `../receipts-p0/`). Settings are P0's: `MNV101_DUMP_UNIVERSES` set
  to the GEANT bands, every other `MNV101_*` unset, and no `MNV101_DUMP_POINTCLOUD`.
- **The environment.** The binary is launched under `env -u BASH_ENV -u ENV`. A smoke check refuses unless both
  are unset in the job. This keeps a child bash from sourcing Lmod, which C0e's attribution found.
- **Tracing (D4).**
  - openat/open and the stat family (stat, lstat, newfstatat, statx, access) are traced on every playlist, with
    `strace -f -y`.
  - read/pread64 are traced on **one pilot playlist only**, and that playlist's overhead is measured against an
    untraced run of the same playlist.
  - The extra cost is **[0.05, 0.15] node-h, an ESTIMATE** that the pilot's measurement replaces. If the pilot's
    overhead exceeds it, P2 stops and reports before tracing more.
  - C0e's revised families (#1394) apply to every traced playlist.
- **Job names** are `geanttw_p2_<PL>`, plus `geanttw_p2_pilot_<PL>` and `geanttw_p2_pilotref_<PL>` for the pilot
  pair.
- **The fence** refuses on `^(cov2d|t2a|covfix_)` at job start and again just before the binary, read from sacct
  and never squeue. The covfix_ family comes from cov2d's answer (D), which cites `covfix_wrapper.py:131`.
  tune-generator submits no Slurm jobs.
- **Per-playlist limits** come from P0's measured walls, 353 s for pin and 435 s for pat, both under strace. The
  limit for a playlist PL is:

      limit_PL = ceil_to_minute(3 × 435 s × MCbytes_PL / MCbytes_1L), at least 00:30:00

  The MC bytes come from `ANATUPLE-SHA256.tsv`. The package prints each playlist's limit, and a job that reaches
  its limit stops P2 and comes back for a new price.
- **NuE.** P2's read of the NuE file through `SetNuEConstraint(true)` (`runEventLoopOmniFold.cpp:1698`) is covered
  by cov2d's grant (B) of 2026-11-27, verbatim in `cov2d-grants-20261127.md`, on P0's terms:
  - (a) the atime-post is 2026-11-15T02:21:21Z;
  - (b) cov2d's connects refuse while any geanttw_ job is live;
  - (c) each job logs atime_ns and mtime_ns, with UTC, immediately before and after the binary;
  - the fence runs at start and before the binary.

## A3. P3: two slim omnifiles and the unchanged driver

**The driver** is `2d-unfolding/unfold_2d_omnifold_unbinned.py` at sha256 `74a4ed69…`, which is Stage C's
`PROD_SHA` (`stageC/production/sbatch_prod.sh:23`). It is byte-identical on main since `c53e9c36`. It runs with
Stage C's universe argv (`sbatch_prod.sh:83-84, 116`):

    --omnifile SLIM --flux-universe-file FLUXU --verbose --mcfile MCFILE --iters 5 --use-weights
    --estimator lgbm --bkg-mode purity --out OUT --universe GEANT_<b>:<i> --seed 42 --branch-select derived

The pinned inputs are MCFILE `d40aea69…`, FLUXU `5eecae84…` and helper `e9623412…`.

**The seed.** S5's July GEANT unfolds (`sweeps.json` `15b57de9…`, `pn/GEANT_*`) record no seed. Seed 42 comes from
S4(ii)'s "July identity at seed 42" (`stageC/production/REPORT.md:65`). C3 tests it.

**The slims, under the director's terms.**
1. **C3 gates the slim approach.** C3 runs on the pinned slim. If it does not reproduce S5's three GEANT band
   matrices to C3's tolerance, that is a STOP before any patched run. The slim is never adjusted to make C3 pass.
2. **What the driver reads.** With `--branch-select derived`, the four loaders read exactly
   `expected_loader_branches` (`unfold_2d_omnifold_unbinned.py:991-1030`). A run refuses if the access-derived
   list differs from that rule (`:1044-1053`) or if a selected branch has no address (`:960-972`). For a GEANT
   universe (vertical, with no lateral branches in any tree), the union over the six universes is:
   - data: `measured`, `measured_pz`, `measured_pass`
   - mc_background: `sim_background`, `sim_background_pz`, `sim_background_pass`, and the six `w_bkg_GEANT_*`
   - mc_truth_denom: `MC`, `MC_pz`, and the six `w_truth_GEANT_*`
   - mc_signal_reco: `MC`, `MC_pz`, `sim`, `sim_pz`, `sim_pass`, the six `w_truth_GEANT_*` and the six
     `w_reco_GEANT_*`

   The builder imports the driver and takes this list from `expected_loader_branches`. It does not restate it.

   **Read by name, outside the loaders:**
   - the four trees (`:1646-1649`);
   - the p∥ presence checks on `sim_pz`, `MC_pz`, `sim_background_pz` and `measured_pz` (`:1658-1664`);
   - `dataPOTUsed` and `mcPOTUsed` (`:118-119`, refused if absent);
   - `hasTruthOnlyMisses` and `nTruthOnlyMisses` (`:1676-1677`). These are **silently defaulted if absent**.
   - `pTmu_fiducial_nucleons` (`:1690`). This is absent in UOMNI, and its absence is the driver's documented path.

   **Control C-SLIM** therefore requires:
   - the slim's top-level key set to equal UOMNI's exactly (D1: `data`, `dataPOTUsed`, `hasTruthOnlyMisses`,
     `mcPOTUsed`, `mc_background`, `mc_signal_reco`, `mc_truth_denom`, `nTruthOnlyMisses`);
   - each TParameter value to equal UOMNI's;
   - each tree's entry count to equal UOMNI's;
   - each copied branch to be bitwise equal to UOMNI's, entry by entry;
   - every name the driver probes with `GetBranch` or `FindObject` for these six universes to be present in the
     slim exactly when it is present in UOMNI.

   A test runs the unchanged driver on a slim missing one branch and requires it to refuse.
3. **Location and lifetime.** The slims are written only under `/pscratch/sd/j/josephrb/geanttw-20261124/p3/`, as
   `slim-pinned.root` and `slim-patched.root`, and never to CFS. Each one's size is checked against the estimate
   derived from its branches' header sizes. They are deleted once P3's receipts are accepted, unless Joseph says
   to keep them.
4. **Price, an ESTIMATE until the branch sizes are read.**
   - The slims hold 37 branches out of UOMNI's 952, plus the four TParameters. **C4 measured** those branches at
     5,857,242,672 B compressed and 6,458,621,231 B uncompressed, so a slim is about 5.9 GB, and two are about 12 GB.
   - The build is one plain ROOT read of about 5.86 GB compressed. It runs as one job, `geanttw_p3_slim`, at
     [0.02, 0.10] node-h and 0:20–1:00 wall. That is an ESTIMATE from the read size, until measured.
5. **The patched slim** is the pinned slim with only the six `w_truth_GEANT_*` columns replaced, in
   `mc_signal_reco` and `mc_truth_denom`, by P2's values concatenated in hadd order. **Control C-PATCH:** every
   other branch, key and TParameter equals the pinned slim bitwise.
6. **cov2d's (C)** is asked fresh, on exactly these terms:
   - an in-place, plain ROOT read of UOMNI's branches listed above;
   - a slim copy of that protected content, written to geanttw's root;
   - P0/P2's per-job atime log;
   - the `^(cov2d|t2a|covfix_)` fences.

   It also discloses the per-playlist header reads (A1) and the C2 pre-check's read of 1L's rows. The grant text
   goes in the package.

**D2: the miss rows.** The bound miss override, after `stageB/diagnostics/p5/build_miss_override.py`, carries P2's
patched `mc_truth_denom` weights onto the patched slim's miss rows in `mc_signal_reco`. **Control C-MISS:**
re-histogramming the override's denominator must equal P2's patched `mc_truth_denom` histogram **bitwise**. Both
are float64 sums of the same values in the same order, so bitwise is achievable. If the order cannot be made the
same, the tolerance is declared before the run. If the override needs the values of `hasTruthOnlyMisses` or
`nTruthOnlyMisses`, that read is its own item under (C).

**R3** is unchanged from the declaration.

## A4. The NuE grep of every bound source

`grep -n SetNuEConstraint` over every source P2–P3 binds: the S0-manifest event-loop tree (B/src/evloop, as built),
MAT at `35097b65`, MAT-MINERvA at `50d76314` and with `3e411c0d` applied, and P3's driver tree at M. The command,
the commits and every hit are committed in `c4/c4.out`, part 2. **Result:**
- In the bound evloop tree, `SetNuEConstraint(true)` is at `runEventLoopOmniFold.cpp:1698`, the P2 binary's source
  (sha256 `57792e42…`). The other hits are in programs P2 does not run: `runEventLoop`, `runEventLoopMod`, the
  `_OLD`/`_OLDEST` variants and `.ipynb_checkpoints` copies.
- MAT `35097b65` has one hit, a validation python script that is not in libMAT.
- MAT-MINERvA pin (`50d76314`) and pat (`6c5a7722`) have only the setter's declaration and definition
  (`MinervaUniverse.h:62`, `MinervaUniverse.cxx:314/320`), identical in both.
- So P2's NuE read comes only from `:1698`, which cov2d's (B) covers.

## A5. Open before the package head

- the per-playlist MC bytes, which give P2's limits;
- the code, tests, mutants and receipts;
- the codex-school2 read.
