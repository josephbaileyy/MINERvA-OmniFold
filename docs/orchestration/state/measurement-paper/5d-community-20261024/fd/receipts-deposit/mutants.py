import subprocess, sys, shutil, tempfile, os
from pathlib import Path
W = Path(sys.argv[1]); SRC = W / "nd-unfolding/fd_deposit_candidate.py"; orig = SRC.read_text()
M = [
 ("P5 tolerance ignored", "rel <= CHI2_TOL and out[key]", "True and out[key]"),
 ("P2 covariance compare dropped", "np.array_equal(C_csv, C_dp) and", "True and"),
 ("P2 f compare dropped", "np.array_equal(f_csv, f_dp) and", "True and"),
 ("P2 correlation compare dropped", "np.array_equal(rho_csv, rho_dp) and", "True and"),
 ("P1 union check dropped", "boxes_inside(box) == set(d[\"h2_boxes\"])", "True"),
 ("P1 order check dropped", "[r[\"cell\"] for r in rows] == CELLS", "True"),
 ("P4 subset check dropped", "len(gib) == 1 and sub ==", "len(gib) == 1 or sub =="),
 ("GiBUU edge 4.5 -> 60", "GIBUU_PZ_HI = 4.5", "GIBUU_PZ_HI = 60.0"),
 ("P3 symmetry tolerance 1e-12 -> 1", "asym <= 1e-12, f", "asym <= 1.0, f"),
 ("P3 sigma check dropped", "np.array([float(r[\"sigma_cm2_per_nucleon\"]) for r in rows]), sig) and", "sig, sig) and"),
 ("P0 file digest check dropped", "== js[\"files_sha256\"].get(n))", "== js[\"files_sha256\"].get(n) or True)"),
 ("P0 pin check dropped", "sha256(path) == PINS[key], f", "True, f"),
 ("V_g dropped from chi2", "Vg[idx] = r[\"V_g_cm4_per_nucleon2\"]", "pass"),
 ("P6 g compare dropped", "np.array_equal(np.array(r[\"g_cm2_per_nucleon\"]), np.array(p[\"g\"]))", "True"),
 ("P6 V_g compare dropped", "np.array(r[\"V_g_cm4_per_nucleon2\"]), (np.array(p[\"sigma_Vg_over_f\"]) * f_csv[idx]) ** 2))", "1, 1))"),
 ("P6 source compare dropped", "== (spec[r[\"name\"]][\"path\"], spec[r[\"name\"]][\"sha256\"], p[\"label\"]))", "!= None)"),
 ("P6 order compare dropped", "[p[\"name\"] for p in rp]\n           == [p[\"name\"] for p in gr[\"predictions\"]]", "True or [0]\n           == [0]"),
 ("P6 label compare dropped", "ref[\"label\"] == REFERENCE_LABEL and", "True and"),
 ("P6 chi2 compare dropped", "r[\"stage_g\"][k][\"chi2\"] == p[k][\"chi2\"] and", "True and"),
 ("P0 file-exists check dropped", "report(\"P0\", f\"{n} exists\", (pkg / n).is_file())", "pass"),
 ("reference V_g written as sigma", "Vg = (np.array(p[\"sigma_Vg_over_f\"], float) * f[idx]) ** 2", "Vg = np.array(p[\"sigma_Vg_over_f\"], float) * f[idx]"),
 ("build writes sigma squared", "float(f[i]), float(sigma[i])]", "float(f[i]), float(sigma[i] ** 2)]"),
 ("no-overwrite dropped", "\"no package file exists (no overwrite)\", not any(", "\"no package file exists (no overwrite)\", True or any("),
]
killed = 0
try:
    for name, a, b in M:
        assert orig.count(a) == 1, name
        SRC.write_text(orig.replace(a, b))
        with tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"]) as t:
            p = subprocess.run([sys.executable, "-I", "-B", str(W / "nd-unfolding/tests/test_fd_deposit_candidate.py")],
                               cwd=t, capture_output=True, text=True)
        k = p.returncode != 0; killed += k
        print(f"{'KILLED' if k else 'SURVIVED'}  {name}")
finally:
    SRC.write_text(orig)
print(f"{killed}/{len(M)} killed")
