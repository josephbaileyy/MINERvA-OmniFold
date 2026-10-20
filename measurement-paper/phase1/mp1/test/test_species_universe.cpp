// Unit test of SpeciesResponseUniverse.h and the patch's convention parser against a mock CVUniverse.
// Build and run (no MAT/ROOT needed): bash measurement-paper/phase1/mp1/test/run_test.sh
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>

#include "event/SpeciesResponseUniverse.h"

#include "parser_extracted.inc"  // ParseSpeciesResponseConventions, cut from the patched event loop

namespace {
int g_fail = 0;

void Check(bool ok, const std::string& what) {
  std::printf("%s  %s\n", ok ? "PASS" : "FAIL", what.c_str());
  if (!ok) ++g_fail;
}

bool Close(double a, double b, double rel = 1e-12) { return std::fabs(a - b) <= rel * std::fmax(1.0, std::fabs(b)); }

double RecoveredQ0(const CVUniverse& u) {
  const double q3 = u.RecoQ3(), w = u.RecoW();
  return std::sqrt(q3 * q3 + w * w) - CVUniverse::M_nucleon;
}

PlotUtils::ChainWrapper MakeEvent() {
  PlotUtils::ChainWrapper c;
  auto& s = c.scalars;
  s["Emu"] = 5000.0;
  s["Pmu"] = 4998.9;
  s["Thetamu"] = 0.12;
  s["MasterAnaDev_recoil_E"] = 1500.0;
  const char* blob[] = {"p", "meson", "em", "other", "lown", "midn", "highn", "xtalk", "mu"};
  const double trk[] = {300.0, 250.0, 100.0, 20.0, 5.0, 6.0, 30.0, 25.0, 40.0};
  const double ecal[] = {30.0, 60.0, 80.0, 0.0, 0.0, 1.0, 10.0, 12.0, 15.0};
  double ttot = 0.0, etot = 0.0;
  for (int i = 0; i < 9; ++i) {
    s[std::string("blob_recoil_E_tracker_") + blob[i]] = trk[i];
    s[std::string("blob_recoil_E_ecal_") + blob[i]] = ecal[i];
    ttot += trk[i];
    etot += ecal[i];
  }
  s["blob_recoil_E_tracker"] = ttot;
  s["blob_recoil_E_ecal"] = etot;
  double v = 50.0;
  for (const char* p : species_response::kPartSpecies) {
    s[std::string("part_response_recoil_allNonMuonClusters_") + p + "_id"] = v;
    s[std::string("part_response_recoil_allNonMuonClusters_") + p + "_od"] = 0.1 * v;
    v += 37.0;
  }
  s["part_response_recoil_allNonMuonClusters_other_od"] = -1.0;  // a tuple default: must count as 0
  c.fuzz_ids = {1504968705 + 10, 1700003841 + 10, 1400000000};
  c.fuzz_e = {45.0, 7.0, 999.0};  // the third plane is outside both windows
  return c;
}

double PartIDOD(const PlotUtils::ChainWrapper& c, const std::string& p) {
  const auto& s = c.scalars;
  const double id = s.at("part_response_recoil_allNonMuonClusters_" + p + "_id");
  const double od = s.at("part_response_recoil_allNonMuonClusters_" + p + "_od");
  return (id > 0 ? id : 0) + (od > 0 ? od : 0);
}
}  // namespace

std::shared_ptr<const species_response::PiecewiseLinearMap> WriteAndLoad(const std::string& path, const std::string& text) {
  FILE* f = std::fopen(path.c_str(), "w");
  std::fputs(text.c_str(), f);
  std::fclose(f);
  return species_response::PiecewiseLinearMap::Load(path);
}

bool Throws(const std::string& path, const std::string& text) {
  try { WriteAndLoad(path, text); } catch (const std::exception&) { return true; }
  return false;
}

int main(int argc, char** argv) {
  using species_response::FuzzConvention;
  using species_response::Q0Convention;
  const std::string tmp = argc > 1 ? argv[1] : ".";
  // A two-segment F with the S0 1A slopes: 1.4995567 below 695.74, 1.6067805 above.
  auto F = WriteAndLoad(tmp + "/F_test.txt", "# test\n0 0\n695.73894425207516 1043.3000000000095\n2000 3139.0\n");
  Check(F->Size() == 3 && std::fabs((*F)(100.0) - 149.95567) < 1e-3, "F table: loads and interpolates");
  Check(std::fabs((*F)(3000.0) - (3139.0 + 1000.0 * (3139.0 - 1043.3000000000095) / (2000 - 695.73894425207516))) < 1e-9,
        "F table: extends beyond the last knot with the end slope");
  Check(Throws(tmp + "/F_bad1.txt", "0 0\n10 5\n5 6\n"), "F table: non-increasing x refused");
  Check(Throws(tmp + "/F_bad2.txt", "0 0\n10 5\n20 4\n"), "F table: decreasing y refused");
  Check(Throws(tmp + "/F_bad3.txt", "0 0\n"), "F table: one knot refused");
  Check(Throws(tmp + "/F_bad4.txt", "0 0\n10 5 7\n"), "F table: malformed line refused");

  PlotUtils::ChainWrapper ev = MakeEvent();
  CVUniverse cv(&ev);
  double pc = 0.0;
  for (const char* p : species_response::kPartSpecies) pc += PartIDOD(ev, p);
  ev.scalars["MasterAnaDev_recoil_E"] = (*F)(pc);  // an event on the map, as G0 shows for selected 1A events
  const double E0 = cv.NewEavail(), q0 = ev.scalars["MasterAnaDev_recoil_E"];
  const double raw = ev.scalars["blob_recoil_E_tracker"] + ev.scalars["blob_recoil_E_ecal"];
  const double fuzz = 45.0 + 7.0;

  for (auto qc : {Q0Convention::kLegacyAbsolute, Q0Convention::kFractional, Q0Convention::kFPropagation}) {
    for (auto fc : {FuzzConvention::kProRata, FuzzConvention::kNone, FuzzConvention::kAll}) {
      SpeciesResponseUniverse zero(&ev, 0.0, species_response::kProton, qc, fc, F);
      Check(zero.NewEavail() == cv.NewEavail() && zero.RecoQ3() == cv.RecoQ3() && zero.RecoW() == cv.RecoW(),
            "k = 0 reproduces CVUniverse bit for bit (q0 conv " + std::to_string(int(qc)) + ", fuzz conv " +
                std::to_string(int(fc)) + ")");
    }
  }
  bool threw = false;
  try { SpeciesResponseUniverse u(&ev, 1.0, species_response::kProton, Q0Convention::kFPropagation, FuzzConvention::kProRata); }
  catch (const std::invalid_argument&) { threw = true; }
  Check(threw, "F-propagation without a table is refused");

  for (const auto& sp : species_response::kAll) {
    const std::string b(sp.blob), lab(sp.label);
    const double e_s = ev.scalars["blob_recoil_E_tracker_" + b] + ev.scalars["blob_recoil_E_ecal_" + b];
    const double pc_s = PartIDOD(ev, sp.part);
    for (double ns : {-1.0, +1.0}) {
      const double k = ns * sp.delta;
      const std::string tag = lab + " " + std::to_string(int(ns)) + "s: ";
      SpeciesResponseUniverse n(&ev, ns, sp, Q0Convention::kLegacyAbsolute, FuzzConvention::kNone, F);
      SpeciesResponseUniverse r(&ev, ns, sp, Q0Convention::kFractional, FuzzConvention::kProRata, F);
      SpeciesResponseUniverse a(&ev, ns, sp, Q0Convention::kFPropagation, FuzzConvention::kAll, F);
      Check(Close(n.NewEavail(), E0 + k * 1.17 * e_s), tag + "E_avail, fuzz none");
      Check(Close(r.NewEavail(), E0 + k * E0 * e_s / raw), tag + "E_avail, fuzz pro-rata");
      Check(Close(a.NewEavail(), E0 + k * 1.17 * (e_s - std::fmin(e_s, fuzz))), tag + "E_avail, fuzz all");
      Check(Close(RecoveredQ0(n), q0 + k * pc_s, 1e-10), tag + "q0 legacy = q0 + k pc_s");
      Check(Close(RecoveredQ0(r), q0 * (1.0 + k * pc_s / pc), 1e-10), tag + "q0 fractional = q0 (1 + k pc_s/pc)");
      Check(Close(RecoveredQ0(a), (*F)(pc + k * pc_s), 1e-10), tag + "q0 fprop = F(pc + k pc_s)");
      Check(a.ShortName() == "SpeciesResponse_" + lab && !a.IsVerticalOnly(), lab + ": name and lateral flag");
    }
  }
  // pc of the test event straddles the knot for the large shifts: F-propagation must differ from fractional there.
  SpeciesResponseUniverse fo(&ev, +1.0, species_response::kOther, Q0Convention::kFPropagation, FuzzConvention::kProRata, F);
  SpeciesResponseUniverse fr(&ev, +1.0, species_response::kOther, Q0Convention::kFractional, FuzzConvention::kProRata, F);
  std::printf("INFO  pc = %.3f MeV, q0 = %.3f MeV; other +1s: dq0 fprop %.6f, fractional %.6f\n", pc, q0,
              RecoveredQ0(fo) - q0, RecoveredQ0(fr) - q0);

  // The parser cut from the patch.
  bool en = true;
  Q0Convention q = Q0Convention::kLegacyAbsolute;
  FuzzConvention z = FuzzConvention::kAll;
  std::string err;
  Check(ParseSpeciesResponseConventions(nullptr, nullptr, en, q, z, err) && !en, "parser: both unset -> disabled");
  Check(ParseSpeciesResponseConventions("", "", en, q, z, err) && !en, "parser: both empty -> disabled");
  Check(!ParseSpeciesResponseConventions("fprop", nullptr, en, q, z, err), "parser: Q0 without FUZZ refused");
  Check(!ParseSpeciesResponseConventions(nullptr, "prorata", en, q, z, err), "parser: FUZZ without Q0 refused");
  Check(!ParseSpeciesResponseConventions("Fprop", "prorata", en, q, z, err), "parser: wrong case refused");
  Check(!ParseSpeciesResponseConventions("fprop", "absolute", en, q, z, err), "parser: old fuzz name refused");
  Check(ParseSpeciesResponseConventions("fprop", "prorata", en, q, z, err) && en &&
            q == Q0Convention::kFPropagation && z == FuzzConvention::kProRata, "parser: fprop/prorata accepted");
  Check(ParseSpeciesResponseConventions("fractional", "none", en, q, z, err) && en &&
            q == Q0Convention::kFractional && z == FuzzConvention::kNone, "parser: fractional/none accepted");
  Check(ParseSpeciesResponseConventions("legacy", "all", en, q, z, err) && en &&
            q == Q0Convention::kLegacyAbsolute && z == FuzzConvention::kAll, "parser: legacy/all accepted");

  std::printf("%s: %d failure(s)\n", g_fail ? "FAILED" : "ALL PASS", g_fail);
  return g_fail ? 1 : 0;
}
