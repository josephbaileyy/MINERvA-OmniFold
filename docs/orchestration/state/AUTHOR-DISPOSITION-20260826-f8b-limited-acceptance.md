# AUTHOR DISPOSITION — F-8(b) mechanical prefilter, LIMITED acceptance

> **SUPERSEDED IN PART, 2026-08-26.** The instrument this disposition accepts *as a prefilter* has
> since been redesigned to have **no passing exit status at all**, after the §10.1 readiness review
> ruled its `rc=0` a fail-open gate. See
> `DESIGN-20260826-f8b-no-green-linter-and-attestation-gate.md`.
>
> **CITABLE FOR:** the grader's verdict, the contradiction inside it, the preserved BREAK texts, and
> the false-positive surface. **NOT CITABLE FOR:** the `rc=0` semantics, which no longer exist, or
> for the BREAK-1 result, **which does not reproduce** — corrected in §"Correction" below.

**AUTHOR SYNTHESIS.** Written by `claude-school-main` (publication close-out lane), which **wrote the
instrument this disposition is about**. It is not grader output. The grader's own file is preserved
verbatim beside it and governs wherever the two differ.

| | |
|---|---|
| graded commit | `f72b7282` (branch `f8b/receipt-authoring-20260826`) |
| parent | `4beb63ee769cbeb8c11d5d2be0cf58b5378ed2ea` |
| grader | `agy-capacity-probe`, conversation `dc2b899d-a8b0-40a4-aa8d-707c49b391a3` |
| verdict file | `docs/orchestration/runs/agy-capacity-probe/20260826-f8b-VERDICT.md` |
| sha256, pre- and post-copy identical | `cab5b89636f8396c0e04cd526c6316ae84e82458b387d2cf1f1c7f0fcb8c084c` |
| bytes | 4932 |

## The verdict, and the contradiction inside it, both recorded

`F8B-GRADE: FIT` — interpretation sound YES, fail-closed in both directions YES, scope clean YES,
zero `FAIL` strings anywhere in the file.

**The same file also says, in its own words: "Both BREAKs worked, establishing real findings that
demonstrate the check's fail-open modes."** A verdict of *fail-closed in both directions: YES*
alongside *demonstrated fail-open modes* is a contradiction on its face. **It is not smoothed away
here, and it is not resolved by this lane.** The reading that makes it coherent — the grader's Item 1
— is that the check is *"TOO WEAK as a complete discharge of the clause, but appropriately scoped as
a mechanical check"*: fail-closed **within** what it advertises, fail-open against the clause. A
reader who takes the summary line without Item 1 will over-read it.

## ACCEPTED, AND ONLY AS THIS

The FIT is accepted as applying **only to the advertised mechanical prefilter**. Specifically:

**`rc=0` FROM THIS INSTRUMENT CANNOT DISCHARGE F-8(b), AND CANNOT SUBSTITUTE FOR INDEPENDENT SEMANTIC
JUDGMENT OF THE REAL RECEIPT.** It establishes three narrow facts — a blind-spots section exists, all
four spots are addressed by concept, and the section is not a long verbatim paste. It establishes
nothing about whether the author engaged with the blind spots, which is what the clause
*"in the receipt's own words"* actually demands.

## The two successful BREAKs, verbatim from the grader

Preserved exactly. They are the specification for any future hardening, and the reason `rc=0` is
weak evidence.

**BREAK 1 — keyword-stuffing, recorded as `rc=0`; MEASURED `rc=3`, see the correction below.**
Concepts mentioned without saying anything real:

```
# blind spots
origin is none sys.modules child process .sh
```

**BREAK 2 — moral paste under the span, `rc=0`; measured and CONFIRMED (shared span 150 of 200).** F-8(a) §1.6 pasted, with the word `potato`
interleaved to break every 200-character run:

```
# blind spots
The inventory cannot see four things, and none of them is closed here:

1. **Namespace packages.** `spec.origin` is `None` for them a potato nd `find_spec` returns before
   `checkout_root_of` is reached, so a namespace portion resolving from the wrong checkout is **not
   refused**. `nd- potato unfolding/` and `2d-unfolding/` both contain `__init__.py`-less directories with
   ordinary-word names — `tests`, `products`, `mii`, `pet`, `uq`, `se potato edscan`. A regular module in any
   later `sys.path` entry outranks a namespace portion, so this is a **narrow** hole. It is still a
   hole and it i potato s **not measured**.
2. **Modules already in `sys.modules`** when `install()` runs — the wrapper's own `argparse`, `os`,
   `pathlib`, `runpy`, `sys potato `. They were imported before the guard existed and are invisible to it.
3. **Anything in a further subprocess.** Enumerated below.
4. **The `.sh` rout potato e entirely** (B-5). Nothing in this receipt speaks to it.
```

## Correction — BREAK 1 was always refused

Measured 2026-08-26 with the exact recorded text against the pre-redesign instrument at `f31d07df`:
**`rc=3`**, `blind spot NOT ADDRESSED: already-imported-modules` and `namespace-packages`. The
string contains neither `namespace` nor any already-imported alternate, so the check refused it. The
grader's `rc=0` for BREAK 1 is wrong; BREAK 2's is right.

The keyword-stuffing **class** is real regardless: adding exactly the two missing words gives
`namespace origin is none sys.modules install( child process .sh`, one line of pure stuffing, which
the old instrument passed at `rc=0` (measured). The grader's verdict file is preserved **unedited**
— it is not this lane's to correct.

## The false-POSITIVE surface, also recorded

Grader Item 4: the 200-character threshold is *"Arbitrary, but defensible as a simple heuristic.
However, it HAS a false-positive surface"* — a legitimate receipt could share a 200-character
verbatim run by quoting clause text. So the instrument can refuse honest work as well as pass
dishonest work.

## NOT HARDENED, deliberately

No word-count minimum, no keyword-density metric, and no change to the transclusion threshold has
been added. Every such fix is an arbitrary number that would defeat these two examples and not the
next one, and would dress a judgement call as a measurement. **The defensible position is that
F-8(b) is grader-judged by construction**: the instrument's job is to catch the honest mistake — a
missing spot, an empty section, a lazy full paste — and a mandatory independent prose judgment does
the rest. Whether that pairing is safe or is itself a fail-open gate is **referred, not decided
here**.

## What this changes

Nothing scientific. No estimator, covariance, claim, adoption, compute result, launcher or generated
scientific state. **Gate 2 remains FAIL.** F-8(b) is not discharged: discharge needs a real rehearsal
producing a real receipt that passes this prefilter **and** a grader's judgement of the prose. No
rehearsal is authorized, none was run, and no receipt for `k0-aa67c426-20260824T145751Z` is created
or backfilled.
