#!/bin/bash
# GNU-like strictness for `sha256sum -c FILE`: refuse a file with no properly formatted lines (GNU exits 1).
if [ "$1" = "-c" ] && [ -n "$2" ] && ! grep -qE '^[0-9a-f]{64}  ' "$2" 2>/dev/null; then
  echo "sha256sum: $2: no properly formatted checksum lines found" >&2; exit 1
fi
exec /sbin/sha256sum "$@"
