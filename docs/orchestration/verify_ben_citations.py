#!/usr/bin/env python3
"""Every `BEN-*` cited in source resolves to a registry row, so a citation is a CHECK and not a hope.

WHY THIS EXISTS
---------------
Source and hooks cite BEN ids as load-bearing pointers: `.githooks/pre-commit`'s admitting rule cites
OI-64, its counter block cites BEN-163, `whose_row.py` cites BEN-105 for the attentiveness record.
Nothing verified that any of them resolved.

The 2026-08-20 prepublication freeze pruned `docs/orchestration/FINDINGS.md` from 391 BEN rows to the
handful the active playbook uses, moving the rest to the evidence tag. That prune is exactly the event
that can strand a citation, and it ran with no check over the citing files. It happened not to strand
one -- MEASURED, not assumed, at the commit that added this script -- which is why the check can be
admitted now: it is green on a clean tree, so a committer who did nothing wrong can always make it pass.
Admitting it while it passes is the whole point; a check first written when it is already red cannot be
wired, which is the state `check_canonical_designation.py` has been parked in since 2026-08-13.

WHAT IT MEASURES, and the number worth watching
-----------------------------------------------
The registry is the union of two sources: FINDINGS.md in the working tree, and FINDINGS.md at the
evidence tag named by FINDINGS.md's own header. The second supplies the large majority of resolutions,
and that asymmetry is the standing fragility this check makes visible: those citations resolve only
while the tag is fetched and intact. A `--no-tags` or shallow clone silently converts them to dead
ends, and a dead pointer is worse than no pointer, because the reader who cannot cash it out inlines
the whole argument next time. The TAG-ONLY count prints on every run.

THE TAG NAME IS DERIVED, NEVER RESTATED. It is parsed out of FINDINGS.md's header, the same move
`whose_row.py` makes for the block table and for the same reason: a hardcoded tag here would be BEN-163
in the instrument -- retag the freeze and this file still names the old one, correct-looking and wrong.

THREE-SIDED, per BEN-162's form set:
  * a cited id with no registry row       -> the stranding this exists for;
  * zero citations, or zero registry rows -> CANNOT CHECK. A discoverer that matches nothing reports
    success unless it is made to refuse, which is the SHELL_PIN_FLOOR failure mode;
  * a waiver that is no longer needed     -> also a failure, or the waiver silently authorizes the next
    genuine stranding on that id forever.

LIMITS, stated because a verifier that overstates its reach is the defect it exists to prevent:
  * SCOPE IS SOURCE, NOT PROSE. Tracked `*.py` and `*.sh` outside `docs/`, plus `.githooks/*`. Citations
    inside `docs/` are excluded deliberately: receipts and verdicts cite ids by the hundred, they are
    the auditor's own layer, and pulling them in would make this a whole-corpus link checker whose
    failures are mostly not about source at all.
  * IT CHECKS EXISTENCE, NOT AGREEMENT. A row that exists but says something other than what the citing
    comment claims passes here. No mechanism can close that; it is what review is for.
  * `BEN-\\d{3}` ONLY. `BEN-0XX` in a template and `BEN-09[0-9]` inside a quoted grep command are
    prose about ids, not citations, and the three-digit grammar excludes both. An id ever allocated
    past 999 breaks this grammar loudly rather than silently narrowing.

    verify_ben_citations.py            # 0 ok / 1 stranded / 2 cannot check
    verify_ben_citations.py --self-test
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent               # derived from __file__, never hardcoded (the p4_evidence.py lesson)
FINDINGS = REPO / "docs/orchestration/FINDINGS.md"
FINDINGS_REL = "docs/orchestration/FINDINGS.md"

BEN_ROW = re.compile(r"^\|\s*(BEN-\d{3})\s*\|")
BEN_CITE = re.compile(r"BEN-\d{3}")
EVIDENCE_TAG = re.compile(r"\b(evidence/[A-Za-z0-9._/-]+)\b")

# id -> reason. A waived id is cited in source with no registry row, on purpose and with the reason
# recorded here. Empty is the correct steady state; a stale entry fails (arm 3).
CITATION_WAIVERS: dict[str, str] = {}


def _git(*args: str) -> str | None:
    """Run git in REPO. None on any failure, so a missing ref is a state, not a traceback."""
    try:
        out = subprocess.run(["git", "-C", str(REPO), *args],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def evidence_tag(findings: Path = FINDINGS) -> str | None:
    """The freeze tag, parsed out of FINDINGS.md's header rather than restated here."""
    if not findings.exists():
        return None
    head = "\n".join(findings.read_text(encoding="utf-8", errors="replace").splitlines()[:40])
    names = EVIDENCE_TAG.findall(head)
    return names[0] if names else None


def registry_rows(text: str) -> set[str]:
    return {m.group(1) for line in text.splitlines() if (m := BEN_ROW.match(line))}


def cited_files() -> list[Path]:
    listing = _git("ls-files", "*.py", "*.sh")
    if listing is None:
        return []
    files = [REPO / p for p in listing.split() if not p.startswith("docs/")]
    hooks = REPO / ".githooks"
    if hooks.is_dir():
        files += sorted(p for p in hooks.iterdir() if p.is_file())
    return files


def citations(files: list[Path]) -> dict[str, list[str]]:
    """id -> the paths citing it, repo-relative."""
    found: dict[str, list[str]] = {}
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ident in sorted(set(BEN_CITE.findall(text))):
            found.setdefault(ident, []).append(str(path.relative_to(REPO)))
    return found


def check(findings: Path = FINDINGS, cites: dict[str, list[str]] | None = None,
          waivers: dict[str, str] | None = None) -> int:
    """0 ok / 1 stranded citation or stale waiver / 2 cannot check.

    `cites` and `waivers` are injected only by the self-test, so both failing arms can be exercised
    without planting a bad citation in the tree. The merge_guard.sh precedent (CONVENTION-lane-
    worktrees.md) is why they exist: its one false pass was found end-to-end and NOT by its self-test.
    """
    if not findings.exists():
        print(f"BEN CITATIONS :: CANNOT CHECK -- {FINDINGS_REL} missing. Nothing was verified; "
              f"this is NOT a pass.")
        return 2

    worktree = registry_rows(findings.read_text(encoding="utf-8", errors="replace"))
    tag = evidence_tag(findings)
    if tag is None:
        print(f"BEN CITATIONS :: CANNOT CHECK -- no `evidence/...` tag name found in {FINDINGS_REL}'s "
              f"header. The registry's second half is unaddressable, so most citations cannot be "
              f"resolved. NOT a pass.")
        return 2

    frozen_text = _git("show", f"{tag}:{FINDINGS_REL}")
    if frozen_text is None:
        print(f"BEN CITATIONS :: CANNOT CHECK -- `{tag}` does not resolve, or carries no "
              f"{FINDINGS_REL}. Most source citations resolve only there. NOT a pass.\n"
              f"  If this is a fresh or shallow clone, the tag was simply not fetched:\n"
              f"      git fetch origin --tags")
        return 2
    frozen = registry_rows(frozen_text)

    registry = worktree | frozen
    if cites is None:
        cites = citations(cited_files())
    if waivers is None:
        waivers = CITATION_WAIVERS

    # Zero on either side is CANNOT CHECK, never PASS: a discoverer that matches nothing would
    # otherwise report success forever the moment a grammar or a path changes.
    if not registry or not cites:
        print(f"BEN CITATIONS :: CANNOT CHECK -- {len(registry)} registry rows, {len(cites)} cited "
              f"ids. The row grammar or the file scope no longer matches, so this check would pass "
              f"vacuously.")
        return 2

    stranded = {i: p for i, p in cites.items() if i not in registry and i not in waivers}
    tag_only = sorted(i for i in cites if i not in worktree)

    print(f"  [{len(cites)} cited ids over {len(cited_files())} files, {len(registry)} registry rows "
          f"({len(worktree)} in tree, {len(frozen)} at {tag}), {len(tag_only)} resolve ONLY at the tag, "
          f"{len(waivers)} waived]")

    fail: list[str] = []
    for ident, paths in sorted(stranded.items()):
        fail.append(f"STRANDED {ident} cited in {', '.join(paths)} has no row in {FINDINGS_REL}, in "
                    f"the tree or at {tag}. Restore the row, correct the citation, or waive it here "
                    f"with the reason -- do not delete the citation to make this green.")
    for ident, reason in sorted(waivers.items()):
        if ident in registry or ident not in cites:
            fail.append(f"STALE WAIVER {ident} is waived ({reason}) but now resolves, or is no longer "
                        f"cited. Remove it, or it silently permits the next real stranding on that id.")

    if fail:
        print("BEN CITATIONS :: FAIL")
        for line in fail:
            print(f"  - {line}")
        return 1
    return 0


def self_test() -> int:
    """Power test, both directions: a check that cannot fail is not a check."""
    import tempfile

    bad = 0

    def case(name: str, got: object, want: object) -> None:
        nonlocal bad
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name} (got {got!r}, want {want!r})")

    print("verify_ben_citations self-test")
    case("registry parses a row", registry_rows("| BEN-163 | text |"), {"BEN-163"})
    case("a mention is not a row", registry_rows("see BEN-163 in prose"), set())
    case("two-digit id is not a row", registry_rows("| BEN-09 | text |"), set())
    case("cite grammar takes three digits", set(BEN_CITE.findall("BEN-105 BEN-09 BEN-0XX")), {"BEN-105"})

    with tempfile.TemporaryDirectory() as d:
        missing = Path(d) / "nope.md"
        case("missing FINDINGS -> CANNOT CHECK (2)", check(missing), 2)

        no_tag = Path(d) / "no_tag.md"
        no_tag.write_text("# index\n\n| BEN-163 | row |\n", encoding="utf-8")
        case("no tag name in header -> CANNOT CHECK (2)", check(no_tag), 2)

        bogus = Path(d) / "bogus_tag.md"
        bogus.write_text("# index\n\nevidence/does-not-exist-00000000\n\n| BEN-163 | row |\n",
                         encoding="utf-8")
        case("unresolvable tag -> CANNOT CHECK (2)", check(bogus), 2)

        case("tag parsed out of the header", evidence_tag(bogus), "evidence/does-not-exist-00000000")

    case("live tree passes", check(), 0)

    # The failing arms, exercised without planting a bad citation in the tree.
    case("stranded citation -> FAIL (1)",
         check(cites={"BEN-999": [".githooks/pre-commit"]}, waivers={}), 1)
    case("a waived strand passes",
         check(cites={"BEN-999": [".githooks/pre-commit"]},
               waivers={"BEN-999": "self-test fixture"}), 0)
    case("waiver on a resolving id is STALE -> FAIL (1)",
         check(cites={"BEN-163": [".githooks/pre-commit"]},
               waivers={"BEN-163": "self-test fixture"}), 1)
    case("waiver on an uncited id is STALE -> FAIL (1)",
         check(cites={"BEN-163": [".githooks/pre-commit"]},
               waivers={"BEN-998": "self-test fixture"}), 1)
    case("empty citation set -> CANNOT CHECK (2)", check(cites={}, waivers={}), 2)

    print(f"  {bad} failing case(s)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="power test, both directions")
    args = ap.parse_args()
    return self_test() if args.self_test else check()


if __name__ == "__main__":
    sys.exit(main())
