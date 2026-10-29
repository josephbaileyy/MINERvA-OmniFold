#!/usr/bin/env python3
"""Check the r21 rewrite of the paper body against its fact ledger (r21/fact-ledger.md, built from the base by an
independent agent; the writer adds an `after` column).

usage: check_ledger.py <worktree> [--base SHA] [--ledger PATH] [--require-after]
       check_ledger.py <worktree> --self-test [--base SHA]

Ledger rows: | id | section | fact | atoms | base | status | base text | after |, the atoms in backticks joined by
` && `. The sentence functions are note-n4/check_ledger.py's, imported, not copied.
Checks:
  1. every row's atoms print in the new paper_body.tex (printed text). With --require-after (the default once the
     writer has delivered), each non-STRUCTURE fact row also names its `after` sentence, which must print in the new
     body and must contain every one of the row's atoms;
  2. the PLANTED row fails (a ledger whose planted row passes is refused);
  3. every base sentence id PB0..PBn is the base of some row (the ledger covers the base);
  4. each GATE atom prints exactly once, and the FROZEN sentence prints;
  5. every \\label of the base body still exists;
  6. no new number: every numeral token of the new body's printed text, outside macro arguments, also occurs in the
     base body's printed text;
  7. protected text is byte-identical to the base: main_paper.tex from \\title to \\end{abstract}, and from
     \\begin{acknowledgments} to \\end{document} (Data Availability included: it is out of r21, ruling 2), and every
     \\pubhold hold.
Exit 1 on any failure."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "note-n4"))
from check_ledger import printed, sentences  # noqa: E402

BASE = "78df7327"
NUM = re.compile(r"(?<![A-Za-z\\{])\d+(?:[.,]\d+)*")
HOLD = re.compile(r"\\pubhold\{[^{}]*\}|^.*\\newcommand\{\\pubhold\}.*$", re.M)


def show(wt, rev, f):
    return subprocess.run(["git", "-C", str(wt), "show", f"{rev}:docs/analysis-note/{f}"], capture_output=True,
                          text=True, check=True).stdout


def rows(text):
    out = []
    for line in text.splitlines():
        if not re.match(r"^\| F(X|\d+) \|", line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split(" | ")]
        rid, sec, fact, atoms, base, status = c[:6]
        after = c[7] if len(c) > 7 else ""
        at = [a.strip()[1:-1] if a.strip().startswith("`") and a.strip().endswith("`") else a.strip()
              for a in atoms.split(" && ")]
        aft = after.strip()
        aft = aft[1:-1] if aft.startswith("`") and aft.endswith("`") else aft
        out.append({"id": rid, "atoms": [re.sub(r"\s+", " ", a) for a in at if a], "base": base, "status": status,
                    "after": re.sub(r"\s+", " ", aft)})
    return out


def numerals(t):
    t = re.sub(r"\\(fvval|ref|ref\*|nsec|napp|label|cite|includegraphics|eqref)(\[[^]]*\])?\{[^}]*\}", " ", t)
    return set(NUM.findall(t))


def span(text, a, b):
    i = text.find(a)
    j = text.find(b, i)
    return text[i:j + len(b)] if i >= 0 and j >= 0 else None


def check(cur_pb, old_pb, cur_mp, old_mp, ledger, require_after):
    fails = []
    R = rows(ledger)
    new = printed(cur_pb)
    base_sents = sentences(printed(old_pb))
    new_sents = set(sentences(new))
    # the phrases check_sec4_receipts.py binds, as the ledger's header lists them ("1. `...`" to "8. `...`")
    bound = set(re.findall(r"^\s+\d\. `([^`]+)`", ledger, re.M))
    if len(bound) != 8:
        fails.append(f"the ledger header lists {len(bound)} bound phrases, not 8")
    planted = [r for r in R if r["status"] == "PLANTED"]
    if not planted:
        fails.append("no PLANTED row: the ledger carries no control")
    for r in R:
        if r["status"] in ("PROTECTED",):
            continue
        missing = [a for a in r["atoms"] if a not in new]
        if r["status"] == "PLANTED":
            if not missing:
                fails.append(f"{r['id']}: the PLANTED row passes, so the check proves nothing")
            continue
        if missing:
            fails.append(f"{r['id']}: atom(s) not printed: {[m[:60] for m in missing]}")
        if require_after and r["status"] not in ("STRUCTURE",):
            if not r["after"]:
                fails.append(f"{r['id']}: no after sentence")
            elif r["after"] not in new:
                fails.append(f"{r['id']}: its after sentence does not print: {r['after'][:80]!r}")
            else:
                bad = [a for a in r["atoms"] if a not in r["after"]]
                if bad:
                    fails.append(f"{r['id']}: its after sentence lacks atom(s) {[b[:50] for b in bad]}")
        if r["status"] == "GATE":
            for a in r["atoms"]:
                if a in bound and new.count(a) != 1:
                    fails.append(f"{r['id']}: the bound phrase prints {new.count(a)} times: {a[:60]!r}")
        if r["status"] == "FROZEN" and "Interval coverage has not been validated." not in new_sents:
            fails.append(f"{r['id']}: the FROZEN sentence does not print as its own sentence")
    named = {r["base"] for r in R if r["base"].startswith("PB")}
    for i in range(len(base_sents)):
        if f"PB{i}" not in named:
            fails.append(f"UNCOVERED base sentence PB{i}: {base_sents[i][:80]!r}")
    for lab in sorted(set(re.findall(r"\\label\{([^}]*)\}", old_pb)) - set(re.findall(r"\\label\{([^}]*)\}", cur_pb))):
        fails.append(f"LABEL REMOVED: {lab}")
    extra = numerals(new) - numerals(printed(old_pb))
    if extra:
        fails.append(f"NEW NUMBER(S) in the body: {sorted(extra)[:12]}")
    for a, b in (("\\title", "\\end{abstract}"), ("\\begin{acknowledgments}", "\\end{document}")):
        if span(old_mp, a, b) != span(cur_mp, a, b):
            fails.append(f"PROTECTED: main_paper.tex {a}..{b} differs from base")
    if HOLD.findall(old_mp) != HOLD.findall(cur_mp) or HOLD.findall(old_pb) != HOLD.findall(cur_pb):
        fails.append("PROTECTED: a \\pubhold hold differs from base")
    return fails, len(R)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--ledger", default=str(HERE / "fact-ledger.md"))
    ap.add_argument("--require-after", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve()
    D = wt / "docs/analysis-note"
    cur_pb, cur_mp = (D / "paper_body.tex").read_text(), (D / "main_paper.tex").read_text()
    old_pb, old_mp = show(wt, a.base, "paper_body.tex"), show(wt, a.base, "main_paper.tex")
    lt = Path(a.ledger).read_text()
    if a.self_test:
        # On the base itself, with each row's after sentence set to its base sentence, the check must be silent; then
        # each planted defect must fire.
        bs = sentences(printed(old_pb))
        filled = []
        for line in lt.splitlines():
            m = re.match(r"^\| (F\d+|FX) \|.*\| (PB(\d+)) \| (\w+) \|", line)
            if m and m.group(4) not in ("STRUCTURE", "PLANTED", "PROTECTED"):
                line = line.rstrip() + f" `{bs[int(m.group(3))]}` |"
            filled.append(line)
        fl = "\n".join(filled)
        base_fails, _ = check(old_pb, old_pb, old_mp, old_mp, fl, True)
        ok = not base_fails
        print(f"  {'ok  ' if ok else 'FAIL'} the base, as its own rewrite, passes" + ("" if ok else f": {base_fails[:3]}"))
        gate = next(r for r in rows(lt) if r["status"] == "GATE")["atoms"][0]
        kept = next(r for r in rows(lt) if r["status"] == "KEEP")["atoms"][0]
        abs_ = span(old_mp, "\\begin{abstract}", "\\end{abstract}")
        plants = [
            ("a dropped KEEP atom", old_pb.replace(kept, "", 1), old_mp, fl),
            ("a GATE phrase printed twice", old_pb.replace(gate, gate + " " + gate, 1), old_mp, fl),
            ("a new number", old_pb.replace("\\subsection{Limitations}", "\\subsection{Limitations}\nWe used 9137 events.", 1), old_mp, fl),
            ("a removed label", re.sub(r"\\label\{[^}]*\}", "", old_pb, count=1), old_mp, fl),
            ("an abstract edit", old_pb, old_mp.replace(abs_, abs_.replace(" the ", " a ", 1)), fl),
            ("a PLANTED row that passes", old_pb + "\n@@PLANTED@@\n", old_mp, fl),
            ("an uncovered base sentence", old_pb, old_mp, "\n".join(l for l in fl.splitlines() if "| PB3 |" not in l)),
        ]
        for name, pb, mp, l in plants:
            caught = len(check(pb, old_pb, mp, old_mp, l, True)[0]) > len(base_fails)
            ok &= caught
            print(f"  {'ok  ' if caught else 'FAIL'} {name} is caught")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n = check(cur_pb, old_pb, cur_mp, old_mp, lt, a.require_after)
    for f in fails:
        print("  FAIL", f)
    print(f"ledger rows {n}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
