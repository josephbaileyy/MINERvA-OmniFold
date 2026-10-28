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
 ("V_g dropped from chi2", "Vg[idx] = (np.array(p[\"sigma_Vg_over_f\"]) * f_csv[idx]) ** 2", "pass"),
 ("build writes sigma squared", "float(f[i]), float(sigma[i])]", "float(f[i]), float(sigma[i] ** 2)]"),
 ("no-overwrite dropped", "not any((a.out_dir / n).exists() for n in FILES))", "True)"),
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
