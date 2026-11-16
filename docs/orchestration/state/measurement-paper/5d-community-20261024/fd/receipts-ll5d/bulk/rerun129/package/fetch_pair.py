# After the rerun job ends: one read-only pass on a login node (python3.6), every read O_NOATIME, nothing written there.
# argv[1] = "sha" prints "sha256  relpath" lines; "tar" writes a tar stream of the same files to stdout.
# The files: the 20 originals in $U (orig/<name>), the rerun's products and sidecar in $UO (rerun/<name>), and the
# rerun's own records under $W (w/<relpath>). The 20 names come from $W/rerun-lanes.tsv, the 4 lanes the connect split
# from the bulk's pinned partition row (node 09 lane 4).
#     ssh saul.nersc.gov '/usr/bin/python3 - sha' < fetch_pair.py > node-sha256.raw.txt
import glob, hashlib, io, os, sys, tarfile
P = "/pscratch/sd/j/josephrb"
U, UO, W = P + "/ll5d-unfolds-r2", P + "/ll5d-unfolds-rerun129-r1", P + "/ll5d-rerun129-r1"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 22)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
rows = [l.split("\t") for l in rd(W + "/rerun-lanes.tsv").decode().splitlines() if l and not l.startswith("#")]
assert len(rows) == 4 and all(r[2:4] == ["ar23", "toy"] for r in rows), rows
names = ["ll5d_ar23_toy_%s.npz" % it for r in rows for it in r[4].strip().split(",")]
assert len(names) == 20 and len(set(names)) == 20
files = [("orig/" + n, U + "/" + n) for n in names]
files += [("rerun/" + os.path.basename(p), p) for p in sorted(glob.glob(UO + "/*"))]
files += [("w/" + os.path.relpath(p, W), p) for pat in ("rerun-lanes.tsv", "bulk-09-4.tsv", "bound.sha256", "atime-pre.tsv",
          "sbatch-ll5d-rerun129.sh", "logs/*", "lanes/*") for p in sorted(glob.glob(W + "/" + pat)) if os.path.isfile(p)]
if sys.argv[1] == "sha":
    for rel, p in files:
        print("%s  %s" % (hashlib.sha256(rd(p)).hexdigest(), rel))
    print("# files %d host %s" % (len(files), os.uname()[1]))
else:
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as t:
        for rel, p in files:
            b = rd(p); ti = tarfile.TarInfo(rel); ti.size = len(b); ti.mtime = 0
            t.addfile(ti, io.BytesIO(b))
