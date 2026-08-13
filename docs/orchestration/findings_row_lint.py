#!/usr/bin/env python3
"""Two pre-commit checks over the ledgers, chosen because they enforce rules that ALREADY EXIST.

WHY THIS FILE EXISTS RATHER THAN A CONVENTION PARAGRAPH. A document costs tokens in every future
session forever; a check costs zero and cannot be skipped. Every rule this campaign enforced by
attention on 2026-08-12/13 was broken at least once by the session that had just written it down --
so where a rule is expressible as a check, the check is the correct artifact and the paragraph is
not.

CHECK 1 -- LONG-FORM MUST LIVE ELSEWHERE AND BE POINTED AT.
  The invariant is CLAUDE.md:28, verbatim: "Long-form detail is in sibling FINDING-<date>-<slug>.md
  files, indexed at the top of FINDINGS.md."
  It is NOT a byte target and this check sets none. It flags a BEN row that is long AND carries no
  pointer to its long form. A long row that points at its detail file PASSES; a long row that
  swallowed its own detail FAILS.

  WHY NOT A LENGTH CAP. On 2026-08-13 a "300 B cap, already in CLAUDE.md" was asserted and acted on;
  no such rule existed anywhere in the repo. The observed one-liner median (231 B) is an artifact of
  earlier rows having SHORTER OPENING CLAUSES, not a bar later rows missed -- and codifying it would
  make missing it a violation, which invites rewriting an author's protected verbatim clause to buy
  ~18 bytes. THRESHOLD here is deliberately GENEROUS and is a trigger for "where is your long form",
  never a target to sit under.

CHECK 2 -- RETRACTED LITERALS MUST NOT COME BACK.
  INDEX-retracted-and-superseded-values.md exists because retracted numbers kept being requoted.
  Measured cost of that class on one night: `188x` was reintroduced by two sessions independently,
  and a third (this one) re-derived it from scratch as `79x` -- same wrong denominator, three times.

  ITS COVERAGE IS ONE OF THREE FAILURE MODES AND THE DOCSTRING SAYS SO, because a check trusted
  further than it goes is worse than none:
    CAUGHT     a retracted VALUE reappearing as a literal.
    NOT CAUGHT a right number with a wrong RELATIONSHIP -- e.g. `0.48x` labelled "gap / sd" when
               that quotient is 0.97 and 0.48 is a distance-from-mean. Four artifacts carried it.
    NOT CAUGHT a real line number with wrong SEMANTICS -- e.g. citing train_fullevent_nominal.py:252
               as "fails closed on replicas" when it guards the target receipt in the opposite
               direction. Both were caught by a peer re-deriving from the artifact, not by matching.

Exit codes:  0 clean  /  1 a check failed  /  2 cannot check (missing input; NOT a pass)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent               # derived from __file__, never hardcoded (the p4_evidence.py lesson)

FINDINGS = REPO / "docs/orchestration/FINDINGS.md"
RETRACT_INDEX = REPO / "docs/orchestration/INDEX-retracted-and-superseded-values.md"

BEN_ROW = re.compile(r"^\|\s*(BEN-\d+)\s*\|")
# A pointer to long form, in any of the three shapes the repo actually uses.
POINTER = re.compile(r"\[full\]\(|FINDING-20\d{6}|\[detail\]\(")
# Deliberately generous: a trigger for "where is your long form", not a length target.
LONG_ROW_BYTES = 600


def check_longform_pointers(findings: Path = FINDINGS, threshold: int = LONG_ROW_BYTES) -> int:
    if not findings.exists():
        print(f"LONGFORM :: CANNOT CHECK -- {findings} missing. Nothing was verified; this is NOT a pass.")
        return 2
    rows = [(m.group(1), ln.rstrip())
            for ln in findings.read_text(encoding="utf-8").splitlines()
            if (m := BEN_ROW.match(ln))]
    if not rows:
        print("LONGFORM :: CANNOT CHECK -- no BEN rows parsed. A check over zero rows is not a pass.")
        return 2
    offenders = [(i, len(l.encode())) for i, l in rows
                 if len(l.encode()) > threshold and not POINTER.search(l)]
    # Print the denominator ALWAYS -- "0 offenders" and "we never looked" must not read alike.
    print(f"LONGFORM :: {len(rows)} rows scanned, {sum(1 for _, l in rows if POINTER.search(l))} carry a pointer, "
          f"{len(offenders)} long-without-pointer (trigger {threshold} B)")
    for i, b in offenders:
        print(f"  FAIL {i} is {b} B and points at no long form. "
              f"Move the detail to FINDING-<date>-<slug>.md, index it at the top of FINDINGS.md, "
              f"and link it. CLAUDE.md:28. This is NOT a request to shorten prose.")
    print("LONGFORM :: " + ("PASS" if not offenders else "FAIL"))
    return 1 if offenders else 0


def retracted_literals(index: Path = RETRACT_INDEX) -> list[str]:
    """Literals the retraction index marks as dead. Parsed from its own rows, never hardcoded --
    a hardcoded copy would go stale exactly like the values it guards."""
    if not index.exists():
        return []
    out: list[str] = []
    for ln in index.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("|"):
            continue
        first = ln.split("|")[1] if ln.count("|") > 1 else ""
        for lit in re.findall(r"`([0-9][0-9.,]*(?:[eE][-+]?\d+)?x?)`", first):
            if len(lit.strip("`")) >= 3:
                out.append(lit)
    return sorted(set(out))


def check_retracted(paths: list[Path], index: Path = RETRACT_INDEX) -> int:
    lits = retracted_literals(index)
    if not lits:
        print(f"RETRACTED :: CANNOT CHECK -- no literals parsed from {index.name}. NOT a pass.")
        return 2
    hits = []
    for p in paths:
        if not p.exists() or p.resolve() == index.resolve():
            continue          # the index itself must name them; that is its job
        text = p.read_text(encoding="utf-8", errors="replace")
        for i, ln in enumerate(text.splitlines(), 1):
            if "RETRACTED" in ln or "DO_NOT_QUOTE" in ln or "superseded" in ln.lower():
                continue      # an occurrence that carries its own warning is the correct form
            for lit in lits:
                if lit in ln:
                    hits.append((p, i, lit))
    print(f"RETRACTED :: {len(lits)} retracted literals known, {len(paths)} file(s) scanned, {len(hits)} hit(s)")
    for p, i, lit in hits[:20]:
        # relative_to() RAISES for a path outside REPO, and this is an ERROR path -- so the crash
        # only appears when there IS a hit. Found by the self-test, which uses tempfiles. A guard
        # that dies while reporting a violation reports nothing.
        try:
            shown = p.relative_to(REPO)
        except ValueError:
            shown = p
        print(f"  FAIL {shown}:{i} reintroduces retracted literal {lit!r} "
              f"with no adjacent retraction marker. See {index.name}.")
    print("RETRACTED :: " + ("PASS" if not hits else "FAIL"))
    print("  COVERAGE NOTE: this catches a retracted VALUE reappearing. It does NOT catch a right "
          "number with a wrong relationship, nor a real line number with wrong semantics. Both "
          "happened on 2026-08-13 and both were caught by a peer re-deriving from the artifact.")
    return 1 if hits else 0


def self_test() -> int:
    import tempfile, os
    checks, fails = 0, 0

    def case(label, got, want):
        nonlocal checks, fails
        checks += 1
        ok = got == want
        if not ok:
            fails += 1
            print(f"  FAIL {label}  (got {got!r} want {want!r})")
        else:
            print(f"  ok   {label}")

    fd, tmp = tempfile.mkstemp(suffix=".md"); os.close(fd)
    t = Path(tmp)

    # long + pointer -> PASS; long + no pointer -> FAIL; short + no pointer -> PASS.
    long_body = "x" * 700
    t.write_text(
        "| id | finding |\n|---|---|\n"
        f"| BEN-001 | {long_body} [full](FINDINGS-ARCHIVE-2026-08.md) |\n"
        f"| BEN-002 | {long_body} |\n"
        "| BEN-003 | short, no pointer |\n"
        f"| BEN-004 | {long_body} see FINDING-20260812-thing.md |\n"
        f"| BEN-005 | {long_body} [detail](FINDING-x.md) |\n", encoding="utf-8")
    case("long row WITH [full] passes, long row WITHOUT fails, short row passes",
         check_longform_pointers(t), 1)

    t.write_text("| id | finding |\n|---|---|\n| BEN-001 | short |\n", encoding="utf-8")
    case("no long rows at all -> PASS (0)", check_longform_pointers(t), 0)

    # A file with no BEN rows must be CANNOT-CHECK, not a pass -- the vacuous-pass rule.
    t.write_text("# prose only, no table\n", encoding="utf-8")
    case("zero BEN rows -> CANNOT CHECK (2), never 0", check_longform_pointers(t), 2)

    case("missing file -> CANNOT CHECK (2)", check_longform_pointers(Path(tmp + ".nope")), 2)

    # retracted-literal parsing + the warning-carrying exemption
    fd2, idx = tempfile.mkstemp(suffix=".md"); os.close(fd2)
    Path(idx).write_text(
        "| dead | superseded by |\n|---|---|\n| **`188.4x`** / `188x` | `0.48x` |\n", encoding="utf-8")
    lits = retracted_literals(Path(idx))
    case("literals parsed from the index rather than hardcoded", "188x" in lits, True)

    fd3, doc = tempfile.mkstemp(suffix=".md"); os.close(fd3)
    Path(doc).write_text("the gap was 188x the scatter\n", encoding="utf-8")
    case("bare reintroduction FAILS", check_retracted([Path(doc)], Path(idx)), 1)
    Path(doc).write_text("the RETRACTED figure 188x is shown only to identify the error\n", encoding="utf-8")
    case("occurrence carrying its own RETRACTED marker PASSES", check_retracted([Path(doc)], Path(idx)), 0)

    for f in (tmp, idx, doc):
        os.unlink(f)
    print(f"self-test: {checks - fails} passed, {fails} failed")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--longform", action="store_true", help="check 1 only")
    ap.add_argument("--retracted", nargs="*", metavar="FILE", help="check 2 over these files")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.longform:
        return check_longform_pointers()
    if a.retracted is not None:
        files = [Path(x) for x in a.retracted] or [FINDINGS]
        return check_retracted(files)
    rc1 = check_longform_pointers()
    return rc1


if __name__ == "__main__":
    sys.exit(main())
