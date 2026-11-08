RPD-RECO data-free prologue, rerun, 2026-11-07 (the director's go, after coverage-5b-audit closed C1-C4 on #848):
Codex2's fd_rpd_reco_prologue_connect.sh + fd_rpd_reco_prologue.py at #848's head
2cfa1a1ea6f474471dda43bb95d292edea2a73e3, run by limitation-resolver on login27, 06:48:01-06:48:27Z, at 0 node-h.
Before it, in the same connect, ran the director's C4a shell-options probe.

RESULTS
- C4a: SETTLED. After `set +u; source setup_salloc_env.sh; set -u`, the shell reads flags=ehuB, and errexit, nounset and
  pipefail are all "on" (c4a.out). The probe's rc was 0, and check-mat-setup inside it gave 6 scripts, 0 mismatches.
- The prologue: STOP in the traced worker, reported unrepaired. Quoted (connect2.out, run/worker.stderr.txt):
    MAT setup exit status: 0
    STOP DATA_FREE_TRACE: MAT_PREPARE: stale, foreign or environment-mismatched prepare receipt   (the worker)
    STOP DATA_FREE_TRACE: MAT_WORKER_EXIT: prologue worker exited 4                                 (the parent)
    prologue wrapper rc=4
  - The wrapper's set +u around the source worked: the setup exited 0.
  - prepare completed: it staged the pinned MAT instrument files, built and wrote trace-policy.json, and wrote
    prologue-prepare.json.
  - The traced worker then refused at fd_rpd_reco.checked_prepared_mat (fd_rpd_reco.py:1222-1235 @ 2cfa1a1e). The
    parent refused because the worker exited 4, so the classifier never ran, and there is no data-free-trace.json.
  - The guard is one require over five conjuncts: the run path; FD_RPD_RECO_CONNECT_ID present; equal to the
    prepare's; the prepare's age under 2 h; and environment_after_setup equal to the worker's
    custody.environment_record(), with "_" excluded. It records none of the compared values, so which conjunct failed
    is not in the record.
    - What the record does fix: the connect took 26 s, so age cannot fail. The prepare records run
      /dev/shm/limres-rpd-prologue2-20261107/run and connect_id 0c87679e-f8b7-4544-b951-d90bb8e7a7e9, and the worker
      inherited both through the environment.
    - The prepare's environment record (358 variables) is committed as run/environment_after_setup.json. The worker's
      is not recorded anywhere, so the environment conjunct can be neither confirmed nor excluded here.
  - The prepare's own checks passed:
    - mat_environment mapped exactly {.../MINERvA101/opt/lib/libMAT.so};
    - plotutils_mnvh1d_dictionary is True;
    - the six setup scripts and three MAT files were copied at their pins into run/instrument/. Those copies are not
      committed: one is the 1.9 MB libMAT.so binary, and all are pinned.
- prologue.strace (1,992 lines) is the worker's full trace, ending "+++ exited with 4 +++". It is committed
  unclassified, because the classifier runs only after a worker rc of 0.

THE CONNECT (rpd_prologue2_login.sh, sha256 106bf513..., compared on the node before it ran), in order:
1. The COV2D fence, immediately before: squeue rc 0, no cov2d-* row. It was also clear from the Mac at 06:46:06Z
   (fence2-mac.out). login27 was the lowest-load node (survey2.txt).
2. A fresh https clone at 2cfa1a1e: HEAD equal, porcelain 0. Blobs: the wrapper b2872a6c (the C4 fix), prologue.py
   58f3666d, fd_rpd_reco.py 487084bc, custody 837704db, fd_rpd_inputs.py 7c2e018f. Apart from the wrapper, these are
   the same blobs as at 4ea4a113.
3. The resolved policy config: policy-config.json, sha256 fe1ce7830d9c230dda6cc1c6c569113b58c425c575d97ffc5d9fc12e994370eb.
   It was written from the script, checked on the node, and its copy in the run is byte-identical.
   - It equals the config the director accepted in #870 (39921087) with three paths added to cov2d_protected_paths,
     as ruled:
     - /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux, the whole directory, which holds
       runEventLoopMC_MEFHC.root and flux_integral_universes_MEFHC.root;
     - $UNI, /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root;
     - the CFS CV, /global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
       (cov2d_writer.py:35).
   - The checkout paths name the new literal root /dev/shm/limres-rpd-prologue2-20261107/repo.
   - Each added path was stat-confirmed beforehand (login35, 06:43:59Z).
4. The strace probe: /bin/true, rc 0, 30 lines (strace-probe.txt).
5. The C4a probe, as the director gave it (c4a.sh, c4a.out).
6. The prologue wrapper, as #848's PR body gives it: CHECKOUT CONFIG SHA RUN MAT_PYTHON, with MAT_PYTHON root_6_28's
   python3.

THE RECORDS COMMITTED:
- the trace policy: run/trace-policy.json, sha256 be87e6a1..., which equals the prepare's trace_policy_sha256;
- the env record: run/environment_after_setup.json, prologue-prepare.json's environment_after_setup extracted
  unchanged, with a source line naming the prepare's sha256. Credential-named fields are redacted by the producer;
  only SSH_AUTH_SOCK is, and no token-shaped value is present;
- prologue-prepare.json itself (sha256 fe847284d43285cf3af12e81884a74d029e546ed24d08109a171cc7ec82800be) is NOT
  committed:
  - the receipt-artifact hook reads its module_paths key "nersc_pymon.log", a Python module name, as a bare file
    citation;
  - by the standing rule (don't edit the shared checker from a lane), such a record stays out of git, listed by
    sha256;
  - a byte-identical copy is on pscratch at
    /pscratch/sd/j/josephrb/rpd-reco-records-20261107/prologue2/prologue-prepare.json, mode 440, with sha256
    re-read there;
- the strace output: run/prologue.strace, sha256 571f87a6...;
- the worker's output: run/worker.stderr.txt and run/worker.stdout.txt (empty).

CLEANUP: cleanup2.sh (login27, 06:49:42Z) listed the root and removed /dev/shm/limres-rpd-prologue2-20261107 by its
literal path. It then read "absent", with no launcher copy left.

Files: rpd_prologue2_login.sh, connect2.out (the full transcript, NERSC banner included), policy-config.json, c4a.sh,
c4a.out, strace-probe.txt, run/{trace-policy.json, environment_after_setup.json, prologue.strace,
worker.stderr.txt, worker.stdout.txt}, fence2-mac.out, survey2.txt, cleanup2.sh, cleanup2.out. Digests: SHA256SUMS.txt.
