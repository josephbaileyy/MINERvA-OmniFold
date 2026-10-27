"""P1N adoption test for n3, under the director's noise rule (2026-10-26): an adopted piece reverts only if its sol2
2-run mean falls by more than 0.25 below its baseline mean; a fall of exactly 0.25 gets 2 more sol2 runs (files
<piece>.sol2.3.md and .4.md) and reverts only if the 4-run mean falls below the baseline mean. Gemini is reported
beside it, not used. usage: p1n_adopt.py <baseline p1n dir> <final p1n dir>"""
import re, sys
from pathlib import Path
B, F = Path(sys.argv[1]), Path(sys.argv[2])
ADOPTED = ["N02", "N03", "N04", "N06", "N08", "N09", "N11", "N12", "N13"]
NOTE = {"N01": "not adopted (base + the audit's ACC-A2)", "N10b": "not adopted (= base)", "N07": "not adopted (= base)",
        "N05": "unchanged", "N10a": "unchanged (layout only)", "N14": "unchanged (layout only)"}
def r(d, p, m, k):
    f = d / f"{p}.{m}.{k}.md"
    x = re.search(r"^RATING:\s*([0-9.]+)", f.read_text(), re.M) if f.exists() else None
    return float(x.group(1)) if x else None
order = ["N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08", "N09", "N10a", "N10b", "N11", "N12", "N13", "N14"]
print("| piece | sol2 base | sol2 final | Δ sol2 (mean) | gemini base | gemini final | adoption test |")
print("|---|---|---|---:|---:|---:|---|")
need, fails, tot = [], [], {"sb": [], "sf": [], "gb": [], "gf": []}
fmt = lambda v: ", ".join(f"{x:g}" for x in v)
for p in order:
    sb = [r(B, p, "sol2", k) for k in (1, 2)]; sf = [r(F, p, "sol2", k) for k in (1, 2)]
    gb, gf = r(B, p, "gemini", 1), r(F, p, "gemini", 1)
    tot["sb"] += sb; tot["sf"] += sf; tot["gb"].append(gb); tot["gf"].append(gf)
    mb, mf = sum(sb) / 2, sum(sf) / 2; d = mf - mb
    if p in ADOPTED:
        if d < -0.25 - 1e-9:
            v = "**FAILS (fall > 0.25): reverts**"; fails.append(p)
        elif abs(d + 0.25) < 1e-9:
            extra = [r(F, p, "sol2", k) for k in (3, 4)]
            if None in extra:
                v = "fall of exactly 0.25: **2 more sol2 runs needed**"; need.append(p)
            else:
                m4 = (sum(sf) + sum(extra)) / 4
                v = f"fall of 0.25; 4-run mean {m4:.3f} vs base {mb:.2f}: " + ("**reverts**" if m4 < mb - 1e-9 else "holds")
                if m4 < mb - 1e-9: fails.append(p)
        else:
            v = "holds"
    else:
        v = f"not applicable ({NOTE[p]})"
    print(f"| {p} | {fmt(sb)} | {fmt(sf)} | {d:+.2f} | {gb:g} | {gf:g} | {v} |")
m = lambda v: sum(v) / len(v)
print(f"\nmeans over 15 pieces: sol2 base {m(tot['sb']):.3f}, final {m(tot['sf']):.3f}; gemini base {m(tot['gb']):.3f}, final {m(tot['gf']):.3f}")
print("needs 2 more sol2 runs:", need or "none"); print("reverts:", fails or "none")
