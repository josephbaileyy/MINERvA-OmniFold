# D-ID final numerical verification: same fresh read-only reviewer, result commit `d03a2c72`

The lane owner records this file. The reviewer's final message is reproduced below with its formatting
condensed (lists rejoined, markup escapes removed); the findings, numbers and verdict are unchanged.

The verification was interrupted once by an API session limit, from about 06:50 to 09:32Z, and then
resumed from the reviewer's own scratch. It counts as the same verification activity. The reviewer's
code (`vA_rows.py` … `vE_sens.py`) stays in the owner's session scratch and is not tracked. It used no
part of `did.py`.

---

**Verdict: PASS.** Every consequential reduction and all three branch outcomes were reproduced from the
real inputs with my own code, with no disagreement; branch C holds in J, EW and H2 with the owner's
exact eligible counts and shares. One interpretive caveat applies: H2 rests on two acceptance-hole
functionals out of three.

**(a)** Worktree `.../scratchpad/review-9203add1`, clean, moved read-only to
`d03a2c7209cd4627462c1072ee1ee32e94c42bec`; it adds only `outputs/` and a one-line edit to
`review-admission.md`. I read `results.json` (decision, labels, grids, controls, convergence),
`tables.npz` and `run-record.json`. Real inputs: the MC members of `nd-unfolding/of_inputs_5d.npz`
(`MCgen`, `MCreco`, `pass_reco`, `pass_truth`, `w_truth`, `w_reco`, `denom_nd`, `flux`, `data_pot`,
`n_nucleons`, edges); `measured` and `measured_weights` were never opened, not even their headers. Also
the five receipt-limited study-K traces and the synthesis operands. Imported: the committed reweight
dispatch (`s5n_pseudo.truth_weight` after `s5p_converge.install()` and `s5p_truths.install()`),
`xsec_nd`, `s5c_coverage.reported_functionals` (185 rows), and `comparator.py` (`classify`,
`branch_outcome`). My own code, with no `did.py`: 5D binning, T1/T2 grids and split edges, responses, the
known term b, IBU, fine-cell-share projection, Fisher with b in the variance, CR widths and null cut,
acceptance holes, sensitivity flags, pooling, per-functional convergence.

**(b) Reproduced.**
- Rows and grids: 32,849,103 MC rows (all `pass_truth`); 20,402,110 pair rows; 2,801 truth-out-of-grid
  rows; 10,499 reco cells; T1/T2/T3 = 134/1,383/10,694 non-empty cells. The reweight is exactly 1
  outside the grid for all six sets; b is identical across sets (total 388.92).
- S_dep for GiBUU: 92,363.62732713955, equal to the receipt.
- Nominal control: my same-sample nominal IBU agrees with the tables to 4e-15 (T1) and 2e-15 (T2) at
  K = 5; the driver's C1 is ≤ 1.7e-13.
- r_IBU per functional (180 finite each): T2/nom/K = 5 for all six sets, max |Δr| ≤ 3.1e-15; GiBUU
  T2/nom K = 40, 1.0e-14; T1 nominal and departure and T2 departure, 1.7e-9 to 2.9e-8 (float32
  storage; only T2/same/nom is float64).
- CR widths, nominal and departure, all five departures: σ_rel ≤ 1.7e-11. The infinite/NaN pattern is
  identical (178 finite at T1, 148 at T2). Acceptance holes match with 0 mismatches: T2 has 12
  zero-efficiency cells and 30 functionals touching them; T1 has 1 cell and 2 functionals. Medians over
  reported functionals: T1 J 11.5–12.8% (no infinities), EW 3.1–3.3% and H2 3.0–3.6% (one infinity
  each); T2 J 24.2–25.9%, EW 28.3–30.2%, H2 19.8–22.8% (infinities J 7, EW 12, H2 11 per departure).
- r_GBDT(K = 5) from the traces (GiBUU, W1, W3, q3) and the W2 operand mean equals `gbdt/<ws>/K5`
  exactly (Δ = 0).
- Labels and sensitivity: my T2-nominal, T1-nominal and T2-departure labels and the sensitivity flags
  give 0 mismatches against `decision.labels` (all departures, all maps).
- T2 convergence (my own IBU to 10⁵, nominal): no run converges. Largest cell change 1.50e-3 (GiBUU),
  6.82e-3 (W1), 7.38e-3 (W3), 7.23e-3 (q3), 2.58e-4 (W2), as in the driver. Per-functional
  convergence (AM-26): 48/18/26/15/93 functionals, 0 flag mismatches. r_IBU(∞) agrees to ≤ 1.2e-12.
- Branch outcomes with my own r_IBU(∞), pooled `branch_outcome`:
  - J: 144 eligible, C 0.840 / A 0.014 / B 0 → C;
  - EW: 23 eligible, C 0.870 / B 0.130 → C;
  - H2: 3 eligible, C 1.0.
  - Without W2: J 134 and EW 19 eligible, C in both, shares exact.
- The EW B set is identical:

  | functional | r_GBDT(5) | r_IBU(∞) | step | reading |
  |---|---:|---:|---:|---|
  | GiBUU EW40 | −0.105 | 1.1e-4 | 5.0e-11 | tracks at K = 40 (−0.0721 vs −0.0671) |
  | W1 EW40 | −0.046 | 3.9e-4 | 9.6e-11 | tracks (−0.0330 vs −0.0301) |
  | W2 EW19 | −0.032 | −9.7e-4 | 2.0e-11 | untraced |

  W1's step of 9.6e-11 sits just inside the 1e-10 criterion; this is not consequential, since EW's B
  share is far below C either way.

**(c) Disagreements, defects and interpretive points.** There is no numerical disagreement and no
defect. Interpretive points:
1. Resolution-sensitive exclusions dominate. Of the |r_GBDT| > 2% functionals, J 232/376, EW 129/152
   and H2 63/66 are excluded. In J the flips are mostly T1 vs T2 (148 iteration, 112 identifiability
   flips) rather than weightings (67 / 2). 177 of the 232 are weakly identified at T2. Each C verdict
   therefore concerns the label-stable minority, and the widths roughly double from T1 to T2.
2. Acceptance holes inside C: every σ = ∞ C-labelled eligible functional is an acceptance hole (J 4/121,
   EW 4/20, H2 2/3). The finite-width C share is J 0.812 and EW 0.696, both still C. For H2 it is
   0.333, so the H2 outcome rests on two acceptance-hole functionals out of three eligible and should
   be described so. MINOR (interpretation); the reproduced outcome does not change.
3. The quoted H2 T2 median range "≈ 20–23%" has q3 at 19.75%: trivial rounding.

**(d) VERDICT: PASS.**
- Reproduced: cell counts, S_dep, the nominal control, r_IBU(K = 5; K = 40 for GiBUU), σ_rel with its
  infinities and acceptance holes at T1/T2, r_GBDT, all labels and sensitivity flags, r_IBU(∞) with
  per-functional convergence, the B set and its trace readings, and the pooled branch outcomes with
  and without W2.
- Not reproduced: T3 and split-half trajectories, invisible shares, missed concentration, the C2 T1
  exactness control and P1r–P3r. None of these decides a branch.

**(e) Resources.**
- ≈ 0.23 core-h: row binning 48 s, algebra 18 s, branch/sensitivity ≈ 15 s, convergence ≈ 735 s
  over one crashed and one full attempt.
- ≤ 2 threads; peak RSS 4.15 GB (row binning).
- Scratch 42 MB in `reviewer-scratch` (including `v/binned.npz`, 43 MB on disk); the round-1
  synthetic files were deleted first.
- I removed the ignored `gbdt/__pycache__/` my `vE_sens.py` run created. `git status --porcelain
  --ignored` is empty (exit 0). The worktree is left for the owner to remove.
