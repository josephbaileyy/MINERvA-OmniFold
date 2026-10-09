"""Prototype 1: read only the branches a loader uses.

``TTree::GetEntry`` reads and decompresses every *active* branch, and every
branch is active by default. The 2D driver's loaders call ``SetBranchAddress``
on four to seven branches and never ``SetBranchStatus``, so on the universe
omnifile each ``GetEntry`` decompresses every universe column of the row.

``restrict_active_branches`` deactivates everything, then activates exactly the
named branches. It does not change which entries are read, their order or the
bytes of any value that is read; the pinned loader runs unchanged after it.

The danger is the opposite defect: a branch the loader reads but this function
did not activate keeps its initial buffer value for every entry, silently.
Pass the tree to the loader through ``ActiveOnlyTree``, which raises at the
loader's ``SetBranchAddress`` call instead.
"""


def signal_branches(use_weights, universe_branch=None, tree=None):
    """Names ``collect_signal_arrays_2d`` reads from ``mc_signal_reco``.

    Mirrors the driver's selection: CV kinematics and weights, or the universe
    weights plus, for a lateral universe present in ``tree``, the shifted
    kinematics. The alt-model closure path is out of scope for this prototype.
    """
    mc, mc_pz, sim, sim_pz = "MC", "MC_pz", "sim", "sim_pz"
    wt, wr = "w_truth", "w_reco"
    if use_weights and universe_branch is not None:
        band, idx = universe_branch
        suffix = "".join(c if (c.isalnum() or c == "_") else "_" for c in band) + f"_{int(idx)}"
        wt, wr = f"w_truth_{suffix}", f"w_reco_{suffix}"
        if tree is not None:
            if tree.GetBranch(f"MC_{suffix}") and tree.GetBranch(f"MC_pz_{suffix}"):
                mc, mc_pz = f"MC_{suffix}", f"MC_pz_{suffix}"
            if tree.GetBranch(f"sim_{suffix}") and tree.GetBranch(f"sim_pz_{suffix}"):
                sim, sim_pz = f"sim_{suffix}", f"sim_pz_{suffix}"
    names = [mc, mc_pz, sim, sim_pz, "sim_pass"]
    if use_weights:
        names += [wt, wr]
    return names


def restrict_active_branches(tree, names):
    """Deactivate every branch of ``tree``, then activate exactly ``names``."""
    missing = [n for n in names if not tree.GetBranch(n)]
    if missing:
        raise KeyError(f"branches absent from {tree.GetName()}: {missing}")
    tree.SetBranchStatus("*", 0)
    for n in names:
        tree.SetBranchStatus(n, 1)


class ActiveOnlyTree:
    """Forward every call to ``tree``, refusing ``SetBranchAddress`` on an inactive branch.

    ``TBranch::SetAddress`` returns early on a deactivated branch, so after the
    fact the branch has neither status nor address and no inspection can tell
    that a loader meant to read it. The refusal has to happen at call time.
    """

    def __init__(self, tree):
        self._tree = tree
        self.addressed = []

    def SetBranchAddress(self, name, buf):
        if not self._tree.GetBranchStatus(name):
            raise RuntimeError(f"SetBranchAddress on inactive branch {name!r} of "
                               f"{self._tree.GetName()}")
        self.addressed.append(name)
        return self._tree.SetBranchAddress(name, buf)

    def __getattr__(self, attr):
        return getattr(self._tree, attr)
