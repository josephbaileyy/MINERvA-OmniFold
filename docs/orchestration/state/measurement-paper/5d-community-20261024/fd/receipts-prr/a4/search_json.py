"""A4 search, part 2: every absolute path in the four committed queues, and every committed json the runner path
names (queue arguments, and .json literals in the closure's modules), with each absolute path value it carries."""
import json, re, subprocess, sys
from pathlib import Path
REPO = Path(sys.argv[1]).resolve(); SHA = sys.argv[2]; CLOSURE = Path(sys.argv[3]).read_text().split()
Q = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-prr/dry/cluster/queues"
show = lambda p: subprocess.run(["git", "-C", str(REPO), "show", f"{SHA}:{p}"], capture_output=True, text=True).stdout
absq, args = {}, set()
for q in ("dry", "iter", "cap", "misc"):
    for line in show(f"{Q}/{q}.tsv").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        for i, c in enumerate(cols):
            if c.startswith("/"):
                key = re.sub(r"/runs/[^/]+/[^/]+$", "/runs/<level>/<truth>", c)
                absq[key] = absq.get(key, 0) + 1
            if c.endswith(".json") and not c.startswith("/"):
                args.add(c)
print("absolute paths in the 181 queue lines (runs/<level>/<truth> folded):")
for k, v in sorted(absq.items()):
    print(f"  {v:4d}  {k}")
lit = set()
for m in CLOSURE:
    for s in re.findall(r"[\"']([A-Za-z0-9_./${}-]+\.json)[\"']", show(m)):
        lit.add(s)
print(f"\nrepo-relative json named as queue arguments: {len(args)}; .json literals in the {len(CLOSURE)} modules: {len(lit)}")
files = {}
for s in sorted(args | lit):
    for cand in (s, f"nd-unfolding/{s}", f"docs/orchestration/state/{s}"):
        if subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", f"{SHA}:{cand}"], capture_output=True).returncode == 0:
            files[cand] = s; break
print(f"of them committed at {SHA[:8]} (resolved): {len(files)}")
def walk(o, out, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, out, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o[:50]): walk(v, out, f"{path}[{i}]")
    elif isinstance(o, str) and re.match(r"^/(pscratch|global)/", o):
        out.append((path, o))
for f in sorted(files):
    try:
        found = []; walk(json.loads(show(f)), found)
    except json.JSONDecodeError:
        print(f"  {f}: not json"); continue
    print(f"  {f}: {len(found)} absolute path value(s)" + ("" if not found else ""))
    for p, v in found:
        print(f"      {p} = {v}")
