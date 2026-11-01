#!/usr/bin/env python3
"""Check r22 Step 2's note fact ledger against a worktree, and check that no sentence left silently.

note-n4's checker (note-n4/check_ledger.py), adapted for r22 Step 2 (STEP2-PLAN.md §3):
  - base 9d3054f9 (origin/main at the round's start; the posted note's sources are those of d84124c5, the Step 1 base);
  - the batch is every file the posted note prints from, apart from main_note.tex itself;
  - main_note.tex may differ from its base only by the declared abstract pairs (ABSTRACT, #524: sol2's B01-s-04 and
    B01-s-10), each pinned below by sha256 once the director passes it to Joseph; an unpinned pair allows nothing;
  - a new probe kind, L:, for a cut whose home is the internal ledger outside the records document (#521);
  - note-n4's frozen sentences: the director lifted the n4 freeze on 2026-10-30 (its condition, "until Joseph decides on
    the inventory of his requirements and protections", was met by #465, #521, #522 and #524), so Step 2 runs with
    --no-n4-frozen; the check stays available for a round that needs it.

usage: check_ledger.py <worktree> [--base SHA] [--ledger PATH] [--files f1,f2,...] [--no-n4-frozen]
       check_ledger.py <worktree> --list [--base SHA]      # changed base sentences, with their ids
       check_ledger.py <worktree> --self-test [--base SHA]  # planted defects must each be caught

Ledger rows: | id | fact | before | disposition | after | probe |. Probes, several joined by ` && `:
  N:<file>::text   prints in docs/analysis-note/<file> (comment-stripped, whitespace-collapsed source)
  X:<file>::text   no longer prints there
  P::text          prints in paper_body.tex
  R:<file>::text   prints in the records file docs/analysis-note/<file> (one of RECORDS)
  L:<path>::text   prints in the repository file <path> (whitespace-collapsed), which is not a .tex source of the
                   note or the paper: a ledger home under #521
Checks:
  1. every probe holds;
  2. every printed base sentence of the batch files that no longer prints verbatim is named in some row's "before"
     column, by its id (file prefix + index, as --list prints);
  3. every \\label of the base batch files still exists in the same file;
  4. PROTECTED files are byte-identical to the base; main_note.tex equals its base with the pinned ABSTRACT pairs
     applied;
  5. the check-bound SEC4 phrases still print once in sec_validation.tex;
  6. note-n4's frozen sentences keep their per-file print counts (unless --no-n4-frozen).
Exit 1 on any failure."""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

PREFIX = {"sec_execsummary.tex": "ES", "sec_intro.tex": "IN", "sec_experiment.tex": "EX",
          "selection_features.tex": "SF", "sec_method.tex": "ME", "sec_systematics.tex": "SY",
          "sec_validation.tex": "VA", "sec_results.tex": "RE", "sec_3d.tex": "TD", "scalar_kinematics.tex": "SK",
          "sec_eavailw.tex": "EW", "sec_5d.tex": "FD", "sec_fived16.tex": "FV", "sec_joint.tex": "JT",
          "sec_fps.tex": "FP", "sec_summary.tex": "SU", "app_guide.tex": "AG", "app_statmethods.tex": "AA",
          "app_statmethods_nd.tex": "AB", "app_negweight.tex": "AC", "app_response_mismatch.tex": "AD",
          "app_landscape.tex": "AE", "app_pet_pointer.tex": "AF", "app_release.tex": "RL", "app_codebase.tex": "AH"}
RECORDS = {"app_provenance.tex", "app_history.tex", "app_release_records.tex", "app_codebase_records.tex",
           "main_records.tex", "records_estimators.tex", "records_results_index.tex"}
PROTECTED = ["values.tex", "values_inference.tex", "values_fived16.tex", "app_history.tex", "main_paper.tex",
             "paper_body.tex"]
PAIRED = "main_note.tex"
# labels a round removes by decision, per batch file (a round's wrapper sets it): check 3 allows each, and fails if it is
# still defined in that file or still referenced (\ref, \ref*, \eqref, ...) by any source
REMOVED_LABELS = {}
# (id, old, new) of the abstract pairs; ABSTRACT_PINS[id] = sha256(old + "\0" + new)[:16], set when the director
# passes the pinned pair to Joseph (#524 item 1). Empty until then: main_note.tex must stay byte-identical.
# Approved by Joseph exactly as pinned: DECISION-20261030-joseph-note-abstract-pairs.md (#536).
ABSTRACT = [
    ('B01-s-04',
     'We report a simultaneous measurement of the $\\nu_{\\mu}$ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is \\fvval{sigmed-C_total_resp}\\%.',
     'We report a simultaneous measurement of the $\\nu_{\\mu}$ charged-current inclusive cross section in five observables: the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass. The cross section is unfolded without binning with OmniFold from MINERvA medium-energy open data. It is reported in sixteen cells, with a covariance whose median per-cell uncertainty is \\fvval{sigmed-C_total_resp}\\%.'),
    ('B01-s-10',
     'Three external generator predictions compared on all sixteen cells give $\\chi^{2}$ between \\fvval{g-ext-chi2int-min16} and \\fvval{g-ext-chi2int-max16} for 16 degrees of freedom, and GiBUU, on its 8 cells, \\fvval{g-gibuu-total-chi2int}.',
     'Three external generator predictions, compared on all sixteen cells, give $\\chi^{2}$ between \\fvval{g-ext-chi2int-min16} and \\fvval{g-ext-chi2int-max16} for 16 degrees of freedom. GiBUU, compared only on the 8 cells its sample covers, gives $\\chi^{2}=\\fvval{g-gibuu-total-chi2int}$ on those cells.'),
]
ABSTRACT_PINS = {'B01-s-04': 'd2075a04421dcc5e', 'B01-s-10': '2b0420a3ab1e1432'}
SEC4 = [r"lies entirely below its window \(Gaussian 0\.954\)",
        r"removes the tail undercoverage: \$C_2=0\.977\$ \$\[0\.974,0\.980\]\$ and \$C_1=0\.781\$"]
# note-n4/check_ledger.py's FROZEN list (n4 outline sec. 4), printed (comment-stripped, whitespace-collapsed) source.
N4_FROZEN = [
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
IDRX = re.compile(r"\b(" + "|".join(sorted(PREFIX.values(), key=len, reverse=True)) + r")\d+\b")
SOURCES = re.compile(r"^docs/analysis-note/[^/]+\.tex$")


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src).strip()


def sentences(t):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\\$(0-9])", t) if p.strip()]


def git_show(wt, rev, path):
    r = subprocess.run(["git", "-C", str(wt), "show", f"{rev}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def table_lines(text):
    return [x for x in text.splitlines() if x.startswith("| ") and not x.startswith("| id ") and not x.startswith("|---")]


def rows(text):
    for line in table_lines(text):
        c = [x.strip() for x in line.strip().strip("|").split(" | ")]
        if len(c) == 6:
            yield c


def pin(old, new):
    return hashlib.sha256((old + "\x00" + new).encode()).hexdigest()[:16]


def paired_expected(base_text, pairs, pins):
    """main_note.tex's base with the pinned pairs applied; None if a pair is unpinned or does not match once."""
    t = base_text
    for pid, old, new in pairs:
        if pins.get(pid) != pin(old, new) or t.count(old) != 1:
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


def frozen_fails(all_cur, all_old, frozen):
    fails = []
    names = sorted(set(all_cur) | set(all_old))
    for lit in frozen:
        for f in names:
            c, o = printed(all_cur.get(f, "")).count(lit), printed(all_old.get(f, "")).count(lit)
            if c != o:
                fails.append(f"FROZEN (n4) sentence prints {c}x in {f}, expected {o}x: {lit[:80]!r}")
    return fails


def refs_to(lab, texts):
    rx = re.compile(r"\\\w*ref\*?\{" + re.escape(lab) + r"\}")
    return sorted(f for f, t in texts.items() if t and rx.search(t))


def check(wt, cur, old, files, ledger_text, prot_cur, prot_old, all_cur, all_old, frozen, pairs=None, pins=None,
          removed=None):
    pairs = ABSTRACT if pairs is None else pairs
    pins = ABSTRACT_PINS if pins is None else pins
    removed = REMOVED_LABELS if removed is None else removed
    fails, named, n_rows, n_probes = [], set(), 0, 0
    D = wt / "docs/analysis-note"
    cache = {}

    def txt(f):
        if f not in cache:
            cache[f] = printed(cur[f]) if f in cur else printed((D / f).read_text()) if (D / f).exists() else ""
        return cache[f]

    for rid, fact, before, disp, after, probe in rows(ledger_text):
        n_rows += 1
        named |= {m.group(0) for m in IDRX.finditer(before)}
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(N|X|R):([\w.]+)::(.*)$|P::(.*)$|L:([\w./-]+)::(.*)$", p)
            if not m:
                fails.append(f"{rid}: malformed probe {p!r}")
                continue
            n_probes += 1
            if m.group(4) is not None:
                if re.sub(r"\s+", " ", m.group(4)) not in txt("paper_body.tex"):
                    fails.append(f"{rid}: NOT FOUND in paper_body.tex: {m.group(4)[:80]!r}")
                continue
            if m.group(5) is not None:
                path, lit = m.group(5), re.sub(r"\s+", " ", m.group(6))
                if SOURCES.match(path) and Path(path).name not in RECORDS:
                    fails.append(f"{rid}: L: probe names a note or paper source, {path}")
                elif lit not in re.sub(r"\s+", " ", git_show(wt, "HEAD", path)):
                    fails.append(f"{rid}: NOT IN THE LEDGER ({path} at HEAD): {lit[:90]!r}")
                continue
            kind, f, lit = m.group(1), m.group(2), re.sub(r"\s+", " ", m.group(3))
            present = lit in txt(f)
            if kind == "N" and not present:
                fails.append(f"{rid}: NOT FOUND in {f}: {lit[:90]!r}")
            if kind == "X" and present:
                fails.append(f"{rid}: STILL PRINTS in {f}: {lit[:90]!r}")
            if kind == "R" and f not in RECORDS:
                fails.append(f"{rid}: R: probe names {f}, not a records file")
            elif kind == "R" and not present:
                fails.append(f"{rid}: NOT IN THE RECORDS ({f}): {lit[:90]!r}")
    # a row whose cells hold " | " (a quoted markdown table, say) does not split into six and would be skipped silently
    for line in table_lines(ledger_text):
        if len([x for x in line.strip().strip("|").split(" | ")]) != 6:
            fails.append(f"MALFORMED ROW (not six columns; a probe holding ' | '?): {line[:90]!r}")
    ch = changed(cur, old, files)
    for sid, f, s in ch:
        if sid not in named:
            fails.append(f"UNCOVERED {sid} ({f}): {s[:100]!r}")
    for f in files:
        lo = set(re.findall(r"\\label\{([^}]*)\}", old[f]))
        ln = set(re.findall(r"\\label\{([^}]*)\}", cur[f]))
        gone = removed.get(f, set())
        for lab in sorted(lo - ln - gone):
            fails.append(f"LABEL REMOVED {f}: {lab}")
        for lab in sorted(gone & ln):
            fails.append(f"LABEL DECLARED REMOVED but still defined in {f}: {lab}")
    for f, labs in removed.items():
        for lab in sorted(labs):
            for g in refs_to(lab, all_cur):
                fails.append(f"LABEL DECLARED REMOVED from {f} but still referenced in {g}: {lab}")
    for f in PROTECTED:
        if prot_cur.get(f) != prot_old.get(f):
            fails.append(f"PROTECTED changed: {f}")
    exp = paired_expected(prot_old[PAIRED], pairs, pins)
    if exp is None:
        fails.append(f"{PAIRED}: an abstract pair is unpinned or does not match the base once")
    elif prot_cur[PAIRED] != exp:
        fails.append(f"{PAIRED} differs from its base by more than the pinned abstract pairs")
    if "sec_validation.tex" in cur:  # a writer's own batch may leave it out
        v = printed(cur["sec_validation.tex"])
        for rx in SEC4:
            if len(re.findall(rx, v)) != 1:
                fails.append(f"SEC4 site not found once in sec_validation.tex: {rx}")
    fails += frozen_fails(all_cur, all_old, frozen)
    return fails, n_rows, n_probes, len(ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree")
    ap.add_argument("--base", default="9d3054f9")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("ledger.md")))
    ap.add_argument("--files", default=",".join(PREFIX))
    ap.add_argument("--no-n4-frozen", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    wt = Path(a.worktree).resolve()
    D = wt / "docs/analysis-note"
    files = [f for f in a.files.split(",") if f]
    rd = lambda f: (D / f).read_text() if (D / f).exists() else ""  # noqa: E731
    base = lambda f: git_show(wt, a.base, f"docs/analysis-note/{f}")  # noqa: E731
    cur = {f: rd(f) for f in files}
    old = {f: base(f) for f in files}
    names = sorted({p.name for p in D.glob("*.tex")})
    all_cur = {f: rd(f) for f in names}
    all_old = {f: base(f) for f in names}
    prot_cur = {f: rd(f) for f in PROTECTED + [PAIRED]}
    prot_old = {f: base(f) for f in PROTECTED + [PAIRED]}
    frozen = [] if a.no_n4_frozen else N4_FROZEN
    if a.list:
        for sid, f, s in changed(cur, old, files):
            print(f"{sid}\t{f}\t{s}")
        return 0
    lt = Path(a.ledger).read_text() if Path(a.ledger).exists() else ""
    if a.self_test:
        ok = True
        f0 = "sec_5d.tex"
        s0 = next(s for s in sentences(printed(old[f0])) if len(s) > 40 and s in printed(cur[f0]))
        # the plants' anchor is the base abstract's first four words, so it exists in any round's base (main's abstract
        # began "We report" until #619 and "We present" after it)
        ab_line = next(x for x in prot_old[PAIRED].split("\\begin{abstract}", 1)[1].split("\n")
                       if x.strip() and not x.lstrip().startswith("%"))
        ab_old = " ".join(ab_line.split()[:4])
        ab_new = ab_old + " @@"
        fake = [("T-AB", ab_old, ab_new)]
        # a batch label that no source references, and its file, for the removed-label plants
        lf, lab0 = next((f, x) for f in sorted(cur) for x in re.findall(r"\\label\{([^}]*)\}", cur[f])
                        if not refs_to(x, all_cur))
        es = "sec_execsummary.tex"
        # the undeclared edit plants text at the abstract's end, which no pair declares, so it changes its input once a
        # pinned pair has replaced ab_old (5B-a replaced it, and the old plant's replace then left the file unchanged)
        ab_edit = prot_cur[PAIRED].replace("\\end{abstract}", "@@\n\\end{abstract}", 1)
        # the frozen-sentence plant edits a frozen sentence that still prints (a round may legitimately reword the
        # first one, as r22 Step 3's B01-g-02 did), so the plant always changes its input
        fz_file, fz = next((f, x) for x in N4_FROZEN for f in sorted(all_cur)
                           if all_cur[f] and x.endswith(".") and x in printed(all_cur[f]) and x in all_cur[f])
        planted = [
            ("missing N: probe", dict(cur), lt + "\n| T1 | t | — | KEEP | — | `N:%s::@@NO SUCH TEXT@@` |\n" % f0, {}),
            ("dropped sentence", {**cur, f0: cur[f0].replace(s0.split()[0] + " " + s0.split()[1], "@@", 1)}, lt, {}),
            ("removed label", {**cur, f0: re.sub(r"\\label\{[^}]*\}", "", cur[f0], count=1)}, lt, {}),
            ("false R: probe", dict(cur), lt + "\n| T2 | t | — | CUT | — | `R:app_provenance.tex::@@NOT THERE@@` |\n", {}),
            ("R: probe naming a note file", dict(cur), lt + "\n| T3 | t | — | CUT | — | `R:%s::the` |\n" % f0, {}),
            ("false L: probe", dict(cur), lt + "\n| T4 | t | — | CUT | — | `L:KNOWN_ISSUES.md::@@NOT THERE@@` |\n", {}),
            ("L: probe naming a note source", dict(cur), lt + "\n| T5 | t | — | CUT | — | `L:docs/analysis-note/%s::the` |\n" % f0, {}),
            ("undeclared abstract edit", dict(cur), lt, {"prot": {PAIRED: ab_edit}}),
            ("declared but unpinned abstract pair", dict(cur), lt,
             {"prot": {PAIRED: prot_old[PAIRED].replace(ab_old, ab_new, 1)}, "pairs": fake, "pins": {}}),
            ("protected values file edited", dict(cur), lt, {"prot": {"values.tex": prot_cur["values.tex"] + "%x\n"}}),
            ("SEC4 phrase reworded", {**cur, "sec_validation.tex": cur["sec_validation.tex"].replace(
                "lies entirely below its window", "lies below its window", 1)}, lt, {}),
            ("n4 frozen sentence edited", dict(cur), lt, {"all": {fz_file: all_cur[fz_file].replace(fz, fz[:-1] + " @@.", 1)}}),
            ("ledger row holding ' | '", dict(cur), lt + "\n| T7 | t | — | CUT | — | `L:KNOWN_ISSUES.md::a | b` |\n", {}),
            ("declared removed label still referenced", {**cur, lf: cur[lf].replace("\\label{%s}" % lab0, "", 1)}, lt,
             {"removed": {**REMOVED_LABELS, lf: {lab0}},
              "all": {lf: all_cur[lf].replace("\\label{%s}" % lab0, "", 1) + "\n\\ref{%s}\n" % lab0}}),
        ]
        silent = [("declared removed label, unreferenced", {"cur": {lf: cur[lf].replace("\\label{%s}" % lab0, "", 1)},
                                                          "removed": {**REMOVED_LABELS, lf: {lab0}},
                                                          "all": {lf: all_cur[lf].replace("\\label{%s}" % lab0, "", 1)},
                                                          # dropping a \label also changes its sentence, which check 2
                                                          # rightly reports; this control reads check 3's failures only
                                                          "only": "LABEL"}),
                  ("pinned abstract pair", {"prot": {PAIRED: prot_old[PAIRED].replace(ab_old, ab_new, 1)},
                                            "pairs": fake, "pins": {"T-AB": pin(ab_old, ab_new)}}),
                  ("true L: probe", {"ledger": lt + "\n| T6 | t | — | CUT | — | `L:2d-unfolding/2D_OMNIFOLD_REFERENCE.md::isMinosMatchTrack` |\n"})]
        assert prot_old[PAIRED].count(ab_old) == 1, "self-test abstract anchor not unique"
        assert ab_edit != prot_cur[PAIRED], "self-test undeclared abstract edit does not change its input"
        # the plants run with N4_FROZEN (one of them edits a frozen sentence), so the baseline must too, whatever
        # --no-n4-frozen says; otherwise a round that legitimately rewords a frozen sentence makes the silent controls fire
        base_fails = check(wt, cur, old, files, lt, prot_cur, prot_old, all_cur, all_old, N4_FROZEN)[0]

        def run(c, l, o):
            pc = {**prot_cur, **o.get("prot", {})}
            ac = {**all_cur, **o.get("all", {})}
            return check(wt, {**c, **o.get("cur", {})}, old, files, l, pc, prot_old, ac, all_old, N4_FROZEN,
                         o.get("pairs"), o.get("pins"), o.get("removed"))[0]
        for name, c, l, o in planted:
            caught = len(run(c, l, o)) > len(base_fails)
            ok &= caught
            print(f"  {name}: {'caught' if caught else 'NOT CAUGHT'}")
        for name, o in silent:
            keep = [x for x in base_fails if o.get("only", "") in x]
            quiet = [x for x in run(cur, o.get("ledger", lt), o) if o.get("only", "") in x] == keep
            ok &= quiet
            print(f"  {name}: {'silent' if quiet else 'FIRED (should be silent)'}")
        print("SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails, n, p, c = check(wt, cur, old, files, lt, prot_cur, prot_old, all_cur, all_old, frozen)
    for f in fails:
        print("  FAIL", f)
    print(f"ledger rows {n}, probes {p}, changed base sentences {c}, failures {len(fails)}"
          + ("" if frozen else " (n4 frozen sentences not checked)"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
