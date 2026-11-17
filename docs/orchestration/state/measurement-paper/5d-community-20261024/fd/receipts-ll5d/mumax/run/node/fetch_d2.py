# Read-only O_NOATIME fetch of the D2 run's records as a tar on stdout, with a sha256 list of $W (deploy and tmp excluded).
import hashlib, io, os, sys, tarfile
W = "/pscratch/sd/j/josephrb/cov2d-mumax-20261116"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        b = b""
        while True:
            c = os.read(fd, 1 << 22)
            if not c: break
            b += c
        return b
    finally: os.close(fd)
take = ["environment.txt", "code.sha256", "inputs.txt", "atime-pre.txt", "atime-post.txt", "mumax.json", "out.sha256",
        "logs/mumax.log", "logs/connect.log", "logs/env.log"]
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
