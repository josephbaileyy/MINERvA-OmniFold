"""Prototype 1, complete: let each pinned 2D loader read only the ROOT branches it uses.

The 2D driver (``2d-unfolding/unfold_2d_omnifold_unbinned.py``) never calls
``SetBranchStatus``, so every ``GetEntry`` decompresses every branch of the row: 470 on the
universe omnifile's ``mc_signal_reco``, 236 on ``mc_truth_denom``, 240 on ``mc_background``.
This module wraps the four loaders the driver's ``main()`` calls, without editing them:

* ``fill_data_reco_2d``          (tree ``data``)
* ``fill_bkg_reco_2d``           (tree ``mc_background``)
* ``collect_signal_arrays_2d``   (tree ``mc_signal_reco``)
* ``collect_truth_denom_arrays`` (tree ``mc_truth_denom``)

How the branch set is obtained. It is DERIVED FROM THE LOADER'S OWN ACCESSES, not from a list
kept beside it: the pinned function is first run against ``DiscoveryTree``, which answers the
loader's ``GetBranch``/``GetEntries`` queries from the real tree, records every
``SetBranchAddress`` name without forwarding it, and stops the loader at its first ``GetEntry``,
before any value is read. ``expected_branches`` is a second, static statement of the driver's
selection rules; the two must agree exactly (names and order) or the call is refused. Neither the
real tree's addresses nor its entries are touched during discovery.

How an omission is refused. ``TBranch::SetAddress`` is a no-op on a deactivated branch, so a
branch the loader reads but that was not activated keeps its initial buffer value for every entry
and leaves no address behind. ``SelectiveTree`` therefore refuses at the loader's
``SetBranchAddress`` (a name outside the derived set, or an inactive branch), and again at the
first ``GetEntry`` unless the addressed set, the active set and the derived set are identical and
every derived branch holds a non-null address. Its interface is closed: any attribute other than
the six the pinned loaders use raises, so a loader that started reading through another route
(``GetLeaf``, ``tree.<branch>``) is refused instead of silently reading a stale value.

Tree state. The caller's branch statuses, and the addresses of the branches the loader sets, are
snapshotted on entry and restored exactly in a ``finally``, and the restoration is verified. The
addresses matter: a pinned loader leaves its branches pointing at local buffers that Python frees
when it returns, so a reused, re-activated tree would be written into freed memory by its next
``GetEntry`` (``test_a_reused_tree_is_restored_and_reads_identically_afterwards`` crashed the
interpreter with a segmentation violation before addresses were restored). ``call_all`` leaves the
tree exactly as production does.
"""

import contextlib
import hashlib
import inspect
import io

import numpy as np

#: Loader name -> the tree it reads. The tree is always the loader's first positional argument.
LOADER_TREES = {
    "fill_data_reco_2d": "data",
    "fill_bkg_reco_2d": "mc_background",
    "collect_signal_arrays_2d": "mc_signal_reco",
    "collect_truth_denom_arrays": "mc_truth_denom",
}

#: The only tree methods the pinned loaders call (driver blob e19aeb6d).
_FORWARDED = ("GetBranch", "GetListOfBranches", "GetName", "GetEntries")

_WILDCARD = set("*?[]^$\\")


class SelectionError(RuntimeError):
    """The branch selection could not be derived, applied, verified or restored."""


class UnmodelledAccess(SelectionError):
    """A loader used a tree method this module does not model."""


class _DiscoveryDone(Exception):
    """Raised at the loader's first ``GetEntry`` during discovery."""


def sanitize(band):
    """The C++ ``SanitizeForRootBranchName`` rule (any non-[A-Za-z0-9_] -> ``_``)."""
    return "".join(c if (c.isalnum() or c == "_") else "_" for c in band)


def _cpp():
    import ROOT
    if not hasattr(ROOT, "sb1_branch_address"):
        ROOT.gInterpreter.Declare("""
            #include <cstdint>
            std::uintptr_t sb1_branch_address(TBranch* b) {
                return b ? reinterpret_cast<std::uintptr_t>(b->GetAddress()) : 0; }
            void sb1_restore_address(TTree* t, TBranch* b, std::uintptr_t a) {
                if (a) b->SetAddress(reinterpret_cast<void*>(a)); else t->ResetBranchAddress(b); }
        """)
    return ROOT


def _has_address(branch):
    return _cpp().sb1_branch_address(branch) != 0


def snapshot_addresses(tree, names):
    ROOT = _cpp()
    return [(n, int(ROOT.sb1_branch_address(tree.GetBranch(n)))) for n in names]


def restore_addresses(tree, snapshot):
    """Put back the addresses ``snapshot`` recorded (null on a freshly opened tree).

    After a pinned loader returns, the branches it addressed point at its local buffers, which
    Python then frees. The production driver never reads such a tree again; a reused tree whose
    branches are re-activated would write into freed memory at the next ``GetEntry``.
    """
    ROOT = _cpp()
    for name, addr in snapshot:
        ROOT.sb1_restore_address(tree, tree.GetBranch(name), addr)
    if snapshot_addresses(tree, [n for n, _ in snapshot]) != snapshot:
        raise SelectionError(f"{tree.GetName()}: branch addresses not restored")


def branch_names(tree):
    return [b.GetName() for b in tree.GetListOfBranches()]


def active_names(tree):
    return [n for n in branch_names(tree) if tree.GetBranchStatus(n)]


def snapshot_status(tree):
    return [(n, bool(tree.GetBranchStatus(n))) for n in branch_names(tree)]


def restore_status(tree, snapshot):
    """Put every branch status back to ``snapshot`` and verify it."""
    if all(s for _, s in snapshot):
        tree.SetBranchStatus("*", 1)
    else:
        tree.SetBranchStatus("*", 0)
        for name, status in snapshot:
            if status:
                tree.SetBranchStatus(name, 1)
    if snapshot_status(tree) != snapshot:
        raise SelectionError(f"{tree.GetName()}: branch statuses not restored")


def apply_selection(tree, names):
    """Deactivate every branch, activate exactly ``names``, and verify the active set."""
    present = set(branch_names(tree))
    bad = [n for n in names if n not in present or _WILDCARD & set(n)]
    if bad:
        raise SelectionError(f"{tree.GetName()}: cannot select {bad} (absent or a pattern)")
    tree.SetBranchStatus("*", 0)
    for n in names:
        tree.SetBranchStatus(n, 1)
    got = active_names(tree)
    if sorted(got) != sorted(names):
        raise SelectionError(f"{tree.GetName()}: active set {sorted(got)} != selected "
                             f"{sorted(names)}")


class DiscoveryTree:
    """Answers a loader's schema queries from ``tree`` and records what it would read."""

    def __init__(self, tree):
        self._tree = tree
        self.addressed = []
        self.queried = []
        self.stopped_at_first_entry = False

    def GetBranch(self, name):
        self.queried.append(name)
        return self._tree.GetBranch(name)

    def GetListOfBranches(self):
        return self._tree.GetListOfBranches()

    def GetName(self):
        return self._tree.GetName()

    def GetEntries(self):
        return self._tree.GetEntries()

    def SetBranchAddress(self, name, buf):          # recorded, never forwarded
        self.addressed.append(str(name))
        return 0

    def GetEntry(self, i):
        self.stopped_at_first_entry = True
        raise _DiscoveryDone

    def __getattr__(self, attr):
        raise UnmodelledAccess(f"discovery: the loader used tree.{attr}, which is not modelled")


class SelectiveTree:
    """The loader's view of the real tree under a selection: refuses any unverified read."""

    def __init__(self, tree, names):
        self._tree = tree
        self._names = tuple(names)
        self.addressed = []
        self.verified = False
        self.entries_read_through_guard = 0

    def GetBranch(self, name):
        return self._tree.GetBranch(name)

    def GetListOfBranches(self):
        return self._tree.GetListOfBranches()

    def GetName(self):
        return self._tree.GetName()

    def GetEntries(self):
        return self._tree.GetEntries()

    def SetBranchAddress(self, name, buf):
        if name not in self._names:
            raise SelectionError(f"SetBranchAddress on {name!r}, outside the derived set "
                                 f"{list(self._names)} of {self._tree.GetName()}")
        if not self._tree.GetBranchStatus(name):
            raise SelectionError(f"SetBranchAddress on inactive branch {name!r} of "
                                 f"{self._tree.GetName()}")
        self.addressed.append(name)
        return self._tree.SetBranchAddress(name, buf)

    def verify(self):
        """The check that must pass before the first entry is read."""
        tree, want = self._tree, sorted(self._names)
        if sorted(self.addressed) != want:
            raise SelectionError(f"{tree.GetName()}: addressed {sorted(self.addressed)} != "
                                 f"derived {want}")
        if sorted(active_names(tree)) != want:
            raise SelectionError(f"{tree.GetName()}: active {sorted(active_names(tree))} != "
                                 f"derived {want}")
        missing = [n for n in want if not _has_address(tree.GetBranch(n))]
        if missing:
            raise SelectionError(f"{tree.GetName()}: no address on {missing}")
        self.verified = True

    def GetEntry(self, i):
        self.verify()
        self.entries_read_through_guard += 1
        self.GetEntry = self._tree.GetEntry           # verified: later reads go straight to ROOT
        return self._tree.GetEntry(i)

    def __getattr__(self, attr):
        raise UnmodelledAccess(f"the loader used tree.{attr}, which is not modelled")


def bound_settings(func, args, kwargs):
    """The loader's arguments by name, defaults applied, tree and histogram objects omitted."""
    ba = inspect.signature(func).bind(None, *args, **kwargs)
    ba.apply_defaults()
    out = {}
    for k, v in ba.arguments.items():
        if k.startswith(("t_", "h_")):
            continue
        out[k] = list(v) if isinstance(v, tuple) else v
    return out


def expected_branches(loader, settings, present):
    """The driver's selection rules, stated independently of the access record.

    ``present`` is the set of branch names in the tree. Mirrors driver blob e19aeb6d:
    ``fill_data_reco_2d`` 211-219, ``fill_bkg_reco_2d`` 280-303, ``collect_truth_denom_arrays``
    551-572 and ``collect_signal_arrays_2d`` 636-690. The alt-model closure path is refused.
    """
    uni = settings.get("universe_branch")
    sfx = f"{sanitize(uni[0])}_{int(uni[1])}" if uni is not None else None

    def lateral(a, b):
        return (a, b) if (a in present and b in present) else None

    if loader == "fill_data_reco_2d":
        return ["measured", "measured_pz", "measured_pass"]
    if loader == "fill_bkg_reco_2d":
        kin, w = ("sim_background", "sim_background_pz"), "w_bkg"
        if uni is not None:
            w = f"w_bkg_{sfx}"
            kin = lateral(f"sim_background_{sfx}", f"sim_background_pz_{sfx}") or kin
        return [kin[0], kin[1], "sim_background_pass", w]
    use_w = bool(settings.get("use_weights"))
    if loader == "collect_truth_denom_arrays":
        kin, w = ("MC", "MC_pz"), "w_truth"
        if use_w and uni is not None:
            w = f"w_truth_{sfx}"
            kin = lateral(f"pT_truth_{sfx}", f"pz_truth_{sfx}") or kin
        return [kin[0], kin[1]] + ([w] if use_w else [])
    if loader == "collect_signal_arrays_2d":
        if settings.get("alt_universe_branch") is not None:
            raise SelectionError("the alt-model closure path is not part of SB1")
        mc, sim, wts = ("MC", "MC_pz"), ("sim", "sim_pz"), ("w_truth", "w_reco")
        if use_w and uni is not None:
            wts = (f"w_truth_{sfx}", f"w_reco_{sfx}")
            mc = lateral(f"MC_{sfx}", f"MC_pz_{sfx}") or mc
            sim = lateral(f"sim_{sfx}", f"sim_pz_{sfx}") or sim
        return [mc[0], mc[1], sim[0], sim[1], "sim_pass"] + (list(wts) if use_w else [])
    raise SelectionError(f"no selection rule for loader {loader!r}")


def discover(func, tree, args, kwargs):
    """Run ``func`` against a ``DiscoveryTree``; return the names it addresses, in order."""
    proxy = DiscoveryTree(tree)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            func(proxy, *args, **kwargs)
        except _DiscoveryDone:
            pass
    return proxy.addressed, proxy


def derive(func, tree, args, kwargs):
    """The access-derived branch list, refused unless it equals the static rule."""
    names, _ = discover(func, tree, args, kwargs)
    want = expected_branches(func.__name__, bound_settings(func, args, kwargs),
                             set(branch_names(tree)))
    if names != want:
        raise SelectionError(f"{func.__name__}: accesses {names} != rule {want}")
    if len(set(names)) != len(names):
        raise SelectionError(f"{func.__name__}: a branch is addressed twice: {names}")
    return names


def call_selective(func, tree, *args, extra=(), omit=(), **kwargs):
    """Run the pinned loader on ``tree`` with only its derived branches active.

    ``extra`` and ``omit`` exist only for negative controls: they perturb the APPLIED set while the
    guard still checks against the derived one, so each must be refused before the first read.
    Returns ``(result, record)``.
    """
    snap = snapshot_status(tree)
    names = derive(func, tree, args, kwargs)
    addresses = snapshot_addresses(tree, names)
    applied = [n for n in names if n not in omit] + [n for n in extra if n not in names]
    guard = SelectiveTree(tree, names)
    try:
        apply_selection(tree, applied)
        result = func(guard, *args, **kwargs)
        if not guard.verified:                        # an empty tree never calls GetEntry
            guard.verify()
    finally:
        restore_status(tree, snap)
        restore_addresses(tree, addresses)
    return result, {"mode": "selective", "branches": names,
                    "n_branches_in_tree": len(snap),
                    "n_active_on_entry": sum(s for _, s in snap),
                    "verified_before_first_read": guard.verified}


def call_all(func, tree, *args, **kwargs):
    """Run the pinned loader exactly as production does, refusing unless every branch is active."""
    snap = snapshot_status(tree)
    if not all(s for _, s in snap):
        raise SelectionError(f"{tree.GetName()}: production arm entered with inactive branches")
    result = func(tree, *args, **kwargs)
    return result, {"mode": "all", "branches": None, "n_branches_in_tree": len(snap),
                    "n_active_on_entry": len(snap), "verified_before_first_read": None}


def array_digest(a):
    a = np.asarray(a)
    h = hashlib.sha256()
    h.update(f"{a.dtype.str}|{a.shape}|".encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def hist_digest(h):
    """Contents, Sumw2, statistics and entries of a TH2, as bytes."""
    nx, ny = h.GetNbinsX() + 2, h.GetNbinsY() + 2
    cont = np.array([h.GetBinContent(i, j) for i in range(nx) for j in range(ny)])
    sw2 = h.GetSumw2()
    err2 = (np.array([sw2.At(h.GetBin(i, j)) for i in range(nx) for j in range(ny)])
            if sw2.GetSize() else np.zeros(0))
    stats = np.zeros(13)
    h.GetStats(stats)
    blob = cont.tobytes() + err2.tobytes() + stats.tobytes() + np.float64(h.GetEntries()).tobytes()
    return hashlib.sha256(blob).hexdigest()


def result_digests(loader, result, hist=None):
    """sha256 of every array (dtype, shape and bytes) a loader returns, plus its filled histogram."""
    if isinstance(result, dict):
        out = {k: array_digest(v) for k, v in sorted(result.items())}
        sizes = {k: int(np.asarray(v).size) for k, v in result.items()}
    else:
        out = {f"[{i}]": array_digest(v) for i, v in enumerate(result)}
        sizes = {f"[{i}]": int(np.asarray(v).size) for i, v in enumerate(result)}
    if hist is not None:
        out["histogram"] = hist_digest(hist)
    return {"loader": loader, "digests": out, "sizes": sizes}
