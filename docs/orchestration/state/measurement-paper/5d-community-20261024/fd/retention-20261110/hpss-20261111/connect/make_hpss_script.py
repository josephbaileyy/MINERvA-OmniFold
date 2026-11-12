"""Build connect/hpss_atrisk.sh: the template with the list's sha256 filled in, then __LIST__ and the list."""
import hashlib, sys
tpl, lst, out = sys.argv[1:4]
L = open(lst, "rb").read()
t = open(tpl).read()
assert t.count("@LIST_SHA@") == 1 and t.endswith("exit 9\n")
open(out, "wb").write(t.replace("@LIST_SHA@", hashlib.sha256(L).hexdigest()).encode() + b"__LIST__\n" + L)
