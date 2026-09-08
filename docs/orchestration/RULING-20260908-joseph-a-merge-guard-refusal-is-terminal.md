# RULING 2026-09-08 — a merge-guard refusal is TERMINAL, and no authorizer converts it into a pass

**Ruled by Joseph on 2026-09-08**, on the integration lane's question after it overrode a refusal on a
coordinating session's authorization. The override is the occasion; the rule is general.

## 1. The rule

> **Yes, terminal. No authorizer converts a refusal into a pass.**

**The ground is a category distinction, not caution.** A guard's exit is a **fact about the tree**.
An authorization is a **permission about an act**. Permissions govern acts, not measurements.
Overriding a refusal on authorization treats a permission as if it changed a fact — and it does not.
That is the whole argument, and it does not weaken when the authorizer is senior, correct, or in a
hurry.

**Terminal for the override, never for the task.** There are exactly two legal exits, and both end in
a green run:

1. **Remove the cause and re-run** until the gate exits 0.
2. **If the gate is genuinely over-strict, fix the gate** — reviewable, dated, and it protects
   everyone. An override protects one merge and leaves the trap armed for the next operator, who may
   have worse judgment.

**The instrument already says this and has no override input.** `merge_guard.sh:29` — *"Exit 0 means
you may resolve; anything else means stop."* Its unexpected-code branch — *"Treat as a refusal."* Its
closing comment — *"Do not collapse 2 into 0: that collapse is the entire defect BEN-163 records."*
Proceeding past a nonzero exit is therefore **not an authorized mode of the tool**; it is operating
outside it. The only receipt an override can leave is prose in a commit message, and this repository
already classifies that as a failure mode: *"a remedy of the form 'write it down and read it' must be
assumed to fail."*

## 2. "A refusal" is underspecified — NAME THE EXIT

`whose_row.py` returns exit **1** for two different situations that share one code and one summary
line (`:850-857`), and they are relieved by different people:

| exit | meaning | who can relieve it |
|---:|---|---|
| **1 — foreign** | a contested row belongs to another lane | **only that row's named author**, or Joseph, whose rule of 2026-08-12 it is |
| **1 — unattributable** | *"NO ATTRIBUTABLE ROWS — resolve by hand and route to the author"* | resolve by hand; a conflict confined to a **generated** file lands here |
| **2** | **it did not look** — nothing examined, so nothing verified | **nobody.** Not authorizable |
| **3** | the gate's **own self-test failed** | **nobody.** Not authorizable |

A report that says only "the guard refused" has withheld the one field that determines what to do
next. Say which exit, and which branch of exit 1.

## 3. The generated-file rule, which is what the occasion actually needed

**The file is the symptom; the generators disagreeing is the event.** For a conflict confined to a
generated file, **regenerate from the merged sources**, then read the result:

- **matches one side** → the conflict was spurious, and the regeneration is your receipt;
- **matches neither** → you resolved a real disagreement by picking, and a clean `git status` will
  never show that you did.

`MANIFEST.tsv` carries a row describing **its own** line and byte count, so it conflicts on **every**
concurrent merge by construction. That is expected, not a signal.

**What made the 2026-09-08 override correct was regeneration, not the authorization** — and
regeneration was a three-second command available at the time, for free. Verified independently at
`a1fc54ed`: the generator's `--self-test` PASSes (run first, so a broken generator cannot pass
everything), `--check --committed-only` returns `rc=0`, `rows=758`, and the self-rows match the actual
files — `MANIFEST.tsv` 759 lines / 148,639 bytes, `MANIFEST-overrides.tsv` 173 / 13,418. The
resolution is byte-identical to what the generator produces from the merged sources. **Right answer;
the wrong route to it was available and taken.**

## 4. Consequence for the record already on `main`

The merge at `a1fc54ed`'s second parent (`610d0882`) carries an override notice in its own commit
body. That notice stands as history and is **not** to be rewritten. This ruling supersedes its
reasoning: the override should not have happened, the regeneration should have, and the guard should
have been re-run to a green exit before committing.
