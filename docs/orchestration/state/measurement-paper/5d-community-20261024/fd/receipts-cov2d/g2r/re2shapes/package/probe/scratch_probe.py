import glob, hashlib, os, sys
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
B = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023"
runs = {}
for r in ("partc", "partc-r2"):
    ds = glob.glob(f"{B}/{r}/periods_ns/tmp/tmp*")
    print(r, "mkdtemp dirs:", [os.path.basename(d) for d in ds])
    runs[r] = ds[0] if len(ds) == 1 else None
a, b = runs["partc"], runs["partc-r2"]
na, nb = os.path.basename(a).encode(), os.path.basename(b).encode()
for f in sorted(set(os.listdir(a)) | set(os.listdir(b))):
    x, y = rd(f"{a}/{f}"), rd(f"{b}/{f}")
    xn = x.replace(na, nb).replace(b"/2d-closeout-re2-20261023/partc/", b"/2d-closeout-re2-20261023/partc-r2/").replace(b"/deploy-e079ff05", b"/deploy-903fb78b")
    print(f, "raw_equal" if x == y else ("equal_after_names" if xn == y else "DIFFER"), len(x), len(y),
          "contains_dirname" if nb in y else "", hashlib.sha256(y).hexdigest()[:16])
