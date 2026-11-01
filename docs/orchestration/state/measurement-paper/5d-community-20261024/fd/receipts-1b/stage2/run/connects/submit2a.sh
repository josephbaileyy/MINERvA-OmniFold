B=/pscratch/sd/j/josephrb/fd-1b-20261030
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ -e $B/logs/submit-2a.out ] && { echo "REFUSE: 2a was already submitted"; cat $B/logs/submit-2a.out; exit 3; }
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || { echo "REFUSE: an fd1b job is queued"; exit 3; }
[ "$(grep -c '^sbatch ' $B/logs/l5-submit-2a.txt)" = "3" ] || { echo "REFUSE: l5-submit-2a.txt is not 3 lines"; exit 3; }
bash $B/logs/l5-submit-2a.txt > $B/logs/submit-2a.out 2>&1; echo "rc=$?" >> $B/logs/submit-2a.out
cat $B/logs/submit-2a.out
squeue --me -h -o "%i %j %T %l %D %R"
