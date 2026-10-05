# Extraction and identity contract for Gregor's representation

> **R-1 IS DELIVERED, AND IT CORRECTED THIS DOCUMENT — 2026-09-19.** Agent A built,
> measured and verified the event-identity export. Two things below were wrong:
>
> 1. **`(ev_run, ev_subrun, ev_gate)` is a GATE key on the `data` tree, not an event
>    key.** 212,677 keys over 433,304 of 4,119,797 rows repeat, up to multiplicity 5,
>    and **all 212,677 duplicate blocks differ in kinematics** — muon, vertex,
>    vertex z by metres. They are distinct interactions sharing one DAQ readout.
>    **Do not dedupe them.** Anything in this lane that keys, groups or joins data
>    rows on the bare triple silently merges distinct events on ~10.5 % of rows.
>    The join key is `(source, run, subrun, event, occurrence)`.
>    The three MC trees are clean: zero duplicates over 49,906,108 + 49,906,108 +
>    566,036 rows.
> 2. **The premise that the FPS ROOTs carry no stable event keys is false.** All four
>    trees carry identity under `MNV101_DUMP_POINTCLOUD`.
>    `inventory_order_hash` remains a valid ORDER witness — it just never was an
>    identity, and its docstring says otherwise.
>
> Positives that change what is possible here: `mc_signal_reco` and `mc_truth_denom`
> have **equal identity sets in 12/12 playlists** (49,906,108 shared, 0 either side),
> so a signal row joins to its truth-denominator row as a bijection;
> `mc_background` is disjoint from both, so an identity says which inventory a row
> came from; and the 28,579,364 native no-reco rows are preserved and joinable with
> no all-zero identities.
>
> Also do not join on the C++ `makeEventKey`: it **overflows uint64** for real run
> numbers (1.11e21 against a 1.84e19 ceiling), so the event loop's dedupe and
> miss-append membership test key on a wrapped value. Measured collisions are zero on
> every tree of every playlist — latent, not live.
>
> Artifact: `$SCRATCH/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz`, sha256
> `01e07412…`, a row-aligned sidecar; production NPZ and every receipt bound to it
> untouched. **Run `nd-unfolding/pet/verify_event_identity_sidecar.py` before any
> join.** The join is theirs; `identity_contract.py` verifies, it does not
> reimplement.

**CITABLE FOR:** what must be extracted, how it must be joined, and what authorization
that needs.
**NOT CITABLE FOR:** permission to read anything. §3 exists because an earlier draft of
mine got the authorization scope wrong.

---

## 1. Field-by-field extraction

`tuple` = MasterAnaDev AnaTuple. `ROOT` = Agent A's event-loop output
`runEventLoopOmniFold_G2_FPS_MEFHC.root`. `npz` = `G2_FPS_MEFHC_P12.npz`, what the
estimator reads.

| Gregor field | our branch | tuple | ROOT | npz | action |
|---|---|:--:|:--:|:--:|---|
| muon 4-vector, φ, q/p, MINOS flag | `mu_reco_*`, `mu_reco_minos_ok` | ✓ | ✓ | ✓ `reco_muon` | none |
| reco vertex | `vtx_reco_{x,y,z}` | ✓ | ✓ | ✓ `reco_vertex` | none |
| per-token view, time | `part_reco_view`, `part_reco_time` | ✓ | ✓ | ✓ | none |
| **cap, overflow aggregate, merged count, discarded energy** | full-length `part_reco_*` | ✓ | ✓ **full length** | ✗ truncated to 12 | **dump change + re-run. No C++.** |
| photon energy | `gamma{1,2}_E` | ✓ **A1** | ✗ | ✗ | export |
| photon direction, dE/dx, time, subdetector energies | `gamma{1,2}_{direction,dEdx,time,energy_*,evis_*}` | ✓ | ✗ | ✗ | **new authorization** + export |
| blob position, time, total energy, 3-D flag, cluster count | `MasterAnaDev_Blob{X,Y,Z,T,TPos,TotalE,Is3D,NClusters}` | ✓ | ✗ | ✗ | **new authorization** + export |
| blob multiplicity | `MasterAnaDev_BlobTotalE_sz` | ✓ **A1** | ✗ | ✗ | export |
| prong 4-vector, position, PID, dE/dx, score, mass, charge | `prong_part_{E,pos,pid,score,mass,charge}`, `prong_dEdXMean` | ✓ | ✗ | ✗ | **new authorization** + export |
| prong multiplicity | `n_prongs` | ✓ **A1** | ✗ | ✗ | export |
| 16 event globals | `muon_fuzz_energy`, `muon_iso_blobs_energy`, `MasterAnaDev_hadron_recoil`, `part_response_*_{id,od}`, `improved_nmichel` | ✓ | ✗ | ✗ | **new authorization** + export |
| per-type energy sums | derived | — | — | — | derive **before** the cap, not after as he does |

**The cap is ours.** The dump binds `ROOT.std.vector("double")` cloud buffers and
`_pad_tokens` truncates them (`dump_pointcloud_inputs.py:90-112, 252-268`), which is what
the interface request means by *"the top-12 truncation is a loader choice"*. Raising the
cap, aggregating overflow and recording merged counts and discarded energy therefore need
**a Python change and a dump re-run, not a C++ change**.

---

## 2. Identity and alignment

The npz rows are positional and carry **no event key**; the tuple carries
`ev_run`, `ev_subrun`, `ev_gate`. So the join is possible only if the dump emits those
keys. `identity_contract.py` implements every check below and `test_contracts.py`
exercises each against the direction it must fail in.

| # | hazard | check | on failure |
|---|---|---|---|
| I1 | **key collisions in the source** | `(run, subrun, gate)` unique | **stop.** A repeated key makes the join not a function; picking a winner is silent corruption |
| I2 | **key collisions in the target** | unique across estimator rows | **stop.** Two rows claiming one event means row identity ≠ event identity |
| I3 | **unmatched estimator rows** | every `pass_reco` row matches | **stop.** Zero-filling makes "absent" indistinguishable from "genuinely zero" — the defect we refuse in his own scheme |
| I4 | **native truth-only misses** | unmatched rows allowed **iff** `pass_reco` is false | accepted and **counted**. Conflating these with I3 would let a real defect hide in an expected population |
| I5 | **ordering** | the joined block is in estimator-row order | **stop.** A join returning source order is correctly shaped and entirely wrong |
| I6 | **inventory symmetry** | identical typed-field sets for signal, data, background | **stop.** An asymmetric field set is an inventory label the step-1 classifier can exploit — leakage, not bookkeeping |
| I7 | **provenance** | sha256 of every source file, every manifest, and the npz | recorded in the receipt; a digest proves what was read, never that the right file was named |
| I8 | **selection and weights preserved** | FPS domain gate; `pass_reco`/`pass_truth`; `-9999` sentinels handled as the loader does; RAW `w_truth`/`w_reco`/`w_bkg` with `pot_scale` applied downstream; negweight background inventory; CLM-007 fail-closed data leg; the three identity hashes unchanged | **stop** on any change |
| I9 | **per-event order proof** | positional agreement against the ROOT, on the `build_bkgsub_pointcloud_input.py` precedent | row-count alignment alone is already flagged insufficient by the feature contract |
| I10 | **truth-derived types excluded** | every type code is reconstruction-derived | **permanently excluded** otherwise — direct leakage |

**Two routes, both requests to Agent A** (who owns `runEventLoopOmniFold.cpp`; the
interface request says *"Do not edit A's running C++"*):

* **R-1, recommended:** emit **three scalar branches** `ev_run`, `ev_subrun`, `ev_gate`
  on `mc_signal_reco`, `data` and `mc_background`. Everything else stays ours. Smallest
  possible C++ ask; the price is that we must *prove* the join, which §2's checks do.
* **R-2:** emit ~21 typed-object vector branches. No join risk; a much larger ask, and it
  fixes the vocabulary in C++ where we cannot iterate on it.

---

## 3. Authorization scope — a correction I owe

**An earlier draft of mine said every typed field was "already inside the A1-authorized
branch set". That is wrong.** It is inside
`typed_descriptor_source_smoke.REQUIRED_BRANCHES`, which is a **different and broader**
clearance covering a fixed-source 15-entry smoke.

**A1 authorized 19 branches** (`source-multiplicity.json` `branches_read`): the three
event keys, six `cluster_*` vectors with their six `_sz` counts,
`MasterAnaDev_BlobTotalE_sz`, `n_prongs`, `gamma1_E`, `gamma2_E`. Its scope sentence is
*"counts and cluster energy only; no positions, timing, truth, weights, or muon
kinematics."* So for blobs and prongs A1 covers **the counts, not the values**.

**And the existing guard cannot catch an overrun.** `characterize_source_multiplicity.py`
asserts its branch list is a subset of `REQUIRED_BRANCHES` — **75 branches against A1's
19**. Adding `MasterAnaDev_BlobX` would satisfy the guard and exceed the authorization
silently. Measured by `authorization_scope.audit_guard`; it is a schema check, not a
permission check, and must not be cited as one. The read that actually ran was inside A1;
what is defective is the guard, not the result.

**`authorization_scope.py` enforces the authorization itself**, and reports the
mirror-image case (authorized branches nothing reads) rather than ignoring it.

**Exactly 21 branches need a new authorization** for the typed vocabulary, measured by
`authorization_scope.typed_object_gap`:

```
MasterAnaDev_BlobIs3D, MasterAnaDev_BlobNClusters, MasterAnaDev_BlobT,
MasterAnaDev_BlobTPos, MasterAnaDev_BlobTotalE, MasterAnaDev_BlobX,
MasterAnaDev_BlobY, MasterAnaDev_BlobZ, gamma1_dEdx, gamma1_direction,
gamma1_time, gamma2_dEdx, gamma2_direction, gamma2_time, prong_dEdXMean,
prong_part_E, prong_part_charge, prong_part_mass, prong_part_pid,
prong_part_pos, prong_part_score
```

plus the event-global branches, which are not in `REQUIRED_BRANCHES` at all and would
need enumerating separately. A request must name the branches, the entry count, and what
is emitted — the shape A1 itself took.

---

## 4. What is executable now, and what is not

| item | status |
|---|---|
| all identity checks I1–I10, as tested code | **done** — `identity_contract.py`, 14 tests |
| authorization-scope enforcement and the guard audit | **done** — `authorization_scope.py`, 6 tests |
| the typed-branch gap, enumerated | **done** — 21 branches |
| the join itself | **blocked on R-1 or R-2** (Agent A) |
| reading typed values at scale | **blocked on a new authorization** (Joseph) |
| raising the cap / aggregating overflow | **unblocked** — ours, needs a dump re-run |
