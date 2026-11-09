#!/bin/bash
# Band diagnosis, P2: the pilot (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 rulings 2-5 and addendum A1).
# Login node, from a fresh deploy clone at M on pscratch. In order, every step stamped to the second:
#   1. iris is read first: the m3246 row; the 9.0 node-h cap must not exceed half the remaining balance (user and
#      project), else STOP to the director;
#   2. the fence (A1, with ENS1 ended): every josephrb job must be named fd1b_bdg_*, ll5d_* or prr_*; ens1_*, rs1_*,
#      cov2d-* or any other name refuses; and no fd1b_bdg_* job may already be queued;
#   3. a fresh clone at M into $W/deploy, HEAD equal and porcelain 0; the module, the packer, s5c_array.sh,
#      mnv_guarded_run.py and setup_salloc_env.sh gated on their sha256 (the setup script also on its blob id);
#   4. the wrapper, Part 1's thread probe (unchanged, d9369712) and the table generator written from this script and
#      gated on their sha256;
#   5. the two tables generated: section 4.3's inputs line, and 8 unfold lines carrying exactly the module's 14
#      pilot_items() (the generator imports the module from the deploy and refuses any difference); printed with sha256;
#   6. section 5's control: the 73 sources stat'd (stat only), compared byte for byte with P1's stat-before.txt
#      (7986e2bf); any difference, a moved atime included, is a STOP and nothing is submitted;
#   7. the thread variables in the submitting shell (none set; the job inherits them through --export=ALL);
#   8. the fence again, immediately before submission; then one sbatch of the wrapper: 1 node,
#      -A m3246 -q regular -C cpu --exclusive --no-requeue --time=01:30:00, job name fd1b_bdg_p2; its parsed
#      TimeLimit must read 01:30:00, else scancel. 1.5 node-h reserved against the 9.0 cap.
# The job runs the probe, then the inputs step (any rc other than 0 is a STOP: no unfold runs), then the 8 lanes. Nothing
# is deleted, and nothing is written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
PACKER_SHA=b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3
S5C_SHA=dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f
GUARD_SHA=30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
SETUP_BLOB=b4a9c3f6bb766d8488cbab98878cbac1262cc1bb
WRAPPER_SHA=d8b9ea6832d7125f2768c5585d2e4735fef71bca8c1c3ba85582e0ec326ae863
PROBE_SHA=d93697123b1e3c5a467efde2488dff8422c684061b39f58fa8cc82c545e6190f
GEN_SHA=3ba4ad306afc937a71fa489c0243ea123464b50dcd8e22a815207cc7a1275ce9
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
CAP=9.0
ts() { date -u +%FT%TZ; }
finish() { echo "== bdg-p2 rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
fence() {
  local out frc bad
  out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
  echo "squeue rc=$frc; rows:"; printf '%s\n' "$out"; echo "-- end rows"
  bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(fd1b_bdg_|ll5d_|prr_)/')
  echo "refusing rows: [$bad]"
  [ "$frc" -eq 0 ] && [ -z "$bad" ] && [ "$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^fd1b_bdg_/' | wc -l)" -eq 0 ]
}
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -s "$W/stat-before.txt" ] && [ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: P1's stat-before.txt is not 7986e2bf"; finish 9; }
[ ! -e "$W/deploy" ] && [ ! -e "$W/p2" ] && [ ! -e "$W/unf" ] || { echo "STOP: $W/deploy, $W/p2 or $W/unf already exists"; finish 9; }
echo "== 1. iris (read first) $(ts)"
irisout=$(iris 2>&1); irc=$?
printf '%s\n' "$irisout" | head -3
row=$(printf '%s\n' "$irisout" | grep -E '^m3246 ' | head -1)
echo "iris rc=$irc; m3246 row: [$row]"
read -r _ uch ual pch pal <<< "$row"
verdict=$(awk -v uch="$uch" -v ual="$ual" -v pch="$pch" -v pal="$pal" -v cap="$CAP" 'BEGIN {
  if (ual == "" || pal == "" || ual+0 <= 0 || pal+0 <= 0) { print "UNREADABLE"; exit }
  ur = ual - uch; pr = pal - pch
  printf "user remaining %.1f, project remaining %.1f, cap %.1f; half user %.1f, half project %.1f -> %s\n", ur, pr, cap, ur/2, pr/2,
    (cap <= ur/2 && cap <= pr/2) ? "OK" : "OVER" }')
echo "balance: $verdict"
case "$verdict" in *"-> OK") ;; *) echo "STOP: the cap is above half the remaining balance, or iris is unreadable"; finish 3 ;; esac
echo "== 2. fence (before anything is written) $(ts)"
fence || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 3. fresh deploy clone at M $(ts)"
mkdir -p "$W/p2/tables" "$W/p2/lanes" "$W/p2/logs" "$W/p2/tools" || finish 9
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold.git "$W/deploy" || { echo "STOP: clone failed"; finish 5; }
git -C "$W/deploy" -c advice.detachedHead=false checkout --quiet --detach "$M" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain | wc -l)
echo "deploy HEAD $head; porcelain lines $porc $(ts)"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M clean"; finish 5; }
for pair in "nd-unfolding/fd_1b_band_diag.py:$MOD_SHA" "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh:$PACKER_SHA" \
            "nd-unfolding/s5c_array.sh:$S5C_SHA" "nd-unfolding/mnv_guarded_run.py:$GUARD_SHA" "setup_salloc_env.sh:$SETUP_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/deploy/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
blob=$(git -C "$W/deploy" rev-parse "$M:setup_salloc_env.sh"); echo "setup_salloc_env.sh blob $blob (bound $SETUP_BLOB)"
[ "$blob" = "$SETUP_BLOB" ] || { echo "STOP: the setup blob"; finish 5; }
echo "== 4. the wrapper, the probe and the table generator"
printf '%s' 'IyEvYmluL2Jhc2gKIyBCYW5kIGRpYWdub3NpcywgdGhlIFAyIGpvYiBzY3JpcHQuIEl0IGNhcnJpZXMgbm8gI1NCQVRDSCBkaXJlY3RpdmVzOiB0aGUgYWNjb3VudCwgUU9TLCBjb25zdHJhaW50LCBub2RlIGNvdW50LAojIGV4Y2x1c2l2aXR5LCByZXF1ZXVlLCBleHBvcnQgYW5kIGxpbWl0IGFyZSBvbiB0aGUgc2JhdGNoIGNvbW1hbmQgbGluZSBpbiB0aGUgY29ubmVjdC4KIyAgIHNiYXRjaCAuLi4gYmRnX3AyX3dyYXBwZXIuc2ggPGRlcGxveT4gPHBpbj4gPGlucHV0cyB0YWJsZT4gPHVuZm9sZCB0YWJsZT4gPGxhbmVzIGRpcj4gPHByb2JlIHNjcmlwdD4gPGlucHV0cyBqc29uPgojIEluIG9yZGVyLCBlYWNoIHN0ZXAgc3RhbXBlZCB0byB0aGUgbWlsbGlzZWNvbmQ6CiMgICAxLiB0aGUgaW4tbGFuZSB0aHJlYWQgcHJvYmUgKFBhcnQgMSdzIHBmZF90aHJlYWRwcm9iZS5weSwgdW5jaGFuZ2VkKTogb25lIHNydW4gc3RlcCB3aXRoIHRoZSBsYW5lcycgZXhhY3Qgc2hhcGUKIyAgICAgICgtLWV4YWN0IC1uMSAtYyAzMiAtLW1lbT01NkcgLS1ncmVzPW5vbmUpLCBhZnRlciB0aGUgc2FtZSBzZXR1cF9zYWxsb2NfZW52LnNoIHNvdXJjZSwgd3JpdGluZyBvbmx5CiMgICAgICA8bGFuZXMgZGlyPi90aHJlYWRwcm9iZS08am9iPi5sb2cuIEEgcHJvYmUgZmFpbHVyZSBpcyByZWNvcmRlZCBhbmQgdGhlIHN0ZXBzIHN0aWxsIHJ1bjsKIyAgIDIuIHNlY3Rpb24gNC4zJ3MgaW5wdXRzIHN0ZXA6IHRoZSBvbmUgbGluZSBvZiA8aW5wdXRzIHRhYmxlPiwgcnVuIGJ5IHRoZSBjb21taXR0ZWQgczVjX2FycmF5LnNoIGluIGEgc3RlcCBvZiB0aGUKIyAgICAgIHNhbWUgc2hhcGUuIEl0cyByYyBpcyBmZF8xYl9iYW5kX2RpYWcucHknczogMCBFUVVBTCwgMSBESUZGRVIsIDggYSBtb3ZlZCBhdGltZSwgNCBhIHJlZnVzYWwuIEFueSByYyBvdGhlciB0aGFuIDAKIyAgICAgIGlzIGEgU1RPUDogdGhlIGpvYiBleGl0cyB3aXRoIHRoYXQgcmMgYW5kIG5vIHVuZm9sZCBydW5zOwojICAgMy4gb25seSB0aGVuLCB0aGUgY29tbWl0dGVkIHBhY2tlciBydW5zIGxpbmVzIDAuLjcgb2YgPHVuZm9sZCB0YWJsZT4gd2l0aCAzMiBDUFVzIGFuZCA1NkcgcGVyIGxpbmUgYW5kIGdyZXMgIm5vbmUiLgpzZXQgLW8gcGlwZWZhaWwgICAjIE5PVCBzZXQgLXUgKHRoZSBzZXR1cCBzY3JpcHQgcmVhZHMgdW5zZXQgdmFyaWFibGVzKQpEPSIkezE6P2RlcGxveX0iOyBQSU49IiR7Mjo/cGlufSI7IElUQUJMRT0iJHszOj9pbnB1dHMgdGFibGV9IjsgVEFCTEU9IiR7NDo/dW5mb2xkIHRhYmxlfSI7IE9VVD0iJHs1Oj9sYW5lcyBkaXJ9IgpQUk9CRT0iJHs2Oj9wcm9iZSBzY3JpcHR9IjsgSUpTT049IiR7Nzo/aW5wdXRzIGpzb259IgpzdGFtcCgpIHsgZGF0ZSAtdSArJUZUJVQuJTNOWjsgfQpta2RpciAtcCAiJHtPVVR9IgplY2hvICJbYmRnLXdyYXBwZXJdICQoc3RhbXApIHN0YXJ0IGpvYj0ke1NMVVJNX0pPQl9JRH0gaG9zdD0kKGhvc3RuYW1lKSBkZXBsb3k9JHtEfSBwaW49JHtQSU59IgplY2hvICJbYmRnLXdyYXBwZXJdIHN1Ym1pdHRpbmctc2hlbGwgdGhyZWFkIHZhcmlhYmxlczogT01QX05VTV9USFJFQURTPSR7T01QX05VTV9USFJFQURTLTx1bnNldD59IE9QRU5CTEFTX05VTV9USFJFQURTPSR7T1BFTkJMQVNfTlVNX1RIUkVBRFMtPHVuc2V0Pn0gTUtMX05VTV9USFJFQURTPSR7TUtMX05VTV9USFJFQURTLTx1bnNldD59IE5VTUVYUFJfTlVNX1RIUkVBRFM9JHtOVU1FWFBSX05VTV9USFJFQURTLTx1bnNldD59IgpzcnVuIC0tZXhhY3QgLW4xIC1jIDMyIC0tbWVtPTU2RyAtLWdyZXM9bm9uZSAtLWpvYi1uYW1lPXRocmVhZHByb2JlIFwKICBiYXNoIC1jICdzb3VyY2UgIiQxL3NldHVwX3NhbGxvY19lbnYuc2giID4gL2Rldi9udWxsIDI+JjE7IGNkICIkMSIgfHwgZXhpdCAyOyBweXRob24zICIkMiInIHRocmVhZHByb2JlICIke0R9IiAiJHtQUk9CRX0iIFwKICA+ICIke09VVCUvfS90aHJlYWRwcm9iZS0ke1NMVVJNX0pPQl9JRH0ubG9nIiAyPiYxCnByYz0kPwplY2hvICJbYmRnLXdyYXBwZXJdICQoc3RhbXApIHByb2JlIHJjPSR7cHJjfSQoIFsgIiR7cHJjfSIgLWVxIDAgXSB8fCBlY2hvICcgKHJlY29yZGVkOyB0aGUgc3RlcHMgc3RpbGwgcnVuKScpIgplY2hvICJbYmRnLXdyYXBwZXJdICQoc3RhbXApIGlucHV0cyBzdGVwIHN0YXJ0IChyZWFkIHdpbmRvdyBvcGVucykiCnNydW4gLS1leGFjdCAtbjEgLWMgMzIgLS1tZW09NTZHIC0tZ3Jlcz1ub25lIC0tam9iLW5hbWU9aW5wdXRzIFwKICBlbnYgU0xVUk1fQVJSQVlfVEFTS19JRD0wIGJhc2ggIiR7RH0vbmQtdW5mb2xkaW5nL3M1Y19hcnJheS5zaCIgIiR7RH0iICIke1BJTn0iICIke0lUQUJMRX0iICIke09VVH0iIFwKICA+ICIke09VVCUvfS9pbnB1dHMtJHtTTFVSTV9KT0JfSUR9LmxvZyIgMj4mMQppcmM9JD8KZWNobyAiW2JkZy13cmFwcGVyXSAkKHN0YW1wKSBpbnB1dHMgc3RlcCByYz0ke2lyY30iCmlmIFsgIiR7aXJjfSIgLW5lIDAgXSB8fCBbICEgLXMgIiR7SUpTT059IiBdOyB0aGVuCiAgZWNobyAiW2JkZy13cmFwcGVyXSAkKHN0YW1wKSBTVE9QOiB0aGUgaW5wdXRzIHN0ZXAgZGlkIG5vdCByZWFkIEVRVUFMIChyYyAke2lyY30pOyBubyB1bmZvbGQgcnVucyIKICBleGl0ICIkKFsgIiR7aXJjfSIgLW5lIDAgXSAmJiBlY2hvICIke2lyY30iIHx8IGVjaG8gOSkiCmZpCmVjaG8gIltiZGctd3JhcHBlcl0gJChzdGFtcCkgdW5mb2xkcyBzdGFydCIKYmFzaCAiJHtEfS9kb2NzL29yY2hlc3RyYXRpb24vc3RhdGUvZ3B1LXRpbWluZy0yMDI2MTAyMy90b29scy9zYmF0Y2hfdGltaW5nX3BhY2tlZC5zaCIgXAogICIke0R9IiAiJHtQSU59IiAiJHtUQUJMRX0iICIke09VVH0iIDMyIDU2RyAwIDcgbm9uZQpyYz0kPwplY2hvICJbYmRnLXdyYXBwZXJdICQoc3RhbXApIHBhY2tlciByYz0ke3JjfSAocmVhZCB3aW5kb3cgY2xvc2VzKSIKZXhpdCAke3JjfQo=' | base64 -d > "$W/p2/tools/bdg_p2_wrapper.sh"
printf '%s' 'IiIiMUIgcHJlLWNoZWNrIFBhcnQgMSwgaW4tbGFuZSB0aHJlYWQgcHJvYmUgKHRoZSBkaXJlY3RvcidzIGNob2ljZSAoaSkgZm9yIFAyIGFuZCBQMykuCgpSdW4gYXMgb25lIHNydW4gc3RlcCB3aXRoIHRoZSBsYW5lcycgZXhhY3Qgc2hhcGUsIGFmdGVyIHRoZSBzYW1lIHNldHVwX3NhbGxvY19lbnYuc2ggc291cmNlIGFzIHM1Y19hcnJheS5zaC4gSXQgcmVhZHMKbm8gYW5hbHlzaXMgaW5wdXQsIGltcG9ydHMgb25seSBudW1weSwgbGlnaHRnYm0gYW5kIHRocmVhZHBvb2xjdGwsIGFuZCBwcmludHMgb25lIEpTT04gb2JqZWN0IHRvIHN0ZG91dDsgdGhlIHdyYXBwZXIKcmVkaXJlY3RzIHN0ZG91dCBpbnRvIHRoZSBqb2IncyBvdXRwdXQgZGlyZWN0b3J5LiBJdHMgZmllbGRzIGFyZSB0aGUgb25lcyBQMydzIHByb2JlIG11c3QgcmVwcm9kdWNlOiB0aGUgZm91ciB0aHJlYWQKdmFyaWFibGVzLCBTTFVSTV9DUFVTX1BFUl9UQVNLLCB0aGUgYWZmaW5pdHkgc2l6ZSBhbmQgdGhyZWFkcG9vbF9pbmZvIGFmdGVyIGltcG9ydGluZyBudW1weSBhbmQgbGlnaHRnYm0uCiIiIgppbXBvcnQganNvbgppbXBvcnQgb3MKaW1wb3J0IHN5cwoKcmVjb3JkID0gewogICAgInRocmVhZF92YXJpYWJsZXMiOiB7azogb3MuZW52aXJvbi5nZXQoaywgIjx1bnNldD4iKQogICAgICAgICAgICAgICAgICAgICAgICAgZm9yIGsgaW4gKCJPTVBfTlVNX1RIUkVBRFMiLCAiT1BFTkJMQVNfTlVNX1RIUkVBRFMiLCAiTUtMX05VTV9USFJFQURTIiwgIk5VTUVYUFJfTlVNX1RIUkVBRFMiKX0sCiAgICAiU0xVUk1fQ1BVU19QRVJfVEFTSyI6IG9zLmVudmlyb24uZ2V0KCJTTFVSTV9DUFVTX1BFUl9UQVNLIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9KT0JfSUQiOiBvcy5lbnZpcm9uLmdldCgiU0xVUk1fSk9CX0lEIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9TVEVQX0lEIjogb3MuZW52aXJvbi5nZXQoIlNMVVJNX1NURVBfSUQiLCAiPHVuc2V0PiIpLAogICAgImFmZmluaXR5X3NpemUiOiBsZW4ob3Muc2NoZWRfZ2V0YWZmaW5pdHkoMCkpIGlmIGhhc2F0dHIob3MsICJzY2hlZF9nZXRhZmZpbml0eSIpIGVsc2UgIjx1bmF2YWlsYWJsZT4iLAogICAgIm9zX2NwdV9jb3VudCI6IG9zLmNwdV9jb3VudCgpLAogICAgInB5dGhvbiI6IHN5cy52ZXJzaW9uLnNwbGl0KClbMF0sCiAgICAiZXhlY3V0YWJsZSI6IHN5cy5leGVjdXRhYmxlLAp9CnRyeToKICAgIGltcG9ydCBudW1weSBhcyBucAogICAgaW1wb3J0IGxpZ2h0Z2JtIGFzIGxnYgogICAgaW1wb3J0IHRocmVhZHBvb2xjdGwKICAgIHJlY29yZFsibnVtcHkiXSA9IG5wLl9fdmVyc2lvbl9fCiAgICByZWNvcmRbImxpZ2h0Z2JtIl0gPSBsZ2IuX192ZXJzaW9uX18KICAgIHJlY29yZFsidGhyZWFkcG9vbGN0bCJdID0gdGhyZWFkcG9vbGN0bC5fX3ZlcnNpb25fXwogICAgaW5mbyA9IHRocmVhZHBvb2xjdGwudGhyZWFkcG9vbF9pbmZvKCkKICAgIHJlY29yZFsidGhyZWFkcG9vbF9pbmZvIl0gPSBbe2s6IGkuZ2V0KGspIGZvciBrIGluICgidXNlcl9hcGkiLCAiaW50ZXJuYWxfYXBpIiwgInByZWZpeCIsICJ2ZXJzaW9uIiwgIm51bV90aHJlYWRzIiwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgImZpbGVwYXRoIil9IGZvciBpIGluIGluZm9dCiAgICBvbXAgPSBbaS5nZXQoIm51bV90aHJlYWRzIikgZm9yIGkgaW4gaW5mbyBpZiBpLmdldCgidXNlcl9hcGkiKSA9PSAib3Blbm1wIl0KICAgIHJlY29yZFsib3Blbm1wX2RlZmF1bHRfbnVtX3RocmVhZHMiXSA9IG9tcCBpZiBvbXAgZWxzZSAiPG5vIG9wZW5tcCBwb29sIGxvYWRlZD4iCiAgICByZWNvcmRbInN0YXR1cyJdID0gIm9rIgpleGNlcHQgRXhjZXB0aW9uIGFzIGU6ICAjIHJlY29yZGVkLCBub3QgcmFpc2VkOiBhIHByb2JlIGZhaWx1cmUgZG9lcyBub3Qgc3RvcCB0aGUgbGFuZXMKICAgIHJlY29yZFsic3RhdHVzIl0gPSBmImZhaWxlZDoge3R5cGUoZSkuX19uYW1lX199OiB7ZX0iCnByaW50KGpzb24uZHVtcHMocmVjb3JkLCBpbmRlbnQ9MSwgc29ydF9rZXlzPVRydWUpKQo=' | base64 -d > "$W/p2/tools/pfd_threadprobe.py"
printf '%s' 'IiIiQmFuZCBkaWFnbm9zaXMsIFAyJ3MgdHdvIHRhc2sgdGFibGVzIChGRC0xQi1CQU5ELURJQUdOT1NJUy1ERUNMQVJBVElPTi5tZCBzZWN0aW9uIDc7IEJJTkRJTkctMSBydWxpbmcgMikuCgp0YXNrcy1wMi1pbnB1dHMudHN2OiBvbmUgbGluZSwgc2VjdGlvbiA0LjMncyBpbnB1dHMgc3RlcCAoZmRfMWJfYmFuZF9kaWFnLnB5IGlucHV0cyksIHJ1biBiZWZvcmUgYW55IHVuZm9sZC4KdGFza3MtcDIudHN2OiBlaWdodCBsaW5lcywgb25lIHBlciBsYW5lIG9mIG9uZSBub2RlLCBhdCBtb3N0IHR3byBpdGVtcyBwZXIgbGFuZSwgZXhhY3RseSBzZWN0aW9uIDcncyAxNCBwaWxvdCBpdGVtczoKICBFIGF0IHNlZWQgNDIsIGVwcyAxLCBjaGFubmVsIGJvdGgsIGZvciBDViBhbmQgdGhlIDggZGV0ZWN0b3IgdW5pdmVyc2VzICg1IGxpbmVzOiAyLCAyLCAyLCAyLCAxKTsKICBCIHRoZSBzYW1lIGZvciBDViBhbmQgdGhlIDQgR0VBTlRfTmV1dHJvbi9HRUFOVF9Qcm90b24gdW5pdmVyc2VzICgzIGxpbmVzOiAyLCAyLCAxKS4KRWFjaCBsaW5lIGlzICI8bmFtZT48VEFCPmZkXzFiX2JhbmRfZGlhZy5weTxUQUI+PGFyZ3M+IiwgcnVuIGJ5IHRoZSBjb21taXR0ZWQgczVjX2FycmF5LnNoLiBUaGUgbW9kdWxlJ3Mgb3duCnBpbG90X2l0ZW1zKCksIGltcG9ydGVkIGZyb20gdGhlIGRlcGxveSBjaGVja291dCwgbXVzdCBlcXVhbCB0aGUgaXRlbXMgdGhlIGVpZ2h0IGxpbmVzIGNhcnJ5OyBhbnkgZGlmZmVyZW5jZSByZWZ1c2VzLgoKdXNhZ2U6IHB5dGhvbjMgbWFrZV9iZGdfcDJfdGFibGVzLnB5IDxkZXBsb3kgY2hlY2tvdXQ+IDxXPiA8dGFibGVzIGRpcj4KIiIiCmltcG9ydCBzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgpQID0gIi9wc2NyYXRjaC9zZC9qL2pvc2VwaHJiIgpQSU5TX1NIQSA9ICI1YWRjZDU3NmViNDZmNDQzZmU0MTMzYjA1MDQ0Y2QzMTVjMGVlYjBmMjgxZTIxYWNlZTVmMjMxOGI0YmFiMjQ4IgoKCmRlZiBtYWluKCkgLT4gaW50OgogICAgZGVwbG95LCBXLCBvdXQgPSBQYXRoKHN5cy5hcmd2WzFdKSwgc3lzLmFyZ3ZbMl0sIFBhdGgoc3lzLmFyZ3ZbM10pCiAgICBzeXMucGF0aC5pbnNlcnQoMCwgc3RyKGRlcGxveSAvICJuZC11bmZvbGRpbmciKSkKICAgIGltcG9ydCBmZF8xYl9iYW5kX2RpYWcgYXMgZCAgIyBub3FhOiBFNDAyICAodGhlIGRlcGxveSdzIGJ5dGVzOyB0aGUgY29ubmVjdCBnYXRlcyB0aGVpciBzaGEyNTYpCiAgICBkZXQsIHN1YiA9IGQuZGV0ZWN0b3JfdW5pdmVyc2VzKCksIGQuc3ViamVjdF91bml2ZXJzZXMoKQogICAgZ3JvdXBzID0gWygiRSIsIHUpIGZvciB1IGluIFtbIkNWIiwgZGV0WzBdXSwgZGV0WzE6M10sIGRldFszOjVdLCBkZXRbNTo3XSwgZGV0Wzc6OF1dXQogICAgZ3JvdXBzICs9IFsoIkIiLCB1KSBmb3IgdSBpbiBbWyJDViIsIHN1YlswXV0sIHN1YlsxOjNdLCBzdWJbMzo0XV1dCiAgICBjYXJyaWVkID0gWyhtLCB1LCBkLkJBU0VfU0VFRCwgMS4wLCAiYm90aCIpIGZvciBtLCB1cyBpbiBncm91cHMgZm9yIHUgaW4gdXNdCiAgICBpZiBzb3J0ZWQoY2FycmllZCkgIT0gc29ydGVkKGQucGlsb3RfaXRlbXMoKSkgb3IgbGVuKGNhcnJpZWQpICE9IDE0OgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoZiJUQUJMRTogdGhlIGxpbmVzIGNhcnJ5IHtjYXJyaWVkfSwgbm90IHRoZSBtb2R1bGUncyBwaWxvdF9pdGVtcygpIHtkLnBpbG90X2l0ZW1zKCl9IikKICAgIGlmIGxlbihncm91cHMpICE9IDggb3IgbWF4KGxlbih1cykgZm9yIF8sIHVzIGluIGdyb3VwcykgPiAyOgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiBub3QgZWlnaHQgbGFuZXMgb2YgYXQgbW9zdCB0d28gaXRlbXMiKQogICAgaW5wdXRzID0gWyItLW5weiIsIGYie1B9L01JTkVSdkEtT21uaUZvbGQvbmQtdW5mb2xkaW5nL29mX2lucHV0c181ZC5ucHoiLAogICAgICAgICAgICAgICItLWJrZyIsIGYie1B9L3M1Yy0yMDI2MDkyNC9ydW5zL3AyL2JrZ19kdW1wLm5weiIsCiAgICAgICAgICAgICAgIi0tYmFuayIsIGYie1B9L01JTkVSdkEtT21uaUZvbGQvbmQtdW5mb2xkaW5nL2Jhbmtfc3dlZXBfNWRfYmtnYXdhcmUiLAogICAgICAgICAgICAgICItLWRldGVjdG9yLWRpciIsIGYie1B9L3M1cC0yMDI2MDkyNi9iYW5rX2RldGVjdG9yIiwKICAgICAgICAgICAgICAiLS1waW5zIiwgZiJ7UH0vZmQtMWItMjAyNjEwMzAvcGlucy5qc29uIiwgIi0tZXhwZWN0LXBpbnMtc2hhMjU2IiwgUElOU19TSEFdCiAgICBoZWFkID0gIiMgYmFuZCBkaWFnbm9zaXMsIFAyIChGRC0xQi1CQU5ELURJQUdOT1NJUy1ERUNMQVJBVElPTi5tZCBzZWN0aW9uIDc7IEJJTkRJTkctMSBydWxpbmcgMikiCiAgICBsaW5lcyA9IFtoZWFkLCAiXHQiLmpvaW4oWyJmZDFiX2JkZ19wMl9pbnB1dHMiLCAiZmRfMWJfYmFuZF9kaWFnLnB5IiwgImlucHV0cyJdICsgaW5wdXRzCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKyBbIi0tb3V0IiwgZiJ7V30vcDIvaW5wdXRzLmpzb24iXSldCiAgICAob3V0IC8gInRhc2tzLXAyLWlucHV0cy50c3YiKS53cml0ZV90ZXh0KCJcbiIuam9pbihsaW5lcykgKyAiXG4iKQogICAgbGluZXMgPSBbaGVhZF0KICAgIGZvciBpLCAobSwgdXMpIGluIGVudW1lcmF0ZShncm91cHMpOgogICAgICAgIGxpbmVzLmFwcGVuZCgiXHQiLmpvaW4oW2YiZmQxYl9iZGdfcDJfe2l9X3ttfSIsICJmZF8xYl9iYW5kX2RpYWcucHkiLCAidW5mb2xkIiwgIi0tbW9kZSIsIG0sICItLXNlZWQiLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHN0cihkLkJBU0VfU0VFRCksICItLWVwcyIsICIxIiwgIi0tY2hhbm5lbCIsICJib3RoIiwgIi0tdW5pdmVyc2VzIiwgIiwiLmpvaW4odXMpXQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKyBpbnB1dHMgKyBbIi0tdGhyZWFkcyIsICIzMiIsICItLW91dCIsIGYie1d9L3VuZiJdKSkKICAgIChvdXQgLyAidGFza3MtcDIudHN2Iikud3JpdGVfdGV4dCgiXG4iLmpvaW4obGluZXMpICsgIlxuIikKICAgIHByaW50KGYiVEFCTEVTOiAxIGlucHV0cyBsaW5lOyA4IHVuZm9sZCBsaW5lcyBjYXJyeWluZyB0aGUgMTQgcGlsb3QgaXRlbXM6ICIKICAgICAgICAgICsgIjsgIi5qb2luKGYie219IHsnLCcuam9pbih1cyl9IiBmb3IgbSwgdXMgaW4gZ3JvdXBzKSkKICAgIHJldHVybiAwCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9fIjoKICAgIHN5cy5leGl0KG1haW4oKSkK' | base64 -d > "$W/p2/tools/make_bdg_p2_tables.py"
for pair in "bdg_p2_wrapper.sh:$WRAPPER_SHA" "pfd_threadprobe.py:$PROBE_SHA" "make_bdg_p2_tables.py:$GEN_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/p2/tools/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 5. the task tables $(ts)"
env -u PYTHONPATH "$PY" -B "$W/p2/tools/make_bdg_p2_tables.py" "$W/deploy" "$W" "$W/p2/tables" || { echo "STOP: the table generator refused"; finish 5; }
for t in tasks-p2-inputs.tsv tasks-p2.tsv; do echo "$t sha256 $(sha256sum "$W/p2/tables/$t" | cut -d' ' -f1)"; cat "$W/p2/tables/$t"; done
n=$(grep -v '^#' "$W/p2/tables/tasks-p2.tsv" | grep -c -v '^[[:space:]]*$'); ni=$(grep -v '^#' "$W/p2/tables/tasks-p2-inputs.tsv" | grep -c -v '^[[:space:]]*$')
echo "unfold lines $n; inputs lines $ni"
[ "$n" -eq 8 ] && [ "$ni" -eq 1 ] || { echo "STOP: the tables are not 8 + 1 lines"; finish 5; }
echo "== 6. section 5's control: the 73 sources against P1's stat-before.txt (stat only) $(ts)"
env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
  | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$W/p2/logs/stat-submit.txt"
echo "stat-submit.txt: $(wc -l < "$W/p2/logs/stat-submit.txt") lines; sha256 $(sha256sum "$W/p2/logs/stat-submit.txt" | cut -d' ' -f1) $(ts)"
if cmp -s "$W/stat-before.txt" "$W/p2/logs/stat-submit.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat differs from P1's stat-before; nothing submitted:"; diff "$W/stat-before.txt" "$W/p2/logs/stat-submit.txt" | head -40; finish 4; fi
echo "== 7. thread variables in the submitting shell (none set; inherited by the job through --export=ALL)"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 8. fence, immediately before submission $(ts)"
fence || { echo "STOP: the fence is not clear; nothing submitted"; finish 3; }
echo "FENCE: clear"
cat > "$W/p2/logs/submit-p2.txt" <<SUB
sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb --time=01:30:00 -J fd1b_bdg_p2 -o $W/p2/logs/%x_%j.out $W/p2/tools/bdg_p2_wrapper.sh $W/deploy $M $W/p2/tables/tasks-p2-inputs.tsv $W/p2/tables/tasks-p2.tsv $W/p2/lanes $W/p2/tools/pfd_threadprobe.py $W/p2/inputs.json
SUB
cat "$W/p2/logs/submit-p2.txt"
sub=$(bash "$W/p2/logs/submit-p2.txt" 2>&1); src=$?
echo "$sub" | tee "$W/p2/logs/submit-p2.out"; echo "sbatch rc=$src $(ts)"
job=$(printf '%s\n' "$sub" | awk '/^Submitted batch job/ {print $4}')
[ "$src" -eq 0 ] && [ -n "$job" ] || { echo "STOP: sbatch failed"; finish 6; }
tl=$(scontrol show job "$job" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
echo "job $job TimeLimit=$tl"
if [ "$tl" != "01:30:00" ]; then echo "STOP: TimeLimit is not 01:30:00; scancel $job"; scancel "$job"; echo "scancel rc=$?"; finish 7; fi
squeue -u josephrb -h -o '%i %j %T %l %D %R'
finish 0
