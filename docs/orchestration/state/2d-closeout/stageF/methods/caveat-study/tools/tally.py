"""tally.py -- verify every inventory quote against its document and tabulate the caveat measures.

usage: CAVEAT_WORK=<dir holding blind/> python3 -I tools/tally.py [--self-test]
Reads inv/<doc>.tsv (this study's directory) and $CAVEAT_WORK/blind/<doc>.txt (the blinded texts, which are not
committed; INPUTS.sha256 pins them) for every document in SETS. A row is KEPT only if its quote, after
whitespace is collapsed and line-end hyphens are joined, is a substring of the document text treated the same way.
Writes tables/*.md and prints a summary. --self-test plants a false quote and a true one and checks the verdicts.
"""
import collections
import csv
import re
import sys
from pathlib import Path

H = Path(__file__).resolve().parent.parent  # the study directory: inv/, tables/
import os
T = Path(os.environ.get("CAVEAT_WORK", H))  # holds blind/
WORDS = {  # blinded words, blindcount.py / blind_note.py
    "2504.06857": 7703, "2002.12496": 7980, "2205.05084": 8038, "2301.03700": 9321, "2110.13372": 10310,
    "2102.03346": 11922, "2101.03779": 30678, "1612.05824": 31016, "2007.06722": 35620, "ours-paper": 8785,
    "ours-note": 53018,
}
SETS = {"P": ["2504.06857", "2002.12496", "2205.05084", "2301.03700", "2110.13372", "2102.03346"],
        "N": ["2101.03779", "1612.05824", "2007.06722"], "ours-paper": ["ours-paper"], "ours-note": ["ours-note"]}
PARTS = {"ours-note": ["ours-note-body", "ours-note-app"]}
KINDS = "abcde"
NEG = re.compile(r"\b(not|no|none|neither|nor|cannot|never|without|n't)\b|\bun(tested|measured|validated|known|established|assessed)\b", re.I)
NUM = re.compile(r"\d|%")
LOCS = ["abstract", "intro", "inline", "syst", "limits", "concl", "appendix", "caption"]


def norm(t):
    t = t.replace("­", "")
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)  # a word hyphenated at a line end
    return re.sub(r"\s+", " ", t).strip()


def nojoin(t):
    return re.sub(r"\s+", " ", t.replace("­", "")).strip()


def found(q, text_n, text_h):
    q = re.sub(r"\s+", " ", q).strip()
    return q in text_h or norm(q) in text_n


def load(doc):
    rows, bad, seen, merged = [], [], {}, []
    for part in PARTS.get(doc, [doc]):
        raw = (T / "blind" / f"{part}.txt").read_text(encoding="utf-8", errors="replace")
        tn, th = norm(raw), nojoin(raw)
        p = H / "inv" / f"{part}.tsv"
        if not p.exists():
            return None, None
        with p.open(encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if not r.get("kind") or r["kind"].strip() not in KINDS:
                    bad.append((part, r.get("n"), "bad kind", r.get("kind")))
                    continue
                if not found(r.get("quote") or "", tn, th):
                    bad.append((part, r.get("n"), "quote not found", (r.get("quote") or "")[:80]))
                    continue
                r["part"] = part
                key = (part, r["kind"].strip(), re.sub(r"\s+", " ", r["quote"]).strip())
                iss = (r.get("issue") or "").strip().lower()
                # one instance per sentence and kind (codebook rule): a sentence split into several issue rows merges;
                # the same sentence printed again elsewhere (same issue, e.g. a repeated caption) stays a new instance
                if key in seen and iss not in seen[key]:
                    merged.append(key); continue
                seen.setdefault(key, set()).add(iss)
                rows.append({k: (v or "").strip() for k, v in r.items()})
    return rows, bad


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "–"


def main():
    out = H / "tables"; out.mkdir(exist_ok=True)
    per = {}
    lines = ["| set | document | words | kept rows | dropped (quote not found or bad kind) | " +
             " | ".join(f"({k}) /1k" for k in KINDS) + " | all /1k | distinct issues | rows per issue | distinct /1k | negation word | assigned |",
             "|---" * (11 + len(KINDS)) + "|"]
    for s, docs in SETS.items():
        for d in docs:
            rows, bad = load(d)
            if rows is None:
                lines.append(f"| {s} | {d} | {WORDS[d]} | (not coded yet) |" + " |" * (4 + len(KINDS))); continue
            per[d] = rows
            w = WORDS[d] / 1000
            c = collections.Counter(r["kind"] for r in rows)
            iss = len({(r["kind"], r["issue"].lower()) for r in rows})
            lines.append(f"| {s} | {d} | {WORDS[d]:,} | {len(rows)} | {len(bad)} | " +
                         " | ".join(f"{c[k] / w:.2f}" for k in KINDS) +
                         f" | {len(rows) / w:.2f} | {iss} | {len(rows) / iss if iss else 0:.2f} | {iss / w:.2f}"
                         f" | {pct(sum(bool(NEG.search(r['quote'])) for r in rows), len(rows))}"
                         f" | {pct(sum(r['assigned'] in ('yes', 'partly') for r in rows), len(rows))} |")
            (out / f"dropped-{d}.txt").write_text("\n".join("\t".join(map(str, b)) for b in bad) + "\n")
    (out / "rates.md").write_text("\n".join(lines) + "\n")
    # placement, phrasing, quantification, assignment, per set and kind
    agg = ["| set | kind | rows | " + " | ".join(LOCS) + " | pos (coder) | quantified (coder) | assigned yes/partly | rows per issue | negation word (mech.) | number (mech.) |",
           "|---" * (10 + len(LOCS)) + "|"]
    for s, docs in SETS.items():
        for k in KINDS:
            rs = [r for d in docs if d in per for r in per[d] if r["kind"] == k]
            if not rs:
                agg.append(f"| {s} | ({k}) | 0 |" + " |" * (len(LOCS) + 6)); continue
            lc = collections.Counter(r["loc"] for r in rs)
            iss = len({(r["part"].split("-")[0] if r["part"].startswith("ours-note") else r["part"], r["issue"].lower()) for r in rs})
            agg.append(f"| {s} | ({k}) | {len(rs)} | " + " | ".join(pct(lc[l], len(rs)) for l in LOCS) +
                       f" | {pct(sum(r['polarity'] == 'pos' for r in rs), len(rs))}"
                       f" | {pct(sum(r['quant'] == 'yes' for r in rs), len(rs))}"
                       f" | {pct(sum(r['assigned'] in ('yes', 'partly') for r in rs), len(rs))}"
                       f" | {len(rs) / iss:.2f} | {pct(sum(bool(NEG.search(r['quote'])) for r in rs), len(rs))}"
                       f" | {pct(sum(bool(NUM.search(r['quote'])) for r in rs), len(rs))} |")
    (out / "placement.md").write_text("\n".join(agg) + "\n")
    print((out / "rates.md").read_text()); print((out / "placement.md").read_text())


def self_test():
    text = "The unfolding is not vali-\ndated for   high W.\nAn effect is neglected."
    tn, th = norm(text), nojoin(text)
    cases = [("The unfolding is not validated for high W.", True), ("An effect is neglected.", True),
             ("The unfolding is validated for high W.", False), ("An effect is included.", False)]
    ok = all(found(q, tn, th) == want for q, want in cases)
    print("SELF-TEST ::", "PASS" if ok else "FAIL", f"({len(cases)} cases: two true quotes kept, two false dropped)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main()
