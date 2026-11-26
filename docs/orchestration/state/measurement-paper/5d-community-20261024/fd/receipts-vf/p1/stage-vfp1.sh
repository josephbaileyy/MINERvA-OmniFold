#!/bin/bash
# V_F Phase 1 stager (FD-VF BINDING 1 invocation rules), run on login02 as `bash -s -- start` or `bash -s -- finish`
# through `ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s -- MODE'" < stage-vfp1.sh`.
# start:  refuse unless login02, no V_F chain or vfp1 worker of mine runs, and $BA, /dev/shm/vfp1.sh and
#         /dev/shm/vfp1.log are all absent; create the two files new (O_EXCL), each checked to be a regular file of
#         mine; decode into the copy the bound connect-vf-p1.sh (sha256 WANT) and refuse unless its sha256 is WANT;
#         head the log "vfp1 sha WANT"; run the copy detached as `nohup setsid nice -n 19 bash /dev/shm/vfp1.sh`
#         inside a wrapper that logs "worker start PID" first and "worker exit=N" last; confirm the wrapper started
#         within WAIT seconds, or exit 3 (UNCONFIRMED) without signalling anything, for read-only polls to follow.
# finish: refuse unless login02, both files are regular files of mine, the log is headed "vfp1 sha WANT" and holds
#         "worker start PID", the copy's sha256 is WANT, no worker runs, and the log ends "worker exit=N" (0-255);
#         copy the log into the connect's existing $BA/receipts/vfp1.log ($BA and receipts real directories of mine) (a new file, or one already equal to the
#         log), record its sha256, delete /dev/shm/vfp1.sh and /dev/shm/vfp1.log and nothing else, and exit N.
BA=/pscratch/sd/j/josephrb/vf-20261125-p1
WANT=9cda83f0730350c5e4d73921290c41b127c1299478cc8a49130c33bfe4d48e2f
S=/dev/shm/vfp1.sh; L=/dev/shm/vfp1.log; R=$BA/receipts
umask 077
export TMPDIR=/dev/shm                                 # bash's here-document file stays private, in /dev/shm
set -o noclobber
WAIT=${VFP1_WAIT:-30}
stop() { echo "STOP: $*"; exit "${STOP_RC:-2}"; }
h=$(hostname) && [ "$h" = login02 ] || stop "not login02 (${h:-hostname failed})"
sha() { local s; s=$(sha256sum "$1") || return 1; s=${s%% *}; [[ "$s" =~ ^[0-9a-f]{64}$ ]] || return 1; echo "$s"; }
mine() { [ -f "$1" ] && [ ! -L "$1" ] && [ -O "$1" ]; }        # a regular file of mine, not a symlink
absent() { [ ! -e "$1" ] && [ ! -L "$1" ]; }
newfile() { absent "$1" || return 1; : > "$1" || return 1; mine "$1" && [ ! -s "$1" ]; }
workers() {                                            # my V_F chains and vfp1 workers; fails if ps fails or is empty
  local u out pid args
  u=$(id -un) && [ -n "$u" ] || return 2
  out=$(ps -ww -u "$u" -o pid=,args=) && [ -n "$out" ] || return 2
  while read -r pid args; do
    case "$args" in
      "$HOME/.conda/envs/root_6_28/bin/python3 -I -B "*"/nd-unfolding/fd_vf_addition.py chain "*) echo "$pid $args" ;;
      "bash $S"|"bash -c "*" vfp1 $S"|"setsid nice -n 19 bash -c "*" vfp1 $S"|"nice -n 19 bash -c "*" vfp1 $S") echo "$pid $args" ;;
    esac
  done <<< "$out"
}
case "$1" in
start)
  r=$(workers) || stop "ps failed"
  [ -z "$r" ] || stop "already running: $r"
  absent "$BA" || stop "$BA exists"
  absent "$S" && absent "$L" || stop "$S or $L exists (a previous run not finished)"
  newfile "$S" || stop "cannot create $S as a new regular file of mine (nothing removed)"
  newfile "$L" || stop "cannot create $L as a new regular file of mine (nothing removed)"
  base64 -d >> "$S" <<'B64' || { rm -f "$S" "$L"; STOP_RC=9 stop "decode"; }
IyEvYmluL2Jhc2gKIyBWX0YgUGhhc2UgMSAoRkQtVkYtQURESVRJT04tREVDTEFSQVRJT04ubWQgwqczLCDCpzcuMzsgYW1lbmRtZW50IEExKSwgb25lIGxvZ2luMDIgY29ubmVjdDogY2xhaW0gJEJBIGF0b21pY2FsbHksIGEgZnJlc2gKIyBjbG9uZSBvZiB0aGUgYm91bmQgY29tbWl0LCB0aGUgMjIgYm91bmQgYmxvYnMsIHJvb3RfNl8yOCBjaGVja2VkLCB0aGUgNTQxIG9uLW5vZGUgdGVzdHMgKGFtZW5kbWVudCBBMykgd2l0aCBubyBza2lwLCB0aGVuCiMgZmRfdmZfYWRkaXRpb24ucHkgY2hhaW4gdW5kZXIgdGltZW91dCAzNjAwLiBXcml0ZXMgb25seSB1bmRlciAkQkE7IG5vdGhpbmcgdG8gQ0ZTOyAwIG5vZGUtaDsgcmVtb3ZlcyBub3RoaW5nIGl0IGRpZAojIG5vdCBjcmVhdGUuIEV2ZXJ5IGdhdGUgbmVlZHMgaXRzIGNvbW1hbmQgdG8gc3VjY2VlZCBBTkQgaXRzIG91dHB1dCB0byBiZSB0aGUgZXhwZWN0ZWQgb25lLiBObyBzZXQgLXUgKGNvbmRhKS4KQkE9L3BzY3JhdGNoL3NkL2ovam9zZXBocmIvdmYtMjAyNjExMjUtcDEKTT1jMGZhMGQwMWFhMDVkNWI2YmI5NzkzOTE5NzY4NDkxZDhkOGEwYzIzCkVOVj0kSE9NRS8uY29uZGEvZW52cy9yb290XzZfMjgKc3RvcCgpIHsgZWNobyAiU1RPUDogJCoiOyBleGl0ICIke1NUT1BfUkM6LTl9IjsgfQpoPSQoaG9zdG5hbWUpICYmIFsgIiRoIiA9IGxvZ2luMDIgXSB8fCBTVE9QX1JDPTIgc3RvcCAibm90IGxvZ2luMDIgKCR7aDotaG9zdG5hbWUgZmFpbGVkfSkiCm1rZGlyICIkQkEiIDI+L2Rldi9udWxsIHx8IFNUT1BfUkM9MiBzdG9wICIkQkEgZXhpc3RzIG9yIGNhbm5vdCBiZSBjcmVhdGVkIiAgICAjIGF0b21pYyBjbGFpbTogZmFpbHMgb24gYW55dGhpbmcgdGhlcmUKbWtkaXIgIiRCQS9yZWNlaXB0cyIgIiRCQS9sb2dzIiAiJEJBL3RtcCIgfHwgc3RvcCAibWtkaXIiCmV4cG9ydCBUTVBESVI9JEJBL3RtcCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICMgYmVmb3JlIGFueSBoZXJlLWRvY3VtZW50LCBjb21tYW5kIHN1YnN0aXR1dGlvbiBvciBweXRob24KZXhwb3J0IFhER19DQUNIRV9IT01FPSRCQS90bXAveGRnLWNhY2hlICAgICAgICAgICAgICAgICAgIyBmb250Y29uZmlnJ3MgY2FjaGUgKG1hdHBsb3RsaWIgY2FsbHMgZmMtbGlzdCkgc3RheXMgaW4gJEJBCnRzPSQoZGF0ZSAtdSArJUZUJVRaKSAmJiBbIC1uICIkdHMiIF0gfHwgc3RvcCAiZGF0ZSIKcHJpbnRmICclc1xuJXNcbicgIiRoIiAiJHRzIiA+ICIkQkEvcmVjZWlwdHMvaG9zdC50eHQiIHx8IHN0b3AgImhvc3QudHh0Igpwb3JjZWxhaW5fZW1wdHkoKSB7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAjIHN1Y2NlZWRzIG9ubHkgaWYgZ2l0IHN1Y2NlZWRlZCBhbmQgcHJpbnRlZCBub3RoaW5nCiAgbG9jYWwgb3V0CiAgb3V0PSQoZ2l0IC1DICIkQkEvZGVwbG95IiAtYyBzdGF0dXMuc2hvd1VudHJhY2tlZEZpbGVzPWFsbCBzdGF0dXMgLS1wb3JjZWxhaW4gLS1pZ25vcmVkIC0tdW50cmFja2VkLWZpbGVzPWFsbCkgfHwgcmV0dXJuIDIKICBbIC16ICIkb3V0IiBdIHx8IHsgcHJpbnRmICclc1xuJyAiJG91dCIgfCBoZWFkIC0yMDsgcmV0dXJuIDE7IH0KfQpnaXQgY2xvbmUgLXEgLS1uby1jaGVja291dCBodHRwczovL2dpdGh1Yi5jb20vam9zZXBoYmFpbGV5eS9NSU5FUnZBLU9tbmlGb2xkLmdpdCAiJEJBL2RlcGxveSIgPiAiJEJBL2xvZ3MvY2xvbmUubG9nIiAyPiYxIHx8IHN0b3AgImNsb25lIgpnaXQgLUMgIiRCQS9kZXBsb3kiIC1jIGFkdmljZS5kZXRhY2hlZEhlYWQ9ZmFsc2UgY2hlY2tvdXQgLXEgLS1kZXRhY2ggIiRNIiB8fCBzdG9wICJjaGVja291dCIKaGVhZD0kKGdpdCAtQyAiJEJBL2RlcGxveSIgcmV2LXBhcnNlIEhFQUQpICYmIFsgIiRoZWFkIiA9ICIkTSIgXSB8fCBzdG9wICJIRUFEICR7aGVhZDotdW5yZWFkYWJsZX0gaXMgbm90IHRoZSBib3VuZCBjb21taXQiCnBvcmNlbGFpbl9lbXB0eSB8fCBzdG9wICJwb3JjZWxhaW4gYWZ0ZXIgY2hlY2tvdXQiCndhbnQ9KAogICI5NzQwMjdiMWJjMTcyMTM0MjMzNjVjNzZjZjcxZjYxMDFjMzcwZGRkIG5kLXVuZm9sZGluZy9mZF92Zl9hZGRpdGlvbi5weSIKICAiODc3YmI2MzMzMzAyZDFjZDQxOWQ2NWQ3Y2UxZjM3MzAwMTA0NmY1NyBuZC11bmZvbGRpbmcvdGVzdHMvdGVzdF9mZF92Zl9hZGRpdGlvbi5weSIKICAiMWYzOTc5MDQ2YzA1MTc3ODZlZDNiMWE2ZjkyMDA0ZWM2Y2Y2OGZjZiBuZC11bmZvbGRpbmcvZmRfY3BsX2FkZGl0aW9uLnB5IgogICIwNzg5OWQxNjFiZGI4NGZlNmU2YjU0OWEzYjhlZTU4ODZkZGU3N2E3IG5kLXVuZm9sZGluZy9mZF9nZW5jbXBfZS5weSIKICAiOWUwMjcyZmFiMjI2NDM3NDlkZjY0ZWE5MWE2NzI3MTMwYTc3YzlmNSBuZC11bmZvbGRpbmcvZmRfZ2VuY21wLnB5IgogICJiNWZiY2VmMzA0ZjFjNDZlMGMwMmU1ZTA4ZDgzYTkwMjg0MGJkMzEzIG5kLXVuZm9sZGluZy9mZF9nZW5jbXBfa2luLnB5IgogICJlNGM1MzBiMjVhZmRhNDhlMDAzNmRlMjQ0MTZjZWE0M2U0NjdkYzQ1IG5kLXVuZm9sZGluZy9mZF9mMF9yZWdyYWRlLnB5IgogICJjN2Q4Y2VhZDAxYTJlMzc2ZTAxY2M3M2NhZGEzY2UxZWViNDg0MTYwIG5kLXVuZm9sZGluZy9mZF9nX2NvbXBhcmUucHkiCiAgImQyMjViMTA4ZDgwMDkyNGVmMjhhZGEyOGU3ZDMxYzk0YzU0YjgwMmYgbmQtdW5mb2xkaW5nL2ZkX2dfZGlhZy5weSIKICAiNmYyNTk1NGFmZmE2MmQ2ZTE2Y2RhNWMwNzlmOWIwOWQwMWI1M2ExZSBuZC11bmZvbGRpbmcvZmRfZ19mb2xsb3d1cC5weSIKICAiYjQzNzYwODhlMzM3YTY0Y2E3NDQ2OGYyZTgyZDlmMWVmMWIzYTgwMCBuZC11bmZvbGRpbmcvZmRfZmx1eF9ib290LnB5IgogICI3NmQxYzViOGI0MWRhNDhkOTNmNjA3NzVjNjNhMTQxMWZhYTMzNGM0IG5kLXVuZm9sZGluZy9mZF9nX2ZpZ3VyZXMucHkiCiAgIjk0M2JiMmYyMjk0NjE0NTY5ZTBlZmEzNDNiZmJjMmZlMjA4MjlkZWQgbmQtdW5mb2xkaW5nL2ZkX2dfZmlndXJlc19jaGVjay5weSIKICAiMzE5NzZlNzAwMmM1OTI1MzZhMjU2NjY0ZWEzYTQzODY3M2E1NDFhMSBuZC11bmZvbGRpbmcvZmRfZGF0YV9wcm9kdWN0LnB5IgogICIzZmI4MmM2ZTgxZWQ0NzA5YjgzYjJlZTYzNGI0YzZiODNlMGJhMTZkIG5kLXVuZm9sZGluZy9mZF9kZXBvc2l0X2NhbmRpZGF0ZS5weSIKICAiMTU0MmVkOTQ2ZjcwMWJmZjYyZWM2ZmU4YzA4Y2RjN2MyNDI0YzU5OSBuZC11bmZvbGRpbmcvczFfYXNzZW1ibGUucHkiCiAgImI2YWVlMDVkZGEwNTY4ZTQwMGRiMjcwNmRmMmQ0OWM5NDQ4NTE0ZTYgbmQtdW5mb2xkaW5nL3M1cF9zdGFnZTFfaW5zcGVjdC5weSIKICAiZGVkMWMyYjEwNWUxMGM0ZTcxMzdkYjliYjY3YmY5NjZkMjBkM2JiZiBkb2NzL29yY2hlc3RyYXRpb24vc3RhdGUvbWVhc3VyZW1lbnQtcGFwZXIvNWQtY29tbXVuaXR5LTIwMjYxMDI0L2ZkL3dpdGgtdmYvYmxvY2svdmZfYmxvY2subnB6IgogICI3MTNjMTJjNzAzYjhiM2NlNGNiODMxNTViZDc0ZmYxZWI4NjhkMjJlIGRvY3Mvb3JjaGVzdHJhdGlvbi9zdGF0ZS9tZWFzdXJlbWVudC1wYXBlci81ZC1jb21tdW5pdHktMjAyNjEwMjQvZmQvd2l0aC12Zi9ibG9jay92Zl9ibG9jay5qc29uIgogICI4OGI2Y2FmY2YxNTIxMjYwNmJmYWI1NmVhN2I0YTJjZDRlYTg4YTI0IGRvY3Mvb3JjaGVzdHJhdGlvbi9zdGF0ZS9tZWFzdXJlbWVudC1wYXBlci81ZC1jb21tdW5pdHktMjAyNjEwMjQvRkQtVkYtQURESVRJT04tREVDTEFSQVRJT04ubWQiCiAgIjNiYTBiMzY3YjhiOGUxZDU0MTAyYTBkODhkY2I1NDg4NGE2NDMwOTUgZG9jcy9vcmNoZXN0cmF0aW9uL3N0YXRlL21lYXN1cmVtZW50LXBhcGVyLzVkLWNvbW11bml0eS0yMDI2MTAyNC9GRC1WRi1BRERJVElPTi1BTUVORE1FTlQtQTEubWQiCiAgIjYxZDI4YjFmNzhlMjQ2NjVhNzMwZmI1MGNjZWE1YTc4YWQzYWQ2ODUgZG9jcy9vcmNoZXN0cmF0aW9uL3N0YXRlL21lYXN1cmVtZW50LXBhcGVyLzVkLWNvbW11bml0eS0yMDI2MTAyNC9GRC1WRi1BRERJVElPTi1BTUVORE1FTlQtQTIubWQiCikKWyAiJHsjd2FudFtAXX0iID0gMjIgXSB8fCBzdG9wICJ0aGUgYmxvYiBsaXN0IGhvbGRzICR7I3dhbnRbQF19IGVudHJpZXMsIG5vdCAyMiIKcmVjPSIiOyBuPTAKZm9yIHcgaW4gIiR7d2FudFtAXX0iOyBkbwogIGI9JHt3JSUgKn07IHA9JHt3IyogfQogIGc9JChnaXQgLUMgIiRCQS9kZXBsb3kiIHJldi1wYXJzZSAiJE06JHAiKSB8fCBzdG9wICJjYW5ub3QgcmVzb2x2ZSAkcCIKICBbICIkZyIgPSAiJGIiIF0gfHwgc3RvcCAiYmxvYiAkcCBpcyAkZywgbm90ICRiIgogIHJlYys9IiRnICRwIiQnXG4nOyBuPSQoKG4gKyAxKSkKZG9uZQpbICIkbiIgPSAyMiBdIHx8IHN0b3AgImNoZWNrZWQgJG4gYmxvYnMsIG5vdCAyMiIKcHJpbnRmICclcycgIiRyZWMiID4gIiRCQS9yZWNlaXB0cy9kZXBsb3ktYmxvYnMudHh0IiB8fCBzdG9wICJkZXBsb3ktYmxvYnMudHh0IgplY2hvICJkZXBsb3kgb2sgYXQgJE06ICRuIGJsb2JzIgpob29rPSQoL2dsb2JhbC9jb21tb24vc29mdHdhcmUvbmVyc2MvcGUvY29uZGEvMjQuMTAuMC9NaW5pZm9yZ2UzLTI0LjcuMS0wL2Jpbi9jb25kYSBzaGVsbC5iYXNoIGhvb2spICYmIFsgLW4gIiRob29rIiBdIHx8IHN0b3AgImNvbmRhIGhvb2siCmV2YWwgIiRob29rIiB8fCBzdG9wICJjb25kYSBob29rIGV2YWwiCmNvbmRhIGFjdGl2YXRlICIkRU5WIiB8fCBzdG9wICJjb25kYSBhY3RpdmF0ZSIKWyAiJENPTkRBX1BSRUZJWCIgPSAiJEVOViIgXSB8fCBzdG9wICJDT05EQV9QUkVGSVggaXMgJHtDT05EQV9QUkVGSVg6LXVuc2V0fSIKcHk9JChjb21tYW5kIC12IHB5dGhvbjMpICYmIFsgIiRweSIgPSAiJEVOVi9iaW4vcHl0aG9uMyIgXSB8fCBzdG9wICJweXRob24zIGlzICR7cHk6LW5vdCBmb3VuZH0iClBZPSJlbnYgLXUgUFlUSE9OUEFUSCAkRU5WL2Jpbi9weXRob24zIgpleHBvcnQgTVBMQ09ORklHRElSPSRCQS90bXAvbXBsLXRlc3RzIFBZVEhPTkRPTlRXUklURUJZVEVDT0RFPTEgICMgYmVmb3JlIHRoZSBwcm9iZTogbm8gY2FjaGUgb3IgYnl0ZWNvZGUgb3V0c2lkZSAkQkEKdj0kKCRQWSAtSSAtQiAtYyAnaW1wb3J0IHN5cywgbnVtcHksIG1hdHBsb3RsaWI7IHByaW50KHN5cy52ZXJzaW9uLnNwbGl0KClbMF0sIG51bXB5Ll9fdmVyc2lvbl9fLCBtYXRwbG90bGliLl9fdmVyc2lvbl9fKScpIFwKICB8fCBzdG9wICJ0aGUgdmVyc2lvbiBwcm9iZSBmYWlsZWQiCnByaW50ZiAnJXNcbicgIiR2IiA+ICIkQkEvcmVjZWlwdHMvZW52LnR4dCIgfHwgc3RvcCAiZW52LnR4dCIKWyAiJHYiID0gIjMuMTEuMTQgMS4yNi40IDMuMTAuOCIgXSB8fCBzdG9wICJub3QgRS1BMidzIHJlbmRlcmVyOiAkdiIKY2QgIiRCQS9kZXBsb3kvbmQtdW5mb2xkaW5nL3Rlc3RzIiB8fCBzdG9wICJ0ZXN0cyBkaXIiCiMgdGhlIG9uLW5vZGUgc2VsZWN0aW9uIG9mIGFtZW5kbWVudCBBMzogdGVuIG1vZHVsZXMgd2hvbGUgYW5kIHRlc3RfZmRfZ2VuY21wX2Ugd2l0aG91dCBTdGVwQ1IsIDU0MSB0ZXN0cwp0aW1lb3V0IDM2MDAgJFBZIC1CIC1tIHVuaXR0ZXN0IC12IHRlc3RfZmRfdmZfYWRkaXRpb24gdGVzdF9mZF9jcGxfYWRkaXRpb24gdGVzdF9mZF9nX2NvbXBhcmUgdGVzdF9mZF9nX2RpYWcgXAogIHRlc3RfZmRfZ19mb2xsb3d1cCB0ZXN0X2ZkX2ZsdXhfYm9vdCB0ZXN0X2ZkX2YwX3JlZ3JhZGUgdGVzdF9mZF9nX2ZpZ3VyZXMgdGVzdF9mZF9kZXBvc2l0X2NhbmRpZGF0ZSBcCiAgdGVzdF9mZF9kYXRhX3Byb2R1Y3QgdGVzdF9mZF9nZW5jbXBfZS5TZXRzIHRlc3RfZmRfZ2VuY21wX2UuU3RhZ2UgdGVzdF9mZF9nZW5jbXBfZS5NYXRlcmlhbGl6ZSB0ZXN0X2ZkX2dlbmNtcF9lLkNoYWluIFwKICA+ICIkQkEvbG9ncy90ZXN0cy5vdXQiIDI+ICIkQkEvbG9ncy90ZXN0cy5sb2ciCnRyYz0kPwojIHVuaXR0ZXN0IHdyaXRlcyBpdHMgcmVwb3J0IHRvIHN0ZGVyciAodGVzdHMubG9nOyBhbnl0aGluZyB0aGUgdGVzdHMgcHJpbnQgdG8gc3Rkb3V0IGdvZXMgdG8gdGVzdHMub3V0KS4gSXQgbXVzdCBob2xkCiMgZXhhY3RseSBvbmUgIlJhbiBOIHRlc3RzIiBsaW5lLCBhbmQgaXRzIGxhc3QgdGhyZWUgbm9uLWJsYW5rIGxpbmVzIG11c3QgYmUgdGhlIGNsb3NpbmcgYmxvY2s6IHRoZSBydWxlLAojICJSYW4gNTQxIHRlc3RzIGluIFRzIiwgYW5kICJPSyIgYWxvbmUgKGEgc2tpcCBlbmRzICJPSyAoc2tpcHBlZD1OKSIpLgp2ZXJkaWN0PSQoYXdrICdORiB7IGFbKytuXSA9ICQwIH0gL15SYW4gWzAtOV0rIHRlc3RzPyBpbiAvIHsgcisrIH0KICBFTkQgeyBpZiAociA9PSAxICYmIG4gPj0gMyAmJiBhW25dID09ICJPSyIgJiYgYVtuLTFdIH4gL15SYW4gNTQxIHRlc3RzIGluIFswLTkuXStzJC8gJiYgYVtuLTJdIH4gL14tKyQvKSBwcmludCAiUEFTUyI7CiAgICAgICAgZWxzZSBwcmludGYgIkZBSUw6ICVkIFJhbiBsaW5lczsgJXMgfCAlcyB8ICVzIiwgciwgYVtuLTJdLCBhW24tMV0sIGFbbl0gfScgIiRCQS9sb2dzL3Rlc3RzLmxvZyIpIFwKICB8fCB2ZXJkaWN0PSJGQUlMOiBhd2siCnByaW50ZiAndGVzdHMgcmM9JXMgJXNcbicgIiR0cmMiICIkdmVyZGljdCIgPiAiJEJBL2xvZ3MvdGVzdHMuc3VtbWFyeSIgfHwgc3RvcCAidGVzdHMuc3VtbWFyeSIKY2F0ICIkQkEvbG9ncy90ZXN0cy5zdW1tYXJ5IgpbICIkdHJjIiA9IDAgXSAmJiBbICIkdmVyZGljdCIgPSBQQVNTIF0gfHwgc3RvcCAidGVzdHMgKHJjICR0cmM7ICR2ZXJkaWN0OyBhIHNraXAgZW5kcyAnT0sgKHNraXBwZWQ9TiknKSIKcG9yY2VsYWluX2VtcHR5IHx8IHN0b3AgInRoZSB0ZXN0cyBsZWZ0IGZpbGVzIGluIHRoZSBkZXBsb3kiCnVuc2V0IE1QTENPTkZJR0RJUiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICMgdGhlIGNoYWluIHNldHMgaXRzIG93biwgdW5kZXIgJEJBL3J1bgp0MD0kKGRhdGUgLXUgKyVGVCVUWikgJiYgWyAtbiAiJHQwIiBdIHx8IHN0b3AgImRhdGUiCnByaW50ZiAnY2hhaW4gc3RhcnQgJXNcbicgIiR0MCIgPj4gIiRCQS9yZWNlaXB0cy9ob3N0LnR4dCIgfHwgc3RvcCAiaG9zdC50eHQiCmNkICIkQkEiIHx8IHN0b3AgImNkICRCQSIKdGltZW91dCAzNjAwICRQWSAtSSAtQiAiJEJBL2RlcGxveS9uZC11bmZvbGRpbmcvZmRfdmZfYWRkaXRpb24ucHkiIGNoYWluIC0tc2NyYXRjaCAvcHNjcmF0Y2gvc2Qvai9qb3NlcGhyYiBcCiAgLS1ydW4tZSAvcHNjcmF0Y2gvc2Qvai9qb3NlcGhyYi9nZW5jbXAtZS0yMDI2MTEwMS9yZXJ1bjEgLS1ydW4tZGlyICIkQkEvcnVuIiA+ICIkQkEvbG9ncy9jaGFpbi5vdXQiIDI+ICIkQkEvbG9ncy9jaGFpbi5lcnIiCnJjPSQ/CmVjaG8gImNoYWluIHJjPSRyYyI7IHRhaWwgLW4gNSAiJEJBL2xvZ3MvY2hhaW4ub3V0IjsgdGFpbCAtbiA1ICIkQkEvbG9ncy9jaGFpbi5lcnIiCmZpbmFsPSRyYwpiYWQoKSB7IGVjaG8gIlJFQ0VJUFQ6ICQqIjsgWyAiJGZpbmFsIiA9IDAgXSAmJiBmaW5hbD03OyB9ICAjIGEgcmVjZWlwdCBmYWlsdXJlIG5ldmVyIGxlYXZlcyBhIHN1Y2Nlc3NmdWwgZXhpdApwcmludGYgJ3JjPSVzXG4nICIkcmMiID4+ICIkQkEvbG9ncy9jaGFpbi5vdXQiIHx8IGJhZCAiY2hhaW4ub3V0Igp0MT0kKGRhdGUgLXUgKyVGVCVUWikgJiYgWyAtbiAiJHQxIiBdIHx8IHsgYmFkICJkYXRlIjsgdDE9dW5rbm93bjsgfQpwcmludGYgJ2NoYWluIHJjPSVzIGVuZCAlc1xuJyAiJHJjIiAiJHQxIiA+PiAiJEJBL3JlY2VpcHRzL2hvc3QudHh0IiB8fCBiYWQgImhvc3QudHh0IgppZiBbIC1kICIkQkEvcnVuIiBdOyB0aGVuCiAgaWYgKCBzZXQgLW8gcGlwZWZhaWw7IGNkICIkQkEvcnVuIiAmJiBmaW5kIC4gLXR5cGUgZiAhIC1wYXRoICcuL3RtcC8qJyAhIC1wYXRoICcuL21wbC8qJyAtcHJpbnQwIHwgc29ydCAteiBcCiAgICAgICAgIHwgeGFyZ3MgLTAgLXIgc2hhMjU2c3VtICkgPiAiJEJBL3JlY2VpcHRzL3J1bi5zaGEyNTYiOyB0aGVuCiAgICBuZj0kKHdjIC1sIDwgIiRCQS9yZWNlaXB0cy9ydW4uc2hhMjU2IikgJiYgWyAiJG5mIiAtZ3QgMCBdICYmIGVjaG8gInJ1biBmaWxlcyBoYXNoZWQ6ICRuZiIgfHwgYmFkICJydW4uc2hhMjU2IGVtcHR5IgogIGVsc2UgYmFkICJydW4uc2hhMjU2IGluY29tcGxldGUiOyBmaQplbHNlIGJhZCAibm8gcnVuIGRpcmVjdG9yeSI7IGZpCmlmIHBvcmNlbGFpbl9lbXB0eTsgdGhlbiBwYT0icG9yY2VsYWluIGFmdGVyOiBlbXB0eSI7IGVsc2UgcGE9InBvcmNlbGFpbiBhZnRlcjogTk9UIGVtcHR5IG9yIHVucmVhZGFibGUiOyBbICIkZmluYWwiID0gMCBdICYmIGZpbmFsPTg7IGZpCmVjaG8gIiRwYSI7IHByaW50ZiAnJXNcbicgIiRwYSIgPiAiJEJBL2xvZ3MvcG9yY2VsYWluLWFmdGVyLnR4dCIgfHwgYmFkICJwb3JjZWxhaW4tYWZ0ZXIudHh0IgpleGl0ICIkZmluYWwiCg==
B64
  got=$(sha "$S") || { rm -f "$S" "$L"; STOP_RC=9 stop "sha256sum"; }
  [ "$got" = "$WANT" ] || { rm -f "$S" "$L"; STOP_RC=9 stop "copy sha $got"; }
  printf 'vfp1 sha %s\n' "$WANT" >> "$L" || { rm -f "$S" "$L"; stop "log head"; }
  nohup setsid nice -n 19 bash -c 'echo "worker start $$"; bash "$1"; echo "worker exit=$?"' vfp1 "$S" >> "$L" 2>&1 < /dev/null &
  pid=$!
  for _ in $(seq "$WAIT"); do grep -q '^worker start [0-9][0-9]*$' "$L" && break; sleep 1; done
  if grep -q '^worker start [0-9][0-9]*$' "$L"; then
    echo "started (launcher pid $pid) sha $got on $h at $(date -u +%FT%TZ)"; head -n 3 "$L"
  else                                                 # nothing is signalled: a late wrapper still logs its exit
    echo "UNCONFIRMED: the wrapper has not reported within ${WAIT}s (launcher pid $pid); nothing was signalled;"
    echo "follow the log with read-only polls; the log so far:"; cat "$L"; exit 3
  fi
  ;;
finish)
  mine "$S" && mine "$L" || stop "$S and $L are not both regular files of mine"
  first=$(head -n 1 "$L") && [ "$first" = "vfp1 sha $WANT" ] || stop "the log is not this stager's: ${first:-unreadable}"
  grep -q '^worker start [0-9][0-9]*$' "$L" || stop "the log has no worker start"
  got=$(sha "$S") && [ "$got" = "$WANT" ] || stop "the copy's sha256 is ${got:-unreadable}, not WANT"
  r=$(workers) || stop "ps failed"
  [ -z "$r" ] || stop "still running: $r"
  last=$(tail -n 1 "$L") || stop "read $L"
  [[ "$last" =~ ^worker\ exit=([0-9]{1,3})$ ]] && [ "${BASH_REMATCH[1]}" -le 255 ] \
    || stop "the log does not end with the worker's exit: $last"
  wexit=${BASH_REMATCH[1]}
  [ -d "$BA" ] && [ ! -L "$BA" ] && [ -O "$BA" ] && [ -d "$R" ] && [ ! -L "$R" ] && [ -O "$R" ] || { echo "the connect made no receipts directory; the log:"; cat "$L"; stop "kept $S and $L"; }
  a=$(sha "$L") || STOP_RC=9 stop "hash $L"
  if absent "$R/vfp1.log"; then                        # copy into a new regular file of mine
    newfile "$R/vfp1.log" && cat "$L" >> "$R/vfp1.log" || STOP_RC=9 stop "copy to $R/vfp1.log"
  fi
  mine "$R/vfp1.log" && b=$(sha "$R/vfp1.log") && [ "$a" = "$b" ] \
    || STOP_RC=9 stop "$R/vfp1.log is not a complete copy (kept $S and $L)"
  line="$b  vfp1.log"
  if absent "$R/vfp1.log.sha256"; then
    newfile "$R/vfp1.log.sha256" && printf '%s\n' "$line" >> "$R/vfp1.log.sha256" || STOP_RC=9 stop "sha256 receipt"
  fi
  mine "$R/vfp1.log.sha256" && [ "$(cat "$R/vfp1.log.sha256")" = "$line" ] || STOP_RC=9 stop "the sha256 receipt differs"
  rm -f "$S" "$L" || STOP_RC=9 stop "rm"
  echo "finished: worker exit=$wexit; log $b copied to $R/vfp1.log; removed $S and $L"
  exit "$wexit"
  ;;
*) stop "usage: start | finish" ;;
esac
