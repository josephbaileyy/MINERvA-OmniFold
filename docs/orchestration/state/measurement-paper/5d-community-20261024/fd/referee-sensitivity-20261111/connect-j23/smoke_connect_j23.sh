#!/bin/bash
# Local smoke of rsn_connect_j23.sh (macOS or Linux; never connects, never submits). Usage:
#   bash smoke_connect_j23.sh <new empty work dir> <a local clone that contains M_P1>
# The repository the connect clones is a clone of M_P1 plus ONE throwaway local commit that changes only reweight pins:
# pv-ladder's prep-SHA256SUMS lines for tune_v1 and nuwro, and RSN's committed rsn-prep-SHA256SUMS (the four RSN
# reweights), each to a synthetic file's sha256 (the real reweights are on the cluster). The nine bound RSN files are
# unchanged. The connect copy differs from rsn_connect_j23.sh only in B and P (-> the work dir), PIN (-> that commit),
# PY (-> a stub), REPO (-> the local template) and the host test (-> $FAKE_HOST). The bound launcher (sbatch_rsn.sh,
# unchanged, its sha checked by the connect) runs in its own RSN_SMOKE mode. Stubs: hostname, squeue ($SMOKE_SQUEUE),
# sacct ($SMOKE_SACCT), sbatch (records its argv; fails for a job named in $SMOKE_SBATCH_FAIL), timeout, and the
# python, whose rsn_cmodel.py nc writes an nc.json as the real one would ($SMOKE_NC = pass, fail or badcode); the
# real NC needs the frozen products, which are on the cluster.
W=${1:?work dir}; CLONE=${2:?local clone}
HERE=$(cd "$(dirname "$0")" && pwd)
MP1=5e43e509d08d9b294594988f2c21e50e281e7ad8
J1=61168780
[ -d "$W" ] && [ -z "$(ls -A "$W")" ] || { echo "STOP: $W is not a new empty directory"; exit 9; }
mkdir -p "$W/bin" "$W/pvlprep/ratios/L-5D-PV" "$W/rsnprep/G6" "$W/rsnprep/SM"
printf '#!/bin/bash\necho "${FAKE_HOST:-login27}"\n' > "$W/bin/hostname"
printf '#!/bin/bash\nif [ "$1" = -j ]; then echo "$2|rsn_Jx|PENDING|22:00|regular_milan_ss11|regular_1|1"; exit 0; fi\n[ -n "$SMOKE_SQUEUE" ] && printf "%%s\\n" "$SMOKE_SQUEUE"; exit 0\n' > "$W/bin/squeue"
printf '#!/bin/bash\nprintf "%%s\\n" "${SMOKE_SACCT:-%s|rsn_J1|COMPLETED|0:0|00:14:10}"\n' "$J1" > "$W/bin/sacct"
cat > "$W/bin/sbatch" <<EOF
#!/bin/bash
for a in "\$@"; do case "\$a" in --job-name=*) n=\${a#--job-name=} ;; esac; done
[ -n "\$SMOKE_SBATCH_FAIL" ] && [ "\$n" = "\$SMOKE_SBATCH_FAIL" ] && { echo "sbatch: error: stub refusal" >&2; exit 1; }
echo "\$*" >> "$W/sbatch.argv"; case "\$n" in rsn_J2) echo 61300002 ;; *) echo 61300003 ;; esac
EOF
printf '#!/bin/bash\nshift; exec "$@"\n' > "$W/bin/timeout"
cat > "$W/pystub" <<'PYSTUB'
#!/bin/bash
# stands in for the root_6_28 python: rsn_cmodel.py nc writes the nc.json the real code writes; all else is python3
case "$*" in
  *rsn_cmodel.py*" nc "*)
    prod=""; out=""; prev=""; code=""
    for a in "$@"; do
      [ "$prev" = --product ] && prod="$a"; [ "$prev" = --out ] && out="$a"; prev="$a"
      case "$a" in *rsn_cmodel.py) code="$a" ;; esac
    done
    [ "${SMOKE_NC:-pass}" = fail ] && { echo "[FAIL] rsn_nc: stub mismatch" >&2; exit 1; }
    cs=$(sha256sum "$code" | cut -d' ' -f1); [ "${SMOKE_NC:-pass}" = badcode ] && cs=0000
    printf '{\n "schema": "rsn-nc/1",\n "product_sha256": "%s",\n "nominal_control": {"stub": true},\n "verdict": "PASS",\n "code_sha256": {"rsn_cmodel.py": "%s"}\n}\n' \
      "$(sha256sum "$prod" | cut -d' ' -f1)" "$cs" > "$out"
    echo "[rsn] NC PASS: rsn_nc equals P5 and L-5D-PV_e_tune_v1 bitwise"; exit 0 ;;
  *) while [ "$1" = -I ] || [ "$1" = -B ]; do shift; done; exec python3 "$@" ;;
esac
PYSTUB
chmod +x "$W/bin/"* "$W/pystub"
for f in tune_v1 nuwro; do echo "{\"synthetic\": \"$f\"}" > "$W/pvlprep/ratios/L-5D-PV/$f.json"; done
for f in G6/gibuu SM/genie_mec SM/gibuu SM/nuwro; do echo "{\"synthetic\": \"$f\"}" > "$W/rsnprep/$f.json"; done
git clone -q "$CLONE" "$W/template" && git -C "$W/template" -c advice.detachedHead=false checkout -q "$MP1" || exit 1
python3 - "$W" <<'EOF' || exit 1
import hashlib, os, sys
w = sys.argv[1]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
pv = os.path.join(w, "template/nd-unfolding/pv-ladder/prep-SHA256SUMS")
lines = open(pv).read().splitlines()
for k in ("tune_v1", "nuwro"):
    tag = f"./ratios/L-5D-PV/{k}.json"
    i = [j for j, ln in enumerate(lines) if ln.endswith("  " + tag)]
    assert len(i) == 1, tag
    lines[i[0]] = f"{h(os.path.join(w, 'pvlprep/ratios/L-5D-PV', k + '.json'))}  {tag}"
open(pv, "w").write("\n".join(lines) + "\n")
rs = os.path.join(w, "template/nd-unfolding/rsn/rsn-prep-SHA256SUMS")
rows = [ln.split()[1] for ln in open(rs).read().splitlines() if ln.strip()]
assert rows == ["./G6/gibuu.json", "./SM/genie_mec.json", "./SM/gibuu.json", "./SM/nuwro.json"], rows
open(rs, "w").write("".join(f"{h(os.path.join(w, 'rsnprep', r[2:]))}  {r}\n" for r in rows))
EOF
git -C "$W/template" -c user.name=smoke -c user.email=smoke@invalid commit -q -am "smoke: synthetic reweight pins" || exit 1
SPIN=$(git -C "$W/template" rev-parse HEAD)
echo "smoke: template $SPIN = M_P1 + synthetic reweight pins; bound files unchanged:" \
  "$(git -C "$W/template" diff --name-only "$MP1" "$SPIN" | tr '\n' ' ')"
mkB() {  # mkB <case>: a fresh B in the state J1 leaves (fence, nc_r.json, connect 1's sums and prep, J1's log, product)
  local b="$W/b-$1" o="$W/b-$1/out"; mkdir -p "$o/logs" "$o/products"
  printf '%s\n' cov2d t2a ll5d e96data rpd_ > "$o/fence.txt"
  printf '{\n "schema": "rsn-nc-r/1",\n "verdict": "PASS"\n}\n' > "$o/nc_r.json"
  cp "$W/template/nd-unfolding/rsn/rsn-prep-SHA256SUMS" "$o/rsn-prep-SHA256SUMS"; cp -R "$W/rsnprep" "$o/prep"
  echo "synthetic rsn_nc" > "$o/products/rsn_nc.npz"
  { echo "[rsn] job=J1 slurm=$J1 node=nid004001 tasks=1 mem_per_step=486400M cpus_per_step=42 start=2026-11-12T13:20:00Z"
    sha256sum "$o/products/rsn_nc.npz"; echo "[rsn] job=J1 rc=0 end=2026-11-12T13:34:10Z"; } > "$o/logs/rsn_J1_$J1.out"
  python3 - "$HERE/rsn_connect_j23.sh" "$W/$1.sh" "$W" "$b" "$SPIN" <<'EOF'
import sys
src, dst, w, b, spin = sys.argv[1:6]
s = open(src).read()
for a, c in (("P=/pscratch/sd/j/josephrb", f"P={w}"), ("B=$P/rsn-20261112", f"B={b}"),
             ("PIN=5e43e509d08d9b294594988f2c21e50e281e7ad8", f"PIN={spin}"),
             ("PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3", f"PY={w}/pystub"),
             ("REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git", f"REPO={w}/template"),
             ('case "$(hostname -s)" in login[0-9][0-9])', 'case "${FAKE_HOST:-login27}" in login[0-9][0-9])')):
    assert s.count(a) == 1, a
    s = s.replace(a, c)
open(dst, "w").write(s)
EOF
}
run() {  # run <case> <step> [env...]
  local n=$1 st=$2; shift 2
  cp "$W/$n.sh" "$W/$n.self.sh"; rm -f "$W/sbatch.argv"
  env PATH="$W/bin:$PATH" RSN_PVL_PREP="$W/pvlprep" "$@" bash "$W/$n.self.sh" "$W/$n.self.sh" "$st" > "$W/$n.$st.out" 2>&1
  echo "## case $n $st rc=$?"
  grep -E 'REFUSED|STOP|NC PASS|NC STEP PASS|gates/J.\.ok sha256|^pin=|smoke J. rc|smoke: checks|sbatch J. rc|SUBMITTED|refusing' "$W/$n.$st.out" \
    | sed -E -e "s|$W|<w>|g" -e "s|$SPIN|<smoke-pin>|g" | cut -c1-200
  echo "sbatch called: $([ -s "$W/sbatch.argv" ] && sed -e "s|$W|<w>|g" -e "s|$SPIN|<smoke-pin>|g" "$W/sbatch.argv" || echo no)"
  echo "nc.json: $([ -e "$W/b-$n/out/nc.json" ] && echo yes || echo no); gates: $([ -e "$W/b-$n/out/gates" ] && echo yes || echo no); self copy removed: $([ -e "$W/$n.self.sh" ] && echo no || echo yes)"
}
# step nc
mkB pass;     run pass nc
mkB j1q;      run j1q nc "SMOKE_SQUEUE=$J1|rsn_J1|RUNNING"
mkB e96;      run e96 nc "SMOKE_SQUEUE=61200000|e96data_full|PENDING"
mkB host;     run host nc FAKE_HOST=dtn01
mkB slurm;    run slurm nc SLURM_JOB_ID=1
mkB j1fail;   run j1fail nc "SMOKE_SACCT=$J1|rsn_J1|FAILED|1:0|00:03:10"
mkB j1rc;     sed -i.bak '/job=J1 rc=0/d' "$W/b-j1rc/out/logs/rsn_J1_$J1.out"; run j1rc nc
mkB prodsha;  echo tampered > "$W/b-prodsha/out/products/rsn_nc.npz"; run prodsha nc
mkB ncexists; echo '{}' > "$W/b-ncexists/out/nc.json"; run ncexists nc
mkB depexists; mkdir -p "$W/b-depexists/deploy-p1"; run depexists nc
mkB sums;     echo "0000  ./extra.json" >> "$W/b-sums/out/rsn-prep-SHA256SUMS"; run sums nc
mkB ncfail;   run ncfail nc SMOKE_NC=fail
mkB badcode;  run badcode nc SMOKE_NC=badcode
mkB badstep;  run badstep j9
# step submit, from the pass case's state after its nc step
for c in sub subgate subnonc subdirty sube96 subj2fail subj3fail; do
  mkB "$c"; rm -rf "$W/b-$c/out"; cp -R "$W/b-pass/out" "$W/b-$c/out"; cp -R "$W/b-pass/deploy-p1" "$W/b-$c/deploy-p1"
done
run sub submit
echo "pin=0000" > "$W/b-subgate/out/gates/J3.ok"; run subgate submit
rm -f "$W/b-subnonc/out/nc.json"; run subnonc submit
echo x > "$W/b-subdirty/deploy-p1/nd-unfolding/rsn/stray.txt"; run subdirty submit
run sube96 submit "SMOKE_SQUEUE=61200000|e96data_full|PENDING"
run subj2fail submit SMOKE_SBATCH_FAIL=rsn_J2
run subj3fail submit SMOKE_SBATCH_FAIL=rsn_J3
