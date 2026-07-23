# Round 1 — Gregor Source Archaeology (findings)

Role: `gregor_source_archaeologist`. Read-only. No scientific conclusions from AUC.
Target: https://github.com/gregorkrz/minerva-ml

## 0. Inspected revisions, timestamp, method

- **Pinned commit:** `af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed` (2026-07-16, "fix event viewer MC particles").
- **Upstream HEAD at inspection:** `fc9a099d3c9c060f03cef293c294f9de4eb019cd` (2026-07-20, branch `master`, "small plotting fixes").
- **Inspection timestamp:** 2026-07-23T12:52Z (UTC). Full local clone at `~/local-research/gregor-audit/minerva-ml`.
- Method: direct code reading of model/preprocessing/dataloader/training/checkpoint sources; two parallel delegate audits (codex = dataset pipeline with file:line citations; Antigravity/gemini = web provenance + licenses); all load-bearing facts independently re-verified by me.
- Citation convention below: `path:line` refers to the pinned tree; view as
  `https://github.com/gregorkrz/minerva-ml/blob/af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed/<path>#L<line>`.

## 1. Model core (PET2 / OmniLearned) — concern 1

- **Implementation:** vendored `src/models/omnilearned/{__init__,network,layers,diffusion,utils}.py`. Class `PET2` (`network.py:20`), sub-modules `PET_body`, `PET_classifier`, `PET_generator`. Built by `create_omnilearned_model` (`src/scripts/train.py:1069`).
- **Size presets** (`utils.py get_model_parameters`): small = base_dim 128 / heads 8 / 8 transformers; medium = 512 / 16 / 12; large = 1024 / 32 / 28. `num_tokens=4` readout tokens.
- **MINERvA wiring** (`train.py:1085`): `input_dim=ol_num_feat=4` (η,φ,log pT,log E only), `pid=use_pid` (default **True**, `train.py:577`), `pid_dim=ol_pid_dim=8`, `add_info=True` `add_dim=ol_num_add=5` (dE/dx,x,y,z,t), `conditional=use_cond` `cond_dim=ol_num_cond(10)+e_sum_dim`, `num_coord=coord_dim=2`, interaction matrices default **off** (`--ol-interaction`/`--ol-local-interaction` store_true default False).
- **Tensor signature:** `PET2.forward(x, y, cond, pid, add_info)` (`network.py:146`). Per batch: `x`=(B,N,4) continuous kin, `pid`=(B,N) long, `add_info`=(B,N,5), `cond`=(B,cond_dim). Classifier/regression path sets the diffusion time token to zero (`torch.zeros_like(time)`, `network.py:172`); a random `time` is still drawn every forward (`network.py:157`) — consumes RNG state but does not affect classifier/regression output.
- **Global-feature injection:** `cond` is MLP-embedded and **prepended as one token** (`PET_body.forward`, `network.py:597-599`). `add_info` and `pid` are **added** to the per-particle embedding (masked) (`network.py:591-595`).
- **Normalization:** `DynamicTanh` (a learned tanh norm) is the default `norm_layer`; pre-norm residual AttBlocks. Input is embedded via `InputBlock` MLP. There is **no dataset-level standardization** in the model; feature scaling is the log/÷10000 transforms done in preprocessing (see §2).
- **Objective** (`train.py:1860-1874`, `2328-2336`): regression → `MSELoss` / log-MSE / log1p-Huber / plain `HuberLoss` (config-dependent, with optional binned/inverse-frequency sample weights); classification → `CrossEntropyLoss` (optional class weights). Heads: linear to 1 (regression) or `N_classes` (classification).
- **Optimizer/scheduler** (`train.py:2344-2361`, `928`): `AdamW` **or** `Lion` (`pytorch_optimizer`), `lr=1e-4`, `weight_decay=0.01`; `LambdaLR` = linear warmup (1000 steps) + cosine decay; optional AMP (`autocast`+`GradScaler`).
- **Determinism** (`train.py:920`): `set_seed` sets `torch.manual_seed`/`np.random.seed`/`cuda.manual_seed_all` only. **No** `torch.use_deterministic_algorithms` / `cudnn.deterministic`. `--seed` defaults to `None`; DataLoader `shuffle=True` uses global RNG with no explicit `Generator` → training batch order not reproducible unless `--seed` is passed (data split seed defaults 42 and **is** reproducible).

## 2. Feature/label definitions and units — concern 2

Per-particle token = 10 cols, built in `src/dataset/preprocessing.py` (`:546-606`). Cross-checked against `DATASET.md`; **units are largely undeclared in code** (see caveats).

| idx | value | transform / units |
|---|---|---|
| 0 | η | from 3-momentum, clipped [-10,10] (`preprocessing.py:257-275`) |
| 1 | φ | `atan2(py,px)` rad (`:270-275`) |
| 2 | `log(pT+1e-6)` | **raw momentum units, no MeV→GeV conversion** (`:257-284`) |
| 3 | `log(E+1e-6)` | raw energy units; `E<1e-5` raises (`:249-255`) |
| 4 | PID/node type | integer 0..7 in a float array (`:422-445`) |
| 5 | dE/dx | photon/prong `log(|dedx|+0.1)` (−999→0, >100→100); muon/blob **0** (`:387-406`) |
| 6-8 | x,y,z | `/10000`; muon/photon **0**; raw spatial unit undeclared (`:343-344,381-406`) |
| 9 | t | `/10000` all types; raw time unit undeclared (`:343-344`) |

- **PID scheme:** 0 muon, 1 photon, 2 blob, 3/4/5 prong (raw prong PID 3/8/13), 6 aggregated blob, 7 aggregated prong (`:422-437,494-528`).
- Sources: muon = `muon_corrected_p` (MINOS-corrected); photon = `gamma{1,2}_*`; blob = `MasterAnaDev_Blob{X,Y,Z,T,TotalE}` → direction·E massless pseudo-momentum; prong = `prong_part_E`/`prong_part_pos`/`prong_dEdXMean`.
- **Global features (16)** = 7 base + 3 reco summaries + 6 per-PID log energy sums (`:611-659`; `constants/dataset.py` base dim 10). Cols: 0-2 log calorimetry (fuzz/iso-blob/hadron-recoil), 3-5 log passive recoil (id/od/sum ÷10000), 6 raw `improved_nmichel`, 7 reco-muon-present flag, 8 γγ invariant mass (MeV) if exactly 2 photons, 9 charged-pion prong count (raw pid∈{8,9}), 10-15 log ΣE per PID {2,3,4,5,6,7}.
- **Truth labels (15)** (`:790-824`): 0 `mc_incomingE`, 1 `mc_intType`, 2 `E_nu/E_mu_reco` (−1 if invalid muon), 3 `mc_current`, 4 CC π class, 5/6 `n_pi_plus/minus`, 7 is_multi_pion (source-flagged as wrong), 8/9 E_available with/without muon, 10 `n_pi_zero`, 11-14 selected MC pion (px,py,pz,E). **All 15 require MC-truth branches** (`mc_*`, `mc_FSPart*`).

## 3. Dataset construction / OmniFold contract — concern 3

- **Source:** hard-coded FHC Medium-Energy **Standard MC** playlists **1A–1G, 1L–1P** (12; 1H–1K absent) at `/pscratch/.../MediumEnergy_FHC_StandardMC_Playlist/` (`preprocess_dataset.py:26-44`); only the `MasterAnaDev` TTree is read (`:100-103`). `download_data.py` *could* fetch a real-data playlist if the prefix is changed, but nothing in the ML pipeline reads real data. **Pipeline is MC-only.**
- **Serialized `.pb` = exactly `{data, truth_labels, global_features}`** (`preprocessing.py:599-606`). **No event identifiers** (run/subrun/gate) and **no per-event MC weights** (no flux/PPFX/GENIE/xsec/POT). Events are positional-index only, and split membership is index-based (`split_dataset.py`).
- **Filtering:** interaction-type cut `mc_intType ∈ {1,2,3,4,8}` is applied at **split** time, not preprocessing (`split_dataset.py:30-34`). Muon token requires `muon_corrected_p[:,0/1] ≠ -999` (MINOS match); **a missing muon drops only the token, the event is kept**. Overflow removal (`|val|>1e6`) applies to muons only. Truncation: default keeps top-150 tokens by log E with **no aggregation** (`--use-max-blobs-and-prongs` default False); aggregation path CLI defaults `max_blobs=100`, `max_prongs=10` (both differ from DATASET.md's 20/10).
- **OmniFold contract feasibility (from prepared rows):**
  - reco observables — **present**; truth observables — **partial** (scalar labels + one pion 4-vec; no full truth particle collection); real **data leg — absent**; per-event **weights — absent**; **pass-reco / pass-truth / miss / fake flags — absent**; stable **event ID — absent**.
  - A truth-defined **background** is constructible when the signal is expressible via saved truth columns (current/intType/pion counts). A reliable **"miss"** (truth-passes/reco-fails) population **cannot** be certified from saved rows: no pass-reco/pass-truth flags, and it is unverified that `MasterAnaDev` holds the full truth denominator.
  - `binned_loss_weights.py` = inverse-frequency class-balancing weights computed by the loader on demand — **not** physics weights, and not stored in rows.

## 4. Checkpoints / lineage — concern 4

- **Names/location:** `best_model_{pretrain_s,pretrain_m}.pt` from `https://portal.nersc.gov/cfs/m4567/checkpoints/` (`utils.py PRETRAINED_URL`, `load_pretrained_omnilearned`). No published hashes in code.
- **Accessibility:** could **not** be probed — HTTP returned connection failure/timeout from both audit environments (my sandbox HTTP=000; delegate curl (28) timeout). **Unverified**: cannot confirm public retrievability, size, or hash; may be an egress restriction rather than a server 404.
- **Loading (`utils.py _filter_partial_state`):** skips all `out.*` keys (**heads always reinit fresh**); loads `body`/`classifier_head`/`generator_head` with `strict=False`, shape-filtered → dimensionally tolerant fine-tuning.
- **Frozen vs trainable:** OLS/small (`--use-pretrained pretrain_s`) = **full fine-tune** (whole body trainable, fresh head). OLM/medium = **backbone frozen** (`model.body.requires_grad=False`), head-only training (`train.py:1109`). OLS_RW = random init.
- **Lineage:** generic particle-physics (jets) pretrained OmniLearned → MINERvA fine-tuned. Mapping OLS→pretrain_s, OLM→pretrain_m per `MODELS.md`.

## 5. Licenses — concern 5

- **Repo code:** **MIT**, Copyright (c) 2026 Gregor Krzmanc (`LICENSE`, identical at pin and HEAD). **Legally reusable.**
- **OmniLearned vendored code:** upstream = **`ViniciusMikuni/OmniLearned`**, **MIT** (declared in upstream `pyproject.toml` `license = {text="MIT"}`; **no standalone LICENSE file upstream**). Vendored `src/models/omnilearned/*` is a **near-verbatim copy** (only import-path edits) but carries **no per-file attribution / MIT notice** in this repo → reuse is *permitted* but the copied files omit the MIT copyright notice MIT requires. **Legally reusable with an attribution-hygiene gap.**
- **HyperScale vendored code** (`src/models/hyperscale/*`): stated upstream `github.com/gregorkrz/HyperScale` returns **404** and is absent from the author's public repo list → **upstream unavailable, license unverifiable**. Files carry no header. **Ambiguous / unavailable provenance.**
- **Pretrained weights:** no stated license; endpoint inaccessible → **license unknown, availability unverified.**
- **Dataset (published):** **`huggingface.co/datasets/gregorkrzmanc/minerva-ml`**, public, ungated, **CC-BY-4.0**; self-described as "a preprocessed version of the MINERvA **open data** release." **Legally reusable with attribution.** (Note: distinct from the private NERSC raw MC path in `preprocess_dataset.py`.)
- **Dependency licenses (inferred from imports, not a pinned manifest):** torch/numpy/sklearn/h5py/uproot/awkward/seaborn = BSD-3; einops/plotly/wandb/tqdm = MIT; requests/pytorch_optimizer/transformers = Apache-2.0; matplotlib = PSF. **ROOT/PyROOT = LGPL-2.1+/GPL** (copyleft) — used **only** in ROOT preprocessing; avoidable by consuming the HF dataset instead.
- **arXiv 2604.12364** (Krzmanc, Mikuni, Nachman, Wilkinson): abstract carries **no** code/data/weights availability statement or license.

## 6. Pin → HEAD differences — concern 6

Only **16 files** differ (`git diff af5d92ed..fc9a099d`), **all** under `src/eval/`, `plot_configs/`, `src/jobs/submit_new_dataset_jobs.py`, `tests/`. **Zero** changes to model, preprocessing, dataloader, training, checkpoint, or constants. For reproduction/integration the two revisions are **equivalent**; the delta is plotting/eval only.

## 7. Collision & masking hazards — concern 7

- **CONFIRMED — PID-0 == padding_idx collision.** `dataloader.py:620` feeds the **raw** PID column as `batch["pid"]` (muon = 0, **no +1 shift**); padding fills zeros (`_pad_or_truncate`, `:126-132`); `network.py:492` = `nn.Embedding(pid_dim=8, base_dim, padding_idx=0)`. Therefore **muon (PID 0) and zero-padding both map to the same fixed zero, non-trainable embedding row.** Of 8 PID classes only 1–7 get learnable type embeddings; the muon receives no learned type embedding and is type-indistinct from padding in that channel. Active by default. This is an **integration-boundary** defect: `padding_idx=0` is an upstream OmniLearned assumption (jet "no-particle"), while MINERvA maps muon→0. (Muon is still kept in attention via the separate col-2 mask and its kinematics; the damage is to the type-embedding signal, not token presence.)
- **CONFIRMED — pT-feature is the padding key.** The pad/attention mask everywhere is `x[:, :, 2:3] != 0` (`network.py:249,364,573`), col 2 = `log(pT+1e-6)`. A real particle with pT≈1 (raw unit) yields exactly 0 → **silently masked as padding**. Low probability but real; blobs (pseudo-momenta) are the most exposed.
- **HAZARD (to confirm vs task config) — muon ablation × mask.** `zero_muon_kinematics` (`train.py:1203`) zeros cols 0–3 (incl. col 2) for muons; combined with the col-2 mask this would **drop the muon token entirely** rather than merely blanking its kinematics. Whether this is intended for `-E-available-no-muon` runs needs config confirmation.
- **Other:** default keeps top-150 tokens by energy (or aggregation), so very-soft real objects can be truncated; NaN→0 fill on source collections can inject zero-valued kinematics that interact with the col-2 mask.

---

## STRUCTURED INVENTORY

### Inspected SHAs & primary files
- SHAs: pin `af5d92ed…`, HEAD `fc9a099d…`.
- Model: `src/models/omnilearned/{network,layers,diffusion,utils,__init__}.py`, `src/models/hyperscale/*`, `src/models/vit.py`.
- Data: `src/dataset/{preprocessing,dataloader,baseline_labels,binned_loss_weights}.py`, `src/constants/{dataset,physics}.py`.
- Scripts: `src/scripts/{train,preprocess_dataset,split_dataset,extract_baselines,download_data}.py`.
- Docs/meta: `MODELS.md`, `DATASET.md`, `Dockerfile`, `AGENTS.md`, `CITATION.bib`, `LICENSE`, `pyproject.toml`.
- External: `github.com/ViniciusMikuni/OmniLearned`, `huggingface.co/datasets/gregorkrzmanc/minerva-ml`, `arxiv.org/abs/2604.12364`.

### Verified facts
- Model class/preset/wiring/objective/optimizer/scheduler/determinism as in §1.
- PID-0 == padding_idx=0 collision and pT-feature mask key (§7) — read directly in code.
- `.pb` rows contain no weights, no event IDs, no pass/miss flags; MC-only; muon-less events retained (§3).
- pin↔HEAD differ only in eval/plot/jobs/tests (§6).
- Repo MIT; OmniLearned upstream MIT (near-verbatim vendor, no local notice); HF dataset public CC-BY-4.0 (§5) — all re-verified via primary sources.

### Inferences / unverified
- Reconstructed momentum/energy in **MeV** and spatial/time raw units behind ÷10000 — strongly implied, **not code-declared**.
- Pretrained checkpoint accessibility/size/hash — **could not be probed** (endpoint unreachable from audit envs).
- HyperScale upstream code/license — **unavailable** (404).
- Whether `MasterAnaDev` contains the full truth denominator needed for an unbiased "miss" set — **unknown**.
- Dependency licenses are import-inferred, not from a pinned manifest.

### Reuse classification
- **Legally reusable:** repo code (MIT); vendored OmniLearned/PET2 (upstream MIT — add attribution); HF dataset `gregorkrzmanc/minerva-ml` (CC-BY-4.0, attribute).
- **Technically reusable (subject to above):** the preprocessing→`.pb` schema and model wiring; but ROOT preprocessing is LGPL/GPL-encumbered — prefer consuming the HF dataset.
- **Independently reimplement only:** HyperScale ParticleViT variants (upstream unavailable → cannot lawfully copy; must reimplement from the paper if needed).
- **Unavailable / unverified:** NERSC pretrained weights (endpoint unreachable, no license/hash); raw private NERSC MC playlists.

### Questions only Gregor can answer
1. Authoritative physical units of every reco momentum/energy/position/time/dE/dx branch pre-transform.
2. Are the NERSC `pretrain_s/m` checkpoints intended to be public, and what is their license + a hash to pin?
3. HyperScale upstream: is it private/deleted, and under what license may the vendored copy be used?
4. Which MINERvA flux/xsec/generator/exposure weights should attach per event, and from which branches/friend trees? (None are currently carried.)
5. What exact truth-level and reco-level selection definitions define `pass_truth`/`pass_reco`/miss/fake/background for the intended OmniFold analysis?
6. Does `MasterAnaDev` contain the full truth fiducial denominator (events failing reco selection)?
7. Should run/subrun/gate/event IDs be retained for joining MC/reco/systematics/unfolding?
8. Known bugs: raw prong PID 9 (crashes token mapping vs counted in {8,9}); truth col-4 π-class `if/else` (resets class 1) — intended?

### Handoff to the PET2 implementation lead (no scientific conclusion prescribed)
- Treat pin and HEAD as interchangeable for model/data work (only eval differs).
- Before any OmniFold integration, resolve the **two confirmed collisions**: (a) shift MINERvA PID by +1 (reserve 0 for padding) or set `padding_idx=None`/drop it so the muon gets a real type embedding; (b) replace the implicit `col-2 != 0` pad mask with the explicit `attention_mask` the dataloader already produces, to eliminate the pT≈1 false-padding and the muon-ablation drop interaction.
- The `.pb` schema **cannot** satisfy an OmniFold reco/data/background/miss/weight contract as-is: it lacks a real-data leg, per-event MC weights, pass-reco/pass-truth flags, and stable event IDs. These must be sourced/added upstream of any unfolding work — decide with Gregor whether to extend preprocessing or obtain a differently-prepared sample.
- Weights available: OLS full-fine-tune vs OLM frozen-backbone are the two published lineages, but checkpoint retrievability is currently **unverified** — do not assume the NERSC files are fetchable until confirmed.
- Legal posture for reuse: repo + OmniLearned + HF dataset are permissively licensed (add the missing OmniLearned attribution); HyperScale is not lawfully copyable without its license; pretrained-weight license is unknown.
