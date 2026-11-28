#!/bin/bash
# Builds sidecar-probe.sh from sidecar_probe_remote.py: the reader is embedded as base64 (no here-document and no
# temporary file on the node) with its sha256 computed here by command; the node checks that sha256 before running it.
#   bash build_probe.sh      (in this directory; refuses if sidecar-probe.sh exists)
set -euo pipefail
cd "$(dirname "$0")"
[ ! -e sidecar-probe.sh ] || { echo "STOP: sidecar-probe.sh exists"; exit 2; }
SHA=$(shasum -a 256 < sidecar_probe_remote.py | cut -d' ' -f1)
PYB=$(base64 < sidecar_probe_remote.py | tr -d '\n')
cat > sidecar-probe.sh <<WRAP
#!/bin/bash
# RPD-RECO amendment 1's read-only sidecar probe, one login02 session:
#   ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'" < sidecar-probe.sh > probe.json 2> probe.err
# The reader (sidecar_probe_remote.py, sha256 $SHA) is embedded below as base64 and checked against its sha256 on the
# node. It lstats the 12 omnifiles and lat_zero (never opens them), and hashes only the sidecar through O_NOATIME.
# Writes nothing on the cluster. Exit 2: refused before any read; 9: a file missing or a check failed; 0: PASS.
stop() { echo "STOP: \$*" >&2; exit 2; }          # a fixed code: nothing inherited can turn a refusal into 0
h=\$(hostname) && [ "\$h" = login02 ] || stop "not login02 (\${h:-hostname failed})"
PYB='$PYB'
# the digest is of the raw decoded stream (no command substitution, which would drop trailing newlines or NULs)
s1=\$(printf '%s' "\$PYB" | base64 -d | sha256sum) && [ "\${s1%% *}" = $SHA ] || stop "reader sha \${s1%% *}"
py=\$(printf '%s' "\$PYB" | base64 -d) && [ -n "\$py" ] || stop "decode reader"
[ -x /usr/bin/python3 ] || stop "no /usr/bin/python3"
echo "probe start \$(date -u +%FT%TZ) on \$h; reader $SHA" >&2
/usr/bin/python3 -I -c "\$py" < /dev/null
rc=\$?
echo "probe end \$(date -u +%FT%TZ) rc=\$rc" >&2
exit \$rc
WRAP
bash -n sidecar-probe.sh
echo "reader           $SHA"
echo "sidecar-probe.sh $(shasum -a 256 < sidecar-probe.sh | cut -d' ' -f1)"
