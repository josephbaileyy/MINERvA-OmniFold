set -u
cd /pscratch/sd/j/josephrb/exec-20260907
OUT=/pscratch/sd/j/josephrb/exec-20260907-out/transport-probe-20260908
mkdir -p "$OUT"
/usr/bin/python3.11 - <<'PY' 2>&1 | tee "$OUT/ls-remote-under-git-environment.log"
import json, os, subprocess, sys, datetime
sys.path.insert(0, "docs/orchestration")
import campaignctl as C

fn = getattr(C, "git_environment", None)
print("campaignctl.git_environment present:", callable(fn))
env = fn() if callable(fn) else None
if env is None:
    base = dict(os.environ)
    for key in C.GIT_INJECTING_ENVIRONMENT:
        base.pop(key, None)
    for key in [k for k in base if C.GIT_INJECTING_ENVIRONMENT_INDEXED_RE.match(k)]:
        base.pop(key, None)
    base.update(C.GIT_ISOLATED_CONFIGURATION_ENVIRONMENT)
    env = base
    print("used reconstructed environment from module constants")
print("HOME present:", "HOME" in env, "| SSH_AUTH_SOCK present:", "SSH_AUTH_SOCK" in env)
print("GIT_CONFIG_GLOBAL:", env.get("GIT_CONFIG_GLOBAL"), "| GIT_CONFIG_NOSYSTEM:", env.get("GIT_CONFIG_NOSYSTEM"))
print("timestamp_utc:", datetime.datetime.now(datetime.timezone.utc).isoformat())

for label, url in [
    ("scp-ssh  ", "git@github.com:josephbaileyy/MINERvA-OmniFold"),
    ("https-pin", "https://github.com/josephbaileyy/MINERvA-OmniFold"),
]:
    p = subprocess.run(["git", "ls-remote", url, "refs/heads/main"],
                       env=env, capture_output=True, text=True, timeout=120)
    print(f"{label} rc={p.returncode} out={p.stdout.strip()[:80]!r} err={p.stderr.strip()[:160]!r}")
PY
echo
echo "log written to: $OUT/ls-remote-under-git-environment.log"
sha256sum "$OUT/ls-remote-under-git-environment.log" | sed 's/^/  /'
