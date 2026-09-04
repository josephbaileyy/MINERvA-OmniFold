#!/usr/bin/env python3
"""OI-136: decide, for the committed PATH wrappers, what a non-interpreter launch may exec.

WHY THIS FILE EXISTS AND WHY IT IS NOT A SECOND IMPLEMENTATION. Round 7 makes every admitted shell
run as `bash -r` with a PATH holding the guard's wrapper directories and NOTHING ELSE. That is what
turns bash's own restricted mode into the enforcement -- a command name with a slash is refused by
the shell, so every program a shell program reaches is resolved through that PATH, and the set of
programs it can reach is exactly the set this directory holds a wrapper for. The wrappers therefore
have to answer the questions `mnv_guarded_run.py` answers at its own launch sites: is this `git`
read-only, is this `sbatch`'s batch script scannable, does this `bash` re-enter restricted mode.
Re-answering them in shell would be `_scan_git`, `_scan_sbatch` and `_parse_shell_invocation`
retyped -- the exact defect class this campaign files against, since the copies pass review
separately and drift silently. So the wrappers delegate here, and this file OWNS NO GRAMMAR: it
loads `mnv_guarded_run.py` from the absolute path the contract records and calls the guard's own
functions. `mnv_guard_shim/scan_argv.py` is the same design for the interpreter wrappers.

IT IS RUN ISOLATED, BY DESIGN. The wrapper invokes it as `python -I -S wrapper_exec.py`, which is
the spelling this guard refuses for a science child -- because for a science child those flags mean
"start without the guard". Here they mean the opposite: this process must NOT install the guard, or
every `ls` in a restricted script would emit an inventory record for a scan that ran no science, and
the launch hooks would wrap an `os.execv` this file is about to make on purpose.

IT EXECS RATHER THAN PRINTING A PATH. POSIX `sh` has no arrays, so handing an argv back to the
wrapper would mean re-quoting it and re-splitting it -- two chances to change what runs. `os.execv`
replaces this process instead, so the program the wrapper resolves is the program that runs and
there is no second parse between the decision and the exec.

ROLES, WHICH ARE THE WRAPPERS' CONTRACT:
    shell   -- bash/sh: refuse the options the guard refuses, then exec the pinned real bash with
               `-r` (and `--posix` for `sh`) and the same wrapper-only PATH
    git     -- the read-only subcommand allowlist and the hostile-environment rule, then exec
    sbatch  -- scan the batch script or `--wrap` string statically, then exec
    srun    -- scan the command it will run, then exec
    forward -- exec the system tool of this wrapper's own name; nothing is read

EXIT CODES:
    3   -- REFUSED, under `[oi136 launch]`, by one of the guard's own checks
    127 -- this host has no such tool under a named system prefix, which is what the restricted
           shell would have said itself had the wrapper not been committed
Anything else is a wrapper failure, and a wrapper that did not answer is not an answer.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

PREFIX = "[oi136 launch]"
REFUSED = 3
NO_SUCH_TOOL = 127

MODULE_ENV = "MNV_GUARD_MODULE"


def _refuse(headline: str, detail: str) -> int:
    print(f"\n{PREFIX} {headline} -- REFUSING BEFORE LAUNCH.\n"
          f"{PREFIX}   {detail}\n"
          f"{PREFIX} This launch came through an OI-136 PATH wrapper. A guarded process runs every\n"
          f"{PREFIX} admitted shell as restricted bash whose PATH is this wrapper directory, so the\n"
          f"{PREFIX} wrapper is the only way the program could have reached this tool. Fix the\n"
          f"{PREFIX} launcher, or route the work through mnv_guarded_run.py; do not remove the\n"
          f"{PREFIX} wrapper.\n",
          file=sys.stderr, flush=True)
    return REFUSED


def _load_guard(module_path: str):
    """Load `mnv_guarded_run.py` from an ABSOLUTE path, never through the import path.

    Resolving it as a module would recreate the ambiguity the guard exists to refuse -- and this
    process runs isolated, so there is no import path to resolve it through anyway.
    """
    resolved = pathlib.Path(module_path)
    if not resolved.is_absolute() or not resolved.is_file():
        raise RuntimeError(f"the recorded guard module is not a readable absolute path: "
                           f"{module_path!r}")
    spec = importlib.util.spec_from_file_location(f"_mnv_guard_wrap_{os.getpid()}", str(resolved))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load the OI-136 guard module at {resolved}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exec_the_system_tool(guard, name: str, arguments: list) -> int:
    """`os.execv` the tool of this wrapper's own name, resolved from a named system prefix.

    RESOLVED BY THE GUARD'S OWN RESOLVER and not by a `PATH` lookup: inside a restricted shell the
    only `PATH` is this wrapper directory, so a lookup would find this wrapper again and the exec
    would be a loop. `_locate_a_system_tool` also refuses a shebang text file, which is what keeps a
    site's `/usr/local/bin/git` shell wrapper from being trusted by its name.
    """
    resolved = guard._locate_a_system_tool(name)
    if resolved is None:
        print(f"{PREFIX} {name}: no such tool under any of "
              f"{', '.join(guard._SYSTEM_EXECUTABLE_PREFIXES)}", file=sys.stderr, flush=True)
        return NO_SUCH_TOOL
    os.execv(resolved, [name, *arguments])
    return REFUSED                           # unreachable: execv does not return


def _role_shell(guard, name: str, arguments: list) -> int:
    """`bash`/`sh` reached from inside a restricted shell: re-enter restricted mode.

    THE POINT IS RE-ENTRY AND NOT A SECOND SCAN. The program this shell will run is already inside
    the restricted world -- it was reached through this PATH, from a shell that could not name a
    file with a slash -- so what has to hold is that the CHILD shell is restricted too. A `bash`
    that dropped `-r` would be one line of a restricted script buying an unrestricted shell, which
    is the whole enforcement undone by the most ordinary command in it.
    """
    parsed = guard._parse_shell_invocation([name, *arguments], os.environ)
    argv = guard._restricted_shell_argv(parsed)
    os.execve(argv[0], argv, guard._restricted_shell_environment(os.environ))
    return REFUSED                           # unreachable


def _role_git(guard, name: str, arguments: list) -> int:
    """`git`: the guard's own read-only allowlist and hostile-environment rule, then exec."""
    guard._scan_git([name, *arguments], os.environ, name)
    return _exec_the_system_tool(guard, name, arguments)


def _role_sbatch(guard, name: str, arguments: list) -> int:
    """`sbatch`: the batch script or `--wrap` string is READ NOW or the submission is refused now.

    This is the one role where the static model IS the enforcement, and it is the same reason the
    guard gives at its own launch sites: the job script runs on a compute node, in another process
    tree, where no restricted shell and no wrapper directory of ours exists. Arm (3) of the guard's
    `DECLARED_GAP` states exactly that residual.
    """
    context = guard._ScanContext(os.getcwd(), in_shell=False)
    guard._refuse_runtime_tokens([name, *arguments], "sbatch token")
    guard._scan_sbatch([name, *arguments], os.environ, context, name)
    guard._refuse_write_then_execute(context)
    return _exec_the_system_tool(guard, name, arguments)


def _role_srun(guard, name: str, arguments: list) -> int:
    """`srun`: the command it runs is classified exactly as a direct launch would be."""
    command = [name, *arguments]
    index = guard._parse_wrapper(command, guard._WRAPPER_SPECS["srun"])
    if index is not None:
        context = guard._ScanContext(os.getcwd(), in_shell=False)
        guard._refuse_runtime_tokens(command, "srun token", stop=index)
        guard._scan_resolved_command(command[index:], os.environ, context)
        guard._refuse_write_then_execute(context)
    return _exec_the_system_tool(guard, name, arguments)


def _role_forward(guard, name: str, arguments: list) -> int:
    """A Slurm client that submits or reports and runs nothing locally. Nothing is read."""
    return _exec_the_system_tool(guard, name, arguments)


_ROLES = {
    "shell": _role_shell,
    "git": _role_git,
    "sbatch": _role_sbatch,
    "srun": _role_srun,
    "forward": _role_forward,
}


def main(argv: "list[str] | None" = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    role = name = ""
    while arguments and arguments[0] in ("--role", "--name"):
        if len(arguments) < 2:
            return _refuse("THE WRAPPER EXECUTOR WAS CALLED WITHOUT ITS ROLE",
                           f"{arguments[0]} needs a value")
        if arguments[0] == "--role":
            role = arguments[1]
        else:
            name = arguments[1]
        arguments = arguments[2:]
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    if role not in _ROLES or not name:
        return _refuse("THE WRAPPER EXECUTOR WAS CALLED WITH NO ROLE OR NO NAME",
                       f"role={role!r} name={name!r}; the committed wrappers pass both")
    module_path = os.environ.get(MODULE_ENV) or ""
    if not module_path:
        return _refuse("THE CHILD WOULD START WITHOUT THE PROPAGATION CONTRACT",
                       f"{MODULE_ENV} is unset, so this wrapper could not load the guard's own "
                       f"grammar and nothing here can re-derive it")
    try:
        guard = _load_guard(module_path)
    except BaseException as err:                       # noqa: BLE001 - reported, then refused
        return _refuse("THE WRAPPER EXECUTOR COULD NOT LOAD THE GUARD'S OWN GRAMMAR", repr(err))
    try:
        return _ROLES[role](guard, name, arguments)
    except guard._LaunchRefusal as refusal:
        return _refuse(guard._LAUNCH_HEADLINES[refusal.reason], str(refusal))
    except OSError as err:
        return _refuse(f"THE WRAPPER FOR {name} COULD NOT EXEC THE SYSTEM TOOL", repr(err))


if __name__ == "__main__":
    sys.exit(main())
