"""Repairs (b)-(g) to Z's prospective unified-throw precursor, plus admission accounting.

EVERY FIXTURE IS BUILT FROM THE PRODUCER, NEVER FROM THE RULE UNDER TEST. The bank in
`SyntheticBank` is assembled from `unified_throw_cov._load_bank`'s own requirements -- its knob
stems, its flux-id set, its `cv.npz` key list -- so it can disagree with the code being checked. A
fixture derived from the predicate cannot.

WHAT IS REAL AND WHAT IS SUBSTITUTED, stated because a reader is entitled to know which:
  * REAL: `do_combine` and every guard in it, `check_slab_population`, `cv_support_report`, the
    ROOT write sequence, `z_precursor`'s namespace/freshness/receipt code, `z_precursor_admission`,
    `r5_meter`'s parser and receipt builder, `z_build_path.classify_support_change`,
    `z_contract.check_band_partition`, and all four launcher files as bytes.
  * SUBSTITUTED, with the reason: (1) the LightGBM re-unfold, replaced through the producer's OWN
    injection point -- `unified_throw_cov_5d.py:89` does exactly this in production -- because
    lightgbm is not installed on this checkout; (2) `ROOT`, replaced by
    `test_uq_remediation._StubbedRoot`, because ROOT is not importable here either. That recorder
    separates BUILT from WRITTEN, which is the distinction `3be8c052` exists for.

MUTATION CONTROLS REACH THEIR TARGET. Each one is shown to change the very quantity the guard
reads, and the "would the pre-fix source fail" arms are keyed on AST nodes rather than on comment
markers: a marker that stops matching excises zero lines and the assertions then pass on an
unmodified source.
"""

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
for _p in (str(ND), str(REPO / "2d-unfolding"), str(REPO / "docs" / "orchestration"),
           str(ND / "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import r5_meter                                              # noqa: E402
import unified_throw_cov as U                                # noqa: E402
import z_precursor as ZP                                     # noqa: E402
import z_precursor_admission as ZPA                          # noqa: E402
from test_uq_remediation import _StubbedRoot                 # noqa: E402

LAUNCHER = {name: ND / Path(rel).name for name, rel in ZP.ARM_LAUNCHERS.items()}

#: Bins of the fixture's 2x2x2x1x1 binning.
NBIN = 8


# =============================================================================== the fixtures ====
class SyntheticBank:
    """A bank assembled from `unified_throw_cov._load_bank`'s own demands.

    Not a mock and not truncated to fit: `_load_bank` refuses an incomplete knob set, refuses a
    mismatched flux id set, and refuses anything but exactly `EXPECTED_FLUX_UNIVERSES` universes,
    so the fixture has to satisfy all three or nothing below runs at all. That is the point -- a
    probe truncated to fit stops before the hazard. The file count that falls out, 374, is the same
    count the real `bank_uthrow_5d` carries, which is a coincidence worth nothing on its own and a
    reassurance that the shape is right.
    """

    N_EVENTS = 40

    def __init__(self, root):
        self.path = Path(root) / "bank"
        self.path.mkdir(parents=True, exist_ok=True)
        rng = np.random.default_rng(7)
        edges = [np.array([0., 1., 2.]), np.array([0., 1., 2.]), np.array([0., 1., 2.]),
                 np.array([0., 5.]), np.array([0., 10.])]
        n = self.N_EVENTS
        gen = np.column_stack([rng.uniform(0, 2, n), rng.uniform(0, 2, n), rng.uniform(0, 2, n),
                               rng.uniform(0, 5, n), rng.uniform(0, 10, n)])
        cv = {
            "MCgen": gen, "MCreco": gen + rng.normal(0, .05, gen.shape),
            "measured": gen[: n // 2] + rng.normal(0, .05, (n // 2, 5)),
            "pass_reco": np.ones(n, bool), "pass_truth": np.ones(n, bool),
            "measured_weights": np.ones(n // 2),
            "w_truth": np.ones(n), "w_reco": np.ones(n), "td_w": np.ones(n),
            "td_pt": gen[:, 0], "td_pz": gen[:, 1], "td_ea": gen[:, 2],
            "td_q3": gen[:, 3], "td_W": gen[:, 4],
            "flux": np.array([1.0, 1.0]), "data_pot": 1.0, "n_nucleons": 1.0,
        }
        for i, e in enumerate(edges):
            cv[f"edges_{i}"] = e
        np.savez_compressed(self.path / "cv.npz", **cv)
        for band in U.KNOB_BANDS:
            for idx in (0, 1):
                scale = 1.0 + (0.05 if idx else -0.05)
                for stem in (f"sig_{band}_t_{idx}", f"sig_{band}_r_{idx}", f"td_{band}_{idx}"):
                    np.save(self.path / f"{stem}.npy", np.full(n, scale))
        for u in range(U.EXPECTED_FLUX_UNIVERSES):
            scale = 1.0 + 0.01 * ((u % 7) - 3)
            for stem in (f"sig_flux_t_{u}", f"sig_flux_r_{u}", f"td_flux_{u}"):
                np.save(self.path / f"{stem}.npy", np.full(n, scale))
        np.save(self.path / "flux_univ_ratio.npy",
                np.ones((U.EXPECTED_FLUX_UNIVERSES, 2)))


def kernel(zero_bins=(3,), negative_bins=()):
    """A deterministic stand-in for the LightGBM re-unfold, installed through the PRODUCER's hook.

    `zero_bins` and `negative_bins` are how the fixture manufactures the very states repair (b) is
    about. A GENUINELY ZERO CV bin is otherwise unreachable in a synthetic fixture, and an
    unreachable state is one the mask can never be tested against -- an untestable precondition
    means manufacture it, not caveat it.
    """
    def _kernel(d, edges, wt_sig, wr_sig, wt_td, iters, seed, flux=None):
        base = np.linspace(1.0, 2.0, NBIN)
        scale = (float(np.mean(wt_sig)) * float(np.mean(wr_sig))
                 / max(float(np.mean(wt_td)), 1e-12))
        out = base * scale
        for i in zero_bins:
            out[i] = 0.0
        for i in negative_bins:
            out[i] = -abs(out[i]) - 1e-3
        return out.reshape(2, 2, 2, 1, 1)
    return _kernel


def combine_args(**kw):
    """An argparse-shaped namespace with EVERY `--combine` field the producer's parser declares.

    Derived from `U.main`'s parser rather than hand-listed, so a new option cannot leave these
    tests constructing a namespace the producer would never see.
    """
    defaults = {"bank": None, "iters": 1, "draw_seed": 1000, "estimator_seed": 1000,
                "throws": 0, "throw_offset": 0, "out": None, "combine": None,
                "block_slabs": None, "expected_throws": None, "expected_throw_files": None,
                "expected_block_files": None, "blockunits": False, "block_knobs": "all",
                "block_flux": None, "null": False, "invalid_ratio": "neutral", "out_root": None,
                "flux_universe_file": "/nonexistent"}
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


def write_throw_slabs(directory, n_slabs=4, per=2, skip=(), seed=1000, draw=1000,
                      flux_normalized=1):
    """Throw slabs in `do_throws`'s OWN shape, written with the producer's OWN `_atomic_savez`."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    fake = kernel()
    for task in range(n_slabs):
        if task in skip:
            continue
        ids = [task * per + j for j in range(per)]
        xs = np.array([fake(None, None, np.ones(1) * (1 + .001 * i), np.ones(1),
                            np.ones(1), 1, 1).ravel() for i in ids])
        U._atomic_savez(str(directory / f"uthrow5d_slab_{task}.npz"),
                        xs=xs, throws=np.array(ids), flux_u=np.zeros(per, int),
                        estimator_seed=np.int64(seed), draw_seed=np.int64(draw),
                        est_seed_offset_declared=np.int64(0), est_seed_offset=np.int64(0),
                        flux_normalized=np.int64(flux_normalized))
    return str(directory / "uthrow5d_slab_*.npz")


def write_block_slabs(directory, skip=(), n_flux_tasks=20, seed=1000, draw=1000):
    """Block slabs in `do_blockunits`'s OWN shape, tiling flux 0..99 across `n_flux_tasks`."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    one = kernel()(None, None, np.ones(1), np.ones(1), np.ones(1), 1, 1).ravel()
    stamp = dict(estimator_seed=np.int64(seed), draw_seed=np.int64(draw),
                 est_seed_offset_declared=np.int64(0), est_seed_offset=np.int64(0),
                 flux_normalized=np.int64(1))
    if 0 not in skip:
        xs, labels, kinds = [], [], []
        for band in U.KNOB_BANDS:
            for idx in (0, 1):
                xs.append(one * (1 + .01 * idx))
                labels.append(f"{band}:{idx}")
                kinds.append("knob")
        U._atomic_savez(str(directory / "block5d_knobs.npz"), xs=np.array(xs),
                        labels=np.array(labels, dtype=object),
                        kinds=np.array(kinds, dtype=object), **stamp)
    per = U.EXPECTED_FLUX_UNIVERSES // n_flux_tasks
    for task in range(1, n_flux_tasks + 1):
        if task in skip:
            continue
        lo = (task - 1) * per
        xs, labels, kinds = [], [], []
        for u in range(lo, lo + per):
            xs.append(one * (1 + .0001 * u))
            labels.append(f"flux{u}")
            kinds.append("flux")
        U._atomic_savez(str(directory / f"block5d_flux_{task}.npz"), xs=np.array(xs),
                        labels=np.array(labels, dtype=object),
                        kinds=np.array(kinds, dtype=object), **stamp)
    return str(directory / "block5d_*.npz")


class ProducerFixture(unittest.TestCase):
    """One synthetic bank plus a healthy throw/block population, per test."""

    ZERO_BINS = (3,)
    NEGATIVE_BINS = ()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.work = Path(self._tmp.name)
        self.bank = SyntheticBank(self.work)
        self._saved_kernel = U._xsec_for_weights
        U._xsec_for_weights = kernel(self.ZERO_BINS, self.NEGATIVE_BINS)
        self.addCleanup(setattr, U, "_xsec_for_weights", self._saved_kernel)
        self.throw_glob = write_throw_slabs(self.work / "throws")
        self.block_glob = write_block_slabs(self.work / "blocks")
        self.throw_names = sorted(os.path.basename(p) for p in __import__("glob").glob(
            self.throw_glob))
        self.block_names = sorted(os.path.basename(p) for p in __import__("glob").glob(
            self.block_glob))

    def run_combine(self, *, out_root=None, record=True, **kw):
        fields = {"bank": str(self.bank.path), "combine": self.throw_glob,
                  "block_slabs": self.block_glob, "expected_throws": "0-7",
                  "out_root": out_root}
        fields.update(kw)
        args = combine_args(**fields)
        if not record:
            return U.do_combine(args), None
        with _StubbedRoot() as rec:
            result = U.do_combine(args)
        return result, rec


# ======================================================= (b) the CV operand and its support ====
class TheSupportMaskAndBothCvExecutionsReachTheFile(ProducerFixture):
    """(b) `unified_throw_cov.py:370`'s `rep = x_cv > 0` was computed and thrown away.

    The predicate is UNCHANGED -- changing it would change `nrep`, the covariance dimension and
    every consumer, which is a criterion change and is not authorized. What is repaired is that the
    excluded set is now an object in the artifact. Joseph's ruling *"a pinned-zero inflation bin is
    not a null operand"* names that line, and under a strictly-positive support a genuinely zero bin
    and a bin that never existed are the same absence.
    """

    def test_the_mask_and_the_counts_REACH_THE_FILE(self):
        result, rec = self.run_combine(out_root=str(self.work / "out" / "c.root"), null=True)
        for key in ("hCvSupportMask", "n_cv_bins_total", "n_cv_support", "n_cv_genuine_zero",
                    "n_cv_negative", "n_cv_executions", "cv_support_predicate",
                    "hCvExecution0", "hCvExecution1"):
            self.assertIn(key, rec.written, f"{key} was not WRITTEN (built is not written)")
        self.assertEqual(rec.params["n_cv_bins_total"], NBIN)
        self.assertEqual(rec.params["n_cv_support"], NBIN - len(self.ZERO_BINS))
        self.assertEqual(rec.params["n_cv_genuine_zero"], len(self.ZERO_BINS))
        self.assertEqual(rec.params["cv_support_predicate"], U.CV_SUPPORT_PREDICATE)
        self.assertEqual(result["cv_genuine_zero_indices"].tolist(), list(self.ZERO_BINS))

    def test_the_mask_is_indexed_in_the_BINNING_not_in_the_support(self):
        """A support-indexed mask would be all-ones by construction: the vacuous flag in array form.

        Every other histogram this writer emits is `nrep x nrep`, so this is the one place the
        indexing had to differ, and it is the whole content of the object.
        """
        _result, rec = self.run_combine(out_root=str(self.work / "out" / "c.root"))
        bins = rec.hists["hCvSupportMask"]
        self.assertEqual(len(bins), NBIN - len(self.ZERO_BINS),
                         "the mask set a bin for every support member only")
        set_indices = sorted(k[0] - 1 for k in bins)
        self.assertNotIn(self.ZERO_BINS[0], set_indices,
                         "the genuinely-zero bin must be 0 in the mask, i.e. unset")
        self.assertEqual(max(set_indices), NBIN - 1,
                         "the mask must span the BINNING: its last index is the last bin")

    def test_the_counts_are_written_WHEN_ZERO(self):
        """`BEN-450`'s zero case, and it was the only test that caught the missing write by luck.

        With no genuinely-zero bins the loop that populates the mask never runs, so the key can
        only reach the recorder via `Write()`.
        """
        U._xsec_for_weights = kernel(zero_bins=())
        _result, rec = self.run_combine(out_root=str(self.work / "out" / "c.root"))
        self.assertIn("n_cv_genuine_zero", rec.written)
        self.assertEqual(rec.params["n_cv_genuine_zero"], 0)
        self.assertEqual(rec.params["n_cv_support"], NBIN)
        self.assertIn("hCvSupportMask", rec.written,
                      "an all-ones mask is still a write; with no zero bins the populate loop "
                      "runs, so this arm is weaker than the eavailW one and is paired with the "
                      "mutation control below")

    def test_a_NEGATIVE_cv_bin_is_counted_SEPARATELY_from_a_zero(self):
        """A pinned zero is physics; a negative CV cross section is an arithmetic fault.

        One count carrying both would have two meanings and no way to tell which -- the same reason
        `check_projection_support` keeps declared exclusions off its defect ledger.
        """
        U._xsec_for_weights = kernel(zero_bins=(3,), negative_bins=(5,))
        result, rec = self.run_combine(out_root=str(self.work / "out" / "c.root"))
        self.assertEqual(rec.params["n_cv_genuine_zero"], 1)
        self.assertEqual(rec.params["n_cv_negative"], 1)
        self.assertEqual(result["cv_negative_indices"].tolist(), [5])
        self.assertEqual(rec.params["n_cv_support"], NBIN - 2)

    def test_n_cv_executions_has_TWO_REACHABLE_VALUES(self):
        """A flag with one reachable value is not a flag (`BEN-256` rule 2), and lane D deleted
        exactly that shape from `eavailW_covariance`. `--null` is optional, so this one can be 1."""
        _r1, rec1 = self.run_combine(out_root=str(self.work / "a.root"), null=False)
        _r2, rec2 = self.run_combine(out_root=str(self.work / "b.root"), null=True)
        self.assertEqual(rec1.params["n_cv_executions"], 1)
        self.assertEqual(rec2.params["n_cv_executions"], 2)
        self.assertNotIn("hCvExecution1", rec1.written,
                         "without --null there is no second genuine execution to persist")
        self.assertIn("hCvExecution1", rec2.written)

    def test_the_second_execution_is_persisted_as_a_VECTOR_not_a_norm(self):
        """Before this repair the second CV existed only inside `||CV2-CV||`. A norm cannot say
        which bin moved, and cannot be re-checked under a different support."""
        result, rec = self.run_combine(out_root=str(self.work / "c.root"), null=True)
        self.assertEqual(result["n_cv_executions"], 2)
        for vector in result["cv_executions"]:
            self.assertEqual(vector.size, NBIN,
                             "an execution is persisted UNMASKED, over the whole binning")
        self.assertEqual(len(rec.hists["hCvExecution1"]), NBIN)

    def test_provenance_accompanies_the_operand(self):
        _result, rec = self.run_combine(out_root=str(self.work / "c.root"))
        self.assertEqual(rec.params["cv_bank_path"], str(self.bank.path.resolve()))
        self.assertNotEqual(rec.params["cv_bank_cv_sha256"], "UNAVAILABLE")
        self.assertEqual(len(rec.params["cv_producer_sha256"]), 64)

    def test_a_non_finite_cv_REFUSES(self):
        with self.assertRaises(SystemExit) as caught:
            U.cv_support_report(np.array([1.0, np.nan, 2.0]))
        self.assertIn("non-finite", str(caught.exception))

    def test_the_three_populations_PARTITION_the_binning(self):
        """POSITIVE CONTROL on the report's own arithmetic: support + zero + negative == total, so
        no bin can be in two of them and none can be in none."""
        for zeros, negatives in (((), ()), ((3,), ()), ((3,), (5,)), ((0, 7), (1,))):
            with self.subTest(zeros=zeros, negatives=negatives):
                x = np.linspace(1.0, 2.0, NBIN)
                for i in zeros:
                    x[i] = 0.0
                for i in negatives:
                    x[i] = -1.0
                report = U.cv_support_report(x)
                self.assertEqual(
                    report["n_support"] + report["n_zero"] + report["n_negative"],
                    report["n_total"])


class TheSupportWritesAreMutationControlled(ProducerFixture):
    """POWER. Without these, every assertion above is satisfiable by code that builds and discards.

    Keyed on AST nodes, per `3be8c052`'s specification: a comment-marker excision that stops
    matching removes zero lines and the assertions then pass on an unmodified source -- a power
    test that has silently stopped being one.
    """

    def _module_without(self, needle):
        """`unified_throw_cov` re-imported with every `Write()` call mentioning `needle` removed.

        SUBSTITUTION, not deletion: the writes sit inside a multi-line `for` body and dropping a
        line would leave a syntactically broken module, on which every absence assertion is
        trivially true. `ast.parse` afterwards is what catches that, and it caught it here.
        """
        source = (ND / "unified_throw_cov.py").read_text()
        tree = ast.parse(source)
        lines = source.split("\n")
        combine = next((n for n in tree.body
                        if isinstance(n, ast.FunctionDef) and n.name == "do_combine"), None)
        self.assertIsNotNone(combine, "do_combine not found: this power test cannot locate its "
                                      "subject and would otherwise pass vacuously")
        hit = 0
        for node in ast.walk(combine):
            if not isinstance(node, ast.stmt):
                continue
            lo, hi = node.lineno - 1, (node.end_lineno or node.lineno)
            segment = "\n".join(source.split("\n")[lo:hi])
            if needle not in segment or ".Write()" not in segment:
                continue
            if hi - lo != 1:
                continue                       # only single-statement writes are excised
            indent = len(lines[lo]) - len(lines[lo].lstrip())
            lines[lo] = " " * indent + "pass"
            hit += 1
        self.assertGreater(hit, 0, f"no single-line Write() statement mentions {needle!r}: this "
                                   f"mutation would excise nothing and the arms below would pass "
                                   f"on an UNMODIFIED module")
        mutated = "\n".join(lines)
        ast.parse(mutated)                      # a broken module makes every absence assertion true
        module = types.ModuleType("unified_throw_cov_mutated")
        module.__file__ = str(ND / "unified_throw_cov.py")
        exec(compile(mutated, str(ND / "unified_throw_cov.py"), "exec"), module.__dict__)
        module._xsec_for_weights = kernel(self.ZERO_BINS, self.NEGATIVE_BINS)
        return module, hit

    def _combine_with(self, module, **kw):
        args = combine_args(bank=str(self.bank.path), combine=self.throw_glob,
                            block_slabs=self.block_glob, expected_throws="0-7",
                            out_root=str(self.work / "m.root"), **kw)
        with _StubbedRoot() as rec:
            module.do_combine(args)
        return rec

    def test_deleting_the_mask_write_makes_the_assertions_FAIL(self):
        """`3be8c052` exists because a ROOT stub could not tell WRITTEN from BUILT, so deleting
        `hmask.Write()` left the suite green. This is the arm that must not."""
        module, hit = self._module_without("hmask")
        self.assertEqual(hit, 1, "exactly the one mask write is expected")
        rec = self._combine_with(module)
        self.assertNotIn("hCvSupportMask", rec.written,
                         "the mutation did not reach the write it targets")
        self.assertIn("hCvSupportMask", rec.hists,
                      "the object is still BUILT -- which is precisely the state the pre-3be8c052 "
                      "recorder could not distinguish from written, and the reason this arm exists")

    def test_deleting_each_count_write_makes_the_assertions_FAIL(self):
        for needle, key in (("n_cv_genuine_zero", "n_cv_genuine_zero"),
                            ("n_cv_support", "n_cv_support"),
                            ("n_cv_executions", "n_cv_executions"),
                            ("cv_support_predicate", "cv_support_predicate")):
            with self.subTest(needle=needle):
                module, _hit = self._module_without(needle)
                rec = self._combine_with(module)
                self.assertNotIn(key, rec.written,
                                 f"the mutation did not reach {key}'s write")

    def test_POSITIVE_CONTROL_the_unmutated_module_writes_everything(self):
        """A mutation harness that broke the module would make every arm above pass. This runs the
        SAME harness path with no mutation applied and requires the writes to be there."""
        source = (ND / "unified_throw_cov.py").read_text()
        module = types.ModuleType("unified_throw_cov_pristine")
        module.__file__ = str(ND / "unified_throw_cov.py")
        exec(compile(source, str(ND / "unified_throw_cov.py"), "exec"), module.__dict__)
        module._xsec_for_weights = kernel(self.ZERO_BINS, self.NEGATIVE_BINS)
        rec = self._combine_with(module, null=True)
        for key in ("hCvSupportMask", "n_cv_genuine_zero", "n_cv_support", "n_cv_executions",
                    "cv_support_predicate", "hCvExecution0", "hCvExecution1"):
            self.assertIn(key, rec.written, f"{key} missing from an UNMUTATED module")


# ===================================================== (d) exact expected-population validation ==
class ThePopulationIsCheckedByIDENTITYinBothDirections(ProducerFixture):
    """(d) `--expected-ids` occurs ZERO times in the four launchers -- it belongs to the FINALIZE
    launcher -- and `--block-slabs` was a bare glob with no declared population.

    ⚠ AND MY BRIEFING'S PREMISE WAS WRONG, measured. "A short block arm combines silently" is FALSE:
    the 20 flux tasks tile 0..99 exactly, so a missing task leaves the flux inventory short and the
    producer already refuses. The tests below record that as a POSITIVE CONTROL on the existing
    guards, and the case that actually passed is the foreign namespace.
    """

    def test_POSITIVE_CONTROL_the_exact_declared_population_passes_silently(self):
        result, _rec = self.run_combine(
            out_root=str(self.work / "c.root"),
            expected_throw_files=",".join(self.throw_names),
            expected_block_files=",".join(self.block_names))
        self.assertTrue(result["throw_population_declared"])
        self.assertTrue(result["block_population_declared"])
        self.assertEqual(result["block_population"]["n_expected"], len(self.block_names))

    def test_a_MISSING_declared_member_refuses_and_names_it(self):
        os.remove(self.work / "blocks" / "block5d_flux_3.npz")
        with self.assertRaises(SystemExit) as caught:
            self.run_combine(expected_block_files=",".join(self.block_names))
        self.assertIn("MISSING", str(caught.exception))
        self.assertIn("block5d_flux_3.npz", str(caught.exception))

    def test_a_STALE_or_EXTRA_member_refuses_and_names_it(self):
        """The direction a count cannot see, and the one a one-directional check waves through."""
        import shutil
        shutil.copy2(self.work / "blocks" / "block5d_flux_3.npz",
                     self.work / "blocks" / "block5d_flux_3_stale.npz")
        with self.assertRaises(SystemExit) as caught:
            self.run_combine(expected_block_files=",".join(self.block_names))
        self.assertIn("UNDECLARED", str(caught.exception))
        self.assertIn("block5d_flux_3_stale.npz", str(caught.exception))

    def test_a_DUPLICATE_in_the_declaration_refuses(self):
        with self.assertRaises(SystemExit) as caught:
            U.check_slab_population(self.block_glob,
                                    self.block_names + [self.block_names[0]], "block")
        self.assertIn("repeats", str(caught.exception))

    def test_a_GLOB_or_a_PATH_in_the_declaration_refuses(self):
        for bad in ("block5d_*.npz", "blocks/block5d_knobs.npz", "block5d_flux_?.npz"):
            with self.subTest(entry=bad):
                with self.assertRaises(SystemExit) as caught:
                    U.check_slab_population(self.block_glob, [bad], "block")
                self.assertIn("not a plain basename", str(caught.exception))

    def test_an_EMPTY_declaration_refuses_as_a_NON_declaration(self):
        for empty in ([], [""], ["  ", ""]):
            with self.subTest(declaration=empty):
                with self.assertRaises(SystemExit) as caught:
                    U.check_slab_population(self.block_glob, empty, "block")
                self.assertIn("not a declaration", str(caught.exception))

    def test_a_SHORT_block_arm_was_ALREADY_refused_by_the_content_inventory(self):
        """POSITIVE CONTROL on the pre-existing guards, and the correction to my own briefing.

        Deleting flux task 3 removes universes 15..19, which the `expected_flux_ids` check at
        `unified_throw_cov.py:462` catches WITHOUT any file declaration.
        """
        os.remove(self.work / "blocks" / "block5d_flux_3.npz")
        with self.assertRaises(SystemExit) as caught:
            self.run_combine()
        self.assertIn("flux block inventory mismatch", str(caught.exception))

    def test_a_SHORT_throw_arm_was_ALREADY_refused_by_expected_throws(self):
        short = write_throw_slabs(self.work / "throws_short", skip=(1,))
        with self.assertRaises(SystemExit) as caught:
            args = combine_args(bank=str(self.bank.path), combine=short,
                                block_slabs=self.block_glob, expected_throws="0-7")
            U.do_combine(args)
        self.assertIn("throw id mismatch", str(caught.exception))

    def test_a_FOREIGN_but_inventory_complete_namespace_PASSES_and_that_is_the_LIMIT(self):
        """THE MEASURED HOLE, recorded as a test so it cannot be forgotten or overstated.

        A complete set of another campaign's block slabs carries the SAME basenames, so the file
        identity check passes on it and every content check passes too. File identity and namespace
        freshness are two guards over two different populations and NEITHER SUBSUMES THE OTHER:
        `z_precursor.check_namespace_fresh` is what catches this one.
        """
        foreign = write_block_slabs(self.work / "foreign_campaign")
        result, _rec = self.run_combine(
            out_root=str(self.work / "c.root"), block_slabs=foreign,
            expected_block_files=",".join(self.block_names))
        self.assertTrue(result["block_population_declared"],
                        "identity validation ran and PASSED on a foreign namespace")
        # and the guard that DOES catch it:
        plan = ZP.namespace_plan(str(self.work), namespace="ns")
        target = Path(plan["arms"]["block"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        write_block_slabs(target)
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_namespace_fresh(plan, ["block"])
        self.assertIn("NOT FRESH", str(caught.exception))

    def test_the_population_FLAGS_have_two_reachable_values(self):
        declared, _rec = self.run_combine(
            out_root=str(self.work / "a.root"),
            expected_block_files=",".join(self.block_names))
        undeclared, _rec2 = self.run_combine(out_root=str(self.work / "b.root"))
        self.assertTrue(declared["block_population_declared"])
        self.assertFalse(undeclared["block_population_declared"])

    def test_the_population_check_refuses_BEFORE_the_CV_RE_UNFOLD(self):
        """ORDERING, PINNED. The check first sat after the CV execution, so a glob mismatch cost a
        5-iteration LightGBM re-unfold over the 5D bank -- the expensive part of a 3 h job --
        before anyone was told the population was wrong.

        Proved by making the re-unfold FATAL: a kernel that raises. If the refusal still arrives as
        the population SystemExit, nothing reached the kernel. A test asserting on elapsed time or
        on print order could not settle this.
        """
        def explode(*_a, **_k):
            raise AssertionError("the CV re-unfold ran before the population was validated")

        U._xsec_for_weights = explode
        with self.assertRaises(SystemExit) as caught:
            self.run_combine(expected_block_files="block5d_nonexistent.npz")
        self.assertIn("block slab population", str(caught.exception))
        # POSITIVE CONTROL on the harness: with a VALID declaration the kernel IS reached, so the
        # arm above is not passing merely because this fixture never gets that far.
        with self.assertRaises(AssertionError) as reached:
            self.run_combine(expected_block_files=",".join(self.block_names))
        self.assertIn("ran before the population was validated", str(reached.exception))

    # ---- JOSEPH'S THREE DIRECTIONS, 2026-09-11 -------------------------------------------------
    # "incomplete outputs must never match the consumer's input selection. Preserve atomic
    #  publication of completed products, and test interrupted writes, stale temporary files, and
    #  successful completion."
    #
    # All three below can fail, and the third is the one that catches a repair which fixes
    # SELECTION by breaking PUBLICATION -- mutation-controlled in
    # `test_MUTATION_breaking_publication_is_caught_by_the_completion_arm`.

    def test_ARM1_an_INTERRUPTED_write_cannot_be_SELECTED(self):
        """Joseph's direction 1. A temp left by a KILLED process, manufactured not asserted.

        `sys.path[0]` and process death are both properties of an interpreter's own lifetime, so
        the only honest fixture is a CHILD that really dies mid-write. SIGKILL, so no handler of
        any kind runs -- which is the whole point: `_atomic_savez`'s `except` branch would have
        cleaned up, and a wall-clock kill does not give it the chance.
        """
        target = self.work / "arm1"
        target.mkdir(parents=True, exist_ok=True)
        script = target / "victim.py"
        # THE STAND-IN TAKES THE HANDLE, BECAUSE THAT IS THE REAL INTERFACE. `_atomic_savez` passes
        # an open FILE OBJECT to `savez_compressed` (it must -- passing a name makes numpy append
        # `.npz`), so a stand-in taking a path would be testing an interface the producer does not
        # use. My first version took a path and failed for that reason, which is the fixture
        # disagreeing with the producer rather than with the world.
        script.write_text(
            "import os, signal, sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import numpy as np, unified_throw_cov as U\n"
            "def die(fh, **kw):\n"
            "    fh.write(b'PARTIAL'); fh.flush(); os.fsync(fh.fileno())\n"
            "    sys.stderr.write('wrote-partial\\n'); sys.stderr.flush()\n"
            "    os.kill(os.getpid(), signal.SIGKILL)\n"
            "U.np.savez_compressed = die\n"
            f"U._atomic_savez({str(target / 'block5d_knobs.npz')!r}, xs=np.arange(3))\n")
        proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertIn("wrote-partial", proc.stderr,
                      "fixture precondition: the child must have written a partial temp")
        self.assertNotEqual(proc.returncode, 0, "the child must have died, not returned")

        leftovers = U.find_incomplete_writes(target)
        self.assertEqual(len(leftovers), 1,
                         f"the kill must leave exactly one incomplete write, got {leftovers}")
        self.assertFalse((target / "block5d_knobs.npz").exists(),
                         "and NO product: the rename never happened")

        # THE PROPERTY JOSEPH STATED, over every pattern a consumer could plausibly write.
        for pattern in ("block5d_*.npz", "*.npz", "*.np[yz]", "*"):
            with self.subTest(pattern=pattern):
                selected = __import__("glob").glob(str(target / pattern))
                self.assertEqual([p for p in selected if U.is_incomplete_write(p)], [],
                                 f"an interrupted write was SELECTED by {pattern!r}")
        # And the shell agrees, which matters because a future consumer may glob in bash.
        shell = subprocess.run(["bash", "-c", f'cd {target!s} && ls block5d_*.npz 2>/dev/null'],
                               capture_output=True, text=True)
        self.assertEqual(shell.stdout.strip(), "",
                         "a shell glob selected the interrupted write")
        # The DIRECTED scan still reports it, as ITSELF.
        with self.assertRaises(SystemExit) as caught:
            U.check_slab_population(str(target / "block5d_*.npz"),
                                    ["block5d_knobs.npz"], "block")
        self.assertIn("INCOMPLETE write", str(caught.exception))
        self.assertNotIn("UNDECLARED", str(caught.exception))

    def test_ARM2_a_STALE_temp_from_an_EARLIER_run_is_present_at_selection_time(self):
        """Joseph's direction 2, in BOTH eras, because the cluster holds products from both.

        A pre-repair temp is glob-VISIBLE, so it is the case that can still be selected by an
        UNREPAIRED consumer -- which is why the legacy spelling is kept as a live predicate rather
        than deleted as superseded.
        """
        target = self.work / "arm2"
        target.mkdir(parents=True, exist_ok=True)
        for name in ("block5d_knobs.npz", "block5d_flux_1.npz"):
            U._atomic_savez(str(target / name), xs=np.arange(3))
        declared = ["block5d_knobs.npz", "block5d_flux_1.npz"]

        stale_new = target / U.incomplete_name("block5d_flux_9.npz", "deadbeef")
        stale_old = target / f"block5d_flux_9.npz.cafe{U.LEGACY_IN_PROGRESS_SUFFIX}"
        for stale in (stale_new, stale_old):
            with self.subTest(stale=stale.name):
                stale.write_bytes(b"stale from an earlier run")
                self.assertTrue(U.is_incomplete_write(stale.name))
                with self.assertRaises(SystemExit) as caught:
                    U.check_slab_population(str(target / "block5d_*.npz"), declared, "block")
                self.assertIn("INCOMPLETE write", str(caught.exception))
                self.assertIn(stale.name, str(caught.exception))
                stale.unlink()

        # THE ERA IS NAMED, so a reader can tell today's kill from a June leftover.
        stale_old.write_bytes(b"x")
        self.addCleanup(stale_old.unlink)
        with self.assertRaises(SystemExit) as caught:
            U.check_slab_population(str(target / "block5d_*.npz"), declared, "block")
        self.assertIn("1 pre-repair", str(caught.exception))
        self.assertIn("0 post-repair", str(caught.exception))
        # ...and ONLY the legacy one is glob-visible, which is the asymmetry that justifies keeping
        # the legacy predicate at all.
        visible = __import__("glob").glob(str(target / "block5d_*.npz"))
        self.assertIn(stale_old.name, [os.path.basename(v) for v in visible])
        stale_new.write_bytes(b"x")
        self.addCleanup(stale_new.unlink)
        visible = [os.path.basename(v) for v in
                   __import__("glob").glob(str(target / "block5d_*.npz"))]
        self.assertNotIn(stale_new.name, visible)

    def test_ARM3_SUCCESSFUL_COMPLETION_publishes_atomically_and_IS_selected(self):
        """Joseph's direction 3, the positive control, and the arm that catches a repair which
        fixes selection by BREAKING publication.

        A guard that made incomplete writes unselectable by never renaming would satisfy arms 1
        and 2 perfectly and lose every product.
        """
        target = self.work / "arm3"
        names = ["block5d_knobs.npz"] + [f"block5d_flux_{t}.npz" for t in range(1, 4)]
        for name in names:
            U._atomic_savez(str(target / name), xs=np.arange(5), seed=np.int64(7))

        # PUBLISHED: present, readable, complete, and with its content intact.
        for name in names:
            with np.load(target / name) as slab:
                np.testing.assert_array_equal(slab["xs"], np.arange(5))
                self.assertEqual(int(slab["seed"]), 7)

        # NOTHING LEFT BEHIND -- the completed path cleans up after itself.
        self.assertEqual(U.find_incomplete_writes(target), [])
        self.assertEqual(sorted(p.name for p in target.iterdir()), sorted(names),
                         "the directory holds exactly the published products")

        # AND SELECTED: the whole point of the repair is that this still works.
        selected = sorted(os.path.basename(p) for p in
                          __import__("glob").glob(str(target / "block5d_*.npz")))
        self.assertEqual(selected, sorted(names),
                         "a completed product must still be SELECTED by the consumer's glob")
        report = U.check_slab_population(str(target / "block5d_*.npz"), names, "block")
        self.assertEqual(report["n_expected"], len(names))
        self.assertEqual(report["n_found"], len(names))

    #: Every `.npz` selection pattern in every tracked launcher, DERIVED not listed. The review's
    #: scope correction: the consumer population is the launchers that SELECT these products, which
    #: is far wider than the four precursor arms, and a list would have been my guess at it.
    @staticmethod
    def launcher_npz_globs():
        pats = {}
        for sh in sorted(ND.glob("sbatch_*.sh")):
            for line in sh.read_text().split("\n"):
                if line.lstrip().startswith("#"):
                    continue
                for m in re.finditer(r"[\'\"]([^\'\"]*\*[^\'\"]*\.npz)[\'\"]", line):
                    pats.setdefault(os.path.basename(m.group(1)), set()).add(sh.name)
        return pats

    def test_the_CONSUMER_POPULATION_is_derived_and_the_NAME_is_unselectable_across_ALL_of_it(self):
        """The review's points 1 and 2: re-derive the population from the CONSUMERS, and harden
        BOTH selection surfaces.

        SURFACE 1 is the bare launcher glob. SURFACE 2 is the declared-population check in
        `check_slab_population`. A repair hardening one leaves the other exposed, so both are
        asserted here for every pattern any tracked launcher actually uses.

        THE PATTERNS ARE DERIVED FROM THE LAUNCHERS, not retyped: a list would be my guess at the
        consumer set, and my guess is what the review corrected.
        """
        globs = self.launcher_npz_globs()
        # THE PARTITION IS PINNED, so a NEW stem forces a decision instead of quietly joining the
        # covered side. MEASURED 2026-09-11: 8 stems across 13 launchers -- which is wider than the
        # "nine launchers over five stems" I was given, and wider again than the four precursor
        # arms I started from. Scope of the derivation, stated because it bounds the claim:
        # `.npz` selection patterns on NON-COMMENT lines of tracked `nd-unfolding/sbatch_*.sh`.
        COVERED = {"block4d_*.npz", "block5d_*.npz", "blockfps_*.npz",
                   "uthrow4d_slab_*.npz", "uthrow5d_slab_*.npz", "uthrowfps_slab_*.npz"}
        UNCOVERED = {"res_boot_*.npz", "res_split_*.npz"}
        self.assertEqual(set(globs), COVERED | UNCOVERED,
                         "the consumer population moved. A new `.npz` selection pattern must be "
                         "classified: COVERED if its producer routes through `_atomic_savez`, "
                         "UNCOVERED if it writes straight to its --out (see the uncovered-producer "
                         "arm). Defaulting it to either side is the widening this pin prevents.")
        self.assertEqual(len({l for v in globs.values() for l in v}), 13,
                         "the launcher count moved; re-derive the population before trusting any "
                         "coverage claim about it")
        for stem in sorted(UNCOVERED):
            globs.pop(stem)
        target = self.work / "population"
        target.mkdir(parents=True, exist_ok=True)
        real_replace = U.os.replace
        for pattern, launchers in sorted(globs.items()):
            product = pattern.replace("*", "7")
            with self.subTest(pattern=pattern, launchers=sorted(launchers)):
                # An interrupted write for THIS stem: publication suppressed so the temp survives.
                U.os.replace = lambda *a, **k: None
                try:
                    U._atomic_savez(str(target / product), xs=np.arange(3))
                finally:
                    U.os.replace = real_replace
                temps = U.find_incomplete_writes(target)
                self.assertEqual(len(temps), 1, f"expected one temp, got {temps}")
                # SURFACE 1: the launcher's own pattern must not select it.
                selected = [os.path.basename(q) for q in
                            __import__("glob").glob(str(target / pattern))]
                self.assertEqual(selected, [],
                                 f"{pattern!r} (used by {sorted(launchers)}) SELECTED an "
                                 f"incomplete write: {temps}")
                # SURFACE 2: the declared-population check must refuse it, as ITSELF.
                with self.assertRaises(SystemExit) as caught:
                    U.check_slab_population(str(target / pattern), [product], "population")
                self.assertIn("INCOMPLETE write", str(caught.exception))
                (target / temps[0]).unlink()

    def test_a_COULD_NOT_LOOK_scan_REFUSES_instead_of_reporting_CLEAN(self):
        """F1. `find_incomplete_writes` returned `[]` for a directory it could not read, so
        could-not-look was indistinguishable from clean -- one layer BELOW the name-based
        guarantee.

        WHAT THIS DOES AND DOES NOT AFFECT, stated because the severity matters: Joseph's primary
        guarantee is that an incomplete write is never SELECTED, and that rests on the NAME, so it
        was never touched by this. What was degraded is the OPERATOR REPORT -- nobody was told a
        task had died. So the blindness is fixed rather than the guarantee re-scoped.
        """
        blind = self.work / "blind"
        blind.mkdir(parents=True, exist_ok=True)
        (blind / U.incomplete_name("block5d_knobs.npz", "tok")).write_bytes(b"PARTIAL")
        os.chmod(blind, 0o000)
        self.addCleanup(os.chmod, blind, 0o700)
        with self.assertRaises(U.ScanBlind) as caught:
            U.find_incomplete_writes(blind)
        self.assertIn("could not look", str(caught.exception))
        # AND THE CONSUMER TURNS IT INTO A REFUSAL, not a pass.
        with self.assertRaises(SystemExit) as refused:
            U.check_slab_population(str(blind / "block5d_*.npz"), ["block5d_knobs.npz"], "block")
        self.assertIn("could not look", str(refused.exception))
        # POSITIVE CONTROL: readable and clean must still pass silently, or this guard refuses
        # every correct run.
        os.chmod(blind, 0o700)
        for name in U.find_incomplete_writes(blind):
            (blind / name).unlink()
        U._atomic_savez(str(blind / "block5d_knobs.npz"), xs=np.arange(3))
        self.assertEqual(U.find_incomplete_writes(blind), [])
        self.assertEqual(
            U.check_slab_population(str(blind / "block5d_*.npz"),
                                    ["block5d_knobs.npz"], "block")["n_found"], 1)

    def test_a_WILDCARD_DIRECTORY_component_is_EXPANDED_not_treated_as_a_literal(self):
        """F1's second case, and the one that actually PASSED with an incomplete write present.

        `check_slab_population` derived its scan directory as `os.path.dirname(pattern)`. For
        `.../ns_*/block5d_*.npz` that is the unopenable literal `.../ns_*`, so the scan hit
        `OSError`, returned `[]`, and the check passed while an incomplete write sat in the very
        directory it selected from. Reproduced before fixing.

        LATENT TODAY: all 18 launcher patterns across the THREE glob-bearing flags -- `--combine`
        (`:735`), `--block-slabs`, and the population declarations -- have fixed directory
        components. Repaired regardless: "no current caller does this" is a property of today's
        callers, not of the function.
        """
        root = self.work / "wild"
        member = root / "ns_run7"
        member.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(member / "block5d_knobs.npz"), xs=np.arange(3))
        (member / U.incomplete_name("block5d_flux_1.npz", "tok")).write_bytes(b"PARTIAL")
        pattern = str(root / "ns_*" / "block5d_*.npz")

        self.assertEqual(U.incomplete_write_scan_dirs(pattern), [str(member)],
                         "the wildcard directory component must be EXPANDED")
        found, scanned = U.find_incomplete_writes_for_pattern(pattern)
        self.assertEqual(len(found), 1, f"the scan must reach into the matched directory: {found}")
        self.assertEqual(scanned, [str(member)])
        with self.assertRaises(SystemExit) as caught:
            U.check_slab_population(pattern, ["block5d_knobs.npz"], "block")
        self.assertIn("INCOMPLETE write", str(caught.exception))

        # A wildcard matching NOTHING must not be blind either: the MISSING arm reports it.
        with self.assertRaises(SystemExit) as missing:
            U.check_slab_population(str(root / "nomatch_*" / "block5d_*.npz"),
                                    ["block5d_knobs.npz"], "block")
        self.assertIn("MISSING", str(missing.exception))
        self.assertEqual(U.incomplete_write_scan_dirs(str(root / "nomatch_*" / "x_*.npz")), [])

    def test_CONCURRENT_writes_to_ONE_product_get_DISTINCT_temps(self):
        """F3 / T9: the concurrency property had nothing asserting it.

        It HOLDS -- `NamedTemporaryFile` yields a distinct token per call -- but nothing would have
        noticed if the token were dropped "for readability", and every other arm would have stayed
        green: one writer still publishes correctly, and the name is still unselectable. What
        breaks is two array tasks writing the same product concurrently, where a shared temp name
        means one clobbers the other's partial file and the survivor publishes a mixture.

        THIS ARM FAILS IF THE TOKEN GOES, which is the only thing that makes the property defended
        rather than merely true.
        """
        target = self.work / "concurrent"
        target.mkdir(parents=True, exist_ok=True)
        product = str(target / "block5d_knobs.npz")
        real_replace = U.os.replace
        temps = []
        U.os.replace = lambda src, dst: temps.append(src)
        try:
            for _ in range(4):
                U._atomic_savez(product, xs=np.arange(3))
        finally:
            U.os.replace = real_replace
        self.assertEqual(len(temps), 4)
        self.assertEqual(len(set(temps)), 4,
                         f"four writes to ONE product produced {len(set(temps))} distinct temp "
                         f"name(s): {[os.path.basename(x) for x in temps]}. A shared name means "
                         f"concurrent array tasks clobber each other's partial file and the "
                         f"survivor publishes a mixture of two writes.")
        # The token is what carries it: the names differ ONLY in the token position.
        for path in temps:
            base = os.path.basename(path)
            self.assertTrue(base.startswith(f"{U.INCOMPLETE_PREFIX}block5d_knobs.npz."))
            self.assertTrue(base.endswith(U.INCOMPLETE_SUFFIX))
            token = base[len(U.INCOMPLETE_PREFIX) + len("block5d_knobs.npz."):
                         -len(U.INCOMPLETE_SUFFIX)]
            self.assertTrue(token, "the token is empty -- distinctness has been removed")
        self.assertEqual(len({os.path.basename(x) for x in temps}), 4)

    def test_the_INVISIBILITY_claim_is_SCOPED_to_the_idioms_it_covers(self):
        """The universally-stated claim, bounded by measurement.

        `glob.glob` and shell globs refuse a leading dot under ANY pattern including bare `*`.
        `pathlib` does NOT: `Path().glob('*')` and `Path().iterdir()` both return the dotfile. That
        is not live -- no production module under `nd-unfolding/` selects slabs that way -- and it
        is the hole guarantee (2), the `.partial` suffix, exists to close. Asserted rather than
        described, because the universal form of the sentence would send a future consumer straight
        at the one idiom it excludes.
        """
        target = self.work / "idioms"
        target.mkdir(parents=True, exist_ok=True)
        temp = target / U.incomplete_name("block5d_knobs.npz", "tok")
        temp.write_bytes(b"PARTIAL")
        U._atomic_savez(str(target / "block5d_knobs.npz"), xs=np.arange(3))

        for pattern in ("*", "*.npz", "block5d_*.npz", "*.np[yz]"):
            with self.subTest(idiom="glob.glob", pattern=pattern):
                self.assertNotIn(temp.name, [os.path.basename(q) for q in
                                             __import__("glob").glob(str(target / pattern))])
        shell = subprocess.run(["bash", "-c", f'cd {target!s} && ls *'],
                               capture_output=True, text=True)
        self.assertNotIn(temp.name, shell.stdout.split())

        # THE EXCLUDED IDIOMS, measured so the boundary is a fact and not a caveat.
        self.assertIn(temp.name, [q.name for q in target.glob("*")],
                      "pathlib DOES see it; if that ever changes, the scoping comment is stale")
        self.assertIn(temp.name, [q.name for q in target.iterdir()])
        # ...and guarantee (2) is what covers them: the suffix keeps it out of any .npz selection.
        self.assertNotIn(temp.name, [q.name for q in target.glob("*.npz")])
        self.assertFalse(temp.name.endswith(".npz"))
        # No production module CALLS the excluded idioms.
        #
        # ⚠ AST, NOT SUBSTRING, and my first version proved why: it banned the text `.iterdir()`
        # and fired on `unified_throw_cov.py`'s own comment explaining that pathlib sees these
        # files. Banning the warning is not a check -- right check, wrong operand, the same shape
        # this suite has caught four times now. Only a CALL can select anything.
        # `os.walk` IS DELIBERATELY NOT IN THIS SET, and measuring is what removed it. Four
        # production modules call it -- `mnv_guard_firing_census.py`, `mnv_source_manifest.py`,
        # `p4_lib.py`, `protect_throw_slabs.py` -- so banning it would have failed on four correct
        # modules. A tree walk is not by itself a product selection; what matters is the FILTER
        # applied to what it yields. `protect_throw_slabs` is the one that filters for slabs and it
        # gets its own arm below.
        excluded = {"iterdir", "rglob", "scandir"}
        for module in sorted(ND.glob("*.py")):
            with self.subTest(module=module.name):
                calls = {node.func.attr for node in ast.walk(ast.parse(module.read_text()))
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                         and node.func.attr in excluded}
                self.assertEqual(calls, set(),
                                 f"{module.name} CALLS {sorted(calls)}, which SEE incomplete "
                                 f"writes; the scoping comment at INCOMPLETE_PREFIX must be "
                                 f"revisited, and guarantee (2) is what would have to carry it")

    def test_protect_throw_slabs_REJECTS_an_incomplete_write_via_GUARANTEE_2(self):
        """A REAL CONSUMER THAT WALKS, so the leading dot does NOT protect it -- and the concrete
        demonstration that guarantee (2) is load-bearing rather than belt-and-braces.

        `protect_throw_slabs.find_slabs` (`:67-71`) walks the tree and collects
        `fn.endswith(".npz") and ("slab" in fn.lower() or in_slab_dir)`. `os.walk` yields dotfiles,
        so guarantee (1) is no help here at all.

        PRE-REPAIR the legacy temp `uthrow5d_slab_0.npz.<tok>.tmp.npz` satisfies BOTH clauses, so
        this tool would have collected a partial file and then either failed its own `np.load`
        integrity pass or archived it as a "protected slab" -- in a tool whose entire purpose is
        that a byte copy of a corrupt npz is still corrupt. POST-REPAIR `.partial` fails the
        `endswith(".npz")` clause and it is rejected. Measured both ways.
        """
        import protect_throw_slabs

        root = self.work / "protect"
        slabdir = root / "nd-unfolding" / "uq_5d" / "uthrow_slabs_5d"
        slabdir.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(slabdir / "uthrow5d_slab_0.npz"), xs=np.arange(3))

        post = slabdir / U.incomplete_name("uthrow5d_slab_1.npz", "tok")
        post.write_bytes(b"PARTIAL")
        hits = protect_throw_slabs.find_slabs(str(root))
        self.assertEqual([os.path.basename(h) for h in hits], ["uthrow5d_slab_0.npz"],
                         "the post-repair temp must be rejected by this tool's own filter")
        post.unlink()

        legacy = slabdir / f"uthrow5d_slab_1.npz.tok{U.LEGACY_IN_PROGRESS_SUFFIX}"
        legacy.write_bytes(b"PARTIAL")
        legacy_hits = [os.path.basename(h) for h in protect_throw_slabs.find_slabs(str(root))]
        self.assertIn(legacy.name, legacy_hits,
                      "PRECONDITION of the finding: the PRE-REPAIR name satisfies this tool's "
                      "filter, so it would have been collected as a slab worth protecting. If this "
                      "stops being true the finding above is stale and should be re-measured.")
        self.assertTrue(legacy.name.endswith(".npz"))
        self.assertFalse(post.name.endswith(".npz"),
                         "and guarantee (2) -- the suffix, not the dot -- is what excludes the new "
                         "name from a walker")

    def test_PUBLICATION_stays_SAME_DIRECTORY_and_therefore_SAME_DEVICE(self):
        """The review's point 3. `os.replace` is atomic only within one filesystem, so a repair
        that relocated the temp to a sibling temp directory would stop being atomic the moment that
        directory sat on another device -- silently, and only on the machine where it mattered.

        THIS REPAIR RENAMED IN PLACE, so same-device holds BY CONSTRUCTION rather than by policy:
        the temp is created with `dir=os.path.dirname(path)`. Proven rather than argued -- the temp
        path is captured mid-write and both `st_dev` values compared.
        """
        target = self.work / "device"
        target.mkdir(parents=True, exist_ok=True)
        product = target / "block5d_knobs.npz"
        captured = {}
        real_replace = U.os.replace

        def capture(src, dst):
            captured["src"] = src
            captured["dst"] = dst
            captured["src_dev"] = os.stat(src).st_dev
            captured["dir_dev"] = os.stat(os.path.dirname(dst)).st_dev
            return real_replace(src, dst)

        U.os.replace = capture
        try:
            U._atomic_savez(str(product), xs=np.arange(4))
        finally:
            U.os.replace = real_replace

        self.assertEqual(os.path.dirname(captured["src"]), os.path.dirname(captured["dst"]),
                         "the temp must be created in the PRODUCT's own directory")
        self.assertEqual(captured["src_dev"], captured["dir_dev"],
                         "same st_dev: the rename cannot cross a filesystem boundary")
        self.assertEqual(os.stat(product).st_dev, captured["dir_dev"])
        # And the rename really did publish, so this is not a proof about a no-op.
        with np.load(product) as slab:
            np.testing.assert_array_equal(slab["xs"], np.arange(4))

    def test_the_UNCOVERED_producers_are_NAMED_rather_than_left_implicit(self):
        """WHAT THIS REPAIR DOES NOT COVER, asserted so the gap lives in the suite and not only in
        a report.

        `_atomic_savez` derives its temp from `basename(path)`, so the repair covers every stem any
        launcher asks it for -- 4d, 5d and fps alike. But `bootstrap_nd.py` and `seedscan_split.py`
        write `res_boot_*.npz` / `res_split_*.npz` with a BARE `np.savez_compressed(args.out, ...)`:
        no temp, no rename. Their interrupted write lands at the PRODUCT's own name, so it is
        selected by `combine_cov_nd.py --glob` and by `--expected-ids`, which checks identities and
        not integrity. That is STRICTLY WORSE than the defect just repaired, where at least the
        partial file had a temp's name -- and it is outside the authorized scope, because there is
        no temp to rename: it needs atomic publication added, which is a different repair.
        """
        for name in ("bootstrap_nd.py", "seedscan_split.py"):
            src = (ND / name).read_text()
            with self.subTest(producer=name):
                self.assertNotIn("_atomic_savez", src,
                                 f"{name} now routes through the repaired writer -- if that is "
                                 f"deliberate, this exemption should be deleted")
                self.assertIn("np.savez_compressed(a", src,
                              f"{name} is expected to write straight to its --out argument")
                self.assertNotIn("os.replace", src,
                                 f"{name} is expected to have NO atomic publication")

    def test_MUTATION_the_PRE_REPAIR_naming_makes_ARMS_1_AND_2_FAIL(self):
        """POWER for arms 1 and 2. Without this, "an incomplete write is unselectable" is an
        assertion about code nobody has shown can be selectable.

        The two naming constants are set back to the PRE-REPAIR shape -- no leading dot, `.npz`
        suffix -- which is exactly `<product>.<token>.tmp.npz`. `_atomic_savez` reads both at call
        time, so the temp it produces is the old one, and the selection property arms 1 and 2
        assert must then be FALSE.
        """
        target = self.work / "power"
        target.mkdir(parents=True, exist_ok=True)
        saved = (U.INCOMPLETE_PREFIX, U.INCOMPLETE_SUFFIX)
        U.INCOMPLETE_PREFIX, U.INCOMPLETE_SUFFIX = "", ".tmp.npz"
        try:
            # Publication removed so the temp SURVIVES, which is the interrupted-write state.
            real_replace = U.os.replace
            U.os.replace = lambda *a, **k: None
            try:
                U._atomic_savez(str(target / "block5d_knobs.npz"), xs=np.arange(3))
            finally:
                U.os.replace = real_replace
            leftovers = sorted(p.name for p in target.iterdir())
            self.assertEqual(len(leftovers), 1, f"expected one pre-repair temp, got {leftovers}")
            self.assertTrue(leftovers[0].endswith(".tmp.npz"))
            self.assertFalse(leftovers[0].startswith("."))
            # ARM 1's AND ARM 2's CENTRAL PROPERTY, NOW FALSE: the temp IS selected.
            selected = [os.path.basename(q) for q in
                        __import__("glob").glob(str(target / "block5d_*.npz"))]
            self.assertEqual(selected, leftovers,
                             "under the pre-repair naming the incomplete write MUST be selectable "
                             "-- if it is not, arms 1 and 2 are asserting something that was never "
                             "capable of being false and they prove nothing")
            shell = subprocess.run(
                ["bash", "-c", f'cd {target!s} && ls block5d_*.npz 2>/dev/null'],
                capture_output=True, text=True)
            self.assertNotEqual(shell.stdout.strip(), "",
                                "and a shell glob selects it too, which is the form the launchers "
                                "would have used")
        finally:
            U.INCOMPLETE_PREFIX, U.INCOMPLETE_SUFFIX = saved
        # POSITIVE CONTROL ON THE RESTORE: the constants are back, so a fresh write is unselectable
        # again. A mutation harness that leaked its mutation would silently weaken every later test.
        fresh = self.work / "power_restored"
        fresh.mkdir(parents=True, exist_ok=True)
        real_replace = U.os.replace
        U.os.replace = lambda *a, **k: None
        try:
            U._atomic_savez(str(fresh / "block5d_knobs.npz"), xs=np.arange(3))
        finally:
            U.os.replace = real_replace
        self.assertEqual(__import__("glob").glob(str(fresh / "block5d_*.npz")), [])

    def test_the_LAUNCHERS_wall_kill_CLAIM_is_now_true_in_the_part_it_asserts(self):
        """`sbatch_uthrow_run_5d_fast.sh:14`: *"Atomic-save (os.replace) means a wall-kill re-runs
        the whole task cleanly."* The coordinator asked whether the repair makes that true. Each
        clause is checked rather than argued, and the one that is still false is named.

        TRUE (1): the product is never partial -- one `os.replace` in the destination directory.
        TRUE (2): an incomplete write is never SELECTED. This clause is what the repair bought; it
                  was FALSE before, and the claim asserted it without warrant.
        TRUE (3): a re-run reproduces the full slab, because `do_throws` rewrites the WHOLE slab on
                  every throw (`:594-596`), so a short slab is overwritten rather than merged.
        FALSE (4): "cleanly" does not extend to litter. SIGKILL runs no handler, so one temp
                  survives per kill, and the repair made it invisible to `ls *.npz`. Measured
                  sizes: a throw slab is 372 086 B and a block slab 464 850 B on the cluster, so
                  the litter is sub-MB per kill -- real, small, and findable only by
                  `find_incomplete_writes`.
        """
        target = self.work / "claim"
        target.mkdir(parents=True, exist_ok=True)
        product = target / "uthrow5d_slab_0.npz"

        # (3) A SHORT SLAB IS OVERWRITTEN, NOT MERGED. Two throws, then the full four.
        U._atomic_savez(str(product), xs=np.zeros((2, NBIN)), throws=np.arange(2))
        U._atomic_savez(str(product), xs=np.ones((4, NBIN)), throws=np.arange(4))
        with np.load(product) as slab:
            self.assertEqual(slab["throws"].tolist(), [0, 1, 2, 3],
                             "a re-run must REPLACE the short slab, not append to it")

        # (1) + (2) after an interrupted write beside an already-published product.
        orphan = target / U.incomplete_name("uthrow5d_slab_0.npz", "killed")
        orphan.write_bytes(b"PARTIAL")
        with np.load(product) as slab:
            self.assertEqual(slab["throws"].tolist(), [0, 1, 2, 3],
                             "(1) the published product is untouched by the interrupted write")
        selected = [os.path.basename(q) for q in
                    __import__("glob").glob(str(target / "uthrow5d_slab_*.npz"))]
        self.assertEqual(selected, ["uthrow5d_slab_0.npz"],
                         "(2) only the product is selected; the orphan is not")

        # (4) THE CLAUSE THAT IS STILL FALSE, asserted so the residual cannot be forgotten.
        self.assertTrue(orphan.exists(),
                        "(4) nothing removes the orphan -- 'cleanly' does not cover litter")
        listing = subprocess.run(["bash", "-c", f'cd {target!s} && ls'],
                                 capture_output=True, text=True)
        self.assertNotIn(orphan.name, listing.stdout,
                         "(4) and the repair made it invisible to a plain `ls`, which is a real "
                         "downside of the repair and the reason the directed scan exists")
        self.assertEqual(U.find_incomplete_writes(target), [orphan.name],
                         "the directed scan is the only thing that finds it")

    def test_MUTATION_breaking_publication_is_caught_by_the_completion_arm(self):
        """POWER for arm 3. Without this, "publication still works" is an assertion about code
        nobody has shown can fail this way.

        `os.replace` is neutralized, which is exactly the shape of a repair that makes incomplete
        writes unselectable by never publishing. Arm 3's three properties -- product present,
        no leftover, product selected -- must all fail.
        """
        target = self.work / "mut"
        target.mkdir(parents=True, exist_ok=True)
        product = target / "block5d_knobs.npz"
        real_replace = U.os.replace
        U.os.replace = lambda *a, **k: None          # publication removed, write still happens
        try:
            U._atomic_savez(str(product), xs=np.arange(5))
        finally:
            U.os.replace = real_replace
        self.assertFalse(product.exists(),
                         "the mutation must reach publication: no product may appear")
        self.assertEqual(len(U.find_incomplete_writes(target)), 1,
                         "and the temp must survive, which is what arm 3's leftover check sees")
        self.assertEqual(__import__("glob").glob(str(target / "block5d_*.npz")), [],
                         "nothing is selectable, so arm 3's selection check fails too -- three "
                         "independent properties of arm 3 all break under this mutation")

    def test_the_FRESHNESS_check_does_not_read_a_temp_as_a_product(self):
        """The other side of the same hazard, and the direction that refuses a CORRECT run.

        The suffix is imported from the producer in both places, so the two cannot drift apart.
        """
        plan = ZP.namespace_plan(str(self.work / "fresh"), namespace="ns")
        target = Path(plan["arms"]["block"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        (target / f"block5d_knobs.npz.abc{U.LEGACY_IN_PROGRESS_SUFFIX}").write_bytes(b"partial")
        self.assertTrue(ZP.check_namespace_fresh(plan, ["block"])["fresh"],
                        "an interrupted write is not a product and must not refuse a fresh "
                        "namespace")
        (target / "block5d_knobs.npz").write_bytes(b"real")
        with self.assertRaises(ZP.PrecursorError):
            ZP.check_namespace_fresh(plan, ["block"])

    def test_declaring_a_block_population_without_a_block_glob_refuses(self):
        with self.assertRaises(SystemExit) as caught:
            args = combine_args(bank=str(self.bank.path), combine=self.throw_glob,
                                block_slabs=None, expected_throws="0-7",
                                expected_block_files="block5d_knobs.npz")
            U.do_combine(args)
        self.assertIn("names no glob", str(caught.exception))


# ============================================= (c) ONE explicit namespace, freshness a REFUSAL ===
class TheNamespaceIsOneExplicitValueAndFreshnessRefuses(unittest.TestCase):
    """(c) The block arm writes `_sb` or not depending on `mr_declared`, the combine reads `_sb`
    unconditionally, and `mr_dir_prefix` returns its argument unchanged when undeclared. Measured on
    the cluster: `block_slabs_5d` holds 8 products and `block_slabs_5d_sb` holds 36, from separate
    campaigns, so an undeclared precursor would consume 36 foreign files -- and the glob MATCHES, so
    it does not fail closed.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.work = Path(self._tmp.name)

    def test_an_UNSET_namespace_refuses_rather_than_defaulting(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.resolve_namespace({})
        self.assertIn("NO DEFAULT", str(caught.exception))

    def test_a_MALFORMED_namespace_refuses_rather_than_normalizing(self):
        for bad in ("a/b", "..", ".", "", "  ", " ns", "ns ", "../escape", "/abs", "-lead"):
            with self.subTest(value=bad):
                with self.assertRaises(ZP.PrecursorError):
                    ZP.resolve_namespace({ZP.NAMESPACE_ENV: bad})

    def test_POSITIVE_CONTROL_a_well_formed_namespace_resolves(self):
        for good in ("zprec_20260911", "ns", "z-prec.1", "A0"):
            with self.subTest(value=good):
                self.assertEqual(ZP.resolve_namespace({ZP.NAMESPACE_ENV: good}), good)

    def test_ALL_FOUR_ARMS_resolve_under_the_SAME_namespace_segment(self):
        """The mismatch closed: one value, four directories, one parent. Before this, the block
        arm's parent and the combine's parent could differ by the `_sb` suffix."""
        plan = ZP.namespace_plan(str(self.work), namespace="ns")
        self.assertEqual(sorted(plan["arms"]), ["block", "combine", "dump", "run"])
        parents = set()
        for arm, entry in plan["arms"].items():
            directory = Path(entry["dir"])
            parents.add(directory if arm == "combine" else directory.parent)
        self.assertEqual(len(parents), 1, f"the arms do not share one namespace root: {parents}")
        self.assertEqual(next(iter(parents)).name, "ns")

    def test_an_ABSENT_or_EMPTY_directory_is_FRESH(self):
        plan = ZP.namespace_plan(str(self.work), namespace="ns")
        self.assertTrue(ZP.check_namespace_fresh(plan)["fresh"])
        for entry in plan["arms"].values():
            Path(entry["dir"]).mkdir(parents=True, exist_ok=True)
        self.assertTrue(ZP.check_namespace_fresh(plan)["fresh"])

    def test_a_NON_EMPTY_namespace_REFUSES_and_names_the_arm(self):
        plan = ZP.namespace_plan(str(self.work), namespace="ns")
        target = Path(plan["arms"]["run"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        (target / "uthrow5d_slab_0.npz").write_bytes(b"x")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_namespace_fresh(plan)
        self.assertIn("NOT FRESH", str(caught.exception))
        self.assertIn("run:", str(caught.exception))
        self.assertIn("uthrow5d_slab_0.npz", str(caught.exception))

    def test_POSITIVE_CONTROL_a_NON_PRODUCT_file_does_not_trip_freshness(self):
        """A guard that fires on every correct run is not a guard, and the benign names here are
        MEASURED rather than invented.

        The live `uq_5d/block_slabs_5d` holds 18 directory entries but only 8 products: the other
        10 are `knob_<band>.log`. So an `os.listdir`-based emptiness test would call that namespace
        occupied 10 times over for reasons that have nothing to do with products, and `.log` files
        beside a product directory are the normal state of these arms. `_atomic_savez` also leaves
        a `*.tmp.npz` on an interrupted rename.

        ⚠ AND COUNTING THE WRONG POPULATION IS HOW I FIRST MIS-READ THIS. `ls -1 | wc -l` on those
        four archive directories gave 18/41/320/40 against the 8/36/160/40 that the product globs
        give. Same directories, different denominators, and only the second pair is a statement
        about products.
        """
        plan = ZP.namespace_plan(str(self.work), namespace="ns")
        target = Path(plan["arms"]["block"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        for benign in ("knob_2p2h.log", "knob_MaCCQE.log", ".gitkeep",
                       "block5d_flux_1.npz.abc.tmp.npz"):
            (target / benign).write_text("x")
        self.assertTrue(ZP.check_namespace_fresh(plan)["fresh"],
                        "ten .log files and an interrupted-rename temp are not products")
        (target / "block5d_knobs.npz").write_bytes(b"x")
        with self.assertRaises(ZP.PrecursorError):
            ZP.check_namespace_fresh(plan, ["block"])

    def test_the_freshness_sweep_covers_ALL_arms_by_DEFAULT(self):
        """`arms=None` means all four. A per-arm opt-in would let a caller shrink the sweep to the
        arms it already believes are fresh, which is the covering-search failure."""
        plan = ZP.namespace_plan(str(self.work), namespace="ns")
        for arm in plan["arms"]:
            with self.subTest(occupied=arm):
                fresh = ZP.namespace_plan(str(self.work / arm), namespace="ns")
                target = Path(fresh["arms"][arm]["dir"])
                target.mkdir(parents=True, exist_ok=True)
                name = fresh["arms"][arm]["glob"].replace("*", "x").replace("[yz]", "z")
                (target / name).write_bytes(b"x")
                with self.assertRaises(ZP.PrecursorError):
                    ZP.check_namespace_fresh(fresh)
        with self.assertRaises(ZP.PrecursorError):
            ZP.check_namespace_fresh(plan, [])

    def test_the_RESIDUAL_is_MARKED_ON_THE_LAUNCHER_ITSELF(self):
        """The independent review's one condition, and its reasoning is the part that matters:
        *"the general launcher's next user is precisely the reader who will not have read this
        review."* A lane record cannot reach that reader; a notice in the file can.

        Asserted ABOVE the branch it warns about, because a warning a reader meets after the code
        it describes is not a warning.
        """
        text = LAUNCHER["block"].read_text()
        lines = text.split("\n")
        for required in ("**CITABLE FOR:**", "**NOT CITABLE FOR:**",
                         "**Owner of the DEFECT:**", "**Owner of this RECORD:**"):
            with self.subTest(field=required):
                self.assertIn(required, text, f"the residual notice lacks {required}")
        notice = next(i for i, line in enumerate(lines) if "**CITABLE FOR:**" in line)
        branch = next(i for i, line in enumerate(lines)
                      if line.startswith('if [[ -n "${MNV_Z_PRECURSOR_NS:-}" ]]'))
        undeclared = next(i for i, line in enumerate(lines)
                          if line.strip() == 'BLOCK_DIR="uq_5d/block_slabs_5d"')
        self.assertLess(notice, branch,
                        "the notice must sit ABOVE the namespace branch, not below it")
        self.assertLess(notice, undeclared)
        # BOTH NAMESPACES NAMED, and the direction of the mismatch stated -- a notice that said
        # only "there is a mismatch" would leave the reader to work out which way it runs.
        for fact in ("block_slabs_5d_sb", "sbatch_uthrow_combine_5d_fast.sh",
                     "does not take this branch", "did NOT grant"):
            with self.subTest(fact=fact):
                self.assertIn(fact, text)

    def test_the_RESIDUALS_REASON_is_the_SURVIVING_one_not_the_WITHDRAWN_one(self):
        """A DIRECTION INVERSION, and the withdrawn form sat 317 lines above its own correction --
        inside the section my marker tells the reader to read FIRST.

        `:350-353` withdraws the reason "repointing would change where an ARCHIVE reproduction
        writes": the archive IS `_sb`, so repointing points an UNDECLARED writer INTO it. The two
        directions license different repairs -- under the withdrawn one the prudent act is to leave
        the literal alone; under the surviving one, pointing the undeclared path at a THIRD
        namespace would also satisfy the constraint. So this is not a wording quibble, and a
        reader who stops at the top section must not be handed the weaker sentence.

        The file states the withdrawal, so the withdrawn phrasing legitimately APPEARS. What must
        not happen is for it to appear as a live reason. Checked positionally: every occurrence of
        the withdrawn phrasing must be accompanied, in its own paragraph, by the correction.
        """
        raw = LAUNCHER["block"].read_text()
        # PARAGRAPHS, NOT LINES. My own rewrite wrapped the withdrawn phrase across two comment
        # lines, so a per-line search found nothing and this test reported the phrase "deleted".
        # A guard that stops matching because the text reflowed is a guard that silently switches
        # off -- the same failure as a comment-marker excision that stops locating its subject.
        paragraphs = [" ".join(chunk.replace("#", " ").split())
                      for chunk in re.split(r"\n#\s*\n", raw)]
        needle = "change where an ARCHIVE reproduction"
        hits = [q for q in paragraphs if needle in q]
        self.assertTrue(hits, "the withdrawn phrasing is not where this test looks; if it has been "
                              "deleted outright, delete this test with it")
        for hit in hits:
            with self.subTest(paragraph=hit[:70]):
                self.assertTrue("archive IS `_sb`" in hit or "archive IS _sb" in hit,
                                f"this paragraph states the withdrawn reason with no correction in "
                                f"the same paragraph. A reader stopping there concludes the archive "
                                f"sits at the current literal and the prudent act is to leave it "
                                f"alone -- the opposite of the surviving constraint, which is that "
                                f"`_sb` needs protecting FROM undeclared writers. Paragraph: {hit}")
        lines = raw.split("\n")
        # THE SURVIVING REASON IS IN THE TOP SECTION, which is the review's actual requirement.
        fence = [i for i, line in enumerate(lines) if line.startswith("# ===========")]
        top = "\n".join(lines[fence[0]: fence[-1] + 1])
        # CASE-NORMALIZED, and this is the FOURTH time an assertion string of mine drifted from the
        # prose it checks ("the archive" against "The archive"). A literal match over hand-written
        # English is a brittle operand; normalizing removes the class of failure rather than fixing
        # this instance of it.
        top_norm = " ".join(top.replace("#", " ").split()).lower()
        for required in ("archive is `_sb`", "write into the",
                         "protecting from undeclared writers"):
            with self.subTest(required=required):
                self.assertIn(required, top_norm,
                              "the top section must state the SURVIVING reason, because that is "
                              "the section the marker sends the reader to first")

    def test_the_UNRECONCILED_124_is_NAMED_rather_than_repeated(self):
        """A figure doing rhetorical work without a denominator. Pre-existing at `:352-353`; what
        would have been mine is repeating it.

        Measured 2026-09-11: `block_slabs_5d_sb` 36 + `uthrow_slabs_5d_sb` 40 = 76, and all seven
        `uq_5d/*slab*` directories hold 271. No measured population equals 124.
        """
        text = LAUNCHER["block"].read_text()
        self.assertIn("does not reconcile", text.lower().replace("DOES NOT RECONCILE".lower(),
                                                                 "does not reconcile"),
                      "the figure must be named as unreconciled where a reader meets it")
        for measured in ("36", "40", "76", "271"):
            with self.subTest(figure=measured):
                self.assertIn(measured, text,
                              "the reconciliation must show its own populations, or it is one "
                              "unexplained number replaced by another")

    def test_the_RESIDUAL_notices_LINE_CITATIONS_still_point_at_what_they_claim(self):
        """A line citation in a comment is the most fragile receipt there is: the next edit above it
        silently repoints it. So each one is resolved and compared against what the notice says is
        there. This exists because I got all four wrong on the first write -- inserting the notice
        shifted every line it cited."""
        lines = LAUNCHER["block"].read_text().split("\n")
        # FIRST TO LAST FENCE, not "the two fences": the notice's title is UNDERLINED, so there are
        # three. My first version asserted exactly two and failed on my own formatting -- a test
        # wrong about its own operand, which is the shape this file keeps finding elsewhere.
        fence = [i for i, line in enumerate(lines) if line.startswith("# ===========")]
        self.assertGreaterEqual(len(fence), 2, "the notice's fence lines are not where this looks")
        block = lines[fence[0]: fence[-1] + 1]

        # Citations of THIS file only. A reference like `lib_member_resume.sh:145-149` names another
        # file and must not be resolved against these line numbers -- that would be the
        # right-check-wrong-operand shape, and it is why the filename-qualified form is excluded.
        cited = set()
        for line in block:
            for match in re.finditer(r"(\S*):(\d+)", line):
                if not match.group(1).endswith((".sh", ".py")):
                    cited.add(int(match.group(2)))
        self.assertTrue(cited, "the notice cites no line of this file at all")

        for code, what in (('if [[ -n "${MNV_Z_PRECURSOR_NS:-}" ]]; then', "the namespace branch"),
                           ('BLOCK_DIR="uq_5d/block_slabs_5d"', "the undeclared literal")):
            target = next(i + 1 for i, line in enumerate(lines) if line.strip() == code)
            with self.subTest(cites=what):
                self.assertIn(target, cited,
                              f"no citation in the notice resolves to line {target}, which is "
                              f"where {what} ({code!r}) actually is. A citation that has drifted "
                              f"points a reader at an unrelated line and reads exactly like a "
                              f"correct one.")

    def test_the_CONTRACT_ADDS_NO_python3_LINE_TO_ANY_LAUNCHER(self):
        """RULING 21, AND MY FIRST IMPLEMENTATION VIOLATED IT FIFTEEN TIMES.

        I had each arm run `python3 z_precursor.py require-fresh` and siblings before the science
        invocation. `mnv_preflight_census.py` classifies every non-comment `python3` line as
        guarded / declared-preflight / interpreter-probe / UNCLASSIFIED, pins unclassified at ZERO,
        and refused. Neither escape was open: `z_precursor` fails exclusion criterion (5) because
        it imports `unified_throw_cov` by design, and guarding the calls moves `guarded` off 14 --
        ruling 21's pin and reserved for Joseph. So the contract travels as a FLAG on a call that
        was already guarded.
        """
        for arm, path in LAUNCHER.items():
            with self.subTest(arm=arm):
                live = [line for line in path.read_text().split("\n")
                        if "python3" in line and not line.lstrip().startswith("#")]
                offenders = [line.strip() for line in live if "z_precursor" in line]
                self.assertEqual(offenders, [],
                                 f"{path.name} invokes z_precursor.py as a process: {offenders}")
                self.assertTrue(any("--z-namespace-arm" in line for line in path.read_text()
                                    .split("\n")),
                                f"{path.name} must carry the contract as a producer FLAG instead")

    def test_the_PREFLIGHT_CENSUS_itself_is_CLEAN_on_this_tree(self):
        """The instrument that caught it, run rather than cited. `unclassified == 0` and
        `guarded == 14` are the two numbers that matter, and the second is ruling 21's pin."""
        census = ND / "mnv_preflight_census.py"
        decl = ND / "mnv_preflight_exclusions.json"
        self.assertTrue(census.exists() and decl.exists())
        out = subprocess.run([sys.executable, str(census), "--declaration", str(decl)],
                             capture_output=True, text=True, cwd=str(ND))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("0 unclassified", out.stdout)
        self.assertIn("14 guarded", out.stdout)
        self.assertIn("boundary (guarded + declared-preflight) = 38", out.stdout)

    def test_the_SHELL_path_expression_is_VERIFIED_against_the_python_layout(self):
        """Two spellings of one layout, and the disagreement REFUSES rather than one winning.

        The launcher builds `uq_5d/${MNV_Z_PRECURSOR_NS}/<subdir>` in shell because getting it out
        of Python would need the very invocation ruling 21 forbids. So it is checked.
        """
        env = {ZP.NAMESPACE_ENV: "ns"}
        saved = dict(os.environ)
        os.environ.update(env)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved)))
        good = ZP.arm_directory(str(self.work), "ns", "block")
        contract = ZP.enforce_namespace_contract("block", str(self.work), good)
        self.assertEqual(contract["dir"], good)
        for wrong in (str(self.work / "nd-unfolding" / "uq_5d" / "ns" / "block_slabs_5d_sb"),
                      str(self.work / "nd-unfolding" / "uq_5d" / "block_slabs_5d"),
                      str(self.work / "nd-unfolding" / "uq_5d" / "other" / "block_slabs_5d")):
            with self.subTest(declared=wrong):
                with self.assertRaises(ZP.PrecursorError) as caught:
                    ZP.enforce_namespace_contract("block", str(self.work), wrong)
                self.assertIn("diverged", str(caught.exception))

    def test_the_CONTRACT_IS_INERT_when_the_namespace_is_unset(self):
        """The preservation instruction, asserted: every archive reproduction path is untouched."""
        saved = os.environ.pop(ZP.NAMESPACE_ENV, None)
        self.addCleanup(lambda: os.environ.update({ZP.NAMESPACE_ENV: saved}) if saved else None)
        self.assertIsNone(ZP.enforce_namespace_contract("block", "/anything", "/whatever"),
                          "with the namespace unset the contract must do NOTHING, not refuse")

    def test_the_MEMBER_AXIS_is_a_REFUSAL_not_an_assumption(self):
        """`lib_member_resume.sh:230`'s `mr_declared` is a PRESENCE test, so `0` DECLARES the member
        axis. Nothing landing in `mii/` held only because nobody exported the variable."""
        self.assertTrue(ZP.check_no_member_axis({})["ok"])
        for value in ("0", "1200", "", "-1200"):
            with self.subTest(value=value):
                with self.assertRaises(ZP.PrecursorError) as caught:
                    ZP.check_no_member_axis({ZP.MEMBER_OFFSET_ENV: value})
                self.assertIn("mii/member_kNNNNNN", str(caught.exception))

    def test_the_member_presence_test_matches_the_SHELL_predicate_it_mirrors(self):
        """A fixture agreeing with my code rather than with the world would be worthless here, so
        the shell library's own `mr_declared` is executed and compared."""
        library = ND / "lib_member_resume.sh"
        self.assertTrue(library.exists())
        for value, expected_declared in (("0", True), ("1200", True), ("", False)):
            with self.subTest(value=value):
                script = (f'source "{library}" 2>/dev/null; export MNV_EST_SEED_OFFSET="{value}"; '
                          f'if mr_declared; then echo DECLARED; else echo UNDECLARED; fi')
                out = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
                self.assertEqual(out.stdout.strip() == "DECLARED", expected_declared,
                                 f"shell says {out.stdout.strip()!r} for {value!r}")


# ====================================== (d') the declarations are DERIVED from the launchers =====
class TheDeclarationsAreDerivedFromEachArmsOwnSbatchLines(unittest.TestCase):
    """A range literal in the checker would be a second implementation of the arm's layout."""

    EXPECTED = {"dump": ("uthrow5d_dump", 8, 6.0), "block": ("uthrow5d_block", 21, 12.0),
                "run": ("uthrow5d_runF", 40, 6.0), "combine": ("uthrow5d_combF", 1, 3.0)}

    def test_every_arm_parses_to_its_declared_population_and_ceiling(self):
        for arm, (name, tasks, hours) in self.EXPECTED.items():
            with self.subTest(arm=arm):
                info = ZP.parse_sbatch_arm(LAUNCHER[arm])
                self.assertEqual(info["job_name"], name)
                self.assertEqual(info["n_tasks"], tasks)
                self.assertEqual(info["time_limit_hours"], hours)

    def test_the_THROTTLE_is_stripped_from_the_population(self):
        """`0-39%40` is forty tasks. Reading `%40` as a population is the `sacct` bracket error one
        level up, and the bracket errs in BOTH directions."""
        self.assertEqual(ZP._parse_array_spec("0-39%40"), list(range(40)))
        self.assertEqual(ZP._parse_array_spec("0-20%10"), list(range(21)))
        self.assertEqual(ZP._parse_array_spec("0-7"), list(range(8)))
        self.assertEqual(ZP._parse_array_spec("1,3,5"), [1, 3, 5])

    def test_PINNED_BY_PATH_the_sibling_run_launcher_is_a_DIFFERENT_ARM(self):
        """`sbatch_uthrow_run_5d.sh` declares `0-19%10` / `12:00:00` while the fast one declares
        `0-39%40` / `06:00:00`. A stem-based lookup would answer correctly about the wrong arm."""
        fast = ZP.parse_sbatch_arm(ND / "sbatch_uthrow_run_5d_fast.sh")
        slow = ZP.parse_sbatch_arm(ND / "sbatch_uthrow_run_5d.sh")
        self.assertNotEqual(fast["n_tasks"], slow["n_tasks"])
        self.assertNotEqual(fast["time_limit_hours"], slow["time_limit_hours"])
        self.assertEqual((slow["n_tasks"], slow["time_limit_hours"]), (20, 12.0))

    def test_the_derived_file_names_match_the_launchers_own_write_expressions(self):
        """The names are compared against the `--out` expressions IN the launcher text, so the
        derivation is checked against the producer rather than against my own template."""
        block = ZP.declare_arm_files("block", LAUNCHER["block"])
        self.assertEqual(block[0], "block5d_knobs.npz")
        self.assertEqual(len(block), 21)
        text = LAUNCHER["block"].read_text()
        self.assertIn('block5d_knobs.npz', text)
        self.assertIn('block5d_flux_${T}.npz', text)
        run = ZP.declare_arm_files("run", LAUNCHER["run"])
        self.assertEqual(len(run), 40)
        self.assertIn('uthrow5d_slab_${SLURM_ARRAY_TASK_ID}.npz', LAUNCHER["run"].read_text())

    def test_an_arm_with_NO_per_task_layout_refuses_to_invent_one(self):
        for arm in ("dump", "combine"):
            with self.subTest(arm=arm):
                with self.assertRaises(ZP.PrecursorError) as caught:
                    ZP.declare_arm_files(arm, LAUNCHER[arm])
                self.assertIn("no per-task file layout", str(caught.exception))

    def test_a_launcher_with_no_TIME_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "no_time.sh"
            path.write_text("#!/bin/bash\n#SBATCH --job-name=x\n#SBATCH --array=0-3\n")
            with self.assertRaises(ZP.PrecursorError) as caught:
                ZP.parse_sbatch_arm(path)
            self.assertIn("UNBOUNDED", str(caught.exception))


# ================================= (e) guarded import provenance for the DUMP producer ===========
class TheDumpArmNoLongerImportsFromAHardcodedTree(unittest.TestCase):
    """(e) `sbatch_uthrow_dump_5d.sh` hardcoded `REPO=/pscratch/...`, `cd`-ed there and ran a bare
    `python3 unified_throw.py`, so `sys.path[0]` was that tree whatever `MNV_CODE_ROOT` said.

    That is OI-136 reached by `cd` rather than by a Python insert, which is exactly why the sweep
    that repaired inserts missed it: there was no insert to find.
    """

    def setUp(self):
        self.text = LAUNCHER["dump"].read_text()
        self.code_lines = [line for line in self.text.split("\n")
                           if line.strip() and not line.lstrip().startswith("#")]

    def test_the_hardcoded_cluster_root_is_gone_ENTIRELY(self):
        """⚠ AND IT MUST NOT SURVIVE IN A COMMENT EITHER, which is where my first version put it.

        `test_k0_launcher_two_roots.test_no_launcher_still_assigns_the_cluster_root_unconditionally`
        checks the whole TEXT, not just code lines, so quoting the removed assignment verbatim in
        the header tripped it. That test's operand is deliberately the text: the other eight
        launchers all write the removed line with a `<the canonical checkout>` PLACEHOLDER for
        exactly this reason, and this one now follows the same convention rather than the other
        lane's assertion being relaxed to accommodate it.
        """
        cluster = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))
        self.assertNotIn(f'REPO="{cluster}"', self.text)
        self.assertEqual([line for line in self.code_lines if cluster in line], [])
        self.assertIn("<the canonical checkout>", self.text,
                      "the removed line must still be RECORDED, in the placeholder form the other "
                      "eight use; a repair with no record of its subject is unreviewable")

    def test_the_repair_is_recorded_in_terms_of_the_DEFECT_it_closes(self):
        for phrase in ("OI-136", "sys.path[0]", "cd", "PYTHONPATH", "MNV_DATA_ROOT"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_BOTH_roots_are_mandatory_with_no_default(self):
        for var in ("MNV_CODE_ROOT", "MNV_DATA_ROOT", "MNV_ENV_ROOT"):
            with self.subTest(var=var):
                self.assertIn(f"${{{var}:?", self.text,
                              f"{var} must be mandatory (`:?`), not defaulted (`:-`)")
        self.assertNotIn("MNV_CODE_ROOT:-", self.text)
        self.assertNotIn("MNV_DATA_ROOT:-", self.text)

    def test_the_producer_runs_THROUGH_the_guard_with_an_inventory(self):
        self.assertIn('python3 "$GUARD" --expect-root "$CODE_ROOT"', self.text)
        self.assertIn('--inventory "$(mnv_inv uthrow_dump)"', self.text)
        self.assertIn('"${CODE_ROOT}/nd-unfolding/unified_throw.py"', self.text)

    def test_the_bare_invocation_and_the_cd_into_the_code_tree_are_gone(self):
        """⚠ THE OPERAND IS A WORKING-DIRECTORY CHANGE, NOT THE STRING `cd`.

        My first version of this arm banned `cd "${CODE_ROOT}/nd-unfolding"` anywhere in a code
        line and failed on `:322` -- the member-axis containment check, which is
        `$(cd ... && pwd -P)` inside a SUBSHELL and resolves a path rather than moving the
        process. A right check over the wrong object. So subshell substitutions are stripped
        first, and what is banned is a `cd` that actually changes where the interpreter starts.
        """
        stripped = [re.sub(r"\$\([^)]*\)", "<subshell>", line) for line in self.code_lines]
        for banned in ("python3 unified_throw.py", 'cd "${REPO}', 'cd "${CODE_ROOT}'):
            with self.subTest(pattern=banned):
                offenders = [line for line in stripped if banned in line]
                self.assertEqual(offenders, [], f"{banned!r} survives in code: {offenders}")
        self.assertTrue(any('cd "${DATA_ROOT}/nd-unfolding"' in line for line in stripped),
                        "POSITIVE CONTROL: the arm must still cd into the DATA root, so this "
                        "sweep is shown to be looking at lines that contain a real `cd`")

    def test_the_inputs_come_from_the_DATA_root(self):
        """`unified_throw_cov.py:63-68` justifies its gigabyte gitignored defaults on the ground
        that every k=0 launcher passes them explicitly from `${MNV_DATA_ROOT}`. This arm had ZERO
        such references, so that justification was false of it."""
        self.assertGreaterEqual(sum("${DATA_ROOT}" in line for line in self.code_lines), 2)
        self.assertIn('--omnifile "${DATA_ROOT}/nd-unfolding/'
                      'runEventLoopOmniFold_5D_MEFHC_universes_full.root"', self.text)

    def test_POWER_the_PRE_FIX_launcher_would_FAIL_these_assertions(self):
        """Reconstructed literally, from the six lines the header records, so the arms above are
        shown to be capable of failing rather than asserted to be."""
        cluster = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))
        prefix = "\n".join([
            "#!/bin/bash",
            "#SBATCH --job-name=uthrow5d_dump",
            "#SBATCH --array=0-7",
            "#SBATCH --time=06:00:00",
            "set -eo pipefail",
            f'REPO="{cluster}"; source "${{REPO}}/setup_salloc_env.sh"',
            'export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"',
            "python3 unified_throw.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 8 \\",
            '  --omnifile "${REPO}/nd-unfolding/x.root" --axes eavail,q3,W \\',
            '  --bankdir "${REPO}/nd-unfolding/bank_uthrow_5d"',
        ])
        lines = [line for line in prefix.split("\n")
                 if line.strip() and not line.lstrip().startswith("#")]
        self.assertTrue(any(cluster in line for line in lines),
                        "the reconstruction must carry the defect it stands for")
        self.assertNotIn("${MNV_CODE_ROOT:?", prefix)
        self.assertNotIn('python3 "$GUARD"', prefix)
        self.assertTrue(any("python3 unified_throw.py" in line for line in lines))
        self.assertEqual(sum("${DATA_ROOT}" in line for line in lines), 0)

    def test_the_cd_MECHANISM_is_demonstrated_in_a_CHILD_PROCESS(self):
        """The hazard itself, run rather than described: `python3 script.py` from a directory puts
        THAT DIRECTORY at `sys.path[0]`, so a same-named module there shadows the real one.

        A subprocess is the only honest fixture for this -- `sys.path[0]` is decided at interpreter
        start, so nothing in-process can reproduce it. The fixture's SUBSTRATE is the impossibility.
        """
        with tempfile.TemporaryDirectory() as td:
            wrong = Path(td) / "wrong-tree"
            right = Path(td) / "right-tree"
            for tree, mark in ((wrong, "WRONG"), (right, "RIGHT")):
                tree.mkdir()
                (tree / "shadowed_module.py").write_text(f"MARK = {mark!r}\n")
            entry = right / "entry.py"
            entry.write_text("import shadowed_module\nprint(shadowed_module.MARK)\n")
            env = dict(os.environ, PYTHONPATH=str(right))
            # (1) the DEFECT: cd into the wrong tree, run a bare relative script name.
            import shutil
            shutil.copy2(entry, wrong / "entry.py")
            bad = subprocess.run([sys.executable, "entry.py"], cwd=str(wrong), env=env,
                                 capture_output=True, text=True)
            self.assertEqual(bad.stdout.strip(), "WRONG",
                             "the cd-ed directory must win; if it did not, this hazard is not "
                             "real and the repair above is unnecessary")
            # (2) PYTHONPATH CANNOT OUTRANK POSITION 0, which is the half a re-deploy cannot fix.
            self.assertEqual(env["PYTHONPATH"], str(right))
            # (3) the REPAIRED shape: name the entrypoint by its approved-tree path.
            good = subprocess.run([sys.executable, str(entry)], cwd=str(wrong), env=env,
                                  capture_output=True, text=True)
            self.assertEqual(good.stdout.strip(), "RIGHT",
                             "naming the entrypoint by its CODE_ROOT path is what moves "
                             "sys.path[0] to the approved tree")

    def test_the_dump_arm_is_IN_the_two_roots_test_population(self):
        """A ninth copy of the preamble with nothing asserting it had not drifted would be worse
        than none. Every byte-identity assertion there quantifies over `LAUNCHERS`."""
        import test_k0_launcher_two_roots as K0
        names = [sh for sh, _e, _t in K0.LAUNCHERS]
        self.assertIn("sbatch_uthrow_dump_5d.sh", names)
        self.assertIn("uthrow_dump", K0.ALL_TAGS)


# ======================================================== (f) the receipt is written LAST ========
class TheReceiptIsWrittenAfterTheProduct(unittest.TestCase):
    """(f) These arms have no receipt. Their provenance is in-product (`TParameter`s,
    `_atomic_savez`), which is good provenance and is NOT a receipt: it cannot say the product was
    completed, nor by which run. A receipt written beside its product records an intention.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.work = Path(self._tmp.name)
        self.bank = SyntheticBank(self.work)
        self.product = self.work / "unified_throw_cov_5d.root"
        self.product.write_bytes(b"root" + b"\x00" * 200)
        self.out = self.work / "receipt.json"

    def _write(self, **kw):
        return ZP.write_receipt(product=str(self.product), out_path=str(self.out), arm="combine",
                                namespace="ns", extra=ZP.producer_provenance(
                                    bank=str(self.bank.path),
                                    population_declared="throw,block"), **kw)

    def test_POSITIVE_CONTROL_a_healthy_product_gets_a_receipt_that_GATES_CLEAN(self):
        receipt = self._write()
        self.assertTrue(self.out.exists())
        self.assertEqual(receipt["product"]["sha256"], ZP.sha256_file(str(self.product)))
        self.assertTrue(ZP.check_receipt(str(self.out))["ok"])

    def test_an_ABSENT_product_refuses_and_writes_NOTHING(self):
        self.product.unlink()
        with self.assertRaises(ZP.PrecursorError) as caught:
            self._write()
        self.assertIn("does not exist", str(caught.exception))
        self.assertFalse(self.out.exists(),
                         "a refused receipt must leave no file: a half-written record is the "
                         "artifact this ordering exists to prevent")

    def test_a_ZERO_BYTE_product_refuses(self):
        self.product.write_bytes(b"")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self._write()
        self.assertIn("zero bytes", str(caught.exception))
        self.assertFalse(self.out.exists())

    def test_a_product_that_EXISTS_but_does_NOT_OPEN_refuses(self):
        """Existence is not completion. A `TFile` is finalized by `Close()`, and a truncated npz
        has a size."""
        cases = {
            "root magic absent": b"NOTR" + b"\x00" * 200,
            "root header only": b"root" + b"\x00" * 10,
        }
        for label, payload in cases.items():
            with self.subTest(case=label):
                self.product.write_bytes(payload)
                with self.assertRaises(ZP.PrecursorError):
                    self._write()
                self.assertFalse(self.out.exists())
        truncated = self.work / "slab.npz"
        good = self.work / "good.npz"
        np.savez_compressed(good, a=np.arange(50))
        truncated.write_bytes(good.read_bytes()[: len(good.read_bytes()) // 2])
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.write_receipt(product=str(truncated), out_path=str(self.out), arm="run",
                             namespace="ns", extra={})
        self.assertIn("does not open", str(caught.exception))

    def test_POSITIVE_CONTROL_a_real_npz_product_opens_and_its_keys_are_recorded(self):
        slab = self.work / "slab.npz"
        U._atomic_savez(str(slab), xs=np.zeros((2, NBIN)), throws=np.arange(2))
        receipt = ZP.write_receipt(product=str(slab), out_path=str(self.work / "r2.json"),
                                   arm="run", namespace="ns", extra={})
        self.assertEqual(receipt["product"]["opened_as"]["kind"], "npz")
        self.assertIn("xs", receipt["product"]["opened_as"]["keys"])

    def test_an_EXISTING_receipt_is_not_OVERWRITTEN_without_an_explicit_opt_in(self):
        self._write()
        original = self.out.read_text()
        with self.assertRaises(ZP.PrecursorError) as caught:
            self._write()
        self.assertIn("already exists", str(caught.exception))
        self.assertEqual(self.out.read_text(), original)
        self._write(allow_overwrite=True)

    def test_check_receipt_refuses_when_the_product_has_CHANGED_since_measurement(self):
        """A receipt FIELD is a timestamped observation, never a current state."""
        self._write()
        self.product.write_bytes(b"root" + b"\x01" * 300)
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_receipt(str(self.out))
        self.assertIn("CHANGED since it was measured", str(caught.exception))

    def test_check_receipt_refuses_when_the_product_has_been_REMOVED(self):
        self._write()
        self.product.unlink()
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_receipt(str(self.out))
        self.assertIn("no longer exists", str(caught.exception))

    def test_check_receipt_refuses_an_UNDECLARED_population_and_accepts_a_declared_one(self):
        """The flag has TWO reachable values, so this criterion is not satisfied by every product
        carrying it. A 4D combine legitimately carries 0 and is refused, which is correct: it is
        not a Z precursor product."""
        for declared, ok in (("throw,block", True), ("throw", False), ("block", False),
                             ("", False)):
            with self.subTest(declared=declared):
                out = self.work / f"r-{declared or 'none'}.json"
                ZP.write_receipt(product=str(self.product), out_path=str(out), arm="combine",
                                 namespace="ns",
                                 extra=ZP.producer_provenance(bank=str(self.bank.path),
                                                              population_declared=declared))
                if ok:
                    self.assertTrue(ZP.check_receipt(str(out))["ok"])
                else:
                    with self.assertRaises(ZP.PrecursorError) as caught:
                        ZP.check_receipt(str(out))
                    self.assertIn("population was never declared", str(caught.exception))

    def test_check_receipt_refuses_UNAVAILABLE_provenance(self):
        """`UNAVAILABLE` is stamped deliberately rather than omitted so this gate can SEE it.
        Refusing in the producer instead would make provenance a scheduler dependency."""
        for field in ZP.REQUIRED_PROVENANCE:
            with self.subTest(field=field):
                extra = ZP.producer_provenance(bank=str(self.bank.path),
                                               population_declared="throw,block")
                extra[field] = "UNAVAILABLE"
                out = self.work / f"r-{field}.json"
                ZP.write_receipt(product=str(self.product), out_path=str(out), arm="combine",
                                 namespace="ns", extra=extra)
                with self.assertRaises(ZP.PrecursorError) as caught:
                    ZP.check_receipt(str(out))
                self.assertIn(field, str(caught.exception))

    def test_a_MISSING_population_flag_is_distinguished_from_a_ZERO_one(self):
        """Absence means the receipt predates the check; 0 means it ran and found nothing declared.
        Collapsing them would make the criterion pass vacuously on an old artifact."""
        out = self.work / "r-old.json"
        ZP.write_receipt(product=str(self.product), out_path=str(out), arm="combine",
                         namespace="ns", extra={"code_revision": "abc"})
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_receipt(str(out))
        self.assertIn("predates population validation", str(caught.exception))

    def test_provenance_is_IMPORTED_from_the_producer_not_recomputed(self):
        extra = ZP.producer_provenance(bank=str(self.bank.path), population_declared="throw")
        self.assertEqual(extra["code_revision"], U.code_provenance()["code_revision"])
        self.assertEqual(extra["producer_sha256"], U.code_provenance()["producer_sha256"])
        self.assertEqual(extra["bank_cv_sha256"], U._bank_cv_digest(str(self.bank.path)))
        self.assertEqual(extra["cv_support_predicate"], U.CV_SUPPORT_PREDICATE)

    def test_a_TYPO_in_the_population_declaration_refuses(self):
        """Silently recording 0 for a typo would read as a deliberate non-declaration."""
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.producer_provenance(population_declared="throws,block")
        self.assertIn("not populations", str(caught.exception))

    def test_there_is_NO_os_exit_on_the_receipt_or_producer_PATHS(self):
        """`os._exit` skips `finally`, and a record emitted from a bypassed `finally` is the
        bypassed-receipt hazard. AST-keyed, not grep: a grep hits comments and strings."""
        for name in ("z_precursor.py", "z_precursor_admission.py", "unified_throw_cov.py",
                     "unified_throw.py", "unified_throw_cov_5d.py"):
            with self.subTest(module=name):
                tree = ast.parse((ND / name).read_text())
                hits = [node for node in ast.walk(tree)
                        if isinstance(node, ast.Attribute) and node.attr == "_exit"
                        and isinstance(node.value, ast.Name) and node.value.id == "os"]
                self.assertEqual(hits, [], f"{name} calls os._exit at lines "
                                           f"{[h.lineno for h in hits]}")

    def test_the_os_exit_detector_CATCHES_one(self):
        """POSITIVE CONTROL on the detector: an inference from absence needs a covering search, and
        a detector that matches nothing returns the same answer as a correct tree."""
        tree = ast.parse("import os\ndef f():\n    os._exit(1)\n")
        hits = [node for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and node.attr == "_exit"
                and isinstance(node.value, ast.Name) and node.value.id == "os"]
        self.assertEqual(len(hits), 1)


# ============================================================== admission accounting ============
def sacct_rows(rows):
    """Rows in `r5_meter.SACCT_FIELDS` order, so the fixture is the meter's own input shape."""
    return "\n".join("|".join(str(f) for f in row) for row in rows)


NOW = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)


class AdmissionBoundsCommittedExposureNotElapsed(unittest.TestCase):
    """Joseph: bound charged expenditure PLUS the maximum remaining exposure of admitted tasks,
    including queued jobs and retries; do not rely on elapsed-so-far checks alone; preserve R5's
    rule for jobs already running at the stop.
    """

    def arms(self, *names):
        return [ZP.parse_sbatch_arm(LAUNCHER[n]) for n in names]

    def test_the_METER_charges_RUNNING_attempts_and_not_PENDING_ones(self):
        """The reused fact, re-measured here rather than trusted: the cap cannot be overshot by an
        UNCOUNTED in-flight population, so this module does not pretend otherwise."""
        raw = sacct_rows([
            ("100", "a", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
             "2026-09-05T01:00:00", "cpu=32"),
            ("101", "a", "RUNNING", 7200, "shared", "2026-09-05T02:00:00", "Unknown", "cpu=32"),
            ("102", "a", "PENDING", 0, "shared", "Unknown", "Unknown", "cpu=32"),
        ])
        spend = r5_meter._calculate_spend(r5_meter._parse_sacct_dump(raw))
        self.assertEqual(spend["cpu_task_hours"], 3.0)
        self.assertEqual(spend["attempt_count"], 2)
        self.assertNotIn("102", spend["metered_task_ids"],
                         "a PENDING row has no Start, so it is not an attempt at all -- which is "
                         "why the admitted set must be DECLARED and cannot be derived")

    def test_POSITIVE_CONTROL_a_small_proposal_is_PERMITTED(self):
        raw = sacct_rows([("100", "done", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
                           "2026-09-05T01:00:00", "cpu=8")])
        report = ZPA.admission_report(raw_text=raw, admitted=[],
                                      proposed=self.arms("combine"), max_retries=0,
                                      spend_basis="utc", now=NOW)
        self.assertEqual(report["decision"], "PERMITTED")
        self.assertEqual(report["exit_code"], 0)
        self.assertAlmostEqual(report["proposed_remaining_exposure_cpu_task_hours"], 3.0)

    def test_the_FOUR_REAL_ARMS_exceed_R5s_CPU_ceiling_at_ZERO_retries(self):
        """MEASURED, and it is the consequential number: 8x6 + 21x12 + 40x6 + 1x3 = 543 CPU task-h
        committed, against a 500 task-hour ceiling, before a single retry and before the 15.42
        already charged. Reported, not resolved -- shortening an arm's `--time` is a design change
        with its own consequence (a task killed at the wall loses its work), not a repair."""
        raw = sacct_rows([("100", "done", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
                           "2026-09-05T01:00:00", "cpu=8")])
        report = ZPA.admission_report(
            raw_text=raw, admitted=[],
            proposed=self.arms("dump", "block", "run", "combine"),
            max_retries=0, spend_basis="utc", now=NOW)
        self.assertAlmostEqual(report["proposed_remaining_exposure_cpu_task_hours"], 543.0)
        self.assertEqual(report["decision"], "REFUSED_BOUND_EXCEEDS_CEILING")
        self.assertEqual(report["exit_code"], 5)
        self.assertLess(report["headroom_after_bound_cpu_task_hours"], 0.0)

    def test_RETRIES_multiply_the_bound_and_are_NOT_defaulted_away(self):
        """1882 of 1893 measured attempts on the live window are REQUEUED, so a defaulted 0 would
        price the dominant term at nothing."""
        raw = sacct_rows([("100", "done", "COMPLETED", 36, "shared", "2026-09-05T00:00:00",
                           "2026-09-05T00:00:36", "cpu=8")])
        base = None
        for retries in (0, 1, 2):
            report = ZPA.admission_report(raw_text=raw, admitted=[],
                                          proposed=self.arms("combine"), max_retries=retries,
                                          spend_basis="utc", now=NOW)
            got = report["proposed_remaining_exposure_cpu_task_hours"]
            if base is None:
                base = got
            self.assertAlmostEqual(got, base * (1 + retries))
        self.assertNotIn("default", ZPA._build_parser().format_help().split("--max-retries")[1]
                         .split("--now")[0].lower().replace("no default", ""))

    def test_the_THROTTLE_does_NOT_reduce_the_bound(self):
        """`%40` bounds CONCURRENCY, not spend. A throttled array charges exactly as much."""
        run = ZP.parse_sbatch_arm(LAUNCHER["run"])
        self.assertEqual(run["throttle"], 40)
        self.assertAlmostEqual(ZPA.committed_task_hours(run, 0), 40 * 6.0)
        unthrottled = dict(run, throttle=None)
        self.assertAlmostEqual(ZPA.committed_task_hours(unthrottled, 0),
                               ZPA.committed_task_hours(run, 0))

    def test_ELAPSED_SO_FAR_REDUCES_the_bound_but_never_below_zero(self):
        """The one direction elapsed may act in: it can only subtract from a committed maximum."""
        combine = ZP.parse_sbatch_arm(LAUNCHER["combine"])
        raw = sacct_rows([("100", combine["job_name"], "RUNNING", 3600, "shared",
                           "2026-09-05T00:00:00", "Unknown", "cpu=8")])
        report = ZPA.admission_report(raw_text=raw, admitted=[combine], proposed=[],
                                      max_retries=0, spend_basis="utc", now=NOW)
        row = report["admitted"][0]
        self.assertAlmostEqual(row["already_charged_cpu_task_hours"], 1.0)
        self.assertAlmostEqual(row["committed_max_cpu_task_hours"], 3.0)
        self.assertAlmostEqual(row["remaining_exposure_cpu_task_hours"], 2.0)
        over = sacct_rows([("100", combine["job_name"], "RUNNING", 3600 * 99, "shared",
                            "2026-09-05T00:00:00", "Unknown", "cpu=8")])
        row2 = ZPA.admission_report(raw_text=over, admitted=[combine], proposed=[],
                                    max_retries=0, spend_basis="utc", now=NOW)["admitted"][0]
        self.assertEqual(row2["remaining_exposure_cpu_task_hours"], 0.0)

    def test_a_NAIVE_or_UNKNOWN_spend_basis_REFUSES(self):
        raw = sacct_rows([("100", "d", "COMPLETED", 36, "shared", "2026-09-05T00:00:00",
                           "2026-09-05T00:00:36", "cpu=8")])
        for basis in ("naive", "unknown"):
            with self.subTest(basis=basis):
                with self.assertRaises(ZP.PrecursorError) as caught:
                    ZPA.admission_report(raw_text=raw, admitted=[], proposed=[], max_retries=0,
                                         spend_basis=basis, now=NOW)
                self.assertIn("1894", str(caught.exception),
                              "the refusal must carry the measurement behind it")
        with self.assertRaises(ZP.PrecursorError):
            ZPA.admission_report(raw_text=raw, admitted=[], proposed=[], max_retries=0,
                                 spend_basis="pacific", now=NOW)

    def test_the_refusal_adopts_NO_NUMERICAL_MARGIN(self):
        """No threshold is adopted for the naive case: the 0.4858 task-hour under-read appears
        nowhere in the module, because encoding it would be adopting a number AND would be the
        wrong number the moment the offset changes."""
        source = (ND / "z_precursor_admission.py").read_text()
        tree = ast.parse(source)
        literals = [node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Constant) and isinstance(node.value, float)]
        self.assertNotIn(0.4858, literals)
        self.assertEqual([v for v in literals if v not in (0.0, 3600.0)], [],
                         f"an unexpected float literal entered the module: {literals}")

    def test_an_UNDECLARED_LIVE_arm_REFUSES(self):
        raw = sacct_rows([
            ("200", "somebody_elses_array", "RUNNING", 60, "shared", "2026-09-05T00:00:00",
             "Unknown", "cpu=8"),
        ])
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZPA.admission_report(raw_text=raw, admitted=[], proposed=self.arms("combine"),
                                 max_retries=0, spend_basis="utc", now=NOW)
        self.assertIn("somebody_elses_array", str(caught.exception))
        self.assertIn("NOT sufficient", str(caught.exception),
                      "the refusal must state its own limit: a wholly-queued undeclared arm is "
                      "invisible to the meter and would not appear here")

    def test_DECLARING_that_arm_makes_the_same_dump_PERMITTED(self):
        """The other direction of the same guard. Without this arm a guard that refuses everything
        would be indistinguishable from one that works."""
        fake = dict(ZP.parse_sbatch_arm(LAUNCHER["combine"]),
                    job_name="somebody_elses_array", n_tasks=1, time_limit_hours=1.0)
        raw = sacct_rows([
            ("200", "somebody_elses_array", "RUNNING", 60, "shared", "2026-09-05T00:00:00",
             "Unknown", "cpu=8"),
        ])
        report = ZPA.admission_report(raw_text=raw, admitted=[fake],
                                      proposed=self.arms("combine"), max_retries=0,
                                      spend_basis="utc", now=NOW)
        self.assertEqual(report["decision"], "PERMITTED")

    def test_HISTORICAL_REQUEUES_with_a_TERMINAL_final_row_are_NOT_live(self):
        """THE REGRESSION THIS GUARD ALREADY HAD, and it fired on a correct state.

        Run against the real accounting window, the first version refused immediately: task
        `57712764` carries 1885 attempts, 1882 of them REQUEUED, and its FINAL row is CANCELLED.
        Liveness is a property of the TASK, and the row that settles it here has `Start` `None`, so
        the meter's attempt set cannot see it -- which is why `_live_tasks` reads the raw rows.
        """
        requeues = [("300", "waker", "REQUEUED", 10, "shared",
                     f"2026-09-05T0{h}:00:00", f"2026-09-05T0{h}:00:10", "cpu=8")
                    for h in range(1, 6)]
        live = sacct_rows(requeues)
        self.assertIn("waker", ZPA._live_tasks(live)[0].values(),
                      "with no terminal row the task IS live")
        finished = sacct_rows(requeues + [
            ("300", "waker", "CANCELLED by 12345", 0, "shared", "None",
             "2026-09-09T14:39:30", "cpu=8")])
        self.assertEqual(ZPA._live_tasks(finished)[0], {},
                         "a terminal row ends the task however many requeues precede it")
        report = ZPA.admission_report(raw_text=finished, admitted=[],
                                      proposed=self.arms("combine"), max_retries=0,
                                      spend_basis="utc", now=NOW)
        self.assertEqual(report["decision"], "PERMITTED")

    def test_an_UNRECOGNISED_state_fails_CLOSED_towards_being_live(self):
        raw = sacct_rows([("400", "odd", "SOME_NEW_STATE", 10, "shared",
                           "2026-09-05T00:00:00", "2026-09-05T00:00:10", "cpu=8")])
        self.assertEqual(list(ZPA._live_tasks(raw)[0]), ["400"])

    def test_R5s_RUNNING_AT_THE_STOP_rule_is_PRESERVED_and_STATED(self):
        """R5: a job running at the stop runs to completion and its spend is counted. Nothing here
        may read as an instruction to cancel one."""
        combine = ZP.parse_sbatch_arm(LAUNCHER["combine"])
        raw = sacct_rows([("100", combine["job_name"], "RUNNING", 60, "shared",
                           "2026-09-05T00:00:00", "Unknown", "cpu=8")])
        report = ZPA.admission_report(raw_text=raw, admitted=[combine], proposed=[],
                                      max_retries=0, spend_basis="utc", now=NOW)
        self.assertIn("RUN TO COMPLETION", report["running_at_stop_policy"])
        self.assertIn("never cancels", report["running_at_stop_policy"])
        text = json.dumps(report).lower()
        for word in ("scancel", "cancel the", "kill "):
            self.assertNotIn(word, text)
        self.assertGreater(report["admitted"][0]["remaining_exposure_cpu_task_hours"], 0.0,
                           "its exposure is COUNTED, which is what preserving the rule means")

    def test_the_STOP_FIRING_outranks_the_bound(self):
        """A fired stop and an exceeded bound are different outcomes and must not be conflated."""
        raw = sacct_rows([("100", "big", "COMPLETED", int(600 * 3600), "shared",
                           "2026-09-03T00:00:00", "2026-09-05T00:00:00", "cpu=8")])
        report = ZPA.admission_report(raw_text=raw, admitted=[], proposed=[], max_retries=0,
                                      spend_basis="utc", now=NOW)
        self.assertEqual(report["decision"], "REFUSED_STOP_FIRED")
        self.assertEqual(report["exit_code"], 3)
        self.assertTrue(report["r5_fired"]["cpu"])

    #: THE ONE DETECTOR. Module level so the equality arm and its positive control call the SAME
    #: code. The review's finding: my control re-typed the sweep, so a detector blind to a
    #: particular spelling would have been confirmed blind by its own control -- a fixture derived
    #: from the rule it tests, which cannot disagree with it.
    @staticmethod
    def private_meter_attrs_of(source):
        tree = ast.parse(source)
        return {node.attr for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "r5_meter" and node.attr.startswith("_")}

    def test_the_meter_reuse_rides_a_DECLARED_private_surface(self):
        """The independent review's durability point, made into an instrument instead of a note.

        Reuse of an underscore name rides an unversioned interface and would break silently under a
        refactor of the meter. A COMMENT saying so rots -- which is the failure mode being guarded
        against -- so the set is declared in `METER_PRIVATE_DEPENDENCIES` and checked BOTH WAYS:

          * every declared name must still EXIST on the meter, so a refactor that removes one fails
            here rather than at runtime on the cluster;
          * the declared set must EQUAL what the detector finds, so a future edit that reaches for a
            SECOND private name fails too instead of widening the coupling unrecorded.

        The second arm is the one that makes this more than a spelling check. Measured over
        EXECUTABLE code, not text: the module docstring names FOUR further private functions while
        discussing them, and a naive regex over the text returns more tokens than there are live
        attribute accesses.
        """
        for declared in (ZPA.METER_PRIVATE_DEPENDENCIES, ZPA.METER_PRIVATE_DEPENDENCIES_IN_TESTS):
            for name, reason in declared.items():
                with self.subTest(name=name):
                    self.assertTrue(hasattr(r5_meter, name),
                                    f"r5_meter.{name} is GONE -- the meter was refactored and this "
                                    f"module's reuse is broken. Declared reason: {reason}")
                    self.assertTrue(reason.strip(), f"{name} is declared with no reason")

        for path, expected in ((ND / "z_precursor_admission.py",
                                set(ZPA.METER_PRIVATE_DEPENDENCIES)),
                               (ND / "tests" / "test_z_precursor.py",
                                set(ZPA.METER_PRIVATE_DEPENDENCIES_IN_TESTS))):
            with self.subTest(file=path.name):
                self.assertEqual(self.private_meter_attrs_of(path.read_text()), expected,
                                 "the ACTUAL private meter dependencies and the declared set have "
                                 "diverged; declare the new one with its reason rather than leaving "
                                 "the coupling unrecorded")

    def test_the_detectors_BLIND_SPOTS_are_ABSENT_from_both_files(self):
        """WHAT THE EQUALITY ARM'S COMPLETENESS RESTS ON, named and checked.

        The detector sees `r5_meter.<attr>` and nothing else. Four forms would evade it, so the
        equality arm is a complete statement of the coupling only while all four are absent:
        `getattr(r5_meter, "_x")`, `from r5_meter import _x`, an aliased import then `m._x`, and
        `sys.modules["r5_meter"]._x`. Measured absent from both files -- which is what makes the
        declared sets complete TODAY, and is exactly what the re-typed control did not establish.
        If one is ever introduced, widen the DETECTOR rather than the declaration.
        """
        for path in (ND / "z_precursor_admission.py", ND / "tests" / "test_z_precursor.py"):
            source = path.read_text()
            tree = ast.parse(source)
            with self.subTest(file=path.name, form="getattr"):
                self.assertEqual(
                    [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name) and n.func.id == "getattr"
                     and n.args and isinstance(n.args[0], ast.Name)
                     and n.args[0].id == "r5_meter"], [])
            with self.subTest(file=path.name, form="from-import"):
                self.assertEqual(
                    [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                     and n.module == "r5_meter"], [])
            with self.subTest(file=path.name, form="alias"):
                self.assertEqual(
                    [a.asname for n in ast.walk(tree) if isinstance(n, ast.Import)
                     for a in n.names if a.name == "r5_meter" and a.asname], [])
            with self.subTest(file=path.name, form="sys.modules"):
                # KEYED ON THE SUBSCRIPT, NOT ON THE SUBSTRING. My first version banned
                # `sys.modules[` outright and fired on this file's own docstring, which discusses
                # `sys.modules["ROOT"]` -- a right check over the wrong operand, and the form this
                # suite keeps catching elsewhere. Only a subscript naming r5_meter evades the
                # detector; one naming ROOT is the stubbed-ROOT instrument and is unrelated.
                self.assertEqual(
                    [n for n in ast.walk(tree) if isinstance(n, ast.Subscript)
                     and isinstance(n.value, ast.Attribute) and n.value.attr == "modules"
                     and isinstance(n.slice, ast.Constant) and n.slice.value == "r5_meter"], [])

    def test_the_private_surface_detector_CATCHES_an_undeclared_name(self):
        """POSITIVE CONTROL, now calling the SAME detector the equality arm uses.

        My first version re-typed the sweep inline, so a detector blind to a spelling would have
        been confirmed blind by its own control. This proves the detector is not vacuous; the blind
        spots it CANNOT see are enumerated in the arm above, which is the honest division.
        """
        found = self.private_meter_attrs_of(
            "import r5_meter\nx = r5_meter._brand_new_private(1)\n")
        self.assertEqual(found, {"_brand_new_private"})
        self.assertNotIn("_brand_new_private", ZPA.METER_PRIVATE_DEPENDENCIES)
        # And it does NOT over-match: a public access must not be reported as private.
        self.assertEqual(self.private_meter_attrs_of(
            "import r5_meter\ny = r5_meter.build_receipt\n"), set())

    def test_parse_sacct_dump_has_a_CONTRACT_arm_not_only_an_existence_check(self):
        """`hasattr` catches REMOVAL, not semantic DRIFT -- the review's second residual, and it was
        a real gap: `_calculate_spend` had a contract arm and `_parse_sacct_dump` had none.

        The three properties this module's arithmetic depends on, asserted directly:
          * STEP ROWS ARE EXCLUDED. `.batch`/`.extern` rows carry the same ElapsedRaw as their
            allocation row, so counting them would double every job.
          * AN ATTEMPT IS `(JobID, Start)`. Two executions of one requeued job id are TWO attempts;
            keying on job id alone is the defect the meter's own repair closed.
          * ONE ATTEMPT OBSERVED TWICE IS COUNTED ONCE, which is what makes concatenating two query
            windows safe -- and `_charged_by_name` relies on it, because it takes the attempt SET
            from here and only the job NAMES from the raw rows.
        """
        rows = sacct_rows([
            ("900", "arm", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
             "2026-09-05T01:00:00", "cpu=8"),
            ("900.batch", "batch", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
             "2026-09-05T01:00:00", "cpu=8"),
            ("900.extern", "extern", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
             "2026-09-05T01:00:00", "cpu=8"),
        ])
        attempts = r5_meter._parse_sacct_dump(rows)
        self.assertEqual(len(attempts), 1, f"step rows must be excluded; got {sorted(attempts)}")

        requeued = sacct_rows([
            ("901", "arm", "REQUEUED", 600, "shared", "2026-09-05T00:00:00",
             "2026-09-05T00:10:00", "cpu=8"),
            ("901", "arm", "COMPLETED", 1200, "shared", "2026-09-05T01:00:00",
             "2026-09-05T01:20:00", "cpu=8"),
        ])
        self.assertEqual(len(r5_meter._parse_sacct_dump(requeued)), 2,
                         "two executions of one job id are TWO attempts -- if this collapses to "
                         "one, every retry is under-counted and the admission bound is too low")

        twice = sacct_rows([
            ("902", "arm", "RUNNING", 600, "shared", "2026-09-05T00:00:00", "Unknown", "cpu=8"),
            ("902", "arm", "RUNNING", 600, "shared", "2026-09-05T00:00:00", "Unknown", "cpu=8"),
        ])
        self.assertEqual(len(r5_meter._parse_sacct_dump(twice)), 1,
                         "one attempt observed twice is ONE attempt; otherwise concatenating two "
                         "query windows double-charges")

    def test_the_METER_is_REUSED_rather_than_reimplemented(self):
        """A rule retyped is a second implementation. The module must call the meter, not restate
        its ceilings, its unit, or its parser."""
        source = (ND / "z_precursor_admission.py").read_text()
        tree = ast.parse(source)
        imported = {alias.name for node in ast.walk(tree)
                    if isinstance(node, ast.Import) for alias in node.names}
        self.assertIn("r5_meter", imported)
        for restated in ("CPU_TASK_HOURS_CEILING =", "GPU_TASK_HOURS_CEILING =", "T0_UTC =",
                         "def _parse_sacct_dump", "def _calculate_spend"):
            self.assertNotIn(restated, source, f"{restated!r} is a second implementation")
        report = ZPA.admission_report(
            raw_text=sacct_rows([("1", "x", "COMPLETED", 36, "shared", "2026-09-05T00:00:00",
                                  "2026-09-05T00:00:36", "cpu=8")]),
            admitted=[], proposed=[], max_retries=0, spend_basis="utc", now=NOW)
        self.assertEqual(report["ceilings"]["cpu_task_hours"], r5_meter.CPU_TASK_HOURS_CEILING)
        self.assertEqual(report["meter_reuse"]["unit"], r5_meter.UNIT)

    def test_the_bound_does_NOT_double_count_an_arms_own_charged_hours(self):
        combine = ZP.parse_sbatch_arm(LAUNCHER["combine"])
        raw = sacct_rows([
            ("100", combine["job_name"], "RUNNING", 3600, "shared", "2026-09-05T00:00:00",
             "Unknown", "cpu=8"),
            ("101", "unrelated", "COMPLETED", 3600, "shared", "2026-09-05T00:00:00",
             "2026-09-05T01:00:00", "cpu=8"),
        ])
        report = ZPA.admission_report(raw_text=raw, admitted=[combine], proposed=[],
                                      max_retries=0, spend_basis="utc", now=NOW)
        # charged = 2.0 (1 h arm + 1 h unrelated); exposure = 3.0 - 1.0 = 2.0; bound = 4.0
        # = unrelated 1.0 + the arm's FULL committed 3.0. Nothing counted twice.
        self.assertAlmostEqual(report["charged"]["cpu_task_hours"], 2.0)
        self.assertAlmostEqual(report["bound_cpu_task_hours"], 4.0)

    def test_the_CLI_exits_with_the_decisions_code(self):
        with tempfile.TemporaryDirectory() as td:
            dump = Path(td) / "d.txt"
            dump.write_text(sacct_rows([("1", "x", "COMPLETED", 36, "shared",
                                         "2026-09-05T00:00:00", "2026-09-05T00:00:36",
                                         "cpu=8")]) + "\n")
            base = ["--sacct-dump", str(dump), "--now", "2026-09-11T12:00:00Z",
                    "--max-retries", "0"]
            self.assertEqual(ZPA.main(base + ["--spend-basis", "utc"]), 0)
            self.assertEqual(ZPA.main(base + ["--spend-basis", "naive"]), 2)
            # The RUN arm ALONE is 240 committed task-h, which is under the 500 ceiling -- so a
            # single-arm proposal is correctly PERMITTED and is the positive control for exit 0
            # with real exposure in the bound. It takes the whole precursor to cross it.
            self.assertEqual(
                ZPA.main(base + ["--spend-basis", "utc", "--proposed-launcher",
                                 str(LAUNCHER["run"])]), 0)
            self.assertEqual(
                ZPA.main(base + ["--spend-basis", "utc"]
                         + [arg for arm in ("dump", "block", "run", "combine")
                            for arg in ("--proposed-launcher", str(LAUNCHER[arm]))]), 5)


# ============================================ the 13/27/5 partition, and NO donor decision ======
class ThePartitionIsEnforcedAndNoDonorIsChosen(unittest.TestCase):
    """Joseph: enforce the 13/27/5 disjoint partition, but do not change a band's donor."""

    def setUp(self):
        try:
            import z_contract
        except Exception as exc:                             # noqa: BLE001
            self.skipTest(f"z_contract unavailable: {exc}")
        self.contract = z_contract

    def inventory(self):
        """The support family's actual band set, from the PRODUCER's own two lists plus the
        derived remainder. `check_band_partition` requires a real inventory precisely because 27
        invented residual names once passed a count-only check."""
        vert = list(self.contract.VERT_BANDS)
        lateral = list(self.contract.LATERAL_BANDS)
        residual = [f"__residual_{i}" for i in range(self.contract.N_RESIDUAL)]
        return vert, residual, lateral

    def test_the_partition_is_13_27_5_disjoint_and_exhaustive(self):
        vert, residual, lateral = self.inventory()
        report = self.contract.check_band_partition(vert, residual, lateral,
                                                    vert + residual + lateral)
        self.assertEqual((report["n_vert"], report["n_residual"], report["n_lateral"]),
                         (13, 27, 5))
        self.assertEqual(report["n_total"], 45)
        self.assertTrue(report["exhaustive"])

    def test_a_COUNT_only_operand_cannot_pass(self):
        """27 invented residual names are 45 disjoint names and the right counts. The inventory is
        what refuses them."""
        vert, residual, lateral = self.inventory()
        real_inventory = vert + [f"__real_residual_{i}" for i in range(27)] + lateral
        with self.assertRaises(self.contract.ZContractError) as caught:
            self.contract.check_band_partition(vert, residual, lateral, real_inventory)
        self.assertIn("inventory", str(caught.exception))

    def test_an_EMPTY_inventory_refuses(self):
        vert, residual, lateral = self.inventory()
        with self.assertRaises(self.contract.ZContractError):
            self.contract.check_band_partition(vert, residual, lateral, [])

    def test_overlap_in_EITHER_direction_refuses(self):
        vert, residual, lateral = self.inventory()
        for label, v, r, a in (("V&R", vert, [vert[0]] + residual[1:], lateral),
                               ("V&A", vert, residual, [vert[0]] + lateral[1:]),
                               ("R&A", vert, residual, [residual[0]] + lateral[1:])):
            with self.subTest(overlap=label):
                with self.assertRaises(self.contract.ZContractError):
                    self.contract.check_band_partition(v, r, a, list(set(v + r + a)))

    def test_NO_DONOR_IS_DECIDED_ANYWHERE_IN_THIS_WORK(self):
        """Explicit per-band donor BINDING is provenance and is permitted; DECIDING which file
        supplies a band is not.

        ⚠ THE OPERAND IS EXECUTABLE CODE, NOT THE FILE'S TEXT. My first version banned the token
        anywhere and failed on `z_precursor.py`'s own docstring, which names G's throw in the
        sentence saying it MUST NOT be substituted. Banning that is banning the warning. So the
        sweep is over CODE -- string constants and identifiers reachable at runtime -- via the AST.
        """
        for name in ("z_precursor.py", "z_precursor_admission.py"):
            with self.subTest(module=name):
                tree = ast.parse((ND / name).read_text())
                docstrings = set()
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef,
                                         ast.AsyncFunctionDef)):
                        doc = ast.get_docstring(node, clean=False)
                        if doc:
                            docstrings.add(doc)
                live = [node.value.lower() for node in ast.walk(tree)
                        if isinstance(node, ast.Constant) and isinstance(node.value, str)
                        and node.value not in docstrings]
                live += [node.id.lower() for node in ast.walk(tree)
                         if isinstance(node, ast.Name)]
                live += [node.attr.lower() for node in ast.walk(tree)
                         if isinstance(node, ast.Attribute)]
                for token in ("donor", "fluxfix"):
                    offenders = [text for text in live if token in text]
                    self.assertEqual(offenders, [],
                                     f"{name} has {token!r} in live code: {offenders}")

    def test_the_donor_detector_CATCHES_one(self):
        """POSITIVE CONTROL: a detector that matches nothing gives the same answer as clean code."""
        tree = ast.parse('CHOSEN = "unified_throw_cov_5d_fluxfix_20260806_full160.root"\n')
        live = [node.value.lower() for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        self.assertTrue(any("fluxfix" in text for text in live))

    def test_PER_BAND_DONOR_BINDING_is_RECORDED_and_is_not_a_DECISION(self):
        """Joseph permits recording which file supplied each band; he forbids deciding it.

        The record is checked against the fixture's own file layout rather than against a template:
        the knob endpoints come from `block5d_knobs.npz` and flux universe `u` from the flux task
        that tiles it, and those are the launcher's own placements.
        """
        work = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or None))
        self.addCleanup(__import__("shutil").rmtree, str(work), True)
        bank = SyntheticBank(work)
        saved = U._xsec_for_weights
        U._xsec_for_weights = kernel()
        self.addCleanup(setattr, U, "_xsec_for_weights", saved)
        block_glob = write_block_slabs(work / "b")
        throw_glob = write_throw_slabs(work / "t")
        with _StubbedRoot() as rec:
            result = U.do_combine(combine_args(
                bank=str(bank.path), combine=throw_glob, block_slabs=block_glob,
                expected_throws="0-7", out_root=str(work / "o.root")))
        donors = result["band_donor"]
        self.assertEqual(result["n_band_donors"], len(U.KNOB_BANDS) * 2
                         + U.EXPECTED_FLUX_UNIVERSES)
        for band in U.KNOB_BANDS:
            for idx in ("0", "1"):
                self.assertEqual(donors[f"{band}:{idx}"], "block5d_knobs.npz")
        per = U.EXPECTED_FLUX_UNIVERSES // 20
        for u in range(U.EXPECTED_FLUX_UNIVERSES):
            self.assertEqual(donors[f"flux{u}"], f"block5d_flux_{u // per + 1}.npz")
        self.assertIn("n_band_donors", rec.written)
        self.assertEqual(rec.params["band_donor_MaCCQE_1"], "block5d_knobs.npz")

    def test_the_donor_binding_FOLLOWS_the_files_rather_than_prescribing_them(self):
        """THE PROOF THAT IT IS A RECORD AND NOT A CHOICE: move a band's endpoints to a different
        file and the binding must FOLLOW, with no list in the code to contradict it."""
        work = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or None))
        self.addCleanup(__import__("shutil").rmtree, str(work), True)
        bank = SyntheticBank(work)
        saved = U._xsec_for_weights
        U._xsec_for_weights = kernel()
        self.addCleanup(setattr, U, "_xsec_for_weights", saved)
        # Ten flux tasks of ten universes instead of twenty of five: a DIFFERENT donor layout that
        # no code path here knows about.
        block_glob = write_block_slabs(work / "b", n_flux_tasks=10)
        throw_glob = write_throw_slabs(work / "t")
        result = U.do_combine(combine_args(
            bank=str(bank.path), combine=throw_glob, block_slabs=block_glob,
            expected_throws="0-7"))
        self.assertEqual(result["band_donor"]["flux0"], "block5d_flux_1.npz")
        self.assertEqual(result["band_donor"]["flux15"], "block5d_flux_2.npz",
                         "under a ten-task layout universe 15 comes from task 2, and the record "
                         "must say so rather than what a twenty-task layout would give")

    def test_Gs_THROW_IS_NOT_SUBSTITUTED_FOR_Zs(self):
        """`SPEC` §1.3a: Z derives its OWN. G's throw exists and must not be substituted."""
        plan = ZP.namespace_plan("/data", namespace="ns")
        for entry in plan["arms"].values():
            self.assertNotIn("fluxfix", entry["product_glob"])
            self.assertIn("/uq_5d/ns", entry["product_glob"])


# =========================================================== (g) the END-TO-END fixture =========
class EndToEndTheProducerWritesWhatTheZReaderAccepts(ProducerFixture):
    """(g) The ACTUAL producer and the ACTUAL reader interfaces, not a stub that agrees with me.

    The chain exercised here is: synthetic bank built from `_load_bank`'s demands -> the real
    `do_combine` -> the real support mask -> `z_build_path.classify_support_change`, which is the Z
    reader's own entry point for a support declaration -> the real receipt, written after the
    product and then gated. The only substitutions are the LightGBM kernel (through the producer's
    own hook) and `ROOT` (through the recorder that separates written from built).
    """

    def setUp(self):
        super().setUp()
        try:
            import z_build_path
        except Exception as exc:                             # noqa: BLE001
            self.skipTest(f"z_build_path unavailable: {exc}")
        self.reader = z_build_path

    def test_the_persisted_mask_is_ACCEPTED_by_the_Z_readers_support_classifier(self):
        result, rec = self.run_combine(out_root=str(self.work / "z" / "c.root"),
                                       null=True,
                                       expected_throw_files=",".join(self.throw_names),
                                       expected_block_files=",".join(self.block_names))
        observed = result["cv_support_mask"]
        # The mask as the FILE carries it, reconstructed from the recorder rather than from the
        # in-process array: the artifact is what a downstream reader actually gets.
        from_file = np.zeros(rec.params["n_cv_bins_total"], bool)
        for key in rec.hists["hCvSupportMask"]:
            from_file[key[0] - 1] = True
        np.testing.assert_array_equal(from_file, observed)
        verdict = self.reader.classify_support_change(from_file, observed)
        self.assertEqual(verdict["state"], "RESOLVED")
        self.assertEqual(verdict["n_differing"], 0)

    def test_a_CHANGED_support_is_classified_as_a_DECLARATION_defect(self):
        """The reader's other direction. Without the persisted mask this comparison had no left
        operand at all, which is why it could never fire."""
        result, _rec = self.run_combine(out_root=str(self.work / "z" / "c.root"))
        observed = result["cv_support_mask"]
        declared = observed.copy()
        declared[self.ZERO_BINS[0]] = True       # a declaration that the pinned zero is supported
        verdict = self.reader.classify_support_change(declared, observed)
        self.assertEqual(verdict["state"], "SUPPORT_DEFINITION_CHANGED")
        self.assertEqual(verdict["n_differing"], 1)
        self.assertEqual(verdict["indices"], [self.ZERO_BINS[0]])

    def test_a_SUPPORT_INDEXED_mask_would_make_the_reader_BLIND(self):
        """Why the mask is indexed in the BINNING. A support-indexed mask is all-ones, so the
        reader's comparison is vacuous and returns RESOLVED against any declaration of that shape.
        """
        result, _rec = self.run_combine(out_root=str(self.work / "z" / "c.root"))
        support_indexed = np.ones(result["n_cv_support"], bool)
        verdict = self.reader.classify_support_change(support_indexed, support_indexed)
        self.assertEqual(verdict["state"], "RESOLVED")
        self.assertEqual(support_indexed.size, NBIN - len(self.ZERO_BINS))
        self.assertEqual(result["cv_support_mask"].size, NBIN,
                         "the real mask spans the binning, so it CAN disagree")

    def test_the_CONTRACT_FIRES_FROM_INSIDE_do_combine(self):
        """The redesign's load-bearing claim: the refusals happen in the PRODUCER, not in a
        launcher-side process. Same interpreter that does the writing, so nothing can change
        between the check and the use."""
        data_root = self.work / "dr"
        saved = dict(os.environ)
        os.environ[ZP.NAMESPACE_ENV] = "nsX"
        os.environ["MNV_DATA_ROOT"] = str(data_root)
        os.environ.pop("MNV_EST_SEED_OFFSET", None)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved)))
        plan = ZP.namespace_plan(str(data_root), namespace="nsX")
        run_dir, block_dir = Path(plan["arms"]["run"]["dir"]), Path(plan["arms"]["block"]["dir"])
        # THE REAL DECLARED POPULATIONS, because the producer now DERIVES them from the arms' own
        # `#SBATCH --array` lines: 40 slabs x 4 throws = 160, and 21 block slabs. A smaller
        # fixture was this test disagreeing with the world rather than with the code.
        throw_glob = write_throw_slabs(run_dir, n_slabs=40, per=4)
        block_glob = write_block_slabs(block_dir)
        out = Path(plan["arms"]["combine"]["dir"]) / "unified_throw_cov_5d.root"

        def run(**kw):
            fields = dict(bank=str(self.bank.path), combine=throw_glob,
                          block_slabs=block_glob, expected_throws="0-159",
                          out_root=str(out), z_namespace_arm="combine")
            fields.update(kw)
            with _StubbedRoot():
                return U.do_combine(combine_args(**fields))

        # (1) HEALTHY: the combine arm's own namespace is empty, so it proceeds -- and the expected
        #     populations were DERIVED inside the producer with nothing passed in.
        result = run()
        self.assertTrue(result["throw_population_declared"])
        self.assertTrue(result["block_population_declared"])

        # (2) THE MEMBER AXIS refuses from in here, including at offset 0.
        os.environ["MNV_EST_SEED_OFFSET"] = "0"
        with self.assertRaises(ZP.PrecursorError) as caught:
            run()
        self.assertIn("mii/member_kNNNNNN", str(caught.exception))
        os.environ.pop("MNV_EST_SEED_OFFSET")

        # (3) A READER POINTED AT A DIFFERENT NAMESPACE refuses -- (c)'s defect, caught by the
        #     producer rather than matched by a glob.
        foreign = write_block_slabs(self.work / "foreign")
        with self.assertRaises(SystemExit) as refused:
            run(block_slabs=foreign)
        self.assertIn("--block-slabs reads", str(refused.exception))
        self.assertIn("is the (c) defect itself", str(refused.exception))

        # (4) A NON-FRESH combine namespace refuses.
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"root" + b"\x00" * 300)
        with self.assertRaises(ZP.PrecursorError) as stale:
            run()
        self.assertIn("NOT FRESH", str(stale.exception))

    def test_the_RECEIPT_is_written_by_the_producer_AFTER_Close(self):
        """(f) moved into the producer with the rest. `fo.Close()` is the only thing that
        finalizes a `TFile`, so a receipt written before it could not have observed the product."""
        data_root = self.work / "dr2"
        saved = dict(os.environ)
        os.environ[ZP.NAMESPACE_ENV] = "nsR"
        os.environ["MNV_DATA_ROOT"] = str(data_root)
        os.environ.pop("MNV_EST_SEED_OFFSET", None)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved)))
        plan = ZP.namespace_plan(str(data_root), namespace="nsR")
        throw_glob = write_throw_slabs(Path(plan["arms"]["run"]["dir"]), n_slabs=40, per=4)
        block_glob = write_block_slabs(Path(plan["arms"]["block"]["dir"]))
        out = Path(plan["arms"]["combine"]["dir"]) / "unified_throw_cov_5d.root"
        receipt = out.with_suffix(".receipt.json")
        args = combine_args(bank=str(self.bank.path), combine=throw_glob,
                            block_slabs=block_glob, expected_throws="0-159",
                            out_root=str(out), z_namespace_arm="combine",
                            z_receipt=str(receipt))
        # The recorder stands in for the TFile, so nothing lands at `out`. That is EXACTLY the
        # state a receipt must refuse -- and it does, which is this arm's whole point.
        with self.assertRaises(ZP.PrecursorError) as caught:
            with _StubbedRoot():
                U.do_combine(args)
        self.assertIn("does not exist", str(caught.exception))
        self.assertFalse(receipt.exists(),
                         "a refused receipt leaves no file, so no record can claim a completion "
                         "that did not happen")

    def test_the_WHOLE_CHAIN_from_a_fresh_namespace_to_a_gated_receipt(self):
        data_root = self.work / "data"
        plan = ZP.namespace_plan(str(data_root), namespace="zprec_test")
        self.assertTrue(ZP.check_namespace_fresh(plan)["fresh"])
        self.assertTrue(ZP.check_no_member_axis({})["ok"])

        block_dir = Path(plan["arms"]["block"]["dir"])
        run_dir = Path(plan["arms"]["run"]["dir"])
        block_glob = write_block_slabs(block_dir)
        throw_glob = write_throw_slabs(run_dir)
        # NOW the namespace is populated, so freshness must REFUSE a re-run into it.
        with self.assertRaises(ZP.PrecursorError):
            ZP.check_namespace_fresh(plan, ["block", "run"])

        product = Path(plan["arms"]["combine"]["dir"]) / "unified_throw_cov_5d.root"
        args = combine_args(bank=str(self.bank.path), combine=throw_glob,
                            block_slabs=block_glob, expected_throws="0-7",
                            expected_throw_files=",".join(
                                sorted(os.path.basename(p)
                                       for p in __import__("glob").glob(throw_glob))),
                            expected_block_files=",".join(
                                sorted(os.path.basename(p)
                                       for p in __import__("glob").glob(block_glob))),
                            null=True, out_root=str(product))
        with _StubbedRoot() as rec:
            result = U.do_combine(args)
        self.assertTrue(result["throw_population_declared"])
        self.assertTrue(result["block_population_declared"])
        self.assertIn("hCvSupportMask", rec.written)

        # The recorder stands in for the TFile, so the product is materialized here with ROOT's
        # magic bytes. That is the honest limit: no ROOT on this checkout, so the receipt's
        # openability check is exercised against a real file whose CONTENT is not a real TFile.
        product.parent.mkdir(parents=True, exist_ok=True)
        product.write_bytes(b"root" + json.dumps(
            {k: v for k, v in rec.params.items()}).encode() + b"\x00" * 200)
        receipt_path = product.with_suffix(".receipt.json")
        receipt = ZP.write_receipt(
            product=str(product), out_path=str(receipt_path), arm="combine",
            namespace="zprec_test", plan_json=plan, code_root=str(REPO),
            extra=ZP.producer_provenance(bank=str(self.bank.path),
                                         population_declared="throw,block"))
        self.assertTrue(ZP.check_receipt(str(receipt_path))["ok"])
        self.assertEqual(receipt["namespace_plan"]["namespace"], "zprec_test")
        self.assertEqual(receipt["extra"]["cv_support_predicate"], U.CV_SUPPORT_PREDICATE)

        # AND THE RECEIPT IS LAST: mutating the product afterwards invalidates the gate.
        product.write_bytes(b"root" + b"\x02" * 400)
        with self.assertRaises(ZP.PrecursorError):
            ZP.check_receipt(str(receipt_path))


if __name__ == "__main__":
    unittest.main()
