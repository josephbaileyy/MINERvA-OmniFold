"""connect-s5.sh: phase S at M_A5 (COV2D-BINDING-2, "Addendum A5, the M line"), from connect-s.sh. Adds A5's grade-refusal
verdict line and ruling 3's reading rule: for every grade with ndf = 205, a finite kappa2 and tol and a finite
max_rel_diff <= tol, else the truth's score reads INVALID. T and D stay placeholders."""
from pathlib import Path
MA5 = "b1d56e4f08e62983784e34b2278f38a09a68eca0"
s = Path("/Users/josephbailey/cov2d-work/connect-s.sh").read_text()
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep("# Login node, 0 node-h (A4 section 9), at M = ac25b665.", "# Login node, 0 node-h (A4 section 9), at M_A5 = b1d56e4f (A5's M line; was ac25b665).")
rep("# goes to the director unrepaired, with the mechanism named (binding A4, ruling 2).\n",
    "# goes to the director unrepaired, with the mechanism named (binding A4, ruling 2).\n"
    "# A5 (M line rulings 1-3): a grade refusal is rc 3 \"COV2D-SCORE <T> INVALID (grade refused, <grade>: <text>)\" with\n"
    "# score_<T>.invalid.json. Ruling 3's reading rule is applied here after the run and printed per grade (A5-READING):\n"
    "# for each grade (cholesky_check = C_T, cholesky_check_minus = C_T-) whose compared ndf is 205, kappa2, tol and\n"
    "# max_rel_diff must be finite, max_rel_diff <= tol, and the tol the grade used (compared.tol) must be the recorded\n"
    "# tol; a grade with no compared values also fails. If it fails, the PHASE-S line reads INVALID (A5 reading rule),\n"
    "# whatever the driver printed; the records are left as written.\n")
rep("M=ac25b66533788ceb18b1d4e5add259c53b216669\n", f"M={MA5}   # M_A5 (#900's merge; bound by #911)\n")
rep("READOUT_SHA=d1a3cff9768cb3913c9b95c9c6c1bb7402c5a14103f1dd22f5131c16aacda297\n",
    "READOUT_SHA=0c3ad137be128691cce7bbe3ec72493b76791e761e6cd897f75aaf0a4fc7444f   # cov2d_readout.py at M_A5\n")
rep('''  "3:COV2D-SCORE $T STOP"|"3:COV2D-SCORE $T INVALID") V=${L#COV2D-SCORE $T } ;;\n''',
    '''  "3:COV2D-SCORE $T STOP"|"3:COV2D-SCORE $T INVALID") V=${L#COV2D-SCORE $T } ;;\n'''
    '''  "3:COV2D-SCORE $T INVALID (grade refused, "*) V=${L#COV2D-SCORE $T } ;;\n''')
rep('''echo "PHASE-S $T $V rc=$rc"\n''', '''# A5 M line ruling 3: the reading rule, per grade, from whichever score record was written
SR=""; for f in "$W/out/score_$T.json" "$W/out/score_$T.invalid.json"; do [ -f "$f" ] && SR="$SR $f"; done
if [ -n "$SR" ]; then
  "$PY310" -B - $SR <<'A5R'; a5=$?
import json, math, sys
ok = True
for p in sys.argv[1:]:
    rec = json.load(open(p))
    for key, grade in (("cholesky_check", "C_T"), ("cholesky_check_minus", "C_T_minus")):
        cc = rec.get(key) or {}
        cmp = cc.get("compared") or {}
        k, tol, mrd, ndf = cc.get("kappa2"), cc.get("tol"), cmp.get("max_rel_diff"), cmp.get("ndf")
        fin = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
        if not cmp:
            good = False; why = "no compared values"
        elif ndf != 205:
            good = True; why = f"ndf {ndf}: the rule applies at ndf 205 only"
        else:
            good = fin(k) and fin(tol) and fin(mrd) and mrd <= tol and cmp.get("tol") == tol
            why = ("finite, max_rel_diff <= tol, the grade used the recorded tol" if good
                   else "not finite, or max_rel_diff > tol, or the grade's tol is not the recorded tol")
        ok &= good
        print(f"A5-READING {p.rsplit('/', 1)[-1]} {grade} ndf={ndf} kappa2={k!r} tol={tol!r} cmp_tol={cmp.get('tol')!r} "
              f"max_rel_diff={mrd!r} {'OK' if good else 'FAIL'} ({why})")
print("A5-READING-RULE " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 8)
A5R
  [ "$a5" = 0 ] || V="INVALID (A5 reading rule; the driver printed: $V)"
else
  echo "A5-READING-RULE NOT-CHECKED (no score record written; verdict $V)"
fi
echo "PHASE-S $T $V rc=$rc"
''')
Path("/Users/josephbailey/cov2d-work/connect-s5.sh").write_text(s)
print("written")
