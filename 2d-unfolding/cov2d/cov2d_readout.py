"""COV2D's bulk readout driver (COV2D-ADDENDUM-A4.md): from the bulk's products to C_T, its null, the graded reading and
section 6's readouts, at each truth, in two phases. Glue over cov2d_blocks, cov2d_null, cov2d_score and cov2d_readouts,
imported unchanged; the one new check is section 9.9 (implemented here, not glue). root_6_28 with the pinned MAT
environment, on a login node, as control95.

* Phase N (``null``) reads only what the null needs: X_<T>, the 175 universes, the 10 laterals and the 300 replicas, each
  against #866's completeness digest; part B's E_R; the rollup's inputs, C08_R and C_model at their pins. It builds the
  blocks (cov2d_blocks.assemble) and the null (cov2d_null.null_at_T), checks section 9.9 on those products, and records
  the input inventory: step A's cells.npz and pseudo_a.json and step B's truth_xsec.npz hashed without parsing, the 300
  toy products by stat only. It opens no toy product, and its own open audit log is checked for that (auditor A4-3).
  It writes null_<T>.json and blocks_<T>.npz, which reach main through a receipt PR before phase S may run.
* Phase S (``score``) refuses, before it opens any toy product, unless origin/main's null_<T>.json has the sha256 it is
  given, names this deploy's HEAD as M, this truth and verdict PASS; blocks_<T>.npz matches the record; and the
  inventory re-hashes to the record (section 9.7: the null is committed before the scorer opens any toy product). Then
  it checks section 9.9 on the toys, the toys' code against the null record's (auditor A4-1), and grades with
  cov2d_score and the readouts of cov2d_readouts.
* Section 9.9 (COV2D-DECLARATION.md:523-525): one driverSha256 and one omnifoldHelperSha256 across every product of a
  truth; each product's runConfig names its truth, role and seed (the label in ``out``, and per class ``data_file``,
  ``universe``, ``omnifile``, ``bootstrap_seed``); its runArgv is its runs-table row expanded, plus --out; its
  dataFileSha256 is the realization's or its own toy's file in the committed pseudo_b.json.
* Addendum A5 (COV2D-BINDING-2): at ndf = 205, 1B grade's Cholesky cross-check runs to max(1e-9, 10 kappa_2(C_T) eps),
  kappa_2 computed from C_T alone before any toy is read and recorded with the tolerance (``cholesky_check``); the
  leave-out-MEC readout's grade of C_T- takes the same rule from C_T- (``cholesky_check_minus``). A refusal from either
  grade writes score_<T>.invalid.json (which grade, its text and compared values) through Run.finish and prints
  "COV2D-SCORE <T> INVALID (grade refused, C_T|C_T_minus: ...)".

  python cov2d_readout.py null  --truth T --out DIR [--run-dir O]
  python cov2d_readout.py score --truth T --null-digest SHA256 --out DIR [--run-dir O] [--ref origin/main]

MEASURES: C_T, the null and the reading at a truth. CANNOT AUTHORIZE: a verdict beyond the declared reading; it goes to
the director.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402
import cov2d_blocks as cb  # noqa: E402
import cov2d_null as cn  # noqa: E402
import cov2d_readouts as cr  # noqa: E402
import cov2d_score as cs  # noqa: E402

REC_REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d"
REC = REPO / REC_REL
READOUT_REL = REC_REL + "/readout"
COMPLETENESS = (REC / "a2/bulk/completeness/completeness.tsv",
                "401e9d972d3d721999cadd184e7ce24544edbc80fba2a5b47eaac4db138230ae")   # stage 4's PASS record (#866)
C2_RECORD = (REC / "clip/c2-clip2.json", "39e333c557857672abda049b2caeab6cbe19cf9d24e800531a8763c805636d5e")
PSEUDO_A_SHA = {"G18": "163cf1aaac8b60b6c028c2e6f5fdbb97533f8f6af8d917f2cc0043ded630f416",     # pseudo/<T>/remote_sha256.txt
                "AR23": "bdb7a57d900ab62ee15cfeb6183a5529e04c3b6cfc6e3836c699cafd76595994"}
RUNS_SHA = {"G18": "bacf963137a63c4403ef8129362965606887abea2323d0d638f459ab5801074a",       # a2/bulk listing-130406Z.txt
            "AR23": "839ff2d623814fdc63cc4d6aa598f7fb508123c9803fb2610ba9e06ab4443a29",
            "G18C": "5ef2aca150959b972c6519a6599d6f84d5539504589a664ce9e591e9a6c2db7d"}       # connect-complete-1.log
RUN_DIR = "/pscratch/sd/j/josephrb/cov2d-run-20261104"
ENV_FILE = HERE / "jobs" / "cov2d_env.sh"
# The identity evidence (A4 section 3.4): sacct times are node-local PST, UTC-8 on these dates (DST ended 2026-11-01).
PST = timezone(timedelta(hours=-8))
JOB_WINDOW = {"G18": ("2026-11-05T02:42:18", "2026-11-05T05:06:52"),      # job 60848251 (pseudo/G18/end_state.txt)
              "AR23": ("2026-11-05T22:19:09", "2026-11-06T00:50:53")}     # job 60889690 (pseudo/AR23/end_state.txt)
G18_CELLS = {"size": 4_321_842, "minute": "2026-11-05T03:52"}            # pseudo/G18/end_state.txt:43
ROLLUP_PINS = ("constraint", "vl175_build_json", "vl175_minos_npz", "flux_mefhc")
LABEL = re.compile(r"^(?P<role>[XULBT])_(?P<truth>G18|AR23)(?:_(?P<rest>.+))?$")


def pseudo_dir(truth: str) -> str:
    """cov2d_env.sh's pseudo_dir: AR23 reran into pseudo/AR23-a2 (addendum A2); G18C is G18's symlink (addendum A3)."""
    return "pseudo/AR23-a2" if truth == "AR23" else f"pseudo/{truth}"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_pinned(path, want: str) -> bytes:
    data, got = cb.read_noatime(path)
    if got != want:
        raise c.Refusal(f"{path}: sha256 {got} != {want}")
    return data


def completeness(truth: str) -> dict:
    """{label: row} of stage 4's committed table for one truth; every row must read PASS."""
    text = read_pinned(*COMPLETENESS).decode()
    lines = text.splitlines()
    head = lines[0].split("\t")
    rows = {}
    for ln in lines[1:]:
        r = dict(zip(head, ln.split("\t")))
        if r["truth"] == truth:
            if r["verdict"] != "PASS":
                raise c.Refusal(f"completeness: {r['label']} is {r['verdict']}")
            rows[r["label"]] = r
    return rows


def plan(truth: str, comp: dict) -> dict:
    """The labels by class, in the order the bound functions read them; refused unless each class is exactly declared."""
    p = {"central": f"X_{truth}", "universe": {}, "lateral": {}, "replica": [], "toy": []}
    for lab in comp:
        m = LABEL.match(lab)
        if not m or m["truth"] != truth:
            raise c.Refusal(f"completeness: {lab} is not a {truth} label")
        role, rest = m["role"], m["rest"]
        if role == "U":
            b, i = rest.rsplit("_", 1)
            p["universe"].setdefault(b, {})[int(i)] = lab
        elif role == "L":
            b, i = rest.rsplit("_", 1)
            p["lateral"].setdefault(b, {})[int(i)] = lab
        elif role == "B":
            p["replica"].append(lab)
        elif role == "T":
            p["toy"].append(lab)
    p["universe"] = {b: [v[i] for i in sorted(v)] for b, v in p["universe"].items()}
    p["lateral"] = {b: [v[i] for i in sorted(v)] for b, v in p["lateral"].items()}
    if p["central"] not in comp:
        raise c.Refusal(f"completeness lists no {p['central']}")
    if set(p["universe"]) != set(c.ORDER) or any(len(p["universe"][b]) != c.BANDS[b] for b in c.ORDER):
        raise c.Refusal("the universes are not the declared 38 bands and 175 universes")
    if set(p["lateral"]) != set(c.LATERAL_BANDS) or any(len(v) != 2 for v in p["lateral"].values()):
        raise c.Refusal("the laterals are not the declared 5 bands x 2")
    if sorted(p["replica"]) != [f"B_{truth}_{n:03d}" for n in range(1, 301)]:
        raise c.Refusal("the replicas are not B_<T>_001..300")
    p["replica"] = sorted(p["replica"])
    toys = {int(lab.rsplit("_", 1)[1]): lab for lab in p["toy"]}
    if sorted(toys) != list(c.TOY_SEEDS[truth]):
        raise c.Refusal(f"the toys are not {truth}'s declared seeds")
    p["toy"] = [toys[s] for s in c.TOY_SEEDS[truth]]
    return p


def runs_rows(run_dir: str, truth: str) -> dict:
    """{label: (table truth, job, args)} from the pinned runs tables (G18's five completion rows from runs_G18C.tsv)."""
    out = {}
    for t in ([truth, "G18C"] if truth == "G18" else [truth]):
        text = read_pinned(f"{run_dir}/tables/runs_{t}.tsv", RUNS_SHA[t]).decode()
        lines = text.splitlines()
        head = lines[0].split("\t")
        for ln in lines[1:]:
            r = dict(zip(head, ln.split("\t")))
            out[r["label"]] = (t, r["job"], r["args"])     # runs_G18C.tsv's rows supersede runs_G18.tsv's (A3)
    return out


def job_env(env_text: str, run_dir: str) -> dict:
    """The variables cov2d_env.sh exports for the runs' arguments (plain NAME=value assignments, in order)."""
    env = {"O": run_dir}
    for raw in env_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("export "):
            line = line[len("export "):]
        toks = line.split()
        if not toks or not all(re.match(r"^[A-Z][A-Z0-9_]*=\S+$", t) for t in toks):
            continue
        for t in toks:
            k, v = t.split("=", 1)
            if ":-" in v:
                continue
            env[k] = re.sub(r"\$\{?([A-Z][A-Z0-9_]*)\}?", lambda m: env.get(m.group(1), m.group(0)), v)
    return env


def expected_argv(args: str, env: dict, out: str) -> list:
    """The runs-table row as the job hands it to re2_driver.py: ``eval "set -- $args"`` with the job's environment,
    then --out (cov2d_job.sbatch)."""
    toks = [re.sub(r"\$\{?([A-Z][A-Z0-9_]*)\}?", lambda m: env[m.group(1)], t) for t in shlex.split(args)]
    return toks + ["--out", out]


def read_provenance(path) -> dict:
    """A product's TNamed records, read as test_re2_data_file.records reads them (only the TNamed provenance)."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.ClassName() == "TNamed":
            out[key.GetName()] = obj.GetTitle()
    f.Close()
    return out


def section_9_9(label: str, prov: dict, truth: str, row: tuple, env: dict, run_dir: str, data_sha: str,
                code: dict | None = None) -> list:
    """Section 9.9 for one product (implemented here, not glue): the problems, empty when it holds."""
    table_truth, _, args = row
    probs = []
    try:
        cfg, argv = json.loads(prov["runConfig"]), json.loads(prov["runArgv"])
    except (KeyError, ValueError) as e:
        return [f"{label}: no readable runConfig/runArgv ({e})"]
    out = f"{run_dir}/out/{label}/xsec.root"
    m = LABEL.match(Path(str(cfg.get("out", ""))).parent.name)
    if cfg.get("out") != out or not m:
        probs.append(f"{label}: runConfig out {cfg.get('out')!r} != {out!r}")
    elif m["truth"] != truth:
        probs.append(f"{label}: names truth {m['truth']}, not {truth}")
    want_role = LABEL.match(label)["role"]
    if m and m["role"] != want_role:
        probs.append(f"{label}: names role {m['role']}, not {want_role}")
    e = dict(env, D=f"{run_dir}/{pseudo_dir(table_truth)}/b")
    try:
        want_argv = expected_argv(args, e, out)
    except KeyError as k:
        return probs + [f"{label}: its row names an unset variable {k}"]
    if Path(str(argv[0])).name != "re2_driver.py" or list(argv[1:]) != want_argv:
        probs.append(f"{label}: runArgv differs from its runs row")
    row_seed = int(shlex.split(args)[shlex.split(args).index("--seed") + 1])
    if cfg.get("seed") != row_seed:
        probs.append(f"{label}: seed {cfg.get('seed')} != {row_seed}")
    rest = LABEL.match(label)["rest"]
    data = Path(str(cfg.get("data_file", ""))).name
    if want_role == "T":
        s = int(rest)
        if data != f"data_{s}.root" or s not in c.TOY_SEEDS[truth]:
            probs.append(f"{label}: data_file {data} is not its toy's")
    else:
        if data != f"data_{c.REALIZATION_SEED[truth]}.root":
            probs.append(f"{label}: data_file {data} is not the realization's")
        if want_role == "U":
            b, i = rest.rsplit("_", 1)
            if cfg.get("universe") != f"{b}:{i}":
                probs.append(f"{label}: universe {cfg.get('universe')!r} != {b}:{i}")
        elif want_role == "L":
            b, i = rest.rsplit("_", 1)
            if not str(cfg.get("omnifile", "")).endswith(f"_active_{b}_{i}.root"):
                probs.append(f"{label}: omnifile is not lateral {b}_{i}'s")
        elif want_role == "B":
            if cfg.get("bootstrap_seed") != int(rest):
                probs.append(f"{label}: bootstrap_seed {cfg.get('bootstrap_seed')} != {int(rest)}")
        if want_role in ("X", "L") and (cfg.get("universe") is not None or cfg.get("bootstrap_seed") is not None):
            probs.append(f"{label}: a {want_role} product carries a universe or a bootstrap seed")
    if prov.get("dataFileSha256") != data_sha:
        probs.append(f"{label}: dataFileSha256 {prov.get('dataFileSha256')} != {data_sha}")
    if code is not None:
        for k in ("driverSha256", "omnifoldHelperSha256"):
            if prov.get(k) != code[k]:
                probs.append(f"{label}: {k} {prov.get(k)} != the null record's {code[k]}")
    return probs


def one_code(provs: dict) -> tuple[dict | None, list]:
    """The single driverSha256 and omnifoldHelperSha256 of a set of products, or the problem."""
    code, probs = {}, []
    for k in ("driverSha256", "omnifoldHelperSha256"):
        vals = sorted({p.get(k) for p in provs.values()}, key=str)
        if len(vals) != 1 or vals[0] is None:
            probs.append(f"{k}: {len(vals)} values across the products")
        code[k] = vals[0] if vals else None
    return (code if not probs else None), probs


def data_shas(truth: str) -> dict:
    """{seed: sha256} of the truth's data files, from its committed pseudo_b.json."""
    rec = json.loads((REC / "pseudo" / truth / "pseudo_b.json").read_text())
    return {int(f["seed"]): f["sha256"] for f in rec["files"]}


def inventory_paths(run_dir: str, truth: str) -> dict:
    d = f"{run_dir}/{pseudo_dir(truth)}"
    return {"cells_npz": f"{d}/a/cells.npz", "pseudo_a_json": f"{d}/a/pseudo_a.json", "truth_xsec_npz": f"{d}/b/truth_xsec.npz"}


def stat_of(path) -> dict:
    st = os.stat(path)        # metadata only: no open, no read
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "inode": st.st_ino}


def hashed(path) -> dict:
    data, s = cb.read_noatime(path)
    return dict(stat_of(path), sha256=s)


def epoch_pst(text: str) -> float:
    return datetime.fromisoformat(text).replace(tzinfo=PST).timestamp()


def identity(truth: str, inv: dict) -> list:
    """A4 section 3.4's checks against the earlier evidence on main; the problems, empty when they hold."""
    lo, hi = (epoch_pst(t) for t in JOB_WINDOW[truth])
    probs = []
    for k in ("cells_npz", "pseudo_a_json", "truth_xsec_npz"):
        t = inv[k]["mtime_ns"] / 1e9
        if not lo <= t <= hi:
            probs.append(f"{k}: mtime {t} outside the job's window [{lo}, {hi}]")
    if inv["pseudo_a_json"]["sha256"] != PSEUDO_A_SHA[truth]:
        probs.append(f"pseudo_a.json sha256 {inv['pseudo_a_json']['sha256']} != {PSEUDO_A_SHA[truth]}")
    if truth == "G18":
        cn_ = inv["cells_npz"]
        minute = datetime.fromtimestamp(cn_["mtime_ns"] / 1e9, PST).strftime("%Y-%m-%dT%H:%M")
        if cn_["size"] != G18_CELLS["size"] or minute != G18_CELLS["minute"]:
            probs.append(f"G18 cells.npz: size {cn_['size']}, minute {minute} != {G18_CELLS}")
    return probs


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.generic):
        return o.item()
    return o


def null_from_json(d: dict) -> dict:
    """fd_1b_null.null_contents' dict back from JSON: its per-cell vectors as float64 arrays (exact: JSON's repr)."""
    out = dict(d)
    for k in ("p_cell", "se_cell"):
        out[k] = np.asarray(d[k], np.float64)
    return out


def git_show(ref_path: str) -> bytes | None:
    r = subprocess.run(["git", "-C", str(REPO), "show", ref_path], capture_output=True)
    return r.stdout if r.returncode == 0 else None


class Run:
    """What both phases share: the record, the open audit, the rollup, private copies and the atime ledger."""
    def __init__(self, truth: str, run_dir: str, tmp: Path):
        import ROOT
        ROOT.gROOT.SetBatch(True)
        self.truth, self.run_dir, self.tmp = truth, run_dir, tmp
        cb.AUDIT = cb.OpenAudit().install(ROOT)
        self.rec = {"truth": truth, "host": os.uname().nodename, "root": ROOT.gROOT.GetVersion(), "pins_checked": True,
                    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "stop": [], "controls_failed": [],
                    "M": c.deploy_head(REPO), "mat_environment": cb.pinned_mat_environment()}
        self.ro = cb.rollup()
        self.atimes = {}
        self.prod = tmp / "products"
        self.prod.mkdir()

    def watch(self, path):
        self.atimes.setdefault(str(path), os.stat(path).st_atime_ns)

    def copy(self, src, want: str, name: str) -> Path:
        self.watch(src)
        dst = self.prod / name
        dst.write_bytes(read_pinned(src, want))
        return dst

    def er_cells(self):
        sums = self.ro.partb_sums()
        er = self.copy(f"{self.ro.NS_R}/out/ER/xsec.root", sums["ER/xsec.root"], "ER.root")
        return self.ro.Cells(er)

    def finish(self, out: Path, name: str) -> dict:
        rec = self.rec
        rec["atime_checked"] = len(self.atimes)
        rec["atime_moved"] = [p for p, a in self.atimes.items() if os.stat(p).st_atime_ns != a]
        if rec["atime_moved"]:
            rec["stop"].append(f"atime moved on {len(rec['atime_moved'])} inputs")
        rec["open_audit"] = {"opens": len(cb.AUDIT.log), "refused": cb.AUDIT.refused, **cb.AUDIT.counts()}
        if cb.AUDIT.refused:
            rec["stop"].append(f"open audit refused {len(cb.AUDIT.refused)} opens")
        rec["modules"] = {m.__name__: os.path.realpath(m.__file__) for m in (c, cb, cn, cs, cr, self.ro)}
        outside = [k for k, f in rec["modules"].items() if not f.startswith(os.path.realpath(REPO) + os.sep)]
        if outside:
            rec["stop"].append(f"modules imported from outside the clone: {outside}")
        if rec["stop"]:                # a stop outranks any reading; the graded one is kept beside it
            if "verdict" in rec:
                rec["verdict_graded"] = rec["verdict"]
            rec["verdict"] = "STOP"
        elif "verdict" not in rec:
            rec["verdict"] = "INVALID" if rec["controls_failed"] else "PASS"
        (out / name).write_text(json.dumps(jsonable(rec), indent=1, sort_keys=True))
        cb.AUDIT.uninstall()
        return rec


def phase_null(truth: str, out: Path, run_dir: str) -> dict:
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        run = Run(truth, run_dir, Path(td))
        rec, ro = run.rec, run.ro
        comp = completeness(truth)
        pl = plan(truth, comp)
        rows = runs_rows(run_dir, truth)
        env = job_env(ENV_FILE.read_text(), run_dir)
        for k in ROLLUP_PINS:
            run.watch(ro.PIN[k][0])
        rec["inputs"] = cb.noatime_inputs(ro, Path(td) / "rollup", {k: ro.PIN[k] for k in ROLLUP_PINS})
        cells = run.er_cells()
        rep, x_R = cells.rep, cells.x
        C_model, C_minus, rec["c_model"] = cb.c_model()
        if rec["c_model"]["cells"] != [int(i) for i in np.flatnonzero(rep)]:
            rec["stop"].append("cmodel_2d.json's 205 cells are not E_R's reported cells")
        run.watch(cb.C08_R_FILE[0])
        C08_R = np.load(io.BytesIO(read_pinned(*cb.C08_R_FILE)))["c08"]

        def get(label):
            return run.copy(f"{run_dir}/out/{label}/xsec.root", comp[label]["sha256"], f"{label}.root")
        files = {pl["central"]: get(pl["central"])}
        for labs in list(pl["universe"].values()) + list(pl["lateral"].values()):
            files.update({lab: get(lab) for lab in labs})
        files.update({lab: get(lab) for lab in pl["replica"]})
        n_checks = len(ro.CHECKS)
        w_flux, phi_minos = ro.flux_weights()
        x_T = cells.vec(files[pl["central"]])
        bands = {b: np.stack([cells.vec(files[lab]) for lab in labs]) for b, labs in pl["universe"].items()}
        bands.update({b: np.stack([cells.vec(files[lab]) for lab in labs]) for b, labs in pl["lateral"].items()})
        minos_x = ro.x01(cells, [files[lab] for lab in pl["lateral"]["Muon_Energy_MINOS"]], phi_minos, f"cov2d_{truth}")
        failed = [k for k in list(ro.CHECKS)[n_checks:] if not ro.CHECKS[k]["ok"]]
        if failed:
            rec["controls_failed"].append(f"rollup checks failed: {failed}")
        X_rep = np.stack([cells.vec(files[lab]) for lab in pl["replica"]])
        blocks = cb.assemble(x_T, rep, bands, minos_x, w_flux, X_rep, x_R, C08_R, C_model, C_minus)
        rec["section_9_8"] = blocks["section_9_8"]
        if not blocks["section_9_8"]["pass"]:
            rec["controls_failed"].append("section 9.8: C_T is not symmetric PSD at 1e-12")
        res = cn.null_at_T(blocks, bands, minos_x, w_flux)
        rec.update({"null": res["null"], "thresholds": res["thresholds"], "size": res["size"],
                    "null_minus": res.get("null_minus")})
        # section 9.9 on the non-toy products (implemented here, not glue)
        provs = {lab: read_provenance(f) for lab, f in files.items()}
        real = data_shas(truth)[c.REALIZATION_SEED[truth]]
        probs = [p for lab, pv in provs.items() for p in section_9_9(lab, pv, truth, rows[lab], env, run_dir, real)]
        code, cprobs = one_code(provs)
        rec["code"] = code
        rec["section_9_9"] = {"products": len(provs), "problems": probs + cprobs}
        if probs or cprobs:
            rec["controls_failed"].append(f"section 9.9: {len(probs) + len(cprobs)} problems")
        # the input inventory: step A/B files hashed unparsed, toys by stat only (no open)
        for p in inventory_paths(run_dir, truth).values():
            run.watch(p)
        inv = {k: hashed(p) for k, p in inventory_paths(run_dir, truth).items()}
        inv["toys"] = {lab: stat_of(f"{run_dir}/out/{lab}/xsec.root") for lab in pl["toy"]}
        rec["inventory"] = inv
        rec["identity"] = {"problems": identity(truth, inv)}
        if rec["identity"]["problems"]:
            rec["stop"].append(f"identity: {rec['identity']['problems']}")
        toy_opens = [p for _, p, _ in cb.AUDIT.log if f"/out/T_{truth}_" in p]
        rec["toy_paths_opened"] = len(toy_opens)
        if toy_opens:
            rec["stop"].append(f"phase N opened {len(toy_opens)} toy paths")
        arrays = {k: blocks[k] for k in ("C_T", "C_univ", "C_lat", "C_norm", "C_stat", "C08", "C_model_abs")}
        if "C_T_minus" in blocks:
            arrays["C_T_minus"] = blocks["C_T_minus"]
        arrays.update(x_T=x_T, x_R=x_R, rep=rep, minos_x=minos_x, w_flux=np.asarray(w_flux, np.float64))
        arrays.update({f"band__{b}": v for b, v in bands.items()})
        np.savez(out / f"blocks_{truth}.npz", **arrays)
        rec["blocks_npz_sha256"] = sha((out / f"blocks_{truth}.npz").read_bytes())
        rec["products_read"] = len(files)
        return run.finish(out, f"null_{truth}.json")


def gate(truth: str, digest: str, ref: str, run_dir: str) -> tuple[dict, dict]:
    """Phase S's refusals, before any toy product is opened (section 9.7)."""
    raw = git_show(f"{ref}:{READOUT_REL}/{truth}/null_{truth}.json")
    if raw is None:
        raise c.Refusal(f"{ref} holds no null_{truth}.json")
    if sha(raw) != digest:
        raise c.Refusal(f"{ref}'s null_{truth}.json is {sha(raw)}, not {digest}")
    rec = json.loads(raw)
    if rec.get("M") != c.deploy_head(REPO):
        raise c.Refusal(f"the null record's M {rec.get('M')} is not this deploy's HEAD")
    if rec.get("truth") != truth:
        raise c.Refusal(f"the null record is {rec.get('truth')}'s, not {truth}'s")
    if rec.get("verdict") != "PASS":
        raise c.Refusal(f"the null record's verdict is {rec.get('verdict')}")
    npz = git_show(f"{ref}:{READOUT_REL}/{truth}/blocks_{truth}.npz")
    if npz is None or sha(npz) != rec.get("blocks_npz_sha256"):
        raise c.Refusal("blocks npz does not match the null record")
    blocks = dict(np.load(io.BytesIO(npz)))
    for k, p in inventory_paths(run_dir, truth).items():
        if hashed(p) != rec["inventory"][k]:
            raise c.Refusal(f"inventory: {k} differs from the null record")
    for lab, st in rec["inventory"]["toys"].items():
        if stat_of(f"{run_dir}/out/{lab}/xsec.root") != st:
            raise c.Refusal(f"inventory: {lab}'s stat differs from the null record")
    return rec, blocks


def cholesky_tol(C_T: np.ndarray) -> dict:
    """COV2D-BINDING-2 addendum A5: the tolerance of 1B grade's Cholesky cross-check at full rank, from C_T alone:
    max(1e-9, 10 kappa_2(C_T) eps), kappa_2 = lambda_max / lambda_min, eps float64's machine epsilon."""
    lam = np.linalg.eigvalsh(np.asarray(C_T, np.float64))
    eps = float(np.finfo(np.float64).eps)
    kappa = float(lam[-1] / lam[0]) if lam[0] > 0 else float("inf")
    return {"rule": "max(1e-9, 10 kappa_2(C_T) eps)", "kappa2": kappa, "eps": eps, "tol": max(1e-9, 10 * kappa * eps)}


def phase_score(truth: str, digest: str, out: Path, run_dir: str, ref: str) -> dict:
    import fd_1b_mc as mc
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        run = Run(truth, run_dir, Path(td))
        try:
            for p in inventory_paths(run_dir, truth).values():
                run.watch(p)
            nrec, B = gate(truth, digest, ref, run_dir)     # under the open audit; no toy product opened yet
        except Exception:
            cb.AUDIT.uninstall()
            raise
        rec, ro = run.rec, run.ro
        rec.update(null_digest=digest, ref=ref, code=nrec["code"])
        rec["cholesky_check"] = cholesky_tol(B["C_T"])      # addendum A5: from C_T alone, before any toy is read
        rec["cholesky_check_minus"] = cholesky_tol(B["C_T_minus"])     # the same rule for the leave-out-MEC grade
        comp = completeness(truth)
        pl = plan(truth, comp)
        rows = runs_rows(run_dir, truth)
        env = job_env(ENV_FILE.read_text(), run_dir)
        cells = run.er_cells()
        if not np.array_equal(np.asarray(cells.rep, bool), B["rep"].astype(bool)):
            raise c.Refusal("E_R's cells differ from the null record's")
        flat = [int(i) for i in np.flatnonzero(cells.rep)]
        dshas = data_shas(truth)
        files = {lab: run.copy(f"{run_dir}/out/{lab}/xsec.root", comp[lab]["sha256"], f"{lab}.root") for lab in pl["toy"]}
        probs = []
        for lab, f in files.items():
            s = int(lab.rsplit("_", 1)[1])
            probs += section_9_9(lab, read_provenance(f), truth, rows[lab], env, run_dir, dshas[s], code=nrec["code"])
        rec["section_9_9"] = {"products": len(files), "problems": probs}
        if probs:            # refused before any toy error is used
            rec["controls_failed"].append(f"section 9.9: {len(probs)} problems")
            rec["verdict"] = "INVALID"
            return run.finish(out, f"score_{truth}.json")
        x_hat = np.stack([cells.vec(files[lab]) for lab in pl["toy"]])
        paths = inventory_paths(run_dir, truth)
        txs = np.load(io.BytesIO(read_pinned(paths["truth_xsec_npz"], nrec["inventory"]["truth_xsec_npz"]["sha256"])))
        cnpz = dict(np.load(io.BytesIO(read_pinned(paths["cells_npz"], nrec["inventory"]["cells_npz"]["sha256"]))))
        pa = json.loads(read_pinned(REC / "pseudo" / truth / "pseudo_a.json", PSEUDO_A_SHA[truth]))
        natures = pa["natures"]
        toys_n = [n for n in natures if n["role"] == "toy"]
        if [n["seed"] for n in toys_n] != list(c.TOY_SEEDS[truth]):
            raise c.Refusal("pseudo_a's toys are not the declared seeds in order")
        nseeds = [int(s) for s in txs["seeds"]]
        if nseeds != [n["seed"] for n in natures]:
            raise c.Refusal("truth_xsec.npz's rows are not pseudo_a's natures in order")
        xs = np.asarray(txs["xsec"], np.float64).reshape(len(nseeds), -1)[:, np.asarray(cells.rep, bool)]
        x_true = xs[[nseeds.index(s) for s in c.TOY_SEEDS[truth]]]
        x_true_real = xs[nseeds.index(c.REALIZATION_SEED[truth])]
        cseeds = [int(s) for s in cnpz["seeds"]]
        toy_index = [cseeds.index(s) for s in c.TOY_SEEDS[truth]]
        lam = {t["seed"]: t["truth_lambda"] for t in pa["toys"]}
        rec["truth_lambda_inequality"] = {
            "holds_in": int(sum(np.sum(cnpz["m_all"][cseeds.index(s)]) <= -lam[s]["sum_lambda_neg"] * (1 + 1e-12)
                                for s in c.TOY_SEEDS[truth])), "of": len(toy_index),
            "operands": {"cells_npz": nrec["inventory"]["cells_npz"]["sha256"], "pseudo_a_json": PSEUDO_A_SHA[truth]},
            "decisive": False}
        bands = {k[len("band__"):]: v for k, v in B.items() if k.startswith("band__")}
        C_T = B["C_T"]
        deltas = cs.lateral_deltas(bands, B["minos_x"])
        E, cross = cs.errors(x_hat, x_true, natures, deltas, C_T)
        null, null_minus = null_from_json(nrec["null"]), null_from_json(nrec["null_minus"])
        ratio_rec = json.loads(read_pinned(*C2_RECORD))
        if [int(x) for x in ratio_rec["efficiency"]["cells205"]] != flat:
            raise c.Refusal("C2's 205 cells are not E_R's reported cells")
        weak_ratio = np.asarray(ratio_rec["b"][truth]["variance_ratio"]["option_1_clipped"], np.float64)
        compared, compared_minus, which = {}, {}, "C_T"
        try:
            g = cs.score(E, C_T, null, truth, flat, weak_ratio, rec["controls_failed"] + nrec["controls_failed"],
                         chol_tol=rec["cholesky_check"]["tol"], chol_out=compared)
            which = "C_T_minus"
            lom = cr.leave_out_mec(E, {"C_T_minus": B["C_T_minus"]}, null_minus, g, flat,
                                   chol_tol=rec["cholesky_check_minus"]["tol"], chol_out=compared_minus)
        except mc.Refusal as e:      # addendum A5: a grade refusal is INVALID with its record, and Run finishes
            key = "cholesky_check" if which == "C_T" else "cholesky_check_minus"
            rec[key]["compared"] = getattr(e, "compared", None)
            rec["grade_refusal"] = {"grade": which, "text": str(e), "compared": getattr(e, "compared", None)}
            rec["controls_failed"].append(f"grade refused ({which}): {e}")
            rec["verdict"] = "INVALID"
            return run.finish(out, f"score_{truth}.invalid.json")
        rec["cholesky_check"]["compared"] = compared
        rec["cholesky_check_minus"]["compared"] = compared_minus
        sigma = np.sqrt(np.diag(C_T))
        rec["grade"] = g
        rec["cross_term"] = cross
        rec["readouts"] = {
            "spread_alone": cr.spread_alone(E, C_T, B["C_model_abs"]),
            "bias": cr.bias(E, sigma),
            "predicted_offset": cr.predicted_offset(bands, B["w_flux"], B["x_T"]),
            "leave_out_mec": lom,
            "realization_check": cr.realization_check(B["x_T"], x_true_real, sigma),
            "clipping_residual": cr.clipping_residual(cnpz, toy_index, np.asarray(flat), x_true, sigma, C_T,
                                                      g["flagged_cells"], truth)}
        rec["verdict"] = g["verdict"]
        return run.finish(out, f"score_{truth}.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    pn = sub.add_parser("null")
    ps_ = sub.add_parser("score")
    for p_ in (pn, ps_):
        p_.add_argument("--truth", required=True, choices=sorted(c.TOY_SEEDS))
        p_.add_argument("--out", required=True)
        p_.add_argument("--run-dir", default=RUN_DIR)
    ps_.add_argument("--null-digest", required=True)
    ps_.add_argument("--ref", default="origin/main")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "null":
        rec = phase_null(a.truth, out, a.run_dir)
        print(f"COV2D-NULL {a.truth} {rec['verdict']} stops={len(rec['stop'])} controls_failed={len(rec['controls_failed'])}")
        return 0 if rec["verdict"] == "PASS" else 3
    try:
        rec = phase_score(a.truth, a.null_digest, out, a.run_dir, a.ref)
    except c.Refusal as e:
        (out / f"score_{a.truth}.refused.json").write_text(json.dumps({"truth": a.truth, "refused": str(e)}, indent=1))
        print(f"COV2D-SCORE {a.truth} REFUSED {e}")
        return 2
    if rec.get("grade_refusal"):
        gr = rec["grade_refusal"]
        print(f"COV2D-SCORE {a.truth} {rec['verdict']} (grade refused, {gr['grade']}: {gr['text']})")
        return 3
    print(f"COV2D-SCORE {a.truth} {rec['verdict']}")
    return 0 if rec["verdict"] in ("COVERS", "UNDER-COVERS") else 3


if __name__ == "__main__":
    sys.exit(main())
