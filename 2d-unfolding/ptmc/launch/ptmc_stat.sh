#!/bin/bash
# PTMC D4: the read-only stat connect (the director's instruction, 2026-11-27). Runs on a login node through
# ptmc_stat_launch.sh, as `bash <self> <self>`. It lstats, and opens no file and writes nothing on /pscratch: every
# line comes from find's -printf (lstat; no file is opened, so no file's atime moves). The two directories are read with
# readdir, which may move a DIRECTORY's own atime, never a file's.
#   ROOT/units       : c2_central.* and c2_replica_b*.* (REF-C2C1's IBU products; the baseline uses b1..200)
#   ROOT/read-2/inputs : every entry (000 the publication, 001 E_R's central, 002.. Q_R's replicas, by the reader's order)
# Prints: type, size, mtime, atime, owner, mode, path. Then the expected names present/missing for b = 1..200.
set -u -o pipefail
export LC_ALL=C
ROOT=/pscratch/sd/j/josephrb/ref-c2c1-20261106
U=$ROOT/units
I=$ROOT/read-2/inputs
stop() { echo "STOP: $*"; exit 7; }
me=$(id -un) && [ "$me" = josephrb ] || stop "user"
echo "node $(hostname) $(date -u +%FT%TZ) ptmc stat"
for d in "$ROOT" "$U" "$ROOT/read-2" "$I"; do
  if [ -L "$d" ]; then stop "$d is a symlink"; fi
  if [ ! -e "$d" ]; then echo "ABSENT $d"; continue; fi
  [ -d "$d" ] || stop "$d is not a directory"
  find "$d" -maxdepth 0 -printf 'dir|%s|%T@|%A@|%u|%m|%p\n' || stop "lstat $d"
done
echo "== UNITS (c2_*)"
if [ -d "$U" ]; then
  find "$U" -mindepth 1 -maxdepth 1 -name 'c2_*' -printf '%y|%s|%T@|%A@|%u|%m|%p\n' | sort || stop "list $U"
fi
echo "== INPUTS"
if [ -d "$I" ]; then
  find "$I" -mindepth 1 -maxdepth 1 -printf '%y|%s|%T@|%A@|%u|%m|%p\n' | sort || stop "list $I"
fi
echo "== EXPECTED (regular files, by lstat)"
miss=0; have=0
chk() { if [ -f "$1" ] && [ ! -L "$1" ]; then have=$((have+1)); else miss=$((miss+1)); echo "MISSING $1"; fi; }
for s in npz done; do chk "$U/c2_central.$s"; done
for b in $(seq 1 200); do for s in npz done; do chk "$U/c2_replica_b$b.$s"; done; done
chk "$I/000_cov_ptpl_minerva_inclusive_6GeV.root"
for k in $(seq 1 201); do chk "$I/$(printf '%03d' "$k")_xsec.root"; done
echo "expected present $have missing $miss (of $((2 + 400 + 1 + 201)))"
echo "stat done $(date -u +%FT%TZ)"; exit 0
