"""note_palette.py: the note's figure palette (Joseph, 2026-11-17; COMBINED-PLAN.md section 5(a))."""
import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
pal = importlib.import_module("note_palette")

# Machado, Oliveira and Fernandes (2009), severity 1.0, applied to linear RGB.
MACHADO = {
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}
DELTA_E_FLOOR = 14.0


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _rgb_lin(hexs):
    h = hexs.lstrip("#")
    return [_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]


def _lab(lin):
    lin = [min(1.0, max(0.0, v)) for v in lin]
    x = 0.4124564 * lin[0] + 0.3575761 * lin[1] + 0.1804375 * lin[2]
    y = 0.2126729 * lin[0] + 0.7151522 * lin[1] + 0.0721750 * lin[2]
    z = 0.0193339 * lin[0] + 0.1191920 * lin[1] + 0.9503041 * lin[2]
    f = lambda t: t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29  # noqa: E731
    fx, fy, fz = f(x / 0.95047), f(y / 1.0), f(z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _sim(lin, m):
    return [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]


def _min_delta_e(vision):
    labs = {}
    for k in pal.LINE_IDENTITIES:
        lin = _rgb_lin(pal.color(k))
        labs[k] = _lab(lin if vision == "normal" else _sim(lin, MACHADO[vision]))
    ks = list(labs)
    pairs = [(sum((a - b) ** 2 for a, b in zip(labs[p], labs[q])) ** 0.5, p, q)
             for i, p in enumerate(ks) for q in ks[i + 1:]]
    return min(pairs)


def test_delta_e_floor_in_every_vision():
    for vision in ("normal", "protanopia", "deuteranopia", "tritanopia"):
        d, p, q = _min_delta_e(vision)
        assert d >= DELTA_E_FLOOR, f"{vision}: {p} and {q} at CIE76 dE {d:.1f} < {DELTA_E_FLOOR}"


def test_delta_e_rule_fires_on_a_close_pair():
    """The rule is not vacuous: a GENIE CV a shade off this work's red fails it."""
    keep = pal.IDENTITIES["genie_cv"]
    try:
        pal.IDENTITIES["genie_cv"] = (keep[0], "#c8402f") + keep[2:]
        d, p, q = _min_delta_e("normal")
        assert d < DELTA_E_FLOOR and {p, q} == {"this_work", "genie_cv"}
    finally:
        pal.IDENTITIES["genie_cv"] = keep


def test_unique_style_per_identity():
    """Each identity's (colour, line style, marker, face) is its own; the null distribution and Tune v1 share a colour
    and a line, and differ by the fill (the plan's "filled step" against "solid step")."""
    seen = {}
    for k, (_, c, ls, mk, face) in pal.IDENTITIES.items():
        t = (c.lower(), str(ls), mk, face)
        assert t not in seen, f"{k} repeats {seen.get(t)}'s style {t}"
        seen[t] = k


def test_exact_key_lookup_only():
    for bad in ("GENIE", "genie", "GENIE_CV", "genie_cv ", "this work", "tune"):
        try:
            pal.style(bad)
        except KeyError:
            continue
        raise AssertionError(f"{bad!r} resolved; only exact keys may")
    assert pal.style("genie_cv")["color"] == "#CC79A7"
    assert pal.style("genie_mec")["color"] == "#eb6834"


def test_paper_hexes_are_the_paper_producers():
    """The paper identities' colours equal publication/release/figs/make_figs.py's COLORS and its this-work red."""
    src = (ROOT / "publication/release/figs/make_figs.py").read_text()
    tree = ast.parse(src)
    colors = next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "COLORS" for t in n.targets))
    assert pal.color("genie_mec").lower() == colors["GENIE+MEC"].lower()
    assert pal.color("nuwro").lower() == colors["NuWro"].lower()
    assert pal.color("gibuu").lower() == colors["GiBUU"].lower()
    assert pal.color("tune_v1").lower() == colors["GENIE-CV"].lower()  # the paper's Tune/CV blue stays Tune's
    assert 'color="#c0392b"' in src and pal.color("this_work") == "#c0392b"
    assert pal.color("genie_cv") == "#CC79A7"  # Joseph's one new colour


def test_no_side_effects_on_import():
    import subprocess
    code = ("import matplotlib as mpl; before = dict(mpl.rcParams); import note_palette; "
            "assert dict(mpl.rcParams) == before; print('ok')")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip() == "ok", out.stderr


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    for v in ("normal", "protanopia", "deuteranopia", "tritanopia"):
        d, p, q = _min_delta_e(v)
        print(f"{v}: smallest dE {d:.1f} ({p}, {q})")
