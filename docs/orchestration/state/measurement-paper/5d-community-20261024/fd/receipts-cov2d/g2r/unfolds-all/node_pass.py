# Runs on a login node (python3.6): O_NOATIME over the G2R unfold jobs' files under $O.
# argv[1] = "sha" -> prints "sha256  relpath" lines; "tar" -> writes a tar stream to stdout.
import os, sys, glob, hashlib, tarfile, io
O = "/pscratch/sd/j/josephrb/cov2d-g2r-20261112"
JOBS = ["D_Ua", "D_Ub", "D_Uc", "D_Ud", "G18_Ua", "G18_Ub", "G18_Uc", "G18_Ud", "AR23_Ua", "AR23_Ub", "AR23_Uc", "AR23_Ud"]
pats = ["submissions.log", "tables/*", "inventory/*.jsonl", "out/*/xsec.root"]
for j in JOBS:
    pats += ["walls.%s.*.tsv" % j, "SHA256SUMS.%s.*" % j, "logs/check-%s-*.json" % j, "logs/cov2dg2r-%s-*.out" % j,
             "logs/bound-%s.sha256" % j, "logs/gate-%s-*.psv" % j, "logs/gate-%s-*.psv.gate.json" % j, "logs/order-%s.json" % j]
pats += ["logs/mat-6122%s.json" % x for x in ("5732", "6353", "6525", "6543", "6562", "6579", "6663", "6699", "6719", "6757", "6781", "6797")]
pats += ["logs/[ACO]_*.log"]
rel = sorted({os.path.relpath(p, O) for pat in pats for p in glob.glob(os.path.join(O, pat))})
inv = [r for r in rel if r.startswith("inventory/")]
rel = [r for r in rel if not (r.startswith("inventory/") and r[len("inventory/"):-len(".jsonl")].startswith("E_"))]
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 20)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
if sys.argv[1] == "sha":
    for r in rel:
        print("%s  %s" % (hashlib.sha256(rd(os.path.join(O, r))).hexdigest(), r))
    print("# files %d host %s" % (len(rel), os.uname()[1]))
else:
    out = sys.stdout.buffer
    with tarfile.open(fileobj=out, mode="w|") as t:
        for r in rel:
            b = rd(os.path.join(O, r)); ti = tarfile.TarInfo(r); ti.size = len(b); ti.mtime = 0
            t.addfile(ti, io.BytesIO(b))
