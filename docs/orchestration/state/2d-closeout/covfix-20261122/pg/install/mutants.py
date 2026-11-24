"""Hand mutants of pg-install-g2111a.py (B2) and pg-node-launch.py, under the director's kill rule (../mutrun.py).

Run: python3 -B mutants.py > mutants.log   (from this directory; every mutant runs in a throwaway copy)
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("mutrun", HERE.parent / "mutrun.py")
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)
D = "docs/orchestration/state/2d-closeout/covfix-20261122/pg/install"
IN, NL = f"{D}/pg-install-g2111a.py", f"{D}/pg-node-launch.py"
M = [(f, old, new, what, "install") for f, old, new, what in [
    (IN, '        if not rec["identity"]["pass"]:', '        if False:', "identity not enforced"),
    (IN, '        if not dbconfig_sha:', '        if False:', "an unfilled dbconfig pin"),
    (IN, '        if os.path.lexists(root):', '        if False:', "an existing product directory"),
    (IN, '        if not (parent + "/").startswith(scratch):', '        if False:', "a product directory off scratch"),
    (IN, '        if rec["tarball_sha256"] != tarball_sha:', '        if False:', "the download's pin"),
    (IN, '            os.unlink(tarball)\n            raise Stop("the download', '            raise Stop("the download',
     "a bad download kept"),
    (IN, '        if rec["scan_problems"]:', '        if False:', "a member mismatch extracted"),
    (IN, '                if h.hexdigest() != want["sha256"]:', '                if False:', "member bytes in the scan"),
    (IN, '            elif kind == "symlink" and m.linkname != want["target"]:', '            elif False:',
     "link targets in the scan"),
    (IN, '    probs += [f"missing: {n}" for n in sorted(set(members) - set(seen))]\n    return probs\n\n\ndef extract',
     '    return probs\n\n\ndef extract', "a missing member in the scan"),
    (IN, '            if want is None or n in seen:', '            if n in seen:', "an unpinned member in the scan"),
    (IN, '        if rec["dbconfig_sha256"] != dbconfig_sha:', '        if False:', "dbconfig's pin"),
    (IN, '        make_readonly(os.path.join(root, "genie_xsec"))\n', '', "the product left writable"),
    (IN, '        if readonly and kind != "symlink" and st.st_mode & 0o222:', '        if False:', "writable members accepted"),
    (IN, '    probs += [f"extra: {n}" for n in sorted(set(seen) - set(members))]\n', '', "extra members accepted"),
    (IN, '        elif kind == "file" and sha_path(p) != m["sha256"]:', '        elif False:', "installed bytes"),
    (IN, '        if rec["tree_problems"]:', '        if False:', "a bad installed tree"),
    (IN, '        os.unlink(tarball)\n        os.rmdir(os.path.join(root, "dl"))\n', '', "the download left in the product"),
    (NL, '    if got != want:', '    if False:', "the script's sha"),
    (NL, 'os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW', 'os.O_RDWR | os.O_CREAT | os.O_TRUNC', "output not reserved"),
    (NL, '    if not isinstance(rec, dict) or rec.get("schema") != schema:', '    if not isinstance(rec, dict):',
     "another script's schema"),
    (NL, '    if v not in RC_FOR or RC_FOR[v] != rc:', '    if v not in RC_FOR:', "verdict/rc mismatch"),
    (NL, '    if not isinstance(stops, list) or (v == "GO") != (not stops):', '    if not isinstance(stops, list):',
     "a GO with stops"),
    (NL, '    if schema is None:', '    if False:', "an unreviewed script"),
    (NL, '    return p.returncode if ok else 4', '    return p.returncode', "invalid receipt exit"),
    (NL, 'SSH_OPTS = ["-F", "/dev/null", ', 'SSH_OPTS = [', "user ssh config used"),
]]

if __name__ == "__main__":
    raise SystemExit(R.main(M))
