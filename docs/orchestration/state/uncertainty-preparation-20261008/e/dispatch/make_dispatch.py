#!/usr/bin/env python3
"""Write the paste-ready A-D dispatch packets from the committed preparation plan.

    python3 docs/orchestration/state/uncertainty-preparation-20261008/e/dispatch/make_dispatch.py
    python3 .../make_dispatch.py --check    # exit 1 if any packet differs from regenerated text

Each packet is a lane-specific header followed by plan sections copied verbatim from the plan blob
at the dispatch base, so a pasted goal cannot drift from the plan. The blob is read with
`git show`, never from the working tree, and is refused unless it is the expected object.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = "f8e2bf8535a90d7ed1315530cff3b80860ef9f9c"
PIN = "ad2716d8b7ac826c5c06690a5b7459ef04fa701b"
PLAN = "docs/orchestration/PLAN-20261008-uncertainty-investigation-preparation.md"
PLAN_BLOB = "fbbc0d656c4ef4793496d215dd5a65aae1a7b1b6"
E_BRANCH = "prep/uncertainty-e-20261008"
ROOT = "/Users/josephbailey/local-research"
E_WORKTREE = f"{ROOT}/MINERvA-OmniFold-uncertainty-planner-20261008"
P = "docs/orchestration/state/uncertainty-preparation-20261008"
OUT = Path(__file__).resolve().parent

SHARED_SECTIONS = (
    "## Baseline and evidence corrections",
    "## Common contract — paste with every goal",
    "## Dependency and ownership tables",
    "## Explicit preparation budgets",
)
RUBRIC = "## Final integration rubric"

LANES = {
    "A": {
        "title": "2D engineering and estimator pairing",
        "goal": "## Paste-ready goal A — 2D engineering and estimator pairing",
        "branch": "prep/uncertainty-a-pairing-20261008",
        "worktree": "MINERvA-OmniFold-uncprep-a-20261008",
        "model": "Opus 5.5 as the scientific owner",
        "owns": [
            "`docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md`",
            "`P/a/pairings.tsv`, `P/a/verification.md`",
            "conditionally, narrow edits to `2d-unfolding/unfold_2d_omnifold_unbinned.py`, "
            "`2d-unfolding/uq/analyze_uq.py`, `2d-unfolding/uq/analyze_universes.py`, "
            "`2d-unfolding/uq/rollup_vl170_adoption.sh` and "
            "`2d-unfolding/tests/test_bootstrap_completeness_ki84.py`, under the release rule below",
        ],
        "sequencing": [
            "Start at once on reading evidence, building `pairings.tsv`, and the checks the goal names "
            "(inspect each test before running it).",
            "Hold edits to the five conditional 2D paths until `[uncprep-D] INVENTORY` is on "
            "`origin/prep/uncertainty-d-navigation-20261008`. Each path that inventory does not claim is "
            "then released without asking anyone. A path it does claim stays deferred: record the conflict "
            "under a `## For E` heading in `P/a/verification.md` and carry on with the rest.",
            "Push `[uncprep-A] CONTRACT`, the frozen estimator contract section of your assessment, as soon "
            "as the evidence supports it. B and C find it by that subject marker and build on it.",
            "D routes proposed reference corrections to you for a factual check. Answer in "
            "`P/a/verification.md`; D stays the writer of the reference.",
            "If you hand D one of at most two existing non-frozen source files for a structural edit, "
            "record the exact path and the base commit of the handoff in `P/a/verification.md`.",
        ],
    },
    "B": {
        "title": "Independent statistical-validation design",
        "goal": "## Paste-ready goal B — Independent statistical-validation design",
        "branch": "prep/uncertainty-b-statval-20261008",
        "worktree": "MINERvA-OmniFold-uncprep-b-20261008",
        "model": "Opus 5.5 as the scientific owner",
        "owns": [
            "`docs/orchestration/DESIGN-20261008-2d-independent-statistical-validation.md`",
            "`P/b/populations.tsv`, `P/b/assurance.py`, `P/b/assurance.json`",
            "any additional operand fixture under `P/b/`, listed in your report",
        ],
        "sequencing": [
            "Start at once on the independent-population inventory and the provisional design.",
            "Exchange one provisional procedure/count/cost table with C: push `[uncprep-B] PROVISIONAL` "
            "and read C's from `origin/prep/uncertainty-c-total-20261008`.",
            "Freeze the estimator specification against A's `[uncprep-A] CONTRACT`, then reconcile once "
            "with C after A's `[uncprep-A] FREEZE`.",
            "If an input never arrives within budget, close the dependent conclusion under the "
            "missing-dependency rule; do not wait idle.",
        ],
    },
    "C": {
        "title": "Total-uncertainty feasibility",
        "goal": "## Paste-ready goal C — Total-uncertainty feasibility",
        "branch": "prep/uncertainty-c-total-20261008",
        "worktree": "MINERvA-OmniFold-uncprep-c-20261008",
        "model": "Opus 5.5 as the scientific owner",
        "owns": [
            "`docs/orchestration/ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md`",
            "`P/c/components.tsv`, `P/c/costs.json`, `P/c/costs.py`",
        ],
        "sequencing": [
            "Start at once on the source inventory and timing evidence.",
            "Exchange one provisional procedure/count/cost table with B: push `[uncprep-C] PROVISIONAL` "
            "and read B's from `origin/prep/uncertainty-b-statval-20261008`.",
            "Finalize costs against A's pairings (`[uncprep-A] CONTRACT`, then `FREEZE`) and B's "
            "procedure and counts, reconciling once after A freezes.",
            "If an input never arrives within budget, close the dependent conclusion under the "
            "missing-dependency rule; do not wait idle.",
        ],
    },
    "D": {
        "title": "Repository comprehensibility and targeted consolidation",
        "goal": "## Paste-ready goal D — Repository comprehensibility and targeted consolidation",
        "branch": "prep/uncertainty-d-navigation-20261008",
        "worktree": "MINERvA-OmniFold-uncprep-d-20261008",
        "model": "Opus 5.5, or a Sol-class model that escalates for scientific wording",
        "owns": [
            "`README.md`, `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, `docs/POST_PUBLICATION_REORG_PLAN.md`",
            "`P/d/dependencies.tsv`, `P/d/disposition.md`",
            "one existing workstream README, named in `P/d/disposition.md` before you edit it",
            "at most two existing non-frozen source files, each only after A records the exact transfer",
        ],
        "sequencing": [
            "First, an initial inventory of at most one active hour, charged to your six hours: the "
            "immediate dependency map, the supported-entrypoint list, the protected/frozen paths, and the "
            "exact proposed write ownership. Push it as `[uncprep-D] INVENTORY` (`P/d/dependencies.tsv` "
            "plus the ownership section of `P/d/disposition.md`). A's edits wait on this commit, so push it "
            "even if it is partial.",
            "Do not claim any of A's five conditional 2D paths in the inventory unless you are proposing a "
            "transfer. A claim defers A's edit to that path and goes to E.",
            "Then continue your improvements alongside A-C. Route proposed reference corrections to A for a "
            "factual check (read A's answers in `P/a/verification.md` on A's branch); you remain the writer.",
        ],
    },
}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def plan_sections(text: str) -> dict[str, str]:
    """Split the plan at its `## ` headings; each value keeps its heading line."""
    sections: dict[str, str] = {}
    current = None
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            current = line.rstrip("\n")
            sections[current] = ""
        if current is not None:
            sections[current] += line
    return sections


def header(x: str, lane: dict) -> str:
    lx = x.lower()
    owns = "\n".join(f"  - {item}" for item in lane["owns"])
    seq = "\n".join(f"- {item}" for item in lane["sequencing"])
    return f"""# Dispatch packet — Session {x}: {lane["title"]}

Prepared by E, the integration owner, on 2026-10-09 UTC. Paste this whole file as the session's goal.
It is a preparation task. It grants no compute and authorizes no experiment.

## Dispatch facts (measured by E; re-measure anything volatile)

- **Agreed base commit for A, B, C and D:** `{BASE}` on `{E_BRANCH}`. It is the plan pin `{PIN[:8]}`
  plus E's coordination commit (the plan, five `MANIFEST-overrides.tsv` rows, one `CATALOG.md` section,
  `P/e/integration.json`). No scientific source, product, receipt or governing record differs from the
  pin; `git diff --name-only {PIN[:8]} {BASE[:8]}` prints exactly those four paths.
- Remote `main` was checked once, at 2026-10-09T05:51:13Z, and equals the pin. Do not track moving
  `main` or rebase onto it. E reconciles any later upstream change at integration.
- The plan text after the divider is copied verbatim from `git show {BASE[:8]}:{PLAN}` (blob
  `{PLAN_BLOB[:8]}`). If the two ever disagree, the blob governs.
- E's baseline and ownership snapshot is `P/e/integration.json` at the base. `P` is `{P}/`.

## Setup

1. Measure free disk with `df -h` (45 GiB free at dispatch; a checkout is 0.4 GiB). Then:

       git -C {E_WORKTREE} fetch origin
       git -C {E_WORKTREE} worktree add -b {lane["branch"]} {ROOT}/{lane["worktree"]} {BASE}

   Work only in that worktree. Never edit the shared checkout `{ROOT}/MINERvA-OmniFold/`.
2. Use a dedicated temporary directory and the thread cap:

       export TMPDIR=/private/tmp/minerva-uncprep-{lx}-20261008/tmp && mkdir -p "$TMPDIR"
       export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4

   Copy any log you cite into `P/{lx}/` before deleting only that directory.
3. Commit as `git -c user.name="uncprep lane {x}" -c user.email="uncprep-{lx}@minerva-omnifold.invalid" commit ...`.
   Without it the commit takes the repository's unattributed fallback identity. Stage explicit paths
   only, never `-A`, `-u`, `.` or a directory, and read `git diff --cached --name-only` before each commit.
4. The pre-commit hook runs from the shared checkout's `.githooks`; all 13 of its checks pass at the
   base. E pre-registered every new `docs/orchestration/*.md` deliverable's overrides row and
   `CATALOG.md` entry, so do not edit `MANIFEST-overrides.tsv`, `MANIFEST.tsv` or `CATALOG.md`.
   `MANIFEST.tsv` is already out of date at the pin; leave it. A JSON file under `P/` that pairs
   `path`, `file` or `script` with `sha256` (or `<role>_path` with `<role>_sha256`) counts as a new
   receipt binding, and the hook refuses the changed inventory. Record digests in TSV or Markdown,
   or under unpaired keys as `P/e/integration.json` does. If a digest should be a verified receipt
   binding, raise it with E. Never edit `verify_hash_bindings.py`'s expected constants.
5. Deliver by pushing the branch: `git push -u origin {lane["branch"]}`. Do not force push, open a PR
   or merge. E integrates.

## Ownership at dispatch

- You write only:
{owns}
- Do not edit the other lanes' surfaces in the writer table below; the publication follow-up's
  `docs/analysis-note/`, `publication/release/`, `docs/publication/corrections-20261008/` and
  `MANIFEST.tsv`; E's surfaces; or anything on the plan's "No owner edits" list.
- At dispatch no worktree had uncommitted edits to any A-E surface and no live unmerged branch
  touched one. Recheck your own paths before the first edit.

## Sequencing

{seq}

Lanes coordinate through pushed commits on their own branches, not messages. Read another lane's
work with `git fetch origin` and `git show origin/<branch>:<path>`. Commit subjects that start with
these markers are the handoffs: `[uncprep-D] INVENTORY`, `[uncprep-A] CONTRACT`,
`[uncprep-B] PROVISIONAL`, `[uncprep-C] PROVISIONAL`, and `[uncprep-<lane>] FREEZE` for a lane's final
delivery. E integrates only `FREEZE` commits or terminal missing-dependency records. Anything for E
goes under a `## For E` heading in your own `P/{lx}/` record; the affected item stays deferred and you
continue with the rest.

## Session record

Owner/reviewer setup (CAMPAIGN-REVIEW-20260929 §1): you own this lane, and the single independent
review happens in E. Do not spawn reviewers or worker agents. Recommended starting point, advisory
under CAMPAIGN-REVIEW-20260929 §5: {lane["model"]}. In your terminal report, record the actual
model and version, effort, full session id, base and output commits, and resources measured against
your budget row, in addition to everything the common contract's terminal report requires.

---

"""


def render(x: str, sections: dict[str, str]) -> str:
    lane = LANES[x]
    body = [sections[name] for name in (*SHARED_SECTIONS, lane["goal"], RUBRIC)]
    return header(x, lane) + "".join(part if part.endswith("\n\n") else part + "\n" for part in body).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    blob = git("rev-parse", f"{BASE}:{PLAN}").strip()
    if blob != PLAN_BLOB:
        print(f"refused: {BASE[:8]}:{PLAN} is blob {blob}, expected {PLAN_BLOB}", file=sys.stderr)
        return 2
    sections = plan_sections(git("show", f"{BASE}:{PLAN}"))
    wanted = (*SHARED_SECTIONS, RUBRIC, *(lane["goal"] for lane in LANES.values()))
    missing = [name for name in wanted if name not in sections]
    if missing:
        print(f"refused: plan headings not found: {missing}", file=sys.stderr)
        return 2

    stale = []
    for x in LANES:
        target = OUT / f"DISPATCH-{x}.md"
        text = render(x, sections)
        if args.check:
            if not target.exists() or target.read_text() != text:
                stale.append(target.name)
        else:
            target.write_text(text)
            print(f"wrote {target.name}")
    if stale:
        print(f"OUT OF DATE: {', '.join(stale)}", file=sys.stderr)
        return 1
    if args.check:
        print("OK: every packet matches the plan blob")
    return 0


if __name__ == "__main__":
    sys.exit(main())
