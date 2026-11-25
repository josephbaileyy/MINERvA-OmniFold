#!/bin/bash
# EVW5D: the Mac-side launcher (ESS's ess_launch.sh, adapted). One ssh session per call: it enters at saul.nersc.gov and
# hops to NODE; stdin carries the script through both hops; on NODE the script is staged in a private mktemp file in
# /dev/shm whose sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs. The remote
# script's exit status is the remote wrapper's, so ssh's status (read unpiped) is the script's.
# Usage: bash evw5d_launch.sh connect|post <new empty session dir> <login node, e.g. login27>
#        bash evw5d_launch.sh hpss <new empty session dir> <login node> <bound SHA256SUMS sha256>
#        bash evw5d_launch.sh fetch <new empty dir>                     (post.tar.gz and hpss.tar.gz; no remote script)
#        bash evw5d_launch.sh fetch-products <new empty dir> <bound SHA256SUMS sha256>
#             (the products by scp, then evw5d.accepted(dir, bound) on the Mac with $EVW5D_PY, default python3)
MODE=${1:?connect|post|hpss|fetch|fetch-products}; F=${2:?session dir}; NODE=${3:-}; BOUND=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=/pscratch/sd/j/josephrb/evw5d-20261125
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
hex64() { case "$1" in *[!0-9a-f]*|"") return 1;; esac; [ ${#1} -eq 64 ]; }
case "$MODE" in
  connect) S="$HERE/evw5d_connect.sh"; SHA=__CONNECT_SHA256__ ;;
  post)    S="$HERE/evw5d_post.sh";    SHA=__POST_SHA256__ ;;
  hpss)    S="$HERE/evw5d_hpss.sh";    SHA=__HPSS_SHA256__
           hex64 "$BOUND" || { echo "STOP: hpss needs the bound SHA256SUMS sha256"; exit 9; } ;;
  fetch)
    rc=0
    for f in post.tar.gz hpss.tar.gz; do
      scp "${SSH[@]}" "saul.nersc.gov:$OUT/$f" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
      echo "scp $f rc=$r"; [ $r = 0 ] && shasum -a 256 "$F/$f"; [ $r = 0 ] || rc=$r
    done
    exit $rc ;;
  fetch-products)
    BOUND=$3
    hex64 "$BOUND" || { echo "STOP: fetch-products needs the bound SHA256SUMS sha256"; exit 9; }
    mkdir -p "$F/evw5d/product"
    for f in weights.npz constants.npz constants.json run.json SHA256SUMS evw5d.done product/data_b-_j-.npz; do
      scp "${SSH[@]}" "saul.nersc.gov:$OUT/evw5d/$f" "$F/evw5d/$f" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
      echo "scp $f rc=$r"; [ $r = 0 ] || exit $r
    done
    TOP=$(cd "$HERE/../../../../../../../.." && pwd) || exit 9      # launch/ is 8 levels below the checkout's top
    "${EVW5D_PY:-python3}" -B -c "import sys; sys.path.insert(0, sys.argv[1]); import evw5d
ok = evw5d.accepted(sys.argv[2], sys.argv[3]); print('ACCEPTED' if ok else 'REFUSED'); sys.exit(0 if ok else 1)" \
      "$TOP/nd-unfolding/evw5d" "$F/evw5d" "$BOUND"
    r=$?; echo "accepted rc=$r"; exit $r ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 for $MODE is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="umask 077; f=\$(mktemp /dev/shm/evw5d-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\" $BOUND; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
