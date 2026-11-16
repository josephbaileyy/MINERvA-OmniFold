"""Generate the flux connect 1 scripts (revision 2) from their templates.

usage: python3 -I gen_flux1.py OUT_DIR S REPO [TOOLS_DIR]
  OUT_DIR  the committed flux1-20261111 directory (holds the config and tools/)
  S        the full sha of #848's code commit the job runs
  REPO     any checkout that holds commit S; the 11 pins are read from it with git show
"""

import base64
import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT, S, REPO = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
assert re.fullmatch(r"[0-9a-f]{40}", S), S
PINNED = (
    "nd-unfolding/fd_rpd_reco.py",
    "nd-unfolding/fd_rpd_reco_custody.py",
    "nd-unfolding/fd_rpd_inputs.py",
    "nd-unfolding/fd_rpd_reco_flux_connect.sh",
    "nd-unfolding/tests/fd_rpd_reco_mat_check.py",
    "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/"
    "flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root",
    "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/INPUTS.sha256",
    "nd-unfolding/pv-ladder/readouts/h2_definition.json",
    "docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/flux-pot-provenance-20261104/"
    "energy-spectrum-candidates.tsv",
    "MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h",
    "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/code-audit-fix-20261106/"
    "MAT-DATA-DEPENDENCIES.json",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fill(text: str, values: dict) -> str:
    for key, value in values.items():
        assert text.count(key) >= 1, key
        text = text.replace(key, value)
    assert "@@" not in text
    return text


pins = "\n".join(
    f"{sha(subprocess.run(['git', '-C', REPO, 'show', f'{S}:{p}'], capture_output=True, check=True).stdout)} {p}"
    for p in PINNED
)
cfg = (OUT / "production-config.ready.json").read_bytes()
TOOLS = Path(sys.argv[4]) if len(sys.argv) > 4 else OUT / "tools"  # a 4th argument: the test harness's tools copy
tools = {name: (TOOLS / name).read_bytes() for name in ("c3_check.py", "check_redaction.py", "fence_overlap.py", "protected_read.py")}
assert sha(cfg) == "cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b", sha(cfg)
assert sha(tools["check_redaction.py"]) == "992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316"
assert b"${" not in cfg
b64 = lambda data: base64.b64encode(data).decode()  # noqa: E731

job = fill((HERE / "rpd_flux1_job.template.sh").read_text(), {"@@S@@": S, "@@PINS@@": pins})
assert "\nJOB\n" not in job
connect = fill(
    (HERE / "rpd_flux1_connect.template.sh").read_text(),
    {
        "@@JOB@@": job.rstrip("\n"),
        "@@S8@@": S[:8],
        "@@S@@": S,
        "@@PINS@@": pins,
        "@@CONFIG_B64@@": b64(cfg),
        "@@FENCE_SHA@@": sha(tools["fence_overlap.py"]),
        "@@FENCE_B64@@": b64(tools["fence_overlap.py"]),
    },
)
fetch = fill(
    (HERE / "rpd_flux1_fetch.template.sh").read_text(),
    {
        "@@C3_SHA@@": sha(tools["c3_check.py"]),
        "@@C3_B64@@": b64(tools["c3_check.py"]),
        "@@CHECK_B64@@": b64(tools["check_redaction.py"]),
        "@@PREAD_SHA@@": sha(tools["protected_read.py"]),
        "@@PREAD_B64@@": b64(tools["protected_read.py"]),
    },
)
launch = fill(
    (HERE / "rpd_flux1_launch.template.sh").read_text(),
    {"@@CONNECT_SHA@@": sha(connect.encode()), "@@FETCH_SHA@@": sha(fetch.encode())},
)
for name, text in (("rpd_flux1_connect.sh", connect), ("rpd_flux1_fetch.sh", fetch), ("rpd_flux1_launch.sh", launch)):
    (OUT / name).write_text(text)
    print(sha(text.encode()), name)
print(sha(job.encode()), "rpd_flux1_job.sh (as the connect writes it)")
for name, data in sorted(tools.items()):
    print(sha(data), "tools/" + name)
print("S", S)
print(pins)
