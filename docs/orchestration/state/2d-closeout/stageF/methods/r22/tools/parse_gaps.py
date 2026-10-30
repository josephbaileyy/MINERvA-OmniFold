"""Parse r22's gap-prompt outputs (G1, G1N), locate each quote in the rated text, and score the planted controls.

usage: python3 -I parse_gaps.py R22_DIR ANALYZE_PY      writes R22_DIR/gap/gaps.json and prints a summary

Quote location is the calibration's rule: key() and locate() are taken from ANALYZE_PY
(rater-calibration/tools/analyze.py) by ast and executed alone, since that file runs on import.
Run files: R22_DIR/gap/runs/G__<input>__<model>.txt; the rated text is gap/inputs/<input>/{manuscript,chapter}.txt.
A control run passes when at least 2 of its 3 plants are quoted (a located quote whose span lies within a plant)."""
import ast
import json
import re
import sys
from pathlib import Path

R, AN = Path(sys.argv[1]), Path(sys.argv[2])
src = AN.read_text()
ns = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("key", "locate"):
        exec(compile(ast.Module([node], []), str(AN), "exec"), ns)
exec("import unicodedata, re", ns)
sys.path.insert(0, str(Path(__file__).parent))
from plants import PLANTS  # noqa: E402

ITEM = re.compile(r'^\s*(\d+)\.\s*QUOTE:\s*["“](.*?)["”]\s*$', re.M)


def field(block, name):
    m = re.search(rf"^\s*{name}:\s*(.*)$", block, re.M)
    return m.group(1).strip() if m else ""


def parse(t):
    m = re.search(r"CURRENT RATING:\s*\**\s*([0-5](?:\.\d+)?)", t)
    starts = list(ITEM.finditer(t))
    gaps = []
    for i, s in enumerate(starts):
        block = t[s.end():starts[i + 1].start() if i + 1 < len(starts) else len(t)]
        sh = re.search(r"(\d+(?:\.\d+)?)", field(block, "SHARE"))
        gaps.append({"n": int(s.group(1)), "quote": s.group(2), "scope": field(block, "SCOPE"),
                     "problem": field(block, "PROBLEM"), "change": field(block, "CHANGE"),
                     "share": float(sh.group(1)) if sh else None})
    e = re.search(r"^\s*ENOUGH:\s*(.*)$", t, re.M)
    return (float(m.group(1)) if m else None), gaps, (e.group(1).strip() if e else "")


out = {}
for f in sorted((R / "gap" / "runs").glob("G__*.txt")):
    _, inp, model = f.stem.split("__")
    d = R / "gap" / "inputs" / inp
    text = next(p for p in (d / "manuscript.txt", d / "chapter.txt") if p.exists()).read_text(encoding="utf-8")
    ns["doc_key"] = {inp: ns["key"](text)}
    rating, gaps, enough = parse(f.read_text(encoding="utf-8"))
    plant_spans = []
    for pl in PLANTS:
        k = ns["key"](pl)
        i = ns["doc_key"][inp].find(k)
        plant_spans.append((i, i + len(k)) if i >= 0 else None)
    for g in gaps:
        loc = ns["locate"](inp, g["quote"])
        g["located"] = loc[2] if loc else None
        g["plant"] = next((j + 1 for j, sp in enumerate(plant_spans) if sp and loc and sp[0] <= loc[0] and loc[1] <= sp[1]),
                          None)
    shares = [g["share"] for g in gaps if g["share"] is not None]
    rec = {"input": inp, "model": model, "rating": rating, "enough": enough, "gaps": gaps,
           "share_sum": sum(shares), "n_unlocated": sum(1 for g in gaps if not g["located"])}
    if inp.endswith("-ctl"):
        found = sorted({g["plant"] for g in gaps if g["plant"]})
        rec["plants_found"] = found
        rec["control_pass"] = len(found) >= 2
    out[f.stem] = rec
(R / "gap" / "gaps.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for k, r in out.items():
    extra = f" plants={r['plants_found']} {'PASS' if r['control_pass'] else 'FAIL'}" if "control_pass" in r else ""
    print(f"{k:28s} rating={r['rating']} gaps={len(r['gaps'])} share_sum={r['share_sum']:.0f} "
          f"unlocated={r['n_unlocated']}{extra}")
