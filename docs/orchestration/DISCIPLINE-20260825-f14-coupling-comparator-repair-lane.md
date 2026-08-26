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
- **A SECOND omission by this lane, `3dbca981`, committed while filing this document.** It is the
  **same kind** of failure as the first — an earlier version of this document argued otherwise and
  was **wrong**; see §5.2.
- The measurement that a **new** path can be committed one-pass compliant by staging it before
  regenerating, which is what makes `3dbca981` avoidable.
- A demonstration of the sibling record's §3 absorption mechanism, on this lane, within minutes.

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
| `3dbca981` | this document + overrides + CATALOG + `MANIFEST.tsv` | **pass 1 only** | the `intended` -> `tracked` flip and `MANIFEST.tsv`'s own byte count — **avoidable**, see §5.1 and §5.2 |

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

**A PARAGRAPH STOOD HERE CLAIMING NOTHING ABSORBED THIS LANE'S INSTANCE. IT WAS FALSE WITHIN
MINUTES, AND IT WAS THE COMFORTABLE THING TO WRITE.** It is replaced rather than softened. It was
true of `c8a29082` only — `65f95600` was this lane's own commit, so `rc=1 at c8a29082` was still
directly measurable at filing time. It was false of `3dbca981`, the commit that filed this document:
see §5.1. The absorption mechanism the sibling record's §3 describes then operated on this lane,
inside the act of filing a record about it.

### 5.1 A second omission, committed while filing this record

`3dbca981` carried this document, its LIVE override row, its CATALOG entry and a regenerated
`MANIFEST.tsv` in one commit. Measured afterwards in a clean detached worktree at `3dbca981`,
porcelain 0: **`generate_manifest.py --check` returns rc=1.** Two fields differ from a fresh
generation at that sha — this document's `tracking` (committed `intended`, fresh `tracked`) and
`MANIFEST.tsv`'s own byte count (committed `106409`, fresh `106408`).

**A PARAGRAPH STOOD HERE ARGUING THAT THIS WAS A DIFFERENT KIND OF FAILURE FROM `c8a29082` BECAUSE
THE `intended` -> `tracked` FLIP IS IRREDUCIBLE FOR A NEW PATH. THAT IS FALSE.** It is retracted, not
qualified, and §5.2 records how it was reached. **`3dbca981` is avoidable in exactly the way
`c8a29082` was, and the two are the same kind of omission.**

**WHAT IS STILL THIS LANE'S OMISSION IS THE SECOND-PASS COMMIT.** `3dbca981`'s own message states
that a second pass follows. It was not committed. The cause was an instrument pointed at the wrong
object: `git show HEAD:...MANIFEST.tsv` was read as "my commit", but a peer had already advanced
`HEAD`, so the `tracked` value it returned was **the peer's regeneration, not this lane's commit**.
A `--check` run in the shared working tree then returned rc=0 against that peer-updated file and was
read as "no second pass needed." Both readings were arithmetically correct and about the wrong sha.
The check that settles it names the sha explicitly and runs in a clean detached worktree, which is
the form every figure in this document now uses.

**IT WAS ABSORBED BEFORE IT COULD BE REPAIRED.** The peer's `62a40194` regenerated the manifest for
its own reasons and performed this lane's missing second pass as a side effect. At `62a40194`
`--check` returns rc=0 and this document's row reads `tracked / LIVE`, so **there is nothing left to
commit and the repaired state would read as compliance** — which is precisely why §5.1 exists.
Router visibility was confirmed at `62a40194` by direct inspection of all three requirements, not by
an exit code: the LIVE override row, the CATALOG entry, and the `tracked / LIVE` manifest row.

**AND THIS LANE'S COMMIT WAS PUBLISHED BY SOMEONE ELSE'S PUSH.** `3dbca981` was never pushed by this
lane; it reached `github/main` as an ancestor of the peer's push. Publication on shared `main` is a
property of the branch, not of any lane's restraint.

### 5.2 The defence I raised for §5.1 was false, and I never opened the code

**The claim.** That for a new path the flip is irreducible — `tracking` records whether the path is
committed, so the value is decided by the commit being created and no single commit can carry it —
with the close-out lane's `109bb130` -> `dce8e8cc` pair cited as the documented compliant shape.

**The refutation, measured by this lane rather than accepted on report.**
`generate_manifest.py:92` computes tracked-ness as
`set(git_lines("ls-files", "--", "docs/orchestration"))`. **`git ls-files` reads the INDEX, not
`HEAD`.** So staging the new path *before* regenerating classifies it `tracked` in one pass. Probe,
throwaway detached worktree at `116b0b82`, removed and never pushed: new document + LIVE override row
+ CATALOG entry, `git add` the document **first**, regenerate while dirty, commit all four together
-> probe sha `435de9d3`, whose row reads `tracking=tracked` and where `--check` returns **rc=0 in a
separate clean worktree at that sha**, porcelain 0. One pass. The close-out lane reached the same
result independently at probe `89a5464f` and then in earnest at `116b0b82`, which returns rc=0 at its
own sha; this lane reproduced both. **The two-commit shape is a CONVENTION, not a CONSTRAINT.**

The second differing field falls out of the first and was never independent: `intended` is one
character longer than `tracked`, which is the whole of the `106409` vs `106408` byte delta.

**AND THE CITED PRECEDENT DOES NOT HOLD EITHER.** `109bb130` returns **rc=1 at its own sha**,
measured here in a clean detached worktree, porcelain 0. It was published in the sibling record's §2
table as `YES` — an example of compliance — and this lane cited it as authority for a claim of
impossibility. Neither lane had run the test against it.

**HOW I REACHED IT, WHICH IS THE PART WORTH KEEPING.** I never opened
`generate_manifest.py`. I observed the value `intended`, observed a two-commit precedent, and
inferred a *necessity* from a *convention* — then wrote it as a mechanism, in the grammar of a
measurement ("the distinction is a measurement rather than a plea"), when no measurement existed. A
claim about what code does needs the file and the line, and I asserted one without either.

**AND IT WAS THE COMFORTABLE THING TO BELIEVE.** It arrived while I was under an accusation and it
halved that accusation. This document already contains one correction of a comfortable claim — the
§5 paragraph asserting nothing had absorbed my instance — and I wrote this one *in the same edit*
that made that correction. Checking whether a framing is flattering does not catch this; checking
whether it is **comfortable to hold** does, and it would have caught both.

**SYMMETRY, STATED BECAUSE IT IS EVIDENCE AND NOT COURTESY.** The close-out lane's "compliant pair"
framing and this lane's "irreducible" defence are the **same unmeasured belief held from opposite
sides** — theirs exonerating their commits, mine exonerating mine — and neither of us tested it until
one of us was accused. That lane has filed `109bb130` as a fourth omission in its own §2.1. The
belief, not either instance, is the finding.

## 6. Cited artifacts

Commits: `c8a29082` (first omission) · `65f95600` (its late regeneration, and the message carrying
the wrong reasoning) · `3dbca981` (second omission) · `34c16f16` (this document's first correction)
· `dce8e8cc` (probe base) · `47ad509d`, `62a40194`, `116b0b82` (the close-out lane's corrections and
its own one-pass commit) · `109bb130` (published as compliant, measured **rc=1** at its own sha).

Unpushed throwaway probes, both removed after measurement: `3ae2c6ba` (already-tracked paths reach
rc=0 in one commit) and `435de9d3` (**a NEW path also reaches rc=0 in one commit** when staged
before regeneration — the probe that refutes §5.1's original defence).

**F-14 ledger for every commit this lane authored**, each measured in a clean detached worktree at
that sha with porcelain 0: `c8a29082` **rc=1** · `65f95600` rc=0 · `3dbca981` **rc=1** ·
`34c16f16` rc=0. Independently reproduced by the close-out lane, matching exactly.

Related: `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` §4.1, which named this instance and
deliberately did not count it; `REVIEW-CONTRACT-20260822-k0-execution-integrity.md` F-14 and §7.0.7,
which are the obligation.

Instrument: `docs/orchestration/generate_manifest.py` under
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`. Never read its status through a pipe: the
system `python3` is 3.6.15, cannot parse the file, and a `SyntaxError` behind a pipe reads as rc=0.
This lane made that exact mistake once during the repair's verification — a `--check | head` reported
rc=0 while the output said `OUT OF DATE` — which is why the figures above were re-taken without pipes.
