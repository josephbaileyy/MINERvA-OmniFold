REF-C2C1 completion attempt 1 (job 60897523): the B9-form ledger row for renaming its paths aside (the director's ruling
of 2026-11-06 and its addendum; follow-up to ../README.txt). Run by limitation-resolver: refc2c1_rename_attempt1_login.sh,
sha256 0216f736ae2397031b8ebfc6b76a9a4dec6ae4439bdecc65e14c803afc02c0c2, read by coverage-5b-audit before the run. It ran on
login27 at 2026-11-06T12:36:20Z-12:37:02Z, rc 0, at 0 node-h. Copied by O_NOATIME reads (pullr_tar.py) from
/pscratch/sd/j/josephrb/ref-c2c1-20261106/rename-attempt-1-60897523/. Full sha256 of each file: SHA256SUMS.txt.

LEDGER ROW (ledger.log):
- Gate: main d293b13d holds completion-attempt-1/REPLICAS-DONE-j4 at sha256 7016fdef...4ab1, equal to the pscratch record
  and to the expected value. No fd_c2c1r job was queued, and no target name existed.
- REPLICAS-DONE-j0..3: absent before and after. REPLICAS-TIMEOUT-j0..3, unchanged: 33e194d4, d9534758, 3e5c2557, 809fc771.
- Before (12:36:52Z): `ls -la` of the five paths. REPLICAS-DONE-j4 is 1055 B at sha256 7016fdef. deploy-completion has
  21723 entries at HEAD 77d76cfc. libcheck-completion has 1 entry, logs-completion 19 and tmp-replicas-j4 0. The full
  stat manifests (type, size, mtime, relative path) are in measure-before.txt, with per-file sha256 for logs-completion
  and libcheck-completion.
- The moves, one per path, `mv -n` with no deletion, 12:36:59.400Z-12:36:59.426Z:
    REPLICAS-DONE-j4     -> REPLICAS-DONE-j4.attempt-1-60897523
    deploy-completion    -> deploy-completion.attempt-1-60897523
    libcheck-completion  -> libcheck-completion.attempt-1-60897523
    logs-completion      -> logs-completion.attempt-1-60897523
    tmp-replicas-j4      -> tmp-replicas-j4.attempt-1-60897523
- After (12:36:59Z): the same measurements on the new names (measure-after.txt). Outside its stat header lines,
  measure-after.txt is byte-identical to measure-before.txt: "contents before and after: identical (sha256, stat
  manifests, HEAD)". None of the old names remains.
- logs-completion's contents were already copied into ../ (#833) before the rename, and the 12:22:38Z stat listing is
  ../survey/leftovers-1222Z.txt.

This frees the five paths that attempt 2's unchanged connect refuses on. Attempt 2's connect writes
$O/refc2c1_completion_job.sbatch anew and checks it against its JOB_SHA; attempt 1's copy there (bee44fae, in ../) does not
block. Files: ledger.log, measure-before.txt, measure-after.txt, the script's own copy, rename.done, clone.log, and
pullr_tar.py, the copy script. The main clone the gate used stays on pscratch under rename-attempt-1-60897523/main-clone/.
