#!/bin/bash
# T2B's fetch, the remote half (T2B-FD-GRADE-VARIANTS-DECLARATION.md §2; T2-BINDING-1.md ruling 3), on a Perlmutter
# login node: the five declared pscratch files, each by explicit path, read with O_NOATIME, stat before and after
# (size, mtime and atime must not move), sha256 of the bytes read, streamed as one uncompressed tar on stdout.
# Everything else (the per-file lines, the verdict) goes to stderr. Writes nothing on the cluster. Exit 0 only if all
# five were read whole with stat unchanged; else exit 4 (the local half then keeps nothing).
# Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
trap 'rm -f -- "$SELF"' EXIT
echo "fetch host=$(hostname) utc=$(date -u +%FT%TZ)" >&2
/usr/bin/python3 -I - <<'PY'
import hashlib, io, os, sys, tarfile
paths = [
    "/pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz",
    "/pscratch/sd/j/josephrb/cmodel5d-20261024/out/cmodel_5d.npz",
    "/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz",
    "/pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz",
    "/pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz",
]
ok = True
tf = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
for p in paths:
    try:
        s0 = os.stat(p)
        fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
        chunks = []
        while True:
            b = os.read(fd, 1 << 22)
            if not b:
                break
            chunks.append(b)
        os.close(fd)
        data = b"".join(chunks)
        s1 = os.stat(p)
    except OSError as e:
        print(f"FILE {p} ERROR {e}", file=sys.stderr)
        ok = False
        continue
    same = (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) == (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns)
    whole = len(data) == s0.st_size
    print(f"FILE {p} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()} "
          f"stat_unchanged={same} whole={whole} atime_ns={s0.st_atime_ns}", file=sys.stderr)
    ok &= same and whole
    ti = tarfile.TarInfo(os.path.basename(p))
    ti.size, ti.mode, ti.mtime = len(data), 0o600, int(s0.st_mtime)
    tf.addfile(ti, io.BytesIO(data))
tf.close()
sys.stdout.buffer.flush()
print("FETCH " + ("OK" if ok else "FAILED"), file=sys.stderr)
sys.exit(0 if ok else 4)
PY
