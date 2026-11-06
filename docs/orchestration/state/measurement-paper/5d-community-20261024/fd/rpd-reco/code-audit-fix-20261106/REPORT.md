# RPD-RECO: audit repairs and the constrained-MAT boundary

This packet repairs the code reviewed at `10731ed3` in draft PR #848. It does not supply Binding 2, a P0 go, a production result, or a publication claim. The governing recipe is `FD-RPD-RECO-DECLARATION.md` revision 2, with Binding 1 addendum A1 (merged in #854). The director's measured-price and custody rulings are preserved verbatim beside this report.

Owner: Codex2, local code and fixtures only. Reviewer: coverage-5b-audit through the director; the director retains the merge and execution decisions. The decision is whether this code implements the bound reconstruction-level recipe. The terminal condition for this lane is passing local tests and required mutants, committed receipts, and a pushed draft PR. The review budget is one consolidated delta audit plus repairs to concrete blockers. No scientific sampling, cluster contact, or new campaign is authorized for this lane.

## Output refusal and measured price

The resolved CFS refusal is the first check in `main`, and it runs again in the error handler before any directory or STOP receipt can be written. `run_stage` and `Inputs` also guard entry. Tests combine CFS with THREADS, NICE, dry-run, and existing-output refusals and intercept both `mkdir` and `open`. Mutants move the first check late or remove the handler recheck. The older packet's unconditional claim about STOP receipts is explicitly withdrawn in its REPORT.

`--priced-wall-seconds N` and `--measured-seconds-per-draw S` are paired. N must be positive and at most 165,600 seconds (46 hours), under Joseph's merged #851 decision. A measured run requires the pinned timing record, all 23 actual axes, 65,536 rows, 200 bootstrap replicas, five variants, a real-signal pass, and the matching numerical environment. Each step plans its own draws times S times 1.5; an estimate above N refuses PRICE_REVIEW. Without the pair, the previous Poisson probe, factor 10, and 7,200-second limit remain. Every PASS/STOP records the request, effective budget, rate/source, estimate or its explicit absence, and scheduler request fields when present. This packet chooses no N. Streams, row order, single-thread execution and the indivisible C-0 invocation remain as bound.

## Flux evaluation under A1

The MAT-only extract calls the analysis's string constructor for `minervame1D`, `minervame1M`, and `minervame1N`, with PDG 14, the nu-e constraint, gen2thin, g4numiv6 and 100 universes. `GetFluxReweighted(14)` supplies the constrained phi; `GetFluxGenerated(14)` supplies the row's own MC generation spectrum.

ROOT evaluates every passing row's flux values. It interpolates at E <= 75 GeV and uses bin contents above 75. With w(n,g) = 1 if either argument is zero, otherwise n/g, the factor is w(phi_target,g_own) / w(phi_own,g_own). Full-row products preserve the original signal digest and row count, including rows of zero weight. All eight zero combinations have counts and pass_reco weight shares. Out-of-range factors remain unity, with the existing 0.1% primary-weight refusal unchanged. Tests discriminate interpolation from bins, both sides and exactly 75, and every zero combination, with required mutants.

The background bracket integrates the constrained CV densities over their common range. Raw-file integrals are recorded under `raw_file_integral_descriptive_only` and are read by no scorer.

The numerical environment never evaluates a ROOT flux histogram. P0 reads only a pinned extraction JSON, individually pinned row-factor products, and a separately pinned passing syscall custody receipt. It checks producer, custody-code, selection and MC identities. It records the actual interpreter, resolved interpreter, Python, NumPy, SciPy and uproot versions. The named production numerical environment is in the DRAFT config, from the merged timing receipt; it is distinct from the pinned MAT/root_6_28 extraction environment.

## P-F's shared convention is measured

The source premise concerns the constrained numerator and fixed own-MC generated denominator. It does not establish an absolute POT or energy-density normalization. P0 separately measures:

- identical constrained-phi and generated-flux bin edges, with absolute tolerance 1e-12;
- byte-equal constrained-phi histogram title, x/y axis titles, and available file units metadata, within the same gen2thin/rearranged production family.

A difference refuses before any swap. STOP details retain both observed strings and the compared edges. Each measurement has firing/silent tests and a required mutant. Their conjunction with the generated-flux source premise is the recorded P-F result; the DRAFT config supplies no precomputed result.

The extract records textual unit/POT metadata if present for the staged ROOT dependencies. The optional descriptive ALL integral check is explicitly SKIPPED because this extract does not call `GetIntegratedFluxReweighted` for the exposure-weighted ALL combination. It records the analysis's 6.243e-8 cm^-2 per POT beside that status, citing `docs/analysis-note/paper_body.tex:27`, `sec_method.tex:187`, and their provenance route `README-gen5d-fluxfix.md:43-49,74`. That value occurs in the paper prose, not a located values macro. The descriptive field gates nothing and is read by no numerical step.

## Fresh staging and native custody

The source-routed inventory has exactly fifteen dependencies: twelve +/-14 flux files, lowNuReweight.root, Muon_Energy_MnvH1D.root and the MPARAMFILES constraint text. The director reviewed those names at `d3d379d3`. Runtime stat/digest checks and the syscall trace remain decisive.

The connect checks the six pinned setup scripts before sourcing the existing setup route. It restores TMPDIR afterwards. Prepare runs the existing MAT environment instrument before tracing, records checked instrument copies and source stats, checks the COV2D queue and the two named terminal jobs, and stages the original constraint fresh through O_NOATIME. It does not reuse COV2D, RPD or REF copies. A changed source fingerprint or atime refuses.

The traced extract verifies the same run/connect, fresh prepare receipt, recorded environment, MnvH1D dictionary, mapped MAT libraries and their dev/inode/size. It checks staged instrument digests and all staged data dependencies. Only PLOTUTILSROOT and MPARAMFILES data lookups are temporarily redirected; both are restored, including on exceptions. Loaded MAT libraries stay pinned.

Any attempted open under a protected original data/input root, including ENOENT or the original FluxReweighter source, refuses. Successful opens need exactly one disposition: staged data, pinned MAT libraries, the explicitly reviewed environment/ROOT paths, system paths, or the run directory. Unclassified successes refuse. Failed searches outside protected roots are counted by prefix and allowed. Relative paths require an identified directory, and a cwd change refuses. The environment is preserved after setup; credential fields and URL credentials are redacted. Every imported module's on-disk origin is recorded.

The connect first withholds one own staged dependency, requires a traced MAT_DATA_STAGE refusal, checks its trace, and restores the copy. It then runs the positive extraction and writes a passing custody receipt only after the trace check. A failed trace cannot be supplied to numerical P0 as a PASS handoff.

## Local verification and remaining run-lane gates

At frozen code head `d9740563f014c1642546edf314559887003b9920`, the final suite passed **134 tests in 216.92 s**, and the harness printed **130 required, 130 executed, 130 killed, all_killed true** (both exit 0). Black, Ruff, strict mypy and shell syntax passed. `VERIFICATION.json`, `SUITE.txt` and `MUTATIONS.{json,txt}` bind that head, executable blobs and printed runner counts. `LOCAL-DRY-RUN.json` contains two local pins/P0 fixture runs with all twelve stat-only nn siblings and no measured-key access. `IMPORT-CLOSURE.json` distinguishes exercised numerical imports from static-only MAT/custody boundary files; `OPEN-CLOSURE.tsv` gives a disposition for every source-open hit. `SOURCE-SHA256SUMS` and `SHA256SUMS` bind source and packet files.

The local positive I/O fixtures use an explicitly labeled O_NONBLOCK stand-in on macOS. They do not clear native Linux O_NOATIME. Synthetic ROOT protocol and custody fixtures do not clear the real MnvH1D, constrained-constructor, native redirect or syscall gates. The separate native CLI probe records the expected local NOATIME refusal.

The run lane must execute the real non-input MnvH1D check and the cold staged connect at the frozen PR code head, return their exact environment/trace/custody receipts, and retain the originals' stat/atime records. `production-config.draft.json` remains DRAFT: runtime paths, reviewed trace classes, source-premise acceptance, retention and extract/custody digests need completion and audit. All eight C-N rows remain CANDIDATE_NOT_RUNTIME_SELECTED; the proposed three choices add nothing beyond the declaration and A1. No Binding 2 or P0 permission is inferred from local test success.
