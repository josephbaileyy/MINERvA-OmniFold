# PTMC: the narrow confirm read of r4 (2026-11-27)

**What it was for.** The director's instruction: one narrow confirm read on codex-school2, the reader that raised the
most in round 3. It covers only whether r4's fixes are correct and complete:
- the shared blockers, the exact C-COUPLE and §7's projection;
- codex's round-3 #3, #5 and #6.

New findings count only in classes (a)–(c). There is no round 5.

**What was read.** r4 at PR head `643d1adbc`: `PTMC-DECLARATION.md` sha256
`110fa23bee365da7df366fd9b6295a220530d4272cd3447010d821a9e24a3ba3`. The 17 inputs (`inputs-sha256.txt`) were r3, the
r3→r4 diff, the round-3 reports and dispositions, the C-COUPLE receipt and script, the event loop, and the sources.

**Reader:** codex-school2, `codex exec --sandbox read-only -m gpt-6.2-sol -c model_reasoning_effort=high` (codex-cli
0.172.0), 111,423 tokens. The prompt is `prompt.txt`, sha256 `812a4422…`.

**Result:** `codex-school2-report.txt` (`cef0fe71…`, verbatim).
- CONFIRMED: #3 (lost support), #5 (moved-entry reuse) and #6 (normalization).
- NOT CONFIRMED: (i) C-COUPLE and (ii) §7, each for one class finding.
- A third class finding is new.
- The report's last line ran into the token count in the transcript ("BLOCKERS 34649-111,423"). It names three class
  findings, (a), (c) and (b).

The dispositions are in `DISPOSITION.md`.
