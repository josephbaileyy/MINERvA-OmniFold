#!/bin/bash
# 1B pre-check Part 1, P1 rerun: fetch the run's own records for the receipt. Login node, 0 node-h. It reads only files
# the P1 rerun wrote under $V (no staged copy, no original), each with O_NOATIME, and prints each one's sha256 and base64.
# It writes nothing. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
finish() { echo "== pfd-p1r-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== COV2D fence (allowed names: rs1_* and ens1_*; anything else refuses)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
printf '%s\n' "$fence"
bad=$(printf '%s\n' "$fence" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "squeue rc=$frc; refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
env -u PYTHONPATH "$PY" -I -S - "$V" <<'PYEOF'
import base64, hashlib, os, sys
V = sys.argv[1]
for name in ("p1r-stage-atime-before.tsv", "p1r-stage-atime-after-rehash.tsv", "p1r-stage-atime-after-controls.tsv",
             "stat-p1r.txt", "stat-p1r-end.txt"):
    fd = os.open(os.path.join(V, name), os.O_RDONLY | os.O_NOATIME)
    chunks = []
    try:
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    data = b"".join(chunks)
    print(f"== FILE {name} sha256 {hashlib.sha256(data).hexdigest()} bytes {len(data)}")
    print(base64.encodebytes(data).decode(), end="")
    print(f"== END FILE {name}")
PYEOF
finish $?
