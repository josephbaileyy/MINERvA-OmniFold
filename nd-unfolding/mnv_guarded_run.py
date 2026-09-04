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
with the propagation contract and shim-first `PYTHONPATH`. An ARGV that strips the
contract is re-armed too where the argv is ours to rewrite: `env -i`,
`env -u MNV_GUARD_MODULE` and `env PYTHONPATH=...` are repaired by INSERTING the
contract as `NAME=VALUE` operands immediately before `env`'s command word, which
is the argv spelling of the same repair `env={}` already gets and leaves the
launch running instead of refused. Where the repair is impossible the launch is
REFUSED instead: a command that arrived inside a STRING this guard will not
rewrite (`env -S`, `sh -c`), and a Python child of a process that deleted a
`MNV_GUARD_*` variable or overwrote `PYTHONPATH` in its own `os.environ` after
`install()` -- there is nothing left to re-arm from. So a Python child of a
guarded interpreter either starts guarded or does not start.

THE LAUNCH ARGV IS PARSED, NOT PATTERN-MATCHED, AND AN UNMODELLED SPELLING REFUSES.
Round 5 of review reached the wrong-tree import through `env -- python -I ...` and
`env -S 'python -I ...'`: the earlier parser modelled a subset of `env`'s options and
LEFT AN UNRECOGNISED PREFIX UNSCANNED, so both forms exited 0 and emitted only the
parent's inventory. "Unparsed" is now a REFUSAL and never a pass. `_parse_env`
implements the whole coreutils/BSD grammar -- `--`, `-i`/`--ignore-environment`,
`-u NAME`/`-uNAME`/`--unset=NAME`, `-C DIR`/`--chdir=DIR`, `-0`/`--null`,
`-v`/`--debug`, `-S STRING`/`--split-string=STRING`, the four signal options,
`--argv0=NAME`/`-a NAME`, then `NAME=VALUE` assignments, then the command -- and the
same fail-closed rule covers the other launch wrappers a science launcher reaches
for: `nohup`, `nice`, `stdbuf`, `timeout`, `time`, `command`, `exec` and `xargs`.
The resolved command is then subject to the SAME Python-flag scan and re-arming as a
direct launch, however deep the wrapper nesting.

`srun`, `mpirun` and the other job launchers are DELIBERATELY NOT in that table, and
saying so is part of the contract. Their option grammars are large enough that a
fail-closed parser would refuse correct submissions, so they are treated as ordinary
non-Python children: they inherit the re-armed contract AND the wrapper directory on
`PATH`, so `srun python3 -I x.py` is refused by the wrapper rather than by the argv
scan, and `srun /abs/python3 -I x.py` is the declared gap below. What is NOT true of
them is that this file parsed them.

`sh -c`, `bash -c` and `zsh -c` carry a COMMAND STRING rather than an argv, so the
string is tokenised with `shlex`, split into simple commands at `;`, `&&`, `||`,
`|`, `&` and unquoted newlines, and every simple command whose executable is a
Python interpreter is scanned by the same grammar. A string the tokenizer cannot
parse is refused rather than skipped, and so is a shell option this parser does not
model, for the reason above. An interpreter named by an ABSOLUTE PATH counts as
Python: `/usr/bin/python3.11 -I` is the same request as `python3 -I`.

INTERPRETER WRAPPERS ON PATH COVER THE SECOND LAUNCH SITE. `install()` also prepends
`mnv_guard_shim/bin/` -- tracked wrappers named `python3` and `python`, plus one
generated at arm time for the basename of `sys.executable` when that is neither --
and exports `MNV_GUARD_REAL_PYTHON`, `MNV_GUARD_PATH_SHIM_DIRS`. Each wrapper is
POSIX `sh`: it re-injects the shim-first `PYTHONPATH`, delegates the argv scan to
`mnv_guard_shim/scan_argv.py` running under the guard's OWN grammar rather than a
retyped copy of it, refuses `-S`/`-I`/`-E` in every spelling, and otherwise `exec`s
the real interpreter of the same name resolved through `PATH` with the shim
directories removed (`MNV_GUARD_REAL_PYTHON` is the recorded fallback, not a
substitution: a wrapper must not silently change WHICH interpreter runs). This is
what covers a bash child running `python3 -I child.py`. Every inventory record says
`path_shim: armed`; a deployment whose tree lacks `bin/` records `not-armed:<why>`
instead, because a missing half must be READABLE and never inferred from silence.
The wrappers are tracked, but a `sh` script installed on `PATH` as `python3` cannot
carry a `.sh` suffix -- the suffix would be part of the name it intercepts -- so the
A-2(f) source manifest does not bind them and `path_shim_sha256` in every record
does instead. See `_path_shim_digests`.

THE ONE DECLARED RESIDUAL GAP, AFTER BOTH HALVES, is a non-Python child that invokes
the interpreter by an ABSOLUTE PATH with `-S`, `-I` or `-E`, or that clears `PATH` or
the environment before invoking it. Neither half can reach it: the argv is built
inside a process this interpreter does not guard, an absolute path consults no `PATH`
and therefore no wrapper, and a cleared environment removes both the wrapper
directory and the contract. It is written into EVERY inventory record as
`declared_gap` so a ratchet reader sees the coverage boundary without reading this
file, and it is measured -- not asserted -- in
`tests/test_mnv_guarded_run.py::TheSubprocessBoundaryIsCovered`, beside the covered
counterparts it must be distinguished from. Read `declared_gap` together with
`path_shim`: when `path_shim` is not `armed` the boundary is WIDER than that
sentence, because the `PATH`-wrapper half did not run.

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
         without the guard -- a startup flag that prevents shim installation, an argv or
         environment that strips the propagation contract, or a launch prefix whose grammar
         this guard does not model and therefore CANNOT scan (fail-closed: unparsed is a
         refusal, never a pass)
2 is deliberately not 3, so "we could not check" can never be read as "we checked
and it was clean".
"""
from __future__ import annotations

import argparse
import atexit
import datetime
import functools
import hashlib
import inspect
import json
import os
import pathlib
import re
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile

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

#: The PATH half of the contract. `MNV_GUARD_REAL_PYTHON` is a RECORDED FALLBACK and not a
#: substitution: the wrapper resolves the interpreter of its own name through `PATH` with the shim
#: directories removed first, so a run that asked for `/opt/env/bin/python3` does not silently get
#: this process's `sys.executable`. `MNV_GUARD_PATH_SHIM_DIRS` is what lets the wrapper subtract
#: itself from `PATH` -- and what lets an inheriting `install()` drop its parent's generated
#: directory instead of growing `PATH` by one entry per process boundary.
#: `MNV_GUARD_WRAPPER_NAME` is set by a delegating wrapper and UNSET by the one it delegates to,
#: because a leaked value would make a grandchild's `python3` resolve the parent's name instead.
REAL_PYTHON_ENV = "MNV_GUARD_REAL_PYTHON"
PATH_SHIM_DIRS_ENV = "MNV_GUARD_PATH_SHIM_DIRS"
WRAPPER_NAME_ENV = "MNV_GUARD_WRAPPER_NAME"
PATH_SHIM_DIR = SHIM_DIR / "bin"
SCAN_ARGV_FILE = SHIM_DIR / "scan_argv.py"

#: Wrapper basenames the tracked `bin/` already carries. Any other `sys.executable` basename --
#: `python3.11`, `python3.12` -- gets a generated delegator at arm time, because a wrapper only
#: intercepts the NAME it is installed under and the versioned name is the one a cluster module
#: file puts in front of a science script.
TRACKED_WRAPPER_NAMES = ("python3", "python")

#: THE COVERAGE BOUNDARY, AS A STRING IN EVERY RECORD. A gap stated only in a docstring is invisible
#: to the ratchet readers that consume these records, and a reader who cannot see the boundary reads
#: a green record as total coverage. Read it beside `path_shim`: when that is not `armed` the
#: boundary is wider than this sentence, because the PATH-wrapper half did not run.
DECLARED_GAP = ("a non-Python child that invokes the interpreter by an ABSOLUTE PATH with -S, -I or "
                "-E, or that clears PATH or the environment before invoking it: the argv is built "
                "inside a process this interpreter does not guard, an absolute path consults no "
                "PATH and therefore no wrapper, and a cleared environment removes both the wrapper "
                "directory and the propagation contract")

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
        #: The PATH-wrapper half's state, set by `install()` through `_arm_path_shim`. "not-armed"
        #: until then, because a record written before arming must not claim the half ran.
        self.path_shim = "not-armed"
        self.path_shim_sha256 = _path_shim_digests()
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


def _arm_child_environment(expect_root: str, allow: tuple[str, ...]) -> "tuple[str, dict]":
    """Arm inheriting Python children through the tracked sitecustomize shim and the PATH wrappers.

    Returns `(path_shim state, wrapper digests)`. The state is a RECORDED FIELD and not a boolean:
    the sitecustomize half and the PATH half fail independently, and a deployment carrying only the
    first is a NARROWER guard rather than a broken one. See `_arm_path_shim`.
    """
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
    return _arm_path_shim()


def _path_shim_digests() -> dict:
    """sha256 of every tracked file the PATH half executes, or None where one cannot be read.

    WHY THE DIGESTS ARE IN THE RECORD AND NOT ONLY IN GIT. The wrappers are tracked, but the A-2(f)
    source manifest binds `.py` and `.sh` files -- and a POSIX `sh` script installed on `PATH` as
    `python3` cannot carry a suffix, because the suffix would be part of the name it intercepts. So
    the manifest does not cover `bin/python3` or `bin/python`, and widening its suffix rule is a
    change to another contract's semantics rather than a fix here. What binds these bytes is
    therefore this digest, recorded per run beside `shim_sha256`, which is the same instrument the
    sitecustomize half already uses. `scan_argv.py` IS manifest-covered and is digested anyway:
    reading two of the three from one place and the third from another is how a reader ends up
    comparing unlike things.
    """
    return {
        "bin/python3": _sha256_or_none(str(PATH_SHIM_DIR / "python3")),
        "bin/python": _sha256_or_none(str(PATH_SHIM_DIR / "python")),
        "scan_argv.py": _sha256_or_none(str(SCAN_ARGV_FILE)),
    }


def _arm_path_shim() -> "tuple[str, dict]":
    """Put the interpreter wrappers in front of `PATH`; return the state to record.

    THE SECOND LAUNCH SITE, WHICH `sitecustomize` CANNOT REACH. A non-Python child -- a bash script
    on a Slurm arm -- runs `python3 -I child.py`, and isolated mode ignores the inherited shim, so
    the contract this process exported cannot install anything. The wrapper intercepts that launch
    by NAME: it is found through `PATH`, refuses the isolating flags with the guard's own grammar,
    and otherwise `exec`s the interpreter the caller asked for.

    A WRAPPER ONLY INTERCEPTS THE NAME IT IS INSTALLED UNDER, which is why the versioned basename of
    `sys.executable` is generated at arm time when the tracked pair does not already cover it: a
    cluster module file puts `python3.11` in front of a science script, and a `bin/` holding only
    `python3` and `python` would watch that launch go past.

    IT RETURNS A STATE RATHER THAN RAISING. A deployed tree that carries `sitecustomize.py` and not
    `bin/` still gets the whole first half of the contract, and refusing the run would convert a
    narrower guard into no run at all -- while a SILENT narrowing is what the campaign refuses. So
    the state goes into every inventory record beside `declared_gap`, where a reader who did not
    run the command can see which half was armed.
    """
    wrapper = PATH_SHIM_DIR / "python3"
    digests = _path_shim_digests()
    if not wrapper.is_file():
        return f"not-armed:the tracked interpreter wrapper is missing at {wrapper}", digests
    if not SCAN_ARGV_FILE.is_file():
        return f"not-armed:the tracked argv scanner is missing at {SCAN_ARGV_FILE}", digests
    state = "armed"
    directories = [str(PATH_SHIM_DIR.resolve())]
    basename = _executable_basename(sys.executable)
    if basename and basename not in TRACKED_WRAPPER_NAMES:
        try:
            directories.insert(0, _generated_wrapper_dir(basename, wrapper.resolve()))
        except OSError as err:
            # Tracked names still intercept `python3`/`python`; the VERSIONED name does not, and
            # that difference is exactly what a reader must not have to guess at.
            state = (f"armed-tracked-names-only:no wrapper for {basename} could be generated "
                     f"({err})")
    os.environ[REAL_PYTHON_ENV] = sys.executable
    inherited = [entry for entry in (os.environ.get(PATH_SHIM_DIRS_ENV) or "").split(os.pathsep)
                 if entry]
    os.environ[PATH_SHIM_DIRS_ENV] = os.pathsep.join(directories)
    # A PARENT'S GENERATED DIRECTORY IS DROPPED RATHER THAN KEPT IN FRONT. Re-prepending at every
    # process boundary would grow PATH by one entry per depth and leave a torn-down temp directory
    # ahead of the live one; the inherited list is exactly the set that is safe to remove.
    superseded = set(directories) | set(inherited)
    entries = [entry for entry in (os.environ.get("PATH") or os.defpath).split(os.pathsep)
               if entry not in superseded]
    os.environ["PATH"] = os.pathsep.join([*directories, *entries])
    return state, digests


def _generated_wrapper_dir(basename: str, tracked: pathlib.Path) -> str:
    """A per-process directory holding one delegating wrapper named `basename`.

    IT DELEGATES RATHER THAN DUPLICATES. The wrapper body is the tracked file, and this writes four
    lines that hand it the NAME to resolve -- so a fix to the body reaches the generated wrapper
    too, and there is no second copy of the logic to drift. `MNV_GUARD_WRAPPER_NAME` is exported
    here and UNSET by the body before it execs, or a grandchild's `python3` would resolve this
    name instead of its own.
    """
    directory = tempfile.mkdtemp(prefix=f"mnv-guard-bin-{os.getpid()}-")
    generated = pathlib.Path(directory) / basename
    generated.write_text(
        "#!/bin/sh\n"
        f"# GENERATED at arm time by {__file__} for this process only. Not tracked, not evidence:\n"
        "# it exists because a wrapper intercepts only the NAME it is installed under, and the\n"
        "# tracked bin/ carries python3 and python. The body it delegates to IS tracked.\n"
        f"MNV_GUARD_WRAPPER_NAME={shlex.quote(basename)}\n"
        "export MNV_GUARD_WRAPPER_NAME\n"
        f"exec {shlex.quote(str(tracked))} \"$@\"\n",
        encoding="utf-8",
    )
    generated.chmod(0o755)
    #: Best-effort removal, and deliberately not a guarantee: an `os.exec*` replacement never runs
    #: atexit, and a child outliving its parent must not lose its interpreter. Losing this
    #: directory costs the VERSIONED name only -- the tracked directory is still on PATH behind it.
    atexit.register(shutil.rmtree, directory, True)
    return directory


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
    armed["PYTHONPATH"] = _shim_first_pythonpath(env.get("PYTHONPATH"))
    guard.launch_env = "re-armed"
    return armed


def _shim_first_pythonpath(existing) -> str:
    """The shim directory, then every entry of `existing` that is not already the shim.

    ONE IMPLEMENTATION, TWO CALLERS -- the `env=` keyword repair and the `env` ARGV repair. They
    have to agree: an argv-level re-arm that assembled PYTHONPATH differently from the keyword-level
    one would make the same launch guarded in one spelling and not in the other, which is the class
    of divergence this whole file exists to refuse.
    """
    if isinstance(existing, bytes):
        existing = os.fsdecode(existing)
    entries = [] if not existing else str(existing).split(os.pathsep)
    shim = SHIM_DIR.resolve()
    retained = []
    for entry in entries:
        try:
            is_shim = pathlib.Path(entry or os.curdir).resolve() == shim
        except OSError:
            is_shim = False
        if not is_shim:
            retained.append(entry)
    return os.pathsep.join([str(shim), *retained])


#: `env` is the ARGV spelling of two things this guard already refuses in their keyword spelling:
#: "the real executable is a later word" and, for `env -i`, THE CLEARED ENVIRONMENT the reviewer's
#: finding names. Neither the flag scan nor `_rearm_launch_environment` sees it on its own -- the
#: scan resolves a non-Python executable, and the keyword re-arm is handed `env=None` because the
#: stripping happens in the launched process rather than in the caller -- so an unhandled
#: `env -i python3 child.py` from a guarded interpreter reproduces the finding verbatim.
_ENV_BASENAMES = frozenset({"env"})


class _LaunchRefusal(Exception):
    """A launch this guard cannot SCAN, and therefore will not allow.

    THE ROUND-5 FINDING WAS THE ABSENCE OF THIS CLASS. The previous parser returned None for an
    `env` prefix whose options it did not model, and None meant "leave the launch alone" -- so
    `env -- python -I child.py` and `env -S 'python -I child.py'` were LEFT UNSCANNED, ran the
    wrong-tree import, and exited 0 with only the parent's inventory to show for it. Every
    not-modelled and not-parseable path now raises this instead, which makes "we could not read
    this launch" a refusal rather than a pass. The cost is the opposite direction -- a correct
    `env --some-new-option ./binary` is refused -- and that cost is deliberate and cheap to fix:
    add the option to the table below, with a control.
    """

    def __init__(self, reason: str, offending: str, executable: "str | None" = None):
        self.reason = reason
        self.offending = offending
        #: The executable the refusal is ABOUT, when the walk got far enough to know it -- the
        #: resolved interpreter rather than the `env`/`bash` word in front of it. The record's
        #: `executable` field otherwise names the wrapper, which answers a different question than
        #: the one a reader of a refusal asks.
        self.executable = executable
        super().__init__(f"{reason}: {offending}")


#: `env`'s FULL option grammar, coreutils and the BSD `env` macOS ships, as the union of the two.
#: The union is the fail-closed direction: modelling an option the local `env` lacks costs a launch
#: nobody makes, while omitting one the local `env` HAS is exactly the round-5 defect.
#: `-P utilpath` is deliberately NOT modelled and therefore refuses: it changes the search path
#: `env` uses to find the utility, so a parser that accepted it would resolve the executable
#: through a PATH the launch does not use and answer confidently about the wrong file.
_ENV_FLAG_OPTIONS = frozenset({
    "-i", "--ignore-environment", "-0", "--null", "-v", "--debug",
    "--list-signal-handling",
})
_ENV_VALUE_OPTIONS = frozenset({
    "-u", "--unset", "-C", "--chdir", "-S", "--split-string", "-a", "--argv0",
})
#: Long options whose value, when present, is ATTACHED with `=`. coreutils takes no separate word
#: for these, so `--ignore-signal INT` means "ignore every signal, then run INT".
_ENV_OPTIONAL_VALUE_LONG = frozenset({"--default-signal", "--ignore-signal", "--block-signal"})
_ENV_CLEARING_OPTIONS = frozenset({"-", "-i", "--ignore-environment"})
_ENV_SPLIT_STRING_OPTIONS = frozenset({"-S", "--split-string"})
_ENV_UNSET_OPTIONS = frozenset({"-u", "--unset"})

#: Launch wrappers that are not `env`: each runs a LATER WORD as the real command, so an unhandled
#: one hides a Python child exactly as `env` did. Same fail-closed rule -- an option not in the
#: table refuses -- and the same reason. `positionals` is how many non-option operands come BEFORE
#: the command (`timeout DURATION COMMAND`); `print_only` options make the wrapper report instead
#: of exec, so they launch nothing and are allowed; `clearing` options wipe the environment.
_WRAPPER_SPECS = {
    "nohup": {"flags": frozenset(), "values": frozenset()},
    "nice": {"flags": frozenset(), "values": frozenset({"-n", "--adjustment"}),
             "numeric_short": True},
    "stdbuf": {"flags": frozenset(),
               "values": frozenset({"-i", "--input", "-o", "--output", "-e", "--error"})},
    "timeout": {"flags": frozenset({"--preserve-status", "--foreground", "-v", "--verbose"}),
                "values": frozenset({"-s", "--signal", "-k", "--kill-after"}),
                "positionals": 1},
    "time": {"flags": frozenset({"-p", "--portability", "-a", "--append", "-v", "--verbose",
                                 "-q", "--quiet"}),
             "values": frozenset({"-o", "--output", "-f", "--format"})},
    "command": {"flags": frozenset({"-p"}), "values": frozenset(),
                "print_only": frozenset({"-v", "-V"})},
    "exec": {"flags": frozenset({"-l"}), "values": frozenset({"-a"}),
             "clearing": frozenset({"-c"})},
    # `-i`, `-e`, `--replace` and `--eof` appear in BOTH tables, which is not a mistake: GNU xargs
    # gives them OPTIONAL arguments, so the bare spelling consumes nothing and only the ATTACHED
    # spelling (`-i{}`, `-eEOF`) carries a value. Listing them as value-taking only would make
    # `xargs -i python3 x.py` eat the interpreter word and scan `x.py` instead -- an option's value
    # swallowing the command is the same fail-open the `env` parser was rebuilt for.
    "xargs": {"flags": frozenset({"-0", "--null", "-r", "--no-run-if-empty", "-t", "--verbose",
                                  "-x", "--exit", "-p", "--interactive", "-o", "--open-tty",
                                  "-i", "-e", "--replace", "--eof"}),
              "values": frozenset({"-n", "--max-args", "-P", "--max-procs", "-s", "--max-chars",
                                   "-L", "--max-lines", "-I", "-i", "--replace", "-d",
                                   "--delimiter", "-a", "--arg-file", "-E", "-e", "--eof"})},
}

#: Shells whose `-c` argument is a COMMAND STRING and not an argv. Their own option grammar is
#: modelled for the same fail-closed reason as `env`'s: an unmodelled option can consume the token
#: that holds the command string, and reading the wrong token as the command is worse than refusing.
_SHELL_BASENAMES = frozenset({"sh", "bash", "zsh", "dash", "ksh", "mksh"})
#: `c` is in the set because a cluster is what carries it -- `bash -lc <string>` is the spelling a
#: login-shell launcher uses, and a table that listed every OTHER short flag but not `c` refused
#: exactly the invocations it was written to read (measured on `bash -c` itself).
_SHELL_FLAG_CHARS = "abcCefhiklmnpstuvxBDPT"
_SHELL_VALUE_OPTIONS = frozenset({"-o", "+o", "-O", "+O", "--rcfile", "--init-file"})
_SHELL_FLAG_LONG = frozenset({"--login", "--noprofile", "--norc", "--posix", "--noediting",
                              "--interactive", "--verbose", "--debugger", "--restricted"})

#: Shell-string operator characters, CLASSIFIED BY SHAPE RATHER THAN ENUMERATED. A token made only
#: of these is an operator: one containing `<` or `>` is a redirection, whose TARGET must be dropped
#: with it, and anything else (`;`, `&&`, `||`, `|`, `&`, `(`, `)`, `{`, `}`, `;;`, `|&`) ends a
#: simple command. Enumerating the spellings instead was WRONG IN THE FAIL-OPEN DIRECTION and the
#: two measured escapes are why this is a character class: `python3 2>/dev/null -I x.py` tokenises
#: with a bare `2` that ended the flag scan before the `-I`, and bash's `&>` is a spelling no
#: redirection list I wrote contained. A leading file-descriptor digit is dropped with the operator
#: for the same reason.
_SHELL_PUNCTUATION = frozenset(";&|<>(){}")

#: How deep a wrapper chain is followed before the launch is refused as unreadable. `env nice nohup
#: timeout 5 python -I x` is four; a chain longer than this is not a launcher, and an unbounded walk
#: over an argv that can be shaped by a child is not a walk this file should contain.
_MAX_WRAPPER_DEPTH = 8

#: WHY the launch was refused, as a field. Every refusal here is the same SITE (this wrapper owns one
#: launch boundary) and the same exit code, and the repo's own rule -- see the `SITE_*` block --
#: is that a reader must not have to parse which check fired out of prose.
LAUNCH_REASON_FLAGS = "python-startup-flags-bypass-the-shim"
LAUNCH_REASON_ENV = "the-launch-argv-or-environment-strips-the-propagation-contract"
LAUNCH_REASON_UNMODELLED = "a-launch-wrapper-option-this-guard-does-not-model"
LAUNCH_REASON_UNPARSED = "a-launch-argv-or-command-string-this-guard-cannot-parse"

_LAUNCH_HEADLINES = {
    LAUNCH_REASON_FLAGS: "PYTHON STARTUP FLAGS BYPASS THE IMPORT SHIM",
    LAUNCH_REASON_ENV: "THE CHILD WOULD START WITHOUT THE PROPAGATION CONTRACT",
    LAUNCH_REASON_UNMODELLED: "THIS LAUNCH PREFIX USES AN OPTION THIS GUARD DOES NOT MODEL",
    LAUNCH_REASON_UNPARSED: "THIS LAUNCH CANNOT BE PARSED, SO IT CANNOT BE SCANNED",
}

_LAUNCH_EXPLANATIONS = {
    LAUNCH_REASON_FLAGS: ("-S, -I and -E prevent reliable sitecustomize propagation. -I must be "
                          "handled by a launcher-design change, not a guard exception."),
    LAUNCH_REASON_ENV: ("The interpreter would start with no MNV_GUARD_* contract or no shim-first "
                        "PYTHONPATH, so it could not install the guard. An environment passed as "
                        "`env=` is re-armed, and so is an `env NAME=VALUE`/`env -i`/`env -u` argv "
                        "this guard can rewrite; one arriving inside a STRING, or deleted from "
                        "this process's own os.environ, cannot be, so the launch is refused."),
    LAUNCH_REASON_UNMODELLED: ("An unmodelled option is not a safe option: its VALUE may be the "
                               "command word, so the scan would read the wrong token and answer "
                               "confidently about the wrong file. Round 5 reached the wrong-tree "
                               "import through exactly this hole, when an unmodelled prefix was "
                               "LEFT UNSCANNED instead of refused. Add the option to "
                               "_ENV_FLAG_OPTIONS/_ENV_VALUE_OPTIONS or _WRAPPER_SPECS, with a "
                               "control, rather than switching the guard off."),
    LAUNCH_REASON_UNPARSED: ("A command string that shlex cannot tokenise, a value-taking option "
                             "with no value, or a wrapper chain deeper than this file follows. "
                             "None of them can be scanned, and an unscanned Python launch is the "
                             "defect this guard exists for."),
}


#: The `outcome` string each launch-refusal reason records. TWO OUTCOMES AND NOT FOUR: the pair that
#: refuses a launch this guard READ keeps the outcome downstream controls already name, and the pair
#: that refuses a launch it COULD NOT READ gets its own, because those are the two different claims
#: a reader of a record has to be able to tell apart. The reason field carries the finer detail.
LAUNCH_OUTCOMES = {
    LAUNCH_REASON_FLAGS: "refused:launch-python-startup-flags",
    LAUNCH_REASON_ENV: "refused:launch-python-startup-flags",
    LAUNCH_REASON_UNMODELLED: "refused:launch-unmodelled-launch-grammar",
    LAUNCH_REASON_UNPARSED: "refused:launch-unmodelled-launch-grammar",
}


def launch_outcome(refusal: "dict | None") -> str:
    """The `outcome` for a launch refusal. Shared with the shim, which records the same states."""
    reason = (refusal or {}).get("reason", LAUNCH_REASON_FLAGS)
    return LAUNCH_OUTCOMES.get(reason, "refused:launch-python-startup-flags")


def _executable_basename(word: str) -> str:
    """The basename a wrapper table is keyed by, `.exe` suffix removed."""
    name = pathlib.Path(word).name
    if name.lower().endswith(".exe"):
        name = name[:-4]
    return name


def _split_string_tokens(text: str, option: str) -> list[str]:
    """`env -S`'s STRING, split the way `env` splits it. A string that will not split REFUSES.

    coreutils' `-S` has its own escape layer (`\\c`, `\\_`, `${VAR}`) on top of shell-like quoting.
    `shlex` in POSIX mode covers the quoting, which is the part that decides WHERE THE WORDS ARE --
    and the words are all this scan needs. What it does not model (variable expansion) can only
    make a token longer or shorter, never turn a non-interpreter word into `python -I`; and a
    string it cannot tokenise at all is refused rather than guessed.
    """
    try:
        return shlex.split(text, posix=True)
    except ValueError as err:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{option} {text!r}: {err}") from err


def _parse_env(argv: list[str]) -> "dict | None":
    """Parse an `env ...` launch. Returns None when it launches nothing; REFUSES the unmodelled.

    The result is `{"command", "index", "clears", "stripped", "assignments"}`:
      command      -- the argv `env` would exec, `command[0]` being the executable word
      index        -- where in THIS argv the command word sits, so the contract can be re-armed by
                      inserting `NAME=VALUE` operands there; None when the command came out of a
                      `-S` string, which this guard will not rewrite
      clears       -- `-i`, `--ignore-environment` or the legacy bare `-` was given
      stripped     -- the first operand that removes or overwrites a contract variable
      assignments  -- every `NAME=VALUE` operand, last-wins, so a repair can PRESERVE an explicit
                      PYTHONPATH with the shim in front rather than overwriting the caller's value
      unset        -- every `-u NAME`, so a repair does not silently restore a variable the caller
                      deliberately removed; only the contract's own variables are put back
    """
    index = 1
    options_done = False
    clears = False
    stripped: "str | None" = None
    assignments: dict[str, str] = {}
    unset: set[str] = set()
    while index < len(argv):
        token = argv[index]
        if not options_done:
            if token == "--":
                options_done = True          # `--` ends OPTIONS; operands still parse below
                index += 1
                continue
            if token in _ENV_CLEARING_OPTIONS:
                clears = True
                index += 1
                continue
            if token in _ENV_FLAG_OPTIONS or token in _ENV_OPTIONAL_VALUE_LONG:
                index += 1
                continue
            if token in _ENV_VALUE_OPTIONS:
                if index + 1 >= len(argv):
                    raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                         f"{token} with no value")
                value = argv[index + 1]
                if token in _ENV_SPLIT_STRING_OPTIONS:
                    return _parse_env_split_string(token, value, argv[index + 2:],
                                                   clears, stripped, assignments, unset)
                if token in _ENV_UNSET_OPTIONS:
                    unset.add(value)
                    if _breaks_propagation_contract(value, None):
                        stripped = stripped or f"{token} {value}"
                index += 2
                continue
            if token.startswith("--") and "=" in token:
                name, _, value = token.partition("=")
                if name in _ENV_OPTIONAL_VALUE_LONG:
                    index += 1
                    continue
                if name in _ENV_SPLIT_STRING_OPTIONS:
                    return _parse_env_split_string(name, value, argv[index + 1:],
                                                   clears, stripped, assignments, unset)
                if name in _ENV_VALUE_OPTIONS:
                    if name in _ENV_UNSET_OPTIONS:
                        unset.add(value)
                        if _breaks_propagation_contract(value, None):
                            stripped = stripped or token
                    index += 1
                    continue
                raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
            if token.startswith("-") and len(token) > 2 and not token.startswith("--"):
                #: A SHORT-OPTION CLUSTER, walked character by character exactly as
                #: `_forbidden_python_flag` walks CPython's. The BSD usage line is literally
                #: `env [-0iv] ...`, so `-iv` is a legal spelling and a parser that only understood
                #: `-i` would refuse a correct launch -- the direction that gets a guard removed.
                #: An attached value ENDS the cluster (`-uFOO`, `-Spython x.py`), which is why the
                #: walk breaks rather than continuing through the value's characters.
                consumed = 1
                position = 1
                while position < len(token):
                    character = token[position]
                    #: CLEARING IS TESTED BEFORE PLAIN FLAGS, and the order is a MEASURED bug fix:
                    #: `-i` is in both tables, so testing `_ENV_FLAG_OPTIONS` first consumed it as
                    #: an ordinary flag and `env -iv python x.py` came back with `clears=False` --
                    #: a cleared environment read as an armed one, which is the fail-open direction.
                    if f"-{character}" in _ENV_CLEARING_OPTIONS:
                        clears = True
                        position += 1
                        continue
                    if f"-{character}" in _ENV_FLAG_OPTIONS:
                        position += 1
                        continue
                    option = f"-{character}"
                    if option not in _ENV_VALUE_OPTIONS:
                        raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
                    value = token[position + 1:]
                    if not value:
                        if index + 1 >= len(argv):
                            raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                                 f"{option} with no value")
                        value, consumed = argv[index + 1], 2
                    if option in _ENV_SPLIT_STRING_OPTIONS:
                        return _parse_env_split_string(option, value, argv[index + consumed:],
                                                       clears, stripped, assignments, unset)
                    if option in _ENV_UNSET_OPTIONS:
                        unset.add(value)
                        if _breaks_propagation_contract(value, None):
                            stripped = stripped or token
                    break
                index += consumed
                continue
            if token.startswith("-"):
                raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        name, separator, value = token.partition("=")
        if separator and name:
            assignments[name] = value
            if _breaks_propagation_contract(name, value):
                stripped = stripped or token
            index += 1
            continue
        return {"command": argv[index:], "index": index, "clears": clears,
                "stripped": stripped, "assignments": assignments, "unset": unset}
    #: `env` with options and assignments but NO command word prints the environment and execs
    #: nothing, so there is no launch to scan. Parsed successfully and deliberately not refused --
    #: the fail-closed rule is about what this guard cannot READ, never about what it read as empty.
    return None


def _parse_env_split_string(option: str, text: str, remainder: list[str], clears: bool,
                           stripped: "str | None", assignments: dict,
                           unset: "set[str]") -> "dict | None":
    """Continue parsing at `-S STRING`'s split result, which may itself hold options.

    coreutils lets `-S` carry the whole invocation -- `env -S '-i python x.py'` is legal -- so the
    split tokens are re-parsed as `env`'s own argument list rather than assumed to be the command.
    `index` is dropped to None on this path: the command word no longer corresponds to a position
    in the argv the caller passed, and inserting an operand at a made-up index is how a repair
    becomes a corruption.
    """
    tokens = _split_string_tokens(text, option)
    parsed = _parse_env(["env", *tokens, *remainder])
    if parsed is None:
        return None
    parsed["index"] = None
    parsed["clears"] = parsed["clears"] or clears
    parsed["stripped"] = stripped or parsed["stripped"]
    merged = dict(assignments)
    merged.update(parsed["assignments"])
    parsed["assignments"] = merged
    parsed["unset"] = set(unset) | parsed["unset"]
    return parsed


def _parse_wrapper(argv: list[str], spec: dict) -> "int | None":
    """The index of the command word in a non-`env` launch wrapper, or None when none is launched.

    Fail-closed on the same rule as `_parse_env`: an option this spec does not list REFUSES,
    because its value may be the command word.
    """
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "--":
            index += 1
            break
        if token == "-" or not token.startswith(("-", "+")):
            break
        if token in spec.get("print_only", frozenset()):
            return None                      # reports instead of exec: nothing is launched
        if token in spec.get("clearing", frozenset()):
            raise _LaunchRefusal(LAUNCH_REASON_ENV, token)
        if token in spec["flags"]:
            index += 1
            continue
        if token in spec["values"]:
            if index + 1 >= len(argv):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{token} with no value")
            index += 2
            continue
        if token.startswith("--") and "=" in token:
            name = token.partition("=")[0]
            if name in spec["values"] or name in spec["flags"]:
                index += 1
                continue
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        if len(token) > 2 and not token.startswith("--") and token[:2] in spec["values"]:
            index += 1
            continue
        if spec.get("numeric_short") and re.fullmatch(r"[-+]-?\d+", token):
            index += 1                       # `nice -5`, `nice --5`: the legacy adjustment forms
            continue
        raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
    index += spec.get("positionals", 0)      # `timeout DURATION COMMAND`
    if index >= len(argv):
        return None
    return index


def _shell_command_string(argv: list[str]) -> "str | None":
    """The `-c` COMMAND STRING in a shell invocation, or None when the shell runs no string.

    Fail-closed on an unmodelled shell option for the reason on `_SHELL_VALUE_OPTIONS`: an option
    that consumes a word could consume the command string, and scanning the wrong token is worse
    than refusing. A shell invoked on a SCRIPT FILE has no string here and is not refused -- what
    that script does at ITS launch sites is the PATH wrapper's half of the contract.
    """
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "--":
            return None                      # everything after is the script and its argv
        if token == "-" or not token.startswith(("-", "+")):
            return None
        if token in _SHELL_VALUE_OPTIONS:
            if index + 1 >= len(argv):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{token} with no value")
            index += 2
            continue
        if token in _SHELL_FLAG_LONG:
            index += 1
            continue
        if token.startswith("--"):
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        cluster = token[1:]
        if "c" in cluster:
            if not set(cluster) <= set(_SHELL_FLAG_CHARS):
                raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
            if index + 1 >= len(argv):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{token} with no command string")
            return argv[index + 1]
        if not set(cluster) <= set(_SHELL_FLAG_CHARS):
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        index += 1
    return None


def _unquoted_lines(text: str) -> list[str]:
    """Split a command string at NEWLINES THAT ARE NOT INSIDE QUOTES.

    `shlex` treats a newline as ordinary whitespace, so `"cd x\\npython3 -I y.py"` tokenises to
    `['cd', 'x', 'python3', '-I', 'y.py']` and the `python3` reads as an ARGUMENT to `cd` -- the
    separator is gone and the isolated launch is invisible. `shlex.lineno` cannot repair it either:
    it counts the LINES THE LEXER HAS READ, not the position of the token it just yielded, so on
    that string it flags the boundary one token early (measured, not assumed).

    This is a quote-state scan and deliberately not a second tokenizer: it decides nothing about
    words, options or commands. An unbalanced quote raises, and the caller turns that into a
    refusal, because a string this cannot split is a string nothing can scan.
    """
    parts: list[str] = []
    current: list[str] = []
    quote: "str | None" = None
    escaped = False
    for character in text:
        if escaped:
            current.append(character)
            escaped = False
            continue
        if character == "\\" and quote != "'":
            current.append(character)
            escaped = True
            continue
        if quote is not None:
            if character == quote:
                quote = None
            current.append(character)
            continue
        if character in "\"'":
            quote = character
            current.append(character)
            continue
        if character == "\n":
            parts.append("".join(current))
            current = []
            continue
        current.append(character)
    if quote is not None:
        raise ValueError(f"no closing quotation in {text!r}")
    parts.append("".join(current))
    return parts


def _simple_commands(text: str) -> list[list[str]]:
    """Every SIMPLE COMMAND in a shell command string, tokenised, redirections removed.

    Split at `;`, `&&`, `||`, `|`, `&`, subshell parentheses and unquoted newlines, because each of
    those starts a command whose first word is an executable -- and a Python interpreter behind any
    of them is a launch this guard owns. Redirection operators take their target with them so that
    a redirection cannot end the startup-flag scan early.
    """
    commands: list[list[str]] = []
    for line in _unquoted_lines(text):
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)                 # ValueError here is the caller's refusal
        current: list[str] = []
        skip_next = False
        for token in tokens:
            if skip_next:
                skip_next = False
                continue
            if token and set(token) <= _SHELL_PUNCTUATION:
                if "<" in token or ">" in token:
                    if current and current[-1].isdigit():
                        current.pop()        # the file descriptor belongs to the redirection
                    skip_next = True         # drop the operator AND its target
                    continue
                if current:
                    commands.append(current)
                current = []
                continue
            current.append(token)
        if current:
            commands.append(current)
    return commands


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


def _resolve_launch_command(argv: list[str], env) -> "dict | None":
    """The command a launch will actually exec, after every wrapper prefix this guard models.

    Returns None when the launch execs nothing (`env` with no command word, `command -v`), and the
    same shape `_parse_env` documents otherwise, with `inject_at` counted in the ORIGINAL argv so a
    repair lands where `env` will read it. Raises `_LaunchRefusal` for a prefix this guard cannot
    read -- an unmodelled option, a value-taking option with no value, or nesting deeper than
    `_MAX_WRAPPER_DEPTH`.
    """
    command = list(argv)
    if not command:
        return None
    offset: "int | None" = 0
    clears = False
    stripped: "str | None" = None
    assignments: dict[str, str] = {}
    unset: set[str] = set()
    for _ in range(_MAX_WRAPPER_DEPTH):
        name = _executable_basename(_resolve_executable(command[0], env))
        if name in _ENV_BASENAMES:
            parsed = _parse_env(command)
            if parsed is None:
                return None
            clears = clears or parsed["clears"]
            stripped = stripped or parsed["stripped"]
            merged = dict(assignments)
            merged.update(parsed["assignments"])
            assignments = merged
            unset |= parsed["unset"]
            index = parsed["index"]
            offset = None if index is None or offset is None else offset + index
            command = parsed["command"]
            continue
        spec = _WRAPPER_SPECS.get(name)
        if spec is not None:
            index = _parse_wrapper(command, spec)
            if index is None:
                return None
            offset = None if offset is None else offset + index
            command = command[index:]
            continue
        return {"command": command, "inject_at": offset, "clears": clears,
                "stripped": stripped, "assignments": assignments, "unset": unset}
    raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                         f"launch wrappers nested deeper than {_MAX_WRAPPER_DEPTH}")


def _contract_operands(resolved: dict) -> "tuple[list[str], dict]":
    """The `NAME=VALUE` operands that re-arm an `env` launch, and the environment they produce.

    THE OPERANDS ARE THE ARGV SPELLING OF `_rearm_launch_environment`, and they are inserted rather
    than substituted: `env` applies assignments in order and the LAST one wins, so appending the
    contract in front of the command word repairs `-i`, `-u MNV_GUARD_MODULE` and an explicit
    `PYTHONPATH=...` alike while leaving every other operand the caller wrote exactly where it was.

    PATH IS DELIBERATELY NOT RESTORED. `env -i` clears it, and putting it back would overrule the
    caller on something that is not this guard's contract -- the interpreter itself needs no PATH.
    What is lost is the PATH-wrapper half for that child's own non-Python descendants, which is the
    `clears PATH or the environment` arm of `DECLARED_GAP` and is stated there rather than here.

    The returned environment view is what the caller checks with
    `_environment_reaching_child_is_armed`: if this process's own `os.environ` has already lost the
    contract, the operands carry empty values and the repair MUST fail rather than launch a child
    that reads an empty `MNV_GUARD_MODULE` as an armed one.
    """
    assignments = resolved["assignments"]
    operands, view = [], {}
    for name in PROPAGATION_ENV_VARS:
        value = os.environ.get(name, "")
        operands.append(f"{name}={value}")
        view[name] = value
    if "PYTHONPATH" in assignments:
        inherited = assignments["PYTHONPATH"]
    elif resolved["clears"] or "PYTHONPATH" in resolved["unset"]:
        inherited = ""
    else:
        inherited = os.environ.get("PYTHONPATH", "")
    pythonpath = _shim_first_pythonpath(inherited)
    operands.append(f"PYTHONPATH={pythonpath}")
    view["PYTHONPATH"] = pythonpath
    return operands, view


def _scan_shell_string(text: str, env, depth: int = 0) -> bool:
    """Scan a shell COMMAND STRING; raise to refuse, and return whether it launches an interpreter.

    THE RETURN VALUE IS LOAD-BEARING AND IS NOT A CONVENIENCE. `env -i bash -c 'python3 x.py'`
    holds no isolating flag and no disarming operand INSIDE the string -- the clearing happens
    outside it -- so a scan that only raised would have returned quietly and launched a shell whose
    interpreter starts unguarded. The caller therefore has to know whether the contract still has
    to reach this child, and it may not simply assume it does: requiring the contract for EVERY
    shell string would refuse `bash -c 'ls'` from a process that had disarmed itself, which is a
    launch with no interpreter in it and nothing to guard.

    A `-c` string is not an argv, so nothing above can see the interpreter inside it: round 5's
    `bash -c "python3 -I child.py"` is the same request as `python3 -I child.py` at a launch site,
    and it was invisible. Every simple command is resolved through the same wrapper grammar, and a
    LEADING `NAME=VALUE` prefix is read as that command's environment because every shell applies
    it that way -- `PYTHONPATH=/nowhere python3 x.py` disarms the child exactly as `env` would.

    A STRING IS REFUSED AND NEVER REPAIRED. Rewriting a command string means re-quoting somebody
    else's shell program, and a guard that edits a shell string can change what a run computes.
    The argv spelling is repaired because the tokens are ours to insert between; this one is not.
    """
    try:
        commands = _simple_commands(text)
    except ValueError as err:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{text!r}: {err}") from err
    launches_python = False
    for command in commands:
        stripped = None
        index = 0
        while index < len(command):
            name, separator, value = command[index].partition("=")
            if not separator or not name:
                break
            if _breaks_propagation_contract(name, value):
                stripped = stripped or command[index]
            index += 1
        command = command[index:]
        if not command:
            continue
        resolved = _resolve_launch_command(command, env)
        if resolved is None:
            continue
        target = _resolve_executable(resolved["command"][0], env)
        if _executable_basename(target) in _SHELL_BASENAMES:
            nested = _shell_command_string(resolved["command"])
            if nested is not None:
                if depth >= _MAX_WRAPPER_DEPTH:
                    raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                         f"shell strings nested deeper than {_MAX_WRAPPER_DEPTH}")
                launches_python = _scan_shell_string(nested, env, depth + 1) or launches_python
            continue
        if not _is_python_executable(target):
            continue
        launches_python = True
        flag = _forbidden_python_flag(resolved["command"])
        if flag is not None:
            raise _LaunchRefusal(LAUNCH_REASON_FLAGS, flag, executable=target)
        disarming = stripped or resolved["stripped"]
        if resolved["clears"] and disarming is None:
            disarming = "env -i"
        if disarming is not None:
            raise _LaunchRefusal(LAUNCH_REASON_ENV, disarming, executable=target)
    return launches_python


def _scan_launch(argv: list[str], env, guard: GuardedPathFinder) -> list[str]:
    """Return the argv to launch, re-armed if that is what the contract needs; raise to refuse.

    THE ORDER IS THE CHEAPEST CORRECT ONE. The wrapper prefixes are resolved first, because until
    they are there is no executable to ask questions about; a shell `-c` string is scanned next,
    because a shell is not a Python child and its string holds launches of its own; only a resolved
    PYTHON command is flag-scanned; and the environment question is asked LAST, after any argv
    repair, so a repaired launch is not refused for the state it was repaired out of.

    A non-Python child is not refused here. It inherits the re-armed contract AND the wrapper
    directory on `PATH`, which is what makes an ordinary interpreter it launches guarded; what
    remains is `DECLARED_GAP`.
    """
    resolved = _resolve_launch_command(argv, env)
    if resolved is None:
        return argv
    command = resolved["command"]
    target = _resolve_executable(command[0], env)
    text = (_shell_command_string(command)
            if _executable_basename(target) in _SHELL_BASENAMES else None)
    if text is not None:
        # A SHELL STRING IS NOT A PYTHON CHILD, BUT IT CAN HOLD ONE, and the wrapper prefix in
        # front of the SHELL is what would disarm it: `env -i bash -c 'python3 x.py'` clears the
        # environment outside the string, so the string itself is clean and the interpreter inside
        # it starts unguarded. The scan therefore reports whether an interpreter is in there, and
        # the contract checks below run for that case exactly as they do for a direct launch.
        if not _scan_shell_string(text, env):
            return argv
    elif _is_python_executable(target):
        flag = _forbidden_python_flag(command)
        if flag is not None:
            raise _LaunchRefusal(LAUNCH_REASON_FLAGS, flag, executable=target)
    else:
        return argv
    if resolved["clears"] or resolved["stripped"] is not None:
        disarming = resolved["stripped"] or "env -i"
        if resolved["inject_at"] is None:
            #: The command came out of an `env -S` STRING, so there is no argv position to insert
            #: the contract at. Refused rather than rewritten, for the reason on `_scan_shell_string`.
            raise _LaunchRefusal(LAUNCH_REASON_ENV, disarming, executable=target)
        operands, view = _contract_operands(resolved)
        missing = _environment_reaching_child_is_armed(view)
        if missing is not None:
            raise _LaunchRefusal(LAUNCH_REASON_ENV, missing, executable=target)
        guard.launch_env = "argv-re-armed"
        return [*argv[:resolved["inject_at"]], *operands, *argv[resolved["inject_at"]:]]
    missing = _environment_reaching_child_is_armed(env)
    if missing is not None:
        raise _LaunchRefusal(LAUNCH_REASON_ENV, missing, executable=target)
    return argv


def _prepare_launch(executable, arguments, env, guard: GuardedPathFinder):
    """Re-arm a launch, or refuse a Python child that could not install the guard.

    Returns `(environment, argv)`. The environment is re-armed FIRST so that the armed copy is what
    every later check reads, and the argv comes back possibly REWRITTEN -- see `_contract_operands`.
    A caller that ignores the returned argv would silently drop an argv-level repair, which is why
    every wrapped primitive below writes both back.
    """
    armed_env = _rearm_launch_environment(env, guard)
    argv = _launch_argv(arguments)
    try:
        return armed_env, _scan_launch(argv, armed_env, guard)
    except _LaunchRefusal as refusal:
        launched = getattr(refusal, "executable", None)
        refusal_record = {
            "executable": launched or _resolve_executable(executable, armed_env),
            "offending_flag": refusal.offending,
            "argv": argv,
            "reason": refusal.reason,
        }
        guard.launch_refusal = refusal_record
        _report_launch(refusal_record)
        raise SystemExit(VIOLATION_EXIT) from None


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
        armed_env, armed_argv = _prepare_launch(executable, argv, env, guard)
        if env is not None:
            bound.arguments["env"] = armed_env
        # AN ARGV-LEVEL REPAIR IS ONLY REAL IF IT IS WRITTEN BACK. `shell=True` is excluded because
        # its `argv` is one this wrapper SYNTHESIZED around the caller's string -- `_scan_launch`
        # refuses a string it would have had to rewrite, so it never returns a repaired one here --
        # and a `str` `args` names a program with no wrapper prefix to insert into.
        if not shell and armed_argv != argv and not isinstance(command, (str, bytes, os.PathLike)):
            bound.arguments["args"] = armed_argv
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
            armed_env, armed_argv = _prepare_launch(
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
            if armed_argv != _launch_argv(argv):
                if len(positional) > argv_index:
                    positional[argv_index] = armed_argv
                else:
                    call_kwargs[argv_parameter] = armed_argv
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
            armed_env, armed_argv = _prepare_launch(executable, argv, env, guard)
            if has_env:
                bound.arguments["args"] = (*armed_argv, armed_env)
            elif armed_argv != _launch_argv(argv):
                bound.arguments["args"] = tuple(armed_argv)
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
        # The argv is discarded deliberately: `os.system` takes a STRING, and `_scan_launch`
        # refuses a string it would have to rewrite rather than returning a repaired one.
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
            guard.path_shim, guard.path_shim_sha256 = _arm_child_environment(expect, allow_roots)
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
        # THE SECOND HALF OF THE PROCESS-BOUNDARY CONTRACT, as a state and never a boolean. `armed`
        # means a non-Python child's `python3 -I` is refused by the wrapper on PATH; anything else
        # names why it is not, and widens `declared_gap` below by exactly that much.
        "path_shim": (guard.path_shim if guard is not None else "not-armed"),
        "path_shim_dirs": [d for d in (os.environ.get(PATH_SHIM_DIRS_ENV) or "").split(os.pathsep)
                           if d],
        # The bytes the PATH half would execute. See `_path_shim_digests` for why this record is
        # what binds them rather than the A-2(f) source manifest.
        "path_shim_sha256": (guard.path_shim_sha256 if guard is not None
                             else _path_shim_digests()),
        # THE COVERAGE BOUNDARY IN THE RECORD ITSELF (P-3's rule applied to a GAP rather than to a
        # count): a ratchet reader consuming these records cannot open the module docstring, and a
        # boundary it cannot see is one it reads as absent. Written on every path, including the
        # ones with no guard, because a run that could not look has the widest boundary of all.
        "declared_gap": DECLARED_GAP,
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
            outcome, site = launch_outcome(guard.launch_refusal), SITE_LAUNCH
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
