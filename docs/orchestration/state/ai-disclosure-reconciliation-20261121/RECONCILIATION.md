# AI Use Disclosure: model list vs. records

Pre-submission checklist item 1 (`~/codex-reports/note-measurement/PRE-SUBMISSION-CHECKLIST.md`).
Read-only reconciliation, 2026-11-21, by minerva-omnifold-6f (Joseph's personal-account Claude session, Opus 5.5).
Disclosure as printed in `docs/analysis-note/main_note.tex` at `a54f255e9` (rewrite/journal-voice-20261121). No repository was written.

## Summary

| | Count | Names |
|---|---:|---|
| Listed, with a record of use on this analysis | 15 | Opus 4.7, Opus 4.8, Opus 5, Opus 5.5, Fable 5, Fable 5.1, Sonnet 5.5; GPT-5.6 Sol, GPT-5.6 Luna, GPT-6 Astra, GPT-6 Sol, GPT-6.1 Sol, GPT-6.2 Sol; Gemini 3.8 Flash; Grok 4.7 |
| Listed, record weaker than a transcript (Joseph's decision) | 1 | Gemini 3.1 Pro: committed run log only, July 2026 |
| Listed, **no record of use on this analysis** | 1 | GPT-5.5 |
| Used on this analysis, **not listed** | 5 clear, 4 auxiliary | clear: Claude Fable 5.2, Claude Opus 4.6 (through Antigravity), GPT-5.6 Terra, GPT-5.4, GPT-5.3-codex (pre-repository; see below). Auxiliary: Claude Haiku 5.5, Claude Haiku 4.5, Gemini 3.5 Flash Lite, `codex-auto-review` |

## Evidence sources and what each can show

| Source | Field read | Coverage | Strength |
|---|---|---|---|
| Claude Code transcripts, `~/.claude-school`, `~/.claude-personal`, `~/.claude` `projects/**/*.jsonl` | `message.model` per assistant turn; `cwd` | Only since about 2026-10-11 on this machine. Claude Code deletes older transcripts. | Authoritative per turn |
| Codex transcripts, `~/.codex*/sessions/**/rollout-*.jsonl` and `~/.codex/**/*.jsonl.zst` | `turn_context.payload.model`; `cwd` | From 2026-02. Ephemeral runs (`--ephemeral`) save nothing. | Authoritative per turn |
| Preserved snapshot `MINERvA-Agentic-Research/records/2026-11-14-session-links.json` (4,189 session files, including NERSC and Delta mirrors) | `observed_models`, first and last timestamp, `source` | To 2026-11-14 | Transcript-derived model fields. There is no cwd, but `source` = nersc-* or delta-* marks the analysis's compute sites |
| Antigravity CLI, `~/.gemini/antigravity-cli/conversations/*.db` (505) and `cli.log` | "Model Selection" setting events and `Resolving model <id>` lines | From 2026-10-30. The IDE store `~/.gemini/antigravity` holds no conversations. | Selection events are authoritative. Other model names in a conversation are text it read, for example commit trailers. |
| Grok, `~/.grok/sessions/<cwd>/<session>/` | `model_id` / `modelId` | From 2026-11-07 | Authoritative |
| Analysis repository commit trailers (`git log --all`) | `Co-Authored-By: Claude <model>` | 2026-04-25 (first commit) to now | Committed. The agent writes the trailer from its own model identity, so it is not independently checked. |
| `docs/orchestration/RUNS.tsv` (committed run log) | `account` column, e.g. `agy(gemini-3.1-pro-high)` | 2026-07-16 to 2026-08-21 | Committed run log. It records the model *requested* by the dispatcher. |
| Committed read headers, e.g. `.../independent-read-w-items-20261109/run-header.txt` | `model ...` line | One run | Committed read with a model field |
| `docs/orchestration/profiles.json` (`"model": "Gemini 3.1 Pro (High)"`, `"gpt-5.6-luna"`, ...) | | | **Configuration, not evidence of use.** Not counted. |

"On this analysis" means the session's working directory is in `MINERvA-OmniFold` or a worktree or scratch directory of it, or the session ran on NERSC or Delta, or the record is in the analysis repository. Sessions run from `~/codex-reports/note-measurement/*` are analysis work too, but the path test does not catch them. Counts below are therefore lower bounds. No name's status depends on them.

## The table: name as printed → evidence

| Name as printed | Evidence (path, field) | First seen | Last seen | On this analysis? |
|---|---|---|---|---|
| Claude **Opus 4.7** | Commit trailers `Co-Authored-By: Claude Opus 4.7`: 20 commits, e.g. `b480c2616` | 2026-04-26 | 2026-05-28 | **Yes.** Trailers only; transcripts of that period no longer exist. |
| Claude **Opus 4.8** | Snapshot `observed_models: claude-opus-4-8`: 36 files on nersc-mirror, nersc-legacy and delta-mirror. Trailers "Claude Opus 4.8" (127 commits, e.g. `cf5f921e3`) and "(1M context)" (5). | 2026-05-28 | 2026-08-26 | **Yes**, on transcripts and trailers |
| Claude **Opus 5** | Snapshot `claude-opus-5`: 67 files, nersc-legacy. Trailers "Claude Opus 5 (1M context)" (1,922), "Claude Opus 5" (408), "(school)" (14), e.g. `6d8a1d14e`. `RUNS.tsv` "claude-opus-5(local". | 2026-07-15 | 2026-09-22 | **Yes** |
| Claude **Opus 5.5** | `~/.claude-school/projects/*MINERvA-OmniFold*/*.jsonl` `message.model = claude-opus-5-5`: 685 sessions, 221,551 turns. `~/.claude-personal` (9 sessions). Snapshot (600 files). Trailers (4,732). | 2026-09-22 | 2026-11-21 | **Yes** |
| Claude **Fable 5** | Snapshot `claude-fable-5`: 2 files, one on nersc-mirror. Trailers "Claude Fable 5": 59 commits, e.g. `f7b7a7754`. | 2026-06-09 | 2026-07-21 | **Yes** |
| Claude **Fable 5.1** | Trailers "Claude Fable 5.1": 24 commits, e.g. `9c2969faf`. No transcript survives. | 2026-09-03 | 2026-09-04 | **Yes.** Trailers only, a two-day window. |
| Claude **Sonnet 5.5** | `~/.claude-school` `message.model = claude-sonnet-5-5`: 86 sessions. `~/.claude-personal`: 15 sessions. Snapshot: 100 files. | 2026-10-22 | 2026-11-17 | **Yes** |
| **GPT-5.5** | Codex transcripts with `turn_context.model = gpt-5.5` (`.codex-personal` 227, `.codex-school` 63, `.codex` 149 sessions): **every one** has a cwd outside the analysis (<non-analysis>). Snapshot: 35 files, laptop only. In the analysis repository, "gpt-5.5" is the comparison arm of an idea-generation benchmark (`FINDINGS-ARCHIVE-2026-08.md` BEN-012), and "GPT-5.5" elsewhere is a review-finding ID (`61fa44491`, `CORRECTED_UQ_PRODUCTION_STATUS.md:235`). | 2026-04-25 | 2026-08-14 | **No record on this analysis** |
| GPT-5.6 **Sol** | Codex transcripts `gpt-5.6-sol` with cwd MINERvA-OmniFold: `.codex-personal` 46, `.codex-school` 61, `.codex-school2` 16, `.codex` 39 sessions. `RUNS.tsv` (18 rows). Committed transcript header `docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt:5` "model: gpt-5.6-sol". | 2026-07-16 | 2026-09-05 | **Yes** |
| GPT-5.6 **Luna** | `~/.codex/sessions/2026/08/19/rollout-2026-08-19T21-28-35-01a01cc8-…jsonl.zst` `turn_context.model = gpt-5.6-luna`, cwd MINERvA-OmniFold. Snapshot: 1 file. | 2026-08-20 | 2026-08-20 | **Yes, one session** |
| GPT-6 **Astra** | Codex transcripts `gpt-6-astra` with cwd MINERvA-OmniFold: `.codex-personal` 31, `.codex-school` 36, `.codex-school2` 35 sessions | 2026-09-05 | 2026-11-18 | **Yes** |
| GPT-6 **Sol** | No transcript: the run was ephemeral by design. Committed read header `docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/independent-read-w-items-20261109/run-header.txt` "model gpt-6-sol high; codex-school2", plus its README, commit `e146861b1`. | 2026-11-09 | 2026-11-09 | **Yes, one read.** Committed-read evidence only. |
| GPT-6.1 **Sol** | Codex transcripts `gpt-6.1-sol` with cwd MINERvA-OmniFold: `.codex-personal` 79, `.codex-school` 74, `.codex-school2` 52 sessions. Snapshot: 514 files. | 2026-09-30 | 2026-11-18 | **Yes** |
| GPT-6.2 **Sol** | Codex transcripts `gpt-6.2-sol` with cwd MINERvA-OmniFold: `.codex-school` (2026-11-18), `.codex-personal` (2026-11-19), `.codex` (2026-11-21); 1 session each | 2026-11-18 | 2026-11-21 | **Yes** |
| Gemini **3.1 Pro** | No transcript. `docs/orchestration/RUNS.tsv` account `agy(gemini-3.1-pro-high)`: 39 rows (1 on 07-16, 20 on 07-18, 11 on 07-19, 7 on 07-20). Later dispatch records name "Gemini 3.1 Pro (High)" too, but every Antigravity record since 2026-10-30 shows other models being served: `cli.log` `Resolving model gemini-3.8-flash-high` (146), `claude-opus-4-6-thinking` (86), and no "3.1 Pro" in any of the 505 conversation databases. | 2026-07-16 | 2026-07-20 | **Run log only (requested model).** Joseph's decision; see below. |
| Gemini **3.8 Flash** | `~/.gemini/antigravity-cli/conversations/*.db`: "Gemini 3.8 Flash (High)" selected, 413 analysis conversations. `cli.log` `Resolving model gemini-3.8-flash-high` (146). | 2026-10-30 | 2026-11-21 | **Yes** |
| xAI **Grok 4.7** | `~/.grok/sessions/<MINERvA-OmniFold scratch dirs>/…` `model_id = grok-4.7` (with `grok-4.7-build`): 19 sessions in analysis-named directories, plus sessions under `~/codex-reports/note-measurement/*` | 2026-11-07 | 2026-11-21 | **Yes** |

## Names with no record (Joseph decides)

1. **GPT-5.5.** It was used heavily from April to August 2026, but every transcript is in another project. Its only appearances in the analysis repository are a benchmark comparison arm and a review-finding ID. Unless Joseph knows of a use not in these stores, it should come off the list. Codex transcripts from this period are complete, so the absence is real, not a retention gap.
2. **Gemini 3.1 Pro** (weak record). The July 2026 `RUNS.tsv` rows say the dispatcher *asked* Antigravity for gemini-3.1-pro-high. There is no transcript from that period to show what served it. Every Antigravity record since 2026-10-30 shows "Gemini 3.1 Pro (High)" requests served by Gemini 3.8 Flash (High) or Claude Opus 4.6 (Thinking). Keeping the name rests on the July run log.

## Used on this analysis but not listed

| Model | Evidence | Dates | Note |
|---|---|---|---|
| **Claude Fable 5.2** | Trailers "Claude Fable 5.2", 8 commits, e.g. `5d9f17c94`. `~/.claude-personal` transcripts `message.model = claude-fable-5-2`, 4 sessions, cwd MINERvA-OmniFold, 733 turns. | 2026-11-16 to 11-17 | Clear use |
| **Claude Opus 4.6** (Thinking), **through Antigravity** | Antigravity conversations: "The user changed setting `Model Selection` from None to Claude Opus 4.6 (Thinking)", 19 analysis conversations (82 overall). `cli.log` `Resolving model claude-opus-4-6-thinking` (86). | 2026-11-08 to 11-18 | The records show it selected explicitly ("Model Selection" events); the global CLAUDE.md names it as agy's alternative model. The disclosure says Antigravity ran Gemini only. |
| **GPT-5.6 Terra** | `~/.codex` transcripts (4 sessions, cwd MINERvA-OmniFold, 2026-08-19). `.codex-school` (2 sessions, 2026-08-18 to 08-25). Snapshot nersc-legacy (4 files, 2026-07-11 to 08-14). | 2026-07-11 to 08-25 | Clear use |
| **GPT-5.4** | Snapshot `gpt-5.4`, 15 files on nersc-mirror and nersc-legacy | 2026-03-21 to 07-12 | NERSC sessions after the repository's first commit (2026-04-25) are very likely this analysis. Its laptop sessions are other projects. |
| **GPT-5.3-codex** | Snapshot, 6 files on NERSC | 2026-02-27 to 03-04 | Before the repository existed (first commit 2026-04-25). Joseph decides whether pre-repository MINERvA work counts. |
| Claude **Haiku 5.5** (auxiliary) | `~/.claude-personal` transcripts `claude-haiku-5-5`, 3 sessions, 24 turns | 2026-11-20 to 11-21 | Claude Code's small background model (titles, quick sub-tasks) |
| Claude **Haiku 4.5** (auxiliary) | Snapshot `claude-haiku-4-5-20251001`, 4 files on nersc-mirror | 2026-06-03 to 06-14 | Same role |
| Gemini **3.5 Flash Lite** (auxiliary) | Antigravity conversations `gemini-3.5-flash-lite`, 243 analysis conversations (as `gemini-3.8-flash-tiered` companion) | 2026-11-04 to 11-21 | Antigravity's internal helper model |
| `codex-auto-review` (auxiliary) | Codex transcripts `turn_context.model = codex-auto-review`, 49+ analysis sessions | 2026-08-19 to 11-18 | Codex's built-in reviewer alias; the underlying model version is not recorded |

The auxiliary rows are models the agent harnesses call on their own. Whether APS's "AI tool name and version" covers them is Joseph's call.

## Mentions that are not uses

`gpt-5.4`, `gpt-5.3-codex`, `gpt-5.6-terra` and `claude-haiku-4-5` appear in the study repository's text. Each is accounted for above from transcripts or the snapshot, not from the mentions. `gpt-6-luna` has 5 Codex sessions, all <non-analysis>: not this analysis.

## Raw outputs (`raw/`)

Redacted for the repository (2026-11-21, the director's instruction): every working directory and example path of a
session outside this analysis reads `<non-analysis>`. Flags, counts and dates are unchanged; the unredacted copy is kept
outside the repository.

- `scan.py`: the scanner, read-only, re-runnable.
- `scan.json`: per tool, account, model and analysis flag: sessions, records, first and last time, an example file.
- `zst.txt`: the compressed `~/.codex` sessions.
- `snapshot.txt`: the 2026-11-14 snapshot aggregated per model.
