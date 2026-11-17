"""Print the D2 mu_max record per truth, as recorded, beside geant_full.json's (D2's) values; no reading added.
    python3 d2_report.py <mumax.json> <geant_full.json>"""
import json, sys
r, g = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))["matrices"]
print(f"verdict {r.get('verdict')} stop {r.get('stop')}")
for k, v in g.items():
    print(f"D2 (S1 at the data) {k}: mu_max {v['mu_max']!r}, 1/(1-mu) {v['chi2_ratio_bound']!r}, max eigenmode share "
          f"{v['max_eigenmode_share']!r}, smallest-4 {v['smallest4_eigenmode_shares']}, direction {v['mu_max_direction_cells']}")
for t, d in r["truths"].items():
    print(f"[{t}] products {d.get('products_sha256')} match {d.get('products_match')} made_from {d.get('made_from_match')}; "
          f"removal dev {d.get('removal_control_on_G', {}).get('max_abs_dev')!r} (limit {d.get('removal_control_on_G', {}).get('limit')!r}); "
          f"G top3 abs eigenvalues {d.get('G_eigenvalues_top3_abs')}")
    for m in ("primary C_T (all)", "secondary C_T^- (all, leave-out-MEC)"):
        v = d.get(m)
        if v:
            print(f"[{t}] {m}: mu_max {v['mu_max']!r}, top3 {v['mu_top3']}, 1/(1-mu) {v['chi2_ratio_bound']!r}, "
                  f"G off-diagonal |.| share {v['G_offdiagonal_abs_share']!r}")
            print(f"[{t}] {m}: direction {v['mu_max_direction_cells']}; max eigenmode share {v['max_eigenmode_share']!r}; "
                  f"smallest-4 eigenmode shares {v['smallest4_eigenmode_shares']}")
