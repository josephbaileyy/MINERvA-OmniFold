#!/bin/bash
# Result package, 2D arrays: a read-only copy of RE-2 part C's adopted 2D export, cov2d_Q_205.npz (sha256 7153b194...;
# re2/run/partc_r2/partc-r2/SHA256SUMS:76). It holds Q_R and its blocks (s5_total, universe, stat, c08, C_PL) on the 205
# reported cells, the cells' global ids (pt*16 + pz) and x = E_R on those cells (outA/cov2d_Q_205.json.gz).
# Login node, nice 19, 0 node-h, no Slurm job. Every step stamped to the second. In order:
#   1. the file's stat (%F|%i|%h|%s|%Y|%X|%Z|%n) before the read;
#   2. one read through O_NOATIME: its sha256 must equal 7153b194...; only then are the bytes printed, base64, between
#      the markers, with their byte count. On a mismatch nothing is printed and the connect exits 8;
#   3. the stat after the read, which must be byte-identical to the one before (atime included); a difference is a STOP
#      (exit 4) and is reported unrepaired.
# It writes nothing on the cluster: no file under pscratch, CFS or HPSS; the only file it touches is the /dev/shm copy
# of itself ($1) that the launcher made, which it deletes. The Mac side decodes the block and re-checks the sha256.
SELF=$1
F=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/outA/cov2d_Q_205.npz
WANT=7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
ts() { date -u +%FT%TZ; }
finish() { echo "== c2a rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -f "$F" ] || { echo "STOP: $F is not a file"; finish 5; }
echo "== 1. stat before $(ts)"
before=$(stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$F"); echo "$before"
echo "== 2. read (O_NOATIME) $(ts)"
nice -n 19 env -u PYTHONPATH "$PY" -B -c '
import base64, hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME)
chunks = []
while True:
    b = os.read(fd, 1 << 20)
    if not b:
        break
    chunks.append(b)
os.close(fd)
data = b"".join(chunks)
got = hashlib.sha256(data).hexdigest()
print(f"read {len(data)} bytes; sha256 {got} (bound {sys.argv[2]})")
if got != sys.argv[2]:
    print("STOP: the file is not the bound file; nothing is printed")
    sys.exit(8)
print("== BEGIN cov2d_Q_205.npz base64")
enc = base64.b64encode(data).decode()
for i in range(0, len(enc), 76):
    print(enc[i:i + 76])
print("== END cov2d_Q_205.npz base64")
' "$F" "$WANT"
r=$?
echo "read rc=$r $(ts)"
echo "== 3. stat after $(ts)"
after=$(stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$F"); echo "$after"
if [ "$before" = "$after" ]; then echo "stat: byte-identical before and after"; else echo "STOP: the file's stat moved during the read"; finish 4; fi
[ "$r" -eq 0 ] || finish "$r"
finish 0
