"""ROOT-free power tests for BEN-106 construction-contract propagation."""

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "adopt_unified_5d.py"
SPEC = importlib.util.spec_from_file_location("adopt_unified_5d_contract_test", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeParameter:
    def __init__(self, value):
        self.value = value

    def GetVal(self):
        return self.value


class FakeHistogram:
    def __init__(self, bins, writes=None):
        self.bins = bins
        self.directory = "source"
        self.writes = [] if writes is None else writes

    def GetNbinsX(self):
        return self.bins

    def Clone(self, _name):
        return FakeHistogram(self.bins, self.writes)

    def SetDirectory(self, directory):
        self.directory = directory

    def Write(self, name):
        self.writes.append(("histogram", name, self.bins))


class FakeFile:
    def __init__(self, objects):
        self.objects = objects

    def Get(self, name):
        return self.objects.get(name)


class FakeWritableParameter:
    def __init__(self, writes, kind, name, value):
        self.writes = writes
        self.kind = kind
        self.name = name
        self.value = value

    def Write(self):
        self.writes.append((self.kind, self.name, self.value))


class FakeRoot:
    def __init__(self, writes):
        self.writes = writes

    def TParameter(self, kind):
        return lambda name, value: FakeWritableParameter(self.writes, kind, name, value)


def valid_objects(bins=4):
    return {
        "fixed_seed_null_norm": FakeParameter(1.0e-50),
        "joint_mean_shift_norm": FakeParameter(2.0e-38),
        "n_throws": FakeParameter(160),
        "hJointMeanShift": FakeHistogram(bins),
    }


class ConstructionContractTests(unittest.TestCase):
    def test_contract_reader_fails_closed_on_every_missing_item(self):
        for missing in (
            "fixed_seed_null_norm",
            "joint_mean_shift_norm",
            "n_throws",
            "hJointMeanShift",
        ):
            with self.subTest(missing=missing):
                objects = valid_objects()
                del objects[missing]
                with self.assertRaisesRegex(ValueError, missing):
                    MODULE._read_construction_contract(FakeFile(objects), expected_bins=4)

    def test_contract_reader_rejects_mean_shift_dimension_mismatch(self):
        with self.assertRaisesRegex(
            ValueError, "hJointMeanShift bins 3 != covariance bins 4"
        ):
            MODULE._read_construction_contract(
                FakeFile(valid_objects(bins=3)), expected_bins=4
            )

    def test_contract_round_trip_writes_all_parameters_and_detached_histogram(self):
        values, mean_shift = MODULE._read_construction_contract(
            FakeFile(valid_objects()), expected_bins=4
        )
        self.assertEqual(mean_shift.directory, 0)

        writes = mean_shift.writes
        MODULE._write_construction_contract(FakeRoot(writes), values, mean_shift)
        self.assertEqual(
            writes,
            [
                ("double", "fixed_seed_null_norm", 1.0e-50),
                ("double", "joint_mean_shift_norm", 2.0e-38),
                ("int", "n_throws", 160),
                ("histogram", "hJointMeanShift", 4),
            ],
        )


if __name__ == "__main__":
    unittest.main()
