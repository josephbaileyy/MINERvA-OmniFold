#!/usr/bin/env python3
"""Repo-wide sweep for GATES THAT CANNOT FAIL, with each detector proved to have power.

WHY THIS EXISTS. On 2026-08-07 two independent lanes filed the same defect class within hours:

    BEN-043 (PET)   EarlyStopping(patience=10) inside epochs=8 -- a guard whose trigger is unreachable,
                    so the saved checkpoint was never the trained model and extraction was blocked.
    BEN-044 (PET)   absolute tolerances (1e-30; -1e-9*max(eig,1.0)) against ~1e-80 quantities -- a
                    covariance gate that would bless an arbitrarily wrong matrix.
    BEN-046 (GBDT)  a runbook describing a gate as a checkpoint to pass when the gate tests only that
                    a variable is non-empty.

Plus, already in the ledger: BEN-023 (`[[ -s $OUT ]] && skip` -- existence read as completeness),
BEN-032/BEN-025 (a check run over a population that cannot exhibit the defect), BEN-039 (a stored INPUT
named like a measurement, so the datum could not disagree), BEN-040 (a fail-closed gate that had never
returned PASS on real input), BEN-042 (a normalised quantity compared against an absolute one, inverting
the verdict). Joseph's read, and I agree: five-plus instances across two lanes in one day is systemic, not
local, so the response should be a repo-wide detector rather than another per-lane list.

THE DETECTOR MUST ITSELF HAVE POWER, or it joins the list it is meant to find. Every real instance above
is now FIXED, so a sweep of the current tree cannot demonstrate the detectors work. `--power` therefore
runs each detector against a synthetic reconstruction of the pre-fix source and REQUIRES it to fire. The
sweep refuses to report anything if any detector fails its own power test.

CONFIDENCE IS LABELLED, because mixing certain and speculative hits is how a report becomes noise:
  DEFECT  the pattern is unsafe on its face (an unreachable trigger; a size-only completeness guard)
  REVIEW  the pattern is a strong smell that needs a human to confirm the scale or the intent

Static only: no imports of the audited code, no execution, so it is safe to run anywhere and cannot be
defeated by an import side effect.
"""
import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------------------------
# Detectors. Each returns a list of (severity, path, lineno, line, why).
# ---------------------------------------------------------------------------------------------

_TOL_CALL = re.compile(r"\bmax\s*\(\s*[^,()]+,\s*1(?:\.0+)?\s*\)")
_ABS_EPS = re.compile(r"[<>]=?\s*(-?)(\d(?:\.\d+)?)e-(\d+)\b")
_SIZE_GUARD = re.compile(r"\[\[?\s*-s\s+[\"']?\$")
_NONEMPTY_GUARD = re.compile(r"\[\[?\s*-[nz]\s+[\"']?\$\{?(\w+)")
_WEAK_BODY_NAME = re.compile(r"^\s*def\s+((?:assert|require|validate|check|ensure|verify)_\w+)\s*\(")
_STRONG_ASSERT = re.compile(r"\b(?:==|!=|<=|>=|array_equal|allclose|isclose|startswith|in\b|match)\b")
_WEAK_ONLY = re.compile(r"\b(?:isfinite|len|is not None|is None|shape|any|all|> 0|>= 0)\b")
_PATIENCE = re.compile(r"\bpatience\s*=\s*(\d+)")
_EPOCHS = re.compile(r"\bepochs?\s*=\s*(\d+)")
_TAUT_NAME = re.compile(
    r"^\s*(\w*(?:achieved|measured|class_ratio|_ratio|realized)\w*)\s*=\s*"
    r"(?:\w+)\.get\(|^\s*\w+\[[\"'](\w*(?:achieved|measured|class_ratio)\w*)[\"']\]\s*=\s*\w+\[")


_PY_DOC = re.compile(r"^\s*(\"\"\"|''')")


def strip_noncode(lines, is_python):
    """Blank comments and docstrings, PRESERVING line numbers.

    MENTION vs USE. Without this the sweep's loudest hits are the ledger prose and the regression tests
    that exist *because* of these defects: it flags a comment reading "EarlyStopping(patience=10) cannot
    fire inside epochs=8" as an instance of the very thing that sentence documents. This session already
    paid for that lesson once today, on a test that failed on its own rationale comment, so the fix is
    applied here rather than rediscovered -- `_executable_lines()` in
    test_pet_fullevent_nominal_launcher.py is the same idiom.
    """
    out = []
    doc_q = None
    for l in lines:
        if is_python:
            if doc_q is not None:
                if doc_q in l:
                    doc_q = None
                out.append("")
                continue
            m = _PY_DOC.match(l)
            if m:
                q = m.group(1)
                if l.count(q) == 1:
                    doc_q = q
                out.append("")
                continue
            out.append(re.sub(r"#.*", "", l))
        else:
            out.append("" if l.lstrip().startswith("#") else re.sub(r"\s#\s.*", "", l))
    return out


def d_unreachable_trigger(path, lines):
    """BEN-043: a guard whose firing condition cannot be met given the configured bound."""
    out = []
    # EarlyStopping ONLY. `ReduceLROnPlateau(patience=1000)` is a DELIBERATE no-op that pins the LR
    # (omnifold.py:263-265 documents it), so flagging it would be a false positive on purpose-built code.
    pats = [(i, int(m.group(1))) for i, l in enumerate(lines)
            for m in [_PATIENCE.search(l)] if m and "EarlyStopping" in l]
    eps = [int(m.group(1)) for l in lines for m in [_EPOCHS.search(l)] if m]
    if not pats or not eps:
        return out
    max_ep = max(eps)
    for i, p in pats:
        if p >= max_ep:
            out.append(("DEFECT", path, i + 1, lines[i].strip(),
                        f"patience={p} >= max epochs={max_ep} in this file: the stopper can never fire, "
                        f"so restore_best_weights never runs (BEN-043)"))
    return out


def d_absolute_floor_in_tolerance(path, lines):
    """BEN-044: `max(x, 1.0)` inside a tolerance pins it absolute exactly when the data is small."""
    out = []
    for i, l in enumerate(lines):
        # NO \b here: the real instance was `psd_ok = ... max(max_eig, 1.0)` and `psd_tol = ...`, and
        # `\btol\b` cannot match inside `psd_tol` because `_` is a word character. That bug made this
        # detector silent on its own power case -- caught by the power test, which is the point of it.
        if _TOL_CALL.search(l) and re.search(r"(tol|eps|atol|rtol|thresh|_ok|_min|_max|psd)", l, re.I):
            out.append(("DEFECT", path, i + 1, l.strip(),
                        "max(expr, 1.0) inside a tolerance converts it from relative to ABSOLUTE "
                        "whenever the quantity is < 1 (BEN-044)"))
    return out


def d_scale_blind_epsilon(path, lines):
    """BEN-044: a bare absolute epsilon in a file whose own numbers live many orders away."""
    out = []
    text = "\n".join(lines)
    small = [int(m.group(1)) for m in re.finditer(r"\de-(\d\d+)\b", text)]
    if not small:
        return out
    deepest = max(small)
    if deepest < 20:
        return out
    for i, l in enumerate(lines):
        for m in _ABS_EPS.finditer(l):
            exp = int(m.group(3))
            # An epsilon MULTIPLIED by a scale (`1e-12 * lmax`), or compared against a quotient
            # (`abs(a-b)/total`, `_relmax(...)`), is already relative and must not be flagged -- the
            # first pass reported 20 such lines and every one was a false positive. Only a BARE
            # absolute epsilon survives.
            tail = l[m.end():m.end() + 40]
            relative = (re.match(r"\s*[*/]", tail)
                        or re.search(r"(?:/\s*[\w\[\]\.\(\)]+|_?rel(?:max|ative|_)?|ratio|frac)"
                                     r"[^<>]*[<>]", l, re.I))
            if deepest - exp >= 15 and not relative:
                out.append(("REVIEW", path, i + 1, l.strip(),
                            f"absolute epsilon 1e-{exp} in a file containing 1e-{deepest} scales "
                            f"({deepest - exp} orders apart) -- confirm it is relative or rescale "
                            f"(BEN-044)"))
    return out


def d_size_only_completeness(path, lines):
    """BEN-023: existence/size read as completeness."""
    out = []
    for i, l in enumerate(lines):
        # Only the SKIP-on-success branch. `[[ -s F ]] || die` is the CORRECT direction -- it fails when
        # the file is absent -- and flagging it would invert the finding. And a line that ALSO calls a
        # content validator (`valid_root`, `valid_merged`, `rg_*`, a sha) is the REPAIRED BEN-023 pattern,
        # size AND content, which is what the ledger prescribes; that must not be reported as the defect.
        if not _SIZE_GUARD.search(l):
            continue
        skips = (re.search(r"&&.*\b(skip|exit 0|continue|return 0)\b", l, re.I)
                 or re.search(r"\bthen\b.*\bskip\b", l, re.I))
        validates = re.search(r"\b(valid_\w+|rg_\w+|sha256|verify_\w+)\b", l)
        if skips and not validates:
            out.append(("DEFECT", path, i + 1, l.strip(),
                        "`-s FILE` treated as proof of completeness with nothing checking content; a "
                        "truncated file passes (BEN-023) -- validate content or temp+rename"))
    return out


def d_nonemptiness_gate(path, lines):
    """BEN-046: a gate that tests only that a variable is set."""
    out = []
    for i, l in enumerate(lines):
        m = _NONEMPTY_GUARD.search(l)
        if not m:
            continue
        var = m.group(1)
        # NO \b: the real instance is `P4_VERIFIER_PASS`, where `_PASS` has no word boundary before it.
        if re.search(r"(PASS|APPROV|CONFIRM|VERIF|_OK|GATE|AUTH)", var, re.I):
            out.append(("DEFECT", path, i + 1, l.strip(),
                        f"gate keyed on whether ${var} is merely NON-EMPTY: setting it to any string "
                        f"defeats the checkpoint rather than passing it (BEN-046)"))
    return out


def d_strong_name_weak_body(path, lines):
    """Strong-name/weak-check: assert_*/validate_* whose body compares against nothing."""
    out = []
    for i, l in enumerate(lines):
        m = _WEAK_BODY_NAME.match(l)
        if not m:
            continue
        indent = len(l) - len(l.lstrip())
        body = []
        for j in range(i + 1, min(i + 40, len(lines))):
            nxt = lines[j]
            if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= indent and not nxt.lstrip().startswith("#"):
                break
            body.append(nxt)
        btxt = "\n".join(body)
        # strip docstrings and comments before judging
        btxt = re.sub(r'""".*?"""', "", btxt, flags=re.S)
        btxt = re.sub(r"#.*", "", btxt)
        if not btxt.strip():
            continue
        if not _STRONG_ASSERT.search(btxt) and _WEAK_ONLY.search(btxt):
            out.append(("REVIEW", path, i + 1, l.strip(),
                        f"`{m.group(1)}` asserts only finiteness/length/presence -- it never compares "
                        f"against an independent reference, so it cannot detect a WRONG value"))
    return out


def d_tautological_datum(path, lines):
    """BEN-039: a field named like an outcome, assigned from the input it is meant to validate."""
    out = []
    for i, l in enumerate(lines):
        m = _TAUT_NAME.match(l)
        if m:
            out.append(("REVIEW", path, i + 1, l.strip(),
                        "a field named like a MEASUREMENT assigned straight from an input: it cannot "
                        "disagree with that input, so it is not evidence (BEN-039)"))
    return out


DETECTORS = [
    ("unreachable-trigger", d_unreachable_trigger),
    ("absolute-floor-in-tolerance", d_absolute_floor_in_tolerance),
    ("scale-blind-epsilon", d_scale_blind_epsilon),
    ("size-only-completeness", d_size_only_completeness),
    ("nonemptiness-gate", d_nonemptiness_gate),
    ("strong-name-weak-body", d_strong_name_weak_body),
    ("tautological-datum", d_tautological_datum),
]

# ---------------------------------------------------------------------------------------------
# POWER TESTS: each detector must fire on a reconstruction of the real pre-fix source.
# Every string below is a paraphrase of code that actually shipped in this repo and was fixed.
# ---------------------------------------------------------------------------------------------
POWER = {
    "unreachable-trigger": ("omnifold.py (pre-BEN-043)", [
        "        self.EPOCHS = epochs",
        "        model_e.fit(train, epochs=8, callbacks=callbacks)",
        "        cb = EarlyStopping(patience=10, restore_best_weights=True)",
    ]),
    "absolute-floor-in-tolerance": ("combine_cstat_bkgsub_100rep.py (pre-BEN-044)", [
        "    psd_tol = -1e-9 * max(max_eig, 1.0)",
    ]),
    "scale-blind-epsilon": ("combine_cstat_bkgsub_100rep.py (pre-BEN-044)", [
        "    C = (Z.T @ Z) / (n - 1)   # entries ~ 8.13e-79, diagonal median 3.87e-86",
        "    if sym_err > 1e-30:",
        "        raise SystemExit('asymmetric')",
    ]),
    "size-only-completeness": ("uq launchers (pre-BEN-023)", [
        '  [[ -s "${OUT}" ]] && { echo "skip (exists)"; exit 0; }',
    ]),
    "nonemptiness-gate": ("run_p4_standard.sh (BEN-046)", [
        '  [[ -n "${P4_VERIFIER_PASS}" ]] || die "verifier gate not cleared"',
    ]),
    "strong-name-weak-body": ("a coverage guard of the weak kind", [
        "def assert_truth_denominator_coverage(comp):",
        "    if not np.all(np.isfinite(comp)):",
        "        raise SystemExit('non-finite')",
        "    return True",
    ]),
    "tautological-datum": ("train_fullevent_nominal.py (pre-BEN-039)", [
        '    class_ratio = target_meta.get("step1_class_ratio")',
    ]),
}


def run_power():
    print("=== POWER TEST: every detector must fire on the real pre-fix source ===")
    ok = True
    by_name = dict(DETECTORS)
    for name, (origin, lines) in POWER.items():
        hits = by_name[name]("<power:" + name + ">", lines)
        fired = len(hits) > 0
        ok &= fired
        print(f"  {name:30s} {'FIRES' if fired else '*** SILENT ***':16s} on {origin}")
        if not fired:
            print(f"      -> this detector cannot demonstrate power and the sweep is not trustworthy")
    print()
    return ok


def sweep(root, exts=(".py", ".sh")):
    findings = []
    n_files = 0
    skip_dirs = {".git", "__pycache__", "worktrees", "node_modules", ".pytest_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if not fn.endswith(exts):
                continue
            p = os.path.join(dirpath, fn)
            if os.path.islink(p):
                continue
            rel = os.path.relpath(p, root)
            if rel.split(os.sep)[0] == "orchestration":       # symlink alias of docs/orchestration
                continue
            if fn == os.path.basename(__file__):              # do not audit the auditor's own patterns
                continue
            try:
                lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
            except OSError:
                continue
            n_files += 1
            raw = lines
            lines = strip_noncode(lines, fn.endswith(".py"))
            for name, fn_d in DETECTORS:
                for sev, _pth, ln, _blanked, why in fn_d(rel, lines):
                    # report the RAW line so the operator sees real source, not the blanked copy
                    findings.append((sev, name, rel, ln, raw[ln - 1].strip(), why))
    return findings, n_files


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # THREE levels up, not two: this file is docs/orchestration/<me>, so two dirnames land on
    # `docs/` and the sweep silently examines 0 files while printing "0 hits" -- a clean bill of
    # health from a check that looked at nothing, i.e. exactly the defect class this tool hunts.
    # I shipped that bug on the first run. The guard below is why it cannot recur silently.
    _here = os.path.dirname(os.path.abspath(__file__))
    _repo = os.path.dirname(os.path.dirname(_here))
    ap.add_argument("--root", default=_repo)
    ap.add_argument("--min-files", type=int, default=200,
                    help="refuse to report if the sweep visited fewer files than this; a sweep "
                         "that matches nothing reports success (BEN-032 / SHELL_PIN_FLOOR idiom)")
    ap.add_argument("--power-only", action="store_true")
    ap.add_argument("--severity", choices=("DEFECT", "REVIEW", "ALL"), default="ALL")
    a = ap.parse_args()

    if not run_power():
        raise SystemExit("[audit] a detector failed its own power test; refusing to report a sweep "
                         "whose detectors are not shown to fire (fail closed)")
    if a.power_only:
        print("power test PASSED for all detectors")
        return 0

    findings, n_files = sweep(a.root)
    if n_files < a.min_files:
        raise SystemExit(f"[audit] the sweep visited only {n_files} files under {a.root} (floor "
                         f"{a.min_files}). A sweep that matches nothing reports success, so this "
                         f"fails closed rather than printing a clean bill of health.")
    order = {"DEFECT": 0, "REVIEW": 1}
    findings.sort(key=lambda f: (order[f[0]], f[1], f[2], f[3]))

    n_def = sum(1 for f in findings if f[0] == "DEFECT")
    print(f"=== SWEEP of {a.root} ({n_files} files) ===")
    print(f"  {len(findings)} hits: {n_def} DEFECT, {len(findings) - n_def} REVIEW")
    print()
    cur = None
    for sev, name, rel, ln, line, why in findings:
        if a.severity != "ALL" and sev != a.severity:
            continue
        if (sev, name) != cur:
            cur = (sev, name)
            print(f"--- {sev}: {name} ---")
        print(f"  {rel}:{ln}")
        print(f"    {line[:150]}")
        print(f"    why: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
