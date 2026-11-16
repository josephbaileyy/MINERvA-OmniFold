#!/bin/bash
# FD-PRR prr_ibu attempt 2: the move (the director's ruling of 2026-11-09, FD-PRR-ADDENDUM-A4 section 10.1). Run in the
# foreground in one ssh session, after the attempt-2 record (#997) has merged. It moves $OUT/log-ibu and $OUT/route2 into
# $OUT/ibu-attempt2/, with a listing and every file's sha256 before and after, and refuses unless they are the same
# files. It reads only these four files, the study's own, and writes nothing outside $OUT/ibu-attempt2.
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
A=$OUT/ibu-attempt2
echo "node $(hostname) $(date -u +%FT%TZ)"
[ -d "$OUT/log-ibu" ] && [ -d "$OUT/route2" ] && [ ! -e "$A" ] || { echo "STOP: precondition (log-ibu and route2 present, ibu-attempt2 absent)"; exit 9; }
q=$(squeue --me -h -o '%j') || { echo "STOP: squeue did not answer"; exit 9; }
[ -z "$(printf '%s\n' "$q" | grep -E '^prr_')" ] || { echo "STOP: a prr_* job is queued or running"; exit 9; }
# attempt 2's record (fd/receipts-prr/ibu/attempt2/lane/remote-sha256.txt): the four log-ibu files; tasks/ and route2/ empty
( cd "$OUT" && sha256sum -c ) <<SUMS || { echo "STOP: log-ibu is not attempt 2's record"; exit 9; }
986cd8be1cbe0a1a8b5640e6417203f8bfedea06b9284be5b62163521c164608  log-ibu/env.log
9830ce9d409097e8147e1ce53d55c9b0539a7344c241bd2caad75ca441f08355  log-ibu/FAILED
6c0c07e7bc387fb7b6f1edcfe7c5106c9c4c4114e419e1ea1fdb19083763b1e6  log-ibu/ibu.log
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  log-ibu/verify-stage.log
SUMS
echo "== before"; ( cd "$OUT" && find log-ibu route2 -printf "%y %s %p\n" | sort -k3 )
before=$( cd "$OUT" && find log-ibu route2 -type f | sort | xargs -r sha256sum )
echo "$before"
[ "$(cd "$OUT" && find log-ibu route2 -type f | wc -l)" -eq 4 ] || { echo "STOP: log-ibu and route2 hold other than attempt 2's 4 files"; exit 9; }
mkdir "$A" && mv "$OUT/log-ibu" "$A/log-ibu" && mv "$OUT/route2" "$A/route2" || { echo "STOP: the move failed"; exit 5; }
echo "== after"; ( cd "$A" && find log-ibu route2 -printf "%y %s %p\n" | sort -k3 )
after=$( cd "$A" && find log-ibu route2 -type f | sort | xargs -r sha256sum )
echo "$after"
[ "$before" = "$after" ] || { echo "STOP: the moved files differ"; exit 5; }
ls -d "$OUT/log-ibu" "$OUT/route2" 2>&1
echo "moved rc=0 $(date -u +%FT%TZ)"
