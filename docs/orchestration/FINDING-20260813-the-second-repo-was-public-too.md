# FINDING 2026-08-13 — the second repository was public too, and the lesson had already been filed

**`BEN-221`.** Lane A (E_avail). Found in the same session, in the same document, immediately after
`BEN-215` was filed.

## What `BEN-215` said

`BEN-215`, filed by lane A earlier today:

> **An id, a date and a commit message were verified as STRINGS while the claim built on them never met the
> diff — and the repo was PUBLIC.**

The repo was `MinervaExpt/GENIEXSecExtract`. Opening it inverted three clauses of a load-bearing provenance
argument.

## What the same advisory then said, two sections later

`ADVISORY-20260813-eavail-published-conventions.md` §7.4, *"Not verified here"*:

> *"MAT-MINERvA's `CCQE3DFitFunctions.h` (**private**; the sibling advisory's reading is inherited, and its
> id/date were independently confirmed by Codex per that file)."*

**`MinervaExpt/MAT-MINERvA` is public.** Measured:

```
gh api repos/MinervaExpt/MAT-MINERvA --jq '.private, .visibility'
  false
  public
```

The one repository the advisory declared unreachable was one `gh api` call away, in the section whose whole
purpose is to bound what was not checked — written by the session that had just filed the finding about
exactly this.

## What opening it establishes

All three previously-inherited claims hold, and one is stronger than claimed.

**1. Exactly one commit, ever.** `gh api "repos/MinervaExpt/MAT-MINERvA/commits?path=calculators/CCQE3DFitFunctions.h"`
returns **one** entry: `f790cc79473202ebb7f8ccfb011d36c0f4cce329`, **2021-07-07T18:15:28Z**, Ben Messerly,
*"calculators/ initial commit."* Never edited.

**2. It still reads `135` today.** Line 38 of the current file:

```cpp
double GetEAvailableTrue() const { /* MeV */
  double recoil = 0;
  int n_parts = GetInt("mc_nFSPart");
  double mass_pion = 135;
  double mass_proton = 938.27;
```

**3. Ours is not "line-for-line" ours — it is TOKEN-IDENTICAL.** Stripping block comments, line comments and
all whitespace from both function bodies:

| | length | sha256 (first 16) |
|---|---|---|
| `MINERvA101/…/CVUniverse.h:361-374` | 424 | `5296998043add43c` |
| `MAT-MINERvA/calculators/CCQE3DFitFunctions.h:34-50` | 424 | `5296998043add43c` |

**Same hash.** Four species (γ total E, π± KE, π⁰ total E, p KE), bare `if`s rather than `else if`, no
lepton branch, no neutron branch, no clamp, `return recoil;` in MeV. The only textual differences are that
MAT writes the unit as `/* MeV */` where we write `// MeV`, and the comments read `//kinetic` where ours read
`// KE`.

## Why this matters beyond closing an unverified row

**`OI-30(b)` is promoted from inherited to measured.** Its claim — *"because MAT still reads `135`, 'exact
MAT compatibility' and 'physically correct pion mass' are in DIRECT CONFLICT and cannot both be
satisfied"* — is the reason the `135` decision is framed as a choice between two defensible goods rather
than a bug fix. That framing now rests on a fact anyone can re-run, which matters because it is the framing
Joseph is being asked to decide against.

**It sharpens `BEN-220` in a way that changes the recommended fix.** `BEN-220` recorded that
`docs/EAVAIL_DEFINITION.md` §1 says *"we implement the Rodrigues 2016 convention, deliberately and
uniformly"* where the source said *"Rodrigues 2016's closed list, **minus e±**"* — and proposed restoring
three words. **The token-identity says the sentence is wronger than that.** Our species list is not a
convention selected from the literature and then narrowed; it is **MAT's list, copied whole, from a single
2021 commit that was never edited and never reviewed**, which *happens* to coincide with Rodrigues 2016
minus e±.

So the honest §1 is not "Rodrigues 2016 minus e±". It is: **we inherited MAT's four-species list; it
coincides with Rodrigues 2016's five minus e±; the coincidence is what makes it defensible, and the
inheritance is what makes "deliberately" false.** That is a stronger position than the document currently
claims, not a weaker one — it is checkable, and the alternative invites an advisor to ask which paper we
read.

## Why the miss happened, stated mechanically

`BEN-215`'s check as filed is *"verify what a citation changed, not that it exists."* That is a check on
**citations you are using**. §7.4 is a list of things **not** used — and a not-verified list is exactly where
no check fires, because nothing there is load-bearing yet. **The reachability of a source was recorded as a
property of the source rather than measured**, and `private` is the one attribute that terminates enquiry
without producing an error.

Contributing: `Codex` had previously confirmed the id and date *"per that file"*, which reads as an
independent verification having already happened. It had — of the strings. `BEN-215` is the finding that
those are different things, and the reassurance survived the finding that should have killed it.

## The check

**Before writing "private", "unreachable" or "internal" about a repository, run one command.** For GitHub:
`gh api repos/<org>/<repo> --jq .visibility`. Zero cost, and it is the only claim in a *not-verified* list
that can be wrong in the direction of doing less work.

**And: a "not verified here" section deserves the same scepticism as a verified one.** It is written last, at
the point of least energy, and every entry in it is an assertion — usually an assertion about why something
cannot be done.

## Related

`BEN-215` (the first public repo nobody opened — this is its second instance, same session, same document),
`BEN-220` (the summary that dropped the qualifier — sharpened here), `BEN-207` (a PRESENT verdict is also a
statement about the search), `BEN-205` (reading some artifact is not reading the governing one), `OI-30(a)`,
`OI-30(b)`.
