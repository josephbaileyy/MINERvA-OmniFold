import subprocess, sys
from pathlib import Path
W = Path(sys.argv[1]); L = "docs/orchestration/state/2d-closeout/evw2d-20261124/launch/"
H, D, F = L + "evw2d_hpss.sh", L + "evw2d_deposit.sh", L + "fill_deposit_pins.sh"
MUT = [
 ("HPSS_POSTPASS", H, '[ "$pp" = "$want" ] || bail', 'true || bail'),
 ("HPSS_NO_POSTPASS", H, '[ -f "$LANE/post.pass" ] && [ ! -L "$LANE/post.pass" ] || bail "no post.pass"', 'true || bail "no post.pass"'),
 ("HPSS_BOUND", H, '[ "$s" = "$BOUND" ] || bail "SHA256SUMS is not the bound one"', 'true || bail "SHA256SUMS is not the bound one"'),
 ("HPSS_DONE_BOUND", H, '[ "$s" = "$DONE_SHA" ] || bail "evw2d.done is not the bound one"', 'true || bail "evw2d.done is not the bound one"'),
 ("HPSS_REGULAR", H, 'for n in $NAMES; do [ -f "$E/$n" ] && [ ! -L "$E/$n" ] || bail', 'for n in $NAMES; do true || bail'),
 ("HPSS_CHECKER_SHA", H, '[ "$w" = "$EVW_SHA" ] || bail', 'true || bail'),
 ("HPSS_REALDIR", H, '[ -d "$d" ] && [ ! -L "$d" ] && [ "$(cd "$d" && pwd -P)" = "$d" ] || bail', 'true || bail'),
 ("HPSS_EXISTS", H, '[ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"', 'true || bail "$f exists"'),
 ("HPSS_PIN_FILLED", H, 'for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$DONE_SHA" "$JOBID"; do case "$v" in *__*) bail', 'for v in; do case "$v" in *__*) bail'),
 ("HPSS_SCRATCH_ACC", H, '[ "$arc" -eq 0 ] && [ "$acc" = ACCEPTED ] || stop', 'true || stop'),
 ("HPSS_CHK_JOB", H, "\n      and str(run.get('slurm_job')) == sys.argv[7])", ")"),
 ("HPSS_CHK_CFG", H, " and run.get('config_sha256') == sys.argv[6]\n", "\n"),
 ("HPSS_LS_RC", H, '|| stop "hsi could not list $H"', '|| true "hsi could not list $H"'),
 ("HPSS_NAME_PATTERN", H, '$R\\.tar(\\.part)?(\\.idx)?\\$', '$R\\.tar\\$'),
 ("HPSS_SPACE", H, '[ $(( avail * 1024 )) -ge $(( need + need / 10 + 67108864 )) ] || stop', 'true || stop'),
 ("HPSS_HTAR_RC", H, '[ "$r" -eq 0 ] || stop "htar rc', 'true || stop "htar rc'),
 ("HPSS_HASH", H, '[ "$hc" -eq 0 ] && [ "$hv" -eq 0 ] || bad=1', 'true || bad=1'),
 ("HPSS_HV_ONLY", H, '[ "$hc" -eq 0 ] && [ "$hv" -eq 0 ] || bad=1', '[ "$hc" -eq 0 ] || bad=1'),
 ("HPSS_SCRATCH_AFTER", H, '"$O/scratch-after.log" 2>&1 || { echo "scratch changed during the archive"; bad=1; }', '"$O/scratch-after.log" 2>&1 || true'),
 ("HPSS_FIN_RC", H, 'fin "$bad"', 'fin 0'),
 ("DEP_CDPATH", D, 'unset CDPATH\n', '\n'),
 ("DEP_HOME", D, 'case "$dest/" in "$home"/?*/) ;; *)', 'case "$dest/" in *) ;; *)'),
 ("DEP_TEMPROOT", D, 'case "$dest/" in /private/tmp/*|/tmp/*|/private/var/*|/var/*) echo', 'case "$dest/" in /nonexistent/*) echo'),
 ("DEP_LOCAL_CHECKER", D, '[ "$w" = "$EVW_SHA" ] || \\', 'true || \\'),
 ("DEP_CHK_DONE", D, " and done == sys.argv[5] and run.get", " and run.get"),
 ("DEP_CHK_JOB", D, "\n      and str(run.get('slurm_job')) == sys.argv[7])", ")"),
 ("DEP_CHK_CFG", D, " and run.get('config_sha256') == sys.argv[6]\n", "\n"),
 ("DEP_SCP_RC", D, 'echo "scp $f rc=$r"; [ $r = 0 ] || exit $r', 'echo "scp $f rc=$r"'),
 ("DEP_FETCH_ABSENT", D, '0:absent) echo "hpss.tar.gz absent"; exit 4 ;;', '0:absent) echo "hpss.tar.gz absent" ;;'),
 ("DEP_FETCH_VERIFY", D, '[ "$v" = 1 ] || {', 'true || {'),
 ("DEP_FETCH_RC0", D, "tail -1 \"$log\" | grep -Eq '^hpss rc=0 ' || v=0", "true"),
 ("DEP_FETCH_66", D, 'grep -Fxq "retrieved and equal to their pins: 6 of 6; files retrieved: 6" "$log" || v=0', 'true'),
 ("DEP_FETCH_RENAME", D, 'grep -Fxq "renamed to /home/j/josephrb/mnv-$R/$R.tar" "$log" || v=0', 'true'),
 ("FILL_ACC", F, 'ok = (acc.get("pass") is True and', 'ok = (True and'),
 ("FILL_JOB", F, 'and str(acc.get("run_slurm_job")) == job', ''),
 ("FILL_JOBBOUND", F, 'and acc.get("job_bound") is True', ''),
 ("FILL_MARKER_SUMS", F, ' and marker.get("SHA256SUMS") == bound', ''),
 ("FILL_MARKER", F, 'and marker == acc.get("done")', ''),
 ("HPSS_NAME_FOUND", H, '  0) stop "$H already holds an archive name";;', '  0) echo found;;'),
 ("HPSS_GREP_ERR", H, '  *) stop "could not read the listing (grep rc $g)";;', '  *) echo err;;'),
 ("HPSS_RENAME_GATE", H, 'if [ "$bad" -eq 0 ]; then\n  if ! hsi -q "mv', 'if true; then\n  if ! hsi -q "mv'),
 ("HPSS_MV_IDX", H, 'if ! hsi -q "mv ${TARP}.idx ${TAR}.idx" > "$O/hsi-mv.log" 2>&1; then', 'if ! { hsi -q "mv ${TARP}.idx ${TAR}.idx" > "$O/hsi-mv.log" 2>&1; true; }; then'),
 ("HPSS_MV_ARCHIVE", H, 'elif ! hsi -q "mv $TARP $TAR" >> "$O/hsi-mv.log" 2>&1; then', 'elif false; then'),
 ("HPSS_REGULAR_AFTER", H, 'for n in $NAMES; do [ -f "$E/$n" ] && [ ! -L "$E/$n" ] || { echo "$E/$n is no longer a regular file"; bad=1; }; done', 'true'),
 ("FILL_BLOB_MODE", F, '[ "$m" = "100644 blob" ] ||', 'true ||'),
 ("FILL_EVW", F, '[ "$(hblob 2d-unfolding/evw2d/evw2d.py)" = "$EVW" ] ||', 'true ||'),
 ("HPSS_READBACK", H, '[ "$tr" -eq 0 ] && [ "$nl" -eq "$nf" ] || { echo "FAILED: the archive does not read back"; bad=1; }', 'true'),
 ("DEP_PIN_FILLED", D, 'for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$DONE_SHA" "$JOBID" "$HPSS_SHA"; do\n  case "$v" in *__*)', 'for v in; do\n  case "$v" in *__*)'),
 ("DEP_HPSS_MARGIN", D, 'hpss) S="$HERE/evw2d_hpss.sh"; SHA=$HPSS_SHA; MARGIN=3600 ;;', 'hpss) S="$HERE/evw2d_hpss.sh"; SHA=$HPSS_SHA; MARGIN=600 ;;'),
 ("DEP_APPROVED", D, '[ "$(shasum -a 256 < "$S" | cut -d\' \' -f1)" = "$SHA" ] || {', 'true || {'),
 ("DEP_FETCH_JOB", D, 'case "$first" in *" hpss sha256 $HPSS_SHA bound $BOUND done $DONE_SHA job $JOBID") ;; *) v=0;; esac', 'true'),
 ("DEP_FETCH_JOB_EXACT", D, '*" hpss sha256 $HPSS_SHA bound $BOUND done $DONE_SHA job $JOBID") ;;', '*" hpss sha256 $HPSS_SHA bound $BOUND done $DONE_SHA job $JOBID"*) ;;'),
 ("DEP_FETCH_TF", D, 'grep -Fxq "htar -tf rc=0" "$log" || v=0', 'true'),
 ("DEP_FETCH_READBACK", D, 'grep -Fxq "the archive lists 6 of 6 pinned names" "$log" || v=0', 'true'),
 ("DEP_FETCH_SNAP", D, 's=$(shasum -a 256 < "$snap" | cut -d\' \' -f1) && [ "$s" = "$BOUND" ] || v=0', 'true'),
 ("DEP_FETCH_PINS", D, 'cmp -s "$pins" "$F/pinned-want.sha256" && [ "$(wc -l < "$F/pinned-want.sha256" | tr -d \' \')" = 6 ] || v=0', 'true'),
 ("FILL_TEMPLATE_HEAD", F, '[ "$(shasum -a 256 < "$TOP/$f" | cut -d\' \' -f1)" = "$h" ] ||', 'true ||'),
 ("HPSS_LS_AFTER", H, 'if [ "$la" -eq 0 ] && grep -Eq "(^|[[:space:]/])$R\\.tar\\$" "$O/hsi-ls-after.txt" \\\n       && grep -Eq "(^|[[:space:]/])$R\\.tar\\.idx\\$" "$O/hsi-ls-after.txt" && [', 'if ['),
 ("HPSS_FINAL_GATE", H, '&& [ "$tf" -eq 0 ] && [ "$fl" -eq "$nf" ]; then', '; then'),
 ("HPSS_ROLLBACK_IDX", H, 'hsi -q "mv ${TAR}.idx ${TARP}.idx" >> "$O/hsi-mv.log" 2>&1; ri=$?', 'ri=0'),
 ("HPSS_PIN_FORMAT", H, 'for v in "$EVW_SHA" "$CFG_SHA" "$BOUND" "$DONE_SHA"; do hex64 "$v" || bail', 'for v in; do hex64 "$v" || bail'),
 ("HPSS_JOB_FORMAT", H, 'case "$JOBID" in *[!0-9]*|"") bail', 'case "$JOBID" in "") bail'),
 ("DEP_PIN_FORMAT", D, 'hex64 "$v" || { echo "STOP: a digest pin is not 64 hex', 'true || { echo "STOP: a digest pin is not 64 hex'),
 ("DEP_JOB_FORMAT", D, 'case "$JOBID" in *[!0-9]*|"") echo "STOP: the job pin is not a number', 'case "$JOBID" in "") echo "STOP: the job pin is not a number'),
 ("FILL_WT_REGULAR", F, '[ -f "$TOP/$f" ] && [ ! -L "$TOP/$f" ] || { echo "STOP: $f is not a regular file in the working tree"', 'true || { echo "STOP: $f is not a regular file in the working tree"'),
 ("DEP_LC_ALL", D, 'export LC_ALL=C                 # byte semantics', '#export LC_ALL=C                # byte semantics'),
 ("DEP_NUL", D, 'tr -d \'\\000\' < "$log" | cmp -s - "$log" || { echo "the receipt log holds a NUL byte"; v=0; }', 'true'),
 ("DEP_FETCH_FINAL_TF", D, 'grep -Fxq "htar -tf (final) rc=0" "$log" || v=0', 'true'),
 ("DEP_FETCH_FINAL_LIST", D, 'grep -Fxq "the final archive lists 6 of 6 pinned names" "$log" || v=0', 'true'),
 ("DEP_LANE_FORM", D, 'case "$LANE" in /pscratch/sd/j/josephrb/evw2d-20', 'case "$LANE" in *evw2d-20'),
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
