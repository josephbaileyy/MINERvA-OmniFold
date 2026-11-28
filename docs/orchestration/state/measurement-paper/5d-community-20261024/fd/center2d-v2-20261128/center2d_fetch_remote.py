"""CENTER2D remote reader (runs on a NERSC login node, fed on stdin by center2d_fetch.sh; Python 3.6 compatible).

Reads the 16 files of CENTER2D-DECLARATION.md section 3 through O_RDONLY|O_NOATIME|O_NOFOLLOW only, and streams them as
an uncompressed tar on stdout. The last tar member is MANIFEST.tsv: name, size, sha256, atime_ns before, atime_ns after,
mtime_ns. The before and after stats are taken by this one process on this one node (never compared across nodes or
jobs). It writes nothing on the cluster: no file, no directory, no cache (run as `python3 -I -B -`).

Fail-closed: any missing, non-regular, symlinked, foreign-owned or empty file, any change of size, mtime, inode or atime
between the first lstat and the last, or any read error exits 9 before MANIFEST.tsv is written, so the tar on the laptop
has no manifest and the verifier refuses it. The last stderr line on success is exactly "FETCH-DONE 16 files".

argv: none (the 16 paths are fixed here; center2d.py's FETCH carries the same list and a test checks they are equal).
"""
import hashlib
import io
import os
import socket
import stat
import sys
import tarfile
import time

NS_G2R = "/pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout"
NS_RE2 = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023"
NS_C04 = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build"
S3_LABELS = ("BeamAngleX", "BeamAngleY", "MuonResolution", "MuonEnergyMINERvA", "MuonEnergyMINOS")
FILES = [
    ("g2r/data_g2r.npz", NS_G2R + "/data/data_g2r.npz"),
    ("g2r/blocks_g2r_AR23.npz", NS_G2R + "/AR23/blocks_g2r_AR23.npz"),
    ("g2r/blocks_g2r_G18.npz", NS_G2R + "/G18/blocks_g2r_G18.npz"),
    ("partc/cov2d_Q_205.npz", NS_RE2 + "/partc-r2/outA/cov2d_Q_205.npz"),
    ("partc/production_cov.npz", NS_RE2 + "/partc-r2/s5/production_cov.npz"),
] + [("partb/S3_%s%d.root" % (L, u), "%s/partb/out/S3_%s%d/xsec.root" % (NS_RE2, L, u))
     for L in S3_LABELS for u in (0, 1)] + [
    ("c04/minos_rescaled.npz", NS_C04 + "/minos_rescaled.npz"),
]
N_FILES = 16


def fail(msg):
    sys.stderr.write("FETCH-REFUSED: %s\n" % msg)
    sys.stderr.flush()
    os._exit(9)


def snap(path, uid):
    try:
        st = os.lstat(path)
    except OSError as e:
        fail("lstat %s: %s" % (path, e))
    if not stat.S_ISREG(st.st_mode):
        fail("%s is not a regular file (or is a symlink)" % path)
    if st.st_uid != uid:
        fail("%s is owned by uid %d, not %d" % (path, st.st_uid, uid))
    if st.st_size <= 0:
        fail("%s is empty" % path)
    return st


def main(argv):
    if len(argv) != 1:
        fail("usage: center2d_fetch_remote.py (no arguments)")
    noatime = getattr(os, "O_NOATIME", None)
    if noatime is None:
        fail("O_NOATIME is not available here: refusing a plain read")
    flags = os.O_RDONLY | noatime | os.O_NOFOLLOW
    uid = os.getuid()
    if len(FILES) != N_FILES or len(set(n for n, _ in FILES)) != N_FILES or len(set(p for _, p in FILES)) != N_FILES:
        fail("the file list is not %d distinct names and paths" % N_FILES)
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    before = [snap(p, uid) for _, p in FILES]
    rows = []
    tar = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
    for (name, path), st in zip(FILES, before):
        try:
            fd = os.open(path, flags)
        except OSError as e:
            fail("open %s with O_NOATIME: %s" % (path, e))
        with os.fdopen(fd, "rb") as f:
            fst = os.fstat(f.fileno())
            if (fst.st_ino, fst.st_dev, fst.st_size) != (st.st_ino, st.st_dev, st.st_size):
                fail("%s changed between lstat and open" % path)
            data = f.read()
        if len(data) != st.st_size:
            fail("%s: read %d bytes, expected %d" % (path, len(data), st.st_size))
        ti = tarfile.TarInfo(name)
        ti.size = len(data)
        ti.mtime = int(st.st_mtime)
        ti.mode = 0o644
        tar.addfile(ti, io.BytesIO(data))
        rows.append([name, len(data), hashlib.sha256(data).hexdigest(), st.st_atime_ns, st.st_mtime_ns])
    for (name, path), st, row in zip(FILES, before, rows):
        st2 = snap(path, uid)
        if (st2.st_ino, st2.st_size, st2.st_mtime_ns) != (st.st_ino, st.st_size, st.st_mtime_ns):
            fail("%s changed during the fetch" % path)
        if st2.st_atime_ns != st.st_atime_ns:
            fail("%s: atime moved (%d -> %d)" % (path, st.st_atime_ns, st2.st_atime_ns))
        row.insert(4, st2.st_atime_ns)
    head = "# host %s uid %d start %s end %s files %d\n" % (
        socket.gethostname(), uid, t0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), len(rows))
    body = "".join("%s\t%d\t%s\t%d\t%d\t%d\n" % tuple(r) for r in rows)
    m = (head + "name\tsize\tsha256\tatime_ns_before\tatime_ns_after\tmtime_ns\n" + body).encode()
    ti = tarfile.TarInfo("MANIFEST.tsv")
    ti.size = len(m)
    ti.mtime = int(time.time())
    ti.mode = 0o644
    tar.addfile(ti, io.BytesIO(m))
    tar.close()
    sys.stdout.buffer.flush()
    sys.stderr.write("FETCH-DONE %d files\n" % len(rows))
    sys.stderr.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
