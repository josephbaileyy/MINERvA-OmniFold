import subprocess, sys, shutil
from pathlib import Path
SP = Path(sys.argv[1]); A = SP / "mut/nd-unfolding/s2r/s2r_arm.py"; R = SP / "mut/nd-unfolding/s2r/s2r_rule.py"; SP_ = SP / "mut/nd-unfolding/s2r/s2r_probe.py"
orig = {A: A.read_text(), R: R.read_text(), SP_: SP_.read_text()}
M = [
 (A, "        w[:self.n] = ref * self.w_truth\n", "        w[:self.n] = self.w_truth\n", "fit ref dropped"),
 (A, "        q = self._s2r_ref * reweight_like_loop(inner)\n", "        q = reweight_like_loop(inner)\n", "output not times ref"),
 (A, "        if not free.all():", "        if False:", "saturation STOP off"),
 (A, "        if not np.array_equal(self._s2r_ref, self.w_push):", "        if False:", "ref check off"),
 (A, "        ref = np.array(self.w_push, dtype=float, copy=True)", "        ref = np.ones(self.n)", "ref = 1 always"),
 (R, "        clears = bool(float(a) <= float(b) - BAR)", "        clears = bool(float(a) < float(b) - BAR)", "bar strict"),
 (R, "    ok = not bool(nominal_flagged)", "    ok = True", "nominal ignored"),
 (A, 'GRADE_K = 5', 'GRADE_K = 20', "grade at k20"),
 (SP_, "        if Path(os.path.realpath(out)) != want:", "        if False:", "out root pin off"),
 (SP_, "        with install(arm, truth, rho, runs=runs), esp.pvl_truth():", "        with install(arm, truth, rho), esp.pvl_truth():", "runs not passed"),
 (A, "        if k == 1 and not np.all(self._s2r_ref == 1.0):", "        if False:", "nu0 check off"),
]
for f, old, new, name in M:
    s = orig[f]; assert s.count(old) == 1, name
    f.write_text(s.replace(old, new))
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/s2r/test_s2r.py"], cwd=SP / "mut", capture_output=True, text=True)
    print(f"{name}: {'KILLED' if p.returncode else 'SURVIVED'}")
    f.write_text(orig[f])
