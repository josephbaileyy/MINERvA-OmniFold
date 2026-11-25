# (file, old, new, label) mutants of the plot_2d_cross_section fix
M = [
 ("2d-unfolding/plot_2d_cross_section.py", 'label = f"{edge_label(lo)} < p_T < {edge_label(hi)}"', 'label = f"{lo:.2f} < p_T < {hi:.2f}"', "M1 pT label back to .2f"),
 ("2d-unfolding/plot_2d_cross_section.py", 'label = f"{lo:.1f} < p_|| < {hi:.1f}"', 'label = f"{edge_label(lo)} < p_|| < {edge_label(hi)}"', "M2 pz label via edge_label"),
 ("2d-unfolding/plot_2d_cross_section.py", 'pt_edges, pz_edges = (list(e) for e in th2d_edges(h2d))', 'pt_edges, pz_edges = list(PT_EDGES), list(PZ_EDGES)', "M3 projections on module edges"),
 ("2d-unfolding/plot_2d_cross_section.py", 'return project_xsec_1d(h2d, "pt", pt_edges, pz_edges), project_xsec_1d(h2d, "pz", pt_edges, pz_edges)', 'return project_xsec_1d(h2d, "pz", pt_edges, pz_edges), project_xsec_1d(h2d, "pt", pt_edges, pz_edges)', "M4 projections swapped"),
 ("2d-unfolding/plot_2d_cross_section.py", '    return pz_edges, pt_edges, eff_arr', '    return np.asarray(PZ_EDGES), np.asarray(PT_EDGES), eff_arr', "M5 efficiency mesh on module edges"),
 ("2d-unfolding/plot_2d_cross_section.py", 'im = ax.pcolormesh(pz_edges, pt_edges, eff_arr,', 'im = ax.pcolormesh(PZ_EDGES, PT_EDGES, eff_arr,', "M6 main draws the map on module edges"),
 ("2d-unfolding/plot_2d_cross_section.py", '            eff_arr[ix - 1, iy - 1] = h_eff.GetBinContent(ix, iy)', '            eff_arr[ix - 1, iy - 1] = h_eff.GetBinContent(iy, ix) if ix <= 0 else h_eff.GetBinContent(ix, iy) * 1.0000001', "M7 efficiency values perturbed"),
 ("2d-unfolding/uq/reported_cells.py", '    for nd in range(2, 10):', '    for nd in range(1, 10):', "M8 edge_label min decimals 1"),
 ("2d-unfolding/uq/reported_cells.py", '        if abs(round(x, nd) - x) <= 1e-9:', '        if abs(round(x, nd) - x) <= 1e-2:', "M9 edge_label tolerance loose"),
 ("2d-unfolding/plot_2d_cross_section.py", '    hXSecTruth_pt, hXSecTruth_pz = truth_projections(hXSecTruth2D)', '    from unfold_2d_omnifold_unbinned import project_xsec_1d\n    hXSecTruth_pt, hXSecTruth_pz = (project_xsec_1d(hXSecTruth2D, a, PT_EDGES, PZ_EDGES) for a in ("pt", "pz"))', "M10 main bypasses truth_projections"),
]
M += [
 ("2d-unfolding/plot_2d_cross_section.py", '    for h in h2ds:\n        require_pt_on_x(h)\n    pt, pz = th2d_edges(h2ds[0])', '    return\n    pt, pz = th2d_edges(h2ds[0])', "M11 require_one_grid disabled"),
 ("2d-unfolding/plot_2d_cross_section.py", '    if (h.GetNbinsX(), h.GetNbinsY()) != (N_PT, N_PZ):\n        raise ValueError', '    if False:\n        raise ValueError', "M12 orientation guard disabled"),
 ("2d-unfolding/plot_2d_paper_comparison.py", '    require_one_grid([hXSec2D, hTruth2D, hEff2D])\n', '', "M13 paper_comparison drops the grid check"),
 ("2d-unfolding/plot_2d_cross_section.py", 'pt_edges, pz_edges = (list(e) for e in th2d_edges(h2d))', 'pt_edges, pz_edges = list(th2d_edges(h2d)[0]), list(PZ_EDGES)', "M14 projections hardcode PZ_EDGES"),
 ("2d-unfolding/plot_2d_cross_section.py", '    return pz_edges, pt_edges, eff_arr', '    return np.asarray(PZ_EDGES), pt_edges, eff_arr', "M15 efficiency mesh hardcodes PZ_EDGES"),
 ("2d-unfolding/plot_2d_cross_section.py", '        dpt = hTruth2D.GetXaxis().GetBinWidth(ix)', '        dpt = PT_EDGES[ix] - PT_EDGES[ix - 1]', "M16 truth xsec uses module pT widths"),
 ("2d-unfolding/plot_2d_cross_section.py", '    hXSecTruth_pt, hXSecTruth_pz = truth_projections(hXSecTruth2D)', '    hXSecTruth_pt, hXSecTruth_pz = truth_projections(hXSec2D)', "M17 main projects the data, not the truth"),
 ("2d-unfolding/plot_2d_cross_section.py", 'f, args.infile, args.mcfile, args.flux_hist, pt_edges=th2d_edges(hTruth2D)[0])', 'f, args.infile, args.mcfile, args.flux_hist)', "M18 main skips the flux edge check"),
 ("2d-unfolding/plot_2d_cross_section.py", '    require_flux_on(h_flux, pt_edges, f"{mc_path}:{flux_hist}")\n', '', "M19 fallback flux unchecked"),
 ("2d-unfolding/plot_2d_cross_section.py", '        require_flux_on(h_embedded, pt_edges, "embedded hFlux_pt")\n', '', "M20 embedded flux unchecked"),
 ("2d-unfolding/plot_2d_paper_comparison.py", 'f, args.infile, args.mcfile, args.flux_hist, pt_edges=th2d_edges(hTruth2D)[0])', 'f, args.infile, args.mcfile, args.flux_hist)', "M21 paper_comparison skips the flux edge check"),
 ("2d-unfolding/plot_2d_cross_section.py", '    require_pt_on_x(h2d)\n    slices = []', '    slices = []', "M22 th2_to_slices unguarded"),
 ("2d-unfolding/plot_2d_cross_section.py", '    for h, want in ((h_pt, pt), (h_pz, pz)):', '    for h, want in ((h_pt, pt),):', "M23 hXSec_pz edges unchecked"),
 ("2d-unfolding/plot_2d_cross_section.py", '    require_one_grid([hXSec2D, hTruth2D, hEff2D], hXSec_pt, hXSec_pz)', '    require_one_grid([hXSec2D, hEff2D], hXSec_pt, hXSec_pz)', "M24 truth not in the grid check"),
]
M += [("2d-unfolding/plot_2d_paper_comparison.py", '    require_one_grid([hXSec2D, hTruth2D, hEff2D])\n', '    require_one_grid([hXSec2D, hEff2D])\n', "M25 paper_comparison: truth not in the grid check")]
