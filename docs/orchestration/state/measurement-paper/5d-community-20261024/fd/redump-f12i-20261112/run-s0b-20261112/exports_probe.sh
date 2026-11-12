echo "== host $(hostname -s) $(date -u +%FT%TZ)"
bash -c 'env | cut -d= -f1 | sort > /tmp/rdx_env_a.$$; source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1; env | cut -d= -f1 | sort > /tmp/rdx_env_b.$$; comm -13 /tmp/rdx_env_a.$$ /tmp/rdx_env_b.$$; rm -f /tmp/rdx_env_a.$$ /tmp/rdx_env_b.$$'
echo "== end"
