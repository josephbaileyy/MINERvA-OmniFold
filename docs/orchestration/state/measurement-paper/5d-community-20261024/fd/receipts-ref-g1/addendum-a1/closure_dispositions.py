"""Closure-grep dispositions for REF-G1 at the A1 revision: python3 g1_dispositions.py REPO GREP.txt OUT.tsv

Each hit is attributed to its enclosing def (nearest preceding `def` at lower indentation); the disposition comes from
the (file, function) tables below; anything else is "not reached", which closure_trace.py then checks at run time."""
import re
import sys
from pathlib import Path

repo, grep, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
G, R = "nd-unfolding/ref_g1/ref_g1.py", "nd-unfolding/ref_g1/ref_g1_read.py"
STAGED = "staged: an O_NOATIME copy, digest taken in the same pass (A1 section 2.2)"
TABLE = {
    # REF-G1's own read discipline
    (G, "noatime_flag"): "the O_NOATIME flag itself; refuses where absent (A1 section 2.2)",
    (G, "open_noatime"): "O_NOATIME open; EPERM raised, never retried plain",
    (G, "copy_noatime"): "the O_NOATIME source read and the copy's write ('xb'); the copy re-hashed (allowed root)",
    (G, "tfile_guard"): "the TFile guard: any mode outside the allowed roots refused",
    (G, "guarded"): "the TFile guard handing an admitted open (under the allowed roots) to ROOT",
    (G, "read_guards"): "docstring, no read",
    (G, "_audit"): "the audit hook on Python opens",
    (G, "staged"): "docstring, no read",
    # units
    (G, "__init__"): "repo: IBU-1's config (Lib)",
    (G, "load_ratio"): "the ratio's staged copy (D6, fixed)",
    (G, "universes"): "repo: the committed preconditions listing",
    (G, "bank_cv"): "the bank cv.npz's staged copy (D1, fixed)",
    (G, "universe"): "the weight files' and flux-universe file's staged copies (D2, D7, fixed)",
    (G, "run_unit"): "run output: the unit's own done-marker and product (own products read in place)",
    (G, "main"): "repo: config.json",
    (G, "run_units"): "repo: the listing and IBU-1's contract; of_inputs_5d and bkg_dump as staged copies (D5, fixed)",
    (G, "unit_reads"): "enumeration only (Path.exists via weight_keys: a stat, no read)",
    # reader
    (R, "load"): "the run's own products in place, and staged copies (D_N, the gibu1 product)",
    (R, "e_cells"): "an (e) product's staged copy (D8, fixed)",
    (R, "reading_r2"): "the run's own closure product in place; the (e) closure's staged copy (D8, fixed)",
    (R, "g_ibu1"): "staged copies of D_N.npz and the gibu1 product, each pinned (D8, fixed)",
    (R, "g_cells"): "s1_assembly.npz's staged copy (D8, fixed)",
    (R, "g_pair"): "repo: the listing; (e) digests from the staged copies (D8, fixed)",
    (R, "read"): "the bars file (beside the readout, an allowed root) and repo digests",
    (R, "bars"): "write of bars.json",
    (R, "main"): "repo: config.json",
    (R, "command"): "the flux constraint's staged copy (D3, fixed)",
    (R, "digest"): "the run's own products in place; (e) digests from the staged copies (D8, fixed)",
    (R, "e_sha"): "staged digest",
    (R, "every_k"): "the run's own central product in place",
    (R, "g_cv"): "the run's own products in place",
    (R, "ibu_cells"): "the run's own products in place",
    # shared modules, reached only with copies or repository files
    ("nd-unfolding/ibu1/ibu1.py", "sha256"): "plain read, reached only on staged copies, repository files and REF-G1's own outputs (the guard refuses it elsewhere)",
    ("nd-unfolding/ibu1/ibu1.py", "load_inputs"): "bkg_dump's staged copy (D5, fixed)",
    ("nd-unfolding/ibu1/ibu1.py", "write"): "write of a unit's product",
    ("nd-unfolding/s5c_unfold.py", "load_inputs"): "of_inputs_5d's staged copy (D5, fixed)",
    ("nd-unfolding/s5p_universe.py", "weights"): "a universe's staged weight copies (D2, fixed)",
    ("nd-unfolding/flux_universe.py", "read_flux_universe_table"): "the flux-universe file's staged copy, under the TFile guard (D7, fixed)",
    ("nd-unfolding/s1_assemble.py", "sha256"): "plain read via require_sha, reached only on the constraint's staged copy and repo files",
    ("nd-unfolding/s1_assemble.py", "flux_weights"): "the flux constraint's staged copy (D3, fixed)",
    ("nd-unfolding/s1_assemble.py", "check_meta"): "an (e) product's staged copy (D8, fixed)",
    ("nd-unfolding/s1_assemble.py", "fine_map"): "repo: the H2 definition",
}
rows = []
for line in open(grep):
    f, ln, text = line.split(":", 2)
    src = (repo / f).read_text().split("\n")
    ind = len(src[int(ln) - 1]) - len(src[int(ln) - 1].lstrip())
    fn = "<module>"
    for i in range(int(ln) - 1, -1, -1):
        m = re.match(r"(\s*)def (\w+)", src[i])
        if m and len(m.group(1)) < max(ind, 1) or (m and i == int(ln) - 1):
            fn = m.group(2)
            break
    d = TABLE.get((f, fn), f"not reached from REF-G1's run path under A1 (in {fn}) -> no change")
    rows.append("\t".join((f, ln, fn, text.strip()[:110].replace("\t", " "), d)))
open(out, "w").write("file\tline\tfunction\tcode\tdisposition\n" + "\n".join(rows) + "\n")
print(len(rows), "rows;", sum("not reached" in r for r in rows), "not reached")
