RPD-RECO #848: data-free prologue, rerun 3, at combined head 2ed446b4 (2026-11-08T04:47Z, login04, 0 node-h)

The director gave the go after #848 round 1 was found GO at 2ed446b4ba78269565ee1104462fc9e15b63afba (tested head
91dbf0a7; coverage-5b-audit, #848 comment 6717323539). The connect sha256 is
03d4ab1ea2814fa5f0c1341a0976a2aa8c3e54c84dba8804c7474c698955e0a5. The purpose was to record the worker's real
key-level environment diff. The guard was expected to STOP again, now with the diff. It did.

This receipt reports the diff exactly as recorded. It does not read a cause. Round 2 is Codex2's.

RESULT
  prologue wrapper rc=4. Last stderr line: "STOP DATA_FREE_TRACE: MAT_WORKER_EXIT: prologue worker exited 4".
  The worker wrote run/prologue-worker.STOP.json with guard MAT_PREPARE_ENVIRONMENT. Its details:
    run           prepared = observed = /dev/shm/limres-rpd-prologue3-20261108/run
    connect_id    prepared = observed = f15a28ae-e0cc-415d-9e8a-f93f049a2a76 (presence required: true; observed: true)
    age           observed_age_ns 2064781177 (bounds 0 .. 7200000000000, exclusive)
    environment   excluded: "_" (shell-maintained last-command value)
                  record_display_diff: {} (empty)
                  diff.added:   CLING_PREBUILT_MODULE_PATH = "/global/u2/j/josephrb/.conda/envs/root_6_28/lib:"
                  diff.removed: {} (empty)
                  diff.changed: NERSC_PYMON_UUID  prepared "edfe380a-17cb-4881-9a8a-aa894f32fba2"
                                                  observed "277b2777-abc4-4ea2-9d6c-ec6965ae4fab"
                                ROOTSYS           prepared "/global/homes/j/josephrb/.conda/envs/root_6_28"
                                                  observed "/global/u2/j/josephrb/.conda/envs/root_6_28"
  The redaction's per-key table agrees: 358 keys on the prepare side, plus the 1 added on the worker side. By
  comparison: 355 equal, 2 changed, 1 added, 1 excluded, 0 removed.

WHAT RAN (rpd_prologue3_login.sh; its stdout is connect3.out and its stderr connect3.err)
  0. Before the connect, from the Mac: fence-mac.out (no cov2d-* job). survey.txt picked login04 (load 8.30 on 244).
     One ssh (saul -> login04) wrote the script to a /dev/shm mktemp, compared its sha256 (matched), then ran it.
     ssh's rc was 4, read unpiped; that is the connect's own exit status, which passes through the wrapper's.
  1. The in-script fence passed. squeue listed no jobs; rs1_* and ens1_* names would have been allowed, and any other
     name refused.
  2. A fresh clone at 2ed446b4, HEAD equal and porcelain 0. Blob ids and sha256 of the five RPD-RECO files are in
     connect3.out.
  3. policy-config.json (6c60de0b...): #881's fe1ce783 with only the clone root renamed in five path strings. The five
     repo pins it names were re-hashed at 2ed446b4 and are unchanged. The redaction scripts were written from the
     connect and gated on their sha256.
  4. strace-probe.txt: the strace probe, 30 lines.
  5. Codex2's fd_rpd_reco_prologue_connect.sh, unchanged at 2ed446b4 since #881. The real MAT source exited 0. The
     traced worker is run/prologue.strace, with run/worker.stderr.txt and an empty run/worker.stdout.txt. Also
     run/trace-policy.json. No analysis input is read, and no flux connect is made.
  6. The redaction, on the cluster, under MAT_PYTHON -I -S:
     tools/redact_prepare.py (5be4650d...) wrote the view of the raw run/prologue-prepare.json. It deletes
     environment_snapshot.fingerprints and keeps, per key, only the name, its presence on the prepare and worker
     sides, and the comparison (environment_snapshot.fingerprint_comparison). The worker side comes from the STOP
     record. Output: run/redact.out.
     tools/check_redaction.py (df244a49...) checked the view and every file sent against the raw fingerprints. Output:
     run/redaction-check.txt, REDACTION CHECK: PASS.
       - no fingerprints map;
       - zero 64-hex strings under environment_snapshot or environment_after_setup;
       - zero fingerprint values in the view, the STOP record, worker stderr and stdout, the strace, the trace
         policy, the policy config, the strace probe or redact.out;
       - the 21 other 64-hex strings in the view are listed by path (instrument and setup file digests, the trace
         policy's digest, the raw record's digest).
  7. Only after the check passed: a base64 tar of an explicit list of nine files. The list cannot name the raw
     record. Each file's sha256 on the cluster (connect3.out) equals its sha256 on the Mac. In the committed
     connect3.out the 10420-line base64 block is replaced by a one-line note giving the decoded tar's sha256
     (b697cf25...) and the full stdout's sha256 (3a5d87db...).

THE RAW RECORD IS NOT IN THIS RECEIPT
  run/prologue-prepare.json, sha256 337a88c893f0e1b24d90db8d940133d172f22a1d67f0aa7f8cc5f5044c73b5c8, 162122 bytes.
  It holds unsalted SHA-256 fingerprints of every environment value, credential fields included. It never left the
  cluster. It stays at /dev/shm/limres-rpd-prologue3-20261108 on login04, mode 600 in a 700 root, until this receipt
  merges. It is then deleted by rpd_prologue3_cleanup.sh (418c6aad...) under the ledger row
  delete-copies/row1-dev-shm-raw-prepare/ledger.json. That connect deletes nothing unless the record's sha256 still
  equals the declared value.

THE VIEW: module_paths MOVED TO module-paths.tsv (the director's choice (a))
  The receipt-artifact hook reads the module name nersc_pymon.log, a key of module_paths, as a bare .log citation.
  This is the same false positive that kept #881's prepare record off git. The checker is not touched; the director
  holds it for the follow-up list.
  On the Mac, tools/move_module_paths.py moved module_paths, unchanged, into run/module-paths.tsv: 320 rows of
  name<TAB>path, sorted by name. It left a pointer in the view, rebuilt the original from the two outputs, and
  confirmed the bytes equal (tools/move.out).
    view as redacted on the cluster (before the move)  ea71db558c44231a683a5b7b0a13a11f7850ade8e91e8d5cbc14e11b2f467307
    committed view run/prologue-prepare.view.json      c4f52563cd40a345c9d764b6cb7df84f6532a4bf5dd660c75e98bae5ee7a3a6d
    run/module-paths.tsv                                1b7f7df9890915dc7d05d6e3ecfe5bbcd599735ee8f9fa12b3775a6cb7b9d0a9
  The pre-move view is not committed. It is the committed view with module_paths rebuilt from the TSV.

SHA256SUMS.txt
  It lists every committed file, then three records that are not committed, marked "not committed": the pre-move
  view, the raw record and the full stdout. `shasum -c` reports those three as missing.
