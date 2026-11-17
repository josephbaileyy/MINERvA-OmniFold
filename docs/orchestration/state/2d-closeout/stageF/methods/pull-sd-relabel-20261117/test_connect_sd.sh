#!/bin/bash
# Stand-in test of the filled connect-sd.sh, on the laptop. A copy runs with exact substitutions (each asserted once):
# P -> a temp tree, URL -> this repository (git clone --shared), LOG -> the temp tree, and `source setup_salloc_env.sh`
# -> `true`. Shims: squeue, sacct, nproc, hostname, timeout (runs the command), sha256sum (-c, in python), and python3:
# the environment probe prints; the O_NOATIME hash answers E_R's and the covariance's pinned digests (another by
# scenario); boxes.py runs for real (miniconda python) with the deploy's toy_pull.py in place of the producer, so the
# three arms draw through boxes.py and capture.py as on the cluster. The deploy is a real clone at PKG, the base tree a
# real git archive of db5276148, and the code-sha checks are real. The clean scenario's arms then go through check_sd.py
# (the "installed" figure is the stand-in's own "before" PDF). Each other scenario must STOP with its own reason.
#   bash test_connect_sd.sh <filled connect> <repo worktree> <PKG>
set -u
CONN=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); REPO=$(cd "$2" && pwd); PKG=$3
H=$(cd "$(dirname "$0")" && pwd); T0=$(mktemp -d "${TMPDIR:-/tmp}/tcs.XXXXXX"); SH=$T0/shims; mkdir -p "$SH"; fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
REALGIT=$(command -v git); REALPY=/opt/homebrew/bin/python3.13; MPY=/Users/josephbailey/miniconda3/bin/python3
cat > "$SH/git" <<EOF
#!/bin/bash
if [ "\$1" = clone ]; then shift; [ "\$1" = --quiet ] && shift; exec "$REALGIT" clone --quiet --shared "$REPO" "\$2"; fi
exec "$REALGIT" "\$@"
EOF
cat > "$SH/squeue" <<'EOF'
#!/bin/bash
n=$(( $(cat "$SC_CNT" 2>/dev/null || echo 0) + 1 )); echo $n > "$SC_CNT"
[ -n "${SC_SQ_RC:-}" ] && [ "$n" -ge "${SC_SQ_FROM:-1}" ] && { echo "squeue: error" >&2; exit "$SC_SQ_RC"; }
echo "JOBID|NAME|STATE|TIME_LIMIT|NODES"; for j in ${SC_SQ_NAMES:-}; do echo "1|$j|RUNNING|0:22:00|1"; done
EOF
cat > "$SH/sacct" <<'EOF'
#!/bin/bash
if [[ "$*" == *"--name rdx_s1_1A"* ]]; then printf '%b' "61300000|rdx_s1_1A|COMPLETED|2026-11-14T20:00:00\n"
else printf '%b' "61300000|rdx_s1_1A|COMPLETED\n61443055|rdx_s2_merge|COMPLETED\n"; [ -n "${SC_UNENDED:-}" ] && printf '%b' "61500000|rdx_s3_a|RUNNING\n"; fi
exit 0
EOF
printf '#!/bin/bash\necho 256\n' > "$SH/nproc"; printf '#!/bin/bash\necho login99\n' > "$SH/hostname"
printf '#!/bin/bash\nshift; exec "$@"\n' > "$SH/timeout"
cat > "$SH/sha256sum" <<EOF
#!/bin/bash
exec "$REALPY" - "\$@" <<'PY'
import hashlib, sys
a = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
if a and a[0] == "-c":
    bad = 0
    for ln in open(a[1]).read().splitlines():
        d, p = ln.split(None, 1)
        try: good = h(p) == d
        except OSError: good = False
        bad += not good; print(f"{p}: {'OK' if good else 'FAILED'}")
    sys.exit(1 if bad else 0)
for p in a:
    try: print(f"{h(p)}  {p}")
    except OSError: print(f"sha256sum: {p}: No such file", file=sys.stderr)
PY
EOF
cat > "$SH/python3" <<EOF
#!/bin/bash
case "\$1" in
  -c)
    case "\$2" in
      *ROOT*matplotlib*) echo "python 3.11.9"; echo "ROOT 6.28/10"; echo "matplotlib 3.9.2"; echo "numpy 1.26.4"; exit 0 ;;
      *O_NOATIME*) case "\$3" in
          *xsec.root) [ -n "\${SC_XBAD:-}" ] && { echo 0000; exit 0; }; echo a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef ;;
          *cov_ptpl_minerva_inclusive_6GeV.root) echo 6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3 ;;
          *) echo "unexpected O_NOATIME read \$3"; exit 98 ;;
        esac; exit 0 ;;
    esac ;;
  -I) shift; [ "\$1" = -B ] && shift
      case "\$1" in
        */boxes.py) bx=\$1 cap=\$2 dep=\$3; shift 4
            arm=\$(basename "\$(dirname "\$(dirname "\$cap")")")
            [ "\${SC_ARM_FAIL:-}" = "\$arm" ] && { echo "producer failed (stand-in)"; exit 3; }
            [ -n "\${SC_STRAY:-}" ] && [ "\$arm" = off ] && touch "\$SC_STRAY"
            exec "$MPY" -I -B "\$bx" "\$cap" "\$dep" "\$(dirname "\$bx")/toy_pull.py" "\$@" ;;
      esac ;;
esac
echo "unexpected python3 \$*"; exit 99
EOF
chmod +x "$SH"/*
run() {  # run <scenario> <connect copy source> [VAR=value ...]: a fresh tree; the log in $T0/<scenario>/connect.log
  local sc=$1 src=$2; shift 2
  local T=$T0/$sc; mkdir -p "$T/p/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc" "$T/p/MINERvA-OmniFold/docs" \
    "$T/p/2d-closeout-re2-20261023/partb/out/ER"
  printf 'E_R stand-in\n' > "$T/p/2d-closeout-re2-20261023/partb/out/ER/xsec.root"
  printf 'covariance stand-in\n' > "$T/p/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"
  printf 'x\n' > "$T/p/MINERvA-OmniFold/docs/readme"
  "$REALPY" - "$src" "$T/connect.sh" "$T" "$REPO" <<'PY'
import sys
src, dst, T, repo = sys.argv[1:5]
s = open(src).read()
for a, b in (("P=/pscratch/sd/j/josephrb\n", f"P={T}/p\n"), ("URL=https://github.com/josephbaileyy/MINERvA-OmniFold\n", f"URL={repo}\n"),
             ("LOG=/dev/shm/josephrb-pullsd.log\n", f"LOG={T}/connect.log\n"),
             ('source "$DEP/setup_salloc_env.sh" > "$W/logs/env.log" 2>&1\n', "true\n")):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(dst, "w").write(s)
PY
  (export PATH="$SH:$PATH" SC_CNT=$T/sqcount "$@"; cd "$T" && bash "$T/connect.sh" > "$T/stdout" 2>&1); echo $? > "$T/rc"
}
expect_stop() {  # expect_stop <scenario> <reason regex>
  local T=$T0/$1
  grep -qE "^STOP $2" "$T/connect.log" && grep -q '^PULLSD INVALID (connect)$' "$T/connect.log" && [ "$(cat "$T/rc")" = 2 ] \
    && ok "$1 (rc 2): $(grep '^STOP' "$T/connect.log" | head -1 | cut -c1-100)" \
    || { bad "$1 (rc $(cat "$T/rc"))"; tail -5 "$T/connect.log" 2>/dev/null; }
}
# clean
run clean "$CONN"
T=$T0/clean; W=$T/p/note-pullsd-20261117
grep -q '^PULLSD CONNECT PASS' "$T/connect.log" && [ "$(cat "$T/rc")" = 0 ] && grep -q '^DONE$' "$T/connect.log" \
  && ok "clean (rc 0): $(grep -c '^fence (' "$T/connect.log") fences clear; $(grep -c ': OK$' "$T/connect.log") code shas OK; arms $(grep -o '^arm [a-z]* rc=0' "$T/connect.log" | awk '{print $2}' | paste -sd, -)" \
  || { bad "clean (rc $(cat "$T/rc"))"; tail -20 "$T/connect.log"; }
grep -q 'newer than the marker: 0$' "$T/connect.log" && [ -s "$W/SHA256SUMS" ] && (cd "$W" && shasum -a 256 -c SHA256SUMS > /dev/null) \
  && ok "clean: no stray write; SHA256SUMS ($(awk 'END {print NR}' "$W/SHA256SUMS") files) verifies" || bad "clean: stray count or SHA256SUMS"
"$MPY" -I "$H/check_sd.py" --before "$W/before" --off "$W/off" --after "$W/after" --installed "$W/before/out/MEFHC_5iter_pull_full.pdf" \
  --installed-sha "$(shasum -a 256 "$W/before/out/MEFHC_5iter_pull_full.pdf" | cut -d' ' -f1)" --deploy "$W/deploy" \
  --strip "$W/before=RUN" --strip "$W/off=RUN" --strip "$W/after=RUN" > "$T/check.out" 2>&1 \
  && grep -q '^CHECK_SD :: PASS$' "$T/check.out" && ok "clean: check_sd.py on the stand-in's arms: $(grep -c '^PASS K' "$T/check.out") checks PASS" \
  || { bad "clean: check_sd.py"; cat "$T/check.out"; }
# the fence, the inputs, the code, the arms
run job-queued "$CONN" SC_SQ_NAMES=rdx_s3_a;              expect_stop job-queued "a job of josephrb is queued or running"
run squeue-fails "$CONN" SC_SQ_RC=1;                       expect_stop squeue-fails "squeue failed \(rc 1\)"
run unended "$CONN" SC_UNENDED=1;                          expect_stop unended "a job of josephrb is unended"
run fence-arms "$CONN" SC_SQ_RC=1 SC_SQ_FROM=2;            expect_stop fence-arms "squeue failed \(rc 1\)"
[ ! -e "$T0/fence-arms/p/note-pullsd-20261117/before" ] && grep -q '^fence (start) clear' "$T0/fence-arms/connect.log" \
  && ok "fence-arms: the start fence cleared, the second refused, and no arm ran" || bad "fence-arms: an arm ran"
mkdir -p "$T0/figmark/p/note-figstyle-20261114" && echo "group C" > "$T0/figmark/p/note-figstyle-20261114/RUNNING"
run figmark "$CONN";                                       expect_stop figmark "a group C figure connect is running"
mkdir -p "$T0/w-exists/p/note-pullsd-20261117"
run w-exists "$CONN";                                      expect_stop w-exists ".*note-pullsd-20261117 exists"
run x-bad "$CONN" SC_XBAD=1;                               expect_stop x-bad "E_R is not its pinned digest"
"$REALPY" - "$CONN" "$T0/code-bad.sh" <<'PY'
import re, sys
s = open(sys.argv[1]).read(); m = re.search(r"SHA_BOXES=([0-9a-f]{64});", s); assert m
open(sys.argv[2], "w").write(s.replace(m.group(0), "SHA_BOXES=" + "0" * 64 + ";"))
PY
run code-bad "$T0/code-bad.sh";                            expect_stop code-bad "a code file is not its pinned sha256"
run arm-fails "$CONN" SC_ARM_FAIL=after;                   expect_stop arm-fails "arm after rc=3"
run stray "$CONN" SC_STRAY="$T0/stray/p/MINERvA-OmniFold/docs/stray.txt"; expect_stop stray "a stray write \(1 file"
run unfilled "$H/connect-sd.template.sh";                  expect_stop unfilled "PKG is not filled"
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "PULLSD CONNECT TEST PASS" || echo "PULLSD CONNECT TEST FAILED"
exit $fail
