#!/usr/bin/env python3
"""Login-safe tests for the Gate-3 P3F-PET fresh full-event production launcher, BOUND production form
(nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh). No compute, no sbatch: bash -n, structural
grep of the bound footing/composition, the define-only selftest + map modes, and static fail-closed
behavior (dry-run dies before compute when the submit-time launcher SHA is missing/wrong).

  python tests/test_p3f_pet_fullevent_launcher.py     # or via pytest
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
LAUNCHER = os.path.join(REPO, "nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh")
TEXT = open(LAUNCHER).read()

P3F_SHA = "d782a47868863f2fc9a743f25f91549f0ab70a3ce7ff64f4db946b36a2df38ed"
DOMAIN_SHA = "32634d6832b4c1f6e5f9036a425b7412f004e2de0aa77828106646d7fc6e3739"
BASE_SHA = "3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8"
BIN_SHA = "61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b"
BUILT_COMMIT = "486e53e677eb64eb9d622ff6e5daecb3e62aab22"
IFACE_COMMIT = "2e8c214abc4b3ffc4ef371e8da6b5f107611862f"
SRC_BLOB = "b7e1edbce21545f1f824fe706047bd0f943a60ea"
SRC_SHA = "57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3"
RECEIPT_SCHEMA = "p3f-pet-production-playlist-receipt-v1"


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _embedded_python(containing):
    matches = re.findall(r"<<'PY'\n(.*?)\nPY", TEXT, re.S)
    found = [src for src in matches if containing in src]
    assert len(found) == 1, (containing, len(found))
    return found[0]


def _run(env_extra):
    env = dict(os.environ)
    for k in ("SLURM_ARRAY_TASK_ID", "P3F_LAUNCHER_SHA256", "P3F_PET_SELFTEST", "P3F_PET_MAP_TASK"):
        env.pop(k, None)
    env.update(env_extra)
    return subprocess.run(["bash", LAUNCHER], cwd=os.path.dirname(LAUNCHER), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


# ---- syntax + token binding ----
def test_bash_syntax():
    r = subprocess.run(["bash", "-n", LAUNCHER], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    assert r.returncode == 0, r.stderr


def test_all_embedded_python_byte_compiles():
    for i, src in enumerate(re.findall(r"<<'PY'\n(.*?)\nPY", TEXT, re.S)):
        compile(src, f"launcher-heredoc-{i}", "exec")


def test_no_unresolved_placeholder_token():
    assert "__P3F_VALIDATOR_SHA256__" not in TEXT, "unresolved validator placeholder must be gone"


def test_bound_validator_hashes():
    assert f'EXPECTED_P3F_VAL_SHA="{P3F_SHA}"' in TEXT
    assert f'EXPECTED_DOMAIN_VAL_SHA="{DOMAIN_SHA}"' in TEXT
    assert f'EXPECTED_BASE_G2_VAL_SHA="{BASE_SHA}"' in TEXT


def test_source_and_build_provenance_bound():
    assert f'EXPECTED_BIN_SHA="{BIN_SHA}"' in TEXT
    assert f'BUILT_SOURCE_COMMIT="{BUILT_COMMIT}"' in TEXT
    assert f'ACTIVE_INTERFACE_COMMIT="{IFACE_COMMIT}"' in TEXT     # FULL commit, not truncated
    assert f'EXPECTED_SOURCE_BLOB="{SRC_BLOB}"' in TEXT
    assert f'EXPECTED_SOURCE_SHA="{SRC_SHA}"' in TEXT


def test_source_fail_closed_guard():
    assert "git hash-object" in TEXT and "$EXPECTED_SOURCE_BLOB" in TEXT and "$EXPECTED_SOURCE_SHA" in TEXT
    assert "merge-base --is-ancestor" in TEXT and '${BUILT_SOURCE_COMMIT}:${SOURCE_REL}' in TEXT
    assert "do NOT rebuild/launch" in TEXT


# ---- exact validator CLI + composition ----
def test_p3f_cli_named_options():
    for opt in ("--root", "--band", "--endpoint", "--playlist", "--work",
                "--domain-validator", "--base-validator"):
        assert opt in TEXT, opt
    assert '"$P3F_VALIDATOR" --root "$WORK_ROOT_FILE"' in TEXT


def test_requires_verdict_pass_not_status():
    assert 'd.get("verdict")=="PASS"' in TEXT
    assert '"status":"PASS"' not in TEXT              # receipt no longer stamps a fabricated status
    assert 'd.get("status")' not in TEXT              # validator report keyed on verdict, not status


def test_base_validator_never_invoked_directly():
    assert 'python3 "$BASE_G2_VALIDATOR"' not in TEXT
    assert 'python3 "$DOMAIN_VALIDATOR"' not in TEXT   # domain also only composed by P3F, not called here
    assert "base NEVER invoked directly" in TEXT or "NEVER called directly" in TEXT


def test_no_standalone_base_json_artifact():
    assert "BASE_VAL_JSON" not in TEXT
    assert "base_g2_validation_" not in TEXT


# ---- receipt binds the actual P3F report fields ----
def test_receipt_actual_report_fields():
    for key in ('"verdict":report.get("verdict")', 'report.get("expected_active")',
                'report.get("observed_active")', 'report.get("observed_census")',
                '"domain_validator"', '"base_validator"', '"source_git_blob"', '"source_sha256"',
                '"active_interface_commit"', '"validation_report":report',
                '"domain_validator":report.get("domain_validator")',
                '"base_validator":report.get("base_validator")',
                '"inventory":report.get("inventory")', '"counts":report.get("counts")'):
        assert key in TEXT, key


def test_receipt_no_nonexistent_fields():
    assert "active_identity" not in TEXT              # nonexistent validator field, removed
    assert '"census":val.get("census")' not in TEXT
    assert '"base_g2_validator"' not in TEXT
    assert '"domain_report":pick' not in TEXT and '"base_report":pick' not in TEXT
    assert "def pick(" not in TEXT


def test_prepublication_report_integration_is_fail_closed():
    for needle in ('d.get("n_failed")==0', 'set(components)=={"inventory","domain","active","census"}',
                   'dom.get("exit")==0', 'base.get("non_superseded_failures")==[]'):
        assert needle in TEXT, needle


def test_resume_revalidates_embedded_report_and_nested_evidence():
    for needle in ('embedded validation_report missing', 'embedded P3F root hash mismatch',
                   'embedded active identity mismatch', 'embedded census invalid',
                   'top-level domain report differs', 'top-level base report differs',
                   'base validator has non-superseded failures',
                   'top-level inventory/counts copy differs'):
        assert needle in TEXT, needle


def test_running_receipt_does_not_fabricate_terminal_accounting():
    assert '"sacct"' not in TEXT
    assert '"state":"COMPLETED"' not in TEXT
    assert "does not fabricate" in TEXT and "complete Gate-3 manifest" in TEXT


def test_receipt_and_resume_synthetic_roundtrip():
    build_src = _embedded_python("receipt-temp-written")
    resume_src = _embedded_python("[resume-ok]")
    with tempfile.TemporaryDirectory() as td:
        root = os.path.join(td, "final.root")
        dman = os.path.join(td, "1A_Data.txt")
        mman = os.path.join(td, "1A_MC.txt")
        valjson = os.path.join(td, "validation.json")
        receipt = os.path.join(td, "receipt.json")
        open(root, "wb").write(b"synthetic-root")
        open(dman, "wb").write(b"data-manifest")
        open(mman, "wb").write(b"mc-manifest")
        root_sha, dsha, msha = _sha(root), _sha(dman), _sha(mman)
        census_names = ["activeUniverseTruthEntrants", "activeUniverseTruthExits",
                        "activeUniverseRecoEntrants", "activeUniverseRecoExits"]
        active = {"activeUniverseBand": "BeamAngleX", "activeUniverseIndex": 0,
                  "hasActiveUniverse": 1, "activeUniverseIsLateral": 1}
        domain = {"path": "/validator/domain.py", "sha256": DOMAIN_SHA, "ran": True,
                  "exit": 0, "receipt": "/work/domain.json", "receipt_sha256": "d" * 64,
                  "status": "PASS", "fatal": [], "domain": {"pt_max": 30.0,
                  "p_par_max": 120.0}, "out_of_domain_censused_and_bound": 0}
        base = {"path": "/validator/base.py", "sha256": BASE_SHA, "ran": True,
                "exit": 0, "receipt": "/work/base.json", "receipt_sha256": "b" * 64,
                "n_checks": 60, "n_failed": 0, "non_superseded_failures": [],
                "superseded_failures": []}
        report = {"receipt_schema": "p3f-pet-fullevent-validation-v1", "verdict": "PASS",
                  "root": {"path": "/work/root", "sha256": root_sha,
                           "size_bytes": os.path.getsize(root)},
                  "this_validator": {"path": "/validator/p3f.py", "sha256": P3F_SHA},
                  "domain_validator": domain, "base_validator": base,
                  "inventory": {"band": "BeamAngleX", "endpoint": 0, "playlist": "1A",
                                "n_total_files": 120, "in_inventory": True},
                  "expected_active": dict(active, census_params=census_names),
                  "observed_active": active,
                  "observed_census": dict((k, 0) for k in census_names),
                  "counts": {"data": 1}, "n_checks": 20, "n_failed": 0,
                  "component_verdicts": {"inventory": True, "domain": True,
                                         "active": True, "census": True}}
        with open(valjson, "w") as f:
            json.dump(report, f)
        launcher_sha = "a" * 64
        build_args = [receipt, root, root_sha, str(os.path.getsize(root)), "BeamAngleX", "0", "1A",
                      BIN_SHA, BUILT_COMMIT, IFACE_COMMIT, SRC_BLOB, SRC_SHA, launcher_sha,
                      dman, mman, dsha, msha, "/validator/p3f.py", P3F_SHA, valjson,
                      "/validator/domain.py", DOMAIN_SHA, "/validator/base.py", BASE_SHA,
                      "123", "0", REPO, RECEIPT_SCHEMA]
        r = subprocess.run([sys.executable, "-c", build_src] + build_args,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        assert r.returncode == 0, r.stderr
        produced = json.load(open(receipt))
        assert produced["validation_report"] == report
        assert produced["domain_validator"] == domain and produced["base_validator"] == base
        assert "sacct" not in produced["slurm"] and "state" not in produced["slurm"]
        resume_args = [receipt, root, "BeamAngleX", "0", "1A", BIN_SHA, BIN_SHA,
                       P3F_SHA, P3F_SHA, DOMAIN_SHA, DOMAIN_SHA, BASE_SHA, BASE_SHA,
                       SRC_BLOB, SRC_BLOB, SRC_SHA, SRC_SHA, dman, mman, dsha, msha,
                       dsha, msha, RECEIPT_SCHEMA, BUILT_COMMIT, launcher_sha]
        r = subprocess.run([sys.executable, "-c", resume_src] + resume_args,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        assert r.returncode == 0, r.stderr
        produced["validation_report"]["observed_active"]["activeUniverseIndex"] = 1
        with open(receipt, "w") as f:
            json.dump(produced, f)
        r = subprocess.run([sys.executable, "-c", resume_src] + resume_args,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        assert r.returncode != 0 and "active identity mismatch" in r.stderr


# ---- SBATCH: absolute log paths + resources ----
def test_absolute_log_paths():
    assert "--output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs/" in TEXT
    assert "--error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs/" in TEXT


def test_sbatch_resources():
    for needle in ("--cpus-per-task=4", "--mem=48G", "--time=12:00:00", "--array=0-119%16",
                   "--qos=shared", "--constraint=cpu"):
        assert needle in TEXT, needle


# ---- retained mechanics ----
def test_isolation_and_noclobber_mechanics():
    assert "nd-unfolding/p3f_pet_fullevent/work" in TEXT and "nd-unfolding/p3f_pet_fullevent/final" in TEXT
    for fn in ("publish_root_noclobber", "publish_receipt_noclobber", "classify_publication",
               "quarantine_stale_partial", "validate_resume", "assert_isolated_namespace"):
        assert fn in TEXT, fn
    assert "flock -n 200" in TEXT and "os.fsync" in TEXT and "mktemp" in TEXT
    assert 'ln "$src" "$dst"' in TEXT and 'ln "$tmp" "$dst"' in TEXT


def test_runtime_flag_contract():
    assert 'MNV101_ACTIVE_UNIVERSE="${BAND}:${ENDPOINT}"' in TEXT
    assert "MNV101_DUMP_POINTCLOUD=1" in TEXT and "MNV101_FULL_PHASE_SPACE=1" in TEXT
    assert "unset MNV101_DUMP_UNIVERSES" in TEXT and "env -u MNV101_DUMP_UNIVERSES" in TEXT


def test_24_manifest_shas_bound():
    assert len(re.findall(r"\[1[A-P]_(?:Data|MC)\.txt\]=[0-9a-f]{64}", TEXT)) == 24


def test_footing_reasserted_and_source_checked_each_time():
    assert TEXT.count("assert_input_footing ") >= 3       # before compute, after loop, before publish


def test_launcher_sha_supplied_at_submission():
    assert "P3F_LAUNCHER_SHA256" in TEXT and "assert_launcher_sha" in TEXT


def test_does_not_write_g2_launcher():
    assert not re.search(r">\s*\S*sbatch_g2_fullevent_evloop_array\.sh", TEXT)


# ---- define-only selftest + map (no compute) ----
def test_selftest_reports_bound_composition():
    r = _run({"P3F_PET_SELFTEST": "1"})
    blob = r.stdout + r.stderr
    assert r.returncode == 0, blob[-400:]
    assert "tasks=120" in blob and "array=0-119%16" in blob
    assert f"p3f={P3F_SHA} (bound)" in blob
    assert f"domain={DOMAIN_SHA}" in blob and f"base={BASE_SHA}" in blob
    assert "P3F->domain->base" in blob and "PLACEHOLDER(UNBOUND)" not in blob
    assert f"source_blob={SRC_BLOB}" in blob


def test_map_mode_band_major():
    cases = {"0": ("BeamAngleX", "0", "1A"), "1": ("BeamAngleX", "0", "1B"),
             "12": ("BeamAngleX", "1", "1A"), "24": ("BeamAngleY", "0", "1A"),
             "119": ("Muon_Energy_MINOS", "1", "1P")}
    for task, (band, ep, pl) in cases.items():
        r = _run({"P3F_PET_MAP_TASK": task})
        assert r.returncode == 0, r.stderr
        assert f"band={band} endpoint={ep} playlist={pl}" in r.stdout, (task, r.stdout)


def test_map_rejects_out_of_range():
    r = _run({"P3F_PET_MAP_TASK": "120"})
    assert r.returncode != 0 and "out of range" in (r.stderr + r.stdout)


# ---- static fail-closed (dry run dies before compute) ----
def test_static_fail_closed_missing_launcher_sha():
    r = _run({"SLURM_ARRAY_TASK_ID": "0"})            # no P3F_LAUNCHER_SHA256
    blob = r.stderr + r.stdout
    assert r.returncode != 0 and "P3F_LAUNCHER_SHA256 must be supplied" in blob, blob[-400:]
    assert "START loop" not in blob


def test_static_fail_closed_wrong_launcher_sha():
    r = _run({"SLURM_ARRAY_TASK_ID": "0", "P3F_LAUNCHER_SHA256": "deadbeef"})
    blob = r.stderr + r.stdout
    assert r.returncode != 0 and "launcher SHA drift" in blob, blob[-400:]
    assert "START loop" not in blob


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn(); print(f"[PASS] {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} P3F-PET bound-launcher tests passed")


if __name__ == "__main__":
    _run_all()
