"""Controls for fd_gencmp_rebuild.py (FD-GENCMP-DECLARATION.md sections 1 and 3), on synthetic inputs. No real event,
product or pool is read; the only real file read is M4-W's committed probe_gen.json, for B2's reference counts.

gen_to_xsec5d imports ROOT at module import, so its pure-numpy and pure-Python functions (extract_gibuu, extract_nuwro
behind a fake ROOT, w_true, in_truth_phase_space, q3_true) are imported here with a stub ROOT module; the driver itself
imports without ROOT. The one case that needs real ROOT (a TMemFile over verified bytes) is skipped without it.

* n = z reproduces the generator kinematics bitwise: GENIE against MP-5's own events() (also for a drawn n, the axisonly
  build), NuWro against extract_nuwro through the MemROOT proxy, GiBUU against extract_gibuu; gibuu_density against
  mp3c_build.gibuu_density.
* the analysis W uses the struck-nucleon mass (or the fixed override), and W^2 < 0 entries are dropped before any
  histogram; the per-tag draws do not depend on which other samples drew.
* section 1: the O_NOATIME reader leaves atime unchanged and reports a moved atime; a mismatched or absent pin refuses;
  MemROOT refuses any ROOT read of an unverified path; --out that exists refuses before anything is read.
* B2's factor-2 rule in both directions, and its reference counts against probe_gen.json.
* a sample that fails B0 writes only its gen product and stops; the next sample still runs every variant."""
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
GENIE_DIR = REPO / "3d-unfolding" / "genie"
sys.path.insert(1, str(ND))
import fd_gencmp_kin as K  # noqa: E402
import fd_gencmp_rebuild as RB  # noqa: E402

RNG = np.random.default_rng(20261101)
G5 = None
try:
    import ROOT as _ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # noqa: BLE001
    HAVE_ROOT = False


def setUpModule():
    global G5
    with mock.patch.dict(sys.modules, {"ROOT": mock.MagicMock(name="ROOT stub")}):
        import gen_to_xsec5d
    G5 = gen_to_xsec5d


# ---------------------------------------------------------------- fixtures


def synthetic_part(n=400, hitnuc=None, seed=1):
    """A vectorised GiBUU-like part: lepton (px, py, pz) about +z, with a stored generator W."""
    r = np.random.default_rng(seed)
    p = r.uniform(1.0, 12.0, n)
    th = r.uniform(0.0, 0.4, n)
    ph = r.uniform(0, 2 * np.pi, n)
    px, py, pz = p * np.sin(th) * np.cos(ph), p * np.sin(th) * np.sin(ph), p * np.cos(th)
    emu = np.sqrt(p * p + K.M_MU ** 2)
    enu = emu + r.uniform(0.05, 3.0, n)
    Wg = r.uniform(0.9, 3.0, n)

    def ps(cc, pt, pzb):
        return cc & (pt <= 4.5) & (pzb >= 1.5) & (pzb <= 60) & (np.arctan2(pt, pzb) < np.radians(20))

    return RB.Part("main", np.ones(n, bool), enu, emu, r.uniform(0, 2, n), (px, py, pz), hitnuc, ps,
                   lambda sel, q, c, z: Wg[sel], lambda keep: np.full(keep.size, 0.5), None,
                   info={"Wg": Wg})


def synthetic_pools():
    out = []
    for b in range(6):
        a = RNG.uniform(0, 3e-3, 50)
        f = RNG.uniform(0, 2 * np.pi, 50)
        out.append(np.column_stack([np.sin(a) * np.cos(f), np.sin(a) * np.sin(f), np.cos(a), RNG.uniform(0.5, 2, 50)]))
    return out


def gibuu_text(n_ev=300, seed=3):
    """FinalEvents.dat rows (15 columns): a muon (pid 902), hadrons (1 = p, 101 = pi, 999), a perweight-0 target row;
    some events without a muon, some with a zero muon perweight."""
    r = np.random.default_rng(seed)
    rows = []
    for i in range(n_ev):
        run, ev = 1 + i // 100, i % 100
        enu = r.uniform(1.0, 18.0)
        p = r.uniform(0.5, enu * 0.9)
        th, ph = r.uniform(0.0, 0.5), r.uniform(0, 2 * np.pi)
        E = np.sqrt(p * p + 0.105658 ** 2)
        mu = [run, ev, 902, -1, 0.0 if i % 37 == 0 else r.uniform(0.1, 5.0), 0, 0, 0, E,
              p * np.sin(th) * np.cos(ph), p * np.sin(th) * np.sin(ph), p * np.cos(th), 0, 0, enu]
        if i % 23 != 0:
            rows.append(mu)
        for pid, ch, m in ((1, 1, 0.93827), (101, 1, 0.135), (101, 0, 0.135), (999, 0, 0.5), (1, 0, 0.9396)):
            if r.random() < 0.6:
                q = r.uniform(0, 1.0, 3)
                rows.append([run, ev, pid, ch, mu[4], 0, 0, 0, np.sqrt(m * m + q @ q), *q, 0, 0, enu])
        rows.append([run, ev, 1, 1, 0.0, 0, 0, 0, 0.93827, 0, 0, 0, 0, 0, enu])
    buf = io.StringIO()
    buf.write("# run event pid charge perweight x y z E px py pz hist prod Enu\n")
    np.savetxt(buf, np.array(rows), fmt="%.10g")
    return buf.getvalue()


def nuwro_flat(n=500, seed=5) -> dict:
    """nuwro_to_flat_5d.C's branches, with its W formula (fixed M_n, +z axis) and -9999 for entries without a muon."""
    r = np.random.default_rng(seed)
    p = r.uniform(1.0, 15.0, n)
    th = r.uniform(0.0, 0.45, n)
    Emu = np.sqrt(p * p + K.M_MU ** 2)
    Enu = Emu + r.uniform(0.05, 4.0, n)
    pt, pz = p * np.sin(th), p * np.cos(th)
    MN = 0.939565
    q2 = 4 * Enu * Emu * np.sin(th / 2) ** 2
    w2 = MN * MN + 2 * (Enu - Emu) * MN - q2
    W = np.where(w2 > 0, np.sqrt(np.maximum(w2, 0)), 0.0)
    q0 = Enu - Emu
    nomu = r.random(n) < 0.05
    pt, pz, W, q0 = (np.where(nomu, -9999.0, a) for a in (pt, pz, W, q0))
    return {"cc": (r.random(n) < 0.9).astype(np.int32), "pt": pt, "pz": pz, "eavail": r.uniform(0, 3, n), "W": W,
            "weight": np.full(n, 7.5e-39), "Enu": Enu, "Q2": q2, "q0": q0, "q3": r.uniform(0, 3, n),
            "dyn": r.integers(0, 9, n).astype(np.int32), "hitnuc": r.choice([2112, 2212], n).astype(np.int32)}


class FakeFile:
    def __init__(self, objs):
        self.objs = objs

    def Get(self, k):  # noqa: N802
        return self.objs.get(k)

    def Close(self):  # noqa: N802
        pass

    def IsZombie(self):  # noqa: N802
        return False


class FakeParam:
    def __init__(self, v):
        self.v = v

    def GetVal(self):  # noqa: N802
        return self.v


class FakeDF:
    def __init__(self, cols):
        self.cols = cols

    def Define(self, name, expr):  # noqa: N802
        return self

    def AsNumpy(self, cols):  # noqa: N802
        return {k: np.array(self.cols[k]) for k in cols}


class FakeROOT:
    """TMemFile over np.savez bytes (a 'nuwro_obs' tree and nTotal); a plain TFile.Open fails the test."""
    kError = 3000
    gErrorIgnoreLevel = 0

    class TFile:
        @staticmethod
        def Open(*a):  # noqa: N802
            raise AssertionError("a plain TFile.Open reached ROOT")

    def TMemFile(self, name, buf, size, option):  # noqa: N802
        assert option == "READ" and size == len(buf)
        with np.load(io.BytesIO(bytes(buf))) as z:
            cols = {k: z[k] for k in z.files if k != "nTotal"}
            nt = float(z["nTotal"])
        return FakeFile({"nuwro_obs": cols, "nTotal": FakeParam(nt)})

    def RDataFrame(self, tree):  # noqa: N802
        return FakeDF(tree)


class Tmp(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name).resolve()

    def tearDown(self):
        self._td.cleanup()

    def file(self, name, data: bytes) -> Path:
        p = self.tmp / name
        p.write_bytes(data)
        st = p.stat()
        os.utime(p, ns=(st.st_mtime_ns + 10**9, st.st_mtime_ns))    # atime after mtime: no relatime update
        return p


# ---------------------------------------------------------------- section 1


class Import(unittest.TestCase):
    def test_driver_imports_without_root(self):
        code = ("import sys; sys.dont_write_bytecode = True; sys.modules['ROOT'] = None; "
                f"sys.path.insert(0, {str(ND)!r}); import fd_gencmp_rebuild")
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class NoAtimeReader(Tmp):
    def test_atime_unchanged_and_digest(self):
        data = b"abc" * 1000
        p = self.file("f.dat", data)
        inp = RB.Inputs({str(p): hashlib.sha256(data).hexdigest()})
        self.assertEqual(inp.read(str(p)), data)
        rec = inp.records[-1]
        self.assertTrue(rec["atime_unchanged"] and rec["sha256_match"])
        self.assertEqual(rec["o_noatime"], hasattr(os, "O_NOATIME"))
        self.assertEqual(inp.deviations(), [])

    def test_moved_atime_is_reported_and_the_read_stands(self):
        data = b"xyz" * 100
        p = self.file("g.dat", data)
        real = RB._read_all

        def read_then_touch(fd):
            b = real(fd)
            st = os.stat(p)
            os.utime(p, ns=(st.st_atime_ns + 5 * 10**9, st.st_mtime_ns))   # what a plain open could do
            return b
        inp = RB.Inputs({str(p): hashlib.sha256(data).hexdigest()})
        with mock.patch.object(RB, "_read_all", read_then_touch):
            self.assertEqual(inp.read(str(p)), data)
        self.assertFalse(inp.records[-1]["atime_unchanged"])
        self.assertEqual(inp.deviations(), [str(p)])

    def test_pscratch_requires_o_noatime(self):
        p = self.file("h.dat", b"1")
        with mock.patch.object(RB, "PSCRATCH", str(self.tmp) + os.sep):
            if hasattr(os, "O_NOATIME"):
                self.assertTrue(RB.read_noatime(str(p))[1]["o_noatime"])
            else:
                with self.assertRaises(RB.InputRefused):
                    RB.read_noatime(str(p))


class Pins(Tmp):
    def test_mismatched_pin_refuses_and_is_logged(self):
        p = self.file("a.bin", b"data")
        inp = RB.Inputs({str(p): "0" * 64})
        with self.assertRaises(RB.InputRefused):
            inp.read(str(p))
        self.assertFalse(inp.records[-1]["sha256_match"])

    def test_unpinned_refuses_before_reading(self):
        p = self.file("b.bin", b"data")
        inp = RB.Inputs({})
        with self.assertRaises(RB.InputRefused):
            inp.read(str(p))
        self.assertEqual(inp.records, [])

    def test_read_pins_resolves_relative_and_refuses_conflicts(self):
        d1, d2 = "a" * 64, "b" * 64
        f = self.file("P.sha256", f"# c\n\n{d1}  /abs/x.root\n{d2}  rel/y.npz\n".encode())
        pins = RB.read_pins([f], root=self.tmp)
        self.assertEqual(pins, {"/abs/x.root": d1, str(self.tmp / "rel/y.npz"): d2})
        g = self.file("Q.sha256", f"{d2}  /abs/x.root\n".encode())
        with self.assertRaises(ValueError):
            RB.read_pins([f, g], root=self.tmp)
        h = self.file("R.sha256", b"nothex  /abs/z\n")
        with self.assertRaises(ValueError):
            RB.read_pins([h], root=self.tmp)

    def test_the_committed_inputs_file_parses(self):
        pins = RB.read_pins([RB.INPUTS])
        ctx = RB.Ctx(None, None, RB.Inputs(pins), (None, None, None))
        for name, n in (("nuwro_C12", (8, 1)), ("nuwro_H", (25, 5)), ("gibuu_C12", (80,)), ("gibuu_H", (80,)),
                        ("genie_cv", (1, 1)), ("genie_mec", (1, 1))):
            files = RB.sample_files(ctx, name)
            self.assertEqual(tuple(len(v) for v in files.values()), n, name)
            self.assertTrue(all(f in pins for v in files.values() for f in v), name)
        g = RB.sample_files(ctx, "gibuu_C12")["main"]
        self.assertEqual(g, sorted(g))
        self.assertTrue(g[1].endswith("task10/FinalEvents.dat"))      # sorted(glob) order, as the frozen build read
        self.assertIn(RB.gfr.DEFAULTS["gibuu_flux"], pins)              # pinned in INPUTS family B; no --allow-meta-pin
        for name, (path, _, _) in RB.TARGETS.items():
            self.assertIn(path, pins, name)
        for b in range(6):
            self.assertIn(os.path.join(RB.POOL_DIR, f"pool_b{b}.npy"), pins)

    def test_meta_pin_only_for_the_named_absent_path(self):
        inp = RB.Inputs({"/x": "a" * 64})
        inp.pin_from_meta("/y", {"path": "/other", "sha256": "b" * 64}, "s")
        inp.pin_from_meta("/x", {"path": "/x", "sha256": "c" * 64}, "s")
        self.assertEqual(inp.pins, {"/x": "a" * 64})
        inp.pin_from_meta("/y", {"path": "/y", "sha256": "b" * 64}, "s")
        self.assertEqual(inp.pins["/y"], "b" * 64)
        self.assertEqual(len(inp.meta_pins), 1)


class OutRefusal(Tmp):
    def test_existing_out_refuses_before_anything(self):
        out = self.tmp / "out"
        out.mkdir()
        (out / "keep").write_text("x")
        rc = RB.main(["--out", str(out)])          # valid default pins: only the --out rule can refuse
        self.assertEqual(rc, 2)
        self.assertEqual(sorted(os.listdir(out)), ["keep"])

    def test_unreadable_pins_refuse_without_creating_out(self):
        out = self.tmp / "new"
        self.assertEqual(RB.main(["--out", str(out), "--inputs", str(self.tmp / "absent.sha256")]), 2)
        self.assertFalse(out.exists())


class MemRootProxy(Tmp):
    def flat(self, name, d, n_total):
        b = io.BytesIO()
        np.savez(b, **d, nTotal=np.float64(n_total))
        return self.file(name, b.getvalue())

    def test_extract_nuwro_runs_on_verified_bytes_only(self):
        d = nuwro_flat()
        p = self.flat("flat5d_p1.root", d, 812.0)
        inp = RB.Inputs({str(p): hashlib.sha256(p.read_bytes()).hexdigest()})
        mem = RB.MemROOT(FakeROOT())
        mem.add(str(p), inp.read(str(p)))
        stub = G5.ROOT
        try:
            with mock.patch.dict(sys.modules, {"gen_to_xsec5d": G5}):
                self.assertIn("gen_to_xsec5d", RB.install_memroot(stub, mem, [GENIE_DIR]))
            self.assertIs(G5.ROOT, mem)
            ref, _, _ = G5.extract_nuwro([str(p)], [str(p)])
            arr, n_total = RB.nuwro_arrays(mem, [str(p)])
        finally:
            for m in list(sys.modules.values()) + [G5]:
                if getattr(m, "ROOT", None) is mem:
                    m.ROOT = stub
        self.assertEqual(n_total, float(ref["divisor"]))
        part = RB.nuwro_part("main", arr, G5, None, {"weight": arr["weight"]})
        keep, cols, cnt = RB.select(part)
        al = RB.alignment([part], {"main": (keep, cols)}, {"main": ref})
        self.assertEqual(set(al["main"]), {"pt", "pz", "eavail", "q3", "W", "weight_raw"})
        self.assertTrue(all(al["main"].values()), al)
        self.assertGreater(keep.size, 100)

    def test_refuses_unverified_and_write_opens(self):
        mem = RB.MemROOT(FakeROOT())
        with self.assertRaises(RB.InputRefused):
            mem.TFile.Open("/not/verified.root")
        with self.assertRaises(RB.InputRefused):
            mem.RDataFrame("nuwro_obs", "/not/verified.root")
        mem.add("/v.root", b"")
        with self.assertRaises(RB.InputRefused):
            mem.TFile.Open("/v.root", "RECREATE")
        with self.assertRaises(RB.InputRefused):
            mem.TFile("/v.root")
        mem.gErrorIgnoreLevel = 1
        self.assertEqual(mem._root.gErrorIgnoreLevel, 1)

    @unittest.skipUnless(HAVE_ROOT, "needs PyROOT (the root_6_28 env): TMemFile over verified bytes")
    def test_tmemfile_roundtrip(self):
        import array
        import ROOT
        src = self.tmp / "t.root"
        f = ROOT.TFile.Open(str(src), "RECREATE")
        t = ROOT.TTree("nuwro_obs", "")
        x = array.array("d", [0.0])
        t.Branch("pt", x, "pt/D")
        for v in (0.25, 1.5, 3.0):
            x[0] = v
            t.Fill()
        h = ROOT.TH1D("flux_numu", "", 3, array.array("d", [0, 1, 2, 4]))
        h.SetBinContent(2, 7.0)
        t.Write()
        h.Write()
        f.Close()
        data = src.read_bytes()
        inp = RB.Inputs({str(src): hashlib.sha256(data).hexdigest()})
        mem = RB.MemROOT(ROOT)
        mem.add(str(src), inp.read(str(src)))
        got = mem.RDataFrame("nuwro_obs", str(src)).AsNumpy(["pt"])["pt"]
        self.assertTrue(np.array_equal(got, [0.25, 1.5, 3.0]))
        e, c = RB.gfr.read_th1(mem, str(src), "flux_numu")
        self.assertTrue(np.array_equal(e, [0, 1, 2, 4]) and np.array_equal(c, [0, 7, 0]))


# ---------------------------------------------------------------- the variants


class Select(unittest.TestCase):
    def test_n_z_returns_the_generator_kinematics_bitwise(self):
        p = synthetic_part()
        px, py, pz = p.lepton
        for n in (None, K.unit_z(p.n)):
            keep, cols, cnt = RB.select(p, n)
            pt = np.hypot(px, py)
            self.assertTrue(np.array_equal(keep, np.flatnonzero(p.ps(p.cc, pt, pz))))
            self.assertTrue(np.array_equal(cols["pt"], pt[keep]) and np.array_equal(cols["pz"], pz[keep]))
            self.assertTrue(np.array_equal(cols["W"], p.info["Wg"][keep]))

    def test_stored_pt_without_azimuth_is_kept_bitwise(self):
        p = synthetic_part()
        px, py, pz = p.lepton
        pt = np.hypot(px, py)
        p.lepton = (pt, None, pz)
        keep, cols, _ = RB.select(p)
        self.assertTrue(np.array_equal(cols["pt"], pt[keep]))
        phi = RNG.uniform(0, 2 * np.pi, p.n)
        keep2, cols2, _ = RB.select(p, K.unit_z(p.n), phi)
        np.testing.assert_allclose(cols2["pt"], pt[keep2], rtol=1e-15)

    def test_analysis_W_uses_the_struck_mass_and_drops_negative_W2(self):
        n = 4
        cc = np.ones(n, bool)
        enu, emu = np.array([5.0, 5.0, 5.0, 10.0]), np.array([3.0, 3.0, 3.0, 9.5])
        th = np.array([0.1, 0.1, 0.1, 0.3])
        p = np.sqrt(emu ** 2 - K.M_MU ** 2)
        lep = (p * np.sin(th), np.zeros(n), p * np.cos(th))
        hit = np.array([2112, 2212, 0, 2112])
        part = RB.Part("main", cc, enu, emu, np.zeros(n), lep, hit, lambda c, a, b: c,
                       lambda s, q, c, z: np.ones(s.size), lambda k: np.zeros(k.size), None)
        keep, cols, cnt = RB.select(part, w="ana")
        self.assertEqual(keep.tolist(), [0, 1, 2])
        self.assertEqual(cnt["n_W2_negative_dropped"], 1)
        self.assertFalse(np.isnan(cols["W"]).any())
        c = K.beam_frame(*lep, K.unit_z(n))[2]
        want = [K.w_analysis(enu[i], emu[i], c[i], m) for i, m in enumerate((K.CVU_M_N, K.CVU_M_P, K.CVU_M_NUCLEON))]
        np.testing.assert_array_equal(cols["W"], np.array(want, float))
        part.hitnuc = None
        _, cols, _ = RB.select(part, w="ana")
        np.testing.assert_array_equal(cols["W"], K.w_analysis(enu[:3], emu[:3], c[:3], K.CVU_M_NUCLEON))
        _, cols, _ = RB.select(part, w="ana", m_fixed=K.CVU_M_N)
        np.testing.assert_array_equal(cols["W"], K.w_analysis(enu[:3], emu[:3], c[:3], K.CVU_M_N))

    def test_dropped_entries_never_reach_the_histogram(self):
        p = synthetic_part(hitnuc=np.full(400, 2112))
        p.emu = p.enu - 0.01      # makes W^2 < 0 for every entry with a sizeable angle
        keep, cols, cnt = RB.select(p, w="ana")
        self.assertGreater(cnt["n_W2_negative_dropped"], 0)
        self.assertEqual(keep.size + cnt["n_W2_negative_dropped"], cnt["n_in_ps"])
        self.assertTrue(np.isfinite(cols["W"]).all())

    def test_draws_are_per_tag_and_independent_of_other_samples(self):
        pools = synthetic_pools()
        p = synthetic_part()
        p.enu = RNG.uniform(0.5, 60.0, p.n)
        p.cc = RNG.random(p.n) < 0.8
        a, phi_a = RB.directions("genie_cv", p, K.SEEDS[0], pools)
        RB.directions("nuwro_C12", p, K.SEEDS[0], pools)
        b, phi_b = RB.directions("genie_cv", p, K.SEEDS[0], pools)
        self.assertTrue(np.array_equal(a, b) and np.array_equal(phi_a, phi_b))
        c, _ = RB.directions("nuwro_C12", p, K.SEEDS[0], pools)
        d, _ = RB.directions("genie_cv", p, K.SEEDS[1], pools)
        self.assertFalse(np.array_equal(a[p.cc], c[p.cc]) or np.array_equal(a[p.cc], d[p.cc]))
        self.assertTrue(np.array_equal(a[~p.cc], K.unit_z(int((~p.cc).sum()))))

    def test_variant_list(self):
        names = [v.name for v in RB.variants("gibuu_C12")]
        self.assertEqual(names, ["gen", "wonly"] + [f"ana_s{s}" for s in K.SEEDS] + ["axisonly", "ana_mn"])
        self.assertNotIn("ana_mn", [v.name for v in RB.variants("gibuu_H")])
        v = {x.name: x for x in RB.variants("gibuu_C12")}
        self.assertEqual((v["axisonly"].seed, v["axisonly"].w), (K.SEEDS[0], "gen"))
        self.assertEqual((v["ana_mn"].seed, v["ana_mn"].m_fixed), (K.SEEDS[0], K.CVU_M_N))
        self.assertEqual((v["wonly"].seed, v["wonly"].w), (None, "ana"))


class FrozenParity(unittest.TestCase):
    """The restated readers against the frozen statements, bitwise."""

    def genie_arrays(self, n=600):
        r = np.random.default_rng(9)
        p = r.uniform(0.5, 20.0, n)
        th, ph = r.uniform(0, 0.5, n), r.uniform(0, 2 * np.pi, n)
        El = np.sqrt(p * p + K.M_MU ** 2)
        Ev = El + r.uniform(0.01, 5.0, n)
        return {"cc": (r.random(n) < 0.9).astype(np.int32), "mec": (r.random(n) < 0.1).astype(np.int32), "Ev": Ev,
                "pxv": np.zeros(n), "pyv": np.zeros(n), "pzv": Ev.copy(), "El": El,
                "pxl": p * np.sin(th) * np.cos(ph), "pyl": p * np.sin(th) * np.sin(ph), "pzl": p * np.cos(th),
                "Q2": np.zeros(n), "hitnuc": r.choice([2112, 2212, 2000000200], n).astype(np.int32),
                "eav5d": r.uniform(0, 3, n)}

    def test_genie_equals_mp5_events_for_z_and_drawn_n(self):
        d = self.genie_arrays()
        fake = mock.MagicMock()
        fake.RDataFrame.return_value = FakeDF(d)
        part = RB.genie_part("main", d, G5, None, {})
        drawn = K.unit_z(part.n)
        drawn[part.cc] = K.draw_directions(RNG.random(int(part.cc.sum())), part.enu[part.cc], synthetic_pools(),
                                           K.ENU_BINS_GEV)
        for n in (None, drawn):
            ev, info = RB.mp5.events(fake, G5, "gst", n)
            keep, cols, _ = RB.select(part, n)
            self.assertTrue(np.array_equal(keep, info["sel"]))
            for k in ("pt", "pz", "eavail", "q3", "W"):
                self.assertTrue(np.array_equal(cols[k], ev[k]), k)
        self.assertTrue(part.info["nu_along_z"])

    def test_gibuu_equals_extract_gibuu(self):
        text = gibuu_text()
        e = RB.gibuu_entries(G5, np.loadtxt(io.StringIO(text), comments="#"))
        part = RB.gibuu_part("main", e, G5, None, None, None, {"weight": e["w"]})
        keep, cols, _ = RB.select(part)
        ref, _, _ = G5.extract_gibuu([io.StringIO(text)])
        al = RB.alignment([part], {"main": (keep, cols)}, {"main": ref})["main"]
        self.assertEqual(set(al), {"pt", "pz", "eavail", "q3", "W", "weight_raw"})
        self.assertTrue(all(al.values()), al)
        self.assertGreater(keep.size, 50)
        self.assertLess(e["w"].size, 300)        # events without a muon or with zero perweight are not entries

    def test_gibuu_density_equals_mp3c(self):
        with tempfile.TemporaryDirectory() as td:
            E = np.arange(0.025, 30.0, 0.05)
            flux = Path(td) / "flux.dat"
            np.savetxt(flux, np.column_stack([E, np.exp(-E / 4.0)]), header="E flux")
            job = Path(td) / "job"
            job.write_text("&neutrino_induced\n Enu_lower_cut = 0.2 ! lo\n Enu_upper_cut = 20.0\n/\n")
            with mock.patch.dict(RB.gfr.DEFAULTS, {"gibuu_flux": str(flux)}):
                want = RB.mp3c.gibuu_density(str(job))
            got = RB.gibuu_density(flux.read_text(), job.read_text())
        for a, b in zip(got, want):
            self.assertTrue(np.array_equal(np.asarray(a), np.asarray(b)))

    def test_parts_add_in_order(self):
        def builder(scale):
            def build(keep, cols):
                n = G5.hist([cols[a] for a in G5.AXES], None, [G5.EDGES[a] for a in G5.AXES]).reshape(-1)
                return n * scale, n * scale ** 2, n
            return build
        a, b = synthetic_part(seed=2), synthetic_part(seed=4)
        a.build, b.build, b.name = builder(0.3), builder(0.7), "supp"
        x, v, n, counts, _ = RB.assemble("s", [a, b], RB.Variant("gen", None, "gen"), None, {})
        xa, va, na = a.build(*RB.select(a)[:2])
        xb, vb, nb = b.build(*RB.select(b)[:2])
        self.assertTrue(np.array_equal(x, xa + xb) and np.array_equal(v, va + vb) and np.array_equal(n, na + nb))
        self.assertEqual(set(counts), {"main", "supp"})


# ---------------------------------------------------------------- B1, B2 and the run


class B2(unittest.TestCase):
    def test_factor_two_both_directions(self):
        ref = (29, 938141)
        f = ref[0] / ref[1]
        for ratio, ok in ((1.0, True), (2.0, True), (0.5, True), (2.05, False), (0.48, False)):
            n_ps = 10**8
            r = RB.b2_rule(int(round(ratio * f * n_ps)), n_ps, ref)
            self.assertEqual(r["pass"], ok, (ratio, r))
        self.assertFalse(RB.b2_rule(0, 938141, ref)["pass"])
        self.assertTrue(RB.b2_rule(2, 100, (1, 100))["pass"] and RB.b2_rule(1, 200, (1, 100))["pass"])
        self.assertFalse(RB.b2_rule(201, 10000, (1, 100))["pass"] or RB.b2_rule(49, 10000, (1, 100))["pass"])

    def test_reference_counts_are_m4ws(self):
        d = json.loads((REPO / "docs/orchestration/state/2d-closeout/stageF/methods/m4-w/probe_gen.json").read_text())
        for name, key in (("genie_cv", "genie_cv"), ("nuwro_C12", "nuwro")):
            self.assertEqual(RB.M4W_REF[name], (d[key]["n_W_nan_analysis"], d[key]["n_events_in_ps"]))


class B1(unittest.TestCase):
    def test_alpha_summary(self):
        pools = synthetic_pools()
        s = RB.b1_summary(pools)
        a = np.concatenate([1e3 * np.arctan2(np.hypot(P[:, 0], P[:, 1]), P[:, 2]) for P in pools])
        self.assertAlmostEqual(s["all_bins"]["unweighted"]["median"], float(np.median(a)))
        self.assertEqual(len(s["per_bin"]), 6)
        self.assertEqual(s["mp5_recorded"]["median"], 1.03)


class WriteVariant(Tmp):
    def test_keys_dtype_shape(self):
        x = np.arange(RB.N_FINE, dtype=float)
        info = RB.write_variant(self.tmp, "s", "gen", x, x, x, {"a": np.int64(1)})
        with np.load(info["path"], allow_pickle=False) as z:
            self.assertEqual(sorted(z.files), ["meta_json", "nevt_flat", "sumw2_flat", "xsec_flat"])
            self.assertEqual(z["xsec_flat"].shape, (RB.N_FINE,))
            self.assertEqual(json.loads(str(z["meta_json"]))["a"], 1)
        with self.assertRaises(ValueError):
            RB.write_variant(self.tmp, "s", "bad", x[:10], x, x, {})


class RunSamples(Tmp):
    """A sample failing B0 writes only gen and stops; the next one runs every variant and B2 is recorded."""

    def test_b0_failure_stops_only_that_sample(self):
        def loader(ctx, name, files, tmeta):
            p = synthetic_part(hitnuc=np.full(400, 2112))

            def build(keep, cols):
                n = G5.hist([cols[a] for a in G5.AXES], None, [G5.EDGES[a] for a in G5.AXES]).reshape(-1)
                return n * 1e-40, n * 1e-80, n
            p.build = build
            keep, cols, _ = RB.select(p)
            ref = {k: v.copy() for k, v in cols.items()}
            if name == "bad":
                ref["pt"][0] += 1e-12
            return [p], {"main": ref}, {}
        ctx = RB.Ctx(G5, RB.MemROOT(FakeROOT()), RB.Inputs({}), (None, None, None))
        run = RB.Run(ctx, self.tmp, "/none")
        with mock.patch.dict(RB.LOADERS, {"bad": loader, "good": loader}), \
                mock.patch.object(RB, "sample_files", lambda c, n: {"main": []}), \
                mock.patch.object(RB.Run, "load_pools", lambda self: synthetic_pools()):
            self.assertFalse(run.sample("bad"))
            self.assertTrue(run.sample("good"))
        files = sorted(os.listdir(self.tmp))
        self.assertEqual([f for f in files if f.startswith("bad_")], ["bad_gen.npz"])
        self.assertEqual(len([f for f in files if f.startswith("good_")]), len(RB.variants("good")))
        self.assertEqual(run.res["samples"]["bad"]["stage"], "B0")
        self.assertFalse(run.res["B0"]["bad"]["pass"])
        self.assertTrue(run.res["B0"]["good"]["pass"])
        self.assertIn("good", run.res["B2"])


if __name__ == "__main__":
    unittest.main()
