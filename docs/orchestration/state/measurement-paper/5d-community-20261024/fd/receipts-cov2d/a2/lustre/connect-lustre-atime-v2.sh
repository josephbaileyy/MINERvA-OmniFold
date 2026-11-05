#!/bin/bash
# COV2D connect LUSTRE-ATIME v2: Joseph's ruling of 2026-11-05 (A2 item 5), the atime settings of /pscratch's Lustre,
# where they can be read without privilege, on a login node. 0 node-h; it opens no data file and reads no file under
# /pscratch or /global/cfs: only /proc/mounts, findmnt, and lctl's client parameter lists. Every command's output and
# rc is logged, including refusals, so the record says what could not be read. The compute nodes' settings are not
# read here (a login node is not a compute node; the record says so).
# Run on login02: bash /dev/shm/josephrb-cov2d-lustre2.sh > /dev/shm/josephrb-cov2d-lustre2.log 2>&1
L=/usr/sbin/lctl   # v2: lctl is not on the user PATH (v1 rc 127); full path
run() { echo "\$ $*"; "$@" 2>&1; echo "rc=$?"; echo; }
echo "host=$(hostname) start=$(date -u +%FT%TZ) kernel=$(uname -r)"
run grep -E ' /pscratch | lustre ' /proc/mounts
run findmnt -T /pscratch -o TARGET,SOURCE,FSTYPE,OPTIONS
run $L --version
run $L list_param llite.*
run sh -c "$L list_param -R 'llite.*' 2>&1 | grep -i -E 'atime|lazy|stat' | head -40"
run $L get_param 'llite.*.lazystatfs' 'llite.*.statahead_max' 'llite.*.xattr_cache'
run sh -c "$L get_param 'mdc.*.atime*' 'llite.*.*atime*' 2>&1 | head -20"
run sh -c "$L list_param -R 'mdc.*' 2>&1 | grep -i atime | head -20"
echo "end=$(date -u +%FT%TZ)"; echo DONE
