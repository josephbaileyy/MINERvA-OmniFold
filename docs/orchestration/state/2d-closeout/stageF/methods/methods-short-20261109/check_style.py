#!/usr/bin/env python3
r"""The prose-style targets of the paper, the abstract and the Supplement (the director, 2026-11-12, on Joseph's read
of 800579be: "many 'X, so Y' qualifications, many semicolons, and the paragraphs still feel long").

usage: check_style.py <worktree> [--base REV] [--part body|supplement|abstract ...] [--report]
       exit 1 if a judged metric is worse than the base by more than TOLERANCE
       check_style.py --self-test

--part limits which texts are judged; the others are still printed, marked "(not judged)". The default judges all
three. Each lane gates on its own part: the paper body and the abstract are director-helper-3's, and the Supplement
prose is journal-editor's (the director, 2026-11-12). The full run is the final gate.

The metric is the director's style_metrics script (2026-11-12), which measured ours against six reference papers'
arXiv sources (OmniFold PRL, TUnfold, Wiener-SVD JINST, Arratia et al., Huetsch et al., H1 PRL). Only the source is read,
with comments removed. Removed with it: table, figure, equation, align, eqnarray, thebibliography and tabular
environments, plus xltabular and longtable, the Supplement's page-breaking tables (added here: the director's script
predates them), and display maths. Paragraphs are split at blank lines. A paragraph counts if it has at least 25 words
and a full stop, and does not open with a sectioning or preamble command. Citations, references and \fvval keys count
as one word, and inline maths as one word. Sentences are split at [.?!] followed by whitespace and a capital, so
clauses joined by a semicolon count as one sentence.

What it judges (Joseph's refinement, via the director, 2026-11-12). The metrics are validation tests that the prose
is moving in the right direction. They are not targets: the target is comparison with relevant published papers, as
the style referee judges it. Each metric is printed for three texts:
- the working tree;
- the base, by default the branch's upstream tip @{u}, the previously pushed head (or --base REV);
- the references' median and range, from style-references.tsv. Each reference paper's metrics were measured by this
  metric on its arXiv source, and the table carries its arXiv id and title; the sources are not committed.

A metric FAILS only when it is worse than the base by more than TOLERANCE:
- 0.1 per 1000 words for the two rates;
- 2 words for the median paragraph;
- 1 percentage point for the share of paragraphs over 150 words;
- 0.2 words per sentence.
Otherwise it passes and prints where the text sits against the references. The metrics are semicolons and ", so" per
1000 words, the median paragraph, the share of paragraphs over 150 words, and words per sentence. paper_body.tex and
supplemental_body.tex are measured separately.

The abstract is one paragraph whose length check_round's ABSTRACT LENGTH gate (250 words) governs. So on every rendered
case (check_round.abstract_text over check_round.abstract_cases) only the rate and sentence metrics apply, as the
worst case. The base's abstract is rendered over the same cases.

A reference may be added only with its arXiv id and title checked through the arXiv API, and the addition recorded in
the table's header.

Variant alternatives (\fvcase) are measured as the source holds them, every alternative included, as the director
measured them. This counts a semicolon inside an alternative once for each alternative that contains it.
"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTE = "docs/analysis-note"
METRICS = ("semi", "so", "median", "gt150", "wps")
ABBREV = re.compile(r"\b(Secs?|Refs?|Figs?|Eqs?|Apps?|Tabs?|secs?|refs?|figs?|eqs?|apps?|tabs?|cf|al|vs|e\.g|i\.e)\.(?=\s)")


def references(path=HERE / "style-references.tsv"):
    """{arxiv id: {metric: value}} from the committed reference table."""
    rows = [l.split("\t") for l in path.read_text().split("\n") if l.strip() and not l.startswith("#")]
    head = rows[0]
    return {r[0]: {k: float(r[head.index(k)]) for k in METRICS} for r in rows[1:]}


def bounds(refs):
    """{metric: (median, maximum)} over the references; the maximum is the least tight reference."""
    out = {}
    for k in METRICS:
        v = sorted(r[k] for r in refs.values())
        n = len(v)
        out[k] = ((v[n // 2] + v[(n - 1) // 2]) / 2, v[-1])
    return out


TOLERANCE = {"semi": 0.1, "so": 0.1, "median": 2, "gt150": 1, "wps": 0.2}
ABSTRACT_TARGETS = ("semi", "so", "wps")
ENVS = r"table|figure|equation|align|eqnarray|thebibliography|tabular|xltabular|longtable"


def paragraphs(s):
    s = "\n".join(l for l in s.split("\n") if not l.lstrip().startswith("%"))
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\begin\{(" + ENVS + r")\*?\}.*?\\end\{\1\*?\}", "", s, flags=re.S)
    s = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]", "", s, flags=re.S)

    def clean(p):
        p = re.sub(r"\\(cite|ref|eqref|label|[a-z]*ref|fvval|nsec|ssec|sfig|stab|napp)\*?\{[^}]*\}", "X", p)
        p = re.sub(r"\$[^$]*\$", "X", p)
        p = re.sub(r"\\[a-zA-Z]+\*?(\[[^]]*\])?", "", p)
        return re.sub(r"[{}~]", " ", p)
    P = [clean(p.strip()) for p in re.split(r"\n\s*\n", s)
         if not re.match(r"\\(section|subsection|title|author|begin|end|maketitle|bibliography|documentclass|usepackage"
                         r"|newcommand|def)", p.strip())]
    return [p for p in P if len(p.split()) >= 25 and p.count(".") >= 1]


def metrics(P):
    L = sorted(len(p.split()) for p in P)
    w = sum(L)
    semi = sum(p.count(";") for p in P)
    so = sum(len(re.findall(r",\s+so\s", p)) for p in P)
    # an abbreviation's full stop before a reference is not a sentence end (journal-editor, 2026-11-12: "Sec.~\ref",
    # "Ref.~\cite", "ref.~\cite" and "Fig.~" became "Sec. X" after cleaning and counted as breaks); neutralised on both
    # sides of every comparison, since the base is measured by this same function
    sent = sum(len(re.findall(r"[.?!]\s+[A-Z]", ABBREV.sub(r"\1", p))) + 1 for p in P)
    return dict(words=w, paras=len(P), median=L[len(L) // 2], gt150=round(100 * sum(x > 150 for x in L) / len(L)),
                semi=round(1000 * semi / w, 1), so=round(1000 * so / w, 1), wps=round(w / sent, 1),
                n_semi=semi, n_so=so, long=[(x, p[:60]) for x, p in sorted(((len(p.split()), p) for p in P), reverse=True)
                                            if x > 150])


def judge(m, keys, targets):
    """Absolute limits (the self-test's)."""
    return [f"{k} {m[k]} > {targets[k]}" for k in keys if m[k] > targets[k]]


def worse(m, base, keys):
    """The metrics worse than the base by more than TOLERANCE."""
    return [f"{k} {m[k]}, worse than the base's {base[k]} by more than {TOLERANCE[k]}" for k in keys
            if m[k] > base[k] + TOLERANCE[k] + 1e-9]


def against(m, base, keys):
    b = bounds(references())
    lo = {k: min(r[k] for r in references().values()) for k in keys}
    return "\n".join(f"    {k:7s} now {m[k]:>6g}  base {base[k]:>6g}  references median {b[k][0]:g}, range {lo[k]:g}-{b[k][1]:g}"
                      for k in keys)


def at_rev(wt, rev, f):
    import subprocess
    return subprocess.run(["git", "-C", str(wt), "show", f"{rev}:{NOTE}/{f}"], capture_output=True, text=True,
                          check=True).stdout


def abstract_texts(wt, rev=None):
    spec = importlib.util.spec_from_file_location("check_round", HERE / "check_round.py")
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    mv = cr.load_mv(wt)
    main = (wt / NOTE / "main_paper.tex").read_text() if rev is None else at_rev(wt, rev, "main_paper.tex")
    vals = (wt / NOTE / "values_fived16.tex").read_text() if rev is None else at_rev(wt, rev, "values_fived16.tex")
    return [cr.abstract_text(main, vals, c) for c in cr.abstract_cases(mv)]


def abstract_metrics(texts):
    worst = {}
    for t in texts:
        m = metrics([t])
        for k in ABSTRACT_TARGETS:
            if k not in worst or m[k] > worst[k][0]:
                worst[k] = (m[k], t)
    return {k: v[0] for k, v in worst.items()}, worst


def run(wt, report, parts=("body", "supplement", "abstract"), base="@{u}"):
    import subprocess
    rev = subprocess.run(["git", "-C", str(wt), "rev-parse", "--short", base], capture_output=True, text=True,
                         check=True).stdout.strip()
    print(f"CHECK-STYLE base {base} = {rev}; references: {', '.join(references())}")
    fails = []
    for part, name, f in (("body", "paper body", "paper_body.tex"), ("supplement", "Supplement", "supplemental_body.tex")):
        m = metrics(paragraphs((wt / NOTE / f).read_text()))
        b = metrics(paragraphs(at_rev(wt, rev, f)))
        if part in parts:
            fails += [f"{name}: {x}" for x in worse(m, b, METRICS)]
        print(f"STYLE {name}{'' if part in parts else ' (not judged)'}: {m['words']} words, {m['paras']} paragraphs "
              f"(semicolons {m['n_semi']}, ', so' {m['n_so']}; base {b['n_semi']}, {b['n_so']})\n{against(m, b, METRICS)}")
        if report:
            for x, p in m["long"]:
                print(f"    {x:4d}  {p}")
    texts = abstract_texts(wt)
    am, _ = abstract_metrics(texts)
    same = all(at_rev(wt, rev, f) == (wt / NOTE / f).read_text() for f in ("main_paper.tex", "values_fived16.tex"))
    ab = am if same else abstract_metrics(abstract_texts(wt, rev))[0]      # the base renders the same text: reuse it
    if "abstract" in parts:
        fails += [f"abstract (worst of {len(texts)} rendered cases): {x}" for x in worse(am, ab, ABSTRACT_TARGETS)]
    print(f"STYLE abstract{'' if 'abstract' in parts else ' (not judged)'}, worst of {len(texts)} rendered cases\n"
          f"{against(am, ab, ABSTRACT_TARGETS)}")
    for x in fails:
        print("FAIL", x)
    print("CHECK-STYLE ::", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


def self_test():
    ok = True
    good = ("This sentence has exactly ten words in it for tests. " * 3).strip()
    good_p = "\n\n".join([good] * 5)
    m = metrics(paragraphs(good_p))
    T = {"semi": 3.0, "so": 0.7, "median": 110, "gt150": 25, "wps": 22.0}
    refs = references()
    if len(refs) < 6 or bounds(refs)["semi"][1] != max(r["semi"] for r in refs.values()):
        print("self-test: the reference table is short or its maximum is misread"); ok = False
    if judge(m, METRICS, T) or m["paras"] != 5 or m["median"] != 30 or m["wps"] != 10.0:
        print("self-test: a clean text fails or is mismeasured:", m); ok = False
    planted = {
        "semi": good_p.replace("for tests. This", "for tests; this"),
        "so": good_p.replace("for tests. This", "for tests, so this"),
        "median": "\n\n".join([(good + " ") * 4] * 5),
        "gt150": "\n\n".join([(good + " ") * 6] + [good] * 2),
        "wps": "\n\n".join([good.replace(". This", " and this")] * 5),
    }
    for k, t in planted.items():
        if k not in [x.split()[0] for x in judge(metrics(paragraphs(t)), METRICS, T)]:
            print(f"self-test: NOT CAUGHT {k}:", metrics(paragraphs(t))); ok = False
    hidden = good_p + "\n\n% a; comment; with; semicolons, so what\n\\begin{xltabular}{x}{y}\na; b; c; d, so e. F; g.\n\\end{xltabular}\n"
    if judge(metrics(paragraphs(hidden)), METRICS, T):
        print("self-test: a comment or an xltabular is measured as prose"); ok = False
    ab = "\n\n".join(["See Sec.~\\ref{a} and ref.~\\cite{b} and Fig.~\\ref{c} and Eq.~(\\ref{d}) for these numbers, e.g. Here " + good] * 5)
    if metrics(paragraphs(ab))["wps"] != round(metrics(paragraphs(ab))["words"] / 15, 1):     # three sentences per paragraph
        print("self-test: an abbreviation before a reference counts as a sentence end:", metrics(paragraphs(ab))); ok = False
    am, _ = abstract_metrics([good, good.replace("for tests. This", "for tests; this", 1)])
    if am["semi"] == 0:
        print("self-test: NOT CAUGHT a semicolon in one abstract case of two"); ok = False
    base = metrics(paragraphs(good_p))
    if worse(base, base, METRICS) or not worse(metrics(paragraphs(planted["semi"])), base, ["semi"]):
        print("self-test: the base comparison misjudges"); ok = False
    if worse(metrics(paragraphs(good_p.replace("for tests. This", "for tests; this", 1))), metrics(paragraphs(planted["semi"])), ["semi"]):
        print("self-test: an improvement is judged worse"); ok = False
    print("CHECK-STYLE self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    a = sys.argv[1:]
    parts = [x for i, x in enumerate(a) if i and a[i - 1] == "--part"] or ["body", "supplement", "abstract"]
    bad = set(parts) - {"body", "supplement", "abstract"}
    if bad:
        sys.exit(f"check_style.py: unknown --part {sorted(bad)}")
    base = a[a.index("--base") + 1] if "--base" in a else "@{u}"
    sys.exit(run(Path(a[0]).resolve(), "--report" in a, tuple(parts), base))
