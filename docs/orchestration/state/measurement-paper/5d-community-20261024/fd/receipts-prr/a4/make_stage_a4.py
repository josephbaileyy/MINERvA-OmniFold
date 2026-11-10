"""Fill prr_stage_a4.sh.template after the A4 binding.
Usage: python3 make_stage_a4.py <M_A4 40hex> <bind_sha> <a4_sha> <sums file: 'sha  name', the six FD-PRR files at M_A4>
Writes prr_stage_a4.sh beside the template and prints its sha256 and size."""
import hashlib, sys
from pathlib import Path
H = Path(__file__).resolve().parent
M, BIND, A4, SUMS = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]).read_text().strip()
assert len(M) == 40 and len(BIND) == 64 and len(A4) == 64 and len(SUMS.splitlines()) == 6
t = (H / "prr_stage_a4.sh.template").read_text()
for k, v in (("@M@", M), ("@BIND_SHA@", BIND), ("@A4_SHA@", A4), ("@SUMS@", SUMS)):
    assert t.count(k) == 1, k
    t = t.replace(k, v)
assert "@" not in "".join(l for l in t.splitlines() if l.startswith(("M=", "A4_SHA=", "BIND_SHA=")))
(H / "prr_stage_a4.sh").write_text(t)
b = t.encode(); print(hashlib.sha256(b).hexdigest(), len(b), "prr_stage_a4.sh")
