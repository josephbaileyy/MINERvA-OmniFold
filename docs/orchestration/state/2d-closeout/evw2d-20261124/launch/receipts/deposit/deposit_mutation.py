import subprocess, sys
from pathlib import Path
W = Path(sys.argv[1]); L = "docs/orchestration/state/2d-closeout/evw2d-20261124/launch/"
H, D, F = L + "evw2d_hpss.sh", L + "evw2d_deposit.sh", L + "fill_deposit_pins.sh"
MUT = [
 ("HPSS_POSTPASS", H, '[ "$pp" = "$want" ] || bail', 'true || bail'),
 ("HPSS_NO_POSTPASS", H, '[ -f "$LANE/post.pass" ] && [ ! -L "$LANE/post.pass" ] || bail "no post.pass"', 'true || bail "no post.pass"'),
 ("HPSS_BOUND", H, '[ "$s" = "$BOUND" ] || bail "SHA256SUMS is not the bound one"', 'true || bail "SHA256SUMS is not the bound one"'),
 ("HPSS_CHECKER_SHA", H, '[ "$w" = "$EVW_SHA" ] || bail', 'true || bail'),
 ("HPSS_REALDIR", H, '[ -d "$d" ] && [ ! -L "$d" ] && [ "$(cd "$d" && pwd -P)" = "$d" ] || bail', 'true || bail'),
 ("HPSS_EXISTS", H, '[ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"', 'true || bail "$f exists"'),
 ("HPSS_PIN_FILLED", H, 'for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$JOBID"; do case "$v" in *__*) bail', 'for v in; do case "$v" in *__*) bail'),
 ("HPSS_SCRATCH_ACC", H, '[ "$arc" -eq 0 ] && [ "$acc" = ACCEPTED ] || stop', 'true || stop'),
 ("HPSS_CHK_JOB", H, "\n      and str(run.get('slurm_job')) == sys.argv[5])", ")"),
 ("HPSS_CHK_CFG", H, " and run.get('config_sha256') == sys.argv[4]\n", "\n"),
 ("HPSS_TAR_EXISTS", H, 'hsi -q "ls $TAR" > "$O/hsi-ls-before.txt" 2>&1 && stop', 'false && stop'),
 ("HPSS_HTAR_RC", H, '[ "$r" -eq 0 ] || stop "htar rc', 'true || stop "htar rc'),
 ("HPSS_HASH", H, '[ "$hc" -eq 0 ] && [ "$hv" -eq 0 ] || bad=1', 'true || bad=1'),
 ("HPSS_HV_ONLY", H, '[ "$hc" -eq 0 ] && [ "$hv" -eq 0 ] || bad=1', '[ "$hc" -eq 0 ] || bad=1'),
 ("HPSS_SNAPSHOT", H, 'cmp -s "$E/$f" "$O/snapshot/$f" || {', 'true || {'),
 ("HPSS_FIN_RC", H, 'fin "$bad"', 'fin 0'),
 ("DEP_PIN_FILLED", D, 'for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$JOBID"; do\n  case "$v" in *__*)', 'for v in; do\n  case "$v" in *__*)'),
 ("DEP_HOME", D, 'case "$dest/" in "$home"/?*/) ;; *)', 'case "$dest/" in *) ;; *)'),
 ("DEP_TEMPROOT", D, 'case "$dest/" in /private/tmp/*|/tmp/*|/private/var/*|/var/*) echo', 'case "$dest/" in /nonexistent/*) echo'),
 ("DEP_LOCAL_CHECKER", D, '[ "$w" = "$EVW_SHA" ] || \\', 'true || \\'),
 ("DEP_CHK_SUMS", D, "sums == sys.argv[3] and run.get", "run.get"),
 ("DEP_CHK_JOB", D, "\n      and str(run.get('slurm_job')) == sys.argv[5])", ")"),
 ("DEP_CHK_CFG", D, " and run.get('config_sha256') == sys.argv[4]\n", "\n"),
 ("DEP_SCP_RC", D, 'echo "scp $f rc=$r"; [ $r = 0 ] || exit $r', 'echo "scp $f rc=$r"'),
 ("DEP_HPSS_MARGIN", D, 'hpss) S="$HERE/evw2d_hpss.sh"; SHA=__HPSS_SHA256__; MARGIN=3600 ;;', 'hpss) S="$HERE/evw2d_hpss.sh"; SHA=__HPSS_SHA256__; MARGIN=600 ;;'),
 ("DEP_APPROVED", D, '[ "$(shasum -a 256 "$S" | cut -d\' \' -f1)" = "$SHA" ] || {', 'true || {'),
 ("DEP_FETCH_ABSENT", D, '0:absent) echo "hpss.tar.gz absent"; exit 4 ;;', '0:absent) echo "hpss.tar.gz absent" ;;'),
 ("FILL_ACC", F, 'ok = (acc.get("pass") is True and', 'ok = (True and'),
 ("FILL_JOB", F, 'and str(acc.get("run_slurm_job")) == job', ''),
 ("FILL_JOBBOUND", F, 'and acc.get("job_bound") is True', ''),
 ("FILL_DONE_SUMS", F, 'and acc.get("done", {}).get("SHA256SUMS") == bound', ''),
 ("FILL_HEAD", F, 'git -C "$TOP" diff --quiet HEAD -- "$RD" "$PINS1" ||', 'true ||'),
 ("FILL_EVW", F, '[ "$(shasum -a 256 "$TOP/2d-unfolding/evw2d/evw2d.py" | cut -d\' \' -f1)" = "$EVW" ] ||', 'true ||'),
]
res = {}
for name, rel, old, new in MUT:
    p = W / rel; orig = p.read_bytes(); t = orig.decode()
    assert t.count(old) == 1, (name, t.count(old))
    p.write_text(t.replace(old, new))
    try:
        r = subprocess.run([sys.argv[2], "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "2d-unfolding/evw2d/test_evw2d_deposit.py"],
                           cwd=W, capture_output=True, text=True, env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"})
        res[name] = r.returncode != 0
    finally:
        p.write_bytes(orig)
    print(name, "KILLED" if res[name] else "SURVIVED", flush=True)
print("killed", sum(res.values()), "of", len(res))
