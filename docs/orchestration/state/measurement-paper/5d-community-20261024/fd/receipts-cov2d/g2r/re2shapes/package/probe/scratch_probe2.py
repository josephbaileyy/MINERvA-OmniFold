import difflib, glob, os, json
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
a = glob.glob(f"{B}/partc/periods_ns/tmp/tmp*")[0]; b = glob.glob(f"{B}/partc-r2/periods_ns/tmp/tmp*")[0]
x, y = rd(f"{a}/inj.json").decode(), rd(f"{b}/inj.json").decode()
xs, ys = json.dumps(json.loads(x), indent=1).splitlines(), json.dumps(json.loads(y), indent=1).splitlines()
for ln in list(difflib.unified_diff(xs, ys, lineterm="", n=0))[:30]: print(ln[:220])
