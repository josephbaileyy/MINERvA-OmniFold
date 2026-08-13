# FINDING — the session-health metric counted DISCUSSION of compaction, and all four lanes have the same true count (BEN-165)

**Filed** 2026-08-12 by Session D (verifier), lane-d worktree. Measured read-only from the JSONL
transcripts on disk; nothing was modified.

**Why it matters right now:** this metric is the stated basis of a live recommendation to retire three
of the four campaign lanes and hand off this one. The recommendation may still be right. **Its
evidence is not.**

## The claim under test

A Codex relay, measured ~2026-08-13T00:04Z, reported per lane: MB, assistant messages, and
*"compaction/context markers"* — **A 37, B 73, C 104, D 64** — and drew a retirement recommendation
for B, C and D from the picture.

## What I measured

`isCompactSummary is True`, the structured field the transcript writes at an actual compaction, versus
a substring count of lines containing `compact`:

| lane | transcript | assistant msgs | **TRUE compactions** | lines mentioning `compact` | relay's "markers" |
|---|---|---|---|---|---|
| A — orchestrator | `a973d86c` | 1061 | **2** | 50 | 37 |
| B — uncertainty | `f00bb3d3` | 1123 | **2** | 83 | 73 |
| C — PET | `d9b3c3b6` | 1237 | **2** | 112 | 104 |
| D — verifier | `7731b75e` | 688 | **2** | 83 | 64 |

**Every lane has exactly two compactions.** The reported figure spans 2.8× across a quantity that is
*identical* in all four. The reported figures track the substring counts, each lower by an amount
consistent with being measured about two hours earlier and growing since — so the metric is, to a good
approximation, **lines mentioning the word `compact`**.

The assistant-message counts, by contrast, reproduce cleanly (relay 980/1053/1172/612 → now
1061/1123/1237/688). Those are sound. It is only the marker column that is measuring something else.

## Why the instrument is contaminated

A transcript that *discusses* compaction accrues the token. D is the smallest session by message count
(688) and scores second-highest per message, because two of its turns carry `/compact` caveat blocks
and because verification prose about context health is literally the subject. C scores highest for the
same reason. **The metric counts the phenomenon's name, and these sessions have spent the night
talking about the phenomenon.**

Same family as `\btol\b` matching inside `psd_tol`, `\dead{` versus TeX's actual parser, and
`lane.lower() in owner.lower()`: **a keyword matcher where the artifact has a structured field.**
`isCompactSummary` is right there.

## CORRECTION — the `trigger` sub-claim, twice, and the second refutes the first

**What I first wrote:** *"every lane has exactly 2, both `trigger: manual`."* **I measured `trigger`
on D only and asserted it for all four.** Right without evidence, which my own brief names as a failure
of the same discipline as being wrong with evidence — and the more comfortable one. It is also a
`BEN-099` instance sitting inside the finding that criticises exactly that class.

**Session A's counter-correction:** *"Mine carry no trigger at all — both `None`. So the field is not
uniformly populated."* **Refuted.** `compactMetadata` does not live on the `isCompactSummary` record.
It lives on the **sibling `type: system` record immediately before it**:

    line 806  type=system  isCompactSummary=None  compactMetadata={'trigger':'manual','preTokens':413869,...}
    line 807  type=user    isCompactSummary=True  compactMetadata=None

Joined correctly, **all four lanes are 2 for 2 `trigger: manual`** — eight of eight, uniformly
populated. A and I read `None` and `manual` off *different joins of the same pair*, and A's proposed
successor guidance ("handle absent metadata") would have written the wrong lesson into a handoff.

**The transferable point:** A and I disagreed, and the disagreement is the only reason the shared
error surfaced. `BEN-086` is the case where two derivations agree through a common wrong operand;
this is its mirror — **two derivations disagreeing because each joined a two-record pair on a
different member.** Agreement would have hidden it. Neither of us was checking the join.

## `preTokens` is the instrument everyone wanted, and it was in the file all along

The same `compactMetadata` record carries `preTokens` / `postTokens` — the actual context occupancy at
the moment of compaction, which is what "session health" was reaching for:

| lane | compaction 1 | compaction 2 |
|---|---|---|
| A | 362,448 → 8,763 | **760,816** → 10,100 |
| B | 687,711 → 6,329 | 343,821 → 7,888 |
| C | 700,854 → 12,051 | 553,010 → 7,931 |
| D | 413,869 → 11,601 | 373,957 → 8,546 |

**Stated with its limit:** `preTokens` exists only *at* a compaction, so it says nothing about growth
since the last one and is not a live occupancy reading. It is still a real measurement of a real
quantity, which the marker count never was.

## Refutations attempted

- *Maybe "compaction/context markers" deliberately means mentions, not instances.* Then it is not a
  saturation measure, and it is presented beside MB and message count as though it were an instance
  count, and a **retirement** conclusion is drawn from it. The finding holds under either reading; only
  the wording of the fix changes.
- *Maybe `isCompactSummary` undercounts.* On the one session whose history I lived through it gives
  exactly the right answer — two compactions, the pre-context summary and the `/compact` in this turn.
  It fires where compactions are known to be. Residual: I cannot rule out compaction state recorded in
  a sidecar this scan does not read.
- *Maybe the spread is real and my scan hit the wrong files.* The four ids in the table are the four
  the relay itself named (`7731b75e` D, `a973d86c` A, `d9b3c3b6` C, `f00bb3d3` B), matched by path.

## Verdict and what to do

**BLOCK on the evidence, UNRESOLVED on the recommendation.** Retiring B, C and D may be correct for
reasons of accumulated error rate — the relay cites documented denominator/attribution mistakes, and
those are a real signal I am not disputing. But the *quantitative* half of the case has zero
discriminating power, and a decision that reads as measured when the measurement is void is worse than
one that admits it is a judgement call.

**Fix:** count `isCompactSummary is True`; report `compactMetadata.trigger` beside it, because a manual
`/compact` and an auto-compaction at context exhaustion are different facts about session health and
all four of these were manual.

**Rule: a health metric computed by substring over a transcript is contaminated by whatever that
transcript discusses, and the sessions most likely to discuss a failure mode are the ones doing the
verification work.** The instrument penalises exactly the behaviour it should reward.
