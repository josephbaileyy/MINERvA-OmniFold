# FINDING 2026-08-13 — A commit id, date and message were verified as STRINGS while the claim built on them never met the diff

**`BEN-215`.** Lane A block (`210-219`). Measured, live. Full physics context:
`ADVISORY-20260813-eavail-published-conventions.md` §2.

## The claim, and how much weight it was carrying

`ADVISORY-20260813-oi30-eavail-residuals.md` §1 — echoed verbatim into `docs/OPEN_ITEMS.md`'s `OI-30`
row and labelled there **`PROVENANCE SETTLED`** — read:

> *"The same organisation **fixed the identical constant in its other implementation of the same
> quantity**: `GENIEXSecExtract/src/XSec.cxx`, commit `564e2788051f`, 2021-11-26 … a different MINERvA
> developer, in a different MINERvA repository implementing the same quantity, called `135` a
> neutral-pion-mass mistake and fixed it **four months later**."*

That sentence is the entire evidential basis for `OI-30(a)`, and `OI-30(b)` — the MAT-compatibility
conflict Joseph committed publicly to putting to Gregor — rests on it.

## What was actually checked, and what was not

The advisory states *"Codex's id and date verify."* **They do.** The commit exists, the sha is right, the
date is right, and the message is quoted correctly including its hedge.

**Nobody opened the diff.** `MinervaExpt/GENIEXSecExtract` is a **public GitHub repository** — reachable
in one `gh api` call with no credentials beyond the CLI already installed. Measured here, all 8 commits
that have ever touched `src/XSec.cxx`:

| commit | UTC | author | what it did |
|---|---|---|---|
| `03ebef5fd197` | 2021-07-28T15:51:11Z | Andrew Olivier | *"Imported … from the MINERvA 101 tutorial"* — brings in `case kPZRecoil:`, whose recoil coordinate uses `mass_pion = 135` |
| `0e6740cec071` | **2021-11-26T10:14:03Z** | abbeywaldron | **creates `case kEAvail:`, already `139.57`** (+21/−0) |
| `564e2788051f` | **2021-11-26T10:17:10Z** | abbeywaldron | **+1/−1**, `135` → `139.57` |
| `2f0097bde564` … `374082adf7b1` | 2022-03 → 2023-04 | Hang Su, A. Olivier, A. Waldron | species extension and later variants — see `BEN-217` |

**Three errors, and all three run in the same direction:**

1. **"four months later" → three minutes and seven seconds later**, by the **same author**, in the same
   sitting. The four months came from differencing against MAT's 2021-07-07 commit **in a different
   repository** — not the thing `564e2788051f` changed.
2. **"its other implementation of the same quantity" → a different quantity.** The patch is +1/−1 and its
   indentation locates it: it removes `\t\tdouble mass_pion = 135;` (two tabs), whereas `kEAvail`'s
   declaration is `\t    double mass_pion = 139.57;` (one tab, four spaces). Confirmed by fetching the
   blob at both refs — the file holds **two** `mass_pion` declarations and the one fixed is inside
   **`case kPZRecoil:`**, a `(recoil, pt, pz)` hyperdim **bin-number lookup**. **`case kEAvail:` never
   contained `135` for one second of its existence.**
3. **The independence the argument rests on does not exist.** Not two implementations converging on a
   correction — one person who had just written `139.57` in a new function noticing the pre-existing site
   next door disagreed. Unreviewed, and hedged *"I think"*.

## The mechanism: a corroborating citation is the one checked least

**All three errors made the evidence look MORE independent than it was**, and that is not a coincidence.
The citation's job in the argument was corroboration — a second, arm's-length party reaching our
conclusion. A reading that delivers exactly that is the reading nobody re-opens. The advisory even
flagged, correctly and in bold, that its *first* version had overstated the attribution ("the author
admitted his own bug" — two different people, two repos) and fixed that. **The correction pass tightened
the who and left the what unexamined.**

Note what was *not* missing: sourcing discipline, a named instrument, or a verification step. The id and
date were checked against the upstream repo. **What was checked was the citation's identity, not its
content** — and for a claim of the form *"X fixed Y in Z"*, identity is the cheap third of it.

## The conclusion survives, on a better basis — and this is why the row is not a retraction

`abbeywaldron`, writing a MINERvA low-recoil `E_avail` from scratch in November 2021, **chose `139.57`
unprompted on the first try**, then went back and labelled the inherited `135` a bug. That is real
evidence about what MINERvA's low-recoil closure-test author believed correct, and it is *stronger* than
"someone fixed a copy four months later."

**And the two `135`s are not independent either.** The only `135` ever present in public
GENIEXSecExtract arrived in the 2021-07-28 import *"from the MINERvA 101 tutorial"* — **the same ancestor
as our `CVUniverse.h:364`**, which lives under `MINERvA101/MINERvA-101-Cross-Section/`. Ours and theirs
are one inherited copy, not two choices. So `OI-30(a)`'s π⁰-reuse verdict is *strengthened* while its
corroboration is *removed*.

**What had to go is the framing**, and it had to go before it reached Gregor: "two independent
implementations of the same quantity agreed that `135` is wrong" is the kind of claim an advisor checks,
and it does not survive one `gh api` call.

## The check

- **Verifying that a cited commit EXISTS is not verifying what it CHANGED.** For any claim of the form
  *"party X fixed constant C in implementation I"*, fetch the patch. `gh api
  repos/<org>/<repo>/commits/<sha>` gives filenames, `+/−` counts and the diff.
- **A `+1/−1` patch has exactly one changed line — read it, and read its indentation.** Here whitespace
  was the only thing distinguishing two same-named declarations in one file, and it settled the finding.
- **Diff the DATES you are about to characterise.** "Four months later" was a subtraction nobody
  performed; `10:14:03Z` → `10:17:10Z` is visible in the same API response.
- **Give a corroborating citation the same scrutiny as a contradicting one.** Sibling of `BEN-206` (the
  interesting finding outruns the boring check) with a sharper trigger: **when a source's role in the
  argument is to agree with you, that is the moment to open it.**
- **Check whether the "other" repository is public before assuming it is not.** Nobody stated that
  GENIEXSecExtract was unreachable; it was simply never tried, and MAT-MINERvA's genuine privacy nearby
  made unreachability the default assumption for both.

## Related

`BEN-217` — the same pass, same repo: `kEAvail`'s history was not read either, and that turned out to
matter more. `BEN-172` (cite-without-opening) is the ancestor; this is its sharper case, because the
source *was* opened — as a string.
