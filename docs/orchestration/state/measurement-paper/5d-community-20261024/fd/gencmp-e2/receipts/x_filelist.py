"""HPSS deferral (RECORD-20261102-director-hpss-deferral.md ruling 1): one run directory's file list as it stands on
pscratch, deploy clone (and the attempted archive's hpss/) excluded: '<sha256>  <bytes>  <path relative to $P>' per
file, sorted, each file read O_NOATIME. Prints the list; the caller digests it. Usage: x_filelist.py <run dir name>."""
import hashlib, os, sys
P = "/pscratch/sd/j/josephrb"
d = sys.argv[1]
rows = []
for root, dirs, files in os.walk(os.path.join(P, d)):
    rel = os.path.relpath(root, P)
    dirs[:] = sorted(x for x in dirs if os.path.join(rel, x) not in (f"{d}/deploy", f"{d}/deploy-a1", f"{d}/deploy-a2", f"{d}/hpss"))
    for f in sorted(files):
        p = os.path.join(root, f)
        if os.path.islink(p):
            rows.append(f"{'symlink':<64}  {0:>12}  {os.path.relpath(p, P)} -> {os.readlink(p)}")
            continue
        h, n = hashlib.sha256(), 0
        fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
        with os.fdopen(fd, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""):
                h.update(b); n += len(b)
        rows.append(f"{h.hexdigest()}  {n:>12}  {os.path.relpath(p, P)}")
sys.stdout.write("".join(r + "\n" for r in sorted(rows, key=lambda r: r.split("  ")[-1])))
