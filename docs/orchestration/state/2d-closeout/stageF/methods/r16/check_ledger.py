#!/usr/bin/env python3
"""Check the r16 fact ledger against a worktree, and check that the round dropped no sentence silently.

usage: check_ledger.py <worktree> [--base SHA] [--ledger PATH]   # exit 1 on any failure
       check_ledger.py <worktree> --list [--base SHA]            # print the changed sentences with their ids
       check_ledger.py <worktree> --self-test [--base SHA]       # planted defects must each be caught

Four checks:
  1. Probes. Every probe of every row must occur in the printed source, after comments are stripped and whitespace is
     collapsed. P::text is looked up in docs/analysis-note/paper_body.tex, MP::text in main_paper.tex, and
     N:file::text in docs/analysis-note/<file>.
  2. Dispositions. A MOVE->note row needs an N: probe. Every other row (KEEP, MOVE->L, MOVE->S, COLLAPSED, REPOINT)
     needs a P: or MP: probe.
  3. Coverage. Every printed sentence of paper_body.tex and main_paper.tex at --base that no longer prints verbatim
     must be named in the "before" column of some row, as P<n> or M<n>.
  4. Protected text. The span of main_paper.tex from \\begin{acknowledgments} to \\end{document} must be
     byte-identical to --base, and so must every line of either file that holds \\pubhold.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

FILES = {"P": "paper_body.tex", "M": "main_paper.tex"}


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src).strip()


def sentences(t):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\\$(0-9])", t) if p.strip()]


def at_base(wt, base, name):
    return subprocess.run(["git", "-C", str(wt), "show", f"{base}:docs/analysis-note/{name}"],
                          capture_output=True, text=True, check=True).stdout


def load(wt, base):
    D = wt / "docs/analysis-note"
    cur = {k: (D / f).read_text() for k, f in FILES.items()}
    old = {k: at_base(wt, base, f) for k, f in FILES.items()}
    return cur, old


def changed(cur, old):
    out = []
    for k in FILES:
        a = printed(cur[k])
        for i, s in enumerate(sentences(printed(old[k]))):
            if s not in a:
                out.append((f"{k}{i}", s))
    return out


def rows(ledger_text):
    for line in ledger_text.splitlines():
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) == 6:
            yield cells


def check(wt, cur, old, ledger_text, note_override=None):
    fails = []
    note_cache = {}

    def text(key):
        if key in ("P", "M"):
            return printed(cur[key])
        if note_override and key in note_override:
            return printed(note_override[key])
        if key not in note_cache:
            note_cache[key] = printed((wt / "docs/analysis-note" / key).read_text())
        return note_cache[key]

    named, n_rows, n_probes = set(), 0, 0
    for rid, fact, before, disp, after, probe in rows(ledger_text):
        n_rows += 1
        named |= set(re.findall(r"\b[PM]\d+\b", before))
        kinds = set()
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(P|MP|N:[\w.]+)::(.*)$", p)
            if not m:
                fails.append(f"{rid}: malformed probe {p!r}")
                continue
            where, lit = m.group(1), re.sub(r"\s+", " ", m.group(2))
            key = "P" if where == "P" else "M" if where == "MP" else where[2:]
            kinds.add("N" if where.startswith("N:") else "P")
            n_probes += 1
            if lit not in text(key):
                fails.append(f"{rid}: NOT FOUND in {FILES.get(key, key)}: {lit[:90]!r}")
        if disp.startswith("MOVE→note") and "N" not in kinds:
            fails.append(f"{rid}: MOVE→note row without a note probe")
        if not disp.startswith("MOVE→note") and "P" not in kinds:
            fails.append(f"{rid}: in-paper row without a paper probe")
    ch = changed(cur, old)
    for sid, s in ch:
        if sid not in named:
            fails.append(f"UNCOVERED {sid}: {s[:100]!r}")
    # protected text
    def span(t):
        i, j = t.find("\\begin{acknowledgments}"), t.find("\\end{document}")
        return t[i:j] if i >= 0 and j > i else None
    if span(cur["M"]) is None or span(cur["M"]) != span(old["M"]):
        fails.append("PROTECTED: main_paper.tex acknowledgments..end{document} differs from base")
    for k in FILES:
        h_old = [l for l in old[k].splitlines() if "\\pubhold" in l]
        h_cur = [l for l in cur[k].splitlines() if "\\pubhold" in l]
        if h_old != h_cur:
            fails.append(f"PROTECTED: \\pubhold lines of {FILES[k]} differ from base")
    return fails, n_rows, n_probes, len(ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="927f40bf0792556e3fa50a841a139905a63bd619")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("ledger.md")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve()
    cur, old = load(wt, a.base)
    ledger_text = Path(a.ledger).read_text()
    if a.list:
        for sid, s in changed(cur, old):
            print(f"{sid}: {s}\n")
        return 0
    if a.self_test:
        ok = True
        f0, *_ = check(wt, cur, old, ledger_text)
        if f0:
            print("self-test needs a clean ledger first:", *f0[:5], sep="\n  ")
            return 1
        # (a) a planted probe that does not print must fail
        bad = ledger_text + "\n| X1 | planted | P0 | KEEP | I | `P::this sentence was never printed anywhere` |\n"
        fa, *_ = check(wt, cur, old, bad)
        ok &= any(x.startswith("X1: NOT FOUND") for x in fa)
        print("planted bad paper probe:", "caught" if any(x.startswith("X1: NOT FOUND") for x in fa) else "MISSED")
        # (b) a planted note probe on a moved fact, with the note text removed, must fail
        rid = "K3"
        nf = wt / "docs/analysis-note/sec_joint.tex"
        note = printed(nf.read_text()).replace("The scan probes one prescribed direction;", "XX")
        assert note != printed(nf.read_text()), "the planted deletion must change the note"
        fb, *_ = check(wt, cur, old, ledger_text, note_override={"sec_joint.tex": note})
        hit = any(x.startswith(f"{rid}: NOT FOUND") for x in fb)
        ok &= hit
        print("collapsed fact deleted from the note:", "caught" if hit else "MISSED")
        # (c) deleting an unchanged printed sentence from the paper must be UNCOVERED
        victim = "Each OmniFold iteration consists of two classification steps."
        cur_c = dict(cur, P=cur["P"].replace(victim, ""))
        fc, *_ = check(wt, cur_c, old, ledger_text)
        hit = any(x.startswith("UNCOVERED") and "Each OmniFold iteration" in x for x in fc)
        ok &= hit
        print("silently dropped sentence:", "caught" if hit else "MISSED")
        # (d) an edit inside the protected span must fail
        cur_d = dict(cur, M=cur["M"].replace("under project m3246", "under project m3247"))
        fd, *_ = check(wt, cur_d, old, ledger_text)
        hit = any(x.startswith("PROTECTED") for x in fd)
        ok &= hit
        print("edit in the protected span:", "caught" if hit else "MISSED")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n_rows, n_probes, n_ch = check(wt, cur, old, ledger_text)
    for f in fails:
        print(f)
    print(f"ledger rows {n_rows}, probes {n_probes}, changed sentences {n_ch}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
