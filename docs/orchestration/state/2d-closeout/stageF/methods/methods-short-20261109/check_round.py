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
  6. SEC4 TESTS. test_check_sec4_receipts.py passes (the director, 2026-11-09; the hook does not run it).
  7. FILL TEST (--fill-test, slow). The paper is built once per class index: every pending key set to its i-th
     class (cyclically), and the like-for-like group to the i-th of make_values_fived16.ll5d_fill_cases(), which
     are consistent with its derived keys and between them reach every class; so every variant is typeset at least
     once. Each build must succeed with no "[PENDING", no "??", no undefined reference, and no printed class name
     (check 8).
  8. NO CLASS NAME IN PRINT (printed_class_names; run by the fill test and by preread-outcomes/build_cases.py on
     every build). A filled build prints no raw class name (any class with a hyphen, in either spelling, or "na"),
     and never "joseph" outside the author line, the email and the repository URL (the director, 2026-11-09, item 8).
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
         **{f"ll5d-{t}-{r}": {"na"} for t in ("g18", "ar23") for r in ("minus2", "all")},
         **{f"ll5d-{t}-{r}-{x}": {"none", "na"} for t in ("g18", "ar23") for r in ("minus2", "all")
            for x in ("weak", "over", "clip")},
         "ll5d-route": {"direct", "na"},
         "ll5d-abs-minus2": {"na"}, "ll5d-abs-all": {"na"}, "ll5d-abs-close": {"na"},
         **{f"ll5d-{x}": {"none", "na"} for x in ("anypass", "anyunder", "cellflags", "anyweak", "anyover")}}
# numerals the paper prints that the base does not, each with its source (ledger rows)
NEW_NUMERALS = {"285": "L-12b: re2 partc-r2 receipts/figs/tension_report.txt:55, 1.391 x 205 = 285.2 (in [285.05, 285.26])",
                "136": "L-12b: the note's sec_results.tex:128 (chi2 = 136 on the 73 best-determined directions)",
                "0.05": "L-27: FD-PRR-DECLARATION.md:281-286, the bar delta_F = max(0.05, 9.03 s_F)",
                "9.03": "L-27: FD-PRR-DECLARATION.md:281-286 (the two-sided Student-t quantile on 4 degrees of freedom at 0.01/12)",
                "0.01": "L-27: FD-PRR-DECLARATION.md:282-284 (the familywise rate 0.01 over the 12 primary readings)",
                "0.10": "P-9: LL5D-DECLARATION.md:486, the test's resolution, about 0.10 in coverage per cell",
                "0.08": "P-9: LL5D-DECLARATION.md:486, the test's resolution, about 0.08 jointly (0.10 per cell)",
                "0.025": "P-9: LL5D-DECLARATION.md:471-472, :482, the size per (truth, reading): 0.025 over the cells, 0.025 joint",
                "99.7": "L-28: r5:176's bar 39.04 at the null's 0.997 quantile, printed as the 99.7th percentile (round 6, the editor's B8)"}
ONCE = [
    "and their cross-covariance is not available, so no difference between them can be given a calibrated significance.",
    "The five-observable estimator is the baseline this study characterizes",
    "It is a tested mitigation of the instability, not a replacement.",
    "These results bound what the study shows.",
    "That test is a next step.",
    "The grading rules and their timing are stated with the individual tests; comparisons without a grading rule are descriptive.",
]
GONE = [r"stabili[sz]ed variant", r"validat\w* the (full|five-observable) distribution", r"detector[- ]inadequa",
        r"locali[sz]ed in", r"\bE_?\{?96", r"\bFD-PRR\b", r"\bLL5D\b", r"\bV-HALF\b", r"\bV-ATLAS\b", r"\bV-PRIOR\b",
        r"\bCOV2D\b", r"\bRS1\b", r"\bENS1\b", r"\bFD-STAB\b", r"BIAS_WORSE", r"Stage~?0c", r"\bPR-[123]",
        r"\bdeclared\b", r"joint-test estimator", r"\\chi\^\{2\}/205", r"tracks the same bias", r"natural next step"]


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


LABELS = GONE[4:]   # the internal labels (not the claim phrases): checked in the printed pending-group names too


def check_printed_names(values_tex):
    """Round 6 (the editor's C4): the pending groups' names print in the paper, so the internal labels must not be in them."""
    fails = []
    for g, name in re.findall(r"\\@namedef\{fvgd@([^}]+)\}\{([^}]*)\}", values_tex):
        for pat in LABELS:
            if re.search(pat, name):
                fails.append(f"values_fived16.tex: the pending group {g} prints the internal label {pat!r}: {name!r}")
    return fails


def check_dates(texts):
    """Round 6 (the director's item 2): no ISO date in the printed paper or Supplement (comments stripped)."""
    fails = []
    for f, t in texts.items():
        for m in re.finditer(r"\b(19|20)\d\d-\d\d-\d\d\b", strip_comments(t)):
            fails.append(f"{f}: an internal date prints: {m.group(0)}")
    return fails


def check_sec4_tests(wt):
    """The director, 2026-11-09: test_check_sec4_receipts.py's cases bind printed sentences of the paper and the
    Supplement, and the pre-commit hook does not run them, so two went stale unnoticed. Run them here."""
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_check_sec4_receipts.py"], cwd=wt / NOTE,
                       capture_output=True, text=True, errors="replace")
    return [] if r.returncode == 0 else [f"test_check_sec4_receipts.py fails: {r.stdout.strip().splitlines()[-1]}"]


def run(wt, base):
    mv = load_mv(wt)
    cur = {f: (wt / NOTE / f).read_text() for f in FILES}
    old = {f: subprocess.run(["git", "-C", str(wt), "show", f"{base}:{NOTE}/{f}"], capture_output=True, text=True,
                             check=True).stdout for f in FILES}
    supp = (wt / NOTE / "supplemental_body.tex").read_text()
    fails = (check_variants(cur, mv.PENDING, mv.PENDING_GROUPS) + check_no_number(cur)
             + check_keys({**cur, "supplemental_body.tex": supp}, (wt / NOTE / "values_fived16.tex").read_text())
             + check_numerals(cur, old) + check_once_gone(cur)
             + check_printed_names((wt / NOTE / "values_fived16.tex").read_text())
             + check_dates({**cur, "supplemental_body.tex": supp})
             + check_sec4_tests(wt))
    return fails


IDENT = ("Joseph Bailey", "josephrb@stanford.edu", "josephbaileyy")   # the author line, the email, the repository URL


def printed_class_names(txt, mv):
    """Check 8 on one build's pdftotext: the raw class names and 'joseph' that print, if any."""
    t = re.sub(r"-\n(?=[a-z])", "-", txt)                 # keep a compound's hyphen at a line break
    t = re.sub(r"\s+", " ", t)
    for s in IDENT:
        t = t.replace(s, " ")
    words = {w for k in getattr(mv, "WORDS", {}) for w in mv.WORDS[k].values()}
    names = {c for _, cls in mv.PENDING.values() if cls for c in cls if "-" in c}
    pats = sorted({re.escape(s) for c in names for s in (c, c.replace("-", " ")) if s not in words})
    found = [m.group(0) for p in pats for m in re.finditer(r"(?<![\w-])" + p + r"(?![\w-])", t)]
    found += re.findall(r"(?<![\w-])na(?![\w-])", t)
    found += re.findall(r"(?i)joseph", t)
    return sorted(set(found))


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
        ll5d, prr = mv.ll5d_fill_cases(), mv.prr_fill_cases()
        for i in range(max(n, len(ll5d), len(prr))):
            ver = {}
            for k, (g, cls) in mv.PENDING.items():
                ver[k] = cls[i % len(cls)] if cls else f"X{k.split('-')[-1]}"
            ver.update(ll5d[i % len(ll5d)])
            ver.update(prr[i % len(prr)])
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
            bad = printed_class_names(txt, mv)
            if bad:
                fails.append(f"fill test {i}: a class name prints: {bad}")
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
    if not check_printed_names(r"\@namedef{fvgd@x}{LL5D, the test}"):
        print("self-test: NOT CAUGHT an internal label in a printed group name"); ok = False
    if not check_dates({"f": "until 2026-10-11; "}) or check_dates({"f": "% 2026-10-11 in a comment"}):
        print("self-test: the date check is wrong"); ok = False
    if not check_once_gone({"f": " ".join(ONCE[1:])}):
        print("self-test: NOT CAUGHT a missing ONCE sentence"); ok = False
    class _MV:
        PENDING = {"k": ("g", ("under-cells", "no-effect", "covers"))}
        WORDS = {"k": {"no-effect": "no effect"}}
    if printed_class_names("the test covers; the factor has no effect. Joseph Bailey, josephrb@stanford.edu", _MV):
        print("self-test: check 8 flags a printed word or the author line"); ok = False
    for planted in ("it under cells here", "it under-\ncells here", "the status to joseph", "na, na", "under-cells"):
        if not printed_class_names(planted, _MV):
            print("self-test: NOT CAUGHT a printed class name:", repr(planted)); ok = False
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
