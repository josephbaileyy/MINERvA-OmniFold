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
9. **Independent review:** a fresh read-only Opus 5.5 subagent, in a detached worktree at `d9a75393`.
   - Cycle 1 returned **ACCEPT WITH CHANGES** (1 blocking, 6 should-fix, 12 notes); every finding was resolved.
   - Cycle 2, a focused re-check of `407c351f`, returned ACCEPT WITH CHANGES (1 should-fix, 5 notes); all were
     applied, without a third review.
   - The record is `REVIEW-20261005-independent.md`.

## 3. Remaining dependencies (owners keep their procedures and budgets)

- **D1: DONE.** AGREE 1379/1379 is at `466b427b` (recompute branch, report §8). The joint result is recorded on
  main at `9b26b8c3` (`RECORD-20261005-s5p-joint-5d-inference-result.md`): ten rejected, robust, "can change". Both
  workers notified `pub`, and this lane verified the committed files.
- **D2:** the lost-seed recovery. Procedure revision 5 is at `51648245`, and **Phase 0 PASS** is at `15a32b0e`, and the
  **determinism array 59397841** was submitted at `87256e75` (measured 2026-10-05T23:42Z). Still to come: the
  determinism verdict, the recovery, the resolution and the recompute cross-check.
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
  verdict, the recovered-seed cross-check, and any abandonment or disagreement. This commitment exists **only as a
  relayed message** and is not committed anywhere.

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

## 5. State after Joseph's 2026-10-06 approvals (`DECISION-20261006-joseph-publication-approvals.md`)

**Approved:**
- items 1–4 and 6: PRD article working target, with a PRX assessment due with the finished manuscript;
- the uncertainty-product prerequisite lifted for this article only;
- the headline hold;
- W1;
- W2a, with W2b automatic inside the 8 node-hour ceiling if review and costing pass;
- manuscript, figures, release preparation, builds and sync.

**Deferred:** item 5, the collaborator question.

**Done since then** (branch `docs/publication-decision-20261005`, pushed):

| item | commit / path | state |
|---|---|---|
| Approvals recorded verbatim | `827627d0` | — |
| Article draft 1 (PRD; paper sources converted from the Letter) | `ee9b8bee`: `docs/analysis-note/main_paper.tex`, `paper_body.tex`, new `values_inference.tex`, `publication.bib` | `build_all.sh` PASS (note 114 / primer 7 / article 7 pp), also from a cold tree. Six red `\pubhold{}` markers remain: abstract, results interpretation plus W1, lost seeds, W2, conclusions, data availability. |
| Recovery interpretation framework (D3) | `RECOVERY-INTERPRETATION-20261006.md` (`078d1f9d`) | Fixed before any recovered outcome was seen. Classes R1–R4 and X, each with wording and a proposed disposition. |
| Release tooling | `publication/release/` (`10f63ade`) | extract (frozen code) plus a standalone replay; 5 equivalence tests pass, and 2 mutations are caught. |
| Release replay | `docs/publication/release/RECEIPT-20261006-inference-sufficient-frozen.json` (`02c7684b`) | The 7.1 MB npz (`7bd019c6…`, on `/pscratch/sd/j/josephrb/pub-release-20261006/frozen/`) replays `joint-evaluate.json` with **AGREE, 0 differences**, on the cluster and on macOS. |
| W1 code (not run) | `publication/w1/` (`120ec68d`) | Runs after D1 and D2; the criterion is applied after D3. |
| W2a | branch `study/w2-recoil-response-20261006`, worktree `../MINERvA-OmniFold-w2-recoil` | Forked implementation lane running. It returns a report (`docs/publication/w2/W2A-REPORT-20261006.md` on its branch). This lane then launches a **fresh independent reviewer**. |

**Coordination agreed with `gbdt worker`** (recorded on main at `4e7c20bb`):
- that lane owns the Stage-7 s5p text in the note and primer and the four fields;
- this lane owns `main_paper.tex` and `paper_body.tex`;
- shared files get new entries only, announced both ways;
- the paper sync is this lane's; the note sync is coordinated;
- before editing note sources outside the paper, tell the note-organization lane (`minerva-omnifold-bf`).

Stage 7 starts after D2 and D3, on `docs/s5p-stage7-20261006`.

## 6. Next action

1. **On the W2a report:** check the cost gate, then launch one fresh read-only reviewer of the W2a code and report.
   W2b proceeds only if the review clears **and** measured W2a + W2b ≤ 8 CPU node-hours, and only after D2.
2. **On D2** (resolution report plus the recompute §6 cross-check):
   - extract the recovery group(s) with `extract_inference_sufficient.py` (readings (a) and (b));
   - classify with `RECOVERY-INTERPRETATION-20261006.md`;
   - bring Joseph the class, the table, the wording and a one-sentence D3 proposal.
3. **After D3:** run W1, then apply its criterion. Fill the article's holds from D2–D4 and W1/W2.
4. **Then:**
   - a release candidate with an independent empty-checkout replay;
   - the PRX assessment;
   - the standalone-repo paper sync, coordinated with `gbdt worker`;
   - the submission package for Joseph.

   Deposit, tag and submission stay unauthorized.
5. **Standalone note-repo sync owed** (fold into the next sync coordinated with `gbdt worker`): this branch's
   article sources, and main's PR #21 PET note corrections (`2fb6f035`; `sec_pet_campaigns.tex`,
   `PET_STUDY_SYNTHESIS.md`, one `sec_execsummary.tex` phrase). The note-organization lane `minerva-omnifold-bf`
   is no longer a live session, so PR bodies serve as its notice.
6. **2D statistical band (KI-84):** a candidate rebuilt band exists (PR #22, main `fd64f737`, VL170). It is
   **not adopted** and no quoted value changed; per-bin σ ratio median 1.179, √tr C ratio 1.063; no rollup or
   coverage re-test. The article keeps the VL162/VL169 wording. If Joseph adopts the rebuilt band, update the
   article's 2D-uncertainty paragraph (and the 6.87% median only if the rollup is rebuilt).
7. **W2a** done (branch `study/w2-recoil-response-20261006` at `35241cbd`; measured 0.0985 node-h; projected
   W2a+W2b 2.5-3.1, ≤ 6.2 with retry: cost gate GO). An independent read-only review (detached worktree
   `../MINERvA-OmniFold-w2-review`) is running. W2b runs only if it CLEARS and after D2's cross-check.
8. **D2 progress:** resolution recorded (`11a266c6`, `RECORD-20261006-s5p-lost-seed-recovery-resolution.md`):
   every decision unchanged under (a), (b) and the earliest stops; PENDING the recompute lane's §6 cross-check.
   This lane's replay of `resolved-evaluate.json` from the recovery-union extract AGREEs (receipt `000cd276`),
   which is a consistency check, not the §6 cross-check.
9. **W1 done** (`22a004e7`; independent reproduction 40/40 exact, `09718448`): no prediction qualifies; the
   joint-information claim is omitted (terminal). The article states the outcome (`d91db17b`).
10. **W2 done** (branch `study/w2-recoil-response-20261006` at `940d84aa`; report `publication/w2/W2B-REPORT-20261006.md`):
    the δ = 0 control PASS via fallback (not bitwise); **all 10 rejections robust at ±4%** (NuWro shape k 1 → 3 at
    +4%, p 0.0023 against 0.05); spend **1.9967 of 8.0** CPU node-h, no retries. The independent check by the
    recompute lane (per-copy files sent, 12 digests verified) is PENDING. Fill the article's W2 `\pubhold` only
    after it AGREEs. Merge the W2 branch into the publication branch at integration.
11. **D3** (Joseph's disposition of the recovery, class R1, `cd810761`) is requested. `gbdt worker` is asking with
    the same sentence. Then D4 (Stage-7 wording) follows.
12. **Discovery route:** when this branch is integrated, add a `docs/publication/` row to the `AGENTS.md` evidence
   routes.
