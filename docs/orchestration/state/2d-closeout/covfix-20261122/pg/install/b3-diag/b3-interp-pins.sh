#!/bin/bash
# Read-only pin probe for round 9's interpreter family (the director's ruling (ii), 2026-11-27): the programs ROOT
# 6.22's interpreter ran under gspl2root in B3 run 3 (b3-run3-diag2.out). For each path as it was executed: lstat
# (type, mode, size), each link in its chain (readlink), its real path, and the real file's size and sha256 (read
# O_NOATIME|O_NOFOLLOW, or O_NOFOLLOW alone where O_NOATIME is refused for a file not ours; a real path that is not a regular file is a STOP). Then the larsoft and minerva CVMFS
# revisions and root hashes. Nothing is written on NERSC. The output stays on the laptop beside this script.
set -u
OUT="$(dirname "$0")/b3-interp-pins.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import hashlib, json, os, socket, stat, sys
GCC = "/cvmfs/larsoft.opensciencegrid.org/products/gcc/v9_3_0/Linux64bit+3.10-2.17"
PATHS = ("/bin/sh", "/usr/bin/bash", "/usr/bin/ls", "/usr/bin/sed", "/usr/bin/ldd", "/lib/ld-linux.so.2",
         "/lib64/ld-linux-x86-64.so.2", GCC + "/bin/g++",
         GCC + "/bin/../libexec/gcc/x86_64-pc-linux-gnu/9.3.0/cc1plus")
def sha(p):
    h = hashlib.sha256()
    try:
        fd = os.open(p, os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW)
    except PermissionError:                     # O_NOATIME needs ownership (pg_verify's _open does the same)
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                return h.hexdigest()
            h.update(b)
    finally:
        os.close(fd)
print("host", socket.gethostname(), flush=True)
rows = {}
for p in PATHS:
    print("==", p)
    q, chain = p, []
    while True:
        st = os.lstat(q)
        print("   lstat", q, "type", oct(stat.S_IFMT(st.st_mode)), "mode", oct(stat.S_IMODE(st.st_mode)), "size", st.st_size)
        if not stat.S_ISLNK(st.st_mode) or len(chain) > 16:
            break
        t = os.readlink(q)
        chain.append(t)
        print("   link ->", t)
        q = os.path.join(os.path.dirname(q), t)
    real = os.path.realpath(p)
    st = os.lstat(real)
    if not stat.S_ISREG(st.st_mode):
        print("STOP:", real, "is not a regular file")
        sys.exit(1)
    rows[p] = {"real": real, "size": st.st_size, "sha256": sha(real)}
    print("   real", real, "size", st.st_size, "sha256", rows[p]["sha256"], flush=True)
print("== CVMFS")
for repo in ("/cvmfs/larsoft.opensciencegrid.org", "/cvmfs/minerva.opensciencegrid.org"):
    print("  ", repo, "revision", os.getxattr(repo, "user.revision").decode(), "root_hash",
          os.getxattr(repo, "user.root_hash").decode())
print("PINS", json.dumps(rows, sort_keys=True))
print("== end")
REMOTE
