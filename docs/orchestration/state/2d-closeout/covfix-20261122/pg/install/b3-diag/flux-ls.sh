#!/bin/bash
# One read-only metadata check of B3's flux input (the director's GO (3), 2026-11-26): ls -ld and stat of the
# directory and its immediate entries. No file is opened or read; nothing is written on NERSC. The output is kept
# on the laptop only.
set -u
OUT="$(dirname "$0")/flux-ls.out"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 5; }
H="$HOME"
exec /usr/bin/ssh -F /dev/null -o BatchMode=yes -o User=josephrb -o IdentitiesOnly=yes \
  -o IdentityFile="$H/.ssh/nersc" -o CertificateFile="$H/.ssh/nersc-cert.pub" \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$H/.ssh/known_hosts" \
  -o ForwardAgent=no -o ForwardX11=no -o ClearAllForwardings=yes -o PermitLocalCommand=no \
  -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov \
  "env -i PATH=/usr/bin:/bin LC_ALL=C /bin/bash -c 'F=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix; hostname; ls -ld \"\$F\"; echo rc_ls_dir=\$?; stat -c \"%n|%F|%s|%y|%x\" \"\$F\" \"\$F\"/* 2>&1; echo rc_stat=\$?'" \
  < /dev/null > "$OUT" 2>&1
