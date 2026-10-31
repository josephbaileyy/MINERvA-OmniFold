import json, sys, re
from pathlib import Path
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "nd-unfolding"))
import fd_cpl_addition as A
for k in A.READOUTS:
    r = json.loads((WT / A.COMMITTED[k][0]).read_text())
    nums = [(p, v) for p, v in A.numeric_leaves(r) if not A.skipped(p, ("/argv", "/code_sha256", "/code", "/versions"))]
    strs = [(p, v) for p, v in A.string_leaves(r) if not p.startswith("/labels") and not A.skipped(p, ("/argv", "/code_sha256", "/code", "/versions"))]
    tiny = [(p, v) for p, v in nums if isinstance(v, float) and v != 0 and abs(v) < 1e-13]
    worst = [(p, v) for p, v in nums if re.search(r"worst|asym|diff|resid|max_abs|repro", p, re.I)]
    runlike = [(p, v) for p, v in nums if re.search(r"time|wall|elapsed|second|_s$|pid|date", p, re.I)]
    nested = [p for p, _ in A.structure(r) if re.search(r"/(code_sha256|argv|versions|code)$", p) and p.count("/") > 1]
    print(f"== {k}: {len(nums)} numeric leaves, {len(strs)} non-label string leaves, {len(tiny)} nonzero |x|<1e-13")
    for p, v in tiny[:6]: print("   tiny", p, v)
    for p, v in worst[:8]: print("   diag", p, v)
    for p, v in runlike[:5]: print("   runlike", p, v)
    if nested: print("   nested excluded-name keys NOT excluded:", nested[:5])
    # sample non-label strings
    import collections
    print("   string samples:", [p for p, _ in strs[:6]])
