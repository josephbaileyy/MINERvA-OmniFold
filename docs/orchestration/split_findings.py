#!/usr/bin/env python3
"""Split FINDINGS.md into a compact ACTIVE ledger + a byte-verbatim ARCHIVE.

Losslessness contract: every row line of the input appears byte-identical in the
archive, in the original order.

THIS SCRIPT IS NOT IDEMPOTENT AND MUST NOT BE RE-RUN ON ITS OWN OUTPUT. It is a
one-shot migration: it takes a full FINDINGS.md and splits it. Run a second time
on the already-split file, it would rewrite the archive from the *one-line* rows
and destroy the full text (measured: 330,018 B -> 26,465 B). The original commit
message claimed idempotence; that was wrong, and wrong in the destructive
direction, so the two guards below now fail closed. (BEN-200.)
"""
import re, sys, os

SRC = sys.argv[1]
ARCHIVE_NAME = "FINDINGS-ARCHIVE-2026-08.md"
CAP = 240
SENTINEL = "This is the ACTIVE ledger"

raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

# GUARD 1: refuse to run on an already-split source.
if SENTINEL in raw:
    sys.exit(
        f"REFUSING: {SRC} is already split (found the ACTIVE-ledger banner).\n"
        f"Re-running would rebuild {ARCHIVE_NAME} from the one-line rows and destroy\n"
        f"the full text. To re-do the migration, restore a pre-split FINDINGS.md first:\n"
        f"    git show <pre-split-sha>:docs/orchestration/FINDINGS.md > FINDINGS.md"
    )

row_idx = [i for i, l in enumerate(lines) if l.lstrip().startswith("| BEN-")]
assert row_idx, "no BEN rows found"
assert row_idx == list(range(row_idx[0], row_idx[-1] + 1)), "row block is not contiguous"
first, last = row_idx[0], row_idx[-1]

# header line of the table + its separator sit immediately above the row block
hdr_i = first - 2
sep_i = first - 1
assert lines[hdr_i].startswith("| id"), f"unexpected table header: {lines[hdr_i][:60]}"
assert set(lines[sep_i].replace("|", "").replace("-", "").strip()) <= set(""), \
    f"unexpected separator: {lines[sep_i][:60]}"

preamble = lines[:hdr_i]
rows = lines[first:last + 1]
trailer = lines[last + 1:]

def split_cells(line):
    s = line.strip()
    if s.startswith("|"): s = s[1:]
    if s.endswith("|"): s = s[:-1]
    return [c.strip() for c in s.split("|")]

def summarize(body):
    b = body.strip()
    m = re.match(r"\*\*(.+?)\*\*", b, re.S)
    cand = m.group(1).strip() if m else ""
    if not cand or len(cand) > CAP:
        # fall back to the first sentence of the plain text
        plain = re.sub(r"\*\*", "", b)
        m2 = re.search(r"(?<![A-Z])\.\s", plain)
        cand = plain[:m2.start() + 1] if m2 and m2.start() + 1 <= CAP else plain
    cand = re.sub(r"\*\*", "", cand)
    cand = re.sub(r"\s+", " ", cand).strip()
    if len(cand) > CAP:
        cand = cand[:CAP - 1].rstrip() + "…"
    return cand.replace("|", r"\|")

active_rows, archive_rows, report = [], [], []
for line in rows:
    cells = split_cells(line)
    assert len(cells) >= 3, f"row has too few cells: {line[:80]}"
    ben_id  = cells[0]
    episode = cells[-1]
    cross   = cells[-2]
    body    = "|".join(cells[1:-2]) if len(cells) > 3 else cells[1]
    summ    = summarize(body)
    active_rows.append(f"| {ben_id} | {summ} | {cross} | {episode} |")
    archive_rows.append(line)
    report.append((ben_id, len(body), len(summ)))

ACTIVE_NOTE = f"""
> **This is the ACTIVE ledger: one line per finding.** The full text of every row —
> unchanged, byte for byte — lives in [`{ARCHIVE_NAME}`]({ARCHIVE_NAME}). To read a
> finding in full, `grep -n 'BEN-0XX' docs/orchestration/{ARCHIVE_NAME}`.
> **Add new findings here as one line (≤{CAP} chars) and put the long form in a
> `FINDING-<date>-<slug>.md`.** A row that outgrows one line is a row that belongs in
> its own file — this ledger reached 330 KB (≈78k tokens, 73% of a context window when
> combined with the rest of the prescribed read path) because that rule had no enforcement.
"""

out_active = "\n".join(preamble + [ACTIVE_NOTE, lines[hdr_i], lines[sep_i]] + active_rows + trailer)
if not out_active.endswith("\n"):
    out_active += "\n"

archive_hdr = f"""# FINDINGS archive — full text of every BEN row (through 2026-08-12)

Split out of `FINDINGS.md` on 2026-08-12. **Nothing here is edited, retired, or summarised:**
these are the original rows, byte for byte, in their original order. `FINDINGS.md` now carries
a one-line version of each and is the file agents read; this file is the reference you `grep`
when a one-liner is not enough.

Do not append new findings here — new rows go to `FINDINGS.md`, and their long form goes to a
`FINDING-<YYYYMMDD>-<slug>.md`.

"""
out_archive = archive_hdr + lines[hdr_i] + "\n" + lines[sep_i] + "\n" + "\n".join(archive_rows) + "\n"

dest = os.path.dirname(SRC)
archive_path = os.path.join(dest, ARCHIVE_NAME)

# GUARD 2: never shrink an existing archive. Guard 1 catches the ordinary re-run;
# this catches every other route to the same loss (renamed sentinel, hand-edited
# banner, a truncated source), because the archive only ever grows.
if os.path.exists(archive_path):
    existing = os.path.getsize(archive_path)
    if len(out_archive.encode("utf-8")) < existing:
        sys.exit(
            f"REFUSING: would shrink {ARCHIVE_NAME} from {existing:,} B to "
            f"{len(out_archive.encode('utf-8')):,} B.\nThe archive is append-only; "
            f"a smaller rewrite means the source was already split or truncated."
        )

open(SRC, "w", encoding="utf-8").write(out_active)
open(archive_path, "w", encoding="utf-8").write(out_archive)

print(f"rows processed: {len(rows)}")
print(f"active  : {len(out_active):>8,} B (~{len(out_active)//4:,} tok)")
print(f"archive : {len(out_archive):>8,} B (~{len(out_archive)//4:,} tok)")
print(f"original: {len(raw):>8,} B (~{len(raw)//4:,} tok)")
print(f"read-path reduction: {100 - len(out_active)*100//len(raw)}%")
over = [r for r in report if r[2] > CAP]
print("summaries over cap:", len(over))
