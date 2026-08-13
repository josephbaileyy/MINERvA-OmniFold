# FINDING 2026-08-13 — the summary that outran its sources

**BEN-174, BEN-175, BEN-176, BEN-177, BEN-178.** Lane D (verifier), sole-auditor pass on
`docs/EAVAIL_DEFINITION.md` at `bcdb388`, commissioned by its own author.

**Per-claim adjudication lives in `VERDICTS-20260811-session-D.md` §V34–V40 and is not repeated here.**
This file is the transferable part: five distinct ways a *summary* document drifted from sources that
were themselves correct, and the check that catches each. Written once here, indexed there.

## Why this document and not another

`EAVAIL_DEFINITION.md` is the only artifact in this campaign written to leave the collaboration —
Joseph intends to paste it to Gregor Kafka and defend it line by line. Its sources (`OI-30`, `OI-56`,
`OI-59`, two advisories, `VALIDATION_LEDGER.md`) are careful, heavily corrected, and in several places
explicitly self-retracting. **Every defect below was introduced in the summarising step, and none is an
arithmetic error.** All five numbers re-derive from their operands; the bracket `[7.7%, 297%]` is a
genuine one-assumption span; nothing is adopted and nothing unfrozen. **The document passes every check
that has a number in it.**

That is the finding. A summary is not audited by re-checking its arithmetic.

## 1. The dropped qualifier (BEN-174)

`OI-56` says *"ours is the 2016 convention **minus e±**."* `VALIDATION_LEDGER.md:1331` says *"closed
**four-species** list."* `CVUniverse.h:361-374` implements four species in fourteen lines with no e±
branch. The summary's headline paragraph — the one framed *"in one paragraph"*, i.e. built to be
extracted — says we implement Rodrigues *"deliberately and uniformly … over a closed **five**-species
list"*, while enumerating **three** (it drops γ).

Three counts in one sentence, no two agreeing, and the true one is in a source that states it in words.

> **Check:** for each load-bearing claim in a summary, find the sentence in the source it compresses.
> If the source spends words on a qualifier and the summary spends none, that is the finding — not a
> stylistic difference. Qualifiers are the first thing compression deletes and the last thing a reader
> can reconstruct.

The related trap: **"deliberately"** and **"uniformly"** assert intent. The advisory concludes the
opposite — *"our exclusion follows the νe-era code and not the νμ paper"* — and traces `135` to an
inherited tutorial import. **An adverb of intent placed where the record shows inheritance is a claim
with no evidence behind it and no obvious place to check it.**

## 2. The comparator swap (BEN-175)

Four independent sources — `OI-56`, `OI-59`, advisory §6, `VALIDATION_LEDGER.md:1334` — attribute
`+212.18` MeV/event, `4.837%` and `−10.99%` to *"the reference rule"*, meaning
`GENIEXSecExtract`'s `case kEAvail:`. The summary calls them the effect of moving to *"the open
convention"*, meaning Ascencio 2022's published Eq. 1. The advisory devotes an entire section to
keeping those apart, because `kEAvail` post-dates Ascencio v1 and cannot have produced its numbers.

They differ on **e±** (`kEAvail` excludes, the open list includes at total E) and on **the clamp**.

**The document refutes itself, which is what makes this checkable rather than arguable:** *"four species
carry the disagreement"* is true against the code and false against the open list — five, once e± is
counted — and the same document asserts twenty lines later that the papers include e± and we do not.

> **Check:** every measured number has a comparator. Name it, then find the sentence in the source that
> names it. `BEN-150` is this at the level of two JSON keys; this is the same defect between a
> *measurement* and a *convention*. A number keeps its label when it changes hands, and the label is
> the part nobody re-derives.

Direction matters and is worth recording: including e± makes the shift **larger**, so the relabelled
number understates the quantity it is relabelled as. ~0.7%. **Small, and favourable — which is why
nobody would have caught it downstream.**

## 3. Who gets which verb (BEN-176)

`minerva-ml` is `gregorkrz/minerva-ml`, the repository of the person the document is addressed to.
`OI-30` records neutrally that it *"adds ~140 MeV/pion"*. The summary's opening paragraph upgrades this
to *"that is a **defect in that code**, not in ours."*

The mirror-image case — e±, where `minerva-ml` matches Rodrigues and we do not, same class of
disagreement, same kind of evidence — sits forty lines later, and §5 characterises **our** divergence as
*"a **declared convention choice**."*

On substance the defect verdict holds: all four comparators specify charged-pion *kinetic* energy.
**That is not the finding.** The finding is the asymmetry between the two verbs, in a document whose
purpose is to be read by the party on the wrong end of the harsher one.

> **Check outbound documents for who gets which verb.** Where we differ from someone, and they differ
> from us, both sentences should be constructible from the same template. If ours reads "convention
> choice" and theirs reads "defect", the document is arguing rather than reporting — and it discredits
> numbers that are sound.

## 4. The complete-looking list (BEN-177)

*"Correcting it is a **five-site change or nothing**: `CVUniverse.h:364` plus four generator converters
that bind to our value by comment."*

Executed — [`state/probe-eavail-pion-mass-sites-20260813.py`](state/probe-eavail-pion-mass-sites-20260813.py),
five arms with expectations predeclared before the run:

| arm | expected | observed |
|---|---|---|
| P1 sites the document names by path | 1 | **1** — it names one of its five; the rest must be re-derived |
| P2 code sites binding `135` as an E_avail π± mass | > 5 | **6** |
| P3 of the 4 converters, how many bind BY COMMENT | 2 | **2** |
| P4 CONTROL `139.57` in an E_avail π± term | 0 | **1** — fired |
| P5 each `135` declaration has a re-read use line | 6 | **6** |

**The uncovered site is `nd-unfolding/pet/pointcloud_projection.py:51`** — the PET truth-cloud projector,
the path the live Gate-5 campaign runs — and **the document's own source names it**, at
`ADVISORY-20260813-oi30-eavail-residuals.md:95`, as one of *"the two mirrors deliberately kept in
lockstep"* that *"will **silently desync** if only one is changed."* The GiBUU pair
(`gibuu_to_xsec3d.py:53`, `gibuu_to_xsec_eavailW.py:38`) are bare copies with no comment.

**Both errors run the same direction: the repair looks smaller and more greppable than it is.** A
repairer executing "or nothing" faithfully produces exactly the partial change that phrase exists to
forbid, in the live path.

> **Check:** an "N-site change or nothing" is a completeness claim, and completeness claims are the
> cheapest kind to execute. Run the enumeration. A list that names one of its N members cannot be
> executed at all without re-deriving the rest — at which point the count is decoration.

Compounding, and not this document's fault but on its execution path: `pointcloud_projection.py:50` and
`POINTCLOUD_PROJECTION.md:28` both cite *"`GetEAvailableTrue()` … (CVUniverse.h:330-343)"*, which is
`GetRecoClusters`. The function is at `:361-374`. Already-filed shape —
`FINDING-20260813-line-range-on-a-file-that-never-existed.md`.

### Two of the probe's own arms fired

**P4 expected 0 and observed 1.** The ±8-line context window cannot separate `M_PION_EAVAIL = 135.0`
(`:51`) from `M_PI = 139.57` (`:55`), four lines apart in one file. **Left at its predeclared
expectation** rather than moved to 1 — adjusting an expectation after seeing output is how a probe stops
being able to fail. It also surfaced a hazard nobody had named: that file holds both constants on
purpose, and correcting the convention one to `139.57` makes them identical and the separation invisible.

**P5b, the arm built to refute the finding, fired too** — it reported only 2 of 6 declarations reaching
an accumulation line, which would have meant four of the six sites were dead code and the count
inflated. **All six use lines were read by hand before the regex was touched**, in that order. All six
are genuine; the pattern had never covered `econ[m] = E[m] - MASS_PI`. No cleverer regex was then
written: separating *subtracted into a sum* from *subtracted to test a threshold* is semantics, and a
wrong automated oracle is worse than none. P5 is now a recorded table of six use lines re-read from
disk — whose first run caught two of the auditor's own transcriptions as fragments.

## 5. The honesty section sorted the wrong way (BEN-178)

The provenance section labels the `GENIEXSecExtract` archaeology *"Relayed from lane A and NOT
independently verified by the author"* and supplies two credential-free `gh` commands. It is the
strongest paragraph in the document.

But its other bucket — *"Measured in this repo and re-derivable: every number in §2 and §3"* — silently
absorbs the **two-paper reading**: the CLOSED/OPEN table, the *"`strange` and `kaon` appear zero times"*
count, both quotations. Those are external `ar5iv` fetches, not repo measurements, and advisory §7.1
records them as **the one item where two instruments disagreed** — a summarising and a verbatim fetch
contradicted each other about Ascencio Eq. (1)'s surroundings until a third settled it, with the note
*"the disagreement is the only warning you get."*

So the claim labelled unverified is two commands from confirmation, and the claim the document's entire
position rests on is bucketed as repo-measured, is not, and is the fragile one. **No instrument is named
for it anywhere.**

> **Check:** a provenance section sorted by *how much of this did I personally do* inverts its own
> purpose. Sort by *how hard is this for the reader to check*. The two orders diverge precisely on
> inherited-but-load-bearing claims, which is the class that needs the label most.

## What this pass did not establish

- **Neither paper was re-fetched.** The closed/open readings are taken from advisory §1. BEN-174 does
  not depend on them — it rests on `CVUniverse.h`, the ledger and `OI-56`, all in-tree — but BEN-175 does.
- **The two `gh` commands were not run.** Untested, not endorsed.
- **P2's six is a lower bound.** A regex over declarations can prove a list incomplete; it cannot prove
  a count total.
- **The auditor's own interest, named:** BEN-174, BEN-175 and the §5 gap are all *"the summary is more
  confident than its source"*, which is the shape this lane filed as `BEN-173` and is therefore most
  primed to see. The reading that would save the headline — that *"over a closed five-species list"*
  modifies Rodrigues' convention rather than our implementation — was sought and does not survive: the
  same sentence says *"we implement"* and *"deliberately and uniformly"*, and §2's table repeats
  *"what we do: implement this"* unqualified.
