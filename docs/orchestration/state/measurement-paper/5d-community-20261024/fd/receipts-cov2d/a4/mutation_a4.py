"""COV2D addendum A4 mutants: one guard or declared rule per mutant, over cov2d_readout.py (and the open audit it relies
on in cov2d_blocks.py), killed by test_cov2d_readout. Run from a scratchpad with an interpreter that has PyROOT and numpy:
    TMPDIR=<dir> PYTHONDONTWRITEBYTECODE=1 python -B mutation_a4.py <worktree> [<mutant name> ...]
As mutation_amendment.py: each mutant rewrites one text of one file (it must occur once, or it counts as not killed),
runs the file's test modules, and restores it; a kill counts only on a test failure (rc != 0). The run exits 1 unless
every mutant is killed, and names any REQUIRED mutant (COV2D-ADDENDUM-A4.md section 8, with coverage-5b-audit's
additions) that was not."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
D = WT / "2d-unfolding/cov2d"
T = D / "tests"
R = "cov2d_readout.py"
TESTS = {R: ["test_cov2d_readout"], "cov2d_blocks.py": ["test_cov2d_readout"]}
M = [
    # phase S's gate (section 9.7), each refusal on its own
    (R, "null gate reads the local record, not origin's", 'raw = git_show(f"{ref}:{READOUT_REL}/{truth}/null_{truth}.json")',
     'raw = (Path(os.environ["TMPDIR"]).parent / f"null_{truth}.json").read_bytes()'),
    (R, "digest compare removed", "    if sha(raw) != digest:\n", "    if False:\n"),
    (R, "M refusal removed", '    if rec.get("M") != c.deploy_head(REPO):\n', "    if False:\n"),
    (R, "truth refusal removed", '    if rec.get("truth") != truth:\n', "    if False:\n"),
    (R, "verdict refusal removed", '    if rec.get("verdict") != "PASS":\n', "    if False:\n"),
    (R, "blocks-digest refusal removed", '    if npz is None or sha(npz) != rec.get("blocks_npz_sha256"):\n',
     "    if npz is None:\n"),
    (R, "inventory re-hash removed", '        if hashed(p) != rec["inventory"][k]:\n', "        if False:\n"),
    (R, "toy stat compare removed", '        if stat_of(f"{run_dir}/out/{lab}/xsec.root") != st:\n', "        if False:\n"),
    # section 9.9 (implemented here, not glue)
    (R, "section 9.9 skipped on the toys",
     'probs += section_9_9(lab, read_provenance(f), truth, rows[lab], env, run_dir, dshas[s], code=nrec["code"])',
     "probs += []"),
    (R, "A4-1 toys not held to the null record's code", 'dshas[s], code=nrec["code"])', "dshas[s], code=None)"),
    (R, "code compare removed", "            if prov.get(k) != code[k]:\n", "            if False:\n"),
    (R, "dataFileSha256 compare removed", '    if prov.get("dataFileSha256") != data_sha:\n', "    if False:\n"),
    (R, "runArgv compare removed", '    if Path(str(argv[0])).name != "re2_driver.py" or list(argv[1:]) != want_argv:\n',
     "    if False:\n"),
    (R, "seed compare removed", '    if cfg.get("seed") != row_seed:\n', "    if False:\n"),
    (R, "A4-2 the product's own label not checked",
     '    if cfg.get("out") != out or not m:\n        probs.append(f"{label}: runConfig out {cfg.get(\'out\')!r} != {out!r}")\n'
     '    elif m["truth"] != truth:\n        probs.append(f"{label}: names truth {m[\'truth\']}, not {truth}")\n',
     ""),
    (R, "toy data_file not its own", '        if data != f"data_{s}.root" or s not in c.TOY_SEEDS[truth]:\n',
     "        if False:\n"),
    (R, "non-toy data_file not the realization's", '        if data != f"data_{c.REALIZATION_SEED[truth]}.root":\n',
     "        if False:\n"),
    (R, "universe compare removed", '            if cfg.get("universe") != f"{b}:{i}":\n', "            if False:\n"),
    (R, "bootstrap seed compare removed", '            if cfg.get("bootstrap_seed") != int(rest):\n', "            if False:\n"),
    (R, "lateral omnifile compare removed", '            if not str(cfg.get("omnifile", "")).endswith(f"_active_{b}_{i}.root"):\n',
     "            if False:\n"),
    (R, "X/L may carry a universe", '        if want_role in ("X", "L") and (cfg.get("universe") is not None or cfg.get("bootstrap_seed") is not None):\n',
     "        if False:\n"),
    (R, "one code: several drivers admitted", "        if len(vals) != 1 or vals[0] is None:\n", "        if vals[0] is None:\n"),
    (R, "toys graded despite section 9.9", "        if probs:            # refused before any toy error is used\n",
     "        if False:\n"),
    # pins, seeds, inventory, identity, atime, phase N's own toy check
    (R, "pins removed (read_pinned)", "    if got != want:\n", "    if False:\n"),
    (R, "#866 product-digest pin removed",
     'return run.copy(f"{run_dir}/out/{label}/xsec.root", comp[label]["sha256"], f"{label}.root")',
     'return run.copy(f"{run_dir}/out/{label}/xsec.root", cb.read_noatime(f"{run_dir}/out/{label}/xsec.root")[1], f"{label}.root")'),
    (R, "toy seed-set check removed", '        if [n["seed"] for n in toys_n] != list(c.TOY_SEEDS[truth]):\n', "        if False:\n"),
    (R, "plan admits any toy set", "    if sorted(toys) != list(c.TOY_SEEDS[truth]):\n", "    if False:\n"),
    (R, "truth rows' order unchecked", '        if nseeds != [n["seed"] for n in natures]:\n', "        if False:\n"),
    (R, "phase N's toy-open check removed", "        if toy_opens:\n", "        if False:\n"),
    (R, "identity problems ignored", '        if rec["identity"]["problems"]:\n', "        if False:\n"),
    (R, "mtime window an hour early", "        if not lo <= t <= hi:\n", "        if not lo - 3600 <= t <= hi:\n"),
    (R, "PST taken as UTC-7", "PST = timezone(timedelta(hours=-8))", "PST = timezone(timedelta(hours=-7))"),
    (R, "G18 cells size unchecked", '        if cn_["size"] != G18_CELLS["size"] or minute != G18_CELLS["minute"]:\n',
     '        if minute != G18_CELLS["minute"]:\n'),
    (R, "atime STOP removed", '        if rec["atime_moved"]:\n', "        if False:\n"),
    (R, "a stop does not outrank the reading", '        if rec["stop"]:                # a stop outranks any reading; the graded one is kept beside it\n',
     "        if False:\n"),
    (R, "noatime_inputs dropped", 'rec["inputs"] = cb.noatime_inputs(ro, Path(td) / "rollup", {k: ro.PIN[k] for k in ROLLUP_PINS})',
     'rec["inputs"] = {}'),
    ("cov2d_blocks.py", "open audit off", "        if p.startswith(self.guarded) and not (noatime or p in self.sanctioned):\n",
     "        if False:\n"),
]
REQUIRED = {"null gate reads the local record, not origin's", "digest compare removed", "M refusal removed",
            "verdict refusal removed", "blocks-digest refusal removed", "inventory re-hash removed",
            "section 9.9 skipped on the toys", "A4-1 toys not held to the null record's code", "code compare removed",
            "dataFileSha256 compare removed", "runArgv compare removed", "seed compare removed",
            "A4-2 the product's own label not checked", "toy seed-set check removed", "#866 product-digest pin removed",
            "atime STOP removed", "open audit off", "noatime_inputs dropped", "phase N's toy-open check removed"}
if sys.argv[2:]:
    unknown = set(sys.argv[2:]) - {m[1] for m in M}
    assert not unknown, f"no such mutant: {sorted(unknown)}"
    M = [m for m in M if m[1] in sys.argv[2:]]
bak = Path(os.environ["TMPDIR"])
files = sorted({m[0] for m in M})
for f in files:
    (bak / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(D / f, bak / f)
killed, alive = 0, []
try:
    for f, name, a, b in M:
        src = (bak / f).read_text()
        if src.count(a) != 1:
            print(f"NOMATCH {f}: {name}", flush=True)
            alive.append(name)
            continue
        (D / f).write_text(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", *TESTS[f]], cwd=T, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        killed += bool(r.returncode)
        if not r.returncode:
            alive.append(name)
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {f}: {name}", flush=True)
        shutil.copy(bak / f, D / f)
finally:
    for f in files:
        shutil.copy(bak / f, D / f)
print(f"killed {killed} of {len(M)}")
if REQUIRED & set(alive):
    print(f"REQUIRED NOT KILLED: {sorted(REQUIRED & set(alive))}")
sys.exit(1 if alive else 0)
