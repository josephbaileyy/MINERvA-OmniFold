// Mock of MINERvA-101 CVUniverse for compiling and unit-testing SpeciesResponseUniverse.h without MAT/ROOT.
// NewEavail(), GetTrackerECALMuFuzz(), RecoQ3() and RecoW() repeat the production bodies
// (MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h) so the identity test is meaningful.
#ifndef CVUNIVERSE_H
#define CVUNIVERSE_H

#include <cmath>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace PlotUtils {
struct ChainWrapper {
  std::map<std::string, double> scalars;
  std::vector<int> fuzz_ids;
  std::vector<double> fuzz_e;
};
}  // namespace PlotUtils

struct MinervaUniverse {
  static std::string GetTreeName() { return "MasterAnaDev"; }
};

class CVUniverse {
 public:
  CVUniverse(PlotUtils::ChainWrapper* chw, double nsigma = 0) : m_chw(chw), m_nsigma(nsigma) {}
  virtual ~CVUniverse() {}

  static constexpr double M_n = 939.56536;
  static constexpr double M_p = 938.272013;
  static constexpr double M_nucleon = (1.5 * M_n + M_p) / 2.5;

  double GetDouble(const char* name) const {
    auto it = m_chw->scalars.find(name);
    if (it == m_chw->scalars.end()) throw std::runtime_error(std::string("missing branch ") + name);
    return it->second;
  }
  int GetInt(const char* name) const {
    if (std::string(name) == "muon_fuzz_per_plane_r80_planeIDs_sz") return static_cast<int>(m_chw->fuzz_ids.size());
    throw std::runtime_error(std::string("missing int ") + name);
  }
  double GetVecElem(const char* name, int i) const {
    if (std::string(name) == "muon_fuzz_per_plane_r80_planeIDs") return m_chw->fuzz_ids.at(i);
    if (std::string(name) == "muon_fuzz_per_plane_r80_energies") return m_chw->fuzz_e.at(i);
    throw std::runtime_error(std::string("missing vector ") + name);
  }
  double GetEmu() const { return GetDouble("Emu"); }
  double GetPmu() const { return GetDouble("Pmu"); }
  double GetThetamu() const { return GetDouble("Thetamu"); }

  virtual std::vector<double> GetTrackerECALMuFuzz() const {
    double trk_mufuzz = 0.0;
    double ecal_mufuzz = 0.0;
    int nfuzz = GetInt("muon_fuzz_per_plane_r80_planeIDs_sz");
    if (nfuzz == 0) return {0.0, 0.0};
    for (int i = 0; i < nfuzz; i++) {
      int planeID = GetVecElem("muon_fuzz_per_plane_r80_planeIDs", i);
      if (planeID < 1504968704 || planeID > 1709703168) continue;
      double fuzze = GetVecElem("muon_fuzz_per_plane_r80_energies", i);
      if (planeID > 1504968704 and planeID < 1560805376)
        trk_mufuzz += fuzze;
      else if (planeID > 1700003840 and planeID < 1709703168)
        ecal_mufuzz += fuzze;
    }
    return {trk_mufuzz, ecal_mufuzz};
  }

  virtual double NewEavail() const {  // MeV
    double recoiltracker = GetDouble("blob_recoil_E_tracker") - GetTrackerECALMuFuzz()[0];
    double recoilEcal = GetDouble("blob_recoil_E_ecal") - GetTrackerECALMuFuzz()[1];
    const double Eavailable_scale = 1.17;
    double eavail = recoiltracker + recoilEcal;
    return eavail * Eavailable_scale;
  }

  virtual double RecoQ3() const {  // MeV
    double q0 = GetDouble((MinervaUniverse::GetTreeName() + "_recoil_E").c_str());
    double E_lep = GetEmu();
    double p_lep = GetPmu();
    double theta = GetThetamu();
    double mass_sq = E_lep * E_lep - p_lep * p_lep;
    double Enu = E_lep + q0;
    double q2 = 2.0 * Enu * (E_lep - p_lep * cos(theta)) - mass_sq;
    if (q2 < 0.0) q2 = 0.0;
    return sqrt(q2 + q0 * q0);
  }

  virtual double RecoW() const {  // MeV
    double q0 = GetDouble((MinervaUniverse::GetTreeName() + "_recoil_E").c_str());
    double E_lep = GetEmu();
    double p_lep = GetPmu();
    double theta = GetThetamu();
    double mass_sq = E_lep * E_lep - p_lep * p_lep;
    double Enu = E_lep + q0;
    double q2 = 2.0 * Enu * (E_lep - p_lep * cos(theta)) - mass_sq;
    if (q2 < 0.0) q2 = 0.0;
    double M = M_nucleon;
    double w2 = M * M + 2.0 * M * q0 - q2;
    if (w2 < 0.0) w2 = 0.0;
    return sqrt(w2);
  }

  virtual bool IsVerticalOnly() const { return true; }
  virtual std::string ShortName() const { return "cv"; }
  virtual std::string LatexName() const { return "CV"; }

 protected:
  PlotUtils::ChainWrapper* m_chw;
  double m_nsigma;
};

#endif  // CVUNIVERSE_H
