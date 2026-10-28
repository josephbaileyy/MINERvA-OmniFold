"""F1 amendment 2, section 7: every cluster command touching F1b's f1b/ after Joseph's "never read" decision
(2b1c9d63, 2026-10-27 19:56:16 PDT = 2026-10-28T02:56:16Z), from the measurement session's transcripts.

Reads the session transcript <base>.jsonl and every <base>/subagents/*.jsonl (local to the machine the session ran on;
they are not in git, so this script's output, disclosure-sweep.out, is the committed receipt). Prints:
  1. every line of a Bash or Monitor command sent over ssh (or fed to `bash -s`) after the decision that names an f1b/
     path (f1b2/ and f1b3/ excluded), with its timestamp and transcript;
  2. the subset of those lines naming gst, ghep, ROOT, RDataFrame, TFile or uproot;
  3. the outputs of the F1a′ receipts review's access-time commands (find/ls printing atimes over f1b/).
Usage: python3 -I disclosure_sweep.py <transcript base without .jsonl>"""
import glob
import json
import os
import re
import sys

base = sys.argv[1]
files = [base + ".jsonl"] + sorted(glob.glob(base + "/subagents/*.jsonl"))
DECISION = "2026-10-28T02:56:16"
F1B = re.compile(r"(fd-f1-20261027/f1b(?![23])|\$OUT/f1b(?![23])|\$O/f1b(?![23])|\bf1b/(work|logs|gst|gen5d|prep)"
                 r"|cd \S*fd-f1-20261027 && .*\bf1b\b)")
ROOTISH = re.compile(r"\b(gst|ghep|ROOT|RDataFrame|TFile|uproot)\b")
ATIME = re.compile(r"%A|--time=atime")
hits, rootish, results = [], [], {}
want = {}
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
            if "ssh" not in s and "bash -s" not in s:
                continue
            matched = [l for l in s.splitlines() if F1B.search(l)]
            src = os.path.basename(fn)
            for l in matched:
                hits.append((ts, src, l.strip()))
                if ROOTISH.search(l):
                    rootish.append((ts, src, l.strip()))
            if matched and ATIME.search(s) and "ssh saul" in s:
                want[b["id"]] = (ts, src, s.strip())
print(f"transcripts read: {len(files)}; decision boundary {DECISION}Z")
print(f"\n== 1. cluster command lines naming f1b/ after the decision: {len(hits)}")
for ts, src, l in sorted(hits):
    print(f"{ts} {src[:28]} | {l[:300]}")
print(f"\n== 2. of those, lines naming gst/ghep/ROOT/RDataFrame/TFile/uproot: {len(rootish)}")
for ts, src, l in sorted(rootish):
    print(f"{ts} {src[:28]} | {l[:300]}")
print(f"\n== 3. outputs of the access-time commands over f1b/: {len(want)}")
for tid, (ts, src, s) in sorted(want.items(), key=lambda kv: kv[1][0]):
    print(f"--- {ts} {src[:28]}\n$ {s[:400]}\n{(results.get(tid) or '(no result recorded)')[:3000]}")
