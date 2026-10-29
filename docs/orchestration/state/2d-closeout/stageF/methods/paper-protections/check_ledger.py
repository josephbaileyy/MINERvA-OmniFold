#!/usr/bin/env python3
"""Check the ledger of the four paper protection edits (DECISION-20261028-joseph-protections-remade-and-r21.md items
1-4) against a worktree.

usage: check_ledger.py <worktree> [--base SHA] [--ledger PATH]
       check_ledger.py <worktree> --list [--base SHA]
       check_ledger.py <worktree> --self-test [--base SHA]

It reuses note-n4/check_ledger.py's sentence splitter, ledger reader and pin, imported, not copied. The rules for the
paper:
  1. every probe holds. The probes are P::text (paper_body.tex), MP::text (main_paper.tex) and N:file::text (a note
     file);
  2. every printed base sentence of paper_body.tex and main_paper.tex that no longer prints verbatim is named in some
     row's "before" column, by its id (PB<n> or MP<n>, as --list prints);
  3. every \\label of the two base files still exists;
  4. protected text is byte-identical to the base:
     - main_paper.tex from \\title to \\end{abstract} (the title and the abstracts' final wording);
     - every \\pubhold{...} hold of either file, and its definition line;
     - main_paper.tex from \\begin{acknowledgments} to \\end{document}, except the Data Availability statement
       (item 2: released), which may differ from its base only by DA_PAIRS, each pinned by sha256 in DA_PINS;
  5. "Interval coverage has not been validated." still prints in paper_body.tex (item 4);
  6. no numeral is typed by hand in a sentence these edits add: a number is a \\fvval or value macro.
Exit 1 on any failure."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "note-n4"))
from check_ledger import printed, sentences, rows, pin  # noqa: E402

FILES = {"paper_body.tex": "PB", "main_paper.tex": "MP"}
IDRX = re.compile(r"\b(PB|MP)\d+\b")
KEEP_SENTENCE = "Interval coverage has not been validated."
sys.path.insert(0, str(HERE))
import apply_p  # noqa: E402
# Item 2, the director's ruling (b) of 2026-10-28: apply_p.ITEM2's pair, pinned here, so that an edit of the pair in
# apply_p.py without a new pin allows nothing.
DA_PAIRS = [(eid, old, new) for eid, _f, old, new in apply_p.ITEM2]
DA_PINS = {"DA1": "7cbceaf999d9b799"}
NUMERAL = re.compile(r"(?<![\\\w{-])\d[\d,.]*")


def show(wt, rev, f):
    r = subprocess.run(["git", "-C", str(wt), "show", f"{rev}:docs/analysis-note/{f}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def span(text, a, b):
    i = text.find(a)
    j = text.find(b, i)
    return text[i:j + len(b)] if i >= 0 and j >= 0 else None


def da_span(text):
    return span(text, "\\section*{Data availability}", "\\bibliography{")


def changed(cur, old):
    out = []
    for f, pre in FILES.items():
        a = printed(cur[f])
        for i, s in enumerate(sentences(printed(old[f]))):
            if s not in a:
                out.append((f"{pre}{i}", f, s))
    return out


def added(cur, old):
    out = []
    for f in FILES:
        b = set(sentences(printed(old[f])))
        out += [(f, s) for s in sentences(printed(cur[f])) if s not in b]
    return out


def check(wt, cur, old, ledger_text, da_pairs=None, da_pins=None):
    da_pairs = DA_PAIRS if da_pairs is None else da_pairs
    da_pins = DA_PINS if da_pins is None else da_pins
    D = wt / "docs/analysis-note"
    fails, named, nrows, nprobes = [], set(), 0, 0
    txt = {f: printed(cur[f]) for f in FILES}
    for rid, fact, before, disp, after, probe in rows(ledger_text):
        nrows += 1
        named |= {m.group(0) for m in IDRX.finditer(before)}
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(P|MP)::(.*)$|N:([\w.]+)::(.*)$", p)
            if not m:
                fails.append(f"{rid}: malformed probe {p!r}"); continue
            nprobes += 1
            if m.group(1):
                f, lit = ("paper_body.tex" if m.group(1) == "P" else "main_paper.tex"), m.group(2)
                hay = txt[f]
            else:
                f, lit = m.group(3), m.group(4)
                hay = printed((D / f).read_text())
            if re.sub(r"\s+", " ", lit) not in hay:
                fails.append(f"{rid}: NOT FOUND in {f}: {lit[:90]!r}")
    for sid, f, s in changed(cur, old):
        if sid not in named:
            fails.append(f"UNCOVERED {sid} ({f}): {s[:100]!r}")
    for f in FILES:
        for lab in sorted(set(re.findall(r"\\label\{([^}]*)\}", old[f])) - set(re.findall(r"\\label\{([^}]*)\}", cur[f]))):
            fails.append(f"LABEL REMOVED {f}: {lab}")
    mp_o, mp_c = old["main_paper.tex"], cur["main_paper.tex"]
    if span(mp_o, "\\title", "\\end{abstract}") != span(mp_c, "\\title", "\\end{abstract}"):
        fails.append("PROTECTED: main_paper.tex \\title..\\end{abstract} differs from base")
    # The holds themselves, each \pubhold{...} macro with its text and its definition line: the Data Availability
    # sentence shares a source line with its hold, so a line comparison would charge the released text to the hold.
    hold = re.compile(r"\\pubhold\{[^{}]*\}|^.*\\newcommand\{\\pubhold\}.*$", re.M)
    for f in FILES:
        if hold.findall(old[f]) != hold.findall(cur[f]):
            fails.append(f"PROTECTED: the \\pubhold holds of {f} differ from base")
    tail_o, tail_c = span(mp_o, "\\begin{acknowledgments}", "\\end{document}"), span(mp_c, "\\begin{acknowledgments}", "\\end{document}")
    da_o = da_span(mp_o)
    exp = da_o
    for eid, o, n in da_pairs:
        if da_pins.get(eid) != pin(o, n) or exp.count(o) != 1:
            exp = None
            break
        exp = exp.replace(o, n)
    if exp is None:
        fails.append("RELEASED Data Availability: a pair is unpinned or does not match the base once")
    elif tail_o.replace(da_o, exp) != tail_c:
        fails.append("PROTECTED: main_paper.tex acknowledgments..end differs from base by more than the pinned DA pairs")
    if KEEP_SENTENCE not in txt["paper_body.tex"]:
        fails.append(f"KEEP: {KEEP_SENTENCE!r} no longer prints in paper_body.tex")
    for f, s in added(cur, old):
        bare = [x for x in NUMERAL.findall(re.sub(r"\\(fvval|ref|nsec|napp|label|cite)\{[^}]*\}", "", s)) if x.strip(".,")]
        if bare:
            fails.append(f"NUMERAL typed by hand in an added sentence of {f}: {bare} in {s[:80]!r}")
    return fails, nrows, nprobes, len(changed(cur, old))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="b554de56")
    ap.add_argument("--ledger", default=str(HERE / "ledger.md"))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve()
    cur = {f: (wt / "docs/analysis-note" / f).read_text() for f in FILES}
    old = {f: show(wt, a.base, f) for f in FILES}
    if a.list:
        for sid, f, s in changed(cur, old):
            print(f"{sid}\t{f}\t{s}")
        return 0
    lt = Path(a.ledger).read_text() if Path(a.ledger).exists() else ""
    if a.self_test:
        base_fails, *_ = check(wt, cur, old, lt)
        mp = cur["main_paper.tex"]
        abs_s = span(mp, "\\begin{abstract}", "\\end{abstract}")
        da = da_span(mp)
        hold = next(l for l in mp.splitlines() if "\\pubhold" in l and "newcommand" not in l)
        word = next(w for w in re.findall(r"[a-z]{6,}", da) if da.count(w) == 1)   # a word the DA span holds once
        planted = [
            ("missing probe", cur, lt + "\n| T1 | t | — | KEEP | — | `P::@@NO SUCH TEXT@@` |\n", {}),
            ("abstract edit", {**cur, "main_paper.tex": mp.replace(abs_s, abs_s.replace(" the ", " a ", 1))}, lt, {}),
            ("\\pubhold line edit", {**cur, "main_paper.tex": mp.replace(hold, hold.replace("\\pubhold{", "\\pubhold{X ", 1))}, lt, {}),
            ("undeclared DA edit", {**cur, "main_paper.tex": mp.replace(da, da.replace(word, word + "s", 1))}, lt, {}),
            ("declared but unpinned DA pair", {**cur, "main_paper.tex": mp.replace(da, da.replace(word, word + "s", 1))}, lt,
             {"da_pairs": [("T-DA", word, word + "s")], "da_pins": {}}),
            ("the kept coverage sentence dropped", {**cur, "paper_body.tex": cur["paper_body.tex"].replace(KEEP_SENTENCE, "")}, lt, {}),
            ("a hand-typed numeral added", {**cur, "paper_body.tex": cur["paper_body.tex"].replace(
                "\\subsection{Limitations}", "\\subsection{Limitations}\nThe cells number 17 in all.", 1)}, lt, {}),
        ]
        ok = True
        for name, c, l, kw in planted:
            caught = len(check(wt, c, old, l, **kw)[0]) > len(base_fails)
            ok &= caught
            print(f"  {name}: {'caught' if caught else 'NOT CAUGHT'}")
        # the silent direction: a pinned DA pair is allowed
        c = {**cur, "main_paper.tex": mp.replace(da, da.replace(word, word + "s", 1))}
        quiet = check(wt, c, old, lt, DA_PAIRS + [("T-DA", word, word + "s")], {**DA_PINS, "T-DA": pin(word, word + "s")})[0]
        quiet = [x for x in quiet if "UNCOVERED" not in x]
        silent = not any("Data Availability" in x or "acknowledgments" in x for x in quiet)
        ok &= silent
        print(f"  pinned DA pair: {'silent' if silent else 'FIRED (should be silent)'}")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n, p, c = check(wt, cur, old, lt)
    for f in fails:
        print("  FAIL", f)
    print(f"ledger rows {n}, probes {p}, changed base sentences {c}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
