#!/usr/bin/env python3
"""Check the five-observable integration PR's fact ledger against a worktree, and check that no sentence left silently.

usage: check_ledger.py <worktree> [--base SHA] [--ledger PATH] [--old-dir DIR] [--files f1,f2,...]
       check_ledger.py <worktree> --list [--base SHA] [--files ...]   # changed base sentences, with their ids
       check_ledger.py <worktree> --self-test [--base SHA]             # planted defects must each be caught

Ledger rows: | id | fact | before | disposition | after | probe |. Probes, several joined by ` && `:
  N:<file>::text   prints in docs/analysis-note/<file> (comment-stripped, whitespace-collapsed source)
  X:<file>::text   no longer prints there (a removed restatement or phrase)
  P::text          prints in paper_body.tex
  R:<file>::text   prints in the records file docs/analysis-note/<file> (one of RECORDS): the home of a fact removed
                   from the note (director, n2 ruling 1: every removed provenance fact carries one)
Checks:
  1. every probe holds;
  2. every printed base sentence of the batch files that no longer prints verbatim is named in some row's "before"
     column, by its id (file prefix + index, as --list prints);
  3. every \\label of the base batch files still exists in the same file;
  4. protected files are byte-identical to the protected base (--protected-base; default the merge base of HEAD and
     origin/main, n3 2026-10-27): values.tex, values_inference.tex, app_history.tex,
     app_release.tex, main_note.tex, main_paper.tex, paper_body.tex (main_records.tex has not been protected since n2: N2-1
     numbers the App. G entries there; check_note_records.py P5 guards the record paragraphs);
  5. the check-bound SEC4 phrases still print once in sec_validation.tex;
  6. the structural exception (director, 2026-10-27): main_note.tex and main_paper.tex differ from the protected base
     by exactly the added lines in STRUCTURAL, and in nothing else outside their abstract blocks (ABSTRACT_OPEN, director
     2026-10-27, for the move decision's item 5; the abstract text itself is Joseph's);
  7. no numeral is typed by hand in the new prose (sec_fived16.tex, and paper_body.tex between FIVED16-BEGIN and
     FIVED16-END): every number prints through \fvval{key} from values_fived16.tex, which make_values_fived16.py
     generates from pinned readouts; only the integers in NUMERAL_OK may appear bare.
Adapted from note-consolidate/check_ledger.py (paper_body.tex and sec_fived16.tex join the checked files; main_note,
main_paper and paper_body leave PROTECTED, the first two under STRUCTURAL).
Exit 1 on any failure."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

PREFIX = {"sec_execsummary.tex": "ES", "sec_intro.tex": "IN", "sec_summary.tex": "SU", "sec_method.tex": "ME",
          "sec_systematics.tex": "SY", "sec_validation.tex": "VA", "sec_3d.tex": "TD", "sec_eavailw.tex": "EW",
          "sec_5d.tex": "FD", "sec_joint.tex": "JT", "sec_fps.tex": "FP", "app_statmethods.tex": "AA",
          "app_statmethods_nd.tex": "AB", "app_negweight.tex": "AC", "app_response_mismatch.tex": "AD",
          "result_status_rows.tex": "RS", "selection_features.tex": "SF", "app_guide.tex": "AG", "app_codebase.tex": "AH",
          "paper_body.tex": "PB", "sec_fived16.tex": "FV"}
RECORDS = {"app_provenance.tex", "app_history.tex", "app_release_records.tex", "app_codebase_records.tex",
           "main_records.tex"}
PROTECTED = ["values.tex", "values_inference.tex", "app_history.tex", "app_release.tex"]
STRUCTURAL = {"main_note.tex": [r"\input{values_fived16}", r"\input{sec_fived16}"],
              "main_paper.tex": [r"\input{values_fived16}"]}
# The abstract block of each driver may change (director, 2026-10-27, approving decision
# DECISION-20261027-joseph-move-nonfinal-configurations-to-note item 5 for the abstract block only): the lines strictly between
# \begin{abstract} and \end{abstract}. Every other line of the driver must still equal the protected base.
ABSTRACT_OPEN = {"main_paper.tex", "main_note.tex"}


def mask_abstract(text):
    """The driver with its abstract block's content replaced by one marker line; None if the markers are not each once."""
    lines = text.splitlines()
    if lines.count("\\begin{abstract}") != 1 or lines.count("\\end{abstract}") != 1:
        return None
    a, b = lines.index("\\begin{abstract}"), lines.index("\\end{abstract}")
    if b < a:
        return None
    return "\n".join(lines[:a + 1] + ["@@ABSTRACT@@"] + lines[b:])


NUMERAL_OK = {"16", "8", "5"}   # the cell count, GiBUU's cell count, the number of observables
SEC4 = [r"lies entirely below its window \(Gaussian 0\.954\)",
        r"removes the tail undercoverage: \$C_2=0\.977\$ \$\[0\.974,0\.980\]\$ and \$C_1=0\.781\$"]
IDRX = re.compile(r"\b(" + "|".join(sorted(PREFIX.values(), key=len, reverse=True)) + r")\d+\b")


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src).strip()


def sentences(t):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\\$(0-9])", t) if p.strip()]


def base_text(wt, base, name, old_dir):
    if old_dir:
        p = Path(old_dir) / name
        return p.read_text() if p.exists() else ""   # a file new in this PR has no base text
    r = subprocess.run(["git", "-C", str(wt), "show", f"{base}:docs/analysis-note/{name}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def rows(text):
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("| id ") and not line.startswith("|---"):
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            if len(c) == 6:
                yield c


def changed(cur, old, files):
    out = []
    for f in files:
        a = printed(cur[f])
        for i, s in enumerate(sentences(printed(old[f]))):
            if s not in a:
                out.append((f"{PREFIX[f]}{i}", f, s))
    return out


def new_prose(cur):
    """(name, printed text) of the new prose: sec_fived16.tex, and paper_body.tex between the FIVED16 markers."""
    out = []
    if "sec_fived16.tex" in cur:
        out.append(("sec_fived16.tex", cur["sec_fived16.tex"]))
    for m in re.finditer(r"% FIVED16-BEGIN[^\n]*\n(.*?)% FIVED16-END", cur.get("paper_body.tex", ""), re.S):
        out.append(("paper_body.tex (FIVED16 block)", m.group(1)))
    return out


def numerals(cur):
    fails = []
    for name, src in new_prose(cur):
        t = printed(src)
        t = re.sub(r"\\(fvval|ref|label|cite|eqref|input|includegraphics|fvpending)(\[[^]]*\])?\{[^}]*\}", " ", t)
        t = re.sub(r"\bR\d\d\b", " ", t)                       # cell names R00-R15
        t = re.sub(r"\^\{?2\}?", " ", t)                          # the square of chi^2 is notation, not a number
        t = re.sub(r"\\multicolumn\{\d+\}", " ", t)                 # a table's column span is layout
        t = re.sub(r"\\cmidrule(\([a-z]*\))?\{\d+-\d+\}", " ", t)    # a rule's column range is layout
        t = re.sub(r"\\setlength\{\\\w+\}\{[\d.]+pt\}", " ", t)   # a table's column spacing is layout
        t = re.sub(r"_\{?\d\}?", " ", t)                            # a one-digit subscript (q_3, chi^2_16 is caught)
        t = re.sub(r"\\[A-Za-z]+", " ", t)                        # other macro names
        for m in re.finditer(r"(?<![A-Za-z])\d+(?:\.\d+)?", t):
            if m.group(0) not in NUMERAL_OK:
                fails.append(f"NUMERAL typed by hand in {name}: {m.group(0)!r} in {t[max(0, m.start() - 40):m.end() + 20]!r}")
    return fails


def check(wt, cur, old, files, ledger_text, prot_cur, prot_old, struct_cur=None):
    fails, named, n_rows, n_probes = [], set(), 0, 0
    D = wt / "docs/analysis-note"
    cache = {}

    def txt(f):
        if f not in cache:
            cache[f] = printed(cur[f]) if f in cur else printed((D / f).read_text())
        return cache[f]
    for rid, fact, before, disp, after, probe in rows(ledger_text):
        n_rows += 1
        named |= {m.group(0) for m in IDRX.finditer(before)}
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(N|X|R):([\w.]+)::(.*)$|P::(.*)$", p)
            if not m:
                fails.append(f"{rid}: malformed probe {p!r}"); continue
            n_probes += 1
            if m.group(4) is not None:
                ok = re.sub(r"\s+", " ", m.group(4)) in printed((D / "paper_body.tex").read_text())
                if not ok: fails.append(f"{rid}: NOT FOUND in paper_body.tex: {m.group(4)[:80]!r}")
                continue
            kind, f, lit = m.group(1), m.group(2), re.sub(r"\s+", " ", m.group(3))
            present = lit in txt(f)
            if kind == "N" and not present: fails.append(f"{rid}: NOT FOUND in {f}: {lit[:90]!r}")
            if kind == "X" and present: fails.append(f"{rid}: STILL PRINTS in {f}: {lit[:90]!r}")
            if kind == "R" and f not in RECORDS: fails.append(f"{rid}: R: probe names {f}, not a records file")
            elif kind == "R" and not present: fails.append(f"{rid}: NOT IN THE RECORDS ({f}): {lit[:90]!r}")
    ch = changed(cur, old, files)
    for sid, f, s in ch:
        if sid not in named:
            fails.append(f"UNCOVERED {sid} ({f}): {s[:100]!r}")
    for f in files:
        lo = set(re.findall(r"\\label\{([^}]*)\}", old[f])); ln = set(re.findall(r"\\label\{([^}]*)\}", cur[f]))
        for lab in sorted(lo - ln):
            fails.append(f"LABEL REMOVED {f}: {lab}")
    for f in PROTECTED:
        if prot_cur.get(f) != prot_old.get(f):
            fails.append(f"PROTECTED changed: {f}")
    for f, allowed in STRUCTURAL.items():
        lines = (struct_cur or {}).get(f, (D / f).read_text()).splitlines()
        for a in allowed:
            if lines.count(a) != 1:
                fails.append(f"STRUCTURAL {f}: the line {a!r} must appear exactly once")
            elif a in lines:
                lines.remove(a)
        now, base = "\n".join(lines), "\n".join(prot_old.get(f, "").splitlines())
        if f in ABSTRACT_OPEN:
            now, base = mask_abstract(now), mask_abstract(base)
            if now is None:
                fails.append(f"STRUCTURAL {f}: the abstract markers must each appear exactly once, in order")
        if now is not None and now != base:
            fails.append(f"STRUCTURAL {f}: changed beyond the approved \\input lines and the abstract block")
    fails += numerals(cur)
    if "sec_validation.tex" in cur:
        v = printed(cur["sec_validation.tex"])
        for rx in SEC4:
            if len(re.findall(rx, v)) != 1:
                fails.append(f"SEC4 site not found once in sec_validation.tex: {rx}")
    return fails, n_rows, n_probes, len(ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="8b0f83fd")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("ledger.md")))
    ap.add_argument("--old-dir")
    ap.add_argument("--protected-base", help="commit the protected files are compared with (default: the merge base of HEAD and origin/main, so a protected-file change that reached main by its own PR, such as the absence audit #400, is not charged to the round; falls back to --base)")
    ap.add_argument("--files", default=",".join(PREFIX))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve(); D = wt / "docs/analysis-note"
    files = [f for f in a.files.split(",") if f]
    prot_cur = {f: (D / f).read_text() for f in PROTECTED}
    files = [f for f in files if (D / f).exists()]
    cur = {f: (D / f).read_text() for f in files}
    old = {f: base_text(wt, a.base, f, a.old_dir) for f in files}
    pbase = a.protected_base
    if not pbase and not a.old_dir:
        mb = subprocess.run(["git", "-C", str(wt), "merge-base", "HEAD", "origin/main"], capture_output=True, text=True)
        pbase = mb.stdout.strip() if mb.returncode == 0 and mb.stdout.strip() else a.base
    prot_old = {f: base_text(wt, pbase or a.base, f, a.old_dir) for f in PROTECTED + list(STRUCTURAL)}
    if a.list:
        for sid, f, s in changed(cur, old, files):
            print(f"{sid}\t{f}\t{s}")
        return 0
    lt = Path(a.ledger).read_text() if Path(a.ledger).exists() else ""
    if a.self_test:
        ok = True
        f0 = files[0]
        sents = sentences(printed(old[f0]))
        s0 = next(s for s in sents if len(s) > 40 and s in printed(cur[f0]))
        planted = [("missing probe", cur, lt + "\n| T1 | t | — | KEEP | — | `N:%s::@@NO SUCH TEXT@@` |\n" % f0),
                   ("dropped sentence", {**cur, f0: cur[f0].replace(s0.split()[0] + " " + s0.split()[1], "@@", 1)}, lt),
                   ("removed label", {**cur, f0: re.sub(r"\\label\{[^}]*\}", "", cur[f0], count=1)}, lt),
                   ("false R: probe", cur, lt + "\n| T2 | t | — | MOVE | — | `R:app_provenance.tex::@@NOT IN THE RECORDS@@` |\n"),
                   ("R: probe naming a note file", cur, lt + "\n| T3 | t | — | MOVE | — | `R:%s::the` |\n" % f0),
                   ("a numeral typed by hand in the new chapter",
                    {**cur, "sec_fived16.tex": cur.get("sec_fived16.tex", "") + "\nThe median is 7.29 per cent.\n"}, lt),
                   ("a numeral typed by hand in the paper's FIVED16 block",
                    {**cur, "paper_body.tex": cur["paper_body.tex"] + "\n% FIVED16-BEGIN\nIt is 109/16.\n% FIVED16-END\n"}, lt)]
        mn = (D / "main_note.tex").read_text()
        mp = (D / "main_paper.tex").read_text()
        struct_plants = [("an edit after the note abstract's end", {"main_note.tex": mn.replace("\\end{abstract}", "\\end{abstract}\nAn edit.", 1)}),
                         ("the note abstract's end marker removed", {"main_note.tex": mn.replace("\\end{abstract}\n", "", 1)}),
                         ("an edit to the paper's title, outside its abstract", {"main_paper.tex": mp.replace("\\title{", "\\title{An edit ", 1)}),
                         ("an approved input line missing", {"main_note.tex": mn.replace("\\input{sec_fived16}\n", "", 1)})]
        base_fails, *_ = check(wt, cur, old, files, lt, prot_cur, prot_old)
        for name, sc in [("an edit inside the paper abstract", {"main_paper.tex": mp.replace("\\begin{abstract}", "\\begin{abstract}\nAn edit.", 1)}),
                         ("an edit inside the note abstract", {"main_note.tex": mn.replace("\\end{abstract}", "An edit.\n\\end{abstract}", 1)})]:
            fails, *_ = check(wt, cur, old, files, lt, prot_cur, prot_old, sc)
            passed = len(fails) == len(base_fails)
            ok &= passed
            print(f"  {name}: {'allowed' if passed else 'WRONGLY REFUSED'}")
        for name, sc in struct_plants:
            fails, *_ = check(wt, cur, old, files, lt, prot_cur, prot_old, sc)
            base_fails, *_ = check(wt, cur, old, files, lt, prot_cur, prot_old)
            caught = len(fails) > len(base_fails)
            ok &= caught
            print(f"  {name}: {'caught' if caught else 'NOT CAUGHT'}")
        for name, c, l in planted:
            fails, *_ = check(wt, c, old, files, l, prot_cur, prot_old)
            base_fails, *_ = check(wt, cur, old, files, lt, prot_cur, prot_old)
            caught = len(fails) > len(base_fails)
            ok &= caught
            print(f"  {name}: {'caught' if caught else 'NOT CAUGHT'}")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n, p, c = check(wt, cur, old, files, lt, prot_cur, prot_old)
    for f in fails:
        print("  FAIL", f)
    print(f"ledger rows {n}, probes {p}, changed base sentences {c}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
