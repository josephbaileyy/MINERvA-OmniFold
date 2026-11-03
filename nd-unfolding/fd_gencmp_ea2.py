#!/usr/bin/env python3
"""GENCMP amendment E, addendum E-A2 (FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2.md): the corner "CH, analysis definitions"
figures redrawn from amendment E's committed E-1 with-arm readouts, with the two hydrogen flags off the legend.

    fd_gencmp_ea2.py --out-dir <dir>      (login node, 0 node-h; from a fresh clone at the bound commit)

It runs, from committed bytes only:
* the chain's own figure entry (fd_gencmp_e.BOOT: fd_g_figures.run with the committed pins file
  rerun1/chain/pins/chdefs-with-figures.json and the committed prediction set rerun1/chain/pins/predictions-chdefs.json),
  with the committed sidecar's argv but for the paths, into <dir>;
* fd_g_figures_check.py --prediction-set gencmp-chdefs on <dir>;
* control D: each new sidecar against amendment E's committed one (rerun1/chain/chdefs/with/figures). Everything is
  equal but argv, code, versions, the PDF's digest and bytes, and the text of the items drawn from a prediction's label;
  each of those texts equals the committed text with the two hydrogen flags removed, and at least one such text changed.

Every input is required at its committed digest before anything runs; the out-dir must not exist. Exit 0 only if all
three pass; a refusal writes nothing.

MEASURES: nothing new; the figures redraw committed readouts. CANNOT AUTHORIZE: a paper or caption edit (the paper
lane's), any readout or covariance change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
DEPLOY = _ND.parent
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
CHAIN = f"{FD}/fd/gencmp-e/rerun1/chain"
READOUT = f"{CHAIN}/chdefs/with/readout"
COMMITTED_FIGS = f"{CHAIN}/chdefs/with/figures"
PINS_FILE = f"{CHAIN}/pins/chdefs-with-figures.json"
PREDS_FILE = f"{CHAIN}/pins/predictions-chdefs.json"
F0B = f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json"
DEFINITION = "nd-unfolding/pv-ladder/readouts/h2_definition.json"
FIG_NAMES = ("fd_g_fig_ratio", "fd_g_fig_modes", "fd_g_fig_sens")
HYDROGEN = ("; hydrogen: supplement FLAGGED", "; hydrogen: closure B3 failed")
SIDECAR_FREE = ("argv", "code", "versions", "pdf_sha256", "pdf_bytes", "file")
INPUT_ARGS = (("--g-readout", f"{READOUT}/fd_g_readout.json", "g_readout"),
              ("--g-diag-readout", f"{READOUT}/fd_g_diag_readout.json", "g_diag_readout"),
              ("--g-followup-readout", f"{READOUT}/fd_g_followup_readout.json", "g_followup_readout"),
              ("--g-sens2-readout", f"{READOUT}/fd_g_sens2_readout.json", "g_sens2_readout"),
              ("--f0b-readout", F0B, "f0b_readout"),
              ("--definition", DEFINITION, "definition"))


class Refuse(Exception):
    pass


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def label_item(it: dict) -> bool:
    return any(s.endswith("].label") and "predictions[name=" in s for s in it.get("source") or [])


def control_d(old: dict, new: dict) -> tuple[list[str], int]:
    """Control D on one sidecar: the list of differences that are not allowed (empty means it holds)."""
    bad = []
    for k in sorted(set(old) | set(new)):
        if k in SIDECAR_FREE or k == "plotted":
            continue
        if old.get(k) != new.get(k):
            bad.append(f"/{k}")
    po, pn = old.get("plotted", {}), new.get("plotted", {})
    for k in sorted(set(po) | set(pn)):
        if k != "items" and po.get(k) != pn.get(k):
            bad.append(f"/plotted/{k}")
    io, inew = po.get("items", []), pn.get("items", [])
    if len(io) != len(inew):
        return bad + [f"/plotted/items: {len(io)} vs {len(inew)}"], 0
    changed = 0
    for i, (a, b) in enumerate(zip(io, inew)):
        if label_item(a):
            want = a.get("text")
            for h in HYDROGEN:
                want = want.replace(h, "") if isinstance(want, str) else want
            if b.get("text") != want:
                bad.append(f"/plotted/items[{i}]/text: {b.get('text')!r} != {want!r}")
            if any(h in str(b.get("text")) for h in HYDROGEN):
                bad.append(f"/plotted/items[{i}]/text still carries a hydrogen flag")
            changed += a.get("text") != b.get("text")
            a, b = {k: v for k, v in a.items() if k != "text"}, {k: v for k, v in b.items() if k != "text"}
        if a != b:
            bad.append(f"/plotted/items[{i}] ({a.get('gid')})")
    return bad, changed


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--deploy", type=Path, default=DEPLOY)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    D = a.deploy
    try:
        if a.out_dir.exists():
            raise Refuse(f"{a.out_dir} exists")
        pins = json.loads((D / PINS_FILE).read_text())
        committed = {n: json.loads((D / COMMITTED_FIGS / f"{n}.json").read_text()) for n in FIG_NAMES}
        want_inputs = committed["fd_g_fig_ratio"]["inputs_sha256"]
        for flag, rel, key in INPUT_ARGS:
            got = sha256(D / rel)
            if got != pins.get(key) or got != want_inputs.get(key):
                raise Refuse(f"{rel}: sha256 {got} is not the committed figure step's {key}")
        old_argv = committed["fd_g_fig_ratio"]["argv"][1:]
        argv_new = []
        i = 0
        paths = {flag: str(D / rel) for flag, rel, _ in INPUT_ARGS}
        while i < len(old_argv):
            x = old_argv[i]
            if x in paths:
                argv_new += [x, paths[x]]
                i += 2
            elif x == "--out-dir":
                argv_new += [x, str(a.out_dir)]
                i += 2
            else:
                argv_new.append(x)
                i += 1
        if argv_new.count("--prediction-set") != 1 or argv_new[argv_new.index("--prediction-set") + 1] != "gencmp-chdefs":
            raise Refuse("the committed figure step is not the gencmp-chdefs set")
        sys.path.insert(0, str(_ND))
        import fd_gencmp_e as E
    except (Refuse, OSError, KeyError, ValueError) as e:
        print(f"[E-A2] refusing: {e}", file=sys.stderr, flush=True)
        return 2
    rc = subprocess.run([sys.executable, "-I", "-B", "-c", E.BOOT, str(_ND), "fd_g_figures", str(D / PINS_FILE),
                         str(D / PREDS_FILE), json.dumps(argv_new)]).returncode
    if rc != 0:
        print(f"[E-A2] fd_g_figures exited {rc}", file=sys.stderr, flush=True)
        return 1
    chk = [sys.executable, "-I", "-B", str(_ND / "fd_g_figures_check.py"),
           *[x for flag, rel, _ in INPUT_ARGS for x in (flag, str(D / rel))],
           "--figures-dir", str(a.out_dir), "--prediction-set", "gencmp-chdefs"]
    rc = subprocess.run(chk).returncode
    if rc != 0:
        print(f"[E-A2] fd_g_figures_check exited {rc}", file=sys.stderr, flush=True)
        return 1
    report, ok = {}, True
    for n in FIG_NAMES:
        new = json.loads((a.out_dir / f"{n}.json").read_text())
        bad, changed = control_d(committed[n], new)
        report[n] = {"pass": not bad and changed > 0, "label_texts_changed": changed, "differences": bad[:40]}
        ok = ok and report[n]["pass"]
    out = {"schema": "fd-gencmp-ea2-control-d/1", "pass": ok, "figures": report,
           "committed_sidecars": {n: sha256(D / COMMITTED_FIGS / f"{n}.json") for n in FIG_NAMES},
           "new_sidecars": {n: sha256(a.out_dir / f"{n}.json") for n in FIG_NAMES},
           "code_sha256": {p.name: sha256(p) for p in (Path(__file__).resolve(), _ND / "fd_g_figures.py",
                                                        _ND / "fd_g_figures_check.py", _ND / "fd_gencmp_e.py")}}
    (a.out_dir / "control_d.json").write_text(json.dumps(out, indent=1) + "\n")
    for n, r in report.items():
        print(f"[E-A2] control D {n}: {'PASS' if r['pass'] else 'FAIL'} ({r['label_texts_changed']} label texts changed)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
