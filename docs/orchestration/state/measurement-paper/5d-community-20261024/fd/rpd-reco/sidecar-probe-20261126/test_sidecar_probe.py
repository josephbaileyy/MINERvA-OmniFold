"""Controls for the read-only sidecar probe (sidecar_probe_remote.py and build_probe.sh). The reader runs on a copy
whose BASE is a temporary tree; on a platform without O_NOATIME (macOS) the flag is set to 0 for the test only.
    python3 -m pytest -q -p no:cacheprovider test_sidecar_probe.py
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
READER = HERE / "sidecar_probe_remote.py"
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")


@pytest.fixture()
def tree(tmp_path):
    base = Path(os.path.realpath(tmp_path)) / "pscratch"
    side = base / "rdx-20261112b/out/dumps/truthx_RDX_ALL.npz"
    side.parent.mkdir(parents=True)
    side.write_bytes(os.urandom(5000))
    (base / "rdx-20261112b/out/evloop").mkdir(parents=True)
    for pl in PLAYLISTS:
        (base / f"rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_{pl}.root").write_bytes(b"r" * 10)
    lz = base / "measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz"
    lz.parent.mkdir(parents=True)
    lz.write_bytes(b"z" * 20)

    def run(pin=None, opened_log=None, hook=""):
        text = READER.read_text().replace('BASE = "/pscratch/sd/j/josephrb/"', f'BASE = "{base}/"')
        pin = pin or hashlib.sha256(side.read_bytes()).hexdigest()
        text = re.sub(r'SIDECAR_SHA256 = "[0-9a-f]{64}"', f'SIDECAR_SHA256 = "{pin}"', text)
        # without O_NOATIME (macOS) a sentinel bit stands in for it; the recording open strips it before the real call
        pre = "import os\nSENT = 0\nif not hasattr(os, 'O_NOATIME'):\n    SENT = 1 << 29\n    os.O_NOATIME = SENT\n"
        log = opened_log or (base.parent / "opened-default.txt")
        pre += (f"_o = os.open\ndef _rec(p, flags, *a, **k):\n"
                f"    open({str(log)!r}, 'a').write('%s\\t%d\\n' % (p, flags & os.O_NOATIME))\n"
                "    return _o(p, flags & ~SENT, *a, **k)\nos.open = _rec\n" + hook)
        r = subprocess.run([sys.executable, "-I", "-c", pre + text], capture_output=True, text=True)
        rep = json.loads(r.stdout) if r.stdout.strip() else None
        return r, rep

    return {"base": base, "side": side, "lz": lz, "run": run}


def test_probe_passes_and_reports_every_file(tree):
    r, rep = tree["run"]()
    assert r.returncode == 0 and rep["verdict"] == "PASS", r.stdout + r.stderr
    assert len(rep["stat_only"]) == 13 and all("atime" in x and "purge_exposure_from" in x for x in rep["stat_only"])
    s = rep["sidecar"]
    assert s["sha256_matches"] and s["atime_unchanged"] and s["bytes_read"] == 5000 and s["size_matches_read"]


def test_probe_opens_only_the_sidecar(tree, tmp_path):
    log = Path(os.path.realpath(tmp_path)) / "opened.txt"
    r, rep = tree["run"](opened_log=log)
    assert r.returncode == 0, r.stderr
    rows = [ln.split("\t") for ln in log.read_text().splitlines()]
    opened = [p for p, _ in rows]
    assert opened[-1] == "truthx_RDX_ALL.npz" and opened.count("truthx_RDX_ALL.npz") == 1
    assert int(rows[-1][1]) != 0, "the sidecar was not opened O_NOATIME"
    assert not any(x.endswith((".root", "lat_zero.npz")) for x in opened), opened
    assert {x for x in opened[:-1]} <= {str(tree["base"]), "rdx-20261112b", "out", "dumps"}


def test_probe_fails_on_another_digest(tree):
    r, rep = tree["run"](pin="0" * 64)
    assert r.returncode == 9 and rep["verdict"] == "FAIL" and rep["sidecar"]["sha256_matches"] is False


@pytest.mark.parametrize("which", ["omnifile", "lat_zero", "sidecar"])
def test_probe_reports_a_missing_file_and_fails(tree, which):
    target = {"omnifile": tree["base"] / "rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_1G.root",
              "lat_zero": tree["lz"], "sidecar": tree["side"]}[which]
    target.unlink()
    r, rep = tree["run"](pin="1" * 64 if which == "sidecar" else None)   # the right pin: only the missing file fails
    assert r.returncode == 9 and rep["verdict"] == "FAIL", r.stdout + r.stderr
    rows = rep["stat_only"] + [rep["sidecar"]]
    assert sum("missing" in x for x in rows) == 1


@pytest.mark.parametrize("which", ["dir", "file"])
def test_probe_refuses_a_symlink_before_opening_anything(tree, tmp_path, which):
    if which == "file":
        lz = tree["lz"]
        lz.rename(lz.with_name("real.npz"))
        lz.symlink_to(lz.with_name("real.npz"))
    else:
        d = tree["base"] / "rdx-20261112b/out/dumps"
        d.rename(d.with_name("dumps-real"))
        d.symlink_to(d.with_name("dumps-real"))
    log = Path(os.path.realpath(tmp_path)) / "opened.txt"
    r, rep = tree["run"](opened_log=log)
    assert r.returncode == 2 and "is a symlink" in r.stderr and rep is None
    assert not log.exists() or "truthx_RDX_ALL.npz" not in log.read_text()


def test_probe_fails_when_the_sidecar_atime_moves(tree):
    side = str(tree["side"])
    hook = (f"_c = os.close\ndef _close(fd):\n    _c(fd)\n    st = os.lstat({side!r})\n"
            f"    os.utime({side!r}, (st.st_atime + 7, st.st_mtime))\nos.close = _close\n")
    r, rep = tree["run"](hook=hook)
    assert r.returncode == 9 and rep["sidecar"]["atime_unchanged"] is False and rep["verdict"] == "FAIL"


def test_probe_fails_when_fewer_bytes_are_read_than_the_size(tree):
    head = tree["side"].read_bytes()[:1000]
    hook = ("_r = os.read\n_seen = [0]\ndef _read(fd, n):\n    b = _r(fd, n)[:1000 - _seen[0]]\n"
            "    _seen[0] += len(b)\n    return b\nos.read = _read\n")
    r, rep = tree["run"](pin=hashlib.sha256(head).hexdigest(), hook=hook)   # the digest of what was read matches
    assert r.returncode == 9 and rep["sidecar"]["sha256_matches"] is True
    assert rep["sidecar"]["size_matches_read"] is False and rep["verdict"] == "FAIL"


def test_probe_writes_nothing_under_base(tree):
    before = sorted((p, p.stat().st_mtime_ns, p.stat().st_size) for p in tree["base"].rglob("*"))
    tree["run"]()
    after = sorted((p, p.stat().st_mtime_ns, p.stat().st_size) for p in tree["base"].rglob("*"))
    assert before == after


def test_built_wrapper_checks_the_reader_digest_and_node(tmp_path):
    w = HERE / "sidecar-probe.sh"
    text = w.read_text()
    sha = hashlib.sha256(READER.read_bytes()).hexdigest()
    b64 = re.search(r"^PYB='([A-Za-z0-9+/=]+)'$", text, re.M).group(1)
    import base64
    assert base64.b64decode(b64) == READER.read_bytes(), "the embedded reader is not the committed one"
    assert f'[ "${{s1%% *}}" = {sha} ]' in text and '[ "$h" = login02 ]' in text
    assert subprocess.run(["bash", "-n", str(w)]).returncode == 0
