#!/bin/bash
# Local smoke of rsn_connect_j1.sh (macOS or Linux; never connects, never submits). Usage:
#   bash smoke_connect_j1.sh <new empty work dir> <a local clone that contains M_RSN> <connect 1's nc_r.json>
# The deploy is a clone of M_RSN plus ONE throwaway local commit that changes only pv-ladder's prep-SHA256SUMS line
# for ./ratios/L-5D-PV/tune_v1.json to a synthetic reweight's sha256 (the real frozen reweight is on the cluster). The
# connect copy differs from rsn_connect_j1.sh only in B (-> the work dir), PIN (-> that commit), PY (-> python3) and
# the host test (-> $FAKE_HOST). The bound launcher (sbatch_rsn.sh, unchanged, its sha checked) runs in its own
# RSN_SMOKE mode, with RSN_PVL_PREP pointing at the synthetic prep. Stubs: hostname, squeue ($SMOKE_SQUEUE), sbatch
# (records its argv and prints a job id), and sha256sum where absent.
W=${1:?work dir}; CLONE=${2:?local clone}; NCR=${3:?nc_r.json}
HERE=$(cd "$(dirname "$0")" && pwd)
PIN=af7112989417f180e846573c31d101e44e6b02f9
[ -d "$W" ] && [ -z "$(ls -A "$W")" ] || { echo "STOP: $W is not a new empty directory"; exit 9; }
mkdir -p "$W/bin" "$W/prep/ratios/L-5D-PV"
printf '#!/bin/bash\necho "${FAKE_HOST:-login27}"\n' > "$W/bin/hostname"
printf '#!/bin/bash\nif [ "$1" = -j ]; then echo "61234567|rsn_J1|PENDING|19:00|regular_milan_ss11|regular_1|1"; exit 0; fi\n[ -n "$SMOKE_SQUEUE" ] && printf "%%s\\n" "$SMOKE_SQUEUE"; exit 0\n' > "$W/bin/squeue"
printf '#!/bin/bash\necho "$*" >> "%s/sbatch.argv"; echo 61234567\n' "$W" > "$W/bin/sbatch"
chmod +x "$W/bin/"*
echo '{"synthetic": "tune_v1"}' > "$W/prep/ratios/L-5D-PV/tune_v1.json"
TSHA=$(shasum -a 256 "$W/prep/ratios/L-5D-PV/tune_v1.json" | cut -d' ' -f1)
git clone -q "$CLONE" "$W/template" && git -C "$W/template" -c advice.detachedHead=false checkout -q "$PIN" || exit 1
sed -i.bak "s|^[0-9a-f]\{64\}  \./ratios/L-5D-PV/tune_v1.json$|$TSHA  ./ratios/L-5D-PV/tune_v1.json|" \
  "$W/template/nd-unfolding/pv-ladder/prep-SHA256SUMS" && rm -f "$W/template/nd-unfolding/pv-ladder/prep-SHA256SUMS.bak"
git -C "$W/template" -c user.name=smoke -c user.email=smoke@invalid commit -q -am "smoke: synthetic tune_v1 pin" || exit 1
SPIN=$(git -C "$W/template" rev-parse HEAD)
mk() {  # mk <case>: a fresh B with a clean deploy at SPIN and connect 1's nc_r.json; the connect copy
  local b="$W/b-$1"; mkdir -p "$b/out"
  git -c advice.detachedHead=false clone -q "$W/template" "$b/deploy" && git -C "$b/deploy" -c advice.detachedHead=false checkout -q "$SPIN"
  cp "$NCR" "$b/out/nc_r.json"
  python3 - "$HERE/rsn_connect_j1.sh" "$W/$1.sh" "$b" "$SPIN" <<'EOF'
import sys
src, dst, b, spin = sys.argv[1:5]
s = open(src).read()
for a, c in (("B=/pscratch/sd/j/josephrb/rsn-20261112", f"B={b}"),
             ("PIN=af7112989417f180e846573c31d101e44e6b02f9", f"PIN={spin}"),
             ("PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3", "PY=python3"),
             ('case "$(hostname -s)" in login[0-9][0-9])', 'case "${FAKE_HOST:-login27}" in login[0-9][0-9])')):
    assert s.count(a) == 1, a
    s = s.replace(a, c)
open(dst, "w").write(s)
EOF
}
run() {  # run <case> [env...]
  local n=$1; shift
  cp "$W/$n.sh" "$W/$n.self.sh"; rm -f "$W/sbatch.argv"
  env PATH="$W/bin:$PATH" RSN_PVL_PREP="$W/prep" "$@" bash "$W/$n.self.sh" "$W/$n.self.sh" > "$W/$n.out" 2>&1
  echo "## case $n rc=$?"
  grep -E 'REFUSED|STOP|fence.txt sha256|smoke rc|smoke: checks|^STEP|sbatch rc|J1 SUBMITTED|refusing' "$W/$n.out" \
    | sed -E -e "s|$W|<w>|g" -e "s|$SPIN|<smoke-pin>|g" | cut -c1-200
  echo "sbatch called: $([ -s "$W/sbatch.argv" ] && sed -e "s|$W|<w>|g" -e "s|$SPIN|<smoke-pin>|g" "$W/sbatch.argv" || echo no)"
  echo "self copy removed: $([ -e "$W/$n.self.sh" ] && echo no || echo yes)"
}
mk pass; run pass
mk ll5d; run ll5d "SMOKE_SQUEUE=61078463|ll5d_gate_G18|RUNNING"
mk e96; run e96 "SMOKE_SQUEUE=61200000|e96data_full|PENDING"
mk rsnq; run rsnq "SMOKE_SQUEUE=61200001|rsn_J1|PENDING"
mk host; run host FAKE_HOST=dtn01
mk slurm; run slurm SLURM_JOB_ID=1
mk fence; echo x > "$W/b-fence/out/fence.txt"; run fence
mk noncr; rm -f "$W/b-noncr/out/nc_r.json"; run noncr
mk r1bad; sed -i.bak 's/661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652/0000000000000000000000000000000000000000000000000000000000000000/' "$W/b-r1bad/out/nc_r.json"; run r1bad
mk dirty; echo x > "$W/b-dirty/deploy/nd-unfolding/rsn/stray.txt"; run dirty
mk product; mkdir -p "$W/b-product/out/products"; touch "$W/b-product/out/products/rsn_nc.npz"; run product
mk badreweight; echo '{"tampered": 1}' > "$W/prep2.json"; mkdir -p "$W/prep2/ratios/L-5D-PV"; cp "$W/prep2.json" "$W/prep2/ratios/L-5D-PV/tune_v1.json"
cp "$W/badreweight.sh" "$W/badreweight.self.sh"; rm -f "$W/sbatch.argv"
env PATH="$W/bin:$PATH" RSN_PVL_PREP="$W/prep2" bash "$W/badreweight.self.sh" "$W/badreweight.self.sh" > "$W/badreweight.out" 2>&1
echo "## case badreweight rc=$?"; grep -E 'STOP|refusing|smoke rc' "$W/badreweight.out" | sed "s|$W|<w>|g" | cut -c1-200
echo "sbatch called: $([ -s "$W/sbatch.argv" ] && echo yes || echo no)"
