echo "== host $(hostname -s) $(date -u +%FT%TZ) pwd-at-login $(pwd)"
ls -la ~/x86_64-conda-linux-gnu ~/x86_64-conda-linux-gnu/* /pscratch/sd/j/josephrb/MINERvA-OmniFold/x86_64-conda-linux-gnu 2>&1
grep -n "^ *cd " /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
echo "== variables setup_salloc_env.sh adds"
bash -c 'env | cut -d= -f1 | sort > /tmp/rdx_env_a.$$; source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1; env | cut -d= -f1 | sort > /tmp/rdx_env_b.$$; comm -13 /tmp/rdx_env_a.$$ /tmp/rdx_env_b.$$; rm -f /tmp/rdx_env_a.$$ /tmp/rdx_env_b.$$'
echo "== end"
