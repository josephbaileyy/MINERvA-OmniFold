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
  2. a modelled SHELL -- `sh`, `bash` and `dash`, all three REWRITTEN to run as restricted
     bash. A `-c` string is scanned as before AND A SCRIPT FILE OPERAND IS READ AND SCANNED
     WITH THE SAME SCANNER. A shell with no operand and no `-c` reads its program
     from stdin and is refused; so are `-l`/`--login`, `-i`, `-s`, `--rcfile`,
     `--init-file`, `+r`, an `-o`/`-O` value this file does not model, and any shell
     launch made with `$BASH_ENV` or `$ENV` set, because each of them runs a startup file
     this guard was never handed or asks for the restriction not to hold. `zsh` joined
     `ksh`, `mksh`, `fish`, `csh` and `tcsh` as a refused shell when the rewrite arrived:
     an admitted zsh program would have to run under `bash -r`, which is a different
     language, or under a zsh restricted mode this file does not model;
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

ROUND 7 CLASSIFIES BY THE EXECUTABLE THE KERNEL WILL RUN, NOT BY `argv[0]`. Every POSIX
exec primitive takes the file to execute separately from the argv, and `argv[0]` is a
DISPLAY NAME -- `subprocess.run(["ls", "-I", "child.py"], executable=sys.executable)` was
classified as a leaf tool called `ls` while Python ran with `-I`. So the scan is now over
`(the real executable, argv[1:])` for all sixteen wrapped primitives: `executable=` for
`subprocess.*` (and with `shell=True` the shell is the executable and `executable=`
replaces it), the path argument for `os.execv`/`execve`/`spawn*`/`posix_spawn*`, the name
resolved on the CHILD's PATH for the `p` spellings, and `/bin/sh` for `os.system`.

AND EVERY ADMITTED SHELL NOW RUNS AS RESTRICTED BASH WITH A WRAPPER-ONLY PATH, which is the
change that stops this file's model of shell syntax from being the residual. Rounds 5, 6 and
7 each found a construct the model got wrong -- an unparsed `env` prefix, an unread script
file, a `"$FLAG"` in an argument, a `cd` the resolver did not follow -- and each time the
answer was a better model. It is now a smaller claim instead: `install()` pins a real bash
from a named system prefix and records its sha256, and `_scan_launch` REWRITES every
admitted shell launch to `<that bash> -r [--posix] <surviving options> <-c string|script>`
with `PATH` set to the guard's wrapper directories and nothing else. Bash's own restricted
mode then refuses a command name with a slash, `cd`, `exec`, a `PATH`/`SHELL`/`ENV` or
`BASH_ENV` assignment, `command -p`, `hash -p`, `enable -f`, output redirection and
`set +r`; and everything the wrapper directory does not hold is `command not found`. The
static scanner stays as the FIRST refuser, and for an `sbatch` job script -- which runs on a
compute node, in another process tree -- it stays the ONLY one.

THE WRAPPER DIRECTORY IS THEREFORE WHAT A SHELL PROGRAM MAY REACH. Beside `python`/`python3`
it carries committed wrappers for `bash` and `sh` (re-enter restricted mode), `git` (the
read-only allowlist and the hostile-environment rule, then exec), `sbatch` and `srun` (scan
what they will run, then exec) and the five reporting Slurm clients; and `install()`
generates one forwarder per leaf tool that exists under a named system prefix ON THIS HOST,
because which tools exist is a property of the machine and cannot be committed. Every
committed wrapper delegates its decision to `mnv_guard_shim/wrapper_exec.py`, which loads
THIS module and calls these same functions -- the wrappers own no grammar.

ROUND 8 HOOKS THE LOWEST PYTHON-VISIBLE LAYER, BECAUSE COVERAGE ENUMERATED BY PUBLIC API IS NOT
COVERAGE. Round 7's table listed sixteen primitives; round 8's reviewer went under the list.
`_posixsubprocess.fork_exec` is the last Python-visible layer before the kernel on POSIX -- every
one of `subprocess.Popen`, `multiprocessing`'s `spawnv_passfds` (both the `spawn` and the
`forkserver` start methods) and `concurrent.futures` ends up there -- and a DIRECT call to it
running `python3 -I <child>` ran, printed its sentinel, loaded the wrong tree and wrote no record.
Every signature above it was unchanged, so nothing in the public table was wrong; the table was
simply not the floor. The floor is hooked now, in BOTH bindings CPython gives it: the module
attribute `_posixsubprocess.fork_exec`, and the `from _posixsubprocess import fork_exec as
_fork_exec` alias `subprocess` holds at module level -- which is the one `Popen._execute_child`
actually calls, so patching only the first would have left `subprocess` on the old path. Both exist
in 3.11, 3.12 and 3.13 and both are patched; see `_FORK_EXEC_BINDINGS`. The scan there is the same
`(real executable, argv[1:])` classification and the same environment contract as everywhere else,
with two shapes peculiar to that layer: the executable arrives as `executable_list`, a list of
CANDIDATE paths tried in order, so the file scanned is the first one that EXISTS -- which is the one
the kernel will run; and the environment arrives as a list of `NAME=VALUE` BYTES, which is parsed,
re-armed and written back as bytes, or refused when `_scan_launch` says so. A call whose shape
cannot be read at all is `LAUNCH_REASON_KERNEL_FLOOR`, which names the layer.

THE PUBLIC HOOKS ARE KEPT AND THE FLOOR DOES NOT SCAN TWICE. The public primitives are still where
a launch is REPAIRED, because they are where the argv positions are known well enough to insert
`env` contract operands or to swap in the restricted-bash spelling; the floor is what catches a
caller that never visits them. A launch `_prepare_launch` has already read is handed down as an
approved ticket (`_ApprovedLaunch`, per thread) and the lower layer consumes it instead of
re-reading -- which is not an optimisation. Re-scanning a launch this guard itself REWROTE refuses
it: the rewrite runs with `PATH` set to the wrapper directories only, and a second scan resolving
`ls` through that `PATH` finds no system prefix and refuses a correct program. That was already
live before round 8 wherever `subprocess.Popen` chose `os.posix_spawn` over `fork_exec`
(`close_fds=False`), and the ticket closes it in the one place both layers pass through.

THE TICKET IS KEYED ON (ARGV, FILE), because the argv is not the executable -- which is round 8's
own finding applied to round 8's own mechanism. Keyed on the argv alone, anything that got to run
inside the window IN THIS THREAD could spend the approval on a different file: CPython calls
`preexec_fn` in the forked child with the approval stack inherited, and a `__del__`, a weakref
finalizer or a `fileno()` reached from inside `Popen.__init__` is the same shape. So the issue site
records the file the layer below will actually exec, resolved through the ARMED environment, and
both halves must be equal before the floor skips its scan; `preexec_fn` is refused outright beside
that (`LAUNCH_REASON_PREEXEC`).

AND THE ENVIRONMENT IS CHECKED AT THE CONSUME SITE RATHER THAN CARRIED BY THE TICKET, which is
round 10's correction. The ticket certifies that the layer above scanned this argv and this file,
and NOTHING ELSE: on the ticket path the lower layer passed the caller's own environment straight
through, so an in-window call matching both halves of the key while stripping only `MNV_GUARD_*`
and `PYTHONPATH` started an UNGUARDED interpreter on the approved argv and the approved file --
round 9's class, one field over. Every consume site now requires that the environment REACHING THE
CHILD is armed and refuses with `LAUNCH_REASON_TICKET_ENV` when it is not. It is a CHECK and not a
third half of the key, because a correct launch's environment already is the armed one, while a
key half that every re-spelling of an environment could break would only ever make the lower layer
scan MORE -- silently, which is the failure the ticket itself was introduced to fix. An ABSENT
environment is admitted: at these layers None means inherit, and what an inheriting child gets is
this armed process's own `os.environ`, which is what the check reads.

`multiprocessing.set_executable` IS NOT ADVERSARIAL AND IS HOOKED WHERE THE CHOICE IS MADE. A direct
`fork_exec` call is something only an attacker writes; `set_executable` is public API a launcher may
reasonably reach for, and it names the file every `spawn` and `forkserver` child will exec. Since
`multiprocessing` builds that child's argv itself -- `[exe, *interpreter flags, "-c",
"<spawn_main>"]` -- the chosen file must be a PYTHON INTERPRETER this guard admits, and anything
else is `LAUNCH_REASON_UNPROVEN` at the moment it is set rather than a puzzle at spawn time. The
hook is installed lazily, when `multiprocessing.spawn` is imported, so a guarded process that never
uses `multiprocessing` does not pay for it. `fork` needs no hook -- the forked child IS this
interpreter, with this guard installed -- and `forkserver` launches through `spawnv_passfds` and is
therefore covered by the floor; both are asserted rather than assumed.

THE FOUR DECLARED RESIDUALS, AFTER THE CLOSURE AND ALL THREE HALVES, ARE NONE OF THEM AN
UNSCANNED PYTHON LAUNCH. (1) TRUST BY LOCATION: a leaf tool, a read-only `git`, `sbatch` and
the real bash are admitted because the file was found in a named system prefix and carries
no shebang, so a tampered system prefix -- or a repository-local `.git` configuration naming
an external program -- is outside this guard. (2) THE RESTRICTED-SHELL GUARANTEE IS BASH'S
OWN, documented in the bash manual section 6.10, so a defect in bash's restricted mode is
the residual for shells. (3) AN `sbatch` JOB SCRIPT is read statically because it runs where
no shell of ours does, and its residual is the static model's -- which is a REFUSAL and
never an unguarded run: a job script whose command words, interpreter options or sbatch
options are built at run time is refused and not read. (4) AN ADMITTED PYTHON CHILD is
guarded by the shim on `PYTHONPATH` and by these hooks in turn, DOWN TO
`_posixsubprocess.fork_exec`. What remains is a caller that reaches the kernel WITHOUT that
layer -- `ctypes`/`cffi` calling `execve` or `posix_spawn` in libc directly, a C extension
doing the same, or a rebuilt interpreter whose `_posixsubprocess` is not the module object
this process patched. That one is NAMED AND NOT COVERED, and it is the only residual here
whose measurement is a run that SUCCEEDS: a ctypes `execve` of `python3 -I` loads the wrong
tree, and the control that says so asserts exactly that. All four are written into
EVERY inventory record as `declared_gap` so a ratchet reader sees the coverage boundary
without reading this file, and they are measured -- not asserted -- in
`tests/test_mnv_guarded_run.py::TheSubprocessBoundaryIsCovered`,
`TheClosedChildModelRefusesWhatItCannotProve`,
`TheRestrictedShellIsTheSecondLayerAndRefusesOnItsOwn` and
`TheKernelFloorIsHookedAndTheResidualIsBelowIt`, beside the covered counterparts they
must be distinguished from. Read `declared_gap` together with `path_shim` and `shell`: when
either is not armed, one of the enforcing halves did not run.

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
import threading

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
WRAPPER_EXEC_FILE = SHIM_DIR / "wrapper_exec.py"

#: THE DYNAMIC HALF'S CONTRACT, exported by `install()` and read by the committed wrappers.
#: `MNV_GUARD_REAL_BASH` is the bash the guard pinned at arm time -- the wrappers must not resolve
#: one of their own, or the shell that enforces the restriction would be chosen by whatever `PATH`
#: happened to say. `MNV_GUARD_SYSTEM_PREFIXES` is `_SYSTEM_EXECUTABLE_PREFIXES` as a string,
#: because a wrapper that retyped the prefix list would be a second implementation of arm (1) of
#: `DECLARED_GAP` and the two copies would drift.
REAL_BASH_ENV = "MNV_GUARD_REAL_BASH"
SYSTEM_PREFIXES_ENV = "MNV_GUARD_SYSTEM_PREFIXES"

#: A KNOB THAT EXISTS FOR THE TEST SUITE AND FOR NOTHING ELSE, and it is named so that a reader of a
#: record cannot miss it. Round 7's design requires the two layers -- the static scanner and the
#: restricted shell -- to be shown REFUSING INDEPENDENTLY, and a layer cannot be shown to refuse on
#: its own while the layer in front of it refuses first. Setting this makes `_scan_launch` swallow
#: its own `_LaunchRefusal` and hand the launch on to the shell rewrite, so what refuses next is
#: bash. It does NOT disable the rewrite, the environment contract or the import guard, and every
#: record written while it is set says `static_scan: disabled-for-test`.
STATIC_SCAN_DISABLED_ENV = "MNV_GUARD_TEST_ONLY_DISABLE_STATIC_SCAN"

#: Wrapper basenames the tracked `bin/` already carries. Any other `sys.executable` basename --
#: `python3.11`, `python3.12` -- gets a generated delegator at arm time, because a wrapper only
#: intercepts the NAME it is installed under and the versioned name is the one a cluster module
#: file puts in front of a science script.
TRACKED_WRAPPER_NAMES = ("python3", "python")

#: EVERY COMMITTED FILE THE PATH HALF EXECUTES, relative to `mnv_guard_shim/`. This tuple is the
#: single list: `_path_shim_digests` hashes it into every record, `docs/orchestration/campaignctl.py`
#: binds the same paths through `GUARD_SHIM_PATHS`, and the campaign fixture copies them. A file
#: added to `bin/` and not to this tuple is a file the queue does not bind and no record pins, which
#: is the state the round-5 wrapper-swap control exists to make impossible.
COMMITTED_SHIM_FILES = (
    "sitecustomize.py",
    "scan_argv.py",
    "wrapper_exec.py",
    "bin/python3",
    "bin/python",
    "bin/_wrapper_body",
    "bin/bash",
    "bin/sh",
    "bin/git",
    "bin/sbatch",
    "bin/srun",
    "bin/sacct",
    "bin/squeue",
    "bin/sinfo",
    "bin/scancel",
    "bin/sstat",
)

#: The basenames the committed `bin/` occupies. A generated forwarder is NOT written for any of
#: them: the committed file is the one that must win, and two files of one name in two directories
#: on one PATH is a question about ordering that nobody should have to answer.
COMMITTED_WRAPPER_NAMES = frozenset(
    name[len("bin/"):] for name in COMMITTED_SHIM_FILES if name.startswith("bin/")
)

#: THE COVERAGE BOUNDARY, AS A STRING IN EVERY RECORD. A gap stated only in a docstring is invisible
#: to the ratchet readers that consume these records, and a reader who cannot see the boundary reads
#: a green record as total coverage. Read it beside `path_shim` and `shell`: when either is not
#: armed the boundary is wider than this sentence, because one of the two enforcing halves did not
#: run.
#:
#: REWRITTEN FOR ROUND 7, AND THE ARM THAT LEFT IS THE STATIC MODEL OF SHELL SYNTAX. The round-6
#: sentence named two residuals, TRUST BY LOCATION and REFUSAL, and it was silent about the thing
#: that actually carried the weight: every claim about a shell child rested on this file's model of
#: shell syntax being right. It was not. Round 7's reviewer walked through it three times -- an
#: `executable=` that the classification ignored, a `"$FLAG"` in an argument rather than in a
#: command word, and a `cd` the resolver did not model -- and each of the three ran the wrong-tree
#: import and wrote no child record. So the model stopped being the enforcement: an admitted shell
#: is REWRITTEN to run as `bash -r` with a PATH holding the guard's wrapper directories and nothing
#: else, and what a shell program can reach is now bounded by bash's own restricted mode rather than
#: by how well this file parses. The static scanner stays as the first refuser -- and stays the ONLY
#: enforcement for an `sbatch` job script, which runs where no shell of ours does -- so its residual
#: is named separately and honestly as arm (3).
DECLARED_GAP = (
    "FOUR RESIDUALS, AND NONE OF THEM IS AN UNSCANNED PYTHON LAUNCH. (1) TRUST BY LOCATION: a leaf "
    "tool (ls, cat, mkdir, tar, ... -- see _LEAF_TOOL_BASENAMES), a read-only `git`, `sbatch`, and "
    "THE REAL bash THE RESTRICTED REWRITE RUNS are executed because their file was found under a "
    "named system prefix (/bin, /usr/bin, /sbin, /usr/sbin, /usr/local/bin, /usr/local/sbin, "
    "/opt/homebrew/bin, /opt/local/bin, /opt/slurm/bin, /usr/global/bin) and carries no shebang; "
    "nothing about its behaviour is read. So a TAMPERED SYSTEM PREFIX, or a repository-local .git "
    "configuration naming an external program (diff.external, a hook, core.pager), is outside this "
    "guard: those are files rather than an argv, and the environment variables that do the same job "
    "(GIT_EXTERNAL_DIFF, GIT_SSH_COMMAND, GIT_PAGER, ...) are refused where they can be seen. "
    "(2) THE RESTRICTED-SHELL GUARANTEE IS BASH'S OWN. Every admitted shell launch is rewritten to "
    "`<that bash> -r [--posix] ...` with PATH set to the guard's wrapper directories only, so a "
    "command name with a slash, `cd`, `exec`, a PATH/SHELL/ENV/BASH_ENV assignment, `command -p`, "
    "`hash -p`, `enable -f`, output redirection and `set +r` are refused BY BASH, and every other "
    "program is `command not found`. The residual for shells is therefore a defect in bash's "
    "restricted mode as documented in the bash manual section 6.10 -- not this file's model of "
    "shell syntax, which is now the first refuser rather than the enforcement. (3) AN sbatch JOB "
    "SCRIPT RUNS ON THE CLUSTER, OUTSIDE THIS PROCESS TREE, where no restricted shell and no "
    "wrapper directory of ours exists -- so for it the static model IS the enforcement and its "
    "residual is the static model's. That residual is a REFUSAL and never an unguarded run: a job "
    "script whose command words, interpreter options, wrapper options or sbatch options are built "
    "at run time is REFUSED and not read, and the cost is a submission that must be respelled. "
    "(4) AN ADMITTED PYTHON CHILD IS GUARDED BY THE SHIM ON PYTHONPATH AND BY THESE HOOKS IN TURN, "
    "DOWN TO _posixsubprocess.fork_exec -- the last Python-visible layer before the kernel on "
    "POSIX, hooked in BOTH of the bindings CPython gives it (_posixsubprocess.fork_exec and the "
    "`from _posixsubprocess import fork_exec as _fork_exec` alias subprocess holds), so "
    "subprocess.Popen, multiprocessing's spawnv_passfds (spawn AND forkserver), "
    "concurrent.futures and a DIRECT caller are all scanned with the executable and argv they "
    "pass; multiprocessing.set_executable is classified where the choice is made rather than only "
    "where it is used. WHAT REMAINS IS A CALLER THAT REACHES THE KERNEL WITHOUT THAT LAYER: ctypes "
    "or cffi calling execve/posix_spawn/fork+exec in libc directly, a C extension doing the same, "
    "or a REBUILT INTERPRETER whose _posixsubprocess is not the module object this process "
    "patched. That is NAMED AND NOT COVERED -- it is measured rather than asserted, in "
    "tests/test_mnv_guarded_run.py::TheKernelFloorIsHookedAndTheResidualIsBelowIt, where a ctypes "
    "execve of `python3 -I` RUNS -- and it is a different claim from the three above: an "
    "in-process caller that declines every Python-visible launch API there is")

#: THE PATH HALF'S OWN CONTRACT, as a tuple, because it has to be RE-ARMED in exactly the two
#: places the propagation contract is. A restricted shell's `PATH` is the wrapper directories, so a
#: wrapper that could not find the real interpreter, the real bash or the system prefixes would be
#: the only thing on `PATH` and unable to run anything -- and an `env -i` in front of the shell wipes
#: all four. `PROPAGATION_ENV_VARS` is deliberately NOT widened to hold them: those four are what a
#: CHILD INTERPRETER needs to install the guard, and `_environment_reaching_child_is_armed` refuses
#: a launch that lacks one. A missing `MNV_GUARD_REAL_PYTHON` does not make a child unguarded, it
#: makes a wrapper unable to resolve -- a different failure with a different verdict.
PATH_HALF_ENV_VARS = (
    REAL_PYTHON_ENV,
    PATH_SHIM_DIRS_ENV,
    SYSTEM_PREFIXES_ENV,
    REAL_BASH_ENV,
)

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
        #: THE DYNAMIC HALF'S STATE, recorded for the same reason `path_shim` is: a deployment whose
        #: named prefixes hold no bash still guards imports and still refuses at every launch site,
        #: but it refuses EVERY shell launch, and that is a different guard from this one. A reader
        #: of the record must be able to see which. `real_bash` pins the bytes that enforced.
        self.shell = "not-armed"
        self.real_bash = {"path": None, "sha256": None}
        #: `enabled`, or `disabled-for-test` when `MNV_GUARD_TEST_ONLY_DISABLE_STATIC_SCAN` made the
        #: static half stand down so the restricted shell could be measured on its own. A record
        #: written in that state is not evidence about a production run and says so.
        self.static_scan = "enabled"
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
        if fullname == _MULTIPROCESSING_SPAWN_MODULE:
            self._arm_multiprocessing_when_it_loads(spec)
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

    def _arm_multiprocessing_when_it_loads(self, spec) -> None:
        """Hook `multiprocessing.spawn.set_executable` the moment that module finishes executing.

        WHY THE IMPORT HOOK RATHER THAN AN IMPORT. `set_executable` names the file every `spawn` and
        `forkserver` child is exec'd from, so it has to be classified -- but importing
        `multiprocessing.spawn` from `install()` to reach it would pull `socket`, `pickle` and a
        dozen more modules into EVERY guarded process, including the ones `sitecustomize` starts
        during interpreter startup, and would move the `checked` count every inventory record
        reports. This finder already sees every import, so the cheap and honest place to arm the
        hook is the one import that makes it relevant.

        IT WRAPS THE LOADER, NOT THE FINDER'S ANSWER, because the module's attributes do not exist
        until `exec_module` has run: a patch applied at `find_spec` time would be overwritten by the
        module's own `def set_executable`. The wrapper runs the real `exec_module` FIRST and hooks
        after it returns, so an import that raises leaves nothing half-armed.
        """
        loader = getattr(spec, "loader", None)
        exec_module = getattr(loader, "exec_module", None)
        if exec_module is None or getattr(exec_module, "_mnv_guard_armed", False):
            return

        def armed(module):
            exec_module(module)
            _install_multiprocessing_guards(self)

        armed._mnv_guard_armed = True
        try:
            loader.exec_module = armed
        except (AttributeError, TypeError):
            #: A LOADER THAT WILL NOT TAKE THE ATTRIBUTE IS NOT A REFUSAL. The launch itself is
            #: still covered by the `fork_exec` floor, which is where the enforcement lives; what
            #: is lost is only WHERE the refusal lands. Raising here would turn an unusual loader
            #: into a process that cannot import multiprocessing at all.
            return

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


def _sha256_of_committed_shim_files() -> dict:
    """sha256 of every committed file the PATH half executes, keyed by its path under the shim.

    ONE LIST AND NOT FIFTEEN CALL SITES: `COMMITTED_SHIM_FILES` is what `campaignctl` binds and what
    the campaign fixture copies, so hashing anything else here would let a record pin a set the
    queue does not bind. A file that cannot be read hashes to None rather than raising, because a
    record must be writable on the path where the deployment is broken.
    """
    return {name: _sha256_or_none(str(SHIM_DIR / name)) for name in COMMITTED_SHIM_FILES}


def _resolve_real_bash() -> "tuple[str | None, str]":
    """The real bash every admitted shell launch is rewritten onto, and its sha256, or why not.

    IT IS LOOKED FOR IN A NAMED LIST AND NOT ON `PATH`. The whole point of the rewrite is that the
    shell stops being chosen by the environment the guarded program controls; resolving it through
    `PATH` would put the enforcer back under the control of the thing it enforces against. This is
    arm (1) of `DECLARED_GAP` -- trust by location -- applied to the one binary the dynamic half
    depends on, and it is pinned by sha256 in every record so a reader can see WHICH bash ran.

    A TEXT FILE WITH A SHEBANG IS NOT A bash. `/usr/local/bin/bash` is a wrapper script on some
    sites, and running `-r` under a wrapper enforces nothing, so a candidate with a `#!` is skipped
    exactly as a leaf tool with a shebang is not trusted by its name.

    Returns `(path or None, state)`. None is not an exception: a deployment with no bash under any
    named prefix still guards imports and still refuses at every launch site -- it simply refuses
    EVERY shell launch, which is narrower and must be READABLE rather than inferred from silence.
    """
    for candidate in _REAL_BASH_CANDIDATES:
        if not (os.path.isfile(candidate) and os.access(candidate, os.X_OK)):
            continue
        try:
            with open(candidate, "rb") as handle:
                if handle.read(2) == b"#!":
                    continue
        except OSError:
            continue
        return candidate, "restricted"
    return None, ("not-armed:no bash under any of "
                  f"{', '.join(_REAL_BASH_CANDIDATES)}; every shell launch refuses")


def _path_without_shim_dirs(path_value) -> str:
    """`path_value` with the guard's own wrapper directories removed.

    WHY A SCAN MUST NOT RESOLVE THROUGH THE WRAPPERS. Round 7 puts a forwarder for every leaf tool
    on `PATH`, so `shutil.which("ls")` from a guarded process finds the guard's own file -- which is
    not under a system prefix, so `_check_leaf` would refuse `ls` and the guard would refuse every
    correct launcher on the machine. The scan asks "which real program is this", and the real
    program is the one `PATH` names once this guard's own directories are taken out; the wrappers
    are what the CHILD resolves, and they are deliberately in front of it. `bin/python3` performs
    exactly this subtraction in shell for exactly this reason.
    """
    if isinstance(path_value, bytes):
        path_value = os.fsdecode(path_value)
    text = os.environ.get("PATH") if path_value is None else str(path_value)
    if text is None:
        text = os.defpath
    shim_dirs = {entry for entry in (os.environ.get(PATH_SHIM_DIRS_ENV) or "").split(os.pathsep)
                 if entry}
    if not shim_dirs:
        return text
    return os.pathsep.join(entry for entry in text.split(os.pathsep) if entry not in shim_dirs)


def _restricted_shell_environment(env) -> dict:
    """The environment an admitted shell launch runs with. PATH is the wrapper directories, ONLY.

    THIS IS THE HALF THAT MAKES `-r` MEAN SOMETHING. Restricted bash refuses a command name with a
    slash, so every program the script runs is resolved through `PATH` -- and if `PATH` is the
    guard's wrapper directory and nothing else, the set of programs the script can reach is exactly
    the set this guard wrote a wrapper for. Anything else is `command not found`, which is a refusal
    the shell issues without this guard having to model the syntax that reached it. That is the
    whole of round 7's answer to "the static model of shell syntax is the residual": it is not, any
    more; the residual is bash's own restricted mode.

    The propagation contract and the shim-first `PYTHONPATH` are KEPT, because a Python child the
    script starts must still arrive guarded. The stripped set is `_RESTRICTED_SHELL_STRIPPED_ENV_VARS`
    plus every `BASH_FUNC_*`, each of which is a program or a lookup that would run before, or
    instead of, what the wrapper directory allows.
    """
    source = dict(os.environ if env is None else env)
    for name in _RESTRICTED_SHELL_STRIPPED_ENV_VARS:
        source.pop(name, None)
    for name in [n for n in source
                 if any(n.startswith(p) for p in _RESTRICTED_SHELL_STRIPPED_ENV_PREFIXES)]:
        source.pop(name, None)
    source["PATH"] = os.environ.get(PATH_SHIM_DIRS_ENV) or str(PATH_SHIM_DIR.resolve())
    source["PYTHONPATH"] = _shim_first_pythonpath(source.get("PYTHONPATH"))
    for name in PATH_HALF_ENV_VARS:
        #: RE-ARMED FROM THIS PROCESS, never copied from the caller's `env=`. The wrappers ARE the
        #: PATH now, so a caller who passed an `env=` without these would hand the restricted shell
        #: a directory of wrappers none of which can resolve anything.
        value = os.environ.get(name)
        if value is None:
            source.pop(name, None)
        else:
            source[name] = value
    return source


def _path_shim_digests() -> dict:
    """sha256 of every tracked file the PATH half executes, or None where one cannot be read.

    WHY THE DIGESTS ARE IN THE RECORD AND NOT ONLY IN GIT. The wrappers are tracked, but the A-2(f)
    source manifest binds `.py` and `.sh` files -- and a POSIX `sh` script installed on `PATH` as
    `python3` cannot carry a suffix, because the suffix would be part of the name it intercepts. So
    the manifest does not cover `bin/python3` or `bin/python`, and widening its suffix rule is a
    change to another contract's semantics rather than a fix here. What binds these bytes is
    therefore this digest, recorded per run beside `shim_sha256`, which is the same instrument the
    sitecustomize half already uses. `scan_argv.py` IS manifest-covered and is digested anyway:
    reading some of the set from one place and the rest from another is how a reader ends up
    comparing unlike things. Round 7 added ten more committed wrappers -- `bash`, `sh`,
    `git`, `sbatch`, `srun` and the five Slurm clients -- and the one list they all come
    from is `COMMITTED_SHIM_FILES`, so a wrapper with no digest is not a state this reaches.
    """
    global _PATH_SHIM_DIGESTS
    if _PATH_SHIM_DIGESTS is None:
        #: MEMOISED PER PROCESS, and that is a statement about the files rather than an
        #: optimisation for its own sake: these are the bytes THIS process executes, they are read
        #: at arm time, and a change to them mid-run would not be picked up by the wrappers either.
        #: It is called at least twice per `install()` and once more from `write_inventory`, and
        #: hashing sixteen committed files three times shows up in a wall-clock budget.
        _PATH_SHIM_DIGESTS = _sha256_of_committed_shim_files()
    return dict(_PATH_SHIM_DIGESTS)


_PATH_SHIM_DIGESTS: "dict | None" = None


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
    if not WRAPPER_EXEC_FILE.is_file():
        return f"not-armed:the tracked wrapper executor is missing at {WRAPPER_EXEC_FILE}", digests
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
    # THE COMMITTED DIRECTORY PREPENDS THE GENERATED ONE, deliberately: the committed `bash`, `sh`,
    # `git` and Slurm wrappers are the ones that must win, and the generated set is only the leaf
    # tools this HOST happens to carry. Which leaf tools exist is a property of the machine and can
    # never be committed, which is why they are generated rather than tracked.
    try:
        directories.append(_generated_forwarder_dir())
    except OSError as err:
        state = (f"armed-no-leaf-forwarders:{err}; a restricted shell reaches no leaf tool and "
                 f"every one of them is `command not found`")
    os.environ[REAL_PYTHON_ENV] = sys.executable
    os.environ[SYSTEM_PREFIXES_ENV] = os.pathsep.join(_SYSTEM_EXECUTABLE_PREFIXES)
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


def _locate_a_system_tool(basename: str) -> "str | None":
    """The absolute path of a leaf tool under a named system prefix, or None.

    THE PREFIXES ARE SEARCHED IN ORDER AND `PATH` IS NOT CONSULTED, which is the same rule
    `_check_leaf` applies and for the same reason: a leaf is trusted because of the directory it was
    found in, and a `PATH` lookup inside a guarded process would find this guard's own wrappers
    first. A SHEBANG TEXT FILE IS NOT A LEAF -- `/usr/bin/shasum` is a Perl script on macOS and
    `/usr/bin/which` is a shell script on several distributions -- so no forwarder is written for
    it, and inside a restricted shell it is `command not found` rather than a program nobody read.
    """
    for prefix in _SYSTEM_EXECUTABLE_PREFIXES:
        if basename not in _names_in_a_system_prefix(prefix):
            continue
        candidate = os.path.join(prefix, basename)
        if not (os.path.isfile(candidate) and os.access(candidate, os.X_OK)):
            continue
        try:
            with open(candidate, "rb") as handle:
                if handle.read(2) == b"#!":
                    return None              # a script, and a script is read rather than trusted
        except OSError:
            return None
        return candidate
    return None


_SYSTEM_PREFIX_NAMES: dict = {}


def _names_in_a_system_prefix(prefix: str) -> frozenset:
    """The basenames in one system prefix, listed ONCE per process rather than stat'ed per name.

    `_generated_forwarder_dir` asks this question forty times over ten prefixes, at `install()`, in
    every guarded process in a run -- four hundred `stat` calls on a path that cannot change under
    it. One `scandir` per prefix answers all of them, and the CORRECTNESS check (a regular
    executable file, no shebang) still runs on the candidate this narrows to.
    """
    if prefix not in _SYSTEM_PREFIX_NAMES:
        try:
            _SYSTEM_PREFIX_NAMES[prefix] = frozenset(os.listdir(prefix))
        except OSError:
            _SYSTEM_PREFIX_NAMES[prefix] = frozenset()
    return _SYSTEM_PREFIX_NAMES[prefix]


def _write_an_executable_file(path: pathlib.Path, text: str) -> None:
    """Create an executable file in one open, rather than write-then-chmod.

    Forty forwarders per guarded process is forty extra syscalls the mode argument of `os.open`
    already covers, and this runs at `install()` inside a wall-clock budget a campaign control
    measures. The mode is applied at creation, so there is no window in which the file exists and
    is not executable.
    """
    descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o755)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text)


def _generated_forwarder_dir() -> str:
    """One forwarder per leaf tool that exists under a system prefix ON THIS HOST.

    WHY THEY ARE GENERATED AND NOT COMMITTED, which is the same argument `_generated_wrapper_dir`
    already makes for the versioned interpreter name: WHICH leaf tools exist, and WHERE, is a
    property of the machine. `/sbin/sha256sum` on this laptop, `/usr/bin/sha256sum` on Perlmutter,
    `shasum` as a Perl script on one and absent on the other -- a committed file would either bake
    in one host's answer or have to search at run time, and searching at run time in shell is the
    prefix list retyped. So `install()` resolves each name ONCE, here, and writes a forwarder whose
    body is a single `exec` of an absolute path.

    A NAME WITH NO FORWARDER IS `command not found` INSIDE THE RESTRICTED SHELL, and that is the
    intended state rather than a gap: the restricted shell's `PATH` is these directories only, so
    the set of programs a shell program can reach is exactly the set this guard resolved and can
    name. `awk`, `perl` and `make` are absent from `_LEAF_TOOL_BASENAMES`, so they are absent here.
    """
    directory = tempfile.mkdtemp(prefix=f"mnv-guard-tools-{os.getpid()}-")
    for basename in sorted(_LEAF_TOOL_BASENAMES):
        if basename in COMMITTED_WRAPPER_NAMES:
            continue                         # the committed wrapper is the one that must win
        resolved = _locate_a_system_tool(basename)
        if resolved is None:
            continue
        forwarder = pathlib.Path(directory) / basename
        _write_an_executable_file(
            forwarder,
            "#!/bin/sh\n"
            f"# GENERATED at arm time by {__file__} for this process only. Not tracked, not\n"
            "# evidence: it exists so that a restricted shell, whose PATH is the guard's wrapper\n"
            "# directories and nothing else, can still reach the leaf tools _LEAF_TOOL_BASENAMES\n"
            "# names. The path below was resolved ONCE, from a named system prefix, and the file\n"
            "# it names carries no shebang -- that is the whole of what admits it.\n"
            f"exec {shlex.quote(resolved)} \"$@\"\n")
    #: Best-effort removal, for the reason recorded on `_generated_wrapper_dir`: an `os.exec*`
    #: replacement never runs `atexit`, and a child outliving its parent must not lose `ls`.
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
    found = shutil.which(text, path=_path_without_shim_dirs(path_value))
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

#: ROUND 8's REASON, AND IT NAMES A LAYER RATHER THAN A CONSTRUCT. Round 8's reviewer went UNDER the
#: public API. `_posixsubprocess.fork_exec` is the last Python-visible layer before the kernel on
#: POSIX -- `subprocess.Popen`, `multiprocessing`'s `spawnv_passfds` and `concurrent.futures` all
#: end up there -- and a DIRECT call to it with `python3 -I <child>` ran, printed its sentinel and
#: left no record: the exact defect round 7 closed for `subprocess`, `os.exec*` and `os.spawn*`,
#: reached one floor down and with every signature unchanged. The floor is hooked now, in both of
#: its bindings, so every caller above it is scanned with the executable and argv it passes. THIS
#: reason is what the floor itself raises when it is handed a call whose SHAPE it cannot read -- no
#: argument vector, an empty candidate-executable list, or an environment member that is not
#: `NAME=VALUE` -- and it names the layer so a reader of a record can tell a refusal issued at the
#: floor from one a public primitive issued. It is fail-closed for the same reason
#: `LAUNCH_REASON_UNPARSED` is: an unreadable call cannot be scanned, and an unscanned Python launch
#: is the defect this file exists for.
LAUNCH_REASON_KERNEL_FLOOR = "a-fork_exec-call-at-the-kernel-floor-this-guard-cannot-read"

#: ROUND 9's REASON, AND IT NAMES A CONSTRUCT THAT RUNS CALLER CODE INSIDE THIS GUARD'S OWN WINDOW.
#: `preexec_fn` is arbitrary caller code that CPython runs in the forked child, after `fork` and
#: before `exec` -- which is to say inside an already-armed process, holding this thread's
#: `_ApprovedLaunch` stack by inheritance, at the one moment an approval for the launch in progress
#: is outstanding. So it is not merely "a callback": it is the only place in `subprocess` where a
#: caller gets to run between a ticket being issued and the ticket being spent, and round 9's
#: finding is that a launch from there was matched on argv alone. Binding the ticket to the FILE
#: closes the matching hole; this reason closes the construct, because the guarantee it costs is not
#: worth what it buys. CPython's own documentation calls `preexec_fn` unsafe in the presence of
#: threads (and it is disabled outright in subinterpreters), the launch it wants can always be
#: spelled with `cwd`/`env`/`start_new_session`/`pass_fds`, and no non-test file in this repository
#: passes it -- measured with `git grep -n preexec_fn -- '*.py'`, whose only hit was this module's
#: own prose. It is refused AT the `Popen` hook rather than inside the scan so that the test-only
#: static-scan knob cannot swallow it: the knob exists to hand a REFUSED argv on to the restricted
#: shell, and there is no shell reading in this refusal to hand anywhere.
LAUNCH_REASON_PREEXEC = "a-preexec-fn-runs-caller-code-inside-this-guards-approval-window"

#: ROUND 10's REASON, AND IT NAMES THE CONSUME SITE RATHER THAN THE SCAN. Round 10's reviewer keyed
#: on the field round 9's ticket does NOT carry: the environment. The identity is `(argv, file)`,
#: and on the ticket path both consume sites used to hand the CALLER's own environment straight to
#: the child -- never read by `_environment_reaching_child_is_armed`, never repaired by
#: `_rearm_launch_environment`. So an in-window call (`stdout.fileno()` from `Popen._get_handles`,
#: same thread, approval outstanding) matching BOTH halves of the key while stripping only
#: `MNV_GUARD_*` and `PYTHONPATH` started an UNGUARDED interpreter on the approved argv and the
#: approved file: the wrong tree loaded, exit 0, no refusal recorded. That is round 9's class
#: exactly, one field over.
#:
#: WHY IT IS NOT `LAUNCH_REASON_ENV`, WHICH NAMES THE SAME MISSING VARIABLE. They are about the same
#: CONTRACT and a different CLAIM, and the difference is what a reader of a record needs:
#: `LAUNCH_REASON_ENV` says "the scan READ this launch and its argv or environment strips the
#: contract", i.e. the launch as written is wrong. THIS one says "a layer above scanned and APPROVED
#: this argv and this file, and the environment that arrived at the consume site is not the armed
#: one the approval was issued around", i.e. something got in BETWEEN the two layers. A record
#: carrying the first reason sends a reader to the caller's argv; this one sends them to the window.
#: They share an `outcome` for the reason `LAUNCH_REASON_KERNEL_FLOOR` shares one -- see
#: `LAUNCH_OUTCOMES`.
#:
#: THE ENVIRONMENT IS CHECKED AND NOT ADDED TO THE IDENTITY, which is the reviewer's own remedy and
#: the only one of the two that cannot backfire. A check cannot reintroduce a false refusal, because
#: a correct launch's environment already IS the armed one; a third key half would make every layer
#: that legitimately RE-SPELLS an environment a mismatch (`Popen._posix_spawn`'s
#: `if env is None: env = os.environ`, the floor's `NAME=VALUE` bytes round-trip, and
#: `_restricted_shell_environment`'s rebuild), and a mismatch is invisible in every refusal arm
#: because it only ever makes the lower layer scan MORE -- which is how the ticket came to exist.
LAUNCH_REASON_TICKET_ENV = "an-approved-launch-whose-child-environment-is-not-the-armed-one"


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

#: Shells this guard MODELS: their option grammar is parsed, their `-c` string is scanned, their
#: SCRIPT FILE OPERAND IS READ AND SCANNED WITH THE SAME SCANNER -- and, since round 7, the launch
#: is REWRITTEN to run the pinned real bash in restricted mode. `zsh` LEFT THIS SET when the rewrite
#: arrived and the reason is the rewrite: a `zsh -f` program admitted by the static scan would then
#: have to run under `bash -r`, which is a different language, or under zsh with no restricted mode
#: this guard models. Neither is a shell whose enforcement can be stated, so zsh joins the refused.
_SHELL_BASENAMES = frozenset({"sh", "bash", "dash"})

#: The two of the three whose requested semantics are POSIX. They are rewritten to `bash -r --posix`
#: so the program keeps the dialect it was written for while the enforcement is bash's own.
_POSIX_SHELL_BASENAMES = frozenset({"sh", "dash"})

#: Shells that are RECOGNISED AS SHELLS AND REFUSED, which is not the same as being unknown. Their
#: option grammars, startup-file rules and restricted modes differ from the three above in ways this
#: file does not model, and the fail-closed rule is that a shell whose grammar is unmodelled cannot
#: be read -- naming them keeps a reader from concluding that `csh` simply was not thought of.
_UNMODELLED_SHELL_BASENAMES = frozenset({"zsh", "ksh", "ksh93", "mksh", "pdksh", "fish", "csh",
                                         "tcsh", "rc", "es", "xonsh", "elvish", "nu"})

#: `c` is in the set because a cluster is what carries it -- `bash -ec <string>` is the spelling a
#: launcher uses, and a table that listed every OTHER short flag but not `c` refused exactly the
#: invocations it was written to read (measured on `bash -c` itself).
_SHELL_FLAG_CHARS = "abcCefhklmnprtuvxBDPT"
#: THE SHORT FLAGS THAT REFUSE, and each for a different reason a reader should not have to guess:
#: `-l` runs the login startup files, `-i` runs the interactive ones, and `-s` reads the program
#: from STDIN. In all three cases a program this guard cannot read runs before -- or instead of --
#: the one it was handed, so there is nothing to scan.
_SHELL_REFUSING_FLAG_CHARS = "ils"
_SHELL_VALUE_OPTIONS = frozenset({"-o", "+o", "-O", "+O"})

#: `set -o` NAMES AND `shopt -O` NAMES THIS GUARD MODELS, and the value of one of these options is
#: no longer SKIPPED. Skipping it was the fail-open shape `_parse_env` was rebuilt for one level up:
#: `-o` can name an option that undoes the restriction the rewrite installs, and a parser that walks
#: past the value cannot tell `-o errexit` from `-o privileged`. Everything not listed refuses, so
#: adding one is a deliberate edit with a control rather than a silent widening.
_SHELL_MODELLED_SET_O_OPTIONS = frozenset({
    "errexit", "nounset", "pipefail", "xtrace", "verbose", "noglob", "noclobber", "notify",
    "errtrace", "functrace", "monitor", "hashall", "braceexpand", "onecmd", "physical",
})
_SHELL_MODELLED_SHOPT_OPTIONS = frozenset({
    "extglob", "globstar", "nullglob", "dotglob", "failglob", "nocasematch", "nocaseglob",
    "inherit_errexit", "lastpipe", "huponexit", "checkwinsize", "expand_aliases", "xpg_echo",
})
#: The shopt name that IS the restriction. `bash -O restricted_shell` / `+O restricted_shell` is the
#: one spelling that could ask the rewrite to undo itself, so it is refused by name rather than by
#: falling off the modelled list -- a reader who sees the refusal should see WHY.
_SHOPT_RESTRICTED_SHELL = "restricted_shell"
#: `--rcfile`/`--init-file` NAME A STARTUP FILE THIS GUARD DOES NOT READ, so they refuse rather than
#: consume their value. They were previously in `_SHELL_VALUE_OPTIONS`, which skipped the value and
#: left the startup file unexamined.
_SHELL_REFUSING_VALUE_OPTIONS = frozenset({"--rcfile", "--init-file"})
_SHELL_FLAG_LONG = frozenset({"--noprofile", "--norc", "--posix", "--noediting",
                              "--verbose", "--debugger", "--restricted"})
_SHELL_REFUSING_LONG = frozenset({"--login", "--interactive"})

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

#: WHERE THE REAL bash IS LOOKED FOR, first found wins. `install()` pins one of these and its
#: sha256, and every admitted shell launch is rewritten to run THAT file with `-r`. The list is a
#: constant rather than a `PATH` lookup on purpose: the shell that enforces the restriction must not
#: be chosen by the same `PATH` the restriction exists to control. No bash under any of them means
#: the dynamic half cannot be armed, and then every shell launch refuses -- see `_resolve_real_bash`.
_REAL_BASH_CANDIDATES = (
    "/bin/bash", "/usr/bin/bash", "/usr/local/bin/bash", "/opt/homebrew/bin/bash",
)

#: THE ENVIRONMENT VARIABLES A RESTRICTED SHELL MAY NOT CARRY, and each is a program or a lookup it
#: would otherwise run or consult before the guard sees anything. `SHELLOPTS`/`BASHOPTS` are applied
#: at startup and can re-enable what `-r` disables; `BASH_ENV`/`ENV` name a startup file; `CDPATH`
#: makes a literal `cd` operand resolve somewhere the static scan did not model; `BASH_FUNC_*` is an
#: exported shell FUNCTION, so a name the scan read as `ls` runs the caller's code; `LD_PRELOAD`,
#: `DYLD_INSERT_LIBRARIES` and `DYLD_LIBRARY_PATH` inject code into every child; `PYTHONHOME` and
#: `PYTHONEXECUTABLE` change which interpreter and which standard library a Python child gets.
_RESTRICTED_SHELL_STRIPPED_ENV_VARS = (
    "SHELLOPTS", "BASHOPTS", "BASH_ENV", "ENV", "CDPATH", "LD_PRELOAD",
    "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH", "PYTHONHOME", "PYTHONEXECUTABLE",
)
_RESTRICTED_SHELL_STRIPPED_ENV_PREFIXES = ("BASH_FUNC_",)

#: THE SAME QUESTION AT THE OTHER WRAPPER. A restricted child cannot carry these -- they are
#: stripped above -- but `bin/python3` is also reached from an admitted NON-SHELL child, which was
#: never handed a restricted environment. `PYTHONHOME` and `PYTHONEXECUTABLE` decide which stdlib
#: and which binary the interpreter uses, and the two library-injection variables run code before
#: `sitecustomize` does, so a wrapper that execs the interpreter with any of them set would be
#: standing in front of a launch it did not read.
_WRAPPER_HOSTILE_ENV_VARS = (
    "PYTHONHOME", "PYTHONEXECUTABLE", "LD_PRELOAD", "DYLD_INSERT_LIBRARIES",
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
    LAUNCH_REASON_KERNEL_FLOOR: ("THIS CALL AT THE _posixsubprocess.fork_exec FLOOR CANNOT BE "
                                 "READ, SO IT CANNOT BE SCANNED"),
    LAUNCH_REASON_PREEXEC: ("preexec_fn RUNS CALLER CODE IN THE FORKED CHILD, INSIDE THIS "
                            "GUARD'S OWN LAUNCH APPROVAL"),
    LAUNCH_REASON_TICKET_ENV: ("AN APPROVED LAUNCH WOULD START ITS CHILD WITHOUT THE PROPAGATION "
                               "CONTRACT"),
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
    LAUNCH_REASON_KERNEL_FLOOR: ("_posixsubprocess.fork_exec is the last Python-visible layer "
                                 "before the kernel, and this guard hooks it so that a caller "
                                 "which skips subprocess, os.exec* and os.spawn* is scanned "
                                 "anyway. The call it was handed does not have the shape this "
                                 "interpreter's fork_exec documents -- no argument vector, an "
                                 "empty executable_list, or an environment member that is not "
                                 "NAME=VALUE -- so the executable, the argv or the propagation "
                                 "contract reaching the child cannot be read. Route the launch "
                                 "through subprocess or os.posix_spawn, whose argv positions this "
                                 "guard can also repair."),
    LAUNCH_REASON_PREEXEC: ("preexec_fn is called IN THE FORKED CHILD, between fork and exec: "
                            "arbitrary caller code running inside a process this guard has "
                            "already armed, holding this thread's launch approval by "
                            "inheritance, at the one instant an approval for the launch in "
                            "progress is outstanding. Code reached there can fork again, execve "
                            "directly or unwind this guard's state, and none of that is readable "
                            "from an argv. CPython's own documentation calls preexec_fn unsafe in "
                            "the presence of threads. Spell the intent with cwd=, env=, "
                            "start_new_session=, pass_fds= or umask= -- all of which this layer "
                            "sees -- or do the work in the parent before the launch."),
    LAUNCH_REASON_TICKET_ENV: ("A layer above scanned THIS argv and THIS file and handed the launch "
                               "down as an approved ticket, and the environment that arrived with "
                               "it at the consume site is not the armed one: a MNV_GUARD_* "
                               "variable is missing or holds a value other than this process's, or "
                               "PYTHONPATH's first entry is not the shim directory. The ticket "
                               "certifies the argv and the file and NOTHING ELSE -- it never "
                               "certified the environment -- so the environment reaching the child "
                               "is checked here rather than trusted, and a child that would start "
                               "without the contract is refused exactly as the scan refuses one. "
                               "An absent environment is NOT this state: at these layers None "
                               "means inherit, and what the child inherits is this armed process's "
                               "own os.environ. Pass the environment the layer above armed and "
                               "wrote back, or make the launch through a public primitive, which "
                               "re-arms an explicit env= before it scans."),
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
    #: THE FLOOR SHARES THE SECOND OUTCOME for the reason the paragraph above gives: "this guard
    #: could not establish that this launch stays guarded" is the same claim to a ratchet reader
    #: whether the obstacle was an unmodelled option or an unreadable call at the kernel floor. The
    #: `reason` field carries which.
    LAUNCH_REASON_KERNEL_FLOOR: "refused:launch-unmodelled-launch-grammar",
    #: AND SO DOES `preexec_fn`, for the same reason once more: a construct whose contents this
    #: guard cannot read is a launch whose coverage it could not establish. It is not the FLAGS
    #: outcome, which would tell a ratchet reader that a startup flag was found -- nothing was
    #: scanned here at all.
    LAUNCH_REASON_PREEXEC: "refused:launch-unmodelled-launch-grammar",
    #: ROUND 10's REASON TAKES THE **FIRST** OUTCOME, and that is the one place it differs from the
    #: three above it. Nothing was unreadable here: the layer above READ this launch, and what this
    #: refusal reports is that the child would start without the propagation contract -- which is
    #: the claim `LAUNCH_REASON_ENV` already carries to a ratchet reader, and the same remedy. The
    #: `reason` field is what says the contract went missing BETWEEN the two layers rather than in
    #: the caller's own argv.
    LAUNCH_REASON_TICKET_ENV: "refused:launch-python-startup-flags",
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

    ROUND 7 ADDED THE OTHER THREE KEYS, AND THEY ARE WHAT THE REWRITE IS BUILT FROM. `options` is
    the caller's option tokens THAT SURVIVE -- `-e`, `-u`, `-o pipefail` -- with `-c` and `-r`
    removed, because the rewrite re-emits those itself; `posix` says the requested shell was `sh` or
    `dash` (or asked for `--posix`), which becomes `bash -r --posix`; `args` is everything after the
    `-c` string or the script operand, which is the child program's own `$0`/`$@` and is forwarded
    verbatim. A parse that dropped them would silently change what the program computes, and a
    guard that changes a result is worse than one that refuses.

    THE REFUSALS ARE ALL ONE SHAPE: a shell program would run, or a restriction would not hold, that
    this guard was not handed. `-l`/`--login` and `-i`/`--interactive` run startup files;
    `--rcfile`/`--init-file` name one; `-s` and a bare invocation read the program from STDIN, which
    does not exist at scan time; `$BASH_ENV`/`$ENV` in the child's environment name one that runs
    before the script's first line; `+r` and `-O restricted_shell` ask for the restriction the
    rewrite installs to be absent; and an `-o`/`-O` value this file does not model may be any of
    those under a name nobody read.
    """
    basename = _executable_basename(_text_argument(argv[0]))
    source = os.environ if env is None else env
    for name in _SHELL_STARTUP_ENV_VARS:
        if source.get(name):
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                 f"${name} names a shell startup file this guard cannot read")
    index = 1
    options_done = False
    options: list[str] = []
    posix = basename in _POSIX_SHELL_BASENAMES
    while index < len(argv):
        token = argv[index]
        if token == "--":
            options_done = True
            index += 1
            break
        if token == "-" or not token.startswith(("-", "+")):
            break
        if token in _SHELL_REFUSING_VALUE_OPTIONS or token in _SHELL_REFUSING_LONG:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, token)
        if token.startswith("--") and token.partition("=")[0] in _SHELL_REFUSING_VALUE_OPTIONS:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, token)
        if token in _SHELL_VALUE_OPTIONS:
            if index + 1 >= len(argv):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{token} with no value")
            value = argv[index + 1]
            _refuse_an_unmodelled_shell_option_value(token, value)
            if value == "posix":
                posix = posix or token == "-o"
            options.extend([token, value])
            index += 2
            continue
        if token in _SHELL_FLAG_LONG:
            if token == "--posix":
                posix = True
            if token != "--restricted":      # the rewrite emits `-r` itself; never twice
                options.append(token)
            index += 1
            continue
        if token.startswith("--"):
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        cluster = token[1:]
        if token.startswith("+"):
            #: `+r` IS THE ONE SPELLING THAT ASKS FOR THE RESTRICTION NOT TO HOLD. Every other `+`
            #: cluster is an option this file does not model, and both refuse -- but they refuse
            #: with different words, because a reader of `+r` must not go looking for a table.
            if "r" in cluster:
                raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                                     f"{token} turns off the restricted mode every admitted shell "
                                     f"launch is rewritten to run under")
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        refusing = [c for c in cluster if c in _SHELL_REFUSING_FLAG_CHARS]
        if refusing:
            raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN, f"{token} (-{refusing[0]})")
        if not set(cluster) <= set(_SHELL_FLAG_CHARS):
            raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, token)
        surviving = "".join(c for c in cluster if c not in "cr")
        if "c" in cluster:
            if index + 1 >= len(argv):
                raise _LaunchRefusal(LAUNCH_REASON_UNPARSED, f"{token} with no command string")
            if surviving:
                options.append(f"-{surviving}")
            return {"kind": "string", "text": argv[index + 1], "options": options,
                    "posix": posix, "args": list(argv[index + 2:])}
        if surviving:
            options.append(f"-{surviving}")
        index += 1
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
    return {"kind": "script", "path": operand, "options": options, "posix": posix,
            "args": list(argv[index + 1:])}


def _refuse_an_unmodelled_shell_option_value(option: str, value: str) -> None:
    """`-o`/`+o`/`-O`/`+O`'s VALUE, checked instead of skipped.

    THE PREDECESSOR SKIPPED IT, which is the same shape as an unmodelled `env` option whose value is
    the command word: the parse walked past a token that decides what the shell does. `-o` names a
    `set` option and `-O` a `shopt`, and one of those names IS the restriction -- `restricted_shell`
    -- so the value is where a launch would ask the rewrite to undo itself.
    """
    if value == _SHOPT_RESTRICTED_SHELL:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"{option} {value} toggles the restricted mode every admitted shell "
                             f"launch is rewritten to run under")
    modelled = (_SHELL_MODELLED_SET_O_OPTIONS if option in ("-o", "+o")
                else _SHELL_MODELLED_SHOPT_OPTIONS)
    if value == "posix" and option in ("-o", "+o"):
        return
    if value not in modelled:
        raise _LaunchRefusal(LAUNCH_REASON_UNMODELLED, f"{option} {value}")


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
    wrappers: list[str] = []
    for _ in range(_MAX_WRAPPER_DEPTH):
        name = _executable_basename(_resolve_executable(command[0], env))
        if name in _ENV_BASENAMES:
            wrappers.append(name)
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
            wrappers.append(name)
            index = _parse_wrapper(command, spec)
            if index is None:
                return None
            offset = None if offset is None else offset + index
            command = command[index:]
            continue
        return {"command": command, "inject_at": offset, "clears": clears,
                "stripped": stripped, "assignments": assignments, "unset": unset,
                "wrappers": wrappers}
    raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                         f"launch wrappers nested deeper than {_MAX_WRAPPER_DEPTH}")


def _refuse_an_unreadable_wrapper_prefix(tokens: list, resolved: dict, context: _ScanContext
                                         ) -> None:
    """The wrapper prefix's own tokens, and `xargs`'s command. Round 7, part of C(2).

    A WRAPPER PREFIX IS ALL DECISION AND NO DATA. `timeout "$T" python3 x.py`, `nice "$N" python3`,
    `env "$A" python3` -- every token before the command word either IS an option or is the value of
    one, and an option's value can be the command word (that is the whole reason `_parse_env` is
    fail-closed). So a token built at run time anywhere in the prefix means the walk that found the
    command word read a token nobody can predict, and the command word it landed on is a guess.

    `xargs` IS SEPARATE AND STRICTER: it APPENDS words read from its standard input to the command,
    so its child's argv is built at run time BY CONSTRUCTION, whatever the argv says. That is
    harmless for a leaf tool -- `xargs rm` gets more files -- and it is the reviewer's finding for
    anything else, because `xargs python3` gets a SCRIPT nobody read.
    """
    if context.in_shell:
        stop = resolved["inject_at"]
        _refuse_runtime_tokens(tokens, "launch wrapper token", stop=stop)
    if "xargs" not in resolved.get("wrappers", ()):
        return
    head = _executable_basename(_text_argument(resolved["command"][0]))
    if head not in _LEAF_TOOL_BASENAMES:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"xargs appends words read at run time to `{head}`, so the argv this "
                             f"scan read is not the argv that runs; only a leaf tool may be run "
                             f"that way")


def _contract_operands(resolved: dict, restricted_shell: bool = False
                       ) -> "tuple[list[str], dict]":
    """The `NAME=VALUE` operands that re-arm an `env` launch, and the environment they produce.

    THE OPERANDS ARE THE ARGV SPELLING OF `_rearm_launch_environment`, and they are inserted rather
    than substituted: `env` applies assignments in order and the LAST one wins, so appending the
    contract in front of the command word repairs `-i`, `-u MNV_GUARD_MODULE` and an explicit
    `PYTHONPATH=...` alike while leaving every other operand the caller wrote exactly where it was.

    PATH IS DELIBERATELY NOT RESTORED FOR AN INTERPRETER. `env -i` clears it, and putting it back
    would overrule the caller on something that is not this guard's contract -- the interpreter
    itself needs no PATH. What is lost is the PATH-wrapper half for that child's own descendants --
    the SECOND chance to refuse, not the coverage: the closed child model reads what the child will
    run before it starts, so a cleared PATH costs redundancy rather than opening a route. This was
    the `clears PATH or the environment` arm of the pre-round-6 `DECLARED_GAP`, and it is not one.

    `restricted_shell` IS THE ONE CASE WHERE IT MUST BE, and the reason is that PATH stops being the
    caller's business there. An admitted shell is rewritten to run under `bash -r` with a PATH that
    is the guard's wrapper directories and nothing else -- that PATH is not a convenience, it is the
    enforcement -- so an `env -i` in front of it has to be repaired with the PATH as well as with
    the contract, or the restricted shell starts with no PATH at all and every line of a correct
    program is `command not found`.

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
    if restricted_shell:
        wrapper_path = os.environ.get(PATH_SHIM_DIRS_ENV) or str(PATH_SHIM_DIR.resolve())
        operands.append(f"PATH={wrapper_path}")
        view["PATH"] = wrapper_path
        for name in PATH_HALF_ENV_VARS:
            value = os.environ.get(name)
            if value is not None:
                operands.append(f"{name}={value}")
                view[name] = value
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
    return shutil.which(text, path=_path_without_shim_dirs(path_value)) or text


def _locate_command_word(word: str, env, context: "_ScanContext") -> str:
    """Where a command word will be FOUND, honouring the launch's working directory.

    MEASURED, NOT ANTICIPATED: `subprocess.run(["./stage.sh"], cwd=<dir>)` from a guarded parent
    resolved `./stage.sh` against THIS process's cwd, found nothing, and refused the launch for
    having no readable shebang -- a refusal that is fail-closed and also about the wrong file, which
    is the class of error where a check is right about an object nobody asked about. A word with a
    separator in it is a PATH and is resolved against the launch's cwd (and then the directory of
    the other candidate working directories, for the reason on `_scan_every_resolution`); a bare
    word is a PATH
    lookup and `_locate_executable` owns it.
    """
    if os.sep in word and not os.path.isabs(word):
        for base in _candidate_directories(context):
            candidate = os.path.join(base, word)
            if os.path.exists(candidate):
                return candidate
    return _locate_executable(word, env)


def _candidate_directories(context: "_ScanContext") -> list:
    """Every directory a relative operand of this scan may be resolved against, launch cwd first.

    The launch's own working directory leads because it is the one the shell starts in; the rest are
    what `cd` added and the directories of the scripts this scan has opened. Order matters only for
    the diagnostics -- every entry is tried and every hit is scanned.
    """
    ordered = [context.cwd] if context.cwd else []
    for path in sorted(context.dirs.paths):
        if path not in ordered:
            ordered.append(path)
    if context.script_dir and context.script_dir not in ordered:
        ordered.append(context.script_dir)
    return ordered


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


class _CandidateDirectories:
    """THE SET OF DIRECTORIES A RELATIVE OPERAND MIGHT BE RESOLVED AGAINST. Round 7, finding 3.

    THE FINDING THIS EXISTS FOR, VERBATIM: "A preceding cd can make the scanner inspect the wrong
    script. :2448 explicitly does not model cd. With a benign child.sh in the launch directory and a
    malicious one under sub/: `cd sub` / `bash child.sh` -- the guard scanned the benign file; the
    shell executed the malicious file." The predecessor resolved an operand against ONE directory
    and then, when that missed, against the scanned script's own directory -- two guesses, neither
    of them the shell's answer, and the first of them was a file that existed.

    A SET AND NOT A VARIABLE, AND IT ONLY GROWS. `cd` inside an `if` happens on one branch and not
    on the other, and this scan does not model conditional structure -- so BOTH the directory before
    the `cd` and the one after it are directories the operand may be resolved against, and the
    fail-closed reading is that every one of them is read and scanned. `popd` therefore adds nothing
    and removes nothing: removing would shrink the set on the strength of structure nobody modelled.

    UNKNOWN IS A THIRD STATE AND NOT AN EMPTY SET. `cd "$D"`, `cd` with no operand (`$HOME`), `cd -`
    (`$OLDPWD`), `cd ~user`, and `CDPATH` anywhere all make the shell's working directory something
    decided after this scan ends. An empty set would make every relative operand "not found", which
    reads as a file that is absent; `known = False` makes it a REFUSAL that names the construct.
    """

    __slots__ = ("known", "paths", "why")

    def __init__(self, start: str):
        self.known = True
        self.why = ""
        self.paths = {_realpath_or_self(start)}

    def add(self, path: str) -> None:
        self.paths.add(_realpath_or_self(path))

    def mark_unknown(self, why: str) -> None:
        self.known = False
        self.why = self.why or why


class _ProgramFileUses:
    """Every path a shell PROGRAM writes, and every path it runs. Round 7's write-then-execute rule.

    TWO SETS AND A LATE CHECK, because the order of the lines does not bound the defect. A script
    that writes `stage.sh` on line 3 and runs it on line 9 is the obvious spelling; one that runs it
    on line 3 and writes it on line 9 is the same program the second time round, and a scan that
    only looked backwards would read the first run and never the second. So both sets are collected
    over the WHOLE program -- sourced files included, because they are the same program -- and the
    intersection is taken once, at the end, by `_refuse_write_then_execute`.

    `runtime_target` IS THE OTHER HALF. A write whose target is `$OUT` names a path this scan cannot
    compare with anything, so the intersection is empty for the wrong reason. Paired with ANY
    relative script or `source` operand it is a refusal: the operand's identity is decided by the
    directory, the target's by the expansion, and nothing here can rule out that they meet.
    """

    __slots__ = ("written", "runtime_target", "executed", "relative_executed")

    def __init__(self):
        self.written: set[str] = set()
        self.runtime_target: "str | None" = None
        self.executed: set[str] = set()
        self.relative_executed: list[str] = []


def _realpath_or_self(path: str) -> str:
    """`os.path.realpath`, and the input back when the filesystem will not answer.

    EVERY RESOLUTION IS REALPATHED, so a symlink that points out of the candidate set is still
    scanned BY ITS TARGET rather than by the name that reached it -- the bytes that run are the
    target's. A failure here is not a refusal on its own: the caller decides, and it decides on
    whether the file exists, which is a question this function does not answer.
    """
    try:
        return os.path.realpath(path)
    except OSError:
        return path


class _ScanContext:
    """The state a scan carries across nesting: where it is, how deep, and what it has read.

    `defined`, `seen`, `dirs`, `uses` and `rewrite` are SHARED DOWNWARDS AND NOT COPIED,
    deliberately. A function defined in a sourced file is callable in the file that sourced it, so
    the names have to travel; `seen` is what makes `a.sh` sourcing `b.sh` sourcing `a.sh` a refusal
    instead of a hang; `dirs` travels because a `cd` in a sourced file changes the sourcing file's
    working directory too; `uses` travels because a sourced file is part of the same program; and
    `rewrite` travels because the ONE thing the whole scan produces for its caller -- the restricted
    argv the launch is rewritten to -- is decided at the outermost shell and read at the top.

    `in_shell` SAYS WHICH LANGUAGE THE TOKENS CAME FROM, and it is not cosmetic. A `$` inside a
    shell program is an expansion and is refused wherever it could select a program or an option; a
    `$` inside an argv element is the character `$` and refusing it would refuse
    `subprocess.run(["python3", "x.py", "$MODE"])`, which launches nothing this guard cannot see.
    """

    __slots__ = ("cwd", "depth", "defined", "seen", "script_dir", "dirs", "uses", "in_shell",
                 "rewrite")

    def __init__(self, cwd: str, depth: int = 0, defined=None, seen=None, script_dir=None,
                 dirs=None, uses=None, in_shell=False, rewrite=None):
        self.cwd = cwd
        self.depth = depth
        self.defined: set[str] = set() if defined is None else defined
        self.seen: set[str] = set() if seen is None else seen
        self.script_dir = script_dir
        self.dirs = _CandidateDirectories(cwd) if dirs is None else dirs
        self.uses = _ProgramFileUses() if uses is None else uses
        self.in_shell = in_shell
        #: A ONE-SLOT BOX AND NOT A PLAIN ATTRIBUTE, so that a nested context writing the rewrite is
        #: visible to the outermost one that has to return it. `_ScanContext` is copied at every
        #: `deeper()`, and a copied attribute would leave the top-level caller reading its own None.
        self.rewrite: list = [] if rewrite is None else rewrite

    def deeper(self, script_dir=None, in_shell=None) -> "_ScanContext":
        if self.depth >= _MAX_WRAPPER_DEPTH:
            raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                                 f"shell programs nested deeper than {_MAX_WRAPPER_DEPTH}")
        return _ScanContext(self.cwd, self.depth + 1, self.defined, self.seen,
                            script_dir if script_dir is not None else self.script_dir,
                            self.dirs, self.uses,
                            self.in_shell if in_shell is None else in_shell,
                            self.rewrite)

    def record_rewrite(self, argv: list) -> None:
        """The restricted argv for the OUTERMOST admitted shell. Written once and never replaced.

        The outermost is the one that runs: `bash a.sh` where `a.sh` runs `bash b.sh` is one launch
        this process makes and one this guard rewrites, and `b.sh`'s own launch is made by the
        restricted shell through the committed `bin/bash` wrapper rather than by this code.
        """
        if not self.rewrite:
            self.rewrite.append(argv)


#: Shell builtins and reserved words that RUN NO PROGRAM NAMED BY THEIR ARGUMENTS. They are listed
#: rather than pattern-matched because each one that is missing refuses a correct script and each one
#: wrongly present admits an unscanned launch. `eval`, `exec`, `source`, `.`, `command`, `alias`,
#: `hash`, `trap`, `export`, `unset`, `declare`, `typeset` and `readonly` are NOT here: every one of
#: them either runs something or changes what a later name resolves to, and each has its own handler.
#: `local` IS DELIBERATELY NOT HERE even though it looks like `declare`: it is handled by
#: `_SHELL_DECLARING_BUILTINS`, because the inert check runs FIRST and `local PATH=/usr/bin` inside a
#: function changes PATH for every command that function calls. A name in both tables is admitted by
#: the first, which is how a declaring builtin becomes a fail-open by being listed twice.
#: `cd` AND `pushd` LEFT THIS TABLE IN ROUND 7 for the same reason `local` never joined it. They run
#: no program, so "inert" was true of what they EXECUTE and false of what they DECIDE: they change
#: which file a later relative operand names, which is finding 3. `popd` stays, because the
#: candidate set only grows and popping removes nothing from it.
_SHELL_INERT_BUILTINS = frozenset({
    ":", "true", "false", "pwd", "popd", "dirs", "echo", "printf", "read", "set",
    "shopt", "shift", "umask", "ulimit", "wait", "return", "break", "continue", "exit", "logout",
    "let", "test", "[", "[[", "getopts", "jobs", "fg", "bg", "kill", "disown", "suspend", "times",
    "type", "help", "history", "bind", "complete", "compgen", "compopt", "caller", "mapfile",
    "readarray",
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
#: `export -n NAME` UN-EXPORTS a variable, which removes it from every later child's environment --
#: the same effect as `unset` from a child's point of view, and it is not an assignment, so the
#: assignment rule alone would wave it through.
_SHELL_UNEXPORT_OPTIONS = frozenset({"-n"})

#: `NAME=VALUE` and `NAME+=VALUE` in command position. A regex rather than `partition("=")` because
#: the append form has to be recognised AS AN ASSIGNMENT: `partition` gives the name `PATH+`, which
#: matches no protected name, so `PATH+=/tmp/bin` read as a command word and refused for the wrong
#: reason.
_SHELL_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(\+?)=(.*)$", re.DOTALL)

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


#: `git` SUBCOMMANDS WHOSE OPERANDS AFTER A LITERAL `--` SELECT NO PROGRAM AND NO OPTION. This is
#: the one exemption from round 7's runtime-token rule, and it exists because it is the shape the
#: campaign's provenance code is written in: `git rev-parse "$REF"`, `git cat-file -p "$BLOB"`,
#: `git ls-files -- "$PATHSPEC"`. None of these subcommands has ANY option that names a program, so
#: an expansion in an operand can change WHICH object is read and never WHAT runs. `log`, `show`,
#: `diff`, `diff-index`, `diff-tree` and `diff-files` are DELIBERATELY ABSENT: each takes
#: `--ext-diff`, `--pager` or an `-c` override, so an expanded operand there can select a program.
_GIT_LITERAL_OPERAND_SUBCOMMANDS = frozenset({
    "rev-parse", "ls-files", "hash-object", "cat-file", "merge-base", "rev-list", "describe",
    "name-rev", "for-each-ref", "symbolic-ref", "check-ignore", "status",
})


def _is_a_word_built_at_runtime(word: str) -> bool:
    """Whether `_refuse_a_word_built_at_runtime` would refuse `word`. One rule, two questions."""
    try:
        _refuse_a_word_built_at_runtime(word, "word")
    except _LaunchRefusal:
        return True
    return False


def _refuse_runtime_tokens(tokens, role: str, *, start: int = 0, stop: "int | None" = None) -> None:
    """Refuse an expansion anywhere in `tokens[start:stop]`. Round 7, finding 2.

    THE FINDING THIS EXISTS FOR, VERBATIM: "Shell-expanded Python flags bypass the static scan.
    :2655 rejects runtime-built command words, but not runtime-built arguments. `FLAG=-I` /
    `/usr/bin/python3 "$FLAG" child.py`. This also ran successfully outside the shim contract with
    no refusal or child record." The predecessor asked its question of ONE token -- the command word
    -- on the theory that the word is the answer. It is not: an interpreter's OPTIONS decide whether
    the shim installs, a wrapper's options decide which word is the command, and `sbatch`'s decide
    which file is the batch script. Every one of those is a token whose expansion selects a program
    or an option, and every one of them is refused here.

    WHAT IS DELIBERATELY NOT COVERED, because the tokens after it are DATA rather than a decision: a
    script's own argv (`python3 x.py "$@"`), a leaf tool's operands (`ls "$DIR"`), and the operands
    of the `git` subcommands in `_GIT_LITERAL_OPERAND_SUBCOMMANDS`. Refusing those would refuse
    correct launchers over an expansion that cannot reach an interpreter.
    """
    for token in tokens[start:len(tokens) if stop is None else stop]:
        _refuse_a_word_built_at_runtime(token, role)


def _refuse_runtime_python_tokens(command: list) -> None:
    """Every token of a Python launch up to AND INCLUDING its first operand must be literal.

    THE WALK IS CPYTHON'S OWN OPTION GRAMMAR, the same one `_forbidden_python_flag` follows and for
    the same reason: the boundary between "an option this guard must read" and "the child program's
    own argv" is decided by that grammar and by nothing else. `python3 x.py "$@"` is a script with
    arguments and is admitted; `python3 "$@"` is an interpreter whose SCRIPT is chosen at run time
    and is refused; `python3 -m "$MOD"` and `python3 -c "$CODE"` are the same defect spelled with an
    option's value.
    """
    _refuse_a_word_built_at_runtime(command[0], "interpreter path")
    index = 1
    while index < len(command):
        argument = command[index]
        _refuse_a_word_built_at_runtime(argument, "python interpreter option")
        index += 1
        if argument in ("-", "--"):
            return
        if not argument.startswith("-"):
            return                           # the script operand: everything after it is its argv
        if argument.startswith("--"):
            if argument in _VALUE_TAKING_LONG_FLAGS and index < len(command):
                _refuse_a_word_built_at_runtime(command[index], "python option value")
                index += 1
            continue
        cluster = argument[1:]
        for position, character in enumerate(cluster):
            if character in _PROGRAM_ENDING_SHORT_FLAGS:
                if position == len(cluster) - 1 and index < len(command):
                    #: `-c CODE` and `-m MODULE`: the VALUE is what runs, so it is the operand this
                    #: rule is about, and every token after it belongs to the child program.
                    _refuse_a_word_built_at_runtime(command[index], "python -c/-m value")
                return
            if character in _VALUE_TAKING_SHORT_FLAGS:
                if position == len(cluster) - 1 and index < len(command):
                    _refuse_a_word_built_at_runtime(command[index], "python option value")
                    index += 1
                break


def _refuse_runtime_git_tokens(command: list) -> None:
    """Every token of a `git` launch, except the operands a literal-operand subcommand takes.

    The allowlist over subcommands is worth nothing if an expansion can supply a global option --
    `git "$G" status` where `$G` is `-c core.pager=...` is the whole allowlist defeated in one
    token -- so the walk to the subcommand is literal-only, and so is the subcommand itself.
    """
    _refuse_runtime_tokens(command, "git option", start=0, stop=1)
    index = 1
    while index < len(command):
        token = command[index]
        _refuse_a_word_built_at_runtime(token, "git global option")
        if token == "--":
            index += 1
            break
        if not token.startswith("-"):
            break
        index += 2 if token in _GIT_GLOBAL_VALUE_OPTIONS else 1
    if index >= len(command):
        return
    subcommand = command[index]
    _refuse_a_word_built_at_runtime(subcommand, "git subcommand")
    rest = command[index + 1:]
    if subcommand in _GIT_LITERAL_OPERAND_SUBCOMMANDS:
        #: The operands after a literal `--` name objects and paths, never programs and never
        #: options, so an expansion in them cannot change what runs. Before the `--` an option is
        #: still possible, so those tokens stay literal-only.
        if "--" in rest:
            rest = rest[:rest.index("--")]
        else:
            rest = [token for token in rest if token.startswith("-")]
    _refuse_runtime_tokens(rest, f"git {subcommand} argument")


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
    """Read ONE shell SCRIPT FILE and scan it with the same scanner a `-c` string gets.

    THE WHOLE OF ROUND 6's FIRST FINDING IS THAT THIS FUNCTION DID NOT EXIST. `bash script.sh` was
    admitted unread; the three mutations the reviewer wrote were ordinary shell lines in an ordinary
    file. Nothing about a file makes it less scannable than a string -- `_shell_logical_lines`
    reduces both to the same logical lines, with `#!` and `#SBATCH` inert as the comments they are.

    A CYCLE IS A REFUSAL, not a recursion limit reached the slow way: `a.sh` sourcing `b.sh`
    sourcing `a.sh` is a program whose text this scan cannot enumerate.

    THE SCRIPT'S OWN DIRECTORY JOINS THE CANDIDATE SET. A script that runs `bash helper.sh` beside
    itself is the ordinary shape, and the shell resolves that against its working directory -- which
    this scan does not know exactly and therefore over-approximates. Adding the directory can only
    put more files in front of the scanner.
    """
    resolved = _realpath_or_self(os.path.abspath(path))
    if resolved in context.seen:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"the shell script {resolved} is reached from itself; a cyclic "
                             f"program cannot be read to the end")
    context.seen.add(resolved)
    context.dirs.add(os.path.dirname(resolved))
    inner = context.deeper(script_dir=os.path.dirname(resolved), in_shell=True)
    return _scan_shell_program(_read_shell_script(resolved), env, inner)


def _scan_every_resolution(word: str, env, context: _ScanContext, role: str) -> bool:
    """Read and scan EVERY file a relative shell operand could name. Round 7, finding 3.

    THE PREDECESSOR RETURNED ONE PATH AND THE SHELL RAN ANOTHER. `cd sub` then `bash child.sh` has
    two answers on a tree that holds both `child.sh` and `sub/child.sh`, and the old resolver
    returned the first one that existed -- the benign one, while the shell ran the malicious one.
    There is no way to pick correctly without executing the `cd`, so this picks ALL of them: every
    candidate directory that actually holds the file is read and scanned, and a refusal in any one
    of them refuses the launch. The cost is a launcher refused for a file it was never going to run,
    which is the direction this whole file errs in.

    AN UNKNOWN DIRECTORY SET REFUSES A RELATIVE OPERAND OUTRIGHT. `cd "$D"` means the shell's
    working directory is chosen after this scan ends, so "every file it could name" is unbounded and
    scanning a sample of it would establish nothing.
    """
    if os.path.isabs(word):
        return _scan_shell_script_file(word, env, context)
    if not context.dirs.known:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"the relative {role} {word!r} cannot be resolved: {context.dirs.why}")
    candidates = _candidate_directories(context)
    existing = []
    for base in candidates:
        candidate = os.path.join(base, word)
        if os.path.exists(candidate):
            resolved = _realpath_or_self(candidate)
            if resolved not in existing:
                existing.append(resolved)
    if not existing:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"the {role} {word!r} names no readable file under any candidate "
                             f"working directory ({', '.join(candidates)}), so its launches cannot "
                             f"be scanned")
    launches_python = False
    for resolved in existing:
        if resolved in context.seen:
            continue                         # already read on another candidate's path
        launches_python = _scan_shell_script_file(resolved, env, context) or launches_python
    return launches_python


def _record_script_operand(word: str, context: _ScanContext) -> None:
    """Remember a path this program RUNS, for the write-then-execute check at the end."""
    if os.path.isabs(word):
        context.uses.executed.add(_realpath_or_self(word))
        return
    context.uses.relative_executed.append(word)
    for base in _candidate_directories(context):
        context.uses.executed.add(_realpath_or_self(os.path.join(base, word)))


def _refuse_write_then_execute(context: _ScanContext) -> None:
    """A path this program WRITES and also RUNS is a program this scan did not read. Round 7, C(4).

    THE SCAN READS BYTES THAT ARE NOT THE BYTES THAT RUN. Everything above establishes what a script
    file contains AT SCAN TIME; a line earlier in the same program that copies, moves, links,
    downloads or redirects onto that same path replaces those bytes before the shell reaches them,
    and the scan's answer is then about a file that no longer exists. It is not a race this guard
    can win by re-reading -- the write happens after the launch is admitted -- so the composition is
    refused instead.

    A RUNTIME WRITE TARGET IS THE SAME DEFECT WITH THE PATH HIDDEN. `cp new "$OUT"` names a path
    this scan cannot compare with anything, so the intersection is empty for the wrong reason;
    paired with any relative script or `source` operand, whose identity is also decided later, the
    two cannot be shown apart and the program refuses.
    """
    collision = sorted(context.uses.written & context.uses.executed)
    if collision:
        raise _LaunchRefusal(LAUNCH_REASON_UNPARSED,
                             f"{collision[0]} is both written and run by the same program, so the "
                             f"bytes this scan read are not the bytes that would run")
    if context.uses.runtime_target is not None and context.uses.relative_executed:
        raise _LaunchRefusal(
            LAUNCH_REASON_UNPARSED,
            f"the write target {context.uses.runtime_target!r} is built at run time and the "
            f"program runs the relative script {context.uses.relative_executed[0]!r}; neither path "
            f"is decided at scan time, so they cannot be shown to be different files")


#: COMMANDS WHOSE OPERANDS ARE A WRITE, and WHICH of their operands is one. Each of them can
#: replace a file this scan read -- `cp new stage.sh`, `tee stage.sh`, `sed -i`, `curl -o stage.sh`,
#: `install`, `dd of=stage.sh`, `chmod +x stage.sh`. The list is short and every name on it is a
#: name whose write this file is asserting without reading anything, exactly as
#: `_LEAF_TOOL_BASENAMES` is. A writer NOT on it is covered by the redirection rule or by nothing,
#: and "or by nothing" is why the intersection is not the only control: the restricted shell refuses
#: redirection outright and refuses every command the wrapper directory does not hold.
#:
#: WHICH OPERAND IS THE TARGET IS PER-COMMAND AND IS NOT GUESSABLE, which is why there are four
#: tables rather than one rule. `cp a b c dir` writes the LAST; `tee a b` and `chmod +x a b` write
#: EVERY one; `curl` and `wget` name theirs with an option; `dd` names it with `of=`; and `sed -i`
#: writes every operand EXCEPT the first, because the first is the script expression -- unless `-e`
#: or `-f` supplied the expression, in which case every operand is a file. Reading `sed -i s/a/b/
#: stage.sh` with the wrong rule records `s/a/b/` as a path and `stage.sh` as safe, which is a
#: check that is right about the wrong object.
_WRITER_BASENAMES = frozenset({"cp", "mv", "ln", "install", "tee", "sed", "chmod", "dd", "rsync",
                               "curl", "wget"})
_WRITER_TARGET_OPTIONS = {"curl": ("-o", "--output"), "wget": ("-O", "--output-document")}
_WRITERS_OVER_EVERY_OPERAND = frozenset({"tee", "chmod"})
_WRITERS_OVER_THE_LAST_OPERAND = frozenset({"cp", "mv", "ln", "install", "rsync"})
_SED_IN_PLACE_OPTIONS = ("-i", "--in-place")
_SED_EXPRESSION_OPTIONS = ("-e", "--expression", "-f", "--file")


def _record_write_targets(tokens: list, context: _ScanContext) -> None:
    """Remember every path a simple command WRITES, for `_refuse_write_then_execute`.

    NOT A SECURITY CHECK ON ITS OWN and deliberately not spelled as one: writing a file is what a
    science step does. What it feeds is the COMPOSITION check -- a write and a run of the same path
    -- so a target recorded here costs nothing unless the same program also runs it.
    """
    name = _executable_basename(_text_argument(tokens[0]))
    if name not in _WRITER_BASENAMES:
        return
    options = _WRITER_TARGET_OPTIONS.get(name, ())
    operands: list = []
    in_place = False
    expression_given = False
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in options and index + 1 < len(tokens):
            _record_one_write_target(tokens[index + 1], context)
            index += 2
            continue
        if any(token.startswith(f"{option}=") for option in options):
            _record_one_write_target(token.partition("=")[2], context)
            index += 1
            continue
        if name == "dd" and token.startswith("of="):
            _record_one_write_target(token.partition("=")[2], context)
            index += 1
            continue
        if name == "sed":
            if any(token.startswith(option) for option in _SED_IN_PLACE_OPTIONS):
                in_place = True              # `-i` and `-i.bak` alike: the suffix is not a target
                index += 1
                continue
            if token in _SED_EXPRESSION_OPTIONS and index + 1 < len(tokens):
                expression_given = True
                index += 2
                continue
        if token.startswith("-"):
            index += 1
            continue
        operands.append(token)
        index += 1
    if name == "sed":
        targets = (operands if expression_given else operands[1:]) if in_place else []
    elif name in _WRITERS_OVER_EVERY_OPERAND:
        targets = operands
    elif name in _WRITERS_OVER_THE_LAST_OPERAND:
        targets = operands[-1:]
    else:
        targets = []                         # curl/wget/dd: the target came from its own option
    for target in targets:
        _record_one_write_target(target, context)


def _record_one_write_target(target: str, context: _ScanContext) -> None:
    """One write target, resolved against every candidate directory, or flagged as runtime-built."""
    if not target:
        return
    try:
        _refuse_a_word_built_at_runtime(target, "write target")
    except _LaunchRefusal:
        context.uses.runtime_target = target
        return
    if os.path.isabs(target):
        context.uses.written.add(_realpath_or_self(target))
        return
    for base in _candidate_directories(context):
        context.uses.written.add(_realpath_or_self(os.path.join(base, target)))


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
    if positional is None and index < len(command):
        positional = command[index]
    if positional is None:
        #: NO OPERAND MEANS sbatch READS ITS BATCH SCRIPT FROM STDIN -- the same state a bare
        #: `bash` is in, and it must refuse for the same reason: the program does not exist as
        #: bytes this scan can reach, because the parent writes it after the fork. Reached two
        #: ways (`sbatch` alone, and options with no operand), so it is tested once here rather
        #: than at each exit.
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             "sbatch with no script operand reads its batch script from stdin, "
                             "which does not exist at scan time", executable=target)
    _refuse_a_word_built_at_runtime(positional, "sbatch script operand")
    _record_script_operand(positional, context)
    return _scan_every_resolution(positional, env, context, "sbatch script operand")


def _restricted_shell_argv(parsed: dict, script: "str | None" = None) -> list:
    """The argv an admitted shell launch is REWRITTEN to. Round 7, part B.

    THE SHELL BECOMES THE ENFORCER AND THE STATIC MODEL STOPS BEING THE RESIDUAL. Everything above
    reads a shell program and decides whether it can be proven safe; what it proves is bounded by
    how well this file models shell syntax, and rounds 5, 6 and 7 each found a construct it modelled
    wrongly. So an admitted shell no longer runs as the caller spelled it: it runs as
    `<pinned real bash> -r [--posix] <surviving options> <-c string | script> <args>` with a `PATH`
    holding the guard's wrapper directories and nothing else. What a program can then reach is the
    set this guard wrote a wrapper for, and everything else is `command not found` -- issued by
    bash, from bash's own documented restricted mode (manual section 6.10), which is what the
    residual for shells now is.

    THE CALLER'S OPTIONS SURVIVE AND THE CALLER'S OPERANDS SURVIVE, because a guard that changes
    what a program computes is worse than one that refuses it: `-e` and `-u` change a script's
    behaviour on error, `--posix` keeps `sh` semantics for a program written in them, and the words
    after the `-c` string are the program's own `$0` and `$@`.
    """
    #: THE PINNED ONE, AND THE SAME RESOLUTION WHEN NOTHING PINNED. `install()` exports the pin so
    #: that the committed wrappers -- which run in another process, with no guard installed -- read
    #: the SAME bash this process chose. A scan running before or without `install()` has no pin and
    #: resolves it here instead; both go through `_resolve_real_bash`, so the answer cannot differ.
    real_bash = os.environ.get(REAL_BASH_ENV) or _resolve_real_bash()[0]
    if not real_bash:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             "no bash under any named system prefix, so an admitted shell launch "
                             "cannot be run in restricted mode and is refused instead")
    #: LONG OPTIONS FIRST, AND THIS IS MEASURED RATHER THAN STYLISTIC. bash 3.2 -- the bash macOS
    #: ships and the one this rewrite runs on here -- parses its GNU long options only BEFORE the
    #: short-option cluster, so `bash -r --posix -c ...` exits 2 with "--: invalid option" while
    #: `bash --posix -r -c ...` runs. A rewrite that produced the first spelling would turn every
    #: admitted `sh` launch into a usage error, which is a guard that breaks correct runs.
    long_options, short_options = [], []
    index = 0
    while index < len(parsed["options"]):
        token = parsed["options"][index]
        if token in _SHELL_VALUE_OPTIONS:
            short_options.extend(parsed["options"][index:index + 2])
            index += 2
            continue
        (long_options if token.startswith("--") else short_options).append(token)
        index += 1
    if parsed["posix"] and "--posix" not in long_options:
        long_options.append("--posix")
    argv = [real_bash, *long_options, "-r", *short_options]
    if parsed["kind"] == "string":
        argv.extend(["-c", parsed["text"]])
    else:
        argv.append(parsed["path"] if script is None else script)
    argv.extend(parsed["args"])
    return argv


def _shebang_shell_invocation(shebang: list, script: str, env) -> dict:
    """A `#!/bin/sh -e` script, parsed as the shell invocation the kernel will actually make."""
    return _parse_shell_invocation([shebang[0], *shebang[1:], script], env)


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
        if context.in_shell:
            _refuse_runtime_python_tokens(command)
        else:
            _refuse_a_word_built_at_runtime(word, "interpreter path")
        flag = _forbidden_python_flag(command)
        if flag is not None:
            raise _LaunchRefusal(LAUNCH_REASON_FLAGS, flag, executable=target)
        return True
    if name in _SHELL_BASENAMES:
        parsed = _parse_shell_invocation(command, env)
        if context.in_shell:
            #: The shell's OPTIONS, never its `-c` string: the string is scanned as a program of its
            #: own, which is a strictly stronger treatment than refusing it for holding a `$`, and
            #: refusing it would refuse `bash -c 'echo $HOME'`. The script PATH is checked below.
            _refuse_runtime_tokens(parsed["options"], "shell option")
        context.record_rewrite(_restricted_shell_argv(parsed))
        if parsed["kind"] == "string":
            return _scan_shell_program(parsed["text"], env, context.deeper(in_shell=True))
        _refuse_a_word_built_at_runtime(parsed["path"], "shell script operand")
        _record_script_operand(parsed["path"], context)
        return _scan_every_resolution(parsed["path"], env, context, "shell script operand")
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
        if context.in_shell:
            _refuse_runtime_git_tokens(command)
        _scan_git(command, env, target)
        return False
    if name == "sbatch":
        #: EVERY TOKEN, and not only the operand. `sbatch` is the one class where the static model
        #: IS the enforcement -- the batch script runs on a compute node, outside this process tree,
        #: where no restricted shell and no wrapper directory of ours exists -- so an option built
        #: at run time is an option nobody will ever read. See arm (3) of `DECLARED_GAP`.
        _refuse_runtime_tokens(command, "sbatch token")
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
    if not shebang:
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             f"the shebang of {target} names no interpreter", executable=target)
    interpreter = shebang[0]
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
        parsed = _shebang_shell_invocation([interpreter, *options], target, env)
        #: THE SHEBANG'S LAUNCH IS REWRITTEN TOO, and the argv it is rewritten to names the SCRIPT
        #: rather than the shebang's implicit operand: `./stage.sh` becomes
        #: `<real bash> -r <shebang options> /abs/stage.sh <the caller's arguments>`. A shebang that
        #: was not rewritten would be the one admitted shell in the file that ran unrestricted, and
        #: `./stage.sh` is the spelling round 6's reviewer used.
        context.record_rewrite(_restricted_shell_argv(parsed, script=target) + list(command[1:]))
        if parsed["kind"] == "string":
            return _scan_shell_program(parsed["text"], env, context.deeper(in_shell=True))
        _record_script_operand(target, context)
        return _scan_shell_script_file(target, env, context)
    raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                         f"the shebang of {target} names {interpreter}, which is neither an "
                         f"interpreter, a shell nor env", executable=target)


def _track_a_directory_change(tokens: list, context: _ScanContext) -> None:
    """`cd`/`pushd`: add a candidate working directory, or mark the set UNKNOWN. Round 7, C(3).

    THE SCAN DOES NOT EXECUTE THE PROGRAM, so it cannot know which branch's `cd` happened. It
    therefore ACCUMULATES: after `cd sub` the operand `child.sh` may name the file in the launch
    directory or the one in `sub/`, and both are read. The alternative -- following the `cd` and
    replacing the directory -- is what the predecessor did implicitly by resolving against one
    directory, and it is what made the reviewer's benign `child.sh` the file that was scanned while
    the malicious one ran.

    THE FOUR SPELLINGS THAT MAKE IT UNKNOWN are the ones whose destination is not in the token: a
    runtime-built operand, no operand at all (`$HOME`), `-` (`$OLDPWD`) and `~user` (the password
    database). None of them can be resolved here, and an unknown destination makes every later
    relative operand a refusal rather than a guess.
    """
    operands = [token for token in tokens[1:] if not token.startswith("-")]
    if not operands:
        context.dirs.mark_unknown(f"`{tokens[0]}` with no operand moves to $HOME, which this scan "
                                  f"cannot resolve")
        return
    operand = operands[0]
    if operand == "-":
        context.dirs.mark_unknown("`cd -` moves to $OLDPWD, which this scan cannot resolve")
        return
    if operand.startswith("~"):
        context.dirs.mark_unknown(f"`{tokens[0]} {operand}` depends on tilde expansion")
        return
    if _is_a_word_built_at_runtime(operand):
        context.dirs.mark_unknown(f"`{tokens[0]} {operand}` names a directory built at run time")
        return
    if os.path.isabs(operand):
        context.dirs.add(operand)
        return
    for base in list(_candidate_directories(context)):
        context.dirs.add(os.path.join(base, operand))


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
        assignment = _SHELL_ASSIGNMENT_RE.match(tokens[index])
        if assignment is None:
            break
        name, appends, value = assignment.group(1), assignment.group(2), assignment.group(3)
        if _is_protected_shell_variable(name):
            raise _LaunchRefusal(LAUNCH_REASON_ENV, tokens[index])
        if name == "CDPATH":
            #: NOT A REFUSAL AND DELIBERATELY NOT ONE. `CDPATH` does not disarm anything -- it makes
            #: a LITERAL `cd` operand resolve somewhere this scan did not model, which is exactly
            #: the state `_CandidateDirectories.known = False` names. An absolute script operand is
            #: still resolvable and still admitted; a relative one refuses.
            context.dirs.mark_unknown(f"{tokens[index]} makes a literal `cd` operand resolve "
                                      f"against a path this scan cannot enumerate")
        #: `NAME+=VALUE` IS AN ASSIGNMENT AND NOT A COMMAND WORD. Read as a command word it would
        #: still have refused -- as an unprovable child -- but the reason would have named a
        #: nonexistent executable instead of the variable, which is a check that is right about the
        #: wrong object. An append cannot be compared to this process's value, so it is treated as
        #: disarming whenever the name is one the contract depends on.
        if _breaks_propagation_contract(name, None if appends else value):
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
    if word in ("cd", "pushd"):
        _track_a_directory_change(tokens, context)
        return False
    if word in _SHELL_INERT_BUILTINS:
        return False
    if word in _SHELL_DECLARING_BUILTINS:
        unexports = any(operand in _SHELL_UNEXPORT_OPTIONS for operand in tokens[1:])
        for operand in tokens[1:]:
            if operand.startswith("-"):
                continue
            assignment = _SHELL_ASSIGNMENT_RE.match(operand)
            declared = assignment.group(1) if assignment else operand
            if declared == "CDPATH" and assignment is not None:
                context.dirs.mark_unknown(f"{word} {operand} makes a literal `cd` operand resolve "
                                          f"against a path this scan cannot enumerate")
            if not _is_protected_shell_variable(declared):
                continue
            if assignment is not None or unexports:
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
        _record_script_operand(operands[0], context)
        return _scan_every_resolution(operands[0], env, context, f"{word} operand")
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
    _record_write_targets(tokens, context)
    resolved = _resolve_launch_command(tokens, env)
    if resolved is None:
        return False
    _refuse_an_unreadable_wrapper_prefix(tokens, resolved, context)
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
    #: THE TOKENS BELOW CAME FROM A SHELL, and that is what turns a `$` from a character into an
    #: expansion. Set here rather than at every construction site, so a path that reaches this
    #: function by any route gets the shell reading of its tokens.
    context.in_shell = True
    if (os.environ if env is None else env).get("CDPATH"):
        context.dirs.mark_unknown("$CDPATH is set in the child environment, so a literal `cd` "
                                  "operand may resolve anywhere on it")
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
        commands, redirections = _split_simple_commands_with_terminators(tokens)
        for target in redirections:
            #: A REDIRECTION TARGET IS A WRITE. The restricted shell refuses redirection outright,
            #: so this is not what stops it -- it is what makes `echo ... > stage.sh` and
            #: `bash stage.sh` in one program a REFUSAL rather than a scan of bytes that are about
            #: to be replaced, which is the case the static half still owns for `sbatch`.
            _record_one_write_target(target, context)
        for command, terminator in commands:
            if case_depth and terminator == ")":
                continue                     # a `case` PATTERN, not a command
            substituted = any(_SUBSTITUTION_PLACEHOLDER in token for token in command)
            launches_python = _scan_shell_simple_command(
                command, env, context, substituted) or launches_python
    return launches_python


def _split_simple_commands_with_terminators(tokens: list[str]
                                            ) -> "tuple[list[tuple[list[str], str]], list[str]]":
    """`_split_simple_commands`, with the OPERATOR that ended each command and the WRITE TARGETS.

    ONE CONSUMER FOR THE TERMINATOR, ONE REASON: `case`. A pattern list -- `stage2) python3 x.py ;;`
    -- tokenises so that `stage2` is a simple command of its own, and an unknown one-word command is
    a refusal. The operator that ended it is `)`, which is the only thing in the token stream that
    distinguishes a pattern from a command, so the scanner needs to see it.

    THE SECOND RETURN VALUE IS ROUND 7's, and it is the token this function has always DROPPED. A
    redirection's target has to leave the command -- otherwise it ends the startup-flag scan early,
    which is the measured escape recorded on `_SHELL_PUNCTUATION` -- but dropping it made the one
    path a program writes to invisible to the scan. An OUTPUT redirection's target is a write; an
    input redirection's is a read and is not collected.
    """
    commands: "list[tuple[list[str], str]]" = []
    written: list[str] = []
    current: list[str] = []
    pending_write = False
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            if pending_write:
                written.append(token)
            pending_write = False
            continue
        if token and set(token) <= _SHELL_PUNCTUATION:
            if "<" in token or ">" in token:
                if current and current[-1].isdigit():
                    current.pop()
                pending_write = ">" in token
                skip_next = True
                continue
            if current:
                commands.append((current, token))
            current = []
            continue
        current.append(token)
    if current:
        commands.append((current, ""))
    return commands, written


def _scan_shell_string(text: str, env, depth: int = 0) -> bool:
    """Scan a shell COMMAND STRING. The entry point for a `-c` string and for `os.system`.

    `_scan_shell_program` is where the work is; this spelling keeps the name the shim, the controls
    and the docstring above all refer to, and it is what makes a string and a SCRIPT FILE provably
    the same scan rather than two implementations that agree today. The write-then-execute
    composition is checked HERE and not inside `_scan_shell_program`, because it is a property of
    the WHOLE program and `_scan_shell_program` is also the recursion.
    """
    context = _ScanContext(os.getcwd(), depth, in_shell=True)
    launches_python = _scan_shell_program(text, env, context)
    _refuse_write_then_execute(context)
    return launches_python


#: THE TWO BINDINGS OF THE KERNEL FLOOR, and BOTH have to be patched or the patch is decorative.
#: `_posixsubprocess.fork_exec` is the module attribute -- the one
#: `multiprocessing.util.spawnv_passfds` calls, because it does `import _posixsubprocess` and then
#: `_posixsubprocess.fork_exec(...)` -- and
#: `subprocess._fork_exec` is a SEPARATE name bound once at import by
#: `from _posixsubprocess import fork_exec as _fork_exec`, which is what `Popen._execute_child`
#: calls. Rebinding the first does not touch the second: that is what a `from ... import` means.
#: MEASURED, NOT REMEMBERED: both names exist on 3.11.15, 3.12.2 and 3.13.7, and
#: `tests/test_mnv_guarded_run.py::TheKernelFloorIsHookedAndTheResidualIsBelowIt` re-derives the
#: pair and the callsite from THIS interpreter's own `subprocess` source rather than from this
#: tuple, so a CPython that adds or moves a binding is red on the test rather than silently
#: unhooked. A name absent from an interpreter is skipped, not invented.
_FORK_EXEC_BINDINGS = (
    ("_posixsubprocess", "fork_exec"),
    ("subprocess", "_fork_exec"),
)

#: `fork_exec`'s POSITIONAL layout. It is a C function that takes NO KEYWORD ARGUMENTS, so there is
#: no signature to bind against and no parameter name to read -- the positions are the contract.
#: These four are the ones a scan needs, and they are identical in 3.11, 3.12 and 3.13:
#:   0  args             the argument vector, argv[0] included and a DISPLAY NAME as everywhere else
#:   1  executable_list  CANDIDATE files, bytes, tried in order -- `os._execvpe`'s semantics
#:   4  cwd              the launch's working directory, or None for this process's
#:   5  env_list         [b"NAME=VALUE", ...], or None meaning "execv, inherit this environment"
#: A call whose shape does not match is REFUSED with `LAUNCH_REASON_KERNEL_FLOOR` rather than read
#: at these offsets anyway: an interpreter that reordered them would otherwise have this guard
#: parsing an fd as an environment, which is the "right pattern over the wrong rows" failure.
_FORK_EXEC_ARGV_INDEX = 0
_FORK_EXEC_EXECUTABLE_LIST_INDEX = 1
_FORK_EXEC_CWD_INDEX = 4
_FORK_EXEC_ENV_LIST_INDEX = 5
_FORK_EXEC_MINIMUM_ARITY = 6


def _fork_exec_executable(executable_list) -> str:
    """The file the KERNEL will run, out of `fork_exec`'s candidate list.

    `executable_list` IS A LIST BECAUSE THE `p` SEMANTICS LIVE HERE. `subprocess` hands down one
    entry for a path with a directory in it and one entry PER `PATH` DIRECTORY for a bare name, and
    the C code execs the first that works -- so "the executable" is the first candidate that
    exists, not the first candidate. Scanning `[0]` unconditionally would let a launch put a
    nonexistent path in front of a real interpreter and be classified on a file that never runs.
    When none of them exists the launch will fail with ENOENT whatever this returns, so the first
    is used and the refusal (if any) names a file the caller did write.
    """
    candidates = [_text_argument(candidate) for candidate in executable_list]
    if not candidates:
        raise _LaunchRefusal(LAUNCH_REASON_KERNEL_FLOOR,
                             "fork_exec was handed an empty executable_list, so there is no file "
                             "to classify")
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def _environment_from_fork_exec(env_list) -> "dict | None":
    """`[b"NAME=VALUE", ...]` as a mapping; None stays None, which means "inherit, via execv".

    THE None IS NOT AN EMPTY ENVIRONMENT AND THE DISTINCTION IS LOAD-BEARING. `subprocess` sets
    `env_list = None` when the caller passed no `env=` and says so in its own comment ("Use execv
    instead of execve"), and this guard's whole environment contract already spells that state
    None -- `_rearm_launch_environment(None, ...)` returns None, and
    `_environment_reaching_child_is_armed(None)` reads `os.environ`. Turning None into
    `dict(os.environ)` here would convert every inherit-launch into an explicit one and make this
    layer's answer differ from every other layer's for the same launch.

    A MEMBER WITHOUT A `=` IS A REFUSAL, not a skipped entry: the propagation contract is read out
    of this list, and an entry this guard cannot parse is an entry it cannot say is armed.
    """
    if env_list is None:
        return None
    mapping = {}
    for entry in env_list:
        text = os.fsdecode(entry) if isinstance(entry, (bytes, bytearray)) else str(entry)
        name, separator, value = text.partition("=")
        if not separator or not name:
            raise _LaunchRefusal(LAUNCH_REASON_KERNEL_FLOOR,
                                 f"fork_exec was handed the environment member {text!r}, which is "
                                 f"not NAME=VALUE, so the propagation contract reaching the child "
                                 f"cannot be read")
        mapping[name] = value
    return mapping


def _read_fork_exec_call(call_args: tuple, call_kwargs: dict) -> tuple:
    """`fork_exec`'s positional call, read as `(argv, executable, cwd, environment)` or REFUSED.

    THE SHAPE IS VALIDATED RATHER THAN TRUSTED, and that is not defensive padding. `fork_exec` is a
    C function that takes NO KEYWORD ARGUMENTS, so there is no signature to bind against and no
    parameter name to read -- the positions ARE the contract, and this guard's copy of them is a
    constant. If an interpreter reordered them, reading at these offsets anyway would have the guard
    parsing a file descriptor as an environment and answering confidently about the wrong object.
    So each field is checked for the KIND it must be, and a mismatch is
    `LAUNCH_REASON_KERNEL_FLOOR`: a vector where a vector belongs, `None`/`str`/`bytes` for the
    working directory, and `None` or `NAME=VALUE` members for the environment. This function is
    where every one of those refusals is spelled, so the wrapper below has no second copy.
    """
    if call_kwargs or len(call_args) < _FORK_EXEC_MINIMUM_ARITY:
        raise _LaunchRefusal(
            LAUNCH_REASON_KERNEL_FLOOR,
            f"fork_exec was called with {len(call_args)} positional and {len(call_kwargs)} keyword "
            f"arguments; it takes no keyword arguments and this guard reads the argv, the "
            f"executable_list, the cwd and the environment at positions {_FORK_EXEC_ARGV_INDEX}, "
            f"{_FORK_EXEC_EXECUTABLE_LIST_INDEX}, {_FORK_EXEC_CWD_INDEX} and "
            f"{_FORK_EXEC_ENV_LIST_INDEX}, so this call cannot be read")
    raw_argv = call_args[_FORK_EXEC_ARGV_INDEX]
    if raw_argv is None or isinstance(raw_argv, (str, bytes, bytearray)):
        raise _LaunchRefusal(
            LAUNCH_REASON_KERNEL_FLOOR,
            f"fork_exec's argument vector is {type(raw_argv).__name__} and not a vector, so the "
            f"arguments the child receives cannot be read")
    cwd = call_args[_FORK_EXEC_CWD_INDEX]
    if cwd is not None and not isinstance(cwd, (str, bytes, bytearray, os.PathLike)):
        raise _LaunchRefusal(
            LAUNCH_REASON_KERNEL_FLOOR,
            f"fork_exec's working directory is {type(cwd).__name__} and not a path, so a relative "
            f"operand of this launch cannot be resolved against the directory it will run in")
    try:
        argv = _launch_argv(raw_argv)
        executable = _fork_exec_executable(call_args[_FORK_EXEC_EXECUTABLE_LIST_INDEX])
        env = _environment_from_fork_exec(call_args[_FORK_EXEC_ENV_LIST_INDEX])
    except TypeError as err:
        raise _LaunchRefusal(
            LAUNCH_REASON_KERNEL_FLOOR,
            f"fork_exec's argv, executable_list or environment could not be walked as the kind it "
            f"must be ({err})") from None
    return argv, executable, cwd, env


def _fork_exec_environment_list(mapping) -> list:
    """A mapping back into the `[b"NAME=VALUE", ...]` shape the C code requires.

    BYTES, ALWAYS, and encoded with `os.fsencode` rather than `str.encode`: that is what
    `subprocess` does one layer up, and a re-armed environment that round-tripped through a
    different codec would hand the child different bytes than the caller's own path would have.
    """
    return [os.fsencode(str(name)) + b"=" + os.fsencode(str(value))
            for name, value in mapping.items()]


def _launch_file_identity(executable, env=None) -> "str | None":
    """The FILE a launch will hand the kernel, as ONE comparable value -- or None if unnameable.

    THIS IS THE HALF OF A TICKET THAT ROUND 8's FINDING SAYS MUST BE THERE. Round 8's whole result
    was that THE ARGV IS NOT THE EXECUTABLE: `os.execv`, `os.posix_spawn` and `fork_exec` all take
    the file separately, and `argv[0]` is a display name. An approval keyed on the argv alone is
    therefore keyed on the display name, and anything that runs inside the window -- a `preexec_fn`
    in the forked child, a `__del__` or a `fileno()` reached from inside `Popen.__init__`, all of
    which inherit this thread's approval stack -- could spend the ticket on a DIFFERENT file with
    the same argv. `['ls', '-I', child]` approved as the leaf tool it is, then handed to
    `fork_exec` with `executable_list=[sys.executable]`, is round 7's finding 1 reached through
    round 8's ticket, and it is measured in
    `TheApprovalIsBoundToTheFileAndNotOnlyToTheArgv`.

    A BARE NAME IS RESOLVED ON THE CHILD'S OWN PATH, SHIM DIRECTORIES INCLUDED, and that is the one
    place this function must NOT reuse the scan's resolver as-is. `_resolve_executable` answers the
    SCAN's question -- "which real program is this" -- and to answer it it SUBTRACTS this guard's
    wrapper directories, deliberately. The ticket asks a different question: "which file will the
    layer below exec", and the layer below is `subprocess` building one candidate per
    `os.get_exec_path(env)` entry -- wrapper directories and all, because they are in front of the
    child's PATH on purpose -- and exec'ing the first that works. Resolving `ls` the scan's way
    here would name `/bin/ls` at the issue site while the floor was handed the generated forwarder:
    two names for one launch, no match, and the floor would re-scan its own layer's repair and
    refuse a correct `subprocess.run(['ls', ...])` -- the very failure the ticket exists to prevent,
    reintroduced by the key meant to sharpen it, and visible in NO refusal arm because a mismatch
    only ever makes the floor scan MORE. `TheApprovalIsBoundToTheFileAndNotOnlyToTheArgv`'s
    bare-name row is the arm that fails when this paragraph is ignored. So the candidate list is built
    the way the producer builds it and read by `_fork_exec_executable`, which is the SAME function
    the floor reads its own `executable_list` with, and `_resolve_executable` is then applied to the
    located path -- where, having a directory component, it only resolves and cannot subtract.

    `os.path.realpath` LAST, so two spellings of one file are one identity: the layer above may name
    `/usr/bin/python3` and the layer below a symlink chain ending at the same inode, and a ticket
    that treated those as different files would refuse every correct launch through a symlinked
    interpreter.

    None IS "THIS CANNOT BE NAMED" AND IT IS NEVER A WILDCARD. `_consume_approved_launch` requires
    both halves to be EQUAL, so a None recorded here matches only a launch whose file is equally
    unnameable -- which is the fail-closed direction: the floor's unreadable-call path has no file,
    and an approval issued for a real file must not be spendable there.
    """
    if executable is None:
        return None
    try:
        text = _text_argument(executable)
    except (TypeError, ValueError):
        return None
    if not text:
        return None
    try:
        if os.path.dirname(text):
            located = text
        else:
            candidates = [os.path.join(directory, text) for directory in os.get_exec_path(env)]
            located = _fork_exec_executable(candidates) if candidates else text
        return os.path.realpath(_resolve_executable(located, env))
    except (OSError, TypeError, ValueError, _LaunchRefusal):
        return None


class _ApprovedLaunch:
    """One launch `_prepare_launch` has already read, handed down to the layer beneath it.

    WHY A TICKET AND NOT A FLAG. The public primitives are where a launch is REPAIRED -- their argv
    positions are known well enough to insert `env` operands or to substitute the restricted-bash
    spelling -- and the lower layers (`_posixsubprocess.fork_exec`, and `os.posix_spawn` when
    `subprocess.Popen` chooses it) then see the REPAIRED argv. Re-scanning that is not merely
    wasteful, it REFUSES A CORRECT LAUNCH: the restricted rewrite runs with `PATH` set to the
    guard's wrapper directories only, and a second scan resolving `ls` through that `PATH` finds no
    system prefix, so `_check_leaf` refuses it. `subprocess.run("ls", shell=True, close_fds=False)`
    was refused exactly that way before this existed.

    A FLAG WOULD SUPPRESS MORE THAN IT APPROVED. The ticket carries an IDENTITY and is consumed
    ONCE, so a lower layer launching a DIFFERENT ARGV, or the same argv with a DIFFERENT FILE,
    while an approval is outstanding does not match and is scanned.

    WHAT IT CERTIFIES, EXACTLY: THAT THE LAYER ABOVE SCANNED **THIS ARGV** AND **THIS FILE**. That
    is the whole of it, and round 10's finding is that the consume sites read it as though it said
    more. IT NEVER CERTIFIED THE ENVIRONMENT -- there is no environment in the identity and there
    never was -- yet on the ticket path both sites handed the CALLER's own environment to the child
    unread by `_environment_reaching_child_is_armed` and unrepaired by `_rearm_launch_environment`.
    So an in-window call matching both halves of the key while stripping only `MNV_GUARD_*` and
    `PYTHONPATH` started an UNGUARDED interpreter on the approved argv and the approved file: the
    wrong tree loaded, exit 0, nothing refused. THE ENVIRONMENT IS THEREFORE CHECKED AT EVERY
    CONSUME SITE (`_refuse_an_approved_launch_whose_environment_is_disarmed`,
    `LAUNCH_REASON_TICKET_ENV`) AND IS DELIBERATELY NOT A THIRD HALF OF THE KEY: a check cannot
    refuse a correct launch, whose environment already IS the armed one, while a third key half
    would turn every layer that legitimately re-spells an environment into a mismatch -- and a
    mismatch is invisible, because it only ever makes the lower layer scan MORE.

    THE IDENTITY IS (ARGV, FILE) AND NOT THE ARGV, WHICH IS ROUND 9's CORRECTION. Keyed on the argv
    alone it contradicted round 8's own finding -- the argv is not the executable -- and the earlier
    version of this docstring claimed the opposite of what the code did: it said a `preexec_fn`
    "does not match and is scanned", which held for a different THREAD (the stack is thread-local)
    and was FALSE for anything running inside the window in THIS thread. CPython runs `preexec_fn`
    in the forked child between `fork` and `exec`, with this thread's approval stack inherited; a
    `__del__`, a weakref finalizer or a `fileno()` called from inside `Popen.__init__` is the same
    shape. Any of them could call `fork_exec` with the approved argv and `executable_list` naming a
    different file, and the floor would spend the ticket and skip the scan. Both halves must now be
    equal, so the argv is only half a key and the file -- `_launch_file_identity`, computed at the
    issue site through the ARMED environment, which is the one the child will receive -- is the
    other. `preexec_fn` is refused outright as well (`LAUNCH_REASON_PREEXEC`): the identity closes
    the matching hole, but arbitrary caller code running after `fork` inside an armed process is
    worth refusing on its own terms.

    IT IS PER-THREAD for the reason it always was: an approval in one thread must not wave through
    another thread's launch.
    """

    __slots__ = ("argv", "executable", "consumed")

    def __init__(self, argv: tuple, executable: "str | None"):
        self.argv = argv
        #: The resolved, realpath'd file the layer below is expected to exec. None means "the issue
        #: site could not name a file", and it matches only an equally unnameable one.
        self.executable = executable
        self.consumed = False


_APPROVED_LAUNCHES = threading.local()


def _approved_launches() -> list:
    """This thread's outstanding approvals, innermost last."""
    stack = getattr(_APPROVED_LAUNCHES, "stack", None)
    if stack is None:
        stack = []
        _APPROVED_LAUNCHES.stack = stack
    return stack


def _launch_identity(arguments, executable=None, env=None) -> tuple:
    """`(argv, file)`, each normalised the one way both layers normalise it, as a comparable value.

    ONE FUNCTION FOR BOTH SIDES, deliberately: an issue site and a consume site that each computed
    their own half would be two implementations of one key, and the first thing they would diverge
    on is exactly the bare-name resolution `_launch_file_identity` spells out.
    """
    return tuple(_launch_argv(arguments)), _launch_file_identity(executable, env)


def _approve_launch(arguments, executable=None, env=None) -> _ApprovedLaunch:
    """Record that THIS argv AND THIS FILE have been scanned, for the layer below. Always paired.

    `env` IS THE ARMED ENVIRONMENT AND NOT THE CALLER'S, at every issue site, because it is the one
    the child will receive and therefore the one the layer below will resolve a bare name through.
    """
    ticket = _ApprovedLaunch(*_launch_identity(arguments, executable, env))
    _approved_launches().append(ticket)
    return ticket


def _withdraw_launch_approval(ticket: _ApprovedLaunch) -> None:
    """Drop `ticket` whether or not it was consumed. Removed BY IDENTITY, never by value.

    Two launches with the same argv and file are two tickets, and `list.remove` would delete the
    wrong one.
    """
    stack = _approved_launches()
    for index in range(len(stack) - 1, -1, -1):
        if stack[index] is ticket:
            del stack[index]
            return


def _consume_approved_launch(arguments, executable=None, env=None) -> bool:
    """Whether a layer above already scanned exactly this argv AND this file. Consumes it.

    BOTH HALVES, AND EQUALITY RATHER THAN A SUBSUMPTION. There is no wildcard here and no "the
    ticket did not record a file, so anything matches": an approval whose file could not be named
    matches only a launch whose file cannot be named either. See `_launch_file_identity`.
    """
    argv, launched = _launch_identity(arguments, executable, env)
    for ticket in reversed(_approved_launches()):
        if not ticket.consumed and ticket.argv == argv and ticket.executable == launched:
            ticket.consumed = True
            return True
    return False


def _refuse_the_launch(refusal: _LaunchRefusal, guard: GuardedPathFinder, argv, executable,
                       env=None):
    """Record a launch refusal on the guard, report it, and exit 3. EVERY layer refuses here.

    It exists because the floor can refuse BEFORE it has an executable to name -- an unreadable
    `fork_exec` call has no classified file -- and a second copy of this block would be a second
    place for the record's shape to drift from `write_inventory`'s reader.
    """
    launched = getattr(refusal, "executable", None)
    if not launched:
        launched = _resolve_executable(executable, env) if executable is not None else None
    record = {
        "executable": launched,
        "offending_flag": refusal.offending,
        "argv": list(argv),
        "reason": refusal.reason,
    }
    guard.launch_refusal = record
    _report_launch(record)
    raise SystemExit(VIOLATION_EXIT) from None


def _refuse_an_approved_launch_whose_environment_is_disarmed(argv, executable, env,
                                                             guard: GuardedPathFinder) -> None:
    """THE TICKET PATH'S ENVIRONMENT GATE. Every consume site calls it before the launch runs.

    ROUND 10's FINDING IS THAT THE TICKET NEVER CERTIFIED THE ENVIRONMENT, and the ticket path was
    the one route to a child where nothing did. `_ApprovedLaunch`'s identity is `(argv, file)`;
    matching it used to be the whole of the consume site, and what followed was the caller's own
    environment handed to the child untouched -- `_environment_reaching_child_is_armed` is called
    from `_scan_launch`, which the ticket exists to SKIP, and `_rearm_launch_environment` runs one
    line further down `_prepare_launch` than a matched ticket ever reaches. An in-window call
    matching both halves of the key while stripping only `MNV_GUARD_*` and `PYTHONPATH` therefore
    ran an unguarded interpreter on the approved argv and the approved file.

    ONE FUNCTION FOR BOTH CONSUME SITES, for the reason `_launch_identity` is one function for both
    sides of the key: two sites each spelling their own environment check are two implementations
    of one rule, and the first thing they diverge on is the `None` below.

    IT IS THE SAME PREDICATE THE SCAN PATH USES AND NOT A SECOND ONE.
    `_environment_reaching_child_is_armed` is called here with the environment REACHING THE CHILD,
    so a ticket path and a scan path refuse the same disarmed child for the same missing variable;
    only the `reason` differs, because only the reason differs -- see `LAUNCH_REASON_TICKET_ENV`.

    `env=None` IS ADMITTED, AND IT IS NOT A HOLE. At both consume sites None means INHERIT, which is
    the same spelling this file uses everywhere: `_environment_from_fork_exec` keeps the floor's
    `env_list=None` as None ("use execv instead of execve"), and `_rearm_launch_environment(None)`
    returns None. What an inheriting child receives is THIS process's `os.environ`, which is armed
    -- `install()` exported the contract into it -- and which is exactly what
    `_environment_reaching_child_is_armed(None)` reads. Refusing None instead would refuse the
    commonest correct launch in the file: `subprocess.run([sys.executable, "child.py"])` passes no
    `env=`, so the ticket is issued with None, `Popen._execute_child` builds `env_list = None`, and
    the floor consumes the ticket with None. A guard that fired on every correct run would not be a
    guard.

    THE TICKET IS ALREADY SPENT WHEN THIS RUNS, and that is deliberate: the caller has to CONSUME to
    know it is on the ticket path at all, and the refusal below exits the process, so there is no
    later launch for an unspent ticket to serve. `_refuse_the_launch` names the file from
    `executable` in its own single place rather than a second copy here.
    """
    missing = _environment_reaching_child_is_armed(env)
    if missing is None:
        return
    _refuse_the_launch(_LaunchRefusal(LAUNCH_REASON_TICKET_ENV, missing), guard, argv, executable,
                       env)


def _scan_launch(argv, env, guard: GuardedPathFinder, cwd=None, executable=None):
    """The argv to launch and the environment to launch it with; raise to refuse.

    Returns `(argv, environment or None)`. None means "the caller's environment, unchanged"; a
    mapping means an ADMITTED SHELL, whose environment this guard replaces outright -- see
    `_restricted_shell_environment`.

    IT CLASSIFIES BY THE EXECUTABLE THE KERNEL WILL RUN, NEVER BY argv[0]. Round 7's first finding
    is that it used to do the opposite: `subprocess.run(["ls", "-I", "child.py"],
    executable=sys.executable)` was classified as `ls`, admitted as a leaf tool, and ran Python with
    `-I`. `argv[0]` is a DISPLAY NAME -- every exec primitive in POSIX takes it separately from the
    file to execute, and `env -a`, `exec -a` and `bash -c cmd name` all exist to set it to something
    else. So the caller hands this function the real executable and the scan is over
    `(executable, argv[1:])`; the positions still line up with the caller's argv, which is what lets
    an argv repair be written back at the index it was computed at.

    THE ORDER IS THE CHEAPEST CORRECT ONE. The wrapper prefixes are resolved first, because until
    they are there is no executable to ask questions about; the resolved child is then CLASSIFIED
    (`_scan_resolved_command`), which reads a shell's string or script file, flag-scans an
    interpreter, and refuses a child whose coverage cannot be established; the write-then-execute
    composition is checked once the whole program has been read; and the environment question is
    asked LAST, after any argv repair, so a repaired launch is not refused for the state it was
    repaired out of.
    """
    argv = list(argv)
    scan_argv = list(argv)
    if executable is not None:
        scan_argv[0:1] = [_text_argument(executable)]
    resolved = _resolve_launch_command(scan_argv, env)
    if resolved is None:
        return argv, None
    command = resolved["command"]
    target = _resolve_executable(command[0], env)
    context = _ScanContext(os.fspath(cwd) if cwd is not None else os.getcwd())
    _refuse_an_unreadable_wrapper_prefix(scan_argv, resolved, context)
    launches_python = _scan_resolved_command(command, env, context)
    _refuse_write_then_execute(context)
    rewrite = context.rewrite[0] if context.rewrite else None
    prefix_end = resolved["inject_at"]
    if rewrite is not None and prefix_end is None:
        #: The shell came out of an `env -S` STRING, so there is no argv position its rewrite could
        #: replace. Refused rather than re-quoted, for the reason on `_scan_shell_program`.
        raise _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                             "a shell reached through an `env -S` string cannot be rewritten into "
                             "restricted mode, and an admitted shell that is not restricted is not "
                             "a shell this guard can account for", executable=target)
    tail = list(rewrite) if rewrite is not None else argv[prefix_end:] if prefix_end else argv
    head = argv[:prefix_end] if prefix_end else []
    restricted = _restricted_shell_environment(env) if rewrite is not None else None
    if resolved["clears"] or resolved["stripped"] is not None:
        #: THE REPAIR RUNS FOR A SHELL EVEN WHEN NOTHING PYTHON IS IN IT, and that is round 7's
        #: change here. `env -i bash -c ...` used to be left alone when the string held no
        #: interpreter -- correct then, because the shell inherited the machine's PATH. It is not
        #: correct now: the restricted shell's PATH is the guard's wrapper directories, and an
        #: `env -i` that wiped it would leave a correct program with no `ls`.
        disarming = resolved["stripped"] or "env -i"
        if prefix_end is None:
            if not launches_python and rewrite is None:
                return argv, restricted
            raise _LaunchRefusal(LAUNCH_REASON_ENV, disarming, executable=target)
        if not launches_python and rewrite is None:
            return argv, restricted
        operands, view = _contract_operands(resolved, restricted_shell=rewrite is not None)
        if launches_python:
            missing = _environment_reaching_child_is_armed(view)
            if missing is not None:
                raise _LaunchRefusal(LAUNCH_REASON_ENV, missing, executable=target)
        guard.launch_env = "argv-re-armed"
        return [*head, *operands, *tail], restricted
    if not launches_python:
        return ([*head, *tail] if rewrite is not None else argv), restricted
    missing = _environment_reaching_child_is_armed(restricted if restricted is not None else env)
    if missing is not None:
        raise _LaunchRefusal(LAUNCH_REASON_ENV, missing, executable=target)
    return ([*head, *tail] if rewrite is not None else argv), restricted


def _prepare_launch(executable, arguments, env, guard: GuardedPathFinder, cwd=None):
    """Re-arm a launch, or refuse a child that could not be proven to keep its launches guarded.

    Returns `(environment, argv)`. The environment is re-armed FIRST so that the armed copy is what
    every later check reads, and the argv comes back possibly REWRITTEN -- either with `env`
    contract operands inserted (`_contract_operands`) or, for an admitted shell, replaced outright
    with the restricted-bash spelling (`_restricted_shell_argv`). A caller that ignores the returned
    argv would silently drop both, which is why every wrapped primitive below writes them back.

    THE RETURNED ENVIRONMENT IS NOW SOMETIMES NON-None FOR A CALLER THAT PASSED None, which is new
    in round 7 and is the reason the primitives below had to learn the `*e` spellings of themselves:
    an admitted shell runs with a `PATH` this guard chose, and `os.execv` has no parameter to say so
    -- so the launch is routed through `os.execve` instead. A caller's `env=` is never discarded, it
    is the base the restricted environment is built from.

    `executable` IS THE REAL EXECUTABLE AND NOT `argv[0]`. See `_scan_launch`.

    IT CHECKS FOR AN APPROVAL BEFORE IT SCANS ANYTHING, which is round 8's addition and is what
    makes a second, lower hook safe to add. `_posixsubprocess.fork_exec` and -- when
    `subprocess.Popen` chooses it -- `os.posix_spawn` are both reached FROM a public primitive that
    has already been through here, and what they are handed is the argv this function REWROTE. A
    second reading of that argv refuses it, because the restricted rewrite runs with a `PATH` the
    scan resolves nothing through. See `_ApprovedLaunch`.

    `cwd` IS THE LAUNCH'S WORKING DIRECTORY AND NOT THIS PROCESS'S, where the caller gave one. It
    matters because a relative operand -- `bash ./stage.sh`, `source ./setup.sh` -- names a
    different file under a different cwd, and a scan that resolved it against the wrong directory
    would read the wrong bytes and report on a program that does not run. The primitives that have
    no `cwd` parameter (`os.exec*`, `posix_spawn`) pass None, which means this process's own.
    """
    argv = _launch_argv(arguments)
    if _consume_approved_launch(argv, executable, env):
        #: ALREADY READ ONE LAYER UP, and re-reading it here would REFUSE IT. See `_ApprovedLaunch`:
        #: what reaches this point is the argv a public primitive already scanned and possibly
        #: rewrote, and the restricted rewrite carries a `PATH` that a second scan resolves nothing
        #: through. The caller's environment and argv are returned exactly as handed in, because the
        #: layer that issued the approval is the one that armed them.
        #: THE FILE IS HALF THE KEY, which is round 9's correction: `executable` is passed here, not
        #: just `argv`, because the argv is not the executable and an approval matched on the argv
        #: alone was spendable by anything running inside the window on a DIFFERENT file. `env` is
        #: the environment the layer above ARMED and wrote back, so a bare name resolves here to the
        #: same file it resolved to there.
        #: AND THE ENVIRONMENT IS CHECKED RATHER THAN TRUSTED, which is round 10's correction. What
        #: is returned here is the caller's own `env` -- the ticket certifies the argv and the file
        #: and never certified this -- so a call that matched both halves of the key while stripping
        #: the contract started an unguarded child from here. `os.posix_spawn` reaches this line on
        #: every `close_fds=False` launch, so this is a consume site and not only a fast path.
        _refuse_an_approved_launch_whose_environment_is_disarmed(argv, executable, env, guard)
        return env, argv
    armed_env = _rearm_launch_environment(env, guard)
    try:
        launch_argv, restricted = _scan_launch(argv, armed_env, guard, cwd, executable)
    except _LaunchRefusal as refusal:
        if os.environ.get(STATIC_SCAN_DISABLED_ENV):
            #: THE TEST-ONLY KNOB. It exists so the two layers can be shown refusing INDEPENDENTLY:
            #: with the static scanner in front, a reproducer never reaches the restricted shell, so
            #: "the shell would have refused it too" would be an assertion nobody measured. It
            #: swallows the static refusal and hands the launch on to whatever rewrite the scan had
            #: already established -- so what refuses next is bash, in its own words. Every record
            #: written while it is set says so; see `write_inventory`.
            guard.static_scan = "disabled-for-test"
            return _static_scan_disabled_launch(argv, armed_env, guard, cwd, executable)
        _refuse_the_launch(refusal, guard, argv, executable, armed_env)
    return (restricted if restricted is not None else armed_env), launch_argv


def _static_scan_disabled_launch(argv, armed_env, guard, cwd, executable):
    """The launch a REFUSED argv becomes when the test-only knob is set: rewritten, not refused.

    The rewrite has to be recomputed rather than remembered, because the refusal may have come from
    anywhere in the scan. What is recomputed is ONLY the classification of the outermost command --
    is it a shell, and if so with which options -- which is the part that decides how the child
    RUNS rather than whether it may. Nothing here reads the program.
    """
    scan_argv = list(argv)
    if executable is not None:
        scan_argv[0:1] = [_text_argument(executable)]
    try:
        resolved = _resolve_launch_command(scan_argv, armed_env)
        if resolved is None:
            return armed_env, argv
        command = resolved["command"]
        name = _executable_basename(_text_argument(command[0]))
        prefix_end = resolved["inject_at"] or 0
        if name in _SHELL_BASENAMES:
            parsed = _parse_shell_invocation(command, armed_env)
            rewrite = _restricted_shell_argv(parsed)
        else:
            target = _resolve_executable(command[0], armed_env)
            shebang = _read_shebang(target)
            if not shebang or _executable_basename(shebang[0]) not in _SHELL_BASENAMES:
                return armed_env, argv
            parsed = _shebang_shell_invocation(shebang, target, armed_env)
            rewrite = _restricted_shell_argv(parsed, script=target) + list(command[1:])
    except _LaunchRefusal:
        return armed_env, argv
    return _restricted_shell_environment(armed_env), [*argv[:prefix_end], *rewrite]


#: THE `os` PRIMITIVES THIS FILE REPLACES, snapshotted before any of them is replaced. Two reasons,
#: and the second is round 7's. (1) A wrapper must call the ORIGINAL and not whatever is at the name
#: when it runs, or a second `install()` in the same interpreter builds a wrapper around a wrapper.
#: (2) `os.execv` HAS NO ENVIRONMENT PARAMETER, and an admitted shell must be launched with a PATH
#: this guard chose -- so the `v` spelling is routed through the ORIGINAL `ve` spelling, which is a
#: call this module cannot make through `os.` without re-entering its own wrapper.
_WRAPPED_OS_PRIMITIVES = (
    "execv", "execve", "execvp", "execvpe", "posix_spawn", "posix_spawnp",
    "spawnv", "spawnvp", "spawnve", "spawnvpe", "spawnl", "spawnlp", "spawnle", "spawnlpe",
)


def _install_launch_guards(guard: GuardedPathFinder) -> None:
    """Wrap process-launch primitives for this guarded interpreter.

    EVERY ONE OF THEM CLASSIFIES BY THE EXECUTABLE THE KERNEL WILL RUN. That is round 7's first
    finding and it is not a `subprocess` detail: `os.execv(path, argv)`, `os.spawnv(mode, file,
    args)` and `os.posix_spawn(path, argv, env)` all take the file separately from `argv`, and
    `argv[0]` is a display name in every one of them. The table below therefore says, for each
    primitive, WHICH parameter is the executable and which is the argv, and `_prepare_launch` is
    handed the first.
    """
    originals = {name: getattr(os, name) for name in _WRAPPED_OS_PRIMITIVES if hasattr(os, name)}
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
            #: WITH `shell=True` THE SHELL IS THE EXECUTABLE, and `executable=` REPLACES it -- that
            #: is what CPython does (`subprocess.py`: `args = [unix_shell, "-c"] + args`, with
            #: `executable` overriding `unix_shell`), so a scan that read the caller's string as the
            #: program would be reading an argument to a shell it never identified.
            executable = executable or os.environ.get("COMSPEC") or "/bin/sh"
            argv = [executable, "-c", *_launch_argv(command)]
        else:
            argv = _launch_argv(command)
            executable = executable or argv[0]
        if bound.arguments.get("preexec_fn") is not None:
            #: REFUSED BEFORE ANYTHING IS SCANNED, because what it runs is not a launch this guard
            #: can read at all. CPython calls `preexec_fn` IN THE FORKED CHILD, after `fork` and
            #: before `exec` -- so it executes arbitrary caller code inside a process this guard has
            #: already armed, holding this thread's `_ApprovedLaunch` stack by inheritance, at the
            #: one instant an approval for the launch in progress is outstanding. That window is
            #: round 9's finding, and binding the ticket to the file (`_launch_file_identity`) is
            #: only the matching half of the answer: code that gets to run there can also fork
            #: again, `execve` directly, or unwind this guard's own state, and none of that is
            #: reachable by reading an argv. The launch a caller wants it for is spelled by
            #: `cwd`, `env`, `start_new_session`, `pass_fds` and `umask`, all of which this layer
            #: sees; CPython's own documentation calls `preexec_fn` unsafe with threads. Measured
            #: before it was refused: no non-test file in this repository passes it.
            _refuse_the_launch(
                _LaunchRefusal(LAUNCH_REASON_PREEXEC,
                               f"subprocess.Popen was given preexec_fn="
                               f"{bound.arguments['preexec_fn']!r}, which CPython runs in the "
                               f"forked child between fork and exec -- inside this armed process "
                               f"and inside this thread's outstanding launch approval",
                               executable=_resolve_executable(executable, env)),
                guard, argv, executable, env)
        armed_env, armed_argv = _prepare_launch(executable, argv, env, guard,
                                                bound.arguments.get("cwd"))
        if armed_env is not None:
            bound.arguments["env"] = armed_env
        if armed_argv != argv:
            # AN ARGV-LEVEL REPAIR IS ONLY REAL IF IT IS WRITTEN BACK, and round 7 made the repair
            # reach `shell=True` as well: an admitted shell is REWRITTEN to `<real bash> -r ...`,
            # which is an argv and not a string, so the launch stops being a `shell=True` launch and
            # becomes the explicit one CPython would have built. The string still runs, under `-c`,
            # with the caller's own `$0`/`$@` behind it.
            bound.arguments["args"] = armed_argv
            bound.arguments["shell"] = False
            if armed_argv[:1] != argv[:1]:
                #: `executable=` NAMED THE OLD argv[0] AND WOULD OVERRIDE THE NEW ONE. Dropping it
                #: is what makes the rewrite the thing that runs; keeping it would exec the shell
                #: the caller asked for with the restricted argv, which is the worst of both.
                bound.arguments["executable"] = None
        #: THE APPROVAL, ISSUED AROUND THE ORIGINAL CALL AND NOWHERE WIDER. `_execute_child` reaches
        #: either `_posixsubprocess.fork_exec` or `os.posix_spawn` (the latter whenever
        #: `close_fds=False`), and round 8 hooks both -- so without this the layer below re-reads a
        #: launch THIS layer rewrote, under the restricted `PATH` the rewrite carries, and refuses
        #: it. `armed_argv` is the identity to approve in all three shapes: for a rewritten launch
        #: it is what was written back, and for an untouched one it is value-identical to the argv
        #: CPython builds -- including the `[shell, "-c", string]` a surviving `shell=True` makes.
        #: AND THE FILE BESIDE IT, which is round 9's correction. `launch_file` is what the layer
        #: below will actually exec, read off the write-backs above rather than guessed: a rewritten
        #: launch runs `armed_argv[0]` (the restricted bash, by absolute path, with the caller's
        #: `executable=` dropped just above precisely so that it does), and an unrewritten one runs
        #: the `executable` this hook already normalised -- the caller's `executable=` where it gave
        #: one, the shell for a `shell=True` launch, `argv[0]` otherwise, which is CPython's own
        #: `if executable is None: executable = args[0]`. `armed_env` is the environment written
        #: back, so a bare name resolves through the PATH the child will really have.
        launch_file = armed_argv[0] if armed_argv[:1] != argv[:1] else executable
        ticket = _approve_launch(armed_argv, launch_file, armed_env)
        try:
            return original_popen_init(*bound.args, **bound.kwargs)
        finally:
            _withdraw_launch_approval(ticket)

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
        env_fallback=None,
    ) -> None:
        original = originals.get(name)
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
            armed_env, armed_argv = _prepare_launch(executable, argv, env, guard)
            original_argv = _launch_argv(argv)
            if armed_argv[:1] != original_argv[:1]:
                executable = armed_argv[0]
                if len(positional) > executable_index:
                    positional[executable_index] = executable
                else:
                    call_kwargs[executable_parameter] = executable
            if armed_argv != original_argv:
                if len(positional) > argv_index:
                    positional[argv_index] = armed_argv
                else:
                    call_kwargs[argv_parameter] = armed_argv
            if env_parameter is not None:
                if env_index is not None and len(positional) > env_index:
                    positional[env_index] = armed_env
                else:
                    call_kwargs[env_parameter] = armed_env
                return original(*positional, **call_kwargs)
            if armed_env is None:
                return original(*positional, **call_kwargs)
            #: NO ENVIRONMENT PARAMETER AND AN ENVIRONMENT TO PASS. The `v` spelling is routed
            #: through the ORIGINAL `ve` spelling of itself, which is the same system call with the
            #: environment named explicitly -- the alternative, mutating `os.environ` and hoping the
            #: exec succeeds, leaves a failed exec's parent holding an environment nobody chose.
            argv_now = (positional[argv_index] if len(positional) > argv_index
                        else call_kwargs[argv_parameter])
            return env_fallback(executable, argv_now, armed_env, positional, call_kwargs)

        setattr(os, name, guarded)

    wrap_vector_launch("execv", executable_index=0, executable_parameter="path",
                       argv_index=1, argv_parameter="argv",
                       env_fallback=lambda ex, av, en, pos, kw: originals["execve"](ex, av, en))
    wrap_vector_launch("execve", executable_index=0, executable_parameter="path",
                       argv_index=1, argv_parameter="argv", env_index=2,
                       env_parameter="env")
    wrap_vector_launch("execvp", executable_index=0, executable_parameter="file",
                       argv_index=1, argv_parameter="args",
                       env_fallback=lambda ex, av, en, pos, kw: originals["execvpe"](ex, av, en))
    wrap_vector_launch("execvpe", executable_index=0, executable_parameter="file",
                       argv_index=1, argv_parameter="args", env_index=2,
                       env_parameter="env")
    for name in ("posix_spawn", "posix_spawnp"):
        wrap_vector_launch(name, executable_index=0, executable_parameter="path",
                           argv_index=1, argv_parameter="argv", env_index=2,
                           env_parameter="env")

    def _spawn_mode(positional, call_kwargs):
        return positional[0] if positional else call_kwargs["mode"]

    wrap_vector_launch("spawnv", executable_index=1, executable_parameter="file",
                       argv_index=2, argv_parameter="args",
                       env_fallback=lambda ex, av, en, pos, kw: originals["spawnve"](
                           _spawn_mode(pos, kw), ex, av, en))
    wrap_vector_launch("spawnvp", executable_index=1, executable_parameter="file",
                       argv_index=2, argv_parameter="args",
                       env_fallback=lambda ex, av, en, pos, kw: originals["spawnvpe"](
                           _spawn_mode(pos, kw), ex, av, en))
    wrap_vector_launch("spawnve", executable_index=1, executable_parameter="file",
                       argv_index=2, argv_parameter="args", env_index=3,
                       env_parameter="env")
    wrap_vector_launch("spawnvpe", executable_index=1, executable_parameter="file",
                       argv_index=2, argv_parameter="args", env_index=3,
                       env_parameter="env")

    def wrap_spawnl(name: str, *, has_env: bool, vector: str) -> None:
        original = originals.get(name)
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
            if armed_argv[:1] != _launch_argv(argv)[:1]:
                bound.arguments["file"] = armed_argv[0]
                executable = armed_argv[0]
            if has_env:
                bound.arguments["args"] = (*armed_argv, armed_env)
                return original(*bound.args, **bound.kwargs)
            if armed_argv != _launch_argv(argv):
                bound.arguments["args"] = tuple(armed_argv)
            if armed_env is None:
                return original(*bound.args, **bound.kwargs)
            return originals[vector](bound.arguments["mode"], executable, list(armed_argv),
                                     armed_env)

        setattr(os, name, guarded)

    wrap_spawnl("spawnl", has_env=False, vector="spawnve")
    wrap_spawnl("spawnlp", has_env=False, vector="spawnvpe")
    wrap_spawnl("spawnle", has_env=True, vector="spawnve")
    wrap_spawnl("spawnlpe", has_env=True, vector="spawnvpe")

    original_system = os.system

    @functools.wraps(original_system)
    def guarded_system(command):
        """`os.system`: `/bin/sh -c <string>`, and therefore an admitted shell like any other.

        IT NO LONGER CALLS `os.system`. Round 7 makes every admitted shell run as restricted bash
        with the guard's own PATH, and `os.system` has no parameter for either -- it runs
        `/bin/sh -c` with this process's environment and nothing can be said to it. So the rewritten
        argv is spawned directly, through the ORIGINAL `Popen.__init__` so the scan does not run
        twice, and the wait status is re-encoded into the shape `os.system`'s callers read.
        """
        shell = os.environ.get("COMSPEC") or "/bin/sh"
        armed_env, armed_argv = _prepare_launch(shell, [shell, "-c", command], None, guard)
        if armed_env is None and armed_argv == [shell, "-c", command]:
            return original_system(command)
        process = subprocess.Popen.__new__(subprocess.Popen)
        #: `armed_argv[0]` IS THE FILE HERE and there is no second candidate: the call below passes
        #: no `executable=`, so CPython's `executable = args[0]` names exactly this -- the real
        #: `bash` of a restricted rewrite, or the `/bin/sh` this wrapper chose when only the
        #: environment changed.
        ticket = _approve_launch(armed_argv, armed_argv[0], armed_env)
        try:
            original_popen_init(process, armed_argv, env=armed_env)
        finally:
            _withdraw_launch_approval(ticket)
        status = process.wait()
        #: `os.system` RETURNS A WAIT STATUS AND NOT AN EXIT CODE -- `os.waitstatus_to_exitcode`'s
        #: input, not its output -- and a caller doing `os.system(...) != 0` reads either. The two
        #: encodings are re-derived here rather than guessed: a negative `returncode` is a signal.
        return (-status) & 0x7F if status < 0 else (status & 0xFF) << 8

    os.system = guarded_system

    def wrap_the_kernel_floor(module_name: str, attribute: str) -> None:
        """Hook one binding of `_posixsubprocess.fork_exec`: the floor beneath every primitive here.

        WHY A FLOOR AT ALL, WHEN THE SIXTEEN PRIMITIVES ABOVE ARE HOOKED. Because coverage
        enumerated by public API is not coverage. Round 8's reviewer called this function directly
        with `python3 -I <hijacking child>`, every signature above it unchanged, and the child ran:
        it is the last Python-visible layer before the kernel on POSIX, and `subprocess`,
        `multiprocessing`'s `spawnv_passfds` and `concurrent.futures` are all callers OF it rather
        than alternatives TO it. So this is where a launch can no longer be missed by a caller
        nobody thought of, and the primitives above are kept for the argv positions they give a
        REPAIR rather than for the coverage they were carrying.

        IT DOES NOT RE-SCAN WHAT A LAYER ABOVE ALREADY SCANNED -- see `_ApprovedLaunch`. The ticket
        is checked before anything is parsed, so a repaired launch reaches the C function exactly as
        the layer above built it.

        A FLOOR AROUND A FLOOR IS STRUCTURALLY IMPOSSIBLE, and that is what `_mnv_guard_floor`
        buys. The two bindings name ONE C function, so if the second visit ever found the first
        visit's wrapper -- a CPython that re-exported the alias, or a table that listed the same
        attribute twice -- it would wrap it, and then every `subprocess` launch would be scanned
        twice: the second time against the restricted `PATH` its own rewrite carries, which refuses
        a correct program. The marker makes that a no-op instead. It is the same concern
        `_WRAPPED_OS_PRIMITIVES` answers by snapshotting before anything is replaced.
        """
        module = sys.modules.get(module_name)
        if module is None:
            return
        original = getattr(module, attribute, None)
        if original is None or getattr(original, "_mnv_guard_floor", False):
            return

        @functools.wraps(original)
        def guarded(*call_args, **call_kwargs):
            try:
                argv, executable, cwd, env = _read_fork_exec_call(call_args, call_kwargs)
            except _LaunchRefusal as refusal:
                #: NO EXECUTABLE TO NAME, and that is the honest record: the call's shape could not
                #: be read, so the file it would have run was never established. `argv` is empty
                #: for the same reason -- reporting the raw arguments here would put whatever
                #: object sat at position 0 into a json record.
                _refuse_the_launch(refusal, guard, [], None)
            if _consume_approved_launch(argv, executable, env):
                #: THE EXECUTABLE IS PART OF WHAT IS MATCHED, and at this layer it is the file
                #: `_fork_exec_executable` says the kernel will actually run -- the first candidate
                #: that exists, not `argv[0]`. An approval issued upstairs for one file is therefore
                #: not spendable on another with the same argv, which is round 9's finding: this
                #: `return` is the line that skips the scan, and before the file was keyed it could
                #: be reached by anything running inside the window with `executable_list` of its
                #: own choosing.
                #: AND THE ENVIRONMENT REACHING THE CHILD IS CHECKED BEFORE THAT `return` RUNS,
                #: which is round 10's correction. `original(*call_args, **call_kwargs)` passes the
                #: CALLER's `env_list` -- the ticket certifies the argv and the file and never
                #: certified this -- so an in-window call matching both halves of the key while
                #: stripping only `MNV_GUARD_*` and `PYTHONPATH` used to exec an unguarded
                #: interpreter from this line. `env` is the mapping `_environment_from_fork_exec`
                #: read out of position 5, so None still means "execv, inherit this armed process's
                #: environment" and is admitted.
                _refuse_an_approved_launch_whose_environment_is_disarmed(argv, executable, env,
                                                                        guard)
                return original(*call_args, **call_kwargs)
            armed_env, armed_argv = _prepare_launch(executable, argv, env, guard, cwd)
            positional = list(call_args)
            if armed_argv != argv:
                #: THE CALLER'S OWN OBJECTS SURVIVE AN UNCHANGED LAUNCH. `argv` here is the decoded
                #: reading of position 0; writing it back unconditionally would hand the C function
                #: `str` where the caller passed `bytes`. That round-trips losslessly through
                #: `os.fsdecode`/`fsencode`, but it is a change to what the caller wrote for no
                #: reason, and this file's rule is that a repair is written back and nothing else
                #: is.
                positional[_FORK_EXEC_ARGV_INDEX] = armed_argv
            if armed_argv[:1] != argv[:1]:
                #: THE EXECUTABLE MOVES WITH THE ARGV, and at this layer it is a CANDIDATE LIST of
                #: one: a rewritten launch runs the restricted bash by absolute path, and leaving
                #: the caller's candidates in place would exec the program the caller asked for
                #: with the argv the guard chose -- the worst of both, exactly as at `Popen`.
                positional[_FORK_EXEC_EXECUTABLE_LIST_INDEX] = (os.fsencode(armed_argv[0]),)
            if armed_env is not None and armed_env is not env:
                #: WRITTEN BACK ONLY WHEN IT CHANGED. An untouched `env=` keeps the caller's own
                #: bytes rather than this guard's round-trip of them, and an untouched None stays
                #: None -- which at this layer means `execv`, i.e. inherit, and is not the same
                #: launch as an explicit copy of `os.environ`.
                positional[_FORK_EXEC_ENV_LIST_INDEX] = _fork_exec_environment_list(armed_env)
            return original(*positional, **call_kwargs)

        guarded._mnv_guard_floor = True
        setattr(module, attribute, guarded)

    for module_name, attribute in _FORK_EXEC_BINDINGS:
        wrap_the_kernel_floor(module_name, attribute)

    _install_multiprocessing_guards(guard)


#: `multiprocessing.spawn` -- the module that owns the executable EVERY `spawn` and `forkserver`
#: child is exec'd from. `multiprocessing.set_executable` and `BaseContext.set_executable` both
#: resolve to `multiprocessing.spawn.set_executable` at CALL time, so hooking the one function
#: covers all three spellings; `get_executable` is only a reader of what it stored.
_MULTIPROCESSING_SPAWN_MODULE = "multiprocessing.spawn"


def _classify_a_chosen_interpreter(chosen: str, guard: GuardedPathFinder) -> None:
    """`multiprocessing.set_executable(chosen)`: admit a Python interpreter, refuse anything else.

    WHY THE RULE HERE IS NARROWER THAN `_scan_resolved_command`'s SIX CLASSES. `set_executable`
    names a FILE and no argv: `multiprocessing` builds the child's command line itself, as
    `[chosen, *this interpreter's flags, "-c", "<spawn_main ...>"]`. So the only thing that file can
    correctly be is a PYTHON INTERPRETER -- a leaf tool, a shell script or a `git` handed `-c
    "from multiprocessing.spawn import spawn_main"` is not a launch anyone meant, and the classes
    this guard admits by REWRITING (a shell) cannot be rewritten here at all, because there is no
    argv to rewrite and `multiprocessing` will not consult one. A shell admitted by reading its
    script and then exec'd with multiprocessing's own argv would be the one admitted shell in this
    file that ran unrestricted.

    IT IS NOT THE ONLY LAYER AND IT IS NOT LOAD-BEARING ALONE. The launch itself goes through
    `spawnv_passfds` to `_posixsubprocess.fork_exec`, which this guard also hooks, so a bad choice
    is refused at spawn time even with this hook removed. What this adds is WHERE the refusal lands:
    at the line that made the choice, with the chosen file named, instead of at a launch whose argv
    `multiprocessing` assembled. Round 8's finding is that `set_executable` is public API a
    launcher may reasonably reach for -- unlike a direct `fork_exec` call -- so the diagnostic
    matters.
    """
    context = _ScanContext(os.getcwd())
    launches_python = _scan_resolved_command([chosen], os.environ, context)
    if launches_python and not context.rewrite:
        return
    raise _LaunchRefusal(
        LAUNCH_REASON_UNPROVEN,
        f"multiprocessing.set_executable({chosen!r}) chooses the file every spawn and forkserver "
        f"child is exec'd from, and multiprocessing appends its own `-c <spawn_main>` argv to it, "
        f"so the file must be a Python interpreter this guard admits and this is not one",
        executable=_resolve_executable(chosen, None))


def _guarded_set_executable(original, guard: GuardedPathFinder):
    """`multiprocessing.spawn.set_executable`, wrapped so the CHOICE is classified where it is made.

    The original still runs, and runs LAST: a refusal must leave `_python_exe` as it was, or a
    refused choice would be recorded in the module even though the launch never happened.
    """

    @functools.wraps(original)
    def guarded(executable):
        if executable is None:
            #: `set_executable(None)` NAMES NO FILE, so there is nothing to classify and refusing it
            #: would refuse a reset. It is not a hole either: `_python_exe = None` cannot produce a
            #: working launch, and the `spawnv_passfds` that follows hands the floor an
            #: `executable_list` of `[None]`, which is refused there with
            #: `LAUNCH_REASON_KERNEL_FLOOR`.
            return original(executable)
        try:
            chosen = _text_argument(executable)
        except TypeError as err:
            _refuse_the_launch(
                _LaunchRefusal(LAUNCH_REASON_UNPROVEN,
                               f"multiprocessing.set_executable was handed "
                               f"{type(executable).__name__} ({err}), which names no file this "
                               f"guard can classify"),
                guard, [], None)
        try:
            _classify_a_chosen_interpreter(chosen, guard)
        except _LaunchRefusal as refusal:
            _refuse_the_launch(refusal, guard, [chosen], chosen)
        return original(executable)

    guarded._mnv_guard_set_executable = True
    return guarded


def _install_multiprocessing_guards(guard: GuardedPathFinder) -> None:
    """Hook `multiprocessing.spawn.set_executable` if that module is loaded, else when it loads.

    LAZILY, AND THE LAZINESS IS THE POINT. Importing `multiprocessing.spawn` from `install()` would
    pull `socket`, `pickle` and a dozen more modules into EVERY guarded process -- including the
    ones started from `sitecustomize` during interpreter startup -- to hook a function most of them
    never call, and it would move the `checked` count every inventory record reports. So the module
    is hooked if it is already there, and otherwise `GuardedPathFinder` arms it at the moment the
    program imports it. The other two start methods need no hook of their own and are asserted, not
    assumed: `fork` produces a child that IS this interpreter with this guard installed, and
    `forkserver` launches through `spawnv_passfds` and is therefore covered by the `fork_exec`
    floor.
    """
    module = sys.modules.get(_MULTIPROCESSING_SPAWN_MODULE)
    if module is None:
        return
    original = getattr(module, "set_executable", None)
    if original is None or getattr(original, "_mnv_guard_set_executable", False):
        return
    module.set_executable = _guarded_set_executable(original, guard)


def _arm_restricted_shell() -> "tuple[str, dict]":
    """Pin the bash every admitted shell launch is rewritten onto, and export it for the wrappers.

    IT RETURNS A STATE RATHER THAN RAISING, for the reason recorded on `_arm_path_shim`: a
    deployment with no bash under any named prefix still guards imports and still refuses at every
    launch site. What it loses is the ability to run a shell AT ALL -- `_restricted_shell_argv`
    refuses without a pinned bash -- and that is narrower, not open, and it must be READABLE in the
    record rather than inferred from a run that suddenly refuses `bash -c ls`.
    """
    path, state = _resolve_real_bash()
    if path is None:
        os.environ.pop(REAL_BASH_ENV, None)
        return state, {"path": None, "sha256": None}
    os.environ[REAL_BASH_ENV] = path
    return state, {"path": path, "sha256": _sha256_or_none(path)}


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
            guard.shell, guard.real_bash = _arm_restricted_shell()
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
        # THE DYNAMIC HALF, as a state and the bytes that enforced it. `restricted` means every
        # admitted shell in this process ran as `<real_bash> -r` with a PATH holding the guard's
        # wrapper directories and nothing else, so what a shell program could reach was the set this
        # guard wrote a wrapper for; anything else names why it did not, and then every shell launch
        # was REFUSED rather than run unrestricted. Read it beside `declared_gap` arm (2).
        "shell": (guard.shell if guard is not None else "not-armed"),
        "real_bash": (guard.real_bash if guard is not None else {"path": None, "sha256": None}),
        # `enabled`, or `disabled-for-test`. A record carrying the second is a measurement of the
        # RESTRICTED SHELL on its own and is not evidence about a production run.
        "static_scan": (guard.static_scan if guard is not None else "enabled"),
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
