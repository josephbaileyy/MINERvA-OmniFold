# DECLARATION 1B gate-D diagnosis: readouts, the localization rule, a time-box and the fork (2026-11-01)

**By** the measurement session `coverage-5b`, for the director to bind.

**Under** `DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md` (#623), item 2: "a diagnosis of gate
D at 0 node-h, then a fork fixed before any number is read". It follows
[`FD-1B-STAGE2-REPORT.md`](FD-1B-STAGE2-REPORT.md) (#618), where gate D read FAIL.

**ASKS TO AUTHORIZE:**
- one run of `nd-unfolding/fd_1b_diag.py` on a login node (0 node-h), from the 176 derivation products and S1's
  assembly already on pscratch;
- its readout, committed with a report;
- the fork of §4, applied as written.

**CANNOT AUTHORIZE:**
- any job;
- a toy redesign or a rerun of gate D (the fork's "localized" branch is an amendment with its own declaration,
  price and binding);
- any change to gate D's window, the tested matrix or a claim.

**Fixed already** (the decision):
- the [0.9, 1.1] window is not relaxed;
- the matrix 1B tests stays C_total + C_resp of `fd_data_product.json` (`b79556f0…`), without the run-period block
  (`FD-1B-DECLARATION.md` §2);
- the stopped attempt is disclosed in every outcome.

**What has been read before this declaration.** Only gate D's committed readout (`run/score/gate-d.json`,
`e1838c0a…`): ρ_c and the per-group σ ratios, already reported in #618.
- No per-band ratio, raw shift or g = f/x_T has been computed. `fd_1b_diag.py` has met synthetic fixtures only.
- Two things are known from #618: the flux group's ratio lies outside the window in 9 cells, and the detector
  group's in 3. So the rule below lets a named set include any of the 38 bands, not only interaction ones.

## 1. The readouts (`fd_1b_diag.py`, all labelled DERIVATION)

The computation is gate D's own: `fd_1b_score.derivation_blocks`, factored out of `cmd_gate_d` with its result
unchanged and its tests passing. It computes each band's block with S1's estimator over the noise-free derivation
unfolds; uncarried, E_raw,b; and carried by diag(g) with g = f / x_T, E_b. S1's blocks are M_b, and M_d is S1's drawn
matrix.

The run refuses (exit 4) unless the `--gate-d` file is the committed readout (sha256 `e1838c0a…`, pinned in code)
and its ρ equals that readout's ρ bit for bit. The readout records `fd_1b_diag.py`'s own sha256.

- **(i) Per band, all 38 bands** (Flux; the 33 interaction bands, 2p2h with 3 universes and 32 with 2; the 4
  detector bands), per cell c:
  - the carried σ ratio √(E_b,cc / M_b,cc);
  - the raw σ ratio √(E_raw,b,cc / M_b,cc);
  - S1's share M_b,cc / M_d,cc and the toys' share E_b,cc / E_d,cc.
  - Where S1's diagonal M_b,cc is zero, a ratio reads "inf" if the toys' is not zero and null if both are. No rule
    reads these ratios.
- **(ii) The raw shifts without the carry:** ρ_raw,c = √(E_d,raw,cc / M_d,cc), with every band's block uncarried and
  S1's stat, normalization and lateral blocks as in gate D.
- **(iii) The carry against ρ:** g_c beside ρ_c and ρ_raw,c, per cell. This is descriptive, with no verdict of its
  own.

## 2. What counts as a localized cause: a rule a readout satisfies or fails

- **L1, named bands.** Some set B of at most **K_MAX = 3** bands, of the 38, satisfies the rule if putting S1's
  diagonal in place of the toys' for every band in B,

      ρ_c(−B) = √( (E_d,cc − Σ_{b∈B} (E_b,cc − M_b,cc)) / M_d,cc ),

  puts **every** cell's ρ_c(−B) in [0.9, 1.1].
  - Sets are searched by size, 1 then 2 then 3, and the smallest size with any such set is the minimal size.
  - Every minimal set is counted, and their union and intersection are taken over all of them. Up to 200 are listed.
  - **L1 PASS** if minimal sets exist **and their union has at most K_MAX bands**. Those bands are the named
    bands. A union larger than K_MAX reads L1 FAIL: the departure is then diffuse, not named.
  - The window is inclusive at both edges, as in gate D.
  - The numerator is a sum of covariance diagonals (the fixed blocks, the toys' outside B, S1's inside), so it is
    never negative.
  - L1 cannot pass trivially, since gate D failed and the search starts at size 1.
- **L2, the carry.** ρ_raw,c lies in [0.9, 1.1] in **every** cell.
  - A PASS means that removing the carry closes the gap. It does not show that the carry is wrong.
  - Uncarried is the only alternative tested, and it is tested for all bands at once. A carry problem in only some
    bands is a question for the amendment.
- **LOCALIZED** if L1 or L2 passes, and the readout states which. Otherwise **NOT LOCALIZED**.

**Two choices for the director to bind:**
1. **K_MAX = 3.** A cause that needs four or more of the 38 bands substituted is not named bands in any useful
   sense. It is a constant in `fd_1b_diag.py`, pinned by a test, so another value needs a code change and a new M3.
2. **The band scope: all 38 bands,** not only the interaction group the decision names for readout (i). The
   decision's fork says "named bands" without a group. #618 had already published the flux group outside the window
   in 9 cells, and that informed this choice, which is disclosed here.

## 3. Time-box

- **One run** on login37 under `nice -n 19`, 0 node-h. It starts only after the director's binding record of this
  declaration is on `main`.
- **The deadline is 24 h from the binding record's merge.** By then the readout is committed and the report PR is
  open.
- **Failures.** A run that exits non-zero and writes no readout may be rerun **once**, after a message to the
  director giving the cause. A second non-zero exit is a **STOP**, reported unrepaired. A run that writes a readout
  is never rerun.
- **NOT DIAGNOSED** covers two cases: a run that has not ended by the deadline, and a report PR not open by then.
- **A STOP or NOT DIAGNOSED** takes the "otherwise" branch of §4.

## 4. The fork, fixed before any number is read

- **LOCALIZED:** an amendment follows, with its own declaration, price and binding. It redesigns the toys for the
  named bands, or the carry, and reruns gate D at the same unrelaxed window. This diagnosis does not authorize it.
- **NOT LOCALIZED, a STOP, or NOT DIAGNOSED: 1B stops** with a report.
- **Every outcome:** the report, and later the paper and the note, disclose the stopped attempt. What 1B tests stays
  the matrix without the run-period block.

## 5. Steps

**D0. This PR.** It holds the declaration, `fd_1b_diag.py`, the `derivation_blocks` factoring and its tests:
`tests/test_fd_1b_diag.py`, plus `test_fd_1b.py` unchanged and passing.
- An independent read-only review of the declaration and the code is posted on the PR before the binding.
- M3 is this PR's merge.

**D1. The deploy** (a connect announced to the director): `git clone --quiet
https://github.com/josephbaileyy/MINERvA-OmniFold $B/deploy/diag && git -C $B/deploy/diag checkout --quiet --detach
M3`. The porcelain must be empty, and HEAD must be M3.

**D2. The run** (the same connect):

    nice -n 19 $PY $B/deploy/diag/nd-unfolding/fd_1b_diag.py --derivation $B/runs/derivation --tag fd1b_derivation \
      --s1-npz $P/s1-20261024/s1_assembly.npz --flux-constraint $CON \
      --gate-d $B/deploy/diag/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/stage2/run/score/gate-d.json \
      --out $B/score/diag.json > $B/logs/diag.log 2>&1; echo rc=$? >> $B/logs/diag.log

$P, $B, $PY and $CON are as in `FD-1B-STAGE2-DECLARATION.md` §2.

**D3. The report.** Copy `diag.json` and `diag.log` down to `fd/receipts-1b/diag/`, then open a report PR. It gives the readouts, L1 and L2
with their verdicts, and the fork's branch. It also gives the time from merge to report.

## 6. Not changed

The protocol, gate D's window, the tested matrix, the reported covariance, κ, every claim and number. Nothing is
submitted.
