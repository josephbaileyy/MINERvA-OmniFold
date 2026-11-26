#!/bin/bash
# EVW2D: the Mac-side launcher for the HPSS copy and the deposit fetch (EVW5D's hpss and fetch-products modes, with
# EVW2D's certificate and credential checks from evw2d_launch.sh, verbatim). Every pin is filled into this file at the
# binding: the lane root, the approved evw2d.py, the bound config digest, the products' SHA256SUMS digest (the post's,
# e60867ef...), the job id and the approved evw2d_hpss.sh.
# Before every step: the NERSC sshproxy certificate by command (TZ=UTC ssh-keygen -L on the public certificate; it
# reads no key) must succeed, have begun and last the step's margin, and `ssh -G` must offer only that key and
# certificate. Otherwise exit 7.
# Usage: bash evw2d_deposit.sh hpss <new empty session dir> <login node, e.g. login27>
#          one ssh session through saul to NODE; NODE stages evw2d_hpss.sh in a private mktemp file in /dev/shm, runs
#          it only if its sha256 is the approved one (else deletes it and exits 8), then deletes it.
#        bash evw2d_deposit.sh fetch <new empty dir>
#          hpss.tar.gz (an absent archive is told apart from an ssh failure), then its receipt is verified: the log names
#          the bound digests and job, 6 of 6 retrieved and equal to their pins, the rename to the final name and
#          "hpss rc=0", and its pinned list holds the bound digests. Exit 0 only then; 5 = fetched but not verified.
#        bash evw2d_deposit.sh fetch-products <new empty dir under $HOME, outside /private/tmp and /tmp>
#          the six product files by scp into <dir>/out, then the checker on the Mac: the local evw2d.py must be the
#          approved bytes and is executed as the very bytes hashed (no import, no cache); evw2d.accepted(<dir>/out) must
#          pass with SHA256SUMS's and evw2d.done's digests, run.json's config digest and slurm_job the bound ones
#          ($EVW2D_PY, default python3, with numpy).
# The directory argument is resolved once, to a physical path (CDPATH unset), and every write uses that path.
MODE=${1:?hpss|fetch|fetch-products}; F=${2:?session dir}; NODE=${3:-}
unset CDPATH
F=$(cd -- "$F" 2>/dev/null && pwd -P) || { echo "STOP: $2 is not a directory"; exit 9; }
HERE=$(cd "$(dirname "$0")" && pwd)
LANE=__LANE_ROOT__
EVW_SHA=__EVW2D_PY_SHA256__
CFG_SHA=__CONFIG_SHA256__
BOUND=__PRODUCTS_SHA256SUMS_SHA256__
DONE_SHA=__EVW2D_DONE_SHA256__
JOBID=__JOB_ID__
CERT=${EVW2D_CERT:-$HOME/.ssh/nersc-cert.pub}
KEY=${CERT%-cert.pub}
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o IdentitiesOnly=yes -o "IdentityFile=$KEY"
     -o "CertificateFile=$CERT")
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$DONE_SHA" "$JOBID"; do
  case "$v" in *__*) echo "STOP: a pin is not filled in"; exit 9;; esac
done
cert_ok() {   # cert_ok <seconds>: ssh-keygen succeeds; the window "Valid: from A to B" (UTC) has begun and lasts that long
  local out from to b e now
  out=$(TZ=UTC ssh-keygen -L -f "$CERT" 2>&1) || { echo "STOP: ssh-keygen -L failed on $CERT"; return 1; }
  from=$(printf '%s\n' "$out" | sed -n 's/^ *Valid: from \([0-9T:-]*\) to \([0-9T:-]*\)$/\1/p' | head -1)
  to=$(printf '%s\n' "$out" | sed -n 's/^ *Valid: from \([0-9T:-]*\) to \([0-9T:-]*\)$/\2/p' | head -1)
  [ -n "$from" ] && [ -n "$to" ] || { echo "STOP: no validity window read from $CERT"; return 1; }
  b=$(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%S "$from" +%s 2>/dev/null) || { echo "STOP: cannot read the time '$from'"; return 1; }
  e=$(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%S "$to" +%s 2>/dev/null) || { echo "STOP: cannot read the time '$to'"; return 1; }
  now=$(date +%s) || { echo "STOP: no clock"; return 1; }
  echo "certificate valid $from to $to UTC ($(( (e - now) / 60 )) min left; this step needs $(( $1 / 60 )))"
  [ "$b" -le "$now" ] || { echo "STOP: the certificate is not valid yet"; return 1; }
  [ $(( e - now )) -ge "$1" ] || { echo "STOP: the certificate expires too soon for this step"; return 1; }
}
cred_ok() {   # the resolved ssh configuration for saul offers only the checked key and certificate
  local g bad
  g=$(ssh -G "${SSH[@]}" saul.nersc.gov 2>&1) || { echo "STOP: ssh -G failed"; return 1; }
  bad=$(printf '%s\n' "$g" | awk -v k="$KEY" -v c="$CERT" -v h="$HOME" '
    $1 == "identityfile" || $1 == "certificatefile" { p = $2; sub(/^~/, h, p)
      if (($1 == "identityfile" && p != k) || ($1 == "certificatefile" && p != c)) print $1 " " $2 }
    $1 == "identitiesonly" && $2 != "yes" { print "identitiesonly " $2 }')
  [ -z "$bad" ] || { echo "STOP: ssh would offer another credential: $bad"; return 1; }
}
case "$MODE" in
  hpss) S="$HERE/evw2d_hpss.sh"; SHA=__HPSS_SHA256__; MARGIN=3600 ;;
  fetch)
    cert_ok 600 || exit 7
    cred_ok || exit 7
    have=$(ssh "${SSH[@]}" saul.nersc.gov "if [ -f $LANE/hpss.tar.gz ]; then echo present; else echo absent; fi" < /dev/null); r=$?
    case "$r:$have" in
      0:present) ;;
      0:absent) echo "hpss.tar.gz absent"; exit 4 ;;
      *) echo "STOP: could not ask saul for hpss.tar.gz (ssh rc=$r)"; exit "${r/#0/3}" ;;
    esac
    scp "${SSH[@]}" "saul.nersc.gov:$LANE/hpss.tar.gz" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
    echo "scp hpss.tar.gz rc=$r"; [ $r = 0 ] || exit $r
    shasum -a 256 "$F/hpss.tar.gz" || exit 3
    mkdir "$F/receipt" && tar xzf "$F/hpss.tar.gz" -C "$F/receipt" || { echo "NOT VERIFIED: the archive does not unpack"; exit 5; }
    log="$F/receipt/hpss/hpss.log"; pins="$F/receipt/hpss/pinned.sha256"; R=${LANE##*/}
    [ -f "$log" ] && [ ! -L "$log" ] && [ -f "$pins" ] && [ ! -L "$pins" ] || { echo "NOT VERIFIED: no hpss.log or pinned.sha256"; exit 5; }
    v=1
    head -1 "$log" | grep -Fq " bound $BOUND done $DONE_SHA job $JOBID" || v=0
    grep -Fxq "retrieved and equal to their pins: 6 of 6; files retrieved: 6" "$log" || v=0
    grep -Fxq "renamed to /home/j/josephrb/mnv-$R/$R.tar" "$log" || v=0
    tail -1 "$log" | grep -Eq '^hpss rc=0 ' || v=0
    grep -Fxq "$BOUND  $R/out/SHA256SUMS" "$pins" || v=0
    grep -Fxq "$DONE_SHA  $R/out/evw2d.done" "$pins" || v=0
    [ "$(wc -l < "$pins" | tr -d ' ')" = 6 ] || v=0
    [ "$v" = 1 ] || { echo "NOT VERIFIED: the HPSS receipt is not a passing copy bound to $BOUND and job $JOBID"; exit 5; }
    echo "VERIFIED: the HPSS copy of $R ($BOUND, job $JOBID) is in place and was verified by retrieval"
    exit 0 ;;
  fetch-products)
    home=$(cd -- "$HOME" && pwd -P) || { echo "STOP: no HOME"; exit 9; }
    dest=$F                                                   # already resolved to a physical path
    case "$dest/" in "$home"/?*/) ;; *) echo "STOP: $F is not a directory under \$HOME"; exit 9;; esac
    case "$dest/" in /private/tmp/*|/tmp/*|/private/var/*|/var/*) echo "STOP: $F is under a temporary root"; exit 9;; esac
    TOP=$(git -C "$HERE" rev-parse --show-toplevel) || { echo "STOP: the launcher is not in a checkout"; exit 9; }
    W="$TOP/2d-unfolding/evw2d/evw2d.py"
    w=$(shasum -a 256 "$W" | cut -d' ' -f1) && [ -f "$W" ] && [ ! -L "$W" ] && [ "$w" = "$EVW_SHA" ] || \
      { echo "STOP: the local checker $W is not the approved bytes"; exit 8; }
    cert_ok 1800 || exit 7
    cred_ok || exit 7
    mkdir "$F/out" || exit 9
    for f in SHA256SUMS evw2d.done constants.json run.json xsec.root weights.npz; do
      scp "${SSH[@]}" "saul.nersc.gov:$LANE/out/$f" "$F/out/$f" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
      echo "scp $f rc=$r"; [ $r = 0 ] || exit $r
    done
    ( cd "$F/out" && shasum -a 256 SHA256SUMS evw2d.done constants.json run.json xsec.root weights.npz )
    "${EVW2D_PY:-python3}" -I -B -c "import hashlib, json, sys, types
src = open(sys.argv[1], 'rb').read()
if hashlib.sha256(src).hexdigest() != sys.argv[3]:
    print('REFUSED: the checker changed'); sys.exit(1)
evw2d = types.ModuleType('evw2d'); evw2d.__file__ = sys.argv[1]; sys.modules['evw2d'] = evw2d
exec(compile(src, sys.argv[1], 'exec'), evw2d.__dict__)   # the very bytes hashed: no import, no cache
from pathlib import Path
out = Path(sys.argv[2])
r = evw2d.accepted(out)
run = json.loads((out / 'run.json').read_text())
sums = hashlib.sha256((out / 'SHA256SUMS').read_bytes()).hexdigest()
done = hashlib.sha256((out / 'evw2d.done').read_bytes()).hexdigest()
ok = (r['pass'] is True and sums == sys.argv[4] and done == sys.argv[5] and run.get('config_sha256') == sys.argv[6]
      and str(run.get('slurm_job')) == sys.argv[7])
print(json.dumps({'verdict': 'ACCEPTED' if ok else 'REFUSED', 'accepted_pass': r['pass'],
                  'acceptance': r['acceptance'], 'sums': sums, 'done': done,
                  'config_sha256': run.get('config_sha256'), 'slurm_job': run.get('slurm_job')}))
print('ACCEPTED' if ok else 'REFUSED'); sys.exit(0 if ok else 1)" \
      "$W" "$F/out" "$EVW_SHA" "$BOUND" "$DONE_SHA" "$CFG_SHA" "$JOBID"
    r=$?; echo "checker rc=$r"; exit $r ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 for $MODE is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
cert_ok "$MARGIN" || exit 7
cred_ok || exit 7
R="umask 077; f=\$(mktemp /dev/shm/evw2d-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
