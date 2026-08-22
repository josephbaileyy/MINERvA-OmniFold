#!/usr/bin/env python3
"""Clause (c) RERUN: manufacture ONE defect in a STAMPED product, by rebuilding it key by key.

WHY REBUILD RATHER THAN REOPEN UPDATE. ROOT APPENDS A SECOND CYCLE rather than replacing a key, which
would leave two answers to one question in the artifact -- the exact thing `_stamp_output`'s
double-stamp refusal exists to prevent. A mutated fixture carrying both the original and the mutation
would not be a manufactured defect, it would be a different defect. So every key is copied forward and
the targeted one is written in its place, once.

EVERY MUTATION HERE IS APPLIED AFTER the wrapper has finished, so it models CORRUPTION OF A FINISHED
PRODUCT rather than a wrapper bug. That is the direction the gate is supposed to act in.
"""
import argparse
import numpy as np

INT_KEYS_PARSE = lambda s: (s.split("=", 1)[0], int(s.split("=", 1)[1]))
BIN_PARSE = lambda s: (s.split("=", 1)[0].split("@")[0], int(s.split("=", 1)[0].split("@")[1]),
                       float(s.split("=", 1)[1]))


# WHY `del` AND NEVER `.Delete()` ON A HISTOGRAM THIS FILE CREATED.
# Measured on ROOT 6.28/12 / python 3.11.14: Delete() frees the C++ object while the Python proxy
# still holds it, and cppyy frees it AGAIN at dealloc -- SIGSEGV inside op_dealloc_nofree.
# `read_keys_pyroot` calls Delete() safely because its objects come from `key.ReadObj()`, which is a
# DIFFERENT ownership. `ROOT.TH1.AddDirectory(False)` puts ownership in Python, so plain `del`
# releases the buffer immediately by refcount -- which is what keeps peak memory at ONE live
# 915 MB TH2D without the double free.


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--set-int", action="append", default=[], metavar="KEY=VALUE",
                    help="replace a TParameter(int) value")
    ap.add_argument("--drop", action="append", default=[], metavar="KEY",
                    help="omit a key entirely")
    ap.add_argument("--set-bin", action="append", default=[], metavar="HIST@I=VALUE",
                    help="set 1-D histogram bin I (0-based) to VALUE")
    ap.add_argument("--scale-bin", action="append", default=[], metavar="HIST@I=FACTOR",
                    help="multiply 1-D histogram bin I (0-based) by FACTOR. EXISTS SO NO VALUE EVER "
                         "ROUND-TRIPS THROUGH THE SHELL: reading a bin out with `python3 -c` and "
                         "piping it back in silently produced an EMPTY argument in rehearsal, and an "
                         "empty argument makes a mutation that did not happen look like one that did.")
    ap.add_argument("--pad-bins", action="append", default=[], metavar="HIST=DELTA",
                    help="rewrite a 1-D histogram with DELTA more (positive) or fewer (negative) "
                         "bins; added bins are 0.0, dropped bins come off the end")
    a = ap.parse_args()
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.TH1.AddDirectory(False)

    set_int = dict(INT_KEYS_PARSE(s) for s in a.set_int)
    drop = set(a.drop)
    set_bin, scale_bin = {}, {}
    for s in a.set_bin:
        h, i, v = BIN_PARSE(s)
        set_bin.setdefault(h, []).append((i, v))
    for s in a.scale_bin:
        h, i, v = BIN_PARSE(s)
        scale_bin.setdefault(h, []).append((i, v))
    pad = dict((s.split("=", 1)[0], int(s.split("=", 1)[1])) for s in a.pad_bins)

    fin = ROOT.TFile.Open(a.src)
    if not fin or fin.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {a.src}")
    fout = ROOT.TFile.Open(a.out, "RECREATE")
    seen, applied = [], []
    for key in fin.GetListOfKeys():
        name = key.GetName()
        seen.append(name)
        if name in drop:
            applied.append(f"DROPPED {name}")
            continue
        obj = key.ReadObj()
        fout.cd()
        if name in set_int:
            ROOT.TParameter("int")(name, int(set_int[name])).Write()
            applied.append(f"SET {name} = {set_int[name]}")
        elif name in set_bin or name in pad or name in scale_bin:
            nb = obj.GetNbinsX()
            arr = np.array([obj.GetBinContent(i + 1) for i in range(nb)], dtype=np.float64)
            if name in pad:
                d = pad[name]
                arr = (np.concatenate([arr, np.zeros(d)]) if d > 0 else arr[:d])
                applied.append(f"RESIZED {name} {nb} -> {arr.size}")
            for i, v in set_bin.get(name, []):
                old = arr[i]
                arr[i] = v
                applied.append(f"SET {name}[{i}] {old!r} -> {v!r}")
            for i, fac in scale_bin.get(name, []):
                old = arr[i]
                arr[i] = old * fac
                if arr[i] == old:
                    raise SystemExit(f"[FAIL] scaling {name}[{i}] by {fac} did NOT change it "
                                     f"({old!r}); a control that mutates nothing reports the refusal "
                                     "it was built to test as absent")
                applied.append(f"SCALED {name}[{i}] {old!r} x{fac} -> {arr[i]!r}")
            h = ROOT.TH1D(name, obj.GetTitle(), arr.size, 0, arr.size)
            for i, v in enumerate(arr):
                h.SetBinContent(i + 1, float(v))
            h.Write(name)
            del h
        else:
            obj.Write(name)
        del obj
    fout.Close()
    fin.Close()
    unknown = (set(set_int) | drop | set(set_bin) | set(pad) | set(scale_bin)) - set(seen)
    if unknown:
        # FAIL CLOSED ON A MUTATION THAT DID NOT LAND. A negative control that silently mutated
        # nothing is the worst possible arm: it reports the refusal it was built to test as absent.
        raise SystemExit(f"[FAIL] these keys are not in {a.src} so the mutation did NOT land: "
                         f"{sorted(unknown)}. Keys present: {sorted(seen)}")
    print(f"[mutate] {a.src} -> {a.out}")
    for l in applied:
        print(f"[mutate]   {l}")
    if not applied:
        raise SystemExit("[FAIL] no mutation was requested; refusing to emit an identical 'control'")


if __name__ == "__main__":
    main()
