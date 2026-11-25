#!/usr/bin/env python3
"""Stand-in sha256sum: a file (or stdin) whose content starts with 'STANDIN-PIN:<64 hex>' hashes to that pin; any other
content is hashed for real. Supports FILE..., stdin, and -c [--strict] [--quiet] SUMS, as the connect uses them."""
import hashlib, re, sys

def digest(data: bytes) -> str:
    m = re.match(rb"STANDIN-PIN:([0-9a-f]{64})", data)
    return m.group(1).decode() if m else hashlib.sha256(data).hexdigest()

args = sys.argv[1:]
if "-c" in args:
    strict = "--strict" in args; quiet = "--quiet" in args
    sums = [a for a in args if not a.startswith("-")][0]
    bad = malformed = 0
    for line in open(sums):
        m = re.match(r"^([0-9a-f]{64})  (.+)$", line.rstrip("\n"))
        if not m:
            malformed += 1; continue
        ok = digest(open(m.group(2), "rb").read()) == m.group(1)
        bad += not ok
        if not ok or not quiet:
            print(f"{m.group(2)}: {'OK' if ok else 'FAILED'}")
    sys.exit(1 if bad or (strict and malformed) else 0)
files = [a for a in args if not a.startswith("-")]
if not files:
    print(f"{digest(sys.stdin.buffer.read())}  -")
else:
    for f in files:
        print(f"{digest(open(f, 'rb').read())}  {f}")
