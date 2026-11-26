#!/bin/bash
# OOFVC post, on a login node, through oofvc_launch.sh: sacct for every OOFVC job, the charge, and post.tar.gz of the
# records (logs, the dumps' logs and digests, the join's record and rows, the units, the deploy's digests). The
# staged copies and the dump ROOT files are not archived; their digests are. Writes only $R/post and $R/post.tar.gz.
set -u
R=/pscratch/sd/j/josephrb/oofvc-20261126
[ ! -e "$R/post" ] && [ ! -e "$R/post.tar.gz" ] || { echo "STOP: post exists"; exit 2; }
sq=$(squeue -h -u "$USER" -o '%j') || { echo "STOP: squeue failed"; exit 2; }
q=$(printf '%s\n' "$sq" | grep -c '^oofvc_' || true)
[ "$q" = 0 ] || { echo "STOP: an oofvc job is still queued or running"; exit 2; }
mkdir -p "$R/post" || exit 2
{ echo "node $(hostname) $(date -u +%FT%TZ)"
  for f in pilot rest units; do
    [ -e "$R/logs/$f.jobid" ] || continue
    j=$(cat "$R/logs/$f.jobid")
    TZ=UTC sacct -j "$j" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES,Start,End,NodeList
  done; } > "$R/post/sacct.txt" 2>&1
# charge: shared tasks as Test C counts them (ElapsedRaw x AllocCPUS / 2 / 128 / 3600); the exclusive units node as
# ElapsedRaw / 3600 (one node). Allocation lines only (no '.' in JobID).
awk -F'|' 'NR > 1 && $1 !~ /\./ && $2 == "oofvc_dump" {s += $5 * $6 / 2 / 128 / 3600}
           NR > 1 && $1 !~ /\./ && $2 == "oofvc_units" {u += $5 / 3600}
           END {printf "dump_node_h=%.4f units_node_h=%.4f total_node_h=%.4f\n", s, u, s + u}' "$R/post/sacct.txt" \
  > "$R/post/charge.txt"
cat "$R/post/sacct.txt" "$R/post/charge.txt"
(cd "$R" && sha256sum dump/*.root stage/* 2>/dev/null) > "$R/post/large.sha256"
(cd "$R" && tar -czf "$R/post.tar.gz" logs post join units gates dump/built.sha256 dump/manifests.sha256 dump/*.log \
  dump/[0-9]*.sha256 dump/*.done) || { echo "STOP: tar"; exit 3; }
sha256sum "$R/post.tar.gz"
echo "post rc=0 $(date -u +%FT%TZ)"
