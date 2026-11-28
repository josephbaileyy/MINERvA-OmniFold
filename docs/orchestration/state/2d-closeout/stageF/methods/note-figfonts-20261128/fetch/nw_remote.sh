#!/bin/bash
# nw_remote.sh: the remote half of the negweight input fetch (limitation-resolver, 2026-11-28; the figure PR, Joseph's GO
# relayed by the director). It runs on one Perlmutter login node, in one ssh session, fed on stdin:
#   ssh ... 'bash -s -- <mode>' < nw_remote.sh  >payload.tar  2>session.log
# Its stdout is ONLY a tar stream (the payload); every log line goes to stderr. It writes nothing on the cluster: no
# file, no directory, no Slurm job; the pscratch reads use O_RDONLY|O_NOATIME|O_NOFOLLOW and the HPSS read streams to
# stdout. The mode is a required argument, never chosen here:
#   pscratch  read the two ROOT files from the checkout on pscratch (refuses if either is missing; no fallback)
#   hpss      stream negweight_runs_8.tar from HPSS (hsi get to stdout); the laptop extracts the two members
# Both modes run the fence first and refuse (exit 10) on any queued, running or unended job of the protected families.
set -u
MODE=${1:-}
log() { printf '%s\n' "$*" >&2; }
case "$MODE" in pscratch|hpss) ;; *) log "REFUSED: mode must be pscratch or hpss (got '$MODE')"; exit 2;; esac
log "nw_remote mode=$MODE host=$(hostname) utc=$(date -u +%FT%TZ)"

# ---- fence: sacct and squeue at START; refuse on a protected family -------------------------------------------------
python3 -s - <<'FENCE' >&2
import re, subprocess, sys, datetime
FAMILIES = re.compile(r"^(cov2d|t2a|rpd|precharge_c|geanttw_|oofvc_|covfix_|ibuchi_|ptmc_)")
TERMINAL = re.compile(r"^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE|REVOKED)")
start = (datetime.datetime.utcnow() - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
P = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)   # python 3.6-safe
sa = subprocess.run(["sacct", "-X", "-n", "-P", "-S", start, "-u", "josephrb", "-o", "JobID,JobName,State"], **P)
sq = subprocess.run(["squeue", "--me", "-h", "-o", "%i|%j|%T"], **P)
print(f"fence sacct rc={sa.returncode} rows={len([l for l in sa.stdout.splitlines() if l.strip()])} since {start}")
print(f"fence squeue rc={sq.returncode} rows={len([l for l in sq.stdout.splitlines() if l.strip()])}")
if sa.returncode != 0 or sq.returncode != 0:
    print("REFUSED: sacct or squeue failed"); sys.exit(10)
active = []
for l in sa.stdout.splitlines():
    f = l.split("|")
    if len(f) >= 3 and not TERMINAL.match(f[2]):
        active.append(("sacct", f[0], f[1], f[2]))
for l in sq.stdout.splitlines():
    f = l.split("|")
    if len(f) >= 3:
        active.append(("squeue", f[0], f[1], f[2]))
for a in active:
    print("fence active: " + " ".join(a))
hit = [a for a in active if FAMILIES.match(a[2])]
if hit:
    print(f"REFUSED: {len(hit)} queued/running/unended job(s) of a protected family"); sys.exit(10)
print(f"FENCE CLEAR ({len(active)} other active job(s) listed above, none of a protected family)")
FENCE
frc=$?
[ "$frc" = 0 ] || { log "nw_remote: fence rc=$frc, nothing read"; exit 10; }

# ---- payload --------------------------------------------------------------------------------------------------------
if [ "$MODE" = pscratch ]; then
python3 -s - <<'READ'
import hashlib, io, os, stat, sys, tarfile
ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
RELS = ["2d-unfolding/HANDOFF_bkg_negweight/runs/2d_xsec_purity_seed1_hist5.root",
        "2d-unfolding/HANDOFF_bkg_negweight/runs/2d_xsec_negweight_seed1_hist5.root"]
FLAGS = os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW
def log(s): print(s, file=sys.stderr, flush=True)
def st(p):
    s = os.lstat(p); return (s.st_atime_ns, s.st_mtime_ns, s.st_size, stat.S_ISREG(s.st_mode))
pre, data = {}, {}
for rel in RELS:
    p = os.path.join(ROOT, rel)
    if not os.path.lexists(p):
        log(f"MISSING {p}"); log("REFUSED: a pscratch input is missing; the hpss mode is a separate, explicit run"); sys.exit(20)
    if os.path.realpath(p) != p:
        log(f"REFUSED: {p} resolves to {os.path.realpath(p)}"); sys.exit(21)
    pre[rel] = st(p)
    if not pre[rel][3]:
        log(f"REFUSED: {p} is not a regular file"); sys.exit(21)
for rel in RELS:
    p = os.path.join(ROOT, rel)
    fd = os.open(p, FLAGS)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b: break
            chunks.append(b)
    finally:
        os.close(fd)
    data[rel] = b"".join(chunks)
bad = 0
for rel in RELS:
    p = os.path.join(ROOT, rel); post = st(p)
    h = hashlib.sha256(data[rel]).hexdigest()
    same = post == pre[rel] and len(data[rel]) == pre[rel][2]
    log(f"node-read {rel} bytes={len(data[rel])} sha256={h} atime_ns pre={pre[rel][0]} post={post[0]} "
        f"mtime_ns pre={pre[rel][1]} post={post[1]} {'UNCHANGED' if same else 'CHANGED'}")
    bad += not same
if bad:
    log("REFUSED: an atime, mtime or size changed during the read; no payload written"); sys.exit(22)
out = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
for rel in RELS:
    ti = tarfile.TarInfo(rel); ti.size = len(data[rel]); ti.mtime = pre[rel][1] // 10**9; ti.mode = 0o644
    out.addfile(ti, io.BytesIO(data[rel]))
out.close(); sys.stdout.buffer.flush()
log("nw_remote: pscratch payload written to stdout (2 members)")
READ
rc=$?
else
OBJ=mnv-negweight-historical-20260821/negweight_runs_8.tar
log "nw_remote: hsi get - : $OBJ (to stdout; nothing written on the cluster)"
hsi -q "get - : $OBJ"
rc=$?
fi
log "nw_remote: payload rc=$rc utc=$(date -u +%FT%TZ)"
exit "$rc"
