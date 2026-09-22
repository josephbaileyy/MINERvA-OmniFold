#!/usr/bin/env python3
"""THE single definition of "an executable stage line" in a shell driver.

Same pattern, and the same reason, as `tests/root_probe.py`: several detectors were each carrying
their own idea of what counts as code, they disagreed, and the disagreement was invisible until
something broke all of them at once.

WHAT THEY ALL WANT is the ORDER IN WHICH STAGES EXECUTE -- "merge+audit before unfold", "the
verifier gate before component construction". What they all DID was `text.index("<stage name>")`,
sometimes after stripping `#` comments. That works right up until the file contains prose that
NAMES the stages, and then `index()` returns the position of the prose.

⚠ IT HAS NOW HAPPENED TWICE, IN TWO DIFFERENT SYNTAXES.

  1. The stage-list COMMENT at the top of `run_p4_standard.sh` names every stage in order. The
     remedy was `_code_lines` -- strip lines starting with `#` -- and the docstring of
     `test_covariance_stages_are_still_gated` still records it.
  2. 2026-09-21, the member-axis refusal added an ABORT message telling the operator which stages
     are member-aware and how to drive them. `echo "... python3 p4_build_components.py ..."` is
     not a comment, so it survived the `#` filter and became the first occurrence -- and FOUR
     detectors in THREE files went red on a driver whose stage order had not moved at all.

THE RULE THE FIRST REMEDY ALMOST STATED: documentation is not defined by `#`. A diagnostic string
is executable, is prose, and names the things it is prose about -- which is exactly why a good
error message is useful and exactly why an occurrence detector must not count it.

So the operand is: lines that are neither comments nor output statements. Nothing else is
excluded; a stage guarded by an `if`, a `case`, or a `&&` is still a stage and still counted.
"""

_DOC_PREFIXES = ("#", "echo ", "echo\t", "printf ", "printf\t")


def stage_lines(text):
    """The executable, non-diagnostic lines of a shell script, in order."""
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(_DOC_PREFIXES):
            continue
        out.append(line)
    return out


def stage_text(text):
    """`stage_lines` rejoined, for callers that want to `.index()` into it."""
    return "\n".join(stage_lines(text))
