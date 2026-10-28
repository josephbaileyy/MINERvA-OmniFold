# F1 report: the GENIE v3 held-out bias test (2026-10-28)

**By** the measurement session, under [`FD-F1-BINDING.md`](FD-F1-BINDING.md) (PR #429),
[`FD-F1-BINDING-AMENDMENT-1.md`](FD-F1-BINDING-AMENDMENT-1.md) (PR #435) and
[`FD-F1-BINDING-AMENDMENT-2.md`](FD-F1-BINDING-AMENDMENT-2.md) (PR #445), for the director.

**What this is:** a bias test at two held-out GENIE v3 truths, **not a coverage test**, as the readout's own label
says: "a bias test at two held-out GENIE v3 truths, not a coverage test: Poisson pseudo-data with no nuisance draws
cannot test the intervals' width (…); the detector response is not probed".

**MEASURES:** the 5D estimator's per-cell bias at two GENIE v3.04.00 truths, G18_10a_02_11b and AR23_20i_00_000,
graded against the reported C_total + C_resp. **CANNOT AUTHORIZE:** a reading, a claim, paper text, or any
statement about coverage. Numbers only; nothing here interprets them.

**The readout:** [`fd/readout/fd_f1_readout.json`](fd/readout/fd_f1_readout.json), schema `fd-f1-readout/1`, sha256
`cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7`. Its table is on pscratch, as F0b's:
`$OUT/grade/fd_f1_experiments.npz` (table sha256 `997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc`).
`$OUT` is `/pscratch/sd/j/josephrb/fd-f1-20261027` throughout.

## 1. The grade

The grade is `fd_f0_regrade.py` with F0b's recorded argv plus the declared F1 options (FD-F1-DECLARATION §5). It ran on login36 at
0 node-h, in F0b's environment (Python 3.11.14, numpy 1.26.4), and exited 0.

**Control 9 passed:** "the 18 F0b truths grade exactly as the committed F0b readout records them, field for field".
The grader's controls passed are 0–6, 8 and 9. **Control 7**, the offset control that gates only row 6, did not
pass, so row 6 is descriptive and ungraded: χ²₁₆ 245.742, p 0. That is the same line, with the same χ², as F0b's own
committed output (`fd/receipts-f0b/f0b.out:30`).

### 1.1 The full-matrix records (the graded result, ruling 2)

Each truth's ensemble (row 7, 20 Poisson pseudo-experiments on half the MC) and its noise-free closure (row 8) are
graded against C_total + C_resp, ndf 16. The p value is descriptive, because b is a deterministic bias.

| record | row | experiments | χ² (full matrix) | ndf | p (descriptive) | max abs(z), cell | cells abs(z) > 2 | p < 0.01 |
|---|---:|---:|---:|---:|---:|---|---:|---|
| `F1_genie_v3_g18` | 7 | 20 | 11.836 | 16 | 0.755 | 0.623, R11 | 0 | no |
| `F1_closure_genie_v3_g18` | 8 | 1 | 11.440 | 16 | 0.782 | 0.608, R11 | 0 | no |
| `F1_genie_v3_ar23` | 7 | 20 | 16.863 | 16 | 0.395 | 0.644, R07 | 0 | no |
| `F1_closure_genie_v3_ar23` | 8 | 1 | 16.050 | 16 | 0.449 | 0.600, R07 | 0 | no |

**Per cell:** the bias b = X̂/X_true − 1 (the ensemble mean for row 7, the noise-free value for row 8) and the
full-matrix z = b/√diag(C + N) of each record (N = 0 for a closure).

| cell | G18 b | G18 z | G18 closure b | G18 closure z | AR23 b | AR23 z | AR23 closure b | AR23 closure z |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R00 | +0.0092 | +0.129 | +0.0083 | +0.117 | +0.0108 | +0.153 | +0.0097 | +0.137 |
| R01 | -0.0039 | -0.055 | -0.0032 | -0.045 | -0.0024 | -0.033 | -0.0021 | -0.030 |
| R02 | -0.0123 | -0.088 | -0.0126 | -0.090 | -0.0178 | -0.127 | -0.0173 | -0.124 |
| R03 | -0.0302 | -0.239 | -0.0296 | -0.234 | -0.0407 | -0.322 | -0.0371 | -0.293 |
| R04 | +0.0013 | +0.031 | +0.0022 | +0.053 | +0.0020 | +0.049 | +0.0015 | +0.037 |
| R05 | +0.0088 | +0.118 | +0.0080 | +0.106 | +0.0133 | +0.178 | +0.0135 | +0.181 |
| R06 | +0.0007 | +0.011 | -0.0007 | -0.011 | -0.0041 | -0.069 | -0.0043 | -0.074 |
| R07 | -0.0404 | -0.506 | -0.0429 | -0.538 | -0.0513 | -0.644 | -0.0479 | -0.600 |
| R08 | +0.0247 | +0.394 | +0.0200 | +0.319 | +0.0153 | +0.245 | +0.0144 | +0.230 |
| R09 | +0.0121 | +0.193 | +0.0123 | +0.197 | +0.0088 | +0.141 | +0.0084 | +0.134 |
| R10 | -0.0084 | -0.098 | -0.0113 | -0.131 | -0.0232 | -0.270 | -0.0237 | -0.276 |
| R11 | -0.0852 | -0.623 | -0.0832 | -0.608 | -0.0557 | -0.407 | -0.0553 | -0.404 |
| R12 | +0.0053 | +0.080 | +0.0061 | +0.091 | +0.0045 | +0.068 | +0.0068 | +0.103 |
| R13 | -0.0381 | -0.344 | -0.0367 | -0.331 | -0.0287 | -0.260 | -0.0295 | -0.267 |
| R14 | +0.0001 | +0.001 | +0.0012 | +0.023 | +0.0026 | +0.050 | +0.0021 | +0.041 |
| R15 | +0.0094 | +0.118 | +0.0072 | +0.090 | +0.0062 | +0.078 | +0.0058 | +0.072 |

**The triggers in the held-out group** (ruling 2 of the original binding: reporting triggers, not gates). The rule is
"a cell with |z| > 2, or a truth with P(χ²₁₆ > χ²) < 0.01, against the grade matrix".
- **Per record** (the table above): `F1_genie_v3_g18`, `F1_closure_genie_v3_g18`, `F1_genie_v3_ar23` and
  `F1_closure_genie_v3_ar23` each have 0 cells with |z| > 2 and p ≥ 0.01.
- **The grader's group tally,** as binding §4.8 and the declaration §5 require it: 0 of 64 cells and 0 of 4 records.
  It prints a Gaussian reference beside it (2.91 cells, 0.04 records), which the readout labels "context only: b is a
  deterministic bias, not a Gaussian draw".
- **The four records are not four independent tests.** They are two truths, each counted twice, by its ensemble and
  by its own noise-free closure, and the two truths share their CCQE model (§1.3). The reference's 64 × P(|z| > 2)
  and 4 × 0.01 count them as if they were independent; it is printed here only as the readout records it.

The group is never pooled with the vertex-family, non-vertex or prior groups, and it is kept out of `all_graded`.

### 1.2 The descriptive records

The declared sensitivity matrix leaves the GENIE+MEC vertex out. It is descriptive for both truths and was not chosen
after reading. The model-only variant is descriptive, as in F0.

| record | leave-out-GENIE+MEC χ² (ndf 16), p | model-only χ² (ndf 16), p; cells abs(z) > 2 |
|---|---|---|
| `F1_genie_v3_g18` | 15.155, 0.513 | 817.4, 0; none |
| `F1_closure_genie_v3_g18` | 14.352, 0.572 | 833.6, 0; none |
| `F1_genie_v3_ar23` | 24.604, 0.077 | 828.4, 0; R00 |
| `F1_closure_genie_v3_ar23` | 22.427, 0.130 | 921.8, 0; R00 |

The model-only label, from the readout: "descriptive, no threshold: C_stat + C_model leaving out the own vertex; drops
the interaction, flux, detector, lateral and normalization blocks, so a lower bound on C_model's reach".

### 1.3 The overlaps (ruling 2)

- G18_10a_02_11b's 2p2h is `NievesSimoVacasMECPXSec`, the Valencia family of the GENIE+MEC vertex (GENIE 2.12 +
  Valencia MEC).
- Both truths use `NievesQELCCPXSec` for CCQE. AR23_20i_00_000's 2p2h is `SuSAv2MECPXSec`, not the Valencia family.
- Both are GENIE-family truths, so they are partial evidence (`LIMITATION-PLAN.md` §1.4, 1A).
- **The two truths are not two independent tests.** Each is reported on its own above, and nothing here sums or
  combines them as independent.

### 1.4 f_MEC, spline versions and the energy range (rulings 3 and 4)

| | G18_10a_02_11b | AR23_20i_00_000 |
|---|---|---|
| f_MEC (gen5d meta `normalisation.f_MEC`) | 0.026116 | 0.035285 |
| spline product README version line | `version v3_02_00 qualifier G1810a0211b:k250:e1000` | `version v3_04_00 qualifier AR2320i00000:k250:e1000` |
| spline header check (F1a) | tune G18_10a_02_11b, format 3.00, 937 splines, refused: none | tune AR23_20i_00_000, format 3.00, 937 splines, refused: none |
| events generated / CC | 1,120,000 / 823,440 | 1,120,000 / 825,082 |
| CC events with E_ν > 50 GeV | 3,651 | 3,660 |
| fine cells, of the 10,694 CV-positive: own ratio / coarse cell (pooled) / r = 1 | 141 / 5,324 / 5,229 | 143 / 5,218 / 5,333 |
| prior-weight share of those tiers | 0.266 / 0.696 / 0.038 | 0.269 / 0.691 / 0.040 |
| ratio normalisation k | 0.98897 | 0.97906 |

**Sources:**
- f_MEC and the event and CC counts: `cluster/f1b3/gen5d/*.meta.json`. The CC counts equal the gst counts.
- The spline rows: `cluster/f1a/spline_check_*.json`, F1a's products, reused after re-verification.
- The E_ν > 50 GeV counts: `s14-look.out`, from F1b′'s merged gst, tree `gst`, `cc==1 && Ev>50`.
- The tiers and k: the prep's `ratios/L-5D-PV/ratios.json` (gate `stat_max` 0.05), on pscratch, identified in the
  committed `f1-prep-SHA256SUMS`.

No event fell outside the grid on any axis in either conversion.

## 2. The run

**Scope:** what ran, and in what order, under the three bindings. Jobs are on Perlmutter CPU, regular QOS, one
exclusive node, `--no-requeue`, no GPU.

| step | where | job | state | elapsed | batch MaxRSS (K) | node-h |
|---|---|---|---|---:|---:|---:|
| deploy and tests (binding §4.1) | login12 | — | 31, 47 OK | 326 s | — | 0 |
| F1a | nid005953 | 60415571 | COMPLETED; gate GO | 377 s | 45,610,936 | 0.104722 |
| F1b | nid006737 | 60417614 | OUT_OF_MEMORY: STOP | 730 s | 499,490,432 | 0.202778 |
| amendment-1 deploy and tests | login38 | — | 13, 31, 47 OK | 441 s | — | 0 |
| F1a′ re-pilot | nid005643 | 60425719 | FAILED 3:0 = budget2 STOP | 363 s | 287,876,772 | 0.100833 |
| amendment-2 deploy and tests | login36 | — | 15, 13, 31, 47 OK | 479 s | — | 0 |
| F1b′ | nid006313 | 60436278 | COMPLETED 0:0 | 1,116 s | 300,836,072 | 0.310000 |
| F1c deploy and submit | login36 | — | prep OK | 38 s | — | 0 |
| F1c | nid007141 | 60439400 | COMPLETED 0:0, 8 lanes COMPLETED | 2,193 s | 118,368 (lane steps up to 17,530,368 = sacct's 17119.50M, line0) | 0.609167 |
| checks and product manifest | login36 | — | 42 products | 1 s | — | 0 |
| grade (deploy at `da5f157f`, then the grade) | login36 | — | rc 0, control 9 PASS | 116 s (grade 71 s) | — | 0 |
| HPSS | login36 | — | PASS | 46 s | — | 0 |

**The total charge is 1.327500 node-h,** against the priced 2.0 and Joseph's ceiling of 2.5
(`DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` item 1). The ledger rows are `F1 S4.1`–`S4.13` in
[`fd/LEDGER.tsv`](fd/LEDGER.tsv).

### 2.1 F1b and the first STOP (amendment 1's report items)

- **The STOP:** F1b ran 128 gevgen processes at once and ran out of memory at gevgen's start-up. Its receipts are from
  `fd/f1-report` at `183b31e4` (merged in PR #442), with ledger rows S4.1–S4.3.
- **The re-pilot, against budget2's limits** (`cluster/f1a2/budget2.json`):
  - memory passed: 14 × the largest per-process RSS, 22,015,472 K, is 61.7 % of the node, against 75 %;
  - wall did not: the long walls were 215.81–327.72 s, so F1b′ in 10 waves projected 4,177.2 s, and 1.25 × that is
    5,221.5 s against 3,420 s. The priced and ceiling rules failed too, at 2.3156 against 2.0 and 2.7719 against 2.5.
  - That was the second STOP. Amendment 2 re-laid F1b′ from its records.
- **§2 of amendment 1, the pilots' process mix,** from each pilot's gst (10,000 events per tune):

| flag | G18_10a_02_11b, all (CC) | AR23_20i_00_000, all (CC) | in the list |
|---|---:|---:|---|
| qel | 938 (663) | 902 (661) | QEL-CC, QEL-NC |
| mec | 238 (203) | 320 (283) | MEC-CC, MEC-NC |
| res | 2,254 (1,592) | 2,284 (1,637) | RES-CC, RES-NC |
| dis | 6,495 (4,785) | 6,432 (4,780) | DIS-CC, DIS-NC |
| coh | 60 (40) | 52 (30) | COH-CC-PION, COH-NC-PION |
| dfr | 15 (9) | 10 (9) | DFR-CC, DFR-NC |
| charm | 103 (103) | 88 (88) | DIS-CC-CHARM, QEL-CC-CHARM |
| imd, imdanh, nuel, em, singlek, amnugamma | 0 | 0 | IMD, IMD-ANH, NUE-EL; the rest are not in the list |
| CC / NC | 7,292 / 2,708 | 7,400 / 2,600 | |
| events with no flag; with two or more | 0; 103 | 0; 88 | the two-or-more count equals the charm count |

### 2.2 F1b′ against its projection (amendment 2's report items)

**The gate** (`cluster/gate3/budget3.json`) projected a task wall of 1,704.7 s, an F1b′ wall of 2,604.7 s, a total of
1.8819 node-h and a worst case of 2.2250. The job's limit was 0:55, and the per-task timeout was 5,115 s.

**Measured:** the longest task took 1,022.8 s, 60.0 % of the projected task wall, and the job took 1,116 s, 42.8 % of
the projected F1b′ wall. Every task exited 0. The NOWIDTH flux-check passed for all 14.

| tune | seed | wall (s) | max RSS (K) | exit |
|---|---:|---:|---:|---:|
| AR23_20i_00_000 | 61001 | 554.66 | 21,624,488 | 0 |
| AR23_20i_00_000 | 61002 | 567.05 | 20,371,376 | 0 |
| AR23_20i_00_000 | 61003 | 569.04 | 21,548,376 | 0 |
| AR23_20i_00_000 | 61004 | 556.67 | 20,261,980 | 0 |
| AR23_20i_00_000 | 61005 | 569.83 | 21,270,224 | 0 |
| AR23_20i_00_000 | 61006 | 558.33 | 20,991,640 | 0 |
| AR23_20i_00_000 | 61007 | 568.26 | 20,739,260 | 0 |
| G18_10a_02_11b | 60001 | 1022.80 | 22,378,784 | 0 |
| G18_10a_02_11b | 60002 | 785.71 | 22,008,860 | 0 |
| G18_10a_02_11b | 60003 | 759.63 | 22,474,848 | 0 |
| G18_10a_02_11b | 60004 | 791.58 | 21,510,652 | 0 |
| G18_10a_02_11b | 60005 | 873.69 | 22,753,284 | 0 |
| G18_10a_02_11b | 60006 | 675.28 | 21,430,012 | 0 |
| G18_10a_02_11b | 60007 | 998.87 | 21,438,720 | 0 |

**Memory:**
- The largest per-process RSS, 22,753,284 K (G18 seed 60005), is **3.35 % above** the re-pilot's largest, 22,015,472 K.
  The re-pilot's tasks ran up to 17,500 events; F1b′'s ran 160,000.
- 14 × that largest RSS is 63.8 % of the node. The node-level batch MaxRSS was 300,836,072 K, 60.2 %. Both are within
  the 75 % rule.

### 2.3 F1c

**The deploy:** F1c ran from `$OUT/deploy/f1c` at the F1c pin `741ad029`. It was absent beforehand, HEAD was the pin
and porcelain was 0. Its 8 lanes ran the pin's 10 steps (`f1c/f1c-steps.tsv`, `f1c/tasks-f1c.tsv`).

**Each lane opens only:**
- the committed tables;
- the prep's ratio and bridged JSONs on pscratch, each with its expected sha256;
- `of_inputs_5d.npz` and `bkg_dump.npz`, by pinned sha256.

**The product manifest** (`cluster/manifest/f1-products-SHA256SUMS`, sha256 `fdb02740…`):
- It lists **42 products**: 2 closures and 2 × 20 pseudo-experiments. They are equal by name to the tables' 42
  declared outputs.
- Every product file lies under `closure/` or `pe/<truth>/`. Everything else in `$OUT/f1c` is the launcher's
  `line*-60439400.log`, the lane environment logs in `logs/`, and `inventory/` (`s11.out`).

## 3. Deviations and disclosures

1. **The f1b/ reads (`FD-F1-BINDING-AMENDMENT-2.md` §3, restated).**
   - `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` item 1 says the partial F1b output "stays
     untouched as the STOP's evidence and is never read". `FD-F1-BINDING-AMENDMENT-1.md` forbids any read of `f1b/`.
   - The reads are recorded by amendment 2 §7 and its committed transcript sweep (`fd/receipts-f1/amendment-2/`
     `disclosure_sweep.py` and `disclosure-sweep.out`, command bodies C1–C14):
     - **before amendment 1's binding:** the measurement session's probes 18 and 19 (C5, C6) read F1b's 128 task logs
       and the work-directory status files of four seeds, `grep -c Killed` included; amendment 1's §1 cites them;
     - **after amendment 1's binding:** the F1a′ review hashed the 128 task logs (C9) and read file metadata, against
       binding amendment 1's prohibition. Amendment 1's own review (C1–C4) read metadata only.
   - **No gst or GHEP event content was read.** All 22 gst files were last accessed when F1b wrote them, provided
     Lustre updates access times on read. Nothing in `f1b/` was modified.
   - **The effect,** as the binding records it: none on any F1 product or grade. The reads were of logs, status files
     and metadata from a stopped job, used to diagnose its failure. No event from F1b enters F1b′, F1c or the grade.
   - **The director's share,** as the binding records it: the director bound amendment 1 with §1 citing probes 18 and
     19, and did not connect them to the decision's "never read". The measurement session raised it first.
2. **The F1c product root (director's ruling R4, §6):** a deviation from FD-F1-DECLARATION §4, §5 and §9. It is a change
   of product path only, made when the tables were generated.
   - The pin's committed tables name `$OUT/f1c/closure` and `$OUT/f1c/pe`, not `$OUT/f1c/products/`.
   - The manifest was made with `--runs $OUT/f1c`, the grade used `--f1-root $OUT/f1c`, and the HPSS members are
     `f1c/closure` and `f1c/pe`.
   - Nothing was moved after the fact.
3. **The F1c pin and the manifest gate (director's ruling R1, §6).**
   - The F1c pin `741ad029` is a child of the bound pin `5f5e392c`. It changes 63 files, all under `fd/receipts-f1/`.
     The pre-commit hook passes on exactly that diff.
   - `generate_manifest.py --check` fails at the pin, because its receipts are manifest rows. The report branch
     regenerates the manifest after it (`s9-pin-checks.out`).
4. **Files held out of the pin, then landed (director's rulings R2 and R3, §6).** A deviation from
   FD-F1-DECLARATION §6, whose first receipt commit carries the gen5d meta JSONs.
   - The two gen5d meta JSONs and `prep/config-f1.json` were not in the pin, because their results-index rows and a
     citation need paths outside `fd/receipts-f1/`. The pin's `f1b3-SHA256SUMS` identifies all three by sha256.
   - The meta JSONs landed with the results-index regeneration, and their bytes match those digests
     (`s9-held-check.out`).
   - `config-f1.json` landed with a byte copy of the `k1_p5_rerun.npz` it cites, 95,311 bytes. Its sha256 `e36f3b25…`
     equals the §8 pin and the cluster original (`s9-npz-check.out`). The hook passed with no override.
5. **The first amendment-2 deploy launch ran an empty script** (director's acknowledgement R5, §6). The command and
   the first launcher's text are in `s7-first-attempt.txt`; that launcher had no hash check, and it ran with its stdin
   from `/dev/null`. It ran nothing: no clone, no tests, no output directories. Its two 0-byte files are kept as
   `*.aborted-empty-20261028T103228Z`. The real step was uploaded separately and launched by the committed, hash-checked
   `s7-launch.sh` only after its sha256 matched (`s7-launch.out`).
6. **The grade's command** (`s12.sh`):
   - It is F0b's recorded argv (`fd/receipts-f0b/step3.sh`) with every input path in F0b's own deploy `c4396756`
     (porcelain 0) and the same C_resp extra block, plus the declared F1 options.
   - The program came from a deploy of the second receipt commit `da5f157f`, which carries the committed product
     manifest.
   - The `timeout` wrapper was 900 s, where F0b's was 375 s. That is a wrapper, not an argument; the grade took 71 s.
7. **The HPSS tar's name,** `stage0-inputs.tar`, is the fixed name in `stage0_preserve.sh`, which the binding names as
   the pattern.
8. **The F1c pin's branch** (director's ruling R1, §6). Binding §4.4 has the first receipt commit "pushed on the report
   branch". It was pushed on its own branch, `fd/f1c-pin`, as R1 directs, and merged into the report branch with merge
   commits, so the pin is an ancestor of the report.
9. **The E_ν > 50 GeV count ran twice.** A first run at 12:26:26Z, with no end stamp, gave the same counts as the
   stamped run in `s14-look.out` (12:29:31–12:29:42Z), which is the one recorded.

## 4. HPSS (binding §4.7)

- **Path:** `/home/j/josephrb/mnv-5d-f1-20261028/stage0-inputs.tar`, 1,229,916,160 bytes, sha256
  `d05cf925767d6431d8714732dc64dce9f727dc8ea1213f7daea0e1e356e0dde3`, with `INVENTORY.sha256` and
  `stage0-inputs.tar.sha256` beside it.
- **Members:** 60 files from `f1a/splines`, `f1b3/gst`, `f1b3/gen5d`, `f1b3/prep`, `f1c/closure` and `f1c/pe`; never
  `f1b/` or `f1b2/`.
- **Before the tar,** each inventory line matched a committed sums line: `f1a-SHA256SUMS`, `f1b3-SHA256SUMS` or the
  product manifest, 60 of 60.
- **The copy** was verified by `hsi hashverify` and by retrieval and sha256 compare (`cluster/logs/preserve-f1.out`).
  `hpssquota` at 14:12:59Z, after the copy, shows 422.79 of 512 GiB used (`s15-look.out`). That equals F0b's
  2026-10-26 reading (`FD-F0b-REPORT.md`), unchanged although 1,229,916,160 bytes were written to HPSS in between;
  this run took no reading before the copy.

## 5. Records and retention

- **Receipts:** `fd/receipts-f1/run/`.
  - Steps s1–s6 are from the earlier bindings; s7–s14 are from this one.
  - Cluster records are under `cluster/`. Every fetched file was verified by sha256 against the cluster.
- **Commits:**
  - the F1c pin `741ad029` and the second receipt commit `da5f157f`, on `fd/f1c-pin`;
  - both merged into the report branch `fd/f1-run-amend2` with merge commits, so both are its ancestors.
- **Retention:** `fd-f1-20261027` stays on the pscratch list. It holds `f1a/`, `f1a2/`, `f1b3/`, `f1c/`, `manifest/`,
  `grade/`, `preserve/`, `gate3/`, the deploys, and `f1b/`, unmodified (its disclosed reads are in §3, item 1). (`f1b2/` did not exist at amendment 1's deploy check,
  `s4.out`, and amendment 1's F1b′ was never submitted after F1a′'s STOP.)
  <!-- absence-ok: s4.out:35 records "f1b2 exists=no" at amendment 1's deploy check; f1b2/ is not read under the binding, so no newer listing is made -->

## 6. The director's rulings during the run

The director (the paper-tighten lane) gave these rulings in messages to the measurement session on 2026-10-28, after
the bindings. They are quoted here, in order, as the record of their authority. The director may also record them
separately.

- **R1, the F1c pin and the manifest gate:** "Your F1c-pin plan is accepted. The path rule governs the F1c deploy pin,
  and the six gates govern what lands on main. They can differ at a deploy pin as long as the report branch head passes
  all six before any PR." Its conditions: "The F1c pin commit is a child of 5f5e392c that changes only fd/receipts-f1/
  paths. The receipts record `git diff --stat 5f5e392c <F1c pin>`, plus the fact that `generate_manifest.py --check`
  fails there and why"; and "The pin must stay reachable from GitHub … Push it on its own branch, e.g. fd/f1c-pin,
  before deploying. Merge it into fd/f1-run-amend2 with a merge commit, never a rebase or squash." It also accepted
  `$OUT/deploy/f1c`, "given it is absent beforehand, HEAD equals the F1c pin, and porcelain is 0".
- **R2, the split of the pin commit:** "Your split is accepted. The pin commit on fd/f1c-pin carries everything declared
  except the two gen5d *.meta.json files and cluster/f1b3/prep/config-f1.json. Those three land in the next commit on
  the report branch, with the results-index regeneration under ruling (a), the MANIFEST and the ledger. No
  --no-verify, which is right." Its conditions: the pin identifies all three by sha256; no F1c step reads them from the deploy; a check
  that their committed bytes match the pin's digests; and the receipts give the diff --stat and the hook's PASS at the
  pin.
- **R3, config-f1.json:** "(c) replaces (a). Commit the byte copy of k1_p5_rerun.npz (95,311 bytes) with `git add -f`
  at cluster/f1b3/prep/k1_p5_rerun.npz. Its sha256 must equal the §8 pin and the cluster original, both recorded in the
  receipts. config-f1.json lands unchanged beside it, and the hook must pass with no override." The director's
  checker-fix follow-up was withdrawn in the same ruling.
- **R4, the F1c product root:** "option (i). Proceed with `--runs $OUT/f1c` for the manifest, `--f1-root $OUT/f1c` for
  the grade, and f1c/closure plus f1c/pe as the HPSS members. Record it in the report as a deviation from
  FD-F1-DECLARATION §4/§5/§9: a product-path change only, made at table generation, with the pin's committed tables
  naming the paths actually used. Don't move anything after the fact." Its two checks are in `s11.out`.
- **R5, the empty launch:** "The empty-launcher slip was handled correctly: it did nothing, the 0-byte files are kept
  and labelled, and the real body was launched only after its sha256 matched. Put it in the report's receipts as you
  have it."
