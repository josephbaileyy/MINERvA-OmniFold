#!/bin/bash
# Local smoke of RDX's launcher tranche (macOS or Linux; never connects, never submits). Usage:
#   bash smoke_rdx_stages.sh <new empty work dir>
# A tiny git deploy holds what the three job scripts read from it (manifests, the AnaTuple table, rdx_tasks.tsv, the
# inputs sums, pv-ladder's prep sums, a stand-in fd_ct_period_inputs.py whose MP1_ZERO pins the smoke's own lat_zero
# files); fake AnaTuples, dumps and gates sit under the work dir. Each job script runs in its own RDX_SMOKE mode. The
# connect runs as a copy with only its constants pointed at the work dir, a stub python path set to python3, and stubs
# for hostname, squeue, sacct and sbatch.
W=${1:?work dir}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$W" ] && [ -z "$(ls -A "$W")" ] || { echo "STOP: $W is not a new empty directory"; exit 9; }
mkdir -p "$W/bin" "$W/canon/2d-unfolding/playlist_manifests" "$W/ana/MC/StandardMC/Playlist1A" "$W/ana/Data/Playlist1A"
D="$W/deploy"; mkdir -p "$D/2d-unfolding/playlist_manifests" "$D/publication/release/preservation/anatuple-checksums" \
  "$D/nd-unfolding/rdx" "$D/nd-unfolding/pv-ladder"
printf '#!/bin/bash\necho "${FAKE_HOST:-login27}"\n' > "$W/bin/hostname"
cat > "$W/bin/squeue" <<'EOF'
#!/bin/bash
if [ "$1" = -j ]; then echo "999|stub|PENDING|19:00|regular"; exit 0; fi
[ -n "$SMOKE_SQUEUE" ] && printf '%s\n' "$SMOKE_SQUEUE"; exit 0
EOF
printf '#!/bin/bash\n[ -n "$SMOKE_SACCT" ] && printf "%%s\\n" "$SMOKE_SACCT"; exit 0\n' > "$W/bin/sacct"
printf '#!/bin/bash\necho "$*" >> "%s/sbatch.argv"; echo 70000001\n' "$W" > "$W/bin/sbatch"
chmod +x "$W/bin/"*
export PATH="$W/bin:$PATH"
# fake AnaTuples and the manifest rows for them
: > "$D/publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv"
for kind in MC Data; do
  if [ $kind = MC ]; then sub=MC/StandardMC/Playlist1A; else sub=Data/Playlist1A; fi
  : > "$D/2d-unfolding/playlist_manifests/1A_${kind}.txt"
  for i in 1 2; do
    f="$W/ana/$sub/f$i.root"; echo "$kind $i" > "$f"
    echo "$f" >> "$D/2d-unfolding/playlist_manifests/1A_${kind}.txt"
    m=$(python3 -c "import os,sys,time; print(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(os.stat(sys.argv[1]).st_mtime))))" "$f")
    printf '%s\t%s\t%s\t%s\n' "$(printf 'a%.0s' {1..64})" "$(wc -c < "$f" | tr -d ' ')" "$m" "$sub/f$i.root" \
      >> "$D/publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv"
  done
  cp "$D/2d-unfolding/playlist_manifests/1A_${kind}.txt" "$W/canon/2d-unfolding/playlist_manifests/"
done
# dumps, MP-1 lateral stand-ins, ratio, and their pins
mkdir -p "$W/B/out/dumps" "$W/B/out/checks" "$W/B/out/gates" "$W/B/out/stage" "$W/mp1lat" "$W/prep/ratios/L-5D-PV"
for f in lat_RDX_ALL.npz lat_RDX_ALL_bkg.npz truthx_RDX_ALL.npz; do echo "$f" > "$W/B/out/dumps/$f"; done
(cd "$W/B/out/dumps" && sha256sum lat_RDX_ALL.npz lat_RDX_ALL_bkg.npz truthx_RDX_ALL.npz | sed 's/  /  .\//') > "$D/nd-unfolding/rdx/rdx-inputs-SHA256SUMS"
echo lz > "$W/mp1lat/lat_zero.npz"; echo lb > "$W/mp1lat/lat_zero_bkg.npz"; echo tune > "$W/prep/ratios/L-5D-PV/tune_v1.json"
echo "$(sha256sum "$W/prep/ratios/L-5D-PV/tune_v1.json" | cut -d' ' -f1)  ./ratios/L-5D-PV/tune_v1.json" > "$D/nd-unfolding/pv-ladder/prep-SHA256SUMS"
printf 'MP1_ZERO = {"lat_npz": "%s", "lat_bkg": "%s"}\n' "$(sha256sum "$W/mp1lat/lat_zero.npz" | cut -d' ' -f1)" \
  "$(sha256sum "$W/mp1lat/lat_zero_bkg.npz" | cut -d' ' -f1)" > "$D/nd-unfolding/fd_ct_period_inputs.py"
cp "$HERE/rdx_tasks.tsv" "$D/nd-unfolding/rdx/"
git -C "$D" init -q && git -C "$D" add -A && git -C "$D" -c user.name=s -c user.email=s@invalid commit -q -m smoke
PIN=$(git -C "$D" rev-parse HEAD)
for c in k1 truthx_npz; do echo '{"verdict": "PASS"}' > "$W/B/out/checks/$c.json"; done
printf 'pin=%s\n' "$PIN" > "$W/B/out/gates/S3a.ok"; printf 'pin=%s\n' "$PIN" > "$W/B/out/gates/S3b.ok"
printf 'pin=%s\nlimit=0:40:00\n' "$PIN" > "$W/B/out/gates/merge.ok"
echo "x" > "$W/B/out/loops.sha256"; cp "$W/mp1lat/"*.npz "$W/B/out/stage/"
echo bin > "$W/rdx.bin"; MD5=$(md5sum "$W/rdx.bin" | cut -d' ' -f1)

ev() { env RDX_SMOKE=1 RDX_CANON="$W/canon" RDX_ANATUPLE_ROOT="$W/ana/" "$@" bash "$HERE/sbatch_rdx_evloop.sh" "$W/B" "$D" 1A "$W/rdx.bin" "${EV_MD5:-$MD5}" 2>&1 | sed "s|$W|<w>|g" | tail -2; }
echo "## evloop pass";            ev
echo "## evloop wrong name";      ev RDX_NAME=rdx_s2_1A
echo "## evloop limit too long";  ev RDX_TIMELIMIT=3:00:00
echo "## evloop fenced job";      ev "SMOKE_SQUEUE=ll5d_gate_G18|RUNNING"
echo "## evloop rsn job";         ev "SMOKE_SQUEUE=rsn_J2|PENDING"
echo "## evloop md5";             EV_MD5=0123456789abcdef0123456789abcdef ev
cp "$W/canon/2d-unfolding/playlist_manifests/1A_MC.txt" "$W/mc.keep"; echo "/extra" >> "$W/canon/2d-unfolding/playlist_manifests/1A_MC.txt"
echo "## evloop manifest not committed"; ev; cp "$W/mc.keep" "$W/canon/2d-unfolding/playlist_manifests/1A_MC.txt"
touch -r "$W/ana/Data/Playlist1A/f2.root" "$W/f2.mtime"; touch -m -t 202001010000 "$W/ana/Data/Playlist1A/f2.root"
echo "## evloop AnaTuple mtime differs"; ev
touch -m -r "$W/f2.mtime" "$W/ana/Data/Playlist1A/f2.root"
mkdir -p "$W/B/out/evloop"; touch "$W/B/out/evloop/runEventLoopOmniFold_RDX_1A.root"
echo "## evloop output exists"; ev
rm -f "$W/B/out/evloop/runEventLoopOmniFold_RDX_1A.root"

mg() { mv "$W/B/out/dumps" "$W/dumps.keep"; mv "$W/B/out/checks" "$W/checks.keep"; env RDX_SMOKE=1 "$@" bash "$HERE/sbatch_rdx_merge.sh" "$D" "$PIN" "$W/B" "${MG_LIMIT:-0:40:00}" 2>&1 | sed "s|$W|<w>|g" | tail -6; mv "$W/dumps.keep" "$W/B/out/dumps"; mv "$W/checks.keep" "$W/B/out/checks"; }
echo "## merge pass";                mg
echo "## merge gate limit mismatch"; MG_LIMIT=0:50:00 mg
mv "$W/B/out/loops.sha256" "$W/loops.keep"; echo "## merge no loops.sha256"; mg; mv "$W/loops.keep" "$W/B/out/loops.sha256"
mkdir -p "$W/B/out/merged"; touch "$W/B/out/merged/runEventLoopOmniFold_RDX_ALL.root"; echo "## merge output exists"; mg
rm -f "$W/B/out/merged/runEventLoopOmniFold_RDX_ALL.root"

ar() { env RDX_SMOKE=1 RDX_PVL_PREP="$W/prep" RDX_MP1_LATERAL="$W/mp1lat" bash "$HERE/sbatch_rdx_arms.sh" "$D" "$PIN" "$W/B" "$1" 2>&1; }
echo "## arms S3a pass"; ar S3a | sed -e "s|$W|<w>|g" | grep -v '^STEP' | tail -1; ar S3a | grep '^STEP' | sed -e "s|$W|<w>|g" | awk '{print $1, $2, ($0 ~ /--truthx-permute 20261113/ ? "permute" : ""), ($0 ~ /--transfer/ ? "transfer" : ""), ($0 ~ /--closure/ ? "closure" : ""), ($0 ~ /lat_zero.npz/ ? "lat_zero" : ""), ($0 ~ /--regressor-features wide/ ? "wide" : ""), ($0 ~ /w_push_w_truth/ ? "weighted" : "")}'
echo "## arms S3b pass"; ar S3b | sed -e "s|$W|<w>|g" | grep -v '^STEP' | tail -1; ar S3b | grep '^STEP' | sed -e "s|$W|<w>|g" | awk '{print $1, $2, ($0 ~ /--truthx-permute 20261113/ ? "permute" : ""), ($0 ~ /--transfer/ ? "transfer" : ""), ($0 ~ /--truth a7_gibuu/ ? "a7" : ""), ($0 ~ /--truth q3/ ? "q3" : ""), ($0 ~ /--closure/ ? "closure" : ""), ($0 ~ /--regressor-features wide/ ? "wide" : ""), ($0 ~ /w_push_w_truth/ ? "weighted" : "")}'
echo tampered >> "$W/B/out/dumps/truthx_RDX_ALL.npz"; echo "## arms sidecar tampered"; ar S3a | tail -1
git -C "$D" checkout -q -- . ; echo truthx_RDX_ALL.npz > "$W/B/out/dumps/truthx_RDX_ALL.npz"
echo '{"verdict": "FAIL"}' > "$W/B/out/checks/k1.json"; echo "## arms k1 FAIL"; ar S3a | tail -1
echo '{"verdict": "PASS"}' > "$W/B/out/checks/k1.json"; mv "$W/B/out/gates/S3b.ok" "$W/s3b.keep"
echo "## arms gate missing"; ar S3b | tail -1; mv "$W/s3b.keep" "$W/B/out/gates/S3b.ok"
echo "## arms wrong pin"; env RDX_SMOKE=1 RDX_PVL_PREP="$W/prep" RDX_MP1_LATERAL="$W/mp1lat" bash "$HERE/sbatch_rdx_arms.sh" "$D" 0000000000000000000000000000000000000000 "$W/B" S3a 2>&1 | tail -1

# the connect, as a copy with its constants pointed at the work dir (its deploy is the same tiny repo)
ln -s "$D" "$W/B/deploy"; rm -f "$W/B/out/gates/merge.ok"
mkdir -p "$W/mp1/s0/evloop" "$W/mp1/s1/evloop/zero" "$W/mp1/s1/lateral" "$W/B/build"
echo cv > "$W/mp1/s0/evloop/base_cv.root"
for pl in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do echo z > "$W/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_${pl}_zero.root"; done
cp "$W/mp1lat/"*.npz "$W/mp1/s1/lateral/"
echo "$MD5  $W/B/build/bld_rdx/runEventLoopOmniFold" > "$W/B/build/MANIFEST.md5"; mkdir -p "$W/B/build/bld_rdx"; cp "$W/rdx.bin" "$W/B/build/bld_rdx/runEventLoopOmniFold"
POL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/prologue3-20261107/policy-config.json
mkdir -p "$D/$(dirname "$POL")"; echo '{"cov2d_protected_paths": ["/pscratch/sd/j/josephrb/cov2d-run-20261104"]}' > "$D/$POL"
mkdir -p "$D/nd-unfolding/rdx"; for f in rdx_paths.py rdx_cap.py sbatch_rdx_evloop.sh sbatch_rdx_merge.sh sbatch_rdx_arms.sh; do cp "$HERE/$f" "$D/nd-unfolding/rdx/"; done
git -C "$D" add -A && git -C "$D" -c user.name=s -c user.email=s@invalid commit -q -m "smoke 2"; PIN2=$(git -C "$D" rev-parse HEAD)
python3 - "$HERE/rdx_connect.sh" "$W/connect.sh" "$W" <<'EOF'
import sys
src, dst, w = sys.argv[1:4]
s = open(src).read()
for a, b in (("B=/pscratch/sd/j/josephrb/rdx-20261112", f"B={w}/B"), ("CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold", f"CANON={w}/canon"),
             ("MP1=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1", f"MP1={w}/mp1"),
             ("PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3", "PY=python3"), ("SYSPY=/usr/bin/python3", "SYSPY=python3"),
             ('case "$(hostname -s)" in login[0-9][0-9])', 'case "${FAKE_HOST:-login27}" in login[0-9][0-9])')):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(dst, "w").write(s)
EOF
cn() { cp "$W/connect.sh" "$W/c.self.sh"; rm -f "$W/sbatch.argv"; env RDX_SMOKE= RDX_CANON="$W/canon" RDX_ANATUPLE_ROOT="$W/ana/" "$@" bash "$W/c.self.sh" "$W/c.self.sh" $CN_ARGS 2>&1 | sed -e "s|$W|<w>|g" -e "s|$PIN2|<pin>|g" | grep -E 'REFUSED|STOP|SUBMIT|rc=|^pin=|^limit=|smoke:' | tail -4; echo "  sbatch called: $([ -s "$W/sbatch.argv" ] && sed -e "s|$W|<w>|g" -e "s|$PIN2|<pin>|g" "$W/sbatch.argv" || echo no)"; }
echo "## connect gs2 writes the gate";        CN_ARGS="gs2 $PIN2" cn
echo "## connect gs2 refuses to overwrite";   CN_ARGS="gs2 $PIN2" cn
echo "## connect gmerge without a limit";     CN_ARGS="gmerge $PIN2" cn
echo "## connect s1 without the LL5D time";   CN_ARGS="s1 $PIN2" cn
echo "## connect s1 with a future LL5D time"; CN_ARGS="s1 $PIN2 2099-01-01T00:00:00Z" cn
echo "## connect s1 fenced";                  CN_ARGS="s1 $PIN2 2026-11-12T00:00:00Z" cn "SMOKE_SQUEUE=e96data_full|PENDING"
echo "## connect s1 over the cap";            CN_ARGS="s1 $PIN2 2026-11-12T00:00:00Z" cn "SMOKE_SACCT=1|rdx_s3_a|COMPLETED|9000|1|22"
echo "## connect s1 submits";                 CN_ARGS="s1 $PIN2 2026-11-12T00:00:00Z" cn
echo "## connect dtn host";                   CN_ARGS="s1 $PIN2 2026-11-12T00:00:00Z" cn FAKE_HOST=dtn01
echo "## connect bad pin";                    CN_ARGS="s1 notapin" cn
