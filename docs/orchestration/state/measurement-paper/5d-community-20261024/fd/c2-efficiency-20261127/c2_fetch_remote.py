"""C2-EFF remote reader (runs on a NERSC login node, fed on stdin by c2_fetch.sh; Python 3.6 compatible).

Reads, through O_NOATIME|O_NOFOLLOW only, REF-C2C1's c2 units (c2_replica_b1..b300 and c2_central, .npz and .done)
and the read-2 staged E_R copies 001..301_xsec.root, and streams them as an uncompressed tar on stdout. The last tar
member is MANIFEST.tsv: name, size, sha256, atime_ns before, atime_ns after, mtime_ns. It writes nothing on the
cluster: no file, no directory, no cache (run as `python3 -I -B -`).

Fail-closed: any missing, non-regular, symlinked, foreign-owned or empty file, any change of size, mtime, inode or
atime between the first lstat and the last, or any read error exits 9 before MANIFEST.tsv is written, so the tar on
the laptop has no manifest and the verifier refuses it. The last stderr line on success is exactly
"FETCH-DONE 903 files".

argv: UNITS_DIR INPUTS_DIR (the wrapper passes the two fixed paths).
"""
import hashlib
import io
import os
import socket
import stat
import sys
import tarfile
import time

N_REP = 300
N_FILES = 2 * N_REP + 2 + (N_REP + 1)  # replica npz+done, central npz+done, 301 xsec.root = 903


def fail(msg):
    sys.stderr.write("FETCH-REFUSED: %s\n" % msg)
    sys.stderr.flush()
    os._exit(9)


def expected(units, inputs):
    out = []
    for b in range(1, N_REP + 1):
        for ext in (".npz", ".done"):
            out.append(("units/c2_replica_b%d%s" % (b, ext), os.path.join(units, "c2_replica_b%d%s" % (b, ext))))
    for ext in (".npz", ".done"):
        out.append(("units/c2_central%s" % ext, os.path.join(units, "c2_central%s" % ext)))
    for i in range(1, N_REP + 2):
        out.append(("inputs/%03d_xsec.root" % i, os.path.join(inputs, "%03d_xsec.root" % i)))
    return out


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
    if len(argv) != 3:
        fail("usage: c2_fetch_remote.py UNITS_DIR INPUTS_DIR")
    noatime = getattr(os, "O_NOATIME", None)
    if noatime is None:
        fail("O_NOATIME is not available here: refusing a plain read")
    flags = os.O_RDONLY | noatime | os.O_NOFOLLOW
    uid = os.getuid()
    files = expected(argv[1], argv[2])
    if len(files) != N_FILES or len(set(n for n, _ in files)) != N_FILES:
        fail("the expected list is not %d distinct names" % N_FILES)
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    before = [snap(p, uid) for _, p in files]
    rows = []
    tar = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
    for (name, path), st in zip(files, before):
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
    for (name, path), st, row in zip(files, before, rows):
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
