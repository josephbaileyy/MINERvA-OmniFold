# Read-only evidence for the LL5D bulk's rc-8 and rc-129 calls (the director's items a, b, d, e, f, g; 2026-11-14).
# Runs on a login node (python3.6). Every file read is O_NOATIME; nothing is written on the node.
import os, re, glob, json, hashlib, datetime
W = "/pscratch/sd/j/josephrb/ll5d-bulk-r1"; U = "/pscratch/sd/j/josephrb/ll5d-unfolds-r2"
MAN = W + "/deploy/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt"
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 22)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
Z = lambda s: datetime.datetime.utcfromtimestamp(s).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
print("host", os.uname()[1], "utc", Z(datetime.datetime.utcnow().timestamp() if hasattr(datetime.datetime, "timestamp") else 0))
# (a)
st = os.stat(MAN); b = rd(MAN); st2 = os.stat(MAN)
print("(a) manifest", MAN)
print("    atime", st.st_atime_ns, Z(st.st_atime_ns / 1e9), "mtime", st.st_mtime_ns, Z(st.st_mtime_ns / 1e9), "ctime", Z(st.st_ctime_ns / 1e9), "size", st.st_size)
print("    sha256 (O_NOATIME)", hashlib.sha256(b).hexdigest(), "atime after read", st2.st_atime_ns, "unchanged" if st2.st_atime_ns == st.st_atime_ns else "MOVED")
# (d)
bs = rd(W + "/bound.sha256").decode()
print("(d) bound.sha256 sha256", hashlib.sha256(bs.encode()).hexdigest(), "lines", len(bs.splitlines()))
for l in bs.splitlines():
    if "inputs-sha256.txt" in l: print("    lists:", l)
# (b) log lines
for f in sorted(glob.glob(W + "/logs/ll5d_bulk_*.out")):
    t = rd(f).decode(errors="replace")
    s = re.search(r"^host=(\S+) job=(\d+) node=(\d+) start=(\S+)$", t, re.M)
    ok = [l for l in t.splitlines() if "inputs-sha256.txt" in l]
    print("(b)", os.path.basename(f), "start_line", s.group(4) if s else None, "|", ok)
# (e) every atime json from the bulk's job ids
ids = ("61214597", "61214601", "61214604", "61214605", "61214607", "61214609", "61214610", "61214612", "61214614", "61214615")
n = 0; moves = []
for f in sorted(glob.glob(U + "/atime-*.json")):
    if not any("-%s-" % i in f for i in ids): continue
    n += 1; d = json.loads(rd(f).decode())
    for p, v in d["files"].items():
        if v["atime_ns_first"] != v["atime_ns_now"]:
            moves.append((os.path.basename(f), p, v["atime_ns_first"], v["atime_ns_now"]))
print("(e) bulk atime json", n, "moves", len(moves), "paths", sorted({m[1] for m in moves}))
for m in moves: print("    MOVE", m[0], Z(m[2] / 1e9), "->", Z(m[3] / 1e9))
# (f) all npz
outs = []
for f in sorted(glob.glob(W + "/lanes/*.out")):
    for l in rd(f).decode().splitlines():
        if l.startswith('{"out": '): outs.append((os.path.basename(f), json.loads(l)["out"]))
npz = sorted(os.path.basename(p) for p in glob.glob(U + "/ll5d_*.npz"))
print("(f) npz", len(npz), "out lines", len(outs), "distinct", len({o for _, o in outs}))
missing = [o for _, o in outs if o not in npz]; print("    out lines without a file", missing)
extra = sorted(set(npz) - {o for _, o in outs})
for e in extra:
    s = os.stat(U + "/" + e); print("    EXTRA", e, "mtime", Z(s.st_mtime), "size", s.st_size)
H = {}
for e in npz: H[e] = hashlib.sha256(rd(U + "/" + e)).hexdigest()
with open(os.devnull, "w"): pass
print("(f) NPZ-SHA256 BEGIN")
for e in npz:
    s = os.stat(U + "/" + e); print("%s  %s  mtime=%s size=%d" % (H[e], e, Z(s.st_mtime), s.st_size))
print("(f) NPZ-SHA256 END")
# (g)
g = [o for f, o in outs if f == "node09-lane4.out"]
print("(g) node09-lane4 products", len(g))
for o in g:
    s = os.stat(U + "/" + o); print("    %s  %s  mtime=%s size=%d" % (H[o], o, Z(s.st_mtime), s.st_size))
