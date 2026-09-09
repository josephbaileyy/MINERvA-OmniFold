#!/usr/bin/env python3
"""THE MUTATION TABLE for `whose_row.py`'s clean-merge terminal state, produced by REVERTING.

WHY THIS FILE EXISTS
--------------------
Every condition in `verify_clean_merge` is claimed to be load-bearing. A claim like that is worth
nothing until the condition is REMOVED and something is observed to fail: a condition whose removal
changes no verdict is a condition the suite is not testing, and this repository has twice recorded
guards that could not fail (`a-fixture-derived-from-the-rule`, and the 178 controls that missed an
unsatisfiable guard). So this driver reverts one condition at a time and records WHICH TESTS DIE.
Rows where nothing dies are printed as UNKILLED and are findings, not footnotes.

A MUTATED GATE NEVER EXISTS INSIDE THE REPOSITORY
-------------------------------------------------
Each mutant is written into a throwaway directory OUTSIDE the working tree and the suite is pointed
at it with `MNV_CLEAN_MERGE_GATE_SRC`, which `test_whose_row_clean_merge.py` reads for exactly this
purpose. The driver refuses to run if that directory would land inside the repository, and it digests
the host repository's `config`, `config.worktree`, `index` and `--is-bare-repository` around the
whole run: on 2026-09-08 a fixture in a linked worktree wrote `core.bare=true` into a SHARED
`.git/config` and broke an unrelated checkout, so "my harness cannot reach the host" is measured
here rather than asserted.

EACH MUTATION IS CHECKED BEFORE IT IS TRUSTED
---------------------------------------------
A replacement that no longer matches the source would silently produce an UNMUTATED copy, and an
unmutated copy passes every test -- which would be reported as "this condition is untested" when in
fact the mutation never happened. So every replacement must match EXACTLY ONCE, the mutant must
differ from the original, and it must compile. Any of those failing is a hard error, not a row.

THE RUNS ARE SEQUENTIAL, DELIBERATELY. `test_the_gate_writes_neither_the_index_nor_the_working_tree`
lists the system temp directory before and after and asserts the gate left no `whose_row-mergecheck-`
directory behind. A concurrent run's live scratch directory would be visible in that window and the
test would fail for a reason that has nothing to do with the mutant, quietly corrupting the table.

    python3 docs/orchestration/mutation_whose_row_clean_merge.py            # the whole table
    python3 docs/orchestration/mutation_whose_row_clean_merge.py --list
    python3 docs/orchestration/mutation_whose_row_clean_merge.py --only C7 --keep
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GATE = HERE / "whose_row.py"
SUITE = HERE / "test_whose_row_clean_merge.py"
FAILED = re.compile(r"^(?:FAILED|ERROR)\s+\S+::(?:\S+::)?(\w+)")


class Mutation(NamedTuple):
    row: str                       # the condition, as the report names it
    arm: str                       # which arm of it, when a condition has more than one
    reverts: str                   # what the revert restores, in one line
    edits: tuple[tuple[str, str], ...]


def _unless(condition: str) -> tuple[str, str]:
    """Make a guard unreachable while keeping the block, the message and the indentation intact.

    `if X:` -> `if False and X:`. A deleted block would also delete the return inside it and change
    the function's shape; this changes exactly one thing -- whether the condition can ever speak.
    """
    return condition, condition.replace("if ", "if False and ", 1)


MUTATIONS: tuple[Mutation, ...] = (
    Mutation("IDENTITY", "no mutation",
             "nothing -- the control that proves the swap harness itself passes", ()),

    Mutation("C1", "a merge is in progress",
             "certifying when there is no MERGE_HEAD at all (a fast-forward, or an "
             "already-committed merge)",
             (_unless("        if not mh_path.exists():"),)),

    Mutation("C1", "exactly two parents",
             "reconstructing an octopus merge with a two-parent facility",
             (_unless("        if len(heads) != 1:"),)),

    Mutation("C2", "the reconstruction is isolated",
             "the pre-8fef9d8e/e19822f2 form: `merge-tree` in the OPERATOR'S repository, under "
             "their config, attributes and HOME",
             (('rc, out, err = _git(["merge-tree", "--write-tree", head, merge_head], iso,\n'
               '                            env_full=iso_env)',
               'rc, out, err = _git(["merge-tree", "--write-tree", head, merge_head], repo)'),)),

    Mutation("C2", "the isolation is PROVEN",
             "trusting the isolated repository instead of measuring it -- an unprovable "
             "environment would certify",
             (_unless("        if why_not:"),)),

    Mutation("C3", "the reconstruction was conflict-FREE",
             "treating a CONFLICTED reconstruction as a clean one, so only the tree comparison "
             "stands between a hand resolution and a certificate",
             (("        # ---- C3: and it was conflict-FREE ---------"
               "-----------------------------------------------\n        if rc == 1:",
               "        # ---- C3: and it was conflict-FREE ---------"
               "-----------------------------------------------\n        if False and rc == 1:"),)),

    Mutation("C4", "staged tree == reconstruction",
             "certifying a staged tree that is NOT the reconstruction: any edit on top of the "
             "automatic merge",
             (_unless("        if staged != reconstructed:"),)),

    Mutation("C5(ii)", "zero unmerged entries",
             "losing the second, independent measurement of the unmerged set -- the report calls "
             "this arm's exit-code effect masked, and this row is where that is confirmed or not",
             (_unless("        if entries:"),)),

    Mutation("C5(iii)", "the reconstruction's scope is enumerable",
             "printing an empty scope when `diff-tree` against the reconstructed tree failed, so "
             "the pass would name nothing it looked at",
             (('rc, out, err = _git(["diff-tree", "-r", "-z", "--no-commit-id", "--name-only",\n'
               '                             head + "^{tree}", reconstructed], iso, '
               'env_full=iso_env)\n        if rc != 0:',
               'rc, out, err = _git(["diff-tree", "-r", "-z", "--no-commit-id", "--name-only",\n'
               '                             head + "^{tree}", reconstructed], iso, '
               'env_full=iso_env)\n        if False and rc != 0:'),)),

    Mutation("C6", "tracked working tree == index",
             "the pre-e19822f2 form: certifying the INDEX while `git commit -a` would record "
             "something else",
             (_unless("        if drift:"),)),

    Mutation("C7", "committed merge attributes refuse",
             "the whole of finding 3: a committed conflict-forcing attribute launders a "
             "hand-resolved conflict",
             (_unless('                if value != "unspecified":'),)),

    Mutation("C7", "the attribute query must succeed",
             "certifying git's BUILT-IN default semantics when the attribute query itself failed",
             (_unless("            if rc != 0 or not out.endswith(\"\\0\") or len(fields) != "
                      "len(batch) * len(attrs) * 3:"),)),

    Mutation("C7", "the changed-scope enumeration must succeed",
             "an empty checked scope when `diff-tree` failed OR skipped rename detection, which "
             "reads as `no path was content-merged, so no attribute can matter`",
             ((('        rc, out, err = _git(\n'
                '            ["diff-tree", "-r", "-z", "-M", "-l0", "--no-commit-id", '
                '"--name-status",\n'
                '             bases[0], parent], iso, env_full=env\n'
                '        )\n'
                '        if rc != 0 or err.strip():'),
               ('        rc, out, err = _git(\n'
                '            ["diff-tree", "-r", "-z", "-M", "-l0", "--no-commit-id", '
                '"--name-status",\n'
                '             bases[0], parent], iso, env_full=env\n'
                '        )\n'
                '        if False and (rc != 0 or err.strip()):')),)),

    Mutation("C7", "scope = both sides, not the union",
             "419e4ed9's union scope, which refuses a clean merge whenever an attributed path "
             "moved on ONE side -- unreachable green on this repository's `*.pdf binary`",
             (("    content_merged = sides[0] & sides[1]",
               "    content_merged = sides[0] | sides[1]"),)),

    Mutation("C7", "rename destinations are in scope",
             "a scope of intersecting PATHS ALONE, which misses an attribute on the destination "
             "git merged INTO",
             (("    content_merged |= {dst for src in tuple(content_merged) "
               "for dst in renames.get(src, ())}",
               "    pass  # MUTATION: rename destinations dropped from the checked scope"),)),

    Mutation("C7", "one merge base, both repositories",
             "certifying a criss-cross history, where `merge-tree` picks a base that need not be "
             "the one the operator's merge used",
             (_unless("    if rc != 0 or len(bases) != 1 or tuple(out.split()) != bases:"),)),

    Mutation("C7", "no local graph override",
             "certifying while a replace ref rewrites the graph in the operator's repository but "
             "not in the reconstruction",
             ((('    rc, out, err = _git(["for-each-ref", "--format=%(refname)", "refs/replace/"], '
                'repo)\n    if rc != 0 or out.strip():'),
               ('    rc, out, err = _git(["for-each-ref", "--format=%(refname)", "refs/replace/"], '
                'repo)\n    if False and (rc != 0 or out.strip()):')),)),
)


def host_state() -> dict[str, str]:
    """The state this driver must never touch, digested. Same instrument as the suite's."""
    state: dict[str, str] = {}
    for label in ("config", "config.worktree", "index"):
        r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-path", label],
                           capture_output=True, text=True)
        path = Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
        if path is None:
            state[label] = f"unlocatable (rc={r.returncode})"
            continue
        if not path.is_absolute():
            path = REPO / path
        state[label] = (hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.is_file()
                        else "absent")
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--is-bare-repository"],
                       capture_output=True, text=True)
    state["is-bare-repository"] = r.stdout.strip() or f"rc={r.returncode}"
    return state


def build(mutation: Mutation, into: Path) -> Path:
    source = GATE.read_text(encoding="utf-8")
    mutated = source
    for old, new in mutation.edits:
        hits = mutated.count(old)
        if hits != 1:
            raise SystemExit(
                f"MUTATION {mutation.row} / {mutation.arm} IS STALE: its anchor matches {hits} "
                f"times in {GATE}, not once. A non-matching anchor would leave the gate UNMUTATED "
                f"and the row would read 'nothing failed' for a mutation that never happened.\n"
                f"anchor:\n{old}")
        mutated = mutated.replace(old, new)
    if mutation.edits and mutated == source:
        raise SystemExit(f"MUTATION {mutation.row} / {mutation.arm} changed nothing")
    if not mutation.edits and mutated != source:
        raise SystemExit("the IDENTITY control is not identical")
    compile(mutated, str(into), "exec")          # a mutant that cannot parse is not evidence
    into.write_text(mutated, encoding="utf-8")
    return into


def run_suite(gate_src: Path, timeout: int) -> tuple[int, list[str], str]:
    env = dict(os.environ, MNV_CLEAN_MERGE_GATE_SRC=str(gate_src))
    env.pop("MNV_LANE", None)
    started = time.time()
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", str(SUITE), "-q", "--tb=no",
             "-p", "no:cacheprovider"],
            cwd=REPO, capture_output=True, text=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -1, ["<TIMEOUT>"], f"timed out after {timeout}s"
    dead = sorted({m.group(1) for m in (FAILED.match(l) for l in r.stdout.splitlines()) if m})
    tail = [l for l in r.stdout.splitlines() if " passed" in l or " failed" in l or " error" in l]
    return r.returncode, dead, f"{(tail or ['(no summary)'])[-1].strip()}  [{time.time()-started:.0f}s]"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print the mutations and exit")
    ap.add_argument("--only", default=None, help="only rows whose condition starts with this")
    ap.add_argument("--keep", action="store_true", help="keep the mutants for probing by hand")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--out", default=None, help="directory for mutation-table.md / .json")
    args = ap.parse_args()

    chosen = [m for m in MUTATIONS
              if args.only is None or m.row.startswith(args.only) or m.row == "IDENTITY"]
    if args.list:
        for m in chosen:
            print(f"{m.row:9} {m.arm:34} reverting restores: {m.reverts}")
        return 0

    work = Path(tempfile.mkdtemp(prefix="whose-row-mutants-")).resolve()
    if work == REPO or REPO in work.parents:
        raise SystemExit(f"REFUSING: the mutant directory {work} is inside the repository {REPO}. "
                         f"A mutated gate must never exist inside the working tree.")
    before = host_state()
    print(f"gate      {GATE}")
    print(f"mutants   {work}   (outside {REPO})")
    print(f"host      {before}")
    print(f"tip       {subprocess.run(['git', '-C', str(REPO), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
    print()

    rows = []
    for m in chosen:
        tag = re.sub(r"[^A-Za-z0-9]+", "_", f"{m.row}_{m.arm}").strip("_")
        mutant = build(m, work / f"whose_row__{tag}.py")
        rc, dead, summary = run_suite(mutant, args.timeout)
        killed = bool(dead) if m.row != "IDENTITY" else not dead
        rows.append({"row": m.row, "arm": m.arm, "reverts": m.reverts, "rc": rc,
                     "killed_by": dead, "summary": summary, "mutant": str(mutant),
                     "verdict": ("KILLED" if dead else "UNKILLED") if m.row != "IDENTITY"
                                else ("CLEAN" if not dead else "HARNESS BROKEN")})
        mark = rows[-1]["verdict"]
        print(f"{m.row:9} {m.arm:34} {mark:14} {summary}")
        for name in dead:
            print(f"{'':9} {'':34}   <- {name}")
        print(flush=True)

    after = host_state()
    if before != after:
        print("HOST MOVED DURING THE MUTATION RUN -- the table is void until this is explained:")
        print(f"  before {before}\n  after  {after}")
        return 1
    print(f"host UNCHANGED across the whole run: {after}")

    unkilled = [r for r in rows if r["verdict"] == "UNKILLED"]
    table = ["| condition | arm | reverting it restores | killed by |",
             "|---|---|---|---|"]
    for r in rows:
        if r["row"] == "IDENTITY":
            continue
        names = "<br>".join(f"`{n}`" for n in r["killed_by"]) or "**NOTHING -- UNKILLED**"
        table.append(f"| {r['row']} | {r['arm']} | {r['reverts']} | {names} |")
    print()
    print("\n".join(table))
    if unkilled:
        print(f"\n{len(unkilled)} UNKILLED MUTANT(S): "
              + "; ".join(f"{r['row']}/{r['arm']}" for r in unkilled)
              + " -- each is a condition this suite does not test.")

    if args.out:
        out = Path(args.out)
        (out / "mutation-table.md").write_text("\n".join(table) + "\n", encoding="utf-8")
        (out / "mutation-run.json").write_text(json.dumps(
            {"gate": str(GATE), "host_before": before, "host_after": after, "rows": rows},
            indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {out / 'mutation-table.md'} and {out / 'mutation-run.json'}")
    if args.keep:
        print(f"mutants kept at {work}")
    else:
        shutil.rmtree(work, ignore_errors=True)
    return 1 if unkilled else 0


if __name__ == "__main__":
    raise SystemExit(main())
