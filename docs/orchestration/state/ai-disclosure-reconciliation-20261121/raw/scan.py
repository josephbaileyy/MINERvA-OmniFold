"""Read-only scan of local agent session stores for model identifiers. One row per (tool, account, model, analysis?):
sessions, first and last timestamp, and an example file. 'analysis' = the session's working directory (or, failing
that, its store path) names MINERvA-OmniFold / minerva / omnifold."""
import json, os, re, sys, glob, subprocess, collections, datetime as dt
HOME = os.path.expanduser("~")
AN = re.compile(r"minerva|omnifold", re.I)
rows = collections.defaultdict(lambda: {"sessions": set(), "first": None, "last": None, "example": None, "msgs": 0})

def iso(ts):
    if ts is None: return None
    if isinstance(ts, (int, float)):
        ts = ts / 1000 if ts > 1e12 else ts
        return dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(ts)[:19] + "Z" if "T" in str(ts) else str(ts)

def add(tool, acct, model, analysis, sess, ts, path):
    r = rows[(tool, acct, model, analysis)]
    r["sessions"].add(sess); r["msgs"] += 1
    t = iso(ts)
    if t:
        r["first"] = t if not r["first"] or t < r["first"] else r["first"]
        r["last"] = t if not r["last"] or t > r["last"] else r["last"]
    if not r["example"]: r["example"] = path

# Claude Code: projects/**/*.jsonl, assistant message.model; cwd field
for acct in (".claude", ".claude-personal", ".claude-school"):
    for f in glob.glob(f"{HOME}/{acct}/projects/**/*.jsonl", recursive=True):
        cwd = None
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    if '"cwd"' in line and cwd is None:
                        m = re.search(r'"cwd":"([^"]*)"', line); cwd = m.group(1) if m else None
                    if '"model"' not in line: continue
                    try: o = json.loads(line)
                    except Exception: continue
                    msg = o.get("message") if isinstance(o.get("message"), dict) else {}
                    model = msg.get("model")
                    if not model or model == "<synthetic>": continue
                    an = bool(AN.search(o.get("cwd") or cwd or f))
                    add("claude-code", acct, model, an, f, o.get("timestamp"), f)
        except OSError: pass

# Codex: sessions/**/rollout-*.jsonl and archived_sessions; turn_context.payload.model; session_meta.payload.cwd
for acct in (".codex", ".codex-personal", ".codex-school", ".codex-school2"):
    files = glob.glob(f"{HOME}/{acct}/sessions/**/*.jsonl", recursive=True) + glob.glob(f"{HOME}/{acct}/archived_sessions/**/*.jsonl", recursive=True)
    for f in files:
        cwd = None
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    if '"session_meta"' in line or ('"cwd"' in line and cwd is None):
                        m = re.search(r'"cwd":"([^"]*)"', line)
                        if m: cwd = m.group(1)
                    if '"model"' not in line: continue
                    try: o = json.loads(line)
                    except Exception: continue
                    p = o.get("payload") if isinstance(o.get("payload"), dict) else {}
                    if o.get("type") != "turn_context" and "model" not in p: continue
                    model = p.get("model")
                    if not model: continue
                    an = bool(AN.search(p.get("cwd") or cwd or ""))
                    add("codex", acct, model, an, f, o.get("timestamp"), f)
        except OSError: pass

# Grok: sessions/<url-encoded cwd>/<session>/...: model_id fields
for f in glob.glob(f"{HOME}/.grok/sessions/**/*", recursive=True):
    if not os.path.isfile(f) or f.endswith(".sqlite"): continue
    rel = os.path.relpath(f, f"{HOME}/.grok/sessions")
    parts = rel.split(os.sep)
    if len(parts) < 3: continue
    cwd = parts[0].replace("%2F", "/"); sess = parts[1]
    try: text = open(f, errors="replace").read()
    except OSError: continue
    for m in set(re.findall(r'"model(?:_id|Id)?":"([^"]+)"', text)):
        an = bool(AN.search(cwd))
        ts = re.findall(r'"(?:timestamp|created_at|createdAt)":"?([0-9T:.Z-]{10,})', text)
        add("grok", ".grok", m, an, sess, min(ts) if ts else os.path.getmtime(f), f)
        if ts: add("grok", ".grok", m, an, sess, max(ts), f)

# Antigravity (agy): conversations/*.db (+ .pb); model labels from strings; workspace from strings; time = mtime
LBL = re.compile(r"(Gemini [0-9.]+ (?:Pro|Flash)(?: Lite)?(?: \((?:High|Low|Medium)\))?|gemini-[0-9][0-9a-z.-]*|claude-[a-z]+-[0-9][0-9a-z.-]*|Claude (?:Opus|Sonnet|Haiku) [0-9.]+(?: \(Thinking\))?|gpt-oss[-0-9a-z]*|GPT-OSS[ 0-9A-Za-z]*)")
for acct in ("antigravity", "antigravity-cli"):
    for f in glob.glob(f"{HOME}/.gemini/{acct}/conversations/*"):
        if f.endswith(("-shm", "-wal")) : continue
        try:
            s = subprocess.run(["strings", f], capture_output=True, text=True, errors="replace").stdout
            if os.path.exists(f + "-wal"):
                s += subprocess.run(["strings", f + "-wal"], capture_output=True, text=True, errors="replace").stdout
        except Exception: continue
        labels = set(LBL.findall(s))
        an = bool(AN.search(s))
        st = os.stat(f)
        for m in labels:
            add("antigravity", acct, m, an, f, getattr(st, "st_birthtime", st.st_mtime), f)
            add("antigravity", acct, m, an, f, st.st_mtime, f)

out = []
for (tool, acct, model, an), r in sorted(rows.items()):
    out.append({"tool": tool, "account": acct, "model": model, "analysis": an, "sessions": len(r["sessions"]),
                "records": r["msgs"], "first": r["first"], "last": r["last"], "example": r["example"]})
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(len(out), "rows")
