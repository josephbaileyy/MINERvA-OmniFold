# MP3-C: GiBUU on CH, beside A7, after a failed B3 and a passed post-hoc bias check

**By** the measurement session, 2026-10-20, under MP3-C and the director's ruling on option (b) (message, 2026-10-20;
binding addendum 7). Earlier stages are in [`STOP-B3.md`](STOP-B3.md). This file was written by the coordinating session
from the agent's report text, because the agent's write was refused.

**Label, required by the ruling:** "B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise
passed at ≤ 0.1 σ_c". **B3 stays FAILED.** No GiBUU-on-CH prediction is described as having passed its gates.

**CITABLE FOR:**
- GiBUU 2019's own carbon-to-CH target effect per J cell in the 72-cell GiBUU domain, under that label;
- the descriptive T replay beside A7.

**NOT CITABLE FOR:**
- a re-grade of A7 (D6);
- any claim.

Option (c), the borrowed GENIE hydrogen, was not run.

**Headline.** No decision change. GiBUU total and shape stay "rejected" under the frozen W, under W_CH and at κ = 3.
Their boundary margins shrink from 7.86 to 3.18 null SD (total) and from 3.58 to 2.24 (shape).

## 1. The post-hoc check (b)

- **Declared before computing:** `measurement-paper/phase1/mp3c/DECLARATION-b.json`, sha256 `00efbb25…`, recorded
  05:58 PDT 10-20. The job refused to run unless the file matched.
- **Alternative weight.** Applied in each 0.5 GeV flux point with E ≥ 1.5 GeV, over the 5 equal sub-bins B3 uses.
  - Unweighted least-squares fit of the sub-bin counts, n_j = α + β(x_j − 0.5), giving b = β/α.
  - Per-event factor s_e = c_k / (1 + b_k(x_e − 0.5)), with c_k fixed so that the sum of s over a point's events
    equals its event count. Events below 1.5 GeV keep s = 1.
- **Readout.** Δ_c = μ_CH,alt − μ_CH,frozen over the 72 GiBUU-domain cells, over σ_c in MP3-B's readings.
- **Acceptance.** max |Δ/σ (a)| ≤ 0.1.

| quantity | value |
|---|---|
| fitted slopes b_k | −0.059 to +0.212; largest at low energy (0.139 at 1.5 GeV, 0.066 at 2.0, 0.065 at 2.5, 0.052 at 3.0) |
| s on in-grid events, 1st / 50th / 99th percentile | 0.975 / 1.000 / 1.024 |
| **max \|Δ_c/σ_c\| (a)** | **5.1e-4** (J93); median −5.1e-5 |
| readings (b) / (c) | max 4.1e-4 / 5.0e-4 |
| Δ relative to the H contribution | ≤ 2.3e-3; integrated alternative/frozen 0.99970 |
| ΔᵀW⁻¹Δ (frozen W) | 1.4e-5 |
| control | the C12 rebuild is bitwise equal to the frozen GiBUU product (xsec, sumw2) |

**Check (b) PASSES.** The within-point slope that failed B3 moves the CH prediction by at most 5e-4 of a null SD.

## 2. GiBUU-on-CH readout, frozen r(E), 72 cells

- **B4 PASS.** The H/C12 error ratio is ≤ 0.082 in every cell (worst J9, median 0.036); 2 cells have no H event.
- **Controls.** All bitwise: GiBUU's frozen test recomputed, the robust nulls, the Holm decisions and `holm_point`.
  The identity replay returns A7 exactly.
- **Totals.** Σμ_CH/Σμ_C12 = **0.9693**; f_H = 0.0477.
- **Per-cell distributions** (min / median / max):

  | quantity | value | note |
  |---|---|---|
  | r_c | 0.923 / 0.963 / 1.036 | |
  | shape form | 0.952 / 0.994 / 1.069 | |
  | f_H | 0 / 0.042 / 0.109 | |
  | Δ/σ (a) | −1.57 / −0.42 / +0.41 | 64 of 72 cells < 0; Σ(Δ/σ)² = 25.5 |
  | Δ/σ (b) | −1.04 / −0.35 / +0.31 | |
  | Δ/σ (c) | −1.43 / −0.38 / +0.37 | |
  | shape Δ/σ | −2.41 / −0.08 / +1.80 | |

- **By region** (Σ r / f_H): E_avail < 0.4 is 0.952 / 0.030 (Δ/σ −1.57 to −0.11); E_avail 0.4–1.5 is 0.974 / 0.052;
  E_avail ≥ 1.5 is 0.979 / 0.057. By W: < 1.4 is 0.970, 1.4–2.2 is 0.962, ≥ 2.2 is 0.977.
- **Fine W bins:** W0 0.923 (f_H 1e-4); W1 1.017 (f_H 0.092); W2–W5 0.958–0.977.
- **Norms.** ΔᵀW⁻¹Δ = **47.7** (W_CH 52.0; V alone 170.9). The shape norm with the Jacobian at the data is **64.4**.

**T replay against GiBUU's frozen null (DESCRIPTIVE, not a re-grade).** The null has median ± SD 1791.4 ± 88.8 (total)
and 1975.0 ± 298.4 (shape).

| metric | T_total (Δ null SD; margin over median; margin above T_crit) | T_shape (same) | claim k / B | decisions |
|---|---|---|---|---|
| frozen A7 | 2867.0 (—; 12.12; 7.86) | 4013.3 (—; 6.83; 3.58) | 0 / 1351, both | both rejected |
| **CH, frozen W** | 2452.1 (−4.67; 7.44; **3.18**) | 3615.0 (−1.33; 5.50; **2.24**) | 0 / 1351, both | **both rejected**; κ = 3 also; **no change** |
| CH, W_CH | 2675.3 (−2.16; 9.96; 5.70) | 3971.3 (−0.14; 6.69; 3.44) | 0 / 1351, both | both rejected; no change |

- **Frozen positions.** T_crit is 2169.7 for total (threshold 0.01) and 2946.3 for shape (threshold 0.0125). Both
  replays stay above them, so unlike NuWro's (MP3-B), no Holm re-sort is involved.
- **Decomposition.** T_CH − T_C12 = −462.6 (cross term) + 47.7 = −414.9. The data lie on the CH side of the C12
  prediction, the same sign as NuWro.
- **Jitter p:** all at the floor, 7.4e-4.
- **Under the alternative (b) reweight:** T_total 2452.13, T_shape 3615.11 (frozen W); 2675.3 / 3971.4 (W_CH). These
  agree with the frozen-r(E) replay to ≤ 5e-4 null SD; claims k = 0; no decision change.

## 3. Jobs and charge (ElapsedRaw × billing / 256 / 3600)

| job | QOS | State | Exit | ElapsedRaw | billing | CPU node-h |
|---|---|---|---|---:|---:|---:|
| 60029251 | debug | FAILED (startup, environment) | 3:0 | 8 | 256 | 0.002222 |
| 60029299 | debug | COMPLETED (probe) | 0:0 | 99 | 256 | 0.027500 |
| 60029398 | debug | FAILED (B3 STOP) | 1:0 | 160 | 256 | 0.044444 |
| 60033564 | debug | COMPLETED (option (b) check and replays) | 0:0 | 75 | 256 | 0.020833 |

MP3-C total: **0.0950 CPU node-h**; 0 GPU. Everything finished by 06:01 PDT 10-20; nothing is left running.

## 4. Not established

- The cause of the within-point slope inside GiBUU.
- The missing final nucleon in ≈ 3e-4 of events.
- An independent recompute of the readout.

## 5. Files

- **Code:** `measurement-paper/phase1/mp3c/`: `DECLARATION-b.json`, `mp3c_bcheck.py`, `mp3c_bjob.sh`, and the earlier
  stage scripts.
- **Evidence:** this directory:
  - `out_b/bcheck/mp3c_bcheck.json`;
  - `out_b/eval_frozen/` and `out_b/eval_alt/`, each holding `mp3b_results.json` and `mp3b_cells.csv`; the eval reuses
    MP3-B's names;
  - `logs/`.
