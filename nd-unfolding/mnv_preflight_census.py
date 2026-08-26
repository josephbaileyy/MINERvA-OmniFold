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

EXIT CODES: 0 clean, 2 could not look, 3 violation. A count that DISAGREES with the declaration is a
violation, in either direction: a set that shrank is as much a finding as one that grew.

WHAT IT CANNOT SAY. It reads launcher bytes; it does not run them. A guarded call whose guard is
defeated at runtime (a wrong --expect-root, a subprocess boundary) is outside its reach and belongs
to `test_mnv_guarded_run.TheSubprocessBoundaryIsNotCovered` and the dynamic arms of the launcher
suite. It also says nothing about python invoked as anything other than the literal token `python3`.
"""
import argparse
import json
import os
import pathlib
import re
import sys

OK_EXIT = 0
CANNOT_CHECK_EXIT = 2
VIOLATION_EXIT = 3

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
    excluded_vars = [t["shell_var"] for t in decl["excluded_tools"]]
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
        for tool in decl["excluded_tools"]:
            want = f'{tool["shell_var"]}="${{CODE_ROOT}}/{tool["resolves_to"]}"'
            if want not in text:
                v.append(f'{sh}: ${tool["shell_var"]} does not resolve to '
                         f'{tool["resolves_to"]}. Expected the literal definition {want!r}. '
                         f'A declared exclusion is only as good as what the name points at.')

        parts = classify(text, excluded_vars, decl)
        for k in ("guarded", "excluded", "probe", "unknown", "commented"):
            totals[k] += len(parts[k])
        for ln, src in parts["unknown"]:
            v.append(f"{sh}:{ln}: UNCLASSIFIED python3 invocation -- neither routed through "
                     f"mnv_guarded_run.py nor a declared preflight tool. This is the widening "
                     f"ruling 21 fixed the boundary against.\n      {src[:160]}")
        # Per-launcher shape, so a compensating error (one launcher loses a preflight call while
        # another gains one) cannot cancel out in the total.
        for tool in decl["excluded_tools"]:
            want_n = tool["per_launcher"]
            got_n = sum(1 for _, s in parts["excluded"] if f'"${tool["shell_var"]}"' in s)
            if got_n != want_n:
                v.append(f'{sh}: expected {want_n} ${tool["shell_var"]} invocation(s), found '
                         f'{got_n}. Totals can hide this; per-launcher counts cannot.')

    c = decl["counts"]
    checks = (("launchers", totals["launchers"], c["launchers"]),
              ("guarded", totals["guarded"], c["guarded"]),
              ("excluded_preflight", totals["excluded"], c["excluded_preflight"]),
              ("unclassified", totals["unknown"], c["unclassified"]),
              ("inline_interpreter_probes", totals["probe"],
               c.get("inline_interpreter_probes", 0)),
              ("non_comment_python3_invocations",
               totals["guarded"] + totals["excluded"] + totals["probe"] + totals["unknown"],
               c["non_comment_python3_invocations"]),
              ("commented_out_python3_lines", totals["commented"],
               decl["commented_out_python3_lines"]))
    for name, got, want in checks:
        if got != want:
            v.append(f"COUNT {name}: measured {got}, declared {want}. Identity, not a floor -- a "
                     f"set that shrank is as much a finding as one that grew.")
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
    if decl.get("schema") != "mnv_preflight_exclusions/1":
        print(f"[preflight-census] COULD NOT LOOK: schema is {decl.get('schema')!r}, expected "
              f"'mnv_preflight_exclusions/1'", file=sys.stderr)
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
    if violations:
        for line in violations:
            print(f"[preflight-census] VIOLATION: {line}", file=sys.stderr)
        print(f"[preflight-census] {len(violations)} violation(s)", file=sys.stderr)
        return VIOLATION_EXIT
    print("[preflight-census] OK: every python3 invocation is guarded or declared")
    return OK_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
