# OOFVC mutation campaign

- **The full campaign:** `mutation-dbe40c6d.json.txt` (log `mutation-dbe40c6d.log.txt`), at commit dbe40c6d, 55 mutants.
  The control (every test class) passed. 51 of 55 were killed.
- **The survivors** were four test gaps: LIB_BAND_LITTLE, LIB_COLUMN_AREA, JOIN_LAB_TOL and SCORE_STAGE_PATH.
  bbc3fc1b closes them:
  - a band case at r = 1.055;
  - an area-weighted column case;
  - C-LAB refusing a 1e-7 value change with equal counts;
  - `oofvc_score.argv_is_e_r`, factored out with its logic unchanged, tested directly.
- **The targeted pass:** `mutation-targeted-bbc3fc1b.json.txt`, at bbc3fc1b. The control passed, and all four were
  killed.
- **Together, every one of the 55 mutants is killed.**
- **Suites:** `tests-dbe40c6d.txt` (41 passed) and `tests-bbc3fc1b.txt` (43 passed).
- **Environment:** ROOT 6.40 with LightGBM, locally. No libRooUnfold exists here, so the runner tests use the numpy
  unfolder, which the scorer refuses for production units.
- **Not covered:** `oofvc_dump.cpp` cannot be built here (no MAT). Its behaviour is checked on the cluster, bit for bit, by
  C-ROUTE, C-JOIN, C-SIGW and C-LAB, each a STOP.
<!-- absence-ok: a statement about this lane's own test environment and coverage, not a claim that a result does not exist -->
