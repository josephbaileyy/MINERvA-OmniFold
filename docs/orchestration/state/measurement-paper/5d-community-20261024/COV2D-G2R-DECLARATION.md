# DECLARATION COV2D-G2R: the 2D universes' misses approximation removed, the systematic block rebuilt at the data, and the 2D coverage test regraded at both tunes (2026-11-11)

**By** the `cov2d` session, which owns the 2D coverage test, at the director's request of 2026-11-11, for
`coverage-5b-audit` to audit and the director to bind. **DRAFT: nothing has run.**

**Under:**
- the fresh referee round's major 3
  (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-fresh-20261111/gpt.txt:34-38`): "The authors
  should rebuild the affected universe propagation consistently, or demonstrate a sufficiently tight bound ... The
  relevant comparison is with the final covariance and the directions driving under-coverage";
- the independent consult `secondary-results/consult-sol-2dregrade-20261111/` (PR #1078), which recommends (a+) and
  whose item D this declaration takes as requirements;
- the director's ruling of 2026-11-11: option (a+), with the pseudo-experiments' generation checked first. Joseph
  confirmed (a+) on 2026-11-11 ("okay ya I agree", relayed by the director). **His confirmation was given at the
  price then quoted, about 10 node-h. §7 re-prices it at about 70 node-h expected from COV2D's own records. The price
  is Joseph's to accept (§12).**

**After:** [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md) and its bindings and addenda, whose rule, null and controls
this regrade reuses unchanged; [`OUTCOME-20261108-cov2d-both-tunes-under-cover.md`](../../../OUTCOME-20261108-cov2d-both-tunes-under-cover.md);
the T2A split ([`fd/tier2-20261110/T2A-COV2D-SPLIT-DECLARATION.md`](fd/tier2-20261110/T2A-COV2D-SPLIT-DECLARATION.md)
and its receipt `fd/tier2-20261110/t2a/README.md`); the G2 record
[`DECISION-20261015-joseph-g2-carry.md`](../../../DECISION-20261015-joseph-g2-carry.md) and the P5 design
`state/2d-closeout/stageB/diagnostics/p5/DESIGN.md`.

**MEASURES:** nothing yet. Every statement about code below cites a file at `origin/main`
`270508cbbfaadbcf612475502bd5442e22156a5d` unless another commit is named.

**CANNOT AUTHORIZE:** any job before the director's binding of this declaration and of its code amendment (§9), and
the director's go on each connect; any change to E_R's estimator, to COV2D's rule, null or toys, or to any reported
number before the outcome is read under §10; any paper or note text, which the paper lane drafts when the result lands.

**CITABLE FOR:** the design, the finding of §2, the outcome table of §10 (fixed before any number), the price of §7.
**NOT CITABLE FOR:** any coverage statement; any size of the correction.

## 1. What the approximation is

In dump mode, every universe weight of an appended truth-only miss row (a truth event with no reconstructed partner)
is the CV truth weight (P5 DESIGN §1-2: `runEventLoopOmniFold.cpp` `AppendTruthOnlyMisses` sets every universe weight
to `w_truth`). In a `--universe BAND:IDX` unfold, the driver reads those proxies from `mc_signal_reco`'s miss rows
(`re2_driver.py` `collect_signal_arrays_2d`, the universe branch swap) and divides each cell by the universe's
completeness, which departs from 1 where truth weights vary (P5 DESIGN §1). The correct per-event universe truth weight
of every miss row is in the same file's `mc_truth_denom` tree, as `w_truth_<band>_<idx>` (P5 DESIGN §2), so the
repair is re-unfolds only, with no new event loop.

**Which unfolds carry it.** Only `--universe` unfolds of `$UNI` (the 175 universes of the 38 weight bands). A CV-mode
unfold (no `--universe`) reads `w_truth` itself, where the proxy is exact. The 10 lateral unfolds are CV-mode unfolds
of the lateral omnifiles (COV2D-DECLARATION §4.4: "each of the 10 lateral omnifiles `--data-file d̃_T`"), so they
carry no proxy. §8 control G2 checks this per universe rather than assuming it. The paper's "185 universes in 43
bands" is these 175 plus the 10 laterals.

## 2. First: the pseudo-experiments' generation does not use the approximation

The consult's item D and the director's ruling ask this first. **Finding (from the code, 0 node-h): COV2D's
pseudo-experiments neither draw nor unfold through the proxies. The 300 stored error vectors per tune stand, and no
toy is regenerated.**
- **The graded truth** composes the truth weights from `mc_truth_denom`'s own universe columns:
  `cov2d_receipt.ARRAYS` = `(("wr", "mc_signal_reco", "w_reco"), ("wt", "mc_truth_denom", "w_truth"), ("bkgw",
  "mc_background", "w_bkg"))` (`2d-unfolding/cov2d/cov2d_receipt.py:46`), consumed by step A at
  `2d-unfolding/cov2d/cov2d_pseudo.py:295-311` (`if name == "wt": truth.add(...)`). Those are the correct universe
  weights of every truth event, misses included.
- **The pseudo-data** are written only on reco-passing rows: the writer's check requires the data tree's rows to equal
  `ks[ps_].sum() + kb[pb_].sum()`, with `ps_ = sig["sim_pass"] != 0`, and refuses any row that is not a passing row
  (`cov2d_pseudo_write.py:170-190`, `section_9_11`). A miss row has `sim_pass = 0` (P5 DESIGN §2, check 1), so its
  proxy `w_reco_<u>` never reaches the pseudo-data.
- **Each toy is unfolded once with the CV simulation** (COV2D-DECLARATION §4.2, "then unfolded once"; Table S14: "The
  pseudo-data are unfolded once with the nominal simulation"), so no toy unfold reads a universe column.
- **What does carry it:** C_T's universe block, the 175 `--omnifile $UNI --universe BAND:IDX --data-file d̃_T` unfolds
  per tune (COV2D-DECLARATION §4.4), and with it the null's Discrete laws, which are those shift vectors
  (§5.2: "the Flux universes' centred shift vectors at T ..."). So today the toys draw natures from the correct truth
  weights while C_T and the null describe the approximated ones. The rebuild removes that mismatch.
- **Retained, not regenerated:** each tune's 300 error vectors are committed as
  `fd/tier2-20261110/t2a/AR23/E_AR23.npz` (`ccda9c50c6bb1cbbdd2206c8954652f4f77c6cf2b4451e8488601e9896b0a85e`) and
  `.../G18/E_G18.npz` (`846b9d852218b531d605bd955ca9a9037d187e74723077bdfff4557efafc3ba6`), captured by the bound
  `capture_e.py` with its control A0 equal (T2A receipt). The regrade reads them, not the pscratch products.

If the audit finds a path by which a proxy reaches a toy, this section's finding is withdrawn and the toys are
regenerated consistently before any regrade, at a price brought back to the director first.

## 3. Part (a): the systematic block rebuilt at the data

- **The runs:** the 175 universe unfolds of RE-2 part B's universe block (COV2D-DECLARATION §4.2, "The bank": 38 bands,
  175 universes, checked against part B's J2 run list), each with part B's argv exactly plus the miss-row override
  (§9), at estimator seed 42 and part B's thread configuration.
- **The block:** C_univ,new from the rollup's own functions (`re2c_rollup.universe_block`, `band_cov`, imported, not
  copied, as COV2D-DECLARATION §4.4 does). Every other block of the reported covariance is unchanged:
  C_new = C_rep − C_univ,old + C_univ,new, and ΔC = C_univ,new − C_univ,old.
- **The readings** (consult items C and D), each against the reported covariance C_rep:
  1. **ε**, the covariance-normalized change in each retained eigensystem: with C_rep = UΛUᵀ on its non-null subspace
     (eigenvalues above 10⁻¹² of the largest, the grade's rule), ε = ‖Λ^{-1/2} Uᵀ ΔC U Λ^{-1/2}‖₂; also at the 73 and
     139 largest-eigenvalue directions, with the coupling to the discarded directions,
     ‖P_⊥ ΔC U Λ^{-1/2}‖₂, printed beside each;
  2. **off-diagonal changes:** the largest |Δρ_ij| of the correlation matrix, and its median over i < j;
  3. **rank** above 10⁻¹² of the largest eigenvalue, before and after;
  4. **marginal and integrated uncertainties:** the median per-bin relative uncertainty (reported 6.41 %), and the
     integrated cross section's (reported 4.76 %), before and after.
- **The noise floor, printed beside ε:** two universes rerun with the override off (one Flux, one interaction band,
  named in the amendment before any run). If each reproduces part B's stored product bitwise, the floor is 0. If not,
  their ε against part B's products is printed as the run-to-run floor, and every ε is read beside it.
- **The consult's escalation rule (ε > 0.10)** is recorded but decides nothing: (+) runs regardless, by the ruling.

## 4. Part (+): C_T rebuilt at both tunes

- **The runs:** at each tune, the 175 universe unfolds of COV2D-DECLARATION §4.4, `--omnifile $UNI --universe BAND:IDX
  --data-file d̃_T`, E_R's argv, on the same realization d̃_T (seeds 5,721,000 and 5,731,000), plus the override. 350
  unfolds in all.
- **The matrix:** C_T' = C_univ'(T) + C_lat(T) + C_norm(T) + C_stat(T) + C08(T) + C_model_abs(T). Every block but
  C_univ is taken unchanged from the committed `fd/receipts-cov2d/readout/<T>/blocks_<T>.npz`.
- **The tune-level ε:** the §3 readings with C_T and ΔC_T, at each tune.

## 5. The regrade, under the existing rule

- **The rule, the null's construction and the readings are COV2D's, unchanged** (COV2D-DECLARATION §5, through
  `fd_1b_null.py` and `cov2d_null.laws_at_T`, imported). Only C_T and the Discrete laws (the corrected shift vectors)
  change. The null is recomputed at C_T' at seed 5,742,000, with 2,000,000 vectors, before any error is read against
  it, and must pass `check_matched` to 10⁻¹².
- **The errors:** the 300 committed vectors per tune of §2, in `TOY_SEEDS` order.
- **The verdict per tune:** COVERS, UNDER-COVERS or INVALID, as COV2D-DECLARATION §5.2 defines them, with the
  weakened-pass lists and the outlier cell exactly as fixed there.
- **The descriptive readouts,** recomputed at C_T': COV2D §6's per-cell readouts, and T2A's decomposition (ēᵀC_T⁺ē and
  tr(C_T⁺S)) and its joint test truncated to the 73 and 139 largest eigenpairs, through the bound `t2a_split.py`
  functions, imported.
- **The code version:** both tunes at one code commit (A5's reading rule), so the AR23/G18 code split of the first
  grade does not recur.

## 6. Order

1. **Prepare (one job):** build the 175 miss-row overrides from `$UNI` (§9), with P5's five alignment checks, and
   record per universe the count of miss rows whose override differs from the proxy.
2. **Part (a):** the 175 corrected universe unfolds at the data, then the block and the §3 readings on a login node.
3. **Part (+):** the 350 corrected unfolds at the two tunes, then C_T', the null, the regrade and the readouts on a
   login node.
4. (a) and (+) are independent and may run in either order. Neither reads the other's products.

**After the maintenance and after LL5D's gates** (the director's instruction), with LL5D's jobs taking precedence on
the shared fence. **Every read of `$UNI` must end before 2026-12-19**, the exposure date COV2D-DECLARATION §7 fixed
"as if no read moved it".

## 7. Price (from COV2D's own records; helper-3's basis is re-derived)

**helper-3's basis does not price this work.** RESPONSE.md F3.1 (#977 at `39d0ff8c`) prices (a) as "35 jobs × 0.25
node-h cap = 8.75 node-h (AUTHORIZATION-20261015 §2)". In that §2, the 35 runs are S4(ii), "7 universe settings × 5
seeds", not the universe set. (a) is 175 universe unfolds and (+) is 350.

**The measured unit.** COV2D ran this exact unfold, 350 times: "the eight universe jobs of stage 3, all COMPLETED except
G18_Ua: 44.67" node-h (`fd/receipts-cov2d/a2/bulk/README.md`, "Charges"). G18_Ua failed "solely from its expected skips":
its one skipped label, U_G18_Flux_0, came from the completion job G18_C (0.66 node-h, which also completed other
labels). So 44.67 node-h bought 349 universe unfolds, about 0.13 node-h per unfold on regular nodes, packed in lanes. The Stage C pilot measured 0.1418 node-h for a
shared 128-CPU universe unfold (`state/2d-closeout/stageC/pilot/REPORT.md` §7, u_U,sel), and the corrected (G2_on) runs
took 1,607 s and 752 s, against 695 s for the s43 off run.

| item | unfolds | expected (node-h) | held at submission (node-h) |
|---|---:|---:|---:|
| prepare: overrides and checks | 0 | ≤ 1 | 2.0 |
| (a) at the data | 175 | 22–25 | 4 jobs × 8.9 = 35.6 |
| (+) at G18 and AR23 | 350 | about 45 | 8 jobs × 8.9 = 71.2 |
| regrade, readouts, (a)'s readings | 0 (login) | 0 | 0 |
| **total** | **525** | **about 68–71** | **108.8** |

- **The cap proposed: 110 node-h**, its own, separate from COV2D's 165.8 (112.74 spent) and from LL5D's 148. Its gate
  prices unfinished attempts at their limits, with COV2D's sacct-lag ruling (one submission per call, the previous id
  listed first, and an independent recompute).
- **The record agrees:** the G2 repair price on record is "43–129 node-h" (DECISION-20261015-joseph-g2-carry.md §3).
- **Cheaper variant, for the director (not assumed):** a universe whose override equals the proxy bitwise (its truth
  weight is not varied on any miss row) gives loader arrays bitwise equal to production (P5's control C2), so its stored
  product could be reused, with a bitwise reproduction control on two such universes. Flux (100 universes) and 2p2h (3)
  vary truth weights, so the saving is bounded by the other 72. The prepare job measures the count.

## 8. Controls (any failure is INVALID, reported unrepaired; a crash, OOM, kill or time-out is INVALID)

| | control | reads INVALID if |
|---|---|---|
| G1 | **no-op:** the driver with the override flag off gives loader arrays bitwise equal to the production driver's, in universe mode (P5's C1) | any array differs |
| G2 | **identity plumbing:** an override equal to the stored proxy gives arrays bitwise equal to production (P5's C2); the lateral unfolds' omnifiles carry no universe column read under `--universe` | any array differs |
| G3 | **effect only on miss rows:** the override changes `w_truth`/`w_reco` only on rows with `sim_pass = 0`, `sim = −9999` (P5's C3); every kinematic and pass array is bitwise equal | any other row changes |
| G4 | **alignment:** P5's five fail-closed checks (tail rows are proxies, unique truth keys, every miss found, strictly increasing indices, the unmatched truth rows equal the reco-loop rows as multisets), on `$UNI` | any check fails |
| G5 | **the file is P5's:** `$UNI`'s size, by stat, is 171,117,087,867 B, the size P5's job checked for its omnifile (`stageB/diagnostics/p5/sbatch_p5.sh:61`, "sha256 220c479e..., Stage B; not re-hashed per job") and COV2D-DECLARATION §7 recorded; its mtime is recorded | the size differs |
| G6 | **block reproduction:** the imported functions, fed the OLD universe products, reproduce part B's universe block (data) and each committed `blocks_<T>.npz`'s C_univ to 10⁻¹² relative | either differs |
| G7 | **grade reproduction:** from the committed `E_<T>.npz`, the committed `blocks_<T>.npz` and the committed null, the regrade code reproduces `score_<T>.json`'s grade (counts and ndf exact, χ² to A5's tolerance) before any number at C_T' is computed | any field differs |
| G8 | **the realization:** each tune's d̃_T file's sha256 equals its committed record; if it is gone from pscratch it is regenerated by the bound writer at its seed and must hash equal | the hash differs |
| G9 | **atime and reads:** every input read outside the driver goes through `O_NOATIME`; the driver's own reads are listed in advance, as COV2D-DECLARATION §7 does | an unlisted read moves an atime |

No universe is dropped, replaced or re-seeded. A missing product is INVALID for its point (the data, or that tune).

## 9. Code (the amendment, to come)

Bound later, by blob digest, with tests and mutants, as COV2D's two-step ruling did:
- **`re2_driver.py`:** an `--miss-weight-override NPZ` flag, default off, carried from P5's `driver_p5.py`
  (`f71b5759bf01422fa8c6b6e5432885b34d1f127653df1165a0adb7527bdb12d2`) into E_R's driver, lines marked `# G2R`. With
  the flag off, E_R's driver is unchanged in behaviour (G1). The flag requires `--universe` and `--use-weights`, checks
  the npz's universe, entry count, omnifile realpath and size, and records its path and sha256 in the run's provenance.
- **The override builder:** P5's `build_miss_override.py` (`7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b`)
  extended to all 175 universe columns in one pass. P5 aligned per playlist block using the per-playlist files for
  the block sizes; if those files are no longer on disk, that is a STOP to the director before any unfold, not a
  repair.
- **The block and regrade script:** imports `re2c_rollup`, `cov2d_blocks`, `cov2d_null`, `fd_1b_null` and `t2a_split`;
  writes one record per point with the §3 readings, and one per tune with the verdict and readouts.
- **Required mutants:** the flag silently ignored; the override applied to a passing row; a universe's override taken
  from another universe's column; ε computed on the full space instead of the retained eigensystem; the regrade
  reading the old C_T; the null left at the old laws.

## 10. The outcome table, fixed now, before any number is read

**Part (a), at the data:**

| (a) | the reported 2D covariance | limitation 7 |
|---|---|---|
| **VALID** | **Proposed for Joseph:** the corrected covariance C_new replaces C_rep in the paper and the note, whatever ε reads, since it is the declared procedure with the approximation removed. The numbers it feeds (the 6.41 % and 4.76 % uncertainties, and every quantity graded against the 2D covariance at the data) are recomputed from it. The §3 readings are reported in the note, and ε with its floor in the response to the referee. | removed. The covariance text states that the systematic-universe unfoldings weight each missed event at its universe's truth weight. |
| **INVALID / STOP / not run before 2026-12-19** | unchanged | stands, with one added clause: a consistent rebuild was attempted and produced no reading |

**Part (+), the regrade at G18 and AR23** (COV2D's rule; the headline sentence is the abstract's "The procedure's
two-dimensional covariance, rebuilt at each of two held-out generator tunes, under-covers at both", limitation 1's
"The procedure's two-dimensional covariance under-covers at both held-out tunes (section 6.2)", and §6.2's "It
under-covers at both tunes"):

| case | G18 | AR23 | the headline 2D under-coverage sentence | §6.2, table 5 and the decomposition |
|---|---|---|---|---|
| **unchanged** | UNDER-COVERS | UNDER-COVERS | **Stands.** It now grades the corrected procedure. | Every number is replaced by the regrade's (counts, thresholds, χ²/ndf, ndf, flagged cells, attribution, false-flag rate, the decomposition's parts and the truncated counts). The note records the first grade as superseded. |
| **changed at one tune** | one of COVERS / UNDER-COVERS | the other | **Replaced** by a per-tune sentence: it under-covers at the tune that under-covers, and no under-coverage is detected at the other. The text states that the first grade, with the approximation, under-covered at both, and that the change at that tune follows the correction. | As above, per tune. |
| **changed at both** | COVERS | COVERS | **Replaced:** no under-coverage is detected at either tune. The abstract's clause and limitation 1's sentence are rewritten to that. The text states that the first grade, with the approximation, under-covered at both. | As above. The decomposition is reported as for any pass. |
| **INVALID at one tune** | INVALID or a verdict | a verdict or INVALID | The valid tune reads by its own row above. For the INVALID tune, the sentence keeps the first grade, labelled as graded with the approximation, and limitation 7 states that its consistent regrade produced no reading. | The INVALID tune keeps its first-grade numbers, labelled. |
| **INVALID at both, a STOP, or not run before 2026-12-19** | | | **Unchanged.** Limitation 7 states the approximation, the attempt and that it produced no reading. | Unchanged. |

**In every case:**
- **The conditional scope stays** (consult item D, COV2D-DECLARATION §12-13): the result concerns the procedure's
  covariance at two held-out tunes, not the reported intervals at the data; the run-period block is not drawn; G18
  shares its 2p2h model family with a C_model generator; the earlier fixed-truth failure stays in the Limitations.
- **A pass does not license** a claim that the learner, regularization or other limitations are addressed (consult
  item D). Limitation 8 (the miss regressor's equal event weights) is a different approximation, and is untouched.
- **Which implementation each result uses** is stated (consult item D, first bullet): the covariance at the data, C_T
  at each tune, and the regrade all use the corrected propagation, or the text says which does not.
- **The wording** is drafted by the paper lane when the result lands, read by a PRD referee and by Joseph before merge.
  This table fixes what each case must say, not its words.
- **(a) and (+) are read independently.** If (a) is VALID and (+) INVALID, the covariance at the data is corrected and
  the coverage sentence is labelled as graded with the approximation. If (a) is INVALID and (+) VALID, the coverage
  sentence follows (+), and the covariance at the data keeps limitation 7.

## 11. For the auditor

- **§2 is the claim to attack.** It rests on three code facts: `ARRAYS` maps the truth to `mc_truth_denom`; the writer
  writes passing rows only; toys unfold with the CV file. Any route by which a miss row's proxy reaches a toy's draw,
  its truth or its unfold voids it.
- **§1's scope:** whether any of the 175 universes is a lateral read through `--universe` with shifted kinematics
  (`re2_driver._universe_kine_branches`). If one is, its miss rows' proxies are in play too, and the override covers it.
- **§7's unit:** COV2D's 44.67 node-h for 350 unfolds, against helper-3's 35-run basis.
- **§10:** whether each case's effect on the headline sentence is the only one consistent with COV2D-DECLARATION §12.

## 12. For the director

1. **The price (§7) is Joseph's:** about 68–71 node-h expected, held 108.8, cap proposed 110, against the ~10 he
   confirmed. It matches the G2 repair price on record (43–129).
2. **Adopting C_new at the data (§10, part (a) VALID)** is proposed, not decided: it changes reported numbers, which
   is Joseph's.
3. **The cheaper reuse variant (§7)** is offered, not assumed.
4. **The schedule:** after the maintenance and LL5D's gates, and before 2026-12-19 for every `$UNI` read.

Nothing is submitted, deposited or tagged.
