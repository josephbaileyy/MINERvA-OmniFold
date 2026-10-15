#!/usr/bin/env python3
"""Write jobs.tsv, the frozen Stage C production job table (DESIGN §3-§5). Deterministic; no inputs.

  python make_jobs.py            writes jobs.tsv next to this script
  python make_jobs.py --check    exit 1 if jobs.tsv differs from what this script writes

Columns: name item batch qos cpus mem time billing enforced_nh after what
  billing = CPUs on the shared QOS (mem = 1905M x CPUs); enforced_nh = billing x time / 256 (the gate's cap charge).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLS = ["name", "item", "batch", "qos", "cpus", "mem", "time", "billing", "enforced_nh", "after", "what"]

# Walltime caps = 1.5 x a projection from the pilot's measured elapsed times (grant §1; DESIGN §5).
CAP_CV = "00:51:00"    # 64-CPU CV unfold: P1 replica max 2,003 s x 1.5 = 3,005 s -> 00:51:00 (3,060 s)
CAP_U = "00:30:00"     # 128-CPU universe unfold, derived read: P2 derived max 1,166 s x 1.5 = 1,749 s -> 00:30:00
CAP_A = "01:10:00"     # 128-CPU active-file lateral: P3 re-projection 2,800 s x 1.5 = 4,200 s -> 01:10:00

SEEDS = [42, 45, 48, 51, 54]              # five disjoint GBDT seed triplets (s, s+1, s+2)
PANEL_U = ["NormDISCC:0", "Flux:23", "MaRES:0", "MaCCQE:0", "2p2h:0", "MinosEfficiency:0", "Muon_Energy_MINOS:0"]
LATERALS = ["BeamAngleX_0", "BeamAngleX_1", "BeamAngleY_0", "BeamAngleY_1", "MuonResolution_0", "MuonResolution_1",
            "Muon_Energy_MINERvA_0", "Muon_Energy_MINERvA_1", "Muon_Energy_MINOS_0", "Muon_Energy_MINOS_1"]


def hours(t):
    h, m, s = (int(x) for x in t.split(":"))
    return h + m / 60 + s / 3600


def row(name, item, batch, cpus, time, after, what):
    return {"name": name, "item": item, "batch": batch, "qos": "shared", "cpus": str(cpus),
            "mem": f"{1905 * cpus}M", "time": time, "billing": str(cpus),
            "enforced_nh": f"{cpus * hours(time) / 256:.4f}", "after": after, "what": what}


def utag(u):
    return u.replace(":", "")


def rows():
    out = []
    # G0: controls, first and alone (grant §3 "order").
    out.append(row("2dc_P_C0_unit", "C0", "G0", 64, CAP_CV, "-",
                   "b==1 control: driver_p1 --bootstrap-streams three --unit-factors --bootstrap-seed 1 --seed 42, "
                   "CV omnifile; vs XR-L0 at 1e-8"))
    out.append(row("2dc_P_C0_cv", "C0", "G0", 64, CAP_CV, "-",
                   "production driver CV, --seed 42, default read; vs XR-L0 at 1e-8; the seed-42 CV of the S4(ii) panel"))
    # G1: S3, all 10 laterals from the active files.
    for u in LATERALS:
        out.append(row(f"2dc_P_S3_{u.replace('_', '')}", "S3", "G1", 128, CAP_A, "C0_PASS",
                       f"active file {u} (CFS, sha-checked in job), production driver, --seed 42, no --universe, "
                       "--branch-select all"))
    # G2: S4(ii), 7 universe settings x 5 seeds, plus the CV at the 4 non-42 seeds.
    for u in PANEL_U:
        for s in SEEDS:
            out.append(row(f"2dc_P_S4U_{utag(u)}_s{s}", "S4ii", "G2", 128, CAP_U, "C0_PASS",
                           f"universe {u}, production driver, universe omnifile, --seed {s}, --branch-select derived"))
    for s in SEEDS[1:]:
        out.append(row(f"2dc_P_S4CV_s{s}", "S4ii", "G2", 64, CAP_CV, "C0_PASS",
                       f"production driver CV, --seed {s}, default read (per-seed reference for the panel shifts)"))
    # S1: 300 three-stream replicas at --seed 42, bootstrap seeds 1..300, in 6 batches of 50.
    for k in range(6):
        for n in range(50 * k + 1, 50 * k + 51):
            out.append(row(f"2dc_P_S1_{n:03d}", "S1", f"S1{'abcdef'[k]}", 64, CAP_CV, "C0_PASS",
                           f"driver_p1 --bootstrap-streams three --bootstrap-seed {n} --seed 42, CV omnifile"))
    # S2: 100 bkg-only replicas at --seed 42, bootstrap seeds 1..100, in 2 batches of 50.
    for k in range(2):
        for n in range(50 * k + 1, 50 * k + 51):
            out.append(row(f"2dc_P_S2_{n:03d}", "S2", f"S2{'ab'[k]}", 64, CAP_CV, "C0_PASS",
                           f"driver_p1 --bootstrap-streams bkg --bootstrap-seed {n} --seed 42, CV omnifile"))
    # S4(i): bootstrap seeds 1..20 (three streams) at the 4 non-42 seed triplets (the seed-42 column is S1_001..020).
    for k, pair in enumerate([(45, 48), (51, 54)]):
        for s in pair:
            for n in range(1, 21):
                out.append(row(f"2dc_P_S4B_s{s}_{n:02d}", "S4i", f"S4{'ab'[k]}", 64, CAP_CV, "C0_PASS",
                               f"driver_p1 --bootstrap-streams three --bootstrap-seed {n} --seed {s}, CV omnifile"))
    return out


def text():
    lines = ["\t".join(COLS)] + ["\t".join(r[c] for c in COLS) for r in rows()]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    p = HERE / "jobs.tsv"
    if "--check" in sys.argv:
        ok = p.is_file() and p.read_text() == text()
        print("jobs.tsv", "OK" if ok else "STALE")
        sys.exit(0 if ok else 1)
    p.write_text(text())
    r = rows()
    print(f"wrote {p} ({len(r)} jobs, enforced total {sum(float(x['enforced_nh']) for x in r):.4f} node-h)")
