# One read-only pass (python3.6, O_NOATIME) over $O/readout/{data,G18,AR23}: "sha" prints sha256 lines, "tar" streams.
import glob, hashlib, io, os, sys, tarfile
O = "/pscratch/sd/j/josephrb/cov2d-g2r-20261112"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 22)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
files = sorted(p for ph in ("data", "G18", "AR23") for p in glob.glob(O + "/readout/%s/*" % ph) if os.path.isfile(p))
rel = lambda p: os.path.relpath(p, O)
if sys.argv[1] == "sha":
    for p in files: print("%s  %s" % (hashlib.sha256(rd(p)).hexdigest(), rel(p)))
    print("# files %d host %s" % (len(files), os.uname()[1]))
else:
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as t:
        for p in files:
            b = rd(p); ti = tarfile.TarInfo(rel(p)); ti.size = len(b); ti.mtime = 0; t.addfile(ti, io.BytesIO(b))
