# MP3-B: NuWro on CH, reported beside A7

**By** the measurement session, 2026-10-20, under MP3-B (PLAN.md §4.3, frozen by BINDING-PHASE1-20261019 §2 and D6).
It also follows the director's rulings after the first attempt's abort ([`ATTEMPT1-STOP.md`](ATTEMPT1-STOP.md)):
- (A), chunked generation;
- (C), a mixed variant;
- the kaskada_on check.

Patching NuWro (B) was not approved and was not done. The agent's file write was refused, so this file was written by
the coordinating session from the agent's report text and checked against the fetched outputs under `runA/`.

**CITABLE FOR:**
- NuWro 21.09's own carbon-to-CH target effect per reported J cell;
- the descriptive T replay beside A7;
- the kaskada_on finding;
- the abort accounting.

**NOT CITABLE FOR:** a re-grade of A7 (D6: beside A7, never in place of it), or any claim; claims are Joseph's.
Variant (C) is labelled **"mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH"**.

**Headline (descriptive).** Under the frozen metric W, the primary NuWro-on-CH prediction keeps both NuWro tests
"rejected", but NuWro total survives only because Holm re-sorts it to the last position. At its frozen position it
would be 1.11 null SD below its boundary, i.e. "undetermined". The report-only κ = 3 family gives NuWro total "not
rejected". The mixed variant (C) gives both NuWro tests "undetermined". Under the CH prediction's own variance W_CH
nothing changes. This was reported to the director at once, as a claim question for Joseph.

## 1. Construction

- **Combination per fine cell.**
  - x_CH = (12/13)·x_C12 + (1/13)·x_H, and sumw2_CH = (12/13)²·sumw2_C12 + (1/13)²·sumw2_H.
  - x_C12 is the frozen `nuwro_cv_xsec5d_full.npz` (sha256 `475a2871…`).
  - x_H is NuWro's per-proton product through the frozen chain: `nuwro_to_flat_5d.C` (`01e89fb2…`), then
    `extract_nuwro` over the chunk files (N_total summed, exactly as p1..p8 are combined), then the flux-fix weight
    Σ w r / N_total on 0.5–50 GeV, plus the 50–100 GeV supplement (constant r = 4.8375e-4).
- **Statistics.** These come from the frozen `s5p_joint` and `s5p_inference` copies (byte-identical to `4f5a613f`,
  import-asserted), with metric V `35979ef7…`.
- **σ_c readings.** (a) is the SD of the J-cell result over NuWro's frozen B = 1751 null; it is the primary, as accepted
  for MP3-A. (b) is √diag W. (c) is the SD of the simulated residual.

## 2. Generation (A)

**Seeds.** `SEEDS-chunked.txt` (sha256 `0a6ebc5f…`) was declared before submission. An earlier version (`6d1e85bb…`) was
superseded before any use, when the kaskada cards were added.
- H_main is 25 × 10k events, seeds 63101–63125, with alternates 63201–25 and 63301–25.
- H_supp is 5 × 5k events, seeds 64101–64105, with alternates 64201–05 and 64301–05.
- Card k1 is the H card; k0 is the same card plus `kaskada_on = 0`.

| sample | chunks done / declared | dropped | aborts (rerun on alt-1) | events | DIS fraction per chunk | DIS done + DIS before aborts | excluded fraction (aborts per DIS event) |
|---|---|---|---|---:|---|---|---:|
| H_main | 25 / 25 | none | 3: c04 (63104, at 48.8% of DIS), c05 (63105, 91.3%), c12 (63112, 55.6%) | 250,000 | 0.609–0.632 | 154,622 + 12,049 | **1.8e-5** |
| H_supp | 5 / 5 | none | 1: c03 (64103, at 43.6%) | 25,000 | 0.958–0.962 | 24,005 + 2,095 | **3.8e-5** |

- **The excluded fraction is an approximation**: each abort removes one DIS configuration. Including attempt 1's two
  aborts gives ≈ 1.9e-5 (main) and ≈ 6.2e-5 (supp). These rest on 4–6 events. For the supplement, the Poisson 95% upper
  bound for one abort in 26k DIS events is ≈ 1.8e-4. **That is above the director's 1e-4 bar, so the supplement is
  FLAGGED, not assumed negligible.**
- **Every abort has the same signature**: `particle.h:227 E>=_mass`, with NuWro printing `E=1.19e+03 mass=1.19e+03`
  or `E=1.18e+03 mass=1.19e+03` (a Σ), in dyn 4. An aborted attempt is deleted whole (`.root` and `.part`); its logs
  stay.

## 3. Gates (k1, primary; k0 identical except C0's extra key)

| gate | result |
|---|---|
| C0 | **PASS.** 34 `.par` cards per card set, aborted attempts included. The differing keys are exactly {random_seed, number_of_events, nucleus_p, nucleus_n, nucleus_target}, plus `kaskada_on` for k0 only |
| C1 | **PASS.** The frozen macro reproduces the frozen C12 p1 and supplement flat trees: 12 branches bitwise, nTotal equal |
| B1 | **PASS.** CC dyn counts: main {2: 95,278, 4: 154,622}; supp {2: 919, 4: 24,005}. QEL, COH and MEC are 0. hitnuc = 2212 for all 249,900 + 24,924 CC events |
| B2 | **PASS.** The rebuilt `<50 GeV` and full C12 products (xsec, sumw2, nevt) are bitwise equal to the frozen ones; the frozen sampling statistics are reproduced |
| B3 | **PASS.** The supplement flux is bitwise phi_t × width and r is constant. The sampling test on the supplement gives p = 0.525 / 0.629 (across / within) with the H1 graph, the primary, as ruled; the literal C12 graph gives 0.525 / 0.641. The main sample, under the chain's own STOP rule, gives 0.585 / 0.880 (H1) and 0.547 / 0.863 (C12) |
| B4 | **PASS.** The H/C12 error ratio is ≤ 0.282 in every reported cell (worst J55; median 0.125); 3 cells have no H event |

**Evaluation controls (all pass).**
- J-cell μ and Var of the rebuild are bitwise equal to the frozen prediction.
- NuWro's `test_null` is bitwise equal to `joint-evaluate.json`.
- The robust nulls, both Holm decision sets and `holm_point` are bitwise equal to the frozen record.
- The identity replay (μ := μ_C12) returns A7 exactly.
- The combination identity holds to 5.6e-16.

## 4. The kaskada_on check (director's ruling)

- **RNG and content.** RNG consumption is identical for all 30 matched seeds: `in` and `out` agree for all 275,000
  events. Particle content is identical.
- **Final states.** 169,240 events are exact, and 243,422 are within 1e-6 MeV. **31,578 differ in momentum.** Under
  kaskada_on = 1:
  - Λ (5,613 particles) has E higher by exactly 27 MeV;
  - Σ⁰ (930) and Σ⁺ (4,977) have E lower by exactly 70 MeV;
  - protons (20,084) have ΔE = 0 and |Δp| ≤ 0.031 MeV.
- **Rule outcome.** The final states differ, so by the declared rule **kaskada_on = 1 (A) stays primary**.
- **No observable is affected.** The H and CH fine products are **bitwise identical** between k1 and k0: E_avail, W and
  q3 do not read hyperon energies, and proton energies are unchanged.
- **The abort is not in the cascade.** Under kaskada_on = 0, NuWro aborts at the same four seeds, at the same progress
  point, with the same Σ print. This **corrects** the pointer to `kaskada7.cc` in ATTEMPT1-STOP.md §2 and in the
  session's message to the director. The abort site is unidentified.

## 5. Readout (A), DESCRIPTIVE, not a re-grade

**Integrated over the grid:** σ_H/σ_C12 per nucleon = 0.642 (probe 0.642), and f_H = 5.08%.

**Over the 109 reported cells:**

| quantity | min / median / max | other |
|---|---|---|
| r_c = μ_CH/μ_C12 | 0.923 / 0.963 / 1.039 | Σ ratio 0.9722; median \|r − 1\| is 18 × its MC error (median 0.0019) |
| shape-normalized r_c | 0.949 / 0.991 / 1.069 | |
| f_H | 0 / 0.042 / 0.112 | Σ 0.0506 |
| Δ/σ, reading (a) | −1.46 / −0.42 / +0.55 | 100 cells < 0, none > 1, 44 with \|Δ/σ\| > 0.5; Σ(Δ/σ)² = 37.0 |
| Δ/σ, reading (b) | −1.12 / −0.36 / +0.50 | |
| Δ/σ, reading (c) | −1.16 / −0.37 / +0.54 | |
| shape Δ/σ | −1.84 / −0.15 / +1.92 | |

- **By region** (Σ r / f_H / Σ shape-r):
  - W < 1.4: 0.976 / 0.055 / 1.004.
  - W 1.4–2.2: 0.969 / 0.047 / 0.996.
  - W ≥ 2.2: 0.972 / 0.050 / 1.000.
  - E_avail < 0.4: 0.956 / 0.035 / 0.984, with Δ/σ from −1.46 to −0.18.
  - E_avail 0.4–1.5: 0.981 / 0.059 / 1.009.
  - E_avail ≥ 1.5: 0.975 / 0.054 / 1.003.
- **By fine W bin, inside the reported cells:** W0 0.923 (f_H 0.0001); W1 1.025 (0.100); W2–W5 0.967–0.972.
- **Largest |Δ/σ|:** J58, J139, J31, J112, J197, J224, J136, J28, J143, J35.
- **Norms.** ΔᵀW⁻¹Δ = **81.1** under the frozen W (86.1 with W_CH; 231.5 with V alone). The shape norm with the
  Jacobian at the data is **91.6** (70.3 at μ_CH, 73.5 at μ_C12).

**T replay against NuWro's frozen null** (null median ± SD: total 6323.9 ± 174.3, shape 7110.3 ± 890.0):

| metric | T_total (Δ in null SD; margin over median) | T_shape (Δ; margin) | claim p (k): total / shape | decisions (Holm with determinacy) |
|---|---|---|---|---|
| frozen (A7) | 7427.1 (6.33) | 9660.0 (2.86) | 0.00057 (0) / 0.00114 (1) | both rejected |
| **CH, frozen W** | 6759.8 (−3.83; 2.50) | 9333.1 (−0.37; 2.50) | 0.0257 (44) / 0.0040 (6) | **both rejected**, see below |
| CH, W_CH | 7328.4 (−0.57; 5.76) | 10122.2 (+0.52; 3.38) | 0.00057 (0) / 0.00057 (0) | both rejected; no change |

- **The re-sort under the frozen W.**
  - NuWro shape moves to threshold 0.025, with CP [0.00126, 0.00744]. That is 0.74 SD above its frozen T_crit of
    8672.55.
  - NuWro total moves to the LAST position, threshold 0.05, with CP [0.0183, 0.0336].
  - At its frozen position (threshold 0.005, T_crit 6953.94), total would be (6759.8 − 6953.94)/174.29 = **−1.11 SD**,
    i.e. undetermined. It stays rejected only because the order changed.
- **κ = 3 robust (report-only), frozen W.** NuWro total p = 0.0748 (k = 130): **not rejected**. Shape is rejected.
- **Decomposition.** T_CH − T_C12 = −748.4 (cross term) + 81.1 = −667.4. The data lie on the CH side of NuWro's C12
  prediction, the opposite sign to GENIE's in MP3-A.
- **Jitter p under the frozen W** (A7's own stability check, p over the data's 20 rounding jitters): total 0.020–0.039,
  shape 0.0034–0.0040.
- **A diagnostic null evaluated with the CH metric** (not the frozen null): margins 2.54 / 2.50 SD, p 0.0080 / 0.0023.

## 6. Variant (C): "mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH"

- **Construction.** The H part is 13 × MP3-A's GENIE CV `xsec_H1` (sha256 `f2599b71…`, as in its receipt). The split
  closes to 1.1e-14; B2 is bitwise.
- **B4 is NOT met** (report only; it does not gate (C)): 21 cells exceed 1/3, worst 1.41 (J152). The GENIE H sample is
  statistically thin. The job log's "B4 passed" line for (C) is wrong.
- **Readout.** Σ ratio 0.9786, f_H 0.0567, Δ/σ −1.47 / −0.33 / +0.72, ΔᵀW⁻¹Δ = 93.7.
- **Frozen W.**
  - T_total 6480.7 (−5.43 SD; claim p 0.332).
  - T_shape 8798.8 (−0.97 SD; p 0.0251, k = 43), at threshold 0.025 with CP [0.0178, 0.0329]: **undetermined**.
  - NuWro total inherits **undetermined**. κ = 3 gives the same.
- **W_CH.** Both claims p = 0.0034; no change.

## 7. Jobs and charge (ElapsedRaw × billing / 256 / 3600)

| job | QOS | State | Exit | ElapsedRaw | billing | CPU node-h |
|---|---|---|---|---:|---:|---:|
| 60017813 | shared | CANCELLED (held, never started) | 0:0 | 0 | — | 0 |
| 60022605 | debug | FAILED (attempt 1, Σ abort) | 5:0 | 275 | 256 | 0.076389 |
| 60029039 | debug | FAILED (generation, kaskada check and (C) done; the NuWro builds crashed on a C1 print bug before any gate) | 6:0 | 164 | 256 | 0.045556 |
| 60029088 | debug | COMPLETED (build and eval only, on the same files, after the print fix) | 0:0 | 121 | 256 | 0.033611 |

- **Totals.** 0.156 CPU node-h against a 3 node-h cap; 0 GPU.
- **Why debug.** Shared was draining ahead of maintenance_20261021, so the jobs ran on debug, which bills a full node.
- **The fix.** One print line in `mp3b_build.py` (blob `91e1aa12` → `4777ae07`). No gate or formula changed. The as-run
  copy is kept at `runA/mp3b_build.py.as-run-60029039` on the cluster.
- **Timing and storage.** Everything finished by 01:13 PDT 10-20. Outputs are only under
  `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/`; nothing went to CFS.

## 8. Not established

- The abort site inside NuWro. It is not the cascade.
- Why proton 3-momenta shift under k0.
- The excluded fraction, beyond a 1–4-event estimate.
- Any independent recompute. Every control is self-consistency against frozen bytes.

## 9. Files

- **Code:** `measurement-paper/phase1/mp3b/`: `mp3b_jobA.sh`, `mp3b_jobA_post.sh`, `mp3b_build.py`, `mp3b_eval.py`,
  `mp3b_mixed.py`, `mp3b_kaskada.py`, `compare_kaskada.C`, `SEEDS-chunked.txt`. The originals, `mp3b_job.sh` and
  `SEEDS.txt`, are kept.
- **Evidence, in this directory:**
  - `runA/`: logs, `out/kaskada_decision.json`, `out/eval_mixed/`, `out_r2/build_k{1,0}/mp3b_build.json`,
    `out_r2/eval_k{1,0}/`, the per-chunk comparison files, `attempts.tsv` and the `RESULT` files;
  - attempt 1's `gen/` and `logs/`;
  - [`PREP.md`](PREP.md).
