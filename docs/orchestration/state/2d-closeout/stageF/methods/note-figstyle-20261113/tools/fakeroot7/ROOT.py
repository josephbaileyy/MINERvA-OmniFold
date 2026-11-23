"""A stand-in for PyROOT for the family-7 identity test (tools/identity_family7.py): it lets
plot_uncertainty_fig6_7_style.py import, and raises on any use, so a run that passes read no ROOT input."""


def __getattr__(name):
    raise RuntimeError(f"fakeroot7: ROOT.{name} was used; --from-projections must read no ROOT input")
