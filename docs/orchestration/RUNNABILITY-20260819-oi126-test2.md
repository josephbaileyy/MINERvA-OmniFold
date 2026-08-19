# RUNNABILITY — OI-126 Test 2 (target-level spatial probe)

**Filed 2026-08-19 by lane B.** Answers the factual question the ruling refused to answer from prose.
`RULING-20260817-lanec-oi126-branch-set-not-exhaustive.md` §4 names Test 2 and then declines to cost it:
*"per `BEN-384` I am explicitly NOT costing it from this row: its runnability must be established by
writing the invocation and running `verify_hash_bindings.py` against it, not by reading this paragraph.
An item's cost is a property of where its code lives."* This is that establishment.

**THE MEASUREMENT WAS NOT RUN AND IS NOT AUTHORISED.** Joseph's authorisation, relayed via the mediator,
covers writing the invocation and checking hash bindings, and explicitly excludes running Test 2,
submitting compute, modifying pinned files, editing publication text, or changing publication
disposition. Nothing here produces a number about the physics. No cluster access was attempted.

**Invocation:** [`nd-unfolding/pet/probe_oi126_test2_target_level_spatial.py`](../../nd-unfolding/pet/probe_oi126_test2_target_level_spatial.py)

Every claim below carries **MEASURED** (I ran something and read the result), **INFERRED** (derived from
something measured, stated with its derivation), or **NOT ESTABLISHED**.

---

## 0. Headline

**Test 2 is NOT RUNNABLE FROM THIS MACHINE, and it is not blocked on anything else.** All three input
classes are cluster-only; none is in the local checkout or the git index. The code is written, its
guards are power-tested, and its hash bindings are clean, so **the cluster-return step is one command,
not an investigation** (§6). Compute cost is **~3 s single-core, ~190 MiB** — Test 2 is not expensive;
it is merely somewhere else.

---

## 1. Where the arrays live, and whether anything is reachable

| input | path | reachable here? |
|---|---|---|
| 50 per-replica refined targets | `<family_root>/replicas/replica_{00..49}/target/GATE5_REPLICA_TARGET.npy` | **NO** |
| family root | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50` | **NO** |
| certified Gate-2 nominal target | `<REPO>/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` | **NO** |
| source dump (kinematics) | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz` | **NO** |

- **MEASURED.** `ls` on all four: every one `No such file or directory`. `/pscratch/sd/j/josephrb` is not
  a directory on this host. `git ls-files --error-unmatch` on the nominal target returns *"Did you forget
  to 'git add'?"* — it is **not tracked**. The local `gate2/final/` directory holds only
  `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` and three `superseded-*` subdirectories: **the receipts are
  local, the arrays are not.**
- **NOT ESTABLISHED: whether the cluster is reachable right now.** I was instructed not to touch it and
  did not. This does not affect the headline — the arrays are not on this filesystem either way, so
  Test 2 cannot run here regardless of `ssh` state.
- **Neither HPSS nor an off-scratch copy was found for these arrays.** Searched the tracked tree; no
  archival location is recorded. Scratch is purgeable, which makes this a live exposure rather than a
  detail — but it is **NOT ESTABLISHED** whether a copy exists somewhere unindexed.

### The inventory the ruling refers to

**MEASURED.** `docs/orchestration/state/gate5-target-promotion-evidence-56873858/GATE5_TARGET_FAMILY_RECONCILIATION.slurm-56873858.json`
carries `target_sha256_measured` for all 50 replicas — 50 occurrences, one per entry in `.targets[]`.
Read directly:

- indices `0..49` contiguous: **True**
- distinct digests: **50 of 50** (the pairwise-distinctness the ruling cites)
- nominal-target collision: **False**
- `.root` = `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50` (`:1`, key `root`)
- `.counts` = `targets_present 50, targets_passing 50, targets_absent 0`
- every `target_size_bytes_measured` = **18723004**, identical across all 50

A second copy of the same 50 digests is at
`docs/orchestration/state/gate5-family-promotion-evidence-20260814/family-20260814-FULLSTRENGTH-50of50.json`.

**The nominal target's digest is `544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9`** —
**MEASURED** at `nd-unfolding/pet/sbatch_gate5_target_family_reconcile.sh:29` and
`sbatch_gate5_training_family_validate.sh:34` (identical), cross-checked at
`VALIDATION_LEDGER.md:808` (`VL87`, "refined target sha256") and
`nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json:281`. Its **filename** comes
from `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md:154` and from the launchers that consume it
(e.g. `sbatch_step1_iteration_dynamics_array.sh:32`). Note the digest is **not** hardcoded in the
reconciler — deliberately, per `reconcile_gate5_family.py:151-152`.

---

## 2. Array shapes and dtype

- **MEASURED.** `4680719` rows: `G2_GATE2_TARGET_RUNTIME_RECEIPT.json:135` (`n_measured_rows`), `:277`
  (`rows`), and `gate2/benchmark/gate2-hedge-56139568/G2_GATE2_BENCHMARK.json:10`
  (`full_refinement_rows`).
- **MEASURED, dtype `float32`.** Not read off a receipt — *reproduced*: I wrote a synthetic
  `np.float32` array of 4,680,719 elements with `np.save` and its on-disk size was **exactly
  18723004 bytes**, matching every inventoried `target_size_bytes_measured`. (`4680719*4 + 128`-byte
  header `= 18723004`.) A float64 array cannot produce that size.

---

## 3. The loader entry point — and the one place the ruling's wording does not survive contact

**The ruling says "using the loader's own per-event assignment." NOT ESTABLISHED — because no such
callable exists.** This is the single most consequential finding here, and a reviewer should check it
first.

- `build_fullevent_loaders` (`nd-unfolding/pet/fullevent_fps_dataloader.py:1077`) returns
  `(data, mc, imc, coord_reco, coord_gen, meta)`. **MEASURED:** `coord_reco` is **not a bin index** —
  `build_reco_cloud` (`:136-177`) returns the literal tuple `(1, 2)`, the point cloud's *(pos, z) KNN
  neighbourhood columns*. Its own docstring says so: *"coord_idx is (1,2) either way => the KNN
  neighborhood stays the (pos, z) detector geometry."*
- The binned refiner `stay_positive_refine_binned(signed_w, cell, n_cells)` (`:628`) **receives** `cell`
  and does not derive it; `build_negweight_refined_target(data_cell, bkg_cell, ...)` (`:642`) likewise.
- **MEASURED:** `grep -n 'digitize\|searchsorted\|ravel_multi_index'` over the loader returns **zero
  hits**. Nothing in it maps an event to a reco-grid cell.
- **And the production nominal does not use the binned path at all**: it refines over *features* via
  `refine_signed_measured` / `learned_stay_positive_refiner` (`:667`, `:708`).

**Consequence, stated so the next reader does not inherit my wording as authority:** the faithful
reconstruction is *the loader's own canonical edges, its own guard, and `digitize`* — which is what
`cell_index()` in the probe does, importing `CANONICAL_PT_EDGES`, `CANONICAL_PPARALLEL_EDGES`,
`assert_extended_fps_edges` and `SCALAR_COLS` from the pinned loader rather than restating any of them.
**This is a reconstruction, not the loader's own assignment, and Test 2's result inherits that.** It is
the sort of gap that should be ruled on rather than absorbed.

**It can be called without training anything — INFERRED, and the inference is short:** the probe never
imports TensorFlow, never constructs a model, and never calls `build_fullevent_loaders`; it reads arrays
and histograms them. Its `--help` runs to completion locally under the Mac interpreter, which means the
loader module *imports* here even though its inputs do not exist (**MEASURED**, `HELP_RC=0`).

### Row order, which the probe must match or every number is misaligned

**MEASURED** from `build_signed_measured_inventory` (`:675-705`): it returns
`feat = np.vstack([fd, fb])` and `signed = concatenate([data_signed, bkg_signed])` — so the refined
target's rows are **the data rows followed by the aligned background rows**, in that order. The
kinematics are therefore two concatenations, and they are **columns of a scalars block, not standalone
npz keys**: `SCALAR_COLS` (`:76`) puts `pt` at column 0 and `pparallel` at column 1 of
`measured_scalars` (data) and `bkg_reco_scalars` (background). Both npz keys are in the loader's own
read set (**MEASURED** — the loader reads `measured_scalars`, `bkg_reco_scalars`, `pass_reco` among 24
keys). FPS misses carry `SENTINEL = -9999.0` (`:96`, `:446`) and are excluded and counted separately.

**NOT ESTABLISHED: `n_data` and `n_bkg` individually.** Only their sum (4,680,719) is recorded in a
receipt I can read. The probe therefore asserts `n_data + n_bkg == target rows` and fails closed on
mismatch rather than assuming a split.

---

## 4. The grid, and the three regions

**MEASURED** by importing the pinned loader:

- `CANONICAL_PT_EDGES`, 16 edges → **15 pT bins**: `0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30`
- `CANONICAL_PPARALLEL_EDGES`, 20 edges → **19 p∥ bins**: `0, 0.75, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60, 120`
- **285 cells** (15 × 19). *(The 266-cell figure elsewhere is the adopted common reported mask, a subset;
  this probe histograms the full 285 and does not apply that mask.)*

**The ruling's three regions resolve exactly, MEASURED:** `edges[10] = 6.0` and `edges[16] = 20.0`, so
"band cols 10–15" is p∥ ∈ [6, 20] GeV and the two flanks are the ruling's own "below 6 GeV" / "above
20 GeV". Column counts **10 / 6 / 3 = 19**. The probe asserts those two edge values and refuses if the
grid drifts, so the region names cannot silently come to mean different physics.

---

## 5. Cost if run — derived from the shapes above, not from prose

**MEASURED** on synthetic arrays of the real shape (4,680,719 float32), this machine, single core:

| stage | one array | × 51 |
|---|---|---|
| sha256 (digest binding) | 0.021 s | **1.1 s** |
| `np.load` | 0.004 s | **0.2 s** |
| one `bincount` histogram pass | 0.025 s | **1.3 s** |
| | | **≈ 3 s total** |

**Peak resident ≈ 190 MiB** (float64 working set: `pt`, `pp`, `cell`, `nominal`, one replica at 35.7 MiB
each, plus two boolean masks at 4.5 MiB) — **INFERRED** from the shapes, arithmetic shown.

**NOT ESTABLISHED: the cost of extracting `measured_scalars` and `bkg_reco_scalars` from the 9.9 GB
`.npz`.** It depends on the archive's compression, which I cannot inspect without the file. Two bounds
that are established: only those two blocks are touched, never 9.9 GB; and **`mmap_mode` is silently
inert for `.npz`** — **MEASURED**, `np.load(z, mmap_mode="r")["x"]` returns a plain `ndarray`, not an
`np.memmap`. The probe therefore does not pass it, so as not to advertise a memory bound it lacks.

**No GPU, no unfolding, no training, nothing written inside the promoted arm.** Comfortably a login-node
or `--qos=interactive` job.

---

## 6. What would be needed the hour the cluster returns

One command. `$REPO` = `/pscratch/sd/j/josephrb/MINERvA-OmniFold`.

```
python3 $REPO/nd-unfolding/pet/probe_oi126_test2_target_level_spatial.py \
  --family-root    $REPO/nd-unfolding/pet/fullevent_cstat_n50 \
  --nominal-target $REPO/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy \
  --nominal-target-sha 544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9 \
  --source-npz     $REPO/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz \
  --reconciliation $REPO/docs/orchestration/state/gate5-target-promotion-evidence-56873858/GATE5_TARGET_FAMILY_RECONCILIATION.slurm-56873858.json \
  --out            $REPO/docs/orchestration/state/OI126-TEST2-<jobid>.json \
  --expect-below -0.128 --expect-band 3.555 --expect-above -1.828
```

Needs only a numpy interpreter — **not** the TF module, since nothing is trained. Prerequisite: a
ruling on §3 (the reconstructed assignment), because that is a method choice and not a detail.

**`verify_hash_bindings.py` CAN be run locally with the inputs absent — MEASURED, and it was.** It walks
receipts and shell pins in the checkout, not campaign data, so it is a *code*-provenance check and is
fully available here. That is why the runnability question was answerable at all.

---

## 7. `verify_hash_bindings.py` — real unpiped output, rc=0

```
resolved 185 bindings (609 unresolvable: data files, off-repo artifacts, binaries)
  181 OK
  15 of them from EXPECTED_*_SHA guards in *.sh (22 pins seen, floor 15)
  170 of them from receipt bindings (floor 140)
44 canonical-namespace FIELD pins verified (floor 30) over 17 of 22 RECORD-FROZEN JSON receipts -- these pin a POINTER, not bytes; green says the receipts still point where they pointed
  4 known pre-existing drift (submit-time provenance):
      docs/orchestration/wakerctl.py  <- p3f-pet-gate3-queue-latency-reconciliation-56169838.json
      docs/orchestration/test_wakerctl.py  <- p3f-pet-gate3-queue-latency-reconciliation-56169838.json
      nd-unfolding/pet/sbatch_dump_g2_mefhc.sh  <- g2-dump-submit-20260719.json
      docs/orchestration/gate2_queue_hedge_controller.sh  <- gate2-queue-hedge-recovery-armed-20260719.json

ALL BINDINGS INTACT
```

`ALL BINDINGS INTACT`, exit **0**. The four drift rows are pre-existing and named by the tool as such;
none is touched by this work. **The probe pins nothing and is pinned by nothing** — it is new, carries no
`EXPECTED_*_SHA`, and appears in no receipt, so it neither creates nor voids a binding. Its own
provenance discipline is at *call* time: it re-hashes all 51 arrays against the inventory and refuses on
any mismatch.

---

## 8. Fail-closed behaviour — power-tested, not asserted

**MEASURED**, run locally against the real (absent) paths:

```
[oi126-test2] FAIL-CLOSED: certified Gate-2 nominal target is absent, or is a symlink, at
../g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy. This probe does not substitute,
reconstruct or skip an input -- if the array is not visible from HERE, the answer is that this probe is
not runnable here, which is itself the finding.
EXIT=1
```

No output file was created. The grid logic was then exercised on synthetic events, with no cluster input:

- 19 in-grid events (one per p∥ column) + 2 deliberate out-of-grid → `in_grid=19, out_of_grid=2`
- region column counts `10 / 6 / 3`, band edges `[6.0, 20.0]` GeV
- out-of-grid events get cell `-1`, **not clipped**. This matters: `np.clip` would pile overflow into
  the edge bins, and those edge bins ([4.5, 30] in pT, [0, 0.75] and [20, 120] in p∥) are exactly the
  catch bins the extended grid exists to hold — so clipping would corrupt the two regions the −1.828
  comparison is about.
- the drifted-grid guard was made to fire by substituting a 19-edge integer grid: refused.

Guards that exist but could not be fired locally, because firing them needs the arrays
(**NOT ESTABLISHED** by execution, present in code): digest mismatch vs the inventory, two byte-identical
replicas, a replica equal to the nominal, row-count mismatch between target and inventory, missing npz
block, scalars-column drift, and `--out` already existing.

---

## 9. What Test 2's result would and would not mean

**Do not read a Test 2 result as adjudicating branch (c).** §4 designed it for that, and **(c) is
already refuted by lane D independently** — mass-addition limb null with power at +0.000179%, 0.03 SE,
19 of 50 above; redistribution limb requires a nonlinearity inactive in the band, 0 of 86 cells. A pass
here would not establish (c); a fail would not refute it. Both are already decided.

**Its remaining value is real, unique, and narrower than the ruling implies: LOCALISATION.** The
2026-08-15 push-versus-extraction split localised the band deficit to *training*, but push and
extraction are **both downstream of the targets**, so nothing on the record probes the layer above
them. Test 2 is that probe: it asks whether the structure is already present in the targets themselves.
Both statements are carried in the probe's own docstring and in every JSON it writes
(`WHAT_THIS_DOES_NOT_SETTLE`), so a future reader who finds only the artifact still gets the caveat.

The probe reports the gap and per-region sign agreement and **makes no verdict**
(`INTERPRETATION_IS_NOT_MADE_HERE`). Whether the structure "reproduces" is a ruling, not a computation.

---

## 10. Open, for whoever rules next

1. **§3 needs a ruling before the number is quotable.** "The loader's own per-event assignment" does not
   exist as a callable; the probe reconstructs it from the loader's edges. That is a method choice.
2. **`n_data` / `n_bkg` individually are unrecorded** — only the sum. The probe fails closed rather than
   assuming a split, but a receipt naming them would remove a whole class of misalignment.
3. **The 51 arrays exist only on purgeable scratch** with no archival copy found. Independent of Test 2,
   and larger than it.
4. **Test 2's cost was never the obstacle** — ~3 s and ~190 MiB. Anything that framed it as expensive
   was costing it from prose, which is exactly what `BEN-384` warns against.
