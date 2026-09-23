#!/usr/bin/env python3
"""Guard: a document this commit declares LIVE must be reachable from CATALOG.md.

    python3 docs/orchestration/live_doc_indexed.py --check       # the gate (pre-commit); WHOLE-TREE since 2026-09-21
    python3 docs/orchestration/live_doc_indexed.py --self-test   # both directions, synthetic
    python3 docs/orchestration/live_doc_indexed.py --backlog     # pre-existing violations, no exit code
    python3 docs/orchestration/live_doc_indexed.py --unrowed     # whole tree: docs with NO overrides row; exit 1 if any

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

⚠ **NO LONGER SCOPED TO THIS COMMIT. The whole-tree arm ENFORCES as of 2026-09-21**, which is the
one-line widening the paragraph below said was somebody's decision. It was taken after the backlog
was driven to **zero** — all twelve remaining documents were indexed in `CATALOG.md` in the same
commit — so the trap the paragraph names is disarmed: this does not go red the moment it is
installed, and a red from it now is NEW debt. The historical reasoning is kept verbatim because it
is the reason the widening had to wait, not a reason it was wrong.

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

THE UNDECLARED HOLE, NARROWED 2026-09-23 (KNOWN_ISSUES row 60, part 3). Both arms above intersect the
LIVE rows, so a document that never receives ANY overrides row was outside this check permanently --
`OUTCOME-20260921-L2-probe-blocked-at-stage-4.md` landed in `15edf148` with no row and no pointer, and
every later run said "nothing newly LIVE". Two additions, split by the hook's admitting rule:
  * ENFORCED, forward: a `.md` this commit ADDS under docs/orchestration/ (outside runs/ and state/)
    must have a row in the staged overrides file -- any class. The committer can always satisfy it,
    because ARCHIVAL is a legal declaration; what is refused is declaring nothing.
  * WHOLE TREE: every tracked `.md` in that scope with no row is counted on every `--check` and listed
    by `--unrowed`, which exits 1 while any exist. 106 such documents pre-dated this (measured at
    `aeb6668c`, `OUTCOME-20260921-L2-…` among them). All 106 were classified on 2026-09-23 (106 -> 0),
    and after that `--unrowed` became a HARD pre-commit check (`.githooks/pre-commit`, "every doc has an
    overrides row"). A red from it now is new debt, never inherited debt.
The judgement is still the author's -- a row saying ARCHIVAL passes -- so this makes the declaration
mandatory, not correct.

COST: two small file reads plus two `git show`s. No generator -- regenerating `MANIFEST.tsv` would be
far too expensive for a hook and is independently ~140 lines stale anyway. Measured runtime is printed
by --self-test.
"""
import os
import subprocess
import sys
from pathlib import Path

OVERRIDES = "docs/orchestration/MANIFEST-overrides.tsv"
CATALOG = "docs/orchestration/CATALOG.md"
DOCDIR = "docs/orchestration/"
# CATALOG.md is the router itself. A router that must list itself to be reachable is a tautology, and
# the alternative (adding a self-referential row) makes the index worse to read.
EXEMPT = {"CATALOG.md"}
# THE ROUTER MAY BE SPLIT, AND THE CONTINUATION FILES ARE DECLARED IN IT (2026-09-21).
# CATALOG.md reached ~4,270 lines, half of it two closed campaigns, and the fix is to move era
# history into separate files. This check read CATALOG.md ALONE and enforces whole-tree, so the
# split would have reddened the commit performing it -- the blocker named in CATALOG's own
# "THE SPLIT" section.
#
# DECLARED, NOT GLOBBED, and that is the whole safety property. A `CATALOG-*.md` glob would let any
# new file silently become an index, so a document could be "indexed" by a file nobody routes
# through -- which is the defect this check exists to prevent, arriving through its own fix.
# The declaration is a line in CATALOG.md:
#
#     <!-- CATALOG-CONTINUES: CATALOG-ARCHIVE-gate1-k0.md -->
#
# One per continuation file. A declared file that cannot be read is CANNOT CHECK, never a pass:
# an unreadable index is an inability to look, and this file's whole design distinguishes that
# from a clean result.
CONTINUATION_MARKER = "<!-- CATALOG-CONTINUES:"


def live_paths(overrides_text):
    """The set of paths the overrides file classifies LIVE. This IS the classification path."""
    out = set()
    for line in overrides_text.splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 2 and f[1].strip() == "LIVE":
            out.add(f[0].strip())
    return out


def row_paths(overrides_text):
    """Every path the overrides file declares, whatever its class."""
    out = set()
    for line in overrides_text.splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 2 and f[0].strip():
            out.add(f[0].strip())
    return out


def needs_row(path):
    """A document the retention convention requires a declared class for."""
    return (path.startswith(DOCDIR) and path.endswith(".md")
            and not path.startswith((DOCDIR + "runs/", DOCDIR + "state/"))
            and os.path.basename(path) not in EXEMPT)


def unrowed(paths, overrides_text):
    """Documents in `paths` that need an overrides row and have none. Sorted."""
    declared = row_paths(overrides_text)
    return sorted(p for p in paths if needs_row(p) and p not in declared)


def in_scope(added_md, staged_live, head_live):
    """Docs this commit makes newly LIVE, by either route. Sorted for a stable message."""
    newly_added = {p for p in added_md if p in staged_live}
    reclassified = {p for p in staged_live if p not in head_live and p.endswith(".md")}
    return sorted((newly_added | reclassified) - {DOCDIR + e for e in EXEMPT})


def declared_continuations(catalog_text):
    """Continuation filenames CATALOG.md declares, in declaration order. Bare names, no paths."""
    out = []
    for line in catalog_text.splitlines():
        line = line.strip()
        if not line.startswith(CONTINUATION_MARKER):
            continue
        name = line[len(CONTINUATION_MARKER):].split("-->")[0].strip()
        if name and name not in out:
            out.append(name)
    return out


def router_text(catalog_text, read=None):
    """(combined index text, error_or_None) for CATALOG.md plus every file it DECLARES.

    A declared-but-unreadable continuation returns an error rather than a short text, because the
    difference between "this document is not indexed" and "I could not read the index" is the
    distinction this whole file is built on.
    """
    read = read or (lambda name: Path(DOCDIR + name).read_text())
    parts = [catalog_text]
    for name in declared_continuations(catalog_text):
        try:
            parts.append(read(name))
        except OSError as exc:
            return None, f"CATALOG.md declares continuation {name!r} and it cannot be read: {exc}"
    return "\n".join(parts), None


def unindexed(paths, catalog_text):
    return [p for p in paths if os.path.basename(p) not in catalog_text]


def _git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def backlog(staged_ov=None, staged_cat=None, read_continuation=None):
    """Every LIVE .md absent from CATALOG.md. ENFORCED as of 2026-09-21; see the header.

    ⚠ READS THE INDEX, NOT THE WORKING TREE, when the caller supplies it. The working-tree read
    below is the fallback for `--backlog` outside a commit. A pre-commit hook that judged the
    working tree would answer a different question from the one the commit asks -- `git commit --
    <pathspec>` commits a subset of the tree, so the two genuinely differ -- and this file's own
    scoped arm has always used `git show :<path>` for exactly that reason. Making the whole-tree arm
    enforcing without matching it would have installed the inconsistency at the moment it started
    costing something.
    """
    try:
        ov = staged_ov if staged_ov is not None else open(OVERRIDES).read()
        cat = staged_cat if staged_cat is not None else open(CATALOG).read()
    except OSError as e:
        return None, f"cannot read the index files: {e}"
    # The router is CATALOG.md plus whatever it declares. A continuation that cannot be read is an
    # error, not a smaller index -- see router_text.
    cat, err = router_text(cat, read=read_continuation)
    if err:
        return None, err
    live = {p for p in live_paths(ov) if p.endswith(".md")}
    live -= {DOCDIR + e for e in EXEMPT}
    live -= {DOCDIR + n for n in declared_continuations(cat)}
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

    # UNDECLARED ARM (row 60, part 3). Forward-enforced; the whole-tree count is reported only.
    added_unrowed = unrowed(added_md, staged_ov)
    tree_unrowed = unrowed(_git("ls-files", "--", DOCDIR).splitlines(), staged_ov)
    if added_unrowed:
        print("LIVE-INDEX :: FAIL -- %d document(s) ADDED by this commit have NO row in "
              "MANIFEST-overrides.tsv:" % len(added_unrowed))
        for p in added_unrowed:
            print("    %s" % p)
        print("  Declare each one's class in docs/orchestration/MANIFEST-overrides.tsv in THIS "
              "commit (ARCHIVAL is a legal declaration). With no row it defaults to ARCHIVAL and is "
              "outside every arm of this check forever -- the 15edf148 shape.")
        return 1

    scope = in_scope(added_md, live_paths(staged_ov), live_paths(head_ov))
    staged_cat = _git("show", ":" + CATALOG) or None

    def _staged_continuation(name):
        """A continuation file read from the INDEX, for the same reason the catalog is."""
        text = _git("show", ":" + DOCDIR + name)
        if text:
            return text
        return Path(DOCDIR + name).read_text()

    bl, err = backlog(staged_ov, staged_cat, read_continuation=_staged_continuation)
    bl_note = ("  (%d LIVE doc(s) absent from CATALOG -- %s)" % (len(bl), ", ".join(bl))
               if bl else "  (whole tree: every LIVE doc is indexed)") if not err else \
              "  (backlog unreadable: %s)" % err
    bl_note += ("  (whole tree: %d tracked doc(s) have NO overrides row, enforced by the hook via --unrowed; "
                "list them with --unrowed)" % len(tree_unrowed))

    # WHOLE-TREE ARM, ENFORCING SINCE 2026-09-21. It reports before the scoped arm because an
    # unindexed doc somebody else left behind is the same defect as one you are adding, and the
    # scoped arm cannot see it.
    if bl:
        print("LIVE-INDEX :: FAIL -- %d LIVE document(s) are not reachable from CATALOG.md:"
              % len(bl))
        for b in bl:
            print("    %s" % b)
        print("  Add a pointer row to docs/orchestration/CATALOG.md, or -- if the document is not "
              "live -- fix its class in MANIFEST-overrides.tsv. Do NOT misclassify to silence this.")
        print("  ⚠ THIS ARM IS WHOLE-TREE, so it can fail on a document you did not touch. That is "
              "the gate working: an unindexed LIVE doc is one nobody reads, and it belongs to "
              "whoever notices. The backlog was driven to ZERO on 2026-09-21 before this was "
              "switched on, so a red here is new debt, not inherited debt.")
        return 1

    if not scope:
        print("LIVE-INDEX :: nothing newly LIVE in this commit." + bl_note)
        return 0
    _cat, _cerr = router_text(staged_cat or open(CATALOG).read(), read=_staged_continuation)
    if _cerr:
        print("LIVE-INDEX :: CANNOT CHECK -- " + _cerr)
        return 2
    bad = unindexed(scope, _cat)
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
    fails, ran = [], []

    def ck(label, ok, detail=""):
        print(("  PASS  " if ok else "  FAIL  ") + label + (" :: " + detail if detail else ""))
        ran.append(label)
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

    # ---- DECLARED CONTINUATION FILES (2026-09-21). The widening is the dangerous kind -- it makes
    # MORE things count as indexed -- so the cases that matter are the ones where it must still
    # refuse. Cases 3 and 4 are the whole safety argument: declared-not-globbed, and unreadable-is-
    # not-clean.
    CONT = "CATALOG-ARCHIVE-x.md"
    cat_decl = "# router\n<!-- CATALOG-CONTINUES: %s -->\n" % CONT
    ck("CONT: the declaration is parsed", declared_continuations(cat_decl) == [CONT])
    ck("CONT: an undeclared CATALOG-like name is NOT picked up",
       declared_continuations("# router\nsee CATALOG-ARCHIVE-y.md\n") == [])
    # 1. THE NEW CAPABILITY: indexed only in the continuation -> clean
    bl, e = backlog(staged_ov=staged, staged_cat=cat_decl,
                    read_continuation=lambda n: "- [`NEWDOC-20260817-x.md`](NEWDOC-20260817-x.md)")
    ck("CONT: a doc indexed ONLY in a declared continuation is clean", e is None and bl == [], str(bl))
    # 2. and the property it must not cost: indexed nowhere is still caught
    bl, e = backlog(staged_ov=staged, staged_cat=cat_decl, read_continuation=lambda n: "| nothing |")
    ck("CONT: a doc indexed in NEITHER file is still CAUGHT",
       e is None and bl == ["NEWDOC-20260817-x.md"], str(bl))
    # 3. DECLARED, NOT GLOBBED. A file that exists and is not declared must not count, or any new
    #    file could silently become an index.
    bl, e = backlog(staged_ov=staged, staged_cat="# router, no declaration\n",
                    read_continuation=lambda n: "- [`NEWDOC-20260817-x.md`](NEWDOC-20260817-x.md)")
    ck("CONT: an UNDECLARED file does not count as an index even if it names the doc",
       e is None and bl == ["NEWDOC-20260817-x.md"], str(bl))
    # 4. UNREADABLE IS NOT CLEAN. The failure this whole file exists to distinguish.
    def _boom(name):
        raise OSError("no such file")
    bl, e = backlog(staged_ov=staged, staged_cat=cat_decl, read_continuation=_boom)
    ck("CONT: a declared-but-unreadable continuation is an ERROR, not an empty backlog",
       bl is None and e is not None and CONT in e, repr(e))
    # 5. the continuation file is the index; it need not be indexed by itself
    ov_cont = HDR + DOCDIR + CONT + "\tLIVE\topen\t\n"
    bl, e = backlog(staged_ov=ov_cont, staged_cat=cat_decl, read_continuation=lambda n: "| nothing |")
    ck("CONT: a declared continuation is exempt from needing its own pointer",
       e is None and bl == [], str(bl))

    # ---- THE WHOLE-TREE ARM, enforcing since 2026-09-21. Both directions, same bar as above:
    # a backlog function that returned everything would satisfy 10 and fail 11, and one that
    # returned nothing would satisfy 11 and fail 10. Neither alone is a test.
    bl_abs, e1 = backlog(staged_ov=staged, staged_cat="| some other row |")
    ck("whole tree: a LIVE doc absent from CATALOG is CAUGHT",
       e1 is None and bl_abs == ["NEWDOC-20260817-x.md"], str(bl_abs))
    bl_pres, e2 = backlog(staged_ov=staged,
                          staged_cat="- [`NEWDOC-20260817-x.md`](NEWDOC-20260817-x.md)")
    ck("whole tree: the SAME doc present in CATALOG is clean",
       e2 is None and bl_pres == [], str(bl_pres))
    bl_arch, e3 = backlog(staged_ov=arch, staged_cat="| nothing |")
    ck("whole tree: an ARCHIVAL doc absent from CATALOG is NOT a violation",
       e3 is None and bl_arch == [], str(bl_arch))
    bl_exempt, e4 = backlog(staged_ov=catrow, staged_cat="| nothing |")
    ck("whole tree: CATALOG.md itself is still exempt",
       e4 is None and bl_exempt == [], str(bl_exempt))
    # THE OPERAND, which is the half a passing/failing pair cannot show: it must read what was
    # HANDED to it, not the repository. If it silently fell back to the working tree these two
    # would agree with each other and with the real repo, and the fallback would be invisible.
    bl_op, e5 = backlog(staged_ov=HDR, staged_cat="| nothing |")
    ck("whole tree: an EMPTY staged overrides yields an empty backlog, not the repo's",
       e5 is None and bl_op == [], str(bl_op))

    # ---- THE UNDECLARED ARM (row 60, part 3). Both directions: it must fire on a doc with no row
    # and stay silent on one with ANY row, including ARCHIVAL -- otherwise it would be a LIVE-only
    # rule wearing a new name, or a rule no committer can satisfy.
    ck("UNROWED: an added doc with NO overrides row FIRES", unrowed([NEW], HDR) == [NEW])
    ck("UNROWED: the same doc with an ARCHIVAL row is silent", unrowed([NEW], arch) == [])
    ck("UNROWED: the same doc with a LIVE row is silent", unrowed([NEW], staged) == [])
    ck("UNROWED: runs/ and state/ records are not documents needing a row",
       unrowed([DOCDIR + "runs/x/NOTE.md", DOCDIR + "state/y.md"], HDR) == [])
    ck("UNROWED: non-.md files and files outside docs/orchestration are out of scope",
       unrowed([DOCDIR + "tool.py", "docs/OPEN_ITEMS.md"], HDR) == [])
    ck("UNROWED: CATALOG.md stays exempt", unrowed([DOCDIR + "CATALOG.md"], HDR) == [])
    ck("UNROWED: a malformed row does not count as a declaration of the doc",
       unrowed([NEW], HDR + "garbage-with-no-tabs\n") == [NEW])

    n_cases = len(ran)
    dt = time.time() - t0
    print()
    if fails:
        print("SELF-TEST :: FAILED -> %s" % fails)
        return 1
    print("SELF-TEST :: %d/%d PASS in %.3f s (synthetic; no repo state touched)"
          % (n_cases, n_cases, dt))
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
    if "--unrowed" in a:
        # WHOLE TREE, from the index: tracked docs and the staged overrides file.
        ov = _git("show", ":" + OVERRIDES)
        if not ov:
            print("unrowed :: CANNOT CHECK -- the overrides file could not be read from the index")
            raise SystemExit(2)
        missing = unrowed(_git("ls-files", "--", DOCDIR).splitlines(), ov)
        print("tracked docs under %s with NO overrides row: %d" % (DOCDIR, len(missing)))
        for p in missing:
            print("    %s" % p)
        raise SystemExit(1 if missing else 0)
    raise SystemExit(check())
