# Referee requests mapped to records on main, 2026-11-06

**What it is:** `MAP.md`. A read-only search agent, commissioned by the director, checked each analysis the referees
requested (rounds 1–2 and the JINST test) against the records on origin/main @ `86bd113ea`. It also checked each against
the methods draft at `0de103f7`, round 2. It opened every record it cites and read that record's licence section.

**Why.** limitation-resolver found that one of the referees' main requests, the coverage pre-check diagnosis, was
already answered by bound records (DIAG #633, I0 #645, I2 #650, staged stage 0 #667). The paper just didn't say so.
The referees read only the paper, so a request measures what the paper contains, not what the records contain.

**The director spot-checked two claims against their records at origin/main:**
- `period-unfold-20261014/REPORT.md:63-64`: the reco-level step is +6.10 %, and the unfolded double ratio is
  +6.94 % ± 0.41.
- `FD-1B-INV-I0-REPORT.md:66-68`: σ_J/f on the data has median 0.133 % over the 16 cells.

Both match.

**Limits:**
- It is an agent's survey, not a record of results.
- Each row's "status" is the agent's reading. Its ABSENT rows give the agent's search terms, so ABSENT means "not found
  by those terms".
- The draft column describes round 2. Round 3 (`efa093e0`) adds REF-G1, REF-C2C1 and the gate-D diagnosis.

**CITABLE FOR:** which records answer which referee requests, as a route to those records.

**NOT CITABLE FOR:** any result. Cite the records themselves.
