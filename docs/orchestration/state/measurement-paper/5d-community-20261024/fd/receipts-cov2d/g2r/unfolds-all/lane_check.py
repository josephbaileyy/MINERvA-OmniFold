# Read-only node check of the 12 G2R unfold jobs (2026-11-14), python3.6 on a login node, every read O_NOATIME.
# Against $O/tables/runs_g2r.tsv: for each lane with a walls file, its walls labels and its SHA256SUMS labels equal the
# table's labels for that lane, with no duplicates; every walls rc column is 0; every out/<label>/xsec.root exists.
import os, collections
O = "/pscratch/sd/j/josephrb/cov2d-g2r-20261112"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); b = b""
    while True:
        c = os.read(fd, 1 << 20)
        if not c: break
        b += c
    os.close(fd); return b.decode()
rows = [l.split("\t") for l in rd(O + "/tables/runs_g2r.tsv").splitlines()]
h, rows = rows[0], rows[1:]; L, LAB = h.index("lane"), h.index("label")
want = collections.defaultdict(list)
for r in rows: want[r[L]].append(r[LAB])
print("host", os.uname()[1], "table runs", len(rows), "lanes", len(want))
bad = 0; tot = 0; nz = []
for lane in sorted(want):
    if not os.path.exists(O + "/walls.%s.tsv" % lane):
        print("no walls file for lane", lane, "runs", want[lane]); continue
    W = [l.split("\t") for l in rd(O + "/walls.%s.tsv" % lane).splitlines()]
    S = [l.split() for l in rd(O + "/SHA256SUMS.%s" % lane).splitlines()]
    wl = [w[0] for w in W]; sl = [s[1].split("/")[0] for s in S]
    nz += [(lane, w) for w in W if w[3] != "0"]
    ok = sorted(wl) == sorted(want[lane]) and sorted(sl) == sorted(want[lane]) and len(set(wl)) == len(wl)
    ok = ok and all(os.path.exists(O + "/out/%s/xsec.root" % x) for x in want[lane])
    tot += len(W)
    print("lane %-10s runs %2d walls %2d sums %2d %s" % (lane, len(want[lane]), len(wl), len(sl), "ok" if ok else "MISMATCH"))
    bad += not ok
print("walls lines", tot, "mismatched lanes", bad, "nonzero rc", nz)
print("LANE-CHECK", "PASS" if bad == 0 and not nz and tot == 527 else "FAIL")
