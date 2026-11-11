#!/bin/bash
# RPD-RECO flux connect 1 (revision 2), the fetch: reads what job rpd_flux1 left under the literal root
# /pscratch/sd/j/josephrb/rpd-reco-flux-20261111, on any login node. DRAFT for coverage-5b-audit and the director's go.
#   0. The job is finished when job.rc exists, or when sacct gives its jobid a terminal state (a job killed at its
#      time limit or out of memory writes no job.rc). Otherwise it prints job.id, job-host.txt and squeue's row,
#      writes nothing and exits 10. It can be run again.
#   1. job.id, job-host.txt (jobid, host, start and end UTC), job.rc and sacct's row; a listing of the whole root (mode,
#      bytes, path), the private tree by name only.
#   2. The factor products run/flux-factors-<PL>.npz stay on pscratch (director, F1). Each one's sha256 is printed and
#      compared with the sha256 flux-extract.json records for it.
#   3. The protected read (tools/protected_read.py): from the private prestage record, the public record
#      protected-read.json of the one listed exception (stat_before, stat_after, the UTC staging window, both staged
#      copies' sha256) and of every staged original that overlaps a protected path. Not applicable with no record.
#   4. The send list: the root's records that exist (job.id, job-host.txt, job.rc, job.out, job.err, rpd_flux1_job.sh,
#      connect.log, strace-probe.txt, fence-overlap.txt, exception-stat-outer.txt, protected-read.json); every regular
#      file directly in run/ except flux-factors-*.npz; every regular file directly in run/real-mnv-check/. Nothing in
#      run/original-inputs, run/mat-data, run/prepare-check, run/tmp, clone, tools or .rpd-private. Over 64 MiB refuses.
#   5. C3 (tools/c3_check.py) when run/prestage-reference.json exists; a .rpd-private without it refuses.
#   6. The redaction check (tools/check_redaction.py, prologue 5's, byte-identical), VIEW NONE; with no private
#      record, any file on the send list holding the string "fingerprints" refuses.
#   7. Only if those pass: connect.log printed, the sha256 of each file sent, and a base64 tar of the list. A FAIL in
#      the protected read does not stop the send (it is the finding); the fetch then exits 11.
# Writes: protected-read.json and the two check outputs under the root, and three tools under
# /dev/shm/limres-rpd-flux1-fetch (refused if it exists, removed at exit). Nothing is written to CFS. umask 077.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
C3_SHA=aed41794b72d8b8de6580d75e0fc4467cad3bc73c5b11dfac44075783b461192
CHECK_SHA=992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316
PREAD_SHA=309f59d46a4f200d924c98cd6beeece9a8c9a2b92cd493fb2e84f6b5693aa7f9
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-flux1-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- /dev/shm/limres-rpd-flux1-fetch/c3_check.py /dev/shm/limres-rpd-flux1-fetch/check_redaction.py /dev/shm/limres-rpd-flux1-fetch/protected_read.py; rmdir /dev/shm/limres-rpd-flux1-fetch 2>/dev/null; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ); fetch script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -d /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 ] || { echo "STOP: no root /pscratch/sd/j/josephrb/rpd-reco-flux-20261111"; rm -f -- "$SELF"; exit 9; }
cd /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 || { rm -f -- "$SELF"; exit 9; }
[ -f job.id ] || { echo "STOP: no job.id (the connect submitted no job)"; rm -f -- "$SELF"; exit 9; }
jid=$(cat job.id)
[[ "$jid" =~ ^[0-9]+$ ]] || { echo "STOP: job.id is not a jobid"; rm -f -- "$SELF"; exit 9; }
acct=$(sacct -X -n -P -j "$jid" -o JobID,JobName,State,ExitCode,Elapsed,Start,End,NodeList,MaxRSS,AllocCPUS,ReqMem,Timelimit)
arc=$?
state=$(printf '%s\n' "$acct" | awk -F'|' -v j="$jid" '$1 == j {print $3}' | cut -d' ' -f1)
echo "job $jid; sacct rc=$arc; state [$state]"
printf '%s\n' "$acct" | sed '/^$/d; s/^/sacct: /'
echo "== job-host.txt"; cat job-host.txt 2>/dev/null || echo "(absent)"
if [ ! -f job.rc ]; then
  case "$state" in
    COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)
      echo "FINISHED WITHOUT job.rc: sacct state $state" ;;
    *)
      echo "NOT FINISHED: no job.rc; squeue:"; squeue -h -j "$jid" -o '%i|%j|%T|%M|%l|%N' 2>&1
      rm -f -- "$SELF"; exit 10 ;;
  esac
else
  echo "job.rc: $(cat job.rc)"
fi
[ ! -e /dev/shm/limres-rpd-flux1-fetch ] || { echo "STOP: /dev/shm/limres-rpd-flux1-fetch exists"; rm -f -- "$SELF"; exit 9; }
[ ! -e c3-check.txt ] && [ ! -e redaction-check.txt ] && [ ! -e protected-read.json ] || { echo "STOP: a fetch output already exists"; rm -f -- "$SELF"; exit 9; }
echo "== 1. listing of the root"
find . -path ./clone -prune -o -printf '%M %s %P\n' | sort -k3
mkdir -m 700 /dev/shm/limres-rpd-flux1-fetch || finish 9
printf '%s' 'IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJDaGVjayB3aGVyZSB0aGUgY29kZSBwdXQgdGhlIGNhbm9uaWNhbCBmaW5nZXJwcmludC1iZWFyaW5nIHByZXBhcmUgcmVjb3JkIChDMyksIGFuZCB0aGF0IG5vdGhpbmcgc2VudCBpcyBpdC4KCkF0ICM4NDgncyBoZWFkIGE0YzNlNTU2LCBjdXN0b2R5IHByZXBhcmUgd3JpdGVzIHRoZSBjYW5vbmljYWwgcHJlc3RhZ2UgcmVjb3JkIG93bmVyLW9ubHkgb3V0c2lkZSB0aGUgcnVuLCBhdApjdXN0b2R5LnByaXZhdGVfcHJlcGFyZV9wYXRoKHJ1biwgInByZXN0YWdlIiwgY29ubmVjdF9pZCkgPQpyZWFscGF0aChydW4pLnBhcmVudC8ucnBkLXByaXZhdGUvc2hhMjU2KHJlYWxwYXRoKHJ1bikgTlVMICJwcmVzdGFnZSIgTlVMIGNvbm5lY3RfaWQpL3ByZXN0YWdlLmpzb24sCmFuZCBsZWF2ZXMgaW4gdGhlIHJ1biBhIHJlZmVyZW5jZSwgcHJlc3RhZ2UtcmVmZXJlbmNlLmpzb24sIG5hbWluZyBpdHMgcGF0aCBhbmQgc2hhMjU2LgpDaGVja3MsIGVhY2ggcmVjb3JkZWQ6CiAgMS4gdGhlIHJlZmVyZW5jZSdzIHNjaGVtYSwgcnVuLCBwcmVwYXJlIG5hbWUsIGFuZCB0aGF0IGl0cyBwYXRoIGVxdWFscyB0aGUgbG9jYXRpb24gcmVjb21wdXRlZCBoZXJlOwogIDIuIHRoZSByZWNvcmQgaXMgdW5kZXIgUk9PVC8ucnBkLXByaXZhdGUgYW5kIG5vdCB1bmRlciB0aGUgcnVuIGRpcmVjdG9yeTsKICAzLiB0aGUgcmVjb3JkIGFuZCBpdHMgZGlyZWN0b3J5IGFyZSBvd25lZCBieSB0aGlzIHVpZCwgd2l0aCBubyBncm91cCBvciBvdGhlciBiaXRzIChtb2RlcyBwcmludGVkKTsKICA0LiB0aGUgcmVjb3JkJ3Mgc2hhMjU2IGVxdWFscyB0aGUgcmVmZXJlbmNlJ3MsIGFuZCBpdCBob2xkcyBlbnZpcm9ubWVudF9zbmFwc2hvdC5maW5nZXJwcmludHMgKHRoZSBjb3VudCBwcmludGVkKTsKICA1LiBST09ULy5ycGQtcHJpdmF0ZSBob2xkcyBleGFjdGx5IHRoYXQgb25lIGZpbGUgKGV2ZXJ5IGVudHJ5IGxpc3RlZCBieSB0eXBlLCBtb2RlIGFuZCByZWxhdGl2ZSBwYXRoKTsKICA2LiBubyBmaWxlIG9uIHRoZSBzZW5kIGxpc3QgbGllcyB1bmRlciAucnBkLXByaXZhdGUsIG9yIGhhcyB0aGUgcmVjb3JkJ3Mgc2hhMjU2LgpQcmludHMgQzMgbGluZXMgYW5kIGEgdmVyZGljdDsgZXhpdHMgMCBvbiBQQVNTLCAxIG9uIEZBSUwuCgp1c2FnZTogYzNfY2hlY2sucHkgUk9PVCBSVU4gU0VORF9GSUxFIFtTRU5EX0ZJTEUgLi4uXQoiIiIKCmZyb20gX19mdXR1cmVfXyBpbXBvcnQgYW5ub3RhdGlvbnMKCmltcG9ydCBoYXNobGliCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgc3RhdAppbXBvcnQgc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKCmRlZiBtYWluKCkgLT4gaW50OgogICAgcm9vdCwgcnVuID0gUGF0aChzeXMuYXJndlsxXSkucmVzb2x2ZSgpLCBQYXRoKHN5cy5hcmd2WzJdKS5yZXNvbHZlKCkKICAgIHNlbmQgPSBbUGF0aChwKSBmb3IgcCBpbiBzeXMuYXJndlszOl1dCiAgICBmYWlsdXJlcyA9IDAKCiAgICBkZWYgY2hlY2sobGFiZWw6IHN0ciwgb2s6IGJvb2wpIC0+IE5vbmU6CiAgICAgICAgbm9ubG9jYWwgZmFpbHVyZXMKICAgICAgICBwcmludChmIkMzIHtsYWJlbH06IHsnb2snIGlmIG9rIGVsc2UgJ0ZBSUwnfSIpCiAgICAgICAgZmFpbHVyZXMgKz0gbm90IG9rCgogICAgcmVmZXJlbmNlID0ganNvbi5sb2FkcygocnVuIC8gInByZXN0YWdlLXJlZmVyZW5jZS5qc29uIikucmVhZF90ZXh0KCkpCiAgICBpdGVtID0gcmVmZXJlbmNlWyJwcml2YXRlX3ByZXBhcmUiXQogICAgcGF0aCA9IFBhdGgoaXRlbVsicGF0aCJdKQogICAgdG9rZW4gPSBoYXNobGliLnNoYTI1NigKICAgICAgICAoc3RyKHJ1bikgKyAiXDAiICsgInByZXN0YWdlIiArICJcMCIgKyByZWZlcmVuY2VbImNvbm5lY3RfaWQiXSkuZW5jb2RlKCkKICAgICkuaGV4ZGlnZXN0KCkKICAgIGV4cGVjdGVkID0gKHJ1bi5wYXJlbnQgLyAiLnJwZC1wcml2YXRlIiAvIHRva2VuIC8gInByZXN0YWdlLmpzb24iKS5yZXNvbHZlKCkKICAgIHByaW50KGYiQzMgcmVmZXJlbmNlIHNjaGVtYSB7cmVmZXJlbmNlLmdldCgnc2NoZW1hJyl9OyBzdGF0dXMge3JlZmVyZW5jZS5nZXQoJ3N0YXR1cycpfTsgIgogICAgICAgICAgZiJwcmVwYXJlX25hbWUge3JlZmVyZW5jZS5nZXQoJ3ByZXBhcmVfbmFtZScpfTsgcnVuIHtyZWZlcmVuY2UuZ2V0KCdydW4nKX0iKQogICAgcHJpbnQoZiJDMyBwcml2YXRlIHBhdGgge3BhdGh9IikKICAgIHByaW50KGYiQzMgcmVjb21wdXRlZCAgIHtleHBlY3RlZH0iKQogICAgY2hlY2soIjEgcmVmZXJlbmNlIG5hbWVzIHRoZSByZWNvbXB1dGVkIGxvY2F0aW9uIiwKICAgICAgICAgIHJlZmVyZW5jZS5nZXQoInNjaGVtYSIpID09ICJmZC1ycGQtcmVjby1wcml2YXRlLXByZXBhcmUtcmVmZXJlbmNlLzEiCiAgICAgICAgICBhbmQgcmVmZXJlbmNlLmdldCgicHJlcGFyZV9uYW1lIikgPT0gInByZXN0YWdlIgogICAgICAgICAgYW5kIHJlZmVyZW5jZS5nZXQoInJ1biIpID09IHN0cihydW4pCiAgICAgICAgICBhbmQgcGF0aC5yZXNvbHZlKCkgPT0gZXhwZWN0ZWQpCiAgICBjaGVjaygiMiB1bmRlciBST09ULy5ycGQtcHJpdmF0ZSBhbmQgbm90IHVuZGVyIHRoZSBydW4iLAogICAgICAgICAgKHJvb3QgLyAiLnJwZC1wcml2YXRlIikgaW4gcGF0aC5yZXNvbHZlKCkucGFyZW50cyBhbmQgcnVuIG5vdCBpbiBwYXRoLnJlc29sdmUoKS5wYXJlbnRzKQogICAgaW5mbywgcGFyZW50ID0gb3MubHN0YXQocGF0aCksIG9zLmxzdGF0KHBhdGgucGFyZW50KQogICAgcHJpbnQoZiJDMyByZWNvcmQgbW9kZSB7c3RhdC5maWxlbW9kZShpbmZvLnN0X21vZGUpfSB1aWQge2luZm8uc3RfdWlkfTsgIgogICAgICAgICAgZiJkaXJlY3RvcnkgbW9kZSB7c3RhdC5maWxlbW9kZShwYXJlbnQuc3RfbW9kZSl9IHVpZCB7cGFyZW50LnN0X3VpZH07IHRoaXMgdWlkIHtvcy5nZXR1aWQoKX0iKQogICAgY2hlY2soIjMgb3duZXItb25seSBmaWxlIGFuZCBkaXJlY3RvcnkiLAogICAgICAgICAgc3RhdC5TX0lTUkVHKGluZm8uc3RfbW9kZSkgYW5kIHN0YXQuU19JU0RJUihwYXJlbnQuc3RfbW9kZSkKICAgICAgICAgIGFuZCBpbmZvLnN0X3VpZCA9PSBvcy5nZXR1aWQoKSBhbmQgcGFyZW50LnN0X3VpZCA9PSBvcy5nZXR1aWQoKQogICAgICAgICAgYW5kIGluZm8uc3RfbW9kZSAmIDBvMDc3ID09IDAgYW5kIHBhcmVudC5zdF9tb2RlICYgMG8wNzcgPT0gMCkKICAgIGRhdGEgPSBwYXRoLnJlYWRfYnl0ZXMoKQogICAgZGlnZXN0ID0gaGFzaGxpYi5zaGEyNTYoZGF0YSkuaGV4ZGlnZXN0KCkKICAgIHJlY29yZCA9IGpzb24ubG9hZHMoZGF0YSkKICAgIGNvdW50ID0gbGVuKHJlY29yZC5nZXQoImVudmlyb25tZW50X3NuYXBzaG90Iiwge30pLmdldCgiZmluZ2VycHJpbnRzIiwge30pKQogICAgcHJpbnQoZiJDMyByZWNvcmQgc2hhMjU2IHtkaWdlc3R9IChyZWZlcmVuY2Uge2l0ZW0uZ2V0KCdzaGEyNTYnKX0pOyBlbnZpcm9ubWVudCBmaW5nZXJwcmludHMge2NvdW50fSBrZXlzIikKICAgIGNoZWNrKCI0IGRpZ2VzdCBlcXVhbHMgdGhlIHJlZmVyZW5jZSBhbmQgdGhlIHJlY29yZCBjYXJyaWVzIHRoZSBmaW5nZXJwcmludHMiLAogICAgICAgICAgZGlnZXN0ID09IGl0ZW0uZ2V0KCJzaGEyNTYiKSBhbmQgY291bnQgPiAwKQogICAgZW50cmllcyA9IFtdCiAgICBmb3IgZGlycGF0aCwgZGlybmFtZXMsIGZpbGVuYW1lcyBpbiBvcy53YWxrKHJvb3QgLyAiLnJwZC1wcml2YXRlIik6CiAgICAgICAgZGlybmFtZXMuc29ydCgpCiAgICAgICAgZm9yIG5hbWUgaW4gc29ydGVkKGRpcm5hbWVzKSArIHNvcnRlZChmaWxlbmFtZXMpOgogICAgICAgICAgICBmdWxsID0gUGF0aChkaXJwYXRoKSAvIG5hbWUKICAgICAgICAgICAgc3QgPSBvcy5sc3RhdChmdWxsKQogICAgICAgICAgICBlbnRyaWVzLmFwcGVuZCgoc3RhdC5maWxlbW9kZShzdC5zdF9tb2RlKSwgc3RyKGZ1bGwucmVsYXRpdmVfdG8ocm9vdCkpKSkKICAgIGZvciBtb2RlLCByZWwgaW4gZW50cmllczoKICAgICAgICBwcmludChmIkMzIHByaXZhdGUgZW50cnkge21vZGV9IHtyZWx9IikKICAgIGZpbGVzID0gW3JlbCBmb3IgbW9kZSwgcmVsIGluIGVudHJpZXMgaWYgbW9kZS5zdGFydHN3aXRoKCItIildCiAgICBjaGVjaygiNSAucnBkLXByaXZhdGUgaG9sZHMgZXhhY3RseSB0aGUgb25lIHJlY29yZCIsCiAgICAgICAgICBmaWxlcyA9PSBbc3RyKHBhdGgucmVzb2x2ZSgpLnJlbGF0aXZlX3RvKHJvb3QpKV0gYW5kIGFsbChtWzBdIGluICItZCIgZm9yIG0sIF8gaW4gZW50cmllcykpCiAgICBsZWFrZWQgPSBbc3RyKHApIGZvciBwIGluIHNlbmQKICAgICAgICAgICAgICBpZiAiLnJwZC1wcml2YXRlIiBpbiBwLnJlc29sdmUoKS5wYXJ0cyBvciBoYXNobGliLnNoYTI1NihwLnJlYWRfYnl0ZXMoKSkuaGV4ZGlnZXN0KCkgPT0gZGlnZXN0XQogICAgcHJpbnQoZiJDMyBzZW5kIGZpbGVzIGV4YW1pbmVkIHtsZW4oc2VuZCl9OyB1bmRlciAucnBkLXByaXZhdGUgb3IgZXF1YWwgdG8gdGhlIHJlY29yZDoge2xlYWtlZH0iKQogICAgY2hlY2soIjYgbm90aGluZyBvbiB0aGUgc2VuZCBsaXN0IGlzIHRoZSByZWNvcmQiLCBub3QgbGVha2VkKQogICAgcHJpbnQoZiJDMyBDSEVDSzogeydQQVNTJyBpZiBmYWlsdXJlcyA9PSAwIGVsc2UgJ0ZBSUwnfSIpCiAgICByZXR1cm4gMCBpZiBmYWlsdXJlcyA9PSAwIGVsc2UgMQoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBzeXMuZXhpdChtYWluKCkpCg==' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/c3_check.py
printf '%s' 'IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJDaGVjayB0aGF0IG5vIGVudmlyb25tZW50LXZhbHVlIGZpbmdlcnByaW50IGZyb20gdGhlIGNhbm9uaWNhbCBwcmVwYXJlIHJlY29yZCByZWFjaGVzIGEgZmlsZSBib3VuZCBmb3IgdGhlIHJlcG8uCgpSZXJ1biA0IChzZWNvbmQgbGluZSBvZiBkZWZlbmNlIGJlaGluZCB0aGUgY29kZSdzIEMzKTogUkFXIGlzIHRoZSBvd25lci1vbmx5IGNhbm9uaWNhbCByZWNvcmQgb3V0c2lkZSB0aGUgcnVuOyBWSUVXCmlzIHRoZSBjb2RlJ3Mgb3duIHB1YmxpYyBwcmVwYXJlIHZpZXcgaW4gdGhlIHJ1biAocHJvbG9ndWUtcHJlcGFyZS5qc29uIG9uIFBBU1MsIHByb2xvZ3VlLXByZXBhcmUuU1RPUC5qc29uIG9uIGEKU1RPUCksIG9yIE5PTkUgd2hlbiB0aGUgY29kZSB3cm90ZSBub25lLiBDaGVja3MsIGVhY2ggcmVjb3JkZWQ6CiAgMS4gdGhlIHZpZXcgaGFzIG5vIGVudmlyb25tZW50X3NuYXBzaG90LmZpbmdlcnByaW50cyBtYXA7CiAgMi4gbm8gNjQtaGV4IHN0cmluZyBhcHBlYXJzIGFueXdoZXJlIHVuZGVyIHRoZSB2aWV3J3MgZW52aXJvbm1lbnRfc25hcHNob3Qgb3IgZW52aXJvbm1lbnRfYWZ0ZXJfc2V0dXA7CiAgMy4gbm8gZmluZ2VycHJpbnQgdmFsdWUgZnJvbSB0aGUgcmF3IHJlY29yZCBhcHBlYXJzIGluIHRoZSB2aWV3LCBvciBpbiBhbnkgb3RoZXIgbGlzdGVkIGZpbGUuIFRoZSBmaW5nZXJwcmludCBvZgogICAgIHRoZSBlbXB0eSBzdHJpbmcgKGEgcHVibGljIGNvbnN0YW50KSBpcyBjb3VudGVkIGFwYXJ0OiBpbiB0aGUgdmlldyBpdCBmYWlscywgZWxzZXdoZXJlIGl0IGlzIHJlcG9ydGVkIG9ubHk7CiAgNC4gZXZlcnkgNjQtaGV4IHN0cmluZyBlbHNld2hlcmUgaW4gdGhlIHZpZXcgaXMgbGlzdGVkIGJ5IGl0cyBKU09OIHBhdGgsIGZvciB0aGUgcmVjb3JkOwogIDUuIG5vIGtleSBuYW1lZCAiZmluZ2VycHJpbnRzIiBhcHBlYXJzIGF0IGFueSBkZXB0aCBpbiB0aGUgdmlldyBvciBpbiBhbnkgb3RoZXIgbGlzdGVkIGZpbGUgdGhhdCBwYXJzZXMgYXMgSlNPTi4KV2l0aCBWSUVXIE5PTkUsIGNoZWNrcyAxLCAyIGFuZCA0IGFyZSByZWNvcmRlZCBhcyBub3QgYXBwbGljYWJsZTsgMyBhbmQgNSBydW4gb24gdGhlIG90aGVyIGZpbGVzLgpQcmludHMgQ0hFQ0sgbGluZXMgYW5kIGEgZmluYWwgdmVyZGljdDsgZXhpdHMgMCBvbiBQQVNTLCAxIG9uIEZBSUwuCgp1c2FnZTogY2hlY2tfcmVkYWN0aW9uLnB5IFJBV19QUkVQQVJFIFZJRVd8Tk9ORSBbT1RIRVJfRklMRSAuLi5dCiIiIgoKZnJvbSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5vdGF0aW9ucwoKaW1wb3J0IGhhc2hsaWIKaW1wb3J0IGpzb24KaW1wb3J0IHJlCmltcG9ydCBzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgpIRVg2NCA9IHJlLmNvbXBpbGUociIoPzwhWzAtOWEtZkEtRl0pWzAtOWEtZkEtRl17NjR9KD8hWzAtOWEtZkEtRl0pIikKRU1QVFkgPSBoYXNobGliLnNoYTI1NihiIiIpLmhleGRpZ2VzdCgpCkVOVl9TRUNUSU9OUyA9ICgiZW52aXJvbm1lbnRfc25hcHNob3QiLCAiZW52aXJvbm1lbnRfYWZ0ZXJfc2V0dXAiKQoKCmRlZiB3YWxrKG5vZGUsIHBhdGg9IiIpOgogICAgIiIiWWllbGQgKGpzb25fcGF0aCwgdGV4dCkgZm9yIGV2ZXJ5IGtleSBhbmQgc3RyaW5nIHZhbHVlLiIiIgogICAgaWYgaXNpbnN0YW5jZShub2RlLCBkaWN0KToKICAgICAgICBmb3Iga2V5LCB2YWx1ZSBpbiBub2RlLml0ZW1zKCk6CiAgICAgICAgICAgIHlpZWxkIGYie3BhdGh9L3trZXl9I2tleSIsIHN0cihrZXkpCiAgICAgICAgICAgIHlpZWxkIGZyb20gd2Fsayh2YWx1ZSwgZiJ7cGF0aH0ve2tleX0iKQogICAgZWxpZiBpc2luc3RhbmNlKG5vZGUsIGxpc3QpOgogICAgICAgIGZvciBpbmRleCwgdmFsdWUgaW4gZW51bWVyYXRlKG5vZGUpOgogICAgICAgICAgICB5aWVsZCBmcm9tIHdhbGsodmFsdWUsIGYie3BhdGh9W3tpbmRleH1dIikKICAgIGVsaWYgaXNpbnN0YW5jZShub2RlLCBzdHIpOgogICAgICAgIHlpZWxkIHBhdGgsIG5vZGUKCgpkZWYgbWFpbigpIC0+IGludDoKICAgIHJhdyA9IGpzb24ubG9hZHMoUGF0aChzeXMuYXJndlsxXSkucmVhZF90ZXh0KCkpCiAgICB2aWV3X3BhdGggPSBOb25lIGlmIHN5cy5hcmd2WzJdID09ICJOT05FIiBlbHNlIFBhdGgoc3lzLmFyZ3ZbMl0pCiAgICBvdGhlcnMgPSBbUGF0aChwKSBmb3IgcCBpbiBzeXMuYXJndlszOl1dCiAgICBmaW5nZXJwcmludHMgPSByYXdbImVudmlyb25tZW50X3NuYXBzaG90Il1bImZpbmdlcnByaW50cyJdCiAgICBieV92YWx1ZTogZGljdFtzdHIsIGxpc3Rbc3RyXV0gPSB7fQogICAgZm9yIGtleSwgdmFsdWUgaW4gZmluZ2VycHJpbnRzLml0ZW1zKCk6CiAgICAgICAgYnlfdmFsdWUuc2V0ZGVmYXVsdCh2YWx1ZS5sb3dlcigpLCBbXSkuYXBwZW5kKGtleSkKICAgIGZhaWx1cmVzID0gMAogICAgcHJpbnQoZiJDSEVDSzogcmF3IGZpbmdlcnByaW50cyB7bGVuKGZpbmdlcnByaW50cyl9IGtleXMsIHtsZW4oYnlfdmFsdWUpfSBkaXN0aW5jdCB2YWx1ZXMiKQogICAgcHJpbnQoZiJDSEVDSzogdmlldyB7dmlld19wYXRoIGlmIHZpZXdfcGF0aCBlbHNlICdOT05FICh0aGUgY29kZSB3cm90ZSBubyBwdWJsaWMgcHJlcGFyZSB2aWV3KSd9IikKCiAgICBpZiB2aWV3X3BhdGggaXMgbm90IE5vbmU6CiAgICAgICAgdmlldyA9IGpzb24ubG9hZHModmlld19wYXRoLnJlYWRfdGV4dCgpKQogICAgICAgIHByZXNlbnQgPSAiZmluZ2VycHJpbnRzIiBpbiB2aWV3LmdldCgiZW52aXJvbm1lbnRfc25hcHNob3QiLCB7fSkKICAgICAgICBwcmludChmIkNIRUNLIDEgdmlldyBlbnZpcm9ubWVudF9zbmFwc2hvdC5maW5nZXJwcmludHMgcHJlc2VudDoge3ByZXNlbnR9IikKICAgICAgICBmYWlsdXJlcyArPSBwcmVzZW50CiAgICAgICAgZW52X2hleCA9IFsKICAgICAgICAgICAgKHBhdGgsIG1hdGNoKQogICAgICAgICAgICBmb3IgcGF0aCwgdGV4dCBpbiB3YWxrKHZpZXcpCiAgICAgICAgICAgIGlmIHBhdGgubHN0cmlwKCIvIikuc3BsaXQoIi8iKVswXSBpbiBFTlZfU0VDVElPTlMKICAgICAgICAgICAgZm9yIG1hdGNoIGluIEhFWDY0LmZpbmRhbGwodGV4dCkKICAgICAgICBdCiAgICAgICAgcHJpbnQoZiJDSEVDSyAyIDY0LWhleCBzdHJpbmdzIHVuZGVyIHsnLycuam9pbihFTlZfU0VDVElPTlMpfSBpbiB0aGUgdmlldzoge2xlbihlbnZfaGV4KX0iKQogICAgICAgIGZvciBwYXRoLCBfIGluIGVudl9oZXg6CiAgICAgICAgICAgIHByaW50KGYiICBhdCB7cGF0aH0iKQogICAgICAgIGZhaWx1cmVzICs9IGJvb2woZW52X2hleCkKICAgIGVsc2U6CiAgICAgICAgcHJpbnQoIkNIRUNLIDEgbm90IGFwcGxpY2FibGUgKG5vIHZpZXcpIikKICAgICAgICBwcmludCgiQ0hFQ0sgMiBub3QgYXBwbGljYWJsZSAobm8gdmlldykiKQoKICAgIGZvciB0YXJnZXQgaW4gKFt2aWV3X3BhdGhdIGlmIHZpZXdfcGF0aCBlbHNlIFtdKSArIG90aGVyczoKICAgICAgICB0ZXh0ID0gdGFyZ2V0LnJlYWRfdGV4dChlcnJvcnM9InJlcGxhY2UiKS5sb3dlcigpCiAgICAgICAgaGl0cyA9IHNvcnRlZCh2YWx1ZSBmb3IgdmFsdWUgaW4gYnlfdmFsdWUgaWYgdmFsdWUgaW4gdGV4dCkKICAgICAgICBzZWNyZXQgPSBbdmFsdWUgZm9yIHZhbHVlIGluIGhpdHMgaWYgdmFsdWUgIT0gRU1QVFldCiAgICAgICAgZW1wdHkgPSBFTVBUWSBpbiBoaXRzCiAgICAgICAgcHJpbnQoCiAgICAgICAgICAgIGYiQ0hFQ0sgMyB7dGFyZ2V0Lm5hbWV9OiBmaW5nZXJwcmludCB2YWx1ZXMgZm91bmQge2xlbihzZWNyZXQpfSIKICAgICAgICAgICAgZiI7IGVtcHR5LXN0cmluZyBmaW5nZXJwcmludCBmb3VuZCB7ZW1wdHl9IgogICAgICAgICkKICAgICAgICBmb3IgdmFsdWUgaW4gc2VjcmV0OgogICAgICAgICAgICBwcmludChmIiAgZmluZ2VycHJpbnQgb2Yga2V5cyB7c29ydGVkKGJ5X3ZhbHVlW3ZhbHVlXSl9IikKICAgICAgICBmYWlsdXJlcyArPSBib29sKHNlY3JldCkgb3IgKGVtcHR5IGFuZCB0YXJnZXQgPT0gdmlld19wYXRoKQoKICAgIGlmIHZpZXdfcGF0aCBpcyBub3QgTm9uZToKICAgICAgICBlbHNld2hlcmUgPSBbCiAgICAgICAgICAgIChwYXRoLCBtYXRjaCkKICAgICAgICAgICAgZm9yIHBhdGgsIHRleHQgaW4gd2Fsayh2aWV3KQogICAgICAgICAgICBpZiBwYXRoLmxzdHJpcCgiLyIpLnNwbGl0KCIvIilbMF0gbm90IGluIEVOVl9TRUNUSU9OUwogICAgICAgICAgICBmb3IgbWF0Y2ggaW4gSEVYNjQuZmluZGFsbCh0ZXh0KQogICAgICAgIF0KICAgICAgICBwcmludChmIkNIRUNLIDQgb3RoZXIgNjQtaGV4IHN0cmluZ3MgaW4gdGhlIHZpZXcgKHJlY29yZCBvbmx5KToge2xlbihlbHNld2hlcmUpfSIpCiAgICAgICAgZm9yIHBhdGgsIG1hdGNoIGluIGVsc2V3aGVyZToKICAgICAgICAgICAgcHJpbnQoZiIgIHtwYXRofSB7bWF0Y2h9IikKICAgIGVsc2U6CiAgICAgICAgcHJpbnQoIkNIRUNLIDQgbm90IGFwcGxpY2FibGUgKG5vIHZpZXcpIikKCiAgICBmb3IgdGFyZ2V0IGluIChbdmlld19wYXRoXSBpZiB2aWV3X3BhdGggZWxzZSBbXSkgKyBvdGhlcnM6CiAgICAgICAgdHJ5OgogICAgICAgICAgICBub2RlID0ganNvbi5sb2Fkcyh0YXJnZXQucmVhZF90ZXh0KCkpCiAgICAgICAgZXhjZXB0IChWYWx1ZUVycm9yLCBVbmljb2RlRGVjb2RlRXJyb3IpOgogICAgICAgICAgICBjb250aW51ZQogICAgICAgIGtleXMgPSBbcGF0aCBmb3IgcGF0aCwgdGV4dCBpbiB3YWxrKG5vZGUpIGlmIHBhdGguZW5kc3dpdGgoIiNrZXkiKSBhbmQgdGV4dCA9PSAiZmluZ2VycHJpbnRzIl0KICAgICAgICBwcmludChmIkNIRUNLIDUge3RhcmdldC5uYW1lfToga2V5cyBuYW1lZCBmaW5nZXJwcmludHMge2xlbihrZXlzKX0iKQogICAgICAgIGZvciBwYXRoIGluIGtleXM6CiAgICAgICAgICAgIHByaW50KGYiICBhdCB7cGF0aH0iKQogICAgICAgIGZhaWx1cmVzICs9IGJvb2woa2V5cykKCiAgICB2ZXJkaWN0ID0gIlBBU1MiIGlmIGZhaWx1cmVzID09IDAgZWxzZSAiRkFJTCIKICAgIHByaW50KGYiUkVEQUNUSU9OIENIRUNLOiB7dmVyZGljdH0iKQogICAgcmV0dXJuIDAgaWYgZmFpbHVyZXMgPT0gMCBlbHNlIDEKCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgogICAgc3lzLmV4aXQobWFpbigpKQo=' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/check_redaction.py
printf '%s' 'IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJXcml0ZSB0aGUgcHVibGljIHJlY29yZCBvZiB0aGUgb25lIHByb3RlY3RlZC1wYXRoIHJlYWQgKGNvdjJkJ3MgY29uZGl0aW9uLCBiaW5kaW5nIGJ5IHRoZSBkaXJlY3RvciwgMjAyNi0xMS0xMSkuCgpGcm9tIHRoZSBvd25lci1vbmx5IHByZXN0YWdlIHJlY29yZCBSQVcsIGZvciB0aGUgbGlzdGVkIGV4Y2VwdGlvbiAodGhlIE1QQVJBTUZJTEVTIGNvbnN0cmFpbnQgZmlsZSksIGNvcHkgaW50byBPVVQ6Cml0cyBvcmlnaW5hbCAoYXMgd3JpdHRlbiBhbmQgcmVzb2x2ZWQpLCB0aGUgc2hhMjU2IHByZXBhcmUgbWVhc3VyZWQsIHRoZSBzaGEyNTYgb2YgYm90aCBzdGFnZWQgY29waWVzIChyZWNvbXB1dGVkIGhlcmUKZnJvbSB0aGUgY29waWVzIHVuZGVyIHRoZSBydW4sIG5ldmVyIGZyb20gdGhlIG9yaWdpbmFsKSwgc3RhdF9iZWZvcmUgYW5kIHN0YXRfYWZ0ZXIgKGRldmljZSwgaW5vZGUsIGJ5dGVzLCBtdGltZV9ucywKYXRpbWVfbnMpIGFuZCB0aGUgVVRDIHN0YWdpbmcgd2luZG93IChjdXN0b2R5IGNvcHkoKTogb25lIHN0YXQtYnJhY2tldGVkIHN0YWdpbmcsIHdpdGggdHdvIE9fTk9BVElNRSByZWFkcykuCkl0IGFsc28gbGlzdHMgZXZlcnkgc3RhZ2VkIG9yaWdpbmFsIHRoYXQgb3ZlcmxhcHMgYSBwcm90ZWN0ZWQgcGF0aCBvZiB0aGUgY29uZmlnLiBPbmx5IHRoZSBleGNlcHRpb24gbWF5LgpOb3RoaW5nIGZyb20gdGhlIGVudmlyb25tZW50IHNlY3Rpb25zIG9mIFJBVyBpcyBjb3BpZWQuIEV4aXRzIDAgb24gUEFTUywgMSBvbiBGQUlMOyBPVVQgaXMgd3JpdHRlbiBlaXRoZXIgd2F5LgoKdXNhZ2U6IHByb3RlY3RlZF9yZWFkLnB5IFJBVyBDT05GSUcgT1VUCiIiIgoKZnJvbSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5vdGF0aW9ucwoKaW1wb3J0IGRhdGV0aW1lCmltcG9ydCBoYXNobGliCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKRVhDRVBUSU9OID0gKAogICAgIi9wc2NyYXRjaC9zZC9qL2pvc2VwaHJiL01JTkVSdkEtT21uaUZvbGQvTUlORVJ2QTEwMS9vcHQvZXRjL01QYXJhbUZpbGVzL2RhdGEvRmx1eENvbnN0cmFpbnRzLyIKICAgICJzb3J0ZWRfTnVFQ29uc3RyYWludF9GSENfUkhDX0lNRC50eHQiCikKUkVMQVRJVkUgPSAiRmx1eENvbnN0cmFpbnRzL3NvcnRlZF9OdUVDb25zdHJhaW50X0ZIQ19SSENfSU1ELnR4dCIKU1RBVF9GSUVMRFMgPSB7ImRldmljZSIsICJpbm9kZSIsICJieXRlcyIsICJtdGltZV9ucyIsICJhdGltZV9ucyJ9CgoKZGVmIGZvcm1zKHBhdGg6IHN0cikgLT4gc2V0W3N0cl06CiAgICByZXR1cm4ge29zLnBhdGgubm9ybXBhdGgocGF0aCksIG9zLnBhdGgucmVhbHBhdGgocGF0aCl9CgoKZGVmIG92ZXJsYXBzKGE6IHN0ciwgYjogc3RyKSAtPiBib29sOgogICAgcmV0dXJuIGFueSgKICAgICAgICB4ID09IHkgb3IgeC5zdGFydHN3aXRoKHkucnN0cmlwKCIvIikgKyAiLyIpIG9yIHkuc3RhcnRzd2l0aCh4LnJzdHJpcCgiLyIpICsgIi8iKQogICAgICAgIGZvciB4IGluIGZvcm1zKGEpCiAgICAgICAgZm9yIHkgaW4gZm9ybXMoYikKICAgICkKCgpkZWYgc2hhMjU2KHBhdGg6IHN0cikgLT4gc3RyIHwgTm9uZToKICAgIHRyeToKICAgICAgICByZXR1cm4gaGFzaGxpYi5zaGEyNTYoUGF0aChwYXRoKS5yZWFkX2J5dGVzKCkpLmhleGRpZ2VzdCgpCiAgICBleGNlcHQgT1NFcnJvcjoKICAgICAgICByZXR1cm4gTm9uZQoKCmRlZiB1dGMobnM6IG9iamVjdCkgLT4gc3RyIHwgTm9uZToKICAgIGlmIG5vdCBpc2luc3RhbmNlKG5zLCBpbnQpOgogICAgICAgIHJldHVybiBOb25lCiAgICByZXR1cm4gZGF0ZXRpbWUuZGF0ZXRpbWUuZnJvbXRpbWVzdGFtcChucyAvIDFlOSwgZGF0ZXRpbWUudGltZXpvbmUudXRjKS5pc29mb3JtYXQodGltZXNwZWM9Im1pY3Jvc2Vjb25kcyIpCgoKZGVmIG1haW4oKSAtPiBpbnQ6CiAgICByYXcgPSBqc29uLmxvYWRzKFBhdGgoc3lzLmFyZ3ZbMV0pLnJlYWRfdGV4dCgpKQogICAgcHJvdGVjdGVkID0ganNvbi5sb2FkcyhQYXRoKHN5cy5hcmd2WzJdKS5yZWFkX3RleHQoKSlbImNvdjJkX3Byb3RlY3RlZF9wYXRocyJdCiAgICBvdXQgPSBQYXRoKHN5cy5hcmd2WzNdKQogICAgcHJvYmxlbXM6IGxpc3Rbc3RyXSA9IFtdCiAgICBmaWxlcyA9IHJhdy5nZXQoImZpbGVzIiwge30pCiAgICBkZXBlbmRlbmNpZXMgPSBbCiAgICAgICAgaXRlbQogICAgICAgIGZvciBpdGVtIGluIHJhdy5nZXQoIm1hdF9kZXBlbmRlbmNpZXMiLCBbXSkKICAgICAgICBpZiBpdGVtLmdldCgiZW52aXJvbm1lbnRfa2V5IikgPT0gIk1QQVJBTUZJTEVTIiBhbmQgaXRlbS5nZXQoInJlbGF0aXZlX3BhdGgiKSA9PSBSRUxBVElWRQogICAgXQogICAgaWYgbGVuKGRlcGVuZGVuY2llcykgIT0gMToKICAgICAgICBwcm9ibGVtcy5hcHBlbmQoZiJleGNlcHRpb24gZGVwZW5kZW5jeSBlbnRyaWVzOiB7bGVuKGRlcGVuZGVuY2llcyl9LCBleHBlY3RlZCAxIikKICAgIGVudHJ5ID0gZGVwZW5kZW5jaWVzWzBdIGlmIGRlcGVuZGVuY2llcyBlbHNlIHt9CiAgICBvcmlnaW5hbCA9IGVudHJ5LmdldCgib3JpZ2luYWwiKQogICAgaXRlbSA9IGZpbGVzLmdldChvcmlnaW5hbCwge30pIGlmIGlzaW5zdGFuY2Uob3JpZ2luYWwsIHN0cikgZWxzZSB7fQogICAgaWYgbm90IGl0ZW06CiAgICAgICAgcHJvYmxlbXMuYXBwZW5kKCJ0aGUgZXhjZXB0aW9uJ3Mgb3JpZ2luYWwgaXMgbm90IGFtb25nIHRoZSBzdGFnZWQgZmlsZXMiKQogICAgaWYgaXNpbnN0YW5jZShvcmlnaW5hbCwgc3RyKSBhbmQgb3MucGF0aC5yZWFscGF0aChFWENFUFRJT04pICE9IG9zLnBhdGgucmVhbHBhdGgob3JpZ2luYWwpOgogICAgICAgIHByb2JsZW1zLmFwcGVuZChmInRoZSBzdGFnZWQgb3JpZ2luYWwge29yaWdpbmFsfSBkb2VzIG5vdCByZXNvbHZlIHRvIHRoZSBsaXN0ZWQgZXhjZXB0aW9uIikKICAgIGZvciBzaWRlIGluICgic3RhdF9iZWZvcmUiLCAic3RhdF9hZnRlciIpOgogICAgICAgIHZhbHVlID0gaXRlbS5nZXQoc2lkZSkKICAgICAgICBpZiBub3QgKGlzaW5zdGFuY2UodmFsdWUsIGRpY3QpIGFuZCBzZXQodmFsdWUpID09IFNUQVRfRklFTERTIGFuZCBhbGwoaXNpbnN0YW5jZSh2LCBpbnQpIGZvciB2IGluIHZhbHVlLnZhbHVlcygpKSk6CiAgICAgICAgICAgIHByb2JsZW1zLmFwcGVuZChmIntzaWRlfSBpcyBtaXNzaW5nIG9yIGxhY2tzIHRoZSBmaXZlIGZpZWxkcyIpCiAgICBpZiBpdGVtLmdldCgic3RhdF9iZWZvcmUiKSAhPSBpdGVtLmdldCgic3RhdF9hZnRlciIpOgogICAgICAgIHByb2JsZW1zLmFwcGVuZCgic3RhdF9iZWZvcmUgZGlmZmVycyBmcm9tIHN0YXRfYWZ0ZXIiKQogICAgd2luZG93ID0gaXRlbS5nZXQoInN0YWdpbmdfdXRjX25zIikKICAgIGlmIG5vdCAoCiAgICAgICAgaXNpbnN0YW5jZSh3aW5kb3csIGRpY3QpCiAgICAgICAgYW5kIHNldCh3aW5kb3cpID09IHsic3RhcnRlZCIsICJlbmRlZCJ9CiAgICAgICAgYW5kIGFsbChpc2luc3RhbmNlKHdpbmRvd1trXSwgaW50KSBmb3IgayBpbiAoInN0YXJ0ZWQiLCAiZW5kZWQiKSkKICAgICAgICBhbmQgd2luZG93WyJzdGFydGVkIl0gPD0gd2luZG93WyJlbmRlZCJdCiAgICApOgogICAgICAgIHByb2JsZW1zLmFwcGVuZCgic3RhZ2luZ191dGNfbnMgaXMgbWlzc2luZyBvciBtYWxmb3JtZWQiKQogICAgICAgIHdpbmRvdyA9IHt9CiAgICBtZWFzdXJlZCA9IGl0ZW0uZ2V0KCJzaGEyNTYiKQogICAgY29waWVzID0ge3BhdGg6IHNoYTI1NihwYXRoKSBmb3IgcGF0aCBpbiAoaXRlbS5nZXQoInN0YWdlZCIpLCBlbnRyeS5nZXQoInN0YWdlZCIpKSBpZiBpc2luc3RhbmNlKHBhdGgsIHN0cil9CiAgICBpZiBsZW4oY29waWVzKSAhPSAyIG9yIGFueSh2YWx1ZSAhPSBtZWFzdXJlZCBmb3IgdmFsdWUgaW4gY29waWVzLnZhbHVlcygpKToKICAgICAgICBwcm9ibGVtcy5hcHBlbmQoImEgc3RhZ2VkIGNvcHkncyBzaGEyNTYgZGlmZmVycyBmcm9tIHRoZSBtZWFzdXJlZCBvcmlnaW5hbCdzLCBvciBhIGNvcHkgaXMgbWlzc2luZyIpCiAgICBpZiBlbnRyeS5nZXQoInNoYTI1NiIpICE9IG1lYXN1cmVkOgogICAgICAgIHByb2JsZW1zLmFwcGVuZCgidGhlIGRlcGVuZGVuY3kgZW50cnkncyBzaGEyNTYgZGlmZmVycyBmcm9tIHRoZSBzdGFnZWQgZmlsZSdzIikKICAgIG92ZXJsYXBwaW5nID0gc29ydGVkKAogICAgICAgIHtuYW1lIGZvciBuYW1lIGluIGZpbGVzIGZvciBwYXRoIGluIHByb3RlY3RlZCBpZiBvdmVybGFwcyhuYW1lLCBwYXRoKX0KICAgICkKICAgIG90aGVycyA9IFtuYW1lIGZvciBuYW1lIGluIG92ZXJsYXBwaW5nIGlmIG9zLnBhdGgucmVhbHBhdGgobmFtZSkgIT0gb3MucGF0aC5yZWFscGF0aChFWENFUFRJT04pXQogICAgaWYgb3RoZXJzOgogICAgICAgIHByb2JsZW1zLmFwcGVuZChmIm90aGVyIHN0YWdlZCBvcmlnaW5hbHMgb3ZlcmxhcCBwcm90ZWN0ZWQgcGF0aHM6IHtvdGhlcnN9IikKICAgIHJlY29yZCA9IHsKICAgICAgICAic2NoZW1hIjogInJwZC1mbHV4MS1wcm90ZWN0ZWQtcmVhZC8xIiwKICAgICAgICAic3RhdHVzIjogIlBBU1MiIGlmIG5vdCBwcm9ibGVtcyBlbHNlICJGQUlMIiwKICAgICAgICAicHJvYmxlbXMiOiBwcm9ibGVtcywKICAgICAgICAiZXhjZXB0aW9uX2FzX2xpc3RlZCI6IEVYQ0VQVElPTiwKICAgICAgICAib3JpZ2luYWxfcmVzb2x2ZWQiOiBvcmlnaW5hbCwKICAgICAgICAicmVhZHMiOiAib25lIHN0YXQtYnJhY2tldGVkIHN0YWdpbmcsIHdpdGggdHdvIE9fTk9BVElNRSByZWFkcyAoY3VzdG9keSBjb3B5KCk6IG5vYXRpbWVfZGlnZXN0LCB0aGVuIHN0YWdlX2NvcHkpIiwKICAgICAgICAic2hhMjU2X21lYXN1cmVkX2J5X3ByZXBhcmUiOiBtZWFzdXJlZCwKICAgICAgICAic3RhZ2VkX2NvcGllc19zaGEyNTYiOiBjb3BpZXMsCiAgICAgICAgInN0YXRfYmVmb3JlIjogaXRlbS5nZXQoInN0YXRfYmVmb3JlIiksCiAgICAgICAgInN0YXRfYWZ0ZXIiOiBpdGVtLmdldCgic3RhdF9hZnRlciIpLAogICAgICAgICJzdGFnaW5nX3V0Y19ucyI6IHdpbmRvdyBvciBOb25lLAogICAgICAgICJzdGFnaW5nX3V0YyI6IHtrOiB1dGModikgZm9yIGssIHYgaW4gd2luZG93Lml0ZW1zKCl9IGlmIHdpbmRvdyBlbHNlIE5vbmUsCiAgICAgICAgInN0YWdlZF9vcmlnaW5hbHMiOiBsZW4oZmlsZXMpLAogICAgICAgICJzdGFnZWRfb3JpZ2luYWxzX292ZXJsYXBwaW5nX3Byb3RlY3RlZCI6IG92ZXJsYXBwaW5nLAogICAgfQogICAgb3V0LndyaXRlX3RleHQoanNvbi5kdW1wcyhyZWNvcmQsIGluZGVudD0xLCBzb3J0X2tleXM9VHJ1ZSkgKyAiXG4iKQogICAgcHJpbnQoZiJQUk9URUNURUQgUkVBRDoge3JlY29yZFsnc3RhdHVzJ119IikKICAgIGZvciBsaW5lIGluIHByb2JsZW1zOgogICAgICAgIHByaW50KGYiICBwcm9ibGVtOiB7bGluZX0iKQogICAgcmV0dXJuIDAgaWYgbm90IHByb2JsZW1zIGVsc2UgMQoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBzeXMuZXhpdChtYWluKCkpCg==' | base64 -d > /dev/shm/limres-rpd-flux1-fetch/protected_read.py
for pair in "/dev/shm/limres-rpd-flux1-fetch/c3_check.py:$C3_SHA" "/dev/shm/limres-rpd-flux1-fetch/check_redaction.py:$CHECK_SHA" "/dev/shm/limres-rpd-flux1-fetch/protected_read.py:$PREAD_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 2. the factor products (kept on pscratch)"
for f in run/flux-factors-*.npz; do
  [ -f "$f" ] || { echo "no factor products"; break; }
  echo "product $(stat -c %s "$f") bytes sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"
done
if [ -f run/flux-extract.json ]; then
  "$MAT_PYTHON" -I -S -c '
import hashlib, json, sys
products = json.load(open(sys.argv[1])).get("factor_products", {})
bad = 0
for playlist, item in sorted(products.items()):
    try:
        got = hashlib.sha256(open(item["path"], "rb").read()).hexdigest()
    except OSError as error:
        got = "unreadable: " + str(error)
    ok = got == item.get("sha256")
    bad += not ok
    print("recorded", playlist, item.get("sha256"), "equal" if ok else "DIFFERS (" + got + ")", item.get("path"))
print("factor products recorded", len(products), "differing", bad)
' run/flux-extract.json
fi
echo "== 3. the protected read"
raw=NONE
prc=0
if [ -f run/prestage-reference.json ]; then
  raw=$("$MAT_PYTHON" -I -S -c 'import json,sys; print(json.load(open(sys.argv[1]))["private_prepare"]["path"])' run/prestage-reference.json)
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/protected_read.py "$raw" production-config.ready.json protected-read.json
  prc=$?
  echo "protected read rc=$prc"
elif [ -e .rpd-private ]; then
  echo "STOP: .rpd-private exists without run/prestage-reference.json; nothing is sent"; finish 7
else
  printf '%s\n' '{"schema": "rpd-flux1-protected-read/1", "status": "NOT_APPLICABLE", "problems": ["no private prestage record: prepare did not complete"]}' > protected-read.json
  echo "PROTECTED READ: not applicable (no private record)"
fi
cat protected-read.json
echo "== 4. the send list"
send=()
for f in job.id job-host.txt job.rc job.out job.err rpd_flux1_job.sh connect.log strace-probe.txt fence-overlap.txt exception-stat-outer.txt protected-read.json; do
  if [ -f "$f" ]; then send+=("$f"); else echo "absent (not sent): $f"; fi
done
while IFS= read -r f; do send+=("${f#./}"); done < <(find ./run ./run/real-mnv-check -maxdepth 1 -type f ! -name 'flux-factors-*.npz' 2>/dev/null | sort -u)
total=0
for f in "${send[@]}"; do
  case "$f" in *.rpd-private*|run/original-inputs/*|run/mat-data/*|run/prepare-check/*|run/tmp/*|clone/*|tools/*|run/flux-factors-*) echo "STOP: $f may not be sent"; finish 7 ;; esac
  b=$(stat -c %s "$f"); total=$((total + b)); echo "send $b $f"
done
echo "send files ${#send[@]}, bytes $total"
[ "$total" -le 67108864 ] || { echo "STOP: over 64 MiB; nothing is sent"; finish 7; }
abs=(); for f in "${send[@]}"; do abs+=("/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/$f"); done
echo "== 5. C3"
if [ "$raw" != NONE ]; then
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/c3_check.py /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 \
    /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run "${abs[@]}" > c3-check.txt 2>&1
  c3=$?
  cat c3-check.txt; echo "c3 check rc=$c3"
  [ "$c3" -eq 0 ] || { echo "STOP: the C3 check did not pass; nothing is sent"; finish 7; }
else
  echo "C3 not applicable: custody wrote no private record (no .rpd-private, no run/prestage-reference.json)" > c3-check.txt
  cat c3-check.txt
fi
echo "== 6. the redaction check"
if [ "$raw" != NONE ]; then
  "$MAT_PYTHON" -I -S /dev/shm/limres-rpd-flux1-fetch/check_redaction.py "$raw" NONE "${abs[@]}" \
    /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/c3-check.txt > redaction-check.txt 2>&1
  crc=$?
else
  hits=$(grep -l -F fingerprints "${abs[@]}")
  { echo "REDACTION CHECK not applicable: no private record exists"; echo "files naming fingerprints: [$hits]"; } > redaction-check.txt
  [ -z "$hits" ]; crc=$?
fi
cat redaction-check.txt; echo "check rc=$crc"
[ "$crc" -eq 0 ] || { echo "STOP: the redaction check did not pass; nothing is sent"; finish 7; }
echo "== 7. connect.log (checked)"
[ -f connect.log ] && cat connect.log
echo "== end connect.log"
send+=(c3-check.txt redaction-check.txt)
for f in "${send[@]}"; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
tar -cf - "${send[@]}" | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[0]}"
echo "left in place for the post-merge deletion: /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 (the factor products, the staged copies, the clone, the private record)"
[ "$prc" -eq 0 ] || { echo "PROTECTED READ FAILED: the records were sent; the failure is in protected-read.json"; finish 11; }
finish 0
