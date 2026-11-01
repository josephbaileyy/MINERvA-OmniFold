B=/pscratch/sd/j/josephrb/fd-1b-20261030
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ -e $B/logs/submit-2a-r.out ] && { echo "REFUSE: 2a-r was already submitted"; cat $B/logs/submit-2a-r.out; exit 3; }
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || { echo "REFUSE: an fd1b job is queued"; exit 3; }
[ "$(grep -c '^sbatch ' $B/logs/a4-submit-2a-r.txt)" = "1" ] || { echo "REFUSE: a4-submit-2a-r.txt is not 1 line"; exit 3; }
bash $B/logs/a4-submit-2a-r.txt > $B/logs/submit-2a-r.out 2>&1; echo "rc=$?" >> $B/logs/submit-2a-r.out
cat $B/logs/submit-2a-r.out
squeue --me -h -o "%i %j %T %l %D %R"
