#!/usr/bin/env python3
"""RE-2 part C K1-roll: the purity arm's outputs against their committed originals (RE2-DECLARATION-C.md §4.1).

    python3 -I re2c_k1roll.py --repo REPO --dry <re2c_run.sh purity outdir> --out k1roll.json

Each comparison is one of:
  bytes  the sha256 of a product the original wrote deterministically (np.savez fixes its zip dates; json.dump of
         the same objects), against the digest the records pin;
  json   the same JSON fields, with only the copy's own script digest, its arm record and input paths excluded
         (each exclusion named in the result);
  text   a producer's printout, line for line, without the lines that carry a path or a write message and without
         ROOT's rootmap warnings (stderr, which the run's log captures and the committed stdout did not);
  value  a number against the committed number it must equal exactly.
A ROOT file is never compared by bytes (TFile records its creation time); its content enters through the npz and
the readbacks. Exit 0 only if every comparison passes.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

S = "docs/orchestration/state/2d-closeout"
R42 = "docs/orchestration/receipts/2d-lgbm42-20261011"
PATHLINE = re.compile(r"/pscratch/|/global/|\bwrote\b|opening:|\bsaved\b|^Warning in <TInterpreter::ReadRootmapFile>",
                      re.I)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def load(p):
    p = Path(p)
    return json.loads(gzip.open(p, "rt").read()) if p.suffix == ".gz" else json.loads(p.read_text())


def drop(d, keys):
    """d without the dotted keys `keys` (missing keys are ignored)."""
    d = json.loads(json.dumps(d))
    for k in keys:
        parts, cur = k.split("."), d
        for q in parts[:-1]:
            cur = cur.get(q, {}) if isinstance(cur, dict) else {}
        if isinstance(cur, dict):
            cur.pop(parts[-1], None)
    return d


def diff(a, b, path=""):
    """The first few differing paths between two JSON values."""
    if type(a) is not type(b):
        return [f"{path}: {type(a).__name__} != {type(b).__name__}"]
    if isinstance(a, dict):
        out = [f"{path}.{k}: only on one side" for k in sorted(set(a) ^ set(b))]
        for k in sorted(set(a) & set(b)):
            out += diff(a[k], b[k], f"{path}.{k}")
        return out[:8]
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
        return out[:8]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def text(p):
    return [ln.rstrip() for ln in Path(p).read_text().splitlines() if not PATHLINE.search(ln) and ln.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--dry", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    repo, dry = Path(a.repo), Path(a.dry)
    res = {}

    def rec(name, kind, ok, detail=None, excluded=None):
        res[name] = {"kind": kind, "pass": bool(ok), "detail": detail, **({"excluded": excluded} if excluded else {})}

    # ---- analyze_prod: the six item records
    for item in ("c0", "s3", "s4ii", "s1", "s2", "s4i"):
        mine = load(dry / "results" / f"{item}.json")
        ref = load(repo / S / "stageC/production/evidence/production/results" / f"{item}.json")
        ex = ["analyze_prod_sha256", "arm"]
        d = diff(drop(mine, ex), drop(ref, ex))
        key = {"c0": "C0", "s3": "S3", "s4ii": "S4ii", "s1": "S1", "s2": "S2", "s4i": "S4i"}[item]
        rec(f"analyze_{item}", "json", not d and mine.get(key) == "PASS", d or mine.get(key), ex)

    # ---- bytes of the deterministic products
    for name, path, want in (
            ("rollup_production_cov", "s5/production_cov.npz",
             "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc"),
            ("export_cov_work_cov", "work_cov/work_cov.npz",
             "70c4daf2048875538eb74ee507b1d8741ca4ff80a8a351f0500450151a19ed1d"),
            ("periods_analysis", "periods/analysis.json",
             "05edff61673fed987f487f8c19ad25ec055db8118491815b9c263f3a7c3de72b"),
            ("playlist_npz", "playlist/playlist_term.npz",
             "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476"),
            ("combine_npz", "combination/s5_plus_playlist.npz",
             "8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e"),
            ("build_q_cov2d", "outA/cov2d_Q_205.npz",
             "771e49a5510ff15fa522b73ab49b18329c2a58f092efb12a26aee39949168ced")):
        got = sha256(dry / path)
        rec(name, "bytes", got == want, {"got": got, "want": want})
    for name, path, ref in (("periods_control", "periods/control.json", "control.json"),
                            ("periods_roles", "periods/roles.json", "roles.json"),
                            ("periods_selftest", "periods/selftest.json", "selftest.json")):
        r = repo / S / "period-unfold-20261014/outputs" / ref
        rec(name, "bytes", sha256(dry / path) == sha256(r), {"got": sha256(dry / path), "want": sha256(r)})

    # ---- JSON records
    s5m, s5r = load(dry / "s5/s5.json"), load(repo / S / "stageC/production/evidence/production/results/s5.json")
    d = diff({k: s5m[k] for k in ("numbers", "checks", "S5")}, {k: s5r[k] for k in ("numbers", "checks", "S5")})
    rec("rollup_s5_json", "json", not d, d, ["s5_rollup_sha256", "inputs (the item records' digests)"])
    ex = ["arm"]
    d = diff(drop(load(dry / "work_cov/cov_controls.json"), ex),
             load(repo / S / "playlist-spread-20261014/coverage/outputs/cov_controls.json"))
    rec("export_cov_controls", "json", not d, d, ex)
    for name, mine, ref in (("playlist_json", "playlist/playlist_term.json", "playlist-term/outputs/playlist_term.json"),
                            ("combination_json", "combination/combination.json",
                             "playlist-term/outputs/combination/combination.json")):
        m, r = load(dry / mine), load(repo / S / ref)
        d = diff({k: m[k] for k in ("checks", "report")}, {k: r[k] for k in ("checks", "report")})
        rec(name, "json", not d, d, ["inputs (script paths of the copies)", "npz.path"])
    bm = load(dry / "outA/budget_Q.json")
    br = load(repo / S / "stageF/rebuild/outputs/outA/budget_Q.json.gz")
    ex = ["provenance", "s5_copied.source.path"] + [f"checks.{k}.value" for k in bm.get("checks", {})
                                                    if k.startswith("A0_module_")]
    d = diff(drop(bm, ex), drop(br, ex))
    rec("build_q_budget", "json", not d, d, ex)
    fm, fr = load(dry / "fig67/fig67_projections.json"), load(repo / S / "stageF/rebuild/outputs/fig67/fig67_projections.json")
    strip = lambda o: {k: v for k, v in o.items() if not (isinstance(v, str) and "/" in v)}  # noqa: E731
    d = diff(strip(fm), strip(fr))
    rec("fig67_projections", "json", not d, d, ["string fields holding paths"])
    am = load(dry / "receipts/RECEIPT-agreement-windows.json")
    ar = load(repo / R42 / "RECEIPT-2d-agreement-windows-lgbm42-20261011.json")
    d = diff({k: am[k] for k in ("results", "denominator")}, {k: ar[k] for k in ("results", "denominator")})
    d += diff(am["headline_totals_oi130"]["values"], ar["headline_totals_oi130"]["values"])
    rec("agreement_receipt", "json", not d, d, ["everything but results, denominator, headline_totals_oi130.values"])

    # ---- check_rebuild's steps C and D (CR-02, CR-03), against the committed checks.json's same entries
    cm = load(dry / "checks.json")
    cr = load(repo / S / "stageF/rebuild/outputs/checks.json")
    keys = sorted(k for k in cm if k.startswith(("C_chi2_", "D_fig67_Q_", "D_fig67_projections")))
    d = diff({k: cm[k] for k in keys}, {k: cr.get(k) for k in keys})
    rec("check_rebuild_CR02_CR03", "json", len(keys) == 5 and not d and all(cm[k]["ok"] for k in keys), d or keys)

    # ---- printouts
    for name, mine, ref in (
            ("chi2_Q_std", "chi2/chi2_Q_std.txt", f"{S}/stageF/rebuild/outputs/chi2/chi2_Q_std.txt"),
            ("chi2_Q_lognormal", "chi2/chi2_Q_lognormal.txt", f"{S}/stageF/rebuild/outputs/chi2/chi2_Q_lognormal.txt"),
            ("chi2_Q_substat", "chi2/chi2_Q_substat.txt", f"{S}/stageF/rebuild/outputs/chi2/chi2_Q_substat.txt"),
            ("ours_only_Q", "chi2/ours_only_Q.txt", f"{S}/stageF/rebuild/outputs/chi2/ours_only_Q.txt"),
            ("ours_only_universe", "chi2/ours_only_universe.txt", f"{S}/stageF/rebuild/outputs/chi2/ours_only_universe.txt"),
            ("ours_only_universe_plus_stat", "chi2/ours_only_universe_plus_stat.txt",
             f"{S}/stageF/rebuild/outputs/chi2/ours_only_universe_plus_stat.txt"),
            ("chi2_paperonly", "receipts/chi2_paperonly.txt", f"{R42}/chi2_lgbm42_paperonly.txt"),
            ("tune", "receipts/tune.log", f"{R42}/tune.log"),
            ("model_comp_report", "receipts/figs/model_comp_report.txt", f"{R42}/model_comp_report.txt"),
            ("tension_report", "receipts/figs/tension_report.txt", f"{R42}/tension_report.txt")):
        m, r = text(dry / mine), text(repo / ref)
        bad = [(i, x, y) for i, (x, y) in enumerate(zip(m, r)) if x != y][:5]
        rec(name, "text", len(m) == len(r) and not bad, {"lines": [len(m), len(r)], "first_diffs": bad})

    # ---- values
    nm = load(dry / "partc_numbers.json")
    rn = load(repo / S / "stageF/methods/re1/run2/f/numbers.json")["p3"]["vs_E_U"]
    rx = load(repo / S / "stageF/methods/re1/run2/readouts/report2_extras.json")["marginal_vs_EU_scatter"]["p3"]
    t = nm["threeD_p3_vs_central"]
    pairs = {"total_change_percent": (t["total_change_percent"], rn["total_change_percent"]),
             "median_ratio": (t["median_ratio"], rn["median_ratio"]), "sd_ratio": (t["sd_ratio"], rx["sd_ratio"])}
    rec("numbers_threeD_vs_re1", "value", all(x == y for x, y in pairs.values()), pairs)
    lm = nm["learner_vs_E_C_pct"]
    rec("numbers_learner_vs_lgbm_metrics", "value",
        f"{lm['median_abs']:.3f}" == "0.983" and f"{lm['max_abs']:.2f}" == "12.18", lm)
    vt = load(dry / "values_table.json")["summary"]
    rec("values_controls", "value", vt["unexpected"] == 0, vt)

    n_fail = sum(not r["pass"] for r in res.values())
    out = {"schema": "re2c-k1roll/1", "n": len(res), "n_fail": n_fail, "verdict": "PASS" if n_fail == 0 else "FAIL",
           "results": res}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"verdict": out["verdict"], "n": len(res), "failed": [k for k, r in res.items() if not r["pass"]]}))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
