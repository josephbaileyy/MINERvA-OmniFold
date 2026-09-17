# NAVIGATION 2026-09-17 — where the Z assembly/spectrum pilot's outcome lives

**CLASS: navigation only.** This record carries **no measurement, no verdict and no
authorization**. It exists because the pilot's outcome and its reconciliation live on a lane branch,
and `main` had no pointer to them. Authorized by Joseph 2026-09-17 as a documentation-only route:
**explicitly not a campaign code merge and not an analysis-note change.**

## NOT CITABLE FOR

Any scientific grade, acceptance boundary, adoption, projection or publication use. The pilot's
`scientific_acceptance` is **NON-PASSING**, `adoptable` is **false**, `outcome.assessable` is
**false** on reject condition `4c`, and `B`, `S` (in full) and `ε` are **all open**. **Successful
construction authorizes nothing.** Gate 2 remains **FAIL**.

## What happened, in one paragraph

The Z assembly/spectrum pilot ran once and completed. Job **`58454524`**, `nid004093`,
`ExitCode 2:0` — **2 is the CLI's completion code for "construction ran, science NON-PASSING"**, so
`sacct`'s `FAILED` label is not the verdict; judge it by the artifact and receipt contract.
`ElapsedRaw` 1037 s. Two 5D covariance objects and a null slab now exist, with matching receipts.
The single authorization is **consumed**; no replacement submission is authorized.

## Route, at full commit identity

| what | where |
|---|---|
| **branch** | `lane/z-assembly-pilot-20260914`, pushed to `origin` |
| **outcome record** (RUN_LOG § 2026-09-17, STATUS, reconciliation §10) | **`1b2873a8e9b3c78568725494799a3df6234a39d5`** |
| **corrected recommendation** (§12 **as corrected by §13**; §11 is withdrawn) | **`affc9e03119230ece17f977325d8a1ba00d68827`** on the same branch — **read §13 first**; §12.7's decision table is superseded by §13.7, and §11 is not citable |
| **independent assessment of §12** | **`ed18a231de4c3b6b016e268be54257579b6c7739`** on `lane/z-criteria-independent-assessment-20260910` — `ASSESSMENT-20260917-decision-support-section-12.md`. **It closes nothing:** full `S` OPEN, §7 item 4 UNASSESSED, `θ` RECOMMENDED NOT ADOPTED, A1 OPEN, Gate 2 FAIL |
| **accounting + the detailed result in its message** | **`0202591b15092486b6db167478cf72290fcc7ed9`** |
| **assembling revision** (deployed, immutable) | **`fb9ec3560fd6d62295dffc81b5694c9e26667d5b`** |
| **producer revision** (the precursor's) | **`e09513d842ad3acc1964c1af740696f02eaed7d9`** |
| **B's estimator + repeat-design predeclaration** | **`78a8c2ee42c71db1e300e4cfe3735554101bf8ce`** on `lane/z-criteria-recommendation-20260910` |
| **preserved evidence on the cluster** | `/pscratch/sd/j/josephrb/zpilot-20260916/outcome-58454524/` |
| **products, left in place** | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/` |

Product digests, re-measured 2026-09-17 and matching their receipts:

```
3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5  z-cv.npz    890,500,272 B
61b7a4939bd40459452e232d4a5cec3c0b19ad7a21715452f7bb3bc9e0c72dd2  z-mean.npz  890,383,062 B
cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e  z-null.npz      190,817 B
```

## ⚠ CORRECTION — "`main` contains no Z content" was FALSE

A 2026-09-17 session report stated that `origin/main` "carries **zero** Z content". **That is
wrong, and it is recorded here rather than left to propagate.** It came from a three-pattern `grep`
over a single status file — a non-covering search read as a null result. Measured properly at
`66d357060c1d14fc79cab479cc1c0e19fad54783`, `main` carries **26 Z-named files**:

- **the scientific contract:** `docs/orchestration/SPEC-20260906-complete-scalar5d-successor-Z.md`
- **Joseph's own ruling:** `docs/orchestration/DECISION-20260906-joseph-authorizes-z-specification-only.md`
- plus `PROMPTS-20260906-z-specification-session.md`,
  `PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md`,
  `RECORD-20260908-z-operand-schema-assignment-block-and-pass.md`,
  `state/probe-z-projected-stability-20260910.py`
- **four planning/contract docs:** `nd-unfolding/Z_BUILD.md`, `Z_BUILD_PACKET.md`,
  **`Z_CONSTRUCTION_PLAN.md`** (§4.4a lives here), `Z_DECISION_PACKET.md`
- **ten modules:** `z_assembly.py`, `z_build.py`, `z_build_path.py`, `z_contract.py`,
  `z_precursor.py`, `z_precursor_admission.py`, `z_receipt.py`, `z_reproducibility.py`,
  `z_statistics.py`, `z_validator.py`
- **six test files** under `nd-unfolding/tests/test_z_*.py`

**What `main` genuinely lacks** is narrower and is the whole reason this record exists:

1. the **pilot-specific** code — `z_pilot.py`, `z_null_bridge.py`, `z_pilot_manifest_cli.py`,
   `sbatch_z_pilot_5d.sh`, `submit_z_pilot_a5.sh`;
2. the two 2026-09-16 records — `DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md` and
   `PROPOSAL-20260916-B-and-S-bounded-determinism-control.md`;
3. the **post-freeze RUN_LOG chronology** — `main`'s `ND_OMNIFOLD_RUN_LOG.md` is **16 lines** and
   carries no `## Post-freeze chronology`; the lane's is 364.

So the accurate statement is: **the Z specification, contract, planning documents, build modules and
tests are on `main`; the pilot's execution code and its chronology are not.** Landing those is a
separate merge decision (54 files, ~12.5k insertions, including production launchers and
analysis-note sources) and **is not authorized by this record.**

## Open, and not changed by any of the above

`B`, `S` — **in full**, not only the F7 channel — and `ε` are open. `ε = 1e-9` is **PROPOSED and
UNGRADED**, its falsifier **UNEVALUATED**. All four `withheld_boundaries` (`null_epsilon`,
`cause3_agg`, `cause3_med`, `cause3_corr`) remain `WITHHELD` with `value: null`. The completed
precursor and the completed pilot are **closed** and are not to be reopened.
