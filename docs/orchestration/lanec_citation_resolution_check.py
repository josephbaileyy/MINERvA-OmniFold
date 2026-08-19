#!/usr/bin/env python3
"""Lane C — every path citation in a lane-C ruling must resolve to EXACTLY ONE tracked file.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH
----------------------------------------
`CLAUDE.md`: *"a document costs tokens in every future session forever; a check costs zero
and cannot be skipped. Prefer the executable form of any rule you are tempted to write
down."*  The rule this enforces was going to be a prose amendment; it is this instead.

WHAT IT CATCHES, and why each half is needed
--------------------------------------------
1. UNRESOLVED — a citation naming no tracked file.  A ruling that cites a path which does
   not exist cannot be checked by anybody.
2. AMBIGUOUS — a BARE BASENAME matching two or more tracked paths.  This is `BEN-380`'s
   species (*a definite description re-points as soon as a second file satisfies it*) and it
   is the one that actually fired: `RULING-20260817-lanec-unity-factor-diagnostic-is-admissible.md`
   cited `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`, which matches FOUR tracked paths — one live
   and three `superseded-*`.  All four happened to carry the quoted values, so the claim was
   right BY LUCK AND NOT BY METHOD.  That is exactly the condition a check should remove.

WHY IT ALSO CARRIES FIXTURES
----------------------------
A filter needs a test in the direction it acts.  A resolution check that silently passes
because its own token regex matched nothing is indistinguishable from one that passes
because every citation resolved.  The regex here replaced one that matched `np.shares_memory`
as `np.sh` and `sig_full.shape` as `sig_full.sh` — a substring test cannot express "the
extension ENDS the token" — so `self_check()` asserts BOTH that real defects are detected
and that those two expressions are NOT.  Run with `--self-check` alone to exercise only that.

EXIT: 0 = every citation resolves uniquely.  1 = at least one unresolved or ambiguous.
      2 = the instrument itself failed its fixtures, which invalidates any verdict above.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC_DIR = REPO / "docs" / "orchestration"

# A citation token: a filename with a known extension, where the extension ENDS the token.
# `(?![A-Za-z0-9_])` is the whole point — see the module docstring's regex note.
# SCOPE: REPO OBJECTS ONLY.  `.root` and `.npz` are deliberately EXCLUDED, and this is a
# narrowing with a reason rather than a convenience: those are cluster DATA PRODUCTS living
# under `$MNV_REPO` on purgeable scratch, never tracked by git, so "resolves to a tracked
# file" is the wrong predicate for them and would fail forever on correct citations.  The
# first version of this check included them and reported 12 problems of which 10 were that
# false positive — 17% precision.  A check that cries wolf gets disabled, which is worse than
# not having it.  The two scope entries in `self_check`'s `must_not_match` lock this in the
# negative direction.  (That comment first cited a test function that did not exist — the very
# defect this script detects, committed inside the script. Caught by re-reading, not by the check,
# because the check reads DOCUMENTS and not its own source.  A known blind spot, stated.)
CITATION = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|tsv|py|sh|json))"
    r"(?![A-Za-z0-9_])"
)

# Tokens that LOOK like paths and are not.  Each needs a reason; an unreasoned entry here is
# how a real defect gets suppressed, so the tuple is (token, reason) and the reason is printed.
ALLOWLIST: dict[str, str] = {
    "SPEC-...md": "prose ellipsis standing for a class of spec filenames, not a citation",
    "gate5_cstat_contract_v2.json": "names a PROPOSED future artifact, deliberately not yet created",
}


def tracked_files() -> set[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout
    return set(out.splitlines())


def lanec_documents() -> list[Path]:
    docs = sorted(DOC_DIR.glob("*lanec*.md"))
    mc = DOC_DIR / "mii_anchor_confound_mc.py"
    if mc.exists():
        docs.append(mc)
    return docs


def resolve(token: str, tracked: set[str]) -> tuple[str, list[str]]:
    """Return (verdict, matches).  verdict in {OK, UNRESOLVED, AMBIGUOUS}."""
    if token in tracked:
        return "OK", [token]
    hits = sorted(p for p in tracked if p.endswith("/" + token))
    if len(hits) == 1:
        return "OK", hits
    if not hits:
        return "UNRESOLVED", []
    return "AMBIGUOUS", hits


def scan(tracked: set[str]) -> tuple[list[tuple], int, int]:
    problems: list[tuple] = []
    n_docs = 0
    n_citations = 0
    for doc in lanec_documents():
        n_docs += 1
        text = doc.read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for m in CITATION.finditer(text):
            token = m.group(1)
            if token in seen or token in ALLOWLIST:
                continue
            seen.add(token)
            n_citations += 1
            verdict, hits = resolve(token, tracked)
            if verdict != "OK":
                line = text.count("\n", 0, m.start()) + 1
                problems.append((doc.name, line, token, verdict, hits))
    return problems, n_docs, n_citations


def self_check() -> bool:
    """Prove the instrument fires, and prove it does NOT fire on the known false positives."""
    ok = True

    must_match = [
        "docs/orchestration/FINDINGS.md",
        "MANIFEST.tsv",
        "unified_throw_cov.py",
        "sbatch_uthrow_run_5d_fast.sh",
        "receipt_construction_contract_5d.json",
    ]
    for token in must_match:
        if not CITATION.fullmatch(token):
            print(f"  SELF-CHECK FAIL: should be a citation but is not matched: {token}")
            ok = False

    # The regression this regex exists for.  A substring test matched these as `.sh` paths.
    must_not_match = [
        "np.shares_memory", "sig_full.shape", "arr.shape", "obj.json_repr",
        # scope fixture: cluster data products are out of scope by design, see CITATION above
        "uq_5d/unified_throw_cov_5d.root", "GATE5_REPLICA_WEIGHTS.npz",
    ]
    for expr in must_not_match:
        hits = [m.group(1) for m in CITATION.finditer(expr)]
        if hits:
            print(f"  SELF-CHECK FAIL: attribute access read as a path: {expr} -> {hits}")
            ok = False

    # The detector must actually detect: a synthetic ambiguity and a synthetic absence.
    fake = {"a/dup.md", "b/dup.md", "c/only.md"}
    if resolve("dup.md", fake)[0] != "AMBIGUOUS":
        print("  SELF-CHECK FAIL: two matching basenames not reported AMBIGUOUS")
        ok = False
    if resolve("absent.md", fake)[0] != "UNRESOLVED":
        print("  SELF-CHECK FAIL: a nonexistent path not reported UNRESOLVED")
        ok = False
    if resolve("only.md", fake)[0] != "OK":
        print("  SELF-CHECK FAIL: a unique basename not reported OK")
        ok = False

    print(f"  self-check: {'PASS' if ok else 'FAIL'} "
          f"({len(must_match)} positive, {len(must_not_match)} negative, 3 resolver fixtures)")
    return ok


def main() -> int:
    only_self = "--self-check" in sys.argv
    print("lane-C citation resolution check")
    if not self_check():
        print("INSTRUMENT FAILED ITS FIXTURES — no verdict below is trustworthy.")
        return 2
    if only_self:
        return 0

    tracked = tracked_files()
    problems, n_docs, n_citations = scan(tracked)
    print(f"  scanned {n_docs} lane-C documents, {n_citations} distinct citations, "
          f"{len(tracked)} tracked files")
    if ALLOWLIST:
        print(f"  allowlisted (with reasons), {len(ALLOWLIST)}:")
        for token, reason in ALLOWLIST.items():
            print(f"    {token} — {reason}")

    if not problems:
        print("PASS: every citation resolves to exactly one tracked file.")
        return 0

    print(f"\nFAIL: {len(problems)} citation(s) do not resolve uniquely.")
    for name, line, token, verdict, hits in problems:
        print(f"  {name}:{line}  {verdict}  {token}")
        for h in hits:
            print(f"      candidate: {h}")
    print("\nRepair by writing the full repo-relative path, not the basename. A bare basename is\n"
          "BEN-380's species: it re-points the moment a second file satisfies it.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
