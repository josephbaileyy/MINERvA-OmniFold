# Handoff: publication preparation lane (2026-10-05)

**CITABLE FOR:** what this lane completed, where its evidence is, what it waits on, how it is notified, and the
next action.
**NOT CITABLE FOR:** any physics result or authorization. The scientific content is in
`PACKET-20261005-publication-decision.md` and its companions.

## 1. Identity and scope

| | |
|---|---|
| session | `pub` (Claude Code, Opus 5.5) |
| worktree | `/Users/josephbailey/local-research/MINERvA-OmniFold-publication-20261005` |
| branch | `docs/publication-decision-20261005`, created from `origin/main` `895a622c` and fast-forwarded to `61cad10d` before its first commit |
| authority | Joseph, 2026-10-05. It covers the decision packet, routine local analysis of existing products within their contracts, literature research, and one fresh independent read-only review. **It does not cover** new cluster compute, adoption, public deposit, release tag, external messages to coauthors, or submission. |
| files written | `docs/publication/` only. No `docs/analysis-note/`, `docs/orchestration/`, campaign worktree, product, procedure or budget was touched. |

## 2. Completed

1. **Baseline measured.** `origin/main` was at `895a622c`, then `61cad10d`; the shared checkout's local `main`
   (`3ea5f06a`) was 548 commits behind `895a622c` (`git rev-list --count`). The fresh worktree is the base.
2. **Governing records read:**
   - `AGENTS.md` and `CAMPAIGN-REVIEW-20260929.md`;
   - the PLAN (copied here; sha256 `c8b950d6…`);
   - the s5p terminal record, `DECISION-20261005`, the procedure (revisions 3 and 4), `CHECKLIST-20261001`,
     amendment 7, the independent-recompute final report (`02df81e6`), and the 2D coverage outcome (`80862878`);
   - the 09-01 and 09-19 rulings, the 09-26 authorization, the Letter source, the release appendix and package,
     and the reproduction harness.
3. **Literature comparison**, with the load-bearing quotes re-verified against the source text:
   `LITERATURE-20261005-comparison.md`.
4. **Claim-to-evidence table:** `CLAIMS-20261005-claim-to-evidence.md`. It has 9 inference claims and 13 Letter
   claims, and §C holds the derived descriptive distances.
5. **Manuscript outline**, for the recommended article and the conditional Letter:
   `OUTLINE-20261005-manuscript.md`.
6. **Release inventory:** `RELEASE-INVENTORY-20261005.md`. It found two corrections owed (the access sentence and
   the open-data citation) and one provenance gap (the design does not pin a digest for `data_central`).
7. **Decision packet**, with its recommendation, the four questions, W1 and W2 proposed with caps, criteria and
   terminal rules, and the batched approval wording: `PACKET-20261005-publication-decision.md`.
8. **Notification channel verified** (§4).
9. **Independent review:** `REVIEW-20261005-independent.md`, which records the cycles and their resolution.

## 3. Remaining dependencies (owners keep their procedures and budgets)

- **D1:** the extended comparer is reviewed, compare returns AGREE, and the joint result is recorded.
- **D2:** the lost-seed recovery runs (procedure revision 4 at `61cad10d`; nothing submitted), the resolution is
  reported, and the recompute cross-check is done.
- **D3:** Joseph's disposition of the resolution.
- **D4:** the Stage-7 approved wording and the four final fields.
- **D5:** the 2D coverage branch is merged into main.
- **Joseph's decisions in packet §7**, (1) to (6).

Without (1), every route is a **scientific hold**, which is a legitimate terminal result for this effort.

## 4. Notification channel and fallback check

**Primary channel (verified 2026-10-05):** cross-session `SendMessage` to `pub`.
- `gbdt worker` (the s5p owner) acknowledged that it will send one line (sha plus record path) for each of D1, D2,
  D3 and D4, and will report abandonment, for example a determinism FAIL. It also recorded the commitment in
  `campaign-state.json` incidents (commit `1aa9c121`).
- `gbdt independent` (the recompute lane) acknowledged that it will report the extension review and compare
  verdict, the recovered-seed cross-check, and any abandonment or disagreement.

**Fallback, bounded and read-only.** These are existing files; no new tooling was built. Run from this worktree:

```sh
git fetch -q origin
git show origin/main:docs/orchestration/state/s5p/campaign-state.json | python3 -c 'import json,sys;d=json.load(sys.stdin);print("phase:",d["phase"]);[print(i["utc"],i["what"][:200]) for i in d["incidents"][-5:]]'
git log --oneline -5 origin/s5p-parallel-recompute-20260928
git merge-base --is-ancestor origin/study/2d-coverage-test-20261005 origin/main && echo "D5 merged" || echo "D5 not merged"
```

**Operating limits:**
- It sees only **pushed** commits. A result held in a peer's uncommitted tree, or relayed in a message, is not
  quotable (`AGENTS.md`) and is invisible here.
- It reads the s5p state from `origin/main` (the s5p lane pushes there directly) and the recompute state from its
  branch tip. A record on another branch would be missed.
- The recompute lane names the STATUS block of `HANDOFF-20260928-s5p-recompute.md` on its branch as its poll
  point. This command shows only the commit subjects; open the file for the state.
- Incident text is truncated at 200 characters. Open the record before acting.
- It is a manual check run when a session resumes. No scheduler or loop was created. Suggested cadence: at
  session start, and no more than daily while D2 runs (a day or more per the owner decision).
- Notifications travel between live sessions only. If a peer session ends, its notification commitment ends with
  it, and the fallback becomes the only route.

## 5. Next action

1. **Joseph:** answer packet §7 (one batch).
2. **This lane, on notification of D1–D4:**
   - re-measure the records;
   - fill packet §5.2 and the claims-table rows I1–I4 from the **recorded** result, not the pending outputs;
   - apply the D3 disposition to the wording;
   - re-assess route A against W1 and W2 if those were authorized and run;
   - finalize the headline.
3. **If (1) and (6) are approved:**
   - draft the article in an isolated branch from current main, coordinating with the note owners. The GBDT
     model-dependence lane (`analysis/gbdt-model-dependence-20261003`) also edits the note;
   - apply the corrections owed: `paper_body.tex:61` "coverage is untested", the open-data DOI and acknowledgment,
     and the `app_release.tex:32–35` access sentence;
   - build and synchronize both repositories per PLAN §8.
4. **Discovery route:** when this branch is integrated into main, add a row for `docs/publication/` to the
   `AGENTS.md` evidence routes. That front-door edit was not made here, because it is shared state.
