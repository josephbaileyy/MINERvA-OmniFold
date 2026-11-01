#!/usr/bin/env python3
"""Check the RE-2 integration against its fact ledger (ledger.tsv beside this file).

usage: check_ledger.py <worktree> [--base REF] [--ledger FILE] [--self-test]

Modelled on re1-integration/check_ledger.py. Paths in the ledger are relative to the repository root, except a V row's
table path, which is relative to stageF/methods. The printed text of a file is its source with LaTeX comments removed
and whitespace collapsed. Row kinds:

  V  a regenerated value of RE-2 part C's values table (re2/run/partc_r2/partc-r2/values_table.tsv):
       V <id> <file> <base line> <old printed> <new printed> <new context> <old context or -> <table> <row id> <field>
     the table row <row id> must have status "control PASS", `printed` equal to <old printed> and <field> equal to
     <new printed>; <new context> (which contains the new value) must print in docs/analysis-note/<file>; when the value
     changed, <old context> must print in NO posted file (the printed \\input closure of main_note, main_paper,
     main_primer and pet_note), so a stale copy elsewhere also fails.
  M  a new values.tex macro computed from a committed product:
       M <id> <macro> <source> <key> <scale> <format>
     \\newcommand{\\<macro>}{X} must be defined exactly once in values.tex, and X must equal
     format(scale * value), where value is <key> of <source>: a dotted path into a .json or .json.gz file, or
     "<row id>.<column>" of a .tsv file.
  F  a fact of a wording draft:
       F <id> <file> <new: must print> <old: must not print, or -> <source> <source literal>
     <new> must print in docs/analysis-note/<file>; <old> must print in no posted file; <source literal> must occur
     (whitespace collapsed) in <source> (.gz read as text).
  G  a figure installed from RE-2 part C's refined products:
       G <id> <basename> <sha256> <SHA256SUMS file> <its entry>
     docs/analysis-note/figures/<basename> and the committed copy re2-integration/figs/<basename> must both have
     <sha256>; <SHA256SUMS file> must list exactly <sha256> for <entry>; and make_figures.sh must install the file with
     that pin ("install_re2_fig <basename> <sha256>").
       G <id> <basename> <sha256> <SHA256SUMS file> <its entry> <copy directory>
     A row re-pointed by the 2D figure restyle (fig-restyle-20261031/DECLARATION.md section 5 item 3, ruling 1:
     re-point, do not replace) names its committed copy's directory, relative to the repository root; the copy is
     read there, and make_figures.sh must install it with "install_restyle_fig <basename> <sha256>". The figure's
     RE-2 digests stay in fig-restyle-20261031/DIGESTS.tsv.
  --figures checks the G rows and Fig. 1 only, with no posted-text sweep. The V, M and F rows record the RE-2
  integration's text of 2026-10-23; later note rounds rewrote that text, so the full run no longer applies to the
  current tree, while the figure pins still do.

Also:
  - Fig. 1: docs/analysis-note/figures/paper_fig1_validation.pdf and the committed copy fig1/fig1_validation.pdf both
    have sha256 71a2ea48... (RE2-PARTC-A3-REPORT.md sec. 3);
  - check_sec4_receipts.py reads Q_R's budget (BUDGET_Q names re2/run/partc_r2/partc-r2/outA/budget_Q.json.gz);
  - protected text is untouched: main_paper.tex has no diff against BASE, and no added or removed line of any changed
    .tex deliverable matches the protected patterns (holds, acknowledgments, funding, AI-use, data availability).
--self-test plants one bad row of each kind (a V row whose new value is not the table's, an M row whose macro value is
wrong, an F row whose old text still prints in another posted file, a G row whose pin is not the file's digest) and
requires exactly those four to fail.
Exit 1 on any failure.
"""
import csv
import gzip
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = HERE.parent
FIG_SHA = "71a2ea488ab758a466d40b7d5a7a061ebd95b1cdb90a79427c3da968238b6427"
BUDGET_QR = "2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/outA/budget_Q.json.gz"
PROTECTED = re.compile(r"\\pubhold|acknowledg|funding|DE-AC|DE-SC|Claude|AI-use|AI use|data availability|"
                       r"artificial intelligence", re.I)
POSTED_DRIVERS = ["main_note", "main_paper", "main_primer", "pet_note"]
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
BASE_DEFAULT = "104c69a365e7e63734062ad642924cdf6b9a96ea"  # origin/main when this integration branched


def printed(path):
    src = path.read_text()
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)


def norm(t):
    return re.sub(r"\s+", " ", t.strip())


def read_text(path):
    return gzip.open(path, "rt", encoding="utf-8").read() if path.suffix == ".gz" else path.read_text()


def posted_files(note):
    seen, todo = set(), list(POSTED_DRIVERS)
    while todo:
        name = todo.pop()
        f = name if name.endswith(".tex") else name + ".tex"
        if f in seen or not (note / f).is_file():
            continue
        seen.add(f)
        todo += INPUT_RE.findall(printed(note / f))
    return sorted(seen)


def lookup(path, key):
    if path.suffix == ".tsv":
        rid, _, col = key.partition(".")
        with open(path, newline="") as fh:
            rows = [r for r in csv.DictReader(fh, delimiter="\t") if r.get("id") == rid]
        if len(rows) != 1:
            raise KeyError(f"{rid}: {len(rows)} rows")
        return float(rows[0][col])
    obj = json.loads(read_text(path))
    for k in key.split("."):
        obj = obj[k]
    return float(obj)


def check_rows(wt, ledger, figures_only=False):
    note = wt / "docs/analysis-note"
    posted = [] if figures_only else posted_files(note)
    cache = {f: printed(note / f) for f in posted}
    macros = [] if figures_only else re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}",
                                                 cache.get("values.tex", printed(note / "values.tex")))
    tables = {}
    fails, failed, counts = 0, set(), {"V": 0, "M": 0, "F": 0, "G": 0}
    mkfig = (note / "make_figures.sh").read_text()

    def fail(rid, msg):
        nonlocal fails
        print(f"{rid}: {msg}"); fails += 1; failed.add(rid)

    def stale(rid, old):
        where = [g for g in posted if norm(old) in cache[g]]
        if where:
            fail(rid, f"OLD STILL PRINTED in {', '.join(where)}: {old!r}")

    for line in ledger.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        c = line.split("\t")
        kind = c[0]
        if kind not in counts:
            print(f"MALFORMED row: {line[:80]!r}"); fails += 1; continue
        if figures_only and kind != "G":
            continue
        counts[kind] += 1
        if kind == "V":
            if len(c) != 11:
                fail(c[1] if len(c) > 1 else "?", "MALFORMED V row"); continue
            _, rid, f, _ln, old, new, nctx, octx, table, trow, field = c
            if table not in tables:
                with open(METHODS / table, newline="") as fh:
                    tables[table] = {r["id"]: r for r in csv.DictReader(fh, delimiter="\t")}
            r = tables[table].get(trow)
            if r is None or r["status"] != "control PASS" or r["printed"] != old or r[field] != new:
                fail(rid, f"TABLE MISMATCH: {table} row {trow} does not give {old!r} -> {new!r} with control PASS")
            if new not in nctx:
                fail(rid, f"new value {new!r} not in its context {nctx!r}")
            if f not in cache:
                cache[f] = printed(note / f)
            if norm(nctx) not in cache[f]:
                fail(rid, f"NEW NOT PRINTED in {f}: {nctx!r}")
            if octx != "-":
                stale(rid, octx)
        elif kind == "G":
            if len(c) not in (6, 7):
                fail(c[1] if len(c) > 1 else "?", "MALFORMED G row"); continue
            _, rid, base, sha, sums, entry = c[:6]
            copydir, installer = (wt / c[6], "install_restyle_fig") if len(c) == 7 else (HERE / "figs", "install_re2_fig")
            for path in (note / "figures" / base, copydir / base):
                h = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
                if h != sha:
                    fail(rid, f"FIGURE {path.name} at {path.parent.name}/ has sha256 {h}, pinned {sha}")
            listed = [l.split()[0] for l in (wt / sums).read_text().splitlines() if l.split()[1:] == [entry]]
            if listed != [sha]:
                fail(rid, f"SHA256SUMS {sums} lists {listed} for {entry}, not {sha}")
            if not re.search(r"^" + installer + r"\s+" + re.escape(base) + r"\s+" + sha + r"\s*$", mkfig, re.M):
                fail(rid, f"make_figures.sh does not install {base} with pin {sha} ({installer})")
        elif kind == "M":
            if len(c) != 7:
                fail(c[1] if len(c) > 1 else "?", "MALFORMED M row"); continue
            _, rid, macro, src, key, scale, fmt = c
            defs = [v for n, v in macros if n == macro]
            try:
                want = format(float(scale) * lookup(wt / src, key), fmt)
            except Exception as exc:  # a missing source or key is a failure, not a skip
                fail(rid, f"SOURCE {src} {key}: {exc}"); continue
            if len(defs) != 1 or defs[0] != want:
                fail(rid, f"MACRO \\{macro} is {defs} in values.tex; {src} {key} gives {want!r}")
        else:
            if len(c) != 7:
                fail(c[1] if len(c) > 1 else "?", "MALFORMED F row"); continue
            _, rid, f, new, old, src, lit = c
            if f not in cache:
                cache[f] = printed(note / f)
            if norm(new) not in cache[f]:
                fail(rid, f"NEW NOT PRINTED in {f}: {new!r}")
            if old != "-":
                stale(rid, old)
            sp = wt / src
            if not sp.is_file() or norm(lit) not in norm(read_text(sp)):
                fail(rid, f"SOURCE LITERAL NOT FOUND in {src}: {lit!r}")
    print(f"  rows: V {counts['V']}, M {counts['M']}, F {counts['F']}, G {counts['G']}; old-text sweep over {len(posted)} posted files")
    return counts, fails, failed


def check_fig(wt):
    fails = 0
    for p in (wt / "docs/analysis-note/figures/paper_fig1_validation.pdf", HERE / "fig1/fig1_validation.pdf"):
        h = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "missing"
        ok = h == FIG_SHA
        print(f"  figure {p.relative_to(wt) if p.is_relative_to(wt) else p} {h} {'OK' if ok else '!= ' + FIG_SHA}")
        fails += not ok
    return fails


def check_sec4(wt):
    src = (wt / "docs/analysis-note/check_sec4_receipts.py").read_text()
    m = re.findall(r'^BUDGET_Q = "([^"]+)"', src, re.M)
    ok = m == [BUDGET_QR] and (wt / "docs/orchestration/state" / BUDGET_QR).is_file()
    print(f"  check_sec4_receipts.py BUDGET_Q = {m} {'OK' if ok else '!= ' + BUDGET_QR}")
    return 0 if ok else 1


def check_protected(wt, base):
    fails = 0
    paper = subprocess.run(["git", "-C", str(wt), "diff", "--quiet", base, "--", "docs/analysis-note/main_paper.tex"])
    if paper.returncode != 0:
        print("PROTECTED: main_paper.tex differs from base"); fails += 1
    diff = subprocess.run(["git", "-C", str(wt), "diff", "-U0", base, "--", "docs/analysis-note/*.tex"],
                          capture_output=True, text=True, check=True).stdout
    n = 0
    for l in diff.splitlines():
        if l[:1] in "+-" and not l.startswith(("+++", "---")):
            n += 1
            if PROTECTED.search(l):
                print(f"PROTECTED pattern in a changed line: {l[:120]!r}"); fails += 1
    print(f"  protected: main_paper.tex unchanged against {base[:12]}; {n} changed .tex lines scanned")
    return fails


def main():
    args = sys.argv[1:]
    self_test = "--self-test" in args
    figures_only = "--figures" in args
    args = [a for a in args if a not in ("--self-test", "--figures")]
    base, ledger = BASE_DEFAULT, HERE / "ledger.tsv"
    if "--base" in args:
        i = args.index("--base"); base = args[i + 1]; del args[i:i + 2]
    if "--ledger" in args:
        i = args.index("--ledger"); ledger = Path(args[i + 1]); del args[i:i + 2]
    wt = Path(args[0]).resolve()
    if self_test and not figures_only:
        bad = ("V\tSELFTEST-V\tvalues.tex\t125\t2.65\t2.64\t\\newcommand{\\chiPaper}{2.64}\t-\t"
               "re2/run/partc_r2/partc-r2/values_table.tsv\tm-chiPaper\trefined_rendered\n"
               "M\tSELFTEST-M\tqrCmodelMedian\tdocs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/"
               "partc-r2/cmodel/cmodel_R.json\tcell_rel_sigma.C_model.median\t100\t.2f\n"
               # an old text absent from sec_3d.tex but printed in another posted file (sec_systematics.tex)
               "F\tSELFTEST-F\tsec_3d.tex\tcross-configuration comparison\tGenerator-shape model dependence\t"
               "docs/orchestration/DECISION-20261024-joseph-2d-model-dependence-component.md\tC_model has rank 3\n"
               # a figure pinned with a digest that is not the installed file's
               "G\tSELFTEST-G\tuq_corr_2d.pdf\t" + "0" * 64 + "\tdocs/orchestration/state/2d-closeout/stageF/methods/re2/"
               "run/partc_r2/partc-r2/SHA256SUMS\t./stat/uq_corr_2d.pdf\n")
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as t:
            t.write(ledger.read_text() + bad)
        _, _, failed = check_rows(wt, Path(t.name))
        print(f"SELF-TEST: failed ids {sorted(failed)}")
        want = {"SELFTEST-V", "SELFTEST-M", "SELFTEST-F", "SELFTEST-G"}
        if failed != want:
            print("SELF-TEST :: FAIL (want exactly the four planted rows to fail)"); sys.exit(1)
        print("SELF-TEST :: PASS (the four planted rows fail: a figure pin that is not the file's digest, a new value "
              "that is not the table's, a macro that is "
              "not its product's value, and an old text still printed in another posted file)")
        sys.exit(0)
    if figures_only:
        if self_test:  # both directions: the committed rows pass; a wrong pin and a re-pointed row at a wrong copy fail
            _, f0, _ = check_rows(wt, ledger, figures_only=True)
            rows = [l for l in ledger.read_text().splitlines() if l.startswith("G\t") and len(l.split("\t")) == 7]
            bad = ("G\tSELFTEST-G6\tuq_corr_2d.pdf\t" + "0" * 64 + "\tdocs/orchestration/state/2d-closeout/stageF/methods/"
                   "re2/run/partc_r2/partc-r2/SHA256SUMS\t./stat/uq_corr_2d.pdf\n")
            if rows:  # a re-pointed row whose copy directory is the RE-2 one, where the restyled file is not
                c = rows[0].split("\t")
                bad += "\t".join(["G", "SELFTEST-G7"] + c[2:6] + ["docs/orchestration/state/2d-closeout/stageF/methods/"
                                                                   "re2-integration/figs"]) + "\n"
            with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as t:
                t.write(ledger.read_text() + bad)
            _, _, failed = check_rows(wt, Path(t.name), figures_only=True)
            want = {"SELFTEST-G6"} | ({"SELFTEST-G7"} if rows else set())
            ok = f0 == 0 and failed == want
            print(f"FIGURES SELF-TEST :: {'PASS' if ok else 'FAIL'} (committed rows {f0} failures; planted failures "
                  f"{sorted(failed)}, want {sorted(want)})")
            sys.exit(0 if ok else 1)
        counts, fails, _ = check_rows(wt, ledger, figures_only=True)
        fails += check_fig(wt)
        print(f"LEDGER FIGURES :: {'PASS' if not fails else 'FAIL'} (G {counts['G']} rows and Fig. 1; {fails} failures)")
        sys.exit(1 if fails else 0)
    counts, fails, _ = check_rows(wt, ledger)
    fails += check_fig(wt)
    fails += check_sec4(wt)
    fails += check_protected(wt, base)
    print(f"LEDGER :: {'PASS' if not fails else 'FAIL'} (V {counts['V']}, M {counts['M']}, F {counts['F']}, G {counts['G']} rows; "
          f"{fails} failures)")
    sys.exit(1 if fails else 0)


main()
