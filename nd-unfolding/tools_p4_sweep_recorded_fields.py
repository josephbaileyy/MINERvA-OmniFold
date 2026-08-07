#!/usr/bin/env python3
"""Mechanical sweep of the standard P4 lane (repair-6 item 2).

Two enumerations, grep-level, no judgement in the extraction step:
  A. every field WRITTEN into a manifest/receipt, and whether its name ever appears
     in a comparison context anywhere in the lane;
  B. every named PASS-gate label, and what the gate's body actually does.

The point is that the list exists as a checkable artifact. Last round's sweep was a pass I
performed and it missed an item on its own list.
"""
import json, re, subprocess, sys
from pathlib import Path

ND = Path(__file__).resolve().parent   # re-runnable from any checkout
MODULES = ["p4_lib.py", "p4_evidence.py", "p4_validate_active_lateral.py",
           "p4_build_components.py", "p4_project_4d.py", "p4_adopt_standard.py",
           "p4_check_receipt.py", "p4_lateral_replace.py"]
SHELL = ["run_p4_standard.sh", "run_p4_unfold_std.sh", "run_p4_merge_audit_std.sh"]

src = {m: (ND / m).read_text() for m in MODULES if (ND / m).exists()}
sh = {s: (ND / s).read_text() for s in SHELL if (ND / s).exists()}
allsrc = "\n".join(src.values()) + "\n" + "\n".join(sh.values())

# ---------- A. fields written into products ----------
written = {}          # field -> set(files that write it)
# python:  man["x"] = ... / out["x"] = ... / rec["x"] = ... / prov["x"] = ... / "x": value
for f, s in src.items():
    for m in re.finditer(r'\b(?:man|out|rec|prov|foot|ids)\["([a-zA-Z0-9_]+)"\]\s*=', s):
        written.setdefault(m.group(1), set()).add(f)
    # dict literals assigned into those products
    for m in re.finditer(r'"([A-Za-z][a-zA-Z0-9_]{2,})"\s*:', s):
        written.setdefault(m.group(1), set()).add(f)
# shell: printf JSON keys
for f, s in sh.items():
    for m in re.finditer(r'"([a-z][a-zA-Z0-9_]{2,})":"', s):
        written.setdefault(m.group(1), set()).add(f)

# ---------- is the field ever COMPARED? ----------
# a comparison = the name appears adjacent to ==, !=, <=, >=, or inside require/need with a
# second operand; presence-only = only `in`, `is not None`, or bare truthiness.
def classify(field):
    compared, presence = [], []
    for f, s in {**src, **sh}.items():
        for line in s.splitlines():
            if field not in line:
                continue
            if line.lstrip().startswith("#"):
                continue
            has_cmp = bool(re.search(r'(==|!=|<=|>=|<|>)', line))
            pres_only = bool(re.search(
                rf'(is not None|is None|"{field}" (?:not )?in |\.get\("{field}"\)\s*[,)])', line))
            if has_cmp:
                compared.append((f, line.strip()[:110]))
            elif pres_only:
                presence.append((f, line.strip()[:110]))
    return compared, presence

IGNORE = {"note", "reason", "title", "help", "type", "default", "action", "required",
          "gates", "result", "endpoints", "merged", "census", "identities", "config",
          "footing", "tree_entries", "band_meta", "sha256"}

rows = []
for field in sorted(written):
    if field in IGNORE or len(field) < 4:
        continue
    comp, pres = classify(field)
    if comp:
        continue                      # compared somewhere -> not an instance
    rows.append((field, sorted(written[field]), pres[:2]))

# ---------- B. named PASS-gate labels ----------
gates = []
for f, s in src.items():
    for m in re.finditer(r'gates"\]\.append\("([a-zA-Z0-9_]+)"\)', s):
        gates.append((m.group(1), f))
    for m in re.finditer(r'^def (check_[a-z0-9_]+|require_[a-z0-9_]+|prove_[a-z0-9_]+)',
                         s, re.M):
        gates.append((m.group(1) + "()", f))

print("=" * 78)
print("A. FIELDS WRITTEN INTO A PRODUCT AND NEVER COMPARED ANYWHERE")
print("=" * 78)
for field, files, pres in rows:
    print(f"\n  {field}")
    print(f"    written by : {', '.join(files)}")
    if pres:
        for f, l in pres:
            print(f"    presence   : {f}: {l}")
    else:
        print("    presence   : (recorded only; no check of any kind)")
print(f"\n  TOTAL: {len(rows)} fields")

print()
print("=" * 78)
print("B. NAMED GATES / PASS LABELS")
print("=" * 78)
for name, f in sorted(set(gates)):
    print(f"  {name:52s} {f}")
print(f"\n  TOTAL: {len(set(gates))} named gates")
