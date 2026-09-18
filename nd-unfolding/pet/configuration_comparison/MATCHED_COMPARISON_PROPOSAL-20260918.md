# Matched comparison of two complete PET configurations: execution proposal

**Revision 2, 2026-09-18.** Revision 1 is superseded; §1 lists what it got wrong.

**CITABLE FOR:** a frozen design for selecting between our production PET configuration
and Gregor's, on our unfolding task.
**NOT CITABLE FOR:** any result — none exists — or any publication adoption. PET remains
diagnostic method development.

**Nothing is launched.** The deliverable is the complete comparison and a final decision
deck. **Tier A is optional preparation, not a substitute for it.**

---

## 1. What revision 1 got wrong

| # | revision 1 said | corrected |
|---|---|---|
| 1 | "the exact upstream configuration is the `Transformer1` regression preset" | **`Transformer1` is not a model his paper reports.** `plot_configs/V1Paper.json` lists OmniLearned-small, OmniLearned-small-rw and OmniLearned-medium as the V1 paper lineup and puts Transformer-xsmall/small under `_disabled_models`. Revision 1 pinned, costed and designed around the wrong object. §2 |
| 2 | Gregor's model is "**18.9×** ours" | that is Transformer1. His **paper** backbone is **58.7×** ours (2,762,550 vs 47,041 parameters); medium is **1,112×**. Measured, `receipts/model-capacity.json`. §2 |
| 3 | the representation is "blocked on a C++ event-loop deliverable" | **partly false.** The cap, overflow aggregation, merged counts and discarded energy need **no C++ at all** — the full-length cloud vectors are already in the ROOT and the top-12 truncation is a Python choice in `dump_pointcloud_inputs._pad_tokens`. What is genuinely blocked is narrower and has a cheaper route. §3 |
| 4 | cited `FULL_EVENT_INTERFACE_REQUEST.md` "**§D**" as the typed-object request | §D is *"Residual-energy summary tokens (optional)"*. **No filed request for the typed-object vocabulary exists anywhere.** Sections A, B and C of that request have **landed**. Owner is **Agent A**. §3 |
| 5 | "our production baseline on the endpoint is **0.5126033**" | that is `VL100`, from closure `56552326`, **every artifact of which is prefixed `NONQUOTABLE-DIAGNOSTIC.` with `quotable: False`**, and **`recovery_evaluated` is still `False` at the promoted configuration**. `OI-71` is `WAITING-USER`. It is not a production baseline, and **δ's justification in revision 1 rested on it**. §4, §6 |
| 6 | V-PORT checked **forward** agreement only | forward agreement does not establish that training is equivalent. Extended to forward, **gradient** and **weight-update**. §7 |
| 7 | sizing used normal quantiles (`1.96 + 0.84`) | at n ≈ 8 that understates the interval. Replaced by a **t-based iterative** rule, sized on the **upper** confidence bound of the pilot's σ. §7 |
| 8 | "one endpoint" | the powered closure injects a tilt in **truth muon pT** — a muon kinematic. For a comparison whose entire subject is the **hadronic** representation, that is close to the wrong variable, and the closure is separately **silent** about the 34 % fold-forward deficit. §5 |
| 9 | 70 GPU-h presented as the campaign cost | **70 GPU-h is a Tier-A ceiling only.** The cost of completing the comparison is **unresolved** and depends on a ratio stage 2 must measure. §8 |

What revision 1 got right and is retained: one engine for both arms; the powered closure
rather than the identity closure; freezing before comparative results exist; and the
refusal to restart isolated component campaigns. The component inventory in
`CONFIGURATION_COMPARISON-20260918.md` is **preserved unchanged** and remains the record
of what differs.

---

## 2. The intended Gregor configuration

**Paper:** *Cross-Domain Transfer with Particle Physics Foundation Models: From Jets to
Neutrino Interactions* — Krzmanc, Mikuni, Nachman, Wilkinson, **arXiv:2604.12364**
(`CITATION.bib`). The title states the subject: the paper is about **transfer from a
pretrained foundation model**, so the pretrained arm is its contribution and a
from-scratch transformer is a baseline.

**Version.** Repository `gregorkrz/minerva-ml` at **`fc9a099d3c9c060f03cef293c294f9de4eb019cd`**
(2026-07-20, clean tree). **No release tags exist, so the commit that produced the paper
is unidentified** — this is prerequisite **R1** and it is a question for Gregor.

**Backbone.** `PET2`, `src/models/omnilearned/network.py`, vendored near-verbatim from
OmniLearned (MIT). Not `PointGlobalMixedViT`.

### The three configurations, kept separate

| tier | id in `submit_train_jobs.py` | what it is | init | in the paper? |
|---|---|---|---|---|
| **P1** | `OLS` | OmniLearned **small**, `--use-pretrained pretrain_s` | **pretrained** | **yes** — `OmniLearned-small` |
| **P2** | `OLS_RW` | OmniLearned **small**, no pretrained flag | scratch | **yes** — `OmniLearned-small-rw` |
| **P3** | `OLM` / `OLM_FB` | OmniLearned **medium**, `pretrain_m`, **backbone frozen** | pretrained, frozen | **yes** — displayed `OL-medium-frozen` |
| **B1** | `Transformer1` | `PointGlobalMixedViT` d_model 128 / depth 4 / heads 8 | scratch | **NO** — `_disabled_models` |

Sources: `plot_configs/V1Paper.json`; `submit_train_jobs.py:155-169`.

**Constructor configuration, as his code builds it** (`train.py:1085-1105`, so these are
the values his runs use, not class defaults): `input_dim` 4, `add_dim` 5, `pid` True,
`pid_dim` 8, `cond_dim` **16** (10 base globals + 6 per-PID energy sums), `num_coord` 2,
**`K = 10`** (hardcoded at `train.py:1103`, *not* the `PET2` default of 15), `add_info`
True, `conditional` True. Presets from `get_model_parameters`: **small** = 8 transformers
+ 2 head transformers, 8 heads, `base_dim` 128, `mlp_ratio` 2, `num_tokens` 4;
**medium** = 12 + 2, 16 heads, `base_dim` 512.

**Measured capacity** (`receipts/model-capacity.json`, both models instantiated):

| model | trainable parameters | vs our step-1 PET (47,041) |
|---|---:|---:|
| ours (step 1) | 47,041 | 1× |
| B1 Transformer1 — **not a paper model** | 890,130 | 18.9× |
| **P1 / P2 OmniLearned-small** | **2,762,550** | **58.7×** |
| P3 OmniLearned-medium | 52,294,730 | 1,112× |
| P3 with backbone frozen | 20,989,958 trainable | 446× |

**Checkpoints.** `load_pretrained_omnilearned` fetches
`best_model_{pretrain_s,pretrain_m}.pt` from
**`https://portal.nersc.gov/cfs/m4567/checkpoints`** (`utils.py:58-79`) — CFS project
**m4567**, not ours. Audit `B_provenance` verified these **time out consistently**, and
the `gregorkrz/HyperScale` repo returns 404. Two consequences worth stating plainly:
**the code silently attempts a download when the file is absent**, so a naive
reproduction fails at runtime rather than at configuration time; and **P1 and P3 are not
runnable at all** without the files. Obtaining them with hashes is prerequisite **R2**.

**One configuration detail that matters for this comparison.** All three paper arms carry
**`--zero-cond-feature 2`**, which zeroes global feature index 2 —
`log(max(MasterAnaDev_hadron_recoil,0) + 1e-5)`. His paper configuration **deliberately
removes a hadronic recoil summary**. A comparison of hadronic representations must
reproduce that, not quietly restore it.

**What is runnable today:** **P2 only** (`OLS_RW`, scratch). P1 and P3 are gated on R2.
A comparison against P2 alone answers "is his architecture better than ours"; it does
**not** answer "is his *paper* method better", because the paper's claim is about
transfer. That distinction must survive into the final deck.

---

## 3. Extraction contract, field by field

### 3.1 What is where

`AnaTuple` = the MasterAnaDev source tuples. `ROOT` = Agent A's event-loop output
`runEventLoopOmniFold_G2_FPS_MEFHC.root`. `npz` = `G2_FPS_MEFHC_P12.npz`, which is what
the estimator reads.

| Gregor field | his source | our branch | AnaTuple | ROOT | npz | needed |
|---|---|---|---|---|---|---|
| muon 4-vector, φ, q/p, MINOS | `muon_corrected_p` | `mu_reco_*`, `mu_reco_minos_ok` | ✓ | ✓ | ✓ `reco_muon` | **nothing** |
| reco vertex | — | `vtx_reco_{x,y,z}` | ✓ | ✓ | ✓ `reco_vertex` | **nothing** |
| token view / time | — | `part_reco_view`, `part_reco_time` | ✓ | ✓ | ✓ | **nothing** |
| **cap, overflow aggregate, merged count, discarded energy** | `max_particles`, aggregation | full-length `part_reco_*` vectors | ✓ | ✓ **full length** | ✗ truncated to 12 | **dump change + re-run. NO C++.** |
| photon 4-mom, dE/dx, time | `gamma{1,2}_*` | `gamma{1,2}_E`, `gamma{1,2}_direction`, `gamma{1,2}_dEdx`, `gamma{1,2}_time` | ✓ **authorized** | ✗ | ✗ | **export** |
| blob position, time, energy | `Blob{X,Y,Z,T,TPos,TotalE}` | `MasterAnaDev_Blob{X,Y,Z,T,TPos,TotalE,Is3D,NClusters}` | ✓ **authorized** | ✗ | ✗ | **export** |
| prong 4-mom, position | `prong_part_E`, position | `prong_part_E`, `prong_part_pos` (nested) | ✓ **authorized** | ✗ | ✗ | **export** |
| prong PID, dE/dx | `prong_part_pid`, `prong_dEdXMean` | same names | ✓ **authorized** | ✗ | ✗ | **export** |
| 16 event globals | fuzz, iso-blob, hadron recoil, passive id/od, Michel, γγ mass, prong count, 6 energy sums | `muon_fuzz_energy`, `muon_iso_blobs_energy`, `MasterAnaDev_hadron_recoil`, `part_response_*`, `improved_nmichel`, … | ✓ present, **NOT in the authorized set** | ✗ | ✗ | **authorization + export** |
| per-type energy sums | derived post-truncation | — | derivable once types exist | — | — | derive **pre**-cap, not post |

**Two findings that change the shape of the work.** Every typed-object field Gregor's
tokens need **already exists in the AnaTuple and is already inside the A1-authorized
branch set** (`typed_descriptor_source_smoke.REQUIRED_BRANCHES`; A1 read all of them on
the real tuples under job 58470099). And the **cap is ours to change**: the dump binds
`ROOT.std.vector("double")` cloud buffers and `_pad_tokens` truncates them
(`dump_pointcloud_inputs.py:90-112, 252-268`), exactly as the interface request says
(*"the top-12 truncation is a loader choice"*).

### 3.2 The actual blocker is alignment, and it has a cheap route

The AnaTuple carries event keys — `ev_run`, `ev_subrun`, `ev_gate`
(`typed_descriptor_source_smoke.py:86`, inside the authorized set). **The npz carries
none.** Rows are identified positionally, with `sig_identity_hash` / `data_identity_hash`
/ `bkg_indices` for order integrity only. So a Python-side join of AnaTuple typed objects
onto estimator rows is **impossible today** — not because the data is missing, but
because the key that would join them is discarded.

| route | ask of Agent A | our work | risk |
|---|---|---|---|
| **R-1 (recommended)** | emit **three scalar branches** `ev_run`, `ev_subrun`, `ev_gate` on `mc_signal_reco`, `data`, `mc_background` | read typed objects from the AnaTuples and join by key; all representation logic stays ours | join correctness must be **proved**, not assumed; a second pass over the playlist AnaTuples |
| R-2 | emit ~20 typed-object **vector** branches on all three trees | none | a much larger ask against A's running active-universe production, and the vocabulary would then be fixed in C++ |

R-1 is the smaller ask by an order of magnitude and keeps the representation where we can
iterate on it. **It is not free of obligation:** the interface request is explicit that
Agent A owns `runEventLoopOmniFold.cpp` and *"Do not edit A's running C++"*, so either
route is a request to A, not an edit by us.

### 3.3 Selection, weights and alignment that any route must preserve

These are not optional; each is an existing fail-closed property of the input and a join
that breaks one produces a silently wrong estimator.

1. **FPS domain gate** — rows are gated on the retained extended-FPS domain, sourced only
   from `MNV101_FULL_PHASE_SPACE=1` loops.
2. **`pass_reco` / `pass_truth`** — native truth-only misses are **preserved** as appended
   rows with an empty reco cloud and sentinel muon/vertex. A key join must not drop them,
   and they have no AnaTuple reco counterpart to join to.
3. **Sentinels** — `!pass_reco` muon features are `-9999`; normalization is fitted over
   `pass_reco` only and those rows are zeroed after. Typed objects must follow the same
   rule or they pollute the scale.
4. **Weights** — `w_truth` / `w_reco` / `w_bkg` are **RAW**; consumers apply `pot_scale`.
   A join must not reorder them relative to their rows.
5. **Background** — negweight-refined nominal, row-aligned background clouds, fail-closed
   without the inventory. `purity` is a labelled control only.
6. **Data scalars** — CLM-007: the data leg must come from an explicit row-aligned source,
   never a silent fallback to MC `reco_scalars`.
7. **Verification, predeclared:** row counts per inventory; the three identity hashes
   unchanged; **a per-event order proof against the ROOT** on the
   `build_bkgsub_pointcloud_input.py` precedent (row-count alignment alone is what the
   feature contract already flags as insufficient); and key **uniqueness and
   completeness** on both sides, with the unmatched count reported, not silently dropped.
8. **Data/MC/background symmetry** — a reco-derived type code must exist with the same
   semantics in all three inventories. An asymmetric vocabulary is an **inventory label**
   the step-1 classifier can exploit, and a truth-derived one is direct leakage and is
   excluded permanently.

---

## 4. The historical recovery, corrected per OI-71

Revision 1 called **0.5126033** "our production baseline". `OI-71` says otherwise, and
the correction is load-bearing because δ was justified from it.

* The number is **`VL100`**, from closure **`56552326`** (re-derived 47/47 by `56562169`).
* **Every artifact of that closure is prefixed `NONQUOTABLE-DIAGNOSTIC.` and carries
  `quotable: False`.** That receipt scopes its non-quotability to not authorizing engine
  edits or promotion, so **whether the recovery number itself may be quoted is a question
  it raises and does not answer**. `OI-71` is **`WAITING-USER`**; the disposition is the
  PET lane's and Joseph's.
* **`recovery_evaluated` remains `False` at the promoted configuration.** Recovery has
  never been evaluated at the artifact actually promoted. The bridge is `OI-23`'s
  configuration equivalence — *an argument that the two would score alike, not a
  measurement that they do*.
* Of the four quotability grounds, three are determined and **`G4` alone survives**, and
  `OI-71` records that it is **not determinable read-only at any effort**, because
  recovery is defined against an injected truth reweight and the promoted nominal has
  neither tilt nor A/B split.

**And the finding that reshapes §5.** That closure's own fold-forward ratio is
**≈1.0114** against the promoted nominal's **0.736746** — so **the closure does not
exercise the nominal's ~34 % normalization deficit at all.** It is **silent** about that
failure mode rather than reassuring about it (`OI-71`(4)(e)). Separately, `OI-125`:
`git grep fold_forward` over both closure drivers returns **zero hits** — the closure
driver has no fold-forward computation, which is why the quarantine had to reach for
another run's weights. Adding it is ~8 lines and **must not be done by editing the pinned
driver**.

**Consequences, applied:**

1. δ **cannot** be justified as "the margin by which production clears its criterion".
   That construction used a non-quotable number at a configuration where recovery was
   never evaluated. §6 rebuilds δ on a different footing.
2. Any recovery value this campaign produces is **a value for its own configuration**,
   not a re-measurement of the promoted nominal, and must be labelled that way.
3. The fold-forward recorder is a **prerequisite** of the validation set, not an extra.
4. Nothing here discharges `OI-71`. This proposal must not be read as answering it.

---

## 5. Minimum representative validation for a configuration decision

The powered pT closure alone is **not sufficient**: it injects a muon kinematic, and it
is silent about the deficit. The minimum set below is what a *configuration* decision
needs — no more, and each item is tied to a failure mode that is live in production.

| id | what it measures | why it is required | status |
|---|---|---|---|
| **V1** | **hadronic** powered closure: an injected truth-level tilt in a **hadronic** variable, recovered | the comparison's whole subject is the hadronic representation; a muon-pT tilt can be transported by the muon event block alone, so it can be **insensitive to the thing under test** | **specified: a clipped exponential tilt in truth `E_avail`.** It is already in the npz — `truth_scalars` col 2, from `MC_eavail` (`dump_pointcloud_inputs.py:79`) — so it needs **no new export**, and available hadronic energy is precisely the quantity a hadronic representation must encode. Protocol mirrors the pT injection exactly (clipped, rate-preserving, truth-passing rows only, disjoint halves at split seed 7) so the two differ in **one** variable. `q3` (col 3) is the pre-registered alternate; truth `MC_hadangle` is in the ROOT and dropped by the loader if an angular tilt is later wanted. **Joseph ratifies the variable** — it decides what the comparison is sensitive to |
| **V2** | fold-forward ratio per iteration **and** end-of-run, both arms | the promoted nominal carries a ~34 % deficit that the existing closure does not exercise; a comparison blind to it cannot support a configuration decision | needs the `OI-125` recorder (~8 lines, new file, **not** an edit to the pinned driver) |
| **V3** | the existing **muon-pT** powered closure, protocol unchanged | continuity with the campaign record, and a muon-side control against V1 | reuse `closure_powered_truth_reweight.py` as-is |
| **V4** | omitted-muon stress closure, per-stratum L1 | the established directional control: proves the estimator **moves** when it should | exists; PASS for our arm (0.582 → 0.043) |
| **V5** | identity self-consistency closure | plumbing only — **never read as power**, since a constant estimator optimizes it | exists |
| **V6** | data / signal / background **type-vocabulary symmetry**, plus a leakage screen | an asymmetric reco type code is an inventory label; a truth-derived one is direct leakage | required by any typed arm |
| **V7** | sentinel and missingness handling on the new fields | `-9999` `!pass_reco` rows; zero-filled absent fields are indistinguishable from real zeros in his scheme | required by any typed arm |
| **V8** | acceptance stratification: Tier-1 vs Tier-2 dead cells | ~28 % of rate sits in prior-dominated cells; an arm cannot be credited for cells no feature can measure | exists (`acceptance_map_fullevent_fps`) |
| **V9** | background mode is negweight-refined, fail-closed | `purity` is a labelled control, never a nominal | exists |

**V1 is the one genuinely new scientific instrument this campaign needs**, and it is not
an "isolated component experiment" — it is the endpoint without which the comparison
cannot speak to hadronic representation at all. It reuses the existing injection code
path with one variable changed, so the cost is implementation and not a new campaign.
Its protocol is frozen **before** any comparative number exists.

**Why the muon-pT injection is not enough, stated concretely.** Our muon block is 13
features conditioning the transformer through FiLM. A tilt in truth muon pT can be
transported almost entirely by that block, so both arms can score well on V3 while
differing arbitrarily in how they handle the hadronic cloud — which is the only thing
Tier B varies. Using V3 alone would be choosing an endpoint that is insensitive to the
treatment.

---

## 6. Three separate questions

Revision 1 collapsed these. They are distinct and a configuration decision needs all
three.

### 6.1 Absolute adequacy — asked of each arm alone

Does the arm clear the adopted criterion `recovery ≥ f × reference` (`f = 0.80`;
CLM-012's k-dependent ceiling) on **V1 and V3**, with **V2, V4–V9 passing**?

**An arm that fails adequacy is not recommendable regardless of the comparison.** Two
inadequate arms mean no selection, and "ours is non-inferior" would then be a statement
about two unusable configurations.

### 6.2 Non-inferiority — is ours acceptably close to his?

`H0: recovery(ours) − recovery(his) ≤ −δ`. Rejecting `H0` concludes non-inferiority.

**δ = 0.017 recovery points**, justified as an **acceptable scientific loss** and not
from any gate margin:

The campaign has already made one explicit judgement about tolerable shape loss. Adopting
the fit-time LR anneal **knowingly paid −0.0342 of recovery** to buy a 33-point
normalization repair, and Joseph adopted it (CLM-012 (viii)) — so a shape cost of ~0.034
was accepted *when something was bought with it*. Non-inferiority buys nothing: it is the
price of keeping the incumbent. **δ is therefore set at half that accepted price,
0.017** — we will tolerate at most half the shape loss the campaign accepted when it was
getting a real benefit in return.

Three properties of that choice, stated so it can be checked:

* it is a **decision anchor**, traceable to a ruling Joseph made, **not** a measurement,
  and in particular not the `VL100` margin revision 1 misused;
* in units of the endpoint it is ~2.8 % of the k=3 reference ceiling 0.618228 and ~2.7 %
  of the dilution-model ideal 0.6332 — a small relative shape loss;
* it is **far above** the closure's same-configuration repeat spread (1.226e-3), so it is
  not a noise-level margin, and **far below** the ~19 % by which the trained estimator
  already sits under the dilution ideal, so it is not a margin that would wave through a
  materially worse estimator.

δ is provisional until Joseph ratifies it (approval **E**). If he prefers a different
tolerable loss, the number changes and the design does not.

### 6.3 Superiority, and the switching threshold

`H0: recovery(his) − recovery(ours) ≤ δ_switch`. Rejecting it concludes his is
materially better.

**When a smaller but demonstrated advantage for Gregor still leads us to retain ours.**
Adoption is not free, and the costs are specific:

* a **new estimator fingerprint**, which invalidates every `v1`-keyed artifact including
  the Gate-2 target, and a full pin cascade;
* **re-validation of every covariance component** against the new estimator;
* a **58.7×** larger model multiplied through the campaign's ~130 trains (§8);
* a framework decision, and for P1/P3 a **permanent dependency on a checkpoint we cannot
  currently obtain**.

So: **`δ_switch = 0.02` recovery points**, and adoption additionally requires that his
arm pass absolute adequacy **and**, for P1/P3, that the checkpoint be obtained and
hash-pinned. A demonstrated advantage **below** `δ_switch` is reported exactly as what it
is — *"his configuration scored better by X, which is below the switching threshold, so we
retain ours for the stated costs"* — an honest statement that he won on the endpoint and
we kept ours for reasons we name, never as "no difference was found".

`δ_switch > δ` is deliberate and asymmetric: retaining a validated incumbent is cheap,
replacing it is not.

### 6.4 The four outcomes

| adequacy | comparison | conclusion |
|---|---|---|
| both pass | CI lower bound `> −δ` | **Recommend OURS** — non-inferior at equal tuning |
| both pass | CI for (his − ours) lower bound `> δ_switch` | **Recommend HIS** — materially better by more than the switching cost |
| both pass | `0 <` advantage to his `< δ_switch`, demonstrated | **Retain OURS, and say he scored better.** Not "no difference" |
| both pass | CI contains `−δ` | **Inconclusive — no selection.** Incumbent is a *provisional engineering choice* |
| either fails | — | that arm is **not recommendable**; if both fail, no selection and the report says the configurations are inadequate |

---

## 7. What is frozen before any comparative result exists

One digest-verified file, `MATCHED_FREEZE-<date>.json`, on the
`VALIDATION_CRITERIA-20260918.json` precedent (sha256 verified by the launcher). It
carries every item below. **None of these may be changed after a comparative number
exists.**

### 7.1 Input adaptations

Stated as a table of *forced mappings*, because each is a place where "his configuration"
is not literally his, and an unstated adaptation is an unfalsifiable comparison.

| adaptation | why forced | recorded as |
|---|---|---|
| his positional encoding consumes `(η, φ)`; our tokens carry `(pos, z)` | our cloud has no per-token `(η, φ)` | same *mechanism* over the geometry we have — a mapped, not identical, choice |
| his 10-column token vs our 5-column cluster | until R-1/R-2 lands, his arm sees our 5 columns | **his arm is representation-identical to ours in Tier A**; the difference is architecture and recipe only |
| his 16 globals vs our 13 muon/vertex features | his globals are not exported | Tier A uses **our** event block for both arms |
| `--zero-cond-feature 2` | his paper zeroes the hadron-recoil global | reproduced in his arm once globals exist; **inapplicable** in Tier A and recorded as inapplicable |
| his `log1p` Huber loss | OmniFold requires weighted BCE; his loss is an `E_avail` regression objective with no counterpart | **not ported.** His arm keeps his optimizer, schedule, clipping, batch |
| his `max_particles` 33 + batch-time first-N truncation | our cap is 12, applied at dump time | Tier A uses our cap for both; a raised cap is a Tier-B variable |

### 7.2 Port checks — forward, gradient, and update

Revision 1 checked forward only. Forward agreement does not establish that **training** is
equivalent: an optimizer or initializer difference reproduces forward outputs and diverges
after one step. All three are required, reusing the shape of the tail-validation battery:

| id | check | criterion |
|---|---|---|
| P-1 | parameter count and per-layer shapes | **exactly equal** |
| P-2 | **forward** outputs after transferring his weights into the port | ≤1e-5 max abs, float64, on 1,024 fixed inputs including fully-masked and single-token rows |
| P-3 | **gradient** agreement w.r.t. every parameter, same loss, same inputs | tolerance set by a **measured step-size sweep**, per the earlier finite-difference lesson — not asserted |
| P-4 | **weight-update** agreement after one optimizer step, same optimizer state | ≤ the tolerance P-3 establishes, reported per tensor |
| P-5 | masked slots cannot reach the output | exact |
| P-6 | repeatability and checkpoint reload | bitwise |

**Any P-* failure stops the campaign.** A port that cannot be shown to train like his code
is not his configuration.

### 7.3 Training-budget fairness

Frozen definition, because "fair" is otherwise decided after the fact:

* **the fairness axis is example presentations** — equal epochs over the same training
  subsample, so both arms see each event the same number of times. His batch is 2048 and
  ours 512, so his run has **4× fewer optimizer steps**; his cosine schedule is defined
  over `max_steps`, so `max_steps` is **derived from the fair budget**, never copied from
  his job script.
* **equal tuning**: 4 trials per arm, each arm's own published/adopted setting as trial 1,
  on a tuning slice **disjoint** from both evaluation halves. A trial that touches an
  evaluation half voids the stage.
* **wall-clock and GPU-hours are recorded as cost and are never the fairness axis.** If
  his arm costs 20× more per epoch, that is a finding to report, not a reason to shorten
  his training.
* batch size is part of each arm's configuration and is **not** equalized; it is one of
  the things being compared.

### 7.4 Inference on a small sample

* the statistic is the **paired** difference in recovery across estimator seeds;
* intervals use the **t distribution with n−1 df**, not normal quantiles — at n ≈ 8 the
  normal understates the interval by ~15 %;
* sample size is set by the **iterative t-based rule** (solve `n` with `t_{n−1}`, re-solve
  until stable), not a closed-form normal expression;
* sizing uses the **upper one-sided 80 % confidence bound on σ** from the pilot, not the
  point estimate — with 4 pilot seeds the χ² interval on σ is wide, and sizing on the
  point estimate under-powers the final stage about half the time.

### 7.5 Pilot uncertainty and what the interval covers

Stated next to every interval in the final deck:

**The reported interval covers training-seed variability at a fixed evaluation sample.**
It does **not** cover test-sample uncertainty — both 2 M halves are fixed by split seed 7
and identical across arms, which is what makes the design paired and also what removes
that term from the interval. It does not cover MC statistical uncertainty, flux or
detector systematics, or the prior-dependence band on Tier-2 cells. The pilot's σ is
itself an estimate from few seeds and its uncertainty is carried into sizing (§7.4), not
ignored.

---

## 8. Reusable preparation versus completing the comparison

### 8.1 Reusable preparation — Tier A, ≤70 GPU-h

Every item is needed by the complete comparison too, which is why it is preparation and
not a detour:

| item | reused by the full comparison? |
|---|---|
| port of his backbone to our engine + P-1…P-6 | **yes** — the same port runs the Tier-B arm |
| V1 hadronic injection, specified and implemented | **yes** — it is the primary endpoint |
| V2 fold-forward recorder (`OI-125`) | **yes** |
| fairness definition, freeze machinery, t-based sizing | **yes** |
| cost calibration of **his** backbone in our engine | **yes — and it is what makes §8.2 answerable** |
| a Tier-A comparison at our representation | partly: it is a *result about architecture and recipe*, and a control for Tier B |

**Tier A is optional.** Its result is a genuine sub-conclusion — "his architecture and
recipe, at our representation, are / are not better" — but it is **not** the deliverable
and must never be presented as the configuration decision.

### 8.2 What completing the comparison requires

| work | blocker | cost |
|---|---|---|
| representation export (R-1 or R-2) | **Agent A** | A's effort; ours is the join + §3.3 verification |
| re-dump at a raised cap with overflow telemetry | none — ours | one dump re-run over 221 GB |
| pretrained checkpoint (P1/P3) | **Gregor** (R2) | none if supplied |
| final comparison at his **real** backbone | the cost ratio below | **unresolved** |

**The cost of completing the goal is not 70 GPU-h.** What decides it is one ratio `r`:
the per-evaluation cost of his backbone relative to ours, in our engine, on GPU.
Revision 1 implied `r ≈ 1`. The 58.7× parameter ratio suggests it might be ~80×. **Both
are wrong**, and I measured enough to say so.

`receipts/step-cost-scale.json` times one forward+backward of each model at matched token
count, at **two batch sizes**, with the second batch as a control on overhead dominance:

| batch | ours | PET2-small | ratio | PET2-medium | ratio |
|---:|---:|---:|---:|---:|---:|
| 64 | 175.2 ms | 278.2 ms | **1.6×** | 1338.4 ms | 7.6× |
| **512** (production) | 386.1 ms | 2255.3 ms | **5.8×** | 15792.6 ms | 40.9× |

The ratio **moves by 3.6× across an 8× batch change**, so the small-batch figure was
measuring framework overhead, not the models — the script says so in its own verdict
field rather than letting a reader take 1.6× as the answer. This is **CPU and
cross-framework** (PyTorch against TensorFlow, with a known-slow optimizer path on this
Mac), so it is not the GPU ratio. What it does establish:

* the **parameter ratio is a bad proxy** — 58.7× in weights is nowhere near 58.7× in step
  cost, because our model is so small that both sides carry large fixed overheads;
* at production batch the paper's small backbone is **single-digit multiples**, not tens,
  of ours — so `r ≈ 6` is the working expectation and the complete comparison is
  **plausibly affordable**, which revision 1 could not have said either way;
* **medium (P3) is a different cost class** at ~41× and should not be assumed in scope.

Sizing the final stage at 8 paired seeds, with `c` = our per-evaluation cost (~1.5 GPU-h,
itself to be confirmed in stage 2):

| `r` | final comparison ≈ `8c(1 + r)` | verdict against 274 GPU-h remaining |
|---:|---:|---|
| 2 | 36 GPU-h | comfortable |
| **6** (working expectation, P2/P1) | **84 GPU-h** | **feasible**, and the basis for planning |
| 20 | 252 GPU-h | at the ceiling; nothing else fits |
| 41 (P3 medium) | 504 GPU-h | **out of reach** without a new allocation |

**Stage 2 is a go/no-go on the goal, not a formality**, and it is cheap precisely because
everything before it is preparation. Until `r` is measured on GPU in one framework, no
total is quotable and this proposal quotes none — but the campaign should be planned
against `r ≈ 6`, not against the parameter ratio.

---

## 9. Stages and gates

| stage | work | cost | gate to proceed |
|---|---|---:|---|
| 0 | specify V1's injection variable and protocol; draft the freeze; file R-1 with Agent A; send R1–R3 to Gregor | 0 | **Joseph ratifies V1 and δ** |
| 1 | port his backbone; P-1…P-6 | 0.5 GPU-h | all P-* pass |
| 2 | **cost calibration: one evaluation per arm; measure `r`** | 3 GPU-h | `r` measured; §8.2 re-costed; **go/no-go on completing the goal** |
| 3 | equal-budget tuning, 4 trials per arm | 12 GPU-h | both arms frozen; no evaluation half touched |
| 4 | variance pilot, 4 paired seeds × 2 arms; V2 recorder exercised | 12 GPU-h | upper-bound σ admits δ within stage 5 |
| 5 | Tier-A matched comparison, 8 paired seeds | 24 GPU-h | — |
| | contingency | 18 GPU-h | |
| | **Tier-A ceiling requested** | **≤70 GPU-h** | of 290, with 16.0 consumed |
| 6+ | **Tier B — the complete comparison** | **not costed; see §8.2** | R-1 landed, R2 obtained, `r` known, and a separate authorization |

---

## 10. Stop conditions

1. Any port check P-1…P-6 fails.
2. Stage 2's measured `r` puts the complete comparison outside the available allocation —
   **report that and stop**; do not raise the ceiling, narrow the endpoint, or widen δ.
3. Either arm fails absolute adequacy (§6.1).
4. The pilot's upper-bound σ cannot resolve δ inside stage 5.
5. Any safeguard V2–V9 fails and is not attributable to a defect fixable in contingency.
6. Limits exhausted. **Repaired submissions count as retries.** No automatic relaunch.
7. The endpoint, δ, `δ_switch`, the decision rule or the samples would have to change —
   that is a new approval, not a mid-campaign amendment.

---

## 11. Prerequisites and owners

| id | prerequisite | owner | blocks |
|---|---|---|---|
| **R1** | the commit and configuration behind arXiv:2604.12364 | **Gregor** | whether any result speaks about his *published* method |
| **R2** | `best_model_pretrain_s.pt` / `pretrain_m.pt` + hashes + a weights licence | **Gregor** | **P1 and P3 entirely**; the paper's transfer claim |
| **R3** | his `E_avail` definition in writing | **Gregor** | any numeric comparison against his reported values |
| **R-1** | three event-key branches `ev_run/ev_subrun/ev_gate` on the dump trees | **Agent A** (owns `runEventLoopOmniFold.cpp`) | the whole representation half, cheaply |
| R-2 | typed-object vector branches on the dump trees | **Agent A** | the alternative to R-1 |
| **R4** | authorization to read Gregor's 16 global branches from the AnaTuples | **Joseph** | his event-global block |
| **R5** | disposition of `OI-71` | **Joseph / PET lane** | whether `VL100` may be quoted at all |

**I have contacted no one.** R1–R3 are messages to Gregor and R-1/R-2 a request to Agent
A; sending them is Joseph's call.

---

## 12. What the final deck recommends

The final deck leads with the configuration the **matched evidence** supports — **his if
it earns it** under §6.3, ours if it earns it under §6.2, and neither if §6.4's
inconclusive row holds. It states, in this order: the selected configuration; the matched
evidence with its interval against δ and `δ_switch`, plus the signed/scatter
decomposition; the safeguard table; and the conditions under which the conclusion holds —
which tier was compared, which adaptations were forced, what the interval covers, and
every unresolved prerequisite.

Pre-committed now, so neither can be softened later: **if his configuration wins by more
than `δ_switch`, the deck recommends his and says so in the title**; and **if he wins by
less, the deck says he won and that we retained ours anyway, naming the switching costs.**

PET remains method development throughout. Nothing here is a publication adoption, an
uncertainty product, a central-value change, a Gate-6 action, or a discharge of `OI-71`.
