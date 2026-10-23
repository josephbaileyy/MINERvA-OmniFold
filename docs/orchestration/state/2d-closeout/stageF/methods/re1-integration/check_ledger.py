#!/usr/bin/env python3
"""Check the RE-1 integration against its fact ledger (ledger.tsv beside this file).

usage: check_ledger.py <worktree> [--base REF] [--ledger FILE] [--self-test]

For every ledger row:
  1. the "new" text occurs in the printed (comment-stripped, whitespace-collapsed) source of docs/analysis-note/<file>;
  2. the "old" text (unless "-") no longer occurs there;
  3. the "source literal" occurs in the cited authority file (under stageF/methods), so each printed number is tied to
     the line of RE1-REPORT-2 / its rulings / the decisions it came from, not to memory.
Also:
  4. each replaced figure equals, byte for byte, the RE-1 run-2 F2 output of the same name (sha256 printed);
  5. protected text is untouched: main_paper.tex has no diff against BASE, and no added or removed line in any changed
     deliverable matches the protected patterns (holds, acknowledgments, funding, AI-use, data availability).
--self-test plants a bad probe (an old value given as the new one) and requires the check to fail on it.
Exit 1 on any failure."""
import hashlib, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = HERE.parent
FIGS = ["eavail_spectrum", "generators_vs_unfolded_band_central", "mode_decomp_eavail_central",
        "compare_mec_eavail_central", "ascencio_fullcov_compare_central"]
PROTECTED = re.compile(r"\\pubhold|acknowledg|Acknowledg|funding|Funding|DE-AC|DE-SC|Claude|AI-use|AI use|"
                       r"[Dd]ata availability|artificial intelligence", re.I)


def printed(path):
    src = path.read_text()
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)


def norm(t):
    return re.sub(r"\s+", " ", t.strip())


def check_rows(wt, ledger):
    note = wt / "docs/analysis-note"
    cache, fails, n, failed = {}, 0, 0, set()
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
        txt = cache[f]
        if norm(new) not in txt:
            print(f"{rid}: NEW NOT PRINTED in {f}: {new!r}"); fails += 1; failed.add(rid)
        if old != "-" and norm(old) in txt:
            print(f"{rid}: OLD STILL PRINTED in {f}: {old!r}"); fails += 1; failed.add(rid)
        sp = (METHODS / srcf).resolve()
        if not sp.is_file() or norm(srclit) not in norm(sp.read_text()):
            print(f"{rid}: SOURCE LITERAL NOT FOUND in {srcf}: {srclit!r}"); fails += 1; failed.add(rid)
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
    base = "origin/main"
    ledger = HERE / "ledger.tsv"
    if "--base" in args:
        i = args.index("--base"); base = args[i + 1]; del args[i:i + 2]
    if "--ledger" in args:
        i = args.index("--ledger"); ledger = Path(args[i + 1]); del args[i:i + 2]
    wt = Path(args[0]).resolve()
    if self_test:
        bad = "SELFTEST\tsec_3d.tex\tindicative distance is $\\chi^{2}/\\mathrm{ndf}=4.98$\t-\tre1/RE1-REPORT-2.md\t**4.52**\n"
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as t:
            t.write(ledger.read_text() + bad)
        n, fails, failed = check_rows(wt, Path(t.name))
        print(f"SELF-TEST: {n} rows, failed ids {sorted(failed)}")
        if failed != {"SELFTEST"}:
            print("SELF-TEST :: FAIL (want exactly the planted row to fail)"); sys.exit(1)
        print("SELF-TEST :: PASS (the planted bad probe fails)"); sys.exit(0)
    n, fails, _ = check_rows(wt, ledger)
    fails += check_figs(wt)
    fails += check_protected(wt, base)
    print(f"LEDGER :: {'PASS' if not fails else 'FAIL'} ({n} rows, {fails} failures)")
    sys.exit(1 if fails else 0)


main()
