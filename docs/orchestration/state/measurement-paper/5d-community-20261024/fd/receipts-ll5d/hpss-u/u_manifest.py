# Read-only manifest of $U = /pscratch/sd/j/josephrb/ll5d-unfolds-r2 for the bulk HPSS copy (the director's pin rulings of
# 2026-11-16): every regular file, sorted by name, read by os.open(O_RDONLY | O_NOATIME); "sha256<TAB>size<TAB>atime_ns
# before<TAB>atime_ns after<TAB>name" per line, then a summary line. Writes nothing.
import hashlib, os, sys
U = "/pscratch/sd/j/josephrb/ll5d-unfolds-r2"
names = sorted(n for n in os.listdir(U) if os.path.isfile(os.path.join(U, n)))
moved = 0
for n in names:
    p = os.path.join(U, n); a0 = os.stat(p).st_atime_ns
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256(); size = 0
    while True:
        b = os.read(fd, 1 << 24)
        if not b: break
        h.update(b); size += len(b)
    os.close(fd); a1 = os.stat(p).st_atime_ns; moved += a0 != a1
    print(f"{h.hexdigest()}\t{size}\t{a0}\t{a1}\t{n}")
print(f"# files {len(names)} atime_moved {moved}")
