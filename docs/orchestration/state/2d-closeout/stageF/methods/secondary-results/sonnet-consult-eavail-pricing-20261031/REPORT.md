# Independent referee's read of the E_avail 139.57 MeV switch pricing (Sonnet, 2026-10-31)

**By** the paper-tighten lane, as director, before the pricing goes to Joseph. **It rules nothing.**

- **Model:** Sonnet (claude-school), a general-purpose subagent, read-only, working only from four files.
- **Inputs** (sha256 in `INPUTS.SHA256SUMS`):
  - the pricing as filed in PR #622 at `ac619e2d` (`ASSESSMENT.md`, later
    `ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md`);
  - its bracket output, `bracket_16cell.txt`;
  - `DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md`;
  - `docs/EAVAIL_DEFINITION.md` at `main`.
- **Prompt and answer:** `prompt.txt`, verbatim, and `answer.txt`, the final answer verbatim plus a final newline.

**Its recommendations:**
- **Step 0:** measure the unfolded effect, not only prior level. Give it per cell and as a full-covariance norm. Add a
  one-file event-loop exactness check, and keep the event-loop files whichever option is chosen.
- **Thresholds:** keep 135 below about 0.15σ per cell (and about 0.3σ in norm). Make a scoped switch at about 0.25σ or
  above (or 0.5σ in norm). The full switch is not worth 208 node-h.
- **The departure sentence:** as drafted, it reads as the only departure from published E_avail. It should also name
  the larger species differences that `EAVAIL_DEFINITION.md` records.
- **Gaps in the assessment:**
  - that `MC_npip` and `GetEAvailableTrue` count the same pions;
  - the 0.081 % net move in the bracket;
  - the event-loop inputs to the 2D result;
  - the doc's six-site list;
  - the closure figures, which have no producer.

**The director's action:** step 0's scope was extended with points (a)–(e) of the referee's read. The rerun and unfold
it proposes are priced as options for Joseph and not authorized.
