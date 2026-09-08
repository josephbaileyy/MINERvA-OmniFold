set -u
D=/pscratch/sd/j/josephrb/exec-20260907
cd "$D"
echo "=== does the queue's own gitdir exist yet? ==="
/usr/bin/python3.11 - <<'PY'
import sys, os, json, subprocess, datetime
sys.path.insert(0, "docs/orchestration")
import campaignctl as C
print("  QUEUE_SCRATCH_GIT_NAME:", C.QUEUE_SCRATCH_GIT_NAME)
sd = getattr(C, "DEFAULT_STATE_DIR", None)
print("  default state dir:", sd)
cands = []
if sd: cands.append(os.path.join(str(sd), C.QUEUE_SCRATCH_GIT_NAME))
cands.append(os.path.expanduser("~/.campaignctl/" + C.QUEUE_SCRATCH_GIT_NAME))
for c in cands:
    print("   ", c, "exists" if os.path.isdir(c) else "ABSENT")

env = C.git_environment()
pin = json.load(open("docs/orchestration/control-plane/campaign-origin.json"))["origin_url"]
print()
print("  === POSITIVE CONTROL: read a namespace that DOES exist ===")
print("  timestamp_utc:", datetime.datetime.now(datetime.timezone.utc).isoformat())
print("  url (the pin):", pin)
for label, pattern in (("refs/heads/*   ", "refs/heads/*"),
                       ("refs/campaign/*", "refs/campaign/*")):
    p = subprocess.run(["git", "ls-remote", pin, pattern],
                       env=env, capture_output=True, text=True, timeout=120)
    rows = [l for l in p.stdout.splitlines() if l.strip()]
    print(f"  {label}  rc={p.returncode}  rows={len(rows)}  err={p.stderr.strip()[:80]!r}")
print()
print("  interpretation: a NONZERO row count on a namespace that exists is the positive")
print("  control. Zero rows on refs/campaign/* is then a measured emptiness, not a blind read.")
PY
