# Cold-start handoff — PET final-design study (living document; update at each milestone)

Read this, then `PROTOCOL-20260925.md` (with Amendments 1, 2, 2b, 2c, 3a, 3b, 3b-bis, 3c, 3d, 3e, 3f), `DEVELOPMENT-20260926.md`,
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

- **2026-09-27 ~09:15Z — FINALISTS RE-FROZEN (supersedes earlier state lines).** N2 repair arm decided (seed sd of R_E0
  at K\*, limit 0.05; `sizing/n2_all-20260927.json`): H2S1 0.095, L128S1 0.091, L64S1 0.057, L128S1E16 0.071, H2S1E16
  0.074, CS1 0.054 FAIL; **H2S1T24 (24-epoch truth step) 0.037 PASS, L128S1T24 0.043 PASS**. PET2 closed (P2preA1
  stable but topology ≤ 0.225). **Decision set {H2S1T24 K5, L128S1T24 K4}** (Amendments 3c, 3d), anchors CTL K3 /
  C K3. X4 arm stopped (not needed). FB released blinded: `runs/s4f_a3.tsv` (FINAL draws 0–23, finalists + anchors),
  `runs/s4s_a3.tsv` (library 21 × 8). Measured cost per unfolding: H2S1T24 1.77, L128S1T24 1.49 A100-h.
  Pilots for the new finalists running: `runs/s3p_t24.tsv`, `runs/s3p_l24.tsv` (OUT `$B/s3p`). Withdrawn rows (X4,
  H2S1 K5 FB) are flock-held by `$B/hold_rows.py` (until ~23:00Z) so old lanes skip them. Watcher `aa5f847e`
  (interactive ×2, shared_interactive ×2, debug = anchors' FINAL rows only).

- **2026-09-27 14:20Z.** Amendment 3e: n_F = 60 (capped; E0 NI between the finalists needs 250 draws); FINAL draws 24–59
  and D4c/D3 draws 8–59 released blinded (`runs/s4f_a3e.tsv`, `runs/s4s_a3e.tsv`; draw-ordered; only the first N_LIB
  D4c/D3 draws enter decisions). **Done 15:00Z (Amendment 3f): N_LIB = 40**; the lanes run `runs/s4s_a3e_n40.tsv`; draws 40–59 are held unused by
  `$B/hold_lib40.py` (6 h) and never enter decisions. The watcher
  (`c2978ddd`) runs **until 2026-10-01T22:00Z** so the released FB rows keep running while no session is attached;
  stop early with `touch $B/keep_busy.stop`. The NERSC certificate of the orchestrating session expired 2026-09-27
  16:04Z; renew with `sshproxy` to continue (scoring, UNBLIND, decision, coverage).

- **2026-09-28 02:40Z.** Look-1 FB progress 285/944 (s4f_a3 161/192, s4s_a3 34/336, s4f_a3e 82/288, s4s_a3e_n40
  8/128), ≈ 15–18 rows/h → complete ≈ 2026-09-29 18:00–22:00Z. Study total 1,001.8 A100-h (`resources/`). All lanes
  healthy; stall monitor `$B/fbmon.sh` (8-h cycles). The orchestrating certificate expires 2026-09-28 10:46Z: renew
  (`sshproxy`) before look-1 completes to run the UNBLIND step (next actions 3–5).

- **2026-09-28 10:58Z.** Look-1 FB 426/944 (s4f_a3 **192/192 complete**, s4s_a3 80/336, s4f_a3e 141/288,
  s4s_a3e_n40 13/128), ≈ 16–18 rows/h → complete ≈ 2026-09-29 18:00–22:00Z. Study total 1,196.0 A100-h. Certificate
  valid to 2026-09-29 04:56Z: one more renewal is needed before the UNBLIND step.

## Next actions, in order

1. When `s3p_t24` and `s3p_l24` are COMPLETE: score (`analysis/score_design.py --k 4 5`, guarded CPU debug, into
   `$B/scored/s3p_new`), then `analysis/build_pilot.py --small H2S1T24:5 --large L128S1T24:4` (build_pilot matches the
   run name's K: both pilots are named with their frozen K) → `analysis/sizing.py` for the FINAL and library groups;
   commit `sizing/SIZING-*.md`.
2. **Amendment 3e (sizing + extension release):** fill `freeze/EVIDENCE_DECLARATION-20260927.json` (`<N_F>`,
   `<N_LIB>`); if n_F > 24 generate FINAL draws 24…n_F−1 for finalists and anchors
   (`freeze/make_stage_manifests.py --stage S4F --bank FB --replicates 24-<n_F−1> --candidates H2S1T24:5 L128S1T24:4
   CTLref:3 Cref:3 --cases dev D1_m0.350`), and D4c up / D3 +0.35 draws 8…N_LIB−1 (`--stage S4S --replicates 8-..
   --candidates H2S1T24:5 L128S1T24:4 --cases D4c_p_up D3_p0.35`); list them with `RELEASED-MANIFEST` lines; add
   them to the watcher lanes. No word UNBLIND.
3. When every look-1 row (s4f_a3, s4s_a3, extensions) is COMPLETE: completeness manifest + **UNBLIND amendment**;
   score FB rows; `analysis/decide.py --evidence <filled declaration>`; then `--provisional` for the coverage order.
4. Coverage (`freeze/make_coverage_stage.sh <ID:K> <tag>`, release by amendment), `analysis/coverage.py`, final decision.
5. Independent review of the decision; report/deck; decision record; RUN_LOG/STATUS/VALIDATION_LEDGER (merge
   `origin/main` first for the next dense VL id); resource ledger (note the lost rounds: ~80 empty debug rounds
   20:00–21:08Z and ~12 killed L128S1T24 debug iterations, 2026-09-26/27); update draft PR #4.

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
