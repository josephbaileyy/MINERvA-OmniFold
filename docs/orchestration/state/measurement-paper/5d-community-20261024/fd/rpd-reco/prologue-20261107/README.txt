RPD-RECO data-free prologue, 2026-11-07 (the director's go, under coverage-5b-audit's run clearance): Codex2's
fd_rpd_reco_prologue_connect.sh + fd_rpd_reco_prologue.py at #848's head 4ea4a113f72f32465f2a8c4eddd7bbaa2db5683c, run
by limitation-resolver on login27 at 0 node-h.

RESULT: STOP before the prologue ran. The wrapper sources the pinned MAT setup under its own "set -euo pipefail", and
the source failed on an unbound variable inside root_6_28's conda activation script. The wrapper exited 1 there.
- No trace was taken, and no policy was built.
- There is no trace-policy.json, prologue.strace, data-free-trace.json, prologue-prepare.json or worker record to
  commit: the run directory was never created.
- Reported unrepaired. Nothing was patched or rerun.

THE QUOTED LINES (connect.out), in order, after the wrapper started:
  {"mat_setup_scripts": 6, "mismatches": 0}
  /global/homes/j/josephrb/.conda/envs/root_6_28/etc/conda/activate.d/activate-binutils_linux-64.sh: line 68: ADDR2LINE: unbound variable
  prologue wrapper rc=1
- check-mat-setup passed, then `source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh` stopped under
  set -u.
- The wrapper's next commands (export TMPDIR="$RUN/tmp"; mkdir -p "$TMPDIR") never ran: the run directory does not
  exist ("find: ... /run: No such file or directory").
- The same setup sourced without set -u, in the real-class check of 2026-11-06 (real-mnv-check-20261106/connect.out),
  returned 0. That is a fact about that connect only. Which wrapper change is right is Codex2's.

THE COMMAND (rpd_prologue_login.sh, sha256 3cbffe30..., compared on the node before it ran):
  bash $CK/nd-unfolding/fd_rpd_reco_prologue_connect.sh $CK $CK/../policy-config.json \
    3992108792db2bc7c26b570531efec2df739a392398c03af366b82eb9190fa4b /dev/shm/limres-rpd-prologue-20261107/run \
    /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
  with CK = /dev/shm/limres-rpd-prologue-20261107/repo, a fresh https clone at 4ea4a113 (HEAD equal, porcelain 0).
  The blobs are in connect.out: the wrapper 509e04bf, prologue.py 58f3666d, fd_rpd_reco.py 487084bc, custody
  837704db, fd_rpd_inputs.py 7c2e018f. MAT_PYTHON is root_6_28's python3, the interpreter
  receipts-rpd/root_tests_login.log measured in the pinned MAT environment.

BEFORE IT, IN THE SAME CONNECT:
- The COV2D fence, immediately before: squeue rc 0, no cov2d-* row (02:17:54Z). It was also clear from the Mac at
  02:15Z (fence-mac.out). The two cov2d-AR23 jobs of 11-06 had ended.
- The resolved policy config (policy-config.json, sha256 3992108792db..., written from the script and checked on the
  node). It is production-config.draft.json at 4ea4a113, with every policy path resolved. Physics and source fields
  stay DRAFT as the PR allows, and only flux_extract / flux_custody keep ${EXTRACT_RUN}, which the prologue does not
  read.
  - dump_root: /pscratch/sd/j/josephrb/fd-rpd-20261103/dumps. This is the only directory INPUTS.sha256 @ 4ea4a113
    names (24 files).
  - pins, h2, inventory, constants, mat_dependencies: their repository paths under the clone.
  - flux_root: /pscratch/sd/j/josephrb/minerva/minerva_large_files. $PLOTUTILSROOT/data, i.e.
    MINERvA101/opt/lib/data, is a symlink to that root's MATFluxAndReweightFiles, which flux_selection's
    relative_path names (stat_probe.out). The root also holds MParamFiles, which MINERvA101/opt/etc/MParamFiles
    links to, so both MAT data trees are protected.
  - flux_source: /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT/PlotUtils/FluxReweighter.cxx, the pinned
    checkout's source (sha256 4576346d..., timing-20261106/README.txt). It is metadata only and is not opened.
  - trace_environment_roots: /global/homes/j/josephrb/.conda/envs/root_6_28 and its realpath
    /global/u2/j/josephrb/.conda/envs/root_6_28. ROOTSYS is that environment (real-mnv-check-20261106).
  - trace_instrument_directories: MINERvA101/opt/lib and MINERvA101/opt/include of the pinned checkout.
  - cov2d_protected_paths, from this run lane's COV2D input list (the 303 inputs the REF-C2C1 connects watched),
    widened to directories where that is stricter:
    - the flux constraint sorted_NuEConstraint_FHC_RHC_IMD.txt;
    - .../2d-closeout-re2-20261023/partb/out/ER/xsec.root;
    - the directory .../2d-closeout-re2-20261023/partb/out, which holds ER and the 300 S1_*/xsec.root;
    - the publication covariance cov_ptpl_minerva_inclusive_6GeV.root;
    - COV2D's own run directory /pscratch/sd/j/josephrb/cov2d-run-20261104.
  Every path was confirmed by a stat-only probe (stat_probe.sh / .out, login04, 02:13Z), which read no file content.
- The strace probe: strace -f -e trace=open,openat,openat2 /bin/true, rc 0, 30 lines.

CLEANUP: cleanup.sh (login27, 02:18:26Z) listed the scratch root (repo, policy-config.json, strace-probe.txt; no
run/), recorded the digests of the config and the probe, and removed /dev/shm/limres-rpd-prologue-20261107 by its
literal path. It then read "absent", with no launcher copy left. The connect script deleted its own /dev/shm copy.

Files: rpd_prologue_login.sh, policy-config.json, connect.out (the full transcript, NERSC banner included),
stat_probe.sh/.out, fence-mac.out, survey.txt, cleanup.sh/.out. Digests: SHA256SUMS.txt.
