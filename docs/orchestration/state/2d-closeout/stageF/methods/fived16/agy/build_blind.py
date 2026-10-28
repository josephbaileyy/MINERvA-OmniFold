"""Build the blind agy input for one group of note files.

usage: build_blind.py BASE_DIR TREE_DIR LEDGER.md OUT_DIR file1,file2,...   (writes OUT_DIR/blind.{passages,context}.txt)

Passages: every changed paragraph of the named files, BEFORE (BASE_DIR) and AFTER (TREE_DIR). Context: per ledger row
that names a passage, the row's fact (any review note removed) and each N: home probe in its full paragraph of TREE_DIR.
Blind: the context carries no disposition column, no probe that TREE_DIR does not print, and no probe that is the
passage's own text, so the rater is not handed the fix. Run with register-method/tools/run_x.sh gemini prompt.md OUT
blind.context.txt blind.passages.txt."""
import re, sys, difflib, os
BASE, CUR, LEDGER, OUT = sys.argv[1:5]
ONLY = sys.argv[5].split(",") if len(sys.argv) > 5 else None   # blind build: one group of these files
GROUPS = {"g1": ["selection_features", "sec_method", "sec_systematics", "sec_validation"],
          "g2": ["sec_3d", "sec_eavailw"], "g3": ["sec_5d", "sec_joint"],
          "g4": ["app_statmethods", "app_negweight", "app_guide", "app_codebase"],
          "g5": ["sec_execsummary", "sec_intro", "sec_summary"]}
strip = lambda l: " ".join(re.sub(r"(?<!\\)%.*", "", l).split())
def paras(path):
    return [strip(l) for l in open(path, encoding="utf-8")]
rows = []
for l in open(LEDGER, encoding="utf-8"):
    if l.startswith("| ") and not l.startswith("| id ") and not l.startswith("|---"):
        c = [x.strip() for x in l.rstrip("\n").split(" | ")]
        def unwrap(p):
            p = p.strip().rstrip("|").strip()
            return p[1:-1] if len(p) > 1 and p[0] == "`" and p[-1] == "`" and p[1] != "`" else p
        probes = [unwrap(p) for p in c[-1].split(" && ")]
        rows.append((c[0].lstrip("| "), c[1], c[3], probes))
def home_para(fname, text):
    p = os.path.join(CUR, fname)
    if not os.path.exists(p): return None
    for s in paras(p):
        if text in s: return s
    whole = " ".join(x for x in paras(p) if x)   # a home whose source spans several lines (a table or caption)
    i = whole.find(text)
    return None if i < 0 else "..." + whole[max(0, i - 900):i + len(text) + 900] + "..."
if ONLY: GROUPS = {"blind": ONLY}
for g, files in GROUPS.items():
    P, C, n = [], [], 0
    used = set()
    for f in files:
        b, a = paras(f"{BASE}/{f}.tex"), paras(f"{CUR}/{f}.tex")
        sm = difflib.SequenceMatcher(None, b, a, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal": continue
            bt = "\n".join(x for x in b[i1:i2] if x); at = "\n".join(x for x in a[j1:j2] if x)
            if not bt and not at: continue
            n += 1; pid = f"{f}:{j1+1}"
            P.append(f"PASSAGE {pid}\nBEFORE:\n{bt or '(none)'}\nAFTER:\n{at or '(removed)'}\n")
            for rid, fact, disp, probes in rows:
                hit = any(pr[2:].split("::",1)[1][:60] in (bt + at) for pr in probes if "::" in pr and pr.split("::")[0][2:] == f + ".tex")
                if hit and rid not in used:
                    used.add(rid)
                    hs = []
                    for pr in probes:
                        if not pr.startswith("N:") or "::" not in pr: continue
                        fn, tx = pr[2:].split("::", 1)
                        if home_para(fn, tx) is None or tx[:60] in at or tx[:60] in bt: continue   # not a home in this tree, or the passage itself
                        hp = home_para(fn, tx)
                        hs.append(f"  home {fn}: \"{tx}\"\n    in its paragraph: {hp[:2500] if hp else '(NOT FOUND)'}")
                    fact_b = re.sub(r"[;,]?\s*review W[12][^);]*", "", fact)
                    C.append(f"ROW {rid} (passage {pid}): fact: {fact_b}\n" + "\n".join(hs))
    open(f"{OUT}/{g}.passages.txt", "w").write("\n".join(P))
    open(f"{OUT}/{g}.context.txt", "w").write("CONTEXT: the consolidation's fact-ledger rows for these passages. Each N: probe is the exact home text, shown inside its full paragraph of the delivered note.\n\n" + "\n\n".join(C))
    print(g, "passages", n, "rows", len(C), "words", sum(len(x.split()) for x in P + C))
