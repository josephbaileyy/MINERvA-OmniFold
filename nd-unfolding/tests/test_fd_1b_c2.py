"""fd_1b_c2 (FD-1B-STAGED-ADDENDUM-A2-1.md): #724's gate, the reading through cov2d's code, the draw law, 1B's
graded truth from fine sums, and the calibration's outputs. Every rule is tested in the direction it acts and the
other."""
import itertools
import math
import sys
import unittest
from unittest import mock
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fd_1b_c2 as c2  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s5n_pseudo  # noqa: E402
from xsec_nd import extract_cross_section_nd  # noqa: E402

cp2, cov2d = c2.cp2, c2.cov2d


def ratios(beyond=0, dev=0.25, base=1.0):
    r = np.full(c2.N_CELLS, base)
    r[:beyond] = 1.0 + dev
    return r


class Gate(unittest.TestCase):
    def test_the_constants_are_joseph_s(self):
        self.assertEqual((c2.GATE_K, c2.GATE_DEV, c2.GATE_LOGMEAN, c2.GATE_MAX), (2, 0.20, 0.07, 0.35))
        self.assertEqual((c2.SD_MULT_LOGMEAN, c2.SD_MULT_CELL, c2.UNION_LIMIT), (3.5, 4.3, 0.01))

    def test_i_allows_two_cells_and_stops_at_three(self):
        r2 = np.full(16, 0.995)
        r2[:2] = 1.25
        r3 = r2.copy()
        r3[2] = 1.25
        self.assertTrue(c2.gate_724(r2)["i"])
        self.assertFalse(c2.gate_724(r3)["i"])
        edge = np.ones(16)
        edge[:3] = 1.0 + c2.GATE_DEV              # exactly 0.20 is not beyond
        self.assertEqual(c2.gate_724(edge)["cells_beyond"], 0)
        edge[:3] = np.nextafter(1.0 + c2.GATE_DEV, 2.0)
        self.assertEqual(c2.gate_724(edge)["cells_beyond"], 3)

    def test_ii_at_and_past_its_bound(self):
        at = np.full(16, math.exp(0.07 * (1 - 1e-12)))
        past = np.full(16, math.exp(0.0701))
        self.assertTrue(c2.gate_724(at)["ii"])
        self.assertFalse(c2.gate_724(past)["ii"])
        self.assertFalse(c2.gate_724(1 / past)["ii"])
        self.assertFalse(c2.gate_724(past)["passes"])

    def test_iii_at_and_past_its_bound(self):
        at = 1.0 + c2.GATE_MAX
        while at - 1.0 > c2.GATE_MAX:            # the largest ratio whose |r - 1| is <= 0.35 in float
            at = np.nextafter(at, 0.0)
        r = np.ones(16)
        r[0] = at
        self.assertTrue(c2.gate_724(r)["iii"])
        r[0] = np.nextafter(at, 2.0)
        self.assertFalse(c2.gate_724(r)["iii"])
        self.assertFalse(c2.gate_724(r)["passes"])
        r[0] = 1.0 - c2.GATE_MAX - 1e-9
        self.assertFalse(c2.gate_724(r)["iii"])

    def test_ii_exactly_at_its_bound_passes(self):
        """A mean log of exactly 0.07 is reachable (15 cells at exp(0.07), the 16th searched): it passes (ii)."""
        r = np.full(16, math.exp(0.07))
        x = r[15]
        for _ in range(2500):
            x = np.nextafter(x, 0)
        for _ in range(5000):
            r[15] = x
            if np.mean(np.log(r)) == c2.GATE_LOGMEAN:
                break
            x = np.nextafter(x, 2)
        self.assertEqual(np.mean(np.log(r)), c2.GATE_LOGMEAN)
        self.assertTrue(c2.gate_724(r)["ii"])

    def test_iii_exactly_at_its_bound_passes(self):
        r = np.ones(16)
        r[0] = 0.65                                           # 1 - 0.65 is exactly the double 0.35 (Sterbenz)
        self.assertEqual(abs(r[0] - 1.0), c2.GATE_MAX)
        self.assertTrue(c2.gate_724(r)["iii"])

    def test_i_at_exactly_0_20_is_unreachable(self):
        """The receipt's one equivalent mutant ((i) at >= 0.20): no double r has |r - 1| == 0.20 (r - 1 is exact
        for r in [0.5, 2], and neither 1 + 0.2 nor 1 - 0.2 is representable as such), so > and >= agree on every
        input. Shown on the doubles within 10,000 ulps of 1.2 and of 0.8."""
        for c in (1.2, 0.8):
            r = c
            for _ in range(10_000):
                r = np.nextafter(r, 0)
            for _ in range(20_000):
                self.assertNotEqual(abs(r - 1.0), c2.GATE_DEV)
                r = np.nextafter(r, 2)

    def test_passes_only_when_all_three_hold(self):
        self.assertTrue(c2.gate_724(np.ones(16))["passes"])
        self.assertTrue(c2.gate_724(ratios(2, 0.3, 0.98))["passes"])

    def test_refuses_what_it_is_not_defined_on(self):
        for bad in (np.ones(15), np.r_[np.ones(15), np.nan], np.r_[np.ones(15), 0.0], np.r_[np.ones(15), np.inf]):
            with self.assertRaises(c2.Refusal):
                c2.gate_724(bad)


def record(med, p90, vr, worst, cells=16):
    sig = {"abs_median": list(med), "abs_p90": list(p90)}
    return {"vi": {"largest_cell_unmatched_share": worst},
            "b": {"T": {"option_1": {"sigma_Q": sig}, "variance_ratio": {k: list(v) for k, v in vr.items()}}}}


def grid(cells=16):
    """Records crossing every edge of the reading: medians and p90s at each threshold's two sides and in shares
    either side of each share rule, each composition's gate passing and failing, and the mismatch bounded or not."""
    med_levels = [0.1, cp2.R1_MEDIAN, np.nextafter(cp2.R1_MEDIAN, 1), 0.35, cp2.OPT3_MEDIAN, 0.8]
    p90_levels = [0.3, cp2.R1_P90, np.nextafter(cp2.R1_P90, 1), 0.5, cp2.POS_P90, np.nextafter(cp2.POS_P90, 1)]
    counts = [0, 1, 2, 3, 4, cells]
    vr_pass, vr_fail = np.ones(cells), np.r_[np.full(2, 1.5), np.ones(cells - 2)]
    for ml, mn, pl, pn, gc, gm, worst in itertools.product(med_levels, counts, p90_levels, counts,
                                                          (True, False), (True, False),
                                                          (None, 0.01, cp2.MISMATCH_BOUND, 0.06)):
        med = np.r_[np.full(mn, ml), np.full(cells - mn, 0.05)]
        p90 = np.r_[np.full(pn, pl), np.full(cells - pn, 0.1)]
        vr = {"first_order": vr_pass, c2.CLIPPED: vr_pass if gc else vr_fail,
              "multiplicative": vr_pass if gm else vr_fail}
        yield record(med, p90, vr, worst, cells)


class Reading(unittest.TestCase):
    def test_equals_clip_probe2_under_c2s_gate(self):
        n = 0
        for rec in grid():
            self.assertEqual(c2.reading_1b(rec), cp2.reading(rec))
            n += 1
        self.assertGreater(n, 10_000)

    def test_option_1_is_q1_and_bounded_under_either_gate(self):
        """The audit's identity: reads option (1) <=> q1 and the mismatch bounded, so no other gate can move it."""
        for gates in (None, c2.GATES_1B):
            for rec in grid():
                got = c2.reading_1b(rec, gates)["T"]
                self.assertEqual(got["reads"] == "option (1)", got["option_1_qualifies"] and got["mismatch_bounded"])

    def test_1b_gate_acts_on_the_clipped_ratio(self):
        med, p90 = np.full(16, 0.05), np.full(16, 0.1)
        ok = {"first_order": np.ones(16), "multiplicative": np.ones(16)}
        two = ratios(2, 0.25, 1.0)                 # C2's 95 % rule fails it; #724 passes it
        three = ratios(3, 0.25, 1.0)
        rec = record(med, p90, {**ok, c2.CLIPPED: two}, 0.01)
        self.assertEqual(cp2.reading(rec)["T"]["reads"], "no rule of the reading fires")
        self.assertEqual(c2.reading_1b(rec, c2.GATES_1B)["T"]["reads"], "option (1)")
        rec = record(med, p90, {**ok, c2.CLIPPED: three}, 0.01)
        self.assertNotEqual(c2.reading_1b(rec, c2.GATES_1B)["T"]["reads"], "option (1)")

    def test_the_16_cell_counts(self):
        """On 16 cells the reading's shares are: 'every cell' 16, '>= 90 %' 15, '> 10 %' 2 or more, '>= 20 %' 4."""
        ok = {"first_order": np.ones(16), c2.CLIPPED: np.ones(16), "multiplicative": np.ones(16)}
        base_med = np.full(16, 0.05)
        for n_bad, want in ((1, True), (2, False)):        # p90 <= 0.4 in >= 90 %: 15 of 16 pass, 14 fail
            p90 = np.r_[np.full(n_bad, 0.45), np.full(16 - n_bad, 0.1)]
            self.assertEqual(c2.reading_1b(record(base_med, p90, ok, 0.01))["T"]["option_1_qualifies"], want)
        med = np.r_[0.25, np.full(15, 0.05)]                # every cell: one cell above 0.2 fails q1
        self.assertFalse(c2.reading_1b(record(med, np.full(16, 0.1), ok, 0.01))["T"]["option_1_qualifies"])
        for n, want in ((1, False), (2, True)):            # positivity: median > 0.3 in more than 10 %
            med = np.r_[np.full(n, 0.35), np.full(16 - n, 0.05)]
            self.assertEqual(c2.reading_1b(record(med, np.full(16, 0.1), ok, 0.01))["T"]["positivity_preferred"],
                             want)
        fail = {"first_order": np.ones(16), c2.CLIPPED: ratios(3, 0.5), "multiplicative": ratios(3, 0.5)}
        for n, want in ((3, False), (4, True)):            # option (3): median >= 0.7 in >= 20 %, no gate passing
            med = np.r_[np.full(n, 0.75), np.full(16 - n, 0.05)]
            self.assertEqual(c2.reading_1b(record(med, np.full(16, 0.1), fail, 0.01))["T"]["option_3_applies"], want)


class Law(unittest.TestCase):
    def test_band_reference_equals_clip_probe2s_on_cov2ds_layout(self):
        rng = np.random.default_rng(1)
        h = rng.normal(size=(cov2d.N_UNIVERSES, 7))
        w = rng.uniform(0.5, 1.5, cov2d.BANDS[cov2d.FLUX])
        self.assertTrue(np.array_equal(c2.band_reference(h, w, cov2d.ORDER, cov2d.BANDS, cov2d.FLUX),
                                       cp2.band_reference(h, w)))

    def test_band_reference_refuses_a_wrong_row_count(self):
        with self.assertRaises(c2.Refusal):
            c2.band_reference(np.ones((5, 2)), np.ones(100), cov2d.ORDER, cov2d.BANDS, cov2d.FLUX)

    def test_1b_layout_is_s1s_bands_in_draw_order(self):
        order, bands, tags = c2.layout_1b()
        self.assertEqual(len(tags), 175)
        self.assertEqual(len(order), 38)
        self.assertEqual(bands["Flux"], 100)
        p = np.full(100, 0.01)
        groups = {b: [f"{b}_{i}" for i in range(bands[b])] for b in toys.INTERACTION_BANDS}
        col = {t: i for i, t in enumerate(tags)}
        S = c2.selection(c2.calibration_draws("g18", 0, p, groups, n=5), col, bands)
        self.assertTrue(np.all(S.sum(axis=1) == 38))
        with self.assertRaises(c2.Refusal):
            c2.selection([tags[:3]], col, bands)

    def test_the_streams_are_disjoint_from_the_declared_draws(self):
        p = np.full(100, 0.01)
        groups = {b: [f"{b}_{i}" for i in range(2 if b != "2p2h" else 3)] for b in toys.INTERACTION_BANDS}
        a = c2.calibration_draws("g18", 0, p, groups, n=50)
        self.assertEqual(a, c2.calibration_draws("g18", 0, p, groups, n=50))
        self.assertNotEqual(a, c2.calibration_draws("ar23", 0, p, groups, n=50))
        self.assertNotEqual(a, c2.calibration_draws("g18", 1, p, groups, n=50))
        declared = [mc.draw_universes(toys.draw_for_seed(s, p, groups)) for s in range(3_620_000, 3_620_050)]
        self.assertNotEqual(a, declared)
        seeds = [s for t in mc.TOY_SEEDS for s in mc.TOY_SEEDS[t]] + list(mc.STAT_SEED.values())
        self.assertFalse(set(c2.CAL_SEED.values()) & set(seeds))
        self.assertNotEqual(c2.CAL_SALT, 0)       # SeedSequence zero-pads: [a, b] is [a, b, 0] (audit W4)
        two = np.random.default_rng([c2.CAL_SEED["g18"], 0]).random(4)
        self.assertTrue(np.array_equal(two, np.random.default_rng([c2.CAL_SEED["g18"], 0, 0]).random(4)))
        self.assertFalse(np.array_equal(two, np.random.default_rng([c2.CAL_SEED["g18"], 0, c2.CAL_SALT]).random(4)))
        with mock.patch.object(c2, "CAL_SALT", 0), self.assertRaises(c2.Refusal):
            c2.calibration_draws("g18", 0, p, groups, n=1)

    def test_the_count_law_check_is_one_on_average(self):
        """D4's law half on a toy layout: the linear count's ratio averages to 1 within CONTROL_Z SEs."""
        order, bands = ("Flux", "x", "y"), {"Flux": 5, "x": 2, "y": 3}
        tags = [f"{b}_{i}" for b in order for i in range(bands[b])]
        col = {t: i for i, t in enumerate(tags)}
        w = np.array([1.0, 2.0, 1.0, 3.0, 1.0])
        rng = np.random.default_rng(2)
        cvA = rng.uniform(5, 10, 4)
        HA = cvA + rng.normal(0, 1, (len(tags), 4))
        Ucount = np.ones((1, 4))
        ref = c2.band_reference(HA @ Ucount.T, w, order, bands, "Flux")
        out = []
        for s in range(800):
            r = np.random.default_rng([9, s])
            draws = [[f"Flux_{r.choice(5, p=w / w.sum())}", f"x_{r.integers(2)}", f"y_{r.integers(3)}"]
                     for _ in range(300)]
            S = c2.selection(draws, col, bands)
            L = c2.composite_sums(S, {"A": HA, "B": HA, "D": HA}, {"A": cvA, "B": cvA, "D": cvA})["A"] @ Ucount.T
            out.append(np.var(L, axis=0, ddof=1) / ref)
        self.assertTrue(c2.control({"t": np.array(out)})["holds"])
        self.assertFalse(c2.control({"t": np.array(out) * 1.05})["holds"])


class Block(unittest.TestCase):
    def test_c2_block_reads_each_quantity(self):
        """R = m_seen/S - m_all/N, and the clipped ratio is Nc's variance, first order's N's (the receipt's survivors)."""
        rng = np.random.default_rng(8)
        d = 50
        q = {"S": np.full((16, d), 100.0), "m_seen": np.full((16, d), 2.0), "N": np.full((16, d), 50.0),
             "m_all": np.full((16, d), 1.0), "S_reco": np.full((16, d), 100.0), "m_bkg": np.zeros((16, d)),
             "Nm": rng.normal(50, 1, (16, d))}
        q["Nc"] = rng.normal(51, 2.0, (16, d))
        q["N"] = q["N"] + rng.normal(0, 1.0, (16, d))
        b = c2.c2_block(q, np.ones(16), np.ones(16))
        R = q["m_seen"] / q["S"] - q["m_all"] / q["N"]
        np.testing.assert_allclose(b["option_1"]["sigma_Q"]["signed_median"], np.median(R, axis=1))
        np.testing.assert_allclose(b["variance_ratio"][c2.CLIPPED], np.var(q["Nc"], axis=1, ddof=1))
        np.testing.assert_allclose(b["variance_ratio"]["first_order"], np.var(q["N"], axis=1, ddof=1))


REF_SHA256 = "f19adbda6126d79d1f337755de873b530a76ebbcfd412ab60f85ab53cb33fe49"


CAL300_REF_SHA256 = "c3c346454928290038585cf1f682209808258b7e06869848d750ee284c821d1d"   # 02e71a0b, job 60771025's
CAL300_RECORD = (Path(__file__).resolve().parents[2] / "docs/orchestration/state/measurement-paper/5d-community-20261024"
                 / "fd/receipts-1b/staged/a2-1/calib-run/calibration.json")


def reference_module(rev: str, sha: str):
    """fd_1b_c2 at ``rev`` (tests/data/fd_1b_c2_at_<rev>.py.txt, its exact bytes, checked against ``sha``), executed as
    a module with the real module's __file__ so its paths resolve."""
    import hashlib
    import types
    raw = (Path(__file__).resolve().parent / "data" / f"fd_1b_c2_at_{rev}.py.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sha
    m = types.ModuleType(f"fd_1b_c2_at_{rev}")
    m.__file__ = c2.__file__
    exec(compile(raw, f"fd_1b_c2@{rev}", "exec"), m.__dict__)
    return m


def reference_c2():
    """fd_1b_c2 as bound at f19adbda: the reference the director's ruling (a) requires the hoisted code to equal
    bitwise."""
    return reference_module("f19adbda", REF_SHA256)


class Cal300Code(unittest.TestCase):
    """The director's rulings of 2026-11-05: the backstop's 300-draw calibration (job 60771025, at 02e71a0b) is admitted
    only while the code behind its SDs is unchanged, statement for statement (fd_1b_c2.code_closure, version-stable
    source text), with _one_set's one-argument change the one named exemption."""

    TOOL = (Path(__file__).resolve().parents[2] / "docs/orchestration/state/measurement-paper/5d-community-20261024"
            / "fd/receipts-1b/staged/a2-1/cal300_code_check.py")

    def setUp(self):
        import json
        import tempfile
        self.rec = json.loads(CAL300_RECORD.read_text())
        self.pins = json.loads((Path(c2.__file__).resolve().parent / c2.CAL300_PINS).read_text())
        self.tmp = Path(tempfile.mkdtemp())

    def check_with(self, pins: dict, rec=None):
        """cal300_code_check against a pins file written here and named by its own digest."""
        import hashlib
        import json
        f = self.tmp / f"pins-{len(list(self.tmp.iterdir()))}.json"
        f.write_text(json.dumps(pins))
        with mock.patch.object(c2, "CAL300_PINS", str(f)), \
                mock.patch.object(c2, "CAL300_PINS_SHA256", hashlib.sha256(f.read_bytes()).hexdigest()):
            return c2.cal300_code_check(rec or self.rec)

    def with_entry(self, label: str, **change) -> dict:
        es = [dict(e, **change) if f"{e['module']}.{e['label']}" == label else e for e in self.pins["closure"]]
        self.assertNotEqual(es, self.pins["closure"], label)
        return dict(self.pins, closure=es)

    def test_silent_on_the_real_tree_and_record(self):
        self.assertIsNone(c2.cal300_code_check(self.rec))                       # the committed pins, unpatched
        self.assertEqual(self.rec["code_sha256"]["fd_1b_c2.py"], CAL300_REF_SHA256)
        self.assertEqual(self.pins["record_fd_1b_c2_sha256"], CAL300_REF_SHA256)
        self.assertEqual(len(self.pins["closure"]), 157)
        self.assertEqual(set(self.pins["exempt"]), set(c2.CAL300_EXEMPT))

    def test_the_text_rules_on_a_toy_module(self):
        """A decorator is part of its def; a docstring is cut by its span, a comment kept; a tuple assignment binds
        each name; a bare method call binds its base; a comprehension's variable binds nothing at module level."""
        src = ('@dec\ndef f(x):\n    """a docstring,\n    two lines"""\n    return g(x)  # kept\n\n\ndef g(y):\n    return y\n'
               'A, B = 1, 2\nEXP = {}\nEXP.update({k: 1 for k in KS})\nKS = (A,)\nOTHER = 3\n')
        es = c2.code_closure(lambda m: ("toy.py", src) if m == "toy" else None, [("toy", "f"), ("toy", "EXP")])
        self.assertEqual([e["label"] for e in es], ["A,B", "EXP", "EXP", "KS", "f", "g"])   # OTHER and dec unreached
        got = {e["label"]: e["text"] for e in es}
        self.assertEqual(got["f"], "@dec\ndef f(x):\n    return g(x)  # kept")
        self.assertEqual(got["g"], "def g(y):\n    return y")
        self.assertEqual(sorted(e["text"] for e in es if e["label"] == "EXP"),
                         ["EXP = {}", "EXP.update({k: 1 for k in KS})"])

    def test_the_glue_is_reached(self):
        """The audit's G2: module-level statements that are not `Name = ...` are walked and pinned."""
        labels = [f"{e['module']}.{e['label']}" for e in self.pins["closure"]]
        for want in ("s1_assemble.DROPPED,FLUX,MINOS", "s1_assemble.MODEL_BANDS_2",
                     "fd_1b_c2.GATE_DEV,GATE_K,GATE_LOGMEAN,GATE_MAX", "fd_1b_c2.SD_MULT_CELL,SD_MULT_LOGMEAN"):
            self.assertIn(want, labels)
        self.assertEqual(labels.count("s1_assemble.EXPECT"), 2)                 # the dict and its .update(...)

    def test_refuses_a_changed_pinned_statement(self):
        for label in ("fd_1b_c2.rates", "fd_1b_mc.draw_universes", "s1_assemble.MODEL_BANDS_2"):
            with self.assertRaisesRegex(c2.Refusal, "changed since 02e71a0b"):
                self.check_with(self.with_entry(label, text_sha256="0" * 64))

    def test_refuses_an_added_or_a_missing_statement(self):
        es = self.pins["closure"]
        with self.assertRaisesRegex(c2.Refusal, r"\[\] changed or missing, \['s1_assemble.MODEL_BANDS_2'\] added"):
            self.check_with(dict(self.pins, closure=[e for e in es if e["label"] != "MODEL_BANDS_2"]))
        with self.assertRaisesRegex(c2.Refusal, r"\['s1_assemble.MODEL_BANDS_2'\] changed or missing, \[\] added"):
            self.check_with(dict(self.pins, closure=es + [e for e in es if e["label"] == "MODEL_BANDS_2"]))

    def test_refuses_another_record_or_pins_file(self):
        with self.assertRaisesRegex(c2.Refusal, "not the record its pins describe"):
            c2.cal300_code_check(dict(self.rec, code_sha256=dict(self.rec["code_sha256"], **{"fd_1b_c2.py": "0" * 64})))
        with self.assertRaisesRegex(c2.Refusal, "not the record its pins describe"):
            c2.cal300_code_check({k: v for k, v in self.rec.items() if k != "code_sha256"})
        with mock.patch.object(c2, "CAL300_PINS_SHA256", "0" * 64), \
                self.assertRaisesRegex(c2.Refusal, "pins file is not the one this code names"):
            c2.cal300_code_check(self.rec)

    def test_refuses_a_module_loaded_from_another_file(self):
        pins = dict(self.pins, closure=[dict(e, file="nd-unfolding/fd_1b_mc.py") if e["module"] == "xsec_nd" else e
                                        for e in self.pins["closure"]])
        with self.assertRaisesRegex(c2.Refusal, "xsec_nd is loaded from"):
            self.check_with(pins)

    def test_a_pinned_module_is_imported_before_the_guard(self):
        """The audit's G3: a pinned module not yet imported is imported first, so the guard sees the file that will
        run. Here a shadow flux_universe ahead on sys.path is what an import would load; the check must refuse it."""
        shadow = self.tmp / "shadow"
        shadow.mkdir()
        (shadow / "flux_universe.py").write_text("X = 1\n")
        saved = sys.modules.pop("flux_universe", None)
        sys.path.insert(0, str(shadow))
        try:
            with self.assertRaisesRegex(c2.Refusal, "flux_universe is loaded from .*shadow"):
                c2.cal300_code_check(self.rec)
        finally:
            sys.path.remove(str(shadow))
            sys.modules.pop("flux_universe", None)
            if saved is not None:
                sys.modules["flux_universe"] = saved

    def test_the_exemption_is_by_name_only(self):
        cur = next(e["text_sha256"] for e in c2.code_closure(lambda m: next(
            ((f"{d}/{m}.py", (Path(c2.__file__).resolve().parents[1] / d / f"{m}.py").read_text()) for d in c2.CODE_DIRS
             if (Path(c2.__file__).resolve().parents[1] / d / f"{m}.py").is_file()), None), c2.CAL300_ROOTS)
            if e["module"] == "fd_1b_c2" and e["label"] == "prepare")
        pins = self.with_entry("fd_1b_c2.prepare", text_sha256="0" * 64)
        pins["exempt"] = dict(self.pins["exempt"], **{"fd_1b_c2.prepare": {"text_sha256": cur}})
        with self.assertRaisesRegex(c2.Refusal, "fd_1b_c2.prepare"):           # an exemption c2 does not name
            self.check_with(pins)
        with self.assertRaisesRegex(c2.Refusal, "fd_1b_c2._one_set"):           # the named one, at another digest
            self.check_with(dict(self.pins, exempt={"fd_1b_c2._one_set": {"text_sha256": "0" * 64}}))
        with self.assertRaisesRegex(c2.Refusal, "fd_1b_c2._one_set"):           # without it, 02e71a0b's pin refuses
            self.check_with(dict(self.pins, exempt={}))

    def test_the_pins_are_not_a_fixed_point(self):
        """The pins live in a file c2check reads, named here by digest; no pinned statement mentions the constants
        that name the file or the functions that check it, so editing them cannot move a pin."""
        root = Path(c2.__file__).resolve().parents[1]
        tree = c2.code_closure(lambda m: next(((f"{d}/{m}.py", (root / d / f"{m}.py").read_text()) for d in c2.CODE_DIRS
                                               if (root / d / f"{m}.py").is_file()), None), c2.CAL300_ROOTS)
        self.assertEqual(len(tree), len(self.pins["closure"]))
        for e in tree:
            for name in ("CAL300", "code_closure", "cal300_closure_diff", "CODE_DIRS"):
                self.assertNotIn(name, e["text"], f"{e['module']}.{e['label']}")

    def tool(self, python: str, *args) -> str:
        import subprocess
        r = subprocess.run([python, "-I", "-B", str(self.TOOL), *args], cwd=Path(c2.__file__).resolve().parents[1],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-1200:] + r.stderr[-1200:])
        return r.stdout

    def test_the_pins_file_is_the_tools_walk(self):
        """cal300_code_check.py, run here from 02e71a0b, writes the committed pins."""
        import json
        out = self.tmp / "pins-tool.json"
        self.tool(sys.executable, self.pins["rev"], self.pins["exempt"]["fd_1b_c2._one_set"]["rev"], "--write-pins", str(out))
        self.assertEqual(json.loads(out.read_text()), self.pins)

    def test_the_pins_recompute_identically_under_python_3_11(self):
        """The audit's G1: the cluster runs Python 3.11 (root_6_28). The pins, recomputed from this tree by c2check's
        own functions under a real 3.11 interpreter (PY311, else uv's), match, as they do under this one."""
        import os
        import shutil
        import subprocess
        py311 = os.environ.get("PY311") or (subprocess.run(["uv", "python", "find", "3.11"], capture_output=True,
                                                            text=True).stdout.strip() if shutil.which("uv") else "")
        if not py311:
            self.skipTest("no Python 3.11 here (set PY311): the pins are not verified under 3.11 by this run")
        out = self.tool(py311, "--verify-tree")
        self.assertRegex(out, r"(?m)^python 3\.11\.")
        self.assertIn("CAL300-PINS-VERIFY :: MATCH :: python 3.11.", out)
        self.assertIn(f"CAL300-PINS-VERIFY :: MATCH :: python {sys.version.split()[0]}", self.tool(sys.executable, "--verify-tree"))


class Multiplicative(unittest.TestCase):
    """The director's ruling (a): C2's (v) with its draw-independent terms built once and Z sparse, bitwise equal to
    the f19adbda implementation, on a fixture that reaches every branch."""

    def fixture(self, seed=31):
        rng = np.random.default_rng(seed)
        U, R, D = 24, 4000, 60
        V = rng.uniform(0.5, 1.5, (U, R))
        V[rng.random((U, R)) < 0.03] = 0.0
        V[rng.random((U, R)) < 0.03] = -0.2
        cv = rng.uniform(0.5, 1.5, R)
        cv[rng.random(R) < 0.05] = 0.0
        cv[rng.random(R) < 0.05] = -0.3
        S = np.zeros((D, U))
        S[np.arange(D)[:, None], rng.integers(0, U, (D, 6))] = 1.0
        S[0, 3] = 2.0                                      # a universe drawn twice
        return V, cv, S

    def test_bitwise_equal_to_f19adbda(self):
        ref = reference_c2()
        V, cv, S = self.fixture()
        T = c2.multiplicative_terms(V, cv)
        self.assertGreater(T["zu"].size, 0)                        # the sparse floor is reached
        self.assertGreater(int((~T["pos"]).sum()), 0)              # and rows with a_CV <= 0
        got = c2.multiplicative(V, cv, S)
        want = ref.multiplicative(V, cv, S)
        self.assertTrue(np.array_equal(got, want))
        floored = (S @ (T["pos"][None] & (V <= 0)).astype(float)) != 0
        self.assertTrue(np.any(floored & T["pos"][None]))         # some draw floors a positive-CV row
        for d0 in range(0, S.shape[0], c2.DRAW_BLOCK):            # by blocks, from one set of terms
            self.assertTrue(np.array_equal(c2.multiplicative_apply(T, S[d0:d0 + c2.DRAW_BLOCK]),
                                           ref.multiplicative(V, cv, S[d0:d0 + c2.DRAW_BLOCK])))

    def test_no_floor_at_all(self):
        ref = reference_c2()
        V, cv, S = self.fixture(32)
        V, cv = np.abs(V) + 0.1, np.abs(cv) + 0.1
        T = c2.multiplicative_terms(V, cv)
        self.assertEqual(T["zu"].size, 0)
        self.assertTrue(np.array_equal(c2.multiplicative_apply(T, S), ref.multiplicative(V, cv, S)))

    def test_c2_truth_refuses_a_negative_selection(self):
        n = 3
        geo = {"U": np.ones((16, 4)), "shape": (4,), "fm": np.zeros(4, int), "gen": np.zeros(n, int),
               "reco": np.zeros(n, int), "bkg": np.zeros(1, int), "td": np.zeros(n, int)}
        with self.assertRaisesRegex(c2.Refusal, "negative entry"):
            c2.c2_truth({}, {}, np.array([[1.0, -1.0]]), np.ones(n), geo, np.ones((1, 4)),
                        {"pack": {"keep": np.ones(4, bool)}})


class LargeSample(unittest.TestCase):
    """Joseph's large-sample gate (P1-P7): the gate seeds, the s rule, power, the verdict's order."""

    def test_stops_at_counts_i_alone(self):
        """P2: a set that only (i) stops (three cells beyond 0.20, its mean log 0, every z far under s 4.3) is a STOP
        (the final receipt's survivor "stops_at without (i)")."""
        rng = np.random.default_rng(21)
        R = 1.0 + rng.normal(0, 0.3, (2000, 16))
        R = np.clip(R, 0.05, None)
        R[0] = 1.0
        R[0, :3], R[0, 3:6] = 1.25, 0.8                      # 3 beyond 0.20; 0.8 is AT 0.20, not beyond
        st = c2.null_stats(R)
        self.assertTrue(st["i"][0])
        self.assertAlmostEqual(st["ml"][0], 0.0, places=12)
        stops = c2.stops_at(st, 1.0, st["sd_ml"], st["sd_c"])
        self.assertLess(float(np.max(st["dev"][0] / st["sd_c"])), 4.3)    # (iii) by (alpha) does not fire
        self.assertTrue(stops[0])

    def test_stops_at_counts_iii_alone(self):
        """P2: a set that only (iii) stops (one cell 10 SD_c out but inside 0.20, its mean log under s 3.5 SD_ii) is a
        STOP (the final receipt's survivor "stops_at without (iii)")."""
        rng = np.random.default_rng(22)
        R = 1.0 + rng.normal(0, 0.01, (2000, 16))
        R[0] = 1.0
        R[0, 5] = 1.10
        st = c2.null_stats(R)
        self.assertFalse(st["i"][0])                                       # no cell beyond 0.20
        self.assertLess(abs(st["ml"][0]), 1.0 * c2.SD_MULT_LOGMEAN * st["sd_ml"])   # (ii) does not fire
        self.assertGreater(float(np.max(st["dev"][0] / st["sd_c"])), 1.0 * c2.SD_MULT_CELL)
        self.assertTrue(c2.stops_at(st, 1.0, st["sd_ml"], st["sd_c"])[0])

    def test_stops_at_ii_at_its_own_multiple(self):
        """P2: (ii) stops at s 3.5 SD_ii, not at (iii)'s 4.3: a uniform shift with |mean log| at 4 SD_ii, every cell
        inside 0.20 and every z near 1, stops (the final receipt's survivor "(ii) at the cell multiple")."""
        rng = np.random.default_rng(23)
        R = 1.0 + rng.normal(0, 0.01, (2000, 16))
        sd0 = c2.null_stats(R)["sd_ml"]
        R[0] = np.exp(4.0 * sd0)
        st = c2.null_stats(R)
        z_ml = abs(st["ml"][0]) / st["sd_ml"]
        self.assertTrue(c2.SD_MULT_LOGMEAN < z_ml < c2.SD_MULT_CELL, z_ml)
        self.assertFalse(st["i"][0])
        self.assertLess(float(np.max(st["dev"][0] / st["sd_c"])), c2.SD_MULT_CELL)
        self.assertTrue(c2.stops_at(st, 1.0, st["sd_ml"], st["sd_c"])[0])

    def test_the_two_truth_union_projects_the_plugin(self):
        """P2 without the plug-in: each grid point's union is the labelled projection, the plug-in's rate taken as the
        mean of the two measured and independent of them, 1 - (1 - p_g)(1 - p_a)(1 - (p_g + p_a)/2), from the rule's
        own per-truth rates (the final receipt's survivor "the projection without the plug-in")."""
        rng = np.random.default_rng(25)
        R = {t: 1.0 + rng.normal(0, 0.02, (3000, 16)) for t in ("g18", "ar23")}
        rule = c2.threshold_rule(R)
        self.assertFalse(rule["three_truths_measured"])
        self.assertIn("mean of the others", rule["projection"])
        moved = 0
        for g in rule["grid"]:
            pg, pa = g["per_truth"]["g18"], g["per_truth"]["ar23"]
            self.assertAlmostEqual(g["union"], 1 - (1 - pg) * (1 - pa) * (1 - (pg + pa) / 2), places=12)
            moved += (pg + pa) > 0
        self.assertGreater(moved, 10)                       # the plug-in's factor is non-trivial on the grid

    def test_three_truths_measure_the_union_per_replicate(self):
        """P2 with all three truths: the union is measured per replicate, not projected. Three truths sharing one set
        of draws stop on the same replicates, so the measured union is each truth's own rate, which a product of
        independent rates exceeds (the final receipt's survivor "three truths as a product")."""
        rng = np.random.default_rng(26)
        X = 1.0 + rng.normal(0, 0.02, (3000, 16))
        rule = c2.threshold_rule({t: X.copy() for t in ("g18", "ar23", "plugin")})
        self.assertTrue(rule["three_truths_measured"])
        self.assertIsNone(rule["projection"])
        hit = 0
        for g in rule["grid"]:
            p = g["per_truth"]["g18"]
            self.assertEqual((g["per_truth"]["ar23"], g["per_truth"]["plugin"]), (p, p))
            self.assertAlmostEqual(g["union"], p, places=12)
            hit += 0 < p < 1
        self.assertGreater(hit, 10)                         # where a product would differ

    def test_the_null_sds_are_over_every_set(self):
        """null_stats' SD_ii and SD_c are over every replicate set (ddof 1), built here independently: the first 100
        sets are ten times tighter than the rest, so an SD over a subset cannot match (the final receipt's survivor
        "the null SD over too few sets")."""
        rng = np.random.default_rng(27)
        R = 1.0 + np.vstack([rng.normal(0, 0.002, (100, 16)), rng.normal(0, 0.02, (1900, 16))])
        st = c2.null_stats(R)
        self.assertAlmostEqual(st["sd_ml"], float(np.std(np.log(R).mean(axis=1), ddof=1)), places=14)
        np.testing.assert_allclose(st["sd_c"], np.std(R, axis=0, ddof=1), rtol=1e-12)
        self.assertGreater(st["sd_ml"], 2 * float(np.std(np.log(R[:100]).mean(axis=1), ddof=1)))

    def test_power_is_against_a_deflation(self):
        """P4's uniform case deflates by UNIFORM_DEFLATION. With (ii)'s threshold set between |log 0.92| = 0.0834 and
        |log 1.08| = 0.0770, and (iii) out of reach, a deflation always stops and an inflation never would (the final
        receipt's survivor "a uniform inflation")."""
        rng = np.random.default_rng(28)
        R = {"g18": 1.0 + rng.normal(0, 1e-4, (500, 16))}
        thr = 0.080
        rule = {"s": 1.0, "thresholds": {"g18": {"sd_mean_log": thr / c2.SD_MULT_LOGMEAN, "sd_per_cell": [1.0] * 16}}}
        self.assertTrue(abs(np.log(1 + c2.UNIFORM_DEFLATION)) < thr < abs(np.log(1 - c2.UNIFORM_DEFLATION)))
        pw = c2.power_at(R, rule)
        self.assertEqual(pw["g18"]["uniform"], 1.0)
        self.assertTrue(pw["g18"]["uniform_meets"] and pw["meets"])

    def test_power_exactly_at_the_minimum_meets(self):
        """P4: power of exactly POWER_MIN meets the requirement (>=). Eight of ten sets stop once deflated and two,
        set at 1/(1 - UNIFORM_DEFLATION), land on 1 and do not (the final receipt's survivor "power at the boundary
        fails")."""
        R = {"g18": np.vstack([np.ones((8, 16)), np.full((2, 16), 1.0 / (1.0 - c2.UNIFORM_DEFLATION))])}
        rule = {"s": 1.0, "thresholds": {"g18": {"sd_mean_log": 0.080 / c2.SD_MULT_LOGMEAN, "sd_per_cell": [1.0] * 16}}}
        pw = c2.power_at(R, rule)
        self.assertEqual(pw["g18"]["uniform"], c2.POWER_MIN)
        self.assertTrue(pw["g18"]["uniform_meets"])

    def test_power_must_meet_at_every_truth(self):
        """P4: the requirement is per truth; one truth short fails it however the other does (the final receipt's
        survivor "one truth's power suffices")."""
        thr = {"sd_mean_log": 0.080 / c2.SD_MULT_LOGMEAN, "sd_per_cell": [1.0] * 16}
        R = {"g18": np.ones((10, 16)), "ar23": np.full((10, 16), 1.0 / (1.0 - c2.UNIFORM_DEFLATION))}
        pw = c2.power_at(R, {"s": 1.0, "thresholds": {"g18": thr, "ar23": thr}})
        self.assertEqual((pw["g18"]["uniform"], pw["ar23"]["uniform"]), (1.0, 0.0))
        self.assertFalse(pw["meets"])

    def test_stops_at_iii_at_its_own_multiple(self):
        """P2: (iii) by (alpha) stops at s 4.3 SD_c, not at (ii)'s 3.5: one cell at 4 SD_c, inside 0.20, with its mean
        log far under (ii)'s threshold, does not stop (the converse of the one above)."""
        rng = np.random.default_rng(24)
        R = 1.0 + rng.normal(0, 0.01, (2000, 16))
        sdc = c2.null_stats(R)["sd_c"]
        R[0] = 1.0
        R[0, 7] = 1.0 + 4.0 * sdc[7]
        st = c2.null_stats(R)
        z = float(np.max(st["dev"][0] / st["sd_c"]))
        self.assertTrue(c2.SD_MULT_LOGMEAN < z < c2.SD_MULT_CELL, z)
        self.assertLess(abs(st["ml"][0]), c2.SD_MULT_LOGMEAN * st["sd_ml"])
        self.assertFalse(st["i"][0])
        self.assertFalse(c2.stops_at(st, 1.0, st["sd_ml"], st["sd_c"])[0])

    def test_the_gate_seeds_extend_the_declared_toys(self):
        for t in ("g18", "ar23", "plugin"):
            g = c2.gate_seeds(t)
            self.assertEqual(len(g), c2.GATE_N)
            self.assertEqual(g[:300], [int(x) for x in mc.TOY_SEEDS[t]])                 # bit for bit (P1)
            self.assertEqual(len(set(g)), c2.GATE_N)

    def test_the_new_seeds_are_used_nowhere_else(self):
        """P1's no-reuse scan, in a test: the gate's new seeds are disjoint from every declared seed set in the code,
        and no committed task table, script or receipt under docs/orchestration names an integer in their ranges."""
        import re
        import fd_f1_tasks
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "2d-unfolding" / "cov2d"))
        import cov2d as cv2
        new = {x for t in ("g18", "ar23", "plugin") for x in c2.gate_seeds(t)[300:]}
        declared = {int(x) for t in mc.TOY_SEEDS for x in mc.TOY_SEEDS[t]} | set(mc.STAT_SEED.values())
        declared |= {mc.SEED_CHECK, mc.VALIDATE_SEED} | set(c2.CAL_SEED.values())
        declared |= {s + k for s in fd_f1_tasks.SEEDS.values() for k in range(fd_f1_tasks.N_PE)}
        declared |= {x for r in cv2.TOY_SEEDS.values() for x in r} | set(cv2.REALIZATION_SEED.values()) | {cv2.NULL_SEED}
        self.assertFalse(new & declared)
        lo, hi = min(new), max(new)
        root = Path(__file__).resolve().parents[2] / "docs" / "orchestration"
        hits = []
        for p in [*root.rglob("*.tsv"), *root.rglob("*.sh")]:
            for m in re.finditer(r"(?<![0-9])([0-9]{7})(?![0-9])", p.read_text(errors="ignore")):
                if lo <= int(m.group(1)) <= hi and int(m.group(1)) in new:
                    hits.append(f"{p.name}: {m.group(1)}")
        self.assertEqual(hits, [])

    def null(self, n=4000, sd=0.03, seed=1):
        rng = np.random.default_rng(seed)
        return np.exp(rng.normal(0, sd, (n, 1)) + rng.normal(0, 0.05, (n, 16)))

    def test_the_rule_picks_the_smallest_s_within_the_budget(self):
        R = {"g18": self.null(seed=1), "ar23": self.null(seed=2)}
        rule = c2.threshold_rule(R)
        self.assertFalse(rule["three_truths_measured"])
        self.assertIsNotNone(rule["projection"])
        s = rule["s"]
        u = {g["s"]: g["union"] for g in rule["grid"]}
        self.assertLessEqual(u[s], c2.UNION_LIMIT)
        self.assertTrue(all(u[x] > c2.UNION_LIMIT for x in u if x < s))
        self.assertEqual(len(rule["grid"]), len(c2.S_GRID))
        t = rule["thresholds"]["g18"]
        self.assertAlmostEqual(t["ii_mean_log"], s * c2.SD_MULT_LOGMEAN * t["sd_mean_log"])
        self.assertAlmostEqual(t["iii_alpha_multiple"], s * c2.SD_MULT_CELL)
        R3 = dict(R, plugin=self.null(seed=3))
        self.assertTrue(c2.threshold_rule(R3)["three_truths_measured"])

    def test_i_alone_over_the_budget_is_flagged(self):
        R = self.null()
        R[:200, :3] = 1.3                                     # (i) fires in 5 % of sets
        rule = c2.threshold_rule({"g18": R, "ar23": R})
        self.assertTrue(rule["i_alone_exceeds"])
        self.assertFalse(c2.threshold_rule({"g18": self.null(), "ar23": self.null(seed=4)})["i_alone_exceeds"])

    def test_power_uniform_and_concentrated(self):
        R = {"g18": self.null(sd=0.005, seed=5), "ar23": self.null(sd=0.005, seed=6)}
        rule = c2.threshold_rule(R)
        pw = c2.power_at(R, rule)
        self.assertTrue(pw["meets"])                          # a small common SD: an 8 % deflation is caught
        self.assertEqual(len(pw["g18"]["concentrated"]["1_cells_20pct"]["placements"]), 16)
        self.assertEqual(len(pw["g18"]["concentrated"]["4_cells_10pct"]["placements"]), c2.PLACEMENTS)
        R = {"g18": self.null(sd=0.03, seed=7), "ar23": self.null(sd=0.03, seed=8)}
        rule = c2.threshold_rule(R)
        self.assertIsNotNone(rule["s"])
        self.assertFalse(c2.power_at(R, rule)["meets"])       # the 300-draw regime's common SD: it is not

    def test_gate_n_both_ways(self):
        thr = {"ii_mean_log": 0.03, "iii_alpha_multiple": 4.0, "sd_per_cell": [0.02] * 16}
        self.assertTrue(c2.gate_n(np.ones(16), thr)["passes"])
        self.assertFalse(c2.gate_n(np.full(16, math.exp(0.031)), thr)["ii"])
        self.assertTrue(c2.gate_n(np.full(16, math.exp(0.029)), thr)["ii"])
        r = np.ones(16)
        r[3] = 1.0 + 4.0 * 0.02 * 1.001
        self.assertFalse(c2.gate_n(r, thr)["iii"])
        self.assertFalse(c2.gate_n(r, thr)["passes"])        # (iii) alone fails the gate
        r[3] = 1.0 - 4.0 * 0.02 * 1.001                      # and on either side of 1
        self.assertFalse(c2.gate_n(r, thr)["iii"])
        r[3] = 1.0 + 4.0 * 0.02 * 0.999
        self.assertTrue(c2.gate_n(r, thr)["iii"])
        r = np.full(16, 0.999)
        r[:3] = 1.25
        self.assertFalse(c2.gate_n(r, dict(thr, iii_alpha_multiple=100.0, ii_mean_log=1.0))["i"])

    def test_the_backstop_both_ways(self):
        sd = [0.05] * 16
        self.assertTrue(c2.backstop(np.ones(16), sd)["passes"])
        r = np.ones(16)
        r[0] = 1.0 + 4.3 * 0.05 * 1.01
        self.assertFalse(c2.backstop(r, sd)["passes"])
        r = np.full(16, 0.99)
        r[:3] = 1.21
        self.assertFalse(c2.backstop(r, [1.0] * 16)["passes"])           # (i) at k = 2

    def test_the_config_hash_moves_with_each_input(self):
        code, ins = {"a.py": "1"}, {"npz_sha256": "x"}
        h = c2.config_hash(code, ins, "nature")
        self.assertEqual(h, c2.config_hash(dict(code), dict(ins), "nature"))
        for other in (c2.config_hash({"a.py": "2"}, ins, "nature"), c2.config_hash(code, {"npz_sha256": "y"}, "nature"),
                      c2.config_hash(code, ins, "data")):
            self.assertNotEqual(h, other)
        seeds = dict(mc.TOY_SEEDS, g18=range(mc.TOY_SEEDS["g18"][0] + 1, mc.TOY_SEEDS["g18"][-1] + 2))
        with mock.patch.object(mc, "TOY_SEEDS", seeds):               # the declared toys' seeds are in it
            self.assertNotEqual(h, c2.config_hash(code, ins, "nature"))

    def test_the_large_sample_verdict_in_its_order(self):
        ok, no = {"holds": True}, {"holds": False}
        rule = {"i_alone_exceeds": False, "s": 1.0}
        self.assertEqual(c2.calibration_verdict_n(no, no, rule, None), "CONTROL_FAILED")
        self.assertEqual(c2.calibration_verdict_n(ok, no, rule, None), "LINEARISATION_TO_DIRECTOR")
        self.assertEqual(c2.calibration_verdict_n(ok, ok, dict(rule, i_alone_exceeds=True), None), "I_ALONE_TO_DIRECTOR")
        self.assertEqual(c2.calibration_verdict_n(ok, ok, dict(rule, s=None), None), "NO_THRESHOLD_TO_DIRECTOR")
        self.assertEqual(c2.calibration_verdict_n(ok, ok, rule, {"meets": False}), "POWER_SHORT_TO_DIRECTOR")
        self.assertEqual(c2.calibration_verdict_n(ok, ok, rule, {"meets": True}), "CALIBRATED")


class Linearisation(unittest.TestCase):
    def test_the_tolerance_both_ways_and_the_values_either_way(self):
        R = np.ones((10, 16))
        R[:, 3] = 1.02 - 1e-12
        out = c2.linearisation({"t": R})
        self.assertTrue(out["holds"])
        self.assertAlmostEqual(out["t"]["mean_ratio_minus_1"][3], 0.02, places=9)
        R[:, 3] = 1.0201
        out = c2.linearisation({"t": R, "u": np.ones((10, 16))})
        self.assertFalse(out["holds"])
        self.assertFalse(out["t"]["holds"])
        self.assertTrue(out["u"]["holds"])
        self.assertEqual(len(out["u"]["mean_ratio_minus_1"]), 16)
        self.assertEqual((c2.LINEARISATION_TOL, c2.CONTROL_Z), (0.02, 4.0))


class Truth(unittest.TestCase):
    def world(self, rng, n=4000):
        edges = [np.array([0, 1, 2.0]), np.array([0, 1, 2, 3.0]), np.array([0, 1.0, 2]), np.array([0, 1.0, 2]),
                 np.array([0, 2.0])]
        gen = np.column_stack([rng.uniform(0, e[-1], n) for e in edges])
        wt = rng.uniform(0.5, 1.5, n)
        wt[:50] = -0.3
        pt = rng.uniform(size=n) > 0.1
        denom, _ = np.histogramdd(gen, bins=edges, weights=np.abs(wt) * 1.3)
        return {"edges": edges, "MCgen": gen, "w_truth": wt, "pass_truth": pt, "denom_nd": denom,
                "flux": np.array([2.0, 3.0]), "data_pot": 1e20, "n_nucleons": 3e30}

    def test_xt_flat_is_true_xsec_bitwise(self):
        rng = np.random.default_rng(3)
        w = self.world(rng)
        r = rng.uniform(0.5, 2, w["MCgen"].shape[0])
        half = dict(w, w_truth=0.5 * w["w_truth"])
        x = s5n_pseudo.true_xsec(half, np.ones(w["MCgen"].shape[0], bool), r).ravel()
        sel = w["pass_truth"]
        A, _ = np.histogramdd(w["MCgen"][sel], bins=w["edges"], weights=2.0 * half["w_truth"][sel] * r[sel])
        B, _ = np.histogramdd(w["MCgen"][sel], bins=w["edges"], weights=2.0 * half["w_truth"][sel])
        got = c2.xt_flat(A[None], B[None], w["denom_nd"][None], w["flux"][None], w["n_nucleons"], w["data_pot"],
                         A.shape, w["edges"])
        self.assertTrue(np.array_equal(got[0], x))

    def test_xt_flat_zero_where_the_extraction_is(self):
        rng = np.random.default_rng(4)
        w = self.world(rng)
        D = w["denom_nd"].copy()
        D.flat[0] = 0.0
        x, good = extract_cross_section_nd(np.ones_like(D), np.zeros_like(D), w["flux"], 1e20, 3e30, w["edges"])
        got = c2.xt_flat(np.ones_like(D)[None], np.ones_like(D)[None], D[None], w["flux"][None], 3e30, 1e20,
                         D.shape, w["edges"])
        self.assertEqual(got[0, 0], 0.0)
        self.assertTrue(np.all(got[0, 1:] > 0))

    def test_composite_sums_are_the_histogram_of_the_row_composite(self):
        rng = np.random.default_rng(5)
        n, nu, cells = 500, 6, 8
        cell = rng.integers(0, cells, n)
        cv = rng.uniform(0.5, 1.5, n)
        V = cv + rng.normal(0, 0.3, (nu, n))
        S = np.zeros((4, nu))
        for d, cols in enumerate(([0, 2], [1, 3, 5], [4], [0, 1, 2, 3])):
            S[d, cols] = 1
        hist = lambda a: np.bincount(cell, weights=a, minlength=cells)  # noqa: E731
        H = np.array([hist(v) for v in V])
        got = c2.composite_sums(S, {"A": H, "B": H, "D": H}, {"A": hist(cv), "B": hist(cv), "D": hist(cv)})["A"]
        for d in range(4):
            cols = np.flatnonzero(S[d])
            row = V[cols[0]] + sum(V[j] - cv for j in cols[1:])
            self.assertTrue(np.allclose(got[d], hist(row), rtol=1e-12, atol=1e-12))

    def test_draw_flux_is_the_flux_universes(self):
        S = np.array([[1, 0, 1, 0], [0, 1, 0, 1.0]])
        phi = np.array([[1.0, 2], [3, 4]])
        self.assertTrue(np.array_equal(c2.draw_flux(S, np.array([0, 1]), phi), phi))
        with self.assertRaises(c2.Refusal):
            c2.draw_flux(np.array([[1, 1, 0, 0.0]]), np.array([0, 1]), phi)


class Rates(unittest.TestCase):
    def test_each_rate_counts_its_own_rule(self):
        R = np.ones((4, 16))
        R[0, :3] = 1.25                     # (i) only
        R[1] = math.exp(0.08)               # (ii) only: 1.083 is within 0.20
        R[2, 0] = 1.36                      # (iii) only
        out = c2.rates({"t": R})["t"]["b"]
        self.assertEqual([out[k]["rate"] for k in ("i", "ii", "iii", "union")], [0.25, 0.25, 0.25, 0.75])

    def test_the_rates_are_gate_724s_at_each_edge(self):
        """Audit W2: each rule's rate equals gate_724's verdict on the same replicate, at each bound and one ulp past."""
        at_max = 1.0 + c2.GATE_MAX
        while at_max - 1.0 > c2.GATE_MAX:
            at_max = np.nextafter(at_max, 0.0)
        at_dev = 1.0 + c2.GATE_DEV
        while at_dev - 1.0 > c2.GATE_DEV:
            at_dev = np.nextafter(at_dev, 0.0)
        rows = []
        for v in (at_max, np.nextafter(at_max, 2.0)):
            r = np.ones(16)
            r[0] = v
            rows.append(r)
        for k, v in ((2, at_dev), (3, at_dev), (2, np.nextafter(at_dev, 2.0)), (3, np.nextafter(at_dev, 2.0))):
            r = np.full(16, 0.99)
            r[:k] = v
            rows.append(r)
        ml = math.exp(c2.GATE_LOGMEAN)
        rows += [np.full(16, ml * (1 - 1e-15)), np.full(16, np.nextafter(ml, 2.0) * (1 + 1e-15))]
        exact = np.full(16, ml)                               # a mean log of exactly 0.07 (passes (ii))
        x = exact[15]
        for _ in range(2500):
            x = np.nextafter(x, 0)
        for _ in range(5000):
            exact[15] = x
            if np.mean(np.log(exact)) == c2.GATE_LOGMEAN:
                break
            x = np.nextafter(x, 2)
        rows.append(exact)
        R = np.array(rows)
        out = c2.rates({"t": R})["t"]["b"]
        g = [c2.gate_724(x) for x in R]
        for k in ("i", "ii", "iii"):
            self.assertAlmostEqual(out[k]["rate"], np.mean([not x[k] for x in g]))
        self.assertAlmostEqual(out["union"]["rate"], np.mean([not x["passes"] for x in g]))
        self.assertGreater(out["union"]["rate"], 0)
        self.assertLess(out["union"]["rate"], 1)

    def test_the_route_to_joseph_is_on_b_not_c(self):
        """(b)'s union above 1 % and (c)'s below: 2 % of the sets sit at a mean log of 0.08 (past 0.07, inside
        3.5 x the SD of 0.03)."""
        rng = np.random.default_rng(3)
        ml = rng.normal(0, 0.03, 5000)
        ml[:100] = 0.08
        R = np.exp(ml)[:, None] * np.ones((1, 16))
        out = c2.rates({"a": R, "b": np.roll(R, 2500, axis=0)})
        self.assertGreater(out["over_truths_b"]["union_per_replicate"], c2.UNION_LIMIT)
        self.assertLess(out["over_truths_c"]["union_per_replicate"], c2.UNION_LIMIT)
        self.assertTrue(out["to_joseph"])

    def test_the_verdict_in_its_order(self):
        ok, no = {"holds": True}, {"holds": False}
        self.assertEqual(c2.calibration_verdict(no, no, {"to_joseph": True}), "CONTROL_FAILED")
        self.assertEqual(c2.calibration_verdict(ok, no, {"to_joseph": True}), "LINEARISATION_TO_DIRECTOR")
        self.assertEqual(c2.calibration_verdict(ok, ok, {"to_joseph": True}), "TO_JOSEPH")
        self.assertEqual(c2.calibration_verdict(ok, ok, {"to_joseph": False}), "CALIBRATED")

    def test_power_moves_the_mean_log_by_the_deflation(self):
        R = np.full((10, 16), 1.0)
        out = c2.rates({"t": R * np.exp(np.random.default_rng(0).normal(0, 0.01, (10, 1)))})["t"]
        self.assertEqual(out["power_ii"]["at_fixed"], 1.0)        # log 0.9 = -0.105 is past 0.07
        self.assertEqual(c2.rates({"t": R}, deflation=0.95)["t"]["power_ii"]["at_fixed"], 0.0)

    def test_c_thresholds_use_the_measured_sds(self):
        rng = np.random.default_rng(6)
        R = np.exp(rng.normal(0, 0.02, (4000, 1)) + rng.normal(0, 0.05, (4000, 16)))
        out = c2.rates({"t": R})["t"]
        ml = np.mean(np.log(R), axis=1)
        self.assertAlmostEqual(out["c"]["ii_threshold"], 3.5 * np.std(ml, ddof=1))
        sd_c = np.std(R, axis=0, ddof=1)
        alpha = np.mean(np.max(np.abs(R - 1) / sd_c, axis=1) > 4.3)
        self.assertAlmostEqual(out["c"]["iii_alpha"]["rate"], alpha)

    def test_the_union_over_truths_and_the_route_to_joseph(self):
        R = np.ones((1000, 16))
        stop = R.copy()
        stop[:4, :3] = 1.25                 # 0.4 % per truth
        out = c2.rates({"a": stop, "b": np.roll(stop, 4, axis=0), "c": np.roll(stop, 8, axis=0)})
        self.assertAlmostEqual(out["over_truths_b"]["union_per_replicate"], 0.012)
        self.assertAlmostEqual(out["over_truths_b"]["union_product"], 1 - 0.996 ** 3)
        self.assertTrue(out["to_joseph"])
        out = c2.rates({"a": stop, "b": stop, "c": stop})          # same replicates fail together: 0.4 %
        self.assertAlmostEqual(out["over_truths_b"]["union_per_replicate"], 0.004)
        self.assertFalse(out["to_joseph"])


import argparse  # noqa: E402
import json  # noqa: E402

import s1_assemble as sa  # noqa: E402
import s5p_universe  # noqa: E402
import test_fd_1b_mc as tmc  # noqa: E402


class Job(tmc.Case):
    """calibrate_main over amendment 2's toy world: one read per universe, the checks, the timing guard, the outputs."""

    def run_job(self, det_equal=True, budget=1e6, r_neg=0, tdw_cv=True, prepare_only=False):
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": json.loads(self.w.pins.read_text()),
                 "npz_sha": "n", "bkg_sha": "b", "tdw_cv": np.ones(50) if tdw_cv else None}
        n_bins = int(np.prod([np.asarray(e).size - 1 for e in self.inputs["edges"]]))
        cells = mc.flat_cells(np.asarray(self.inputs["MCgen"], float), self.inputs["edges"])
        live = np.unique(cells[(cells >= 0) & np.asarray(self.inputs["pass_truth"], bool)])
        fm = np.full(n_bins, -1)
        fm[live] = np.arange(live.size) % sa.N_CELLS           # every reporting cell holds populated fine cells
        U = np.vstack([np.where(fm == c, 1.0, 0.0) for c in range(sa.N_CELLS)])
        real = mc._single

        def single(inputs, bkg, bank_cv, tag, w, flux):
            w = self.consistent(tag, w)
            if not det_equal and "denom_nd" in w:
                w = dict(w, denom_nd=np.asarray(self.inputs["denom_nd"], float) * 1.01)
            return real(inputs, bkg, bank_cv, tag, w, flux)

        def weight(t, inputs, ratio, push):
            rr = np.random.default_rng(len(t)).uniform(0.8, 1.2, inputs["w_truth"].shape[0])
            rr[np.flatnonzero(np.asarray(inputs["pass_truth"], bool))[:r_neg]] = -0.1
            return rr

        a = argparse.Namespace(flux_constraint=self.w.constraint, definition=self.tmp / "d.json", truths=["g18", "ar23"],
                               prep=self.tmp, push=None, expect_push_sha256=None, sets=40, workers=2, draws=300,   # speed: the rule is N-free
                               budget_seconds=budget, bank=self.w.bank, detector_dir=self.w.det,
                               expect_pins_sha256="p", expect_flux_table_sha256="f", expect_cv_tdw_sha256="t",
                               out=self.tmp / "cal" / "cal.json")
        with mock.patch.object(mc, "_load_world", lambda a: world), mock.patch.object(mc, "_single", single), \
                mock.patch.object(sa, "fine_map", lambda p: fm), mock.patch.object(sa, "functional_matrix", lambda f: U), \
                mock.patch.object(mc, "truth_ratio", lambda t, p: (None, None)), \
                mock.patch.object(mc, "truth_weight", weight):
            return c2.prepare(a, rows=True) if prepare_only else c2.calibrate_main(a)

    def test_a_calibration_over_the_toy_world(self):
        rec = self.run_job()
        self.assertEqual(rec["schema"], c2.SCHEMA_CAL)
        self.assertEqual(rec["checks"]["detector_denominator_differs_from_cv"], [])
        self.assertEqual(rec["checks"]["r_negative"]["g18"]["rows"], 0)
        for t in ("g18", "ar23"):
            self.assertEqual(rec["outputs"][t]["sets"], 40)
            self.assertEqual(len(rec["ratio_mean_per_cell"][t]), sa.N_CELLS)
        z = np.load(self.tmp / "cal" / "cal.npz")
        self.assertEqual(z["ratio_g18"].shape, (40, sa.N_CELLS))
        self.assertTrue(np.all(np.isfinite(z["count_ratio_ar23"])))
        self.assertTrue(rec["control_law"]["holds"])
        self.assertIn(rec["verdict"], ("CALIBRATED", "CONTROL_FAILED", "LINEARISATION_TO_DIRECTOR", "I_ALONE_TO_DIRECTOR", "NO_THRESHOLD_TO_DIRECTOR", "POWER_SHORT_TO_DIRECTOR"))
        self.assertEqual(len(rec["rule"]["grid"]), len(c2.S_GRID))
        self.assertEqual(len(rec["control_linearisation"]["g18"]["mean_ratio_minus_1"]), sa.N_CELLS)
        self.assertEqual(rec["atime"]["moved"], [])

    def test_the_checks_are_silent_when_they_hold_and_name_rows_when_not(self):
        rec = self.run_job(r_neg=3)
        self.assertEqual(rec["checks"]["detector_denominator_differs_from_cv"], [])
        with self.assertRaisesRegex(c2.Refusal, "detector denominators differ"):
            self.run_job(det_equal=False)
        with self.assertRaisesRegex(c2.Refusal, "need --cv-tdw"):
            self.run_job(tdw_cv=False)
        self.assertEqual(rec["checks"]["r_negative"]["g18"]["rows"], 3)
        self.assertEqual(len(rec["checks"]["r_negative"]["ar23"]["first_rows"]), 3)

    def test_prepare_uses_the_float32_cv_denominator(self):
        """(e2) in prepare: d_CV is hist_f32(tdw_CV), not the npz's denom_nd, when the two differ (as on the real files)."""
        import s5p_universe
        d32 = s5p_universe.denominator(self.bank_cv, np.ones(50), self.inputs["edges"])
        npz = np.array(d32, float)
        c = np.flatnonzero(np.ravel(npz) > 1)[:2]
        npz.flat[c[0]] -= 1.0
        npz.flat[c[1]] += 1.0
        with mock.patch.dict(self.inputs, {"denom_nd": npz}):
            P = self.run_job(prepare_only=True)
        np.testing.assert_array_equal(P["D_cv_full"], np.ravel(d32))
        self.assertFalse(np.array_equal(P["D_cv_full"], np.ravel(npz)))

    def test_the_budget_guard_refuses_before_the_pool(self):
        with self.assertRaisesRegex(c2.Refusal, "passes the budget"):
            self.run_job(budget=1e-3)


class C2Truth(tmc.Case):
    """D1: c2check's truth is the bulk's. c2_truth's N and Nc for a declared draw equal U x_T of toy_experiment's own
    truth under "data" and "nature" on fd_1b_mc.compose's composite of the same draw (summation order aside)."""

    def matrices(self):
        tags = toys.s1_universes()
        inputs = self.inputs
        n_bins = int(np.prod([np.asarray(e).size - 1 for e in inputs["edges"]]))
        V = {k: [] for k in ("wt", "wr", "bkgw", "tdw", "D")}
        for t in tags:
            w = self.weights_cv_det(t)
            single, _ = mc._single(inputs, self.bkg, self.bank_cv, t, w, self.flux)
            for k in ("wt", "wr", "bkgw"):
                V[k].append(single[k])
            V["tdw"].append(np.asarray(w["tdw"], float) if "tdw" in w else np.ones(50))
            V["D"].append(np.ravel(single["denom"]))
        V = {k: np.array(v) for k, v in V.items()}
        cv = {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
              "bkgw": np.asarray(self.bkg["bkg_w"], float), "tdw": np.ones(50),
              "D": np.ravel(np.asarray(inputs["denom_nd"], float))}
        return tags, V, cv, n_bins

    def test_the_gates_truth_is_the_bulks(self):
        tags, V, cv, n_bins = self.matrices()
        inputs = self.inputs
        col = {t: i for i, t in enumerate(tags)}
        groups = toys.interaction_groups(self.w.bank)
        flux_p = np.full(100, 0.01)
        seeds = [3_620_000, 3_620_001, 3_620_002]
        draws = [mc.draw_universes(toys.draw_for_seed(sd, flux_p, groups)) for sd in seeds]
        _, bands, _ = c2.layout_1b()
        S = c2.selection(draws, col, bands)
        shape = tuple(np.asarray(e).size - 1 for e in inputs["edges"])
        fm = np.arange(n_bins) % sa.N_CELLS
        U = np.vstack([np.where(fm == c, 1.0 + 0.1 * c, 0.0) for c in range(sa.N_CELLS)])
        keep = np.arange(n_bins)
        pack = c2.packing(keep, shape, inputs["edges"])
        ptru, prec = np.asarray(inputs["pass_truth"], bool), np.asarray(inputs["pass_reco"], bool)
        geo = {"gen": np.where(ptru, mc.flat_cells(np.asarray(inputs["MCgen"], float), inputs["edges"]), -1),
               "reco": np.where(prec, mc.flat_cells(np.asarray(inputs["MCreco"], float), inputs["edges"]), -1),
               "bkg": mc.flat_cells(np.asarray(self.bkg["bkg_reco"], float), inputs["edges"]),
               "td": mc.td_cells(self.bank_cv, inputs["edges"]), "fm": fm, "U": U, "shape": shape}
        phi = np.array([self.flux[int(d[0].rpartition("_")[2])] for d in draws])
        r = np.random.default_rng(11).uniform(0.7, 1.3, inputs["w_truth"].shape[0])
        V["wt"][:, :40] *= -1.0                         # negative truth rows, so the clip acts
        tdc = geo["td"]
        counts = np.bincount(tdc[tdc >= 0], minlength=n_bins)
        busy = np.flatnonzero((tdc >= 0) & (counts[np.maximum(tdc, 0)] >= 4))
        self.assertGreater(busy.size, 0)
        V["tdw"][col["MaRES_1"], busy[:1]] = -0.2         # a negative composite row in a cell that stays positive
        V["tdw"][col["MaRES_0"], busy[:1]] = -0.2
        for t in ("MaRES_0", "MaRES_1"):                  # the precondition: each universe's D is its rows' histogram
            V["D"][col[t]] = np.ravel(s5p_universe.denominator(self.bank_cv, V["tdw"][col[t]], inputs["edges"]))
        const = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]), "pack": pack}
        q = c2.c2_truth(V, cv, S, r, geo, phi, const, block=2)

        def load(t):
            w = dict(self.weights_cv_det(t))
            i = col[t]
            w["wt"] = V["wt"][i]
            if "tdw" in w:
                w["tdw"] = V["tdw"][i]
            return w
        moved = 0
        for d, tags_d in enumerate(draws):
            ui, ub, _ = mc.compose(inputs, self.bkg, self.bank_cv, tags_d, load, self.flux, np.ones(50))
            for rule, key in (("data", "N"), ("nature", "Nc")):
                _, x, _ = mc.toy_experiment(inputs, self.bkg, ui, ub, r, seeds[d], rule)
                np.testing.assert_allclose(q[key][:, d], U @ np.ravel(x), rtol=1e-10, atol=0, err_msg=f"{rule} {d}")
            moved += int(np.any(q["Nc"][:, d] != q["N"][:, d]))
        self.assertGreater(moved, 0)
        self.assertTrue(np.all(np.isfinite(q["Nm"])))



if __name__ == "__main__":
    unittest.main()
