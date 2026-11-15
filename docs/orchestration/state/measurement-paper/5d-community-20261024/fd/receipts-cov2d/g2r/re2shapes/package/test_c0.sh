#!/bin/bash
# c0_sums.py on synthetic partc-r2 / c0 trees, after the real re2c_determinism.py (M's) has compared them. Each tree's
# SHA256SUMS is made as re2c_run.sh:199-200 makes it. The c0 tree names its own namespace and deploy inside a JSON
# record (undone by the path pairs), and its logs/, PDF and ROOT bytes differ (skipped categories).
#   bash test_c0.sh re2c_determinism.at-M.py
set -u
CMP=$1; H=$(cd "$(dirname "$0")" && pwd); PY=${PY:-/opt/homebrew/bin/python3.13}
T0=$(mktemp -d "${TMPDIR:-/tmp}/tc0.XXXXXX"); fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
mk() {  # mk <root> <ns> <deploy> <logtext> <npzbyte>
  mkdir -p "$1/logs" "$1/s5" "$1/combination" "$1/chi2"
  printf '%s' "$4" > "$1/logs/run.txt"; printf 'x=%s' "$5" > "$1/s5/production_cov.npz"
  printf 'root %s' "$4" > "$1/s5/uq_production_covariance.root"; printf 'pdf %s' "$4" > "$1/chi2/a.pdf"; printf 'png' > "$1/chi2/a.png"
  printf '{"path": "/pscratch/sd/j/josephrb/%s/x", "code": "/pscratch/sd/j/josephrb/%s/2d-unfolding/re2/partc/re2c_combine.py"}' "$2" "$3" > "$1/combination/combination.json"
  (cd "$1" && find . -type f ! -path './tmp/*' ! -path './mpl/*' ! -name SHA256SUMS -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$1/SHA256SUMS"
}
PP=(--path-pair /cov2d-re2shapes-20261114/c0=/2d-closeout-re2-20261023/partc-r2 --path-pair /cov2d-re2shapes-20261114/deploy-903fb78b=/2d-closeout-re2-20261023/deploy-903fb78b)
run() {  # run <case> <want rc>
  "$PY" -I "$CMP" --stopped "$R2" --rerun "$C0" "${PP[@]}" --out "$T0/$1.det.json" > "$T0/$1.det.out" 2>&1
  "$PY" -I "$H/c0_sums.py" --comparator "$CMP" --determinism "$T0/$1.det.json" --partc-r2 "$R2" --c0 "$C0" --out "$T0/$1.json" > "$T0/$1.out" 2>&1; r=$?
  [ "$r" = "$2" ] && ok "$1 rc=$r: $(head -c 230 "$T0/$1.out")" || { bad "$1 rc=$r want $2"; cat "$T0/$1.det.out" "$T0/$1.out"; }
}
case_() { R2=$T0/$1/2d-closeout-re2-20261023/partc-r2; C0=$T0/$1/cov2d-re2shapes-20261114/c0
  mk "$R2" 2d-closeout-re2-20261023/partc-r2 2d-closeout-re2-20261023/deploy-903fb78b "log-old" 1; }
case_ same; mk "$C0" cov2d-re2shapes-20261114/c0 cov2d-re2shapes-20261114/deploy-903fb78b "log-new" 1; run same 0
grep -q '"SHA256SUMS": "SHA256SUMS"\|"combination/combination.json": "path-pairs (equal)"' "$T0/same.json" && ok "same: combination.json classed path-pairs" || bad "same: classes"
case_ npz; mk "$C0" cov2d-re2shapes-20261114/c0 cov2d-re2shapes-20261114/deploy-903fb78b "log-new" 2; run npz 1
grep -q '"other": \[' "$T0/npz.json" && grep -q 's5/production_cov.npz' "$T0/npz.json" && ok "npz: the differing npz is OTHER" || bad "npz: OTHER"
case_ extra; mk "$C0" cov2d-re2shapes-20261114/c0 cov2d-re2shapes-20261114/deploy-903fb78b "log-new" 1; printf 'y' > "$C0/s5/g2r_driver.json"
(cd "$C0" && find . -type f ! -path './tmp/*' ! -path './mpl/*' ! -name SHA256SUMS -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$C0/SHA256SUMS"; run extra 1
case_ wrongdeploy; mk "$C0" cov2d-re2shapes-20261114/c0 cov2d-re2shapes-20261114/deploy-9855389f "log-new" 1; run wrongdeploy 1
find "$T0" -type f -exec rm -f {} +; find "$T0" -depth -type d -exec rmdir {} \;
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "C0 TEST PASS" || echo "C0 TEST FAILED"
exit $fail
