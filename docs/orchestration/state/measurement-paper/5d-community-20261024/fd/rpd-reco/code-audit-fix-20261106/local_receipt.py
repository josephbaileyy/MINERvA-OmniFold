"""Build local fixture receipts and enumerate the exercised import closure."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[8]
STATE = Path(__file__).resolve().parent
OUT = Path(__file__).resolve().parent
SOURCE = REPO / "nd-unfolding/fd_rpd_reco.py"


def module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def label(path: Path) -> str:
    for root, replacement in (
        (REPO, "$REPO"),
        (Path(sys.prefix), "$PYTHON"),
        (Path.home(), "$HOME"),
    ):
        try:
            return replacement + "/" + str(path.relative_to(root))
        except ValueError:
            pass
    return "$SYSTEM/" + str(path).lstrip("/")


def worker(root: Path, seed: int) -> None:
    native = hasattr(os, "O_NOATIME")
    if not native:
        os.O_NOATIME = os.O_NONBLOCK
    producer = module(SOURCE, "receipt_producer")
    sibling_opens: list[str] = []

    def refuse_sibling_open(event: str, arguments: tuple[Any, ...]) -> None:
        if event == "open" and isinstance(arguments[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(arguments[0]))
            if path.parent == root / "dumps" and path.name in {
                f"nn_{playlist}.npz" for playlist in producer.PLAYLISTS
            }:
                sibling_opens.append(path.name)
                raise AssertionError("known sibling opened")

    sys.addaudithook(refuse_sibling_open)
    config = root / "config.json"
    sha = hashlib.sha256(config.read_bytes()).hexdigest()
    statuses = []
    for step in ("pins", "p0"):
        code = producer.main(
            [
                step,
                "--config",
                str(config),
                "--config-sha256",
                sha,
                "--run",
                str(root / "run"),
                "--dry-run",
            ]
        )
        assert code == 0, (step, code)
        statuses.append(json.loads((root / "run" / f"{step}.json").read_text()))
    assert not any(
        row.get("key") == "measured"
        for record in statuses
        for row in record["keys_read"]
    )
    assert statuses[0]["result"]["n_files"] == 24
    assert len(statuses[0]["result"]["known_siblings_stat_only"]) == 12
    producer.shape_score(
        producer.np.array([0.1, 0.2, 0.3]),
        producer.np.ones(3),
        producer.np.full(3, 30.0),
    )
    closure = sorted(
        {
            str(Path(m.__file__).resolve())
            for m in list(sys.modules.values())
            if getattr(m, "__file__", None) and Path(m.__file__).is_file()
        }
    )
    (root / "worker.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "known_sibling_open_count": len(sibling_opens),
                "native_noatime_available": native,
                "test_only_flag": None if native else "O_NONBLOCK",
                "records": statuses,
                "closure": closure,
            },
            indent=2,
        )
    )


if len(sys.argv) > 1 and sys.argv[1] == "--worker":
    worker(Path(sys.argv[2]), int(sys.argv[3]))
    raise SystemExit

fixture_module = module(
    REPO / "nd-unfolding/tests/test_fd_rpd_reco.py", "receipt_fixture"
)
receipts = []
paths = set()
for seed in (17, 43):
    with tempfile.TemporaryDirectory(prefix="rpd-receipt-") as temporary:
        root = Path(temporary)
        fixture_module.Fixture(root, seed=seed)
        for playlist in fixture_module.R.PLAYLISTS:
            (root / "dumps" / f"nn_{playlist}.npz").write_bytes(
                b"stat-only sibling stand-in"
            )
        env = os.environ | {k: "1" for k in fixture_module.R.THREAD_KEYS}
        p = subprocess.run(
            check=False,
            args=[
                sys.executable,
                str(Path(__file__)),
                "--worker",
                str(root),
                str(seed),
            ],
            env=env,
            text=True,
            capture_output=True,
        )
        assert p.returncode == 0, p.stdout + p.stderr
        raw = json.loads((root / "worker.json").read_text())
        paths.update(map(Path, raw.pop("closure")))
        text = (
            json.dumps(raw, indent=2)
            .replace(str(root), "$FIXTURE")
            .replace(str(REPO), "$REPO")
            .replace(str(Path.home()), "$HOME")
        )
        receipts.append(json.loads(text))
fixture_names = sorted(
    {
        token
        for token in re.findall(
            r"(?<![%\w./\-])[\w./\-]+(?:\.npz|\.root)\b", json.dumps(receipts)
        )
        if "/" not in token
    }
)
(OUT / "LOCAL-DRY-RUN.json").write_text(
    json.dumps(
        {
            "scope": "local real-format NPZ, TH1 ROOT and synthetic constrained-MAT/custody handoff fixtures only; no real MnvH1D or syscall custody claim",
            "disposable_fixture_artifact_paths": [
                "/tmp/rpd-reco-disposable-fixture/" + name for name in fixture_names
            ],
            "fixture_path_note": "Absolute /tmp paths above are a normalized namespace for disposable fixtures, not surviving files or binary deliverables. Recreate with this driver.",
            "path_normalization": "$FIXTURE/$REPO/$HOME replace private paths; fixture pin and configuration digests refer to original local bytes",
            "runs": receipts,
        },
        indent=2,
    )
    + "\n"
)
# A separate native-platform CLI probe must refuse without a test substitution.
with tempfile.TemporaryDirectory(prefix="rpd-native-stop-") as temporary:
    run = Path(temporary) / "run"
    (Path(temporary) / "absent.json").write_text("{}")
    p = subprocess.run(
        check=False,
        args=[
            sys.executable,
            str(SOURCE),
            "pins",
            "--config",
            str(Path(temporary) / "absent.json"),
            "--config-sha256",
            "a" * 64,
            "--run",
            str(run),
            "--dry-run",
        ],
        env=os.environ | {k: "1" for k in fixture_module.R.THREAD_KEYS},
        capture_output=True,
        text=True,
    )
    native = json.loads((run / "pins.STOP.json").read_text())
    assert (
        p.returncode == 4
        and native["guard"] == "NOATIME"
        and native["readings"] is None
    )
    native = json.loads(
        json.dumps(native).replace(temporary, "$FIXTURE").replace(str(REPO), "$REPO")
    )
    (OUT / "NATIVE-NOATIME-STOP.json").write_text(json.dumps(native, indent=2) + "\n")
exercised_paths = set(paths)
paths.update(
    {
        REPO / "nd-unfolding/fd_rpd_reco_custody.py",
        REPO / "nd-unfolding/tests/fd_rpd_reco_mat_check.py",
    }
)
modules = []
hits = []
pattern = re.compile(
    r"\b(?:open|Open|ReadObj|read_text|read_bytes|write_text|write_bytes|fromfile|tofile|memmap|TFile|FileIO|GzipFile|BZ2File|ZipFile|NamedTemporaryFile|TemporaryFile|load|savez|savez_compressed)\s*\("
)
for path in sorted(paths):
    modules.append(
        {
            "path": label(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "kind": "python" if path.suffix == ".py" else "extension_or_bytecode",
            "exercised": path in exercised_paths,
        }
    )
    if path.suffix != ".py":
        continue
    text = path.read_text(errors="replace")
    for number, line in enumerate(text.splitlines(), 1):
        if not pattern.search(line):
            continue
        if path == SOURCE:
            tree = ast.parse(text)
            function = next(
                (
                    n.name
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.lineno <= number <= n.end_lineno
                ),
                "module",
            )
            if function == "stage_copy":
                disposition = "Declared source: os.open uses required O_NOATIME; source/copy SHA and source fingerprint checked; runtime audit active."
            elif function == "read_flux_histogram":
                disposition = "MAT-only path: PyROOT TFile uses an exact checked staged path. This numerical fixture run does not execute that path or establish its native closure; the real-Mnv and syscall trace gates remain required."
            elif function in (
                "key",
                "load_pins",
                "declared",
                "p0",
                "require_prediction",
                "step0",
            ):
                disposition = "Declared input read uses staged copy; NPZ archive keys explicitly allowlisted; committed prediction restaged for every measured access."
            else:
                disposition = "Owned code, staged copy, generated output, or CLI record; declared original roots are not passed to this open."
        elif path not in exercised_paths:
            disposition = "Static-only custody/real-MAT boundary source; not executed by this receipt. Original staging requires O_NOATIME; traced extraction is gated by a separate passing syscall receipt. No native closure is claimed here."
        elif line.lstrip().startswith("#") or ">>>" in line:
            disposition = "Comment/example text; no executable open at this line."
        else:
            disposition = "Dependency/stdlib general-purpose I/O: production calls pass staged copies or owned outputs; active Python audit rejects plain reads under declared roots. Native extension internals are not established by this source grep."
        hits.append((label(path), number, line.strip().replace("\t", " "), disposition))
(OUT / "IMPORT-CLOSURE.json").write_text(
    json.dumps(
        {
            "scope": "Exercised numerical pins/p0 and shape_score closure plus explicitly unexercised static custody/real-MAT boundary files; fixture generator/pytest stay in the parent",
            "modules": modules,
            "ROOT_imported": any("/ROOT/" in str(p) for p in paths),
            "limitations": "Source grep cannot inspect native extension internals. Numerical P0 reads pinned extraction/factor products. Real constrained MAT execution, native Linux O_NOATIME, cold staged-prefix closure and syscall classes remain run-lane gates; static-only files are explicitly marked unexercised.",
        },
        indent=2,
    )
    + "\n"
)
with (OUT / "OPEN-CLOSURE.tsv").open("w") as stream:
    stream.write("module\tline\ttext\tdisposition\n")
    for hit in hits:
        stream.write("\t".join(map(str, hit)) + "\n")
print(
    json.dumps(
        {
            "dry_runs": len(receipts),
            "closure_files": len(modules),
            "open_hits_with_dispositions": len(hits),
        }
    )
)
