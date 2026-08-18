# A Slurm array tally needs two commands, and the sum is the check

`BEN-431`. Mediator lane. Filed on a number that reached Joseph wrong: `57194054` reported at
**30 COMPLETED / 9 RUNNING / 1 PENDING** when the truth was **10 / 4 / 36**.

## The rule, which is the whole point of the finding

> **For a Slurm array: `sacct -X` for terminal states, `squeue -r` for live ones, and the two must sum
> to the declared array size. Quoting either alone is a count of ROWS, not TASKS.**

```
sacct -X   ->  10 COMPLETED,  4 RUNNING,   1 PENDING     PENDING wrong: an array range is ONE row
squeue -r  ->                 4 RUNNING,  36 PENDING     live tasks, expanded
true       ->  10 COMPLETED,  4 RUNNING,  36 PENDING  =  50
```

**Neither command alone gives a task tally.** `-X` suppresses the `.batch`/`.extern` step rows and does
**not** expand a pending `[12-49%10]`, which stays one row under both commands.

**The sum check catches every version of this without anyone knowing why it is wrong.** The bad tally
was `30 + 1 + 9 = 40 != 50`. An `-X`-only read gives `10 + 4 + 1 = 15 != 50`. Both fail the same
one-step test.

## The actual cause, which is NOT what it first looked like

The mediator attributed the error to misreading `-X` row counts. **That diagnosis was wrong and would
have taught a rule that is not the bug** — `-X` was never used, and `-X` alone gives the correct `10`.

The original command was:

```
sacct -j 57194054 --format=State%14 -P | grep -vE '\.batch|\.extern|^State' | sort | uniq -c
```

**`--format=State%14` prints only the State column. The JobID never appears in the output, so
`grep -v '\.batch'` had nothing to match and removed nothing.** The filter was a silent no-op, every
task was counted three times (`_N`, `_N.batch`, `_N.extern`), and both COMPLETED and RUNNING came out
exactly `3x`. `30/1/9` is a plausible-looking array state, so nothing flagged it.

## Fourth register of the check that cannot fire

A guard or filter written correctly for a stream that does not exist:

1. **scope** — `--diff-filter=D` matching only commits that delete a file (`BEN-391`)
2. **operating point** — a ceiling test at a median of `0.16`
3. **matching semantics** — `200000` matching inside `2000000`
4. **field presence** — *filtering on a column that is not in the output* (this one)

**Nothing in the command looks wrong.** That is the family resemblance, and it is why these are found
by arithmetic that does not add up rather than by reading the command again.

## Provenance and what it bounds

The number was produced by lane Assistant and relayed by the mediator to Joseph, to lane C, and to
lane E without a command run in the same turn — `BEN-027`. **Producing a bad number and relaying one
are different failures and both happened here.** It was also stated as a clean tally with no
derivation shown; had the command been printed, `40 != 50` was visible immediately. That is the
receipt-ingredients rule (`BEN-077`) applying to a one-line status number, not only to a receipt.

**Bounded consequence:** the tally fed nothing except a timeline. The `~2 GPU-h` exposure estimate for
`57194055` used the full 50-task array and did not depend on it, so the decision not to seek a cancel
stands unchanged. What moved is that the CPU target family is one-fifth complete rather than
three-fifths — the hours remain *spent-and-kept*, but mostly still to spend.
