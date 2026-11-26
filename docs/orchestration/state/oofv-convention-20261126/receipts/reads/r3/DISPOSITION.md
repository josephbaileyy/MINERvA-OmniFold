# OOFVC r3 (the last full round): dispositions

The r3 reads were of commit b265e7cf (inputs in `inputs.sha256`). The prompt stated the director's scope rule: after
this round, only findings that could change a printed number, a gate's acceptance, or cause a false STOP of a correct
run block.
- **codex-school `gpt-6.2-sol`, high:** 4 BLOCKERs and 3 NONBLOCKERs, NO-GO. It used 135,016 tokens; the account went
  from 14% to 13% weekly.
- **agy `gemini-4-hydrogen-high`:** GO. Its one NONBLOCKER is a crash path on an already-invalid K list.

All items were fixed in the commit that adds this file (declaration revision 6). Every BLOCKER bears on a gate's
acceptance or a false STOP, so each falls under the scope rule.

| # | reader | finding | disposition |
|---|---|---|---|
| c1 | codex | Input pins were by file name, so a second staged file of the same name could stand in | Fixed. Each unit's argv must carry the exact staged paths (`/pscratch/sd/j/josephrb/oofvc-20261126/stage/…`), the rows file included. Mutant: SCORE_STAGE_PATH |
| c2 | codex | A unit's output manifest could omit a file | Fixed. Each manifest must list exactly the unit's files. The scorer reports each pin condition by name. Test: `Runner.test_scorer_requires_full_manifests_and_the_pinned_join_record`. Mutant: SCORE_MANIFEST |
| c3 | codex | split.json was hashed in the scorer's working tree (a false STOP on a local edit), and the join record's classes could be replaced | Fixed. split.json is hashed at `--tool-commit`. Each unit process pins the join record's digest (`--join-record`), and the scorer requires it. Test as c2. Mutant: SCORE_JOIN_PIN |
| c4 | codex | The timing gate could validate one line and project from another | Fixed. Each playlist must have exactly one entry-count line, and it must be complete |
| c5 | codex | No test showed the output-digest check catching a swap | Fixed. `Runner.test_scorer_catches_a_swapped_n_file` copies off's n.npz over R's and requires exactly one record's outputs to fail. Mutant: SCORE_OUTPUTS |
| a1 | agy | C-BASE's zero check raised on a mismatched K list instead of printing STOP | Fixed. The check is guarded by the K-list and shape equality |
| c6, c7, a2 | both | The round-1 and round-2 fixes check out | No change |
