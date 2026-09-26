# Cold-start handoff — PET final-design study (living document; update at each milestone)

Read this, then `PROTOCOL-20260925.md` (with Amendments 1, 2, 2b, 2c), `DEVELOPMENT-20260926.md`,
`DIAGNOSTICS-20260925.md`, `CAPACITY-20260925.md`, and the two review dispositions. Everything referenced is on the
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

## Next actions, in order

1. **Harvest development** when complete: `dev2P`, `dev2T` (run `diagnostics/posthoc_iterations.py` on the cluster
   into `posthoc/<stage>/`, `results/harvest.sh <stage>`), regenerate `dev/DEV_TABLES-*.json` with
   `dev/summarize_dev.py`, apply `dev/apply_finalist_rule.py`. Extend `DEVELOPMENT-20260926.md` with the PET2
   pretrained-vs-scratch contrast and the 16-epoch large arm.
2. **Amendment 3 (large-slot freeze)**: the rule's large finalist and its K; if it is not L128S1 K = 5, pilot it on
   the same S3P draws before fixing `n_F`; fill `freeze/EVIDENCE_DECLARATION-20260926.json` (`<LARGE>`, `<N_F>`,
   m); generate its FB manifests with `freeze/make_final_stage.sh` (same stages → paired draws), list them with
   `RELEASED-MANIFEST` lines; if `n_F` > 24 list FINAL draws 24…n_F−1 for every finalist and anchor. Must not
   contain the word UNBLIND.
3. Run the large finalist's FB rows (blinded).
4. **UNBLIND amendment** only when every look-1 row (both finalists, anchors) of `s4f` and `s4s` is COMPLETE; list
   them in a completeness manifest. Then score with `analysis/score_design.py`, harvest, and decide with
   `analysis/decide.py --evidence <filled declaration>`.
5. **Coverage (§9 as amended)** for each finalist not INELIGIBLE: B = 6 bootstrap members per replicate
   (`freeze/make_stage_manifests.py --bootstrap-members 1-6`, stage `S5`), N_cov = 120 at look 1, D4c 60; release by
   amendment with `RELEASED-MANIFEST` lines.
6. Selection (§6.6 as amended), independent scientific-scope review, report, deck, decision record, RUN_LOG/STATUS/
   VALIDATION_LEDGER (at delivery, after merging `origin/main` for the next dense VL id), draft PR.

## Known traps (measured this study)

- `grep -l COMPLETE` also matches `INCOMPLETE`; use `grep -lx COMPLETE`.
- `gpu_shared` jobs with long walltimes rarely start; 1–2 h requests start sometimes; `gpu_regular`/`gpu_preempt`
  did not start in 6 h. `gpu_debug` (2 running, 5 submitted per user) and `gpu_interactive` (2 per user, 4 h,
  `srun` only) carry the load. Iterations longer than ~26 min (16 epochs, PET2) cannot use `gpu_debug`.
- Login nodes do not share `/tmp`; put helper files in the study area.
- Pushing large commits over HTTPS needs `git -c http.postBuffer=524288000 push`.
- The runner refuses FB/RB rows not listed (sha256-pinned) in the protocol; the launcher forces `SCORE=0` on them.
