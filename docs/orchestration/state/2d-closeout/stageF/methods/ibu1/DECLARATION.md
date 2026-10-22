# Declaration: IBU-1, a binned iterative-unfolding baseline under matched conditions (2026-10-22)

**By** the validation lane, under [`../IBU1-SPEC.md`](../IBU1-SPEC.md) (frozen 2026-10-21) and the lane brief
([`../../lanes/VALIDATION-LANE-BRIEF.md`](../../lanes/VALIDATION-LANE-BRIEF.md)). **Written** 2026-10-22, before any
IBU-1 job was submitted and before IBU was run on any analysis input. **Status:** awaiting the director's binding. A
run started before binding is held and not used.

**CITABLE FOR:** what will be run, on which pseudo-experiments, against which OmniFold products, the amendments to
the spec (IA-1 to IA-14), and the readout and reading rule, fixed before any result.

**NOT CITABLE FOR:** any result.

**Spec amendments.** The director agreed IA-1 to IA-6 and IA-10 (message of 2026-10-22). It added IA-9, the
small-n rule in IA-10, and the retention of the K scan and the data comparison (IA-11).

The admission review (§9) then changed one agreed item. At n = 60 and n = 20 the below-gate count can never resolve,
so below n = 400 **the count is descriptive and the residual decides** (IA-10). **This needs the director's binding
explicitly.** The review also added IA-14. Each amendment is coded where its tag appears in `nd-unfolding/ibu1/`.

## 1. The question (spec §1, unchanged)

Does a conventional binned IBU (D'Agostini), on the same simulation, background treatment, pseudo-data, cells and
iteration count, show the residual bias and miscoverage that our OmniFold configurations show? If it does, the
failures belong to the inverse problem at this binning and prior. If it does not, they are specific to the OmniFold
implementation.

## 2. What exists to compare against (measured from the records, 2026-10-22)

OmniFold has a 400-seed coverage result under the amendment-4 correction **only at nominal and at the ~10% rate
change**: s5c Tier S, configuration (c), purity background (`state/s5c/tier_s/interim_400.json`, `aa574c17…`).

At the other truths only small ensembles exist, with negative-weight background and uncorrected f̂ ± σ intervals:
- **GiBUU:** the s5n development grid, configuration (d), seeds 301000–301059, n = 60
  (`state/s5n/stage1/dev_receipt.json`, `1ef4096c…`, grid `C4_eavail_shape`).
- **W1–W3:** the s5e candidate-R assessment, configuration (e), 20 seeds each (`state/s5e/cand/assess_receipt.json`,
  `84266e30…`, points `W1`–`W3`).

The spec's "at least 400 per truth" and "matched conditions" cannot both hold at GiBUU and W1–W3. IA-1 and IA-2
resolve this by pairing with what exists and saying so.

## 3. Amendments to the spec

| tag | the spec says / leaves open | fixed here | why |
|---|---|---|---|
| IA-1 | two background treatments: purity, and "a nominal background expectation" | **Two arms, each matching an existing comparator's construction.** **P** (purity): IBU on the s5c Tier-S pseudo-experiments, rebuilt by `s5c_pseudo.build_experiment`. **N** (nominal background expectation = the negative-weight template): IBU on the s5n/s5e pseudo-experiments, rebuilt by `s5n_pseudo.build_pseudo`, with `ratio_nd` installed by `s5e_deform.install_ratio_truth` exactly as `s5e_candidate.install` does | the like-for-like comparison is only possible on the pseudo-data the OmniFold numbers were measured on |
| IA-2 | seeds "the OmniFold studies used where recorded"; ≥ 400 per truth | the comparator's seeds and split keys (`split_key_for(seed)`, the batch-mode derivation; d1 as explicit pairs). Where a comparator has fewer than 400, the IBU ensemble extends the same range to 400 (§4). The **paired** subset carries the rule; the extension gives IBU's own 400-seed numbers (IA-12) | pairing makes IBU and OmniFold see identical Poisson draws and halves |
| IA-3 | — | **Pairing gate, per experiment.** The OmniFold product must carry this experiment's truth bitwise (`xtrue_flat`), its seed, its split key and an identical experiment record (signal and background event counts, expected sums, half sizes; JSON-equal). It must also carry the declared construction flags: truth, amplitude, input and background digests, and for arm N `bkg_mode` and the ratio digest. Where the product's schema records them, it must also carry `no_background` false, `prior_matches_truth` false, `iters` 5, `estimator_seed` 42, `permute_seed` none and `config` deterministic. A failed gate makes the experiment not a result | proves the pseudo-data are the comparator's, built as declared, not merely by the same code |
| IA-4 | "unfolding to the 109 J cells" | IBU on the J partition (`contract.json` `partition_J`, 3⁵ cells, empty cells dropped). The reco bins are the 65,856-cell 5D grid (`s5e_trace.flat_index`, D-ID's). The prior is the unfolding half's own truth. Each J estimate is spread over its fine cells by that half's truth shape (D-ID AM-4). It then passes through `xsec_nd.extract_cross_section_nd` with that half's completeness, exactly as `s5c_unfold.unfold` does, and through the 153 rows of `s5c_coverage.reported_functionals`. **Residual** of a functional = the mean over the ensemble of f̂/f_true − 1, raw (uncorrected). It is summarized by the median and maximum of its absolute value over the 109 J functionals | the spec's readout is per J cell. Raw residuals keep the estimator's bias separate from the correction |
| IA-5 | background "subtracted as in (a) and, separately, as a nominal background expectation" | Arm P **`pur`** (primary): the binned purity-weighted measured sample OmniFold received. **`fold`** (secondary): raw counts, with `bkg_nd` as a known term in the fold. Arm N **`fold`** (primary): observed counts, with the template (half D ×2) as a known term in the fold, the positivity-safe binned form of the signed sample. **`sub`** (secondary): max(0, observed − template) per reco cell | the primary variant of each arm is the comparator's own treatment. The secondaries are reported and carry no rule |
| IA-6 | "IBU intervals from the same ensemble's spread at nominal truth, with amendment 4's bias correction" | **σ:** IBU on the comparator's declared bootstrap: P at s5c's (nominal, seed 1, split 20260924; replicas 1–200; the replica is `s5c_pseudo.run_bootstrap`'s, proved by capture). For N it is s5n's (nominal 349999, replicas 1–200) for the GiBUU comparison and IBU's own coverage, and R's (nominal 700000, replicas 1–100) for W1–W3. Replicas come from `s5n_pseudo.bootstrap_replica`. **β, se:** P from IBU on the nine d1 experiments that made `bias_correction.json`. I identified those numerically as d1_split_s4–s11 plus p3_nominal_s1; they reproduce its β to 7e-18. N from IBU on s5n's nominal development seeds 300000–300059. **Interval per comparison:** amendment-4-corrected at nominal and tilt (as Tier S), uncorrected f̂ ± σ at GiBUU and W1–W3 (as their receipts) | each IBU interval is built the way its comparator's was. The ensemble-spread reading of the spec would make nominal coverage in-sample |
| IA-7 | — | reco rule: a reco row is in the window when it lies in [first, last) on every axis (`s5n_pseudo.fid_mask`; purity gives a row on an upper edge weight 0). It applies to the response and to every measured sample | both constructions exclude upper-edge rows on the measured side |
| IA-8 | — | truth-passing, reco-passing rows whose truth lies outside the grid (the −9999 sentinels) enter as a known additive term in the fold, from the unfolding half (D-ID AM-2) | they are in the pseudo-data and have no truth cell |
| IA-9 | "split-half where the matching OmniFold study is split-half" | **Response provenance, per arm, gated.** Every experiment is split-half: the response uses half A ×2, the rows and weights the comparator's unfold received. Bootstrap replicas use the replica's half-A weights, and the data use the full MC ×1. `half_from_experiment` refuses unless the experiment's unfolding arrays equal the full sample's half-A rows, with weights bitwise ×2. Together with IA-3 this proves the matrix was built from the same events and weights. A sample with any row failing `pass_truth` is refused; the pinned npz has none (D-ID §9.1) | director's item 1 |
| IA-10 | "count of quantities below the gate within a factor of 2" | **Count** = J functionals below a gate (68% at 0.66 or 95% at 0.94), with a one-sided Clopper–Pearson bound at 0.05/459, the Tier-S per-comparison level. `definite` = the upper bound is below a gate, which equals the Tier-S futility count at n = 400 (tested). `possible` = the lower bound is below a gate. The count is `definite`, its interval [`definite`, `possible`], and the point count is reported beside it. **Relations:** "within a factor 2" if max ≤ 2·min, or both ≤ 2; otherwise "better" or "worse". **Resolved** only if all four corners of the two intervals give the same relation. The residual ratio IBU/OmniFold gets a paired seed-bootstrap 95% interval (2,000 resamples, seed 20261022). It is resolved only if both ends fall in the same relation region (< ½, ½–2, > 2). **Small n (admission repair):** at n = 20 and 60, a functional covered in every experiment still has a CP lower bound at 0.05/459 (0.634, 0.859) below a gate (0.66, 0.94). So `possible` is all 109 at any coverage, and the count can never resolve. **Below n = 400 the count is reported with its interval and is descriptive; the residual decides.** At n = 400 (the rate change) both metrics decide | director's item 2: no reading may rest on a count whose interval spans the factor-2 boundary. At n < 400 the count always spans it, so no reading rests on it |
| IA-11 | data unfold at K = 5 compared with (a) and (e) | IBU on the real data, full MC ×1. Arm P: the npz's stored purity weights, against (a) `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` `hXSecND_flat` (`630306e2…`). Arm N: `s5n_pseudo.build_data`, against (e) `s5p-20260926/runs/s2/num/data/data_b-_j-.npz` (`fb5cc679…`). Reported per J cell as IBU/(a) and IBU/(e). Descriptive; no rule | kept from the spec |
| IA-12 | — | IBU's own amendment-4-corrected coverage at 400 seeds for arm N (nominal at 300060–300459, GiBUU, W1, W2, W3), with σ from s5n's bootstrap and β from 300000–300059. W1–W3 also use s5n's σ here, not R's: arm N's pseudo-data construction is the same for both, and s5n's bootstrap has 200 replicas against R's 100. Reported, no OmniFold comparator, no rule | what the spec's 400-per-truth asks of IBU, where OmniFold has no 400 |
| IA-14 | — | **Oracle floor, per experiment.** The exact departed J totals of the unfolding half pass through the same spreading and extraction as an IBU estimate. They are compared with the half's departed truth in `build_experiment`'s x_true spelling (reweighted counts over unreweighted completeness). The median and maximum \|oracle/truth − 1\| over J is reported per truth beside the residuals. Descriptive, no rule | the J-cell estimator has a floor it cannot remove at any K or n when a departure varies inside a J cell and the completeness varies across its fine cells (review finding 3: up to 1.5% in a probe) |
| IA-13 | — | **Preconditions** (else the verdict is INCOMPLETE): (i) every paired experiment passes IA-3 and IA-9; (ii) every bootstrap's base experiment passes IA-3 and the replica capture passes; (iii) every truth uses all 109 J functionals; (iv) the paired OmniFold estimates reproduce their receipts, meaning hits equal to `interim_400` exactly under its σ and β, and mean residuals equal to the s5n and R receipts to 1e-12 | the population IBU is compared against must be the one the receipts describe |

The K scan is unchanged from the spec: K ∈ {1, 2, 3, 4, 5, 10, 20} is reported, K = 5 is primary, and σ and β are
recomputed at each K.

## 4. Code, inputs and units

**Code** (commit `127dc266`, branch `validation/ibu1-declaration-20261022`; first written at `c770cd29`, then
repaired in `d6cb822c` and `127dc266` after admission review, §9), under `nd-unfolding/ibu1/`. The review saw these
commits as `56d546ef`, `2687b388` and `8b21b91b`, before a rebase onto main `bb35803b`; the file digests below are
unchanged by it, and the rebase added only `nd-unfolding/re1/` files.

| file | sha256 (first 16) | role |
|---|---|---|
| `ibu1.py` | `f862a953425c006f` | driver: the units below |
| `ibu1_read.py` | `2214d4877d0351fa` | readout and reading rule (§5) |
| `config.json` | `82a24f419d4e738d` | every pin, seed, unit and comparator path |
| `test_ibu1.py` | `1af9889230c2ebf4` | 35 synthetic controls (all pass) |
| `make_tasks.py`, `tasks.tsv` | `aeae8d937b896acb`, `2bf49ffbfa863baa` | the 124 task lines (the table equals the generator's output, tested) |
| `sbatch_ibu1.sh` | `52687487c4750ad6` | launcher: concurrent srun steps, each through `mnv_guarded_run.py` (OI-136) from a clean deploy at the pin |

**Producers, imported unchanged** and digest-pinned in `config.json` `code_sha256`, checked before import:
`s5c_pseudo.py` `d81d4f46…`, `s5n_pseudo.py` `8981f97b…`, `s5e_deform.py` `6726ff99…`, `s5c_unfold.py` `510d749a…`,
`xsec_nd.py` `454001f3…`, `s5e_trace.py` `c47e9dd3…`, `s5c_coverage.py` `e47f0d8f…`, and D-ID's `did.py` `d918c816…`.

These are main's bytes, and they match the products' recorded code. Every s5e/s5p deploy that made the R products
carries `s5n_pseudo` `8981f97b` and `s5c_pseudo` `d81d4f46` (measured on Perlmutter 2026-10-22). The s5n dev deploys
carry `s5n_pseudo` `ec5ac3ed`, whose `build_pseudo` differs only by the unused `prior_matches_truth` flag. The Tier-S
deploy 4bdfa75e carries `s5c_pseudo` `e423aaae`, which differs from main only in the `q3_given_eavail_w` branch of
`truth_weight`, unused here. IA-3 checks the equivalence per experiment.

**Inputs** (each checked by sha256 at load):
- `of_inputs_5d.npz` `07fccc1a…`;
- `runs/p2/bkg_dump.npz` `2addac8f…`;
- `contract.json` `d54fd7c9…`;
- the ratio files: GiBUU `45cc3e0a…`, W1 `2a208df9…`, W2 `80e16f95…`, W3 `3455daf3…`;
- the receipts `interim_400.json` `aa574c17…`, `bias_correction.json` `6c49c66c…`, `dev_receipt.json` `1ef4096c…`
  and `assess_receipt.json` `84266e30…`;
- the data comparators in IA-11.

The comparator products are read where they lie on `$PSCRATCH` (paths in `config.json`), and each read's sha256 is
recorded in the product's meta.

**Units** (`config.json` `units`):

| unit | arm | truth | seeds (n) | paired OmniFold comparator | role |
|---|---|---|---|---|---|
| `P_nominal` | P | nominal | 200000–200399 (400) | s5c `s_valid` (400) | reference |
| `P_tilt` | P | `eavail_tilt` a = 0.2 (the ~10% rate change, KI 98) | 204000–204399 (400) | s5c `s_valid` (400) | **rule** |
| `P_d1` | P | nominal | (1, 20260924), (4–11, 1004–1011) (9) | d1/p3 products | β, se |
| `P_sigma` | P | nominal | seed 1 / 20260924, replicas 1–200 | `s_sigma/boot_b1` (base) | σ |
| `N_nominal_dev` | N | nominal | 300000–300059 (60) | s5n dev (60) | β, se (N); reference |
| `N_nominal_val` | N | nominal | 300060–300459 (400) | — | IA-12 |
| `N_gibuu` | N | `eavail_shape` a = 1, GiBUU | 301000–301399 (400) | s5n dev, first 60 | **rule** (paired 60); IA-12 (400) |
| `N_gibuu_R` | N | GiBUU | 801000–801019 (20) | R `eavail_gibuu` (20) | reference |
| `N_nominal_R` | N | nominal | 800000–800039 (40) | R `nominal` (40) | reference |
| `N_w1` | N | `eavail_shape` a = 1, W1 | 803000–803399 (400) | R `W1`, first 20 | **rule** (paired 20); IA-12 |
| `N_w2` | N | `ratio_nd` a = 1, W2 | 804000–804399 (400) | R `W2`, first 20 | **rule** (paired 20); IA-12 |
| `N_w3` | N | `ratio_nd` a = 1, W3 | 805000–805399 (400) | R `W3`, first 20 | **rule** (paired 20); IA-12 |
| `N_sigma_s5n` | N | nominal | 349999, replicas 1–200 | s5n `sigma/boot_b1` (base) | σ (GiBUU, IA-12) |
| `N_sigma_R` | N | nominal | 700000, replicas 1–100 | R `dev/sigma/boot_b1` (base) | σ (W1–W3) |
| `D_P`, `D_N` | P, N | data | — | (a), (e) | IA-11 |

That is 2,932 pseudo-experiment builds, 500 bootstrap replicas and 2 data unfolds, each at 7 iterations × 2
variants.

## 5. Readout and reading rule (fixed now; it may not change after any result)

**Per deformed truth** (tilt, GiBUU, W1, W2, W3), at K = 5, on the primary variant and the paired seeds:
- the residual median and maximum over the 109 J functionals, IBU and OmniFold, and the ratio with its interval
  (IA-4, IA-10);
- the counts and their intervals, IBU and OmniFold (IA-10). OmniFold's hits come from the receipts: `interim_400`
  for tilt, `dev_receipt` `C4_eavail_shape` for GiBUU, and `assess_receipt` `W1`–`W3`.

**Per-truth reading.** It uses both metrics at n = 400 (the rate change, coded `tilt`: `eavail_tilt` a = 0.2, KI 98),
and the residual alone at n < 400 (IA-10):
- **consistent:** within a factor 2;
- **IBU better:** better by more than a factor 2;
- **IBU worse:** worse by more than a factor 2;
- **mixed:** the two metrics disagree (n = 400 only).

Each truth carries the set of readings its unresolved ranges allow. The residual contributes its ratio interval and
the count its four corners. The reading is the point word if that set holds only it. Otherwise it is "unresolved",
with the point word beside it.

**Verdict:**
- **Inverse-problem limited** if every deformed truth is consistent.
- **Implementation specific** if IBU is better at both GiBUU and the rate change. "Both metrics" is the conservative
  reading of "better by more than a factor of 2" (director, agreed).
These two are decided on the sets: every truth's set must be {consistent}, or the GiBUU and rate-change sets must be
{IBU better}.
- **Unresolved** if neither is decided but one is still in the sets.
- **Mixed** otherwise, which is decided even when some truths are unresolved.
- **INCOMPLETE** if a precondition (IA-13) fails.

The verdict is descriptive, for the methods paper. It authorizes nothing.

**Reported, no rule:**
- the same readout at the references: nominal (P), nominal (N, s5n and R) and GiBUU under (e);
- every K in the scan;
- the secondary variants at K = 5;
- IBU's own corrected 400-seed coverage (IA-12);
- the data ratios (IA-11).

These branches were exercised on constructed numbers before this declaration (`test_ibu1.py` `Rule`): all
consistent → inverse-problem limited; better at tilt and GiBUU → implementation specific; one truth worse → mixed; an
interval spanning the boundary → unresolved; tilt resolved worse with an unresolved count → mixed (not unresolved); a
fully covered n = 60 count → descriptive, residual decides.

## 6. Compute (grant: ≤ 10 CPU node-h on m3246, spec §4)

- **Deploy:** a clean checkout of the bound commit at `/pscratch/sd/j/josephrb/ibu1-20261022/deploy/<sha>`. The
  launcher refuses a dirty tree or a different HEAD. Every task runs under `mnv_guarded_run.py --expect-root <deploy>`.
- **Job A (smoke, debug QOS):** 1 node, time limit 30 min, task lines 0–2 (`P_d1`, `D_P`, `D_N`). It measures seconds
  per build, seconds per IBU variant and peak RSS (sacct MaxRSS per step). **Cap 0.5 node-h.**
- **Jobs B1 and B2 (regular QOS):** 1 node each, lines 3–63 and 64–123, steps of 2 CPUs and 10 GB. If job A's peak
  RSS exceeds 8 GB, the step memory becomes 1.25 × that peak. The time limit is 1.25 × the wall projected from job A
  (tasks × measured seconds ÷ steps per node), at most 1 h 30 min each. **Cap 3.0 node-h.** Expected about
  1 node-h in all, from about 20 s per build, measured at 17–19 s in the Tier-S products' `seconds_build`.
- **Worst case 3.5 CPU node-h** against the 10 granted. Never premium; every job under 12 h.
- **Failures.** A failed task or a failed gate is never a result. The failed lines may run once more in one job if
  the charge so far plus that job's limit stays within 10 node-h. Otherwise the verdict is INCOMPLETE. A job beyond
  1.25 × its projected wall is stopped and reported.
- **Storage:** `/pscratch/sd/j/josephrb/ibu1-20261022/run/` (products, logs, inventory, tmp), about 100 MB. Nothing
  goes to CFS.
- **Ledger:** every job in `LEDGER.tsv` here, with job id, QOS, elapsed and charge (ElapsedRaw × billing/256/3600
  from sacct).
- **Evidence committed with the report:** the products' SHA256SUMS, the `ibu1_read.py` output, the consolidated K = 5
  functional tables (≤ 10 MiB), sacct and the guard inventories.

## 7. Order after binding

1. Deploy the bound commit; submit job A.
2. When A is terminal, check sacct, the task logs and the gates; set the B limits by §6; submit B1 and B2.
3. When both are terminal, check sacct, the logs, every gate and the controls. Copy the products locally and run
   `ibu1_read.py`.
4. Have an independent read-only reviewer check the result in both directions (nothing lost, nothing strengthened).
5. Commit the receipts, `LEDGER.tsv` and `REPORT.md` here; open a PR and message the director. This lane does not
   merge.

## 8. Not tested

- Total (statistical plus systematic) coverage; nuisance settings away from nominal.
- The q3-conditional point, which is a recorded construction defect (s5c OUTCOME §3).
- OmniFold at 400 seeds for GiBUU and W1–W3: no such products exist, and producing them is not IBU-1's scope.
- Unbinned or prior-free IBU variants, other truth grids (T2/T3), and other K than the scan.
- Any statement about real data beyond the descriptive ratios of IA-11.

## 9. Admission review

One fresh Claude Opus 5.5 subagent reviewed the code read-only in a detached worktree: the same model family, so not
cross-provider independent.
- **At `56d546ef`: ADMIT-WITH-REPAIRS.** It verified the extraction, response, reco window, both background
  variants, the P replica capture, the pairing values, the guard usage and the task coverage against the producers,
  and found 2 MATERIAL and 6 MINOR defects.
- **Focused re-review at `2687b388`:** F1–F8 closed, one NEW defect.
- **At `8b21b91b`: ADMIT.**

| # | severity | finding | disposition |
|---|---|---|---|
| F1 | MATERIAL | the reader indexed the K axis by position, so the secondary variants were read at K = 1 and labelled K = 5 | **fixed** (`2687b388`): indexed by value everywhere; a test with K-dependent F |
| F2 | MATERIAL | at n = 20 and 60 the count can never resolve (CP lower bound at full coverage below a gate), so "implementation specific" was unreachable | **fixed** (IA-10): below n = 400 the count is descriptive and the residual decides; test at n = 60 and 400 |
| F3 | MINOR | spreading J estimates over fine cells leaves an unmeasured floor under within-cell departures with varying completeness | **fixed** (IA-14): per-experiment oracle reported per truth; the synthetic completeness now varies, and a control fires |
| F4 | MINOR | the verdict returned "unresolved" where "mixed" was already decided | **fixed:** readings carry their possible sets, and the verdict decides on them |
| F5 | MINOR | a partial temp file matched the reader's glob | **fixed:** `.tmp` temp files and an anchored glob |
| F6 | MINOR | the gate did not compare construction flags (e.g. `prior_matches_truth`) | **fixed** (IA-3): required and if-present flags; a test fires on five bad flags |
| F7 | MINOR | `pass_truth` all true was assumed silently | **fixed** (IA-9): refused otherwise |
| F8 | MINOR | some controls could not disagree with the code (N replica, end-to-end K, the verdict test) | **fixed:** controls rewritten |
| F9 | NIT | state the W1–W3 σ choice in IA-12, and name the rate change | **done** (IA-12, §5) |
| NEW | MATERIAL | the count's possible set used only the four corners, skipping an interior "within" | **fixed** (`8b21b91b`): "within" is added when the corners hold both "better" and "worse"; test |

**Confirmation at `8b21b91b`: ADMIT.** The NEW finding is closed; the reviewer's worktree was clean and has been removed.
