# Orchestrator migration handoff — fe-fps campaign

> **ARCHIVAL/INDEX-ONLY (2026-07-19).** This immutable cutover snapshot is not
> live campaign state. Normal turns start from `LIVE-STATE.md`; follow links
> there to canonical science receipts and append-only history.

Snapshot 2026-07-18 02:07 PDT (09:07 UTC). Lossless state for a successor orchestrator.
Companion machine-readable roster: `MIGRATION-WORKERS.json` (same dir).
Ledger head at snapshot: git `3b5945b` on `main` (remote `github`).

---

## 1. Objective

Graduate MINERvA OmniFold from a small observable set to the full available phase space,
AND (as the concurrent publication-completion campaign this orchestrator took over
coordinating) drive the corrected-UQ covariance endpoints to completion. Two things are in
flight tonight:
- **FPS P4 (Agent C):** produce the publishable corrected-FPS covariance with
  selection-complete active laterals (final adopt).
- **Standard P4 (Agent A):** produce the selection-complete standard lateral block — the
  missing input that finalizes the corrected-4D covariance (the R1 candidate).

The headline full-event PET measurement (P5B) is a SEPARATE, later campaign — see §5 Stage 3;
it is NOT what tonight's chains deliver.

## 2. Stopping condition

Tonight's coordination is DONE when BOTH:
- Agent C's FPS chain reaches **final adopt** → `uq_fps/corrected/..._combined_uthrow_activelat.root`
  (PSD-verified, validate-PASS), recorded X5 PASS in RUNS.tsv, committed+pushed.
- Agent A's standard chain reaches **CANDIDATE** (cov→validate; commit gate, no final adoption),
  its selection-complete standard lateral available to finalize corrected-4D.
Then: write the consolidated BEN note (§8) and commit. The broader campaign continues at Stage 3.

## 3. Verified results (as of snapshot)

Committed and independently checked (see CLAIMS.md for evidence rows):
- **CLM-001..005** VERIFIED (P5A engineering + closures reproduced on GPU, job 56003372).
- **CLM-006** VERIFIED-NUMERIC — full-event PET pilot, both arms PASS (Tier-1 per-cell median
  |FE/recoil-only−1| = 4.25% purity / 4.37% ones vs 10% gate; unit-check bit-exact; miss
  neutrality exact). Estimator `pet-fullevent-fps-pilot0`; not a publication result.
- **CLM-007** RESOLVED upstream — Agent B fail-closed data-scalar guard (aa3f44c).
- **CLM-008** CLOSED except F7 — F2/F3 (25d8360, publication logit-space F3, GPU-val 56041808),
  F9/F10 (4043e3f/220c970); F8 mooted by no-Horovod policy. **F7 is the sole open engine gate**
  (coherent global Poisson C_stat draw before subsetting) — blocks any P5B C_stat replica.
- **CLM-009** VERIFIED-NUMERIC — sieve reduction (negweight→purity binned limit), in note App. B.2,
  pushed to Overleaf (analysis-note remote head c02ec6e; later qualification d8bb0aa).
- **R1** PASS — Agent D's 4D-corrected chain repaired by THIS orchestrator (comb4dCc 55971617
  had failed on 15 partial slabs; regen 56025478→combine 56025481→adopt 56025483): 160/160
  throws, null 4.24e-51, adopt PSD OK, √tr ×1.194 (2.099e-38→2.508e-38), median frac 13.47%→14.08%.
  Outputs `uq_4d/corrected/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow{,_cvcentered}.root`.
- **P5B launch gates** adopted (f0f2ad1): no nominal until F2/F3 committed+val (done); no C_stat
  until F7; no Horovod; no publication laterals from reduced-schema P3F sidecars; distinct
  estimator fingerprints (`pet-fullevent-fps-v1` full-schema only / `pet-reduced-fps-cross`).

In-flight tonight (NOT yet complete):
- **X5 (C, FPS P4):** merge 10/10 + audit PASS (gate refined: energy-band zero-migration=WARN in
  FPS). Unfolds: **5/10 validated** (wave-1); wave-2's 5 relaunched on fresh holder 56080370.
- **X-std (A, standard P4):** merges 10/10 validated (setsid-detached redo after truncation),
  audit PASS (GATE1 120/120, GATE2 10/10 all-4-trees). Unfolds: **0/10** (running detached on 56076881).

## 4. Unresolved questions / risks

- **F7** must be implemented before any P5B C_stat replica (coherent global Poisson over full
  inventories before subset selection; persisted factors/seeds; same MC draw at extraction).
- **Corrected-4D finalization:** the R1 candidate uses the SUPPORT-LIMITED sweep lateral. Final
  swap needs Agent A's selection-complete standard lateral (tonight's A output) → a follow-on
  adopt step, owner not yet assigned.
- **P3F schema:** current FPS endpoints are scalar-schema (pre-full-event binary). Publication
  full-event P5B laterals require option-(b) fresh full-schema P3F after the C++ dump (G2) lands
  (Agent B's P5B_LATERAL_SOURCE_DECISION.md).
- **Interactive walls:** both chains ride 4h interactive holders; each wall-kill leaves
  write-at-end unfolds cleanly absent (good) but a wall-kill DURING a hadd leaves full-sized
  truncated files (bad) — completeness validation (not existence) is mandatory on every skip.

## 5. Current plan (stages; canonical detail in ROLLOUT-PLAN.md)

- **Stage 1 (tonight):** finish C's FPS P4 → final adopt; finish A's standard P4 → CANDIDATE.
- **Stage 2:** DONE (CLM-007 upstreamed; CLM-008 closed except F7).
- **Stage 3 (P5B production, later):** gated on G2 (C++ full-event dump) + fresh full-schema P3F
  (option b) + F7. Launch order + gates in ROLLOUT-PLAN.md and FULL_EVENT_FEATURE_CONTRACT.md.
- **Stage 4/5:** negweight full-event arm; Gregor four-way pilot (both optional/gated).

## 6. Role assignments

| role | who | state | scope |
|---|---|---|---|
| Orchestrator | this session (Opus 4.8; was Fable) | active, handing off | coordinate A/B/C, verify, ledger |
| Agent A | school session 14951826 | ACTIVE | standard P3S/P4 only (NOT FPS) — holder 56076881 |
| Agent B | school session 46e4af3e | IDLE (done) | P5B engine; resumes when G2/P3F land |
| Agent C | school session 4580f42d | ACTIVE | FPS P3F/P4-FPS/P6-FPS — holder 56080370 |
| Agent D (4D-corrected) | delegate UUID uncertain — see WORKERS.json | chain COMPLETE (R1) | orchestrator-executed; no active delegate |
| note/Overleaf | school session 748c7f6b | STALE (07-17 05:51) | analysis-note subtree; last act = Overleaf force-push |

Ownership rule (hard): A and C each own ONE interactive node; neither cancels the other's holder;
A=standard only, C=FPS only. C++ binary frozen while active. `uq_4d/corrected/` = orchestrator.

## 7. Important paths, commands, quota

**Alloc assignment (current):** C-FPS on holder **56080370** (nid004149, wall ~12:38 UTC).
A-std on holder **56076881** (nid004178, wall ~09:33 UTC ≈ 02:33 PDT, ~26min left → will re-grab).
2-job interactive cap: one node each.

**Product paths:**
- FPS unfolds: `nd-unfolding/active_universe_5d/fps/unfolds/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<EP>.root` (need 10)
- FPS final adopt target: `nd-unfolding/uq_fps/corrected/...combined_uthrow_activelat.root`
- Standard unfolds: `nd-unfolding/active_universe_5d/standard/unfolds/*.root` (need 10)
- Merged endpoints: `active_universe_5d/{fps,standard}/merged/`
- Ledgers: `docs/orchestration/{CLAIMS.md,RUNS.tsv,ROLLOUT-PLAN.md,FINDINGS.md}`
- Delegate prompts/replies: `MINERvA-OmniFold-fe/orchestration_runs/coordination/{msg_*,reply_*}`

**Delegate dispatch (verified working; NESTED school home is mandatory):**
```
HOME=/global/homes/j/josephrb/claude-homes/school/claude-homes/personal \
  /global/homes/j/josephrb/.local/bin/claude -p --resume <UUID> "<msg>" \
  --model opus --dangerously-skip-permissions
```
**Monitoring:** `squeue -u josephrb`; validate an output before trusting it (open ROOT, check
`hXSecND_flat`/`[CHECK] c=1.0000`). Peek at a node: `srun --overlap --jobid=<J> -w <node> bash -lc 'ps -u josephrb -o etimes,args'`.

**Quota state (snapshot):**
- claude-school (opus): 5h windows from 08:40 PDT → current window **23:40 PDT(07-17)–04:40 PDT(07-18)**;
  hit its cap once ~07:40 PDT earlier today; ~8 pings fired this window; cap ≈42 jobs/window.
  A capped ping fails in ~60s with the reset time in stdout.
- codex / codex-school (gpt-5.6-sol xhigh): headroom; ≈16–20 xhigh jobs/window/account. Not used tonight.
- agy (gemini 3.1 pro): effectively uncapped.
- Orchestrator: Opus 4.8, user relaxed usage concern; delegate heavy lifting to codex/agy by directive.

## 8. Next three recommended actions

1. **Verify the wall transitions** (a fallback wakeup is armed ~02:18 PDT): confirm A crossed its
   09:33 UTC wall onto a fresh holder and resumed its 10 standard unfolds via completeness-validated
   skip; confirm C's 5 FPS wave-2 unfolds are training on 56080370. Harvest `reply_C7.out`/`reply_A6.out`
   (already read at snapshot) and any newer replies.
2. **Close FPS (critical path):** when `fps_unfold_complete.py --all` == 10/10, ensure Agent C runs
   cov→validate→PSD-safe swap→final adopt on 56080370; independently verify PSD (min-eig ≳ −1e-10
   rel), symmetry, validate-PASS; record **X5 PASS** in RUNS.tsv with the covariance fingerprint
   (√trace, median frac/bin, rank, PSD); commit+push.
3. **Close standard + write the BEN note:** when A's 10 unfolds validate, ensure cov→validate→CANDIDATE;
   note the follow-on (swap A's selection-complete standard lateral into the R1 corrected-4D candidate —
   assign an owner). Then write a consolidated FINDINGS.md BEN entry for tonight's four recurring modes
   (interactive-QOS grabbed in seconds vs 6.5h shared backlog; cross-alloc jobid confusion starving a
   co-agent — assign explicit jobid-per-chain + verify by node; setsid-detach drivers or they die at
   session boundaries [extends BEN-024]; wall-kill truncation — validate completeness not existence
   [extends BEN-023]); commit.
