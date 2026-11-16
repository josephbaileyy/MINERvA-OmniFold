"""Write re2c_run_g2r.sh: re2c_run.sh at M (sha256 RUN_SHA) with one line changed, the refined arm's rollup step,
which runs the driver re2c_rollup_g2r.py and its products.tsv.txt (both staged beside this script) in place of re2c_rollup.py. Its mode comes from
RE2C_G2R_MODE (g2r or identity) and must be set. Every other byte is unchanged.
    python3 make_run_g2r.py re2c_run.at-M.sh re2c_run_g2r.sh"""
import hashlib, sys
RUN_SHA = "ff66c7a9faa3529f1a84582fc3df2cfaea43a20016c01523077bbb7880fcf589"
OLD = '    step rollup "$O" "$L/rollup.log" "$P/re2c_rollup.py" --arm refined --out "$O/s5" --results "$O/results"\n'
NEW = ('    step rollup "$O" "$L/rollup.log" "$(cd "$(dirname "$0")" && pwd)/re2c_rollup_g2r.py" '
       '--driver-mode "${RE2C_G2R_MODE:?}" --deploy "$D" --products-tsv "$(cd "$(dirname "$0")" && pwd)/products.tsv.txt" '
       '--sidecar "$O.g2r_driver.json" --arm refined --out "$O/s5" --results "$O/results"\n')
src = open(sys.argv[1], "rb").read()
assert hashlib.sha256(src).hexdigest() == RUN_SHA, "re2c_run.sh is not M's"
s = src.decode()
assert s.count(OLD) == 1
open(sys.argv[2], "w").write(s.replace(OLD, NEW))
