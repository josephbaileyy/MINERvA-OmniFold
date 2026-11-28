# PTMC declaration reads, round 2 (2026-11-27)

**What was read.** DRAFT r2 at branch commit `783a73a10`: `PTMC-DECLARATION.md` sha256
`f0ed2554dbc2997cd2d2e68d46e065b8656307f6066a5ccddef9d96ca0e4b33b`.
- The readers also had its scoping, the round-1 reports, `reads/r1/DISPOSITION.md` and round 1's 12 sources: 15 files
  in all (`inputs-sha256.txt`). The two readers' copies were identical.
- The prompt, `prompt.txt` (`67a86cc0…`), asked for a verdict on every round-1 disposition and for new findings.

| reader | invocation | report |
|---|---|---|
| codex-school2 | `codex exec --sandbox read-only -m gpt-6.2-sol -c model_reasoning_effort=high` (codex-cli 0.172.0); 133,292 tokens | `codex-school2-report.txt` (`bc173bfd…`): BLOCKERS 6, MAJOR 5, MINOR 2 |
| agy | `agy -p … --model gemini-4-hydrogen-high` (agy 1.5.18) | `agy-hydrogen-high-report.txt` (`2748bcf0…`): BLOCKERS 5, MAJOR 2, MINOR 2 |

The reports are verbatim. The dispositions are in `DISPOSITION.md`.

**A correction to round 1's README:** it said the readers had "the same 14 input files". They had 12, as its
`inputs-sha256.txt` lists.
