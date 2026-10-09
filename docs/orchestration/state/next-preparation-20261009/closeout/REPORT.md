# Session 1 — preparation closeout and shared ownership

| field | content |
|---|---|
| `Lane` | Session 1, closeout |
| `Decision` | Is the completed A–E preparation accurately documented and ready for Joseph's merge decision, with a concrete description of the remaining scientific choices? |
| `Branch` / `Base` / `Head` | `prep/next-closeout-20261009` / dispatch `8eafd357e8ecf1fce6082a9a888432c5b3a729ba` (parent `901f0088`) / the commit that carries this revision of the report; review-fixed heads are in §7 |
| `Owned files` | `Q/DISPATCH.md`; `Q/closeout/` (this report, `GOALS-20261009-as-dispatched.md`, `checks/`, `logs/`); `docs/orchestration/CATALOG.md`, `MANIFEST-overrides.tsv`, `MANIFEST.tsv` (generated); closeout corrections only in `DELIVERY-20261008-uncertainty-preparation.md`, `ASSESSMENT-20261008-2d-estimator-pairing.md`, `DESIGN-20261008-2d-independent-statistical-validation.md`, `ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md` |
| `Pinned inputs` | delivery `901f0088e23c2394d5ea9cdce7c12d9a2710bb07`; frozen review `ee61fb223668252dc571327af7678d40c3d47aee`; E freeze `287f25f5`; upstream `460631d1f93c2f0cbaab6ecffdf313121c431751` (= `origin/main`, 2026-10-09T18:30Z); lane tips A `cc9eed27`, B `c783d9c3`, C `57f6dd30`, D `ecb52dde`; operands named in §3 |
| `Resources` | see §8 |
| `Review` | see §7 |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | see §9 |
| `Next action` | see §10 |

`Q` = `docs/orchestration/state/next-preparation-20261009`. **This report changes no scientific
result, gate, adoption or publication text.** The scientific limits of the preparation stand as
recorded in DELIVERY §1. The guard and successor lanes are not prerequisites for this PR.

## 1. First deliverable: the dispatch base

Published as `8eafd357` at about 18:36Z, roughly 10 minutes after the session started, and pushed to
`origin/prep/next-closeout-20261009`. It contains:

- [`Q/DISPATCH.md`](../DISPATCH.md): the common base, the writer table, the six report paths with
  their required header fields, and the ownership observed at dispatch;
- the planner's goals file, copied unedited to
  [`GOALS-20261009-as-dispatched.md`](GOALS-20261009-as-dispatched.md) (sha256 `81496789…`);
- seven `MACHINE open` overrides rows, for `DISPATCH.md` and the six `REPORT.md` paths;
- a `CATALOG.md` § Current work route;
- a regenerated `MANIFEST.tsv`.

The only live writer outside the six lanes was `preserve/anatuple-data-cfs-20261009`, the publication
preservation lane. Its publication paths are excluded from every lane. The generated `MANIFEST.tsv`
is the one overlap, and it is resolved by regenerating it rather than hand-merging. No surface had to
be withheld for an active conflict. Lanes 2–6 have no message from this session: the pushed commit is
the handoff.

## 2. Delta inspected: `ee61fb22` → `901f0088`

- **`287f25f5`, E's freeze.** It edits DELIVERY, `2D_OMNIFOLD_STUDY_STATUS.md` (one label, `P01`–`P09b`),
  the proposal's §0 citation, `e/integration.json`, `e/recompute/README.md` and `MANIFEST.tsv`. It adds
  `e/review-cycle1.md`, the reviewer's `rc_c_exact.py` and `rc_sens.py`, and three cycle-1 logs.
- **`901f0088`, the integration of upstream `460631d1`.** That is PR #59, which adds
  `docs/publication/audit-20261008/` (22 files) and regenerates `MANIFEST.tsv`. It touches no reviewed
  file. A search of the audit report for the pairing, the estimator or the transfer finds nothing that
  bears on the preparation.
- **Preserved review bodies.** `review.md` from line 15 hashes to `7b71fb61…` (29,847 B), and
  `review-cycle1.md` from line 10 to `adbd2c12…` (11,688 B). Both equal the digests their headers state.
  All 20 rows of `e/recompute/README.md` match their files.

### E's post-review wording, checked against `review-cycle1.md`

| E's statement | evidence | result |
|---|---|---|
| §2 focused-review commit `ee61fb22` | cycle-1 status table | correct |
| §6 `P09b` label; 170–350 / 330–510 node-h | cycle-1 N2, N4; recomputed (§3.3) | correct |
| §6 rationale marked as E's judgement | cycle-1 N5 | correct |
| §7: F1–F3 RESOLVED, no new material finding | cycle-1 verdict | correct; "cycle 2 was not needed" **corrected** to "not used", because E's later wording repairs were never re-reviewed |
| §8 focused-review summary (F-statuses, 355174fe checks, moved numbers) | cycle-1 §§1–3 | correct |
| §8 residuals; §9.2 N1 reasoning | cycle-1 N1 | §9.2 still left the reference-aware variant open; N1 applies to N1's coverage test too, so **corrected** (§3.1) |
| §11 E time about 1.1 h; reviewer 0.4 + 0.3 h | the windows add to 69 min; `review.md` §7 and cycle-1 resources | consistent; E's own core-h is not checkable |
| proposal §0 cites `review-cycle1.md` at `ee61fb22` | cycle-1 N3 | correct |
| STATUS `P01`–`P09b` | `pairings.tsv` ids | correct |
| `integration.json` "every upstream file equals 33811d7d" | blob comparison | true at the freeze, stale after `901f0088`; immutable, so DELIVERY §2 now supersedes it |

## 3. Corrections (Goal 1 items 1–4), each against its first operands

### 3.1 B's N1 truth-free variant (`9b64588f`)

- **Premises re-read.**
  - `f_data` = (0.48696 / 0.67382)² = **0.5223**. The numerator is the median relative spread of the
    200 data-only real-data replicas (`ki85-diag-20261006/ki85_result.json`
    `median_rel_spread_pct.realboot`). The denominator is the VL170 both-stream bootstrap median
    (`ki84-adopt-20261006/recompute_2d_budget.json` `VL170.boot.median_pct`).
  - MC/data = 4.978e21 / 1.0574e21 = **4.7078**.
  - N1's bank is half the MC (B §14 "half-MC bank", §16 "MC/data 2.35"). The reviewer used N2's 48 %
    bank.
- **Result.** MC-stream variance × 2.000, data share 0.3534, **κ = 0.594**; at 48 %, × 2.083, 0.344,
  **κ = 0.587**. Both are below the 0.80 edge (`checks/arith.py`, `logs/arith.txt`).
- **Mismatch.**
  - The fixed bank means the outer scatter carries only the data-stream term, while the both-stream
    inner bootstrap puts the MC-stream term into σ̂. So κ ≈ 0.59 for the truth-free width test.
  - The bank's own MC realization is a per-functional offset against `T_R`, rms √(1 − 0.353) =
    0.80 σ̂. With the both-stream bootstrap, pooled I68 coverage is exactly nominal (0.6827), but per
    functional it is mixed: 62.6 % over-cover (exact edge d* = 0.714 σ̂), and the bias test fails in
    most functionals (about 188 of 206, the reviewer's figure; `review/review-cycle1.md`). With a data-only stream the offset is 1.35 σ̂ and mean I68 coverage is 0.448
    (`checks/arith.py` `n1_bank_offset`).
  - The first committed version of this correction (`9b64588f`) called it "over-coverage" and said
    a data-only stream would also make the reference-aware form a data-stream test. The closeout
    review's F1 showed both were wrong, and `265efc2f` repairs them.
- **Change needed.**
  - The reference-aware variant is not open with either inner stream: its `τ_ref` model covers the
    reservoir, not the bank offset.
  - Only the truth-free width form survives, where `Ū` cancels the offset, and only with a data-only
    inner stream (`--bootstrap-streams data`, as N2's arm B uses). It is then a per-experiment,
    data-only diagnostic of N2's kind. It is conditional on `S` and `R`, covers no MC stream, no
    coverage of truth and no total, and is unpriced.
  - N2 is **not** upgraded to coverage validation.
- **Edited.** DESIGN §7, the §16 N1 row, §17 and §18.
- **Limits.** `f_data` is a ratio of medians. The 1/(bank) scaling of the MC-stream variance is B's own
  convention (`assurance.py` `mc_stat_variance_inflation_vs_production`). Per-bin shares vary, so κ is
  stated at the median bin.

### 3.2 C's unsplit `P09` (`1545ee2a`)

| C line (at `901f0088`) | context | now |
|---|---|---|
| 43 | "produced by LightGBM, not by `E_C`" (estimator identity) | `P09a` |
| 44 | transfer unmeasured | `P09b` added |
| 52, 138, 412 (twice) | measured transfers / stage-0 transfers | `P09b` |
| 365 | exact seed scan price | `P09b` |

The tally sentence now names both counts: the FREEZE (`f762749d`: 4 of 17 DISPROVED, 3 UNRESOLVED) and
the split (`cc9eed27`: P02, P04, P09a and P17 DISPROVED; P03, P05, P07 and P09b UNRESOLVED; 18 rows).
Both were re-read from `pairings.tsv`. C's machine records carry no `P09` label.

### 3.3 A's `P05` price and C's ratio (`ac59ac28`)

- **A's figure.** 188 × 0.68 = **127.84 node-h**. It assumes an exact universe unfold costs what the
  exact CV unfold does. The 0.68 node-h is A's memory-packed extrapolation from the one measured exact
  run (`53116554`, 69,523 s, 1 core, MaxRSS 16.8 GB). Packing contention is unmeasured, and no exact
  universe unfold exists.
- **C's figure.**
  - The ratio is 0.5 h / (804 s / 3600) = 2.2388. The two walls are documented, not receipts: STATUS's
    runtime table (13m24s), and the archived run log for sweep `53441839` ("Per-task wall ~30 min",
    `evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:2995`).
  - It gives 187 × 0.68 × 2.2388 + 0.68 = **285.37 node-h**.
  - C calls the multiplicative ratio an upper-side choice and an additive I/O overhead smaller.
- **Transfer totals** (P03 34–215 + P05 + P09b 6.8): **168.6–349.6** at the CV rate and **326.2–507.2**
  at the ratio. These reproduce the quoted 170–350 / 330–510.
- **Edits.** A's price bullet and C's own list now state the assumption and give both figures. C's
  stage-0 row quotes both totals. No single price is manufactured.
- **Left unchanged.** `pairings.tsv` (A's record) still reads "~ 128 node-h".

### 3.4 DELIVERY (`db76069a`)

- **§2.** It now names the final upstream `460631d1`, E's freeze `287f25f5`, the delivery commit
  `901f0088` and this branch.
- **The identity sentence** was re-measured with `checks/identity.py`, a blob-by-blob comparison:
  - at `901f0088` every lane-touched file equals its final tip (A 32, B 7, C 4, D 11);
  - every file changed upstream since `ad2716d8` (87 files) equals `460631d1`, except the
    regenerated `MANIFEST.tsv`;
  - positive control: the same comparison at `ee61fb22` lists the 22 audit files;
  - at the closeout head, exactly the three corrected lane documents differ (`logs/identity.txt`).
- **Smaller fixes.**
  - The §6 paper reference is now `paper_body.tex:126-129`. The file is identical at `901f0088` and
    `origin/main`.
  - §7 now says "cycle 2 was not used".
  - §8 records the three closeout corrections and leaves the F12 test note open.
  - §9.2 is corrected as in §3.1.

## 4. Proposed publication wording for "keep and disclose" (not applied)

**This is a proposal for Joseph and the publication owner. It does not choose the option, edit a
publication source, or make the package publication-ready.** Choosing it is Joseph's decision
(KNOWN_ISSUES 88). Applying it is the publication owner's work, under the three-build and
standalone-synchronization rules in `AGENTS.md`.

**Manuscript location (`docs/analysis-note/paper_body.tex`, identical at `901f0088` and
`origin/main` `460631d1`).**

**(1) The estimator list, lines 126–129.** Current text:

> \item \emph{Two-dimensional uncertainty ensembles}: the finalized systematic-universe and
> Poisson-bootstrap ensembles use LightGBM at matched nominal capacity, so the uncertainty ensembles
> use a different implementation from the two-dimensional central-value estimator.

Proposed:

> \item \emph{Two-dimensional uncertainty ensembles}: the finalized systematic-universe,
> Poisson-bootstrap, and training-seed ensembles use LightGBM at matched nominal capacity.  The
> two-dimensional covariance is therefore computed for a different estimator from the exact-split
> central value, and whether it also describes that central value has not been measured
> (Sec.~\ref{sec:validation}).

**(2) § "Two-dimensional uncertainty and its coverage", lines 180–181.** Insert after "…compared with
\SI{\uqPaper}{\percent} for the publication.":

> These ensembles use the LightGBM estimator rather than the exact-split estimator of the quoted
> central value (Sec.~\ref{sec:method}).  The LightGBM and exact-split central values differ by a
> median of \SI{0.97}{\percent} per bin, and by a per-bin median of 1.3 times the statistical
> uncertainty, a difference that no block of the covariance carries, and the transfer of the covariance to the exact-split central value has not
> been measured.

Optional, if the owner wants the denominator stated: "(\SI{6.83}{\percent} relative to the exact-split
central value)". `P14` gives 6.8269, and the reviewer reproduced it.

**What it must state, and where each statement comes from.**

| statement | evidence | origins |
|---|---|---|
| central = exact-split sklearn GBT; universe, bootstrap and seed blocks = LightGBM | `a/pairings.tsv` `P01`, `P02`, `P04`, `P08`, `P09a`; A §2.1 | A; reviewer re-read sacct and revision (`review.md` §2) |
| median 0.97 % per bin; per-bin median 1.30 σ_stat (p84 2.76, max 8.32 σ_stat, 12.5 %); LightGBM seed 1 vs exact (CV42 vs exact: 0.98 %, 1.32) | A §3; `a/verification.md:100`; `e/recompute/rc_pairing.json.txt` `cmp` "seed1 vs exact": 0.966 %, 1.2995 | A and reviewer, independently coded |
| "no block carries it" | A §5 item 3 | A |
| transfer unmeasured | `P03`, `P05`, `P07`, `P09b` UNRESOLVED; KNOWN_ISSUES 88 | A; reviewer confirmed the labels |
| 6.83 % against `E_C` | `P14`; `rc_pairing.json.txt` `blocksum_median_rel_pct_den_exact_central` 6.8269 | A and reviewer |
| integrated ratio 0.9999 (not used in the wording) | `a/logs/check_a_output.txt:80` (seed 1 vs exact, 0.999899; `:134` is CV42 vs exact, 0.999906) | **A only**; the reviewer did not recompute it, so the wording leaves it out |

**For the publication owner's consistency sweep (observed, not exhaustive, not edited):**

- note `sec_method.tex:87-93` already says the central value and its covariance are "not
  estimator-matched", but it does not say the transfer is unmeasured;
- `sec_method.tex:98` calls the central value "a single-run unfold with pinned seeds", while A's `P01`
  records the exact central's `random_state` as unpinned (`None`). The owner should reconcile that
  sentence against `P01` before reuse;
- the note's 2D budget statements (`sec_results.tex:137`, `sec_systematics.tex:44`,
  `app_statmethods.tex`) and the primer's (`primer_body.tex:151`) quote the 6.87 % median without the
  estimator qualification.

## 5. Verification

| check | command | result |
|---|---|---|
| pre-commit (13 checks: findings, ledger ids, owners, OI ids, hash bindings, receipt artifacts, LIVE-index, unrowed, control plane, manifest self-test …) | `.githooks/pre-commit` on each of the six commits | 13 passed each time |
| hash bindings | `python3 docs/orchestration/verify_hash_bindings.py` | see `logs/verify.txt` |
| manifest from source | `generate_manifest.py` then `--check` | see `logs/verify.txt` |
| routes / links | `checks/linkcheck.py` on the five changed documents and `CATALOG.md` | the only unresolved items are intended or pre-existing: six REPORT paths (absent until pushed; this one resolves now), Session 2's future `n2/`, a branch name, a `file:line` suffix, B's pre-existing brace glob; CATALOG has 27 pre-existing |
| diff limited to declared fixes | `git diff --stat 901f0088 HEAD`; `checks/identity.py HEAD` | only the four corrected documents, the registration surfaces and `Q/` change; exactly the three corrected lane documents differ from their tips |
| OI-136 ratchets (static scans; read first: they run `git ls-files` and the repository's own probe, no job) | `python3 -B -m unittest -v` on both suites, `TMPDIR` in scratch, 69 s | 17 tests, the same 2 FAIL as `e/recompute/logs/oi136_cycle1.txt`, with an identical failing-site path set apart from the worktree prefix: the closeout adds no site. Still red, owned by the `OI-136` route / Session 2 (`logs/oi136_ratchets.txt`) |
| identity-check positive control | `checks/identity.py ee61fb22` | reports the 22 audit files, so the comparison can fire |

These are engineering and record-integrity checks. None is a scientific validation.

## 6. Limitations

- κ ≈ 0.59 and the 0.80 σ̂ bank offset are median-bin statements from a ratio of medians, and they
  assume an exactly calibrated bootstrap. The 62.6 % over-cover fraction is in `checks/arith.py`. The
  bias-test count (about 188 of 206) is the closeout reviewer's figure, preserved in `review/`; the
  owner did not re-derive it. κ and the offset show that N1's variants cannot pass as specified; they
  measure nothing about the production band.
- The two `P05` figures are forecasts. A third, additive-overhead convention would fall between them;
  it is not priced here.
- The proposed wording's 0.97 % / 1.3 σ_stat comes from two independent codings of the same operands,
  not from two productions.
- `pairings.tsv` and `e/integration.json` keep their own wording (records not edited).

## 7. Independent review

- **Reviewer.** One fresh read-only context: a Claude Code general-purpose subagent with no authorship
  of A–E or of this closeout. Its model inherits the owner's (Opus 5.5); its effort is not observable.
  CAMPAIGN-REVIEW §5 suggests Astra High, which this session cannot reach.
- **Setup.** A detached clean worktree. Writes only to external scratch, and its own code for every
  number. Its reports and scripts are preserved verbatim with digests in [`review/`](review/).
- **Budget.** One initial review and one focused re-review, both used.

| cycle | fixed commit | status start/end | findings |
|---|---|---|---|
| initial (18:52–19:00Z) | `3a9c84b8` | empty / empty | **F1 MATERIAL**: the N1 correction misstated the second failure mode ("over-coverage") and said a data-only stream would open the reference-aware variant. F2 MINOR (wording of 0.97 % / 1.3 σ). F3–F6 NOTE. Items 2–4, 7 and scope PASS, all numbers reproduced with its own code |
| focused re-review (19:05–19:06Z) | `e87d8df8` | empty / empty | F1–F5 **RESOLVED**; F6 deferred to this revision. New: R1 MINOR (two numbers not re-runnable in the tree), R2 MINOR (§§7–10 pending, a dangling "It"), R3 NOTE (62 → 63 %), R4 NOTE (the pooled-nominal statement needs "if `T_R` is treated as exact") |

**After the final review** the owner applied R1–R4:

- R1: `checks/arith.py` now computes the exact over-cover fraction, 0.6256 (edge 0.7142, equal to the
  reviewer's independent root), and the review files are preserved for the bias count;
- R2: these sections, and the dangling "It";
- R3: "about 63 %";
- R4: the qualifier in DESIGN §7.

**These last edits are not independently reviewed.** No further review cycle is permitted.

## 8. Resources

| item | measured |
|---|---|
| active elapsed time | about 0.75 h (18:26Z → about 19:12Z), including review; cap 4 h |
| local CPU | under 0.1 core-h. The largest step was the two OI-136 suites (61 s user). The reviewer reported under 0.02 core-h in total. Every command ran at 2 threads or fewer; cap 2 core-h |
| scratch | about 0.5 MiB in the session scratchpad, plus a 409 MiB detached review checkout in `/private/tmp`, removed at closeout; cap 1 GiB |
| tracked evidence added under `Q/` | about 0.17 MiB; cap 10 MiB |
| cluster / GPU / training / toys | 0 / 0 / none / none |

## 9. Disposition

| decision | disposition | reason |
|---|---|---|
| dispatch base and writer table published within 30 min | **PASS** | `8eafd357`, about 10 min in; pushed; no live conflict withheld a surface |
| the A–E record is accurate and merge-ready within its existing scientific limits | **PASS** | Items 1–4 are corrected against first operands. The diff is limited to the declared fixes and the registration surfaces. Hooks, hash bindings, the manifest and routes pass. The one material review finding is RESOLVED. The minor post-review edits R1–R4 are disclosed as unreviewed |
| proposed "keep and disclose" wording prepared | **PASS (proposal only)** | §4. It states both the distinct estimators and the unmeasured transfer, each with evidence and origin count. It is not applied and not a readiness claim |
| independent review | **PASS** | Two cycles, as budgeted (§7) |

**Preserved, not changed:** the named primary is INFEASIBLE UNDER STATED CONSTRAINTS; total
uncertainty is NO-GO; N2 is NOT READY; nothing is ready for a claim about the quoted central's
uncertainty; transfer is UNRESOLVED; VL170 is not coverage re-tested; KNOWN_ISSUES 85 is deferred;
s5c, s5n, s5e, s5p and PET are terminal.

**Open items carried, not hidden:**

- the OI-136 ratchets are still red (KNOWN_ISSUES 89; the `OI-136` route and Session 2);
- the cycle-1 F12 test note;
- `e/integration.json`'s freeze-time identity field (superseded by DELIVERY §2);
- `pairings.tsv`'s single P05 price;
- `sec_method.tex:98` "pinned seeds" against `P01`, for the publication owner.

## 10. Next action and decision list

These are Joseph's decisions. Nothing here is decided for him.

1. **Merge.**
   - What: whether to merge `prep/next-closeout-20261009`, which carries the A–E preparation and this
     closeout, into `main`.
   - Inputs: this report and DELIVERY.
   - Cost: 0 compute.
   - Note: open PR #60 also changes the generated `MANIFEST.tsv`. Whichever merges second regenerates
     it with `generate_manifest.py`.
2. **Pairing (KNOWN_ISSUES 88; DELIVERY §6).** One of:
   - **keep and disclose:** 0 node-h; the publication owner then applies §4's wording with the three
     builds and standalone synchronization;
   - **measure the transfer:** `P03` 34–39 node-h at N = 50; all three about 170–350 or 330–510
     node-h (forecasts on a 0.68 node-h packing extrapolation); needs a design with declared
     observables and tolerances, and its own authorization;
   - **re-quote the LightGBM central:** 0 node-h for the central; an estimator and publication-scope
     change.
3. **N2.** Only if decision 2 makes the LightGBM estimator the target. It needs Joseph's lift of the
   KNOWN_ISSUES 85 deferral (after the publication package), a guarded provenance-recording harness
   (Session 2's report), its own registration and review, and 9.8–12.2 node-h with a 20 % reserve.
   It is a data-stream diagnostic, not coverage validation.

**Reopening this closeout** needs a demonstrated error in a corrected statement's operands, or a new
upstream delta that touches a reviewed file. Either would require a new bounded dispatch, because
this session's review budget is spent.

## 11. Joseph's ruling and merge authorization, 2026-10-09 (after this report's review)

Joseph authorized this session to integrate `main` after PR #60 and to merge PR #61, subject to the
integration checks in §12. He gave this scientific direction, quoted verbatim:

> - I choose "keep and disclose" as the immediate disposition of the existing 2D result.
> - This is an interim documentation decision, not acceptance of unresolved uncertainty transfer as a
>   publication-ready endpoint.
> - My intended endpoint is a publication-ready measurement with a reproducible central estimator,
>   matched uncertainty construction, and validation supporting the claims actually made.
> - The publication correction must disclose the unmeasured transfer and correct the inaccurate
>   "pinned seeds" statement. Leave implementation of those changes to a separately assigned
>   publication owner; this merge does not authorize submission.
> - Do not re-quote the LightGBM central, launch transfer measurements or N2, lift KI-85, change
>   scientific gates, or reopen terminal campaigns.
>
> A justified no-go remains a valid completed outcome for an individual investigation. It does not
> mean the overall publication-ready objective has been achieved.

**What follows from it, and what does not.**

- The §4 wording is now the input for a separately assigned publication owner. It is not applied here.
- That owner's correction must do two things: disclose the unmeasured transfer, and correct
  `sec_method.tex:98` ("pinned seeds"; `P01` records `random_state=None`). It then needs the three
  builds and the standalone synchronization.
- Submission is not authorized.
- Decision 2 in §10 is settled for the interim. Decision 3 (N2), the transfer measurement, the
  LightGBM re-quote and the KNOWN_ISSUES 85 lift are not authorized. The overall publication-ready
  objective is **not** achieved.
- **Proposed text for the shared registers' owners.** This session does not edit them. KNOWN_ISSUES
  row 88 could record: *"Interim disposition 2026-10-09 (Joseph): keep and disclose; the transfer stays
  unmeasured and is not accepted as a publication-ready endpoint; the publication correction (transfer
  disclosure and the `sec_method.tex:98` seed statement) is assigned to a separate publication owner;
  route: `state/next-preparation-20261009/closeout/REPORT.md` §11."*

## 12. Integration with `main` before merge

- **Merge.** `origin/main` `a0c26bd1` (PR #60, merged 2026-10-09T19:20:44Z) was merged into this
  branch as merge commit `93e29d18` (parents `d40f5bbc`, `a0c26bd1`). There was no squash or rebase,
  so every pinned commit stays reachable.
- **Conflict.** The only conflict was `MANIFEST.tsv`, resolved by regenerating it from source.
- **Integration effects.** Against `d40f5bbc`, the manifest differs in 16 rows, only in their
  `inbound_count` and `consumer` columns, plus the manifest's own byte count. The six PR #60 files are
  blob-identical to `a0c26bd1`. Every file this branch changed since `901f0088` is blob-identical to
  `d40f5bbc`. The merged tree differs from `main` only in this branch's files.
- **Checks on the final head:** see `logs/integration.txt`.
