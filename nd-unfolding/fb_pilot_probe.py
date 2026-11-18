#!/usr/bin/env python3
"""PILOT-FB: one remedy unfold (forced LightGBM bins) through RS1's bound stability path, or the prep step's edges.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/pilot-fb/
PILOT-FB-DECLARATION.md rev 3 (§3 the edges, §4 the arms, §5.1 the gates, §8 this module), bound by PILOT-FB-BINDING-1
at M_PFB 522ac0b6. Authority: DECISION-20261117b-joseph-note-plan.md item 3.

    fb_pilot_probe.py prep --edges-out DIR -- <s5p_numerics.py arguments, --pairs=-:->
    fb_pilot_probe.py run --set E1|E2|E3 --edges DIR -- <s5p_numerics.py arguments, one pair>

Both go through ``estimator_stability_probe.main`` as FD-STAB's ``control`` stability path, unchanged, exactly as RS1's
``rounding_mechanism_probe.py run`` does; A0R is RS1's own A0 task and needs nothing here. This module installs first,
so the bound probe's ``install`` and ``s5e_candidate.install`` compose over its rebindings:

* ``argparse.ArgumentParser.parse_args``: the runner's arguments must be RS1's declared stability input
  (``rounding_mechanism_probe.check_namespace``'s rules) with this set's declared pairs only; nothing is written unless
  the check ran;
* ``s5p_numerics.jittered``: keeps the run's unjittered inputs and its jittered sources, for J;
* ``s5p_numerics.unfold_one``: prep builds the base role matrices and the edges (G0) and stops before any fit; run
  builds, in the same process (after the runner's own installs), the base and the rebuilt jittered role matrices
  (``role_matrices``) for G2 and J, then calls the bound unfold;
* ``omnifold_nn_core.make_estimators``: each of clf1, clf2 and reg gets its role's forced-bins file and the set's
  ``max_bin``; its first fit and scored matrices are captured (J2, G2), G3 (a) runs on its first fit, and G3 (b)-(c)
  on every fit;
* ``s5n_pseudo.refine_params`` and ``s5n_pseudo.recorded_classifier``: the refinement gets its file and ``max_bin``;
  its fit matrix is captured, G3 (a) runs on it and G3 (b)-(c) on its model;
* ``s5n_pseudo.write_product``: the product's meta gains a ``pilot_fb`` block, and a sidecar ``<product>.pfb.json``
  carries every gate's record (the identity gate's parameters included). The product is written whatever the gates
  read; the analysis (``fb_pilot_analyze.py``) refuses to read a failed gate.

MEASURES: one remedy unfold and its gate records. CANNOT AUTHORIZE: a reading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import estimator_stability_probe as esp  # noqa: E402
import fb_pilot_edges as E  # noqa: E402
import fb_pilot_gates as G  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import rounding_mechanism_probe as rmp  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402

SCHEMA = "pilot-fb/1"
SEEDS = tuple(range(1, 21))
PAIRS = {"E1": ["-:-"] + [f"-:{s}" for s in SEEDS], "E2": ["-:-"], "E3": ["-:-"]}
SOURCES = ("MCgen", "MCreco", "measured")  # s5p_numerics.COORD_KEYS; and bkg_reco
LOOP_ROLES = ("clf1", "clf2", "reg")


class Refusal(RuntimeError):
    pass


class PrepDone(Exception):
    pass


def sha256_path(path: Path) -> str:
    return rmp.sha256_path(Path(path))


def role_matrices(exp: dict, dtype) -> dict:
    """{role: (fit, scored or None)} as the bound path hands them to LightGBM (§2 item 1):
    the refinement fits and scores signed_sample(exp)'s rows (s5n_pseudo.py:222-227, unfold_2d...:446-447); the loop
    takes the [pass_truth] subsets (omnifold_nn_core.py:210-211), clf1 fits MCreco[pass_reco] with the measured rows
    (measured = the signed sample cast as the run casts it, every row passing) and scores MCreco[pass_reco]; reg fits
    MCgen[pass_reco] and scores MCgen[~pass_reco]; clf2 fits MCgen twice and scores MCgen."""
    feat = s5n_pseudo.signed_sample(exp)[0]
    measured = feat.astype(dtype)
    pt = np.asarray(exp["pass_truth"], bool)
    mcreco, mcgen = np.asarray(exp["MCreco"])[pt], np.asarray(exp["MCgen"])[pt]
    pr = np.asarray(exp["pass_reco"], bool)[pt]
    return {"ref": (feat, None),
            "clf1": (np.concatenate([mcreco[pr], measured]), mcreco[pr]),
            "reg": (mcgen[pr], mcgen[~pr]),
            "clf2": (np.concatenate([mcgen, mcgen]), mcgen)}


def check_namespace(ns, s: str) -> str | None:
    """RS1's stability-input rules (rounding_mechanism_probe.check_namespace), with this set's pairs."""
    want = rmp.STABILITY
    if getattr(ns, "truth", None) != want["truth"] or float(getattr(ns, "amplitude", -1)) != want["amplitude"]:
        return f"PILOT-FB runs only RS1's stability truth {want['truth']} at amplitude {want['amplitude']}"
    ratio = getattr(ns, "eavail_ratio", None)
    if ratio is None or sha256_path(Path(ratio)) != want["ratio_sha256"]:
        return "the --eavail-ratio file is not the declared one"
    if getattr(ns, "expect_npz_sha256", None) != want["npz_sha256"] or \
            getattr(ns, "expect_bkg_sha256", None) != want["bkg_sha256"]:
        return "the expected input digests are not the declared of_inputs_5d.npz and bkg_dump.npz"
    for key in ("iters", "threads", "estimator_seed"):
        if getattr(ns, key, None) != want[key]:
            return f"--{key.replace('_', '-')} must be {want[key]}"
    if getattr(ns, "pseudo_seed", None) != want["pseudo_seed"]:
        return f"--pseudo-seed must be {want['pseudo_seed']}"
    if getattr(ns, "fixed_split_seed", None) is not None or getattr(ns, "pseudo_seeds", None) is not None:
        return "--fixed-split-seed and --pseudo-seeds are refused"
    pairs = s5p_numerics.parse_pairs(getattr(ns, "pairs", ""))
    allowed = set(s5p_numerics.parse_pairs(",".join(PAIRS[s])))
    if len(pairs) != 1 or pairs[0] not in allowed:
        return f"set {s} runs one of the pairs {','.join(PAIRS[s])} per invocation"
    return None


class Role:
    """A pass-through estimator for one loop role: forced bins in, captures and G3 out."""

    def __init__(self, base, role: str, st: dict):
        self.base, self.role, self.st = base, role, st
        self.fits = 0

    @property
    def booster_(self):
        return getattr(self.base, "booster_", None)

    def get_params(self, deep: bool = True):
        return self.base.get_params(deep)

    def set_params(self, **params):
        self.base.set_params(**params)
        return self

    def fit(self, X, y, sample_weight=None):
        rec = self.st["roles"].setdefault(self.role, {"g3bc": []})
        if self.fits == 0:
            rec["fit"] = np.array(X, copy=True)
            rec["params"] = {k: v for k, v in self.base.get_params().items()
                             if k in ("max_bin", "forcedbins_filename", "num_threads", "random_state", "n_estimators",
                                      "num_leaves", "bin_construct_sample_cnt", "deterministic", "force_row_wise")}
            rec["g3a"] = G.g3a(X, self.base.get_params(), self.st["intended"][self.role], self.st.get("workdir"))
        self.base.fit(X, y, sample_weight=sample_weight)
        rec["g3bc"].append(G.g3bc(self.base.booster_.model_to_string(), self.st["intended"][self.role]))
        self.fits += 1
        return self

    def _scored(self, X):
        rec = self.st["roles"].setdefault(self.role, {"g3bc": []})
        if "scored" not in rec:
            rec["scored"] = np.array(X, copy=True)

    def predict_proba(self, X):
        self._scored(X)
        return self.base.predict_proba(X)

    def predict(self, X):
        self._scored(X)
        return self.base.predict(X)


@contextmanager
def install(mode: str, s: str | None, edges: Path, workdir: Path | None = None):
    """Rebind for one invocation; restore on exit. mode is "prep" or "run"."""
    here = sha256_path(Path(__file__).resolve())
    st: dict = {"checked": False, "roles": {}, "workdir": workdir}
    saved = {"jittered": s5p_numerics.jittered, "unfold_one": s5p_numerics.unfold_one,
             "make_estimators": onc.make_estimators, "refine_params": s5n_pseudo.refine_params,
             "recorded_classifier": s5n_pseudo.recorded_classifier, "write_product": s5n_pseudo.write_product,
             "parse_args": argparse.ArgumentParser.parse_args}
    o = dict(saved)
    if mode == "run":
        index = json.loads((Path(edges) / "INDEX.json").read_text())
        cfg = index["sets"][s]
        files = {r: Path(edges) / cfg["roles"][r]["file"] for r in E.ROLES}
        for r, p in files.items():
            if sha256_path(p) != cfg["roles"][r]["sha256"]:
                raise Refusal(f"the {s} edge file of {r} is not the one INDEX.json records")
        st["intended"] = {r: E.load_intended(Path(edges) / "INDEX.json", s, r) for r in E.ROLES}
        st["index_sha256"] = sha256_path(Path(edges) / "INDEX.json")
        forced = {r: {"forcedbins_filename": str(files[r].resolve()), "max_bin": int(cfg["max_bin"])} for r in E.ROLES}

    def jittered(inputs, bkg, seed):
        st["seed"], st["inputs"], st["bkg"] = seed, inputs, bkg
        out = o["jittered"](inputs, bkg, seed)
        st["sources"] = out
        return out

    def unfold_one(exp, dtype, seed, threads, iters, unfold_fn=None):
        base_exp = st.get("base_exp")
        j = st.get("seed")
        a = st["ns"]
        ratio = json.loads(Path(a.eavail_ratio).read_text())
        split_key = s5c_pseudo.split_key_for(a.pseudo_seed)
        if j is None:
            base_exp = exp
        else:
            base_exp = s5n_pseudo.build_pseudo(st["inputs"], st["bkg"], a.truth, a.amplitude, split_key,
                                               a.pseudo_seed, ratio)[0]
        base = role_matrices(base_exp, np.float32)
        if mode == "prep":
            if j is not None:
                raise Refusal("the prep step runs the float32 base only")
            st["prep_index"] = E.build_edges(base, Path(st["edges_out"]))
            raise PrepDone()
        st["base_roles"] = base
        if j is not None:  # J1, J3 and the rebuilt selection for J2
            ji, jb = o["jittered"](st["inputs"], st["bkg"], j)
            si, sb = st["sources"]
            j1 = [G.j_compare(k, si[k], ji[k], base=False) for k in SOURCES] + \
                 [G.j_compare("bkg_reco", sb["bkg_reco"], jb["bkg_reco"], base=False)]
            edges_grid = st["inputs"]["edges"]
            j3 = {k: G.j3_moved(si[k], st["inputs"][k], edges_grid) for k in SOURCES}
            j3["bkg_reco"] = G.j3_moved(sb["bkg_reco"], st["bkg"]["bkg_reco"], edges_grid)
            rebuilt_exp = s5n_pseudo.build_pseudo(ji, jb, a.truth, a.amplitude, split_key, a.pseudo_seed, ratio)[0]
            st["j"] = {"j1": [x for x in j1 if x], "j3": j3}
            st["rebuilt_roles"] = role_matrices(rebuilt_exp, dtype)
        else:
            st["j"] = {"j1": [], "j3": None}
            st["rebuilt_roles"] = base
        return o["unfold_one"](exp, dtype, seed, threads, iters, unfold_fn)

    def make_estimators(kind, nvars, seed=None):
        ests = o["make_estimators"](kind, nvars, seed=seed)
        out = []
        for e, r in zip(ests, LOOP_ROLES):
            e.set_params(**forced[r])
            out.append(Role(e, r, st))
        return tuple(out)

    def refine_params(estimator_seed, threads):
        return {**o["refine_params"](estimator_seed, threads), **forced["ref"]}

    @contextmanager
    def recorded_classifier(u2d, record):
        with o["recorded_classifier"](u2d, record):
            inner = u2d._make_bkg_classifier

            def factory(estimator, params, device):
                clf = inner(estimator, params, device)
                fit0 = clf.fit

                def fit(X, y, sample_weight=None):
                    rec = st["roles"].setdefault("ref", {"g3bc": []})
                    rec["fit"] = np.array(X, copy=True)
                    rec["params"] = {k: v for k, v in clf.get_params().items() if k in ("max_bin", "forcedbins_filename")}
                    rec["g3a"] = G.g3a(X, clf.get_params(), st["intended"]["ref"], st.get("workdir"))
                    r = fit0(X, y, sample_weight=sample_weight)
                    rec["g3bc"].append(G.g3bc(clf.booster_.model_to_string(), st["intended"]["ref"]))
                    return r

                clf.fit = fit
                return clf

            u2d._make_bkg_classifier = factory
            try:
                yield
            finally:
                u2d._make_bkg_classifier = inner

    def gates() -> dict:
        base = st.get("seed") is None
        roles = st["roles"]
        received = {r: (roles[r].get("fit"), roles[r].get("scored") if r != "ref" else None) for r in E.ROLES if r in roles}
        rebuilt = {r: (st["rebuilt_roles"][r][0], st["rebuilt_roles"][r][1] if r != "ref" else None) for r in received}
        j2 = []
        for r, (fit, scored) in received.items():
            for name, a_, b_ in (("fit", fit, rebuilt[r][0]), ("scored", scored, rebuilt[r][1])):
                if a_ is None and b_ is None:
                    continue
                if a_ is None or b_ is None:
                    j2.append(f"{r}.{name}: captured {a_ is not None}, rebuilt {b_ is not None}")
                    continue
                why = G.j_compare(f"{r}.{name}", a_, b_, base=base)
                if why:
                    j2.append(why)
        jrec = st["j"]
        j3 = jrec["j3"]
        j3_bad = [] if j3 is None else [k for k, v in j3.items() if v["moved_off_edge"] == 0 or v["moved_on_edge"] != 0]
        missing_roles = sorted(set(E.ROLES) - set(roles))
        g2 = G.g2(received, {r: (st["base_roles"][r][0], st["base_roles"][r][1] if r != "ref" else None) for r in received},
                  st["intended"])
        ident = {}
        for r in E.ROLES:
            p = roles.get(r, {}).get("params", {})
            ok = (p.get("max_bin") == forced[r]["max_bin"] and p.get("forcedbins_filename") == forced[r]["forcedbins_filename"])
            ident[r] = {"params": p, "pass": bool(ok)}
        g3 = {r: {"g3a": roles[r].get("g3a"), "g3bc": roles[r]["g3bc"],
                  "pass": bool(roles[r].get("g3a", {}).get("pass")) and bool(roles[r]["g3bc"])
                  and all(x["pass"] for x in roles[r]["g3bc"])} for r in roles}
        return {"J": {"pass": not jrec["j1"] and not j2 and not j3_bad and not missing_roles,
                      "j1": jrec["j1"], "j2": j2, "j3": j3, "j3_failing": j3_bad, "missing_roles": missing_roles},
                "G2": g2,
                "G3": {"pass": not missing_roles and all(v["pass"] for v in g3.values()), "roles": g3},
                "identity": {"pass": not missing_roles and all(v["pass"] for v in ident.values()), "roles": ident}}

    def write_product(out, arrays, meta):
        if not st["checked"]:
            raise Refusal("refusing to write: the runner's arguments were never checked by PILOT-FB")
        rec = gates()
        block = {"schema": SCHEMA, "set": s, "jitter_seed": st.get("seed"), "edges_index_sha256": st["index_sha256"],
                 "code_sha256": {"fb_pilot_probe.py": here, "fb_pilot_edges.py": sha256_path(Path(E.__file__)),
                                 "fb_pilot_gates.py": sha256_path(Path(G.__file__))},
                 "gates_pass": {k: v["pass"] for k, v in rec.items()}}
        side = Path(out).with_name(Path(out).name[:-4] + ".pfb.json")
        tmp = side.with_name(side.name + f".partial-{os.getpid()}")
        tmp.write_text(json.dumps({**block, "gates": rec}, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x)))
        rc = o["write_product"](out, arrays, {**meta, "pilot_fb": block})
        if rc == 0:
            os.replace(tmp, side)
        else:
            tmp.unlink()
        st["roles"].clear()
        return rc

    def parse_args(self, args=None, namespace=None):
        ns = o["parse_args"](self, args, namespace)
        if hasattr(ns, "pairs") and hasattr(ns, "construction"):
            if mode == "prep":
                pairs = s5p_numerics.parse_pairs(getattr(ns, "pairs", ""))
                why = check_namespace(argparse.Namespace(**{**vars(ns), "pairs": "-:-"}), "E2") or \
                    (None if pairs == [(None, None)] else "the prep step runs the pair -:- only")
            else:
                why = check_namespace(ns, s)
            if why:
                print(f"refusing: {why}", file=sys.stderr)
                raise SystemExit(2)
            st["checked"], st["ns"] = True, ns
        return ns

    s5p_numerics.jittered, s5p_numerics.unfold_one = jittered, unfold_one
    argparse.ArgumentParser.parse_args = parse_args
    if mode == "run":
        onc.make_estimators, s5n_pseudo.refine_params = make_estimators, refine_params
        s5n_pseudo.recorded_classifier, s5n_pseudo.write_product = recorded_classifier, write_product
    try:
        yield st
    finally:
        s5p_numerics.jittered, s5p_numerics.unfold_one = saved["jittered"], saved["unfold_one"]
        onc.make_estimators, s5n_pseudo.refine_params = saved["make_estimators"], saved["refine_params"]
        s5n_pseudo.recorded_classifier, s5n_pseudo.write_product = saved["recorded_classifier"], saved["write_product"]
        argparse.ArgumentParser.parse_args = saved["parse_args"]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] not in (["prep"], ["run"]) or "--" not in argv:
        print("usage: fb_pilot_probe.py prep --edges-out DIR -- <args> | run --set S --edges DIR -- <args>", file=sys.stderr)
        return 2
    cut = argv.index("--")
    ap = argparse.ArgumentParser(prog=f"fb_pilot_probe.py {argv[0]}", allow_abbrev=False)
    if argv[0] == "prep":
        ap.add_argument("--edges-out", type=Path, required=True)
    else:
        ap.add_argument("--set", choices=sorted(PAIRS), required=True)
        ap.add_argument("--edges", type=Path, required=True)
    ap.add_argument("--workdir", type=Path, default=None, help="where G3 (a)'s dataset dump is written and removed")
    a = ap.parse_args(argv[1:cut])
    try:
        if argv[0] == "prep":
            if a.edges_out.exists():
                print(f"refusing: {a.edges_out} exists", file=sys.stderr)
                return 2
            with install("prep", None, a.edges_out, a.workdir) as st:
                st["edges_out"] = a.edges_out
                try:
                    esp.main(["--candidate", "control", "stability", "--", *argv[cut + 1:]])
                except PrepDone:
                    print(json.dumps({"edges": str(a.edges_out), "index_sha256": sha256_path(a.edges_out / "INDEX.json")}))
                    return 0
                print("refusing: the prep step never reached the unfold", file=sys.stderr)
                return 5
        with install("run", a.set, a.edges, a.workdir):
            return esp.main(["--candidate", "control", "stability", "--", *argv[cut + 1:]])
    except E.Infeasible as exc:
        print(f"INFEASIBLE: {exc}", file=sys.stderr)
        return 6
    except Refusal as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())
