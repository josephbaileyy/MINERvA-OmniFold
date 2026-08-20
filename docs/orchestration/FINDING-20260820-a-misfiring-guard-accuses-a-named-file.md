# 2026-08-20 — A MISFIRING FAIL-CLOSED GUARD DOES NOT MERELY BLOCK. IT ACCUSES A NAMED FILE, AND THE ACCUSATION IS THE DAMAGE.

**BEN-469.** *(id taken from lane C's `460-469` block, derived free by BOTH routes immediately before filing — `git grep -ohE 'BEN-469' origin/main` and `grep -rhoE 'BEN-469' --exclude-dir=.git .` each returned 0. This filing EXHAUSTS `460-469`. Note the table's clause read "466-467 filed … 469 free" while `468` was also filed — stale again, exactly as that cell warns. And a naive "highest id anywhere" sweep returns `BEN-505`, which is a FIXTURE STRING in `test_ben_filing_owner_check.py:102`, not a filing: a derivation over all files includes files that deliberately contain fake ids.)* Related: `BEN-040` (a fixture shaped like the consumer, not the producer, makes a fail-closed gate
untestable), `BEN-474` (an instrument's conditions are part of the measurement: stricter is a false alarm,
looser is a false pass, and neither appears in its output), `BEN-485` (a caveat's author had the reuse made the
point).

## The instance

Remedy (A)'s wrapper, `nd-unfolding/mii_adopt_unified_5d_stamped.py`, closes a TOCTOU window it opens: having
re-read the combined intermediate after the pinned child exited, it requires the re-read trace to reproduce the
`sqrt_tr_old` the child stamped from *its own* read. Sound design, and the wrapper's author named it as the
compensating benefit for the extra read.

Its reader integer-truncates:

    :375   out[k] = int(obj.GetVal()) if obj else None

`sqrt_tr_old` is a `ROOT.TParameter("double")` (`adopt_unified_5d.py:177`) whose value is
**`4.357790406860002e-38`** (`VALIDATION_LEDGER.md` VL1). **`int(4.357790406860002e-38) == 0`.** So the
comparison takes its `want == 0.0` branch and **refuses on every real product**, before a single key is written
— which means `hDiagCombinedOld`, §11g's precondition and `sqrt_tr_old`'s only surviving ingredient, is never
produced. The remedy is inoperative in all cases.

## Why this is not just "a guard misfired"

**The refusal message names the combined intermediate as the culprit:**

> *the re-read diagonal of `hCov_combined5d_total` has trace 1.899…e-75, but the child stamped
> `sqrt_tr_old=0.0` … The combined intermediate is not the matrix this product was built from — refusing to
> write `hDiagCombinedOld` from it.*

That artifact is the **41.44 GB member intermediate** whose only regeneration path costs **2.087 TiB**. On the
cluster this reads as a corruption or TOCTOU event on precisely the file the campaign cannot afford to lose,
emitted by a check whose whole purpose is to protect it.

**So the failure mode of a misfiring fail-closed guard is not silence and is not merely a blocked pipeline. It
is a FALSE ACCUSATION WITH A NAMED DEFENDANT.** And the more expensive the artifact the guard protects, the more
expensive its false accusation, because the accusation will be *believed* — it comes from the one instrument
built to notice that exact problem. The plausible next action on reading it is to distrust or re-derive a 41.44
GB file that is fine.

**THE REVIEW QUESTION THIS ADDS, AND IT IS CHEAP:** for every fail-closed guard, ask *what does its message
accuse when it misfires, and what would a reader do about that?* A guard that says "refusing: I could not
establish X" costs a stall. A guard that says "artifact Y is wrong" costs whatever acting on Y costs. **These
should not be written the same way, and today they are.** Where the guard cannot distinguish "Y is corrupt"
from "I could not read Y at the right type", it must say the second, because the second is always true when
the first is.

## The cause is the fixture rule, and the magnitude was already written down

The suite had 34 tests and no power here **in either direction** — a mutation that *fixes* the coercion also
leaves all 34 green. `TheDiagonalIsTiedToTheProduct` passes `math.sqrt(t)` — **a float it constructs itself** —
into the assertion, and **its own docstring says "The 5D traces are ~1e-76."**

**So the author knew the magnitude, recorded it in the fixture's own docstring, and did not carry it across the
one boundary the wrapper's reader crosses.** A fixture that obtained the anchor the way `main` does — through
`_read_scalars` — would have failed on day one. This is `BEN-040` in its exact shape: the fixture was shaped
like the *consumer* of the value, not like its *producer*.

**A denormal-range double is the ideal carrier for this class**, because every intermediate representation of
it looks fine. It prints, it compares equal to itself, it survives JSON — and one `int()` sends it to zero with
no exception, no warning, and a comparison that still runs.

## The generalisation

**A TYPE COERCION IN A READER IS A SILENT DATA LOSS AT EXACTLY THE POINT WHERE NOTHING RE-READS THE SOURCE.**
`int()` on a value whose scale is `1e-38` is not a rounding error; it is a total loss that leaves a *valid*
number behind, so every downstream check is well-formed and wrong. The guard against it is not more assertions
downstream — it is **building the fixture from the producer**, which is the only construction that has to cross
the coercion.

## Both instruments, and what each one did and did not find

- **The mediator's mechanical check** (`VERIFICATION-20260820-...-mechanical.md`) found no regressions, all
  bindings intact, and a symmetric +35-tests/0-regressions comparison. **All true, and blind to this**, because
  every test it ran was one of the 34 with no power. It also framed what remained as a *cluster-execution* gap —
  understating it, since D1 is reachable by static reasoning and needs no ROOT at all.
- **The governing ruling** (`RULING-20260820-...`) was right that the table row should not be gated on cluster
  execution, **and its own "Open" section was the place to ask what the wrapper's reader does to a `double`.**
  It did not. Neither did the builder, nor the mediator. **That question is not asymmetric — it is the one
  question the wrapper form newly creates**, because the in-file edit had `diag_comb` in memory and never read a
  scalar back at all.

*Found by lane C by MUTATING the code and predicting each outcome first — 8 mutations, 2 caught, 6 survived.
Reading the file had already happened, three times, by three parties.*
