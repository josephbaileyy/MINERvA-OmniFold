# PREDECLARATION — the construction-contract receipt (BEN-101's provenance leg)

**Written 2026-08-11 BEFORE the read, and before knowing whether the artifacts still exist.**
Purpose: satisfy — or fail to satisfy, visibly — the **Provenance** leg of quarantine causes 1, 2, 3
and 4 for the 5D GBDT covariance, per
[`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`](CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md).

**Why a receipt and not a re-run.** The stamps that prove the construction contract are already written —
`unified_throw_cov.py:479-484` writes `fixed_seed_null_norm`, `joint_mean_shift_norm`, `n_throws` and
`hJointMeanShift`; `:255,286,303` stamp `flux_normalized`; `do_throws`/`do_blockunits` stamp `seed` and
`do_combine` rejects mixed-seed slabs at `:330-331,370-371`. But `*.root` and `*.npz` are `.gitignore`d,
and the committed evidence is two summary text files carrying **magnitudes only** — no seed, no null norm,
no centering convention, no endpoint inventory. So the claim *"built under the corrected contract"* is
currently **unfalsifiable from the repository**. This reads the existing stamps and commits them.

**This adopts nothing and recomputes nothing.** It opens files read-only and writes one JSON.

## Artifacts to read

| role | path (relative to `$MNV_REPO/nd-unfolding`) |
|---|---|
| pre-J28 throw ROOT — feeds `5.81e-38` / `6.24e-38` | `uq_5d/unified_throw_cov_5d.root` |
| J28-corrected throw ROOT — feeds `5.2600e-38` / `5.6609e-38` | `uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` |
| bkgaware block sum (the `13.36` source) | `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` |
| bkgaware adopted, both conventions | `…_bkgaware_uthrow.root`, `…_bkgaware_uthrow_cvcentered.root` |
| J28 adopted, both conventions | `uq_5d/rescaled_20260806/adopted_{meancentered,cvcentered}_20260806_full160.root` |
| throw slabs — seed + flux stamps | `uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz` |
| block slabs — seed + flux stamps | `uq_5d/block_slabs_5d_sb/block5d_*.npz` |

## PREDECLARED BRANCH SET — four outcomes, and UNRESOLVED is a real one

**B1 — STAMPS PRESENT AND CONSISTENT.** Every throw ROOT carries `fixed_seed_null_norm` **as a present
key** with value ≤ tol; `joint_mean_shift_norm` and `n_throws` present; every slab carries one and the
same `seed`; the throw inventory is exactly the expected range. → The **Provenance** leg becomes MET for
causes 3 and 4, and for cause 2 to the extent that the mean shift is stored separately. Cause 1 still needs
the ± endpoint inventory, which is a separate read.

**B2 — SOME STAMPS ABSENT.** A product is missing `fixed_seed_null_norm` because `--null` was not passed —
`unified_throw_cov.py:482-483` writes the key *only if the flag was given*. → Provenance **FAILS** for
cause 4 on that product, and the null-as-absent shape (PB2) is realized in cause 4's own evidence rather
than hypothesised. **A criterion phrased as "the null norm is not large" would pass here vacuously**, which
is why the criterion is written as *key present AND ≤ tol*.

**B3 — STAMPS PRESENT BUT INCONSISTENT.** Mixed seeds across slabs, `n_throws` ≠ the expected inventory, or
a null norm above tol. → A substantive construction defect, not a bookkeeping gap; escalate rather than
file a receipt.

**B4 — UNRESOLVED: the artifacts are not readable.** Scratch is **purgeable** and these products date from
2026-07-13 to 2026-08-06; nine slabs of this very ensemble have already been lost to purge once
(`VALIDATION_LEDGER.md:257`). The ROOT/TF environment split may also block a single interpreter from
reading both `.root` and `.npz`. → **UNRESOLVED is the verdict, and it must not be re-read as B1 or B2.**
It is not "the stamps are fine, we just could not check" and it is not "the stamps are missing"; it is
*"the evidence has been destroyed by retention policy"*, which is a **worse** finding than B2 because it is
not repairable by a flag — it would mean the corrected-contract claim can never be checked for the products
the note currently quotes, only for products rebuilt from scratch.

## Committed on any outcome

`nd-unfolding/uq_5d/receipt_construction_contract_5d.json`, carrying **per artifact**: path, existence,
size, mtime, sha256 where affordable, every construction `TParameter` found **and every one looked for and
not found** (absence recorded explicitly, never omitted), and the per-slab seed/stamp census. Plus the
verdict against the branch set above. Per `CONVENTION-receipt-ingredients.md`: the operands ship with the
verdict, so the numbers can contradict each other.

**Recording absence explicitly is the whole design.** A receipt that lists only the keys it found cannot
distinguish *"the key is not there"* from *"nobody looked"* — which is the defect this receipt exists to
close, one level up.
