#!/bin/bash
# Band diagnosis, P3: the bulk (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 rulings 2-5 as addenda A1 and
# A2 set them: 4 jobs x 7 lanes x 4 items, --time=01:40:00). Login node; every step stamped to the second. In order:
#   1. iris first: the 9.0 node-h cap must not exceed half the remaining balance (user and project), else STOP;
#   2. P2's gates are on disk: $W/p2/inputs.json reads EQUAL and $W/p2/pilot.json reads PASS, else STOP;
#   3. the fence (A1): every josephrb job must be named fd1b_bdg_*, ll5d_* or prr_*; ens1_*, rs1_*, cov2d-* or any
#      other name refuses; and no fd1b_bdg_* job may be queued;
#   4. the deploy $W/deploy (P2's) is still M with no tracked change; the module, the packer, s5c_array.sh,
#      mnv_guarded_run.py and setup_salloc_env.sh gated on their sha256;
#   5. Part 1's committed P2/P3 job script (pfd_p2_wrapper.sh 038a6353, unchanged), Part 1's thread probe (d9369712,
#      unchanged) and the P3 table generator written from this script and gated on their sha256;
#   6. the table: 28 lines, each one unfold call over 4 items of one (mode, seed, eps, channel) group; the generator
#      imports the module from the deploy and refuses unless the lines carry exactly bulk_items(); job j runs lines
#      7j..7j+6;
#   7. section 5's control: the 73 sources re-stat'd and compared byte for byte with P1's stat-before.txt (7986e2bf);
#      any difference is a STOP and nothing is submitted;
#   8. the fence again, then four sbatch of the wrapper, each 1 node, -A m3246 -q regular -C cpu --exclusive
#      --no-requeue --time=01:40:00, job name fd1b_bdg_p3, lines 7j..7j+6; each parsed TimeLimit must read 01:40:00,
#      else every P3 job is cancelled. 6.67 node-h reserved; 8.17 with P2, against the 9.0 cap.
# Nothing is deleted or written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
ts() { date -u +%FT%TZ; }
restat() {  # $1 = output file: the 73 sources of P1's stat-before.txt, stat only
  env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
    | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$1"
}
PACKER_SHA=b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3
S5C_SHA=dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f
GUARD_SHA=30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
WRAPPER_SHA=038a6353b81a066476f96312e9764feac714bdc3cc350b5e533fd2a40f6e0256
PROBE_SHA=d93697123b1e3c5a467efde2488dff8422c684061b39f58fa8cc82c545e6190f
GEN_SHA=0aed80b85788a1497eaf461dea1b86a631f7c32bb4a3bc05efc33335487d3954
CAP=9.0
finish() { echo "== bdg-p3 rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
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
[ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: stat-before.txt is not 7986e2bf"; finish 9; }
[ ! -e "$W/p3" ] || { echo "STOP: $W/p3 already exists"; finish 9; }
echo "== 1. iris (read first) $(ts)"
irisout=$(iris 2>&1); irc=$?
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
echo "== 2. P2's gates on disk $(ts)"
g=$(env -u PYTHONPATH "$PY" -B -c 'import json,sys; i=json.load(open(sys.argv[1]))["verdict"]; p=json.load(open(sys.argv[2]))["verdict"]; print(i, p)' "$W/p2/inputs.json" "$W/p2/pilot.json" 2>&1)
echo "inputs and pilot verdicts: [$g]"
[ "$g" = "EQUAL PASS" ] || { echo "STOP: P2's gates are not EQUAL and PASS"; finish 3; }
echo "== 3. fence (before anything is written) $(ts)"
fence || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 4. the deploy $(ts)"
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain --untracked-files=no | wc -l)
echo "deploy HEAD $head; tracked porcelain $porc"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M clean"; finish 5; }
for pair in "nd-unfolding/fd_1b_band_diag.py:$MOD_SHA" "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh:$PACKER_SHA" \
            "nd-unfolding/s5c_array.sh:$S5C_SHA" "nd-unfolding/mnv_guarded_run.py:$GUARD_SHA" "setup_salloc_env.sh:$SETUP_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/deploy/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
echo "== 5. the job script, the probe and the table generator"
mkdir -p "$W/p3/tables" "$W/p3/lanes" "$W/p3/logs" "$W/p3/tools" || finish 9
printf '%s' 'IyEvYmluL2Jhc2gKIyAxQiBwcmUtY2hlY2sgUGFydCAxLCB0aGUgUDIvUDMgam9iIHNjcmlwdCAodGhlIGRpcmVjdG9yJ3MgY2hvaWNlIChpKSk6IG9uZSBpbi1sYW5lIHRocmVhZCBwcm9iZSBzdGVwLCB0aGVuIHRoZQojIGNvbW1pdHRlZCBwYWNrZXIgdW5jaGFuZ2VkLiBJdCBjYXJyaWVzIG5vICNTQkFUQ0ggZGlyZWN0aXZlcy4gVGhlIHBhY2tlcidzIG93biBkaXJlY3RpdmVzICgtLW5vZGVzPTEgLS1leGNsdXNpdmUKIyAtLW5vLXJlcXVldWUgLS1leHBvcnQ9QUxMLEhPTUU9L2dsb2JhbC9ob21lcy9qL2pvc2VwaHJiKSBhbmQgc2VjdGlvbiA3J3MgYWNjb3VudCwgUU9TLCBjb25zdHJhaW50IGFuZCBsaW1pdCBhcmUgb24gdGhlCiMgc2JhdGNoIGNvbW1hbmQgbGluZSBpbiB0aGUgY29ubmVjdC4KIyAgIHNiYXRjaCAuLi4gcGZkX3AyX3dyYXBwZXIuc2ggPGRlcGxveT4gPHBpbj4gPHRhYmxlPiA8bGFuZXMgZGlyPiA8Zmlyc3Q+IDxsYXN0PiA8cHJvYmUgc2NyaXB0PgojIFRoZSBwcm9iZSBpcyBvbmUgc3J1biBzdGVwIHdpdGggdGhlIGxhbmVzJyBleGFjdCBzaGFwZSAoc3J1biAtLWV4YWN0IC1uMSAtYyAzMiAtLW1lbSA1NkcgLS1ncmVzPW5vbmUsIGFzIHRoZSBwYWNrZXIKIyBydW5zIGVhY2ggbGluZSB3aXRoIGdyZXMgIm5vbmUiKSwgYWZ0ZXIgdGhlIHNhbWUgc2V0dXBfc2FsbG9jX2Vudi5zaCBzb3VyY2UgYXMgczVjX2FycmF5LnNoLCB3cml0aW5nIG9ubHkgdG8KIyA8bGFuZXMgZGlyPi90aHJlYWRwcm9iZS08am9iPi5sb2cuIEEgcHJvYmUgZmFpbHVyZSBpcyByZWNvcmRlZCBhbmQgdGhlIGxpbmVzIHN0aWxsIHJ1bi4gVGhlbiB0aGUgcGFja2VyIHJ1bnMKIyBsaW5lcyA8Zmlyc3Q+Li48bGFzdD4gb2YgPHRhYmxlPiB3aXRoIDMyIENQVXMgYW5kIDU2RyBwZXIgbGluZSBhbmQgZ3JlcyAibm9uZSIuCnNldCAtbyBwaXBlZmFpbCAgICMgTk9UIHNldCAtdSAodGhlIHNldHVwIHNjcmlwdCByZWFkcyB1bnNldCB2YXJpYWJsZXMpCkQ9IiR7MTo/ZGVwbG95fSI7IFBJTj0iJHsyOj9waW59IjsgVEFCTEU9IiR7Mzo/dGFibGV9IjsgT1VUPSIkezQ6P2xhbmVzIGRpcn0iOyBGSVJTVD0iJHs1Oj9maXJzdH0iOyBMQVNUPSIkezY6P2xhc3R9IgpQUk9CRT0iJHs3Oj9wcm9iZSBzY3JpcHR9IgpzdGFtcCgpIHsgZGF0ZSAtdSArJUZUJVQuJTNOWjsgfQpta2RpciAtcCAiJHtPVVR9IgplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIGpvYj0ke1NMVVJNX0pPQl9JRH0gaG9zdD0kKGhvc3RuYW1lKSBkZXBsb3k9JHtEfSBwaW49JHtQSU59IHRhYmxlPSR7VEFCTEV9IGxpbmVzPSR7RklSU1R9Li4ke0xBU1R9IgplY2hvICJbcGZkLXdyYXBwZXJdIHN1Ym1pdHRpbmctc2hlbGwgdGhyZWFkIHZhcmlhYmxlczogT01QX05VTV9USFJFQURTPSR7T01QX05VTV9USFJFQURTLTx1bnNldD59IE9QRU5CTEFTX05VTV9USFJFQURTPSR7T1BFTkJMQVNfTlVNX1RIUkVBRFMtPHVuc2V0Pn0gTUtMX05VTV9USFJFQURTPSR7TUtMX05VTV9USFJFQURTLTx1bnNldD59IE5VTUVYUFJfTlVNX1RIUkVBRFM9JHtOVU1FWFBSX05VTV9USFJFQURTLTx1bnNldD59IgpzcnVuIC0tZXhhY3QgLW4xIC1jIDMyIC0tbWVtPTU2RyAtLWdyZXM9bm9uZSAtLWpvYi1uYW1lPXRocmVhZHByb2JlIFwKICBiYXNoIC1jICdzb3VyY2UgIiQxL3NldHVwX3NhbGxvY19lbnYuc2giID4gL2Rldi9udWxsIDI+JjE7IGNkICIkMSIgfHwgZXhpdCAyOyBweXRob24zICIkMiInIHRocmVhZHByb2JlICIke0R9IiAiJHtQUk9CRX0iIFwKICA+ICIke09VVCUvfS90aHJlYWRwcm9iZS0ke1NMVVJNX0pPQl9JRH0ubG9nIiAyPiYxCnByYz0kPwplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIHByb2JlIHJjPSR7cHJjfSQoIFsgIiR7cHJjfSIgLWVxIDAgXSB8fCBlY2hvICcgKHJlY29yZGVkOyB0aGUgbGluZXMgc3RpbGwgcnVuOyB0aGUgaW4tbGFuZSByZWNvcmQgbWF5IGJlIG1pc3NpbmcpJykiCmJhc2ggIiR7RH0vZG9jcy9vcmNoZXN0cmF0aW9uL3N0YXRlL2dwdS10aW1pbmctMjAyNjEwMjMvdG9vbHMvc2JhdGNoX3RpbWluZ19wYWNrZWQuc2giIFwKICAiJHtEfSIgIiR7UElOfSIgIiR7VEFCTEV9IiAiJHtPVVR9IiAzMiA1NkcgIiR7RklSU1R9IiAiJHtMQVNUfSIgbm9uZQpyYz0kPwplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIHBhY2tlciByYz0ke3JjfSIKZXhpdCAke3JjfQo=' | base64 -d > "$W/p3/tools/pfd_p2_wrapper.sh"
printf '%s' 'IiIiMUIgcHJlLWNoZWNrIFBhcnQgMSwgaW4tbGFuZSB0aHJlYWQgcHJvYmUgKHRoZSBkaXJlY3RvcidzIGNob2ljZSAoaSkgZm9yIFAyIGFuZCBQMykuCgpSdW4gYXMgb25lIHNydW4gc3RlcCB3aXRoIHRoZSBsYW5lcycgZXhhY3Qgc2hhcGUsIGFmdGVyIHRoZSBzYW1lIHNldHVwX3NhbGxvY19lbnYuc2ggc291cmNlIGFzIHM1Y19hcnJheS5zaC4gSXQgcmVhZHMKbm8gYW5hbHlzaXMgaW5wdXQsIGltcG9ydHMgb25seSBudW1weSwgbGlnaHRnYm0gYW5kIHRocmVhZHBvb2xjdGwsIGFuZCBwcmludHMgb25lIEpTT04gb2JqZWN0IHRvIHN0ZG91dDsgdGhlIHdyYXBwZXIKcmVkaXJlY3RzIHN0ZG91dCBpbnRvIHRoZSBqb2IncyBvdXRwdXQgZGlyZWN0b3J5LiBJdHMgZmllbGRzIGFyZSB0aGUgb25lcyBQMydzIHByb2JlIG11c3QgcmVwcm9kdWNlOiB0aGUgZm91ciB0aHJlYWQKdmFyaWFibGVzLCBTTFVSTV9DUFVTX1BFUl9UQVNLLCB0aGUgYWZmaW5pdHkgc2l6ZSBhbmQgdGhyZWFkcG9vbF9pbmZvIGFmdGVyIGltcG9ydGluZyBudW1weSBhbmQgbGlnaHRnYm0uCiIiIgppbXBvcnQganNvbgppbXBvcnQgb3MKaW1wb3J0IHN5cwoKcmVjb3JkID0gewogICAgInRocmVhZF92YXJpYWJsZXMiOiB7azogb3MuZW52aXJvbi5nZXQoaywgIjx1bnNldD4iKQogICAgICAgICAgICAgICAgICAgICAgICAgZm9yIGsgaW4gKCJPTVBfTlVNX1RIUkVBRFMiLCAiT1BFTkJMQVNfTlVNX1RIUkVBRFMiLCAiTUtMX05VTV9USFJFQURTIiwgIk5VTUVYUFJfTlVNX1RIUkVBRFMiKX0sCiAgICAiU0xVUk1fQ1BVU19QRVJfVEFTSyI6IG9zLmVudmlyb24uZ2V0KCJTTFVSTV9DUFVTX1BFUl9UQVNLIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9KT0JfSUQiOiBvcy5lbnZpcm9uLmdldCgiU0xVUk1fSk9CX0lEIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9TVEVQX0lEIjogb3MuZW52aXJvbi5nZXQoIlNMVVJNX1NURVBfSUQiLCAiPHVuc2V0PiIpLAogICAgImFmZmluaXR5X3NpemUiOiBsZW4ob3Muc2NoZWRfZ2V0YWZmaW5pdHkoMCkpIGlmIGhhc2F0dHIob3MsICJzY2hlZF9nZXRhZmZpbml0eSIpIGVsc2UgIjx1bmF2YWlsYWJsZT4iLAogICAgIm9zX2NwdV9jb3VudCI6IG9zLmNwdV9jb3VudCgpLAogICAgInB5dGhvbiI6IHN5cy52ZXJzaW9uLnNwbGl0KClbMF0sCiAgICAiZXhlY3V0YWJsZSI6IHN5cy5leGVjdXRhYmxlLAp9CnRyeToKICAgIGltcG9ydCBudW1weSBhcyBucAogICAgaW1wb3J0IGxpZ2h0Z2JtIGFzIGxnYgogICAgaW1wb3J0IHRocmVhZHBvb2xjdGwKICAgIHJlY29yZFsibnVtcHkiXSA9IG5wLl9fdmVyc2lvbl9fCiAgICByZWNvcmRbImxpZ2h0Z2JtIl0gPSBsZ2IuX192ZXJzaW9uX18KICAgIHJlY29yZFsidGhyZWFkcG9vbGN0bCJdID0gdGhyZWFkcG9vbGN0bC5fX3ZlcnNpb25fXwogICAgaW5mbyA9IHRocmVhZHBvb2xjdGwudGhyZWFkcG9vbF9pbmZvKCkKICAgIHJlY29yZFsidGhyZWFkcG9vbF9pbmZvIl0gPSBbe2s6IGkuZ2V0KGspIGZvciBrIGluICgidXNlcl9hcGkiLCAiaW50ZXJuYWxfYXBpIiwgInByZWZpeCIsICJ2ZXJzaW9uIiwgIm51bV90aHJlYWRzIiwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgImZpbGVwYXRoIil9IGZvciBpIGluIGluZm9dCiAgICBvbXAgPSBbaS5nZXQoIm51bV90aHJlYWRzIikgZm9yIGkgaW4gaW5mbyBpZiBpLmdldCgidXNlcl9hcGkiKSA9PSAib3Blbm1wIl0KICAgIHJlY29yZFsib3Blbm1wX2RlZmF1bHRfbnVtX3RocmVhZHMiXSA9IG9tcCBpZiBvbXAgZWxzZSAiPG5vIG9wZW5tcCBwb29sIGxvYWRlZD4iCiAgICByZWNvcmRbInN0YXR1cyJdID0gIm9rIgpleGNlcHQgRXhjZXB0aW9uIGFzIGU6ICAjIHJlY29yZGVkLCBub3QgcmFpc2VkOiBhIHByb2JlIGZhaWx1cmUgZG9lcyBub3Qgc3RvcCB0aGUgbGFuZXMKICAgIHJlY29yZFsic3RhdHVzIl0gPSBmImZhaWxlZDoge3R5cGUoZSkuX19uYW1lX199OiB7ZX0iCnByaW50KGpzb24uZHVtcHMocmVjb3JkLCBpbmRlbnQ9MSwgc29ydF9rZXlzPVRydWUpKQo=' | base64 -d > "$W/p3/tools/pfd_threadprobe.py"
printf '%s' 'IiIiQmFuZCBkaWFnbm9zaXMsIFAzJ3MgdGFzayB0YWJsZSAoRkQtMUItQkFORC1ESUFHTk9TSVMtREVDTEFSQVRJT04ubWQgc2VjdGlvbiA3OyBCSU5ESU5HLTEgcnVsaW5nIDIgYXMgYWRkZW5kdW0gQTIKc2V0cyBpdDogNCBqb2JzIHggNyBsYW5lcyB4IDQgaXRlbXMsIC0tdGltZT0wMTo0MDowMCkuCgoyOCBsaW5lcywgZWFjaCBvbmUgZmRfMWJfYmFuZF9kaWFnLnB5IHVuZm9sZCBjYWxsIG92ZXIgZXhhY3RseSA0IGl0ZW1zIHRoYXQgc2hhcmUgb25lIChtb2RlLCBzZWVkLCBlcHMsIGNoYW5uZWwpIGdyb3VwOgp0aGUgMTIgZ3JvdXBzIG9mIDggZGV0ZWN0b3IgdW5pdmVyc2VzIChFIGFuZCBCIGF0IHNlZWRzIDQ1LCA0OCwgNTEsIDU0LCBhbmQgYXQgZXBzIDEvMiBhbmQgMikgc3BsaXQgNCArIDQsIGFuZCB0aGUgNApncm91cHMgb2YgNCBHRUFOVF9OZXV0cm9uL0dFQU5UX1Byb3RvbiB1bml2ZXJzZXMgKEUgYW5kIEIsIGNoYW5uZWxzIHNpZ25hbCBhbmQgYmFja2dyb3VuZCkgd2hvbGUuIEpvYiBqICgwLTMpIHJ1bnMgbGluZXMKN2ogLi4gN2orNi4gVGhlIG1vZHVsZSdzIG93biBidWxrX2l0ZW1zKCksIGltcG9ydGVkIGZyb20gdGhlIGRlcGxveSBjaGVja291dCwgbXVzdCBlcXVhbCB0aGUgaXRlbXMgdGhlIDI4IGxpbmVzIGNhcnJ5LAplYWNoIGxpbmUgbXVzdCBiZSBvbmUgZ3JvdXAgb2YgZXhhY3RseSA0IGRpc3RpbmN0IHVuaXZlcnNlcywgbm8gaXRlbSBtYXkgcmVwZWF0LCBhbmQgbm8gcGlsb3QgaXRlbSBtYXkgYXBwZWFyOyBhbnkKZGlmZmVyZW5jZSByZWZ1c2VzLgoKdXNhZ2U6IHB5dGhvbjMgbWFrZV9iZGdfcDNfdGFibGUucHkgPGRlcGxveSBjaGVja291dD4gPFc+IDxvdXQgdGFibGU+CiIiIgppbXBvcnQgc3lzCmZyb20gY29sbGVjdGlvbnMgaW1wb3J0IE9yZGVyZWREaWN0CmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKUCA9ICIvcHNjcmF0Y2gvc2Qvai9qb3NlcGhyYiIKUElOU19TSEEgPSAiNWFkY2Q1NzZlYjQ2ZjQ0M2ZlNDEzM2IwNTA0NGNkMzE1YzBlZWIwZjI4MWUyMWFjZWU1ZjIzMThiNGJhYjI0OCIKRVBTX0FSRyA9IHswLjU6ICIwLjUiLCAxLjA6ICIxIiwgMi4wOiAiMiJ9CgoKZGVmIG1haW4oKSAtPiBpbnQ6CiAgICBkZXBsb3ksIFcsIG91dCA9IFBhdGgoc3lzLmFyZ3ZbMV0pLCBzeXMuYXJndlsyXSwgUGF0aChzeXMuYXJndlszXSkKICAgIHN5cy5wYXRoLmluc2VydCgwLCBzdHIoZGVwbG95IC8gIm5kLXVuZm9sZGluZyIpKQogICAgaW1wb3J0IGZkXzFiX2JhbmRfZGlhZyBhcyBkICAjIG5vcWE6IEU0MDIgICh0aGUgZGVwbG95J3MgYnl0ZXM7IHRoZSBjb25uZWN0IGdhdGVzIHRoZWlyIHNoYTI1NikKICAgIGJ1bGsgPSBkLmJ1bGtfaXRlbXMoKQogICAgZ3JvdXBzID0gT3JkZXJlZERpY3QoKQogICAgZm9yIG0sIHUsIHMsIGUsIGMgaW4gYnVsazoKICAgICAgICBncm91cHMuc2V0ZGVmYXVsdCgobSwgcywgZSwgYyksIFtdKS5hcHBlbmQodSkKICAgIGxpbmVzX2l0ZW1zID0gW10KICAgIGZvciBrZXksIHVzIGluIGdyb3Vwcy5pdGVtcygpOgogICAgICAgIGlmIGxlbih1cykgPT0gODoKICAgICAgICAgICAgbGluZXNfaXRlbXMgKz0gWyhrZXksIHVzWzo0XSksIChrZXksIHVzWzQ6XSldCiAgICAgICAgZWxpZiBsZW4odXMpID09IDQ6CiAgICAgICAgICAgIGxpbmVzX2l0ZW1zLmFwcGVuZCgoa2V5LCB1cykpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgcmFpc2UgU3lzdGVtRXhpdChmIlRBQkxFOiBncm91cCB7a2V5fSBoYXMge2xlbih1cyl9IHVuaXZlcnNlcywgbm90IDQgb3IgOCIpCiAgICBjYXJyaWVkID0gWyhtLCB1LCBzLCBlLCBjKSBmb3IgKG0sIHMsIGUsIGMpLCB1cyBpbiBsaW5lc19pdGVtcyBmb3IgdSBpbiB1c10KICAgIGlmIGxlbihsaW5lc19pdGVtcykgIT0gMjggb3IgYW55KGxlbih1cykgIT0gNCBvciBsZW4oc2V0KHVzKSkgIT0gNCBmb3IgXywgdXMgaW4gbGluZXNfaXRlbXMpOgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiBub3QgMjggbGluZXMgb2YgZXhhY3RseSA0IGRpc3RpbmN0IHVuaXZlcnNlcyIpCiAgICBpZiBsZW4oY2FycmllZCkgIT0gMTEyIG9yIGxlbihzZXQoY2FycmllZCkpICE9IDExMiBvciBzb3J0ZWQoY2FycmllZCkgIT0gc29ydGVkKGJ1bGspOgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiB0aGUgbGluZXMgZG8gbm90IGNhcnJ5IGV4YWN0bHkgYnVsa19pdGVtcygpIikKICAgIGlmIHNldChjYXJyaWVkKSAmIHNldChkLnBpbG90X2l0ZW1zKCkpOgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiBhIHBpbG90IGl0ZW0gaXMgb24gYSBQMyBsaW5lIikKICAgIGxlZ2FsID0gc2V0KGQuaXRlbXMoKSkKICAgIGlmIG5vdCBzZXQoY2FycmllZCkgPD0gbGVnYWw6CiAgICAgICAgcmFpc2UgU3lzdGVtRXhpdCgiVEFCTEU6IGFuIGl0ZW0gb3V0c2lkZSBzZWN0aW9uIDciKQogICAgaW5wdXRzID0gWyItLW5weiIsIGYie1B9L01JTkVSdkEtT21uaUZvbGQvbmQtdW5mb2xkaW5nL29mX2lucHV0c181ZC5ucHoiLAogICAgICAgICAgICAgICItLWJrZyIsIGYie1B9L3M1Yy0yMDI2MDkyNC9ydW5zL3AyL2JrZ19kdW1wLm5weiIsCiAgICAgICAgICAgICAgIi0tYmFuayIsIGYie1B9L01JTkVSdkEtT21uaUZvbGQvbmQtdW5mb2xkaW5nL2Jhbmtfc3dlZXBfNWRfYmtnYXdhcmUiLAogICAgICAgICAgICAgICItLWRldGVjdG9yLWRpciIsIGYie1B9L3M1cC0yMDI2MDkyNi9iYW5rX2RldGVjdG9yIiwKICAgICAgICAgICAgICAiLS1waW5zIiwgZiJ7UH0vZmQtMWItMjAyNjEwMzAvcGlucy5qc29uIiwgIi0tZXhwZWN0LXBpbnMtc2hhMjU2IiwgUElOU19TSEFdCiAgICBsaW5lcyA9IFsiIyBiYW5kIGRpYWdub3NpcywgUDMgKEZELTFCLUJBTkQtRElBR05PU0lTLURFQ0xBUkFUSU9OLm1kIHNlY3Rpb24gNzsgQklORElORy0xIHJ1bGluZyAyIGFzIGFkZGVuZHVtIEEyKTogIgogICAgICAgICAgICAgIjI4IGxpbmVzOyBqb2IgaiBydW5zIGxpbmVzIDdqLi43ais2Il0KICAgIGZvciBpLCAoKG0sIHMsIGUsIGMpLCB1cykgaW4gZW51bWVyYXRlKGxpbmVzX2l0ZW1zKToKICAgICAgICBsaW5lcy5hcHBlbmQoIlx0Ii5qb2luKFtmImZkMWJfYmRnX3AzX3tpOjAyZH1fe219IiwgImZkXzFiX2JhbmRfZGlhZy5weSIsICJ1bmZvbGQiLCAiLS1tb2RlIiwgbSwgIi0tc2VlZCIsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgc3RyKHMpLCAiLS1lcHMiLCBFUFNfQVJHW2VdLCAiLS1jaGFubmVsIiwgYywgIi0tdW5pdmVyc2VzIiwgIiwiLmpvaW4odXMpXQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKyBpbnB1dHMgKyBbIi0tdGhyZWFkcyIsICIzMiIsICItLW91dCIsIGYie1d9L3VuZiJdKSkKICAgIG91dC53cml0ZV90ZXh0KCJcbiIuam9pbihsaW5lcykgKyAiXG4iKQogICAgZm9yIGogaW4gcmFuZ2UoNCk6CiAgICAgICAgcHJpbnQoZiJUQUJMRTogam9iIHtqfTogbGluZXMgezcgKiBqfS4uezcgKiBqICsgNn06ICIKICAgICAgICAgICAgICArICI7ICIuam9pbihmInttfSBze3N9IGV7RVBTX0FSR1tlXX0ge2N9IHsnLCcuam9pbih1cyl9IiBmb3IgKG0sIHMsIGUsIGMpLCB1cyBpbiBsaW5lc19pdGVtc1s3ICogajo3ICogaiArIDddKSkKICAgIHByaW50KGYiVEFCTEU6IDI4IGxpbmVzLCAxMTIgaXRlbXMgPSBidWxrX2l0ZW1zKCk7IGVhY2ggbGluZSBvbmUgZ3JvdXAgb2YgNCIpCiAgICByZXR1cm4gMAoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBzeXMuZXhpdChtYWluKCkpCg==' | base64 -d > "$W/p3/tools/make_bdg_p3_table.py"
for pair in "pfd_p2_wrapper.sh:$WRAPPER_SHA" "pfd_threadprobe.py:$PROBE_SHA" "make_bdg_p3_table.py:$GEN_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/p3/tools/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 6. the task table $(ts)"
env -u PYTHONPATH "$PY" -B "$W/p3/tools/make_bdg_p3_table.py" "$W/deploy" "$W" "$W/p3/tables/tasks-p3.tsv" || { echo "STOP: the table generator refused"; finish 5; }
echo "tasks-p3.tsv sha256 $(sha256sum "$W/p3/tables/tasks-p3.tsv" | cut -d' ' -f1)"
cat "$W/p3/tables/tasks-p3.tsv"
n=$(grep -v '^#' "$W/p3/tables/tasks-p3.tsv" | grep -c -v '^[[:space:]]*$'); echo "lines $n"
[ "$n" -eq 28 ] || { echo "STOP: the table is not 28 lines"; finish 5; }
echo "== 7. section 5's control: the 73 sources against P1's stat-before.txt $(ts)"
restat "$W/p3/logs/stat-submit.txt"
echo "stat-submit.txt: $(wc -l < "$W/p3/logs/stat-submit.txt") lines; sha256 $(sha256sum "$W/p3/logs/stat-submit.txt" | cut -d' ' -f1)"
if cmp -s "$W/stat-before.txt" "$W/p3/logs/stat-submit.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved; nothing submitted:"; diff "$W/stat-before.txt" "$W/p3/logs/stat-submit.txt" | head -40; finish 4; fi
echo "thread variables in the submitting shell: OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 8. fence, immediately before submission $(ts)"
fence || { echo "STOP: the fence is not clear; nothing submitted"; finish 3; }
echo "FENCE: clear"
jobs=()
for j in 0 1 2 3; do
  first=$((7 * j)); last=$((7 * j + 6))
  echo "sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb --time=01:40:00 -J fd1b_bdg_p3 -o $W/p3/logs/%x_%j.out $W/p3/tools/pfd_p2_wrapper.sh $W/deploy $M $W/p3/tables/tasks-p3.tsv $W/p3/lanes $first $last $W/p3/tools/pfd_threadprobe.py" > "$W/p3/logs/submit-p3-$j.txt"
  cat "$W/p3/logs/submit-p3-$j.txt"
  sub=$(bash "$W/p3/logs/submit-p3-$j.txt" 2>&1); src=$?
  echo "$sub" | tee "$W/p3/logs/submit-p3-$j.out"; echo "sbatch $j rc=$src $(ts)"
  job=$(printf '%s\n' "$sub" | awk '/^Submitted batch job/ {print $4}')
  [ "$src" -eq 0 ] && [ -n "$job" ] || { echo "STOP: sbatch $j failed; cancelling ${jobs[*]}"; [ ${#jobs[@]} -gt 0 ] && scancel "${jobs[@]}"; finish 6; }
  jobs+=("$job")
  tl=$(scontrol show job "$job" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
  echo "job $job (lines $first..$last) TimeLimit=$tl"
  if [ "$tl" != "01:40:00" ]; then echo "STOP: TimeLimit is not 01:40:00; scancel ${jobs[*]}"; scancel "${jobs[@]}"; echo "scancel rc=$?"; finish 7; fi
done
printf '%s\n' "${jobs[@]}" > "$W/p3/logs/jobs.txt"
squeue -u josephrb -h -o '%i %j %T %l %D %R'
finish 0
