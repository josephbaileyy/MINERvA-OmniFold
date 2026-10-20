# MP1-A step S0: prepared, not submitted (2026-10-19)

**By** the measurement session, under [`BINDING-PHASE1-20261019.md`](../../BINDING-PHASE1-20261019.md) (MP1-A frozen,
D1 sizes) and [`PLAN.md`](../../PLAN.md) §2.3–2.4. **Tree:** worktree of `measurement-paper/phase1-20261019` at
`da43e98d`; nothing is committed. **Spend:** 0 node-h. Only login-node reads were made (≤ 20,000 tuple entries, file
metadata, hashes). Nothing was built or submitted.

**CITABLE FOR:** the S0 universe design and formulas; the q0-convention and G2 checks; the proposed z seed key; the
prepared files with their hashes; the submission commands; the charge estimate.
**NOT CITABLE FOR:** any J-cell number or result; G1 (not run); a frozen q0 convention. **The rule selects neither
candidate (§2), so that part is stopped.**
**Receipts** ([`receipts/`](receipts/)): `s0_q0_g2_1A_mc_first20000.txt` (the decisive check), `s0_unit_test.txt`,
`s0_cluster_hashes.txt`, `s0_g1_reference_candidates.txt`.

## 1. The universe (`measurement-paper/phase1/mp1/src/event/SpeciesResponseUniverse.h`)

`SpeciesResponseUniverse(chw, nsigma, species s, q0conv, fuzzconv)` subclasses `CVUniverse`. Its shift is
k = nsigma·δ_s, with D1's sizes hard-coded: proton 0.035, meson 0.05, EM 0.03, other 0.20, cross-talk 0.20. Muon
and neutrons are absent by construction.

- **E_avail' = NewEavail() + k·E_avail,s**, with E_s = `blob_recoil_E_tracker_<b>` + `blob_recoil_E_ecal_<b>` and
  b ∈ {p, meson, em, other, xtalk}.
  - `fuzz=absolute`: E_avail,s = 1.17·E_s. The subtracted muon fuzz is treated as not species s.
  - `fuzz=fractional`: E_avail,s = NewEavail()·E_s/(tracker + ECAL). The fuzz is treated as having the event's
    species mix, so the species parts sum to NewEavail() exactly.
- **q0' = q0 + k·q0,s**, with q0 = `MasterAnaDev_recoil_E`, pc_s = `part_response_recoil_allNonMuonClusters_<s>_id`
  + `_od`, and pc = the same sum over all ten species (proton, meson, em, other, low/mid/high_neutron, xtalk, muon,
  none). On 1A MC, pc = `MasterAnaDev_recoil_passivecorrected` exactly.
  - `q0=legacy`: q0,s = pc_s. This is MAT's absolute `_id_err` shift (`ResponseSystematics.cxx:370-416`), extended
    to ID+OD because pc contains OD.
  - `q0=fractional`: q0,s = q0·pc_s/pc. This is MAT's newer path (`:356-365`), here on ID+OD. MAT uses ID only,
    through `passive_<s>_id`, which equals the allNonMuon ID branch exactly (receipt §3–4).
- **Unchanged from CVUniverse.** RecoQ3() and RecoW() are its formulas verbatim, evaluated at q0'. Truth, weights and
  cuts are inherited, and no cut reads the recoil. Data use `dataCV`, so they are never shifted. Other details:
  `IsVerticalOnly() = false`, and negative tuple defaults count as 0, as in MAT. At **k = 0** every override returns
  CVUniverse's value, through an early return or identical arithmetic.
- **Patch** (`src/runEventLoopOmniFold-species-response.patch`, 106 lines). A fresh patch on canonical
  `runEventLoopOmniFold.cpp` (sha256 `57792e42…`, the file W2 patched), without W2's band. It requires
  `MNV101_SPECIES_RESPONSE_Q0` ∈ {legacy, fractional} and `_FUZZ` ∈ {absolute, fractional} (no default); builds
  `SpeciesResponse_<s>` = {0: −1σ, 1: +1σ} for the five species and `SpeciesResponse_zero` = {k = 0} in the reco and
  truth maps; refuses `MNV101_SKIP_SYST`, and in the binary (closing W2 review F5) `MNV101_DUMP_UNIVERSES` and
  `MNV101_DUMP_POINTCLOUD`. It applies cleanly to the canonical tree (verified locally).
- **One active universe per pass.** `ParseActiveUniverse` takes a single `BAND:IDX`, and `activeRecoUniverse` is one
  pointer (`runEventLoopOmniFold.cpp:1764-1846`). **A multi-endpoint pass is not possible** without a larger change;
  none is prepared.
- **Local unit test** (`test/`). It compiles the header against a mock CVUniverse that copies the production
  NewEavail, fuzz, RecoQ3 and RecoW, plus the parser cut from the patched source. Result: **ALL PASS**. k = 0 is bit
  for bit under all four convention pairs; all five species at ±1σ match the formulas; 7 parser cases pass.
  Negative control: a mutated header (k = 0 path ×(1+1e-15), legacy shift ×1.5) fails with 15 FAIL lines.

## 2. The q0 convention: **neither candidate reproduces `MasterAnaDev_recoil_E` from its parts — STOPPED, not picked**

**Sample.** 1A MC `MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root`, first 20,000 entries.
**Selection.** 4,561 selected-like events (4,551 true ν_μ CC) under the six reco pre-cuts
(`runEventLoopOmniFold.cpp:1710-1715`). The tuple's `MasterAnaDev_muon_theta` and `minos_trk_qp` stand in for MAT's
`GetThetamu()` and `GetMuonQP()`.

**What q0 is.** q0 = F(pc), a single-valued, nonlinear (polyline) function of the parts' sum (receipt §6–7):
- Of 2,852 neighbour pairs with pc within 0.1%, none differ in q0 by more than 1%.
- q0 = `recoil_E_polylinecorrected` on all 882 events where pc = `recoil_E_nopolyline` (= `blob_recoil_E`).
- F is exactly linear, q0 = 1.499556707·pc, for pc < ~509 MeV. That covers 43.85% of events.
- Above that, q0/pc runs from 1.4996 to 1.549. The local slope dF/dpc over the secant q0/pc is 1.000 below 509 MeV,
  then 1.015 and 1.054, then 0.978–0.993 up to 15 GeV.

**The rule** is "reproduces `MasterAnaDev_recoil_E` from its parts", tested as ratio 1 or a fixed multiple, to 1e-6:

| candidate | q0 / Σ parts, 4,561 events | reproduces? |
|---|---|---|
| legacy, Σ_s pc_s = pc (ID+OD) | 1.4996–1.5490, median 1.514; 0.0% at 1 | **no** (its parts sum to about q0/1.5) |
| legacy, ID only | median 1.558, p99 14.7 | **no** |
| fractional, q0 = c·pc for a fixed c | c = 1.4995567 on 43.85% of events only; 0.02% at the median | **no** (not a fixed multiple above ~500 MeV) |

**For the director's ruling.** The size of each shift, as (q0' − q0)/(δ_s·pc_s), against the response itself (dF/dpc):
legacy gives 1, under-shifting by a factor of about 1.5 everywhere; fractional gives q0/pc, exact for pc < 509 MeV and
between 5.2% below and 2.2% above the local slope at higher pc.

A third convention would reproduce q0 exactly: q0' = F(pc + k·pc_s). F is tabulated implicitly in the tuples, as
(`recoil_E_nopolyline`, `recoil_E_polylinecorrected`) pairs. It is not one of the binding's two candidates and is not
implemented. **Choosing among legacy, fractional and F-propagation is the director's ruling.** Both candidates are
built and switchable, and the ±1σ jobs take the convention as a required argument.

## 3. G2: identity PASS; cross-talk is a component, so **cross-talk IN** under D1; muon-fuzz clause UNRESOLVED

**Identity.** The nine pieces (p, meson, em, other, lown, midn, highn, xtalk, mu) sum to `blob_recoil_E_tracker` with
max |ratio − 1| = 1.8e-15 over 4,559 events, and to `_ecal` with 1.1e-15 over 4,109 events. No piece is negative.
The identity holds (≪ 1e-6).

**`_xtalk` and `_mu` are components of both sums.** Dropping `_xtalk` breaks the identity in 97.2% (tracker) and
84.4% (ECAL) of events; its mean share is 2.8% (tracker) and 29.0% (ECAL). Dropping `_mu` breaks it in 75.4% and
48.1%. Cross-talk is also one of pc's ten species.

So under D1's condition, **cross-talk is IN** (δ = 20%). *Flag:* MAT's own list marks xtalk `//DO NOT USE`
(`ResponseSystematics.cxx:34`); D1 does not mention this.

**The muon fuzz is not confined to `_mu`.** This is CVUniverse's `GetTrackerECALMuFuzz`, subtracted inside
NewEavail. On tracker / ECAL events that have fuzz: fuzz ≤ `_mu` in 16.0% / 37.5%; fuzz ≤ `_mu` + `_xtalk` in
28.7% / 55.3%; fuzz ≤ total in 100% / 99.96%. So the fuzz removes energy of other species, and the tuples do not split it by species. Species s's share of
NewEavail therefore cannot be identified exactly.

**Bound on the double count.** With `fuzz=absolute`, 1.17·E_s includes species-s energy that NewEavail has already
subtracted. A strict bound on that energy is Σ min(E_s, fuzz)/Σ E_s; the indicative bound uses (fuzz − `_mu`)₊:

| species | proton | meson | EM | other | xtalk |
|---|---:|---:|---:|---:|---:|
| strict bound | 0.32 | 0.27 | 0.28 | 0.45 | 0.40 |
| indicative bound | 0.27 | 0.23 | 0.25 | 0.41 | 0.34 |

`fuzz=fractional` avoids this by assuming the fuzz has the event's species mix. Its factor NewEavail/(1.17·raw) has
median 0.913 and p1 0.468.

**Not decided here:** whether G2's "no double count" clause is met, and which fuzz convention is frozen. A G2
failure ends MP-1 as "not propagated" (PLAN §2.3), so this needs the director's ruling.

**Also measured:** the tuples' `_id_err/_id` equal the D1 sizes exactly for all five species, ID and OD; and
low + mid + high_proton = proton exactly.

## 4. The z-draw seed key (S2; named before S2, as the binding requires)

**Existing keys.** Sources: `default_rng` in `nd-unfolding/s5p_*.py`, plus every hex tag passed to `default_rng`
anywhere in the repository's `.py` files (`git grep`: 0x4A01 ×2, 0x4A02 ×2, 0x5F5 ×1; nothing else).
- `0x4A01`: `s5p_joint.py:120` (the jitter stream) and `s5p_recompute.py:60/468` (`TAG_SURROGATE`).
- `0x4A02`: `s5p_joint.py:158` and `s5p_recompute.py:61/473` (`TAG_PREDICTION`, entropy `[seed0, pseudo_seed, 0x4A02]`).
- `0x5F5`: `s5p_nullexp.py:316`, the nuisance draw that includes the five existing `lateral_z`.
- Reached through `s5p_nullexp`, in `s5n_pseudo.py`: single-integer seeds `pseudo_seed` (`:131`), `b`,
  `b+10_000_000`, `b+20_000_000` (`:210-212`) and `permute_seed` (`:320`); the split salt `0xB6D5E1A7C3F29041`
  (`:59`).

**Proposed key: `0x4D31`** ("M1"). It is unused anywhere in the repository. The draw per frozen pseudo-experiment is
z_s = `np.random.default_rng([pseudo_seed, 0x4D31, i_s]).standard_normal()`, with i_s = 1 proton, 2 meson, 3 EM,
4 other, 5 cross-talk. The three-element entropy cannot coincide with any stream above; the fixed index leaves each
z_s unchanged whether cross-talk is in or out; the species are uncorrelated, as the spec requires.

## 5. Prepared files (worktree paths under `measurement-paper/phase1/mp1/`; sha256, lines)

```
55347c3463b75aa39307933222102ee113f111de96fa463a6aadfab6d8eb93ab 167 src/event/SpeciesResponseUniverse.h
79ea3acec1221d288bed51ecfad03f44a822dee46136d8a942d2eb0f400b1108 106 src/runEventLoopOmniFold-species-response.patch
74ef936e3a0ee23227536dd8458a030747cbddc955388413e054256036b8b72f  80 build_mp1_s0.sh
0ed3eb9c4af64edbb080fb361ff8905dfdb1988f0041b54f313a63ee8590e547  78 sbatch_mp1_s0_evloop.sh
6382fed4f0fee87eaea8d56e1071d33ebe535ee41a2406f22114ea5df6ddcd71 118 check_species_pass.py
73d8bbb097fec618924e8d48e986e4c2550cb4617c511a1b6ef378a2c58d5451 304 s0_inspect_q0_g2.py
67d0dc9a71321b61fc85dba0bc5e38fb12a137e78efcc256db0c37b01cbdbdfd  22 test/run_test.sh
58348a36b47e62cc026f1a24e1475000089133e6419b4d7a614004c6385343d1 127 test/test_species_universe.cpp
e28c91a51e2c4af04f922e13b2edcc300da89e9709e8521656809fd952f14db4 113 test/mock/event/CVUniverse.h
```

- **`build_mp1_s0.sh`** (login node, like W2's; **not run**) mirrors `build_w2.sh` and closes W2 review F9. It
  refuses a dirty clone or a namespace outside `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/`; checks the
  four tracked inputs against the commit and pins the untracked `cuts/MaxPzMu.h` (`c50f6b5a…`) and
  `systematics/Systematics.h` (`1bdfa4f0…`); checks rsync; fails unless base equals canonical and mod differs only by
  the header and the patch; and writes `MANIFEST.sha256` (every source file, the MAT libraries, both binaries).
- **`sbatch_mp1_s0_evloop.sh`** runs one variant per job on full 1A (`base_cv`, `zero`, `<s>_m1|_p1`), with the
  binary's md5 and both conventions as required arguments. It pins the 1A manifests (Data `b74d8965…`, 253 files; MC
  `4100dca4…`, 41), keeps W2's unset list, refuses the dump variables, and never overwrites. QOS shared, `-A m3246
  -C cpu`, 2 CPUs, 16 GB, `-t 01:55:00`, `--no-requeue`. Guards exercised locally (`SPECIES_ENV_CHECK_ONLY=1`): 10
  cases, all as expected.
- **`check_species_pass.py`** (login node, ROOT env, the W2 comparer's reader) checks that every unshifted branch and
  the data tree are identical, the sign of the shift, |ΔE| ≤ δ·E (fractional fuzz) and |Δq0| ≤ δ·q0 (fractional q0),
  and reports the fraction of rows moved. On synthetic input the good case passes; wrong sign, over-bound and a
  shifted data tree each fail.

## 6. The cluster: checkouts and the G1 reference (`receipts/s0_cluster_hashes.txt`, `s0_g1_reference_candidates.txt`)

**Canonical checkout** `/pscratch/sd/j/josephrb/MINERvA-OmniFold` (HEAD `32e403b8`, only docs dirty): the git blobs
of `runEventLoopOmniFold.cpp`, `CVUniverse.h`, `MaxPtMu.h`, `CMakeLists.txt` (`b7e1edbc`, `04906da5`, `91e7fce4`,
`4401b2d9`) **equal** the worktree's. MAT libraries (`opt/lib/*.so`) are dated 2026-05-14, before W2's build. It has
no `publication/w2/compare_omnifiles.py`; use the clone's (blob `3a8eeb0e`, as in the W2 namespace repo).

**W2's build** (login04, `/pscratch/sd/j/josephrb/w2-recoil-20261006/build/`, repo `049eff95`): base md5
`74c0717f…`, mod md5 `f3e9c97b…`; `src_mod` holds W2's patched loop (blob `1ad3b7f9`) and header (`62d254c6`, equal
to the worktree's).

**G1's "production 1A CV" cannot be met literally.** The W2 review names
`nd-unfolding/runEventLoopOmniFold_5D_1A_universes_full_bkgaware.root` (2026-07-13) as the production file. It has
2,679,264 `mc_signal_reco` entries (470 branches) and 39,870 `mc_background`; the current binary's lateral path
(W2's `mod_rr0`, W2b's `rrzero`) gives 2,489,136 (16 branches) and 52,626. So `compare_omnifiles.py equal` against it
FAILs whatever the universe does. This conflicts with the review's "entry counts are equal in all four trees"
(`docs/publication/w2/REVIEW-20261006-w2a-independent.md:16-19`), at least for the files as they are today.

**Proposed G1:** primary `equal base_cv.root zero.root` (W2a's no-op design, on full 1A, same source); secondary
`equal` against W2b's `rrzero_1A` (same source and libraries). **The choice of reference is the director's.**

## 7. Submission (for the reviewer; nothing has been run)

```bash
# 0. commit measurement-paper/phase1/mp1/ + this directory (explicit paths), push; then on a login node:
NS=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0
git clone --branch measurement-paper/phase1-20261019 <origin> $NS/repo        # clean clone of the reviewed commit
bash $NS/repo/measurement-paper/phase1/mp1/build_mp1_s0.sh $NS/repo $NS       # login-node compile, as W2 (unbilled)
B=$NS/build/bld_base/runEventLoopOmniFold; M=$NS/build/bld_mod/runEventLoopOmniFold
MB=$(md5sum $B | cut -d' ' -f1); MM=$(md5sum $M | cut -d' ' -f1); mkdir -p $NS/logs
S=$NS/repo/measurement-paper/phase1/mp1/sbatch_mp1_s0_evloop.sh
# 1. now (independent of the open rulings; at k = 0 the conventions do not enter, but both must be named):
sbatch --job-name=mp1s0_base_cv --output=$NS/logs/%x_%j.out $S $NS base_cv $B $MB - -
sbatch --job-name=mp1s0_zero    --output=$NS/logs/%x_%j.out $S $NS zero    $M $MM fractional absolute
# 2. only after the director's q0 (§2) and fuzz (§3) rulings, Q0 in {legacy,fractional}, FZ in {absolute,fractional}:
sbatch --job-name=mp1s0_proton_p1 --output=$NS/logs/%x_%j.out $S $NS proton_p1 $M $MM $Q0 $FZ
sbatch --job-name=mp1s0_meson_p1  --output=$NS/logs/%x_%j.out $S $NS meson_p1  $M $MM $Q0 $FZ
# 3. checks, login node, ROOT env (source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh):
python $NS/repo/publication/w2/compare_omnifiles.py --out $NS/g1_base_vs_zero.json equal $NS/evloop/base_cv.root $NS/evloop/zero.root
python $NS/repo/publication/w2/compare_omnifiles.py --out $NS/g1_zero_vs_w2b_rrzero.json equal \
       /pscratch/sd/j/josephrb/w2-recoil-20261006/w2b/evloop/rrzero/runEventLoopOmniFold_5D_1A_w2b_rrzero.root $NS/evloop/zero.root
python $NS/repo/measurement-paper/phase1/mp1/check_species_pass.py $NS/evloop/zero.root $NS/evloop/proton_p1.root \
       --species proton --sign 1 --q0 $Q0 --fuzz $FZ --out $NS/check_proton_p1.json   # likewise meson
# 4. every job id with its sacct charge into phase1/LEDGER.tsv (BINDING §3).
```

**Optional, the director's call.** S0 computes no J-cell number, so it could run the ±1σ passes under both q0
conventions to show their difference on the omnifiles (+2 jobs). The binding fixes the convention "at S0 … before
any J-cell number", which seems to allow this. It is not assumed.

## 8. Charge estimate (`publication/w2/LEDGER-w2.tsv`; billed node-h = ElapsedRaw × billing/256/3600, billing 10 on shared)

**Measured 1A passes**, with the same loop and input and no point clouds:

| job | 59408361 | 59408363 | 59421456 | 59421476 | 59421491 |
|---|---:|---:|---:|---:|---:|
| elapsed (s) | 3,849 | 4,842 | 4,392 | 4,223 | 2,247 |

That gives **0.0244–0.0525 node-h per pass** (mean 0.0424). The species band adds about 22 `GetDouble` reads per
reco event; this is assumed negligible, not measured.

| jobs | central | upper (4,842 s) | worst case at the 1 h 55 min limit |
|---|---:|---:|---:|
| `base_cv` + `zero` (submittable now) | 0.085 | 0.105 | 0.150 |
| `proton_p1` + `meson_p1` (after the rulings) | 0.085 | 0.105 | 0.150 |
| **S0 total, 4 jobs** | **0.170** | **0.210** | **0.300** |
| optional: both conventions (+2 jobs) | +0.085 | +0.105 | +0.150 |

This matches PLAN §2.4 ("0.2 on shared"), is far inside the 35 node-h grant, and no job can exceed 0.075 node-h at
its limit. Storage: about 0.4 GB per output, about 1.6 GB on pscratch.

## 9. UNCONFIRMED, and decisions this session could not make

1. **The q0 convention (director).** The rule, as written, selects neither candidate (§2). Nothing was picked.
2. **The G2 muon-fuzz clause and the fuzz convention (director).** The fuzz contains non-muon species energy (§3).
   This is either a G2 failure, which ends MP-1 as "not propagated", or a declared approximation under one of the
   two conventions.
3. **Cross-talk IN** follows from D1's condition. MAT marks xtalk "DO NOT USE" (`ResponseSystematics.cxx:34`).
4. **The G1 reference (director).** The named production file cannot match the current binary's entry counts (§6).
   Proposed instead: a fresh `base_cv`.
5. **Not yet compiled against MAT/ROOT.** The code was compiled only against the mock (clang 15,
   `-std=c++14 -Werror`). Two things are therefore unverified: the lookup of `MinervaUniverse::GetTreeName` through
   PlotUtils, and ChainWrapper reads of the extra branches.
6. **The band also sits on the truth chain**, as in W2. That tree lacks the reco branches, so this is safe only if
   the truth loop never calls `NewEavail`, `RecoQ3` or `RecoW`. W2's identical pattern ran 36 jobs cleanly.
7. **The S0 read is narrow** (selected-like, one 1A file, first 20,000 entries); F's single-valuedness and 1.4995567
   are shown there only. 8. **G1 checks plumbing, not the species reads** (k = 0 short-circuits them); the ±1σ passes
   and the mock test exercise them. 9. **Charge per pass** is assumed equal to W2's 1A passes. 10. **`0x4D31`** is
   proposed, not yet frozen in a committed record.
