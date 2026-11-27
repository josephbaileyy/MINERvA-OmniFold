# DECLARATION geanttw: does MAT-MINERvA `3e411c0d`'s GEANT truth weighting change our 2D GEANT bands? (2026-11-25)

**Lane:** `minerva-lib`, which writes the code and runs every phase.
**Under:** the director's approval in principle of 2026-11-24, given under Joseph's "yes", and the director's rulings
of 2026-11-25 on the blocking read.
**Cap:** 8.0 CPU node-h for the whole campaign; the estimate is [1.8, 3.1] (§4: P0 + P2 + P3).
**Priority:** below COVFIX, the IBUB readout and the step-2 time box.
**Status:** this is a measurement. It **adopts nothing** and changes no quoted product: not Q, not the 5D trunk
`3d7465f6…`, not LL5D's reading, and no note or paper text.

**Binding is phase by phase.** The director binds P0 alone, from this declaration and the P0 package (§8). P2–P3
get their own binding, and their own code package, after P0's records are in.

**There is no P4.** The director dropped it on 2026-11-25. Band-diag's F_src = sqrt(E/B) is built from the toys'
factors and does not respond to truth weights (`nd-unfolding/fd_1b_band_diag.py:5,442,607`), so a "not this" reading
on it would pass trivially. Any 5D test needs its own declaration, built on a truth-sensitive quantity (Part 1's rule K
or kappa, `nd-unfolding/fd_1b_precheck_fd.py`), and limitation-resolver's agreement.

## 1. The question, and what is fixed

At our pin, MAT-MINERvA `50d7631416d1c93edd4db6886a2ca29da64fee60`, `GeantHadronUniverse<T>::GetWeightRatioToCV()`
returns 1 for truth-tree events. So our `GEANT_Neutron`, `GEANT_Pion` and `GEANT_Proton` universes leave the
efficiency denominator at the CV weight. Upstream `3e411c0d3a6f598aa2072c6729790e4701e4089d` removes that early
return (`docs/orchestration/state/mat-upstream-audit-20261124/README.md` §3).

**Question.** How much does the upstream treatment change these three bands in 2D, per cell?

`docs/orchestration/state/mat-upstream-audit-20261124/2D-CLOSURE-A1.md` (merged at `638cfa9d`, PR #1304) found the
bands negligible in the quoted median and integral, but not per cell:
- in 13 of 205 cells, G's σ exceeds 0.3 of S5's total σ;
- a single cell reaches 19.5% of S5's variance;
- 6 of those 13 cells exceed 15%.

**Fixed, in every outcome:**
- every earlier record;
- Q and its digests;
- 2D-CLOSURE and its A1 addendum;
- the 1B records and gate D;
- LL5D's primary reading.

No outcome is a coverage statement, a mechanism ruling or an adoption.

## 2. Pins

| object | pin | role |
|---|---|---|
| repository | main at **M**, named by the P0 binding | this campaign's code, the manifests and the committed references |
| **event-loop source** | the canonical cluster tree `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MINERvA-101-Cross-Section`, **pinned by MP-1 S0's 46 `src_base` rows**, committed here as `code/S0-src_base.sha256` | **M alone does not pin the event-loop source.** M tracks only 10 of the tree's 46 files (of `util/` only `Binning.h` is tracked; the rest of `util/`, the systematics headers, the playlists and
  `setup.sh.in` are untracked). The build syncs the tree into B and STOPs unless `geanttw_provenance.py` passes (below). |
| MAT | `35097b65ab1680db8058f9ede18fecffdc3a1ea3`, GitHub `MinervaExpt/MAT` | identical in both builds |
| MAT-MINERvA, **pinned** | `50d7631416d1c93edd4db6886a2ca29da64fee60` | the control build |
| MAT-MINERvA, **patched** | the pinned commit plus a cherry-pick of `3e411c0d3a6f598aa2072c6729790e4701e4089d`, and nothing else | the test build |
| UnfoldUtils, GENIEXSecExtract | the production install's cmake configs, `…/opt/lib/cmake/{UnfoldUtils,GENIEXSecExtract}` | **read at configure time only, never linked.** The event loop's `CMakeLists.txt:56-60` REQUIRES both packages. The production binary NEEDs only `libMAT-MINERvA`, `libMAT` and ROOT (read 2026-11-24). C0a and C0e confirm the runtime opens. |
| production install | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt` (`libMAT-MINERvA.so` md5 `2b842b145352f58e7f42bae11da881e2`; `bin/runEventLoopOmniFold` md5 `f4f18045d74d5109dcd0f6abce9dc968`, read 2026-11-24; the build re-measures both) | **never written, never linked.** Its data trees are read through symlinks in each prefix: `lib/data`, `etc/MParamFiles` and `etc/MATFluxAndReweightFiles`. |
| AnaTuples | `2d-unfolding/playlist_manifests/<PL>_{MC,Data}.txt` at M, rows of `publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv` | size and mtime checked per file, as in RDX; content checked by C0f |
| 1L content reference | MP-1 S1's 1L zero loop, `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_1L_zero.root`, sha256 in the committed `…/fd/retention-20261110/hpss-20261111/manifests/SHA256SUMS.zero_loops` (line 8) | C0f's reference, read through an O_NOATIME copy |

**`S0-src_base.sha256`'s provenance.**
- **Source:** the 46 `src_base` rows of `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/build/MANIFEST.sha256`.
  That file's own sha256 is `fe0bc458b6bcbabcb3f589858e118e325a1c9d33de04edbdf677d06d5696f591`, recorded in the file's
  header.
- **How it was read:** with O_NOATIME, on 2026-11-25T03:22:36Z; the atime was unchanged. ⚠ That read happened after
  the cert's stated expiry, 2026-11-25T01:36:35Z, through an ssh master connection that was still open. It is disclosed
  to the director; §7 now forbids it.
- **The director's ruling (2026-11-25):** the read stands provisionally. P0's first connect under a fresh certificate
  (`deploy`) re-hashes the file with O_NOATIME and STOPs unless it is still `fe0bc458…`. `geanttw_remote.sh` pins the
  ruling's path and sha256 (`S0_PATH`, `S0_SHA`), and this file must have exactly one `# source` line naming the same
  two. A passing re-hash is recorded inside the checkout's own `.git` (`deploy/.git/geanttw-s0-rehash.txt`, which no
  porcelain check sees), and `build`, `p0` and `check` refuse without it, so a replacement checkout has none.
- **What a check on 2026-11-24 found:** the canonical tree matched all 46 rows (none differing, missing or extra), and
  M's 10 tracked files matched their rows, including `build_mp1_s0.sh:28-34`'s pins.

**The build has five checks, each recorded as a `CHECK` in `run/p0/build.log`; any FAIL stops the campaign:**
- **DIFF_EQUALS_UPSTREAM:** `git diff` from the pinned source to the patched source equals `3e411c0d`'s own diff, byte
  for byte, and touches exactly `universes/GeantHadronSystematics.cxx` and `weighters/GeantNeutronCVReweighter.h`.
  It is checked before anything compiles.
- **SOURCE_PROVENANCE:** the synced event-loop tree's files are exactly the manifest's paths, with every sha256 equal,
  and every file M tracks under the tree equals its row. It is checked before anything compiles.
- **RPATH_CLEAN:** every RPATH/RUNPATH entry of each binary is the conda ROOT env's lib or that build's own prefix lib.
- **LIBMAT_IDENTICAL and LIBMATMINERVA_DIFFER:** the two `libMAT.so` match each other, and the two
  `libMAT-MINERvA.so` differ.

## 3. The fence

- **Writes** go only to `B = /pscratch/sd/j/josephrb/geanttw-20261124/`. Inside B these are `src/`, `build-*/`,
  `prefix-{pin,pat}/`, `deploy/` and `run/`.
- **Nothing goes to CFS from jobs.**
- **Nothing is written** under the production install, any other lane's root or `minerva_large_files`.
- **Job names** in P0 are `geanttw_p0_pin_1L` and `geanttw_p0_pat_1L`, and in P2 `geanttw_p2_<PL>`. P3's job names
  are declared with the P2–P3 package, under the prefix `geanttw_p3_`. Nothing uses `rpd`, `cov2d`, `ibub` or `msr`.
  The director names `geanttw_` to every fenced lane before P0's GO.
- **sacct only, never squeue** (the standing rule, `cov2d_fence.sh:3`). Every fence reads `sacct` through
  `geanttw_sacct.py fence`, which is fail-closed: a matching job in any state not known to be terminal counts as
  live, and a malformed row refuses. The job reads its own TimeLimit with `sacct -j`.
- **Every connect:**
  - takes a fresh ack from the cov2d session and the NuE exception's ack, as arguments. Both are recorded in the
    connect's output and appended by the remote step to `run/acks.log`. `cov2d_fence.sh`'s header requires the cov2d
    ack because sacct cannot see held jobs.
  - runs cov2d's `cov2d_fence.sh` (rev 3, read from M) on a Perlmutter login node over ssh. ssh's rc is read unpiped.
  - Every `--time` is HH:MM:SS, and Slurm's TimeLimit is checked inside the job.
- **The launcher refuses** while any `^(cov2d|t2a)` job is live. It checks at start and again immediately before the
  binary. The director's `geanttw_` announcement sequences this campaign against the other fenced lanes (COVFIX,
  IBUB, RPD).

## 4. Phases, cost and readings

Every node-h figure is an **ESTIMATE** as `[low, high]`, from RDX's measured shared rate of 0.0391 node-h per hour of
wall for the same request (`nd-unfolding/rdx/rdx_cap.py`). A phase that runs over twice its high end stops and
REPRICES to the director, unless the 8.0 cap stops it first. Before every sbatch, the cap gate (`geanttw_sacct.py cap`)
refuses any job whose ceiling would take spent + held + the new job past 8.0.

### P0, feasibility and the controls: [0.02, 0.08] node-h, plus login work

Four connect steps, each on its own go: `deploy`, `build`, `p0` and `check`.

1. **`deploy`.** Clone the repository at M into `B/deploy`. STOP unless it is clean at M. Print the sha256s of every file the cluster runs: `geanttw_remote.sh`,
   `geanttw_build.sh`, `geanttw_evloop.sbatch`, `geanttw_sacct.py`, `geanttw_provenance.py`, `dumpcmp.py`, `p0_check.py`
   and `S0-src_base.sha256`. Then re-hash S0's `MANIFEST.sha256` with O_NOATIME, and STOP unless its sha256 is the
   ruling's `fe0bc458…` (§2). A Python without O_NOATIME refuses rather than reading normally.
2. **`build`.** This is login-node work, run with `nice -n 19`, and costs 0 node-h.
   - Clone MAT and MAT-MINERvA at the pins. Make the patched source by `git cherry-pick 3e411c0d`, then run the
     DIFF_EQUALS_UPSTREAM check.
   - rsync the canonical event-loop tree into `B/src/evloop` and run the SOURCE_PROVENANCE check.
   - Build MAT, MAT-MINERvA pin and pat, and `runEventLoopOmniFold` against each prefix, in the conda ROOT env
     activated as `setup_salloc_env.sh` does, without sourcing it. The build script runs under `set -u`, so nounset
     is turned off for the hook and the activation: `root_6_28`'s `activate.d` scripts read unset variables
     (`…/fd/rpd-reco/prologue-20261107/README.txt:14`, `ADDR2LINE: unbound variable`).
   - Write each prefix's own `bin/setup.sh`. It sets the production umbrella's variables for that prefix only, and
     refuses unless `MINERVA_PREFIX` names it.
   - Record the production md5s (`PROD`), the sha256 of every installed `.so` and both binaries, each binary's RPATH,
     and the five CHECKs.
3. **`p0`.** Two jobs on playlist 1L, one per build, each `--time=01:00:00`, with 2 CPUs and 16 GB on `shared`.
   - **Why 1L:** it is the 1:00 playlist with the fewest MC bytes in `ANATUPLE-SHA256.tsv`: 6 MC files of 124.9 GB
     and 15 data files of 12.4 GB. Plain 1L loops took 0:12:01 (RDX) and 0:11:16 (ibuchi). strace's overhead is
     unmeasured, which is why the limit is 1:00:00. **A P0 job that reaches its limit STOPs the campaign and
     REPRICES.**
     Search: strace (git grep outside this directory; 143 files, none times traced against untraced) @ fbf6c537eb8ba2582e078dd8aefdb554783f6015
   - **Settings:** `MNV101_DUMP_UNIVERSES=GEANT_Neutron,GEANT_Pion,GEANT_Proton`, with every other `MNV101_*` unset.
     Each binary runs under `strace -f -y -e trace=openat,open`. `-y` prints the path of each descriptor an open
     returns, which C0e needs: the binary runs in a work directory under B, so its own opens are relative.
   - **The step's order:**
     1. the LL5D atime-post (§6 (a)) must be given, well formed and already past;
     2. build.log's five CHECKs must all be PASS;
     3. the sacct fence must show no live cov2d/t2a or `geanttw_p0_` job;
     4. there must be no earlier p0 submission;
     5. the launcher's smoke must pass for **both** builds;
     6. only then is the atime-post recorded, once;
     7. then, for each build, the fence is re-read, the cap gate is passed and the job is submitted.
   - **The launcher** refuses if conda's activation does not give the ROOT env. It also refuses if `ldd` resolves any
     library under the production `opt`, or any `libMAT*` outside its own prefix (or not at all), and if the NuE
     file is missing.
4. **`check`, after both jobs end.** Copy the 1L reference with O_NOATIME, taking its sha256 from the committed
   manifest, and run `p0_check.py`. **Any control failure STOPS the campaign:**
   - **C0a, loaded library.** Each strace shows `libMAT.so` and `libMAT-MINERvA.so` opened, and every such open
     resolves under that build's own `prefix-<build>/lib`. No successful open resolves to a `.so` under the
     production `opt/lib`.
   - **C0b, the patch is active (positive control).** In the patched dump, **both** `mc_signal_reco` and
     `mc_truth_denom` carry `w_truth` and all six targets `w_truth_GEANT_{Neutron,Pion,Proton}_{0,1}`. In each of the
     two trees, every target differs from `w_truth` (bitwise) in at least one entry. Every target is finite and > 0.
   - **C0c, the patch is absent in the pinned build (negative control).** The same trees carry them, and every
     target equals `w_truth` bitwise in every entry. That is expected because MAT-MINERvA's `Model::GetWeight`
     returns `weight * univ.GetWeightRatioToCV()` (`weighters/Model.h:66` at the pin), and at the pin that ratio is
     exactly 1 for truth events. If the ratio did not enter the dumped weight, C0b and C0c would both fail.
   - **C0d, nothing else changes.** `dumpcmp.py pin pat` passes with exactly the six targets exempt, in exactly those
     two trees. `w_reco_GEANT_*` and `w_bkg_GEANT_*` are **not** exempt: they are reco-mode, so they must stay equal.
   - **C0e, reads.** Every successful open is placed by the path `strace -y` gives its descriptor, and resolved
     through symlinks. A relative open with no such path cannot be placed, and FAILs. The rest must lie either in B
     (not through a symlink out of it) or in a family fixed in `p0_check.py`:
     - the 1L manifests' AnaTuples, by exact path;
     - the production `opt/lib/data`, `opt/etc/MParamFiles/data` and `opt/etc/MATFluxAndReweightFiles` trees;
     - the conda ROOT env;
     - `/usr`, `/lib`, `/lib64`, `/etc`, `/proc`, `/sys`, `/dev`;
     - since the director's C0e ruling of 2026-11-26, three environment families, each allowed only when opened the
       way P0's jobs were seen opening it:
       - Lmod's tree under `/opt/cray/pe/lmod`, by a child process only. The binary's own PID is the log's first
         successful open, and its open of an Lmod file still FAILs.
       - seven library directories (`ENV_DIRS`: darshan 3.4.6, libfabric 2.3.1, papi 7.3.0.1, and four under the
         NVIDIA HPC SDK 26.5), as an `O_DIRECTORY` open of exactly that directory only. A regular open of the
         directory, or any open of a file or subdirectory under it, still FAILs.
       - two files by exact path: the SDK's `cuda/13.2/targets/x86_64-linux/include/cuda.h` (clang's CUDA detection
         in cling) and `/var/lib/sss/mc/passwd` (NSS's user lookup).

     Any other path FAILs and goes to the director. Tests may replace the production and conda paths only in
     smoke mode.

     **What happened at P0's check (2026-11-26).** C0e FAILED on 23 paths that the list then in force did not allow,
     and the check STOPPED. That FAIL stands as recorded: the receipts carry it with the 23 paths verbatim. The
     director ruled that the list may be widened only on evidence. `c0e-attribution/` holds the evidence: every one
     of the 23, attributed from the two jobs' own strace logs to its PID, its open flags and its build. The
     families above are exactly what that attribution showed.

     **What these logs cannot show.** The jobs traced `openat` and `open` only. So they show which process opened a
     path and with what flags, but not whether its content was read, and not which process spawned a child. The
     director's test was this: STOP if the binary itself opens any of the 23 as a regular file (not `O_DIRECTORY`),
     other than `cuda.h` and the SSSD cache. It found no case in either build. It is the strongest test these logs
     support. P2–P3's package traces `read` and `stat` as well, if that stays within its price.
   - **C0f, AnaTuple content (hash-pinned).** The reference copy's sha256 equals the committed value. Then
     `dumpcmp.py reference pin` passes: the same trees and entries, every reference branch present in the pinned dump
     and bitwise equal, and the pinned dump's extras only `w_{truth,reco,bkg}_GEANT_{Neutron,Pion,Proton}_{0,1}`. This
     is what size and mtime alone cannot show: a silent change in AnaTuple content would move the CV branches.
5. **Reading.** P0 reads only the controls and each job's measured wall and charge. It reads no physics number.
   Its measured wall sets P2's per-playlist limits at the P2–P3 binding.

**If P0 shows that any launcher, the event loop or the build needs a code change** beyond §8, the campaign stops and
that comes back to the director as a new proposal.

### P1, empty

P1 is empty: P0's two-sided control needs both builds, so the build runs inside P0, and the label is kept so the
proposal's phase numbers still hold.

### P2, the event loop: [0.4, 1.0] node-h

- **Before P2 launches, a 0-node-h C2 pre-check** compares P0's pinned 1L dump with the 1L events of the production
  2D universe dump that S5 consumed. That dump's path, sha256 and overlap check are named at the P2–P3 binding.
  - **Why it is needed:** the event-key branches (`mc_run`, `mc_subrun`, `mc_nthEvtInFile`) are booked only under
    `MNV101_DUMP_POINTCLOUD` (`runEventLoopOmniFold.cpp:461-474, 1001-1035, 1374-1393`).
  - **What it decides:** P2's key option. That is either running with the point-cloud dump for keys or joining on
    entry order. It is settled at the P2–P3 binding.
- **The run.** The patched build runs on the 12 ME-FHC playlists: 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P. Settings are
  as in P0, without strace. 1L's P0 output is reused if C0 passed.
- **Control C2.** Every branch except the six targets equals the production dump, on the declared key. **C2 gates
  P3's splice, not P2:** a C2 failure stops P3 and comes to the director, but does not void P2's record.

### P3, 2D: [1.4, 2.0] node-h

- **What is unfolded.** S5's six universe unfolds for `GEANT_{Neutron,Pion,Proton}_{0,1}`, with **M's driver**,
  S5's configuration and S5's seeds. They run twice: once on S5's pinned inputs, and once with the six
  `w_truth_GEANT_*` columns replaced by P2's, matched on the declared key, in **both** trees the driver reads them
  from: `mc_truth_denom` (the efficiency denominator, `unfold_2d_omnifold_unbinned.py:557-558`) and
  `mc_signal_reco` (`:642-643`). `w_reco_GEANT_*` is not replaced: C0d requires it unchanged. The exact command, flags and inputs are
  pinned in the P2–P3 package.
- **Miss rows (declared now; the choice is made at the P2–P3 binding).** Appended miss rows carry the CV `w_truth`
  in **every** `w_truth_*` universe column (`runEventLoopOmniFold.cpp:840-862`, the KNOWN_ISSUES #12 fix). So the
  patch's effect on misses never reaches `mc_signal_reco`. P3's reading must name one of two choices:
  - **(i) reco-matched rows only.** Then P3 **cannot measure the efficiency-denominator effect that upstream's change
    targets**, which is its main effect. The record states that in its first paragraph, not as a footnote.
  - **(ii) a bound miss override,** which carries P2's patched `mc_truth_denom` weights onto the miss rows, after
    `docs/orchestration/state/2d-closeout/stageB/diagnostics/p5/build_miss_override.py`.
- **Control C3, before any patched number is read.** C3 compares the pinned run of M's driver with S5's committed
  band matrices in `production_cov.npz` (`6689d2fc…`), band by band. There are three: `band_GEANT_Neutron`,
  `band_GEANT_Pion` and `band_GEANT_Proton`, each built by `s5_rollup.py` from the band's two universe unfolds.
  C3 builds its three the same way.
  - **Why C3 is needed:** S5 took its GEANT unfolds from the July sweep
    (`docs/orchestration/state/2d-closeout/stageC/production/s5_rollup.py:369`), whose producer revision was never
    committed (`docs/orchestration/state/2d-closeout/stageB/REPORT.md:164-166`). Stage C's S4(ii) reproduced July
    unfolds to ≤ 1.38e-11, but on 7 non-GEANT universes at seed 42
    (`docs/orchestration/state/2d-closeout/stageC/production/REPORT.md:65`). No GEANT universe has been reproduced.
  - **C3 PASS:** for each of the three GEANT band matrices, `max|C − S| / max|S|` ≤ 1e-10, where C is M's driver's
    and S is S5's. That is `s5_rollup.py`'s own metric (`rel`, `s5_rollup.py:101-102`), within an order of S4(ii)'s
    1.38e-11. It is not an element-by-element ratio: the band elements span 2.5e-93 to 8.6e-82, so a per-element
    ratio would be set by round-off in the smallest. S5's matrices are then the pinned side.
  - **C3 NOT REPRODUCED:** the pinned run completes but is beyond that tolerance. Then the pinned side is M's driver's
    own pinned run, and the record reports the size of the disagreement with S5.
  - **C3 FAIL:** the driver cannot run S5's configuration, or gives a non-finite or non-PSD band. That is a STOP, and
    it comes to the director.

**Reading R3.** It is fixed here, before any number is read. "Pinned" means the pinned side named by C3.
- **R3a.** Per cell, σ_c for each band and for their sum G, pinned against patched. Every cell is read. The 13 tail
  cells are named: those where G's σ over S5's total σ exceeds 0.3 (a ratio of σ, not variance; `2D-CLOSURE-A1.md`
  §3). They are 195, 203, 193, 1, 0, 194, 182, 183, 201, 202, 184, 196 and 192.
- **R3b.** These formulas are exact:
  - Δmedian = `median(σ_c(T′)) − median(σ_c(T))` and Δintegral = `σ_int(T′) − σ_int(T)`.
  - T is S5's total: median 6.0406%, integral 4.3284% (`recompute_results.json`). T′ = T + (G_patched − G_pinned).
    G_patched is always M's driver's. G_pinned is the pinned side C3 names. Under C3 PASS it is S5's own G, which
    M's driver reproduced within C3's tolerance, so T′ is S5's total with G replaced. Under C3 NOT REPRODUCED it is
    M's driver's own pinned G, while T still holds S5's July G. T′ is then S5's total shifted by the change M's
    driver measures, and the record says so: it is not S5's total with its G replaced.
  - Also per band and for G: `median(σ_c,patched) − median(σ_c,pinned)`.
  - The A1 formulas are used for σ_c and σ_int.
- **No χ² is read in P3.** Any like-for-like χ² on our grid must be declared by amendment before P3's binding. No
  χ² against the published result is read: its pT edges are 0.075/0.325/0.475 and ours are 0.07/0.33/0.47. That
  waits for the matched-edge products, as an amendment.
- **Caveat 1's tails.** The tail caveat of `2D-CLOSURE-A1.md` is discharged only if, in all 13 cells of R3a, the
  patched G's σ_c does not exceed the pinned G's σ_c by more than 10% relative. **The 10% is a new threshold, set
  here.** A1 states no bound. A cell whose pinned G's σ_c is 0 counts as discharged only if its patched σ_c is also
  0. Otherwise the caveat stays open, and is reported as open.
- **Caveat 2 of A1** (Q's median needs C_PL, which is on CFS and unread) stays open. R3b reads against S5's total T,
  not Q.
- **Sanity, a stop:** a patched G with σ_c 0 or non-finite in a cell where the pinned G's σ_c > 0.
- **Licenses.** R3 licenses the measured σ_c changes as values. It licenses no change to Q or to any quoted number,
  no direction claim beyond the values, and no paper text.

## 5. Controls, collected

P0's controls are C0a–C0f and the five build CHECKs. Every one of them has planted failures in §8's tests and
mutants. C2's pre-check, C2 and C3 are declared here, but their code, tests and mutants come with the P2–P3 package.

## 6. Inputs, reads and overlap

The reads were checked against each lane's **committed** input and watch sets, not by a directory walk. The source
is the overlap research at main `75c63def`, with its citations spot-checked.

| read | lane | intersection | record |
|---|---|---|---|
| the NuE constraint `MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | **cov2d (protected)** | read plainly, once per loop. `runEventLoopOmniFold.cpp:1698` sets the flag; the file is opened when the flux reweighter is constructed (MAT-MINERvA `weighters/FluxAndCVReweighter.h:32`). | cov2d's 36 protected paths, first entry (`docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux2-20261122/production-config.ready.json:8`) |
| the same file | RDX, RPD-RECO | the same read, under their exceptions | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/redump-f12i-20261112/RDX-DECLARATION.md:304-321`; `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux2-20261122/tools/fence_overlap.py:26-29` |
| AnaTuples of the 12 manifests | ibuchi, RDX | in their input sets; **neither watches AnaTuple atimes** | `docs/orchestration/state/ibu-chi2-20261123/evloop/README.md:88-92`; `RDX-DECLARATION.md:299` |
| AnaTuples by prefix (`minerva_large_files`) | MSR's `LR_EXTRA` (`nd-unfolding/msr/msr_overlap.py:38-42`; the RPD flux2 entry at `:40`), which IBUB's overlap list aggregates along with cov2d, rpd, IBUCHI and LR_P0 (`2d-unfolding/ibub/ibub_overlap.py:78-85`) | listed; no atime watch | those lines |
| `opt/lib/data/flux` | ibuchi | in its input set; its atimes already moved on 2026-11-23 | `docs/orchestration/state/ibu-chi2-20261123/evloop/results/README.md:94-96` |
| `opt/lib` and `opt/etc/MParamFiles/data`, apart from the NuE file | RPD-RECO | staged originals, not on cov2d's list | `fence_overlap.py:12,33-36` |
| `opt/etc/MATFluxAndReweightFiles`, and the production cmake configs of UnfoldUtils and GENIEXSecExtract | none found | not on cov2d's list | the 36 paths above |
| AnaTuple atimes | the MC AnaTuple retention stat (`docs/orchestration/state/measurement-paper/5d-community-20261024/fd/anatuple-mc-stat-20261124/`) | **a measurement, not a watch.** Our reads move the atimes later, so the purge exposure it reports next moves later. | its README |
| MP-1 S0's `MANIFEST.sha256` (read once, 2026-11-25) and MP-1 S1's 1L zero loop (read at P0's `check`) | the HPSS retention record of the zero loops | both read with **O_NOATIME**, as RDX read MP-1's inputs | `…/fd/retention-20261110/hpss-20261111/manifests/SHA256SUMS.zero_loops` |
| **P3:** the production 2D universe dump `2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root` | **cov2d (protected)** | read at P3 only. Disclosed now; the read is staged (O_NOATIME) and fenced in the P2–P3 package. | `production-config.ready.json:14` |
| IBUB's inputs (`xr-input/runEventLoopOmniFold_MEFHC.root` and the rest), `cov2d-run-20261104`, `cov2d-2a`, `ibuchi-evloop-20261123`, `rdx-20261112b`, tier3-design's msr and t3p roots | IBUB, cov2d, ibuchi, RDX, tier3-design | **not read by P0 or P2** | the inputs above |

**The NuE exception is REQUESTED.** It is not assumed. There is no P0 GO until the director's ruling and cov2d's
no-objection are both on record.

**The precedent.** RDX's exception was granted on 2026-11-12, "with cov2d's no-objection"
(`fd/redump-f12i-20261112/RDX-BINDING-1.md:146`). The binding lists its terms at `RDX-BINDING-1.md:146-152`:
- the job-start and pre-binary fence checks;
- the connect's fence check;
- the announcement;
- the per-job atime and mtime log in ns, with UTC;
- cov2d's condition (a).

**The conditions requested.** These are cov2d's conditions, quoted verbatim from
`fd/redump-f12i-20261112/RDX-DECLARATION.md`. Each is followed by how it applies here, where the job prefix
`rdx_` → `geanttw_` is the only change.

- **(a)** — `RDX-DECLARATION.md:315-317`; in the binding at `RDX-BINDING-1.md:152`.
  > "The first `rdx_` job starts only after cov2d has taken the LL5D gates' atime-post. Step s1 takes that UTC
  > time, as the director passes it on, refuses unless it is given and already past, and records it in
  > `gates/ll5d_atime_post.txt`. Step s2 requires that record. squeue alone is never relied on."

  *Here:* the first `geanttw_` job starts only after that atime-post. P0's `p0` step takes the UTC time as the
  director passes it on, and refuses unless it is given and already past. It records the time in
  `run/gates/ll5d_atime_post.txt`, after its other checks pass. P2's step requires that record.
- **(b)** — `RDX-DECLARATION.md:318-319`. RDX-BINDING-1's term list does not restate it, and the declaration gives it
  as enforced on cov2d's side.
  > "cov2d's atime-snapshot connects refuse while an `rdx_` job is queued or running. That is enforced on cov2d's
  > side."

  *Here:* the same, for `geanttw_` jobs. It is enforced on cov2d's side once the director's announcement names
  `geanttw_`.
- **(c)** — `RDX-DECLARATION.md:320-321`; in the binding at `RDX-BINDING-1.md:151`.
  > "Each event-loop job logs the NuE file's `atime_ns` and `mtime_ns`, with the UTC time, before and after its
  > run. The logs go into the receipt."

  *Here:* the same, for each `geanttw_` event-loop job.

**The other binding terms** (`RDX-BINDING-1.md:148-150`) also apply here:
- the job's fence check at start and immediately before the binary (§3);
- the connect's fence check before each submit (§3);
- the director's announcement of `geanttw_` to the fenced lanes.

## 7. Terminal conditions

The campaign STOPS on any of the following:
- any failure of C0a–C0f, of a build CHECK, or of C3 (C3 FAIL; C3 NOT REPRODUCED is §4's declared fallback). A
  C2 failure stops P3 only (§4 P2).
- a P0 job reaching its time limit;
- the 8.0 node-h cap (the cap gate refuses before any sbatch that would pass it);
- a phase over twice the high end of its estimate, which goes to REPRICE;
- any script exiting nonzero. In P3 this includes a NaN or Inf in an unfolded result or band matrix, a band matrix
  that is not positive semi-definite (minimum eigenvalue < −1e-12 × maximum), and §4's sanity stop;
- a needed code change outside §8;
- **no valid NERSC certificate.** A connect runs only on a certificate Joseph has renewed for it. An ssh master
  connection that is still open after the certificate expires is **not** a valid certificate (see §2's disclosure).
  The connect's ssh never uses a master or a jump client (`-o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none`),
  so each call authenticates afresh and fails rather than prompting. Calls may land on different login nodes; every
  step keeps its state on `/pscratch`. Only the tests can replace that command: the connect refuses
  `GEANTTW_SSH` outside them.
- **The tests' door is not a guard.** Both scripts honour test-only variables (`GEANTTW_TEST_B`, `GEANTTW_SSH` and
  the rest) that redirect paths and the ssh command. Setting them for a real connect is a deliberate bypass the code
  cannot prevent, and it is forbidden: a connect runs with none of them set. Likewise, the S0 record is written
  into the checkout that `deploy` verified; someone swapping `deploy/` by hand while `deploy` runs could misplace it.
  That too is a deliberate act, and `deploy/` is touched only by `geanttw_remote.sh`.
- a director's stop.

**Records.** Each phase ends in a `[receipt]` PR. Each holds scripts and committed outputs, sha256s, the measured
charge, the acks, and the readings exactly as §4 licenses them.

## 8. The P0 package (in this PR before P0's binding)

All files are in `code/`. Every step that runs is the committed bytes at M.

| file | role |
|---|---|
| `geanttw_connect.sh` | the Mac side: `connect STEP M COV2D_ACK NUE_ACK [ARG]`, with STEP one of `deploy`, `build`, `p0`, `check`. It requires both acks, as tokens, and prints them. It reads `cov2d_fence.sh` rev 3 and `geanttw_remote.sh` with `git show M:…`, never from the working tree. It runs the fence on the login node and STOPs on any nonzero rc. Then it either streams `geanttw_remote.sh` (`deploy`) or first checks that the deploy's copy has the sha256 of M's blob. Its ssh opens a fresh connection every time (§7). |
| `geanttw_remote.sh` | the login-node steps of §4 P0. It refuses off a login node or inside a Slurm job, and appends every step's acks to `run/acks.log`. `build`, `p0` and `check` STOP unless the deploy is clean at M. `deploy` STOPs unless S0's `MANIFEST.sha256` re-hashes (O_NOATIME) to the ruling's sha256; the other three steps STOP unless that re-hash is recorded. Every O_NOATIME read refuses on a Python without the flag. |
| `geanttw_sacct.py` | `fence`, fail-closed on sacct rows, and `cap`, the 8.0 node-h gate at 0.0391 node-h/h, counting sacct's spent and held jobs plus the unlisted submissions. Python 3.6. |
| `geanttw_build.sh` | the login-node build and its five CHECKs (§2). It writes each prefix's `setup.sh` and the three data symlinks. Pin, canonical-source and production-opt overrides exist only for the tests (`GEANTTW_SMOKE_B`). |
| `geanttw_provenance.py` and `S0-src_base.sha256` | SOURCE_PROVENANCE: the synced tree against MP-1 S0's committed 46 rows, plus M's tracked files. Python 3.6. |
| `geanttw_evloop.sbatch` | the job: its name, its TimeLimit from sacct, the sacct fence (twice), the binary's md5, the manifests against M, each AnaTuple's size and mtime, the conda activation, `ldd`, the NuE file, and `MNV101_*`. **Smoke mode runs every one of these, with two
exceptions:** outside Slurm it takes its TimeLimit from the caller (`GEANTTW_TIMELIMIT`, set to the job's `--time`
by `geanttw_remote.sh`), not from `sacct -j`, and it stops before the second fence check, which belongs with the
binary. It logs the NuE atime/mtime before and after, runs strace in P0, and writes the output via `.partial` with mode 0440. Its build variable is `GBUILD`, not `BUILD`: the ROOT env's conda activation exports `BUILD`, which overwrote RDX's (`fd/redump-f12i-20261112/RDX-BINDING-1.md:189-190`). |
| `dumpcmp.py` | bitwise, branch-by-branch, entry-by-entry comparison of two dumps, at each tree's highest cycle. It takes an exempt regex (C0d) and an allowed-extras regex (C0f). No key join: C2's comes with the P2 package. |
| `p0_check.py` | C0a–C0f and build.log's CHECKs, with the allowed read families fixed in code. C0e's three environment families (§4, C0e) are judged on each open's PID and flags, read from the same strace lines. |
| `../c0e-attribution/` | not run on the cluster. The C0e FAIL's record (`check.txt`), and the attribution of its 23 paths, which C0e's environment families rest on: `attribute.py`, `attribution.json` and a README with the fetched logs' sha256s. |
| `tests/` | pytest. The Python half uses synthetic ROOT fixtures (uproot) and strace logs in `-f` formats. The shell half uses stubbed `sacct`/`sbatch`/`ssh`/`conda`/`ldd`/`strace`/`readelf`/`cmake`/`make` (a stub `squeue` fails if called) and local git repositories. The full run paths are executed, not grepped. Which refusals no test notices is `mutation.txt`'s to say, not this table's. Tests added for mutants the earlier runs left alive assert the refusal's own message or, where a refusal prints none, its exit code and that the step after it did not run; in the launcher (`only_refusal`) also that it is the only REFUSE, since a guard whose `exit` is removed still prints its message. |
| `mutation.py` → `mutation.txt` | single-site planted mutants. In the Python modules these are operator, keyword and verdict-literal tokens, found by Python's tokenizer, so string text is never mutated. In the shell scripts they are each refusal's `exit` or `bail`/`stop` call (after `||`, `&&` or a `case` label), and each `==`, `!=`, `-eq` and `-ne` on a refusal, `CHECK` or `[[` line. `=~`, `<`, `>` and the unary tests are not mutated. Each mutant runs its owner's test file in a scratch copy. A mutant whose tests time out is counted as not killed. |
| `linetrace.py` → `linetrace.txt` | line trace under the tests: coverage.py for Python, including the tests' `python3 -I` subprocesses; a DEBUG-trap trace for the shell scripts (bash 3.2 has no `BASH_XTRACEFD`). Inside a command substitution that continues over `\` lines, bash 3.2 reports the command's last line, so a hit on a continuation line counts for the line its command starts on. It lists every executable line no test reaches. |

Before the first contact, the launcher's smoke mode runs locally, as a stand-in, against a fake B (the tests above).
