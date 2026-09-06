# SPECIFICATION 2026-09-06 — the complete scalar-5D successor **Z**: scientific contract, cause
# dispositions, terminal criteria, dependency analysis, and a costed execution proposal
# **rev. 2 — contract review round 1, and Joseph's rulings on its recommendations**

**CITABLE FOR:** §1's contract, §2's seven cause dispositions, §3's terminal criteria, §4's dependency
table, §5's cost arithmetic **with its stated uncertainty**, and §6's rulings with their authority.

**NOT CITABLE FOR:** any construction, any authorization to construct, any implementation, any compute,
any grade on any leg, any discharge, any adoption, any count, any gate movement, any spend, any
`SCOREBOARD` cell, or any publication claim. **Gate 2 remains FAIL. Counts hold at CAND `1 of 7`,
QUOTED `0 of 7` — this record moves no count.** No scalar-5D covariance is adopted. `(cause 7, G)`
remains permanently OPEN under `R1`. Y remains cause-7-only and unconstructed under `R2`; **Z is not Y
renamed and nothing here widens Y**. PET remains diagnostic under `R6`. `R5`'s accounting start,
ceilings and stop date are preserved exactly. **`CRITERIA` §0's three-token vocabulary is NOT extended
— see §6.1.**

**Status: SPECIFICATION ONLY.** `RZ(iv)`: this *"authorizes no implementation, construction, compute,
grading, adoption, or publication change"*. **All seven of Z's prospective cells are unopened and
ungraded here**, and this document opens none.

**`BEN-381` DISQUALIFIES THIS LANE FROM GRADING THE LEGS THIS CONTRACT DEFINES.** It drafted them and it
re-measured the evidence they rest on. The grading lane must be one that took none of the deciding
measurements. That separation is `R2`'s pattern and it carries forward.

## 0.0 What changed in rev. 2, so a reader of rev. 1 is not silently overtaken

Rev. 1 was `d2a515e0`. An independent contract review (detached checkout
`/private/tmp/z-contract-review.POIDb8`, read-only, no compute, no files edited) returned three
implementation-blocking findings, a set of cost corrections, and four non-blocking factual corrections.
**Every one was re-measured at this base before being applied. The reviewer is upheld on all of them,
and five were rev. 1 defects of mine.** Joseph then ruled on the decisions the review put to him (§6).

| # | rev. 1 said | rev. 2 says | whose call it was |
|---|---|---|---|
| 1 | §1.3: the unified-throw inflation is *"inside"* `C_syst(Z)` | **§1.3a now carries the explicit algebra** — `D_Z`, the 13-band vertical set `V`, its operands, zero-denominator handling and both centering variants, transferred from `adopt_unified_5d.py:1-27` | **reviewer.** *"Inside"* is not an implementation contract |
| 2 | §2.1: Z's cause-1 `M` *"must include all three excluded bands"* | **WITHDRAWN.** `Flux` (N=100), `2p2h` (N=3) and `__Normalization_flat` have **no ±pair**, so the one-sided counterfactual is undefined for them; the census carries them **unchanged in both totals**, where they cancel. Including them means **inventing endpoints** — a criterion extension, not arithmetic | **reviewer.** I read a definitional boundary as an omission |
| 3 | §2.6: the bidirectional coverage guard is *"an unrepaired instance of cause 6 in current code"* | **WITHDRAWN — stale.** Both projectors guard both directions at this base, and they differ **deliberately** in fail-closed-ness | **reviewer** |
| 4 | §2.6: *"Z must break that reuse"* of `C_stat`/`C_ML` | **WITHDRAWN as an inference.** The finalize launcher proves **reuse**, not **incompleteness**; fresh replica generation needs a stated scientific rationale, which this lane does not have | **reviewer** |
| 5 | §6.1 Route A: *"define a fourth token"* | **WITHDRAWN — already ruled against, in a record in this tree that I did not open.** `DECISION-20260902-joseph-rules-no-fourth-grade-token.md`. Route B was always the only route, and it is now ruled (§6.1) | **my miss**, surfaced by the review's cause-5 framing |
| 6 | §1.3: the Y closure *"would fail on every correct Z"* | softened — it is **not an identity for Z**, and other differences **could cancel**, so it may pass **accidentally**. That is worse than failing | **reviewer** |
| 7 | §§2.3/3.1: the fixed-seed null alternates *"exactly zero"* and *"≤ tol"* | reconciled, and the implemented tolerance is measured and found **vacuous on this scale** (§3.1a). Joseph has ruled a scale-relative bound (§6.4) | **reviewer** |
| 8 | §5: `71.5`/`113`, and a replay that doubles to `143`/`226` | **corrected throughout** — the P4 figure is a runtime prior, not R5 spend; assembly, both variants and the combine were missing; the replay doubling is withdrawn as mandatory | **reviewer** |
| 9 | §5.4: the cause-3 scope fork is *"≈4.5× on GPU"* | **WITHDRAWN — mixes three populations.** Replaced by the complete-member accounting | **reviewer** |
| 10 | §5.2: the cause-4 extra unfold at `0.73` **GPU** task-hours | **WITHDRAWN — my own population mix.** `--null` runs in the **CPU** combine step; the `43.5`-min basis is a **GPU** arm-3 per-task time. Re-treated in §5.2 | **found here**, applying the reviewer's own rule to a line the reviewer did not name |

**Upheld from rev. 1, re-verified by the reviewer independently:** the S marker correction (§1.4), the
cause-3 seed-split supersession (§2.3), and that Y's lateral closure is not Z's (§1.3c).

## 0.1 Authority and subject, bound by digest and re-measured at this base

| role | artifact | sha256, **recomputed at this base** |
|---|---|---|
| **the ruling this drafts against** | `docs/orchestration/DECISION-20260906-joseph-authorizes-z-specification-only.md` (`RZ`) | `304179df3905337d0ecd22af8a7416ed6aca5d7e050f89999667b57a6d251904` |
| **the prompt, subordinate to it** | `docs/orchestration/PROMPTS-20260906-z-specification-session.md` | `69b86539ed4c36ca1c527f17d943bac9f12081ffdd40e95bdaa9b9a814491688` |
| **controlling above both** | `docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` (`R1`–`R6`) | `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064` |
| **the grade vocabulary, ruled CLOSED — and rev. 1 missed it** | `docs/orchestration/DECISION-20260902-joseph-rules-no-fourth-grade-token.md` | `e59df9557e6ec1d21b845d7647c0038662c490713d8a43b2f72cd60bd34dc477` |
| **the question `RZ` answers** | `docs/orchestration/PACKET-20260905-full-scalar5d-successor-scope-question.md` | `fe46d64f04b7a34246275fc09b52b6c1db76d47756b9b6731f7c329b0fcd7de8` |
| **method reused, limits inherited** | `docs/orchestration/PREDECLARE-20260905-cause7-only-successor-Y.md` | `6bcb01581287d63010c9dee8d93e930f9da36eba2eacb1990c30a70d5c80f369` |
| **the `C`/`P`/`M`/`T` legs for cause 7** | `docs/orchestration/PREDECLARE-20260901-cause7-discharge-criteria.md` | `572c0825a926329dfaa5bfdfe37f8e277954def1b62f46c34a47ac12ab3f2c2b` |

**Base of every measurement in this file: `d2a515e0`** (rev. 1's tip), branch
`lane/y-cause7-spec-and-scope`. **Every `file:line` citation carries its symbol name beside it**, because
a line number in a growing file decays (`CRITERIA` §4.4; `SCOREBOARD` `POINTER 3`) — rev. 1 propagated
four decayed citations and corrected them before landing.

**One off-branch pair is cited and is NOT an ancestor of this tip:**
`VOI-20260906-cause3-mii-estimator-seed-scan.md` and
`FINDING-20260906-cause3-scan-execution-composition.md` at **`47494dbe`**, branch
`lane/cause3-voi-20260906` (ancestry measured: **not an ancestor**). They are cited for cause-3 cost
populations (§5.4), and they corroborate §2.3's seed-split finding by an independent route.

## 0.2 The rulings — authority, quoted rather than summarized

Joseph, 2026-09-06, on the contract review's recommendations, in his own turn to this lane:

> *"Can you correct these issues? Follow the recommendations for decisions from me."*

**Asked explicitly** — because in this repository an authorization is itself an evidence artifact, and
"RULED" is not a wording choice — whether the decisions the review framed as questions for him were to
be recorded as **his rulings** or left open in a carve-out, he selected: **record them as his rulings.**
That selection was made from an option list this lane wrote, and is recorded as such so a later reader
can weigh it; the sentence above is his own text.

**The recommendation text is the REVIEWER's; the adoption is HIS.** Both are recorded, and §6 quotes the
recommendations rather than paraphrasing them. This is `DECISION-20260902` §1's own pattern: *"The
framing under each ruling is this lane's and remains open to challenge on its merits; the adoption of
the conclusions is his."*

**What the rulings do NOT do:** they construct nothing, run nothing, grade no leg, discharge no cause,
move no count and no gate, and adopt nothing. **They do not extend `CRITERIA` §0's vocabulary.** They do
not retroactively regrade G.

## 0.3 What Z is, in one paragraph, so it is not read as something larger

Z is **one new scalar-5D covariance artifact on G's grid**, built at a new pinned revision, named under
`RZ(i)` as a **prospective** grading subject for **all seven** quarantine causes and a **possible**
adoption subject. Both hedges are Joseph's and both are load-bearing. Z **does not exist**: its output
paths, receipt schema and version, and producing revision are all undefined (§1.6). Z is **not** G
repaired — G's bytes are immutable and `RETAINED` under `R1`. Z is **not** Y widened — Y is cause-7-only
under `R2` and stays there. Z is **not** S promoted — §1.4. Z's seven cells are **new**; they overwrite,
reuse and retire nothing, and they may **never** be combined with G's or Y's grades, in either direction
(`RZ(iii)`). §3.4 states the limits without hedging.

---

# 1. THE SCIENTIFIC CONTRACT — deliverable `RZ(v)(a)`

## 1.1 Artifact identities — path plus digest, no definite descriptions

**`*.root` is `.gitignore`d, so no ROOT below is in this checkout**; ROOT digests are quoted from
committed receipts and labelled as such, never as this lane's own file reads.

| name | identity | role for Z | where measured |
|---|---|---|---|
| **G** | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root`, sha256 `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`, job `56720356`, **10,694** reported bins of the **65,856**-bin grid | **required, digest-bound `parent_candidate`**; the **`M`-leg comparison baseline for every one of Z's seven cells**. **NOT an operand of Z's construction** — §1.3 | `R1`; `PREDECLARE-20260901-cause7` §0 |
| **G.combined_source** | `uq_universe_5d_covariance_combined_bkgaware.root` — **name only; no digest for it is recorded anywhere in the tree** | the support-limited lateral family Z replaces five bands of, **and the file the 13 vertical per-band covariances are read from** (§1.3a) | `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json:28-30`, key `combined_source` |
| **G.uthrow_source** | `unified_throw_cov_5d_fluxfix_20260806_full160.root` | the throw ROOT G's inflation was derived from. **Z derives its own** — §1.3a | same receipt, `:32-34`, key `uthrow_source` |
| **G.centering** | `mean-centered` | Z's **primary** variant inherits it; the CV-centered variant is the F7 sibling, not a replacement | same receipt, `:24-26`, key `centering_convention` |
| **G total √Tr** | `5.269625166386846e-38` | the `M`-leg denominator for aggregate comparisons | `DECISION-20260831` §5 |
| **block-sum footing** | `4.357790406860002e-38` | byte-identical between G and X; the footing every arm is matched on. **G / blocksum = `1.2092`, which is the inflation's whole effect at trace level** | `DECISION-20260831` §5; ratio computed here |
| **S** | `nd-unfolding/active_universe_5d/standard/candidate/std_final5_candidate.root`, sha256 `950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263`, **42,326,607,877 B**, Slurm `57128458` step `.1`, 2026-08-16 | **component donor only**, each donated band **re-digested into Z's receipt**. **Supplies no inflation** — §1.4c | `p4_standard_validation.json`; `state/RECEIPT-20260816-p4-standard-stages456.json` |
| **S.component_manifest** | `nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json`, sha256 **`269232245870632884d6e589ac8d7aa9ba7fb4e07d0860e077cbd98fe6de04b5`** — **recomputed by this lane, MATCHING the `component_manifest_sha256` its sibling receipt records** | the bound inventory of what S may donate: 45 `all_syst_bands`, 40 `retained_bands`, 5 `replaced_lateral_bands`, per-band `component_content_hash` for all 45 | this lane |
| **S.support_family** | `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root`, sha256 `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` | **the same PATH G's receipt names as `combined_source`** — a candidate answer to `PM-2`, **but not an answer**: S read it 2026-08-16, G was built 2026-08-12, and nothing binds the two reads to the same bytes | `std_component_manifest.json` |
| **S.stat_cov / S.ml_cov** | `uq_cov_stat_5d.root:hCov_stat5d_reported` sha256 `6580016fa7136e6f98867707f4d48557350b26a91773d0c300be20113c2c6934`; `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported` sha256 `27b2e456f80e15d8a5c4da1bcd3b01a201b80385341af68614c85b6b7f8f5374` | Z's candidate `C_stat` and `C_ML` inputs. **Whether Z reuses or regenerates them is an open scientific question, not a settled requirement** — §2.6 | same manifest |
| **F** | `uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`, **266** bins, job `56431823` | **not evidence for Z**; `266 ≠ 10,694` | `OI-5`, `VL68`, `CRITERIA` §4.1 |
| **J** | the July `uq_universe_5d_covariance_combined_bkgaware_uthrow{,_cvcentered}.root` pair quoted by `values.tex` | **not evidence for Z**; wrong parent digest, every named stamp `ABSENT` | `DECISION-20260831` §1; `SCOREBOARD` §1 |
| **Y** | **specified, unconstructed.** Constructing it requires `D-Y-CONSTRUCT` (`R2(iv)`), which does not exist | **not a prerequisite for Z** — §4 row 1 | `PREDECLARE-20260905`; `R2(iv)` |
| **Z** | **PATHS, RECEIPT SCHEMA/VERSION, AND PRODUCING REVISION DO NOT EXIST.** §1.6 | the object specified here | this record |

## 1.2 The constants that must be imported rather than retyped

- `GRID_NBINS = 65856` — `nd-unfolding/p4_lib.py:22`, the `14×16×7×7×6` `(p_T, p_∥, E_avail, q3, W)` grid.
- `BANDS` — `p4_lib.py:18-19`, *"Canonical standard lateral inventory (exactly these; order fixed)"*:
  `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS`.
- `ENDPOINTS = (0, 1)`, `N_ENDPOINTS = len(BANDS) * len(ENDPOINTS)` — `p4_lib.py:20-21`, value `10`.
- `NONZERO_MIGRATION_BANDS = {BeamAngleX, BeamAngleY}`,
  `ZERO_MIGRATION_BANDS = {MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS}` — `p4_lib.py:64-65`.
- **`VERT_BANDS` — NEW IN REV. 2**, `nd-unfolding/adopt_unified_5d.py:42-43`: the **13** vertical bands
  the 5D unified throw covers (12 knob bands + `Flux`) — `2p2h`, `CCQEPauliSupViaKF`, `FrAbs_pi`,
  `FrElas_N`, `HighQ2`, `LowQ2`, `MaCCQE`, `MaRES`, `MFP_N`, `MvRES`, `Rvn2pi`, `Rvp2pi`, `Flux`.
  §1.3a cannot be written without it.
- **`F7_FLOOR_MULTIPLE = 2.0` — NEW IN REV. 2**, `nd-unfolding/uq_math.py:138`, with the predicate
  `f7_cv_centered_required` at `:160-169` and a **strict `>`** boundary. §2.2.

**Z's producing code must import every one of these, never restate them.** A retyped list is a second
implementation of a rule that already has one, and this repository already carries a **conflicting**
lateral inventory: `nd-unfolding/pet_lateral_correction.py:42-43` defines `LATERAL` with **six** entries,
adding `MinosEfficiency`. **The reported-bin count is a PREDICATE, not a literal:** `10,694` is the count
of bins with candidate CV > 0; select by predicate, then **assert** against G's, never hardcode.

## 1.3 Z's construction, stated as algebra rather than as prose

**Z holds the central value fixed.** All seven causes are *covariance construction* causes; the scalar
4D/5D central values are `VALIDATED`. So Z is built on **G's central value**, therefore on **G's reported
mask and row ordering**, as a **declared invariant with a guard**:

    mask_digest(Z) == mask_digest(G)        row_order_digest(Z) == row_order_digest(G)

Both must be **read from G** before construction (`PM-4`, §4) and re-asserted by Z's validator. A Z whose
mask differs makes every `M`-leg comparison in §2 ill-posed, because the two sides would be distributions
over different populations.

### 1.3a The composition, with the inflation given its explicit place

**This subsection is the reviewer's first implementation-blocking finding, discharged.** Rev. 1 said the
inflation was *"inside"* `C_syst(Z)` without saying which components change; that is not an
implementation contract. The construction below is **transferred from `adopt_unified_5d.py:1-27`**, which
already specifies it for G, and is restated here as Z's requirement.

Partition Z's systematic bands into three **disjoint** sets:

- **`V`** — the **13** vertical bands the unified throw covers, exactly `adopt_unified_5d.VERT_BANDS`.
- **`A`** — the **5** selection-complete active lateral bands, exactly `p4_lib.BANDS`.
- **`R`** — **every other systematic band** in the support family: the 4 weight-only detector-lateral
  bands (`MinosEfficiency`, `GEANT_Neutron`, `GEANT_Pion`, `GEANT_Proton`) plus the remaining
  non-vertical bands. `|V| + |A| + |R|` must equal the support family's band count, and the three sets
  must be **verified disjoint and exhaustive at build time**, not assumed.

**The partition is well-defined and the gate is satisfiable — measured, on the one committed 5D band
inventory that exists.** Against `std_component_manifest.json`'s 45 `all_syst_bands`:
**`|V| = 13`, `|A| = 5`, `|R| = 27`, summing to `45`**; `V` is a subset of the 40 `retained_bands`;
`V` and `A` are disjoint; the union is exactly `all_syst_bands`; and `R` holds all four weight-only
detector-lateral bands. **That measurement is against S's family read, not G's** — `R` is defined as
a complement, so it is only as good as the family list it complements, and `PM-5` (§4 row 8) is the
read that closes it on G's own `combined_source`.

Then, for each centering variant `c ∈ {mean-centered, cv-centered}`:

    C_Z^c  =  D_Z^c · ( Σ_{b∈V} C_b ) · D_Z^c   +   Σ_{b∈R} C_b   +   Σ_{b∈A} L_b   +   C_stat   +   C_ML

`D_Z^c = diag(g^c)` is the **per-bin unified/block sigma inflation**, *transferred* rather than swapped
in — for the reason `adopt_unified_5d.py:6-11` gives: with `n_throws ≪ bins`, `C_unified` is a low-rank
noisy estimate of the full matrix and *"swapping the whole matrix in directly breaks
positive-definiteness"*. The transfer is PSD by construction.

    v_uni^c[i] =  clip(diag(C_unified)[i], 0, ∞)          ( + mean_shift[i]^2  when c = cv-centered )
    v_blk[i]   =  clip(diag(C_blocksum)[i], 0, ∞)
    g^c[i]     =  sqrt( max( v_uni^c[i], v_blk[i] ) ) / sqrt( v_blk[i] )          >= 1
    g^c[i]     =  1                                        wherever  sqrt(v_blk[i]) == 0

**Operands, each named.** `C_unified` and `C_blocksum` are read **diagonals only** from **Z's own** throw
ROOT (`adopt_unified_5d.py:89-90`, via `_diag`); `mean_shift` is `hJointMeanShift` from the same file
(`:93-96`). `Σ_{b∈V} C_b` is read from **Z's own** `combined_source` as `hCov_universe5d_<band>` for each
of the 13 (`:129-141`) — **the same sweep estimator as the rest of `C_syst`**, which is exactly why the
transfer is PSD rather than a matrix substitution.

**Six properties a Z receipt must state and a Z validator must check:**

1. **Each vertical component appears exactly once**, inflated, inside `D_Z (Σ_V C_b) D_Z`. It does
   **not** also appear in `R`.
2. **The full throw covariance `C_unified` is NOT a budget block.** Only its **diagonal** is used, and
   only to form `g`. A Z that adds `C_unified` to the sum has double-counted the vertical systematics.
3. **`C_seed`, if measured (§2.3), is a DIAGNOSTIC and is NOT a budget block either** —
   `PREDECLARE-20260901-cause3-mii` §5's own limit, *"It does not add `C_seed` to the uncertainty
   budget"*, restated here because §1.3a is precisely where an extra block gets added by accident.
4. **`R` and `A` are never inflated.** The throw does not cover them (`adopt_unified_5d.py:19-20`), and
   `max()` never under-covers the block baseline.
5. **Zero denominator is `g = 1`, not a division.** `adopt_unified_5d.py:108-113` masks on `sb > 0`. A
   bin with zero block variance is left alone; it must not become `NaN`, `inf`, or be silently dropped.
6. **Both centering variants are produced, always, to distinct explicitly-passed `--out` paths.** F7
   requires the shift reported *either way* (§2.2). `adopt_unified_5d.py:79-80` **defaults** `--out` and
   opens it `RECREATE`, so a defaulted `--out` is a destructive-overwrite hazard — which is why
   `sbatch_j28_adopt_5d.sh:111,113` passes it explicitly, twice.

### 1.3b The identity set Z's writer and validator must EACH independently recompute

The existing standard-P4 gates verify a **block sum**. Z is an **inflated** object, so the gate set must
be **extended** — and the extension is the part that does not exist today.

| identity | tolerance | status at this base |
|---|---|---|
| `Σ active-5 == L_active(Z)` | rel `1e-9` | **exists** — `active_total_eq_sum5` |
| band set is exactly the support family's | exact set | **exists** — `band_set_completeness_vs_support_family` |
| exactly five active bands, ten ± endpoints | exact | **exists** — `exact_5_active_bands` |
| symmetry and PSD | exact / eigenvalue | **exists** — `symmetric_psd` |
| `C_syst^blocksum == Σ_V + Σ_R + Σ_A` (the **uninflated** sum) | rel `1e-9` | **exists** — `c_syst_recomputed_from_components` |
| `C_Z^blocksum == C_syst^blocksum + C_stat + C_ML` | rel `1e-9` | **exists** — `full_total_identity_recomputed` |
| **`V`, `R`, `A` pairwise disjoint AND exhaustive over the family** | exact set | **DOES NOT EXIST** |
| **`C_Z^c − C_Z^blocksum == (g^c_i g^c_j − 1) · (Σ_V C_b)_{ij}`** | rel `1e-9` | **DOES NOT EXIST.** This is the inflation's closure identity and the one gate that can catch a double-counted or mis-scoped vertical set |
| **`g^c >= 1` everywhere, finite, and `== 1` exactly where `v_blk == 0`** | exact | **DOES NOT EXIST** |
| **PSD of the INFLATED object**, not only of the block sum | eigenvalue | **partial** — `adopt_unified_5d.py:150-165` checks `ev[0] >= -1e-12·ev[-1]` on the adopted matrix, but outside the P4 gate list, so no receipt records it as a gate |

`1e-9` is the existing standard-P4 relative closure tolerance (`p4_build_components.py:140-171`). **It is
a numerical closure tolerance and may not be reported as an `M`-leg materiality threshold**
(`PREDECLARE-20260901-cause7` §1 `C`(4)).

### 1.3c The place Y's method does NOT carry over

Y's closure is `C_Y − C_G == L_active − L_support`, exact because Y changes **only** the lateral block and
`C_G` is literally the minuend. **Z has no such identity**: Z rebuilds the inflation, the centering, and
possibly the statistical block, so `C_Z − C_G` is a sum of independent differences.

**Rev. 1 said such an assertion "would fail on every correct Z". That is too strong and is withdrawn:**
the other differences **could cancel**, so the assertion might **pass**. That is the worse case, because
a check that can pass for the wrong reason certifies nothing. The requirement is §1.3b's component
identities, and **`C_Z − C_G` is a reported difference, never a closure condition** — see §2.7 for the
matching distinction on cause 7's magnitude.

## 1.4 S is not Z's starting point — and the ground usually given for that does not reproduce

**The conclusion holds. One of the two reasons routinely given for it is stale.** The reviewer confirms
this correction reproduces independently, and adds the right qualification: *"This removes the claimed
marker refusal; it does not establish scientific adoptability or supply inflation."*

### 1.4a The measurement

`PROMPTS-20260906` §2(a), `PACKET-20260905` §6.2, `PREDECLARE-20260905` §1 and `SCOREBOARD` §5 all state
that S *"carries `publication_gate_rejects_this: true`"* and that *"`p4_adopt_standard.py` refuses it
outright"*. Measured against the committed candidate packet:

| claim | measurement | verdict |
|---|---|---|
| S's component manifest carries the marker `true` | `std_component_manifest.json` — key **absent** | **does not reproduce** |
| S's validation receipt carries the marker `true` | `p4_standard_validation.json` — key **absent**; records `"result": "PASS"` over **11 gates**, `full_total_identity_relerr = 4.6027194117555535e-14` | **does not reproduce** |
| S's projection manifest carries the marker | `std_proj4d_candidate_projmanifest.json` — `publication_gate_rejects_this: **false**`, `non_adoptable_marker_key_present_in_parent: **false**` | **carries the marker FALSE** |
| the `true` marker exists somewhere | `nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json:324` — the **FPS purity-control** manifest | **a different artifact** |
| `fps_build_control_manifest.py:202-204` *dies* if the gate fails to reject | true; its operand is *"the purity-control manifest"* (`die_evidence_blocked`, `:203`) | **true of FPS, not of S** |
| `p4_adopt_standard.py` refuses S outright | `result == "PASS"` ✓; `gates` a list ✓; `band_set_completeness_vs_support_family in gates` ✓; `component_manifest_sha256` present and **recomputed to match** ✓; `require_adoptable(prov)` passes on an absent key; `val.get(NON_ADOPTABLE_KEY)` absent | **does not reproduce as stated** |

### 1.4b Why the claim exists, dated — it was true, of a different S

The pre-2026-08-16 candidate was built by allocation `56636802` *"explicitly non-adoptable
(`P4_NON_ADOPTABLE=1`, verifier token unset)"* (`P4_STANDARD_STATUS.md:77`) — the switch
`p4_lib.stamp_non_adoptable` (`p4_lib.py:677-690`) reads. Its digest was `602bbcf2…`. Run `57128458`
rewrote it to `950f8cb1…` **under the repair-11 PASS token**. **`VALIDATION_LEDGER` `VL68` already
carries the 2026-08-22 correction** — *"The cause-7 verdict in this cell is UNCHANGED and still correct:
built is not adopted. `p4_adopt_standard.py` has never run… Only the *build* clause was stale."* The
broader conclusion is `VL68`'s, not this lane's.

### 1.4c The durable ground — three reasons, the third new in rev. 2

1. **S is a block-sum object; G is an inflated one, and Z must be inflated.** S's receipt records
   `sqrt_tr_full = 4.3576e-38` against the block-sum footing `4.357790406860002e-38` — ratio **`0.99996`**.
   G's total is `5.269625166386846e-38`, **`1.2092×`** the block sum. Substituting S's total for G's is
   forbidden outright by `PREDECLARE-20260901-cause7` §1 `C`(3).
2. **S addresses one cause of seven.** `replaced_lateral_bands` is exactly `p4_lib.BANDS`;
   `retained_bands` is the other 40, read from the same support family. That is **cause 7 and nothing
   else**.
3. **NEW — S cannot donate the component Z most needs.** `D_Z` is derived from **Z's own throw ROOT's**
   `C_unified`/`C_blocksum` diagonals. **S has no throw arm**, so §1.3a's entire vertical term is absent
   from it and there is nothing in S to donate for it.

**S may donate**, and this is real reusable evidence: the 45 per-band `component_content_hash` values,
`reported_mask_hash = 74374b1af0795c3eb077c9ef0ee6ef3cfa4d7b7b3df63bd4f392d7db80eb136a`,
`row_index_sha256 = 61746918371fb9a99f69b8e657f98e0796ae9efd63e21a89346fbb620a596f08` under key
`hRowIndex5D`, and the five active-band traces. **Every donated component is re-digested into Z's receipt
at Z's build time.**

## 1.5 Receipt schema — written LAST, identifying the exact Z it describes

Versioned, per `PREDECLARE-20260901-cause7` §1 `P`, extended from Y's §3 to seven causes and to §1.3a:

- **Z:** path, byte size, sha256, reported-bin count, **mask digest**, **row-order digest**, producing
  job/run **and step**, and **which centering variant this file is**.
- **Parent:** G's exact path and **full** sha256 as `parent_candidate`; G's committed `combined_source`
  **name and the digest of the support-family ROOT actually read** (`PM-2`).
- **Code identity:** pinned producing revision **plus executable import-closure digests, bound to the
  run**. *A clean implementation at an unpinned revision is not `C`.*
- **The inflation block — new in rev. 2:** `V`/`R`/`A` membership as read from the imported constants;
  the disjointness and exhaustiveness results; the throw ROOT's path and digest; `g` as a histogram plus
  `min`, `median`, `max`, the count of bins `> 1`, and **the count of bins where `v_blk == 0` and `g` was
  pinned to 1**; the measured residual of §1.3b's inflation closure identity; and `sqrt_tr` before and
  after inflation.
- **Per cause, a named block** carrying its own operands — cause 1's counterfactual **with its scope
  statement** (§2.1); cause 2's F7 operands **with `k` and its source**; cause 3's `estimator_seed` and
  `draw_seed` at **both** legs; cause 4's re-added print value, seed and both operand digests; cause 5's
  path trace; cause 6's projection operator digest and **both** coverage censuses; cause 7's five removed
  support keys, ten endpoints with **migration censuses and declared policies**, and five active digests.
- **Closure:** measured operands and residuals for **every** identity in §1.3b; symmetry; PSD **of the
  inflated object**.
- **The negative statement, verbatim:** *F's 266-bin receipt, S's whole-file PASS, and any receipt about
  G are not evidence that Z was produced. Where S supplies a component, that component's digest is
  rebound into this receipt at Z's build time.*

**The two fields whose absence has cost this campaign before:** the per-endpoint migration census and
declared policy, and the import-closure digest bound to the run. A declared-zero band measuring nonzero
migration, **or the reverse**, must **abort**.

## 1.6 What does not exist yet

1. **Z's output paths** — one per centering variant, under a Z-specific directory, never a rewrite of
   G's or S's path. **`p4_build_components.py:180` opens `--out` with `RECREATE`** and
   `adopt_unified_5d.py:79-80` **defaults** `--out`, so Z's paths must not collide with any existing
   candidate and `--out` must always be passed explicitly.
2. **Z's receipt schema and version** — §1.5's field set, versioned, written **last**.
3. **Z's producing revision** — pinned commit plus import-closure digests bound to the run.
4. **Z's validator** — the standard-P4 validator covers the block-sum identities; **§1.3b's four
   inflation gates do not exist**, and the six non-cause-7 causes have no Z-side validator at all.
5. **Z's test-contract fixtures** — §3.3.

---

# 2. CAUSE DISPOSITIONS — all seven, each argued, none inherited — deliverable `RZ(v)(b)`

**The governing rule:** discharge is a property of a **(cause × artifact)** pair (`CRITERIA` §0). **Z
inherits nothing from G.** Every cell below is `OPEN` for Z by construction, including the two settled
for G. Each row states **what Z would have to do differently, and what evidence would show it** — not a
prediction and not a grade. Leg states quoted for G are read from `SCOREBOARD-20260817`'s CAND column and
its `POINTER 4`; where a later record supersedes the board, that record is named.

## 2.1 Cause 1 — one-sided endpoint interpolation

**G:** `C` MET, `P` MET, **`M` MEASURED, not MET**, `T` MET. Cause 1 does not close, ruled 2026-09-01
(`DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` `RULING 1`): the `+3.1%`/`+5.9%` √Tr difference
with a `1.7–2.0×` median per-band ratio is **material enough to need its own statement in the note**.

**RULED for Z, 2026-09-06 (§6.2): measure-and-disclose closure, irrespective of magnitude, once
independently verified.**

**What Z must do differently: nothing in the construction.** Every `C_syst` builder on G's path already
forms band covariances via `uq_math.mat_covariance` over both endpoints. The ruled obstruction was never
the construction; it was `M`'s materiality plus the disclosure obligation.

**⚠ REV. 1 WAS WRONG ABOUT THE THREE NON-PAIR BANDS, AND THE CORRECTION IS THE POINT OF THIS ROW.**
Rev. 1 said Z's cause-1 `M` *"must include all three excluded bands"*, reading `RULING 1`'s third ground
as an omission to be filled. Measured in the producing receipt,
`nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json`:

> `:744` `"counterfactual_scope": "N==2 pair bands only. Flux (N=100), 2p2h (N=3) and
> __Normalization_flat are carried UNCHANGED in both totals."`
> `:738` `"scope_note": "Totals differ ONLY through the pair bands; Flux, 2p2h and the norm band are
> byte-identical contributions in both."`
> `:753` `"excluded_reason": "N != 2, so there is no '+1 sigma endpoint'; carried unchanged in both
> totals"`

**So they are not missing from the measurement — they are outside its domain, and they cancel.** The
one-sided form is `diag(outer(x_ep − CV))`, which requires a ±pair; for `N ≠ 2` there is no
`+1σ endpoint` to take. **Constructing a counterfactual for them means inventing endpoints that do not
exist, which is a criterion EXTENSION and not arithmetic** — and it would be a proposal for §6, not a
requirement of this contract. **Rev. 1's requirement is withdrawn.**

**What Z's cause-1 `M` must do, as ruled:**

1. **Both one-sided choices, for the actual ± pairs.** The receipt already computes them —
   `:746` `"one_sided": "... computed for BOTH ep in {0,1}"` — and reports
   `ratio_one_sided_ep0_over_as_built` and `ratio_one_sided_ep1_over_as_built` per band. Z reports both,
   per band, on Z's own bank.
2. **Off-diagonal effects.** The census is `"diagonal_only": true`, which is exactly `RULING 1`'s third
   ground. Z compares off-diagonal structure as well as diagonals.
3. **Denominator qualifications stated.** Every ratio names its denominator and the population it is
   over; a per-band ratio and a √Tr ratio are different objects and must not share a sentence without
   both denominators named.
4. **The non-pair bands accounted for EXPLICITLY, without inventing endpoints.** Z's receipt states, for
   `Flux` (N=100), `2p2h` (N=3) and `__Normalization_flat`, that they are carried unchanged in both
   totals, with their band count `N` and their contribution to each total — so a reader can see they
   cancel rather than infer it.
5. **The sign report.** `RULING 1`'s second ground: the effect **changes sign** — `MaCCQE` ep0 `0.6377`
   and `MaRES` ep1 `0.6111` are *understated*. Z reports the ratio distribution **with its below-1 tail**,
   because a consumer assuming conservatism is wrong on those bands.
6. **Independent verification** of the measurement, by a lane `BEN-381` does not disqualify. This is the
   ruling's own condition and it is what "measure-and-disclose" rests on.

**And the disclosure.** `RULING 1` created a note obligation for cause 1. Under §6.2 that obligation is
part of Z's closure condition, **and writing the note text remains a publication act outside `RZ(iv)`** —
so `(cause 1, Z)` cannot be *graded* closed until the disclosure exists, and this specification does not
write it.

**Evidence that would show it:** Z's own bank, built both ways, per band, distribution plus off-diagonal,
with `uq_math.require_truth_ratio_bank` PASS and the scope statement in Z's receipt.

## 2.2 Cause 2 — CV centering

**G:** all four legs MET, and it is the **one** cause discharged — *"`1 of 7` (cause 2, Joseph,
2026-08-12, **candidate only**)"*. **That discharge was BY DECISION**, which the board's counts table
records separately from *"causes with four METs"*, which is **`0`**. That precedent matters for §6.1.

**What Z must do differently: nothing in the construction, everything in the evidence.** `RZ(iii)`
applies with full force: **Z cannot borrow G's cause-2 discharge.** `P` is a statement about *which
bytes*, and Z's bytes are new.

**Cheapest of the seven, for a stated reason: cause 2's `M` criterion is predeclared, mechanical, and —
new in rev. 2 — its factor is PINNED IN CODE.** The reviewer's directive is *"Pin F7's existing factor
rather than leave ≫ executable by interpretation"*, and the factor exists:

- `uq_math.F7_FLOOR_MULTIPLE = 2.0` (`nd-unfolding/uq_math.py:138`);
- `mean_shift_sampling_floor(sqrt_trace, n_throws) = sqrt_trace / sqrt(n_throws)` (`:141-149`);
- `f7_cv_centered_required(...)` returns `mean_shift_over_floor(...) > k` — a **strict** inequality
  (`:160-169`), with the boundary pinned by a test asserting `2.0 × floor` is False and
  `2.000001 × floor` is True (`tests/test_uq_remediation.py:407-413`).

**Z's contract therefore says `k = uq_math.F7_FLOOR_MULTIPLE`, imported and not retyped, strict `>`.**
The module's own comment is preserved as part of the contract: `2.0` is *"a CODIFICATION, NOT A REPO
DECISION"*, chosen so a shift at `1.0×` is unambiguously below and the measured `4.69×` unambiguously
above, and *"deliberately not tuned to sit just under 4.69x"*. On G it measured `4.83×` after the flux
correction.

**And the rule's other half, which the predicate's own docstring insists on:** `False` does **not** mean
the shift may be dropped. F7 requires the shift **reported either way**; `False` only means the
CV-centered variant is not *additionally mandatory*. §1.3a property 6 requires both variants regardless,
so for Z the predicate's value is **reported**, not branched on.

**One discrepancy this lane will not resolve.** `CRITERIA` §2 cause 2 states `T` is *"Absent, and this is
cause 2's only real gap"*; `SCOREBOARD` grades cause 2's `T` **MET** (`f7_cv_centered_required`, N3/N4).
The two control documents disagree; the board is later and is the board. Reconciling them is a third
document's act.

**Evidence that would show it:** Z's own `hJointMeanShift` and `joint_mean_shift_norm`; both centering
variants as separate files with `--out` passed explicitly; the floor with `N` stated; `k` and its source;
and the F7 predicate's value recomputed on Z's ensemble.

## 2.3 Cause 3 — varying estimator seeds

**G:** `C` PARTIAL (*"INAPPLICABLE to the dominant block"*), `P-i` PARTIAL, `P-ii` OPEN **with its
premise measured FALSE at HEAD** (`POINTER 4`), **`M` OPEN and "NOT CURRENTLY MEASURABLE"**, `T` MET.

**RULED for Z, 2026-09-06 (§6.3): the quantity is the JOINT-BASELINE variation of the assembled
covariance; the narrow fixed-draw scan is DIAGNOSTIC for Z unless substitution is separately ruled; the
existing 46/50-member family is NOT assumed to be the necessary design; and favourable, unfavourable and
inconclusive outcomes are specified BEFORE measurement.**

**⚠ THE BOARD'S §2b IS SUPERSEDED AT THIS BASE.** `SCOREBOARD` §2b (2026-08-17) records that `M(ii)`
*"cannot be configured on either leg"*. **Both halves are false at `d2a515e0`:**

| §2b's finding | measured |
|---|---|
| sweep leg: seed is a literal, no flag, 14 `add_argument` | `sweep_bank_5d.py:358` **`--estimator-seed`**; `add_argument` count is **15**; `:344` comments *"This was the literal `seed=42`"*; `:309` writes `TParameter("estimator_seed")` |
| throw leg: one `--seed`, two roles, varying is unsatisfiable | `unified_throw_cov.py:630` **`--draw-seed`** and `:634` **`--estimator-seed`**, **both `required=True`**; `:269` `rng = np.random.default_rng(args.draw_seed + gj)` drives the draw while `args.estimator_seed` drives `_xsec_for_weights`; `:569-570` writes **both** keys |
| `do_combine` guards one seed | `:477-479` refuses a mixed **estimator** seed **and** `:483-485` refuses an incoherent **draw** seed |

**Landed `3dd5e66e`, 2026-08-18T01:16:55−04:00** (*"GATE 1 BUILT: `unified_throw_cov.py`'s dual-role
`--seed` is split into required `--draw-seed` and `--estimator-seed`"*), verified an ancestor of this
base — **one day after** §2b was written, so §2b was correct when written. Corroborated independently by
`VOI-20260906` §7.5 at the off-branch `47494dbe`.

**The reviewer's qualification is right and is adopted:** *"Configurable code does not repair historical
provenance or settle composite-scan scope."* The split makes the composite **buildable**; it settles
nothing about G's provenance and nothing about which quantity closes the leg.

**What Z must do differently.**

- **`C`:** extend the guard to the dominant block. §2b's surviving finding is that *"the single-seed
  property of the dominant block holds by hardcoding and is checked by nothing"*. `sweep_bank_5d.py` now
  **stamps** its seed, which is `P`; **refusing** a mixed-seed `C_syst` slab is still new code.
- **`P`:** Z's receipt records the seed **value** at both legs. The write sites exist at this base
  (`sweep_bank_5d.py:309`; `analyze_universes_5d.py:273-277`, the `_identity` write loop;
  `unified_throw_cov.py:569-570`; and `mii_adopt_unified_5d_stamped.py:168`'s `LEG_IDENTITY_KEYS`, which
  `POINTER 4` cites as a write site and which at this base is the key **tuple** those writes use). **A
  new build at current HEAD writes them** — structurally the same route as cause 4's: the capability
  landed after G's bytes existed.
- **`M(i)`:** the fixed-seed null, under §6.4's ruled scale-relative bound — see §3.1a.
- **`M(ii)`:** **the joint-baseline composite quantity on Z**, per §6.3 — the variation of the
  **assembled** `C_Z` when the sweep-side and throw-side estimator baselines are varied **jointly**, not
  the fixed-draw 12-seed scan. The design (how many members, which offsets) is **open and must be
  specified**; §6.3 explicitly does not adopt the 46/50-member family as necessary. Costed in §5.4.

**The three outcome classes must be predeclared, per §6.3.** `PREDECLARE-20260901-cause3-mii` §4's six
branches are the model and `R4` preserves them: two INCONCLUSIVE (wrong footing; vacuous seed variation),
one favourable, three unfavourable. **A valid large result is not automatically MET** — the branch
structure is what makes the leg falsifiable, and Z's must be written before Z's measurement, not after.

## 2.4 Cause 4 — scalar jitter subtraction

**G:** `C` MET, `P` MET, **`M` OPEN — AND IT CANNOT BECOME `MET`**, `T` MET. The ground is **structural,
not a search** (`DECISION-20260902-joseph-applies-oi173-cause4-m.md` §5, superseding `SCOREBOARD` §3's
empty search at `:670`): no **committed** revision of `unified_throw_cov.py` carries both the
jitter-floor print and the flux fix `081ae4ac`.

**Re-measured at this base:** ancestry of `081ae4ac` in `a0cdc019` → **false** (the print revision,
2026-06-08T16:24:23−07:00, **predates** the flux fix, 2026-07-31T23:53:54−04:00); ancestry of `081ae4ac`
in this base → **true**; `unified_throw_cov.py` carries **one** `jitter` occurrence, a **comment** at
`:476`, and `jit_trace` **zero** times. **This measurement is narrow and is labelled narrow:** it
establishes that those two revisions do not coexist and that the current file carries no print, not that
no committed revision anywhere carries both. The broader conclusion is
`DECISION-20260902-joseph-applies-oi173-cause4-m.md` §4's, whose cell text carries *"committed"*
deliberately.

**What Z must do differently: build at a NEW revision that re-adds the print on top of current HEAD.**
This base descends from `081ae4ac`, so such a revision carries **both**. G can never benefit; Z's would.

**`OI-173` `RULING 2` fixes the referent:** `M` is specified **against the class of object the defect
actually reached — the reported ratio — NOT against the stored covariance.**

**Packet §5's three verification conditions, plus a fourth this lane adds because §5's third needs a
mechanism:**

1. the re-added print computes **the same quantity** the retired code printed —
   `jit_trace = float(np.sum((x_cv2 − base) ** 2))`, `x_cv2` a second CV unfold at `seed + 7`, recovered
   from `a0cdc019:232-252` and compared line for line;
2. its **operands are the new build's own** — both vectors' content digests in Z's receipt;
3. adding it **does not change the covariance content**;
4. **the print is print-only, never subtracted.** Cause 4's `C` leg is *"no subtraction term anywhere on
   the path"*; a quantity in scope is one edit from being subtracted. Condition 3 must be enforced by a
   **guard that fails** if the computed value ever reaches the stored covariance, not by a one-time
   comparison.

**The single-draw referent is RETAINED.** `jit_trace` is a **one-sample estimate of a variance** — the
recovered comment writes it as `E‖x_cv2 − x_cv1‖² = 2 Σ_bin σ_jit²` and a single evaluation is one draw
(`SCOREBOARD` §3). **For Z this is materially better than for G:** Z's printed value is *the* realization
Z's own construction would have subtracted, contemporaneous with the build. It is still one draw, and
Z's receipt states so with its seed named. **Rev. 1 floated requiring `n > 1` draws; that is withdrawn
(§6.5) on the reviewer's directive, adopted by Joseph** — the defect cause 4 names *is* a single-draw
subtraction, so a multi-draw `M` would measure something the defective construction never did.

## 2.5 Cause 5 — frozen PET weights

**G:** **`N/A` ON ITS MERITS**, established 2026-08-17, declaration landed in `VL66` at `d1c5f90`.

**RULED for Z, 2026-09-06 (§6.1): an artifact-specific "INAPPLICABLE, DISPOSED BY DECISION" outcome is
authorized for `(cause 5, Z)`, after the complete trace and the falsifier check — without four
artificial METs, without extending `CRITERIA` §0's vocabulary, and distinguished from a mechanical
four-MET discharge.**

**What Z must do first: re-run the trace on Z's own path.** `VL66`'s declaration carries its own scope,
stated by the declarer so it could be falsified: *"the trace covered the bank build (`sweep_bank_5d.py`),
the three block producers, and the background source. It did **NOT** exhaustively audit
`analyze_universes_5d.py` or `adopt_unified_5d.py` for every input."* And it names the falsifier: *"a
PET-derived product consumed by either of those two modules."*

**Z's path is a superset of the traced one** — it adds a lateral-replacement chain, and `D_Z`'s transfer
runs through `adopt_unified_5d.py`, **one of the two modules `VL66` did not audit**. So the trace must be
re-run over **every module Z invokes**. This is a **static read**, not compute — cheap, but neither free
nor inherited. **And not by cause 5's owner:** `VL66` records that `OI-3`'s owner cell reads *"PET /
cause 5 owner"*, so the non-transferability claim is the owning lane's own and *"is not itself the
outside-lane evidence"*; the outside evidence is the `sweep_bank_5d.py` trace and *"it stands alone"*.

**Why a ruling was needed, and why the remedy rev. 1 proposed was the wrong one.** `CRITERIA` §3:246
defines the vocabulary as `MET` / `OPEN` / `UNRESOLVED` and states *"a cause is discharged only with four
METs"*. `SCOREBOARD` §7b put the question and it was **RULED 2026-08-17, the conservative branch**: a leg
graded outside those three *"can never discharge, however sound the reasoning for its inapplicability."*
So a cause-5 `N/A` blocks a mechanical seven-MET Z. **Rev. 1 offered "define a fourth token" as a route.
That route was already closed** — `DECISION-20260902-joseph-rules-no-fourth-grade-token.md`
(`e59df955…`), Joseph, *"okay I also agree"*: **`CRITERIA-20260811` §0's vocabulary stands unchanged; no
token is added for the permanently-unmeetable state.** That record is in this tree and rev. 1 did not
open it. §6.1 records the correction and the ruling that replaces it.

## 2.6 Cause 6 — incomplete statistical projection

**G:** `C` PARTIAL, **`P` OPEN — *"no product rebuilt at all"***, `M` OPEN, `T` MET.

**⚠ TWO REV. 1 CLAIMS ARE WITHDRAWN HERE. Both were the reviewer's findings and both reproduce.**

### 2.6a WITHDRAWN — the bidirectional coverage guard is not missing

`CRITERIA` §2 cause 6 `C` says *"`build_projection_M` checks 5D→4D coverage and **never** 4D→5D"* and
calls it *"an unrepaired instance of cause 6 in current code"*. Rev. 1 carried that forward as a Z
requirement. **Measured at this base, it is stale, and BOTH projectors guard both directions:**

- **`p4_lib.build_projection_M` (`:1353`) — FAIL-CLOSED both ways.** The construction loop requires every
  reported HIGH bin to land in a reported LOW bin (`:1380`), and an explicit second block at
  `:1394-1395` — `empty = np.nonzero(~M.any(axis=1))[0]; require(empty.size == 0, ...)` — fails on any reported LOW bin
  no HIGH bin reaches. Its comment is dated **2026-08-09, BEN-064** and names the exact masking defect
  `CRITERIA` describes: *"an error that is loudest about the least important thing is worse than no
  error, because it redirects the investigation."*
- **`p4_lib.reachable_low_mask` (`:1322`) — the contract correction, 2026-08-10.** The projection's low
  support is *"not 'the 4D reported mask'; it is 'the part of the 4D reported mask the 5D support
  reaches'"*, **derived** rather than assumed, with the bidirectional check *"left exactly as it is — it
  becomes a genuine invariant that must never fire in production rather than a thing the caller argues
  with."* The 5 dropped bins hold `3.00e-46 .. 2.09e-44`, *"0.0000% of the 4D total; that is a fact about
  these products, not a licence"*, and the caller records indices and count.
- **`eavailW_covariance.py:407-432` — guarded both ways and DELIBERATELY NOT fail-closed.** Added
  2026-08-11 for quarantine cause 6, with the reason stated in the code: the `(E_avail, W)` plane is
  kinematically constrained (`W² = M² + 2·M·E_avail − Q²`), *"so some cells are physically unreachable
  and an empty row here can be correct, where in a 5D→4D marginal it cannot be. Aborting would make a
  legitimate geometry unrunnable. So: count it, name it, and put it in the output."* The value is
  single-sourced in `ew_coverage_report` (`:55-68`) and propagated to the ROOT by `write_ew_outputs`
  (`:71`), so a propagation test has something to bind to.

**Z's requirement is therefore NOT "repair the guard". It is: preserve the asymmetry, and prove it.**
Z's contract requires the P4 projector to stay **fail-closed** and the `(E_avail,W)` projector to stay
**count-and-report**, with both censuses in Z's receipt. **A Z that "fixes" the `(E_avail,W)` projector
into fail-closed would break a legitimate geometry** — the opposite error, and the one this correction
exists to prevent.

### 2.6b WITHDRAWN — reuse of `C_stat`/`C_ML` is not evidence of incompleteness

Rev. 1 read `sbatch_finalize_5d_bkgaware_gpu.sh:8-10` — *"C_stat/C_ML are #13-invariant → reuse existing
`uq_cov_stat_5d.root` / `uq_cov_mlsplit_5d.root`"* — as proof that Z must regenerate them. **The reviewer
is right that this does not follow:** the launcher proves **reuse**, and reuse of an invariant input is
not incompleteness. **Fresh scalar replica generation needs a stated scientific rationale, and this lane
does not have one.**

**And the sentence rev. 1 leaned on is PET-scoped.** `CRITERIA` §2 cause 6 grounds the cause on
*"`docs/OPEN_ITEMS.md:62-63`: 'Rerun the five-axis statistical replicas and project the full covariance
as `M C_5D Mᵀ` before rebuilding `(E_avail,W)` significances'"*. **At this base `:62-63` carries an
unrelated ID-collision note.** Measured: the archived form is at `docs/OPEN_ITEMS-ARCHIVE-2026-08.md:76`,
and the **live home is `OI-4`** — owner *"C (PET)"*, route `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`,
prerequisite *"the full-event nominal and coherent ensemble"*. **Cite it by id, never by line.** The scope
consequence the decay hid: the sentence `CRITERIA` applies to the 5D GBDT covariance now lives in a
PET-scoped row. **This lane flags that and does not reconcile it.**

### 2.6c What Z's cause-6 disposition actually is

1. **`P` is the real gap, and it is about a PRODUCT, not an ensemble.** *"No product rebuilt at all"*
   means no `(E_avail,W)` covariance has been rebuilt since the fix (`KNOWN_ISSUES.md:357`), and the same
   script's J28 flux site is code-fixed with **no number produced** (`KNOWN_ISSUES.md:338-349`). Z closes
   this by **producing** `C_low = M C_Z Mᵀ` via `uq_math.project_covariance`, with a receipt naming
   **both** the operator and the corrected `C_5D` input. *"Never sum standard deviations across
   marginalized cells"* — the comment is at `eavailW_covariance.py:392-395` at this base and the call is
   `project_covariance(C5stat, Mew)` at `:441` (`CRITERIA` §2 cites the pre-drift range `:316-341`).
2. **`C` is the coverage contract of §2.6a, preserved and evidenced**, plus the exactness of the map.
3. **`M`:** √Tr and per-bin median of the marginalized covariance under (i) summed standard deviations
   and (ii) `M C Mᵀ`, on **identical** inputs, plus the orphan-bin count **in each direction** and the
   fraction of √Tr they carry.
4. **The ensemble question is OPEN and is named as open.** Whether Z reuses S's `stat_cov`/`ml_cov`
   digests or regenerates the replicas is a **scientific** decision requiring a rationale — for example,
   a measured incompatibility between those inputs' footing and Z's. **This specification does not
   decide it**, and §5 prices both.
5. **A scope question, stated rather than decided.** `6a` (the operator) is a property of a projection
   *from* the trunk; `6b` (the ensemble) is a property of the trunk. Whether `(cause 6, Z)` is graded on
   both is a scoping call the grading lane should make **explicitly** rather than inherit.

**A recorded cross-check that must not be read as a gate.** `RECEIPT-20260816` surfaces it deliberately:
between the marginal and the independent 4D routes, **3,009 of 4,825 bins differ by more than 3%**,
median `4.4%`, max `72.9%`, integrals agreeing to `0.56%`. The receipt states it *"bears on the
marginalization-vs-direct question, NOT on the projection identity (`3.76e-16`)"*.

## 2.7 Cause 7 — CV-support-limited lateral selection

**G:** **permanently OPEN** under `R1`, an immutable historical cell. **Z cannot change that.**

**What Z must do differently:** `PREDECLARE-20260905`'s replacement algebra applied to a **full rebuild**.
`L_support` is exactly the five-band sum over `p4_lib.BANDS` read from the support family; `L_active`
exactly the corresponding five selection-complete mean-centered MAT endpoint covariances on Z's mask and
row order; support keys `hCov_universe5d_<band>`, active keys `p4_lib.candidate_band_key(band)`.

**⚠ THE COUNTERFACTUAL AND THE AGGREGATE DIFFERENCE ARE TWO DIFFERENT OBJECTS, and rev. 2 separates them
on the reviewer's directive.** For Y they coincide, because the lateral swap is Y's only change. **For Z
they do not:**

- **The lateral counterfactual** — `Σ_A L_active` against `Σ_A L_support` on Z's own inputs — is
  `(cause 7, Z)`'s `M`. It isolates the defect cause 7 names.
- **`C_Z − C_G`** is an aggregate difference that **also contains** the inflation, the centering, the
  statistical block and every other cause's change. **It is a reported number and it is NOT cause 7's
  magnitude.** Reporting it in cause 7's cell would attribute six causes' worth of movement to one.

Z's receipt reports both, each labelled with **what it is a difference of**, and cause 7's `M` cites only
the first.

**The five-of-nine scope limit is inherited in full, and so is its pre-condition.**
`nd-unfolding/uq_5d/detector_universes.txt` enumerates **nine** detector lateral bands (18 lines = 9
bands × 2 endpoints): the five kinematic ones plus `MinosEfficiency`, `GEANT_Neutron`, `GEANT_Pion`,
`GEANT_Proton`. Z replaces five of nine; the other four sit in `R` (§1.3a). The justification is that
they are **weight-only** — `VALIDATION_LEDGER.md:788-791` and `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:239-241`
both say so. **But the ledger sentence sits in the FPS row** (job `56431823`, the 266-bin chain), so it is
a **2D/FPS-side claim**, and `PM-1` — re-measuring it on G's own `combined_source` — is a Z pre-condition
exactly as it is Y's. **The `2D_OMNIFOLD_REFERENCE.md` sentence is not a second measurement**; both
describe the same kinematic/weight-only split.

**A measured expectation, and the prohibition attached to it.** S's committed `support_comparison` records
`sqrt_tr_active = 1.4742855148740122e-38` against `sqrt_tr_support = 1.474709838719496e-38`, ratio
**`0.9997122662137712`** — the five-band lateral block moves **−0.0288%** on the 5D grid. F's 266-bin
replacement moved **+10.96%** (`VL69`–`VL71`), per-bin σ ratio min `0.7897`, median `1.0071`, max `1.4402`
(`VL74`). **Prohibited:** citing either as Z's `M`, or as a reason Z's `M` need not be measured.
**Permitted:** sizing the run, and noting that the two differ **in sign and by two orders of magnitude** —
which is itself why the 5D number cannot be inferred from the FPS one, and why §3.3's fixtures must be
**bidirectional**. The S ratio carries `support_ratio_is_diagnostic_not_bounded` in its own receipt, and
`p4_lib.py:1309-1318`'s helper *"deliberately bounds nothing"*.

---

# 3. TERMINAL CRITERIA — deliverable `RZ(v)(c)`

**`RZ(ii)`: seven distinct assessment cells.** What a completed Z assessment looks like **per cell**, and
what a **failed** one looks like. **It opens no cell. It grades nothing.**

**And, per `RZ(ii)` as §6.1 reads it: `RZ` requires seven ASSESSMENTS, not seven favourable results.** A
Z with six METs and one `INAPPLICABLE — disposed by decision` is a **complete** assessment under §6.1,
not a failed one.

## 3.1 The fixed-seed null contract, stated once so §§2.3 and 3.2 cannot contradict it

### 3.1a The measurement, and why the implemented bound is not a bound

Rev. 1 alternated *"exactly zero"* and *"≤ tol"*. The implementation is
`nd-unfolding/unified_throw_cov.py:509-520`, with the tolerance at `:517`:

```
# Fixed-seed null: this must be exactly zero (within floating tolerance).
null_norm = float(np.linalg.norm(x_cv2 - base))
tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)
if null_norm > tol: raise SystemExit("[FAIL] CV re-unfold is non-deterministic ...")
```

**So the contract is "exactly zero within a floating tolerance", and the two phrasings are not in
conflict — but the tolerance as written is vacuous on this scale.** `base` is a cross-section vector:
per-bin values are order `1e-39` over 10,694 reported bins, so `‖base‖` is order `1e-37` — **far below
`1.0`**. Therefore `max(‖base‖, 1.0)` evaluates to `1.0` and `tol` is an **absolute `1e-12`**, roughly
`10^25` times `‖base‖`. **It is not a relative determinism bound; it is a bound that essentially nothing
can violate.**

**This does not mean G's null is bad.** The measured value on G is `5.8223e-50`, i.e. `1.31e-12` of the
sqrt-trace (`CRITERIA` §2 cause 4) — genuinely tiny *relative* to the scale. **The defect is in the
guard, not in the product**, and it is the `T`-leg shape this campaign already knows: a check that cannot
fail.

### 3.1b What Z's contract requires

**Ordinary correction, no decision needed:** acknowledge the floating tolerance rather than claiming
literal zero; require the key **present** (absence must fail, never pass vacuously) and both operands
**finite**; and state the **units and normalization** of every quantity in the comparison.

**RULED, 2026-09-06 (§6.4): Z uses a SCALE-RELATIVE null bound, fixed before production**, with the
numerical value justified by precision and sensitivity controls established **before** implementation and
**not** selected from a favourable production result. **This does not retrospectively regrade G.**

## 3.2 Per-cell completion and per-cell failure

A cell is `(cause n, Z)`. Under `CRITERIA` §0 each carries four legs `C`/`P`/`M`/`T`, all four must hold,
and `UNRESOLVED` is a permitted per-leg verdict that must not be re-read as the nearer of PASS/FAIL.

| cell | **complete** looks like | **failed** looks like |
|---|---|---|
| **(1, Z)** | both one-sided choices per ± pair, **off-diagonal included**, denominators named, the three non-pair bands accounted for **without invented endpoints**, the below-1 tail reported, `require_truth_ratio_bank` PASS, **independently verified**, and the `RULING 1` disclosure written | the counterfactual is diagonal-only; a denominator is unnamed; a ± endpoint is invented for a non-pair band; the below-1 tail is dropped; the measuring lane also grades it |
| **(2, Z)** | `hJointMeanShift` and `joint_mean_shift_norm` present; the floor `√Tr/√N` with `N` stated; `k = uq_math.F7_FLOOR_MULTIPLE` **imported**, strict `>`, value reported; **both** centering variants emitted as separate files with explicit `--out` | a mean-centered-only product; the shift folded into the variance; `k` retyped or left as *"≫"*; `--out` defaulted |
| **(3, Z)** | `estimator_seed` **and** `draw_seed` stamped at **both** legs; a mixed-seed `C_syst` slab **refused**, not merely unstamped; the null under §3.1b's scale-relative bound with the key **present**; `M(ii)` measured as the **joint-baseline** quantity under a predeclared three-class outcome rule | any leg unstamped; the null key **absent**; `M(ii)` substituted by the narrow fixed-draw scan **without** the substitution being separately ruled; `M(ii)` inferred from `\gbdtAiEstTrace`, which `FOOTING-20260817` established cannot serve on footing; outcome classes written after the result |
| **(4, Z)** | the re-added print's value, **seed** and both operand digests; §2.4's four conditions met, condition 4 enforced by a **guard**; the `M` referent is the **reported ratio** per `OI-173` `RULING 2`; the single-draw nature stated | the quantity differs from `a0cdc019:232-252`; operands borrowed; covariance content changes; the value is ever **subtracted**; `M` reported against the stored covariance |
| **(5, Z)** | the trace re-run over **every** module Z invokes — **including `adopt_unified_5d.py`, which `VL66` did not audit and which `D_Z` runs through** — by a lane that does not own cause 5, with the falsifier restated; then **`INAPPLICABLE — disposed by decision`** under §6.1 | the trace is inherited from `VL66`; a module Z introduces is unaudited; the owning lane's own statement is counted as outside corroboration; **or four METs are manufactured to avoid the token problem** |
| **(6, Z)** | `C_low = M C_Z Mᵀ` **produced**, with a receipt naming operator and input; the P4 projector **fail-closed** and the `(E_avail,W)` projector **count-and-report**, both censuses recorded; `M` under both routes; the reuse-vs-regenerate decision made **with a stated rationale** | the projection sums standard deviations or is diagonal-only; the `(E_avail,W)` projector is "fixed" into fail-closed, breaking a legitimate geometry; the `3.76e-16` identity is quoted as if it settled the marginal-vs-direct route question; replicas regenerated with no rationale |
| **(7, Z)** | five-band inventory exact both sides; ten ± endpoints each with migration census and declared policy; §1.3b's identities within `1e-9`; `PM-1` clearing the five-band scope on G's own `combined_source`; `M` reported as the **lateral counterfactual**, with `C_Z − C_G` reported **separately and labelled** | any band missing, extra, duplicated, one-sided, or on the wrong grid; a declared-zero band measuring nonzero migration **or the reverse**, noted rather than aborting; a whole-S total substituted; `C_Z − C_G` cited as cause 7's magnitude |

## 3.3 Reject-Z conditions — the specification's falsifiers

**Z is rejected outright, before any cell is graded, if any of these holds:**

1. `mask_digest(Z) != mask_digest(G)` or `row_order_digest(Z) != row_order_digest(G)`.
2. Any §1.3b identity fails outside relative `1e-9` — **including the four that do not exist yet**.
3. `V`, `R`, `A` are not pairwise disjoint, or do not exhaust the support family's band set.
4. Any `g^c[i] < 1`, or non-finite, or `≠ 1` where `v_blk[i] == 0`.
5. `C_unified` appears as a budget block rather than through its diagonal, or `C_seed` appears as a
   budget block at all.
6. Symmetry or PSD fails **on the inflated object**.
7. The parent digest recorded is not G's `4f168e83…`.
8. A band list was **retyped** rather than imported from `p4_lib.BANDS` / `adopt_unified_5d.VERT_BANDS`.
9. Any endpoint lacks a selection-migration census, or contradicts `p4_lib.py:64-65`'s declared policy.
10. The producing revision is unpinned, or import-closure digests are not bound to the run.
11. The fixed-seed null key is **absent**, or its bound is not the scale-relative one §6.4 rules.
12. `PM-1` shows the five-band scope does not cover cause 7's defect class on G's own `combined_source`.
13. The receipt reports `C_Z − C_G == L_active − L_support` as an identity (§1.3c), or cites `C_Z − C_G`
    as cause 7's magnitude (§2.7).
14. Only one centering variant was produced, or `--out` was defaulted for either.
15. Z's tally is presented combined with G's or Y's grades, in either direction (`RZ(iii)`).

**A large `M` on any cause is NOT a reject condition.** `R3` settled that for cause 7; `CRITERIA` §0
states it framework-wide — *"M does not require the corrected number to be small… what is forbidden is an
unmeasured one."* **Cause 1 is the one place a magnitude stopped a cause**, and it did so by a separate
ruling creating a disclosure obligation, not by a threshold — and §6.2 now closes that route for Z.

## 3.4 The test contract — power-tested in both required directions, per cell

`CRITERIA` §0's `T` leg requires a guard that fails when the defect is reintroduced **and** when the
guarded object disappears.

- **Direction 1 — defect reintroduced.** Per cause: substitute the one-sided form (1); emit
  mean-centered-only above the floor (2); feed a mixed-seed slab (3); **subtract** the jitter value (4);
  introduce a PET-derived input to a module Z invokes (5); replace `M` by its diagonal (6); substitute
  CV-support-limited bands for the active endpoints (7). **Plus, for §1.3a:** move a vertical band from
  `V` into `R`; add `C_unified` as a block; feed a `v_blk == 0` bin and check `g` is pinned to 1 rather
  than `inf`. Each must fail **specifically**, even when dimensions, PSD, total trace and internal sums
  still pass.
- **Direction 2 — guarded object disappears.** Delete or rename, one at a time: an active endpoint; an
  active-band object; a migration census/policy; G's parent digest; `fixed_seed_null_norm`; a seed stamp;
  the throw ROOT; `hJointMeanShift`; the projection operator. Each must **fail**, never skip, never
  reduce a band count, never read absence as zero.
- **Positive control** passes with exactly five ± endpoint pairs, the exact G parent digest, G's exact
  mask and row order, both centering variants, and every §1.3b identity within `1e-9`.
- **Artifact-confusion controls must fail:** F (wrong 266-bin grid), J (wrong parent digest), a whole S
  total (no inflation, and changes more than the lateral block), and **G itself**.
- **Two things that do not satisfy `T`:** a source-string assertion, and a test of
  `check_support_comparison` alone — that helper *"deliberately bounds nothing"* (`p4_lib.py:1309-1318`).
- **One thing that does not satisfy `T` and is new in rev. 2:** a fixed-seed-null test written against
  the **current** `tol` formula, which §3.1a measures as unable to fail on this scale.
- **Fixture provenance.** Build fixtures from the **producer's** own objects and metadata. A fixture
  derived from the predicate cannot disagree with it.
- **Mutation discipline.** Each mutation must be shown to **reach** the guard it targets. A digest check
  that refuses a mutated input first, with the same exit status, tests the digest check and not the
  guard; call the unit directly where that is a risk.

## 3.5 What a completed, seven-cell Z assessment could and could NOT establish

**A Z with all seven cells complete and favourable would establish exactly one thing:** that the seven
quarantine causes are disposed **for the artifact Z**, as a self-contained tally. Nothing else.

It would **not**: move any of G's cells (`RZ(ii)`; `(cause 7, G)` stays permanently OPEN under `R1`);
move Y's cell or widen Y; move the CAND or QUOTED counts (`RZ(iii)` — CAND stays `1 of 7`, QUOTED
`0 of 7`); move **Gate 2**, which remains FAIL on six independently sufficient NOT-DISCHARGED clauses
(`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`, exercised at `327bc105`); **adopt Z**
(`RZ(i)` names a *possible* adoption subject; adoption is a separate decision and is Joseph's); license a
projection (3D/4D covariances must be exact projections from an **adopted** trunk); touch `values.tex`,
any publication claim, or `R5`'s scoped-Letter default; or **authorize its own construction** (`RZ(iv)`;
`R5`'s ceilings remain *"a prohibition and an accounting boundary … NOT authorization to spend up to"*).

---

# 4. DEPENDENCY ANALYSIS — deliverable `RZ(v)(d)`

**The three questions are answered separately for every candidate, and one answer is never allowed to
stand in for another** (`PROMPTS` §2.1): **necessary** — would Z's specification or construction be
*unsound* without it? **applicable** — is the thing it measures a property *Z would share*, or a property
of the artifact it was measured on? **reusable now** — can Z take the evidence *without anyone spending
compute*, because it is already committed or is a measurement rather than a build?

**Nothing in this table creates authority.** Items carrying suspended or absent authorization are flagged
`⚠ AUTH`; naming one a prerequisite does **not** authorize it.

| # | candidate prerequisite | **necessary?** | **applicable?** | **reusable now?** |
|---|---|---|---|---|
| 1 | **A standalone Y construction** (`⚠ AUTH`: needs `D-Y-CONSTRUCT`, `R2(iv)`, which **does not exist**) | **NO.** Y is cause-7-only and built by a different algebra — a lateral-only swap with `C_G` as minuend (§1.3c). Z's cause-7 evidence must be measured on Z's own construction | **as METHOD only.** Y's artifact-identity discipline, receipt field set, migration-census requirement and bidirectional test contract are reused in §1.5 and §3.4. Y's *measurements* are not: Y's `M` is `C_Y` vs `C_G`, an object Z does not build | **method: YES, zero compute.** **product: N/A** — it does not exist and constructing it is unauthorized |
| 2 | **The historical-candidate cause-3 fixed-draw seed scan** (`⚠ AUTH`: `R4` **SUSPENDS** it; needs **both** `D-C3-VOI` and `D-C3-RUN`) | **NO for Z**, and §6.3 now settles why: Z's `M(ii)` is the **joint-baseline** quantity on Z's own assembled covariance, and the narrow scan is **diagnostic** for Z unless substitution is separately ruled | **NO as evidence; YES as method and cost prior.** What transfers is the predeclared quantity form, the six exhaustive branches, the thresholds `f_agg ≤ 0.0415` / `f_med ≤ 0.0274` and the 13-task shape. No measured value transfers | **method and thresholds: YES, committed.** **a measured value: NO — none exists.** `R4`: no `nd-unfolding/uq_5d/cause3_mii_20260901/`, no receipt; the run never launched |
| 3 | **The first `r5_meter` accounting receipt measured on Perlmutter** | **YES — for a Z CAMPAIGN, not for this specification.** `campaignctl` is fail-closed and *"admits no item at all until a receipt measured on Perlmutter is committed, and none is"* (`ACCEPTANCE-20260905`) | **YES.** It measures the campaign's spend against `R5`, a property of any Z campaign | **NO — it does not exist.** `docs/orchestration/state/r5-meter-receipt.json` is **absent at this base**. It is a login-node `sacct` query plus a commit, not a build; §5.6 |
| 4 | **`PM-1`** — the nine-vs-five weight-only band census on **G's own `combined_source`** | **YES.** If any of the four weight-only bands carries selection-dependent support in the 5D chain, Z's five-band scope is **incomplete for cause 7** and this specification must be amended | **YES** — a property of the support family Z reads | **NO.** The tree's claim is the **FPS-side** row `VALIDATION_LEDGER.md:788-791`, corroborated by `2D_OMNIFOLD_REFERENCE.md:239-241` — the same split, not a second measurement. A cluster read |
| 5 | **`PM-2`** — G's `combined_source` sha256, **read from the file** | **YES.** Without it Z's parent chain has a definite description where it needs a digest | **YES** | **NO, and the near-miss must be named.** `std_component_manifest.json` records `support_family_sha256 = 9f7b2f55…` for **the same path**, but S read it 2026-08-16 and G was built 2026-08-12. **Using S's digest as G's is the substitution `PM-2` exists to prevent** |
| 6 | **`PM-3`** — availability, provenance and **grid/footing compatibility** of the ten selection-complete endpoints | **YES.** They are `L_active`'s inputs | **YES** | **PARTLY, and rev. 2 narrows what the evidence shows.** `RECEIPT-20260816` records all 20 stage-1/2 tags **SKIPPED** as of 2026-08-16 and `DETERMINATION-20260811` records the samples *"Gate-3 promoted… since 2026-07-20"*. **Historical SKIPs establish neither present availability nor mandatory retraining** — the reviewer's formulation. A cluster `ls` plus digest and footing check; a **rebuild is priced only if that check fails** (§5.5) |
| 7 | **`PM-4`** — G's mask digest and row-order digest, read from G | **YES.** §1.3's invariant is unassertable without them, and without it every `M` comparison is over two populations | **YES** | **NO.** S's `reported_mask_hash`/`row_index_sha256` are **S's**, and `row_index_basis` warns that *"builds before [2026-08-10] lack it"* — G is 2026-08-12, so it plausibly carries `hRowIndex5D`, but that is an inference, not a read |
| 8 | **`PM-5` (NEW in rev. 2)** — the `V`/`R`/`A` partition measured against G's own `combined_source` band inventory | **YES.** §1.3a's disjointness-and-exhaustiveness gate cannot be written against an unmeasured family | **YES** | **PARTLY.** `VERT_BANDS` (13) and `p4_lib.BANDS` (5) are committed constants; S's manifest gives 45 `all_syst_bands`. **But that is S's family read, not G's**, and `R`'s membership is a *complement*, so it is only as good as the family list. A cluster read closes it |
| 9 | **The cause-4 jitter-print re-add**, with §2.4's four conditions | **YES.** The only route by which `(cause 4, Z)`'s `M` can be anything but permanently unmeetable | **YES — the property Z has and G cannot.** The obstruction is a property of the committed history, and this base descends from `081ae4ac` | **NO — code that does not exist.** The *specification* of what to re-add **is** reusable: `a0cdc019:232-252`, recovered and committed |
| 10 | **The four inflation gates of §1.3b** | **YES.** Without them Z's inflated object has no closure check at all, and the one that catches a double-counted `V` does not exist | **YES** | **NO — new code.** `adopt_unified_5d.py` computes the quantities; nothing asserts the identity |
| 11 | **Extending the cause-3 seed guard to the dominant block** | **YES** for `(cause 3, Z)`'s `C`. Today *"the single-seed property of the dominant block holds by hardcoding and is checked by nothing"* | **YES** | **NO — new code.** But **half already landed**: `sweep_bank_5d.py:358`'s flag and `:309`'s stamp exist. What remains is the *refusal*, not the *stamp* |
| 12 | **The cause-3 throw-leg seed/draw separation** | **NO — already done.** `unified_throw_cov.py:630/:634`, both `required=True`; `:477-479` and `:483-485` refuse mixed estimator and incoherent draw seeds | **YES** | **YES, zero compute.** Landed `3dd5e66e`, 2026-08-18, an ancestor. **`SCOREBOARD` §2b's *"unsatisfiable"* is superseded** |
| 13 | **A bidirectional projection-coverage repair** | **NO — WITHDRAWN, it already exists** (§2.6a). `p4_lib.build_projection_M:1353` is fail-closed both ways (BEN-064, 2026-08-09) with `reachable_low_mask:1322` as the contract correction (2026-08-10); `eavailW_covariance.py:407-432` is guarded and **deliberately not** fail-closed | **YES** | **YES, zero compute.** What Z needs instead is to **preserve the asymmetry and evidence both censuses** |
| 14 | **The standard-P4 validator's 11 gates as Z's cause-7 `C`/`T` machinery** | **NO as a prerequisite; YES as reuse** | **YES for the BLOCK-SUM identities**, already PASSed on a 10,694-bin object (`full_total_identity_relerr = 4.6e-14`). **NOT for the inflated object** — §1.3b's four gates are outside its scope | **YES for what it covers, zero compute.** What is **not** reusable is the *verdict*: S's PASS is evidence about S |
| 15 | **The cause-5 construction-path re-trace on Z's own path** | **YES** for `(cause 5, Z)`, and §6.1 makes it the **precondition of the ruled disposal** | **PARTLY.** The *reasoning* transfers; the *coverage* does not — Z's path is a superset and runs through `adopt_unified_5d.py`, which `VL66` did not audit | **YES, zero compute** — a static read. **But not by cause 5's owner**, per `VL66`'s own weighting caveat |
| 16 | **Cause 1's completed magnitude measurement** (both one-sided choices, off-diagonal, non-pair bands accounted) | **YES** for `(cause 1, Z)`'s `M`, and §6.2 fixes its form | **YES** — a property of the bank Z rebuilds | **NO.** A measurement on Z's own bank. **No unfold**: the census reads `uq_5d/universe_sweep_bkgaware/…` outputs, so the marginal cost is post-processing, not GPU — but **off-diagonal means full `10,694²` per band**, which is a real memory/CPU cost this lane has not sized |
| 17 | **Cause 1's disclosure** (`RULING 1`'s note obligation) | **YES**, and §6.2 makes it part of closure | **YES** | **NO** — and writing it is a **publication act outside `RZ(iv)`** |
| 18 | **A vocabulary decision on `N/A`** | **NO — CLOSED.** `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` (`e59df955…`): no fourth token. **Rev. 1 proposed one; that was a miss** | n/a | n/a. §6.1's per-cell disposal is the route, and it needs no `§0` change |
| 19 | **`D-RESOURCE`** — an exact resource authorization naming a Z run (`R5`) | **YES** for construction; **NO** for this specification | **YES** | **NO — it does not exist.** `R5`'s ceilings are *"NOT authorization to spend up to"* them |
| 20 | **Two independent pre-launch reviews** (`PLAN-20260905` #17) | **YES** for a construction Z's grade can rest on. Worker agreement is not independence | **YES** | **NO.** The prompts are committed and reusable as method; the reviews are not done |
| 21 | **An independent ARTIFACT REPLAY from digest-bound artifacts** (`PLAN` #19) | **YES**, and rev. 2 narrows what it is: *"cold checkout, no producer helpers"* means **no producer code paths**, **not** retraining | **YES** | **NO**, but it is **not a second production campaign** — §5.3. Rev. 1's automatic doubling is withdrawn |
| 22 | **A grading lane `BEN-381` does not disqualify** | **YES.** This lane is disqualified by drafting; the cause-4 measuring lanes by `DECISION-20260902-…-oi173` §3 | **YES** | **YES, zero compute** — a routing act |

## 4.1 The two authorization facts, stated so no dependency claim launders them

1. **Constructing Y requires `D-Y-CONSTRUCT` (`R2(iv)`). It does not exist.** This analysis finds Y is
   **not** a Z prerequisite (row 1). If a later plan asserts one, the assertion does not create authority.
2. **The cause-3 narrow scan requires BOTH `D-C3-VOI` and `D-C3-RUN` (`R4`), and its launch authorization
   is SUSPENDED.** This analysis finds it is **not** a Z prerequisite (row 2), and §6.3 makes it
   diagnostic for Z. **A Z schedule that assumes it will run is asserting a decision Joseph has not
   taken.** The reviewer's related point is adopted: **substitution is not a third prerequisite for the
   historical narrow scan** — permission to *measure* and permission to *substitute* are different acts,
   and the off-branch `VOI-20260906` at `47494dbe` distinguishes them correctly.

**The honest converse, as a finding rather than a plan:** this analysis does **not** find that Z needs
either suspended item. What Z needs and does not have are rows 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17,
19, 20, 21 — of which **row 19 is Joseph's decision, not work**, and **row 3 is the fail-closed gate on
every row that costs compute**.

---

# 5. COSTED EXECUTION PROPOSAL — deliverable `RZ(v)(e)`

**An estimate for a decision. Not a bid, not a request, not an authorization.** `RZ(iv)` withholds
compute; `R5`'s ceilings are a prohibition, not a budget to spend.

## 5.1 The anchor, and what it is an anchor for

**The only ratified anchor is a complete seven-arm k=0 rehearsal round at `70` GPU / `113` CPU
task-hours** (`AMENDMENT-20260831-oi177` §5, ratified 2026-09-01 — *"I sign"*), against `R5`'s `500`/`500`.
The reviewer confirms it is a valid ratified ceiling anchor. Three things about it:

- **`70`/`113` is the RATIFIED CEILING SUM, not a measured actual.** Summing §5's own columns:
  **round 1 = `54.80` GPU / `66.80` CPU; round 2 = `54.90` GPU / `86.53` CPU.** Using the ceiling is the
  conservative choice and this proposal uses it; a reader comparing to an actual compares to `~55` GPU /
  `67–87` CPU.
- **`k=0` is a MEMBER INDEX, not a reduced-iteration configuration** —
  `PROPOSAL-20260830-forward-only-rehearsal.md`: *"k=0 is the anchor and the only member with an archive
  comparand."* So the anchor is a **full-scale** seven-arm production round, which is what makes it
  transferable to Z at all.
- **Arm 2 "seed split" is the ML-split replica arm, not any estimator-seed scan.** Measured:
  `sbatch_seedscan_split_5d.sh:300` writes `seedscan_split_5d/res_split_<id>.npz`, and
  `sbatch_combine_5d_budget.sh:16-17` turns that glob into `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported`
  — **`C_ML`**. Conflating it with a cause-3 scan on the shared word *"seed"* double-counts one and omits
  the other. The off-branch `VOI-20260906` records the same collision independently.

## 5.2 One Z build

| item | GPU task-h | CPU task-h | basis, and how firm |
|---|---:|---:|---|
| seven-arm production round | **70** | **113** | ratified **ceiling** sum `20+20+30` / `8+60+40+5`. Firm as a ceiling; conservative against both actuals. **Contains the statistical replica ensemble (arm 1) and the ML-split ensemble (arm 2)** |
| standard-P4 lateral stages 3–6 | **3.00** | 0 | **corrected in rev. 2 — see §5.2a.** The observed instance metered at the parent task's `03:00:03`; the step's `00:47:58` is a runtime floor, not R5 spend. Assumes stages 1–2 skip, **conditional on `PM-3`** |
| statistical + ML **combine** | 0 | **≤ 1.0** | `sbatch_combine_5d_budget.sh` — **not one of the seven arms** (grep over the proposal and the amendment returns nothing). Its own header requests `--qos=shared --constraint=cpu --ntasks=1 --time=01:00:00`, so `1.0` is a wall-clock ceiling, not a measurement. It performs **both** `combine_cov_nd.py` calls and `analyze_universes_5d.py` |
| **inflated assembly, both variants** | 0 | **≤ 4.0** | **missing from rev. 1.** `sbatch_j28_adopt_5d.sh` — `--qos=shared --constraint=cpu --ntasks=1 --time=04:00:00`, running `adopt_unified_5d.py` twice (`:111` mean-centered, `:113` `--cv-centered`) plus the rescale step. **Not one of the seven arms.** Wall-clock ceiling, not a measurement |
| cause-4 `--null` extra CV unfold | 0 | **absorbed** | **corrected in rev. 2.** `--null` runs in the **CPU** combine (`sbatch_j28_adopt_5d.sh:98`; arm 7 `sbatch_uthrow_combine_5d_fast.sh`, `--constraint=cpu`). Arm 7's ratified ceiling is `5` CPU against measured actuals `0.42`/`0.58` — **~8× headroom** — so one extra unfold is expected to be absorbed. **If it is not, the ceiling is the bound** |
| cause-1 counterfactual, incl. off-diagonal | 0 | **unpriced** | post-processing of `uq_5d/universe_sweep_bkgaware/…` outputs (`receipt_cause1_endpoint_census_5d.json`, `inputs.glob`) — **no unfold**. But off-diagonal means full `10,694²` per band; this lane did not size it |
| validation and 4D projection | — | — | **inside** the stages 3–6 line: `RECEIPT-20260816` records stage 5 (11 gates) and stage 6 in that chain |
| **ONE Z BUILD** | **73.0** | **≤ 118.0** | **`14.6%` of `R5`'s GPU ceiling; `≤23.6%` of its CPU ceiling** |

### 5.2a The scheduler-accounting correction, because it changed the number

Rev. 1 priced stages 3–6 at `0.80` GPU task-hours from step `57128458.1`'s `00:47:58`. **That is a
runtime prior, not R5 spend, and the reviewer is right to separate them:**

- `r5_meter._calculate_spend` (`docs/orchestration/r5_meter.py:277`) sums `ElapsedRaw` over **distinct
  task identities**, with step rows excluded by `_parse_sacct_dump` (asserted by
  `test_steps_extern_and_array_bracket_rows_are_excluded`). **So R5 meters the parent task, not the
  step.**
- The parent's own record: `RECEIPT-20260816-p4-standard-stages456.json` `job_later_TIMED_OUT` —
  *"2026-08-16T18:37:31 after 03:00:03, AFTER this chain completed"*. **Metered, that instance is `3.00`
  task-hours, not `0.80`.**
- **And it predates `t0` (`2026-09-02T13:44:27Z`), so it contributes nothing to actual R5 consumption.**
  It is a prior for planning, and nothing else.

**Consequence for a Z plan:** the metered cost of this step is the **wall request**, not the runtime. A
right-sized request (say `--time=01:30:00` against a 48-minute chain) meters near `1.0`–`1.5`; dispatching
inside a 3-hour hold meters `3.00`. This proposal prices the observed `3.00` and notes the lever.

**Rev. 1 also stated this backwards in its own §5.6.** It described `RUNS.tsv:321`'s allocation-level
`node_h=6.00` as a `7.5×` error against `0.80`. Under `R5`'s unit the **allocation-level view is the
closer one**, and the step-level figure was the misleading one. Corrected here.

## 5.3 The campaign, not the build

| scenario | GPU task-h | CPU task-h | vs. `R5` 500/500 |
|---|---:|---:|---|
| one Z build | `73.0` | `≤118.0` | `14.6%` / `≤23.6%` |
| **+ independent ARTIFACT REPLAY** | **not a production round** | **not a production round** | see below |
| + optional independent **regeneration**, if separately proposed and authorized | `146.0` | `≤236.0` | `29.2%` / `≤47.2%` |

**Rev. 1's automatic doubling to `143`/`226` is WITHDRAWN.** The reviewer's correction: *"price
independent reconstruction from digest-bound artifacts separately. 'Cold checkout, no producer helpers'
does not require retraining."* `PLAN-20260905` #19 asks for an independent replay; **replaying the
identities from Z's digest-bound components is verification work, not a second production campaign.** Its
cost is reading and recomputing `10,694²` matrices from committed digests — CPU, bounded by the same
shape as the combine and the assembly, and **this lane has not sized it**. A second full regeneration
**may be proposed** and is priced above, but **it is not a mandatory replay cost** and rev. 1 was wrong
to treat it as one.

**Time, measured rather than recalled.** At `2026-09-05T22:46Z` the `R5` stop (`2026-09-30T00:00:00Z`,
inclusive) was **24 days 1 hour** away; `3 days 9 hours` had elapsed since `t0 = 2026-09-02T13:44:27Z`
(`9ce59a59`). **The date binds and the ceilings are the backstop** — `DECISION-20260902` §1's own reading
of the pairing Joseph selected. Nothing here reopens it.

## 5.4 Cause 3's magnitude, priced against the RULED quantity

**Rev. 1 claimed a "`≈4.5×` scope fork". That is WITHDRAWN: it divided two figures with different
populations.** The three figures in play, each with its own scope:

| figure | what it actually prices | population |
|---|---|---|
| `8.7` GPU (worst `18`), `0.08` CPU | **12 CV unfolds** at 12 estimator seeds, one fixed data/MC draw, **on G's footing** | the narrow fixed-draw scan |
| `39.223` GPU / `55.337` CPU | **one additional estimator seed on the `C_syst` sweep/detector arms only** — `23.840 + 14.2075 + 1.030 = 39.078`, plus `0.1458` (`SCOPE-20260818-gate1-seed-separation-two-keys.md` `:22`, `:340`, **derived at neither site**) | a partial-arm increment |
| **`54.90` GPU / `86.53` CPU** | **one complete seven-arm member round**, round-2 actuals | **the joint-baseline composite — the quantity §6.3 rules for Z** |

**No ratio among these three is a scope comparison.** The off-branch `VOI-20260906` at `47494dbe`
identifies the same trap and records that its own earlier use of the letter `Z` for the composite scan
would *"attribute a `39.223`/`55.337`-per-seed scan price"* to the wrong object.

**What §6.3's ruled quantity would cost, at the design that is NOT assumed.** A joint-baseline composite
is measured over **members**, each a complete seven-arm round:

- at the historical family sizes, `46 × (54.90, 86.53) = **2,525** GPU + **3,980** CPU`, and
  `50 × … = **2,745** + **4,326**` — **5× to 9× over `R5`'s `500`/`500`**, i.e. **out of reach inside
  this campaign entirely**;
- **§6.3 explicitly does not adopt 46/50 as the necessary design.** A smaller, purpose-built design is
  what Z's cause-3 specification must produce, and **this lane does not propose one** — that is a
  measurement-design question with a scientific answer, not an arithmetic one.

**So the honest statement is:** `(cause 3, Z)`'s `M(ii)` as ruled is **not affordable at the historical
family size inside `R5`**, and its affordability at a smaller design is **unknown until the design
exists**. That is a finding for Joseph, not a plan (§7 item 3).

## 5.5 Conditional and unpriced items, named rather than absorbed

- **Endpoint rebuild.** Priced **only if** `PM-3`'s availability, provenance or compatibility checks
  fail. **Historical SKIPs establish neither present availability nor mandatory retraining**, so a
  rebuild is neither assumed nor pre-costed here.
- **Cause-1 off-diagonal counterfactual** — §5.2, unsized.
- **Artifact replay** — §5.3, unsized.
- **The four inflation gates and the cause-3 dominant-block refusal** — code, not compute.
- **A joint-baseline design for `(cause 3, Z)`** — §5.4.

## 5.6 The meter gap, named in the proposal as the brief requires

**The instrument is built and admission is fail-closed. The ceilings have never been measured against
the scheduler.** Measured at this base:

- `docs/orchestration/r5_meter.py` exists (27,357 B) and encodes `R5` exactly: `T0_UTC_TEXT =
  "2026-09-02T13:44:27Z"` (`:33`), `STOP_DATE_UTC_TEXT = "2026-09-30T00:00:00Z"` (`:37`),
  `GPU_TASK_HOURS_CEILING = CPU_TASK_HOURS_CEILING = 500.0` (`:41-42`), task-hours with t0 clipping.
- `docs/orchestration/campaignctl.py` exists (204,141 B); admission is fail-closed.
- **`docs/orchestration/state/r5-meter-receipt.json` DOES NOT EXIST.** Measured, not recalled. The
  reviewer confirms: *"No operational meter receipt is committed at either reviewed revision."*
- `test_r5_meter.py`: **18 tests, all passing** — **on three checked-in fixtures**
  (`test_fixtures_r5_meter/{mixed,perlmutter_regular_gpu,rows_vs_identities}.sacct`) that are
  **hand-authored, not captured** (job ids `50000`/`60000`, task names `task-0`,
  `reviewer-regular-gpu`). **The parser is tested; the deployment is not**, and a fixture authored beside
  its parser cannot disagree with it.
- `_sacct_argv()` (`:380-392`) requests `JobID,JobName,State,ElapsedRaw,Partition,Start,End,AllocTRES`
  for the current user from t0 to now. **Whether real Perlmutter `sacct` output parses cleanly through
  it is unmeasured.**
- **No unattended execution is configured** (`ACCEPTANCE-20260905`; the credential decision is Joseph's
  or the site owner's).

**Consequence:** *"The queue admits no item at all until a receipt measured on Perlmutter is committed,
and none is."* **A first receipt is a prerequisite to any Z campaign and is itself an uncosted item** —
a login-node `sacct` query plus a commit, so its **task-hour** cost is ≈0, but its credential and
authorization cost is not this lane's to price. **Do not infer the meter is deployment-ready.**

**And the other production prerequisites, per the reviewer:** measured headroom, compatible input
identities (`PM-2`, `PM-3`, `PM-5`), and an explicit run authorization (`D-RESOURCE`). None exists.

## 5.7 The uncertainty on all of the above

1. **No Z arm has ever run.** Every figure is transferred from a different product's arms. This dominates
   and no arithmetic here reduces it.
2. **CPU-partition arms are demonstrably not reproducible across scheduler regimes.** `AMENDMENT` §3c/§3e
   establish it and the measurement is stark: arm 5 went `30.94 → 49.11` between rounds, **+58.7% on one
   arm**, and the amendment says *"a third run may exceed them."* **Treat the CPU column as carrying at
   least a ±60% single-arm swing.**
3. **Three of the four non-arm lines are WALL REQUESTS, not measurements** — the combine (`≤1.0`), the
   assembly (`≤4.0`), and the metered stages-3–6 figure (`3.00`). They are upper bounds by construction
   and will over-state a well-sized campaign.
4. **Failed and retried tasks count in full** under `R5` §3, including `FAILED`, `CANCELLED` and
   `TIMEOUT`. A single failed pass spends its full elapsed time and produces no Z.
5. **Two build lines are unsized** (§5.5), and `(cause 3, Z)`'s ruled quantity has **no design and
   therefore no cost** (§5.4).

---

# 6. THE RULINGS — taken 2026-09-06 on the contract review's recommendations

**These are DECIDED, not proposed.** §0.2 records the authority and how it was given. **The
recommendation text is the REVIEWER's, quoted verbatim; the adoption is Joseph's.** §§1–5 already
incorporate them; this section is where they are recorded so a citation has one home.

**None of them extends `CRITERIA` §0's vocabulary, and none regrades G.**

## 6.1 `(cause 5, Z)` — an artifact-specific "INAPPLICABLE, DISPOSED BY DECISION" outcome is authorized

**The question put:** *"Can independently demonstrated absence of PET-derived inputs terminally dispose
of (cause 5, Z) without four artificial METs?"*

**The recommendation, adopted:**

> *"Authorize an artifact-specific 'inapplicable, disposed by decision' outcome after the complete trace
> and falsifier check. Preserve historical cells and distinguish this from mechanical four-MET discharge.
> RZ requires seven assessments, not seven favourable results."*

**RULED.** `(cause 5, Z)` may be terminally disposed as **`INAPPLICABLE — disposed by decision`**, on
these conditions, all of which are part of the outcome and none of which this record discharges:

1. the **complete construction-path trace** over every module Z invokes — including
   `adopt_unified_5d.py`, which `VL66` did not audit and which `D_Z` runs through (§2.5);
2. the **falsifier check** — no PET-derived product consumed by any module on Z's path;
3. performed by a lane that does **not** own cause 5, per `VL66`'s own weighting caveat;
4. recorded as **distinct from a mechanical four-MET discharge**, with the distinction visible in the
   cell rather than inferable from it;
5. **G's and Y's historical cells untouched.**

**Why this needed a ruling, and why rev. 1's proposed route was wrong.** `CRITERIA` §3:246 admits only
`MET`/`OPEN`/`UNRESOLVED` and discharges only on four METs; `SCOREBOARD` §7b **RULED 2026-08-17** that a
leg outside those three *"can never discharge."* So a cause-5 `N/A` blocks a mechanical seven-MET Z.
**Rev. 1 offered "define a fourth token." That route was already closed on 2026-09-02** —
`DECISION-20260902-joseph-rules-no-fourth-grade-token.md` (`e59df9557e6ec1d21b845d7647c0038662c490713d8a43b2f72cd60bd34dc477`),
Joseph, *"okay I also agree"*: *"`CRITERIA-20260811` §0's vocabulary — `MET` / `OPEN` / `UNRESOLVED`,
discharge on four `MET`s — STANDS UNCHANGED. No token is added for the *permanently unmeetable*
state."* **That record is in this tree and rev. 1 did not open it.** The miss is recorded here rather
than quietly repaired.

**This ruling does NOT reopen it.** It adds no token. It is a **per-cell decision**, and the framework
already distinguishes that from a mechanical discharge: cause 2's CAND cell is *"discharged **by
decision**"* (Joseph, 2026-08-12) while the board's counts table keeps *"causes with four METs"* at
**`0`**. `RZ(ii)` asks for seven **assessments**; a complete assessment whose honest outcome is
"inapplicable" is an assessment, not a gap.

## 6.2 `(cause 1, Z)` — measure-and-disclose closure, irrespective of magnitude

**The question put:** *"Does a complete, artifact-specific measurement plus the required disclosure
permit closure for Z irrespective of magnitude, and what counterfactual applies to non-pair bands?"*

**The recommendation, adopted:**

> *"Permit measure-and-disclose closure once independently verified. Compare both one-sided choices for
> actual ± pairs, including off-diagonal effects and denominator qualifications. Explicitly account for
> the other bands without inventing ± endpoints. The original receipt already includes Flux,
> three-universe 2p2h and normalization unchanged in both totals; changing their construction is a
> proposed criterion extension, not merely filling missing arithmetic."*

**RULED.** `(cause 1, Z)` closes on a **complete, artifact-specific measurement plus the `RULING 1`
disclosure**, **irrespective of magnitude**, once **independently verified**. The measurement's form is
§2.1's six requirements. **The three non-pair bands are accounted for explicitly and their endpoints are
NOT invented**; any change to their construction is a **criterion extension** requiring its own decision,
and this specification does not make one.

**Consistency with `RULING 1`, stated because it is the obvious challenge.** `RULING 1` (2026-09-01)
found cause 1's magnitude *"material enough to need its own statement in the note"* and therefore did not
close cause 1 **for G**. This ruling does not disturb that: G's cell is unchanged, and the note obligation
is not waived — it becomes part of **Z's** closure condition. What is settled is the question `RULING 1`
left open: **that for a new artifact, a complete measurement plus the disclosure suffices, and magnitude
alone does not block.** Writing the disclosure remains a publication act outside `RZ(iv)`.

## 6.3 `(cause 3, Z)` — the joint-baseline quantity, with the narrow scan diagnostic

**The question put:** *"What quantity and outcome rule closes Z's estimator-seed magnitude leg: the
narrow fixed-draw measurement, or variation of the assembled covariance with estimator baselines varied
jointly?"*

**The recommendation, adopted:**

> *"Retain the joint-baseline quantity for a claim about composite Z; do not assume the existing
> 46/50-member family is the necessary measurement design. Treat the narrow scan as diagnostic unless
> substitution is explicitly ruled. Specify favourable, unfavourable and inconclusive outcomes before
> measurement."*

**RULED**, in four parts:

1. **The quantity** for `(cause 3, Z)`'s `M(ii)` is the variation of the **assembled** covariance `C_Z`
   when the sweep-side and throw-side estimator baselines are varied **jointly** — `SCOREBOARD` §2c's
   `(B)`, applied to Z.
2. **The design is open.** The existing 46/50-member family is **not** assumed to be the necessary
   measurement design. §5.4 prices it at 5×–9× over `R5` precisely so that the design question is put
   before the money is.
3. **The narrow fixed-draw scan is DIAGNOSTIC for Z**, not `M(ii)`, **unless substitution is explicitly
   ruled** — which this record does not do. That preserves
   `PREDECLARE-20260901-cause3-mii` §5's own reservation: *"treating it as a substitute for a full
   two-baseline composite scan would require a separate ruling."*
4. **Three outcome classes — favourable, unfavourable, inconclusive — are specified BEFORE measurement**,
   on §4's six-branch model, which `R4` preserves. **A valid large result is not automatically MET.**

**This ruling touches neither `R4` nor the narrow scan's own criterion.** `R4`'s suspension stands;
§1's quantity, §2's footing falsifiers, §3's thresholds `f_agg ≤ 0.0415` / `f_med ≤ 0.0274` and §4's six
branches are preserved exactly. **And permission to measure is not permission to substitute** —
substitution is **not** a third prerequisite for the historical narrow scan, and nothing here adds one.

## 6.4 A scale-relative fixed-seed null bound for Z, fixed before production

**The question put:** *"Should Z use a scale-relative null bound, fixed before production?"*

**The recommendation, adopted:**

> *"Yes, with the numerical bound justified by precision and sensitivity controls before implementation
> — not selected from a favourable production result. This does not retrospectively regrade G."*

**RULED.** Z's fixed-seed null uses a **scale-relative** bound, **fixed before production**, with its
numerical value justified by **precision and sensitivity controls established before implementation** and
**not** chosen from a favourable production result.

**The measured defect this replaces** is §3.1a: `unified_throw_cov.py:517`'s
`tol = 1e-12 * max(‖base‖, 1.0)` evaluates to an **absolute `1e-12`** on a cross-section vector whose norm
is order `1e-37`, so it is roughly `10^25` times the scale it is meant to bound. **It is not a relative
determinism bound.** Choosing Z's bound after seeing Z's null would be a threshold placed to obtain a
verdict — the failure `PREDECLARE-20260901-cause7` §1 `M` and `uq_math.py:128-137` both name.

**This does not retrospectively regrade G**, and it is not a finding that G's null is bad: G's measured
value is `5.8223e-50`, `1.31e-12` of the sqrt-trace — genuinely small *relative* to the scale. **The
defect is in the guard, not in the product.**

## 6.5 WITHDRAWN — the multi-draw cause-4 proposal

Rev. 1 §6.2 asked whether `(cause 4, Z)`'s `M` should require `n > 1` jitter draws. **Withdrawn**, on the
review's directive, adopted: *"Keep cause 4's single-draw referent; requiring multiple draws would be a
separate, optional criterion change."*

The reason is the one rev. 1 gave against its own proposal: **the defect cause 4 names *is* a single-draw
subtraction**, so a multi-draw `M` measures something the defective construction never did. §2.4 retains
the single draw, with its seed named and its one-sample nature stated in the receipt. **Anyone who wants
the multi-draw variant should raise it as a separate, optional criterion change; it is not part of this
contract and nothing in §§1–5 depends on it.**

## 6.6 What remains a criterion question and is NOT ruled here

- **Whether the three non-pair bands' construction should change** (§6.2) — a criterion extension nobody
  has proposed and this lane does not.
- **Whether the narrow fixed-draw scan may SUBSTITUTE for the joint-baseline quantity** (§6.3) — reserved,
  by `PREDECLARE-20260901-cause3-mii` §5's own terms.
- **Whether `(cause 6, Z)` is graded on `6a` as well as `6b`** (§2.6c item 5) — a scoping call for the
  grading lane, to be made explicitly rather than inherited.
- **Whether Z regenerates or reuses `C_stat`/`C_ML`** (§2.6b) — a **scientific** decision needing a
  stated rationale, not a criterion change.
- **Reconciling `CRITERIA` §0's declared-three-against-used-seven vocabulary** — named by
  `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` §3 as *"the better-motivated change"* **if**
  §0 is ever opened. It is not opened here.

---

# 7. WHAT THIS LANE COULD NOT ESTABLISH, AND WHAT IT WOULD TAKE

1. **`PM-1`, `PM-2`, `PM-3`, `PM-4`, `PM-5`.** All five are reads of cluster-resident ROOTs this checkout
   does not carry (`*.root` is `.gitignore`d). **What it would take:** five cluster reads under an
   existing session, costed against `R5`'s meter — which itself needs §4 row 3 first.
2. **Whether S's `support_family_sha256` is G's `combined_source` digest.** Same path, reads four days
   apart, nothing binding them. **What it would take:** `PM-2`.
3. **A measurement design for `(cause 3, Z)`'s ruled joint-baseline quantity.** §6.3 fixes the *quantity*
   and explicitly does not fix the *design*; §5.4 shows the historical family size is **5×–9× over
   `R5`**, so the design is the whole question. **What it would take:** a measurement-design proposal
   with a scientific rationale for its member count and offsets — not arithmetic, and **not this lane's**,
   since `BEN-381` will disqualify whoever drafts it from grading the leg.
4. **The numerical value of §6.4's scale-relative null bound.** The ruling fixes the *form* and forbids
   choosing it from a result; the value awaits the precision and sensitivity controls it must be
   justified by. **What it would take:** those controls, before implementation.
5. **The cost of the cause-1 off-diagonal counterfactual and of the artifact replay.** Both are
   post-processing on `10,694²` matrices; neither needs an unfold; neither was sized here. **What it
   would take:** a memory/wall-clock estimate against the reported-bin dimension.
6. **Whether real Perlmutter `sacct` output parses through `r5_meter._parse_sacct_dump`.** 18 tests pass
   on hand-authored fixtures, and a fixture written beside its parser cannot disagree with it. **What it
   would take:** one login-node `sacct` capture — the same act as §4 row 3.
7. **Two control-document discrepancies, left standing.** `CRITERIA` vs `SCOREBOARD` on cause 4's `M`
   (`UNRESOLVED` vs `OPEN`), already filed by `DECISION-20260902-…-oi173` §6 as *"a finding owned by
   neither lane"*; and on cause 2's `T` (*"absent"* vs `MET`) (§2.2). **What it would take:** an owner
   for the two control documents.
8. **Whether `CRITERIA` §2 cause 6's *"unrepaired instance in current code"* should now be amended.**
   §2.6a measures it stale on both projectors. **This lane does not edit `CRITERIA`**; the finding is
   surfaced for its owner.
9. **RESOLVED during rev. 1 drafting, kept because it changed §5.** The cause-6 statistical **ensemble**
   is arm 1 (`sbatch_bootstrap_5d_gpu.sh:313` → `boot_nd_5d/res_boot_*.npz`, consumed by
   `sbatch_combine_5d_budget.sh:14-15` at `--expected-ids 1-100 --tag stat5d`) and **is** inside the
   seven-arm anchor; the **combine** is not, and is priced separately. **Still unestablished:** whether
   that `≤1.0` is representative. `grep` over `RUNS.tsv` for `budget5d` and `combine_5d_budget` returns
   **0** rows against a positive control on the same file (`57128458` → `:321`), so the ledger carries no
   accounting for it. **What it would take:** one `sacct` read.

---

# 8. WHAT THIS RECORD DOES NOT DO

It constructs nothing, implements nothing, launches nothing, spends nothing, grades no leg, discharges no
cause, adopts no artifact, moves no count and no gate, opens no `SCOREBOARD` cell, licenses no
projection, touches no publication claim and no `values.tex`, authorizes no submission, closes no `OI-*`,
and writes no scheduler state.

**It does not extend `CRITERIA` §0's grade vocabulary.**
`DECISION-20260902-joseph-rules-no-fourth-grade-token.md` stands; §6.1 is a per-cell decision on cause 2's
own precedent and adds no token. It does not retrospectively regrade G on any leg — §6.4 in particular is
a forward requirement on Z and explicitly not a re-grade.

It does not widen Y, does not rename Y as Z, and does not create Z's cells — `RZ(ii)` constrains a future
assessment and does not create one. It does not combine Z's prospective grades with G's or Y's in any
direction. It does not promote S, does not find S adoptable, and leaves `VL68`'s *"built is not adopted"*
standing unchanged. It does not reopen `R5`: the accounting start `2026-09-02T13:44:27Z` (`9ce59a59`),
both `500` task-hour ceilings and the `2026-09-30` stop are preserved exactly, and no new cap, accounting
start or extension is proposed. It is **not** `D-C3-VOI` and **not** `D-C3-RUN`; `R4`'s suspension stands
and §6.3 does not touch it. It does not authorize the historical narrow scan, and it does not rule
substitution. It does not alter PET's diagnostic status under `R6`; Gate 6 stays BLOCKED under its five
prohibition keys.

It does not perform `RZ` §5's owner applications, and it does not edit `CRITERIA`, `SCOREBOARD`, `MAP`,
`OPEN_ITEMS`, `VALIDATION_LEDGER`, `PLAN-20260905`, either 2026-09-06 decision record, or anything on the
off-branch `lane/cause3-voi-20260906`.

It regenerates no state: `OI-73`'s hold stands and `generate_live_state.py --check-freshness` reports
STALE at this base by design.

**And it does not grade the legs it defines.** `BEN-381`; see the header. That applies to the four
rulings too: they fix criteria and outcomes, and the lane that drafted them grades nothing under them.
