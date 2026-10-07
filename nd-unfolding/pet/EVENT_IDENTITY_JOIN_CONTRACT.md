# Event-identity export and join contract — G2 full-event inventories

**Scope.** How a row of a G2 full-event inventory (`part_reco`, `measured_pc`, `bkg_part_reco` and
everything aligned to them, plus any per-row result computed from them — PET weights, fold-forward
scalars, per-event diagnostics) is tied back to the event it came from, and what that tie does and
does not guarantee.

**Status.** This document is the contract for a *new* export. It adopts nothing, changes no
production artifact, and quotes no publication number. The G2 inventory NPZ, its digests, and every
receipt bound to them are unchanged by this work — the identity ships as a **sidecar** NPZ written
beside the inventory it describes.

**Route.** `AGENTS.md` → `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md` for the PET workstream;
`nd-unfolding/pet/G2_FULLEVENT_CPP_DUMP_STATUS.md` for the C++ dump this reads.

---

## 1. What identity the files actually carry

The event loop (`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`) writes real event
identity on all four trees under `MNV101_DUMP_POINTCLOUD`, which is the flag the G2 FPS production
used. Measured on the production merged ROOT
(`nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`, sha256
`9a16331f…` per its merge receipt) on 2026-09-18:

| tree | entries | identity branches | leaf type |
|---|---|---|---|
| `mc_truth_denom` | 49,906,108 | `mc_run`, `mc_subrun`, `mc_nthEvtInFile` | `Int_t` |
| `mc_signal_reco` | 49,906,108 | `mc_run`, `mc_subrun`, `mc_nthEvtInFile` | `Int_t` |
| `mc_background` | 566,036 | `mc_run`, `mc_subrun`, `mc_nthEvtInFile` | `Int_t` |
| `data` | 4,119,797 | `ev_run`, `ev_subrun`, `ev_gate` | `Int_t` |

**This corrects a statement in the code.**
`fullevent_fps_dataloader.inventory_order_hash`'s docstring says *"The FPS ROOTs carry NO stable
event keys, so this hash is how training and extraction prove they consume the SAME inventory in
the SAME order."* The first clause is false on the production files. The rest of the sentence
stands: the order hash is a valid **order** witness and this work does not replace it — the two
objects answer different questions, and `assert_identity_consistency` in
`fullevent_dump_contract.py` continues to answer the order one. What the order hash was standing in
for, and could not supply, is a per-row **identity**; that is what this export adds.

MC identity and data identity are **different tuples over different namespaces** and are never
compared. An `ev_gate` is a DAQ gate number; an `mc_nthEvtInFile` is an index within a generated
file. "run/subrun/gate" names the data tuple only.

## 2. The identity tuple

```
(source, run, subrun, event, occurrence)
```

* **`source`** — the playlist (`1A`…`1P`). The G2 inventories are built from a 12-playlist `hadd`,
  and the merged ROOT carries no per-row playlist branch, so `source` is derived from the
  concatenation boundaries declared in `G2_MEFHC_MERGE_RECEIPT.json`'s `ordered_inputs` and then
  **verified**: the audit compares the distinct key set of each declared row range against that
  playlist's own file, so a wrong concatenation order is caught rather than assumed. Whether
  `source` is *required* or merely informative is the measured question of §4.
* **`run`, `subrun`, `event`** — the tree's own identity columns; `event` is `mc_nthEvtInFile`
  (MC) or `ev_gate` (data).
* **`occurrence`** — the 0-based ordinal of a row among rows sharing the same `(source, run,
  subrun, event)`, **computed over the full source tree in entry order and only then restricted to
  the retained rows**. It is `0` everywhere the tuple already identifies, so it costs nothing in
  the unique case, and it is the only thing that separates rows in the non-unique one.

  The ordering matters and is not an implementation detail: an ordinal computed *after* selection
  would renumber when the selection changed, making a row's identity a function of the cut rather
  than of the event. `event_identity.occurrence_index` is documented and tested against exactly
  that confusion.

Packing: `event_identity.pack_identity` packs the three components into one exact `uint64` with
declared bit widths (24 / 16 / 24) and **raises** on any value outside them.

> **Do not join on the C++ `makeEventKey`.** `(run*1e8 + subrun)*1e8 + nth` overflows `uint64` for
> real MINERvA run numbers — run 111353 alone gives 1.11e21 against a ceiling of 1.84e19 — so the
> event loop's dedupe and its miss-append membership test are keyed on a **wrapped** value,
> injective only by arithmetic accident of the observed ranges. `event_identity.cxx_wrapped_key`
> reproduces it exactly, wrap included, so the audit can measure whether that accident holds; see
> §4. Nothing in this export depends on the answer.

## 3. What is preserved

**Selection.** The exporter does not restate the retention rule. It imports
`select_signal_row` and `in_fps_domain` from `dump_pointcloud_inputs` and applies them per row in
entry order, so a change to the production selection moves the exporter with it. Applying the
scalar predicate row by row is deliberate: a vectorised rewrite would be a second implementation
that could disagree exactly at the non-finite and boundary values the predicate exists to handle.

**Row order.** The identity arrays are built by masking the full-tree arrays with the retained-row
mask, so they are in inventory row order by construction. That is then *checked*, not asserted —
see §5.

**Weights.** Untouched. The exporter reads `w_truth` and `w_bkg` only to re-derive the target's own
order hashes; it writes no weights and rescales nothing.

**Native misses.** A truth-only miss (`sim_pass == 0`, `sim` at the −9999 sentinel) is retained by
`select_signal_row` through `pass_truth`, exactly as the dumper retains it, and carries the
`mc_run/mc_subrun/mc_nthEvtInFile` that `AppendTruthOnlyMisses` copied from the truth-denom cache.
Misses are therefore joinable on the same tuple as matched rows, with `pass_reco == False` marking
them. The audit measures this rather than trusting it:
`rows_without_reco.identity_populated` reports whether any row lacking a reconstructed muon
carries an all-zero identity (which would mean such rows are exportable but not joinable).

That field's population is `sim_pass == 0`, which is the union of the appended truth-only misses
and the reco-loop rows that failed the reco gate. It is **not** the C++ `nTruthOnlyMisses` count
and must not be reported as one — see §8, where the two differ by 44%. The appended misses are a
subset, so the identity check covers them.

## 4. Measured uniqueness

See §8 — the measurement is a receipt, not a sentence in this file, and the numbers below are
copied from it with its path and date. Re-run the audit rather than quoting an old number:

```
python3 nd-unfolding/pet/audit_event_identity.py \
    --root 1A=<final>/runEventLoopOmniFold_G2_FPS_1A.root ... \
    --merged <merged>/runEventLoopOmniFold_G2_FPS_MEFHC.root \
    --out EVENT_IDENTITY_AUDIT_MEFHC.json
```

The audit reports, per tree and per playlist: component ranges (the check that the declared bit
widths still cover the data), within-file duplication, cross-playlist key overlap, cross-inventory
set relations, how much work `occurrence` is doing, the identity check on rows without reco, and
the C++ wrapped-key collision count. Its
verdict for each tree is one of `unique-without-source`, `unique-with-source`, or `not-unique`, and
the sidecar carries the verdict it was built under so no consumer has to assume uniqueness nobody
measured.

**A duplication count alone cannot be acted on**, which is why the audit also measures the
*character* of each duplicate block. Rows that agree on their kinematics are an upstream
double-fill and the remedy is a dedupe — this is the known MEFHC 1E `run00111353` case the event
loop already dedupes on the MC side. Rows that *disagree* are distinct physical events sharing the
tuple, and the remedy is the opposite: more identity. `duplicate_block_character` separates them.

## 5. The join contract

### 5.1 Artifacts

| artifact | what it is |
|---|---|
| `G2_FPS_MEFHC_P12.npz` (or a per-playlist equivalent) | the inventory: features, weights, masks, in row order |
| `<inventory>.identity.npz` | **the sidecar**: `{sig,data,bkg}_event_{id,source,occurrence,key}` plus digests, row-aligned to the inventory |
| `EVENT_IDENTITY_AUDIT_*.json` | the uniqueness measurement the sidecar was built under |

Per inventory prefix `p ∈ {sig, data, bkg}` the sidecar carries
`p_identity_fields`, `p_event_id` `(n,3) int32`, `p_event_source` `(n,) int16`,
`p_event_occurrence` `(n,) int32`, `p_event_key` `(n,) uint64`, `p_event_id_hash`,
`p_bound_identity_hash`; plus `identity_source_labels`, `identity_contract_version`,
`identity_uniqueness`, `identity_provenance`.

### 5.2 How a consumer joins

1. Load the inventory and the sidecar.
2. Run `verify_event_identity_sidecar.py --inventory <npz> --sidecar <identity.npz>`, or call
   `event_identity.verify_identity_block(prefix, sidecar, n_rows, inventory_order_hash,
   bound_identity_hash=inventory[f"{prefix}_identity_hash"])` yourself for each inventory you use.
   **Do not skip this.** It is the step that makes row `i` of the sidecar mean row `i` of the
   inventory, and passing `bound_identity_hash` is the part that does it — the exporter's own
   in-process check does not perform that comparison.
3. Join on `(p_event_source, p_event_key, p_event_occurrence)`, or equivalently on
   `(source, run, subrun, event, occurrence)` via `unpack_identity`. Use the playlist *label* from
   `identity_source_labels[source]` when reporting; the integer is an index into that array and is
   not stable across exports with a different playlist set.
4. Read `identity_uniqueness` before assuming a tuple shorter than the full five components
   identifies anything.

### 5.3 What binds a sidecar to its inventory

Row count alone is not a binding — two different dumps of the same ROOT have the same row count.
The exporter re-derives the inventory's **own** stored order hashes from the same ROOT and refuses
to write unless they match:

* `sig_identity_hash` = `inventory_order_hash(w_truth, pass_truth)` — **re-derived and compared**;
* `bkg_identity_hash` = `inventory_order_hash(w_bkg, bkg_indices)` — **re-derived and compared**;
* `data_identity_hash` = `inventory_order_hash(measured_pc)` — its evidence array is the padded
  point cloud, which the exporter does not rebuild. **The data binding is row count plus the
  stored value copied into `data_bound_identity_hash`, and is therefore weaker than the other
  two.** Stated here rather than left to be inferred from an equal-looking field name.

A matching re-derivation proves the exporter retained the same rows in the same order as the dump
it is being joined to. It does not prove the dump is the right dump for your analysis; that is
what `p_bound_identity_hash` and the provenance record are for.

### 5.4 What the join does NOT guarantee

* **It is not a cross-processing identity.** `occurrence` is an ordinal within the source tree's
  entry order. It is stable for a given set of upstream AnaTuples read in the same order, and it
  is *not* stable across a reprocessing that reorders or re-slices events. Where `occurrence` is
  non-zero, the join is to *a row of this production*, not to a physics object that survives
  re-reconstruction. §6 says what would fix that.
* **It is not a `mc_signal_reco` ↔ `mc_truth_denom` bijection claim.** The two trees have equal
  entry counts by the Phase-18.2 `c`-invariant; whether their identity *sets* are equal is a
  separate fact the audit measures per file and that this document does not assert in advance.
* **It does not make a quarantined product quotable.** Identity is plumbing. Every quarantine in
  `AGENTS.md` and `VALIDATION_LEDGER.md` applies unchanged to anything joined this way.

## 6. The upstream remedy, where identity is insufficient

Where the measured verdict is anything but `unique-without-source`, the shortfall is in what the
ROOT carries, not in this export. The durable fix is to write the missing component in the event
loop, so a future production carries a real identity instead of a positional one:

* **`data`**: the MAD AnaTuple's slice identifier alongside `ev_run/ev_subrun/ev_gate`. One DAQ
  gate can contain several reconstructed interactions, and the `data` tree's 24 branches contain
  nothing that separates them.
* **MC**: nothing further is needed if the audit's MC verdict is `unique-without-source` or
  `unique-with-source`; if it is `not-unique`, the duplicate character tells you whether the fix is
  a dedupe (as the event loop already does per playlist) or a further field.

Both are changes to `runEventLoopOmniFold.cpp` and to the hash bindings that pin it, and both are
out of scope here: this work was explicitly not to modify running production. The insertion points
are the four `out->Branch("mc_run", …)` blocks and the data block near the `ev_run/ev_subrun/
ev_gate` writes, each already gated on `MNV101_DUMP_POINTCLOUD`, plus `explicitNames` in
`AppendTruthOnlyMisses` so the KNOWN_ISSUES #12 rebinder cannot override a new branch.

The same applies to emitting identity **inline** in `dump_pointcloud_inputs.py` rather than as a
sidecar. That is the better end state — one file, no re-read of a 113 GB ROOT, no binding problem
— and it is deliberately not done here, because it would change a production dumper whose output
digest and source SHA are bound in receipts and launchers.

## 7. Files

| file | role |
|---|---|
| `nd-unfolding/pet/event_identity.py` | the contract: fields, packing, occurrence, uniqueness primitives, block build/verify. Pure; no ROOT, no TF |
| `nd-unfolding/pet/audit_event_identity.py` | the uniqueness measurement → receipt JSON. Read-only; PyROOT |
| `nd-unfolding/pet/export_event_identity.py` | the sidecar export. PyROOT |
| `nd-unfolding/pet/verify_event_identity_sidecar.py` | the CONSUMER check: sidecar against inventory, NPZ-only, no ROOT |
| `nd-unfolding/pet/smoke_export_event_identity.py` | end-to-end export smoke on a synthetic G2 ROOT |
| `nd-unfolding/pet/sbatch_event_identity_audit.sh` | the audit over 12 playlists + the merged ROOT |
| `nd-unfolding/pet/sbatch_event_identity_export.sh` | the sidecar write for the merged inventory |
| `nd-unfolding/tests/test_event_identity.py` | pure tests; every fail-closed check exercised in both directions |

## 8. Measurement record

Receipt: [`EVENT_IDENTITY_AUDIT_PLAYLISTS.json`](EVENT_IDENTITY_AUDIT_PLAYLISTS.json), committed
beside this file, sha256 `942ebfea4622e11db8cdccf21c87658711f912c70ff096bebcb04adaaa79c535`.
Written 2026-09-19T00:26:39Z by `audit_event_identity.py` at sha256
`f16e9b03598c08da211300b71ce13d6b4bda4d4add6396bce95075272fe33a12` over all 12 per-playlist
G2 ROOTs, **full trees, `truncated_read: false`**.

> The producing sha is the version **before** the `native_misses` → `rows_without_reco` rename,
> so this receipt's field is still spelled `native_misses` and its `n_miss_rows` is the
> `sim_pass == 0` count discussed below, not an appended-miss count. The rename changed a label
> and nothing measured. The current tool is
> `17e3100df3c9c20cb434e682f04e7718f8215e6dd6260b31edddd2226108f2cd`. That the rename is
> label-only is measured, not assumed: re-running the current tool on 1L and diffing every field
> against this receipt's 1L block gives no difference outside the renamed keys, and the renamed
> counts are equal (350,044 == 350,044). It was produced on a login node in ~14 min of
single-core read; no allocation and no write outside the receipt. Re-measure rather than quoting this table; the numbers
below are its contents, not a second source.

### Verdicts

| tree | rows | duplicated keys | duplicated rows | max multiplicity | verdict |
|---|---:|---:|---:|---:|---|
| `mc_signal_reco` | 49,906,108 | 0 | 0 | 1 | `unique-without-source` |
| `mc_truth_denom` | 49,906,108 | 0 | 0 | 1 | `unique-without-source` |
| `mc_background` | 566,036 | 0 | 0 | 1 | `unique-without-source` |
| `data` | 4,119,797 | **212,677** | **433,304** | **5** | **`not-unique`** |

**Cross-playlist: disjoint on all four trees** — 0 overlapping pairs, 0 keys in more than one
playlist. The MC run ranges do not overlap between playlists (1A 110000–110040, 1B 111000–111010,
… 1N 113270–113300), and neither do the data run ranges. So **`source` is informative, not
required**: it is carried because it makes a row's provenance readable and because a future
playlist set could collide, not because today's does.

### `data` is a gate key, not an event key

All **212,677 of 212,677** duplicated-key blocks have **differing** kinematics
(`measured`, `measured_pz`, `mu_reco_E`, `vtx_reco_z`); **zero** blocks are identical. So these
are not upstream double-fills — they are several reconstructed interactions sharing one DAQ gate,
and no dedupe is appropriate. `occurrence` reaches **4** and is non-zero on **220,627** rows
(5.4% of the data inventory); on all three MC trees it is **0 everywhere** and does no work.

This is the one place the join rests on a positional component. §5.4 and §6 say what that costs.

### Native misses

`mc_signal_reco` has **29,315,904** rows with `sim_pass == 0`, and **0** of them carry an
all-zero identity; **0** rows *with* reco carry one either. Every row without a reconstructed
muon — appended truth-only miss or reco-gate failure — is joinable on the same tuple as a matched
row.

> That 29,315,904 is **not** the appended-miss count. The merge receipt's `nTruthOnlyMisses` is
> **20,361,799**; `sim_pass == 0` is the union of those and the reco-loop rows that failed the
> reco gate, and quoting it as "native misses" overstates them by 44%. The identity check covers
> the appended rows as a subset, which is what the join needs.

### Cross-inventory

| pair | shared | only A | only B | equal sets in |
|---|---:|---:|---:|---|
| `mc_signal_reco` ↔ `mc_truth_denom` | 49,906,108 | 0 | 0 | **12/12 playlists** |
| `mc_background` ↔ `mc_signal_reco` | 0 | 566,036 | 49,906,108 | disjoint, 12/12 |
| `mc_background` ↔ `mc_truth_denom` | 0 | 566,036 | 49,906,108 | disjoint, 12/12 |

So signal and truth-denom are a **bijection on identity**, not merely equal in count — a signal
row can be joined to its truth-denominator row — and an identity says unambiguously which
inventory a row came from.

### The C++ wrapped key

`collisions_beyond_exact` is **0** on every tree of every playlist. The `makeEventKey` overflow
described in §2 is real but **latent** on these files: the event loop's dedupe and miss-append
membership test were not corrupted by it. That is a property of the observed run/subrun ranges,
not of the formula, and it is measured per file rather than argued — re-measure before relying on
it for a different playlist set.

### The merged ROOT

> **Redacted for publication (2026-10-06, Joseph's decision).** The two committed audit receipts have every
> `examples` list under a `data` tree emptied: 70 and 60 real MINERvA data run/subrun/event identities.
> Each count is kept in `examples_redacted`, and a top-level `redaction` block records the change. Every
> count, multiplicity and verdict is unchanged. The sha256 values quoted here are those of the **original**
> receipts, which are preserved, with the original 8 commits (head `6023b1b8`), in the git bundle
> `/global/cfs/cdirs/m3246/josephrb/pet-studies-20261006/_git-bundles/worktree-event-identity-export-6023b1b8.bundle`
> (sha256 `3bdc24cc…a4d4`). Sidecars on the cluster record the original receipt's digest.

Receipt: [`EVENT_IDENTITY_AUDIT_MEFHC.json`](EVENT_IDENTITY_AUDIT_MEFHC.json), sha256
`9507a75527295c491f40762a13dda58563df639343cba4263114e0586de1b9bf`, written
2026-09-19T00:39:59Z, `truncated_read: false`. Same 12 playlists plus
`runEventLoopOmniFold_G2_FPS_MEFHC.root`.

| tree | merged entries | Σ per-playlist | counts agree | concatenation order verified | range mismatches |
|---|---:|---:|---|---|---|
| `mc_signal_reco` | 49,906,108 | 49,906,108 | yes | **yes** | none |
| `mc_truth_denom` | 49,906,108 | 49,906,108 | yes | **yes** | none |
| `mc_background` | 566,036 | 566,036 | yes | **yes** | none |
| `data` | 4,119,797 | 4,119,797 | yes | **yes** | none |

"Verified" here is the real check, not the count check: for each playlist the distinct key set of
its declared row range in the merged tree was compared against that playlist's own file, and all
twelve matched on all four trees. So the row → playlist map the sidecar derives from
`ordered_inputs` is the actual concatenation, and `source` is a measured attribute of each merged
row rather than an inference from a filename order.

On the merged file the per-playlist findings reproduce exactly: all three MC trees have **0**
duplicated keys, `data` has the same **212,677 / 433,304 / max 5**, and
`collisions_beyond_exact` is **0** everywhere. Qualifying by `source` changes nothing — `data` is
still `is_unique: false` with the identical counts — which is the direct confirmation that its
duplication is **within** a playlist, not across playlists, and therefore that `occurrence` and
not `source` is what resolves it.

### The produced sidecar

`G2_FPS_MEFHC_P12.identity.npz`, 192,993,519 bytes, sha256
`01e07412b253ff496c30025cc71a9185b166a00892b1e1b4c8bce714ddd5f95c`, written
2026-09-19T01:17:29Z under `$SCRATCH/event-identity-audit/` by job `58553718`
(`COMPLETED`, 5 min 32 s). It is **not** committed — it is a 193 MB derived artifact whose
inputs, tool digests and verification all are.

Row counts match the inventory exactly: **sig 49,152,885 / data 4,116,128 / bkg 564,591**.
`occurrence` is non-zero on **220,439** data rows and **0** on every MC row, reproducing the
audit's finding inside the retained inventory.

**The binding held.** The exporter re-derived the inventory's own stored `sig_identity_hash` and
`bkg_identity_hash` from its independent re-read of the ROOT and they matched, which is what
establishes that it retained the same rows in the same order as the production dump. Had it
retained a different set, or the same set in a different order, it would have refused to write.

Independent readback, by `verify_event_identity_sidecar.py` (a separate program — a producer
validating its own output proves the producer self-consistent, not the artifact correct):
**12 of 12 checks passed, 0 failed**, including the `bound_identity_hash` comparison against the
real inventory that the exporter does *not* perform in-process. Every inventory verified and
bound; **0** retained rows with an all-zero identity anywhere; **28,579,364** native-miss rows
(`pass_reco == False & pass_truth`) present, **0** of them with an all-zero identity.

Provenance recorded inside the sidecar: the omnifile, the target NPZ, the audit receipt, and the
resolved path **and sha256** of both the selection module
(`dump_pointcloud_inputs.py`, `c8fa219f0ca2537b…`) and the order-hash module
(`fullevent_fps_dataloader.py`, `e1402370cdb8bd63…`) — so which selection produced this sidecar
is a recorded fact, not an inference from a directory name.

### A launcher defect this produced, recorded because it fails silently

Batch job `58552413` died in 5 seconds with exit 1 and **both Slurm logs at 0 bytes** — a state
indistinguishable from "never started". Cause, isolated by bisecting the shell flags:
`set -u` plus `source setup_salloc_env.sh`. `root_6_28`'s conda activation runs
`activate.d/activate-binutils_linux-64.sh`, which reads `$ADDR2LINE` unbound; measured,
`set -e` alone survives, `set -u` alone dies 127, `set -eu` dies 1. Both launchers here now
clear `set -u` across the source, keep the source's stderr, and decide on the postcondition
(`import ROOT`) rather than on the source's exit code.

**The same shape exists in four launchers this lane does not own** — `alloc_run.sh`,
`2d-unfolding/sbatch_negweight_cov_analysis.sh`,
`nd-unfolding/sbatch_boot5d_gpu_interactive.sh`, and
`docs/orchestration/runs/clausec-rerun-20260821/harness/submit_clausec.sh` each combine a
`set -*u*` line with an unguarded source of `setup_salloc_env.sh`. Whether each actually aborts
depends on its ordering and guards, which is for their owners to check; the reproduction is
`bash -c 'set -u; cd <repo>; source setup_salloc_env.sh'`. Recorded rather than fixed here,
because editing four other lanes' launchers is not this task.
