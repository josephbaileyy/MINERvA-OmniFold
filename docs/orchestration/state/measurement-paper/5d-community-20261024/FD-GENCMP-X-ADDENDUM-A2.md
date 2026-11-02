# ADDENDUM X-A2 to GENCMP X: V1's weight lookup accepts byte-identical copies, and K1 names a band that is null on both sides (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director to bind by addendum to
[`FD-GENCMP-X-BINDING.md`](FD-GENCMP-X-BINDING.md) (addendum X-A1, bound in #672 at M′ = `f14119b1`).

**Under** two rulings of the director's, both of 2026-11-02:
- on the full V1's stop: the lookup rule in §2;
- on K1's 2D NormDISCC failure in K's dry run: explicit null bands (§3), not a tolerance floor.

Each ruling's points are restated in §6, with where each is met.

**MEASURES:** nothing new. This repairs two controls that could not pass on correct inputs. It also records the dry runs
of V1 and K that found them.

**CANNOT AUTHORIZE:**
- a change to any other control or tolerance, or to the route rule;
- a reading, a paper edit or a claim.

`$R` = `/pscratch/sd/j/josephrb/gencmp-x-20261102/`, as bound. Receipts are in `fd/xcov/receipts/` and its `a2/`.

## 1. The two defects

**V1 (the full run, job 60679146).**
- The run took 4:14 (0.0706 node-h), then stopped: "FAIL control V1: EtaNCEL:0 wt: 22 files carry its digest". The stop
  is final, and no V1 readout was written.
- `weight_files` required exactly one pinned file to carry the digest S1's product recorded for each weight. Some knobs
  leave the CC weights at CV, so several pinned files are byte-identical copies of one another.
- Any of those copies is the file S1 read: they have the same sha256, so they hold the same bytes.
- The probe (job 60678999: MaRES and Flux 0–9) did not reach such a universe. It passed.

**K1 (found by K's dry run, §4, before any K run).**
- **16-cell NormDISCC.** On CC signal the band's two universes are identical. So S1's block and its recomputation are
  both exactly zero, and `same_block` required a positive scale. Fixed in `92be5e32`: two exactly-zero blocks of one
  shape are the same block, and zero against non-zero still fails.
- **2D NormDISCC.** The band's block is floating-point cancellation noise:
  - its largest entry is 1.15e-25 of C2q's largest;
  - the two universes differ by 3.5e-13 relative;
  - the recomputed and committed quadrant blocks differ by 2.8% of their scale (`a2/x_k1_diag2.out.json`).

  `same_block` at 1e-10 cannot pass on it. The comparison has nothing to compare, because the block carries no
  information.

## 2. V1's change

- **The lookup rule.** `weight_files` takes the sorted-first of the pinned files that carry the recorded digest, and
  records how many do (`n_matches`). It still stops when none does.
- **Where V1 writes.** `fd_xcov_steps.V1_DIR` = `v1-a2`. V1 writes `$R/v1-a2/` and refuses if it exists; K reads it.
- **What V1 records.** The schema becomes `fd-xcov-v1/2`. Each weight records `file` and `n_matches`. The record lists
  each multi-match class: the digest, its file count, the universes resolving to it, and the bands they span.
- **Unchanged:** V1's test (`ratio_test`), its tolerance, the 175 universes, the omnifile reads and the route rule.

## 3. K1's change (the director's ruling)

- **The null rule** (`fd_xcov.k1_band`). A band is null on a side when every entry of both of that side's quadrant-level
  blocks is below PD_REL = 1e-12 × the largest |entry| of the side's own matrix. The two blocks are the one from the
  products and the committed one. The side's own matrix is C16q or C2q, as in K2.
- **Null on both sides:** K1 asserts that, instead of equality at 1e-10.
- **Null on one side only:** K1 fails on both sides.
- **Every other band** keeps `same_block` at 1e-10, and so does the zero-equals-zero rule of `92be5e32`. Normalization,
  C_PL and C_model blocks are not bands and are untouched.
- **The readout.** `k_compute` returns `k1_null_bands`, which lists each null band by name and side with its largest
  ratio, in the dry run and in the full K record. K prints a `[K1 null]` line for each.
- **Scope, for the director's review.** The rule applies to the 38 universe bands and the 5 lateral bands, all 43 that
  K1 compares by band. Only NormDISCC is null (§4).

## 4. The dry runs

Both dry runs ran on login37 in omnifold_py310, from a clone of this branch in `/dev/shm`, against `$R`.
- They read `$R` O_NOATIME, through the bound `Inputs` class.
- They wrote nothing under `$R`. Its listing was equal before and after each run: top level at `a6736d33`, recursive
  (by digest) after.
- The clone was deleted after each run. `$R/deploy-a1`'s porcelain was empty after.

**V1 (`v1 --dry`, at `a6736d33`; 297 s; `a2/x_v1_dry.out.json`): PASS.**

| control | real input | result |
|---|---|---|
| each weight's recorded digest is carried by at least one pinned file | 350 lookups (wt and wr) for the 175 universes, the digests as S1's product metadata records them, against the two pinned digest maps | PASS: 0 zero-match; matches per lookup {1: 322, 2: 4, 8: 8, 22: 16} |
| each resolved file exists, and its .npy header has the tree's length | the 350 resolved files (header only, O_NOATIME) | PASS: every shape (32,849,103) |
| each universe's branches exist in the universe omnifile | `w_truth_<b>_<i>`, `w_reco_<b>_<i>` | PASS (350) |
| the base arrays have the tree's length | the tree's entries; MC, MC_pz, w_truth, w_reco; the 5D MCgen | PASS (32,849,103 each) |

Multi-match classes:
- digest `df9d8727…`, 22 files: EtaNCEL, GEANT_Neutron, GEANT_Pion, GEANT_Proton, MaNCEL, MinosEfficiency, NormDISCC
  and NormNCRES;
- digest `28b168a0…`, 8 files: EtaNCEL, MaNCEL, NormDISCC and NormNCRES;
- four 2-file classes (Rvn1pi).

Before the lookups, the dry run checks the 5D npz and the universe omnifile against their pins, as the full run does.
It does not hash the 350 weight files. The full run reads each through `Inputs`, pinned to the digest it resolved to.

The probe `a2/x_v1_hits_probe.py` (on login37, before the dry run) gives the same histogram from the real digest maps. The test fixture
`tests/fixtures/xcov_v1_lookup/` is a copy of those maps (`PROVENANCE.tsv` there).

**K (`k --own-only`).** K0, K1 and K2 run on each side's own matrices through `k_compute` itself. Every cross block, the
statistical cross term, z and χ² are skipped. The small staged files go to a temporary directory.

| run at | result | record |
|---|---|---|
| `a6736d33` | stopped at "K1 16 band NormDISCC" (defect 1) | — |
| `92be5e32` | stopped at "K1 2D band NormDISCC" (defect 2) | — |
| `312022c3` (lists every control and goes on) | 101 of 102; only "K1 2D band NormDISCC" fails | `a2/x_k_own_312022c3.out.txt` |
| **`d670e9a5`** (the null rule) | **102 of 102 PASS**; 11.2 s; atime deviations none | `a2/x_k_own_d670e9a5.out.txt` |

The 102 controls at `d670e9a5`, each on its real input:

| control | real input | result |
|---|---|---|
| K0 (6) | C-R's quadrant record; `Q_R`; `cpl_block.npz`; `cmodel_2d.json`, `cmodel_R.json`, `cmodel_5d.json` | PASS |
| K1 C_model,2D's per-cell σ (1) | `cmodel_2d.json`'s vertices against `cmodel_R.json` | PASS |
| K1 universe bands (38 × 2) | S1's and RE-2's universe products against S1's and S5_R's blocks | PASS. 37 bands are equal at 1e-10; NormDISCC is null on both sides |
| K1 lateral bands (5 × 2) | S1's lateral products (MINOS scaled by X01) and RE-2's S3 products | PASS, equal at 1e-10 |
| K1 normalization (2) | A f and B x | PASS |
| K1 C_PL5D, C_PL_R from periods (2) | the periods record; `C_PL_R.npz` | PASS |
| K1 C_model_abs from vertices (1) | `cmodel_5d.json`; the data product | PASS |
| K2 own matrices PSD (2) | C16q, C2q; each side's statistical matrix | PASS |
| B replicas (2) | BOOT's 100 paired replicas (each its recorded sha256) and RE-2's 100 | PASS: 4-quadrant and 205-cell vectors |

**The null readout** (`k1_null_bands`): band NormDISCC, side 16, max ratio 0; side 2D, max ratio 1.15e-25. No other band
is null on either side. Any other null band would either be listed or fail K1 as mixed, and the run did neither.

## 5. The tests

`tests/test_fd_xcov.py` gives 60 passed locally:
- **V1Lookup** runs on the real digest maps: the histogram, the zero-match stop, the classes and `npy_shape`.
- **`test_same_block_on_zero_blocks`.**
- **`test_k1_band_null_rule`.** Both null passes, including blocks that differ by 2.8%. Mixed fails either way round, and
  either 16-cell block being non-null is enough. A block exactly at 1e-12 is not null (powers of 2 make the ratio exact).
  An informative block at 1e-11 still fails at 1 + 1e-9 and passes at 1 + 1e-12.
- **Code mutants** (`x_a2_null_mutants.tsv`): seven edits to the rule, each caught.

## 6. The director's rulings

| point | where it is met |
|---|---|
| V1: a lookup resolving to several byte-identical pinned files takes one, records the count, and zero matches still stop | §2; `V1Lookup` |
| null when every entry of the quadrant-level block is below 1e-12 × max\|C_side\|, C16q and C2q as in K2 | §3; `k1_band`, `null_ratio` |
| K1 asserts both sides null for that band, instead of equality at 1e-10 | §3 |
| the readout lists every null band by name and side with its max ratio; the report names NormDISCC | §4; `k1_null_bands`; the X report |
| null on one side and not the other still fails | §3; `test_k1_band_null_rule`; mutants |
| every other block keeps `same_block`'s tolerance, and so does the zero rule of `92be5e32` | §3; `test_same_block_*` |
| the addendum with its tables (control, real input, PASS) and receipts | this document; `fd/xcov/receipts/a2/` |
| a final full dry run of K's own side at the head shows 102/102 | §4, at `d670e9a5`. The commits after it change documents and receipts only: `git diff d670e9a5 HEAD -- nd-unfolding` is empty |

## 7. How it runs

| step | where | from | writes |
|---|---|---|---|
| clone | saul | a fresh clone at this addendum's merge commit M⁗, into `$R/deploy-a2`; empty porcelain; the tests in both environments | `$R/deploy-a2`, `$R/logs/clone-a2.log` |
| V1 (full) | `x_v1.sh`, `MODE=full`, `-t 01:45:00`, `BOUND` = M⁗ | `$R/deploy-a2` | `$R/v1-a2/`, its log |
| K | login node, as bound | `$R/deploy-a2` | as bound |

- **Where V1 runs.** `x_v1.sh` changes its `cd` from `$R/deploy` to `$R/deploy-a2`. That is its only change.
- **What stays as the record:**
  - `$R/v0-a1` and `$R/boot`, which K reads, are not rerun;
  - `$R/deploy` and `$R/deploy-a1` are not touched.
- **Stops.** Any stop is final, unless a new addendum is bound.
- **Cost.** X has used 3.064 of its 5.0 node-h: the probe 0.0706, the failed V1 0.0706 and BOOT 2.923. The probe
  projected 1,068 s for 175 universes. The full V1's cap is unchanged at 1.75 node-h. K and the dry runs cost 0 node-h.

## 8. Deviations disclosed with this addendum

- **The diagnosis probes ran outside the bound steps,** on login37 (omnifold_py310, O_NOATIME). They print magnitudes
  only, and wrote only `/dev/shm`, deleted after:
  - `a2/x_v1_hits_probe.py`: the lookup histogram;
  - `a2/x_k1_diag.py` and `x_k1_diag2.py`: the NormDISCC blocks' magnitudes;
  - `a2/x_k1_floor.py`: the margin of the scale floor I first proposed, which the director did not take.
- **The four K dry runs** are listed in §4. The two that stopped wrote no record. The first V1 dry run's code is at
  `a6736d33`; the V1 code is unchanged since.

## 9. The code (blob digests at this branch's head, recorded in the PR and the addendum binding)

| path | what |
|---|---|
| `nd-unfolding/fd_xcov.py` | `same_block`'s zero rule; `null_ratio` and `k1_band`; the CLI's `--dry` and `--own-only` |
| `nd-unfolding/fd_xcov_steps.py` | `weight_files`, `npy_shape` and `multi_match_classes`; `V1_DIR`; `v1_dry`; `k_own_only` and `k_own_tail`; K1 through `k1_band` |
| `nd-unfolding/tests/test_fd_xcov.py` | adds `V1Lookup`, the zero-block test and the null-rule test |
| `nd-unfolding/tests/fixtures/xcov_v1_lookup/` | the digest maps and `PROVENANCE.tsv` |
| `fd/xcov/receipts/x_v1.sh` | `cd "$R/deploy-a2"` |
| `fd/xcov/receipts/x_a2_null_mutants.tsv`, `a2/` | the mutants; the dry runs' outputs; the probes and their outputs |

`fd/xcov/INPUTS.sha256` is unchanged.

**Review:** the director reviews the diff (ruling of 2026-11-02).

Nothing is submitted, deposited or tagged.
