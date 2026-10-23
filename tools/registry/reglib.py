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


def git_env() -> dict:
    """The environment with every GIT_* variable removed except the index file a hook may set."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    if "GIT_INDEX_FILE" in os.environ:
        # A hook run by `git commit -a`/`--only` uses a temporary index; honour it so the check judges the
        # index the commit is being built from.
        env["GIT_INDEX_FILE"] = os.environ["GIT_INDEX_FILE"]
    return env


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    out = subprocess.run(["git", "-C", str(repo), *args], input=input_bytes, capture_output=True,
                         env=git_env())
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


def locate(index: Index, source: str, line: str, quote: str) -> tuple[int | None, str | None, str | None]:
    """Where the cited quote is: (line number, error, warning).

    The quote on its cited line: (n, None, None). The quote MOVED to exactly one other line of the same file: (that
    line, None, a warning naming it) -- the citation still identifies one line, so this passes and
    `check_registry.py --repoint` updates the number. The quote absent, or on several other lines: (None, error, None).
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
    lines = text.split("\n")
    if 1 <= n <= len(lines) and quote in lines[n - 1]:
        return n, None, None
    now = [i for i, l in enumerate(lines, start=1) if quote in l]
    if len(now) == 1:
        return now[0], None, (f"{source}:{n} no longer holds the quote {quote!r}; it is on line {now[0]} only "
                              "(passes; run `python3 tools/registry/check_registry.py --repoint`)")
    if now:
        return None, (f"{source}:{n} does not hold the quote {quote!r}, which occurs on {len(now)} other lines "
                      f"({', '.join(map(str, now[:5]))}): re-point the row by hand"), None
    return None, f"{source}:{n}: the quote {quote!r} is no longer in the file: re-source the row", None


def verify_citation(index: Index, source: str, line: str, quote: str) -> tuple[str | None, str | None]:
    """(error, warning) for one citation; see locate()."""
    _, err, warn = locate(index, source, line, quote)
    return err, warn


def cited_text(index: Index, source: str, line: str, quote: str) -> str | None:
    n, err, _ = locate(index, source, line, quote)
    if n is None:
        return None
    return (index.text(source) or "").split("\n")[n - 1]


CITED_TABLES = (ESTIMATORS, ALIASES, UNRESOLVED, ATTRIBUTION, STATUS)


def repoint(index: Index, repo: Path) -> list[str]:
    """Rewrite, in the working-tree TSVs, the line number of every citation whose quote moved to exactly one other
    line of its (staged) source. Returns what changed and what could not be fixed. Never changes a quote."""
    report = []
    for table in CITED_TABLES:
        if not index.has(table):
            continue
        text = (repo / table).read_text()
        lines = text.split("\n")
        header = lines[0].split("\t")
        src_col = header.index("defining_source") if "defining_source" in header else header.index("source")
        line_col = header.index("defining_line") if "defining_line" in header else header.index("line")
        quote_col = header.index("defining_quote") if "defining_quote" in header else header.index("quote")
        changed = False
        for i in range(1, len(lines)):
            if not lines[i]:
                continue
            cells = lines[i].split("\t")
            src, ln, quote = cells[src_col], cells[line_col], cells[quote_col]
            n, err, warn = locate(index, src, ln, quote)
            if n is not None and not warn:
                continue
            if n is not None:
                cells[line_col] = str(n)
                lines[i] = "\t".join(cells)
                changed = True
                report.append(f"REPOINTED {table} row {i + 1}: {src}:{ln} -> {n}")
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

    def cite(label: str, source: str, line: str, quote: str) -> None:
        err, warn = verify_citation(index, source, line, quote)
        if err:
            errs.append(f"{label}: {err}")
        if warn:
            warns.append(f"{label}: {warn}")

    ests = read_tsv(index, ESTIMATORS)
    ids = [e["id"] for e in ests]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        errs.append(f"ESTIMATORS: id {i} defined more than once")
    for e in ests:
        cite(f"ESTIMATORS {e['id']}", e["defining_source"], e["defining_line"], e["defining_quote"])
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
        cite(f"ALIASES row {n} ({a['estimator']} / {a['alias']})", a["source"], a["line"], a["quote"])
    if index.has(UNRESOLVED):
        for n, u in enumerate(read_tsv(index, UNRESOLVED), start=2):
            cite(f"UNRESOLVED-NAMES row {n} ({u['name']})", u["source"], u["line"], u["quote"])
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
            hits[a["estimator"]].append(f"the name is a word of alias {a['alias']!r} {where}")
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
