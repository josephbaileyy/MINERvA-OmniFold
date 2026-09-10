#!/usr/bin/env python3
"""Withdrawal-completeness check for RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md.

WHY THIS EXISTS, and it is not a hygiene tool. In this lane a withdrawn claim survived its own
retraction FOUR times, in four different ways, and every failure was a search whose FORM excluded
the instance it was meant to find:

  1. rev. 2 withdrew the `M`-independence claim by editing the sentence it had searched for. The
     claim count across that commit went 1 -> 2: the paraphrase survived, and landed inside the
     paragraph headed "What still stands, unqualified".
  2. a line-oriented `grep` acquitted it, because the survivor was line-wrapped.
  3. round 3's first sweep was scoped to the `.md`, so it missed the PROBE'S OWN HEADER and
     `CATALOG.md` -- the third stale router entry in this lane.
  4. the independent reviewer's own multi-paraphrase `grep` also missed the probe header; it found
     it by reading.

So "I swept by claim content" is not a claim anyone can check, and the reviewer was right that it
cannot stand with no artifact behind it. THIS IS THE ARTIFACT.

HOW IT WORKS -- a PINNED INVENTORY, not a heuristic. Every occurrence of every withdrawn claim is
enumerated and approved here, per file, with a reason. The check compares the live counts against
the approved ones and FAILS CLOSED on any difference. It therefore catches:

  * a new affirmation appearing anywhere in the file set (count goes up)          -> FAIL
  * a withdrawal's quotation being deleted, which would orphan the retraction     -> FAIL
  * an UNREGISTERED FILE ON DISK carrying a withdrawn claim, found by CONTENT     -> FAIL
    (R5-2: the first version enumerated three files and had no filesystem discovery at all, so a
     fourth file with a live affirmation went undetected -- round 3's ".md-only" scoping defect,
     reproduced inside the instrument built to prevent it)

⚠ AND THE AUDITED DOCUMENTS MUST NOT REPRODUCE THESE MATCH STRINGS AS EXAMPLES. Round 5's own
write-up quoted two of them while explaining them, and the count for one claim went 1 -> 3 on the
next run. The checker excludes itself from its corpus for this reason; the prose it audits has to
observe the same rule and DESCRIBE a match string rather than quote it. That is a real constraint on
how a withdrawal can be documented, and it is cheaper than the alternative -- an audit that trips on
its own explanation trains its reader to ignore it.

It does NOT try to decide automatically whether an occurrence is a live affirmation or a quotation
inside a withdrawal. That judgement is a human's, made once, recorded here, and then PINNED -- which
is the part that makes it re-runnable. An unclassified occurrence is a failure, not a warning.

⚠ WHAT IT CANNOT DO, STATED SO NOBODY READS A PASS AS MORE THAN IT IS. It compares COUNTS. If an
approved quotation were rewritten IN PLACE into a live affirmation, the count would not move and this
check would stay green. It catches appearance, disappearance and re-scoping; it does not read
meaning. The pinned `reason` field is what a human re-reads to check that -- so a green run means
"no occurrence has appeared or vanished since these were classified", NOT "every occurrence is still
a quotation". Anyone changing the prose around an approved occurrence must re-read its reason.

AND ITS FIRST RUN CAUGHT ITS OWN AUTHOR. I pinned `recommendation: 0` for the rank-263 claim while
Part 6's F1(b) row quotes it, so the very first invocation failed. Hand classification is exactly as
fallible as the sweeps this replaces -- which is the argument for pinning rather than remembering.

Run:        python3 docs/orchestration/state/check-withdrawal-completeness-20260910.py
Self-test:  python3 docs/orchestration/state/check-withdrawal-completeness-20260910.py --self-test

The self-test is a POWER TEST IN BOTH DIRECTIONS: it injects a live affirmation and requires the
check to FAIL, and deletes an approved quotation and requires the check to FAIL. A check that only
passes on the current tree proves nothing about its ability to detect anything.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ORCH = _HERE.parent

DELIVERY = {
    "recommendation": _ORCH / "RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md",
    "probe": _HERE / "probe-z-criteria-acceptance-mathematics-20260910.py",
    "catalog": _ORCH / "CATALOG.md",
}

# Each withdrawn claim, probed by SEVERAL paraphrases, because one wording is what failed.
# `approved` maps file key -> expected occurrence count, with the reason each is permitted.
#
# A PARAPHRASE IS EITHER A STRING OR AN AND-GROUP (a tuple). ⚠ The tuple form exists because
# discovery's false-positive control caught TWO generic-English paraphrases the moment it ran:
# "needs no tolerance" matched an innocent August sentence about a bit-exact readback, and "the
# production trunk" matched ordinary prose about a pipeline. A bare phrase asks "do these WORDS
# appear"; an AND-group asks "do the words AND the claim-specific token appear TOGETHER", which is
# the difference between matching a wording and matching a CLAIM. An AND-group contributes
# `text.count(group[0])` when EVERY element is present, and 0 otherwise.
WITHDRAWN = [
    {
        "claim": "M-independence: a trunk-level rho bounds every marginal",
        "withdrawn_by": "F2, round 2 -- needs range(Ck-C0) inside range(C0), unmeasured on Z",
        "paraphrases": [
            "discharges the sensitivity question for all marginals",
            "BOUND is `M`-independent",
            "bounds rho on every marginal",
            "BOUND does not depend on which projection",
            "evaluated BEFORE the projection question",
            "evaluated **before** the projection question",
        ],
        "approved": {"recommendation": 5, "probe": 2, "catalog": 0},
        "reason": "recommendation: 3 in the F2 withdrawal block + 2 in the R3-1 correction quoting "
                  "the survivor. probe: 2 in the section-1b header withdrawal. catalog: none.",
    },
    {
        "claim": "domination implies non-bindingness",
        "withdrawn_by": "F9 -- the implication needs rho_crit <= tau, a relation between THRESHOLDS",
        "paraphrases": ["cannot bind independently, by definition", "dominated statistic cannot bind"],
        "approved": {"recommendation": 0, "probe": 0, "catalog": 0},
        "reason": "fully removed; Part 6 was rewritten rather than patched.",
    },
    {
        "claim": "the declaration-stability leg needs no tolerance",
        "withdrawn_by": "R3-2 -- it carries exactly one, the 1e-8 subspace gate",
        # ⚠ R5-2 FOLLOW-UP: "needs no tolerance" alone is GENERIC ENGLISH and produced a FALSE
        # POSITIVE the moment discovery went live -- `PREDECLARATION-20260816-hrowindex4d-readback.md:68`
        # says "An exact comparison needs no tolerance and must not be given one", an innocent and
        # unrelated August sentence. A paraphrase used for DISCOVERY must be specific to the CLAIM's
        # SUBJECT, not just its predicate. Too-narrow wording gave false NEGATIVES (R3-1);
        # too-generic wording gives false POSITIVES. Same underlying error: the string is not the claim.
        "paraphrases": ["it needs no tolerance", "NEEDS NO TOLERANCE", "leg needs no tolerance",
                        "This leg needs no tolerance"],
        "approved": {"recommendation": 0, "probe": 0, "catalog": 1},
        "reason": "catalog: 1, inside the sentence that records the earlier revision said it and "
                  "that it was FALSE.",
    },
    {
        "claim": "the builder-comparison premise was superseded by measurement",
        "withdrawn_by": "authoring lane's sustained objection -- 1 of 6 pairs measured",
        "paraphrases": ["SUPERSEDED by measurement"],
        "approved": {"recommendation": 2, "probe": 0, "catalog": 0},
        "reason": "both inside the NOT-SUPERSEDED correction, quoting the wrong verdict.",
    },
    {
        "claim": "retained-rank ndf rests on a distributional fact",
        "withdrawn_by": "F6 -- the protocol says those assumptions are not established",
        "paraphrases": ["rests on a distributional fact"],
        "approved": {"recommendation": 1, "probe": 0, "catalog": 0},
        "reason": "1, inside the withdrawal that quotes it.",
    },
    {
        "claim": "rank 263 is a property of Z, G, or the production trunk",
        "withdrawn_by": "F1(b) -- 263 is S's, the component donor",
        # AND-group: "the production trunk" alone is ordinary English and leaked in the
        # false-positive control. The CLAIM is that the 263 figure belongs to the trunk, so
        # the rank token must co-occur.
        "paraphrases": [("the production trunk", "263")],
        "approved": {"recommendation": 1, "probe": 1, "catalog": 0},
        "reason": "recommendation: 1, in Part 6's F1(b) row quoting what my probe had called "
                  "it. probe: 1, inside the docstring correction quoting the misattribution. "
                  "NOTE: I pinned recommendation at 0 and this check caught it on its FIRST "
                  "run -- hand classification is exactly as fallible as the sweeps it "
                  "replaces, which is why the counts are pinned rather than remembered.",
    },
    {
        "claim": "cause3_corr has no proposal",
        "withdrawn_by": "Joseph's 2026-09-10 ruling; Part 6 gives one",
        "paraphrases": ["Only `cause3_corr` is left without a proposal", "the one boundary I do not propose"],
        "approved": {"recommendation": 0, "probe": 0, "catalog": 0},
        "reason": "fully removed from both the document and the router entry.",
    },
    {
        "claim": "the applied pinv cutoff is max(shape)*eps in production",
        "withdrawn_by": "R4-1 -- production is numpy 1.26.4, whose default is the literal 1e-15; "
                        "and the figure was this lane's own arithmetic, not a measurement of numpy",
        "paraphrases": ["4.4408920985006262e-14", "4.440892098500626e-14"],
        "approved": {"recommendation": 1, "probe": 0, "catalog": 0},
        "reason": "1, inside the R4-1 correction quoting the withdrawn figure.",
    },
]


# The checker itself holds every paraphrase, so it must NEVER be part of its own corpus -- adding it
# would make every count explode and the failure would look like a document defect. Guarded, not
# merely documented, because "remember not to do X" is what this whole file exists to replace.
assert Path(__file__).resolve() not in {p.resolve() for p in DELIVERY.values()}, (
    "the withdrawal checker is inside its own DELIVERY set; it holds the paraphrases it searches for")


def _count(text: str, paraphrase) -> int:
    """Occurrences of a paraphrase. A tuple is an AND-GROUP: all elements must be present."""
    if isinstance(paraphrase, tuple):
        if all(part in text for part in paraphrase):
            return text.count(paraphrase[0])
        return 0
    return text.count(paraphrase)


def _present(text: str, paraphrase) -> bool:
    return _count(text, paraphrase) > 0


def _flat(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text())


def audit(corpus: dict[str, str]) -> list[str]:
    """Return a list of failure strings. Empty list == the inventory matches."""
    failures = []
    for entry in WITHDRAWN:
        for key, text in corpus.items():
            expected = entry["approved"].get(key)
            if expected is None:
                failures.append(f"{entry['claim']!r}: file {key!r} is in the delivery but has no "
                                f"approved count -- classify it and pin it")
                continue
            actual = sum(_count(text, ph) for ph in entry["paraphrases"])
            if actual != expected:
                direction = "NEW OCCURRENCE(S)" if actual > expected else "APPROVED QUOTATION LOST"
                failures.append(
                    f"{direction}: claim {entry['claim']!r} in {key}: expected {expected}, "
                    f"found {actual}. Withdrawn by: {entry['withdrawn_by']}. "
                    f"Approved because -- {entry['reason']}")
    return failures


# ---- R5-2: DISCOVERY, because enumeration cannot fail closed on a file nobody remembered.
# Round 3's sweep was "scoped to the .md" and missed the probe header and CATALOG.md. The first
# version of THIS FILE reproduced that scoping assumption: `DELIVERY` was a literal 3-entry dict
# with no `glob`/`iterdir`/`walk` anywhere, so a fourth file carrying a live affirmation went
# undetected and the checker stayed green while blind. Measured: 583 files / 12.0 MB / 0.15 s, so
# scanning by content costs nothing worth saving.
SCAN_EXTS = {".md", ".py", ".tsv", ".json", ".sh"}
SCAN_SKIP = ("/runs/",)          # bulk machine receipts; never prose, and large


def discover(root: Path, paraphrases: set[str]) -> dict[Path, str]:
    """Every file under `root` whose text contains ANY registered paraphrase.

    Discovery is driven by the very strings being audited, so it cannot miss a file BECAUSE of
    what that file contains -- which is the failure mode enumeration has. The checker itself is
    excluded: it holds every paraphrase by construction.
    """
    me = Path(__file__).resolve()
    found = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in SCAN_EXTS:
            continue
        if any(s in str(path) for s in SCAN_SKIP) or path.resolve() == me:
            continue
        try:
            flat = re.sub(r"\s+", " ", path.read_text(errors="ignore"))
        except OSError:
            continue
        if any(_present(flat, ph) for ph in paraphrases):
            found[path.resolve()] = flat
    return found


def all_paraphrases() -> list:
    """Every paraphrase, strings and AND-groups alike. A list, not a set: tuples and strings mix."""
    out = []
    for e in WITHDRAWN:
        for ph in e["paraphrases"]:
            if ph not in out:
                out.append(ph)
    return out


def unregistered(root: Path) -> list[Path]:
    """Discovered files carrying a withdrawn claim that are NOT in the pinned DELIVERY set."""
    registered = {q.resolve() for q in DELIVERY.values()}
    return sorted(set(discover(root, all_paraphrases())) - registered)


def _load() -> dict[str, str]:
    missing = [k for k, p in DELIVERY.items() if not p.is_file()]
    if missing:
        raise SystemExit(f"[FAIL] delivery file(s) absent: {missing}. The check cannot pass by "
                         f"finding nothing -- an absent file is a failure, not a clean sweep.")
    return {k: _flat(p) for k, p in DELIVERY.items()}


def self_test() -> int:
    """Power test in BOTH directions. A check that only passes on the current tree proves nothing."""
    corpus = _load()
    print("SELF-TEST")
    clean = audit(corpus)
    print(f"  (a) unmodified corpus            -> {len(clean)} failure(s)   must be 0")
    if clean:
        for f in clean:
            print(f"        {f}")
        print("  self-test ABORTED: fix the live tree before trusting the detector")
        return 1

    # (b) inject a LIVE AFFIRMATION of a withdrawn claim.
    injected = dict(corpus)
    injected["recommendation"] += (
        " So the BOUND is `M`-independent and a small rho_5D discharges the sensitivity question "
        "for all marginals at once.")
    f_inj = audit(injected)
    print(f"  (b) live affirmation injected    -> {len(f_inj)} failure(s)   must be >= 1")

    # (c) DELETE an approved quotation, which would orphan its retraction.
    deleted = dict(corpus)
    deleted["recommendation"] = deleted["recommendation"].replace("SUPERSEDED by measurement", "", 1)
    f_del = audit(deleted)
    print(f"  (c) approved quotation deleted   -> {len(f_del)} failure(s)   must be >= 1")

    # (d) ⚠ RELABELLED IN R5-2. This mutates the IN-MEMORY dict, so it tests `audit()`'s handling
    # of a corpus key SOMEBODY ALREADY REMEMBERED TO ADD. It never touched the discovery path, and
    # its old label -- "a new delivery file" -- is what made it read as coverage it did not have.
    extra = dict(corpus)
    extra["key_with_no_approved_count"] = "some text"
    f_new = audit(extra)
    print(f"  (d) corpus key with no pinned count -> {len(f_new)} failure(s)   must be >= 1")
    print("      (tests audit(), NOT discovery -- see (e), which is the coverage test)")

    # (e) THE REAL COVERAGE TEST, new in R5-2: an UNREGISTERED file on disk carrying a live
    # affirmation must be DISCOVERED and must fail closed. Run against a temp root so the check
    # can be power-tested without writing into the repository.
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "state").mkdir()
        (root / "an-unregistered-note.md").write_text(
            "Some prose. So the BOUND is `M`-independent, restored after review.\n")
        (root / "state" / "irrelevant.json").write_text('{"no": "claims here"}\n')
        hits = discover(root, all_paraphrases())
        strays = unregistered(root)
        print(f"  (e) unregistered file on disk       -> discovered {len(hits)}, "
              f"unregistered {len(strays)}   both must be >= 1")
        ok_e = len(hits) >= 1 and len(strays) >= 1
        # (f) THE FALSE-POSITIVE CONTROL, and it exists because discovery's FIRST live run tripped
        # on one: an innocent August sentence, "An exact comparison needs no tolerance and must not
        # be given one", matched a paraphrase that was generic English rather than specific to the
        # claim's subject. A discovery check without this control is one-directional -- it would
        # flag unrelated documents forever and train its reader to ignore it.
        with tempfile.TemporaryDirectory() as td2:
            root2 = Path(td2)
            (root2 / "clean.md").write_text("nothing withdrawn is asserted here\n")
            (root2 / "innocent.md").write_text(
                "An exact comparison needs no tolerance and must not be given one.\n"
                "The projection question is settled for this readback.\n"
                "We inspected the production trunk of the pipeline informally.\n")
            clean_hits = discover(root2, all_paraphrases())
        print(f"      (f) false-positive control: innocent generic prose -> discovered "
              f"{len(clean_hits)}   must be 0")
        for hit, txt in clean_hits.items():
            matched = [ph for ph in all_paraphrases() if _present(txt, ph)]
            print(f"          LEAKED: {hit.name} via {matched}")
        ok_e = ok_e and not clean_hits

    ok = bool(f_inj) and bool(f_del) and bool(f_new) and ok_e
    print(f"  SELF-TEST {'PASSED' if ok else 'FAILED'} -- fires on an injected affirmation, a "
          f"deleted quotation, an unpinned key and an UNREGISTERED FILE ON DISK; silent on a "
          f"clean tree and on a tree with no claims")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    failures = audit(_load())
    stray = unregistered(_ORCH)
    if stray:
        failures = [f"UNREGISTERED FILE carrying a withdrawn claim: {s} -- it is not in DELIVERY, "
                    f"so its occurrences were never classified. Classify and pin it, or remove "
                    f"the claim from it." for s in stray] + failures
    if failures:
        print(f"[FAIL] withdrawal-completeness: {len(failures)} discrepanc(ies)\n")
        for f in failures:
            print(f"  - {f}\n")
        print("A count that ROSE means a withdrawn claim is affirmed somewhere new: find it, and\n"
              "either delete the affirmation or classify it as a quotation and pin it here.\n"
              "A count that FELL means an approved quotation was removed, orphaning its retraction.")
        return 1
    n = sum(len(e["approved"]) for e in WITHDRAWN)
    print(f"[OK] withdrawal-completeness: {len(WITHDRAWN)} withdrawn claims x "
          f"{len(DELIVERY)} delivery files = {n} pinned counts, all matching.")
    # ⚠ R5-1. This line used to read "Every occurrence is an approved quotation inside a
    # withdrawal. No live affirmation." -- which asserted, in the OUTPUT, precisely the
    # meaning-level claim the docstring above DISCLAIMS. The reviewer demonstrated it (Test K):
    # rewriting an approved quotation IN PLACE, keeping the phrase and inverting the framing from
    # "REV. 2's OWN EDIT LEFT THE WITHDRAWN CLAIM STANDING" to "THIS REMAINS THE OPERATIVE
    # PRACTICAL CONSEQUENCE, RESTORED AFTER REVIEW", left the counts at 5 -> 5 and the checker
    # GREEN. Reproduced independently here before repair. That is the headline-overrides-body
    # shape, inside the instrument built to prevent it. The count-only limitation is INHERENT and
    # is carried to Joseph; the WORDING was a defect and is fixed here.
    print("     What this establishes: no occurrence has APPEARED or VANISHED since it was")
    print("     classified. What it does NOT establish: that each occurrence is still a")
    print("     quotation. The framing around a pinned occurrence can be inverted without moving")
    print("     its count -- so re-read the pinned `reason` whenever you edit prose near one.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
