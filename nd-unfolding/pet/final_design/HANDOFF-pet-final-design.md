# Cold-start handoff — PET final-design study (living document; update at each milestone)

Read this, then `PROTOCOL-20260925.md` (with Amendments 1, 2, 2b, 2c, 3a, 3b), `DEVELOPMENT-20260926.md`,
`DIAGNOSTICS-20260925.md`, `CAPACITY-20260925.md`, and the three review dispositions (IMPL, STAT, SCOPE). Everything referenced is on the
pushed branch; nothing depends on a local scratch directory.

## Identity

- Repository `github.com/josephbaileyy/MINERvA-OmniFold` (public — stage explicit paths only).
- Branch **`pet-final-design-20260925`** (from `pet-improvement-20260922` @ `9368ec9e`); verify with
  `git ls-remote origin pet-final-design-20260925`. Study directory `nd-unfolding/pet/final_design/`.
- Authorization `docs/orchestration/AUTHORIZATION-20260925-pet-final-design.md` (Joseph's grant, verbatim);
  scope = the byte copy `SCOPE-HANDOFF-20260925.md`. Exclusions: no real data, no adoption, no `C_stat`/`C_ML`,
  no Gate 6, no `OI-126`, no scalar-5D covariance change, no note/primer/paper edits, no collaborator messages,
  no merge (draft PR only).
- Cluster area `/pscratch/sd/j/josephrb/pet-final-design-20260925/` (repo mirror `repo/`, pinned checkouts
  `checkouts/<sha8>/`, one directory per stage). Access needs a live NERSC certificate
  (`ssh-keygen -L -f ~/.ssh/nersc-cert.pub`; Joseph renews with `sshproxy`).

## State (update this block)

- **2026-09-26 15:05Z.** Stages S0–S2 done or nearly: capacity/banks frozen (DEV 45.09 M, FB 2.65 M sealed except
  the listed runs, RB 1.41 M sealed); failure localized (detector step); development screen complete for our PET
  designs. **Compact finalist frozen: H2S1 at K = 5** (Amendment 2). Anchors CTL K = 3 and C K = 3 (FINAL only).
  **Large slot not yet frozen**: waiting for PET2 pretrained/scratch (`dev2P`) and the 16-epoch large arm (`dev2T`);
  L128S1 (K* = 5) and L64S1 (K* = 4) already pass the screens. PET2-pretrained diverges from k = 3 under the
  declared recipe with warm start (development observation; see the development record when written).
- **Final-bank runs executing BLINDED** (`s4f_a2` FINAL, `s4s_a2` library; `SCORE=0` forced; scorers refuse S4/S5
  until an `UNBLIND` amendment). Do not open, score or harvest anything under `s4f/`, `s4s/`, `s5*/` before the
  UNBLIND amendment. Only job states and wall times may be read.
- **Sizing pilot S3P** (DEV) running (`runs/s3p_all.tsv`, incl. D3 rows); it fixes `n_F` by the §8 rule as amended.
- **Watcher** `jobs/keep_busy.sh` runs on a Perlmutter login node (host in `keep_busy.host`, log `keep_busy.log`)
  until 2026-09-27 22:00Z: it relaunches the two 4-h `gpu_interactive` allocations and keeps two `gpu_debug` chains
  on the highest-priority incomplete manifests. Stop it early with `touch $B/keep_busy.stop`.
- Independent reviews so far: implementation (`REVIEW_DISPOSITION-IMPL-20260926.md`: 1 BLOCK + 5 MAJOR fixed) and
  statistical design (`REVIEW_DISPOSITION-STAT-20260926.md`: 1 BLOCK + 7 MAJOR fixed, all prospective).

- **2026-09-26 15:50Z additions.** Interim sizing from 28/44 pilot runs (H2S1 vs L128S1 at K = 5, 4 DEV draws; not
  yet the sizing record): FINAL contrasts give n_F = 30 (E0-driven, joint power ≈ 0.73); the E4 (proton-topology)
  non-inferiority contrast sits at −0.045 against its −0.05 margin (sd 0.040) and would need ≈ 1,770 draws — a
  quantified limit for the equivalence path (the cost path is closed anyway if the large finalist costs < 2×).
  PET2-pretrained diverges from k = 3 under the declared constant per-iteration rate (pull max 5.5 × 10⁵ at k = 5)
  while PET2-scratch is stable; a matched tuning arm (`dev2Q`, both initializations with the annealed step-1
  schedule) is queued before the large slot is closed. The watcher now runs from checkout `0e00644f`.

- **2026-09-26 ~18:30Z additions.** Independent scientific-scope review done (`REVIEW_DISPOSITION-SCOPE-20260926.md`);
  prospective rules in **Amendment 3a** (terminal practical default `UNRESOLVED_WITH_DEFAULT`; cost = charged A100-h at
  declared packing via `analysis/cost_from_receipts.py`; N1 stays on E9 truth weights, pull reported; E4/E5 sized as a
  separate library group; coverage ordered by `decide.py --provisional`; futility and bank-effect bound reported; cost
  part UB repair) and the **finalist-rule addendum** (`dev/FINALIST_RULE-20260926.md`: completeness on both draws,
  S-N1 at K* gating pull+push weights, between-design step in `dev/apply_finalist_rule.py`). The PET2 policy arm
  `dev2Q` now has ids `P2preA1`/`P2scrA1` and D1 −0.35 rows (16 runs, not started at 18:20Z). All development
  post-hoc files are being recomputed with the committed tool into `$B/posthoc_v2/<stage>` (15 dev1 files were stale).
  DEV costs per unfolding (A100-h, declared packing): H2S1 K5 0.88, L128S1 K5 ≈1.0, L64S1 K4 0.77, H2S1E16 K4 1.29,
  L128S1E16 K5 2.04, P2preS1 K4 2.23, P2scrS1 K5 2.78 (`$B/costs/`). PET2-pretrained's step-1 weights reach 334–1,217
  at k = 4 on the development tilt (S-N1 fails there). The watcher runs from checkout `3e3059f3`; its helper
  `$B/start_watcher.sh <sha>` restarts it (never `pkill -f`/`pgrep -f` inside an ssh one-liner).

- **2026-09-26 ~20:40Z (supersedes the next-actions list below where they differ).** Sizing pilot complete and scored
  (`sizing/SIZING-20260926.md`: n_F = 30; library E4/E5 draws 60, E4 NI a quantified limit). **N2 finding**
  (Amendment 3b): estimator-seed sd of R_E0 0.095 (H2S1 K5) / 0.091 (L128S1 K5) > 0.05, located in the truth step.
  Repair arm running: `runs/dev3N.tsv` (H2S1T24/L128S1T24 screens, OUT `$B/dev3N`), `runs/s3n_fast.tsv` and
  `runs/s3n_slow.tsv` (N2 seed runs on the pilot's events/seeds, OUT `$B/s3p`). H2S1 FB rows paused. Step-2 ensemble
  fallback code merged (`runner/step2_ensemble.py`, inert at M = 1; needs the cluster smoke test in its commit message
  before use). Watcher from `b98986e9` with per-GPU lanes; restart with `bash $B/start_watcher.sh <sha>`
  (copy in `jobs/start_watcher.sh`). Two overlap lanes run inside the current interactive allocations.

## Next actions, in order

1. When `dev3N`, `s3n_fast`, `s3n_slow`, `dev2P`, `dev2T`, `dev2Q` are complete: post-hoc (`posthoc_iterations.py
   --workers 24` into `$B/posthoc_v2/<stage>`, CPU debug, guarded), score the S3P seed runs at k = 4, 5, 6
   (`analysis/score_design.py`), `dev/n2_table.py` at each design's K\*, regenerate the tables
   (`dev/summarize_dev.py --root <view with posthoc2 dev1 dev2L dev2S dev2T dev2P dev2Q dev3N>`), apply
   `dev/apply_finalist_rule.py --n2 n2.json`, commit `DEV_TABLES`/`SCREENS`, harvest (`results/harvest.sh`).
2. **Amendment 3c (re-freeze)**: both packages by the rule with S-N2; if a finalist changes, pilot it on the S3P draws
   (`freeze/make_stage_manifests.py --stage S3P ...`) and recompute sizing (`analysis/build_pilot.py`, `sizing.py`);
   fill `freeze/EVIDENCE_DECLARATION-*.json` (decision set, m, n_F, n_required D4c/D3 = library n, cost block from
   `analysis/cost_from_receipts.py` at declared packing); generate FB manifests (`freeze/make_final_stage.sh`, same
   stages → paired draws; extensions for FINAL draws 24…n_F−1 and D4c/D3 draws 8…n−1) and list them with
   `RELEASED-MANIFEST` sha256 lines. Must not contain the word UNBLIND. If every design fails S-N2: smoke-test the
   step-2 ensemble on the cluster and run an X4 arm (Amendment 3b item 5) first.
3. Run the finalists' FB rows (blinded; watcher priorities).
4. **UNBLIND amendment** only when every look-1 row is COMPLETE (completeness manifest). Score (`score_design.py`),
   decide (`decide.py --evidence`), then `decide.py --provisional` to order coverage (3a.5).
5. Coverage (`freeze/make_coverage_stage.sh <ID:K> <tag>`; release by amendment), `analysis/coverage.py`, final decision.
6. Independent review of the final decision, report/deck (`slides/make_final_deck.py`), decision record, RUN_LOG/
   STATUS/VALIDATION_LEDGER (after merging `origin/main` for the next dense VL id), resource ledger, draft PR.

## Known traps (measured this study)

- `grep -l COMPLETE` also matches `INCOMPLETE`; use `grep -lx COMPLETE`.
- Never `pkill -f`/`pgrep -f` a pattern inside an ssh one-liner (it matches its own shell); use `start_watcher.sh`.
- The local shell is zsh: unquoted `$VAR` lists do not word-split (use `${=VAR}`); `${t:+--flag $t}` is one word.
- Post-hoc files written while a run is going are stale; the tool now refreshes them (checks iteration count and tool sha).
- `gpu_shared` jobs with long walltimes rarely start; 1–2 h requests start sometimes; `gpu_regular`/`gpu_preempt`
  did not start in 6 h. `gpu_debug` (2 running, 5 submitted per user) and `gpu_interactive` (2 per user, 4 h,
  `srun` only) carry the load. Iterations longer than ~26 min (16 epochs, PET2) cannot use `gpu_debug`.
- Login nodes do not share `/tmp`; put helper files in the study area.
- Pushing large commits over HTTPS needs `git -c http.postBuffer=524288000 push`.
- The runner refuses FB/RB rows not listed (sha256-pinned) in the protocol; the launcher forces `SCORE=0` on them.
