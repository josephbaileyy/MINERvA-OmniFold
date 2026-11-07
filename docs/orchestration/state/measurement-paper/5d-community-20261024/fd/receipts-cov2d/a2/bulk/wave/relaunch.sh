#!/bin/bash
# Relaunch wave N of the reviewed stage-4 connect (director: approved under the sequence). Usage: relaunch.sh <N>
# Stage the three reviewed files in a fresh /dev/shm dir; compare the node's digests to the reviewed ones (a separate
# step from the launch); launch with the connect's own sha as $1; wait for DONE; fetch the log and compare its digest;
# remove the files and the log, logged.
set -u
N=$1; S=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad
F=$S/wavefetch; SELF=f20da2d56845de3be68c0b3c828ef66d6560dc33ceb6441f683f8acc066d112e   # connect-wave v2, the auditor's GO 2026-11-06
r(){ ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 \"$1\""; }
[ -e "$F/connect-wave-$N.log" ] && { echo "wave $N already fetched"; exit 2; }
r "test ! -e /dev/shm/josephrb-cov2d-wave && test ! -e /dev/shm/josephrb-cov2d-wave.log && mkdir -m 700 /dev/shm/josephrb-cov2d-wave" || { echo "REFUSED /dev/shm not clear"; exit 2; }
for f in connect-wave.sh cov2d_cap.py test_cov2d_cap.py; do r "cat > /dev/shm/josephrb-cov2d-wave/$f" < "$S/wt-wave/$f" || exit 2; done
r "cd /dev/shm/josephrb-cov2d-wave && sha256sum connect-wave.sh cov2d_cap.py test_cov2d_cap.py" > "$F/staged_sha-$N.txt"
diff "$F/staged_sha-$N.txt" "$F/want_sha.txt" || { echo "DIGEST_MISMATCH: not launched (files left for inspection)"; exit 3; }
echo "DIGEST_MATCH"
r "setsid nohup bash /dev/shm/josephrb-cov2d-wave/connect-wave.sh $SELF >/dev/null 2>&1 </dev/null & sleep 1; date -u +%FT%TZ"
for i in $(seq 1 180); do [ "$(r 'tail -1 /dev/shm/josephrb-cov2d-wave.log' 2>&1)" = DONE ] && break; sleep 20; done
r "cat /dev/shm/josephrb-cov2d-wave.log" > "$F/connect-wave-$N.log"
r "sha256sum /dev/shm/josephrb-cov2d-wave.log /dev/shm/josephrb-cov2d-wave/*; echo host=\\\$(hostname) \\\$(date -u +%FT%TZ); for f in /dev/shm/josephrb-cov2d-wave/* /dev/shm/josephrb-cov2d-wave.log; do rm -f \\\$f; echo rm -f \\\$f rc=\\\$?; done; rmdir /dev/shm/josephrb-cov2d-wave; echo rmdir rc=\\\$?; ls -la /dev/shm" > "$F/removal-wave-$N.log"
got=$(shasum -a 256 "$F/connect-wave-$N.log" | cut -c1-64); want=$(awk '/josephrb-cov2d-wave.log$/ {print $1}' "$F/removal-wave-$N.log")
echo "log local=$got node=$want"; [ "$got" = "$want" ] && echo LOG_DIGEST_MATCH || echo LOG_DIGEST_MISMATCH
cat "$F/removal-wave-$N.log"; tail -1 "$F/connect-wave-$N.log"
