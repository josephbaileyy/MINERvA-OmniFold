RPD-RECO #848: data-free prologue, rerun 4, at combined head 6a287e1a (2026-11-08T08:27:31–08:27:58Z, login27, 0 node-h)

The director gave the go after #848 round 2 was found GO at 6a287e1ab6fb53bf3e1a42309202d5c28e04c4de (tested
225d8949). The connect sha256 is 38b9b98bf757240cc30f5ec20c7b683321f403c6d28d3b58e9fe0f53b1e6d20f. Rerun 4 had to
show three things:
  - the guard passes where rerun 3's MAT_PREPARE_ENVIRONMENT STOPped, with the import diff holding only the five
    whitelisted keys at their pinned values;
  - the worker reaches the classifier, and the trace is classified;
  - any STOP is reported exactly as recorded, unrepaired.

This receipt reports what was recorded. It does not read a cause. Round 3 is Codex2's.

RESULT
  ssh rc 4, which is the connect's exit status: the prologue wrapper's rc 4.
  The guard PASSED. The worker wrote run/prologue-worker.json with status PASS and data_keys_read [], and wrote no
  prologue-worker.STOP.json.
  The classifier then STOPped. The worker exited and the parent ran custody.classify_trace on run/prologue.strace.
  classify_trace refused, so run/data-free-trace.json was not written. The verdict exists only as line 12 of
  wrapper.out:
    "STOP DATA_FREE_TRACE: syscall custody violations: [...]"
  That line is 30767 characters, and its JSON list has 146 entries. It is committed parsed as
  run/classifier-stop-entries.json. The parser is tools/parse_stop_line.py, with its output in tools/parse.out.
  json.dumps of the parsed list equals the line's text byte for byte. Entries by reason:
    unclassified or ambiguous successful open    77   (keys request, resolved, success, reason, categories)
    unparsed open syscall                         67   (keys line, reason; each line is an openat ending
                                                        "<unfinished ...>")
    cwd changed inside extraction trace            2   (keys line, reason; chdir("/dev/shm/limres-rpd-prologue4-
                                                        20261108/repo") = 0)
  The full strace that the classifier read is run/prologue.strace (446312 bytes).

THE GUARD, AS RECORDED (run/prologue-worker.json, under environment)
  This is the worker context's record. The prepare context records no import diff: the public view
  run/prologue-prepare.json has no root_import key.
  root_import_environment_diff:
    added:   CLING_PREBUILT_MODULE_PATH  "/global/u2/j/josephrb/.conda/envs/root_6_28/lib:"
             CLING_STANDARD_PCH          "none"
             CPPYY_API_PATH              "none"
             CPPYY_NO_ROOT_FILTER        "1"
    changed: ROOTSYS  prepared "/global/homes/j/josephrb/.conda/envs/root_6_28"
                      observed "/global/u2/j/josephrb/.conda/envs/root_6_28"
    removed: {}
  root_import_validation:
    pass                   true
    unexpected             {"added": {}, "changed": {}, "removed": {}}
    invalid_pinned_values  {}
    rootsys                prepared_present true; expected_realpath = observed =
                           "/global/u2/j/josephrb/.conda/envs/root_6_28"; valid true
    allowed_import_keys    CLING_PREBUILT_MODULE_PATH, CLING_STANDARD_PCH, CPPYY_API_PATH, CPPYY_NO_ROOT_FILTER,
                           ROOTSYS
  runtime_environment_exclusions: {}
  The public view run/prologue-prepare.json carries comparison_status PASS.

WHAT RAN (rpd_prologue4_login.sh; its stdout is connect4.out and its stderr connect4.err)
  0. Before the connect, from the Mac: fence-mac.out showed no cov2d-* job (08:25:37Z). survey.txt picked login27
     (load 6.70 on 244). One ssh (saul -> login27) wrote the script to a /dev/shm mktemp, compared its sha256 (it
     matched), and ran it. ssh's rc was read unpiped.
  1. The in-script fence passed: squeue listed no jobs. rs1_*, ens1_* and, for this connect only, fd1b_pfd_* would have
     been allowed. Any other name refuses.
  2. A fresh clone at 6a287e1a: HEAD equal, porcelain 0. The blob ids and sha256 of the five prologue files are in
     connect4.out.
  3. policy-config.json (211224e5...) is rerun 3's 6c60de0b with only the clone root renamed in five path strings. The
     five repo pins it names were re-hashed at 6a287e1a and are unchanged. The two check scripts were written from
     the connect and gated on their sha256.
  4. strace-probe.txt: the strace probe, 30 lines.
  5. fd_rpd_reco_prologue_connect.sh, unchanged at 6a287e1a since #881. Its stdout and stderr went to wrapper.out,
     which was printed and sent only after both checks passed. The real MAT source exited 0. The traced worker is
     run/prologue.strace, with run/worker.stderr.txt and an empty run/worker.stdout.txt. Also run/trace-policy.json
     and the reference run/prologue-prepare-reference.json. No analysis input is read, and no flux connect is made.
  6. C3 and the redaction check, both on the cluster, under MAT_PYTHON -I -S:
     tools/c3_check.py (de197369...), output c3-check.txt: C3 CHECK PASS.
       - The reference names the location recomputed from custody.private_prepare_path:
         /dev/shm/limres-rpd-prologue4-20261108/.rpd-private/3cdf27c8.../prologue-prepare.json.
       - It is outside the run.
       - The record is -rw------- in a drwx------ directory, both owned by uid 112498, the connect's uid.
       - Its sha256 7f12fdfd... equals the reference's, and it carries 355 fingerprint keys.
       - .rpd-private holds that one file only.
       - No file on the send list is under .rpd-private or has the record's sha256.
     tools/check_redaction.py (992be729...), output redaction-check.txt: REDACTION CHECK PASS. This is rerun 3's
     df244a49 taking the private record as RAW and the code's view as VIEW, plus a fifth check.
       - The view has no fingerprints map.
       - There are 0 64-hex strings under environment_snapshot or environment_after_setup.
       - There are 0 fingerprint values in any of the 11 files checked.
       - The 22 other 64-hex strings in the view are listed by path.
       - Check 5: 0 keys named fingerprints in any JSON sent.
  7. Only after both passed: a base64 tar of an explicit list of 11 files, none under .rpd-private. Each file's sha256
     on the cluster (connect4.out) equals its sha256 here. In the committed connect4.out the 15271-line base64 block
     is replaced by a one-line note giving the decoded tar's sha256 (bbffef65...) and the full stdout's (318cec2e...).

WHAT THE PUBLIC RECORDS CARRY
  The code's public_record() removes every "fingerprints" map. It replaces each credential-pattern key (here only
  SSH_AUTH_SOCK) with a presence and equality summary, listed under redacted_environment. Module paths are exported
  as module_name_components and source_path.
  The other environment values are kept as display values: 355 keys in the view's environment_snapshot.values and
  environment_after_setup, and in the worker's environment_after_setup; 359 in its native_environment_after_mat.

THE PRIVATE RECORD IS NOT IN THIS RECEIPT
  /dev/shm/limres-rpd-prologue4-20261108/.rpd-private/3cdf27c8d29fe5d5407acb8ca456ade8a1df23de41ce5930c70a2a3bcb5cc522/
  prologue-prepare.json, sha256 7f12fdfdd14bf82ff1e9ba72324b9269bba183984f41cc6fdf5b4383573a0afb, 161842 bytes. It
  never left the cluster. It and the whole root stay on login27 until this receipt merges. They are then deleted by
  rpd_prologue4_cleanup.sh (58b2942c...) under the ledger row delete-copies/row1-dev-shm-private-prepare/ledger.json.
  That connect deletes nothing unless the record's sha256 still equals the declared value. Its sha256 goes to the
  director before it runs.

FILES
  rpd_prologue4_login.sh, connect4.out, connect4.err, fence-mac.out, survey.txt
  policy-config.json, tools/c3_check.py, tools/check_redaction.py
  the 11 files sent: strace-probe.txt, wrapper.out, run/trace-policy.json, run/prologue-prepare-reference.json,
    run/prologue.strace, run/worker.stderr.txt, run/worker.stdout.txt, run/prologue-prepare.json (the code's public
    view), run/prologue-worker.json, c3-check.txt, redaction-check.txt
  run/classifier-stop-entries.json, tools/parse_stop_line.py, tools/parse.out (written on the Mac from wrapper.out)
  rpd_prologue4_cleanup.sh, delete-copies/row1-dev-shm-private-prepare/ledger.json (declared)
