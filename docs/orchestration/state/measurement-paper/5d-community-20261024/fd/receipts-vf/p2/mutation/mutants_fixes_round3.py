import subprocess, shutil, sys, os, hashlib
from pathlib import Path
W = Path.home() / "s2r-wt"
F = W / "nd-unfolding/fd_vf_p2.py"
V = W / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-vf/readings/vf_readings.py"
MUT = [
 (V, '"in_cells", "named", "quadrants_over"}', '"in_cells", "quadrants_over"}', "named not a flag list"),
 (V, 'r"unchanged|units|what)$")', 'r"unchanged|units|what|truths)$")', "truths descriptive"),
 (V, 'return sc.index(b) < sc.index(a)', 'return sc.index(b) > sc.index(a)', "scale reversed"),
 (V, 'if ma and mb and ma.group(2) == mb.group(2):', 'if ma and mb:', "verdict across arms"),
 (V, 'r"unchanged|units|what)$")', 'r"unchanged|units|what|.*)$")', "descriptive matches all"),
 (V, '["T0", "T1", "T2"], ', '', "T scale missing"),
]
env = dict(os.environ, VF_P2_FETCH="/Users/josephbailey/vf-p2-fetch-20261126")
res = []
for path, old, new, label in MUT:
    src = path.read_bytes(); txt = src.decode()
    assert txt.count(old) == 1, (label, txt.count(old))
    work = Path.home() / "vf-p2-fetch-20261126-xk"
    try:
        path.write_text(txt.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-x", "-q", "tests/test_fd_vf_p2.py"], cwd=W / "nd-unfolding",
                           env=env, capture_output=True, text=True, timeout=1800)
        killed = r.returncode != 0
    finally:
        path.write_bytes(src)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == hashlib.sha256(src).hexdigest()
    res.append((label, "KILLED" if killed else "SURVIVED", r.stdout.strip().splitlines()[-1][:120]))
    print(*res[-1], sep=" | ", flush=True)
print(f"{sum(x[1]=='KILLED' for x in res)}/{len(res)} killed")

