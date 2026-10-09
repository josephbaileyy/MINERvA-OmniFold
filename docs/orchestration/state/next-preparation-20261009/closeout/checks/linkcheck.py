"""Resolve every relative markdown link and every backticked repo path in the given files."""
import os, re, subprocess, sys
tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split())
dirs = {os.path.dirname(p) for p in tracked}
while True:
    more = {os.path.dirname(d) for d in dirs} - dirs
    if not more: break
    dirs |= more
bad = 0; n = 0
for f in sys.argv[1:]:
    base = os.path.dirname(f)
    text = open(f).read()
    for m in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        tgt = m.group(1)
        if re.match(r"[a-z]+://", tgt): continue
        p = os.path.normpath(os.path.join(base, tgt)).rstrip("/")
        n += 1
        if p not in tracked and p not in dirs:
            bad += 1; print(f"LINK {f}: {tgt} -> {p}")
    for m in re.finditer(r"`((?:docs|2d-unfolding|nd-unfolding|state|publication)/[^`\s]+)`", text):
        tgt = m.group(1).rstrip("/")
        cands = [tgt, os.path.normpath(os.path.join(base, tgt)), "docs/orchestration/" + tgt]
        n += 1
        if not any(c in tracked or c in dirs for c in cands):
            bad += 1; print(f"PATH {f}: {tgt}")
print(f"checked {n}, unresolved {bad}")
