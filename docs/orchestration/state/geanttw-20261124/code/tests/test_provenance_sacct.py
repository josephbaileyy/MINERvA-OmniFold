"""geanttw_provenance.py and geanttw_sacct.py: a pass case and one planted failure per rule."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
REL = "MINERvA101/MINERvA-101-Cross-Section"


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Prov:
    def __init__(self, tmp):
        self.tree = tmp / "synced"
        self.deploy = tmp / "deploy"
        files = {"CMakeLists.txt": b"cmake\n", "runEventLoopOmniFold.cpp": b"int main(){}\n",
                 "util/Binning.h": b"// b\n", "systematics/Systematics.h": b"// s\n"}
        for rel, data in files.items():
            for root in (self.tree, self.deploy / REL):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.tree / rel).write_bytes(data)
        for rel in ("CMakeLists.txt", "runEventLoopOmniFold.cpp"):   # M tracks only some of the files
            (self.deploy / REL / rel).write_bytes(files[rel])
        subprocess.run(["git", "init", "-q"], cwd=self.deploy, check=True)
        subprocess.run(["git", "add", "."], cwd=self.deploy, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "M"], cwd=self.deploy,
                       check=True)
        self.manifest = tmp / "S0-src_base.sha256"
        self.manifest.write_text("# header\n" + "".join(f"{sha(d)}  {r}\n" for r, d in sorted(files.items())))

    def run(self):
        return subprocess.run([sys.executable, "-I", str(CODE / "geanttw_provenance.py"), "--manifest",
                               str(self.manifest), "--tree", str(self.tree), "--deploy", str(self.deploy)],
                              capture_output=True, text=True)


def test_provenance_passes(tmp_path):
    r = Prov(tmp_path).run()
    assert r.returncode == 0, r.stdout
    assert "SOURCE_PROVENANCE PASS: 4 manifest rows, 0 problem(s)" in r.stdout


def test_provenance_extra_file(tmp_path):
    p = Prov(tmp_path)
    (p.tree / "util" / "Stray.h").write_text("x")
    r = p.run()
    assert r.returncode == 1 and "not in the manifest: util/Stray.h" in r.stdout


def test_provenance_missing_file(tmp_path):
    p = Prov(tmp_path)
    (p.tree / "util" / "Binning.h").unlink()
    r = p.run()
    assert r.returncode == 1 and "missing from the synced tree: util/Binning.h" in r.stdout
    assert "SOURCE_PROVENANCE FAIL: 4 manifest rows, 1 problem(s)" in r.stdout


def test_provenance_hash_mismatch(tmp_path):
    p = Prov(tmp_path)
    (p.tree / "systematics" / "Systematics.h").write_text("// changed\n")
    r = p.run()
    assert r.returncode == 1 and "sha256 mismatch: systematics/Systematics.h" in r.stdout


def test_provenance_tracked_file_differs(tmp_path):
    p = Prov(tmp_path)
    f = p.deploy / REL / "runEventLoopOmniFold.cpp"
    f.write_text("int main(){return 1;}\n")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "x"], cwd=p.deploy,
                   check=True)
    r = p.run()
    assert r.returncode == 1 and "tracked at M but differs from the manifest: runEventLoopOmniFold.cpp" in r.stdout


def test_provenance_tracked_file_not_in_manifest(tmp_path):
    p = Prov(tmp_path)
    (p.deploy / REL / "runEventLoopOmniFold_OLD.cpp").write_text("old\n")
    subprocess.run(["git", "add", "."], cwd=p.deploy, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"], cwd=p.deploy,
                   check=True)
    r = p.run()
    assert r.returncode == 1 and "tracked at M but not in the manifest: runEventLoopOmniFold_OLD.cpp" in r.stdout


@pytest.mark.parametrize("text", ["", "# only a header\n", "nothex  a\n", f"{'a' * 64} b\n",
                                  f"{'a' * 64}  x\n{'b' * 64}  x\n"])
def test_provenance_unusable_manifest(tmp_path, text):
    p = Prov(tmp_path)
    p.manifest.write_text(text)
    r = p.run()
    assert r.returncode == 2 and r.stdout.startswith("UNUSABLE")


# ── geanttw_sacct.py ──
def sacct(tmp_path, cmd, rows, *args, subs=None):
    psv = tmp_path / "s.psv"
    psv.write_text("".join(r + "\n" for r in rows))
    extra = []
    if subs is not None:
        lg = tmp_path / "sub.log"
        lg.write_text("".join(s + "\n" for s in subs))
        extra = ["--submissions", str(lg)]
    elif cmd == "cap":
        extra = ["--submissions", str(tmp_path / "absent.log")]
    return subprocess.run([sys.executable, "-I", str(CODE / "geanttw_sacct.py"), cmd, "--sacct", str(psv), *extra,
                           *args], capture_output=True, text=True)


FENCE = ["--regex", "^(cov2d|t2a)"]


@pytest.mark.parametrize("rows,rc", [
    ([], 0),
    (["1|cov2d_ll5d|COMPLETED|10|1|60", "2|t2a_x|CANCELLED by 123|0|1|60", "3|ibub_run|RUNNING|5|1|60"], 0),
    (["1|cov2d_ll5d|RUNNING|10|1|60"], 3),
    (["1|t2a_x|PENDING|0|1|60"], 3),
    (["1|cov2d_x|SOMETHING_NEW|0|1|60"], 3),
    (["1|cov2d_x||0|1|60"], 3),
    (["1|xcov2d|RUNNING|0|1|60"], 0),
    (["sacct: error: something"], 2),
    (["|cov2d|RUNNING|0|1|60"], 2),
    (["", "1|cov2d_x|COMPLETED|1|1|60", "  "], 0),   # blank lines are skipped, not unusable
])
def test_fence(tmp_path, rows, rc):
    r = sacct(tmp_path, "fence", rows, *FENCE)
    assert r.returncode == rc, r.stdout
    if rc == 3:
        assert r.stdout.startswith("LIVE ")


def cap_json(r):
    return json.loads(r.stdout)


def test_cap_within(tmp_path):
    r = sacct(tmp_path, "cap", ["9|geanttw_p0_pin_1L|COMPLETED|3600|1|60"], "--name", "geanttw_p0_pat_1L",
              "--limit", "01:00:00")
    j = cap_json(r)
    assert r.returncode == 0 and j["pass"] is True
    assert j["spent"] == pytest.approx(0.0391) and j["want_ceiling"] == pytest.approx(0.0391)


def test_cap_held_and_unlisted(tmp_path):
    r = sacct(tmp_path, "cap", ["9|geanttw_p0_pin_1L|RUNNING|100|1|60", "8|other|RUNNING|1|1|60"],
              "--name", "geanttw_p0_pat_1L", "--limit", "01:00:00",
              subs=["SUBMIT id=9 name=geanttw_p0_pin_1L limit=01:00:00", "SUBMIT id=77 name=geanttw_p2_1A limit=02:00:00",
                    "note line"])
    j = cap_json(r)
    assert r.returncode == 0
    assert j["held"] == pytest.approx(0.0391 + 2 * 0.0391) and j["unlisted_ids"] == ["77"]
    assert j["total"] == pytest.approx(4 * 0.0391)


def test_cap_over(tmp_path):
    big = [f"{i}|geanttw_p2_1A|COMPLETED|{3600 * 30}|1|60" for i in range(7)]   # 7 x 30 h x 0.0391 = 8.21
    r = sacct(tmp_path, "cap", big, "--name", "geanttw_p0_pin_1L", "--limit", "00:00:01")
    assert r.returncode == 3 and cap_json(r)["pass"] is False


def test_cap_at_exactly_the_cap_passes(tmp_path, monkeypatch):
    import importlib.util
    s = importlib.util.spec_from_file_location("gs", CODE / "geanttw_sacct.py")
    gs = importlib.util.module_from_spec(s)
    s.loader.exec_module(gs)
    rec = gs.cap([], [], "geanttw_p0_pin_1L", "01:00:00", cap_=0.0391)
    assert rec["pass"] is True
    assert gs.cap([], [], "geanttw_p0_pin_1L", "01:00:01", cap_=0.0391)["pass"] is False


@pytest.mark.parametrize("rows,args,subs", [
    (["9|geanttw_p0_pin_1L|RUNNING|1|1|UNLIMITED"], ["--name", "geanttw_p0_pat_1L", "--limit", "01:00:00"], None),
    ([], ["--name", "geanttw_p3_x", "--limit", "01:00:00"], None),
    ([], ["--name", "geanttw_p0_pin_1L", "--limit", "1:0:0"], None),
    ([], ["--name", "geanttw_p0_pin_1L", "--limit", "01:60:00"], None),
    ([], ["--name", "geanttw_p0_pin_1L", "--limit", "01:00:00"], ["SUBMIT name=x"]),
    ([], ["--name", "geanttw_p0_pin_1L", "--limit", "01:00:00"], ["SUBMIT id=5 name=x"]),
    ([], ["--name", "geanttw_p0_pin_1L", "--limit", "01:00:00"], ["SUBMIT limit=01:00:00 name=x"]),
    (["bad row"], ["--name", "geanttw_p0_pin_1L", "--limit", "01:00:00"], None),
])
def test_cap_unusable(tmp_path, rows, args, subs):
    r = sacct(tmp_path, "cap", rows, *args, subs=subs)
    assert r.returncode == 2 and "error" in cap_json(r)


def test_no_subcommand(tmp_path):
    r = subprocess.run([sys.executable, "-I", str(CODE / "geanttw_sacct.py")], capture_output=True, text=True)
    assert r.returncode == 2



@pytest.mark.parametrize("drop", ["--manifest", "--tree", "--deploy"])
def test_provenance_every_argument_is_required(tmp_path, drop):
    p = Prov(tmp_path)
    args = {"--manifest": str(p.manifest), "--tree": str(p.tree), "--deploy": str(p.deploy)}
    del args[drop]
    r = subprocess.run([sys.executable, "-I", str(CODE / "geanttw_provenance.py"), *sum(args.items(), ())],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "the following arguments are required: " + drop in r.stderr, r.stderr


@pytest.mark.parametrize("cmd,drop", [("fence", "--sacct"), ("fence", "--regex"), ("cap", "--sacct"),
                                      ("cap", "--submissions"), ("cap", "--name"), ("cap", "--limit")])
def test_sacct_every_argument_is_required(tmp_path, cmd, drop):
    psv = tmp_path / "s.psv"
    psv.write_text("")
    args = {"--sacct": str(psv), "--regex": "^x"} if cmd == "fence" else {
        "--sacct": str(psv), "--submissions": str(tmp_path / "s.log"), "--name": "geanttw_p0_pin_1L",
        "--limit": "01:00:00"}
    del args[drop]
    r = subprocess.run([sys.executable, "-I", str(CODE / "geanttw_sacct.py"), cmd, *sum(args.items(), ())],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "the following arguments are required: " + drop in r.stderr, r.stderr


def test_cap_json_is_printed_with_sorted_keys(tmp_path):
    r = sacct(tmp_path, "cap", [], "--name", "geanttw_p0_pin_1L", "--limit", "01:00:00")
    keys = list(json.loads(r.stdout))
    assert keys == sorted(keys)


# ── the cap gate's job families (p2p3/AMENDMENT-P2P3.md A2, A3) ──
def _gs():
    import importlib.util
    s = importlib.util.spec_from_file_location("gs_fam", CODE / "geanttw_sacct.py")
    gs = importlib.util.module_from_spec(s)
    s.loader.exec_module(gs)
    return gs


@pytest.mark.parametrize("name,rate", [
    ("geanttw_p0_pat_1L", 0.0391), ("geanttw_p2_1A", 0.0391), ("geanttw_p2_pilot_1B", 0.0391),
    ("geanttw_p2_pilotref_1B", 0.0391), ("geanttw_p2_c2pre", 0.0391), ("geanttw_p3_c2", 0.0391),
    ("geanttw_p3_slim", 0.0391), ("geanttw_p3_extract_pin", 0.0391), ("geanttw_p3_extract_all", 0.0391), ("geanttw_p3_unf_pin_GEANT_Pion_0", 0.5), ("geanttw_p3_unf_patov_GEANT_Proton_1", 0.5), ("geanttw_p3_unf_pinov_GEANT_Neutron_0", 0.5),
])
def test_each_family_has_its_rate(name, rate):
    gs = _gs()
    assert gs.rate(name) == rate
    assert gs.cap([], [], name, "02:00:00")["want_ceiling"] == pytest.approx(2 * rate)


@pytest.mark.parametrize("name", ["geanttw_p2_1L", "geanttw_p3_unf_pin_GEANT_Pion_2", "geanttw_p3_unf_pat_GEANT_Pion_0", "geanttw_p3_unf_GEANT_Pion_0",
                                  "geanttw_p3_slimx", "geanttw_p2_pilot_1L", "geanttw_p4_x"])
def test_names_outside_every_family_are_unusable(name):
    gs = _gs()
    with pytest.raises(gs.Unusable):
        gs.rate(name)


def test_listed_and_unlisted_jobs_are_held_at_their_own_rates():
    gs = _gs()
    rows = ["101|geanttw_p3_unf_pin_GEANT_Pion_0|RUNNING|60|1|30", "102|geanttw_p2_1A|COMPLETED|3600|1|60"]
    subs = ["SUBMIT id=103 name=geanttw_p3_unf_pin_GEANT_Pion_1 limit=00:30:00 utc=x"]
    rec = gs.cap(rows, subs, "geanttw_p3_slim", "01:00:00")
    assert rec["held"] == pytest.approx(0.5 * 0.5 + 0.5 * 0.5) and rec["spent"] == pytest.approx(0.0391)
    assert rec["total"] == pytest.approx(0.5 + 0.0391 + 0.0391) and rec["unlisted_ids"] == ["103"]


def test_an_unknown_geanttw_job_in_sacct_is_unusable():
    gs = _gs()
    with pytest.raises(gs.Unusable):
        gs.cap(["101|geanttw_mystery|RUNNING|60|1|30"], [], "geanttw_p3_slim", "01:00:00")


def test_a_submission_without_a_name_is_unusable():
    gs = _gs()
    with pytest.raises(gs.Unusable):
        gs.cap([], ["SUBMIT id=103 limit=00:30:00"], "geanttw_p3_slim", "01:00:00")
