#!/bin/bash
# REF-C2C1 step two, stage 2 (the units), part 2: the replicas connect (REF-C2C1-BINDING-2.md ruling 2.2; the
# director's ruling of 2026-11-06: centrals and projection accepted; the fence recorded, not refused, for guarded
# readers), on a login node, detached:
#   - the gate: part 1's record on pscratch is the accepted one (CENTRALS-DONE: job 60889566, rcs 0 0 0, 3 PASS
#     markers, porcelain 0), and the two staged copies are present;
#   - the fence, recorded: the full `squeue -u josephrb` at launch (no refusal);
#   - a fresh clean clone at M into $O/deploy-replicas, porcelain --ignored 0, the binding's 8 blobs;
#   - libRooUnfold.so copied by an O_NOATIME read into $O/libcheck-replicas/ and checked against config.json's full
#     sha256 (F2's interim);
#   - the 303 COV2D inputs (the flux constraint, E_R's ER/xsec.root and 300 S1_*/xsec.root, the publication's
#     covariance) listed for the jobs' before/after stat;
#   - lanes.tsv (350 units, 4 jobs x 4 lanes) and the job script written from this file, each refused unless its
#     sha256 is the reviewed one;
#   - the price: 4 jobs x --time=02:30:00 on 1 node = at most 10.0 node-h; with 0.3839 spent (C-DRAW 0.1789, the
#     centrals 0.2050), under the 12.5 cap; the iris half-balance check;
#   - four sbatch, each one's TimeLimit must read 02:30:00, else every submitted job is cancelled, rc 6.
# Writes only under $O. No set -u. Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
D=$O/deploy-replicas
L=$O/logs-replicas
M=77d76cfc2d621f8faa010b75006811868494652a
LIB=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so
LIB_SHA=0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
TLIMIT=02:30:00
PRICE=10.0
SPENT=0.3839
CAP=12.5
LANES_SHA=7b737d0c4bb5e547adae0376f9c50da00cc1ec9a08d7dc2c892804e0b968524c
JOB_SHA=4f38fc64436448746c3b026ca34b201d4ee9e244ac93e0d981a3420225ac4b2d
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -d "$O/stage" ] && [ -d "$O/units" ] && [ -s "$O/CENTRALS-DONE" ] && [ -x "$PY" ] || bail
for x in deploy-replicas libcheck-replicas logs-replicas REPLICAS-DONE-j0 REPLICAS-DONE-j1 REPLICAS-DONE-j2 REPLICAS-DONE-j3; do [ ! -e "$O/$x" ] || bail; done
[ -z "$(squeue --me -h -n fd_c2c1r -o %i)" ] || bail
mkdir -p "$L" "$O/libcheck-replicas" || bail
exec > "$L/connect.log" 2>&1
finish() { echo "ref-c2c1 replicas connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/refc2c1_replicas_submit.sh"
echo "fence, recorded (the director's ruling of 2026-11-06): squeue -u josephrb at $(date -u +%FT%TZ):"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed 's/^/  /'
cd_rec=$(cat "$O/CENTRALS-DONE"); echo "gate: CENTRALS-DONE $cd_rec"
[ "$cd_rec" = '{"job": "60889566", "rcs": "0 0 0", "pass_markers": 3, "porcelain_after": 0}' ] || { echo "STOP: part 1's record is not the accepted one"; finish 4; }
for f in runEventLoopOmniFold_MEFHC.root runEventLoopMC_MEFHC.root; do [ -s "$O/stage/$f" ] || { echo "STOP: staged $f missing"; finish 4; }; done
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$L/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
128b4e00505f82153d1d400a482b7b1a5a3d56be 2d-unfolding/ref_c2c1/ref_c2c1.py
e51367aa3d9d68b8c89f76cd7f556c70bd4a226f 2d-unfolding/ref_c2c1/ref_c2c1_read.py
96dbbaa223a3dec4ceba80686f07721e87ec9045 2d-unfolding/ref_c2c1/config.json
0d2f1a2445fe22130be94635cabb280837be4edb 2d-unfolding/ref_c2c1/test_ref_c2c1.py
0e80efd2d927390e4360cf10134e5b74e7554deb 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
f2711d4ea81141205f6ef8a450707051713faf20 2d-unfolding/ref_c2c1/run_suite.py
f4dbaf1fe57bcf4ab0f128d70c1725aa64ae8d29 2d-unfolding/ref_c2c1/run_tests.sh
990ec7894a982709298ce3550ffa3fa1e73fe1b9 2d-unfolding/ref_c2c1/test_run_suite.py
BLOBS
echo "bound blobs: 8 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
dd if="$LIB" iflag=noatime status=none of="$O/libcheck-replicas/libRooUnfold.so" || { echo "STOP: copying the library"; finish 4; }
lsrc=$(dd if="$LIB" iflag=noatime status=none | sha256sum | cut -d' ' -f1); lcopy=$(sha256sum "$O/libcheck-replicas/libRooUnfold.so" | cut -d' ' -f1)
echo "libRooUnfold.so: source sha256 (O_NOATIME read) $lsrc; copy $lcopy; config.json $LIB_SHA"
[ "$lsrc" = "$LIB_SHA" ] && [ "$lcopy" = "$LIB_SHA" ] || { echo "STOP: libRooUnfold.so is not the bound library"; finish 4; }
{ echo /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
  echo /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root
  ls -d /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_*/xsec.root
  echo /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root; } > "$L/cov2d-watch-paths.txt"
echo "COV2D inputs listed for the jobs' stat: $(wc -l < "$L/cov2d-watch-paths.txt")"
[ "$(wc -l < "$L/cov2d-watch-paths.txt")" -eq 303 ] || { echo "STOP: the watch list is not 303 paths"; finish 4; }
echo "== price: 4 x $TLIMIT on 1 node = at most $PRICE node-h; spent $SPENT; cap $CAP"
awk -v p=$PRICE -v s=$SPENT -v c=$CAP 'BEGIN{exit !(p + s <= c)}' || { echo "STOP: the projection is over the cap"; finish 9; }
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
cat > "$L/lanes.tsv" <<'LANESEOF'
# job	lane	unit (REF-C2C1 step two, the replicas: 300 c2_replica over Q_R's S1_001..300 and 50 c1_replica, longest-first over 4 jobs x 4 lanes, by the centrals' srun step times: c1 722 s, c2 217 s)
0	0	c1_replica:1
0	0	c1_replica:17
0	0	c1_replica:33
0	0	c1_replica:49
0	0	c2_replica:57
0	0	c2_replica:73
0	0	c2_replica:89
0	0	c2_replica:105
0	0	c2_replica:121
0	0	c2_replica:137
0	0	c2_replica:153
0	0	c2_replica:169
0	0	c2_replica:185
0	0	c2_replica:201
0	0	c2_replica:217
0	0	c2_replica:233
0	0	c2_replica:249
0	0	c2_replica:265
0	0	c2_replica:281
0	0	c2_replica:297
0	1	c1_replica:2
0	1	c1_replica:18
0	1	c1_replica:34
0	1	c1_replica:50
0	1	c2_replica:58
0	1	c2_replica:74
0	1	c2_replica:90
0	1	c2_replica:106
0	1	c2_replica:122
0	1	c2_replica:138
0	1	c2_replica:154
0	1	c2_replica:170
0	1	c2_replica:186
0	1	c2_replica:202
0	1	c2_replica:218
0	1	c2_replica:234
0	1	c2_replica:250
0	1	c2_replica:266
0	1	c2_replica:282
0	1	c2_replica:298
0	2	c1_replica:3
0	2	c1_replica:19
0	2	c1_replica:35
0	2	c2_replica:1
0	2	c2_replica:15
0	2	c2_replica:29
0	2	c2_replica:43
0	2	c2_replica:59
0	2	c2_replica:75
0	2	c2_replica:91
0	2	c2_replica:107
0	2	c2_replica:123
0	2	c2_replica:139
0	2	c2_replica:155
0	2	c2_replica:171
0	2	c2_replica:187
0	2	c2_replica:203
0	2	c2_replica:219
0	2	c2_replica:235
0	2	c2_replica:251
0	2	c2_replica:267
0	2	c2_replica:283
0	2	c2_replica:299
0	3	c1_replica:4
0	3	c1_replica:20
0	3	c1_replica:36
0	3	c2_replica:2
0	3	c2_replica:16
0	3	c2_replica:30
0	3	c2_replica:44
0	3	c2_replica:60
0	3	c2_replica:76
0	3	c2_replica:92
0	3	c2_replica:108
0	3	c2_replica:124
0	3	c2_replica:140
0	3	c2_replica:156
0	3	c2_replica:172
0	3	c2_replica:188
0	3	c2_replica:204
0	3	c2_replica:220
0	3	c2_replica:236
0	3	c2_replica:252
0	3	c2_replica:268
0	3	c2_replica:284
0	3	c2_replica:300
1	0	c1_replica:5
1	0	c1_replica:21
1	0	c1_replica:37
1	0	c2_replica:3
1	0	c2_replica:17
1	0	c2_replica:31
1	0	c2_replica:45
1	0	c2_replica:61
1	0	c2_replica:77
1	0	c2_replica:93
1	0	c2_replica:109
1	0	c2_replica:125
1	0	c2_replica:141
1	0	c2_replica:157
1	0	c2_replica:173
1	0	c2_replica:189
1	0	c2_replica:205
1	0	c2_replica:221
1	0	c2_replica:237
1	0	c2_replica:253
1	0	c2_replica:269
1	0	c2_replica:285
1	1	c1_replica:6
1	1	c1_replica:22
1	1	c1_replica:38
1	1	c2_replica:4
1	1	c2_replica:18
1	1	c2_replica:32
1	1	c2_replica:46
1	1	c2_replica:62
1	1	c2_replica:78
1	1	c2_replica:94
1	1	c2_replica:110
1	1	c2_replica:126
1	1	c2_replica:142
1	1	c2_replica:158
1	1	c2_replica:174
1	1	c2_replica:190
1	1	c2_replica:206
1	1	c2_replica:222
1	1	c2_replica:238
1	1	c2_replica:254
1	1	c2_replica:270
1	1	c2_replica:286
1	2	c1_replica:7
1	2	c1_replica:23
1	2	c1_replica:39
1	2	c2_replica:5
1	2	c2_replica:19
1	2	c2_replica:33
1	2	c2_replica:47
1	2	c2_replica:63
1	2	c2_replica:79
1	2	c2_replica:95
1	2	c2_replica:111
1	2	c2_replica:127
1	2	c2_replica:143
1	2	c2_replica:159
1	2	c2_replica:175
1	2	c2_replica:191
1	2	c2_replica:207
1	2	c2_replica:223
1	2	c2_replica:239
1	2	c2_replica:255
1	2	c2_replica:271
1	2	c2_replica:287
1	3	c1_replica:8
1	3	c1_replica:24
1	3	c1_replica:40
1	3	c2_replica:6
1	3	c2_replica:20
1	3	c2_replica:34
1	3	c2_replica:48
1	3	c2_replica:64
1	3	c2_replica:80
1	3	c2_replica:96
1	3	c2_replica:112
1	3	c2_replica:128
1	3	c2_replica:144
1	3	c2_replica:160
1	3	c2_replica:176
1	3	c2_replica:192
1	3	c2_replica:208
1	3	c2_replica:224
1	3	c2_replica:240
1	3	c2_replica:256
1	3	c2_replica:272
1	3	c2_replica:288
2	0	c1_replica:9
2	0	c1_replica:25
2	0	c1_replica:41
2	0	c2_replica:7
2	0	c2_replica:21
2	0	c2_replica:35
2	0	c2_replica:49
2	0	c2_replica:65
2	0	c2_replica:81
2	0	c2_replica:97
2	0	c2_replica:113
2	0	c2_replica:129
2	0	c2_replica:145
2	0	c2_replica:161
2	0	c2_replica:177
2	0	c2_replica:193
2	0	c2_replica:209
2	0	c2_replica:225
2	0	c2_replica:241
2	0	c2_replica:257
2	0	c2_replica:273
2	0	c2_replica:289
2	1	c1_replica:10
2	1	c1_replica:26
2	1	c1_replica:42
2	1	c2_replica:8
2	1	c2_replica:22
2	1	c2_replica:36
2	1	c2_replica:50
2	1	c2_replica:66
2	1	c2_replica:82
2	1	c2_replica:98
2	1	c2_replica:114
2	1	c2_replica:130
2	1	c2_replica:146
2	1	c2_replica:162
2	1	c2_replica:178
2	1	c2_replica:194
2	1	c2_replica:210
2	1	c2_replica:226
2	1	c2_replica:242
2	1	c2_replica:258
2	1	c2_replica:274
2	1	c2_replica:290
2	2	c1_replica:11
2	2	c1_replica:27
2	2	c1_replica:43
2	2	c2_replica:9
2	2	c2_replica:23
2	2	c2_replica:37
2	2	c2_replica:51
2	2	c2_replica:67
2	2	c2_replica:83
2	2	c2_replica:99
2	2	c2_replica:115
2	2	c2_replica:131
2	2	c2_replica:147
2	2	c2_replica:163
2	2	c2_replica:179
2	2	c2_replica:195
2	2	c2_replica:211
2	2	c2_replica:227
2	2	c2_replica:243
2	2	c2_replica:259
2	2	c2_replica:275
2	2	c2_replica:291
2	3	c1_replica:12
2	3	c1_replica:28
2	3	c1_replica:44
2	3	c2_replica:10
2	3	c2_replica:24
2	3	c2_replica:38
2	3	c2_replica:52
2	3	c2_replica:68
2	3	c2_replica:84
2	3	c2_replica:100
2	3	c2_replica:116
2	3	c2_replica:132
2	3	c2_replica:148
2	3	c2_replica:164
2	3	c2_replica:180
2	3	c2_replica:196
2	3	c2_replica:212
2	3	c2_replica:228
2	3	c2_replica:244
2	3	c2_replica:260
2	3	c2_replica:276
2	3	c2_replica:292
3	0	c1_replica:13
3	0	c1_replica:29
3	0	c1_replica:45
3	0	c2_replica:11
3	0	c2_replica:25
3	0	c2_replica:39
3	0	c2_replica:53
3	0	c2_replica:69
3	0	c2_replica:85
3	0	c2_replica:101
3	0	c2_replica:117
3	0	c2_replica:133
3	0	c2_replica:149
3	0	c2_replica:165
3	0	c2_replica:181
3	0	c2_replica:197
3	0	c2_replica:213
3	0	c2_replica:229
3	0	c2_replica:245
3	0	c2_replica:261
3	0	c2_replica:277
3	0	c2_replica:293
3	1	c1_replica:14
3	1	c1_replica:30
3	1	c1_replica:46
3	1	c2_replica:12
3	1	c2_replica:26
3	1	c2_replica:40
3	1	c2_replica:54
3	1	c2_replica:70
3	1	c2_replica:86
3	1	c2_replica:102
3	1	c2_replica:118
3	1	c2_replica:134
3	1	c2_replica:150
3	1	c2_replica:166
3	1	c2_replica:182
3	1	c2_replica:198
3	1	c2_replica:214
3	1	c2_replica:230
3	1	c2_replica:246
3	1	c2_replica:262
3	1	c2_replica:278
3	1	c2_replica:294
3	2	c1_replica:15
3	2	c1_replica:31
3	2	c1_replica:47
3	2	c2_replica:13
3	2	c2_replica:27
3	2	c2_replica:41
3	2	c2_replica:55
3	2	c2_replica:71
3	2	c2_replica:87
3	2	c2_replica:103
3	2	c2_replica:119
3	2	c2_replica:135
3	2	c2_replica:151
3	2	c2_replica:167
3	2	c2_replica:183
3	2	c2_replica:199
3	2	c2_replica:215
3	2	c2_replica:231
3	2	c2_replica:247
3	2	c2_replica:263
3	2	c2_replica:279
3	2	c2_replica:295
3	3	c1_replica:16
3	3	c1_replica:32
3	3	c1_replica:48
3	3	c2_replica:14
3	3	c2_replica:28
3	3	c2_replica:42
3	3	c2_replica:56
3	3	c2_replica:72
3	3	c2_replica:88
3	3	c2_replica:104
3	3	c2_replica:120
3	3	c2_replica:136
3	3	c2_replica:152
3	3	c2_replica:168
3	3	c2_replica:184
3	3	c2_replica:200
3	3	c2_replica:216
3	3	c2_replica:232
3	3	c2_replica:248
3	3	c2_replica:264
3	3	c2_replica:280
3	3	c2_replica:296
LANESEOF
lt=$(sha256sum "$L/lanes.tsv" | cut -d' ' -f1); echo "lanes.tsv sha256 $lt; units $(grep -vc '^#' "$L/lanes.tsv")"
[ "$lt" = "$LANES_SHA" ] || { echo "STOP: lanes.tsv is not the reviewed one"; finish 9; }
cat > "$O/refc2c1_replicas_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 step two, stage 2 (the units), part 2: the replicas, one of 4 single-node jobs (REF-C2C1-BINDING-2.md
# ruling 2.2; the director's ruling of 2026-11-06 on the centrals and the fence; code at M = 77d76cfc from the fresh
# clean clone, with -B). This job runs its 4 lanes of lanes.tsv (column 1 = <J>) concurrently, one srun step per lane,
# `srun --exclusive -n1 -c 64 --mem=120G`, each lane one process running its units in order, at OMP/MKL/OPENBLAS =
# 64/1/1 (NUMEXPR 1, as part B): each unit refuses (rc 4) unless its affinity is exactly 64 and those three variables
# match config.json e_r. The units read only the staged copies (C-IN) and the repository; the c2 units dlopen
# config.json's libRooUnfold.so, whose full sha256 the connect checked. The fence is a recorded line: the full squeue
# at the start. The 303 COV2D inputs (cov2d-watch-paths.txt) are stat'd (no read) before and after; a moved atime is
# a STOP. Porcelain, with --ignored, before and after. Writes only under <O>. Arguments: <deploy> <O> <J>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"; J="${3:?job index}"
M=77d76cfc2d621f8faa010b75006811868494652a
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
U="$O/units"; L="$O/logs-replicas"
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261106 ] || { echo "[c2c1r$J] refusing: O is $O"; exit 2; }
case "$J" in 0|1|2|3) ;; *) echo "[c2c1r] refusing: job index $J"; exit 2;; esac
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[c2c1r$J] refusing: deploy HEAD is not M"; exit 2; }
[ -s "$L/lanes.tsv" ] && [ -s "$L/cov2d-watch-paths.txt" ] && [ -d "$U" ] || { echo "[c2c1r$J] refusing: lanes, watch list or units missing"; exit 2; }
[ ! -e "$O/REPLICAS-DONE-j$J" ] || { echo "[c2c1r$J] refusing: REPLICAS-DONE-j$J exists"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[c2c1r$J] refusing: the deploy is not clean"; exit 2; }
echo "[c2c1r$J] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
echo "[c2c1r$J] fence, recorded (the director's ruling: guarded readers record, not refuse): squeue -u josephrb:"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed "s/^/[c2c1r$J]   /"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-before.txt" 2>&1
echo "[c2c1r$J] COV2D inputs stat'd before: $(wc -l < "$L/j$J-watch-before.txt")"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[c2c1r$J] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp-replicas-j$J" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR"
echo "[c2c1r$J] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
cd "$C" || exit 2
pids=""; n=0
for l in 0 1 2 3; do
  args=(); while IFS=$'\t' read -r jj ll u; do [ "$jj" = "$J" ] && [ "$ll" = "$l" ] && args+=(--unit "$u"); done < <(grep -v '^#' "$L/lanes.tsv")
  n=$((n + ${#args[@]} / 2))
  echo "[c2c1r$J] lane $l: $(( ${#args[@]} / 2 )) units"
  srun --exclusive -n1 -c 64 --mem=120G --job-name="r$J-l$l" \
      /usr/bin/time -v -o "$L/j$J-lane$l.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1.py "${args[@]}" --out "$U" \
      > "$L/j$J-lane$l.log" 2>&1 &
  pids="$pids $!"
done
rcs=""; for p in $pids; do wait "$p"; rcs="$rcs $?"; done
echo "[c2c1r$J] lanes done $(date -u +%FT%TZ); rcs:$rcs"
for l in 0 1 2 3; do
  echo "[c2c1r$J] lane $l: $(grep -E 'Elapsed|Maximum resident|Exit status' "$L/j$J-lane$l.time" | tr -s ' \t' ' ' | tr '\n' ';')"
done
pass=0; for u in $(grep -v '^#' "$L/lanes.tsv" | awk -F'\t' -v j="$J" '$1 == j {print $3}'); do
  name=$(echo "$u" | sed 's/:\(.*\)/_b\1/'); grep -q '"verdict": "PASS"' "$U/$name.done" 2>/dev/null && pass=$((pass + 1))
done
echo "[c2c1r$J] PASS markers: $pass of $n"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-after.txt" 2>&1
if cmp -s "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt"; then moved=0; echo "[c2c1r$J] COV2D inputs: no atime moved"
else moved=1; echo "[c2c1r$J] STOP: a COV2D input's atime moved:"; diff "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt" | head -20; fi
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
printf '{"job": "%s", "index": %s, "units": %s, "pass_markers": %s, "rcs": "%s", "watch_moved": %s, "porcelain_after": %s}\n' \
    "$SLURM_JOB_ID" "$J" "$n" "$pass" "${rcs# }" "$moved" "$na" > "$O/REPLICAS-DONE-j$J"
cat "$O/REPLICAS-DONE-j$J"
[ "$pass" = "$n" ] && [ "$moved" = 0 ] && [ "$na" = 0 ] && [ "$(echo $rcs | tr -d ' 0')" = "" ]
JOBEOF
j=$(sha256sum "$O/refc2c1_replicas_job.sbatch" | cut -d' ' -f1); echo "refc2c1_replicas_job.sbatch sha256 $j"
[ "$j" = "$JOB_SHA" ] || { echo "STOP: the job script is not the reviewed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
cd "$O" || finish 9
jobs=""
for J in 0 1 2 3; do
  sbatch --time=$TLIMIT --job-name=fd_c2c1r --output="$L/%x_%j.out" "$O/refc2c1_replicas_job.sbatch" "$D" "$O" "$J" > "$L/submit-j$J.out" 2>&1
  rc=$?; echo "sbatch j$J rc=$rc: $(cat "$L/submit-j$J.out")"
  job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$L/submit-j$J.out")
  if [ $rc != 0 ] || [ -z "$job" ]; then [ -n "$jobs" ] && scancel $jobs; echo "STOP at sbatch j$J (submitted jobs cancelled: $jobs)"; finish 9; fi
  jobs="$jobs $job"; echo "$J $job" >> "$L/jobs.tsv"
  tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
  echo "j$J job $job scontrol TimeLimit=$tl (declared $TLIMIT)"
  if [ "$tl" != "$TLIMIT" ]; then
    scancel $jobs; echo "STOP: TimeLimit $tl is not $TLIMIT; jobs$jobs cancelled (rc $?)"; sleep 5
    sacct -j "$(echo $jobs | tr ' ' ',')" -X -n -P -o JobID,State,Elapsed; finish 6
  fi
done
sleep 5
squeue -j "$(echo $jobs | tr ' ' ',')" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after submission: $n"
finish 0
