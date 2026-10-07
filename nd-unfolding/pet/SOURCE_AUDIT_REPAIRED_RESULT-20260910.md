# Repaired PET source audit: terminal result

**COMPLETE. `mapping=PASS`; `semantic=DISCREPANCY`; `release=RELEASE_UNVERIFIED`; all four
object-family verdicts `UNRESOLVED`.** Exit zero is mechanical mapping acceptance only. The
semantic, release and family verdicts are separate and none of them passes.

This is the single attempt authorized in
[SOURCE_AUDIT_REPAIRED_AUTHORIZATION-20260910.md](SOURCE_AUDIT_REPAIRED_AUTHORIZATION-20260910.md)
under [the repaired packet](SOURCE_AUDIT_REPAIRED_PACKET-20260910.md). It is diagnostic,
fixed-source telemetry on a deterministic, unselected convenience sample. It is not a physics
measurement.

## Execution binding

| Item | Value |
|---|---|
| Code commit (clean detached standalone clone) | `ca34a03a9f04ec16b56064c5bc6faaf85b9ebf17` |
| `SOURCE_AUDIT_BINDINGS.json` SHA-256 | `fea412de2f1f4702873e6f62ae98ef6bdfe8e0da65b5ef5066c4cd1cdd4057c3` |
| Authorization JSON SHA-256 | `4e1b9b8520a332780e7937d052ce602bd3f25f51549da0813e9c0486e6952704` |
| Runtime | Python 3.11.14, ROOT 6.28/12, NumPy 1.26.4, SciPy 1.16.3, TensorFlow 2.16.2, Keras 3.15.1, `TF_ENABLE_ONEDNN_OPTS=1` |
| Output root | `$SCRATCH/pet-v2-source-audit-repaired-20260910` (new; `audit` child absent before launch) |
| Allocation | `58186616`, `shared_interactive`, 2 CPUs requested / 6 reserved, 8 GiB, 15 min, node `nid004190` |

Checks made before source access:

- `generate_live_state.py --check-freshness` on the Perlmutter canonical main (`32e403b8`)
  returned `FRESH`.
- `squeue` showed no jobs for the user.
- The output root did not exist.
- `--check-preparation` returned `PASS` and imported no ROOT.
- The bindings digest and both manifest-line-1 digests matched.
- Both source paths were present.
- The runtime's module versions matched the pins.
- The execution checkout had no tracked, untracked or ignored files beyond the commit.

The allocation script refused grants above six CPUs or fifteen minutes; neither refusal fired.
The launcher ran through `mnv_guarded_run.py` with the packet's exact command.

## Terminal state

| Measure | Value |
|---|---|
| Allocation `58186616` | `COMPLETED`, exit `0:0`, elapsed 00:07:55, 6 reserved CPUs |
| Step `58186616.0` | `COMPLETED`, exit `0:0`, 2 CPUs, TotalCPU 05:10.189, MaxRSS 2,448,868 KiB |
| Audit wall time | 387.25 s |
| Peak observed process threads / RSS | 4 / 1,219,506,176 bytes |
| Output bytes before accounting | 283,206,787 (ceiling 1 GiB) |
| Exceptions | none; `stdout.log` and `stderr.log` are empty |
| Entry lists | requested, attempted, captured, mapped and completed are each exactly `0..4095` for both data and MC |
| Source UUIDs | data `bcd43694-ef17-11f0-9717-17a6e183beef`, MC `c0347da6-2a99-11ef-9717-31a7e183beef`, matching the bindings |
| Import guard | outcome `child-systemexit:0`; 3,860 modules checked, zero origins outside the expected root, one checkout root |
| `accounting.json` SHA-256 | `3bb911e6be1e83209c94a0d47ed6f79ddaddd85d84998444913cfcd591a49543` |
| `receipt.json` SHA-256 | `5e8d545b6a8b45ed1872852417c13518472b0fbb07832faf78c39406e153b3da` |
| Bounded-payload SHA-256 (captured entries only, not a file checksum) | `17dc0a014fe7f53d5711f5ceeed7bd3ab0b610f6f30c6035fb544dbca441421d` |

`scontrol` showed `NumCPUs=6` and `TimeLimit=00:15:00`, so the allocation fitted both ceilings.
It was relinquished at completion.

The observed data `metadata.json` digest,
`f3d43367a7382c74259ca54c803cf52b3a1360d6518887750814d6f67f9dbf53`, equals the one preserved from
the interrupted `58832843` attempt.

This run exercised `RootAuditReader` and the source launcher's final `accounting.json` writer.
The synthetic preflight did not reach either.

## Verdicts

**Mapping — PASS.** All six mandatory checks pass: `identity_metadata`,
`independent_typed_values_masks`, `alignment_membership`, `round_trip`,
`finite_numpy_keras_agreement` and `C0_C1_64_columns`. All 512 16-row chunks completed.

**Semantic — DISCREPANCY.** Of the eight correspondence checks, every one passes in both
anchor intervals `[0,16)`, but `prong_time` fails in both extensions. That check requires an
eligible prong's `prong_part_pos[token][3]` to lie in `[0, 10000]`. Five finite values exceed the
upper bound:

| Role | Entry | Token | Observed time |
|---|---|---|---|
| data | 2121 | 0 | 13181.452089379482 |
| data | 2704 | 0 | 15159.489724392435 |
| data | 3418 | 0 | 13674.652787144687 |
| data | 3867 | 0 | 10052.797142089019 |
| mc | 3654 | 1 | 15980.891188914475 |

Denominators: data extension 4 of 6,050 eligible prongs; MC extension 1 of 7,140. Every
other check reports zero discrepancies, including sentinel score/mass, PID support, charge
support, photon direction and blob cluster count. `photon_direction` has large `missing`
counts because absent photon slots are ineligible.

Per the runbook, the discrepancy is retained as a diagnostic. It is not a cut, a misordering
determination or an explanation. The receipt's qualification reads: *"Unexplained discrepancies
block PASS; release applicability and producer ordering remain unresolved."*

**Release — RELEASE_UNVERIFIED.** No producer attestation, PID enumeration, filler or
reconstruction configuration was supplied or inferred.

**Object families.** `photons`, `blobs`, `prong_hypotheses` and `shared_objects_primary_lepton`
are all `UNRESOLVED`.

**Also recorded:** the receipt lists 955 duplicate event-key groups:

| Role | Groups | Rows | Largest group |
|---|---|---|---|
| data | 950 | 2,185 | 6 rows |
| MC | 5 | 10 | — |

These are recorded observations only, with no interpretation.

## Preservation and transfer

On Perlmutter, every one of the 16,899 receipt-bound artifacts was rehashed. Digests and byte
counts all matched, and no unbound file was present. The receipt digest matched
`accounting.json`, as did the digests of the interruption marker, progress log and both logs.

The following were transferred and matched the remote SHA-256 list:

- the authorization JSON, launch scripts, allocation record and terminal `sacct` record;
- the guard inventory, receipt, accounting and telemetry summary;
- the progress log, interruption marker and both logs;
- both source `metadata.json` files;
- the raw and observation rows for the five discrepant entries.

They are preserved under [`source_audit_runs/20260910-repaired/`](source_audit_runs/20260910-repaired/)
with `preservation-manifest.json` and `verification.json`. Large JSON is gzip-compressed, and
both compressed and uncompressed digests are recorded.

At audit completion, the remaining raw, observation and typed shards (about 279 MB)
were only at the remote scratch output root. On 2026-09-11 the complete output root
was copied to CFS and every copied file read back and verified; see
[the preservation record](SOURCE_AUDIT_PRESERVATION-20260911.md). The scratch original
and all audit verdicts are retained.

## Boundary

This result does not establish:

- release applicability, PID calibration or particle overlap;
- population support, coverage or production normalization;
- `pass_reco` selection;
- training readiness.

No normalization was fitted and nothing was trained. No covariance was constructed and no
central value changed. No retry was made and no subset was selected. OI-126 remains ruled and
PET remains diagnostic. The receipt's `prohibitions_applied` keys are unchanged:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```
