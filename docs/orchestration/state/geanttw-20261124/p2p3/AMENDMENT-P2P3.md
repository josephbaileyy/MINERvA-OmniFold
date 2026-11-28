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
  - The extra cost of the read trace is **at most 0.027 node-h at the limit**: 1B's 00:42:00 at 0.0391 node-h/h.
    An earlier "[0.05, 0.15] node-h" estimate could never be reached at that limit. The director replaced it on
    2026-11-27 with the ratio bound below.
  - The pilot playlist is **1B** only. The job names, the cap gate's family and the event-loop job all refuse a
    pilot on any other playlist.
  - **The pilot gate** (`geanttw_sacct.py pilot`, run by `p2run` before any other playlist is submitted):
    - both pilots, by the ids their SUBMIT lines name, are COMPLETED in sacct;
    - ElapsedRaw(pilot) / ElapsedRaw(pilotref) ≤ 3, the factor P2's limits already assume (the director's ruling,
      2026-11-27). The measured extra cost is recorded too.
    Otherwise `p2run` STOPs to the director. Either way it writes `run/p2p3/pilot.json`.
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
  - (c) each job logs atime_ns and mtime_ns, with UTC, immediately before and after the binary. Under cov2d's (C)
    amendment 3, this is fail-closed and covers UOMNI too. The event-loop job stamps the NuE file and UOMNI by stat,
    with `ino=` showing which file the prefix's symlinked path reached (`geanttw_build.sh:140`). It refuses before
    the binary if a stamp cannot be taken, and exits 20 if the after-stamps cannot be written. The fence's scratch
    file is made under `B/run`;
  - the fence runs at start and before the binary.

## A3. P3: three slim omnifiles and the unchanged driver

**The driver** is `2d-unfolding/unfold_2d_omnifold_unbinned.py` at sha256 `74a4ed69…`, which is Stage C's
`PROD_SHA` (`stageC/production/sbatch_prod.sh:23`). It is byte-identical on main since `c53e9c36`. It runs with
Stage C's universe argv (`sbatch_prod.sh:83-84, 116`):

    --omnifile SLIM --flux-universe-file FLUXU --verbose --mcfile MCFILE --iters 5 --use-weights
    --estimator lgbm --bkg-mode purity --out OUT --universe GEANT_<b>:<i> --seed 42 --branch-select derived

The pinned inputs are MCFILE `d40aea69…` and helper `e9623412…`. Both MCFILE and FLUXU are under `baseline_flux`,
cov2d's protected entry 6, and cov2d's (C) amendment 3 sets the terms for them:
- **MCFILE** is read in place, plainly, by the driver in each of the 18 unfolds. It is hashed exactly once, by the
  slim job, which records its sha256, size and mtime in `run/p3/slim.json`. Each unfold STOPs before the driver
  unless MCFILE's size and mtime_ns are that record's.
- **FLUXU** (`flux_integral_universes_MEFHC.root`) is in the argv only, as in Stage C. No geanttw step reads or
  hashes it. In the driver, the guard `if universe_branch is not None and universe_branch[0] == "Flux":` is at
  `unfold_2d_omnifold_unbinned.py:1709`. Inside it, `:1710-1711` call `load_flux_universe_bins` (`:148`), the
  only function that opens the file, and `:1715` only builds a string. Outside that branch, the path appears only
  as a string in the output's `runConfig` metadata (`:1340`). So a GEANT universe never opens the file.
- Each unfold logs the atime_ns and mtime_ns of UOMNI, the NuE file, MCFILE and FLUXU, by stat, before and after
  the driver. It exits 21, a deviation to report to cov2d, if FLUXU's atime or mtime moves or MCFILE's mtime moves.
  MCFILE's atime is not checked, because the grant allows the driver's plain read of it, and that read can move it.
  cov2d confirmed this reading of condition 1-a on 2026-11-27 (22:26:12Z, verbatim in `cov2d-grant-C-20261127.md`).

**The seed.** S5's July GEANT unfolds (`sweeps.json` `15b57de9…`, `pn/GEANT_*`) record no seed. Seed 42 comes from
S4(ii)'s "July identity at seed 42" (`stageC/production/REPORT.md:65`). C3 tests it.

**The slims, under the director's terms.**
1. **C3 gates the slim approach.** C3 runs on the six pinned-slim unfolds. It PASSes only if both of these hold,
   each at rel = max|a − b| / max|b| ≤ 1e-10:
   - each pinned universe vector equals S5's own July unfold of that universe (`sweeps.json` `pn/GEANT_*`, under
     `2d-unfolding/uq/`, not a protected path). `sweeps.json` and each July file are sha-checked through O_NOATIME.
     Their histograms are then read by S5's own `Cells` through ROOT, a plain read, as for every `xsec.root`.
   - each band's `build_repair.wcov` over the pinned pair equals `production_cov.npz`'s `band_GEANT_<b>`.
   A band covariance cannot see a common shift or a swapped pair, so the per-universe comparison is required too.
   Anything else is a STOP before any patched run, and the slim is never adjusted to make C3 pass. On PASS, `c3.json`
   records the sha256 of each pinned `xsec.root`. Each override unfold and `extract all`, in both
   `geanttw_remote.sh` and the job itself, refuses unless `c3.json` is PASS and those six outputs still hash to
   it. A missing file or a missing recorded hash never matches. R3 refuses unless the extracted vectors' six pinned
   outputs are the ones C3 recorded. R3 has no "not reproduced" path, and it STOPs on any override band that is not
   finite and PSD.
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

   No test runs the driver on a slim. A slim missing a selected branch is caught twice. C1-a and `verify` require
   each tree's branch set to be exactly the 37, and the driver itself refuses a selected branch with no address
   (`:960-972`). The lateral names the driver probes for these universes (`_universe_kine_branches`) are checked
   absent in UOMNI (C1-a) and in every slim (`verify`). The top-level `pTmu_fiducial_nucleons` is checked absent
   in UOMNI (C1-a), and each slim's top-level key set must be exactly the four trees and four TParameters.
3. **Location and lifetime.** The slims are exactly `/pscratch/sd/j/josephrb/geanttw-20261124/p3/slim-pinned.root`,
   `slim-pinned-override.root` and `slim-patched.root` (cov2d's (C) amendment 3), never on CFS or HPSS. They are
   deleted by literal path once P3's receipts are accepted, unless Joseph says to keep them.
4. **Price, an ESTIMATE until the branch sizes are read.**
   - The slims hold 37 branches out of UOMNI's 952, plus the four TParameters. **C4 measured** those branches at
     5,857,242,672 B compressed and 6,458,621,231 B uncompressed, so a slim is about 5.9 GB, and two are about 12 GB.
   - **One open, one pass** (cov2d's (C) amendment 3, (2)). In the slim job, `geanttw_p3_slim`, only
     `p3_slim.py build` opens UOMNI, once. In that open it runs C1-a on the headers and records each TParameter's
     class and value and each slim branch's typename. It then walks UOMNI once, playlist block by playlist block in
     hadd order. It reads the 37 + 2 granted branches (about 5.86 GB compressed, plus 2 × about
     250 MB of key branches) and the 12 dumps in step. From memory, it runs the full C2, the tail checks and both
     overrides, and writes the three slims, about 18 GB in all. Every UOMNI read goes through one function that
     refuses a branch outside the 37 + 2 (condition 2-a). That list is written out in `p3_slim.py`, not derived
     from the slim list. The job records the branches it read and fails unless they are exactly those 39.
   - **Read-back without re-reading UOMNI.** The build records the sha256 of every array it writes, per slim, tree,
     branch and playlist block. `slim_tparams.py` writes each slim's TParameters from build's record, with
     UOMNI's class and value, and never opens UOMNI. `verify` reads each slim back, never UOMNI, and recomputes
     those digests. Against build's record, it also checks the key set, each TParameter's class and value, the
     branch sets, the typenames, the entry counts and the absent lateral probes. Only on success does it write `run/p3/slim.json`
     (PASS, each slim's sha256 and size, MCFILE's sha256, size and mtime). No unfold runs without that file.
   - **Memory.** Each block is held whole, so the job is sized from the largest, 1M's 5,917,406 signal rows. It
     asks for 2 CPUs and 32G and refuses before reading if any C4 block exceeds 6,500,000 rows. The 32G request is
     twice the 16G one, so the cap gate charges it 0.0782 node-h/h (twice 0.0391). Its limit is 02:00:00, a
     ceiling of 0.16 node-h. The wall is an ESTIMATE of 0:30–1:30 until measured.
   - The unfolds are 6 universes × 3 slims = 18 jobs, `geanttw_p3_unf_<slim>_GEANT_<b>_<i>`, at Stage C's request
     (128 CPUs, 243840M, shared, billed at 0.5 node-h/h) and Stage C's 00:30:00 limit. At the limits that is
     **4.5 node-h, a ceiling**. **This exceeds the declaration's P3 estimate of [1.4, 2.0] node-h.** There are two
     reasons. The director's D2 ruling (a) adds a third slim, so there are 18 unfolds where the declaration counted 12.
     And the figure is a ceiling, at Stage C's 00:30:00 limit for every unfold, not an estimate from measured walls. From the code's own rates and
     limits, the P2–P3 ceiling is 5.93 node-h:
     - P2's 10 playlists at their limits, 1.16;
     - the pilot pair, 0.05;
     - the C2 pre-check, 0.02;
     - the slim job, 0.16;
     - the two extracts, 0.04;
     - the 18 unfolds, 4.5.
     With P0's spent 0.0086 (`../receipts-p0/README.md:58`), the campaign's ceiling is about 5.94 node-h. That is inside the 8.0 cap that
     `geanttw_sacct.py cap` enforces. The patched and pinned+override unfolds run only after
     C3 PASSes on the pinned ones.
5. **The patched slim** is UOMNI's columns with only the six `w_truth_GEANT_*` columns replaced, in `mc_signal_reco`
   and `mc_truth_denom`, by P2's values in hadd order, with the misses then overridden (D2). **Control C-PATCH:**
   every other branch is UOMNI's array as read, written once to each slim. The per-block digests show it read back
   unchanged in all three slims. The keys and TParameters are checked as for C-SLIM.
6. **cov2d's (C)** is asked fresh, on exactly these terms:
   - an in-place, plain ROOT read of UOMNI's branches listed above;
   - a slim copy of that protected content, written to geanttw's root;
   - P0/P2's per-job atime log;
   - the `^(cov2d|t2a|covfix_)` fences.

   It also discloses the per-playlist header reads (A1) and the C2 pre-check's read of 1L's rows. The grant text
   goes in the package.

**D2: the miss rows, and three slims (the director's ruling (a), 2026-11-27).**
- **Why three slims.** The miss rows of `mc_signal_reco` carry the CV `w_truth` in every universe column, as a
  proxy (`runEventLoopOmniFold.cpp:862-863`). An override replaces that proxy with the truth rows' denominator
  weights. On the patched slim alone, that would mix the patch's effect on misses with the proxy's removal. So P3
  builds three slims, all under `/pscratch/sd/j/josephrb/geanttw-20261124/p3/`:
  - `slim-pinned.root`: UOMNI's columns. C3 runs on this one.
  - `slim-pinned-override.root`: UOMNI's columns, with each playlist's misses overridden from UOMNI's own
    `mc_truth_denom` `w_truth_GEANT_*`.
  - `slim-patched.root`: P2's columns, with the misses overridden from P2's `mc_truth_denom`.
- **The matching.** Misses are matched to truth rows by the exact key (MC, MC_pz, w_truth), as an ordered
  subsequence per playlist (`p3_slim.py override_block`, after `build_miss_override.py`).
  - For the pinned override, UOMNI's `w_truth` in both trees is read for the key only, under cov2d's (C)
    amendment 2. It is written into no slim.
  - Each playlist's block sizes are C4's per-playlist counts (`c4/c4.out`). Each dump must have exactly those, and
    their sums must be UOMNI's entries. Each playlist's miss count is its dump's `nTruthOnlyMisses`. The counts must
    sum to UOMNI's `nTruthOnlyMisses`, and `hasTruthOnlyMisses` must agree.
  - **The tail check**, on UOMNI's block and on the dump's (`build_miss_override.py:94-100`): the block's last
    n_miss signal rows have `sim_pass` 0, `sim` −9999, and every `w_truth_GEANT_*` equal to `w_truth`, the CV
    proxy. The row before them must not have `sim` −9999, so n_miss is the whole run of misses. This assumes
    that no reco-matched row carries the −9999 sentinel. If one does, the build STOPs on the cluster. The pinned
    override therefore uses UOMNI's own blocks, with the miss counts checked against UOMNI's rows.
- **Control C-MISS, exact, on both overrides.** Per playlist and universe, the multiset of
  (MC, MC_pz, w_truth, w_truth_<u>) over the overridden signal rows equals the denominator's. Any per-bin sum taken in exact arithmetic (fsum) then
  agrees bitwise, in any order.

**R3, re-read for three slims** (the director's ruling; the declaration's R3 compares "patched" with "pinned"):
- **The patch's effect** is G(patched+override) − G(pinned+override). In R3a and R3b, "patched" and "pinned" now
  mean those two. T′ = T + [G(patched+override) − G(pinned+override)].
- **The proxy's removal alone** is G(pinned+override) − G(pinned). It is reported separately, per cell, with the
  same formulas.
- **C3** runs on the plain pinned slim, against S5's July unfolds and band matrices (A3, term 1), and gates the
  slim approach.
- **The record answers "which convention, and why"** (the director's note of 2026-11-27, from App. A's review). The
  pinned toolkit's GEANT hadron universes return 1 for truth-tree events, so they leave the efficiency denominator at
  CV. Upstream's `3e411c0d` reweights the denominator too.
  - The record cites upstream's own reason. That is the commit's message, "Turn truth weighting on for Geant Hadron
    weights and systematics." (author David Last, 2025-10-17; quoted by the build's cherry-pick echo,
    `../receipts-p0/connects/p0-build.out`), and any linked MAT-MINERvA issue, which the record names or says it
    did not find.
  - It states the measured effect on V^(2D)'s three GEANT band matrices, on the total covariance (T to T′) and on
    the 13 tail cells.
  - It says what the 2021 paper's toolkit version did only from a cited source. Otherwise it reports that as not
    established.

**A declared deviation in C2.** The declaration's C2 compares "every branch except the six targets" with the
production dump. **This package does not.** The reason is cov2d's (C) grant, which allows UOMNI to be read for the
slim's branches only, plus the two w_truth key branches. So:
- the pre-check compares all 37 slim branches, targets included, of P0's pinned 1L dump with UOMNI's 1L slice. Each of
  the dump's trees must first have exactly C4's 1L count, so the read is exactly the granted slice;
- the full C2 compares the 25 non-target slim branches of P2's 12 patched dumps, in hadd order, with UOMNI. It runs
  inside the slim job's one pass, from memory, before any slim is written. A difference writes `run/p3/c2.json`
  FAIL and stops the job. There is no separate C2 job.

C2's purpose is that P3 sees the same events, in the same order, on every branch it reads. The 25 branches,
kinematics included, are every branch P3 reads, so the purpose still holds. The director accepted this deviation on
2026-11-27.

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

## A5. The P2–P3 package

All files are in `../code/`. Every step that runs is the committed bytes at the binding's M.

| file | role |
|---|---|
| `geanttw_remote.sh` | P2–P3's login-node steps, each on its own GO and a fresh cov2d ack:<br>• `c2pre`, then `p2pilot` (the 1B pair), then `p2run` (the other 10 playlists)<br>• `p3slim`, after every P2 output and with no P2 job live<br>• `p3unf pin`, which needs `slim.json` PASS, then `p3extract pin`, which writes `run/p3/c3.json`<br>• `p3unf rest`, which needs `c3.json` PASS, then `p3extract all`, which needs it too<br>`p2run` first runs the pilot gate (A2).<br>Each step runs `ready`, the ack, the fence and `p2_limits.py --check`. `submit()` refuses a name already submitted, re-fences, passes the cap gate, runs sbatch and logs one SUBMIT line. |
| `geanttw_connect.sh` | the Mac side, as for P0, with the new step names |
| `geanttw_evloop.sbatch` | P2's event loop: the trace modes (A2), the launch with `BASH_ENV` and `ENV` unset, and the `^(cov2d|t2a|covfix_)` fence |
| `geanttw_p3.sbatch` | the C2 pre-check and the P3 jobs: `c2pre`, `slim`, `unf` and `extract pin|all`. Each checks its name and limit, runs the fence at start and before the work (its scratch file under B), and checks the deploy's scripts against their committed blobs. Every mode stamps UOMNI and the NuE file before and after, plus MCFILE in `slim` and MCFILE and FLUXU in `unf`, and stops if a stamp cannot be written. `c2pre` and `slim` size-check UOMNI by stat. `unf` runs Stage C's universe argv after the slim.json and C3 checks (A3), with the driver, helper and `setup_salloc_env.sh` hashed. Each sourcing of the ROOT setup resets `TMPDIR` to `B/run/tmp`, because `setup_salloc_env.sh:24` points it outside B. |
| `geanttw_sacct.py` | the fence; the cap gate, charging each job the larger of its family's rate and its sacct AllocTRES billing / 256 (the director's ruling), with both totals reported; the pilot gate (A2); and `completed`, which every step uses to require its predecessor jobs COMPLETED in sacct, so an output left by a job that exited nonzero is never consumed. This includes P0's two jobs, read from P0's own submissions.log: `c2pre` needs `geanttw_p0_pin_1L` COMPLETED and `p3slim` needs `geanttw_p0_pat_1L` and `geanttw_p2_c2pre` COMPLETED. The sacct snapshot covers the last 14 days, so a P0 job run on 2026-11-26 drops out after 2026-12-10, and those steps then stop rather than pass |
| `p2_limits.py` → `p2_limits.txt` | P2's per-playlist limits (A2) |
| `c2_check.py` | C2's pre-check, bitwise, on entry order; and the slim lists and `same_bits` the full C2 uses (A3) |
| `p3_slim.py`, `slim_tparams.py` | `build`, UOMNI's one open (C1-a, the metadata record, the one pass: C2, the tail checks, C-MISS, the three slims and their digests); `slim_tparams.py` from the record; `verify` from the record and the slims (C-SLIM, C-PATCH, `slim.json`) (A3, D2) |
| `p3_readout.py` | `extract` (S5's own `Cells`; with `pin`, also S5's July unfolds), `c3` and `r3` (A3, R3) |
| `tests/` | `test_p2_limits.py`, `test_c2_check.py`, `test_p3_slim.py`, `test_p3_readout.py`, `test_p3_sbatch.py` and `test_p2p3_steps.py`, plus the P2 and family tests added to `test_shell_scripts.py` and `test_provenance_sacct.py` |
| `mutation.py` → `mutation.txt`, `linetrace.py` → `linetrace.txt` | P0's receipts discipline, now covering every P2–P3 file |

**Not run, and not to be:** nothing here runs before GEANTTW-BINDING-P2P3 and a GO for each step. Every UOMNI read
is through an O_NOATIME file object, the stricter method cov2d's (C) amendment 2 allows. There are two: the C2
pre-check's 1L slice, and the slim build's one open. The slim job stamps UOMNI, the NuE file and MCFILE before and
after its whole run. The driver reads only the slims, never UOMNI.

**Rates.** SHARED_RATE 0.0391 is 10/256. P0's two jobs had AllocCPUS 10 for a 2-CPU request, so the declaration's
rate already charges the allocated CPUs.

**The readout's own bindings.** `extract` records the sha256 of its npz in the sidecar. `c3` and `r3` refuse an npz
that is not the one its sidecar names. `extract` refuses any override slim unless `--c3` names a PASSing c3.json
whose six pinned hashes are the live outputs'. R3 also STOPs on a negative variance in T′.

## A6. Open before the package head

- the full receipts run (`linetrace.txt`, `mutation.txt`) on the frozen code, and `SHA256SUMS-P2P3`;
- the codex-school2 read.
