# A narrowing flag guaranteed the answer, and the narrowing is invisible in the result

**BEN-391.** Filed 2026-08-17 by the seconding lane (block `390-399`), on a failure reported by peer session
`minerva-omnifold-72` and **re-derived here in full** — every number, sha and line reference below was
measured in this session against `HEAD` `91fc4e9`, not copied from the dispatch.

**This is `BEN-235`'s second instance** — *"an inference from absence is only as strong as the search that
would have refuted it"* — and it is filed as its own row rather than appended to `BEN-235` because that row
is lane C's and a lane's row is its author's (`BEN-159`, `BEN-223`), and because it carries three things
`BEN-235` does not: the unrestricted control, the one-source counting error, and the documents-vs-code axis.

## The two rules

> **1. Before reporting an absence, run the query WITHOUT its restrictions and confirm the unrestricted form
> returns a plausible corpus.** Empty output looks identical whether the history lacks the thing or the query
> excluded it. **If dropping a restriction moves the count off zero, the restriction is the finding.**
>
> **2. N citations of one sentence is one source.** Before counting two documents as corroboration, diff the
> sentences. And check the *subject*: a claim about **documents** does not settle a question about **code**.

## Instance 1 — `--diff-filter=D` cannot see a method retired by editing

The peer's search, verbatim, and my re-run of both legs at `HEAD`:

| query | peer | measured here |
|---|---|---|
| `git log -S'jitter' --diff-filter=D --all -- '*.py'` | 0 commits | **0 commits** |
| `git log -S'jitter' --all` | 71 commits | **72 commits** |

(The 71/72 difference is a commit landing between the two measurements, not a disagreement; the point is
`0` against a two-order-of-magnitude corpus.)

**`--diff-filter=D` matches only commits that DELETE A FILE.** A method retired by editing a file in place
is invisible to it — and editing is the normal retirement mechanism. Verified for this exact case:
**`07c18aee` (2026-07-14) removed the block by editing**, `1 file changed, 238 insertions(+), 84
deletions(-)`, of which **16 removed lines match `jit`**, and `git show --diff-filter=D --name-only 07c18aee`
lists **0 files**. So the commit that did the thing being searched for is, by construction, outside the
search space.

**What was actually there**, confirmed by reading it: `a0cdc019f83f283505e886eb8c36e6250ec6ca7b`
(2026-06-08, *"ND campaign: PET 4D combined cov + (E_avail,W) generator band + rigorous unified throw"*),
`nd-unfolding/unified_throw_cov.py:224` — a `# JITTER CORRECTION.` block carrying **its full derivation in
the comment**, through to the `[null] jitter floor` print at line ~239.

**And no literal scalar ever existed**, which is why every value-shaped search agreed. At that revision
`jit_trace` is computed at runtime:

```python
x_cv2 = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters,
                          args.seed + 7).ravel(order="C")[rep]
jit_trace = float(np.sum((x_cv2 - base) ** 2))
```

A second CV unfold at `seed + 7`. So a scientific-notation grep, a `-G` on a numeric literal, and a
value-shaped grep were all searching for an object that never appeared in the source — **and their
agreement felt like convergent evidence when it was three instruments sharing one blind spot.** That is the
part worth carrying forward: *independent* searches that are all narrowed the same way are not independent.

**Residue at `HEAD`, since "absent" was the claim under test:** `grep -in 'jitter\|jit_trace'
nd-unfolding/unified_throw_cov.py` returns exactly one line — `416: # estimator jitter across slabs.` — a
comment, not the procedure. So the procedure is genuinely retired from that file; what was false was that
its specification had never been committed.

## Instance 2 — two documents, one sentence

The peer reported *"two committed documents establish it"*:

- `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md:171`
- `DETERMINATION-20260817-causes-3-4-provenance-measured.md:190`

Read side by side, **the second quotes the first inside quotation marks**:

> *"The retired procedure subtracted a scalar, and no committed document records which scalar or how it was
> estimated. Constructing one now and calling the difference a measurement would be precisely the 'success
> condition invented after the fact' this document exists to prevent."*

**One source, cited twice.** The peer had even written *"quotes the same sentence"* in its own dispatch and
still counted it as corroboration — which is the useful detail: the counting error survived the author
noticing the fact that refutes it, because *number of citations* is read off a list of paths and the list
was honestly two items long.

**And the sentence is about the wrong thing.** It says *no committed **document** records…*; the dispatch
asked about **code**. Both statements are true simultaneously — the specification was in a source file with
its derivation in a comment, and apparently in no prose document. **Absence-from-documents does not entail
absence-from-code**, and the two searches do not even cover the same corpus.

## Why this class survives careful work

`FINDING-20260814-absence-of-an-error-is-not-a-result.md` (`BEN-251`) already says *an operation that
reports nothing has told you nothing* — but its remedy is *read the resulting state*, which presupposes you
can tell a real empty from a manufactured one. **That is exactly what an empty search result does not tell
you.** This row is that rule's necessary complement: `BEN-251` says look, `BEN-235` says your grep may not
be able to find it, and rule 1 above is the cheap way to know which case you are in — **one command, and it
is the same command with a flag removed.**

## How it was caught

By a **designated second session dissenting rather than ratifying**, under Joseph's 2026-08-17 two-session
rule. The peer had already relayed `ABSENT` to two lanes with confidence and had run its own confirming
search, which came back empty — because it was narrowed the same way.

**The rule's value here was entirely in the dissent.** A quorum of agreeable sessions ships this, and ships
it faster for being seconded. The obvious misreading of a two-session rule is that agreement is the goal;
today's record is that the second key came back **negative** and was right.

## Re-deriving this

```bash
git log -S'jitter' --diff-filter=D --all --oneline -- '*.py' | wc -l   # 0  <- the reported absence
git log -S'jitter' --all --oneline | wc -l                             # 72 <- the unrestricted control
git show --diff-filter=D --name-only --format='' 07c18aee | wc -l      # 0  <- deleted no files
git show --stat 07c18aee -- nd-unfolding/unified_throw_cov.py          # 238 insertions, 84 deletions
git show a0cdc019:nd-unfolding/unified_throw_cov.py | sed -n '224,240p' # the block + its derivation
sed -n '171p' docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md
sed -n '190p' docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md
```

## Cross-references

- `BEN-235` — the class, and its first instance (`grep set_seed` could not match `set_random_seed`). Lane C
  paired the two; the pairing is C's contribution and is recorded here rather than in C's row.
- `BEN-251` / `FINDING-20260814-absence-of-an-error-is-not-a-result.md` — the complement, above.
- `BEN-392` — unqualified transport of good measurement. Instance 2 here is also instance 2 there, seen from
  the other side: the sentence was *correct about documents* and was transported to a question about code.
- `BEN-390` — the sibling filed in the same commit. Same shape: **a signal that reads as evidence about the
  world when it is evidence about the instrument.**
