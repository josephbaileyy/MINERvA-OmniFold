"""LaTeX-to-printed-text helpers shared by the final-draft generator and the d2 tools (one implementation).

init(worktree) binds them to a tree: values from values_fived16.tex, labels from the builds' .aux files, citation
numbers from main_paper.aux."""
import re
from pathlib import Path

A = VALS = LAB = BIB = None


def init(W):
    global A, VALS, LAB, BIB
    A = Path(W) / "docs/analysis-note"
    VALS = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{([^}]*)\}", (A / "values_fived16.tex").read_text()))
    LAB = {"paper": aux_labels("main_paper.aux"), "note": aux_labels("main_note.aux")}
    BIB = dict(re.findall(r"\\bibcite\{([^}]*)\}\{\{(\d+)\}", (A / "main_paper.aux").read_text(encoding="latin-1")))


def aux_labels(name):
    return {k: v.replace("\\,", " ") for k, v in
            re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", (A / name).read_text(encoding="latin-1"))}


def src(name):
    t = (A / name).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.splitlines()))


def plain(t, doc):
    """LaTeX to the plain text it prints. Fails on anything it does not know."""
    lab = LAB[doc]
    t = re.sub(r"\\fvval\{([^}]*)\}", lambda m: VALS[m.group(1)], t)
    t = re.sub(r"\\nsec\{([^}]*)\}", lambda m: f"Ref. [{BIB['AnalysisNote2026']}], Sec. {LAB['note'][m.group(1)]}", t)
    t = re.sub(r"\\napp\{([^}]*)\}", lambda m: f"Ref. [{BIB['AnalysisNote2026']}], App. {LAB['note'][m.group(1)]}", t)
    t = re.sub(r"\\ref\*\{N-([^}]*)\}", lambda m: LAB["note"][m.group(1)], t)
    t = re.sub(r"\\ref\{([^}]*)\}", lambda m: lab[m.group(1)], t)
    if doc == "paper":
        t = re.sub(r"\\cite\{([^}]*)\}", lambda m: "[" + ",".join(BIB[k.strip()] for k in m.group(1).split(",")) + "]", t)
    else:
        t = re.sub(r"~?\\cite\{([^}]*)\}", "", t)   # the note's citations are numbered by biblatex; not quoted here
    t = re.sub(r"\\pubhold\{([^}]*)\}", r"[HOLD: \1]", t)
    t = re.sub(r"\\SI\{([^}]*)\}\{\\percent\}", r"\1%", t)
    t = re.sub(r"\\SI\{([^}]*)\}\{([A-Za-z]+)\}", r"\1 \2", t)
    t = re.sub(r"\\(?:emph|texttt|mathrm|textrm)\{([^}]*)\}", r"\1", t)
    for a, b in [(r"\chi^{2}", "χ²"), (r"\chi^2", "χ²"), (r"\geq", "≥"), (r"\leq", "≤"), (r"\sigma", "σ"),
                 (r"\alpha", "α"), (r"\nu_{\mu}", "ν_μ"), (r"\Eavail", "E_avail"), (r"\pT", "p_T"), (r"\pPar", "p∥"),
                 (r"\times", "×"), (r"\,\%", "%"), (r"\%", "%"), (r"\_", "_"), (r"\S", "§"), (r"\,", " "), (r"\ ", " "),
                 ("~", " "), ("---", "—"), ("--", "–"), ("``", "“"), ("''", "”")]:
        t = t.replace(a, b)
    t = re.sub(r"\$([^$]*)\$", r"\1", t)
    t = re.sub(r"_\{([^}]*)\}", r"_\1", t).replace("{", "").replace("}", "")
    t = re.sub(r"q_3\b", "q3", t)
    left = re.findall(r"\\[A-Za-z]+", t)
    assert not left, f"unconverted LaTeX {left[:5]} in {t[:80]!r}"
    return re.sub(r"\s+", " ", t).strip()


def grab(name, start, end, doc):
    t = src(name)
    i = t.find(start)
    j = t.find(end, i + len(start) - 1)
    assert i >= 0 and j >= i, f"{name}: {start[:40]!r} .. {end!r} not found"
    assert t.count(start) == 1, f"{name}: {start[:40]!r} occurs {t.count(start)} times"
    return plain(t[i:j + len(end)], doc)


def line_of(name, needle):
    for n, l in enumerate((A / name).read_text(encoding="utf-8").splitlines(), 1):
        if needle in l:
            return n
    raise AssertionError(f"{needle[:40]!r} not in {name}")


def rec(path, pattern, flags=re.M):
    m = re.search(pattern, Path(path).read_text(encoding="utf-8"), flags)
    assert m, f"{path}: {pattern[:50]!r}"
    return m.group(1).strip()
