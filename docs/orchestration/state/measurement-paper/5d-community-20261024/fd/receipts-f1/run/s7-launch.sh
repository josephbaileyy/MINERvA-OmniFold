# Launch step 7 detached on a login node. Usage: bash s7-launch.sh <sha256 of the uploaded s7-body.sh>.
# The body is uploaded first by its own ssh call (ssh saul "cat > $OUT/logs/s7-body.sh" < s7.sh); this refuses unless
# the uploaded bytes are the expected ones, then runs them under nohup.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
B=$OUT/logs/s7-body.sh
[ "$(sha256sum $B | cut -c1-64)" = "${1:?expected sha256}" ] || { echo "STOP: $B is not the expected bytes"; exit 3; }
nohup bash $B > $OUT/logs/s7-nohup.out 2>&1 < /dev/null &
echo "launched pid $! on $(hostname) at $(date -u +%FT%TZ)"
