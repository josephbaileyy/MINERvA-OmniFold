#!/usr/bin/env python3
"""MP3-B preflight (login node, before GO): exercises mp3b_build / mp3b_eval code paths on FROZEN inputs and on
the phase-0 probe sample, writing NO file (stdout only). It prints control flags and A7's own frozen margins;
it prints no H cell-level quantity and no H gate verdict (the probe's sampling tests are run as code exercises
and their verdicts are suppressed).

  build: card_control (probe H .par vs production .par), converter_control (frozen supplement flat vs itself),
         gate_b1 on the probe H flat, rebuild_c12 (the B2 path on the frozen C12 product), h_sample 'main' on
         the probe H flat and h_sample 'supp' on the frozen C12 supplement flat (code exercise only).
  eval:  load_setup, frozen_reproduction (test_null vs joint-evaluate.json, robust nulls, Holm-with-determinacy),
         replay_identity_control (mu := mu_C12 must return the frozen T, claim p and decisions).

Usage (root_6_28): python3 mp3b_preflight.py build|eval --inputs INPUTS_DIR
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

PROBE = Path("/pscratch/sd/j/josephrb/measurement-paper/phase0/mp3/H")
S5P = "/pscratch/sd/j/josephrb/s5p-20260926"


def build():
    import mp3b_build as b
    ROOT = b.gfr.import_root()
    g5 = b.gfr.load_g5(b.gfr.DEFAULTS["gen5d_tree"])
    print("modules", {m.__name__: m.__file__ for m in (b, b.gfr, b.sup, g5)})
    cc = b.card_control(str(PROBE / "nuwro_H.root.par"), b.FROZEN_MAIN_PAR, 9101, 20000)
    print("card_control(probe H vs production) pass:", cc["pass"], cc["differing_keys"])
    cv = b.converter_control(ROOT, b.FROZEN_SUPP_FLAT, b.FROZEN_SUPP_FLAT)
    print("converter_control(self) pass:", cv["pass"], cv["n_entries"])
    b1 = b.gate_b1(ROOT, str(PROBE / "flat5d_H.root"), str(PROBE / "nuwro_H.root.txt"))
    print("gate_b1(probe H): dyn_cc", b1["dyn_counts_cc"], "hitnuc_cc", b1["hitnuc_counts_cc"], "pass", b1["pass"])
    z, _, _ = b.gfr.load_phi_t(b.FLUXFIX)
    rec, arrays, integ, _ = b.rebuild_c12(ROOT, g5, z)
    print("rebuild_c12 (B2 path on frozen C12):", json.dumps({
        "main": [rec["main"]["xsec"]["bitwise_equal"], rec["main"]["sumw2"]["bitwise_equal"], rec["main"]["nevt"]["bitwise_equal"]],
        "full": [rec["full"]["xsec"]["bitwise_equal"], rec["full"]["sumw2"]["bitwise_equal"], rec["full"]["nevt"]["bitwise_equal"]],
        "full_from_rebuilt_main": [rec["full_from_rebuilt_main"]["xsec"]["bitwise_equal"],
                                   rec["full_from_rebuilt_main"]["sumw2"]["bitwise_equal"]],
        "sampling_main_reproduced": rec["sampling_main_reproduced"]["identical"],
        "sampling_supp_reproduced": rec["sampling_supp_reproduced"]["identical"],
        "inputs_match_meta": rec["inputs"]["main_flats_match_frozen_meta"], "pass": rec["pass"]}))
    if not rec["sampling_main_reproduced"]["identical"] or not rec["sampling_supp_reproduced"]["identical"]:
        for k in ("sampling_main_reproduced", "sampling_supp_reproduced"):
            print(k, json.dumps(rec[k], default=float)[:3000])
    for which, flat in (("main", str(PROBE / "flat5d_H.root")), ("supp", b.FROZEN_SUPP_FLAT)):
        chk, (x, v, n) = b.h_sample(ROOT, g5, z, flat, which)
        print(f"h_sample({which}) code exercise: keys", sorted(chk)[:6], "...; arrays finite:",
              bool(np.all(np.isfinite(x)) and np.all(np.isfinite(v))), "shape", x.shape,
              "populations", [s["population"] for s in chk["sampling_model_H1_proxy_PRIMARY"]], "(verdicts suppressed)")


def evaluate(inputs: Path):
    import mp3b_eval as e
    a = SimpleNamespace(design=inputs / "design.json", s5c_contract=inputs / "s5c_contract.json",
                        v=Path(f"{S5P}/stage3/V/V-s3v.npz"), frozen_eval=inputs / "joint-evaluate.json")
    print("modules", {m.__name__: m.__file__ for m in (e, e.si, e.sj, e.s1)})
    st = e.load_setup(a)
    fr = e.frozen_reproduction(st)
    print("frozen_reproduction controls:", json.dumps(fr["controls"]))
    ic = e.replay_identity_control(st, fr)
    print("replay_identity_control:", json.dumps(ic))
    o = e.replay_one(st, fr, st["mu_C"], st["var_C"])
    print("A7 frozen NuWro (from the identity replay): T", o["T"], "in_null_sd", json.dumps(o["in_null_sd"]),
          "critical", json.dumps(o["critical"]))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "build":
        build()
    else:
        evaluate(Path(sys.argv[sys.argv.index("--inputs") + 1]))
