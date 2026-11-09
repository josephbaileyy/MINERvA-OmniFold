# The sixth methods referee round: JINST, the short methods paper's placeholder draft, paper plus Supplement, 2026-11-09

**What was read:** `draft/methods-short-20261109` (#977) at `e3b99c82b`. It is unmerged, and no wording is approved.
Under `DECISION-20261109-joseph-placeholder-draft-reads.md`, the pending results print as "[PENDING: ...]". There are
eight such strings in the manuscript.

**The rater copies,** built by the lane's committed scripts and copied here byte for byte:
- `manuscript-short-r6.blind.txt`: 8,463 words, sha256 `0fef2e44a57cfdd7…`;
- `supplement-short-r6.blind.txt`: 13,516 words, sha256 `1c5fa5bea686f1d1…`.

**Procedure:** as round 5's JINST arm (`../referee-methods-round5-20261109/README.md`), with one change. The prompt
(`referee-prompt-jinst-r6.txt`) is round 5's JINST prompt plus one sentence after the Ref. [14] sentence: the pending
results print as placeholders; judge the paper as if each could come out either way; do not penalize a placeholder
itself, but say where the claims or structure depend on its outcome.
- **Sonnet:** two separate `claude -p --model sonnet --strict-mcp-config --tools "" --disable-slash-commands` calls,
  under `CLAUDE_CONFIG_DIR=~/.claude-school`, with the whole input on stdin.
- **Gemini:** two `agy --sandbox --model gemini-3.8-flash-high -p` calls, the input prefixed with `gemini-preamble.txt`.
- Each read ran from its own empty directory, which was still empty afterwards. All four exited 0 with empty stderr.
  `run.sh.txt` is the script.

**Comparability:** the venue is JINST only, the draft is new (shortened and restructured), and the prompt has the
placeholder sentence. So round 6 is not strictly comparable with round 5.

## Scores (JINST publishability, 1–10)

| draft | Sonnet | Gemini | mean |
|---|---|---|---|
| **round 6** (`e3b99c82b`, short, placeholders) | 4, 4 | 5, 5 | **4.5** |
| round 5 (`bc867318`), JINST arm | 3, 3 | 5, 5 | 4.0 |

All four reads recommend major revision.

## What the reads agree on (the referees' findings, not verified facts)

1. **Table 1** is overloaded. Its status vocabulary is undefined, and a pending row is duplicated (all four).
2. **The ensemble's rejection on a "no worse at every truth" rule** is called thin. A bias–variance trade-off is the
   asked-for basis (both Sonnet reads, one Gemini read).
3. **Prior retention** is not yet attributed to OmniFold rather than the configuration. The pending prior-retention
   result is the deciding item (both Sonnet reads).
4. **The 2D benchmark's χ²** over a near-singular published covariance should not carry a validation role (both Sonnet
   reads).
5. **Fig. 3's panels** use different estimator configurations, and the largest residual quoted comes from the
   lower-capacity variant (one Sonnet read, one Gemini read).
6. **Process language:** an internal date survives in S4 ("until 2026-10-11"), and the syntax is telegraphic in places
   (Gemini).
7. **The five-observable physics case,** the practical gain over a binned approach, is not made (both Sonnet reads).

Nothing is submitted, deposited or tagged.
