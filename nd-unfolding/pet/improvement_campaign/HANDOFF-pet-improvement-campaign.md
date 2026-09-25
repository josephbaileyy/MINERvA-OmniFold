# Cold-start handoff — PET improvement campaign (living document; updated at each milestone)

Read this, then `README.md` (state table), then `PROTOCOL-20260922.md` (design + amendments), then
`REPORT-20260922.md`. Everything referenced here is on the pushed branch; nothing depends on a local scratch dir.

## Identity

- Repository: `github.com/josephbaileyy/MINERvA-OmniFold` (public, continuously harvested — push only campaign
  files, `git add` explicit paths).
- Campaign branch: **`pet-improvement-20260922`** (from `pet-direct-token-comparison` @ `7090fcc1`, the historical
  comparison, preserved unmodified). Verify the head with `git ls-remote origin pet-improvement-20260922`.
- Campaign directory: `nd-unfolding/pet/improvement_campaign/`. The historical comparison lives in
  `nd-unfolding/pet/configuration_comparison/` and must never be modified.
- Authorization: `docs/orchestration/AUTHORIZATION-20260922-pet-improvement-campaign.md` (Joseph's grant, verbatim).
  Scope: `SCOPE-HANDOFF-20260922.md`. Hard exclusions: no OI-126, no Gate-6, no `C_stat`/`C_ML`, no publication
  adoption, no change to the historical thresholds/verdict, no real-data unfolding, no note/primer/paper changes,
  no collaborator messages, no merge (draft PR only). Codex dispatches need Joseph's explicit approval (one
  codex-school review lane was approved 2026-09-23).

## Delegate branches (all merged into the campaign branch unless noted)

| branch | content |
|---|---|
| `pet-improvement-20260922-phaseA1` | runtime audit of the historical recipe; repaired per-step driver |
| `pet-improvement-20260922-phaseA2` | historical headline recompute, data path, feature inventory, resources |
| `pet-improvement-20260922-phaseB1` | scalar IBU/GBDT/MLP references, reference decomposition, truth learnability |
| `pet-improvement-20260922-phaseB2` | PET experiments 1–5 (driver faithfulness, truth-only, stepwise closure, schedule/miss rule, feature arms) |
| `pet-improvement-20260922-phaseE1` | distortion library, identifiability, scalar references under distortion, reference assessment |
| `pet-improvement-20260922-phaseF1` | AUSSIE scalar benchmark + miss-handling ablation; development-stage scalar scaling (`phase_d/`) |
| `pet-improvement-20260922-pools` | event-pool manifest (`pools/POOL_MANIFEST.json`) |
| `pet-improvement-20260922-confirm` | confirmatory runner; PILOT and FINAL execution (merged at `ce1f97e0`; retired — later work is on the campaign branch) |
| `pet-improvement-20260922-deck` | generated deck v2 (`slides/`) |

## Where things stand (update this block)

- **2026-09-25 00:30Z** — Review round 2 (FINAL) done and dispositioned (`REVIEW_DISPOSITION-ROUND2-20260925.md`):
  fail-closed FINAL gate, audit verdicts CLEAN/SUSPECT/UNVERIFIABLE (re-audit all CLEAN), scoring lock for new
  submissions, two concurrently scored FINAL runs re-scored IDENTICAL, §11 attribution scoped. FINAL decisions
  unchanged. Resource ledger now includes every confirmatory job (`confirm/ledger_from_sacct.py`). STRESS 29/360
  iterations; expected complete ~2026-09-25 15:00-19:00Z. When it lands: harvest, **re-score any STRESS run with
  more than one `score-<job>.log`** (`confirm/jobs/sbatch_rescore.sh`; the running chains predate the scoring lock),
  re-audit, analyze, decide coverage, review round 2 on STRESS (the codex-school lane approval covers it).
- **2026-09-24 23:45Z** — Orchestration moved to a claude-school session (the personal session `b160e1e8` hit its
  weekly limit; V1's delegate ended with it — the orchestrator now runs V1's harvest/analysis itself). **FINAL
  complete 36/36**, gate clean (re-audit `confirm/results/audit_locks-20260924T2320Z.json`, 0 suspect; receipts
  match the frozen manifest). Decisions: A, B, C all superior to CTL at K* = 10; adequate by the mean rule B@10,
  C@10, C@3; only C@10 (0.786, lower bound 0.763) clears the floor with its lower bound. Report §11 and deck slide
  15 carry it. STRESS running (6/360 iterations at 23:30Z; ~16 run-iterations per debug cycle when the queue is
  free). Next: harvest STRESS (`confirm/harvest.sh stress`), decide coverage (amendment 2), review round 2.
- **2026-09-24 12:30Z** — DEV complete; candidates frozen (amendment 2); PILOT complete (pool P, 3 replicates,
  reported separately); FINAL sized n = 12 before pool F was read; FINAL 15/36 runs harvested; STRESS (36 runs, pool
  T) queued behind FINAL. Review round 1 dispositioned (`REVIEW_DISPOSITION-20260924.md`); the run-lock BLOCK is
  fixed (flock) and audited (one suspect run quarantined and rerun from scratch).

## How to resume

1. Since 2026-09-24 23:45Z harvests and analysis commit **directly to the campaign branch** (the V1 delegate that
   used `pet-improvement-20260922-confirm` ended; that branch is fully merged at `ce1f97e0` and receives no more
   commits). Read `confirm/README.md` (status block, job ids, run tables) and `confirm/CONFIRM_RESULTS.md`.
2. On Perlmutter (`ssh perlmutter.nersc.gov`; access is a **24-hour sshproxy certificate** — if ssh says
   `Permission denied (publickey)`, check `ssh-keygen -L -f ~/.ssh/nersc-cert.pub` and ask Joseph to run
   `/usr/local/bin/sshproxy -u josephrb -o nersc`): `squeue -u josephrb` for `pv1-*` jobs. Run outputs:
   `/pscratch/sd/j/josephrb/pet-improvement-20260922/confirm/{pilot,final,stress}/<run>/scores.json`. Harvest with
   `confirm/harvest.sh`; analyze with `confirm/analyze_confirm.py` (decisions only when the FINAL manifest is complete).
3. Queue facts: `gpu_debug` starts in minutes (30-min cap, 2 jobs/user, one iteration per round at ~750 s/iteration);
   `gpu_shared` waits 1.5–6 h; `gpu_regular`/`gpu_preempt` rarely start. Runs self-chain in `gpu_debug` with bit-exact
   resume; do not change a frozen config.
4. When FINAL is complete: run the analyzer, write the confirmatory section of the report, regenerate the deck
   (`cd slides && python make_campaign_deck.py`, then `pytest test_deck_numbers.py`), run review round 2 on the
   FINAL/STRESS results, then the required records, the resource ledger (`python aggregate_resources.py`), the draft
   PR, and update this handoff. Resources: re-run `confirm/ledger_from_sacct.py` (command in its docstring), then
   `python aggregate_resources.py`.
5. Coverage runs only if amendment 2's condition holds (adequate at K* on FINAL **and** no "moves away" on an
   identifiable stress case).

## Known traps

- agy (Gemini) fabricated quotations and wrote placeholder results in this campaign — never merge an agy product
  without checking data hashes and quotes. Its code is often reusable.
- The engine's historical loader reads (and discards) real-data arrays; the confirmatory path does not (amendment 4).
- D5 numbers are the implemented variant, not amendment 1's operation order (amendment 4).
- Development results (DEV halves, pilot) must never be presented as confirmatory.
