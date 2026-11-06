import io, os, sys, tarfile, glob
O = "/pscratch/sd/j/josephrb/ref-c2c1-20261106"; L = O + "/logs-completion"
files = sorted(p for p in glob.glob(L + "/*") if os.path.isfile(p))
files += [O + "/refc2c1_completion_job.sbatch", O + "/REPLICAS-DONE-j4"]
out = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")
for p in files:
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f: data = f.read()
    ti = tarfile.TarInfo(os.path.relpath(p, O)); ti.size = len(data); ti.mtime = int(os.stat(p).st_mtime); ti.mode = 0o644
    out.addfile(ti, io.BytesIO(data))
out.close(); sys.stderr.write(f"{len(files)} files\n")
