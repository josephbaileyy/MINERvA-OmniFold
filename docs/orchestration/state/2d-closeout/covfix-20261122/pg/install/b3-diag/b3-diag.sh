#!/bin/bash
# One read-only diagnostic of B3 run 2's exe-check STOP (for the director's GO). In B3's own replay directory
# (covfix-pg/replay-20261126T211924Z: public seed only, stopped before any GENIE program ran) it prints the driver's
# log and the records it wrote for that step; then it lists the compat-lib shim directory that setup_genie_v3.sh puts
# first on LD_LIBRARY_PATH ($HOME/.genie_compatlibs, HOME from passwd as the runner sets it) with each entry's
# readlink -f. cat, ls and readlink only: nothing is written on NERSC. The output stays on the laptop.
set -u
OUT="$(dirname "$0")/b3-diag.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /bin/bash -c 'W=/pscratch/sd/j/josephrb/covfix-pg/replay-20261126T211924Z; R=\$W/run; HM=\$(getent passwd \$(id -un) | cut -d: -f6); hostname; ls -ld \"\$W\" \"\$R\"; echo == driver.log; cat \"\$W/driver.log\"; echo == exe_check.json; cat \"\$R/exe_check.json\"; echo; echo == logs/exe.log; cat \"\$R/logs/exe.log\"; echo == exe and ld_library_path records; for t in G21_11a_00_000 G18_02a_00_000; do for k in exe ld_library_path awk gxmlpath; do echo \"-- \${k}_\$t\"; cat \"\$R/\${k}_\$t.txt\"; done; done; echo == compat \$HM/.genie_compatlibs; ls -la \"\$HM/.genie_compatlibs\"; for f in \"\$HM\"/.genie_compatlibs/*; do printf \"%s -> %s\\n\" \"\$f\" \"\$(readlink -f \"\$f\")\"; done; echo == end'" \
  < /dev/null > "$OUT" 2>&1
