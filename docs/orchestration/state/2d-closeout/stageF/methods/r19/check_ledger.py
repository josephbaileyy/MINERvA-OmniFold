#!/usr/bin/env python3
"""Check the r19 fact ledger against a worktree, and check that the round dropped no sentence silently.

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
  6. Scope guards (director, 2026-10-28; agy missed a strengthening of a structural sentence twice, so its SAME is no
     evidence there). A GUARD row pins a structural or scope sentence's scope words with a P: or MP: probe, and its
     "after" column names a planted strengthening, `plant: OLD => NEW`. OLD must occur in the probe. --self-test applies
     each plant to the paper and requires that row's probe to fail.
  5. Labels (director, Q2 ruling; DECISION-20261028 item 5). A label of paper_body.tex at --base may be missing now only
     if it is in REMOVABLE, and a label new now must be in ADDABLE.
Adapted from r18/check_ledger.py for r19 (base: step 0, 9df8f748). The five-observable integration's ledger
(fived16/ledger.md) covers 8b0f83fd..9df8f748 and is checked on that revision, not on this worktree.
"""
REMOVABLE = {  # variant B: Sec. VI's seven labels, Table III and Fig. 4 (O1, O4), and Table I (Q1, folded)
    "sec:joint", "sec:hypotheses", "sec:calibration", "sec:conditions", "sec:response", "sec:joint-results",
    "tab:joint", "tab:binned", "fig:coverage", "tab:findings"}
ADDABLE = {"sec:cov16", "tab:result16"}
import argparse
import re
import subprocess
import sys
from pathlib import Path
import hashlib
import importlib.util

_spec = importlib.util.spec_from_file_location("apply_c1a", Path(__file__).resolve().parents[1] / "fived16/c1a/apply_c1a.py")
C1A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C1A)
_spec2 = importlib.util.spec_from_file_location("apply_d2", Path(__file__).resolve().parents[1] / "fived16/d2/apply_d2.py")
D2 = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(D2)

FILES = {"P": "paper_body.tex", "M": "main_paper.tex",
         # the note files r19 adds to (N1-N4): a changed sentence there needs a row too (J, Q, Z ids)
         "J": "sec_joint.tex", "Q": "sec_5d.tex", "Z": "app_codebase.tex",
         # step (c)'s 1A half (fived16/c1a) also edits the note's sixteen-cell chapter and its abstract (F, A ids)
         "F": "sec_fived16.tex", "A": "main_note.tex"}
NOTE_ADDABLE = {"fig:coverage-5d-paper", "app:coverage-fig"}  # N3; F3 (director 2026-10-28)


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src).strip()


def sentences(t):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\\$(0-9])", t) if p.strip()]


def at_base(wt, base, name, old_dir=None):
    if old_dir:  # a directory holding the base files (for scratch copies that are not git trees)
        return (Path(old_dir) / name).read_text()
    return subprocess.run(["git", "-C", str(wt), "show", f"{base}:docs/analysis-note/{name}"],
                          capture_output=True, text=True, check=True).stdout


def load(wt, base, old_dir=None):
    D = wt / "docs/analysis-note"
    cur = {k: (D / f).read_text() for k, f in FILES.items()}
    old = {k: at_base(wt, base, f, old_dir) for k, f in FILES.items()}
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


# The allowance's pairs, pinned (review of 589f0780, N5): apply_c1a.py is an editable file, so an edit made both there
# and in the protected text must still fail. A change to E1 or E2 needs a new pin here, in its own reviewed commit.
# d2's pairs (DECISION-20261028-joseph-final-draft-d items 1 and 2; ledger row D2-ALLOW): the title T1 and the paper
# abstract's candidate PB, pinned in the same way.
D2_PINS = {'T1': '847ba20823b31aab', 'ABS-P': 'c11de3a217a57d89'}
C1A_PINS = {'E1': 'c6225437b5d563e4', 'E2': 'c04012037a270aa9'}


def c1a_expected(text, edits, keys):
    """The base text with step (c)'s declared 1A edits applied (fived16/c1a/apply_c1a.py, imported, not retyped).

    The director's allowance of 2026-10-28 (ledger row C1A-ALLOW): the 1A sentence may change the protected abstract and
    the Sec. I limitations paragraph, and only by these pairs, so the byte check compares against the edited base and
    the new text stays protected. A base that already holds an edit's new text is left as it is."""
    for k, old, new in edits:
        if k not in keys:
            continue
        if hashlib.sha256((old + "\x00" + new).encode()).hexdigest()[:16] != {**C1A_PINS, **D2_PINS}[k]:
            return None                     # an unpinned pair allows nothing: the span then differs, PROTECTED
        m = list(C1A.pat(old).finditer(text))
        if len(m) == 1:
            text = text[:m[0].start()] + new + text[m[0].end():]
        elif new not in text:
            raise SystemExit(f"check_ledger: the 1A edit {k} matches the base {len(m)} times and is not in it")
    return text


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
    ids = [r[0] for r in rows(ledger_text)]
    for d in sorted({x for x in ids if ids.count(x) > 1}):
        fails.append(f"DUPLICATE row id: {d}")
    for rid, fact, before, disp, after, probe in rows(ledger_text):
        n_rows += 1
        named |= set(re.findall(r"\b[PMJQZFA]\d+\b", before))
        kinds = set()
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(P|MP|N:[\w.]+|R:[\w./-]+)::(.*)$", p)   # R:<repository path>:: a record, not printed text
            if not m:
                fails.append(f"{rid}: malformed probe {p!r}")
                continue
            where, lit = m.group(1), re.sub(r"\s+", " ", m.group(2))
            key = "P" if where == "P" else "M" if where == "MP" else where[2:]
            kinds.add("N" if where.startswith("N:") else "R" if where.startswith("R:") else "P")
            if where.startswith("R:"):
                n_probes += 1
                src = (wt / key).read_text() if (wt / key).is_file() else ""
                if lit not in re.sub(r"\s+", " ", src):
                    fails.append(f"{rid}: NOT FOUND in {key}: {lit[:90]!r}")
                continue
            n_probes += 1
            if lit not in text(key):
                fails.append(f"{rid}: NOT FOUND in {FILES.get(key, key)}: {lit[:90]!r}")
        note_row = disp.startswith(("MOVE→note", "NOTE"))  # NOTE: an r19 note addition or note accuracy fix (N1-N4)
        if note_row and "N" not in kinds:
            fails.append(f"{rid}: note row without a note probe")
        if disp.startswith("GUARD"):
            pm = re.match(r"plant: (.+?) => (.+)$", after)
            lits = [re.sub(r"\s+", " ", re.sub(r"^(P|MP)::", "", q.strip().strip("`"))) for q in probe.split(" && ")]
            if not pm:
                fails.append(f"{rid}: GUARD row without a 'plant: OLD => NEW' in its after column")
            elif not any(pm.group(1) in l for l in lits):
                fails.append(f"{rid}: GUARD plant {pm.group(1)!r} is not in its probe")
        if not note_row and "P" not in kinds and not (disp.startswith("GUARD") and "N" in kinds):  # a note guard (c 1A)
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
    # the title and both abstracts' paper text (Joseph's), and the limitations paragraph whose sentences step (c) owns
    # (review S5): byte-identical to --base
    def tspan(t):
        i, j = t.find("\\title{"), t.find("\\end{abstract}")
        return t[i:j] if i >= 0 and j > i else None
    exp_m = c1a_expected(old["M"], C1A.MAIN_PAPER, {"E2"})
    exp_m = exp_m and c1a_expected(exp_m, D2.TITLE + [D2.ABS_P], {"T1", "ABS-P"})
    if tspan(cur["M"]) is None or exp_m is None or tspan(cur["M"]) != tspan(exp_m):
        fails.append("PROTECTED: main_paper.tex title..end{abstract} differs from base")
    lim = lambda t: [l for l in t.splitlines() if l.startswith("The result has three limitations")]
    exp_p = c1a_expected(old["P"], C1A.PAPER, {"E1"})
    if len(lim(old["P"])) != 1 or exp_p is None or lim(cur["P"]) != lim(exp_p):
        fails.append("PROTECTED: the limitations paragraph of Sec. I differs from base (it is step (c)'s)")
    for k in FILES:
        h_old = [l for l in old[k].splitlines() if "\\pubhold" in l]
        h_cur = [l for l in cur[k].splitlines() if "\\pubhold" in l]
        if h_old != h_cur:
            fails.append(f"PROTECTED: \\pubhold lines of {FILES[k]} differ from base")
    lo = set(re.findall(r"\\label\{([^}]*)\}", old["P"])); ln = set(re.findall(r"\\label\{([^}]*)\}", cur["P"]))
    for lab in sorted(lo - ln - REMOVABLE):
        fails.append(f"LABEL REMOVED: {lab}")
    for lab in sorted(ln - lo - ADDABLE):
        fails.append(f"LABEL ADDED, not approved: {lab}")
    for k in ("J", "Q", "Z", "F", "A"):
        lo = set(re.findall(r"\\label\{([^}]*)\}", old[k])); ln = set(re.findall(r"\\label\{([^}]*)\}", cur[k]))
        for lab in sorted(lo - ln):
            fails.append(f"NOTE LABEL REMOVED ({FILES[k]}): {lab}")
        for lab in sorted(ln - lo - NOTE_ADDABLE):
            fails.append(f"NOTE LABEL ADDED, not approved ({FILES[k]}): {lab}")
    return fails, n_rows, n_probes, len(ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="9df8f748")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("ledger.md")))
    ap.add_argument("--old-dir", help="read the base files from this directory instead of git show BASE:")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve()
    cur, old = load(wt, a.base, a.old_dir)
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
        # (a2) a record probe (R:, step (c) 1A) whose text the record does not hold must fail
        bad = ledger_text + "\n| X3 | planted | — | KEEP | — | `P::Each OmniFold iteration consists of two classification steps.` && `R:docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-REPORT.md::the two truths are two independent tests` |\n"
        fa2, *_ = check(wt, cur, old, bad)
        hit = any(x.startswith("X3: NOT FOUND") for x in fa2)
        ok &= hit
        print("planted bad record probe:", "caught" if hit else "MISSED")
        # (b) a MOVE->note row whose note probe does not print must fail
        bad = ledger_text + "\n| X2 | planted | P0 | MOVE→note | sec_joint.tex | `N:sec_joint.tex::this sentence was never printed in the note` |\n"
        fb, *_ = check(wt, cur, old, bad)
        hit = any(x.startswith("X2: NOT FOUND") for x in fb)
        ok &= hit
        print("moved fact missing from the note:", "caught" if hit else "MISSED")
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
        # (e) removing a label outside REMOVABLE must fail; adding an unapproved one must fail
        cur_e = dict(cur, P=cur["P"].replace("\\label{sec:closure}", "", 1))
        fe, *_ = check(wt, cur_e, old, ledger_text)
        hit = any(x == "LABEL REMOVED: sec:closure" for x in fe)
        ok &= hit
        print("removed label outside the approved set:", "caught" if hit else "MISSED")
        cur_f = dict(cur, P=cur["P"] + "\n\\label{sec:unapproved}\n")
        ff, *_ = check(wt, cur_f, old, ledger_text)
        hit = any(x == "LABEL ADDED, not approved: sec:unapproved" for x in ff)
        ok &= hit
        print("unapproved new label:", "caught" if hit else "MISSED")
        for name, cg in [("an edit to the abstract", dict(cur, M=cur["M"].replace("\\begin{abstract}", "\\begin{abstract}\nAn edit.", 1))),
                         ("an edit to the limitations paragraph", dict(cur, P=cur["P"].replace("The result has three limitations", "The result has two limitations", 1))),
                         ("an undeclared edit to the 1A sentence of the limitations paragraph",
                          dict(cur, P=cur["P"].replace("finds the estimator's bias below", "finds the estimator's bias well below", 1))),
                         ("an undeclared edit to the abstract (d2: its fake-data sentence)",
                          dict(cur, M=cur["M"].replace("does not cover the estimator's bias at GiBUU-like truths",
                                                       "does not cover the estimator's bias at most GiBUU-like truths", 1))),
                         ("an undeclared edit to the title",
                          dict(cur, M=cur["M"].replace("in five observables from MINERvA open data}", "in five observables from all MINERvA data}", 1)))]:
            assert cg != cur, f"the plant for {name} did not apply"
            fg, *_ = check(wt, cg, old, ledger_text)
            hit = any(x.startswith("PROTECTED") for x in fg)
            ok &= hit
            print(f"{name}:", "caught" if hit else "MISSED")
        # (h) the allowance's pair edited together with the paper (review N5): the pin must refuse it
        k0, o0, n0 = next(e for e in C1A.PAPER if e[0] == "E1")
        w0, w1 = "finds the estimator's bias below", "finds the estimator's bias well below"
        n1 = n0.replace(w0, w1, 1)
        cur_h = dict(cur, P=cur["P"].replace(w0, w1, 1))
        assert n1 != n0 and cur_h["P"] != cur["P"], "the allowance plant did not apply"
        keep = list(C1A.PAPER)
        C1A.PAPER[:] = [(k, o, n1 if k == "E1" else n) for k, o, n in keep]
        try:
            fh, *_ = check(wt, cur_h, old, ledger_text)
        finally:
            C1A.PAPER[:] = keep
        hit = any(x.startswith("PROTECTED: the limitations paragraph") for x in fh)
        ok &= hit
        print("allowance pair edited with the paper:", "caught" if hit else "MISSED")
        first = next(rows(ledger_text))[0]          # duplicate the ledger's own first row id, whatever the ledger
        fdup, *_ = check(wt, cur, old, ledger_text + "\n| %s | duplicate | — | KEEP | — | `P::Each OmniFold iteration consists of two classification steps.` |\n" % first)
        hit = any(x == f"DUPLICATE row id: {first}" for x in fdup)
        ok &= hit
        print("duplicate row id:", "caught" if hit else "MISSED")
        # (g) every GUARD row's planted strengthening must make that row fail
        n_g = 0
        for rid, fact, before, disp, after, probe in rows(ledger_text):
            if not disp.startswith("GUARD"):
                continue
            pm = re.match(r"plant: (.+?) => (.+)$", after)
            q = probe.split(" && ")[0].strip().strip("`")
            nm = re.match(r"N:([\w.]+)::", q)          # a note guard (step (c) 1A): plant in the note file
            key = nm.group(1) if nm else "M" if q.startswith("MP::") else "P"
            lit = re.sub(r"^(P|MP|N:[\w.]+)::", "", q)
            src = (wt / "docs/analysis-note" / key).read_text() if nm else cur[key]
            # plant in the source: the probe's first word run containing OLD, whitespace-tolerant
            rx = re.compile(r"\s+".join(re.escape(w) for w in lit.split()))
            m = rx.search(src)
            if not pm or not m:
                ok = False; print(f"guard {rid}: could not plant"); continue
            planted = src[:m.start()] + m.group(0).replace(pm.group(1), pm.group(2), 1) + src[m.end():]
            if nm:
                fg, *_ = check(wt, cur, old, ledger_text, note_override={key: planted})
            else:
                fg, *_ = check(wt, dict(cur, **{key: planted}), old, ledger_text)
            hit = any(x.startswith(f"{rid}: NOT FOUND") for x in fg)
            ok &= hit; n_g += 1
            if not hit:
                print(f"guard {rid}: planted {pm.group(1)!r} -> {pm.group(2)!r} MISSED")
        print(f"scope guards: {n_g} planted strengthenings, each caught" if ok else f"scope guards: {n_g} planted")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n_rows, n_probes, n_ch = check(wt, cur, old, ledger_text)
    for f in fails:
        print(f)
    print(f"ledger rows {n_rows}, probes {n_probes}, changed sentences {n_ch}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
