"""P1N adoption test (director, 2026-10-26): for each adopted piece, sol2's mean of 2 runs on the final text must not
fall below its n1 final mean (the n2 baseline, outline line 136); gemini is reported beside it, not used. usage: adopt.py <base p1n dir> <final p1n dir>"""
import re, sys
from pathlib import Path
B, F = Path(sys.argv[1]), Path(sys.argv[2])
ADOPTED = ["N01", "N02", "N03", "N04", "N06", "N07", "N08", "N09", "N10b", "N11", "N12", "N13"]
NOTE = {"N05": "byte-identical to base", "N14": "layout only", "N10a": "not adopted (= base + ACC1, ACC2)"}
def r(d, p, m, k):
    f = d / f"{p}.{m}.{k}.md"
    t = f.read_text() if f.exists() else ""
    x = re.search(r"^RATING:\s*([0-9.]+)", t, re.M)
    return float(x.group(1)) if x else None
pieces = sorted({f.name.split(".")[0] for f in B.glob("N*.md")}, key=lambda s: (int(re.sub(r"\D", "", s)), s))
print("| piece | sol2 base | sol2 final | Δ sol2 (mean) | gemini base | gemini final | adoption test |")
print("|---|---|---|---:|---:|---:|---|")
missing, fails = [], []
tot = {"sb": [], "sf": [], "gb": [], "gf": []}
for p in pieces:
    sb, sf = [r(B, p, "sol2", k) for k in (1, 2)], [r(F, p, "sol2", k) for k in (1, 2)]
    gb, gf = r(B, p, "gemini", 1), r(F, p, "gemini", 1)
    if None in sb + sf + [gb, gf]:
        missing.append(p); print(f"| {p} | {sb} | {sf} | MISSING | {gb} | {gf} | - |"); continue
    tot["sb"] += sb; tot["sf"] += sf; tot["gb"].append(gb); tot["gf"].append(gf)
    d = sum(sf) / 2 - sum(sb) / 2
    if p in ADOPTED:
        verdict = "holds" if d >= 0 else "**FAILS: revert to base**"
        if d < 0: fails.append(p)
    else:
        verdict = f"not applicable ({NOTE[p]})"
    fmt = lambda v: ", ".join(f"{x:g}" for x in v)
    print(f"| {p} | {fmt(sb)} | {fmt(sf)} | {d:+.2f} | {gb:g} | {gf:g} | {verdict} |")
m = lambda v: sum(v) / len(v) if v else float("nan")
print(f"\nmeans over {len(tot['gb'])} pieces: sol2 base {m(tot['sb']):.3f}, final {m(tot['sf']):.3f}; "
      f"gemini base {m(tot['gb']):.3f}, final {m(tot['gf']):.3f}")
print("missing:", missing or "none"); print("adoption-test failures:", fails or "none")
