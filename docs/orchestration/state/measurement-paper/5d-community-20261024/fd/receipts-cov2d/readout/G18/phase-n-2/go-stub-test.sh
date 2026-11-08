#!/bin/bash
# go.sh against a STUB launcher (director's ruling 4, A5 M line): the copy in $S differs from go.sh only in LAUNCHER_SHA = the stub's
W=/Users/josephbailey/cov2d-work; S=$W/a4/gostub
LS=$(shasum -a 256 "$S/launch-s5.sh" | cut -c1-64); CS=$(shasum -a 256 "$S/connect-n-G18.sh" | cut -c1-64); Z=$(printf '0%.0s' {1..64})
echo "go.sh sha256 $(shasum -a 256 "$W/go.sh" | cut -c1-64); stub launcher $LS; stub connect $CS"
echo "copy vs go.sh:"; diff "$W/go.sh" "$S/go.sh"
t() { echo "== $1: go.sh ${*:2}"; bash "$S/go.sh" "${@:2}"; echo "rc=$?"; }
t "right digests" nG18 "$CS"
t "wrong connect digest" nG18 "$Z"
t "no such connect" sAR23 "$CS"
t "no digest" nG18
cp "$S/launch-s5.sh" "$S/l.bak"; echo '#' >> "$S/launch-s5.sh"; t "launcher changed" nG18 "$CS"; mv "$S/l.bak" "$S/launch-s5.sh"
