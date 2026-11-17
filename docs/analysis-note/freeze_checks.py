#!/usr/bin/env python3
r"""Thursday freeze checks for the analysis note (COMBINED-PLAN sec. 7; the director's brief of 2026-11-17).

Every check FAILS LOUDLY: it prints each offending item with its context, and the script exits 1 if any check fails.

usage:
  freeze_checks.py --base-pdf OLD.pdf --new-pdf NEW.pdf [--note-dir DIR] [--new-aux NEW.aux]
                   [--allowlist numbers-allowlist.tsv] [--limitations limitations-export.tsv]
                   [--spelling check_spelling_us.py] [--only 1,2,3,4,5] [--report OUT.md]
  freeze_checks.py --self-test

The defaults are main_note.pdf, main_note.aux and the .tsv files in --note-dir (default: this script's directory).
--spelling defaults to `git show 6f1e59ca4:<methods-short>/check_spelling_us.py`, the US-spelling gate (read-only).

1. NUMBERS DIFF. The multiset of numeric tokens in the pdftotext of OLD and NEW must be equal, apart from the rows of
   numbers-allowlist.tsv: token, delta (+n or -n, NEW minus OLD), owner, item, reason.
   - Skipped: the pages of the contents, the list of figures and the list of tables.
   - Not counted (renumbered references): page footers; numbers after Fig./Figure/Table/Sec./Section/§/App./Eq. and
     their lists and ranges; section-heading numbers; equation tags; citation brackets [n], [n, m] and [n-m].
   - Every unexplained token added or removed is printed with up to three contexts.
2. LIMITATION RETENTION. Every row of limitations-export.tsv (row_id, file, quote, reanchor_file, reanchor_quote,
   note) must have its quote, or its re-anchor quote, in the input closure of main_note.tex or in the NEW PDF text.
   A missing export fails the check.
3. LABELS.
   - No "??" in the NEW PDF text.
   - No hard-coded page reference ("p. 5", "pp. 3-4", "page 12") in the closure's printed source. \pageref uses are
     listed, not failed.
   - Every float label (fig:, tab:, or any \label inside a figure, table, longtable or xltabular) is referenced at
     least once by \ref, \cref, \Cref, \autoref, \pageref or \subref in the closure.
4. US SPELLING over every file of the posted note's input closure.
5. FONTS. pdffonts, page by page: a sans-serif font may appear only on the pages of the figures allowed one
   (SANS_ALLOWED; the plan: base Figs. 6, 17, 18, 33 = fig:eff, fig:eavail-marg, fig:calibration,
   fig:negweight-ratio). Monospace fonts are listed, not failed.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPELLING_REV = "6f1e59ca4"
SPELLING_PATH = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/check_spelling_us.py"
SANS_ALLOWED = ("fig:eff", "fig:eavail-marg", "fig:calibration", "fig:negweight-ratio")
SANS_RE = re.compile(r"(Sans(?!Mono)|Helvetica|Arial|CMSS|SFSS|LMSans|cmss|Gothic|Verdana)", re.I)
MONO_RE = re.compile(r"(Mono|Courier|CMTT|SFTT|LMMono)", re.I)
EXCLUDED_INPUTS = re.compile(r"^(preamble|values[a-z_]*)\.tex$")     # definitions only, no printed prose

# ---------------------------------------------------------------- shared helpers

def pdftext_pages(pdf: Path) -> list[str]:
    out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    pages = out.split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages


def strip_comments(t: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.split("\n"))


def closure(note_dir: Path, top: str = "main_note.tex") -> list[str]:
    seen, todo = [], [top]
    while todo:
        f = todo.pop(0)
        if f in seen or not (note_dir / f).exists():
            continue
        seen.append(f)
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", strip_comments((note_dir / f).read_text())):
            n = m.group(1)
            todo.append(n if n.endswith(".tex") else n + ".tex")
    return seen


def norm_ws(s: str) -> str:
    s = s.replace("\u00ad", "").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("ﬃ", "ffi")
    s = re.sub(r"-\n(?=[a-z])", "", s)                      # a line-end hyphen inside a word
    return re.sub(r"\s+", " ", s).strip()


def detex(s: str) -> str:
    s = re.sub(r"\\(emph|textit|textbf|mathrm|text|textsc|texttt)\{([^}]*)\}", r"\2", s)
    s = re.sub(r"\\(S|Eavail|pT|pPar)\b", lambda m: {"S": "§", "Eavail": "Eavail", "pT": "pT", "pPar": "p∥"}[m.group(1)], s)
    s = re.sub(r"\\[A-Za-z]+\*?(\[[^]]*\])?(\{[^}]*\})?", " ", s)
    s = s.replace("~", " ").replace("$", "").replace("{", "").replace("}", "").replace("--", "–")
    return norm_ws(s)

# ---------------------------------------------------------------- 1. numbers diff

LIST_HEAD = re.compile(r"^\s*(Contents|List of Figures|List of Tables)\s*$", re.M)
LEADER = re.compile(r"(\.\s){3,}\.?\s*\d+\s*$")
NUM = r"[A-Z]?\d+(?:\.\d+)*[a-z]?"
NUMLIST = NUM + r"(?:\s*(?:,|–|—|-|and|to|&)\s*" + NUM + r")*"
KW = (r"(?:Figures?|Figs?\.|Tables?|Tabs?\.|§§?|Sections?|Secs?\.|Appendix|Appendices|Apps?\.|Equations?|Eqs?\.|"
      r"Ref\.|Refs\.|pp?\.)")
REF_RE = re.compile(KW + r"\s*~?\s*\(?" + NUMLIST)
CITE_RE = re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]")
EQTAG_RE = re.compile(r"\(\s*[A-Z]?\d+(?:\.\d+)?\s*\)\s*$")
HEAD_RE = re.compile(r"^\s*(?:[A-J]|\d{1,2})(?:\.\d{1,2}){0,3}\s+[A-Z][a-z]")
TOKEN_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def skip_pages(pages: list[str]) -> set[int]:
    skip, in_list = set(), False
    for i, p in enumerate(pages):
        lines = [l for l in p.split("\n") if l.strip()]
        if LIST_HEAD.search(p):
            skip.add(i); in_list = True; continue
        if in_list and lines and any(LEADER.search(l) for l in lines):     # a list continues while its page has leaders
            skip.add(i); continue
        in_list = False
    return skip


def page_tokens(page: str, index: int | None = None) -> list[tuple[str, str]]:
    """(token, its line) for the countable numbers of one page (index: 0-based physical page)."""
    lines = page.split("\n")
    nonempty = [i for i, l in enumerate(lines) if l.strip()]
    # the page number: the last non-empty line if it is a bare number, and any bare-integer line whose value is within
    # 12 of the physical page (pdftotext can place the footer before a float's text)
    if nonempty and re.fullmatch(r"\s*(\d+|[ivxlc]+)\s*", lines[nonempty[-1]]):
        lines[nonempty[-1]] = ""
    if index is not None:
        cand = [i for i in nonempty if re.fullmatch(r"\s*\d+\s*", lines[i]) and abs(int(lines[i]) - (index + 1)) <= 12]
        if cand:
            best = min(cand, key=lambda i: abs(int(lines[i]) - (index + 1)))
            lines[best] = ""
    # section-heading numbers, line by line
    for i, l in enumerate(lines):
        if HEAD_RE.match(l) and len(l) < 100 and not l.rstrip().endswith("."):
            lines[i] = re.sub(r"^\s*(?:[A-J]|\d{1,2})(?:\.\d{1,2}){0,3}", " ", l)
    # references and citations may wrap across lines: substitute on the joined text, then split back
    SEP = "\u2029"
    s = SEP.join(lines)
    s = CITE_RE.sub(lambda m: re.sub(r"[^\u2029]", " ", m.group(0)), s)
    s = REF_RE.sub(lambda m: re.sub(r"[^\u2029]", " ", m.group(0)), s)
    out = []
    for orig, l in zip(page.split("\n") + [""] * 0, s.split(SEP)):
        if not l.strip():
            continue
        l = EQTAG_RE.sub(" ", l)
        for m in TOKEN_RE.finditer(l):
            out.append((m.group(0).replace(",", ""), orig.strip()))
    return out


def count_tokens(pages: list[str], other_lines: set[str] | None = None):
    """Token counts; contexts prefer lines absent from the other build (other_lines), which show the change."""
    skip = skip_pages(pages)
    c, ctx, fallback = collections.Counter(), collections.defaultdict(list), collections.defaultdict(list)
    for i, p in enumerate(pages):
        if i in skip:
            continue
        for tok, line in page_tokens(p, i):
            c[tok] += 1
            item = f"p.{i + 1}: {line[:150]}"
            if other_lines is not None and norm_ws(line) not in other_lines:
                if len(ctx[tok]) < 3:
                    ctx[tok].append(item)
            elif len(fallback[tok]) < 3:
                fallback[tok].append(item)
    for tok in fallback:
        if not ctx[tok]:
            ctx[tok] = ["(no changed line holds it; first occurrences:)"] + fallback[tok]
    return c, ctx, skip


def line_set(pages: list[str]) -> set[str]:
    skip = skip_pages(pages)
    return {norm_ws(l) for i, p in enumerate(pages) if i not in skip for l in p.split("\n") if l.strip()}


def read_allowlist(path: Path) -> tuple[collections.Counter, list[str]]:
    allow, bad = collections.Counter(), []
    if not path.exists():
        return allow, [f"allow-list {path} missing: every token change counts as unexplained"]
    for n, l in enumerate(path.read_text().split("\n"), 1):
        if not l.strip() or l.startswith("#") or l.startswith("token\t"):
            continue
        f = l.split("\t")
        try:
            allow[f[0].strip().replace(",", "")] += int(f[1].replace("−", "-").replace("+", ""))
        except (IndexError, ValueError):
            bad.append(f"allow-list line {n} unreadable: {l!r}")
    return allow, bad


def check_numbers(base_pdf: Path, new_pdf: Path, allowlist: Path):
    bp, np_ = pdftext_pages(base_pdf), pdftext_pages(new_pdf)
    bc, bctx, bskip = count_tokens(bp, line_set(np_))
    nc, nctx, nskip = count_tokens(np_, line_set(bp))
    allow, bad = read_allowlist(allowlist)
    lines = [f"pages skipped as contents/lists: base {sorted(x + 1 for x in bskip)}, new {sorted(x + 1 for x in nskip)}",
             f"tokens counted: base {sum(bc.values())}, new {sum(nc.values())}; allow-list rows net {sum(allow.values()):+d}"]
    lines += bad
    resid = {}
    for tok in set(bc) | set(nc) | set(allow):
        d = nc[tok] - bc[tok] - allow[tok]
        if d:
            resid[tok] = d
    for tok, d in sorted(resid.items(), key=lambda kv: (-abs(kv[1]), kv[0])):
        where = nctx[tok] if d > 0 else bctx[tok]
        lines.append(f"  {'ADDED' if d > 0 else 'REMOVED'} {tok!r} x{abs(d)} (new {nc[tok]}, base {bc[tok]}, allowed {allow[tok]:+d})")
        lines += [f"      {w}" for w in where]
    ok = not resid and not bad
    lines.append(f"NUMBERS-DIFF :: {'PASS' if ok else 'FAIL'} ({len(resid)} unexplained token value(s), "
                 f"{sum(abs(v) for v in resid.values())} occurrence(s))")
    return ok, lines

# ---------------------------------------------------------------- 2. limitation retention

def check_limitations(export: Path, note_dir: Path, new_pdf: Path):
    if not export.exists():
        return False, [f"LIMITATIONS :: FAIL (export {export} missing; limitation-resolver writes it)"]
    files = closure(note_dir)
    src_raw = {f: (note_dir / f).read_text() for f in files}
    src_all = norm_ws("\n".join(src_raw.values()))
    pdf_all = norm_ws("\n".join(pdftext_pages(new_pdf)))
    lines, fails, n = [], 0, 0
    for l in export.read_text().split("\n"):
        if not l.strip() or l.startswith("#") or l.startswith("row_id\t"):
            continue
        f = (l.split("\t") + [""] * 6)[:6]
        rid, _file, quote, rfile, rquote, _ = f
        n += 1

        def found(q):
            q = q.strip()
            return bool(q) and (norm_ws(q) in src_all or detex(q) in pdf_all)
        if found(quote):
            continue
        if found(rquote):
            continue
        fails += 1
        lines.append(f"  MISSING {rid} ({_file}): {quote[:150]!r}" + (f"; re-anchor {rfile}: {rquote[:100]!r} also missing" if rquote else ""))
    lines.append(f"LIMITATIONS :: {'PASS' if not fails and n else 'FAIL'} ({n} row(s), {fails} missing)")
    return (not fails and n > 0), lines

# ---------------------------------------------------------------- 3. labels

FLOAT_ENVS = r"figure\*?|table\*?|longtable|xltabular"
PAGE_HARD = re.compile(r"(?<![A-Za-z])(?:pp?\.|pages?)\s*~?\s*\d+")


def check_labels(note_dir: Path, new_pdf: Path):
    lines, ok = [], True
    text = "\n".join(pdftext_pages(new_pdf))
    qq = [m.start() for m in re.finditer(r"\?\?", text)]
    for p in qq[:20]:
        lines.append(f"  ?? at: {norm_ws(text[max(0, p - 80):p + 40])!r}")
    if qq:
        ok = False
    files = closure(note_dir)
    hard, pagerefs, labels, refs = [], [], {}, collections.Counter()
    for f in files:
        t = strip_comments((note_dir / f).read_text())
        for n, l in enumerate(t.split("\n"), 1):
            for m in PAGE_HARD.finditer(l):
                hard.append(f"  hard page ref {f}:{n}: {l[max(0, m.start() - 50):m.end() + 30].strip()!r}")
            if "\\pageref{" in l:
                pagerefs.append(f"{f}:{n}")
        for m in re.finditer(r"\\begin\{(" + FLOAT_ENVS + r")\}(.*?)\\end\{\1\}", t, re.S):
            for lab in re.findall(r"\\label\{([^}]+)\}", m.group(2)):
                labels.setdefault(lab, f)
        for lab in re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", t):
            labels.setdefault(lab, f)
        for m in re.finditer(r"\\(?:[cC]ref|autoref|ref\*?|pageref|subref|eqref)\{([^}]+)\}", t):
            for lab in m.group(1).split(","):
                refs[lab.strip()] += 1
    unref = sorted(l for l in labels if not refs[l])
    lines += hard
    lines += [f"  float never referenced: {l} ({labels[l]})" for l in unref]
    if pagerefs:
        lines.append(f"  (listed, not failed) \\pageref uses: {', '.join(pagerefs)}")
    ok = ok and not hard and not unref
    lines.append(f"LABELS :: {'PASS' if ok else 'FAIL'} ({len(qq)} '??', {len(hard)} hard page ref(s), "
                 f"{len(unref)} of {len(labels)} float label(s) never referenced)")
    return ok, lines

# ---------------------------------------------------------------- 4. US spelling

def load_spelling(path: str | None):
    if path:
        src = Path(path)
    else:
        repo = subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                              check=True).stdout.strip()
        code = subprocess.run(["git", "-C", repo, "show", f"{SPELLING_REV}:{SPELLING_PATH}"], capture_output=True,
                              text=True, check=True).stdout
        src = Path(tempfile.mkdtemp()) / "check_spelling_us.py"
        src.write_text(code)
    spec = importlib.util.spec_from_file_location("check_spelling_us", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_spelling(note_dir: Path, spelling: str | None):
    mod = load_spelling(spelling)
    lines, bad = [], 0
    files = [f for f in closure(note_dir) if not EXCLUDED_INPUTS.match(f)]
    for f in files:
        for n, w, us in mod.hits((note_dir / f).read_text()):
            lines.append(f"  {f}:{n}: {w} -> {us}")
            bad += 1
    lines.append(f"US-SPELLING :: {'PASS' if not bad else 'FAIL'} ({bad} British form(s) in {len(files)} closure file(s))")
    return not bad, lines

# ---------------------------------------------------------------- 5. fonts

def aux_pages(aux: Path) -> dict[str, int]:
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{(\d+)\}", aux.read_text(errors="replace")):
        out[m.group(1)] = int(m.group(3))
    return out


def page_fonts(pdf: Path, p: int) -> list[str]:
    out = subprocess.run(["pdffonts", "-f", str(p), "-l", str(p), str(pdf)], capture_output=True, text=True,
                         check=True).stdout.split("\n")[2:]
    return [l.split()[0] for l in out if l.strip()]


def check_fonts(new_pdf: Path, aux: Path):
    labs = aux_pages(aux)
    allowed = {labs[l] for l in SANS_ALLOWED if l in labs}
    missing = [l for l in SANS_ALLOWED if l not in labs]
    npages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(new_pdf)], capture_output=True,
                                                                 text=True, check=True).stdout).group(1))
    by_page = collections.defaultdict(list)
    for l, p in labs.items():
        if l.startswith("fig:"):
            by_page[p].append(l)
    lines, bad, mono = [], 0, []
    for p in range(1, npages + 1):
        fonts = page_fonts(new_pdf, p)
        sans = sorted({f.split("+")[-1] for f in fonts if SANS_RE.search(f)})
        ms = sorted({f.split("+")[-1] for f in fonts if MONO_RE.search(f)})
        if ms:
            mono.append(f"p.{p} {','.join(ms)}")
        if sans and p not in allowed:
            bad += 1
            lines.append(f"  sans on p.{p}: {', '.join(sans)}; figures there: {', '.join(by_page.get(p, [])) or 'none'}")
    if missing:
        lines.append(f"  allowed labels not in the aux: {missing}")
    lines.append(f"  (listed, not failed) monospace: {'; '.join(mono[:12])}{' ...' if len(mono) > 12 else ''}")
    lines.append(f"FONTS :: {'PASS' if not bad and not missing else 'FAIL'} ({bad} page(s) with a sans font outside "
                 f"the allowed figures' pages {sorted(allowed)})")
    return (not bad and not missing), lines

# ---------------------------------------------------------------- self-test

def self_test() -> bool:
    ok = True
    base = ["Contents\n1 Intro . . . . . . 3\n\f", "Text with 0.535 and 2.27 (Fig. 8; §6.4).\nSee [3, 14].\n4\n",
            "4.7 Which pieces exist\n300 replicas, Eq. (4.3)\n(12)\n5\n"]
    new = ["Contents\n1 Intro . . . . . . 3\n", "Text with 0.535 (Figs. 9–10; §§4–6).\nSee [5].\n4\n",
           "4.8 Which pieces exist\n300 replicas, Eq. (5.1)\n(13)\n6\n"]
    bc, _, bs = count_tokens(base)
    nc, _, ns = count_tokens(new)
    d = {t: nc[t] - bc[t] for t in set(bc) | set(nc) if nc[t] - bc[t]}
    if d != {"2.27": -1}:
        print("self-test: numbers diff should see only the removed 2.27, got", d); ok = False
    if bs != {0} or ns != {0}:
        print("self-test: the contents page is not skipped", bs, ns); ok = False
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        (t / "main_note.tex").write_text("\\input{a}\n")
        (t / "a.tex").write_text("See p.~5 and Fig.~\\ref{fig:x}.\n\\begin{figure}\\caption{c}\\label{fig:x}\\end{figure}\n"
                                 "\\begin{table}\\caption{d}\\label{tab:y}\\end{table}\n% p. 9 in a comment\n")
        files = closure(t)
        if files != ["main_note.tex", "a.tex"]:
            print("self-test: closure", files); ok = False
        hard = [m for l in strip_comments((t / "a.tex").read_text()).split("\n") for m in PAGE_HARD.finditer(l)]
        if len(hard) != 1:
            print("self-test: hard page refs", hard); ok = False
    if not SANS_RE.search("ABCDEF+DejaVuSans") or SANS_RE.search("ABCDEF+DejaVuSerif") or SANS_RE.search("X+DejaVuSansMono"):
        print("self-test: the sans pattern"); ok = False
    print("FREEZE-CHECKS SELF-TEST ::", "PASS" if ok else "FAIL")
    return ok

# ---------------------------------------------------------------- main

def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return 0 if self_test() else 1
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base-pdf", type=Path, required=True)
    ap.add_argument("--new-pdf", type=Path)
    ap.add_argument("--note-dir", type=Path, default=HERE)
    ap.add_argument("--new-aux", type=Path)
    ap.add_argument("--allowlist", type=Path)
    ap.add_argument("--limitations", type=Path)
    ap.add_argument("--spelling")
    ap.add_argument("--only", default="1,2,3,4,5")
    ap.add_argument("--report", type=Path)
    a = ap.parse_args()
    nd = a.note_dir
    new_pdf = a.new_pdf or nd / "main_note.pdf"
    aux = a.new_aux or nd / "main_note.aux"
    allow = a.allowlist or nd / "numbers-allowlist.tsv"
    lim = a.limitations or nd / "limitations-export.tsv"
    want = {int(x) for x in a.only.split(",")}
    runs = [(1, "Numbers diff", lambda: check_numbers(a.base_pdf, new_pdf, allow)),
            (2, "Limitation retention", lambda: check_limitations(lim, nd, new_pdf)),
            (3, "Labels", lambda: check_labels(nd, new_pdf)),
            (4, "US spelling", lambda: check_spelling(nd, a.spelling)),
            (5, "Fonts", lambda: check_fonts(new_pdf, aux))]
    report, fails = [f"# Freeze checks: {new_pdf} against {a.base_pdf}", ""], []
    for k, name, fn in runs:
        if k not in want:
            continue
        ok, lines = fn()
        print(f"=== {k}. {name} ===")
        print("\n".join(lines))
        report += [f"## {k}. {name}: {'PASS' if ok else 'FAIL'}", "", "```", *lines, "```", ""]
        if not ok:
            fails.append(name)
    verdict = "PASS" if not fails else f"FAIL ({', '.join(fails)})"
    print(f"FREEZE-CHECKS :: {verdict}")
    report.insert(1, f"**Verdict:** {verdict}")
    if a.report:
        a.report.write_text("\n".join(report) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
