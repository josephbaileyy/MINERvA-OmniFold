# Agent A handoff — #16 standard active-universe chain (P0/P2/P3S/P4)

Live as of 2026-07-15. Owner: Publication Agent A (integration lead). This is a
working handoff, not a results claim. Verified numbers belong in the ledger; this
file points to state and the completion recipe.

## OWNERSHIP CORRECTION (2026-07-17, fe-fps orchestrator, user-authorized)
- **FPS post-processing is Agent C's, NOT Agent A's.** The P4-FPS chain
  (audit/merge/unfold/lateral-covariance/adopt under `active_universe_5d/fps/`
  and `uq_fps/`) is owned and run ONCE by Agent C. Agent A's earlier plan to
  auto-run the FPS P4 chain at FPS 120/120 is **STRUCK/DISABLED**.
- **Agent A post-processing scope = STANDARD ONLY:** the P3S -> standard P4
  chain under `active_universe_5d/standard/` when it reaches 120/120.
- Agent A still MONITORS both arrays (babysitting is correct) and owns the
  STANDARD array's health (throttle, scheduler-override resubmit-if-walled per
  the freeze exception). Agent A does NOT run FPS P4, does NOT touch C's FPS
  launcher, and does NOT resubmit the FPS array.
- Do not modify/reinstall the C++ binary while either array is active.
- Not Agent A's scope: 4D corrected combine repair (orchestrator owns
  56025478/56025481/56025483; do not resubmit anything in `uq_4d/corrected/`).
- FUTURE (post-drain, coordinate w/ Agent B): current P3F ROOTs are scalar-FPS
  schema from the pre-full-event binary; full-event C++ branch work (muon
  four-vector, vertex, view, timing, residual-energy) precedes any endpoint
  regeneration decision — not to be actioned unilaterally.

## Completed + committed
- **P0 (reconciliation):** committed only Agent A's own interface; left all other
  concurrent-session dirty files untouched (07-13 corrected-UQ/negweight batch,
  the live 07-15 `OPEN_ITEMS.md`/`ND_OMNIFOLD_STATUS.md` doc edits, Agent D's
  `tests/test_uq_remediation.py`). Ownership inventory in the job tmp.
- **P2 (#16 interface validation): DONE, committed+pushed `2e8c214`.** Rebuilt +
  installed `runEventLoopOmniFold` from current source
  (md5 `e63c74961d699313ef155065fc790ff1`, 383448 B, 9 ACTIVE_UNIVERSE strings).
  All gates pass on the 1A smoke: 20/20 unit tests; invalid band/index fail
  closed; CV smoke zero census; `BeamAngleX:0` endpoint isLateral=1, reco
  migration entrants/exits 21/21 (truth 0/0); completeness 1.000000; native
  misses rebuilt; point-cloud branches complete on all 4 trees under
  `MNV101_DUMP_POINTCLOUD=1` (incl. new background `part_reco_*`); FPS distinct
  (×1.52). Record: `active_universe_5d/INTERFACE_VALIDATION.md` + `interface_smoke/`.

## In progress  (live state 2026-07-16 ~01:00 UTC)
- **P3S (standard active event loops, 5 bands × 2 endpoints × 12 playlists = 120):
  43/120 done** (see `active_universe_5d/standard/<BAND>_<EP>/`; remaining are the
  LARGE playlists — Muon_Energy_MINOS 0/12, MINERvA 3/0, and the big playlists in
  every band). **Active path: CPU batch `55972349`** (shared QOS, `-c 2 --mem 16G`,
  5 h wall, `%12`, skip-if-exists, unique `_b<jobid>` workdirs) — PENDING,
  backfilling.
- **Two diagnosed constraints:**
  1. **Global /pscratch (Lustre) contention** — four sessions do heavy I/O
     concurrently; each output is ~6.7 GB (point clouds for P5). Per-loop rate is
     ~30 MB/min *regardless of my concurrency* (measured identical at MAX=12 and
     MAX=40) → ~3.7 h/loop. So an **interactive 4 h wall wall-kills the large
     playlists** (loop ≈ wall); interactive only ever completed small playlists
     (43 total over several walls). **Do NOT use interactive for the remainder —
     use a batch job whose wall (5–6 h) exceeds the loop time.**
  2. **Fairshare priority starvation** (0.088), NOT balance — balance is fine
     (~4844 node-hours; `overrun` QOS is *rejected* because balance is too high).
     The batch's start estimate reads "now" but higher-priority jobs keep taking
     the slots. It will backfill as B/C/D drain and fairshare recovers. Shrinking
     the task footprint (done: `-c 2 --mem 16G` bills ~8 cores) improves gap-fit.
- Loops are progressing (state D, I/O-wait), NOT broken. Fully resumable.

## Freeze exception — standard array re-tune (user-authorized 2026-07-16)
Narrowly-scoped exception to the launcher freeze, authorized after the 5h wall was
CONFIRMED wall-killing large-playlist loops under 4-agent Lustre saturation (~2-3
MB/min/loop; 0 standard completions in 60 min; FPS's ~12h wall kept trickling).
- **Cancelled:** standard array `55972349` (defective config: 5h wall + %12).
  Reason: 5h wall < per-loop time under saturation → repeated wall-kills.
- **New:** standard array `55985231`, via SCHEDULER OVERRIDES only
  (`sbatch --time=12:00:00 --array=0-119%2` on the UNCHANGED committed launcher).
  Verified live: `TimeLimit=12:00:00`, `ArrayTaskThrottle=2`.
- **Binary/physics-args/launcher CONTENT unchanged** (launcher clean vs HEAD;
  binary md5 `e63c749…`). FPS array `55972324` + Agent C's launcher untouched.
- **Reused outputs:** exactly the 43 standard endpoints that PASS the full
  acceptance validator (manifest `active_universe_5d/standard/p3s_standard_manifest.json`);
  57 dead standard workdirs (partials) quarantined/removed so skip-if-exists
  matches only complete FINAL outputs (FINAL paths verified: 43 files, 0 zero-byte).
- **Ramp rule:** start %2; bump to %4 (scontrol ArrayTaskThrottle) ONLY after two
  large-playlist tasks project runtime <10 h. If %2 still projects >12 h wall,
  STOP launching further standard tasks and reassess (no repeat wall-kills).
- **To report:** throughput + ETA after the first large-playlist completion.

## Remaining dependencies
- P3S must reach 120/120 before P4. P4 (this agent) and P5 (Agent B, shifted
  clouds) both consume the P3S outputs. Full 5-band coverage is the publication
  gate (#16); the presentation is closed and does not require it.

## CANONICAL standard P4 recipe — ONE driver (repair 2026-07-18)
Single authoritative, manifest-bound, fail-closed chain. Run inside a compute alloc:
```
srun --overlap --jobid=<HOLDER> -w <NODE> -n1 -c128 bash -lc \
  'export HOME=/global/homes/j/josephrb; source setup_salloc_env.sh >/dev/null 2>&1; \
   cd nd-unfolding && STOP_AFTER=evidence bash run_p4_standard.sh'
```
Ordered stages (each fail-closed; chain aborts on any nonzero stage):
1. `run_p4_merge_audit_std.sh` — 10 endpoint hadd (large-tree-safe) + per-playlist audit.
2. `p4_evidence.py` — recompute+bind hashes (endpoint SHA256s, mask/order 10694,
   central 5D/4D, edges/bin-volume, endpoint-manifest) → `evidence/p4_standard_manifest.json`,
   `p4_merged_audit.json`, `p4_endpoint_evidence.json`. (`STOP_AFTER=evidence` = repair preflight.)
3. `run_p4_unfold_std.sh` — atomic (`OUT.tmp`→validate→rename ROOT+`.done` receipt),
   resumable by exact tag set, `--seed 42`, no `--universe`, fail-closed parallel return.
--- HARD GATE: standard-p4-verifier PASS on the committed patch → set `P4_VERIFIER_PASS=<token>` ---
4. `p4_build_components.py` — manifest-bound; C_final5 = named corrected **bkgaware**
   non-lateral components + 5 active per-band MAT blocks (no globs; traces>0; exact
   active-total identity). Writes candidate + component provenance manifest.
5. `p4_validate_active_lateral.py` — exact 5 bands / positive-finite traces / exact
   component sum / symmetry+PSD / complete support comparison / mandatory `--merged-dir`.
6. `p4_project_4d.py` — C4=M C5 M^T; 10694→4830 mask/edge hashes; frozen 5D/4D central
   byte-identical pre/post; PSD; declared central-reproduction. Candidate paths only.

**RETIRED / FORBIDDEN for standard publication** (guarded to abort with `[RETIRED]`):
`merge_active_endpoints.sh`, `run_active_lateral_unfolds_interactive.sh`,
`run_active_laterals_interactive.sh`, and bare `analyze_universes_5d.py --glob …`
(superseded by the manifest-bound `p4_build_components.py`). Never write onto adopted
paths; never use the non-bkgaware combined ROOT as the support family. Final adoption
consumes the component provenance manifest (do not rely on `adopt_unified_5d.py`
leaving lateral bands untouched).

## Coordination — do NOT touch (other agents)
- B: `55963058` (claude-hold / orchestrate_gpu_node, PET), `pet_boot_arr`.
- C: `ev5d_active_fp` (P3F FPS via this launcher, FPS=1), `bootfpsC`/`sspfpsC`.
- D: `p6_4d_rep` / `boot4dC` / `ssp4dC` / `cv4dpilot` (corrected 4D UQ).
- Namespaces off-limits: `products/pet/*`, `uq_fps/corrected/`,
  `active_universe_5d/fps/`, `uq_4d/corrected/`.
