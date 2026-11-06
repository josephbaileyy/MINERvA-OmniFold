import io, os, sys, tarfile
P = "/pscratch/sd/j/josephrb/ref-c2c1-20261106/tests-5938a167"
files = [f"{P}/{n}" for n in ("test.log", "test.done", "clone.log", "refc2c1_tests_login.sh", "watch-before.txt", "watch-after.txt")]
out = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")
for p in files:
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f: data = f.read()
    ti = tarfile.TarInfo(os.path.basename(p)); ti.size = len(data); ti.mtime = int(os.stat(p).st_mtime); ti.mode = 0o644
    out.addfile(ti, io.BytesIO(data))
out.close(); sys.stderr.write(f"{len(files)} files\n")
