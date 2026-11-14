# One read-only pass (python3.6, O_NOATIME) over the null's W, excluding the deploy clone: "sha" prints sha256 lines,
# "tar" streams the same files.
import glob, hashlib, io, os, sys, tarfile
W = "/pscratch/sd/j/josephrb/ll5d-null-r1"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 22)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
files = sorted(p for pat in ("*", "logs/*") for p in glob.glob(W + "/" + pat) if os.path.isfile(p))
rel = lambda p: os.path.relpath(p, W)
if sys.argv[1] == "sha":
    for p in files: print("%s  %s" % (hashlib.sha256(rd(p)).hexdigest(), rel(p)))
    print("# files %d host %s" % (len(files), os.uname()[1]))
else:
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as t:
        for p in files:
            b = rd(p); ti = tarfile.TarInfo(rel(p)); ti.size = len(b); ti.mtime = 0; t.addfile(ti, io.BytesIO(b))
