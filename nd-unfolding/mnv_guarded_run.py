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

IT ALSO EMITS A LOADED-CHECKOUT INVENTORY, WHICH IS A RECEIPT AND NOT A GATE
---------------------------------------------------------------------------
At the end of the wrapped run this walks `sys.modules` and reports, on STDERR under
the prefix `[oi136-inv]`, every checkout root the interpreter ACTUALLY LOADED a
module from, the module names under each, and the total count. It answers the
COVERING form of the question the refusal half answers by exception: not "did an
import escape" but "which trees did this interpreter end up holding code from".

WHY IT IS NOT REDUNDANT WITH THE REFUSAL, which is the whole reason it is here.
The refusal sees only what passes through the WRAPPED `PathFinder` AFTER `install()`
returns. Everything imported before that -- this file itself, and anything a
`sitecustomize` or `PYTHONSTARTUP` pulled in -- was resolved by the unwrapped finder
and the guard is structurally blind to it. `sys.modules` is blind to none of it. So a
green refusal-half and a two-root inventory are consistent, and the second is the one
that would have named run 4's second tree without needing the import to still be
pending.

IT CANNOT REFUSE, BY CONSTRUCTION, AND THAT IS A DESIGN CONSTRAINT NOT AN ACCIDENT.
Every lane routing compute through this wrapper depends on WHEN it refuses. So the
emission runs from a `finally`, returns nothing, and swallows `BaseException` --
`BaseException` and not `Exception` because a receipt must not be able to change a
run's outcome, and a `KeyboardInterrupt` arriving inside the emission would otherwise
replace the child's own exit status with the receipt's failure. A failed emission
prints `INVENTORY EMISSION FAILED` and the run's verdict is untouched.

STDERR, NOT STDOUT, AND NOT A FILE. Consumers parse the child's stdout -- the two
Gate-5 launchers grep it -- so writing there would make this wrapper a producer on a
surface that belongs to the child, which is the same class of error the mandatory
`--` exists to prevent. Every other diagnostic in this file is already on stderr. A
file would need a path, a flag, a default and a failure mode for an unwritable
directory, and would make the receipt absent exactly where nobody passed the flag.

THE SCOPE IS ONE INTERPRETER, AND THE EMISSION SAYS SO IN ITS OWN OUTPUT. It reports
the PARENT's `sys.modules`. A child started with `subprocess.run([sys.executable,
...])` is a fresh interpreter and NOTHING it imports appears -- the same boundary the
refusal half does not cross, for the same reason. Modules imported by the child's own
`atexit` handlers land after this runs and are not counted either, and the wrapped
script is not itself a module unless something imported it by name. Read the
inventory as "at least these trees", never as "only these trees".

USAGE, AND THE `--` IS MANDATORY
--------------------------------
    mnv_guarded_run.py --expect-root <tree> [--allow <tree> ...] -- <script> [argv ...]

The `--` split and the refusal of bare positionals are copied deliberately from
`mii_adopt_unified_5d_stamped.py:431-437`, whose comment records why: a wrapper
that quietly swallows a child flag builds one product under another product's
name. Everything after `--` is forwarded to the child VERBATIM, including strings
that look like this wrapper's own options.

EXIT CODES follow `verify_executing_copy_is_committed.py` rather than inventing a
third convention:
    0 or the child's own status -- the child ran; its SystemExit is preserved
    2 -- COULD NOT LOOK (bad usage, or --expect-root is not a checkout)
    3 -- MEASURED VIOLATION: an import resolved outside the expected tree
2 is deliberately not 3, so "we could not check" can never be read as "we checked
and it was clean".
"""
from __future__ import annotations

import argparse
import os
import pathlib
import runpy
import sys

MARKERS = ("VALIDATION_LEDGER.md", "nd-unfolding")

#: Prefix for the loaded-checkout inventory. Distinct from `[oi136]` on purpose: a log
#: merged with `2>&1` must let a reader separate the RECEIPT from the GATE, because the
#: two have different authority and only one of them can fail a run.
INVENTORY_PREFIX = "[oi136-inv]"

VIOLATION_EXIT = 3
CANNOT_CHECK_EXIT = 2


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
        if root is not None and root not in self.allowed:
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


def loaded_checkout_roots(modules=None) -> "dict[str, list[str]]":
    """Every checkout root THIS interpreter has actually loaded a module from.

    `{root: [module names]}`, names sorted, built by walking `sys.modules` and handing
    each module's `__file__` to `checkout_root_of` -- THE SAME resolver and therefore the
    same marker pair the refusal half uses. There is deliberately no second marker test
    here: a receipt that answered "is this a checkout" differently from the gate could
    report a clean single root for a tree the gate would have refused, and the two
    products would then disagree without either being wrong.

    WHAT IT SKIPS, WHICH IS THE SAME SET THE DOCSTRING SAYS THE GUARD IGNORES: a module
    with no `__file__` (built-in, frozen, and namespace packages), and any file whose
    walk reaches the filesystem root without finding both markers -- the stdlib,
    site-packages and conda. Skipped because they are not the confusion this exists for,
    exactly as in `GuardedPathFinder.find_spec`.

    `sys.modules` is SNAPSHOTTED before iterating: it is mutated by any import, and an
    emission that raised `RuntimeError: dictionary changed size` would be a receipt that
    can fail a run. `getattr` is guarded per module for the same reason -- a lazy-loader
    module object may raise from `__getattr__`, and one such module must not cost the
    whole inventory.
    """
    mods = sys.modules if modules is None else modules
    by_root: dict[str, list[str]] = {}
    for name, mod in sorted(list(mods.items()), key=lambda kv: kv[0]):
        try:
            origin = getattr(mod, "__file__", None)
        except BaseException:
            origin = None
        if not origin or not isinstance(origin, str):
            continue
        root = checkout_root_of(origin)
        if root is None:
            continue
        by_root.setdefault(root, []).append(name)
    return by_root


def _emit_inventory(expect_root: str, refused: "ImportTreeViolation | None" = None,
                    stream=None) -> None:
    """Print the loaded-checkout inventory. Returns None on every path, always.

    THIS FUNCTION MAY NOT CHANGE A RUN'S OUTCOME. It is called from a `finally`, it
    returns nothing a caller can branch on, and it swallows `BaseException`. See the
    module docstring for why `BaseException` and not `Exception`.
    """
    out = sys.stderr if stream is None else stream
    try:
        by_root = loaded_checkout_roots()
        total = sum(len(v) for v in by_root.values())
        guard_root = checkout_root_of(__file__)
        say = [
            f"{INVENTORY_PREFIX} LOADED-CHECKOUT INVENTORY -- a RECEIPT, not a gate. It reports "
            f"and never refuses; the run's verdict is decided above this line.",
            f"{INVENTORY_PREFIX} modules loaded from inside a checkout: {total}"
            f"   distinct checkout roots: {len(by_root)}",
        ]
        for root in sorted(by_root):
            tags = []
            if root == expect_root:
                tags.append("expect-root")
            if root == guard_root:
                tags.append("this-guard")
            label = ",".join(tags) if tags else "NOT expect-root"
            say.append(f"{INVENTORY_PREFIX}   [{label}] {root}  "
                       f"({len(by_root[root])}) {', '.join(by_root[root])}")
        if not by_root:
            say.append(f"{INVENTORY_PREFIX} NO module resolved inside any checkout. That is a "
                       f"statement about this interpreter, not a clean bill of health: read it "
                       f"beside the scope note below before recording it as one.")
        if len(by_root) > 1:
            say.append(f"{INVENTORY_PREFIX} MORE THAN ONE CHECKOUT IS LOADED. This is reported, "
                       f"not refused -- it is legitimate when this wrapper is itself deployed "
                       f"outside --expect-root (the [this-guard] row above), and it is run 4's "
                       f"signature when it is not. Compare the roots, do not count them.")
        if refused is not None:
            say.append(f"{INVENTORY_PREFIX} THE RUN WAS REFUSED, so {refused.module} under "
                       f"{refused.found_root} was NEVER LOADED and is correctly absent above. A "
                       f"refusal's inventory is what got in BEFORE the refusal, never what would "
                       f"have.")
        say.append(f"{INVENTORY_PREFIX} SCOPE -- THIS INTERPRETER ONLY, stated here so the line "
                   f"above is not read as coverage it does not have. A child started with "
                   f"subprocess.run([sys.executable, ...]) is a fresh interpreter and NOTHING it "
                   f"imports is counted, the same boundary the refusal half does not cross. Nor "
                   f"is anything imported after this point, including by the child's own atexit "
                   f"handlers. Read it as 'AT LEAST these trees', never as 'only these trees'.")
        print("\n".join(say), file=out)
    except BaseException as err:  # a receipt must not be able to fail a run
        try:
            print(f"{INVENTORY_PREFIX} INVENTORY EMISSION FAILED: {err!r}\n"
                  f"{INVENTORY_PREFIX} This is a RECEIPT failure and NOT a gate failure. The exit "
                  f"status of this run is whatever the guard and the child decided, unchanged. "
                  f"What is lost is the evidence, so do not record this run as inventoried.",
                  file=out)
        except BaseException:
            pass


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
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)

    rest = list(args.rest)
    if not rest or rest[0] != "--":
        print("[oi136] usage: --expect-root <tree> [--allow <tree>] -- <script> [argv ...]\n"
              "[oi136] the `--` is MANDATORY and bare positionals are refused, so a child flag\n"
              "[oi136] can never be silently eaten by this wrapper (see remedy (A)'s wrapper).",
              file=sys.stderr)
        return CANNOT_CHECK_EXIT
    rest = rest[1:]
    if not rest:
        print("[oi136] nothing to run after `--`", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    expect = pathlib.Path(args.expect_root).resolve()
    if not is_checkout(expect):
        print(f"[oi136] COULD NOT LOOK: --expect-root {expect} is not a checkout "
              f"(needs {' and '.join(MARKERS)}). Exit 2 and not 3 on purpose: this is "
              f"'we could not check', never 'we checked and it was clean'.", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    script = pathlib.Path(rest[0])
    if not script.is_file():
        print(f"[oi136] COULD NOT LOOK: no such script {script}", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    guard = install(str(expect), args.allow)

    # Replicate what `python <script>` does and runpy.run_path does NOT: the script's
    # own directory at sys.path[0]. Silently differing from direct execution would be
    # a fresh instance of this very defect.
    sys.path.insert(0, str(script.resolve().parent))
    sys.argv = [str(script), *rest[1:]]

    # ADDITIVE ONLY. The `finally` exists so the inventory survives the child's own
    # SystemExit -- which is the NORMAL exit path for most entrypoints, so an emission
    # placed after `run_path` would be absent from almost every real run. It cannot
    # change the outcome: `_emit_inventory` returns None on every path and swallows
    # BaseException, and neither the refusal nor its exit code moved to accommodate it.
    refused: list[ImportTreeViolation] = []
    try:
        runpy.run_path(str(script), run_name="__main__")
    except ImportTreeViolation as exc:
        refused.append(exc)
        _report(exc)
        return VIOLATION_EXIT
    finally:
        _emit_inventory(str(expect), refused[0] if refused else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
