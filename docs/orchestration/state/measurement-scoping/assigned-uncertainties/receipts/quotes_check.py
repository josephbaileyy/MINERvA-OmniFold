"""Check every comparator quote in U-PLAN.md section 1 as a substring of its text (whitespace collapsed, line-end
hyphens joined), the caveat study's tally.py rule. Usage: quotes_check.py U-PLAN.md TEXTDIR"""
import re
import sys
from pathlib import Path

DOCS = {"P1": "2504.06857", "P2": "2002.12496", "P3": "2205.05084", "P4": "2301.03700", "P5": "2110.13372",
        "P6": "2102.03346", "N1": "2101.03779", "2004.05434": "2004.05434", "2310.06082": "2310.06082"}


def norm(s):
    s = re.sub(r"-\s*\n\s*", "", s)
    return re.sub(r"\s+", " ", s).strip()


plan, tdir = Path(sys.argv[1]).read_text(), Path(sys.argv[2])
sec = plan.split("## 1. Typical practice", 1)[1].split("## 2.", 1)[0]
texts = {k: norm((tdir / f"{v}.txt").read_text()) for k, v in DOCS.items()}
n = bad = 0
for line in sec.splitlines():
    if not line.startswith("|") or line.startswith("|---") or line.startswith("| doc"):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    ids = [k for k in DOCS if re.search(rf"(^|\W){re.escape(k)}(\W|$)", cells[0])]
    for q in re.findall(r"\"([^\"]+)\"", cells[2]):
        # a quote prefixed "P2:" names its own document
        pre = re.search(rf"(\w[\w.]*): \"{re.escape(q)}\"", cells[2])
        cand = [pre.group(1)] if pre else ids
        hit = [k for k in cand if norm(q) in texts.get(k, "")]
        n += 1
        bad += not hit
        print(("OK  " if hit else "MISS"), ",".join(hit or cand), "|", q[:90])
for q in re.findall(r"both regularised and unregularised results\s+are reported\.", sec):
    n += 1
    ok = norm(q) in texts["2004.05434"]
    bad += not ok
    print("OK  " if ok else "MISS", "2004.05434 |", norm(q))
print(f"{n} quotes, {bad} missing")
sys.exit(1 if bad else 0)
