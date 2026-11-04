#!/usr/bin/env python3
"""Check the referee presentation round against its work order: presentation only, no result changes (REPORT.md).

  1. main_paper.tex equals its base with exactly the item-4 abstract draft applied (ABSTRACT_EDITS) and the one source
     comment before it; nothing else in the file changes;
  2. no number is added to the printed paper: every numeral of the printed paper_body.tex and main_paper.tex (comments
     stripped, \\fvval{...}, \\ref, \\cite and \\label arguments removed) is in the base's printed set, or in NEW_NUMERALS
     with its source;
  3. every \\fvval key the paper prints is defined in values_fived16.tex, and the appendix tables print exactly the note's
     keys: the 16 x 11 per-group keys and the 120 correlation keys;
  4. the claims that replace printed numbers hold in the values: with C_model's shape ratios from CH, and with GENIE's
     hydrogen, GiBUU's total falls below its carbon value (Sec. V B, item 6);
  5. the work order's wording: the phrases each item removes no longer print (GONE), and those it adds print once (ONCE).
usage: check_round.py <worktree> [--base SHA]   (exit 1 on any failure)
       check_round.py <worktree> --self-test    (each planted defect must be caught)"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("round_ledger", HERE / "check_ledger.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
cl = rl.cl
NOTE = "docs/analysis-note"
CELLS = [f"R{i:02d}" for i in range(16)]
GROUPS = ["stat", "flux", "interaction", "detector", "lateral", "normalization", "C_e", "C_model", "C_resp", "C_PL5D",
          "reported"]
# item 4 (a draft for the PRD read and Joseph): the two replacements, each exactly once
ABSTRACT_EDITS = [
    (r"Three external generator predictions give $\chi^{2}$ values of",
     r"As a descriptive comparison, three external generator predictions give $\chi^{2}$ values of"),
    (r"residual bias exceeding predeclared uncertainty-based thresholds",
     r"residual bias exceeding uncertainty-based thresholds fixed in advance"),
]
ABSTRACT_COMMENT = "% Referee round 20261104 (item 4, sonnet minor 2; item 3, minor 1): DRAFT for the PRD read and Joseph"
# numerals the round adds to the printed paper, each with its source
NEW_NUMERALS = {
    "6.243e-8": "sec_method.tex sec:method-xsec (:186); README-gen5d-fluxfix.md :74, 6.243343e-4 m^-2/POT",
    "8.3": "addition 3: sec_5d.tex sec:val-departure :84; d-id/REPORT.md :436 (exact T2 IBU, GiBUU, K = 5)",
    "3.3": "addition 3: sec_5d.tex sec:val-departure :84; d-id/REPORT.md :445 (K = 200, GiBUU)",
    "200": "addition 3: the iteration count of that 3.3 (sec_5d.tex :84; d-id/REPORT.md :442-445)",
}
GONE = [
    ("paper_body.tex", "No hyperparameter search was performed on data."),                       # item 1
    ("paper_body.tex", "the learner was chosen after the LightGBM and exact-split results"),       # item 1
    ("paper_body.tex", "A truth is listed when"),                                                  # item 5
    ("paper_body.tex", "listing criterion"),                                                       # item 5
    ("paper_body.tex", "fake-data listing"),                                                       # item 5
    ("paper_body.tex", "one of its gates"),                                                        # item 3
    ("paper_body.tex", "stopping criterion was fixed in advance"),                                 # item 3
    ("paper_body.tex", "MINERvA Tune~v1 composition below it"),                                    # item 3
    ("paper_body.tex", r"\fvval{g-gibuu-genieh-total-chi2r1}"),                                    # item 6
    ("paper_body.tex", r"\fvval{e2-with-gibuu-total-chr1}"),                                       # item 6
    ("paper_body.tex", r"\fvval{f0b-A7_gibuu-p}"),                                                 # item 6
    ("main_paper.tex", "predeclared"),                                                             # item 3
    ("paper_body.tex", "and ndf is that rank"),                                                    # item 8 (#760)
    ("paper_body.tex", "because it persists over the tested iteration numbers and classifier capacities"),  # addition 3
    ("paper_body.tex", "which we interpret as regularization bias"),                               # addition 3
    ("paper_body.tex", "The simulated detector response is not probed."),                          # addition 2
]
ONCE = [
    ("paper_body.tex", "No learner setting, whether capacity, learning rate, refinement capacity or iteration count, "
                       "was tuned on data."),
    ("paper_body.tex", "this choice was checked on data, against ten iterations with purity-based subtraction and "
                       "against the published result, without a search over the iteration count"),
    ("paper_body.tex", r"LightGBM, rather than the scikit-learn exact-split estimator at the same settings, was chosen "
                       r"after both had been compared with the published result, a choice that lowered "
                       r"$\chi^{2}/\mathrm{ndf}$ from $\chiPaperExact$ to $\chiPaperPurity$"),
    ("paper_body.tex", "and the distance depends on the estimator"),
    ("paper_body.tex", "and ndf is the number of reported bins. The value is descriptive, and no $p$-value is quoted for it."),
    ("paper_body.tex", "Neither panel shows the sixteen-cell result or its reported covariance."),
    ("paper_body.tex", "not the reported covariance (\\nsec{sec:eavailw-adopted})"),
    ("paper_body.tex", r"$^{*}$Closure test: the truth is the simulation's own."),
    ("paper_body.tex", r"\section{Uncertainty tables}"),
    ("paper_body.tex", "run periods (playlists 1A--1G and 1L--1P)"),
    ("paper_body.tex", "the lateral uncertainties shift the reconstructed muon kinematics and beam angle rather than "
                       "reweighting events"),
    ("sec_method.tex", "The change was decided on that closure test, before the rebuilt result's distance from the "
                       "published result was computed"),
    ("paper_body.tex", "The residual is therefore consistent with finite-iteration regularization for the GiBUU-like "
                       "change, but not for every change tested, and no single cause is established"),
    ("paper_body.tex", "These closures are descriptive: no pass threshold is set, and they do not establish the bias "
                       "under the true detector response"),
    ("paper_body.tex", r"$^{\dagger}$Reconstruction stability \fvval{h2-lowstab-min}--\fvval{h2-lowstab-max}"),
    ("app_response_mismatch.tex", "The closures are descriptive and carry no noise estimate: no pass threshold is set"),
]


def numerals(t):
    t = re.sub(r"\\(fvval|ref\*?|nsec|napp|cite|label|eqref|includegraphics|fvpending)(\[[^]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\SI\{([0-9.]+)e([-0-9]+)\}", r" \1e\2 ", t)        # an SI number with exponent is one numeral
    return set(re.findall(r"\d+\.\d+e-?\d+|\d+(?:\.\d+)?", t))


def values(text):
    return dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", text, re.M))


def check(cur, old, vals):
    """cur and old: {file: source}; vals: the values_fived16.tex keys."""
    fails = []
    mp, mp0 = cur["main_paper.tex"], old["main_paper.tex"]
    want = mp0
    for a, b in ABSTRACT_EDITS:
        if want.count(a) != 1:
            fails.append(f"main_paper.tex: the base no longer holds {a[:50]!r} once")
        want = want.replace(a, b, 1)
    got = "\n".join(l for l in mp.splitlines() if not l.startswith(ABSTRACT_COMMENT))
    if got != want.rstrip("\n") and got != want:
        fails.append("main_paper.tex: differs from its base by more than the declared abstract draft")
    if sum(l.startswith(ABSTRACT_COMMENT) for l in mp.splitlines()) != 1:
        fails.append("main_paper.tex: the draft's source comment is not there once")
    pr = {f: cl.printed(cur[f]) for f in cur}
    pr0 = {f: cl.printed(old[f]) for f in old}
    for f in ("paper_body.tex", "main_paper.tex"):
        new = numerals(pr[f]) - numerals(pr0["paper_body.tex"] + " " + pr0["main_paper.tex"]) - set(NEW_NUMERALS)
        if new:
            fails.append(f"{f}: numerals the base does not print and NEW_NUMERALS does not declare: {sorted(new)}")
    used = set(re.findall(r"\\fvval\{([^}]*)\}", pr["paper_body.tex"] + pr["main_paper.tex"]))
    if used - set(vals):
        fails.append(f"the paper prints undefined keys: {sorted(used - set(vals))}")
    app = pr["paper_body.tex"].split(r"\section{Uncertainty tables}")[-1]
    want_keys = {f"sig-{g}-{c}" for g in GROUPS for c in CELLS} | {f"sigmed-{g}" for g in GROUPS} | \
        {f"corr-{CELLS[i]}-{CELLS[j]}" for i in range(16) for j in range(i)}
    have = set(re.findall(r"\\fvval\{((?:sig|sigmed|corr)-[^}]*)\}", app))
    if have != want_keys:
        fails.append(f"the appendix tables' keys differ from the note's: missing {sorted(want_keys - have)[:4]}, "
                     f"extra {sorted(have - want_keys)[:4]}")
    for lo, hi, what in (("e2-with-gibuu-total-ch", "g-gibuu-carbon-total-chi2", "with CH shape ratios"),
                         ("g-gibuu-genieh-total-chi2", "g-gibuu-gen-carbon-total-chi2", "with GENIE's hydrogen")):
        if not float(vals[lo]) < float(vals[hi]):
            fails.append(f"Sec. V B: GiBUU's total {what} ({vals[lo]}) is not below its carbon value ({vals[hi]})")
    flagged = re.findall(r"\n(R\d\d)\$\^\{\\dagger\}\$ &", cur["paper_body.tex"])
    want_f = re.split(r", | and ", vals["h2-lowstab-cells"])
    if flagged != want_f:
        fails.append(f"Table II flags {flagged}, not the low-stability cells {want_f}")
    for f, s in GONE:
        if s in pr[f]:
            fails.append(f"{f}: still prints {s!r}")
    for f, s in ONCE:
        if pr[f].count(s) != 1:
            fails.append(f"{f}: prints {s[:60]!r} {pr[f].count(s)} times, not once")
    return fails


FILES = ["paper_body.tex", "main_paper.tex", "sec_method.tex", "app_response_mismatch.tex"]


def load(wt, base):
    cur = {f: (Path(wt) / NOTE / f).read_text() for f in FILES}
    old = {f: cl.git_show(wt, base, f"{NOTE}/{f}") for f in FILES}
    return cur, old, values((Path(wt) / NOTE / "values_fived16.tex").read_text())


def self_test(wt, base):
    cur, old, vals = load(wt, base)
    assert not check(cur, old, vals), "the worktree must pass before planting"
    pb = "paper_body.tex"
    # each plant: (edit, the failure message it must produce), so a plant caught by another check does not count
    plants = {
        "abstract edited beyond the draft": (lambda c, v: ({**c, "main_paper.tex": c["main_paper.tex"].replace(
            "reported in sixteen cells", "reported in 16 cells", 1)}, v), "more than the declared abstract draft"),
        "abstract draft reverted": (lambda c, v: ({**c, "main_paper.tex": c["main_paper.tex"].replace(
            "As a descriptive comparison, three", "Three", 1)}, v), "more than the declared abstract draft"),
        "a new printed number": (lambda c, v: ({**c, pb: c[pb].replace(
            "Each classifier is trained", "Each classifier, on 9973 events, is trained", 1)}, v), "['9973']"),
        "an undefined key": (lambda c, v: ({**c, pb: c[pb].replace(r"\fvval{f0b-q3-prel}", r"\fvval{f0b-q3-pX}", 1)},
                                           v), "undefined keys: ['f0b-q3-pX']"),
        "an appendix key dropped": (lambda c, v: ({**c, pb: c[pb].replace(r"\fvval{corr-R15-R14}", "", 1)}, v),
                                    "missing ['corr-R15-R14']"),
        "the CH-ratio fall reversed": (lambda c, v: (c, {**v, "e2-with-gibuu-total-ch": "99.00"}), "with CH shape"),
        "the hydrogen fall reversed": (lambda c, v: (c, {**v, "g-gibuu-genieh-total-chi2": "99.00"}),
                                       "with GENIE's hydrogen"),
        "the old Sec. III sentence back": (lambda c, v: ({**c, pb: c[pb].replace(
            "Each classifier is trained", "No hyperparameter search was performed on data. Each classifier is trained",
            1)}, v), "still prints 'No hyperparameter search"),
        "item 8 dropped": (lambda c, v: ({**c, pb: c[pb].replace(
            "The value is descriptive, and no $p$-value is quoted for it.", "", 1)}, v), "and ndf is the number of"),
        "ndf as the rank again": (lambda c, v: ({**c, pb: c[pb].replace(
            "and ndf is the number of reported bins.", "and ndf is that rank.", 1)}, v), "still prints 'and ndf is that rank'"),
        "the closure marker dropped": (lambda c, v: ({**c, pb: c[pb].replace(
            r"$^{*}$Closure test: the truth is the simulation's own.", "", 1)}, v), "Closure test"),
        "a Table II flag moved": (lambda c, v: ({**c, pb: c[pb].replace("\nR06$^{\\dagger}$ &", "\nR06 &", 1).replace(
            "\nR07 &", "\nR07$^{\\dagger}$ &", 1)}, v), "Table II flags"),
        "the old attribution back": (lambda c, v: ({**c, pb: c[pb].replace(
            "The residual is therefore consistent", "We interpret the residual as regularization bias, because it "
            "persists over the tested iteration numbers and classifier capacities. The residual is therefore consistent",
            1)}, v), "still prints 'because it persists"),
        "note sentence dropped": (lambda c, v: ({**c, "sec_method.tex": c["sec_method.tex"].replace(
            "The change was decided on that closure test, ", "", 1)}, v), "sec_method.tex: prints"),
    }
    missed = []
    for k, (f, msg) in plants.items():
        c, v = f(dict(cur), dict(vals))
        if not any(msg in x for x in check(c, old, v)):
            missed.append(k)
    n = len(plants)
    print(f"check_round self-test: {n - len(missed)}/{n} planted defects caught" + (f"; MISSED {missed}" if missed else ""))
    return 1 if missed else 0


def main(argv):
    wt = argv[0]
    base = argv[argv.index("--base") + 1] if "--base" in argv else rl.BASE
    if "--self-test" in argv:
        return self_test(wt, base)
    fails = check(*load(wt, base))
    for x in fails:
        print("FAIL", x)
    print(f"check_round: {'PASS' if not fails else 'FAIL'} (base {base}; {len(GONE)} removals, {len(ONCE)} additions, "
          f"{len(ABSTRACT_EDITS)} abstract edits; {len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
