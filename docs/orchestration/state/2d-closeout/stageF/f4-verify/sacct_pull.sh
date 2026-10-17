#!/bin/bash
V=/pscratch/sd/j/josephrb/tmp-stagec-f4-verify-20261017
TZ=UTC sacct -X -n -P -S 2026-10-15T00:00:00 -E now -u josephrb \
  --format=JobID,JobName%60,QOS,State,Submit,Start,End,ElapsedRaw,TimelimitRaw,AllocTRES%80,ExitCode,Reason > $V/sacct_X.txt
echo "rc_X=$?"
TZ=UTC sacct -n -P -S 2026-10-15T00:00:00 -E now -u josephrb \
  --format=JobID,JobName%60,QOS,State,Start,End,ElapsedRaw,ExitCode,MaxRSS > $V/sacct_steps.txt
echo "rc_steps=$?"
wc -l $V/sacct_X.txt $V/sacct_steps.txt
