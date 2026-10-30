"""Print the rated text around a quote: python3 -I ctx.py R22_DIR INPUT 'quote prefix' [chars]"""
import re
import sys
from pathlib import Path
d = Path(sys.argv[1]) / "gap" / "inputs" / sys.argv[2]
t = re.sub(r"\s+", " ", next(p for p in (d / "manuscript.txt", d / "chapter.txt") if p.exists()).read_text())
q = re.sub(r"\s+", " ", sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 500
i = t.find(q)
print(t[max(0, i - n):i + len(q) + n] if i >= 0 else "NOT FOUND")
