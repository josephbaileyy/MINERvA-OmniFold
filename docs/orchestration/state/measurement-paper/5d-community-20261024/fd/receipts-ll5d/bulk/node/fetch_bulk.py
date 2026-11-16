# One read-only pass (python3.6, O_NOATIME) over the LL5D bulk's namespace (not its deploy clone) and the bulk jobs'
# atime sidecars in $U: "sha" prints sha256 lines, "tar" streams the same files (paths relative: w/... and u/...).
import glob, hashlib, io, os, sys, tarfile
W = "/pscratch/sd/j/josephrb/ll5d-bulk-r1"; U = "/pscratch/sd/j/josephrb/ll5d-unfolds-r2"
IDS = ("61214597", "61214601", "61214604", "61214605", "61214607", "61214609", "61214610", "61214612", "61214614", "61214615")
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME); ch = []
    while True:
        c = os.read(fd, 1 << 22)
        if not c: break
        ch.append(c)
    os.close(fd); return b"".join(ch)
files = [("w/" + os.path.relpath(p, W), p) for pat in ("*", "logs/*", "lanes/*") for p in sorted(glob.glob(W + "/" + pat)) if os.path.isfile(p)]
files += [("u/" + os.path.basename(p), p) for p in sorted(glob.glob(U + "/atime-*.json")) if any("-%s-" % i in p for i in IDS)]
if sys.argv[1] == "sha":
    for rel, p in files: print("%s  %s" % (hashlib.sha256(rd(p)).hexdigest(), rel))
    print("# files %d host %s" % (len(files), os.uname()[1]))
else:
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as t:
        for rel, p in files:
            b = rd(p); ti = tarfile.TarInfo(rel); ti.size = len(b); ti.mtime = 0; t.addfile(ti, io.BytesIO(b))
