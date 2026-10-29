#!/usr/bin/env python3
"""Check the note round n4 fact ledger against a worktree, and check that no sentence left silently.

n3's checker (note-n3/check_ledger.py), extended for n4 (director's rulings on note-n4/outline.md, 2026-10-28):
  - base 371cccec; the batch files add sec_pet_campaigns.tex, primer_body.tex and app_release.tex;
  - app_release.tex is released (DECISION-20261028-joseph-protections-n4-release-retrospective.md item 3): it may
    differ from the protected base only by the declared pairs of apply_n4.REL, each pinned below by sha256;
  - the frozen sentences (outline sec. 4) print exactly as often, in exactly the same files, as at the base, except
    the one declared verbatim move (the readiness sentence, from the status table to the executive summary);
  - a batch file may be deleted (the status table): its base sentences must then be covered like any other.

usage: check_ledger.py <worktree> [--base SHA] [--ledger PATH] [--files f1,f2,...]
       check_ledger.py <worktree> --list [--base SHA]      # changed base sentences, with their ids
       check_ledger.py <worktree> --self-test [--base SHA]  # planted defects must each be caught

Ledger rows: | id | fact | before | disposition | after | probe |. Probes, several joined by ` && `:
  N:<file>::text   prints in docs/analysis-note/<file> (comment-stripped, whitespace-collapsed source)
  X:<file>::text   no longer prints there
  P::text          prints in paper_body.tex
  R:<file>::text   prints in the records file docs/analysis-note/<file> (one of RECORDS)
Checks:
  1. every probe holds;
  2. every printed base sentence of the batch files that no longer prints verbatim is named in some row's "before"
     column, by its id (file prefix + index, as --list prints);
  3. every \\label of the base batch files still exists in the same file;
  4. PROTECTED files are byte-identical to the protected base (the merge base of HEAD and origin/main, as in n3);
     app_release.tex equals the protected base with the pinned REL pairs applied;
  5. the check-bound SEC4 phrases still print once in sec_validation.tex;
  6. the frozen sentences (FROZEN) keep their per-file print counts, apart from the MOVES.
Exit 1 on any failure."""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_n4  # noqa: E402

PREFIX = {"sec_execsummary.tex": "ES", "sec_intro.tex": "IN", "sec_summary.tex": "SU", "sec_method.tex": "ME",
          "sec_systematics.tex": "SY", "sec_validation.tex": "VA", "sec_3d.tex": "TD", "sec_eavailw.tex": "EW",
          "sec_5d.tex": "FD", "sec_joint.tex": "JT", "sec_fps.tex": "FP", "app_statmethods.tex": "AA",
          "app_statmethods_nd.tex": "AB", "app_negweight.tex": "AC", "app_response_mismatch.tex": "AD",
          "result_status_rows.tex": "RS", "sec_pet_campaigns.tex": "PC", "primer_body.tex": "PR",
          "app_release.tex": "RL"}
RECORDS = {"app_provenance.tex", "app_history.tex", "app_release_records.tex", "app_codebase_records.tex",
           "main_records.tex"}
PROTECTED = ["values.tex", "values_inference.tex", "app_history.tex", "main_note.tex", "main_paper.tex",
             "paper_body.tex"]
RELEASED = "app_release.tex"
REL_PINS = {}     # id -> sha256(old + "\0" + new)[:16]; filled when the director rules on the release claim table
SEC4 = [r"lies entirely below its window \(Gaussian 0\.954\)",
        r"removes the tail undercoverage: \$C_2=0\.977\$ \$\[0\.974,0\.980\]\$ and \$C_1=0\.781\$"]
# Outline sec. 4, approved 2026-10-28 (ruling 2): left byte-identical wherever they print until Joseph decides on
# the inventory of his requirements and protections. Printed (comment-stripped, whitespace-collapsed) source text.
FROZEN = [
    r"The pseudo-experiments lost to time limits have been rerun, for reporting only, so every submitted draw has been observed.",
    r"No recovered draw changes a decision (\S\ref{sec:joint5d-lost}).",
    r"The quoted 2D statistical block has had no coverage test; the fixed-truth coverage studies scored two earlier "
    r"statistical bands, of which the first-built undercovers in its tails ($C_2=\covTwoDCTwo$, vs.\ $0.954$; "
    r"\S\ref{sec:uq-boot}, \S\ref{sec:coverage}).",
    r"The quoted two-dimensional statistical block has had no coverage test (\S\ref{sec:uq-boot}, \S\ref{sec:coverage}).",
    r"no release has been tagged or deposited",
    r"has not been deposited or released under a publication tag",
    r"Whether it is ready for publication as a measurement has not been established.",
]
# Ruling 2: the readiness sentence may move verbatim from the status table into the ES's 2D paragraph.
MOVES = {FROZEN[6]: ("result_status_rows.tex", "sec_execsummary.tex")}
IDRX = re.compile(r"\b(" + "|".join(sorted(PREFIX.values(), key=len, reverse=True)) + r")\d+\b")


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src).strip()


def sentences(t):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\\$(0-9])", t) if p.strip()]


def git_show(wt, rev, name):
    r = subprocess.run(["git", "-C", str(wt), "show", f"{rev}:docs/analysis-note/{name}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def tex_names(wt, rev):
    r = subprocess.run(["git", "-C", str(wt), "ls-tree", "--name-only", f"{rev}:docs/analysis-note"],
                       capture_output=True, text=True, check=True)
    return [n for n in r.stdout.split() if n.endswith(".tex")]


def rows(text):
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("| id ") and not line.startswith("|---"):
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            if len(c) == 6:
                yield c


def pin(old, new):
    return hashlib.sha256((old + "\x00" + new).encode()).hexdigest()[:16]


def release_expected(base_text, rel, pins):
    """The protected base of app_release.tex with the pinned pairs applied; None if a pair is unpinned or misses."""
    t = base_text
    for eid, _f, old, new in rel:
        if pins.get(eid) != pin(old, new) or t.count(old) != 1:
            return None
        t = t.replace(old, new)
    return t


def changed(cur, old, files):
    out = []
    for f in files:
        a = printed(cur[f])
        for i, s in enumerate(sentences(printed(old[f]))):
            if s not in a:
                out.append((f"{PREFIX[f]}{i}", f, s))
    return out


def frozen_fails(all_cur, all_old):
    fails = []
    for lit in FROZEN:
        names = sorted(set(all_cur) | set(all_old))
        c = {f: printed(all_cur.get(f, "")).count(lit) for f in names}
        o = {f: printed(all_old.get(f, "")).count(lit) for f in names}
        if lit in MOVES:
            src, dst = MOVES[lit]
            moved = dict(o)
            if c.get(src, 0) == 0 and o.get(src, 0) == 1:
                moved[src], moved[dst] = 0, o.get(dst, 0) + 1
            o = moved
        for f in names:
            if c[f] != o[f]:
                fails.append(f"FROZEN sentence prints {c[f]}x in {f}, expected {o[f]}x: {lit[:80]!r}")
    return fails


def check(wt, cur, old, files, ledger_text, prot_cur, prot_old, all_cur, all_old, rel=None, pins=None):
    rel = apply_n4.REL if rel is None else rel
    pins = REL_PINS if pins is None else pins
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
                ok = re.sub(r"\s+", " ", m.group(4)) in txt("paper_body.tex")
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
    exp = release_expected(prot_old[RELEASED], rel, pins)
    if exp is None:
        fails.append(f"RELEASED {RELEASED}: an allowance pair is unpinned or does not match the base once")
    elif prot_cur[RELEASED] != exp:
        fails.append(f"RELEASED {RELEASED} differs from its base by more than the pinned pairs")
    if "sec_validation.tex" in cur:
        v = printed(cur["sec_validation.tex"])
        for rx in SEC4:
            if len(re.findall(rx, v)) != 1:
                fails.append(f"SEC4 site not found once in sec_validation.tex: {rx}")
    fails += frozen_fails(all_cur, all_old)
    return fails, n_rows, n_probes, len(ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="371cccec")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("ledger.md")))
    ap.add_argument("--protected-base", help="default: the merge base of HEAD and origin/main, as in n3")
    ap.add_argument("--files", default=",".join(PREFIX))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve(); D = wt / "docs/analysis-note"
    files = [f for f in a.files.split(",") if f]
    rd = lambda f: (D / f).read_text() if (D / f).exists() else ""   # a deleted batch file reads as empty
    cur = {f: rd(f) for f in files}
    old = {f: git_show(wt, a.base, f) for f in files}
    names = sorted(set(tex_names(wt, a.base)) | {p.name for p in D.glob("*.tex")})
    all_cur = {f: rd(f) for f in names}
    all_old = {f: git_show(wt, a.base, f) for f in names}
    pbase = a.protected_base
    if not pbase:
        mb = subprocess.run(["git", "-C", str(wt), "merge-base", "HEAD", "origin/main"], capture_output=True, text=True)
        pbase = mb.stdout.strip() if mb.returncode == 0 and mb.stdout.strip() else a.base
    prot_cur = {f: rd(f) for f in PROTECTED + [RELEASED]}
    prot_old = {f: git_show(wt, pbase, f) for f in PROTECTED + [RELEASED]}
    if a.list:
        for sid, f, s in changed(cur, old, files):
            print(f"{sid}\t{f}\t{s}")
        return 0
    lt = Path(a.ledger).read_text() if Path(a.ledger).exists() else ""
    args = (prot_cur, prot_old, all_cur, all_old)
    if a.self_test:
        ok = True
        f0 = "sec_5d.tex"
        s0 = next(s for s in sentences(printed(old[f0])) if len(s) > 40 and s in printed(cur[f0]))
        rel_old = "The bin edges are the one thing a reader cannot recover from a checksum:"
        rel_new = rel_old.replace("one thing", "only thing")
        fake = [("T-REL", RELEASED, rel_old, rel_new)]
        es = "sec_execsummary.tex"
        planted = [
            ("missing probe", dict(cur), lt + "\n| T1 | t | — | KEEP | — | `N:%s::@@NO SUCH TEXT@@` |\n" % f0, {}),
            ("dropped sentence", {**cur, f0: cur[f0].replace(s0.split()[0] + " " + s0.split()[1], "@@", 1)}, lt, {}),
            ("removed label", {**cur, f0: re.sub(r"\\label\{[^}]*\}", "", cur[f0], count=1)}, lt, {}),
            ("false R: probe", dict(cur), lt + "\n| T2 | t | — | MOVE | — | `R:app_provenance.tex::@@NOT IN THE RECORDS@@` |\n", {}),
            ("R: probe naming a note file", dict(cur), lt + "\n| T3 | t | — | MOVE | — | `R:%s::the` |\n" % f0, {}),
            ("undeclared app_release edit", dict(cur), lt, {"prot": {RELEASED: prot_cur[RELEASED].replace(rel_old, rel_new)}}),
            ("declared but unpinned app_release pair", dict(cur), lt,
             {"prot": {RELEASED: prot_old[RELEASED].replace(rel_old, rel_new)}, "rel": fake, "pins": {}}),
            ("frozen sentence edited", dict(cur), lt,
             {"all": {es: all_cur[es].replace("has been observed.", "was observed.")}}),
            ("frozen sentence duplicated by the move", dict(cur), lt,
             {"all": {es: all_cur[es] + "\n" + FROZEN[6] + "\n"}}),
        ]
        # The silent direction: a pinned pair is allowed, and the declared verbatim move is allowed.
        silent = [
            ("pinned app_release pair", {"prot": {RELEASED: prot_old[RELEASED].replace(rel_old, rel_new)}, "rel": fake,
                                         "pins": {"T-REL": pin(rel_old, rel_new)}}),
            ("declared verbatim move", {"all": {es: all_cur[es] + "\n" + FROZEN[6] + "\n",
                                                "result_status_rows.tex": all_cur["result_status_rows.tex"].replace(FROZEN[6], "")}}),
        ]
        base_fails, *_ = check(wt, cur, old, files, lt, *args)

        def run(c, l, o):
            pc = {**prot_cur, **o.get("prot", {})}; ac = {**all_cur, **o.get("all", {})}
            return check(wt, c, old, files, l, pc, prot_old, ac, all_old, o.get("rel"), o.get("pins"))[0]
        for name, c, l, o in planted:
            caught = len(run(c, l, o)) > len(base_fails)
            ok &= caught
            print(f"  {name}: {'caught' if caught else 'NOT CAUGHT'}")
        for name, o in silent:
            quiet = run(cur, lt, o) == base_fails
            ok &= quiet
            print(f"  {name}: {'silent' if quiet else 'FIRED (should be silent)'}")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n, p, c = check(wt, cur, old, files, lt, *args)
    for f in fails:
        print("  FAIL", f)
    print(f"ledger rows {n}, probes {p}, changed base sentences {c}, failures {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
