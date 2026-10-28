"""F1 amendment 2, section 7: every cluster command touching F1b's f1b/ after Joseph's "never read" decision
(2b1c9d63, 2026-10-27 19:56:16 PDT = 2026-10-28T02:56:16Z), from the measurement session's transcripts.

Reads the session transcript <base>.jsonl and every <base>/subagents/*.jsonl (local to the machine the session ran on;
they are not in git, so this script's output, disclosure-sweep.out, is the committed receipt). A command is selected if
it is a Bash or Monitor command after the decision that runs ssh (or feeds `bash -s`) and names an f1b/ path anywhere in
its body (f1b2/ and f1b3/ excluded), directly or through a variable. Prints:
  1. each selected command's complete body, numbered C1, C2, ..., with its timestamp and transcript;
  2. for each, every body line that names a gst, ghep or ROOT file, or calls a reader of file content (cat, head,
     tail, grep, awk on a file, wc, sha256sum, md5sum, python, root, uproot, RDataFrame, TFile, hadd, cp, scp, rsync,
     tar, od, xxd, strings), so content access can be judged line by line;
  3. the complete outputs of the selected commands that list access times (find -printf %A, ls --time=atime).
Usage: python3 -I disclosure_sweep.py <transcript base without .jsonl>"""
import glob
import json
import os
import re
import sys

base = sys.argv[1]
files = [base + ".jsonl"] + sorted(glob.glob(base + "/subagents/*.jsonl"))
DECISION = "2026-10-28T02:56:16"
F1B = re.compile(r"fd-f1-20261027/f1b(?![23])|\$OUT/f1b(?![23])|\$O/f1b(?![23])|\bf1b/(work|logs|gst|gen5d|prep)"
                 r"|fd-f1-20261027 && .*\bf1b\b")
FILEKIND = re.compile(r"\b(gst|ghep)\b|\.root\b")
READER = re.compile(r"(^|[\s|;(&])(cat|head|tail|grep|awk|wc|sha256sum|md5sum|python3?|root|uproot|RDataFrame|TFile|hadd|"
                    r"cp|scp|rsync|tar|od|xxd|strings)\b")
ATIME = re.compile(r"%A|--time=atime")
cmds, want, results = [], {}, {}
for fn in files:
    for line in open(fn):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("message", {})
        c = m.get("content") if isinstance(m, dict) else None
        if not isinstance(c, list):
            continue
        ts = d.get("timestamp", "")
        for b in c:
            if b.get("type") == "tool_result" and b.get("tool_use_id") in want:
                out = b.get("content")
                if isinstance(out, list):
                    out = "\n".join(x.get("text", "") for x in out if isinstance(x, dict))
                results[b["tool_use_id"]] = out
            if b.get("type") != "tool_use" or b.get("name") not in ("Bash", "Monitor") or ts < DECISION:
                continue
            s = b.get("input", {}).get("command", "")
            if not (re.search(r"\bssh\s+(-\S+\s+)*saul", s) or "bash -s" in s) or not F1B.search(s):
                continue
            cmds.append((ts, os.path.basename(fn), b["id"], s))
            if ATIME.search(s):
                want[b["id"]] = len(cmds)
cmds.sort()
print(f"transcripts read: {len(files)}; decision boundary {DECISION}Z; selected commands: {len(cmds)}")
print("\n== 1. selected commands, complete")
for i, (ts, src, _, s) in enumerate(cmds, 1):
    print(f"\n[C{i}] {ts} {src}\n{s}")
print("\n== 2. per command: lines naming a gst/ghep/.root file or calling a content reader")
for i, (ts, src, _, s) in enumerate(cmds, 1):
    lines = [l for l in s.splitlines() if FILEKIND.search(l) or READER.search(l)]
    print(f"\n[C{i}] {len(lines)} line(s)")
    for l in lines:
        tags = []
        if FILEKIND.search(l):
            tags.append("FILE:" + ",".join(sorted(set(x.group(0) for x in FILEKIND.finditer(l)))))
        if READER.search(l):
            tags.append("READ:" + ",".join(sorted(set(x.group(2) for x in READER.finditer(l)))))
        print(f"  {' '.join(tags):40s} | {l.strip()}")
print("\n== 3. outputs of the selected access-time commands, complete")
order = {b_id: n for b_id, n in want.items()}
for i, (ts, src, b_id, s) in enumerate(cmds, 1):
    if b_id in order:
        print(f"\n[C{i}] {ts} {src}\n{results.get(b_id) or '(no result recorded)'}")
