#!/bin/bash
# Launch run N of connect-complete (A3; the auditor's GO). Usage: launch-complete.sh <N>
# As relaunch.sh: stage the three files in a fresh /dev/shm dir; compare the node's digests to want_sha_complete.txt
# (written only after the auditor's GO; its first line is the connect's own sha, passed as $1) in a separate step;
# launch; wait for DONE; fetch the log and compare its digest; remove the files and the log, logged.
set -u
N=$1; S=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad
F=$S/wavefetch; D=/dev/shm/josephrb-cov2d-complete
[ -s "$F/want_sha_complete.txt" ] || { echo "no want_sha_complete.txt: no GO recorded"; exit 2; }
SELF=$(awk '$2 == "connect-complete.sh" {print $1}' "$F/want_sha_complete.txt")
r(){ ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 \"$1\""; }
[ -e "$F/connect-complete-$N.log" ] && { echo "run $N already fetched"; exit 2; }
r "test ! -e $D && test ! -e $D.log && mkdir -m 700 $D" || { echo "REFUSED /dev/shm not clear"; exit 2; }
for f in connect-complete.sh cov2d_cap.py test_cov2d_cap.py; do r "cat > $D/$f" < "$S/wt-wave/$f" || exit 2; done
r "cd $D && sha256sum connect-complete.sh cov2d_cap.py test_cov2d_cap.py" > "$F/staged_sha_complete-$N.txt"
diff "$F/staged_sha_complete-$N.txt" "$F/want_sha_complete.txt" || { echo "DIGEST_MISMATCH: not launched (files left for inspection)"; exit 3; }
echo "DIGEST_MATCH"
r "setsid nohup bash $D/connect-complete.sh $SELF >/dev/null 2>&1 </dev/null & sleep 1; date -u +%FT%TZ"
for i in $(seq 1 120); do [ "$(r "tail -1 $D.log" 2>&1)" = DONE ] && break; sleep 20; done
r "cat $D.log" > "$F/connect-complete-$N.log"
r "sha256sum $D.log $D/*; echo host=\\\$(hostname) \\\$(date -u +%FT%TZ); for f in $D/* $D.log; do rm -f \\\$f; echo rm -f \\\$f rc=\\\$?; done; rmdir $D; echo rmdir rc=\\\$?; ls -la /dev/shm" > "$F/removal-complete-$N.log"
got=$(shasum -a 256 "$F/connect-complete-$N.log" | cut -c1-64); want=$(awk '/josephrb-cov2d-complete.log$/ {print $1}' "$F/removal-complete-$N.log")
echo "log local=$got node=$want"; [ "$got" = "$want" ] && echo LOG_DIGEST_MATCH || echo LOG_DIGEST_MISMATCH
cat "$F/removal-complete-$N.log"; tail -1 "$F/connect-complete-$N.log"
