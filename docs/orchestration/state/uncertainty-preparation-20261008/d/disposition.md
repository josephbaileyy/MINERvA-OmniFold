# Lane D — repository comprehensibility: inventory and dispositions

Base `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c`, branch `prep/uncertainty-d-navigation-20261008`,
worktree `MINERvA-OmniFold-uncprep-d-20261008`. Plan: `docs/orchestration/PLAN-20261008-uncertainty-investigation-preparation.md`
(blob `fbbc0d65`). The measured graph is in [`dependencies.tsv`](dependencies.tsv). This record is
preparation evidence. It grants no compute and changes no gate, adoption or publication scope.

## Ownership (inventory commit)

**D writes only these paths:**

| Path | Status at inventory |
|---|---|
| `README.md` | D; planned edit (routing) |
| `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` | D; planned edit (routing and the bootstrap seed instruction, after A's factual check) |
| `docs/POST_PUBLICATION_REORG_PLAN.md` | D; planned edit (deferred-move designs) |
| `P/d/dependencies.tsv`, `P/d/disposition.md` | D |
| one existing workstream README | **none claimed.** If one is claimed later, it is named in this table in a commit before the edit |

**Source files.** D claims **none** of A's five conditional 2D paths and proposes **no transfer** at
this inventory:
`2d-unfolding/unfold_2d_omnifold_unbinned.py`, `2d-unfolding/uq/analyze_uq.py`,
`2d-unfolding/uq/analyze_universes.py`, `2d-unfolding/uq/rollup_vl170_adoption.sh`,
`2d-unfolding/tests/test_bootstrap_completeness_ki84.py`. All five stay released to A. D's
structural-code allowance (at most two non-frozen files) is unused. Any later use needs an exact
transfer recorded both here and in `P/a/verification.md`.

**Caller constraints for A** (measured, see `dependencies.tsv`):
- The driver has 47 importers (`import unfold_2d_omnifold_unbinned as u2d`). The most-used names are
  `PT_EDGES`, `PZ_EDGES`, `refine_stay_positive`, `MAX_MUON_THETA_RAD`, `get_pot_scales`,
  `in_truth_phase_space`, `load_flux_bins` and `TRACKER_FIDUCIAL_N_NUCLEONS`. A rename or a signature
  change to any of them reaches the 3D and N-D drivers, PET and one note figure script.
- The driver's rooted insert must stay inside `main()`, and `unbinned_unfolding/python/omnifold.py`
  must keep its digest (`test_oi136_rooted_insert_ratchet.py`). Its two current-bytes pins
  (`8ebe0277…`, in the negweight receipt and the Gate-2 launcher) are already broken by KI-84 and
  listed `KNOWN_PREEXISTING`; a further edit does not change that status and does not re-pin anything.
- `analyze_universes.py` is pinned only at revision `901f2c64` (`test_hash_bindings.py:701`), so an
  edit to its current bytes does not break that test.
- `compare_to_paper_fullcov.py` is not one of A's paths. It is a publication figure producer (its
  digest is recorded in `publication/release/figs/_data/fig_arrays.npz.manifest.json`).
- The reported-bin mask is computed four ways from four operands (row D01). A change to how
  `analyze_uq.py` or `analyze_universes.py` chooses reported bins reaches
  `compare_to_paper_fullcov.py`'s ordinal alignment, which checks only the count.

**Not D's:** A–C and E surfaces in the plan's writer table; `docs/analysis-note/`,
`publication/release/`, `docs/publication/corrections-20261008/`; `MANIFEST.tsv`,
`MANIFEST-overrides.tsv`, `CATALOG.md`; `AGENTS.md`; frozen receipts; generated views.

**Path recheck before the first edit** (2026-10-09T06:14Z): no other worktree's uncommitted edits or
live branch deltas touch D's three existing paths. E's dispatch snapshot found none, and
`git fetch origin` showed only `prep/uncertainty-e-20261008` among the lane branches. Older remote
branches differ from the base on `README.md` only because `main` moved past them; none is a live
edit.

## Supported entry points (2D, immediate)

See the `entry` rows E01–E06. Each is either a frozen reproduction (its outputs are pinned
products) or a prospective run, never both:

| Task | Entry point | Kind |
|---|---|---|
| Event loop and merge | `sbatch_evloop_array.sh` → `sbatch_hadd_MEFHC.sh` | prospective |
| Central value | `sbatch_unfold_2d_MEFHC.sh` → `unfold_2d_omnifold_unbinned.py` | frozen reproduction; the product's backend label is open (row D06, A) |
| Statistical replicas (VL170) | `state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh` | frozen reproduction (record) |
| Systematic universes | `sbatch_unfold_2d_MEFHC_5iter_universes_full{,_CV}.sh` | frozen reproduction |
| Active combined rollup (VL172) | `uq/rollup_vl170_adoption.sh` | frozen reproduction |
| Paper comparison | `compare_to_paper_fullcov.py` | deterministic re-evaluation |

## Ranked obstacles and dispositions

Ranked by their effect on estimator tracing, independent-validation design and supported
reproduction, and by the strength of the evidence. There are five, the maximum.

| # | Obstacle | Evidence | Disposition |
|---|---|---|---|
| O1 | The 2D reference sent readers to superseded uncertainty producers. Its rollup bullet named `sbatch_final_rollup_full.sh`, whose universe step reads the pre-fluxfix sweep. Its Fig. 6/7 path named that route's output directory. Its "Driver" was the interactive script. It never mentioned `VL170`, the replica record or `uq/rollup_vl170_adoption.sh` (0 hits). | rows N06, N07, N11; `rollup_vl170_adoption.sh:6-7`; `nav-before.txt` T1/T2 | **IMPLEMENTED** (I1 `abc1e6f7`, I3 `bd738973`). The reference has a producer table that says what each row reads and writes, that every row is a record of how a pinned product was made rather than a prospective command, and how each row guards against overwriting, and the old route is marked superseded. README routes there from "Where to start" and Setup step 6. |
| O2 | The reference's bootstrap item 4 told each replica to pass `--seed N`. Every band producer passes a fixed `--seed 1`, and the scaleup header records that varying both double-counted ML stochasticity. | row D05; six launchers measured; `scaleup.sh:18-19` | **IMPLEMENTED** (I2 `00803510`). **Confirmed by A's CONTRACT** (`acb338a2`, ASSESSMENT rows `E_S`, `E_U`, `E_ML`): `VL170` is LightGBM with `--seed 1` and `--bootstrap-seed b`, b = 1…300; the universes use `--seed 42`. |
| O3 | The frozen central value's backend is labeled inconsistently. The status headline says "MEFHC 5-iter lgbm", but the launcher that writes the frozen path passes no `--estimator` (driver default `exact`). `final_rollup_full.sh` (c) comments "using the exact-GBT production CV here". | row D06 | **RESOLVED by A for D's purposes.** A's CONTRACT (`acb338a2`, row `E_C`) records sklearn exact-split `GradientBoosting` with `random_state=None` for `142a45b0…`, by launcher, revision and wall-time signature. A notes that the executed-bytes origin is unavailable. The reference now states this and routes to A's assessment (the FREEZE commit). **For E:** the status headline's "MEFHC 5-iter lgbm" label is E's to correct. |
| O4 | The 205-bin reported mask is computed four ways from four operands (`analyze_uq.py`: ensemble mean > 0; `analyze_universes.py`: CV > 0; `compare_to_paper_fullcov.py`: paper diagonal > 0; Fig. 6/7: central > 0). The comparison aligns the matrices by ordinal position and checks only the count. Today the cells coincide, so no number is wrong. A future ensemble with one zero-mean reported bin and one extra nonzero cell would misalign every element silently. The 3D analogue `build_bootstrap_cov_3d.py` already takes its mask from the CV, the same operand as its universe rollup. | row D01; `compare_to_paper_fullcov.py:148-159`; `build_bootstrap_cov_3d.py:11-13,84` | **DEFERRED patch design** (below). Two of the files are A's conditional paths and the third is a publication figure producer, so D edits none of them. |
| O5 | `3d-unfolding/genie/gen5d_*` and `run_gen5d_supplement.sh` are the s5p 5D predictor family, in a 3D directory beside 3D generator code. | row N14; `reproduction/s5p/scope.py` `PRODUCER_FILES` | **Routing IMPLEMENTED** in README (I3). **Move DEFERRED**, with a full design in `docs/POST_PUBLICATION_REORG_PLAN.md`, "Uncertainty preparation, lane D". The recommendation is not to move. |

Implemented improvements: three (I1, I2, I3), all documentation. **No source file was edited**,
so D's two-file structural allowance is unused and no ownership transfer happened.

### O4 deferred patch design (for A, or the publication owner for `compare_to_paper_fullcov.py`)

- **Change.** Make each covariance carry its reported-cell identity, not just its size.
  - `analyze_uq.py` and `analyze_universes.py` already write `hCov2D_reported`. Next to it, each
    writes a `TH2D`/`TH1D` mask of the 224-cell grid, or the flat indices.
  - `compare_to_paper_fullcov.py:load_omnifold_cov` refuses when the stored indices differ from the
    paper mask's `np.where(reported_mask)[0]`. If an input has no stored mask, it falls back to the
    current count check and prints a warning.
  - Alternatively, `analyze_uq.py` takes a `--cv` and builds its mask from the CV, as the 3D builder does.
- **Behavior contract.** On today's inputs the four masks coincide, so every output must be identical
  bit for bit: `hCov2D_reported`, `hCov_combined`, the χ² logs and the Fig. 6/7 summary. The only
  addition is the stored mask object.
- **Verification.**
  - Run the VL172 rollup's controls from `rollup_vl170_adoption.sh` on frozen inputs (Perlmutter,
    login-node-safe: about minutes of CPU, no training). Require numerically identical logs and
    covariance arrays, with a declared tolerance of 0 (same code path).
  - Add a synthetic negative control: shift one reported cell, which must be refused.
  - Run `test_bootstrap_completeness_ki84.py`.
  - Record the producer digest in `fig_arrays.npz.manifest.json`, and note that it changes.
- **Why deferred.**
  - The files belong to A (two) or are a publication input (one).
  - The required equivalence run needs the frozen ROOT inputs on Perlmutter, which this lane does not
    run.
  - The hazard is latent, not live.

## Before and after: the four navigation tasks

Logs: [`nav-before.txt`](nav-before.txt) (base docs) and [`nav-after.txt`](nav-after.txt) (head docs).
A reader starts from `README.md`.

| Task | Before (`f8e2bf85`) | After |
|---|---|---|
| T1 Find the adopted statistical producer | The README has no 2D uncertainty route. The reference's only "Driver" is `uq/run_bootstrap_interactive.sh`, which did not make the quoted replicas, and the reference never mentions `VL170`, KI-84 or the replica record (0 hits). Reachable only through `AGENTS.md` → `KNOWN_ISSUES.md` 84 → a receipt directory listing. | README "Where to start" row (line 30) → reference table row "Statistical replicas (`VL170`)" → `state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh` (`--seed 1`, `--bootstrap-seed N`) → `analyze_uq.py` in the rollup. Two hops, both named. |
| T2 Find the active combined rollup | The reference names `sbatch_final_rollup_full.sh` (superseded). Only the ledger and the plan mention `rollup_vl170_adoption.sh`. | Reference table "Combined rollup (`VL172`)" and the universe-workflow bullet both name `uq/rollup_vl170_adoption.sh`, with its inputs, outputs and digests file. README Setup step 6 points there. |
| T3 Find the supported import constraints | Reachable from README "Before changing the 2D driver" (one hop). The reference's driver contract does not mention the constraint (0 hits). | Unchanged in README. The reference's driver contract now opens with the constraint and routes to the ruling (`AUTHORIZATION-20260903-oi136-failopen-repair.md:41`, verified), the ratchet test and `mnv_guarded_run.py`. |
| T4 Recover a historical evidence path through the correct tag | Works through README → reorg plan or `CATALOG.md`, but README names only the 2026-08-20 tag. The A3 path tried at that tag fails (`rc=128`). | README names all three removal-boundary tags and how to pick one. `git show evidence/simplification-2026-10-07-fc97eaf9:nd-unfolding/pet/final_design/results/dev1/dev1-CS1-F0.posthoc.json` gives sha256 `d6d09e6f…`, equal to the external epoch's `a3-blobs.tsv`. The reference's archive citation `evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:441` resolves (Phase-16 heading). |

## Checks

All checks ran locally (macOS, Python 3.12.2), with `TMPDIR=/private/tmp/minerva-uncprep-d-20261008/tmp`
and a four-thread cap.

| Check | Result |
|---|---|
| pre-commit hook (shared `.githooks`) on each of D's commits | 13 checks passed, every commit |
| `python3 docs/orchestration/verify_hash_bindings.py` at D's head | rc 0, ALL BINDINGS INTACT ([`verify_hash_bindings.txt`](verify_hash_bindings.txt)) |
| `python3 -m pytest -q nd-unfolding/tests/test_hash_bindings.py` (inspected first: verifier subprocesses and synthetic temp repos only) | 33 passed, 0 skipped ([`test_hash_bindings.txt`](test_hash_bindings.txt)). It pins `2D_OMNIFOLD_REFERENCE.md` and `analyze_universes.py` at revision `901f2c64`, not at current bytes |
| Paths in D's added lines resolve | 68 resolved. The 26 unresolved occurrences are bare basenames of files named in full nearby, untracked cluster product directories (by design), two formulas, and the proposed destination `nd-unfolding/gen5d` ([`pathcheck.txt`](pathcheck.txt)) |
| `generate_manifest.py --check` | not run: already OUT OF DATE at the pin (E-C1). No lane regenerates it, and D's three paths are not in `MANIFEST.tsv` rows that D may touch |
| Code equivalence | not applicable: no source file changed |
| Document builds | not applicable: no `docs/analysis-note/` input changed |

The `final_rollup_full.sh`, rollup and driver statements in the reference were each checked against
the script text at the base (line citations in `dependencies.tsv`). No product was opened. The
products are on Perlmutter, and D read none of them.

## For A — factual-check requests and their answers

D's three requests are answered by A's CONTRACT commit `acb338a2`
(`docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md`) and read at
`origin/prep/uncertainty-a-pairing-20261008` (`971fc00c`), 2026-10-09T06:56Z. `P/a/verification.md`
did not exist there yet. D polled for it for 30 minutes (06:25–06:55Z) and then used the assessment.
1. I2, the bootstrap seeds: **confirmed** (rows `E_S`, `E_U`). A also reads the pilot log, which prints
   `Pinned GBDT seeds: 1/2/3` at checkout `bb4b0b6f`.
2. I1, the producer table: the replica launcher, the `uq/universe_sweep_fluxfix/` sweep, the matched CV
   and `uq/seedscan_lgbm_ml/uq_covariance_ml.root` (LightGBM, seeds 1…10) are **confirmed**. A's
   assessment does not name the rollup script. That `uq/rollup_vl170_adoption.sh` is the active
   `VL172` route rests on D's evidence: its header, its output directories, and the ledger's
   "Active 2D Result" product path. E's reviewer should re-read that header.
3. O3, the backend: answered (`E_C`), see O3.

## For E

- Integrate D's branch through its FREEZE commit (`d126a115` INVENTORY, then `abc1e6f7`, `00803510`,
  `bd738973`, `3a95fc71`, `c986779b`, `e4883157`, `3848b1ce`, FREEZE). All are documentation. Nothing touches `MANIFEST*`, `CATALOG.md` or a hash-bound file.
- O3 needs a status-routing decision, after A's answer, about the 2D status headline's backend label.
- A's later `P/a/verification.md`, if it disagrees with any D wording, supersedes D's reading. D's
  edits are documentation, so reverting one restores its base text.
- The reference cites A's assessment path, which exists only on A's branch until integration.
- `README.md`'s shared-code row and the reference's producer table contain no numbers. They will need
  a refresh only if the rollup route changes.

## Terminal record

**Decision.** Three structural defects materially obstruct estimator tracing, validation design and
supported reproduction in the 2D lane:
- the reference routed the quoted uncertainty to superseded producers (O1);
- the reference's seed instruction contradicted every producer (O2);
- the frozen central value's backend was mislabeled (O3, now answered by A).

All three were safely improved now, in documentation. Two further defects need code or protected-surface
changes and are deferred with designs: the reported-bin mask alignment (O4) and the gen5d location (O5).

**Disposition: PASS.** The four navigation tasks are demonstrably shorter and point at the correct
artifacts (before/after logs). All five prioritized findings have an implemented or a justified
deferred disposition. No source file changed, so no behavior could regress. The hash bindings,
the hash-binding tests and the pre-commit checks pass.

PASS here does **not** validate coverage, change adoption, grant compute, authorize any move or
removal, advance a pin, or reopen a campaign. The backend finding (O3) is A's measurement. Whether
the LightGBM blocks describe the exact-GBT central value is A's, B's and E's question, not a D
conclusion.

**Unresolved and consequential.**
- The status headline's "lgbm" label for the central value (E, status routing).
- The O4 patch, which needs a Perlmutter equivalence run of the rollup controls (A, or the
  publication owner for `compare_to_paper_fullcov.py`; about minutes of CPU on frozen inputs,
  with Joseph's or the owner's go-ahead).
- `P/a/verification.md`, which was absent when D froze.

**Session.**

| Field | Value |
|---|---|
| Model | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code |
| Effort | not exposed to the session |
| Session id | `0b2adcf5-295f-4aa8-bd36-f6cbc2f1fc9d` |
| Owner / reviewer | D owned the lane; no reviewer or worker agent was spawned; the single independent review is E's |
| Base | `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c` |
| Output commits | `d126a115` … FREEZE, on `prep/uncertainty-d-navigation-20261008` |

**Resources against D's budget row.**

| Resource | Used | Ceiling |
|---|---|---|
| Active time | about 0.9 h (06:08–07:00Z, including the 30-minute bounded wait for A) | 6 h |
| Local CPU | under 0.1 core-h (git, greps, one 91 s pytest run, the verifier) | 3 core-h |
| Peak RAM | under 1 GiB | 8 GiB |
| New scratch/output | the worktree (0.4 GiB of checkout files) plus a TMPDIR under 1 MiB; committed records under 0.1 MiB | 1 GiB |
| Cluster node-hours, GPU-hours, training, toys | 0 | 0 |
| Implemented improvements / source files / repairs | 3 / 0 / 0 | 3 / 2 / 2 |

## Repair 1 (E finding F13, cycle 1 of 2)

E's independent review reproduced the four navigation tasks at the integrated commit and found one
citation-precision defect in `2D_OMNIFOLD_REFERENCE.md`, "Import constraint". The fix is in this
commit; the source checks were made in this session.

- **Citation.** D's text attributed both conditions to `AUTHORIZATION-20260903-oi136-failopen-repair.md:41`.
  That row names the in-`main()` insert and the driver's sha ("pinned in three places"). It does not
  name the helper digest. The helper-digest condition is now cited to
  `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py:266-274` (`OMNIFOLD_SHA256`) and to
  `PLAN-20261008-uncertainty-investigation-preparation.md:18`. Both were checked.
- **Caveat added.** Both `OI-136` ratchet suites fail already on a tree whose `.py` files equal
  `ad2716d8` (`git diff --stat ad2716d8 HEAD -- '*.py'` is empty). Measured: 2 failed, 15 passed
  ([`oi136_ratchets.txt`](oi136_ratchets.txt)). The two failing tests are the set-membership checks,
  which flag nine October rooted-insert sites; E records these as `KNOWN_ISSUES.md` 89, which was not
  yet on E's pushed branch when D checked. The driver's two condition tests pass.
- **Not changed.** `README.md` "Before changing the 2D driver" carries the same two-condition
  attribution to `:41`. That is base text and outside F13. It is left for E's decision; repairing it
  would use D's second and last repair.
