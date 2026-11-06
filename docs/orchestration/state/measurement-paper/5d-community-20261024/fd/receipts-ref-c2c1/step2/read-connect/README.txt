REF-C2C1 step two, stage 3b: the read connect, committed before its launch so that it runs from main's bytes. It has not
run yet.
- refc2c1_read_login.sh, sha256 b162ba9ac8b12887e02ab3130dae4a9185f6fbdcfa2a0db684021e5e06c63f79. coverage-5b-audit read it
  (GO) with the completion connect, and the director named it for 3b. It replaces the unlaunched 68946159 with the gate
  the director ruled after the four TIMEOUT jobs; diff-read-vs-68946159.txt is that change.
- Its gate: CENTRALS-DONE is the accepted record. REPLICAS-TIMEOUT-j0..3 (../units-replicas/timeout/) and
  REPLICAS-DONE-j4 (../units-replicas/completion/) on main each equal the pscratch record and are non-empty, and each
  passes its fields. The five unit sets are disjoint, their union is the 350 of lanes.tsv (7b737d0c), and every unit has
  a PASS done-marker. 3a's cells.root (f06e4a26) is on main and equal to the read directory's.
- It runs `ref_c2c1_read.py read` at M = 77d76cfc in root_6_28 (nice 19, idle I/O, 4 threads). The reader's stdout goes
  to read.stdout and is not echoed; the 303 COV2D inputs are stat'd before and after.
