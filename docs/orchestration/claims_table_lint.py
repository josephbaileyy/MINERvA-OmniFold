#!/usr/bin/env python3
"""Field-count lint for CLAIMS.md's CLM table, and for the one conjunct a row can refute itself on.

WHY THIS EXISTS AND WHY IT IS NOT HARDENING A CONSUMER. `CLM-006` shipped with four stray pipes --
two pairs of absolute-value bars, `|FE/recoil-only-1|` and `|FE/prior-1|` -- written as literal `|`
inside the `evidence artifact` cell. Every column after the break shifted, so the row's
`independent verifier` field read a percentage. It was found by a human counting fields for an
unrelated purpose, and lane A then established that NO column-indexed consumer of `CLAIMS.md` exists
anywhere in the repo: every `split("|")` in every tracked `.py` was resolved individually and none
touches this file.

That inverts the usual case rather than removing it. There is no blind parser to protect -- THIS IS
THE ONLY THING THAT WOULD EVER NOTICE. The file's correctness is currently maintained by nobody
parsing it. And on a file with zero parsers the assertion carries no regression risk, because there
is nothing that could break (lane A's review lane).

TWO CHECKS, and the second is not a formatting one:

  1. FIELD COUNT. Every `| CLM-...` row has exactly as many between-pipe fields as the header.
     Counted BETWEEN the pipes, matching the nine named headers -- not `len(line.split("|"))`, which
     counts the empty strings outside the leading and trailing pipes and reports 13-vs-9 as 15-vs-11
     (`BEN-443`; A corrected its own number and the delta was identical either way, but the base has
     to have its convention stated).

  2. SELF-REFUTED STATUS. `CLAIMS.md:4` requires "a recoverable artifact + an independent check" for
     promotion. A row whose `independent verifier` field DECLARES the second conjunct unmet -- e.g.
     "single-source", "has NOT been independently checked" -- while carrying a promoted status is
     refuted by its own row. The declaration may be PARTIAL and it still fails -- and PARTIAL vs
     WHOLLY is derived from the row's OWN text (does the self-declaration open the field, or follow
     other content?), never from a hardcoded example, because a message naming another row asserts
     that row's facts about this one. That is a
     different defect from a verifier field naming an unrecoverable identity ("me", "this session"):
     there we cannot TELL whether the leg was satisfied, here the row TELLS US it was not. Opposite
     epistemic states, so they get different treatment -- this one fails, that one is reported.

Exit 0 clean, 1 on any failure. Read-only.
"""
from __future__ import annotations

import pathlib
import re
import sys

CLAIMS = pathlib.Path(__file__).resolve().parent / "CLAIMS.md"

PROMOTED = {"PROVED", "VERIFIED-NUMERIC", "VERIFIED-CODE"}
# Phrases in which a row states, of itself, that no independent check was made. Matched
# case-insensitively against the `independent verifier` cell.
SELF_DECLARED_SINGLE_SOURCE = ("single-source", "single source", "no independent")
# Verifier identities that no longer resolve to anything askable. Reported, never failed: the
# artifact leg survives and only the independence leg becomes unverifiable, so failing here would
# demote on a records defect rather than an evidence defect.
UNRECOVERABLE_IDENTITY = re.compile(r"\b(me|this session|myself)\b", re.I)


def fields(line: str) -> list[str]:
    """Between-pipe fields. `| a | b |` -> ['a', 'b'] -- two, not four."""
    return [c.strip() for c in line.split("|")[1:-1]]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = pathlib.Path(argv[0]) if argv else CLAIMS
    lines = path.read_text(encoding="utf-8").split("\n")

    header_idx = next((i for i, l in enumerate(lines)
                       if l.startswith("|") and "independent verifier" in l.lower()), None)
    if header_idx is None:
        print(f"CLAIMS-LINT :: FAIL  no header row carrying 'independent verifier' in {path}")
        return 1
    header = fields(lines[header_idx])
    n = len(header)
    try:
        vcol = [h.lower() for h in header].index("independent verifier")
        scol = [h.lower() for h in header].index("status")
    except ValueError:
        print("CLAIMS-LINT :: FAIL  header lacks a 'status' or 'independent verifier' column")
        return 1

    rows = [(i + 1, l) for i, l in enumerate(lines) if l.startswith("| CLM-")]
    if not rows:
        print(f"CLAIMS-LINT :: FAIL  zero `| CLM-` rows found in {path} -- a lint that finds "
              f"nothing to lint is not a pass")
        return 1

    bad_count, self_refuted, unrecoverable = [], [], []
    for lineno, line in rows:
        f = fields(line)
        cid = f[0] if f else "?"
        if len(f) != n:
            bad_count.append((lineno, cid, len(f)))
            continue                      # column indices are meaningless once the row is shifted
        verifier, status = f[vcol], f[scol]
        hits = [verifier.lower().find(p) for p in SELF_DECLARED_SINGLE_SOURCE]
        first = min([h for h in hits if h >= 0], default=-1)
        if status in PROMOTED and first >= 0:
            # PARTIAL vs WHOLLY is derived from THIS row's own text -- whether the self-declaration
            # opens the field or follows other content. Never from a hardcoded example: a message
            # that names another row asserts that row's facts about this one (lane A, BEN-382's
            # shape at the finest scale -- the row's evidence not bound to the row).
            scope = "WHOLLY single-source" if first <= 4 else "PARTIAL (the field names something else first)"
            self_refuted.append((lineno, cid, status, scope, verifier[:110]))
        if UNRECOVERABLE_IDENTITY.search(verifier):
            unrecoverable.append((lineno, cid, verifier[:70]))

    print(f"CLAIMS-LINT :: header {n} fields at line {header_idx + 1}; {len(rows)} CLM rows scanned")
    for lineno, cid, got in bad_count:
        print(f"  FAIL {cid} (line {lineno}) has {got} between-pipe fields, header has {n}. "
              f"A literal `|` inside a cell splits the row; escape it as `&#124;`, NOT as `\\|` -- "
              f"a backslash fixes the renderer and leaves the pipe byte, so a naive split still "
              f"mis-counts.")
    for lineno, cid, status, scope, verifier in self_refuted:
        print(f"  FAIL {cid} (line {lineno}) status {status}, and its own `independent verifier` "
              f"declares the independent-check leg unmet -- {scope}: {verifier!r}. A promoted "
              f"status resting even PARTLY on a self-declared unchecked component is unsupported; "
              f"CLAIMS.md:4 requires a recoverable artifact AND an independent check. Supply the "
              f"check, or split the row so the status attaches to the claim the evidence covers. "
              f"Do not quote the status meanwhile.")
    for lineno, cid, verifier in unrecoverable:
        print(f"  note {cid} (line {lineno}) verifier identity does not resolve: {verifier!r}. "
              f"Not a failure -- the artifact leg survives. But it may not serve as the "
              f"independent leg for any FUTURE promotion, and new rows must name a lane role or an "
              f"artifact path, never a session.")

    if bad_count or self_refuted:
        print("CLAIMS-LINT :: FAIL")
        return 1
    print("CLAIMS-LINT :: PASS"
          + (f" ({len(unrecoverable)} unresolvable verifier identities noted)" if unrecoverable else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
