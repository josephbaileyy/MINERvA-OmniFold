# FINDING 2026-08-13 — Third-party attribution drift in the flattering direction has no natural discoverer

**`BEN-214`.** Lane A block (`210-219`). **Filed by the party the drift favoured, which is the problem
the row is about.** See the conflict-of-interest note below; it is stated rather than resolved.

## The instance

The mediator reported to Joseph that **`BEN-213` was "filed by D."** It is lane A's: the row sits at
`FINDINGS.md:126`, was introduced at commit `f025532` (2026-08-13T03:21:44−04:00), and `210-219` is
lane A's block per `FINDINGS.md:18`. D's block is `160-172` and holds nothing in that range.

**D caught this itself and argued against its own interest.** Its reasoning, relayed rather than
paraphrased: the *observation* behind the row is D's — V28's generalisation about S2 — but the row is
not, and **"derives from" is not "is."**

## Why it is operational rather than reputational

`CONVENTION-lane-worktrees.md` states that **only a row's author reshapes it.** So a wrong owner is not
a courtesy error: it silently **grants D an edit right over lane A's row and strips lane A of it.**
Attribution here is a write-authority record, and the convention that makes lanes safe to run
concurrently is exactly what turns a mis-credit into a permissions change.

## The mechanism: no natural discoverer

**The party best placed to notice is the one who benefits.** A lane under-credited is the only one with
both the motive and the knowledge to check, and raising it looks like claiming credit; a lane
over-credited has no reason to look. So the error class is stable in the flattering direction and
survives ordinary review, because nobody's incentives point at it.

That makes it a sibling of `BEN-172` (cite-without-opening) and `BEN-207` (a present verdict is also a
statement about the search), with a distinct mechanism: those two fail because a check is not run; this
one fails because **the check has no natural owner.**

## THE ENABLING CONDITION, measured — and this is the part neither lane had

**The shared git identity is what makes the drift invisible to the obvious instrument.** Over
`7c6ffc4..HEAD` (2026-08-13):

| author string | commits |
|---|---|
| `Joseph Bailey` | **47** |
| `Lane C (PET)` | 14 |
| `Lane D (verifier)` | 9 |

**Lane A, the codex session and the mediator all commit as "Joseph Bailey."** C and D are attributable
from `git log`; the other three are not separable from each other by any field git records. So
**`git log` cannot answer "whose row is this" for 47 of 70 commits**, and the mediator identified one
codex launch only by commit *style*.

**Consequence for any future self-report:** a commit count taken from `git log` over a shared-identity
range is not a measure of one lane's work. Lane A told the mediator it had landed "37 commits since
01:58"; measured, that range spans a process boundary (`procStart` 2026-08-13T06:31:33Z, so 7 of those
commits are a predecessor's) **and** counts other lanes' work under the shared name. The honest figure
was "at most 34, and not separable from git alone."

## The check

- **Before attributing a row to a lane, read the row's `BEN-*` id against the block table** — the block
  table is the authority, not the commit author, and not who supplied the idea.
- **Do not use `git log --author` to scope one lane's output** where identities are shared. Scope by
  `BEN-*` block, by artifact path, or by an explicit `Lane X` trailer.
- **A cheap structural fix, not applied here because it is Joseph's call:** give each lane a distinct
  committer identity, as C and D already have. It converts this class from undiscoverable to a `git log`
  one-liner.

## Conflict of interest, stated not resolved

**D explicitly refused to file this**, saying it would be "filing a row about my own credit." **Lane A
is not neutral either — it is the beneficiary of the correction**, and filing establishes its ownership
of `BEN-213`. It is filed here because the mechanism and the shared-identity measurement are worth
having, and because leaving it unfiled to protect appearances is the same suppression the finding
describes. **A reader should weight it accordingly.**

Also noted: `210-219` was allocated to lane A by the mediator under Joseph's delegated grant, and
**whether lanes may self-allocate blocks at all is an open question with Joseph.** Filing into that
block does not settle it and is reversible in one commit.
