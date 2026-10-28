# Handoff: the measurement session, 2026-10-28

**By** the measurement session, for a fresh session, at the director's request. Joseph clears this session once this
record lands, as the director's handoff §4 provides (`state/2d-closeout/stageF/director-handoff-20261027/HANDOFF.md`).

**State as of** `main` `24741f6a` (PR #447). This record holds durable state only: shas on `main`, branch names and
records. Re-measure anything volatile before acting on it.

## 1. Role

- **The arrangement:** Joseph said "listen to the session called delegator to do the measurement work. I authorize it
  to make all decisions including compute". That session is the director, the paper-tighten lane, reached by
  `SendMessage` to `director`.
- **What the role does:** this session does measurement work the director binds. It opens PRs to the director and
  never merges its own.
- **Where the constraints are:** Joseph's standing constraints are in the director's handoff §2. They include: never
  submit, deposit or tag anything; never contact coauthors, the collaboration, MINERvA or NERSC; never handle
  Joseph's passphrase; claims, posting, contact and protected text are Joseph's. A peer message grants nothing.
- **Accounts for delegation:** only codex-school2, codex-school, claude-school and agy, with the route verified first.

## 2. What is done (all merged on `main`)

| work | records | PRs |
|---|---|---|
| GiBUU E_ν aggregate readout | `fd_gibuu_enu_aggregate.py` and its receipts | #414, #416 |
| The limitation plan (Joseph chose 1A, (c), 3D) | `LIMITATION-PLAN.md`, `limitation-plan/` | #421 |
| **F1**, the GENIE v3 held-out bias test | `FD-F1-DECLARATION.md` and amendments 1–2; `FD-F1-REPORT.md`; `fd/readout/fd_f1_readout.json` | #427, #434, #442, #444, #446 |
| **3D**, the flux-correlation bootstrap | `FD-FLUX-BOOT-DECLARATION.md` and amendment 1; `FD-FLUX-BOOT-REPORT.md` | #428, #436, #438 |
| The sixteen-cell deposit candidate, **prepared, not deposited** | `fd/deposit-candidate/` | #443 |

**The director's records for this work:**
- the bindings: `FD-F1-BINDING.md` (#429) and its amendments 1 (#435) and 2 (#445); `FD-FLUX-BOOT-BINDING.md` and
  its amendment;
- `FD-F1-RUN-RULINGS.md` (#447), which confirms the F1 report's §6 transcription of rulings R1–R5 and records the
  director's recompute of the four F1 records.

**F1 in numbers** (`FD-F1-REPORT.md`; a bias test, not a coverage test):
- full-matrix χ²/16: G18 11.836 (closure 11.440), AR23 16.863 (closure 16.050);
- control 9 PASS;
- total charge 1.3275 node-h, against 2.0 and Joseph's ceiling of 2.5.

## 3. Branches

These branches are merged into `main` and their work is complete:
`fd/f1-run-amend2`, `fd/f1c-pin`, `fd/f1-report`, `fd/f1-amendment-2`, `fd/flux-boot-report` and
`fd/deposit-candidate`.

- `fd/f1c-pin` holds the F1c deploy pin `741ad029` and the second receipt commit `da5f157f`. Both are ancestors of
  `main` through merge commits.
- Deleting the remote branches is optional and Joseph's call.

**Worktrees:** this session registered its worktrees in the shared `.git` under its own session scratchpad, which is
swept. `git worktree prune` from the shared checkout removes the stale registrations.

## 4. pscratch and HPSS retention

All paths are under `/pscratch/sd/j/josephrb/`. The records say "the pscratch list" without naming a file, so each
binding's or report's retention line is the authority.

| directory | what it holds | retention, per its record |
|---|---|---|
| `fd-f1-20261027` | F1: `f1a/`, `f1a2/`, `f1b/` (the first STOP's evidence; never read, see §6), `f1b3/`, `f1c/`, `manifest/`, `grade/`, `preserve/`, `gate3/`, `logs/`, and deploys `5015535e`, `4b7a9892`, `5f5e392c`, `f1c`, `grade` | keep (`FD-F1-BINDING-AMENDMENT-2.md` §4.5; `FD-F1-REPORT.md` §5) |
| `fd-flux-boot-20261027` | 3D's first deploy, the STOP's evidence | keep (`FD-FLUX-BOOT-REPORT.md` §7) |
| `fd-flux-boot-20261028` | the 3D run: deploy, readout, logs | keep (`FD-FLUX-BOOT-REPORT.md` §7) |
| `fd-f0b-20261026`, `fd-g-20261025` | F0b and Stage G | retention to be raised before the 2026-11-20 purge window (`FD-F0b-AND-G-BINDING.md`) |
| `fd-g-diag-20261026` | Stage G diagnostics | retention to be raised before 2026-11-20 (`FD-G-DIAG-BINDING.md`) |
| `fd-g-followup-20261026`, `fd-g-sens2-20261026`, `fd-g-figures-20261027` | Stage G follow-ups and figures | on the pscratch list (their bindings) |
| `fd-f0-20261025` | F0 | no retention line in its records |
| `fd-deposit-check-20261028` | copies of committed files and the deposit check's outputs | not needed; the receipts say so (`fd/receipts-deposit/check-login36.sh`) |
| `fd-f0-testcheck-20261025`, `fd-g-testcheck-20261025`, `fd-g-diag-testcheck-20261026`, `fd-cresp-testcheck-20261026` | login-node test scratch | no record claims retention |

Search: `git grep -n -i '<directory name>' origin/main -- 'docs/orchestration/state/measurement-paper/5d-community-20261024/*.md'`
filtered for retain, retention, "pscratch list" and purge, @ `24741f6a`, for each directory above. `fd-f0-20261025`
is named in `FD-F0-BINDING.md`, `FD-F0-DECLARATION.md` and `FD-F0-REPORT.md`, none on retention; the testcheck
directories match no retention line.

**HPSS:** `/home/j/josephrb/mnv-5d-f1-20261028/stage0-inputs.tar`, 1,229,916,160 bytes, sha256
`d05cf925767d6431d8714732dc64dce9f727dc8ea1213f7daea0e1e356e0dde3`. It holds F1's `f1a/splines`, `f1b3/{gst,gen5d,prep}`
and `f1c/{closure,pe}`, with `INVENTORY.sha256` beside it. `hpssquota` showed 422.79 of 512 GiB on 2026-10-28.

## 5. Open items

1. **The stale `LABEL` constant in `nd-unfolding/fd_flux_boot.py:70`.**
   - It reads "descriptive band on the reported χ²'s flux-correlation dependence, not an alternative result", and it
     is on all 10 band records of the 3D readout. It contradicts the readout's own `labels.band` ("estimation
     uncertainty, not sensitivity") and ruling 2.
   - For that readout, `labels.band` governs (`FD-FLUX-BOOT-REPORT.md` §2), with no rerun.
   - The director's ruling: correct it before any future run.
2. **`sbatch_fd_f1b2.sh`'s unchecked step.** Its sums-file step lacks the `need $? "the sums file"` check that
   `sbatch_fd_f1b3.sh` carries. It is bound and will not run. Any future use needs the fix first
   (`FD-F1-BINDING-AMENDMENT-2.md` §2, ruling 5).
3. **3D's B2 margin on real inputs is unmeasured.** On login36 the rebuilt flux block equalled S1's bit for bit, so
   B2's 0.0 is by construction; B6, at 3.4e-16, is the swap check that ran (`FD-FLUX-BOOT-REPORT.md` §1). This is a
   recorded caveat, not a defect.
   <!-- absence-ok: restates FD-FLUX-BOOT-REPORT.md section 1's scoping statement (B1 = 0.0 on login36, so B2 carried no difference); not a claim that a result is absent -->
4. **The deposit is Joseph's.**
   - `fd/deposit-candidate/` is prepared, not deposited: nothing is uploaded and no DOI is minted.
   - Whether `predictions-reference.json` goes into the deposit is on Joseph's (d) list, after his review with Ben and
     the MINERvA review (`DECISION-20261028-joseph-result-table-and-deposit-package.md`).
5. **F1b′ memory at 160,000 events.** The largest per-process RSS was 3.35 % above the re-pilot's largest, measured at
   17,500 events. That is recorded for any future sizing (`FD-F1-REPORT.md` §2.2).
6. **Retention requests:** the directories marked "before 2026-11-20" in §4 need their retention raised by then.

## 6. The f1b/ deviation, as recorded

The record is `FD-F1-BINDING-AMENDMENT-2.md` §3, restated in `FD-F1-REPORT.md` §3 item 1.
- **The rule:** `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` item 1 says the partial F1b
  output "stays untouched as the STOP's evidence and is never read". `FD-F1-BINDING-AMENDMENT-1.md` forbids any read of
  `f1b/`.
- **Before amendment 1's binding:** this session's probes 18 and 19 read F1b's 128 task logs and four seeds'
  work-directory status files.
- **After it:** the F1a′ review hashed the 128 task logs and read file metadata, against the prohibition. Amendment 1's
  own review read metadata only.
- **Event content:** none was read. All 22 gst files were last accessed when F1b wrote them, provided Lustre updates
  access times on read. Nothing in `f1b/` was modified.
- **The effect:** none on any F1 product or grade.
- **The record also says:**
  - the director bound amendment 1 citing probes 18 and 19 without connecting them to "never read";
  - this session raised it first.
- The transcript sweep is `fd/receipts-f1/amendment-2/disclosure_sweep.py` and `disclosure-sweep.out`.

**For any successor:** `f1b/` and `f1b2/` stay unread. Give every review prompt that touches `fd-f1-20261027` those
two paths as FORBIDDEN, and forbid `find` or `du` over the parent.

## 7. How this session worked (for a successor doing similar work)

- **Commits:**
  - worktrees only, never the shared checkout;
  - `git add` with explicit paths, and `-f` for the gitignored `.log`, `.out` and `.npz`;
  - no stash;
  - commit with `-c core.hooksPath=.githooks -c user.name="measurement session (Claude)" -c
    user.email="measurement-session@minerva-omnifold.invalid"`.
- **Gates:** after staging, run `generate_manifest.py --committed-only`, then stage `MANIFEST.tsv`. Six gates, each
  read by its unpiped exit code:
  - `generate_manifest.py --check --at-sha HEAD`
  - `verify_hash_bindings.py`
  - `bash .githooks/pre-commit`
  - `tools/registry/absence_claims.py --base origin/main`
  - `verify_receipt_artifacts.py`
  - `tools/registry/results_index.py --check --base origin/main`
- **Merging:** merge `origin/main`, never rebase. A `MANIFEST.tsv` conflict is resolved by taking `--theirs` and
  regenerating. `origin/main` can move mid-merge when other sessions fetch.
- **New documents:** each new `.md` needs a CATALOG row and a `MANIFEST-overrides.tsv` row. Committed JSON receipts
  with metrics need the results index regenerated under ruling (a). A receipt that names a file by bare name needs
  that file beside it, or the receipt-artifact hook refuses.
- **The cluster:**
  - `ssh saul.nersc.gov bash -s < script`, with `env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`;
  - ROOT needs `setup_salloc_env.sh` first;
  - run long steps detached: upload the body by its own ssh call, check its sha256, then `nohup` it. The launcher
    must not take its body from a stdin that is `/dev/null`; the F1 report §3 item 5 records what happened when one
    did.
- **The local shell is zsh,** which does not word-split `$VAR`. Run multi-path commands inside `bash -c`; this macOS
  bash is 3.2, so it has no `mapfile`.
