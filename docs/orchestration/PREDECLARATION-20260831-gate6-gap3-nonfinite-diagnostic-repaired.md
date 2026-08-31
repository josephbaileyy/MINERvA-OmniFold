# Predeclaration - repaired Gate-6 GAP 3 non-finite energy diagnostic

**Contract ID:** `PET-G6-GAP3-NONFINITE-DIAGNOSTIC-REPAIRED-20260831`

**Preparation base:** `499b0dab93e5ce8aeb881b75ab5154967eae0044`

**Status:** authorized for exactly one repaired diagnostic after every entry preflight passes from
a clean, pushed, immutable checkout. A failure is terminal. No automatic, unchanged, or further
retry is authorized.

## Question and boundary

The job classifies the 2,366 previously observed non-finite raw `part_reco_E` entries and determines
their production rank, stored P=12 representation, PET mask path, possible model influence, and the
scientifically correct denominator for a possible future token-cap measurement. It does not produce
or repair a truncation fraction.

The changed-retry truncation result and failed non-finite diagnostic remain
`INVALID_OR_INCOMPLETE`. Their contracts, jobs, receipts, results, and percentages are immutable and
must not be replaced, reinterpreted, or promoted.

## Frozen scientific operands

The source ROOT is
`nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`, size
`113496440965` bytes and SHA-256
`9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f`.

The stored PET input is `nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz`, size
`9897374636` bytes and SHA-256
`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`. Its producer receipt is
bound at SHA-256 `d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e`.

The populations, selections, cluster definitions, P=12 cap, stable energy sort, kinematic axes,
kinematic bins, source order, and NPZ row order are unchanged from
`PET-G6-GAP3-NONFINITE-DIAGNOSTIC-20260830`:

- signal `mc_signal_reco`: exact production `select_signal_row`; expected source rows `49,906,108`,
  selected reco rows `20,573,521`, and retained NPZ rows `49,152,885`;
- data `data`: expected selected and NPZ rows `4,116,128`;
- background `mc_background`: expected selected and NPZ rows `564,591`; and
- expected raw non-finite energy entries: signal `1,687`, data `456`, background `223`, total
  `2,366`.

No scientific operand may change. The implementation converts the five aligned reco vectors to
`float32` and applies `np.argsort(-energy, kind="stable")`, exactly matching the production dumper.

## Repaired source identity and mapping

ROOT source identity and signal retained-prefix mapping are single-threaded. ROOT implicit
multithreading is disabled and verified disabled before any RDataFrame action. The signal mapper
walks the source TTree in ascending entry order and stores only one prefix count for each affected
selected signal entry. It must not materialize the complete `49,152,885`-row retained index.

The entry preflight must directly recover ROOT entry `10152799` as:

- `sim_pass=0`, `sim=-9999.0`, `sim_pz=-9999.0`;
- `MC=0.2756309263353958`, `MC_pz=5.606105907302817`; and
- exact production predicates `selected=false`, `pass_truth=true`, `keep=true`.

The same sequential preflight must prove `selected && !keep` is zero, reproduce the signal source,
selected, and retained censuses, identify the affected selected entries without `rdfentry_` under
implicit multithreading, and map every affected target by a monotone retained-prefix count.

## Frozen measurements

For every selected affected event, the job must:

1. classify NaN, positive infinity, and negative infinity separately by population;
2. count affected events, non-finite entries, and entries per event;
3. record each non-finite entry's one-based production rank and whether it is inside or beyond rank
   12;
4. compare the reconstructed production cloud, view, time, scalars, weight where present, and signal
   pass flag to the exact stored NPZ row;
5. inspect stored P=12 energy tokens and the hash-bound loader's non-finite-to-zero sanitization;
6. report raw vector length, finite-positive multiplicity, capped finite-positive multiplicity,
   stored finite-positive multiplicity, and the PET `energy != 0` mask multiplicity;
7. test the proposed `energy > 0` interpretation against the actual loader and model source;
8. verify the pre-mask dense encoding, local-neighbor path, first body attention, body re-masking,
   FiLM re-masking, and class-token attention masking; and
9. accumulate the unchanged reco `pT`, `p_parallel`, `Eavail`, `q3`, and Cartesian
   `(pT,p_parallel)` bin counts.

If every provenance, census, alignment, stable-sort, loader, and model-path check passes, the sole
denominator recommendation is `FINITE_POSITIVE_PET_ELIGIBLE_CLUSTERS`. All raw entries remains a
source census containing undefined energy arithmetic. An incomplete diagnostic returns no
denominator recommendation.

## Execution contract

- authorization token:
  `PET-G6-GAP3-NONFINITE-DIAGNOSTIC-REPAIRED-20260831-ONE-SCAN`;
- exactly one Slurm job, one node, one task, 18 allocated CPUs, 32 GiB, two hours, CPU constraint,
  no GPU, no array, and no requeue;
- 36 CPU-hour allocation ceiling;
- source identity and retained-prefix mapper threads: exactly one;
- unique output namespace and clean immutable checkout at the pushed preparation commit;
- guarded execution through `nd-unfolding/mnv_guarded_run.py`; and
- no automatic, unchanged, changed, or further retry after the one submission.

Before `sbatch`, verify the pushed commit, clean checkout, full ROOT and NPZ hashes, producer receipt,
all preserved artifact hashes, new source hashes, ROOT import/JIT, schema, NPZ headers, exact
production predicates, direct real-entry regression, sequential censuses, streaming prefix mapping,
stable-sort fixtures, loader/model path, positive and negative resource guards, disabled implicit
multithreading, and an empty output namespace.

At runtime, repeat every applicable guard and atomically write one result JSON. Terminal verification
must directly inspect Slurm accounting, job specification, result and log hashes, input hashes,
selected-row censuses, finite/non-negative domains, classification totals, source-to-NPZ alignment,
loader output finiteness, model-path findings, and the complete JSON.

## Non-authorization

All diagnostic numbers are nonquotable. No outcome, including `PASS`, can promote the previous
truncation percentages or authorize input filtering or repair, a representation or token-cap change,
retraining, a central-value move, covariance or uncertainty construction, Gate-6 member selection,
Leg 2, further compute, publication claims, or publication edits. A valid truncation measurement
requires a separate decision.
