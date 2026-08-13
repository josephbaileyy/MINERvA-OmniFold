"""Completeness probe for `docs/EAVAIL_DEFINITION.md:101` — "a five-site change or nothing".

WHAT THIS IS. A REPRODUCER, NOT A DISCOVERY INSTRUMENT. I found the extra site by grep
before writing this; the probe exists so the claim is rerunnable and can be shown false,
not so it can be presented as an independent measurement. Read it as an existence proof.

WHAT IT CAN AND CANNOT PROVE. A regex scan over declarations can prove the document's
five-site list is INCOMPLETE (one uncovered site suffices). It CANNOT prove six is the
total -- that is a universal claim and grep does not establish universals. Every count
below is a LOWER bound.

PREDECLARED EXPECTATIONS, written before the run (the habit that caught last round's
vacuous pass: an arm whose expectation is recorded only after seeing output cannot fail):

  P1  sites the document names by path                     expect 1   (of the 5 it claims)
  P2  code sites binding 135 as an E_avail pi+- mass       expect >5  (the list undercounts)
  P3  of the 4 converter sites, how many bind BY COMMENT   expect 2   (doc says all four do)
  P4  CONTROL: 139.57 used as an E_avail pi+- mass         expect 0   (else repair is part-done
                                                                       and P2's premise is wrong)

P4 is the wiring control and it is not trivial: 139.57 DOES occur in the tree, at
pointcloud_projection.py:55, as a multiplicity threshold rather than an E_avail term. A
scan that cannot tell those apart would report the repair partly done. That is exactly the
discrimination a repairer has to make, so the control tests the probe and the task at once.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# The document names exactly one of its five sites by path (:101). The other four are
# described only as "four generator converters that bind to our value by comment", so the
# list cannot be executed without re-deriving them -- recorded as P1 rather than assumed.
DOC_NAMES_BY_PATH = ["MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h"]

# Candidate declarations: a name suggesting a pion mass, bound to 135 in MeV or GeV.
DECL = re.compile(
    r"^(?P<indent>\s*).*?\b(?P<name>[A-Za-z_][A-Za-z0-9_]*(?:PION|PI_PM|PI|MPI)[A-Za-z0-9_]*)\b"
    r"\s*(?:,[^=]*)?=\s*(?P<rhs>[^;#\n]*)",
    re.IGNORECASE,
)
IS_135 = re.compile(r"\b(?:135(?:\.0*)?|0\.135(?:0*)?)\b")
IS_13957 = re.compile(r"\b(?:139\.57|0\.13957)\b")
BINDS_BY_COMMENT = re.compile(r"CVUniverse", re.IGNORECASE)

SCAN_DIRS = ["nd-unfolding", "3d-unfolding", "2d-unfolding", "MINERvA101"]
SUFFIXES = {".py", ".h", ".C", ".cxx", ".cpp"}


def eavail_context(lines, i, window=8):
    """True if the declaration sits near code that actually forms an E_avail sum.

    Deliberately loose. A false positive here weakens my own finding by inflating the
    count, so the bias runs against the claim I am making.
    """
    lo, hi = max(0, i - window), min(len(lines), i + window + 1)
    blob = "\n".join(lines[lo:hi])
    return bool(re.search(r"eavail|GetEAvailableTrue|recoil\s*\+=|r \+= E -", blob, re.I))


def scan(pattern):
    hits = []
    for d in SCAN_DIRS:
        root = REPO / d
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix not in SUFFIXES or not path.is_file():
                continue
            try:
                lines = path.read_text(errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                m = DECL.match(line)
                if not m or not pattern.search(m.group("rhs")):
                    continue
                if not eavail_context(lines, i):
                    continue
                hits.append({
                    "path": str(path.relative_to(REPO)),
                    "line": i + 1,
                    "text": line.strip(),
                    "comment_bound": bool(BINDS_BY_COMMENT.search(
                        "\n".join(lines[max(0, i - 2):i + 2]))),
                })
    return hits


def report(label, expected, observed, detail=""):
    ok = observed == expected if isinstance(expected, int) else expected(observed)
    verdict = "as expected" if ok else "*** UNEXPECTED ***"
    exp = expected if isinstance(expected, int) else "predicate"
    print(f"[{label}]\n  expected : {exp}\n  observed : {observed}   ({verdict})")
    if detail:
        print(detail)
    print()
    return ok


sites135 = scan(IS_135)
sites13957 = scan(IS_13957)

listing = "\n".join(
    f"    {'COMMENT-BOUND' if s['comment_bound'] else 'SILENT       '}  "
    f"{s['path']}:{s['line']}  {s['text']}"
    for s in sites135
)
covered = [s for s in sites135
           if any(s["path"].endswith(n) for n in DOC_NAMES_BY_PATH)]
converters = [s for s in sites135 if s["path"].startswith("3d-unfolding")]
uncovered_nonconverter = [s for s in sites135
                          if s not in covered and s not in converters]

ok = []
ok.append(report("P1 sites the document names by path", 1, len(covered)))
ok.append(report("P2 code sites binding 135 as an E_avail pi+- mass",
                 lambda n: n > 5, len(sites135), listing))
ok.append(report("P3 of the converter sites, how many bind BY COMMENT",
                 2, sum(1 for s in converters if s["comment_bound"]),
                 f"    converters found: {len(converters)}"))
ok.append(report("P4 CONTROL 139.57 used as an E_avail pi+- mass", 0, len(sites13957),
                 "    (139.57 does occur at pointcloud_projection.py:55, as a\n"
                 "     multiplicity threshold -- outside any E_avail sum. If this arm\n"
                 "     were nonzero the scan could not tell the two uses apart.)"))

# P4 FIRED. Kept at its predeclared expectation of 0 rather than relaxed to 1 -- moving a
# goalpost after seeing output is the failure this whole probe style exists to prevent. The
# window-based context test cannot separate two constants declared four lines apart in the
# same file, which is precisely pointcloud_projection.py:51 (M_PION_EAVAIL) vs :55 (M_PI).
# P5 narrows from "declared near E_avail code" to "the NAME appears in an accumulation
# line", which is the discrimination a repairer actually has to make.
#
# P5b FIRED TOO, AND IT IS THE ARM BUILT TO REFUTE ME: it reported only 2 of the 6
# declarations reaching an accumulation line, which would mean four of my six sites are
# dead code and the finding is inflated. I checked all six use lines BY HAND BEFORE
# touching the regex -- the order matters, because adjusting a pattern until an arm passes
# is how a probe stops being able to fail. All six are genuinely subtracted in a charged-
# pion E_avail term. The regex missed two idioms it never covered:
#     econ[m] = E[m] - MASS_PI          (both GiBUU converters)
#     np.copyto(contrib, E - np.float32(M_PION_EAVAIL), where=is_pic)
#
# I did NOT then write a cleverer regex. Distinguishing "subtracted into an E_avail sum"
# from "subtracted to test a KE threshold" (pointcloud_projection.py:116, which is a COUNT,
# not an energy) is a semantic question that a pattern match will get wrong in one
# direction or the other, and a wrong automated oracle here is worse than none. So P5/P5b
# are replaced by a recorded, eye-checkable table: each declaration with the line that
# consumes it. The claim rests on those six lines, not on a regex.
USE_SITES = {
    "nd-unfolding/pet/pointcloud_projection.py:51": (107, "np.copyto(contrib, E - np.float32(M_PION_EAVAIL), where=is_pic)"),
    "3d-unfolding/genie/genie_to_xsec3d.py:42": (53, "elif a == 211:       r += E - MASS_PI_PM"),
    # First run recorded these two as the post-semicolon FRAGMENT rather than the whole
    # line, because that is what grep printed; the arm caught it as verbatim-match=False.
    # A substring test would have passed and hidden the transcription error, so it stays
    # an equality test.
    "3d-unfolding/genie/gibuu_to_xsec3d.py:53": (113, "m = had & (pid == 101) & (np.abs(ch) == 1);  econ[m] = E[m] - MASS_PI      # pi+- (KE-ish, matches reader)"),
    "3d-unfolding/genie/gibuu_to_xsec_eavailW.py:38": (81, "m = had & (pid == 101) & (np.abs(ch) == 1); econ[m] = E[m] - MASS_PI"),
    "3d-unfolding/genie/nuwro_to_flat.C:31": (52, "} else if (pdg == 211 || pdg == -211) { eavail += E - MPI;"),
    "MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:364": (369, "if(pdg == 211 || pdg == -211) recoil+=GetVecElem(\"mc_FSPartE\",i)-mass_pion;  // KE"),
}
confirmed, table = 0, []
for s in sites135:
    key = f"{s['path']}:{s['line']}"
    want = USE_SITES.get(key)
    if not want:
        table.append(f"    {key}  *** NO RECORDED USE LINE -- claim not supported ***")
        continue
    actual = (REPO / s["path"]).read_text(errors="replace").splitlines()[want[0] - 1].strip()
    match = actual == want[1]
    confirmed += match
    table.append(f"    {key}\n        consumed at :{want[0]}  verbatim-match={match}\n"
                 f"        {actual}")
ok.append(report("P5 each 135 declaration has a RECORDED, re-read use line",
                 len(sites135), confirmed, "\n".join(table)))

print("SITES THE DOCUMENT'S FIVE-SITE LIST DOES NOT REACH "
      "(neither CVUniverse.h nor a 3d-unfolding converter):")
for s in uncovered_nonconverter:
    print(f"    {s['path']}:{s['line']}  {s['text']}")
if not uncovered_nonconverter:
    print("    (none -- the finding would not hold)")

print(f"\narms behaving as predeclared: {sum(ok)}/{len(ok)}")
sys.exit(0)
