#!/bin/bash
# Read-only evidence for the director's ruling on B3's compat-lib shim. No GENIE program is run and nothing is
# written on NERSC; the output stays on the laptop beside this script.
#  (c) the libssl/libcrypto/libpcre/libpcreposix/libxxhash files and sonames the login node's system provides
#      (ls of /lib64 and /usr/lib64; ldconfig -p, which reads ld.so.cache);
#  the NEEDED closure of gevgen, gntpc and gspl2root: each NEEDED name resolved, in order, against B3 run 2's
#      recorded LD_LIBRARY_PATH (first the shim, then the CVMFS dirs) and then /lib64, /usr/lib64, using
#      `readelf -dW` (ELF dynamic headers only), with the providing file of every shim-provided name;
#  (a) the real path, size and sha256 of each shim entry's target (sha256sum reads them).
set -u
OUT="$(dirname "$0")/b3-libs.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import glob, hashlib, os, pwd, re, socket, subprocess
R = "/pscratch/sd/j/josephrb/covfix-pg/replay-20261126T211924Z/run"
HM = pwd.getpwuid(os.getuid()).pw_dir
SHIM = os.path.join(HM, ".genie_compatlibs")
G = "/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof"
NAMES = re.compile(r"^(libssl|libcrypto|libpcre|libpcreposix|libxxhash)\.so")
print("host", socket.gethostname())
print(open("/etc/os-release").read().split("\n")[:3])
print("== (c) system files")
for d in ("/lib64", "/usr/lib64"):
    for f in sorted(os.listdir(d)):
        if NAMES.match(f):
            p = os.path.join(d, f)
            print(" ", p, "->", os.path.realpath(p))
print("== (c) ldconfig -p")
out = subprocess.run(["/sbin/ldconfig", "-p"], capture_output=True, text=True).stdout
for ln in out.splitlines():
    if NAMES.match(ln.strip()):
        print(" ", ln.strip())
def needed(f):
    r = subprocess.run(["/usr/bin/readelf", "-dW", f], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"readelf failed on {f}: rc {r.returncode} {r.stderr[:200]}")
    o = r.stdout
    return re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", o)
ldp = open(os.path.join(R, "ld_library_path_G21_11a_00_000.txt")).read().strip().split(":")
search = ldp + ["/lib64", "/usr/lib64"]
def resolve(n):
    for d in search:
        p = os.path.join(d, n)
        if os.path.exists(p):
            return d, p
    return None, None
print("== readelf", os.path.exists("/usr/bin/readelf"))
print("== the NEEDED closure (search:", len(ldp), "LD_LIBRARY_PATH dirs, then /lib64, /usr/lib64)")
todo = [G + "/bin/gevgen", G + "/bin/gntpc", G + "/bin/gspl2root"]
seen, files, unresolved, shim_hits = set(), 0, [], []
while todo:
    f = todo.pop()
    rf = os.path.realpath(f)
    if rf in seen:
        continue
    seen.add(rf); files += 1
    for n in needed(rf):
        d, p = resolve(n)
        if p is None:
            unresolved.append((n, f)); continue
        if d == SHIM or NAMES.match(n):
            shim_hits.append((n, f, d, os.path.realpath(p)))
        todo.append(p)
print("  ELF files read:", files)
print("  unresolved:", sorted(set(unresolved)))
print("  shim-soname NEEDED (name, needed by, providing dir, real file):")
for h in sorted(set(shim_hits)):
    print("   ", h)
print("== (a) shim targets")
for f in sorted(glob.glob(SHIM + "/*")):
    t = os.path.realpath(f)
    h = hashlib.sha256(open(t, "rb").read()).hexdigest()
    print(" ", os.path.basename(f), "->", t, os.path.getsize(t), h)
print("== minerva CVMFS repo")
for k in ("user.fqrn", "user.revision", "user.root_hash"):
    try:
        print(" ", k, os.getxattr("/cvmfs/minerva.opensciencegrid.org", k).decode())
    except OSError as e:
        print(" ", k, "unreadable", type(e).__name__)
print("== end")
REMOTE
