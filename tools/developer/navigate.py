"""Query Python definitions and semantic references in a fresh source-only mirror."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import tempfile
from typing import Any

import jedi

from common import git, identity

EXCLUDED = {
    "data",
    "products",
    "weights",
    "logs",
    "outputs",
    "output",
    "results",
    "state",
    "receipts",
    "runs",
    "figures",
    "build",
    "dist",
    "node_modules",
    "__pycache__",
    "venv",
    "env",
}


def sources(root: Path, scopes: list[Path]) -> dict[Path, bytes]:
    """Read nonignored Python source in explicit scopes, excluding symlinks/artifacts."""
    paths = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    result = {}
    for name in paths.split("\0"):
        path = Path(name)
        if path.suffix != ".py" or not any(path.is_relative_to(s) for s in scopes):
            continue
        if any(p.startswith(".") or p.lower() in EXCLUDED for p in path.parts):
            continue
        full = root / path
        if any(p.is_symlink() for p in [full, *full.parents]) or not full.is_file():
            continue
        if not full.resolve().is_relative_to(root):
            continue
        # A tracked nested repository is an independent checkout, not this source scope.
        if any(
            (p / ".git").exists()
            for p in full.parents
            if p != root and p.is_relative_to(root)
        ):
            continue
        result[path] = full.read_bytes()
    return result


def query(root: Path, file: Path, symbol: str, scopes: list[Path]) -> dict[str, Any]:
    """Resolve a symbol with Jedi and keep lexical occurrences in a separate result.

    Parameters
    ----------
    root : Path
        Git checkout root.
    file : Path
        Repository-relative file containing the definition.
    symbol : str
        Exact Python identifier. Multiple definitions in the file are refused.
    scopes : list[Path]
        Repository-relative source directories to include.

    Returns
    -------
    dict
        Checkout identity, source digest, and categorized file/line locations.
    """
    before = identity(root)
    contents = sources(root, scopes)
    if file not in contents:
        raise ValueError(f"Target is absent or excluded from scopes: {file}")
    with tempfile.TemporaryDirectory(prefix="minerva-nav-") as temp:
        mirror = Path(temp)
        for path, data in contents.items():
            target = mirror / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        jedi.settings.cache_directory = str(mirror / ".cache")
        jedi.settings.use_filesystem_cache = False
        project = jedi.Project(
            path=mirror,
            sys_path=[str(mirror / s) for s in scopes],
            smart_sys_path=False,
            load_unsafe_extensions=False,
        )
        script = jedi.Script(path=mirror / file, project=project)
        definitions = [
            n
            for n in script.get_names(
                all_scopes=True, definitions=True, references=False
            )
            if n.name == symbol and n.type in {"function", "class"}
        ]
        if len(definitions) != 1:
            raise ValueError(
                f"Expected one function/class definition, found {len(definitions)}"
            )
        definition = definitions[0]
        references = script.get_references(
            definition.line, definition.column, include_builtins=False
        )
        # Jedi's project reference search stops at some renamed imports. Resolve
        # explicit import aliases through its goto API before querying their uses.
        for path, data in contents.items():
            try:
                tree = ast.parse(data)
            except SyntaxError:
                continue
            aliases = {
                n.asname
                for n in ast.walk(tree)
                if isinstance(n, ast.alias) and n.asname
            }
            if not aliases:
                continue
            consumer = jedi.Script(path=mirror / path, project=project)
            for name in consumer.get_names(
                all_scopes=True, definitions=True, references=False
            ):
                if name.name not in aliases:
                    continue
                targets = name.goto(follow_imports=True)
                if any(
                    n.module_path == mirror / file
                    and n.line == definition.line
                    and n.column == definition.column
                    for n in targets
                ):
                    references.extend(
                        consumer.get_references(
                            name.line, name.column, include_builtins=False
                        )
                    )
        resolved = []
        seen = set()
        for name in references:
            if name.module_path is None or not name.module_path.is_relative_to(mirror):
                continue
            relative = name.module_path.relative_to(mirror)
            if relative not in contents:
                continue
            key = (relative, name.line, name.column)
            if key in seen:
                continue
            seen.add(key)
            kind = "binding" if name.is_definition() else "reference"
            if key == (file, definition.line, definition.column):
                kind = "definition"
            resolved.append(
                {
                    "file": str(relative),
                    "line": name.line,
                    "column": name.column,
                    "name": name.name,
                    "kind": kind,
                }
            )
        known = {(r["file"], r["line"], r["column"]) for r in resolved}
        occurrences = []
        pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")
        for path, data in sorted(contents.items()):
            for line, text in enumerate(data.decode("utf-8").splitlines(), 1):
                for match in pattern.finditer(text):
                    if (str(path), line, match.start()) not in known:
                        occurrences.append(
                            {
                                "file": str(path),
                                "line": line,
                                "column": match.start(),
                                "kind": "text-only",
                                "text": text.strip(),
                            }
                        )
    if contents != sources(root, scopes) or before != identity(root):
        raise ValueError("Checkout changed during query; retry against stable source")
    checksum = hashlib.sha256()
    for path, data in sorted(contents.items()):
        checksum.update(str(path).encode() + b"\0" + data + b"\0")
    return {
        **before,
        "backend": f"jedi {jedi.__version__}",
        "scopes": list(map(str, scopes)),
        "source_files": len(contents),
        "source_sha256": checksum.hexdigest(),
        "definition": {
            "file": str(file),
            "line": definition.line,
            "column": definition.column,
        },
        "semantic_locations": resolved,
        "unresolved_text_occurrences": occurrences,
        "limitations": "Static Python only; references may be incomplete. Text-only matches are not callers. Dynamic dispatch/imports and monkeypatches need manual review.",
    }


def main() -> int:
    """Print a JSON navigation result; refuse missing or ambiguous definitions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("symbol")
    parser.add_argument("--scope", action="append", type=Path, required=True)
    args = parser.parse_args()
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()
    if any(p.is_absolute() or ".." in p.parts for p in [args.file, *args.scope]):
        parser.error("file/scopes must be paths relative to the checkout root")
    try:
        result = query(root, args.file, args.symbol, args.scope)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"navigation failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
