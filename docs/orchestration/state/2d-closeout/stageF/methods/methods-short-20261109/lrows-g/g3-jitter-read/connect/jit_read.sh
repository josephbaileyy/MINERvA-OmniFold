#!/bin/bash
# G3 (referee6 major 7), step 2: a 0 node-h login read of I0's 21 data-jitter products (the base and j1..j20,
# FD-1B-INV-DECLARATION.md:131-133), for the jitter covariance's off-diagonals, computed on the Mac. Each source is
# opened once with O_NOATIME and copied into a NEW $OUT; the copy's sha256 must equal the source bytes'; every
# source's stat (size, mtime, atime) is recorded before and after and compared byte for byte (exit 4 on a difference);
# nothing is deleted or modified at the source. Named paths only; no directory outside $OUT is listed. Login node
# only. Writes $OUT/jit.tar.gz (the 21 copies and manifest.json). Launched from a /dev/shm copy of itself ($1).
SELF=$1
D=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data
OUT=/pscratch/sd/j/josephrb/g3-jitter-20261112
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== g3-jit-read rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"; echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ ! -e "$OUT" ] || { echo "STOP: $OUT exists"; finish 9; }
mkdir "$OUT" "$OUT/copies" || finish 9
FILES=""
for j in - 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do FILES="$FILES $D/data_b-_j$j.npz"; done
stat -c '%n|%s|%Y|%X' $FILES > "$OUT/stat-before.txt" 2>&1 || { echo "STOP: a source is missing"; cat "$OUT/stat-before.txt"; finish 3; }
env -u PYTHONPATH "$PY" -I - "$OUT" $FILES <<'PY'
import hashlib, json, os, sys
out, files = sys.argv[1], sys.argv[2:]
flag = getattr(os, "O_NOATIME", None)
if flag is None:
    sys.exit("STOP: no O_NOATIME")
rec = []
for f in files:
    fd = os.open(f, os.O_RDONLY | flag)
    with os.fdopen(fd, "rb") as fh:
        b = fh.read()
    dst = os.path.join(out, "copies", os.path.basename(f))
    with open(dst, "xb") as fh:
        fh.write(b)
    with open(dst, "rb") as fh:
        c = fh.read()
    hs, hc = hashlib.sha256(b).hexdigest(), hashlib.sha256(c).hexdigest()
    if hs != hc:
        sys.exit(f"STOP: copy digest differs for {f}")
    rec.append({"src": f, "copy": os.path.basename(f), "bytes": len(b), "sha256": hs})
    print(f"COPY {os.path.basename(f)} {len(b)} {hs}")
json.dump({"schema": "g3-jit-read/1", "files": rec}, open(os.path.join(out, "manifest.json"), "w"), indent=1)
PY
prc=$?
stat -c '%n|%s|%Y|%X' $FILES > "$OUT/stat-after.txt" 2>&1
if cmp -s "$OUT/stat-before.txt" "$OUT/stat-after.txt"; then echo "sources: stat byte-identical before and after (atime unmoved)"
else echo "DEVIATION: a source's stat changed:"; diff "$OUT/stat-before.txt" "$OUT/stat-after.txt"; finish 4; fi
[ "$prc" -eq 0 ] || { echo "STOP: the copy step exited $prc"; finish 5; }
tar -C "$OUT" -czf "$OUT/jit.tar.gz" copies manifest.json stat-before.txt stat-after.txt || finish 6
echo "jit.tar.gz sha256 $(sha256sum "$OUT/jit.tar.gz" | cut -d' ' -f1)"
finish 0
