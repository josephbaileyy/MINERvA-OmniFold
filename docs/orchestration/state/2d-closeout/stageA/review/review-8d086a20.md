# Independent review: 2D closeout Stage A candidate checklist (commit `8d086a20`)

**Reviewer:** a fresh, read-only Claude Opus 5.5 session (`claude-opus-5-5`). The owner was the same model, so this is not cross-provider independence (plan §5).
**Target:** `docs/orchestration/state/2d-closeout/stageA/REPORT.md` at `8d086a20` (branch `closeout/stage-a-checklist-20261012`), with its `scripts/` and `operands/`.
**Date:** 2026-10-12.

## Verdict: PASS WITH CHANGES

I recomputed every number I checked independently, and each matches the record: the `E_U` digest, the 205-cell set, the integral, the agreement with L0, POT and flux. The analysis re-runs byte for byte, the citations I checked point where they claim, and both hygiene checks pass.

The changes are about wording and scope, and none needs new compute:
- **The exit verdict:** "EXIT MET" names `E_U` as a candidate "with a complete manifest", but its own manifest has six fields unrecorded.
- **One false "bitwise" claim:** the integral is said to be bitwise equal to a VL173 receipt field. It is one ulp away from that field.
- **Scope gaps:** KI 90 is missing from NOT CITABLE FOR, the input-drift sentence in §6 overstates what is known, and Stage A's selective-I/O remainder is not mentioned.

## Findings

### MATERIAL

**M1. "EXIT MET" names `E_U` as having a complete manifest, and the record never declares which manifest is frozen for later stages.**
`REPORT.md:24`, `:34–37`; the CATALOG row; the commit subject ("exit met").

- **What the plan requires.** The exit (plan §4) is "one reproducible candidate with a complete manifest and independent comparison".
- **What the record shows.** Its own §4 table (`:211–218`) lists `E_U`'s driver, helper, environment and input digest as **not recorded**, and argv and threads as launcher text only. The record says the manifest is "complete through L0". Plan §4 does allow "a separately verified L0 delivery can supply the candidate". But the record keeps `E_U` as the candidate and treats L0 only as a comparison column. It never states which manifest later stages must freeze, although plan §1 says to "freeze the driver, helper, library versions, effective thread counts … and inputs".
- **Failure scenario.** A Stage C lane reads "E_U … Stage A exit MET" and re-runs `E_U`'s launcher, `sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh`. That launcher uses 128 threads and the path `runEventLoopOmniFold_MEFHC_universes_full.root`.
  - That path now holds a different file: mtime 2026-07-08, 171,117,087,867 B, sha256 `220c479e…` (measured; see N7).
  - It is not `E_U`'s input, and KI 93 records that this kind of file differs in truth inputs from CV42.
  - The record's caveats make this visible, but the verdict word, the CATALOG row and the commit subject stand without them.
- **Fix.** State the exit as met for the candidate **procedure**, whose complete manifest is L0's:
  - driver `3cc5adc7…`, helper `e9623412…`, input `43f8cc16…`, flux `d40aea69…`;
  - the receipt's environment, 64 threads, and seeds 42/43/44.
  - `E_U` is then the quoted file, shown equivalent to that procedure under the frozen 1e-8 criterion.
  - Declare this as the frozen producer for Stages B and C, and carry "via L0" into the CATALOG row.

### MINOR

**m1. The "bitwise equal to the VL173 receipt" claim is false by one ulp.**
`REPORT.md:47` (table row 2), `:93–95`; the commit message.

- The record's integral is 3.0730230563866027e-38.
- The receipt's `integral_ours_reported` is 3.073023056386603e-38. In Python, `==` is False and the two differ by exactly 1 ulp.
- The value is bitwise equal to the receipt's `integral_ours_all_bins` instead.
- `scripts/analyze.py` never opens the receipt, so the committed code never tested this claim.
- **Failure scenario:** a reader checks `analysis.json` against `integral_ours_reported` with `==`, the check fails, and they conclude that `E_U` is not the VL173 operand.
- **Fix:** say "bitwise equal to `integral_ours_all_bins`; 1 ulp from `integral_ours_reported` (summation order)", or add the comparison to `analyze.py`. No quoted number moves.

**m2. KI 90 is missing from NOT CITABLE FOR, and the plan is misquoted.**
`REPORT.md:12–17`, `:46`, `:79–81`.

- The row-1 verdict "205 cell identities VERIFIED" carries no limit.
- KI 90 is not in the NOT CITABLE FOR list, which does name KI 91–94 and P07.
- §3.1 says "the plan places them in Stage A's issue map". The plan's §3 issue map is not divided by stage, and KI 90 appears only at plan line 110.
- **Failure scenario:** row 1 is cited as closing KI 90. KI 90's closure evidence is a refusing negative control (same size, different cells) in the two publication consumers, which this record does not test.
- **Fix:** add KI 90 to NOT CITABLE FOR and correct the attribution.

**m3. §6 says input drift was "None found", but `E_U`'s actual input is unavailable.**
`REPORT.md:247–249`.

- KI 93 states "The May file and code revision are unavailable."
- The bridge from `E_U` to L0's input is an inference. Bitwise-equal *binned* saved inputs alone do not establish event-level identity for an unbinned fit. The 1.4e-11 output agreement is what carries the argument; a different event sample would move LightGBM at about 1e-3.
- **Fix:** write "`E_U`'s input is unavailable (KI 93); its equivalence to `43f8cc16` is inferred from bitwise-equal saved inputs and 1.4e-11 output agreement."

**m4. The selective-I/O remainder of Stage A goes unmentioned.**
CATALOG row; `REPORT.md` throughout.

- Plan §0 names two Stage A remainders: this checklist and the selective-I/O delivery.
- Selective-I/O has not been received (there is no `state/next-preparation-20261009/selective-io/` at `8d086a20`), and the record never mentions it.
- The exit wording does not depend on it. But plan §4 requires an equivalence bridge if the final producer differs from XR's, and selective-I/O is exactly such a producer change.
- **Failure scenario:** "Stage A exit MET" is read as "Stage A closed".
- **Fix:** add one line: selective-I/O is outside A-2's scope and still outstanding.

### NOTE

- **N1. The `Base` field is stale.** `:23` says `origin/main` `37985acc` (PR #92). The commit's parent is `7edb65fa` (PR #93). Every cited file is byte-identical between the two, so the code citations still hold.
- **N2. Histogram count.** `:61` says "17 histograms". `E_U` has 16 (13 TH2D and 3 TH1D), plus 7 TParameters and 2 TNamed, for 25 keys.
- **N3. Flux values are not exactly one value.** `:135` and `:149` say the 14 bins hold one value and "all 14 values are equal". They hold two adjacent doubles, 6.243343376851218e-4 and 6.243343376851219e-4. The conclusion (no numerical effect from the edge mismatch) stands.
- **N4. Units attribution.** `:90` attributes "nucleon⁻¹" to `minerva_paper_anc/README`. The README states cm²/(GeV/c)² only; "per nucleon" comes from the paper and the MINERvA-101 convention.
- **N5. Target count.** The "independent recomputation" (`:120–123`) re-runs the same MAT call that produced the driver constant (driver `:38` comment), so it confirms the transcription rather than deriving the count independently. The source of the call's parameters is not cited. I verified that `runEventLoop.cpp:361` and the omnifile producer `runEventLoopOmniFold.cpp:1708` both set `minZ=5980, maxZ=8422, apothem=850`. Cite them.
- **N6. Purity citation.** `unfold_2d_omnifold_unbinned.py:1044–1048` is argparse help text, not the implementation. The implementation's description is near `:1488`.
- **N7. The launcher-path omnifile digest finished two seconds before the commit.** `/pscratch/…/a2/eu_omnifile.sha256` reads `220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418`, ended 08:20:38Z; the commit time is 08:20:40Z. The record's "not measured" was correct at commit time. Stage B can pick the value up.
- **N8. "Independent comparison" is independent of XR's code, not of the owner.** The record reads values through the same `GetBinContent`/`repr` path XR uses. My read goes through a different path (`TH1::GetArray()` buffers) and reproduces its E_U-vs-L0 numbers exactly. Owner and reviewer being the same model is disclosed at `:260`.
- **N9. Exposure difference.** `RECORD-20261008…:90` states the 0.35 % exposure difference; the correct figure is 0.34 % (10.61e20 / 1.057394e21 − 1 = 0.341 %), which this record states. This is not a defect of this record.

## Item-by-item assessment (plan §4 Stage A)

| item | supported by cited evidence? | verdict word stands alone? |
|---|---|---|
| 205 cell identities | Yes for `E_U`'s own set (independently reproduced) | No: needs the KI-90 limit (m2) |
| units | Yes. The formula reproduces `hXSec2D` to 4.4e-16 and the magnitude matches the paper to about 1 %. The bitwise claim to VL173 is wrong by 1 ulp (m1) | Yes, once m1 is fixed |
| POT | Yes (independently reproduced) | Yes |
| target count | Yes. The parameters match the selection (N5) | Yes |
| flux | Yes (independently reproduced, including the 12-playlist recombination) | Yes, with its qualifier |
| purity / background inputs | Yes. Bitwise equal to L0 under the recorded `bkg_mode purity` | Yes |
| completeness | Yes | Yes |
| effective seeds | Yes by content: 1.4e-11 to L0 against a ~1e-3 seed effect | Yes, with its qualifier |
| **exit** | Supportable through the plan's L0 clause | **No: see M1** |

## What I recomputed (operands named)

My script reads histogram storage through `TH1::GetArray()` buffers instead of `GetBinContent` loops, and works in numpy. It ran on saul `login05` twice:
- under `root_6_28` (ROOT 6.28/12);
- after sourcing the canonical checkout's `setup_salloc_env.sh`, needed to read the per-playlist MnvH1D fluxes.

Script sha256 `daa9a662…`. Outputs: `rv_plain.json` `307339ab…` and `rv_mat.json` `e97636e7…`, under `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/review-a2/`. The two runs agree on every shared field. I compared against the paper's text file locally with my own comma-split parser.

| quantity | operand | my value | record |
|---|---|---|---|
| `E_U` sha256 (pscratch and CFS, via `sha256sum` and hashlib) | `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`, 55,531 B, mtime 2026-05-27 04:58:49 PDT | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` (both copies) | same |
| L0 sha256 | CFS `XR-L0.root` | `751380245dbb27f6…` (equals the L0 receipt's `output.sha256`) | same |
| flux file sha256 | `baseline_flux/runEventLoopMC_MEFHC.root` | `d40aea69235cdc98…` | same |
| cell set | `hXSec2D` against `data_result_ptpl_2D_minerva_inclusive_6GeV.txt` (nonzero = reported, per the README) | 205 positive, 19 zero, 0 negative. The set equals the paper's and XR's `references.json` CV42. Unreported GlobalIDs 144, 160, 161, 176–178, 192–196, 208–215. The axes' edges equal `bin_mapping.txt`, and the GlobalID-to-edge mapping holds in all 224 rows | same |
| integral (205 cells) | `E_U` `hXSec2D` × bin areas | `math.fsum` 3.0730230563866027e-38; `np.sum` 3.073023056386603e-38 | 3.0730230563866027e-38 |
| ratio to the paper's text file | as above | 1.011028965540987; median bin ratio 1.0083619235914807 | 1.01103 / 1.00836 |
| `E_U` vs L0 | both `hXSec2D` over the 205 cells | max rel **1.3751444427612114e-11** (GlobalID 171); median 5.88462611972318e-12; integral 7.01882996168024e-13; 0 cells over 1e-8; 0 bitwise | 1.375e-11, GID 171, 5.88e-12, 7.0e-13 |
| POT | 12 `runEventLoopData_<pl>.root:POTUsed` and 12 `runEventLoopMC_<pl>.root:POTUsed` | data fsum 1.057394261158926e21 = `E_U` `dataPOT` (rel 0); MC fsum 4.978198462880826e21 vs 4.978198462880827e21 (−2.2e-16) | same |
| flux | `E_U` `hFlux_pt` vs the flux file; 12 MC playlists' `pTmu_reweightedflux_integrated`, weighted by data POT (rule from `combine_flux_MEFHC.py:10`) | bitwise equal; recombination max rel 0.0 (dot-product order) | equal; 2.2e-16 |
| VL173 receipt | `RECEIPT-2d-agreement-windows-lgbm42-20261011.json` | `integral_ours_reported` = 3.073023056386603e-38 (≠ record by 1 ulp); `integral_ours_all_bins` = 3.0730230563866027e-38 | "bitwise equal to `integral_ours_reported`" (m1) |
| L0 receipt | `xr-linux/results/outroot/L0/a1/receipt.json` | `random_state` 42×5, 43×5, 44×5; 64 threads; input `43f8cc16…` (mtime 2026-05-18); output digest `75138024…` | same |

## Reproducibility and hygiene

- **`scripts/analyze.py` on `operands/`:** I ran it locally with Python 3.12.2 and numpy 1.26.4. The output is **byte-identical** to `operands/analysis.json` (`cmp` silent; sha256 `1fe7b04f…`). All ten script and operand digests match the §5 prefixes.
- **`python3.12 docs/orchestration/generate_manifest.py --check --at-sha 8d086a20`:** `MANIFEST-CHECK :: OK exit=0`, with rows=2317 and one unused override.
- **`python3.12 docs/orchestration/verify_hash_bindings.py`:** `ALL BINDINGS INTACT`, rc 0.
- **CATALOG and MANIFEST:** one CATALOG row, and a `MACHINE open` override for the REPORT. That matches the convention of every other `state/*/REPORT.md`, such as `xr-linux` and `two-d-followup`.

## Citation spot-check (at `37985acc`): 14 checked, all point where claimed

- `unfold_2d_omnifold_unbinned.py`:
  - `:41` `TRACKER_FIDUCIAL_N_NUCLEONS`;
  - `:126–142` `load_flux_bins` (checks the bin count only, reads by bin index);
  - `:888–945` `extract_cross_section_2d`, formula with `1e4`;
  - `:1044–1048` the purity rule, as help text (N6);
  - `:1348` `hasTruthOnlyMisses` read as a boolean;
  - `:1741–1744` seed rule seed / +1 / +2.
- `ExtractCrossSection.cpp`:
  - `:122–128` `normalize` (Divide by flux, Scale 1/N/POT, `1e4`, width);
  - `:195` `nNucleons` ingredient.
- `runEventLoop.cpp`:
  - `:407` `dansPTBins` 0, 0.075, … (matches the flux file's edges, which I read);
  - `:483` `GetTrackerNNucleons(minZ, maxZ, true, apothem)`.
- `sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh`:
  - `:8` 128 CPUs; `:21` `OMP_NUM_THREADS`; `:43–50` argv; `:49` `--seed 42`.
- `RECORD-20261008-release-audit-corrections.md:90`: the D02 POT row.

## Worktree status

- **Start:** a detached worktree at `/private/tmp/claude-501/review-a2-8d086a20`, HEAD `8d086a20635b43fd8cca319a73bb59f66fd033ef`. `git status --short` was empty.
- **End:** `git status --short` was empty (0 lines) and HEAD was unchanged. The worktree was removed with `git worktree remove` (rc 0) and is no longer in `git worktree list`.
- **No writes outside scratch.** Nothing was edited, committed or pushed in any checkout, and no Slurm job ran. On the cluster I wrote only under `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/review-a2/` (`rv_indep.py`, `rv_plain.json`, `rv_mat.json`). Locally I wrote only under `/private/tmp/claude-501/review-a2-scratch/`.