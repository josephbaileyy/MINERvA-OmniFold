"""Survey of stepped lines in the note's figures (note-stepedges-20261121).

usage: python3 survey_steps.py <worktree> [--all]

For each figure the note's .tex files include (\\includegraphics; commented lines are not excluded, so a commented-out
figure is listed too), or with --all for every stem captured anywhere under docs/orchestration/state, the latest
committed capture (fig-restyle artists index, <stem>.pdf.json, with its .npz) is read, and every line drawn with a
visible line style and a steps drawstyle is listed with its x (a step over bin centres or indices shows up here).
Figures with no capture are listed at the end; their producers are read by hand (README.md).
"""
import json, re, subprocess, sys, os
from pathlib import Path
import numpy as np
W = Path(sys.argv[1])
os.chdir(W)
tex = subprocess.run(["git","grep","-h","-o",r"\\includegraphics\(\[[^]]*\]\)\?{[^}]*}","--","docs/analysis-note/*.tex"],capture_output=True,text=True).stdout
inc = sorted({Path(m.split("{")[-1].rstrip("}")).stem for m in tex.split()})
files = subprocess.run(["git","ls-files","docs/orchestration/state"],capture_output=True,text=True).stdout.split()
caps = {}
for f in files:
    m = re.search(r"/capture/.*/([^/]+)\.pdf\.json$", f)
    if m:
        caps.setdefault(m.group(1), []).append(f)
inst = {p.stem for p in Path("docs/analysis-note/figures").glob("*.pdf")}
print("included stems:", len(inc), "| installed pdfs:", len(inst))
nocap = []
for stem in (sorted(caps) if "--all" in sys.argv else inc):
    cs = caps.get(stem)
    if not cs:
        nocap.append(stem); continue
    # the latest record by commit time of the capture file
    def t(f): return int(subprocess.run(["git","log","-1","--format=%ct","--",f],capture_output=True,text=True).stdout or 0)
    cs2 = [f for f in cs if os.path.exists(f[:-5] + ".npz")] or cs
    c = max(cs2, key=t)
    idx = json.load(open(c)); z = np.load(c[:-5] + ".npz") if os.path.exists(c[:-5] + ".npz") else None
    hits = []
    for it in idx:
        ds = it.get("style", {}).get("drawstyle", "default")
        ls = it.get("style", {}).get("linestyle", "-")
        if it["kind"] == "line" and ds.startswith("steps") and ls not in ("None", "none", "", " "):
            if z is None:
                hits.append(f"ax{it['axes']} {ds} (no npz) lab={it['label']!r}"); continue
            xy = z[f"i{it['i']}.xy"]; x = xy[:, 0]
            hits.append(f"ax{it['axes']} {ds} n={len(x)} x[:4]={np.round(x[:4],3).tolist()} x[-2:]={np.round(x[-2:],3).tolist()} lab={it['label']!r}")
    print(f"{stem}: {len(cs)} captures, latest {c.split('/methods/')[1].split('/')[0]}; step lines {len(hits)}")
    for h in hits: print("    ", h)
print("NO CAPTURE:", nocap)
