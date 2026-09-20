# PET typed-descriptor semantic audit — closed matrix, 2026-09-01

**CITABLE FOR:** the field-by-field readiness classification in §2-§4; the uniform
transformation/mask/presence behaviour in §5; the six resolutions in §6; the shared-frontend
assessment in §7; the go/no-go matrix in §8; the minimum eligible R1 field set in §9; the five
producer questions in §10; and the retractions in §11.

**NOT CITABLE FOR:** authorization to train, to normalize for production, to scan payloads, to
implement ParT, or to take any Gate-6 action. Not a fitness finding, a readiness finding, a gate
movement, a covariance construction or adoption, or a publication claim. **PET remains diagnostic
and method-development, not a publication uncertainty product** (Joseph, 2026-08-20). No field is
"adopted" by being classified READY here; a readiness class is a statement about semantics, not a
grant.

---

## 0. Provenance — read this before quoting any number

Three evidence tiers appear throughout and are never merged:

| tag | meaning |
|---|---|
| `[DOC]` | Official MINERvA tuple documentation: `MinervaExpt/Tuple-Documentation`, `MAD_tuple_MainDoc.csv`. Its README says it is **"a work in progress"**, so an absent row means *no citable definition*, not *no such branch*. Secondary official inventory (names, C++ types, data/MC/truth presence flags, no semantics): `MinervaExpt/CCQENu:utilities/tuple_finder/Input_Files/allCCQENu.csv`. |
| `[CODE]` | Executable code in this repository, cited `file:line`. |
| `[M60]` | **Read-only PyROOT payload measurements by peer session `minerva-omnifold-60`, 2026-09-01.** That lane had pscratch payload access; **this lane did not, and has independently reproduced none of these numbers.** Single-source until a second lane re-measures. Its probes: `~/mad_probe*.py` on its NERSC home. |
| `[INF]` | Inference by this lane, labelled as such and not measured. |

**What this lane did verify itself:** all `[CODE]` citations; all `[DOC]` rows (fetched directly);
and the *arithmetic* of several `[M60]` results — the recipe deviation modes, the ordering-rate
reconciliations, the per-pid count partitions, and the collinearity substitutions. Arithmetic
reconciliation is not reproduction of a measurement.

**Pinned to `main@71ea5c3ec22c3e0401a24bce4bb494df9bd68b46`.** Verified at HEAD `4a3b53a5`:
`git diff 71ea5c3e HEAD -- nd-unfolding/pet/typed_descriptors.py
nd-unfolding/pet/typed_descriptor_keras.py nd-unfolding/pet/typed_descriptor_source_smoke.py
nd-unfolding/pet/TYPED_DESCRIPTOR_STATUS.md nd-unfolding/tests/test_typed_descriptor*.py` is
**empty** — all seven artifacts are byte-identical to the pin, so every `[CODE]` claim below is live
at both shas. Re-run that diff before quoting; other lanes move `nd-unfolding/` frequently.

---

## 1. What the committed contract is

`typed_descriptors.py:511,530,553` — three families, **27 fields, 36 raw scalar components, 82
projector-input columns**:

| family | fields | raw components | `feature_width` |
|---|---|---|---|
| photons | 13 | 15 | 30 |
| blobs | 6 | 8 | 18 |
| prongs | 8 | 13 | 34 |

The **51** in `TYPED_DESCRIPTOR_STATUS.md` is not a field count: it is `3 x (token_embedding_dim 16
+ 1 count)` (`typed_descriptor_keras.py:407`, `:283`), and `13 + 51 = 64` reproduces that document's
`m_reco(num_evt=64)`. Family slices in the augmented output: photons `13:30`, blobs `30:47`,
prongs `47:64`. Schema digest at the pin: `60966a9090b4e86d45f181e913e5d1ab1761c9256a882f8160025dbd489afd08`.

---

## 2. Photons — owning object: the pi0 -> gamma gamma reconstruction

`[DOC]` Branch Group `Pi0`, type `Double`, **`MC Only? = No`** (filled in data and MC), tree
`MasterAnaDev`.

| contract field | source branch | unit / convention | reconstruction-level meaning | class |
|---|---|---|---|---|
| `direction` (3) | `gamma{1,2}_direction[3]` | unitless; **unit-normalized, \|d\|=1 to 1e-15, exactly p-hat** `[M60]` | "3D vector of the gamma1 direction based on the energy barycenter composing the shower" `[DOC]` | **READY** |
| `energy_tracker` | `gamma{i}_energy_trkr` | MeV `[DOC]` | subdetector reconstructed energy; "**Not properly calibrated** User should rebuilt from individual gammas" `[DOC]` | R-L |
| `energy_ecal` | `gamma{i}_energy_ecal` | MeV `[DOC]` | as above; `energy_ecal / evis_ecal = 3.2367`, one distinct value `[M60]` | R-L |
| `energy_scal_x` | `gamma{i}_energy_scal_X` | MeV `[DOC]` | as above; ratio to `evis_scal_X` = 5.1474, one distinct value `[M60]` | R-L |
| `energy_scal_uv` | `gamma{i}_energy_scal_UV` | MeV `[DOC]` | as above; ratio to `evis_scal_UV` = 8.9688, one distinct value `[M60]` | R-L |
| `evis_tracker` | `gamma{i}_evis_trkr` | MeV `[DOC]` | "pre-calibration energy"; **the only evis field NOT recoverable from its energy partner** — `energy_trkr/evis_trkr` varies, mode 1.326 `[M60]` | R-L |
| `evis_ecal`, `evis_scal_x`, `evis_scal_uv` | `gamma{i}_evis_*` | MeV `[DOC]` | pre-calibration; **exactly collinear with their `energy_*` partners** `[M60]` | **M/D — collinear** |
| `energy_hcal`, `evis_hcal` | `gamma{i}_*_hcal` | MeV `[DOC]` | "(=0 by default)" `[DOC]`; **exactly 0.0 on 15771/15771 present photons, min=max=0.0, three files** `[M60]` | **M/D — structurally constant** |
| `dedx` | `gamma{i}_dEdx` | **MeV per plane, 1 plane = 2.5 cm; dE not passive-corrected** `[DOC]` | "dE/dX measurement using the first 4 planes of the shower" `[DOC]`; `-999` on some present photons `[M60]` | R-L |
| `time` | `gamma{i}_time` | **unit unknown — the official doc says so itself**; ns-scale range `[M60]` | "Average time of the blob with respect to the start of the slice (not sure about the unit)" `[DOC]`. **Origin undemonstrated** — same range as `vtx[3]`, not same origin `[M60]` | R-L |

**Slot semantics — the documented ordering is refuted.** `[DOC]` defines `gamma1_E` as "the highest
energy reconstructed gamma" and `gamma2_E` as "the lowest". Measured over both-present events:
`gamma1_E < gamma2_E` in **848 of 8854 (9.58% pooled)** across three playlist files and both roles
(252/2533 1A data, 293/3226 1A MC, 303/3095 1B data), **zero ties**, relative margins to **0.988**
`[M60]`. See §6(g) for the supported mechanism. **Consequence: the slot index is not a reliable
leading/subleading label, and a "leading photon" feature keyed on slot 1 is wrong in ~1 event in 10.**

**Energy independence.** Of the ten photon energy fields only **five are independent** `[M60]`: the
tracker pair (ratio varies) plus one member each of ecal / scal_X / scal_UV; hcal contributes none;
and `gamma_E` is redundant on top (§6a). The committed contract feeds five exactly-redundant value
columns plus their validity bits through the projector — harmless for expressiveness, but it makes
the input covariance singular, produces z-normalized columns that are exact affine transforms of
each other, and makes any later reading of weight magnitude as feature importance meaningless across
a collinear pair. **Collinearity is recorded to the precision `[M60]` reported; the rounding was not
stated for the scal_X and scal_UV pairs, and the ratios are measured on the files that lane ran, not
established as tuple-wide constants.**

---

## 3. Blobs — owning object: the MasterAnaDev **neutron candidate**

`[DOC]` Branch Group **`Neutron Branches`**; `MasterAnaDev_BlobTotalE_sz` is documented "Number of
**Neutron Candidates** (size of following vector)". All six rows `MC Only? = No`. **Neither the
committed contract nor `TYPED_DESCRIPTOR_STATUS.md` records that this family is the neutron-candidate
reconstruction**; the pinned Gregor `DATASET.md` calls it "calorimetric energy deposit (no particle
hypothesis)", which is at best incomplete.

| contract field | source branch | unit / convention | reconstruction-level meaning | class |
|---|---|---|---|---|
| `position` (3) | `MasterAnaDev_Blob{X,Y,Z}` | length, **mm** `[INF]` — not stated `[DOC]` | "X, Y, Z ... position in plane of candidate" `[DOC]`. **70% of blobs have `is_3d == 0`, and among those `BlobY` is exactly 0.0 in 48.7% vs `BlobX` 0.6%** `[M60]` — ~34% of blobs carry a structurally undefined component encoded as an exact zero | **M/D** (see below) |
| `time` | `MasterAnaDev_BlobT` | time; **226-15289 ns** `[M60]`; origin not stated `[DOC]` and **undemonstrated** `[M60]` | "Time ... of candidate" `[DOC]` | R-L |
| `time_position` | `MasterAnaDev_BlobTPos` | **length, bounded at exactly +/-1054.5318 mm in every file** `[M60]` | **"Transverse position in plane of candidate"** `[DOC]` — a SPATIAL coordinate. The contract's field name and its unit string `"tuple-native time-position (unit unresolved)"` (`typed_descriptors.py:540`) both assert a false meaning | **M/D until renamed** |
| `total_energy` | `MasterAnaDev_BlobTotalE` | MeV `[INF]` | "Total Visible Energy (**Calibrated, non-passive corrected**) of the clusters in the candidate" `[DOC]` | R-L |
| `is_3d` (cat 0,1) | `MasterAnaDev_BlobIs3D` | raw `Int` code | "Is the neutron candidate a reconstructed object with 3D position (multiple views)" `[DOC]` | R-L — **see dependency** |
| `cluster_count` | `MasterAnaDev_BlobNClusters` | count, `Int` | "Number of Clusters within the candidate" `[DOC]`; declared continuous and z-normalized | R-L |

**`blobs.position` is silently FALSE-VALID, and the contract cannot express the fix.** `0.0` is not
in the sentinel set and `position` carries `mask_policy="all_components"`
(`typed_descriptors.py:533-538`), so a blob with `BlobY` exactly 0 is marked **fully valid** with a
meaningless component — the mirror of a false-missingness bug, firing at ~34%. The key needed to mask
it (`is_3d`) *is* in the contract, but masks are per-component and sentinel-derived only, so
"Y invalid when `is_3d == 0`" is inexpressible. This is a structural gap, not a parameter choice.

**DEPENDENCY (do not prune):** `is_3d` is the **sole** masking key for `position`. `position` is M/D
*because* `is_3d` exists to remedy it. Dropping `is_3d` for parsimony removes the remedy and strands
the row.

**Blobs are the best-documented family** — all six fields have official definitions. Their only unit
gap is that `[DOC]` states no units for the Neutron position/time rows.

---

## 4. Prongs — owning object: a reconstructed prong and its selected particle hypothesis

**No `prong_*` row exists anywhere in `MAD_tuple_MainDoc.csv`.** The only official trace is the
CCQENu branch inventory: `n_prongs` `Int_t` **Data=1 MC=1 Truth=0**; `prong_part_score` `Double_t`;
`prong_part_mass` `Double_t`; `prong_part_charge` `Int_t`; `prong_part_pid` `Int_t`; `prong_part_E`
and `prong_part_pos` `vector<vector<double>>`; and **`prong_nParticles`**, which the contract never
reads.

| contract field | source | unit / convention | reconstruction-level meaning | class |
|---|---|---|---|---|
| `position` (3) | `prong_part_pos[0:3]` | **(x, y, z) in mm** `[M60]` | order settled; components 0,1 signed at +/-O(10^3) | R-L |
| `time` | `prong_part_pos[3]` | **ns** `[M60]` | **same clock as the reco vertex, DEMONSTRATED**: `pos[3] - vtx[3]` median -0.703 ns (data), -0.216 ns (MC) `[M60]` | R-L |
| `four_momentum[0:3]` | `prong_part_E[0:3]` | `(px, py, pz)` **MeV** `[M60]` | component 2 large and positive (beam axis) | R-L |
| `four_momentum[3]` | `prong_part_E[3]` | MeV | **E = sqrt(p^2 + m_hyp^2), determined by (px,py,pz, pid)** `[M60]`. Also a four-way pid separator: 105.658 / 938.272 / 1.0 / 0.0 for pids 3 / 8 / 13 / {0,-999} `[M60]` | **M/D unconditionally** (see below) |
| `dedx` | `prong_dEdXMean` | **unresolved.** MeV/cm ruled out; MeV-per-plane plausible, unproven `[M60]` | mean dE/dx. `-999` in **75.5%** of 3853 prongs; valid median 5.69 / 5.74, p95 23-25, **max 500.8** `[M60]` | R-L, tail control required |
| `score` | `prong_part_score` | declared "unitless" | **undocumented everywhere** | **AIR** |
| `mass` | `prong_part_mass` | declared energy | **deterministic in `pid`** (105.658 for pid 3, 938.272 for pid 8); `-1` in 26.9% `[M60]` | **M/D — redundant against `raw_pid`** |
| `charge` (cat -1,0,1) | `prong_part_charge` | raw code, `Int` | measured code set **{-999, 0, 1, 2}**; **`2` in 44.3%**; nonzero **only** for pid 3 ({2: 5144, 1: 324, 0: 10}); pids 8/13/0 give exactly 0; pid -999 gives -999 `[M60]`. **Not a physical charge.** Declared `(-1,0,1)`: `-1` never fires, `2` is undeclared | **M/D — vocabulary refuted** |
| `raw_pid` (cat 0,3,8,9,13) | `prong_part_pid` | raw uninterpreted code, `Int` | see below | **R-L as identity-only, five conditions** |

**`four_momentum[3]` is strictly dominated.** If `raw_pid` is retained, component 3 adds exactly zero
information over components 0-2 plus the categorical. If `raw_pid` is dropped to withhold the
hypothesis, component 3 reintroduces it. There is no configuration in which keeping it helps.
It is also not one quantity: a hypothesis-mass energy for pids 3 and 8, an effectively-massless
`|p|` for pid 13 (19.0% of prongs, built on a **1 MeV** value while `prong_part_mass` reads `-1`,
disagreeing in 2207/2207) `[M60]`, and exactly 0.0 for the null slots. Pooling those into one mean
and scale would be a normalization-level version of averaging unlike distributions.

**`raw_pid` — what is and is not established.** Numeric identity is stable and preserved. Physical
meaning: **`3` = muon (mass 105.658) and `8` = proton (mass 938.272)**, identical in all 24 files
`[M60]`; `13` carries the `-1` mass sentinel and is **not** resolvable by mass; `0` is an unset slot;
`-999` is a fully invalid slot; **`9` is never observed.** The pinned Gregor `DATASET.md` table
("3=Pion, 8=EM shower, 13=Muon-like") is **refuted by the tuple's own mass field** — do not cite it,
and do not substitute GEANT3 codes (which would read 3=e-, 8=pi+, 13=n) either. Vocabulary
provenance: `categories=(0,3,8,9,13)` (`typed_descriptors.py:579-585`) was born in the **synthetic**
commit `65e179eb`, before any real row was read, with no recorded derivation; `9` traces only to
`CHARGED_PION_PIDS = {8,9}` in the pinned source, which contradicts that source's own node-type
table on code 8.

Conditions on the R-L class: (i) drop or explicitly mark unevidenced the `9` channel; (ii) treat `0`
as a null slot, not a class; (iii) instrument unknown-channel occupancy (nothing currently measures
it); (iv) attach no physical label anywhere downstream; **(v) two prongs with the same `raw_pid` are
not guaranteed comparable** — the stored hypothesis is selected from up to **5** (`prong_nParticles`
reaches 5, >1 in 35% of data and 52% of MC entries) by a rule the tuple does not record `[M60]`.

**FOUR PID LEAK CHANNELS, at unequal strength.** `four_momentum[3]` recovers pids 3, 8 and 13 exactly
in the forward direction, merging only the null slots (and the reverse direction has intruders: 23
pid-3 and 5 pid-8 zeros, **1A only**). `mass` separates three classes, two named. `charge` is
**one-directional**: nonzero implies pid 3, catching 5468/5478 = 99.82%, but `charge == 0` is
uninformative. The `dedx` **validity bit** is exact in one direction — pid 13 always valid
(2207/2207), pids 3/0/-999 never valid (0/5478, 0/536, 0/454; by role, data pid-3 0/2880 and MC
pid-3 0/2598 across 12 playlists each) — and probabilistic for pid 8 (26.7%). **Exception counts are
reported beside their own populations and are deliberately not totalled**: 15 sqrt-mass exceptions and
10 charge misses come from the 24-file x 300-entry pass; the 23/5 converse failures come from 1A only.

**CONCLUSION: no configuration of the current prong field set withholds the reconstruction's particle
hypothesis from the model.** Any "mask the PID" ablation over this field set would be measuring
something other than what it claims. One field — `four_momentum[3]` — is sufficient on its own, which
makes its M/D the necessary action rather than one of four mitigations.

**No per-prong truth link exists in MAD.** Covering search `[M60]`: **153** prong-named branches in
data, **153** in MC, set difference empty in both directions; `prong_TruePID`, `prong_HasTruth` and
`prong_GEANTTrackNum` (present in NuECCQE-flavour tuples) are **absent**, as is `prong_llr_score_vec`.
The only dEdX siblings are `prong_dEdXMean` and `prong_dEdXMeanFrontTracker`. So no truth crosstab can
identify what pid 13 physically is — it is a producer question by construction, not by our
inconvenience.

---

## 5. Transformation, mask and presence behaviour — uniform, with exceptions named

Stated once because it is identical for all 27 fields.

- **Sentinel -> mask.** `-999.0`, `-9999.0` and any non-finite value set validity `False`; the stored
  value is replaced by `0.0` **after** the mask is formed (`typed_descriptors.py:498-506`).
  Categoricals must additionally be integer-valued.
- **`mask_policy`.** `independent` per component, except `photons.direction`, `blobs.position`,
  `prongs.position`, `prongs.four_momentum` = `all_components` — one bad component invalidates the
  whole vector.
- **Both sentinel codes are load-bearing and mean different things** `[M60]`: **`-9999` marks
  whole-object absence** (all 13 gamma scalars plus all three `direction` components together, in
  12561/15259 data and 16542/20000 MC entries), while **`-999` marks per-field missingness on a
  PRESENT object** (`gamma*_dEdx`). So `all_components` on `direction` is correct rather than
  incidental.
- **Sentinel-in-a-physical-range is theoretical, not live** `[M60]`: exact `-999.0`/`-9999.0` occurred
  **zero** times in `prong_part_pos`, `prong_part_E`, all six `MasterAnaDev_Blob*` branches, or `vtx`,
  despite `-999` lying inside the mm range (`BlobTPos` bounded at +/-1054.53 mm). Recorded as
  downgraded.
- **Normalization.** Valid-components-only per-component mean/std, fitted **only** by an
  inventory-aware caller on predeclared training reco-MC `pass_reco` rows
  (`PRODUCTION_NORMALIZATION_FITTING_POLICY`, `:29`); the module exposes **no** production fitter.
  Zero-variance components fall back to scale 1. Categoricals are never normalized. **Fitting is
  strictly per family**, so fields on a shared physical clock get independent means and scales.
- **Feature build.** Invalid components are **exactly 0.0** in both implementations (NumPy
  `np.subtract(..., where=mask)`; Keras `tf.where(mask, values, means)`), plus one explicit validity
  bit per component. Pinned by `test_masked_values_cannot_change_the_pooled_representation` and
  `test_masked_numerical_values_have_no_influence`.
- **Unknown categorical codes stay VALID on a dedicated unknown channel**; sentinels mask to
  all-zero with validity 0. Pinned by `test_component_masks_and_unknown_pid_identity` (code 42 ->
  `[0,0,0,0,0,1]`) and `test_raw_pid_codes_and_sentinel_mask_survive`.
- **Presence is structural only** — `__present__` / `TOKEN_PRESENT_KEY`, never inferred from any
  feature including dE/dx (`test_prong_presence_is_independent_of_dedx_and_other_masks`). **The
  real-row producer never sets it**, so `token_mask` is all-`True` and `counts` is the tuple's raw
  declared multiplicity, not a count of good objects.
- **Parity boundary.** The NumPy reference and the Keras adapter are parity-tested only *through*
  `prepare_features` (`test_tensor_feature_preparation_matches_committed_contract`). Past that they
  differ by construction: `np.tanh` (`typed_descriptors.py:1183`) vs a relu MLP
  (`typed_descriptor_keras.py:408`). **There is no end-to-end numerical parity claim available**, and
  the module docstring says so.

### Object presence, per family

| family | rule | source | status |
|---|---|---|---|
| photons | `gamma{i}_E > 1e-5`; non-finite `gamma{i}_E` **raises** | `typed_descriptor_source_smoke.py:37,869-874` | **INCOMPLETE — see §6d** |
| blobs | index `<` the common `*_sz`; all eight `_sz` must agree exactly, fail-closed | `:893-907` | clean; no per-blob quality gate — every neutron candidate is a token |
| prongs | index `< n_prongs`; **no filter** | `:924-930` | **diverges from the pinned source**, which drops `pid in {-999, 0}` and `E < 1e-6` ("Remove the weird prongs with zero energy"). Our prong multiplicity is systematically higher |

---

## 6. The six explicit resolutions

### (a) Are component photon energies suitable while canonical `gamma*_E` stays excluded? YES — the exclusion is LOSSLESS, by exact arithmetic.

`gamma_E == energy_trkr + energy_ecal + energy_hcal + energy_scal_X + energy_scal_UV` exactly,
**15771/15771** present photons across three files, worst deviation **identically 0 MeV** `[M60]`.
With hcal exactly 0 always, that is four fields. So `gamma*_E` carries **zero** information beyond
fields the contract already holds.

`[DOC]` independently flags `gamma1_E` **"Not properly calibrated"** and supplies a replacement:
`gamma1_energy_trkr*.97 + gamma1_evis_ecal*3.1880501 + gamma1_energy_scal_UV*.97 +
gamma1_energy_scal_X*0.97`. **That is a recommended replacement, not a description of the branch** —
tested and refuted as an identity: relative deviation is bimodal at exactly `-0.0300` and
`-0.0150307`, matching in **0 of 668** and **0 of 710** `[M60]`.

Both modes are now fully explained, and this lane reproduced the arithmetic: with
`energy_ecal/evis_ecal = 3.2367`, `3.1880501*evis_ecal = 0.9849693*energy_ecal`, so the official
recipe is the branch's own four components under coefficients `(0.97, 0.9849693, 0.97, 0.97)` against
the branch's implicit `(1,1,1,1)`. `1 - 3.1880501/3.2367 = 0.0150307` is exactly the ECAL coefficient
gap; `0.97 - 1 = -0.03` is the other three, seen when `evis_ecal == 0`.

**Therefore both the canonical value and the officially recalibrated value are computable from the
four `energy_*` fields alone, with no `evis` field required.** Combined with `direction` being exactly
p-hat and `gamma_P/gamma_E == 1` (massless-treated) `[M60]`, a properly calibrated photon
four-momentum is fully reconstructible inside the existing field set as `E_recal * n_hat`.

### (b) Does raw `prong_part_pid` have stable reconstruction semantics across data and MC? The CODE IDENTITY does; the PHYSICAL LABELS do not, and must not be attached.

See §4. Codes 3 and 8 are identifiable by mass as a 24-file invariant; 13 is not; 9 never occurs; 0
is a null slot. The pinned source's labels are refuted by the tuple. Branch presence is officially
`Data=1 MC=1 Truth=0`, and `[M60]` confirms every branch of this family present with an identical
title in all 24 files (data 3687 branches, MC 4102; `Blob*MCPID` exists in data as a dummy).

### (c) Do blob/prong position, time, four-momentum, dE/dx, score, mass and charge have defensible units and parity?

Defensible **within** a family — each normalizes independently and nothing arithmetically mixes
families. **Not parity across families**, in three specific ways:

1. Two fields named `dedx` are different quantities: photon `MeV` per 2.5 cm plane `[DOC]` vs
   `prong_dEdXMean`, unit **unresolved** `[M60]`. **Do not record them as demonstrably the same unit.**
2. Three fields named `time` have three origin statuses: prong time is same-clock-as-vertex
   **demonstrated**; photon time is slice-relative per `[DOC]` with origin **undemonstrated**; blob
   time origin **undemonstrated**. Matching ranges are not a shared origin.
3. Only prongs carry a `four_momentum`; blobs deliberately do not
   (`test_raw_contract_avoids_disallowed_interpretations` asserts `"four_momentum" not in
   blob_fields`). Correct: the pinned source *manufactures* a blob pseudo-momentum by normalizing the
   position vector and scaling by energy, and this contract rightly refuses to import that fiction.

Units are documented for photon energies (MeV) and photon dE/dx; inferred (mm / ns / MeV by MAD
convention) for blob and prong position and time, with `[M60]` confirming mm and ns for prongs.

### (d) Object-presence definitions — the photon rule is INCOMPLETE.

`gamma{1,2}_E` takes **three** states, not two `[M60]`: `-9999` (absence), `> 1e-5` (present), and
**exactly `0.0` with a filled non-sentinel direction** — 225/30518 slots (0.74%) data and 306/40000
(0.77%) MC. `PHOTON_PRESENCE_THRESHOLD = 1e-5` classifies the third state as absent.

That third state is a genuine reconstructed object missing only its energy scale: `time` **filled** in
225/225 and 306/306; `direction` norm exactly 1.000000000000; `dedx` a real value in 142/225 and
181/306; and **all ten** energy fields exactly 0.0 with `gamma_P == 0` `[M60]`.

**Absence is per EVENT, not per slot** — the two slots go absent together, always (12561 == 12561;
16542 == 16542) `[M60]`. Joint slot states (A absent, Z zero-energy, P present):

| | AA | PP | ZP | PZ | ZZ |
|---|---|---|---|---|---|
| 1A data (15259) | 12561 | 2533 | 36 | 69 | 60 |
| 1A MC (20000) | 16542 | 3226 | 48 | 110 | 74 |

**`count == 1` is a gate artifact, never the reconstruction producing one photon** — it arises only
when exactly one slot is in state Z: 105 events (0.688%) data, 158 (0.790%) MC. Anyone reading the
photon count column as a physical multiplicity misreads every count-1 row. And `ZZ` events (60 / 74)
are gated to **zero** photons while holding two filled unit directions, two filled times and usually
two dE/dx values — the discard is not confined to count-1 rows.

**Disposition:** keep the drop for R1 — a zero-four-momentum token contributes only an angle with no
scale and would put a fabricated multiplicity into the count column — but make it an **explicit,
recorded choice with its measured rate**, not an inherited threshold. Nothing currently counts
filled-but-discarded slots. If a later lane wants those tokens the correct gate is
`direction != -9999` with energy masked, **never** a lowered `E` threshold, which would admit them
with a fabricated energy scale.

Blob and prong presence: see §5. `counts` is a raw declared multiplicity in all three families.

### (e) Do unknown categorical codes remain valid inputs, or must they be masked? KEEP THEM VALID on the unknown channel. Do not mask.

Masking would collapse "a code we cannot label" into "no value" — two different states. For
`raw_pid` the unknown channel is the only safe home for a code whose meaning we refuse to assert. And
it strictly dominates the pinned source's behaviour, which **raises `ValueError`** on any prong pid
outside `{3,8,13}`.

**But the vocabularies are mis-specified and the mis-specification is measured, not theoretical:**
`charge` declares `(-1,0,1)` while the measured set is `{-999,0,1,2}` with **`2` at 44.3%** — nearly
half the tokens on that field land in the bucket reserved for codes we cannot label `[M60]`.
**Required:** instrument unknown-channel occupancy in production. Its absence is exactly why this went
unnoticed.

### (f) Minimum scientifically eligible R1 field set — see §9.

### (g) Slot ordering (arose during the audit; recorded because it changes how the photon family may be used).

`[DOC]`'s energy ordering is refuted at 9.58% (§2). The supported mechanism is that **slot assignment
happens on pre-calibration visible energy, before `gamma_E` is recomputed** `[M60]`:

| ordering variable | agrees / 8854 | rate |
|---|---|---|
| `sum(evis_*)` | 8621 | **97.37%** |
| `gamma_E` | 8006 | 90.42% |
| `sum(energy_*)` | 8006 | 90.42% — **identical, positive control** for the §6a sum identity |
| `evis_trkr` alone (strict) | 7156 | 80.82%, 437 ties |
| `dEdx` | ~63% | |
| `time` | ~46% | below chance |

`sum(evis_*)` rescues **697 of the 848** `gamma_E` violations (82.2%). The `sum(energy_*)` row is a
genuine instrument validation: the §6a identity **predicts** 8006 = 8006 before the test is run, so
the probe is confirmed to be reading the branches and population claimed.

**The mechanism is supported and incomplete.** Of the 233 residual violations, a near-tie explains
about half — 48.1% sit under a 10% margin against a 4.6% base rate (10.5x enrichment; 14.0x under
5%; 0% below 0.001, so not a floating-point artifact) — but p75 = 0.344 and max = 0.977, so **~121
are gross** and no tie-break accounts for them. The ECAL-discreteness hypothesis gets only 1.29x.

**And there is a hard counterexample the residual analysis could never see.** A Z slot has all ten
energy fields at exactly 0.0, hence `sum(evis_*) == 0`; under strict visible-energy ordering a
zero-sum slot can occupy slot 1 only if the other is also zero-sum (the `ZZ` cell). Yet `ZP` exists:
**36/36 and 48/48** with the present slot at `sum(evis_*) >= 4.25 MeV` (data) and `>= 1.71 MeV` (MC)
against exactly 0.0 in slot 1 `[M60]`. These 84 events sit **outside** the 8854 both-present
population, because a Z slot fails the presence gate. No margin, no tie-break, no floating-point
story. `PZ` is consistent (69/69, 110/110) and `ZZ` is a degenerate tie (60/60, 74/74). Closed
structurally as well: **no subdetector ever has `evis == 0` while `energy != 0`**, zero occurrences,
so positive calibrated energy always implies positive visible energy `[M60]`.

**Two slot asymmetries are COROLLARIES of the ordering, not independent evidence.** Zero-energy states
land in slot 2 about twice as often (36/105 = 34.3%, z = -3.22; 48/158 = 30.4%, z = -4.93), and slot 1
has ECAL energy 3.17x more often than slot 2 (22.8% vs 7.2%) `[M60]`. Both are *predicted* by an
ordering on visible energy — higher visible energy both reaches the ECAL more often and is less likely
to calibrate to zero. **Do not count them as separate evidence.** The layered statement that ships:
**no exposed quantity *orders* the slots exactly, and at least one is systematically *asymmetric*
between them — and the second does not license a rule that picks slot 1.**

**Unrelated legacy defect, recorded because a cross-check would reach for it.**
`gamma1_E_Old == gamma2_E_Old` in **8854/8854** events, every file — the legacy energy branches are
not slot-distinct at all, and `[DOC]`'s description of `gamma2_E_Old` reads *"Legacy reconstructed
energy of **gamma 1**"*, which looks like a transcription slip and is a faithful description of a
defective branch `[M60]`. The committed smoke never binds `_Old` (verified: `grep _Old` over
`typed_descriptor_source_smoke.py` returns nothing), so **no contract row is affected** — but any lane
using `_Old` as an independent cross-check would silently get gamma 1's value twice.

---

## 7. Shared frontend assessment

Current behaviour: **raw count**, **segment sum**. `typed_descriptor_keras.py:377-381`; NumPy mirror
at `typed_descriptors.py:1194-1195`. Unaffected by any payload measurement.

### (i) Raw count vs `log1p(count)` + frozen normalization -> ADOPT `log1p` + frozen normalization.

The count enters as the 17th column of each family block, **unnormalized**, while the 13 event
columns it augments are z-normalized to O(1) and the tests exercise a 90-blob row
(`test_empty_native_miss_and_ninety_blob_row_are_uncapped`). `log1p` maps `0 -> 0` and `90 -> 4.51`,
is monotone and invertible (no information lost), compresses the multiplicity tail; frozen
train-reco-MC statistics then put the column on the event block's footing, consistent with the
module's declared fitting policy. **The transform must be inserted at the `counts` tensor, before the
`enabled` multiply at `:381`** — done there, `C0`'s exact-zero property is preserved for either
transform.

### (ii) Segment sum vs mean pooling + explicit count -> mean+count is the better single change; `sum (+) mean (+) count` strictly dominates both.

### (iii) Does mean-plus-count preserve what sum-plus-count represents? YES information-theoretically, NO representationally. Both halves matter.

- **Information: preserved exactly.** `mean = sum/count` for `count > 0`, `sum = mean*count`, and
  `count == 0` is identified by the count column itself (empty-segment convention gives `sum = 0`,
  `mean := 0`). The map is a bijection on the represented support.
- **Representation: not equivalent.** Sum is natively **extensive** — a total-energy-like quantity is
  a *linear* function of the pooled block. Under mean+count the same quantity needs a **product**,
  which a fixed-capacity MLP only approximates. Mean is natively **intensive** — per-object shape is
  available without dividing out multiplicity.
- **Stability: mean wins decisively, and by more than is generally appreciated.** The final token
  layer is **relu** (`:408`), so token embeddings are **non-negative**; a segment sum of non-negative
  vectors grows monotonically with multiplicity, so multiplicity enters the block **17 times over**
  (16 pooled columns plus the count) and the 51-column block's magnitude is unbounded against a
  13-column O(1) event block. That is exactly the `multiplicity-dependent segment-sum magnitude` gate
  in `TYPED_DESCRIPTOR_STATUS.md`, and mean pooling closes it.
- **Recommendation:** if the 51-wide shape is negotiable, concatenate `sum (+) mean (+) count` (33 per
  family, 99 total) — information-complete, keeps the extensive quantity linear, bounds the intensive
  part. It changes the contract width and the `C0`/`C1` control geometry, so it is a decision, not a
  silent fix.

### The `C0`/`C1` control has an exact degeneracy.

For any row whose three families are all empty, the enabled path produces a segment sum over zero
tokens (= 0) and `count = 0`, and the disabled path produces the same zeros — so **all 51 columns are
byte-identical in both arms.** The arms differ only on rows with at least one object.
`TYPED_DESCRIPTOR_STATUS.md`'s "footing-matched" claim is true about widths and normalization and
silent about this. Concretely for photons: the photon block is all-zero (`AA` + `ZZ`) in **82.71%** of
1A data rows and **83.08%** of 1A MC rows `[M60]`.

---

## 8. Go / no-go matrix

| item | verdict | binding reason |
|---|---|---|
| Excluding canonical `gamma*_E` from features | **GO — lossless** | exact four-field sum identity, 15771/15771 `[M60]` |
| Photon component energies as R1 inputs | **GO** | both the canonical and the officially recalibrated energy are computable from the four `energy_*` fields |
| `gamma*_E` as the presence gate | **GO with a recorded gap** | robust to the mis-calibration, matches the pinned convention — but misses the third state (§6d) |
| Photon presence rule as written | **NO-GO — incomplete** | three states, not two; 0.74% / 0.77% of slots discarded with three filled fields each |
| `energy_hcal`, `evis_hcal` | **NO-GO** | exactly 0.0 on 15771/15771; drop is exactly lossless |
| `evis_ecal`, `evis_scal_x`, `evis_scal_uv` | **NO-GO — collinear** | single fixed ratio to their `energy_*` partners, to the reported precision |
| `evis_trkr` | **GO — keep** | the one evis field not recoverable; its varying ratio makes the calibration factor an event-level observable, accessible only if both members are kept |
| `photons.direction` | **GO** | unit-normalized to 1e-15, exactly p-hat |
| Slot index as a leading/subleading label | **NO-GO** | documented ordering refuted at 9.58%; wrong ~1 event in 10 |
| Permutation-invariant pooling over photons | **GO — costs nothing** | there is no reliable ordering to discard |
| `gamma*_E_Old` as an independent cross-check | **NO-GO** | `gamma1_E_Old == gamma2_E_Old` in 8854/8854 |
| Blob family described as "calorimetric blobs" | **NO-GO** | `[DOC]` group = `Neutron Branches`; these are neutron candidates |
| `blobs.time_position` as committed | **NO-GO** | `[DOC]`: `BlobTPos` = "Transverse position in plane"; bounded at +/-1054.5318 mm. Rename -> GO |
| `blobs.position` as committed | **NO-GO** | ~34% carry an exactly-zero `BlobY` marked fully valid; the fix is inexpressible in the current mask model |
| `blobs.is_3d` | **GO — do not prune** | sole masking key for `blobs.position` |
| `blobs.time`, `total_energy`, `cluster_count` | **GO with recorded limitation** | officially defined; units inferred |
| `prongs.position` (3), `four_momentum[0:3]` | **GO with recorded limitation** | mm and MeV confirmed; order settled |
| `prongs.time` | **GO with recorded limitation** | same clock as the reco vertex, demonstrated |
| `prongs.four_momentum[3]` | **NO-GO — strictly dominated** | redundant if `raw_pid` kept; a leak if `raw_pid` dropped; and not one quantity across classes |
| `prongs.mass` | **NO-GO — redundant** | deterministic in `pid` |
| `prongs.charge` | **NO-GO — vocabulary refuted** | measured `{-999,0,1,2}`, `2` at 44.3%, declared `(-1,0,1)` |
| `prongs.score` | **NO-GO pending author** | undocumented everywhere |
| `prongs.dedx` | **GO with recorded limitation** | unit unresolved; 75.5% sentinel; max 500.8 vs median 5.69 demands tail control |
| Any physical label on `prong_part_pid` | **NO-GO** | pinned source refuted by the tuple's own mass field; `[DOC]` silent |
| `raw_pid` category `9` | **NO-GO as evidenced** | never observed; no recorded derivation |
| `raw_pid` as an identity-only code | **GO under five conditions** | §4 |
| A "mask the PID" ablation over this field set | **NO-GO** | four leak channels; `four_momentum[3]` alone is sufficient |
| Unknown codes staying valid on the unknown channel | **GO** | correct design; dominates the pinned source's crash |
| Unknown-channel occupancy instrumentation | **MISSING — REQUIRED** | 44.3% of one field is in that bucket and nothing measures it |
| Uniform `(-999,-9999)` sentinel default | **GO** | both codes load-bearing with distinct roles; in-range collision measured at zero |
| Uncapped ragged storage + explicit counts | **GO** | strictly dominates the pinned top-20/top-10 + aggregate token |
| Masks-before-substitution, structural presence | **GO** | invalid components exactly zero, tested both implementations |
| `counts` read as a good-object multiplicity | **NO-GO** | raw declared multiplicity; `__present__` never set by the producer |
| Raw count column | **NO-GO** | unnormalized against a z-normalized event block |
| Segment sum with relu embeddings | **NO-GO** | unbounded multiplicity-dependent magnitude |
| `C0`/`C1` as a footing-matched control | **CONDITIONAL** | byte-identical on all-empty rows; 82.71% / 83.08% for the photon block alone |
| NumPy <-> Keras end-to-end parity | **NOT AVAILABLE** | parity only through `prepare_features`; tanh vs relu past it |
| A shared time statistic across families | **NO-GO pending measurement** | prong/vertex same-origin demonstrated; gamma and blob same-RANGE only |
| Any data/MC or playlist DISTRIBUTIONAL claim from the committed smoke | **NO-GO** | data 1B, MC 1A, 16 entries each, receipt self-classifies `FIXED_SAMPLE_TELEMETRY_NOT_AN_ESTIMATE`, zero distributional tests |
| Branch presence / title parity across data and MC | **GO** | `[DOC]` `MC Only? = No` on all gamma and Blob rows; `[M60]` identical titles in all 24 files |

---

## 9. Minimum eligible R1 field set — 14 fields, 22 raw components

| family | keep | raw comps |
|---|---|---|
| photons (8) | `direction` (3), `dedx`, `time`, `energy_tracker`, `energy_ecal`, `energy_scal_x`, `energy_scal_uv`, `evis_tracker` | 10 |
| blobs (4) | `time`, `transverse_position` (**renamed** from `time_position`), `total_energy`, `is_3d` | 4 |
| prongs (2) | `position` (3), `four_momentum[0:3]` | 6 |

Optional, admissible, not minimal: `blobs.cluster_count`; `prongs.time` (now demonstrated);
`prongs.dedx` with tail control; the three collinear `evis_*` fields (zero added information).

**Excluded and why:** `energy_hcal`/`evis_hcal` structurally zero; `evis_ecal`/`evis_scal_x`/
`evis_scal_uv` collinear; `blobs.position` pending an `is_3d`-conditional mask; `prongs.mass`,
`charge`, `four_momentum[3]` redundant or leaking; `prongs.score` and `raw_pid` pending author input.

**Cost of the rename:** field names enter `_schema_json()` (`typed_descriptors.py:794`), so renaming
`time_position` changes `descriptor_schema_digest()` and **invalidates
`typed_descriptor_schema_sha256: 60966a90...`** in
`docs/orchestration/state/pet-typed-descriptor-fixed-source-smoke-20260901.json`. That is a re-cut,
not an edit.

---

## 10. The five producer questions — for the MINERvA contact, not answerable from code, docs or payload

1. **What is `prong_part_pid` code 13?** 19.0% of prongs; dE/dx valid in 2207/2207; no recorded mass
   in 2207/2207; four-momentum built on a 1 MeV value in 2207/2207. Four fields perfectly determined
   by one code, fully stereotyped behaviour, unresolved identity. Codes 3 and 8 are muon and proton by
   mass, so the pinned source's "muon-like" for 13 has no standing.
2. **What selects the stored hypothesis?** `prong_nParticles` reaches 5 and exceeds 1 in 35% of data
   and 52% of MC entries, while the `prong_part_*` leaves are counted by `n_prongs` — so one
   hypothesis per prong is stored and *which* one is unrecorded.
3. **What is `prong_dEdXMean`'s unit and expected range?** MeV/cm is ruled out; MeV-per-plane is
   plausible but unproven. Valid median 5.69 / 5.74, p95 23-25, max 500.8, and valid only for pids 8
   and 13.
4. **What do `prong_part_charge` codes mean?** Measured set `{-999, 0, 1, 2}`; `2` at 44.3%; nonzero
   only for pid 3. Not a physical charge.
5. **What orders the two gamma slots, and is slot assignment expected to survive a candidate whose
   energy reconstruction yields exactly zero?** `[DOC]` documents gamma1 as highest-energy and gamma2
   as lowest, but `gamma1_E < gamma2_E` in 848/8854 (9.58%) across three files and both roles, no
   ties, margins to 99%. `sum(evis_*)` orders correctly in 97.4% against `gamma_E`'s 90.4% and rescues
   82% of the violations, consistent with assignment before calibration; a near-tie explains ~half the
   233 residual and ~121 are gross; and 84 `ZP` events (slot 1 at exactly 0.0 across all ten energy
   fields, slot 2 at >= 1.7 MeV) are a clean violation no version of the visible-energy rule
   accommodates.

**Ben's answers outrank every number in this document**, including the ones this lane reconciled.

---

## 11. Retractions made during this audit — recorded rather than quietly fixed

Six claims by this lane were withdrawn under peer measurement. They are listed because the failures
share two mechanisms worth naming.

1. **"The three `time` fields have possibly-different origins, no cross-family parity"** -> revised to
   "one shared clock" on a peer summary -> **withdrawn back**, because only prong/vertex was
   demonstrated same-origin; gamma and blob were same-RANGE only. **The original position was closer
   to right than the revision.**
2. **"prong `dedx` at 5.69 is quantitatively consistent with MeV-per-plane, so the photon and prong
   `dedx` are the same unit."** Withdrawn: 2.5 cm is the pitch, not the ~1.7 cm active scintillator;
   the valid sample is proton-hypothesis-weighted, not MIP-dominated; and a per-prong mean is not a
   per-plane sample.
3. **"The official recalibration recipe is an identity for `gamma*_E`."** Proposed as a test, and the
   test refuted it. The stronger four-field sum identity replaced it.
4. **"The documented gamma ordering holds in the both-present population and is violated only in the
   `ZP` cell (0.24%)."** Withdrawn: refuted at 9.58%, ~40x larger. This lane asserted the
   discriminating test instead of running it.
5. **"The `ZP`/`PZ` asymmetry is an independent structural finding."** Withdrawn: it is a corollary of
   an ordering on visible energy, and counting it separately would double-count.
6. **"The photon presence rule matches the pinned convention exactly, defensible."** The provenance
   claim was correct and the completeness claim was not; a third state existed in the data.
7. **"The census edit's schema bump serves the 30->38 widening."** Wrong: the widening shipped
   separately at `865b42d7` and was already flagged in the committed file.

**Mechanism A — checking a rule against its cited authority instead of against the world.** Items 4
and 6. Confirming that code matches its documented source is not confirming that the source covers
the domain.

**Mechanism B — a matching magnitude offered as a demonstration with no discriminating prediction.**
Items 1 and 2. A shared range is consistent with two different origins; 5.69 MeV is consistent with
several units. **Operational check: ask what the number would look like if the hypothesis were
false.**

A third, from the other side: `[DOC]` was **wrong once** (the gamma ordering) and **right once where
it looked wrong** (`gamma2_E_Old` describing gamma 1). Two failures in opposite directions from one
reflex. **Do not resolve a documentation claim by expectation in either direction — test it or mark it
untested.**

---

## 12. What this document does not establish

- **No payload was read by this lane.** Every `[M60]` row is single-source and unreproduced here.
- **No distributional data/MC or playlist comparison exists** for the committed smoke: it binds data
  from playlist **1B** and MC from **1A** (`typed_descriptor_source_smoke.py:56,73`), 16 entries each,
  and its receipt self-classifies the object counts
  `FIXED_SAMPLE_TELEMETRY_NOT_AN_ESTIMATE`. `[M60]`'s later passes control playlist properly; the
  committed receipt does not.
- **No gate moves.** Gate 2 remains FAIL, Gate 6 remains BLOCKED, no `C_ML` exists, and no scalar-5D
  covariance is adopted. A readiness class here is not an adoption.
- **Two measurements remain unrun and are claimed by nobody:** per-event `gamma1_time - vtx[3]` and
  `BlobT - vtx[3]`, which would settle whether the gamma and blob clocks share the vertex origin or
  only its range.
- **This document has no `docs/orchestration/MANIFEST.tsv` or `MANIFEST-overrides.tsv` row**, and
  neither does `TYPED_DESCRIPTOR_STATUS.md`. Both are therefore invisible to the router. Registering
  them touches digest-bound generated files and was outside this lane's scope; it is a follow-up, not
  an oversight to be silently inherited.
