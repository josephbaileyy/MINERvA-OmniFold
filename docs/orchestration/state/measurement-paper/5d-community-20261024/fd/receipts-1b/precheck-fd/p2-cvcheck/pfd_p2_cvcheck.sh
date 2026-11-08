#!/bin/bash
# 1B pre-check Part 1, before P3: P2's three CV products against the staged derivation CV, bit for bit (the director's
# go on coverage-5b-audit's optional check). Login node, 0 node-h. Fence first; then O_NOATIME reads of
# $V/stage/derivation/fd1b_derivation_CV.npz and of $V/unf/fd1b_pfd_{A,B,Dnom}_CV.npz, each sha256 printed; per mode,
# dtype, shape and np.array_equal on xsec_flat, and on xtrue_flat where both sides have it, with the first differing
# index. Any difference is a STOP (rc 4). It writes nothing. Launched from a /dev/shm copy of itself ($1).
SELF=$1
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== pfd-p2-cvcheck rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== fence (allowed names: rs1_* and ens1_*; anything else refuses)"
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
printf '%s\n' "$out"
bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "squeue rc=$frc; refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
echo "== CV bitwise"
env -u PYTHONPATH "$PY" -I - "$V" <<'PYEOF'
import hashlib, io, os, sys
import numpy as np
V = sys.argv[1]
def read(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    chunks = []
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    data = b"".join(chunks)
    print(f"read {path} sha256 {hashlib.sha256(data).hexdigest()} bytes {len(data)} (O_NOATIME)")
    return np.load(io.BytesIO(data), allow_pickle=False)
ref = read(f"{V}/stage/derivation/fd1b_derivation_CV.npz")
print("reference keys:", sorted(ref.files))
failures = 0
for mode in ("A", "B", "Dnom"):
    z = read(f"{V}/unf/fd1b_pfd_{mode}_CV.npz")
    for key in ("xsec_flat", "xtrue_flat"):
        if key not in z.files or key not in ref.files:
            print(f"{mode} {key}: not on both sides (product {key in z.files}, reference {key in ref.files})")
            if key == "xsec_flat":
                failures += 1
            continue
        a, r = z[key], ref[key]
        same_dtype, same_shape = a.dtype == r.dtype, a.shape == r.shape
        equal = bool(same_dtype and same_shape and np.array_equal(a, r))
        first = None
        if same_shape and not equal:
            diff = np.flatnonzero(a.ravel() != r.ravel())
            first = int(diff[0]) if diff.size else None
        print(f"{mode} {key}: dtype {a.dtype} vs {r.dtype} ({same_dtype}); shape {a.shape} vs {r.shape} ({same_shape}); "
              f"array_equal {equal}; first differing index {first}")
        failures += not equal
print("CV BITWISE:", "PASS" if failures == 0 else f"FAIL ({failures})")
sys.exit(0 if failures == 0 else 4)
PYEOF
c=$?
case "$c" in 0) ;; 4) echo "STOP: a mode's CV product differs from the derivation CV (reported unrepaired; P3 waits)" ;; *) echo "STOP: the check itself failed (rc $c); no comparison was made" ;; esac
finish "$c"
