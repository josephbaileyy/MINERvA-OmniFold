"""Tests of the negweight fetch package, all local (no ssh): the remote script's fence and pscratch reader run against
stub sacct/squeue and a fake checkout; nw_verify.py runs on synthetic payloads; the wrapper's refusals are exercised.
macOS has no os.O_NOATIME, so the reader runs with a test-only sitecustomize that sets it to 0 (the remote script
itself is unchanged)."""
import hashlib
import io
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nw_verify as nv  # noqa: E402

RELS = list(nv.WANT)


def body(script, tag):
    """The heredoc body <<'tag' ... tag of nw_remote.sh."""
    s = (HERE / script).read_text()
    a = s.index(f"<<'{tag}'"); a = s.index("\n", a) + 1
    return s[a:s.index(f"\n{tag}\n", a)] + "\n"


def stubs(tmp, sacct_out, squeue_out, sacct_rc=0, squeue_rc=0):
    d = tmp / "bin"; d.mkdir(exist_ok=True)
    for name, out, rc in (("sacct", sacct_out, sacct_rc), ("squeue", squeue_out, squeue_rc)):
        (d / f"{name}.out").write_text(out)
        p = d / name; p.write_text(f"#!/bin/sh\ncat '{d}/{name}.out'\nexit {rc}\n"); p.chmod(0o755)
    shim = tmp / "shim"; shim.mkdir(exist_ok=True)
    (shim / "sitecustomize.py").write_text("import os\nif not hasattr(os, 'O_NOATIME'):\n    os.O_NOATIME = 0\n")
    return {"PATH": f"{d}:/usr/bin:/bin", "PYTHONPATH": str(shim), "HOME": str(tmp)}


def fence(tmp, sacct_out, squeue_out, **k):
    env = stubs(tmp, sacct_out, squeue_out, **k)
    return subprocess.run([sys.executable, "-s", "-"], input=body("nw_remote.sh", "FENCE"), text=True,
                          capture_output=True, env=env)


@pytest.mark.parametrize("name", ["cov2d_x", "t2a_y", "rpd_flux5", "precharge_c1", "geanttw_a", "oofvc_b",
                                  "covfix_c", "ibuchi_d", "ptmc_e"])
def test_fence_refuses_each_family_running(tmp_path, name):
    r = fence(tmp_path, f"123|{name}|RUNNING\n", "")
    assert r.returncode == 10 and "REFUSED" in r.stdout


def test_fence_refuses_family_in_squeue_only(tmp_path):
    r = fence(tmp_path, "", "77|ptmc_q|PENDING\n")
    assert r.returncode == 10


def test_fence_clear_on_terminal_or_foreign(tmp_path):
    r = fence(tmp_path, "1|rpd_old|COMPLETED\n2|cov2d_z|CANCELLED by 1\n3|other_job|RUNNING\n", "3|other_job|RUNNING\n")
    assert r.returncode == 0 and "FENCE CLEAR" in r.stdout and "other_job" in r.stdout


@pytest.mark.parametrize("which", ["sacct", "squeue"])
def test_fence_refuses_when_a_tool_fails(tmp_path, which):
    r = fence(tmp_path, "", "", **{f"{which}_rc": 1})
    assert r.returncode == 10 and "failed" in r.stdout


def reader(tmp, make, stale_atime=False):
    """stale_atime: the files' atime is older than their mtime, so this Mac's relatime-like rule updates it on a read
    (a negative control of the atime check); otherwise it is set ahead, so a read leaves it unchanged."""
    root = tmp / "pscratch/sd/j/josephrb/MINERvA-OmniFold"
    files = {}
    for rel in RELS:
        p = root / rel; p.parent.mkdir(parents=True, exist_ok=True)
        if make.get(rel, "file") == "file":
            data = os.urandom(1000) + rel.encode(); p.write_bytes(data); files[rel] = data
            m = p.stat().st_mtime
            os.utime(p, (m - 100 if stale_atime else m + 86400, m))
        elif make[rel] == "link":
            (tmp / "elsewhere").write_bytes(b"x"); p.symlink_to(tmp / "elsewhere")
    code = body("nw_remote.sh", "READ").replace('"/pscratch/sd/j/josephrb/MINERvA-OmniFold"', repr(str(root)))
    env = stubs(tmp, "", "")
    r = subprocess.run([sys.executable, "-s", "-"], input=code.encode(), capture_output=True, env=env)
    return r, files


def test_reader_streams_both_files_and_reports_unchanged(tmp_path):
    r, files = reader(tmp_path, {})
    assert r.returncode == 0, r.stderr
    err = r.stderr.decode()
    assert err.count("UNCHANGED") == 2
    tf = tarfile.open(fileobj=io.BytesIO(r.stdout), mode="r:")
    assert sorted(m.name for m in tf.getmembers()) == sorted(RELS)
    for rel, data in files.items():
        assert tf.extractfile(rel).read() == data
        assert hashlib.sha256(data).hexdigest() in err


def test_reader_refuses_when_atime_moves(tmp_path):
    r, _ = reader(tmp_path, {}, stale_atime=True)
    assert r.returncode == 22 and r.stdout == b"" and b"CHANGED" in r.stderr


def test_reader_refuses_missing_without_fallback(tmp_path):
    r, _ = reader(tmp_path, {RELS[1]: "none"})
    assert r.returncode == 20 and r.stdout == b"" and b"MISSING" in r.stderr


def test_reader_refuses_symlink(tmp_path):
    r, _ = reader(tmp_path, {RELS[0]: "link"})
    assert r.returncode == 21 and r.stdout == b""


def payload(tmp, members, name="p.tar"):
    p = tmp / name
    with tarfile.open(p, "w") as tf:
        for n, b, kind in members:
            ti = tarfile.TarInfo(n)
            if kind == "file":
                ti.size = len(b); tf.addfile(ti, io.BytesIO(b))
            else:
                ti.type = tarfile.SYMTYPE; ti.linkname = "/etc/passwd"; tf.addfile(ti)
    return p


@pytest.fixture
def pins(monkeypatch):
    data = {rel: os.urandom(200) for rel in RELS}
    monkeypatch.setattr(nv, "WANT", {r: (len(b), hashlib.sha256(b).hexdigest()) for r, b in data.items()})
    return data


def test_verify_pass_writes_only_the_two(tmp_path, pins):
    p = payload(tmp_path, [(r, b, "file") for r, b in pins.items()] + [("other/x.root", b"zz", "file")])
    errs, rows = nv.verify("pscratch", p, tmp_path / "out")
    assert errs == [] and len(rows) == 2
    assert sorted(os.listdir(tmp_path / "out")) == sorted([os.path.basename(r) for r in RELS] + ["SHA256SUMS"])


def test_verify_dot_slash_names(tmp_path, pins):
    p = payload(tmp_path, [("./" + r, b, "file") for r, b in pins.items()])
    assert nv.verify("pscratch", p, tmp_path / "out")[0] == []


def test_verify_wrong_bytes(tmp_path, pins):
    items = [(r, b, "file") for r, b in pins.items()]; items[0] = (items[0][0], b"bad", "file")
    errs, _ = nv.verify("pscratch", payload(tmp_path, items), tmp_path / "out")
    assert errs and not (tmp_path / "out").exists()


def test_verify_missing_duplicate_symlink(tmp_path, pins):
    r0, r1 = RELS
    for i, items in enumerate([[(r0, pins[r0], "file")],
                               [(r0, pins[r0], "file"), (r0, pins[r0], "file"), (r1, pins[r1], "file")],
                               [(r0, b"", "link"), (r1, pins[r1], "file")]]):
        errs, _ = nv.verify("pscratch", payload(tmp_path, items, f"p{i}.tar"), tmp_path / f"out{i}")
        assert errs and not (tmp_path / f"out{i}").exists()


def test_verify_hpss_requires_the_archived_tar(tmp_path, pins):
    p = payload(tmp_path, [(r, b, "file") for r, b in pins.items()])
    errs, _ = nv.verify("hpss", p, tmp_path / "out")
    assert errs and "negweight_runs_8.tar" in errs[0] and not (tmp_path / "out").exists()


def test_verify_refuses_existing_out_and_bad_mode(tmp_path, pins):
    p = payload(tmp_path, [(r, b, "file") for r, b in pins.items()])
    (tmp_path / "out").mkdir()
    assert nv.verify("pscratch", p, tmp_path / "out")[0]
    assert nv.verify("auto", p, tmp_path / "o2")[0]


def test_verify_pins_equal_the_inventory():
    rel_inv = "docs/orchestration/state/negweight-hpss-20260821/inventory.tsv"
    cands = [Path(os.environ["NW_REPO"]) / rel_inv] if os.environ.get("NW_REPO") else []
    cands += [a / rel_inv for a in HERE.parents]
    inv = next((c for c in cands if c.exists()), None)
    if inv is None:
        pytest.skip("inventory.tsv not found (set NW_REPO to a checkout)")
    rows = {l.split("\t")[0]: (int(l.split("\t")[1]), l.split("\t")[2]) for l in inv.read_text().splitlines() if l}
    for rel, want in nv.WANT.items():
        assert rows[rel] == want


@pytest.mark.parametrize("args", [["auto", "a", "b", "OUT"], ["pscratch", "0", "0", "OUT"]])
def test_wrapper_refuses_before_any_connect(tmp_path, args):
    args = [str(tmp_path / "o") if a == "OUT" else a for a in args]
    r = subprocess.run(["bash", str(HERE / "nw_fetch.sh"), *args], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
    assert r.returncode == 2 and ("REFUSED" in r.stdout or "usage" in r.stdout)
    assert not (tmp_path / "o").exists()


def test_remote_refuses_without_mode():
    r = subprocess.run(["bash", str(HERE / "nw_remote.sh")], capture_output=True, text=True)
    assert r.returncode == 2 and r.stdout == "" and "REFUSED" in r.stderr
