# G3 set B: stat-only check of the jitter-free replicas (2026-11-12)

**By** the valid-region lane (director-helper-2), under the director's go of 2026-11-12 for `jit_statB.sh`
(`7d97931c`) and `jit_launch.sh` (`bd260274`), with the cov2d fence first. It was a stat-only check on one login
node, at 0 node-h: no file was opened, read or listed.

## Finding

S1-DECLARATION.md:66 names a "set B (100, no jitter)" of s5p study N's data bootstrap. Of its 100 named products,
`/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b{1..100}_j-.npz`, **2 exist: b1 and b2.** These are the
two that the stage0 inventory records (`5d-design-20261023/stage0/INVENTORY.sha256:159,171`). b3–b100 are missing.

The record does not say whether the other 98 were never written or were lost. This check cannot tell the two apart.

**Consequence (the director's ruling):** no jitter-free bootstrap exists to read, so no read script was written. The
jitter's effect on the statistical covariance stays the diagonal statement of G3 (`../rounding_decomp.json`), and
the change in its correlations stays unmeasured (`../jitter_cov.json`, G3b). <!-- absence-ok: a pointer to G3b's committed finding (jitter_cov.json [A20_minus_J_is_a_covariance] = false), not a new claim; this check measures existence only -->

| | b1 | b2 |
|---|---|---|
| size | 94,068 | 94,096 |
| mtime | 1790451583 | 1790452213 |
| atime | 1792791154 | 1792791154 |

## The session (`session/`)

1. **Fence,** `fence3.session.out.txt`: login27, 2026-11-12T09:52:10Z. FENCE CLEAR, with ll5d_gate_G18 and AR23
   RUNNING; cov2d_fence.sh `16a2a5cd`.
2. **A local refusal, before any connection,** `statB1-refused.launch.out.txt`. My first launch redirected its
   output into the session directory itself, so the launcher's guard ("not a new empty directory") refused with
   exit 9 before ssh. Nothing reached the cluster. It is disclosed here and was reported to the director.
3. **The stat run,** `statB2.launch.out.txt` (the launcher's own lines) and `statB2.session.out.txt` (the remote
   session): login27, 2026-11-12T09:52:36Z.
   - The staged sha256 is `7d97931c`, ssh rc 0.
   - "present 2 of 100; missing 98". The script's rc is 1 by design, because rc 0 requires all 100.

This was the only stat run of set B. The scripts as run are in `connect/`.

- **CITABLE FOR:** which of the 100 named set-B products existed on pscratch at 09:52:36Z on 2026-11-12.
- **NOT CITABLE FOR:** why the other 98 are absent, or whether set B was ever complete.
