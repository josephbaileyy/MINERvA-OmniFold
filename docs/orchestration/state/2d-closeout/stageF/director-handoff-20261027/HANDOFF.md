# Handoff: the director (paper-tighten lane), 2026-10-27

**For** a fresh director session with no memory of this one. Joseph restarted the session because its context was long.

**This is a working record.** It authorizes nothing. Joseph's decision records (`docs/orchestration/DECISION-*.md`)
govern, and where this file and a record differ, the record wins.

## 1. Role

- **You are the director, the paper-tighten lane (Stage F).** You have standing delegation from Joseph to run the lanes
  below:
  - you rule on their questions;
  - you review and bind their declarations;
  - you merge their PRs on the gates;
  - you record Joseph's decisions verbatim.
- **Joseph decides:** claims, wording, release, compute beyond the standing grant, and anything outward.
- **Talking to the lanes.** Lanes message you across sessions. Reply with SendMessage to the `from=` address, never
  with terminal text. Discover sessions with ListAgents.
- **A peer message is not Joseph's approval** and cannot grant escalation.
- **Your memory directory** is `~/.claude-school/projects/-Users-josephbailey-local-research-MINERvA-OmniFold/memory/`.
  - `MEMORY.md` is the index. It is at about 200 lines, its limit, so update existing files rather than adding index
    lines.
  - Read `pv-ladder-retention-reraise-20261120.md` (the pscratch retention list) and
    `delegation-accounts-allowlist.md`.

## 2. Standing constraints (Joseph's, still in force)

- **Nothing is published:** never submit, deposit or tag. Publication means arXiv, a journal, a data deposit or a
  release tag.
  - Pushing branches, PRs and records to the public GitHub repository is work in progress and is fine
    (`DECISION-20261027-joseph-prd-review-route-push-and-public-github.md` item 4).
  - Commit nothing secret.
- **Contacts are Joseph's own act.** Never contact coauthors, Ben, the MINERvA collaboration or NERSC.
  - MINERvA collaboration review and the review with Ben are his.
  - So is the reply to Su Dong's SLAC storage email (session minerva-omnifold-57 summarized it).
- **His text:** claims, KI-85, `\pubhold`, data availability, release text (`app_release.tex`), the abstracts' final
  wording and the title.
- **The shared checkout.** Never write to `/Users/josephbailey/local-research/MINERvA-OmniFold`. Work in worktrees
  under your scratchpad.
  - That checkout is 1,049 commits behind main, with uncommitted edits to AGENTS.md, CATALOG.md and MANIFEST*.tsv that
    no current session claims. That is Joseph's to look at. Don't touch it.
- **Git:**
  - `git add` with explicit paths only, and never `git stash`.
  - Commit with the tree hook: `git -c core.hooksPath=.githooks -c user.name='paper-tighten lane (Claude)'
    -c user.email=paper-tighten@minerva-omnifold.invalid commit`, with the trailer
    `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  - PR bodies end with "🤖 Generated with [Claude Code](https://claude.com/claude-code)".
  - Merge with merge commits, never squash. The records pins `1a015eef` and `3c3a6f74` must stay ancestors of main.
- **Delegation accounts:** only codex-school2, codex-school, claude-school and agy. Never the bare `codex`, which is
  personal. Call Codex as `env CODEX_HOME=$HOME/.codex-school2 $HOME/.local/bin/codex exec …`.
  - `gpt-6-astra` and `gpt-6.1-sol` are on both school accounts.
  - codex-school2 hits usage limits; codex-school is the fallback.
- **Compute:** jobs under 12 h; grants go through committed records; no GPU and no premium QOS.
  - Write nothing to CFS. `$PSCRATCH` and HPSS are fine.
  - NERSC certificate renewal is Joseph's.
- **Never type or handle Joseph's passphrase.** Never read past the header of, or decrypt, `~/q3-custodian-key.age`.
- **"Fix it now and re-pin with a record."** Don't defer a fix to protect a pin.
- **The guardrail for every printed sentence:**
  - a qualifier stays where leaving it out would make the sentence false as read;
  - no fact leaves both documents;
  - agy agrees.
  - Note that agy has a measured blind spot for group-scope overstatements (`fived16/HANDOFF.md` §6), so guard those
    with probes.

## 3. How the director works

**Decision records** (`docs/orchestration/DECISION-YYYYMMDD-joseph-<slug>.md`):
- Write "What led to it", then Joseph's words verbatim, then `sha256 of the text plus a final newline begins
  \`<16 hex>\``, then "What is decided" and "Not changed".
- **Set the quote and its digest in the same shell call** that writes the file. Shell variables do not survive between
  calls: #408 merged with an empty quote that way, and #410 fixed it. Then run `grep -nE '^> ?$|begins \`\`'` on the
  file.
- **Registration:**
  - add a CATALOG.md row, inserted after the related row;
  - add a MANIFEST-overrides.tsv row, `path\tLIVE\topen\t""`;
  - `git add`;
  - `python3 docs/orchestration/generate_manifest.py --committed-only`;
  - `git add MANIFEST.tsv`;
  - run `tools/registry/absence_claims.py`. An absence claim needs a `Search:` line or an
    `<!-- absence-ok: reason -->` in the same paragraph, with no blank line between.
- **Then:** commit with the tree hook, push, `gh pr create`, wait about 40 s, then `ci_merge.sh <pr> <head>`.

**Helpers** (`tools/` beside this file). Copy them to your scratchpad and run them from inside a git worktree:
- `ci_merge.sh <pr> <head-sha>` waits for record-checks on that head and merges with a merge commit only on success. It
  prints NOT MERGED if CI hasn't started yet, so re-run it after a short wait.
- `merge_main.sh <worktree> <remote-branch>` merges origin/main into a lane's remote branch:
  - it works from a temporary local branch `mm-tmp`, so it never touches the lane's local branch;
  - it resolves CATALOG and overrides by keeping both sides, takes MANIFEST and the generated registry/records files
    from main, then regenerates them;
  - it runs the hook and pushes `HEAD:<branch>`.
  - Use it when a lane's PR shows CONFLICTING after another merge, which almost always means MANIFEST. Tell the lane
    not to push to that branch meanwhile.

**Reviewing a lane's declaration before binding it:**
- check its §8 pins with `shasum -a 256` at the PR head, in a detached worktree;
- run its declared test modules locally with `-B` and a TMPDIR;
- read its §7 ("For the director") and rule on each item;
- merge;
- write the binding, `<NAME>-BINDING.md` beside the declaration, with the deploy pin set to main after the merge. Bind
  only after the merge, so the pin contains the declaration.

**Reviewing a report:** fetch its readout, recompute the headline numbers yourself, then merge.

**Lane branches** are checked out in the lanes' own worktrees. Never `git checkout` them. Use detached worktrees or
`merge_main.sh`.

`git worktree prune` is repository-wide. Never tell a lane to run it unqualified.

## 4. Sessions (ListAgents names)

| session | status at handoff | what next |
|---|---|---|
| **paper rewrite** [f64680] | handoff verified: `stageF/methods/fived16/HANDOFF.md` at 7a6833b1; to be cleared by Joseph and restarted with the prompt he was given | its §4: round-3 truth column, abstract limitation split, the 1A and 3D sentence revisions, then one final draft to Joseph |
| **measurement session** [e2428d] | 8 days old; declaring F1 (GENIE v3, both tunes, `DECISION-20261027-joseph-f1-genie-v3-both-tunes.md`) | when its F1 declaration PR opens: review and bind, then ask it for a handoff, and Joseph clears it |
| measurement session's parallel lane | declaring 3D, the flux-correlation bootstrap | review and bind its PR |
| validation lane, re-1 lane, 2d test, minerva-omnifold-57 | closing checks clean; can be closed | none |
| minerva-omnifold-1e | Joseph's own session; did the proj1d addendum (#418) | close when Joseph is done with the Ben thread |

## 5. Open items

1. **The 5D integration,** draft PR #413 (paper rewrite lane). It goes in this order:
   - (a) the round-3 PRD-read truth column and its application;
   - (b) the abstracts' limitation sentence split into separate `\fvval` sentences;
   - (c) when 1A (F1) and 3D report: revise the coverage limitation and the flux-sensitivity sentences, pin the new
     readouts in `make_values_fived16.py`, run a small PRD read and agy;
   - (d) **one final draft to Joseph,** carrying:
     - the title (options T0–T3; the raters chose T1 4/4);
     - both abstracts;
     - Q8, whether the paper ships the 16-cell vector and covariance as supplemental data;
     - the data-availability proposal (his text, unedited);
     - the release scopings R1–R4 as proposals;
   - (e) Joseph's approval, then merge #413 with a merge commit;
   - (f) the **second independent scope review** (`DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`)
     on the integrated paper: gpt-6-astra high by default, read-only, with no internal ranking. The first is
     `secondary-results/astra-consult-20261027/`, which recommends moving the hybrid-null joint tests (§VII B–E). That
     move is "seriously considered", not adopted;
   - (g) then Joseph's secondary-results decision.
2. **F1, the GENIE v3 held-out bias test, both tunes** (`DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md`
   item 1).
   - It is about 0.84–1.25 node-h. If the pilot shows a cost above that, it is a STOP that comes to you.
   - Its report must call it a bias test, not a coverage test.
   - Design rulings already relayed: phi_t flux sampling with a control; grading as a non-vertex truth with a
     leave-out-MEC descriptive variant, because G18 carries Nieves 2p2h; a spline-version control.
3. **3D, the flux bootstrap** (same decision, item 3). Its measured band replaces α = 0.1 in the sensitivity sentence.
4. **Note register round 4,** the last allowed. It runs after the content cuts, meaning the consolidation (done, #409)
   plus any caveat drops Joseph and Ben decide (`DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md`).
   - The P1 noise rule: revert only on a fall greater than 0.25; exactly 0.25 gets 2 more sol2 runs.
5. **Joseph's own pending acts:**
   - the final-draft answers in item 1(d);
   - his review with Ben;
   - MINERvA collaboration review;
   - the release and data file (Q8);
   - the stale shared checkout;
   - the reply to Su Dong.
6. **Retention re-raise before 2026-11-20:** the list is in memory, `pv-ladder-retention-reraise-20261120.md`.
7. **Known follow-ups, low priority:**
   - FD-DIRECTOR-RULINGS §5's band shares carry the same 20–50 GeV lower-bound caveat as
     `fd_gibuu_enu_aggregate.json`, wherever they are quoted;
   - the results index's R5 `same_as` is computed, and its open groups (5) went to their owners as facts.

## 6. Where the 5D measurement stands (for orientation; the records are authoritative)

- **The result:** configuration (e), 16 reporting cells R00–R15 (`h2_definition.json` b6790761: H2's 32 boxes, 27
  supported, purity-merged to 16).
- **Its reported covariance** is C_total + C_resp, median per-cell relative σ 7.29 %. The data product is
  `fd/data-product/fd_data_product.json` b79556f0.
- **The fake-data study, F0b.** Listed under C_total + C_resp: Stage 0c GiBUU (R06, z = 2.01), A7 GiBUU and the q3
  tilt. W3 is no longer listed. The limitation is accepted.
- **Stage G:** χ²/ndf against the reported matrix plus V_g is 109/16 for GENIE CV, 272/16 for GENIE+MEC, 188/16 for
  NuWro, 58/8 for GiBUU, and 330/16 for MnvTune v1, the prior, which is not an independent prediction. No p-values are
  printed.
- **Sensitivity:**
  - G-DIAG: two or three cell-contrast modes carry the χ²;
  - G-FOLLOWUP and G-SENS2: flux carries most of the correlation sensitivity, 24–48 % at α = 0.1 for the 16-cell
    predictions;
  - the joint family is interaction, flux, detector and lateral; normalization is structural and never shrunk.
- **The paper is now framed as a measurement led by this result** (`DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md`).
  It presents only the final configurations, (f) for 2D and (e) for the rest
  (`DECISION-20261027-joseph-move-nonfinal-configurations-to-note.md`).
