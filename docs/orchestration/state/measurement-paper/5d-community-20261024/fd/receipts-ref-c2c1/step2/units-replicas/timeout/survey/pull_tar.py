import io, os, sys, tarfile, glob
O = "/pscratch/sd/j/josephrb/ref-c2c1-20261106"; L = O + "/logs-replicas"
files = []
for pat in ["connect.log", "connect.done", "refc2c1_replicas_submit.sh", "lanes.tsv", "cov2d-watch-paths.txt", "jobs.tsv",
            "submit-j*.out", "fd_c2c1r_*.out", "j*-lane*.log", "j*-lane*.time", "j*-watch-before.txt", "clone.log",
            "timeout-record/*"]:
    files += sorted(glob.glob(os.path.join(L, pat)))
files += [O + "/refc2c1_replicas_job.sbatch"] + [f"{O}/REPLICAS-TIMEOUT-j{j}" for j in range(4)]
files += sorted(glob.glob(O + "/units/c[12]_replica_b*.done"))
out = tarfile.open(fileobj=sys.stdout.buffer, mode="w|")
for p in files:
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f: data = f.read()
    ti = tarfile.TarInfo(os.path.relpath(p, O)); ti.size = len(data); ti.mtime = int(os.stat(p).st_mtime); ti.mode = 0o644
    out.addfile(ti, io.BytesIO(data))
out.close()
sys.stderr.write(f"{len(files)} files\n")
