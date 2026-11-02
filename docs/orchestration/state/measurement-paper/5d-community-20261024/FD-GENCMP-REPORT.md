# REPORT GENCMP: Q08, Q10 and Q26 of the sixteen-cell paper (2026-11-01)

**By** the limitation-resolver lane (Claude).

**Under** [`FD-GENCMP-BINDING.md`](FD-GENCMP-BINDING.md) (#647, main `5f335ac5`), which binds
[`FD-GENCMP-DECLARATION.md`](FD-GENCMP-DECLARATION.md) at M = `3410ed0c`.

**MEASURES:** steps 0, A, B, C and D as declared. Each step's readout is in `fd/gencmp/readout/`, and its receipts and
logs are in `fd/gencmp/receipts/` and `fd/gencmp/logs/` (all 17 files of the run's `logs/`, also in the HPSS archive;
`logs/htar.log` is the first archive attempt's log, and `receipts/htar.log` the final one's).

**CANNOT AUTHORIZE:** any paper edit, any Table IV change, any claim (binding ruling 4). §5 proposes the §7 wording and
nothing beyond it.

**CITABLE FOR:** the numbers below, each with its matrix and cells, as the committed readouts hold them.

**NOT CITABLE FOR:**
- a validation of the reported covariance or of Q;
- any generator exclusion;
- the 3D comparison as a validation in either direction (ruling 3);
- the GiBUU CH numbers without their hydrogen label.

## 0. Outcome in brief

| step | limitation | controls | §7 outcome read | charge (node-h) |
|---|---|---|---|---:|
| A | Q08 | A0, A1, A (CH bitwise), A2, R: all PASS | "A0 and A1 pass": NuWro's χ² falls and GiBUU's total χ² rises | 0 (local) |
| B | Q10 | B0 (6 samples + 2 CH combinations), B2 (exact M4-W population): all PASS; B1 printed | "B0 passes" for all four generators; seed spread below the 0.2 σ flag | 0.0675 |
| C | Q26 | R, C0, C1 (2D, 3D), C3 (2D, 3D), structural: all PASS | 2D: every quadrant "agree below a correlation", ρ* 0.9892 (QC) to 0.9999. 3D: "agree at the σ₁₆ scale (descriptive)" | 0 (login node) |
| D | Q08 | native sample complete; rule on the primary route | "agree" on both routes | 0.0905 |

- **Total charge:** 0.158 node-h against the 6.0 cap.
- **Deviations** (§4): four pscratch inputs were read with plain opens by step D's job scripts, and the HPSS archive was
  written three times.

## 1. Execution

**The deploy.** `$B = /pscratch/sd/j/josephrb/gencmp-20261101/` was absent before. A fresh clone was made at M, with
porcelain 0. The five blobs equal the binding's (`receipts/deploy-blobs.txt`). In the deploy, the bound suites pass:
47/47 under root_6_28 and 52/52 under omnifold_py310 (`logs/tests-*.log`). Porcelain was still empty after every job.

| step | where | job | QOS | start–end (PST) | ElapsedRaw | billing | node-h |
|---|---|---|---|---|---:|---|---:|
| A1 | login node, omnifold_py310 | — | — | — | — | — | 0 |
| A | local (numpy 1.26.4), from main `5f335ac5` (code blobs equal M's) | — | — | — | — | — | 0 |
| C | login node, omnifold_py310 | — | — | — | — | — | 0 |
| B | 1 node | 60658825 | regular | 12:33:13–12:37:16 | 243 s | 256 | 0.0675 |
| D probe | 1 node | 60658883 | regular | 12:33:23–12:34:29 | 66 s | 256 | 0.0183 |
| D generation | 1 node | 60659923 | regular | 12:44:26–12:45:56 | 90 s | 256 | 0.0250 |
| D rebuild | 1 node | 60659924 | regular | 12:54:44–12:57:34 | 170 s | 256 | 0.0472 |

Node-h = ElapsedRaw × billing / 256 / 3600 (`receipts/sacct.txt`). Everything was CPU only, on regular QOS, and nothing
was written to CFS.

## 2. Readouts

### 2.1 Step A (Q08): NuWro and GiBUU corrected to CH, generator definitions (`readout/ch.json`)

- **A0.** The carbon arrays reproduce Table IV's committed χ² to 1e-9, in both matrices, total and shape-only.
- **A1.** The committed C12 arrays equal the frozen products bitwise (`readout/a1.json`; login node, atime unchanged).
- **A.** The CH arrays equal the committed `xsec_CH` and `sumw2_CH` bitwise.

| prediction (cells) | carbon: χ² / shape-only | CH: χ² / shape-only | Δ (CH − carbon) | without C_PL,5D: carbon → CH (total; shape-only) |
|---|---|---|---|---|
| NuWro (16; ndf 16, 15) | 130.68 / 113.73 | **128.41 / 108.40** | −2.27 / −5.33 | 188.03 → 181.21; 188.00 → 181.13 |
| GiBUU (8; ndf 8, 7) | 45.25 / 24.75 | **47.55 / 22.01** | **+2.29** / −2.74 | 58.46 → 61.22; 27.69 → 24.49 |

- **The CH/C ratio per cell** (min / median / max): NuWro 0.955 / 0.973 / 0.998; GiBUU 0.948 / 0.975 / 1.008.
- **GiBUU's total χ² rises** with the correction, in both matrices. Its shape-only χ² falls.
- **Sensitivity rows** (printed beside the primary, never in its place):
  - GENIE-CV hydrogen: NuWro 120.47 / 101.20, GiBUU 44.19 / 21.95. GENIE's hydrogen sample is thin, so this spread is
    largely that sample's noise (declaration §2).
  - GiBUU alt weight: 47.55 / 22.01.
- **Labels:** the GiBUU CH rows carry MP3-C's label (B3 failed on hydrogen; post-hoc bias check passed at ≤ 0.1 σ_c;
  46% of the hydrogen sample is DIS that does not conserve energy).

### 2.2 Step B (Q10): the analysis definitions (`readout/defs.json`; rebuild `readout/rebuild_b.json`)

**Controls.**
- **B0.** All six samples (genie_cv, genie_mec, nuwro_C12, nuwro_H, gibuu_C12, gibuu_H) reproduce their frozen products
  bitwise with n = ẑ and the generator W. The NuWro and GiBUU CH combinations equal step A's bitwise.
- **B2.** GENIE CV has 29 of 938,141 in-phase-space events with W² < 0, exactly M4-W's. NuWro C12 has 37 of
  1,261,997, also exactly M4-W's.
- **Status.** Every sample is "complete" (all 8 or 9 variants written).
- **B1 (printed).** The pools' α, w_truth-weighted: median 1.030 mrad, 68% interval [0.504, 1.920], beside MP-5's 1.03
  [0.50, 1.92].
- **The code tree** was copied through O_NOATIME and gated on family H. No atime moved.

| prediction | cells | generator definitions: χ² / shape-only | analysis definitions: χ² / shape-only | max \|Δ/σ\| per cell (cell) | Δ per cell, % | five-seed SD / σ, max |
|---|---|---|---|---|---|---|
| GENIE CV | 16 | 105.42 / 100.57 | 107.18 / 102.11 | 0.062 (R05) | −0.44 to +0.59 | 0.036 |
| GENIE + MEC | 16 | 223.55 / 223.46 | 229.09 / 229.00 | 0.063 (R07) | −0.54 to +0.32 | 0.042 |
| NuWro, carbon | 16 | 130.68 / 113.73 | 129.98 / 112.93 | 0.036 (R07) | −0.28 to +0.30 | 0.028 |
| NuWro, CH | 16 | 128.41 / 108.40 | 127.69 / 107.52 | 0.038 (R07) | −0.31 to +0.34 | 0.026 |
| GiBUU, carbon | 8 | 45.25 / 24.75 | 45.49 / 24.94 | 0.037 (R11) | −0.31 to +0.60 | 0.056 |
| GiBUU, CH | 8 | 47.55 / 22.01 | 47.78 / 22.19 | 0.036 (R11) | −0.36 to +0.62 | 0.052 |

- **χ², all reported matrix.** Without C_PL,5D, the analysis-definition totals are 111.22 (GENIE CV), 277.94
  (GENIE + MEC), 180.62 (NuWro CH) and 61.41 (GiBUU CH).
- **The W-only and axis-only parts** are each ≤ 0.077 σ per cell. GiBUU's M_n variant is ≤ 0.019 σ (printed only).
- **The seed-spread flag** (0.2 σ) is not raised for any prediction.
- **The candidate corner for Table IV**, "CH, analysis definitions":
  - GENIE CV 107.18 / 102.11;
  - GENIE + MEC 229.09 / 229.00;
  - NuWro 127.69 / 107.52;
  - GiBUU (8 cells) 47.78 / 22.19;
  - MnvTune v1 unchanged (already in the analysis definitions, MP-5 T3).

### 2.3 Step C (Q26): the sixteen cells per quadrant against 2D and 3D (`readout/overlap.json`)

**Controls.**
- **C0.** P5 gives f to 1e-12.
- **C1.** The quadrant edges are bin edges of both grids.
- **C3.** The 2D integral is 3.07302e-38 (VL173: 3.0730e-38), and the 3D integral is 3.07886e-38 (headline 3.079e-38).
- **Structural checks.** Q's area and units pass. Quadrant cells and unreported boxes are as declared. The PROJ3D index
  is valid. No E_avail region exists.
- **Diagnostics.** The largest |CV/`cells_x_EU` − 1| is 0. The unreported boxes hold 9e-46 cm² in P5 (box 6), and a
  share of 1.1e-7 of QA in MnvTune v1, so QA and QB are effectively complete. No atime moved.

| quadrant | S₁₆ (σ₁₆) | 2D S (σ₂D) | d, % | outcome (reported matrix) | ρ* | z at ρ = 0 | 3D: d, % | d/σ₁₆ (3D, descriptive) |
|---|---|---|---|---|---:|---:|---:|---:|
| QA (pT < 0.7, p∥ 1.5–4.5) | 7.991e-39 (6.84%) | 8.014e-39 (5.37e-40) | −0.28 | agree below a correlation | 0.9999 | −0.03 | −0.17 | −0.03 |
| QB (pT < 0.7, p∥ 4.5–60) | 6.775e-39 (4.84%) | 6.788e-39 (3.29e-40) | −0.19 | agree below a correlation | 0.9998 | −0.03 | −0.82 | −0.17 |
| QC (pT 0.7–4.5, p∥ 1.5–4.5) | 6.691e-39 (5.33%) | 6.796e-39 (3.48e-40) | −1.54 | agree below a correlation | 0.9892 | −0.21 | −0.76 | −0.14 |
| QD (pT 0.7–4.5, p∥ 4.5–60) | 9.193e-39 (5.48%) | 9.133e-39 (5.13e-40) | +0.65 | agree below a correlation | 0.9985 | +0.08 | −0.20 | −0.04 |

- **Why the outcome reads "agree below a correlation".** σ₁₆ and σ₂D are close in every quadrant, so the
  any-correlation band 2|σ₁₆ − σ₂D| is narrow: 3.6e-42 to 1.9e-41, against S near 7–9e-39. Each |d| lies just outside
  it, and far inside the ρ = 0 band. ρ* is the correlation above which a difference this size would exceed 2σ. The
  declaration's limit on step C's power (§10) applies here.
- **The variant without C_PL,5D** is printed only: QB and QD read "agree" there, QA and QC "agree below a correlation".
- **The 3D descriptive row (PROJ3D)** gives σ of 1.4–4.2e-40. It carries no outcome.

### 2.4 Step D (Q08): native NuWro on CH (`readout/native.json`; rebuild `readout/rebuild_d.json`)

**The run.**
- **Seeds** were declared before any generation (`receipts/d_SEEDS.txt`, `51d20126…`). The card is the production C12
  card with only the target keys changed (`receipts/d_card.sh`): carbon as production (E_b 34, kF 220,
  nucleus_target 2), hydrogen as MP3-B (free, nucleus_target 0). NuWro's `.par` echoes both lines.
- **The probe:** 64/64 chunks, rc 0, about 30 s per 2,000 events.
- **The production run:** 128/128 MAIN chunks (15,625 events each) and 10/10 SUPP chunks (10,000 each), so 2,100,000
  events, with no aborts and no alternate seeds used. Each flat file holds its declared count.
- **Pins and rebuild.** The native files are pinned in `receipts/native_pins.sha256` (138 lines). The rebuild reran
  nuwro_C12 and nuwro_H beside nuwro_CHnative in one directory. All three are complete, and B0 and B2 pass again for
  C12 and H.

| route | Σ z² (16 cells) | max \|z\| | rule: Σz² < 32.0 and \|z\| ≤ 3.5 | native χ² / shape-only | combination χ² / shape-only |
|---|---:|---:|---|---|---|
| generator definitions (primary) | 17.87 | 2.24 | **agree** | 134.02 / 111.98 | 128.41 / 108.40 |
| analysis definitions | 16.92 | 2.23 | agree | 134.71 / 112.01 | 127.69 / 107.52 |

- **The native route** gives a NuWro χ² 5.6 higher than the combination, within the declared per-cell tolerance.
- **The paper uses step A's combination** in every outcome (ruling 2).
- **A diagnostic** (`receipts/d_projection.txt`, not a declared test): probe chunk c1's NuWro test-event total is
  3.654e-38 per nucleon, against (12 σ_C + σ_H)/13 = 3.578e-38 from the production and MP3-B runs. That is +2.1%,
  mostly DIS.

## 3. HPSS

- **Quota first:** `hpssquota` read 446.01 of 512.00 GiB.
- **The archive:** `htar -Hcrc -Hverify=1` from an explicit file list (`receipts/htar_files.txt`, 3,510 entries) to
  `/home/j/josephrb/mnv-gencmp-20261101/gencmp-20261101.tar`. It is 3,236,046,848 B plus its index, and htar exited 0.
- **Retrieval test:** `d_SEEDS.txt`, `defs.json`, `native.json`, `overlap.json` and `native_pins.sha256` were
  extracted, and each equals its original by sha256.
- **What it holds:** the step products, receipts, logs, the native flat files and the raw `nuwro.root` files. The
  deploy clone is excluded (git holds it), as are the per-chunk `nuwro_home_dbg` link trees to cvmfs.
- **After:** `hpssquota` still showed 446.01 GiB, unrefreshed after the write.

## 4. Deviations, reported unprompted

1. **Plain reads of four pscratch inputs by step D's job scripts.**
   - The probe and generation scripts ran `sha256sum` on their inputs, NuWro opened its flux files, and ROOT and the
     shell read the macro and setup with ordinary opens.
   - Affected: `3d-unfolding/genie/setup_nuwro.sh`, `s5p-20260926/gen5d/code/nuwro_to_flat_5d.C`,
     `3d-unfolding/genie/flux_mefhc_numu_nuwro.root` and `s5p-20260926/gen5d_fluxfix/supp/flux_phi_t_50_100.root`.
     Their atimes now read 2026-11-01 12:44–12:45 PST.
   - Not restored (ruling 5). The rebuild driver's own reads were all O_NOATIME, and no atime deviation is recorded in
     either `rebuild.json`.
2. **The HPSS archive was written three times; each write replaced only this campaign's own tar.**
   - The first had its log inside an archived directory (exit 70).
   - The second stored 202 `nuwro_home_dbg/data` symlinks whose cvmfs targets are too long (exit 70, "HTAR SUCCESSFUL").
   - The third used an explicit file list without those link trees and exited 0.
   - htar reads this campaign's own outputs with plain opens.
3. **Step A ran locally on macOS,** where O_NOATIME does not exist. The `atime_deviations` in `ch.json` are of local
   repository files, not pscratch.
   <!-- absence-ok: a statement about the macOS operating system's open flags, not about a result -->
4. **Step D's job scripts were written after the binding.** As the declaration's §6 states, they enforce the probe and
   cap; they are not bound code. The probe projection was recorded before the production submission.

## 5. The §7 reading and the proposed wording (for Joseph; ruling 4)

- **Q08, "A0 and A1 pass, whatever the sign of Δχ²".**
  - Proposed for `paper_body.tex:42` and `:232`: "NuWro and GiBUU, generated on carbon, are corrected to CH by adding
    each generator's free-proton prediction with weight 1/13 per nucleon."
  - Table IV shows the CH rows. The carbon rows and the GENIE-hydrogen sensitivity go to the note. A table note carries
    GiBUU's hydrogen label.
  - Because GiBUU's total χ² rises, the text says so with its size: "for GiBUU the correction raises the total χ² from
    45 to 48 for 8 degrees of freedom and lowers the shape-only χ² from 25 to 22."
- **Q08, "step D agrees" (primary route; the analysis route also agrees).** One clause: "a native CH generation of
  NuWro agrees with the combination".
- **Q10, "B0 passes" for all four generators.**
  - The sentence at `:42` ("Unlike the analysis definitions, the predictions compute W with the neutron mass … and
    measure pT about their own neutrino axis") is removed.
  - Proposed in its place: "The predictions use the analysis definitions of W and of the muon angle, with the neutrino
    direction drawn from the analysis simulation; this changes no cell by more than 0.07 of its uncertainty."
  - Table IV uses the rebuilt values (§2.2's candidate corner).
- **Q26, every quadrant "agree below a correlation".**
  - Proposed for `:119`: "Summed over each of the four (pT, p∥) quadrants, the sixteen-cell result agrees with the
    two-dimensional result to between −1.5 and +0.7 per cent; the two agree within their uncertainties unless their
    correlation exceeds 0.989 (quadrant QC) or 0.998 (the other three)."
  - With the 3D clause: "and with the three-observable central value to between −0.8 and −0.2 per cent at the scale of
    the sixteen-cell uncertainty; no 3D covariance is adopted."

**Every number above changes a Table IV entry or a claim, so it goes to Joseph before any edit (ruling 4).** Nothing is
submitted, deposited or tagged.
