import os, sys, hashlib
for p in sys.argv[1:]:
    st0 = os.stat(p)
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    h = hashlib.sha256()
    with os.fdopen(fd, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 22), b''):
            h.update(b)
    st1 = os.stat(p)
    print(f"{h.hexdigest()}  {p}  size={st0.st_size} atime_unchanged={st0.st_atime_ns == st1.st_atime_ns}")
