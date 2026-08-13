# FINDING 2026-08-13 — the summary dropped the three words that made the finding true

**`BEN-220`.** Lane A (E_avail), source-checking `docs/EAVAIL_DEFINITION.md` (`bcdb388`) against its own
findings at the mediator's request. **The transcription is faithful in substance and wrong at its spine**,
and the two facts are not in tension — that is the point of the finding.

## What was measured, and what was written

`ADVISORY-20260813-eavail-published-conventions.md` §4, lane A's own text:

> *"We implement **Rodrigues 2016's closed list**, which is the paper that introduced the observable,
> **minus e±**."*

`docs/EAVAIL_DEFINITION.md` §1, the paragraph the whole document exists to support:

> *"**We implement the Rodrigues 2016 convention** (arXiv:1511.05944), deliberately and uniformly:
> available energy is the summed kinetic energy of protons and charged pions plus the summed total energy
> of neutral pions, over a **closed** five-species list."*

Rodrigues 2016's five species, quoted verbatim in the advisory: *"the sum of proton and charged pion
kinetic energy, plus **neutral pion, electron, and photon** total energy."* So:

| | Rodrigues 2016 | ours (`CVUniverse.h:361-374`) |
|---|---|---|
| p | KE | KE |
| π± | KE | KE |
| π⁰ | total E | total E |
| γ | total E | total E |
| **e±** | **total E** | **excluded** |

**We implement four of five.** Three failures compound in one sentence:

1. **"minus e±" is gone**, so the claim is false as written.
2. **The enumeration lists three species and calls itself five** — γ and e± both absent from the prose.
3. **"deliberately"** is asserted where the advisory's §5 traced our exclusion to `kEAvail`'s
   `abs(pdg)==11||abs(pdg)==13` *"don't count charged lepton"* branch, written for a νe analysis where the
   primary electron **is** the charged lepton. Ours follows that code, not the νμ paper. **Inherited is the
   measured provenance; deliberate is an upgrade the evidence does not carry.**

§2's table repeats it in the form a reader trusts most — a cell: `what we do | **implement this** | do not
implement`.

## Why this is a compression failure and not a belief failure

**The qualifier survives, 47 lines later, in the same document:**

> *"**The e± case cuts against us and is stated for that reason.** Rodrigues includes electron total
> energy. We exclude it. On this one species `minerva-ml` matches the νμ paper and **we do not**."*

That paragraph is blunt, unhedged, and correct. **So the document contains its own refutation** — §1 claims
we implement a published convention, §2 records the species where we do not. Nothing was misunderstood and
nothing needs re-measuring; three words need restoring.

**This is the shape worth remembering: a summary is where a qualifier dies.** The source states the finding
with its scope attached because the scope is what the measurement supports. The summary is written to be
short, and a scope clause is the cheapest thing to cut — it reads as hedging when it is in fact the claim's
domain of validity. And the summary is the artifact that leaves the building.

## What makes it dangerous here specifically

- **It runs in our favour.** "We implement a published convention" is the strongest available position;
  "we implement four fifths of one" needs a sentence of explanation. `BEN-214` recorded that
  **drift in the flattering direction has no natural discoverer**; this is the same asymmetry inside a
  single document rather than across attributions.
- **It is checkable in one step by the person it is written for.** The document exists to answer Gregor
  Kafka's question. Rodrigues 2016 is one paragraph long on this point and he can read it.
- **The document's honesty elsewhere is what makes the slip cost more, not less.** §5 is titled *"What this
  analysis does NOT claim"* and lists five things — none of them e±. A reader who has learned to trust §5
  as the complete against-us list is *worse* off than one who trusts nothing.

## A second-order observation, recorded because it inverts the usual advice

The e± item is also the one species where we differ from **both** published conventions — Ascencio 2022's
open list includes e± too (advisory §4 table). The document says only that `minerva-ml` matches "the νμ
paper" and we do not. **The stronger true statement was available and the weaker one was written.** Under
compression, understating an against-us finding and overstating a for-us one are the same operation.

## The check

**Before shipping a summary of a measured finding, diff its claim against the source's claim clause by
clause — specifically hunting for scope words the summary dropped: *minus*, *except*, *four of five*,
*on this sample*, *inferred*.** A summary that is shorter because it lost a qualifier is not a summary.

Cheap mechanical form for this repo: any sentence of the form "we implement X" where the source says "we
implement X minus Y" is caught by grepping the source for `minus|except|excluding` within the paragraph the
summary compressed.

## What was checked and held

Recorded so the finding is not read as a general indictment of the document. All verified first-hand this
session, not relayed:

- `gh api "repos/MinervaExpt/GENIEXSecExtract/commits?path=src/XSec.cxx"` → **exactly 8 commits**, ids,
  authors and UTC timestamps matching the advisory's table row for row.
- `564e2788051f` is **+1/−1**, `135`→`139.57`, at two-tab indentation, in the hunk whose context lines
  (`//recoil value` / `double recoil = 0;` / `int n_parts = …`) sit inside **`case kPZRecoil:`** (case label
  line 589, declaration line 604) and **not** `case kEAvail:` (case label 508, declaration 512).
  **The withdrawn framing is not reintroduced anywhere in `EAVAIL_DEFINITION.md`.**
- **No `135` exists in public `GENIEXSecExtract` today** — both `mass_pion` declarations read `139.57`; the
  only `0.135` is `static const double Mpi0`, correctly named.
- **`Su, H.` is among the 56 authors of arXiv:2312.16631** (*"Measurement of Electron Neutrino and
  Antineutrino Cross Sections at Low Momentum Transfer"*), and `CVUniverse.h:163` does cite that paper as
  the authority for `GetEAvailableTrue()`. The "reference implementation is not independent" chain closes.
- Every published ratio re-derives: `4.837/0.1286 = 37.61`; `1.049/13.69 = 7.663%`;
  `7.663% × √1507 = 297.5%`; `1.0563 × 4.57 = 4.8273` MeV/event; `439/65911 = 0.666%`;
  `p(χ²=1.68, 2 dof) = 0.4317`.
- The five-site correction claim holds: `CVUniverse.h:364` plus `genie_to_xsec3d.py:42`,
  `gibuu_to_xsec3d.py:53`, `gibuu_to_xsec_eavailW.py:38`, `nuwro_to_flat.C:31`. **Refinement: only two of
  the four bind by comment** — the other two carry a bare `0.135` with no reference to `CVUniverse` at all,
  which is a *weaker* coupling and therefore the more likely silent desync.

## Related

`BEN-214` (drift in the flattering direction), `BEN-215` (a citation verified as a string), `BEN-216` (a
pointer that resolves to nothing), `BEN-219` (a citation correct at write time and wrong at read time),
`OI-30`, `OI-56` (FROZEN), `OI-59`.
