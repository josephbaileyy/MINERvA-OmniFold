# Read-only O_NOATIME fetch of RE-2-shapes run 2's records ($W = cov2d-re2shapes-20261115) as one tar on stdout, with a
# sha256 list of every file in $W except the deploy clone. Writes nothing on the node. The g2r arm's set mirrors what
# partc_r2/partc-r2/ committed for partc-r2 (records, logs, small JSON and text; the npz/ROOT products are listed by
# sha256 only, except the fig6/7 PDFs); budget_Q.json, s5.json and cov2d_Q_205.json are gzipped as partc-r2's were.
import gzip, hashlib, io, os, sys, tarfile
W = "/pscratch/sd/j/josephrb/cov2d-re2shapes-20261115"
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
top = ["c0-sums.json", "c0-determinism.json", "c1.json", "stage.sha256", "out.sha256", "c0.g2r_driver.json", "g2r.g2r_driver.json",
       "logs/c0.out", "logs/c0-determinism.out", "logs/c1.out", "logs/connect.log", "logs/run-identity.out", "logs/run-g2r.out",
       "c0/SHA256SUMS", "c0/receipts/receipt_model_chi2.json", "c0/logs/rollup.log", "c0/logs/steps.tsv", "c0/logs/run.txt"]
g = []
for root, dirs, files in os.walk(f"{W}/g2r"):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), f"{W}/g2r")
        if rel.split("/")[0] in ("tmp", "mpl", "periods_ns") or rel.endswith((".npz", ".root", ".png")):
            continue
        if rel.endswith(".pdf") and not rel.startswith("fig67/"):   # the fig6/7 PDFs only (print-ready inputs)
            continue
        g.append("g2r/" + rel)
sums = []
for root, dirs, files in os.walk(W):
    dirs[:] = sorted(d for d in dirs if not (root == W and d.startswith("deploy-")))
    for f in sorted(files):
        p = os.path.join(root, f)
        sums.append(f"{hashlib.sha256(rd(p)).hexdigest()}  {os.path.relpath(p, W)}")
buf = io.BytesIO()
GZ = ("g2r/outA/budget_Q.json", "g2r/s5/s5.json", "g2r/outA/cov2d_Q_205.json")
with tarfile.open(fileobj=buf, mode="w") as t:
    for rel in top + sorted(g) + ["NODE-SHA256"]:
        if rel == "NODE-SHA256":
            data = ("\n".join(sums) + "\n").encode()
        else:
            data = rd(os.path.join(W, rel))
            if rel in GZ:
                z = io.BytesIO()
                with gzip.GzipFile(fileobj=z, mode="wb", mtime=0) as gz:   # python 3.6 on the node: no compress(mtime=)
                    gz.write(data)
                data = z.getvalue(); rel += ".gz"
        ti = tarfile.TarInfo(rel); ti.size = len(data); t.addfile(ti, io.BytesIO(data))
sys.stdout.buffer.write(buf.getvalue())
