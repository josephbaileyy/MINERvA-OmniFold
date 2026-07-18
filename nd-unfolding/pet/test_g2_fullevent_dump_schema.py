#!/usr/bin/env python3
"""Static source-regression guard for the G2 full-event PET dump contract.

Scope: this test scans the C++ SOURCE of the OmniFold event loop and its
CVUniverse getters. It is login-node safe -- it imports no ROOT, builds
nothing, and runs no event loop. It therefore does NOT prove ROOT runtime
correctness (branch existence at read time, POT, selection, alignment). It only
fails-closed if a required gated branch declaration/fill, the identity caching,
the parallel-vector clearing, the schema/provenance metadata, or a default-path
gate DISAPPEARS, and it fails on the forbidden truth-detector counterparts and
truth<->reco feature leakage.

Run: python3 test_fullevent_dump_schema.py   (exit 0 = pass, 1 = fail)
"""
import re
import sys
from pathlib import Path

_REL = Path("MINERvA101/MINERvA-101-Cross-Section")


def _find_ana():
    here = Path(__file__).resolve()
    for base in [here.parent, *here.parents]:
        cand = base / _REL / "runEventLoopOmniFold.cpp"
        if cand.exists():
            return base / _REL
    raise SystemExit("could not locate MINERvA101/MINERvA-101-Cross-Section from "
                     f"{__file__}")


ANA = _find_ana()
CPP = ANA / "runEventLoopOmniFold.cpp"
CVU = ANA / "event" / "CVUniverse.h"

_fail = []
_npass = 0


def check(cond, msg):
    global _npass
    if cond:
        _npass += 1
    else:
        _fail.append(msg)


def count(text, needle):
    return text.count(needle)


def strip_comments(text):
    """Blank out C++ // and /* */ comments (preserving newlines and string
    literals) so contract checks only see CODE, never explanatory prose that
    happens to name a branch/getter."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':  # string literal -- copy verbatim (respect \" escapes)
            out.append(c)
            i += 1
            while i < n:
                out.append(text[i])
                if text[i] == "\\" and i + 1 < n:
                    out.append(text[i + 1])
                    i += 2
                    continue
                if text[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            out.append("  ")
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def gate_spans(text):
    """Character ranges of every block controlled by `if(dumpPC)`/`if(dumpPointcloud)`.

    Handles both `if(dumpPC){` and `if(dumpPointcloud)\n{` styles by locating the
    first `{` after the matched header and brace-matching to its close.
    """
    spans = []
    for m in re.finditer(r"if\s*\(\s*(?:dumpPC|dumpPointcloud)\s*\)", text):
        j = text.find("{", m.end())
        if j < 0:
            continue
        depth = 0
        k = j
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        spans.append((m.start(), k))
    return spans


def in_a_gate(spans, off):
    return any(a <= off <= b for a, b in spans)


def function_body(text, signature_substr):
    """Return the {...} body of the first function whose header contains
    `signature_substr`."""
    i = text.find(signature_substr)
    assert i >= 0, f"function marker not found: {signature_substr}"
    j = text.find("{", i)
    depth = 0
    k = j
    while k < len(text):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j:k + 1]
        k += 1
    raise AssertionError(f"unterminated body for {signature_substr}")


def main():
    cpp = strip_comments(CPP.read_text())
    cvu = strip_comments(CVU.read_text())
    spans = gate_spans(cpp)

    # ---- 1. Required gated branch declarations, with expected multiplicity ----
    #  reco-schema families appear on {mc_signal_reco, mc_background, data} = 3;
    #  truth-schema families appear on {mc_truth_denom, mc_signal_reco} = 2.
    expected = {
        'out->Branch("mu_reco_px"': 3,
        'out->Branch("mu_reco_py"': 3,
        'out->Branch("mu_reco_pz"': 3,
        'out->Branch("mu_reco_E"': 3,
        'out->Branch("mu_reco_phi"': 3,
        'out->Branch("mu_reco_qp"': 3,
        'out->Branch("mu_reco_minos_ok"': 3,
        'out->Branch("vtx_reco_x"': 3,
        'out->Branch("vtx_reco_y"': 3,
        'out->Branch("vtx_reco_z"': 3,
        'out->Branch("part_reco_view"': 3,
        'out->Branch("part_reco_time"': 3,
        'out->Branch("mu_true_px"': 2,
        'out->Branch("mu_true_py"': 2,
        'out->Branch("mu_true_pz"': 2,
        'out->Branch("mu_true_E"': 2,
        'out->Branch("mu_true_phi"': 2,
        'out->Branch("vtx_true_x"': 2,
        'out->Branch("vtx_true_y"': 2,
        'out->Branch("vtx_true_z"': 2,
        'out->Branch("mc_run"': 3,        # truth-denom, signal, background (MC id)
        'out->Branch("mc_subrun"': 3,
        'out->Branch("mc_nthEvtInFile"': 3,
        'out->Branch("ev_run"': 1,        # data-only real identity
        'out->Branch("ev_subrun"': 1,
        'out->Branch("ev_gate"': 1,
    }
    for needle, n in expected.items():
        check(count(cpp, needle) == n,
              f"branch {needle!r}: expected {n} declaration(s), found {count(cpp, needle)}")

    # ---- 2. Default-path guard: EVERY new-schema branch decl is inside a
    #         dumpPC/dumpPointcloud gate span (never created on the default path).
    for m in re.finditer(r'out->Branch\("([A-Za-z0-9_]+)"', cpp):
        name = m.group(1)
        if name in ("mu_reco_px", "mu_reco_py", "mu_reco_pz", "mu_reco_E",
                    "mu_reco_phi", "mu_reco_qp", "mu_reco_minos_ok",
                    "vtx_reco_x", "vtx_reco_y", "vtx_reco_z",
                    "part_reco_view", "part_reco_time",
                    "mu_true_px", "mu_true_py", "mu_true_pz", "mu_true_E",
                    "mu_true_phi", "vtx_true_x", "vtx_true_y", "vtx_true_z",
                    "mc_run", "mc_subrun", "mc_nthEvtInFile",
                    "ev_run", "ev_subrun", "ev_gate"):
            check(in_a_gate(spans, m.start()),
                  f"full-event branch {name!r} is declared OUTSIDE a dumpPC gate")

    # Original (default-schema) branches must still exist unconditionally.
    for needle in ('out->Branch("MC"', 'out->Branch("sim"', 'out->Branch("w_bkg"',
                   'out->Branch("measured"', 'out->Branch("w_truth"'):
        check(count(cpp, needle) >= 1, f"default branch {needle!r} missing")

    # ---- 3. Provenance metadata (hadd-safe: TNamed + TParameter<int>,'f') ----
    check(re.search(r'TNamed\(\s*"petSchemaVersion"', cpp) is not None,
          "petSchemaVersion TNamed missing")
    check(re.search(r'TNamed\(\s*"petFeatureFamilies"', cpp) is not None,
          "petFeatureFamilies TNamed missing")
    check(re.search(r'TParameter<int>\("hasFullEventSchema",\s*1,\s*\'f\'\)', cpp) is not None,
          "hasFullEventSchema must be TParameter<int> with 'f' (first) merge mode")
    check(re.search(r'TParameter<int>\("fullPhaseSpace",[^;]*\'f\'\)', cpp) is not None,
          "fullPhaseSpace must be TParameter<int> with 'f' merge mode")
    # metadata block must itself be gated.
    m = re.search(r'TNamed\("petSchemaVersion"', cpp)
    check(in_a_gate(spans, m.start()), "petSchemaVersion metadata is not dumpPointcloud-gated")

    # ---- 4. CVUniverse: 5-arg GetRecoClusters overload, equal-length by design;
    #         3-arg overload preserved. ----
    five = re.search(
        r"GetRecoClusters\(std::vector<double>&\s*E,\s*std::vector<double>&\s*pos,\s*"
        r"std::vector<double>&\s*z,\s*std::vector<int>&\s*view,\s*"
        r"std::vector<double>&\s*time\)\s*const\s*\{",
        cvu)
    check(five is not None, "5-arg GetRecoClusters(E,pos,z,view,time) overload missing")
    if five:
        body = function_body(cvu, five.group(0)[:-1])
        for v in ("E", "pos", "z", "view", "time"):
            check(f"{v}.clear()" in body, f"5-arg GetRecoClusters does not clear {v}")
            check(f"{v}.push_back(" in body, f"5-arg GetRecoClusters does not fill {v}")
        check(body.count("push_back(") == 5,
              "5-arg GetRecoClusters must push each of E,pos,z,view,time exactly once/cluster")
    check("std::vector<double>& z) const {" in cvu,
          "3-arg GetRecoClusters(E,pos,z) overload was not preserved")

    # ---- 5. Miss-append: identity caching, parallel-vector clearing, no leak ----
    miss = function_body(cpp, "long AppendTruthOnlyMisses(")
    for nm in ("part_reco_view", "part_reco_time", "mu_reco_px", "mu_reco_minos_ok",
               "vtx_reco_z", "mu_true_px", "mu_true_phi", "vtx_true_z",
               "mc_run", "mc_subrun", "mc_nthEvtInFile"):
        check(f'SetBranchAddress("{nm}"' in miss,
              f"AppendTruthOnlyMisses does not rebind {nm!r} (would dangle / be #12-mangled)")
    for nm in ('"part_reco_view"', '"part_reco_time"', '"mu_true_px"', '"vtx_true_z"',
               '"mc_run"', '"mc_nthEvtInFile"', '"mu_reco_minos_ok"'):
        check(nm in cpp[cpp.find("explicitNames"):cpp.find("explicitNames") + 1400],
              f"{nm} missing from the explicitNames exclusion set")
    check("miss_id_run = tde.id_run" in miss, "miss row does not carry cached truth identity id_run")
    check("miss_mu_true_px = tde.mu_true_px" in miss, "miss row does not carry cached truth muon")
    # Parallel reco view/time vectors must stay EMPTY on a native miss.
    check(not re.search(r"e_reco_view\.(assign|push_back)", miss),
          "AppendTruthOnlyMisses must leave part_reco_view empty on misses")
    check(not re.search(r"e_reco_time\.(assign|push_back)", miss),
          "AppendTruthOnlyMisses must leave part_reco_time empty on misses")

    # ---- 6. Negative: NO forbidden truth detector counterpart branch ----
    for bad in ("mu_true_qp", "mu_true_minos", "mu_true_ok", "mu_true_range",
                "mu_true_charge", "part_gen_view", "part_gen_time",
                "vtx_true_minos"):
        check(bad not in cpp, f"forbidden truth-detector counterpart branch present: {bad}")

    # ---- 7. Truth<->reco leakage guards ----
    #  truth-muon helper must use ONLY truth accessors (incl. GetPhilepTrue, NOT
    #  the reco GetPhimu), and no reco detector getters.
    tmk = function_body(cpp, "inline TruthMuonKin GetTruthMuonKin(")
    for g in ("GetPlepTrue", "GetThetalepTrue", "GetPhilepTrue", "GetElepTrue"):
        check(g in tmk, f"GetTruthMuonKin must source truth muon via {g}")
    for bad in ("GetPhimu", "GetMuon4V", "GetMuonQP", "IsMinosMatchMuon"):
        check(bad not in tmk, f"GetTruthMuonKin leaks reco getter {bad} into the truth muon")

    #  no line may assign a mu_true_* / vtx_true_* branch from a reco getter.
    reco_getters = ("GetMuon4V", "GetPhimu", "GetMuonQP", "IsMinosMatchMuon", "GetVertex()")
    for line in cpp.splitlines():
        if re.search(r"\b(mu_true_|vtx_true_)\w*\s*=", line):
            for g in reco_getters:
                check(g not in line, f"truth field assigned from reco getter {g}: {line.strip()!r}")

    #  no line may assign a mu_reco_* / vtx_reco_* branch from a truth getter.
    truth_getters = ("GetPlepTrue", "GetElepTrue", "GetPhilepTrue", "GetThetalepTrue",
                     "GetTrueVertex", "GetTruthMuonKin", "tk.")
    for line in cpp.splitlines():
        if re.search(r"\b(mu_reco_|vtx_reco_)\w*\s*=", line):
            for g in truth_getters:
                check(g not in line, f"reco field assigned from truth getter {g}: {line.strip()!r}")

    # ---- 8. Data schema has NO truth side and NO mc_* identity ----
    data_body = function_body(cpp, "void LoopAndFillUnbinnedData(")
    for bad in ("mu_true_", "vtx_true_", 'Branch("mc_run"', "GetTruthFSHadrons",
                "part_gen_"):
        check(bad not in data_body, f"data schema must not carry truth field {bad}")
    check('Branch("ev_run"' in data_body, "data schema must carry real ev_run identity")

    # ---- 9. Reco muon is sentinel on !pass_reco in the signal loop ----
    sig_body = function_body(cpp, "void LoopAndFillUnbinnedMCSelectedSignalReco(")
    check("if(passesReco)" in sig_body and "mu_reco_px = mu_reco_py = mu_reco_pz = mu_reco_E = -9999.0"
          in sig_body,
          "signal reco muon must be sentinel -9999 on !pass_reco rows")

    # ---- report ----
    if _fail:
        print(f"FAIL: {len(_fail)} check(s) failed ({_npass} passed):")
        for f in _fail:
            print(f"  - {f}")
        return 1
    print(f"PASS: {_npass} static full-event-dump contract checks passed.")
    print("NOTE: source-only; does not prove ROOT runtime correctness "
          "(branch existence at read, POT, selection, alignment).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
