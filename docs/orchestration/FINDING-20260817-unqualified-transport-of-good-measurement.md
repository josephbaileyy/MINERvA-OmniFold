# Unqualified transport of good measurement — four instances in one day, no bad measurement among them

**BEN-392.** Filed 2026-08-17 by the seconding lane (block `390-399`). **The four transports are the
mediator's** (`personal-orchestrator` / peer session `minerva-omnifold-72`), which relayed them for filing;
the catches are three by a second Claude session and one by lane `C`, plus C's own self-catch. **Provenance
of the evidence is split and the split is marked per instance below** — one instance re-derived here with a
control, one re-derived here in the course of `BEN-391`, and two relayed and **not** re-derived.

## The defect

> **A number or claim that is correct in its original context, quoted where its qualifier does not hold.**

| quoted | true of | quoted as true of | verified here? |
|---|---|---|---|
| `7.8 GPU-h` | `n=1`, both arms | an `n>=6` design (real cost `39.0`, outside the `24 A100-h` grant) | **no** — relayed |
| *"no committed document records which scalar"* | **documents** | **code** (the spec was at `a0cdc019`, `unified_throw_cov.py:224`, with its derivation) | **yes** — see `BEN-391` |
| `~1 GPU-node-hour` | AI1's footing (`of_inputs_5d.npz`, fixed data seed 0, no flux universes) | the candidate's footing (measured unit `28.50 A100-h`, `28.5x`) | **no** — relayed; **and `28.50` is itself superseded, see below** |
| `8874f1f` | an ancestor of `origin/main` | the identity of the scoreboard commit (which is `2a92c71`) | **yes** — measured, with a control |

**Not one of these is a bad measurement.** Every committed source was correct. In three of the four the
qualifier was **present in the source document and dropped in transport** — in a dispatch or a report. So the
recurring defect on this campaign today is not bad measurement; it is **unqualified transport of good
measurement**, which no amount of re-measuring the source would have caught.

## The cheap check, which caught all four

> **Re-derive the quoted number from its stated operands before acting on it.**

This is `CONVENTION-receipt-ingredients.md` / `BEN-077` turned around: that convention obliges a *writer* to
ship the ingredients of every derived quantity; this row says **the reader's obligation is to use them.** The
convention was already paying for itself in the direction it was written — `BEN-077` was found by failing to
derive a published ratio from published operands — and the same arithmetic, done at read time, is what
exposed all four of these.

Worked, on the first row, from the operands as relayed: `39.0 / 7.8 = 5` exactly, and `39.0 > 24`, so the
design is outside the grant. **The derivation also raises a question the quoted figures do not settle:** a
multiplier of `5` against a design described as `n>=6` needs one further ingredient to be consistent (e.g.
one arm already spent). That is the check working as intended — arithmetic on the operands either reproduces
the claim or names the missing ingredient, and here it does the second.

## Amendment, same day — instance 3's *corrected* value was also wrong

Added after lane B filed `BEN-247` (`6afda0e`) hours later. **`28.50 A100-h` — the figure this row quotes as
the true footing — is itself superseded by `39.078`.** Its lateral term `3.626` came from **5 `COMPLETED`
tasks of a 19-task leg**; the completion run `55894759` was absent from the table, and B's arithmetic
reproduces exactly here (`23.840 + 14.2075 + 1.030 = 39.0775`, `+37.1 %` on `28.50`; `14.36` vs `14.2075`
agree to `1.07 %`). Verified same-quantity rather than assumed: `SCOREBOARD-20260817-quarantine-seven-causes.md:133`
— *"The measured unit on the candidate footing is **28.50 A100-h per re-seed**, ~28.5×"* — is the sentence
instance 3 was drawn from, and it is the same per-re-seed cost B corrected.

**This makes the row's own point against the row: the transport error is LARGER than stated (~39×, not
28.5×), and the descendant ratio `28.5×` does not string-match `28.50`,** which is the first write-time rule
in `INDEX-retracted-and-superseded-values.md` — a retraction propagates by string match and derived
quantities do not. Both the value and its descendant ratio are now indexed there, with the sites that still
carry them.

**Not corrected by me: the six surviving sites owned by other lanes**, including the ones carrying a pending
decision to Joseph at the low figure (`COST-20260817-mii-seed-scan-derivation.md:154,160`,
`SCOREBOARD…:133-134,161`, `HANDOFF-20260817-1133Z.md:39,41,98`,
`PREDECLARATION-20260817-mii-seed-scan-cause-3.md:88,92`,
`FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md:71`). Their owners were told; the index
entry is the mechanism that reaches a lane nobody thought to notify, which is `BEN-302`'s whole point.

## The fourth instance is a verification-method defect, not a citation slip

The peer verified commits with:

```bash
git merge-base --is-ancestor <sha> origin/main   # and read a pass as "this sha is the commit I named"
```

**Every sha on `main` passes that check.** Measured here, with a control:

| sha | subject | `--is-ancestor origin/main` |
|---|---|---|
| `8874f1f` | *Regenerate MANIFEST and LIVE-STATE after merge* | **PASS** |
| `2a92c71` | *Quarantine scoreboard: seven causes, four legs, candidate and quoted product in s…* | **PASS** |
| `d3239355` (repo's oldest commit) | — | **PASS** |

So the claim *"`8874f1f` is the scoreboard commit"* was checked by a test that `8874f1f`, `2a92c71` and the
root commit all pass identically. **It confirms MEMBERSHIP, never IDENTITY — a check that cannot fail, which
is worse than no check because it manufactures confidence.** The scoreboard commit is `2a92c71`.

> **Rule: run `git show --stat <sha>` beside any ancestry test**, so the sha has to match the content being
> claimed. An ancestry test answers *is this on main*; only the content answers *is this the commit I mean*.

`BEN-390`'s exit-code problem is the same failure at the process level (a signal that is 0 whatever
happened), and `BEN-380`'s definite description is the same failure in prose. **A check with no failing case
is not a weak check; it is not a check.**

## Attribution, and the point about the two-session rule

All four transports are the mediator's. Three catches are the second session's, one is lane C's — **and C
also caught its own** (`--diff-filter=D`, `BEN-391`), which is the harder direction.

The rule that produced them is **Joseph's 2026-08-17 two-session rule, and its entire value today has been
the second key coming back NEGATIVE — three for three.** A quorum of agreeable sessions ships all four of
these. **The obvious misreading of a "two sessions must agree" rule is that agreement is the goal**; the
day's record says the rule pays only when the second session is positioned, and willing, to dissent. This
repo already refuses *"worker agreement is not verification"* for physics claims (`CLAIMS.md`); the same
refusal applies to the control plane.

## Relation to the other rows filed in this commit

- **`BEN-390`** — a delegate failure has no reliable signal. An instrument-level instance: exit `0` is a
  correct statement about a process that is quoted as a statement about the work.
- **`BEN-391`** — a narrowing flag guarantees its answer. Its instance 2 is this row's instance 2 seen from
  the other side: the sentence was correct **about documents** and was transported to a question **about
  code**.

They are arguably instances of this row and are kept separate deliberately: each has its own executable
remedy (a report-format check; an unrestricted control run), and a merged row would carry three remedies
under one headline that names none of them.

## Cross-references

`BEN-077` / `CONVENTION-receipt-ingredients.md` (the writer's half of this rule) · `BEN-380` (a definite
description is not a citation) · `BEN-303` (a job id in a receipt is a measurement, not a label) ·
`CLAUDE.md`'s `BEN-027` rule — *every id, rank, count and queue name must come from a command run in the same
turn*, which is this defect's already-written special case for status reports.
