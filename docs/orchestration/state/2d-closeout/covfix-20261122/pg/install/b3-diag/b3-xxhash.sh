#!/bin/bash
# Read-only search for a CVMFS libxxhash.so.0 to replace the conda env's (the director's (ii), 2026-11-26). No program
# is run but readelf and nm; nothing is written on NERSC; the output stays on the laptop beside this script.
#  1. larsoft: the products listing for xxhash (any case), and each product's libxxhash.so* files (glob, no find);
#  2. minerva: each containers/<c>/{lib64,usr/lib64}/libxxhash.so* (glob), and the containers listing;
#  3. for each candidate, and the conda file the shim uses today: real path, size, sha256, SONAME (readelf -dW), the
#     defined XXH* dynamic symbols (nm -D --defined-only) and their versions (readelf --dyn-syms -W);
#  4. ROOT v6_22_08d libCore.so: its undefined XXH* dynamic symbols (nm -D --undefined-only), and its version needs
#     on libxxhash (readelf -V); then, per candidate, whether its SONAME is libxxhash.so.0 and it defines all of them.
set -u
OUT="$(dirname "$0")/b3-xxhash.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import glob, hashlib, os, re, socket, subprocess
LP = "/cvmfs/larsoft.opensciencegrid.org/products"
MC = "/cvmfs/minerva.opensciencegrid.org/minerva/containers"
CORE = LP + "/root/v6_22_08d/Linux64bit+3.10-2.17-e20-p392-prof/lib/libCore.so"
CONDA = "/global/u2/j/josephrb/.conda/envs/root_6_28/lib/libxxhash.so.0.8.2"
def run(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{argv[0]} failed on {argv[-1]}: rc {r.returncode} {r.stderr[:200]}")
    return r.stdout
print("host", socket.gethostname(), "| readelf", os.path.exists("/usr/bin/readelf"), "| nm", os.path.exists("/usr/bin/nm"))
for k in ("user.revision", "user.root_hash"):
    for repo in ("/cvmfs/larsoft.opensciencegrid.org", "/cvmfs/minerva.opensciencegrid.org"):
        print(" ", repo, k, os.getxattr(repo, k).decode())
print("== 1. larsoft products matching xxhash")
prods = [p for p in sorted(os.listdir(LP)) if "xxhash" in p.lower()]
print("  ", prods)
cands = []
for p in prods:
    for f in sorted(glob.glob(f"{LP}/{p}/*/*/lib*/libxxhash.so*") + glob.glob(f"{LP}/{p}/*/lib*/libxxhash.so*")):
        cands.append(f)
print("== 2. minerva containers")
cs = sorted(os.listdir(MC)) if os.path.isdir(MC) else []
print("  ", cs)
for c in cs:
    for sub in ("lib64", "usr/lib64"):
        cands += sorted(glob.glob(f"{MC}/{c}/{sub}/libxxhash.so*"))
print("  candidates:", cands)
print("== 4. libCore.so's needs")
und = sorted(set(re.findall(r"^\s+U (XXH\w+)", run(["/usr/bin/nm", "-D", "--undefined-only", CORE]), re.M)))
print("  undefined XXH symbols:", und)
vneed = run(["/usr/bin/readelf", "-VW", CORE])
blk = [ln.strip() for ln in vneed.splitlines() if "xxhash" in ln.lower()]
print("  version needs naming xxhash:", blk)
print("  NEEDED:", [n for n in re.findall(r"\[([^\]]+)\]", run(["/usr/bin/readelf", "-dW", CORE])) if "xxhash" in n])
print("== 3. each candidate (real file) and the conda file")
seen = set()
for f in cands + [CONDA]:
    rf = os.path.realpath(f)
    if rf in seen:
        print("  (same file)", f, "->", rf); continue
    seen.add(rf)
    soname = re.findall(r"\(SONAME\)\s+Library soname: \[([^\]]+)\]", run(["/usr/bin/readelf", "-dW", rf]))
    defined = sorted(set(re.findall(r"^\S+\s+[TtWiV] (XXH\w+)", run(["/usr/bin/nm", "-D", "--defined-only", rf]), re.M)))
    vers = sorted(set(re.findall(r"(XXH\w+)@+(\S+)", run(["/usr/bin/readelf", "--dyn-syms", "-W", rf]))))
    h = hashlib.sha256(open(rf, "rb").read()).hexdigest()
    print(f"  {f} -> {rf}\n    size {os.path.getsize(rf)} sha256 {h}\n    SONAME {soname}\n    defined XXH: {len(defined)}"
          f"\n    versioned XXH: {vers[:6]}{' ...' if len(vers) > 6 else ''}")
    missing = [s for s in und if s not in defined]
    print(f"    MATCH: soname libxxhash.so.0 = {soname == ['libxxhash.so.0']}; libCore's {len(und)} undefined XXH "
          f"symbols all defined = {not missing}; missing {missing}")
print("== end")
REMOTE
