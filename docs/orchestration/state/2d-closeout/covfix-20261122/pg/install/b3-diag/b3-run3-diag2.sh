#!/bin/bash
# The second read-only diagnostic of B3 run 3's STOP at "trace check (graphs)" (for the director's GO). In B3's own
# replay directory (covfix-pg/replay-20261127T050508Z: public seed only) it prints:
#  1. trace_check_graphs.json's 365 problems counted by code, every problem that is not a search-probes one in full,
#     and the search-probes basenames, each once;
#  2. from gspl2root's trace (run/traces/graphs_G21_11a_00_000.trace): its size and line count, then every line of a
#     process event (execve, chdir, fchdir, clone, clone3, vfork, fork, a nonzero exit, a kill), at most 400;
#  3. every trace line naming master_config.xml, ModelConfiguration.xml or AGKY2019.xml, at most 120 for each;
#  4. the first 60 lines naming '.rootmap' or 'GENIE/Tools/Flux';
#  5. run/gxmlpath_G21_11a_00_000.txt.
# Each line is cut at 400 characters. Each file is read O_NOATIME|O_NOFOLLOW and must be a regular file. Nothing is
# written on NERSC. The output stays on the laptop beside this script.
set -u
OUT="$(dirname "$0")/b3-run3-diag2.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -" > "$OUT" 2>&1 <<'REMOTE'
import collections, json, os, re, socket, stat
W = "/pscratch/sd/j/josephrb/covfix-pg/replay-20261127T050508Z"
R = W + "/run"
T = "G21_11a_00_000"
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
print("host", socket.gethostname())
print("== 1. problems")
d = json.loads(read(R + "/trace_check_graphs.json"))
probs = d["problems"]
codes = collections.Counter(p.split(":", 1)[0] for p in probs)
print("  ", len(probs), "problems:", dict(sorted(codes.items())))
show([p for p in probs if not p.startswith("search-probes:")], 400)
sp = [p for p in probs if p.startswith("search-probes:")]
kinds = collections.Counter(re.sub(r"^search-probes: \S+ read at \S+ ", "", p) for p in sp)
print("   search-probes kinds:", dict(kinds))
print("   search-probes basenames:", " ".join(sorted({p.split()[1] for p in sp})))
print("== 2. the trace's process events")
text = read(f"{R}/traces/graphs_{T}.trace")
lines = text.splitlines()
print("   bytes", len(text), "lines", len(lines))
pe = re.compile(r"\b(execve|execveat|chdir|fchdir|clone|clone3|vfork|fork)\(|\+\+\+ exited with [1-9]|\+\+\+ killed")
show([ln for ln in lines if pe.search(ln)], 400)
print("== 3. three config files")
for b in ("master_config.xml", "ModelConfiguration.xml", "AGKY2019.xml"):
    print("--", b)
    show([ln for ln in lines if b in ln], 120)
print("== 4. rootmap and relative GENIE include lookups")
show([ln for ln in lines if ".rootmap" in ln or "GENIE/Tools/Flux" in ln], 60)
print("== 5. gxmlpath")
print("  ", read(f"{R}/gxmlpath_{T}.txt").strip())
print("== end")
REMOTE
