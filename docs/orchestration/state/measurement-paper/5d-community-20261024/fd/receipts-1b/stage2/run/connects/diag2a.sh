B=/pscratch/sd/j/josephrb/fd-1b-20261030; J=60624652
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== sacct steps"; sacct -j $J -P -n -o JobID,JobName%40,State,ExitCode,Elapsed,MaxRSS,NodeList
echo "=== logs present"; ls -la $B/logs | grep -E "fd1b2an0|$J" ; ls -la $B/runs/2a 2>&1 | head -30
echo "=== batch log tail"; tail -40 $B/logs/fd1b2an0_$J.out
echo "=== grep errors in batch log"; grep -n -i -E "error|fail|traceback|refus|killed|oom|rc=[1-9]|signal|cancel" $B/logs/fd1b2an0_$J.out | head -40
echo "=== partials"; ls -la $B/runs/*/*.partial-* 2>&1 | head
echo "=== pilot-half"; ls -la $B/runs/pilot-half
