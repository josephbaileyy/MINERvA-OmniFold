"""Local checks for rehearsal workspace confinement and evidence handling."""

import ast
import json
import os
import sys
import time
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

import rehearse
import run_ibukt


def test_production_paths_do_not_import_numpy_testing():
    # NumPy 1.26's testing import can launch lscpu under the production guard.
    repo = run_ibukt.REPO
    sources = (
        "2d-unfolding/ibukt/connect.py",
        "2d-unfolding/ibukt/ibukt.py",
        "2d-unfolding/ibukt/jobs.py",
        "2d-unfolding/ibukt/run_ibukt.py",
        "2d-unfolding/ref_c2c1/ref_c2c1.py",
        "2d-unfolding/re2/re2_driver.py",
        "unbinned_unfolding/python/omnifold.py",
        "nd-unfolding/mnv_guarded_run.py",
    )
    violations = []
    for source in sources:
        nodes = list(ast.walk(ast.parse((repo / source).read_text(), filename=source)))
        numpy_names = {"numpy"}
        for node in nodes:
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name == "numpy" and name.asname:
                        numpy_names.add(name.asname)
                    if name.name.split(".")[:2] == ["numpy", "testing"]:
                        violations.append(f"{source}:{node.lineno}")
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                module = node.module or ""
                if module.split(".")[:2] == ["numpy", "testing"] or (
                    module == "numpy"
                    and any(name.name == "testing" for name in node.names)
                ):
                    violations.append(f"{source}:{node.lineno}")
        for node in nodes:
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "testing"
                and isinstance(node.value, ast.Name)
                and node.value.id in numpy_names
            ):
                violations.append(f"{source}:{node.lineno}")
    assert not violations, "numpy.testing in guarded production paths: " + ", ".join(
        violations
    )


@pytest.mark.parametrize("location", ["cfs", "outside", "symlink"])
def test_probe_refuses_before_creating_anything(tmp_path, monkeypatch, location):
    scratch = tmp_path / "pscratch"
    home = scratch / "user"
    parent = home / "ibukt-rehearsal-test"
    parent.mkdir(mode=0o700, parents=True)
    target = tmp_path / location
    target.mkdir()
    workspace = target
    if location == "symlink":
        workspace = parent / "paper-mask"
        workspace.symlink_to(target, target_is_directory=True)
    monkeypatch.setenv("SCRATCH", str(home))
    monkeypatch.setenv("IBUKT_REHEARSAL_ROOT", str(parent))
    monkeypatch.setattr(rehearse, "SCRATCH_ROOT", scratch)
    monkeypatch.setattr(
        rehearse,
        "run_probe",
        lambda *args: pytest.fail("invalid workspace reached the probe"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "rehearse.py",
            "--probe",
            "paper-mask",
            "--workspace",
            str(workspace),
        ],
    )
    monkeypatch.chdir(workspace)
    with pytest.raises(SystemExit) as caught:
        rehearse.main()
    assert caught.value.code == 2
    assert not list(target.iterdir())


def test_probe_accepts_the_private_working_directory(tmp_path, monkeypatch):
    parent = tmp_path / "user" / "ibukt-rehearsal-test"
    parent.mkdir(mode=0o700, parents=True)
    workspace = parent / "score"
    workspace.mkdir(mode=0o700)
    (workspace / "stage").mkdir(mode=0o700)
    monkeypatch.setattr(rehearse, "SCRATCH_ROOT", tmp_path)
    monkeypatch.setenv("SCRATCH", str(parent.parent))
    monkeypatch.setenv("IBUKT_REHEARSAL_ROOT", str(parent))
    monkeypatch.chdir(workspace)
    for variable, suffix in (
        ("TMPDIR", "tmp"),
        ("MPLCONFIGDIR", "mpl"),
        ("XDG_CACHE_HOME", "cache"),
    ):
        directory = workspace / suffix
        directory.mkdir(mode=0o700)
        monkeypatch.setenv(variable, str(directory))
    assert rehearse.validated_workspace("score", workspace) == workspace


def test_inventory_preserves_rows_across_missing_and_malformed_evidence(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), raising=False)
    inventory = tmp_path / "imports.jsonl"
    assert not rehearse.probe_result(inventory, 0)["complete"]
    passed = dict(outcome="ok", verdict="ok", launch_refusal=None, offending_argv=None)
    lines = [json.dumps(passed), json.dumps(passed)]
    inventory.write_text("\n".join(lines))
    assert rehearse.probe_result(inventory, 0)["complete"]
    refused = dict(
        outcome="refused:launch",
        verdict="refused",
        launch_refusal="blocked",
        offending_argv=["lscpu"],
    )
    inventory.write_text("\n".join([*lines, "{", json.dumps(refused)]))
    result = rehearse.probe_result(inventory, 3)
    assert result["outcomes"] == ["ok", "ok", "refused:launch"]
    assert result["refusals"][0]["argv"] == ["lscpu"]
    assert len(result["inventory_errors"]) == 1
    assert not result["complete"]


def test_probe_timeout_kills_descendants(tmp_path):
    program = (
        "import subprocess, sys; "
        "subprocess.Popen([sys.executable, '-c', "
        '\'import time; time.sleep(1); open("late", "w").close()\']); '
        "print('spawned', flush=True); "
        "import time; time.sleep(10)"
    )
    result = rehearse.run_child(
        [sys.executable, "-c", program], tmp_path, dict(os.environ), 0.5
    )
    assert result == 124
    assert "spawned" in (tmp_path / "probe.log").read_text()
    time.sleep(0.75)
    assert not (tmp_path / "late").exists()


@pytest.mark.parametrize("matching", [True, False])
def test_paper_mask_compares_exact_indices_without_numpy_testing(
    tmp_path, monkeypatch, capsys, matching
):
    expected = np.arange(19, 224)
    matrix = Mock(side_effect=lambda row, col: float(row == col and row >= 19))
    matrix.GetNrows.return_value = matrix.GetNcols.return_value = 224
    source = MagicMock()
    source.Get.return_value = matrix
    source.IsZombie.return_value = False
    source.__enter__.return_value = source
    root = SimpleNamespace(TFile=SimpleNamespace(Open=Mock(return_value=source)))
    monkeypatch.setitem(sys.modules, "ROOT", root)
    monkeypatch.setitem(np.__dict__, "testing", None)
    monkeypatch.setattr(rehearse, "digest", lambda _: "pinned-paper")
    if matching:
        rehearse.paper_mask(tmp_path / "paper.root")
        assert json.loads(capsys.readouterr().out)["selected"] == expected.tolist()
    else:
        monkeypatch.setattr(run_ibukt, "_reporting_cells", lambda _: expected[::-1])
        with pytest.raises(ValueError, match="differ from the legacy mask"):
            rehearse.paper_mask(tmp_path / "paper.root")


def test_topology_uses_module_versions_without_distribution_metadata(
    monkeypatch, capsys
):
    context = SimpleNamespace(_count_physical_cores=lambda: 32)
    loky = SimpleNamespace(__version__="loky-test")
    joblib = SimpleNamespace(__version__="joblib-test")

    class Estimator:
        n_jobs = None

        def _process_n_jobs(self, _configured):
            return context._count_physical_cores()

    class Classifier(Estimator):
        pass

    class Regressor(Estimator):
        pass

    lightgbm = SimpleNamespace(
        __version__="lightgbm-test", LGBMClassifier=Classifier, LGBMRegressor=Regressor
    )
    for name, module in {
        "lightgbm": lightgbm,
        "joblib": joblib,
        "joblib.externals": SimpleNamespace(loky=loky),
        "joblib.externals.loky.backend": SimpleNamespace(context=context),
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(
        os, "sched_getaffinity", lambda _: set(range(64)), raising=False
    )
    rehearse.topology()
    record = json.loads(capsys.readouterr().out)
    assert record["versions"] == dict(
        lightgbm="lightgbm-test", joblib="joblib-test", loky="loky-test"
    )
    assert record["physical_core_branch"] is True
    assert record["lscpu_attempted"] is False
    assert record["effective_n_jobs"] == dict(Classifier=32, Regressor=32)
