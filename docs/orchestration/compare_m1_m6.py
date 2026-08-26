#!/usr/bin/env python3
"""Turn two or more `measure_m1_m6.py --json` documents into a machine verdict.

CITABLE FOR: whether a named set of M-1..M-6 documents differ, which differences are declared
expected by a reviewable list, and what was compared. NOT CITABLE FOR: any F-number's verdict, the
far-end evidence, or authority to grade. This instrument compares documents. It measures no tree.

WHY IT EXISTS. `F-17(b)` (contract `:621`, `:1471`) obliges M-1..M-6 on BOTH trees with
"differences reported as findings". `measure_m1_m6.py` measures one tree per invocation and does it
well; nothing turned two of its outputs into a verdict, so the comparison was performed by a human
reading two columns into a receipt -- no negative control, and no record of what was compared.
`F-17(a)` was discharged that way at candidate `30ec0707`.

IT COMPUTES NO MEASUREMENT (R1). There is no `ast`, no `subprocess`, no git call, no glob of a tree
anywhere in this file, and a test asserts that by parsing this module's own imports. A rule retyped
is a second implementation of it. Every number here comes from a document that `measure_m1_m6.py`
produced; if a document is wrong, this instrument is wrong in exactly the same way, which is the
intended failure mode.

THE COMPARISON IS JOINT, NEVER COMPOSED FROM PAIRS (R5). For each field the instrument takes the
distinct-value set over all n inputs at once. Under exact equality that is the same answer pairwise
would give -- equality is an equivalence relation, so "pairwise-consistent but jointly inconsistent"
is IMPOSSIBLE for equality and R5's fixture cannot be built from it. It becomes possible the moment
an expected-difference rule carries a TOLERANCE (`max-abs-delta`): with values 3, 0, 6 and a
tolerance of 4, a baseline-relative pass -- input 0 against each of the rest, which is the natural
shape of a two-column F-17(a) table -- finds every comparison inside tolerance while the joint
spread is 6. That is the fixture in the test suite, and it is the only form in which this arm can
fail.

WHAT THE INPUT DOCUMENT CANNOT TELL IT, stated rather than papered over. `measure_m1_m6.py --json`
emits no timestamp, no digest of itself, and no branch/detached state -- `m4()` returns
`is_git, head, dirty, untracked, modified, behind, ahead, upstream` and nothing else. So:
  * R3's "detached-or-branch" and R6's "wall-clock of each measurement" are NOT derivable here and
    are emitted as `UNAVAILABLE-BY-INPUT-SCHEMA` with the reason attached, never silently dropped.
    Deriving them by running git against the tree would break R1 AND would answer about the tree as
    it is NOW rather than as it was when measured, which is this campaign's named defect.
  * two documents from different revisions of `measure_m1_m6.py` cannot be told apart by this
    instrument. What it CAN see is that their field sets differ. **This paragraph used to claim that
    was reported as an unexpected finding, and the code did not do it** -- `field_set_differs` was a
    boolean reaching no count and no exit code, and a field present on one side and absent on the
    other was an ordinary finding the whitelist could suppress. Since 2026-08-25 it is true in three
    places: an ABSENT value is never suppressible, `may-differ` fails closed on the sentinel, and
    `field_set_differs` forces the some-unexpected exit. The F-17(a) failure was exactly an
    instrument difference (5 literals reported where there were 7).
  * the fix belongs in `measure_m1_m6.py`, and NOT NOW: adding fields to it mid-rehearsal would give
    the post-rehearsal documents fields the already-filed pre-submission documents lack, and this
    instrument would correctly report that as a finding. Manufacturing findings is worse than
    declaring a gap. Propose it after Gate 2.

THE EXPECTED LIST IS A WHITELIST, SO IT HAS FAILING ARMS (R4). It is an input file, never a literal
in this code, so widening it is a reviewable diff. Every entry must carry a citation that RESOLVES
-- the cited document must exist under `--repo`, must contain the quoted string, and if the entry
declares a digest the document must still have it -- and an unresolved citation is a hard refusal,
not a warning. Three further refusals exist because a whitelist that can swallow a whole measurement
is not reviewable:
  * A PATTERN MUST NAME ONE FIELD, enforced by a POSITIVE GRAMMAR rather than a deny-list of
    spellings: `M-1[<exact file path or *>].<field>` for the per-file measurement, `M-k.<field>`
    for the others, and `*` is a SELECTOR-space device -- legal inside `M-1[...]`, where it
    ranges over FILES, and nowhere else. The terminal field name is always a literal, so a
    pattern cannot match two fields of one object. THE SELECTOR IS A BARE `*` OR AN EXACT
    LITERAL; a PARTIAL selector wildcard is refused, ruled by Joseph 2026-08-25 (section 12.2.1)
    because it reads as one file while already covering two and its reach moves silently as the
    file population grows -- see `parse_pattern` for the two measurements. `M-4.behind` and
    `M-1[*].first_insert` are allowed; `M-4.*`, `M-1[*].*`, `M-4.*e*`, `M-1[`, `M-3[x].y`,
    `M-1[*` and `M-1[nd-*].first_insert` are all refused.
    THE LAST ONE IS WHY THIS IS A GRAMMAR AND NOT ANOTHER SPELLING. The old test was
    `pattern.rsplit(".", 1)[-1] in ("*", "**")`. A DOTLESS pattern has no last segment, so
    `M-1[*` -- the documented per-file form with its `]` dropped -- was compared WHOLE against
    `"*"`, passed the guard, and then matched every M-1 field. Measured on the real far-end
    inputs with a genuine one-line citation: all 19 M-1 findings suppressed as
    EXPECTED-BY-RULING, expected 0 -> 19, no warning and no refusal (defect D-3,
    `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` section 8.3). The deny-list arm
    that reviewed it tested `M-4`, `M-4.*`, `M-1[*].*`, `*`, `M-4behind`, `behind` -- the
    spellings someone thought to type -- and a fixture enumerated from the same intuition as
    the rule cannot disagree with the rule. `M-6[*` and `M-4.*e*` were fail-open too, in the
    same class and in spellings nobody listed. Backed by `matcher_disagreement`, which
    interrogates `field_matches` ITSELF with canary fields instead of modelling the pattern
    language a second time -- the divergence between the guard's model and the matcher's
    behaviour IS the defect;
  * NO pattern may target M-2 at all (R7): `F-17(b)` names M-2 as the perishable claim, so an M-2
    difference is never suppressible, is reported in its own block, and forces the some-unexpected
    exit whatever the list says;
  * A CITATION MUST LOCATE. The quote must match at least one whole line and no more than
    `MAX_CITATION_LINES` of them, because a quote matching 96 of a document's 146 lines -- measured,
    from `{"quote": "a"}` -- resolves without citing anything. And `--expected` must resolve inside
    `--repo`: a whitelist from outside the tree is not the reviewable diff this file claims it is.
  * ONE CITATION PER FIELD PATTERN. A single `citation` may license exactly one pattern; a
    multi-field entry needs a `citations` mapping with an entry for each, checked in both
    directions. The first entry ever shipped here failed exactly this way -- see
    `resolve_citations`. Note what no check can do: resolving is not SUPPORTING, and no mechanical
    test reads a quote's aboutness. This shape only stops one quote licensing a list.
  * the shipped list is deliberately ONE entry over ONE field. See the REJECTED section below.

REJECTED FROM THE SPEC (`SPEC-20260825-f17b-tree-comparison-instrument.md`), re-derived rather than
re-quoted:
  * R4's second declared-expected bullet -- "M-1, M-5 and P-6 are falsified by any commit to
    `build-k0-execution-integrity`" -- is NOT in the shipped expected list, because as a whitelist
    entry it would suppress the very findings F-17(b) exists to catch. Measured 2026-08-25 at
    `49dbdf8f`: of the 46 commits in `8c156a37..build-k0-execution-integrity`, 2 touch the ten M-1
    files, 8 touch the eight M-5 launchers, 3 touch `mnv_guarded_run.py`, and 10 touch any of them
    -- so 36 of 46 commits to that branch cannot move M-1, M-5 or M-6, and "any commit" is false.
    (Contract 7.0.19 makes the same point from the other side: a docs commit is "provably unable" to
    move the source listing because `SOURCE_SUFFIXES = (".py", ".sh")`.) The differences those
    measurements DID show -- M-1's dropped tenth entrypoint, M-5's 0-of-8 against 8-of-8 -- are
    findings against the builder, and a rule that pre-declared them expected is how a gate stops
    being able to fail. Also: "P-6" is not a measurement this tool emits; M-6 is.
  * R4's first bullet HOLDS, for `M-4.behind` ALONE, and is the one shipped entry:
    `MEASUREMENT-20260822-m1-m6-at-pinned-sha.md:89` records the behind-count as having "moved
    twice" (36 -> 55 -> 65) with `HEAD`, `dirty` and the `717/4` split all unchanged in the same
    block -- drift demonstrated with the tree held FIXED -- and `measure_m1_m6.py`'s `--upstream`
    does default to `origin/main`.
    **`M-4.ahead` was in this entry and has been REMOVED, 2026-08-25, on a peer's reading of the
    citation.** The cited document mentions `ahead` exactly once, as `ahead = 0 ; --is-ancestor
    rc=0`: a stable zero, and affirmative evidence that the tree carried no commits of its own. So
    the citation did not support the field, it recorded the opposite. The counter-argument is real
    and loses on cost: `ahead` CAN move with the tree unchanged, if someone pushes that tree's
    commits to the upstream -- but it can also move because the measured tree GAINED a commit
    nobody else has, which is precisely the drift F-17 exists to surface. Suppressing a field with
    two causes, one of them the finding, to save a reviewer one dismissible line, is the wrong
    trade: F-17 says differences are REPORTED as findings, so reporting is the obligation and
    suppression needs authority. No document supports it yet; if one appears, cite it.
    Also NOT covered: `M-4.upstream`, because two invocations run against different upstreams are
    not the same comparison and that must surface.

EXIT CODES ARE A DISJOINT VOCABULARY (R8), documented in --help and asserted one arm per code:
    0  no differences        10  differences, all expected      20  differences, some unexpected
    4  refusal: an input      5  refusal: the expected list      2  refusal: usage (argparse's own)
    1  RESERVED AND NEVER A VERDICT -- an uncaught traceback exits 1, so no verdict may share it.
The vocabulary is declared as a SEQUENCE and checked by `check_vocabulary` at import, because a dict
literal cannot represent the collision it would need to refuse. See the comment beside it: collapsing
two verdicts onto one integer is the silent pass this whole instrument exists to prevent, and the
first version of it was pinned only by an assertion that was true of every dict.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys

SCHEMA = "mnv_m1m6_comparison/1"
EXPECTED_SCHEMA = "mnv_m1m6_expected_differences/1"
INSTRUMENT_VERSION = "1"

EXIT_NO_DIFFERENCES = 0
EXIT_DIFFERENCES_ALL_EXPECTED = 10
EXIT_DIFFERENCES_SOME_UNEXPECTED = 20
EXIT_REFUSAL_INPUT = 4
EXIT_REFUSAL_EXPECTED_LIST = 5
# A SEQUENCE OF PAIRS, NOT A DICT LITERAL, AND THAT IS THE FIX.
#
# A dict CANNOT REPRESENT a collision: write two entries under one code and the literal silently
# keeps the last, so `len(set(EXIT_CODES)) == len(EXIT_CODES)` is a TAUTOLOGY for every dict alive
# and pins nothing in either direction. Found 2026-08-25 by a peer who mutated
# EXIT_DIFFERENCES_SOME_UNEXPECTED to 10, collapsing "some unexpected" onto "all expected" -- the
# exact silent pass this instrument exists to prevent. Exactly one arm caught it, and it caught it
# through the help TEXT rather than through behaviour, because every behavioural assertion in the
# suite compared the observed exit against THE CONSTANT UNDER TEST, so the oracle moved with the
# mutation. A collision must be REPRESENTABLE before it can be refused; hence pairs, checked, and
# only then a dict.
EXIT_VOCABULARY = (
    (EXIT_NO_DIFFERENCES, "NO-DIFFERENCES"),
    (EXIT_DIFFERENCES_ALL_EXPECTED, "DIFFERENCES-ALL-EXPECTED"),
    (EXIT_DIFFERENCES_SOME_UNEXPECTED, "DIFFERENCES-SOME-UNEXPECTED"),
    (EXIT_REFUSAL_INPUT, "REFUSAL-INPUT"),
    (EXIT_REFUSAL_EXPECTED_LIST, "REFUSAL-EXPECTED-LIST"),
)
RESERVED_EXIT_CODES = {1: "an uncaught traceback; never a verdict", 2: "argparse usage refusal"}


def check_vocabulary(vocabulary, reserved):
    """Refuse to be IMPORTABLE with a collapsed verdict vocabulary. Returns the dict.

    Fails closed at import, before any comparison can be run, and deliberately by raising: an
    uncaught raise exits 1, which this file already documents as reserved and never a verdict. A
    collapsed vocabulary that merely printed a warning would still produce a number a receipt could
    quote.
    """
    codes = [code for code, _ in vocabulary]
    names = [name for _, name in vocabulary]
    duplicated = sorted({code for code in codes if codes.count(code) > 1})
    if duplicated:
        raise RuntimeError(f"exit vocabulary COLLAPSED: code(s) {duplicated} carry more than one "
                           f"verdict. Two verdicts on one integer is a silent pass.")
    repeated = sorted({name for name in names if names.count(name) > 1})
    if repeated:
        raise RuntimeError(f"exit vocabulary has repeated name(s) {repeated}")
    taken = sorted(set(codes) & set(reserved))
    if taken:
        raise RuntimeError(f"exit vocabulary claims reserved code(s) {taken}: "
                           f"{[reserved[c] for c in taken]}")
    return dict(vocabulary)


EXIT_CODES = check_vocabulary(EXIT_VOCABULARY, RESERVED_EXIT_CODES)

# A CITATION MUST LOCATE A PASSAGE, NOT MERELY OCCUR.
#
# The guard used to require only that a quote was non-blank and present somewhere in the cited
# document. A grader fed it `{"quote": "a"}` and suppressed M-3.rc, M-3.all_intact, M-4.modified and
# M-6.counts_resolutions at exit 10 with every arm green. Measured on the document actually cited by
# the shipped list: the real quote resolves to 1 line of 146; "a" resolves to 96 of 146. So the
# defect has a measurable signature -- an uninformative quote matches everywhere -- and the bound
# below separates the two cases by a wide margin.
#
# THE NUMBER IS A JUDGEMENT, and saying so is the point: 3 is not derived from anything, it is chosen
# to sit far above the legitimate case (1) and far below the attack (96). It is a backstop. The real
# defence is the covering control in the suite, which fixes the set of suppressible fields against
# the measured field universe and therefore fires on ANY widening, however well quoted.
MAX_CITATION_LINES = 3

MEASUREMENT_IDS = ("M-1", "M-2", "M-3", "M-4", "M-5", "M-6")
REQUIRED_KEYS = ("label", "tree") + MEASUREMENT_IDS
PERISHABLE_ID = "M-2"          # F-17(b) singles it out; see R7

# THE SHAPE OF A FIELD PATH, DECLARED ONCE. `flatten` emits `M-1[<file>].<key>` for the row
# measurement and `M-k.<key>` for the block ones, and `parse_pattern` accepts exactly that
# shape. Both read these two names so the emitter and the grammar cannot drift apart: the
# defect they replace was a guard that modelled the pattern language separately from the
# matcher that implements it.
ROW_MEASUREMENT_ID = MEASUREMENT_IDS[0]            # measured once PER FILE, hence the [...]
BLOCK_MEASUREMENT_IDS = MEASUREMENT_IDS[1:]        # measured once per tree, hence no [...]
WILDCARD = "*"
# Canary tokens for `matcher_disagreement`. They carry no `*`, so they are inert as patterns,
# and no real path or measured key looks like them.
PROBE_PATH = "__probe__/__probe__.py"
PROBE_FIELD = "__probe_field__"
ABSENT = "<FIELD ABSENT FROM THIS DOCUMENT>"
UNAVAILABLE = "UNAVAILABLE-BY-INPUT-SCHEMA"

# MANY OF THESE FIELDS ARE CONDITIONALLY PRESENT, AND ABSENCE IS NOT FALSITY. `M-3.rc` and
# `M-3.all_intact` are omitted when the script is missing; every `M-4` field but nothing else when
# the tree is not a repository; `behind`/`ahead`/`upstream` when the upstream ref does not resolve;
# every `M-6` field but `present`/`state` when the guard file is absent; every `M-1` row field but
# `present` when that file is absent. The "a field with no UNITS entry is reported UNDECLARED"
# mechanism does NOT cover this, because absence is not a new field -- what covers it is that an
# ABSENT value is never suppressible.
#
# WHAT EACH FIELD IS, AND WHERE ITS VALUE CAME FROM. The recurring defect here is asymmetric
# comparison: a delta believed without naming the unit of each side and the population each side was
# drawn from. Matched in order by fnmatch. A field with no entry is reported with unit UNDECLARED
# and counted separately, so a new field in `measure_m1_m6.py` cannot arrive silently unitless.
UNITS = (
    ("M-1[*].present", "boolean",
     "one of the ten paths in measure_m1_m6.py's M1_FILES, resolved inside the measured tree"),
    ("M-1[*].literals",
     "sorted list of compact-JSON objects with FOUR keys -- form, line, name, value -- and NOT"
     " the name@line(form) rendering, which is measure_m1_m6.py:260, the non---json print path."
     " Two trees agreeing on name, line and form but differing in value produce a delta here",
     "every string Constant in that file whose value is the canonical root, exact or subpath"),
    ("M-1[*].first_insert", "line number of the first sys.path insert/append, or null",
     "that file's parsed syntax tree"),
    ("M-1[*].repo_modules_after", "list of (module, line)",
     "imports below the first sys.path insert whose top-level name is a repo module -- and the repo"
     " module set is the *.py stems under nd-unfolding/ and 2d-unfolding/, tracked or not"),
    ("M-1[*].n_after", "count of the repo_modules_after list",
     "same population as repo_modules_after"),
    ("M-2.importable", "count of distinct top-level importable names",
     "*.py stems under nd-unfolding/ and 2d-unfolding/ in the measured tree, TRACKED OR UNTRACKED --"
     " the glob does not consult git, which is what makes this the perishable claim"),
    ("M-2.stdlib_collisions", "set of module names",
     "the same glob population intersected with sys.stdlib_module_names of the MEASURING"
     " interpreter"),
    ("M-2.python", "version string of the interpreter that RAN measure_m1_m6.py",
     "NOT a property of the measured tree; a difference here means the two documents are not"
     " comparable on M-2, and it is never expected"),
    ("M-3.present", "boolean", "docs/orchestration/verify_hash_bindings.py in the measured tree"),
    ("M-3.rc", "process exit status of verify_hash_bindings.py",
     "the MEASURING interpreter (measure_m1_m6.py:161 runs sys.executable) against the script"
     " in the measured tree, with cwd set to that tree -- so like M-2.python this is NOT a"
     " property of the tree alone, and the F-17(a) column was taken on a different interpreter"
     " from any local re-measurement"),
    ("M-3.all_intact", "boolean, substring 'ALL BINDINGS INTACT' seen on stdout",
     "the same run's stdout, and therefore also a property of the MEASURING interpreter, not"
     " of the measured tree alone"),
    ("M-4.is_git", "boolean", "whether rev-parse HEAD succeeded in the measured tree"),
    ("M-4.head", "40-hex commit sha", "the measured tree's HEAD at measurement time"),
    ("M-4.dirty", "count of NON-BLANK porcelain lines",
     "the measured tree's working tree; measure_m1_m6.py:177 drops blank lines before"
     " counting, so this is not simply the porcelain line count"),
    ("M-4.untracked", "count of non-blank porcelain lines starting ??",
     "the same non-blank subset as M-4.dirty"),
    ("M-4.modified", "count of non-blank porcelain lines not starting ??",
     "the same non-blank subset as M-4.dirty"),
    ("M-4.behind", "count of commits, DRIFTING -- never quotable without its date",
     "a left-right count of <upstream>...HEAD, so the population is whatever <upstream> pointed at"
     " when the measurement ran"),
    ("M-4.ahead", "count of commits, DRIFTING", "the same left-right count as M-4.behind"),
    ("M-4.upstream", "the ref name given to --upstream (default origin/main)",
     "an ARGUMENT of the measurement, not an observation of the tree"),
    ("M-5.n", "count", "the eight names in measure_m1_m6.py's LAUNCHERS tuple"),
    ("M-5.missing", "set of launcher filenames", "LAUNCHERS not present under nd-unfolding/"),
    ("M-5.repo_assign", "set of launcher filenames",
     "LAUNCHERS carrying a line matching ^\\s*(export\\s+)?REPO="),
    ("M-5.activator_from_code_root", "set of launcher filenames",
     "LAUNCHERS containing the literal source \"${CODE_ROOT}/setup_salloc_env.sh\""),
    ("M-5.activator_from_env_root", "set of launcher filenames",
     "LAUNCHERS containing the literal source \"${ENV_ROOT}/setup_salloc_env.sh\""),
    ("M-6.present", "boolean", "nd-unfolding/mnv_guarded_run.py in the measured tree"),
    ("M-6.n_lines", "count of lines", "that file"),
    ("M-6.counts_resolutions", "boolean, substring 'self.checked'", "that file"),
    ("M-6.inventory_write_lines", "set of line numbers",
     "lines of that file carrying BOTH '\"checked\"' AND a colon (measure_m1_m6.py:225 tests"
     " for both; naming only the first would overstate the population)"),
    ("M-6.else_zero_default_lines", "set of line numbers",
     "lines carrying both 'guard.checked' and 'else 0'"),
    ("M-6.state", "one of FOUR named states, never a boolean",
     "three are derived from the two line sets above; the fourth is 'FILE ABSENT'"
     " (measure_m1_m6.py:221), returned when mnv_guarded_run.py is missing, where no line sets"
     " exist at all -- and a tree missing the guard is precisely a difference F-17 must"
     " surface, so the declared unit must not imply the file is always there"),
)


class Refusal(Exception):
    """Fail closed with a code that is not 'no differences found'."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc(stamp=None):
    when = (datetime.datetime.now(datetime.timezone.utc) if stamp is None else
            datetime.datetime.fromtimestamp(stamp, datetime.timezone.utc))
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def canon(value):
    """A canonical, order-insensitive, JSON-serializable rendering of one measured value.

    Lists are SORTED: M-5's come out in LAUNCHERS order and M-6's in line order, and a difference of
    order alone is not a difference of measurement. Rendering a list's dict elements as compact json
    keeps them comparable and readable in one field.
    """
    if isinstance(value, dict):
        return {key: canon(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        rendered = []
        for item in value:
            if isinstance(item, (dict, list)):
                rendered.append(json.dumps(canon(item), sort_keys=True, separators=(",", ":")))
            else:
                rendered.append(item)
        try:
            return sorted(rendered)
        except TypeError:                  # mixed types: keep them, stringified, rather than crash
            return sorted(str(item) for item in rendered)
    return value


def field_matches(pattern, field):
    """Glob a field path with `*` only, because `fnmatch` CANNOT do this job.

    THE FIELD PATHS THEMSELVES CONTAIN BRACKETS. `M-1[nd-unfolding/bootstrap_nd.py].first_insert` is
    a field, and to `fnmatch` the pattern `M-1[*].first_insert` reads `[*]` as a CHARACTER CLASS
    matching one literal asterisk -- so the per-file wildcard silently matched nothing and every
    M-1 difference was classified UNEXPECTED whatever the expected list said. Found by the arm that
    asserts the narrowing direction still works, which is the arm a one-directional guard omits.
    Here `*` is the only metacharacter and `[`, `]`, `.` are literal.
    """
    parts = pattern.split("*")
    if len(parts) == 1:
        return field == pattern
    if not field.startswith(parts[0]) or not field.endswith(parts[-1]):
        return False
    if len(parts[0]) + len(parts[-1]) > len(field):
        return False
    cursor = len(parts[0])
    for middle in parts[1:-1]:
        found = field.find(middle, cursor)
        if found < 0:
            return False
        cursor = found + len(middle)
    return cursor <= len(field) - len(parts[-1])


def unit_of(field):
    for pattern, unit, population in UNITS:
        if field_matches(pattern, field):
            return unit, population, True
    return ("UNDECLARED", "UNDECLARED -- this field is not in compare_m1_m6.py's UNITS table, so a"
                          " delta on it is reported WITHOUT a unit or a population", False)


def load_document(path_text, index):
    """Read one `measure_m1_m6.py --json` document. NO DEFAULTS, and absence is a refusal."""
    path = pathlib.Path(path_text)
    if not path.exists():
        raise Refusal(EXIT_REFUSAL_INPUT, f"input {index} does not exist: {path}")
    if not path.is_file():
        raise Refusal(EXIT_REFUSAL_INPUT, f"input {index} is not a file: {path}")
    raw = path.read_bytes()
    if not raw.strip():
        raise Refusal(EXIT_REFUSAL_INPUT,
                      f"input {index} is empty: {path}. An empty document is not 'no differences'.")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refusal(EXIT_REFUSAL_INPUT,
                      f"input {index} is not readable json: {path}: {exc}")
    if not isinstance(doc, dict):
        raise Refusal(EXIT_REFUSAL_INPUT,
                      f"input {index} is a {type(doc).__name__}, not a measure_m1_m6 document: "
                      f"{path}")
    missing = [key for key in REQUIRED_KEYS if key not in doc]
    if missing:
        raise Refusal(EXIT_REFUSAL_INPUT,
                      f"input {index} is missing {', '.join(missing)}: {path}. A document short of "
                      f"a measurement is a refusal, never a silent agreement on the rest.")
    resolved = path.resolve()
    return {"index": index, "path": str(resolved), "given_path": path_text,
            "sha256": sha256_of(resolved), "bytes": len(raw),
            "file_mtime_utc": utc(resolved.stat().st_mtime), "doc": doc}


def identity_of(record):
    """Who this side IS. R3: resolved path, HEAD, porcelain count -- and the two fields the input
    schema cannot supply, named as unavailable rather than omitted."""
    doc = record["doc"]
    m4 = doc.get("M-4") if isinstance(doc.get("M-4"), dict) else {}
    return {
        "index": record["index"],
        "key": f"[{record['index']}] {doc.get('label') or '(unlabelled)'}",
        "label": doc.get("label"),
        "tree_resolved_path": doc.get("tree"),
        "input_path": record["path"],
        "input_sha256": record["sha256"],
        "input_bytes": record["bytes"],
        "input_file_mtime_utc": record["file_mtime_utc"],
        "measurement_wall_clock": UNAVAILABLE,
        "head": m4.get("head", ABSENT),
        "is_git": m4.get("is_git", ABSENT),
        "porcelain_dirty": m4.get("dirty", ABSENT),
        "porcelain_untracked": m4.get("untracked", ABSENT),
        "porcelain_modified": m4.get("modified", ABSENT),
        "branch_or_detached": UNAVAILABLE,
    }


def flatten(doc, index):
    """One document -> {field path: canonical value}. Identity keys are NOT compared fields."""
    flat = {}
    rows = doc[ROW_MEASUREMENT_ID]
    if not isinstance(rows, list):
        raise Refusal(EXIT_REFUSAL_INPUT,
                      f"input {index}: M-1 is a {type(rows).__name__}, expected a list of rows")
    for row in rows:
        if not isinstance(row, dict) or "file" not in row:
            raise Refusal(EXIT_REFUSAL_INPUT,
                          f"input {index}: an M-1 row has no 'file' key, so rows cannot be paired")
        for key, value in row.items():
            if key == "file":
                continue
            flat[f"{ROW_MEASUREMENT_ID}[{row['file']}].{key}"] = canon(value)
    for measurement in BLOCK_MEASUREMENT_IDS:
        block = doc[measurement]
        if not isinstance(block, dict):
            raise Refusal(EXIT_REFUSAL_INPUT,
                          f"input {index}: {measurement} is a {type(block).__name__}, expected an "
                          f"object")
        for key, value in block.items():
            flat[f"{measurement}.{key}"] = canon(value)
    return flat


def parse_pattern(pattern):
    """Parse an expected-list pattern under a POSITIVE grammar. Returns (parsed, why); one is None.

    THE GRAMMAR IS THE SHAPE `flatten` EMITS, AND NOTHING ELSE:

        M-1 '[' selector ']' '.' field      -- the row measurement, one row per file
        M-k '.' field                       -- the block measurements, k in BLOCK_MEASUREMENT_IDS

    `*` is a SELECTOR-space device. It may appear inside the `M-1` bracket, where it ranges over
    FILES, and nowhere else; the terminal field name is always a literal. That single rule is what
    makes "swallow every field of an object" UNREACHABLE rather than checked-for -- a pattern must
    terminate in one literal field name, so it cannot match two fields that differ in field name.

    AND THE SELECTOR IS A BARE `*` OR AN EXACT LITERAL -- PARTIALS ARE REFUSED. Ruled by Joseph on
    2026-08-25, section 12.2.1 of `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`, after a
    grader returned "(c), an ambiguity requiring a specification decision" on measured controls.
    This code previously argued the opposite -- that permitting a partial "costs nothing in the
    breadth direction, because whatever a partial selector matches the already-legal bare `*`
    matches too". That argument is sound and is the WRONG COMPARISON: it measures a whitelist entry
    against the most permissive form available instead of against the literal actually on the table.
    Two measurements retired it, both on the real `M1_FILES` population and neither hypothetical:

      * `M-1[nd-unfolding/unified_throw_cov*].first_insert` was ACCEPTED with no warning and reaches
        TWO files -- `unified_throw_cov.py` and `unified_throw_cov_5d.py` -- where the literal form
        reaches one. A reviewer sees something shaped like a file path and reads it as one file. The
        file it silently picks up is the row whose omission WAS the F-17(a) failure.
      * a partial's reach is not stable as the population grows: add one plausible file and
        `M-1[nd-unfolding/bootstrap*]` goes 1 -> 2, silently, while the literal stays 1.

    That second property is the exact reason this guard already refuses `M-4.behin*`, which reaches
    one field TODAY -- so the inconsistency was internal: the guard applied the silent-widening rule
    in field space and not in selector space. A literal is stable; a bare `*` is honest about
    covering everything; a partial looks specific and moves. Measured compatibility cost of the
    narrowing: ZERO -- 0 of 30 `UNITS` patterns and 0 shipped expected-list entries use one.

    WHY A GRAMMAR REPLACED A DENY-LIST. The predecessor asked whether the pattern's last DOTTED
    segment was `*`. A dotless pattern has no last segment, so `M-1[*` was compared whole against
    `"*"`, was accepted, and matched every M-1 field -- 19 real findings suppressed with no warning
    (defect D-3). Its review fixture listed six remembered spellings and omitted that one, and a
    fixture enumerated from the same intuition as the rule cannot disagree with the rule. Adding a
    seventh spelling would have left `M-6[*` and `M-4.*e*`, both measured fail-open in the same
    class. A grammar cannot EXPRESS the class, so there is no spelling left to remember.
    """
    if not isinstance(pattern, str) or not pattern:
        return None, "a field pattern must be a non-empty string"
    head = pattern[:3]
    if head not in MEASUREMENT_IDS:
        return None, (f"'{pattern}' does not begin with a measurement id "
                      f"({MEASUREMENT_IDS[0]}..{MEASUREMENT_IDS[-1]})")
    rest = pattern[3:]
    if not rest:
        return None, f"'{pattern}' is a bare measurement id and would whitelist all of it; name fields"
    if head == ROW_MEASUREMENT_ID:
        if not rest.startswith("["):
            return None, (f"'{pattern}': {ROW_MEASUREMENT_ID} is measured once PER FILE, so its"
                          f" patterns are"
                          f" {ROW_MEASUREMENT_ID}[<exact file path or {WILDCARD}>].<field>")
        close = rest.find("]")
        if close < 0:
            return None, (f"'{pattern}': the '[' selector is never closed. THIS IS DEFECT D-3: the"
                          f" per-file form with its ']' dropped used to pass the guard and then"
                          f" match every field of every file.")
        selector, after = rest[1:close], rest[close + 1:]
        if not selector:
            return None, f"'{pattern}': the selector between '[' and ']' is empty"
        if not after.startswith("."):
            return None, (f"'{pattern}': after ']' the next character must be '.', followed by one"
                          f" literal field name")
        field = after[1:]
    else:
        if "[" in rest or "]" in rest:
            return None, (f"'{pattern}': only {ROW_MEASUREMENT_ID} is measured per file, so {head}"
                          f" takes no '[...]' selector and this pattern can match nothing")
        if not rest.startswith("."):
            return None, (f"'{pattern}': after the measurement id the next character must be '.'"
                          f" (or '[' for {ROW_MEASUREMENT_ID})")
        selector, field = None, rest[1:]
    if not field:
        return None, f"'{pattern}': the field name after '.' is empty"
    if WILDCARD in field:
        return None, (f"'{pattern}': the field name '{field}' carries a wildcard, which would"
                      f" whitelist more than one field of that object. The wildcard is a"
                      f" SELECTOR-space device -- legal inside {ROW_MEASUREMENT_ID}[...] and"
                      f" nowhere else, and there only as the WHOLE selector. Name the field.")
    # THE SELECTOR IS A BARE WILDCARD OR AN EXACT LITERAL, AND NOTHING BETWEEN (Joseph, 2026-08-25).
    # Checked LAST, after every structural check, so that no pattern refused before this ruling
    # changes the reason it is refused: the only patterns whose behaviour moves are the ones that
    # parsed clean AND carried a partial selector.
    if selector is not None and selector != WILDCARD and WILDCARD in selector:
        return None, (f"'{pattern}': the selector '{selector}' is a PARTIAL wildcard. Inside"
                      f" {ROW_MEASUREMENT_ID}[...] exactly two forms are legal: the bare"
                      f" '{WILDCARD}', which is visibly EVERY file, or ONE exact literal file path."
                      f" A partial is neither -- it reads as one file, can already cover several,"
                      f" and its reach moves silently when the measured file population changes."
                      f" Name the file, or use '{WILDCARD}'.")
    return {"measurement": head, "selector": selector, "field": field}, None


def matcher_probes(parsed):
    """Canary field paths for one parse: (the field it must match, [(why, field it must not)]).

    Built in the shape `flatten` emits, from the PARSE rather than from the pattern text, so the
    probes do not inherit whatever the grammar got wrong about the text.
    """
    mid, selector, field = parsed["measurement"], parsed["selector"], parsed["field"]
    other = next(m for m in BLOCK_MEASUREMENT_IDS if m not in (mid, PERISHABLE_ID))
    if selector is None:
        live = f"{mid}.{field}"
        sibling = f"{mid}.{PROBE_FIELD}"
        longer, shorter = f"{mid}.{field}{PROBE_FIELD}", f"{mid}.{PROBE_FIELD}{field}"
    else:
        concrete = selector.replace(WILDCARD, PROBE_PATH)
        live = f"{mid}[{concrete}].{field}"
        sibling = f"{mid}[{concrete}].{PROBE_FIELD}"
        longer = f"{mid}[{concrete}].{field}{PROBE_FIELD}"
        shorter = f"{mid}[{concrete}].{PROBE_FIELD}{field}"
    forbidden = [
        ("a sibling field of the same object", sibling),
        ("a field whose name merely BEGINS with this one", longer),
        ("a field whose name merely ENDS with this one", shorter),
        ("the same field name under a different measurement", f"{other}.{field}"),
    ]
    if mid != PERISHABLE_ID:
        forbidden.append((f"a {PERISHABLE_ID} field, which is never suppressible",
                          f"{PERISHABLE_ID}.{field}"))
    return live, forbidden


def matcher_disagreement(pattern, parsed):
    """Ask `field_matches` ITSELF what this pattern does, or None. Fails closed on any surprise.

    THE GUARD AND THE MATCHER ARE TWO IMPLEMENTATIONS OF ONE LANGUAGE, and their divergence is the
    whole of defect D-3: the guard reasoned with `rsplit(".")` while matching is done by
    `split("*")`, so the guard's picture of `M-1[*` ("a dotless string, not a wildcard segment")
    and the matcher's ("prefix M-1[, empty suffix, matches everything") were both internally
    consistent and not the same language. Restating the grammar more carefully would have produced
    a third model. This arm instead CALLS the matcher on canary fields, so a future hole in
    `parse_pattern` is caught by the component that would exploit it.

    Both directions are checked. Over-broad -- the matcher reaches a field the parse does not name
    -- is the direction that silently suppresses real findings. Matches-nothing is the opposite
    direction and is refused too: an entry that can never apply is a dead whitelist row that reads
    as live cover, which is precisely the F-17(a) `fnmatch` failure `field_matches` exists to fix.

    Under the current grammar no arm here can fire through `bad_pattern`; that is the point of a
    backstop, and it is why its own test calls this function directly with a parse the grammar
    would never produce, rather than scoring it caught through a path that cannot reach it.
    """
    live, forbidden = matcher_probes(parsed)
    if not field_matches(pattern, live):
        return (f"'{pattern}' matches NOTHING it names: the matcher does not match '{live}', the"
                f" field this pattern parses as. A whitelist entry that can never apply is a dead"
                f" row that reads as live cover -- the F-17(a) failure mode -- so it is refused"
                f" rather than shipped silent.")
    for why, probe in forbidden:
        if field_matches(pattern, probe):
            return (f"'{pattern}' is OVER-BROAD: the grammar reads it as one field but the matcher"
                    f" also matches '{probe}' ({why}). The guard and the matcher disagree about"
                    f" this pattern, which is defect D-3's mechanism; failing closed.")
    return None


def bad_pattern(pattern):
    """Why this expected-list pattern may not be used, or None. A whitelist that can swallow a whole
    measurement is not reviewable, and M-2 may not be whitelisted at all.

    Three layers, in order: the grammar (`parse_pattern`) makes breadth inexpressible, the M-2 rule
    keeps the perishable claim unsuppressible, and `matcher_disagreement` backstops both by asking
    the matcher rather than a second model of it.
    """
    parsed, why = parse_pattern(pattern)
    if why is not None:
        return why
    if parsed["measurement"] == PERISHABLE_ID:
        return (f"'{pattern}' targets {PERISHABLE_ID}, which F-17(b) names as the perishable claim."
                f" {PERISHABLE_ID} differences are never expected and never suppressible.")
    return matcher_disagreement(pattern, parsed)


def resolve_one_citation(entry_id, pattern, citation, repo):
    """Resolve a single citation against `repo`, or refuse. Returns the recorded citation."""
    where = f"entry {entry_id}, field {pattern!r}"
    if not isinstance(citation, dict):
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"{where}: the citation is not an object. An expected difference with no "
                      f"citation is a judgement, and this list holds declarations.")
    doc_rel, quote = citation.get("doc"), citation.get("quote")
    if not isinstance(doc_rel, str) or not doc_rel:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"{where}: the citation has no 'doc' path")
    if not isinstance(quote, str) or not quote.strip():
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"{where}: the citation has no 'quote'")
    cited = repo / doc_rel
    if not cited.is_file():
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"{where}: the cited document does not exist under --repo: {cited}")
    text = cited.read_text(encoding="utf-8", errors="replace")
    if quote not in text:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"{where}: the quote is not in {doc_rel}. An unresolved citation is a hard "
                      f"error: this list is a whitelist and may not become a silent suppressor.")
    matched = [n + 1 for n, line in enumerate(text.splitlines()) if quote in line]
    if not matched:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"{where}: the quote occurs in {doc_rel} but on no single LINE, so it spans a"
                      f" line break and names no locatable passage. Quote one line.")
    if len(matched) > MAX_CITATION_LINES:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"{where}: the quote matches {len(matched)} lines of {doc_rel} (the limit is "
                      f"{MAX_CITATION_LINES}). A quote that matches everywhere locates nothing: this"
                      f" is a citation of no informational content, and a one-character quote is the"
                      f" limiting case. Quote the passage you mean.")
    measured_digest = sha256_of(cited)
    declared = citation.get("doc_sha256")
    if isinstance(declared, str) and declared and declared != measured_digest:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"{where}: {doc_rel} is sha256 {measured_digest[:12]}, the entry pins "
                      f"{declared[:12]}. The cited document moved; re-read it and re-declare.")
    return {"doc": doc_rel, "quote": quote, "doc_sha256_measured": measured_digest,
            "doc_sha256_declared": declared if isinstance(declared, str) else None,
            "matched_lines": matched}


def resolve_citations(entry_id, fields, raw_entry, repo):
    """ONE CITATION PER FIELD PATTERN, and that is the second thing this guard learned.

    The first version accepted one `citation` for a whole `fields` list, and the very first entry
    shipped under it was wrong in exactly the way that licence permits. `E1-m4-behind-and-ahead-drift`
    claimed `M-4.behind` AND `M-4.ahead` on a citation whose heading is "the BEHIND-COUNT has moved
    twice" and whose only mention of ahead is `ahead = 0 ; --is-ancestor rc=0` -- a STABLE ZERO, and
    affirmative evidence that the tree carried no commits of its own. The citation did not merely
    fail to support the second field; it recorded the opposite, and the guard passed because it
    checks that a quote RESOLVES and is PRESENT, never that it is ABOUT the field.

    Resolving is still not supporting -- no mechanical check can read a quote's aboutness, and this
    is stated so a green run is not over-read. What the shape can do is stop ONE quote licensing a
    LIST, so that every suppressed field has a citation a reviewer can read beside it, and a second
    field cannot ride in on the first field's evidence.
    """
    single, per_field = raw_entry.get("citation"), raw_entry.get("citations")
    if single is not None and per_field is not None:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"entry {entry_id}: declares both 'citation' and 'citations'; which one "
                      f"licenses which field is then a guess")
    if single is not None:
        if len(fields) != 1:
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                          f"entry {entry_id}: a single 'citation' may license exactly ONE field "
                          f"pattern, and this entry names {len(fields)} ({list(fields)}). One quote "
                          f"licensing a field list is how a whitelist widens silently: use "
                          f"'citations', a mapping from each pattern to its own citation.")
        return {fields[0]: resolve_one_citation(entry_id, fields[0], single, repo)}
    if not isinstance(per_field, dict) or not per_field:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"entry {entry_id}: no 'citation' and no 'citations' mapping")
    missing = [pattern for pattern in fields if pattern not in per_field]
    if missing:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"entry {entry_id}: 'citations' has no entry for {missing}; every suppressed "
                      f"field needs its own citation")
    extra = [key for key in per_field if key not in fields]
    if extra:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"entry {entry_id}: 'citations' names {extra}, which are not in 'fields'; a "
                      f"citation for a field this entry does not claim is dead evidence")
    return {pattern: resolve_one_citation(entry_id, pattern, per_field[pattern], repo)
            for pattern in fields}


def load_expected(path_text, repo):
    """The declared-expected list, with every citation RESOLVED. Any failure is exit 5."""
    path = pathlib.Path(path_text)
    if not path.is_file():
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"no expected-differences file at {path}")
    raw = path.read_bytes()
    if not raw.strip():
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"the expected-differences file is empty: {path}")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"the expected-differences file is not json: {exc}")
    if not isinstance(doc, dict) or doc.get("schema") != EXPECTED_SCHEMA:
        found = doc.get("schema") if isinstance(doc, dict) else None
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      f"the expected-differences file must declare schema {EXPECTED_SCHEMA!r}, "
                      f"found {found!r}")
    entries = doc.get("entries")
    if not isinstance(entries, list):
        raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                      "the expected-differences file has no 'entries' list")
    seen, out = set(), []
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, "an entry is not an object")
        entry_id = raw_entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, "an entry has no string 'id'")
        if entry_id in seen:
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"duplicate entry id {entry_id!r}")
        seen.add(entry_id)
        fields = raw_entry.get("fields")
        if not isinstance(fields, list) or not fields:
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                          f"entry {entry_id}: 'fields' must be a non-empty list")
        for pattern in fields:
            why = bad_pattern(pattern)
            if why:
                raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"entry {entry_id}: {why}")
        rule = raw_entry.get("rule")
        if not isinstance(rule, dict) or rule.get("kind") not in ("may-differ", "max-abs-delta"):
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                          f"entry {entry_id}: 'rule.kind' must be 'may-differ' or 'max-abs-delta'")
        if rule["kind"] == "max-abs-delta":
            value = rule.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                              f"entry {entry_id}: max-abs-delta needs a numeric 'value'")
        citations = resolve_citations(entry_id, fields, raw_entry, repo)
        out.append({"id": entry_id, "fields": list(fields), "rule": dict(rule),
                    "why": raw_entry.get("why", ""), "citations": citations,
                    "used": False})
    return {"path": str(path.resolve()), "sha256": sha256_of(path), "entries": out}


def evaluate_rule(rule, values):
    """Joint, over ALL n values at once. Returns (satisfied, detail)."""
    if rule["kind"] == "may-differ":
        # THE SECOND MECHANISM. `compare` already refuses to consult the list for an absent field, so
        # this arm is unreachable through `main` -- and it is here because the last time this
        # instrument had one guard behind another, deleting the inner one changed no test result and
        # the survey scored it caught. Its own arm calls `evaluate_rule` directly.
        if any(value == ABSENT for value in values):
            return False, {"kind": "may-differ",
                           "reason": "a value is ABSENT: 'may differ' is a licence about how a"
                                     " measurement MOVES, never about it being missing; failing"
                                     " closed"}
        return True, {"kind": "may-differ"}
    numeric = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if len(numeric) != len(values):
        return False, {"kind": "max-abs-delta", "value": rule["value"],
                       "reason": "a value is absent or non-numeric, so the tolerance cannot be "
                                 "applied; failing closed"}
    spread = max(numeric) - min(numeric)
    return spread <= rule["value"], {
        "kind": "max-abs-delta", "value": rule["value"], "joint_spread": spread,
        "min": min(numeric), "max": max(numeric),
        "note": "the spread is max-min over ALL n inputs, never composed from pairs"}


def compare(records, expected):
    identities = [identity_of(record) for record in records]
    flats = [flatten(record["doc"], record["index"]) for record in records]
    field_sets = [frozenset(flat) for flat in flats]
    all_fields = sorted(set().union(*field_sets)) if field_sets else []
    field_set_differs = len(set(field_sets)) > 1

    findings = []
    for field in all_fields:
        values = [flat.get(field, ABSENT) for flat in flats]
        distinct = {json.dumps(value, sort_keys=True) for value in values}
        if len(distinct) == 1:
            continue
        unit, population, unit_declared = unit_of(field)
        measurement = field[:3]
        classification, matched = "UNEXPECTED", []
        absent_somewhere = any(value == ABSENT for value in values)
        if measurement == PERISHABLE_ID:
            reason = (f"{PERISHABLE_ID} is the perishable claim F-17(b) singles out; its differences"
                      f" are never expected and never suppressible")
        elif absent_somewhere:
            # A MISSING MEASUREMENT IS NOT A DRIFTING VALUE, and this is the defect that needed no
            # actor to trigger. `may-differ` returned True without looking at the values, so the one
            # shipped entry -- written to excuse M-4.behind's drift -- also excused M-4.behind not
            # having been TAKEN: two documents differing only in that one lacked the key came back
            # exit 10, DIFFERENCES-ALL-EXPECTED. A truncated write, a partial measurement or a
            # schema change at the far end reported green. No citation about drift licenses absence,
            # so absence is classified here and the list is never consulted for it.
            reason = ("this measurement is MISSING from at least one document. That is not a drift in"
                      " a value, it is the value not having been taken, and no expected-difference"
                      " entry can license it: a citation about how a number moves says nothing about"
                      " the number being absent.")
        else:
            reason = "no entry in the expected-differences list covers this field"
            covering = [entry for entry in expected["entries"]
                        if any(field_matches(pattern, field) for pattern in entry["fields"])]
            for entry in covering:
                satisfied, detail = evaluate_rule(entry["rule"], values)
                # WHICH pattern licensed this field, and therefore WHICH citation applies. With one
                # citation per pattern, a finding can no longer be annotated with evidence that was
                # filed for a different field.
                pattern = next(p for p in entry["fields"] if field_matches(p, field))
                matched.append({"id": entry["id"], "satisfied": satisfied, "rule_detail": detail,
                                "matched_pattern": pattern,
                                "citation": entry["citations"][pattern]})
                entry["used"] = True
                if satisfied:
                    classification = "EXPECTED-BY-RULING"
            if classification == "EXPECTED-BY-RULING":
                reason = "declared expected by " + "; ".join(
                    m["id"] for m in matched if m["satisfied"])
            elif covering:
                reason = ("an entry covers this field but its rule is NOT satisfied: "
                          + "; ".join(m["id"] for m in matched))
        findings.append({
            "field": field, "measurement": measurement, "unit": unit,
            "unit_declared": unit_declared, "population": population,
            "classification": classification, "reason": reason,
            "absent_from_some_input": absent_somewhere,
            "expected_entries_matched": matched,
            "n_distinct_values": len(distinct),
            "sides": [{"key": identities[i]["key"], "label": identities[i]["label"],
                       "tree_resolved_path": identities[i]["tree_resolved_path"],
                       "input_sha256": identities[i]["input_sha256"],
                       "head": identities[i]["head"],
                       "porcelain_dirty": identities[i]["porcelain_dirty"],
                       "value": values[i]} for i in range(len(records))],
        })

    m2_findings = [f for f in findings if f["measurement"] == PERISHABLE_ID]
    absent_findings = [f for f in findings if f["absent_from_some_input"]]
    unexpected = [f for f in findings if f["classification"] == "UNEXPECTED"]
    if findings:
        code = (EXIT_DIFFERENCES_SOME_UNEXPECTED if unexpected
                else EXIT_DIFFERENCES_ALL_EXPECTED)
    else:
        code = EXIT_NO_DIFFERENCES
    # THE DOCSTRING PROMISED THIS AND THE CODE DID NOT DO IT. `field_set_differs` was a boolean in
    # the record that reached no count and no exit code, while the docstring claimed the instrument
    # "reports that as an unexpected finding". Differing field sets are the visible symptom of two
    # documents from different revisions of the measuring tool, which is the F-17(a) failure exactly.
    # AN EQUIVALENT MUTANT, AND RECORDED AS ONE. Deleting these two lines changes no observable
    # behaviour, because differing field sets always produce at least one field whose value is the
    # ABSENT sentinel on one side, and absence is already classified UNEXPECTED above -- so the
    # forced code always equals the natural one. That makes it defensive redundancy that no arm can
    # pin, not a coverage gap, and the distinction is worth writing down: a survivor list that does
    # not separate "unpinned" from "unpinnable" over-reports its own weakness. It stays because it
    # is the line that makes the docstring's promise true independently of the absence rule.
    if field_set_differs:
        code = EXIT_DIFFERENCES_SOME_UNEXPECTED
    return {
        "schema": SCHEMA,
        "instrument": {"name": pathlib.Path(__file__).name, "version": INSTRUMENT_VERSION,
                       "self_sha256": sha256_of(pathlib.Path(__file__).resolve())},
        "generated_utc": utc(),
        "comparison_mode": ("JOINT over all n inputs. Pairwise agreement is never composed into a "
                            "global verdict: every field's verdict is the distinct-value set over "
                            "all n, and every tolerance is max-min over all n."),
        "global_agreement_inferred_from_pairs": False,
        "input_schema_gaps": {
            "branch_or_detached": "measure_m1_m6.py --json emits no symbolic-ref state",
            "measurement_wall_clock": ("measure_m1_m6.py --json emits no timestamp; the "
                                       "input_file_mtime_utc below is a property of the FILE, not "
                                       "of the measurement"),
            "measuring_instrument_digest": ("measure_m1_m6.py --json does not identify its own "
                                            "revision; field_set_differs is the only visible "
                                            "symptom of two documents from different revisions"),
        },
        "n_inputs": len(records),
        "inputs": identities,
        "expected_list": {"path": expected["path"], "sha256": expected["sha256"],
                          "entries": expected["entries"]},
        "fields_compared": len(all_fields),
        "field_set_differs": field_set_differs,
        "findings": findings,
        "m2_perishable": {
            "measurement": PERISHABLE_ID,
            "status": "DIFFERS" if m2_findings else "IDENTICAL-ACROSS-ALL-INPUTS",
            "fields": [f["field"] for f in m2_findings],
            "note": ("F-17(b) names M-2 as the perishable claim. It is reported here separately so "
                     "it cannot be absorbed into a summary count, it is never suppressible by the "
                     "expected list, and any M-2 difference forces the some-unexpected verdict."),
        },
        "summary": {
            "all_agree": not findings,
            "n_findings": len(findings),
            "n_expected": len(findings) - len(unexpected),
            "n_unexpected": len(unexpected),
            "n_unexpected_excluding_m2": len([f for f in unexpected
                                              if f["measurement"] != PERISHABLE_ID]),
            "n_m2_findings": len(m2_findings),
            "n_absent_findings": len(absent_findings),
            "absent_fields": [f["field"] for f in absent_findings],
            "n_findings_with_undeclared_unit": len([f for f in findings if not f["unit_declared"]]),
            "expected_entries_unused": [e["id"] for e in expected["entries"] if not e["used"]],
        },
        "verdict": EXIT_CODES[code],
        "exit_code": code,
    }


def print_human(record):
    print(f"=== {record['schema']}  n_inputs={record['n_inputs']}  {record['generated_utc']}")
    print(f"--- comparison mode: {record['comparison_mode']}")
    for side in record["inputs"]:
        print(f"  {side['key']}")
        print(f"      tree     {side['tree_resolved_path']}")
        print(f"      HEAD     {side['head']}   porcelain={side['porcelain_dirty']}"
              f"  branch/detached={side['branch_or_detached']}")
        print(f"      document {side['input_path']}")
        print(f"      sha256   {side['input_sha256']}")
        print(f"      file mtime {side['input_file_mtime_utc']}   measured at "
              f"{side['measurement_wall_clock']}")
    expected = record["expected_list"]
    print(f"--- expected-differences list: {expected['path']}  "
          f"sha256={expected['sha256'][:12]}  entries={len(expected['entries'])}")
    for entry in expected["entries"]:
        print(f"      {entry['id']}: {entry['rule']['kind']} over {entry['fields']}")
        for pattern, citation in entry["citations"].items():
            print(f"        {pattern} cites {citation['doc']}:{citation['matched_lines']} "
                  f"sha256={citation['doc_sha256_measured'][:12]}")
    print(f"--- fields compared: {record['fields_compared']}   "
          f"field_set_differs={record['field_set_differs']}")
    if not record["findings"]:
        print("--- NO DIFFERENCES on any compared field, across all inputs jointly.")
    for finding in record["findings"]:
        print(f"--- {finding['classification']}  {finding['field']}")
        print(f"      unit       {finding['unit']}")
        print(f"      population {finding['population']}")
        print(f"      because    {finding['reason']}")
        for side in finding["sides"]:
            print(f"      {side['key']:<30} = {json.dumps(side['value'])}")
    perishable = record["m2_perishable"]
    print(f"--- M-2 PERISHABILITY: {perishable['status']}  fields={perishable['fields']}")
    if record["summary"]["n_absent_findings"]:
        print(f"--- MEASUREMENTS MISSING FROM AT LEAST ONE DOCUMENT: "
              f"{record['summary']['absent_fields']}")
        print("      A missing measurement is not a drifting value. No expected-difference entry "
              "licenses it.")
    if record["field_set_differs"]:
        print("--- FIELD SETS DIFFER between the inputs: the visible symptom of two documents from "
              "different revisions of measure_m1_m6.py")
    summary = record["summary"]
    print(f"--- summary: findings={summary['n_findings']} expected={summary['n_expected']} "
          f"unexpected={summary['n_unexpected']} "
          f"unexpected_excluding_M2={summary['n_unexpected_excluding_m2']} "
          f"m2={summary['n_m2_findings']} "
          f"undeclared_unit={summary['n_findings_with_undeclared_unit']}")
    if summary["expected_entries_unused"]:
        print(f"--- expected entries that matched nothing: {summary['expected_entries_unused']}")
    print(f"=== VERDICT {record['verdict']}  exit {record['exit_code']}")


EPILOG = """exit codes -- a disjoint, documented vocabulary:
   0  NO-DIFFERENCES                 every compared field has one distinct value across all inputs
  10  DIFFERENCES-ALL-EXPECTED       every difference is declared by the --expected list
  20  DIFFERENCES-SOME-UNEXPECTED    at least one difference is undeclared, or is an M-2 difference
   4  REFUSAL-INPUT                  an input is absent, empty, unreadable, or not a document
   5  REFUSAL-EXPECTED-LIST          the expected list is malformed, over-broad, or its citation
                                     does not resolve
   2  REFUSAL-USAGE                  argparse's own
   1  RESERVED. Never a verdict: an uncaught traceback exits 1, so no verdict may share it.

This instrument computes no measurement. Feed it `measure_m1_m6.py --json` documents."""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", action="append", required=True, metavar="JSON",
                       help="a measure_m1_m6.py --json document. Repeat it. No default, "
                            "deliberately; two or more are required.")
    parser.add_argument("--expected", required=True, metavar="JSON",
                       help=f"the declared-expected differences list, schema {EXPECTED_SCHEMA}. "
                            f"No default: an implicit whitelist is not reviewable.")
    parser.add_argument("--repo", required=True, metavar="DIR",
                       help="the tree the expected list's citations are resolved against. No "
                            "default.")
    parser.add_argument("--json", action="store_true",
                       help="emit the comparison record on stdout")
    parser.add_argument("--record", metavar="PATH",
                       help="also write the comparison record here")
    args = parser.parse_args(argv)
    try:
        if len(args.input) < 2:
            raise Refusal(EXIT_REFUSAL_INPUT,
                          f"{len(args.input)} input given; a comparison needs two or more. One "
                          f"document is a measurement, not a comparison.")
        repo = pathlib.Path(args.repo)
        if not repo.is_dir():
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST, f"--repo is not a directory: {repo}")
        repo = repo.resolve()
        # THE WHITELIST MUST BE AN IN-TREE ARTIFACT. Every claim made for this list -- that widening
        # it is a reviewable diff, that its digest can be re-derived from a commit -- is false for a
        # file passed in from outside the tree whose documents it cites. Refusing that removes the
        # whole "whitelist from /tmp" branch at no cost, and it is prevention rather than an audit
        # obligation nobody has yet been given.
        expected_path = pathlib.Path(args.expected).resolve()
        if not expected_path.is_relative_to(repo):
            raise Refusal(EXIT_REFUSAL_EXPECTED_LIST,
                          f"--expected must resolve INSIDE --repo, so that the whitelist is an"
                          f" in-tree artifact whose widening is a reviewable diff.\n"
                          f"    --expected {expected_path}\n    --repo     {repo}")
        expected = load_expected(str(expected_path), repo)
        records = [load_document(text, i) for i, text in enumerate(args.input)]
        record = compare(records, expected)
    except Refusal as refusal:
        print(f"REFUSING ({EXIT_CODES[refusal.code]}): {refusal.message}", file=sys.stderr)
        return refusal.code
    if args.record:
        pathlib.Path(args.record).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(record, indent=2))
    else:
        print_human(record)
    return record["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
