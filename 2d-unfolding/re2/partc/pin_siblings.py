"""Write the sha256 of re2c_analyze_periods.py and re2c_periods.py into the PINS of re2c_playlist_term.py and
re2c_combine.py (PT-01, CB-01). Run after editing either period copy; test_re2c.py fails if they are stale."""
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHA = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in ("re2c_analyze_periods.py", "re2c_periods.py")}
for target in ("re2c_playlist_term.py", "re2c_combine.py"):
    p = HERE / target
    s = p.read_text()
    for n, d in SHA.items():
        s, k = re.subn(r'(f"\{SCRIPTS\}/' + re.escape(n) + r'": ")[^"]*(")', r"\g<1>" + d + r"\2", s)
        assert k == 1, (target, n, k)
    p.write_text(s)
    print(target, SHA)
