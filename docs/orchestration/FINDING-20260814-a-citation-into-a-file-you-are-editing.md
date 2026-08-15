# FINDING 2026-08-14 — a line citation into a file you are editing in that commit is stale the moment you edit it

**`BEN-228`.** Lane A. **Strictly cheaper to trigger than `BEN-225`, and therefore more common: it needs no
rebase, no second lane, and no concurrency at all.** Written at the mediator's request, which called it *"the
most transferable thing"* in the report it came from.

## The mechanism

Two citations in one commit were falsified **by that same commit's own edits**:

| citation written | what it became | why |
|---|---|---|
| `ND_OMNIFOLD_STATUS.md:52` | **`:59`** | the STATUS one-liner edited *above it*, in the same commit, grew by 7 lines |
| `…gate4-nominal-promotion…json:95` | **`:102`** | a supersession block inserted *above it*, in the same commit |

Both numbers were derived correctly with `grep -n`. Both were **true when derived and false when committed**,
and the interval was minutes with nobody else involved.

## WHY THIS IS NOT `BEN-225`, AND THE DIFFERENCE IS THE POINT

`BEN-225` is: a claim verified pre-rebase, published post-rebase, falsified by **another lane's** work arriving
under a finished commit. Its remedy is **re-run the check after `git pull --rebase` and before `git push`.**

**That remedy does not catch this one.** Re-running after the rebase re-runs the *check*; it does not
re-derive the *number*. If the stale line number is sitting in prose you already wrote, a rebase-time re-run
finds nothing wrong, because nothing about the rebase caused it and nothing about the rebase reveals it.

| | `BEN-225` | **`BEN-228`** |
|---|---|---|
| needs another lane | yes | **no** |
| needs a rebase | yes | **no** |
| interval | 7 seconds | minutes, entirely self-inflicted |
| caught by re-running after rebase | yes | **no — unless numbers are RE-DERIVED, not re-used** |

**So this is the cheaper failure and it will happen more often.** Every commit that both edits a file and
cites a line in it is exposed, and multi-file bookkeeping commits do this constantly — the more thoroughly a
commit cross-references itself, the more exposed it is. **Rewarding cross-referencing while making it
self-falsifying is the trap.**

## THE RULE

> **Derive every cited line number AFTER the last edit to the file it points into. Re-derive, never re-use —
> a number you wrote down 40 minutes ago is a measurement of a file that no longer exists.**

Operationally, and this is the whole procedure:

1. Make all edits first. Do not interleave citing and editing.
2. **Then** re-derive every citation with `grep -n '<the actual text>'` — search for the *content*, not the
   line, because content survives edits and line numbers do not.
3. Only then write the numbers in, and commit without further edits to those files.
4. If a later edit becomes necessary, **go back to step 2**. There is no shortcut, because the failure is
   silent by construction.

**A cheap structural alternative where it fits: cite the content, not the coordinate.** `explicitly_not_claimed[2]`
is stable under insertion; `:95` is not. A JSON pointer, a key path, or a quoted phrase all survive edits that
a line number cannot. **Prefer them wherever the target has an addressable name** — the line number is a
last resort for prose that has no other handle.

## How both were caught, and it generalises

By re-deriving *every* cited line with `grep -n` before the push rather than trusting the numbers recorded
earlier in the same session — done because `BEN-225`'s remedy had already forced a full re-verification pass
after the third rebase of the night, and the self-inflicted pair fell out of it **as a side effect**.

**That is luck, and it should not be relied on.** Three rebases happened to force a re-derivation pass; a
commit with no rebase gets none, and would have published both stale numbers with every check green. **The
re-derivation pass therefore belongs to the commit, not to the rebase.**

## THE GENERAL FORM, which is larger than line numbers

Lane D's mediator supplied the unification and it is better than this finding's first framing:

> **A hand-maintained index of a machine-derivable fact goes stale silently.**

**A line number is exactly that** — `grep -n` derives it in milliseconds, and writing it down converts a
derivable fact into a hand-maintained one with a hidden timestamp. Every instance below is the same defect at
a different size:

| the hand-maintained index | what derives it | how it went stale |
|---|---|---|
| `…promotion…json:95` in prose | `grep -n 'That OI-23 is discharged'` | a block inserted above it, **same commit** |
| `FINDINGS.md`'s *"`221-229` free"* | `grep -oE '^\| BEN-22[0-9] \|' \| sort -u` | wrong since `BEN-221`, **in the same file as the "derived, not narrated" rule that forbids it** — cell at `:19`, rule at `:79` |
| `MANIFEST.tsv`'s `generated` + producer for `live-state.json` | reading `generate_live_state.py:22-23` | the file is that script's **input**; it is never written by it (`OI-73`) |
| a bare sha256 in prose | `git show <ref>:<path> \| shasum -a 256` | the file was edited after the note (`BEN-227`) |

**The free-list instance is the one that shows the mechanism cleanly**, because it was found only by someone
editing the row for an unrelated reason — the filer is the last person who will ever reread their own
free-list, so the index is maintained by exactly the party with no reason to check it. **`OI-73` is this
shape one size up**, and it is the worst of the four because its stale index does not merely mislead: it makes
the documented remedy look forbidden, so following the procedure exactly cannot fix it.

**The unified rule, and it subsumes the procedure above:** *if a fact is machine-derivable, cite the
derivation or an address that survives edits — never the coordinate.* Content addresses
(`explicitly_not_claimed[2]`, a quoted phrase, a key path) survive insertion; line numbers, counts and
free-lists do not.

## Related

`BEN-225` (the concurrency version, and the remedy that does *not* cover this), `BEN-219` (a citation correct
at write time — same family, longer interval, different cause), `BEN-216` (why cited ids are not renumbered),
`CONVENTION-verifying-a-check-is-deployed.md` (*a fact about a concurrently-written repository is a measurement
with a timestamp* — here the repository is not even concurrent; the writer is).

## DERIVE THE INDEX AT READ TIME — and why the check is NOT armed tonight

Added 2026-08-15 at the mediator's request, after this rule caught its own author a second time: lane A nearly
filed a duplicate `BEN-229` on the authority of an index cell reading *"NO BEN ROW"*, in the file where this
finding lives, while `BEN-210` and `BEN-211` had pointed at that same finding since 2026-08-13.

> **THE RULE: whether a finding has a ledger row is DERIVABLE. Derive it at read time; do not trust a cell that
> asserts it.** One command, and it is cheaper than the mistake it prevents:
>
> ```
> grep -n 'FINDING-<date>-<slug>.md' docs/orchestration/FINDINGS.md
> ```
>
> **Both times this rule was caught being broken, it was caught by someone running one `grep` — not by any
> mechanism.** `BEN-228`'s remedy is currently enforced by attention, which is the property it says not to rely
> on. That is stated rather than hidden, because a rule whose enforcement is attention should not be read as a
> rule whose enforcement is a check.

**THE EXECUTABLE FORM WAS MEASURED AND DELIBERATELY NOT ARMED, and the measurement is the reason.** A check
asserting *"every indexed finding has a row"* would be the natural gate. Run over `FINDINGS.md` at
`a642edb`: **80 index entries, 234 `BEN-*` rows, and 31 indexed findings carry no row at all** — every one of
them dated **2026-07-30 to 2026-08-12**, i.e. before the row-per-finding convention took hold, while nearly
everything from 08-13 onward has one.

**Those 31 are not drift and must not be treated as such.** Backfilling them is what `BEN-080` forbids:
back-filling sorts a new item among old ones and destroys the one thing an id's ordering carries. So the gate
would fail closed on 31 entries that are correct as they stand, block four live lanes, and its only available
remedies would be a mass backfill (forbidden) or 31 waivers (a hand-maintained index of a machine-derivable
fact — this finding's own defect, one level out). **`BEN-226` applies too: a hook check has no advisory
channel, so "warn about the 31" does not exist.** The honest state is **one** genuinely stale cell, now fixed,
against 31 by-design absences — a ratio that does not justify a gate.

**AND THE MEASURING INSTRUMENT WAS ITSELF NON-COVERING, which is the fourth instance of that class tonight.**
Lane A's first detector matched only the markdown-link form `[Detail](FINDING-….md)` and reported **40**
mismatches. Rows that cite their file with backticks instead — `BEN-233`'s *"See `FINDING-…md`"* — were
invisible to it, **8 of them**. Matching any mention of the filename gives 32, of which 31 are the
by-design absences. **A tool built to detect stale indices was itself wrong about the index**, and the error
was in the direction of over-reporting a defect. Joining `awk -F'|'` counting `\|` escapes, `TZ=UTC` with
`--date=format:`, and `which sbatch` as a covering search: **four instruments in one night that answered
confidently outside the domain they were built for.** The generalisation is the mediator's and it belongs
here: *validate an instrument against a case it should get wrong, before believing a number it produces.*

**AND THE NOT-ARMED DECISION GOT ONE MORE PIECE OF EVIDENCE, from the fix itself.** The corrected index cell
now records what it used to say — *"this cell read `NO BEN ROW` until 2026-08-15"* — and **lane A's detector
still flags it**, because a scanner looking for the string `NO BEN ROW` cannot distinguish an **assertion**
from a **quotation of a retracted assertion**. The cell is right; the scanner is wrong; and the scanner cannot
be made right without understanding that a retraction quotes what it retracts.

**This is `BEN-227`'s argument, independently confirmed by a second instrument.** `BEN-227` ruled *against*
prose-scanning for digests on the prediction that it *"false-positives on every digest legitimately quoted as
history, and this repo quotes retired digests deliberately."* That was reasoning; **this is a measurement of
the same failure in a different scanner on the same day.** Any gate built by pattern-matching prose in this
repository inherits it, because **retaining superseded text beside its correction is a deliberate convention
here** (`INDEX-retracted-and-superseded-values.md`, and every `DO_NOT_RECORD_AS` block). A checker that
punishes that convention will be switched off, and should be.

**So the gate is refused on two independent grounds, not one:** 31 pre-convention absences that `BEN-080`
forbids backfilling, **and** the fact that the only cheap way to detect the defect cannot tell a correction
from the error it corrects.

**A POSTSCRIPT IN WHICH THE REMEDY WORKS PROSPECTIVELY, which is the first time tonight one did.** The counts
above are written *"at `a642edb`"* rather than bare, per `BEN-227`. The very next rebase pulled in another
lane's row and took the total from **234 to 235**. **A bare "234 `BEN-*` rows" would therefore have been false
in the commit that published it — `BEN-225` exactly — and quoting the ref is the only reason it was not.**
Verified rather than assumed: `git show a642edb:docs/orchestration/FINDINGS.md` counts **234** rows and **80**
index entries, so the claim is true as scoped and stays true permanently.

Every other instance in this file is a rule catching an error after the fact. This one is a rule **preventing**
one, and it is worth more than the rest: `value + ref` converts a perishable measurement into a durable fact,
so the number needs no maintenance and no re-derivation. **That is the whole argument for the executable form,
demonstrated on the smallest possible case.**
