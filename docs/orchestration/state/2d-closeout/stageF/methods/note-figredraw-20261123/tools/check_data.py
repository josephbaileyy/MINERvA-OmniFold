#!/usr/bin/env python3
"""Data equality of the two arms of one redrawn figure (note-figredraw-20261123, README.md "Checks").

usage: python3 -I check_data.py <bkg|cov|f16> <run dir> <R|D>

Reads each arm's capture (note-figstyle-20261117/tools/capture_palette.py: every data artist's arrays, as
fig-restyle-20261031/tools/artists.py collects them). In each arm, every marker point is paired with the vertical bar
segment drawn at the same x on the same axes (exactly one) and, where drawn, its cap markers. Each point is named:
  arm 0 by the ORIGINAL producer's x rule (fig_m3_background.py: k -+ 0.17 over EW0..41 / J..,total;
        fig_m3_coverage.py: k -+ 0.18 over EW..,EW_all_ones,J..,total; make_fig_fived16_headline.py: i + 0.7 (i//4));
  arm 1 by the (axes, x) the redraw copy wrote in its <stem>_data.json.
ROUND 2 (2026-11-23): f16 compares the one round-2 figure (fived16_headline.pdf, its _data.json) with arm 0 and asserts
all 16 markers share one style; bkg and cov are unchanged.
ROUND 3 (2026-11-23): a third argument names the variant (R or D). Points are named from the dump's own axes index
(dump["axes_index"] / each point's "axes"). Added per variant:
  bkg R  the annotation names J88 and its |t| is the receipt's max_abs_t;
  bkg D  panel (a) is two heatmaps: per functional name, the drawn colour value (the QuadMesh array) is bit-equal to
         arm 0's plotted y, the dump's error matches arm 0's bar ends, the printed string is fmt(arm 0 y) and occurs
         among the drawn texts, bold = |t| > t_crit; both meshes share one symmetric colour limit; the 84 bars of
         panel (a) are listed as not drawn in arm 1 (the value is drawn, the bar is not);
  cov    the printed failure counts equal the receipt's counts; D: within each family the points run in increasing
         upper bound and every point's (level, name) is drawn once;
  f16 R  the printed value labels equal three significant figures of arm 0's y for R04 and R14;
  f16 D  horizontal bars: the point's x and the bar's x ends are compared with arm 0's y and bar ends.
ROUND 4 (2026-11-23): variant P, the polish of the reviewer's choices, runs its base variant's checks: bkg P = bkg D's
  (heatmaps, panel (b) points) plus bkg R's annotation check (J88, receipt max_abs_t, drawn once); cov P = cov D's;
  f16 P = f16 R's (value labels).
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

FIG, RUN, VAR = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
assert VAR in ("R", "D", "P"), VAR
BASE = {"bkg": "D", "cov": "D", "f16": "R"}[FIG] if VAR == "P" else VAR   # ROUND 4: P is checked as its base variant
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


def points(items, horizontal=False):
    """[(axes, position, value, lo, hi, caps, mfc, marker)] for every marker point; and the decoration items.
    Vertical bars (default): position = x, value = y, bar ends and caps in y. ROUND 3, horizontal=True (f16 D):
    position = y, value = x, bar ends and caps in x."""
    pts, used, deco = [], set(), []
    marks = [it for it in items if it["kind"] == "line" and it["style"]["marker"] not in ("None", "", "_", "|")
             and it["style"]["linestyle"] in ("None", "none") and len(it["arr"]["xy"]) and it["label"] != "_break"]
    P, V = (1, 0) if horizontal else (0, 1)   # column of the position and of the value in an (x, y) pair
    segs = {}   # (axes, position) -> [(item i, lo, hi)]
    for it in items:
        if it["kind"] == "LineCollection" and "segments" in it["arr"]:
            s, n = it["arr"]["segments"], it["arr"]["segment_lengths"].astype(int)
            k = 0
            for m in n:
                seg = s[k:k + m]
                k += m
                if m == 2 and seg[0, P] == seg[1, P]:
                    segs.setdefault((it["axes"], float(seg[0, P])), []).append((it["i"], seg[0, V], seg[1, V]))
    caps = {}
    for it in items:
        if it["kind"] == "line" and it["style"]["marker"] == ("|" if horizontal else "_"):
            for xy in it["arr"]["xy"]:
                caps.setdefault((it["axes"], float(xy[P])), []).append(xy[V])
            used.add(it["i"])
    for it in marks:
        used.add(it["i"])
        for xy in it["arr"]["xy"]:
            pos, val = float(xy[P]), xy[V]
            s = segs.get((it["axes"], pos), [])
            if len(s) != 1:
                need(False, f"point at axes {it['axes']} position {pos}: {len(s)} bar segments")
                continue
            used.add(s[0][0])
            pts.append((it["axes"], pos, val, min(s[0][1:]), max(s[0][1:]),
                        tuple(sorted(caps.get((it["axes"], pos), []))),
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




def drawn_texts(arm, pdf):
    """Counter of every drawn text string of an arm's figure (capture_palette.py .texts)."""
    d = json.loads((RUN / arm / "capture" / f"{pdf}.texts").read_text())
    return Counter(t for _, t in d["texts"])


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
    assert dump["variant"] == VAR, dump["variant"]
    axes_of = dump["axes_index"]
    name_at, dumpv = {}, {}
    for s in dump["series"]:
        for p in s["points"]:
            key = (axes_of[s["axes"]], p["x"])
            assert key not in name_at
            name_at[key] = (s["series"], p["name"])
            dumpv[(s["series"], p["name"])] = (p["y"], p["err"])
    items1 = capture("arm1", f"{STEM}.pdf")
    p1, dec1 = points(items1)
    a1 = {}
    for ax, x, y, lo, hi, caps, mfc, mk in p1:
        k = name_at[(ax, x)]
        assert k not in a1
        need((mk == "o") == (k[0] == "purity"), f"{k}: marker {mk}")
        a1[k] = {"y": y, "lo": lo, "hi": hi, "caps": caps, "open": mfc == (1.0, 1.0, 1.0, 1.0)}
    t = np.array(c3["per_functional"]["mean_rel"]) / np.array(c3["per_functional"]["se_rel"])
    tc = c3["criterion"]["t_crit"]
    heat = {}
    if BASE == "D":
        # panel (a) is drawn as heatmaps: compare the marker points of panel (b) here, the heatmaps below
        a0_pts = {k: v for k, v in a0.items() if not k[1].startswith("EW")}
        a0_ew = {k: v for k, v in a0.items() if k[1].startswith("EW")}
        compare(a0_pts, a1, "bkg D panel (b) points")
        texts1 = drawn_texts("arm1", f"{STEM}.pdf")
        meshes = {it["gid"]: it for it in items1 if it["kind"] == "QuadMesh" and str(it["gid"]).startswith("heat:")}
        need(sorted(meshes) == ["heat:purity", "heat:refined"], f"heatmap meshes: {sorted(meshes)}")
        clims = {tuple(meshes[m]["arr"]["clim"]) for m in meshes}
        need(len(clims) == 1 and list(clims)[0][0] == -list(clims)[0][1],
             f"the two heatmaps do not share one zero-centred colour limit: {clims}")
        bad_c, bad_t, bad_e, bad_b = [], [], [], []
        for ser in ("purity", "refined"):
            arr = np.asarray(meshes[f"heat:{ser}"]["arr"]["array"], np.float64).reshape(7, 6)
            cells = {c["name"]: c for c in dump["heatmaps"][ser]}
            need(set(cells) == {k[1] for k in a0_ew if k[0] == ser}, f"{ser}: heatmap names differ from arm 0's")
            for nm, c in cells.items():
                k = int(nm[2:])
                v0 = a0_ew[(ser, nm)]
                heat[(ser, nm)] = c
                if not (c["iE"], c["iW"]) == divmod(k, 6) or bits(arr[c["iE"], c["iW"]]) != bits(v0["y"]) \
                        or bits(c["value"]) != bits(v0["y"]):
                    bad_c.append((ser, nm))
                want = f"{v0['y']:.2f}".replace("-", "−")
                if c["text"] != want or texts1[want] < 1:
                    bad_t.append((ser, nm, c["text"], want))
                if bits(v0["y"] - c["err"]) != bits(v0["lo"]) or bits(v0["y"] + c["err"]) != bits(v0["hi"]):
                    bad_e.append((ser, nm))
                if c["bold"] != (ser == "refined" and bool(abs(t[names.index(nm)]) > tc)):
                    bad_b.append((ser, nm))
        need(not bad_c, f"heatmap colour value differs from arm 0's y for {bad_c[:10]}")
        need(not bad_t, f"printed heatmap number is not fmt(arm 0 y) or is not drawn: {bad_t[:10]}")
        need(not bad_e, f"heatmap dump error differs from arm 0's bar ends for {bad_e[:10]}")
        need(not bad_b, f"bold is not |t| > t_crit for {bad_b[:10]}")
        print(f"bkg D panel (a) heatmaps: {len(heat)} (series, name) cells; colour value (QuadMesh array) bit-equal to "
              f"arm 0's y: {len(heat) - len(bad_c)}/{len(heat)}; printed string = fmt(arm 0 y) and drawn: "
              f"{len(heat) - len(bad_t)}/{len(heat)}; dump error = arm 0's bar ends: {len(heat) - len(bad_e)}/{len(heat)}; "
              f"bold = |t| > {tc}: {len(heat) - len(bad_b)}/{len(heat)}; shared colour limits {sorted(clims)}")
        print(f"   shown in arm 0 and NOT drawn in arm 1: the {len(a0_ew)} error bars of panel (a) (arm 1 draws the value "
              f"as colour and number; the error is in the dump and checked above)")
        need(set(a0) == set(a1) | set(heat), "the plotted (series, name) set differs between arms")
        print(f"(series, name) set: arm 0 {len(a0)} = arm 1 points {len(a1)} + heatmap cells {len(heat)}: "
              f"{set(a0) == set(a1) | set(heat)}")
    else:
        compare(a0, a1, "bkg")
    if VAR in ("R", "P"):   # ROUND 4: P carries R's callout
        ann = dump["annotation"]
        need(ann["at"] == names[int(np.argmax(np.abs(t)))] == "J88" and ann["abs_t"] == c3["max_abs_t"]
             and round(c3["max_abs_t"], 2) == 14.42 and ann["text"] == f"up to {int(np.floor(c3['max_abs_t']))} standard errors",
             f"annotation {ann}")
        need(drawn_texts("arm1", f"{STEM}.pdf")[ann["text"]] == 1, "annotation text not drawn once")
        if VAR == "P":   # ROUND 4: the arrow tip is the drawn refinement square of J88 (x from the dump, y bit-equal)
            xs88 = [x for (axi, x), k in name_at.items() if k == ("refined", "J88") and axi == axes_of["b"]]
            need(len(xs88) == 1 and ann["xy"] == [xs88[0], float(a1[("refined", "J88")]["y"])],
                 f"annotation tip {ann.get('xy')} is not J88's drawn square {xs88}, {a1[('refined', 'J88')]['y']!r}")
            print(f"bkg P annotation tip {ann['xy']} = the drawn refinement square of J88 (x {xs88}, y bit-equal "
                  f"to arm 0's): {len(xs88) == 1 and ann['xy'] == [xs88[0], float(a1[('refined', 'J88')]['y'])]}")
        print(f"bkg {VAR} annotation: '{ann['text']}' at {ann['at']}, |t| {ann['abs_t']!r} = receipt max_abs_t "
              f"{c3['max_abs_t']!r} (14.42 to 2 d.p.: {round(c3['max_abs_t'], 2) == 14.42}); drawn once")
    r4 = [k for k, (y, e) in dumpv.items() if not (bits(a1[k]["y"]) == bits(y) and bits(a1[k]["lo"]) == bits(y - e)
                                                   and bits(a1[k]["hi"]) == bits(y + e))]
    need(not r4, f"arm 1 dump differs from its artists for {r4[:10]}")
    print(f"arm 1 dump against arm 1's artists: {len(dumpv) - len(r4)}/{len(dumpv)} bit-equal")
    r5 = [k for k in a1 if k[0] == "refined" and (not a1[k]["open"]) != bool(abs(t[names.index(k[1])]) > tc)]
    need(not r5, f"filled state is not |t| > {tc} for {r5[:10]}")
    marked = {k: not v["open"] for k, v in a1.items() if k[0] == "refined"}
    marked.update({k: c["bold"] for k, c in heat.items() if k[0] == "refined"})
    na = sum(1 for k, m in marked.items() if m and k[1].startswith("EW"))
    nb = sum(1 for k, m in marked.items() if m and not k[1].startswith("EW"))
    unpl = [n for n in names if ("refined", n) not in marked]
    nu = sum(1 for n in unpl if abs(t[names.index(n)]) > tc)
    need(na + nb + nu == c3["n_abs_t_gt_crit"], "fail count")
    print(f"marked = |t| > {tc} (filled squares; D panel (a): bold numbers): all {len(marked)} refined agree: "
          f"{not r5 and not (BASE == 'D' and bad_b)}; panel (a) {na}/42, panel (b) {nb}/110; unplotted {unpl} with "
          f"|t| > t_crit: {nu}; total {na + nb + nu} = receipt n_abs_t_gt_crit {c3['n_abs_t_gt_crit']}: "
          f"{na + nb + nu == c3['n_abs_t_gt_crit']}")
    need(sorted({k[1] for k in marked}) == sorted(names[i] for i in ew + jj), "plotted functionals are not EW0..41, J, total")
    print(f"plotted functionals: {len({k[1] for k in marked})} (42 EW, 109 J, total); not plotted in either arm: {unpl}")
    deco_report(dec0, dec1, f"bkg {VAR}")

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
    assert dump["variant"] == VAR, dump["variant"]
    name_at, dumpv = {}, {}
    for lvl, pts in dump["levels"].items():
        for p in pts:
            key = (p["axes"] if "axes" in p else {"a": 0, "b": 1}[p["panel"]], p["x"])
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
    compare(a0, a1, f"cov {VAR}")
    r5 = [k for k in a0 if k in a1 and a0[k]["open"] != a1[k]["open"]]
    need(not r5, f"filled/open differs for {r5[:10]}")
    print(f"filled/open state equal in both arms for all {len(a0)} points: {not r5}; filled (68%, 95%): "
          f"{[sum(1 for k in a1 if k[0] == l and not a1[k]['open']) for l in ('68', '95')]}")
    r4 = [k for k, p in dumpv.items() if not (bits(a1[k]["y"]) == bits(p["coverage"]) and bits(a1[k]["lo"]) == bits(p["lcb"])
                                              and bits(a1[k]["hi"]) == bits(p["ucb"]) and a1[k]["open"] == (not p["filled"]))]
    need(not r4, f"arm 1 dump differs from its artists for {r4[:10]}")
    print(f"arm 1 dump against arm 1's artists: {len(dumpv) - len(r4)}/{len(dumpv)} equal")
    # printed failure counts: the receipt's ucb < cutoff over the 153 drawn functionals
    texts1 = drawn_texts("arm1", f"{STEM}.pdf")
    for l in ("68", "95"):
        n = int(np.sum(np.array(g[f"ucb{l}"])[order] < THR[l]))
        want = f"{n}/153 failures"
        hits = [tx for tx in texts1 if want in tx]
        need(dump["failure_counts"][l] == n and len(hits) == 1, f"{l}%: printed count {dump['printed_counts'][l]} "
                                                                f"vs receipt {n}; drawn texts holding it {hits}")
        print(f"printed failure count ({l}%): receipt {n}/153; drawn: {hits}")
    if BASE == "D":
        bad_o = []
        for l in ("68", "95"):
            for fam in ("proj", "joint"):
                pts = sorted((p for p in dump["levels"][l] if p["panel"] == fam), key=lambda p: p["x"])
                u = [g[f"ucb{l}"][names.index(p["name"])] for p in pts]
                if any(b < a_ for a_, b in zip(u, u[1:])) or [p["rank"] for p in pts] != list(range(1, len(pts) + 1)):
                    bad_o.append((l, fam))
                print(f"  D order {l}% {fam}: {len(pts)} points, ucb non-decreasing along x (receipt values): "
                      f"{(l, fam) not in bad_o}; first {pts[0]['name']} ucb {u[0]:.4f}, last {pts[-1]['name']} ucb {u[-1]:.4f}")
        need(not bad_o, f"D: not ordered by the upper bound: {bad_o}")
    print(f"plotted functionals: {len({k[1] for k in a1})} of {len(names)}")
    deco_report(dec0, dec1, f"cov {VAR}")

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
    dump = json.loads((RUN / "arm1" / "out" / f"{STEM}_data.json").read_text())
    assert dump["variant"] == VAR, dump["variant"]
    horiz = dump["orientation"] == "horizontal"
    assert horiz == (BASE == "D")
    name_at = {(p["axes"], p["y"] if horiz else p["x"]): p["cell"] for p in dump["points"]}
    assert len(name_at) == 16
    p1, dec1 = points(capture("arm1", f"{STEM}.pdf"), horizontal=horiz)
    a1 = {}
    for ax, pos, v, lo, hi, caps, mfc, mk in p1:
        nm = name_at[(ax, pos)]
        assert nm not in a1
        a1[nm] = {"y": v, "lo": lo, "hi": hi, "caps": caps, "marker": mk, "mfc": mfc}
    compare(a0, a1, f"f16 variant {VAR}" + (" (horizontal: arm 1 x vs arm 0 y)" if horiz else ""))
    r4 = [p["cell"] for p in dump["points"] if not (bits(a1[p["cell"]]["y"]) == bits(p["f"])
                                                    and abs((a1[p["cell"]]["hi"] - a1[p["cell"]]["lo"]) / 2 - p["sigma"]) <= 1e-12 * p["sigma"])]
    need(not r4, f"variant {VAR} dump differs from its artists for {r4}")
    print(f"variant {VAR} dump against its artists: {16 - len(r4)}/16")
    need(len({(a1[n]["marker"], a1[n]["mfc"]) for n in a1}) == 1 and len(a1) == 16, "f16: markers not uniform")
    if BASE == "R":
        texts1 = drawn_texts("arm1", f"{STEM}.pdf")
        for n, lab in dump["value_labels"].items():
            y = a0[n]["y"]
            want = f"{y:.{max(0, 2 - int(np.floor(np.log10(abs(y)))))}f}"
            need(lab == want and texts1[lab] == 1, f"value label {n}: {lab} vs {want} (drawn {texts1[lab]})")
            print(f"value label {n}: printed '{lab}', 3 s.f. of arm 0's y {y!r}: '{want}'; drawn once: {texts1[lab] == 1}")
        want_labels = {"R04": "49.0", "R14": "49.6"} | ({"R07": "3.21"} if VAR == "P" else {})  # P adds R07 (final)
        need(dump["value_labels"] == want_labels, f"value labels are not {want_labels}")
    deco_report(dec0, dec1, f"f16 variant {VAR}")

print(f"CHECK-DATA {FIG} {VAR} :: {'PASS' if not bad else 'FAIL'}")
sys.exit(1 if bad else 0)
