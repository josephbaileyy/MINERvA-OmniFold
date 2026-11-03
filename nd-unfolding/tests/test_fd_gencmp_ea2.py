"""Controls for GENCMP amendment E's addendum E-A2 (FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2.md): the gencmp-chdefs set's
legend and K7 strings without the two hydrogen flags, control D in both directions, and the redraw end to end from
amendment E's committed E-1 with-arm bytes."""
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_g_figures as FG  # noqa: E402
import fd_g_figures_check as FC  # noqa: E402
import fd_gencmp_e as E  # noqa: E402
import fd_gencmp_ea2 as A2  # noqa: E402

REPO = ND.parent
FLAGS = ("hydrogen: supplement FLAGGED", "hydrogen: closure B3 failed")


class Sets(unittest.TestCase):
    def test_the_flags_leave_the_legend_and_k7s_required_strings(self):
        quals, required = FG.PREDICTION_SETS["gencmp-chdefs"]
        names, must = FC.PREDICTION_SETS["gencmp-chdefs"]
        for f in FLAGS:
            self.assertFalse(any(f in q for v in quals.values() for q in v), f)
            self.assertNotIn(f, required)
            self.assertFalse(any(f in v for v in names.values()), f)
            self.assertNotIn(f, must)

    def test_what_the_legend_keeps(self):
        quals, required = FG.PREDICTION_SETS["gencmp-chdefs"]
        self.assertEqual(quals["nuwro"], ("CH",))
        self.assertEqual(quals["gibuu"], ("CH", "p_parallel < 4.5 cells only"))
        self.assertEqual(quals["mnvtune_v1"], ("prior (not an independent prediction)",))
        self.assertEqual(set(required), {"prior (not an independent prediction)", "p_parallel < 4.5 cells only"})
        names, _ = FC.PREDICTION_SETS["gencmp-chdefs"]
        self.assertEqual(names["nuwro"], "NuWro 21.09: CH")
        self.assertEqual(names["gibuu"], "GiBUU 2019: CH; $p_\\parallel$ < 4.5 cells only")

    def test_the_labels_still_carry_the_flags(self):
        # the facts move to Table III's footnote and the note; the readouts' labels are unchanged
        self.assertIn(FLAGS[0], E.CHDEFS[2]["label"])
        self.assertIn(FLAGS[1], E.CHDEFS[3]["label"])

    def test_stage_gs_set_is_unchanged(self):
        self.assertIs(FG.PREDICTION_SETS["stage-g"][0], FG.QUALIFIERS)
        self.assertIs(FC.PREDICTION_SETS["stage-g"][0], FC.NAMES)


def sidecar(text_nuwro="NuWro 21.09: CH; hydrogen: supplement FLAGGED"):
    return {"schema": "s", "labels": {}, "figure": "ratio", "file": "a.pdf", "pdf_sha256": "0", "pdf_bytes": 1,
            "controls_passed": ["K0"], "inputs_sha256": {"g_readout": "1"}, "code": {}, "versions": {}, "argv": ["x"],
            "options": {"prediction_set": "gencmp-chdefs"},
            "plotted": {"figure": "ratio", "legends": [{"n": 5}], "items": [
                {"gid": "ratio:nuwro:line", "kind": "line", "x": [0.0, 1.0], "y": [1.1, 0.9]},
                {"gid": "ratio:nuwro:legend", "kind": "legend",
                 "source": ["fd_g_readout.json predictions[name=nuwro].label"], "text": text_nuwro}]}}


class ControlD(unittest.TestCase):
    def test_holds_when_only_the_flag_leaves_the_label_text(self):
        old, new = sidecar(), sidecar("NuWro 21.09: CH")
        new.update(argv=["y"], code={"a": 1}, versions={"m": 2}, pdf_sha256="9", pdf_bytes=7, file="b.pdf")
        bad, changed = A2.control_d(old, new)
        self.assertEqual((bad, changed), ([], 1))

    def test_fails_on_a_changed_number_a_changed_option_or_another_text(self):
        old = sidecar()
        for mutate in (lambda d: d["plotted"]["items"][0]["y"].__setitem__(0, 1.1000001),
                       lambda d: d["options"].__setitem__("prediction_set", "stage-g"),
                       lambda d: d["plotted"]["legends"][0].__setitem__("n", 4),
                       lambda d: d["plotted"]["items"][1].__setitem__("text", "NuWro 21.09"),
                       lambda d: d["plotted"]["items"].pop(0)):
            new = sidecar("NuWro 21.09: CH")
            mutate(new)
            bad, _ = A2.control_d(old, new)
            self.assertTrue(bad)

    def test_counts_no_change_when_the_flag_stays(self):
        bad, changed = A2.control_d(sidecar(), sidecar())
        self.assertTrue(bad)            # the new text still carries the flag
        self.assertEqual(changed, 0)


class Redraw(unittest.TestCase):
    def test_redraws_from_the_committed_bytes_and_every_control_passes(self):
        tmp = Path(tempfile.mkdtemp(prefix="ea2-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = A2.main(["--out-dir", str(tmp / "fig")])
        self.assertEqual(rc, 0, err.getvalue()[-2000:])
        rec = json.loads((tmp / "fig/control_d.json").read_text())
        self.assertTrue(rec["pass"])
        self.assertEqual({n: r["label_texts_changed"] for n, r in rec["figures"].items()},
                         {"fd_g_fig_ratio": 2, "fd_g_fig_modes": 1, "fd_g_fig_sens": 2})

    def test_refuses_an_existing_out_dir_and_a_changed_input(self):
        tmp = Path(tempfile.mkdtemp(prefix="ea2-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(A2.main(["--out-dir", str(tmp)]), 2)
        d = tmp / "deploy"
        for rel in (A2.PINS_FILE, A2.PREDS_FILE, *(r for _, r, _ in A2.INPUT_ARGS),
                    *(f"{A2.COMMITTED_FIGS}/{n}.json" for n in A2.FIG_NAMES)):
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, d / rel)
        p = d / A2.INPUT_ARGS[0][1]
        p.write_text(p.read_text().replace("GENIE", "GENIE ", 1))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(A2.main(["--out-dir", str(tmp / "fig"), "--deploy", str(d)]), 2)
        self.assertIn("is not the committed figure step's g_readout", err.getvalue())
        self.assertFalse((tmp / "fig").exists())


class RedrawRefusals(unittest.TestCase):
    def deploy_copy(self, tmp):
        d = tmp / "deploy"
        for rel in (A2.PINS_FILE, A2.PREDS_FILE, *(r for _, r, _ in A2.INPUT_ARGS),
                    *(f"{A2.COMMITTED_FIGS}/{n}.json" for n in A2.FIG_NAMES)):
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, d / rel)
        return d

    def test_fails_when_no_label_text_changes(self):
        tmp = Path(tempfile.mkdtemp(prefix="ea2-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        d = self.deploy_copy(tmp)
        p = d / A2.COMMITTED_FIGS / "fd_g_fig_modes.json"
        rec = json.loads(p.read_text())
        for it in rec["plotted"]["items"]:
            if A2.label_item(it) and isinstance(it.get("text"), str):
                for h in A2.HYDROGEN:
                    it["text"] = it["text"].replace(h, "")
        p.write_text(json.dumps(rec))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = A2.main(["--out-dir", str(tmp / "fig"), "--deploy", str(d)])
        self.assertEqual(rc, 1)
        res = json.loads((tmp / "fig/control_d.json").read_text())["figures"]["fd_g_fig_modes"]
        self.assertEqual((res["pass"], res["label_texts_changed"], res["differences"]), (False, 0, []))

    def test_fails_when_the_figure_check_fails(self):
        from unittest import mock
        tmp = Path(tempfile.mkdtemp(prefix="ea2-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        real = A2.subprocess.run
        calls = []

        def run(cmd, *a, **k):
            calls.append(cmd)
            if any(str(x).endswith("fd_g_figures_check.py") for x in cmd):
                return A2.subprocess.CompletedProcess(cmd, 1)
            return real(cmd, *a, **k)
        with mock.patch.object(A2.subprocess, "run", run), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = A2.main(["--out-dir", str(tmp / "fig")])
        self.assertEqual(rc, 1)
        self.assertEqual(len(calls), 2)
        self.assertFalse((tmp / "fig/control_d.json").exists())


if __name__ == "__main__":
    unittest.main()
