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
imports a different file entirely. The run that established this, the rules tried
and rejected, and the order the two receipts were built in are recorded in
`docs/orchestration/FINDING-20260828-oi136-guard-provenance.md`.

The 59 are hash-pinned science files inside frozen provenance, so this wrapper
converts the fail-OPEN direction into the fail-CLOSED one rather than editing them.

IT DOES NOT REPLACE THE PARITY CHECK AND IT IS NOT REDUNDANT WITH IT.
`verify_executing_copy_is_committed.py` answers "are the FILES AT THESE PATHS the
committed ones". This answers "are the MODULES THE INTERPRETER ACTUALLY LOADED
from the tree we think we are running". Those are two different questions: the
first can pass honestly while the second is false. Adding another `--pair` would
not catch it, and neither would a re-deploy.

WHAT IT REFUSES, AND WHAT IT DELIBERATELY IGNORES
-------------------------------------------------
A module is refused when its resolved origin lies inside a MINERvA-OmniFold
CHECKOUT (a directory holding both `VALIDATION_LEDGER.md` and `nd-unfolding/`)
whose root is neither `--expect-root` nor an explicit `--allow`. The stdlib,
site-packages, conda and any path outside a checkout are IGNORED, because they are
not the confusion this exists for and flagging them would make the guard something
people switch off. The marker pair must hold across checkout GENERATIONS: both
files predate every frozen tree on scratch, and a marker introduced later would
fail to recognise an older frozen tree and wave it through.

It also refuses a script that is not itself in the expected tree. That check runs
BEFORE `install()`, so the refusal precedes the first import as well as the work.
`--allow` does not cover it: `--allow` declares an IMPORT tree, never an execution
tree.

IT CROSSES PROCESS BOUNDARIES AND FAILS CLOSED AT PYTHON LAUNCHES. `install()`
prepends the tracked `mnv_guard_shim/` directory to `PYTHONPATH`, records the
absolute guard module, expected root, allow-list and inventory path in
`MNV_GUARD_*`, and wraps the process-launch primitives owned by the interpreter.
At child-interpreter startup, `sitecustomize.py` verifies that the recorded guard
module is inside the expected checkout, loads it, and calls
`install(expect_root, allow)` before the child script runs. The installed
meta-path finder checks the RESOLVED ORIGIN, so a later
`sys.path.insert(0, ...)` in the child does not outrank it.

Every covered child in an inventoried run appends its OWN record with
`propagated_from` naming the parent pid and `depth` incremented once per Python
boundary. This is the live shape of `mii_adopt_unified_5d_stamped.py`, which launches
the receipt-bound, fail-open `adopt_unified_5d.py` as a subprocess and cannot edit
that child in place.

Direct Python launches using `-S`, `-I` or `-E`, standalone or combined with other
short flags, are refused at the launch site because each option prevents reliable
shim startup. In particular, `-I` implies isolated mode and ignores the shim; a
legitimate need for `-I` requires a launcher-design change, not a guard exception.
The scan follows CPython's OWN option grammar rather than approximating it, so an
option's VALUE is never read as a flag (`-Xpycache_prefix=/tmp/CACHE` is not an
`-E`) and a flag after a value is never missed (`-W ignore -I` is refused).

An explicitly supplied environment, including `env={}`, is copied and re-armed
with the propagation contract and shim-first `PYTHONPATH`. Where the contract
cannot be re-armed it is REFUSED instead of launched: a Python child whose ARGV
strips it -- `env -i`, `env -u MNV_GUARD_MODULE`, `env PYTHONPATH=...` -- and a
Python child of a process that deleted a `MNV_GUARD_*` variable or overwrote
`PYTHONPATH` in its own `os.environ` after `install()`. So a Python child of a
guarded interpreter either starts guarded or does not start. Non-Python children
are never refused: they inherit the re-armed contract, which is what makes an
ordinary Python interpreter they launch guarded.

THE ONE DECLARED PROCESS-BOUNDARY GAP is a non-Python child that itself launches
`python -I`. The guarded interpreter owns only the first launch site, while the
second launch occurs inside the non-Python process and isolated mode ignores the
inherited shim. The same one gap covers every other way that second launch can
defeat the contract -- clearing the environment, or unsetting `PYTHONPATH` --
because they share the single cause: the launching process is one this
interpreter does not guard. The measured gap and all covered counterparts are
pinned in `tests/test_mnv_guarded_run.py::TheSubprocessBoundaryIsCovered`.

TWO RECEIPTS, NEITHER OF WHICH IS A GATE
----------------------------------------
At the end of the wrapped run this walks `sys.modules` and reports, on STDERR under
the prefix `[oi136-inv]`, every checkout root the interpreter ACTUALLY LOADED a
module from, the module names under each, and the total count. It answers the
COVERING form of the question the refusal half answers by exception: not "did an
import escape" but "which trees did this interpreter end up holding code from".
The refusal sees only what passes through the WRAPPED `PathFinder` AFTER `install()`
returns; everything imported before that was resolved by the unwrapped finder and the
guard is structurally blind to it. `sys.modules` is blind to none of it, so a green
refusal half and a two-root inventory are consistent.

`--inventory <path>` (or `$MNV_GUARD_INVENTORY`) appends ONE json object per process
recording the interpreter, both roots, the script and its checkout root, `checked`,
the final `sys.path`, the executed shim's `shim_sha256`, and EVERY module whose
resolved origin lies inside any checkout -- the allowed ones as well as the refused
one. `repo_origin_count` and
`repo_origin_inventory_is_empty` are written UNCONDITIONALLY: a zero is a REPORTABLE
STATE and never a pass, and an absent key cannot tell "no repository import occurred"
from "the inventory did not run". The CLI parent emits both receipts from one
`finally`; a propagated child emits them from its shutdown hook, or immediately
before an import refusal terminates it. They answer different questions.

IT CANNOT REFUSE, BY CONSTRUCTION, AND THAT IS A DESIGN CONSTRAINT NOT AN ACCIDENT.
Every lane routing compute through this wrapper depends on WHEN it refuses. The text
emission returns nothing and swallows `BaseException` -- `BaseException` and not
`Exception` because a receipt must not be able to change a run's outcome. A failed
emission prints `INVENTORY EMISSION FAILED` and the run's verdict is untouched. The
CLI invokes it from a `finally`; the shim invokes it from the child-finalization paths
described above.

STDERR, NOT STDOUT. Consumers parse the child's stdout -- the two Gate-5 launchers
grep it -- so writing there would make this wrapper a producer on a surface that
belongs to the child, which is the same class of error the mandatory `--` exists to
prevent. Every other diagnostic in this file is already on stderr.

EACH INVENTORY RECORD COVERS ONE INTERPRETER, AND THE EMISSION SAYS SO IN ITS OWN
OUTPUT. It reports only that process's `sys.modules`; a covered child writes a
separate record rather than appearing in its parent's record. The wrapped script is
not itself a module unless something imported it by name. Read each record as "at
least these trees", never as "only these trees".

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
    3 -- MEASURED VIOLATION: an import resolved outside the expected tree, the script itself
         lies in a checkout that is not --expect-root, or a Python child would have started
         without the guard -- a startup flag that prevents shim installation, or an argv or
         environment that strips the propagation contract
2 is deliberately not 3, so "we could not check" can never be read as "we checked
and it was clean".
"""
from __future__ import annotations

import argparse
import datetime
import functools
import hashlib
import inspect
import json
import os
import pathlib
import re
import runpy
import shutil
import subprocess
import sys

MARKERS = ("VALIDATION_LEDGER.md", "nd-unfolding")

#: Prefix for the loaded-checkout inventory. Distinct from `[oi136]` on purpose: a log
#: merged with `2>&1` must let a reader separate the RECEIPT from the GATE, because the
#: two have different authority and only one of them can fail a run.
INVENTORY_PREFIX = "[oi136-inv]"

VIOLATION_EXIT = 3
CANNOT_CHECK_EXIT = 2

#: Environment fallback for `--inventory`. A flag OR an env var, because the launcher that needs the
#: record and the wrapper invocation that emits it are edited by different hands.
INVENTORY_ENV = "MNV_GUARD_INVENTORY"

#: Propagation contract consumed by `mnv_guard_shim/sitecustomize.py`. The module path is absolute
#: because resolving this module through the child's import path would recreate the ambiguity the
#: guard exists to refuse.
MODULE_ENV = "MNV_GUARD_MODULE"
EXPECT_ROOT_ENV = "MNV_GUARD_EXPECT_ROOT"
ALLOW_ENV = "MNV_GUARD_ALLOW"
PARENT_PID_ENV = "MNV_GUARD_PARENT_PID"
DEPTH_ENV = "MNV_GUARD_DEPTH"
SHIM_DIR = pathlib.Path(__file__).resolve().parent / "mnv_guard_shim"
CHILD_PREFIX = "[oi136 child]"
LAUNCH_PREFIX = "[oi136 launch]"

PROPAGATION_ENV_VARS = (
    MODULE_ENV,
    EXPECT_ROOT_ENV,
    ALLOW_ENV,
    INVENTORY_ENV,
    PARENT_PID_ENV,
    DEPTH_ENV,
)

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
VERDICT_REFUSED_LAUNCH = "REFUSED launch"

#: FOUND BY RUNNING IT, 2026-08-22, on the real N-1 arm against the canonical checkout. A B-4
#: script-containment refusal raises no `ImportTreeViolation`, so the verdict fell through to
#: VERDICT_EMPTY and the record of a REFUSAL read "THE GUARD REFUSED NOTHING BECAUSE IT SAW
#: NOTHING". Both clauses were false and the sentence was the exact inversion of what happened --
#: precisely the confusion P-3 exists to prevent, reintroduced by the field meant to prevent it.
#: The verdict is now derived from the OUTCOME as well as from the exception.
VERDICT_REFUSED_SCRIPT = ("REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT "
                          "--expect-root; nothing was imported because nothing was run")

#: WHICH PROTECTION FIRED, as a field rather than as a string a reader has to parse out of
#: `outcome`. Every refusal in this file returns the same VIOLATION_EXIT, so AN EXIT CODE OF 3 NEVER
#: SAYS WHICH CHECK REFUSED -- and that is not a cosmetic gap: it is exactly how B-4 silently
#: invalidated F-9's import-specific expectation the day B-4 landed, because both arms were "exit
#: 3" and nothing in the artifact distinguished them. Any check added AHEAD of an existing one
#: changes which site fires first, so every downstream control has to be re-derived; naming the site
#: is what makes that re-derivation mechanical instead of a memory exercise.
SITE_NONE = None
SITE_SCRIPT_CONTAINMENT = "b4-script-containment"
SITE_IMPORT_RESOLUTION = "import-tree-violation"
SITE_LAUNCH = "launch-python-startup-flags"

#: `checked` provenance. A ZERO IS NOT SELF-EXPLANATORY and F-9 now makes zero the EXPECTED value on
#: the containment path, which is precisely when a defaulted zero would pass unnoticed. Two states
#: produce it and they are completely different evidence:
#:   * the guard installed and resolved no absolute origin  -> MEASURED zero
#:   * the guard was never installed, because the run was refused first -> NOT MEASURED at all
#: `guard_installed` already carried half of this; the reader had to infer the rest.
CHECKED_MEASURED = "measured-by-installed-guard"
CHECKED_NOT_MEASURED = "not-measured-no-guard-was-installed"


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

    def __init__(self, inner, expect_root: str, allowed: frozenset[str],
                 propagated_from: int | None, depth: int):
        self._inner = inner
        self.expect_root = expect_root
        self.allowed = allowed
        self.propagated_from = propagated_from
        self.depth = depth
        self.propagation = "not-armed"
        self.chained_sitecustomize = {
            "found": False,
            "executed": False,
            "origin": None,
        }
        self.violation: ImportTreeViolation | None = None
        self.launch_refusal: dict | None = None
        self.launch_env = "not-re-armed"
        self.shim_sha256 = _sha256_or_none(str(SHIM_DIR / "sitecustomize.py"))
        self.on_violation = None
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
            violation = ImportTreeViolation(fullname, origin, root, self.expect_root)
            if self.propagated_from is not None:
                self.violation = violation
                _report(violation, prefix=CHILD_PREFIX)
                if self.on_violation is not None:
                    self.on_violation()
                sys.stdout.flush()
                sys.stderr.flush()
                os._exit(VIOLATION_EXIT)
            raise violation
        return spec

    def invalidate_caches(self):
        inv = getattr(self._inner, "invalidate_caches", None)
        if inv is not None:
            inv()


def _lineage_from_environment() -> tuple[int | None, int]:
    """Return the current process's inherited guard parent and depth."""
    parent_text = os.environ.get(PARENT_PID_ENV)
    depth_text = os.environ.get(DEPTH_ENV)
    if parent_text is None and depth_text is None:
        return None, 0
    try:
        parent_pid = int(parent_text) if parent_text is not None else None
        depth = int(depth_text) if depth_text is not None else 0
    except ValueError as exc:
        raise RuntimeError("invalid inherited OI-136 guard lineage") from exc
    if parent_pid is None or parent_pid <= 0 or depth <= 0:
        raise RuntimeError("incomplete inherited OI-136 guard lineage")
    return parent_pid, depth


def _arm_child_environment(expect_root: str, allow: tuple[str, ...]) -> None:
    """Arm inheriting Python children through the tracked sitecustomize shim."""
    shim = SHIM_DIR.resolve()
    shim_file = shim / "sitecustomize.py"
    module = pathlib.Path(__file__).resolve()
    if not shim_file.is_file():
        raise RuntimeError(f"OI-136 subprocess shim is missing: {shim_file}")
    if not module.is_file():
        raise RuntimeError(f"OI-136 guard module is missing: {module}")

    existing_pythonpath = os.environ.get("PYTHONPATH")
    shim_text = str(shim)
    if existing_pythonpath is None:
        os.environ["PYTHONPATH"] = shim_text
    elif existing_pythonpath != shim_text and not existing_pythonpath.startswith(
            shim_text + os.pathsep):
        os.environ["PYTHONPATH"] = shim_text + os.pathsep + existing_pythonpath

    _, current_depth = _lineage_from_environment()
    os.environ[MODULE_ENV] = str(module)
    os.environ[EXPECT_ROOT_ENV] = expect_root
    os.environ[ALLOW_ENV] = os.pathsep.join(allow)
    os.environ.setdefault(INVENTORY_ENV, "")
    os.environ[PARENT_PID_ENV] = str(os.getpid())
    os.environ[DEPTH_ENV] = str(current_depth + 1)


def _text_argument(value) -> str:
    """Return a JSON-safe representation of a process argument."""
    raw = os.fspath(value)
    if isinstance(raw, bytes):
        return os.fsdecode(raw)
    return str(raw)


def _launch_argv(arguments) -> list[str]:
    """Normalize a process argument vector without changing what is launched."""
    if isinstance(arguments, (str, bytes, os.PathLike)):
        return [_text_argument(arguments)]
    return [_text_argument(argument) for argument in arguments]


def _resolve_executable(executable, env=None) -> str:
    """Resolve a launch executable using the environment that launch will receive."""
    text = _text_argument(executable)
    path_value = None if env is None else env.get("PATH")
    if isinstance(path_value, bytes):
        path_value = os.fsdecode(path_value)
    found = shutil.which(text, path=path_value)
    candidate = found or text
    try:
        return str(pathlib.Path(candidate).resolve())
    except OSError:
        return candidate


def _is_python_executable(executable: str) -> bool:
    """Return whether an executable is the current or a Python interpreter."""
    try:
        if pathlib.Path(executable).resolve() == pathlib.Path(sys.executable).resolve():
            return True
    except OSError:
        pass
    basename = pathlib.Path(executable).name
    if basename.lower().endswith(".exe"):
        basename = basename[:-4]
    return re.fullmatch(r"python[0-9.]*", basename, flags=re.IGNORECASE) is not None


#: The three startup options that prevent reliable shim installation, as CPython spells them in a
#: short-option CLUSTER: `-IS`, `-Es` and `-OI` are the same request as `-I`, `-E` and `-I`.
FORBIDDEN_STARTUP_FLAG_CHARS = "SIE"

#: CPython short options that CONSUME A VALUE, and the two of those that also END option parsing.
#: The distinction is not pedantry: a scan that walks a value's characters is wrong in BOTH
#: directions, and the naive "stop at the first non-flag token" scan this replaced was measured
#: wrong in both. `-Xpycache_prefix=/tmp/CACHE` read as an `-E` and REFUSED A CORRECT LAUNCH, which
#: is how a guard gets switched off; and `-W ignore -I child.py` -- the option's value in the NEXT
#: token -- ended the scan at `ignore` and LAUNCHED THE ISOLATED CHILD, which is the reviewer's
#: finding with a different spelling. After `-c` or `-m` every later token belongs to the child
#: program, so a `-I` there is the child's own argument and refusing it would be the first error
#: again. Both directions are pinned in `TheStartupFlagScanFollowsCPythonsOptionGrammar`.
_VALUE_TAKING_SHORT_FLAGS = "cmWX"
_PROGRAM_ENDING_SHORT_FLAGS = "cm"

#: The one long option that takes a separate value. Its value cannot be a startup flag, so the
#: token after it is skipped rather than read.
_VALUE_TAKING_LONG_FLAGS = ("--check-hash-based-pycs",)

#: NOT CPython spellings -- `python --isolated` exits with "unknown option". Refused anyway: a
#: launcher that grew them is asking for isolation, and refusing a launch CPython would reject
#: costs nothing.
_FORBIDDEN_LONG_FLAGS = ("--isolated", "--ignore-environment", "--no-site")


def _forbidden_python_flag(argv: list[str]) -> str | None:
    """Return the first startup flag that prevents reliable shim installation.

    The walk follows CPython's own option grammar rather than approximating it, for the reason
    recorded on `_VALUE_TAKING_SHORT_FLAGS`: the approximation was measured to fail open on
    `-W ignore -I` and to refuse the correct `-Xpycache_prefix=/tmp/CACHE`.
    """
    index = 1
    while index < len(argv):
        argument = argv[index]
        index += 1
        if argument in ("-", "--") or not argument.startswith("-"):
            return None                      # the script, `-` for stdin, or the end of the options
        if argument.startswith("--"):
            if argument in _FORBIDDEN_LONG_FLAGS:
                return argument
            if argument in _VALUE_TAKING_LONG_FLAGS:
                index += 1
            continue
        cluster = argument[1:]
        for position, character in enumerate(cluster):
            if character in FORBIDDEN_STARTUP_FLAG_CHARS:
                return argument
            if character in _PROGRAM_ENDING_SHORT_FLAGS:
                return None                  # -c/-m: every later token is the child's own argv
            if character in _VALUE_TAKING_SHORT_FLAGS:
                if position == len(cluster) - 1:
                    index += 1               # the value is the NEXT token, and is not a flag
                break                        # the rest of THIS token is the value
    return None


def _pythonpath_starts_with_shim(pythonpath) -> bool:
    """Return whether PYTHONPATH's first entry resolves to the tracked shim."""
    if not isinstance(pythonpath, (str, bytes)):
        return False
    text = os.fsdecode(pythonpath) if isinstance(pythonpath, bytes) else pythonpath
    if not text:
        return False
    try:
        first = pathlib.Path(text.split(os.pathsep, 1)[0]).resolve()
        return first == SHIM_DIR.resolve()
    except OSError:
        return False


def _breaks_propagation_contract(name: str, value: "str | None") -> bool:
    """Return whether setting `name` to `value` (None for unset) disarms an inheriting child.

    The two halves are not interchangeable. A `MNV_GUARD_*` variable must arrive with THIS
    process's value, because the child reads the guard module path and the expected root out of it.
    `PYTHONPATH` must arrive with the shim FIRST, because a later entry does not get imported as
    `sitecustomize`.
    """
    if name in PROPAGATION_ENV_VARS:
        return value != os.environ.get(name)
    if name == "PYTHONPATH":
        return not _pythonpath_starts_with_shim(value)
    return False


def _environment_reaching_child_is_armed(env) -> "str | None":
    """Return the contract variable a Python child would start WITHOUT, or None when armed.

    THE LAST FAIL-OPEN ROUTE AT A LAUNCH SITE, and it is not the `env=` keyword: it is this
    process's OWN `os.environ`. `install()` exports the contract, but a script that deletes a
    `MNV_GUARD_*` variable, or overwrites `PYTHONPATH`, disarms every later launch -- the inherited
    environment is then missing the contract and there is nothing in the call to re-arm FROM. A
    Python child in that state starts unguarded and writes no record, which is the reviewer's
    finding reached by deleting a variable instead of by passing one. So it is REFUSED, and a
    correct run cannot reach it: `install()` sets all four, and an explicit `env=` is re-armed
    before this check reads it.

    `MNV_GUARD_ALLOW` and `MNV_GUARD_INVENTORY` are deliberately NOT required to be non-empty --
    both are legitimately empty (no `--allow`, no `--inventory`) and requiring them would refuse
    correct launches.
    """
    source = os.environ if env is None else env
    for name in (MODULE_ENV, EXPECT_ROOT_ENV, PARENT_PID_ENV, DEPTH_ENV):
        if not source.get(name):
            return name
    if not _pythonpath_starts_with_shim(source.get("PYTHONPATH")):
        return "PYTHONPATH"
    return None


def _rearm_launch_environment(env, guard: GuardedPathFinder):
    """Copy and repair an explicitly supplied child environment when necessary."""
    if env is None:
        return None
    needs_rearm = any(env.get(name) != os.environ.get(name)
                      for name in PROPAGATION_ENV_VARS)
    needs_rearm = needs_rearm or not _pythonpath_starts_with_shim(env.get("PYTHONPATH"))
    if not needs_rearm:
        return env

    armed = dict(env)
    for name in PROPAGATION_ENV_VARS:
        # ABSENT IS COPIED AS ABSENT, never invented: `os.environ` is the only place this process
        # holds the contract, so a variable missing there cannot be re-derived here. That state is
        # caught by `_environment_reaching_child_is_armed`, which refuses the launch rather than
        # letting an empty value read as an armed one.
        armed[name] = os.environ.get(name, "")
    existing_pythonpath = env.get("PYTHONPATH")
    if isinstance(existing_pythonpath, bytes):
        existing_pythonpath = os.fsdecode(existing_pythonpath)
    shim_text = str(SHIM_DIR.resolve())
    entries = [] if not existing_pythonpath else str(existing_pythonpath).split(os.pathsep)
    retained = []
    for entry in entries:
        try:
            is_shim = pathlib.Path(entry or os.curdir).resolve() == SHIM_DIR.resolve()
        except OSError:
            is_shim = False
        if not is_shim:
            retained.append(entry)
    armed["PYTHONPATH"] = os.pathsep.join([shim_text, *retained])
    guard.launch_env = "re-armed"
    return armed


#: `env` is the ARGV spelling of two things this guard already refuses in their keyword spelling:
#: "the real executable is a later word" and, for `env -i`, THE CLEARED ENVIRONMENT the reviewer's
#: finding names. Neither existing check sees it -- the flag scan resolves a non-Python executable,
#: and `_rearm_launch_environment` is handed `env=None` because the stripping happens in the
#: launched process rather than in the caller -- so an unhandled `env -i python3 child.py` from a
#: guarded interpreter reproduces the finding verbatim. No tracked launcher uses `env` today
#: (measured over `*.py` and `*.sh`), so handling it costs only the parser below.
_ENV_BASENAMES = frozenset({"env"})

#: `env`'s OWN option grammar, split by whether an option consumes a value. An option this table
#: does not list leaves the launch UNPARSED and therefore unscanned, which is deliberate: GNU
#: coreutils and the BSD `env` macOS ships do not agree on the option set, and a parser that
#: guessed would either read an option's value as a startup flag or refuse a correct
#: `env -u LD_PRELOAD ./binary`. An unparsed prefix stays in the declared gap; a MIS-parsed one
#: would be a wrong answer.
_ENV_FLAG_OPTIONS = frozenset({"-i", "--ignore-environment", "-0", "--null", "-v", "--debug"})
_ENV_VALUE_OPTIONS = frozenset({"-u", "--unset", "-C", "--chdir", "-S", "--split-string",
                                "-P", "-a"})
_ENV_CLEARING_OPTIONS = frozenset({"-", "-i", "--ignore-environment"})
_ENV_UNSET_PREFIXES = ("-u", "--unset=")
_ENV_OTHER_ATTACHED_PREFIXES = ("--chdir=", "--split-string=", "-C", "-P", "-S", "-a")

#: WHY the launch was refused, as a field. Both refusals are the same SITE (this wrapper owns one
#: launch boundary) and the same exit code, and the repo's own rule -- see the `SITE_*` block --
#: is that a reader must not have to parse which check fired out of prose.
LAUNCH_REASON_FLAGS = "python-startup-flags-bypass-the-shim"
LAUNCH_REASON_ENV = "the-launch-argv-or-environment-strips-the-propagation-contract"

_LAUNCH_HEADLINES = {
    LAUNCH_REASON_FLAGS: "PYTHON STARTUP FLAGS BYPASS THE IMPORT SHIM",
    LAUNCH_REASON_ENV: "THE CHILD WOULD START WITHOUT THE PROPAGATION CONTRACT",
}

_LAUNCH_EXPLANATIONS = {
    LAUNCH_REASON_FLAGS: ("-S, -I and -E prevent reliable sitecustomize propagation. -I must be "
                          "handled by a launcher-design change, not a guard exception."),
    LAUNCH_REASON_ENV: ("The interpreter would start with no MNV_GUARD_* contract or no shim-first "
                        "PYTHONPATH, so it could not install the guard. An environment passed as "
                        "`env=` IS re-armed; one stripped in argv or deleted from this process's "
                        "own os.environ cannot be, so the launch is refused instead."),
}


def _is_env_executable(executable: str) -> bool:
    """Return whether an executable is the `env` command rather than the program it runs."""
    return pathlib.Path(executable).name in _ENV_BASENAMES


def _env_command_argv(argv: list[str]) -> "tuple[list[str], str | None] | None":
    """Split an `env ...` launch into the command it runs and the token that disarms the child.

    Returns `(command argv, disarming token or None)`, or None when the prefix cannot be parsed or
    launches nothing at all -- see `_ENV_VALUE_OPTIONS` for why an unparsed prefix is left alone.
    """
    index = 1
    stripped = None
    while index < len(argv):
        token = argv[index]
        if token in _ENV_CLEARING_OPTIONS:
            stripped = stripped or token
            index += 1
            continue
        if token in _ENV_FLAG_OPTIONS:
            index += 1
            continue
        if token in _ENV_VALUE_OPTIONS:
            if index + 1 >= len(argv):
                return None                  # a value-taking option with no value: not parseable
            if (token in ("-u", "--unset")
                    and _breaks_propagation_contract(argv[index + 1], None)):
                stripped = stripped or f"{token} {argv[index + 1]}"
            index += 2
            continue
        attached = next((p for p in _ENV_UNSET_PREFIXES
                         if token.startswith(p) and len(token) > len(p)), None)
        if attached is not None:
            if _breaks_propagation_contract(token[len(attached):], None):
                stripped = stripped or token
            index += 1
            continue
        if any(token.startswith(p) and len(token) > len(p)
               for p in _ENV_OTHER_ATTACHED_PREFIXES):
            index += 1
            continue
        if token.startswith("-"):
            return None                      # an option this parser does not model: do not guess
        name, separator, value = token.partition("=")
        if separator:
            if _breaks_propagation_contract(name, value):
                stripped = stripped or token
            index += 1
            continue
        return argv[index:], stripped
    return None                              # `env` with no command word launches nothing


def _report_launch(refusal: dict) -> None:
    """Print a fail-closed Python-launch refusal."""
    reason = refusal.get("reason", LAUNCH_REASON_FLAGS)
    print(
        f"\n{LAUNCH_PREFIX} {_LAUNCH_HEADLINES[reason]} -- REFUSING BEFORE LAUNCH.\n"
        f"{LAUNCH_PREFIX}   executable     {refusal['executable']}\n"
        f"{LAUNCH_PREFIX}   offending flag {refusal['offending_flag']}\n"
        f"{LAUNCH_PREFIX}   argv           {refusal['argv']!r}\n"
        f"{LAUNCH_PREFIX} {_LAUNCH_EXPLANATIONS[reason]}\n",
        file=sys.stderr,
        flush=True,
    )


def _prepare_launch(executable, arguments, env, guard: GuardedPathFinder):
    """Re-arm a launch environment, or refuse a Python child that could not install the guard.

    THE THREE REFUSALS AND THE ONE REPAIR ARE ORDERED, and the order is the cheapest correct one:
    the environment is re-armed FIRST so that the armed copy is what every later check reads, then
    the executable is resolved THROUGH that environment, and only a resolved PYTHON child is
    scanned. A non-Python child is never refused here -- it inherits the re-armed contract, which
    is what makes an ordinary interpreter it launches guarded, and the isolated one it may launch
    instead is the module docstring's single declared gap.
    """
    armed_env = _rearm_launch_environment(env, guard)
    argv = _launch_argv(arguments)
    resolved = _resolve_executable(executable, armed_env)
    scan_argv, stripped = argv, None
    if _is_env_executable(resolved):
        split = _env_command_argv(argv)
        if split is not None:
            scan_argv, stripped = split
            resolved = _resolve_executable(scan_argv[0], armed_env)
    if not _is_python_executable(resolved):
        return armed_env
    if stripped is not None:
        reason, offending = LAUNCH_REASON_ENV, stripped
    else:
        offending, reason = _forbidden_python_flag(scan_argv), LAUNCH_REASON_FLAGS
        if offending is None:
            offending = _environment_reaching_child_is_armed(armed_env)
            reason = LAUNCH_REASON_ENV
    if offending is None:
        return armed_env
    refusal = {
        "executable": resolved,
        "offending_flag": offending,
        "argv": argv,
        "reason": reason,
    }
    guard.launch_refusal = refusal
    _report_launch(refusal)
    raise SystemExit(VIOLATION_EXIT)


def _install_launch_guards(guard: GuardedPathFinder) -> None:
    """Wrap process-launch primitives for this guarded interpreter."""
    original_popen_init = subprocess.Popen.__init__
    popen_signature = inspect.signature(original_popen_init)

    @functools.wraps(original_popen_init)
    def guarded_popen_init(*call_args, **call_kwargs):
        bound = popen_signature.bind(*call_args, **call_kwargs)
        command = bound.arguments["args"]
        env = bound.arguments.get("env")
        shell = bound.arguments.get("shell", False)
        executable = bound.arguments.get("executable")
        if shell:
            executable = executable or os.environ.get("COMSPEC") or "/bin/sh"
            argv = [executable, "-c", *_launch_argv(command)]
        else:
            argv = _launch_argv(command)
            executable = executable or argv[0]
        armed_env = _prepare_launch(executable, argv, env, guard)
        if env is not None:
            bound.arguments["env"] = armed_env
        return original_popen_init(*bound.args, **bound.kwargs)

    subprocess.Popen.__init__ = guarded_popen_init

    def wrap_vector_launch(
        name: str,
        *,
        executable_index: int,
        executable_parameter: str,
        argv_index: int,
        argv_parameter: str,
        env_index: int | None = None,
        env_parameter: str | None = None,
    ) -> None:
        original = getattr(os, name, None)
        if original is None:
            return

        @functools.wraps(original)
        def guarded(*call_args, **call_kwargs):
            positional = list(call_args)
            executable = (positional[executable_index]
                          if len(positional) > executable_index
                          else call_kwargs[executable_parameter])
            argv = (positional[argv_index]
                    if len(positional) > argv_index
                    else call_kwargs[argv_parameter])
            if env_parameter is None:
                env = None
            elif env_index is not None and len(positional) > env_index:
                env = positional[env_index]
            else:
                env = call_kwargs[env_parameter]
            armed_env = _prepare_launch(
                executable,
                argv,
                env,
                guard,
            )
            if env_parameter is not None:
                if env_index is not None and len(positional) > env_index:
                    positional[env_index] = armed_env
                else:
                    call_kwargs[env_parameter] = armed_env
            return original(*positional, **call_kwargs)

        setattr(os, name, guarded)

    wrap_vector_launch("execv", executable_index=0, executable_parameter="path",
                       argv_index=1, argv_parameter="argv")
    wrap_vector_launch("execve", executable_index=0, executable_parameter="path",
                       argv_index=1, argv_parameter="argv", env_index=2,
                       env_parameter="env")
    wrap_vector_launch("execvp", executable_index=0, executable_parameter="file",
                       argv_index=1, argv_parameter="args")
    wrap_vector_launch("execvpe", executable_index=0, executable_parameter="file",
                       argv_index=1, argv_parameter="args", env_index=2,
                       env_parameter="env")
    for name in ("posix_spawn", "posix_spawnp"):
        wrap_vector_launch(name, executable_index=0, executable_parameter="path",
                           argv_index=1, argv_parameter="argv", env_index=2,
                           env_parameter="env")
    for name in ("spawnv", "spawnvp"):
        wrap_vector_launch(name, executable_index=1, executable_parameter="file",
                           argv_index=2, argv_parameter="args")
    for name in ("spawnve", "spawnvpe"):
        wrap_vector_launch(name, executable_index=1, executable_parameter="file",
                           argv_index=2, argv_parameter="args", env_index=3,
                           env_parameter="env")

    def wrap_spawnl(name: str, *, has_env: bool) -> None:
        original = getattr(os, name, None)
        if original is None:
            return
        signature = inspect.signature(original)

        @functools.wraps(original)
        def guarded(*call_args, **call_kwargs):
            bound = signature.bind(*call_args, **call_kwargs)
            executable = bound.arguments["file"]
            arguments = bound.arguments["args"]
            env = arguments[-1] if has_env else None
            argv = arguments[:-1] if has_env else arguments
            armed_env = _prepare_launch(executable, argv, env, guard)
            if has_env:
                bound.arguments["args"] = (*argv, armed_env)
            return original(*bound.args, **bound.kwargs)

        setattr(os, name, guarded)

    for name in ("spawnl", "spawnlp"):
        wrap_spawnl(name, has_env=False)
    for name in ("spawnle", "spawnlpe"):
        wrap_spawnl(name, has_env=True)

    original_system = os.system

    @functools.wraps(original_system)
    def guarded_system(command):
        shell = os.environ.get("COMSPEC") or "/bin/sh"
        _prepare_launch(shell, [shell, "-c", command], None, guard)
        return original_system(command)

    os.system = guarded_system


def install(expect_root: str, allow=()) -> GuardedPathFinder:
    """Wrap import resolution and every owned process-launch boundary."""
    expect = str(pathlib.Path(expect_root).resolve())
    allow_roots = tuple(str(pathlib.Path(path).resolve()) for path in allow)
    allowed = frozenset({expect, *allow_roots})
    propagated_from, depth = _lineage_from_environment()
    for i, finder in enumerate(sys.meta_path):
        if getattr(finder, "__name__", None) == "PathFinder" or type(finder).__name__ == "PathFinder":
            guard = GuardedPathFinder(finder, expect, allowed, propagated_from, depth)
            sys.meta_path[i] = guard
            _arm_child_environment(expect, allow_roots)
            _install_launch_guards(guard)
            guard.propagation = "armed"
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


def _repo_env_capture(expect_root: str) -> "list[str]":
    """`MNV_REPO` and whether it was SET or DERIVED. OI-136's other half.

    THE GAP THIS CLOSES. The inventory above answers "which trees did the interpreter
    load from". It does NOT answer "how was that tree CHOSEN", and those are different
    questions with the same answer surface: two runs with identical inventories can have
    arrived there by different routes, and only one route is stable under redeployment.
    35 files in this tree read `MNV_REPO` with the idiom
    `os.environ.get("MNV_REPO") or os.path.dirname(...)` and insert the result at
    `sys.path[0]` -- see `nd-unfolding/pet/pointcloud_projection.py:29` and `:298`. So the
    same line resolves to an EXPORTED value in one run and to a value DERIVED from each
    reader's own `__file__` in the next, with nothing in the output distinguishing them.

    THREE STATES, NOT TWO, and the third is why presence is not the question. Under that
    idiom an EMPTY string is falsy, so `MNV_REPO=""` is present in the environment and
    yet every reader derives anyway. Reporting `"MNV_REPO" in os.environ` would call that
    SET and be wrong about the effect. What is reported here is the resolution the
    READERS compute, which is the thing that decides which modules execute.

    It routes to the marker pair only through `checkout_root_of`, the same resolver the
    gate uses, for the reason in `TheInventoryReusesTheGuardsOwnResolver`: a receipt with
    its own checkout predicate could call a tree clean that the gate would refuse.
    `checkout_root_of` starts walking at the path's PARENT, so a DIRECTORY has to be
    probed through a child path -- passing the directory itself would silently answer
    about its parent, which is this defect's own shape one level up.
    """
    raw = os.environ.get("MNV_REPO")
    if raw is None:
        state, note = "ABSENT", ("every reader DERIVES its own root from its own __file__, so "
                                "there is no single value to report and the inventory above is "
                                "the only evidence of where modules came from")
    elif raw == "":
        state, note = "PRESENT-BUT-EMPTY", ("the variable is exported and every reader still "
                                            "DERIVES, because `os.environ.get(...) or ...` treats "
                                            "the empty string as absent -- presence and effect "
                                            "disagree here, and the effect is what runs")
    else:
        state, note = "SET", "every reader uses this one value, so it is stable across readers"
    lines = [f"{INVENTORY_PREFIX} MNV_REPO resolution={state}  value={raw!r}",
             f"{INVENTORY_PREFIX}   {note}"]
    if state == "SET":
        root = checkout_root_of(os.path.join(raw, "__mnv_repo_probe__"))
        if root is None:
            lines.append(f"{INVENTORY_PREFIX}   AND IT IS NOT A CHECKOUT ROOT. Reported, not "
                         f"refused. A non-checkout on sys.path[0] cannot shadow this tree's "
                         f"modules, so it is not run 4's shape -- but it is also not the value "
                         f"anyone intended, and it is invisible without this line.")
        elif root != expect_root:
            lines.append(f"{INVENTORY_PREFIX}   AND IT IS A DIFFERENT CHECKOUT FROM --expect-root: "
                         f"{root} vs {expect_root}. This is OI-136's exact shape at the ENV layer. "
                         f"It is reported and not refused, because the refusal half already "
                         f"decided this run on what was actually LOADED, and a receipt may not "
                         f"change an outcome -- but a reader who sees only the roots above would "
                         f"not know the intended root and the exported one disagree.")
        else:
            lines.append(f"{INVENTORY_PREFIX}   and it resolves to --expect-root, so the exported "
                         f"root and the intended root agree.")
    return lines


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
        # MECHANISM BEFORE RESULT: how the root was chosen is a precondition for reading the
        # rows below, so it goes above them. Inside the same `try`, so it inherits the same
        # failure isolation and still cannot change a run's outcome.
        say += _repo_env_capture(expect_root)
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
        say.append(f"{INVENTORY_PREFIX} SCOPE -- THIS INTERPRETER ONLY. Covered Python children "
                   f"write separate records with their own pid and depth; they never appear in "
                   f"this process's module list. Anything imported after this emission is not "
                   f"counted. Read it as 'AT LEAST these trees', never as 'only these trees'.")
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

# MERGE 2026-08-26: the two blocks below arrived from different lines and define DISJOINT
# functions -- no name collides. main contributed the sys.modules/stderr receipt; the
# build-k0-execution-integrity branch contributed the json writer, its verdict helper and
# the fail-soft wrapper. Both are retained; `main()` calls both.

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


def _verdict(outcome, origins, violation, launch_refusal=None) -> str:
    """The one-line human summary. It must never contradict `outcome`.

    ORDER MATTERS AND IS THE WHOLE POINT: a refusal outranks emptiness, because a refused run is
    empty for a reason that has nothing to do with what the entrypoint imports.
    """
    if launch_refusal is not None:
        return VERDICT_REFUSED_LAUNCH
    if violation is not None:
        return VERDICT_REFUSED
    if str(outcome).startswith("refused"):
        return VERDICT_REFUSED_SCRIPT
    if str(outcome).startswith("cannot-check"):
        return f"COULD NOT LOOK -- {outcome}; this is never 'we checked and it was clean'"
    return VERDICT_INSPECTED if origins else VERDICT_EMPTY


def write_inventory(dest, guard, script, expect_root, allow, outcome, violation=None,
                    site=SITE_NONE, label="") -> str | None:
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
    launch_refusal = guard.launch_refusal if guard is not None else None
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
        # ZERO WHEN NO GUARD WAS INSTALLED, BUT NEVER A BARE ZERO. `checked_provenance` says which
        # of the two zeros this is; `guard_installed` and `outcome` are the other two legs. F-9 is
        # read off that triple, never off `checked` alone.
        "checked": (guard.checked if guard is not None else 0),
        "checked_provenance": (CHECKED_MEASURED if guard is not None else CHECKED_NOT_MEASURED),
        "guard_installed": guard is not None,
        "propagation": (guard.propagation if guard is not None else "not-armed"),
        "launch_env": (guard.launch_env if guard is not None else "not-re-armed"),
        "propagated_from": (guard.propagated_from if guard is not None else None),
        "depth": (guard.depth if guard is not None else 0),
        "shim_sha256": (guard.shim_sha256 if guard is not None
                         else _sha256_or_none(str(SHIM_DIR / "sitecustomize.py"))),
        "chained_sitecustomize": (guard.chained_sitecustomize if guard is not None else {
            "found": False, "executed": False, "origin": None,
        }),
        # Which protection refused, or null when nothing did. An exit code cannot carry this.
        "refusal_site": site,
        # Free text from --label, so an artifact says WHICH ARM produced it. Two arms of the same
        # binary that differ only in --expect-root are otherwise easy to mistake for each other in
        # a directory of records, and a distinction a reader has to reconstruct is not carried.
        "label": label,
        # WRITTEN UNCONDITIONALLY (P-3). A zero here is a REPORTABLE STATE, never a pass.
        "repo_origin_count": len(origins),
        "repo_origin_inventory_is_empty": not origins,
        "repo_origins_outside_expect_root": len(outside),
        "repo_origins": origins,
        "outcome": outcome,
        "verdict": _verdict(outcome, origins, violation, launch_refusal),
        "offending_argv": (None if launch_refusal is None else launch_refusal["argv"]),
        "launch_refusal": launch_refusal,
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


def _report(exc: ImportTreeViolation, prefix: str = "[oi136]") -> None:
    print(
        f"\n{prefix} IMPORT TREE VIOLATION -- REFUSING BEFORE THE WORK RUNS.\n"
        f"{prefix}   module        {exc.module}\n"
        f"{prefix}   resolved to   {exc.origin}\n"
        f"{prefix}   which is in   {exc.found_root}\n"
        f"{prefix}   expected      {exc.expect_root}\n"
        f"{prefix} A HARDCODED sys.path.insert(0, ...) IS THE USUAL CAUSE, and a re-deploy will\n"
        f"{prefix} NOT fix it: an absolute insert at position 0 is not escaped by launching from\n"
        f"{prefix} another checkout and cannot be outranked by PYTHONPATH. Deployment parity can\n"
        f"{prefix} report every pinned file CURRENT while this is false -- that is OI-136, and it\n"
        f"{prefix} cost 3 h 08 m of A100 on 57266000_0. Fix the insert in the importing file, or\n"
        f"{prefix} pass --allow if this tree is genuinely intended.\n",
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
    ap.add_argument("--label", default="",
                    help="free text recorded in the inventory so an artifact says which ARM "
                         "produced it. Two arms differing only in --expect-root are otherwise "
                         "easy to confuse in a directory of records.")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    dest = os.path.abspath(args.inventory) if args.inventory else None
    guard = None
    script = None

    rest = list(args.rest)
    if not rest or rest[0] != "--":
        print("[oi136] usage: --expect-root <tree> [--allow <tree>] -- <script> [argv ...]\n"
              "[oi136] the `--` is MANDATORY and bare positionals are refused, so a child flag\n"
              "[oi136] can never be silently eaten by this wrapper (see remedy (A)'s wrapper).",
              file=sys.stderr)
        _safe_inventory(dest, None, None, args.expect_root, args.allow, "cannot-check:usage",
                        label=args.label)
        return CANNOT_CHECK_EXIT
    rest = rest[1:]
    if not rest:
        print("[oi136] nothing to run after `--`", file=sys.stderr)
        _safe_inventory(dest, None, None, args.expect_root, args.allow,
                        "cannot-check:nothing-after-split", label=args.label)
        return CANNOT_CHECK_EXIT

    expect = pathlib.Path(args.expect_root).resolve()
    if not is_checkout(expect):
        print(f"[oi136] COULD NOT LOOK: --expect-root {expect} is not a checkout "
              f"(needs {' and '.join(MARKERS)}). Exit 2 and not 3 on purpose: this is "
              f"'we could not check', never 'we checked and it was clean'.", file=sys.stderr)
        _safe_inventory(dest, None, None, str(expect), args.allow,
                        "cannot-check:expect-root-is-not-a-checkout", label=args.label)
        return CANNOT_CHECK_EXIT

    script = pathlib.Path(rest[0])
    if not script.is_file():
        print(f"[oi136] COULD NOT LOOK: no such script {script}", file=sys.stderr)
        _safe_inventory(dest, None, None, str(expect), args.allow, "cannot-check:no-such-script",
                        label=args.label)
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
                        "refused:script-outside-expect-root",
                        site=SITE_SCRIPT_CONTAINMENT, label=args.label)
        return VIOLATION_EXIT

    os.environ[INVENTORY_ENV] = "" if dest is None else str(dest)
    try:
        guard = install(str(expect), args.allow)
    except RuntimeError as exc:
        print(f"[oi136] COULD NOT LOOK: guard installation failed: {exc}", file=sys.stderr)
        _safe_inventory(dest, None, script, str(expect), args.allow,
                        "cannot-check:guard-installation-failed", label=args.label)
        return CANNOT_CHECK_EXIT

    # Replicate what `python <script>` does and runpy.run_path does NOT: the script's
    # own directory at sys.path[0]. Silently differing from direct execution would be
    # a fresh instance of this very defect.
    sys.path.insert(0, str(script.resolve().parent))
    sys.argv = [str(script), *rest[1:]]

    outcome, violation, recorded, site = "ok", None, True, SITE_NONE
    try:
        runpy.run_path(str(script), run_name="__main__")
    except ImportTreeViolation as exc:
        outcome, violation, site = "refused:import-tree-violation", exc, SITE_IMPORT_RESOLUTION
        _report(exc)
        return VIOLATION_EXIT
    except SystemExit as exc:
        # The child's own status is preserved (see EXIT CODES above), so this is NOT an error path --
        # but the record must be written for it, or every entrypoint that ends in `sys.exit()` would
        # emit no inventory at all and F-4 would count them as missing.
        if guard.launch_refusal is not None:
            outcome, site = "refused:launch-python-startup-flags", SITE_LAUNCH
        else:
            outcome = f"child-systemexit:{exc.code!r}"
        raise
    except BaseException as exc:                      # noqa: BLE001 - re-raised immediately
        outcome = f"child-exception:{type(exc).__name__}"
        raise
    finally:
        recorded = _safe_inventory(dest, guard, script, str(expect), args.allow,
                                   outcome, violation, site=site, label=args.label)
        # MERGE 2026-08-26: main's stderr receipt is invoked here too, so its
        # feature is live rather than dead code. It returns None on every path
        # and swallows BaseException, so it cannot change this run's outcome.
        _emit_inventory(str(expect), violation)
    return 0 if recorded else CANNOT_CHECK_EXIT


if __name__ == "__main__":
    sys.exit(main())
