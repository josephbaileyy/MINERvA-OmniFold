#!/bin/bash
# Remove B3's two stopped replay directories on pscratch (Joseph's approval of 2026-11-27, through the director). They
# hold no outputs: runs 1 and 2 failed closed before any GENIE step (pg-replay-g2111a.py.run1.out, .out). One connect,
# at a quiet point (no B3 run live). The output stays on the laptop beside this script.
#  1. identity: hostname login<NN>; covfix-pg is a real directory, not a link, and its real path is its literal path;
#  2. each target: lstat; refuse unless it is a real directory (not a link) whose real path is its literal path; refuse
#     if any process on this node has its cwd, root or an argument under it (other login nodes cannot be seen here);
#  3. covfix-pg's top-level listing, lstat of each entry (type, mode, size, inode, mtime_ns), taken before;
#  4. the manifest of each target: every entry under it (os.walk, following no link), its type and size, a link's
#     target (not followed), and each regular file's sha256 (read O_NOATIME). Refuse past 8 GiB in all;
#  5. delete only the two literal paths: make each directory under them u+rwx (rmtree cannot unlink from a read-only
#     directory), then shutil.rmtree, which on Linux works by fd and follows no link;
#  6. confirm: neither path exists (lexists), and covfix-pg's listing equals the one before less the two targets,
#     entry for entry (products/ and the rest untouched). Any failure is a nonzero exit, and the last line is not DONE.
set -u
OUT="$(dirname "$0")/replay-cleanup.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import hashlib, os, re, shutil, socket, stat, sys
ROOT = "/pscratch/sd/j/josephrb/covfix-pg"
TARGETS = (ROOT + "/replay-20261126T205214Z", ROOT + "/replay-20261126T211924Z")
CAP = 8 * 2 ** 30
def stop(msg):
    print("STOP:", msg, flush=True)
    sys.exit(1)
def walk_err(e):
    stop(f"walk: {e.filename}: {e.strerror}")
def real_dir(p):
    try:
        st = os.lstat(p)
    except OSError as e:
        stop(f"lstat {p}: {e.strerror}")
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        stop(f"{p} is not a real directory (mode {oct(st.st_mode)})")
    if os.path.realpath(p) != p:
        stop(f"{p}: its real path is {os.path.realpath(p)}")
    return st
def listing():
    out = {}
    for n in sorted(os.listdir(ROOT)):
        s = os.lstat(os.path.join(ROOT, n))
        out[n] = (stat.S_IFMT(s.st_mode), stat.S_IMODE(s.st_mode), s.st_size, s.st_ino, s.st_mtime_ns)
    return out
def sha(p):
    h = hashlib.sha256()
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW)
    try:
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                return h.hexdigest()
            h.update(b)
    finally:
        os.close(fd)
host = socket.gethostname()
print("host", host, "| uid", os.getuid(), "| python", sys.version.split()[0], flush=True)
if not re.fullmatch(r"login\d\d", host):
    stop(f"host {host} is not a login node")
print("== 1. covfix-pg")
real_dir(ROOT)
print("  ", ROOT, "is a real directory")
print("== 2. targets")
for t in TARGETS:
    st = real_dir(t)
    print("  ", t, "real directory, inode", st.st_ino, "mode", oct(stat.S_IMODE(st.st_mode)))
users = []
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    refs = []
    for k in ("cwd", "root"):
        try:
            refs.append(os.readlink(f"/proc/{pid}/{k}"))
        except OSError:
            pass
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            refs += [a.decode("utf-8", "replace") for a in f.read().split(b"\0") if a]
    except OSError:
        pass
    if any(t in r for t in TARGETS for r in refs):
        users.append(pid)
if users:
    stop(f"processes on this node use a target: {users}")
print("   no process on this node refers to either target")
print("== 3. covfix-pg listing before")
before = listing()
for n, v in before.items():
    print("  ", n, "type", oct(v[0]), "mode", oct(v[1]), "size", v[2], "ino", v[3], "mtime_ns", v[4])
for t in TARGETS:
    if os.path.basename(t) not in before:
        stop(f"{t} is not in the listing")
print("== 4. manifest")
total = 0
for t in TARGETS:
    rows = []
    for d, dirs, names in os.walk(t, followlinks=False, onerror=walk_err):
        for n in sorted(dirs) + sorted(names):
            p = os.path.join(d, n)
            s = os.lstat(p)
            if stat.S_ISLNK(s.st_mode):
                rows.append((p, "link", s.st_size, "-> " + os.readlink(p)))
            elif stat.S_ISDIR(s.st_mode):
                rows.append((p, "dir", s.st_size, "-"))
            elif stat.S_ISREG(s.st_mode):
                total += s.st_size
                if total > CAP:
                    stop(f"more than {CAP} bytes under the targets")
                rows.append((p, "file", s.st_size, None))
            else:
                rows.append((p, "special " + oct(stat.S_IFMT(s.st_mode)), s.st_size, "-"))
    rows.sort()
    print(f"-- {t}: {len(rows)} entries")
    for p, k, size, x in rows:
        print("  ", p, k, size, sha(p) if x is None else x)
print("   regular-file bytes in all:", total, flush=True)
print("== 5. delete")
for t in TARGETS:
    os.chmod(t, stat.S_IMODE(os.lstat(t).st_mode) | 0o700)
    for d, dirs, names in os.walk(t, followlinks=False, onerror=walk_err):
        for n in dirs:                                  # each child before the walk enters it
            p = os.path.join(d, n)
            s = os.lstat(p)
            if stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode):
                os.chmod(p, stat.S_IMODE(s.st_mode) | 0o700)
    if not shutil.rmtree.avoids_symlink_attacks:
        stop("this rmtree does not avoid symlink attacks")
    shutil.rmtree(t)
    print("   removed", t, flush=True)
print("== 6. confirm")
for t in TARGETS:
    if os.path.lexists(t):
        stop(f"{t} still exists")
    print("  ", t, "is gone")
after = listing()
want = {n: v for n, v in before.items() if n not in {os.path.basename(t) for t in TARGETS}}
if after != want:
    stop(f"covfix-pg changed beyond the targets: before-less-targets {sorted(want)} after {sorted(after)}")
for n, v in after.items():
    print("  ", n, "unchanged: type", oct(v[0]), "mode", oct(v[1]), "size", v[2], "ino", v[3], "mtime_ns", v[4])
print("DONE: two replay directories removed; covfix-pg otherwise unchanged")
REMOTE
