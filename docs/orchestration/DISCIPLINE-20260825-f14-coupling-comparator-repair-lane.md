# DISCIPLINE 2026-08-25 — one F-14 / §7.0.7 coupling omission by the comparator-repair lane

Filed by the independent comparator-repair lane against its own commit, after the publication
close-out lane raised it directly and named it in §4.1 of
`DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` without counting it as theirs. Attribution
belongs to the lane that made the commit. This is a discipline record: not a defect disclosure, not a
gate document, and not a grade.

## CITABLE FOR

- One F-14 / §7.0.7 coupling omission by this lane: `c8a29082`, and what it left stale.
- The measurement that `generate_manifest.py --check` returned **rc=1 at `c8a29082`** in a clean
  detached worktree with porcelain 0.
- The proof that the coupled single commit was **achievable in one pass**, which removes the excuse
  this lane actually used.
- A discoverability gap: the same-commit coupling for `MANIFEST.tsv` is **not** in §7.0.7's own text.
- An instrument-behaviour finding: `generate_manifest.py`'s DIRTY warning steers a reader toward the
  violation.

## NOT CITABLE FOR

- Any Gate-2 clause. F-14 is not one of the nine, and the Gate-2 FAIL in
  `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` is unchanged by this document.
- The D-3 comparator repair itself. That work stands as filed at `c8a29082`; this record is about
  the **commit's shape**, not its content. The repair remains **UNGRADED** under ruling 3.
- Any other lane's omissions. Three by the publication close-out lane are recorded in their own
  record and are not restated, re-counted, or absorbed here.
- The current state of `MANIFEST.tsv`. Every figure below is as-of a named sha.

## 1. The omission, as measured

`c8a29082` changed two tracked paths and did not regenerate the coupled manifest in that commit:

| Commit | Paths changed | Manifest regenerated in-commit | What it left stale |
|---|---|---|---|
| `c8a29082` | `compare_m1_m6.py`, `test_compare_m1_m6.py` | **NO** | both files' line/byte counts, the decision record's `consumer`/`inbound_count`, the f17b record's `consumer`, and `MANIFEST.tsv`'s own byte count |
| `65f95600` | `MANIFEST.tsv` | — (this *is* the late regeneration) | — |

`git show --name-only c8a29082` returns exactly the two `.py` paths and no `MANIFEST.tsv`.

**Gate state at the offending commit.** In a clean detached worktree at `c8a29082`, porcelain 0,
`generate_manifest.py --check` returns **rc=1**, `OUT OF DATE`, rows=527. Measured at the commit and
in a clean tree, because a dirty working tree fails for reasons that have nothing to do with the
commit. For contrast, at `65f95600` the same check returns **rc=0** — which is precisely the shape
that makes this class invisible: the endpoint is compliant and the intermediate sha is not.

## 2. The excuse, and the measurement that removes it

`65f95600`'s message records this lane's reasoning: commit the sources first **so that the manifest's
line and byte counts describe a commit rather than a working tree**. That reasoning is **wrong**, and
it is wrong in a way that is worth writing down because it sounds careful.

When all three paths are committed together, the working tree **is** the commit content, so counts
taken from the dirty tree are exactly the committed counts. Measured rather than argued: at
`dce8e8cc`, applying this lane's own two-file diff, regenerating **while the sources were dirty**,
and committing all three paths in one commit produced probe sha `3ae2c6ba`, at which
`generate_manifest.py --check` returns **rc=0** in a separate clean detached worktree, porcelain 0,
**in one pass**. The probe commit was never pushed and exists only as the receipt for this paragraph.

So the coupling was satisfiable at no cost. The split was not a trade-off; it was an error.

## 3. The instrument steered toward the violation

Regenerating while the sources are dirty prints:

> `WARNING: 2 tracked path(s) in the inventory scope are DIRTY, so their lines/bytes/inbound_count
> describe the WORKING TREE, not any commit`

That warning is **true in general and inapplicable in exactly the case where coupling is required.**
It has no arm distinguishing *dirty and about to be committed alongside* from *dirty and not*, so it
fires identically on correct procedure and on the hazard it was written for. This lane read it as a
reason to split the commit, which is the opposite of what F-14 requires.

**Not repaired here.** `generate_manifest.py` is coupled to many callers and a warning change is not
this lane's call; it is flagged for Joseph and the close-out lane as a candidate one-line
strengthening, not filed as a defect.

## 4. A discoverability gap in the obligation itself

Read literally, the two clauses have different scopes:

- **F-14** (contract line 618) requires "every row of §6 discharged **in the same commit as the
  repair that moves it**." Its same-commit language is scoped to §6's rows.
- **§7.0.7(1)** requires `generate_manifest.py --check` exiting 0 "**at the graded sha**, measured in
  a clean worktree," and says of itself that "§6's six rows do not name it, which is why this is an
  addition and not a reading."

The same-commit coupling *for the manifest* is therefore a **composition** of the two, and it is
stated explicitly in §1 of the close-out lane's discipline record — not in §7.0.7's own text.

**This lane does not rebut the composition; it is right on the merits.** §7.0.7's stated grounds are
that at `ae42ae8d` the check "exited 1 while the commit message asserted 0," which is a complaint
about a *published sha*, and `c8a29082` reproduces exactly that. A rule whose purpose is that no
published sha misdescribes the tree is not served by allowing intermediate shas to.

The gap is that a lane reading only the contract can satisfy §7.0.7's letter — rc=0 at the sha it
submits for grading — while breaking the coupling at every commit before it. That is what this lane
did, and it did it after reading §7.0.7. **The obligation should be discoverable where the contract
states it**, not only in a discipline record filed after the fact.

## 5. What this record does not do

Regenerating in `65f95600` produced a correct manifest and **does not erase the gap**; the repaired
state would otherwise be the only surviving evidence, and it reads as compliance. The mechanism is
the one the close-out lane identified and it applies here unchanged: any later regeneration by any
lane absorbs every upstream omission, so compliance is measurable only at the commit, in a clean
worktree, and only until someone else regenerates.

One correction to the general claim, in this lane's favour and therefore stated with the measurement
rather than asserted: nothing absorbed this instance before it was measured. `65f95600` was this
lane's own commit, and `rc=1 at c8a29082` was still directly measurable at the time of filing.

## 6. Cited artifacts

Commits: `c8a29082` (the omission) · `65f95600` (the late regeneration, and the message carrying the
wrong reasoning) · `dce8e8cc` (the base the probe was built on) · `3ae2c6ba` (unpushed probe proving
the coupled commit reaches rc=0 in one pass) · `47ad509d` (the close-out lane's corrections, which
named this instance in §4.1).

Related: `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` §4.1, which named this instance and
deliberately did not count it; `REVIEW-CONTRACT-20260822-k0-execution-integrity.md` F-14 and §7.0.7,
which are the obligation.

Instrument: `docs/orchestration/generate_manifest.py` under
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`. Never read its status through a pipe: the
system `python3` is 3.6.15, cannot parse the file, and a `SyntaxError` behind a pipe reads as rc=0.
This lane made that exact mistake once during the repair's verification — a `--check | head` reported
rc=0 while the output said `OUT OF DATE` — which is why the figures above were re-taken without pipes.
