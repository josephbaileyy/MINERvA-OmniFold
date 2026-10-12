# Final independent numerical verification of the xr-linux XR runs at aa6b173d (review use 2)

Preserved verbatim: the reviewer's final message, as returned to the owner on 2026-10-12 (UTC). Nothing below is edited.

---

**Verdict: VERIFIED WITH FINDINGS.** Every number, verdict, digest, receipt property and charge in §1, §6, §7 and §9 reproduces from scheduler and file operands. The findings are NOTEs only: none changes a verdict, a number beyond its last printed digit, or a claim's scope.

**Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), a general-purpose subagent. This is review use 2 of 2, the final numerical verification, read-only. I am the same provider and model as the owner, so this is not a cross-provider review. I also did the admission review of `60bd68c0`, delivered earlier.
**Fixed commit:** `aa6b173ddf3a917857ef27ce03236dc112a0528f` on `run/xr-linux-20261010`, fetched from origin.
**UTC:** start 2026-10-12T06:16:56Z, end 2026-10-12T06:21:36Z.
**Worktree:** a fresh detached `.../scratchpad/verify-wt`. `git status --porcelain --ignored | wc -l` was 0 at the start and 0 at the end. I did not touch the main checkout's working tree or the owner's worktrees.

**What I ran:**
- **Local:** my own scripts `verify-scratch/check_receipts.py`, `verify_cmp.py` (sha256 `1dcb8e29…`) and `charges.py`, about 0.01 core-hours on one thread. I read, but did not use, `xr_compare.py` and `checks/reproduce_comparisons.py`.
- **Cluster (login23, read-only):**
  - `sha256sum` of the outputs, their CFS copies, the receipts, the references, `admission.json`, `submissions.jsonl` and the preflight receipt;
  - live `sacct` and `squeue`;
  - `verify_cmp.py` under the admission's setup (`setup_salloc_env.sh`) on a `/tmp` copy of `runs.json` (`4a54b025…`) and `references.json` (`af7d5a19…`), which I removed afterwards;
  - one probe that printed the global numpy RNG state.
- Nothing trained, no job submitted, nothing edited.

## Findings

| id | severity | location | what | consequence |
|---|---|---|---|---|
| N-1 | NOTE | REPORT §1 table, integral column | §1 gives the frozen comparator's plain-sum integrals. My correctly rounded sum (`math.fsum`) gives slightly different last digits:<br>• X0_vs_E_C: report 2.2e-16, mine 0.<br>• X0p_vs_E_C: report 0, mine 2.2e-16.<br>• L0_vs_PN_CV: report 1.4e-14 (1.354e-14), mine 1.321e-14.<br>• L1_vs_SEED1: report 4.2e-14 (4.163e-14), mine 4.130e-14.<br>Mine equal `reproduction-final.json` exactly, and differ from `comparisons-final.json` by at most 3.3e-16 absolute. §7 already says the two sets agree "to ≤ 1e-15 absolute (summation order)". | None for any verdict: all are at least 5 orders of magnitude under 1e-8. Optional: footnote §1's integral column with "(comparator's summation)". |
| N-2 | NOTE | REPORT §1 bullet on the one-seed question, "Its mechanism was not examined: the run path sets no global numpy seed" | I measured this. In the frozen environment, after the setup and after importing ROOT, sklearn, lightgbm, joblib, threadpoolctl and scipy, two processes had different global numpy RNG states (`fa5dc5ca…` and `6567034e…`). Importing these did not change the state. `check_random_state(None)` is the global singleton, and its first `randint` differed (802075050 vs 1572971894). The driver and helper use `--seed` only to set `random_state`. The `refine_params` use applies only in `negweight-refined` background mode, which these runs did not use. | This supports the sentence. It also sharpens the open question: the X0, X0p and E_C agreement cannot come from a shared global seed. This is evidence for the 2D estimator owner, not a defect, and no wording change is required. |
| N-3 | NOTE | REPORT §6 table, L1 "submitted 08:41:34" | sacct's Submit for L1 is 01:41:33 PDT (08:41:33Z); `submissions.jsonl` says 08:41:34Z. The record is written after `sbatch` returns. The other times in the table equal sacct, converted from PDT. | None. |

## 1. Comparisons, recomputed from `hXSec2D`

**Inputs verified:**
- All five outputs match their receipts' sha256, and their CFS copies match byte for byte: X0 `68a0de2d…`, X0p `3449de34…`, X1 `11ff7744…`, L0 `75138024…`, L1 `e472fa62…`.
- The five cluster receipts have the same sha256 as the tracked copies under `results/outroot/` (`cd3dcb1e…`, `dd7a94a6…`, `f22c59cd…`, `a6e62d04…`, `c2b2b237…`). So do `submissions.jsonl` (`6a43c4c4…`) and the preflight receipt (`50907f29…`).
- All four references match `references.json`: E_C `142a45b0…`, CV42 `4f5a1b6d…`, PN_CV `b8457af7…`, SEED1 `d7fe901f…`.

**Method:** cells with GlobalID = i×16 + j (0-based) and value > 0. In every product and every comparison, that set equals E_C's frozen 205 cells, and the axes are equal. "Max" is max |new/ref − 1|; I also computed it in exact rational arithmetic and got the same values.

| comparison | verdict | max | argmax cell | median | integral (fsum) | cells over 1e-8 | bitwise-equal cells |
|---|---|---|---|---|---|---|---|
| X0_vs_E_C | PASS | 3.886e-15 | 0 | 5.551e-16 | 0 | 0 | 32 |
| X0p_vs_E_C | PASS | 7.105e-15 | 180 | 4.441e-16 | 2.220e-16 | 0 | 29 |
| **X1_vs_X0** | **FAIL** | **1.618e-02** | **111** | **1.775e-03** | **3.983e-06** | **205** | 0 |
| L0_vs_CV42 | PASS | 1.375e-11 | 171 | 5.885e-12 | 7.019e-13 | 0 | 0 |
| L0_vs_PN_CV | PASS | 9.812e-13 | 15 | 2.176e-14 | 1.321e-14 | 0 | 0 |
| L1_vs_SEED1 | PASS | 2.415e-12 | 159 | 6.251e-14 | 4.130e-14 | 0 | 0 |
| NC_X0_vs_CV42 | FAIL, so the control is met | 1.387e-01 | 159 | 9.928e-03 | 9.440e-05 | 205 | 0 |

**Agreement with the owner's files:**
- Every maximum and median equals both `comparisons-final.json` (`e43bf8f1…`) and `reproduction-final.json` (`50dc9561…`) exactly.
- So do every argmax cell, every count of cells over 1e-8 and every bitwise-equal count.
- Integrals: see N-1.

**X1_vs_X0, the consequential FAIL:**
- Confirmed: max 1.618 % at cell 111, median 0.18 %, integral 4.0e-6, and all 205 cells exceed 1e-8.
- The top ten cells are 111, 127, 5, 17, 18, 15, 1, 223, 4 and 6, at 1.6178 %, 1.4460 %, 1.3417 %, 1.2435 %, 1.2156 %, 1.1271 %, 1.1149 %, 1.0765 %, 1.0474 % and 0.9322 %. This matches §7.

## 2. Receipts (tracked copies, byte-equal to the cluster)

**All five runs:**
- `status: complete`, exit 0, `launches: []`, strict identity.
- Deployed commit `92386d3f`. Its package, driver, helper and guard are identical to `60bd68c0` (`git diff` is empty).
- 10 classifier and 5 regressor fits, with the frozen classes and seeds in order:
  - X0 and X0p: `GradientBoosting*` with seed None;
  - X1: 1, 2, 1, 2, … for the classifiers and 3 for the regressor;
  - L0: `LGBM*` with 42/43 and 44;
  - L1: `LGBM*` with 1/2 and 3.
- 205 reported cells each. The environment check passed: Python 3.11.14, ROOT 6.28/12, and package versions equal to `runs.json`.

**LightGBM runs (L0, L1):**
- num_threads 64 at all 15 fits, and 15 predict calls all at 64.
- Affinity 64 of 256; joblib's physical count 64; `OMP_NUM_THREADS` 64.

**Drivers:**
- X0, X1, L0 and L1 executed the driver with sha256 `3cc5adc7…`.
- X0p executed `unfold_2d_omnifold_unbinned_d1bc8813.py.record` at sha256 `447288e2…`.
- Each matches `runs.json`'s `driver_digest`.

**Guard inventories:** the preflight and all five runs read `REPOSITORY-ORIGINS-INSPECTED`, with no violation, 0 modules outside the expected root, and the guard installed.

**Preflight receipt:** this confirms §5.
- `preflight-pass`, `launches: []`, wall time 104.2 s;
- affinity 12 of 256, joblib 12;
- all six fixture checks true;
- L0 repeat bitwise equal in 176 of 176 cells (max 0);
- X0 vs L0 FAIL at 0.725;
- all four refusal and launch controls met, and both job controls met.

## 3. Charges, from live sacct (06:19:53Z)

Charged node-h = ElapsedRaw/3600 × billing/256.

| group | jobs | CPU-s (ElapsedRaw × billing) | node-h |
|---|---|---|---|
| prior (5 `xr_*`, 1 `xrr_*`) | 6 | 2,132 | 0.0023134 |
| `xrl_PF_a1` 59659845 | 1 | 147 × 12 = 1,764 | 0.0019141 |
| `xrl_L0` 59660487 + `xrl_L1` 59664203 | 2 | (836 + 909) × 64 = 111,680 | 0.1211806 |
| `xrl_X0`/`X0p`/`X1` 59664200–02 | 3 | (75,296 + 76,470 + 75,999) × 12 = 2,733,180 | 2.9656901 |
| **cumulative** | 12 | **2,848,756** | **3.0910981 (exactly 712189/230400) of 6.4** |

- This matches REPORT §9 and `ledger-final.json` to every digit: cumulative 3.091098090277778, `over: []`.
- The prior part is exactly 533/230400 = 0.0023133680555….
- The headroom left under the cap is 3.3089 node-h.
- Attempts used: preflight 1 of 2, exact 3 of 4, LightGBM 2 of 3.
- All six `xrl` jobs are COMPLETED 0:0. `squeue` is empty.
- Every `xrl` Submit, Start and End falls inside the window from 2026-10-11T06:13:23Z (the preflight's Submit, 23:13:23 PDT) to 2026-10-14T06:13:23Z. The last end is X0p's, at 2026-10-12T06:12:33Z.
- The exact runs took 20.92, 21.24 and 21.11 h, which matches "20.9–21.2 h".

## 4. Report wording

- **§1 and §7 stay within the numbers.**
  - "Central reproduction PASS": the maxima are at most 7.1e-15, with 29–32 bitwise-equal cells.
  - "≤ 1.4e-11 … inside the 5.8e-9 prior": the largest L-arm maximum is 1.375e-11.
  - "One-seed FAIL … every one of the 205 cells … median 0.18 %, max 1.6 %": confirmed.
- **The X1 interpretation is adequately scoped.**
  - "Not invariant to the estimator seed at the frozen criterion" is supported: one counterexample refutes invariance.
  - The report explicitly disclaims a seed-spread estimate, a mechanism and any gate change.
  - It routes the open question to the 2D estimator owner (§1, §10 item 6, §11). N-2 adds evidence for that open question.
- **NOT CITABLE FOR is respected.** No cross section, uncertainty, re-quote, adoption, gate change or general seed-invariance claim appears in §1, §7 or §10. The proposed CATALOG row (§10 item 2) restates only verified numbers.
- §1's "independently reproduced … by the final numerical verification (§8)" will be accurate once this report is placed in §8, which is still a placeholder.

## What I could not verify

- **How the outputs were produced inside the jobs:** the training itself, and the in-job input re-hashes, which the receipts store as stat fields plus a checked digest. I checked outputs and receipts after the fact, not the jobs' execution.
- **The mechanism behind X1_vs_X0,** beyond N-2: why unseeded runs with different global RNG states agree to 1e-15 while seeds 1/2/3 move every cell.
- **Values from earlier or other runs:** the 5.8e-9 thread prior and the earlier products' provenance. I took these from the frozen record, not re-derived them.
- **Local resource figures** in §9 (active hours, local core-hours), which are self-reported.
