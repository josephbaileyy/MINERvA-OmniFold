# Sourced by mp2_s2_job.sh and its step-0 concurrency test: the job's memory allocation in MiB.
# Perlmutter leaves SLURM_MEM_PER_NODE unset when sbatch gives no --mem (60112440), so read AllocTRES instead.
alloc_mem_mib() {
  if [ -n "$SLURM_MEM_PER_NODE" ]; then echo "$SLURM_MEM_PER_NODE"; return 0; fi
  local m
  m=$(scontrol show job -o "${SLURM_JOB_ID:?no SLURM_JOB_ID}" | tr ' ' '\n' | sed -n 's/^AllocTRES=//p' | tr ',' '\n' | sed -n 's/^mem=//p')
  awk -v m="$m" 'BEGIN { u = substr(m, length(m)); v = substr(m, 1, length(m) - 1) + 0
    f = (u == "M") ? 1 : (u == "G") ? 1024 : (u == "T") ? 1048576 : 0
    if (f == 0 || v <= 0) { print "STOP: cannot read the job memory from AllocTRES mem=" m > "/dev/stderr"; exit 4 }
    printf "%d\n", v * f }'
}
