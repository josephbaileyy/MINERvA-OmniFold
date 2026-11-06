#!/bin/bash
# REF-C2C1 step two, stage 4: delete the staged copies (REF-C2C1-BINDING-2.md ruling 2.4; the director's GO of
# 2026-11-06 after the read's receipt #844 merged), in the B9 form, on a login node, 0 node-h. Only the $CV/$MC staging
# root that binding 2 §2.1 created, /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage, holding the two copies. read/,
# read-2/, the units, the deploys and every COV2D path are not touched. Literal paths only; no variable rm targets.
#   - refuses unless the root holds exactly its two copies and nothing else (anything else is listed and it stops), and
#     no fd_c2c1r job is queued;
#   - before: `ls -la` of the root, and each copy's sha256 through an O_NOATIME read, which must equal stage.json's pins
#     (43f8cc16, d40aea69);
#   - the deletion: rm of the two files by literal path, then rmdir of the now-empty root by literal path;
#   - after: `ls -la` of the parent, and a stat of each path, which must be absent.
# The ledger goes to /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage4-ledger/ (refused if it exists). No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
L=/pscratch/sd/j/josephrb/ref-c2c1-20261106/stage4-ledger
bail() { rm -f -- "$SELF"; exit 9; }
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -d /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage ] && [ ! -e "$L" ] || bail
[ -z "$(squeue --me -h -n fd_c2c1r -o %i)" ] || bail
mkdir -p "$L" || bail
exec > "$L/ledger.log" 2>&1
finish() { echo "ref-c2c1 stage 4 rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/stage4.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "stage-4 script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/refc2c1_stage4_delete_login.sh"
echo "== the root's contents (stat only), $(date -u +%FT%TZ)"
find /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage -mindepth 1 -printf '%y %s %T@ %u %m %P\n' | LC_ALL=C sort > "$L/root-contents-before.txt"
cat "$L/root-contents-before.txt"
want=$(printf '%s\n' runEventLoopMC_MEFHC.root runEventLoopOmniFold_MEFHC.root)
got=$(awk '$1 == "f" {print $NF}' "$L/root-contents-before.txt" | LC_ALL=C sort)
others=$(awk '$1 != "f" || ($NF != "runEventLoopMC_MEFHC.root" && $NF != "runEventLoopOmniFold_MEFHC.root")' "$L/root-contents-before.txt")
if [ -n "$others" ] || [ "$got" != "$want" ]; then echo "STOP: the root holds something other than its two copies:"; printf '%s\n' "$others"; finish 4; fi
echo "== BEFORE $(date -u +%FT%TZ)"
ls -la --time-style=full-iso /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage
cv=$(dd if=/pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopOmniFold_MEFHC.root iflag=noatime bs=4M status=none | sha256sum | cut -d' ' -f1)
mc=$(dd if=/pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopMC_MEFHC.root iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "sha256 (O_NOATIME read) runEventLoopOmniFold_MEFHC.root $cv (stage.json pin 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df)"
echo "sha256 (O_NOATIME read) runEventLoopMC_MEFHC.root $mc (stage.json pin d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316)"
[ "$cv" = 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df ] && [ "$mc" = d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316 ] \
  || { echo "STOP: a copy's digest is not its stage.json pin; nothing deleted"; finish 4; }
echo "== DELETION"
echo "$(date -u +%FT%T.%3NZ) rm -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopOmniFold_MEFHC.root"
rm -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopOmniFold_MEFHC.root || { echo "STOP: rm CV failed"; finish 9; }
echo "$(date -u +%FT%T.%3NZ) rm -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopMC_MEFHC.root"
rm -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopMC_MEFHC.root || { echo "STOP: rm MC failed"; finish 9; }
echo "$(date -u +%FT%T.%3NZ) rmdir -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage"
rmdir -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage || { echo "STOP: rmdir failed (not empty?)"; finish 9; }
echo "== AFTER $(date -u +%FT%TZ)"
ls -la --time-style=full-iso /pscratch/sd/j/josephrb/ref-c2c1-20261106
left=0
for p in /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopOmniFold_MEFHC.root \
         /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopMC_MEFHC.root \
         /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage; do
  if [ -e "$p" ]; then echo "STILL PRESENT: $p"; left=1; else echo "absent: $p"; fi
done
[ "$left" -eq 0 ] || finish 8
finish 0
