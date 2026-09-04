#!/usr/bin/env python3
"""OI-136: decide, for the PATH interpreter wrappers, whether a Python launch may proceed.

WHY THIS FILE EXISTS AND WHY IT IS NOT A SECOND IMPLEMENTATION. `mnv_guard_shim/bin/python3` is a
POSIX `sh` wrapper standing in front of the real interpreter on `PATH`, and it has to answer the
same two questions a guarded parent answers at its own launch sites: does this argv carry `-S`,
`-I` or `-E`, and would the child start with the propagation contract. Re-answering them in shell
would be a retyped copy of `_forbidden_python_flag`'s option grammar -- the exact defect class this
campaign files against, since the two copies pass review separately and drift silently. So the
wrapper delegates here, and this file OWNS NO GRAMMAR: it loads `mnv_guarded_run.py` from the
absolute path the contract records and calls the guard's own functions.

IT IS RUN ISOLATED, BY DESIGN, AND THAT IS NOT A CONTRADICTION. The wrapper invokes it as
`python -I -S scan_argv.py`, which is the spelling this guard refuses for a science child -- because
for a science child those flags mean "start without the guard". Here they mean the opposite: this
process must NOT install the guard, or every interpreter launch would emit an extra inventory
record for a scan that ran no science, and `-S` keeps a decision that gates every launch off
`site-packages`. It imports the standard library and the guard module and nothing else.

EXIT CODES, WHICH ARE THE WRAPPER'S CONTRACT:
    0 -- the launch may proceed
    3 -- REFUSED: an isolating startup flag, or a contract the child could not start with. The
         message is printed here, under `[oi136 launch]`, because this process is the one that
         knows which check fired.
Anything else is a scanner failure, and the wrapper treats it as a refusal too: a scan that did not
answer is not an answer.

USAGE
    scan_argv.py [--guard <mnv_guarded_run.py>] [--] <interpreter argument> ...

`<interpreter argument>` is what would follow the interpreter, WITHOUT the interpreter word. The
guard's scan takes a full argv and skips element 0, so a placeholder is prepended here -- passing
the arguments alone to a scan that skips the first one would silently ignore a leading `-I`.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

PREFIX = "[oi136 launch]"
REFUSED = 3

MODULE_ENV = "MNV_GUARD_MODULE"


def _refuse(headline: str, detail: str) -> int:
    print(f"\n{PREFIX} {headline} -- REFUSING BEFORE LAUNCH.\n"
          f"{PREFIX}   {detail}\n"
          f"{PREFIX} This launch came through the OI-136 PATH interpreter wrapper, which stands in\n"
          f"{PREFIX} front of the real interpreter so that a NON-PYTHON child's `python3 -I` is\n"
          f"{PREFIX} refused at the second launch site as well as the first. Fix the launcher, or\n"
          f"{PREFIX} route the run through mnv_guarded_run.py; do not remove the wrapper.\n",
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
    spec = importlib.util.spec_from_file_location(f"_mnv_guard_scan_{os.getpid()}", str(resolved))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load the OI-136 guard module at {resolved}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: "list[str] | None" = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    module_path = os.environ.get(MODULE_ENV) or ""
    if arguments and arguments[0] == "--guard":
        if len(arguments) < 2:
            return _refuse("THE ARGV SCANNER WAS CALLED WITHOUT ITS GUARD MODULE",
                           "--guard needs a path")
        module_path, arguments = arguments[1], arguments[2:]
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    if not module_path:
        return _refuse("THE CHILD WOULD START WITHOUT THE PROPAGATION CONTRACT",
                       f"{MODULE_ENV} is unset, so this interpreter could not install the guard "
                       f"and nothing here can re-derive it")
    try:
        guard = _load_guard(module_path)
    except BaseException as err:                       # noqa: BLE001 - reported, then refused
        return _refuse("THE ARGV SCANNER COULD NOT LOAD THE GUARD'S OWN GRAMMAR", repr(err))

    # ONE PLACEHOLDER, NOT A GUESS AT THE INTERPRETER'S NAME: the grammar walks argv[1:], and what
    # sits at argv[0] is a path fragment it deliberately never reads (`/opt/python-SIE/bin/python3`
    # is not three flags). See `_forbidden_python_flag`.
    flag = guard._forbidden_python_flag(["python", *arguments])
    if flag is not None:
        return _refuse("PYTHON STARTUP FLAGS BYPASS THE IMPORT SHIM",
                       f"offending flag {flag} in {arguments!r}: "
                       f"{guard._LAUNCH_EXPLANATIONS[guard.LAUNCH_REASON_FLAGS]}")
    missing = guard._environment_reaching_child_is_armed(None)
    if missing is not None:
        return _refuse("THE CHILD WOULD START WITHOUT THE PROPAGATION CONTRACT",
                       f"{missing} is missing or does not name the shim, so the interpreter could "
                       f"not install the guard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
