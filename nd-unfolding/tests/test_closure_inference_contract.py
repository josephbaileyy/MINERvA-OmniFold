"""KNOWN_ISSUES #31: the powered-closure artifact carries its inference contract.

Before this, `closure_powered_truth_reweight.py` saved only `dump_rows_a/b`, `weights_push` and
`mc_indices`, so an inference-only reproduction had no stored event-feature normalization or network
configuration to assert against. The contract is built from the REAL loader's meta on a synthetic
dump here (no TensorFlow), and the driver's `main` is checked to build both networks from the same
architecture constants it records and to write the contract into the artifact.
"""
import ast
import os
import sys
import tempfile
import unittest

import numpy as np

TESTS = os.path.dirname(os.path.abspath(__file__))
PET = os.path.join(os.path.dirname(TESTS), "pet")
for _p in (PET, TESTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import closure_powered_truth_reweight as cpt  # noqa: E402
import fullevent_fps_dataloader as fed        # noqa: E402
from test_fullevent_schema import real_dataloader, synthetic  # noqa: E402

NORM_KEYS = ("reco_norm_mean", "reco_norm_std", "truth_norm_mean", "truth_norm_std")


class ContractFromTheRealLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.path, _ = synthetic(cls._td.name)
        cls.loader_args = {"inputs": cls.path, "max_events": 400, "seed": 0, "bkg_mode": "mc-only"}
        with real_dataloader():
            _d, mc, _imc, cls.cr, cls.cg, cls.meta = fed.build_fullevent_loaders(
                cls.path, max_events=400, seed=0, bkg_mode="mc-only")
        cls.reco, cls.gen = np.asarray(mc.reco), np.asarray(mc.gen)
        cls.contract = cpt.closure_inference_contract(
            cls.meta, num_feat_reco=cls.reco.shape[-1], num_feat_gen=cls.gen.shape[-1],
            num_part=cls.reco.shape[1], coord_reco=cls.cr, coord_gen=cls.cg,
            loader_args=cls.loader_args, multifold_name="fe_powered",
            weights_folder=cls._td.name, step1_mc_normalization=fed.STEP1_MC_NORMALIZATION)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def test_normalization_is_the_loaders(self):
        for k in NORM_KEYS:
            self.assertEqual(self.contract[k], [float(x) for x in self.meta[k]], k)
            self.assertEqual(len(self.contract[k]),
                             self.meta["n_evt_reco" if k.startswith("reco") else "n_evt_truth"])

    def test_loader_args_reproduce_the_normalization(self):
        """The stored loader_args are sufficient: rebuilding from them gives the same statistics."""
        la = self.contract["loader_args"]
        with real_dataloader():
            *_, meta2 = fed.build_fullevent_loaders(la["inputs"], max_events=la["max_events"],
                                                    seed=la["seed"], bkg_mode=la["bkg_mode"])
        for k in NORM_KEYS:
            self.assertEqual([float(x) for x in meta2[k]], self.contract[k], k)

    def test_architecture_matches_what_main_builds(self):
        s1, s2 = self.contract["pet_arch_step1"], self.contract["pet_arch_step2"]
        self.assertEqual(s1["num_feat"], self.reco.shape[-1])
        self.assertEqual(s2["num_feat"], self.gen.shape[-1])
        self.assertEqual(s1["num_evt"], self.meta["n_evt_reco"])
        self.assertEqual(s2["num_evt"], self.meta["n_evt_truth"])
        self.assertEqual(s1["num_part"], self.reco.shape[1])
        self.assertEqual(s1["coord_idx"], [int(c) for c in self.cr])
        self.assertEqual(s2["coord_idx"], [int(c) for c in self.cg])
        for k, v in cpt.PET_ARCH_FIXED.items():
            self.assertEqual(s1[k], v)
            self.assertEqual(s2[k], v)

    def test_survives_the_artifact_round_trip(self):
        path = os.path.join(self._td.name, "art.npz")
        np.savez_compressed(path, inference_contract=np.asarray(self.contract, dtype=object))
        with np.load(path, allow_pickle=True) as z:
            self.assertEqual(z["inference_contract"].item(), self.contract)

    def test_missing_normalization_fails_closed(self):
        meta = dict(self.meta)
        del meta["truth_norm_std"]
        with self.assertRaises(SystemExit):
            cpt.closure_inference_contract(
                meta, num_feat_reco=1, num_feat_gen=1, num_part=1, coord_reco=[0],
                coord_gen=[0], loader_args={}, multifold_name="x", weights_folder=".",
                step1_mc_normalization=1.0)


class MainWiring(unittest.TestCase):
    """`main` needs TensorFlow and the 9.9 GB dump, so its wiring is checked on the AST."""

    @classmethod
    def setUpClass(cls):
        with open(cpt.__file__) as fh:
            tree = ast.parse(fh.read())
        cls.main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")

    def _calls(self, name):
        return [n for n in ast.walk(self.main) if isinstance(n, ast.Call)
                and (getattr(n.func, "id", None) == name or getattr(n.func, "attr", None) == name)]

    def test_both_networks_are_built_from_the_recorded_constants(self):
        pets = self._calls("PET")
        self.assertEqual(len(pets), 2)
        for call in pets:
            splats = [kw for kw in call.keywords if kw.arg is None]
            self.assertEqual([ast.unparse(kw.value) for kw in splats], ["PET_ARCH_FIXED"])
            self.assertFalse({kw.arg for kw in call.keywords} & set(cpt.PET_ARCH_FIXED),
                             "an architecture literal beside PET_ARCH_FIXED can drift from the "
                             "contract")

    def test_the_artifact_write_includes_the_contract(self):
        saves = self._calls("savez_compressed")
        self.assertEqual(len(saves), 1)
        self.assertIn("inference_contract", {kw.arg for kw in saves[0].keywords})


if __name__ == "__main__":
    unittest.main(verbosity=2)
