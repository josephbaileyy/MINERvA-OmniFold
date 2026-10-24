#!/usr/bin/env python3
"""RE-2 dependency inventory of the analysis note (RE2-PLAN.md sec. 2.2-2.4).

    python3 2d-unfolding/re2/re2_inventory.py --out re2/inventory.tsv [--repo DIR]

Reads only the git-tracked files under docs/analysis-note/ (``git ls-files``), as they stand in the working tree,
and writes one TSV row per hit:

    kind  name  file  line  text  action  builds  in_comment

* ``macro``: every use of each macro of the RE2-PLAN sec. 2.2 groups in ``N/*.tex``. A macro's own definition is
  not a use; another macro's definition that expands it is.
* ``figure``: every mention of each sec. 2.3 figure basename in ``N/*.tex`` and ``N/*.sh``, and every
  ``\\ref``-family reference to the ``\\label`` of the figure environment that includes it.
* ``literal``: the PHASE2-INVENTORY number-and-keyword grep (PHASE2-INVENTORY.md:9-14), here for E_U's and Q's
  printed numbers at several precisions, over ``N/*.tex``, ``N/*.sh`` and ``N/*.py``. A literal hit is a site to
  read, not a finding: many short numbers collide with unrelated values.

``builds`` lists the build targets (``build_all.sh``'s ``targets=(...)``) whose ``\\input`` closure contains the
file, or ``none``. ``in_comment`` is ``yes`` when the hit lies after an unescaped ``%`` on its line.

Every macro the groups name must be defined exactly once among the note's .tex files, and every figure basename
must be found in some ``\\includegraphics``; otherwise the script exits 2 without writing. Output order is
deterministic: kind (macro, figure, literal), then name, file, line, column.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

NOTE = "docs/analysis-note"

# RE2-PLAN sec. 2.2: (group, action, macro names or "prefix*").
MACRO_GROUPS = [
    ("published comparison", "re-evaluate (P12)",
     ["sigTwoD", "ratioTot", "medianBinRatio", "binsFive", "binsTen", "binsTwenty",
      "pullMean", "pullRMS", "pullRMSr", "chiPaper"]),
    ("published-side values", "unchanged",
     ["sigTwoDpaper", "uqPaper", "uqPaperIntegral"]),
    ("exact-split comparators", "unchanged value; reword text comparing it to \\chiPaper",
     ["chiPaperExact", "chiPaperExactSeeded"]),
    ("combined covariance", "re-evaluate (P11)",
     ["chiCombined", "chiCombinedLog", "chiCombinedSubStat"]),
    ("uncertainty budget", "re-evaluate (P11)",
     ["uqMedian", "uqIntegral", "uqSFiveMedian", "fluxBand"]),
    ("flux-muon correlation", "unchanged",
     ["rhoFluxMuon"]),
    ("extended fiducial", "re-evaluate against E_R's total",
     ["fpsAbove"]),
    ("extended fiducial", "outside RE-2 (sec. 2.7)",
     ["fpsSigma", "fpsAnchor", "covFPS", "covFPSanalytic"]),
    ("purity coverage history", "unchanged value; reword text applying it to the quoted covariance",
     ["covTwoD*", "pullFrac", "pullMeanAbs", "pullGauss"]),
    ("negative-weight study", "unchanged",
     ["nw*"]),
]

# RE2-PLAN sec. 2.3: (basename regex, action).
FIGURES = [
    (r"MEFHC_5iter_fig13", "re-evaluate on E_R"),
    (r"MEFHC_5iter_xsec_proj_pt", "re-evaluate on E_R"),
    (r"MEFHC_5iter_xsec_proj_pz", "re-evaluate on E_R"),
    (r"MEFHC_5iter_pull_full", "re-evaluate on E_R"),
    (r"MEFHC_5iter_xsec_paper_pt_slices", "re-evaluate on E_R"),
    (r"MEFHC_5iter_xsec_paper_pz_slices", "re-evaluate on E_R"),
    (r"tension_[A-Za-z0-9_]+", "re-evaluate"),
    (r"model_comp_[A-Za-z0-9_]+", "re-evaluate"),
    (r"MEFHC_fig6_7_uncertainty_pt", "re-evaluate on Q_R"),
    (r"MEFHC_fig6_7_uncertainty_pz", "re-evaluate on Q_R"),
    (r"uq_spread_2d", "re-evaluate on Q_R"),
    (r"uq_corr_2d", "re-evaluate on Q_R"),
    (r"paper_fig1_validation", "re-evaluate"),
    (r"MEFHC_5iter_xsec_eff_heatmap", "re-evaluate after the hEff2D control"),
]

# Literal numbers: (number, source, action). "pct" numbers match only in a percent context.
_P11 = "review; if it is the Q value: re-evaluate (P11)"
_P12 = "review; if it is the E_U value: re-evaluate (P12)"
LITERALS = [
    ("3.0730", "sigTwoD", _P12), ("3.073", "sigTwoD", _P12), ("3.07", "sigTwoD (3 s.f.)", _P12),
    ("1.0112", "ratioTot", _P12), ("1.011", "ratioTot", _P12), ("1.1 pct", "ratioTot as a percent", _P12),
    ("1.0081", "medianBinRatio", _P12), ("1.008", "medianBinRatio", _P12),
    ("82.9", "binsFive", _P12), ("170/205", "binsFive count", _P12),
    ("95.6", "binsTen", _P12), ("196/205", "binsTen count", _P12),
    ("99.0", "binsTwenty", _P12), ("203/205", "binsTwenty count", _P12),
    ("0.074", "pullMean", _P12), ("0.564", "pullRMS", _P12), ("0.56", "pullRMSr", _P12),
    ("2.654", "chiPaper", _P12), ("2.65", "chiPaper", _P12),
    ("0.964", "chiCombined", _P11), ("197.59", "chiCombined chi2", _P11),
    ("0.987", "chiCombinedLog", _P11), ("202.33", "chiCombinedLog chi2", _P11),
    ("6.012", "chiCombinedSubStat", _P11), ("6.01", "chiCombinedSubStat", _P11),
    ("1232.38", "chiCombinedSubStat chi2", _P11),
    ("6.4479", "uqMedian", _P11), ("6.448", "uqMedian", _P11), ("6.45", "uqMedian", _P11),
    ("4.75", "uqIntegral", _P11),
    ("6.041", "uqSFiveMedian", _P11), ("6.04", "uqSFiveMedian", _P11),
    ("3.7467", "fluxBand", _P11), ("3.747", "fluxBand", _P11), ("3.75", "fluxBand", _P11),
    ("0.6843", "S1 median (budget_Q stat.median_pct)", _P11), ("0.684", "S1 median", _P11),
    ("0.26", "paper_body.tex:445 literal", _P11),
    ("6.94", "run-period step (P8 analysis.json)", "review; if the run-period step: re-evaluate (P8)"),
    ("7 pct", "run-period step, rounded", "review; if the run-period step: re-evaluate (P8)"),
    ("2.0 pct", "run-period block on the integral", _P11),
    ("6.410", "sec_results.tex:155 per-bin median", _P11),
    ("33.0", "Tune v1 chi2/ndf, data vs tune", "review; if Tune v1: data vs tune is unchanged"),
    ("29.8", "Tune v1 chi2/ndf, ours vs tune", _P12),
    ("26.5", "Tune v1 chi2/ndf, exact-split", "review; exact-split comparator: unchanged"),
    ("9.5 pct", "tension: smallest-lambda share", _P12), ("0.81", "tension: 73 best-measured", _P12),
    ("15 pct", "tension: largest band share", _P12),
    ("46 pct", "fpsAbove", "review; if fpsAbove: re-evaluate against E_R's total"),
    ("1.0016", "3D median marginal/2D (sec. 2.4)", "review; re-evaluate against E_R (sec. 2.4)"),
    ("0.95 pct", "3D vs published (sec. 2.4)", "review; wording fixed at integration (sec. 2.4)"),
    ("4.4 pct", "3D scatter (sec. 2.4)", "review; re-evaluate against E_R (sec. 2.4)"),
    # sec_3d.tex after the RE-1 integration (RE2-PLAN sec. 2.4 predates it): against E_U on its 205 cells.
    ("0.001 pct", "3D marginal total vs E_U", "review; re-evaluate against E_R (sec. 2.4)"),
    ("1.0000", "3D median per-bin ratio vs E_U", "review; re-evaluate against E_R (sec. 2.4)"),
    ("3.5 pct", "3D per-bin scatter vs E_U", "review; re-evaluate against E_R (sec. 2.4)"),
    ("0.44 pct", "D2 vs E_U background-treatment movement", "review; reword at adoption (sec. 2.4)"),
    ("1.13 pct", "D2 vs E_U movement, 84th percentile", "review; reword at adoption (sec. 2.4)"),
]
KEYWORDS = [
    ("4f5a1b6d", "E_U sha256 prefix", "repoint at adoption"),
    ("lgbm_uni_full_CV", "E_U filename", "repoint at adoption"),
    ("8ccb4d72", "Q sha256 prefix", "repoint at adoption"),
    ("s5_plus_playlist", "Q filename", "repoint at adoption"),
    ("budget_Q", "Q budget receipt", "repoint at adoption"),
    ("purity", "estimator description (sec. 2.5)", "review; reword at adoption if it describes E_U or Q"),
]

PCT_AFTER = r"(?=(?:\s|~|\\,|\\;|\\ |\})*\{?\s*(?:\\%|%|\\percent|per\s?cent|percent))"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True).stdout


def comment_start(line):
    """Index of the first unescaped % (a TeX comment), or len(line)."""
    i = 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "%":
            return i
        i += 1
    return len(line)


def trim(text, width=220):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= width else text[: width - 3] + "..."


def read_tracked(repo):
    paths = sorted(p for p in git(repo, "ls-files", "--", NOTE).splitlines() if p)
    files = {}
    for p in paths:
        if p.rsplit(".", 1)[-1] not in ("tex", "sh", "py"):
            continue
        files[p] = (repo / p).read_text(encoding="utf-8", errors="replace").splitlines()
    return files


def input_closure(files):
    """build target -> set of .tex paths in its \\input closure (comments stripped)."""
    build = files.get(f"{NOTE}/build_all.sh")
    m = next((re.match(r"\s*targets=\(([^)]*)\)", l) for l in build or [] if re.match(r"\s*targets=\(", l)),
             None)
    if not m:
        sys.exit(f"FAIL no targets=(...) line in {NOTE}/build_all.sh")
    targets = m.group(1).split()
    closure = {}
    for t in targets:
        seen, todo = set(), [f"{NOTE}/{t}.tex"]
        while todo:
            p = todo.pop()
            if p in seen:
                continue
            if p not in files:
                sys.exit(f"FAIL {p} is \\input by {t} but is not a tracked file")
            seen.add(p)
            for line in files[p]:
                live = line[: comment_start(line)]
                for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", live):
                    todo.append(f"{NOTE}/{name if name.endswith('.tex') else name + '.tex'}")
        closure[t] = seen
    return closure


def definitions(files):
    """macro name -> list of (file, line, column of its backslash) definitions across the note's .tex files."""
    pat = re.compile(r"\\(?:(?:re|provide)?newcommand\*?\{?\\([A-Za-z]+)\}?|[egx]?def\\([A-Za-z]+))")
    defs = {}
    for p, lines in files.items():
        if not p.endswith(".tex"):
            continue
        for n, line in enumerate(lines, 1):
            for m in pat.finditer(line[: comment_start(line)]):
                g = 1 if m.group(1) else 2
                defs.setdefault(m.group(g), []).append((p, n, m.start(g) - 1))
    return defs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="TSV to write")
    ap.add_argument("--repo", default=None, help="repository root (default: git toplevel of the cwd)")
    a = ap.parse_args()
    repo = Path(a.repo or git(Path.cwd(), "rev-parse", "--show-toplevel").strip()).resolve()
    head = git(repo, "rev-parse", "HEAD").strip()
    dirty = git(repo, "status", "--porcelain", "--", NOTE).strip()

    files = read_tracked(repo)
    closure = input_closure(files)
    tex = sorted(p for p in files if p.endswith(".tex"))
    defs = definitions(files)

    def builds(p):
        b = [t for t in sorted(closure) if p in closure[t]]
        return ",".join(b) if b else "none"

    rows, problems = [], []

    def hit(kind, name, p, n, col, line, action):
        incom = "yes" if col >= comment_start(line) else "no"
        rows.append((kind, name, p, n, col, trim(line), action, builds(p), incom))

    # (a)+(b) macros
    macros = []
    for group, action, names in MACRO_GROUPS:
        for name in names:
            if name.endswith("*"):
                found = sorted(m for m in defs if m.startswith(name[:-1]) and
                               any(d[0] == f"{NOTE}/values.tex" for d in defs[m]))
                if not found:
                    problems.append(f"no macro matching \\{name} is defined in values.tex")
                macros += [(m, group, action) for m in found]
            else:
                macros.append((name, group, action))
    for name, group, action in macros:
        d = defs.get(name, [])
        if len(d) != 1 or d[0][0] != f"{NOTE}/values.tex":
            problems.append(f"\\{name}: expected one definition in values.tex, found {d}")
            continue
        pat = re.compile(r"\\" + name + r"(?![A-Za-z])")
        for p in tex:
            for n, line in enumerate(files[p], 1):
                for m in pat.finditer(line):
                    if (p, n, m.start()) == d[0]:
                        continue  # the macro's own definition
                    hit("macro", f"\\{name}", p, n, m.start(), line, f"{group}: {action}")

    # (c) figures and the labels of the figure environments that include them
    labels = {}
    for rx, action in FIGURES:
        pat = re.compile(r"(?<![A-Za-z0-9_])(" + rx + r")(?![A-Za-z0-9_])")
        seen_include = False
        for p in sorted(q for q in files if q.endswith((".tex", ".sh"))):
            lines = files[p]
            for n, line in enumerate(lines, 1):
                for m in pat.finditer(line):
                    hit("figure", m.group(1), p, n, m.start(), line, action)
                    if p.endswith(".tex") and "\\includegraphics" in line[: m.start()] and \
                            m.start() < comment_start(line):
                        seen_include = True
                        for k in range(n - 1, min(len(lines), n + 40)):
                            if "\\end{figure" in lines[k]:
                                break
                            for lab in re.findall(r"\\label\{([^}]+)\}", lines[k][: comment_start(lines[k])]):
                                labels.setdefault(lab, set()).add((m.group(1), action))
        if not seen_include:
            problems.append(f"figure {rx}: no \\includegraphics of it in any tracked .tex")
    refpat = re.compile(r"\\(?:[cC]ref|ref|autoref|pageref|eqref|nameref|cpageref|Cpageref)\*?\{([^}]+)\}")
    for p in tex:
        for n, line in enumerate(files[p], 1):
            for m in refpat.finditer(line):
                for lab in (s.strip() for s in m.group(1).split(",")):
                    for base, action in sorted(labels.get(lab, ())):
                        hit("figure", f"ref:{lab} [{base}]", p, n, m.start(), line, action)

    # (d) literal numbers and keywords
    lit_files = sorted(q for q in files if q.endswith((".tex", ".sh", ".py")))
    specs = []
    for num, src, action in LITERALS:
        pct = num.endswith(" pct")
        val = num[:-4] if pct else num
        rx = r"(?<![\d.])" + re.escape(val) + r"(?![\d])" + (PCT_AFTER if pct else "")
        specs.append((f"{num} [{src}]", re.compile(rx), action))
    for kw, src, action in KEYWORDS:
        specs.append((f"kw:{kw} [{src}]", re.compile(re.escape(kw), re.IGNORECASE), action))
    for name, pat, action in specs:
        for p in lit_files:
            for n, line in enumerate(files[p], 1):
                m = pat.search(line)
                if m:
                    hit("literal", name, p, n, m.start(), line, action)

    if problems:
        print("FAIL inventory not written:", *problems, sep="\n  ", file=sys.stderr)
        return 2

    order = {"macro": 0, "figure": 1, "literal": 2}
    rows.sort(key=lambda r: (order[r[0]], r[1], r[2], r[3], r[4]))
    out = Path(a.out)
    with out.open("w", encoding="utf-8") as f:
        f.write(f"# re2_inventory.py over git-tracked {NOTE}/ at HEAD {head}"
                f"{' (WORKING TREE DIFFERS FROM HEAD)' if dirty else ''}\n")
        f.write("kind\tname\tfile\tline\ttext\taction\tbuilds\tin_comment\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ") for i, x in enumerate(r) if i != 4) + "\n")

    # summary
    print(f"HEAD {head}; note tree {'DIRTY' if dirty else 'clean'}; {len(files)} tracked text files read")
    for t in sorted(closure):
        print(f"  build {t}: {len(closure[t])} .tex files in its \\input closure")
    outside = [p for p in tex if builds(p) == "none"]
    print(f"  .tex files outside every build ({len(outside)}): {', '.join(Path(p).name for p in outside)}")
    for k in order:
        ks = [r for r in rows if r[0] == k]
        names = {r[1] for r in ks}
        live = sum(1 for r in ks if r[8] == "no" and r[7] != "none")
        print(f"  {k}: {len(ks)} rows, {len(names)} names, {live} in a built file outside a comment")
    zero = [name for name, _, _ in specs if not any(r[0] == "literal" and r[1] == name for r in rows)]
    print(f"  literal/keyword patterns with no hit: {len(zero)}" + (f" ({'; '.join(zero)})" if zero else ""))
    unused = sorted(m for m, _, _ in macros if not any(r[0] == "macro" and r[1] == f"\\{m}" for r in rows))
    print(f"  macros with no use: {len(unused)}" + (f" ({', '.join(unused)})" if unused else ""))
    print(f"wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
