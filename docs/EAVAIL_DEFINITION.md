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

**The table above is OI-30(c)'s 2026-08 figure.** It was measured on a 65,911-event sample whose binning that record
does not identify, so it is not a 16-cell number.

**The size on the reported result is now measured** (PR #622,
[`orchestration/ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md`](orchestration/ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md)
§7, 2026-11-01). The method:
- the switch is applied as the exact per-event shift `MC_eavail − 0.00457 × MC_npip`, on the 5D omnifile's
  completeness denominator;
- the 135 histogram is control-checked bitwise against `of_inputs_5d.npz`'s `denom_nd`;
- §7.5 shows the shift exact: 0 of 34.9M charged pions have E ≤ 139.57 MeV.

The results:

| quantity | value |
|---|---|
| largest cell move, prior level / first-order unfolded | **−1.26 % / −1.23 %** (R06), **0.21 σ** of the reported C_total + C_resp |
| the whole 16-cell shift, √(ΔᵀC⁻¹Δ) against C_total + C_resp | **0.43 / 0.42** (0.43 / 0.42 with C_PL,5D) |
| weight changing fine E_avail bin | 0.646 % |
| fine E_avail bins | +0.97 % ([0, 0.1)) to −0.35 % ([3, 100)) at prior level |
| net change of the 16-cell total | 0, to float precision |

**The unfolded column is first order.** Each event carries its fine cell's nominal unfolded-to-prior ratio, so the
step-2 retraining effect is not in it.

**The coherent norm is the better measure.** The shifts move together, so it is about 1.5× the per-cell σ's in
quadrature.

**These replace this section's earlier bracket `[7.7%, 297%]`,** which rested on a 1,507-bin assumption and was
"consistent with immaterial; not proven immaterial". The off-diagonal projection that the bracket said would close it
is the full-covariance norm above.

**On that size, Joseph kept 135** ([`orchestration/DECISION-20261101-joseph-eavail-keep-135.md`](orchestration/DECISION-20261101-joseph-eavail-keep-135.md);
UD-002 stands).

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

**The constant lives at SEVEN sites,** listed in PR #622 §1 at `c7c3ab21`:
1. `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:364`, the event loop's `GetEAvailableTrue()`;
2. `3d-unfolding/genie/genie_to_xsec3d.py:42` (`MASS_PI_PM`). `gen_to_xsec5d.py`, `gen_to_xsec_eavailW.py`,
   `genie_mec_to_xsec3d.py`, `fsi_variation_xsec3d.py` and `mode_decomp_eavail.py` import it;
3. `3d-unfolding/genie/nuwro_to_flat_5d.C:44`;
4. `3d-unfolding/genie/nuwro_to_flat.C:31`;
5. `3d-unfolding/genie/gibuu_to_xsec3d.py:53`;
6. `3d-unfolding/genie/gibuu_to_xsec_eavailW.py:38`;
7. `nd-unfolding/pet/pointcloud_projection.py:51` (`M_PION_EAVAIL = 135.0`), in the PET path.

**Two corrections to the earlier version of this list:**
- **The count.** It counted "four generator converters" and six sites. NuWro has two flatteners, sites 3 and 4.
- **The binding.** It said two converters bind to `CVUniverse` by comment. Three do: sites 2–4 say "match CVUniverse".
  The two GiBUU readers, sites 5 and 6, carry a bare `0.135` with no reference, which is the weaker coupling and the
  likelier silent desync (session A).

**Any future change must move all seven in one commit,** or the generator comparison silently compares two different
observables. With 135 kept, none is changed and nothing quoted moves.

**A hazard in site 7 specifically, which repairing it would create:** `pointcloud_projection.py`
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
3. **Not** that the `135` constant is immaterial in general. Its measured size on the 16 reported cells is at most
   0.21 σ per cell and 0.42 σ as one coherent shift, to first order (§3; PR #622 §7). That size is stated, not
   rounded to zero.
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
zero-η/K⁰_S census. §3's measured size comes from the scripts and outputs under
`orchestration/state/eavail-switch-pricing-20261031/step0/`. Operands are in `OI-30`, `OI-56`, `OI-59` and
`evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/ADVISORY-20260813-eavail-published-conventions.md`.

**Relayed from lane A and NOT independently verified by the author of this document:** the
`GENIEXSecExtract` commit archaeology — the 8-commit history of `src/XSec.cxx`, the 3m07s gap between
`0e6740cec071` and `564e2788051f`, and the finding that the latter lands in `case kPZRecoil:` rather
than `kEAvail`. Two commands check it against a public repo and no credentials beyond `gh`:

```
gh api "repos/MinervaExpt/GENIEXSecExtract/commits?path=src/XSec.cxx"
gh api repos/MinervaExpt/GENIEXSecExtract/commits/564e2788051f
```

**Index:** `OI-30` (the `135` constant; UD-002, kept by `DECISION-20261101-joseph-eavail-keep-135.md`), `OI-56`
(the convention difference, FROZEN), `OI-59` (the
cross-check caveat), `OI-63` (advisor items, deferred), `docs/PUBLICATION_COMPLETION_RUNBOOK.md` §P7.
