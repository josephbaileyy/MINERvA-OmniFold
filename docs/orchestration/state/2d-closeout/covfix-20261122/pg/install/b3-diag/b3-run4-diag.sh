#!/bin/bash
# One read-only diagnostic of B3 run 4's STOP at "spline coverage (slot 1)" (for the director's GO). In B3's own
# replay directory (covfix-pg/replay-20261127T194805Z: public seed only) it prints:
#  1. the last 60 lines of driver.log;
#  2. run/coverage_check.json: its pass, its log_sha256, and every problem (each cut at 400 characters);
#  3. the last 80 lines of run/logs/coverage.log and of run/logs/coverage_slot1.log;
#  4. run/coverage/G21_11a_00_000/gevgen.log: its size and line count; how many lines hold each of pg_verify's three
#     markers ("Need xsec spline for ", "Spline was found", "The spline wasn't loaded at initialization"); every line
#     holding one of them, at most 400; then its last 80 lines.
# Each line is cut at 400 characters. Each file is read O_NOATIME|O_NOFOLLOW and must be a regular file. Nothing is
# written on NERSC. The output stays on the laptop beside this script.
set -u
OUT="$(dirname "$0")/b3-run4-diag.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import json, os, socket, stat
W = "/pscratch/sd/j/josephrb/covfix-pg/replay-20261127T194805Z"
R = W + "/run"
T = "G21_11a_00_000"
MARKS = ("Need xsec spline for ", "Spline was found", "The spline wasn't loaded at initialization")
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
def show(lines, cap):
    for ln in lines[:cap]:
        print("  ", ln[:400])
    if len(lines) > cap:
        print(f"   ... {len(lines) - cap} more")
def tail(p, n):
    print(f"== last {n} lines of {p}")
    try:
        show(read(p).splitlines()[-n:], n)
    except OSError as e:
        print("   unreadable:", e.strerror)
print("host", socket.gethostname())
print("== 1.")
tail(W + "/driver.log", 60)
print("== 2. coverage_check.json")
try:
    d = json.loads(read(R + "/coverage_check.json"))
    print("   pass", d.get("pass"), "| log_sha256", d.get("log_sha256"), "| keys", sorted(d))
    probs = d.get("problems") or []
    print(f"   problems ({len(probs)}):")
    show([str(p) for p in probs], 400)
except (OSError, ValueError) as e:
    print("   unreadable:", e)
print("== 3.")
tail(R + "/logs/coverage.log", 80)
tail(R + "/logs/coverage_slot1.log", 80)
print("== 4. gevgen.log")
try:
    text = read(f"{R}/coverage/{T}/gevgen.log")
    lines = text.splitlines()
    print("   bytes", len(text), "lines", len(lines))
    for m in MARKS:
        print("   marker", repr(m), "lines", sum(m in ln for ln in lines))
    show([ln for ln in lines if any(m in ln for m in MARKS)], 400)
    print("-- its last 80 lines")
    show(lines[-80:], 80)
except OSError as e:
    print("   unreadable:", e.strerror)
print("== end")
REMOTE
