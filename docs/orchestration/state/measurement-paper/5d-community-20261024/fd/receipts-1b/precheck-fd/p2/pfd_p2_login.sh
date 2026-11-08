#!/bin/bash
# 1B pre-check Part 1, P2: the pilot (FD-1B-PRECHECK-FD-DECLARATION.md section 7; Binding 1, addendum A1; the director's
# route (a) with choice (i)). Login node, from a fresh deploy clone at M_A1 on pscratch. In order:
#   1. iris is read first: the m3246 row; the 18.5 node-h cap must not exceed half the remaining balance (project and
#      user), else STOP to the director;
#   2. the COV2D fence (rs1_* and ens1_* allowed, anything else refuses) and no fd1b* job queued;
#   3. a fresh clone at M_A1 into $V/deploy, HEAD equal and porcelain 0; the packer, s5c_array.sh, the module and
#      setup_salloc_env.sh gated on their sha256 (and the setup script on its blob id b4a9c3f6);
#   4. the wrapper, the probe and the table generator written from this script and gated on their sha256;
#   5. the table generated (8 lines, exactly section 7's pilot items), printed with its sha256, and checked again here;
#   6. stat only of the in-place inputs (npz, bkg, pins, the bank's cv.npz) and of the staged flux copy;
#   7. the thread variables in the submitting shell (none set; the job inherits them through --export=ALL);
#   8. the fence again, immediately before submission; then one sbatch of the wrapper: 1 node,
#      -A m3246 -q regular -C cpu --exclusive --no-requeue --time=01:00:00; its parsed TimeLimit must read 01:00:00,
#      else scancel. 1.0 node-h reserved against the 18.5 cap.
# Nothing is deleted. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=8d7a40c23b3b6b70c2913ba363a10a22e152aee4
P=/pscratch/sd/j/josephrb
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
PACKER_SHA=b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3
S5C_SHA=dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f
MOD_SHA=a7fbbb5850733b248c89c3f4e9527c40b8531228b88241ab2d3f2063c0863d2d
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
SETUP_BLOB=b4a9c3f6bb766d8488cbab98878cbac1262cc1bb
WRAPPER_SHA=038a6353b81a066476f96312e9764feac714bdc3cc350b5e533fd2a40f6e0256
PROBE_SHA=d93697123b1e3c5a467efde2488dff8422c684061b39f58fa8cc82c545e6190f
GEN_SHA=43f35c8e3af24184a5af028420a36a371e0225408853b043cdb77787d6af1692
CAP=18.5
finish() { echo "== pfd-p2 rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
fence() {
  local out frc bad
  out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
  echo "squeue rc=$frc; rows:"; printf '%s\n' "$out"; echo "-- end rows"
  bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
  echo "refusing rows: [$bad]"
  [ "$frc" -eq 0 ] && [ -z "$bad" ]
}
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -d "$V/stage" ] && [ -d "$V/unf" ] && [ -z "$(ls -A "$V/unf")" ] || { echo "STOP: $V/stage or an empty $V/unf missing"; finish 9; }
[ ! -e "$V/deploy" ] && [ ! -e "$V/p2" ] || { echo "STOP: $V/deploy or $V/p2 already exists"; finish 9; }
echo "== 1. iris (read first)"
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
echo "== 2. fence (before anything is written)"
fence || { echo "STOP: the fence is not clear"; finish 3; }
[ "$(squeue -u josephrb -h -o %j | grep -c '^fd1b')" = 0 ] || { echo "STOP: an fd1b job is queued"; finish 3; }
echo "FENCE: clear"
echo "== 3. fresh deploy clone at M_A1"
mkdir -p "$V/p2/tables" "$V/p2/lanes" "$V/p2/logs" "$V/p2/tools" || finish 9
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold.git "$V/deploy" || { echo "STOP: clone failed"; finish 5; }
git -C "$V/deploy" -c advice.detachedHead=false checkout --quiet --detach "$M" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C "$V/deploy" rev-parse HEAD); porc=$(git -C "$V/deploy" status --porcelain | wc -l)
echo "deploy HEAD $head; porcelain lines $porc"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M_A1 clean"; finish 5; }
for pair in "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh:$PACKER_SHA" \
            "nd-unfolding/s5c_array.sh:$S5C_SHA" "nd-unfolding/fd_1b_precheck_fd.py:$MOD_SHA" "setup_salloc_env.sh:$SETUP_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$V/deploy/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
blob=$(git -C "$V/deploy" rev-parse "$M:setup_salloc_env.sh"); echo "setup_salloc_env.sh blob $blob (bound $SETUP_BLOB)"
[ "$blob" = "$SETUP_BLOB" ] || { echo "STOP: the setup blob"; finish 5; }
echo "== 4. the wrapper, the probe and the table generator"
printf '%s' 'IyEvYmluL2Jhc2gKIyAxQiBwcmUtY2hlY2sgUGFydCAxLCB0aGUgUDIvUDMgam9iIHNjcmlwdCAodGhlIGRpcmVjdG9yJ3MgY2hvaWNlIChpKSk6IG9uZSBpbi1sYW5lIHRocmVhZCBwcm9iZSBzdGVwLCB0aGVuIHRoZQojIGNvbW1pdHRlZCBwYWNrZXIgdW5jaGFuZ2VkLiBJdCBjYXJyaWVzIG5vICNTQkFUQ0ggZGlyZWN0aXZlcy4gVGhlIHBhY2tlcidzIG93biBkaXJlY3RpdmVzICgtLW5vZGVzPTEgLS1leGNsdXNpdmUKIyAtLW5vLXJlcXVldWUgLS1leHBvcnQ9QUxMLEhPTUU9L2dsb2JhbC9ob21lcy9qL2pvc2VwaHJiKSBhbmQgc2VjdGlvbiA3J3MgYWNjb3VudCwgUU9TLCBjb25zdHJhaW50IGFuZCBsaW1pdCBhcmUgb24gdGhlCiMgc2JhdGNoIGNvbW1hbmQgbGluZSBpbiB0aGUgY29ubmVjdC4KIyAgIHNiYXRjaCAuLi4gcGZkX3AyX3dyYXBwZXIuc2ggPGRlcGxveT4gPHBpbj4gPHRhYmxlPiA8bGFuZXMgZGlyPiA8Zmlyc3Q+IDxsYXN0PiA8cHJvYmUgc2NyaXB0PgojIFRoZSBwcm9iZSBpcyBvbmUgc3J1biBzdGVwIHdpdGggdGhlIGxhbmVzJyBleGFjdCBzaGFwZSAoc3J1biAtLWV4YWN0IC1uMSAtYyAzMiAtLW1lbSA1NkcgLS1ncmVzPW5vbmUsIGFzIHRoZSBwYWNrZXIKIyBydW5zIGVhY2ggbGluZSB3aXRoIGdyZXMgIm5vbmUiKSwgYWZ0ZXIgdGhlIHNhbWUgc2V0dXBfc2FsbG9jX2Vudi5zaCBzb3VyY2UgYXMgczVjX2FycmF5LnNoLCB3cml0aW5nIG9ubHkgdG8KIyA8bGFuZXMgZGlyPi90aHJlYWRwcm9iZS08am9iPi5sb2cuIEEgcHJvYmUgZmFpbHVyZSBpcyByZWNvcmRlZCBhbmQgdGhlIGxpbmVzIHN0aWxsIHJ1bi4gVGhlbiB0aGUgcGFja2VyIHJ1bnMKIyBsaW5lcyA8Zmlyc3Q+Li48bGFzdD4gb2YgPHRhYmxlPiB3aXRoIDMyIENQVXMgYW5kIDU2RyBwZXIgbGluZSBhbmQgZ3JlcyAibm9uZSIuCnNldCAtbyBwaXBlZmFpbCAgICMgTk9UIHNldCAtdSAodGhlIHNldHVwIHNjcmlwdCByZWFkcyB1bnNldCB2YXJpYWJsZXMpCkQ9IiR7MTo/ZGVwbG95fSI7IFBJTj0iJHsyOj9waW59IjsgVEFCTEU9IiR7Mzo/dGFibGV9IjsgT1VUPSIkezQ6P2xhbmVzIGRpcn0iOyBGSVJTVD0iJHs1Oj9maXJzdH0iOyBMQVNUPSIkezY6P2xhc3R9IgpQUk9CRT0iJHs3Oj9wcm9iZSBzY3JpcHR9IgpzdGFtcCgpIHsgZGF0ZSAtdSArJUZUJVQuJTNOWjsgfQpta2RpciAtcCAiJHtPVVR9IgplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIGpvYj0ke1NMVVJNX0pPQl9JRH0gaG9zdD0kKGhvc3RuYW1lKSBkZXBsb3k9JHtEfSBwaW49JHtQSU59IHRhYmxlPSR7VEFCTEV9IGxpbmVzPSR7RklSU1R9Li4ke0xBU1R9IgplY2hvICJbcGZkLXdyYXBwZXJdIHN1Ym1pdHRpbmctc2hlbGwgdGhyZWFkIHZhcmlhYmxlczogT01QX05VTV9USFJFQURTPSR7T01QX05VTV9USFJFQURTLTx1bnNldD59IE9QRU5CTEFTX05VTV9USFJFQURTPSR7T1BFTkJMQVNfTlVNX1RIUkVBRFMtPHVuc2V0Pn0gTUtMX05VTV9USFJFQURTPSR7TUtMX05VTV9USFJFQURTLTx1bnNldD59IE5VTUVYUFJfTlVNX1RIUkVBRFM9JHtOVU1FWFBSX05VTV9USFJFQURTLTx1bnNldD59IgpzcnVuIC0tZXhhY3QgLW4xIC1jIDMyIC0tbWVtPTU2RyAtLWdyZXM9bm9uZSAtLWpvYi1uYW1lPXRocmVhZHByb2JlIFwKICBiYXNoIC1jICdzb3VyY2UgIiQxL3NldHVwX3NhbGxvY19lbnYuc2giID4gL2Rldi9udWxsIDI+JjE7IGNkICIkMSIgfHwgZXhpdCAyOyBweXRob24zICIkMiInIHRocmVhZHByb2JlICIke0R9IiAiJHtQUk9CRX0iIFwKICA+ICIke09VVCUvfS90aHJlYWRwcm9iZS0ke1NMVVJNX0pPQl9JRH0ubG9nIiAyPiYxCnByYz0kPwplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIHByb2JlIHJjPSR7cHJjfSQoIFsgIiR7cHJjfSIgLWVxIDAgXSB8fCBlY2hvICcgKHJlY29yZGVkOyB0aGUgbGluZXMgc3RpbGwgcnVuOyB0aGUgaW4tbGFuZSByZWNvcmQgbWF5IGJlIG1pc3NpbmcpJykiCmJhc2ggIiR7RH0vZG9jcy9vcmNoZXN0cmF0aW9uL3N0YXRlL2dwdS10aW1pbmctMjAyNjEwMjMvdG9vbHMvc2JhdGNoX3RpbWluZ19wYWNrZWQuc2giIFwKICAiJHtEfSIgIiR7UElOfSIgIiR7VEFCTEV9IiAiJHtPVVR9IiAzMiA1NkcgIiR7RklSU1R9IiAiJHtMQVNUfSIgbm9uZQpyYz0kPwplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIHBhY2tlciByYz0ke3JjfSIKZXhpdCAke3JjfQo=' | base64 -d > "$V/p2/tools/pfd_p2_wrapper.sh"
printf '%s' 'IiIiMUIgcHJlLWNoZWNrIFBhcnQgMSwgaW4tbGFuZSB0aHJlYWQgcHJvYmUgKHRoZSBkaXJlY3RvcidzIGNob2ljZSAoaSkgZm9yIFAyIGFuZCBQMykuCgpSdW4gYXMgb25lIHNydW4gc3RlcCB3aXRoIHRoZSBsYW5lcycgZXhhY3Qgc2hhcGUsIGFmdGVyIHRoZSBzYW1lIHNldHVwX3NhbGxvY19lbnYuc2ggc291cmNlIGFzIHM1Y19hcnJheS5zaC4gSXQgcmVhZHMKbm8gYW5hbHlzaXMgaW5wdXQsIGltcG9ydHMgb25seSBudW1weSwgbGlnaHRnYm0gYW5kIHRocmVhZHBvb2xjdGwsIGFuZCBwcmludHMgb25lIEpTT04gb2JqZWN0IHRvIHN0ZG91dDsgdGhlIHdyYXBwZXIKcmVkaXJlY3RzIHN0ZG91dCBpbnRvIHRoZSBqb2IncyBvdXRwdXQgZGlyZWN0b3J5LiBJdHMgZmllbGRzIGFyZSB0aGUgb25lcyBQMydzIHByb2JlIG11c3QgcmVwcm9kdWNlOiB0aGUgZm91ciB0aHJlYWQKdmFyaWFibGVzLCBTTFVSTV9DUFVTX1BFUl9UQVNLLCB0aGUgYWZmaW5pdHkgc2l6ZSBhbmQgdGhyZWFkcG9vbF9pbmZvIGFmdGVyIGltcG9ydGluZyBudW1weSBhbmQgbGlnaHRnYm0uCiIiIgppbXBvcnQganNvbgppbXBvcnQgb3MKaW1wb3J0IHN5cwoKcmVjb3JkID0gewogICAgInRocmVhZF92YXJpYWJsZXMiOiB7azogb3MuZW52aXJvbi5nZXQoaywgIjx1bnNldD4iKQogICAgICAgICAgICAgICAgICAgICAgICAgZm9yIGsgaW4gKCJPTVBfTlVNX1RIUkVBRFMiLCAiT1BFTkJMQVNfTlVNX1RIUkVBRFMiLCAiTUtMX05VTV9USFJFQURTIiwgIk5VTUVYUFJfTlVNX1RIUkVBRFMiKX0sCiAgICAiU0xVUk1fQ1BVU19QRVJfVEFTSyI6IG9zLmVudmlyb24uZ2V0KCJTTFVSTV9DUFVTX1BFUl9UQVNLIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9KT0JfSUQiOiBvcy5lbnZpcm9uLmdldCgiU0xVUk1fSk9CX0lEIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9TVEVQX0lEIjogb3MuZW52aXJvbi5nZXQoIlNMVVJNX1NURVBfSUQiLCAiPHVuc2V0PiIpLAogICAgImFmZmluaXR5X3NpemUiOiBsZW4ob3Muc2NoZWRfZ2V0YWZmaW5pdHkoMCkpIGlmIGhhc2F0dHIob3MsICJzY2hlZF9nZXRhZmZpbml0eSIpIGVsc2UgIjx1bmF2YWlsYWJsZT4iLAogICAgIm9zX2NwdV9jb3VudCI6IG9zLmNwdV9jb3VudCgpLAogICAgInB5dGhvbiI6IHN5cy52ZXJzaW9uLnNwbGl0KClbMF0sCiAgICAiZXhlY3V0YWJsZSI6IHN5cy5leGVjdXRhYmxlLAp9CnRyeToKICAgIGltcG9ydCBudW1weSBhcyBucAogICAgaW1wb3J0IGxpZ2h0Z2JtIGFzIGxnYgogICAgaW1wb3J0IHRocmVhZHBvb2xjdGwKICAgIHJlY29yZFsibnVtcHkiXSA9IG5wLl9fdmVyc2lvbl9fCiAgICByZWNvcmRbImxpZ2h0Z2JtIl0gPSBsZ2IuX192ZXJzaW9uX18KICAgIHJlY29yZFsidGhyZWFkcG9vbGN0bCJdID0gdGhyZWFkcG9vbGN0bC5fX3ZlcnNpb25fXwogICAgaW5mbyA9IHRocmVhZHBvb2xjdGwudGhyZWFkcG9vbF9pbmZvKCkKICAgIHJlY29yZFsidGhyZWFkcG9vbF9pbmZvIl0gPSBbe2s6IGkuZ2V0KGspIGZvciBrIGluICgidXNlcl9hcGkiLCAiaW50ZXJuYWxfYXBpIiwgInByZWZpeCIsICJ2ZXJzaW9uIiwgIm51bV90aHJlYWRzIiwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgImZpbGVwYXRoIil9IGZvciBpIGluIGluZm9dCiAgICBvbXAgPSBbaS5nZXQoIm51bV90aHJlYWRzIikgZm9yIGkgaW4gaW5mbyBpZiBpLmdldCgidXNlcl9hcGkiKSA9PSAib3Blbm1wIl0KICAgIHJlY29yZFsib3Blbm1wX2RlZmF1bHRfbnVtX3RocmVhZHMiXSA9IG9tcCBpZiBvbXAgZWxzZSAiPG5vIG9wZW5tcCBwb29sIGxvYWRlZD4iCiAgICByZWNvcmRbInN0YXR1cyJdID0gIm9rIgpleGNlcHQgRXhjZXB0aW9uIGFzIGU6ICAjIHJlY29yZGVkLCBub3QgcmFpc2VkOiBhIHByb2JlIGZhaWx1cmUgZG9lcyBub3Qgc3RvcCB0aGUgbGFuZXMKICAgIHJlY29yZFsic3RhdHVzIl0gPSBmImZhaWxlZDoge3R5cGUoZSkuX19uYW1lX199OiB7ZX0iCnByaW50KGpzb24uZHVtcHMocmVjb3JkLCBpbmRlbnQ9MSwgc29ydF9rZXlzPVRydWUpKQo=' | base64 -d > "$V/p2/tools/pfd_threadprobe.py"
printf '%s' 'IiIiMUIgcHJlLWNoZWNrIFBhcnQgMSwgUDIncyB0YXNrIHRhYmxlIChGRC0xQi1QUkVDSEVDSy1GRC1ERUNMQVJBVElPTi5tZCBzZWN0aW9uIDc7IEJpbmRpbmcgMSwgYWRkZW5kdW0gQTEpLgoKRWlnaHQgbGluZXMsIG9uZSBwZXIgbGFuZSBvZiBvbmUgbm9kZSwgZXhhY3RseSBzZWN0aW9uIDcncyBwaWxvdCBpdGVtczoKICBBLCBCIGFuZCBEbm9tIGF0IENWOyBBLCBCIGFuZCBEbm9tIGF0IEZsdXhfMDsgQSBhbmQgQiBhdCBNaW5vc0VmZmljaWVuY3lfMC4KRWFjaCBsaW5lIGlzICI8bmFtZT48VEFCPmZkXzFiX3ByZWNoZWNrX2ZkLnB5PFRBQj51bmZvbGQgLS1tb2RlIE0gLS11bml2ZXJzZXMgVSA8dGhlIGJvdW5kIGlucHV0cz4iLCBydW4gYnkgdGhlCmNvbW1pdHRlZCBzNWNfYXJyYXkuc2guIFRoZSBtb2R1bGUncyBvd24gUElMT1QgdHVwbGUgaXMgcmVhZCBmcm9tIGl0cyBzb3VyY2Ugd2l0aCBhc3QgKG5vIGltcG9ydCkgYW5kIG11c3QgZXF1YWwKc2VjdGlvbiA3J3MgbGlzdDsgYW55IG90aGVyIGxpbmUgaXMgcmVmdXNlZC4KCnVzYWdlOiBweXRob24zIC1JIG1ha2VfcDJfdGFibGUucHkgPGRlcGxveSBjaGVja291dD4gPFY+IDxvdXQgdGFibGU+CiIiIgppbXBvcnQgYXN0CmltcG9ydCBzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgpTRUNUSU9ONyA9IFsoIkEiLCAiQ1YiKSwgKCJCIiwgIkNWIiksICgiRG5vbSIsICJDViIpLCAoIkEiLCAiRmx1eF8wIiksICgiQiIsICJGbHV4XzAiKSwgKCJEbm9tIiwgIkZsdXhfMCIpLAogICAgICAgICAgICAoIkEiLCAiTWlub3NFZmZpY2llbmN5XzAiKSwgKCJCIiwgIk1pbm9zRWZmaWNpZW5jeV8wIildClAgPSAiL3BzY3JhdGNoL3NkL2ovam9zZXBocmIiCgoKZGVmIG1vZHVsZV9waWxvdChtb2R1bGU6IFBhdGgpIC0+IGxpc3Q6CiAgICB0cmVlID0gYXN0LnBhcnNlKG1vZHVsZS5yZWFkX3RleHQoKSkKICAgIGZvciBub2RlIGluIHRyZWUuYm9keToKICAgICAgICBpZiBpc2luc3RhbmNlKG5vZGUsIGFzdC5Bc3NpZ24pIGFuZCBhbnkoZ2V0YXR0cih0LCAiaWQiLCBOb25lKSA9PSAiUElMT1QiIGZvciB0IGluIG5vZGUudGFyZ2V0cyk6CiAgICAgICAgICAgIHJldHVybiBbdHVwbGUoeCkgZm9yIHggaW4gYXN0LmxpdGVyYWxfZXZhbChub2RlLnZhbHVlKV0KICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiBubyBQSUxPVCBpbiB0aGUgbW9kdWxlIikKCgpkZWYgbWFpbigpIC0+IGludDoKICAgIGRlcGxveSwgViwgb3V0ID0gUGF0aChzeXMuYXJndlsxXSksIHN5cy5hcmd2WzJdLCBQYXRoKHN5cy5hcmd2WzNdKQogICAgcGlsb3QgPSBtb2R1bGVfcGlsb3QoZGVwbG95IC8gIm5kLXVuZm9sZGluZyIgLyAiZmRfMWJfcHJlY2hlY2tfZmQucHkiKQogICAgaWYgcGlsb3QgIT0gU0VDVElPTjc6CiAgICAgICAgcmFpc2UgU3lzdGVtRXhpdChmIlRBQkxFOiB0aGUgbW9kdWxlJ3MgUElMT1Qge3BpbG90fSBpcyBub3Qgc2VjdGlvbiA3J3MgbGlzdCIpCiAgICBjb21tb24gPSBbIi0tbnB6IiwgZiJ7UH0vTUlORVJ2QS1PbW5pRm9sZC9uZC11bmZvbGRpbmcvb2ZfaW5wdXRzXzVkLm5weiIsCiAgICAgICAgICAgICAgIi0tYmtnIiwgZiJ7UH0vczVjLTIwMjYwOTI0L3J1bnMvcDIvYmtnX2R1bXAubnB6IiwKICAgICAgICAgICAgICAiLS1iYW5rIiwgZiJ7UH0vTUlORVJ2QS1PbW5pRm9sZC9uZC11bmZvbGRpbmcvYmFua19zd2VlcF81ZF9ia2dhd2FyZSIsCiAgICAgICAgICAgICAgIi0tZGV0ZWN0b3ItZGlyIiwgZiJ7UH0vczVwLTIwMjYwOTI2L2JhbmtfZGV0ZWN0b3IiLAogICAgICAgICAgICAgICItLWZsdXgtZmlsZSIsIGYie1Z9L3N0YWdlL2ZsdXhfdW5pdmVyc2VzLnJvb3QiLAogICAgICAgICAgICAgICItLXBpbnMiLCBmIntQfS9mZC0xYi0yMDI2MTAzMC9waW5zLmpzb24iLAogICAgICAgICAgICAgICItLWV4cGVjdC1waW5zLXNoYTI1NiIsICI1YWRjZDU3NmViNDZmNDQzZmU0MTMzYjA1MDQ0Y2QzMTVjMGVlYjBmMjgxZTIxYWNlZTVmMjMxOGI0YmFiMjQ4IiwKICAgICAgICAgICAgICAiLS10aHJlYWRzIiwgIjMyIiwgIi0tb3V0IiwgZiJ7Vn0vdW5mIl0KICAgIGxpbmVzID0gWyIjIDFCIHByZS1jaGVjayBQYXJ0IDEsIFAyIChGRC0xQi1QUkVDSEVDSy1GRC1ERUNMQVJBVElPTi5tZCBzZWN0aW9uIDc7IEJpbmRpbmcgMSwgYWRkZW5kdW0gQTEpIl0KICAgIGZvciBtb2RlLCB1IGluIFNFQ1RJT043OgogICAgICAgIGxpbmVzLmFwcGVuZCgiXHQiLmpvaW4oW2YiZmQxYl9wZmRfcDJfe21vZGV9X3t1fSIsICJmZF8xYl9wcmVjaGVja19mZC5weSIsICJ1bmZvbGQiLCAiLS1tb2RlIiwgbW9kZSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAiLS11bml2ZXJzZXMiLCB1XSArIGNvbW1vbikpCiAgICBib2R5ID0gW2wgZm9yIGwgaW4gbGluZXMgaWYgbm90IGwuc3RhcnRzd2l0aCgiIyIpXQogICAgaWYgbGVuKGJvZHkpICE9IDggb3IgbGVuKHtsLnNwbGl0KCJcdCIpWzBdIGZvciBsIGluIGJvZHl9KSAhPSA4OgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiBub3QgZWlnaHQgZGlzdGluY3QgbGluZXMiKQogICAgb3V0LndyaXRlX3RleHQoIlxuIi5qb2luKGxpbmVzKSArICJcbiIpCiAgICBwcmludChmIlRBQkxFOiB7bGVuKGJvZHkpfSBsaW5lcyB3cml0dGVuIHRvIHtvdXR9IikKICAgIHJldHVybiAwCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9fIjoKICAgIHN5cy5leGl0KG1haW4oKSkK' | base64 -d > "$V/p2/tools/make_p2_table.py"
for pair in "pfd_p2_wrapper.sh:$WRAPPER_SHA" "pfd_threadprobe.py:$PROBE_SHA" "make_p2_table.py:$GEN_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$V/p2/tools/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 5. the task table"
env -u PYTHONPATH "$PY" -I "$V/p2/tools/make_p2_table.py" "$V/deploy" "$V" "$V/p2/tables/tasks-p2.tsv" || { echo "STOP: the table generator refused"; finish 5; }
echo "tasks-p2.tsv sha256 $(sha256sum "$V/p2/tables/tasks-p2.tsv" | cut -d' ' -f1)"
cat "$V/p2/tables/tasks-p2.tsv"
n=$(grep -v '^#' "$V/p2/tables/tasks-p2.tsv" | grep -c -v '^[[:space:]]*$')
items=$(grep -v '^#' "$V/p2/tables/tasks-p2.tsv" | awk -F'\t' '$2 == "fd_1b_precheck_fd.py" && $3 == "unfold" && $4 == "--mode" && $6 == "--universes" {print $5"_"$7}' | tr '\n' ' ')
echo "lines $n; items: $items"
[ "$n" -eq 8 ] && [ "$items" = "A_CV B_CV Dnom_CV A_Flux_0 B_Flux_0 Dnom_Flux_0 A_MinosEfficiency_0 B_MinosEfficiency_0 " ] || { echo "STOP: the table is not section 7's eight items"; finish 5; }
echo "== 6. stat only: in-place inputs and the staged flux copy"
for f in "$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$P/fd-1b-20261030/pins.json" \
         "$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz" "$V/stage/flux_universes.root"; do
  stat -c '%n|%s|%Y|%X' "$f" 2>&1
done | tee "$V/p2/logs/stat-before.txt"
echo "== 7. thread variables in the submitting shell (none set; inherited by the job through --export=ALL)"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 8. fence, immediately before submission"
fence || { echo "STOP: the fence is not clear; nothing submitted"; finish 3; }
[ "$(squeue -u josephrb -h -o %j | grep -c '^fd1b')" = 0 ] || { echo "STOP: an fd1b job is queued; nothing submitted"; finish 3; }
echo "FENCE: clear"
cat > "$V/p2/logs/submit-p2.txt" <<SUB
sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb --time=01:00:00 -J fd1b_pfd_p2 -o $V/p2/logs/%x_%j.out $V/p2/tools/pfd_p2_wrapper.sh $V/deploy $M $V/p2/tables/tasks-p2.tsv $V/p2/lanes 0 7 $V/p2/tools/pfd_threadprobe.py
SUB
cat "$V/p2/logs/submit-p2.txt"
sub=$(bash "$V/p2/logs/submit-p2.txt" 2>&1); src=$?
echo "$sub" | tee "$V/p2/logs/submit-p2.out"; echo "sbatch rc=$src"
job=$(printf '%s\n' "$sub" | awk '/^Submitted batch job/ {print $4}')
[ "$src" -eq 0 ] && [ -n "$job" ] || { echo "STOP: sbatch failed"; finish 6; }
tl=$(scontrol show job "$job" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
echo "job $job TimeLimit=$tl"
if [ "$tl" != "01:00:00" ]; then echo "STOP: TimeLimit is not 01:00:00; scancel $job"; scancel "$job"; echo "scancel rc=$?"; finish 7; fi
squeue -u josephrb -h -o '%i %j %T %l %D %R'
finish 0
