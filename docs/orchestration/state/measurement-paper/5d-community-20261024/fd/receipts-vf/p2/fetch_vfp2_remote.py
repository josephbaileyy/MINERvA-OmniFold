# V_F Phase 2's read-only fetch (FD-VF-ADDITION-DECLARATION.md section 4.2; FD-VF BINDING 2), run on login02 by
# fetch-vfp2.sh with the bound list on stdin: each listed file, in order, is opened O_NOATIME, its size checked against
# the list by fstat before any byte is sent, then streamed into a tar on stdout (member name = path under
# /pscratch/sd/j/josephrb/) while hashed; a size or sha256 that is not the list's stops with exit 9. Nothing is written
# on the cluster; messages go to stderr only. Python 3.6 compatible (the login node's /usr/bin/python3).
import hashlib
import os
import stat
import sys
import tarfile

BASE = "/pscratch/sd/j/josephrb/"
NEVER = ("universes_full.root", "bkg_dump.npz", "data_b-_j-.npz")   # never read (route (1); the EVW5D watch)
FIELDS = ["path", "sha256", "pin_source", "size_bytes", "reader_file_line", "recompute"]


def stop(why, rc=9):
    sys.stderr.write("STOP fetch: %s\n" % why)
    sys.stderr.flush()
    sys.exit(rc)


class Hashing(object):
    """A read-only file object that hashes what tarfile reads from it."""

    def __init__(self, fd):
        self.fd, self.h, self.n = fd, hashlib.sha256(), 0

    def read(self, k=-1):
        b = os.read(self.fd, k if k and k > 0 else 1 << 22)
        self.h.update(b)
        self.n += len(b)
        return b


def open_nofollow(path):
    """Opens path with no symlink in any component below BASE: each directory O_DIRECTORY|O_NOFOLLOW relative to its
    parent's descriptor, the file O_NOATIME|O_NOFOLLOW|O_NONBLOCK (a FIFO is refused by the S_ISREG check, not waited
    on). A symlink anywhere below BASE refuses, so no link's own atime moves."""
    parts = path[len(BASE):].split("/")
    try:
        d = os.open(BASE, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as e:
        stop("cannot open %s: %s" % (BASE, e))
    try:
        for comp in parts[:-1]:
            try:
                nd = os.open(comp, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=d)
            except OSError as e:
                stop("%s: directory component %r is not a plain directory: %s" % (path, comp, e))
            os.close(d)
            d = nd
        try:
            return os.open(parts[-1], os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=d)
        except OSError as e:
            stop("cannot open %s O_NOATIME|O_NOFOLLOW: %s" % (path, e))
    finally:
        os.close(d)


def main():
    if not hasattr(os, "O_NOATIME"):
        stop("this platform has no O_NOATIME", 2)
    lines = sys.stdin.read().splitlines()
    if not lines or lines[0].split("\t") != FIELDS:
        stop("the list's header is not the bound one")
    rows = [ln.split("\t") for ln in lines[1:] if ln]
    if any(len(r) != 6 for r in rows) or len(set(r[0] for r in rows)) != len(rows):
        stop("the list is malformed or repeats a path")
    tf = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
    total = 0
    for path, sha, _, size, _, _ in rows:
        if not path.startswith(BASE) or ".." in path.split("/"):
            stop("%s is not under %s" % (path, BASE))
        if os.path.basename(path) in NEVER or path.endswith(NEVER):
            stop("%s is a file the fetch never reads" % path)
        fd = open_nofollow(path)
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode):
                stop("%s is not a regular file" % path)
            if st.st_size != int(size):
                stop("%s is %d bytes, listed %s" % (path, st.st_size, size))
            ti = tarfile.TarInfo(path[len(BASE):])
            ti.size, ti.mtime, ti.mode = st.st_size, int(st.st_mtime), 0o600
            src = Hashing(fd)
            tf.addfile(ti, src)
            if src.n != st.st_size or src.h.hexdigest() != sha:
                stop("%s: sha256 %s over %d bytes, pinned %s" % (path, src.h.hexdigest(), src.n, sha))
        finally:
            os.close(fd)
        total += int(size)
    tf.close()
    sys.stdout.buffer.flush()
    sys.stderr.write("fetch done: %d files, %d bytes, every size and sha256 the list's\n" % (len(rows), total))


main()
