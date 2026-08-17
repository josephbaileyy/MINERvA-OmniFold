# PREDECLARATION — the persisted `C4 = M C5 Mᵀ` identity on the real products

**Written and committed BEFORE execution.** Lane B, 2026-08-16. Consensus run: Joseph ruled *"run it if
there's consensus"*; lanes B and A confirmed independently and the conditions below are the **union** of
both lanes' requirements.

---

## 1. What is being tested, and what is NOT

**Tested:** that the **persisted** 4D covariance (`std_proj4d_candidate.root`, `181,361,072 B`,
`f042e746…`) is the projection of the **persisted** 5D covariance
(`std_final5_candidate.root:hCov_stdcombined5d_total_candidate`, `950f8cb1…`).

**This is not a restatement of stage 6's `projection_identity_relerr = 3.7568690548899724e-16`.** The
mediator's original justification — in-memory versus persisted — was **wrong on the 5D side**:
`p4_project_4d.py:150` already reads `C5` off disk, so the recorded identity was computed on the real
persisted 5D object. The gap is entirely on the **4D side**, and it is this:

* `C4, stats = P.check_projection_validity(C5, M)` runs at `:158`;
* `h.SetContent(np.ascontiguousarray(np.pad(C4, 1), dtype=np.float64).ravel())` writes at `:182`;
* **every gate ran before the write, on the in-memory array**;
* **nothing, anywhere, reads the persisted product back.** Measured: a grep for
  `std_proj4d_candidate` / `hCov_std_proj4d` / `hRowIndex4D` across all `p4_*.py` and `run_p4_*.sh`
  returns one comment (`p4_build_components.py:211`) and one `--out` argument
  (`run_p4_standard.sh:122`);
* the projmanifest records `candidate_c5_sha256`, `central4d_sha256`, `M_content_sha256` and
  `row_index_sha256` — **and no digest of the 4D covariance it just wrote**;
* `row_index_sha256` is hashed from the same in-memory `np.nonzero(m4_eff)` used to write
  `hRowIndex4D`, so **the row binding added specifically so it would "travel with the object" has
  never been read out of the object.**

So a transposition, a pad off-by-one, or a wrong ravel order yields a wrong persisted matrix while
`projection_identity=3.76e-16` and `symmetric_psd` both pass.

## 2. PREDECLARED TOLERANCE — `1e-12`

Fixed here, before execution, and **not** chosen after seeing the number.

Expected agreement is `1e-15`–`1e-14` (float64 round-off over a grouped sum of ~1e8 terms), so `1e-12`
leaves ~100× margin while remaining a number that cannot be talked past. The in-memory leg's `1e-9`
(`check_projection_validity`'s `rtol_identity`) is **too loose to reuse** here, and stage 6's realized
`3.76e-16` is **the wrong baseline to quote at a tolerance** — it is a different comparison.

## 3. `falsified_by` — the observations that would show a defect PRESENT

A defect is present if **any** of these is observed. Each has a reachable other outcome; a pad or ravel
error produces **O(1)** relative deviation, not `1e-16`.

| # | observation | what it would mean |
|---|---|---|
| F1 | `max abs(C4_disk − blocksum(C5_disk, M)) / max abs(C4_disk) > 1e-12` | the persisted bytes are not the matrix that was gated |
| F2 | `C4_disk` asymmetric beyond float64 round-off | pad / ravel / transpose error in the write |
| F3 | `hRowIndex4D` read from disk ≠ the receipt's `row_index_sha256` `de966d2a…` | the row binding in the object is wrong |
| F4 | persisted TH2 dimension ≠ 4825, or `hRowIndex4D` length ≠ 4825 | shape or padding error |
| F5 | the read-back index set disagrees with the recorded unreachable indices `9679, 9686, 9714, 9721, 10169` | the excluded set in the object differs from the one recorded |
| F6 | either product's `sha256` differs before vs after the check | the check was not read-only, contrary to its own claim |
| F7 | the mutation control does **not** fire | the instrument cannot detect a defect and **no PASS may be reported from this run** |

## 4. BINDING CONDITIONS (union of both lanes)

1. **Read `C4` off disk.** Do not recompute and trust.
2. **Recompute with `_block_sum_projection`, never `project()`** — a route sharing no expression with
   the code that wrote the bytes, and cheaper (A measured 1.0 s vs 6.6 s BLAS at this shape).
3. **Mutation control in the same run**: perturb one entry of a **temp copy** of the persisted `C4` and
   show the comparison fires. Per F7, a non-firing control voids the PASS.
4. **Tolerance predeclared** — §2, this file, committed before execution.
5. **Read-only made FALSIFIABLE, not asserted**: `sha256` both products **before and after**, record
   both pairs, require equality (F6). Every `TFile` opened in default `READ` mode. No `UPDATE`, no
   `RECREATE`. **`run_p4_standard.sh` and its stages are NOT invoked** — stages 4/5 rebuild, which is
   the clobber that held the previous run.
6. **Derive the index set from `hRowIndex4D` read out of the object**, not by recomputing `m4_eff`;
   cross-check against `row_index_sha256 de966d2a…` and the recorded unreachable indices. **If those
   disagree, STOP and report — that is a finding and needs no matrix product.**
7. **Assert both dimensions equal 4825** rather than assuming.
8. **Write set: exactly one new receipt JSON** under `docs/orchestration/state/`, plus a force-added
   log (`KNOWN_ISSUES 48`). Nothing else. No ROOT output. Nothing in `candidate/`. Nothing on the
   20-path execution surface.
9. **Record `proj4d_sha256` and the read-back `hRowIndex4D` digest** so the next run detects drift
   rather than re-deriving this gap.

## 5. THE SHARED-`M` LIMIT — A's `BEN-328` claim, ATTACKED

A states the check shares `M`, hence `AXIS_EDGES`, with what it checks, so **a wrong width array or a
wrong drop axis is invisible here, and the recipe gate does not close it either because it rebuilds
from the same edges.** A asked for this to be attacked rather than accepted. Measured:

**The claim is TRUE of the identity and FALSE as a statement of the campaign's exposure, and the two
halves come apart.**

* **Widths: CLOSED by a different gate.** `p4_project_4d.py:74-78` computes
  `ebv = P.edges_bin_volume_hash(edges)` and **requires** `ebv["edge_hash"] == man["edge_hash"]` and
  `ebv["bin_volume_hash"] == man["bin_volume_hash"]`, against the frozen `p4_standard_manifest.json`
  — which additionally carries `axis_edges` verbatim
  (`edge_hash = e05889ac…`, `bin_volume_hash = f71145ce…`). **A wrong width array fails at `:77`
  before `M` exists.** So the edges are gated one level up, which is structurally the *same*
  relationship A itself correctly described for `M`: *"this gate passing says nothing about it; a
  caller that calls only this one has gated the product and not the map."* The edges have their own
  gate; the identity is not it, and does not need to be.
* **Drop axis: GENUINELY UNPINNED, and this is the real residual.** `W_AXIS = 4` is a hardcoded module
  constant at `p4_project_4d.py:27`. Measured: **no manifest key, no hash and no `require` pins the
  dropped axis** — `mask4d_nreported` and `mask4d_hash` are pinned, but `m4_eff` is *derived* and is
  not. A wrong axis is therefore visible only as a change in the derived unreachable set (from the
  recorded 5) rather than against a frozen expectation.
* **Partially self-limiting, which is not the same as gated.** A wrong axis changes the 4D grid
  cardinality, so `reachable_low_mask`'s output length would usually disagree with `m4`'s and raise
  rather than pass quietly. *"Usually raises"* is not a gate.

**So the correct limit statement is narrower and more actionable than A's:** the identity does not gate
the geometry, and it does not need to, because `:77-78` do — **except for the dropped-axis index, which
nothing pins.** The cheap durable closure is to record `w_axis` in the manifest and require it: one
integer, one `require`, and it belongs to repair-12, not to this read-only check.

## 6. TH2 ROUND-TRIP — proved SYNTHETICALLY, at zero cost, not from the real products

`C4` is written as `np.pad(C4, 1)` + `SetContent` and `_th2` reads back `[1:n+1, 1:n+1]` — constructed
inverses. Their fidelity is therefore provable on a small synthetic TH2 and **must not be counted as a
real-product finding**. A 4×4 round-trip runs in the same script at no measurable cost; if it fails,
the real-product comparison is uninterpretable and the run stops there.

## 7. SCOPE OF WHAT A PASS LICENSES — narrow, and pre-committed

**Only: that the persisted 4D covariance is the projection of the persisted 5D covariance.**

Explicitly **NOT**: adoption or promotion (construction is not adoption; the five Gate-6 prohibitions
at `19585b7` stay live); `M`'s correctness (the recipe gate owns that); the physics; the geometry (see
§5); `self_guards_adequate`, which repair-11 records as `NO`; and **not** *"the 5D→4D projection is
verified on the real products"*, which A names as exactly the overreach it had narrowed in `BEN-328`.

**Whether this construction is the identity repair-11's verdict excluded from its scope is a question
for lane C, which wrote the exclusion. Asked directly rather than inferred; this predeclaration does
not assume the answer either way.**
