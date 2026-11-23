#!/usr/bin/env python3
"""Reorganize the records document (main_records.tex) by topic, following the note, and prove that nothing was lost.

usage:
  records_reorg.py inventory [--note-dir D] [--rev SHA] [--out FILE]
  records_reorg.py assemble  [--note-dir D] [--rev SHA] [--out-dir DIR]
  records_reorg.py check     --base SHA [--note-dir D]
  records_reorg.py dropped   --base SHA [--out FILE]
  records_reorg.py rekey     [--note-dir D] [--write]
  records_reorg.py --self-test

The records document grew by moves out of the note, lane by lane, one heading per moved sentence. This tool cuts the
records files that hold that moved text (SPLIT_FILES) into BLOCKS, one per heading, each with the % comment lines that
belong to it, routes every block to a section of a new table of contents that follows the note (records-reorg/toc.tsv,
records-reorg/rules.tsv), and writes one file per section. The files that the record checks pin by name
(check_note_records.py RECORD_FILES) are never split and never edited: the driver inputs them whole.

The data (all in records-reorg/):
  toc.tsv      dest, level (part|section|subsection), title, label, file[, inputs]: the new table of contents; a
               subsection titled "-" prints no heading, and `inputs` lists whole files it inputs (unsplit, unedited). Sections are printed by
               the driver between the RECORDS-REORG markers of main_records.tex, so that check_note_records.py's count of
               \\section before app_provenance stays right; each section's subsections and blocks go in its file.
  rules.tsv    dest, field, regex: first match routes a block. Fields: key, file, src (the source file named by the
               block's "% From <file>.tex" comment), title, text (the block's first printed line).
  groups.tsv   key, group, runin, order: blocks that share a group print as ONE paragraph under the run-in head of the
               group; their own headings go. Without a group a block keeps its heading, as a run-in \\paragraph.
  drops.tsv    kind (block|line|comment), key or exact text, reason: what leaves the printed records, each one listed for
               Joseph in DROPPED.md (`dropped`).
  demote.tsv   key, reason: blocks whose printed lines become % comments (kept in the source, not printed).
  adds.tsv     text, reason: printed lines the reorganization adds (a sentence carried over from a dropped copy, the
               driver's new opening). Every other printed line must already exist at the base.
  keep-leadin.tsv  row_id: register rows whose re-anchor lies inside a lead-in quote; those lead-ins stay printed.
  comment-fixes.tsv  old, new, reason: a base comment line corrected in place (2026-11-22); the old line may be lost
               only under its row, and the new line must be a comment line of the new records.

Option B (Joseph, 2026-11-21, via the director): every lead-in line "In the paragraph as the note printed it, this text
followed: ``...''\\par" is demoted to a % comment, except the lead-ins that hold a register row's re-anchor.

`check` is the invariance gate. Against the base commit it compares the printed LINES of the whole records closure
(comments, heading commands, \\label and \\input removed; whitespace collapsed): every base line must still print, or be
declared (a dropped block, a demoted block, a lead-in) and then present as a comment; every new line must be a base
line or listed in adds.tsv. Every base comment line must still be a comment line. Every register row located in the
records keeps its re-anchor verbatim in the closure. A re-wrapped line fails, because it is one lost and one new line.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = "records-reorg"
SPLIT_FILES = ("app_compression_records.tex", "records_compression_lr.tex", "records_compression_lr_p4.tex",
               "records_compression_h3.tex", "records_compression_h3_p6.tex", "records_compression_h3_p3c.tex",
               "records_compression_cv.tex", "records_compression_h3_rw.tex")
HEAD = re.compile(r"^\s*\\(part|section|subsection|subsubsection|paragraph)(\*?)\{")
LEVEL = {"part": -1, "section": 0, "subsection": 1, "subsubsection": 2, "paragraph": 3}
COMMENT = re.compile(r"(?<!\\)%.*")
LEADIN = re.compile(r"^\s*(?:In the paragraph as the note printed it, this text followed: ``.*''\\par"
                    r"|\\emph\{(?:After|Before),? in .*the note's ``.*''\})\s*$")
SRC = re.compile(r"^\s*%.*?\b[Ff]rom\s+(?:the note's\s+)?([A-Za-z0-9_]+)\.tex\b(?::(\d+))?")
INPUT = re.compile(r"\\(?:input|include)\{([^}]+)\}")
STRUCT = re.compile(r"^\\(?:input|include)\{[^}]*\}$")
DEMOTE_PREFIX = "% [records reorg, not printed] "
LEADIN_PREFIX = "% [lead-in, Option B] "
MARK_BEGIN, MARK_END = "% RECORDS-REORG BEGIN", "% RECORDS-REORG END"


# ---------------------------------------------------------------------------------------------------- reading
def git_show(rev: str, rel: str, cwd: Path) -> str | None:
    p = subprocess.run(["git", "show", f"{rev}:./{rel}"], cwd=cwd, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


class Tree:
    """docs/analysis-note as a working directory or at a commit."""

    def __init__(self, note_dir: Path, rev: str | None = None):
        self.dir, self.rev = note_dir, rev

    def read(self, name: str) -> str | None:
        if self.rev:
            return git_show(self.rev, name, self.dir)
        p = self.dir / name
        return p.read_text(encoding="utf-8") if p.exists() else None

    def closure(self, driver: str = "main_records.tex") -> dict[str, str]:
        out: dict[str, str] = {}

        def walk(name: str) -> None:
            name = name if name.endswith(".tex") else name + ".tex"
            if name in out:
                return
            text = self.read(name)
            if text is None:
                return
            out[name] = text
            for line in text.split("\n"):
                for m in INPUT.finditer(COMMENT.sub("", line)):
                    walk(m.group(1))
        walk(driver)
        return out


def heading_span(line: str) -> tuple[int, int, str] | None:
    """(start, end, title) of the heading command that opens `line`, braces balanced; None if no heading."""
    m = HEAD.match(line)
    if not m:
        return None
    i, depth = m.end() - 1, 0
    for j in range(i, len(line)):
        depth += {"{": 1, "}": -1}.get(line[j], 0) if line[j - 1:j] != "\\" else 0
        if depth == 0:
            return m.start(), j + 1, line[i + 1:j]
    raise SystemExit(f"records_reorg: unbalanced heading braces: {line[:100]!r}")


def strip_headings(line: str) -> str:
    """The printed text of a line with heading commands and labels removed."""
    while True:
        s = re.search(r"\\(part|section|subsection|subsubsection|paragraph)\*?\{", line)
        if not s:
            break
        sub = line[s.start():]
        span = heading_span(sub)
        line = line[:s.start()] + sub[span[1]:]
    return re.sub(r"\\label\{[^}]*\}", "", line)


def printed_lines(text: str) -> list[str]:
    out = []
    for line in text.split("\n"):
        if line.lstrip().startswith("%"):
            continue
        t = re.sub(r"\s+", " ", strip_headings(COMMENT.sub("", line))).strip()
        if t and not STRUCT.match(t):
            out.append(t)
    return out


def comment_lines(text: str) -> list[str]:
    return [l.strip() for l in text.split("\n") if l.lstrip().startswith("%")]


# ---------------------------------------------------------------------------------------------------- blocks
@dataclass
class Block:
    file: str
    start: int                      # 1-based line of the block's first line (a leading comment, or the heading)
    lines: list[str]
    head: int | None                # index into lines of the heading line
    level: int
    title: str
    key: str = ""
    src: str = ""
    src_line: int = 0
    regrows: list[str] = field(default_factory=list)

    @property
    def end(self) -> int:
        return self.start + len(self.lines) - 1

    def first_text(self) -> str:
        body = self.lines[self.head + 1:] if self.head is not None else self.lines
        lead = strip_headings(self.lines[self.head]).strip() if self.head is not None else ""
        for l in ([lead] if lead else []) + body:
            if l.strip() and not l.lstrip().startswith("%"):
                return l.strip()
        return ""


def split_blocks(name: str, text: str) -> list[Block]:
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    heads = [i for i, l in enumerate(lines) if HEAD.match(l)]
    cuts = []
    for h in heads:
        # A run of comment lines directly above a heading belongs to the heading's block when a blank line (or the
        # file start) separates it from the text above. A run that follows text with no blank line belongs to that
        # text's paragraph (a "% Search:" line supporting it, for instance), so it stays with the block above.
        c = h
        while c > 0 and lines[c - 1].lstrip().startswith("%"):
            c -= 1
        if c > 0 and lines[c - 1].strip():
            c = h
        cuts.append(c)
    bounds = ([0] if not cuts or cuts[0] > 0 else []) + cuts + [len(lines)]
    blocks = []
    for a, b in zip(bounds, bounds[1:]):
        seg = lines[a:b]
        h = next((k for k, l in enumerate(seg) if HEAD.match(l)), None)
        if h is None:
            blk = Block(name, a + 1, seg, None, -2, "(file preamble)")
        else:
            m = HEAD.match(seg[h])
            blk = Block(name, a + 1, seg, h, LEVEL[m.group(1)], heading_span(seg[h])[2])
        for l in seg:
            m = SRC.match(l)
            if m:
                blk.src, blk.src_line = m.group(1), int(m.group(2) or 0)
                break
        blocks.append(blk)
    seen: collections.Counter = collections.Counter()
    for blk in blocks:
        basis = "\n".join([blk.file, blk.lines[blk.head].strip() if blk.head is not None else "", blk.first_text()])
        k = hashlib.sha1(basis.encode()).hexdigest()[:10]
        seen[k] += 1
        blk.key = k if seen[k] == 1 else f"{k}-{seen[k]}"
    return blocks


def read_tsv(path: Path, ncols: int) -> list[list[str]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) < ncols:
            raise SystemExit(f"records_reorg: {path.name}: want {ncols} tab-separated cells: {line[:100]!r}")
        rows.append(cells)
    return rows[1:] if rows and rows[0][0] in ("dest", "key", "kind", "text", "row_id") else rows


PHASES = "BCD"


class Config:
    """The data of records-reorg/, filtered to a phase: B moves blocks with their headings as run-in heads; C also
    merges blocks into paragraphs, demotes lead-ins (Option B) and the demote.tsv blocks; D also applies the
    duplicate resolution (drops, cuts, carries). Rows of drops/demote/adds carry the phase that introduces them."""

    def __init__(self, note_dir: Path, phase: str = "D"):
        d = note_dir / DATA
        self.phase = phase
        on = lambda row, col, default: PHASES.index((row[col] if len(row) > col and row[col] else default)) <= PHASES.index(phase)
        self.toc = read_tsv(d / "toc.tsv", 5)
        self.rules = [(r[0], r[1], re.compile(r[2])) for r in read_tsv(d / "rules.tsv", 3)]
        self.titles = {r[0]: r for r in read_tsv(d / "titles.tsv", 2)} if self.merging else {}
        self.joins = {r[0]: r[1] for r in read_tsv(d / "joins.tsv", 2)} if self.merging else {}
        self.drops = [r for r in read_tsv(d / "drops.tsv", 3) if on(r, 3, "B")]
        self.demote = {r[0]: r[1] for r in read_tsv(d / "demote.tsv", 2) if on(r, 2, "C")}
        self.adds = [r for r in read_tsv(d / "adds.tsv", 2) if on(r, 2, "B")]
        self.cuts = [r for r in read_tsv(d / "cuts.tsv", 3)] if phase == "D" else []
        self.carries = [r for r in read_tsv(d / "carries.tsv", 5)] if phase == "D" else []
        # Joseph's rulings on the reorganized records (2026-11-21): a lead-in printed only because it holds a
        # register re-anchor that also prints elsewhere is demoted (demote-leadin.tsv: key, anchor, reason), and a
        # marker line is printed after a sentence (inserts.tsv: key, anchor, text, reason).
        self.demote_leadin = [r for r in read_tsv(d / "demote-leadin.tsv", 3)] if phase == "D" else []
        self.inserts = [r for r in read_tsv(d / "inserts.tsv", 4)] if phase == "D" else []
        self.keep_leadin = {r[0] for r in read_tsv(d / "keep-leadin.tsv", 1)}
        # 2026-11-22 (the director: a stale source comment is corrected through this data, so the gate covers it):
        # comment-fixes.tsv: old comment line, new comment line, reason. A base comment line may be lost only when a
        # row declares it, and the row's new line must then be a comment line of the new records.
        self.comment_fixes = [r for r in read_tsv(d / "comment-fixes.tsv", 3)]
        # Option B' (Joseph, 2026-11-21): a lead-in stays printed when the sentence after it would dangle.
        self.keep_context = {(r[0], r[1]) for r in read_tsv(d / "keep-leadin-context.tsv", 2)}
        self.splits: dict[str, list[str]] = collections.defaultdict(list)
        if self.merging:
            for r in read_tsv(d / "splits.tsv", 2):
                self.splits[r[0]].append(r[1])
        dests = {r[0] for r in self.toc}
        for dest, _, _ in self.rules:
            if dest not in dests and dest != "DROP":
                raise SystemExit(f"records_reorg: rules.tsv routes to {dest!r}, which toc.tsv does not define")

    @property
    def merging(self) -> bool:
        return self.phase in "CD"

    def dropped_keys(self) -> dict[str, str]:
        return {r[1]: r[2] for r in self.drops if r[0] == "block"}


def register_rows(tree: Tree) -> list[tuple[str, str]]:
    """(row_id, text) for each limitations-export row whose re-anchor (or quote) must be found in the records."""
    text = tree.read("limitations-export.tsv") or ""
    out = []
    for line in text.rstrip("\n").split("\n")[1:]:
        c = (line.split("\t") + [""] * 6)[:6]
        if c[4]:
            out.append((c[0], c[4]))
    return out


def apply_splits(blk: Block, anchors: list[str]) -> list[Block]:
    """splits.tsv: cut one block into paragraphs that can be placed apart. Each anchor is a substring of the first
    printed line of a new part; the comment lines directly above that line go with it. Part n has key <key>#n."""
    parts, cur = [], 0
    starts = []
    for anchor in anchors:
        hits = [i for i, l in enumerate(blk.lines) if anchor in l and not l.lstrip().startswith("%")]
        if len(hits) != 1:
            raise SystemExit(f"records_reorg: splits.tsv: anchor occurs {len(hits)} times in {blk.key}: {anchor[:60]!r}")
        i = hits[0]
        while i > 0 and blk.lines[i - 1].lstrip().startswith("%"):
            i -= 1
        starts.append(i)
    if starts != sorted(starts) or (starts and blk.head is not None and starts[0] <= blk.head):
        raise SystemExit(f"records_reorg: splits.tsv: anchors of {blk.key} are out of order or before its heading")
    bounds = [0] + starts + [len(blk.lines)]
    for n, (a, b) in enumerate(zip(bounds, bounds[1:])):
        if n == 0:
            part = Block(blk.file, blk.start, blk.lines[a:b], blk.head, blk.level, blk.title, blk.key, blk.src,
                         blk.src_line)
        else:
            part = Block(blk.file, blk.start + a, blk.lines[a:b], None, max(blk.level + 1, 3), "", f"{blk.key}#{n}",
                         blk.src, blk.src_line)
        parts.append(part)
    return parts


def all_blocks(tree: Tree, cfg: "Config | None" = None) -> list[Block]:
    regs = register_rows(tree)
    splits = cfg.splits if cfg else {}
    blocks = []
    for name in SPLIT_FILES:
        text = tree.read(name)
        if text is None:
            continue
        for whole in split_blocks(name, text):
            for blk in (apply_splits(whole, splits[whole.key]) if whole.key in splits else [whole]):
                body = "\n".join(blk.lines)
                blk.regrows = [rid for rid, q in regs if q in body]
                blocks.append(blk)
    return blocks


def route(blk: Block, cfg: Config) -> str:
    fields = {"key": blk.key, "file": blk.file, "src": blk.src, "title": blk.title, "text": blk.first_text()}
    for dest, fld, rx in cfg.rules:
        if rx.search(fields[fld]):
            return dest
    return ""


def routes(blocks: list[Block], cfg: Config) -> dict[str, str]:
    """key -> dest. A block no rule routes inherits the destination of its parent: the nearest earlier block of the
    same file with a higher heading level (a run-in \\paragraph under its \\subsection)."""
    out: dict[str, str] = {}
    stack: list[Block] = []
    for blk in blocks:
        if stack and stack[-1].file != blk.file:
            stack = []
        while stack and stack[-1].level >= blk.level:
            stack.pop()
        dest = route(blk, cfg)
        if not dest and stack:
            dest = out[stack[-1].key]
        out[blk.key] = dest
        if blk.level >= -1:
            stack.append(blk)
    return out


# ---------------------------------------------------------------------------------------------------- commands
def cmd_inventory(tree: Tree, cfg: Config, out: Path | None) -> int:
    rows = ["key\tfile\tstart\tend\tlevel\tsrc\tsrc_line\twords\tleadin\tregrows\tdest\ttitle\tfirst_text"]
    unrouted = 0
    blocks = all_blocks(tree, cfg)
    dests = routes(blocks, cfg)
    for blk in blocks:
        dest = dests[blk.key]
        unrouted += not dest
        words = sum(len(l.split()) for l in printed_lines("\n".join(blk.lines)))
        leadin = sum(bool(LEADIN.match(l)) for l in blk.lines)
        t = re.sub(r"\s+", " ", blk.title)[:90]
        rows.append("\t".join(map(str, [blk.key, blk.file, blk.start, blk.end, blk.level, blk.src, blk.src_line, words,
                                        leadin, ",".join(blk.regrows), dest or "UNROUTED", t,
                                        blk.first_text()[:90].replace("\t", " ")])))
    text = "\n".join(rows) + "\n"
    if out:
        out.write_text(text)
    else:
        sys.stdout.write(text)
    print(f"RECORDS-REORG inventory :: {len(rows) - 1} blocks, {unrouted} unrouted", file=sys.stderr)
    return 1 if unrouted else 0


ANAPHOR = re.compile(r"^(This|These|That|Those|It|Its|They|Their|Both|Each|Such|Here|There|The same|Neither|Either|"
                     r"Together|Instead|However|But|So|Thus|Hence|Also|Otherwise|In this|With this|With these|"
                     r"For these|For this|At this|Above|Below)\b")


def next_printed(lines: list[str], i: int) -> str:
    return next((x.strip() for x in lines[i + 1:] if x.strip() and not x.lstrip().startswith("%")), "")


def keeps_context(blk: Block, i: int, cfg: Config) -> bool:
    return (blk.key, next_printed(blk.lines, i)[:80]) in cfg.keep_context


PARA_KEY = re.compile(r"the paragraph beginning ``(.*?)(?:''|$)")
DROP_PREFIX = "% [records reorg, duplicate not printed] "
CUT_PREFIX = "% [records reorg, repeated sentence not printed] "


def auto_title(blk: Block) -> str:
    """A run-in title from a heading that already names its topic; "" when the heading only says where the text came
    from (the one-sentence moves), which titles.tsv must then name."""
    t = re.sub(r"\s+", " ", blk.title).strip()
    if not t or PARA_KEY.search(t) or re.match(r"^From (the note's|Part \d|App\.)", t):
        return ""
    t = re.sub(r"\s*\((?:from|caption pass)[^()]*(?:\([^()]*\)[^()]*)*\)\s*$", "", t)
    t = re.sub(r",? (?:formerly in the note|moved from the note.*)$", "", t)
    return t.rstrip(" .") + "."


def group_blocks(members: list[Block], cfg: Config) -> list[list[Block]]:
    """Phase C: the blocks of one destination as paragraphs. Blocks moved from the same note paragraph (the same
    "paragraph beginning" key and source file) form one paragraph, at the place of the first; joins.tsv puts a block
    into the paragraph of another; every other block is a paragraph of its own."""
    groups: dict[str, list[Block]] = {}
    order: list[str] = []
    for blk in members:
        m = PARA_KEY.search(re.sub(r"\s+", " ", blk.title))
        gid = cfg.joins.get(blk.key) or (f"P|{blk.src}|{m.group(1)[:40]}" if m else f"S|{blk.key}")
        if gid not in groups:
            groups[gid] = []
            order.append(gid)
        groups[gid].append(blk)
    if any(cfg.joins.get(b.key) not in (None,) and cfg.joins[b.key] not in groups for b in members):
        raise SystemExit("records_reorg: joins.tsv names a group that is not in the same destination")
    out = [groups[g] for g in order]
    first = lambda g: g[0].key
    explicit = {first(g): float(cfg.titles[first(g)][2]) for g in out
                if first(g) in cfg.titles and len(cfg.titles[first(g)]) > 2 and cfg.titles[first(g)][2]}
    return sorted(out, key=lambda g: (explicit.get(first(g), g[0].order)))


def group_title(group: list[Block], cfg: Config) -> str:
    row = cfg.titles.get(group[0].key)
    if row is not None:
        return row[1]
    return next((t for t in (auto_title(b) for b in group) if t), "")


def render_block(blk: Block, cfg: Config, keep_head: bool = False) -> list[str]:
    """The block's lines in its new place. Phase B: its heading becomes a run-in \\paragraph. Phase C/D: its heading
    goes (the group prints one run-in title); a lead-in is demoted unless it holds a register re-anchor; a demote.tsv
    block becomes comments. Phase D: a dropped duplicate becomes comments, a cut sentence leaves its line for a comment,
    a carried sentence follows its anchor line. Comments and labels always stay."""
    dropped = blk.key in cfg.dropped_keys()
    hide = DROP_PREFIX if dropped else DEMOTE_PREFIX if blk.key in cfg.demote else ""
    cuts = [r for r in cfg.cuts if r[0] == blk.key]
    carries = [r for r in cfg.carries if r[0] == blk.key]
    out = []
    for k, line in enumerate(blk.lines):
        if line.lstrip().startswith("%"):
            out.append(line)
            continue
        if SPLIT_INPUT.match(line):                 # a moved file inputs another: its blocks are placed on their own
            out.append(f"% [records reorg] {line.strip()}: its blocks are placed by the routing rules")
            continue
        if k == blk.head:
            s, e, title = heading_span(line)
            rest = line[e:]
            labels = "".join(re.findall(r"\\label\{[^}]*\}", rest))
            rest = re.sub(r"\\label\{[^}]*\}", "", rest)
            if keep_head:
                head = line[s:e]
            elif cfg.merging:
                head = ""
            elif blk.level == 3:
                head = line[s:e]
            else:
                t = title.strip()
                head = "\\paragraph{" + t + ("" if t.endswith((".", "?", ":")) else ".") + "}"
            out.append(f"% [records reorg] former heading: {line[s:e].strip()}")
            line = (head + labels + rest).rstrip()
            if not line.strip():
                continue
        if hide and line.strip():
            out.append(hide + line)
            continue
        forced = any(r[0] == blk.key and r[1] in line for r in cfg.demote_leadin)
        if cfg.merging and LEADIN.match(line) and (forced or (not leadin_holds_row(line, blk, cfg)
                                                              and not keeps_context(blk, k, cfg))):
            out.append(LEADIN_PREFIX + line.strip())
            continue
        for _, text, reason in [c[:3] for c in cuts]:
            if text in line:
                out.append(CUT_PREFIX + text)
                line = re.sub(r"  +", " ", line.replace(text, "")).rstrip()
        if line.strip():
            out.append(line)
        for _, anchor, text, reason in [c[:4] for c in cfg.inserts if c[0] == blk.key]:
            if anchor in line:
                out.append(f"% [records reorg] {reason}")
                out.append(text)
        for _, anchor, text, src, reason in [c[:5] for c in carries]:
            if anchor in line:
                out.append(f"% [records reorg] carried verbatim from the duplicate {src}: {reason}")
                out.append(text)
    while out and not out[-1].strip():
        out.pop()
    while out and not out[0].strip():
        out.pop(0)
    return out


_REG_CACHE: dict[str, str] = {}


def leadin_holds_row(line: str, blk: Block, cfg: Config) -> bool:
    """A lead-in stays printed if it holds the re-anchor of any register row (keep-leadin.tsv documents the five
    known at 1b04a91da; the test is the text itself, so a row added later is protected too)."""
    return any(q in line for q in _REG_CACHE.values())


def assemble(tree: Tree, cfg: Config) -> tuple[dict[str, str], str, list[str]]:
    """{file: text} for the new section files, the driver region, and the move-manifest rows."""
    for rid, q in register_rows(tree):
        _REG_CACHE[rid] = q
    blocks = all_blocks(tree, cfg)
    dests = routes(blocks, cfg)
    by_dest: dict[str, list[Block]] = collections.defaultdict(list)
    for n, blk in enumerate(blocks):
        dest = dests[blk.key]
        if not dest:
            raise SystemExit(f"records_reorg: block {blk.key} ({blk.file}:{blk.start}) is unrouted")
        blk.order = n
        by_dest[dest].append(blk)
    for key in [r[0] for r in cfg.cuts] + [r[0] for r in cfg.carries] + list(cfg.dropped_keys()) + list(cfg.demote):
        if key not in {b.key for b in blocks}:
            raise SystemExit(f"records_reorg: the data names block {key}, which is not a block of this tree")
    if cfg.merging:
        for blk in blocks:
            for i, l in enumerate(blk.lines):
                if (LEADIN.match(l) and not leadin_holds_row(l, blk, cfg) and not keeps_context(blk, i, cfg)
                        and ANAPHOR.match(next_printed(blk.lines, i))):
                    print(f"  WARN lead-in demoted before a dangling opening, not in keep-leadin-context.tsv: "
                          f"{blk.key} {next_printed(blk.lines, i)[:60]!r}", file=sys.stderr)
    files: dict[str, list[str]] = collections.defaultdict(list)
    driver = [MARK_BEGIN, "% Generated by records_reorg.py assemble from records-reorg/toc.tsv; edit the data, not this region."]
    manifest = []
    for row in cfg.toc:
        dest, level, title, label, fname = row[:5]
        inputs = [f for f in (row[5] if len(row) > 5 else "").split(",") if f]
        if level == "part":
            driver += ["\\part{" + title + "}"]
            continue
        if level == "section":
            driver += ["\\section{" + title + "}\\label{" + label + "}", f"\\input{{{fname[:-4]}}}"]
            files[fname]
            continue
        out = files[fname]
        out.append("")
        if title != "-":
            out.append("\\subsection{" + title + "}\\label{" + label + "}")
        out += [f"\\input{{{f}}}" for f in inputs]
        members = by_dest.get(dest, [])
        groups = group_blocks(members, cfg) if cfg.merging else [[b] for b in members]
        for n_group, group in enumerate(groups):
            head = group_title(group, cfg) if cfg.merging else ""
            if head == "-":                         # titles.tsv "-": the group continues the previous paragraph
                head = ""
            else:
                out.append("")
            if cfg.merging and not (title == "-" and n_group == 0):
                printing = [b for b in group if b.key not in cfg.dropped_keys() and b.key not in cfg.demote]
                if printing and head:
                    out.append("\\paragraph{" + head + "}")
            for n_member, blk in enumerate(group):
                out += render_block(blk, cfg, keep_head=(title == "-" and n_group == 0 and n_member == 0))
                manifest.append(f"RR-{blk.key}\t{blk.file}:{blk.start} @{tree.rev or 'worktree'}\t{fname}, {title}\t"
                                f"verbatim move, records reorganization (records/reorg-20261121)\t\t{blk.title[:120]}")
    driver.append(MARK_END)
    texts = {f: "% Generated by records_reorg.py assemble (records-reorg/); edit the data and re-run, not this file.\n"
                + "\n".join(v).lstrip("\n") + "\n" for f, v in files.items()}
    return texts, "\n".join(driver), manifest


OLD_INPUTS = ("app_compression_records", "records_compression_lr", "records_compression_lr_p4", "records_compression_h3",
              "records_compression_h3_p6", "records_compression_h3_p3c", "records_compression_cv")
SPLIT_INPUT = re.compile(r"^\s*\\input\{(" + "|".join(re.escape(f[:-4]) for f in SPLIT_FILES) + r")\}\s*$")
PROVENANCE_GROUP = "\\begingroup\n\\setlist[description]{format=\\recentrylabel}\n\\input{app_provenance}"


def rewrite_driver(main: str, region: str, opening: str) -> str:
    """main_records.tex with the generated region in place. The first time (no markers yet): the opening paragraph is
    replaced, the old result-package and codebase stubs and the moved-text inputs go, and the region is put before the
    provenance group, so the R-sections of Part I precede Part II. Every anchor must occur exactly once."""
    if MARK_BEGIN in main:
        a, b = main.index(MARK_BEGIN), main.index(MARK_END) + len(MARK_END)
        return main[:a] + region + main[b:]

    def once(text: str, old: str, new: str) -> str:
        if text.count(old) != 1:
            raise SystemExit(f"records_reorg: driver anchor occurs {text.count(old)} times: {old[:80]!r}")
        return text.replace(old, new)
    a = main.index("\\noindent This document holds")
    b = main.index("\n\n", a)
    main = main[:a] + opening.rstrip("\n") + main[b:]
    m = re.search(r"\\section\{Result package: fixed identities and audit record\}.*?\\input\{app_codebase_records\}\n", main, re.S)
    if not m:
        raise SystemExit("records_reorg: driver: the result-package and codebase stubs were not found")
    main = main[:m.start()] + main[m.end():]
    for name in OLD_INPUTS:
        main = once(main, f"\\input{{{name}}}\n", "")
    main = once(main, PROVENANCE_GROUP, region + "\n" + PROVENANCE_GROUP)
    return re.sub(r"\n{3,}", "\n\n", main)


def cmd_assemble(tree: Tree, cfg: Config, out_dir: Path) -> int:
    texts, driver, manifest = assemble(tree, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f, t in texts.items():
        (out_dir / f).write_text(t, encoding="utf-8")
    main = tree.read("main_records.tex")
    opening = (tree.dir / DATA / "opening.tex").read_text(encoding="utf-8")
    (out_dir / "main_records.tex").write_text(rewrite_driver(main, driver, opening), encoding="utf-8")
    (out_dir / "history-cuts").mkdir(exist_ok=True)
    (out_dir / "history-cuts" / "move-manifest-records-reorg-20261121.tsv").write_text("id\tfrom\tto\tmode\tsha256_utf8_no_newline\tsentence\n"
                                          + "\n".join(manifest) + "\n", encoding="utf-8")
    print(f"RECORDS-REORG assemble :: {len(texts)} section files and main_records.tex, {len(manifest)} blocks placed, "
          f"into {out_dir}; remove the moved files ({', '.join(OLD_INPUTS)}) with git rm")
    return 0


GENERATED = ("records_entry_numbers.tex", "records_results_index.tex", "records_estimators.tex", "records_earlier_labels.tex")


def check(base: Tree, new: Tree, cfg: Config) -> list[str]:
    """The invariance gate (module docstring). Generated files (GENERATED) are left out: they are regenerated, never
    edited, and records_entry_numbers.tex changes by design when the provenance section's number does."""
    fails = []
    old_c = {f: t for f, t in base.closure().items() if f not in GENERATED}
    new_c = {f: t for f, t in new.closure().items() if f not in GENERATED}
    old_p = collections.Counter(l for t in old_c.values() for l in printed_lines(t))
    new_p = collections.Counter(l for t in new_c.values() for l in printed_lines(t))
    old_k = collections.Counter(l for t in old_c.values() for l in comment_lines(t))
    new_k = collections.Counter(l for t in new_c.values() for l in comment_lines(t))

    def as_printed(comment: str) -> str:
        body = re.sub(r"^%\s*(\[[^]]*\]\s*)?", "", comment)
        return re.sub(r"\s+", " ", strip_headings(body)).strip()
    new_comment_text = "\n".join(as_printed(l) for l in new_k.elements())
    blocks = {b.key: b for b in all_blocks(base, cfg)}
    hidden = collections.Counter()         # base lines declared not printed: they must be in the new comments
    gone = collections.Counter()           # base lines declared removed outright (the driver's old opening)
    for kind, key, reason in [r[:3] for r in cfg.drops]:
        if kind == "block":
            if key not in blocks:
                fails.append(f"drops.tsv names block {key}, which is not a block at the base")
                continue
            hidden.update(printed_lines("\n".join(blocks[key].lines)))
        elif kind == "line":
            gone[re.sub(r"\s+", " ", key).strip()] += 1
    for key in cfg.demote:
        if key not in blocks:
            fails.append(f"demote.tsv names block {key}, which is not a block at the base")
            continue
        hidden.update(printed_lines("\n".join(blocks[key].lines)))
    # Cuts: each block's base lines are replaced by the lines without the cut sentences, applied in order; every cut
    # sentence must occur in exactly one line of its block and be a comment now.
    by_block: dict[str, list[str]] = collections.defaultdict(list)
    for key, text, reason in [r[:3] for r in cfg.cuts]:
        by_block[key].append(text)
    for key, texts in by_block.items():
        blk = blocks.get(key)
        if not blk:
            fails.append(f"cuts.tsv names block {key}, which is not a block at the base")
            continue
        before = printed_lines("\n".join(blk.lines))
        after = list(before)
        for text in texts:
            t = re.sub(r"\s+", " ", text).strip()
            hits = [i for i, l in enumerate(after) if t in l]
            if len(hits) != 1:
                fails.append(f"cuts.tsv: {key}: the sentence occurs in {len(hits)} printed lines of the block: {t[:80]!r}")
                continue
            after[hits[0]] = re.sub(r"\s+", " ", after[hits[0]].replace(t, "")).strip()
            if t not in new_comment_text:
                fails.append(f"cuts.tsv: {key}: the cut sentence is not kept as a comment: {t[:80]!r}")
        old_p.subtract(before)
        old_p.update(l for l in after if l)
    old_p = +old_p
    allowed = collections.Counter(re.sub(r"\s+", " ", r[0]).strip() for r in cfg.adds)
    for key, anchor, text, src, reason in [r[:5] for r in cfg.carries]:
        sblk = blocks.get(src)
        if not sblk or text not in "\n".join(sblk.lines):
            fails.append(f"carries.tsv: {key}: the carried sentence is not verbatim in its source block {src}")
        if src not in cfg.dropped_keys() and not any(c[0] == src and c[1] == text for c in cfg.cuts):
            fails.append(f"carries.tsv: {key}: its source {src} still prints the sentence (drop or cut it there)")
        allowed[re.sub(r"\s+", " ", text).strip()] += 1
    for key, anchor, text, reason in [r[:4] for r in cfg.inserts]:
        if key not in blocks or not any(anchor in l for l in blocks[key].lines):
            fails.append(f"inserts.tsv: {key}: the anchor is not in the block at the base: {anchor[:60]!r}")
        allowed[re.sub(r"\s+", " ", text).strip()] += 1
    for key, anchor, reason in [r[:3] for r in cfg.demote_leadin]:
        hits = [l for l in (blocks[key].lines if key in blocks else []) if anchor in l and LEADIN.match(l)]
        if len(hits) != 1:
            fails.append(f"demote-leadin.tsv: {key}: {len(hits)} lead-ins hold the anchor {anchor[:60]!r}")
    lost = old_p - new_p
    n_leadin = 0
    for line, n in lost.items():
        n -= min(n, gone[line])
        if n <= 0:
            continue
        is_leadin = cfg.merging and LEADIN.match(line) is not None
        n_leadin += n if is_leadin else 0
        if (hidden[line] or is_leadin) and line in new_comment_text:
            continue
        fails.append(f"LOST printed line ({n}x): {line[:160]!r}")
    added = new_p - old_p
    for line, n in added.items():
        if n > allowed[line]:
            fails.append(f"NEW printed line not declared ({n - allowed[line]}x): {line[:160]!r}")
    fixed = collections.Counter()
    for old_l, new_l, reason in [r[:3] for r in cfg.comment_fixes]:
        old_l, new_l = old_l.strip(), new_l.strip()
        if not old_k[old_l]:
            fails.append(f"comment-fixes.tsv: the old line is no base comment line: {old_l[:100]!r}")
        elif not new_k[new_l]:
            fails.append(f"comment-fixes.tsv: the new line is no comment line of the new records: {new_l[:100]!r}")
        elif not reason.strip():
            fails.append(f"comment-fixes.tsv: no reason for {old_l[:60]!r}")
        else:
            fixed[old_l] += 1
    for line, n in (old_k - new_k).items():
        if n - fixed[line] > 0:
            fails.append(f"LOST comment line ({n - fixed[line]}x): {line[:160]!r}")

    def uncommented(c: dict[str, str]) -> str:
        return "\n".join("\n".join(l for l in t.split("\n") if not l.lstrip().startswith("%")) for t in c.values())
    new_text, old_text = uncommented(new_c), uncommented(old_c)
    for rid, q in register_rows(new):
        if q in old_text and q not in new_text:
            fails.append(f"register row {rid}: its re-anchor printed in the records at the base and does not print now")
    print(f"RECORDS-REORG check (phase {cfg.phase}) :: base {sum(old_p.values())} printed / {sum(old_k.values())} "
          f"comment lines; new {sum(new_p.values())} / {sum(new_k.values())}; not printed: {sum(hidden.values())} "
          f"dropped or demoted, {n_leadin} lead-ins, {len(cfg.cuts)} cut sentences; removed {sum(gone.values())}; "
          f"added {sum(added.values())}", file=sys.stderr)
    return fails


def cmd_dropped(base: Tree, cfg: Config, out: Path | None) -> int:
    """DROPPED.md: every printed text the reorganization stops printing, for Joseph to accept or reject row by row."""
    blocks = {b.key: b for b in all_blocks(base, cfg)}

    def where(key: str) -> str:
        b = blocks.get(key)
        return f"`{b.file}:{b.start}-{b.end}`" if b else "NOT FOUND"

    def cell(t: str) -> str:
        return re.sub(r"\s+", " ", t).replace("|", "/")
    lines = ["# Not printed after the records reorganization", "",
             f"Base `{base.rev}`. Nothing below is deleted from the sources: every item stays in the reorganized "
             "`.tex` as a `%` comment beside the text it belonged to, and the base holds it as printed "
             f"(`git show {base.rev}:docs/analysis-note/<file>`). Joseph and the rewrite helper accept or reject each "
             "row; a rejected row is restored by deleting it from the named `records-reorg/` data file and re-running "
             "`records_reorg.py assemble`.", "",
             "Generated by `records_reorg.py dropped` from `records-reorg/drops.tsv`, `cuts.tsv`, `carries.tsv` and "
             "`demote.tsv`.", ""]
    rows = [r for r in cfg.drops if r[0] == "block"]
    lines += ["## 1. Duplicate copies not printed (`drops.tsv`)", "", "| # | Block | Base location | Heading | Reason |",
              "|---:|---|---|---|---|"]
    lines += [f"| {n} | `{k}` | {where(k)} | {cell(blocks[k].title if k in blocks else '')[:70]} | {cell(r)} |"
              for n, (_, k, r) in enumerate([x[:3] for x in rows], 1)]
    lines += ["", "## 2. Repeated sentences not printed (`cuts.tsv`)", "",
              "Each sentence prints, word for word or with the same content, in the paragraph named in the reason, "
              "which now precedes it.", "", "| # | Block | Base location | Sentence | Reason |", "|---:|---|---|---|---|"]
    lines += [f"| {n} | `{k}` | {where(k)} | {cell(t)[:160]} | {cell(r)} |"
              for n, (k, t, r) in enumerate([x[:3] for x in cfg.cuts], 1)]
    lines += ["", "## 3. Sentences carried from a dropped copy (`carries.tsv`)", "",
              "| # | Into block | Sentence | From | Reason |", "|---:|---|---|---|---|"]
    lines += [f"| {n} | `{k}` | {cell(t)} | `{src}` | {cell(r)} |"
              for n, (k, a, t, src, r) in enumerate([x[:5] for x in cfg.carries], 1)]
    lines += ["", "## 4. Paragraphs demoted to source comments (`demote.tsv`)", "",
              "| # | Block | Base location | Text | Reason |", "|---:|---|---|---|---|"]
    lines += [f"| {n} | `{k}` | {where(k)} | "
              f"{cell(' '.join(printed_lines(chr(10).join(blocks[k].lines))) if k in blocks else '')[:160]} | {cell(r)} |"
              for n, (k, r) in enumerate(cfg.demote.items(), 1)]
    drv = [r for r in cfg.drops if r[0] == "line"]
    lines += ["", "## 5. Driver text replaced (`drops.tsv`, kind `line`)", "",
              f"{len(drv)} printed lines of `main_records.tex`: the old opening paragraph (it described Sections R1--R4 "
              "as the October move) and the two stub sentences that introduced the result-package and codebase "
              "records. The new opening is `records-reorg/opening.tex`.", "",
              "## 6. Lead-ins (Option B)", "",
              "Every lead-in that quotes the note's text around a moved sentence is demoted to a comment: the line "
              "\"In the paragraph as the note printed it, this text followed: ``...''\\par\" and the italic "
              "\"\\emph{After|Before, in \\S..., the note's ``...''}\". A lead-in that holds a register re-anchor stays "
              "printed (`keep-leadin.tsv` lists the five at the base: n07, n09, n13, n38, n46), and so does a lead-in "
              "whose next sentence would dangle without it (Option B', `keep-leadin-context.tsv`, 42 lines). The count "
              "is in `records_reorg.py check`'s summary line."]
    text = "\n".join(lines) + "\n"
    (out.write_text(text) if out else sys.stdout.write(text))
    return 0


def cmd_rekey(tree: Tree, write: bool, base: Tree | None = None, cfg: "Config | None" = None) -> int:
    """Bookkeeping after the move, for the two records locators that name a file: point reanchor_file of each
    records-located limitations row, and each R:<file>::<text> probe of records-move-ledger.md, at the records file
    that now holds the text. A text found in no file or in several is left alone and reported, for the checks to fail."""
    rec = tree.closure()
    printed = {f: "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("%")) for f, t in rec.items()}
    gone = set(SPLIT_FILES)
    path = tree.dir / "limitations-export.tsv"
    lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
    changed, unresolved = 0, []
    for i, line in enumerate(lines[1:], 1):
        c = (line.split("\t") + [""] * 6)[:6]
        if c[3] not in gone:
            continue
        hits = [f for f, t in rec.items() if c[4] and c[4] in t]
        if len(hits) > 1 and base and cfg:          # the text prints twice: follow the block it was in at the base
            dest_file = {r[0]: r[4] for r in cfg.toc}
            blocks = all_blocks(base, cfg)
            dests = routes(blocks, cfg)
            own = [dest_file.get(dests[b.key]) for b in blocks if b.file == c[3] and c[4] in "\n".join(b.lines)]
            hits = [f for f in hits if f in own] or hits
        if len(hits) == 1:
            c[3] = hits[0]
            c[5] += " || re-keyed to the reorganized records file (records/reorg-20261121)"
            lines[i] = "\t".join(c)
            changed += 1
        else:
            unresolved.append(f"limitations row {c[0]}: {len(hits)} records files hold the re-anchor")
    ledger = tree.dir / "records-move-ledger.md"
    ltext = ledger.read_text(encoding="utf-8")
    n_probe = 0

    def fix(m: re.Match) -> str:
        nonlocal n_probe
        fname, text = m.group(1), m.group(2)
        if fname not in gone:
            return m.group(0)
        hits = [f for f, t in printed.items() if text in t]
        if len(hits) != 1:
            unresolved.append(f"ledger probe R:{fname}::{text[:50]!r}: {len(hits)} records files print it")
            return m.group(0)
        n_probe += 1
        return f"R:{hits[0]}::{text}"
    ltext = re.sub(r"R:([A-Za-z0-9_]+\.tex)::(.+?)(?=\s*(?:&&|`))", fix, ltext)
    # The estimator registry cites a source file, line and quote (tools/registry/check_registry.py); a row citing a
    # moved file is pointed at the file that now holds the quote (line hints: check_registry.py --repoint).
    reg_dir = tree.dir.parent / "orchestration" / "registry"
    reg_new: dict[Path, str] = {}
    n_reg = 0
    for reg in sorted(reg_dir.glob("*.tsv")) if reg_dir.exists() else []:
        rlines = reg.read_text(encoding="utf-8").rstrip("\n").split("\n")
        head = rlines[0].split("\t")
        pairs = [(head.index(sc), head.index(qc)) for sc, qc in (("source", "quote"), ("defining_source", "defining_quote"))
                 if sc in head and qc in head]
        changed_reg = False
        for i, line in enumerate(rlines[1:], 1):
            cells = line.split("\t")
            for si, qi in pairs:
                if si < len(cells) and cells[si].startswith("docs/analysis-note/") and cells[si][19:] in gone:
                    hits = [f for f, t in rec.items() if cells[qi] and cells[qi] in t]
                    if len(hits) == 1:
                        cells[si] = "docs/analysis-note/" + hits[0]
                        rlines[i] = "\t".join(cells)
                        n_reg += 1
                        changed_reg = True
                    else:
                        unresolved.append(f"registry {reg.name} row {i}: {len(hits)} records files hold the quote")
        if changed_reg:
            reg_new[reg] = "\n".join(rlines) + "\n"
    print(f"RECORDS-REORG rekey :: {n_reg} registry citations {'re-pointed' if write else 'would be re-pointed'}")
    if write:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        ledger.write_text(ltext, encoding="utf-8")
        for reg, text in reg_new.items():
            reg.write_text(text, encoding="utf-8")
    for u in unresolved:
        print("  UNRESOLVED " + u)
    print(f"RECORDS-REORG rekey :: {changed} limitations rows and {n_probe} ledger probes "
          f"{'re-keyed' if write else 'would be re-keyed'}; {len(unresolved)} unresolved")
    return 1 if unresolved else 0


# ---------------------------------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Plant a two-file records tree, reorganize it, and make the check fire on each kind of loss."""
    fails = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / DATA).mkdir()
        (d / "main_records.tex").write_text("\\begin{document}\n" + MARK_BEGIN + "\n\\input{records_compression_lr}\n"
                                            + MARK_END + "\n\\end{document}\n")
        (d / "records_compression_lr.tex").write_text(
            "\\section{Method detail moved from the note}\n\\label{app:lr}\nThis section holds moved text.\n\n"
            "\\subsection{From Part 2, sec_method.tex: the paragraph beginning ``A''}\n"
            "% From sec_method.tex:5 @abc; qualifier\n"
            "In the paragraph as the note printed it, this text followed: ``A sentence.''\\par\n"
            "The moved sentence one.\n\n"
            "\\subsection{From Part 2, sec_method.tex: the paragraph beginning ``A''}\n"
            "% From sec_method.tex:5 @abc; qualifier\n"
            "In the paragraph as the note printed it, this text followed: ``Kept lead-in with ROW TEXT.''\\par\n"
            "The moved sentence two.\n\n"
            "\\subsection{From App. A, app_statmethods.tex: the paragraph beginning ``B''}\n"
            "% From app_statmethods.tex:9 @abc\nA statistics sentence.\n")
        (d / "limitations-export.tsv").write_text("row_id\tfile\tquote\treanchor_file\treanchor_quote\tnote\n"
                                                  "r1\tx.tex\tq\trecords_compression_lr.tex\tROW TEXT\tn\n")
        (d / DATA / "toc.tsv").write_text("dest\tlevel\ttitle\tlabel\tfile\n"
                                          "R2\tsection\tMethod\trec:r2\trecords_r2_method.tex\n"
                                          "R2.1\tsubsection\tTraining\trec:r2-1\trecords_r2_method.tex\n"
                                          "R7\tsection\tStatistics\trec:r7\trecords_r7_stat.tex\n"
                                          "R7.1\tsubsection\tCovariance\trec:r7-1\trecords_r7_stat.tex\n")
        (d / DATA / "rules.tsv").write_text("dest\tfield\tregex\nR2.1\tsrc\t^sec_method$\nR7.1\tsrc\t^app_statmethods$\n"
                                            "R2.1\tfile\t.\n")
        (d / DATA / "keep-leadin.tsv").write_text("row_id\nr1\n")
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        subprocess.run(["git", "add", "-A"], cwd=d, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"], cwd=d, check=True)
        base_rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()

        def apply(mutate=None) -> list[str]:
            cfg = Config(d)
            texts, driver, _ = assemble(Tree(d, base_rev), cfg)
            for f, t in texts.items():
                (d / f).write_text(t)
            (d / "records_compression_lr.tex").unlink(missing_ok=True)
            main = git_show(base_rev, "main_records.tex", d)
            a, b = main.index(MARK_BEGIN), main.index(MARK_END) + len(MARK_END)
            (d / "main_records.tex").write_text(main[:a] + driver + main[b:])
            if mutate:
                mutate()
            return check(Tree(d, base_rev), Tree(d), Config(d))

        def reset():
            subprocess.run(["git", "checkout", "-q", "--", "."], cwd=d, check=True)
            for f in d.glob("records_r*.tex"):
                f.unlink()

        cases = [
            ("clean reorganization passes", None, False),
            ("a lost sentence fails", lambda: (d / "records_r2_method.tex").write_text(
                (d / "records_r2_method.tex").read_text().replace("The moved sentence one.\n", "")), True),
            ("a re-wrapped sentence fails", lambda: (d / "records_r7_stat.tex").write_text(
                (d / "records_r7_stat.tex").read_text().replace("A statistics sentence.", "A statistics\nsentence.")), True),
            ("an added sentence fails", lambda: (d / "records_r7_stat.tex").write_text(
                (d / "records_r7_stat.tex").read_text() + "An invented sentence.\n"), True),
            ("a lost comment fails", lambda: (d / "records_r7_stat.tex").write_text(
                (d / "records_r7_stat.tex").read_text().replace("% From app_statmethods.tex:9 @abc\n", "")), True),
            ("a register lead-in demoted fails", lambda: (d / "records_r2_method.tex").write_text(
                (d / "records_r2_method.tex").read_text().replace(
                    "In the paragraph as the note printed it, this text followed: ``Kept",
                    LEADIN_PREFIX + "In the paragraph as the note printed it, this text followed: ``Kept")), True),
        ]
        for name, mutate, want_fail in cases:
            reset()
            got = apply(mutate)
            if bool(got) != want_fail:
                fails.append(f"{name}: expected {'FAIL' if want_fail else 'PASS'}, got {got or 'PASS'}")
        reset()
        apply()
        r2 = (d / "records_r2_method.tex").read_text()
        if LEADIN_PREFIX + "In the paragraph as the note printed it, this text followed: ``A sentence." not in r2:
            fails.append("the ordinary lead-in was not demoted")
        if "\nIn the paragraph as the note printed it, this text followed: ``Kept lead-in" not in r2:
            fails.append("the register lead-in did not stay printed")
    for f in fails:
        print("  FAIL " + f)
    print(f"RECORDS-REORG self-test :: {'FAIL' if fails else 'PASS'} ({len(cases)} planted cases)")
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", choices=["inventory", "assemble", "check", "dropped", "rekey"])
    ap.add_argument("--note-dir", type=Path, default=HERE)
    ap.add_argument("--rev")
    ap.add_argument("--base")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--phase", choices=list(PHASES), default="D")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    cfg = Config(a.note_dir, a.phase)
    if a.cmd == "inventory":
        return cmd_inventory(Tree(a.note_dir, a.rev), cfg, a.out)
    if a.cmd == "assemble":
        return cmd_assemble(Tree(a.note_dir, a.rev), cfg, a.out_dir or a.note_dir)
    if a.cmd == "check":
        if not a.base:
            ap.error("check needs --base SHA")
        fails = check(Tree(a.note_dir, a.base), Tree(a.note_dir), cfg)
        for f in fails[:80]:
            print("  FAIL " + f)
        print(f"RECORDS-REORG check :: {'FAIL' if fails else 'PASS'} ({len(fails)} failures)")
        return 1 if fails else 0
    if a.cmd == "dropped":
        return cmd_dropped(Tree(a.note_dir, a.base), cfg, a.out)
    if a.cmd == "rekey":
        return cmd_rekey(Tree(a.note_dir), a.write, Tree(a.note_dir, a.base) if a.base else None, cfg)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
