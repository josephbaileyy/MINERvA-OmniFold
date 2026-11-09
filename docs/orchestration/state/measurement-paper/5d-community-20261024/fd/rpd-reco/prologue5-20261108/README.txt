RPD-RECO #848: data-free prologue, rerun 5, at head 9634aadf (2026-11-08T23:43:21–23:43:50Z, login27, 0 node-h)

RESULT: PASS.
  The environment guard, the platform-library pins, the classifier through process exit and the post-exit library
  verification all passed. The prologue wrapper exited 0, the connect exited 0 and ssh's rc was 0 (read unpiped).
  run/data-free-trace.json was written, with:
    status "PASS"; violations []; worker_exit_code 0; scope "data-free prologue only; no full-connect permission";
    trace_line_count 2711; trace_sha256 dc744840... (= run/prologue.strace);
    successful_open_counts: environment 552, system 297, platform_system 44, pinned_platform_libs 26, run 16,
      python_directory 9, instrument_directory 7, pinned_mat_libs 6, private_prepare 2.
  No STOP record exists: prologue-prepare.STOP.json, prologue-worker.STOP.json and data-free-trace.STOP.json are all
  absent (connect5.out). run/prologue-worker.json has status PASS.
  This receipt reports what was recorded. It grants nothing beyond the data-free prologue: the real-MnvH1D check and
  the full flux-connect gates remain separate.

DIRECTOR'S RELEASE BEFORE LAUNCH
  The connect's header (line 2) describes its authority as "the director's go to prepare, 2026-11-08: #848 GO at
  9634aadf ... coverage-5b-audit https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6726690708".
  That comment is coverage-5b-audit's GO on the code. It is not the release to run. The header is not edited, because
  that would change the connect's sha256. Its wording is superseded by the release quoted here.
  The director's release, verbatim, sent at about 20:45Z on 2026-11-08 (message 5543808b):
    "director → limitation-resolver: **go for prologue rerun 5**, `rpd_prologue5_login.sh`
    f305972d0905ecddbc92cd19e34842e44ba3fd73810b3e7875cdb541eb07d3e1. My local sha matches. It's login-only, with no
    sbatch, salloc or srun in it, at head 9634aadf.
    - **Overlap: none that matters.** It reads the MAT and RooUnfold instruments, the conda environment and platform
      libraries, and none of ENS1's, the band diagnosis's, LL5D's or FD-PRR's data inputs. ENS1's jobs already read the
      same conda environment plainly, and no gate depends on those atimes.
    - **The RooUnfold slot resolution is accepted.** Resolving it to the pscratch build that is on the MAT environment's
      LD_LIBRARY_PATH matches rerun 4's trace and the head's own replay test (test_fd_rpd_reco.py:4827-4829 @
      9634aadf). State it in the receipt as a named resolution of the template's literal, with that citation.
      coverage-5b-audit reads the receipt.
    - **The verdict:** PASS only if the classifier passes, including the after-exit library check against the
      prepare-fixed pins. A STOP comes to me unrepaired, with its public STOP record.
    - Send the receipt PR when it's done."
  Beside it, the audit GO: https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6726690708
  (coverage-5b-audit, GO at 9634aadf, tested source 4fb2add1).
  The launch came about three hours after the release, after a pause in this lane. The fence and the node survey were
  re-run immediately before it (23:41Z), and the connect's sha256 was re-checked on the Mac and on the node.

THE AFTER-EXIT LIBRARY CHECK (run/data-free-trace.json, library_open_checks)
  55 entries: 14 kind "library", 28 "metadata" (stat recorded) and 13 "directory".
  All 14 library entries equal their prepare-fixed pins:
    - the 13 OVIS/LDMS exit-hook libraries under /opt/ovis-ldms/lib (libcoll, libldms, libldms_auth_munge, libmmalloc,
      libovis_ev, libovis_event, libovis_json, libovis_log, libovis_third, libovis_thrstats, libovis_util, libzap,
      ovis-ldms/libzap_sock; each .so.0.0.0): observed == prepared in bytes, device, inode, mtime_ns and sha256;
    - /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/libMAT.so: observed sha256 5901f18a... equals its
      MAT pin (the prepared value is the sha256 alone).
  Where the OVIS libraries appear in run/prologue.strace:
    - line 2546: the worker reads /proc/self/maps;
    - lines 2547–2559: the worker opens the 13 inventory files by canonical path, to verify every inventory pin
      including those not yet mapped;
    - line 2561: the worker writes run/prologue-worker.json;
    - lines 2564–2694: pymon's exit hook loads the same 13 libraries by soname at interpreter exit (rerun 4's late
      loads, there at 2562–2692).
  The late loads come after the worker's record, and they are covered: each opened platform library passed the
  classifier's pin rule, and the parent's post-exit verification re-checked them against stat and digest pins after
  the traced process returned.

NAMED RESOLUTION OF THE TEMPLATE'S ROOUNFOLD SLOT
  The draft template (late-platform-library-repair-20261108/production-config.draft.json @ 9634aadf, line 279) writes
  the third trace_instrument_directories entry as "${BOUND_CHECKOUT}/unbinned_unfolding/build". Read literally, that
  is the fresh clone, which has no build. This connect resolves it to
    /pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build
  for three reasons:
    - it is the directory the MAT environment puts on LD_LIBRARY_PATH (prologue2-20261107/run/environment_after_setup.json);
    - rerun 4's trace opened it (prologue4-20261108/run/prologue.strace @ 68a36cf8);
    - the head's replay test appends exactly that path (test_fd_rpd_reco.py:4827-4829 @ 9634aadf).
  The director accepted it in the release above. Every other slot was resolved to rerun 4's value: the clone root
  (prologue5-20261108); REVIEWED_MAT_PREFIX = /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt; the dump and
  flux roots, the FluxReweighter source path, the two environment roots and rerun 4's COV2D protected paths.
  EXTRACT_RUN is left unresolved, as in rerun 4, because the prologue extracts nothing. The five repo pins, re-hashed
  at 9634aadf, are unchanged. policy-config.json is sha256 6152adce...

WHAT RAN (rpd_prologue5_login.sh, sha256 f305972d...; its stdout is connect5.out and its stderr connect5.err)
  0. Before the connect, from the Mac: fence-mac.out showed no cov2d-* job (23:41:24Z). survey.txt picked login27
     (load 2.27 on 244). One ssh (saul -> login27) wrote the script to a /dev/shm mktemp, compared its sha256 (it
     matched) and ran it.
  1. The in-script fence passed (refusing rows: []). Only rs1_* and ens1_* would have been allowed.
  2. A fresh clone at 9634aadf: HEAD equal, porcelain 0. The blob ids and sha256 of the five prologue files are in
     connect5.out.
  3. policy-config.json, tools/c3_check.py (de197369...) and tools/check_redaction.py (992be729...) were written from
     the connect and gated on their sha256. The two check scripts are rerun 4's, byte-identical: custody's
     private_prepare_path, read_private_prepare, write_private_prepare, public_record and export are AST-identical
     between 6a287e1a and 9634aadf. tools/gen_connect.py generated this connect from rerun 4's (38b9b98b). Its only body
     changes are the head, the root, the config, the fence names, and run/data-free-trace.STOP.json added to the send
     list.
  4. strace-probe.txt: the strace probe, 30 lines.
  5. fd_rpd_reco_prologue_connect.sh at 9634aadf. Its output is wrapper.out (11 lines: MAT setup scripts 6, mismatches
     0; MAT setup exit status 0; nine ROOT rootmap warnings, "class RooUnfold... found in libUnfoldUtilsDict.so is already
     in libRooUnfold.so"). No analysis input is read and no flux connect is made.
  6. C3 and the redaction check, under MAT_PYTHON -I -S:
     - c3-check.txt, C3 CHECK PASS. The canonical record is at
       /dev/shm/limres-rpd-prologue5-20261108/.rpd-private/23ee3e97.../prologue-prepare.json, the recomputed location,
       outside the run. It is -rw------- in a drwx------ directory, both owned by uid 112498. Its sha256 81c3fb7a...
       equals the reference's, and it carries 355 fingerprint keys. .rpd-private holds only it. None of the 11 send
       files is it.
     - redaction-check.txt, REDACTION CHECK PASS. The view has no fingerprints map and 0 64-hex strings under the
       environment keys; 0 fingerprint values were found in any file checked, data-free-trace.json included.
  7. Only after both passed: a base64 tar of 12 files, none under .rpd-private. Each file's sha256 on the cluster
     (connect5.out) equals its sha256 here (12 of 12). In the committed connect5.out, the 50302-line base64 block is
     replaced by a one-line note giving the decoded tar's sha256 (ca94d0a1...) and the full stdout's (085e9917...).
  connect5.err is the NERSC login banner only.

THE PRIVATE RECORD IS NOT IN THIS RECEIPT
  /dev/shm/limres-rpd-prologue5-20261108/.rpd-private/23ee3e970f74d1084106615b6dba8e6c4798e1728044d8831a90b8abc1296a66/
  prologue-prepare.json, sha256 81c3fb7af87602b13cff1cdad59e2faababffff8cd9d69a80a660fcffc3988e4. It never left the
  cluster. It and the whole root stay on login27 until this receipt merges. They are then deleted by
  rpd_prologue5_cleanup.sh (2d3e62ba...) under the declared ledger row delete-copies/row1-dev-shm-private-prepare/
  ledger.json. That connect deletes nothing unless the record's sha256 still equals the declared value, and its
  sha256 goes to the director before it runs. It is rerun 4's cleanup connect with the root, token, digest and labels
  changed.

FILES
  rpd_prologue5_login.sh, connect5.out, connect5.err, fence-mac.out, survey.txt
  policy-config.json, tools/c3_check.py, tools/check_redaction.py, tools/gen_connect.py
  the 12 files sent: strace-probe.txt, wrapper.out, run/trace-policy.json, run/prologue-prepare-reference.json,
    run/prologue.strace, run/worker.stderr.txt, run/worker.stdout.txt, run/prologue-prepare.json (the code's public
    view), run/prologue-worker.json, run/data-free-trace.json, c3-check.txt, redaction-check.txt
  rpd_prologue5_cleanup.sh, delete-copies/row1-dev-shm-private-prepare/ledger.json (declared)
  Digests: SHA256SUMS.txt.
