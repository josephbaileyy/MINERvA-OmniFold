# Step 15 (read-only, login node), after the independent review of eeff25b5: hpssquota after the F1 HPSS copy, the F1c
# lane steps' MaxRSS as sacct prints them, and the HPSS directory listing.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
date -u +%FT%TZ; hostname
module load hpss 2>/dev/null; hpssquota 2>&1 | grep -i "HPSS\|Usage"
sacct -n -P -j 60439400 -o JobID,JobName,MaxRSS
hsi -q "ls -l /home/j/josephrb/mnv-5d-f1-20261028" 2>&1
