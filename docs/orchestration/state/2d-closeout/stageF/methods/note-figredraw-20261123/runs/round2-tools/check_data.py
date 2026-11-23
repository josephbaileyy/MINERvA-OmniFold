#!/usr/bin/env python3
"""Data equality of the two arms of one redrawn figure (note-figredraw-20261123, README.md "Checks").

usage: python3 -I check_data.py <bkg|cov|f16> <runs/<fig> dir>

Reads each arm's capture (note-figstyle-20261117/tools/capture_palette.py: every data artist's arrays, as
fig-restyle-20261031/tools/artists.py collects them). In each arm, every marker point is paired with the vertical bar
segment drawn at the same x on the same axes (exactly one) and, where drawn, its cap markers. Each point is named:
  arm 0 by the ORIGINAL producer's x rule (fig_m3_background.py: k -+ 0.17 over EW0..41 / J..,total;
        fig_m3_coverage.py: k -+ 0.18 over EW..,EW_all_ones,J..,total; make_fig_fived16_headline.py: i + 0.7 (i//4));
  arm 1 by the (axes, x) the redraw copy wrote in its <stem>_data.json.
ROUND 2 (2026-11-23): f16 compares the one round-2 figure (fived16_headline.pdf, its _data.json) with arm 0 and asserts
all 16 markers share one style; bkg and cov are unchanged.
Then, per (series, functional or cell name), it asserts:
  1. the set of plotted names is identical in the two arms (none added, dropped or duplicated);
  2. y, bar lower end, bar upper end (and the caps) are BIT-equal between arms (float64 bytes);
  3. the arm-0 values equal the committed receipt's numbers (independent of both producers' drawing code);
  4. the arm-1 dump's y and error equal arm 1's drawn artists (the dump is what was drawn);
  5. for cov, the filled/open state of every point is the same in both arms; for bkg, arm 1's filled state is
     |mean_rel/se_rel| > t_crit of the s5n receipt and its counts per panel are printed.
It prints every artist that is not a named data point (decoration: reference lines, shading, separators), per arm, and
the difference between the arms' decoration lists. Exit 0 only if 1-5 hold.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

FIG, RUN = sys.argv[1], Path(sys.argv[2])
REPO = Path(__file__).resolve().parents[8]
STEM = {"bkg": "m3_fig1_background", "cov": "m3_fig3_coverage", "f16": "fived16_headline"}[FIG]
INPUT = {"d1": ("docs/orchestration/state/s5c/d1/d1_summary.json",
                "f5c802e37bf196ed0c1ecbf2414decb7fa0f2bbc0459ca3422c191c26f4a3c44"),
         "s5n": ("docs/orchestration/state/s5n/stage1/dev_receipt.json",
                 "1ef4096c39e2cfb2ded7d7e70c649eebcea09fbd0b31dca97e7b9d16c9878526"),
         "tier_s": ("docs/orchestration/state/s5c/tier_s/interim_400.json",
                    "aa574c17756ac9cea55306a731728104f7e084621372c8941c91bd9d0aab031f"),
         "fd": ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/data-product/"
                "fd_data_product_cpl.json", "d6752d2c")}
bad = []


def need(ok, msg):
    if not ok:
        bad.append(msg)
        print("FAIL", msg)


def load_input(key):
    rel, pin = INPUT[key]
    b = (REPO / rel).read_bytes()
    assert hashlib.sha256(b).hexdigest().startswith(pin), f"{rel}: sha256 is not the pin {pin}"
    return json.loads(b)


def capture(arm, pdf):
    p = RUN / arm / "capture" / f"{pdf}.json"
    idx, z = json.loads(p.read_text()), np.load(str(p)[:-5] + ".npz")
    return [dict(it, arr={k.split(".", 1)[1]: z[k] for k in z.files if k.split(".")[0] == f"i{it['i']}"}) for it in idx]


def points(items):
    """[(axes, x, y, lo, hi, caps, mfc, marker)] for every marker point; and the decoration items."""
    pts, used, deco = [], set(), []
    marks = [it for it in items if it["kind"] == "line" and it["style"]["marker"] not in ("None", "", "_")
             and it["style"]["linestyle"] in ("None", "none") and len(it["arr"]["xy"]) and it["label"] != "_break"]
    segs = {}   # (axes, x) -> [(item i, lo, hi)]
    for it in items:
        if it["kind"] == "LineCollection" and "segments" in it["arr"]:
            s, n = it["arr"]["segments"], it["arr"]["segment_lengths"].astype(int)
            k = 0
            for m in n:
                seg = s[k:k + m]
                k += m
                if m == 2 and seg[0, 0] == seg[1, 0]:
                    segs.setdefault((it["axes"], float(seg[0, 0])), []).append((it["i"], seg[0, 1], seg[1, 1]))
    caps = {}
    for it in items:
        if it["kind"] == "line" and it["style"]["marker"] == "_":
            for x, y in it["arr"]["xy"]:
                caps.setdefault((it["axes"], float(x)), []).append(y)
            used.add(it["i"])
    for it in marks:
        used.add(it["i"])
        for x, y in it["arr"]["xy"]:
            s = segs.get((it["axes"], float(x)), [])
            if len(s) != 1:
                need(False, f"point at axes {it['axes']} x {x}: {len(s)} bar segments")
                continue
            used.add(s[0][0])
            pts.append((it["axes"], float(x), y, min(s[0][1:]), max(s[0][1:]),
                        tuple(sorted(caps.get((it["axes"], float(x)), []))),
                        tuple(np.round(it["arr"]["mfc"], 6)), it["style"]["marker"]))
    for it in items:
        if it["i"] not in used:
            deco.append(f"axes{it['axes']}:{it['kind']}:{it['style'].get('linestyle', '')}:"
                        f"{it['style'].get('marker', '')}:n={len(it['arr'].get('xy', it['arr'].get('segment_lengths', [])))}")
    return pts, deco


def bits(v):
    return np.asarray(v, np.float64).tobytes()


def compare(a0, a1, label):
    k0, k1 = set(a0), set(a1)
    need(k0 == k1, f"{label}: plotted names differ: arm 0 only {sorted(k0 - k1)[:10]}, arm 1 only {sorted(k1 - k0)[:10]}")
    neq = [k for k in sorted(k0 & k1) if any(bits(a0[k][f]) != bits(a1[k][f]) for f in ("y", "lo", "hi", "caps"))]
    need(not neq, f"{label}: values not bit-equal for {neq[:10]}")
    print(f"{label}: {len(k0 & k1)} (series, name) points; y, bar ends{', caps' if FIG == 'f16' else ''} bit-equal "
          f"in both arms: {not neq}")


def deco_report(d0, d1, label):
    c0, c1 = Counter(d0), Counter(d1)
    print(f"{label}: decoration artists (not data points): arm 0 {sum(c0.values())}, arm 1 {sum(c1.values())}")
    print(f"   arm 0 only: {sorted((c0 - c1).elements())}")
    print(f"   arm 1 only: {sorted((c1 - c0).elements())}")


if FIG == "bkg":
    d1, s5n = load_input("d1"), load_input("s5n")
    names = d1["functional_names"]
    g, c3 = d1["groups"]["split_F2"], s5n["grid"]["C3_nominal"]
    val = {"purity": (100 * np.array(g["mean_rel"]), 100 * np.array(g["se_rel"])),
           "refined": (100 * np.array(c3["per_functional"]["mean_rel"]), 100 * np.array(c3["per_functional"]["se_rel"]))}
    ew = [names.index(f"EW{i}") for i in range(42)]
    jj = [i for i, n in enumerate(names) if n.startswith("J")] + [names.index("total_integrated")]
    p0, dec0 = points(capture("arm0", f"{STEM}.pdf"))
    a0 = {}
    for ax, x, y, lo, hi, caps, mfc, mk in p0:
        ser, dx = ("purity", -0.17) if mk == "o" else ("refined", 0.17)
        k = int(round(x - dx))
        assert abs(x - (k + dx)) < 1e-12
        nm = names[(ew if ax == 0 else jj)[k]]
        assert (ser, nm) not in a0
        a0[(ser, nm)] = {"y": y, "lo": lo, "hi": hi, "caps": caps}
    # 3. arm 0 against the receipts
    r3 = [k for k, v in a0.items() if not (bits(v["y"]) == bits(val[k[0]][0][names.index(k[1])])
                                           and bits(v["lo"]) == bits(val[k[0]][0][names.index(k[1])] - val[k[0]][1][names.index(k[1])])
                                           and bits(v["hi"]) == bits(val[k[0]][0][names.index(k[1])] + val[k[0]][1][names.index(k[1])]))]
    need(not r3, f"arm 0 differs from the receipts for {r3[:10]}")
    print(f"arm 0 against the receipts (100 x mean_rel, y -+ 100 x se_rel): {len(a0) - len(r3)}/{len(a0)} bit-equal")
    dump = json.loads((RUN / "arm1" / "out" / f"{STEM}_data.json").read_text())
    axes_of = {"a_main": 0, "a_strip": 1, "b": 2}
    name_at, fill_at, dumpv = {}, {}, {}
    for s in dump["series"]:
        for p in s["points"]:
            key = (axes_of[s["axes"]], p["x"])
            assert key not in name_at
            name_at[key] = (s["series"], p["name"])
            fill_at[(s["series"], p["name"])] = s["filled"]
            dumpv[(s["series"], p["name"])] = (p["y"], p["err"])
    p1, dec1 = points(capture("arm1", f"{STEM}.pdf"))
    a1 = {}
    for ax, x, y, lo, hi, caps, mfc, mk in p1:
        k = name_at[(ax, x)]
        assert k not in a1
        need((mk == "o") == (k[0] == "purity"), f"{k}: marker {mk}")
        a1[k] = {"y": y, "lo": lo, "hi": hi, "caps": caps, "open": mfc == (1.0, 1.0, 1.0, 1.0)}
    compare(a0, a1, "bkg")
    r4 = [k for k, (y, e) in dumpv.items() if not (bits(a1[k]["y"]) == bits(y) and bits(a1[k]["lo"]) == bits(y - e)
                                                   and bits(a1[k]["hi"]) == bits(y + e))]
    need(not r4, f"arm 1 dump differs from its artists for {r4[:10]}")
    print(f"arm 1 dump against arm 1's artists: {len(dumpv) - len(r4)}/{len(dumpv)} bit-equal")
    t = np.array(c3["per_functional"]["mean_rel"]) / np.array(c3["per_functional"]["se_rel"])
    tc = c3["criterion"]["t_crit"]
    r5 = [k for k in a1 if k[0] == "refined" and (not a1[k]["open"]) != bool(abs(t[names.index(k[1])]) > tc)]
    need(not r5, f"filled state is not |t| > {tc} for {r5[:10]}")
    na = sum(1 for k in a1 if k[0] == "refined" and not a1[k]["open"] and k[1].startswith("EW"))
    nb = sum(1 for k in a1 if k[0] == "refined" and not a1[k]["open"] and not k[1].startswith("EW"))
    unpl = [n for n in names if ("refined", n) not in a1]
    nu = sum(1 for n in unpl if abs(t[names.index(n)]) > tc)
    need(na + nb + nu == c3["n_abs_t_gt_crit"], "fail count")
    print(f"filled = |t| > {tc}: all {sum(k[0] == 'refined' for k in a1)} refined points agree: {not r5}; filled in "
          f"panel (a) {na}/42, panel (b) {nb}/110; unplotted {unpl} with |t| > t_crit: {nu}; total {na + nb + nu} = "
          f"receipt n_abs_t_gt_crit {c3['n_abs_t_gt_crit']}: {na + nb + nu == c3['n_abs_t_gt_crit']}")
    need(sorted({k[1] for k in a1}) == sorted(names[i] for i in ew + jj), "plotted functionals are not EW0..41, J, total")
    print(f"plotted functionals: {len({k[1] for k in a1})} (42 EW, 109 J, total); not plotted in either arm: {unpl}")
    deco_report(dec0, dec1, "bkg")

elif FIG == "cov":
    d = load_input("tier_s")
    names = d["functional_names"]
    g = {x["truth"]: x for x in d["grid"]}["eavail_tilt"]
    order = ([i for i, n in enumerate(names) if n.startswith("EW")]
             + [i for i, n in enumerate(names) if n.startswith("J")] + [names.index("total_integrated")])
    THR = {"68": 0.66, "95": 0.94}
    p0, dec0 = points(capture("arm0", f"{STEM}.pdf"))
    a0 = {}
    for ax, x, y, lo, hi, caps, mfc, mk in p0:
        lvl, dx = ("68", -0.18) if mk == "o" else ("95", 0.18)
        k = int(round(x - dx))
        assert abs(x - (k + dx)) < 1e-12
        nm = names[order[k]]
        assert (lvl, nm) not in a0
        a0[(lvl, nm)] = {"y": y, "lo": lo, "hi": hi, "caps": caps, "open": mfc == (1.0, 1.0, 1.0, 1.0)}
    r3 = []
    for (lvl, nm), v in a0.items():
        i = names.index(nm)
        c = np.array(g[f"hits{lvl}"]) / g["n_present"]
        ok = (bits(v["y"]) == bits(c[i]) and bits(v["lo"]) == bits(g[f"lcb{lvl}"][i])
              and bits(v["hi"]) == bits(g[f"ucb{lvl}"][i]) and v["open"] == (not g[f"ucb{lvl}"][i] < THR[lvl]))
        if not ok:
            r3.append((lvl, nm))
    need(not r3, f"arm 0 differs from the receipt for {r3[:10]}")
    print(f"arm 0 against the receipt (hits/400, lcb, ucb, filled = ucb < threshold): {len(a0) - len(r3)}/{len(a0)} equal")
    dump = json.loads((RUN / "arm1" / "out" / f"{STEM}_data.json").read_text())
    name_at, dumpv = {}, {}
    for lvl, pts in dump["levels"].items():
        for p in pts:
            key = ({"a": 0, "b": 1}[p["panel"]], p["x"])
            assert key not in name_at
            name_at[key] = (lvl, p["name"])
            dumpv[(lvl, p["name"])] = p
    p1, dec1 = points(capture("arm1", f"{STEM}.pdf"))
    a1 = {}
    for ax, x, y, lo, hi, caps, mfc, mk in p1:
        k = name_at[(ax, x)]
        assert k not in a1
        need((mk == "o") == (k[0] == "68"), f"{k}: marker {mk}")
        a1[k] = {"y": y, "lo": lo, "hi": hi, "caps": caps, "open": mfc == (1.0, 1.0, 1.0, 1.0)}
    compare(a0, a1, "cov")
    r5 = [k for k in a0 if k in a1 and a0[k]["open"] != a1[k]["open"]]
    need(not r5, f"filled/open differs for {r5[:10]}")
    print(f"filled/open state equal in both arms for all {len(a0)} points: {not r5}; filled per panel (68%, 95%): "
          f"(a) {[sum(1 for k in a1 if k[0] == l and not a1[k]['open'] and k[1].startswith('EW')) for l in ('68', '95')]}, "
          f"(b) {[sum(1 for k in a1 if k[0] == l and not a1[k]['open'] and not k[1].startswith('EW')) for l in ('68', '95')]}")
    r4 = [k for k, p in dumpv.items() if not (bits(a1[k]["y"]) == bits(p["coverage"]) and bits(a1[k]["lo"]) == bits(p["lcb"])
                                              and bits(a1[k]["hi"]) == bits(p["ucb"]) and a1[k]["open"] == (not p["filled"]))]
    need(not r4, f"arm 1 dump differs from its artists for {r4[:10]}")
    print(f"arm 1 dump against arm 1's artists: {len(dumpv) - len(r4)}/{len(dumpv)} equal")
    print(f"plotted functionals: {len({k[1] for k in a1})} of {len(names)}")
    deco_report(dec0, dec1, "cov")

else:
    fd = load_input("fd")
    UNIT = 1e-40
    f = [x / UNIT for x in fd["f"]]
    C = fd["matrices"]["C_total_plus_C_resp_plus_C_PL5D"]
    sig = [float(np.sqrt(C[i][i])) / UNIT for i in range(16)]
    names = [c["cell"] for c in fd["cells"]]
    xs = [i + 0.7 * (i // 4) for i in range(16)]
    p0, dec0 = points(capture("arm0", f"{STEM}.pdf"))
    a0 = {}
    for ax, x, y, lo, hi, caps, mfc, mk in p0:
        i = xs.index(x)
        a0[names[i]] = {"y": y, "lo": lo, "hi": hi, "caps": caps}
    r3 = [n for n, v in a0.items() if not (bits(v["y"]) == bits(f[names.index(n)])
                                           and abs((v["hi"] - v["lo"]) / 2 - sig[names.index(n)]) <= 1e-12 * sig[names.index(n)]
                                           and v["caps"] == (v["lo"], v["hi"]))]
    need(not r3, f"arm 0 differs from the record for {r3}")
    print(f"arm 0 against the record (f bit-equal; half bar = sqrt(diag) to 1e-12, the producer's own tolerance; caps at "
          f"the bar ends): {16 - len(r3)}/16")
    for v in ("round 2",):   # round 1 drew variants A and B; round 2 draws one figure (fived16_headline.pdf)
        dump = json.loads((RUN / "arm1" / "out" / f"{STEM}_data.json").read_text())
        name_at = {p["x"]: p["cell"] for p in dump["points"]}
        p1, dec1 = points(capture("arm1", f"{STEM}.pdf"))
        a1 = {}
        for ax, x, y, lo, hi, caps, mfc, mk in p1:
            a1[name_at[x]] = {"y": y, "lo": lo, "hi": hi, "caps": caps, "marker": mk, "mfc": mfc}
        compare(a0, a1, f"f16 variant {v}")
        r4 = [p["cell"] for p in dump["points"] if not (bits(a1[p["cell"]]["y"]) == bits(p["f"])
                                                        and abs((a1[p["cell"]]["hi"] - a1[p["cell"]]["lo"]) / 2 - p["sigma"]) <= 1e-12 * p["sigma"])]
        need(not r4, f"variant {v} dump differs from its artists for {r4}")
        print(f"variant {v} dump against its artists: {16 - len(r4)}/16")
        need(len({(a1[n]["marker"], a1[n]["mfc"]) for n in a1}) == 1 and len(a1) == 16, "f16: markers not uniform")
        deco_report(dec0, dec1, f"f16 variant {v}")

print(f"CHECK-DATA {FIG} :: {'PASS' if not bad else 'FAIL'}")
sys.exit(1 if bad else 0)
