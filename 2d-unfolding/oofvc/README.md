# OOFVC: the 2D central values under MINERvA's counting convention

The declaration is `docs/orchestration/state/oofv-convention-20261126/OOFVC-DECLARATION.md`. It holds the question,
the rulings, the controls, the readings fixed before any number, and the price. This directory is its code.

| file | what it is |
|---|---|
| `oofvc_driver.diff` | the default-off `--signal-convention minerva` option on `re2_driver.py`, at M = 77d76cfc with Tier 1's edge edit. It gives the driver 0cbd02a1… |
| `make_tree.sh` | builds the deploy tree at M: archive mode for the tests, clone mode on the cluster. It applies the edge edit and the diff, re-pins `ref_c2c1/config.json`, and prints every digest |
| `oofvc_dump.cpp` | route A's AnaTuple pass, one MC playlist: every selected entry with both routings, the truth and both weights |
| `oofvc_join.py` | C-ROUTE, C-JOIN, C-SIGW and C-LAB. It writes the driver's `--oofvc-rows` file and the class sizes |
| `oofvc_run.py` | the four units through REF-C2C1's `run_unit`, unchanged, plus N from each c2 unit |
| `oofvc_score.py` | the laptop scorer: C-BASE, C-FIX, C-MOVE and the unit verdicts first, then the operands, bands and statements |
| `oofvc_lib.py` | the pure functions those call: the join, the moved rows, N, the distance, the bands |
| `test_oofvc.py` | the suite: pure tests, plus ROOT tests on RE-2's fixture and a join fixture |
| `oofvc_mutation.py` | the mutation campaign |
| `launch/` | the cluster steps. `fill_pins.sh` writes `launch/bound/` at the tool commit |

**Tests.** The pure tests need numpy only. The ROOT tests need PyROOT, LightGBM and scikit-learn. No libRooUnfold
exists locally, so the runner tests use the numpy unfolder, and the scorer refuses such units.

    OMP_NUM_THREADS=1 /path/to/python -B -m pytest -q -p no:cacheprovider test_oofvc.py

**Cluster** (after the reads, the director's GO and a fence round):

    bash launch/bound/oofvc_launch.sh dump-pilot|dump-rest|units|post <new empty dir> loginNN
    bash launch/bound/oofvc_launch.sh fetch <new empty dir>
