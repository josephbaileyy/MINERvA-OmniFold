# SCOPING — `C_syst`, the joint per-nuisance retraining component (OI-3 / quarantine cause 5)

**Design only. Nothing here is executed, nothing is submitted, and no cluster state is mutated.** This
document does not discharge cause 5, does not build the construction, and makes no PET magnitude
quotable. It answers one question the campaign currently cannot answer: **what would it take.**

**Scope boundary that governs every number below.** Every measured magnitude in §2 and §3 comes from
**RECOIL-representation** products. Per the 2026-08-01 full-event landing, every pre-08-01 PET number is
a **different estimator**, so **no magnitude here transfers to the full-event budget.** What transfers is
the *sign*, the *rough size*, and the *structure* — as design inputs. Where I use a recoil number to size
a full-event decision I say so at that point, not in a footnote.

Written by Lane B while Gate 6 Leg F's draw 5 is queued. **Gate 6 remains BLOCKED at `19585b7`** with all
five prohibitions live; nothing here touches it, and `C_ML` still needs a decision Joseph has not made.

---

## 1. What `C_syst` must measure, stated so it could be falsified

For each nuisance endpoint `u`, the component is built from **one** joint displacement:

    δ_u  =  x_u^{varied + retrained}  −  x_CV

where `x` is the extracted cross-section vector on the reported 5D bins, `x_CV` is the adopted P5A
central, and *"varied + retrained"* means the physical variation is applied to the estimator's **training
inputs** and a **fresh reweighter is trained on the varied prior**, then the cross section is extracted
through **that** map.

**What varies:** the nuisance's per-event truth prior (verticals) or the selected point cloud itself
(laterals — a different component, see §2.4). **What is held:** the reported bin set and order, the mask,
the `pet-fullevent-fps-v1` fingerprint, the target-normalization contract, `niter`, `epochs`,
`train_events`, `batch_size`, and — this is the part that makes it a *systematic* rather than a
seed study — **the seed pair.**

**What the estimator sees here that it does not see for `C_stat`:** `C_stat` varies the *data* (coherent
Poisson draws over the complete inventory) and leaves the MC prior alone. `C_syst` varies the **MC prior**
and leaves the data alone. Both retrain; they are not the same displacement, and they are not the same
noise. The distinction matters operationally because `C_stat`'s replicas each need their own target
(hence Gate 5's CPU target array feeding a GPU training array), whereas a vertical `C_syst` endpoint
reuses the **same input cloud** with a different per-event weight vector — no new event loop, no new dump.

**The falsifiable form, and the reason it is not the frozen-map construction.** Writing
`δ_u = s_u + Δ_u` with `s_u = x_frozen − CV` and `Δ_u = x_retrain − x_frozen` is an algebraic identity,
but

    outer(δ,δ) = outer(s,s) + outer(Δ,Δ) + outer(s,Δ) + outer(Δ,s)

and summing a frozen-map `C_syst` with a separate `C_retrain` block keeps the first two terms and drops
the cross terms. **PSD-ness of the sum does not restore them.** So the component is falsified if any of
these fails, each mechanically checkable:

1. Every quoted endpoint stores `δ_u` formed as **one object**, recomputed as `x_retrain − x_CV` and
   **never** as `s_u + Δ_u`. A receipt publishing `s_u` and `Δ_u` separately does **not** satisfy this
   even when they sum correctly, because the covariance is what is at issue.
2. The assembly contains **no** `C_syst + C_retrain` pair — no two blocks whose shift definitions differ
   by the frozen map.
3. `cos(s_u, Δ_u)` and `additive/joint` are **published per endpoint**, so a reader can see what the old
   construction would have said.
4. The identity `‖δ‖² = ‖s‖² + ‖Δ‖² + 2 s·Δ` is **checked**, not assumed. The existing recoil tool holds
   it to a max relative residual of `5.144e-15`; a full-event port that cannot reproduce that has
   arrays that are not what their names say.

Full discharge criteria — six of them, with what is explicitly *not* sufficient — are already written in
`DETERMINATION-20260811-cause5-binding-half.md` §6 and are **not** restated here.

---

## 2. The nuisance inventory: what needs retraining, and what may legitimately be frozen-push

This is the crux. **Measured from the code, this turn.**

### 2.1 The inventory, with counts

| class | members | endpoints each | **endpoints** | where handled today |
|---|---|---|---|---|
| Vertical GENIE/FSI knob bands | 12: `2p2h`, `CCQEPauliSupViaKF`, `FrAbs_pi`, `FrElas_N`, `HighQ2`, `LowQ2`, `MaCCQE`, `MaRES`, `MFP_N`, `MvRES`, `Rvn2pi`, `Rvp2pi` | 2 (`±1σ`, **not** one-sided vs CV) | **24** | `pet_systematics_5d.py:42-43` (`KNOB_BANDS`), block built at `:215-225` |
| Flux (PPFX) | 1 band, many universes | 100 | **100** | `pet_systematics_5d.py:226-232`, `N_FLUX = 100` at `unified_throw.py:52`, gate `require_truth_ratio_bank(..., expected_flux=100)` |
| **`C_syst` total** | 13 bands | | **124** | — |
| Lateral muon/beam (a **different** component, `C_lateral`) | 5: `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` | 2 | **10** | samples Gate-3 promoted, `state/p3f-pet-gate3-promotion-56169838.json` |

`VERT_BANDS` in `eavailW_covariance.py:35-36` and `adopt_unified_*.py` is the same 12 plus `Flux`, which
is where the receipt's own phrase *"`C_syst` sums 13 bands over both endpoints"* comes from.
`MinosEfficiency` and `GEANT_*` are weight-only and correctly stay ordinary universe bands (they
discharged cause 7 on 2026-08-07), so they are **not** in the retraining set as laterals.

### 2.2 "Weight-only" is a statement about the EVENT LOOP, not a frozen-map exemption

`unified_throw.py:19-22` classifies the 124 as *"VERTICAL (**weight-only**) bands"* and excludes the
laterals because they *"shift kinematics and cannot be composed from weights."* **That classification is
correct and it is about a different question than the one the runbook asks.**

Weight-only means the **selected cloud membership does not change** — the same events, with different
per-event truth weights. That is why the verticals need **no new event loop, no per-endpoint merge, and
no 1.1 TB of intermediate storage** (contrast §2.4). It is a large cost saving and it is real.

It is **not** an argument that the learned map is unchanged. In OmniFold step 1 the classifier separates
data from MC-reco **using the MC weights**; changing the MC prior changes the training distribution,
which changes the learned likelihood ratio. So the runbook's rule — *"for every nuisance that can alter
the learned mapping, vary physical inputs and retrain jointly. A frozen-map-only exception requires an
explicit proof that the nuisance cannot change the mapping"* — is **not** satisfied by weight-only status.

### 2.3 And the repo already contains the measurement that refutes the exception for 5 of the 12

`nd-unfolding/products/pet/bkgsub/pet_joint_vs_additive_retrain.json`, read this turn. **Recoil, so not
quotable — but the retraining response is not a small correction, and that is a structural fact:**

| universe | `‖s‖` (frozen) | `‖Δ‖` (retrain response) | `‖δ‖` (joint) | additive/joint | `cos(s,Δ)` |
|---|---|---|---|---:|---:|
| `2p2h:1` | 7.73741e-39 | 5.11033e-39 | 8.53834e-39 | 1.0860 | −0.165 |
| `CCQEPauliSupViaKF:1` | 7.59828e-39 | 6.16815e-39 | **4.09545e-39** | 2.3897 | −0.843 |
| `LowQ2:1` | 8.69552e-39 | 8.25841e-39 | 4.09574e-39 | 2.9280 | −0.885 |
| `MaCCQE:1` | 1.02987e-38 | **1.28115e-38** | 9.48537e-39 | 1.7330 | −0.683 |
| `MaRES:1` | 1.36324e-38 | 1.32354e-38 | 1.01691e-38 | 1.8685 | −0.714 |

**`‖Δ‖` is comparable to `‖s‖` in all five and LARGER for `MaCCQE`.** A frozen-map exception for these
would discard a response of the same order as the effect. The cross term is **negative in every one**, so
the additive construction **overstates** the joint block — aggregate `1.786×` over the five, realized
per-universe range `1.086`–`2.928`. This is a realized range over 5 universes, not a fitted interval
(BEN-025).

**So the answer to the crux is: `C_syst` does NOT reweight away. It is the schedule-dominating component.**

Stated as limits, not hidden: **5 of 12 knob bands have both operands stored** — the receipt's own
`band_coverage_caveat` says only the Phase-7 material endpoints do. The other 7 knob bands and all 100
flux universes have **no measured retraining response at all**, in any representation. `flux:55` is the
one flux universe measured, at `additive/joint = 1.106` — closer to 1 than any knob band, which *hints*
that flux's retraining response may be relatively smaller, but **n=1 of 100 and one universe's `‖s‖`
alone exceeds the published whole-flux block `√tr`, so it is not a term in that block and I will not
generalize from it.**

### 2.4 What is legitimately outside `C_syst`

- **The 10 lateral endpoints are `C_lateral`**, a separate runbook component. They need regenerated
  selected clouds (the 120 Gate-3-promoted P3F ROOTs, which **exist**), plus a per-endpoint merge of 12
  playlists and a converter pass — ~1.1 TB of additional intermediate storage on purgeable scratch, and
  the merge inherits the `TParameter` extensive/intensive hazard
  (`FINDING-20260809-tparameter-merge-semantics.md`). Do not fold this into `C_syst`'s cost.
- **`MinosEfficiency`, `GEANT_*`** — weight-only universe bands, already discharged as such.
- **Nothing else that I can identify.** If there is a nuisance in the quoted budget outside these lists,
  I did not find it, and that is a gap in this document rather than evidence of absence.

---

## 3. Cost, with the arithmetic shown

### 3.1 Operands, every one measured in the turn this was written

| operand | value | source |
|---|---|---|
| Gate 5 per-member wall, mean | **10866.7 s = 3.0185 h** | `sacct -j 56857233 -X`, **n = 35 COMPLETED** |
| Gate 5 per-member wall, min / max | 10728 s (2:58:48) / 11281 s (3:08:01) | same |
| Leg F per-draw wall (train **+ 3 diagnostic stages**) | 11709, 11726, 11555 s → mean **11663.3 s = 3.2398 h** | `sacct -j 56863958 -X` |
| `C_syst` endpoints | **124** | §2.1 |
| Observed sustained concurrency for one array | **10** | `squeue -u josephrb`, Gate 5 at 10 RUNNING |

Gate 5's figure is **training only**; Leg F's includes the three no-training diagnostics that a `C_syst`
endpoint also needs (gate A/B, decomposition, extraction-side check). **I use the Leg F figure**, which
is `+7.3%` over Gate 5's, and show both so the choice can be contradicted.

### 3.2 The arithmetic

    one retrain per endpoint, no replicates:
        124 endpoints x 3.2398 h  =  401.7 GPU-h
        at 10 concurrent          =   40.2 h wall  ( ~1.7 days, IF slots are free )

    with k replicates per endpoint (see 3.3 -- this is the open decision):
        k = 2   ->    803.5 GPU-h,   80.4 h wall
        k = 3   ->  1_205.2 GPU-h,  120.6 h wall
        k = 5   ->  2_008.6 GPU-h,  200.9 h wall

    for comparison, the SEPARATE lateral component:
        10 endpoints x 3.2398 h   =   32.4 GPU-h  + merge/convert + ~1.1 TB intermediate

Cross-check against the existing figures, **with a citation correction I owe.** The **"≥100 GPU-h"**
whole-build figure and the unverified **"170–250"** live at
**`docs/OPEN_ITEMS-ARCHIVE-2026-08.md:696`**, *not* at `docs/OPEN_ITEMS.md`. The determination cites the
live file; that item has since been archived, so the pointer is stale, and **I repeated the stale
citation from the determination before checking it** — the BEN-215 shape (a citation verified as a
string), caught here only by grepping for the number rather than the claim. My single-retrain `C_syst`
number alone is **401.7 GPU-h ≈ 4.02×** the `≥100` floor. The `≥100` is consistent with mine *as a floor*
and is not an estimate of this component; the `170–250` figure is **not** reproducible from any operands I
found and I do not adopt it. `DETERMINATION-…-cause5` derives a `≥24 GPU-h` floor for the **lateral** block only,
from `~2 h 25 m` per retrain read off checkpoint mtimes; my `3.24 h` is `1.34×` that, and the difference
is that mine is `niter=3` with diagnostics and measured over `n=38` jobs rather than one mtime pair.

**"40.2 h wall" is arithmetic, not a schedule, and today's evidence says so.** Leg F ran at **2**
concurrent for hours and its last draw has now waited **~6 h** behind our *own* Gate-5 array in a
saturated partition. Concurrency is not a property we control (BEN-153/BEN-126). Any wall-clock
commitment needs a queue answer, not a division.

### 3.3 The replicate question, which is where the cost is actually decided

Each `δ_u` from a single retrain carries that retrain's process noise. If the across-process training
noise is comparable to a nuisance's `δ_u`, one retrain per endpoint **cannot resolve that nuisance** and
`k > 1` is forced — which is the factor-of-`k` above.

The repo has a **training-noise control** for exactly this: Phase 7's `null` / `identity` universe
(`phase7_retrain_universe.py:99-104`, *"same seed/config as a universe retrain, so `x_null − CV`
measures the training noise that contaminates every universe `Δ`"*). Measured value, recoil:

    ||Delta_null||           = 2.3124629464350753e-41
    5-band joint sqrt-trace  = 1.7315713222649896e-38   ->  749x the noise      RESOLVED
    weakest single band      = 4.09545e-39 (CCQEPauliSupViaKF) ->  177x         RESOLVED

**On that control, `k = 1` is ample.** But the control is almost certainly **within-process**, and this
campaign has already been burned by exactly that distinction: `VL126` measures the within-process floor
at `1.26775e-04` against an across-process floor of `1.62987e-02`, **`128.6×` larger.**

**Illustration, and explicitly NOT a derivation:** if a `128.6×` within→across inflation applied here,
`‖Δ_null‖` would become `≈ 2.97e-39`, and the weakest band's margin would fall from `177×` to **`1.38×`
— not resolved.** I flag hard that this multiplication is **not justified**: `VL126`'s ratio is in the
fold-forward/trajectory metric and `‖Δ_null‖` is in cross-section units, so the two are not commensurable
and the product is an order-of-magnitude gesture, not a result. **What it does establish is that the
question is live and cheap to settle, and that `k` is not obviously 1.**

**There is a nearly free way to settle it, and it is the single highest-value item in this document.**
Gate 6 Leg F is producing **five across-process draws of one fixed seed pair in the full-event
representation** — the exact identity-retrain control this needs — and each draw has already written a
complete weights `npz`. Leg F reads only the trajectory metric from them. **Extracting the cross-section
vector from those same five artifacts would give the across-process training-noise floor in the units
`C_syst` needs, for zero additional GPU time.** That is an extraction pass over existing artifacts, not a
retrain. **I am not doing it** — it is outside Leg F's predeclared rule, it is a decision (§5.4), and
inventing it now is the after-the-fact scope creep the predeclaration exists to prevent.

---

## 4. What this shares with Gate 5 and Gate 6, named by file

Reusable as-is:

| machinery | file | what it gives `C_syst` |
|---|---|---|
| Per-endpoint job skeleton: fail-closed digest tables, `flock` sole-writer, refuse-to-overwrite, execution-environment sidecar, 4 stages | `nd-unfolding/pet/sbatch_pet_fullevent_floor_replicate_array.sh` | the launcher pattern; `C_syst` is this with a universe axis instead of a draw axis |
| Sequencing gate that refuses to start until a prerequisite receipt is terminal | `nd-unfolding/pet/sbatch_pet_fullevent_legx_2x2_array.sh` | the same shape gates `C_syst` on a settled `k` |
| Gate A/B push provenance (exact MC-index + truth-normalization identity) | `nd-unfolding/pet/gate_ab_push_provenance.py` | per-endpoint validity, unchanged |
| Pull/push decomposition + within-job reproduction gate | `nd-unfolding/pet/step1_pull_push_decomposition.py` | per-endpoint validity, unchanged |
| Convergence trajectory | `nd-unfolding/pet/step1_increment_trajectory.py` | per-endpoint convergence screen |
| Predeclared statistic → validity → three-way verdict, with refusal to verdict on a subset | `nd-unfolding/pet/gate6_floor_statistics.py` + `tests/test_gate6_floor_statistics.py` | the receipt/verdict skeleton, and the `do_not_select_passing_subset` mechanism |
| Truth-ratio bank per universe, `expected_flux=100` fail-closed | `nd-unfolding/pet/…` via `uq_math.require_truth_ratio_bank`, `pet_systematics_5d.py:214` | the universe priors themselves |
| Per-universe retrain **mechanism**, including the `null` control | `nd-unfolding/pet/phase7_retrain_universe.py` | `--universe 'MaRES:1'`/`'flux:37'` resolution and the identity-retrain control |
| Joint-vs-additive measurement + its power tests | `nd-unfolding/pet/measure_joint_vs_additive_nuisance_retrain.py` | discharge criterion 3, and the identity check |
| Coherent-target → training array orchestration at N=50 | `nd-unfolding/pet/sbatch_gate5_replica_train_array.sh` | the two-stage array pattern; note its `EXPECTED_HEAD` guard (OI-57) |
| Per-endpoint merge + converter (laterals only) | `nd-unfolding/pet/merge_g2_gate1_mefhc.sh`, `nd-unfolding/pet/dump_pointcloud_inputs.py` | `C_lateral`, and **not parameterised** over band/endpoint |

Every path in this table was `ls`-checked in the turn this was written — 20 of 20 exist (BEN-216: `ls`
before quoting a path to another agent).

### 4.1 The structural blocker, which is why `C_syst` has no design

**`train_fullevent_nominal.py` cannot retrain on a universe prior. Measured — its entire CLI is:**
`--inputs --out --tag{nominal,floor} --gate3-manifest --target-npy --target-receipt --estimator-seed
--subsample-seed --niter --epochs --max-events --batch-size --config-gate-only --allow-overwrite`.
**No `--universe`, no truth-ratio bank, no per-event reweight.**

`phase7_retrain_universe.py` has all of it — and is recoil-era: it defaults to
`of_inputs_pc_fullcloud_bkgsub_5d.npz` and `bank_uthrow_5d`, runs `--niter 2` against the adopted `3`,
produces the **increment** `Δ_u` rather than the joint `δ_u`, and its own docstring says extraction
*"uses the nominal cloud"* — i.e. it is both the additive decomposition and CV-support-limited.

So the obvious path — add a universe axis to the pinned full-event driver — **is gated. Verified against
the live receipt, after pulling:** `docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260813.json` is
`PASS_CODE_ONLY` with `superseded_by: null`, carries **19 `files` entries**, and its
`files.driver.path` is exactly `nd-unfolding/pet/train_fullevent_nominal.py` at sha256
`91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc` — the same digest Leg F and Leg X
pin. So editing that driver converts a code change into a **code-gate re-issue plus re-attestation of
those bindings**, and `verify_hash_bindings.collect()` harvests any dict carrying `path`+`sha256`, so the
blast radius is wider than the 19. That is exactly the constraint Leg F's and Leg X's launchers were
written to avoid, and it is the reason this component has no design rather than an incomplete one. **It is
a decision, not an engineering task (§5.1).**

**A near-miss worth recording, because it nearly went into this section as a finding.** Before pulling, my
tree showed **two** Gate-4 receipts — `20260812` and `20260813` — *both* with `superseded_by: null` and
binding the same driver to **different** digests (`5fda80df…` vs `91144bee…`), which would have made "the
live receipt" ambiguous and undercut this whole subsection. It was **already repaired on `origin/main`,
25 commits ahead of me**: `20260812` now carries `superseded_by`, `files: 0`, and `files_at_issue: 17`
with `5fda80df…` preserved verbatim — exactly the repair the pre-commit hook's own text prescribes. The
new whole-tree binding check was **inert in my worktree** (the hook file is the main checkout's; the
checks it runs are the worktree's copy), so what looked like a live defect was a stale snapshot of one.
**Pull before reporting a tree-wide condition** — it is one command and it is the difference between a
finding and a false alarm. Filed as BEN-129.

---

## 5. The decisions this forces onto Joseph — listed, not pre-decided

**5.1 — How the universe axis reaches the pinned driver.** Add `--universe` + truth-ratio-bank support
to `train_fullevent_nominal.py` and re-issue the Gate-4 launch-code gate with full pin re-attestation;
or write a separate full-event universe driver that duplicates the nominal contract and must then be kept
in step with it. Both have real costs and they are different kinds of cost. **Not pre-decided here.**

**5.2 — Whether the 100 flux universes are all retrained, or a predeclared subset is.** `100 × 3.24 h =
324 GPU-h` is **81%** of `C_syst`'s single-retrain cost. The one flux universe with both operands stored
has `additive/joint = 1.106`, the closest to 1 of anything measured — but that is `n = 1` of `100` and I
will not generalize from it. The runbook permits an ordered targeted-versus-full universe decision that
*"may reduce unnecessary work but may not weaken the joint-universe contract."* **Any subset must be
predeclared before the covariance is viewed.**

**5.3 — `k`, the number of retrains per endpoint.** `k` multiplies the whole component (§3.2). It cannot
be chosen honestly before the across-process training-noise floor is known in cross-section units
(§3.3). **Choosing `k = 1` by default is a decision, not a neutral option.**

**5.4 — Whether to extract the cross-section vector from Gate 6 Leg F's five existing artifacts.** This
settles 5.3 for **zero additional GPU time** and is the cheapest decision in this document. It is
outside Leg F's predeclared rule, so it needs to be authorized as its own small step rather than folded
into Leg F. **I have not done it.**

**5.5 — Whether the 7 knob bands with no stored retraining response get one measured first.** Five of
twelve have both operands; the rest are unmeasured in any representation. A cheap targeted pre-measurement
would tell us whether the `1.086`–`2.928` range is representative before committing `400+` GPU-h.

**5.6 — Ordering against `C_lateral` and the `niter=3` recomputation.** `C_lateral` shares the retraining
machinery but adds a per-endpoint merge and `~1.1 TB` on purgeable scratch. And every pre-`niter=3`
covariance is inconsistent with the adopted central (`OPEN_ITEMS` items (d)/(e)), so `C_syst` must be
built at `niter=3` from the start — which rules out reusing `phase7_retrain_universe.py`'s `niter=2`
defaults without a change.

---

## 6. What I cannot establish from the repo — "needs X" is the complete answer

1. **The across-process training-noise floor on the cross-section vector, in the full-event
   representation.** Needs: an extraction pass over Leg F's five draws (§5.4), or a dedicated identity-retrain
   control. `VL113` is the closest existing number and is `n=1` in the **wrong metric**.
2. **The retraining response for 7 of 12 knob bands and 99 of 100 flux universes.** Needs: either the
   full build, or a predeclared targeted pre-measurement (§5.5). **Nothing in the repo bounds these.**
3. **Whether any full-event nuisance qualifies for the frozen-map exception.** The runbook requires an
   explicit proof per nuisance; **no such proof exists for any nuisance**, and §2.3's measurement points
   the other way for the five it covers.
4. **Whether `dump_pointcloud_inputs.py` and a per-endpoint merge actually work on a P3F ROOT.** The
   determination states plainly that *"no new estimator code"* is an inference from argument signatures,
   not a demonstration. Needs: one trial merge + convert. (`C_lateral`, not `C_syst`.)
5. **The queue cost.** §3.2's wall-clock is `GPU-h ÷ concurrency`; today's evidence is that concurrency
   is contended and not ours to set. Needs: a scheduling decision, not an estimate.
6. **The `170–250 GPU-h` figure** (at `OPEN_ITEMS-ARCHIVE-2026-08.md:696`, **not** the live
   `OPEN_ITEMS.md` the determination points to). Not reproducible from any operands I found. Needs: its
   author's operands, or retirement. The stale pointer needs fixing in the determination too — **not done
   here, because that file is another lane's** and editing a peer's cited document to fix my reading of it
   is the BEN-204 shape.
7. **Whether the 124-endpoint list is complete.** Assembled from `KNOB_BANDS`/`VERT_BANDS`/`N_FLUX` in
   the code. If a nuisance in the quoted budget sits outside those lists I did not find it — and this
   document would then understate the cost.

---

**Nothing in this document is executed.** No submission, no cluster mutation, nothing that touches
arrays `56863958` or `56857233`. Gate 6 remains BLOCKED at `19585b7` with all five prohibitions live; Leg
X remains authorized-but-unsubmitted; `C_ML` still needs a decision Joseph has not made; and cause 5
remains **OPEN** — measuring what a construction would cost is not building it.
