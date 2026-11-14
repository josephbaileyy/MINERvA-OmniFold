"""Print, side by side, the per-tune grade quantities of the G2R regrade (score_g2r_<T>.json) and COV2D's committed
grade (score_<T>.json), read field by field; no new computation beyond counting cells against their thresholds."""
import json, sys
def grade(rec):
    return rec["grade"] if "grade" in rec else rec
for T in ("G18", "AR23"):
    new = json.load(open(f"node/readout/{T}/score_g2r_{T}.json"))
    old = json.load(open(f"cov2d-committed/score_{T}.json"))
    print(f"===== {T}")
    for lab, rec in (("G2R (C_T')", new), ("COV2D committed (C_T)", old)):
        g = grade(rec)
        c, k = g["counts"], g["k_cell"]
        below = [i for i in range(len(c)) if c[i] < k[i]]
        print(f"--- {lab}: verdict {rec.get('verdict', g.get('verdict'))}; ndf {g.get('ndf')}; cells {len(c)}")
        print(f"    per-cell: counts min {min(c)} max {max(c)}; k_cell min {min(k)} max {max(k)}; cells with count < k_cell: {below}")
        print(f"    flagged_cells {g.get('flagged_cells')}; sum(cell_flag) {sum(g['cell_flag'])}")
        for cell in g.get("flagged_cells", []):
            print(f"      cell {cell}: count {c[cell]} k_cell {k[cell]} pull_mean {g['pull_mean'][cell]:.4f} pull_sd {g['pull_sd'][cell]:.4f} s_c {g['s_c'][cell]:.4f}")
        print(f"    joint: joint_count {g.get('joint_count')} of 300; k_joint {g.get('k_joint')}; joint_flag {g.get('joint_flag')}")
        print(f"    size: {json.dumps({kk: (vv if not isinstance(vv, list) else f'list({len(vv)})') for kk, vv in g.get('size', {}).items()})}")
        print(f"    chi2_mean_over_ndf {g.get('chi2_mean_over_ndf')} se {g.get('chi2_mean_over_ndf_se')}")
        print(f"    attribution {json.dumps(g.get('attribution'))}")
        print(f"    outlier_cell {json.dumps(g.get('outlier_cell'))}")
        print(f"    weakened_pass {g.get('weakened_pass')} share {g.get('weakened_share')}")
        print(f"    controls_failed {rec.get('controls_failed', g.get('controls_failed'))}; stop {rec.get('stop')}")
    ro = new.get("readouts", {})
    print(f"--- G2R descriptive readouts: keys {sorted(ro)}")
    lm = ro.get("leave_out_mec", {})
    print(f"    leave_out_mec: flagged_under_minus {lm.get('flagged_under_minus')}; changes_no_verdict {lm.get('changes_no_verdict')}; reading {lm.get('reading')!r}")
    print(f"    tune_eps {json.dumps(new.get('tune_eps'))}")
    oro = old.get("readouts", {})
    print(f"--- COV2D committed readouts keys {sorted(oro)}")
