#!/usr/bin/env python3
"""Check r22 Step 2's paper fact ledger against a worktree, and check that no sentence left silently.

The paper round's checker (STEP2-PAPER.md section 3). It is the note round's step2/check_ledger.py with the paper as its
batch, plus r21's paper checks (r21/check_ledger.py: GATE, FROZEN, labels, no new number, protected text):
  - base f47b1b4a (origin/main at the round's start);
  - the batch is paper_body.tex; main_paper.tex may differ from its base only by the declared PAIRS (the abstract and
    Data availability sentences, A4 and A1, #524), each pinned below by sha256 once the director passes it to Joseph;
    an unpinned pair allows nothing;
  - every other .tex and .bib file of docs/analysis-note is byte-identical to the base.

usage: check_paper.py <worktree> [--base SHA] [--ledger PATH]
       check_paper.py <worktree> --list [--base SHA]       # changed base sentences, with their ids
       check_paper.py <worktree> --self-test [--base SHA]  # planted defects must each be caught

Ledger rows: | id | fact | before | disposition | after | probe |. Probes, several joined by ` && `:
  P::text          prints in paper_body.tex (comment-stripped, whitespace-collapsed source)
  XP::text         no longer prints in paper_body.tex
  N:<file>::text   prints in the note source docs/analysis-note/<file> (a #522 move's home)
Checks:
  1. every probe holds;
  2. every printed base sentence of paper_body.tex that no longer prints verbatim is named in some row's "before"
     column, by its id (PB + index, as --list prints);
  3. every \\label of the base paper_body.tex still exists;
  4. every other note-directory .tex/.bib file is byte-identical to the base, apart from the two files that
     tools/registry/results_index.py generates from the registry (GENERATED; its --check proves them fresh, and the
     B4 re-pin changes them); main_paper.tex equals its base with the pinned PAIRS applied;
  5. each of the eight GATE phrases prints exactly once in paper_body.tex, and the FROZEN sentence prints exactly once;
  6. no new number: every numeral token of the new body's printed text, outside macro names, occurs in the base's;
  7. the registered alias "the joint-test estimator" still prints (STEP2-PLAN.md section 7, ruling 4).
The \\pubhold holds are all in main_paper.tex, which check 4 holds byte-identical apart from the pinned pairs, and a
pair may not contain one. Files that git does not track (build products such as main_paperNotes.bib) are ignored.
Exit 1 on any failure."""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

BODY = "paper_body.tex"
PAIRED = "main_paper.tex"
# (id, old, new) of the paper's Joseph pairs; PAIR_PINS[id] = sha256(old + "\0" + new)[:16], set when the director
# passes the pinned pair to Joseph (#524 item 1). Empty until then: main_paper.tex must stay byte-identical.
PAIRS = []
PAIR_PINS = {}
# r21/ledger.md's eight GATE phrases (check_sec4_receipts.py finds them by regex in paper_body.tex), printed source.
GATE = [r"with a median statistical uncertainty of \SI{0.676}{\percent}",
        r"biased by up to \SI{4}{\percent} in simulation",
        r"reduces it to below \SI{0.3}{\percent}",
        r"leaving up to \SI{1}{\percent} in some joint cells",
        r"differ by at most \SI{1.4}{\percent}",
        r"by up to \SI{74}{\percent} at high $W$",
        r"it is \SIrange{16}{31}{\percent} in the most affected",
        r"within the quoted total uncertainty in about half of those cells"]
FROZEN = "Interval coverage has not been validated."
GENERATED = {"records_estimators.tex", "records_results_index.tex"}
ALIAS = "the joint-test estimator"
NUM = re.compile(r"(?<![A-Za-z\\{])\d+(?:[.,]\d+)*")
IDRX = re.compile(r"\bPB\d+\b")


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src).strip()


def sentences(t):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\\$(0-9])", t) if p.strip()]


def pin(old, new):
    return hashlib.sha256((old + "\x00" + new).encode()).hexdigest()[:16]


def git_show(wt, rev, path):
    r = subprocess.run(["git", "-C", str(wt), "show", f"{rev}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def git_ls(wt, rev=None):
    cmd = ["ls-tree", "--name-only", rev, "docs/analysis-note/"] if rev else ["ls-files", "docs/analysis-note/"]
    r = subprocess.run(["git", "-C", str(wt)] + cmd, capture_output=True, text=True)
    return [Path(p).name for p in r.stdout.split() if re.search(r"\.(tex|bib)$", p) and "/" not in p[19:]]


def rows(text):
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| id "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) >= 6:
            yield cells[0], cells[1], cells[2], cells[3], cells[4], cells[-1]


def paired_expected(base_text, pairs, pins):
    t = base_text
    for pid, old, new in pairs:
        if pins.get(pid) != pin(old, new) or t.count(old) != 1 or "\\pubhold" in old + new:
            return None
        t = t.replace(old, new)
    return t


def numbers(t):
    return set(NUM.findall(re.sub(r"\\[A-Za-z]+", " ", t)))


def check(cur, old, ledger_text, prot_cur, prot_old, notes, pairs=None, pins=None):
    pairs = PAIRS if pairs is None else pairs
    pins = PAIR_PINS if pins is None else pins
    fails, named, n_rows, n_probes = [], set(), 0, 0
    body = printed(cur)
    for rid, fact, before, disp, after, probe in rows(ledger_text):
        n_rows += 1
        named |= set(IDRX.findall(before))
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(P|XP)::(.*)$|N:([\w.]+)::(.*)$", p)
            if not m:
                fails.append(f"{rid}: malformed probe {p!r}")
                continue
            n_probes += 1
            if m.group(1):
                lit = re.sub(r"\s+", " ", m.group(2))
                if m.group(1) == "P" and lit not in body:
                    fails.append(f"{rid}: NOT FOUND in {BODY}: {lit[:90]!r}")
                if m.group(1) == "XP" and lit in body:
                    fails.append(f"{rid}: STILL PRINTS in {BODY}: {lit[:90]!r}")
            else:
                f, lit = m.group(3), re.sub(r"\s+", " ", m.group(4))
                if f in (BODY, PAIRED) or f not in notes:
                    fails.append(f"{rid}: N: probe names {f}, not a note source")
                elif lit not in printed(notes[f]):
                    fails.append(f"{rid}: NOT FOUND in the note's {f}: {lit[:90]!r}")
    ch = [(f"PB{i}", s) for i, s in enumerate(sentences(printed(old))) if s not in body]
    for sid, s in ch:
        if sid not in named:
            fails.append(f"UNCOVERED {sid}: {s[:100]!r}")
    for lab in sorted(set(re.findall(r"\\label\{([^}]*)\}", old)) - set(re.findall(r"\\label\{([^}]*)\}", cur))):
        fails.append(f"LABEL REMOVED {BODY}: {lab}")
    for f in sorted(set(prot_old) | set(prot_cur)):
        if f != PAIRED and f not in GENERATED and prot_cur.get(f) != prot_old.get(f):
            fails.append(f"PROTECTED changed: {f}")
    exp = paired_expected(prot_old.get(PAIRED, ""), pairs, pins)
    if exp is None:
        fails.append(f"{PAIRED}: a pair is unpinned or does not match the base once")
    elif prot_cur.get(PAIRED) != exp:
        fails.append(f"{PAIRED} differs from its base by more than the pinned pairs")
    for g in GATE:
        if body.count(g) != 1:
            fails.append(f"GATE phrase prints {body.count(g)}x, expected once: {g}")
    if body.count(FROZEN) != 1:
        fails.append(f"FROZEN sentence prints {body.count(FROZEN)}x, expected once")
    if ALIAS not in body:
        fails.append(f"registered alias no longer prints: {ALIAS!r}")
    new_nums = numbers(body) - numbers(printed(old))
    if new_nums:
        fails.append(f"NEW NUMBER(S) in {BODY}: {sorted(new_nums)}")
    return fails, n_rows, n_probes, len(ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="f47b1b4a")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("ledger.md")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve()
    D = wt / "docs/analysis-note"
    base = lambda f: git_show(wt, a.base, f"docs/analysis-note/{f}")  # noqa: E731
    cur, old = (D / BODY).read_text(), base(BODY)
    at_base, tracked = set(git_ls(wt, a.base)), set(git_ls(wt))
    names = sorted((at_base | tracked) - {BODY})
    prot_cur = {f: (D / f).read_text() if f in tracked and (D / f).exists() else None for f in names}
    prot_old = {f: base(f) if f in at_base else None for f in names}
    notes = {f: t for f, t in prot_cur.items() if t is not None and f.endswith(".tex") and f != PAIRED}
    if a.list:
        body = printed(cur)
        for i, s in enumerate(sentences(printed(old))):
            if s not in body:
                print(f"PB{i}\t{s}")
        return 0
    lt = Path(a.ledger).read_text() if Path(a.ledger).exists() else ""
    if a.self_test:
        ok = True
        s0 = next(s for s in sentences(printed(old)) if len(s) > 60 and s in printed(cur) and FROZEN not in s
                  and not any(g in s for g in GATE) and ALIAS not in s)
        ab_old = "Three external generator predictions compared on all sixteen cells"
        ab_new = "Three external generator predictions, compared on all sixteen cells,"
        fake = [("T-AB", ab_old, ab_new)]
        g0 = GATE[1]
        planted = [
            ("missing P: probe", cur, lt + "\n| T1 | t | PB0 | KEEP | — | `P::@@NO SUCH TEXT@@` |\n", {}),
            ("false N: probe", cur, lt + "\n| T2 | t | PB0 | MOVED | — | `N:sec_5d.tex::@@NOT THERE@@` |\n", {}),
            ("N: probe naming the paper", cur, lt + "\n| T3 | t | PB0 | MOVED | — | `N:paper_body.tex::the` |\n", {}),
            ("XP: probe on printed text", cur, lt + "\n| T4 | t | PB0 | CUT | — | `XP::%s` |\n" % s0[:40], {}),
            ("dropped sentence", cur.replace(s0[:40], "@@", 1), lt, {}),
            ("removed label", re.sub(r"\\label\{[^}]*\}", "", cur, count=1), lt, {}),
            ("GATE phrase reworded", cur.replace(g0, g0.replace("biased by up to", "biased by at most"), 1), lt, {}),
            ("GATE phrase printed twice", cur + "\n" + g0 + "\n", lt, {}),
            ("FROZEN sentence reworded", cur.replace(FROZEN, "Interval coverage is not validated.", 1), lt, {}),
            ("alias renamed", cur.replace(ALIAS, "the five-observable estimator"), lt, {}),
            ("new number", cur.replace(s0[:40], s0[:40] + " 987654", 1), lt, {}),
            ("pair that edits a hold", cur, lt,
             {"prot": {PAIRED: prot_old[PAIRED].replace(r"\pubhold{funding", r"\pubhold{grant", 1)},
              "pairs": [("T-H", r"\pubhold{funding", r"\pubhold{grant")],
              "pins": {"T-H": pin(r"\pubhold{funding", r"\pubhold{grant")}}),
            ("undeclared abstract edit", cur, lt, {"prot": {PAIRED: prot_cur[PAIRED].replace(ab_old, ab_new, 1)}}),
            ("declared but unpinned pair", cur, lt,
             {"prot": {PAIRED: prot_old[PAIRED].replace(ab_old, ab_new, 1)}, "pairs": fake, "pins": {}}),
            ("protected note file edited", cur, lt, {"prot": {"sec_5d.tex": prot_cur["sec_5d.tex"] + "%x\n"}}),
            ("protected values file edited", cur, lt, {"prot": {"values.tex": prot_cur["values.tex"] + "%x\n"}}),
        ]
        silent = [("pinned pair", {"prot": {PAIRED: prot_old[PAIRED].replace(ab_old, ab_new, 1)},
                                   "pairs": fake, "pins": {"T-AB": pin(ab_old, ab_new)}}),
                  ("true N: probe", {"ledger": lt + "\n| T5 | t | PB0 | MOVED | — | `N:sec_intro.tex::OmniFold` |\n"})]
        assert prot_old[PAIRED].count(ab_old) == 1, "self-test abstract anchor not unique"
        assert prot_old[PAIRED].count(r"\pubhold{funding") == 1, "self-test hold anchor not unique"
        base_fails = check(cur, old, lt, prot_cur, prot_old, notes)[0]

        def run(c, l, o):
            return check(c, old, l, {**prot_cur, **o.get("prot", {})}, prot_old, notes, o.get("pairs"),
                         o.get("pins"))[0]
        for name, c, l, o in planted:
            caught = len(run(c, l, o)) > len(base_fails)
            ok &= caught
            print(f"  {name}: {'caught' if caught else 'NOT CAUGHT'}")
        for name, o in silent:
            quiet = run(cur, o.get("ledger", lt), o) == base_fails
            ok &= quiet
            print(f"  {name}: {'silent' if quiet else 'FIRED (should be silent)'}")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n, p, c = check(cur, old, lt, prot_cur, prot_old, notes)
    for f in fails:
        print("  FAIL", f)
    print(f"ledger rows {n}, probes {p}, changed base sentences {c}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
