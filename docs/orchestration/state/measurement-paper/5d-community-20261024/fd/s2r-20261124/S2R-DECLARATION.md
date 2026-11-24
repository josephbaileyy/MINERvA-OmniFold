# S2R: one data-usable step-2 candidate, priced and tested at both flagged truths (declaration)

**Lane:** tier3-design, 2026-11-24. **Authority:** Joseph's decision on item 5 of the codex-school advisory, relayed by
the rewrite helper and the director on 2026-11-24: a yes to step 2 as time-boxed pricing. The director accepted this
candidate and its threshold the same day, and approved route (1), a NERSC CPU job, in principle.
**Time box:** a result in hand by 2026-11-25T12:00Z. Otherwise the current estimator is frozen.

The threshold in section 3 was fixed before any run, and nothing in this study is tuned on its output.

## 1. The candidate

**S2R, the incremental step 2.** Step 2 learns its correction relative to the previous push weights:

  ν_n(t) = ν_{n−1}(t) · L[(ω_n^pull, Gen.), (ν_{n−1}, Gen.)](t).

This is Step 2 as Andreassen, Komiske, Metodiev, Nachman and Thaler define it in arXiv:1911.09107 ("2. ν_n(t) =
ν_{n−1}(t) L[(ω_n^pull, Gen.), (ν_{n−1}, Gen.)](t)"). The quote was checked against the PDF's extracted text on
2026-11-24, not taken from memory.

**Production differs.** `omnifold_nn_core.omnifold_loop` relearns the whole ratio from the prior at every iteration:
its step 2 classifies Gen weighted by w_truth against Gen weighted by w_pull · w_truth, and sets w_push to the
classifier's ratio. The vendored ViniciusMikuni/omnifold (`omnifold_nn/omnifold/omnifold.py`, RunStep2) does the same.
The two forms agree for a perfect classifier. For a finite one, the production form repeats the same underfit each
iteration, while S2R learns only the residual, so successive fits accumulate.

**Why this one.** At the q3 tilt, T3 found that even with true weights for every event, step 2 leaves ρ_OP(2) = 0.102
(T3 readout, `fd/tier3-20261110/run-20261121/cluster/read/readout.txt`). That is a limit set by step 2's
representation. Neither FD-PRR (iterations, capacity (400, 31) and (1000, 63), MC statistics, inputs) nor T3 (the miss
fills) changed step 2's reference distribution.

**Data-usable.** S2R uses only w_pull and w_push, which the loop computes from the pseudo-data and the simulation.
No truth or oracle weight reaches it. The truth reweight r enters only the recorder, to compute the readouts, as in T3.

**Implementation for this test.** No production byte changes. `nd-unfolding/s2r/s2r_arm.py` wraps step 2's
estimator, in the same way as T3's arms (`tier3/t3p_arms.py`):
- **Fit weights.** The loop's step-2 weights are first checked bitwise by `s5e_trace`, as for every arm. The inner
  classifier is then fit on [ν_{n−1} · w_truth, w_pull · w_truth].
- **Output.** `predict_proba` returns p with p / (1 − p) = ν_{n−1} · L, where L is the inner classifier's clipped
  ratio. The loop's own `_reweight` therefore sets w_push = ν_{n−1} · L.
- **Unchanged.** Step 1, the miss regressor, the refinement and the extraction are the loop's own.

At n = 1, ν_0 = 1, so S2R's first fit is B0's.

**Adoption** would change two lines of `omnifold_loop`'s step 2, behind a flag. It is not part of this study (section 6).

## 2. The test

- **Pseudo-data.** FD-PRR's B0 queue line for each truth at split 991000, through `s5p_nullexp.main`, unchanged:
  - configuration R, noise-free with background (`--expectation --no-nuisance`), MC half;
  - estimator seed 42, 32 threads.

  Only `--iters`, `--tag` and `--out` are set for the arm.
- **Tasks: six, in one CPU job on one node (6 lanes × 32 threads).**
  - B0 at k = 5 at the nominal truth, A7_gibuu and q3.
  - S2R traced to k = 20 at the same three truths.

  S2R is graded at k = 5, the production iteration count. Its trajectory to k = 20 is reported and not graded.
- **ρ** is the note's retained fraction (`prr_read.rho`, |d_i| ≥ 0.01), on R00–R15. The prior P is FD-PRR's nominal B0
  truth. Flags use F0b's grade matrices (`prr_read.grade_matrices`, with C-CT), as in FD-PRR and T3.

## 3. The pass rule (fixed now; `nd-unfolding/s2r/s2r_rule.py`)

S2R **passes** only if all of the following hold:
- ρ_S2R(5) ≤ ρ_B0(5) − 0.05 at **both** A7_gibuu and q3. Against FD-PRR's B0 values (0.1250 and 0.1785), that is
  ≤ 0.0750 and ≤ 0.1285.
- The nominal truth is **not flagged** under S2R.
- ρ_B0(5) is recomputed in the same job and equals FD-PRR's B0 products **bitwise** (C-PAIR). Otherwise the job STOPs
  and nothing is read.

An undefined ρ at either flagged truth, for either arm, is a FAIL.

The 0.05 is the prr-floor bar that FD-PRR and T3 declared. T3's floor spreads were all ≤ 0.0028, so the bar is at
least 15 times the floor. Flags, rms b, χ², p and max |z| at k = 5 are reported beside the verdict, not graded.

## 4. Controls

- **C-PINS:** FD-PRR's bound modules and probe, plus T3's `t3p_arms.py` and `t3p_probe.py` at T3-BINDING-1's digests.
- **The namespace check** on the runner's own parse:
  - configuration R, noise-free, MC half;
  - seed 42, 32 threads;
  - the declared iterations, tag, split, hypothesis, and the alternative's path, kind and amplitude;
  - the output directory, exactly `<OUT>/runs/<arm>/<truth>`;
  - no `--capacity`.
- **C-ARM** at every S2R iteration:
  - the reference is the previous push weights;
  - w_push equals ν_{n−1} · L to 1e-10 relative where neither is clipped;
  - ν_0 = 1;
  - every row of ν_{n−1} · L inside the loop's clip of p. Otherwise STOP, because the loop would saturate the product;
  - one relative fit per iteration.
- **C-PAIR (the reproduction control):** B0's k = 5 unfold equals FD-PRR's B0 product bitwise at each truth, at FD-PRR's
  thread count.
- **C-X:** every task's truth equals FD-PRR's B0 truth bitwise.
- **C-ONE:** S2R's R00–R15 at k = 1 equals B0's to 1e-12 relative.
- **T3's read controls:** C-TRACE, C-RECO, C-CT, C-P and the leak guard (no absolute value in the readout).
- **Staging:** each input is copied once through O_NOATIME and refused unless the copy is its pin (FD-PRR's
  `prr_probe.stage`).

## 5. Price and resources

- **Per unfold,** S2R costs the same as B0: the same fits on the same rows, 0.022828 CPU node-h at K = 5 (FD-PRR's
  unit).
- **The test** is one job, `s2r_run`, with `--time` 1:00:00, so the cap is **1.0 CPU node-h**.
  - The task budgets are 700 s for B0 and 2,100 s for S2R at k = 20. Each is 1.25 × (194 s + k × 72.6 s), taken from
    FD-PRR's K = 2 and K = 50 maxima. T3's dry job measured about 190 s + k × 78.5 s with its tracer.
  - The lane wall is 0.58 h. Divided by the gate's 0.9 and with 0.25 h added for staging, the least limit is 1.0 h.
  - Expected charge: about 0.6 node-h.
- **Writes:** only `/pscratch/sd/j/josephrb/s2r-20261124` (its temporary files in `tmp/` and `tmp-connect/` there),
  plus the launcher's copy of each connect script and its captured output on the login node,
  `/dev/shm/s2rc.<pid>.sh` and `.out`, which the connect deletes at exit. Nothing goes to CFS.
- **Reads:** FD-PRR's four inputs, the GiBUU fine-ratio ρ array, and FD-PRR's three B0 products at split 991000, each
  by its pin.
- **Job states** come from sacct only.

## 6. What the result can and cannot be used for

- **CAN:** whether S2R clears the declared bar at both flagged truths at k = 5, with the nominal truth unflagged.
- **CANNOT:**
  - Adopt S2R. A pass comes to the director first, with the price of new F0b bias, covariance and LL5D products,
    because adoption also changes what the (b) design freezes. Then it goes to Joseph.
  - Support any cause, or any statement about data.

The readings go to the director before anything else.
