#!/usr/bin/env python3
"""V_F (C_e^infl) readings, Phases 1 and 2: FD-VF-ADDITION-DECLARATION.md section 5.

Imports docs/analysis-note/make_values_fived16.py and make_values_landed.py unchanged and, in this process only (no
file under docs/analysis-note/ is written), computes:
- OLD: make_values_fived16.all_values() and make_values_landed.build(load()), as the note builds them;
- V_F: the same with READOUTS / NOPL_READOUTS pointing at Phase 1's V_F readouts and data product (fd/with-vf/) and
  Phase 2's V_F copies (fd/with-vf/p2/), each pinned below, and ARMS' four matrix names replaced by their V_F names.

Two literal names in make_values_fived16.py are not ARMS entries, so the V_F run supplies them in its loaded data (the
note's repins, listed in the follow-ups):
- "C_total_plus_C_resp" (:678, :689), the arm without C_PL5D: the data product's field takes the V_F
  C_total + C_resp + DeltaC_e sigma, and cresp's C_total_resp row, which :678 checks it against, takes the same values
  (that row's V_F form; its C_e form is the OLD value, both given in section 4);
- the block label it parses (:700-702) is C_PL5D's, unchanged by V_F: taken from the pinned with-cpl product.

Writes vf_readings.json (every key, OLD and V_F, with print sites) and vf_readings.md: decision-rule outcome changes
first, then every moved \\fvval key, the printed-xk check, the S1/C_resp rows both ways, and the follow-ups.
Run: python3 -B vf_readings.py --out-dir <dir>"""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           cwd=Path(__file__).resolve().parent, check=True).stdout.strip())
sys.path.insert(0, str(ROOT / "docs/analysis-note"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_values_fived16 as MV  # noqa: E402  (imported unchanged)
import make_values_landed as ML  # noqa: E402  (imported unchanged)
import phase1_readings as P1  # noqa: E402

FD = MV.FD
W = f"{FD}/fd/with-vf"
P2 = f"{W}/p2"
VF_WITH = {
    "f0": (f"{W}/readout/vf-f0/fd_f0_readout.json", "7d7429d4"),
    "f0b": (f"{W}/readout/vf-with-S/fd_f0b_readout.json", "432243e1"),
    "f1": (f"{W}/readout/vf-with-S/fd_f1_readout.json", "bd36a2aa"),
    "g0": (f"{W}/readout/vf-with-S/fd_g_readout.json", "c9fe9d51"),
    "g": (f"{W}/readout/vf-with-E/fd_g_readout.json", "7034a08e"),
    "diag": (f"{W}/readout/vf-with-E/fd_g_diag_readout.json", "440fc379"),
    "fup": (f"{W}/readout/vf-with-E/fd_g_followup_readout.json", "030b1566"),
    "sens2": (f"{W}/readout/vf-with-E/fd_g_sens2_readout.json", "7a618892"),
    "fboot": (f"{W}/readout/vf-with-E/fd_flux_boot_readout.json", "9387e495"),
    "dp": (f"{W}/data-product/fd_data_product_vf.json", "1a37b082"),
    # Phase 2's V_F copies (fd_vf_p2.py p2; each passed control P, A4)
    "gdefs": (f"{P2}/gdefs.vf.json", "6c202b08b5d9ed0b"),
    "gch": (f"{P2}/gch.vf.json", "52ef42e9500ce62f"),
    "gnat": (f"{P2}/gnat.vf.json", "3607e78c22ba00bf"),
    "gover": (f"{P2}/gover.vf.json", "879d3dca63db4c2e"),
    "cr": (f"{P2}/cr.vf.json", "f58bc91280436c83"),
    "e2": (f"{P2}/e2.vf.json", "7db5bd32180ce66b"),
    "e2sens": (f"{P2}/e2sens.vf.txt", "e31bb03a5f3e0a0a"),
    "eav": (f"{P2}/eav.vf.json", "516b625d5d65fe8c"),
    "xk": (f"{P2}/xk.vf.json", "045eb904bbe25a8b"),
    "prr": (f"{P2}/prr.vf.json", "118741191224815a"),
    "rsn": (f"{P2}/rsn.vf.json", "8e5addb8ec0a7649"),
    "rsnregrade": (f"{P2}/rsnregrade.vf.json", "10dcdd729d2d86fe"),
}
VF_NOPL = dict(VF_WITH, **{
    "f0b": (f"{W}/readout/vf-nopl-S/fd_f0b_readout.json", "7ed24825"),
    "f1": (f"{W}/readout/vf-nopl-S/fd_f1_readout.json", "e473f642"),
    "g0": (f"{W}/readout/vf-nopl-S/fd_g_readout.json", "a0d000d0"),
    "g": (f"{W}/readout/vf-nopl-E/fd_g_readout.json", "eefe1c6d"),
    "diag": (f"{W}/readout/vf-nopl-E/fd_g_diag_readout.json", "a41e8091"),
    "fup": (f"{W}/readout/vf-nopl-E/fd_g_followup_readout.json", "80081f03"),
    "sens2": (f"{W}/readout/vf-nopl-E/fd_g_sens2_readout.json", "5cac1831"),
    "fboot": (f"{W}/readout/vf-nopl-E/fd_flux_boot_readout.json", "3d4af100"),
})
VF_VR = (f"{P2}/vatlas.vf.json", "380682e69408b51b")
XK_OLD_REPLAY = (f"{FD}/fd/receipts-vf/p2/xk-old-replay-k.json", "845ce53770c83cf3")
VF_ARMS = {"with": {"dp": "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e", "rep": "C_total + C_resp + C_PL5D + DeltaC_e",
                    "x": "C_resp + C_PL5D + DeltaC_e", "f1sig": "relative_sigma_plus_C_resp + C_PL5D + DeltaC_e"},
           "without": {"dp": "C_total_plus_C_resp_plus_DeltaC_e", "rep": "C_total + C_resp + DeltaC_e",
                       "x": "C_resp + DeltaC_e", "f1sig": "relative_sigma_plus_C_resp + DeltaC_e"}}
VF_BLOCK_NAMES = ("C_resp + C_PL5D + DeltaC_e", "C_resp + DeltaC_e")
SHIMS = ["BLOCK[<V_F block name>] := a PLACEHOLDER label, so a diagnostic whose dominant component is the V_F block "
         "prints; the label itself is note wording (JE/Joseph)",
         "dp.relative_sigma.C_total_plus_C_resp := the V_F C_total + C_resp + DeltaC_e sigma (make_values_fived16 "
         ":678, :689); cresp.relative_sigma.C_total_resp := the same values (that row's V_F form)",
         "without-C_PL5D arm: dp.correlation := the correlation of C_total + C_resp + DeltaC_e (M_ij/sqrt(M_ii M_jj) "
         "from the V_F product's own matrix), correlation_of := its name, as the OLD nopl product carries for its arm",
         "dp.labels.block := C_PL5D's label from the pinned with-cpl product (:700-702 parse it; V_F's own is kept as "
         "block_DeltaC_e)"]


def recording_module(path: Path, name: str):
    """The module at path with every assert statement recording (line, message) when false instead of raising: an
    in-process AST rewrite, no file changed. Used for the V_F run only, so that every guard on a printed figure that
    moves under V_F is listed (each a note-side follow-up); the OLD run uses the unchanged module."""
    import ast
    import types
    src = path.read_text()
    tree = ast.parse(src, str(path))

    class T(ast.NodeTransformer):
        def visit_Assert(self, node):
            call = ast.Call(func=ast.Name("_vf_assert", ast.Load()),
                            args=[ast.Constant(node.lineno), ast.Lambda(ast.arguments([], [], None, [], [], None, []),
                                                                         node.test),
                                  ast.Lambda(ast.arguments([], [], None, [], [], None, []),
                                             node.msg if node.msg else ast.Constant(None))], keywords=[])
            return ast.copy_location(ast.Expr(call), node)
    tree = ast.fix_missing_locations(T().visit(tree))
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    fails = []

    def _vf_assert(line, test, msg):
        try:
            ok = test()
        except Exception as e:      # a test that cannot even be evaluated is a failure, recorded
            fails.append((line, f"test raised {type(e).__name__}: {e}"))
            return
        if not ok:
            try:
                m = msg()
            except Exception as e:
                m = f"(message raised {type(e).__name__})"
            fails.append((line, m))
    mod._vf_assert = _vf_assert
    exec(compile(tree, str(path), "exec"), mod.__dict__)
    return mod, fails


def shim(d, arm="with"):
    if arm == "without":     # the without-C_PL5D arm reads the correlation of its own matrix (the OLD nopl product's role)
        M = d["dp"]["matrices"][VF_ARMS["without"]["dp"]]
        n = len(M)
        d["dp"]["correlation"] = [[M[i][k] / (M[i][i] * M[k][k]) ** 0.5 for k in range(n)] for i in range(n)]
        d["dp"]["correlation_of"] = VF_ARMS["without"]["dp"]
    rs = d["dp"]["relative_sigma"]
    assert "C_total_plus_C_resp" not in rs
    rs["C_total_plus_C_resp"] = list(rs[VF_ARMS["without"]["dp"]])
    crt = d["cresp"]["relative_sigma"]["C_total_resp"]
    v = rs["C_total_plus_C_resp"]
    d["cresp"]["relative_sigma"]["C_total_resp"] = dict(zip(MV.CELLS, v)) if isinstance(crt, dict) else list(v)
    old_dp = MV.load({"dp": MV.READOUTS["dp"]})["dp"]
    d["dp"]["labels"]["block_DeltaC_e"] = d["dp"]["labels"]["block"]
    d["dp"]["labels"]["block"] = old_dp["labels"]["block"]


def run_vf():
    """The V_F values from the recording copy of make_values_fived16 (its asserts recorded, not raised), and the
    guards that failed."""
    MX, fails = recording_module(ROOT / "docs/analysis-note/make_values_fived16.py", "make_values_fived16_vf")
    # the V_F block names as a diagnostic's dominant component: PLACEHOLDER labels (the printed label is note wording)
    MX.BLOCK.update({k: f"[PLACEHOLDER label for {k}]" for k in VF_BLOCK_NAMES})
    rw, rn = dict(MX.READOUTS, **VF_WITH), dict(MX.NOPL_READOUTS, **VF_NOPL)
    d, dn = MX.load(rw), MX.load(rn)
    shim(d, "with")
    shim(dn, "without")
    MX.ARMS, MX.READOUTS, MX.NOPL_READOUTS = VF_ARMS, rw, rn
    return MX.all_values(d, dn), fails


def run_old_with_mac_xk():
    """The printed-xk check (A4): the OLD values with xk's committed k.json replaced by this Mac's OLD replay."""
    d, dn = MV.load(), MV.load(MV.NOPL_READOUTS)
    mac = MV.load({"xk": XK_OLD_REPLAY})["xk"]
    d["xk"], dn["xk"] = mac, copy.deepcopy(mac)
    return MV.all_values(d, dn)


def landed(vf: bool):
    R = ML.load()
    if vf:
        R["vr"] = MV.load({"vr": VF_VR})["vr"]
    return ML.build(R)


def print_sites():
    sites = {}
    for tex in sorted((ROOT / "docs/analysis-note").glob("*.tex")):
        for i, line in enumerate(tex.read_text(errors="replace").splitlines(), 1):
            for k in re.findall(r"\\fvval\{([^}]+)\}", line):
                sites.setdefault(k, []).append(f"{tex.name}:{i}")
    return sites


def j(rel_pin):
    return MV.load({"x": rel_pin})["x"]


def decision_rules():
    """Every decision-rule outcome, OLD -> V_F (declaration section 5 item 1)."""
    out = {}
    d1 = P1.load()
    rows, counts, stops = P1.decision_rules(d1)
    out["F0/F0b/F1 listings"] = {"changes": rows, "trigger_counts": counts, "stops": stops}
    po, pv = j(MV.READOUTS["prr"]), j(VF_WITH["prr"])
    up = [k for s in ("table", "ibu") for k in po[s] if pv[s][k]["grade"]["flagged"] and not po[s][k]["grade"]["flagged"]]
    cleared = sum(1 for s in ("table", "ibu") for k in po[s]
                  if po[s][k]["grade"]["flagged"] and not pv[s][k]["grade"]["flagged"])
    b0 = {k.split("/")[1]: (po["table"][k]["grade"]["flagged"], pv["table"][k]["grade"]["flagged"])
          for k in po["table"] if k.startswith("B0/") and k.endswith(f"/s{MV.PRR_TRUTHS and ''}") or False}
    pr3 = {lv: {"old": po["readings"]["PR-3"][lv], "vf": pv["readings"]["PR-3"][lv]} for lv in po["readings"]["PR-3"]
           if lv != "IBU_K5" or True}
    out["PRR"] = {"flags_set_under_vf": up, "flags_cleared": cleared, "PR-3": pr3,
                  "PR-1_equal": po["readings"]["PR-1"] == pv["readings"]["PR-1"],
                  "labels_equal": po["readings"]["labels"] == pv["readings"]["labels"]}
    ro, rv = j(MV.READOUTS["rsnregrade"]), j(VF_WITH["rsnregrade"])
    out["RSN regrade"] = {a: {"listed": (ro["arms"][a]["listed"], rv["arms"][a]["listed"]),
                              "by_group": (ro["arms"][a]["by_group"], rv["arms"][a]["by_group"])} for a in ro["arms"]}
    so, sv = j(MV.READOUTS["rsn"]), j(VF_WITH["rsn"])
    out["RSN conclusions"] = {k: (so["conclusions"][k], sv["conclusions"][k]) for k in so["conclusions"]}
    out["RSN arm verdicts"] = {a: (so["arms"][a].get("verdict"), sv["arms"][a].get("verdict")) for a in so["arms"]}
    vo, vv = ML.load()["vr"], j(VF_VR)
    out["V-ATLAS"] = {"valid": (vo["readings"]["V-ATLAS"]["valid"], vv["readings"]["V-ATLAS"]["valid"]),
                      "A3_fail": ([c for c, r in vo["readings"]["V-ATLAS"]["cells"].items() if not r["A3"]],
                                  [c for c, r in vv["readings"]["V-ATLAS"]["cells"].items() if not r["A3"]]),
                      "V-PRIOR_equal": vo["readings"]["V-PRIOR"]["valid"] == vv["readings"]["V-PRIOR"]["valid"]}
    for name in ("gover", "cr"):
        a, b = j(MV.READOUTS[name]), j(VF_WITH[name])
        out[f"{name} labels"] = {q: {"2D": (a["quadrants"][q]["2D"].get("outcome"), b["quadrants"][q]["2D"].get("outcome")),
                                     "3D": (a["quadrants"][q]["3D"]["outcome"], b["quadrants"][q]["3D"]["outcome"])}
                                 for q in a["quadrants"]}
    xo, xv = j(MV.READOUTS["xk"]), j(VF_WITH["xk"])
    out["X agreement"] = {fam: {"outcome": (xo[fam].get("outcome"), xv[fam].get("outcome")),
                                **{r: {k: (xo[fam][r][k], xv[fam][r][k]) for k in ("chi2_4", "p")}
                                   for r in ("r0", "r1") if r in xo[fam]}}
                          for fam in ("primary", "Q_R_alone", "C_PL_pair_zero") if fam in xo}
    eo, ev = j(MV.READOUTS["e2"]), j(VF_WITH["e2"])
    out["E2"] = {"within_seed_variation": (eo["reading"]["within_seed_variation"], ev["reading"]["within_seed_variation"]),
                 "delta_max_abs": (eo["delta_max_abs"], ev["delta_max_abs"]),
                 "largest_change_at": tuple(e2_largest(x) for x in (eo, ev)),
                 "delta_flag": ((eo["delta_flag"]["value"], eo["delta_flag"]["exceeded"]),
                                (ev["delta_flag"]["value"], ev["delta_flag"]["exceeded"]))}
    go, gv = j(MV.READOUTS["gdefs"]), j(VF_WITH["gdefs"])
    flags = []
    for g, rec in go["generators"].items():
        for t, r in rec.items():
            if isinstance(r, dict) and "seed_spread_flag" in r:
                flags.append((f"{g}/{t}", r["seed_spread_flag"], gv["generators"][g][t]["seed_spread_flag"]))
    out["gdefs seed flags"] = flags
    return out


def e2_largest(e2):
    """(arm, generator, kind) of E2's largest |change|, the cell make_values_fived16 :443 names."""
    return list(max((abs(e2["chi2"][a][n][k]["delta"]), a, n, k) for a in ("with", "nopl")
                    for n in e2["chi2"][a] for k in ("total", "shape_only"))[1:])


def headline(dr):
    """The outcome changes, one line each, read from the records below (no hand-written verdicts)."""
    H = []
    f = dr["F0/F0b/F1 listings"]["changes"]
    unl = sorted({r["truth"] for r in f if r["listed_old"] and not r["listed_vf"]})
    still = sorted({r["truth"] for r in f if r["listed_old"] and r["listed_vf"]})
    H.append(f"F0/F0b/F1: no longer listed {unl}; still listed {still}; newly listed "
             f"{sorted({r['truth'] for r in f if r['listed_vf'] and not r['listed_old']})}")
    for k, (a, b) in {**dr["RSN conclusions"], **dr["RSN arm verdicts"]}.items():
        if a != b:
            H.append(f"RSN {k}: \"{a}\" -> \"{b}\"")
    H.append("RSN regrade: " + "; ".join(f"{g} listed {x['listed'][0]} -> {x['listed'][1]}"
                                          for g, x in dr["RSN regrade"].items() if x["listed"][0] != x["listed"][1]))
    p = dr["PRR"]
    H.append(f"PRR: {p['flags_cleared']} flags cleared, {len(p['flags_set_under_vf'])} set")
    for name in ("gover labels", "cr labels"):
        for q, x in dr[name].items():
            for dim in ("2D", "3D"):
                if x[dim][0] != x[dim][1]:
                    H.append(f"{name.split()[0]} {q} {dim}: \"{x[dim][0]}\" -> \"{x[dim][1]}\"")
    for fam, x in dr["X agreement"].items():
        if x["outcome"][0] != x["outcome"][1]:
            H.append(f"X {fam}: {x['outcome'][0]} -> {x['outcome'][1]}")
    e = dr["E2"]
    if e["largest_change_at"][0] != e["largest_change_at"][1]:
        H.append(f"E2's largest change moves: {'/'.join(e['largest_change_at'][0])} -> {'/'.join(e['largest_change_at'][1])}")
    v = dr["V-ATLAS"]
    if v["valid"][0] != v["valid"][1] or v["A3_fail"][0] != v["A3_fail"][1]:
        H.append(f"V-ATLAS: valid/A3 changes")
    return H


def md(rec):
    dr = rec["decision_rules"]
    L = ["# V_F (C_e^infl) readings, Phases 1 and 2: OLD -> C_e^infl", "",
         "Read by `vf_readings.py`; readings go to the director first; nothing here is note wording.", "",
         "## 1. Decision-rule outcome changes (first, each on its own)", "",
         "**Headline (every outcome that changes; anything not named holds):**", ""]
    L += [f"- {h}" for h in headline(dr)] + [""]
    f = dr["F0/F0b/F1 listings"]
    L += [f"**F0/F0b/F1 listings** (p < 0.01 or any |z| > 2): STOPs {len(f['stops'])}; changes:", ""]
    L += [f"- {r['readout']} {r['truth']}: listed {r['listed_old']} -> {r['listed_vf']}; |z|>2 cells "
          f"{' '.join(r['cells_old']) or '-'} -> {' '.join(r['cells_vf']) or '-'}; p {r['p_old']:.3g} -> {r['p_vf']:.3g}"
          for r in f["changes"]]
    p = dr["PRR"]
    L += ["", f"**PRR (PR-3, p < 0.01 or any |z| > 2):** flags set under V_F: {len(p['flags_set_under_vf'])}; "
          f"flags cleared: {p['flags_cleared']}; PR-1 unchanged: {p['PR-1_equal']}; labels unchanged: {p['labels_equal']}.", ""]
    for lv, x in p["PR-3"].items():
        o, v = x["old"], x["vf"]
        if o != v:
            L.append(f"- {lv}: {o['reading']} {o['new_flags']} -> {v['reading']} {v['new_flags']}")
            if "q3" in v["new_flags"] and "q3" not in o["new_flags"]:
                L.append("  - *q3 here is a reference shift, not a new flag:* q3 is flagged at this level under both OLD "
                         "and V_F; it appears \"new\" only because B0's own q3 flag clears under V_F (the director, "
                         "2026-11-26).")
    L += ["", "**RSN regrade** (listed truths; triggers by group):", ""]
    for a, x in dr["RSN regrade"].items():
        lo, lv_ = x["listed"]
        L.append(f"- {a}: listed {lo} -> {lv_}")
    L += ["", "**RSN conclusions and arm verdicts:**", ""]
    L += [f"- {k}: {'unchanged' if a == b else f'{a} -> {b}'}" for k, (a, b) in dr["RSN conclusions"].items()]
    L += [f"- {k}: {'unchanged' if a == b else f'{a} -> {b}'}" for k, (a, b) in dr["RSN arm verdicts"].items()]
    v = dr["V-ATLAS"]
    L += ["", f"**V-ATLAS:** valid {v['valid'][0]} -> {v['valid'][1]}; A3 fails {v['A3_fail'][0]} -> {v['A3_fail'][1]}; "
          f"V-PRIOR unchanged: {v['V-PRIOR_equal']}.", ""]
    for name in ("gover labels", "cr labels"):
        L.append(f"**{name}:** " + "; ".join(f"{q} 2D {a} -> {b}" for q, x in dr[name].items()
                                             for a, b in [x["2D"]] if a != b) + " (3D unchanged in every quadrant)"
                 if all(x["3D"][0] == x["3D"][1] for x in dr[name].values()) else f"**{name}:** {dr[name]}")
    L += ["", "**X agreement (p >= 0.05 and every |z| <= 2.50):**", ""]
    for fam, x in dr["X agreement"].items():
        L.append(f"- {fam}: {x['outcome'][0]} -> {x['outcome'][1]}; " + "; ".join(
            f"{r} chi2_4 {x[r]['chi2_4'][0]:.3f} -> {x[r]['chi2_4'][1]:.3f}, p {x[r]['p'][0]:.3f} -> {x[r]['p'][1]:.3f}"
            for r in ("r0", "r1") if r in x))
    e = dr["E2"]
    L += ["", f"**E2:** within seed variation {e['within_seed_variation'][0]} -> {e['within_seed_variation'][1]}; "
          f"Delta_max {e['delta_max_abs'][0]:.2f} -> {e['delta_max_abs'][1]:.2f}; the 2.3 flag "
          f"{e['delta_flag'][0][0]:.2f} ({e['delta_flag'][0][1]}) -> {e['delta_flag'][1][0]:.2f} ({e['delta_flag'][1][1]}); "
          f"largest change at {'/'.join(e['largest_change_at'][0])} -> {'/'.join(e['largest_change_at'][1])}.",
          "", "**gdefs seed flags:** " + ("unchanged in every record" if all(a == b for _, a, b in dr["gdefs seed flags"])
                                           else str([x for x in dr["gdefs seed flags"] if x[1] != x[2]])), ""]
    L += ["## 1b. make_values_fived16's guards that fail under V_F (each a note-side follow-up)", "",
          "The V_F run uses a copy of the module whose assert statements record instead of raise (an in-process AST "
          "rewrite; no file changed); the OLD run uses the module unchanged, every guard passing.", ""]
    src = (ROOT / "docs/analysis-note/make_values_fived16.py").read_text().splitlines()
    L += [f"- make_values_fived16.py:{g['line']}: {g['message'] if g['message'] is not None else '(no message) `' + src[g['line'] - 1].strip() + '`'}"
          for g in rec["vf_guard_failures"]] or ["- none"]
    L += [""]
    L += ["## 2. Every moved \\fvval key, OLD -> V_F (with print sites)", "",
          f"{rec['n_moved']} of {rec['n_keys']} keys move; {len(rec['moved_printed'])} of them are printed.", "",
          "| key | OLD | V_F | printed at |", "|---|---|---|---|"]
    for k in rec["moved_printed"]:
        x = rec["values"][k]
        L.append(f"| `{k}` | {x['old']} | {x['vf']} | {', '.join(x['sites'][:3])}{' ...' if len(x['sites']) > 3 else ''} |")
    L += ["", f"Moved but not printed: {len(rec['moved']) - len(rec['moved_printed'])} keys (in vf_readings.json).", "",
          "## 3. The printed-xk check (A4)", "",
          f"xk's printed strings from this Mac's OLD replay equal the committed k.json's: {rec['xk_print_check']['equal']} "
          f"({rec['xk_print_check']['n_keys']} xk-dependent keys compared).", "",
          "## 4. The S1/C_resp sigma rows both ways, and the per-cell sigma", "",
          "The C_e form is the OLD value; the C_e^infl form is from the V_F data product (phase1_readings.py, its "
          "section 3, has all sixteen cells). Joseph's open question (declaration section 4.3).", "",
          "## 5. Follow-ups for other lanes (after the director's review)", "",
          "- make_values_fived16.py: READOUTS, NOPL_READOUTS (the V_F files above), ARMS (VF_ARMS), MATRIX_KEYS; its literal "
          "\"C_total_plus_C_resp\" (:678, :689) and the C_PL5D label (:700-702) as supplied here; make_values_landed.py's "
          "\"vr\".", "- make_supplemental.py, fived16_headline, fived16_genresidual, the EA2 redraw, valid_region.py's COV_KEY.",
          "", "Shims in the V_F run (the note's literal names): " + " | ".join(SHIMS), "",
          "NOT CITABLE FOR: a validated size for C_e^infl; a coverage or calibration statement; any note wording."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    old = MV.all_values()
    vf, guard_fails = run_vf()
    lo, lv = landed(False), landed(True)
    old.update({f"landed:{k}": v for k, v in lo.items()})
    vf.update({f"landed:{k}": v for k, v in lv.items()})
    mac = run_old_with_mac_xk()
    diff_mac = sorted(k for k in mac if mac[k] != old.get(k))
    keys = sorted(set(old) | set(vf))
    moved = [k for k in keys if old.get(k) != vf.get(k)]
    sites = print_sites()
    moved_printed = [k for k in moved if sites.get(k.replace("landed:", ""))]
    rec = {"schema": "fd-vf-readings/2", "shims": SHIMS, "vf_readouts": VF_WITH, "vf_nopl_readouts": VF_NOPL,
           "vf_vr": VF_VR, "vf_arms": VF_ARMS,
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "make_values_fived16_sha256": hashlib.sha256((ROOT / "docs/analysis-note/make_values_fived16.py").read_bytes()).hexdigest(),
           "make_values_landed_sha256": hashlib.sha256((ROOT / "docs/analysis-note/make_values_landed.py").read_bytes()).hexdigest(),
           "n_keys": len(keys), "n_moved": len(moved), "moved": moved, "moved_printed": moved_printed,
           "xk_print_check": {"equal": not diff_mac, "differing_keys": diff_mac, "n_keys": len(mac)},
           "vf_guard_failures": [{"line": ln, "message": None if m is None else str(m)} for ln, m in guard_fails],
           "decision_rules": decision_rules(),
           "values": {k: {"old": old.get(k), "vf": vf.get(k), "sites": sites.get(k.replace("landed:", ""), [])}
                      for k in keys}}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "vf_readings.json").write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
    (a.out_dir / "vf_readings.md").write_text(md(rec))
    print(f"keys {len(keys)}; moved {len(moved)} ({len(moved_printed)} printed); printed-xk check "
          f"{'equal' if not diff_mac else diff_mac[:5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
