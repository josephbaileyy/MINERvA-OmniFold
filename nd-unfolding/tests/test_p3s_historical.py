#!/usr/bin/env python3
"""ROOT-free negatives for the P3F historical-provenance validator (p3s_manifest_summary.py), repair-2:
mandatory --hash-files, exact inventory incl. extras, PER-FILE producer binding (strict log-name regex,
skip-only exclusion, allow-listed jobs, md5 + FPS-message + task<->path mapping, missing/duplicate/wrong
producer), terminal-COMPLETED/0:0 accounting parsing, launcher-as-observation-only, no-clobber fsync
publish, and canonical/existing-final protection. Per-file ROOT checks run against real ROOTs at
production time; here we test the pure/log/provenance layers with fixtures + one real CLI negative.

  python tests/test_p3s_historical.py     # or via pytest
"""
import json, os, subprocess, sys, tempfile

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ND)
import p3s_manifest_summary as P

MD5 = "e63c74961d699313ef155065fc790ff1"


def _raises(fn, exc=P.HistoricalEvidenceError):
    try:
        fn()
    except exc:
        return True
    return False


def _mk_producer_log(d, job, task, wrote_paths, md5=MD5, fps=True, skip_only=False):
    p = os.path.join(d, f"ev5d_active_fps_{job}_{task}.out")
    lines = [f"[active-fps] binary fingerprint OK (md5 {md5})"]
    if fps:
        lines.append("[FPS] MNV101_FULL_PHASE_SPACE set: cuts OFF")
    for w in wrote_paths:
        lines.append(f"[active-fps] {'skip (exists)' if skip_only else 'wrote'} {w}")
    open(p, "w").write("\n".join(lines) + "\n")
    return p


# ---- interface md5 / evidence ----
def test_interface_md5_absent():
    assert _raises(lambda: P.parse_interface_md5("/no/such/iface.md"))


def test_interface_md5_parsed():
    d = tempfile.mkdtemp(); p = os.path.join(d, "i.md"); open(p, "w").write(f"md5 `{MD5}`\n")
    assert P.parse_interface_md5(p) == MD5


def test_interface_md5_missing_in_file():
    d = tempfile.mkdtemp(); p = os.path.join(d, "i.md"); open(p, "w").write("nothing\n")
    assert _raises(lambda: P.parse_interface_md5(p))


# ---- strict log-name parse (underscore split is wrong) ----
def test_parse_log_name_ok():
    assert P.parse_log_name("ev5d_active_fps_55972324_7.out") == ("55972324", "7")


def test_parse_log_name_rejects_bad():
    assert P.parse_log_name("ev5d_active_fps_55972324.out") is None
    assert P.parse_log_name("something_else_1_2.out") is None


# ---- task<->path mapping ----
def test_expected_task_mapping():
    assert P.expected_task_for("BeamAngleX", 0, "1A") == 0
    assert P.expected_task_for("BeamAngleX", 0, "1B") == 1
    assert P.expected_task_for("BeamAngleX", 1, "1A") == 12
    assert P.expected_task_for("BeamAngleY", 0, "1A") == 24


# ---- producer index + binding ----
def _index_with(d):
    root = "/x/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1B_active_BeamAngleX_0.root"
    _mk_producer_log(d, "55972324", "1", [root])                       # real producer (task 1 -> 1B)
    _mk_producer_log(d, "55972324", "0",
                     ["/x/.../1A.root"], skip_only=True)               # skip-only -> excluded
    _mk_producer_log(d, "99999999", "5", ["/x/other.root"])            # non-allowlisted job -> excluded
    return P.index_producers(d), root


def test_index_excludes_skip_and_nonallowlisted():
    d = tempfile.mkdtemp(); idx, root = _index_with(d)
    assert os.path.realpath(root) in idx
    assert all("99999999" not in r["producer_job"] for recs in idx.values() for r in recs)
    assert "/x/.../1A.root" not in idx and os.path.realpath("/x/.../1A.root") not in idx


def test_bind_producer_ok():
    d = tempfile.mkdtemp(); idx, root = _index_with(d)
    b = P.bind_producer(root, "BeamAngleX", 0, "1B", idx, MD5)
    assert b["producer_job"] == "55972324" and b["producer_task"] == 1


def test_bind_missing_producer():
    d = tempfile.mkdtemp(); idx, root = _index_with(d)
    assert _raises(lambda: P.bind_producer("/x/nope.root", "BeamAngleX", 0, "1A", idx, MD5))


def test_bind_duplicate_producer():
    d = tempfile.mkdtemp()
    root = "/x/dup_1B_BeamAngleX_0.root"
    _mk_producer_log(d, "55972324", "1", [root])
    _mk_producer_log(d, "55961845", "1", [root])       # two producers for same path
    idx = P.index_producers(d)
    assert _raises(lambda: P.bind_producer(root, "BeamAngleX", 0, "1B", idx, MD5))


def test_bind_wrong_md5():
    d = tempfile.mkdtemp(); root = "/x/r_1B.root"
    _mk_producer_log(d, "55972324", "1", [root], md5="0" * 32)
    idx = P.index_producers(d)
    assert _raises(lambda: P.bind_producer(root, "BeamAngleX", 0, "1B", idx, MD5))


def test_bind_absent_fps_message():
    d = tempfile.mkdtemp(); root = "/x/r_1B.root"
    _mk_producer_log(d, "55972324", "1", [root], fps=False)
    idx = P.index_producers(d)
    assert _raises(lambda: P.bind_producer(root, "BeamAngleX", 0, "1B", idx, MD5))


def test_bind_wrong_task_mapping():
    d = tempfile.mkdtemp(); root = "/x/r_1B.root"
    _mk_producer_log(d, "55972324", "7", [root])       # task 7 != expected 1 for 1B
    idx = P.index_producers(d)
    assert _raises(lambda: P.bind_producer(root, "BeamAngleX", 0, "1B", idx, MD5))


# ---- accounting ----
def test_parse_sacct_state():
    assert P.parse_sacct_state("COMPLETED|0:0\nCOMPLETED|0:0") == ("COMPLETED", "0:0")
    assert P.parse_sacct_state("") is None
    assert P.parse_sacct_state("weird") is None


def test_terminal_ok():
    assert P.terminal_ok("COMPLETED", "0:0")
    assert not P.terminal_ok("RUNNING", "0:0")
    assert not P.terminal_ok("FAILED", "1:0")
    assert not P.terminal_ok("COMPLETED", "0:1")


def test_require_terminal_missing_job():
    assert _raises(lambda: P.require_terminal_completed("999999999", "0"))


def test_require_terminal_returns_receipt_fields():
    original = P._sh
    try:
        P._sh = lambda command: "COMPLETED|0:0\nCOMPLETED|0:0"
        assert P.require_terminal_completed("42", "7") == {
            "state": "COMPLETED", "exitcode": "0:0"}
    finally:
        P._sh = original


# ---- exact inventory / extras ----
def test_no_extra_files_detects_extra():
    d = tempfile.mkdtemp()
    ep = os.path.join(d, "BeamAngleX_0"); os.makedirs(ep)
    open(os.path.join(ep, "runEventLoopOmniFold_5D_1A_active_BeamAngleX_0.root"), "w").write("x")
    open(os.path.join(ep, "runEventLoopOmniFold_5D_ZZ_active_BeamAngleX_0.root"), "w").write("x")  # extra
    extras = P.require_no_extra_files(d)
    assert any("ZZ" in e for e in extras)


# ---- launcher observation-only ----
def test_launcher_is_observation_only():
    d = tempfile.mkdtemp(); iface = os.path.join(d, "i.md"); open(iface, "w").write(f"md5 {MD5}\n")
    prod, obs, md5 = P.build_historical_provenance(os.path.dirname(ND), "fps", iface)
    assert prod["production_launcher_content"].startswith("unknown")
    assert prod["production_launcher_source_commit"] is None
    assert "observation_launcher_candidate" in obs and md5 == MD5


# ---- canonical / preflight output protection ----
def test_resolve_out_rejects_canonical():
    base = "/x/active_universe_5d/fps"
    assert _raises(lambda: P.resolve_historical_out(base, "fps", os.path.join(base, "p3s_fps_manifest.json")))


def test_resolve_out_rejects_outside_preflight():
    base = "/x/active_universe_5d/fps"
    assert _raises(lambda: P.resolve_historical_out(base, "fps", os.path.join(base, "elsewhere.json")))


def test_resolve_out_accepts_preflight():
    base = "/x/active_universe_5d/fps"
    out = P.resolve_historical_out(base, "fps", None)
    assert "/preflight/" in out


# ---- no-clobber fsync publish ----
def test_publish_noclobber_writes_and_no_temp():
    d = tempfile.mkdtemp(); p = os.path.join(d, "sub", "m.json")
    P.publish_receipt_noclobber(p, {"ok": True})
    assert json.load(open(p))["ok"] is True
    assert not any(x.startswith(".p3s_") for x in os.listdir(os.path.dirname(p)))


def test_publish_noclobber_refuses_existing():
    d = tempfile.mkdtemp(); p = os.path.join(d, "m.json"); open(p, "w").write("{}")
    assert _raises(lambda: P.publish_receipt_noclobber(p, {"ok": True}))


def test_publish_noclobber_refuses_broken_symlink():
    d = tempfile.mkdtemp(); p = os.path.join(d, "m.json")
    os.symlink(os.path.join(d, "absent-target"), p)
    assert os.path.lexists(p) and not os.path.exists(p)
    assert _raises(lambda: P.publish_receipt_noclobber(p, {"ok": True}))


# ---- inventory completeness (missing/extra/failing) ----
def test_inventory_complete_true():
    assert P.inventory_complete(120, [], [], [])


def test_inventory_complete_false_on_extra():
    assert not P.inventory_complete(120, [], [], ["BeamAngleX_0/ZZ.root"])


# ---- census retained ----
def test_census_present_and_aggregate():
    assert P.census_present({c: 1 for c in P.CENSUS})
    assert not P.census_present({**{c: 1 for c in P.CENSUS}, P.CENSUS[0]: None})
    assert all(v == 5 for v in P.aggregate_census([{c: 2 for c in P.CENSUS}, {c: 3 for c in P.CENSUS}]).values())


# ---- REAL CLI: historical without --hash-files -> EVIDENCE-BLOCKED before ROOT ----
def test_cli_historical_requires_hash_files():
    r = subprocess.run([sys.executable, "p3s_manifest_summary.py", "--mode", "fps",
                        "--provenance", "historical"], cwd=ND,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    blob = (r.stderr or "") + (r.stdout or "")
    assert r.returncode == 3 and "REQUIRES --hash-files" in blob, blob[-400:]


def test_cli_historical_standard_is_explicitly_unsupported():
    r = subprocess.run([sys.executable, "p3s_manifest_summary.py", "--mode", "standard",
                        "--provenance", "historical", "--hash-files"], cwd=ND,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    blob = (r.stderr or "") + (r.stdout or "")
    assert r.returncode == 3 and "explicitly unsupported for standard mode" in blob, blob[-400:]


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn(); print(f"[PASS] {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} P3F historical-provenance repair-2 tests passed")


if __name__ == "__main__":
    _run_all()
