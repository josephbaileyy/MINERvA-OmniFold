import io, os, sys, tarfile, glob
R = "/pscratch/sd/j/josephrb/ref-c2c1-20261106/read-2"
files = [R + "/" + n for n in ("read.log", "read.done", "read.time", "read.stdout", "readout.json")]
files += sorted(p for p in glob.glob(R + "/logs-read/*") if os.path.isfile(p))
listing = "".join(f"{os.stat(p).st_size} {p}\n" for p in sorted(glob.glob(R + "/inputs/*")))  # stat only: the staged inputs are not copied
out = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")
for p in files:
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f: data = f.read()
    ti = tarfile.TarInfo(os.path.relpath(p, R)); ti.size = len(data); ti.mtime = int(os.stat(p).st_mtime); ti.mode = 0o644
    out.addfile(ti, io.BytesIO(data))
b = listing.encode(); ti = tarfile.TarInfo("inputs-listing.txt"); ti.size = len(b); out.addfile(ti, io.BytesIO(b))
out.close(); sys.stderr.write(f"{len(files) + 1} files\n")
