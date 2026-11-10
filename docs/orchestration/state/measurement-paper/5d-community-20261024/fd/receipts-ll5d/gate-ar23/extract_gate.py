"""Write gate-<T>.fields.txt: the verdict-relevant fields of gate-<T>.json, verbatim, minus `receipt` (the
descriptive per-row pass, ~708 KB), `clip_prep` (stated in the README by path, size, sha256) and `atime.files`."""
import hashlib, json, sys
src, out = sys.argv[1], sys.argv[2]
raw = open(src, 'rb').read(); d = json.loads(raw)
keep = {k: v for k, v in d.items() if k not in ('receipt', 'clip_prep', 'atime')}
keep['atime'] = {'moved': d['atime']['moved'], 'files_tracked': len(d['atime']['files'])}
hdr = (f"# EXTRACT of {src.rsplit('/', 1)[-1]} (sha256 {hashlib.sha256(raw).hexdigest()}), made by extract_gate.py:\n"
       f"# every top-level key verbatim except `receipt` and `clip_prep` (omitted) and `atime` (reduced to `moved` and\n"
       f"# the count of files tracked). The full record stays on pscratch; see README.\n")
open(out, 'w').write(hdr + json.dumps(keep, indent=1, sort_keys=True) + "\n")
