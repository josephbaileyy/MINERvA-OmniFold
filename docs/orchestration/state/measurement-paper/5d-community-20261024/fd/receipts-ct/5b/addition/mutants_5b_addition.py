#!/usr/bin/env python3
"""Mutation run for the 5B block's addition (FD-CT-5B-ADDITION-DECLARATION.md section 4): one textual change at a time
to nd-unfolding/fd_cpl_addition.py or to one of the three tools it parametrizes, applied in place; the addition's
tests and the mutated tool's own suite run against it, and the file is restored (its sha256 checked after every mutant
and at the end). A mutant is killed if the run fails; one whose text is not found exactly once counts as a failure of
this receipt. The mutants cover each control's comparison and operand, the block's arithmetic, the chain's pin
passing, and each parametrized tool's default and variant paths.

    python3 -I -B mutants_5b_addition.py <repo>        (--dry checks only that every mutant applies once)
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
ND = REPO / "nd-unfolding"
SUITES = {"fd_cpl_addition.py": ["test_fd_cpl_addition"],
          "fd_deposit_candidate.py": ["test_fd_cpl_addition", "test_fd_deposit_candidate"],
          "fd_g_figures.py": ["test_fd_cpl_addition", "test_fd_g_figures"],
          "fd_flux_boot.py": ["test_fd_cpl_addition", "test_fd_flux_boot"]}
C, DEP, FIG, FB = "fd_cpl_addition.py", "fd_deposit_candidate.py", "fd_g_figures.py", "fd_flux_boot.py"
MUTANTS = [
    # control A, L: the audit and the labels
    (C, "A: stop unchecked", 'au["stop_condition"]["stop"] is False', "True"),
    (C, "A: audit's 5B readout unchecked", 'ins["readout_5b"] == PINS["periods"]', "True"),
    (C, "L: context numbers unchecked", "f\"{k}: every number it quotes is the audit readout's, in order "
                                        "({', '.join(nums)})\", not missing,",
     "f\"{k}: every number it quotes is the audit readout's, in order ({', '.join(nums)})\", True,"),
    (C, "L: descriptive mark unchecked", '.startswith("descriptive; not a reason for the addition")', '.startswith("")'),
    (C, "L: labels not compared", 'labels.get(k) == LABELS[k] for k in ("block", "decision",',
     'True for k in ("block", "decision",'),
    # B1, B2: the block
    (C, "B1: rank 3 allowed", "and rank == 2,", "and rank >= 2,"),
    (C, "B1: sigma unchecked", 'per["C_PL5D"]["sigma_rel"]) <= TOL)', 'per["C_PL5D"]["sigma_rel"]) <= 1.0)'),
    (C, "B1: trace share loose", '<= 1e-10 * per["C_PL5D"]["trace_share"]', '<= 1e-3 * per["C_PL5D"]["trace_share"]'),
    (C, "B1: symmetry unchecked", 'report("B1", "P is symmetric", float(np.abs(P - P.T).max()) <= TOL',
     'report("B1", "P is symmetric", float(np.abs(P - P.T).max()) <= 1.0'),
    (C, "block: P not scaled by f f^T", "    Cpl = ff * P\n", "    Cpl = P * ff.mean()\n"),
    (C, "block: X without C_resp", '    X = cr["C_resp"] + Cpl\n', "    X = Cpl\n"),
    (C, "npz: float32", 'dtype="<f8"', 'dtype="<f4"'),
    # K: the product
    (C, "K1: Stage G's name unchecked", 'and xb["name"] == NAME and xb["key"] == XKEY', 'and xb["key"] == XKEY'),
    (C, "K2: C_resp unchecked", 'and np.array_equal(blk["C_resp"], mats["C_resp"]))', ")"),
    (C, "K2: sum loose", "float(np.abs(rep - (mats[WITHOUT] + Cpl)).max()) <= TOL * scale)",
     "float(np.abs(rep - (mats[WITHOUT] + Cpl)).max()) <= 1e-6 * scale)"),
    (C, "K3: Stage G sigma unchecked", 'F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= TOL',
     'F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= 1.0'),
    (C, "product: reported is the without", "WITHOUT: mats[WITHOUT], REPORTED: rep}",
     "WITHOUT: mats[WITHOUT], REPORTED: mats[WITHOUT]}"),
    (C, "product: runs without the chain's pins", '    if pins is None:\n        raise Stop("K0", "product runs',
     '    if False:\n        raise Stop("K0", "product runs'),
    (C, "deposit variant: the without key", "    return DC.Variant(key=REPORTED,", "    return DC.Variant(key=WITHOUT,"),
    (C, "deposit variant: no decision label", '**{k: LABELS[k] for k in ("block", "decision", "context_dr_pair", '
                                              '"context_5a_5b")}}\n    return DC.Variant',
     '**{k: LABELS[k] for k in ("block", "context_dr_pair", "context_5a_5b")}}\n    return DC.Variant'),
    # R: the comparisons
    (C, "R: tolerance 1e-6", "def same_number(x, y, tol: float = TOL)", "def same_number(x, y, tol: float = 1e-6)"),
    (C, "R: structure ignored",
     '    bad += [f"structure {p}" for p in sorted(set(so) | set(sn)) if so.get(p) != sn.get(p)]', "    bad += []"),
    (C, "R: bool equals int", "        return x is y or (x == y and type(x) is type(y))", "        return x == y"),
    (C, "R: readouts unchecked", "c.check(f\"R {k}: every number and the structure are the committed readout's\", "
                                 "not bad, bad[:20])",
     "c.check(f\"R {k}: every number and the structure are the committed readout's\", True, bad[:20])"),
    (C, "R: data product CSVs unchecked", "(dpd / n).read_bytes() == (cdp / n).read_bytes() for n in csvs)",
     "True for n in csvs)"),
    (C, "R: deposit JSON unchecked", "else DC.without_code(a_) == DC.without_code(b_)", "else True"),
    (C, "R: figure PDF unchecked", 'not bad and (fig / f"{n}.pdf").read_bytes() == (cfig / f"{n}.pdf").read_bytes(),',
     "not bad,"),
    (C, "R: sidecar excludes the PDF digest", 'FIG_EXCLUDE = ("/argv", "/code", "/versions")',
     'FIG_EXCLUDE = ("/argv", "/code", "/versions", "/pdf_sha256")'),
    # C, S: the chain
    (C, "chain: pins not passed", "pins = json.load(open(pins_file))\n", "pins = None\n"),
    (C, "chain: sys.argv not the tool's", "sys.argv = [T.__file__, *argv]\n", ""),
    (C, "chain: exit code ignored", "        if rc != 0 or any(v is None for v in rec[\"outputs\"].values()):",
     "        if any(v is None for v in rec[\"outputs\"].values()):"),
    (C, "chain: upstream pins not chained",
     "            pins = {**pins_of(*STEP_PINS[k]), **{f: H[u] for f, u in UPSTREAM[k].items()}}",
     "            pins = dict(pins_of(*STEP_PINS[k]))"),
    (C, "chain: F1 on the committed F0b", '            up["f0b_sha256"] = H[k]\n', '            up["f0b_sha256"] = COMMITTED["f0b"][1]\n'),
    (C, "C: upstream unchecked", "and all(ins.get(f) == H[u] for f, u in UPSTREAM.get(k, {}).items()),", ","),
    (C, "C: block sha unchecked", "bool(named) and all(v == h for v in named)", "bool(named)"),
    (C, "S: Stage G sigma unchecked",
     'F.worst(np.array(q["sigma_total_over_f"]), rep[[CELLS.index(x) for x in q["cells"]]]) <= TOL',
     'F.worst(np.array(q["sigma_total_over_f"]), rep[[CELLS.index(x) for x in q["cells"]]]) <= 1.0'),
    (C, "chain: the deposit without the variant",
     '[dep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=dpins, variant="with-cpl")',
     '[dep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=dpins)'),
    (C, "chain: figures under the default name", '*(["--reported-block-name", NAME] if arm == "with" else [])', "*[]"),
    (C, "argv: F0b drops its extra block", "        return [*p.f0(), *xb0, \"--out-json\", str(out), \"--out-npz\", "
                                           "str(out.parent.parent / \"fd_f0b_experiments.npz\")]",
     "        return [*p.f0(), \"--out-json\", str(out), \"--out-npz\", str(out.parent.parent / \"fd_f0b_experiments.npz\")]"),
    # added after the review: each control's firing direction
    (C, "A: a named clause allowed", '           and au["stop_condition"]["which"] == [])', ")"),
    (C, "A: 5B readout's S1 unchecked", 'per["inputs_sha256"]["s1_npz"] == PINS["s1_npz"]', "True"),
    (C, "B2: cresp's total unchecked", "and float(np.abs(rep - (cr[\"C_total_resp\"] + Cpl)).max()) <= TOL * scale)", ")"),
    (C, "K0: overwrite allowed", 'report("K0", "no output exists (no overwrite)", not any((a.out_dir / n).exists() for n in names))',
     'report("K0", "no output exists (no overwrite)", True)'),
    (C, "K4: block rank unchecked", "and int(np.sum(lam > TOL * lam.max())) == 2)", ")"),
    (C, "K5: without sigma unchecked", "rel[WITHOUT], dp[\"relative_sigma\"][WITHOUT]) <= TOL)", "rel[WITHOUT], rel[WITHOUT]) <= TOL)"),
    (C, "K6: readback unchecked", "        report(\"K6\", f\"{k}: the CSV and the JSON read back bit for bit\", np.array_equal(back, p[\"matrices\"][k])",
     "        report(\"K6\", f\"{k}: the CSV and the JSON read back bit for bit\", True"),
    (C, "T: the with side's name unchecked", 'and p["with"]["matrix"] == want,', ","),
    (C, "T: the order unchecked", '[p["name"] for p in old["g"]["predictions"]] == [p["name"] for p in new["g"]["predictions"]])', "True)"),
    (C, "T: without pins unchecked", 'pins[f"{k}_without"] == COMMITTED[k][1])', "True)"),
    (C, "L: order ignored", "                at_ = i + len(n.lstrip(\"+\"))\n", ""),
    (FIG, "figures: F0b key report removed", '    report("K2", f"F0b records relative_sigma_plus_{name}", f"relative_sigma_plus_{name}" in b)\n', ""),
    # the deposit candidate's variant
    (DEP, "deposit: package reads the default key", '    C = np.array(dp["matrices"][v.key], float)\n    rho',
     '    C = np.array(dp["matrices"]["C_total_plus_C_resp"], float)\n    rho'),
    (DEP, "deposit: P0 on the default pins", 'sha256(path) == v.pins[key], f"{sha256(path)} != {v.pins[key]}")',
     'sha256(path) == PINS[key], f"{sha256(path)} != {PINS[key]}")'),
    (DEP, "deposit: run ignores the variant", "    v = DEFAULT if variant is None else variant\n", "    v = DEFAULT\n"),
    (DEP, "deposit: labels from the default", '    js = {"schema": "fd-deposit-candidate/1", "labels": v.labels,',
     '    js = {"schema": "fd-deposit-candidate/1", "labels": LABELS,'),
    (DEP, "deposit: default key changed", 'DEFAULT = Variant(key="C_total_plus_C_resp"', 'DEFAULT = Variant(key="C_total"'),
    # the figures' block name
    (FIG, "figures: K1 name ignored", '           xb["name"] == name and xb["role"] == "adopted"',
     '           xb["role"] == "adopted"'),
    (FIG, "figures: default name changed", 'BLOCK = "C_resp"  ', 'BLOCK = "C_resp "  '),
    (FIG, "figures: K5 on the default name", 's["reported_matrix"] == reported(name)', 's["reported_matrix"] == REPORTED'),
    (FIG, "figures: the name not passed", '    return {} if name == BLOCK else {"name": name}', "    return {}"),
    (FIG, "figures: option always recorded", '**{f"reported_block_{k}": v for k, v in named(a).items()}}',
     '"reported_block_name": vars(a).get("reported_block_name")}'),
    # the flux bootstrap's labels
    (FB, "flux boot: labels not per run", '"labels": labels(x.comps[0][1][0]),', '"labels": LABELS,'),
    (FB, "flux boot: default units changed", 'LABELS["units"] = UNITS.format(reported="C_total + C_resp")',
     'LABELS["units"] = UNITS.format(reported="C_total")'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


files = {f: ND / f for f in SUITES}
orig = {f: p.read_text() for f, p in files.items()}
digest = {f: sha(p) for f, p in files.items()}
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
bad = [(f, n, orig[f].count(o)) for f, n, o, _ in MUTANTS if orig[f].count(o) != 1]
if "--dry" in sys.argv:
    print(f"{len(MUTANTS)} mutants; not applicable exactly once: {bad}")
    raise SystemExit(1 if bad else 0)
killed = survived = unapplied = 0
print("files " + ", ".join(f"{f} {digest[f][:16]}" for f in files) + f"  mutants {len(MUTANTS)}", flush=True)
try:
    for f, name, old, new in MUTANTS:
        if orig[f].count(old) != 1:
            unapplied += 1
            print(f"NOT APPLIED  {name}: found {orig[f].count(old)} times", flush=True)
            continue
        files[f].write_text(orig[f].replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", *SUITES[f]], cwd=ND / "tests", env=env,
                           capture_output=True, text=True, timeout=3600)
        files[f].write_text(orig[f])
        if sha(files[f]) != digest[f]:
            raise SystemExit("the file was not restored")
        ok = r.returncode != 0
        killed += ok
        survived += not ok
        tail = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAILED", "OK", "Ran"))]
        print(f"{'KILLED  ' if ok else 'SURVIVED'}  {f}: {name}  ({'; '.join(tail)})", flush=True)
finally:
    for f in files:
        files[f].write_text(orig[f])
restored = all(sha(files[f]) == digest[f] for f in files)
print(f"killed {killed} of {len(MUTANTS)}; survived {survived}; not applied {unapplied}; files restored {restored}")
raise SystemExit(0 if survived == 0 and unapplied == 0 and restored else 1)
