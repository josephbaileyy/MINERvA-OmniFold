# Stat-only overlap check before each G2R readout phase (the director's condition, 2026-11-14): the readout's inputs,
# by path (realpath) and by device:inode, against the 1146 LL5D protected paths of the bulk's atime-pre
# (/pscratch/sd/j/josephrb/ll5d-bulk-r1/atime-pre.tsv, sha256 908d3922..., read O_NOATIME). Inputs checked: every file
# under $O (/pscratch/sd/j/josephrb/cov2d-g2r-20261112: products, tables, prepare map), the MAT preflight file
# runEventLoopMC_1A.root, setup_salloc_env.sh and the MAT setup scripts the jobs hashed (logs/mat-*.json). Nothing is
# opened except the atime-pre list and the mat json (O_NOATIME); everything else is stat'ed. Exit 0 only with no hit.
#     ssh saul.nersc.gov '/usr/bin/python3 - <PH>' < readout_ovl.py
import hashlib, json, os, sys
P = "/pscratch/sd/j/josephrb"; O = P + "/cov2d-g2r-20261112"; A = P + "/MINERvA-OmniFold"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 20)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
pre = rd(P + "/ll5d-bulk-r1/atime-pre.tsv")
assert hashlib.sha256(pre).hexdigest().startswith("908d3922"), "the atime-pre list is not 908d3922"
ll = [l.split("\t", 1)[1] for l in pre.decode().splitlines()]
assert len(ll) == 1146
llr, lli = set(), set()
for p in ll:
    llr.add(os.path.realpath(p))
    try:
        s = os.stat(p); lli.add((s.st_dev, s.st_ino))
    except OSError:
        pass
inputs = []
for root, dirs, files in os.walk(O):
    for f in files:
        inputs.append(os.path.join(root, f))
mat = json.loads(rd(O + "/logs/mat-61226562.json").decode())
inputs += [A + "/2d-unfolding/baseline_flux/runEventLoopMC_1A.root", A + "/setup_salloc_env.sh"] + sorted(mat["setup_sha256"])
hits = []
for p in inputs:
    try:
        s = os.stat(p)
    except OSError:
        continue
    if os.path.realpath(p) in llr or (s.st_dev, s.st_ino) in lli:
        hits.append(p)
print("readout-ovl PH=%s host=%s: %d readout inputs (under $O %d, MAT %d) x 1146 LL5D paths (%d inodes): hits %s"
      % (sys.argv[1] if len(sys.argv) > 1 else "?", os.uname()[1], len(inputs), len(inputs) - 2 - len(mat["setup_sha256"]),
         2 + len(mat["setup_sha256"]), len(lli), hits))
print("READOUT-OVL", "PASS" if not hits else "STOP")
sys.exit(1 if hits else 0)
