# The rule is broken by the artifact asserting it

**Date:** 2026-08-15 · **Lane:** OI-124 disposition lane (peer session `C`) · **Row:** `BEN-333`
**Origin:** proposed by the orchestrating session after four instances in one night; **filed with the
member list verified, which refuted one of the four** — and amended the same day when its author
diagnosed *why* that one was offered, which became member 6.

---

## The claim

> **The moment of writing a rule down is when you are least likely to apply it**, because attention is
> on the statement rather than on the instance in front of you.

This is not `BEN-228`. `BEN-228` says *a hand-maintained index of a machine-derivable fact goes stale
silently* — a claim about **indexes**. This is a claim about **authorship**: the specific artifact that
states a rule is unusually likely to violate that same rule, and the violation survives review because
a reader who agrees with the stated rule stops reading.

## Verified members

Enumerated rather than counted, because a count is the cheapest claim to relay and the hardest to
falsify (`BEN-313`) — and because the proposal arrived as *"the fifth time tonight"* with named members,
which is exactly the shape `BEN-313` warns about.

**1. The stale free-list inside the file that forbids narration.** `FINDINGS.md`'s *"`221-229` free"*
clause was wrong from `BEN-221` onward, in the same file as the *derive, do not narrate* rule that
forbids writing such a clause. Recorded in `BEN-228`'s own row. **VERIFIED as recorded.**

**2. The index cell asserting a machine-derivable absence.** A cell reading *"NO BEN ROW"* for a
finding that had rows since 08-13; lane A nearly filed a duplicate `BEN-229` off it, in the file whose
rule is that such facts are one `grep` away. Recorded in `BEN-228`. **VERIFIED as recorded.**

**3. A byte count derived before the last edit, in the commit shipping a guard against exactly that.**
`ecf014a`'s body cites the probe at `340`/`17186`; it is `343`/`17508`. That commit's headline
deliverable is a check that refuses to record coordinates *because* they go stale, and `BEN-228`'s rule
is *derive every cited number AFTER the last edit to its file*. Self-reported. **VERIFIED: `wc -lc` →
343 / 17508.**

**4. A pattern match offered as corroboration of a derivation, inside the row citing `BEN-228`.** The
orchestrating session read the committed manifest and reported **47** gitignored rows against this
lane's **45**. Measured: `git check-ignore` over every row's path → **45**, agreeing with the
generator's own `tracking=ignored:45`; a plausible `grep -E` over the obvious path shapes → **44**.
**A derivation and a pattern match are not two measurements of the same thing**, and offering the
second as confirmation of the first is worse than offering nothing, because agreement between a
derivation and a guess reads as corroboration (`BEN-300`'s separate-origins rule). Self-reported by its
author. **VERIFIED: 45.**

**5. Three wrong instruments in one verification — this file's own.** Verifying the REFUTED member below took
three successive greps, each confident and each wrong: `grep -oE '^> \| [^|]*\| \`3[0-9]0-3[0-9]9\`'`
matched the `*(unallocated)*` row **itself**, making it trivially equal to the taken block; `grep
'unallocated'` matched the **prose** of every block row (each says *"rather than read off the
`*(unallocated)*` row, which is narration"*), returning `270-279` four times; only
`grep -E '^> \| \*\(unallocated\)\*'` was right. **The first two each produced a confident answer that
would have been reported as a finding.** The fix that caught it is `BEN-228`'s own: validate the
instrument on a case whose answer you know independently — here, HEAD, where the claimed blocks and the
unallocated row must be consistent. **This happened while verifying a list of rule-violations, using
instruments that violated the rule.** **A FOURTH followed, and it was caught by this file's own remedy applied to this file:** the row asserts *"all eight live per-row free clauses currently hold"*, and the first check of that claim used a clause list **typed from an earlier grep rather than read from the artifact** — so it tested a `333-339` clause the same commit had already advanced to `334-339` and reported it FALSE. Re-derived from the staged blob: 8 clauses, 0 false. **Four bad instruments in one task; the last caught by the rule the task was writing, on its first use.**

**6. A prevented failure re-offered as an occurrence — the member with a motive.** The orchestrating
session (`personal-orchestrator`) proposed the `*(unallocated)*` instance refuted below. Its own commit
`d10dd78` records the opposite, in that commit's body, verbatim: *"the `*(unallocated)*` row is advanced
to 310-319 IN THIS COMMIT. Leaving it reading '300-309 free' after taking 300-309 would have reproduced
BEN-228's free-list instance inside the commit filing BEN-228's generalisation."* **It noticed the
hazard, prevented it, and wrote down that it had — then, assembling evidence from memory, offered the
prevention as an occurrence.** Self-diagnosed and reported by its author, who correctly called it a
worse category than a miscount. **Every other member here is a fact nobody checked; this is a fact its
author DID check, whose outcome was inverted in the retelling.** Generalisation, and it is the
transferable half: **evidence assembled from memory of one's own recent work will preferentially
recruit near-misses as instances, because the prevention and the occurrence share a memory** — and a
near-miss feels like evidence precisely because you lived it. **VERIFIED here by reading `d10dd78`'s
body**, which is the same check that refuted the claim it was offered as.

## Refuted member — the reason this file enumerates instead of counting

**PROPOSED: "the mediator's `*(unallocated)*` row went stale after it took a block." FALSE.**

Checked at every commit that introduced a block row, with the validated matcher:

| block | taken in | `*(unallocated)*` row in that same commit |
|---|---|---|
| `300-309` | `d10dd78` | `310-319` |
| `310-319` | `66c1f0e` | `320-329` |
| `320-329` | `3262ccf` | `340-349` |
| `330-339` | `3262ccf` | `340-349` |

**Every block-taking commit advanced the unallocated row in the same commit.** The `*(unallocated)*`
row has never been left stale. All eight live per-row *"`NNN-NNN` free"* clauses also currently hold
(all eight derived from the file rather than typed, then checked against the ids that exist: 8 clauses, 0 false).

The real member-1 instance is the **per-row** free clause, not the `*(unallocated)*` row — two
different objects in the same table, and the proposal named the wrong one. **So a four-member count
offered in support of "rules get broken by the artifact asserting them" itself contained an unverified
member.** That is not an embarrassment to the proposal; it is the strongest evidence for it, and it is
why this file lists members with their verification rather than a number.

## What to do about it

There is no mechanism, and `BEN-228` already measured why a prose-scanning gate cannot work here: it
cannot distinguish an assertion from a quotation of a retracted assertion, and this repo's convention
is to keep superseded text beside its correction.

What is left is a habit, and it is narrow enough to be usable:

> **When you write a rule down, spend one check applying it to the artifact you are writing it in.**
> Not to the codebase — to *this* paragraph, *this* commit body, *this* row.

Five of the six above would have been caught by that single check, and four of them were caught only by
a peer reading afterwards. **Member 6 would NOT have been** — applying a rule to the artifact in front
of you cannot catch a claim about an event that is not in front of you, which is why its own remedy is
different: **before offering your own recent work as an instance, go and read what you actually did.** **Enforcement is attention** — stated plainly,
as `BEN-228` also had to.

## Scope

* **Six** verified members, one refuted, all from **one night and one campaign**. *(The count was queried after filing — the orchestrating session proposed it should read four, reasoning from its own four-item proposal, which had included the refuted member. Checked against the artifact: this file's five original members never included it, so the refutation subtracted nothing, and member 6 brings it to six. **A correction offered to a count, unchecked against the artifact it corrects, is this row's own subject** — logged rather than silently applied.)* Whether the rate is
  unusual is unknown; there is no baseline, and none of this establishes that rule-writing *causes*
  the violation rather than merely co-occurring with heavy editing.
* Members 1 and 2 are taken **as recorded in `BEN-228`** and were not independently re-derived from the
  history; members 3, 4, 5 and the refutation were measured here.
