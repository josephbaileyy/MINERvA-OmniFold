# Cold-start handoff — PET final-design study (replacing the orchestrating session, 2026-09-29)

This file is self-contained for a successor. It supersedes the chronological state lines in
`HANDOFF-pet-final-design.md` (still valid as history, traps and procedures). **Everything labelled "measured" was
measured at the stated UTC time and must be re-measured before acting** (commands in §6); estimates are labelled.

## 1. Authorization and governing artifacts (read in this order)

1. `docs/orchestration/AUTHORIZATION-20260925-pet-final-design.md` — Joseph's grant, verbatim. The successor
   continues this grant; it is not a new one.
2. `nd-unfolding/pet/final_design/SCOPE-HANDOFF-20260925.md` and `GOAL-20260925-pet-final-design.txt` — the scope
   (byte copies of the original handoff and goal).
3. `nd-unfolding/pet/final_design/PROTOCOL-20260925.md` — frozen decision table §6 plus Amendments 1, 2, 2b, 2c, 3a,
   3b, 3b-bis, 3c, 3d, 3e, 3f (all prospective, before any final-bank score). **No UNBLIND amendment exists yet.**
4. `dev/FINALIST_RULE-20260926.md` (+ Addendum, correction, Addendum 2); `freeze/EVIDENCE_DECLARATION-20260927.json`
   (decision set, m = 2, n_final = 60, n_stress = 8, n_required D4c/D3 = 40, anchors CTLrefK3/CrefK3).
5. `DECISION_RECORD-pet-final-design.md` (status OPEN; decisions to date), `REVIEW_DISPOSITION-{IMPL,STAT,SCOPE}-*.md`.
6. `HANDOFF-pet-final-design.md` §"Known traps" and repo `AGENTS.md` / `CLAUDE.md`.

## 2. Repository, branches, commits (measured 2026-09-29 06:27Z)

| item | value |
|---|---|
| repo | `github.com/josephbaileyy/MINERvA-OmniFold` (public: stage explicit paths only) |
| campaign branch | `pet-final-design-20260925`, head **`44d71467`** before this handoff's commit (verify with `git ls-remote origin pet-final-design-20260925`) |
| predecessor | `pet-improvement-20260922` @ `9368ec9e` (PR #3, draft) |
| campaign PR | **#4, draft, base `pet-improvement-20260922`** — never merge (owner decision) |
| `main` | `9dd32efe` (unrelated to the campaign; PR #5 tooling under `tools/developer/` has no overlap) |
| local worktree | `/Users/josephbailey/local-research/MINERvA-OmniFold-pet-final-design` (clean except two stale untracked copies `dev/DEV_TABLES.json`, `dev/SCREENS.json` — not evidence; the dated `*-20260927*.json` files are) |
| cluster area `$B` | `/pscratch/sd/j/josephrb/pet-final-design-20260925/` (repo mirror `repo/`, pinned worktrees `checkouts/<sha8>/`) |
| deployed checkout | **`checkouts/04703b90`** (`04703b90bd5dccfa29ef6634213b2abfbcb7c5a4`, Amendment 3f): every running lane uses it; never modify or delete it |

## 3. Frozen design and where the campaign stands (measured unless marked)

- Finalists (Amendments 3c/3d): compact **H2S1T24 K = 5**, large **L128S1T24 K = 4**; anchors CTL K3, C K3.
  Measured cost per unfolding 1.77 / 1.49 A100-h (the compact is not cheaper → §6.5 cost path closed).
- Sizing (3e/3f): n_F = 60 (capped; E0 NI needs ≈ 250 draws — quantified limit), N_LIB = 40, n_S = 8.
- **Look-1 final-bank rows (blinded), measured 06:27Z: 617 / 944 COMPLETE** — `s4f_a3` 192/192, `s4s_a3` 228/336,
  `s4f_a3e` 170/288, `s4s_a3e_n40` 27/128. Rate over the last ~24 h ≈ 7–14 rows/h. **Estimate:** all 944 complete
  ≈ 2026-09-30 12:00Z – 2026-10-01 06:00Z.
- Study total 1,196.0 A100-h at 2026-09-28 10:58Z (`resources/`); project `m3246_g` far from exhausted.

## 4. Running processes and jobs — identity, ownership, persistence

All cluster-side processes run as user `josephrb`, detached (`nohup setsid`), **independent of this conversation**.

| what | identity (measured 06:27Z) | persists until | role |
|---|---|---|---|
| watcher `jobs/keep_busy.sh` | host **login07** (`$B/keep_busy.host`), started 2026-09-29T00:01:59Z from `checkouts/04703b90`, last relaunch line 06:04:39Z in `$B/keep_busy.log` | **2026-10-03T22:00Z** or `$B/keep_busy.stop` | the ONLY submitter of `pfd-inter1/2` (gpu_interactive, 4 GPU, 4 h), `pfd-sint1/2` (gpu_shared_interactive, 2 GPU, 4 h) and anchor debug chains; per-GPU lanes walk `s4f_a3 s4s_a3 s4f_a3e s4s_a3e_n40` |
| allocations | 59060723 pfd-inter1, 59060389 pfd-inter2, 59058382 pfd-sint1, 59063316 pfd-sint2 (IDs rotate every 4 h) | relaunched by the watcher | run FB rows (SCORE=0 forced) |
| self-resubmitting chains `pfd-chain` | gpu_shared (7 pending: 59055454, 59058053, 59058077, 59058786, 59058787, 59060047, 59060112), gpu_regular 59037556/57, gpu_preempt 59037558/59 (pending) | resubmit themselves (CHAIN=1) until their manifest is complete or MAX_ROUNDS | extra capacity for the same manifests |
| stall monitor `jobs/fbmon.sh` | detached, relaunched ≈ 05:26Z (`$B/fbmon.out`, empty while running; written on exit) | ≤ 8 h per cycle | read-only; exits on completion, 2-h stall, or no watcher allocations |
| row claims | `flock` on `<out>/<row>/.flock` | held by the running worker | prevents two lanes running one row |

**Depends on this conversation:** nothing on the cluster. Only this session's local background shell polls and
scheduled wakeups (read-only) die with it. **Does depend on an owner action:** the NERSC SSH certificate on the Mac
(`~/.ssh/nersc-cert.pub`, **valid to 2026-09-29 16:05Z**): cluster jobs continue without it, but no ssh access,
scoring, UNBLIND or decision is possible until Joseph renews it (`sshproxy`).

## 5. Transferring operational ownership without duplicates

1. Do **not** start a watcher, allocation or chain on arrival. First confirm the existing watcher is alive: recent
   relaunch lines in `$B/keep_busy.log` (every ≈ 4 h per allocation) and the four allocations in `squeue`.
2. If a watcher restart is ever needed (new checkout, new stop time), use only
   `bash $B/start_watcher.sh <full sha> [stop]` (committed as `jobs/start_watcher.sh`): it stops any watcher on any
   login node through the shared stop file, waits for "keep_busy stopped", then starts one. Never `pkill -f`/`pgrep -f`
   inside an ssh one-liner; `ps` sees only the node the ssh landed on.
3. Do not submit extra chains for the look-1 manifests: 11 are queued; duplicates only waste queue slots (row flocks
   prevent double execution). Never cancel jobs of other lanes (`s5p-*`, `s5e-*` share the user).
4. The monitor is read-only; one more copy is harmless but unnecessary. Relaunch it only after `fbmon.out` shows an
   exit line: `cd $B && nohup setsid bash fbmon.sh > fbmon.out 2>&1 < /dev/null &`.

## 6. Commands to re-measure (from the Mac; the cert must be valid)

```bash
ssh-keygen -L -f ~/.ssh/nersc-cert.pub | grep Valid
ssh -o BatchMode=yes saul.nersc.gov 'B=/pscratch/sd/j/josephrb/pet-final-design-20260925; R=$B/checkouts/04703b90/nd-unfolding/pet/final_design/runs; date -u
  for m in s4f_a3 s4s_a3 s4f_a3e s4s_a3e_n40; do out=$B/s4f; [[ $m == s4s* ]] && out=$B/s4s; t=$(grep -vc "^#" $R/$m.tsv); k=0
  for n in $(cut -f1 $R/$m.tsv | grep -v "^#"); do s=$(timeout 5 cat $out/$n/status.txt 2>/dev/null); [ "$s" = COMPLETE ] && k=$((k+1)); done; echo "$m $k/$t"; done
  timeout 20 squeue --me -h -o "%i %j %q %T %M" | grep -v s5p; tail -4 $B/keep_busy.log | cut -c1-110; cat $B/keep_busy.host; cat $B/fbmon.out'
```
Use `timeout` on every status read (a stuck scratch read hung an unguarded loop on 2026-09-28). The Mac↔NERSC link
dropped for ≈ 15 min on 2026-09-28 ("Can't assign requested address" is local); retry, do not relaunch anything.

## 7. Terminal conditions and the next permitted actions (in order)

1. **Wait** until all 944 look-1 rows are COMPLETE (§6). Failed rows are rerun only with the identical config, draw
   and seed (2c.10); list any rerun in the stage record.
2. `python freeze/completeness_manifest.py --root $B --manifest s4f_a3:s4f s4f_a3e:s4f s4s_a3:s4s s4s_a3e_n40:s4s
   --out COMPLETENESS-look1.tsv` (on the cluster, in the deployed checkout's `final_design/freeze/`; exit 0 required).
   Commit it with **`### Amendment 4 (<date>) — UNBLIND look 1`** in `PROTOCOL-20260925.md` citing that manifest (the
   heading word UNBLIND is what unlocks the scorers). Deploy the new commit as a new `checkouts/<sha8>` (do not
   touch `04703b90`).
3. On the cluster: `bash $B/checkouts/<new sha8>/nd-unfolding/pet/final_design/jobs/score_fb.sh <new sha>`
   (5 guarded CPU-debug jobs → `$B/scored/fb`); FB cost: `analysis/cost_from_receipts.py --packing H2S1T24=2
   L128S1T24=2` on the finalists' FB run dirs (declared packing; runs at other packing are excluded and listed).
4. Locally: rsync `$B/scored/fb` and the cost JSON; `bash analysis/run_look1.sh <scores> <cost> <out>`
   (evidence → `decide.py` look 1 → `--provisional`). Commit `results/final/decision_look1*.json`, the evidence,
   and harvested scores (explicit paths). Record the outcome in `DECISION_RECORD-*.md`.
5. If look 1 returns CONTINUE for a sequential rule: look 2 = FINAL draws 60–119 (same stages), released by a new
   amendment with `RELEASED-MANIFEST` lines before running; decide at look 2 with `--previous`.
6. Coverage (§9, 3a.5) for the provisionally first finalist: `bash freeze/make_coverage_stage.sh <ID:K> <tag>`
   (B = 6, N_cov 120 + D4c 60 ≈ 1,080 unfoldings ≈ 1.7 k A100-h), released by amendment (`RELEASED-MANIFEST`),
   added to the watcher lanes (new checkout via `start_watcher.sh`), then `analysis/coverage.py` and the final
   `decide.py` with the coverage file. The other finalist's coverage only per 3a.5.
7. Terminal outcome (§10): SELECTED, UNRESOLVED_WITH_DEFAULT (3(v)) or NO_ELIGIBLE_DESIGN — never manufactured.
   Then an independent read-only review of the decision (isolated worktree), the report §6–8
   (`REPORT-20260926.md`), deck (`slides/make_final_deck.py` + test), decision record, resource ledger, RUN_LOG/
   STATUS/VALIDATION_LEDGER (merge `origin/main` first for the next dense VL id), this handoff, draft PR #4 body.

## 8. Prohibited

No scoring, harvesting or opening of FB outputs (anything under `$B/s4*`, `$B/s5*` beyond `status.txt` and the
field-restricted timing reader) before the UNBLIND amendment; no change to the frozen decision table, finalists,
sizing or draw cuts except by a prospective amendment before scoring; no real-data unfolding, publication adoption,
C_stat/C_ML, Gate-6 work, OI-126, scalar-5D covariance change, note/primer/paper edits, collaborator messages; no
merge of PR #4; no `git add -A/-u/.`/directories (explicit paths only; `git add -f` only for explicit PDF paths); no history rewrite; no cancelling other lanes' jobs; no restarting jobs or the watcher merely to pick up
tooling (e.g. PR #5); no new watcher without stopping the old one via the stop file.

## 9. Owner decisions outstanding

Only (a) renewing the NERSC certificate when cluster access is needed, and (b) any merge of PR #3/#4 (out of scope).
No scientific decision is pending an owner: UNBLIND, look 2, coverage order and the terminal rule are all
pre-registered.

## 10. Campaign-review choice (2026-09-30, `docs/orchestration/CAMPAIGN-REVIEW-20260929.md` §1)

- **Decision answered:** the terminal outcome for the pair {H2S1T24 K5, L128S1T24 K4} under the frozen §6 and its
  amendments. NO_ELIGIBLE_DESIGN and UNRESOLVED_WITH_DEFAULT (with the quantified limit, 3a.1/3a.6) are useful
  terminal results; none is promoted after scoring.
- **Owner:** the successor orchestrator (Claude Opus 5.5, session `572b8667-2242-4991-ad5b-602e655e23c9`), which
  took over from this handoff on 2026-09-29 07:02Z without starting any watcher, allocation or chain.
- **Independent reviewer of the decision:** a fresh read-only session in an isolated worktree at the fixed decision
  commit, preferably Astra High via Codex (the review's strongest attributed reviews), otherwise a fresh read-only
  Claude session. Frozen rubric: does each verdict follow from the committed evidence under §6 plus amendments;
  operands, reproductions, material impact and a disposition per finding. The reviewer writes nothing.
- **Budgets:** compute per protocol §8 (S4 ≤ 1,800, S5 ≤ 2,200 A100-h; re-plan if the `m3246_g` balance falls below
  the §8 floor). Review/repair: at most two review → repair cycles on the decision, then an explicit
  continue/stop recorded in the decision record; minor bookkeeping findings are dispositioned without restarting
  the review. Strategy reassessed after the look-1 decision and after coverage.

## 11. State after look 1 (2026-09-30 23:45Z; supersedes §3–§4 and §7 items 1–4 for operations)

- **Done:** 944/944 look-1 rows COMPLETE → `freeze/COMPLETENESS-look1.tsv` → **Amendment 4 UNBLIND look 1**
  (`39e8cbbd`) → FB scored (`results/final/scored_fb/`, 5 jobs) and FB cost (`resources/cost_fb_look1-20260930.json`)
  → `analysis/run_look1.sh` → **look-1 decision** (`96e6a412`, `results/final/decision_look1*.json`): L128S1T24 K4
  **INELIGIBLE on B2** (point-decided, statistically unresolved; D4c n down 0.0122 vs ≤ 0.010, 95 % 0.0064–0.0181);
  H2S1T24 K5 passes §6.1–6.3, C1–C5 pending; no look 2. Provisional: H2S1T24 K5 first for coverage.
- **Running:** **Amendment 5** (`d06a495e`) released coverage of H2S1T24 K5: `runs/s5c_a5_H2S1T24.tsv` (720, dev tilt,
  C1–C4) then `runs/s5d_a5_H2S1T24.tsv` (360, D4c up, C5), output `$B/s5`, `SCORE=0`. Watcher restarted by
  `start_watcher.sh` from **`checkouts/d06a495e`** on **login05** (moved to **login37** on 2026-10-02, see incident below), stop **2026-10-10T22:00Z**; lanes = coverage only
  (dev tilt before D4c). Deployed checkouts `04703b90` (look-1 lanes, finished), `016f1fac` (manifest tool),
  `39e8cbbd` (scoring), `d06a495e` (coverage lanes) — never modify any of them.
- **Next:** when all 720 `s5c` rows are COMPLETE: from `checkouts/d06a495e` (module `tensorflow/2.15.0` python — the
  login `python3` is 3.6) run `completeness_manifest.py --manifest s5c_a5_H2S1T24:s5 --out
  freeze/COMPLETENESS-s5c_a5_H2S1T24.tsv` (write it in the study area, copy into the repo), commit it with
  `### Amendment 6 (<date>) — UNBLIND coverage s5c_a5_H2S1T24` (Amendment 5b: the exact group name), deploy, then
  `jobs/score_cov.sh <sha> s5c_a5_H2S1T24 5 $B/population/fb_population_dev.json` and `analysis/coverage.py` for
  C1–C4 via `analysis/run_final.sh results/final/scored_fb resources/cost_fb_look1-20260930.json <dev scores> - <out>`
  (C5 stays incomplete). Then the same for `s5d_a5_H2S1T24` (population `fb_population_D4c_p_up.json`) and C5 (skipped
  only after a decisive C1–C4 FAIL): `run_final.sh … <dev scores> <D4c scores> <out>` → terminal outcome; then the review under
  `REVIEW_BRIEF-DECISION-20261001.md`.
- **Traps found this session:** `freeze/completeness_manifest.py` is not in `04703b90` (run tools from a checkout
  that has them; the `runs/*.tsv` are identical); login-node `python3` is 3.6 (use the module); the Mac has no
  `timeout`; `runner/test_step2_ensemble.py` has 2 stale failures that predate this session (X4 arm; fail on
  `96e6a412` clean); `ps | grep fbmon` matches its own ssh command line; `keep_busy.log` started/stopped counts are
  historical artifacts (start_watcher then waits its full 300 s).
- **Incident 2026-10-02:** the watcher on login05 stayed alive but launched nothing after 04:16Z (its four allocations
  completed normally at 07:28–07:50Z and were not relaunched; login05 refused internal ssh; most likely its `squeue`
  call kept failing, a branch of `keep_busy.sh` that sleeps and retries without logging). It still obeyed the stop
  file: `start_watcher.sh d06a495e… 2026-10-10T22:00Z` from login37 at 09:23Z relaunched all four allocations. No run
  was interrupted (216/720 COMPLETE); ≈ 1.6 h of capacity lost. **Watcher is now on login37.** Signal to watch: zero
  running `pfd-inter*`/`pfd-sint*` allocations for two consecutive polls while rows remain → restart the watcher on
  another node through `start_watcher.sh` (same checkout and stop).

## 12. Terminal state (2026-10-05 13:30Z)

- **Outcome: NO_ELIGIBLE_DESIGN** (`results/final/coverage_dev/decision_final.json`, commit `337e34cf`): H2S1T24 K5 fails
  coverage C1 and C4 (its six-member interval is too wide: 68 % coverage 0.896 vs ≤ 0.80; widths 1.3–1.7 × the limit in
  bins 1–6); L128S1T24 K4 fails B2 (look 1). C5 skipped (3a.5); L128S1T24's coverage not assessed.
- **Cluster:** watcher stopped through the stop file (13:24Z, `keep_busy.log`); the four study allocations cancelled;
  no study job remains. The stop file `$B/keep_busy.stop` is left in place on purpose (a restart needs
  `start_watcher.sh`, which removes it). 24 D4c members are partial and unscored (blinded); `runs/s5d_a5_H2S1T24.tsv`
  has no UNBLIND amendment and must not be scored.
- **Remaining for delivery:** the independent read-only review under `REVIEW_BRIEF-DECISION-20261001.md` and its
  disposition; VALIDATION_LEDGER rows (next dense id on `origin/main`); final PR #4 body. The §11 repair is an owner
  decision (decision record, last row; report §8).
