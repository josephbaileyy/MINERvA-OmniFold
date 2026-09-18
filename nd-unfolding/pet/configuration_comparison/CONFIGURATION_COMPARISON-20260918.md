# Recommended PET configuration: comparison with Gregor's implementation

**CITABLE FOR:** a pinned, code-traced inventory of differences between our production
full-event PET estimator and Gregor Krzmanc's `minerva-ml` transformer, and for the
configuration recommendation that follows from it.
**NOT CITABLE FOR:** any publication adoption, any uncertainty product, any Gate-6
action, or any claim that one implementation is scientifically superior to the other.
PET remains diagnostic method development (ruled 2026-08-20).

Author: Publication Agent B (PET). Date: 2026-09-18.

---

## 0. What is pinned, and what each label means

| label | what it is | pin |
|---|---|---|
| **ours (production)** | `pet-fullevent-fps-v1`, the full-event FPS estimator the driver stamps | `nd-unfolding/pet/train_fullevent_nominal.py`, `fullevent_fps_dataloader.py`, `dump_pointcloud_inputs.py`, `omnifold_nn/omnifold/{net,omnifold}.py` at `44142e8c` (worktree `pet-direct-token-comparison`); contract at `FULL_EVENT_FEATURE_CONTRACT.md` |
| **ours (experimental)** | the four-arm representation comparison — typed descriptors, pooled/individual routing, aggregate overflow | `nd-unfolding/pet/direct_token_comparison/` and `nd-unfolding/pet/typed_descriptor*.py` at `44142e8c`. **Not deployed. No arm of it is in the production path.** |
| **ours (proposed)** | what this document recommends changing | nothing is built for the borrowed items; see §14 |
| **Gregor's** | `gregorkrz/minerva-ml` | commit **`fc9a099d3c9c060f03cef293c294f9de4eb019cd`** ("small plotting fixes", 2026-07-20), clean tree, at `/Users/josephbailey/local-research/gregor-audit/minerva-ml` |

**A pin caveat that matters.** `fc9a099` is the repository as cloned, **not** a paper
commit: the repo has no release tags and has evolved past arXiv:2604.12364. Anything
below describes the code at that commit, which may or may not be what produced the
paper's numbers. Getting the paper commit requires asking Gregor.

**Defaults versus optional features.** Everything attributed to Gregor below is the
**default** unless marked *(optional)*. Verified defaults at `fc9a099`: `--use_pid`
True, `--use_cond` on (`use_cond = not args.no_use_cond`), `--include-E-sum` True,
`--max_particles` 33, `--log1p_loss` True, `--use-max-blobs-and-prongs` **False** (so
aggregation is *off* by default and truncation to 150 is the default overflow policy).
Optional and not default: OmniLearned PET2 backbones, HyperScale ParticleViT, BERT,
pretrained initialization, `--zero-cond-feature`, `--remove-muon-kinematics`.

**The framing difference that conditions everything else.** His model is a *supervised
regressor/classifier*; ours is a *binary reweighting classifier inside OmniFold*. He has
no unfolding, no data leg, no per-event weights, and no truth-reweighting step. Several
rows below therefore have no counterpart on his side, and that is not a deficiency in
his work — it is a different problem. Where a row says "no counterpart", we cannot
borrow, only be informed.

---

## 1. Object membership, filtering, overlap, primary lepton

| | |
|---|---|
| **ours** | The cloud is **raw non-muon calorimeter clusters** (`cluster_{energy,pos,z,view,time}`, `cluster_isMuontrack==0`; `part_reco_*` after the C++ dump). The muon is **removed from the cloud** and carried as a distinguished 13-feature event block that conditions the transformer by FiLM. Truth cloud = FS hadrons, μ± and ν removed at source. |
| **Gregor's** | The cloud is **reconstructed objects**: muon (PID 0), up to 2 photons, blobs (PID 2), prongs (PID 3/4/5 from raw `prong_part_pid` 3/8/13). The muon is **a token like any other**, plus global feature 7 (MINOS-matched muon presence). Muon retained only when `muon_corrected_p[:,0:2] != -999`; missing muon removes the token, not the event. Prongs filtered on raw PID ∉ {-999, 0} and E > 1e-6. `(preprocessing.py:29-37, 150-174, 422-437)` |
| **consequence** | This is the **largest single difference**, and it sets the token budget. On the same two tuple files the **mean** non-muon cluster count is **74.6 (data) / 102.6 (MC)** against a mean typed-object count of **14.0 / 15.6** — a **5.3× / 6.6×** reduction in tokens for a description of the same hadronic system. (Medians are reported per family, not summed: blobs 4/6, prongs 1/2, photons 0/0, plus at most one muon. A sum of medians is not the median of the sum, and the receipt holds marginals only.) Our muon handling is cleaner for OmniFold: a distinguished event input cannot be truncated away, whereas an energy-ranked muon token can be. His PID-3/8/13 remap raises `ValueError` on any other surviving prong PID, and raw PID 9 is counted by his global feature 9 but has no token code — a latent crash, not a silent mislabel. `(preprocessing.py:425-434, 672-705)` |
| **evidence** | `receipts/typed-object-budget.json`; A1 receipt `direct_token_comparison/local_validation/20260918-source/source-multiplicity.json` (job 58470099, 17,930 data + 186,439 MC entries read in full); `gregor-audit/jobs/A_dataset.out.md` §1, §6 |
| **recommendation** | **Borrow the typed-object vocabulary as a candidate, do not borrow the muon-as-token choice.** Keep the muon distinguished. |
| **unresolved prerequisite** | Whether reconstructed objects preserve the calorimetric information the raw cluster cloud carries is **unmeasured**. Blobs group clusters, but nothing establishes that blobs + prongs + photons cover the same energy. Measuring that coverage on our tuples is the gate, and it is cheap (counts and energies only, the A1 pattern). |

---

## 2. Token features, PID/type encoding, missingness, padding

| | |
|---|---|
| **ours** | 5 columns: `E` (GeV), `pos` (m), `z` (m), `view` (raw 1/2/3 plane code), `time` (÷100). **No type code** — every token is a recoil cluster, so there is nothing to distinguish. Padding: zero rows; the mask authority is `E == 0`, and the loader re-zeroes view/time from the energy mask rather than trusting the dump. |
| **Gregor's** | 10 columns: `η`, `φ`, `log(pT+1e-6)`, `log(E+1e-6)`, PID code, `dE/dx` feature, `x/10⁴`, `y/10⁴`, `z/10⁴`, `t/10⁴`. PID is an 8-class learned embedding (`nn.Embedding(8, 16)`). Structurally absent fields are literal zeros (muon `dE/dx,x,y,z`; photon `x,y,z`; blob `dE/dx`). Padding: all-zero rows with mask 0. `(preprocessing.py:389-406, 546-583; dataloader.py:126-165; train.py:1030, 1743)` |
| **consequence** | His token carries **more physics per object** (direction, dE/dx, position, time, type) than ours carries per cluster, which is the natural pairing with fewer tokens. Two hazards on his side. First, **zero-filled absent fields are indistinguishable from genuine zeros** — a photon at `x=0` and a photon with no position both read 0, with no validity mask. Our experimental typed-descriptor schema serializes raw values and validity masks separately, precisely to avoid this. Second, **padded rows carry PID index 0, which is the muon code**, so the embedding returns the muon vector for padding. This is *contained*, not broken: the SDPA key-padding mask excludes those positions and readout is CLS-only, so padded embeddings cannot reach the output. It is a latent hazard that becomes live under any pooled readout. `(vit.py:334-373; train.py:1776-1800)` |
| **evidence** | `A_dataset.out.md` §1; `vit.py:334-373`; `train.py:1743, 1776-1800`; `FULL_EVENT_FEATURE_CONTRACT.md` reco-cloud table; `typed_descriptors.py:1-44` |
| **recommendation** | **Borrow the richer per-token feature set and the learned type embedding. Do not borrow zero-fill-for-absent, and do not reuse index 0 for a real class.** Reserve index 0 for padding and shift real codes by one. |
| **unresolved prerequisite** | Our `cluster_*` branches have no dE/dx or direction. A richer token needs either the typed-object branches (which exist in the tuple — A1 read them) or new dump branches. |

---

## 3. Coordinate transforms and normalization

| | |
|---|---|
| **ours** | Fixed physical divisors only: E ÷1000 (MeV→GeV), positions ÷1000 (mm→m), time ÷100, view **not rescaled** (dividing a 3-valued plane code collapses the views). Event features are **z-normalized with frozen reco-MC `pass_reco` statistics**, reused unchanged for data, validation and inference; `!pass_reco` rows are zeroed post-normalization. Azimuth is carried as `(cos φ, sin φ)`, never raw φ, at both cloud and event level (CLM-008 F10). |
| **Gregor's** | Logs and fixed divisors: `log(pT+1e-6)`, `log(E+1e-6)`, positions and time ÷10⁴. `η` clipped to [-10,10]; **raw `φ` from `atan2`, no periodic encoding**. Continuous point features then pass through a **`LayerNorm` over the feature dimension inside the encoder** (`MixedFeatureEncoder`, `use_cont_layernorm=True` for points, `False` for globals). `(preprocessing.py:257-287; vit.py:125-170)` |
| **consequence** | Two substantive differences. (a) **Periodicity**: raw φ puts −π and +π maximally far apart. In his model this feeds both the token features and the positional MLP (`pos = X[..., :2]` = (η,φ)), so the encoding is discontinuous across the wrap. We fixed exactly this defect in our own code in July. (b) **Frozen versus adaptive normalization**: OmniFold compares data against MC through a classifier, so any input transform that differs between the two legs is a fake discriminant. Frozen MC statistics make the transform provably identical; a per-token LayerNorm is also deterministic and leg-independent, so it is *safe* — but it normalizes each token across its own feature vector, which mixes an energy scale with an angle and removes absolute per-token scale. For a supervised regressor that is a defensible convenience; for our purposes it is not what we want. |
| **evidence** | `preprocessing.py:257-287`; `vit.py:125-170, 344`; `FULL_EVENT_FEATURE_CONTRACT.md` §normalization, §CLM-008 |
| **recommendation** | **Keep ours.** Recommend to Gregor that φ be encoded periodically — this is the one place where we have already paid for the lesson. Do not adopt input-side LayerNorm. |
| **unresolved prerequisite** | None for keeping ours. The φ point is a recommendation to him, not a change to us. |

---

## 4. Event globals

| | |
|---|---|
| **ours** | 13 features, all muon/vertex: `pT`, `p∥`, muon `(px,py,pz,E)`, `(cos φ, sin φ)`, `q/p`, MINOS-ok flag, vertex `(x,y,z)`. Truth side: 2 features (`truth_muon_pT`, `p∥`), separate normalization, `TRUTH_ELIGIBLE_FEATURES` enforces at construction time that no detector/MINOS feature acquires a truth counterpart. |
| **Gregor's** | 16 features: 3 log calorimetric recoil energies (`muon_fuzz`, `muon_iso_blobs`, `hadron_recoil`), 3 log passive-material recoil terms (`id`, `od`, sum), Michel count, MINOS-muon presence, γγ invariant mass, charged-pion prong count, plus **6 per-PID log energy sums** computed *after* truncation/aggregation. `(preprocessing.py:611-659; constants/dataset.py:1-5)` |
| **consequence** | The two sets barely overlap. His are **recoil/calorimetric summaries**; ours are **muon kinematics**. His per-PID energy sums are the interesting item: they are a cheap, fixed-width channel that survives truncation and carries exactly the tail information a cap discards — his own partial remedy for the overflow problem, arrived at independently. Caveat: they are computed *after* truncation (`preprocessing.py:564-594`), so with aggregation off they sum only the retained 150, not the whole event. A hazard on his side: global feature 8 (γγ mass) is a **physics-motivated composite that is zero unless exactly two photons are retained** — the model must learn that 0 means "not two photons" rather than "mass zero". His own help text for `--zero-cond-feature` also misdescribes index 3. |
| **evidence** | `A_dataset.out.md` §2; `preprocessing.py:611-659, 564-594`; `FULL_EVENT_FEATURE_CONTRACT.md` event_reco table |
| **recommendation** | **Borrow the per-PID / per-family log energy sums, computed over the *whole* event before any cap.** They are a fixed-width, cap-proof channel and cost essentially nothing. This is the cheapest candidate on the list. Do not borrow the γγ-mass-or-zero encoding without a companion validity flag. |
| **unresolved prerequisite** | Our event block is currently muon-only by design, and adding recoil summaries to `event_reco` changes `DEFAULT_EVT_FEATURES`, which Gate-4 freezes and which is inside the estimator fingerprint. That is a fingerprint change, not a free parameter — see §14. Also note `eavail`/`q3` are already dumped-but-unread pending the RESTORE Step 7 ranking; adding energy sums should be ranked in the same arm structure rather than adopted ahead of it. |

---

## 5. Pooling versus individual-object attention

| | |
|---|---|
| **ours (production)** | Not applicable — there is only one family (clusters), so no routing question arises. Every cluster is its own token. |
| **ours (experimental)** | Two arms. **Pooled**: each typed family is reduced by `tf.math.unsorted_segment_sum` to one summary token plus an explicit count column (`typed_descriptor_keras.py:390-400`). **Individual**: every typed object gets its own token. |
| **Gregor's** | Individual, unconditionally. Every object is a token; readout is a CLS token fused with an EVT token. No pooling anywhere. |
| **consequence** | **Measured, and inconclusive on accuracy.** Eight paired seeds on the four-object synthetic fixture: median **+9.7 %**, mean **+0.8 %**, seed sd **25.8 points**, 95 % interval **[−20.7 %, +22.4 %]**, paired **p = 0.50**; 6/8 seeds favourable. The cost is not inconclusive: at the real mean multiplicity (14 typed objects) individual routing costs **1.244× training / 1.257× inference**, and in the tail (87 objects) **1.879× / 1.318×**. Pooling is nearly flat in multiplicity; individual routing is not. Theory bounds the loss: the deep-sets sum decomposition is exact when the latent width is at least the set size (Wagstaff et al., ICML 2019), which at width 32 holds to K=32 — above that, pooling can in principle lose information. The relevant fraction is therefore events with **more than 32** objects in a family: **9.2 % (data) / 11.4 % (MC)** have ≥33 blobs. So the regime where pooling is not provably lossless is real but is a minority of events. |
| **evidence** | `direct_token_comparison/local_validation/20260917-matrix/matrix-summary.json` (decision `NO_PASS`, 142/146 checks); `local_validation/20260917-inference/inference-benchmark.json` (all 5 checks pass, CV ≤ 2 %); `local_validation/20260918-a3-cost/cost-half.json`; `RECOMMENDATION-20260918.md` |
| **recommendation** | **Keep pooling as the practical default; his individual routing is not shown to be better and is measurably more expensive at our multiplicities.** This is a development choice under an inconclusive result, not a finding. |
| **unresolved prerequisite** | The accuracy question is **unresolved within budget**: at the only scatter ever measured, resolving a 10-point effect needs ≈73 paired seeds ≈ 175 GPU-hours against 130 authorized. The variance pilot (≤30 GPU-h, authorized but **not launched**) exists to measure whether the scatter is small enough to make the question affordable. |

---

## 6. Caps, ordering, overflow aggregation, merged counts

| | |
|---|---|
| **ours** | One cap, applied **at dump time** in `dump_pointcloud_inputs._pad_tokens`: stable sort by energy descending, keep the top `num_part = 12`, zero-pad. Overflow is **discarded with no trace** — no count, no summed energy, no flag. |
| **Gregor's** | Two caps in series. (a) Preprocessing: if an event exceeds `max_objects = 150`, **all families are jointly sorted by `log E` and the top 150 kept**; below 150, the saved order is the *concatenation* order muon → photons → blobs → prongs, **not** energy order. (b) Dataloader: `_pad_or_truncate` keeps the **first `max_particles = 33` saved rows, without re-sorting**. *(optional)* With `--use-max-blobs-and-prongs`, excess blobs and prongs are instead replaced by **one aggregate token per family** carrying the summed four-momentum, the unweighted arithmetic mean of the five auxiliary fields, and a distinct PID (6 blobs / 7 prongs). Defaults are `max_blobs=100`, `max_prongs=10` at the CLI against `20`/`10` in the helper. `(preprocessing.py:309-339, 494-545, 564-571; preprocess_dataset.py:355-377; dataloader.py:126-132)` |
| **consequence** | Our cap is **much more binding**. On the same tuple entries our 12-token cluster cap binds in **64.1 % (data) / 84.4 % (MC)** of events and the discarded clusters carry a **median 20.8 % / 44.9 %** of non-muon cluster energy. A 33-token typed cap binds in only **9.2–16.9 % (data) / 11.4–27.2 % (MC)** — a bracket, because the receipt has marginal and not joint family multiplicities. But *his default ordering is worse than ours*: below 150 objects the retained 33 are the first 33 in concatenation order, so for a 40-blob event the prongs are dropped **regardless of energy** while low-energy blobs are kept. And his aggregate token is **optional and off by default**, and merges the auxiliary block by unweighted mean rather than energy-weighted, so a 1 GeV and a 10 MeV blob contribute equally to the merged position. |
| **evidence** | `receipts/typed-object-budget.json`; A1 receipt; `A_dataset.out.md` §6; `preprocessing.py:309-339`; our arm-D overflow spec `direct_token_comparison/OVERFLOW_SPECIFICATION-20260915.md`, `four_arm_representation.py` |
| **recommendation** | **Borrow the aggregate-overflow idea (we independently built the same thing as arm D) and test it before anything else. Do not borrow his ordering, his default-off setting, or his unweighted auxiliary mean** — use energy-ranked retention (ours) and an energy-weighted merge. |
| **unresolved prerequisite** | Two. (a) **No closure measurement of aggregation exists on either side.** Measured discarded *energy* bounds how much the cap *could* matter; it does not establish that the discarded clusters carry predictive information, and it does not establish a closure improvement. (b) Our cap is applied in the **dump**, so changing it requires regenerating the point-cloud npz — see §14. |

---

## 7. Architecture, capacity, attention structure

| | |
|---|---|
| **ours** | Vendored `omnifold_nn` PET: input encoding MLP → **K-nearest-neighbour local feature aggregation** over `coord_idx` (reco `(pos,z)`, truth `(θ,cos φ,sin φ)`) → 2 transformer blocks, 2 heads, `projection_dim = 32`, LayerScale (init 1e-3) → a head with a trainable class token and **FiLM conditioning from the event block**. **47,041 trainable parameters** (step-1 reco); 46,913 (step-2 gen); **93,954 per OmniFold iteration**. |
| **Gregor's** | `PointGlobalMixedViT`: mixed continuous+categorical encoder → **absolute Fourier positional MLP** over `(η,φ)` → 4 pre-norm blocks, 8 heads, `d_model = 128`, `mlp_ratio = 4` → CLS token fused with an EVT token. **890,130 trainable parameters** — **18.9× ours**. *(optional)* OmniLearned PET2 small/medium/large (128/8/8, 512/16/12, 1024/32/28) and HyperScale ParticleViT (RMSNorm, SwiGLU, QK-Norm). |
| **consequence** | Ours is a *very* small model, and deliberately so: it is retrained many times inside OmniFold (niter 3 × epochs 8 × 2 steps, then again for every covariance universe), so capacity trades directly against campaign cost. His is trained once per configuration. The structural difference that matters scientifically is **locality**: ours injects detector geometry through KNN in `(pos,z)`, his injects it through a Fourier encoding of `(η,φ)`. Ours encodes where a deposit *is*; his encodes which direction it *points*. For a calorimetric recoil measurement, detector-space adjacency is the better prior — but that is an argument, not a measurement. |
| **evidence** | `receipts/model-capacity.json` (measured by instantiating both models); `omnifold_nn/omnifold/net.py:39-266`; `vit.py:226-373`; `train_fullevent_nominal.py:403-407`; `MODELS.md` |
| **recommendation** | **Keep our architecture and its size. Treat capacity as an open question, not a settled one.** A 19× parameter gap is large enough that "we are under-parameterized" is a live hypothesis, and it is cheap to test one width step. |
| **unresolved prerequisite** | No width scan has ever been run for the full-event estimator. Its cost is the binding issue: capacity multiplies through every covariance universe, so a width increase must be priced against the whole UQ campaign, not one train. |

---

## 8. Initialization and pretraining

| | |
|---|---|
| **ours** | Random, `tf.keras.utils.set_random_seed(42)`, frozen in `NOMINAL_SEED_POLICY`. Estimator seed 42 fixed for the central value, vertical universes and `C_stat`, so `C_stat` varies only the Poisson replica id. No pretraining. |
| **Gregor's** | Random by default (`--seed` default `None`). *(optional)* `--use-pretrained pretrain_s / pretrain_m` loads OmniLearned foundation-model checkpoints; the `OLS` and `OLM` job identifiers use them. |
| **consequence** | Pretraining is the headline of his paper and the thing most worth borrowing in principle. In practice it is **unavailable**: audit `B_provenance` verified that `gregorkrz/HyperScale` returns 404 and the `portal.nersc.gov` checkpoint URLs time out consistently, so the weights are unreachable, unhashed, unlicensed as weight artifacts, and dimensionally unverified. Separately, a fixed seed is load-bearing for us in a way it is not for him: our seed policy is what makes `C_stat` a statistical covariance rather than a mixture of statistical and training noise. |
| **evidence** | `gregor-audit/jobs/B_provenance.out.md` items 2–3; `train_fullevent_nominal.py:47-71`; `MODELS.md` §2; upstream OmniLearned is MIT-licensed |
| **recommendation** | **Keep random init with the frozen seed.** Ask Gregor directly for the checkpoint files and their hashes before planning any pretrained arm — do not plan around a URL. |
| **unresolved prerequisite** | Checkpoint availability, a weights licence, and a dimensional match to our 5-column reco cloud. All three are unresolved; the first is a question for Gregor, not a compute request. |

---

## 9. Training objective, optimizer, regularization, stopping

| | |
|---|---|
| **ours** | Loss: **weighted binary cross-entropy** on the OmniFold classification, with a predeclared symmetric logit clip (F3). Optimizer **Adam**, base LR **1e-4** annealed to **1e-5** at the fit-time anneal adopted 2026-08-10 (CLM-012), realized LRs **asserted against the declared policy at runtime** — a recorded policy is a claim, an asserted realized LR is a measurement. `ReduceLROnPlateau(patience=1000, min_lr=1e-7)` plus `EarlyStopping` on the MultiFold patience. Batch **512**, niter **3**, epochs **8**, train subsample **2 M**. No weight decay, no dropout, no gradient clipping. |
| **Gregor's** | Loss: **Huber on `log1p(target)`** for regression (`--log1p_loss` default True), cross-entropy with class weights for classification. Optimizer **AdamW**, LR **1e-4**, **weight decay 0.01**, **linear warmup 1000 steps then cosine decay** to zero over `max_steps`, **gradient clipping at 1.0**, batch **2048**, `max_steps` 100 k default / 250 k in the job script. Dropout and attention dropout default 0. Best-validation checkpointing; no early stopping. |
| **consequence** | His recipe is the modern default and ours is not: **warmup + cosine + AdamW + grad-clip** is a materially better-conditioned schedule than constant-Adam-then-step-anneal, and costs nothing. Two reasons we cannot simply copy it. First, our LR policy is **inside the estimator fingerprint** and Gate-4 freezes it, so a change re-keys every v1 artifact including the Gate-2 target. Second, **weight decay is not innocuous for a likelihood-ratio classifier**: OmniFold's push weight is `exp(logit)`, so shrinking the logit scale biases weights toward 1 — a regularizer that is free for a regressor is a *bias* for a reweighter. Huber-on-`log1p` has no counterpart: our objective is fixed by the OmniFold construction. |
| **evidence** | `train_fullevent_nominal.py:47-71, 440-458`; `omnifold_nn/omnifold/omnifold.py:263-266, 376-386`; `train.py:927-937, 2328-2358, 2608-2615`; `FULL_EVENT_FEATURE_CONTRACT.md` §backend |
| **recommendation** | **Borrow warmup + cosine decay and gradient clipping; do not borrow weight decay** until someone measures its effect on the reweighting bias. Both are candidates, neither is adopted. |
| **unresolved prerequisite** | Any LR-policy change is a fingerprint change (Gate-4 freeze) and must be validated by a closure re-run, not asserted. The weight-decay bias argument above is an argument from the construction, not a measurement. |

---

## 10. OmniFold integration, ratio conventions, validation

| | |
|---|---|
| **ours** | Full MultiFold: step 1 reweights MC reco to data, step 2 pulls the weight back to truth, 3 iterations. Push weight `w = exp(logit)`, identically `f/(1−f)`, computed in **logit space** so the saturation tail degrades gracefully instead of overflowing to `+inf`. Background: **negweight-refined** (ρ₁ = D − B) with literal background-cloud injection at weight −w_bkg·pot_scale, refined non-negative before training; `bkg_mode="purity"` is a labelled control only, and `build_fullevent_loaders` **fails closed** without the background inventory. Data-side scalars must come from an explicit row-aligned source — a silent fallback to MC `reco_scalars` was a real defect (CLM-007) and is now fail-closed. Validation: omitted-muon stress closure PASS (L1 0.582 prior → 0.043 full-event, 13.6× better than recoil-only); ordinary self-consistency closure PASS (push median 1.059, marginal L1 0.0021). |
| **Gregor's** | **No counterpart.** No unfolding, no data leg, no per-event weight field in the serialized record, no pass-reco or pass-truth flag, and the preprocessor is hard-coded to Standard-MC directories and requires MC truth branches. Real data can be *downloaded* by his repo but is never read by the ML preprocessing path. |
| **consequence** | Nothing to borrow, and one thing to be careful about: **his rows cannot be used as an OmniFold input** without a new serialization that carries weights, a data population, and selection flags. His typed-object vocabulary is borrowable; his *dataset* is not. Also relevant if anyone tries to compare numbers: his `E_avail` uses full charged-pion energy plus K±, against our pion-KE definition — an offset of order 140 MeV per π±. Reconcile before any numeric comparison. |
| **evidence** | `omnifold.py:453-470`; `FULL_EVENT_FEATURE_CONTRACT.md` §background, §CLM-007, §P5A validation status; `A_dataset.out.md` §4, §7; `gregor-pet2-outcome` (E_avail definitional offset) |
| **recommendation** | **Keep ours in full.** If a typed-object representation is ever adopted, it must enter through our dump and loader, carrying weights and flags — not by importing his `.pb` files. |
| **unresolved prerequisite** | None for keeping ours. |

---

## 11. Training and inference cost

| | |
|---|---|
| **ours** | Nominal full-event train ≈ **1.1–1.3 GPU-h** (2 M subsample, niter 3 / epochs 8). The campaign multiplier is what matters: ≈100 `C_stat` replicas at ≈1.2 h each, ≈12 `C_ML` trains, 6–8 vertical/flux joint universes, ≈10 lateral endpoint retrains. |
| **Gregor's** | Single supervised trains, batch 2048, 100 k–500 k steps depending on preset; no covariance ensemble. |
| **consequence** | **Our cost structure is ~100× his per configuration change**, because every representation choice propagates through the whole UQ campaign. That is the real reason to prefer the cheap borrowings (energy sums, aggregate overflow) over the expensive ones (capacity, individual routing). Measured per-arm GPU costs at real multiplicities, relative to the incumbent: aggregate overflow **1.007× train / 0.978× inference** at the operating point and **0.994× / 0.998×** in the tail; individual routing **1.244× / 1.257×** and **1.879× / 1.318×**. |
| **evidence** | `local_validation/20260918-a3-cost/cost-half.json`; `FULL_EVENT_FEATURE_CONTRACT.md` §estimated cost; `local_validation/20260917-inference/inference-benchmark.json` |
| **recommendation** | Order candidate changes by campaign cost, not by per-train cost. |
| **unresolved prerequisite** | The aggregate-overflow parity figure is **at the resolution floor of that measurement** — see §13. |

---

## 12. Numerical behaviour

| | |
|---|---|
| **ours** | Bound precision policy asserted at runtime: TF32 **off**, determinism **on**, float32. Repeatability and checkpoint reload are **bitwise**. Known: CPU/GPU updated-weight agreement fails above ~12 objects in a family, and **pooled and individual fail equally** (gradients 4.96e-5 vs 4.38e-5; updated weights 1.78e-3 vs 1.68e-3 at 48 blobs), with the *pooled* arm failing first as multiplicity grows. |
| **Gregor's** | Not characterized in the audited code. Optional fp16 in the job script; gradient clipping at 1.0 is the only numerical safeguard in the training loop. |
| **consequence** | Nothing to borrow. One finding is worth recording because it kills a plausible objection: the cross-device discrepancy is **not** a property of individual-object routing. |
| **evidence** | `direct_token_comparison/local_validation/20260918-tailval/validation-final.json`; `VALIDATION_CRITERIA-20260918.json` (sha256 `abccd88b…`) |
| **recommendation** | Keep ours. |
| **unresolved prerequisite** | See §13 — the validation is incomplete. |

---

## 13. Audit of the recommendation before it becomes slides

Five corrections applied to my own earlier wording, in the order Joseph raised them.

**(a) "Aggregate overflow is free" — withdrawn.** It is not free on either axis.
*Compute*: the measured ratio is 1.007× train / 0.978× inference, but arm **B** — which
is computationally identical to arm A in the pooled configuration — reads **0.967×** on
the same measurement. So the resolution floor of that measurement is about **±3 %**, and
the honest statement is *"indistinguishable from parity at the ±3 % resolution of this
measurement"*, not "free". *Non-compute*: it requires a dump regeneration, a schema
field, a re-validation and a new estimator fingerprint. Those are the real costs.

**(b) Discarded energy does not establish closure improvement.** The 20.8 % / 44.9 %
median discarded energy share bounds how much the cap *could* matter. It does not show
that the discarded clusters carry predictive information, and it does not predict any
closure improvement. **No closure measurement of aggregation exists.** The deck states
the recommendation as "test this first", never as "this will help".

**(c) 10 of 13 released widths is incomplete validation.** The execution path is **not
validated** across the intended multiplicity range. Three widths — (0,64,2) and
(2,160,12) for the individual arm, (2,12,4) for both — failed check V5 and were not
released. The diagnosis is that the *criterion* was wrong, not the gradient: at the worst
coordinate (|grad| = 0.0215, so not a small-denominator case) the finite-difference
estimate converges on the analytic gradient as h falls — 1.69e-1 at h=3e-2, 1.84e-2 at
the frozen 1e-2, 1.67e-3 at 3e-3, **3.14e-4 at 1e-3**, rising again at 3e-4. Error
falling as h² then giving way to cancellation is textbook truncation, so the frozen
global step was simply too large there. **The criterion was not relaxed after the
failures.** Releasing those widths needs an amended per-coordinate step rule, which is
Joseph's decision. Until then the pilot's precondition — complete validation — is unmet.

**(d) Unselected source measurements do not determine selected-population behaviour.**
Every cap-binding and energy-share number comes from **two files** (data run 00010068
playlist 1B, 17,930 entries; MC run 00110000 playlist 1A, 186,439 entries), read as
**unselected, unweighted tuple entries**. The production selection and POT weighting are
not applied. The cap may bind less often in the selected population. The note's
post-truncation cluster means (11.09 / 11.15) cannot settle this, because they saturate
against the cap by construction.

**(e) Statistical quantities are labelled by what they measure.** The interval
**[−20.7 %, +22.4 %]** is a 95 % interval on the **mean paired injected-improvement
percentage across eight training seeds on the four-object synthetic fixture**. It is not
an interval on production closure, on real-data performance, or on any physics quantity.
**p = 0.50** is a paired test across **training seeds**; it measures seed-to-seed scatter
and says nothing about test-sample uncertainty, which was not separately estimated. The
**25.8-point** scatter is a **planning assumption** carried from a different fixture,
two arms and a different denominator — not measured power for the endpoint now specified.
The **±3 %** figure in (a) is a measurement-resolution estimate inferred from the A/B
null contrast, not a quoted uncertainty.

One further scope statement that belongs with all of the above: in the synthetic fixture
every generic slot is noise and all signal is typed, whereas in production the cluster
cloud carries most of the information. **Neither the direction nor the magnitude of a
synthetic effect transfers automatically.**

---

## 14. Additional comparisons that could change the recommendation

Not one experiment per difference. Four differences are decided by evidence we already
have (§3 normalization, §8 pretraining availability, §10 OmniFold integration, §12
numerics) and need no new work. What remains is ranked by *decision value per GPU-hour*.

**Zero new compute — do these first.**

1. **Typed-object energy coverage.** Do blobs + prongs + photons cover the non-muon
   cluster energy on our tuples? This is the single prerequisite gating the largest
   candidate change (§1), and it is a counts-and-energies read of branches A1 is already
   authorized for. CPU only, of order one core-hour. **If coverage is poor, the typed
   vocabulary is dead and §1, §2 and §6 collapse to the aggregate-overflow item alone.**
2. **Ask Gregor** for the paper commit, the checkpoint files and their hashes, and his
   `E_avail` definition in writing. Resolves §8 and the comparability caveat in §10 at
   zero cost. *(Not done here: I have not contacted anyone.)*

**Consolidated into one bounded proposal — a matched complete-configuration comparison.**

The remaining live items interact, and running them one at a time would be both more
expensive and less informative:

* aggregation versus truncation (§6) changes what information reaches the model;
* per-family energy sums (§4) are a *partial substitute* for the same information, so
  their value depends on whether aggregation is already present;
* individual versus pooled routing (§5) matters more when more objects survive the cap,
  so it interacts with both;
* capacity (§7) sets whether any of the above can be exploited — a 47 k-parameter model
  may simply not have room for a richer representation, which would make a per-item test
  read as "no effect" for the wrong reason.

Those four cannot be read independently. The right instrument is a **matched
complete-configuration comparison**: the current production configuration against one
assembled candidate (energy-ranked aggregate overflow + per-family energy sums + pooled
routing + one width step), scored on the same closure endpoint with the same seeds — with
single-factor arms added only for whichever factors the matched comparison shows to
matter. **This is a proposal, not an authorization request in this document**, and it must
be priced against the campaign multiplier of §11, not against one train.

**Sequencing that is already authorized and already blocked.** The variance pilot
(≤30 GPU-h) would supply the scatter that decides whether *any* of this is resolvable
inside 130 GPU-h. Its precondition is complete validation, which is unmet per §13(c). One
decision unblocks it: amend the frozen V5 criterion to a per-coordinate step rule. That
is Joseph's call, and I did not make it.

---

## 15. The recommended configuration

**Keep**, because the evidence supports them or because they are load-bearing for
OmniFold: the muon as a distinguished FiLM event input (§1); frozen MC normalization
statistics and periodic azimuth (§3); family pooling as the practical default (§5);
energy-ranked retention (§6); KNN locality in detector coordinates (§7); random
initialization under the frozen seed policy (§8); the OmniFold objective, logit-space
ratio, negweight background and fail-closed data path (§10); the bound precision policy
(§12).

**Borrow**, as candidates to test — none deployed, none adopted:

| borrow | from | why | cost | prerequisite |
|---|---|---|---|---|
| per-family log energy sums over the **whole** event | §4 | cap-proof fixed-width channel | ~0 | fingerprint change; rank alongside `eavail`/`q3` |
| aggregate overflow, energy-weighted merge | §6 | addresses a measured 21–45 % energy loss in most events | parity to ±3 % | dump regeneration; **no closure evidence yet** |
| richer per-token features + learned type embedding, index 0 reserved for padding | §2 | more physics per token, fewer tokens | unmeasured | typed-object energy coverage |
| warmup + cosine decay, gradient clipping | §9 | better-conditioned schedule, free | ~0 | Gate-4 fingerprint; closure re-run |
| one capacity step | §7 | 18.9× gap is large enough to be a live hypothesis | multiplies through the UQ campaign | price against the campaign, not one train |

**Do not borrow**: muon as a cloud token (§1); zero-fill for absent fields and PID index
0 shared with padding (§2); input-side LayerNorm and raw φ (§3); γγ-mass-or-zero without
a validity flag (§4); concatenation-order truncation and unweighted auxiliary merging
(§6); weight decay, until its reweighting bias is measured (§9).

**Recommend to Gregor**: encode φ periodically; reserve embedding index 0 for padding;
map raw prong PID 9; compute the per-PID energy sums before truncation rather than after.

**Status.** Every item above is PET method development. Nothing here is a publication
adoption, an uncertainty product, a central-value change, or a Gate-6 action.
