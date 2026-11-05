# BINDING 1 (design): d1 and d2, reconstruction-level data/MC per playlist and the flux swap (director, 2026-11-04)

**Binds** the design of [`FD-RPD-RECO-DECLARATION.md`](FD-RPD-RECO-DECLARATION.md), revision 2, sha256
`b0eee33c95ccb037c681df8d33dccdf1b3d3af60098bba6545c725f706ebe5d8`, as merged in PR #761 at
**M = `5c538db6a0685e3d79fbe487d205540e704ddc1b`**. This covers the recipe, the readings, the outcome table and the
licences, the inputs pinned in `fd/rpd-reco/INPUTS.sha256`, and the price.

**Under** `DECISION-20261104-joseph-referee-analysis-commission.md` (#759, at `1a87d209`), items d1 and d2, and the
Codex diagnosis lane's #760 §C (C-R, C-H).

## What the director checked

- **The digest.** The declaration's sha256 at M is the one above.
- **The audit** is verbatim beside the declaration (`FD-RPD-RECO-AUDIT-1-SONNET-{PROMPT,ANSWER}.txt`). It found 1
  BLOCKING finding (d2's outcome table had a gap), 9 major and 9 minor. §9 maps each finding to its change, and the
  outcome table is now ordered and exhaustive.
- **Admissibility (§6):**
  - a reconstruction-level read with the recipe frozen and bound before any ratio is computed;
  - no new cuts, and no change to any reported number, estimator or covariance;
  - what was already read at reconstruction level, and what was not, is stated;
  - d2-predict fixes the predicted size from simulation before any data is read.
- **The licences (§8):**
  - each covers a note statement first;
  - paper use goes through the PRD-referee read and to Joseph;
  - no outcome names a cause, except TRACKS, which names only a coincidence with the simulation's flux-file
    assignment;
  - "The cause is not known", C_PL,5D and RPD's licensed sentence are unchanged.

## Rulings

1. **The design is bound as declared at M.**
2. **The code** (`nd-unfolding/fd_rpd_reco.py`, the steps pins → p0 → step0 → c0 → d2-predict → d1 → d2) needs its
   own tests, a mutation receipt, an audit of the code and binding 2 before anything runs.
3. **The price is 0 node-h.**
   - Login node, threads 1, nice 19, O_NOATIME, a fresh clone at the bound sha, nothing written to CFS.
   - If the bootstrap's measured wall-clock passes 2 h, or its load is more than light, it moves to a compute node.
     That is priced to the director first.
4. **The order:**
   - the run follows the B4 probe's cluster work in limitation-resolver's queue;
   - each connect's sha256 comes to the director, who gives the go;
   - the flux files' retention is recorded at P0.
5. **The Codex diagnosis lane's C-N** (the per-playlist flux and POT provenance inventory) supplies d2's flux-file
   identities. That lane works from existing records and is not duplicated here.

Nothing is submitted, deposited or tagged.
