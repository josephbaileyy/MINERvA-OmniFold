#!/usr/bin/env python3
"""Run every probe of ledger.md, then the token audit, against the printed (comment-stripped,
whitespace-collapsed) LaTeX source of the worktree.

usage: check_ledger.py <worktree> [ledger.md] [--self-test]
  N:<file>::text   must occur in docs/analysis-note/<file> (a note file, after the rewrite)
  R:<file>::text   must occur in docs/analysis-note/<file> (a records file)
  P::text          must occur in docs/analysis-note/paper_body.tex
  X:<file>::text   must NOT occur in docs/analysis-note/<file>
Every row needs at least one N:/R:/P: probe. SCOPED/NEW/REMOVED rows also need an X: or N: probe as listed.
Token audit: every number, \\ref, \\cite, \\label, \\texttt{} and value macro whose count fell between the base
(origin/main) and the worktree must appear in the ledger's "Token audit" table with that count.
--self-test plants a false N: probe, a false X: probe and an unlisted token loss, and requires all three to fail.
Exit 1 on any failure."""
import re, subprocess, sys
from collections import Counter
from pathlib import Path

FILES = ["sec_5d.tex", "app_statmethods_nd.tex", "app_negweight.tex"]


def printed(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)


def tokens(src):
    t = printed(src)
    c = Counter()
    for m in re.finditer(r"(?<![A-Za-z\\])-?\d+(?:[.,]\d+)*(?:e-?\d+)?", t):
        c["num:" + m.group(0).replace(",", "")] += 1
    for m in re.finditer(r"\\(ref|eqref|cite|label)\{([^}]*)\}", t):
        c[m.group(1) + ":" + m.group(2)] += 1
    for m in re.finditer(r"\\texttt\{([^}]*)\}", t):
        c["tt:" + m.group(1)] += 1
    for m in re.finditer(r"\\([A-Za-z]+)", t):
        if re.match(r"(nw|fps|sproj|sagg|smed|seed|floor|pinned|cvMove|zproj|latBins|jt)", m.group(1)):
            c["macro:" + m.group(1)] += 1
    return c


def run(wt, ledger_text, base_override=None):
    D = Path(wt) / "docs/analysis-note"
    cache = {}

    def text(key):
        if key not in cache:
            cache[key] = printed((D / key).read_text())
        return cache[key]

    rows = probes = fails = 0
    in_audit = False
    audit = {}
    for line in ledger_text.splitlines():
        if line.startswith("## Token audit"):
            in_audit = True
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("| file ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if in_audit:
            if len(cells) == 4:
                audit[(cells[0], cells[1].strip("`"))] = int(cells[2])
            continue
        if len(cells) != 6:
            print(f"MALFORMED row: {line[:80]}"); fails += 1; continue
        rid, fact, before, disp, after, probe = cells
        rows += 1
        kinds = set()
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            if p.startswith("see "):
                kinds.add("ref"); continue
            m = re.match(r"(P|[NRX]:[\w.]+)::(.*)$", p)
            if not m:
                print(f"{rid}: MALFORMED probe {p!r}"); fails += 1; continue
            where, lit = m.group(1), re.sub(r"\s+", " ", m.group(2))
            key = "paper_body.tex" if where == "P" else where[2:]
            kind = where[0]
            kinds.add(kind)
            probes += 1
            present = lit in text(key)
            if kind == "X" and present:
                print(f"{rid}: STILL PRINTS in {key}: {lit!r}"); fails += 1
            elif kind != "X" and not present:
                print(f"{rid}: NOT FOUND in {key}: {lit!r}"); fails += 1
        if not kinds & {"N", "R", "P", "ref"}:
            print(f"{rid}: row without a positive probe"); fails += 1
        if (disp.startswith("REMOVED") or disp.startswith("SCOPED")) and not kinds & {"X", "N", "ref"}:
            print(f"{rid}: {disp.split()[0]} row without an X: or N: probe"); fails += 1
    # token audit
    tok_fails = 0
    for f in FILES:
        base = base_override.get(f) if base_override else None
        if base is None:
            base = subprocess.run(["git", "-C", wt, "show", f"origin/main:docs/analysis-note/{f}"],
                                  capture_output=True, text=True, check=True).stdout
        b, n = tokens(base), tokens((D / f).read_text())
        for k in b:
            lost = b[k] - n.get(k, 0)
            if lost > 0 and audit.get((f, k)) != lost:
                print(f"TOKEN LOST and not accounted: {f} {k} x{lost} (ledger lists {audit.get((f, k))})")
                tok_fails += 1
        for (af, ak), cnt in audit.items():
            if af == f and b.get(ak, 0) - n.get(ak, 0) != cnt:
                print(f"TOKEN AUDIT ROW STALE: {af} {ak} listed x{cnt}, measured x{b.get(ak, 0) - n.get(ak, 0)}")
                tok_fails += 1
    print(f"ledger rows {rows}, probes {probes}, failures {fails}; token audit failures {tok_fails}")
    return fails + tok_fails


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    wt = args[0]
    ledger = Path(args[1] if len(args) > 1 else Path(__file__).with_name("ledger.md"))
    lt = ledger.read_text()
    if "--self-test" in sys.argv:
        planted_n = lt.replace("| S1 | prior reweighting vs response mismatch |",
                               "| S1 | prior reweighting vs response mismatch |", 1)
        planted_n = planted_n.replace("`N:sec_5d.tex::a response mismatch instead changes how a given truth is reconstructed`",
                                      "`N:sec_5d.tex::a response mismatch never changes how a given truth is reconstructed`", 1)
        planted_x = lt.replace("`X:sec_5d.tex::These outcomes stand.`", "`X:sec_5d.tex::D1 and W1 improve slowly.`", 1)
        base = subprocess.run(["git", "-C", wt, "show", "origin/main:docs/analysis-note/sec_5d.tex"],
                              capture_output=True, text=True, check=True).stdout
        planted_tok = {"sec_5d.tex": base + "\n\\SI{987.654}{\\percent}\n"}
        r = [run(wt, planted_n) > 0, run(wt, planted_x) > 0, run(wt, lt, planted_tok) > 0]
        ok = all(r)
        print(f"SELF-TEST :: {'PASS' if ok else 'FAIL'} (false N: probe fails={r[0]}, false X: probe fails={r[1]}, "
              f"unlisted token loss fails={r[2]})")
        sys.exit(0 if ok else 1)
    sys.exit(1 if run(wt, lt) else 0)


if __name__ == "__main__":
    main()
