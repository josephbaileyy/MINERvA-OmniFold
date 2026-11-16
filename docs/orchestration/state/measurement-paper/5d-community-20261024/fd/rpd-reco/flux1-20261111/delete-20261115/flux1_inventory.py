#!/usr/bin/env python3
"""RPD-RECO flux connect 1, cleanup step A: a read-only inventory of the run's pscratch root, so that step B can delete
exactly what is declared. Python >= 3.6, stdlib only (the login node's /usr/bin/python3 is 3.6.15).

What it does:
- Walks ROOT (a literal path below) depth-first in sorted order. Every directory is opened with
  O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_NOATIME and listed through that descriptor (os.listdir(fd)); every entry is
  lstat'ed relative to it (dir_fd). No file's contents are read, no symlink is followed, nothing is written.
- Prints one line per entry outside clone/ (kind, bytes, path relative to ROOT, and a symlink's target), and for clone/
  only its counts, bytes and the sha256 of its own listing.
- Prints the sha256 of the whole canonical listing: one line per entry, "kind<TAB>bytes<TAB>relpath<TAB>target\\n",
  sorted by relpath, with kind f (regular file), d (directory), l (symlink) or o (anything else), target empty except
  for symlinks, and bytes 0 for directories. Step B recomputes it with the same code and must get the same digest.
- Checks: ROOT is a directory (not a symlink); every entry is on ROOT's device and owned by this uid; it reports any
  kind o and every symlink whose target resolves outside ROOT.
Exit: 0 inventory complete (the checks are reported, not enforced); 4 STOP (not a login node, ROOT missing or a
symlink, O_NOATIME unavailable).
Usage: /usr/bin/python3 -B flux1_inventory.py
"""
import hashlib
import os
import socket
import stat
import sys
import time

ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux-20261111"
CLONE = "clone"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def listing(root, noatime):
    """Returns (entries, problems). entries: sorted list of (relpath, kind, size, target, dev, uid)."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | noatime
    out, problems, stack = [], [], [""]
    while stack:
        rel = stack.pop()
        fd = os.open(os.path.join(root, rel) if rel else root, flags)
        try:
            names = sorted(os.listdir(fd))
            subdirs = []
            for n in names:
                st = os.lstat(n, dir_fd=fd)
                r = os.path.join(rel, n) if rel else n
                if stat.S_ISREG(st.st_mode):
                    kind, size, target = "f", st.st_size, ""
                elif stat.S_ISDIR(st.st_mode):
                    kind, size, target = "d", 0, ""
                    subdirs.append(r)
                elif stat.S_ISLNK(st.st_mode):
                    kind, size, target = "l", st.st_size, os.readlink(n, dir_fd=fd)
                else:
                    kind, size, target = "o", st.st_size, ""
                    problems.append("other kind of entry: %s mode %o" % (r, st.st_mode))
                out.append((r, kind, size, target, st.st_dev, st.st_uid))
            stack.extend(reversed(subdirs))
        finally:
            os.close(fd)
    out.sort(key=lambda e: e[0])
    return out, problems


def canon(entries):
    return "".join("%s\t%d\t%s\t%s\n" % (k, s, r, t) for r, k, s, t, _, _ in entries)


def main(root=ROOT, require_login=True, noatime=None):
    if noatime is None:
        noatime = getattr(os, "O_NOATIME", None)
        if noatime is None:
            print("STOP: os.O_NOATIME is not available")
            return 4
    host = socket.gethostname()
    print("inventory host %s python %s start %s root %s" % (host, sys.version.split()[0], now(), root))
    if require_login and not host.startswith("login"):
        print("STOP: not a login node: %s" % host)
        return 4
    if not os.path.lexists(root):
        print("STOP: %s does not exist" % root)
        return 4
    rst = os.lstat(root)
    if not stat.S_ISDIR(rst.st_mode):
        print("STOP: %s is not a directory (mode %o)" % (root, rst.st_mode))
        return 4
    t0 = time.time()
    entries, problems = listing(root, noatime)
    uid = os.getuid()
    for r, k, s, t, dev, u in entries:
        if dev != rst.st_dev:
            problems.append("on another device: %s" % r)
        if u != uid:
            problems.append("owned by uid %d: %s" % (u, r))
        if k == "l":
            dest = os.path.normpath(os.path.join(root, os.path.dirname(r), t))
            if not (dest == root or dest.startswith(root + "/")):
                problems.append("symlink pointing outside the root: %s -> %s" % (r, t))
    clone = [e for e in entries if e[0] == CLONE or e[0].startswith(CLONE + "/")]
    rest = [e for e in entries if not (e[0] == CLONE or e[0].startswith(CLONE + "/"))]
    print("root dev %d ino %d uid %d mode %o" % (rst.st_dev, rst.st_ino, rst.st_uid, rst.st_mode))
    for r, k, s, t, _, _ in rest:
        print("entry\t%s\t%d\t%s\t%s" % (k, s, r, t))
    kinds = {}
    for e in clone:
        kinds[e[1]] = kinds.get(e[1], 0) + 1
    print("clone/ entries %d (%s) bytes %d listing-sha256 %s" % (
        len(clone), " ".join("%s=%d" % kv for kv in sorted(kinds.items())), sum(e[2] for e in clone if e[1] == "f"),
        hashlib.sha256(canon(clone).encode()).hexdigest()))
    tops = {}
    for r, k, s, _, _, _ in entries:
        top = r.split("/", 1)[0]
        c = tops.setdefault(top, [0, 0])
        c[0] += 1
        c[1] += s if k == "f" else 0
    for top in sorted(tops):
        print("top %s entries %d bytes %d" % (top, tops[top][0], tops[top][1]))
    for p in problems:
        print("PROBLEM %s" % p)
    print("tree entries %d files %d bytes %d listing-sha256 %s problems %d seconds %.1f" % (
        len(entries), sum(1 for e in entries if e[1] == "f"), sum(e[2] for e in entries if e[1] == "f"),
        hashlib.sha256(canon(entries).encode()).hexdigest(), len(problems), time.time() - t0))
    print("INVENTORY :: DONE end %s (nothing was read but metadata; nothing was written or removed)" % now())
    return 0


if __name__ == "__main__":
    sys.exit(main())
