#!/usr/bin/env python3
"""SCOPING.md section 6: list every 32-element numeric array (H2 box granularity) in the committed JSON files that
name "H2", h2_cells or "h2". Prints key paths only, never values. Usage: python3 -I h2_json_scan.py <repo>"""
import json, subprocess, sys
repo = sys.argv[1]
files = subprocess.run(["git", "-C", repo, "grep", "-l", "-I", "-E", '"H2"|h2_cells|"h2"', "--", "*.json"],
                       capture_output=True, text=True, check=True).stdout.split()
print(f"files {len(files)}")
for f in files:
    d = json.load(open(f"{repo}/{f}"))
    hits = []
    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{p}/{k}")
        elif isinstance(o, list):
            if len(o) == 32 and all(isinstance(x, (int, float, type(None))) for x in o):
                hits.append(p)
            elif o and isinstance(o[0], (dict, list)):
                walk(o[0], p + "[0]")
    walk(d, "")
    print(f"== {f} {len(hits)}")
    for h in hits:
        print("   ", h)
