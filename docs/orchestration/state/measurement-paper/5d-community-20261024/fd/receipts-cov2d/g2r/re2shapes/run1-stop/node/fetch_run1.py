# Read-only O_NOATIME fetch of the first RE-2-shapes run's records ($W = cov2d-re2shapes-20261114) as one tar on stdout,
# with a sha256 list of every file in $W except the deploy clone. Writes nothing on the node.
import hashlib, io, os, sys, tarfile
W = "/pscratch/sd/j/josephrb/cov2d-re2shapes-20261114"
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
take = ["c0-sums.json", "c0-determinism.json", "stage.sha256", "c0.g2r_driver.json", "c0/SHA256SUMS", "c0/chain.json",
        "c0/receipts/receipt_model_chi2.json", "logs/c0.out", "logs/c0-determinism.out", "logs/run-identity.out",
        "logs/connect.log", "c0/logs/rollup.log", "c0/logs/steps.tsv", "c0/logs/run.txt"]
sums = []
for root, dirs, files in os.walk(W):
    dirs[:] = sorted(d for d in dirs if not (root == W and d.startswith("deploy-")))
    for f in sorted(files):
        p = os.path.join(root, f)
        sums.append(f"{hashlib.sha256(rd(p)).hexdigest()}  {os.path.relpath(p, W)}")
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w") as t:
    for rel in take + ["NODE-SHA256"]:
        data = ("\n".join(sums) + "\n").encode() if rel == "NODE-SHA256" else rd(os.path.join(W, rel))
        ti = tarfile.TarInfo(rel); ti.size = len(data); t.addfile(ti, io.BytesIO(data))
sys.stdout.buffer.write(buf.getvalue())
