"""B2: install slot 1's private genie_xsec product (SciSoft's G2111a00000) on a Perlmutter login node, once, verified.

Run by pg-node-launch.py as `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -` with this file on
stdin (state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md, step B2, approved; the director's answers 3 and 4).
Standard library only. Writes only under ROOT; nothing else.

0. Identity first (hostname login<NN>, /pscratch, /global/common, CVMFS). ROOT must not exist, and its parent must be
   on /pscratch; DBCONFIG_SHA256 must be filled (from the director's pin of PG's probe receipt).
1. Download URL with /usr/bin/curl (--proto =https) to ROOT/dl/, and hash it through its descriptor: it must be
   TARBALL_SHA256, or it is removed and the run STOPs.
2. Pass 1 over the tarball: every member's name, type, link target and sha256 must equal MEMBERS, and none may be
   missing or extra. Nothing is written in this pass.
3. Pass 2: the members are written beneath ROOT one by one (directories 0755, files with O_CREAT|O_EXCL|O_NOFOLLOW,
   links to their pinned targets). The download is then removed.
4. CVMFS's products/.upsfiles/dbconfig is copied byte for byte to ROOT/.upsfiles/dbconfig; its sha256 must be
   DBCONFIG_SHA256. Nothing else is authored in ROOT.
5. Everything under ROOT/genie_xsec and ROOT/.upsfiles is made read-only (files 0444, directories 0555), and the tree
   is checked again: exactly MEMBERS, each file's sha256, each link's target, nothing writable.

The last line is `PG-RESULT <json>` (schema covfix-pg-install/1), with the install date. Exit 0 on GO, 3 on STOP. A
STOP after step 1 leaves ROOT for the director to inspect; nothing is retried.

MEASURES: byte identity of the installed product. CANNOT AUTHORIZE: its use; the binary re-verifies every member.
"""
import datetime
import hashlib
import json
import os
import re
import socket
import stat
import subprocess
import sys
import tarfile

SCHEMA = "covfix-pg-install/1"
ROOT = "/pscratch/sd/j/josephrb/covfix-pg/products"
URL = ("https://scisoft.fnal.gov/scisoft/packages/genie_xsec/v3_04_00/"
       "genie_xsec-3.04.00-noarch-G2111a00000-k250-e1000.tar.bz2")
TARBALL_SHA256 = "ae159887772a54891fc4bddb189ab108d74c4a48db68c13ed7166524e8797590"
DBCONFIG_SRC = "/cvmfs/larsoft.opensciencegrid.org/products/.upsfiles/dbconfig"
DBCONFIG_SHA256 = None            # the director's pin, from PG's probe receipt (xsec.dbconfig.sha256)
CURL = "/usr/bin/curl"
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
MEMBERS_JSON = r'''{
 "members": {
  "genie_xsec/v3_04_00": {
   "mode": "0o755",
   "type": "dir"
  },
  "genie_xsec/v3_04_00.version": {
   "mode": "0o755",
   "type": "dir"
  },
  "genie_xsec/v3_04_00.version/NULL_G2111a00000-k250-e1000": {
   "mode": "0o644",
   "sha256": "0a46f15d8ecd39d7864aaee906c5f38a880013275809f4baf305b8dff60d51a0",
   "size": 456,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL": {
   "mode": "0o755",
   "type": "dir"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000": {
   "mode": "0o755",
   "type": "dir"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data": {
   "mode": "0o755",
   "type": "dir"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/README": {
   "mode": "0o644",
   "sha256": "4a2beead2f261240a4fed7f7d419d2d68c11bc1fa264faa7e129f8223a7ba7fd",
   "size": 2690,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/gxspl-FNALbig.xml.gz": {
   "mode": "0o777",
   "target": "gxspl-NUbig.xml.gz",
   "type": "symlink"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/gxspl-FNALsmall.xml": {
   "mode": "0o777",
   "target": "gxspl-NUsmall.xml",
   "type": "symlink"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/gxspl-NUbig.xml.gz": {
   "mode": "0o644",
   "sha256": "100791492718a525ccf9acaf9eb2b453e872b8efc139fef344e7a189ed5a8f2a",
   "size": 183432408,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/gxspl-NUsmall.xml": {
   "mode": "0o644",
   "sha256": "fa475f7f5066b314f177b10c4c821d76f2db072508be2734243a26544ef7ed1c",
   "size": 561654302,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/gxspl-freenuc.xml.gz": {
   "mode": "0o644",
   "sha256": "fdb326eda3188d82fb603053eb34a89f7ea32d1cdfa2024bd39476731a7fb46d",
   "size": 1442580,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/isotopes.cfg": {
   "mode": "0o644",
   "sha256": "8570db1561c2c41d8928f41f3318218a179cb029d9b5d90761e0f9cd350e4673",
   "size": 13025,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/reduce_gxspl.awk": {
   "mode": "0o755",
   "sha256": "ba64ba5a511fb2314dd1f12ec55a833ce0c257f35f0b8712004e42168c1b6368",
   "size": 3719,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/xsec_graphs.root": {
   "mode": "0o644",
   "sha256": "10707a2debcaf7e6e9174b0a4cdee2439ec3014e92e032885205e7a41129d271",
   "size": 245767846,
   "type": "file"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/ups": {
   "mode": "0o755",
   "type": "dir"
  },
  "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/ups/genie_xsec.table": {
   "mode": "0o644",
   "sha256": "15b0d8abab0abfcedcfa06d7b6552241fb5f1667619367c48457ccc2ebc88d76",
   "size": 752,
   "type": "file"
  }
 },
 "schema": "covfix-pg-members/1",
 "tarball": "genie_xsec-3.04.00-noarch-G2111a00000-k250-e1000.tar.bz2",
 "tarball_sha256": "ae159887772a54891fc4bddb189ab108d74c4a48db68c13ed7166524e8797590"
}'''
MEMBERS = json.loads(MEMBERS_JSON)


class Stop(Exception):
    pass


def identity():
    host = socket.gethostname()
    checks = {"hostname login<NN>": bool(re.fullmatch(r"login\d{2}", host)),
              "/pscratch": os.path.isdir("/pscratch"), "/global/common": os.path.isdir("/global/common"),
              "CVMFS products": os.path.isdir("/cvmfs/larsoft.opensciencegrid.org/products")}
    return {"host": host, "checks": checks, "pass": all(checks.values())}


def sha_fd(fd):
    h = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    for b in iter(lambda: os.read(fd, 1 << 20), b""):
        h.update(b)
    return h.hexdigest()


def sha_path(path):
    fd = os.open(path, os.O_RDONLY | O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Stop(f"{path} is not a regular file")
        return sha_fd(fd)
    finally:
        os.close(fd)


def scan(tarball, members):
    """Pass 1: [problems] of the tarball against the pinned members, writing nothing."""
    seen, probs = {}, []
    with tarfile.open(tarball, "r|bz2") as tf:
        for m in tf:
            n = m.name.rstrip("/")
            want = members.get(n)
            if want is None or n in seen:
                probs.append(f"member {n!r} is not pinned, or repeated")
                seen[n] = True
                continue
            seen[n] = True
            kind = "file" if m.isreg() else "dir" if m.isdir() else "symlink" if m.issym() else "other"
            if kind != want["type"]:
                probs.append(f"{n}: a {kind}, pinned as a {want['type']}")
            elif kind == "file":
                h = hashlib.sha256()
                f = tf.extractfile(m)
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
                if h.hexdigest() != want["sha256"]:
                    probs.append(f"{n}: sha256 differs from the pin")
            elif kind == "symlink" and m.linkname != want["target"]:
                probs.append(f"{n}: link target differs from the pin")
    probs += [f"missing: {n}" for n in sorted(set(members) - set(seen))]
    return probs


def extract(tarball, root, members):
    """Pass 2: write each pinned member beneath root, never following a link, never overwriting. The container
    genie_xsec is not a member of SciSoft's tarball (its first member is genie_xsec/v3_04_00), so it is made here."""
    if "genie_xsec" not in members:
        os.mkdir(os.path.join(root, "genie_xsec"), 0o755)
    with tarfile.open(tarball, "r|bz2") as tf:
        for m in tf:
            n = m.name.rstrip("/")
            want = members[n]
            path = os.path.join(root, n)
            parent = os.path.dirname(path)
            if os.path.realpath(parent) != parent:
                raise Stop(f"extract-link: {n}: its parent resolves through a link")
            if want["type"] == "dir":
                os.mkdir(path, 0o755)
            elif want["type"] == "file":
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | O_NOFOLLOW, 0o644)
                try:
                    f = tf.extractfile(m)
                    for b in iter(lambda: f.read(1 << 20), b""):
                        while b:
                            b = b[os.write(fd, b):]
                    os.fsync(fd)
                finally:
                    os.close(fd)
            elif want["type"] == "symlink":
                os.symlink(want["target"], path)


def check_tree(root, members, readonly):
    """[problems]: root/genie_xsec (a container, not a member) must hold exactly the members, each file's bytes and
    each link's target; root/.upsfiles exactly one dbconfig."""
    seen, probs = {}, []
    stack = [os.path.join(root, "genie_xsec")]
    st = os.lstat(stack[0])
    if not stat.S_ISDIR(st.st_mode) or (readonly and st.st_mode & 0o222):
        probs.append("tree-container: genie_xsec is not a read-only directory")
    while stack:
        d = stack.pop()
        for e in os.scandir(d):
            st = os.lstat(e.path)
            seen[os.path.relpath(e.path, root)] = st
            if stat.S_ISDIR(st.st_mode):
                stack.append(e.path)
    probs += [f"extra: {n}" for n in sorted(set(seen) - set(members))]
    probs += [f"missing: {n}" for n in sorted(set(members) - set(seen))]
    up = os.path.join(root, ".upsfiles")
    if not os.path.lexists(up):
        probs.append("upsfiles: .upsfiles is missing")
    elif not stat.S_ISDIR(os.lstat(up).st_mode):
        probs.append("upsfiles: .upsfiles is not a directory")
    else:
        ust, names = os.lstat(up), sorted(os.listdir(up))
        if (not stat.S_ISDIR(ust.st_mode) or names != ["dbconfig"]
                or not stat.S_ISREG(os.lstat(os.path.join(up, "dbconfig")).st_mode)
                or (readonly and (ust.st_mode & 0o222 or os.lstat(os.path.join(up, "dbconfig")).st_mode & 0o222))):
            probs.append(f"upsfiles: .upsfiles is not a {'read-only ' if readonly else ''}directory holding one dbconfig: {names}")
    for n in sorted(set(seen) & set(members)):
        st, m, p = seen[n], members[n], os.path.join(root, n)
        kind = ("dir" if stat.S_ISDIR(st.st_mode) else "file" if stat.S_ISREG(st.st_mode)
                else "symlink" if stat.S_ISLNK(st.st_mode) else "other")
        if kind != m["type"]:
            probs.append(f"{n}: a {kind}, pinned as a {m['type']}")
        elif kind == "file" and sha_path(p) != m["sha256"]:
            probs.append(f"{n}: sha256 differs from the pin")
        elif kind == "symlink" and os.readlink(p) != m["target"]:
            probs.append(f"{n}: link target differs from the pin")
        if readonly and kind != "symlink" and st.st_mode & 0o222:
            probs.append(f"{n}: writable")
    return probs


def make_readonly(top):
    for d, dirs, files in os.walk(top, topdown=False):
        for f in files:
            p = os.path.join(d, f)
            if not os.path.islink(p):
                os.chmod(p, 0o444)
        os.chmod(d, 0o555)


def install(root=ROOT, url=URL, tarball_sha=TARBALL_SHA256, members=None, dbconfig_src=DBCONFIG_SRC,
            dbconfig_sha=DBCONFIG_SHA256, ident=identity, fetch=None, scratch="/pscratch/"):
    members = members if members is not None else MEMBERS["members"]
    rec = {"schema": SCHEMA, "root": root, "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "tarball_sha256_pin": tarball_sha, "n_members_pinned": len(members), "stops": []}
    rec["identity"] = ident()
    try:
        if not rec["identity"]["pass"]:
            raise Stop("identity: not a Perlmutter login node; nothing was written")
        if not dbconfig_sha:
            raise Stop("dbconfig-unpinned: DBCONFIG_SHA256 is not filled; nothing was written")
        if os.path.lexists(root):
            raise Stop(f"root-exists: {root} already exists; nothing was written")
        parent = os.path.dirname(root)
        if not (parent + "/").startswith(scratch):
            raise Stop(f"root-place: {root} is not on {scratch}")
        a = parent                          # every existing ancestor is its own real path, on scratch, before any mkdir
        while not os.path.lexists(a):
            a = os.path.dirname(a)
        if os.path.realpath(a) != a or not ((a + "/").startswith(scratch) or scratch.startswith(a.rstrip("/") + "/")):
            raise Stop(f"root-place: {a} resolves to {os.path.realpath(a)}, not itself on {scratch}; nothing was written")
        os.makedirs(parent, exist_ok=True)                  # below the checked ancestor, every directory is new
        os.mkdir(root, 0o755)
        os.mkdir(os.path.join(root, "dl"), 0o700)
        tarball = os.path.join(root, "dl", os.path.basename(url))
        (fetch or (lambda u, out: subprocess.run([CURL, "-sf", "--proto", "=https", "-o", out, u], timeout=3600,
                                                 env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"}).returncode))(url, tarball)
        fd = os.open(tarball, os.O_RDONLY | O_NOFOLLOW)
        try:
            rec["tarball_sha256"] = sha_fd(fd)
        finally:
            os.close(fd)
        if rec["tarball_sha256"] != tarball_sha:
            os.unlink(tarball)
            raise Stop("download-sha: the download's sha256 differs from the pin; it was removed")
        rec["scan_problems"] = scan(tarball, members)
        if rec["scan_problems"]:
            raise Stop("members: the tarball's members differ from the pins; nothing was extracted")
        extract(tarball, root, members)
        os.unlink(tarball)
        os.rmdir(os.path.join(root, "dl"))
        sfd = os.open(dbconfig_src, os.O_RDONLY | O_NOFOLLOW)
        try:
            data = b"".join(iter(lambda: os.read(sfd, 1 << 20), b""))
        finally:
            os.close(sfd)
        rec["dbconfig_sha256"] = hashlib.sha256(data).hexdigest()
        if rec["dbconfig_sha256"] != dbconfig_sha:
            raise Stop("dbconfig-sha: CVMFS's dbconfig differs from the pin; it was not copied")
        os.mkdir(os.path.join(root, ".upsfiles"), 0o755)
        dfd = os.open(os.path.join(root, ".upsfiles", "dbconfig"), os.O_WRONLY | os.O_CREAT | os.O_EXCL | O_NOFOLLOW, 0o644)
        try:
            while data:
                data = data[os.write(dfd, data):]
            os.fsync(dfd)
        finally:
            os.close(dfd)
        make_readonly(os.path.join(root, "genie_xsec"))
        make_readonly(os.path.join(root, ".upsfiles"))
        rec["tree_problems"] = check_tree(root, members, readonly=True)
        if sha_path(os.path.join(root, ".upsfiles", "dbconfig")) != dbconfig_sha:
            rec["tree_problems"].append("the copied dbconfig differs from the pin")
        if sorted(os.listdir(root)) != [".upsfiles", "genie_xsec"]:
            rec["tree_problems"].append(f"{root} holds {sorted(os.listdir(root))}")
        if rec["tree_problems"]:
            raise Stop("tree: the installed tree differs from the pins")
        rec["install_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    except Stop as e:
        rec["stops"].append(str(e))
    except (OSError, tarfile.TarError, subprocess.SubprocessError) as e:
        rec["stops"].append(f"io-error: {type(e).__name__}: {e}")
    except Exception as e:                  # fail closed, with a reason no other test expects
        rec["stops"].append(f"internal-error: {type(e).__name__}")
    rec["verdict"] = "GO" if not rec["stops"] else "STOP"
    return rec


def main():
    rec = install()
    print(f"verdict {rec['verdict']} stops {rec['stops']}")
    print("PG-RESULT " + json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
