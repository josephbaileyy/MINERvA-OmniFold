"""Build cfs_1a_check.sh: a stat-only check of the 294 1A AnaTuple CFS copies.

Usage: python3 -I make_cfs_check.py SESSION_TXT ANATUPLE_SHA256_TSV OUT_SH [ROOT_DATA ROOT_MC]
The 294 rows are session.txt's anatuple_{data,mc}_1A FOUND rows; each expected size and mtime is the manifest's.
ROOT_DATA/ROOT_MC override the CFS roots for a local fixture test only.
"""
import calendar, sys, time
sess, man_path, out = sys.argv[1:4]
P = '/pscratch/sd/j/josephrb/minerva/minerva_large_files/'
ROOTS = {'anatuple_data_1A': '/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/anatuple-data-20261009/',
         'anatuple_mc_1A': '/global/cfs/cdirs/m3246/josephrb/mc-1A-preservation-20261014/'}
if len(sys.argv) == 6:
    ROOTS = {'anatuple_data_1A': sys.argv[4], 'anatuple_mc_1A': sys.argv[5]}
man = {}
for line in open(man_path).read().splitlines()[1:]:
    h, b, m, p = line.split('\t')
    man[p] = (int(b), calendar.timegm(time.strptime(m, '%Y-%m-%dT%H:%M:%SZ')))
rows = []
for line in open(sess):
    f = line.split()
    if len(f) == 6 and f[0] == 'FOUND' and f[1] in ROOTS:
        assert f[5].startswith(P), f
        rel = f[5][len(P):]
        b, m = man[rel]
        assert (b, m) == (int(f[2]), int(f[4])), ('session row differs from manifest', rel)
        rows.append('%s\t%d\t%d\t%s%s' % (f[1], b, m, ROOTS[f[1]], rel))
n_data = sum(r.startswith('anatuple_data_1A\t') for r in rows)
assert (len(rows), n_data) == (294, 253), (len(rows), n_data)
assert sum(int(r.split('\t')[1]) for r in rows) == 787539272045
body = r'''#!/bin/bash
# CFS 1A check (valid-region lane, 2026-11-11, for the director): stat only, on dtn01, of the 294 explicit CFS paths of
# the playlist 1A AnaTuple copies (data: prd-release-preservation-20261008/anatuple-data-20261009/, MC:
# mc-1A-preservation-20261014/). Each file's size and mtime must equal the manifest's (ANATUPLE-SHA256.tsv 913e004d).
# No file is opened or read, no directory is listed, nothing is written, and pscratch is not touched.
# Exit 0 = all 294 OK; 3 = any MISSING, not a regular file, or DIFF (a STOP); 9 = wrong host or no python3.
case "$(hostname)" in dtn01*) ;; *) echo "STOP: host $(hostname) is not dtn01"; exit 9;; esac
command -v python3 > /dev/null || { echo "STOP: no python3"; exit 9; }
echo "cfs 1A check host=$(hostname) utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 -I - <<'PY'
import os, stat, sys
ROWS = """
@ROWS@
""".strip().split("\n")
bad = 0; n = {}; tot = 0
for r in ROWS:
    g, b, m, p = r.split("\t"); b = int(b); m = int(m)
    try:
        st = os.stat(p)
    except OSError as e:
        print("MISSING %s %s %s" % (g, e.errno, p)); bad += 1; continue
    kind = "reg" if stat.S_ISREG(st.st_mode) else "notreg"
    ok = kind == "reg" and st.st_size == b and int(st.st_mtime) == m
    print("%s %s size=%d mtime=%d mode=%o uid=%d gid=%d %s" % ("OK" if ok else "DIFF", g, st.st_size, int(st.st_mtime),
          stat.S_IMODE(st.st_mode), st.st_uid, st.st_gid, p))
    if ok:
        n[g] = n.get(g, 0) + 1; tot += st.st_size
    else:
        bad += 1
for g in sorted(n): print("GROUP %s ok=%d" % (g, n[g]))
print("SUMMARY rows=%d ok=%d bad=%d ok_bytes=%d" % (len(ROWS), sum(n.values()), bad, tot))
sys.exit(3 if bad else 0)
PY
rc=$?
echo "check rc=$rc"
exit $rc
'''
open(out, 'w').write(body.replace('@ROWS@', '\n'.join(rows)))
