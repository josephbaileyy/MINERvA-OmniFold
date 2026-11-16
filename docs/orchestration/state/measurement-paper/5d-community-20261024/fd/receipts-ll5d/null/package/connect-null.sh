#!/bin/bash
# LL5D section 11 step 7: the null at G18 and AR23 (ll5d_b.py null, one call per truth, both readings and both
# matrices inside), DRAFT for the director's review. The director's ruling (a), 2026-11-14: run as bound; the
# products_digest moves are the declared deviation of LL5D-DECLARATION.md:672-673. At 4231b14d null_step opens the
# products through the atime watch (ll5d_b.py:499 remade, _x :366-368), and only then hashes them with a plain open
# (:502 products_digest, :477; s5c_unfold.py:87-89). So each call's record should list exactly those products in
# atime.moved and exit 8 with verdict PASS. That expected set is fixed here before the run: the job recomputes it from
# the bound module and must reproduce EXP_<T>_SHA256 (227 paths per truth: central T, seed T, 175 blocks, stat 1-50),
# or it stops before any call. CLEAN per truth = rc exactly 8, verdict PASS, atime.moved set-equal to the fixed set.
# Anything else (rc 0, 13, any extra or missing path) is NOT-CLEAN and goes to the director unrepaired.
# ONE job (-N 1 --exclusive, --time 01:00:00, 1.0 node-h) on a FRESH deploy clone at M that no other job reads; its
# single start check (sha256sum -c) runs before both calls, which run one after the other, so no plain read of a
# watched file runs while a call is in flight (B1). Writes only under $W; $U is read. Nothing to CFS. Not under set -u.
M=4231b14de5ea693e92cb31b1358a816b5c2f6625         # M_A1b.1 (LL5D-BINDING-3.md addendum A1b.1): the merge that carries ll5d_ctl.py
L5=2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14        # ll5d.py's sha256 at M
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
W=$P/ll5d-null-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U: the bulk's 1662 products, read
STAGED=$P/fd-1b-inv-20261101/i0/in   # --staged (setup reads s1/s1_assembly.npz through via_noatime)
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
CMODELSHA=3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60   # nd-unfolding/pv-ladder/readouts/cmodel_5d.json at M
FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run
G18W=$P/ll5d-gate-2-g18-20261110; AR23W=$P/ll5d-gate-2-ar23-20261110
G18GATE=a5d66b7e506a98d5a0b555dbe171aa6c1e931eb93df793c3e515d7d44466fc70   # sha256 of gate-g18.json (receipts-ll5d/gate-2-g18/node-sha256.txt)
AR23GATE=35a20c471cb06f428c49daaaebfc6646babb7f7fb060039d4c63139da51d0a4c  # sha256 of gate-ar23.json (receipts-ll5d/gate-2-ar23/node-sha256.txt)
WALLSSHA=9377977cc9ea330522291363899e6a9a7f233ef71469f46fca184421bbe81e48  # sha256 of the pilot's walls.json (#1123, ll5d_pilot_61184880.out.txt)
CLIPSHA=9632540ecd0d25e2223eedb480b96078459a6e6d75128b4e4132ea1bf644d3aa   # sha256 of the pilot's clipcheck.json (#1123)
CTLSHA=82cc5858263164d7f5dc5977730484c385d960a1bb135208bd5b1f208e9cf2ec    # sha256 of the pilot's controls.json (#1123; amendment A1b.1, ll5d_ctl.py)
AUDITACK=https://github.com/josephbaileyy/MINERvA-OmniFold/pull/1123#issuecomment-6840388077   # coverage-5b-audit's GO (2026-11-13T00:48:18Z)
CAP=148.0; THIS=1.0; TL=01:00:00; NODES="01"   # two null calls, one after the other, on one node
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
for v in "$G18GATE" "$AR23GATE" "$WALLSSHA" "$CLIPSHA" "$CTLSHA" "$L5" "$CMODELSHA"; do [[ $v =~ ^[0-9a-f]{64}$ ]] || { echo "STOP a placeholder is not filled"; exit 2; }; done
[[ $M =~ ^[0-9a-f]{40}$ ]] || { echo "STOP M is not filled"; exit 2; }
[[ $AUDITACK =~ ^https://github\.com/josephbaileyy/MINERvA-OmniFold/pull/[0-9]+#issuecomment-[0-9]+$ ]] || { echo "STOP the audit's acknowledgement is not filled"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-null.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ audit_ack=$AUDITACK"
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -c '^ll5d_')" = "0" ] || stop "an ll5d_ job is queued or running"
[ "$(squeue --me -h -o %j | grep -c '^cov2dg2r-')" = "0" ] || stop "a cov2dg2r- job is queued or running"
[ -e "$FIGMARK" ] && stop "a group C figure connect is running (or left its marker): $(head -c 300 "$FIGMARK")"
echo "group C marker absent: $FIGMARK"
[ "$(squeue --me -h -o %j | grep -cE '^(rsn_|e96data|rdx_)')" = "0" ] || stop "an rsn_, e96data or rdx_ job is queued or running"
# ^cov2d but not ^cov2dg2r-: COV2D-G2R reads no LL5D input outside O_NOATIME (overlap-fence.diff.txt); COV2D proper still refuses
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $2 !~ /^cov2dg2r-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d job is unended: $cv"
echo "== iris"; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}'); [ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP is above half the balance $bal: to Joseph"
charged=$(sacct -X -n -P -S 2026-11-08 -u josephrb -o JobName,State,ElapsedRaw,NNodes | awk -F'|' '$1 ~ /^ll5d_/ && $2 !~ /^(PENDING|RUNNING|REQUEUED|SUSPENDED)/ {s += $3 * $4} END {printf "%.3f", s / 3600}')
held=$(squeue --me -h -o '%j|%l|%D' | awk -F'|' '$1 ~ /^ll5d_/ {split($2, t, /[-:]/); n = length(t); s = (n == 4 ? t[1]*86400 + t[2]*3600 + t[3]*60 + t[4] : n == 3 ? t[1]*3600 + t[2]*60 + t[3] : t[1]*60 + t[2]); h += s * $3} END {printf "%.3f", h / 3600}')
proj=$(awk -v a=$charged -v b=$held -v c=$THIS 'BEGIN{printf "%.3f", a + b + c}')
echo "projection charged=$charged held=$held this=$THIS total=$proj cap=$CAP"
awk -v p=$proj -v c=$CAP 'BEGIN{exit !(p <= c)}' || stop "the projection $proj passes the cap $CAP"
# Section 11 step 6's preconditions, each by the receipted digest; only the named verdict fields are read.
for T in g18 ar23; do
  if [ $T = g18 ]; then GW=$G18W; GS=$G18GATE; else GW=$AR23W; GS=$AR23GATE; fi
  [ "$(sha256sum "$GW/gate-$T.json" | cut -d' ' -f1)" = "$GS" ] || stop "gate-$T.json's digest is not the receipt's"
  python3 -c 'import json,sys; g=json.load(open(sys.argv[1])); ok=g.get("truth")==sys.argv[2] and g.get("verdict")=="PASS"; print("gate", sys.argv[2], "truth=%s verdict=%s" % (g.get("truth"), g.get("verdict"))); sys.exit(0 if ok else 1)' "$GW/gate-$T.json" "$T" || stop "gate $T is not PASS"
done
for f in "walls.json|$WALLSSHA|PASS" "controls.json|$CTLSHA|PASS" "clipcheck.json|$CLIPSHA|PROCEED"; do
  IFS='|' read -r name want verdict <<< "$f"
  [ "$(sha256sum "$PW/$name" | cut -d' ' -f1)" = "$want" ] || stop "the pilot's $name digest is not the receipt's"
  python3 -c 'import json,sys; v=json.load(open(sys.argv[1])).get("verdict"); print(sys.argv[1], "verdict=%s" % v); sys.exit(0 if v==sys.argv[2] else 1)' "$PW/$name" "$verdict" || stop "the pilot's $name is not $verdict"
done
k=$(ls "$U" | grep -c '\.npz$'); echo "products in \$U: $k"
[ "$k" = "1662" ] || stop "\$U does not hold the bulk's 1662 products"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cat > "$W/bound.sha256" <<SUMS
$L5  nd-unfolding/ll5d.py
522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f  nd-unfolding/fd_1b_c2.py
936e1957d330e24d3eaab5f6c53d30b5be42a96f76daac07d527be97c0af30e2  nd-unfolding/fd_1b_mc.py
869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08  nd-unfolding/fd_1b_toys.py
71b3903aa1329807af7e48b29b4ffd3336ad637d4b8c7e43ae0a6cbe28bcdf1f  nd-unfolding/fd_1b_inv.py
b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7  nd-unfolding/s1_assemble.py
805a00063a6136e25c6f8f57d228ec996c85a9bc997981632643baeee6c13d80  nd-unfolding/s5p_universe.py
c6c9a45fa93c6590c4fdf0d9b7d29f01cccf97b281e469fa29a3d2f34b4618fd  nd-unfolding/fd_1b_score.py
b95c562916091b910a5ca8d874d83296035690cb8784db3d318b2f07fed28182  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe2.py
76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed  2d-unfolding/cov2d/cov2d.py
3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031  docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt
b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89  nd-unfolding/pv-ladder/readouts/h2_definition.json
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7  nd-unfolding/s5e_candidate.py
6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f  nd-unfolding/s5e_deform.py
24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb  nd-unfolding/ll5d_b.py
ec1402db5cbb5ca3002d7e45a714319d90a8b93654005d688b304a69caab4d38  nd-unfolding/fd_1b_null.py
8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c  nd-unfolding/s5n_pseudo.py
7ad8ca0f73989128b783b59d55670687c293d186b2643ea799a3e67c047bf185  nd-unfolding/s5p_numerics.py
24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582  nd-unfolding/omnifold_nn_core.py
fc95f53459a5caafea4aa05a24a406535968e25b0bcca52567a38caf4caf3de5  2d-unfolding/uq/coverage_fixed_truth/score_coverage.py
a9f09557ec1b6022b1205f14e8d2241257336d9028b166061a3b33118243a936  nd-unfolding/ll5d_ctl.py
SUMS
[ "$(sha256sum "$W/bound.sha256" | cut -d' ' -f1)" = "7540b2de8f2de64f25d62497abe91a6a04fc7cf6cb18379e624422afb32c52b3" ] || stop "bound.sha256 is not the bulk's 22-line list 7540b2de"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
[ "$(sha256sum "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" | cut -d' ' -f1)" = "$CMODELSHA" ] || stop "cmodel_5d.json is not M's"
echo "cmodel_5d.json $CMODELSHA OK"
ls "$U" > "$W/u-names.txt" || stop "ls \$U"
echo "u-names $(awk 'END {print NR}' "$W/u-names.txt") lines sha256 $(sha256sum "$W/u-names.txt" | cut -d' ' -f1)"
cat > "$W/sbatch-ll5d-null.sh" <<'JOB'
#!/bin/bash
# ll5d_null_01's job: the deploy at M with porcelain 0 and the bound blobs, checked ONCE here, before both calls; the
# expected moved set recomputed from the bound module and pinned; then ll5d_b.py null for g18, then for ar23, one after
# the other; after each, its record checked against the fixed set. Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; U=$4; NODE=$5
P=/pscratch/sd/j/josephrb; STAGED=$P/fd-1b-inv-20261101/i0/in
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
EXP_g18_SHA256=ec363fd10db805005306e12955bc8651a02a340d5e53b8e81097bc53cb0e1e01; EXP_g18_N=227
EXP_ar23_SHA256=923681b295f1226360ca9ba9ee73c783ad7d9e2d559abd0106bc20d6320f3a93; EXP_ar23_N=227
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID node=$NODE start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job-$NODE.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# the expected moved set (the director's ruling (a)): remade's opened products (bands_of, sa.EXPECT, STAT_REPLICAS,
# product_name over READINGS) intersected with products_digest's set (TAG, BLOCK_ROLES) applied to $U's names
for T in g18 ar23; do
  python3 -B - "$DD/nd-unfolding" "$W/u-names.txt" "$U" "$T" "$W/expected_moved_$T.txt" <<'EXPECT' || stop "expected set $T"
import hashlib, sys
sys.path.insert(0, sys.argv[1])
import ll5d, ll5d_b as b
names = [l.strip() for l in open(sys.argv[2]) if l.strip()]
U, T = sys.argv[3].rstrip("/"), sys.argv[4]
opened = set()
for rd in ll5d.READINGS:
    opened |= {b.product_name(T, "central", "T"), b.product_name(T, "seed", "T")}
    opened |= {b.product_name(T, "block", f"{band}_{i}") for band in b.bands_of(rd) for i in range(b.sa.EXPECT[band])}
    opened |= {b.product_name(T, "stat", str(x)) for x in b.STAT_REPLICAS}
dig = {n for n in names if n.startswith(f"{b.TAG}_{T}_") and n.endswith(".npz") and ".partial-" not in n
        and n.split("_")[2] in b.BLOCK_ROLES}
body = "".join(f"{U}/{n}\n" for n in sorted(opened & dig))
open(sys.argv[5], "w").write(body)
print(f"expected {T}: opened {len(opened)} digested {len(dig)} absent {len(opened - set(names))} moved {len(opened & dig)} "
      f"sha256 {hashlib.sha256(body.encode()).hexdigest()}")
sys.exit(1 if opened - set(names) else 0)
EXPECT
  eval "want=\$EXP_${T}_SHA256; wn=\$EXP_${T}_N"
  [ "$(sha256sum "$W/expected_moved_$T.txt" | cut -d' ' -f1)" = "$want" ] && [ "$(awk 'END {print NR}' "$W/expected_moved_$T.txt")" = "$wn" ] \
    || stop "the expected moved set at $T is not the fixed one ($want, $wn paths)"
  echo "expected moved $T: $wn paths, sha256 $want (fixed)"
done
urc=0
for T in g18 ar23; do
  /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" null --staged "$STAGED" \
    --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U" \
    --cmodel-json "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" --flux-constraint "$CONSTRAINT" \
    --truth "$T" --out "$W/null-$T.json" < /dev/null > "$W/null-$T.out" 2> "$W/null-$T.time"; s=$?
  echo "null $T rc=$s: $(tail -1 "$W/null-$T.out")"
  python3 -B - "$W/null-$T.json" "$W/null-$T.invalid.json" "$W/expected_moved_$T.txt" "$s" "$T" <<'CHECK'
import json, os, sys
rec_p, inv_p, exp_p, rc, T = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
exp = sorted(l for l in open(exp_p).read().splitlines() if l)
p = rec_p if os.path.exists(rec_p) else inv_p if os.path.exists(inv_p) else None
if p is None:
    print(f"NULL-EXIT {T} NOT-CLEAN rc={rc}: no record; to the director unrepaired"); sys.exit(1)
rec = json.load(open(p))
moved = sorted(rec.get("atime", {}).get("moved", []))
extra, missing = sorted(set(moved) - set(exp)), sorted(set(exp) - set(moved))
print(f"null {T}: record {os.path.basename(p)} verdict {rec.get('verdict')} moved {len(moved)} expected {len(exp)} "
      f"extra {len(extra)} {extra[:5]} missing {len(missing)} {missing[:5]}")
ok = rc == 8 and p == rec_p and rec.get("verdict") == "PASS" and not extra and not missing
print(f"NULL-EXIT {T} " + ("CLEAN: rc 8, verdict PASS, moved == the fixed set (the declared deviation)" if ok else
      f"NOT-CLEAN rc={rc}: to the director unrepaired; nothing is read from this null"))
sys.exit(0 if ok else 1)
CHECK
  c=$?; urc=$((urc | c))
done
sha256sum "$W"/null-*.json "$W"/null-*.out "$W"/expected_moved_*.txt 2>/dev/null
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/null-*.time
echo "null checks rc=$urc"
echo "end=$(date -u +%FT%TZ)"
exit $urc
JOB
echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-null.sh" | cut -d' ' -f1)"
find "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$ND/bank_sweep_5d_bkgaware" "$P/s5p-20260926/bank_detector" \
  "$P/fd-1b-20261030/pins.json" "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" "$P/fd-f1-20261027/f1b3/prep" "$P/fd-1b-inv-20261101/i0/in" \
  -type f -printf "%A@\t%p\n" | sort -k2 > "$W/atime-pre.tsv" || stop "atime snapshot"
echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"
python3 - "$W/atime-pre.tsv" "$STAGED" "$CONSTRAINT" "$DD" "$U" "$W/u-names.txt" <<'COVER' || stop "a declared protected input is not in atime-pre"
# The null's declared inputs (ll5d_b.setup, remade, made_from at 4231b14d): the staged S1 assembly and the flux
# constraint (protected: each must be in atime-pre), the deploy's definition and cmodel json, and the $U products
# of the two truths' central/seed/block/stat roles (LL5D's own outputs). Classified by path against atime-pre.
import os, sys
pre = {l.split("\t", 1)[1] for l in open(sys.argv[1]).read().splitlines()}
staged, constraint, dd, U = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].rstrip("/")
prot = [f"{staged}/s1/s1_assembly.npz", constraint]
deploy = [f"{dd}/nd-unfolding/pv-ladder/readouts/h2_definition.json", f"{dd}/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"]
prods = [f"{U}/{n}" for n in open(sys.argv[6]).read().split() if n.split("_")[1:2] in (["g18"], ["ar23"])
         and n.split("_")[2:3] and n.split("_")[2] in ("central", "seed", "block", "stat") and n.endswith(".npz")]
missing = [p for p in prot + deploy if not os.path.exists(p)]
print(f"declared inputs: protected {len(prot)} (in atime-pre: {sum(p in pre for p in prot)}), deploy {len(deploy)} "
      f"(in atime-pre: {sum(p in pre for p in deploy)}), products {len(prods)} (in atime-pre: {sum(p in pre for p in prods)}), missing {missing}")
sys.exit(0 if all(p in pre for p in prot) and not missing and not any(p in pre for p in deploy + prods) else 1)
COVER
ids=()
for NN in $NODES; do
  jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive --no-requeue -t "$TL" -J "ll5d_null_$NN" \
    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-null.sh" "$DD" "$M" "$W" "$U" "$NN")
  jid=${jid%%;*}
  [ -n "$jid" ] || { [ ${#ids[@]} -gt 0 ] && scancel "${ids[@]}"; stop "sbatch for ll5d_null_$NN returned no id: cancelled ${ids[*]}"; }
  ids+=("$jid"); echo "Submitted batch job $jid (ll5d_null_$NN)"
  tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
  [ "$tl" = "TimeLimit=01:00:00" ] || { scancel "${ids[@]}"; stop "ll5d_null_$NN's time limit parsed as ${tl#TimeLimit=}, not 01:00:00: cancelled ${ids[*]}"; }
done
squeue --me -h -o '%i %j %T %l %D' | grep ll5d_null_
echo "end=$(date -u +%FT%TZ)"
