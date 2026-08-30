# Predeclaration - Gate-6 GAP 3 non-finite energy diagnostic

**Contract ID:** `PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830`

**Status:** authorized for one bounded diagnostic. Preparation, push, and all preflights must pass
before submission. If the diagnostic cannot be completed without batch compute, exactly one new
CPU-only Slurm job is authorized. Failure is terminal and authorizes no retry.

## Frozen scope and preserved result

The changed-retry GAP 3 result remains `INVALID_OR_INCOMPLETE`. This diagnostic must not replace,
reinterpret, repair, or promote any truncation percentage from that run. The preceding artifacts
are immutable at these SHA-256 values:

| artifact | SHA-256 |
|---|---|
| changed-retry predeclaration | `fc1772058469a34293ba1d8a162c1fe3b6cd3c2ade6c7bd31a65a39bda06c648` |
| changed-retry launcher | `ffadc05bd186d950b718be3f7e4e8d9e9a9563b771ea2cb3097cc6e933cd16db` |
| changed-retry launch receipt | `48a638a593eed9e3ebe9c9fc62da6c6e721816aa1bf4c49c4c2a18e229403015` |
| changed-retry terminal receipt | `42e2609ebc8c7cf4c0a9b501935b9df94a18549f5deae9e78c12b1a9cd1d09ef` |
| changed-retry compressed result | `7c8ff0dc0baa4fd03d29534a2a24558f7705d2e9cd914aa219e528071e0cbf6e` |

The diagnostic is limited to the 2,366 raw non-finite `part_reco_E` entries previously counted:
1,687 signal, 456 data, and 223 background. It may report a mismatch, but it may not broaden into
a new truncation audit or use a mismatch to change the frozen input.

## Frozen inputs and row populations

The source ROOT is
`nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`, size
`113496440965` bytes and SHA-256
`9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f`.

The stored PET input is `nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz`, size
`9897374636` bytes and SHA-256
`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`. Its producer receipt must
have SHA-256 `d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e`.

The exact populations and selections remain:

- signal tree `mc_signal_reco`: `sim_pass != 0`, finite `sim,sim_pz`, and
  `(sim,sim_pz)` in `[0,30] x [0,120]`, expected selected rows `20,573,521`. Source-to-NPZ mapping
  retains rows in ascending ROOT order when either this reco selection or the finite truth
  `(MC,MC_pz)` domain holds, expected NPZ rows `49,152,885`;
- data tree `data`: `measured_pass != 0`, finite `measured,measured_pz`, and the same domain,
  expected selected and NPZ rows `4,116,128`; and
- background tree `mc_background`: `sim_background_pass != 0`, finite
  `sim_background,sim_background_pz`, and the same domain, expected selected and NPZ rows `564,591`.

No selection, population, cluster definition, kinematic edge, or source-to-NPZ ordering rule may
change.

## Frozen diagnostic measurements

For each selected event containing at least one non-finite raw energy, the run must:

1. classify raw `NaN`, positive infinity, and negative infinity separately by population;
2. count affected events, non-finite entries, and non-finite entries per event;
3. convert the five aligned reco vectors to `float32` and reproduce exactly
   `np.argsort(-energy, kind="stable")`, the production stable sort;
4. record each non-finite entry's one-based production rank and whether it is inside or beyond
   rank 12;
5. reconstruct the production P=12 cloud, view, and time arrays, then compare them exactly, with
   equal-position NaNs accepted, to the corresponding stored NPZ row;
6. derive the NPZ row from the complete source retention order, then verify cloud, view, time,
   reco scalar, weight where present, and signal pass alignment;
7. report raw vector length, finite-positive multiplicity, capped finite-positive multiplicity,
   stored finite-positive multiplicity, and the actual PET energy-mask multiplicity;
8. run the exact hash-bound loader `build_reco_cloud`, inspect corresponding stored energy tokens,
   and verify non-finite-to-zero sanitization plus the actual `energy != 0` mask; and
9. verify the hash-bound model path, including pre-mask encoding, local-neighbor construction,
   body masking, first body attention, FiLM re-masking, and class-token attention masking.

The diagnostic must explicitly test the requested `energy > 0` proposition. The predeclared source
reading is that the production loader/model uses `energy != 0`, not `energy > 0`; the run must fail
closed if the bound sources disagree. It must distinguish removal from masking and must report any
model influence path rather than equating a false energy mask with absence from all computation.

## Frozen kinematic reporting

The affected-event and entry counts, classifications, inside/beyond-rank counts, and stored-token
counts must be accumulated in these unchanged bins:

- reco `pT`: `[0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30]` GeV;
- reco `p_parallel`: `[0, 0.75, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60, 120]` GeV;
- reco `Eavail`: `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100]` GeV;
- reco `q3`: `[0, 0.2, 0.4, 0.6, 0.8, 1.2, 2, 100]` GeV; and
- the Cartesian grid of the frozen reco `pT` and `p_parallel` edges.

The axis branches remain `sim,sim_pz,sim_eavail,sim_q3` for signal;
`measured,measured_pz,measured_eavail,measured_q3` for data; and
`sim_background,sim_background_pz,sim_background_eavail,sim_background_q3` for background.

## Denominator decision rule

If every provenance, census, alignment, stable-sort, loader, and source-path check passes, recommend
`FINITE_POSITIVE_PET_ELIGIBLE_CLUSTERS` as the scientifically correct denominator for a possible
future token-cap study. All raw entries remains a source-record census and includes values for which
energy arithmetic is undefined. This recommendation alone must not calculate a replacement
truncation fraction or authorize a token-cap study. An incomplete diagnostic returns no denominator
recommendation.

## Execution, preflight, and terminal contract

- authorization token: `PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830-ONE-SCAN`;
- new output namespace; clean pushed immutable checkout; no output collision;
- at most one job, one task, 18 CPUs, 18 ROOT threads, 32 GiB, two hours, CPU constraint, no GPU;
- allocation ceiling `18 x 2 = 36` CPU-hours;
- no array, requeue, automatic retry, unchanged retry, changed retry, or further retry;
- preflight full ROOT and NPZ SHA-256 values, producer receipt, prior immutable artifacts, new source
  hashes, ROOT import/JIT, ROOT schema, NPZ headers, pure stable-sort semantics, and positive/negative
  launcher resource guards; and
- runtime repeats every applicable check and atomically writes one result JSON.

Terminal verification must directly inspect Slurm accounting, result and log digests, input digests,
selected-row censuses, non-finite class domains, source-to-NPZ alignment, loader output finiteness,
and the result JSON. Any failure is terminal and authorizes no further job.

All diagnostic numbers remain nonquotable. No result can authorize filtering or input repair, a
representation or token-cap change, retraining, a central-value move, covariance construction,
Gate-6 member selection, Leg 2, further compute, a publication claim, or a publication edit.
