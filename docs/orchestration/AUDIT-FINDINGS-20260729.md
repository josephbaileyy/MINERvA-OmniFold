# Audit findings — MINERvA-OmniFold full-event PET path (2026-07-29)

> **Read with [`AUDIT-FINDINGS-20260728.md`](AUDIT-FINDINGS-20260728.md), not instead of it.**
> That document (B1–B5, M1–M14) is the substantive audit of the estimator, the closures, the
> covariance lineage and the Gate-2/Gate-4 chain, and it stands. This one does not repeat it.
> Where the two touch, this document is the later word:
>
> | This doc | Effect on 07-28 |
> |---|---|
> | **N1** | **Corrects the host-memory addendum** (`:1377-1426`). Its headline ~61 GiB/rank / ~246 GiB-over-4-ranks answers the 40M / 4-rank recoil recipe, not the frozen full-event nominal. The nominal is ~13.4 GiB, single rank. This is the same misattribution M12 diagnoses — do not schedule a loader refactor on it. |
> | **Gate-3 section** | Closes the gap §4 names as *"Gate-3 is a **gap**, not a pass"*. New: G1, G2. |
> | **Units (M1)** | Independently re-confirmed a third way, from `validate_g2_fullevent_domain.py:235-237` + `G2_MEFHC_DOMAIN_VALIDATION.json`. The question is closed offline; `RESTORE-2026-08-03.md` Step 2 needs the dump only for the *re-validation*. |
> | **N5** | Partially **retracted by this document's own Gate-3 section** — the schema half of the provenance claim *is* enforced by composition. N5 is narrower than first written. |
>
> Produced in a read-only session with no cluster access and **no numpy / ROOT / pytest**, so
> nothing in either document was executed here. See "Audit basis and its limits" below —
> particularly what that means for 07-28's "reproduced locally" claims.

## Context

`docs/orchestration/start-audit-planner.md` briefs a cold session to audit the full-event
PET/OmniLearn path before P5A launches, deliverable = prioritized findings, no edits.

**The brief is stale relative to HEAD.** It is dated 2026-07-28 and asks for two open
findings to be "verified or refuted"; both were answered in the very commit that is now
HEAD (`5718449`, `docs/orchestration/AUDIT-FINDINGS-20260728.md`, 1426 lines: B1–B5, M1–M14,
plus a measured host-memory addendum). Re-running that audit would produce nothing.

So this pass does three things instead:

1. **Corrects the most recently written conclusion** (the host-memory addendum), which is
   the one an executor is most likely to act on next and which answers the wrong
   configuration.
2. **Audits Gate-3**, which `AUDIT-FINDINGS-20260728.md` §4 explicitly lists as *"a **gap**,
   not a pass"* — `validate_p3f_pet_fullevent.py`, its launcher, and the promotion evidence
   chain were never read in depth.
3. **Checks the control plane** a fresh session is told to enter through.

### Audit basis and its limits — read before trusting any of this

- Read-only checkout at `5718449`. Nothing edited, nothing submitted.
- `python3 docs/orchestration/verify_hash_bindings.py` → `92 resolved / 88 OK / 4 known
  drift / ALL BINDINGS INTACT`, exit 0. Gate-3's two frozen files re-hashed by hand and
  match the receipt (`validate_p3f_pet_fullevent.py` = `d782a478…`,
  `sbatch_p3f_pet_fullevent_evloop_array.sh` = `7c9018ed…`).
- **This container has no numpy, no sklearn, no pytest, no ROOT.** Every "reproduced
  locally" / "mutation-tested" claim in `AUDIT-FINDINGS-20260728.md` was therefore **not
  re-executed here** and is carried forward on its own authority. My own verification is
  code reading, pure-Python arithmetic over committed receipts, and `sha256sum`/`git`.
- The working tree is **dirty**: `nd-unfolding/pet/sbatch_fe_hostmem_ladder_delta.sh` has 12
  uncommitted lines (comment + label fix). Bindings stayed intact, which independently
  confirms that file is unfrozen — but uncommitted science is not live evidence.

---

## BLOCKS the publication nominal / changes a scheduling decision

### N1. The host-memory addendum's headline answers the 40M / 4-rank recoil recipe, not the frozen full-event nominal. Two independent in-repo measurements put the nominal at **~13.4 GiB, single rank**

*Dimensions: loader resource behaviour (brief dim 7), receipt provenance. Verdict:
CONFIRMED by arithmetic over two committed measurements. Not frozen.*

**Claim.** The addendum (`AUDIT-FINDINGS-20260728.md:1400-1419`) concludes *"The production
case is rows = 49,152,885 (with max_events = 40M): ~61 GiB per rank, ~246 GiB across 4
ranks… about 98% of capacity"* and recommends *"Do not launch P5A at `-np 4`."*

The frozen full-event nominal is neither 40M nor 4-rank:

| | addendum's "production case" | frozen nominal |
|---|---|---|
| max_events | 40,000,000 | **2,000,000** (`sbatch_pet_fullevent_nominal.sh:54`, `train_fullevent_nominal.py:37`, `validate_pet_nominal_gate4.py:56`) |
| ranks | 4 | **1** (`sbatch_pet_fullevent_nominal.sh:6-8` = `--nodes=1 --ntasks=1 --gpus=1`; no `srun`/`mpirun`/`horovodrun` anywhere in the file) |

40M/4-rank is the **recoil-only xps2** recipe. This is the *same* misattribution that the
same document diagnoses at M12 (`:916-923`) — the addendum, written last and appended by the
orchestrating session, re-imported it.

**The two configurations are separable from data already in the repo, and the answer is
~4.5× smaller.** The ladder ties `max_events = 0.8138 × rows` at every rung
(`measure_fullevent_host_memory.py:51-52,108`), so its single slope confounds a rows-term
with a max_events-term. Split them:

- rows-term = the `part_gen` materialization at `fullevent_fps_dataloader.py:521`.
  From `G2_FPS_MEFHC_P12_RECEIPT.json`, `part_gen` is float32 `(49152885, 12, 5)` = **10.987
  GiB** ⇒ `2.2352e-7 GiB/row`. The synthetic fixture carries the same schema
  (`make_synthetic_g2_fullevent.py:117-118`, ncol 3/5) at `--tokens 12`
  (`sbatch_fe_hostmem_ladder_delta.sh:55`), so the term is comparable.
- ladder slope (refit from the five published rungs: `1.2380e-6`, matching the printed
  `1.238e-6 * rows + 0.239`) minus the rows-term, divided by 0.8138
  ⇒ **`1.2467e-6 GiB` (1339 B) per selected event.**

Validate that two-term model against a **completely independent real-data measurement**:
`G2_GATE2_TARGET_RUNTIME_RECEIPT.json` records `environment.max_rss_kib = 11,632,724`
(= 11.09 GiB) for a `build_fullevent_loaders` run on the real 49,152,885-row dump at
`max_mc_events = 200,000`.

- model predicts `0.240 + 49.15e6×2.2352e-7 + 200000×1.2467e-6` = **11.48 GiB**
- measured **11.09 GiB** → **agreement to 3.4%**

Apply it to the frozen nominal (rows = 49,152,885, max_events = 2,000,000, one rank):

- from the model: **13.7 GiB**
- anchored on the measured 11.09 GiB instead of the fitted rows-term:
  `11.09 + (2.0e6 − 0.2e6) × 1.2467e-6` = **13.3 GiB**

**Failure scenario.** The addendum is the newest text in the file and ends with an explicit
recommendation. On 08-03 the executor reads *"~2-3% of the ceiling, do not launch at -np 4"*
and schedules the loader refactor it names (shard-before-build / chunked construction /
a memmap builder that does not exist). That refactor touches
`fullevent_fps_dataloader.py`, which is bound by `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`
jointly with `gate2_target_runtime.py` — so it costs a **two-file Gate-2 re-issue plus a
Gate-2 canonical-runtime re-run on the 9.9 GB dump**, consuming the restore window, to solve
a problem the publication nominal does not have. Meanwhile B4 (the unimportable
Stay-Positive refiner) — which *does* stop Step 3 of `RESTORE-2026-08-03.md` dead — is not
what the addendum points at.

**Confidence: high** for the nominal (~13-14 GiB, two anchors, 3.4% agreement).
**Deliberately not claimed:** that a 4-rank 40M run is safe. If anything ever runs that
configuration the addendum's ~246 GiB lower bound and its two caveats (CPU node excludes
CUDA/TF host pinning; `sacct MaxRSS` undersampled by 1.7×) stand unchallenged.

**Minimal check** (zero cost, no cluster). Re-run the ladder script's own reporting block
with `--max-events 2000000 --rows 49152885` decoupled — or simply add one rung at
`RUNGS="49152885"` with `--max-events 2000000`. `measure_fullevent_host_memory.py` accepts
`--max-events` (`:108`) and is **not frozen** (`f308c1ec…`, absent from all 92 bindings and
from every receipt). One CPU rung settles it directly instead of by extrapolation.

**Frozen: no.** Both ladder files are unfrozen; correcting the addendum is a doc edit.

---

### N2. Gate-3 dropped the migration-census non-degeneracy check that the scalar path enforces — an all-zero census PASSes, and the "downstream" check it was deferred to does not exist for the full-event path

*Dimensions: fail-closed guards (brief dim 8), receipt provenance (dim 9), covariance (dim
4). Verdict: CONFIRMED by reading both validators side by side. **Frozen — Gate-3 re-issue.***

**Claim.** `validate_p3f_pet_fullevent.py:161-169` is the whole census gate:

```python
def check_migration_census(observed):
    """The four signed migration-census TParameters must EXIST and be integral & non-negative."""
    for name in MIGRATION_CENSUS_PARAMS:
        present = name in observed and observed[name] is not None
        ok = present and _is_integral_nonneg(observed[name])
```

Presence, integrality, non-negativity. **`{0, 0, 0, 0}` passes.**

The repo's own scalar/5D interface validator enforces exactly the missing condition —
`nd-unfolding/active_universe_5d/interface_smoke/p2_validate.py:75-77`:

```python
if mode == "endpoint":
    # CV comparison run; for a lateral band at least one migration direction is nonzero
    total_mig = sum(abs(x) for x in (te, tx, re_, rx) if x is not None)
    check(total_mig > 0, "lateral endpoint shows nonzero selection migration vs CV")
```

So this is a **regression against an established in-repo convention**, not an unconsidered
gap. Every other layer is equally weak or weaker:

- launcher `sbatch_p3f_pet_fullevent_evloop_array.sh:280-283` — `int(value)!=value or value<0` only;
- `_audit_gate3_source.py` (the orchestrator's 120/120 audit) — never reads the census;
- `p3s_manifest_summary.py:434` computes `agg["migration_abs_total"]` and **never gates on it**;
- `audit_merged_fps.py:117` states the policy explicitly — zero migration is *"only a WARNING
  (the real applied-check is the nonzero shift + nonzero covariance are verified
  downstream)"*.

That deferral is the load-bearing part. The downstream verifier it names
(`p4_validate_active_lateral_fps.py:13-14`, *"per-band nonzero trace"*) is on the **5D/scalar
covariance path**. `AUDIT-FINDINGS-20260728.md:1221-1223` establishes independently that
**no full-event covariance builder exists anywhere in this repository**. So for the
full-event lateral endpoints the check was deferred to a consumer that has never been
written.

**Failure scenario.** One of the five lateral bands is enabled but its shift produces no
selection migration — the shift magnitude resolves to zero, or it is applied to a variable
the FPS selection does not use, or an index silently clamps. `hasActiveUniverse=1` and
`activeUniverseIsLateral=1` are still written (they record that the *mechanism* engaged, not
that it *moved* anything), `activeUniverseBand` echoes the requested env string, and all
four counters are 0 — integral and non-negative. Gate-3 PASSes for all 24 files of that band
and the promotion receipt records `all_120_terminal_accounting: true`. When P5B eventually
builds the lateral budget, endpoint − CV is identically zero, that band contributes exactly
zero covariance, and the published systematic budget is short one of five lateral bands.
**This fails in the dangerous direction: an under-estimated uncertainty is invisible
downstream, because a zero band and a small band look the same.**

**Confidence: high** that the gate cannot detect this. **Unknown** whether it actually
happened — the census values were read and written into all 120 per-task receipts
(`validate_p3f_pet_fullevent.py:296` `observed_census`) but are **not** in any committed
artifact: `p3f-pet-gate3-source-manifest-56169838.json`'s 120 task rows carry only
verdict/hashes/sizes, and `grep activeUniverseTruthEntrants` over `docs/orchestration/state/`
and `nd-unfolding/g2_fullevent/` returns nothing.

**Minimal check** (seconds of I/O, needs `/pscratch`, no compute, decides the question
outright):

```bash
python3 - <<'PY'
import glob, json
for p in sorted(glob.glob("/pscratch/sd/j/josephrb/MINERvA-OmniFold/"
                          "nd-unfolding/p3f_pet_fullevent/final/P3F_PET_receipt_*.json")):
    c = json.load(open(p)).get("observed_census", {})
    tot = sum(abs(v or 0) for v in c.values())
    print(f"{'ZERO ' if tot == 0 else '     '}{p.split('receipt_')[1][:-5]:28s} {tot:>12}  {c}")
PY
```

Expect 120 rows, every `tot > 0`. Any zero row names a band/endpoint/playlist whose lateral
shift did nothing. Run this **before** anything consumes the endpoints — it costs nothing and
retires the finding either way.

**Frozen: yes.** `validate_p3f_pet_fullevent.py` is bound by
`docs/orchestration/state/p3f-pet-gate3-launch-code-gate-20260720.json` (`files.validator`
`d782a478…`), which also binds the launcher, both tests, and the domain/base validator
hashes. Adding `total_mig > 0` is a **Gate-3 launch-code-gate re-issue**. Its tests are
login-safe (146/146 + 29/29 per the receipt), so the re-run is cheap — but note it does not
by itself re-certify the 120 existing ROOTs, which is why the receipt sweep above is the
first move and the code change is the second.

---

## Should fix eventually

### N3. Gate-3's 120 endpoint ROOTs are bound by size after validation, never re-hashed by anyone

*Dimension: receipt provenance (dim 9). Verdict: CONFIRMED — self-reported in the manifest.*

`p3f-pet-gate3-source-manifest-56169838.json` says so in its own `integrity_note`:

> *"final ROOT integrity verified by existence + size_bytes match against the
> receipt-recorded sha256 produced in-job at validation time; per-file 9.4GB x120 rehash not
> performed in-turn."*

`_audit_gate3_source.py:141-148` bears this out — it compares `os.path.getsize(root_p)`
against `recorded_size` and cross-checks that two *fields inside the receipt* agree, but
never recomputes the ROOT hash. The independent verifier's item 5
(`p3f-pet-gate3-promotion-56169838.json`) is `"outputs_sizes_locks_done_markers"` — also
sizes. So the sha256 in each receipt is bound to what the in-job validator saw at
`validate_p3f_pet_fullevent.py:424`, and **nothing since has confirmed the file on disk still
matches it.** 120 × 9.4 GB ≈ 1.1 TB on purgeable `/pscratch`, unverified for 8+ days across
a maintenance window.

**Failure scenario.** Post-purge or post-truncation, an endpoint ROOT of the right size but
wrong content feeds P5B. Size-only equality is exactly the check a truncation-to-block-
boundary or a partially rewritten file can survive; a full-file hash is exactly the check it
cannot.

**Confidence: high** on the gap, **low** on it having bitten. This is defensible triage (1.1
TB of hashing is not free) — the finding is that `validated_final_root_receipt_pairs: true`
in the promotion receipt reads stronger than what was done, and the omission is recorded
only in a nested `integrity_note`.

**Minimal check** (post-restore, batch not login, ~1.1 TB of reads — schedule it, do not
inline it): `sha256sum` each of the 120 ROOTs against its receipt's `final_root.sha256`.
Cheaper partial: hash the first and last 64 MiB of each, which catches truncation and
tail-rewrite for ~1.5% of the I/O. **Frozen: no** — a new unbound audit script.

---

### N4. `LIVE-STATE.md`, the declared control-plane entrypoint, is 8 days and ~10 commits stale and declares a state that predates every known P5A blocker

*Dimension: code/process integrity. Verdict: CONFIRMED. Generated file — regenerate, do not
hand-edit.*

`docs/orchestration/LIVE-STATE.md:5-9` — `Observed: 2026-07-21T20:05:25Z`, `Git: ada72b0`.
HEAD is `5718449`. Its `Declared state` line ends *"Pre-shutdown checklist PASS; ready for
2026-07-22 -> 2026-08-03 maintenance"* and its DAG node reads *"Gate 4 launch-code gate
PASS_CODE_ONLY; training launch deferred post-restore."*

Everything that has happened since is absent: `RESTORE-2026-08-03.md`, the dead-P5A-closure
diagnosis, the synthetic-fixture power caveat, the host-memory ladder, and the entire
B1–B5/M1–M14 findings set. The file's own header calls it *"the normal-turn control-plane
entrypoint"* and `start-audit-planner.md:110` lists it first under "Where the truth lives".

**Failure scenario.** The next cold session enters through LIVE-STATE as instructed, reads
"ready", and proceeds toward the P5A launch without seeing that the extraction path has no
working end (B3), the refiner is unimportable (B4), or Gate-4 evaluates none of its four
physics checks (B2). This is not hypothetical — the brief I was handed exhibits the same
staleness, asking for two findings that HEAD already answers.

**Minimal check / fix** (zero cost, now): `python3 docs/orchestration/generate_live_state.py`
and commit the result. Then reconcile whether the generator draws from anything that would
surface the audit findings; if not, the "Declared state" line needs a source that does.
**Frozen: no** (generator and output both unbound).

---

### N5. The Gate-3 validator's docstring asserts a binary/env provenance requirement the validator does not enforce

*Dimension: receipt provenance. Verdict: CONFIRMED by grep. Frozen (Gate-3), low severity.*

`validate_p3f_pet_fullevent.py:4-8` opens: *"Each endpoint ROOT must be produced by the
canonical installed binary (SHA-256 61d7dfbf…, built from 486e53e) under the runtime
combination `MNV101_ACTIVE_UNIVERSE=BAND:IDX` + `MNV101_DUMP_POINTCLOUD=1` +
`MNV101_FULL_PHASE_SPACE=1`. The older MD5-e63c scalar ROOTs are CONTROLS only…"*

`grep -n "61d7dfbf\|MNV101_" validate_p3f_pet_fullevent.py` returns **only those docstring
lines**. Neither the binary hash nor the env combination is checked anywhere in the module.
Both *are* enforced — by `sbatch_p3f_pet_fullevent_evloop_array.sh:163` (`binary drift`) and
`:246-249` (env identity + binary hash), and by Gate-1's
`validate_g2_gate1_pairs.py:22,115-116`. The exposure is narrow but real: the docstring's own
`Usage:` block (`:44-47`) documents standalone invocation, and a standalone run emits a
`p3f-pet-fullevent-validation-v1` receipt with `verdict: PASS` carrying **no binary, source,
or env binding at all** — only `this_validator`/`domain_validator` hashes and the ROOT's own
hash. A reader of that receipt would reasonably conclude the docstring's requirements were
checked.

Practically mitigated: a scalar MD5-e63c ROOT fails `petSchemaVersion` in the composed base
validator (`validate_g2_fullevent_smoke.py:96`), and a CV ROOT fails
`active:hasActiveUniverse==1`.

**Minimal check / fix.** Either bind the launcher-recorded provenance into the validator's
report (Gate-3 re-issue), or — cheaper and unfrozen — amend the docstring to say the binary
and env bindings are enforced by the launcher, and mark standalone invocation as
provenance-unbound.

---

### N6. `check_active_metadata` coerces two markers with a bare `int()` and crashes on a string, while the third is guarded

`validate_p3f_pet_fullevent.py:153-156` does `en is not None and int(en) == 1` and
`lat is not None and int(lat) == 1`, while the index check one line above uses the
`_is_integral_nonneg(oi)` guard. `read_active_markers:351-354` falls back to
`p.GetTitle()` on `AttributeError`, so a TNamed (rather than TParameter) named
`hasActiveUniverse` yields a string and `int("cv")` raises `ValueError` uncaught — the
validator dies with a traceback and no receipt, instead of writing a FAIL receipt.
Fail-closed by crash rather than by verdict, and the asymmetry with the index check is
almost certainly unintentional. **Fix:** reuse `_is_integral_nonneg` for both. Frozen —
fold into the N2 Gate-3 re-issue rather than paying for a separate one.

### N7. `freeze:bin_order` is a string with no referent (extends B2)

`validate_pet_nominal_gate4.py:54` freezes `"pt-major row-major: cell = i_pt *
n_pparallel_bins + i_pparallel"`, which is consistent with `fps_provenance.py:31-32`
(`NBINS_EXT = NPT*NPZ`, `RAVEL_ORDER = "C"`). So the convention itself is coherent — the
brief's dimension-5 concern about ravel order does **not** reproduce as a live mismatch.
But per B2 the check at `:140-141` compares `FROZEN` to `FROZEN`, and per B3 no full-event
extractor exists, so nothing in the publication path actually ravels using this convention.
The freeze is a well-formed string that currently binds no code. It becomes real the moment
the full-event extractor is written — pin it against `fps_provenance.RAVEL_ORDER` then.

### N8. The 266/285 reported mask for a PET publication is defined by a GBDT central value

`fps_reported_mask.py:48,63-67` builds the mask as `cv > 0` from `hXSecND_flat` in
`fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` — an **LGBM** central value. So which cells
the PET double-differential result reports is fixed by where a *different estimator's*
central value was positive. The fingerprint lock itself is sound (12 candidate
serializations, one matching a pre-declared sha256 — a 256-bit match over the real mask is
identity evidence, not curve-fitting). The finding is the cross-estimator dependency, which
should be stated as a deliberate convention in `sec_method` rather than left implicit —
and it connects to the prior audit's open question of whether the LGBM `CV>0` 266 is the
same set as the truth-MC-occupancy 266 in the floor study. Not frozen; documentation.

---

## Prior-audit claims I independently re-confirmed

Spot-checks only, chosen because the recommendations lean hardest on them:

- **B1 mechanism** — `normalize=True` on **both** full-event loaders confirmed at
  `fullevent_fps_dataloader.py:613` (MC) and `:658` (negweight-refined measured), plus
  `:621` on the purity control. Read directly.
- **M12 leg 2** — nominal is single-rank: `sbatch_pet_fullevent_nominal.sh:6-8`, no
  `srun`/`mpirun`/`horovodrun` in the file. `TRAIN_EVENTS=2000000` at `:54`. Read directly.
- **Known finding A (tokens)** — real dump is 12 slots: `part_gen (49152885, 12, 5)`,
  `part_reco (49152885, 12, 3)` from `G2_FPS_MEFHC_P12_RECEIPT.json`. Ladder correctly
  overrides `TOKENS=12` (`sbatch_fe_hostmem_ladder_delta.sh:55`). Confirmed.
- **Gate-3 freeze intact** — both frozen Gate-3 files re-hashed by hand against
  `p3f-pet-gate3-launch-code-gate-20260720.json`; exact match.
- **Frozen-file discipline holds** — `verify_hash_bindings.py` exit 0, `ALL BINDINGS
  INTACT`, the same 4 documented drifts. No new drift since `5a22e1c`.

---

## Gate-3 completion (added after the initial pass)

The first pass left Gate-3 *partly* audited: I had read `validate_p3f_pet_fullevent.py` and the
promotion chain, but the two validators it composes were only grepped. Both are now read in
full. Net result: **the composition logic is sound and I found no way to route around it — but
the supersession that justifies the whole design was applied to 2 of ~9 head-sampled checks,
and the remaining 7 include the one invariant the point-cloud dumper depends on.**

### What I verified holds (state this, so the gap below is not read as "Gate-3 is broken")

`validate_g2_fullevent_domain.py` fails closed on every route I could construct:

- `--no-structural` omits the `structural` block ⇒ Gate-3's `domain:base_ran` and
  `domain:base_result_bound` (`validate_p3f_pet_fullevent.py:216,227-229`) both FAIL. Gate-3
  never passes that flag anyway (`:366-368`).
- Base validator crashes or writes an unreadable receipt ⇒ `n_checks`/`n_failed` stay `None`
  ⇒ `domain:base_result_bound` FAILS, even though the domain validator itself would not have
  flagged it (`validate_g2_fullevent_domain.py:308-313` checks `ran`/`error`/
  `non_superseded_failures`, never `exit == 0`). Gate-3 catches what the domain layer misses.
- Out-of-domain census truncation at the `cap=100000` limit is explicitly fatal (`:270-273`),
  and Gate-3 re-derives completeness independently (`check_domain_census_complete:172-194`).
  Headroom on the real merged dump is large — the largest context is `signal_reco_pass` at
  16,683 out-of-domain rows, 21,797 total.
- The schema markers **are** structurally enforced. `petSchemaVersion == "g2-fullevent-v1"`,
  `hasFullEventSchema`, `fullPhaseSpace` (`validate_g2_fullevent_smoke.py:96-101`) are ordinary
  base checks outside `SUPERSEDED_BASE_CHECKS`, so a failure propagates to
  `non_superseded_failures` → domain FATAL → Gate-3 FAIL. **This partially retracts N5:** the
  docstring's "MD5-e63c scalar ROOTs are CONTROLS only" half *is* enforced by composition. Only
  the binary-sha/env half is unenforced by the validator, and the launcher covers that. N5
  should be read as narrower than I first wrote it.
- The `invalid_muon_or_minos` design is correct and non-trivially exercised: 24/62/191 corrupt-
  but-finite muon rows on the real dump, none in-domain, hence censused and not fatal
  (`:254-263`) — the playlist-1D behaviour working as intended.

**Independent third confirmation of prior-audit M1 (the Gate-2 units question).**
`validate_g2_fullevent_domain.py:235-237` asserts, for every in-domain row,
`|sqrt(px²+py²)/1000 − pt| ≤ 1e-6·max(1,|pt|)` — i.e. the muon four-vector is MeV and **the
scalar is GeV**. `G2_MEFHC_DOMAIN_VALIDATION.json` records `in_domain_scalar_muon_mismatch = 0`
for all three reco contexts on the real merged inventory. Combined with the two lines M1
already cites, the units question is now settled from three independent directions without the
dump: `gate2_target_runtime.py:421-422`'s `/1000.0` is wrong. `RESTORE-2026-08-03.md` Step 2
can stop treating this as an open empirical question and go straight to the re-issue.

---

### G1. The exhaustive supersession covers 2 of ~9 head-sampled base checks. Cloud-token length equality — the invariant the dumper assumes and does not assert — is verified on the first 0.040% of the signal tree

*Dimensions: fail-closed guards (dim 8), test/gate power (dim 10), truth-reco leakage (dim 6).
Verdict: CONFIRMED, with measured coverage. **Frozen — Gate-3 re-issue** (or a new unbound
script to answer it retroactively).*

**Claim.** The entire domain-validator design rests on one argument, stated in its own docstring
(`:6-11`): the base validator samples 20,000 rows, playlist 1D proved a single corrupt row can
hide beyond that sample, therefore replace the sampled checks with exhaustive `TTree::Draw`
scans. `SUPERSEDED_BASE_CHECKS = {"bkg_reco_muon_valid", "data_reco_muon_valid"}` (`:46`).

That reasoning applies verbatim to seven other checks in the same file, on the same trees, with
the same 20,000-row head slice — and none of them were superseded. Measured coverage, from
`G2_MEFHC_DOMAIN_VALIDATION.json.base.json` on the real merged dump:

| base check | rows scanned | tree size | coverage |
|---|---|---|---|
| `sig_cloud_lengths_equal` | 20,000 | 49,906,108 | **0.040%** |
| `data_cloud_lengths_equal` | 20,000 | 4,119,797 | 0.485% |
| `bkg_cloud_lengths_equal` | 20,000 | 566,036 | 3.53% |
| `miss_reco_vectors_empty` (+3 siblings) | 5,000 | 20,361,799 misses | **0.025%** |
| `data_ev_id_populated` | 5,000 | 4,119,797 | 0.121% |

And it is not a random sample — `cloud_len_ok:152-153` is `for i, ev in enumerate(tree): if i >=
n_scan: break`, i.e. the **first** N rows in tree order. The domain validator's exhaustive scans
(`:203-302`) cover scalars, muon four-vectors, MINOS quality, sentinel discipline and miss
scalars. **They never touch cloud vector lengths.**

**Why this one matters more than the others.** `dump_pointcloud_inputs.py:_pad_tokens:90-99`
*assumes* the invariant in its docstring — *"cols: list of equal-length per-feature sequences"* —
and never asserts it. Two distinct outcomes:

- **Loud:** ragged columns reach `np.array([list(c) for c in cols], np.float32)` (`:99`), which
  under numpy ≥1.24 (Delta NGC ships 1.24.4; Perlmutter TF 2.15 is higher) raises
  `ValueError: setting an array element with a sequence … inhomogeneous shape`. The G2 producer
  dies partway through a multi-hour dump with a bare numpy traceback and no provenance.
- **Silent:** `n = len(cols[0])` reads the length from `part_reco_E` **alone** (`:95`), and
  `if n == 0: return out` (`:97-98`) short-circuits **before** the ragged array is ever built.
  So a `pass_reco` row with an empty `part_reco_E` but a populated `part_reco_view`/`_time`
  returns an all-zero cloud with no error — an event that enters step-1 training with an empty
  point cloud, indistinguishable from a genuine miss, and no check anywhere reports it.

**Failure scenario.** One `mc_signal_reco` row past index 20,000 — out of 49.9 million — has
`len(part_reco_E) != len(part_reco_view)`. Gate-3 PASSes it; the domain receipt records a
complete exhaustive census that does not cover the defect; the promotion receipt records
120/120. The G2 dump then either aborts mid-production (loud branch) or ships one silently
empty cloud into training (silent branch). This is the *same shape* as the failure the domain
validator was created to catch, one branch over.

**Honest de-escalation on the leakage half.** `miss_reco_vectors_empty` at 0.025% looked like a
truth/reco leakage channel — a native miss carrying a reco cloud. It is not, because the dumper
is independently fail-safe: `_reco_row:274-281` reads the cloud **only** `if pass_reco`, and
`reco_scalar_row:151`, `reco_muon_row:158`, `reco_vertex_row:165` all return sentinels for
`!pass_reco`. A miss's branch contents are structurally unreachable. So this is dump-contract
hygiene, not leakage — the defense-in-depth genuinely works here. The cloud-length finding
above stands on its own and does not depend on it.

**Minimal check** (one exhaustive pass per tree, C++ speed, no new gate — write it as a **new
unbound script** so the 120 existing ROOTs can be answered without a Gate-3 re-issue):

```python
cut = ("@part_reco_E.size()!=@part_reco_pos.size()"
       "||@part_reco_E.size()!=@part_reco_z.size()"
       "||@part_reco_E.size()!=@part_reco_view.size()"
       "||@part_reco_E.size()!=@part_reco_time.size()")
for tname in ("mc_signal_reco", "mc_background", "data"):
    n = f.Get(tname).Draw(">>__el", cut, "goff")   # expect 0
```

Run it on the merged G2 dump first (that is the one the publication input was built from), then
across the 120 Gate-3 endpoints. **Confidence: high** that the coverage gap is real;
**unknown** whether any violating row exists — the invariant has never been checked past row
20,000 anywhere.

**Frozen: yes** for the fix (`validate_g2_fullevent_domain.py` is bound as
`domain_validator_sha256: 32634d68…` in `p3f-pet-gate3-launch-code-gate-20260720.json`). Adding
the scan to that file is a Gate-3 re-issue — fold it into the same re-issue as N2 and N6 rather
than paying three times. Answering the question retroactively costs nothing.

### G2. `cluster_view_populated` / `cluster_time_populated` assert only that one nonzero value exists anywhere

`validate_g2_fullevent_smoke.py:186-194` breaks out of the loop the instant
`seen_view_vals and seen_time_vals` are both set — so the check is satisfied by a **single**
nonzero entry in the first data row scanned. If `runEventLoopOmniFold` wrote view/time correctly
for early rows and zeros thereafter, both checks pass. The receipt reports them with an empty
`detail` string, so nothing downstream can even tell how many rows contributed.

This is the concrete instance of the prior audit's observation that no gate binds cloud
*content* (only ROOT branch names): the two checks whose names read like content validation are
existence-of-one-nonzero. Cheap fix in the same re-issue — report the *fraction* of scanned rows
with populated view/time and require it above a predeclared floor. Low severity on its own;
listed because these two are easy to mistake for coverage that exists.

---

## NOT ASSESSED — this is not a clean bill of health

**Beyond the prior audit's own §4 list, which stands unchanged, add:**

- **Nothing was executed that needs numpy, sklearn, ROOT or pytest** — none are installed in
  this container. In particular the prior audit's mutation matrix, its
  Perlmutter-equivalent 339-passed baseline, its Gate-4 "PASS on pure noise" reproduction,
  and its `refine_signed_measured` acceptance measurements were **not** re-verified. They
  are carried forward on the prior session's word.
- **The 120 Gate-3 endpoint receipts were never read** — they are on `/pscratch`, not in the
  repo. N2's severity is therefore "the gate cannot detect this", not "this happened".
  The check that decides it is written out above and costs seconds.
- ~~The composed domain and smoke validators were grepped, not read.~~ **Closed** — both read
  in full; see the Gate-3 completion section (G1, G2, and the verified fail-closed routes).
  What remains open on Gate-3: the ROOT-backed paths were never *executed* (no PyROOT here),
  so `_draw_indices`' entry-list handling (`validate_g2_fullevent_domain.py:95-106`, which
  re-`Get`s `__el` from `gDirectory` on every cut) is read-verified only. If two cuts ever
  returned the same stale list the censuses would silently describe the wrong rows; `>>__el`
  should replace rather than append, but that was not observed.
- **`test_p3f_pet_fullevent_validator.py` (375 lines) was read only around its census
  assertions.** Its coverage of `check_domain_result` and `build_report` was not audited, so
  G1/G2 are findings about the validators, not about their test suite's power.
- **`test_p3f_pet_fullevent_launcher.py` (320 lines) remains uncollected** here
  (`conftest.py` `collect_ignore` while the frozen `#SBATCH` target is absent) and
  unaudited, as in the prior pass.
- **N1 is arithmetic, not a measurement.** The two-term model reproduces an independent
  real-data anchor to 3.4%, but the frozen (49.15M rows, 2M max_events) point itself has
  never been run. The one-rung check named above closes it for a few CPU-minutes.
- **`p3s_manifest_summary.py` and `audit_merged_fps.py`** were read only around their census
  handling; their broader verdict logic was not audited.

---

## Suggested order of work (deltas to the existing plan only)

The prior audit's §5 ordering is sound and I am not restating it. Three insertions:

1. **Before anything else on 08-03: run the 120-receipt census sweep (N2).** Seconds of I/O,
   no compute, and it either retires the finding or names a broken lateral band before P5B
   is scoped around it.
2. **Correct the addendum's headline and re-scope the loader-refactor line of work (N1)**
   — now, off-cluster. If ~13.4 GiB is right, the refactor and the Gate-2 re-issue it would
   cost come off the restore window entirely. One decoupled ladder rung confirms it on CPU.
3. **Regenerate `LIVE-STATE.md` (N4)** before the next cold session enters through it, and
   fold N2/N6 into a single Gate-3 launch-code-gate re-issue (login-safe tests, no data, no
   GPU — so it can be run before 08-03, like the Gate-4 re-issue in the prior plan).

**Standing constraints observed:** no file edited, no receipt or `RUNS.tsv` touched, no
sha256 hand-edited, no job submitted, no de-rooting of the load-bearing `/pscratch`
literals.
