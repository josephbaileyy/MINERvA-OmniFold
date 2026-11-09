#!/usr/bin/env python3
"""Check the short methods paper's round (methods-short-20261109) against its work order and ledgers.

  1. VARIANTS. Every pending key of make_values_fived16.PENDING that a sentence depends on is written once per class:
     at each site (one paragraph of paper_body.tex or main_paper.tex), the classes of its \\fvcase{key}{class}{...}
     equal the key's declared class set, minus the classes declared EMPTY below (a class that prints nothing). Every
     \\fvcase key is declared, and every \\fvcase sits inside an \\fvgroup of the key's own group.
  2. NO NUMBER IN A VARIANT. The text of every \\fvcase, with \\fvval{...}, \\ref{...} and \\cite{...} removed, has no
     digit: filling a result writes no number that the readout does not supply.
  3. EVERY KEY DEFINED. Every \\fvval key of the paper and the Supplement is defined in values_fived16.tex. A key
     inside a pending \\fvgroup is never expanded, so the build cannot catch a missing one; this does.
  4. NUMERALS. Every numeral the paper prints (comments stripped; \\fvval, \\ref, \\cite, \\label, \\includegraphics and
     pointer arguments removed) is printed by the base (round 5, BASE) too, or is in NEW_NUMERALS with its source.
  5. ONCE / GONE. The new sentences the ledger records print exactly once (ONCE); the claims the decision excludes,
     and the internal labels the editor's read lists, print nowhere in the paper (GONE).
  6. FILL TEST (--fill-test, slow). The paper is built once per class index: every pending key set to its i-th
     class (cyclically), so that every variant is typeset at least once; each build must succeed with no
     "[PENDING", no "??" and no undefined reference.
usage: check_round.py <worktree> [--base SHA] [--fill-test]   (exit 1 on any failure)
       check_round.py <worktree> --self-test                  (each planted defect must be caught)"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = "bc8673186"
NOTE = "docs/analysis-note"
FILES = ["paper_body.tex", "main_paper.tex"]
# classes that print nothing by design (variants.md, the rows marked EMPTY)
EMPTY = {**{f"prr-label-{l}-{t}": {"not"} for l in ("fir", "info", "impl", "obs", "stat", "unattr") for t in ("gibuu", "q3")},
         **{f"ll5d-{t}-{r}": {"na"} for t in ("g18", "ar23") for r in ("minus2", "all")}}
# numerals the paper prints that the base does not, each with its source (ledger rows)
NEW_NUMERALS = {"285": "L-12b: re2 partc-r2 receipts/figs/tension_report.txt:55, 1.391 x 205 = 285.2 (in [285.05, 285.26])",
                "136": "L-12b: the note's sec_results.tex:128 (chi2 = 136 on the 73 best-determined directions)"}
ONCE = [
    "and their cross-covariance is not available, so no difference between them can be given a calibrated significance.",
    "The joint-test estimator is the baseline this study characterizes",
    "It is a tested mitigation of the instability, not a replacement:",
    "These results bound what the study shows.",
    "That test is the natural next step.",
    "Every criterion was fixed before the results it grades were seen.",
]
GONE = [r"stabili[sz]ed variant", r"validat\w* the (full|five-observable) distribution", r"detector[- ]inadequa",
        r"locali[sz]ed in", r"\bE_?\{?96", r"\bFD-PRR\b", r"\bLL5D\b", r"\bV-HALF\b", r"\bV-ATLAS\b", r"\bV-PRIOR\b",
        r"\bCOV2D\b", r"\bRS1\b", r"\bENS1\b", r"\bFD-STAB\b", r"BIAS_WORSE", r"Stage~?0c", r"\bPR-[123]",
        r"\bdeclared\b"]


def load_mv(wt):
    spec = importlib.util.spec_from_file_location("mv", wt / NOTE / "make_values_fived16.py")
    mv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv)
    return mv


def strip_comments(t):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", l) for l in t.split("\n"))


def braced(t, i):
    """The content of the brace group opening at t[i] == '{', and the index after it."""
    assert t[i] == "{", t[i:i + 20]
    d, j = 1, i + 1
    while d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 1:j - 1], j


def macro_calls(t, name, nargs):
    """(start, [args]) for every \\name{..}{..} call in t."""
    out = []
    for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", t):
        j, args = m.end(), []
        for _ in range(nargs):
            a, j = braced(t, j)
            args.append(a)
        out.append((m.start(), j, args))
    return out


def check_variants(texts, pending, groups):
    fails = []
    for f, t in texts.items():
        t = strip_comments(t)
        spans = [(s, e, a[0]) for s, e, a in macro_calls(t, "fvgroup", 2)]
        for ln, line in enumerate(re.split(r"\n\s*\n", t), 1):     # a site is one paragraph
            sites = {}
            for _, _, (k, c, _) in macro_calls(line, "fvcase", 3):
                sites.setdefault(k, set()).add(c)
            for k, cs in sites.items():
                if k not in pending:
                    fails.append(f"{f} paragraph {ln}: \\fvcase key {k} is not declared in PENDING")
                    continue
                want = set(pending[k][1] or ()) - EMPTY.get(k, set())
                if cs != want:
                    fails.append(f"{f} paragraph {ln}: {k} has variants {sorted(cs)}, its declared classes are {sorted(want)}")
        for s, _, (k, _, _) in macro_calls(t, "fvcase", 3):
            g = pending.get(k, (None,))[0]
            if not any(a <= s < b and gg == g for a, b, gg in spans):
                fails.append(f"{f}: \\fvcase{{{k}}} is not inside an \\fvgroup{{{g}}}")
        for _, _, (g, _) in macro_calls(t, "fvgroup", 2):
            if g not in groups:
                fails.append(f"{f}: \\fvgroup{{{g}}} is not a declared group")
    return fails


def check_no_number(texts):
    fails = []
    for f, t in texts.items():
        for _, _, (k, c, body) in macro_calls(strip_comments(t), "fvcase", 3):
            b = re.sub(r"\\(fvval|ref|cite|label)\{[^}]*\}", "", body)
            b = re.sub(r"\\fvcase\{[^}]*\}\{[^}]*\}", "", b)          # a nested variant's key and class
            b = re.sub(r"_\{?\d\}?", "", b)                             # a symbol's subscript, as in $q_3$
            if re.search(r"\d", b):
                fails.append(f"{f}: the variant {k}={c} prints a number: {body[:80]!r}")
    return fails


def check_keys(texts, values_tex):
    have = set(re.findall(r"\\@namedef\{fv@([^}]+)\}", values_tex))
    fails = []
    for f, t in texts.items():
        for k in set(re.findall(r"\\fvval\{([^}]+)\}", strip_comments(t))):
            if k not in have:
                fails.append(f"{f}: \\fvval{{{k}}} is not defined in values_fived16.tex")
    return fails


def numerals(t):
    t = strip_comments(t)
    t = "\n".join(l for l in t.split("\n") if not l.lstrip().startswith(r"\begin{tabular}"))   # column widths
    t = re.sub(r"\\(fvval|ref\*?|nsec|napp|cite|label|eqref|includegraphics|fvpending|fvgroup|ssecc?|stab)(\[[^]]*\])?\{[^}]*\}(\{[^}]*\})?", " ", t)
    t = re.sub(r"\\fvcase\{[^}]*\}\{[^}]*\}", " ", t)
    t = re.sub(r"\\(begin|end)\{[^}]*\}(\{[^}]*\})?", " ", t)
    t = re.sub(r"\\[A-Za-z]+", " ", t)
    return set(re.findall(r"\d+(?:\.\d+)?", t))


def check_numerals(cur, base):
    have = set().union(*(numerals(t) for t in base.values()))
    new = set().union(*(numerals(t) for t in cur.values())) - have - set(NEW_NUMERALS)
    return [f"a numeral new to the base, with no source: {n}" for n in sorted(new)]


def check_once_gone(cur):
    fails = []
    body = re.sub(r"\s+", " ", " ".join(strip_comments(t) for t in cur.values()))
    for s in ONCE:
        n = body.count(s)
        if n != 1:
            fails.append(f"ONCE: printed {n} times: {s[:70]!r}")
    for g in GONE:
        m = re.search(g, body)
        if m:
            fails.append(f"GONE: {g!r} prints: ...{body[max(0, m.start() - 40):m.end() + 40]}...")
    return fails


def run(wt, base):
    mv = load_mv(wt)
    cur = {f: (wt / NOTE / f).read_text() for f in FILES}
    old = {f: subprocess.run(["git", "-C", str(wt), "show", f"{base}:{NOTE}/{f}"], capture_output=True, text=True,
                             check=True).stdout for f in FILES}
    supp = (wt / NOTE / "supplemental_body.tex").read_text()
    fails = (check_variants(cur, mv.PENDING, mv.PENDING_GROUPS) + check_no_number(cur)
             + check_keys({**cur, "supplemental_body.tex": supp}, (wt / NOTE / "values_fived16.tex").read_text())
             + check_numerals(cur, old) + check_once_gone(cur))
    return fails


def fill_test(wt):
    """Build the paper once per class index, every pending key at its i-th class; every build must be clean."""
    mv = load_mv(wt)
    n = max(len(c) for _, c in mv.PENDING.values() if c)
    fails = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "docs/analysis-note"
        shutil.copytree(wt / NOTE, d, ignore=shutil.ignore_patterns("archive", "main_*.pdf", "*.aux", "*.log", "*.fls", "*.fdb_latexmk"))
        (Path(td) / "docs/orchestration").mkdir(parents=True)
        (Path(td) / "docs/orchestration/state").symlink_to(wt / "docs/orchestration/state")
        r = subprocess.run(["latexmk", "-pdf", "-g", "-interaction=nonstopmode", "-halt-on-error", "main_note.tex"], cwd=d,
                           capture_output=True, text=True, errors="replace")
        if r.returncode:
            return [f"fill test: main_note build failed ({r.returncode})"]
        base_vals = (d / "values_fived16.tex").read_text()
        head = base_vals.split("\n")
        for i in range(n):
            ver = {}
            for k, (g, cls) in mv.PENDING.items():
                ver[k] = cls[i % len(cls)] if cls else f"X{k.split('-')[-1]}"
            lines = [l for l in head if not re.match(r"\\@namedef\{fv(g|gd|c)@", l)
                     and not any(l.startswith(rf"\@namedef{{fv@{k}}}") for k in mv.PENDING)]
            end = lines.index(r"\makeatother")
            pl = [l.replace("FILLED", "FILLED") for l in mv.pending_lines(ver)]
            (d / "values_fived16.tex").write_text("\n".join(lines[:end] + pl + lines[end:]))
            for f in d.glob("main_paper.*"):
                if f.suffix != ".tex":
                    f.unlink()
            r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main_paper.tex"],
                               cwd=d, capture_output=True, text=True, errors="replace")
            if r.returncode:
                fails.append(f"fill test {i}: main_paper build failed; see {d}/main_paper.log")
                continue
            txt = subprocess.run(["pdftotext", "main_paper.pdf", "-"], cwd=d, capture_output=True, text=True, errors="replace").stdout
            log = (d / "main_paper.log").read_text(errors="replace")
            for bad, what in (("[PENDING", "a pending marker"), ("??", "an unresolved reference")):
                if bad in txt:
                    fails.append(f"fill test {i}: the text prints {what}")
            if re.search(r"undefined (references|citations)|Reference .* undefined", log):
                fails.append(f"fill test {i}: undefined references")
            print(f"fill test {i}: built, {len(txt.split())} words")
    return fails


def self_test():
    pend = {"k": ("g", ("a", "b")), "e": ("g", ("x", "y"))}
    EMPTY["e"] = {"y"}
    good = {"f": r"\fvgroup{g}{\fvcase{k}{a}{one}\fvcase{k}{b}{two} \fvcase{e}{x}{three}}"}
    cases = [
        ("a missing variant", {"f": r"\fvgroup{g}{\fvcase{k}{a}{one}}"}, check_variants),
        ("an undeclared variant", {"f": r"\fvgroup{g}{\fvcase{k}{a}{1}\fvcase{k}{b}{2}\fvcase{k}{c}{3}}"}, check_variants),
        ("a case outside its group", {"f": r"\fvcase{k}{a}{one}\fvcase{k}{b}{two}"}, check_variants),
    ]
    ok = not check_variants(good, pend, {"g"}) and not check_no_number(good)
    for name, t, fn in cases:
        if not fn(t, pend, {"g"}):
            print("self-test: NOT CAUGHT", name)
            ok = False
    if not check_no_number({"f": r"\fvgroup{g}{\fvcase{k}{a}{in 3 cells}}"}):
        print("self-test: NOT CAUGHT a number in a variant"); ok = False
    if check_no_number({"f": r"\fvgroup{g}{\fvcase{k}{a}{in cells \fvval{k-cells} (section~\ref{s:1})}}"}):
        print("self-test: a key or a reference was taken for a number"); ok = False
    if not check_keys({"f": r"\fvval{nope}"}, r"\@namedef{fv@yes}{1}"):
        print("self-test: NOT CAUGHT an undefined key"); ok = False
    if not check_numerals({"f": "a 7.77 here"}, {"f": "a 7.7 here"}):
        print("self-test: NOT CAUGHT a new numeral"); ok = False
    if not check_once_gone({"f": "the stabilised variant " + " ".join(ONCE)}):
        print("self-test: NOT CAUGHT a GONE phrase"); ok = False
    if not check_once_gone({"f": " ".join(ONCE[1:])}):
        print("self-test: NOT CAUGHT a missing ONCE sentence"); ok = False
    del EMPTY["e"]
    print("self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    wt = Path(argv[0]).resolve()
    base = argv[argv.index("--base") + 1] if "--base" in argv else BASE
    fails = run(wt, base)
    if "--fill-test" in argv:
        fails += fill_test(wt)
    for f in fails:
        print("FAIL", f)
    print(f"CHECK-ROUND methods-short :: {'PASS' if not fails else 'FAIL'} ({len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
