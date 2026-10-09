"""Compare lane-tip and upstream files with the delivery tree 901f0088 (read-only git queries)."""
import subprocess, sys
def g(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
def blob(rev, path):
    r = subprocess.run(["git", "rev-parse", "-q", "--verify", f"{rev}:{path}"], capture_output=True, text=True)
    return r.stdout.strip() or None
T = sys.argv[1] if len(sys.argv) > 1 else "901f0088"
lanes = {"A": "cc9eed27", "B": "c783d9c3", "C": "57f6dd30", "D": "ecb52dde"}
for lane, tip in lanes.items():
    files = set()
    for c in g("rev-list", "--no-merges", f"f8e2bf85..{tip}").split():
        files |= set(g("diff-tree", "--no-commit-id", "--name-only", "-r", c).split())
    diff = sorted(f for f in files if blob(tip, f) != blob(T, f))
    print(f"{lane} tip {tip}: {len(files)} lane-touched files; differ at {T}: {diff or 'none'}")
for up_base, up in (("ad2716d8", "33811d7d"), ("ad2716d8", "460631d1")):
    files = set(g("diff", "--name-only", up_base, up).split())
    diff = sorted(f for f in files if blob(up, f) != blob(T, f))
    print(f"upstream {up_base}..{up}: {len(files)} files; differ at {T}: {diff or 'none'}")
