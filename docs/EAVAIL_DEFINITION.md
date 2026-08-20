# Which E_avail definition this analysis uses, and why

**Purpose.** One place that answers *"which available-energy definition do you use?"* — a question this
repo could previously answer only by assembling `OI-30`, `OI-56` and `OI-59`. Written 2026-08-13 at
Joseph's instruction after the question was raised with Gregor Kafka.

**Status: reference, not a decision.** Nothing here adopts, changes, or unfreezes anything. `OI-56`
remains **FROZEN** — its freeze rests on the reco-underflow repair choice being Joseph's, and is
untouched by anything in this document. The analysis note absorbs this at **Packet P7**; per `OI-40`
the note is not edited before the full-event PET and adopted UQ products are quotable.

---

## 1. The position, in one paragraph

**What we implement is MAT-MINERvA's species list, copied whole — and it COINCIDES with Rodrigues 2016
(arXiv:1511.05944) minus e±.** Available energy is the summed kinetic energy of protons and charged
pions plus the summed total energy of neutral pions. **Rodrigues' closed list is five species — p, π±,
π⁰, e, γ — and we implement four of them.**

**The provenance and the defence are two different things, and conflating them is the error this
paragraph previously made.** Our list is **inherited, not chosen**: comments and whitespace stripped,
our function body is **token-identical to MAT-MINERvA's `calculators/CCQE3DFitFunctions.h`** — both 424
chars, sha256 prefix `5296998043add43c` (**16 of 64 hex — a prefix, not a full digest**; our side
independently reproduced by session D on its first normalisation attempt, the MAT side **not** verified
by anyone with access, so this is one operand of a two-operand identity) — from a file that has
**exactly one commit in its history**
(`f790cc794732`, 2021-07-07, Ben Messerly, *"calculators/ initial commit."*), never edited since. The
e± exclusion likewise follows `kEAvail`'s `abs(pdg)==11||13` "don't count the charged lepton" branch,
written for a νe analysis in which the primary electron **is** the charged lepton.

**So: the coincidence with a published convention is what makes the position defensible; the inheritance
is what makes "deliberate" false.** This document claims the first and not the second. We do not claim
to implement "the
published definition of E_avail," because **there is no single published definition** — Rodrigues 2016
and Ascencio 2022 (arXiv:2110.13372) differ from each other, and the difference is measurable in our
sample. Any statement that this analysis "matches the published E_avail definition" without naming a
paper is a claim we cannot support and should not be made.

The charged-pion half of the convention is **settled and matches the νe reference**: arXiv:2312.16631
Eq. 4 reads `E_avail = Σ_p T_p + Σ_π± T_π± + Σ_π0 E_π0` — kinetic for protons and charged pions, total
for π⁰. Ours agrees. (`minerva-ml` uses total energy for charged pions, which adds ~140 MeV/pion; that
is a defect in that code, not in ours. **The same comparison runs the other way on e±, where
`minerva-ml` matches the νμ paper and we do not** — see §2 and §5(6). Both halves are stated here so
neither is read alone.)

---

## 2. Where the two published conventions differ

| | Rodrigues 2016 (`1511.05944`) | Ascencio 2022 (`2110.13372`) |
|---|---|---|
| species list | **CLOSED** — five species | **OPEN** — "any other final state particles except neutrons" |
| `strange`, `kaon` in text | appear **zero times** | covered by the open clause |
| what we do | **coincide with it on 4 of its 5 species** (inherited from MAT, not selected — §1) | do not implement |

**FIVE species separate us from the open convention.** Four of them are the ones below. **The fifth is
e±**, which the open list also includes and which we also exclude — so any count of "four" here is a
count against *Rodrigues*, not against Ascencio. The measured figures immediately following are the
`kEAvail` comparison, and `kEAvail` includes e±:

- **K±** — included at total energy
- **p̄** — `E + m_p` (for antibaryons the nucleon mass is **added**, not subtracted)
- **strange baryons Λ, Σ** — `E − m_p`
- **neutral kaons K⁰, K⁰_L, K⁰_S and η** — included at total energy

**Measured effect of moving to the open convention, on our sample:**

| quantity | value |
|---|---|
| mean shift | **+212.18 MeV/event** |
| events changing truth bin | **4.837%** |
| migration out of truth bin 1 | **−10.99%** |
| offline reproduction fidelity | 0.1286% of weight misplaced vs. the exact C++ `MC_eavail` |

The fidelity figure is **37.6× smaller than the effect it measures** (`4.837 / 0.1286`), which is what
makes the comparison sound. (`OI-56` rounds this to "37×"; both are the same operands.) It is computed from `part_gen[:,:,4]` of `G2_FPS_MEFHC_P12.npz` (49,152,885 rows) — raw PDG
codes, no ROOT and no event-loop rerun.

**One clause is inert on this sample rather than unresolved.** Eq. 4's "strange, *or heavier quark*"
extension: η (221), η′ (331) and K⁰_S (310) are **zero across all 49.15M rows** — GENIE emits 311/130 —
and there are no charm baryons. So the extension has nothing to act on here.

**The e± case cuts against us and is stated for that reason.** Rodrigues includes electron total
energy. We exclude it. On this one species `minerva-ml` matches the νμ paper and **we do not**.

---

## 3. The `135` vs `139.57` MeV charged-pion mass

A separate and much smaller issue, and **documentation-grade rather than physics-grade**.

`CVUniverse.h:364` uses `mass_pion = 135` MeV — the **π⁰** mass — where the charged-pion mass 139.57
MeV is meant. The difference is **4.57 MeV per charged pion**.

| quantity | value |
|---|---|
| charged pions per signal event | 1.0563 |
| mean shift | **4.827 MeV/event** |
| events changing truth bin | **439 / 65,911 = 0.666%** |
| worst single bin | **+1.049%**, in bin 1 |

**Materiality against the adopted covariance** (13.69% median per-bin, `VALIDATION_LEDGER.md` — **cite
it by the string `adopted median per-bin fraction **13.69%**`, not by line number**: it was at `:1043`
when first cited at 02:34Z and at `:1116` by 17:53Z the same day, because Gate 5 appended 73 lines above
it, and `:1043` now lands inside a heading reading *"CANDIDATE; final lateral replacement pending"* —
a citation labelled "adopted" resolving into a candidate entry, `BEN-219`) is
**bracketed `[7.7%, 297%]`**. Both ends re-derive from the same two operands: `1.049 / 13.69 = 7.66%`,
and `7.66% × √1507 = 297%` for the ~1507 5D bins per E_avail slice. **The upper end IS the lower times
√1507** — it is one assumption varied, not two independently asserted endpoints. That is a bracket, not
a result:

> **The `7.7%` end assumes the ~1507 5D bins per E_avail slice are perfectly correlated. It is the most
> favourable reading available, not the answer.** The honest label is **consistent with immaterial; not
> proven immaterial.**

The single step that would close it is projecting the adopted covariance onto the E_avail marginal
**retaining off-diagonals**, and comparing +1.049% against that. It has not been done. It requires no
rerun.

**`135` is NOT a compatibility constraint with either comparator.** Neither Rodrigues 2016 nor
Ascencio 2022 states any numeric mass, and `kEAvail` did not exist until a month after Ascencio v1. The
`135` traces to a 2021-07-28 import "from the MINERvA 101 tutorial" — **the same ancestor as our own
line**. It is one inherited copy in two places, not two independent choices. **Tense matters here:
public `GENIEXSecExtract` holds no `135` today** — both `mass_pion` declarations read `139.57`, and the
only `0.135` is a correctly-named `Mpi0`. Ours is the copy that still carries it.

**The positive evidence that `135` is wrong, stated at its actual strength.** Writing a MINERvA
low-recoil E_avail from scratch, `abbeywaldron` chose `139.57` unprompted and first try, then went back
and labelled an inherited `135` elsewhere a bug — *"this should be the charged pion mass not the neutral
pion mass I think."* That is the whole of the affirmative case: **single author, hedged, never
reviewed.** It is real evidence and it is weak evidence, and it should be quoted with the hedge intact
rather than paraphrased into confidence.

**Correcting it is a SIX-site change or nothing:** `CVUniverse.h:364`, four generator converters, **and
`nd-unfolding/pet/pointcloud_projection.py:51`** (`M_PION_EAVAIL = 135.0`) — the sixth is in the **live
PET path** and was missing from every earlier statement of this list, including two rewrites of this
document (session D, `BEN-177`). They must move in one commit, or the four-generator comparison silently
compares two different observables. **Two of the four converters bind by comment; the other two carry a
bare `0.135` with no reference to `CVUniverse` at all** — the weaker coupling, hence the likelier silent
desync (session A). Not applied; nothing quoted moves.

**A hazard in the sixth site specifically, which repairing it creates:** `pointcloud_projection.py`
holds `M_PION_EAVAIL = 135.0` and `M_PI = 139.57` four lines apart, deliberately separated. **Setting
the convention constant to `139.57` makes them identical and the separation invisible**, so a later
reader cannot tell the two were ever distinct quantities. Rename or comment at the same time.

---

## 4. The Ascencio cross-check carries a caveat it did not previously carry (`OI-59`)

The bin-identical cross-check against Ascencio **passed** (`p = 0.432` on 2 dof) and shipped three
caveats. It did not ship the definitional one: **the two sides' E_avail truth axes differ**, by exactly
the amount in §2.

Both maximal common super-cells are the low-E_avail ones. `OI-56` measures **−10.99% out of truth bin
1**. Ours/theirs is above one in exactly those cells — **1.092 and 1.063**. **Sign and location match.**

**This is an unexcluded alternative explanation, not a refutation**, and the symmetry matters in both
directions:

- the migration is a *truth-population* effect, and their cells span our bins 1+2+3 whose aggregate is
  measured nowhere;
- `p = 0.432` on 2 dof **separates nothing at the ~10% scale in play here** (the advisory's scope, which
  earlier drafts of this line dropped) — so the cross-check neither refutes us **nor validates us
  as strongly as its PASS implies**.

Computing this further is `OI-56`'s arithmetic pointed at a published PASS, and `OI-56` is frozen. That
is Joseph's decision, not a lane's.

---

## 5. What this analysis does NOT claim

Stated explicitly, because this is the section the rest of the document exists to support.

1. **Not** that our E_avail matches "the published definition." There is no single published
   definition.
2. **Not** that the Rodrigues/Ascencio difference is immaterial. It is `+212.18 MeV/event` and `4.837%`
   of events change truth bin. **Nor that it was chosen** — see item 6. It is a position we can now
   *declare and defend*, arrived at by inheritance; "declared" describes what this document does with
   it, never how it came about.
3. **Not** that the `135` constant is proven immaterial. `[7.7%, 297%]`, most-favourable end quoted
   first, projection not done.
4. **Not** that we match a neutral "reference implementation." `GENIEXSecExtract`'s `kEAvail`
   kaon/strange-baryon/antibaryon branches were added 2022-03-07 in a commit titled *"adding NuE low
   recoil"*, by an author of arXiv:2312.16631 — **the same paper `CVUniverse.h:163` cites as our
   authority.** Our cited authority and our putative independent reference are one analysis.
5. **Not** that the Ascencio cross-check independently validates our E_avail axis. See §4.
6. **Not** that we implement any published convention *completely*. **We exclude e±, and e± is the one
   species on which we differ from BOTH published conventions** — Rodrigues' closed list includes
   electrons, and Ascencio's open list covers them too. On this species `minerva-ml` matches the νμ
   paper and **we do not**. The exclusion is **inherited** from a νe-analysis charged-lepton branch, not
   established as a choice. This item exists because §5 is the list a reader trusts as *complete*: an
   against-us finding present in §2 but absent here is worse than one stated nowhere.

---

## Provenance of the statements here

**Measured in this repo and re-derivable:** every number in §2 and §3, the `OI-59` ratios, and the
zero-η/K⁰_S census. Operands are in `OI-30`, `OI-56`, `OI-59` and
`evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/ADVISORY-20260813-eavail-published-conventions.md`.

**Relayed from lane A and NOT independently verified by the author of this document:** the
`GENIEXSecExtract` commit archaeology — the 8-commit history of `src/XSec.cxx`, the 3m07s gap between
`0e6740cec071` and `564e2788051f`, and the finding that the latter lands in `case kPZRecoil:` rather
than `kEAvail`. Two commands check it against a public repo and no credentials beyond `gh`:

```
gh api "repos/MinervaExpt/GENIEXSecExtract/commits?path=src/XSec.cxx"
gh api repos/MinervaExpt/GENIEXSecExtract/commits/564e2788051f
```

**Index:** `OI-30` (the `135` constant), `OI-56` (the convention difference, FROZEN), `OI-59` (the
cross-check caveat), `OI-63` (advisor items, deferred), `docs/PUBLICATION_COMPLETION_RUNBOOK.md` §P7.
