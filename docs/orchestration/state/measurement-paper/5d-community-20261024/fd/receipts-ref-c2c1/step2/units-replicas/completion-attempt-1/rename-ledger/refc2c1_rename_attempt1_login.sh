#!/bin/bash
# REF-C2C1 completion attempt 1 (job 60897523): rename its paths aside, so attempt 2's unchanged connect and job can run
# (the director's ruling of 2026-11-06 and its addendum: every attempt-1 path that exists among REPLICAS-DONE-j4,
# deploy-completion, libcheck-completion, logs-completion and tmp-replicas-j4 becomes <name>.attempt-1-60897523; no
# deletions; a B9-form ledger row: ls and sha256, or a file manifest for a directory, before and after, the mv lines and
# the time). On a login node, detached. It refuses unless attempt 1's receipt is on main (in a fresh clone,
# completion-attempt-1/REPLICAS-DONE-j4 hashes equal to the pscratch record), no fd_c2c1r job is queued, and no target
# name exists. Files are hashed by O_NOATIME reads; directories get a stat manifest (type, size, mtime, relative path),
# plus per-file sha256 for logs-completion and libcheck-completion, and HEAD for the deploy clone. After the moves the
# same measurements run on the new names and must be equal; the old names must be absent. Writes only under $O (the
# moves, and $O/rename-attempt-1-60897523/). No set -u. Launched from a /dev/shm copy of itself ($1).
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
S=.attempt-1-60897523
X=$O/rename-attempt-1-60897523
DONE_SHA=7016fdef7b4810b55b3c9dc2d70d05934dc64526d47add3fac661b4d8ac54ab1
AP=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/units-replicas/completion-attempt-1
NAMES="REPLICAS-DONE-j4 deploy-completion libcheck-completion logs-completion tmp-replicas-j4"
bail() { rm -f -- "$SELF"; exit 9; }
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$X" ] || bail
for n in $NAMES; do [ ! -e "$O/$n$S" ] || bail; done
[ -z "$(squeue --me -h -n fd_c2c1r -o %i)" ] || bail
mkdir -p "$X" || bail
exec > "$X/ledger.log" 2>&1
finish() { echo "ref-c2c1 attempt-1 rename rc=$1"; date -u +%FT%TZ; echo "$1" > "$X/rename.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "rename script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$X/refc2c1_rename_attempt1_login.sh"
git clone -q --depth 1 https://github.com/josephbaileyy/MINERvA-OmniFold.git "$X/main-clone" > "$X/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
ms=$(git -C "$X/main-clone" show "HEAD:$AP/REPLICAS-DONE-j4" 2>/dev/null | sha256sum | cut -d' ' -f1)
ps=$(dd if="$O/REPLICAS-DONE-j4" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "gate: main $(git -C "$X/main-clone" rev-parse HEAD): $AP/REPLICAS-DONE-j4 $ms; pscratch $ps; expected $DONE_SHA"
[ "$ms" = "$DONE_SHA" ] && [ "$ps" = "$DONE_SHA" ] || { echo "STOP: attempt 1's receipt is not on main, or the record changed"; finish 4; }
measure() {  # $1 = suffix ("" before, $S after); writes $X/measure<tag>.txt with relative names so before and after compare
  local sfx=$1 n p
  for n in $NAMES; do
    p=$O/$n$sfx
    if [ ! -e "$p" ]; then echo "== $n: absent"; continue; fi
    echo "== $n: $(stat -c '%F %s %U %a %y' "$p")"
    if [ -f "$p" ]; then echo "sha256 $(dd if="$p" iflag=noatime status=none | sha256sum | cut -d' ' -f1)"
    else
      echo "entries $(find "$p" -mindepth 1 | wc -l)"
      (cd "$p" && find . -mindepth 1 -printf '%y %s %T@ %P\n' | LC_ALL=C sort) | sed 's/^/  /'
      case "$n" in logs-completion|libcheck-completion)
        (cd "$p" && find . -type f -printf '%P\n' | LC_ALL=C sort | while read -r f; do echo "  sha256 $(dd if="$f" iflag=noatime status=none | sha256sum | cut -d' ' -f1) $f"; done);;
      deploy-completion) echo "  HEAD $(git -C "$p" rev-parse HEAD 2>/dev/null || echo unreadable)";;
      esac
    fi
  done
}
echo "== the four TIMEOUT jobs' records (unchanged by this; REPLICAS-DONE-j0..3 must be absent)"
for J in 0 1 2 3; do
  [ ! -e "$O/REPLICAS-DONE-j$J" ] || { echo "STOP: REPLICAS-DONE-j$J exists"; finish 4; }
  echo "REPLICAS-DONE-j$J absent; REPLICAS-TIMEOUT-j$J sha256 $(dd if="$O/REPLICAS-TIMEOUT-j$J" iflag=noatime status=none | sha256sum | cut -d' ' -f1)"
done
echo "== BEFORE $(date -u +%FT%TZ)"; ls -la --time-style=full-iso "$O" | grep -E " ($(echo $NAMES | tr ' ' '|'))(\.attempt-1-60897523)?$"
measure "" > "$X/measure-before.txt"; cat "$X/measure-before.txt" | grep -E '^(==|sha256|entries|  HEAD)'
echo "== MOVES"
for n in $NAMES; do
  [ -e "$O/$n" ] || { echo "skip $n: absent"; continue; }
  echo "$(date -u +%FT%T.%3NZ) mv -n -- $O/$n $O/$n$S"; mv -n -- "$O/$n" "$O/$n$S" || { echo "STOP: mv $n failed"; finish 9; }
done
echo "== AFTER $(date -u +%FT%TZ)"; ls -la --time-style=full-iso "$O" | grep -E " ($(echo $NAMES | tr ' ' '|'))(\.attempt-1-60897523)?$"
measure "$S" > "$X/measure-after.txt"; cat "$X/measure-after.txt" | grep -E '^(==|sha256|entries|  HEAD)'
left=0; for n in $NAMES; do [ -e "$O/$n" ] && { echo "STOP: $n still present"; left=1; }; done
for J in 0 1 2 3; do [ ! -e "$O/REPLICAS-DONE-j$J" ] || { echo "STOP: REPLICAS-DONE-j$J exists"; left=1; }; done
echo "REPLICAS-DONE-j0..3 absent after: $([ "$left" -eq 0 ] && echo yes || echo NO)"
if cmp -s <(grep -v '^== ' "$X/measure-before.txt") <(grep -v '^== ' "$X/measure-after.txt") && [ -s "$X/measure-before.txt" ]; then
  echo "contents before and after: identical (sha256, stat manifests, HEAD)"
else echo "STOP: contents differ:"; diff "$X/measure-before.txt" "$X/measure-after.txt" | head -20; finish 8; fi
[ "$left" -eq 0 ] || finish 8
finish 0
