# PTMC declaration reads, round 1 (2026-11-27)

**What was read.** The DRAFT declaration at branch commit `8040eedba`: `PTMC-DECLARATION.md` sha256
`e88d6ee86e4196f603cb7927f2b27f4aeb11c8880ec262d0927bf52e848f8f9c`, with its scoping and the sources named in
`prompt.txt`.
- Both readers had the same 14 input files; `inputs-sha256.txt` lists them, and the two copies were identical.
- Both used the same prompt, `prompt.txt`, sha256 `573259d2…`.

**The readers** (Grok is unfunded; the director's instruction):

| reader | invocation | report |
|---|---|---|
| codex-school2 | `codex exec --sandbox read-only -m gpt-6.2-sol -c model_reasoning_effort=high` (codex-cli 0.172.0); 118,015 tokens | `codex-school2-report.txt` (`1b1d216a…`): BLOCKERS 5, MAJOR 8, MINOR 3 |
| agy | `agy -p … --model gemini-4-hydrogen-high` (agy 1.5.18) | `agy-hydrogen-high-report.txt` (`9c980fc0…`): BLOCKERS 4, MAJOR 3, MINOR 1 |

The reports are verbatim (`.txt`, so their bytes carry no waivers). Their `file://` links point at the readers' local
input copies. The disposition of every finding is in `DISPOSITION.md`.
