#!/bin/bash
# c0_sums.py on synthetic partc-r2 / c0 trees, after the real re2c_determinism.py (M's) has compared them. Each tree's
# SHA256SUMS is made as re2c_run.sh:199-200 makes it (so periods_ns/tmp/<mkdtemp>/ is listed). The c0 tree names its
# own namespace and deploy inside a JSON record (undone by the path pairs); its logs/, PDF and ROOT bytes differ
# (skipped categories); its period-selftest scratch sits under a different random mkdtemp name, as every real run's
# does (coverage-5b-audit blocker 1), with the five files' shapes as the O_NOATIME probe found them (id.txt and
# inj.txt bitwise; id.json and inj.json naming the run's own paths and mkdtemp name; inj.json recording inj.root's
# sha256; inj.root differing). values_table.tsv must be bitwise (the director's M2). Rev 3 (the director's (a2)):
# each run writes receipts/receipt_model_chi2.json with its own generated_by path, time, host and repo_commit (R1), and
# partc-r2's directory gains the 8 later fig1/ and fig1-a2-cabbbbc3/ files AFTER its SHA256SUMS is written (R2).
#   bash test_c0.sh re2c_determinism.at-M.py
set -u
CMP=$1; H=$(cd "$(dirname "$0")" && pwd); PY=${PY:-/opt/homebrew/bin/python3.13}
T0=$(mktemp -d "${TMPDIR:-/tmp}/tc0.XXXXXX"); fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
mk() {  # mk <root> <ns> <deploy> <logtext> <npzbyte> <mkdtemp name> <value> [inj.root digest to record] [chi2] [commit]
  mkdir -p "$1/logs" "$1/s5" "$1/combination" "$1/chi2" "$1/periods_ns/tmp/$6"
  printf '%s' "$4" > "$1/logs/run.txt"; printf 'x=%s' "$5" > "$1/s5/production_cov.npz"
  printf 'root %s' "$4" > "$1/s5/uq_production_covariance.root"; printf 'pdf %s' "$4" > "$1/chi2/a.pdf"; printf 'png' > "$1/chi2/a.png"
  printf '{"path": "/pscratch/sd/j/josephrb/%s/x", "code": "/pscratch/sd/j/josephrb/%s/2d-unfolding/re2/partc/re2c_combine.py"}' "$2" "$3" > "$1/combination/combination.json"
  printf 'id\tvalue\nm-uqMedian\t%s\n' "$7" > "$1/values_table.tsv"
  local d=$1/periods_ns/tmp/$6 q=/pscratch/sd/j/josephrb/$2/periods_ns/tmp/$6
  printf 'id table\n' > "$d/id.txt"; printf 'inj table\n' > "$d/inj.txt"; printf 'TFile %s' "$4" > "$d/inj.root"
  printf '{"work": "/pscratch/sd/j/josephrb/%s/work_cov/work_cov.npz", "out": "%s/id.json"}' "$2" "$q" > "$d/id.json"
  local rs=${8:-$(shasum -a 256 "$d/inj.root" | cut -c1-64)}
  printf '{"s42": "%s/inj.root", "inputs": {"%s/inj.root": {"path": "%s/inj.root", "sha256": "%s"}}}' "$q" "$q" "$q" "$rs" > "$d/inj.json"
  mkdir -p "$1/receipts"
  printf '{"generated_by": "/pscratch/sd/j/josephrb/%s/2d-unfolding/receipt_model_chi2_2d.py", "generated_utc": "%s", "host": "%s", "repo_commit": "%s", "chi2": {"GENIE": %s}}' \
    "$3" "$4" "host-$4" "${10:-32e403b8}" "${9:-123.456}" > "$1/receipts/receipt_model_chi2.json"
  sums "$1"
}
sums() { (cd "$1" && find . -type f ! -path './tmp/*' ! -path './mpl/*' ! -name SHA256SUMS -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) > "$1/SHA256SUMS"; }
PP=(--path-pair /cov2d-re2shapes-20261115/c0=/2d-closeout-re2-20261023/partc-r2 --path-pair /cov2d-re2shapes-20261115/deploy-903fb78b=/2d-closeout-re2-20261023/deploy-903fb78b)
NEWNS=cov2d-re2shapes-20261115/c0; NEWDEP=cov2d-re2shapes-20261115/deploy-903fb78b
run() {  # run <case> <want rc>
  "$PY" -I "$CMP" --stopped "$R2" --rerun "$C0" "${PP[@]}" --out "$T0/$1.det.json" > "$T0/$1.det.out" 2>&1
  "$PY" -I "$H/c0_sums.py" --comparator "$CMP" --determinism "$T0/$1.det.json" --partc-r2 "$R2" --c0 "$C0" "${PP[@]}" --out "$T0/$1.json" > "$T0/$1.out" 2>&1; r=$?
  [ "$r" = "$2" ] && ok "$1 rc=$r: $(head -c 240 "$T0/$1.out")" || { bad "$1 rc=$r want $2"; cat "$T0/$1.det.out" "$T0/$1.out"; }
}
fig1later() { for d in fig1 fig1-a2-cabbbbc3; do mkdir -p "$1/$d"; for f in RUN-fig1.txt fig1_run.log pins.json uqmedian.tex; do printf '%s' "$d/$f" > "$1/$d/$f"; done; done; }
case_() { R2=$T0/$1/2d-closeout-re2-20261023/partc-r2; C0=$T0/$1/cov2d-re2shapes-20261115/c0
  mk "$R2" 2d-closeout-re2-20261023/partc-r2 2d-closeout-re2-20261023/deploy-903fb78b "log-old" 1 tmp6hw50588 6.448; fig1later "$R2"; }
case_ same; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448 "" "" ed3590ea; run same 0
grep -q '"receipts/receipt_model_chi2.json": "R1 (receipt equal without repo_commit' "$T0/same.json" && grep -q '"R1_receipt": true' "$T0/same.json" \
  && grep -q '"R2_only_stopped_fig1_later": true' "$T0/same.json" && ok "same: R1 (receipt differs only in time, host, path, repo_commit) and R2 (the 8 later fig1 files) accepted" || { bad "same: R1/R2"; cat "$T0/same.json"; }
grep -q '"combination/combination.json": "path-pairs (equal)"' "$T0/same.json" && grep -q '"values_table.tsv": "bitwise"' "$T0/same.json" \
  && grep -q '"periods_ns/tmp/<mkdtemp>/id.json": "scratch (id.json: equal after' "$T0/same.json" \
  && grep -q '"periods_ns/tmp/<mkdtemp>/inj.json": "scratch (inj.json: equal after the path pairs and the mkdtemp name, inj.root digest)"' "$T0/same.json" \
  && grep -q '"periods_ns/tmp/<mkdtemp>/inj.root": "scratch (inj.root: TFile time' "$T0/same.json" \
  && grep -q '"periods_ns/tmp/<mkdtemp>/inj.txt": "bitwise"' "$T0/same.json" && grep -q '"c0": "tmpq3zk81xa"' "$T0/same.json" \
  && ok "same: path-pairs, values_table bitwise, the five scratch files each by its rule under two mkdtemp names" || { bad "same: classes"; cat "$T0/same.json"; }
case_ npz; mk "$C0" $NEWNS $NEWDEP "log-new" 2 tmpq3zk81xa 6.448; run npz 1
grep -q 's5/production_cov.npz' "$T0/npz.json" && ok "npz: the differing npz is OTHER" || bad "npz: OTHER"
case_ extra; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448; printf 'y' > "$C0/s5/g2r_driver.json"; sums "$C0"; run extra 1
case_ wrongdeploy; mk "$C0" $NEWNS cov2d-re2shapes-20261115/deploy-9855389f "log-new" 1 tmpq3zk81xa 6.448; run wrongdeploy 1
case_ values-one-value; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.449; run values-one-value 1
grep -q '"values_table.tsv": "OTHER (values table differs)"' "$T0/values-one-value.json" && ok "values-one-value: one printed value changed is OTHER" || bad "values-one-value: class"
case_ scratch-extra; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448; printf 'x' > "$C0/periods_ns/tmp/tmpq3zk81xa/inj2.txt"; sums "$C0"; run scratch-extra 1
grep -q '"periods_ns/tmp/tmpq3zk81xa/inj2.txt": "OTHER (only in c0)"' "$T0/scratch-extra.json" && ok "scratch-extra: a file outside the five is OTHER" || bad "scratch-extra: class"
case_ scratch-missing; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448; find "$C0/periods_ns/tmp/tmpq3zk81xa" -name inj.txt -delete; sums "$C0"; run scratch-missing 1
grep -q '"periods_ns/tmp/<mkdtemp>/inj.txt": "OTHER (only in partc-r2)"' "$T0/scratch-missing.json" && ok "scratch-missing: a missing scratch file is OTHER" || bad "scratch-missing: class"
case_ scratch-txt; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448; printf 'inj table 2\n' > "$C0/periods_ns/tmp/tmpq3zk81xa/inj.txt"; sums "$C0"; run scratch-txt 1
grep -q '"periods_ns/tmp/<mkdtemp>/inj.txt": "OTHER (scratch: must be bitwise)"' "$T0/scratch-txt.json" && ok "scratch-txt: a changed inj.txt is OTHER" || bad "scratch-txt: class"
case_ scratch-rootsha; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448 0000000000000000000000000000000000000000000000000000000000000000; run scratch-rootsha 1
grep -q 'OTHER (scratch: inj.root digest not its inj.json' "$T0/scratch-rootsha.json" && ok "scratch-rootsha: inj.json recording another inj.root digest is OTHER" || bad "scratch-rootsha: class"
case_ scratch-idjson; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448; printf '{"work": "changed"}' > "$C0/periods_ns/tmp/tmpq3zk81xa/id.json"; sums "$C0"; run scratch-idjson 1
grep -q '"periods_ns/tmp/<mkdtemp>/id.json": "OTHER (scratch: id.json differs after normalization)"' "$T0/scratch-idjson.json" && ok "scratch-idjson: a changed id.json is OTHER" || bad "scratch-idjson: class"
case_ receipt-chi2; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448 "" 123.457 ed3590ea; run receipt-chi2 1
grep -q "OTHER (receipt fields differ beyond repo_commit: \['chi2'\])" "$T0/receipt-chi2.json" && ok "receipt-chi2: a second differing receipt field (chi2) is OTHER" || bad "receipt-chi2: class"
case_ ninth-only-stopped; printf 'x' > "$R2/fig1/extra.txt"; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448 "" "" ed3590ea; run ninth-only-stopped 1
grep -q '"R2_only_stopped_fig1_later": false' "$T0/ninth-only-stopped.json" && ok "ninth-only-stopped: a ninth only_stopped file fails R2" || bad "ninth-only-stopped: R2"
case_ seven-only-stopped; find "$R2/fig1" -name pins.json -delete; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448 "" "" ed3590ea; run seven-only-stopped 1
case_ two-mkdtemps; mk "$C0" $NEWNS $NEWDEP "log-new" 1 tmpq3zk81xa 6.448 "" "" ed3590ea; mkdir -p "$C0/periods_ns/tmp/tmpzzzzzzzz"; printf 'z' > "$C0/periods_ns/tmp/tmpzzzzzzzz/id.json"; sums "$C0"; run two-mkdtemps 1
find "$T0" -type f -exec rm -f {} +; find "$T0" -depth -type d -exec rmdir {} \;
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "C0 TEST PASS" || echo "C0 TEST FAILED"
exit $fail
