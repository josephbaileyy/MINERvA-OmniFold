#!/bin/bash
# One read-only diagnostic of B3 run 3's STOP at "trace check (graphs)" (for the director's GO). In B3's own replay
# directory (covfix-pg/replay-20261127T050508Z: public seed only) it prints the driver's log, the graphs trace check's
# record (its pass, its keys, and its problems, the first 200, each cut at 400 characters), and the last 80 lines of
# logs/trace_check.log and logs/graphs.log. Each file is read O_NOATIME|O_NOFOLLOW and must be a regular file; the
# trace itself is not printed. Nothing is written on NERSC. The output stays on the laptop beside this script.
set -u
OUT="$(dirname "$0")/b3-run3-diag.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import json, os, socket, stat
W = "/pscratch/sd/j/josephrb/covfix-pg/replay-20261127T050508Z"
R = W + "/run"
def read(p):
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        raise SystemExit(f"{p} is not a regular file")
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW)
    try:
        b = b""
        while True:
            c = os.read(fd, 1 << 20)
            if not c:
                return b.decode("utf-8", "replace")
            b += c
    finally:
        os.close(fd)
def tail(p, n=80):
    print(f"== last {n} lines of {p}")
    try:
        print("\n".join(read(p).splitlines()[-n:]))
    except OSError as e:
        print("  unreadable:", e.strerror)
print("host", socket.gethostname())
tail(W + "/driver.log", 60)
print("== trace_check_graphs.json")
try:
    d = json.loads(read(R + "/trace_check_graphs.json"))
    print("  pass", d.get("pass"), "| keys", sorted(d))
    for k, v in sorted(d.items()):
        if isinstance(v, (int, float, str, bool)) or v is None:
            print("  ", k, "=", str(v)[:400])
        elif isinstance(v, (list, dict)):
            print("  ", k, ":", type(v).__name__, len(v))
    probs = d.get("problems") or []
    print(f"  problems ({len(probs)}), the first 200:")
    for p in probs[:200]:
        print("   -", str(p)[:400])
except (OSError, ValueError) as e:
    print("  unreadable:", e)
tail(R + "/logs/trace_check.log")
tail(R + "/logs/graphs.log")
print("== end")
REMOTE
