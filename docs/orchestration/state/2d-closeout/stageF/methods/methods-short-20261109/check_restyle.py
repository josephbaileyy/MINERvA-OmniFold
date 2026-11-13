#!/usr/bin/env python3
r"""Check a restyled paper_body.tex / main_paper.tex against the base, so that a wording-only pass moves no claim.

usage: check_restyle.py <base-dir> <new-dir>     (each holds paper_body.tex and main_paper.tex, and optionally
                                                  supplemental_body.tex; exit 1 on any failure)

Refuses, per file, any change to (comments stripped):
  - the multiset of \\fvval keys, of (\\fvcase key, class) pairs, and of \\fvgroup / \\fvgroupalt groups;
  - the multiset of \\cite keys, and the sets of \\label and \\ref targets (any \\ref-like macro);
  - every numeral the file prints (check_round.numerals): a numeral may not appear or disappear;
  - every other macro name used (a dropped or added \\pubhold, \\SI, \\ssec... is reported);
  - the protected text: Data availability (from its \\section* to the next \\section or \\end), and every make_values
    LISTED_CLAIMS anchor and check_round ONCE sentence. The B0 sentences and RS1's paragraph were protected until
    Joseph approved their controlled rewrite (DECISION-20261112-joseph-consult-d1-d7.md D3 and its addendum, 2026-11-12),
    which removes both spans.
It reports, without failing, the sentences that changed, for the claim-by-claim read.

With supplemental_body.tex in both directories (the director, 2026-11-09, for the Supplement's restyle) it also refuses:
  - the same inventories for the Supplement: \fvval, \fvcase, \fvgroup, \cite, \label, \ref, numerals, macros;
  - any break of the paper's pointers into it: check_supp_pointers.check(paper, supplement) must report no error, with
    as many pointers as the base;
  - any record quote (``...'') of the base Supplement that is missing from the new one;
  - any change to a result-package (#981) quote: each row of supp-quotes.tsv (limitation-resolver's list), counted
    as #981 counts it (whitespace collapsed, ** and ` removed, an exact substring of the raw file).
It reports every paragraph whose text changed under a "(verbatim, ...)" or "verbatim" provenance comment. That comment
must then be updated to say the paragraph was restyled.
"""
import importlib.util
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cr = load(HERE / "check_round.py", "check_round")


def strip(t):
    return cr.strip_comments(t)


def inventory(t):
    s = strip(t)
    return {
        "fvval": Counter(re.findall(r"\\fvval\{([^}]+)\}", s)),
        "fvcase": Counter((k, c) for _, _, (k, c, _) in cr.macro_calls(s, "fvcase", 3)),
        "fvgroup": Counter(a[0] for _, _, a in cr.macro_calls(s, "fvgroup", 2)),
        "fvgroupalt": Counter(a[0] for _, _, a in cr.macro_calls(s, "fvgroupalt", 3)),
        "cite": Counter(k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", s) for k in c.split(",")),
        "label": Counter(re.findall(r"\\label\{([^}]+)\}", s)),
        "ref": Counter(re.findall(r"\\(?:ref\*?|eqref|nsec|napp|ssecc?|stab)\{([^}]+)\}", s)),
        "numerals": Counter(cr.numerals(t)),
        "macros": Counter(re.findall(r"\\([A-Za-z]+)", s)),
    }


def protected(base_main, base_body):
    """The protected spans, taken from the base so that the new files must contain them verbatim."""
    spans = []
    m = re.search(r"\\section\*\{Data availability\}.*?(?=\\section|\\end\{document\}|\\bibliography)", base_main, re.S)
    if m:
        spans.append(("Data availability", strip(m.group(0)).strip()))
    # B0 and RS1 were protected here until DECISION-20261112-joseph-consult-d1-d7.md D3 and its addendum (2026-11-12)
    return spans


def anchors():
    mv = load(ROOT / "docs/analysis-note/make_values_fived16.py", "mv")
    out = []
    for c in getattr(mv, "LISTED_CLAIMS", []):
        a = c[1] if isinstance(c, (tuple, list)) and c[0] in ("paper_body.tex", "main_paper.tex") else None  # (file, anchor, kind)
        if isinstance(a, str):
            out.append(a)
    return out


def sentences(t):
    s = re.sub(r"\s+", " ", strip(t))
    return set(x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", s) if len(x.strip()) > 20)


def supp_checks(base, new, paper_new):
    """The Supplement's extra refusals and reports (see the module docstring)."""
    fails, report = [], []
    b, n = (base / "supplemental_body.tex").read_text(), (new / "supplemental_body.tex").read_text()
    ib, inn = inventory(b), inventory(n)
    for k in ib:
        if ib[k] != inn[k]:
            fails.append(f"supplemental_body.tex: {k} changed; lost {dict(ib[k] - inn[k])}; added {dict(inn[k] - ib[k])}")
    def pointers(d):          # check_supp_pointers runs on import, from its directory: call it there
        r = subprocess.run([sys.executable, "-I", str(ROOT / "docs/analysis-note/check_supp_pointers.py")], cwd=d,
                           capture_output=True, text=True)
        m = re.search(r"(\d+) Supplement pointers checked, (\d+) failures", r.stdout)
        return (int(m.group(1)), int(m.group(2)), r.stdout) if m else (None, None, r.stdout + r.stderr)
    nb, fb, _ = pointers(base)
    nn, fn, out = pointers(new)
    if fn != 0 or nn is None:
        fails.append(f"a paper pointer into the Supplement breaks: {out.strip()[-300:]}")
    if nn != nb:
        fails.append(f"paper pointers into the Supplement: {nb} in the base, {nn} now")
    sb, sn = strip(b), strip(n)
    for q in sorted(set(re.findall(r"``(.+?)''", sb, re.S))):
        if q not in sn:
            fails.append(f"a record quote is gone from the Supplement: ``{q[:70]}''")
    ql = HERE / "supp-quotes.tsv"     # limitation-resolver's list of #981's checks: id, count=N, line, label, string
    if ql.exists():
        rows = [l.split("\t") for l in ql.read_text().split("\n") if l.strip() and not l.startswith("#")]
        norm = lambda s: re.sub(r"\s+", " ", s).replace("**", "").replace("`", "")  # noqa: E731  (#981's matching)
        fb, fnw = norm(b), norm(n)                     # #981 reads the raw file
        for r in rows:
            qid, want, q = r[0], int(r[1].split("=")[1]), r[-1]
            label = q.startswith("\\label{")
            cb, cn = fb.count(q), fnw.count(q)
            if cb != want:
                fails.append(f"{qid}: the base counts {cb}, but #981's list says {want}: {q[:60]!r}")
            if (label and cn < 1) or (not label and cn != want):
                fails.append(f"{qid}: #981's quote now counts {cn} (needs {'>= 1' if label else want}): {q[:70]!r}")
        report.append(f"supplemental_body.tex: {len(rows)} #981 quotes checked (supp-quotes.tsv)")
    else:
        report.append("supplemental_body.tex: no supp-quotes.tsv, so #981's quotes are not checked")
    bl, nl = b.split("\n"), n.split("\n")
    if len(bl) == len(nl):
        prov = [i + 1 for i, (x, y) in enumerate(zip(bl, nl)) if x != y and not x.lstrip().startswith("%")
                and i > 0 and "verbatim" in nl[i - 1] and "restyled" not in nl[i - 1] and nl[i - 1].lstrip().startswith("%")]
        report.append(f"supplemental_body.tex: {len(prov)} restyled paragraphs still sit under a 'verbatim' provenance comment"
                      f" (lines {prov[:12]}{'...' if len(prov) > 12 else ''}){'; update those comments' if prov else ''}")
    else:
        report.append("supplemental_body.tex: the line count changed, so the provenance comments must be read by hand")
    sb2, sn2 = sentences(b), sentences(n)
    report.append(f"supplemental_body.tex: {len(sb2 - sn2)} sentences changed or removed, {len(sn2 - sb2)} new")
    return fails, report


def main(argv):
    base, new = Path(argv[1]), Path(argv[2])
    fails, report = [], []
    for f in ("paper_body.tex", "main_paper.tex"):
        b, n = (base / f).read_text(), (new / f).read_text()
        ib, inn = inventory(b), inventory(n)
        for k in ib:
            if ib[k] != inn[k]:
                lost, added = ib[k] - inn[k], inn[k] - ib[k]
                fails.append(f"{f}: {k} changed; lost {dict(lost)}; added {dict(added)}")
        sb, sn = sentences(b), sentences(n)
        report.append(f"{f}: {len(sb - sn)} sentences changed or removed, {len(sn - sb)} new")
    bm, bb = (base / "main_paper.tex").read_text(), (base / "paper_body.tex").read_text()
    nm, nb = strip((new / "main_paper.tex").read_text()), strip((new / "paper_body.tex").read_text())
    for name, span in protected(bm, bb):
        if span not in nm and span not in nb:
            fails.append(f"protected text changed: {name}")
    for a in anchors():
        if a not in nm and a not in nb:
            fails.append(f"a LISTED_CLAIMS anchor is gone: {a!r}")
    for s in cr.ONCE:
        if (nm + nb).count(s) != 1:
            report.append(f"ONCE sentence not printed exactly once (update check_round.ONCE if the change is approved): {s[:70]!r}")
    if (base / "supplemental_body.tex").exists() and (new / "supplemental_body.tex").exists():
        f2, r2 = supp_checks(base, new, (new / "paper_body.tex").read_text())
        fails += f2
        report += r2
    for r in report:
        print("REPORT", r)
    for x in fails:
        print("FAIL", x)
    print("CHECK-RESTYLE ::", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
