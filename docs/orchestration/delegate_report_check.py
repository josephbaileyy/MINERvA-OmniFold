#!/usr/bin/env python3
"""Decide whether a delegate dispatch actually produced a report.

WHY THIS EXISTS (BEN-390). Neither of the two signals a dispatcher naturally reaches for is
sound:

  * The EXIT CODE is not a success signal in either direction. `agy -p` returns **0** while
    printing only a permission-denial notice (measured 2026-08-17). `codex exec` returned **0**
    on a usage-limit failure at 11:50Z and **1** on the same failure text at 13:05Z and again at
    ~16:22Z; the discriminator is not known.
  * The ABSENCE OF A KNOWN ERROR STRING is not a success signal either. The three delegates word
    exhaustion three different ways ("You've hit your usage limit" / "Your workspace is out of
    credits" / a permission denial that is not a quota error at all), so a predicate keyed to one
    phrase silently does not fire.

So the check below is ordered deliberately: the PRIMARY test is that the report file is non-empty
AND matches the format the dispatch required (`--require-regex`). The failure-signature table is a
SUPPLEMENT that buys a better diagnostic, and it is by construction incomplete — every entry in it
was discovered one dispatch at a time. Do not add a signature and consider the class closed.

`--require-regex` is what makes this check falsifiable, because "non-empty" alone passes a failed
dispatch: agy's denial notice is 303 bytes of fluent prose.

Usage:
    delegate_report_check.py REPORT [--require-regex RE] [--prompt-file P] [--log LOG]

Exit codes: 0 = report present and well-formed; 2 = dispatch failed (reason on stdout);
3 = usage error. Never 1, so a crash of this script is distinguishable from a verdict.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# (label, regex) — every one of these was OBSERVED, not anticipated. Sources in
# FINDING-20260817-a-delegate-failure-has-no-reliable-signal.md.
FAILURE_SIGNATURES: list[tuple[str, str]] = [
    ("codex: personal-account usage limit", r"You've hit your usage limit"),
    ("codex: workspace out of credits", r"Your workspace is out of credits"),
    ("agy: headless permission auto-denial", r"no output produced.*permission|permission that headless mode cannot prompt"),
    ("codex: cwd not a trusted directory", r"Not inside a trusted directory"),
    ("generic quota/limit wording", r"(?i)\b(usage limit|session limit|rate limit|out of credits|quota exceeded|insufficient credit)\b"),
]

# NOT a member of FAILURE_SIGNATURES, deliberately. `codex exec` prints this line on EVERY run,
# including successful ones and including runs given `< /dev/null` — measured, it is in the log of
# both probes that reached the API. As a substring match it fires on every codex log ever captured,
# which is BEN-381's shape: a check that fires on the healthy case gets switched off. It is a real
# failure only when it is the WHOLE output, i.e. the process blocked on stdin and produced nothing
# else.
STDIN_BLOCK_LINE = "Reading additional input from stdin"
STDIN_BLOCK_LABEL = "codex: blocked on stdin, produced nothing (needs `< /dev/null`)"


def _stdin_block_reason(text: str, where: str) -> list[str]:
    body = text.replace(STDIN_BLOCK_LINE, "").strip(" .\n\r\t")
    if STDIN_BLOCK_LINE in text and not body:
        return [f"FAILURE SIGNATURE in {where} [{STDIN_BLOCK_LABEL}]: {' '.join(text.split())}"]
    return []

PROMPT_ECHO_RATIO = 0.9


def evaluate(
    report: Path,
    require_regex: str | None = None,
    prompt_file: Path | None = None,
    log: Path | None = None,
) -> tuple[bool, list[str]]:
    """Return (ok, reasons). ok is True only if every enabled test passes."""
    reasons: list[str] = []

    if not report.exists():
        reasons.append(f"MISSING: report file {report} was never created")
        # A missing report is terminal; the remaining tests have nothing to read. The delegate
        # log is still worth scanning, because that is where the actual error text lives.
        reasons.extend(_scan_log(log))
        return False, reasons

    text = report.read_text(errors="replace")
    if not text.strip():
        reasons.append(f"EMPTY: report file {report} is {len(text)} bytes of whitespace")
        reasons.extend(_scan_log(log))
        return False, reasons

    for label, pattern in FAILURE_SIGNATURES:
        if re.search(pattern, text):
            reasons.append(f"FAILURE SIGNATURE in report [{label}]: {_excerpt(text, pattern)}")
    reasons.extend(_stdin_block_reason(text, "report"))

    if prompt_file is not None:
        prompt = prompt_file.read_text(errors="replace").strip()
        if prompt and _is_echo(prompt, text.strip()):
            reasons.append(
                "PROMPT ECHO: the report is the dispatch prompt handed back, not a result "
                f"({len(text.strip())} B report vs {len(prompt)} B prompt)"
            )

    if require_regex is not None and not re.search(require_regex, text, re.MULTILINE | re.DOTALL):
        reasons.append(
            f"FORMAT: report does not match the required final-message format /{require_regex}/ "
            "— this is the primary test; the signature table above is only a diagnostic"
        )

    reasons.extend(_scan_log(log))
    return (not reasons), reasons


def _scan_log(log: Path | None) -> list[str]:
    """A well-formed report does not clear a log that names a failure, and vice versa."""
    if log is None or not log.exists():
        return []
    text = log.read_text(errors="replace")
    out = []
    for label, pattern in FAILURE_SIGNATURES:
        if re.search(pattern, text):
            out.append(f"FAILURE SIGNATURE in log [{label}]: {_excerpt(text, pattern)}")
    out.extend(_stdin_block_reason(text, "log"))
    return out


def _is_echo(prompt: str, report: str) -> bool:
    if report == prompt:
        return True
    # A report that is mostly the prompt verbatim and adds nothing of its own.
    return prompt in report and len(prompt) >= PROMPT_ECHO_RATIO * len(report)


def _excerpt(text: str, pattern: str, width: int = 160) -> str:
    m = re.search(pattern, text)
    if m is None:
        return ""
    start = max(0, m.start() - 20)
    return " ".join(text[start : start + width].split())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Verify that a delegate dispatch produced a real report (BEN-390).",
    )
    ap.add_argument("report", type=Path, help="the delegate's report / --output-last-message file")
    ap.add_argument(
        "--require-regex",
        help="regex the report MUST match (the dispatch's required final-message format). "
        "Omitting it weakens this check to 'non-empty and no known error string', which is "
        "exactly the check BEN-390 says is unsound.",
    )
    ap.add_argument("--prompt-file", type=Path, help="the dispatched prompt, to catch an echo")
    ap.add_argument("--log", type=Path, help="the delegate's full stdout/stderr log")
    args = ap.parse_args(argv)

    if not args.report:
        print("usage error: no report path", file=sys.stderr)
        return 3

    ok, reasons = evaluate(args.report, args.require_regex, args.prompt_file, args.log)
    if ok:
        note = "" if args.require_regex else "  (NO --require-regex: format unverified)"
        print(f"DELEGATE-REPORT OK :: {args.report}{note}")
        return 0
    print(f"DELEGATE-REPORT FAILED :: {args.report}")
    for r in reasons:
        print(f"  - {r}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
