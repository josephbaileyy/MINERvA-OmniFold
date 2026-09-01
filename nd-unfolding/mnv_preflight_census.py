#!/usr/bin/env python3
"""Census every python3 invocation in the k=0 launchers and classify it GUARDED / EXCLUDED / UNKNOWN.

Gate-1 F-7(a): sixteen preflight `python3` calls are deliberately outside the import guard, but the
exclusion was IMPLICIT -- nothing named the sixteen, and nothing failed if a seventeenth appeared.
The only `python3` regex in the launcher suite SELECTS guarded calls
(`test_k0_launcher_two_roots.py`, `re.search(r'python3 "\\$GUARD" --expect-root', l)`), so an added
`python3 whatever.py` matched nothing and was invisible to the whole suite. This instrument is the
opposite direction: it enumerates FIRST and classifies SECOND, so an invocation that is neither
guarded nor declared is a VIOLATION rather than a silence.

WHAT IT ANCHORS ON, and why not line numbers. The declaration names the shell VARIABLE (`$SRCMAN`,
`$PARITY`) and the path that variable must resolve to. Line numbers move on every edit; a variable
plus its definition is stable and still catches the two mutations that matter -- repointing the
variable at a different tool, and adding a new unguarded call.

WHAT IT ENFORCES SINCE OI-185, AND WHY THAT IS DIFFERENT FROM WHAT IT USED TO.
Authority: Joseph, 2026-09-01, recorded verbatim in
`docs/orchestration/DECISION-20260901-joseph-ratifies-oi185-invariants.md`
-- which reproduces the recommendation his ruling accepts, because 'I like your recommendation,
do it' takes all of its content from the recommendation. Cite that file, not this sentence.
It used to compare five AUTHORED totals against the declaration. Four of them -- excluded_preflight,
inline_interpreter_probes, non_comment_python3_invocations and launchers -- were magic numbers that
moved every time a preflight tool was added, cost a ruling on each move, and protected nothing the
per-launcher per-tool checks did not already cover. They are gone. What is enforced now:

  * `guarded == 14`      -- RULING 21's pin, the only count still needing a ruling to move.
  * `unclassified == 0`  -- F-7(a)'s invariant. Zero is not a magic number.
  * `commented_out == 18`-- a TRIPWIRE, kept pinned deliberately; it is not part of the boundary.
  * for EVERY declared exclusion, in EVERY declared launcher: the entry is structurally complete,
    the shell variable resolves to the declared path, it is invoked exactly `per_launcher` times,
    and its executing copy is A-3 `--pair` BOUND. The last of these is new at OI-185 -- it was
    verified by hand when the row was filed and is now machine-checked.
  * the derived totals are INTERNALLY CONSISTENT with the declaration's own per-launcher structure,
    which closes the one hole the per-tool counts leave (two tool variables on a single line would
    be classified once and counted twice).

The boundary (`guarded + excluded`) is DERIVED and PRINTED, never authored. Cite this tool's output,
not a number copied out of the declaration.

A fifth criterion -- an excluded tool's repository imports must be a SUBSET OF {mnv_guarded_run},
i.e. the guard has nothing to contain but itself -- cannot be checked from bytes because it requires
executing the tool. It lives in tests/test_k0_preflight_exclusion_census.py and has a power arm.

EXIT CODES: 0 clean, 2 could not look, 3 violation. A count that DISAGREES is a violation in either
direction: a set that shrank is as much a finding as one that grew.

WHAT IT CANNOT SAY. It reads launcher bytes; it does not run them. A guarded call whose guard is
defeated at runtime (a wrong --expect-root, a subprocess boundary) is outside its reach and belongs
to `test_mnv_guarded_run.TheSubprocessBoundaryIsNotCovered` and the dynamic arms of the launcher
suite. It also says nothing about python invoked as anything other than the literal token `python3`.
"""
import argparse
import json
import pathlib
import re
import sys

OK_EXIT = 0
CANNOT_CHECK_EXIT = 2
VIOLATION_EXIT = 3

#: Bumped when `counts` was replaced by `pinned_counts` + invariants (OI-185; authority in
#: docs/orchestration/DECISION-20260901-joseph-ratifies-oi185-invariants.md).
#: A v1 declaration is
#: REFUSED rather than read: its `counts` block means something this code no longer enforces, and
#: silently applying v2 semantics to a v1 file is the mismatched-pair failure, not a compatibility
#: nicety. Fail closed.
SCHEMA = "mnv_preflight_exclusions/2"

#: Required, non-empty keys on every `excluded_tools` entry. An exclusion that does not say what it
#: resolves to or why is not a declaration, it is a hole with a name.
REQUIRED_TOOL_KEYS = ("shell_var", "resolves_to", "role", "per_launcher")

ND = pathlib.Path(__file__).resolve().parent

GUARDED_RE = re.compile(r'python3 "\$GUARD" --expect-root')
#: A `python3` token that is not inside a comment. Deliberately loose: the point is to catch calls
#: the declaration does NOT anticipate, so over-matching here is safe and under-matching is not.
PY_TOKEN = "python3"


def classify(text: str, excluded_vars: list[str], decl: dict) -> dict:
    """Partition a launcher's python3 lines. Comments are counted, never silently dropped."""
    excl_re = re.compile(r'python3 "\$(' + "|".join(re.escape(v) for v in excluded_vars) + r')"')
    # THIRD CATEGORY, round 6: an interpreter capability probe invokes python3 itself and no
    # repository module, so the guard has nothing to contain. Declared, counted, and pinned --
    # not waved through, which is what "unclassified" would have become if the pin were bumped.
    probes = [m for e in decl.get("excluded_inline_probes", []) for m in e["match_any"]]
    out = {"guarded": [], "excluded": [], "probe": [], "unknown": [], "commented": []}
    for i, line in enumerate(text.splitlines(), 1):
        if PY_TOKEN not in line:
            continue
        if line.lstrip().startswith("#"):
            out["commented"].append((i, line.strip()))
            continue
        if GUARDED_RE.search(line):
            out["guarded"].append((i, line.strip()))
        elif excl_re.search(line):
            out["excluded"].append((i, line.strip()))
        elif any(m in line for m in probes):
            out["probe"].append((i, line.strip()))
        else:
            out["unknown"].append((i, line.strip()))
    return out


def census(decl: dict, nd: pathlib.Path = ND) -> tuple[list[str], dict]:
    """Return (violations, totals). An empty violation list is the only clean result."""
    v: list[str] = []
    tools = decl["excluded_tools"]

    # OI-185 criterion (1). An entry missing `resolves_to` or `role` is not a declaration, it is a
    # hole with a name -- and under the old authored totals it could be added without anything
    # failing so long as the numbers were bumped to match. Checked before anything reads the keys.
    for i, tool in enumerate(tools):
        for key in REQUIRED_TOOL_KEYS:
            if key not in tool or tool[key] == "" or tool[key] is None:
                v.append(f"excluded_tools[{i}]: required key {key!r} is missing or empty. An "
                         f"exclusion that does not say what it resolves to, or why, is not a "
                         f"declaration.")
    if v:
        # Every later check indexes these keys; continuing would raise KeyError and be reported as
        # COULD NOT LOOK, which is a different and weaker statement than the violation we have.
        return v, {"guarded": 0, "excluded": 0, "probe": 0, "unknown": 0,
                   "commented": 0, "launchers": 0}

    excluded_vars = [t["shell_var"] for t in tools]
    totals = {"guarded": 0, "excluded": 0, "probe": 0, "unknown": 0, "commented": 0, "launchers": 0}

    for sh in decl["launchers"]:
        p = nd / sh
        if not p.is_file():
            v.append(f"{sh}: declared launcher is ABSENT from {nd}. A missing launcher is a "
                     f"failure, not a gap -- the census cannot speak for a file it never read.")
            continue
        text = p.read_text(encoding="utf-8")
        totals["launchers"] += 1

        # The variable must still point where the declaration says. Repointing $SRCMAN at another
        # tool would otherwise sail through as a declared exclusion.
        for tool in tools:
            want = f'{tool["shell_var"]}="${{CODE_ROOT}}/{tool["resolves_to"]}"'
            if want not in text:
                v.append(f'{sh}: ${tool["shell_var"]} does not resolve to '
                         f'{tool["resolves_to"]}. Expected the literal definition {want!r}. '
                         f'A declared exclusion is only as good as what the name points at.')

            # OI-185 criterion (4). A preflight tool is excluded from the GUARD; it is NOT excluded
            # from BINDING, and the A-3 --pair entry is the protection that actually applies to it.
            # Before OI-185 this was true of all three tools and asserted by nobody -- it was
            # verified by hand when the row was filed, which is exactly the state F-7(a) objects to.
            pair = f'--pair "${{{tool["shell_var"]}}}={tool["resolves_to"]}"'
            if pair not in text:
                v.append(f'{sh}: ${tool["shell_var"]} is a declared preflight exclusion but its '
                         f'executing copy is NOT --pair bound. Expected the literal {pair!r}. '
                         f'Excluded from the guard is not excluded from binding.')

        parts = classify(text, excluded_vars, decl)
        for k in ("guarded", "excluded", "probe", "unknown", "commented"):
            totals[k] += len(parts[k])
        for ln, src in parts["unknown"]:
            v.append(f"{sh}:{ln}: UNCLASSIFIED python3 invocation -- neither routed through "
                     f"mnv_guarded_run.py nor a declared preflight tool. This is the widening "
                     f"ruling 21 fixed the boundary against.\n      {src[:160]}")
        # Per-launcher shape, so a compensating error (one launcher loses a preflight call while
        # another gains one) cannot cancel out in the total.
        for tool in tools:
            want_n = tool["per_launcher"]
            got_n = sum(1 for _, s in parts["excluded"] if f'"${tool["shell_var"]}"' in s)
            if got_n != want_n:
                v.append(f'{sh}: expected {want_n} ${tool["shell_var"]} invocation(s), found '
                         f'{got_n}. Totals can hide this; per-launcher counts cannot.')

    # ---- THE THREE PINS ------------------------------------------------------------------
    # OI-185 replaced the authored totals with invariants (record cited in the module docstring).
    # What survives as a
    # pinned number is only what a human decision actually fixed.
    pins = decl["pinned_counts"]
    for name, got, want in (("guarded", totals["guarded"], pins["guarded"]),
                            ("unclassified", totals["unknown"], pins["unclassified"]),
                            ("commented_out_python3_lines", totals["commented"],
                             pins["commented_out_python3_lines"])):
        if got != want:
            v.append(f"PIN {name}: measured {got}, pinned {want}. Identity, not a floor -- a set "
                     f"that shrank is as much a finding as one that grew. `guarded` is ruling 21's "
                     f"pin and moving it needs a ruling; the other two are invariants, not tallies.")

    # ---- DERIVED, NOT AUTHORED -----------------------------------------------------------
    # These used to be numbers a human wrote into the declaration and bumped on every change. They
    # are now computed FROM THE DECLARATION'S OWN STRUCTURE, so adding a principled preflight tool
    # moves them automatically and needs no ruling -- while an UNDECLARED call still lands in
    # `unknown` and still fails. The consistency check is not redundant with the per-launcher counts:
    # a single line naming two tool variables classifies once and counts twice, and only this
    # catches it.
    n_launchers = len(decl["launchers"])
    if totals["launchers"] != n_launchers:
        v.append(f"launchers: read {totals['launchers']} of {n_launchers} declared. A launcher the "
                 f"census could not read is a failure, not a gap.")
    else:
        want_excluded = sum(tool["per_launcher"] for tool in tools) * n_launchers
        if totals["excluded"] != want_excluded:
            v.append(f"DERIVED excluded_preflight: classified {totals['excluded']} line(s), but the "
                     f"declaration's own per-launcher structure implies {want_excluded} "
                     f"({'+'.join(str(t['per_launcher']) for t in tools)} per launcher x "
                     f"{n_launchers}). The two disagree, so at least one line carries more than one "
                     f"declared tool variable and the per-tool counts cannot see it.")
        want_probes = sum(e.get("per_launcher", 0)
                          for e in decl.get("excluded_inline_probes", [])) * n_launchers
        if totals["probe"] != want_probes:
            v.append(f"DERIVED inline_interpreter_probes: classified {totals['probe']}, structure "
                     f"implies {want_probes}.")
    return v, totals


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mnv_preflight_census.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--declaration",
                    default=str(ND / "mnv_preflight_exclusions.json"),
                    help="the mnv_preflight_exclusions/1 record to check against")
    ap.add_argument("--nd-dir", default=str(ND),
                    help="directory holding the launchers (the test fixture repoints this)")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    try:
        with open(a.declaration, encoding="utf-8") as fh:
            decl = json.load(fh)
    except (OSError, ValueError) as err:
        print(f"[preflight-census] COULD NOT LOOK: cannot read {a.declaration}: {err}",
              file=sys.stderr)
        return CANNOT_CHECK_EXIT
    if decl.get("schema") != SCHEMA:
        print(f"[preflight-census] COULD NOT LOOK: schema is {decl.get('schema')!r}, expected "
              f"{SCHEMA!r}. A v1 declaration is REFUSED, not read: its `counts` block pins totals "
              f"this code no longer enforces, and reading it under v2 semantics would silently "
              f"drop four checks.", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    nd = pathlib.Path(a.nd_dir).resolve()
    if not nd.is_dir():
        print(f"[preflight-census] COULD NOT LOOK: no such directory {nd}", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    try:
        violations, totals = census(decl, nd)
    except OSError as err:
        print(f"[preflight-census] COULD NOT LOOK: {err}", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    print(f"[preflight-census] {totals['launchers']} launcher(s): "
          f"{totals['guarded']} guarded + {totals['excluded']} declared-preflight + "
          f"{totals['probe']} interpreter-probe + {totals['unknown']} unclassified = "
          f"{totals['guarded'] + totals['excluded'] + totals['probe'] + totals['unknown']} non-comment python3 "
          f"invocation(s); {totals['commented']} commented out")
    # DERIVED at read time, deliberately not stored anywhere. Cite this line, not a number copied
    # out of the declaration -- that is what let the boundary go stale between rulings.
    print(f"[preflight-census] guarding boundary (guarded + declared-preflight) = "
          f"{totals['guarded'] + totals['excluded']}, DERIVED")
    if violations:
        for line in violations:
            print(f"[preflight-census] VIOLATION: {line}", file=sys.stderr)
        print(f"[preflight-census] {len(violations)} violation(s)", file=sys.stderr)
        return VIOLATION_EXIT
    print("[preflight-census] OK: every python3 invocation is guarded or declared")
    return OK_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
