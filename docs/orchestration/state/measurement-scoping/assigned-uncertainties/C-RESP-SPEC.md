# C_resp: the species-response block on R00–R15, as Stage G's declared sensitivity variant (2026-10-26, session "2d test")

**For** the director's binding, ahead of U-PLAN (assignment of 2026-10-25, under
`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` item 6).

**Status: specification only.**
- Nothing has been computed on real data.
- The only real-file reads were digests, and a probe of each product's `meta` record (§1.2). That probe reads no
  `xsec_flat`.
- The builder runs once, on a login node, after a binding.
<!-- absence-ok: a statement about this session's own actions: the only commands run on real files were sha256sum and receipts-prebinding/cresp_metaprobe.py, which loads only the `meta` key; $P/cresp-20261026 does not exist (ls -d on login37, 2026-10-26) -->

**CITABLE FOR:**
- the construction of C_resp: its inputs, species, estimator, combination and checks;
- the tool and its tests;
- the argv.

**NOT CITABLE FOR:**
- any value of C_resp;
- its adoption into the reported total, which is Joseph's decision, made from U-PLAN;
- coverage, or any claim.

C_resp enters Stage G as a **declared sensitivity variant**, not as an adopted component.

**MEASURES:** nothing yet. **CANNOT AUTHORIZE:** the run, which is the director's binding; adoption; any claim.

## 1. Inputs

### 1.1 The 11 products

**Where they are:** `$P/measurement-paper/phase1/mp1/s1/unf/`, with `P=/pscratch/sd/j/josephrb`. They are the MP-1 S1
data unfolds (`state/measurement-paper/phase1/mp1/S1-REPORT.md`, "Merges, dumps, unfolds" and "Unfold verification").
- **Verification:** all 11 PASS in `s1-receipts/verify/unfold_verify.json`, sha256 `2954de45…`.
- **Measured here:** each sha256 below was re-measured on login37 on 2026-10-25 and equals that receipt's
  `product_sha256`.
- **Pinned in the builder:** each product's two input digests (`input_npz_sha256`, `bkg_dump_sha256`) are pinned in
  `nd-unfolding/build_cresp.py` `PRODUCTS`, from the same receipt's `--npz` and `--bkg` entries.

| product | species, shift | sha256 |
|---|---|---|
| `mp1s1_zero_b-_j-.npz` | none (k = 0) | `f1d5178a86c1aa417d477d205669b642c66760b7e8e65f98b426e1d9d950d195` |
| `mp1s1_proton_m1_b-_j-.npz` | proton −1σ | `bfffb8c54df3895ac1f98113027382418789ed43b59224fe3de8d7bc36419091` |
| `mp1s1_proton_p1_b-_j-.npz` | proton +1σ | `8cbe49ae8407aafb2a67ecdcb6829717dfb8cd3ce1c0c8afe5469c9457f01390` |
| `mp1s1_meson_m1_b-_j-.npz` | meson −1σ | `6f3fbb50ec9102fe198d08f323c20ddce420457f5f3c2e5b13ed7f541a652a21` |
| `mp1s1_meson_p1_b-_j-.npz` | meson +1σ | `e54b01c1c44445362dc11d23c725fd957927348a91ad5ab2cda6ab25ba0e257c` |
| `mp1s1_em_m1_b-_j-.npz` | EM −1σ | `a13521a902c855209e4b7faba3d6e199819a7735e234d8385526d36b56de71d2` |
| `mp1s1_em_p1_b-_j-.npz` | EM +1σ | `15d8d224dba91f9f6ed80324e9bdd99403e1c9207b77c7f616fe70124418883c` |
| `mp1s1_other_m1_b-_j-.npz` | other −1σ | `6580cbde395d16bd3a2decf34dc1fd7dc06e7c87f1615af86826217115e4536e` |
| `mp1s1_other_p1_b-_j-.npz` | other +1σ | `b30f13fb4ea6813e01664c0c3e21c28f1ef7bb14c6dc79bf4a68e390788d799c` |
| `mp1s1_xtalk_m1_b-_j-.npz` | cross-talk −1σ | `c3d8134b28728af68a1e2d10cf4a38ca0061fe561a67cdb79b4d5742b446c882` |
| `mp1s1_xtalk_p1_b-_j-.npz` | cross-talk +1σ | `6e0abe1572bd6624223259dab92017b316702dbb68782d5a4aac7ebe9a8d8ce8` |

### 1.2 Their provenance, from a meta-only probe

**The probe:** [`receipts-prebinding/cresp_metaprobe.py`](receipts-prebinding/cresp_metaprobe.py), run on login37 at
2026-10-26T02:15Z. Its output is [`cresp-metaprobe.txt`](receipts-prebinding/cresp-metaprobe.txt). It loads each npz's
`meta` key and lists the keys present; it reads no other array.

**All 11 products agree:**
- schema `s5p-numerics/1`, config R, capacity None, 5 iterations, estimator seed 42;
- three B0 estimators at 100/8/42;
- the refinement ran, at 400/31, `random_state` 45, `deterministic` true and `bin_construct_sample_cnt` = all rows;
- construction `data`, truth `nominal`, no bootstrap or jitter seed, float32 coordinates;
- keys `meta`, `shape` and `xsec_flat`.

That is configuration (e), the S1 estimator (`s1_assemble.check_meta`).

**The input digests:** all 11 equal `unfold_verify.json` (0 mismatches).
- They are not S1's base inputs: these are lateral-style dumps of the species-shifted event loops.
- That is why the builder calls `check_meta(..., inputs=False)` with the per-product digests instead, as S1 does
  for its own laterals (`s1_assemble.py:337`).

### 1.3 The other inputs

| input | sha256 | role |
|---|---|---|
| S1 assembly `$P/s1-20261024/s1_assembly.npz` | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4`, re-measured on login37 2026-10-25 | f, U, C_e, C_model_abs, C_total; Stage G pins the same file (FD-G-DECLARATION, branch `5d-community/fd-g-20261025`, line 53) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` | R00–R15, via `s1_assemble.fine_map`, which also checks fine map `930326a3…` |

## 2. Species

**The species are MP-1's, at D1's sizes** (`phase1/mp1/S0-PREP.md:17-19`; `state/measurement-paper/PLAN.md:505`). The
shift is applied to the simulation's reconstructed recoil. The data are never shifted (S0-PREP:34).

| species | δ (1σ) | role here |
|---|---:|---|
| proton | 3.5 % | primary: in C_resp |
| meson | 5 % | primary: in C_resp |
| EM | 3 % | primary: in C_resp |
| other | 20 % | primary: in C_resp |
| cross-talk | 20 % | variant: built and reported, **not summed** |

**The conventions are as MP-1 S1 ran them** (`S1-REPORT.md:53`): q0 by F-propagation with each playlist's table, and
fuzz pro-rata.

**Why the split between primary and variant:**
- MP-1's frozen design has proton, meson, EM and other as primary, and adds cross-talk only as a variant
  (`S1-REPORT.md:66-67`).
- MAT's own list marks cross-talk "DO NOT USE" (`S0-PREP.md:239`).

**Not varied:** the muon, and the low-, mid- and high-energy neutron deposits. They are absent by construction
(`S0-PREP.md:18-19`; D1 chose neutrons out).

## 3. The per-species estimator

**For each species s,** with x(∓1) the two endpoint products and U the 16 × 65,856 functional matrix:
- **C_resp,s** = MAT mean-centred covariance of the two endpoint vectors U x(−1) and U x(+1), normalised by 1/N.
- This is S1's lateral convention exactly, `blocks[f"lat:{b}"] = mat_cov(np.array(X))` (`s1_assemble.py:341`, `mat_cov`
  at `:125`, docstring `:15`).
- With two endpoints it equals **d dᵀ, with d = (U x(+1) − U x(−1)) / 2**, the half-span outer product. The builder
  checks that identity to 10⁻¹² relative on every block.

**What this choice implies:**
- No central value enters, so the products' own k = 0 unfold need not equal S1's central value. It does not: its
  inputs differ (§1.2).
- A common offset cancels, and the endpoint order does not matter. Both are tested.
- Each block has rank ≤ 1, and carries the sign pattern of the species' response across cells.

## 4. How the blocks combine

- **Per species:** five separate blocks, `C_resp_proton`, `_meson`, `_em`, `_other` and `_xtalk`.
- **C_resp** = C_resp,proton + C_resp,meson + C_resp,EM + C_resp,other. The four species are independent sources, so
  the sum is not correlated across them. This is the rule for S1's other bands.
- **C_total_resp** = S1's C_total + C_resp. This is the matrix of Stage G's declared sensitivity variant. With each
  prediction's V_g it gives M = C_total_resp + V_g, beside the declared M = C_total + V_g.
- **Cross-talk** stays a separate block, reported beside C_resp and in no sum.

## 5. Checks

**The builder refuses, writing nothing, on any of these:**
- an output path that exists;
- the definition or fine map other than its digest (`s1_assemble.fine_map`);
- **the S1 assembly:**
  - a sha256 other than `db000707…`;
  - its stored U not bitwise equal to this definition's functional matrix (float32);
  - its C_total not bitwise C_e + C_model_abs;
  - f not 16 positive values;
- **any of the 11 products:**
  - missing;
  - a sha256 other than its pin;
  - provenance failing `check_meta`: config R, capacity None, 5 iterations, seed 42, estimators 100/8/42 × 3, and
    the refinement 400/31/45;
  - the pinned `input_npz_sha256` or `bkg_dump_sha256` not matching;
  - construction other than `data`, or truth other than `nominal`;
  - a bootstrap or jitter seed set;
  - coordinates not float32;
- `xsec_flat` not 65,856 finite values;
- a per-species block that is not the half-span outer product, or has rank > 1;
- **C_resp or C_total_resp:**
  - not symmetric to 10⁻¹² of its largest entry;
  - not PSD: min eigenvalue < −10⁻¹² × max |diag|;
- C_resp of rank > 4;
- C_total_resp of rank ≠ 16 (relative cutoff 10⁻¹²).

**What it reports without gating:**
- per cell, the relative σ (√diag / f, with S1's f) of each species block, C_resp, C_total and C_total_resp, with
  their medians;
- each block's share of tr(C_total_resp / f fᵀ);
- the extreme eigenvalues and ranks;
- **descriptive, per species:** the curvature ratio ‖U x(+1) + U x(−1) − 2 U x(0)‖ / ‖U x(+1) − U x(−1)‖ on R00–R15.
  - This is MP-1's G3 form, on these cells.
  - It gates nothing. On the J cells, MP-1 read a curvature of this form as estimator discreteness at rounding
    scale, not hadronic nonlinearity (`S1-REPORT.md`, "Input-jitter study").

**What the readout JSON holds:**
- relative quantities, spectra and ranks only;
- its labels: the component label, what is not varied, the cross-talk rule and the curvature rule.

The absolute matrices are in the npz.

## 6. Code, tests and the run

### 6.1 Code

- **Code commit:** `973142a7fc150f2ceb9fd3530297ec1ddcbd0dc3` (branch `assigned/cresp-spec-20261025`).
- **Builder:** `nd-unfolding/build_cresp.py`, sha256 `fe1aec8b74ab59e5ffa3bc824c4284065c5e8e97b2ce3c2e4bd1a34bec192f22`.
- **Tests:** `nd-unfolding/tests/test_build_cresp.py`, sha256
  `ea0dd6dbdeb9f12f6434bb17f1596e1fc4b5a6846b4d04908711a7dd6a9000d1`. All 22 run on synthetic products and a
  synthetic S1 assembly, and read no real file:
  - the half-span identity, equality with `s1_assemble.mat_cov`, offset cancellation and endpoint order;
  - the curvature ratio on a linear and a quadratic response;
  - the PSD, symmetry and rank functions, each firing and each staying silent;
  - an end-to-end build recomputed by hand: every block, C_resp without cross-talk, C_total_resp, the JSON's
    relative σ, ranks, trace shares and pins;
  - that the readout carries no absolute f or diag(C_total) value;
  - each refusal, checked by its message: overwrite, product digest, missing product, a jittered product, another
    estimator, another dump, non-finite values, another S1 assembly, S1's U on other cells, an S1 total that is not
    its sum, and a singular total;
  - the module as invoked with `-I -B` from a cwd outside `nd-unfolding`, through a wrapper that sets only the pins,
    including the no-overwrite refusal.
- **Code it imports, unchanged:**
  - `nd-unfolding/s1_assemble.py`, `b157250a…`, the file the S1 assembly ran: `fine_map`, `functional_matrix`,
    `mat_cov`, `check_meta`, `require_sha`, `sha256`, `xs`;
  - `nd-unfolding/s5p_stage1_inspect.py`, `26569afc…`.

**A pre-binding test run, synthetic only:**
- **What ran:** a clone at `973142a7` in `$P/cresp-testcheck-20261025/repo`, on login37 at 2026-10-26T02:20Z, with
  `root_6_28`, `-B` and `TMPDIR` on pscratch.
- **Result:** `test_build_cresp` and `test_s1_assemble` ran 40 tests, OK. `git status --porcelain --ignored` printed
  0 lines afterwards.
- **Receipt:** [`receipts-prebinding/cluster-tests-973142a7.txt`](receipts-prebinding/cluster-tests-973142a7.txt).
  - Its last JSON line is `test_s1_assemble`'s synthetic end-to-end output, not a real product.
  - The receipts are listed in [`receipts-prebinding/SHA256SUMS`](receipts-prebinding/SHA256SUMS).

### 6.2 The run, once, after the binding

```
P=/pscratch/sd/j/josephrb; R=$P/cresp-20261026
test ! -e $R
git clone --filter=blob:none https://github.com/josephbaileyy/MINERvA-OmniFold $R/repo
git -C $R/repo checkout --detach 973142a7fc150f2ceb9fd3530297ec1ddcbd0dc3
test "$(git -C $R/repo rev-parse HEAD)" = 973142a7fc150f2ceb9fd3530297ec1ddcbd0dc3
test -z "$(git -C $R/repo status --porcelain --ignored)"
mkdir $R/out $R/tmp
cd $R/repo/nd-unfolding/tests
TMPDIR=$R/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest test_build_cresp test_s1_assemble
cd $R/out
TMPDIR=$R/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B $R/repo/nd-unfolding/build_cresp.py \
    --definition $R/repo/nd-unfolding/pv-ladder/readouts/h2_definition.json \
    --products-dir $P/measurement-paper/phase1/mp1/s1/unf \
    --s1-assembly $P/s1-20261024/s1_assembly.npz \
    --out $R/out/cresp.npz
test -z "$(git -C $R/repo status --porcelain --ignored)"
```

**Once means once:**
- On a test failure or a refusal, nothing is retried, and I report to the director.
- **On success:**
  - `cresp.json` is committed at `state/measurement-scoping/assigned-uncertainties/cresp/cresp.json`, with a short
    report;
  - `cresp.npz` stays on pscratch, named by its sha256;
  - Stage G's binding then names that digest for its sensitivity variant.

**Cost and storage:**
- **Compute: 0 node-h.** This is numpy on 11 files of about 95 KB plus the 119 KB S1 assembly, in seconds. No Slurm
  job runs.
- **Storage:** under 1 MB on pscratch; nothing on CFS.

## 7. What C_resp covers, and what it does not

**Covers:**
- the response of configuration (e)'s 5D result on R00–R15, as unfolded from the data, to a ±1σ scale of the
  simulation's reconstructed recoil energy;
- separately for the proton, meson, EM and other deposits, at D1's sizes, with cross-talk beside it.

**Does not cover:**
- **The joint tests.** Their null distributions are not varied. That is MP1-A-full, priced at about 230–320 CPU
  node-h (`S1-REPORT.md`, "MP1-A-full, priced"), and it is not proposed here.
- **Neutron and muon deposits**, the effects of particle species, energy dependence and resolution beyond a scale, and
  a response difference applied before calibration (item (b) of `docs/analysis-note/sec_joint.tex:684-689`, for the ±4 % study).
- **Configuration (a)'s products:** the (E_avail, W) map, z-cv and Fig. 3(b)'s band.
- **The 3D and 4D central values,** and the 2D result.
  - **For 2D, the block would be zero by construction (inference from code).** The 2D unfold reads only reconstructed
    p_T and p_∥ (`2d-unfolding/unfold_2d_omnifold_unbinned.py:9`).
  - The selection reads no recoil (MP-1 `S1-REPORT.md`, "How rows that fail selection are handled").
  - No run has tested this.
- **The estimator's discreteness.** MP-1 measured a rounding-scale response of the same size as the em and other G3
  curvature on the J cells, and the products are single, unjittered unfolds.
  - So each half-span carries that noise.
  - MP-1's median per-cell relative SD of f₀ under jitter is 0.21 % on the J cells (S1-REPORT, "Input-jitter
    study").
  - The R00–R15 curvature ratio reported here shows its size on these cells. It is descriptive only.

## 8. How it enters Stage G (the director's ruling, 2026-10-25, by correspondence)

**How Stage G would report it:** a declared sensitivity variant, beside its declared comparison. Each χ² would be
reported on M = C_total + V_g and on M = C_total_resp + V_g.

**The order:** binding, then the build, then the readout committed, then Stage G's binding naming `cresp.npz`'s
digest, then Stage G runs. C_resp is therefore fixed before any data-against-generator χ² exists on these cells.

**Whether C_resp joins the reported total** is Joseph's decision, made from U-PLAN. Until then it is labelled a
sensitivity variant everywhere it appears.
