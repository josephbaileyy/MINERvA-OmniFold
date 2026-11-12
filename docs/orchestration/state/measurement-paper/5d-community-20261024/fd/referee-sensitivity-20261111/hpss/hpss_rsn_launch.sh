#!/bin/bash
# RSN's HPSS archive: the Mac-side launcher, kit rev 2 (the director's ruling of 2026-11-12: run on a login node, as
# #1054 did). Its hop is hpss-20261111's hpss_launch.sh (296ea772), unchanged: one ssh session per call enters at
# saul.nersc.gov and hops to NODE (a loginNN; never a data-transfer node, never a Slurm job), with ServerAlive 15/8 on
# both hops and StrictHostKeyChecking=no on the inner one, as #1054 ran. ssh's rc is read unpiped. Needs a current
# sshproxy certificate (Joseph renews it).
# Modes, all writing only into the new empty local directory F, except archive:
#   survey  read-only: for each named login node, its loadavg, nproc and /dev/shm line (#1054's survey, which chose
#           the node with the lowest load and the most free /dev/shm);
#   probe   read-only, on NODE: the tools, /dev/shm, hpssquota, hsi's listing of the HPSS home and of the target, the
#           $OUT path, O_NOATIME, SLURM_JOB_ID, squeue -u josephrb, and, twice, stat -c "%s %F" of the 67 listed
#           paths counted as ok or ZERO (size 0); the list's paths travel on stdin;
#   archive the approved hpss_rsn.sh: on NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes it
#           and exits 8 before anything runs; it runs detached (setsid nohup, stdin /dev/null, output to a /dev/shm
#           file), so a dropped session cannot kill it, and it writes its own log under $OUT/logs;
#   fetch   scp of $OUT/post.tar.gz and $OUT/logs/archive.log through saul.
# Usage: bash hpss_rsn_launch.sh survey <new empty dir> "<loginNN> <loginNN> ..."
#        bash hpss_rsn_launch.sh probe|archive <new empty dir> <loginNN>
#        bash hpss_rsn_launch.sh fetch <new empty dir>
MODE=${1:?survey|probe|archive|fetch}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
OUT=/pscratch/sd/j/josephrb/hpss-rsn-20261111
H=/home/j/josephrb/mnv-rsn-inputs-20261111
LIST="$HERE/hpss_rsn_list.tsv"; LIST_SHA=0dafaac8e3664875f496974fb79f73e319ada7647eb5106dbe6626cefa9d99c6
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=no)
login() { case "$1" in login[0-9][0-9]) ;; *) echo "STOP: '$1' is not a login node name"; exit 9;; esac; }
hop() {  # hop <node> <remote command> : stdin is passed through both hops
  ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $1 $(printf '%q' "$2")" > "$F/session.out" 2> "$F/session.err"
  rc=$?; echo "ssh rc=$rc"; cat "$F/session.out"; exit $rc
}
case "$MODE" in
  survey)
    [ -n "$NODE" ] || { echo "STOP: no login nodes named"; exit 9; }
    for n in $NODE; do login "$n"; done
    R='date -u +%FT%TZ; for n in '"$NODE"'; do ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $n '\''echo $(hostname -s) $(cut -d" " -f1-3 /proc/loadavg) $(nproc) $(df -h /dev/shm | tail -1)'\'' < /dev/null 2>&1; done'
    ssh "${SSH[@]}" saul.nersc.gov "$R" < /dev/null > "$F/session.out" 2> "$F/session.err"
    rc=$?; echo "ssh rc=$rc"; cat "$F/session.out"; exit $rc ;;
  probe)
    login "$NODE"
    [ "$(shasum -a 256 "$LIST" | cut -d' ' -f1)" = "$LIST_SHA" ] || { echo "STOP: the list is not the approved one"; exit 8; }
    R='l=/dev/shm/hpssr-probe.$$.list; umask 077; cat > "$l"; echo "host $(hostname -s) $(date -u +%FT%TZ) slurm_job='\''$SLURM_JOB_ID'\''"; command -v hsi htar hpssquota timeout setsid sha256sum python3; df -h /dev/shm | tail -1; hpssquota 2>&1 | tail -3; hsi -q "ls -d /home/j/josephrb" 2>&1; echo "home rc=$?"; hsi -q "ls -d '"$H"'" 2>&1; echo "target rc=$?"; ls -d '"$OUT"' 2>&1; /usr/bin/python3 -c "import os; print(\"O_NOATIME\", hasattr(os, \"O_NOATIME\"))"; squeue -u josephrb -h -o "%i %j %T" 2>&1; echo "squeue rc=$?"; echo "list rows $(wc -l < "$l")"; for k in 1 2; do echo "stat pass $k"; while read -r p; do stat -c "%s %F %n" "$p"; done < "$l" | awk "{print \$1==0?\"ZERO\":\"ok\"}" | sort | uniq -c; done; rm -f -- "$l"'
    cut -f3 "$LIST" | hop "$NODE" "$R" ;;
  archive)
    login "$NODE"
    S="$HERE/hpss_rsn.sh"; SHA=012a9618adf7e4b493700954747f5afd1ea4235907c1b2f794e754e2062311d8
    [ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local archive script is not the approved one"; exit 8; }
    R="f=/dev/shm/hpssr-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
    hop "$NODE" "$R" < "$S" ;;
  fetch)
    scp "${SSH[@]}" "saul.nersc.gov:$OUT/post.tar.gz" "saul.nersc.gov:$OUT/logs/archive.log" "$F/" > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post.tar.gz" "$F/archive.log"; exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
