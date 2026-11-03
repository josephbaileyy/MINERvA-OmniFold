# BINDING: GENCMP amendment E, Stage G on the "CH, analysis definitions" predictions, and step C-R (director, 2026-11-01)

**Binds** [`FD-GENCMP-AMENDMENT-E-DECLARATION.md`](FD-GENCMP-AMENDMENT-E-DECLARATION.md) and its inputs file
`fd/gencmp-e/INPUTS.sha256`. It binds them as merged in PR #657 at **M = `6cd095d6773a45c8deef47d298245ea270a636ae`**
(PR head `dd91578f3d7b0ee59728be590e0a413e3ab56132`).

**Under:**
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`, item 2;
- `DECISION-20261101-joseph-gencmp-paper-adoption.md` (#651), items 5 and 6, and its correction (#652).

## The code bound (git blob digests at M)

| blob | path |
|---|---|
| `07899d161bdb84fe6e6b549a3b8ee5886dde77a7` | `nd-unfolding/fd_gencmp_e.py` |
| `9e0272fab22643749df64ea91a6727130a77c9f5` | `nd-unfolding/fd_gencmp.py` |
| `51b77bb53b195d622b66bf4daad902e45f09a66c` | `nd-unfolding/fd_g_figures.py` |
| `fdaa9dc13c983249d385d16425aff26bdf235097` | `nd-unfolding/fd_g_figures_check.py` |
| `fe60ff68344facab0436f2befd97ced6a490d477` | `nd-unfolding/tests/test_fd_gencmp_e.py` |
| `728e7812efe47b71da102f7a180fd7870e2cfb60` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/INPUTS.sha256` |

The deploy verifies each of these with `git rev-parse M:<path>` and stops on any difference.

## What the director checked

- **The digests:** `git rev-parse dd91578f:<path>` gives the six digests above, which match the lane's list.
- **The tests:** at that head, in a detached worktree with its own TMPDIR, `python3 -B -m pytest` ran
  `test_fd_gencmp_e.py` (43 collected), `test_fd_gencmp.py`, `test_fd_g_figures.py`, `test_fd_cpl_addition.py` and
  `test_fd_gencmp_rebuild.py`.
  - The result was 266 passed and 3 skipped (ROOT- or Linux-only).
  - The lane reported 265 passed for the same set. The one-test difference is noted, and it changes nothing bound.
- **The review:** a fresh Sonnet subagent audited the declaration and code read-only. Its prompt and answer are
  verbatim in `FD-GENCMP-AMENDMENT-E-REVIEW-PROMPT.txt` and `-ANSWER.txt`. The lane answered its three blockers (A1, B1,
  B2) in the code and tests at M.
- **The declaration, §3, §5, §6 and §8:**
  - R0 reproduces every committed Stage G readout before any new number, and it gates everything after it;
  - no tolerance is relaxed;
  - every stop is named;
  - the paper text for every outcome is fixed in advance.

## Rulings

1. **E-S, E-M, E-R0, E-1 and C-R are bound as declared,** on a saul login node at 0 node-h.
   - They run in `root_6_28`, from a fresh clone detached at M with empty porcelain.
   - Each step keeps its declared timeout. A timeout stops the chain, and nothing moves to a compute node without a
     new binding.
2. **R0 is the gate (declaration §3).** If any R0 check fails in either arm, E stops and reports, and the chdefs set
   does not start.
   - Comparing strings only in the with arm (S1) is accepted. It was fixed before any run, and the reason is recorded.
3. **C-R uses `E_R` and `Q_R` (family R)** with the three added stops of §5, and with C-R3D.
   - Its 2D numbers supersede #648 §2.3's in the records.
   - They go to Joseph together with X's result. `paper_body.tex:119` is not touched until X reports.
4. **E2's cap of 0.5 node-h is bound now** (one regular CPU job, ≤ 25 min, basis PV J5 60206336). Its code is not.
   - E2 runs only after its code's blob digests are bound, by an addendum to this binding.
   - Once they are bound, E2 runs whatever E-1 shows (A2).
   - **Added by the director:** E2's report goes to Joseph in every outcome, beside its §8 sentence. If C_model,CH
     would change the reported covariance's χ² by more than the GiBUU rise already disclosed (2.3), the director also
     brings Joseph the question of whether the reported C_model should be rebuilt on CH. No covariance changes without
     him.
5. **The paper.**
   - If E-1 completes, the paper lane re-pins and drops the scoping clause under §8's row. Every changed values key goes
     to Joseph through the paper lane's report, with before and after.
   - No sentence is reworded under this binding.
6. **Reads, writes and storage:**
   - O_NOATIME for every pscratch original;
   - writes only under `$P/gencmp-e-20261101/`, which must be absent before E-S;
   - nothing to CFS;
   - the HPSS copy after `hpssquota`, with an explicit list, `hashverify` and retrieval.
7. **The report** gives:
   - each step's controls and readouts;
   - the §8 outcome it reads;
   - its cost (0 node-h for the login steps, `sacct` for E2);
   - every deviation, unprompted.
   It goes to the director. Declaration X (#653's route B) is reviewed and bound separately. It cites
   `fd/gencmp-e/INPUTS.sha256` at M.

## Addendum E-A1 (director, 2026-11-01, later)

**The stop.** The first run stopped as bound. E-R0 passed in all 26 checks. In E-1's nopl arm, `fd_g_figures` exited 1
on K6, because the declared legend qualifiers ran off the page. XC did not run. C-R ran in omnifold_py310, as the
director ruled by message: uproot is absent from root_6_28. That is a deviation from §7 and ruling 1, and the report
records it.

**Binds** addendum E-A1 as merged in PR #659 at **M′ = `1d936338d55645a5204c39ff9b02ea3290496003`** (PR head
`c6356fe45b37b0801de60a23fa3d644a5b8a4388`).
- **What changed:** only the `gencmp-chdefs` legend qualifiers and the checker's declared names, plus the label test.
  Each label keeps "CH, analysis definitions".
- **The blobs at M′:**
  - `fd_g_figures.py` `4e760ef762467204ae1b7d306df82938a7b94bbf`;
  - `fd_g_figures_check.py` `e938eeaa4abf4d33a31c96589d8f3c230db5ee90`;
  - `tests/test_fd_gencmp_e.py` `e16c168778b60519d2d06159455d92ca43aad684`.
  `fd_gencmp_e.py`, `fd_gencmp.py` and INPUTS are unchanged from M.
- **What the director checked:** the diff (3 code files, scope as ruled) and the digests above. The lane reported 266
  passed and 3 skipped, and its local K controls K0–K8 at 0 FAIL, with the checker at 498 OK.

**Rulings.**
1. The rerun is a fresh clone at M′, run in `$P/gencmp-e-20261101/rerun1/`. E-S, E-M and the full chain are rerun, and
   R0 re-gates everything. The first run's directory stays untouched as the record.
2. C-R stands as run, since it does not use the figure tool. Its readings go to Joseph with X, under §8's "a quadrant's
   reading changes" row (QA).
3. Everything else in this binding stands.

## Addendum E2 (director, 2026-11-02)

**Binds** [`FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md`](FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md) as merged in PR #670 at
**M″ = `885e366ec46059b230352b08be5a47f13160768c`** (PR head `712edcf1d69ebaf83adcffe00690a807b9f47bc2`, a merge of `2cbea6dd` with main; code unchanged
from `2cbea6dd`). This is ruling 4's code addendum.

**Correction (director, 2026-11-02).** The first version of this section, merged as #674 (`df686ff3`), was defective:
- **The cause.** #670 had not merged, because it conflicted with main in `CATALOG.md`. The director's script discarded
  the merge helper's failure status (a piped `ci_merge.sh`).
- **What it named instead.** M″ = `68d877cd…`, the previous main, which does not contain E2's code. Its blob list was
  `git rev-parse` error text.
- **The consequence.** Nothing ran under it: the lane was told to hold E2 before any stage, clone or unfold.
- **What this section binds now.** It replaces that text and binds the merge commit above.
- **The fix.** The helper now exits 0 only once the PR reads MERGED.

**The blobs at M″:**
  - `nd-unfolding/fd_gencmp_e2.py` `a63e7fe0992d9ef897bd868760ed24c497471f20`;
  - `nd-unfolding/tests/test_fd_gencmp_e2.py` `db6e0eaa6c9b68435aade80b1f8a746ce3b35065`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e2/receipts/x_e2_unfold.sh` `d4a732846fa9ae0588fd198aafee21ace895e703`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e2/INPUTS.sha256` `1fe20983ad8b99e823538eaf73932d70ddd444ff`;

**What the director checked.**
- **The digests.** The four blobs match the lane's list.
- **The tests.** At the head, `test_fd_gencmp_e2.py` and `test_fd_gencmp_e.py` gave 62 passed locally.
- **The review.** The Sonnet audit is verbatim in `FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REVIEW-{PROMPT,ANSWER}.txt`.
- **The director's change after the audit.** The director asked for a measured noise floor in place of the
  "no noise floor estimated" qualifier:
  - two more unfolds, NuWro carbon and GiBUU carbon at estimator seed 43, in the same job;
  - Δ_noise,max reported beside Δ_max;
  - the reading fixed in advance, including "within the estimator's seed variation" when Δ_max ≤ 2 Δ_noise,max.
  The lane added it in `2cbea6dd`, with six tests and three caught mutants.

**Rulings.**
1. **E2 runs as the addendum declares.**
   - The staging and the vertex and ratio steps run on a login node, with controls V and R1.
   - The unfold is one regular CPU job of five 42-CPU steps, at `-t 00:25:00` and **≤ 0.5 node-h**, with controls R2
     and B2.
   - The χ² readout comes after C1–C3.
2. **Stops.** Any control failure or other stop is final, and no E2 number is used (A2).
3. **The flag is unchanged:** the with arm's total χ² |Δ| > 2.3 brings Joseph the C_model-on-CH question. No
   covariance changes without him.
4. **The report goes to Joseph in every outcome.** It gives every signed Δ and Δ_noise and the `sacct` cost.
   - The paper lane replaces #651 item 6's caveat with the fixed reading only after Joseph has the report.
5. **Connects:**
   - O_NOATIME reads;
   - writes only under the addendum's `$R`, and nothing to CFS;
   - a fresh clone at M″;
   - the HPSS copy at the end.

## Addendum E2-A1 (director, 2026-11-02)

**The stop.** E2's first run (`$P/gencmp-e2-20261102/`, from M″) stopped at R1 leg (iii), after stage, V, R1 (i) and
R1 (ii) had passed. It spent 0 node-h, and no E2 number exists.
- **The cause was in the control.** It checked the producer's `truth_cut` branch (`pvl_ratios.py:130-131`).
- **That branch does not run on L-5D-PV.** There p∥ is a reweight axis, so the domain is recorded as `pz_max_cells`
  (`:119`, `:124-125`, `:132-133`), and the committed `gibuu.json` carries `pz_max_cells` = 10.0 and no `truth_cut`.
- **The domain itself was already verified.** R1 (i) re-derived it field by field, and it passed.

**The director's ruling (by message).** This is a repair, as in X-A1. The director also required a sweep of every
other E2 control against the real committed formats.

**Binds** addendum E2-A1 as merged in PR #676 at **M‴ = `372db7653ca16b34d033d076e609cb07b1fce0d2`** (PR head `fb5a6ebda4d2adad0c112fb9138478baba6226d5`).
- **Leg (iii) now reads:** CH GiBUU and the committed GiBUU carry `pz_max_cells` = 10.0 and no `truth_cut`, and CH
  NuWro carries neither.
- **The controls were refactored into testable functions** (`code_differ`, `c1_ok`, `c2_ok`, `c3_failures`), with C3's
  TOL unchanged at 1e-10.
- **The unfold script names the new run directory** `$P/gencmp-e2a1-20261102/`.
- **The blobs at M‴:**
  - `nd-unfolding/fd_gencmp_e2.py` `86e6c3971a11d7e81025f9fb6890c70bef8f8813`;
  - `nd-unfolding/tests/test_fd_gencmp_e2.py` `2738ccd1cfaa13d4e46d10279de64ebbc428b115`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e2/receipts/x_e2_unfold.sh` `60e1f823b969a3305934ea24052faeb41723d415`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e2/INPUTS.sha256` `1fe20983ad8b99e823538eaf73932d70ddd444ff`;

**What the director checked.**
- **The diff.** It does only the above.
- **The tests.** Locally, `test_fd_gencmp_e2.py` and `test_fd_gencmp_e.py` gave 69 passed. On the cluster, the lane
  reports 26 of 26.
- **The receipts.**
  - The mutants: `x_e2a1_mutants.tsv`, 7 field mutants FAIL and 5 code mutants CAUGHT.
  - The sweep: `x_e2a1_sweep.tsv`, with the probes in `fd/gencmp-e2/receipts/sweep-a1/`. On the real committed formats
    it shows B2 (seed 42 and seed 43), the B2 code record, C1, C2 and C3 passing in the run environment.
- **What the sweep cannot test before the run.** R2's rerun side and the job's five steps. Each fails closed with a
  named, final stop.
- **The sweep's disclosed finding (b).** C3 is exact on the cluster's numpy 1.26.4, but on macOS BLAS it misses by up
  to 1.7e-10. The tolerance is not loosened. The run is on the cluster.

**Rulings.**
1. **The rerun.** It starts from a fresh clone at M‴, from stage onward, into `$P/gencmp-e2a1-20261102/`. The first run
   directory stays untouched as the record of the stop.
2. **The cap is unchanged:** ≤ 0.5 node-h for the unfold job. Every other ruling of addendum E2 stands.
3. **The report goes to Joseph** and gives both runs and the stop.

## Addendum E-A2 (director, 2026-11-02, latest)

**Binds** `FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2.md` as merged in PR #709 at **M⁗ = `e1c0af3b0e5367369540e27a25b372f92e49f871`** (PR head `f0f23709`).

**Under** `DECISION-20261102-joseph-caveat-cut-list.md` item 1, move MV07F.

**What it changes.**
- The gencmp-chdefs legend and K7's required strings drop "hydrogen: supplement FLAGGED" and "hydrogen: closure B3
  failed".
- Every label and readout keeps both flags. The facts move to Table III's footnote and the note.
- It supersedes amendment E §4/§12's legend list and review row A6.
- All three chdefs figures (ratio, modes, sens) are redrawn into `chdefs/with/figures-a2/`. The redraw goes through the
  chain's figure entry on E-1's committed with-arm readouts, with every input at its committed digest.
- **Control D:** each new sidecar equals the committed one, except argv, code, versions, the PDF and the label texts.
  Each label text equals the committed text minus the flags.

**The blobs at M⁗:**
  - `nd-unfolding/fd_g_figures.py` `76d1c5b8b41da48d93f60775c63a1411faa334c4`;
  - `nd-unfolding/fd_g_figures_check.py` `943bb2f2294614569e0efa343bfbc2fe20829ded`;
  - `nd-unfolding/fd_gencmp_ea2.py` `16e4e20f6cd671f0d3744d02dfeceb543e56e648`;
  - `nd-unfolding/tests/test_fd_gencmp_ea2.py` `955db2d9db1115b54849f8be9c14312ff58c4af4`;

**What the director checked.**
- **The diff:** only the qualifier strings change in the two figure files, plus the new redraw module and its tests.
- **The tests,** run locally at the head: `test_fd_gencmp_ea2.py`, `test_fd_gencmp_e.py` and `test_fd_g_figures.py`
  gave 101 passed.
- **The mutation receipt:** 16/16 killed.

**Rulings.**
1. **The redraw runs** on login37 in `root_6_28` (matplotlib 3.10.8, as the chain ran), at 0 node-h.
   - It runs from a fresh clone at M⁗ into a new `$R` = `/pscratch/sd/j/josephrb/gencmp-ea2-20261102/`.
   - It reads only committed files in that clone.
   - `fd_g_figures_check` and control D must pass.
2. **The paper lane then:**
   - re-pins make_values' FIGURES to the new ratio PDF and the note's modes figure;
   - drops Fig. 4's pointer sentence and the modes-caption definition of "supplement FLAGGED". The fact stays in the
     note §11.9.
3. **The inexact CHDEFS comment** in `fd_gencmp_e.py` (lines 68–69) is accepted as recorded, which keeps amendment E's
   bound blob.

## Fixed, unchanged

Every claim and number in the paper until Joseph rules on the report; the reported covariance; Table IV as adopted
in #656. Nothing is submitted, deposited or tagged.
