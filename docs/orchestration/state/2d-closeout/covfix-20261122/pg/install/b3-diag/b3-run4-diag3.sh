#!/bin/bash
# A read-only diagnostic for D3′(ii)'s record parser (DESIGN-D3PRIME-II.md §3, "Validating the parser"), for the
# director's GO. It reads B3 run 4's gspl2root log, real GENIE output already on scratch
# (replay-20261127T194805Z/run/graphs_G21_11a_00_000.log, written by run_gevgen_v3.sh's graphs mode at the default
# Messenger.xml levels), and prints:
#  1. its size and line count;
#  2. how many lines match the record prefix the parser assumes (log4cpp BasicLayout, GENIE's LOG and SLOG macros,
#     Messenger.h:84-99): `<seconds> <PRIORITY> <stream> <ndc>: [n] <file::function (line)> : ` or `[s] <function
#     (line)> : `; how many look like a record prefix but don't match; and the counts by priority and stream;
#  3. the first 40 matching lines and the first 40 non-matching lines, each cut at 300 characters, with every digit
#     run in the leading timestamp masked.
# The log carries spline names and interaction codes only (a public product, no seed). The file is read
# O_NOATIME|O_NOFOLLOW and must be a regular file. Nothing is written on NERSC. The output stays on the laptop beside
# this script.
set -u
OUT="$(dirname "$0")/b3-run4-diag3.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import collections, os, re, socket, stat
P = "/pscratch/sd/j/josephrb/covfix-pg/replay-20261127T194805Z/run/graphs_G21_11a_00_000.log"
REC = re.compile(r"^(\d+) (FATAL|ALERT|CRIT|ERROR|WARN|NOTICE|INFO|DEBUG) (\S+) (\S*): \[([ns])\] <(.+?) \((\d+)\)> : ")
LOOSE = re.compile(r"^\d{9,} [A-Z]+ ")
def read(p):
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        raise SystemExit(f"{p} is not a regular file")
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW)
    try:
        chunks = []
        while True:
            c = os.read(fd, 1 << 20)
            if not c:
                return b"".join(chunks).decode("utf-8", "replace")
            chunks.append(c)
    finally:
        os.close(fd)
mask = lambda ln: re.sub(r"^\d+", lambda m: "#" * len(m.group(0)), ln)[:300]
print("host", socket.gethostname())
try:
    lines = read(P).splitlines()
except OSError as e:
    raise SystemExit(f"unreadable: {e.strerror}")
print("== 1.", P, "lines", len(lines))
hit = [ln for ln in lines if REC.match(ln)]
near = [ln for ln in lines if LOOSE.match(ln) and not REC.match(ln)]
print("== 2. matching", len(hit), "| prefix-like but not matching", len(near))
c = collections.Counter((REC.match(ln).group(2), REC.match(ln).group(3), REC.match(ln).group(5)) for ln in hit)
for (pr, s, k), n in sorted(c.items()):
    print(f"   {n:7d}  {pr:6s} {s} [{k}]")
print("== 3. the first 40 matching lines")
for ln in hit[:40]:
    print("  ", mask(ln))
print("-- the first 40 non-matching lines")
for ln in [ln for ln in lines if not REC.match(ln)][:40]:
    print("  ", mask(ln))
print("-- every prefix-like line that does not match, at most 40")
for ln in near[:40]:
    print("  ", mask(ln))
print("== end")
REMOTE
