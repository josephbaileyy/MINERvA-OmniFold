"""Parse the 48 P2N runs and tabulate before/after preferences.

Order AB: Document A = before (r12), B = after (final1). Order BA: A = after, B = before.
Fails loudly if any expected run is missing or unparseable.
"""
import json
import math
import re
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent
RUNS = P / "runs"
IDS = [f"N{i:02d}" for i in range(1, 13)]
MODELS = ["sol2", "gemini"]


def parse(path):
    t = path.read_text()
    w = re.findall(r"^\**\s*WINNER:\**\s*\**\s*([AB])\b", t, re.M)
    s = re.findall(r"^\**\s*STRENGTH:\**\s*\**\s*([123])\b", t, re.M)
    if len(w) != 1 or len(s) != 1:
        raise SystemExit(f"UNPARSEABLE {path.name}: winners={w} strengths={s}")
    reasons = re.findall(r"^\s*([123])\.\s*(.+)$", t.split("REASONS", 1)[-1], re.M)
    return w[0], int(s[0]), [r[1].strip() for r in reasons]


def binom_two_sided(k, n):
    """Exact two-sided sign test p-value for k successes of n at p=0.5."""
    if n == 0:
        return float("nan")
    pk = [math.comb(n, i) / 2**n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


rows = []
for m in MODELS:
    for i in IDS:
        rec = {"piece": i, "model": m}
        for o in ("AB", "BA"):
            f = RUNS / f"P2N__{i}-{o}__{m}__r1.md"
            if not f.exists():
                raise SystemExit(f"MISSING {f.name}")
            letter, strength, reasons = parse(f)
            after_letter = "B" if o == "AB" else "A"
            rec[o] = {"letter": letter, "strength": strength,
                      "winner": "after" if letter == after_letter else "before",
                      "reasons": reasons}
        rec["agree"] = rec["AB"]["winner"] == rec["BA"]["winner"]
        # position: which slot won in each order
        rec["slots"] = rec["AB"]["letter"] + rec["BA"]["letter"]
        # signed score: + for after, strength-weighted, summed over orders
        rec["score"] = sum((1 if rec[o]["winner"] == "after" else -1) * rec[o]["strength"] for o in ("AB", "BA"))
        rows.append(rec)

out = {"rows": rows, "summary": {}}
print(f"{'piece':6}{'model':8}{'AB(A=bef)':>12}{'BA(A=aft)':>12}  agree  slots  score")
for r in rows:
    ab, ba = r["AB"], r["BA"]
    print(f"{r['piece']:6}{r['model']:8}{ab['winner']+'/'+str(ab['strength']):>12}{ba['winner']+'/'+str(ba['strength']):>12}"
          f"  {'yes' if r['agree'] else 'FLIP':5}  {r['slots']:5}  {r['score']:+d}")

print()
for m in MODELS + ["both"]:
    rs = [r for r in rows if m == "both" or r["model"] == m]
    runs = [r[o] for r in rs for o in ("AB", "BA")]
    n_after = sum(x["winner"] == "after" for x in runs)
    agree = [r for r in rs if r["agree"]]
    ag_after = sum(r["AB"]["winner"] == "after" for r in agree)
    flips = [r for r in rs if not r["agree"]]
    slotA = sum(x["letter"] == "A" for x in runs)
    # per-piece sign test on strength-weighted score (ties dropped)
    pos = sum(r["score"] > 0 for r in rs); neg = sum(r["score"] < 0 for r in rs); ties = sum(r["score"] == 0 for r in rs)
    s = {
        "runs": len(runs), "after_wins_runs": n_after,
        "pieces": len(rs), "agree_pieces": len(agree), "agree_after": ag_after,
        "agree_before": len(agree) - ag_after, "flip_pieces": len(flips),
        "flip_pieces_slotA_both": sum(r["slots"] == "AA" for r in flips),
        "flip_pieces_slotB_both": sum(r["slots"] == "BB" for r in flips),
        "slot_A_wins_runs": slotA,
        "sign_test_runs_p": binom_two_sided(n_after, len(runs)),
        "sign_test_agree_pieces_p": binom_two_sided(ag_after, len(agree)),
        "sign_test_position_p": binom_two_sided(slotA, len(runs)),
        "score_pos": pos, "score_neg": neg, "score_tie": ties,
        "sign_test_score_p": binom_two_sided(pos, pos + neg),
    }
    out["summary"][m] = s
    print(m, json.dumps(s))

(P / "results.json").write_text(json.dumps(out, indent=1))
