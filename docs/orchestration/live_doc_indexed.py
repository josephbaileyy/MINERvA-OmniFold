#!/usr/bin/env python3
"""Guard: a document this commit declares LIVE must be reachable from CATALOG.md.

    python3 docs/orchestration/live_doc_indexed.py --check       # the gate (pre-commit)
    python3 docs/orchestration/live_doc_indexed.py --self-test   # both directions, synthetic
    python3 docs/orchestration/live_doc_indexed.py --backlog     # pre-existing violations, no exit code

WHY THIS EXISTS. On 2026-08-17 `RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md` was
committed LIVE and **pre-commit printed "7 checks passed" while the document was in no index at all.**
The pointer was added because a peer asked, not because the mechanism caught it. `CLAUDE.md` records
nine findings that sat orphaned exactly that way, and `CONVENTION-document-retention.md:36` already
requires the declaration -- what was missing is the check. Same shape as `KNOWN_ISSUES 48`
(`verify_receipt_artifacts.py` reads green on precisely the case it does not cover), so the remedy is
the executable form per `CLAUDE.md`: a document costs tokens in every future session forever, a check
costs zero and cannot be skipped.

WHAT IT CHECKS, precisely, and the classification comes from the CLASSIFICATION PATH rather than the
filename -- so a doc cannot be exempted by naming it something else, and `ARCHIVAL` docs are never
touched:

  a document is IN SCOPE if this commit makes it newly LIVE, by either route --
    (1) the .md file is newly ADDED under docs/orchestration/ and its staged
        MANIFEST-overrides.tsv row says LIVE, or
    (2) its overrides row is LIVE in the staged file and was NOT LIVE at HEAD
        (a reclassification, which is the other way a doc becomes LIVE)
  and it PASSES if its basename appears anywhere in CATALOG.md.

SCOPED TO THIS COMMIT ON PURPOSE, and the number is why. Measured before writing: **3 of the 24
currently-LIVE `.md` docs are absent from `CATALOG.md`** -- `CATALOG.md` itself (a router need not route
to itself; exempt below), plus `CONVENTION-document-retention.md` and
`SPEC-20260814-gate5-cstat-construction-v1.md`, which are real. A whole-tree gate would therefore fail
**every lane's next commit** on debt none of them created -- the trap C named for `pipefail`: a check
that goes red the moment it is installed gets routed around. So this enforces forward and REPORTS the
backlog rather than hiding it (`--backlog`, and the count is printed on every run). Widening it to
whole-tree is a one-line change once those two are indexed, and that is deliberately somebody's
decision rather than this file's.

WHAT IT CANNOT DO, stated so a green run is not over-read: **it cannot detect a document that SHOULD be
LIVE but was never declared.** With no overrides row the generator defaults to `ARCHIVAL`
(`generate_manifest.py:145`), so an undeclared doc is out of scope and this check is silent. It enforces
consistency between the author's declaration and the router, not the correctness of the declaration.

COST: two small file reads plus two `git show`s. No generator -- regenerating `MANIFEST.tsv` would be
far too expensive for a hook and is independently ~140 lines stale anyway. Measured runtime is printed
by --self-test.
"""
import os
import subprocess
import sys

OVERRIDES = "docs/orchestration/MANIFEST-overrides.tsv"
CATALOG = "docs/orchestration/CATALOG.md"
DOCDIR = "docs/orchestration/"
# CATALOG.md is the router itself. A router that must list itself to be reachable is a tautology, and
# the alternative (adding a self-referential row) makes the index worse to read.
EXEMPT = {"CATALOG.md"}


def live_paths(overrides_text):
    """The set of paths the overrides file classifies LIVE. This IS the classification path."""
    out = set()
    for line in overrides_text.splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 2 and f[1].strip() == "LIVE":
            out.add(f[0].strip())
    return out


def in_scope(added_md, staged_live, head_live):
    """Docs this commit makes newly LIVE, by either route. Sorted for a stable message."""
    newly_added = {p for p in added_md if p in staged_live}
    reclassified = {p for p in staged_live if p not in head_live and p.endswith(".md")}
    return sorted((newly_added | reclassified) - {DOCDIR + e for e in EXEMPT})


def unindexed(paths, catalog_text):
    return [p for p in paths if os.path.basename(p) not in catalog_text]


def _git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def backlog():
    """Pre-existing LIVE docs absent from CATALOG.md. Reported, never enforced here."""
    try:
        ov = open(OVERRIDES).read()
        cat = open(CATALOG).read()
    except OSError as e:
        return None, f"cannot read the index files: {e}"
    live = {p for p in live_paths(ov) if p.endswith(".md")}
    live -= {DOCDIR + e for e in EXEMPT}
    return sorted(os.path.basename(p) for p in live if os.path.basename(p) not in cat), None


def check():
    added = [l.split("\t")[1] for l in _git("diff", "--cached", "--name-status",
                                            "--diff-filter=A").splitlines()
             if "\t" in l]
    added_md = [p for p in added if p.startswith(DOCDIR) and p.endswith(".md")]

    staged_ov = _git("show", ":" + OVERRIDES) or (open(OVERRIDES).read()
                                                  if os.path.exists(OVERRIDES) else "")
    head_ov = _git("show", "HEAD:" + OVERRIDES)
    if not staged_ov:
        # NOT a pass. Distinguish "nothing to check" from "could not look" -- an empty read and a
        # clean tree are different claims, which is the defect that shipped in shared_push.sh tonight.
        print("LIVE-INDEX :: CANNOT CHECK -- the overrides file could not be read from the index")
        return 2

    scope = in_scope(added_md, live_paths(staged_ov), live_paths(head_ov))
    bl, err = backlog()
    bl_note = ("  (pre-existing, NOT enforced: %d LIVE doc(s) absent from CATALOG -- %s)"
               % (len(bl), ", ".join(bl)) if bl else "  (no pre-existing backlog)") if not err else \
              "  (backlog unreadable: %s)" % err

    if not scope:
        print("LIVE-INDEX :: nothing newly LIVE in this commit." + bl_note)
        return 0
    bad = unindexed(scope, open(CATALOG).read())
    if bad:
        print("LIVE-INDEX :: FAIL -- %d document(s) declared LIVE by this commit are not reachable "
              "from CATALOG.md:" % len(bad))
        for p in bad:
            print("    %s" % p)
        print("  Add a pointer row to docs/orchestration/CATALOG.md in THIS commit. An unindexed LIVE "
              "document is one nobody reads -- CLAUDE.md records nine that sat orphaned.")
        print("  If it should not be LIVE, fix the class in MANIFEST-overrides.tsv instead; do not "
              "misclassify to silence this.")
        print(bl_note)
        return 1
    print("LIVE-INDEX :: OK -- %d newly-LIVE document(s) reachable from CATALOG.md (%s)"
          % (len(scope), ", ".join(os.path.basename(p) for p in scope)) + bl_note)
    return 0


def self_test():
    """POWER-TESTED BOTH DIRECTIONS. A guard shown only to pass proves nothing; lane B's bar is that a
    test which also passes on the broken input tests nothing. Every case is synthetic -- no repo state."""
    import time
    t0 = time.time()
    HDR = "path\tclass\tevent_status\tcanonical_successor\n"
    NEW = DOCDIR + "NEWDOC-20260817-x.md"
    fails = []

    def ck(label, ok, detail=""):
        print(("  PASS  " if ok else "  FAIL  ") + label + (" :: " + detail if detail else ""))
        if not ok:
            fails.append(label)

    staged = HDR + NEW + "\tLIVE\topen\t\n"
    # 1. the defect this exists for: added, LIVE, absent from CATALOG -> must be caught
    s = in_scope([NEW], live_paths(staged), live_paths(HDR))
    ck("a newly-added LIVE doc absent from CATALOG is CAUGHT",
       s == [NEW] and unindexed(s, "| some other row |") == [NEW])
    # 2. and present -> must pass. Without this the check could be "always fail" and case 1 would pass.
    ck("the same doc PRESENT in CATALOG passes",
       unindexed(s, "| route | [`NEWDOC-20260817-x.md`](NEWDOC-20260817-x.md) |") == [])
    # 3. ARCHIVAL must never be in scope -- the requirement that it not become a rule people route
    #    around by misclassifying, and it must be read from the CLASS not the filename.
    arch = HDR + NEW + "\tARCHIVAL\tterminal\t\n"
    ck("an ARCHIVAL doc is NOT in scope", in_scope([NEW], live_paths(arch), live_paths(HDR)) == [])
    # 4. no overrides row at all -> out of scope (generator default is ARCHIVAL)
    ck("an UNDECLARED doc is NOT in scope", in_scope([NEW], live_paths(HDR), live_paths(HDR)) == [])
    # 5. reclassification route: file not newly added, but its row became LIVE this commit
    old = HDR + NEW + "\tARCHIVAL\tterminal\t\n"
    ck("ARCHIVAL -> LIVE reclassification IS in scope",
       in_scope([], live_paths(staged), live_paths(old)) == [NEW])
    # 6. a row that was ALREADY LIVE at HEAD is not re-litigated
    ck("an already-LIVE doc is NOT re-checked", in_scope([], live_paths(staged), live_paths(staged)) == [])
    # 7. CATALOG.md itself is exempt
    catrow = HDR + DOCDIR + "CATALOG.md\tLIVE\topen\t\n"
    ck("CATALOG.md is exempt from routing to itself",
       in_scope([DOCDIR + "CATALOG.md"], live_paths(catrow), live_paths(HDR)) == [])
    # 8. classification is read from the CLASS COLUMN, not from a filename that merely says LIVE
    tricky = HDR + DOCDIR + "LIVE-looking-name.md\tARCHIVAL\tterminal\t\n"
    ck("a doc NAMED 'LIVE-*' but classed ARCHIVAL is NOT in scope",
       in_scope([DOCDIR + "LIVE-looking-name.md"], live_paths(tricky), live_paths(HDR)) == [])
    # 9. a malformed row must not crash or silently classify as LIVE
    ck("a malformed overrides row is ignored, not treated as LIVE",
       live_paths(HDR + "garbage-with-no-tabs\n") == set())

    dt = time.time() - t0
    print()
    if fails:
        print("SELF-TEST :: FAILED -> %s" % fails)
        return 1
    print("SELF-TEST :: 9/9 PASS in %.3f s (synthetic; no repo state touched)" % dt)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:] or ["--check"]
    if "--self-test" in a:
        raise SystemExit(self_test())
    if "--backlog" in a:
        bl, err = backlog()
        if err:
            print("backlog :: %s" % err)
            raise SystemExit(2)
        print("pre-existing LIVE docs absent from CATALOG.md: %d" % len(bl))
        for b in bl:
            print("    %s" % b)
        raise SystemExit(0)
    raise SystemExit(check())
