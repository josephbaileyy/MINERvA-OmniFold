# T2A receipt: COV2D's joint under-coverage, split into bias and fluctuation in C_T's eigenbasis, and the joint test truncated at ranks 73 and 139 (2026-11-10)

**By** the valid-region lane (director-helper-2), under
[`T2A-COV2D-SPLIT-DECLARATION.md`](../T2A-COV2D-SPLIT-DECLARATION.md) (`be83886d…`), [`T2-BINDING-1.md`](../T2-BINDING-1.md)
(M_T2 `3bb2a96c`) and its addendum 1 (A1's χ² tolerance; the precision readout).

**The director's gos:**
- the capture tool `capture_e.py` `dfee305e…` (tool commit `edd1bed05f32d7e2cc05d77f940b79a125b38a29`, PR #1037),
  reviewed by the cov2d session with no objection;
- `t2a_connect.sh` `b2e39ada…`, `cov2d_fence.sh` `16a2a5cd…` and `t2a_launch.sh` `516565ac…`;
- the read-only status check `t2a_status.sh` `609dbea2…` via `t2a_status_launch.sh` `751df58d…`;
- the split `t2a_split.py` `462ff4e2…`.

**The results:**

| record | sha256 |
|---|---|
| [`t2a_AR23.json`](t2a_AR23.json) | `33b7fd401a42b093ed1069925be74a9f3ec6a65da5ee77f36215f3739d3a6fd1` |
| [`t2a_G18.json`](t2a_G18.json) | `6757055ee3ca3101055e7fa52e15edae8be4cc7c578fe7e34c6c3568f07e6389` |
| [`t2a_AR23.png`](t2a_AR23.png) | `d45767aa5b88aab77756010a9a9afaa655ff6265d4bca7de8d07b095eaf20aab` |
| [`t2a_G18.png`](t2a_G18.png) | `b85b7b816fab2a538f1316eed5958147db396ae83279ff459d0b3d041fae1d85` |
| [`AR23/E_AR23.npz`](AR23/E_AR23.npz) (force-added: `*.npz` is gitignored) | `ccda9c50c6bb1cbbdd2206c8954652f4f77c6cf2b4451e8488601e9896b0a85e` |
| [`G18/E_G18.npz`](G18/E_G18.npz) (force-added) | `846b9d852218b531d605bd955ca9a9037d187e74723077bdfff4557efafc3ba6` |

- Every control passed at both tunes: A0 in the capture, and the pins, A1, A2, A3 and A4 in the split.
- **This receipt makes no reading of the numbers.** The director makes the one reading, from this committed record
  (binding ruling 4).

## MEASURES / CANNOT AUTHORIZE

- **MEASURES,** at each tune, on the 300 error vectors the bound grade used:
  - the mean χ² split into ēᵀC_T⁺ē and tr(C_T⁺S);
  - the whitened components against C_T's eigenvalue rank;
  - the joint in-region count truncated to C_T's top 73 and 139 eigenpairs, each against a null drawn on the bound
    null's own draw stream;
  - a precision readout comparing two LAPACK drivers.
- **CANNOT AUTHORIZE:**
  - a change to COV2D's verdict, its rule, C_T or the null;
  - any paper or note wording.

## CITABLE FOR

- A **descriptive** decomposition, at each of the two tunes, of the recorded mean χ² into ēᵀC_T⁺ē and tr(C_T⁺S), with
  their shares.
- The **per-rank** whitened bias and fluctuation profiles, as descriptions, at the ranks the precision readout does not
  mark unresolved.
- The **truncated joint counts** at ranks 73 and 139, each beside its rebuilt null's k_joint, as descriptions.
- **Whether those counts agree between the two drivers** (the precision readout).

## NOT CITABLE FOR

- **A new verdict.** A truncated count at or below k_joint, or above it, neither replaces nor softens UNDER-COVERS.
- **A cause** of the joint under-coverage or of any flag. A bias share is a description, not a cause.
- **Coverage of the reported intervals at the data's point,** or anything about truths unlike these two.
- **Anything about the published covariance,** whose counts 73 and 139 are borrowed as ranks only.
- **C_T⁻, C_PL_R or C_model.**
- **Any per-rank value marked numerically unresolved** (addendum 1).

## 1. The capture (one login-node connect, 0 node-h)

- **The survey** (`connect/login-survey.txt`, 17:36:04Z): one read-only ssh session reading `/proc/loadavg`, and
  stat of the two explicit /dev/shm work paths.
  - login21 was the quietest, at 19.05 / 19.82 / 18.93 on 244 cores, and neither work path existed there.
  - The others: login27 21.33, login37 29.96, login33 36.42, login02 55.60 and login05 62.12.
- **The fence** (`connect/fence.session.out.txt`, login21, 17:37:07Z): `FENCE CLEAR`.
  - squeue held only `61078463 ll5d_gate_G18 PENDING` and `61078506 ll5d_gate_AR23 PENDING`.
  - Of 28 cov2d/t2a sacct rows in 14 days, none was unended.
- **The connect** (login21, launched 17:37:19Z).
  - The remote run's own log is `connect/status.out.txt`, whose last ~150 lines are `connect.log` in full.
    `connect/connect.log.tarball-snapshot.txt` is the copy inside `post.tar.gz`, taken before the final lines.
  - Per tune, AR23 at `ac25b665` and then G18 at `b1d56e4f`:
    - 300 of 300 toys present and non-empty, by stat;
    - porcelain 0 at M;
    - `READOUT-SHA OK` (`d1a3cff9…` and `0c3ad137…`), `NULL-ON-MAIN OK`, `SCORE-ON-MAIN OK` (`fe5263e9…` and
      `84976694…`) and `CAPTURE-SHA OK`;
    - MAT `{"mat_setup_scripts": 6, "mismatches": 0}`, MnvH1D preflight 14 bins, Python 3.11.14, numpy 1.26.4,
      ROOT 6.28/12;
    - phase S printed `COV2D-SCORE <T> UNDER-COVERS`, its own verdict re-printed, which A0 shows equal to the committed
      record. It is not a T2A reading.
    - `T2A-CAPTURE <T> OK rc=0: A0 EQUAL; E written`, with walls 0:10.96 (AR23) and 0:11.53 (G18) and max RSS about
      0.40 GB;
    - porcelain 0 after, blobs unchanged, the copy to `/pscratch/sd/j/josephrb/t2a-20261110/<T>/` verified, and
      `/dev/shm/josephrb-cov2d-s-<T>` removed (rc 0).
  - `t2a connect rc=0` at **17:38:48Z**.
- **The session drop.** The Mac's ssh returned **rc 255 at 17:40:43Z**, with no "script rc" line and no ssh error text
  (`connect/connect.session.{out,err}.txt`).
  - The remote run had finished before that, at 17:38:48Z. No cause is claimed.
  - The director observed GitHub API timeouts from this Mac around that time, and records it as an observation, not a
    cause.
  - The lane stopped and retried nothing.
- **The status check** (`connect/status.out.txt`, the director's go, login21, 18:07:47Z) showed:
  - no capture or connect process left, and neither work path present;
  - `connect.done` = 0, the per-tune `out.sha256`, and `connect.log` complete.
- **The fetch** (`connect/fetch.scp.*`, 18:08:10Z to 18:08:23Z, scp rc 0):
  - `post.tar.gz` `72d9ef4d…` equals the node's;
  - it was unpacked under python -I into a new empty directory, regular files only, with names matched;
  - all six product files equal the node's `out.sha256` (`<T>/out.sha256.txt`).
- **The capture records:** `AR23/capture_AR23.json` and `G18/capture_G18.json` read `status` OK and `A0.equal` true,
  with 20 (AR23) and 22 (G18) fields compared and only `utc` and `host` excepted.
  - E is 300 × 205; the wrapper is `dfee305e…`; the committed score shas are `fe5263e9…` and `84976694…`.
- **The regenerated score records stay on pscratch** at `/pscratch/sd/j/josephrb/t2a-20261110/<T>/score_<T>.json`:
  `6727758d…` (AR23) and `6c159659…` (G18). A0 found each equal to the committed record field for field, utc and host
  excepted, so they duplicate committed records and are not added here.

## 2. The LAPACK measurement, and addendum 1

**What was measured.** Before the split ran, the lane measured how much `fd_1b_null.chi2_nonnull`'s mean moves
between LAPACK paths on the committed C_T alone (`code/lapack_sensitivity.py`, `run/lapack_sensitivity.out.txt`).
- It used 300 synthetic error vectors (N(0, C_T) draws plus a 0.3 σ_c offset), not the toys.
- **A different driver** (scipy `eigh(driver="evr")` against numpy's `eigh`) moved it by 4.0e-9 relative (AR23) and
  9.0e-10 (G18).
- **Eps-level symmetric perturbations** of C_T moved it by 6e-9 to 8e-8 (AR23) and 2.7e-8 to 1.3e-6 (G18).
- **The cause:** C_T's λ_min/λ_max is 9.99e-13 (AR23) and 1.05e-12 (G18).
- **The consequence:** T2A §4's A1 χ² tolerance of 1e-12 could not hold across machines.

**What addendum 1 changed.** The director's addendum 1 set A1's χ² comparison to COV2D A5's rule,
max(1e-9, 10·κ₂(C_T)·eps). The pulls stay at 1e-12, the counts and ndf exact, and A2 at 1e-12. It also added the
precision readout (§4).

## 3. The split's controls (`t2a_<T>.json` `controls`; `run/stdout_<T>.txt`)

The split ran under `python3 -I -B`: Python 3.12.2, numpy 1.26.4, scipy 1.15.2 and matplotlib 3.10.1 (`run/env.txt`).
AR23 ran 18:15:38Z to 18:17:05Z, and G18 18:17:05Z to 18:18:37Z (`run/run.log.txt`).
- **The inputs:**
  - E and the capture from the verified fetch;
  - blocks, score and null as `git archive` copies at M_T2 (`abaebaea…`, `fe5263e9…`, `80274e52…`; `7eb657b8…`,
    `84976694…`, `6bd5259d…`);
  - the null modules from a `git archive` of `b1d56e4f` (`fd_1b_null.py` `ec1402db…`, `cov2d_null.py` `a92c0506…`,
    `cov2d.py` `76cbceba…`), byte-identical at `ac25b665`.

| control | AR23 | G18 |
|---|---|---|
| pins, and E_<T>.npz = the capture's with status OK and A0 equal | pass | pass |
| A4: E 300 × 205, finite, in TOY_SEEDS order | pass (5730000…5730299) | pass (5720000…5720299) |
| A1: ndf exact; χ² mean/ndf within A5's rule; pulls 1e-12; counts exact | pass: ndf 204 = 204; rel diff 2.0e-9 against tol 2.2e-3 (κ₂ 1.00e12) | pass: ndf 205 = 205; 6.8e-9 against 2.1e-3 (κ₂ 9.50e11) |
| A2: ēᵀC⁺ē + tr(C⁺S) = mean χ²; Σb_k, Σf_k = the parts (1e-12) | pass (4.4e-16, 2.2e-16, 0) | pass (5.6e-16, 6.7e-16, 6.7e-16) |
| A3: rebuilt full-rank q within one se_joint; chi2_cut and ndf exact | pass: |Δq| = 0 against se 3.3e-4 | pass: |Δq| = 0 against se 3.2e-4 |

- **What A3 was checked at:** n_mc 2,000,000, chunks of 100,000, seed 5,742,000 (`controls.A3.detail.checked_at`).
- **What A3's exact agreement means.** The rebuilt q equals the committed one exactly. So the one-pass loop drew the
  bound null's sequence, and the truncated statistics were taken on those same draws (ruling 2).

## 4. The records' layout, and the precision readout's definition

- **`split`:** `mean_chi2`, `ebar_Cplus_ebar`, `trace_Cplus_S`, each also over ndf, and the share of the first part.
- **`by_rank`:** λ_k/λ_1, b_k = z̄_k² and f_k = var(z_k) (ddof 0) for k = 1..ndf by descending eigenvalue, and
  cumulative sums at 73, 139 and ndf.
- **`C_T_counts`:** C_T's own eigenvalue counts above 10⁻⁴ and 10⁻⁶ of λ_1, beside the fixed ranks.
- **`truncated.<k>`,** for k ∈ {73, 139}:
  - the in-region count of 300, k_joint and `at_or_below_k_joint` (no verdict word);
  - the null's q, se and joint size;
  - the mean χ²_k/k, with its two parts.
- **`precision`** (addendum 1, descriptive): numpy `eigh` against scipy `eigh(driver="evr")` on the same C_T and E.
  - Per rank, **d_k = max(|Δb_k|, |Δf_k|) / (b_k + f_k)**, normalised by the component's mean square under numpy's
    basis. The director confirmed this normalisation.
    - The reason: b_k and f_k are invariant to an eigenvector's sign, and the denominator stays well-defined where
      b_k ≈ 0, where a bare relative Δb_k would not.
  - A rank with d_k > 1% is listed in `unresolved_ranks` and drawn as a red × on the figure. No reading is made from
    it.
  - Also recorded: the toys' truncated counts at 73 and 139 under both drivers, with `agree`; both drivers' ndf; the
    largest eigenvalue difference; and the split's two parts under evr.
- **The figures:** b_k and f_k against rank on a log scale, with λ_k/λ_1 on the second axis, the line at 1, and
  markers at 73 and 139.

## 5. The code and its tests

- **The tool:** `capture_e.py` and its 12-case test are in the tool commit `edd1bed0` (PR #1037).
- **In `code/`:** `cov2d_fence.sh`, `t2a_connect.sh` (byte-equal to the copy the connect saved on pscratch),
  `t2a_launch.sh`, `t2a_status.sh`, `t2a_status_launch.sh`, `t2a_split.py`, `test_t2a_split.py` (`ecf92cea…`) and
  `lapack_sensitivity.py` (`cdd24a55…`).
- **The split's test** (`run/test_t2a_split.out.txt`, `ALL PASS`, run before the go) uses the real committed
  `blocks_AR23.npz` with a synthetic E.
  - Its null record is the bound `null_contents` at n_mc 200,000. In the clean case the script's rebuilt q equals it
    **exactly**, which checks that the one-pass loop consumes the bound null's draw stream.
  - Each defect stops on its control:
    - a 1% χ² drift stops at A1, and so does a count changed by one;
    - reversed seeds stop at A4;
    - a null q moved by 3·se stops at A3;
    - a wrong capture sha stops at the pin.

Nothing is submitted, deposited or tagged.
