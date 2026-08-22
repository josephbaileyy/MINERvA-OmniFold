#!/usr/bin/env python3
"""OI-136: run an entrypoint and REFUSE if it imports modules from another checkout.

THE DEFECT THIS CLOSES
----------------------
59 of the `.py` files in this tree put an ABSOLUTE path under the hardcoded root
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` at `sys.path[0]`. An absolute
`insert(0, ...)` executes THAT tree's modules no matter which checkout the
entrypoint was launched from, and `PYTHONPATH` cannot outrank position 0. So
`OI-123`'s remedy -- give every leg its own checkout -- does not help, and a
deployment-parity check can report every pinned file CURRENT while the interpreter
imports a different file entirely.

That is measured, not hypothetical. Run `57266000_0` (2026-08-19/20, 3 h 08 m of
A100) printed `deployment parity CURRENT for all pinned executing copies` and
`5 of 5 CURRENT` against the frozen tree `gate5-data-only-frozen-377c713`, then
failed on a guard that the frozen tree's `cstat_data_only.py` CANNOT RAISE: its
`DATA_ONLY_WITHHELD_REQUIRED_KEYS` is empty. The message it actually printed
carries the suffix `; the seed lives under \\`data_bootstrap_seed\\` (P6)`, which
exists only in the PRE-fix blob at `1f6aa9c6^`. The import resolved to the
hardcoded main checkout, 211 commits behind.

WHY A NEW ENTRYPOINT AND NOT AN EDIT TO THE 59
----------------------------------------------
Deriving the root from `__file__` in each of the 59 is the correct END state and is
NOT what this file does. Those are hash-pinned science files inside frozen
provenance; a 59-file sweep needs its own per-site authorization and would be a
larger change than the incident it repairs. What this file does is convert the
FAIL-OPEN direction into the fail-CLOSED one, which is the whole difference
`OI-136` records between itself and `OI-123`: OI-123 dies at exit 3 before any GPU
work, while this family runs to completion and produces numbers. After this, so
does this family.

IT DOES NOT REPLACE THE PARITY CHECK AND IT IS NOT REDUNDANT WITH IT.
`verify_executing_copy_is_committed.py` answers "are the FILES AT THESE PATHS the
committed ones". This answers "are the MODULES THE INTERPRETER ACTUALLY LOADED
from the tree we think we are running". Run 4 proves those are two different
questions: the first passed honestly, five for five, while the second was false.
Adding another `--pair` would not have caught it, and neither would a re-deploy.

WHAT IT REFUSES, AND WHAT IT DELIBERATELY IGNORES
-------------------------------------------------
A module is refused when its resolved origin lies inside a MINERvA-OmniFold
CHECKOUT (a directory holding both `VALIDATION_LEDGER.md` and `nd-unfolding/`)
whose root is neither `--expect-root` nor an explicit `--allow`. The stdlib,
site-packages, conda and any path outside a checkout are IGNORED, because they are
not the confusion this exists for and flagging them would make the guard something
people switch off.

IT DOES NOT CROSS A SUBPROCESS BOUNDARY, AND THAT IS MEASURED, NOT SUSPECTED.
The wrapped `PathFinder` lives in THIS interpreter's `sys.meta_path`. A child started
with `subprocess.run([sys.executable, ...])` gets a fresh interpreter with a clean
`sys.meta_path`, so a rooted `insert(0, ...)` inside the CHILD is not seen and this
wrapper exits 0. Fixture: a correct parent that resolves its own directory from
`__file__` and then subprocess-launches a child which inserts another checkout at
position 0 -- guarded IN-PROCESS it exits 3; guarded through the SUBPROCESS it exits 0
and the child loads the other tree's module. Both halves are asserted in
`tests/test_mnv_guarded_run.py::TheSubprocessBoundaryIsNotCovered`.

THIS IS LIVE IN THIS REPO, NOT A TOY. `mii_adopt_unified_5d_stamped.py:124` resolves
`adopt_unified_5d.py` from its own `_HERE` -- correctly -- and then runs it AS A
SUBPROCESS, deliberately, so that the bytes whose sha256 is pinned are the bytes that
execute. `adopt_unified_5d.py` is one of the fail-open 59. So wrapping that adoption
path in this guard would print a clean banner and refuse nothing. Anyone routing a
launcher through this wrapper must check whether the work happens in the wrapped
interpreter or in a child; if it is a child, this guard is not the check they want and
a green run of it must not be recorded as one.

The marker pair is chosen to hold across checkout GENERATIONS, not just today's:
both files predate every frozen tree on scratch. `AGENTS.md` would have been the
obvious marker and is the wrong one -- it was rewritten as the thin front door on
2026-08-20, so a tree frozen on 2026-08-18 is still a real checkout that a fresh
marker would fail to recognise, and the guard would then wave it through.

IT NOW ALSO REFUSES A SCRIPT THAT IS NOT IN THE EXPECTED TREE (added 2026-08-22, B-4).
Until then this file checked only what was IMPORTED, never what was RUN. For an entrypoint with
repository imports that failed closed by accident at the first import; for one with NONE it did not
fail at all, and running the forbidden checkout's own copy of such an entrypoint with
`--expect-root <clean tree>` exited 0. The check is made BEFORE `install()`, so the refusal precedes
the first import as well as the work. `--allow` does not cover it: `--allow` declares an IMPORT tree
and has never declared an execution tree.

IT NOW EMITS A RESOLVED-ORIGIN INVENTORY (added 2026-08-22, P-1), and that is the POSITIVE half.
`--inventory <path>` (or `$MNV_GUARD_INVENTORY`) appends ONE json object per process recording the
interpreter, both roots, the script and its checkout root, `checked`, the final `sys.path`, and
EVERY module whose resolved origin lies inside any checkout -- the allowed ones as well as the
refused one. Before this, `checked` was incremented and read nowhere, so a production run emitted
nothing that could distinguish "checked many imports, all clean" from "checked nothing", and an
exit 0 was not evidence. `repo_origin_count` and `repo_origin_inventory_is_empty` are written
UNCONDITIONALLY: a zero is a REPORTABLE STATE and never a pass, and an absent key cannot tell
"no repository import occurred" from "the inventory did not run".

USAGE, AND THE `--` IS MANDATORY
--------------------------------
    mnv_guarded_run.py --expect-root <tree> [--allow <tree> ...] [--inventory <path>] \
                       -- <script> [argv ...]

The `--` split and the refusal of bare positionals are copied deliberately from
`mii_adopt_unified_5d_stamped.py:431-437`, whose comment records why: a wrapper
that quietly swallows a child flag builds one product under another product's
name. Everything after `--` is forwarded to the child VERBATIM, including strings
that look like this wrapper's own options.

EXIT CODES follow `verify_executing_copy_is_committed.py` rather than inventing a
third convention:
    0 or the child's own status -- the child ran; its SystemExit is preserved
    2 -- COULD NOT LOOK (bad usage, or --expect-root is not a checkout)
    3 -- MEASURED VIOLATION: an import resolved outside the expected tree, OR the script itself
         lies in a checkout that is not --expect-root
2 is deliberately not 3, so "we could not check" can never be read as "we checked
and it was clean".
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import runpy
import sys

MARKERS = ("VALIDATION_LEDGER.md", "nd-unfolding")

VIOLATION_EXIT = 3
CANNOT_CHECK_EXIT = 2

#: Environment fallback for `--inventory`. A flag OR an env var, because the launcher that needs the
#: record and the wrapper invocation that emits it are edited by different hands.
INVENTORY_ENV = "MNV_GUARD_INVENTORY"

#: The two `verdict` values a GREEN run can carry. They exist because they must be DISTINGUISHABLE:
#: an exit 0 from a process that inspected repository imports and approved every one of them, and an
#: exit 0 from a process that never resolved a repository import at all, are the same exit code and
#: the same refusal count (zero) and are completely different evidence. `adopt_unified_5d.py` is the
#: measured instance of the second (REVIEW-CONTRACT-20260822 M-1: its import list is
#: `argparse, gc, os, sys, numpy` before the insert and `ROOT` after it -- no repository module at
#: all), and reading its clean run as a measurement of the tree is the exact claim P-1 exists to
#: prevent. An ABSENT key cannot make that distinction either, which is why `repo_origin_count` and
#: `repo_origin_inventory_is_empty` are written UNCONDITIONALLY -- the same reasoning
#: `adopt_unified_5d.py:200-206` already applies to its own `*_checked` flags.
VERDICT_INSPECTED = "REPOSITORY-ORIGINS-INSPECTED"
VERDICT_EMPTY = "EMPTY-REPOSITORY-ORIGIN-SET -- THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING"
VERDICT_REFUSED = "REFUSED -- AN IMPORT RESOLVED OUTSIDE THE EXPECTED TREE"


class ImportTreeViolation(Exception):
    """An import resolved inside a checkout that is not the expected one."""

    def __init__(self, module: str, origin: str, found_root: str, expect_root: str):
        self.module = module
        self.origin = origin
        self.found_root = found_root
        self.expect_root = expect_root
        super().__init__(f"{module} resolved to {origin} under {found_root}")


def is_checkout(path: pathlib.Path) -> bool:
    """A directory is a checkout when EVERY marker is present, not any.

    `any` would match `nd-unfolding/` itself, whose parent chain then stops one
    level too early and makes every module in it look like its own checkout root.
    """
    return all((path / m).exists() for m in MARKERS)


def checkout_root_of(path: str, _cache: dict[str, str | None] | None = None) -> str | None:
    """The checkout root containing `path`, or None when it is outside every checkout.

    Walks up from the file. The FIRST matching ancestor wins, which is what makes a
    frozen deployment inside another directory resolve to itself rather than to
    whatever happens to sit above it.
    """
    cache = _cache if _cache is not None else _ROOT_CACHE
    try:
        here = pathlib.Path(path).resolve().parent
    except OSError:
        return None
    key = str(here)
    if key in cache:
        return cache[key]
    chain = []
    cur = here
    while True:
        chain.append(str(cur))
        if str(cur) in cache:
            found = cache[str(cur)]
            break
        if is_checkout(cur):
            found = str(cur)
            break
        if cur.parent == cur:
            found = None
            break
        cur = cur.parent
    for k in chain:
        cache.setdefault(k, found)
    return found


_ROOT_CACHE: dict[str, str | None] = {}


class GuardedPathFinder:
    """Wraps the stdlib `PathFinder` so the guard sees the RESOLVED origin.

    Position matters and is the reason this wraps rather than prepends. A finder
    inserted at `sys.meta_path[0]` would shadow `BuiltinImporter` and
    `FrozenImporter` and have to reimplement them; wrapping the path-based finder
    in place leaves every other finder exactly where it was, and means the origin
    checked is the one the import system would actually have used.
    """

    def __init__(self, inner, expect_root: str, allowed: frozenset[str]):
        self._inner = inner
        self.expect_root = expect_root
        self.allowed = allowed
        self.checked = 0
        #: P-1: EVERY module whose resolved origin lies inside ANY checkout, including
        #: `--expect-root`. The allowed ones are the POSITIVE evidence and they were previously
        #: discarded -- `checked` was incremented at this method and read nowhere in `main()`, so a
        #: production guarded run emitted no artifact distinguishing "checked many imports, all
        #: clean" from "checked nothing" (REVIEW-CONTRACT-20260822 M-6). Order is import order.
        self.repo_origins: list[dict] = []
        self._seen: set[tuple[str, str]] = set()

    def find_spec(self, fullname, path=None, target=None):
        spec = self._inner.find_spec(fullname, path, target)
        if spec is None:
            return None
        origin = getattr(spec, "origin", None)
        if not origin or origin in ("built-in", "frozen", "namespace"):
            return spec
        if not os.path.isabs(origin):
            return spec
        self.checked += 1
        root = checkout_root_of(origin)
        if root is None:
            return spec
        # RECORDED BEFORE THE REFUSAL DECISION, deliberately: the refused module has to appear in
        # the inventory too, or the record of a red run is thinner than the record of a green one.
        key = (fullname, origin)
        if key not in self._seen:
            self._seen.add(key)
            self.repo_origins.append({
                "fullname": fullname,
                "origin": origin,
                "checkout_root": root,
                "sha256": _sha256_or_none(origin),
                "under_expect_root": root == self.expect_root,
                "allowed": root in self.allowed,
            })
        if root not in self.allowed:
            raise ImportTreeViolation(fullname, origin, root, self.expect_root)
        return spec

    def invalidate_caches(self):
        inv = getattr(self._inner, "invalidate_caches", None)
        if inv is not None:
            inv()


def install(expect_root: str, allow=()) -> GuardedPathFinder:
    """Wrap the path-based finder in place. Returns the installed guard."""
    allowed = frozenset({expect_root, *(str(pathlib.Path(a).resolve()) for a in allow)})
    for i, finder in enumerate(sys.meta_path):
        if getattr(finder, "__name__", None) == "PathFinder" or type(finder).__name__ == "PathFinder":
            guard = GuardedPathFinder(finder, expect_root, allowed)
            sys.meta_path[i] = guard
            return guard
    # No PathFinder is not a clean tree, it is an interpreter we do not understand.
    raise RuntimeError("no PathFinder in sys.meta_path; refusing to run unguarded")


def _sha256_or_none(path: str) -> str | None:
    """sha256 of a resolved origin, or None when it cannot be read.

    None rather than a raised exception: an unreadable origin must not turn a guarded science run
    into a crash, and a `null` in the record is a statement that the digest is MISSING. An absent
    key would be indistinguishable from "the inventory did not look".
    """
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def write_inventory(dest, guard, script, expect_root, allow, outcome, violation=None) -> str | None:
    """P-1: append ONE json object, on ONE line, describing THIS process. Returns the path written.

    APPEND MODE AND ONE LINE PER PROCESS, because a run is many processes and the reviewer's F-4 is
    `count of inventories == count of guarded processes`. A truncating write would make the last
    process the only evidence and the loss would be silent.

    IT IS WRITTEN ON EVERY EXIT PATH INCLUDING THE REFUSAL, from a `finally`. An inventory that only
    appears on success cannot be used to establish anything about a run that failed.

    THE EMPTY CASE IS FLAGGED, NOT SILENT. See VERDICT_EMPTY.
    """
    if not dest:
        return None
    origins = list(guard.repo_origins) if guard is not None else []
    outside = [o for o in origins if not o["under_expect_root"]]
    record = {
        "schema": "mnv_guard_inventory/1",
        "written_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pid": os.getpid(),
        "interpreter": {"executable": sys.executable, "version": sys.version},
        "expect_root": expect_root,
        "allow": list(allow),
        "allow_is_empty": not list(allow),
        "script": str(script) if script is not None else None,
        "script_checkout_root": (checkout_root_of(str(pathlib.Path(script).resolve()))
                                 if script is not None else None),
        "script_sha256": _sha256_or_none(str(script)) if script is not None else None,
        "checked": (guard.checked if guard is not None else 0),
        "guard_installed": guard is not None,
        # WRITTEN UNCONDITIONALLY (P-3). A zero here is a REPORTABLE STATE, never a pass.
        "repo_origin_count": len(origins),
        "repo_origin_inventory_is_empty": not origins,
        "repo_origins_outside_expect_root": len(outside),
        "repo_origins": origins,
        "outcome": outcome,
        "verdict": (VERDICT_REFUSED if violation is not None
                    else (VERDICT_INSPECTED if origins else VERDICT_EMPTY)),
        "violation": (None if violation is None else {
            "module": violation.module, "origin": violation.origin,
            "found_root": violation.found_root, "expect_root": violation.expect_root}),
        "sys_path_final": list(sys.path),
    }
    d = os.path.dirname(os.path.abspath(dest))
    if d:
        os.makedirs(d, exist_ok=True)
    with open(dest, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=False) + "\n")
    # ALSO ANNOUNCED ON stderr, unconditionally. The record is the evidence; this line is what stops
    # a reader of a Slurm .out file from mistaking a vacuous green run for a measured one.
    print(f"[oi136] inventory: checked={record['checked']} "
          f"repo_origin_count={record['repo_origin_count']} "
          f"outside_expect_root={record['repo_origins_outside_expect_root']} "
          f"verdict={record['verdict']} -> {dest}", file=sys.stderr)
    return dest


def _safe_inventory(*a, **kw) -> bool:
    """`write_inventory`, but an OSError becomes a LOUD FAILURE FLAG instead of a traceback.

    Two things must both hold and they pull in opposite directions. A record that cannot be written
    must never turn a MEASURED VIOLATION into some other exit code -- exit 3 is the finding and it
    outranks the bookkeeping. And a run that emits NO record must never read as a clean pass, since
    "no inventory" and "an inventory showing nothing" are the two states P-1 exists to separate. So
    the failure is announced here and the caller downgrades a would-be 0 to CANNOT_CHECK (2), while
    a 3 stays 3.
    """
    try:
        write_inventory(*a, **kw)
        return True
    except OSError as err:
        print(f"\n[oi136] INVENTORY WRITE FAILED: {err}\n"
              "[oi136] A guarded run that emits no record establishes nothing about the import\n"
              "[oi136] tree. This is reported as COULD NOT LOOK, never as a clean run.\n",
              file=sys.stderr)
        return False


def _report(exc: ImportTreeViolation) -> None:
    print(
        "\n[oi136] IMPORT TREE VIOLATION -- REFUSING BEFORE THE WORK RUNS.\n"
        f"[oi136]   module        {exc.module}\n"
        f"[oi136]   resolved to   {exc.origin}\n"
        f"[oi136]   which is in   {exc.found_root}\n"
        f"[oi136]   expected      {exc.expect_root}\n"
        "[oi136] A HARDCODED sys.path.insert(0, ...) IS THE USUAL CAUSE, and a re-deploy will\n"
        "[oi136] NOT fix it: an absolute insert at position 0 is not escaped by launching from\n"
        "[oi136] another checkout and cannot be outranked by PYTHONPATH. Deployment parity can\n"
        "[oi136] report every pinned file CURRENT while this is false -- that is OI-136, and it\n"
        "[oi136] cost 3 h 08 m of A100 on 57266000_0. Fix the insert in the importing file, or\n"
        "[oi136] pass --allow if this tree is genuinely intended.\n",
        file=sys.stderr,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="mnv_guarded_run.py",
        description="Run a script and refuse imports from another checkout (OI-136).",
    )
    ap.add_argument("--expect-root", required=True)
    ap.add_argument("--allow", action="append", default=[])
    ap.add_argument("--inventory", default=os.environ.get(INVENTORY_ENV) or None,
                    help="P-1 resolved-origin inventory: append one JSON object for this process "
                         f"to this path. Defaults to ${INVENTORY_ENV}. When neither is set NO "
                         "record is written, and a run with no record establishes nothing.")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    dest = args.inventory
    guard = None
    script = None

    rest = list(args.rest)
    if not rest or rest[0] != "--":
        print("[oi136] usage: --expect-root <tree> [--allow <tree>] -- <script> [argv ...]\n"
              "[oi136] the `--` is MANDATORY and bare positionals are refused, so a child flag\n"
              "[oi136] can never be silently eaten by this wrapper (see remedy (A)'s wrapper).",
              file=sys.stderr)
        _safe_inventory(dest, None, None, args.expect_root, args.allow, "cannot-check:usage")
        return CANNOT_CHECK_EXIT
    rest = rest[1:]
    if not rest:
        print("[oi136] nothing to run after `--`", file=sys.stderr)
        _safe_inventory(dest, None, None, args.expect_root, args.allow,
                        "cannot-check:nothing-after-split")
        return CANNOT_CHECK_EXIT

    expect = pathlib.Path(args.expect_root).resolve()
    if not is_checkout(expect):
        print(f"[oi136] COULD NOT LOOK: --expect-root {expect} is not a checkout "
              f"(needs {' and '.join(MARKERS)}). Exit 2 and not 3 on purpose: this is "
              f"'we could not check', never 'we checked and it was clean'.", file=sys.stderr)
        _safe_inventory(dest, None, None, str(expect), args.allow,
                        "cannot-check:expect-root-is-not-a-checkout")
        return CANNOT_CHECK_EXIT

    script = pathlib.Path(rest[0])
    if not script.is_file():
        print(f"[oi136] COULD NOT LOOK: no such script {script}", file=sys.stderr)
        _safe_inventory(dest, None, None, str(expect), args.allow, "cannot-check:no-such-script")
        return CANNOT_CHECK_EXIT

    # B-4, ADDED 2026-08-22 (REVIEW-CONTRACT-20260822 M-7 and B-4; Joseph's correction 3).
    # THE GUARD USED TO CHECK ONLY WHAT WAS IMPORTED, NEVER WHAT WAS RUN. For an entrypoint that
    # imports repository modules this failed closed by accident, at the first import. For one that
    # imports NONE -- `adopt_unified_5d.py` is the measured instance -- running the FORBIDDEN
    # checkout's own copy of it with `--expect-root <clean tree>` exited 0, and the guard did not
    # notice that the executing file came from the tree the run was supposed to avoid. That is the
    # single largest hole in the wrapper design and it is closed here, BEFORE `install()`, so the
    # refusal precedes not just the work but the first import.
    #
    # `--allow` DELIBERATELY DOES NOT EXTEND TO THE SCRIPT. `--allow` says "modules from this other
    # tree are intended"; it has never said "run the entrypoint from somewhere else", and on a
    # production arm `--allow` is forbidden outright. A script outside EVERY checkout is NOT refused
    # here -- `checkout_root_of` returns None and there is no other tree to have come from -- but
    # that fact is recorded in the inventory as `script_checkout_root: null` rather than left to be
    # inferred from silence.
    script_root = checkout_root_of(str(script.resolve()))
    if script_root is not None and script_root != str(expect):
        print(f"\n[oi136] SCRIPT OUTSIDE THE EXPECTED TREE -- REFUSING BEFORE THE FIRST IMPORT.\n"
              f"[oi136]   script        {script.resolve()}\n"
              f"[oi136]   which is in   {script_root}\n"
              f"[oi136]   expected      {expect}\n"
              "[oi136] The file that EXECUTES is not the file that was approved. An entrypoint with\n"
              "[oi136] no repository imports gives this guard nothing to resolve, so without this\n"
              "[oi136] check it would have exited 0 while running the wrong tree's copy. --allow\n"
              "[oi136] does not cover this: it declares an IMPORT tree, never an execution tree.\n",
              file=sys.stderr)
        _safe_inventory(dest, None, script, str(expect), args.allow,
                        "refused:script-outside-expect-root")
        return VIOLATION_EXIT

    guard = install(str(expect), args.allow)

    # Replicate what `python <script>` does and runpy.run_path does NOT: the script's
    # own directory at sys.path[0]. Silently differing from direct execution would be
    # a fresh instance of this very defect.
    sys.path.insert(0, str(script.resolve().parent))
    sys.argv = [str(script), *rest[1:]]

    outcome, violation, recorded = "ok", None, True
    try:
        runpy.run_path(str(script), run_name="__main__")
    except ImportTreeViolation as exc:
        outcome, violation = "refused:import-tree-violation", exc
        _report(exc)
        return VIOLATION_EXIT
    except SystemExit as exc:
        # The child's own status is preserved (see EXIT CODES above), so this is NOT an error path --
        # but the record must be written for it, or every entrypoint that ends in `sys.exit()` would
        # emit no inventory at all and F-4 would count them as missing.
        outcome = f"child-systemexit:{exc.code!r}"
        raise
    except BaseException as exc:                      # noqa: BLE001 - re-raised immediately
        outcome = f"child-exception:{type(exc).__name__}"
        raise
    finally:
        recorded = _safe_inventory(dest, guard, script, str(expect), args.allow,
                                   outcome, violation)
    return 0 if recorded else CANNOT_CHECK_EXIT


if __name__ == "__main__":
    sys.exit(main())
