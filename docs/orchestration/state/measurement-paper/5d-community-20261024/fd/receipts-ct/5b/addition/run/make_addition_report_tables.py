"""Print FD-CT-5B-ADDITION-REPORT.md's tables from the committed chain receipt and products, so no digest or number is
transcribed by hand.

Usage: python3 -I -B make_addition_report_tables.py <repo>
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
RUN = FD / "receipts-ct/5b/addition/run"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    return str(p.relative_to(FD.parent))


steps = json.loads((RUN / "chain.json").read_text())["steps"]
print(f"chain.json sha256 {sha(RUN / 'chain.json')}; {len(steps)} records, "
      f"{sum(1 for s in steps if s.get('check'))} checks, all ok: {all(s.get('ok', True) for s in steps)}")

print("\n## T1 steps\n")
print("| arm | step | tool | rc | wall (s) | start (UTC) | pins passed in-process |")
print("|---|---|---|---:|---:|---|---|")
for s in steps:
    if s.get("check"):
        continue
    pins = "—" if s["pins"] is None else ", ".join(
        f"{k} `{v[:8]}`" for k, v in s["pins"].items() if k.endswith(("readout", "product", "npz", "json"))
        or k.endswith(("_with", "_without"))) or "defaults"
    print(f"| {s['arm']} | {s['step']} | `{s['tool']}` | {s['rc']} | {s['wall_s']} | {s['start_utc']} | "
          f"{pins}{' (variant ' + s['variant'] + ')' if s.get('variant') else ''} |")

print("\n## T2 checks (control R on the without arm; C and S on the with arm)\n")
for s in steps:
    if s.get("check"):
        print(f"- {'PASS' if s['ok'] else 'FAIL'} {s['step']}")

print("\n## T3 every product, before (committed, unchanged) and after (with the block, beside it)\n")
print("| product | before | sha256 | after | sha256 |")
print("|---|---|---|---|---|")
pairs = [(f"readout {n}", FD / "readout" / n, FD / "with-cpl/readout" / n) for n in
         ("fd_f0b_readout.json", "fd_f1_readout.json", "fd_g_readout.json", "fd_g_diag_readout.json",
          "fd_g_followup_readout.json", "fd_g_sens2_readout.json", "fd_flux_boot_readout.json")]
dp, dpw = FD / "data-product", FD / "with-cpl/data-product"
pairs.append(("data product (JSON)", dp / "fd_data_product.json", dpw / "fd_data_product_cpl.json"))
for m in ("C_e", "C_model_abs", "C_resp", "C_total_plus_C_resp"):
    pairs.append((f"data product {m}", dp / f"fd_data_product_{m}.csv", dpw / f"fd_data_product_cpl_{m}.csv"))
pairs.append(("data product cells", dp / "fd_data_product_cells.csv", dpw / "fd_data_product_cpl_cells.csv"))
pairs.append(("data product reported matrix", dp / "fd_data_product_C_total_plus_C_resp.csv",
              dpw / "fd_data_product_cpl_C_total_plus_C_resp_plus_C_PL5D.csv"))
pairs.append(("data product its correlation", dp / "fd_data_product_corr_C_total_plus_C_resp.csv",
              dpw / "fd_data_product_cpl_corr_C_total_plus_C_resp_plus_C_PL5D.csv"))
pairs.append(("data product C_PL5D", None, dpw / "fd_data_product_cpl_C_PL5D.csv"))
for n in ("cells.csv", "covariance.csv", "correlation.csv", "deposit.json", "predictions-reference.json"):
    pairs.append((f"deposit {n}", FD / "deposit-candidate" / n, FD / "with-cpl/deposit-candidate" / n))
for n in ("fd_g_fig_ratio", "fd_g_fig_modes", "fd_g_fig_sens"):
    for e in (".pdf", ".json"):
        pairs.append((f"figure {n}{e}", FD / "figures" / f"{n}{e}", FD / "with-cpl/figures" / f"{n}{e}"))
for n in ("cpl_block.npz", "cpl_block.json"):
    pairs.append((f"block {n}", None, FD / "with-cpl/block" / n))
for n in ("fd_cpl_table.json", "fd_cpl_table.md"):
    pairs.append((f"table {n}", None, FD / "with-cpl/table" / n))
for name, b, a in pairs:
    bb = ("—", "—") if b is None else (f"`{rel(b)}`", f"`{sha(b)[:16]}…`")
    print(f"| {name} | {bb[0]} | {bb[1]} | `{rel(a)}` | `{sha(a)[:16]}…` |")

blk = json.loads((FD / "with-cpl/block/cpl_block.json").read_text())
print(f"\nblock: npz sha256 {blk['npz']['sha256']}; rank {blk['rank']}; trace share of M + P "
      f"{blk['trace_share_of_M_plus_P']:.6f}; controls {blk['controls_passed']}")
tab = json.loads((FD / "with-cpl/table/fd_cpl_table.json").read_text())
print("table leaf counts: " + ", ".join(f"{k} {v}" for k, v in tab["leaf_counts"].items()))
print("unpaired committed leaves: " + "; ".join(f"{k}: {v}" for k, v in tab["unpaired_without_leaves"].items() if v))
for r in ("f0b", "f1"):
    old = json.loads((FD / "readout" / f"fd_{r}_readout.json").read_text())["triggers"]["listed"]
    new = json.loads((FD / "with-cpl/readout" / f"fd_{r}_readout.json").read_text())["triggers"]["listed"]
    print(f"{r} triggers.listed without: {old}")
    print(f"{r} triggers.listed with: {new}")
g = {k: json.loads((FD / p).read_text())["predictions"] for k, p in
     (("without", "readout/fd_g_readout.json"), ("with", "with-cpl/readout/fd_g_readout.json"))}
falls = [(po["name"], k, 1 - pn[k]["chi2"] / po[k]["chi2"]) for po, pn in zip(g["without"], g["with"])
         for k in ("total", "shape_only")]
top = max(falls, key=lambda x: x[2])
print(f"largest fractional chi2 fall: {top[0]} {top[1]} {top[2]:.4f} (the audit's ceiling 0.7261)")
