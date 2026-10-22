#!/usr/bin/env python3
"""Count project-internal terms in the PRINTED text of the editable note files.

usage: scan_terms.py <dir holding the .tex files> [--show TERM] [--md]

Printed text: LaTeX comments removed; the arguments of \\label, \\ref, \\eqref, \\cite, \\input, \\includegraphics and
similar non-printing commands removed (so a label such as sec:eavailw-adopted is not counted as prose); whitespace
collapsed so a term broken across two source lines is still one match. The verbatim quotation of the joint-test
specification (sec_joint.tex, the quote environment) is counted separately as QUOTE because it must stay verbatim.
"""
import re
import sys
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = (HERE / "files.txt").read_text().split()

# term -> regex over printed text. Grouped as in GLOSSARY.md.
TERMS = {
    # status vocabulary
    "in use": r"\bin use\b",
    "adopt* (status sense)": r"\badopt(?:ed|ion|s)?\b",
    "constructed but not adopted / in use": r"constructed,? (?:but )?not (?:adopted|in use)",
    "adoption gate": r"adoption gate",
    "quotable": r"\bquotable\b",
    "candidate (covariance/product)": r"\bcandidates?\b",
    "report-only": r"report-only",
    "frozen": r"\bfrozen\b",
    "re-qualify": r"re-qualify",
    # background treatment
    "footing / footed": r"\bfoot(?:ing|ings|ed)\b",
    "negweight-refined (label in prose)": r"negweight-refined|Negweight-refined",
    # lateral systematics
    "dump-all": r"\bdump-all\b",
    "dump(s) (event-loop output)": r"\bdumps?\b",
    "selection-complete": r"selection-complete",
    "active-lateral / active-universe": r"active[- ](?:lateral|universe)",
    "support-limited": r"support-limited",
    "universe-complete": r"[Uu]niverse-complete",
    # campaign / repository labels
    "J28": r"\bJ28\b",
    "VL/OI/KI tracker id": r"\b(?:VL|OI|KI)-?\d+\b",
    "KNOWN_ISSUES": r"KNOWN\\?_ISSUES",
    "Stage-1/Stage-2": r"\bStage-\d\b",
    "standard-P4": r"standard-P4",
    "Q (2D covariance name)": r"\bfor Q\b",
    "B3 label": r"\bB3\b",
    "FPS (abbrev.)": r"\bFPS\b",
    "cv / mean variant label": r"\\texttt\{(?:cv|mean)\}",
    "lgbm / exact / hist (backend names in prose)": r"\blgbm\b|\\texttt\{exact\}|\\emph\{exact\}|\bexact-GBT\b",
    # bookkeeping
    "digest": r"\bdigests?\b",
    "receipt / receipted": r"\breceipt(?:s|ed)?\b",
    "lane": r"\blanes?\b",
    "gate (process sense)": r"migration gate|gated battery|gate fails|adoption gate",
    "discharge": r"\bdischarg\w*",
    "ledger": r"\bledger\b|ledger-verified",
    "NONQUOTABLE": r"NONQUOTABLE",
    "the design record": r"design record",
    "self-validated": r"self-validated",
    "campaign's": r"campaign's",
    "contract": r"\bcontract\b",
    "sibling": r"\bsibling",
    "these bytes / this object": r"these bytes|this object|object's own",
    "rollup": r"\brollup\b",
    "omnifile": r"omnifile",
    "headline (as jargon)": r"\bheadline\b",
    # coined labels
    "anchor": r"\banchors?\b",
    "home(s)": r"\b[Hh]omes?\b",
    "truth-tree authoritative / invariants": r"authoritative:|Two invariants|completeness invariants",
    "record-only": r"[Rr]ecord-only",
    "replay": r"\b[Rr]eplays?\b",
    "launcher": r"\blaunchers?\b",
    "MnvTune": r"MnvTune",
    "exact-split (kept term)": r"exact-split",
    # code identifiers in prose
    "CVUniverse::": r"CVUniverse::",
    "hXSec": r"hXSec",
    "--bkg-mode": r"bkg-mode(?!-pins)",
    "App. G tag pointer (kept)": r"App\.~\s*,\s*\\texttt\{|App\.~\s*\(\s*\\texttt\{",
}

NONPRINTING = (r"label|ref|eqref|pageref|autoref|cref|Cref|cite|citep|citet|nocite|includegraphics|input|include"
               r"|addcontentsline|begin|end|setcounter|providecommand")
NONPRINTING_RE = re.compile(r"\\(?:%s)\*?(?:\[[^\]]*\])*\{[^{}]*\}" % NONPRINTING)


def printed(path: Path) -> str:
    lines = [re.sub(r"(?<!\\)%.*", "", l) for l in path.read_text().splitlines()]
    text = " ".join(lines)
    text = NONPRINTING_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text)


def split_quote(name: str, text: str):
    if name != "sec_joint.tex":
        return text, ""
    m = re.search(r"\\begin\{quote\}.*?\\end\{quote\}", text)
    # \begin/\end were stripped as non-printing; find the quote by its first and last verbatim phrases instead.
    a = text.find("``below the fine grid the null truth")
    b = text.find("and as a drawn residual term''")
    if a < 0 or b < 0:
        return text, ""
    b += len("and as a drawn residual term''")
    return text[:a] + text[b:], text[a:b]


def count(root: Path):
    out = collections.OrderedDict()
    for term, rx in TERMS.items():
        r = re.compile(rx)
        per = collections.Counter()
        quote = 0
        for f in FILES:
            p = root / f
            if not p.exists():
                continue
            body, q = split_quote(f, printed(p))
            n = len(r.findall(body))
            if n:
                per[f.replace(".tex", "")] += n
            quote += len(r.findall(q))
        out[term] = (per, quote)
    return out


def main(argv):
    root = Path(argv[1])
    if "--show" in argv:
        term = argv[argv.index("--show") + 1]
        r = re.compile(TERMS[term])
        for f in FILES:
            p = root / f
            for i, l in enumerate(p.read_text().splitlines(), 1):
                l2 = NONPRINTING_RE.sub(" ", re.sub(r"(?<!\\)%.*", "", l))
                if r.search(l2):
                    print(f"{f}:{i}: {l.strip()[:220]}")
        return 0
    res = count(root)
    if "--md" in argv:
        print("| term | total | by file | in verbatim quote |")
        print("|---|---|---|---|")
        for term, (per, q) in res.items():
            print(f"| {term} | {sum(per.values())} | " + (", ".join(f"{k} {v}" for k, v in per.most_common()) or "--")
                  + f" | {q or ''} |")
    else:
        for term, (per, q) in res.items():
            print(f"{term:45s} {sum(per.values()):4d}  " + ", ".join(f"{k}:{v}" for k, v in per.most_common())
                  + (f"   [quote: {q}]" if q else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
