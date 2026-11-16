# Read-only O_NOATIME fetch of the cr run's records as a tar on stdout, with a sha256 list of $W (deploy excluded).
import hashlib, io, os, sys, tarfile
W = "/pscratch/sd/j/josephrb/cov2d-cr-g2r-20261116"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        b = b""
        while True:
            c = os.read(fd, 1 << 20)
            if not c: break
            b += c
        return b
    finally: os.close(fd)
take = ["environment.txt", "out.sha256", "logs/connect.log", "control/overlap_refined.json", "control/overlap.out", "control/overlap.err",
        "control/compare.out", "g2r/overlap_refined.json", "g2r/overlap.out", "g2r/overlap.err"]
sums = []
for root, dirs, files in os.walk(W):
    dirs[:] = sorted(d for d in dirs if not (root == W and d in ("deploy", "tmp")))
    for f in sorted(files):
        p = os.path.join(root, f); sums.append(f"{hashlib.sha256(rd(p)).hexdigest()}  {os.path.relpath(p, W)}")
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w") as t:
    for rel in take + ["NODE-SHA256"]:
        data = ("\n".join(sums) + "\n").encode() if rel == "NODE-SHA256" else rd(os.path.join(W, rel))
        ti = tarfile.TarInfo(rel); ti.size = len(data); t.addfile(ti, io.BytesIO(data))
sys.stdout.buffer.write(buf.getvalue())
