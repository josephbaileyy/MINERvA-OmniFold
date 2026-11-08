#!/bin/bash
# 1B pre-check Part 1, P3: the bulk (FD-1B-PRECHECK-FD-DECLARATION.md section 7; Binding 1, addendum A1; route (a)
# with choice (i), the same wrapper and probe as P2). Login node, from a fresh deploy clone at M_A1. In order:
#   1. iris first: the 18.5 node-h cap must not exceed half the remaining balance (project and user), else STOP;
#      Part 1's charge so far (P2, 0.2631 node-h) plus P3's 17.5 reserved must not exceed the cap;
#   2. the COV2D fence (rs1_* and ens1_* allowed) and no fd1b* job queued; $V/unf must hold exactly P2's 8 products;
#   3. a fresh clone at M_A1 into $V/deploy-p3, HEAD equal and porcelain 0; the packer, s5c_array.sh, the module and
#      setup_salloc_env.sh gated on their sha256 (setup also on its blob id);
#   4. the wrapper and the probe (P2's, unchanged) and P3's table generator written and gated on their sha256;
#   5. the table: 54 one-mode lanes, 319 items, at most 6 per lane, none of P2's 8; printed with its sha256 and
#      re-checked here;
#   6. stat only of the in-place inputs and the staged flux copy;
#   7. the submitting shell's thread variables (none set);
#   8. the fence again, then 7 sbatch submissions of the wrapper, one node each, lines 0-7, 8-15, ..., 48-53:
#      -A m3246 -q regular -C cpu --exclusive --no-requeue --time=02:30:00. Each parsed TimeLimit must read 02:30:00,
#      else every job submitted so far is cancelled and the connect STOPs. 17.5 node-h reserved.
# Nothing is deleted. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=8d7a40c23b3b6b70c2913ba363a10a22e152aee4
P=/pscratch/sd/j/josephrb
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
DD=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107/deploy-p3
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
PACKER_SHA=b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3
S5C_SHA=dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f
MOD_SHA=a7fbbb5850733b248c89c3f4e9527c40b8531228b88241ab2d3f2063c0863d2d
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
SETUP_BLOB=b4a9c3f6bb766d8488cbab98878cbac1262cc1bb
WRAPPER_SHA=038a6353b81a066476f96312e9764feac714bdc3cc350b5e533fd2a40f6e0256
PROBE_SHA=d93697123b1e3c5a467efde2488dff8422c684061b39f58fa8cc82c545e6190f
GEN_SHA=f066f1a09fefc87ef213a71bb692bc36fd7966537c4ada8fe3f5ff642e56c4a2
CAP=18.5
CHARGED=0.2631
RESERVE=17.5
finish() { echo "== pfd-p3 rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
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
[ ! -e "$DD" ] && [ ! -e "$V/p3" ] || { echo "STOP: $DD or $V/p3 already exists"; finish 9; }
want="fd1b_pfd_A_CV.npz fd1b_pfd_A_Flux_0.npz fd1b_pfd_A_MinosEfficiency_0.npz fd1b_pfd_B_CV.npz fd1b_pfd_B_Flux_0.npz fd1b_pfd_B_MinosEfficiency_0.npz fd1b_pfd_Dnom_CV.npz fd1b_pfd_Dnom_Flux_0.npz "
have=$(cd "$V/unf" && ls fd1b_pfd_*.npz 2>/dev/null | sort | tr '\n' ' ')
echo "products in $V/unf: $have"
[ "$have" = "$want" ] || { echo "STOP: $V/unf does not hold exactly P2's 8 products"; finish 9; }
echo "== 1. iris (read first)"
irisout=$(iris 2>&1); irc=$?
printf '%s\n' "$irisout" | head -3
row=$(printf '%s\n' "$irisout" | grep -E '^m3246 ' | head -1)
echo "iris rc=$irc; m3246 row: [$row]"
read -r _ uch ual pch pal <<< "$row"
verdict=$(awk -v uch="$uch" -v ual="$ual" -v pch="$pch" -v pal="$pal" -v cap="$CAP" -v ch="$CHARGED" -v rs="$RESERVE" 'BEGIN {
  if (ual == "" || pal == "" || ual+0 <= 0 || pal+0 <= 0) { print "UNREADABLE"; exit }
  ur = ual - uch; pr = pal - pch
  printf "user remaining %.1f, project remaining %.1f, cap %.1f; half user %.1f, half project %.1f; Part 1 charged %.4f + P3 reserved %.1f = %.4f -> %s\n",
    ur, pr, cap, ur/2, pr/2, ch, rs, ch + rs, (cap <= ur/2 && cap <= pr/2 && ch + rs <= cap) ? "OK" : "OVER" }')
echo "balance: $verdict"
case "$verdict" in *"-> OK") ;; *) echo "STOP: the cap or the reservation is over, or iris is unreadable"; finish 3 ;; esac
echo "== 2. fence (before anything is written)"
fence || { echo "STOP: the fence is not clear"; finish 3; }
[ "$(squeue -u josephrb -h -o %j | grep -c '^fd1b')" = 0 ] || { echo "STOP: an fd1b job is queued"; finish 3; }
echo "FENCE: clear"
echo "== 3. fresh deploy clone at M_A1"
mkdir -p "$V/p3/tables" "$V/p3/lanes" "$V/p3/logs" "$V/p3/tools" || finish 9
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold.git "$DD" || { echo "STOP: clone failed"; finish 5; }
git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C "$DD" rev-parse HEAD); porc=$(git -C "$DD" status --porcelain | wc -l)
echo "deploy HEAD $head; porcelain lines $porc"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M_A1 clean"; finish 5; }
for pair in "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh:$PACKER_SHA" \
            "nd-unfolding/s5c_array.sh:$S5C_SHA" "nd-unfolding/fd_1b_precheck_fd.py:$MOD_SHA" "setup_salloc_env.sh:$SETUP_SHA"; do
  f=${pair%%:*}; w=${pair##*:}; got=$(sha256sum "$DD/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $w) $f"
  [ "$got" = "$w" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
blob=$(git -C "$DD" rev-parse "$M:setup_salloc_env.sh"); echo "setup_salloc_env.sh blob $blob (bound $SETUP_BLOB)"
[ "$blob" = "$SETUP_BLOB" ] || { echo "STOP: the setup blob"; finish 5; }
echo "== 4. the wrapper and the probe (P2's) and P3's table generator"
printf '%s' 'IyEvYmluL2Jhc2gKIyAxQiBwcmUtY2hlY2sgUGFydCAxLCB0aGUgUDIvUDMgam9iIHNjcmlwdCAodGhlIGRpcmVjdG9yJ3MgY2hvaWNlIChpKSk6IG9uZSBpbi1sYW5lIHRocmVhZCBwcm9iZSBzdGVwLCB0aGVuIHRoZQojIGNvbW1pdHRlZCBwYWNrZXIgdW5jaGFuZ2VkLiBJdCBjYXJyaWVzIG5vICNTQkFUQ0ggZGlyZWN0aXZlcy4gVGhlIHBhY2tlcidzIG93biBkaXJlY3RpdmVzICgtLW5vZGVzPTEgLS1leGNsdXNpdmUKIyAtLW5vLXJlcXVldWUgLS1leHBvcnQ9QUxMLEhPTUU9L2dsb2JhbC9ob21lcy9qL2pvc2VwaHJiKSBhbmQgc2VjdGlvbiA3J3MgYWNjb3VudCwgUU9TLCBjb25zdHJhaW50IGFuZCBsaW1pdCBhcmUgb24gdGhlCiMgc2JhdGNoIGNvbW1hbmQgbGluZSBpbiB0aGUgY29ubmVjdC4KIyAgIHNiYXRjaCAuLi4gcGZkX3AyX3dyYXBwZXIuc2ggPGRlcGxveT4gPHBpbj4gPHRhYmxlPiA8bGFuZXMgZGlyPiA8Zmlyc3Q+IDxsYXN0PiA8cHJvYmUgc2NyaXB0PgojIFRoZSBwcm9iZSBpcyBvbmUgc3J1biBzdGVwIHdpdGggdGhlIGxhbmVzJyBleGFjdCBzaGFwZSAoc3J1biAtLWV4YWN0IC1uMSAtYyAzMiAtLW1lbSA1NkcgLS1ncmVzPW5vbmUsIGFzIHRoZSBwYWNrZXIKIyBydW5zIGVhY2ggbGluZSB3aXRoIGdyZXMgIm5vbmUiKSwgYWZ0ZXIgdGhlIHNhbWUgc2V0dXBfc2FsbG9jX2Vudi5zaCBzb3VyY2UgYXMgczVjX2FycmF5LnNoLCB3cml0aW5nIG9ubHkgdG8KIyA8bGFuZXMgZGlyPi90aHJlYWRwcm9iZS08am9iPi5sb2cuIEEgcHJvYmUgZmFpbHVyZSBpcyByZWNvcmRlZCBhbmQgdGhlIGxpbmVzIHN0aWxsIHJ1bi4gVGhlbiB0aGUgcGFja2VyIHJ1bnMKIyBsaW5lcyA8Zmlyc3Q+Li48bGFzdD4gb2YgPHRhYmxlPiB3aXRoIDMyIENQVXMgYW5kIDU2RyBwZXIgbGluZSBhbmQgZ3JlcyAibm9uZSIuCnNldCAtbyBwaXBlZmFpbCAgICMgTk9UIHNldCAtdSAodGhlIHNldHVwIHNjcmlwdCByZWFkcyB1bnNldCB2YXJpYWJsZXMpCkQ9IiR7MTo/ZGVwbG95fSI7IFBJTj0iJHsyOj9waW59IjsgVEFCTEU9IiR7Mzo/dGFibGV9IjsgT1VUPSIkezQ6P2xhbmVzIGRpcn0iOyBGSVJTVD0iJHs1Oj9maXJzdH0iOyBMQVNUPSIkezY6P2xhc3R9IgpQUk9CRT0iJHs3Oj9wcm9iZSBzY3JpcHR9IgpzdGFtcCgpIHsgZGF0ZSAtdSArJUZUJVQuJTNOWjsgfQpta2RpciAtcCAiJHtPVVR9IgplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIGpvYj0ke1NMVVJNX0pPQl9JRH0gaG9zdD0kKGhvc3RuYW1lKSBkZXBsb3k9JHtEfSBwaW49JHtQSU59IHRhYmxlPSR7VEFCTEV9IGxpbmVzPSR7RklSU1R9Li4ke0xBU1R9IgplY2hvICJbcGZkLXdyYXBwZXJdIHN1Ym1pdHRpbmctc2hlbGwgdGhyZWFkIHZhcmlhYmxlczogT01QX05VTV9USFJFQURTPSR7T01QX05VTV9USFJFQURTLTx1bnNldD59IE9QRU5CTEFTX05VTV9USFJFQURTPSR7T1BFTkJMQVNfTlVNX1RIUkVBRFMtPHVuc2V0Pn0gTUtMX05VTV9USFJFQURTPSR7TUtMX05VTV9USFJFQURTLTx1bnNldD59IE5VTUVYUFJfTlVNX1RIUkVBRFM9JHtOVU1FWFBSX05VTV9USFJFQURTLTx1bnNldD59IgpzcnVuIC0tZXhhY3QgLW4xIC1jIDMyIC0tbWVtPTU2RyAtLWdyZXM9bm9uZSAtLWpvYi1uYW1lPXRocmVhZHByb2JlIFwKICBiYXNoIC1jICdzb3VyY2UgIiQxL3NldHVwX3NhbGxvY19lbnYuc2giID4gL2Rldi9udWxsIDI+JjE7IGNkICIkMSIgfHwgZXhpdCAyOyBweXRob24zICIkMiInIHRocmVhZHByb2JlICIke0R9IiAiJHtQUk9CRX0iIFwKICA+ICIke09VVCUvfS90aHJlYWRwcm9iZS0ke1NMVVJNX0pPQl9JRH0ubG9nIiAyPiYxCnByYz0kPwplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIHByb2JlIHJjPSR7cHJjfSQoIFsgIiR7cHJjfSIgLWVxIDAgXSB8fCBlY2hvICcgKHJlY29yZGVkOyB0aGUgbGluZXMgc3RpbGwgcnVuOyB0aGUgaW4tbGFuZSByZWNvcmQgbWF5IGJlIG1pc3NpbmcpJykiCmJhc2ggIiR7RH0vZG9jcy9vcmNoZXN0cmF0aW9uL3N0YXRlL2dwdS10aW1pbmctMjAyNjEwMjMvdG9vbHMvc2JhdGNoX3RpbWluZ19wYWNrZWQuc2giIFwKICAiJHtEfSIgIiR7UElOfSIgIiR7VEFCTEV9IiAiJHtPVVR9IiAzMiA1NkcgIiR7RklSU1R9IiAiJHtMQVNUfSIgbm9uZQpyYz0kPwplY2hvICJbcGZkLXdyYXBwZXJdICQoc3RhbXApIHBhY2tlciByYz0ke3JjfSIKZXhpdCAke3JjfQo=' | base64 -d > "$V/p3/tools/pfd_p2_wrapper.sh"
printf '%s' 'IiIiMUIgcHJlLWNoZWNrIFBhcnQgMSwgaW4tbGFuZSB0aHJlYWQgcHJvYmUgKHRoZSBkaXJlY3RvcidzIGNob2ljZSAoaSkgZm9yIFAyIGFuZCBQMykuCgpSdW4gYXMgb25lIHNydW4gc3RlcCB3aXRoIHRoZSBsYW5lcycgZXhhY3Qgc2hhcGUsIGFmdGVyIHRoZSBzYW1lIHNldHVwX3NhbGxvY19lbnYuc2ggc291cmNlIGFzIHM1Y19hcnJheS5zaC4gSXQgcmVhZHMKbm8gYW5hbHlzaXMgaW5wdXQsIGltcG9ydHMgb25seSBudW1weSwgbGlnaHRnYm0gYW5kIHRocmVhZHBvb2xjdGwsIGFuZCBwcmludHMgb25lIEpTT04gb2JqZWN0IHRvIHN0ZG91dDsgdGhlIHdyYXBwZXIKcmVkaXJlY3RzIHN0ZG91dCBpbnRvIHRoZSBqb2IncyBvdXRwdXQgZGlyZWN0b3J5LiBJdHMgZmllbGRzIGFyZSB0aGUgb25lcyBQMydzIHByb2JlIG11c3QgcmVwcm9kdWNlOiB0aGUgZm91ciB0aHJlYWQKdmFyaWFibGVzLCBTTFVSTV9DUFVTX1BFUl9UQVNLLCB0aGUgYWZmaW5pdHkgc2l6ZSBhbmQgdGhyZWFkcG9vbF9pbmZvIGFmdGVyIGltcG9ydGluZyBudW1weSBhbmQgbGlnaHRnYm0uCiIiIgppbXBvcnQganNvbgppbXBvcnQgb3MKaW1wb3J0IHN5cwoKcmVjb3JkID0gewogICAgInRocmVhZF92YXJpYWJsZXMiOiB7azogb3MuZW52aXJvbi5nZXQoaywgIjx1bnNldD4iKQogICAgICAgICAgICAgICAgICAgICAgICAgZm9yIGsgaW4gKCJPTVBfTlVNX1RIUkVBRFMiLCAiT1BFTkJMQVNfTlVNX1RIUkVBRFMiLCAiTUtMX05VTV9USFJFQURTIiwgIk5VTUVYUFJfTlVNX1RIUkVBRFMiKX0sCiAgICAiU0xVUk1fQ1BVU19QRVJfVEFTSyI6IG9zLmVudmlyb24uZ2V0KCJTTFVSTV9DUFVTX1BFUl9UQVNLIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9KT0JfSUQiOiBvcy5lbnZpcm9uLmdldCgiU0xVUk1fSk9CX0lEIiwgIjx1bnNldD4iKSwKICAgICJTTFVSTV9TVEVQX0lEIjogb3MuZW52aXJvbi5nZXQoIlNMVVJNX1NURVBfSUQiLCAiPHVuc2V0PiIpLAogICAgImFmZmluaXR5X3NpemUiOiBsZW4ob3Muc2NoZWRfZ2V0YWZmaW5pdHkoMCkpIGlmIGhhc2F0dHIob3MsICJzY2hlZF9nZXRhZmZpbml0eSIpIGVsc2UgIjx1bmF2YWlsYWJsZT4iLAogICAgIm9zX2NwdV9jb3VudCI6IG9zLmNwdV9jb3VudCgpLAogICAgInB5dGhvbiI6IHN5cy52ZXJzaW9uLnNwbGl0KClbMF0sCiAgICAiZXhlY3V0YWJsZSI6IHN5cy5leGVjdXRhYmxlLAp9CnRyeToKICAgIGltcG9ydCBudW1weSBhcyBucAogICAgaW1wb3J0IGxpZ2h0Z2JtIGFzIGxnYgogICAgaW1wb3J0IHRocmVhZHBvb2xjdGwKICAgIHJlY29yZFsibnVtcHkiXSA9IG5wLl9fdmVyc2lvbl9fCiAgICByZWNvcmRbImxpZ2h0Z2JtIl0gPSBsZ2IuX192ZXJzaW9uX18KICAgIHJlY29yZFsidGhyZWFkcG9vbGN0bCJdID0gdGhyZWFkcG9vbGN0bC5fX3ZlcnNpb25fXwogICAgaW5mbyA9IHRocmVhZHBvb2xjdGwudGhyZWFkcG9vbF9pbmZvKCkKICAgIHJlY29yZFsidGhyZWFkcG9vbF9pbmZvIl0gPSBbe2s6IGkuZ2V0KGspIGZvciBrIGluICgidXNlcl9hcGkiLCAiaW50ZXJuYWxfYXBpIiwgInByZWZpeCIsICJ2ZXJzaW9uIiwgIm51bV90aHJlYWRzIiwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgImZpbGVwYXRoIil9IGZvciBpIGluIGluZm9dCiAgICBvbXAgPSBbaS5nZXQoIm51bV90aHJlYWRzIikgZm9yIGkgaW4gaW5mbyBpZiBpLmdldCgidXNlcl9hcGkiKSA9PSAib3Blbm1wIl0KICAgIHJlY29yZFsib3Blbm1wX2RlZmF1bHRfbnVtX3RocmVhZHMiXSA9IG9tcCBpZiBvbXAgZWxzZSAiPG5vIG9wZW5tcCBwb29sIGxvYWRlZD4iCiAgICByZWNvcmRbInN0YXR1cyJdID0gIm9rIgpleGNlcHQgRXhjZXB0aW9uIGFzIGU6ICAjIHJlY29yZGVkLCBub3QgcmFpc2VkOiBhIHByb2JlIGZhaWx1cmUgZG9lcyBub3Qgc3RvcCB0aGUgbGFuZXMKICAgIHJlY29yZFsic3RhdHVzIl0gPSBmImZhaWxlZDoge3R5cGUoZSkuX19uYW1lX199OiB7ZX0iCnByaW50KGpzb24uZHVtcHMocmVjb3JkLCBpbmRlbnQ9MSwgc29ydF9rZXlzPVRydWUpKQo=' | base64 -d > "$V/p3/tools/pfd_threadprobe.py"
printf '%s' 'IiIiMUIgcHJlLWNoZWNrIFBhcnQgMSwgUDMncyB0YXNrIHRhYmxlIChGRC0xQi1QUkVDSEVDSy1GRC1ERUNMQVJBVElPTi5tZCBzZWN0aW9uIDc7IEJpbmRpbmcgMSwgYWRkZW5kdW0gQTEpLgoKVGhlIGJ1bGsgaXMgdGhlIDMyNyBpdGVtcyAoQSwgQiBhbmQgRG5vbSwgZWFjaCBhdCBDViBhbmQgdGhlIDEwOCB1bml2ZXJzZXM6IEZsdXhfMC4uOTkgYW5kIHRoZSA4IGRldGVjdG9yIHVuaXZlcnNlcyksCmxlc3MgUDIncyA4IHBpbG90IGl0ZW1zOiAzMTkuIFNlY3Rpb24gNzogNyBvbmUtbm9kZSBqb2JzLCA4IGxhbmVzIHBlciBub2RlLCBhdCBtb3N0IDYgaXRlbXMgcGVyIGxhbmUuCgpFYWNoIHRhYmxlIGxpbmUgaXMgb25lIGxhbmU6ICI8bmFtZT48VEFCPmZkXzFiX3ByZWNoZWNrX2ZkLnB5PFRBQj51bmZvbGQgLS1tb2RlIE0gLS11bml2ZXJzZXMgVTEsLi4uLFVrIDxpbnB1dHM+IiwKcnVuIGJ5IHRoZSBjb21taXR0ZWQgczVjX2FycmF5LnNoLiBUaGUgbW9kdWxlIHJ1bnMgb25lIG1vZGUgcGVyIGludm9jYXRpb24sIHNvIGVhY2ggbGFuZSBob2xkcyBvbmUgbW9kZS4gRWFjaCBtb2RlJ3MKaXRlbXMsIGluIHRoZSBtb2R1bGUncyBiYW5kIG9yZGVyLCBhcmUgc3BsaXQgaW50byBjZWlsKG4vNikgY29udGlndW91cyBsYW5lcyBhcyBldmVuIGFzIHBvc3NpYmxlOiBBIDEwNiAtPiAxOCBsYW5lcywKQiAxMDYgLT4gMTgsIERub20gMTA3IC0+IDE4LiBUaGF0IGlzIDU0IGxhbmVzLCBsYWlkIG91dCBpbiB0aGF0IG9yZGVyIG92ZXIgam9icyBvZiA4IGxpbmVzICh0aGUgc2V2ZW50aCBqb2IgaGFzIDYpLgoKVGhlIG1vZHVsZSBpcyBpbXBvcnRlZCBmcm9tIHRoZSBkZXBsb3kgdG8gcmVhZCB1bml2ZXJzZXMoKSBhbmQgUElMT1QsIHdoaWNoIG11c3QgZXF1YWwgdGhlIGRlY2xhcmF0aW9uJ3MgbGlzdHMsIGFuZApldmVyeSBpdGVtIG91dHNpZGUgdGhlbSBpcyByZWZ1c2VkLgoKdXNhZ2U6IHB5dGhvbjMgLUkgbWFrZV9wM190YWJsZS5weSA8ZGVwbG95IGNoZWNrb3V0PiA8Vj4gPG91dCB0YWJsZT4KIiIiCmltcG9ydCBtYXRoCmltcG9ydCBzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgpQID0gIi9wc2NyYXRjaC9zZC9qL2pvc2VwaHJiIgpERVRFQ1RPUiA9IFsiR0VBTlRfTmV1dHJvbl8wIiwgIkdFQU5UX05ldXRyb25fMSIsICJHRUFOVF9QaW9uXzAiLCAiR0VBTlRfUGlvbl8xIiwgIkdFQU5UX1Byb3Rvbl8wIiwgIkdFQU5UX1Byb3Rvbl8xIiwKICAgICAgICAgICAgIk1pbm9zRWZmaWNpZW5jeV8wIiwgIk1pbm9zRWZmaWNpZW5jeV8xIl0KREVDTEFSRURfVU5JVkVSU0VTID0gW2YiRmx1eF97aX0iIGZvciBpIGluIHJhbmdlKDEwMCldICsgREVURUNUT1IKU0VDVElPTjdfUElMT1QgPSBbKCJBIiwgIkNWIiksICgiQiIsICJDViIpLCAoIkRub20iLCAiQ1YiKSwgKCJBIiwgIkZsdXhfMCIpLCAoIkIiLCAiRmx1eF8wIiksICgiRG5vbSIsICJGbHV4XzAiKSwKICAgICAgICAgICAgICAgICAgKCJBIiwgIk1pbm9zRWZmaWNpZW5jeV8wIiksICgiQiIsICJNaW5vc0VmZmljaWVuY3lfMCIpXQpNT0RFUyA9ICgiQSIsICJCIiwgIkRub20iKQpQRVJfTEFORSwgTEFORVNfUEVSX0pPQiwgSk9CUyA9IDYsIDgsIDcKCgpkZWYgbWFpbigpIC0+IGludDoKICAgIGRlcGxveSwgViwgb3V0ID0gUGF0aChzeXMuYXJndlsxXSksIHN5cy5hcmd2WzJdLCBQYXRoKHN5cy5hcmd2WzNdKQogICAgc3lzLnBhdGguaW5zZXJ0KDAsIHN0cihkZXBsb3kgLyAibmQtdW5mb2xkaW5nIikpCiAgICBpbXBvcnQgZmRfMWJfcHJlY2hlY2tfZmQgYXMgcGZkICAjIG5vcWE6IEU0MDIKICAgIGlmIGxpc3QocGZkLnVuaXZlcnNlcygpKSAhPSBERUNMQVJFRF9VTklWRVJTRVM6CiAgICAgICAgcmFpc2UgU3lzdGVtRXhpdCgiVEFCTEU6IHRoZSBtb2R1bGUncyB1bml2ZXJzZXMoKSBpcyBub3QgdGhlIGRlY2xhcmVkIDEwOCIpCiAgICBpZiBbdHVwbGUoeCkgZm9yIHggaW4gcGZkLlBJTE9UXSAhPSBTRUNUSU9ON19QSUxPVCBvciB0dXBsZShwZmQuTU9ERVMpICE9IE1PREVTOgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoIlRBQkxFOiB0aGUgbW9kdWxlJ3MgUElMT1Qgb3IgTU9ERVMgaXMgbm90IHRoZSBkZWNsYXJhdGlvbidzIikKICAgIHBpbG90ID0gc2V0KFNFQ1RJT043X1BJTE9UKQogICAgbGFuZXMgPSBbXQogICAgZm9yIG1vZGUgaW4gTU9ERVM6CiAgICAgICAgaXRlbXMgPSBbdSBmb3IgdSBpbiBbIkNWIl0gKyBERUNMQVJFRF9VTklWRVJTRVMgaWYgKG1vZGUsIHUpIG5vdCBpbiBwaWxvdF0KICAgICAgICBrID0gbWF0aC5jZWlsKGxlbihpdGVtcykgLyBQRVJfTEFORSkKICAgICAgICBiYXNlLCBleHRyYSA9IGRpdm1vZChsZW4oaXRlbXMpLCBrKQogICAgICAgIGkgPSAwCiAgICAgICAgZm9yIGogaW4gcmFuZ2Uoayk6CiAgICAgICAgICAgIG4gPSBiYXNlICsgKDEgaWYgaiA8IGV4dHJhIGVsc2UgMCkKICAgICAgICAgICAgbGFuZXMuYXBwZW5kKChtb2RlLCBpdGVtc1tpOmkgKyBuXSkpCiAgICAgICAgICAgIGkgKz0gbgogICAgICAgIGFzc2VydCBpID09IGxlbihpdGVtcykKICAgIHRvdGFsID0gc3VtKGxlbih1cykgZm9yIF8sIHVzIGluIGxhbmVzKQogICAgYWxsaXRlbXMgPSB7KG0sIHUpIGZvciBtLCB1cyBpbiBsYW5lcyBmb3IgdSBpbiB1c30KICAgIGV4cGVjdCA9IHsobSwgdSkgZm9yIG0gaW4gTU9ERVMgZm9yIHUgaW4gWyJDViJdICsgREVDTEFSRURfVU5JVkVSU0VTfSAtIHBpbG90CiAgICBpZiB0b3RhbCAhPSAzMTkgb3IgYWxsaXRlbXMgIT0gZXhwZWN0IG9yIGxlbihhbGxpdGVtcykgIT0gdG90YWw6CiAgICAgICAgcmFpc2UgU3lzdGVtRXhpdChmIlRBQkxFOiB7dG90YWx9IGl0ZW1zLCBub3Qgc2VjdGlvbiA3J3MgMzE5IikKICAgIGlmIG1heChsZW4odXMpIGZvciBfLCB1cyBpbiBsYW5lcykgPiBQRVJfTEFORSBvciBsZW4obGFuZXMpID4gTEFORVNfUEVSX0pPQiAqIEpPQlM6CiAgICAgICAgcmFpc2UgU3lzdGVtRXhpdCgiVEFCTEU6IGEgbGFuZSBvdmVyIDYgaXRlbXMsIG9yIG1vcmUgbGFuZXMgdGhhbiA3IGpvYnMgb2YgOCIpCiAgICBjb21tb24gPSBbIi0tbnB6IiwgZiJ7UH0vTUlORVJ2QS1PbW5pRm9sZC9uZC11bmZvbGRpbmcvb2ZfaW5wdXRzXzVkLm5weiIsCiAgICAgICAgICAgICAgIi0tYmtnIiwgZiJ7UH0vczVjLTIwMjYwOTI0L3J1bnMvcDIvYmtnX2R1bXAubnB6IiwKICAgICAgICAgICAgICAiLS1iYW5rIiwgZiJ7UH0vTUlORVJ2QS1PbW5pRm9sZC9uZC11bmZvbGRpbmcvYmFua19zd2VlcF81ZF9ia2dhd2FyZSIsCiAgICAgICAgICAgICAgIi0tZGV0ZWN0b3ItZGlyIiwgZiJ7UH0vczVwLTIwMjYwOTI2L2JhbmtfZGV0ZWN0b3IiLAogICAgICAgICAgICAgICItLWZsdXgtZmlsZSIsIGYie1Z9L3N0YWdlL2ZsdXhfdW5pdmVyc2VzLnJvb3QiLAogICAgICAgICAgICAgICItLXBpbnMiLCBmIntQfS9mZC0xYi0yMDI2MTAzMC9waW5zLmpzb24iLAogICAgICAgICAgICAgICItLWV4cGVjdC1waW5zLXNoYTI1NiIsICI1YWRjZDU3NmViNDZmNDQzZmU0MTMzYjA1MDQ0Y2QzMTVjMGVlYjBmMjgxZTIxYWNlZTVmMjMxOGI0YmFiMjQ4IiwKICAgICAgICAgICAgICAiLS10aHJlYWRzIiwgIjMyIiwgIi0tb3V0IiwgZiJ7Vn0vdW5mIl0KICAgIGxpbmVzID0gWyIjIDFCIHByZS1jaGVjayBQYXJ0IDEsIFAzIChGRC0xQi1QUkVDSEVDSy1GRC1ERUNMQVJBVElPTi5tZCBzZWN0aW9uIDc7IEJpbmRpbmcgMSwgYWRkZW5kdW0gQTEpIl0KICAgIGZvciBuLCAobW9kZSwgdXMpIGluIGVudW1lcmF0ZShsYW5lcyk6CiAgICAgICAgbGluZXMuYXBwZW5kKCJcdCIuam9pbihbZiJmZDFiX3BmZF9wM19sYW5le246MDJkfV97bW9kZX0iLCAiZmRfMWJfcHJlY2hlY2tfZmQucHkiLCAidW5mb2xkIiwgIi0tbW9kZSIsIG1vZGUsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIi0tdW5pdmVyc2VzIiwgIiwiLmpvaW4odXMpXSArIGNvbW1vbikpCiAgICBvdXQud3JpdGVfdGV4dCgiXG4iLmpvaW4obGluZXMpICsgIlxuIikKICAgIGpvYnMgPSBbKGogKiBMQU5FU19QRVJfSk9CLCBtaW4obGVuKGxhbmVzKSwgKGogKyAxKSAqIExBTkVTX1BFUl9KT0IpIC0gMSkgZm9yIGogaW4gcmFuZ2UobWF0aC5jZWlsKGxlbihsYW5lcykgLyBMQU5FU19QRVJfSk9CKSldCiAgICBwcmludChmIlRBQkxFOiB7bGVuKGxhbmVzKX0gbGFuZXMsIHt0b3RhbH0gaXRlbXM7IHBlciBtb2RlICIKICAgICAgICAgICsgIiwgIi5qb2luKGYie219IHtzdW0obGVuKHVzKSBmb3IgbW0sIHVzIGluIGxhbmVzIGlmIG1tID09IG0pfSBpbiB7c3VtKG1tID09IG0gZm9yIG1tLCBfIGluIGxhbmVzKX0gbGFuZXMiIGZvciBtIGluIE1PREVTKQogICAgICAgICAgKyBmIjsgaXRlbXMgcGVyIGxhbmUge21pbihsZW4odXMpIGZvciBfLCB1cyBpbiBsYW5lcyl9Li57bWF4KGxlbih1cykgZm9yIF8sIHVzIGluIGxhbmVzKX0iKQogICAgcHJpbnQoIkpPQlM6ICIgKyAiICIuam9pbihmInthfS17Yn0iIGZvciBhLCBiIGluIGpvYnMpKQogICAgcmV0dXJuIDAKCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgogICAgc3lzLmV4aXQobWFpbigpKQo=' | base64 -d > "$V/p3/tools/make_p3_table.py"
for pair in "pfd_p2_wrapper.sh:$WRAPPER_SHA" "pfd_threadprobe.py:$PROBE_SHA" "make_p3_table.py:$GEN_SHA"; do
  f=${pair%%:*}; w=${pair##*:}; got=$(sha256sum "$V/p3/tools/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $w) $f"
  [ "$got" = "$w" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 5. the task table"
env -u PYTHONPATH "$PY" -I "$V/p3/tools/make_p3_table.py" "$DD" "$V" "$V/p3/tables/tasks-p3.tsv" || { echo "STOP: the table generator refused"; finish 5; }
echo "tasks-p3.tsv sha256 $(sha256sum "$V/p3/tables/tasks-p3.tsv" | cut -d' ' -f1)"
cut -f1,4-7 "$V/p3/tables/tasks-p3.tsv"
check=$(grep -v '^#' "$V/p3/tables/tasks-p3.tsv" | awk -F'\t' '
  $2 != "fd_1b_precheck_fd.py" || $3 != "unfold" || $4 != "--mode" || $6 != "--universes" { bad++ }
  { n = split($7, us, ","); if (n > 6) big++; items += n; lanes++
    for (i = 1; i <= n; i++) { k = $5 "_" us[i]; if (k in seen) dup++; seen[k] = 1 } }
  END { pilot = ("A_CV" in seen) + ("B_CV" in seen) + ("Dnom_CV" in seen) + ("A_Flux_0" in seen) + ("B_Flux_0" in seen) + \
        ("Dnom_Flux_0" in seen) + ("A_MinosEfficiency_0" in seen) + ("B_MinosEfficiency_0" in seen)
        printf "lanes %d items %d over6 %d dup %d malformed %d pilot %d\n", lanes, items, big+0, dup+0, bad+0, pilot }')
echo "re-check: $check"
[ "$check" = "lanes 54 items 319 over6 0 dup 0 malformed 0 pilot 0" ] || { echo "STOP: the table is not section 7's bulk"; finish 5; }
echo "== 6. stat only: in-place inputs and the staged flux copy"
for f in "$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$P/fd-1b-20261030/pins.json" \
         "$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz" "$V/stage/flux_universes.root"; do
  stat -c '%n|%s|%Y|%X' "$f" 2>&1
done | tee "$V/p3/logs/stat-before.txt"
echo "== 7. thread variables in the submitting shell (none set; inherited through --export=ALL)"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 8. fence, immediately before submission"
fence || { echo "STOP: the fence is not clear; nothing submitted"; finish 3; }
[ "$(squeue -u josephrb -h -o %j | grep -c '^fd1b')" = 0 ] || { echo "STOP: an fd1b job is queued; nothing submitted"; finish 3; }
echo "FENCE: clear"
jobs=()
for j in 0 1 2 3 4 5 6; do
  a=$((8 * j)); b=$((8 * j + 7)); [ "$b" -gt 53 ] && b=53
  cmd="sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb --time=02:30:00 -J fd1b_pfd_p3_j$j -o $V/p3/logs/%x_%j.out $V/p3/tools/pfd_p2_wrapper.sh $DD $M $V/p3/tables/tasks-p3.tsv $V/p3/lanes $a $b $V/p3/tools/pfd_threadprobe.py"
  echo "$cmd" | tee -a "$V/p3/logs/submit-p3.txt"
  sub=$($cmd 2>&1); src=$?
  echo "$sub" | tee -a "$V/p3/logs/submit-p3.out"; echo "sbatch rc=$src"
  id=$(printf '%s\n' "$sub" | awk '/^Submitted batch job/ {print $4}')
  if [ "$src" -ne 0 ] || [ -z "$id" ]; then
    echo "STOP: sbatch for job $j failed; cancelling ${jobs[*]}"; [ "${#jobs[@]}" -gt 0 ] && scancel "${jobs[@]}"; finish 6
  fi
  jobs+=("$id")
  tl=$(scontrol show job "$id" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
  echo "job $j: $id lines $a-$b TimeLimit=$tl"
  if [ "$tl" != "02:30:00" ]; then
    echo "STOP: TimeLimit is not 02:30:00; scancel ${jobs[*]}"; scancel "${jobs[@]}"; echo "scancel rc=$?"; finish 7
  fi
done
echo "submitted: ${jobs[*]}"
squeue -u josephrb -h -o '%i %j %T %l %D %R'
finish 0
