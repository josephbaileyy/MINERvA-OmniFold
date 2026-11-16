"""Print cr's readings beside step C-R's, as recorded (no reading added): per quadrant, the 2D primary (S, sigma
[sigma_2D], d, d_pct, outcome, rho_star, z_rho0, bound_any_rho, bound_rho0) and its printed-only variant without
C_PL5D (outcome, rho_star, z_rho0), and the 3D descriptive outcome. With --max-diff, also the per-field maximum
relative difference between two readouts over every numeric field (for a control that STOPs on floats only).
    python3 cr_report.py <step C-R overlap_refined.json> <new overlap_refined.json> [--max-diff]"""
import json, sys
a, b = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
F2 = ("S", "sigma", "d", "d_pct", "outcome", "rho_star", "z_rho0", "bound_any_rho", "bound_rho0")
FV = ("outcome", "rho_star", "z_rho0")
for q in a["quadrants"]:
    A, B = a["quadrants"][q], b["quadrants"][q]
    for f in F2:
        print(f"{q} 2D {f}: step C-R {A['2D'][f]!r} | new {B['2D'][f]!r}")
    for f in FV:
        print(f"{q} 2D without C_PL5D {f}: step C-R {A['2D']['printed_only_without_C_PL5D'][f]!r} | new {B['2D']['printed_only_without_C_PL5D'][f]!r}")
    print(f"{q} 3D outcome: step C-R {A['3D']['outcome']!r} | new {B['3D']['outcome']!r}")
if "--max-diff" in sys.argv:
    worst = {}
    def walk(x, y, p):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in set(x) & set(y): walk(x[k], y[k], f"{p}/{k}")
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            for i, (u, v) in enumerate(zip(x, y)): walk(u, v, f"{p}[{i}]")
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool) and x != y:
            r = abs(x - y) / max(abs(x), abs(y))
            worst[p] = r
        elif x != y and not isinstance(x, (dict, list)):
            worst[p] = f"non-numeric: {x!r} vs {y!r}"
    walk(a["quadrants"], b["quadrants"], "quadrants")
    for k in ("total_2d", "total_3d", "diagnostic_cv_over_Q_x_max_rel"):
        walk(a.get(k), b.get(k), k)
    for p, r in sorted(worst.items(), key=lambda kv: (isinstance(kv[1], str), kv[1] if not isinstance(kv[1], str) else 0), reverse=True):
        print("MAXDIFF", p, r)
    print("MAXDIFF fields differing:", len(worst))
