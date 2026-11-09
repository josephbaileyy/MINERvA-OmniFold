#!/usr/bin/env python3
"""Count "AI-writing" style patterns per 1,000 words (stdlib only).

Usage:
    python3 style_metrics.py file.txt [file2.txt ...]          # table per file
    python3 style_metrics.py --json file.txt [...]              # JSON per file
    python3 style_metrics.py --examples 5 file.txt              # also print matches
    python3 style_metrics.py --rules                            # print the rules only
    python3 style_metrics.py --keep-captions file.txt           # skip caption removal

Every file gets the same normalisation before counting (see `clean`):
  1. rejoin words hyphenated across a line break ("measure-\\nment");
  2. drop figure/table captions: a block starting "FIG. n." / "Figure n:" /
     "TABLE n." / "Table n:" up to the next blank line (at most 25 lines);
  3. drop table-of-contents lines (dot leaders) and lines where fewer than
     half of the whitespace tokens are alphabetic words (equations, numbers);
  4. drop blank-line-delimited blocks of < 12 words with no . ? or !
     (headings, page numbers, running heads, table cells).
Words = whitespace tokens of the cleaned text.  Sentences = the cleaned text
split at . ? ! followed by whitespace and an upper-case letter, digit or
bracket, with a guard for common abbreviations.  All regexes are
case-insensitive.
"""
import argparse
import json
import re
import sys

FLAGS = re.IGNORECASE

# ---------------------------------------------------------------- rules
# Each rule: (key, description, kind, pattern/function).
# kind "regex": count non-overlapping matches in the full cleaned text,
#               sentence by sentence (matches never cross a sentence end).
# kind "sentence": count sentences for which the predicate is true.

AI_VOCAB = (r"delve[sd]?|delving|crucial(?:ly)?|pivotal|underscor(?:e|es|ed|ing)|"
            r"showcas(?:e|es|ed|ing)|testament|tapestry|notably|robust(?:ly|ness)?|"
            r"comprehensive(?:ly)?|intricate|leverag(?:e|es|ed|ing)|seamless(?:ly)?|"
            r"landscapes?|realms?|nuanced|foster(?:s|ed|ing)?|meticulous(?:ly)?")
# "highlight" as a verb: highlights/highlighted/highlighting, or bare
# "highlight" not preceded by a determiner/adjective (which would make it a noun).
HIGHLIGHT_VERB = (r"\bhighlight(?:s|ed|ing)\b|"
                  r"(?<!\ba )(?<!\bthe )(?<!\bkey )(?<!\bone )\bhighlight\b")

ITEM = r"[a-z][\w’'-]*(?: [a-z][\w’'-]*){0,2}"   # 1-3 words, each starting with a letter

# B and C may not open with a subordinator/pronoun (cuts clause-comma false hits)
NOT_CLAUSE = (r"(?!(?:which|that|where|when|while|whose|as|so|but|if|though|although|because|"
              r"since|with|we|it|they|this|these|there|here|then|thus|however)\b)")

HEDGES = {"may", "might", "could", "possibly", "potentially", "appears",
          "suggests", "likely", "approximately", "about"}

FINITE = set("""is are was were be been being am has have had do does did can could
will would shall should may might must follows follow shows show gives give holds hold
remains remain means mean depends depend applies apply agrees agree differs differ fails
fail passes pass covers cover uses use makes make takes take finds find yields yield
lies lie sets set states state reports report tests test reads read changes change
moves move returns return gives seems seem becomes become exists exist contains contain
requires require includes include provides provide""".split())

RULES = [
    ("1_comma_not",
     r'", not X": comma, whitespace, "not", then a word that is not only|yet '
     r"(regex: ,\s+not\s+(?!only\b|yet\b)[a-z])",
     "regex", r",\s+not\s+(?!only\b|yet\b)[a-z]"),
    ("2_not_X_but_Y",
     r'"not X but Y" / "not only ... but (also)": "not", 1-8 tokens without . ; : , '
     r'then "but" (regex: \bnot\s+(?:[^\s.;:]+\s+){1,8}?but\b)',
     "regex", r"\bnot\s+(?:[^\s.;:]+\s+){1,8}?but\b"),
    ("3_rather_than", r'"rather than" (regex: \brather\s+than\b)',
     "regex", r"\brather\s+than\b"),
    ("4_corrective",
     r'corrective framing: (does|do) not establish | is not established | should not be '
     r'read as | should not be confused with | does not show | not shown to',
     "regex",
     r"\b(?:does|do)\s+not\s+establish|\bis\s+not\s+established|\bshould\s+not\s+be\s+read\s+as"
     r"|\bshould\s+not\s+be\s+confused\s+with|\bdoes\s+not\s+show|\bnot\s+shown\s+to\b"),
    ("5_semicolon_chain", "sentences containing >= 2 semicolons",
     "sentence", lambda s: s.count(";") >= 2),
    ("6_copula_avoid",
     r'copula avoidance: serve(s|d)? as | serving as | stand(s)? as | act(s)? as a(n) | '
     r'function(s)? as',
     "regex",
     r"\b(?:serves?|served|serving)\s+as\b|\bstands?\s+as\b|\bacts?\s+as\s+an?\b"
     r"|\bfunctions?\s+as\b"),
    ("7_ai_vocab",
     "AI vocabulary: whole words " + AI_VOCAB.replace("(?:", "(") +
     " plus highlight(s|ed|ing), or bare 'highlight' not after a/the/key/one",
     "regex", r"\b(?:" + AI_VOCAB + r")\b|" + HIGHLIGHT_VERB),
    ("8_triad",
     'triad "A, B(,) and|or C": items of 1-3 words each starting with a letter, B and C '
     "without commas, B and C not opening with which/that/where/when/while/whose/as/so/but/"
     "if/though/although/because/since/with/we/it/they/this/these/there/here/then/thus/"
     "however; a longer list counts once per final 'and/or' (approximate: some clause "
     "commas still match)",
     "regex", ITEM + r", " + NOT_CLAUSE + ITEM + r",? (?:and|or) " + NOT_CLAUSE + ITEM + r"\b"),
    ("9a_fragment_le6_noverb",
     "short fragment: sentence of <= 6 words, opening with a capital, >= 2 words, ending in . ? ! and containing no word from a "
     f"{len(FINITE)}-word list of auxiliaries/common finite verbs",
     "sentence", lambda s: _short_noverb(s)),
    ("9b_sentence_le5",
     "very short sentence: <= 5 words, opening with a capital, >= 2 words, ending in . ? !",
     "sentence", lambda s: _short(s, 5)),
    ("10_didactic",
     r'didactic disclaimer: it is important to note | it should be noted | note that | '
     r'importantly',
     "regex",
     r"\bit\s+is\s+important\s+to\s+note\b|\bit\s+should\s+be\s+noted\b|\bnote\s+that\b"
     r"|\bimportantly\b"),
    ("11_hedge_stack",
     "hedge stacking: sentences with >= 3 tokens from {" + ", ".join(sorted(HEDGES)) + "}",
     "sentence", lambda s: _hedges(s) >= 3),
]


def _words(s):
    return re.findall(r"[A-Za-z][A-Za-z’'-]*", s)


def _short(s, n):
    s = s.strip()
    return (bool(re.search(r"[.?!][)\]”\"’']*$", s)) and len(s.split()) <= n
            and bool(re.match(r"[A-Z]", s)) and len(_words(s)) >= 2)


def _short_noverb(s):
    if not _short(s, 6):
        return False
    return not any(w.lower() in FINITE for w in _words(s))


def _hedges(s):
    return sum(1 for w in _words(s) if w.lower() in HEDGES)


# ---------------------------------------------------------------- cleaning
CAPTION_START = re.compile(r"^\s*(?:FIG\.?|Fig\.|Figure|TABLE|Table)\s*[0-9IVX]+[.:]")
ABBREV = re.compile(r"(?:\b(?i:e\.g|i\.e|cf|vs|al|fig|figs|eq|eqs|ref|refs|sec|secs|sect|"
                    r"tab|approx|resp|no|ch|app|ver)\.|\b[A-Z]\.)$")


def clean(text, keep_captions=False):
    text = text.replace("\f", "\n\n").replace("­", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)        # 1. de-hyphenate line breaks
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):                                  # 2. captions
        if not keep_captions and CAPTION_START.match(lines[i]):
            j = i
            while j < len(lines) and lines[j].strip() and j - i < 25:
                j += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    kept = []
    for ln in out:                                         # 3. junk lines
        toks = ln.split()
        if not toks:
            kept.append("")
            continue
        if re.search(r"(?:\.\s){3,}", ln):
            continue
        alpha = sum(1 for t in toks if re.fullmatch(r"[(\[“\"']?[A-Za-z][A-Za-z’'-]*[)\],.;:?!”\"']*", t))
        if alpha / len(toks) < 0.5:
            continue
        kept.append(ln)
    blocks = re.split(r"\n\s*\n", "\n".join(kept))         # 4. heading-like blocks
    good = [b for b in blocks
            if b.strip() and (re.search(r"[.?!]", b) or len(b.split()) >= 12)]
    return "\n\n".join(" ".join(b.split()) for b in good)


def sentences(text):
    sents = []
    for para in text.split("\n\n"):
        start = 0
        for m in re.finditer(r"[.?!][)\]”\"’']*\s+(?=[A-Z0-9(“\"])", para):
            if ABBREV.search(para[start:m.start() + 1]):
                continue
            sents.append(para[start:m.end()].strip())
            start = m.end()
        if para[start:].strip():
            sents.append(para[start:].strip())
    return sents


# ---------------------------------------------------------------- scoring
def score(text, keep_captions=False, n_examples=0):
    ct = clean(text, keep_captions)
    words = len(ct.split())
    sents = sentences(ct)
    res = {"words": words, "sentences": len(sents), "patterns": {}}
    for key, desc, kind, pat in RULES:
        hits = []
        if kind == "regex":
            rx = re.compile(pat, FLAGS)
            for s in sents:
                for m in rx.finditer(s):
                    hits.append((m.group(0), s))
        else:
            hits = [("", s) for s in sents if pat(s)]
        entry = {"count": len(hits),
                 "per_1000": round(1000.0 * len(hits) / words, 3) if words else 0.0}
        if key == "7_ai_vocab":
            bd = {}
            for g, _ in hits:
                w = g.lower()
                bd[w] = bd.get(w, 0) + 1
            entry["breakdown"] = dict(sorted(bd.items(), key=lambda kv: -kv[1]))
        if n_examples:
            entry["examples"] = [{"match": g, "sentence": s[:300]} for g, s in hits[:n_examples]]
        res["patterns"][key] = entry
    return res


def print_rules(fh=sys.stdout):
    for key, desc, kind, pat in RULES:
        print(f"{key:24s} [{kind}] {desc}", file=fh)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--examples", type=int, default=0, help="matches to show per pattern")
    ap.add_argument("--keep-captions", action="store_true")
    ap.add_argument("--rules", action="store_true", help="print the rules and exit")
    a = ap.parse_args(argv)
    if a.rules or not a.files:
        print_rules()
        return 0
    allres = {}
    for f in a.files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            allres[f] = score(fh.read(), a.keep_captions, a.examples)
    if a.json:
        json.dump(allres, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return 0
    print("RULES (case-insensitive):")
    print_rules()
    for f, r in allres.items():
        print(f"\n== {f}: {r['words']} words, {r['sentences']} sentences")
        for key, e in r["patterns"].items():
            print(f"  {key:24s} count={e['count']:5d}  per_1000={e['per_1000']:7.3f}")
            if "breakdown" in e and e["breakdown"]:
                print("      " + ", ".join(f"{k}:{v}" for k, v in e["breakdown"].items()))
            for ex in e.get("examples", []):
                print(f"      [{ex['match']}] {ex['sentence'][:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
