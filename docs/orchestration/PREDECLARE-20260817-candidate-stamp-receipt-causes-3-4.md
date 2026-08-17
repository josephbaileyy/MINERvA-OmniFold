# PREDECLARE — reading the construction-contract stamps off the ADOPTION CANDIDATE arms

**Lane E, 2026-08-17, written at `00e794e` BEFORE any stamp was read.** Scope: the provenance (`P`) leg
of quarantine causes **3** (varying estimator seeds) and **4** (scalar jitter subtraction).

**This adopts nothing.** `docs/analysis-note/` is untouched, `values.tex` is untouched, no covariance is
rebuilt, no ROOT is modified, and no value here becomes quotable. The only writes are one JSON receipt,
one copied job log, and documentation.

---

## 1. Why this measurement is not already done — the gap, stated so it can be contradicted

`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` §3 grades the `P` leg **MET** for causes 2, 3 and 4
with the citation *"read back **from the adopted product** (job `56695424`)"*. Measured at `00e794e`:

```
docs/orchestration/state/ben106-stamp-verify-complete-56695424.json
  .artifact.path        = nd-unfolding/uq_5d/readopt_20260811_footing/STAMPTEST2_bkgaware_meancentered.root
  .artifact.size_bytes  = 892170857
  .test_product_only    = true      (in the -active- receipt)
  .scope.test_product_adopted = false
  .adopts_nothing       = true      (in the -active- receipt)
```

**So the file behind the words "the adopted product" is `STAMPTEST2`, whose own receipt says it adopts
nothing.** It is also mean-centered only — no CV-centered test product was ever built.

The arms actually named as the adoption candidate are different files, from a different job:

```
nd-unfolding/uq_5d/readopt_20260811_footing/STAMPED_HASH_RECEIPT.slurm-56720356.json
  A1_stamped_meancentered  stamped_bkgaware_meancentered_20260812.root  892170881 B  4f168e83…
  A2_stamped_cvcentered    stamped_bkgaware_cvcentered_20260812.root    892232198 B  dbcd5359…
  verdict = "HASHES_COMPLETE_READ_STDOUT_FOR_ARM_VALUES"
```

`892170881 ≠ 892170857`: A1 and `STAMPTEST2` are **different files**. And that receipt carries **hashes
only** — no stamp values — deferring them to a stdout on purgeable scratch that no committed artifact
contains. `git ls-files | grep 56720356` returns the receipt and nothing else.

**Consequence, and it is why this predeclaration exists:** CRITERIA's own cause-2 box refuses exactly this
substitution — *"Declaring on A1/A2 while citing stamps verified on a different file is the
invented-after-the-fact closure this document exists to prevent"* — and cause 2 was therefore re-cited to
the regenerated arms. **Causes 3 and 4 were not.** Their `P` rows still point at `56695424`. This
measurement re-cites them to the artifact they are supposed to be about, from a **committed** receipt
rather than from a scratch log.

## 2. What will be read

One read-only ROOT open per file; no recomputation. Five files, three roles:

| role | file | why |
|---|---|---|
| **subject** | `stamped_bkgaware_meancentered_20260812.root` (A1) | the candidate the P leg must be about |
| **subject** | `stamped_bkgaware_cvcentered_20260812.root` (A2) | never stamp-verified at all, not even by a test product |
| **control, positive** | `STAMPTEST2_bkgaware_meancentered.root` | the file CRITERIA actually cites; must reproduce `…complete-56695424.json` |
| **control, negative** | `uq_universe_5d_covariance_combined_bkgaware_uthrow.root` (X, feeds `\gbdtFiveAdoptTrace`) | must come back **ABSENT** |
| **control, negative** | `…_bkgaware_uthrow_cvcentered.root` (X, feeds `\gbdtFiveCVTrace`) | must come back **ABSENT** |

**The negative controls are not decoration.** A reader that reports "present" on everything proves
nothing; the two July products are the form in which the defect is still live, so the instrument must be
shown failing on them in the same run that it passes on the candidate. Absence is reported as
`{"present": false}`, never omitted.

## 3. Predeclared values — every one from a committed source, so a mismatch is a refutation

| key | predicted | committed source of the prediction |
|---|---|---|
| `n_throws_checked` | `1` | `adopt_unified_5d.py:198-204` writes it unconditionally |
| `upstream_n_throws` | `160` | `CRITERIA` §4.7 table; `…complete-56695424.json` |
| `joint_mean_shift_norm_checked` | `1` | as above |
| `upstream_joint_mean_shift_norm` | `1.878696733368378e-38` | `CRITERIA` §4.7; `VALIDATION_LEDGER` J28 rows |
| `fixed_seed_null_checked` / `fixed_seed_null_norm_checked` | `1` | `unified_throw_cov.py:487`, `adopt_unified_5d.py:202` |
| `upstream_fixed_seed_null_norm` | `5.8223488501140625e-50` | `CRITERIA` §4.7 (J28-corrected throw ROOT) |
| `centering_convention` | A1 `mean-centered`, A2 `cv-centered` | `adopt_unified_5d.py:207-208`; launcher passes `--cv-centered` only for A2 |
| `uthrow_source` | `unified_throw_cov_5d_fluxfix_20260806_full160.root` | `sbatch_adopt_stamped_footing.sh:32` |
| `combined_source` | `uq_universe_5d_covariance_combined_bkgaware.root` | `sbatch_adopt_stamped_footing.sh:33` |
| `sqrt_tr_old` | `4.357790406860002e-38` | `receipt_construction_contract_5d.json` |
| `sqrt_tr_new` | A1 `5.2696e-38`, A2 `5.6743e-38` | `STAMPED_HASH_RECEIPT…json` `.predicted` |
| `sha256` | A1 `4f168e83…`, A2 `dbcd5359…` | `STAMPED_HASH_RECEIPT…json` `.files` |
| **X, both arms** | every one of the nine keys **ABSENT** | `receipt_construction_contract_5d.json` `.adopted_roots.*.parameters` |

**The tolerance, with its derivation, because cause 4's criterion is *"key present, and ≤ tol, with tol and
its source both stated"*.** `unified_throw_cov.py:445`:

    tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)

`base` is the reported 5D cross-section over 10,694 bins at ~`1e-38` magnitude, so `‖base‖ ≈ 1e-36 ≪ 1`,
the `max(·, 1.0)` binds, and **`tol = 1e-12` exactly** — an absolute floor, not a relative tolerance.
Predicted margin: `5.8223e-50 / 1e-12 = 5.8e-38`, i.e. ~37 orders below tolerance.

## 4. Branch set — declared now, so the verdict cannot be chosen after the read

* **S1 — CONFIRM.** A1 and A2 both carry all six required stamps; every value equals §3 digit for digit;
  both sha256 match the committed hash receipt; **and both negative controls come back ABSENT.**
  → The `P` leg of causes 3 and 4 is **MET for the candidate, from a committed artifact**, and no longer
  depends on an uncommitted scratch stdout or on a file that adopts nothing.
  **It does not discharge either cause** — see §5.
* **S2 — REFUTE.** Any required stamp absent, or any value differing, on A1 or A2.
  → CRITERIA §3's `P` rows and the 2026-08-12 cause-2 discharge rest on a claim the artifact does not
  support. **Routed to Joseph, not adjudicated here.**
* **S3 — BINDING BROKEN.** Stamps fine but sha256 ≠ the committed receipt.
  → The file on disk is not the artifact that was hashed; provenance is broken independently of stamping.
* **S4 — EVIDENCE GONE.** A file is absent or unreadable (purgeable scratch).
  → `P` unsatisfiable without a rebuild. (`ls` at 01:5x UTC showed all five present; an `ls` is not a read,
  so this branch stays live until the read completes.)
* **S5 — NEGATIVE CONTROL FAILS.** X comes back *carrying* stamps.
  → Either the July products were rebuilt since 2026-07-14 or the reader cannot distinguish stamped from
  unstamped. **In this branch S1 is void even if the subjects pass**, because the instrument is unproven.

## 5. What this CANNOT do, stated in advance

`P` is one of four legs (`C`/`P`/`M`/`T`, `CRITERIA` §0); all four are required.

* **Cause 4 stays OPEN under S1 regardless**, on `M`. `CRITERIA` §2 records that leg as UNRESOLVED and
  gives a reason for expecting it to stay so — *"the counterfactual is not defined by any surviving
  specification"* — with a **bound** (<0.1% of the sqrt-trace) explicitly labelled *"a bound is not the M
  leg."* No stamp read changes that. Whether the bound may stand in for `M` is a judgement.
* **Cause 3's `M` is contradicted between two sections of one document** and this read does not resolve it:
  §2 flags M(ii) *"UNRESOLVED rather than assumed"*, while §3's table grades `M` **MET** citing only the
  null. These are M(i) and M(ii) — different questions, per §2's own wording. Naming it; not settling it.
* **Nothing here is about X.** Under §0's (cause × artifact) rule the candidate and X are different
  subjects, and X predates stamping: it is replaced, not repaired.

---

**Falsifiability of this document itself:** every predicted value in §3 is committed, so if the read
returns different numbers this predeclaration is what proves it, and the receipt will ship the operands
(`sqrt_tr_old`, `sqrt_tr_new`, sizes, sha256) beside the verdict so the reported numbers can contradict
each other — `CONVENTION-receipt-ingredients.md`, BEN-077.
