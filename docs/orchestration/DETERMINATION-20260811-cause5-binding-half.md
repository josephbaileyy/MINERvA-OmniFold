# DETERMINATION 2026-08-11 — which half of quarantine cause 5 is binding

**Owner:** Session C (PET). **Question asked:** `VALIDATION_LEDGER.md:83-84` quarantines the recoil-PET
budget *"pending a joint nuisance--retraining construction and selection-complete detector samples."*
Establish which of those two is the binding half before starting work on either.

**Answer: the JOINT NUISANCE-RETRAINING CONSTRUCTION is binding. The selection-complete detector
samples already exist, are Gate-3 promoted, and have been since 2026-07-20.** Every number below comes
from a command run on 2026-08-11.

---

## 1. Why anyone would expect the opposite, and the distinction that resolves it

`KNOWN_ISSUES.md` #19 says *"no full-event FPS **result** exists"* — true — and every downstream summary
has been read as *"no full-event anything exists"* — false. **Inputs and products are different
objects.** The full-event PET *estimator's* products (weights, cross section, covariance) do not exist.
The full-event *selection-shifted detector samples* do, and they are the more expensive object.

This distinction is the whole determination, and getting it wrong costs in the direction of doing the
120-endpoint C++ event-loop dump twice.

## 2. The selection-complete detector samples EXIST — measured, not inferred

    /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/final/

| quantity | measured 2026-08-11 |
|---|---|
| files | **120 ROOT + 120 receipt**, 1.1 TB (`du -sh` 1.1T; manifest's own 9.4 GB × 120 = 1.128 TB ✓) |
| receipt verdicts | **120 PASS, 0 non-PASS** — every receipt parsed, not sampled |
| declared inventory | 5 band × 2 endpoint × 12 playlist = 120, **exactly matched** |
| bands | `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` |
| schema | **`g2-fullevent-v1`** — binary sha `61d7dfbf…` built from `486e53e`, under `MNV101_ACTIVE_UNIVERSE=BAND:IDX` + `MNV101_DUMP_POINTCLOUD=1` + `MNV101_FULL_PHASE_SPACE=1` |
| gate | `state/p3f-pet-gate3-promotion-56169838.json` — **`GATE3_PROMOTED_PASS`**, `promoted_at_utc 2026-07-20T23:58:00Z`, `all_120_terminal_accounting: true` |
| array reconciliation | `state/p3f-pet-gate3-source-manifest-56169838.json` — `PASS`, `expected_tasks 120`, `reconciled_tasks 120`, `errors []`, `receipt_published_last: true` |

**These are the five genuinely kinematic lateral bands** — the same five whose GBDT counterpart
discharged quarantine cause 7 on 2026-08-07 (ledger `:90-118`, job `56431823`), where
`MinosEfficiency` and `GEANT_*` are weight-only and correctly stay ordinary universe bands.

**They are full-event, not recoil.** `MNV101_FULL_PHASE_SPACE=1` + `MNV101_DUMP_POINTCLOUD=1` and the
`g2-fullevent-v1` schema are what the 2026-08-01 landing defines, so these are *not* pre-08-01
different-estimator samples. `validate_p3f_pet_fullevent.py` states this at its head: the older MD5-`e63c`
scalar ROOTs are controls only and *"do NOT establish the g2-fullevent-v1 schema."*

**Write conditions established before reading any of it as evidence.** The validator writes its receipt
*"with unique-temp + fsync + atomic `os.replace` ONLY to the caller-supplied WORK path"* and *"NEVER
publishes a final ROOT or a production receipt"* — publication is a separate Gate-3 promotion step. The
source manifest records `receipt_published_last: true`. So a receipt's presence in `final/` means the
work completed, not that it was attempted. A `PASS` there is not a file written on failure.

**What the samples' own gate does NOT establish, in its own words:** integrity was verified by
*"existence + `size_bytes` match against the receipt-recorded sha256 produced in-job at validation
time; per-file 9.4GB ×120 rehash not performed."* So a silent partial corruption would not have been
caught by that manifest. This mattered enough to act on — see §5.

## 3. The joint construction DOES NOT EXIST, and what exists is the defect

The note states cause 5's requirement algebraically (`sec_pet.tex:117-127`). For a nuisance endpoint
`u`, the physical shift and the induced retraining response form **one** joint shift

        δ_u = x_u^{varied+retrained} − x_CV

and *"writing this as a frozen-map piece plus a retraining increment is an algebraic decomposition, but
adding the two separate covariances omits `Cov(δ_frozen, δ_retrain)` and its transpose. Positive
semidefiniteness of that sum does not restore the missing cross term."*

**The historical recoil-PET assembly is exactly the construction that sentence rules out.** `C_syst` is
built from `s_u = x_frozen − CV`; `C_retrain` (Phase 7) from `Δ_u = x_retrain − x_frozen`; and
`PET_UQ_PRODUCTION_STATUS.md:244-250` defends summing them with an explicit no-double-count note — *"the
two blocks sum DISJOINT quantities."* **That argument is correct about the shifts and silent about the
covariance.** With `δ = s + Δ`,

        outer(δ,δ) = outer(s,s) + outer(Δ,Δ) + outer(s,Δ) + outer(Δ,s)

and the assembly keeps the first two terms only.

### 3.1 So it is measurable, and it was measured

Every operand is stored per bin (`products/pet/bkgsub/p7/pet_p7_<tag>_response.npz` carries `cv`,
`x_frozen`, `x_retrain`, `reported_mask`). Measured by
`nd-unfolding/pet/measure_joint_vs_additive_nuisance_retrain.py`, receipt
`products/pet/bkgsub/pet_joint_vs_additive_retrain.json`:

| universe | ‖s‖ | ‖Δ‖ | ‖joint δ‖ | additive √(‖s‖²+‖Δ‖²) | additive/joint | cos(s,Δ) |
|---|---|---|---|---|---:|---:|
| `2p2h:1` | 7.73741e-39 | 5.11033e-39 | 8.53834e-39 | 9.27270e-39 | **1.0860** | −0.165 |
| `CCQEPauliSupViaKF:1` | 7.59828e-39 | 6.16815e-39 | 4.09545e-39 | 9.78672e-39 | **2.3897** | −0.843 |
| `LowQ2:1` | 8.69552e-39 | 8.25841e-39 | 4.09574e-39 | 1.19922e-38 | **2.9280** | −0.885 |
| `MaCCQE:1` | 1.02987e-38 | 1.28115e-38 | 9.48537e-39 | 1.64377e-38 | **1.7330** | −0.683 |
| `MaRES:1` | 1.36324e-38 | 1.32354e-38 | 1.01691e-38 | 1.90005e-38 | **1.8685** | −0.714 |

**Knob-band aggregate (like-for-like): additive √tr `3.093207e-38` vs joint √tr `1.731571e-38` —
the additive construction OVERSTATES the joint covariance by `1.786`×.**

**The cross term is negative in every single universe.** So cause 5 is not only a correctness defect:
the quarantined budget is **inflated by its own construction**, and the direction of the repair is
knowable before the full-event build exists. Realized per-universe range **1.086 to 2.928** over 5
universes — a realized range, not a fitted interval (BEN-025).

### 3.2 Why this is a measurement and not an argument

- **The identity is checked, not assumed.** `δ` is recomputed from `x_retrain − cv`, never from
  `s + Δ`, and `‖δ‖² = ‖s‖² + ‖Δ‖² + 2 s·Δ` holds to a max relative residual of **5.144e-15**. Had it
  failed, the stored arrays would not be what their names say and the tool reports the failure instead
  of the ratios.
- **It independently reproduces a published number.** Phase 7 recorded `corr(Δ,s) = −0.71` for
  MaRES:+1; this measurement returns cosine **−0.714** and Pearson **−0.711** from the raw arrays.
  Cosine and Pearson are reported separately because the Phase-7 record does not state which it meant,
  and they are not the same number unless both vectors are mean-zero across bins.
- **It agrees with an independent integral-level observation.** The Phase-7 record notes frozen `+1.83%`
  → retrained `+0.89%`, i.e. retraining reabsorbs about half the frozen shift. A joint shift *smaller*
  than the frozen one is what a negative cross term predicts, from a completely different quantity.
- **The tool is power-tested in both directions** on synthetic operands with analytic answers:
  orthogonal → 1.000000, anti-correlated at cos −0.71 → 1.856953 (overstates), positively correlated →
  0.764719 (understates), exact cancellation → `nan` rather than a silent pass. A tool that can only
  return one reading cannot be trusted to have found the middle one.

### 3.3 Two scope limits stated in the key, not the footnotes

- **These are RECOIL products.** Per the 2026-08-01 landing, every pre-08-01 PET number is a **different
  estimator**. No magnitude here is quotable and none transfers to the full-event budget. What transfers
  is the **sign and rough size of the omitted cross term**, as a design input.
- **`flux:55` and `null` are excluded from the headline and labelled in the receipt's own keys.**
  `C_syst`'s flux block is built over 100 PPFX universes, so one flux universe's ‖s‖ is not a term in
  it — and measurably so: `flux:55`'s ‖s‖ = 2.80e-38 alone **exceeds** the published whole-flux block
  √tr of 1.0604e-38. `null` is the identity-retrain training-noise control (`s ≡ 0`). Pooling either
  would assert a summation rule the published assembly does not use. The pooled value is retained in the
  receipt under `all_pooled_DO_NOT_QUOTE` so the superseded number stays visible.

## 4. Therefore: the construction is binding, and the reason is a dependency, not a preference

1. The joint construction requires `x_u^{varied+retrained}` **per endpoint**. For a detector endpoint
   that requires a **regenerated selected cloud** — the note names the historical block's defect as
   propagating *"shifted weights and observables through the nominal cloud membership instead of
   regenerating the selected cloud for every lateral endpoint."* Those regenerated samples are the 120
   P3F ROOTs. **They exist**, so this dependency is satisfied.
2. Nothing in the repo builds the joint object. `phase7_retrain_universe.py` retrains per universe, but
   it produces the **increment** `Δ_u` relative to the frozen map, and its own docstring says
   *"extraction uses the nominal cloud"* — i.e. it is both the additive decomposition and
   CV-support-limited. It also *excludes* laterals by design: *"Laterals/detector universes are
   **excluded from this set** — they need selection-complete shifted point clouds (KNOWN_ISSUES #16),
   which do not exist."* **That exclusion's stated reason expired on 2026-07-20** and no code has been
   revisited since.
3. So the ordering is: samples (done) → joint construction (not started) → covariance assembly →
   budget. The binding half is the construction.

**Cost floor, measured rather than estimated.** The annealed full-event nominal's own checkpoint mtimes
give 08:35 → 11:00 for one 3-iteration 2M-event training arm, i.e. ~2 h 25 m per retrain. Ten lateral
endpoints (5 bands × 2) is therefore a **≥ 24 GPU-h floor for the lateral joint block alone**, excluding
extraction, the vertical bands, and the fresh statistical and ML ensembles the note requires
(`sec_pet.tex:133-134`). Consistent with `docs/OPEN_ITEMS.md`'s *"≥100 GPU-h"* for the whole build; the
"170-250" figure there remains unverified and is not adopted here.

## 5. Acted on while determining: the satisfied half was one purge from unsatisfied

`hsi ls` returned only `~/backups` — **HPSS held no copy**, so 1.1 TB of Gate-3-promoted input was the
sole copy on purgeable scratch. Nine throw slabs of the adopted 5D ensemble have already been lost this
way (`docs/OPEN_ITEMS.md` item (g)), turning the adopted covariance into a 76.2% subsample. Job
**56692312** (`sbatch_hpss_protect_p3f_fullevent.sh`, `qos=xfer`) is archiving the tree with
**digest** verification — local md5 against an md5 computed **server-side** by `hsi hashcreate`, so
content is verified without reading 1.1 TB back. Completion condition is
`n_archived_digest_verified == 240` (120 ROOT + 120 receipt), **not** 120.

## 6. A WRITTEN DISCHARGE CRITERION FOR CAUSE 5 — there was none recorded anywhere

A remediation whose success condition is invented after the fact is not a remediation. Cause 5 is
discharged when **all** of the following hold, each with a recoverable artifact:

1. **Joint shifts, not increments.** For every nuisance endpoint `u` in the quoted budget, a stored
   `δ_u = x_u^{varied+retrained} − x_CV`, formed as one object. A receipt that publishes `s_u` and
   `Δ_u` separately does not satisfy this even if `s_u + Δ_u = δ_u`, because the covariance is what is
   at issue.
2. **No summed frozen+retrain blocks anywhere in the quoted total.** The budget contains no
   `C_syst + C_retrain` pair. Mechanically checkable: assert no assembly sums two blocks whose shift
   definitions differ by the frozen map.
3. **The cross term is reported, not merely absorbed.** For each endpoint, publish `cos(s_u, Δ_u)` and
   the ratio `additive/joint`, so a reader can see what the old construction would have said. The
   present measurement is the pre-repair baseline for exactly this.
4. **Detector endpoints use regenerated selected clouds**, evidenced by consumption of the 120
   Gate-3-promoted P3F ROOTs by digest, not by path.
5. **Full-event estimator throughout.** Every component on one full-event nominal, `estimator_fingerprint
   pet-fullevent-fps-v1`, with a fresh statistical and ML ensemble; no recoil component transferred
   (`docs/OPEN_ITEMS.md` item 6: *"No current recoil-PET covariance component is automatically
   transferable to the new estimator."*)
6. **Power-tested gates.** Each new check demonstrated to fail on purpose, both directions, and said so
   in its commit.

**Explicitly NOT sufficient, because each would pass without touching the cause:** a PSD re-check; a
seed ensemble; an independent re-roll; re-running Phase 7 on more bands; promoting the annealed nominal.
This mirrors §3 of `PROMPTS-20260811-four-session-closeout.md` on the `\gbdtFive*` adoption — no
verification pass opens this gate.

## 7. What this determination does not do

It discharges nothing. Cause 5 remains **OPEN**, six of seven quarantine causes remain open, and no PET
magnitude becomes quotable — including everything measured in §3, which is recoil and therefore a
different estimator. It does not lift Branch C, authorize an extraction, or make the `\gbdtFive*`
adoption actionable. Protecting an input is not building a construction, and measuring a defect's size
is not repairing it.
