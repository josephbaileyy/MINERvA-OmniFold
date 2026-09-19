# CHECKLIST 2026-09-19 — re-running against a new digest every check `z-cv.npz` passed

**CITABLE FOR:** the enumeration below and where each check is implemented.
**NOT CITABLE FOR:** any result. Written **before** the campaign returned, so the list cannot be
selected after seeing which checks a new product happens to pass.

Joseph's `(A)` requires *"every check `z-cv.npz` passed re-run against its digest."* This is that
list, derived from the records rather than recalled, with **where each one already lives** — a
check retyped here would be a second implementation that stops agreeing with the first.

## A. Automatic — `z_build` runs these on every build, or there is no product

| # | check | implementation | evidence it ran |
|---|---|---|---|
| A1 | `G1` closure identity | `z_assembly.gate_closure_identity` | `receipt.inflation.G1_closure_identity` |
| A2 | `G2` `g` domain | `gate_g_domain` | `…G2_g_domain` |
| A3 | `G3` `g` reconstruction | `gate_g_reconstruction` | `…G3_g_reconstruction` |
| A4 | **`G3R` raw-operand reconstruction, BOTH variants** | `gate_raw_operand_reconstruction` | `…G3R_raw_operand_reconstruction.per_variant`, with a measured `max_rel_diff` inside a stated `rtol` |
| A5 | `G4` symmetry and PSD on the inflated object | `gate_symmetry_psd` | `…G4_symmetry_psd` |
| A6 | `G5` band partition, `13 + 27 + 5 = 45` | `contract.check_band_partition` | `…G5_band_partition`, `inflation.partition` |
| A7 | blocksum symmetry/PSD | `gate_symmetry_psd` | `closure.blocksum_symmetry_psd` |
| A8 | `active_total == sum of the five` | `p4_lib.check_component_sum` | `closure.active_total_eq_sum5` |
| A9 | pair gates across the two variants | `run_pair_gates` | in both receipts |
| A10 | **product readback** — metadata identical, arrays identical, gates re-run on the bytes read back | `z_build._verify_products` | the build exits non-zero otherwise |
| A11 | null operands persisted, read back unchanged, ratio unchanged | `z_build` + `z_receipt.load_null_operands` | `null_block.persisted` |
| A12 | the declared residual band set (27 names) | `contract.check_declared_residual` | gated on `input_kind == "real"` |

**A1–A12 need no separate run.** A product that exists has passed them; the receipt carries each
gate's **measured output**, not a boolean, and `z_grade` re-checks `A4` through
`z_receipt.validate_reconstruction_ran`.

## B. Re-run explicitly against the new digest

| # | check | how | what would make it fail |
|---|---|---|---|
| B1 | **digest verification** | `sha256sum` the product; compare with `receipt.z.sha256` and with `metadata.manifest_sha256` ↔ `receipt.notes.manifest.sha256` | bytes that are not the ones the receipt describes |
| B2 | **`SRC_COV` identified by MEASUREMENT, not by filename** | `project_cov_nd.py --expect-variant cv` accepts it; `--expect-variant mean` refuses it | a product whose declared variant is not the one the caller asserts |
| B3 | **the guard-set control, all legs** | `run_m1_guardset_control.sh` with `MNV_P=<new product dir>` — it is already parameterised by the directory holding `z-cv.npz` / `z-mean.npz` | any of A1/A2/A3 (launcher gate), B1/B2/B3/B5 (refusals), B4 (positive control) or Q2 changing verdict |
| B4 | **cross-member validity, all nine fields re-measured from bytes** | `z_grade.cross_member_validity` | any field the products do not support |
| B5 | **the null, recomputed and BOUND to the graded member** | `z_grade.measure_null` — sha256 of the slab, reproduction of the receipt's `r_null`, mask equality | a null from another run |
| B6 | **`s_proj`'s baseline resolvability** | `z_statistics._require_baseline_is_resolvable`, inside `s_proj` | a functional positive only by round-off |

## C. Documentary — at the criterion level, not per digest

`C1`–`C7` are cause **dispositions** (`AUTHORIZATION-20260918` ruling 6; C7 closed under
`DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`). They attach to the criteria and the
production route, not to one product's bytes, so a new digest does not re-open them — **except**
that any new product must be built from the same declared band partition and footing, which is
`A6`/`A12` above.

⚠ **`(cause 3, Z)`'s `M(i)` stays `UNRESOLVED` on reject condition `4c` for every candidate.** That
is a permanent property of the criterion, not of `z-cv.npz`, and a PASS on `M(ii)` does not regrade
it. Any adoption record for a new digest must say so in the same place as the adoption, exactly as
the `z-cv.npz` draft does.

## D. What is NOT on this list, and why

- **The `§6.4` null exception.** It covers `3d7465f6…` **and nothing else** by construction. A new
  candidate has no exception available and must clear `ε` on its own measured `r_null`.
- **`P0` / `P2`.** `P0` returned the like-for-like branch and `P2` was not authorized; neither is a
  per-digest check.
- **The `kappa` arm of the `s_proj` degeneracy test.** Unevaluable while `kappa` is undeclared;
  the Rayleigh quotients are recorded instead so it can be applied retrospectively.

**Co-Authored-By: Claude Opus 5 (1M context)**
