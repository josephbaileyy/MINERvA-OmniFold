"""Shared helpers for the estimator registry, the results index and their checks.

Every reader here reads the GIT INDEX (``git ls-files`` and the staged blobs), not the working tree, so a
pre-commit run judges exactly the bytes the commit will contain and a fresh ``--write`` followed by
``git add`` is what ``--check`` compares against. A file that is not staged does not exist for these tools.
"""
from __future__ import annotations

import csv
import io
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REGISTRY_DIR = "docs/orchestration/registry"
ESTIMATORS = f"{REGISTRY_DIR}/ESTIMATORS.tsv"
ALIASES = f"{REGISTRY_DIR}/ALIASES.tsv"
ATTRIBUTION = f"{REGISTRY_DIR}/ATTRIBUTION.tsv"
STATUS = f"{REGISTRY_DIR}/STATUS.tsv"
UNRESOLVED = f"{REGISTRY_DIR}/UNRESOLVED-NAMES.tsv"
WAIVERS = f"{REGISTRY_DIR}/WAIVERS.tsv"


def clean_env() -> dict:
    """The environment with EVERY GIT_* variable removed (GIT_INDEX_FILE, GIT_DIR, GIT_WORK_TREE,
    GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_COMMON_DIR, GIT_PREFIX, ...). Every git call on a
    THROWAWAY repository (self-tests, fixtures) uses this, with an explicit cwd: a hook's GIT_INDEX_FILE names the
    committing worktree's index, and a fixture that inherited it would overwrite that index."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


_HOOK_TOP: list = []


def _hook_toplevel() -> Path | None:
    """The top level of the repository whose hook is running (resolved with the FULL inherited environment from
    the current directory), or None when no GIT_INDEX_FILE is set. Computed once."""
    if not _HOOK_TOP:
        top = None
        if "GIT_INDEX_FILE" in os.environ:
            out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, cwd=os.getcwd())
            if out.returncode == 0:
                top = Path(out.stdout.decode().strip()).resolve()
        _HOOK_TOP.append(top)
    return _HOOK_TOP[0]


def git_env(repo: Path | str | None = None) -> dict:
    """The environment for a git call on `repo`: clean_env(), plus the hook's GIT_INDEX_FILE (made absolute) ONLY
    when `repo` is the top level of the repository whose hook is running -- a `git commit -a`/`--only` hook judges
    a temporary index, and --check must read that one. Any other repository gets a clean environment."""
    env = clean_env()
    if "GIT_INDEX_FILE" in os.environ and repo is not None:
        top = _hook_toplevel()
        if top is not None and Path(repo).resolve() == top:
            idx = os.environ["GIT_INDEX_FILE"]
            env["GIT_INDEX_FILE"] = idx if os.path.isabs(idx) else os.path.join(os.getcwd(), idx)
    return env


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    out = subprocess.run(["git", "-C", str(repo), *args], input=input_bytes, capture_output=True,
                         env=git_env(repo), cwd=str(repo))
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed ({out.returncode}): {out.stderr.decode(errors='replace')}")
    return out.stdout


def repo_root(start: Path | None = None) -> Path:
    start = start or Path(__file__).resolve().parent
    return Path(git(start, "rev-parse", "--show-toplevel").decode().strip())


class Index:
    """Staged paths and blobs of one repository."""

    def __init__(self, repo: Path):
        self.repo = repo
        self.entries: dict[str, str] = {}
        raw = git(repo, "ls-files", "-s", "-z")
        for rec in raw.split(b"\0"):
            if not rec:
                continue
            meta, path = rec.split(b"\t", 1)
            mode, sha, stage = meta.split()
            if stage != b"0":
                continue
            self.entries[path.decode()] = sha.decode()
        self._cache: dict[str, bytes] = {}

    def paths(self) -> list[str]:
        return sorted(self.entries)

    def has(self, path: str) -> bool:
        return path in self.entries

    def read_many(self, paths: list[str]) -> dict[str, bytes]:
        want = [p for p in paths if p not in self._cache and p in self.entries]
        if want:
            req = "".join(self.entries[p] + "\n" for p in want).encode()
            out = git(self.repo, "cat-file", "--batch", input_bytes=req)
            pos = 0
            for p in want:
                nl = out.index(b"\n", pos)
                header = out[pos:nl].split()
                size = int(header[2])
                self._cache[p] = out[nl + 1:nl + 1 + size]
                pos = nl + 1 + size + 1
        return {p: self._cache[p] for p in paths if p in self._cache}

    def read(self, path: str) -> bytes | None:
        return self.read_many([path]).get(path)

    def text(self, path: str) -> str | None:
        b = self.read(path)
        return None if b is None else b.decode("utf-8", errors="replace")


def read_tsv_text(text: str) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE))
    return [{k: (v or "") for k, v in r.items()} for r in rows]


def read_tsv(index: Index, path: str) -> list[dict]:
    text = index.text(path)
    if text is None:
        raise FileNotFoundError(f"{path} is not in the git index")
    return read_tsv_text(text)


import hashlib  # noqa: E402


def line_digest(text: str) -> str:
    """The first 16 hex digits of the sha256 of one line's exact text (no newline)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def find_cited_line(file_text: str, quote: str, sha: str) -> tuple[int, str]:
    """(1-based line number, text) of the one line of `file_text` whose digest is `sha` and which holds `quote`.

    Self-tests use it to find a registry-cited line without assuming its line number, so a document may be edited
    above the cited line. Raises ValueError if no line, or more than one line, matches."""
    hits = [(n, l) for n, l in enumerate(file_text.split("\n"), start=1) if line_digest(l) == sha and quote in l]
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} lines have digest {sha} and hold {quote!r} (want exactly 1)")
    return hits[0]


def alias_citation(aliases_text: str, estimator: str, kind: str) -> dict:
    """The one ALIASES row of `estimator` and `kind` (its source, line hint, quote and line_sha256)."""
    rows = [r for r in read_tsv_text(aliases_text) if r["estimator"] == estimator and r["kind"] == kind]
    if len(rows) != 1:
        raise ValueError(f"{len(rows)} ALIASES rows for {estimator}/{kind} (want exactly 1)")
    return rows[0]


def fields(row: dict) -> tuple[str, str, str, str]:
    """(source, line, quote, line_sha256) of a cited row of any registry table."""
    if "defining_source" in row:
        return (row["defining_source"], row["defining_line"], row["defining_quote"],
                row.get("defining_line_sha256", ""))
    return row["source"], row["line"], row["quote"], row.get("line_sha256", "")


def locate(index: Index, source: str, line: str, quote: str, sha: str) -> tuple[int | None, str | None, str | None]:
    """Where the cited line is: (line number, error, note).

    A citation is resolved by the DIGEST of the whole cited line (`line_sha256`); the TSV line number is a hint.
    It holds if exactly one line of the file has that digest and that line contains the quote; the note then
    names the line found when it differs from the hint (`check_registry.py --repoint` refreshes hints). It FAILS
    if no line has the digest -- the cited line's text changed: an edit, a retraction, a rewording, even if the
    quote survives; re-read it and re-cite by hand (`check_registry.py --cite FILE:LINE`) -- or if several lines
    have it (ambiguous).
    """
    text = index.text(source)
    if text is None:
        return None, f"{source} is not tracked (not in the git index)", None
    try:
        n = int(line)
    except ValueError:
        return None, f"line {line!r} is not an integer", None
    if not quote:
        return None, f"{source}:{n}: empty quote", None
    if not re.fullmatch(r"[0-9a-f]{16}", sha or ""):
        return None, f"{source}:{n}: no line_sha256 recorded (run `check_registry.py --cite {source}:{n}`)", None
    lines = text.split("\n")
    if 1 <= n <= len(lines) and line_digest(lines[n - 1]) == sha:
        same = [n]
    else:
        same = [i for i, l in enumerate(lines, start=1) if line_digest(l) == sha]
    if len(same) == 1:
        k = same[0]
        if quote not in lines[k - 1]:
            return None, f"{source}:{k}: the line has its digest but not the quote {quote!r} (row is malformed)", None
        if k != n:
            return k, None, f"{source}: cited line found at {k} (TSV hint {n}; `check_registry.py --repoint` refreshes it)"
        return k, None, None
    if same:
        return None, (f"{source}:{n}: the cited line's text occurs on {len(same)} lines "
                      f"({', '.join(map(str, same[:5]))}); re-cite by hand"), None
    now = lines[n - 1] if 1 <= n <= len(lines) else "(past end of file)"
    return None, (f"{source}:{n}: the cited line's TEXT CHANGED (no line has digest {sha}); line {n} now reads "
                  f"{now[:120]!r}. Re-read it and re-cite by hand (`check_registry.py --cite {source}:{n}`); "
                  "--repoint does not accept edits"), None


def verify_citation(index: Index, source: str, line: str, quote: str, sha: str = "") -> tuple[str | None, str | None]:
    """(error, note) for one citation; see locate(). A note (the line was found at another number) is not a
    failure."""
    _, err, warn = locate(index, source, line, quote, sha)
    return err, warn


def cited_text(index: Index, source: str, line: str, quote: str, sha: str = "") -> str | None:
    n, err, _ = locate(index, source, line, quote, sha)
    if n is None:
        return None
    return (index.text(source) or "").split("\n")[n - 1]


CITED_TABLES = (ESTIMATORS, ALIASES, UNRESOLVED, ATTRIBUTION, STATUS, WAIVERS)


def repoint(index: Index, repo: Path) -> list[str]:
    """Refresh, in the working-tree TSVs, the line-number HINT of every citation whose whole line (same digest) now
    sits at another number. Never changes a quote or a digest, so an edited line is never accepted here."""
    report = []
    for table in CITED_TABLES:
        if not index.has(table):
            continue
        text = (repo / table).read_text()
        lines = text.split("\n")
        header = lines[0].split("\t")
        pre = "defining_" if "defining_source" in header else ""
        src_col, line_col = header.index(pre + "source"), header.index(pre + "line")
        quote_col, sha_col = header.index(pre + "quote"), header.index(pre + "line_sha256")
        changed = False
        for i in range(1, len(lines)):
            if not lines[i]:
                continue
            cells = lines[i].split("\t")
            src, ln, quote, sha = cells[src_col], cells[line_col], cells[quote_col], cells[sha_col]
            n, err, note = locate(index, src, ln, quote, sha)
            if n is not None and str(n) == ln:
                continue
            if n is not None:
                cells[line_col] = str(n)
                lines[i] = "\t".join(cells)
                changed = True
                report.append(f"REPOINTED {table} row {i + 1}: {src}:{ln} -> {n} (hint refreshed)")
            else:
                report.append(f"CANNOT REPOINT {table} row {i + 1}: {err}")
        if changed:
            (repo / table).write_text("\n".join(lines))
    return report


def verify_registry(index: Index) -> tuple[list[str], list[str]]:
    """(errors, warnings). Every ESTIMATORS definition, ALIASES row and UNRESOLVED-NAMES row cites a line that holds
    its quote (a quote moved to exactly one other line warns and passes); ids resolve; every alias pattern compiles;
    `identifying` is yes/no and `grep` is default/opt-in."""
    errs: list[str] = []
    warns: list[str] = []
    index.read_many([t for t in CITED_TABLES if index.has(t)])
    srcs = set()
    for t in CITED_TABLES:
        if index.has(t):
            for r in read_tsv(index, t):
                srcs.add(r.get("defining_source") or r.get("source", ""))
    index.read_many(sorted(s for s in srcs if s))  # one `git cat-file --batch` for every cited file

    def cite(label: str, row: dict) -> None:
        err, warn = verify_citation(index, *fields(row))
        if err:
            errs.append(f"{label}: {err}")
        if warn:
            warns.append(f"{label}: {warn}")

    ests = read_tsv(index, ESTIMATORS)
    ids = [e["id"] for e in ests]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        errs.append(f"ESTIMATORS: id {i} defined more than once")
    for e in ests:
        cite(f"ESTIMATORS {e['id']}", e)
    for n, a in enumerate(read_tsv(index, ALIASES), start=2):
        if a["estimator"] not in ids:
            errs.append(f"ALIASES row {n}: estimator {a['estimator']!r} is not an ESTIMATORS id")
        if a.get("identifying") not in ("yes", "no"):
            errs.append(f"ALIASES row {n} ({a['alias']}): identifying must be yes or no")
        if a.get("grep") not in ("default", "opt-in"):
            errs.append(f"ALIASES row {n} ({a['alias']}): grep must be default or opt-in")
        try:
            re.compile(a["pattern"])
        except re.error as exc:
            errs.append(f"ALIASES row {n} ({a['alias']}): pattern does not compile: {exc}")
        cite(f"ALIASES row {n} ({a['estimator']} / {a['alias']})", a)
    if index.has(UNRESOLVED):
        for n, u in enumerate(read_tsv(index, UNRESOLVED), start=2):
            cite(f"UNRESOLVED-NAMES row {n} ({u['name']})", u)
    return errs, warns


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("~", " ")).strip().lower()


def resolve(name: str, ests: list[dict], als: list[dict]) -> dict[str, list[str]]:
    """estimator id -> the reasons `name` names it: the union of an exact id or alias match, an alias pattern that
    matches the name, and the name occurring as a whole word inside an alias (so "R" finds "configuration 1 = R"
    and "400/31" finds both "refinement 400/31" and "capacity 400/31"). A reason through an alias marked
    identifying=no ends in "[non-identifying]"."""
    n = norm(name)
    word = re.compile(r"(?<![\w-])" + re.escape(name.strip()) + r"(?![\w-])") if name.strip() else None
    hits: dict[str, list[str]] = defaultdict(list)
    nonid_names = {norm(a["alias"]) for a in als if a.get("identifying", "yes") != "yes"}
    for e in ests:
        if norm(e["id"]) == n:
            hits[e["id"]].append("registry id")
    for a in als:
        tag = "" if a.get("identifying", "yes") == "yes" else " [non-identifying]"
        where = f"({a['kind']}, {a['source']}:{a['line']}){tag}"
        if norm(a["alias"]) == n:
            hits[a["estimator"]].append(f"alias {a['alias']!r} {where}")
            continue
        try:
            if re.search(a["pattern"], name):
                hits[a["estimator"]].append(f"pattern of alias {a['alias']!r} matches the name {where}")
                continue
        except re.error:
            pass
        if word and word.search(a["alias"]):
            # A name that IS a non-identifying alias (lgbm) stays non-identifying when it also appears as a word
            # inside some identifying alias's display text ("production 5D estimator (lgbm, ...)").
            wtag = tag or (" [non-identifying]" if n in nonid_names else "")
            hits[a["estimator"]].append(f"the name is a word of alias {a['alias']!r} "
                                        f"({a['kind']}, {a['source']}:{a['line']}){wtag}")
    return hits


def identifying(hits: dict[str, list[str]]) -> list[str]:
    """The estimators a resolution names through at least one IDENTIFYING alias (or the registry id)."""
    return sorted(e for e, why in hits.items() if any(not w.endswith("[non-identifying]") for w in why))


def unresolved(name: str, rows: list[dict]) -> list[dict]:
    n = norm(name)
    if not n:
        return []
    w = re.compile(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])")
    return [r for r in rows if w.search(norm(r["name"])) or norm(r["name"]) == n]


def tex_escape(s: str) -> str:
    out = []
    for ch in str(s):
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "{}_%#&$":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "-":
            out.append("-{}")  # no -- or --- ligature: a flag prints as typed
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch in "<>|":
            out.append({"<": r"\textless{}", ">": r"\textgreater{}", "|": r"\textbar{}"}[ch])
        elif ord(ch) > 126 or ord(ch) < 32:
            out.append(f"[U+{ord(ch):04X}]")
        else:
            out.append(ch)
    return "".join(out)


def tex_breakable(s: str) -> str:
    """Escaped text with a break opportunity after every / _ - . and , (for paths and key paths in narrow cells)."""
    out = []
    for ch in str(s):
        out.append(tex_escape(ch))
        if ch in "/_-.,":
            out.append(r"\allowbreak{}")
    return "".join(out)
