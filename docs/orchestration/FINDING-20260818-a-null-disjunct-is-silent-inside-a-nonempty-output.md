# A disjunctive grep answers "did any of these appear", never "which" — and a null disjunct is invisible inside a non-empty result

**BEN-443.** Filed 2026-08-18 by the seconding lane, on the **review / second-key lane's** (`Assistant [28640e]`)
self-diagnosis, at its request because it is read-only and cannot commit. **Verified here rather than
transcribed**, which matters more than usual: this row is about a search whose output was true and whose
reading was not.

## The mechanism

One command, three unrelated patterns:

```
grep -nE "split\(.\|.\)|CLAIMS|\[[0-9]+\]" docs/orchestration/whose_row.py
```

The question being answered was *"does anything parse `CLAIMS.md` by column index?"* The `parts[0..2]` lines
matched the **index** disjunct. The `CLAIMS.md` strings at `:381-383` matched the **CLAIMS** disjunct. They
are different lines with no relationship to each other — the `CLAIMS.md` occurrences are **test fixtures**, in
which the filename appears as a *value* in a tab-separated `ROW-OWNERS.tsv` row. **The union was read as an
intersection:** *here are indexed reads, and here is CLAIMS, therefore CLAIMS is read by index.*

**And the disjunct that carried the actual answer returned nothing, which is why it was never seen.**

## Measured, disjunct by disjunct

| disjunct | hits in `whose_row.py` |
|---|---|
| `split("\|")` | **0** ← this was the answer |
| `CLAIMS` | 3 |
| `\[[0-9]+\]` | 11 |
| **the union, as run** | **14** |

`3 + 11 = 14`. **The union is exactly the two non-null disjuncts. The null one contributes no line, no blank,
no marker — nothing.** The output looked full because the others fired, and a full output reads as a
productive search.

> **In a disjunctive search, the absence of one pattern is invisible. There is no row saying "this one matched
> nothing."**

## Why this is its own register

It is a member of `BEN-389`'s family — a null that is evidence about the search — but the failure is at a
different place, and the difference is what makes it worth a row. In every prior instance the search was
**wrong**: too narrow a scope, the wrong operating point, the wrong matching semantics, a filter on an absent
column. **Here the search was correct, complete, and returned true information.** Every line it printed was a
real match for a real pattern. **The entire defect is in reading a union as a conjunction**, and no
improvement to the query would have prevented it.

That also makes it harder to catch by the usual reflex. *"Check your grep"* fails here — the grep was fine.

## The remedy, with the cheap middle option measured

**Run the disjuncts separately whenever the conclusion depends on WHICH one fired.** Three commands, three
counts, and a `0` is a visible answer rather than an absent line.

There is a middle option and it is worth knowing its limit. `grep -oE` with a tally shows which patterns
actually matched:

```
$ grep -oE 'split\(.\|.\)|CLAIMS|\[[0-9]+\]' whose_row.py | sort | uniq -c | sort -rn
  12 [0]
   3 CLAIMS
   3 [1]
   2 [2]
```

`split("|")` is **absent from the tally**, which is the visible form of the null — better than a line-oriented
grep, and still an *absence* rather than a *zero*. A reader scanning four populated rows has to notice a fifth
that is not there, which is the same act that failed the first time. **Per-disjunct counts are the robust
form; the tally is the cheap one.**

## Provenance, and one correction to the diagnosis it came with

The mechanism, the diagnosis and the formulation are the review lane's. It reported the error against itself
within one turn of being shown the correction.

**What this lane contributed is the check that produced the correction:** the review lane's conclusion —
*"latent defect in `CLM-006`, no current misreader"* — was **right**, and its premise, that
`whose_row.py:209`/`:697-698` are indexed reads of `CLAIMS.md` stopping at `parts[2]`, was **wrong**. Both
split on `\t` and read `OWNERS_TSV`. **A right answer suppresses scrutiny of its reasoning**, which is
`BEN-396`'s allocation rule — verification goes where there is disagreement, not where there is fragility —
and a supporting premise inside a correct conclusion is the least-scrutinised position there is.

**The true statement is stronger than the one it replaces:** there is no column-indexed consumer of
`CLAIMS.md` anywhere in the repo. Checked every `.py` hit for `split("|")` individually — `findings_row_lint.py:92`
(reads `FINDINGS.md`), `split_findings.py:53`, `wakerctl.py:365`/`:390`, `analyze_slurm_history.py:121` — none
touch it; the remaining references are prose citations and a filename comparison at `generate_manifest.py:195`.

## The consequence for `CLM-006`, which is the case that produced this

`CLM-006`'s row in `CLAIMS.md` carries **13 fields between its pipes against the header's 9** (four stray
pipes; `line.split("|")` gives 15 vs 11 by counting the empty strings outside the leading and trailing pipes —
**the between-pipes base is the correct one and this lane initially reported the other without saying so**).
Every column after the break is shifted, so its `independent verifier` field reads *"median 1.70%
(prior-dominated cells stay near prior, as expected)"*.

**Nothing misreads it today, because nothing reads it.** Which inverts the usual argument for a check: a
per-row field-count assertion is not hardening a blind consumer, **it is the only thing that would ever
notice** — the file's correctness is currently maintained by nobody parsing it, and this malformation surfaced
only because a human counted fields for an unrelated purpose. The review lane's addition: on a file with zero
parsers such an assertion is cheap **and carries no regression risk**, since there is nothing that could
break, which is usually the objection to adding a check to a mature file.

**Not filed as a repair and not repaired here.** `CLAIMS.md` is lane C's, and a pipe-level edit to an
~1,800-character claim row is not something to do unannounced. Flagged to C and to the mediator.

## Cross-references

- `BEN-389` — a null is evidence about the search. Parent family; this is the case where the search was right.
- `BEN-396` — verification allocated by suspicion rather than fragility. Why a premise inside a correct
  conclusion is the least-checked thing in a message, and the review lane's own row.
- `BEN-391` — *N citations of one sentence is one source*. Neighbouring shape: counting matches without
  resolving what each one is.
