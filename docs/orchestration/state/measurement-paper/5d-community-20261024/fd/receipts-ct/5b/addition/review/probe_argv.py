"""Compare each chain step's argv (flags AND values) with its bound run's script, after mapping the bound run's deploy
roots to one deploy /D and $P to /P. Outputs (--out-*, --figures-dir) are reported, not compared."""
import re, sys
from pathlib import Path
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "nd-unfolding"))
import fd_cpl_addition as A
FDP = WT / A.FD
OVR = {"P": "/P", "D": "/D", "DG": "/D", "T": f"/D/{A.FD}", "TG": f"/D/{A.FD}", "HOME": "/HOME"}

def expand(s, env):
    for _ in range(10):
        s2 = re.sub(r"\$\{?(\w+)\}?", lambda m: env.get(m.group(1), m.group(0)), s)
        if s2 == s: break
        s = s2
    return s

def script_argv(rel, tool):
    text = (FDP / rel).read_text().replace("\\\n", " ")
    env = {}
    for line in text.splitlines():
        for m in re.finditer(r'(?:^|;\s*)([A-Z][A-Z0-9]*)=("(?:[^"]*)"|\S+)', line):
            env[m.group(1)] = m.group(2).strip('"')
    env = {k: v for k, v in env.items()}
    env.update(OVR)
    m = re.search(rf"{re.escape(tool)}\.py(.*?)(?:>|$)", text, re.S | re.M)
    body = expand(m.group(1), env)
    toks = body.split()
    return toks

def pairs(toks):
    out, i = {}, 0
    while i < len(toks):
        t = toks[i]
        if t.startswith("--"):
            vals = []
            j = i + 1
            while j < len(toks) and not toks[j].startswith("--"):
                vals.append(toks[j]); j += 1
            out.setdefault(t, []).append(" ".join(vals)); i = j
        else:
            out.setdefault("<pos>", []).append(t); i += 1
    return out

p = A.Paths(Path("/D"), Path("/P"), Path("/BA"))
cm = {k: Path("/D") / rel for k, (rel, _) in A.COMMITTED.items()}
up = {**cm, "f0b_sha256": A.COMMITTED["f0b"][1]}
xb = A.extra(p.cresp, A.PINS["cresp_npz"], "C_resp", "C_resp"); xb0 = A.extra(p.cresp, A.PINS["cresp_npz"], "C_resp", "C_resp", role=False)
SCRIPTS = {"f0b": ("fd/receipts-f0b/step3.sh", "fd_f0_regrade"), "f1": ("fd/receipts-f1/run/s12.sh", "fd_f0_regrade"),
           "g": ("fd/receipts-g/g2.sh", "fd_g_compare"), "g_diag": ("fd/receipts-g-diag/d2.sh", "fd_g_diag"),
           "g_followup": ("fd/receipts-g-followup/f2.sh", "fd_g_followup"), "g_sens2": ("fd/receipts-g-sens2/s2.sh", "fd_g_followup"),
           "flux_boot": ("fd/receipts-flux-boot/run/amended/logs/s2-body.sh", "fd_flux_boot"),
           "data_product": ("fd/receipts-g-figures/run/s2.sh", "fd_data_product"),
           "figures": ("fd/receipts-g-figures/run/s3.sh", "fd_g_figures"), "figures_check": ("fd/receipts-g-figures/run/s4.sh", "fd_g_figures_check")}
OUTF = {"--out-json", "--out-npz", "--out-dir", "--figures-dir"}
for step, (rel, tool) in SCRIPTS.items():
    want = pairs(script_argv(rel, tool))
    got = pairs([str(x) for x in A.step_argv(p, step, xb, xb0, up, Path("/BA/without/readout/x.json") if step not in ("data_product", "figures", "figures_check") else Path("/BA/without/x"), "without")])
    diffs = []
    for f in sorted(set(want) | set(got)):
        if f in OUTF: continue
        if want.get(f) != got.get(f):
            diffs.append(f"{f}: bound {want.get(f)} chain {got.get(f)}")
    print(f"== {step}: {'values equal' if not diffs else str(len(diffs)) + ' differ'}")
    for d in diffs: print("   ", d)
