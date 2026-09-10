# N-D OmniFold run log

The complete pre-compaction chronology is frozen at
`evidence/prepublication-2026-08-20-0b329e8a` under this exact path:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:nd-unfolding/ND_OMNIFOLD_RUN_LOG.md
```

Read `ND_OMNIFOLD_STATUS.md` for current scalar/PET/FPS state,
`PET_UQ_REMEDIATION_STATUS.md` for the live PET DAG, and `VALIDATION_LEDGER.md` for verified
numbers. The tag is historical evidence, not scientific adoption.

## Post-freeze chronology

Append only committed post-2026-08-20 events here; keep current state in the owning STATUS file.

### 2026-09-10 — Prong correspondence and typed-descriptor continuation

Recorded Carlos Pernas's reconstruction-side explanation in
[PRONG_BRANCH_SEMANTICS.md](pet/PRONG_BRANCH_SEMANTICS.md), preserving the
difference between stated definitions and tentative expected code support,
hypothesis selection and release applicability. The record explains the PID
and charge conflict, missing-value handling, score/mass interpretation,
primary-lepton role, dedicated particle branches and P7/P8 provenance.

[TYPED_DESCRIPTOR_STATUS.md](pet/TYPED_DESCRIPTOR_STATUS.md) routes the next
proposed task: repair the prong contract and validate it locally with synthetic
fixtures before source validation or training. The older fixed-sample packet
gains a forward pointer; its measurements and scope remain unchanged. The
adapter and semantic-evidence branches were measured as already integrated at
base `d147880f`, so the documentation continues on `pet-prong-semantics` from
that base.

Documentation only: no source access, probe, training, covariance construction,
schema implementation or scientific result. No validation-ledger row is added.
The scalar publication task and the `OI-126` PET disposition are unchanged.
