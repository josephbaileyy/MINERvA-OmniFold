# ADVISORY 2026-08-13 — OI-30's two E_available residuals, investigated

**Status: ADVISORY. Nothing here is adopted, and no production definition was changed.** Commissioned
by Joseph via the Codex bridge (*"add the 4.57 MeV per pion discrepency to the list of things to do and
the K+- e+- and bar p handling as well… coordinate another session to deal with that in parallel"*),
executed by a fresh read-only lane launched by Session A, landed here by Session A.

**Why this file exists at all:** the result would otherwise have lived only in a subagent transcript.
Tonight has already produced two instances of a correct answer that reached a peer or a message and not
the record (`BEN-139`'s shape, and OI-55 sitting four hours in a chat log). This is the same failure
declined a third time.

## Provenance and its limits — read before using any number

| | |
|---|---|
| Lane | read-only `Explore` subagent (no Edit/Write/NotebookEdit by construction), Session A |
| Tree | local `a46203f` |
| Physics instrument | `omnifold_py310` + **uproot 5.6.9** on the cluster — NOT ROOT, and not the production analysis code |
| Data | ONE file: `…/MC/StandardMC/Playlist1A/MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root`, `Truth` tree, 544,343 entries |
| Signal selection | **the lane's own re-implementation** of `runEventLoopOmniFold.cpp:1710-1741` → 65,911 signal events |

**The lane's own stated limit, kept verbatim because it governs everything below:** *"It is not the
production cut object; treat the selection as approximate, the per-particle census as exact."* So
per-event *rates* inherit an approximate denominator; per-species *counts and energies* do not.

**Worker agreement is not verification.** These numbers are one lane's measurements with a
non-production instrument on one of 2,365 input files. Promotion needs an independent check.

## 1. The `135` constant — INHERITED ACCIDENT, and the upstream author says so himself

This is the one part that is **not** an inference from a numeric coincidence, and it is stronger than
the evidence Codex relayed.

- `MAT-MINERvA/calculators/CCQE3DFitFunctions.h` contains a `GetEAvailableTrue()` that is line-for-line
  ours, `double mass_pion = 135;` included. Its history is **exactly one commit** — `f790cc794732`,
  2021-07-07, Ben Messerly, *"calculators/ initial commit."* Never edited. **Codex's id and date verify.**
- The same organisation **fixed the identical constant in its other implementation of the same
  quantity**: `GENIEXSecExtract/src/XSec.cxx`, commit `564e2788051f`, 2021-11-26 —

  > *"Bugfix: this should be the charged pion mass not the neutral pion mass I think"*

  with the patch `-double mass_pion = 135;` / `+double mass_pion = 139.57;`.

**CORRECTED BY SESSION A 2026-08-13 — the first version of this section overstated the attribution, and
the overstatement was headed for an outside collaborator.** It read *"the author labelled `135` a
neutral-pion-mass mistake in his own commit message."* **That is wrong: they are two different people
in two different repositories.** Verified directly:

| | MAT-MINERvA `CCQE3DFitFunctions.h` (our source) | `GENIEXSecExtract/src/XSec.cxx` |
|---|---|---|
| author | **Ben Messerly** | **abbeywaldron** |
| commit | `f790cc794732`, 2021-07-07 — **the only commit ever** to that file | `564e2788051f`, 2021-11-26 |
| value **today** | **`135`, still standing** (line 38) | `139.57` |

So the defensible statement is: **a different MINERvA developer, in a different MINERvA repository
implementing the same quantity, called `135` a neutral-pion-mass mistake and fixed it four months
later — and MAT-MINERvA's copy was never fixed and still reads `135` today.** That is strong evidence
and it is *not* an admission by the person who wrote our line. The π⁰-reuse hypothesis remains the
survivor — `XSec.cxx` defines `Mpi0=0.135` and `Mpip=0.13957` two lines apart — but "I think" in that
commit message is hedged, and it should be quoted with the hedge intact.

**Confidence: high that `135` is a π⁰-mass error; NOT established that our copy's author intended it as
an approximation, because he never commented on it and never revisited the file.**

The OI-30 row's "possibly inherited from MAT" is confirmed and sharpened from *inherited* to
*inherited from a copy that was never fixed, while a sibling implementation was*.

**AND THIS IS THE LOAD-BEARING INPUT TO THE MAT-COMPATIBILITY QUESTION** (Joseph's second public
commitment, being answered by lane `dc` — recorded here as evidence, **not** as the verdict, which is
not mine to issue). Because MAT still reads `135` today, **"exact MAT compatibility" and "physically
correct charged-pion mass" are in direct conflict; they are not reconcilable.** Matching MAT bit-for-bit
means matching a value that another MINERvA repo labelled a bug and corrected. Whichever way that
resolves, it is a choice between two defensible goods and should be presented to Gregor as such rather
than as a bug being fixed.

**Recommended minimal correction (a recommendation, NOT an action):** `CVUniverse.h:364` `135` →
`139.57`, plus the two mirrors deliberately kept in lockstep — `nd-unfolding/pet/pointcloud_projection.py:51`
(`M_PION_EAVAIL = 135.0`) and `3d-unfolding/genie/genie_to_xsec3d.py:42` (`MASS_PI_PM = 0.135`, whose
comment *"matches CVUniverse mass_pion=135 MeV"* means it will **silently desync** if only one is
changed). Docs: `3d-unfolding/README.md:28`, `nd-unfolding/pet/POINTCLOUD_PROJECTION.md:28`.

## 2. The clause says two things OI-30's summary did not

Fetched verbatim from arXiv:2312.16631v2:

> *"The weak decay products of strange, or heavier quark, baryons are included by adding their total
> energies to the sum, and by subtracting (or adding) a nucleon mass in the case of baryons
> (antibaryons)."*

**"strange, or heavier quark"** — charm counts. And **for antibaryons the nucleon mass is ADDED, not
subtracted.** Neither was in the OI-30 row.

## 3. The census — and a finding much larger than the two residuals asked about

Per signal event, ancestry traced through `mc_er_ID`/`mc_er_mother`:

| PDG | n | ΣE (MeV/signal-evt) | clause-covered fraction |
|---|---|---|---|
| K⁺ | 2,193 | 71.103 | 1.14% |
| K⁻ | 759 | 26.637 | 11.73% |
| e⁻ | 34 | 0.239 | 17.65% |
| e⁺ | 75 | 1.223 | 21.33% |
| p̄ | 33 | 3.079 | **0.00%** |
| **total** | | **102.28** | **2.105 MeV/evt (2.06%)** |

**Against MINERvA's own reference implementation** of the clause (`GENIEXSecExtract/src/XSec.cxx`
`case kEAvail:`) — not against the lane's reading of the prose:

| species | ours | minerva-ml | MINERvA `kEAvail` |
|---|---|---|---|
| e± | excluded ✔ | total E ✘ | **excluded** |
| K± | excluded ✘ | total E ✔ | **total E** |
| p̄ | excluded ✘ | E − m ✘ | **E + m_p** |
| strange baryons (Λ, Σ) | excluded ✘ | excluded ✘ | **E − m_p** |
| K⁰/K⁰_L/K⁰_S, η | excluded ✘ | excluded ✘ | **total E** |
| π± | E − **135** ✘ | total E ✘ | E − **139.57** |

**On the three species asked about: K± — minerva-ml right, we wrong. e± — we right, minerva-ml wrong.
p̄ — both wrong, in opposite directions.** And the sweep found rows *neither* repo handles: Λ/Σ
(48.89 MeV/evt) and neutral kaons (59.28 MeV/evt).

## 4. The ancestry-fallback question DISSOLVES, and this is the load-bearing result

OI-30's row says *"a PDG-only rule cannot determine that provenance."* True of the **prose** — and
**MINERvA's own realization of the clause is nevertheless PDG-only.** It approximates "weak decay
products of heavy-quark baryons" by catching **the baryon itself** in the final-state list
(`pdg >= 2000` → `E − m_p`) rather than tracing daughters.

The ancestry census independently validates that approximation: daughter-tracing would add
**~2 MeV/event**, catching Λ/Σ directly adds **48.9 MeV/event**. So the recommended rule consults no
ancestry, and **adopting it is *how* the provenance question is made moot** rather than answered.
The requested "fallback for when ancestry is unavailable" is therefore the same rule, unchanged.

## 5. Materiality — the two corrections are NOT in the same class, and should not be bundled

Truth axis edges `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]` GeV. Measured multiplicity **1.0563 π±/signal event**.

**Pion-mass fix alone:** 4.827 MeV/event (measured directly; 4.57 × 1.0563 = 4.827 closes the
arithmetic — the ingredients agree). 0.251% of mean truth E_avail, **4.83% of the narrowest bin
width**, and **439/65,911 = 0.666% of events change bin**, worst case **+1.049% in bin 1**.

**Full reference rule:** mean truth E_avail 1920.49 → **2132.67 MeV (+212.18)**, **4.837% of events
change bin**, per-bin **−10.99% in bin 1** and **+12.81% in bin 7**. Decomposition: K± +97.74,
neutral kaons +59.28, strange baryons +48.89, p̄ +3.55, π-mass −4.83, remainder ~+7.6.

**The smallest test, and it needs NO rerun.** The production 5D omnifiles already carry `MC_npip`
beside `MC_eavail` (verified in `runEventLoopOmniFold_5D_MEFHC.root` and `…_universes_full.root`,
32,849,103 entries), and `MC_npip` counts π± with `E − 139.57 > 0`. So

```
MC_eavail_corrected = MC_eavail - 0.00457 * MC_npip      # GeV
```

is applicable **offline to existing files**: re-bin and re-derive from the frozen unfolded weights, no
retraining, no new inputs. **The full reference rule does NOT have this property** — Λ, K⁰ and η are
not dumped per event — so it needs the point-cloud dump (top-12 truncated) or an event-loop rerun.
**Keep the two decisions separate.**

## 6. Interaction with the reco-support tension — one-directional

Truth `GetEAvailableTrue` and reco `NewEavail()` are computed from disjoint inputs, so **changing the
truth constant cannot move any reco value**; the negative-reco population and underflow boundary are
untouched. For the **pion-mass fix: no material interaction**, the two threads proceed independently.
For the **full reference rule: −10.99% out of truth bin 1** is exactly where an underflow repair
attaches, so #3 **should not land without the underflow choice in hand.**

**Supplementary, and it does not cleanly reproduce.** Re-measuring Codex's figures on
`3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root`: negative-reco signal rows **221** (Codex 218), all
221 truth-selected, signal **37.14** (36.64), background **16.92** (16.74), data **76** (73) → **2.52σ**
(2.30σ). **The qualitative claim reproduces; every count sits 1–4% above his and the cause was NOT
determined** — most likely a marginally different underflow predicate or a different copy of the file.
Note this file **does not exist in the local tree**, so the fork could not be cross-checked.

## 6b. DOES THE CONSTANT MOVE A QUOTED NUMBER? — still NO, but the reassuring ratio is a lower bound

**Added 2026-08-13 by Session A after the adopted-uncertainty artifact was supplied.** This was §7's
top could-not-determine. It is now **partly** closed, and the honest answer is less comfortable than
the arithmetic first suggests.

**The denominator, read directly** (`VALIDATION_LEDGER.md:1043-1045`): adopted covariance
`uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`, **adopted median per-bin
fraction 13.69%** over the **10,550** bins PET also reports. Deliberately NOT the neighbouring 14.8%
(PET) or 13.3% (GBDT) from `pet_vs_gbdt_uncertainty_5d_summary.json`, which are marked *INDICATIVE,
2M-train anchor* and *FLAGGED, NOT ADOPTED*; nor the 4D comparator's 11.8%/13.4% over 4,796 bins.

**THE DIMENSIONAL MISMATCH IS REAL AND IT RUNS IN THE FLATTERING DIRECTION.** `13.69%` is the
fractional uncertainty of a single **5D** bin. My `+1.049%` is a count shift on the **1D truth E_avail
marginal**. From `p4_lib.py:22`, `GRID_NBINS = 65856 = 14*16*7*7*6 (pt,pz,eavail,q3,W)` — **E_avail is a
7-bin axis**, so one E_avail slice aggregates roughly `10,550 / 7 = 1,507` reported 5D bins. Aggregation
reduces fractional uncertainty unless the bins are perfectly correlated, so **the marginal's uncertainty
is smaller than 13.69%, and the true ratio is therefore LARGER than the naive one:**

| assumption about the 5D bins in one E_avail slice | marginal σ | shift / σ |
|---|---|---|
| **perfectly correlated** (no reduction) | 13.69% | **7.7%** |
| **independent** (`13.69/√1507`) | 0.353% | **297%** |

**A factor of 39 between the bounds, so `7.7%` is the most favourable reading available and is NOT the
answer.** It is what you get by assuming the systematics are 100% correlated across every bin of an
E_avail slice. Reality sits between — systematics dominate here so it is nearer the correlated end —
but "nearer" is not a number, and at the independent end the shift would *exceed* the uncertainty
threefold.

**VERDICT: the constant almost certainly does not move a quoted number, and this derivation does not
prove it.** What closes it is one specific thing: **project the adopted covariance onto the E_avail
marginal** — sum the sub-blocks over the other four axes, retaining off-diagonals — and compare
`+1.049%` against *that*. Until then the honest claim is "consistent with immaterial, bracketed
[7.7%, 297%] of the adopted uncertainty depending on correlation structure."

**Two further caveats that the ratio hides, and neither is pedantry.**

1. **The denominator has four live open items.** `VL62` (one-sided endpoint interpolation), `VL63` (CV
   centering), `VL64` (varying estimator seeds), `VL65` (scalar jitter subtraction) are all **OPEN for
   the adopted 5D GBDT covariance that `values.tex` actually quotes** — `VL63` records it as **0 of 7
   for the quoted artifact**, discharged only for the footing-matched stamped candidate, "which carries
   none of the stamps." So this is a ratio against a denominator under active repair.
2. **The numerator is not the same kind of object as the denominator.** `+1.049%` is a change in the
   *truth-axis population*, propagating to a quoted cross-section only through the unfolding. The
   comparison is an order-of-magnitude sanity check, not a derivation of the effect on a published
   value.

**~~Ledger discrepancy noticed in passing~~ — RETRACTED 2026-08-13, THERE IS NO DISCREPANCY.** I flagged
line 1043's **10,550** against `VL62`'s **10,694** as two numbers for one artifact. **They are two
different SETS and the ledger already says so**, at line 1049: *"on the **10550** common 5D bins (GBDT
reports **144** extra)"* — and `10,550 + 144 = 10,694` exactly. So `10,694` is the GBDT covariance's full
reported-bin set and `10,550` is the subset **common to PET**; line 1043's own phrasing carries the
qualifier, *"the 10550 bins PET also reports."* Line 975 likewise says *"10,550-bin reported mask."*
**Nothing is owed and no row needs opening.** Raised by `personal-orchestrator`, verified here against
lines 627/975/1043/1049 rather than accepted.

**Kept rather than deleted, because I am the second reader to trip on it** — which makes it a fact about
the ledger's readability, not about my attention. The resolution now lives at the point of confusion.

## 7. Explicitly could-not-determine — carried forward, not dropped

- **Whether the pion-mass fix moves a QUOTED number.** The shift is known (+1.05% in bin 1); the
  adopted per-bin fractional uncertainty was not read. **One read closes this**, and it is the single
  highest-value next step.
- Why the underflow counts differ from Codex's by 1–4%.
- Whether the reference rule's η and Δ-resonance side effects are acceptable — **η was not censused**,
  and the `pdg>=2000` branch also catches Δ resonances.
- Whether the minimum π± energy in the tuple is ≥ 139.57 — needed before calling the offline
  correction *exact* rather than *near-exact*.

## Recommended disposition (Session A)

**Split OI-30 into two items of different classes rather than treating "settle the constant" as one
task.** The constant is a settled-provenance, offline-correctable, ~0.25% documentation-grade fix. The
rule mismatch is an unsettled, rerun-scale, ~11% physics question that touches an unresolved underflow
repair. Bundling them would let the second block the first, or the first wave the second through.
**Neither is adopted here; both are Joseph's call.**
