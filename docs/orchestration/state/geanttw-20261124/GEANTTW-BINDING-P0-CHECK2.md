# GEANTTW-BINDING-P0-CHECK2: re-running geanttw P0's check with the revised C0e

Follows GEANTTW-BINDING-P0 (#1385). P0's first check (M = 4fe6add5) failed C0e: 23 environment paths were opened outside B. That FAIL stands as recorded. The director's ruling that day was route (A): attribute the opens, then allow exactly those families. The attribution and revision merged in #1394 (`p0_check.py` sha256 `7b56df4b14527ac39c406f76f7437a494399d35dd1d853b4e9e59ddeff191731`), and the first check's records merged in #1396 (`c0e-attribution/first-check/`). No job is re-run.

## What is bound

Main at `f8fac4cda01bb2b79bb54ef42e1a2212654b4dc0`:
- `c0e-attribution/first-check/aside_first_check.sh` sha256 `9be3cdf3d7b5a6e551547653da8b895e4e4b1fbfe5498c4f476a0a53309c7954`;
- `code/p0_check.py` sha256 `7b56df4b14527ac39c406f76f7437a494399d35dd1d853b4e9e59ddeff191731`;
- `SHA256SUMS-P0` sha256 `1c5bf3b4d2db577c586d0149d75e0d3c12219199275d34c8a1c21046caed842d`.

**M** for all three steps is this binding's own merge commit.

## Steps, each on its own GO and a fresh cov2d ack

1. `bash docs/orchestration/state/geanttw-20261124/c0e-attribution/first-check/aside_first_check.sh M <COV2D_ACK>`, from a clean checkout of M. It renames `B/deploy` to `B/deploy-4fe6add5` and `B/run/p0/p0_check.json` to `B/run/p0/p0_check-4fe6add5.json` with `mv -n`. It refuses if a source is missing or a target exists, and it deletes nothing.
2. `geanttw_connect.sh deploy M <COV2D_ACK> GEANTTW-BINDING-P0:NuE-exception@2026-11-26`. It clones M into B/deploy and re-hashes S0, which must equal fe0bc458….
3. `geanttw_connect.sh check M <COV2D_ACK> GEANTTW-BINDING-P0:NuE-exception@2026-11-26`. It runs the revised `p0_check.py` on P0's existing outputs (C0a–C0f) and copies the reference with O_NOATIME.

All three are login-node work and submit no job (0 node-h). The NERSC certificate is checked by command before each step. A FAIL or STOP in any step is terminal and comes back to the director. Not covered: `build`, `p0`, any job, and P2–P3.
