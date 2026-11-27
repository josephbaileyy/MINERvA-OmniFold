#!/bin/bash
# The second read-only diagnostic of B3 run 4's STOP at "spline coverage (slot 1)" (for the director's GO), for the
# design note replacing D3′(ii). It prints:
#  1. the pinned GENIE build's flags: GENIE-Generator/src/make/Make.config and Make.include, each sha256'd against its
#     genie-manifest.json pin, and every line naming NDEBUG, CXXFLAGS, CFLAGS, OPT, DEBUG, -O or -g;
#  2. lib/libGFwEG-3.04.00.so (GEVGDriver's library), sha256'd against its pin; whether its bytes hold the strings an
#     enabled assert compiles in: GEVGDriver.cxx:456's expression "fUseSplines", :457's "Emin<Emax && Emin>0 && nk>2",
#     and the import "__assert_fail" (NDEBUG removes the first two expressions and, if nothing else asserts, the import);
#  3. B3 run 4's coverage trace (replay-20261127T194805Z/run/coverage/G21_11a_00_000/coverage.trace, public seed only):
#     its size and line count; how many write() lines it has; the distinct 32-character write strings with digits
#     masked, counted, the 120 most frequent; and every write() line naming spline, xsec, XSec, Revert, interpolated,
#     computed, SumXSec, Need, FATAL or WARN (case-insensitive), at most 400.
# Each line is cut at 400 characters. Each file is read O_NOATIME|O_NOFOLLOW (O_NOFOLLOW alone where O_NOATIME is
# refused for a file not ours) and must be a regular file. Nothing is written on NERSC. The output stays on the laptop
# beside this script.
set -u
OUT="$(dirname "$0")/b3-run4-diag2.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import collections, hashlib, os, re, socket, stat
G = "/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof"
PINS = {G + "/GENIE-Generator/src/make/Make.config": "95b11fee0c87c6032ea718f0be65cbab3bb30a29bbc0661b3965b922c0455104",
        G + "/GENIE-Generator/src/make/Make.include": "d3ff0f52219b725df6107d601917cc76cd4a699b8399a63c6cc43423e15e989f",
        G + "/lib/libGFwEG-3.04.00.so": "17a907b15fcef1edb5731d18cd046b77161e7b2c57e3e41b1f15a82d2ba38288"}
TRACE = "/pscratch/sd/j/josephrb/covfix-pg/replay-20261127T194805Z/run/coverage/G21_11a_00_000/coverage.trace"
def read(p):
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        raise SystemExit(f"{p} is not a regular file")
    try:
        fd = os.open(p, os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW)
    except PermissionError:                     # O_NOATIME needs ownership (pg_verify's _open does the same)
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        chunks = []
        while True:
            c = os.read(fd, 1 << 20)
            if not c:
                return b"".join(chunks)
            chunks.append(c)
    finally:
        os.close(fd)
def show(lines, cap):
    for ln in lines[:cap]:
        print("  ", ln[:400])
    if len(lines) > cap:
        print(f"   ... {len(lines) - cap} more")
def pinned(p):
    b = read(p)
    h = hashlib.sha256(b).hexdigest()
    print("  ", p, "sha256", h, "pin", "match" if h == PINS[p] else "MISMATCH " + PINS[p])
    return b
print("host", socket.gethostname())
print("== 1. build flags")
flag = re.compile(r"NDEBUG|CXXFLAGS|CFLAGS|\bOPT|DEBUG|(^|\s)-O|(^|\s)-g\b")
for p in (G + "/GENIE-Generator/src/make/Make.config", G + "/GENIE-Generator/src/make/Make.include"):
    t = pinned(p).decode("utf-8", "replace").splitlines()
    show([f"{i + 1}: {ln}" for i, ln in enumerate(t) if flag.search(ln)], 120)
print("== 2. libGFwEG")
b = pinned(G + "/lib/libGFwEG-3.04.00.so")
for s in (b"fUseSplines", b"Emin<Emax && Emin>0 && nk>2", b"__assert_fail", b"GEVGDriver.cxx"):
    print("  ", repr(s.decode()), "occurrences", b.count(s))
print("== 3. the coverage trace")
try:
    text = read(TRACE).decode("utf-8", "replace")
    lines = text.splitlines()
    print("   bytes", len(text), "lines", len(lines))
    wr = [ln for ln in lines if re.search(r"\bwrite\(\d+, ", ln)]
    print("   write() lines", len(wr))
    strs = collections.Counter(re.sub(r"\d", "#", m.group(1)) for ln in wr
                               for m in [re.search(r'write\(\d+, "((?:[^"\\]|\\.)*)"', ln)] if m)
    print("   distinct write strings (digits masked)", len(strs))
    for s, n in strs.most_common(120):
        print(f"   {n:8d}  {s[:200]}")
    key = re.compile(r"spline|xsec|revert|interpolated|computed|need|fatal|warn", re.I)
    print("-- write() lines naming a keyword")
    show([ln for ln in wr if key.search(ln)], 400)
except OSError as e:
    print("   unreadable:", e.strerror)
print("== end")
REMOTE
