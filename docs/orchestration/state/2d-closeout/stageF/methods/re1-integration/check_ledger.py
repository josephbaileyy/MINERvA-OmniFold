#!/usr/bin/env python3
"""Check the RE-1 integration against its fact ledger (ledger.tsv beside this file).

usage: check_ledger.py <worktree> [--base REF] [--ledger FILE] [--self-test]

For every ledger row:
  1. the "new" text occurs in the printed (comment-stripped, whitespace-collapsed) source of docs/analysis-note/<file>;
  2. the "old" text (unless "-") no longer prints. For a .tex row it must print in NO posted file (the printed
     \\input closure of main_note, main_paper, main_primer and pet_note), so a stale copy elsewhere also fails;
     for any other file (make_figures.sh) it must not occur outside whole-line comments of that file;
  3. the "source literal" occurs in the cited authority file (path relative to stageF/methods), so each printed
     number is tied to the line of RE1-REPORT-2 / its rulings / the decisions it came from, not to memory.
Also:
  4. each replaced figure equals, byte for byte, the RE-1 run-2 F2 output of the same name (sha256 printed);
  5. protected text is untouched: main_paper.tex has no diff against BASE, and no added or removed line in any changed
     deliverable matches the protected patterns (holds, acknowledgments, funding, AI-use, data availability).
--self-test plants two bad rows (a wrong new value; an old value still printed in another posted file) and requires
exactly those two to fail.
Exit 1 on any failure.

SCOPE OF VALIDITY (added 2026-10-23, register round r15). This ledger describes the RE-1 integration tree: branch
tip eb1942ce, merged to main as afb7e1fa, on base 08fac419 (the merge-base of that merge). --base now defaults to that
pinned base instead of origin/main, which moves. The ledger is valid for trees up to afb7e1fa; run it there:
    git worktree add --detach <tmp> afb7e1fa
    python3 <tmp>/docs/orchestration/state/2d-closeout/stageF/methods/re1-integration/check_ledger.py <tmp>
On later trees it fails by design for rows E17, E18 and C19 and for the main_paper.tex protection. The register
round r15 rewrote those paper sentences and the abstract. r15/ledger.md carries their facts (rows I9, C4 and C5,
and the abstract rows); r15/changes.md records that r15 supersedes these rows. No check here was relaxed."""
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = HERE.parent
FIGS = ["eavail_spectrum", "generators_vs_unfolded_band_central", "mode_decomp_eavail_central",
        "compare_mec_eavail_central", "ascencio_fullcov_compare_central"]
PROTECTED = re.compile(r"\\pubhold|acknowledg|funding|DE-AC|DE-SC|Claude|AI-use|AI use|data availability|"
                       r"artificial intelligence", re.I)
POSTED_DRIVERS = ["main_note", "main_paper", "main_primer", "pet_note"]
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")


def printed(path):
    src = path.read_text()
    if path.suffix == ".sh":  # a commented-out run line does not run
        src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    else:
        src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)


def norm(t):
    return re.sub(r"\s+", " ", t.strip())


def posted_files(note):
    """The printed \\input/\\include closure of the posted drivers (commented-out inputs do not count)."""
    seen, todo = set(), list(POSTED_DRIVERS)
    while todo:
        name = todo.pop()
        f = name if name.endswith(".tex") else name + ".tex"
        if f in seen or not (note / f).is_file():
            continue
        seen.add(f)
        todo += INPUT_RE.findall(printed(note / f))
    return sorted(seen)


def check_rows(wt, ledger):
    note = wt / "docs/analysis-note"
    posted = posted_files(note)
    cache = {f: printed(note / f) for f in posted}
    fails, n, failed = 0, 0, set()
    for line in ledger.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            print(f"MALFORMED row: {line[:80]!r}"); fails += 1; continue
        rid, f, new, old, srcf, srclit = cells
        n += 1
        if f not in cache:
            cache[f] = printed(note / f)
        if norm(new) not in cache[f]:
            print(f"{rid}: NEW NOT PRINTED in {f}: {new!r}"); fails += 1; failed.add(rid)
        if old != "-":
            scope = posted if f.endswith(".tex") else [f]
            where = [g for g in scope if norm(old) in cache[g]]
            if where:
                print(f"{rid}: OLD STILL PRINTED in {', '.join(where)}: {old!r}"); fails += 1; failed.add(rid)
        sp = (METHODS / srcf).resolve()
        if not sp.is_file() or norm(srclit) not in norm(sp.read_text()):
            print(f"{rid}: SOURCE LITERAL NOT FOUND in {srcf}: {srclit!r}"); fails += 1; failed.add(rid)
    print(f"  old-text sweep over {len(posted)} posted files")
    return n, fails, failed


def check_figs(wt):
    fails = 0
    new = METHODS / "re1/run2/f/new"
    for f in FIGS:
        a = hashlib.sha256((wt / f"docs/analysis-note/figures/{f}.pdf").read_bytes()).hexdigest()
        b = hashlib.sha256((new / f"{f}.pdf").read_bytes()).hexdigest()
        ok = a == b
        print(f"  figure {f}.pdf {a} {'== F2' if ok else '!= F2 ' + b}")
        fails += not ok
    return fails


def check_protected(wt, base):
    fails = 0
    paper = subprocess.run(["git", "-C", str(wt), "diff", "--quiet", base, "--", "docs/analysis-note/main_paper.tex"])
    if paper.returncode != 0:
        print("PROTECTED: main_paper.tex differs from base"); fails += 1
    diff = subprocess.run(["git", "-C", str(wt), "diff", "-U0", base, "--", "docs/analysis-note/*.tex"],
                          capture_output=True, text=True, check=True).stdout
    for l in diff.splitlines():
        if l[:1] in "+-" and not l.startswith(("+++", "---")) and PROTECTED.search(l):
            print(f"PROTECTED pattern in a changed line: {l[:120]!r}"); fails += 1
    return fails


def main():
    args = sys.argv[1:]
    self_test = "--self-test" in args
    args = [a for a in args if a != "--self-test"]
    base = "08fac419046b5ef5b68ee8180ef4f1567e8ce56a"  # the RE-1 integration's base; see SCOPE OF VALIDITY
    ledger = HERE / "ledger.tsv"
    if "--base" in args:
        i = args.index("--base"); base = args[i + 1]; del args[i:i + 2]
    if "--ledger" in args:
        i = args.index("--ledger"); ledger = Path(args[i + 1]); del args[i:i + 2]
    wt = Path(args[0]).resolve()
    if self_test:
        bad = ("SELFTEST\tsec_3d.tex\tindicative distance is $\\chi^{2}/\\mathrm{ndf}=4.98$\t-\t"
               "re1/RE1-REPORT-2.md\t**4.52**\n"
               # an old value absent from sec_3d.tex but still printed in another posted file (sec_eavailw.tex)
               "SELFTEST2\tsec_3d.tex\t\\SI{9.2}{\\percent}\tcentral values \\SI{9.2}{\\percent} and\t"
               "re1/RE1-REPORT-2.md\t**6.0**\n")
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as t:
            t.write(ledger.read_text() + bad)
        n, fails, failed = check_rows(wt, Path(t.name))
        print(f"SELF-TEST: {n} rows, failed ids {sorted(failed)}")
        if failed != {"SELFTEST", "SELFTEST2"}:
            print("SELF-TEST :: FAIL (want exactly the two planted rows to fail)"); sys.exit(1)
        print("SELF-TEST :: PASS (both planted rows fail: a wrong new value, and an old text printed in another "
              "posted file)")
        sys.exit(0)
    n, fails, _ = check_rows(wt, ledger)
    fails += check_figs(wt)
    fails += check_protected(wt, base)
    print(f"LEDGER :: {'PASS' if not fails else 'FAIL'} ({n} rows, {fails} failures)")
    sys.exit(1 if fails else 0)


main()
