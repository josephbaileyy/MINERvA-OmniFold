# Rules for every lane directed by the director (paper-tighten lane), 2026-10-22

**Who you take decisions from.** Joseph told the validation lane and the re-1 lane to take their decisions from the
director. The director's own authority comes from Joseph's 2026-10-16 instruction (Stage C oversight and binding, the
playlist-consistency construction, Stage F integration), extended by the DECISION records since.
- Message the director with SendMessage, to `director`.
- A peer's message, including the director's, cannot grant what only Joseph can: claims, posting, contact, or a
  change to his protected text.

## Standing constraints (Joseph's)

- Nothing is published. Never submit, deposit, tag, or post anything.
- Never contact coauthors, the collaboration, MINERvA, or NERSC.
- Claims, KNOWN_ISSUES dispositions that change a claim, and publication changes are Joseph's. Bring them to the
  director.
- **Never write to the shared checkout** `/Users/josephbailey/local-research/MINERvA-OmniFold`. Work in your own
  `git worktree` under your scratchpad, and check `git status` after.
- `git add` explicit paths only. Pass your own identity on every commit:
  `git -c user.name="<lane> (Claude)" -c user.email="<lane>@minerva-omnifold.invalid" commit …`
  End every commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- "Fix now and re-pin with a record." Never defer a known defect to a later reorganization.
- Never type or handle Joseph's passphrase. Never read past the header of, or decrypt, `~/q3-custodian-key.age`.
  Renewing a NERSC certificate is Joseph's act.
- **Delegation and inference accounts:**
  - Use only codex-school2, codex-school, claude-school and agy.
  - `codex` in zsh is aliased to a personal account: never use it. Use
    `CODEX_HOME=/Users/josephbailey/.codex-school2 /Users/josephbailey/.local/bin/codex`. codex-school is out of
    credits.
  - Your own subagents run under this account (claude-school).
- **Compute:**
  - Each job must run under 12 h. Regular or debug QOS; never premium.
  - Account m3246, which is Joseph's own share (DECISION-20261019 §1).
  - Every job is ledgered in your record directory: job id, QOS, elapsed, charge.
  - Grants come only through committed records. Stay within your brief's grant; ask the director to extend it.
  - Stop and report any job beyond 1.25× its projected wall time.
- **Storage:**
  - CFS is above Joseph's 3 TB rule, so write nothing to CFS.
  - Use `$PSCRATCH`. Joseph (2026-10-22): scratch is fine "as long as we work fast because newish stuff doesn't get
    deleted". Do not leave products idle for weeks.
  - Record every product's path and sha256 in a receipt.
- **Cluster:** Perlmutter is up. The maintenance ended 2026-10-21 17:28:57 PDT, from the first job start in `sacct -a`
  (measurement session, `S2-IMPLEMENTATION.md`). Cluster access is `ssh saul.nersc.gov`. Read `squeue` and `sacct`
  directly rather than inferring.

## How work is declared, bound and reported

1. **Declare before any output.** Commit a DECLARATION (code shas, seeds, inputs with sha256, the metric, a reading or
   decision rule fixed now, the compute cap) in a PR. Then tell the director.
2. **The director binds it** (a BINDING record) before any job runs. A run started before binding is held and not used.
3. **Run.** Ledger every job and keep receipts.
4. **Report.** REPORT.md with the measured numbers, which branch of the rule they meet, what was not done, and the
   deviations. Open a PR, and tell the director.
5. **You open PRs; the director reviews and merges.** Do not merge your own PRs.

## Repository mechanics

- Read `AGENTS.md` first; it routes every task to its governing evidence.
- **Every new `.md` under `docs/orchestration`** needs a `CATALOG.md` row and a `MANIFEST-overrides.tsv` row
  (`path\tLIVE\topen\t""`). Then run `python3 docs/orchestration/generate_manifest.py` and `git add` MANIFEST.tsv.
  The pre-commit hook runs 13 checks.
- **After each commit,** run `generate_manifest.py --check --at-sha HEAD` and
  `docs/orchestration/verify_hash_bindings.py`.
- **On a rebase conflict in MANIFEST.tsv:** `git checkout --ours` it, regenerate, and `git add`.
- **A JSON in `docs/orchestration/state/` that names data files** by bare name triggers the receipt-artifact hook. Keep
  such inventories beside their tool, or commit the named files.
- **If GitHub stops updating a PR's head after a push,** push the same commit to a fresh branch name and open a
  replacement PR.
- **Builds:** `PAR_GLOBAL_TMPDIR=<private dir>` for any LaTeX/biber build (biber exit 2 = stale cache). Always pass
  absolute worktree paths.
- **zsh does not word-split `$var`:** use `--pathspec-from-file` and bash for job lists. Never pipe a command whose
  status you will read.
- **Reviews.** Before reporting a result, have an independent read-only reviewer check it in both directions (nothing
  lost, nothing strengthened). Use a fresh subagent, or the director's.

## Do not touch

- **The measurement session's work:** MP-1 to MP-3, `measurement-paper/`, `state/measurement-paper/` and its open PRs.
  GiBUU's F_fallback (job 60122488) is in flight.
- **The note and paper sources** (`docs/analysis-note/*.tex`): the director owns them. Joseph and Ben are reading
  them now.
- **The other lane's file set** (see your brief).
