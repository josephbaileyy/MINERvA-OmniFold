Valid-region read receipt (BINDING-1.md ruling 4). It was run on 2026-11-07 at 18:48:13Z on the lane's local machine
(host DN0a1f6baa), at 0 node-h, with no cluster contact.

THE RUN (run_read.sh, sha256 f66bfce16a4a780dcc8c2696c75cc9419445941a47f5c9fe5080f7280741b95e)
- It cloned the repo fresh at M = 0687d6f2776b3ad691568f701de3aff166d9ca2a and checked that HEAD == M and the
  porcelain was empty.
- binding-pins.check: the binding's four digests (DECLARATION.md, valid_region.py, test_valid_region.py,
  INPUTS.sha256) were equal, 4/4.
- inputs.check: `shasum -a 256 -c INPUTS.sha256` gave rc 0, with I1-I6 equal, 6/6.
- tests.log: the test suite at M ran 56 tests, OK.
- The read was `python3 -B valid_region.py read --repo <clone> --out <dir>`:
  - rc 0, and read.stderr says "readings written";
  - all 11 controls PASS;
  - the clone's porcelain was still empty afterwards.
- environment.txt: Python 3.12.2 and numpy 1.26.4. BLAS was pinned to 1 thread, with PYTHONDONTWRITEBYTECODE=1.

FILES
- readout.json, sha256 91bb604e3a62e2654e611750830e225061e5c0b0255b12455a23ac9be4eec84c (52,394 B), and
  readout.txt: the tool's outputs, copied unchanged.
- SHA256SUMS, sha256 72ed5893c54ad8803f1fec83b9dbc528ed4eec8af206878ca24a3c55085e0622: it was written by the run and
  covers its 10 files.
- console.txt (sha256 63aaa6bb23460f3a32fbfc21453d4319bdbd04cabe56bc2cf12bf1a11c7b77a0): the run's console.
- run_read.sh and this README: these sit outside SHA256SUMS, and their digests are given above.

INDEPENDENT SPOT-CHECK (by the lane, after the run)
Separate code, not importing valid_region.py, was run on the clone's raw JSON. It reproduced:
- R15's ρ (b_raw/g_raw) as 0.5637;
- Q4's r_Q +0.2118 and z_Q 3.190;
- the R05-R06 contrast z, 3.46, against 3.45 from a 400,000-draw Monte Carlo of f ~ N(f, C) and g_P ~ N(g_P, V_P).
  This check is of the linearized σ.

The readings and their licences are recorded in the outcome record, docs/orchestration/OUTCOME-20261107-valid-region.md,
which follows this receipt in its own PR. Reading (3) is
descriptive only (DECLARATION.md section 6, audit VR-1).
