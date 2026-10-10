# D-ID — binned exact-response diagnostic of the scalar-5D GBDT residual

**CITABLE FOR:** the frozen D-ID implementation (`did.py`, `config.json`) and its synthetic controls
(`test_did.py`); the prospective amendments to gbdt REPORT §6 recorded here before any real input was
opened (§3); the resolution of the post-review branch-B route (§4); the meaning and limits of the
diagnostic labels (§5); and, once filled in, the results, the independent verification and the
disposition (§§8–12).
**NOT CITABLE FOR:** a measured cross section, an interval, a coverage result, an estimator, a
ratified gate, compute authority, or any regrading of s5c/s5n/s5e/s5p. Every result is
simulation-only. It is conditional on the fixed detector response, the signal-only binned
construction and the development departures. The 2.5% / 10% widths, the 5% allowance and the 2%
eligibility floor are **proposals carried from the gbdt lane, not gates**. This diagnostic does not
validate intervals, does not resolve the 2D pairing problem, and does not achieve a joint-5D
publication-ready measurement.

| field | content |
|---|---|
| `Lane` | D-ID owner (bounded local diagnostic) |
| `Decision` | At the declared response binning, truth resolutions and reporting functionals, which parts of the observed GBDT residual are consistent with finite-iteration regularization, GBDT approximation/bookkeeping, or weakly constrained response directions? Which conditional next step, if any, is justified? |
| `Branch` / `Base` | `study/d-id-20261009` / `a16d578646936a0cc6eca41e3e0350e756ee0dca`: the verified main pin, merge of PR #68, recorded in that PR's delivery comment; `origin/main` was equal to it at 2026-10-10T04:34Z |
| `Owned files` | `docs/orchestration/state/next-preparation-20261009/d-id/` only: this report, `did.py`, `config.json`, `test_did.py`, `outputs/` (numerical outputs and manifests) and the preserved review records |
| `Immutable inputs` | the `gbdt/` subtree (design, `comparator.py`, reviews, `results.json`); the committed nd-unfolding code, ratio files, receipts and synthesis operands named in `config.json`; the cluster products in §1 |
| `Authority` | Joseph's D-ID prompt (2026-10-09): implementation, one admission review, then (on PASS) the named local calculation. No training, no s5p extension, no Slurm/GPU/login-node computation |
| `Resources` | §7.1: ≈ 3.0 active h; ≈ 1.5 local core-h in all (owner run 0.81, verification 0.23); peak RSS 4.65 GB; scratch ≤ 1.9 GiB; tracked outputs 7.0 MB; cluster: listings and read-only copies only |
| `Review` | one fresh reviewer (Claude Opus 5.5 subagent, read-only): admission ADMIT-WITH-REPAIRS → one focused re-review ADMIT ([`review-admission.md`](review-admission.md), §8); final numerical verification PASS ([`verification.md`](verification.md), §10). Budget used exactly, no further review |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §11: implementation **PASS**, admission **PASS**, numerical verification **PASS**, discriminating question **PASS**. Branch **C** in J, EW and H2; J carries it, while H2 is uninformative. It is scoped to binned estimators and to the resolution-stable functionals |
| `Next action` | §12: one decision for Joseph, the endpoint-scope question (gbdt §10.3). Should the scalar-5D endpoint move from J cells to identified functionals (I2's MC-only selection), or stop at a recorded binned no-go for J? |

`Q` = `docs/orchestration/state/next-preparation-20261009`. "§6" alone means gbdt REPORT §6.

## 0. Setup (campaign review §1)

- **Roles.** One owner (this session) and one fresh read-only reviewer. CAMPAIGN-REVIEW §5 suggests
  Astra High for consequential review, but it is not reachable from this session. The reviewer is a
  fresh Claude subagent in its own detached worktree, so the review is not cross-provider
  independent. The prompt authorizes exactly this reviewer and no other workers or peer messages.
- **Review budget (whole session).** One admission review of the frozen commit, one final numerical
  verification after the run, and at most one focused repair/re-review. If a required design repair
  uses that allowance and a later material issue appears, the session ends INCONCLUSIVE.
- **Terminal outcomes.** Each of four questions gets its own PASS / FAIL / INCONCLUSIVE:
  implementation, admission, numerical verification and the discriminating question (§11). A
  scientifically supported no-go counts as a completed diagnostic.
- **Caps.**
  - 10 active hours.
  - Local CPU: preparation and synthetic work ≤ 2 core-h. The real diagnostic plus the independent
    numerical verification ≤ 8.8 core-h, with ≥ 20% protected, so the owner's run is capped at
    7.04 core-h (§7). Combined ceiling 10.8 core-h.
  - Two compute threads, 8 GiB RAM, 2 GiB scratch, 10 MiB tracked numerical evidence.
  - Cluster use: read-only `ls` and file copies only.

## 1. Inputs and identities

| role | object | identity (checked by the driver unless stated) |
|---|---|---|
| events | `of_inputs_5d.npz` (cluster `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/`, 1,548,438,020 B, present 2026-10-10T04:3xZ) | sha256 `07fccc1a…` (A1); the MC keys only (A10, AM-17) |
| study-K traces | `s5p-20260926/runs/s2/conv/k_b0_{nominal,w3}.npz`, `k_b0_{gibuu,q3,w1}.npz.partial.npz`, `k_cap10_{gibuu,q3,w3}.npz` | sha256 equal to the synthesis `inventory.json` (A4). Sizes are equal to it at the listing |
| s5e diagnosis products | `s5e-20260925/runs/diag/asimov/asimov_{b0,cap,unity}_*.npz`; `trace/trace_{eavail,q3,nominal}_sig_s30x00{0–3}.npz` | no committed byte digest exists. Admitted by their embedded input digest and construction, and by reproducing the diag receipt's S_dep and λ_5D (AM-13); their sha256 is recorded |
| truth reweights | committed `s5n_pseudo.truth_weight` after `s5p_converge.install()` (+ `s5p_truths` for `cond_ratio`); ratio files `45cc3e0a…` (GiBUU), `2a208df9…` (W1), `80e16f95…` (W2), `3455daf3…` (W3), `9240e4b3…` (P1r), `6a36c9bc…` (P2r), `b3108969…` (P3r); q3 = `q3_given_eavail_w`, a = 0.3 | file digests (A3); module digests in `config.json`, which equal those recorded in the study-K products' `code_sha256` for every weight-path module; A5 (§3) checks the outcome |
| binning, extraction, functionals | `s5e_trace.flat_index`, `xsec_nd.extract_cross_section_nd`, `s5c_coverage.reported_functionals` + `s5p_converge.h2_rows` (185 rows, the traces' own) | module digests; name list equal to each complete trace's `functional_names` (A4) |
| labels and thresholds | `Q/gbdt/comparator.py` | sha256 `f5374fe0…`, imported, never copied |
| W2 comparator | `assessment_W2` / `assessment_W2_truth` of the synthesis `operands.npz` (`61c32477…`) | committed |
| receipts | s5p `stage2_receipt.json` (`0daa7cd8…`), s5e `diag_receipt.json` (`f0880725…`) | committed |

The real-data members of the event file (`measured`, `measured_weights`) are never read. No sealed
bank, no data file and no new simulation is used.

## 2. What the driver computes (§6 computations 1–5)

For each of nine weight sets (nominal, GiBUU, W1, W3, q3, W2, P1r, P2r, P3r), with truth grids T1 (J
cells), T2 (J split at the nearest interior fine edge) and T3 (fine), the two sample roles and the two
response weightings:

1. IBU from the nominal prior, K = 1…200 (sparse response). Residuals are taken on all 183 named
   functionals; the decision uses the 175 reported ones.
2. IBU to convergence at T1 and T2, same-sample, nominal-weighted. The stopping rule is a largest
   relative cell change < 1e-10, or 10⁵ iterations. Non-convergence is recorded and blocks branch B.
3. Fisher `F = Rᵀ diag(1/(R t + b)) R` at T1 and T2, same-sample, both weightings (18 at T2). The
   eigendecomposition is reused for the CR width and the invisible share. Each is tested equal to
   `comparator.cr_width` / `invisible_share`.
4. The invisible share of the GBDT's final fine-grid residual, aggregated to T1/T2, where such an
   estimate exists (AM-9).
5. Labels (`comparator.classify`), the pooled per-map aggregation (`comparator.branch_outcome`, through
   the stage-4 wrapper `declare`), the branch-B trace reading (§4) and the missed-event concentration
   (`comparator.missed_concentration`).

Admission checks (stage 1; any failure stops everything after it):

- A1: event digest.
- A2: the committed records and operands the run reads (receipts, inventory, definition, operands).
- A3: ratio-file digests.
- A4: trace digests, names and input digests. The committed functional rows must be exactly the 185
  study-K rows, equal to a list built from the operands (AM-32/M1).
- A5: the committed reweights reproduce every comparator's own truth functionals within 1e-9 relative.
- A6: each receipt-limited trace prefix reproduces the stage-2 receipt's per-K median series within
  1e-9.
- A7: 10,499 reco cells; S_dep within 0.1% and the GBDT fold λ_5D within 2% at K = 5, 15, 30 of the
  diag receipt; my fold equals the s5e file's within 1e-9.
- A8: 20,402,110 signal pair rows (s5e geometry's `rows_eligible`).
- A9: edges equal `definition.json`.
- A10: the list of keys read.
- A11: every reweight is exactly 1 outside the grid (AM-28).

Controls:

- C1 (gating): same-sample nominal returns |r_IBU| ≤ 1e-8 at every K and grid.
- C2 (gating at T1): with the departure-weighted response, IBU(∞) reaches the exact truth within
  0.01 σ_c on identified functionals. At T2 it is reported only.

## 3. Prospective amendments to §6 (recorded before any real input was opened)

None of these changes a threshold, a grid, a departure, an iteration limit or the aggregation of
`comparator.py`. Each fixes something §6 leaves open, or corrects a factual reading of its inputs.
Each is coded in `did.py` where its tag appears.

| tag | §6 says / leaves open | fixed here | why |
|---|---|---|---|
| AM-1 | the primary asimov_same comparators are "background-inclusive (`no_background: False`)", so confound (a) applies | **Correction:** asimov_same has no background on either side. `s5e_trace.asimov_same` uses the reco-passing *signal* MC rows reweighted by `r` as the measured side. "No Poisson, no background, no refinement" (docstring). `no_background: False` is the unused CLI default, which the tool refuses to change for non-pseudo constructions. Confound (a) therefore does not apply to the primary comparison. It still applies to the D3 `_bkg` runs (not used) and to any transfer to real data. It is preserved in §5 | the code is the authority for what the comparator measured |
| AM-2 | truth-passing rows whose truth lies outside the 5D grid (including the −9999 sentinels, which B0 did not drop) | their reco enters the pseudo-data, as in asimov_same. Their reweight is 1 in every construction, so the IBU carries their fold as a **known additive term b**. Same-sample this is exact; split-half takes it from half A | the reference IBU has no such term; dropping the rows would change the data |
| AM-3 | empty truth cells "dropped and listed"; nothing on zero-efficiency cells | a cell with truth weight but no reco keeps its prior (the reference would raise). It is an exact null direction of F, so every functional touching it is σ = ∞ | otherwise T2/T3 IBU cannot run |
| AM-4 | how an IBU estimate on T1/T2 becomes a functional value | each cell's estimate is spread over its fine cells in proportion to that weighting's own MC truth shape, then passed through the committed extraction and functional rows. The CR map is that same linear map. Relative σ = σ / \|h·t\| at that weighting | the only construction that is exact when the shape is right; tested both ways |
| AM-5 | the "binning bias" as "its own number" | r_IBU is relative to the exact fine-grid departure truth (the comparators' own `fn_true`). Binning bias = r_IBU(nominal-weighted) − r_IBU(departure-weighted), at the same grid and K | the GBDT residual is measured against the same truth |
| AM-6 | the content of each priority stage | (1) admission + C1; (2) T1: same-sample both weightings, K ≤ 200, Fisher, labels, convergence, exactness (C2); (3) T2: same-sample both weightings, Fisher, labels, K ≤ 200; (4) T2 convergence; (5) T3 same-sample and all split-half trajectories, then the T2 exactness report | the resolution-sensitivity rule needs the T2 departure-weighted labels, so they cannot wait for stage 5 |
| AM-7 | "a functional whose label changes between T1 and T2, or between nominal- and departure-weighted responses" | label = `classify`'s (iteration, identifiability) pair at K = 5. Compared T1 vs T2 (nominal, same-sample) and nominal vs departure weighting (T2, same-sample) | explicit operands |
| AM-8 | branch-B route (post-review, unreviewed) | §4 | the issue the prompt names |
| AM-9 | "the invisible share of the GBDT final-K residual" | computed from a fine-grid GBDT estimate where one exists. W3 and nominal use the K = 200 traces. GiBUU and q3 use the s5e D4 asimov_b0 products at K = 30 (same B0 asimov_same construction). W1 and W2 are **missing**: partial checkpoints carry no fine-grid estimate, and W2 has only an ensemble mean. The residual is converted to counts by the extraction's per-cell factor, and fine cells with no factor are set to zero | the partial checkpoints store functionals only (`s5p_converge.install_checkpoints`) |
| AM-10 | "each functional's missed-event fraction" | the share of the functional's departure-weighted truth carried by truth-passing, reco-failing rows. The concentration is computed per departure and map, over the reported functionals with a comparator. Excess = \|r_GBDT(5) − r_IBU(5)\| at T2, nominal, same-sample. Descriptive (§5) | |
| AM-11 | "the existing split key" | `half_mask(n_rows, key)` with key = `split_key_for(301000)` = 798,985,164,084,644, the first D3 signal-only E_avail trace's. It must equal that product's recorded `split_key` bitwise, or split-half is missing. Half B is the pseudo-data source, half A the response/prior/known-term half, both ×2 (s5n) | |
| AM-12 | P1r–P3r construction | a = 1, the s5p power construction (amendments 7/8). P1r/P3r through `ratio_nd` (`s5e_deform`), P2r through `cond_ratio` (`s5p_truths`) | |
| AM-13 | "digests equal to `inventory.json` and to the diag receipt's inputs" for the s5e secondaries | no byte digest of them is committed. They are admitted by embedded `input_npz_sha256` + construction and by A5/A7 reproduction; their sha256 is recorded | |
| AM-14 | the W2 comparator | the mean over the 20 R K = 5 experiments of `fhat/ftrue − 1` (the synthesis definition), at K = 5 only | |
| AM-15 | Fisher `F = Rᵀ diag(1/y) R` | **a correction, not a fill-in** (review m5): F is evaluated with that weighting's response at the departure's binned truth, `Rᵀ diag(1/(R t + b)) R`. This equals §6's formula for the departure-weighted response. For the nominal-weighted response it differs from it by the binning bias in the variance | local Fisher at the true parameter; b in the variance |
| AM-16 | cap enforcement | before each unit, priced in `config.json` `price_s`, and every 1,000 iterations inside long loops, against 7.04 owner core-h of process CPU (all threads + children). Failed attempts count (`--spent-before-s`) | |
| AM-17 | none | the event file's real-data keys are never read. A synthetic file whose real-data members are corrupt proves it end to end | the prompt forbids real data |
| AM-18 | "relative truth change < 1e-10" | the largest over active cells of \|Δt\|/t | |
| AM-19 | T2 split at "the fine edge nearest its midpoint" | lower edge on a tie (pz bin [3.5, 6]: 4.5 vs 5.0). T2 = 6·6·6·4·6 = 5,184 cells at most | |
| AM-20 | "if all three sets are small, record INCONCLUSIVE" | small = every share < 1/3 | |
| AM-21 | event/split convention | A8 checks the signal pair-row count against s5e geometry's `rows_eligible` (pass_reco ∧ pass_truth ∧ both in grid) | an independent committed count |
| AM-22 | "at T2 the exactness control is reported" | the departure-weighted T2 convergence it needs is unpriced in §6, so it runs last in stage 5 and never gates | |
| AM-23 | C2 at T1 | the gate is the frozen criterion (error ≤ 0.01 σ_c on identified functionals); convergence is reported beside it | |
| AM-25 | none (repository convention) | `config.json` stores expected digests as `expect_sha256` / `ratio_expect_sha256` with no sibling path key, and `results.json` stores observed ones as `observed_sha256`. The repository's binding collector therefore counts them as unpaired (printed, not gated). The driver verifies every one at run time (A1–A4). The first freeze attempt was refused by the pre-commit hook, which pairs `path` + `sha256`. That would have changed the pinned receipt-binding inventory in `verify_hash_bindings.py`, a shared guard this lane does not own. The event file is cited with a directory (`nd-unfolding/of_inputs_5d.npz`, relative to the inputs directory), not bare | the gbdt lane's precedent (`results.json` `integrity`); registering these bindings is an integration-owner choice |
| AM-24 | which trace iterations are evidence | the receipt-verified prefixes only: GiBUU 40, W1 40, q3 30 (of 100/125/100 present), W3 and nominal 200. A6 checks the per-K median series at the receipt's K points. Together with the A4 file digest, this identifies each prefix with the one study K recorded (wording corrected, review m5) | N1: later iterations have unverified provenance |
| AM-26 | convergence for branch B (review M2) | **per functional.** A functional counts as converged when its own last-step relative change \|Δ(h·t)\|/\|h·t\| is below 1e-10 at the stop, or when the whole run met AM-18. The run-level rule and flag are kept and reported, and each functional's last-step change is in the tables | gbdt §6 says "a T2 *functional* that has not converged". A per-run flag would let one slow cell outside every reported functional remove all of them, which makes B structurally unreachable at 5,184 cells |
| AM-27 | A8 (review m1) | `rows_eligible` is recounted with its producer's own rule (`s5e_geometry.in_grid`, upper edge excluded, digest-pinned). The pair-row count (edges closed) is recorded beside it | the two rules differ on upper-edge rows |
| AM-28 | AM-2 premise (review m4) | A11 gates, in stage 1, that every weight set's reweight is exactly 1 on rows outside the grid | AM-2 uses the nominal known term b for every departure |
| AM-29 | B without stage 4 (review m2) | `B-undeclarable` only when B is reachable, i.e. its candidates are ≥ 1/2 of the eligible functionals. Otherwise the map is `mixed`, with `b_reachable = false`, the candidates listed and `stage4 = missing`. AM-20 then bounds B by its candidate share | B cannot reach its share whatever stage 4 would give |
| AM-30 | W2 in the pool (review m3) | the frozen pooled outcome is unchanged. Beside it, the shares with W2 left out are reported (`without_w2`), because W2's comparator is the background-inclusive, split-MC, Poisson R ensemble (E2) | input-role transparency |
| AM-31 | σ = ∞ causes (review m6) | each width records whether the functional's map has weight on a zero-efficiency cell (`acceptance_hole`). A C label with an acceptance hole is an acceptance gap, not a weak response | label meaning |
| AM-32 | caps and failures (review M3) | the RAM cap is checked at every budget check (peak RSS against 8 GiB), so a peak cannot be pre-empted, only stopped at the next check. Stored trajectories keep only K and r. Row arrays are freed after binning. The committed row-wise `flat_index`/`in_grid` run in row chunks (identical output, tested). Any other exception marks its stage `error` (exit 6), later stages are `not-started`, and once stage 1 is complete the decision and tables are always written | memory accounting and crash safety |

## 4. The branch-B route (the post-review issue, resolved before execution)

The gbdt lane repaired branch B after its last review (N1, #8): branch B is "first read from D-ID's
matched-K comparison against the existing s5p study-K traces". That repair named no computation, and
the integration report left it unreviewed. Without a computation, a B outcome could be read as "more
GBDT iterations would remove the residual". That claim belongs to the GBDT side of study K, which
terminal s5p already measured and which this prompt forbids extending.

**Frozen rule (AM-8).**

1. **Declaration is unchanged:** `comparator.branch_outcome` at K = 5, T2, same-sample,
   nominal-weighted. B needs the functional to be identified at target, iteration-faithful, and to
   have |r_IBU(∞)| ≤ 0.5 |r_GBDT(5)|. r_IBU(∞) comes from stage 4 and must be *converged for that
   functional* (AM-26). Non-converged functionals enter with r_IBU(∞) = ∞. If stage 4 is incomplete
   at the cap, the map's outcome is C or A if either reaches its share alone. Otherwise it is
   `B-undeclarable` with the candidates listed, unless B is unreachable (AM-29). It is never
   silently folded into mixed.
2. **Trace reading.** For every functional counted toward B, the driver reports K_max (the
   receipt-verified trace length: W3 200, GiBUU 40, W1 40, q3 30), r_GBDT(K_max) and r_IBU(K_max) at
   T2. Each gets one reading, using only the frozen 0.3 tolerance and the 2% floor:
   - `tracks`: still iteration-faithful at K_max, or both residuals ≤ 2%;
   - `departs`: the GBDT leaves the exact iteration's path inside the traced range;
   - `untraced`: W2, which has no trace beyond K = 5.
3. **What B may then say.** Only what the existing traces show. A `tracks` reading says the GBDT
   followed exact IBU over the traced range. Whether it would keep doing so beyond K_max is
   **unresolved by existing evidence**, and extending the traces needs its own authorization
   (≈ 8.7 node-h admitted, gbdt §6). A `departs` reading says the existing traces already contradict
   "iteration count" as the whole mechanism for that functional. B is never an instruction to
   iterate further, and nothing here re-runs study K.

## 5. Meaning of the labels, and their limits

- **Same-sample oracle.** The IBU unfolds the very MC rows that make its data, with exact efficiency.
  It is a diagnostic oracle, not an estimator. Its residual at finite K is regularization by early
  stopping. Its residual at convergence on the nominal-weighted response is within-cell binning bias
  plus the effect of null directions.
- **σ_c is a local, binned, model- and grid-dependent Cramér–Rao width** at the departure's own truth.
  It assumes the Poisson Gaussian limit and unbiasedness in the regular directions. It is
  signal-only: no background variance, which makes it optimistic. It does not bound biased
  estimators, unbinned estimators, or estimators that use prior information. Binned reco
  information is conservative relative to the unbinned data. Coarse truth cells hide within-cell
  freedom and are optimistic. These errors run in opposite directions, so neither T1 nor T2 bounds
  the truth. A label that changes between T1 and T2, or between weightings, is excluded from every
  branch, and the full tables keep it.
- **"Weakly identified" (C)** means: for binned estimators at this reco binning and T2 resolution, at
  the analysis exposure, the functional's CR width exceeds 10%. It is not an impossibility theorem.
- **A finite null-direction search cannot prove identifiability.** The null fraction is computed at a
  relative eigenvalue cut of 1e-12 (the reference's). Functionals with σ = ∞ are flagged, never
  dropped.
- **Missed-event concentration** (≥ 2/3 of the summed excess in the top missed-fraction tercile) has
  no null calibration. The gbdt reviewer's fixtures gave a 5–7% false-positive rate. It is
  descriptive, reported beside the branch, and never decides one.
- **Confounds preserved.**
  - Background: not present in the traced (asimov_same) comparators of GiBUU, W1, W3 and q3 (AM-1).
    It **is** present in W2's comparator, the candidate-R assessment ensemble (background-inclusive,
    split MC, Poisson). W2 enters the pool only through E2's agreement of noise-free and ensemble
    means, so the pooled shares are also reported without W2 (AM-30). Background is also present in
    D3 `_bkg` and in real data, where s5e D3 measured signal-only 10.5% / 74.1% against background-inclusive
    10.7% / 74.5% (E_avail, median/max EW at K = 5).
  - Missed events: the GBDT fills reco-failing rows with a regressor, while the IBU uses exact
    efficiency. That difference is part of what "approximation/bookkeeping" means here, and it is
    measured, not removed.
- **Inconclusive by construction.** Mixed outcomes, undeclarable B, no eligible functional and
  failed controls are INCONCLUSIVE for the discriminating question, not evidence for any mechanism.

## 6. Synthetic controls (`test_did.py`: 22 tests at the freeze `9203add1`, 29 after the admission repairs, all pass)

Unit-level fixtures (dense, small) against `comparator.py`:

| mechanism | fires on the defect | silent on the clean case |
|---|---|---|
| sparse response construction | — | equals a brute-force dense response (1e-13); same-sample y = R t + b exactly; empty cell dropped and listed |
| T2 split / J map | — | T2 edges as in AM-19; T1 cell of every fine cell equals the support of the committed J rows |
| IBU | the reference refuses a zero-efficiency cell | equals `comparator.ibu` at every K (1e-12); with a known term the nominal closes exactly; a zero-efficiency cell keeps its prior |
| convergence / non-convergence | a 20-iteration cap reports `converged = False` | converges below 1e-10 |
| singular Fisher / null space | a duplicated response column makes the difference functional σ = ∞ (null fraction > 0.99) | the sum and an unrelated functional stay finite; Fisher, widths, null fractions and invisible share equal the reference (1e-12); a known term widens σ |
| functional projection | nominal shares on a within-cell departure give a > 0.1% bias | own shares are exact (1e-13); the fine grid has no binning freedom |
| branch aggregation | B-undeclarable when stage 4 is missing; non-converged B candidates fall out of B; tie listed | B, C declared when they should be; `b_counted` equals `branch_outcome`'s B count over 200 random label sets |
| sensitivity / trace reading | a changed label is flagged | `tracks` / `departs` / `untraced` each reached |
| receipt-prefix check (A6) | a 0.1% tampered median, a one-sided NaN and a shifted prefix are caught | exact series → 0 |
| cap / interruption | a 1e-9 core-h budget raises before work and inside an IBU loop; a 1-byte RAM cap raises at the next check | — |
| functional rows (M1) | — | the committed rows are exactly 185 and equal a name list written independently in the test from the operands; H2 is not stacked twice; the end-to-end traces use that independent 185-column layout |
| per-functional convergence (M2) | a functional on a slow, decoupled block stays unconverged | the run is not converged, but the two functionals away from the block are (last step < 1e-12) |
| B reachability (m2) | — | without stage 4 and with a 1/4 candidate share the map is `mixed` with `b_reachable = false` |
| chunked binning (M3) | — | chunked `flat_index` / `in_grid` equal the unchunked ones, including rows on upper edges |
| errors (M3) | an exception injected in stage 4 → exit 6, stage 4 `error`, stage 5 `not-started` | the decision and tables of stages 1–3 are still written; stored trajectories hold only K and r |

End to end, on a synthetic event file with the real 5D grid, the real functional rows and the real
reweight code (40,000 rows; truth in 32 J cells; 30% missed; 40 sentinel rows inside pass_truth), plus
GBDT stand-ins written as `factor × exact T2 IBU residual` at every K:

- **Resolution-sensitivity positive control** (factor 1). Every functional above 2% is
  iteration-faithful at the primary setting. Every one is excluded because the departure-weighted
  label differs (the residual is binning bias). Each map gives `no-eligible-functional`. All stages
  complete, every gating control passes, and the real-data members (deliberately corrupt) are never
  read.
- **Binning-bias negative control** (J-constant departures). Binning bias < 1e-9 everywhere, labels
  equal across weightings, A share 0.
- **Approximation** (factor 5, identified exposure) → J branch **A**.
- **Weak exposure** (same, weights × 1e-6) → J branch **C**.
- **Cap during stage 4** → stage 4 `cap`, stage 5 `not-started`, each map C, A, `B-undeclarable` or
  no-eligible. **Cap during stage 1** → no decision.
- **Tampered input digests** (event, a trace) → exit 4 at that check, later stages not started.
- **Thread limit above 2** → refused.

The small world cannot exercise A6 end to end (some reported functionals are empty there, so the
receipt medians are NaN). A6 has its own finite-valued control, and on the real inputs the driver
records the NaN-median count (expected 0). An end-to-end B case needs larger residuals that are
stable across T1/T2 than this world gives. B is controlled at the aggregation level instead.

Resources of the full suite: 79 s CPU (≈ 0.02 core-h), peak RSS 0.59 GB, two threads (after the repairs).

## 7. Cost, memory and the frozen fallbacks

- **Owner run cap:** 7.04 core-h, i.e. 8.8 minus max(20% = 1.76, the priced 1.0 verification). The
  run stops before a unit that cannot fit and keeps completed stages. The reviewer's verification
  must fit in the remaining ≥ 1.76 core-h.
- **Expected owner run**, from the §6 price, re-derived for T2 = 5,184 cells (not 7,776):
  - histograms ≈ 0.05–0.3 core-h;
  - trajectories ≈ 0.1;
  - T1 convergence + exactness ≤ 0.5 at the 10⁵ worst case;
  - T2 convergence ≤ 1.4 worst case;
  - 18 + 18 Fisher eighs at T1/T2 ≈ 0.2;
  - T2 exactness (stage 5, report only) ≤ 1.4 worst case.

  This is ≈ 1–4 core-h, below the cap with margin.
- **Memory (measured after the M3 repair).**
  - Method: stage-1 row work (load, binning, the nine reweights, the pair tables) in a fresh
    process, on synthetic files with the real per-row layout (58 B/row).
  - Peak RSS: 1.06 GB at 4 M rows and 1.57 GB at 8 M rows, i.e. ≈ 0.13 GB per million rows plus
    0.55 GB fixed.
  - Real file: the 1.548 GB file holds at most ≈ 26.7 M MC rows at that layout, so ≈ 4 GB. Adding
    ≈ 1 GB because the real file has more distinct signal pairs (76% of rows, against 46% in the
    synthetic file) gives ≈ 5 GB, below 8 GiB.
  - Later stages: the dense T2 Fisher is ≤ 215 MB (the cap rule drops T2 only above 6 GiB). A T3
    problem is ≈ 0.2–0.3 GB and is not retained.
  - The RSS guard stops the run at the next check if this estimate is wrong. Stage-1 CPU was 18 s at
    8 M rows, so ≈ 1 min at full size.
- **Scratch:** the event file 1.442 GiB, plus ≈ 30 MB of comparators and ≈ 0.1–0.2 GB of
  verification operands, below 2 GiB. All of it is deleted at delivery. The column-extract alternative
  would need login-node computation, so it is not used.
- **If a cap is reached:** the frozen stage rule of §4/§6 applies. Nothing is retuned.

### 7.1 Actual use

| item | measured | cap |
|---|---|---|
| active time | 04:34–06:50Z and 09:32–≈10:20Z, ≈ 3.0 h. An idle usage-limit pause from 06:50 to 09:32Z is excluded | 10 h |
| preparation and synthetic CPU (owner) | ≈ 0.35 core-h (timed test runs ≈ 0.2, memory measurements ≈ 0.07, hooks/verifiers/smoke ≈ 0.08; partly estimated) | 2 core-h |
| admission reviews (reviewer) | ≈ 0.10 core-h (its own estimates over two rounds) | — |
| real diagnostic (owner) | **0.806 core-h measured** (one attempt, `/usr/bin/time -l` user+sys, 2 threads); input manifest and reading of the outputs ≈ 0.01 | 7.04 core-h |
| numerical verification (reviewer) | ≈ 0.23 core-h (including one crashed attempt) | ≥ 1 protected; 8.8 with the run |
| combined | ≈ 1.5 core-h | 10.8 core-h |
| peak RSS | 4.65 GB (run); 4.15 GB (verification) | 8 GiB |
| threads | 2 | 2 |
| scratch beyond worktrees | peak ≈ 1.88 GiB (inputs 1.59 GB plus reviewer scratch); deleted at delivery | 2 GiB |
| tracked numerical evidence | `outputs/` 7.0 MB | 10 MiB |
| cluster | two `ls` listings and `scp -p` read-only copies; no job, no login-node computation, no GPU, no training, no Slurm | — |

## 8. Admission review

**Verdict at `9203add1`: ADMIT-WITH-REPAIRS** (record: [`review-admission.md`](review-admission.md)).
The reviewer was a fresh Claude Opus 5.5 subagent, read-only, in a detached worktree, and used
≈ 0.06 core-h. It reproduced with its own code:

- the IBU (with the known term and a zero-efficiency cell);
- Fisher, CR widths, null fractions and the invisible share;
- the T2 edges and the J map against the committed rows;
- the B count against `branch_outcome` (3,000 trials);
- end-to-end A, B (`tracks` and `departs`) and C cases through the library functions.

It found no numerical disagreement. It confirmed:

- AM-1: asimov_same is background-free;
- AM-3, AM-11, AM-12 and AM-14;
- that the study-K weights match;
- that the driver can neither fit nor extend s5p;
- that no threshold, grid, departure, iteration limit or aggregation changed.

It judged the CPU cap credible, with an overrun of at most ≈ 14 s. It judged the branch-B route
adequately specified once M2 is fixed.

| # | severity | finding | disposition (one repair batch, commit after `9203add1`) |
|---|---|---|---|
| M1 | MATERIAL | the H2 rows are stacked twice (217 rows), so the real 185-column traces fail A4; the fixture traces were derived from the driver's own list | **fixed:** the committed rows are used as returned. A4 now also checks they equal a list built from the operands. The test builds the name list independently and writes the end-to-end traces in that 185-column layout |
| M2 | MATERIAL | B convergence is judged per run, but §6 says per functional; one slow cell makes B unreachable | **fixed prospectively, AM-26**: per-functional last-step criterion, run-level flag kept; decoupled-slow-block control |
| M3 | MATERIAL | RAM cap unenforced; trajectories retain their operands; row count understated; generic exceptions lose the decision | **fixed, AM-32**: RSS guard; only K and r retained; row arrays freed; chunked binning; per-stage error capture with the decision always written; memory re-measured at 4 M and 8 M rows (§7) |
| m1 | MINOR | A8 in-grid rule differs from the producer's | **fixed, AM-27** |
| m2 | MINOR | B-undeclarable even when unreachable | **fixed, AM-29** |
| m3 | MINOR | W2's comparator is background-inclusive | **fixed, AM-30** and §5 |
| m4 | MINOR | AM-2's premise not gated | **fixed, AM-28** (A11) |
| m5 | MINOR | AM-15 and AM-24 described inaccurately | **fixed** (wording) |
| m6 | MINOR | C does not say why σ = ∞ | **fixed, AM-31** |

The session's one focused re-review is used on this batch.

## 9. Stage B results

**Released** by the admission re-review (ADMIT at `0e32c018`). The inputs and the resource checks
were verified, so no further permission was needed.

- **Inputs:**
  - one read-only `scp -p` copy (2026-10-10T05:41:59–05:44:21Z) into dated scratch, of the event
    file plus 27 comparator products;
  - digests, sources and the MC members' array headers are in
    [`outputs/input-manifest.json`](outputs/input-manifest.json);
  - the real-data members were never opened.
- **Run:** one attempt of the driver at `0e32c018`, local, two threads (record:
  [`outputs/run-record.json`](outputs/run-record.json)).
  - 2026-10-10T05:44:48–06:34:27Z, exit 0, all five stages complete.
  - **2,900.7 CPU-s = 0.806 core-h**, peak RSS **4.65 GB**.
- **Outputs (result commit `d03a2c72`):**
  - [`outputs/results.json`](outputs/results.json): admission, controls, convergence, the decision
    with per-functional labels, and summaries;
  - [`outputs/tables.npz`](outputs/tables.npz): every per-functional array — trajectories, widths,
    null fractions, acceptance holes, invisible shares, missed fractions, r_IBU(∞) with
    per-functional convergence, and the secondaries.
  - No cell is selected; the decision uses all 175 reported functionals.

### 9.1 Admission and controls (all passed)

The events file has 32,849,103 MC rows, all truth-passing. 20,402,110 signal pair rows equal s5e
`rows_eligible`. The 2,801 out-of-grid truth rows are exactly the −9999 sentinels, and every reweight
is exactly 1 on them (A11).

| check | result |
|---|---|
| A1 event digest | `07fccc1a…` |
| A2 records, A3 ratio files, A4 traces / names / inputs | equal to config |
| A5 committed reweights vs each comparator's own truths (15 products) | ≤ 3.6e-15 relative |
| A6 receipt-limited prefixes vs the stage-2 per-K medians (8 traces) | deviation 0, 0 NaN medians; K = 40/30/40/200 of 100/100/125/200 present |
| A7 reco cells; S_dep; GBDT fold λ_5D | 10,499; 92,363.627 / 92,244.780; λ_5D at K = 5/15/30 = 367.69/237.82/163.69 (GiBUU) and 1260.29/1031.03/987.04 (q3), equal to the receipt; my fold equals the s5e file exactly |
| A9 edges | exact |
| C1 nominal control, T1/T2/T3 | max \|r_IBU\| 1.7e-13 / 9.8e-14 / 7.7e-14 |
| C2 exactness at T1 (gating), nine weight sets | all pass; worst error 1.5e-8 σ_c on 54–56 identified functionals (q3 at 10⁵ iterations without run-level convergence, within tolerance) |
| C2 at T2 (reported) | every identified functional (10–12 per set) within 0.0012 σ_c |
| split key (AM-11) | reproduced bitwise; halves 16,429,553 / 16,419,550 rows |

**Grids actually occupied:** T1 has 134 non-empty J cells, T2 1,383 (of ≤ 5,184) and T3 10,694 fine
cells. T2 has 12 zero-efficiency cells (acceptance holes).

### 9.2 The frozen outcome

Primary setting: T2, same-sample, nominal-weighted, K = 5, pooled over GiBUU, W1, W3, q3 and W2.

| map | functionals with \|r_GBDT\| > 2% | resolution-sensitive (excluded) | eligible | C | A | B | outcome | without W2 (AM-30) |
|---|---:|---:|---:|---:|---:|---:|---|---|
| J | 376 | 232 | 144 | 0.840 | 0.014 | 0.000 | **C** | C (134; C 0.828, A 0.015) |
| EW | 152 | 129 | 23 | 0.870 | 0.000 | 0.130 | **C** | C (19; C 0.895, B 0.105) |
| H2 | 66 | 63 | 3 | 1.000 | 0 | 0 | **C** | C (3) |

- Every departure, taken alone, also gives C wherever it has an eligible functional; H2 has none for
  W1, W2 or W3. No tie occurred.
- `all_three_sets_small` is false. No B candidate was blocked by non-convergence.
- EW's three B-counted functionals are GiBUU EW40 and W1 EW40, both reading `tracks`
  (r_GBDT/r_IBU at K = 40: −7.2/−6.7% and −3.3/−3.0%), and W2 EW19 (`untraced`).
- **Bookkeeping (missed-event concentration) is implicated for no departure or map:** the top-tercile
  share is 0.16–0.61 against the 2/3 rule. This is descriptive (§5).

### 9.3 What the frozen outcome rests on (descriptive reading of the full tables)

- **Population.** The branch shares cover only the *resolution-stable* functionals:
  - J keeps 38% of its > 2% residual population, EW 15% and H2 5%.
  - The rest change label between T1 and T2, mostly, or between weightings, and count toward no
    branch. Nothing is claimed about them.
  - H2's C rests on 3 functionals, 2 of them acceptance holes, so it is **effectively
    uninformative**. EW's rests on 23, 4 of them acceptance holes. **J carries the result:** 121
    C-counted functionals, 4 of them acceptance holes.
- **Identifiability of the C-counted J functionals.** Their binned CR width at the analysis exposure
  has a median of **31% at T1** (minimum 10.5%) and **58% at T2**, against a median |r_GBDT(5)| of
  14%.
  - Because the label is stable across T1 and T2 and across both weightings, the width exceeds 10%
    even at the coarser, optimistic truth resolution.
  - For all reported J functionals the T1 median is 11–13%. The T2 median is 24–26%, and EW and H2
    widen from ≈ 2.5–3.5% at T1 to ≈ 20–30% at T2: the coarse grid hides within-cell freedom.
  - Leaving out the acceptance-hole (σ = ∞) functionals, the C share is J 0.812, EW 0.696 and H2
    0.333 (verification). J and EW stay C on finite widths alone. H2 does not, so its C is an
    acceptance gap.
- **Iteration behaviour.**
  - Of the 144 eligible J functionals, 104 are iteration-faithful at K = 5, 15 are
    approximation-dominated (2 of them identified, the A share) and 25 mixed.
  - The J medians of |r| at K = 5 agree:

    | | GiBUU | W1 | W3 | q3 |
    |---|---:|---:|---:|---:|
    | GBDT | 9.5% | 5.4% | 5.6% | 4.3% |
    | exact T2 IBU | 8.3% | 5.4% | 4.9% | 5.3% |
    | fine-grid IBU | 8.6% | 5.6% | 5.0% | 4.0% |

  - At K = 5 the GBDT leaves about the residual an exact binned response iteration leaves.
- **Longer exact iteration (noise-free, nominal-weighted T2).** The J median |r_IBU| at K = 200 and
  after 10⁵ iterations:

  | | K = 200 | 10⁵ iterations |
  |---|---:|---:|
  | GiBUU | 3.3% | 0.8% |
  | W1 | 3.3% | 2.8% |
  | W3 | 4.4% | 8.9% |
  | q3 | 6.6% | 6.7% |

  - For W3 and q3, the within-cell binning bias grows with K (median 2.8% and 4.2% at K = 200).
  - Among the C-counted J functionals, |r_IBU(10⁵)|/|r_GBDT(5)| has a median of 0.35 (70 of 121 at
    or below 0.5), but only 12 of them meet the per-functional convergence criterion.
  - The T2 runs reach 10⁵ iterations with a run-level change of 2e-4 to 7e-3 per step. The
    signature is cells driven toward zero, a maximum on the boundary of the positive orthant.
- **Visibility.** Where a fine-grid GBDT estimate exists (GiBUU and q3 at K = 30, W3 at K = 200), the
  median invisible share of the C-counted J functionals' GBDT residual is 0.61. EW gives 0.98, but
  on only 13.
- **Secondaries.** Signal-only pseudo-experiments (D3) and capacity 400/31 are close to the B0 traces;
  missed events at w = 1 is worse:

  | J median at K = 5 | GiBUU (E_avail) | q3 | W3 |
  |---|---:|---:|---:|
  | D3 signal-only pseudo | 9.2% | 4.4% | — |
  | B0 noise-free trace | 9.5% | 4.3% | — |
  | capacity 400/31 at K = 5 / 10 | 9.2 / 8.7% | 3.9 / 3.5% | 5.0 / 4.4% |
  | missed events at w = 1 | 10.5% | — | — |

- **P1r–P3r** (no vote) look like their historical counterparts:
  - P1r is like W3: J median r_IBU at T2, K = 5 is 5.5%, binning bias 1.1%;
  - P3r is like W2: 0.6%;
  - P2r: 2.5%;
  - their T1 J widths are 11.4–13.0%.

## 10. Final numerical verification

**PASS** (record: [`verification.md`](verification.md)). The same fresh reviewer, read-only, worked
from the real inputs at the result commit `d03a2c72` with its own code. It imported only the committed
reweight/extraction/functional code and `comparator.py`, never `did.py`.

Reproduced:

- the row and cell counts, S_dep and the nominal control;
- r_IBU per functional at T2 for K = 5 (all six sets, ≤ 3.1e-15) and K = 40 (GiBUU, 1e-14);
- the CR widths at T1 and T2 for both weightings (≤ 1.7e-11), with identical infinity and
  acceptance-hole patterns;
- r_GBDT(5) exactly;
- every label and sensitivity flag (0 mismatches);
- r_IBU(∞) (≤ 1.2e-12) and the per-functional convergence flags (0 mismatches);
- the EW B set and its trace readings;
- the three pooled branch outcomes, with and without W2, exactly.

Not reproduced: T3 and split-half trajectories, invisible shares, missed-event concentration, the T1
exactness control and P1r–P3r. None of these decides a branch.

Its interpretive points are carried into §9.3 and §11:

- the resolution-sensitive exclusions;
- the acceptance-hole share of C, which makes H2 uninformative;
- an H2 rounding nit.

It used ≈ 0.23 core-h, ≤ 2 threads and a peak RSS of 4.15 GB. It was interrupted once by an API
session limit and resumed from its own scratch.

## 11. Disposition

| decision | verdict | reason |
|---|---|---|
| implementation | **PASS** | §6 implemented as a digest-pinned driver that reuses the committed code. 29 synthetic controls pass. The three material defects the admission review found (one would have stopped the run at A4) were repaired before any real input was opened. The one run completed every stage, and verification found no defect |
| admission | **PASS** | ADMIT-WITH-REPAIRS at `9203add1`, then ADMIT at `0e32c018` on the session's one focused re-review |
| numerical verification | **PASS** | §10: the consequential reductions and all branch outcomes were reproduced independently with no disagreement |
| discriminating question | **PASS**, within the scope below | stages 1–3 complete, every gate passed, and J returns a declared branch: **C** |

**Supported diagnostic outcome (frozen rules): branch C in J, EW and H2.**

- **J** (121 of 144 eligible; 117 with finite widths): the label-stable residuals sit in functionals
  that are weakly identified **for binned estimators**. At this reco binning and the analysis exposure
  their CR widths are > 10% at both truth resolutions (median 31% at T1, 58% at T2), signal-only.
- **EW**: the same on 23 eligible.
- **H2**: an acceptance gap on 3 functionals, not evidence of a weak response.

**What the evidence says about the three mechanisms.**

- **Finite-iteration regularization: consistent, and dominant at K = 5.** On the J map 72% of the
  eligible functionals are iteration-faithful, and the GBDT's median residual equals exact binned and
  fine-grid IBU's at K = 5. Noise-free, longer exact iteration removes much of it for GiBUU and W1.
  The functionals concerned carry > 10% binned CR widths, so the regularization trades a large
  variance for the bias observed. This is consistent with E1, where the GBDT's repeat SD was
  0.26–0.43%.
- **GBDT approximation or bookkeeping: not supported as the main cause.** It is approximation-dominated
  for 15 of 144 eligible J functionals, and only 2 of them are identified, which is the A share of
  0.014. Missed-event concentration is never implicated (descriptive). This does not contradict E6's
  reco-level q3 stall: that is a fold-χ² statement, and its effect on the reported functionals was
  already small.
- **Weakly constrained response directions: supported for the label-stable J and EW functionals,**
  within the scope below.
- **Inconclusive by construction for the rest.** 62% of J's > 2% residuals, 85% of EW's and 95% of
  H2's are resolution-sensitive, so the frozen rules assign no mechanism to them. The widths roughly
  double between T1 and T2, so the identifiability of those functionals depends on the truth
  resolution, which is exactly why they are excluded.
- **Branch B: not supported in J** (share 0, and no candidate was blocked by non-convergence). In EW
  the share is 0.13, and the existing traces read `tracks` for GiBUU and W1 EW40. This permits no
  further claim and is not an instruction to iterate.

**Limits that travel with this outcome.**

- **Fisher widths.** They are local, binned, model- and grid-dependent and signal-only (optimistic:
  no background variance). Unbinned information is not bounded by them. Neither T1 nor T2 bounds the
  truth.
- **What C means.** C is a quantified no-go for the *present binned-precision expectation* on the
  label-stable J functionals. It is not an impossibility theorem, and it does not exclude estimators
  that use prior information.
- **Convergence.** The T2 runs do not converge at run level: cells are driven toward zero. Per
  functional only 9–34 of 109 J functionals converge for the traced departures. So "exact iteration
  removes the residual noise-free" statements rest on last iterates.
- **Inputs and comparators.**
  - The departures are historical development truths, with no untouched departure. P1r–P3r have no
    comparator.
  - W2's comparator is the R ensemble, but the outcome is unchanged without it.
  - The GBDT comparators are B0 capacity, receipt-limited prefixes, and were not extended.
- **Review independence.** The reviewer was a Claude subagent of the same model family; there was no
  cross-provider review.
- **Simulation only.** The outcome is conditional on the fixed detector response. It does not validate
  an interval, does not address the 2D pairing problem, and does not make the joint-5D measurement
  publication-ready.

## 12. Next decision

**Exactly one, for Joseph: the endpoint-scope decision of gbdt §10.3.** Should the scalar-5D
endpoint move from J cells to identified functionals? That would authorize I2's first, MC-only stage:
select and freeze, before any data result, functionals or response-derived combinations with
σ_c ≤ 2.5% at T2, then evaluate the existing GBDT products on them as a local reduction (gbdt §7,
2–10 CPU core-h). The alternative is to record the J-cell joint endpoint as a binned no-go and stop.

- **Inputs to the decision.**
  - At T2 only 5 of 109 J, 3 of 39 EW and 2 of 27 H2 functionals are identified at target (T1: 22–24
    J), so I2 would need wide combinations, not the present maps.
  - The strict-bounds benchmark has an unpriced solver dependency (gbdt §7).
  - Any outcome stays simulation-only.
- **What branch C does not authorize.** It motivates this decision; it authorizes nothing. I1 (branch
  A) is not justified. Branch-B extension of s5p study K is not indicated, and would in any case need
  its own authorization.
- **Integration (not done here).** `generate_manifest.py` must regenerate once at integration for this
  directory's new files (`REPORT.md` has its pre-registered override row). `verify_hash_bindings.py`'s
  pinned inventory is unchanged by design (AM-25).
