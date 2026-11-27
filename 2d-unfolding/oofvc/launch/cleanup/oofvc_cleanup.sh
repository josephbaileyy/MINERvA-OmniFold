#!/bin/bash
# OOFVC cleanup of the two superseded scratch roots (Joseph 2026-11-27, via the director: "you can remove things that
# are unused"). Runs on a login node through oofvc_cleanup_launch.sh, as `bash <self> <self> MODE [LISTING_SHA]`.
#   manifest : read-only. Prints the listing sha of each root and a manifest of every entry
#              (regular files under 1,000,000,000 bytes with sha256; larger ones with size and mtime only).
#   remove   : recomputes the listing; only if its sha256 equals LISTING_SHA (from the fetched manifest) does it remove
#              the two roots by their literal paths, then confirms both are gone and r3's listing is unchanged.
# Every gate fails closed: a failed command is a STOP, never an empty pass.
set -u
export LC_ALL=C
umask 077
MODE=${2:-}; WANT=${3:-}
R1=/pscratch/sd/j/josephrb/oofvc-20261126
R2=/pscratch/sd/j/josephrb/oofvc-20261126-r2
KEEP=/pscratch/sd/j/josephrb/oofvc-20261126-r3
ROOTS=("$R1" "$R2")
BIG=1000000000
stop() { echo "STOP: $*"; exit 7; }
now() { date -u +%FT%TZ; }

case "$MODE" in
  manifest) [ -z "$WANT" ] || stop "manifest takes no listing sha" ;;
  remove) case "$WANT" in [0-9a-f]*) [ ${#WANT} = 64 ] && [ -z "${WANT//[0-9a-f]/}" ] || stop "listing sha must be 64 hex";;
            *) stop "remove needs the 64-hex listing sha";; esac ;;
  *) stop "mode must be manifest or remove" ;;
esac
[ "${#ROOTS[@]}" = 2 ] || stop "root count ${#ROOTS[@]}"
me=$(id -un) && [ "$me" = josephrb ] || stop "user"
echo "node $(hostname) $(now) mode $MODE"

# Fence: no oofvc_ job of mine queued, held or running (a job could own a root).
q=$(squeue -h -u josephrb -o '%i|%j|%T') || stop "squeue failed"
case "$q" in *oofvc_*) stop "an oofvc_ job is in the queue: $q" ;; esac
echo "fence: no oofvc_ job in the queue $(now)"

# Root checks: lstat (never follow), a real directory I own, its canonical path is itself, r3 is not inside it.
for r in "${ROOTS[@]}"; do
  [ ! -L "$r" ] || stop "$r is a symlink"
  [ -d "$r" ] || stop "$r is not a directory (or is absent)"
  o=$(stat -c %U -- "$r") && [ "$o" = josephrb ] || stop "$r owner"
  c=$(readlink -f -- "$r") && [ "$c" = "$r" ] || stop "$r canonical path differs"
  case "$KEEP/" in "$r"/*) stop "$KEEP lies under $r" ;; esac
  # No name with a newline or tab (the listing is line- and tab-separated).
  n=$(find "$r" -name $'*\n*' -o -name $'*\t*' | wc -l) && [ "$n" = 0 ] || stop "$r has a name with a newline or tab"
  # No other filesystem inside, and no regular file with another hard link (removal would touch an inode elsewhere).
  d=$(find "$r" -xdev | wc -l) && a=$(find "$r" | wc -l) && [ "$d" = "$a" ] || stop "$r crosses a filesystem"
  h=$(find "$r" -type f -links +1 | wc -l) && [ "$h" = 0 ] || stop "$r has $h multiply-linked files"
done

# listing ROOT: one line per entry: type, size, mtime (ns), path, and the target for a symlink. Sorted.
listing() { find "$1" -printf '%y\t%s\t%T@\t%p\t%l\n' | sort; }
lsha() { local o; o=$(listing "$1") || return 1; printf '%s\n' "$o" | sha256sum | cut -d' ' -f1; }
keep_state() { if [ -L "$KEEP" ]; then echo "symlink"; elif [ -d "$KEEP" ]; then lsha "$KEEP" || return 1; else echo "absent"; fi; }

ks=$(keep_state) && [ -n "$ks" ] || stop "r3 state"
echo "r3 before: $ks"
all=""
for r in "${ROOTS[@]}"; do
  s=$(lsha "$r") && [ ${#s} = 64 ] || stop "listing of $r"
  c=$(find "$r" | wc -l) && b=$(du -sb -- "$r" | cut -f1) || stop "size of $r"
  echo "root $r entries $c bytes $b listing_sha256 $s"
  all="$all$s"
done
L=$(printf '%s' "$all" | sha256sum | cut -d' ' -f1) && [ ${#L} = 64 ] || stop "combined listing sha"
echo "LISTING_SHA $L"

if [ "$MODE" = manifest ]; then
  echo "== MANIFEST type|size|mtime|sha256 (- for >= $BIG bytes or a non-file)|path|symlink target"
  for r in "${ROOTS[@]}"; do
    lst=$(listing "$r") || stop "listing of $r"
    c=$(find "$r" | wc -l) || stop "count of $r"
    k=0
    while IFS=$'\t' read -r t s mt p l; do
      h=-
      if [ "$t" = f ] && [ "$s" -lt "$BIG" ]; then h=$(sha256sum -- "$p" | cut -d' ' -f1) && [ ${#h} = 64 ] || stop "sha256 $p"; fi
      printf '%s|%s|%s|%s|%s|%s\n' "$t" "$s" "$mt" "$h" "$p" "$l"
      k=$((k+1))
    done < <(printf '%s\n' "$lst")
    [ "$k" = "$c" ] || stop "manifest of $r has $k lines for $c entries"
  done
  echo "== END MANIFEST"
  ks2=$(keep_state) && [ "$ks2" = "$ks" ] || stop "r3 changed during the manifest: $ks2"
  echo "manifest done $(now)"; exit 0
fi

# remove
[ "$L" = "$WANT" ] || stop "listing sha $L is not the manifested $WANT; nothing removed"
for r in "${ROOTS[@]}"; do
  [ ! -L "$r" ] && [ -d "$r" ] || stop "$r changed before its removal"
  echo "removing $r $(now)"
  rm -rf --one-file-system -- "$r"; rc=$?
  echo "rm rc=$rc"
  [ ! -e "$r" ] && [ ! -L "$r" ] || stop "$r still present after rm (rc $rc)"
  echo "gone: $r"
done
ks2=$(keep_state) && [ "$ks2" = "$ks" ] || stop "r3 listing changed: $ks2"
echo "r3 after: $ks2 (unchanged)"
echo "remove done $(now)"; exit 0
