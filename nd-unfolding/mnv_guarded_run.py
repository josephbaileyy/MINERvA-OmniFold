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

A GUARDED PROCESS MAY START ONLY A CHILD THIS GUARD CAN PROVE KEEPS ITS OWN PYTHON
LAUNCHES GUARDED. That is the whole launch contract, and it replaces the weaker one
round 6 broke. The weaker one was "scan Python launches and let every other child
inherit the wrapper directory on `PATH`" -- so a shell SCRIPT FILE was admitted
UNREAD, and the reviewer wrote three of them that resolve the interpreter without
consulting `PATH` at all (`command -p python3 -I ...`, a reordered
`PATH=/usr/bin:/bin python3 -I ...`, BSD `env -P /usr/bin:/bin python3 -I ...`).
All three exited 0, ran their sentinel, loaded the wrong tree, and wrote no child
record. `_scan_resolved_command` now CLASSIFIES the resolved command word and admits
exactly six things:

  1. a PYTHON interpreter -- by basename or by resolved path, under the startup-flag
     grammar and the environment contract. An interpreter named by an ABSOLUTE OR
     RELATIVE PATH goes through the SAME grammar, which is what retires the
     "absolute path" arm of the old declared gap: what guards a Python child is the
     shim on `PYTHONPATH`, not the wrapper on `PATH`, so there was never a reason to
     treat `/usr/bin/python3 -I` as beyond reach;
  2. a modelled SHELL -- `sh`, `bash`, `dash`, and `zsh` only behind `-f`/`--no-rcs`.
     A `-c` string is scanned as before AND A SCRIPT FILE OPERAND IS READ AND SCANNED
     WITH THE SAME SCANNER. A shell with no operand and no `-c` reads its program
     from stdin and is refused; so are `-l`/`--login`, `-i`, `-s`, `--rcfile`,
     `--init-file`, and any shell launch made with `$BASH_ENV` or `$ENV` set, because
     each of them runs a startup file this guard was never handed. `ksh`, `mksh`,
     `fish`, `csh` and `tcsh` are refused as unmodelled shells rather than treated as
     unknown binaries;
  3. `git`, on an allowlist of subcommands that cannot reach a hook, a pager, an
     external diff or a transport GIVEN THE ARGV ALONE -- plus a refusal when the
     child's environment carries `GIT_EXTERNAL_DIFF`, `GIT_SSH_COMMAND`, `GIT_PAGER`
     or any of the rest of `_GIT_EXTERNAL_PROGRAM_ENV_VARS`. `log`, `show` and `diff`
     require `--no-ext-diff` explicitly; `config` is admitted only in its four
     reading spellings;
  4. `sbatch`, modelled as a wrapper whose operand is a BATCH SCRIPT (read and
     scanned, `#SBATCH` lines being the comments they are) or a `--wrap` STRING.
     `srun` joins `nice`/`nohup`/`timeout`/`xargs` in the wrapper table. Both refuse
     `--export` anything other than `ALL`. `mpirun`/`mpiexec` are refused: two
     implementations, two grammars, and an app-file that names further commands;
  5. a LEAF TOOL -- a short committed list of programs that execs nothing their own
     arguments name -- admitted only when its executable was found in a named system
     prefix and carries NO shebang. A file called `ls` with `#!/bin/sh` in it is
     scanned as the script it is, never trusted by name;
  6. a FILE WITH A SHEBANG naming one of the above, which is how `./stage.sh` and a
     `#!/usr/bin/env python3` entrypoint are covered. A shebang's `-S`/`-I` is a
     refusal exactly as a command line's is.

Everything else is `LAUNCH_REASON_UNPROVEN`: `perl`, `make`, `ssh`, `find`, `awk`,
`sed`, `sudo`, `conda`, `uv run`, an unknown binary, a script whose shebang names
none of the six.

INSIDE A SHELL PROGRAM the same closure applies line by line, and two of round 6's
routes live here rather than at the argv. An assignment to `PATH`, `PYTHONPATH`,
`BASH_ENV`, `ENV`, `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES` or any `MNV_GUARD_*`
variable is refused WHEREVER IT APPEARS -- on its own line, `export`ed, `declare`d or
`unset` -- because it disarms every later line and not only the command it prefixes.
`eval`, `alias`, `unalias`, `hash -p`, `enable -f`, `command -p`, `exec -a`/`-l` and
`module load` are refused because each changes what a later word resolves to or
builds its program after this scan ends; `source`/`.` reads and scans its single
literal operand; `trap`'s handler string is scanned; a function body is scanned as
ordinary lines, which is what makes a later call to the name admissible; a command
substitution's INSIDE is scanned as a program of its own, and a substitution shaping
the argv of a shell, an interpreter, a wrapper or `source` is refused because the
argv that runs is then not the argv that was read. Here-document bodies are DATA and
are skipped, so `python3 - <<EOF` is scanned as the launch it is while its payload is
not read as commands.

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

THE WRAPPERS ARE KEPT AND THEY ARE NO LONGER THE COVERAGE ARGUMENT. They still stand
in front of every interpreter a child ADMITTED by the closure above resolves through
`PATH`, which is a second, independent chance to refuse; what they may no longer be
asked to do is carry the whole claim for a child nobody read. A run whose records say
`path_shim: not-armed` is now narrower by that second chance rather than open.

THE TWO DECLARED RESIDUALS, AFTER THE CLOSURE AND BOTH HALVES, ARE NEITHER OF THEM AN
UNSCANNED PYTHON LAUNCH. (1) TRUST BY LOCATION: a leaf tool or a read-only `git` is
admitted because its executable was found in a named system prefix and carries no
shebang, so a tampered system prefix -- or a repository-local `.git` configuration
naming an external program -- is outside this guard. (2) A COMMAND WORD BUILT AT RUN
TIME is REFUSED and not read, so the residual there is a refused launch and never an
unguarded one; the cost is a correct launcher that has to be respelled. Both are
written into EVERY inventory record as `declared_gap` so a ratchet reader sees the
coverage boundary without reading this file, and they are measured -- not asserted --
in `tests/test_mnv_guarded_run.py::TheSubprocessBoundaryIsCovered` and
`TheClosedChildModelRefusesWhatItCannotProve`, beside the covered counterparts they
must be distinguished from. Read `declared_gap` together with `path_shim`: when
`path_shim` is not `armed` the second chance above did not run.

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
         environment that strips the propagation contract, a launch prefix whose grammar
         this guard does not model and therefore CANNOT scan, or a child whose own launches
         it cannot PROVE stay guarded (fail-closed: unparsed and unproven are both refusals,
         never a pass)
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
#:
#: REWRITTEN FOR ROUND 6, AND NEITHER ARM IS AN UNSCANNED PYTHON LAUNCH ANY MORE. The predecessor
#: sentence named "an ABSOLUTE PATH with -S, -I or -E, or a cleared PATH or environment", and the
#: reviewer's finding was that it was BOTH incomplete and operationally fail-open: three shell
#: SCRIPT FILES reached the wrong-tree import by routes it did not describe, and the absolute-path
#: arm it did describe was a fully admitted run. Both are closed -- a path to an interpreter goes
#: through the same flag grammar as a bare name, and a shell's script file is read. What is left is
#: TRUST BY LOCATION and REFUSAL, and the second one is not a hole.
DECLARED_GAP = (
    "TWO RESIDUALS, AND NEITHER IS AN UNSCANNED PYTHON LAUNCH. (1) TRUST BY LOCATION: a leaf tool "
    "(ls, cat, mkdir, tar, sacct, ... -- see _LEAF_TOOL_BASENAMES) or a read-only `git` is admitted "
    "because its executable was found in a named system prefix (/bin, /usr/bin, /sbin, /usr/sbin, "
    "/usr/local/bin, /usr/local/sbin, /opt/homebrew/bin, /opt/local/bin, /opt/slurm/bin, "
    "/usr/global/bin) and carries no shebang; nothing about its behaviour is read. So a TAMPERED "
    "SYSTEM PREFIX, or a repository-local .git configuration naming an external program "
    "(diff.external, a hook, core.pager), is outside this guard: those are files rather than an "
    "argv, and the environment variables that do the same job (GIT_EXTERNAL_DIFF, GIT_SSH_COMMAND, "
    "GIT_PAGER, ...) are refused where they can be seen. (2) COMMAND WORDS BUILT AT RUN TIME: a "
    "shell script or -c string whose command word comes from a variable, a command substitution, a "
    "glob or tilde expansion is REFUSED and not read, so the residual for it is A REFUSED LAUNCH "
    "AND NEVER AN UNGUARDED ONE -- the cost is a correct launcher that must be respelled, not a "
    "wrong-tree import that runs")

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


#: WHY the launch was refused, as a field. Every refusal here is the same SITE (this wrapper owns one
#: launch boundary) and the same exit code, and the repo's own rule -- see the `SITE_*` block --
#: is that a reader must not have to parse which check fired out of prose.
LAUNCH_REASON_FLAGS = "python-startup-flags-bypass-the-shim"
LAUNCH_REASON_ENV = "the-launch-argv-or-environment-strips-the-propagation-contract"
LAUNCH_REASON_UNMODELLED = "a-launch-wrapper-option-this-guard-does-not-model"
LAUNCH_REASON_UNPARSED = "a-launch-argv-or-command-string-this-guard-cannot-parse"

#: ROUND 6's REASON, AND THE ONE THAT CHANGED THE MODEL RATHER THAN A TABLE. The four reasons above
#: all presuppose that a NON-PYTHON child is somebody else's problem: the old `_scan_launch` returned
#: the argv untouched for anything that was not an interpreter, and the PATH wrappers were the whole
#: of the coverage for what that child then launched. The reviewer walked through that with three
#: SHELL SCRIPT FILES -- `command -p python3 -I`, a reordered `PATH=/usr/bin:/bin python3 -I`, and
#: BSD `env -P /usr/bin:/bin python3 -I` -- each of which resolves the interpreter without consulting
#: the shim directory, and none of which the old declared gap described. A script file was admitted
#: UNREAD, so the coverage claim rested on a PATH lookup the script could simply decline to make.
#: The model is now the other way round: a guarded process may start only a child this guard can
#: PROVE keeps its Python launches guarded -- an interpreter under the flag grammar, a shell whose
#: string or SCRIPT FILE has been read, a leaf tool that execs nothing, a read-only `git`, or a file
#: whose shebang resolves to one of those. Everything else refuses with THIS reason.
LAUNCH_REASON_UNPROVEN = "a-child-this-guard-cannot-prove-keeps-its-launches-guarded"


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
    # `command -p` USES A DEFAULT PATH AND THEREFORE NOT OURS. It is one of the three routes round 6
    # drove through a shell script: the shim directory is on the inherited PATH, `-p` replaces that
    # PATH with the implementation's own, and the interpreter it then finds has no wrapper in front
    # of it. The child would still inherit the shim-first PYTHONPATH, so it is not certainly
    # unguarded -- but "probably still guarded" is not a claim this file makes, and the rule is that
    # a launch removing half the contract is refused rather than reasoned about.
    "command": {"flags": frozenset(), "values": frozenset(),
                "print_only": frozenset({"-v", "-V"}),
                "refusing": {"-p": LAUNCH_REASON_ENV}},
    # `-a` RENAMES argv[0] AND `-l` MAKES A LOGIN SHELL OF THE CHILD, and both were previously
    # followed rather than refused. `-a` is why: the scan reports on the executable it resolved
    # while the child sees a different argv[0], so a record naming `python3` would describe an
    # invocation nobody can find in a process list. `-l` runs the login startup files this guard
    # cannot read. `-c` clears the environment, which is the older refusal and keeps its ENV reason.
    "exec": {"flags": frozenset(), "values": frozenset(),
             "clearing": frozenset({"-c"}),
             "refusing": {"-a": LAUNCH_REASON_UNPROVEN, "-l": LAUNCH_REASON_UNPROVEN}},
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

#: Shells this guard MODELS: their option grammar is parsed, their `-c` string is scanned, and their
#: SCRIPT FILE OPERAND IS READ AND SCANNED WITH THE SAME SCANNER. `zsh` is modelled only behind
#: `-f`/`--no-rcs`, because without it zsh reads `.zshenv` even non-interactively -- a startup file
#: this guard cannot see, running before the script's first line.
_SHELL_BASENAMES = frozenset({"sh", "bash", "zsh", "dash"})

#: Shells that are RECOGNISED AS SHELLS AND REFUSED, which is not the same as being unknown. Their
#: option grammars and startup-file rules differ from the four above in ways this file does not
#: model, and the fail-closed rule is that a shell whose grammar is unmodelled cannot be read --
#: naming them keeps a reader from concluding that `csh` simply was not thought of.
_UNMODELLED_SHELL_BASENAMES = frozenset({"ksh", "ksh93", "mksh", "pdksh", "fish", "csh", "tcsh",
                                         "rc", "es", "xonsh", "elvish", "nu"})

#: `c` is in the set because a cluster is what carries it -- `bash -ec <string>` is the spelling a
#: launcher uses, and a table that listed every OTHER short flag but not `c` refused exactly the
#: invocations it was written to read (measured on `bash -c` itself).
_SHELL_FLAG_CHARS = "abcCefhklmnptuvxBDPT"
#: THE SHORT FLAGS THAT REFUSE, and each for a different reason a reader should not have to guess:
#: `-l` runs the login startup files, `-i` runs the interactive ones, and `-s` reads the program
#: from STDIN. In all three cases a program this guard cannot read runs before -- or instead of --
#: the one it was handed, so there is nothing to scan.
_SHELL_REFUSING_FLAG_CHARS = "ils"
_SHELL_VALUE_OPTIONS = frozenset({"-o", "+o", "-O", "+O"})
#: `--rcfile`/`--init-file` NAME A STARTUP FILE THIS GUARD DOES NOT READ, so they refuse rather than
#: consume their value. They were previously in `_SHELL_VALUE_OPTIONS`, which skipped the value and
#: left the startup file unexamined.
_SHELL_REFUSING_VALUE_OPTIONS = frozenset({"--rcfile", "--init-file"})
_SHELL_FLAG_LONG = frozenset({"--noprofile", "--norc", "--no-rcs", "--posix", "--noediting",
                              "--verbose", "--debugger", "--restricted"})
_SHELL_REFUSING_LONG = frozenset({"--login", "--interactive"})
#: The two spellings that make `zsh` skip `.zshenv` and the rest of its startup files.
_ZSH_NO_STARTUP_OPTIONS = frozenset({"-f", "--no-rcs"})

#: STARTUP-FILE VARIABLES: a non-interactive `bash` sources `$BASH_ENV` and a POSIX `sh` sources
#: `$ENV` BEFORE the script's first line. Whatever they name is a shell program this guard was never
#: handed and cannot read, so a shell launch made with either of them set in the CHILD's environment
#: is refused and the variable is named. This is checked against the environment the child will
#: actually receive, not against `os.environ`, because an explicit `env=` is what a launcher would
#: use to set it.
_SHELL_STARTUP_ENV_VARS = ("BASH_ENV", "ENV")

#: VARIABLES WHOSE ASSIGNMENT IS REFUSED WHEREVER IT APPEARS IN A SHELL PROGRAM, and not only in
#: front of an interpreter. THIS IS ROUND 6's SECOND ROUTE. `_breaks_propagation_contract` already
#: refused `PYTHONPATH=/nowhere python3 x.py`, where the assignment is that command's own
#: environment -- but `PATH=/usr/bin:/bin` ON ITS OWN LINE, or `export`ed, or `unset`, changes what
#: EVERY LATER LINE resolves and disarms an interpreter three lines further down that this scan would
#: otherwise pass. So the assignment itself refuses, whatever follows it.
_SHELL_PROTECTED_VARIABLES = frozenset({
    "PATH", "PYTHONPATH", "PYTHONHOME", "PYTHONSAFEPATH", "PYTHONNOUSERSITE", "PYTHONSTARTUP",
    "PYTHONEXECUTABLE", "LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "BASH_ENV", "ENV",
})
#: Every propagation and PATH-half variable, by PREFIX rather than by list: a variable this guard
#: has not invented yet is still one whose reassignment inside a script it cannot allow.
_GUARD_ENV_PREFIX = "MNV_GUARD_"

#: LEAF TOOLS: programs that do their work and exit, and do NOT exec another program named by their
#: own arguments. They are the reason the closed model is usable at all -- a guarded science step
#: that cannot `mkdir` is a guard nobody keeps -- and the list is deliberately SHORT, because every
#: name on it is a name whose behaviour this file is asserting without reading anything.
#:
#: WHAT IS DELIBERATELY NOT HERE, AND THIS HALF MATTERS MORE THAN THE LIST: `ssh`, `scp`, `rsync -e`,
#: `make`, `xargs` as a leaf, `find` (`-exec`), `perl`, `ruby`, `node`, `awk`, `sed` (`e` command),
#: `sudo`, `su`, `nohup` as a leaf, `time`, `watch`, `tmux`, `screen`, `sh` under another name. Each
#: of them runs a program its arguments name, so admitting it by basename would admit
#: `perl -e 'exec "python3","-I",...'` -- which is the reviewer's finding with a different spelling.
#: `xargs`, `nice`, `nohup`, `timeout`, `stdbuf`, `time`, `command` and `exec` stay in
#: `_WRAPPER_SPECS`, where their command word is RESOLVED and then scanned; they are wrappers, never
#: leaves.
_LEAF_TOOL_BASENAMES = frozenset({
    # coreutils and their BSD equivalents
    "ls", "cat", "cp", "mv", "mkdir", "rm", "rmdir", "touch", "head", "tail", "wc", "sort",
    "uniq", "cut", "tr", "tee", "date", "hostname", "uname", "id", "true", "false", "sleep",
    "stat", "readlink", "realpath", "basename", "dirname", "pwd", "printf", "echo", "which",
    # digests
    "sha256sum", "shasum", "md5sum",
    # archive tools: they extract and compress, they do not run what they extract
    "tar", "gzip", "gunzip", "zstd", "xz",
    # Slurm CLIENTS that submit or report and run nothing locally. `sbatch` and `srun` are NOT
    # here: `sbatch` runs a script and `srun` runs a command, so both are modelled as wrappers.
    "sacct", "squeue", "sinfo", "scancel", "sstat",
    # rsync ONLY without -e/--rsh/--rsync-path, checked in `_check_leaf_options`
    "rsync",
})

#: `rsync`'s three options that make it run a program of the caller's choosing on one end or the
#: other. Present -> the launch is not a leaf and is refused.
_RSYNC_REMOTE_SHELL_OPTIONS = ("-e", "--rsh", "--rsync-path")

#: WHERE A LEAF MAY LIVE. A leaf is admitted because of the DIRECTORY IT WAS FOUND IN, since nothing
#: else about `ls` is being checked -- so the trust is in the prefix, and that is exactly arm (1) of
#: `DECLARED_GAP`. `/usr/bin` already covers the Slurm clients on Perlmutter; `/opt/slurm/bin` and
#: `/usr/global/bin` are named because they are the two other places that site puts them, and a
#: prefix absent from a machine simply matches nothing.
_SYSTEM_EXECUTABLE_PREFIXES = (
    "/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin", "/usr/local/sbin",
    "/opt/homebrew/bin", "/opt/local/bin", "/opt/slurm/bin", "/usr/global/bin",
)

#: `git` SUBCOMMANDS THAT, GIVEN THE ARGV ALONE, CANNOT RUN A CONFIGURED EXTERNAL PROGRAM. This is
#: the one non-leaf tool with a subcommand allowlist, because the guarded code in this repository
#: reads git constantly -- HEAD, `ls-files`, `rev-parse HEAD:<path>`, `hash-object` -- and refusing
#: all of it would refuse the provenance checks the campaign is built on. What is excluded is
#: everything that can reach a hook, a pager, an external diff or a transport.
_GIT_READ_ONLY_SUBCOMMANDS = frozenset({
    "rev-parse", "ls-files", "ls-tree", "hash-object", "cat-file", "merge-base", "rev-list",
    "describe", "name-rev", "for-each-ref", "symbolic-ref", "check-ignore", "status",
    "diff-index", "diff-tree",
})
#: These three CAN run an external diff driver, so they are admitted only with `--no-ext-diff`
#: EXPLICITLY PRESENT. `-p` is the patch flag and is fine; `--ext-diff` re-enables what
#: `--no-ext-diff` disables and refuses.
_GIT_NO_EXT_DIFF_SUBCOMMANDS = frozenset({"log", "show", "diff"})
#: `git config` is admitted only in its four READING spellings. `git config user.name` is a read
#: too, but it is the same argv shape as a WRITE with one more operand, and a rule that has to
#: count operands to tell a read from a write is a rule that will one day miscount.
_GIT_CONFIG_READ_OPTIONS = frozenset({"--get", "--get-all", "--get-regexp", "--get-urlmatch",
                                      "--list", "-l"})
#: Global options accepted in front of the subcommand. `-C` and `--git-dir` only choose WHICH
#: repository, which changes nothing about what can run. `-c`, `--config-env`, `--exec-path` and
#: `--paginate` each install a configuration or a program for the subcommand to run, so they refuse.
_GIT_GLOBAL_VALUE_OPTIONS = frozenset({"-C", "--git-dir", "--work-tree", "--namespace"})
_GIT_GLOBAL_FLAG_OPTIONS = frozenset({"--no-pager", "--no-optional-locks", "--literal-pathspecs",
                                      "--no-replace-objects", "--bare", "--no-lazy-fetch"})

#: ENVIRONMENT VARIABLES THAT MAKE A READ-ONLY `git` RUN AN ARBITRARY PROGRAM. An allowlist over the
#: argv is worth nothing while any of these is set: `GIT_EXTERNAL_DIFF` alone turns `git diff-tree`
#: into a launcher. Checked against the environment the child will receive.
_GIT_EXTERNAL_PROGRAM_ENV_VARS = (
    "GIT_SSH", "GIT_SSH_COMMAND", "GIT_PAGER", "GIT_EDITOR", "GIT_SEQUENCE_EDITOR",
    "GIT_EXTERNAL_DIFF", "GIT_ASKPASS", "GIT_EXEC_PATH", "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM",
)

#: `sbatch`'s operand is a SCRIPT FILE (scanned with the same scanner, `#SBATCH` lines being
#: comments) or a `--wrap` STRING. Its option table is fail-closed for the reason on `_parse_env`:
#: an unmodelled option's VALUE may be the script name.
_SBATCH_FLAGS = frozenset({
    "-H", "--hold", "--parsable", "-Q", "--quiet", "-v", "--verbose", "--exclusive", "--requeue",
    "--no-requeue", "--wait", "-W", "--test-only", "--contiguous", "-O", "--overcommit",
    "--spread-job", "--use-min-nodes", "--ignore-pbs", "--kill-on-invalid-dep", "--no-kill",
    "-k", "--reboot", "--get-user-env", "--exclusive=user", "--gres-flags=enforce-binding",
})
_SBATCH_VALUES = frozenset({
    "-a", "--array", "-A", "--account", "-b", "--begin", "-c", "--cpus-per-task", "-C",
    "--constraint", "-d", "--dependency", "-D", "--chdir", "-e", "--error", "-J", "--job-name",
    "-L", "--licenses", "-m", "--distribution", "-M", "--clusters", "-n", "--ntasks", "-N",
    "--nodes", "-o", "--output", "-p", "--partition", "-q", "--qos", "-S", "--core-spec", "-t",
    "--time", "-w", "--nodelist", "-x", "--exclude", "--comment", "--cpu-freq", "--deadline",
    "--delay-boot", "--exclusive", "--export-file", "--gid", "--gpus", "--gpus-per-node",
    "--gpus-per-task", "--gpu-bind", "--gpu-freq", "--gres", "--hint", "--mail-type",
    "--mail-user", "--mem", "--mem-per-cpu", "--mem-per-gpu", "--mem-bind", "--mincpus",
    "--network", "--nice", "--ntasks-per-core", "--ntasks-per-node", "--ntasks-per-socket",
    "--ntasks-per-gpu", "--open-mode", "--power", "--priority", "--profile", "--propagate",
    "--reservation", "--signal", "--sockets-per-node", "--switches", "--thread-spec",
    "--threads-per-core", "--time-min", "--tmp", "--uid", "--wait-all-nodes", "--wckey",
    "--cores-per-socket", "--extra-node-info", "--container", "--prefer", "--tres-per-task",
})
#: `srun` is a WRAPPER over its command, not over a script. Same fail-closed table rule. It was
#: DELIBERATELY UNMODELLED before round 6, on the argument that a fail-closed parser would refuse
#: correct submissions -- true, and the price of leaving it unmodelled was that `srun <anything>`
#: was admitted unread, so the whole coverage claim for it rested on the PATH wrapper.
_SRUN_FLAGS = frozenset({
    "-Q", "--quiet", "-v", "--verbose", "--exclusive", "-O", "--overcommit", "-l", "--label",
    "-u", "--unbuffered", "-K", "--kill-on-bad-exit", "-k", "--no-kill", "-X", "--disable-status",
    "-Z", "--no-allocate", "--overlap", "--pty", "--contiguous", "--spread-job",
    "--use-min-nodes", "--multi-prog", "--test-only", "-i", "--interactive", "--exact",
    "--preserve-env", "-E", "--wait-all-nodes", "--het-group",
})
_SRUN_VALUES = frozenset({
    "-A", "--account", "-c", "--cpus-per-task", "-C", "--constraint", "-D", "--chdir", "-e",
    "--error", "-J", "--job-name", "-L", "--licenses", "-m", "--distribution", "-n", "--ntasks",
    "-N", "--nodes", "-o", "--output", "-p", "--partition", "-q", "--qos", "-r", "--relative",
    "-s", "--oversubscribe", "-S", "--core-spec", "-t", "--time", "-T", "--threads", "-w",
    "--nodelist", "-x", "--exclude", "--cpu-bind", "--cpu-freq", "--gpus", "--gpus-per-node",
    "--gpus-per-task", "--gpu-bind", "--gpu-freq", "--gres", "--hint", "--jobid", "--mem",
    "--mem-per-cpu", "--mem-per-gpu", "--mem-bind", "--mincpus", "--mpi", "--network", "--nice",
    "--ntasks-per-core", "--ntasks-per-node", "--ntasks-per-socket", "--ntasks-per-gpu",
    "--open-mode", "--power", "--prolog", "--epilog", "--profile", "--propagate", "--reservation",
    "--signal", "--sockets-per-node", "--switches", "--task-epilog", "--task-prolog",
    "--thread-spec", "--threads-per-core", "--time-min", "--tmp", "--tres-per-task", "--input",
    "-I", "--immediate", "--container", "--prefer", "--resv-ports", "--sockets-per-node",
})
#: `--export` on either client decides which of the caller's environment reaches the task, and
#: anything other than `ALL` drops the propagation contract, the shim-first `PYTHONPATH`, or both.
_EXPORT_OPTION_ALLOWED_VALUE = "ALL"

#: REGISTERED HERE AND NOT IN THE LITERAL ABOVE only because the tables it needs are defined after
#: it. `srun` is an ordinary entry in the wrapper table now, so the offset arithmetic, the `--`
#: handling and the fail-closed unmodelled-option rule are the ones every other wrapper already has.
_WRAPPER_SPECS["srun"] = {"flags": _SRUN_FLAGS, "values": _SRUN_VALUES, "export_option": True}

#: `mpirun`/`mpiexec` are REFUSED and not modelled. Two independent implementations (Open MPI and
#: MPICH) with different option grammars, and both accept an app-file whose contents name further
#: commands -- so a fail-closed table would be a table over a grammar that varies by installation.
_REFUSED_LAUNCHER_BASENAMES = frozenset({"mpirun", "mpiexec", "orterun", "prterun", "aprun",
                                         "ibrun", "jsrun", "lrun"})

#: Shell-string operator characters, CLASSIFIED BY SHAPE RATHER THAN ENUMERATED. A token made only
#: of these is an operator: one containing `<` or `>` is a redirection, whose TARGET must be dropped
#: with it, and anything else (`;`, `&&`, `||`, `|`, `&`, `(`, `)`, `{`, `}`, `;;`, `|&`) ends a
#: simple command. Enumerating the spellings instead was WRONG IN THE FAIL-OPEN DIRECTION and the
#: two measured escapes are why this is a character class: `python3 2>/dev/null -I x.py` tokenises
#: with a bare `2` that ended the flag scan before the `-I`, and bash's `&>` is a spelling no
#: redirection list I wrote contained. A leading file-descriptor digit is dropped with the operator
#: for the same reason.
_SHELL_PUNCTUATION = frozenset(";&|<>(){}")

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


_LAUNCH_HEADLINES = {
    LAUNCH_REASON_FLAGS: "PYTHON STARTUP FLAGS BYPASS THE IMPORT SHIM",
    LAUNCH_REASON_ENV: "THE CHILD WOULD START WITHOUT THE PROPAGATION CONTRACT",
    LAUNCH_REASON_UNMODELLED: "THIS LAUNCH PREFIX USES AN OPTION THIS GUARD DOES NOT MODEL",
    LAUNCH_REASON_UNPARSED: "THIS LAUNCH CANNOT BE PARSED, SO IT CANNOT BE SCANNED",
    LAUNCH_REASON_UNPROVEN: ("THIS CHILD CANNOT BE PROVEN TO KEEP ITS OWN PYTHON LAUNCHES "
                             "GUARDED"),
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
    LAUNCH_REASON_UNPROVEN: ("A guarded process may start only a child this guard can PROVE keeps "
                             "its Python launches guarded: an interpreter under the startup-flag "
                             "grammar, a shell whose -c string or SCRIPT FILE has been read and "
                             "scanned, a leaf tool that execs no other program and resolves under "
                             "a system prefix, a read-only `git`, or a file whose shebang is one "
                             "of those. Round 6 reached the wrong-tree import through a shell "
                             "SCRIPT FILE, which the previous model admitted UNREAD on the "
                             "strength of a PATH lookup the script declined to make. Route the "
                             "work through a shell script this guard can read, or through "
                             "mnv_guarded_run.py; do not widen the leaf table to make a launcher "
                             "pass."),
}


#: The `outcome` string each launch-refusal reason records. TWO OUTCOMES AND NOT FIVE: the pair that
#: refuses a launch this guard READ keeps the outcome downstream controls already name, and the ones
#: that refuse a launch whose coverage it COULD NOT ESTABLISH share the second, because those are the
#: two different claims a reader of a record has to be able to tell apart. The reason field carries
#: the finer detail. `LAUNCH_REASON_UNPROVEN` joins the second group deliberately: to a ratchet
#: reader "this guard could not establish that this launch stays guarded" is the SAME claim whether
#: the obstacle was an option it does not model or a child it cannot prove, and giving it a third
#: outcome would silently re-route every control that keys off the existing two.
LAUNCH_OUTCOMES = {
    LAUNCH_REASON_FLAGS: "refused:launch-python-startup-flags",
    LAUNCH_REASON_ENV: "refused:launch-python-startup-flags",
    LAUNCH_REASON_UNMODELLED: "refused:launch-unmodelled-launch-grammar",
    LAUNCH_REASON_UNPARSED: "refused:launch-unmodelled-launch-grammar",
    LAUNCH_REASON_UNPROVEN: "refused:launch-unmodelled-launch-grammar",
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
        #: OPTIONS THAT ARE MODELLED AND STILL REFUSED, which is a third state the first version of
        #: this table did not have. `command -p` and `exec -a`/`-l` are understood exactly -- that
        #: is why they refuse -- so reporting them as UNMODELLED would send a reader to add them to
        #: a table they are already in.
        refusing = spec.get("refusing", {})
        if token in refusing:
            raise _LaunchRefusal(refusing[token], token)
        if spec.get("export_option") and token.partition("=")[0] == "--export":
            #: `--export=ALL` is the only value that carries the caller's environment, and the
            #: contract lives in that environment. Anything else -- `NONE`, an explicit list, or a
            #: separate-word value this table would otherwise skip -- drops it.
            if token != f"--export={_EXPORT_OPTION_ALLOWED_VALUE}":
                raise _LaunchRefusal(LAUNCH_REASON_ENV, token)
            index += 1
            continue
        if spec.get("export_option") and token == "--export":
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


def _parse_shell_invocation(argv: list[str], env=None) -> dict:
    """What a shell launch will actually run: a `-c` STRING, or a SCRIPT FILE. Never nothing.

    ROUND 6's FIRST FINDING IS THE `None` THIS FUNCTION NO LONGER RETURNS. Its predecessor
    (`_shell_command_string`) answered "is there a `-c` string" and returned None for everything
    else -- and None meant ADMITTED, so `bash script.sh` ran a program this guard never opened. The
    old docstring said so out loud: "what that script does at ITS launch sites is the PATH
    wrapper's half of the contract". The reviewer then wrote three scripts that resolve the
    interpreter WITHOUT a PATH lookup, so no wrapper stood in front of any of them. The shell's
    operand is therefore read now, and every outcome of this parse is either a program to scan or a
    refusal:

      {"kind": "string", "text": ...}   -- `-c`: scan the string
      {"kind": "script", "path": ...}   -- a file operand: read it and scan it

    THE REFUSALS ARE ALL ONE SHAPE: a shell program would run that this guard was not handed.
    `-l`/`--login` and `-i`/`--interactive` run startup files; `--rcfile`/`--init-file` name one;
    `-s` and a bare invocation read the program from STDIN, which does not exist yet at scan time;
    `$BASH_ENV`/`$ENV` in the child's environment name one that runs before the script's first
    line; and `zsh` reads `.zshenv` unless `-f`/`--no-rcs` says otherwise.
    """
    basename = _executable_basename(_text_argument(argv[0]))
    source = os.environ if env is None else env
    for name in _SHELL_STARTUP_ENV_VARS:
        if source.get(name):
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"${name} names a shell startup file this guard cannot read")
    index = 1
    options_done = False
    suppresses_startup = False
    while index < len(argv):
        token = argv[index]
        if token == "--":
            options_done = True
            index += 1
            break
        if token == "-" or not token.startswith(("-", "+")):
            break
        if token in _ZSH_NO_STARTUP_OPTIONS:
            suppresses_startup = True
            index += 1
            continue
        if token in _SHELL_REFUSING_VALUE_OPTIONS or token in _SHELL_REFUSING_LONG:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, token)
        if token.startswith("--") and token.partition("=")[0] in _SHELL_REFUSING_VALUE_OPTIONS:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, token)
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
        refusing = [c for c in cluster if c in _SHELL_REFUSING_FLAG_CHARS]
        if refusing:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, f"{token} (-{refusing[0]})")
        if not set(cluster) <= set(_SHELL_FLAG_CHARS):
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        if "f" in cluster:
            suppresses_startup = True
        if "c" in cluster:
            if index + 1 >= len(argv):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{token} with no command string")
            if basename == "zsh" and not suppresses_startup:
                raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                     "zsh reads .zshenv unless -f/--no-rcs is given")
            return {"kind": "string", "text": argv[index + 1]}
        index += 1
    if basename == "zsh" and not suppresses_startup:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             "zsh reads .zshenv unless -f/--no-rcs is given")
    if index >= len(argv):
        #: A SHELL WITH NO OPERAND READS ITS PROGRAM FROM STDIN. `sh <<EOF ...` and
        #: `subprocess.run(["bash"], input=...)` are the two spellings, and in both the program
        #: does not exist as bytes this scan can reach -- the parent writes it after the fork.
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             "a shell with no -c string and no script operand reads its program "
                             "from stdin, which does not exist at scan time")
    operand = argv[index]
    if operand == "-" and not options_done:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             "`-` makes the shell read its program from stdin")
    return {"kind": "script", "path": operand}


def _shell_command_string(argv: list[str]) -> "str | None":
    """The `-c` COMMAND STRING in a shell invocation, or None when the operand is a SCRIPT FILE.

    ONE PARSE, TWO CALLERS, so a shell option cannot mean one thing here and another in the scan:
    this is `_parse_shell_invocation` with the script arm collapsed to None. Callers that need to
    know WHICH of the two a launch is -- and every caller that decides a verdict does -- use the
    parse directly; this spelling survives because the string is the only thing several call sites
    want and because `None` here now means "a script file, go and read it" rather than "admitted".
    """
    parsed = _parse_shell_invocation(argv)
    return parsed["text"] if parsed["kind"] == "string" else None


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


def _mask_quoted(text: str) -> str:
    """`text` with every character INSIDE quotes replaced by NUL, offsets preserved.

    A VIEW FOR SEARCHING, never for tokenising. Two searches below have to distinguish shell syntax
    from data that happens to look like it -- `echo "a << b"` is not a here-document, and `'$(x)'`
    is not a command substitution -- and a regex over the raw line gets both wrong in the direction
    that DROPS LINES from the scan. Offsets are preserved so a match's position is a position in
    the real line.
    """
    out = []
    quote: "str | None" = None
    index = 0
    while index < len(text):
        character = text[index]
        if quote is None and character == "\\" and index + 1 < len(text):
            out.append("\0\0")
            index += 2
            continue
        if quote is not None:
            if character == "\\" and quote == '"' and index + 1 < len(text):
                out.append("\0\0")
                index += 2
                continue
            out.append("\0" if character != quote else character)
            if character == quote:
                quote = None
            index += 1
            continue
        if character in "\"'":
            quote = character
            out.append(character)
            index += 1
            continue
        out.append(character)
        index += 1
    return "".join(out)


#: A word-initial `#` starts a comment; one inside a word (`file#1`) does not. These are the
#: characters after which a `#` is word-initial, plus the start of a line.
_SHELL_WORD_BREAK = frozenset(" \t;&|<>(){}")


def _shell_logical_lines(text: str) -> list[str]:
    """A shell program as LOGICAL LINES: continuations joined, comments stripped, quotes intact.

    THIS IS WHAT MAKES A SCRIPT FILE SCANNABLE BY THE SAME CODE AS A `-c` STRING, and each of the
    three transformations is here because the alternative is a wrong answer rather than an untidy
    one:

      * A `\\`-newline continuation joined here means `python3 \\<newline>  -I x.py` is ONE command
        with an `-I` in it. Left alone, the two halves are two logical lines and the second reads as
        a command called `-I`. This repository has the receipt for the same class of error in the
        other direction: on 2026-08-18 a hook inserted between a continued command's lines
        truncated it to a launch with no arguments, and `bash -n` passed.
      * A comment stripped here is what makes `#!/bin/bash` and every `#SBATCH` line inert. They
        must be inert rather than skipped by pattern, because `#SBATCH --wrap=...` would otherwise
        tokenise into a command; and the shebang is checked separately, by `_read_shebang`, where
        the interpreter it names is the question.
      * Quotes are kept, because the tokeniser below needs them and because a newline inside quotes
        is DATA and not a command separator (`_unquoted_lines`' measured finding).

    An unbalanced quote raises, and the caller turns that into a refusal: a program this cannot
    split is a program nothing can scan.
    """
    lines: list[str] = []
    current: list[str] = []
    quote: "str | None" = None
    at_word_start = True
    index = 0
    length = len(text)
    while index < length:
        character = text[index]
        if quote is None and character == "\\":
            following = text[index + 1] if index + 1 < length else ""
            if following == "\n":
                index += 2                   # a line continuation: both characters disappear
                at_word_start = False
                continue
            current.append(character)
            if following:
                current.append(following)
                index += 2
            else:
                index += 1
            at_word_start = False
            continue
        if quote is not None:
            if character == "\\" and quote == '"' and index + 1 < length:
                current.append(character)
                current.append(text[index + 1])
                index += 2
                continue
            current.append(character)
            if character == quote:
                quote = None
            index += 1
            continue
        if character in "\"'":
            quote = character
            current.append(character)
            at_word_start = False
            index += 1
            continue
        if character == "#" and at_word_start:
            while index < length and text[index] != "\n":
                index += 1
            continue
        if character == "\n":
            lines.append("".join(current))
            current = []
            at_word_start = True
            index += 1
            continue
        current.append(character)
        at_word_start = character in _SHELL_WORD_BREAK
        index += 1
    if quote is not None:
        raise ValueError(f"no closing quotation in {text!r}")
    lines.append("".join(current))
    return lines


#: `<<WORD`, `<<-WORD`, `<<'WORD'`, `<<"WORD"`. `<<<` (bash's here-STRING) deliberately does not
#: match: its data is on the same line, and the tokeniser already drops it with its redirection.
_HEREDOC_RE = re.compile(r"<<-?[ \t]*(?:'([^']*)'|\"([^\"]*)\"|([A-Za-z_][A-Za-z0-9_]*))")


def _drop_heredoc_bodies(lines: list[str]) -> list[str]:
    """Remove here-document BODIES, keeping the line that opens them.

    A HERE-DOCUMENT BODY IS DATA, AND SCANNING IT AS COMMANDS IS WRONG IN BOTH DIRECTIONS. In the
    noisy direction, `python3 - <<EOF` followed by a program that says `import x` would have those
    lines read as commands called `import`, and every one of them would refuse as an unprovable
    child -- a guard that refuses a correct launch is a guard that gets removed. In the quiet
    direction, a body line that happened to tokenise cleanly would make the scan report on a
    command that never runs.

    The OPENING line is kept: `python3 - <<EOF` is a real Python launch and the interpreter word is
    on it. `sh <<EOF` is a real shell launch with no operand, which `_parse_shell_invocation`
    refuses -- the body being data is exactly why it cannot be scanned.

    An unterminated body runs to end of input, which is what a shell does with it too, so the
    remaining lines are consumed rather than refused.
    """
    kept: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        kept.append(line)
        for quoted, double_quoted, bare in _HEREDOC_RE.findall(_mask_quoted(line)):
            terminator = quoted or double_quoted or bare
            while index < len(lines):
                candidate = lines[index]
                index += 1
                if candidate.strip() == terminator:
                    break
    return kept


#: What a command substitution collapses to before tokenising. It CONTAINS A `$` on purpose: a
#: substitution standing where the command word goes is then refused by the same rule that refuses
#: every other command word built at runtime, rather than by a rule of its own.
_SUBSTITUTION_PLACEHOLDER = "$MNV_GUARD_COMMAND_SUBSTITUTION"


def _mask_command_substitutions(line: str) -> "tuple[str, list[str]]":
    """Replace `$(...)` and backticks with one placeholder word; return the masked line and INSIDES.

    TWO PROBLEMS, ONE PASS. Tokenising `python3 $(which x)` with `punctuation_chars=True` splits at
    the substitution's own parentheses, so the simple command breaks in half and the scan reports
    on fragments; and the text inside the substitution IS A COMMAND that runs, so dropping it would
    admit `X=$(python3 -I x.py)` unread. Masking fixes the first and returning the insides lets the
    caller scan them as programs of their own, which is the same rule applied one level down rather
    than a second rule.

    Single quotes protect their contents (`'$(x)'` is a literal); double quotes do NOT, because a
    substitution inside them still runs.
    """
    out: list[str] = []
    insides: list[str] = []
    quote: "str | None" = None
    index = 0
    length = len(line)
    while index < length:
        character = line[index]
        if quote != "'" and character == "\\" and index + 1 < length:
            out.append(character)
            out.append(line[index + 1])
            index += 2
            continue
        if quote == "'":
            out.append(character)
            if character == "'":
                quote = None
            index += 1
            continue
        if character == "'" and quote is None:
            quote = "'"
            out.append(character)
            index += 1
            continue
        if character == '"':
            quote = None if quote == '"' else '"'
            out.append(character)
            index += 1
            continue
        if character == "`":
            end = index + 1
            while end < length and line[end] != "`":
                end += 2 if line[end] == "\\" else 1
            insides.append(line[index + 1:min(end, length)])
            out.append(_SUBSTITUTION_PLACEHOLDER)
            index = end + 1
            continue
        if character == "$" and index + 1 < length and line[index + 1] == "(":
            if index + 2 < length and line[index + 2] == "(":
                #: `$((...))` is ARITHMETIC, not a substitution: it runs no command. Its inner
                #: parentheses would still break the tokeniser, so it is masked and NOT scanned.
                depth = 0
                end = index + 1
                while end < length:
                    if line[end] == "(":
                        depth += 1
                    elif line[end] == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    end += 1
                out.append("0")
                index = end + 1
                continue
            depth = 0
            end = index + 1
            while end < length:
                if line[end] == "(":
                    depth += 1
                elif line[end] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                end += 1
            insides.append(line[index + 2:min(end, length)])
            out.append(_SUBSTITUTION_PLACEHOLDER)
            index = end + 1
            continue
        out.append(character)
        index += 1
    return "".join(out), insides


#: `name()`, `name ()` and `function name` -- the three spellings of a function definition. The
#: BODY is not special-cased: it is ordinary lines, so the scan reads it like any other, and that is
#: what makes a later CALL to the name admissible.
_FUNCTION_DEFINITION_RE = re.compile(
    r"^[ \t]*(?:function[ \t]+([A-Za-z_][A-Za-z0-9_:.-]*)[ \t]*(?:\([ \t]*\))?"
    r"|([A-Za-z_][A-Za-z0-9_:.-]*)[ \t]*\([ \t]*\))[ \t]*")


def _strip_function_definitions(lines: list[str]) -> "tuple[set[str], list[str]]":
    """Every function NAME defined in this program, and the lines with the `name()` prefix removed.

    THE PREFIX HAS TO GO OR THE DEFINITION READS AS A CALL. `mnv_inv() {` tokenises to
    `['mnv_inv', '(', ')', '{']`, the parentheses split the simple command, and what is left is a
    one-word command `mnv_inv` -- an unknown word, refused, on the line that DEFINES it. Stripping
    the prefix leaves the body, which is scanned as ordinary lines.

    THE NAMES ARE COLLECTED IN A PRE-PASS so that a call appearing before the textual definition is
    still admissible. That is more permissive than the shell (which would fail on it) and it is the
    safe direction: the body was scanned either way, so admitting the call adds nothing unscanned.
    """
    defined: set[str] = set()
    rewritten: list[str] = []
    for line in lines:
        match = _FUNCTION_DEFINITION_RE.match(line)
        if match:
            defined.add(match.group(1) or match.group(2))
            line = line[match.end():]
        rewritten.append(line)
    return defined, rewritten


def _tokenise_shell_line(line: str) -> list[str]:
    """One logical line, tokenised with shell punctuation kept as operator tokens."""
    lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)                       # ValueError here is the caller's refusal


def _split_simple_commands(tokens: list[str]) -> list[list[str]]:
    """Split one line's tokens at every operator, dropping redirections with their targets."""
    commands: list[list[str]] = []
    current: list[str] = []
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            continue
        if token and set(token) <= _SHELL_PUNCTUATION:
            if "<" in token or ">" in token:
                if current and current[-1].isdigit():
                    current.pop()            # the file descriptor belongs to the redirection
                skip_next = True             # drop the operator AND its target
                continue
            if current:
                commands.append(current)
            current = []
            continue
        current.append(token)
    if current:
        commands.append(current)
    return commands


def _simple_commands(text: str) -> list[list[str]]:
    """Every SIMPLE COMMAND in a shell program, tokenised, redirections removed.

    Split at `;`, `&&`, `||`, `|`, `&`, subshell parentheses and unquoted newlines, because each of
    those starts a command whose first word is an executable -- and a Python interpreter behind any
    of them is a launch this guard owns. Redirection operators take their target with them so that
    a redirection cannot end the startup-flag scan early. Line continuations, comments and
    here-document bodies are handled by `_shell_logical_lines` and `_drop_heredoc_bodies` first, so
    a `-c` string and a SCRIPT FILE reduce to the same thing before either is scanned.
    """
    commands: list[list[str]] = []
    for line in _drop_heredoc_bodies(_shell_logical_lines(text)):
        commands.extend(_split_simple_commands(_tokenise_shell_line(line)))
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
    What is lost is the PATH-wrapper half for that child's own descendants -- the SECOND chance to
    refuse, not the coverage: the closed child model reads what the child will run before it starts,
    so a cleared PATH costs redundancy rather than opening a route. This was the
    `clears PATH or the environment` arm of the pre-round-6 `DECLARED_GAP`, and it is no longer one.

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


def _locate_executable(executable, env=None) -> str:
    """Where a launch will FIND its executable, WITHOUT resolving symlinks.

    `_resolve_executable` answers "which file runs", which is the right question for "is this
    Python". This answers "which directory was it found in", which is the question a leaf tool is
    admitted by -- and the two differ exactly where it matters: `/usr/local/bin/gzip` is commonly a
    symlink into a versioned cellar outside every system prefix, so resolving first would refuse a
    correct `gzip` while a symlink PLANTED in `/usr/local/bin` is admitted either way. The trust is
    therefore in the lookup directory, and saying so is arm (1) of `DECLARED_GAP` rather than a
    footnote.
    """
    text = _text_argument(executable)
    path_value = None if env is None else env.get("PATH")
    if isinstance(path_value, bytes):
        path_value = os.fsdecode(path_value)
    return shutil.which(text, path=path_value) or text


def _locate_command_word(word: str, env, context: "_ScanContext") -> str:
    """Where a command word will be FOUND, honouring the launch's working directory.

    MEASURED, NOT ANTICIPATED: `subprocess.run(["./stage.sh"], cwd=<dir>)` from a guarded parent
    resolved `./stage.sh` against THIS process's cwd, found nothing, and refused the launch for
    having no readable shebang -- a refusal that is fail-closed and also about the wrong file, which
    is the class of error where a check is right about an object nobody asked about. A word with a
    separator in it is a PATH and is resolved against the launch's cwd (and then the directory of
    the script being scanned, for the reason on `_resolve_shell_operand`); a bare word is a PATH
    lookup and `_locate_executable` owns it.
    """
    if os.sep in word and not os.path.isabs(word):
        for base in (context.cwd, context.script_dir):
            if not base:
                continue
            candidate = os.path.join(base, word)
            if os.path.exists(candidate):
                return candidate
    return _locate_executable(word, env)


def _read_shebang(path: str) -> "list[str] | None":
    """The `#!` line of `path`, split into words, or None when there is no readable shebang.

    None means "this is not a text program", which for a LEAF is the state that lets it be trusted
    by location and for anything else is a refusal. `shlex` splits the line because macOS passes
    the whole tail of a shebang as separate arguments and a `#!/usr/bin/python3 -I` there is an
    isolating launch; Linux passes it as one argument, which splits to the same words.
    """
    try:
        with open(path, "rb") as handle:
            if handle.read(2) != b"#!":
                return None
            line = handle.readline(4096)
    except OSError:
        return None
    try:
        text = line.decode("utf-8", "replace").strip()
        return shlex.split(text, posix=True)
    except ValueError:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"the shebang of {path} cannot be tokenised") from None


def _under_a_system_prefix(located: str) -> bool:
    """Whether `located`'s DIRECTORY is one of the named system executable prefixes."""
    try:
        directory = os.path.dirname(os.path.abspath(located))
    except OSError:
        return False
    return directory in _SYSTEM_EXECUTABLE_PREFIXES


def _check_leaf(command: list[str], located: str, target: str) -> None:
    """Admit a leaf tool, or refuse it. Called only when the file has NO shebang.

    A LEAF IS THE ONE THING HERE ADMITTED WITHOUT READING ANYTHING, so what is checked is where it
    lives and what it is:

      * it must be a regular executable file found in a system prefix -- a name that resolves to
        nothing, or to something under `$HOME`, is not the tool whose behaviour this table asserts.
        `$HOME/bin` in front of `/usr/bin` is not hypothetical here: OI-179 defect 1 is a `mkdir`
        on 2026-08-26 satisfying a conditional in `/etc/profile:171`, with no edit to any tracked
        file, so a table keyed on basename alone would have been a menu;
      * `rsync` must carry none of `-e`/`--rsh`/`--rsync-path`, each of which makes it run a
        program the caller names.

    THE SHEBANG CASE IS NOT A REFUSAL AND IS NOT HANDLED HERE. A file named `ls` with `#!/bin/sh` in
    it is a SCRIPT, and the caller falls through to the shebang path so it is READ AND SCANNED --
    which is strictly better than refusing it, because a shell script named after a leaf is a
    perfectly ordinary thing for a site to install and its contents are readable.
    """
    if not _under_a_system_prefix(located):
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{command[0]} resolved to {located}, which is not in a system "
                             f"prefix ({', '.join(_SYSTEM_EXECUTABLE_PREFIXES)})",
                             executable=target)
    if not os.path.isfile(target) or not os.access(target, os.X_OK):
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{command[0]} is not a regular executable file at {target}",
                             executable=target)
    if _executable_basename(_text_argument(command[0])) == "rsync":
        for option in _RSYNC_REMOTE_SHELL_OPTIONS:
            for argument in command[1:]:
                if argument == option or argument.startswith(f"{option}="):
                    raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, argument, executable=target)


def _scan_git(command: list[str], env, target: str) -> None:
    """Admit a READ-ONLY `git`, or refuse it. Argv allowlist AND environment, because either alone
    is worth nothing.

    WHY `git` HAS AN ALLOWLIST WHEN NOTHING ELSE DOES. This repository's guarded code reads git on
    every provenance path -- `rev-parse HEAD`, `ls-files`, `rev-parse HEAD:<path>`, `hash-object`,
    `status --porcelain` -- and refusing all of it would refuse the checks the campaign's evidence
    rests on. So the subcommands that cannot reach a hook, a pager, an external diff or a transport
    GIVEN THE ARGV ALONE are admitted by name.

    "GIVEN THE ARGV ALONE" IS THE LOAD-BEARING QUALIFIER AND THE REASON THE ENVIRONMENT IS CHECKED
    FIRST. `GIT_EXTERNAL_DIFF` turns `git diff-tree` into a launcher of an arbitrary program, and
    `GIT_SSH_COMMAND` does the same for anything that touches a remote -- so an allowlist over the
    argv with either of those set would be an allowlist over half the input. What remains, and is
    declared in `DECLARED_GAP` rather than covered, is a repository-local `.git/config` that names
    an external program: it is a file, not an argv, and it is trusted the same way a system prefix
    is.
    """
    source = os.environ if env is None else env
    for name in _GIT_EXTERNAL_PROGRAM_ENV_VARS:
        if source.get(name):
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"${name} makes git run a program of the caller's choosing",
                                 executable=target)
    index = 1
    while index < len(command):
        token = command[index]
        if token == "--":
            index += 1
            break
        if not token.startswith("-"):
            break
        if token in _GIT_GLOBAL_VALUE_OPTIONS:
            if index + 1 >= len(command):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"git {token} with no value",
                                     executable=target)
            index += 2
            continue
        if token.partition("=")[0] in _GIT_GLOBAL_VALUE_OPTIONS and "=" in token:
            index += 1
            continue
        if token in _GIT_GLOBAL_FLAG_OPTIONS:
            index += 1
            continue
        #: `-c`, `--config-env`, `--exec-path`, `--paginate` and everything not named above: each
        #: installs configuration or a program for the subcommand to run. `-c alias.x='!python3 -I'`
        #: is the whole allowlist defeated in one token.
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, f"git global option {token}",
                             executable=target)
    if index >= len(command):
        return                               # `git` with no subcommand prints usage
    subcommand = command[index]
    rest = command[index + 1:]
    if subcommand in _GIT_READ_ONLY_SUBCOMMANDS:
        return
    if subcommand in _GIT_NO_EXT_DIFF_SUBCOMMANDS:
        if "--no-ext-diff" not in rest:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"git {subcommand} without --no-ext-diff can run the configured "
                                 f"diff.external program",
                                 executable=target)
        if "--ext-diff" in rest or "--paginate" in rest:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, f"git {subcommand} with --ext-diff or "
                                 f"--paginate", executable=target)
        return
    if subcommand == "worktree" and rest[:1] == ["list"]:
        return
    if subcommand in ("branch", "tag") and "--list" in rest:
        return
    if subcommand == "remote" and rest in ([], ["-v"], ["--verbose"]):
        return
    if subcommand == "config" and any(o in rest or
                                      any(a.startswith(f"{o}=") for a in rest)
                                      for o in _GIT_CONFIG_READ_OPTIONS):
        return
    raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, f"git {subcommand}", executable=target)


class _ScanContext:
    """The state a scan carries across nesting: where it is, how deep, and what it has read.

    `defined` and `seen` are SHARED DOWNWARDS AND NOT COPIED, deliberately. A function defined in a
    sourced file is callable in the file that sourced it, so the names have to travel; and `seen` is
    what makes `a.sh` sourcing `b.sh` sourcing `a.sh` a refusal instead of a hang.
    """

    __slots__ = ("cwd", "depth", "defined", "seen", "script_dir")

    def __init__(self, cwd: str, depth: int = 0, defined=None, seen=None, script_dir=None):
        self.cwd = cwd
        self.depth = depth
        self.defined: set[str] = set() if defined is None else defined
        self.seen: set[str] = set() if seen is None else seen
        self.script_dir = script_dir

    def deeper(self, script_dir=None) -> "_ScanContext":
        if self.depth >= _MAX_WRAPPER_DEPTH:
            raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                 f"shell programs nested deeper than {_MAX_WRAPPER_DEPTH}")
        return _ScanContext(self.cwd, self.depth + 1, self.defined, self.seen,
                            script_dir if script_dir is not None else self.script_dir)


#: Shell builtins and reserved words that RUN NO PROGRAM NAMED BY THEIR ARGUMENTS. They are listed
#: rather than pattern-matched because each one that is missing refuses a correct script and each one
#: wrongly present admits an unscanned launch. `eval`, `exec`, `source`, `.`, `command`, `alias`,
#: `hash`, `trap`, `export`, `unset`, `declare`, `typeset` and `readonly` are NOT here: every one of
#: them either runs something or changes what a later name resolves to, and each has its own handler.
_SHELL_INERT_BUILTINS = frozenset({
    ":", "true", "false", "cd", "pwd", "pushd", "popd", "dirs", "echo", "printf", "read", "set",
    "shopt", "shift", "unalias_placeholder", "umask", "ulimit", "wait", "sleep_placeholder",
    "return", "break", "continue", "exit", "logout", "let", "test", "[", "[[", "getopts", "jobs",
    "fg", "bg", "kill", "disown", "suspend", "times", "type", "help", "history", "bind",
    "complete", "compgen", "compopt", "caller", "mapfile", "readarray", "local", "wait", "trap_p",
})

#: Reserved words in COMMAND POSITION that are followed by another command. Each is stripped and the
#: rest of the simple command re-dispatched -- and the reason is a measured fail-open shape: `if [ -f
#: x ]; then python3 -I y.py; fi` tokenises so that `then` is the first word of a simple command and
#: `python3 -I y.py` are its ARGUMENTS, which no flag scan would ever look at.
_SHELL_COMMAND_PREFIX_WORDS = frozenset({"if", "then", "elif", "else", "do", "!", "while",
                                         "until", "{", "}", "coproc"})
#: Reserved words that END a construct and command nothing.
_SHELL_TERMINATOR_WORDS = frozenset({"fi", "done", "esac", ";;", ";&", ";;&", "]]", "]"})
#: `for NAME in WORD ...` and `select NAME in WORD ...`: the words are DATA, so the whole simple
#: command is skipped rather than dispatched on `for`.
_SHELL_ITERATION_WORDS = frozenset({"for", "select"})

#: Environment-manipulating builtins whose operands are examined for a protected assignment.
_SHELL_DECLARING_BUILTINS = frozenset({"export", "declare", "typeset", "readonly", "local"})

#: Tools that relaunch an interpreter through machinery of their own -- a new `PATH`, a new
#: `PYTHONPATH`, a shim of their own, or a resolved virtualenv. Each is refused because the
#: interpreter it eventually runs is chosen by state this scan cannot see.
_INTERPRETER_MANAGER_BASENAMES = frozenset({"conda", "mamba", "micromamba", "pyenv", "pipenv",
                                            "poetry", "uv", "uvx", "virtualenv", "pipx", "hatch",
                                            "pdm", "rye", "activate"})

#: `module` is a shell FUNCTION on every cluster that has it, and it edits `PATH` and `PYTHONPATH`.
#: `list` is the only subcommand that reports instead of editing, so it is the only one admitted.
_MODULE_READ_ONLY_SUBCOMMANDS = frozenset({"list"})


def _is_protected_shell_variable(name: str) -> bool:
    """Whether assigning or unsetting `name` inside a shell program disarms a later launch."""
    return name in _SHELL_PROTECTED_VARIABLES or name.startswith(_GUARD_ENV_PREFIX)


def _refuse_a_word_built_at_runtime(word: str, role: str) -> None:
    """Refuse a command word, `source` operand or interpreter path this scan cannot READ.

    THE WORD IS THE ANSWER, so a word assembled at run time means there is no answer. `$PY x.py`,
    `` `which python3` x.py ``, `~/bin/python3 x.py` and `./py*/python3 x.py` each name a file whose
    identity is decided after this scan ends, and every one of them is a spelling of the launch the
    guard exists to see. This is where arm (2) of `DECLARED_GAP` comes from: the residual for such a
    script is REFUSED, never an unguarded run.

    `[` and `[[` are exempt: they are the test builtin, and their name simply contains a glob
    character.
    """
    if word in ("[", "[["):
        return
    for character in "$`*?":
        if character in word:
            raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                 f"the {role} {word!r} is built at run time ({character!r})")
    if word.startswith("~"):
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"the {role} {word!r} depends on tilde expansion")
    if "[" in word or "]" in word:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"the {role} {word!r} is a glob pattern")


def _read_shell_script(path: str) -> str:
    """The text of a shell script, or a refusal. An unreadable program cannot be a scanned one."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError as err:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"the shell script {path} cannot be read ({err.strerror}), so its "
                             f"launches cannot be scanned") from None


def _scan_shell_script_file(path: str, env, context: _ScanContext) -> bool:
    """Read a shell SCRIPT FILE and scan it with the same scanner a `-c` string gets.

    THE WHOLE OF ROUND 6's FIRST FINDING IS THAT THIS FUNCTION DID NOT EXIST. `bash script.sh` was
    admitted unread; the three mutations the reviewer wrote were ordinary shell lines in an ordinary
    file. Nothing about a file makes it less scannable than a string -- `_shell_logical_lines`
    reduces both to the same logical lines, with `#!` and `#SBATCH` inert as the comments they are.

    A CYCLE IS A REFUSAL, not a recursion limit reached the slow way: `a.sh` sourcing `b.sh`
    sourcing `a.sh` is a program whose text this scan cannot enumerate.
    """
    resolved = os.path.abspath(path)
    if resolved in context.seen:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"the shell script {resolved} is reached from itself; a cyclic "
                             f"program cannot be read to the end")
    context.seen.add(resolved)
    inner = context.deeper(script_dir=os.path.dirname(resolved))
    return _scan_shell_program(_read_shell_script(resolved), env, inner)


def _resolve_shell_operand(word: str, context: _ScanContext) -> str:
    """A shell operand's path, resolved against the launch cwd and then the script's directory.

    TWO CANDIDATES, AND SEARCHING BOTH IS THE FAIL-CLOSED DIRECTION. `source ./setup.sh` resolves
    against the shell's working directory, which is the `cwd=` of the launch when one was given and
    this process's otherwise; but a launcher `cd`s, and this scan does not execute the `cd`. Looking
    in the script's own directory as well means the file gets READ AND SCANNED in the case where the
    first candidate misses -- scanning more files is never the direction that admits something
    unscanned. When neither exists the caller refuses, because an operand naming no readable file is
    a program this guard cannot see.
    """
    if os.path.isabs(word):
        return word
    first = os.path.join(context.cwd, word)
    if os.path.exists(first):
        return first
    if context.script_dir:
        second = os.path.join(context.script_dir, word)
        if os.path.exists(second):
            return second
    return first


def _scan_sbatch(command: list[str], env, context: _ScanContext, target: str) -> bool:
    """`sbatch`: its operand is a SCRIPT FILE to scan, or a `--wrap` STRING to scan.

    MODELLED AS A WRAPPER OVER A SCRIPT AND NOT AS A LEAF, because that is what it is: everything
    the batch script launches runs later, on a compute node, out of reach of this interpreter and of
    the PATH wrappers. So the script is read now or the submission is refused now. `#SBATCH` lines
    inside it are comments and `_shell_logical_lines` already treats them as such -- they are
    directives to Slurm, never commands.

    `--export` MUST BE `ALL` OR ABSENT: any other value decides which of the submitter's
    environment reaches the task, and the propagation contract lives in that environment.
    """
    index = 1
    positional: "str | None" = None
    while index < len(command):
        token = command[index]
        if token == "--":
            index += 1
            break
        if not token.startswith("-") or token == "-":
            positional = token
            break
        name = token.partition("=")[0]
        if name == "--export":
            if token != f"--export={_EXPORT_OPTION_ALLOWED_VALUE}":
                raise _LaunchRefusal(LAUNCH_REASON_ENV, token, executable=target)
            index += 1
            continue
        if name == "--wrap":
            if "=" in token:
                return _scan_shell_program(token.partition("=")[2], env, context.deeper())
            if index + 1 >= len(command):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, "sbatch --wrap with no value",
                                     executable=target)
            return _scan_shell_program(command[index + 1], env, context.deeper())
        if token in _SBATCH_FLAGS:
            index += 1
            continue
        if "=" in token and name in _SBATCH_VALUES | _SBATCH_FLAGS:
            index += 1
            continue
        if token in _SBATCH_VALUES:
            if index + 1 >= len(command):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"sbatch {token} with no value",
                                     executable=target)
            index += 2
            continue
        if len(token) > 2 and not token.startswith("--") and token[:2] in _SBATCH_VALUES:
            index += 1
            continue
        #: AN UNMODELLED sbatch OPTION MAY TAKE THE SCRIPT NAME AS ITS VALUE, which is the same
        #: fail-open shape `_parse_env` was rebuilt for: the scan would then read a directive file
        #: as the batch script and answer confidently about the wrong bytes.
        raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, f"sbatch {token}", executable=target)
    else:
        return False                         # options only: sbatch reads the script from stdin
    if positional is None:
        if index >= len(command):
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 "sbatch with no script operand reads its batch script from "
                                 "stdin, which does not exist at scan time", executable=target)
        positional = command[index]
    _refuse_a_word_built_at_runtime(positional, "sbatch script operand")
    return _scan_shell_script_file(_resolve_shell_operand(positional, context), env, context)


def _scan_resolved_command(command: list[str], env, context: _ScanContext) -> bool:
    """THE CLOSED CHILD MODEL. Classify what a launch will exec, and refuse what cannot be proven.

    Returns whether the child STARTS A PYTHON INTERPRETER, which is what tells the caller whether
    the propagation contract still has to reach it. Raises `_LaunchRefusal` for everything else.

    The six classes, in the order they are tried, and the order matters because the earlier ones are
    decided by NAME and the later ones by reading bytes:

      1. a PYTHON interpreter, by basename or by resolved path -- the startup-flag grammar, then the
         contract. An ABSOLUTE OR RELATIVE PATH to an interpreter is now admitted only through this
         same grammar, which is what retires the `absolute path` arm of the old declared gap: the
         old model let it through because no PATH lookup happened, but the thing that guards a
         Python child is the shim on `PYTHONPATH`, not the wrapper on `PATH`;
      2. a modelled SHELL -- its `-c` string or its SCRIPT FILE is read and scanned;
      3. `git`, on a read-only subcommand allowlist plus an environment check;
      4. `sbatch`, whose batch script or `--wrap` string is scanned;
      5. a LEAF TOOL that execs no program its arguments name, admitted by location;
      6. a FILE WITH A SHEBANG naming one of the above -- `./x.sh`, or a `#!/usr/bin/env python3`
         entrypoint invoked directly.

    Everything else is `LAUNCH_REASON_UNPROVEN`. `srun`, `nice`, `nohup`, `timeout`, `xargs`,
    `command`, `exec`, `time`, `stdbuf` and `env` never reach here as themselves: they are wrappers,
    and `_resolve_launch_command` has already walked past them to the command they run.
    """
    word = _text_argument(command[0])
    located = _locate_command_word(word, env, context)
    target = _resolve_executable(located, env)
    name = _executable_basename(word)

    if _is_python_executable(target) or _is_python_executable(word):
        _refuse_a_word_built_at_runtime(word, "interpreter path")
        flag = _forbidden_python_flag(command)
        if flag is not None:
            raise _LaunchRefusal(LAUNCH_REASON_FLAGS, flag, executable=target)
        return True
    if name in _SHELL_BASENAMES:
        parsed = _parse_shell_invocation(command, env)
        if parsed["kind"] == "string":
            return _scan_shell_program(parsed["text"], env, context.deeper())
        _refuse_a_word_built_at_runtime(parsed["path"], "shell script operand")
        return _scan_shell_script_file(_resolve_shell_operand(parsed["path"], context), env,
                                       context)
    if name in _UNMODELLED_SHELL_BASENAMES:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{name} is a shell whose option and startup-file grammar this guard "
                             f"does not model", executable=target)
    if name in _REFUSED_LAUNCHER_BASENAMES:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{name} has no single option grammar across implementations and can "
                             f"take an app-file naming further commands", executable=target)
    if name in _INTERPRETER_MANAGER_BASENAMES:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{name} relaunches an interpreter through machinery this scan cannot "
                             f"see", executable=target)
    if name == "git":
        _scan_git(command, env, target)
        return False
    if name == "sbatch":
        return _scan_sbatch(command, env, context, target)
    shebang = _read_shebang(target)
    if name in _LEAF_TOOL_BASENAMES and shebang is None:
        _check_leaf(command, located, target)
        return False
    #: A LEAF NAME THAT IS A SCRIPT FALLS THROUGH TO BE SCANNED, never trusted and never refused for
    #: its name. `/usr/bin/shasum` is a Perl script on macOS and `/usr/bin/which` is a shell script
    #: on several distributions -- both are leaf names, and both are read here.

    if shebang is None:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{word} resolves to {target}, which is neither an interpreter, a "
                             f"shell, a leaf tool nor a script with a readable shebang",
                             executable=target)
    #: A SHEBANG IS AN ARGV WITH THE SCRIPT APPENDED, so it re-enters this same classification --
    #: including `#!/usr/bin/env python3 -I`, whose isolating flag is a refusal exactly as it is on
    #: a command line. The script's own path replaces the shebang's implicit operand so that a
    #: `#!...sh` shebang scans THIS file rather than looking for an operand it has not got.
    interpreter = shebang[0] if not shebang[0].endswith(os.sep) else shebang[0]
    options = shebang[1:]
    inner_name = _executable_basename(interpreter)
    inner_resolved = _resolve_executable(interpreter, env)
    if inner_name in _ENV_BASENAMES:
        parsed = _parse_env(["env", *options, "--placeholder-script"])
        if parsed is None:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"the shebang of {target} runs env with no command",
                                 executable=target)
        if parsed["clears"] or parsed["stripped"] is not None:
            raise _LaunchRefusal(LAUNCH_REASON_ENV,
                                 parsed["stripped"] or "env -i in a shebang", executable=target)
        inner = parsed["command"][:-1]       # drop the placeholder the parse needed
        if not inner:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"the shebang of {target} runs env with no command",
                                 executable=target)
        return _scan_resolved_command([*inner, target], env, context.deeper())
    if _is_python_executable(inner_resolved) or _is_python_executable(interpreter):
        flag = _forbidden_python_flag([interpreter, *options])
        if flag is not None:
            raise _LaunchRefusal(LAUNCH_REASON_FLAGS, f"{flag} in the shebang of {target}",
                                 executable=inner_resolved)
        return True
    if inner_name in _SHELL_BASENAMES:
        parsed = _parse_shell_invocation([interpreter, *options, target], env)
        if parsed["kind"] == "string":
            return _scan_shell_program(parsed["text"], env, context.deeper())
        return _scan_shell_script_file(target, env, context)
    raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                         f"the shebang of {target} names {interpreter}, which is neither an "
                         f"interpreter, a shell nor env", executable=target)


def _scan_shell_simple_command(tokens: list[str], env, context: _ScanContext,
                               substituted: bool) -> bool:
    """One SIMPLE COMMAND out of a shell program. Returns whether it starts an interpreter.

    THE ASSIGNMENT PREFIX IS CHECKED BEFORE ANYTHING ELSE AND REFUSES ON ITS OWN, which is round 6's
    second route. `PATH=/usr/bin:/bin python3 -I x.py` was already caught (the command is Python);
    `PATH=/usr/bin:/bin` ON ITS OWN LINE was not, and it disarms every later line in the file. So a
    protected name refuses wherever it is assigned and whatever follows it.

    Everything after that is a dispatch on the command word, and the shape of it is: a builtin that
    runs nothing is skipped, a builtin that runs something has the something scanned, a builtin that
    changes what a NAME resolves to is refused, and an ordinary word goes through the wrapper
    grammar into `_scan_resolved_command`.
    """
    index = 0
    stripped: "str | None" = None
    while index < len(tokens):
        name, separator, value = tokens[index].partition("=")
        if not separator or not name or name.endswith(("+", "!")):
            break
        if _is_protected_shell_variable(name):
            raise _LaunchRefusal(LAUNCH_REASON_ENV, tokens[index])
        if _breaks_propagation_contract(name, value):
            stripped = stripped or tokens[index]
        index += 1
    tokens = tokens[index:]
    if not tokens:
        return False

    word = tokens[0]
    while word in _SHELL_COMMAND_PREFIX_WORDS:
        tokens = tokens[1:]
        if not tokens:
            return False
        word = tokens[0]
    if word in _SHELL_TERMINATOR_WORDS or word in _SHELL_ITERATION_WORDS or word == "in":
        return False
    if word == "case":
        return False
    if word in context.defined:
        #: A CALL TO A FUNCTION DEFINED IN THIS PROGRAM. Its body was scanned as ordinary lines, so
        #: the call adds nothing this scan has not already read.
        return False
    if word in _SHELL_INERT_BUILTINS:
        return False
    if word in _SHELL_DECLARING_BUILTINS:
        for operand in tokens[1:]:
            declared = operand.partition("=")[0].lstrip("+")
            if not operand.startswith("-") and _is_protected_shell_variable(declared) \
                    and "=" in operand:
                raise _LaunchRefusal(LAUNCH_REASON_ENV, f"{word} {operand}")
        return False
    if word == "unset":
        for operand in tokens[1:]:
            if not operand.startswith("-") and _is_protected_shell_variable(operand):
                raise _LaunchRefusal(LAUNCH_REASON_ENV, f"unset {operand}")
        return False
    if word == "alias" or word == "unalias":
        #: AN ALIAS CHANGES WHAT A LATER WORD RESOLVES TO, so a scan that read past it would be
        #: reading a different program than the shell runs -- and `unalias` is refused with it,
        #: because the only way to unalias is to have aliased.
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{word} changes what a later command word resolves to")
    if word == "eval":
        #: `eval` RE-PARSES ITS ARGUMENTS AT RUN TIME, which is its entire purpose. Scanning the
        #: literal spelling would answer about a program that is not the one that runs.
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             "eval builds its program at run time, so there is nothing to scan")
    if word == "hash":
        for operand in tokens[1:]:
            if operand.startswith("-") and set(operand[1:]) & set("pdr"):
                raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                     f"hash {operand} changes what a later command word resolves "
                                     f"to")
        return False
    if word == "enable":
        for operand in tokens[1:]:
            if operand.startswith("-f"):
                raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                     "enable -f loads a builtin from a shared object")
        return False
    if word == "builtin":
        return _scan_shell_simple_command(tokens[1:], env, context, substituted)
    if word in ("source", "."):
        operands = [t for t in tokens[1:] if t]
        if len(operands) != 1:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"{word} with {len(operands)} operands: only a single literal "
                                 f"path can be read and scanned")
        _refuse_a_word_built_at_runtime(operands[0], f"{word} operand")
        return _scan_shell_script_file(_resolve_shell_operand(operands[0], context), env, context)
    if word == "trap":
        handler = next((t for t in tokens[1:] if not t.startswith("-")), None)
        if handler is None or handler in ("", "-"):
            return False
        return _scan_shell_program(handler, env, context.deeper())
    if word == "module":
        subcommand = next((t for t in tokens[1:] if not t.startswith("-")), None)
        if subcommand in _MODULE_READ_ONLY_SUBCOMMANDS:
            return False
        raise _LaunchRefusal(LAUNCH_REASON_ENV,
                             f"module {subcommand or ''}".strip() +
                             " can reset PATH and PYTHONPATH for every later line")

    _refuse_a_word_built_at_runtime(word, "command word")
    resolved = _resolve_launch_command(tokens, env)
    if resolved is None:
        return False
    if substituted:
        #: A COMMAND SUBSTITUTION IN A SIMPLE COMMAND WHOSE COMMAND WORD IS A SHELL, AN INTERPRETER,
        #: A WRAPPER OR `source` decides part of that command's argv at run time -- so the argv this
        #: scan read is not the argv that runs, and a clean read of it establishes nothing.
        head = _executable_basename(_text_argument(resolved["command"][0]))
        if (head in _SHELL_BASENAMES or head in _WRAPPER_SPECS or head in _ENV_BASENAMES
                or _is_python_executable(_resolve_executable(resolved["command"][0], env))):
            raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                 f"a command substitution shapes the argv of {head}")
    launches_python = _scan_resolved_command(resolved["command"], env, context)
    if not launches_python:
        return False
    disarming = stripped or resolved["stripped"]
    if resolved["clears"] and disarming is None:
        disarming = "env -i"
    if disarming is not None:
        raise _LaunchRefusal(LAUNCH_REASON_ENV, disarming,
                             executable=_resolve_executable(resolved["command"][0], env))
    return True


def _scan_shell_program(text: str, env, context: _ScanContext) -> bool:
    """Scan a shell PROGRAM -- a `-c` string or the text of a script file. Same code for both.

    A STRING IS REFUSED AND NEVER REPAIRED, and so is a file. Rewriting a command string means
    re-quoting somebody else's shell program, and a guard that edits a shell program can change what
    a run computes. The argv spelling is repaired because the tokens are ours to insert between;
    these are not.

    THE RETURN VALUE IS LOAD-BEARING AND IS NOT A CONVENIENCE. `env -i bash -c 'python3 x.py'` holds
    no isolating flag and no disarming operand INSIDE the program -- the clearing happens outside it
    -- so a scan that only raised would have returned quietly and launched a shell whose interpreter
    starts unguarded. The caller therefore has to know whether the contract still has to reach this
    child, and it may not simply assume it does: requiring the contract for EVERY shell program
    would refuse `bash -c 'ls'` from a process that had disarmed itself, which is a launch with no
    interpreter in it and nothing to guard.
    """
    try:
        lines = _drop_heredoc_bodies(_shell_logical_lines(text))
    except ValueError as err:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{text!r}: {err}") from err
    defined, lines = _strip_function_definitions(lines)
    context.defined.update(defined)
    launches_python = False
    case_depth = 0
    for line in lines:
        masked, insides = _mask_command_substitutions(line)
        for inside in insides:
            #: THE INSIDE OF A SUBSTITUTION IS A PROGRAM THAT RUNS, so it is scanned as one.
            #: `X=$(python3 -I x.py)` is otherwise an assignment with an opaque value, and the
            #: isolated interpreter in it is never seen.
            launches_python = _scan_shell_program(inside, env, context.deeper()) or launches_python
        try:
            tokens = _tokenise_shell_line(masked)
        except ValueError as err:
            raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{line!r}: {err}") from err
        first = tokens[0] if tokens else ""
        if first == "case":
            case_depth += 1
        elif first == "esac":
            case_depth = max(0, case_depth - 1)
        for command, terminator in _split_simple_commands_with_terminators(tokens):
            if case_depth and terminator == ")":
                continue                     # a `case` PATTERN, not a command
            substituted = any(_SUBSTITUTION_PLACEHOLDER in token for token in command)
            launches_python = _scan_shell_simple_command(
                command, env, context, substituted) or launches_python
    return launches_python


def _split_simple_commands_with_terminators(tokens: list[str]) -> "list[tuple[list[str], str]]":
    """`_split_simple_commands`, with the OPERATOR that ended each command kept beside it.

    ONE CONSUMER, ONE REASON: `case`. A pattern list -- `stage2) python3 x.py ;;` -- tokenises so
    that `stage2` is a simple command of its own, and an unknown one-word command is a refusal. The
    operator that ended it is `)`, which is the only thing in the token stream that distinguishes a
    pattern from a command, so the scanner needs to see it. Everything else ignores the terminator.
    """
    commands: "list[tuple[list[str], str]]" = []
    current: list[str] = []
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            continue
        if token and set(token) <= _SHELL_PUNCTUATION:
            if "<" in token or ">" in token:
                if current and current[-1].isdigit():
                    current.pop()
                skip_next = True
                continue
            if current:
                commands.append((current, token))
            current = []
            continue
        current.append(token)
    if current:
        commands.append((current, ""))
    return commands


def _scan_shell_string(text: str, env, depth: int = 0) -> bool:
    """Scan a shell COMMAND STRING. The entry point for a `-c` string and for `os.system`.

    `_scan_shell_program` is where the work is; this spelling keeps the name the shim, the controls
    and the docstring above all refer to, and it is what makes a string and a SCRIPT FILE provably
    the same scan rather than two implementations that agree today.
    """
    return _scan_shell_program(text, env, _ScanContext(os.getcwd(), depth))


def _scan_launch(argv: list[str], env, guard: GuardedPathFinder, cwd=None) -> list[str]:
    """Return the argv to launch, re-armed if that is what the contract needs; raise to refuse.

    THE ORDER IS THE CHEAPEST CORRECT ONE. The wrapper prefixes are resolved first, because until
    they are there is no executable to ask questions about; the resolved child is then CLASSIFIED
    (`_scan_resolved_command`), which reads a shell's string or script file, flag-scans an
    interpreter, and refuses a child whose coverage cannot be established; and the environment
    question is asked LAST, after any argv repair, so a repaired launch is not refused for the state
    it was repaired out of.

    A NON-PYTHON CHILD IS NO LONGER WAVED THROUGH, AND THAT IS ROUND 6's CHANGE. It used to be:
    "it inherits the re-armed contract AND the wrapper directory on PATH, which is what makes an
    ordinary interpreter it launches guarded" -- true only for a child that resolves the interpreter
    through PATH, and the reviewer wrote three shell scripts that decline to. A child is admitted now
    only when this guard could read what it will run.
    """
    resolved = _resolve_launch_command(argv, env)
    if resolved is None:
        return argv
    command = resolved["command"]
    target = _resolve_executable(command[0], env)
    context = _ScanContext(os.fspath(cwd) if cwd is not None else os.getcwd())
    if not _scan_resolved_command(command, env, context):
        return argv
    if resolved["clears"] or resolved["stripped"] is not None:
        disarming = resolved["stripped"] or "env -i"
        if resolved["inject_at"] is None:
            #: The command came out of an `env -S` STRING, so there is no argv position to insert
            #: the contract at. Refused rather than rewritten, for the reason on
            #: `_scan_shell_program`.
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


def _prepare_launch(executable, arguments, env, guard: GuardedPathFinder, cwd=None):
    """Re-arm a launch, or refuse a Python child that could not install the guard.

    Returns `(environment, argv)`. The environment is re-armed FIRST so that the armed copy is what
    every later check reads, and the argv comes back possibly REWRITTEN -- see `_contract_operands`.
    A caller that ignores the returned argv would silently drop an argv-level repair, which is why
    every wrapped primitive below writes both back.

    `cwd` IS THE LAUNCH'S WORKING DIRECTORY AND NOT THIS PROCESS'S, where the caller gave one. It
    matters because a relative operand -- `bash ./stage.sh`, `source ./setup.sh` -- names a
    different file under a different cwd, and a scan that resolved it against the wrong directory
    would read the wrong bytes and report on a program that does not run. The primitives that have
    no `cwd` parameter (`os.exec*`, `posix_spawn`) pass None, which means this process's own.
    """
    armed_env = _rearm_launch_environment(env, guard)
    argv = _launch_argv(arguments)
    try:
        return armed_env, _scan_launch(argv, armed_env, guard, cwd)
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
        armed_env, armed_argv = _prepare_launch(executable, argv, env, guard,
                                                bound.arguments.get("cwd"))
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
        # THE SECOND CHANCE TO REFUSE, as a state and never a boolean. `armed` means an admitted
        # child's `python3 -I` is refused by the wrapper on PATH as well as by the scan that read
        # the child; anything else names why it is not. Since round 6 this NARROWS the guard by one
        # redundant check rather than widening `declared_gap`, because the closure below reads what
        # a child will run before it starts.
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
