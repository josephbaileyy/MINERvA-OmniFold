import hashlib, shutil, subprocess, sys
from pathlib import Path
W = Path(sys.argv[1]); L = "docs/orchestration/state/2d-closeout/evw2d-20261124/launch/"
J = "2d-unfolding/evw2d/sbatch_evw2d.sh"
MUT = [
 ("CONNECT_NN_STRICT", L+"evw2d_connect.sh", "grep -Eq '^1(-1)?$' || [ \"$arr\"", "grep -Eq '^1$' || [ \"$arr\""),
 ("CONNECT_NN_LOOSE", L+"evw2d_connect.sh", "grep -Eq '^1(-1)?$' || [ \"$arr\"", "grep -Eq '^1' || [ \"$arr\""),
 ("CONNECT_TL", L+"evw2d_connect.sh", '[ "$tl" != "$TLIMIT" ] || \\', 'false || \\'),
 ("CONNECT_ARRAY", L+"evw2d_connect.sh", '|| [ "$arr" != 0 ]; then', '; then'),
 ("CONNECT_SRC", L+"evw2d_connect.sh", 'if [ "$src" -ne 0 ] || [ "$nrec"', 'if false || [ "$nrec"'),
 ("CONNECT_NREC", L+"evw2d_connect.sh", '[ "$nrec" != 1 ] ||', 'false ||'),
 ("CONNECT_ID", L+"evw2d_connect.sh", '[ "$id" != "$job" ] ||', 'false ||'),
 ("CONNECT_RETRY", L+"evw2d_connect.sh", 'for try in 1 2 3; do', 'for try in 1; do'),
 ("CONNECT_NO_CANCEL", L+"evw2d_connect.sh", '  scancel "$job"; echo "STOP: the allocation', '  echo "STOP: the allocation'),
 ("CONNECT_RELEASE_RC", L+"evw2d_connect.sh", 'if [ "$rrc" -ne 0 ]; then', 'if false; then'),
 ("CONNECT_NO_HOLD", L+"evw2d_connect.sh", 'sbatch --parsable --hold ', 'sbatch --parsable '),
 ("JOB_BATCH_NODES", J, '[ "${SLURM_JOB_NUM_NODES:-}" = 1 ] ||', 'true ||'),
 ("JOB_TL", J, '[ "$tl" = "$TLIMIT" ] ||', 'true ||'),
 ("JOB_NN", J, "printf '%s' \"$nn\" | grep -Eq '^1(-1)?$' ||", 'true ||'),
 ("JOB_PROBE_GATE", J, '[ "$pnn" = 1 ] ||', 'true ||'),
 ("JOB_PROBE_AFF", J, '[ "$paff" = 64 ] ||', 'true ||'),
 ("JOB_PROBE_RC", J, '[ "$prc" -eq 0 ] ||', 'true ||'),
 ("JOB_WSHA", J, '[ "$wgot" = "$WSHA" ] ||', 'true ||'),
 ("JOB_CSHA", J, '[ "$cgot" = "$CSHA" ] ||', 'true ||'),
 ("JOB_CLEAN_C", J, 'clean_at "$DC" "$C" || refuse', 'true || refuse'),
 ("JOB_OUT", J, '[ ! -e "$LANE/out" ] && [ ! -L "$LANE/out" ] ||', 'true ||'),
 ("JOB_ROOT628", J, '[ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || refuse', 'true || refuse'),
 ("JOB_CPUS", J, 'STEP=(--exclusive -n1 -c 64 --mem=200G)', 'STEP=(--exclusive -n1 -c 32 --mem=200G)'),
 ("JOB_THREADS", J, 'export OMP_NUM_THREADS=64 MKL', 'export OMP_NUM_THREADS=32 MKL'),
 ("JOB_NAME", J, '[ "$SLURM_JOB_NAME" = evw2d ] ||', 'true ||'),
 ("JOB_JSON_ESC", J, '"$(jesc "$*")"', '"$*"'),
 ("LAUNCH_CERT", L+"evw2d_launch.sh", 'cert_ok "$MARGIN" || exit 7', 'true || exit 7'),
 ("LAUNCH_CERT_FROM", L+"evw2d_launch.sh", '[ "$b" -le "$now" ] ||', 'true ||'),
 ("LAUNCH_KEYGEN_RC", L+"evw2d_launch.sh", 'out=$(TZ=UTC ssh-keygen -L -f "$CERT" 2>&1) ||', 'out=$(TZ=UTC ssh-keygen -L -f "$CERT" 2>&1; true) ||'),
 ("LAUNCH_CERTFILE", L+"evw2d_launch.sh", '\n     -o "CertificateFile=$CERT")', ')'),
 ("LAUNCH_SHA", L+"evw2d_launch.sh", '= "$SHA" ] || { echo "STOP: the local', '!= "x" ] || { echo "STOP: the local'),
 ("LAUNCH_NODE", L+"evw2d_launch.sh", 'login[0-9][0-9]) ;;', '*) ;;'),
 ("LAUNCH_FETCH_ABSENT", L+"evw2d_launch.sh", '[ "$f" = post.tar.gz ] && rc=4; continue', 'continue'),
 ("LAUNCH_FETCH_SSH", L+"evw2d_launch.sh", '*) echo "STOP: could not ask saul for $f (ssh rc=$r)"; rc=${r/#0/3}; continue ;;', '*) continue ;;'),
 ("POST_SQUEUE_RC", L+"evw2d_post.sh", "q=$(squeue --me -h -o '%i') || bail", "q=$(squeue --me -h -o '%i') || true"),
 ("POST_QUEUED", L+"evw2d_post.sh", 'printf \'%s\\n\' "$q" | grep -qx "$job" && bail', 'false && bail'),
 ("POST_SACCT_ONE", L+"evw2d_post.sh", '[ "$(printf \'%s\\n\' "$row" | grep -c .)" = 1 ] || bail', 'true || bail'),
 ("POST_TERMINAL", L+"evw2d_post.sh", '  *) bail "job $job is \'$state\' in sacct, not a terminal state";;', '  *) ;;'),
 ("POST_ACCT_OK", L+"evw2d_post.sh", '[ "$state" = COMPLETED ] && [ "$exitc" = "0:0" ] && [ "$nnodes" = 1 ] && acct_ok=true', 'acct_ok=true'),
 ("POST_PASS_ACCT", L+"evw2d_post.sh", '[ "$acct_ok" = true ] && [ "$verify" = PASS ]', '[ "$verify" = PASS ]'),
 ("POST_PASS_ACC", L+"evw2d_post.sh", '&& [ "$acc" = true ] && [ "$fail" = 0 ]', '&& [ "$fail" = 0 ]'),
 ("POST_PASS_FAIL", L+"evw2d_post.sh", '&& [ "$fail" = 0 ] && [ -n "$sums" ] && pass=true', '&& [ -n "$sums" ] && pass=true'),
 ("POST_CFG_BOUND", L+"evw2d_post.sh", "sys.exit(0 if r['pass'] and r['config_bound'] else 1)", "sys.exit(0 if r['pass'] else 1)"),
 ("POST_ARCHIVE", L+"evw2d_post.sh", '  echo "FAILED: the archive"; pass=false', '  echo "FAILED: the archive"'),
 ("CLEAN_POSTPASS", L+"evw2d_cleanup.sh", '[ -f "$PP" ] && [ ! -L "$PP" ] || bail "no post.pass', 'true || bail "no post.pass'),
 ("CLEAN_POSTPASS_MATCH", L+"evw2d_cleanup.sh", '[ -n "$sums" ] && [ "$(cat "$PP")" = "$want" ] || bail', 'true || bail'),
 ("FILL_STRIP", L+"fill_pins.sh", "ok = (strip(bound) == strip(base) and", "ok = (True and"),
 ("FILL_DEC", L+"fill_pins.sh", 'and bound["declaration_sha256"] == dec)', ')'),
 ("FILL_LANE_RE", L+"fill_pins.sh", 'r"/pscratch/sd/j/josephrb/evw2d-20\\d{6}"', 'r".*"'),
]
res = {}
for name, rel, old, new in MUT:
    p = W / rel; orig = p.read_bytes(); t = orig.decode()
    assert t.count(old) == 1, (name, t.count(old))
    p.write_text(t.replace(old, new))
    try:
        r = subprocess.run([sys.argv[2], "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "2d-unfolding/evw2d/test_evw2d_launch.py"],
                           cwd=W, capture_output=True, text=True, env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"})
        res[name] = r.returncode != 0
    finally:
        p.write_bytes(orig)
    print(name, "KILLED" if res[name] else "SURVIVED", flush=True)
print("killed", sum(res.values()), "of", len(res))
