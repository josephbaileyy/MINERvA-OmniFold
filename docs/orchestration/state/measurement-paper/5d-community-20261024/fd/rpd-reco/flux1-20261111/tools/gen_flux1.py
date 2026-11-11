"""Generate rpd_flux1_connect.sh and rpd_flux1_fetch.sh from their templates, embedding the config and the two tools."""

import base64
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1])  # the committed flux1-20261111 directory


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


cfg = (OUT / "production-config.ready.json").read_bytes()
c3 = (OUT / "tools/c3_check.py").read_bytes()
check = (OUT / "tools/check_redaction.py").read_bytes()
assert sha(cfg) == "cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b", sha(cfg)
assert sha(check) == "992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316"
assert b"${" not in cfg

connect = (HERE / "rpd_flux1_connect.template.sh").read_text()
assert connect.count("@@CONFIG_B64@@") == 1
connect = connect.replace("@@CONFIG_B64@@", base64.b64encode(cfg).decode())
fetch = (HERE / "rpd_flux1_fetch.template.sh").read_text()
for key, value in (
    ("@@C3_SHA@@", sha(c3)),
    ("@@C3_B64@@", base64.b64encode(c3).decode()),
    ("@@CHECK_B64@@", base64.b64encode(check).decode()),
):
    assert fetch.count(key) == 1, key
    fetch = fetch.replace(key, value)
for name, text in (("rpd_flux1_connect.sh", connect), ("rpd_flux1_fetch.sh", fetch)):
    assert "@@" not in text, name
    (OUT / name).write_text(text)
    print(sha(text.encode()), name)
print(sha(c3), "tools/c3_check.py")
launch = (HERE / "rpd_flux1_launch.template.sh").read_text()
for key, value in (("@@CONNECT_SHA@@", sha(connect.encode())), ("@@FETCH_SHA@@", sha(fetch.encode()))):
    assert launch.count(key) == 1, key
    launch = launch.replace(key, value)
assert "@@" not in launch
(OUT / "rpd_flux1_launch.sh").write_text(launch)
print(sha(launch.encode()), "rpd_flux1_launch.sh")
