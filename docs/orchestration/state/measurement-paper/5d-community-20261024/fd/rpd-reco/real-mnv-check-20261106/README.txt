RPD-RECO standalone real-class check, 2026-11-06 (the director's go): Codex2's fd_rpd_reco_mat_check.py at #848's
frozen code head d9740563f014c1642546edf314559887003b9920, run by limitation-resolver on login27 at 0 node-h.

RESULT: CRASH, not PASS. The check segfaulted inside ROOT's TFile::Close and exited 129. It wrote no
real-mnv-check.json. Reported unrepaired to the director and Codex2; nothing here was patched or rerun.

THE COMMAND, as connect.out records it (cwd = the fresh clone):
  /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 nd-unfolding/tests/fd_rpd_reco_mat_check.py \
    --probe docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root \
    --run /dev/shm/limres-rpd-mnv-20261106/run/probe
  under nice -n 19, OMP/OPENBLAS/MKL/NUMEXPR/VECLIB threads = 1. The connect script is rpd_mnv_check_login.sh
  (sha256 908d313f12a7bfb65f8505015c097fd6cb2941c874e83955c4a3675d7a409d35). The node compared that digest to the
  expected one before running it.

WHAT RAN, in order (connect.out):
- 22:37:45Z, from the Mac: cov2d_fence.sh exit 3, with cov2d-AR23_Tb (60909280) and cov2d-AR23_Tc (60911676) RUNNING.
  Recorded, not a refusal: the check reads only the committed non-input probe and the pinned MAT setup and library
  files, and no COV2D input. The connect printed the same two jobs again at 22:39:37Z.
- login27 was the lowest-load login node (survey.txt, 10.03 of 244).
- Fresh clone (https, --filter=blob:none) checked out at d9740563: HEAD equal and porcelain empty. Blobs:
  fd_rpd_reco_mat_check.py afdff2a4, fd_rpd_reco.py 36d334dd, fd_rpd_inputs.py 7c2e018f (sha256 in connect.out).
- Probe sha256 d9704aa45c016b044284d9e3cfc8c6d5c07cda0835a445866d5f792c8ac82840, equal to the script's PROBE_SHA256.
- The MAT environment, entered as fd_rpd_reco_flux_connect.sh @ d9740563 enters it:
  - check-mat-setup before sourcing: {"mat_setup_scripts": 6, "mismatches": 0}, rc 0;
  - source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh: rc 0, setup log empty
    (matenv.log, sha256 e3b0c442…, 0 bytes);
  - TMPDIR re-exported to the run's tmp;
  - the env record: MAT_PYTHON = root_6_28's python3, Python 3.11.14, also python3 on PATH;
    PLOTUTILSROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib;
    MINERVA_PREFIX=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt;
    ROOTSYS=/global/homes/j/josephrb/.conda/envs/root_6_28.
  MAT_PYTHON is the interpreter that receipts-rpd/root_tests_login.log measured in this environment (its "B:" line).
- The check printed nine "TInterpreter::ReadRootmapFile" warnings (RooUnfold classes in both libUnfoldUtilsDict.so
  and libRooUnfold.so). Then "*** Break *** segmentation violation" twice, each with the same stack:
  TFile::Close -> TDirectoryFile::Close -> THashList::Delete -> TList::Delete, called from Python
  (JIT frames, no symbols). mat_check rc 129, subshell rc 129, script rc 129, ssh rc 0.
- The run directory held only the staged copy non-input-probe.root (3,136,251 bytes), written by stage_copy before
  the crash. There is no real-mnv-check.json.

NOT DETERMINED HERE: which TFile::Close crashed. check() closes two files: inside read_flux_histogram, and its own
file.Close() after cloning. The checks after the reads (class, layout, interpolation, zero cases) did not report,
because the process died first. No CLING_DEBUG or second run was attempted, by the rule that a STOP goes to the
director unrepaired.

CLEANUP: the script removed /dev/shm/limres-rpd-mnv-20261106 by its literal path and deleted its own /dev/shm copy.
cleanup-check.out (22:40:47Z) shows stat "No such file or directory" (rc 1) and no limres-mnv file left. That ssh's
rc 1 is grep -c's exit on a count of 0, the command's last step.

Files: rpd_mnv_check_login.sh (the connect, as run), connect.out (the full transcript, NERSC banner included),
cleanup-check.out, survey.txt. Digests: SHA256SUMS.txt.
