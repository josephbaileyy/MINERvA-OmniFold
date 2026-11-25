# C-OLD: OLD-input outputs vs part C's committed receipts (regenA DECLARATION 085553b4). Numbers to 1e-9 relative;
# text reports compared on their numbers line by line, paths/hostnames/shas ignored.
import json, re, sys, math
F = sys.argv[1]; R = F + "/ref"; O = F + "/out"
NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")
SKIP = re.compile(r"(/pscratch|/Users|/global|/private|\.root|\.png|\.pdf|\.json|sha256|hostname|Warning|opening|commit)", re.I)
def text_nums(path, start=None):
    out = []
    for line in open(path, errors="ignore"):
        if SKIP.search(line): continue
        out += [float(x) for x in NUM.findall(line)]
    return out
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if re.search(r"(path|sha|host|time|produced|file|commit|version|argv|cmd)", k, re.I): continue
            yield from leaves(v, p + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, f"{p}[{i}]")
    elif isinstance(o, bool) or o is None or isinstance(o, str): pass
    elif isinstance(o, (int, float)): yield p, float(o)
def cmp_seq(a, b):
    if len(a) != len(b): return False, f"count {len(a)} vs {len(b)}", None
    worst = max((abs(x - y) / max(abs(y), 1e-300) if y != 0 else abs(x) for x, y in zip(a, b)), default=0.0)
    return worst <= 1e-9, f"{len(a)} numbers", worst
def cmp_json(a, b):
    la, lb = dict(leaves(json.load(open(a)))), dict(leaves(json.load(open(b))))
    keys = sorted(set(la) & set(lb)); miss = sorted(set(la) ^ set(lb))
    ok, info, worst = cmp_seq([la[k] for k in keys], [lb[k] for k in keys])
    return ok and not miss, f"{info}; key mismatch {len(miss)} {miss[:4]}", worst
res = {}
res["P1a chi2_paperonly"] = cmp_seq(text_nums(O + "/old_P1a_chi2_paperonly.log"), text_nums(R + "/chi2_paperonly.txt"))
res["P5 model_comp_report"] = cmp_seq(text_nums(O + "/old/model_comp_report.txt"), text_nums(R + "/model_comp_report.txt"))
res["P4 tension_report"] = cmp_seq(text_nums(O + "/old/tension_report.txt"), text_nums(R + "/tension_report.txt"))
res["P6 receipt_model_chi2"] = cmp_json(O + "/old/receipt_model_chi2.json", R + "/receipt_model_chi2.json")
res["P7 agreement_windows"] = cmp_json(O + "/old/RECEIPT-agreement-windows.json", R + "/RECEIPT-agreement-windows.json")
for k, (ok, info, worst) in res.items(): print(f"{k:24s} {'PASS' if ok else 'FAIL'}  {info}  max_rel={worst}")
