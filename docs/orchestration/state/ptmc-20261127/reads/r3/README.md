# PTMC declaration reads, round 3, the last (2026-11-27)

**What was read.** DRAFT r3 at branch commit `ea1004efa`: `PTMC-DECLARATION.md` sha256
`c94be93248d2c34a6883b7113f07862147849768a80fce6e5a27f0798aa43320`.
- The readers also had its scoping, the round-2 reports and their dispositions, the stat-d4 receipt, and the sources:
  18 files in all, listed in `inputs-sha256.txt`. They included REF-C2C1's `config.json` both at M and on main.
- The two readers' copies were identical.

**The prompt** is `prompt.txt` (`6231dc5f…`). It applies the director's scope rule. A BLOCKER is only:
- (a) a wrong printed number or an over-reaching statement;
- (b) a gate that would pass a defective run;
- (c) a false STOP of a correct run.

**The readers** (Grok is unfunded):

| reader | invocation | report |
|---|---|---|
| codex-school2 | `codex exec --sandbox read-only -m gpt-6.2-sol -c model_reasoning_effort=high` (codex-cli 0.172.0); 127,621 tokens | `codex-school2-report.txt`: BLOCKERS 6, MAJOR 3, MINOR 1 |
| agy | `agy -p … --model gemini-4-hydrogen-high` (agy 1.5.18) | `agy-hydrogen-high-report.txt`: BLOCKERS 2, MAJOR 0, MINOR 3 |

The reports are verbatim. The dispositions are in `DISPOSITION.md`.
