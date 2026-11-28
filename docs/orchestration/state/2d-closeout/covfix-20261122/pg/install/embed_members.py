"""embed_members.py -- write the record's G2111a-members.json into pg-install-g2111a.py's MEMBERS_JSON block.

Run: python3 -I -B embed_members.py   (prints changed or unchanged)
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEMBERS = HERE.parent / "record" / "G2111a-members.json"


def embed(script=HERE / "pg-install-g2111a.py"):
    src = script.read_text()
    block = "MEMBERS_JSON = r'''" + json.dumps(json.loads(MEMBERS.read_text()), indent=1, sort_keys=True) + "'''"
    new = re.sub(r"MEMBERS_JSON = r'''.*?'''", lambda m: block, src, count=1, flags=re.S)
    script.write_text(new)
    return new != src


if __name__ == "__main__":
    print("changed" if embed() else "unchanged")
