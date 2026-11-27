#!/bin/bash
# Removes the old IBUB namespace /pscratch/sd/j/josephrb/ibub-20261123, and nothing else (Joseph's authorization of
# 2026-11-24, given directly to the director: "you can remove that old folder"). On a Perlmutter login node, from a
# /dev/shm copy that its launcher stages and sha-checks. It takes no argument, and every path in it is the literal
# below. It writes nothing on the cluster. The inventory and the rc lines go to stdout only, and the launcher keeps
# them on the laptop.
#
# In order, each failure a refusal (rc 9) before anything is removed:
#  1. no argument; a Perlmutter login node;
#  2. the path: no `..`; not a symlink; a directory; owned by josephrb; realpath equal to the literal;
#  3. sacct over 14 days (no -s filter, State classified in code): no job named ibub_* unended, no malformed row,
#     and 61914825 CANCELLED;
#  4. the directory's stat (mtime, inode, owner), then the inventory, `find -printf '%y %s %T@ %p'`, then the file
#     count and total bytes; the stat again, which must be unchanged (the B9 row's stat_match);
#  5. rm -rf -- the literal; then stat must fail with ENOENT.
set -o pipefail
P=/pscratch/sd/j/josephrb/ibub-20261123
refuse() { echo "REFUSE: $*"; echo "rm-ibub rc=9"; exit 9; }
[ "$#" -eq 0 ] || refuse "this script takes no argument"
case "$(hostname)" in login[0-9][0-9]) ;; *) refuse "not a Perlmutter login node ($(hostname))";; esac
echo "host $(hostname) utc $(date -u +%FT%TZ)"

# ---- the path
case "$P" in *..*) refuse "the path has a '..'";; esac
[ ! -L "$P" ] || refuse "$P is a symlink"
[ -d "$P" ] || refuse "$P is not a directory"
owner=$(stat -c %U -- "$P") || refuse "stat of $P failed"
[ "$owner" = josephrb ] || refuse "$P is owned by '$owner', not josephrb"
real=$(realpath -e -- "$P") || refuse "realpath of $P failed"
[ "$real" = "$P" ] || refuse "$P resolves to $real"
echo "path ok: $P (directory, owner $owner, realpath equal)"

# ---- sacct: no ibub_ job unended, and 61914825 CANCELLED
rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || refuse "sacct failed: $rows"
bad=$(printf '%s\n' "$rows" | awk -F'|' '
  NF == 0 { next }
  NF != 3 || $1 !~ /^[0-9]+([_+].*)?$/ { print "malformed: " $0; next }
  index($2, "ibub_") == 1 {
    split($3, w, " ")
    if (w[1] !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) print
  }') || refuse "the sacct classification failed"
[ -z "$bad" ] || refuse "an ibub_ job is unended, or a row is malformed: $(printf '%s\n' "$bad" | tr '\n' ' ')"
old=$(printf '%s\n' "$rows" | awk -F'|' '$1 == "61914825"')
[ "$(printf '%s\n' "$old" | grep -c .)" -eq 1 ] || refuse "sacct has no single row for 61914825: '$old'"
case "$(printf '%s\n' "$old" | cut -d'|' -f3)" in "CANCELLED"|"CANCELLED "*) ;; *) refuse "61914825 is not CANCELLED: '$old'";; esac
echo "sacct ok: $(printf '%s\n' "$rows" | awk -F'|' 'index($2, "ibub_") == 1' | grep -c .) ibub_ rows, all ended; 61914825: $old"

# ---- the inventory, before anything is removed, between two equal stats of the directory
s1=$(stat -c '%Y %i %U' -- "$P") || refuse "stat of $P failed"
echo "dir stat before: mtime inode owner = $s1"
echo "== inventory begin: find $P -printf '%y %s %T@ %p\n'"
find "$P" -printf '%y %s %T@ %p\n' || refuse "the inventory (find) failed"
echo "== inventory end"
nf=$(find "$P" -type f | wc -l) || refuse "the file count failed"
nb=$(find "$P" -type f -printf '%s\n' | awk '{ s += $1 } END { printf "%d", s }') || refuse "the byte total failed"
ne=$(find "$P" | wc -l) || refuse "the entry count failed"
echo "inventory: $ne entries, $nf files, $nb bytes"
s2=$(stat -c '%Y %i %U' -- "$P") || refuse "stat of $P failed"
[ "$s2" = "$s1" ] || refuse "$P changed during the inventory ($s1 -> $s2)"
echo "dir stat after the inventory: $s2 (stat_match=yes)"

# ---- the removal of the literal path, then ENOENT
rm -rf -- /pscratch/sd/j/josephrb/ibub-20261123; rrc=$?
echo "rm rc=$rrc"
st=$(stat -- /pscratch/sd/j/josephrb/ibub-20261123 2>&1); src=$?
echo "stat rc=$src: $st"
if [ "$rrc" -eq 0 ] && [ "$src" -ne 0 ] && [[ "$st" == *"No such file or directory"* ]] \
    && [ ! -e /pscratch/sd/j/josephrb/ibub-20261123 ] && [ ! -L /pscratch/sd/j/josephrb/ibub-20261123 ]; then
  echo "removed: $P is gone (ENOENT)"; echo "rm-ibub rc=0"; exit 0
fi
echo "STOP: $P is not ENOENT after rm (rm rc $rrc, stat rc $src)"; echo "rm-ibub rc=5"; exit 5
