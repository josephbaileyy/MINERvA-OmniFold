#!/bin/bash
# coverage-5b-audit: launch remote_tieread.sh on a Perlmutter login node; ssh rc read unpiped.
S=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/71f27b67-dd03-4235-a8c6-c96eb2b6c57e/scratchpad/tieread
ssh -o ControlPath=none -o ConnectTimeout=30 saul.nersc.gov bash -s < "$S/remote_tieread.sh" > "$S/tieread.out.txt" 2>&1
rc=$?
echo "ssh rc=$rc" >> "$S/tieread.out.txt"
exit $rc
