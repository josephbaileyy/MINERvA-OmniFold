#!/bin/bash
# COV2D-G2R connect D_Ub (addendum J1 §2; COV2D-G2R-BINDING-1.md addendum J1): the second unfold job, templated from
# the D_Ua connect (46005ade). Its order needs D_Ua's first --miss-map run done (the LightGBM override end-to-end check,
# accepted by the director); g2r_submit.sh's order applies it. It runs beside D_Ua. On a login node it runs:
#   - the fence: no rsn_, e96data, rdx_, t2a or cov2d* job queued or running, and no cov2d* job unended, except
#     COV2D-G2R's own cov2dg2r-* jobs (D_Ua runs; the charge gate holds every one at its limit, and the order allows
#     each job once). ll5d_ is not refused: the audited overlap fence (overlap-fence.diff.txt f40d1000,
#     coverage-5b-audit GO on #1123) lets the LL5D bulk run beside D_Ub;
#   - iris (the cap at most half the balance; the balance is printed for the director's combined LL5D + G2R sum);
#   - the independent recompute of the 110 node-h cap: spent from sacct over cov2dg2r-* plus held from squeue plus
#     this job's THIS, at most 110;
#   - the envtest connect's deploy, reused: a clean checkout at M_J1 (g2r_deploy_ok's porcelain test; ignored files
#     are printed) whose bound blobs still match; no new clone;
#   - the environment test's and the prepare's records on origin/main, each with verdict PASS (the order g2r_submit.sh
#     applies, read first here so a refusal says why), and $MAP's sha256, read through O_NOATIME, equal to the
#     committed prepare record's map_npz_sha256 (the job's own check does the same; here a mismatch costs no node-h);
#   - a stat (no open, so no atime moves) of D_Ub's four inputs ($UNI, $MC, $FLUXU, $MAP): each present, its size and
#     atime printed; and of LL5D's flux-constraint file, whose atime is printed for the bulk's atime-post bracket (G2R's
#     code does not read it);
#   - then the bound g2r_submit.sh, once: D_Ub.
# Nothing else is submitted, and any refusal stops the connect. This log is fetched for the receipt, then it and this
# script are removed from /dev/shm (logged).
# Run: setsid nohup bash /dev/shm/josephrb-g2r-D_Ub.sh >/dev/null 2>&1 </dev/null &
M=401733bce290ce122cfbf38f1526e120f174b3ec         # M_J1 (COV2D-G2R-BINDING-1.md:100, addendum J1, #1118): #1111's merge
P=/pscratch/sd/j/josephrb; A=$P/MINERvA-OmniFold
O=$P/cov2d-g2r-20261112; C=$P/cov2d-g2r-deploy-j1
CAP=110.0; THIS=8.9                                # D_Ub's limit 08:54:00 (jobs_g2r.tsv), one node
LOG=/dev/shm/josephrb-g2r-D_Ub.log
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
[[ $M =~ ^[0-9a-f]{40}$ ]] || { echo "STOP M is not filled"; exit 2; }
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un) M=$M"
# --- the fence
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
echo "cov2dg2r queued or running: [$(squeue --me -h -o '%i %j %T %l' | grep -E '^[0-9]+ cov2dg2r-' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -E '^(rsn_|e96data|rdx_|t2a|cov2d)' | grep -vc '^cov2dg2r-')" = "0" ] \
    || stop "an rsn_, e96data, rdx_, t2a or cov2d (not cov2dg2r-) job is queued or running"
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $2 !~ /^cov2dg2r-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d (not cov2dg2r-) job is unended: $cv"
# --- iris and the independent recompute
echo "== iris"; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}'); [ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP is above half the balance $bal: to Joseph"
spent=$(sacct -X -n -P -S 2026-11-12 -u josephrb -o JobName,State,ElapsedRaw,NNodes | awk -F'|' '$1 ~ /^cov2dg2r-/ && $2 !~ /^(PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|RESIZING)/ {s += $3 * $4} END {printf "%.3f", s / 3600}')
held=$(squeue --me -h -o '%j|%l|%D' | awk -F'|' '$1 ~ /^cov2dg2r-/ {split($2, t, /[-:]/); n = length(t); s = (n == 4 ? t[1]*86400 + t[2]*3600 + t[3]*60 + t[4] : n == 3 ? t[1]*3600 + t[2]*60 + t[3] : t[1]*60 + t[2]); h += s * $3} END {printf "%.3f", h / 3600}')
proj=$(awk -v a=$spent -v b=$held -v c=$THIS 'BEGIN{printf "%.3f", a + b + c}')
echo "recompute spent=$spent held=$held this=$THIS total=$proj cap=$CAP"
awk -v p=$proj -v c=$CAP 'BEGIN{exit !(p <= c)}' || stop "the recompute $proj passes the cap $CAP"
# --- the envtest connect's deploy, reused
[ -d "$O" ] && [ -d "$C" ] || stop "$O or $C is missing (the envtest connect makes them)"
[ -e "$O/logs/bound-D_Ub.sha256" ] && stop "$O/logs/bound-D_Ub.sha256 exists (this connect runs once)"
n=$(git -C "$C" status --porcelain | wc -l); ni=$(git -C "$C" status --porcelain --ignored | grep -c '^!!'); h=$(git -C "$C" rev-parse HEAD)
echo "deploy porcelain=$n ignored=$ni head=$h"   # g2r_deploy_ok's test (untracked counted, ignored only printed)
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "the deploy is not clean at M"
cat > "$O/logs/bound-D_Ub.sha256" <<'SUMS'
7542a68dd344b4cb6252082bfa46d62f512f3c44875bb7d43f17c6368b04f880  2d-unfolding/cov2d/g2r/jobs/g2r_jobs.py
b3ad1d04e6f665b79566fac43f520d2a0329c9d66026f7793f1ab4cf5eb52483  2d-unfolding/cov2d/g2r/jobs/g2r_env.sh
21e4f4ac7330250eb84af653c5a8a0cc8d7fb013489a36d7610025dd539351c8  2d-unfolding/cov2d/g2r/jobs/g2r_job.sbatch
3971fe8596574b4e2c479011a7de422aae3d4fea696a076d68a2dc9ce0189d3f  2d-unfolding/cov2d/g2r/jobs/g2r_envtest.sbatch
3c129b3dd7abb6d47f821f0d61266474a4151dad180c187b8ac43b8730b97433  2d-unfolding/cov2d/g2r/jobs/g2r_prepare.sbatch
a9b2a2ba2f8a902ac9914554e4508dd5dd4fd32ff9f6e291cfb74b3c767c3bc1  2d-unfolding/cov2d/g2r/jobs/g2r_submit.sh
e226daf3f51954c7079cc7b3ab509e464865502f5dbde4acf11876409971dd67  2d-unfolding/re2/re2_driver.py
dbcc416d35565c183d73d6ce03a9efa89dddf8cbda618fa3e6eb00bbe08d28ec  2d-unfolding/cov2d/g2r/g2r.py
bb97fba12034e39c4b6dd5679b93f8259bcc4fab2b69890931c95c1311c7eb57  2d-unfolding/cov2d/g2r/g2r_prepare.py
590ffba1cb8cb65410abee93cd8b3c679b05d4e77155591d619a2f24ba4a0cf1  2d-unfolding/cov2d/g2r/g2r_readout.py
09bcc7b9ca16fd4f7d802ea00d77e7720bc4777041194664911dd7440f9a4936  2d-unfolding/cov2d/jobs/cov2d_jobs.py
3809113878eebefd906155f09cc5ec17745654fc644e074b312590035f0ace5a  2d-unfolding/cov2d/jobs/cov2d_env.sh
76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed  2d-unfolding/cov2d/cov2d.py
c085b51f46afe3675077756aac982d5a7ebc87a5801dd7cbde79dd0f867bd7de  2d-unfolding/cov2d/cov2d_receipt.py
30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b  nd-unfolding/mnv_guarded_run.py
6e4ed0f1d7f55b7bfe2f26752eeb28bb9cbe33325a9d91cc7c06d9494a0b0a70  nd-unfolding/fd_rpd_inputs.py
526b70e0cda78ef476f921d817ff264f67f1b8844b241ca4e65083a196a1127b  docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a  unbinned_unfolding/python/omnifold.py
SUMS
(cd "$C" && sha256sum -c "$O/logs/bound-D_Ub.sha256") || stop "bound blobs differ at M"
# --- the environment test's and the prepare's committed PASS, and the map against the prepare's record
ER=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/envtest/envtest.json
git -C "$C" fetch -q origin main || stop "the fetch of origin main failed"
echo "origin/main=$(git -C "$C" rev-parse origin/main)"
ev=$(git -C "$C" show "origin/main:$ER" 2>/dev/null | python3 -c 'import json, sys; print(json.load(sys.stdin).get("verdict"))' 2>/dev/null)
echo "envtest record on origin/main: verdict=${ev:-absent} sha256=$(git -C "$C" show "origin/main:$ER" 2>/dev/null | sha256sum | cut -c1-64)"
[ "$ev" = PASS ] || stop "the environment test's PASS is not committed on origin/main"
PR=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/prepare/g2r_prepare.json
pv=$(git -C "$C" show "origin/main:$PR" 2>/dev/null | python3 -c 'import json, sys; r = json.load(sys.stdin); print(r.get("verdict"), r.get("map_npz_sha256") or "none")' 2>/dev/null)
echo "prepare record on origin/main: verdict=${pv% *} map_npz_sha256=${pv#* } sha256=$(git -C "$C" show "origin/main:$PR" 2>/dev/null | sha256sum | cut -c1-64)"
[ "${pv% *}" = PASS ] || stop "the prepare's PASS is not committed on origin/main"
MAPF=$O/prepare/g2r_map.npz
ms=$(python3 -c 'import hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256()
while True:
    b = os.read(fd, 1 << 20)
    if not b: break
    h.update(b)
os.close(fd); print(h.hexdigest())' "$MAPF" 2>/dev/null)
echo "map $MAPF sha256=${ms:-unread} (O_NOATIME)"
[ -n "$ms" ] && [ "$ms" = "${pv#* }" ] || stop "the map's sha256 is not the committed prepare record's map_npz_sha256"
# --- the inputs, stat only; and LL5D's flux-constraint file, stat only
for f in "$A/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root" "$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root" \
         "$A/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root" "$MAPF"; do
    s=$(stat --printf '%s %X' "$f" 2>/dev/null) || stop "$f is missing"
    echo "input $f size=${s% *} atime=$(date -u -d "@${s#* }" +%FT%TZ)"
done
CON=$A/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
echo "ll5d constraint $CON atime_epoch=$(stat --printf '%X' "$CON" 2>/dev/null || echo missing) (stat only; not a D_Ub input)"
# --- the one submission
bash "$C/2d-unfolding/cov2d/g2r/jobs/g2r_submit.sh" "$C" "$M" D_Ub; rc=$?; echo "submit D_Ub rc=$rc"
[ -s "$O/submissions.log" ] && cat "$O/submissions.log"
id=$(awk '/ job=D_Ub / {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" 2>/dev/null | tail -1)
[ -n "$id" ] && { scontrol show job "$id" | grep -oE "(JobId|JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo; }
echo "end=$(date -u +%FT%TZ)"; echo DONE
