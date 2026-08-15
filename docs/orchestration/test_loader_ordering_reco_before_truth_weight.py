"""OI-124: the retirement argument for the OI-120(c) `P4` arm, as a CHECK rather than a sentence.

WHAT THIS REPLACES. `P4` of `probe-oi120c-loader-purity-perturbation-20260814.py` perturbed the NPZ
key `w_truth` and required `event_reco` to be bit-identical. It could not fail, and not by accident:
in `build_fullevent_loaders`, `event_reco` is fully assigned by `build_event_features` -- the point at
which the probe raises `_Captured` -- BEFORE the loader has read `w_truth` at all. An array cannot
depend on bytes that were never read, so `P4`'s predeclared `IDENTICAL` was entailed by control flow.
Job 56975592 recorded it as `proxy_hits: 0`, `arrays_actually_changed: {}` -- VOID.

THE ARGUMENT IS STRONGER THAN THE ARM, WHICH IS WHY THE ARM GOES. A perturbation arm samples: it
shows `event_reco` did not move for the one perturbation tried. Ordering PROVES: no perturbation of
`w_truth`, of any magnitude or structure, can move `event_reco`, because the value is finished before
the key is read. Retiring `P4` trades a sample for a proof.

WHY THIS IS A TEST AND NOT A PARAGRAPH IN A FINDING (BEN-228). A proof about source code is only as
durable as the source it was read against; a line number is not an argument, and a hand-maintained
index of a machine-derivable fact goes stale silently. So this file DERIVES the ordering from the
current source on every run and never records a coordinate. If somebody moves a `w_truth` read above
`build_event_features`, or hands the NPZ handle to a helper before it, or rebinds `event_reco` after
it, the retirement's premise is false and this fails -- loudly, at zero cluster cost.

WHY THE MUTANTS. A guard nobody has seen fail is indistinguishable from a guard that cannot fail --
which is the exact defect `P4` turned out to be, and repeating it here would be comic. `audit()` is
therefore run against deliberately corrupted copies of the real source, one per premise, and each is
required to FAIL. The negative controls ship with the guard rather than being observed once by hand.

SCOPE, stated because the trees fork. This binds the TRACKED loader in this checkout. Job 56975592
ran against `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, which is at a different commit with
uncommitted paths (`OI-74`). The premise must be re-derived against whatever checkout a future probe
run uses -- point `MNV_LOADER` at it and run this file.

Run: `python3 -m pytest docs/orchestration/test_loader_ordering_reco_before_truth_weight.py -v`
"""
import ast
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LOADER = Path(os.environ.get("MNV_LOADER", REPO / "nd-unfolding/pet/fullevent_fps_dataloader.py"))

FUNC = "build_fullevent_loaders"
PRODUCT = "event_reco"          # the object whose purity OI-120(c) is about
TRUTH_KEY = "w_truth"           # the NPZ key P4 used to perturb
SINK_KW = "reco_evt"            # how the product leaves the function


def _npz_handle(fn):
    """Name bound to the NpzFile inside `fn`, derived rather than assumed to be `d`.

    This is the object the probe's `PerturbedNpz` proxies, so a subscript of THIS name is exactly the
    event a perturbation can intercept. Deriving it means renaming the variable cannot silently make
    every check below vacuous.
    """
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            f = node.value.func
            if isinstance(f, ast.Attribute) and f.attr == "load" and len(node.targets) == 1:
                if isinstance(node.targets[0], ast.Name):
                    return node.targets[0].id
    return None


def _binds(node):
    """Names bound by an assignment-like statement (tuple targets included)."""
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
        targets = [node.target]
    elif isinstance(node, ast.For):
        targets = [node.target]
    else:
        return []
    out = []
    for t in targets:
        out += [n.id for n in ast.walk(t) if isinstance(n, ast.Name)]
    return out


def audit(source, *, func=FUNC, product=PRODUCT, truth_key=TRUTH_KEY, sink_kw=SINK_KW):
    """Re-derive OI-124's retirement premise from `source`. Returns a list of violations (empty = holds).

    Each premise is one thing that must be true for "no perturbation of `truth_key` can move
    `product`" to be a proof rather than a hopeful reading:

      P-FUNC   the function exists at all
      P-NPZ    the NpzFile handle is identifiable (else every subscript check below is vacuous)
      P-ONCE   `product` is bound exactly ONCE anywhere in the function. This carries the whole
               "captured object == emitted object" half of the argument: a rebinding before the
               capture is a different object, and one after it means the probe captured a value the
               loader then replaced. Both are `bound != 1`, so one premise covers both directions.
      P-USED   `truth_key` IS read somewhere in the function. Without this the guard passes trivially
               the day the key is renamed, which is the failure mode of asserting an absence.
      P-ORDER  every read of `truth_key` is strictly after the binding of `product`
      P-ESCAPE the NPZ handle is not passed to a call, or aliased, before the binding -- otherwise a
               helper could read `truth_key` on our behalf and P-ORDER would be blind to it
      P-LINEAR no loop encloses the binding or any `truth_key` read, so source order IS execution
               order for them (branches can skip a statement; only a loop can reorder one)
      P-FIXED  `product` is not rebound after its binding, and reaches `sink_kw=` -- so the object the
               probe captured at the binding is the object the loader emits
    """
    v = []
    tree = ast.parse(source)
    fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == func]
    if len(fns) != 1:
        return [f"P-FUNC: expected exactly 1 `{func}`, found {len(fns)}"]
    fn = fns[0]

    npz = _npz_handle(fn)
    if npz is None:
        return [f"P-NPZ: no `<name> = *.load(...)` binding found in `{func}`"]

    binds = [n for n in ast.walk(fn) if product in _binds(n)]
    if len(binds) != 1:
        return [f"P-ONCE: `{product}` bound {len(binds)} times in `{func}` (expected exactly 1) "
                f"at lines {sorted(n.lineno for n in binds)}"]
    prod_at = binds[0].lineno

    reads = [(n.lineno, n.slice.value) for n in ast.walk(fn)
             if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
             and n.value.id == npz and isinstance(n.slice, ast.Constant)]
    truth_reads = sorted(l for l, k in reads if k == truth_key)

    if not truth_reads:
        v.append(f"P-USED: `{npz}[{truth_key!r}]` is never read in `{func}` -- the ordering premise "
                 f"would hold vacuously, which is not the claim OI-124 retired P4 on")
    else:
        early = [l for l in truth_reads if l <= prod_at]
        if early:
            v.append(f"P-ORDER: `{npz}[{truth_key!r}]` read at {early} at-or-before `{product}` is "
                     f"bound (line {prod_at}) -- P4's retirement premise is FALSE")

    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and n.lineno <= prod_at:
            handed = [a for a in list(n.args) + [k.value for k in n.keywords]
                      if isinstance(a, ast.Name) and a.id == npz]
            if handed:
                v.append(f"P-ESCAPE: NPZ handle `{npz}` passed to `{ast.unparse(n.func)}` at line "
                         f"{n.lineno}, before `{product}` is bound -- that callee may read "
                         f"{truth_key!r} unseen by P-ORDER")
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Name) and n.value.id == npz \
                and n.lineno <= prod_at:
            v.append(f"P-ESCAPE: NPZ handle aliased at line {n.lineno}, before `{product}` is bound "
                     f"-- reads through the alias are unseen by P-ORDER")

    watched = set(truth_reads) | {prod_at}
    for n in ast.walk(fn):
        if isinstance(n, (ast.For, ast.While, ast.AsyncFor)):
            inside = {ln for ln in watched if n.lineno <= ln <= (n.end_lineno or n.lineno)}
            if inside:
                v.append(f"P-LINEAR: a loop at line {n.lineno} encloses {sorted(inside)} -- source "
                         f"order no longer implies execution order for those statements")

    # NB no separate "rebound after capture" check: P-ONCE above already returns on `bound != 1`, so
    # such a check would be unreachable. It was written, observed unreachable against the rebinding
    # mutant below (which P-ONCE caught instead), and deleted rather than left as decoration.
    sinks = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call)
             for k in n.keywords
             if k.arg == sink_kw and isinstance(k.value, ast.Name) and k.value.id == product]
    if not sinks:
        v.append(f"P-FIXED: `{product}` never reaches `{sink_kw}=` in `{func}` -- cannot show the "
                 f"captured object is the one the loader emits")
    return v


@pytest.fixture(scope="module")
def source():
    assert LOADER.is_file(), f"loader not found: {LOADER}"
    return LOADER.read_text(encoding="utf-8")


def test_retirement_premise_holds_in_the_tracked_loader(source):
    """THE GUARD. `event_reco` is finished before `w_truth` is read, on the source as it stands now.

    This is what OI-124 retired the P4 arm in favour of. If it ever fails, the retirement is void and
    a `w_truth` arm becomes meaningful again -- reopen OI-124, do not silence this.
    """
    assert audit(source) == []


def test_premise_is_about_a_key_that_is_actually_read(source):
    """P-USED, pinned separately: the proof must be `read later`, never `never read`.

    An absence-based guard that also passes when the thing is absent is the shape of BEN-250 -- the
    guard's most reassuring sentence being its empty one.
    """
    assert [v for v in audit(source, truth_key="a_key_this_loader_never_reads")
            if v.startswith("P-USED")], "the vacuity guard did not fire on an absent key"


# ---------------------------------------------------------------------------------------------
# NEGATIVE CONTROLS. Each corrupts one premise in a copy of the real source and requires `audit` to
# say so. A guard is only worth its runtime if it has been seen to fail; these are that observation,
# kept in the suite rather than performed once by hand.
# ---------------------------------------------------------------------------------------------

def _line_of(source, needle):
    for i, line in enumerate(source.splitlines(), 1):
        if needle in line:
            return i
    raise AssertionError(f"anchor not found in loader source: {needle!r}")


def _insert_before(source, needle, text):
    lines = source.splitlines(keepends=True)
    i = _line_of(source, needle) - 1
    indent = " " * (len(lines[i]) - len(lines[i].lstrip()))
    lines.insert(i, f"{indent}{text}\n")
    return "".join(lines)


ANCHOR = "event_reco, event_truth, event_data, meta = build_event_features("

MUTANTS = [
    ("P-ORDER", "a w_truth read moved above the product",
     lambda s: _insert_before(s, ANCHOR, '_leak = d["w_truth"]')),
    ("P-ESCAPE", "the NPZ handle handed to a helper before the product",
     lambda s: _insert_before(s, ANCHOR, "_leak = evt_blocks(d)")),
    ("P-ESCAPE", "the NPZ handle aliased before the product",
     lambda s: _insert_before(s, ANCHOR, "_alias = d")),
    ("P-ONCE", "the product rebound AFTER it was captured",
     lambda s: _insert_before(s, "from omnifold.dataloader import DataLoader",
                              "event_reco = event_reco * 1.0")),
    ("P-ONCE", "the product bound a second time BEFORE the capture",
     lambda s: _insert_before(s, ANCHOR, "event_reco = None")),
    ("P-FIXED", "the product never reaches the loader's output",
     lambda s: s.replace("reco_evt=event_reco", "reco_evt=None")),
]


@pytest.mark.parametrize("premise,label,mutate",
                         MUTANTS, ids=[f"{p}:{l}" for p, l, _ in MUTANTS])
def test_guard_fails_on_a_mutant(source, premise, label, mutate):
    """RED on demand: corrupt one premise, the guard must name that premise."""
    violations = audit(mutate(source))
    assert any(x.startswith(premise) for x in violations), (
        f"guard stayed silent on a source where {label} -- got {violations}")


def test_mutants_are_real_mutations(source):
    """The mutants must differ from the real source and still parse.

    Without this, a mutation that silently no-ops would make every negative control above a test of
    nothing -- the same "the perturbation did not perturb" failure that voided P4 in the first place.
    """
    for premise, label, mutate in MUTANTS:
        out = mutate(source)
        assert out != source, f"mutation {premise}:{label} changed nothing"
        ast.parse(out)
