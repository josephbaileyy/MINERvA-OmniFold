# ADVISORY 2026-08-13 — the PUBLISHED E_avail conventions, read directly; and what that does to OI-30 / OI-56

**Status: ADVISORY. Nothing adopted, no production definition changed, no launcher submitted.**
Lane A (E_avail), reassigned to the Gregor thread this session. Instruments are named per claim; every
external fact below was fetched in this session rather than inherited.

**The commissioning question**, relayed from Joseph via `personal-orchestrator`: *"what value of m(π±) did
Ascencio 2022 and Rodrigues 2016 use? That is the only path by which `135` becomes a real compatibility
constraint rather than an inherited typo."*

**Answer: neither paper states a numerical pion mass, and the code path that could have supplied one did
not exist when Ascencio v1 was submitted. `135` is not a compatibility constraint with either paper on any
evidence reachable from outside MINERvA.** That closes the question in the *typo* direction. Three larger
things turned up on the way and they are the reason this file exists.

---

## 0. Summary of what changed

| | before this session | measured now |
|---|---|---|
| `135` vs published comparators | unknown; possible compatibility constraint | **no constraint** — no numeric mass in either paper; `kEAvail` never held `135` |
| the `564e2788051f` provenance argument | "a second implementation of the same quantity, fixed four months later" | **three minutes later, same author, a DIFFERENT quantity** — §2 |
| "the MINERvA reference rule" | one stable convention (`2312.16631` Eq. 4 ≡ `kEAvail`) | **a νe artifact from 2022-03-07, post-dating Ascencio v1 by four months** — §3 |
| Rodrigues 2016 vs Ascencio 2022 | treated as one lineage | **they disagree with each other**; ours implements the 2016 list — §4 |
| e± ("we are RIGHT, minerva-ml is wrong") | our exclusion correct | **inverted for a νμ analysis** — Rodrigues 2016 includes electron total energy — §5 |
| Ascencio cross-check `ours/theirs = 1.092` | PASS, three caveats | **a fourth caveat is missing and it is the definitional one** — §6 |

**§6 is the item with publication consequences. Everything else is documentation-grade.**

---

## 1. The two papers, quoted verbatim

Both fetched from `ar5iv.labs.arxiv.org` and extracted by **deterministic tag-strip + regex**, not by a
summarising model — the first pass on Ascencio was a model read, and §7 records why that mattered.

### Rodrigues 2016 (arXiv:1511.05944, PRL 116 071802) — a CLOSED list

> *"we define the closely related observable, the hadronic energy available to produce activity in the
> detector E_avail, as the sum of proton and charged pion kinetic energy, plus **neutral pion, electron,
> and photon total energy**, and report d²σ/dE_avail dq₃."*

**The strings `strange` and `kaon` appear ZERO times in the entire paper.** Five species, enumerated,
closed. Its only `25 MeV` is removal energy inside the 2p2h hadron-kinematics model — a different object,
not an E_avail term.

### Ascencio 2022 (arXiv:2110.13372, PRD 106 032001) — an OPEN list

Eq. (1), with the sentence that immediately follows it:

> *"E_avail = Σ T_proton + Σ T_π± + Σ E_particle … where T_proton is the proton kinetic energy, and T_π is
> the charged pion kinetic energy, and E_particle is the total energy of any other final state particles
> **except neutrons**. **The definition excludes a nucleon mass from strange baryons.**"*

**Neither paper states a numerical mass for anything.** The `135`/`139.57` question is not answerable from
the literature, exactly as the commissioning message allowed. It is a *code* question, and §2–§3 answer it
from the code.

---

## 2. THE `564e2788051f` ARGUMENT IS INVERTED BY THREE MINUTES, and it is load-bearing in `OI-30(a)`

`docs/orchestration/ADVISORY-20260813-oi30-eavail-residuals.md` §1 — echoed into the `OI-30` row and
described there as `PROVENANCE SETTLED` — says:

> *"The same organisation **fixed the identical constant in its other implementation of the same
> quantity**… a different MINERvA developer, in a different MINERvA repository implementing the same
> quantity, called `135` a neutral-pion-mass mistake and fixed it **four months later**."*

**`MinervaExpt/GENIEXSecExtract` is PUBLIC on GitHub.** Nobody had opened it; the id, date and message were
relayed and verified as *strings*, and the surrounding claim was never checked against the diff. Measured
here with `gh api` (`repos/MinervaExpt/GENIEXSecExtract`), **only 8 commits in history have ever touched
`src/XSec.cxx`**:

| commit | UTC | author | what it did to `src/XSec.cxx` |
|---|---|---|---|
| `03ebef5fd197` | 2021-07-28T15:51:11Z | Andrew Olivier | *"Imported GENIEXSecExtract from the MINERvA 101 tutorial"* — brings in `case kPZRecoil:`, a **(recoil, pt, pz) hyperdim bin-number lookup** whose recoil coordinate uses `mass_pion = 135` |
| `0e6740cec071` | **2021-11-26T10:14:03Z** | abbeywaldron | **creates `case kEAvail:`, already with `mass_pion = 139.57`** (+21/−0) |
| `564e2788051f` | **2021-11-26T10:17:10Z** | abbeywaldron | **+1/−1**: `135` → `139.57`, *"Bugfix: this should be the charged pion mass not the neutral pion mass I think"* |
| `2f0097bde564` | 2022-03-07T22:15:44Z | Hang Su | **"adding NuE low recoil"** — adds the strange-baryon / antibaryon / kaon-eta branches (+12/−2) |
| `3238bc435c83` | 2022-03-07T22:27:00Z | Hang Su | *"forgot ;"* |
| `30a4edf2b65a` | 2022-03-07T23:46:29Z | Hang Su | *"Corrected EAvail"* — leading `if`s → `else if`; adds charged-lepton skip |
| `23ff7c0ac438` | 2022-03-08T15:51:41Z | Hang Su | *"EAvail fix again"* — adds neutron skip and **`max(0.0, …)` clamp** |
| `374082adf7b1` | 2023-04-06T09:43:12Z | Abigail Waldron | low-recoil q3 variant |

**Every clause of the quoted argument is wrong, and all three errors run toward MORE apparent independence:**

1. **"four months later" → three minutes and seven seconds later.** `10:14:03Z` → `10:17:10Z`, same author,
   same sitting. "Four months" came from differencing against MAT's 2021-07-07 commit **in a different
   repository**, which is not the thing `564e2788051f` changed.
2. **"its other implementation of the same quantity" → a different quantity.** The fix is +1/−1 and the
   diff's indentation locates it: `564e2788051f` removes `\t\tdouble mass_pion = 135;` (two tabs), while
   `kEAvail`'s declaration is `\t    double mass_pion = 139.57;` (one tab, four spaces). Confirmed by
   reading the blobs at both refs — the file holds **two** `mass_pion` declarations, and the one that was
   fixed is inside **`case kPZRecoil:`**, a hyperdim bin-number lookup. **`case kEAvail:` never contained
   `135` for one second of its existence.**
3. **The independence the argument rests on does not exist.** This is not two implementations converging on
   a correction. It is one person, having just written `139.57` in a new function, noticing the
   pre-existing site next door disagreed and changing it — hedged, *"I think"*, and never reviewed.

**THE CONCLUSION SURVIVES AND ITS REAL BASIS IS BETTER.** `abbeywaldron`, writing a MINERvA low-recoil
E_avail from scratch in November 2021, **chose `139.57` unprompted on the first try**, then went back and
labelled the inherited `135` a bug. That is genuine evidence about what MINERvA's low-recoil closure-test
author believed correct. What must go is the *"two independent implementations"* framing — and it must go
before this reaches Gregor, because it is the kind of claim an advisor checks.

**And the `135`s are not independent either.** The only `135` that ever existed in public GENIEXSecExtract
arrived in the 2021-07-28 import *"from the MINERvA 101 tutorial"* — **the same ancestor as our own
`CVUniverse.h:364`**, which sits in `MINERvA101/MINERvA-101-Cross-Section/`. Ours and theirs are one
inherited copy, not two choices. This strengthens `OI-30(a)`'s π⁰-reuse verdict while removing its
corroboration.

---

## 3. "The MINERvA reference implementation" IS A νe ARTIFACT, AND IT POST-DATES ASCENCIO v1

`OI-56` measures our four-species mismatch against `GENIEXSecExtract`'s `case kEAvail:`. The dates matter
and were never put side by side:

| event | UTC |
|---|---|
| **Ascencio v1 submitted** | **2021-10-26T03:01:17Z** |
| `kEAvail` first exists at all | 2021-11-26T10:14:03Z — **a month later**, four species only |
| kaons / strange baryons / antibaryons added | **2022-03-07T22:15:44Z**, commit titled *"adding NuE low recoil"* |
| neutron skip + `max(0,·)` clamp added | 2022-03-08T15:51:41Z |
| **Ascencio v2 submitted** | **2022-07-25T11:46:21Z** |

**So `kEAvail` cannot have produced Ascencio v1's numbers — it did not exist — and its species-complete
form is four months younger than that submission.** Whether v2's numbers were regenerated against it is
not knowable from outside; nothing here claims they were.

**The species extension was written for a νe analysis by an author of the paper our code cites.**
`2f0097bde564` is titled *"adding NuE low recoil"* and its other file is `apps/runCCIncForNuEMEC.cpp`
(+342/−0). Hang Su is an author of **arXiv:2312.16631**, the e-ν / e-ν̄ low-recoil paper that
`CVUniverse.h:163` names as the authority for `GetEAvailableTrue()`. So the chain is closed: our cited
authority and the reference implementation are the same νe analysis, one person, one week in March 2022.

**One consequence for how solid that reference is.** As committed at `2f0097bde564` the four leading
species tests were left as bare `if`s while the new block was an `if/else if/…/else` chain, so the trailing
`else` fired for photons, π±, π⁰ and protons as well — **every already-handled species was counted twice**,
and the commit did not compile (`forgot ;`, +12 min). Fixed 1 h 31 m later by *"Corrected EAvail"*.
Recorded not as a jab but because `OI-56` treats this code as a stable reference convention: it was under
active, error-prone construction in March 2022, and its species list has never been reviewed by anyone but
its author.

---

## 4. RODRIGUES 2016 AND ASCENCIO 2022 DISAGREE, AND WE IMPLEMENT THE 2016 CONVENTION

This is the finding that most changes how `OI-56` should be presented.

| species | Rodrigues 2016 (νμ) | Ascencio 2022 (νμ) | `kEAvail` today | **ours** `GetEAvailableTrue()` | `minerva-ml` |
|---|---|---|---|---|---|
| p | KE | KE | KE (−938.27) | KE (−938.27) | KE |
| π± | KE | KE | KE (−139.57) | **KE (−135)** | total E |
| π⁰ | total E | total E | total E | total E | total E |
| γ | total E | total E | total E | total E | total E |
| **e±** | **total E** | total E (open list) | **excluded** | **excluded** | total E |
| **K±** | **absent from paper** | included, total E | total E | **excluded** | total E |
| **K⁰, η** | **absent from paper** | included, total E | total E | **excluded** | excluded |
| **Λ, Σ** | **absent from paper** | E − m_nucleon | E − 938.27 | **excluded** | excluded |
| **p̄** | **absent from paper** | E **+** m_nucleon | E **+** 938.27 | **excluded** | E − m (wrong sign) |
| n | excluded | excluded | excluded | excluded | excluded |
| negative total | — | — | **clamped `max(0,·)`** | **not clamped** | clamped |

**`OI-56`'s framing — "our rule disagrees with MINERvA's own reference implementation on four species" — is
true and incomplete in a way that matters.** We are not simply wrong against a settled convention. We
implement **Rodrigues 2016's closed list**, which is the paper that introduced the observable, minus e±.
The open list is a **2022** development, stated in Ascencio v1's prose and realised in code four months
after it.

**Presented to Gregor, "we implement the 2016 convention and not the 2022 one" is a defensible position
that needs a decision. "We are wrong on four species" is not the same claim and is the one currently in
the ledger.**

**A fifth mismatch `OI-56` does not enumerate: the clamp.** The reference returns `max(0.0, …)`;
`minerva-ml` clamps; **we do not.** Untested here — our π± mass being `135` rather than `139.57` makes a
negative truth sum *less* likely for pions, but the proton term can still go negative and the advisory's §7
already carries *"whether the minimum π± energy in the tuple is ≥ 139.57"* as open. Recorded as
un-enumerated, not as quantified.

---

## 5. THE e± VERDICT IS INVERTED FOR A νμ ANALYSIS

`ADVISORY-…-oi30-eavail-residuals.md` §3 and the `OI-56` row both state: **"On e± we are RIGHT and
minerva-ml is wrong."** That was measured against `kEAvail`, and against `kEAvail` it is correct.

**Against Rodrigues 2016 it is backwards.** That paper's definition says *"plus neutral pion, **electron**,
and photon total energy"* — electrons in, at total energy. So on e± **`minerva-ml` matches the paper that
introduced the observable, and we do not.**

**The mechanism, and it is why the reference disagrees with the paper.** `kEAvail`'s exclusion is
`abs(pdg)==11 || abs(pdg)==13` — *"do nothing. don't count charged lepton"* — added by Hang Su on
2022-03-07/08, in the same three commits as `apps/runCCIncForNuEMEC.cpp`. **In a νe analysis the primary
electron IS the charged lepton and MUST be excluded.** Applied to a νμ analysis the same branch also drops
every *secondary* e±, which Rodrigues 2016 explicitly includes.

**Stated at its real strength: the temporal association is measured, the motive is inferred.** The
lepton-skip branch and the νe executable land in the same commit window from the same author; I have not
found a statement that the branch exists *for* the νe case. The claim to carry forward is that **our
exclusion follows the νe-era code and not the νμ paper**, and that "we are RIGHT" needs its comparator
named.

Size: the census in the sibling advisory puts e± at **1.462 MeV/signal event** (e⁻ 0.239 + e⁺ 1.223) —
smaller than the pion-mass constant. **It is the direction of correctness that has flipped, not a large
number.**

---

## 6. THE ITEM WITH PUBLICATION CONSEQUENCES: the Ascencio cross-check is missing its definitional caveat

`VALIDATION_LEDGER.md:1293-1304` records:

> **Ascencio bin-identical cross-check (2026-06-10): PASS (consistent)** … `ours/Ascencio = 1.092` and
> `1.063` (pulls 1.29σ, 0.86σ); full-cov χ²/ndf = **1.68/2, p = 0.432**

with three caveats: shared MINERvA systematics treated as independent, the pμ-vs-pz gate at 20 GeV, and
differing fiducial nucleon counts. **None of them is that the two sides' E_avail truth axes are defined
differently** — and `OI-56`'s own measurements say they are.

**Why this is an axis question and not a model question.** Unfolding targets a *truth-level* definition.
Ascencio unfolds to Eq. (1)'s open list; we unfold to `GetEAvailableTrue()`'s closed list with
`mass_pion = 135`. The comparison is data-to-data on their published supplemental table, so no simulation
enters — but the two data cross sections are differential in **two different observables that share a name**.

**The sign and location line up with the residual, which is why this needs closing rather than noting.**
Both maximal common super-cells are the low-E_avail ones — `E_avail < 0.4` GeV in q3 `[0.4,0.6)` and
`[0.6,1.2)` — and `OI-56` measures adopting the reference rule as **−10.99% out of truth bin 1**, i.e. our
present definition holds ~12% *more* population at low E_avail than the reference-like rule Ascencio uses.
Observed: **ours/theirs = 1.092 and 1.063, both above one, in exactly those cells.**

**WHAT THIS IS AND IS NOT.** It is an **unexcluded alternative explanation** for a residual currently read
as statistical agreement. It is **not** a demonstration that the check fails:

- `−10.99%` is a truth-**population** migration, not a cross-section ratio, and the two are related only
  through the unfolding.
- Their super-cells span `E_avail < 0.4` GeV — our bins 1+2+3 — and the per-bin migration is published
  only for bins 1 and 7 (`−10.99%`, `+12.81%`). The 1–3 aggregate is **not** measured anywhere and the
  cancellation inside it could be large.
- `p = 0.432` on 2 degrees of freedom cannot distinguish a ~10% definitional offset from noise either way.

**The closing computation, specified so it can be handed off:** recompute the truth-population migration
under the reference rule **on the Ascencio super-grid** — q3 `[0.4,0.6)` and `[0.6,1.2)`, `E_avail < 0.4`
GeV aggregated, their muon gate — and compare against `1.092` / `1.063`. `OI-56` records that lane `dc`
already has the route: raw PDG in `part_gen[:,:,4]` of `G2_FPS_MEFHC_P12.npz`, ~20 min of login-node I/O,
binning fidelity 0.1286%, no ROOT and no rerun.

**NOT RUN HERE, deliberately.** `OI-56` is **FROZEN** pending Joseph's reco-underflow repair decision, and
this is `OI-56`'s arithmetic pointed at a published cross-check. Running it would action a frozen item and
put a number against a ledger `PASS` in the same turn. **Routed, with the caveat added to the ledger entry
so the `PASS` is not read as unqualified in the meantime.**

**A related model-side fact, recorded at its true (small) weight.** Ascencio's adopted baseline is
**MnvTune-v3**, which per §IV.4 includes *"the deduction of 25 MeV removal energy from a subset of
resonance reactions"* — any CC-resonance event with ≥1 proton has 25 MeV deducted from E_avail, applied to
**both** the true generator quantity and the reconstructed one. That is 5× the pion-mass constant this
whole thread is about, and `MnvTune-v3` appears **nowhere** in this repo (only `MnvTune-v1`/`v1.2`, 15
sites). **It does not bias the data-to-data comparison** — it is a property of their simulation, hence of
their smearing matrix and efficiency, i.e. a residual model dependence in their published values rather
than an offset in ours. It matters if we ever overlay their prediction curve or reproduce their tune.
Recorded because it was invisible and I nearly reported it as a definitional offset; §7.

---

## 7. Instrument notes, kept because two of them nearly produced wrong entries above

1. **A summarising fetch and a deterministic grep disagreed about Ascencio Eq. (1)'s surroundings.** The
   first `WebFetch` reported the strange-baryon sentence; a second, asked for the paragraph verbatim,
   returned the paragraph **without** it. Neither was wrong — the sentence is the next one — but the pair
   is unresolvable without a third instrument. Settled by `curl` + tag-strip + regex, which found it
   adjacent and verbatim. **A model-summarised quotation of a load-bearing sentence needs a deterministic
   confirmation, and the disagreement is the only warning you get.**
2. **I nearly wrote that Ascencio's E_avail definition includes a −25 MeV resonance shift.** The paragraph
   sits in §IV among *candidate* model variations; only §IV.4 establishes it is in the adopted MnvTune-v3,
   and only the same section establishes it is a simulation property rather than a definitional term.
   Reading one paragraph further changed the claim twice. This is `BEN-206`'s shape and it is why §6's
   last paragraph is scoped down rather than headlined.
3. **Two `head -60` truncations of `gh api` patch output** while establishing §2/§3 — `CLAUDE.md` forbids
   truncating a diagnostic at write time. Both were redone to files. The second truncation is what briefly
   hid that `pdg>1000000000` pre-dated `30a4edf2b65a`, which is the fact that sent me to
   `2f0097bde564` and hence to §3's whole result. **The rule earned its keep in the same turn it was
   broken.**
4. **Not verified here:** MAT-MINERvA's `CCQE3DFitFunctions.h` (private; the sibling advisory's reading is
   inherited, and its id/date were independently confirmed by Codex per that file). Ascencio v2's actual
   E_avail code path. Whether the Ascencio supplemental table's own axis was regenerated between v1 and v2.

   > **`MAT-MINERvA` IS NOT PRIVATE, AND THIS ENTRY IS SUPERSEDED — 2026-08-13, lane A, `BEN-221`.**
   > `gh api repos/MinervaExpt/MAT-MINERvA --jq '.private, .visibility'` → **`false`, `public`**. The one
   > source this advisory declared unreachable was one call away — **in the section that exists to bound what
   > was not checked, written by the session that had just filed `BEN-215` (*"the repo was PUBLIC and nobody
   > had opened it"*) about the other repository in the same paragraph.**
   >
   > Opened, and all three inherited claims hold with one stronger than claimed: **exactly one commit ever**
   > (`f790cc79473202ebb7f8ccfb011d36c0f4cce329`, 2021-07-07T18:15:28Z, Ben Messerly, *"calculators/ initial
   > commit."*), it **still reads `double mass_pion = 135;`** at line 38, and our `GetEAvailableTrue()` is
   > not merely "line-for-line" ours but **token-identical**: stripping comments and whitespace from both
   > function bodies gives 424 characters and sha256 `5296998043add43c…` on **both** sides.
   >
   > **Two consequences.** `OI-30(b)`'s MAT-compatibility conflict — the reason the `135` decision is framed
   > as a choice between two defensible goods — is **promoted from inherited to measured**. And §4's reading
   > of our list as *"Rodrigues 2016's closed list minus e±"* is **provenance-inverted**: the list is
   > **MAT's, copied whole**, from one unreviewed 2021 commit, and it *coincides* with Rodrigues minus e±.
   > The coincidence is what makes it defensible; the inheritance is what makes any claim of deliberateness
   > false. See `FINDING-20260813-the-second-repo-was-public-too.md`.
   >
   > Ascencio v2's code path and the supplemental-table axis question remain genuinely unchecked.

---

## Recommended disposition (lane A) — none of this is adopted

1. **Correct the `564e2788051f` framing before anything goes to Gregor** (§2). The conclusion holds on a
   better basis; the "two independent implementations" clause does not.
2. **Reframe `OI-56` as 2016-vs-2022 rather than us-vs-correct** (§4), and add the clamp as a fifth
   mismatch.
3. **Name the comparator on the e± verdict** (§5), which is inverted against Rodrigues 2016.
4. **Add the definitional caveat to the Ascencio ledger entry, and route the closing computation** (§6).
   This is the only item here that touches a published number, and it stays frozen until Joseph decides.
5. **Drop `135`-as-compatibility-constraint.** The literature has no numeric mass and the code timeline
   excludes it. What remains is MAT compatibility, which the sibling advisory already frames correctly as
   a choice between two defensible goods.
