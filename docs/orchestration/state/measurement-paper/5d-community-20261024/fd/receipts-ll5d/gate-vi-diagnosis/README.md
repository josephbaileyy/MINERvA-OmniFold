# LL5D gate STOP: why vi reports every row unmatched (read-only diagnosis, 2026-11-10)

**By** the `cov2d` session, at the director's request after the STOP of both LL5D gates (`../gate-g18/`,
`../gate-ar23/`).

- **Scope.** Nothing ran on the cluster, no bound file changed, nothing was repaired, and no sealed clip-prep file was
  opened. This receipt proposes no fix.
- **Code read.** All code is read at `a95cc39f7437170af0b65ba042934fad079e0ee2` (M_A1a.1, the gates' deploy).
  `fd_1b_c2.py` there is blob `0cb727612a6658f27fe14e51f8120450da581a15`, the verbatim copy from 342c0ce5.
- **INFERENCE.** Steps marked INFERENCE rest on reading code, not on the real files. The rest are code read at the
  stated lines, or the outputs of the three scripts here.

**Classification: an implementation defect. vi's row key cannot match by construction, because the two sides store
the CV weight at different precisions.** It is not a data mismatch of the kind the check exists to catch. One step,
the real files' dtypes, is INFERENCE (section 3).

## 1. What vi hashes

- **The call:** `ll5d.py:974` calls `c2.c2_vi(P, cv, fm, geo)`.
- **The two row sets:** `fd_1b_c2.py:1090-1098` (`c2_vi`) builds them for `row_match`:
  - the signal side: `inputs["MCgen"]` (5 columns) with weight `cv["wt"]`, on rows `pass_truth & (P["cells"] >= 0)`;
  - the denominator side: `bank_cv["td_pt","td_pz","td_ea","td_q3","td_w"]` with weight `world["tdw_cv"]`.
- **The key:** `fd_1b_c2.py:554-560` (`row_match`) keys each row by `cp2.row_hash` of the five coordinates and the
  weight, each cast to float64. `clip_probe2.py:77-85` (`row_hash`) mixes the raw float64 bit patterns, so a key
  matches only if all six values are bitwise equal.
- **How unmatched is counted:** `cp2.unmatched` marks each row that lies beyond the other side's multiplicity of its key.

## 2. The weights LL5D passes

- **Signal weight:** `cv["wt"] = np.asarray(inputs["w_truth"], float)` (`ll5d.py:444`), the npz's CV truth weight.
- **Denominator weight:** `world["tdw_cv"] = tdw_ref` (`ll5d.py:554`), the bank's `GEANT_Neutron_0_tdw.npy`
  (`c0ae3c18…`).
- **install_config is not the cause.** `install_config` (`ll5d.py:509-514`, called at `ll5d.py:925`) calls
  `s5e_candidate.install`, which calls `s5e_deform.install_ratio_truth(s5n_pseudo)`. That registers a truth model; it
  changes neither side. `cv["wt"]` is read raw from the npz after the install (`ll5d.py:444`), and tdw_ref is read
  from its file. So the A1a.1 install is not the cause.

## 3. The precision of each side

These are the writers at a95cc39f. The cited lines date from `923d8de6` (2026-07-02) and are unchanged since, which
is before the bkgaware bank (`07c18aee`, 2026-07-14) and before `of_inputs_5d.npz`. **INFERENCE: that the files were
written by this code.** A cluster-side read of the npy/npz dtype headers would confirm it; that read was not made.

- **Coordinates are float32 on both sides.**
  - Signal: `MCgen = np.column_stack([...]).astype(np.float32)` (`nn_dump_inputs.py:84`). `FD-CT-5B-INPUTS.md:22`
    names `nn_dump_inputs.py` as the writer of `of_inputs_5d.npz`.
  - Denominator: `_f = lambda: carray("f")` (`sweep_bank_5d.py:114`) backs `d_pt … d_w` (`:165`, appended at
    `:177-181`), and `td_pt=np.asarray(d_pt)` stores them (`:218`).
  - **INFERENCE:** the same ROOT doubles rounded to float32 both ways agree bitwise, since both conversions are IEEE
    round-to-nearest.
- **The weight is float64 on the signal side and float32 on the denominator side.**
  - Signal: `wt *= pot_scale` (`unfold_nd_omnifold_unbinned.py:438`) is appended as a Python float and stored as
    `np.asarray(wtl)`, which is float64 (`:466`). It is written unchanged (`nn_dump_inputs.py:97`).
    `measurement-paper/phase1/mp2/mp2_s1_dump.py:13` independently states that `w_truth x pot_scale` must equal
    `of_inputs_5d.w_truth` bitwise.
  - Denominator: `da_w[u].append(float(duw[u][0]) * pot_scale)` (`sweep_bank_5d.py:183`) goes into a `carray("f")`
    and is saved as `np.asarray(..., np.float32)` (`:185`).
  - So tdw_ref ≈ float32(w_truth × pot_scale), while w_truth is that product in float64. They are bitwise equal only
    where the float64 product is exactly float32-representable. In section 4's 200,000 synthetic weights, that never
    happens.
- **Corroboration (INFERENCE: consistent with, not proof of).** The gate's D2 control shows hist(tdw_ref) against
  the npz's `denom_nd` at a max cell relative deviation of 4.1e-4, with the total at 3.5e-12 (`../gate-g18/gate-g18.fields.txt`,
  `controls.denominator.D2`). Per-row float32 rounding of the weights averages out in the total, which is what that
  pattern implies.

## 4. Reproduction with the real row_match (`precision_probe.py`, `precision_probe.out.txt`)

The probe ran against a clean checkout at a95cc39f (porcelain 0 before and after). It builds 200,000 synthetic rows
stored as the writers store them: float32 coordinates on both sides, a float64 signal weight and a float32 denominator
weight.

| case | signal unmatched | truth unmatched | largest share |
|---|---|---|---|
| the writers' precisions | 200000/200000 | 200000/200000 | 1.0 |
| control: both weights float64 | 0/200000 | 0/200000 | 0.0 |
| control: both weights float32 | 0/200000 | 0/200000 | 0.0 |

0 of the 200,000 float64 weights are exactly float32-representable. This reproduces the gate's shape: 100% unmatched
in every cell. The two truths come out identical because vi uses neither the truth nor the draws.

## 5. The tests and the mutants

<!-- absence-ok: scoped statements about what named tests and one named mutant file assert, each read at a95cc39f at the cited lines; not a claim that a result does not exist -->
- **RealChain** (`test_ll5d.py:1275`; `run_vi.py`, `run_vi.out.txt`):
  - the real-chain gate gives vi signal 2980/2980 and truth 50/50 unmatched, share 1.0, every evaluation reads
    "option (3)", and the verdict is STOP;
  - in this fixture that is by construction: `td_*` are drawn uniformly, independent of `MCgen`
    (`test_ll5d.py:1292-1293`), and there are 50 td rows against 2,980 signal rows. This fixture cannot tell the
    mechanisms apart.
- **Two tests accept STOP and assert nothing on `record.vi`:** `RealChain.test_gate_main_runs_the_real_chain`
  (`test_ll5d.py:1405-1413`) and `Jobs.test_a_gate_over_the_toy_world` (`:1154-1166`) both accept
  `verdict in ("PASS", "STOP")`.
- **The equality test pinned an all-unmatched vi.** `A21Equality.test_the_all_path_equals_a21s_bitwise`
  (`:1457-1481`) calls `c2_vi`, but it asserts only equality with A2.1's reference vi. That reference is itself share
  1.0 on its fixture, 2980/2980 and 50/50 (`run_a21_vi.py`, `run_a21_vi.out.txt`).
- **The missing test:** no test runs vi on a fixture whose signal rows ARE the denominator rows, built with the
  writers' dtypes. That is the test that should have existed.
- **The mutants:** `tests/ll5d_a1a_mutation.py` carries no mutant on `c2_vi`, `row_match`, `tdw_cv` or the vi key.
  Its one related mutant, "a failing reading passes" (line 119), forces `ok` at `ll5d.py:1016`.

<!-- absence-ok: a stated search over committed receipts on origin/main at the stated sha; the claim is scoped to that search -->
**No earlier real-data vi was found.** Search: `git grep -l 'signal_rows_unmatched\|largest_cell_unmatched' origin/main -- docs`
@ `fd10736458b9e7db5b0b08aeb758ec2aa383361c` finds only COV2D's clip-probe-2 (`receipts-cov2d/clip/`) and this
receipt tree. As far as committed receipts show, LL5D's gate is the first real-data run of `fd_1b_c2.row_match`.

## 6. Why COV2D's 0% does not contradict this

`clip_probe2.py:201-215` reads both trees from one ROOT file, `mc_truth_denom` and `mc_signal_reco`, with uproot. It
keys both on the same branch, `w_truth`, in float64 (`c2-connect-c2.log:14`: 0 unmatched of 32,849,103 rows on each
side). The two sides there share a precision.

## 7. The 2,801 phase-space rows (unmeasured)
<!-- absence-ok: a scoping statement that one count was not measured in this read-only diagnosis (a cluster read it was not authorized to make); not a claim that a result does not exist -->

- **COV2D's phase space:** `in_ps = rc.truth_cell(pt, pz) >= 0` on the ROOT signal tree's float64 rows
  (`clip_probe2.py:219`). These are 2D cells, with no pass_truth and no eavail/q3/W ranges.
- **LL5D's phase space:** `in_ps = pass_truth & (P["cells"] >= 0)` (`fd_1b_c2.py:1095`), with
  `cells = flat_cells(MCgen, 5D edges)` (`ll5d.py:371`; `flat_cells` at `:180-190`). Against COV2D's this adds:
  - pass_truth;
  - the eavail/q3/W edge ranges (-1 outside);
  - float32 coordinates at the pT/pz box edges;
  - the npz's own row filter: finite, 0 ≤ w < 1e4 (`unfold_nd_omnifold_unbinned.py`, `collect_signal_nd`).
- **truth_rows agree,** 32,849,103 in both, which is consistent with the same denominator set: `sweep_bank_5d.py:172-175`
  filters finite, 0 ≤ w < 1e4 and the 2D box.
- **Not established:** which of these terms makes up the 2,801. That needs a per-term count over `of_inputs_5d.npz`,
  a cluster read that was not made. The 2,801 does not drive the STOP, since the share is 1.0 regardless.

## Files

- **The scripts:** `run_vi.py`, `run_a21_vi.py` and `precision_probe.py`. Each takes the path of a checkout's
  `nd-unfolding/tests` (or `nd-unfolding`).
- **Their outputs:** `run_vi.out.txt`, `run_a21_vi.out.txt` and `precision_probe.out.txt`, each headed by its command,
  the checkout's head and porcelain, and the Python and numpy versions.
- **How to re-run:** from a clean checkout at a95cc39f, with `PYTHONHASHSEED=0 python3 -I <script> <checkout>/nd-unfolding/tests`
  (`precision_probe.py` takes `<checkout>/nd-unfolding`).
