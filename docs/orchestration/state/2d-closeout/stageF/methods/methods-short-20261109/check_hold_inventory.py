#!/usr/bin/env python3
r"""Check 14 of check_round.py: HOLD-INVENTORY.md, the draft-only cover sheet that carries the paper's record inventory.

From 2026-11-11 to 2026-11-16 the inventory printed as a \pubhold in section 7. It moved to the cover sheet, and section 7
prints nothing in its place (the director, relaying Joseph 2026-11-16). The sheet keeps the gates visible, and this
check fails unless it agrees with the tree:
  a. HOLDS. The sheet's "Holds the paper still prints" list equals, as a set of texts with whitespace collapsed, the
     \pubhold arguments that the paper and the Supplement print (main_paper.tex, paper_body.tex, main_supplement.tex,
     supplemental_body.tex and the app_*.tex files, comments stripped). A new hold must be listed, and the inventory
     cannot return to the paper unlisted.
  b. PAPER NUMBERS. Each "section N (`sec:...`)" gives the number of the paper section or subsection that holds the
     label in paper_body.tex (paper_maps). The fill test checks paper_maps against a real build's main_paper.aux.
  c. SUPPLEMENT NUMBERS. Each "SN (`supp:...`)" gives the number that check_supp_pointers.supp_maps gives the label.
  d. NOTE NUMBERS. Each "section/appendix N (`N-...`)" gives the number of that label in note_release_labels.tex, the
     note at its release revision. make_note_labels.py also reads the sheet's N- labels, so a new one is written there.
  e. RECORDS. Every other backticked path ending in .md or .json, and every DECISION-*.md named in the sheet's comment,
     exists under docs/orchestration/. Every backticked token is of a known kind (label, record, file, or a listed hold).
  f. RELEASE REVISION. The sheet's "`NOTE_RELEASE_REV` (`check_round.py`) is `<sha>`" is a prefix of NOTE_RELEASE_REV.
  g. NAMES. Outside its comment, the sheet names no file whose name contains the author's first name (as check 8 rules
     for print).

usage: check_hold_inventory.py <worktree> [--self-test]     (exit 1 on any failure)"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEET = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/HOLD-INVENTORY.md"
NOTE = "docs/analysis-note"
HOLD_FILES = ("main_paper.tex", "paper_body.tex", "main_supplement.tex", "supplemental_body.tex")
NUM = r"([A-Z](?:\.\d+)*|\d+(?:\.\d+)*)"            # 4, 4.2, B, B.6
PAPER_REF = re.compile(r"sections?\s+" + NUM + r"\s+\(`(sec:[^`]+)`\)")
SUPP_REF = re.compile(r"\bS" + NUM + r"\s+\(`(supp:[^`]+)`\)")
NOTE_REF = re.compile(r"(?:section|appendix)\s+" + NUM + r"\s+\(`N-([^`]+)`\)")
REV = re.compile(r"`NOTE_RELEASE_REV` \(`check_round\.py`\) is `([0-9a-f]{7,40})`")
FILE_TOKENS = {"main_paper.tex", "main_paper.tex:4", "check_round.py", "check_hold_inventory.py", "NOTE_RELEASE_REV",
               "note_release_labels.tex", "draft/methods-short-20261109", "docs/orchestration/", "\\pubhold"}


def strip_comments(t):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.split("\n"))


def pubholds(t):
    """The \\pubhold arguments of a TeX text, comments stripped, braces matched, whitespace collapsed."""
    t = strip_comments(t)
    out = []
    for m in re.finditer(r"\\pubhold\{", t):
        if t[max(0, m.start() - 12):m.start()].endswith("\\newcommand{"):
            continue
        depth, i = 1, m.end()
        while depth and i < len(t):
            depth += {"{": 1, "}": -1}.get(t[i], 0)
            i += 1
        out.append(" ".join(t[m.end():i - 1].split()))
    return out


def paper_maps(body):
    """label -> the number of the section (n) or subsection (n.m) of paper_body.tex that holds it."""
    body = strip_comments(body)
    out, n = {}, 0
    for part in re.split(r"(?=\\section\{)", body):
        if not part.startswith("\\section{"):
            continue
        n += 1
        for m, sub in enumerate(re.split(r"(?=\\subsection\{)", part)):
            for lab in re.findall(r"\\label\{([^}]+)\}", sub):
                out.setdefault(lab, f"{n}.{m}" if m else str(n))
    return out


def note_numbers(labels_tex):
    return {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{N-([^}]+)\}\{\{([^}]*)\}", labels_tex)}


def sheet_sections(sheet):
    """(visible text, comment text, the listed printed holds)."""
    comments = "\n".join(re.findall(r"<!--(.*?)-->", sheet, flags=re.S))
    vis = re.sub(r"<!--.*?-->", "", sheet, flags=re.S)
    m = re.search(r"^## Holds the paper still prints\n(.*?)(?=^## )", vis, flags=re.S | re.M)
    listed = []
    if m:
        for item in re.split(r"\n(?=- )", m.group(1).strip()):
            if item.startswith("- "):
                h = re.match(r"- `([^`]+)`", item)
                if h:
                    listed.append(" ".join(h.group(1).split()))
    return vis, comments, listed, (m.group(0) if m else "")


def load_csp(wt):
    """check_supp_pointers.py's functions. The script runs its check at module level and exits, so it is executed with
    its own directory as the working directory, its output discarded and its exit caught; its functions stay defined."""
    import contextlib
    import io
    import os
    ns = {"__name__": "check_supp_pointers"}
    src = (wt / NOTE / "check_supp_pointers.py").read_text()
    cwd, argv = os.getcwd(), sys.argv
    try:
        os.chdir(wt / NOTE)
        sys.argv = ["check_supp_pointers.py"]
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(src, "check_supp_pointers.py", "exec"), ns)
    except SystemExit:
        pass
    finally:
        os.chdir(cwd)
        sys.argv = argv
    return ns


# Content anchors (moved with the inventory from check_supp_pointers.ANCHORS, whose row tied the hold's ensemble-average
# pointers to their targets): (sheet row, Supplement label, regex the label's own text must contain).
ANCHORS = [(6, "supp:diagnostics", r"ensemble average"), (6, "supp:tests", r"ensemble average")]


def supp_maps(supp_body, wt):
    """(label -> the Supplement's number for it, label -> the text of its section or subsection)."""
    csp = load_csp(wt)
    secs = csp["supp_maps"](supp_body)
    text = {k: re.sub(r"\s+", " ", v) for k, v in csp["TEXT"].items()}
    return (secs[0] if isinstance(secs, tuple) else secs), text


def check(wt, texts=None, sheet=None, labels_tex=None, release=None, exists=None):
    wt = Path(wt)
    texts = texts if texts is not None else {f: (wt / NOTE / f).read_text() for f in HOLD_FILES}
    texts = {**{p.name: p.read_text() for p in sorted((wt / NOTE).glob("app_*.tex"))}, **texts}
    if sheet is None:
        p = wt / SHEET
        if not p.exists():
            return [f"hold inventory: {SHEET} is missing"]
        sheet = p.read_text()
    labels_tex = labels_tex if labels_tex is not None else (wt / NOTE / "note_release_labels.tex").read_text()
    if release is None:
        m = re.search(r'^NOTE_RELEASE_REV = "([0-9a-f]{40})"', (HERE / "check_round.py").read_text(), flags=re.M)
        release = m.group(1) if m else ""
    exists = exists or (lambda rel: (wt / "docs/orchestration" / rel).is_file())
    fails = []
    vis, comments, listed, holds_block = sheet_sections(sheet)
    if "**Rule.** Do not submit a build" not in vis:
        fails.append("hold inventory: the sheet does not state the rule (do not submit a build that renders any \\pubhold)")
    printed = []
    for f, t in texts.items():
        printed += pubholds(t)
    if sorted(printed) != sorted(listed):
        extra = sorted(set(printed) - set(listed))
        gone = sorted(set(listed) - set(printed))
        fails.append(f"hold inventory: the printed holds and the sheet's list differ: printed, not listed {extra}; "
                     f"listed, not printed {gone}")
    if any(h.startswith("Where each record") for h in printed):
        fails.append("hold inventory: the record inventory prints as a \\pubhold again; its carrier is the cover sheet")
    pm = paper_maps(texts["paper_body.tex"])
    sm, stext = supp_maps(texts["supplemental_body.tex"], wt)
    nm = note_numbers(labels_tex)
    inv = vis.split("## Where each record", 1)[-1]
    rows = {int(n): " ".join(r.split()) for n, r in re.findall(r"^(\d+)\. (.*?)(?=^\d+\. |\Z)", inv, flags=re.S | re.M)}
    for row, lab, rx in ANCHORS:
        if f"(`{lab}`)" not in rows.get(row, ""):
            fails.append(f"hold inventory: row {row} no longer points to `{lab}`; update ANCHORS with the row")
        elif not re.search(rx, stext.get(lab, ""), flags=re.I):
            fails.append(f"hold inventory: row {row}'s target `{lab}` does not contain /{rx}/")
    known = set()
    for num, lab in PAPER_REF.findall(vis):
        known.add(lab)
        if pm.get(lab) != num:
            fails.append(f"hold inventory: section {num} (`{lab}`), but the paper gives {pm.get(lab, 'no such label')}")
    for num, lab in SUPP_REF.findall(vis):
        known.add(lab)
        if sm.get(lab) != num:
            fails.append(f"hold inventory: S{num} (`{lab}`), but the Supplement gives S{sm.get(lab, '? (no such label)')}")
    for num, lab in NOTE_REF.findall(vis):
        known.add("N-" + lab)
        if nm.get(lab) != num:
            fails.append(f"hold inventory: note {num} (`N-{lab}`), but note_release_labels.tex gives "
                         f"{nm.get(lab, 'no such label (rerun make_note_labels.py)')}")
    m = REV.search(vis)
    if not m or not release.startswith(m.group(1)):
        fails.append(f"hold inventory: the sheet's release revision {m.group(1) if m else '?'} is not "
                     f"NOTE_RELEASE_REV {release[:12]}")
    else:
        known.add(m.group(1))
    holds_vis = set(re.findall(r"`([^`]+)`", holds_block))
    for tok in re.findall(r"`([^`]+)`", vis):
        if tok in known or tok in FILE_TOKENS or tok in holds_vis:
            continue
        if re.search(r"\.(md|json)$", tok):
            if not exists(tok):
                fails.append(f"hold inventory: record {tok} does not exist under docs/orchestration/")
        else:
            fails.append(f"hold inventory: a backticked token of no known kind: {tok!r}")
    for d in re.findall(r"DECISION-[0-9A-Za-z-]+\.md", comments):
        if not exists(d):
            fails.append(f"hold inventory: decision record {d} does not exist under docs/orchestration/")
    if re.search(r"[\w./-]*joseph[\w./-]*\.(md|json|tex|py)\b", vis, flags=re.I):
        fails.append("hold inventory: the sheet names the author's first name outside its comment")
    return fails


def self_test(wt):
    wt = Path(wt)
    texts = {f: (wt / NOTE / f).read_text() for f in HOLD_FILES}
    sheet = (wt / SHEET).read_text()
    labels = (wt / NOTE / "note_release_labels.tex").read_text()
    base = check(wt)
    ok = not base
    if base:
        print("self-test: the committed tree fails:", base)
    pb = texts["paper_body.tex"]
    mp = texts["main_paper.tex"]
    planted = [
        ("a new printed hold", {**texts, "paper_body.tex": pb.replace("\\subsection{Limitations}",
                                                                      "\\pubhold{new gate.}\n\n\\subsection{Limitations}", 1)}, sheet, labels),
        ("the inventory back in the paper", {**texts, "paper_body.tex": pb.replace(
            "\\subsection{Limitations}", "\\pubhold{Where each record this paper relies on is published.}\n\n\\subsection{Limitations}", 1)}, sheet, labels),
        ("a printed hold removed", {**texts, "main_paper.tex": mp.replace("\\pubhold{funding and grant acknowledgments}", "", 1)}, sheet, labels),
        ("a wrong paper number", texts, sheet.replace("section\n   4.2 (`sec:paired2d`)", "section\n   4.3 (`sec:paired2d`)", 1), labels),
        ("a wrong Supplement number", texts, sheet.replace("S7 (`supp:ibu`) only", "S8 (`supp:ibu`) only", 1), labels),
        ("a wrong note number", texts, sheet.replace("appendix B.6", "appendix B.5", 1), labels),
        ("a note label not in the labels file", texts, sheet, re.sub(r"\\newlabel\{N-sec:cov1b-gate\}.*\n", "", labels)),
        ("a missing record", texts, sheet.replace("OUTCOME-20261106-ref-g1-r1-differ.md", "OUTCOME-20261106-no-such.md", 1), labels),
        ("a missing decision record", texts, sheet.replace("DECISION-20261109-joseph-bias-half-rule.md",
                                                           "DECISION-20261109-joseph-no-such.md", 1), labels),
        ("a stale release revision", texts, sheet.replace("is `8342963c1`", "is `acf934d71`", 1), labels),
        ("an unknown token", texts, sheet.replace("Record `OUTCOME-20261106-ref-c2c1-read.md`",
                                                  "Record `OUTCOME-20261106-ref-c2c1-read`", 1), labels),
        ("a visible author name", texts, sheet.replace("the decision withholding", "DECISION-20261110-joseph-vprior-withhold.md, the decision withholding", 1), labels),
        ("the rule dropped", texts, sheet.replace("**Rule.** Do not submit a build", "Do not submit a build", 1), labels),
        ("an anchor's target loses its text", {**texts, "supplemental_body.tex": re.sub(r"ensemble[- ~]average", "mean",
                                                texts["supplemental_body.tex"], flags=re.I)}, sheet, labels),
        ("an anchored row repointed", texts, sheet.replace("S4.4 (`supp:diagnostics`)", "S4 (`supp:estimators`)", 1), labels),
    ]
    for name, t, s, l in planted:
        if s == sheet and t is texts and l == labels:
            print(f"self-test: planting {name!r} changed nothing"); ok = False; continue
        got = check(wt, texts=t, sheet=s, labels_tex=l)
        if len(got) <= len(base):
            print(f"self-test: NOT CAUGHT: {name}"); ok = False
    print("CHECK-HOLD-INVENTORY SELF-TEST ::", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    wt = Path(argv[1]) if len(argv) > 1 and not argv[1].startswith("--") else Path(".")
    if "--self-test" in argv:
        return 0 if self_test(wt) else 1
    fails = check(wt)
    for f in fails:
        print("FAIL", f)
    print("CHECK-HOLD-INVENTORY ::", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
