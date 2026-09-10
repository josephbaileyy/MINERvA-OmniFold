#!/usr/bin/env python3
r"""Consumer-set completeness check for PACKET-20260910-z-consumer-set-and-endpoint-requirements.md.

WHY THIS EXISTS. The packet's first version declared its scope as three globs --
`nd-unfolding/*.py`, `2d-unfolding/*.py`, `docs/analysis-note/*.tex`. Measured: those cover
**136 of 541** tracked `.py` files, 25%. The 405-file remainder included `3d-unfolding/` entirely
(27 files), 211 files under `nd-unfolding/` subdirectories and 30 under `2d-unfolding/`'s -- and it
contained at least four real consumers, one of which (`overlay_generators_band.py`) breaks the
packet's A/B partition, and one of which (`pet/assemble_ctotal_bkgsub.py`) the prior record required
be excluded BY NAME. **An exclusion you cannot state because the file is outside your search is not
an exclusion.**

The reviewer's requirement, passed without addition: *"the consumer-set search must be scoped by
what it covers rather than by directory guess, and its scope statement must be checkable."*
A scope naming three globs is not checkable -- nothing establishes those globs cover the consumers.

SO THE SCOPE IS STATED AS A POPULATION AND VERIFIED AGAINST AN INDEPENDENT COUNT:
every `.py`, `.tex`, `.C`, `.cpp` and `.sh` file under the repository root, excluding the VCS
directory and caches -- **913 files, every extension count pinned and verified**, not two of
five. `--population` prints the per-extension counts so each can be compared against
`git ls-files` directly. A mismatch is reported, not silently absorbed.
⚠ The non-Python extensions were added so their members are IN SCOPE and therefore
EXCLUDABLE BY NAME; their SIGNATURE SET is separately declared UNVALIDATED below.

HOW IT WORKS -- the same PINNED-INVENTORY design as the withdrawal checker, which caught its own
author on its first run. Signatures find CANDIDATES by content; every candidate must appear in
`REGISTRY` with its endpoint(s) and state, or the check FAILS CLOSED. It does not try to classify
automatically: that judgement is made once, recorded, and pinned.

⚠ NO CHARACTER CLASSES IN THE SIGNATURES. A `[a-z_]*` class dropped `sec_3d` from this lane's own
`\input` extraction; a `[a-z_0-9]` class dropped `overlay_eavailW_band.py` from the reviewer's grep,
because of the capital `W`. Three people hit that bug on the same day. Plain substrings only.

Run:            python3 docs/orchestration/state/check-consumer-set-20260910.py
Population:     python3 docs/orchestration/state/check-consumer-set-20260910.py --population
Self-test:      python3 docs/orchestration/state/check-consumer-set-20260910.py --self-test
"""
from __future__ import annotations

import sys
from pathlib import Path

# parents: [0]=state [1]=orchestration [2]=docs [3]=repo root. The first version used [2] and
# scanned `docs/` alone -- 0 files -- and `--population` reported that with exit 0.
_REPO = Path(__file__).resolve().parents[3]
_LAST_UNCITED: list[str] = []
# ⚠ WIDENED. The population was `.py + .tex`, so a consumer in another language was invisible BY
# CONSTRUCTION -- and, by this packet's own rule, UNEXCLUDABLE: a file outside the scanned population
# cannot be excluded by name, because it was never in scope to exclude. `.C`, `.cpp` and `.sh` are
# the other languages actually present in this tree that could carry one.
SCAN_EXTS = {".py", ".tex", ".C", ".cpp", ".sh"}

# ⚠ AND THE NON-PYTHON SIGNATURE SET IS DECLARED **UNVALIDATED**, on evidence rather than caution.
# Two independent attempts to signature these languages both failed -- ⚠ BUT NOT IN THE SAME WAY,
# and an earlier version of this comment wrongly implied they did. The asymmetry is the finding:
#
#   * THIS LANE'S: a FALSE POSITIVE from an UNINSTRUMENTED TOKEN SET. It matched
#     `run_negweight_covariance_analysis.sh` on a filename containing "covariance" plus a stray
#     `trace(`, and MISSED `ExtractCrossSection.cpp` entirely. A coverage failure -- and one that is
#     invisible to its author, because a miss produces no output to inspect.
#
#   * THE REVIEWER'S: a TRUE POSITIVE DISCARDED BY CATEGORY, which it corrected against itself
#     after the first version of this comment let it off more lightly. It DID surface the `.sh` --
#     line 2 of its own printed output -- then wrote "92 non-.py files touch a covariance -- mostly
#     .sh launchers" and moved on to the `.cpp` WITHOUT CHECKING ONE OF THE 92. So it is a JUDGEMENT
#     failure, not a coverage one, and by its own reckoning the worse of the two: the evidence was
#     on screen and was categorised away.
#
# Recorded this way at its request, in its words: "I would rather that be in the record correctly
# than have my half read as the more forgivable failure."
#
# So membership for these extensions rests on NAMED REGISTRATION, not on candidacy. Widening the
# population buys the ability to exclude by name; it does NOT buy signature coverage, and this
# comment exists so a green run is not read as the latter.
NONPY_COV = ("GetTotalErrorMatrix", "TMatrixD", "CovMatrix", "covariance")
NONPY_READ = ("UnfoldHisto", "GetBinError", "Diagonal", "TMatrixDSym")
SKIP_PARTS = {".git", "__pycache__", ".claude", "node_modules"}

# Independent count, measured at 054e4d66 via `git ls-files '*.py' '*.tex'`.
# 541 .py + 24 .tex tracked at 054e4d66, PLUS this checker itself = 542 .py. Verified that the
# +1 was the ONLY untracked .py in the tree when it was pinned, rather than assumed.
EXPECTED_TRACKED = {".C": 2, ".cpp": 6, ".py": 542, ".sh": 339, ".tex": 24}

# ---- SIGNATURES. Plain substrings; AND-groups (tuples) where one token alone is too generic.
INVERSION = ("np.linalg.pinv", "np.linalg.inv(", "np.linalg.solve", "keep.sum()")
COV_TOKENS = ("hCov", "covariance", "_cov", "cov_")
READ_TOKENS = ("np.diag", "np.trace", "sqrt_trace", "trace(")
TEX_DEFER = ("not quoted pending", "not yet in hand", "significance is not assigned",
             "are not reported without", "not assigned")
TEX_BAND = ("uncertainty band", "systematic band", "fractional systematic")

# ---- PINNED REGISTRY. path -> (endpoints, state, note). Endpoints may be BOTH.
REGISTRY = {
    # ---------- endpoint B: inverts a full matrix ----------
    "nd-unfolding/eavail_generator_significance.py": ("B", "GATED", "pinv; ndf = bin count (B-3 defect)"),
    "nd-unfolding/compare_ascencio_fullcov.py": ("B", "deferred", "solve; N1 applies"),
    "nd-unfolding/compare_ascencio_fine.py": ("B", "deferred", "solve; N1 applies"),
    "2d-unfolding/compare_to_paper_fullcov.py": ("B", "LIVE", "SVD pseudo-inverse, RATIFIED app_statmethods:53-58"),
    "3d-unfolding/genie/compare_3d_fullcov.py": ("B", "QUARANTINED", "CONFORMING: retained rank as ndf, :105-110"),
    "2d-unfolding/uq/_ours_only_chi2.py": ("B", "LIVE (2D)", "np.linalg.inv, ndf = bin count; correct at full rank"),
    # ---------- BOTH endpoints in one script ----------
    "3d-unfolding/genie/overlay_generators_band.py": ("A+B", "QUARANTINED",
        "band AND covariance chi2 tension; ndf = nbins (:26,:232). BREAKS the per-script partition"),
    "3d-unfolding/genie/overlay_eavailW_band.py": ("A+B", "QUARANTINED",
        "band overlay; cited by sec_eavailw.tex:71 for the corner-ratio reduction"),
    # ---------- endpoint A: diagonal, trace or band ----------
    "nd-unfolding/eavailW_covariance.py": ("A", "quarantined", "produces C_low; consumes sqrt(diag)"),
    "nd-unfolding/coverage_valid_nd.py": ("A", "diagnostic", "sqrt(diag(C)) only"),
    "nd-unfolding/mii_anchor_comparator.py": ("A", "Gate-2 blocked", "sqrt(trace) from diag"),
    # ---------- EXCLUDED BY NAME, and the exclusion is only statable because it is in scope ----------
    "nd-unfolding/pet/assemble_ctotal_bkgsub.py": ("EXCLUDED", "PET legacy boundary",
        "AGENTS.md: cannot satisfy or feed the full-event DAG"),
    # ---------- .tex deliverables ----------
    "docs/analysis-note/sec_3d.tex": ("A+B", "deferred x2 + bands",
        ":193/:210/:261 bands (A); :322 3D chi2 and :418-419 4D pulls deferred (B)"),
    "docs/analysis-note/paper_body.tex": ("B", "deferred", ":146-148, the PAPER's own words"),
    "docs/analysis-note/primer_body.tex": ("B", "deferred", ":130, the PRIMER's own words"),
    "docs/analysis-note/sec_eavailw.tex": ("A", "quarantined",
        "(E_avail,W) band; :63-67's generator band is NOT covariance-derived and is excluded"),
    "2d-unfolding/agreement_windows_receipt.py": ("EXCLUDED", "2D, VALIDATED",
        "cited by a deliverable, so found by the citation test rather than by a directory guess; "
        "excluded because this set is scoped to Z and 2D is complete on value and uncertainty"),
    "2d-unfolding/compare_to_paper_interior.py": ("EXCLUDED", "2D, VALIDATED",
        "same: cited by a deliverable, inverts, and is the 2D interior comparison"),
    "3d-unfolding/genie/compare_mec_eavail.py": ("A", "QUARANTINED",
        "reads uq_universe_3d_covariance.root (:51) and imports overlay_generators_band's machinery "
        "(:28); product at sec_3d.tex:357. Found by DELEGATION, not by a token: it has 0 inversion "
        "and 0 diagonal tokens of its own"),
    "3d-unfolding/genie/mode_decomp_eavail.py": ("A", "QUARANTINED",
        "same covariance (:91), same import (:121); product at sec_3d.tex:348. Same delegation "
        "mechanism. Both sit on the A side while importing a B-side consumer's machinery -- a third "
        "and fourth example of 'requirements partition, scripts do not'"),
    "nd-unfolding/excess_eavail_W.py": ("A", "quarantined",
        "surfaced by the stem test; (E_avail,W) excess, diagonal-band class"),
    "docs/analysis-note/app_statmethods.tex": ("A+B", "RATIFIED PROTOCOL",
        "not a consumer: it is the protocol the consumers must conform to (:53-58 pseudo-inverse, "
        ":645-658 the four declarations). Registered so the checker stops reporting it"),
    "MINERvA101/MINERvA-101-Cross-Section/ExtractCrossSection.cpp": ("EXCLUDED",
        "vendored reference framework",
        "populates an unfolding covariance via RooUnfold (:83-97), so it IS covariance-touching -- "
        "and is excluded as the vendored MINERvA-101 teaching/reference framework, not a "
        "publication consumer of Z. THE POINT OF REGISTERING IT: this exclusion was unstatable "
        "while the population was .py+.tex, because the file was never in scope to exclude"),
    "2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh": ("EXCLUDED",
        "wrapper, and a FALSE POSITIVE of this lane's own non-Python signature",
        "a shell wrapper whose FILENAME contains 'covariance'; it consumes nothing itself. Recorded "
        "as the false positive that showed the non-Python signature set is unvalidated"),
    "docs/analysis-note/sec_results.tex": ("EXCLUDED", "2D, VALIDATED",
        "fig:uqbands is a real covariance band, out of scope because this set is scoped to Z"),
}


def population(root: Path = _REPO) -> list[Path]:
    """Every .py and .tex under the repo root, excluding the VCS directory and caches.

    ⚠ THE SKIP LIST IS MATCHED AGAINST THE PATH RELATIVE TO `root`, NOT THE ABSOLUTE PATH.
    The first version used `set(p.parts)` on the absolute path. This checkout lives at
    `.../MINERvA-OmniFold/.claude/worktrees/z-criteria-owner-20260910`, so EVERY path under it
    contains `.claude` as a component and the skip rule excluded the entire repository -- 0 files.
    The operand was the whole absolute path when the intended operand was the part below `root`.
    """
    out = []
    for p in root.rglob("*"):
        if p.suffix not in SCAN_EXTS or not p.is_file():
            continue
        try:
            rel_parts = set(p.relative_to(root).parts)
        except ValueError:
            continue
        if SKIP_PARTS & rel_parts:
            continue
        out.append(p)
    return sorted(out)


def _hit(text: str, single=(), pairs=()) -> bool:
    if any(s in text for s in single):
        return True
    return any(all(part in text for part in grp) for grp in pairs)


def delegation_tokens() -> tuple[str, ...]:
    """`import <module>` forms for every registered consumer, so DELEGATION is a signature.

    ⚠ WHY THIS EXISTS, and it is limit (a) rather than the limit (b) it was filed as.
    `compare_mec_eavail.py` and `mode_decomp_eavail.py` both read the same covariance as a
    registered consumer and both appear in `sec_3d.tex` as figure stems -- but measured, each has
    **0** occurrences of `np.linalg.pinv|inv(|solve|keep.sum()` and **0** of `np.diag|np.trace`.
    They were never CANDIDATES at all, so no citation test could have reached them: they call
    `load_cov` / `project_cov` / `build_projectors` imported FROM a registered consumer, so the
    consumption is not syntactically local and a token search cannot see it.

    So a consumer that DELEGATES its covariance handling to an imported helper is invisible to a
    signature-based search. This closes that class by making the registry self-propagating: import
    a consumer's machinery and you are a candidate consumer.
    """
    mods = set()
    for reg_path in REGISTRY:
        if reg_path.endswith(".py"):
            mods.add(Path(reg_path).stem)
    return tuple(f"import {m}" for m in sorted(mods)) + tuple(
        f"from {m} import" for m in sorted(mods))


def candidates(root: Path = _REPO) -> dict[str, list[str]]:
    """Candidate consumers, by signature. Returns repo-relative path -> matched signature names."""
    deleg = delegation_tokens()
    found: dict[str, list[str]] = {}
    for p in population(root):
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        why = []
        if p.suffix == ".py":
            if _hit(text, single=INVERSION):
                why.append("INVERSION")
            if _hit(text, pairs=[(c, r) for c in COV_TOKENS for r in READ_TOKENS]):
                why.append("COV+DIAG")
            if _hit(text, single=deleg):
                why.append("DELEGATION")
        elif p.suffix == ".tex":
            if _hit(text, single=TEX_DEFER):
                why.append("TEX_DEFER")
            if _hit(text, single=TEX_BAND):
                why.append("TEX_BAND")
        else:
            # UNVALIDATED, deliberately: see the note beside NONPY_COV. A hit here is a prompt to
            # classify, not evidence of consumption; a miss here is not evidence of absence.
            if _hit(text, pairs=[(c, r) for c in NONPY_COV for r in NONPY_READ]):
                why.append("NONPY-UNVALIDATED")
        if why:
            found[str(p.relative_to(root))] = why
    return found


def deliverable_texts(root: Path = _REPO) -> str:
    """The concatenated text of the three build targets' inputs -- the DELIVERABLE surface.

    Measured: `main_note`, `main_paper` and `main_primer` intersect in `values` alone, so the
    deliverable surface is the union of all three input sets, not any one of them.
    """
    note = root / "docs" / "analysis-note"
    return "\n".join(f.read_text(errors="ignore") for f in sorted(note.glob("*.tex")))


def feeds_deliverable(rel_path: str, deliv: str) -> bool:
    r"""Does this file's NAME **or its STEM** appear anywhere in the deliverable surface?

    THE DISCRIMINATOR JOSEPH'S MEMBERSHIP RULE ACTUALLY NAMES -- "a statistic with no consumer is
    out" -- applied as a re-runnable test rather than a directory guess. A covariance-touching file
    neither named nor figure-cited in note, paper or primer produces nothing either quotes.

    ⚠ THE STEM TEST IS NEW, AND LIMIT (b) FIRED BEFORE IT EXISTED. The first version tested the
    filename only -- `compare_mec_eavail.py` -- while the note cites the FIGURE STEM,
    `\includegraphics[width=\textwidth]{compare_mec_eavail}`. Two real consumers therefore read as
    *uncited*: `3d-unfolding/genie/compare_mec_eavail.py` and `mode_decomp_eavail.py`, both reading
    the same covariance as a registered consumer, both importing a registered consumer's machinery,
    both with their products in `sec_3d.tex` at `:357` and `:348`. Testing the stem as well as the
    name closes that class.

    ⚠ WHAT REMAINS UNTESTED, so the coverage claim stays scoped to what this does: a file cited
    only through a RECEIPT the deliverable cites, or through a product filename that differs from
    its own stem, is still invisible. A `False` here means "not shown to feed a deliverable", never
    "does not feed one".
    """
    name = Path(rel_path).name
    stem = Path(rel_path).stem
    return name in deliv or stem in deliv


def audit(root: Path = _REPO) -> list[str]:
    failures = []
    pop = population(root)
    if root == _REPO:
        for ext, expected in EXPECTED_TRACKED.items():
            actual = sum(1 for p in pop if p.suffix == ext)
            if actual != expected:
                failures.append(
                    f"POPULATION DRIFT: {ext} count is {actual}, pinned at {expected} "
                    f"(measured via `git ls-files` at 054e4d66). Untracked files inflate this; "
                    f"re-measure and re-pin deliberately rather than absorbing the difference.")
    deliv = deliverable_texts(root) if (root / "docs" / "analysis-note").is_dir() else ""
    unreg_cited, unreg_uncited = [], []
    for path, why in sorted(candidates(root).items()):
        if path in REGISTRY:
            continue
        (unreg_cited if feeds_deliverable(path, deliv) else unreg_uncited).append((path, why))
    for path, why in unreg_cited:
        failures.append(f"UNREGISTERED AND CITED BY A DELIVERABLE: {path} "
                        f"(matched {'+'.join(why)}) -- its name appears in note/paper/primer text, "
                        f"so it feeds a deliverable. Classify into an endpoint and pin it.")
    # The uncited group is REPORTED, not failed. The citation test has shown they feed no
    # deliverable, so failing on them would leave this check permanently red -- which trains its
    # reader to ignore it, the failure this campaign has already named once.
    global _LAST_UNCITED
    _LAST_UNCITED = [p for p, _ in unreg_uncited]
    return failures


def self_test() -> int:
    import tempfile
    print("SELF-TEST")
    clean = audit()
    print(f"  (a) live tree                     -> {len(clean)} failure(s)   must be 0")
    if clean:
        for f in clean:
            print(f"        {f}")
        return 1
    # ⚠ (b) REWRITTEN. Its first version injected an UNCITED consumer and required a failure --
    # which was the wrong expectation once the design changed: uncited candidates are a reported
    # census, not a failure, because a permanently-red check trains its reader to ignore it. The
    # path that DOES fail closed is a consumer CITED BY A DELIVERABLE, so that is what (b) now
    # exercises, and (b2) asserts the census behaviour it used to conflate with it.
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r / "docs" / "analysis-note").mkdir(parents=True)
        (r / "cited_consumer.py").write_text("import numpy as np\nx = np.linalg.pinv(C)\n")
        (r / "docs" / "analysis-note" / "sec_x.tex").write_text(
            "Provenance: cited_consumer.py produced this uncertainty band.\n")
        (r / "uncited_consumer.py").write_text("import numpy as np\ny = np.linalg.solve(C, d)\n")
        (r / "innocent.py").write_text("print('no covariance here')\n")
        (r / "plain.tex").write_text("A band of colour. Nothing statistical.\n")
        cands = candidates(r)
        fails = audit(r)
        cited_named = any("cited_consumer.py" in f for f in fails)
        print(f"  (b) consumer CITED by a deliverable -> detected {len(cands)}, "
              f"failures {len(fails)}, names it: {cited_named}   must fail and name it")
        ok_b = cited_named
        uncited_failed = any("uncited_consumer.py" in f for f in fails)
        print(f"  (b2) consumer NOT cited             -> detected: "
              f"{'uncited_consumer.py' in cands}, failed: {uncited_failed}   "
              f"must be detected but NOT failed (census)")
        ok_b2 = ("uncited_consumer.py" in cands) and not uncited_failed
        leaked = [k for k in cands if k in ("innocent.py", "plain.tex")]
        print(f"  (c) false-positive control          -> leaked {len(leaked)} {leaked}   must be 0")
        ok_c = not leaked
    # (d) a capital letter in a filename must not be dropped -- the bug three people hit.
    caps = [p for p in population() if any(ch.isupper() for ch in p.name)]
    print(f"  (d) filenames with capitals found  -> {len(caps)}   must be >= 1 "
          f"(a class like [a-z_0-9] would report 0)")
    ok_d = len(caps) >= 1
    ok = ok_b and ok_b2 and ok_c and ok_d
    print(f"  SELF-TEST {'PASSED' if ok else 'FAILED'}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    pop = population()
    if "--population" in argv:
        print(f"SCOPE: every {', '.join(sorted(SCAN_EXTS))} under {_REPO}, "
              f"excluding {sorted(SKIP_PARTS)}")
        for ext in sorted(SCAN_EXTS):
            print(f"  {ext}: {sum(1 for p in pop if p.suffix == ext)} "
                  f"(pinned {EXPECTED_TRACKED[ext]})")
        print(f"  total scanned: {len(pop)}")
        globs = " ".join(f"'*{e}'" for e in sorted(SCAN_EXTS))
        print(f"  CHECK THIS against: git ls-files {globs} | wc -l")
        drift = [f for f in audit() if f.startswith("POPULATION DRIFT")]
        if drift:
            for f in drift:
                print(f"\n[FAIL] {f}")
            print("\n  A scope report that finds nothing must NOT exit 0. The first version of this")
            print("  file scanned 0 files and reported success -- the blind-zero shape.")
            return 1
        return 0
    failures = audit()
    cands = candidates()
    if failures:
        print(f"[FAIL] consumer-set completeness: {len(failures)} issue(s)\n")
        for f in failures:
            print(f"  - {f}\n")
        return 1
    breakdown = ", ".join(f"{sum(1 for q in pop if q.suffix == e)} {e}"
                          for e in sorted(SCAN_EXTS))
    print(f"[OK] consumer set complete over a STATED population: {len(pop)} files scanned "
          f"({breakdown}) -- every extension count pinned and verified, not two of five.")
    print(f"     {len(cands)} candidates by signature; all {len(REGISTRY)} registry entries "
          f"classified, including exclusions BY NAME.")
    print(f"     CENSUS: {len(_LAST_UNCITED)} further file(s) touch a covariance but are NOT cited "
          f"by any deliverable, so they feed nothing quoted. Reported, not failed.")
    print("     What this establishes: every file matching an INVERSION, COV+DIAG or DELEGATION")
    print("     signature whose FILENAME OR FIGURE STEM appears in note, paper or primer has a")
    print("     pinned classification, over a population verified against an independent count.")
    print("     What it does NOT establish:")
    print("       (a) that the SIGNATURE SET is complete. It is now three signatures rather than")
    print("           two -- DELEGATION was added after two real consumers were found carrying 0")
    print("           inversion and 0 diagonal tokens -- but no instrument certifies its own")
    print("           signature list, and this is the irreducible residue.")
    print("       (b) that the census files feed nothing. The citation test now covers filename AND")
    print("           figure stem; a file reached only through a RECEIPT, or through a product name")
    print("           differing from its own stem, is still invisible.")
    print("       (c) that the NON-PYTHON signature set works. It is declared UNVALIDATED on")
    print("           evidence: two attempts failed differently -- one a FALSE POSITIVE from an")
    print("           uninstrumented token set, one a TRUE POSITIVE dismissed by category without")
    print("           checking any of 92 surfaced files. Membership for")
    print("           .C/.cpp/.sh rests on NAMED REGISTRATION, not on candidacy -- widening the")
    print("           population bought excludability by name, not signature coverage.")
    print("       (d) that a language ABSENT from this tree would be seen. SCAN_EXTS is chosen from")
    print("           the languages present; a new one is a one-line change and a re-pinned count.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
