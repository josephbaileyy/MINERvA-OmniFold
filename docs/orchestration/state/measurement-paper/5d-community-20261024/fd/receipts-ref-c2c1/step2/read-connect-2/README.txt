REF-C2C1 step two, stage 3b, second run: the read connect re-pinned to M' (the director's ruling of 2026-11-06 in
REF-C2C1-BINDING-2.md, #842: M' = af70e9c4685acdf2d64e30d812942bea1e7ccb0c, the merge of #840). It is committed before
its launch so that it runs from main's bytes. It has not run yet.
- refc2c1_read_login.sh, sha256 d37f6682d8124ba292efd6a17906e53ed0a87f332e60a42f171b42c92ec42b95. It replaces
  ../read-connect/refc2c1_read_login.sh (b162ba9a), whose run stopped on C-PUB (../read/, #838).
  b162ba9a-to-read2.diff is the whole change, in the shape the director adopted:
  - M = M', and the eight blob pins are the binding's table at M' (each re-read here with `git rev-parse M':<path>`).
    ref_c2c1.py, run_suite.py and test_run_suite.py are unchanged.
  - A fresh read directory, R = $O/read-2, and deploy, D = $O/deploy-read-2. The connect refuses if R exists. The stopped
    read's $O/read is left as it is.
  - cells.root is copied from $O/read/cells.root by O_NOATIME into R, and must hash to f06e4a26 (CELLS_SHA) before
    anything else. The unchanged gate then requires main's committed cells.root to be f06e4a26 too.
  - Everything else is unchanged: the five-record gate, the 303-input watch, porcelain, and the reader at M' (which now
    also refuses unless the staged E_R and covariance are C-PUB's source's).
- For the read's receipt (the binding's ruling 1): the units stand on their records at 77d76cfc. ref_c2c1.py is
  byte-identical at M'. The units' meta config_sha256 names 77d76cfc's config.json, which differs from M''s only in
  c_pub, and the read never compares that field.
