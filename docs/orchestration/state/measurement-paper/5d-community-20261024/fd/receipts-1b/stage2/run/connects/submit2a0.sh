B=/pscratch/sd/j/josephrb/fd-1b-20261030
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ -e $B/logs/submit-2a-0.out ] && { echo "REFUSE: 2a-0 was already submitted"; cat $B/logs/submit-2a-0.out; exit 3; }
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || { echo "REFUSE: an fd1b job is queued"; exit 3; }
bash $B/logs/l5-submit-2a-0.txt > $B/logs/submit-2a-0.out 2>&1; echo "rc=$?" >> $B/logs/submit-2a-0.out
cat $B/logs/submit-2a-0.out
squeue --me -h -o "%i %j %T %l %D %R"
