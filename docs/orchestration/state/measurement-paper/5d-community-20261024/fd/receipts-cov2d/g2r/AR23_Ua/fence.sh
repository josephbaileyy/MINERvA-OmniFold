echo "fence host=$(hostname) utc=$(date -u +%FT%TZ)"
echo "squeue:"; squeue -u josephrb -h -o '%i %j %T'
echo "sacct unended cov2d:"; sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $2 !~ /^cov2dg2r-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/'
echo "fence end"
