# DECISION 2026-09-20 — Joseph authorizes publishing the typed-descriptor semantic audit on `main`

**CITABLE FOR:** the decision to publish `nd-unfolding/pet/TYPED_DESCRIPTOR_SEMANTIC_AUDIT-20260901.md`
on `main`, and the measured scope of what that publishes.
**NOT CITABLE FOR:** any scientific claim in the audit, any PET adjudication, or any adoption.

## 1. How the file reached a commit

The file was untracked in the working tree for the whole session. It was swept into commit
`926a92a4` by an **over-broad `git add`**, not by a decision to publish it. It was already public on
the lane branch `lane/z-two-member-campaign-20260919`, whose tip is `926a92a4`.

## 2. The scope, MEASURED — and a corrected count

An earlier statement of this decision said the file carried **five** unpublished data-derived
reconstruction statistics. **That count was wrong and is withdrawn.** It was not counted; it was
asserted. The measured scope:

- **`50` lines carry `[M60]` payload measurements** — `grep -c '\[M60\]'`, the tag the file itself
  defines at `:25` as *"Read-only PyROOT payload measurements by peer session `minerva-omnifold-60`"*.
- **`10` of those `50` lines** also match `data|1A|1B|/[0-9]{3,}|median`, the filter used here and
  stated so the number is reproducible. These are the data-derived ones.
- Many carry **real event counts from named playlists** and **data/MC timing medians**, not summaries.
  Examples, verbatim by line: `:81` *"848 of 8854 (9.58% pooled) ... (252/2533 1A data, 293/3226 1A MC,
  303/3095 1B data)"*; `:141` *"median -0.703 ns (data), -0.216 ns (MC)"*; `:211` *"12561/15259 data and
  16542/20000 MC entries"*; `:304` *"225/30518 slots (0.74%) data and 306/40000"*; `:445` *"83.08% of 1A
  MC rows"*; `:74` *"exactly 0.0 on 15771/15771 present photons"*.

**No count in this record is stated that was not counted.** The complete enumeration is in §5.

## 3. The decision

**Joseph authorizes publication of this file on `main`, taken on the corrected scope above and NOT on
the withdrawn five-statement version.** He was shown the measured scope — `50` payload-measurement
lines, `10` of them data-derived with real event counts and data/MC medians — and decided after
being shown it. Recorded so the audit trail shows a decision rather than an oversight.

Supporting context, not a justification for the decision: the repository is already public, the file
was already public on a pushed lane branch, and origin takes 700+ clones a day from ~240 unique
sources with zero forks, so the content should be assumed already copied.

## 4. What this decision does NOT do

It does not adjudicate any PET result. `AGENTS.md` records that **PET is diagnostic and
method-development, not a publication uncertainty product** (Joseph, 2026-08-20), and this file's own
header repeats it. It does not make any `[M60]` measurement quotable: the file states at `:25` that the
authoring lane **reproduced none of them independently**. Publication is not verification.

## 5. Enumeration — every `[M60]` line, generated not transcribed

```
25:| `[M60]` | **Read-only PyROOT payload measurements by peer session `minerva-omnifold-60`, 2026-09-01.** That lane had pscratch payload access; **this lane did not, and has independently reproduced
29:and the *arithmetic* of several `[M60]` results — the recipe deviation modes, the ordering-rate
67:| `direction` (3) | `gamma{1,2}_direction[3]` | unitless; **unit-normalized, \|d\|=1 to 1e-15, exactly p-hat** `[M60]` | "3D vector of the gamma1 direction based on the energy barycenter composing 
69:| `energy_ecal` | `gamma{i}_energy_ecal` | MeV `[DOC]` | as above; `energy_ecal / evis_ecal = 3.2367`, one distinct value `[M60]` | R-L |
70:| `energy_scal_x` | `gamma{i}_energy_scal_X` | MeV `[DOC]` | as above; ratio to `evis_scal_X` = 5.1474, one distinct value `[M60]` | R-L |
71:| `energy_scal_uv` | `gamma{i}_energy_scal_UV` | MeV `[DOC]` | as above; ratio to `evis_scal_UV` = 8.9688, one distinct value `[M60]` | R-L |
72:| `evis_tracker` | `gamma{i}_evis_trkr` | MeV `[DOC]` | "pre-calibration energy"; **the only evis field NOT recoverable from its energy partner** — `energy_trkr/evis_trkr` varies, mode 1.326 `[M60]
73:| `evis_ecal`, `evis_scal_x`, `evis_scal_uv` | `gamma{i}_evis_*` | MeV `[DOC]` | pre-calibration; **exactly collinear with their `energy_*` partners** `[M60]` | **M/D — collinear** |
74:| `energy_hcal`, `evis_hcal` | `gamma{i}_*_hcal` | MeV `[DOC]` | "(=0 by default)" `[DOC]`; **exactly 0.0 on 15771/15771 present photons, min=max=0.0, three files** `[M60]` | **M/D — structurally c
75:| `dedx` | `gamma{i}_dEdx` | **MeV per plane, 1 plane = 2.5 cm; dE not passive-corrected** `[DOC]` | "dE/dX measurement using the first 4 planes of the shower" `[DOC]`; `-999` on some present photo
76:| `time` | `gamma{i}_time` | **unit unknown — the official doc says so itself**; ns-scale range `[M60]` | "Average time of the blob with respect to the start of the slice (not sure about the unit)"
82:`[M60]`. See §6(g) for the supported mechanism. **Consequence: the slot index is not a reliable
85:**Energy independence.** Of the ten photon energy fields only **five are independent** `[M60]`: the
91:a collinear pair. **Collinearity is recorded to the precision `[M60]` reported; the rounding was not
107:| `position` (3) | `MasterAnaDev_Blob{X,Y,Z}` | length, **mm** `[INF]` — not stated `[DOC]` | "X, Y, Z ... position in plane of candidate" `[DOC]`. **70% of blobs have `is_3d == 0`, and among thos
108:| `time` | `MasterAnaDev_BlobT` | time; **226-15289 ns** `[M60]`; origin not stated `[DOC]` and **undemonstrated** `[M60]` | "Time ... of candidate" `[DOC]` | R-L |
109:| `time_position` | `MasterAnaDev_BlobTPos` | **length, bounded at exactly /-1054.5318 mm in every file** `[M60]` | **"Transverse position in plane of candidate"** `[DOC]` — a SPATIAL coordinate. 
140:| `position` (3) | `prong_part_pos[0:3]` | **(x, y, z) in mm** `[M60]` | order settled; components 0,1 signed at /-O(10^3) | R-L |
141:| `time` | `prong_part_pos[3]` | **ns** `[M60]` | **same clock as the reco vertex, DEMONSTRATED**: `pos[3] - vtx[3]` median -0.703 ns (data), -0.216 ns (MC) `[M60]` | R-L |
142:| `four_momentum[0:3]` | `prong_part_E[0:3]` | `(px, py, pz)` **MeV** `[M60]` | component 2 large and positive (beam axis) | R-L |
143:| `four_momentum[3]` | `prong_part_E[3]` | MeV | **E = sqrt(p^2  m_hyp^2), determined by (px,py,pz, pid)** `[M60]`. Also a four-way pid separator: 105.658 / 938.272 / 1.0 / 0.0 for pids 3 / 8 / 13
144:| `dedx` | `prong_dEdXMean` | **unresolved.** MeV/cm ruled out; MeV-per-plane plausible, unproven `[M60]` | mean dE/dx. `-999` in **75.5%** of 3853 prongs; valid median 5.69 / 5.74, p95 23-25, **m
146:| `mass` | `prong_part_mass` | declared energy | **deterministic in `pid`** (105.658 for pid 3, 938.272 for pid 8); `-1` in 26.9% `[M60]` | **M/D — redundant against `raw_pid`** |
147:| `charge` (cat -1,0,1) | `prong_part_charge` | raw code, `Int` | measured code set **{-999, 0, 1, 2}**; **`2` in 44.3%**; nonzero **only** for pid 3 ({2: 5144, 1: 324, 0: 10}); pids 8/13/0 give e
155:disagreeing in 2207/2207) `[M60]`, and exactly 0.0 for the null slots. Pooling those into one mean
160:`[M60]`; `13` carries the `-1` mass sentinel and is **not** resolvable by mass; `0` is an unset slot;
173:reaches 5, >1 in 35% of data and 52% of MC entries) by a rule the tuple does not record `[M60]`.
190:**No per-prong truth link exists in MAD.** Covering search `[M60]`: **153** prong-named branches in
209:- **Both sentinel codes are load-bearing and mean different things** `[M60]`: **`-9999` marks
214:- **Sentinel-in-a-physical-range is theoretical, not live** `[M60]`: exact `-999.0`/`-9999.0` occurred
255:**15771/15771** present photons across three files, worst deviation **identically 0 MeV** `[M60]`.
263:`-0.0150307`, matching in **0 of 668** and **0 of 710** `[M60]`.
273:p-hat and `gamma_P/gamma_E == 1` (massless-treated) `[M60]`, a properly calibrated photon
280:`Data=1 MC=1 Truth=0`, and `[M60]` confirms every branch of this family present with an identical
289:   `prong_dEdXMean`, unit **unresolved** `[M60]`. **Do not record them as demonstrably the same unit.**
299:convention) for blob and prong position and time, with `[M60]` confirming mm and ns for prongs.
303:`gamma{1,2}_E` takes **three** states, not two `[M60]`: `-9999` (absence), `> 1e-5` (present), and
309:181/306; and **all ten** energy fields exactly 0.0 with `gamma_P == 0` `[M60]`.
312:16542 == 16542) `[M60]`. Joint slot states (A absent, Z zero-energy, P present):
343:half the tokens on that field land in the bucket reserved for codes we cannot label `[M60]`.
352:happens on pre-calibration visible energy, before `gamma_E` is recomputed** `[M60]`:
376:against exactly 0.0 in slot 1 `[M60]`. These 84 events sit **outside** the 8854 both-present
380:so positive calibrated energy always implies positive visible energy `[M60]`.
384:has ECAL energy 3.17x more often than slot 2 (22.8% vs 7.2%) `[M60]`. Both are *predicted* by an
394:defective branch `[M60]`. The committed smoke never binds `_Old` (verified: `grep _Old` over
445:1A data rows and **83.08%** of 1A MC rows `[M60]`.
453:| Excluding canonical `gamma*_E` from features | **GO — lossless** | exact four-field sum identity, 15771/15771 `[M60]` |
492:| Branch presence / title parity across data and MC | **GO** | `[DOC]` `MC Only? = No` on all gamma and Blob rows; `[M60]` identical titles in all 24 files |
589:- **No payload was read by this lane.** Every `[M60]` row is single-source and unreproduced here.
593:  `FIXED_SAMPLE_TELEMETRY_NOT_AN_ESTIMATE`. `[M60]`'s later passes control playlist properly; the
```
