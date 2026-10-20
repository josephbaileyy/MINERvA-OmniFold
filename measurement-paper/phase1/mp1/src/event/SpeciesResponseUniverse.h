// =============================================================================
// SpeciesResponseUniverse: one particle species' calorimetric response varied
// in the reconstructed recoil of simulated events (MP1-A step S0, rulings R1-R3
// of BINDING-PHASE1-ADDENDUM-2).
//
// For species s with fractional size delta_s and shift k = nsigma * delta_s:
//   E_avail' = NewEavail() + k * E_avail,s
//   q0'      = q0 + dq0,s(k),        q0 = <tree>_recoil_E,
// and RecoQ3()/RecoW() are CVUniverse's formulas evaluated at q0'.
//
// E_avail,s, species s's part of NewEavail() (CVUniverse.h: tracker + ECAL
// blob energy minus the muon fuzz, x1.17). E_s = blob_recoil_E_tracker_<b> +
// blob_recoil_E_ecal_<b>; on MC these pieces sum to the detector totals. The
// subtracted muon fuzz is not split by species in the tuples (R2):
//   kProRata (primary): E_avail,s = NewEavail() * E_s / (tracker + ECAL)
//                       (the fuzz has the species mix of the total);
//   kNone:              E_avail,s = 1.17 * E_s (the fuzz holds none of s);
//   kAll:               E_avail,s = 1.17 * (E_s - min(E_s, fuzz))
//                       (the fuzz holds all of s, up to E_s).
//
// q0. pc_s = part_response_recoil_allNonMuonClusters_<p>_id + _od, and pc = the
// same sum over the ten species (= MasterAnaDev_recoil_passivecorrected on 1A
// MC). On selected 1A MC q0 = F(pc) for a fixed monotone polyline F (S0, G0):
//   kFPropagation (R1): dq0 = F(pc + k pc_s) - F(pc), with F tabulated per
//                       playlist (MNV101_SPECIES_RESPONSE_FTABLE). Where
//                       q0 = F(pc) (G0: to 2e-14 on held-out 1A) this is
//                       q0' = F(pc + k pc_s) exactly;
//   kFractional:        dq0 = k * q0 * pc_s / pc (MAT's newer path, ID+OD);
//                       R1's declared fallback if G0 fails;
//   kLegacyAbsolute:    dq0 = k * pc_s (MAT's legacy _id_err shift, ID+OD).
//
// Sizes are D1's: proton 3.5%, meson 5%, EM 3%, other 20%, cross-talk 20%
// (cross-talk is a variant only, R3). Muon and neutrons are absent. Truth,
// weights and cuts are inherited; no selection cut reads the recoil. Negative
// tuple defaults count as zero (as MAT). At k = 0 every override returns
// CVUniverse's value through an early return, so a k = 0 pass reproduces
// CVUniverse bit for bit (G1).
// =============================================================================
#ifndef SPECIESRESPONSEUNIVERSE_H
#define SPECIESRESPONSEUNIVERSE_H

#include <cmath>
#include <fstream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "event/CVUniverse.h"

namespace species_response {

enum class Q0Convention { kLegacyAbsolute, kFractional, kFPropagation };
enum class FuzzConvention { kProRata, kNone, kAll };

struct Species {
  const char* label;  // band suffix: SpeciesResponse_<label>
  const char* blob;   // blob_recoil_E_{tracker,ecal}_<blob>
  const char* part;   // part_response_recoil_allNonMuonClusters_<part>_{id,od}
  double delta;       // D1 fractional size
};

// D1 sizes; the tuples' own _id_err/_id ratios equal these exactly (S0 receipt).
constexpr Species kProton{"proton", "p", "proton", 0.035};
constexpr Species kMeson{"meson", "meson", "meson", 0.05};
constexpr Species kEM{"em", "em", "em", 0.03};
constexpr Species kOther{"other", "other", "other", 0.20};
constexpr Species kXtalk{"xtalk", "xtalk", "xtalk", 0.20};
constexpr Species kAll[] = {kProton, kMeson, kEM, kOther, kXtalk};

// The ten allNonMuonClusters species whose ID+OD sum is pc.
constexpr const char* kPartSpecies[] = {"proton", "meson", "em", "other", "low_neutron",
                                        "mid_neutron", "high_neutron", "xtalk", "muon", "none"};

// A monotone piecewise-linear map, linear between knots and extended with the
// end segments' slopes (the rule s0_g0_ftable.py tabulates and tests).
class PiecewiseLinearMap {
 public:
  // File format: one "x y" pair per line, '#' starts a comment line; at least
  // two knots, x strictly increasing, y non-decreasing.
  static std::shared_ptr<const PiecewiseLinearMap> Load(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open F table '" + path + "'");
    auto map = std::make_shared<PiecewiseLinearMap>();
    std::string line;
    while (std::getline(in, line)) {
      if (line.empty() || line[0] == '#') continue;
      std::istringstream ss(line);
      double x = 0.0, y = 0.0;
      std::string rest;
      if (!(ss >> x >> y) || (ss >> rest)) throw std::runtime_error("bad F-table line '" + line + "'");
      if (!std::isfinite(x) || !std::isfinite(y)) throw std::runtime_error("non-finite F-table knot");
      if (!map->m_x.empty() && (x <= map->m_x.back() || y < map->m_y.back()))
        throw std::runtime_error("F table is not monotone at x = " + std::to_string(x));
      map->m_x.push_back(x);
      map->m_y.push_back(y);
    }
    if (map->m_x.size() < 2) throw std::runtime_error("F table '" + path + "' has fewer than two knots");
    return map;
  }

  double operator()(double x) const {
    const size_t n = m_x.size();
    size_t i = 0;  // segment [i, i+1]
    if (x >= m_x[n - 1]) {
      i = n - 2;
    } else if (x > m_x[0]) {
      size_t lo = 0, hi = n - 1;  // invariant: m_x[lo] <= x < m_x[hi]
      while (hi - lo > 1) {
        const size_t mid = (lo + hi) / 2;
        if (m_x[mid] <= x) lo = mid; else hi = mid;
      }
      i = lo;
    }
    const double slope = (m_y[i + 1] - m_y[i]) / (m_x[i + 1] - m_x[i]);
    return m_y[i] + slope * (x - m_x[i]);
  }

  size_t Size() const { return m_x.size(); }
  double FirstX() const { return m_x.front(); }
  double LastX() const { return m_x.back(); }

 private:
  std::vector<double> m_x, m_y;
};

}  // namespace species_response

class SpeciesResponseUniverse : public CVUniverse {
 public:
  using Q0Convention = species_response::Q0Convention;
  using FuzzConvention = species_response::FuzzConvention;
  using Species = species_response::Species;
  using FMap = species_response::PiecewiseLinearMap;

  SpeciesResponseUniverse(PlotUtils::ChainWrapper* chw, double nsigma, const Species& species,
                          Q0Convention q0conv, FuzzConvention fuzzconv,
                          std::shared_ptr<const FMap> fmap = nullptr)
      : CVUniverse(chw, nsigma),
        m_species(species),
        m_k(nsigma * species.delta),
        m_q0conv(q0conv),
        m_fuzzconv(fuzzconv),
        m_fmap(std::move(fmap)) {
    if (m_q0conv == Q0Convention::kFPropagation && !m_fmap)
      throw std::invalid_argument("F-propagation needs an F table");
  }

  virtual ~SpeciesResponseUniverse() {}

  double Shift() const { return m_k; }

  virtual double NewEavail() const override {  // MeV
    const double base = CVUniverse::NewEavail();
    if (m_k == 0.0) return base;
    return base + m_k * EavailSpecies(base);
  }

  virtual double RecoQ3() const override {  // MeV
    const double q0 = RecoQ0Shifted();
    double E_lep = GetEmu();
    double p_lep = GetPmu();
    double theta = GetThetamu();
    double mass_sq = E_lep * E_lep - p_lep * p_lep;
    double Enu = E_lep + q0;
    double q2 = 2.0 * Enu * (E_lep - p_lep * cos(theta)) - mass_sq;
    if (q2 < 0.0) q2 = 0.0;
    return sqrt(q2 + q0 * q0);
  }

  virtual double RecoW() const override {  // MeV
    const double q0 = RecoQ0Shifted();
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

  // A shifted reconstruction: the active-universe path must rebuild the
  // selection and kinematics rather than treat this as a weight-only band.
  virtual bool IsVerticalOnly() const override { return false; }

  virtual std::string ShortName() const override {
    return std::string("SpeciesResponse_") + m_species.label;
  }
  virtual std::string LatexName() const override {
    return std::string("Response (") + m_species.label + ")";
  }

 private:
  double Positive(const std::string& branch) const {
    const double v = GetDouble(branch.c_str());
    return v > 0.0 ? v : 0.0;
  }

  // Species s's part of NewEavail(); `eavail` is CVUniverse::NewEavail().
  double EavailSpecies(double eavail) const {
    const std::string b(m_species.blob);
    const double e_s = Positive("blob_recoil_E_tracker_" + b) + Positive("blob_recoil_E_ecal_" + b);
    switch (m_fuzzconv) {
      case FuzzConvention::kNone:
        return 1.17 * e_s;
      case FuzzConvention::kAll: {
        const std::vector<double> fuzz = GetTrackerECALMuFuzz();
        const double f = fuzz[0] + fuzz[1];
        return 1.17 * (e_s - (f < e_s ? f : e_s));
      }
      case FuzzConvention::kProRata:
      default: {
        const double raw = GetDouble("blob_recoil_E_tracker") + GetDouble("blob_recoil_E_ecal");
        return raw > 0.0 ? eavail * (e_s / raw) : 0.0;
      }
    }
  }

  double PartIDOD(const char* species) const {
    const std::string p = std::string("part_response_recoil_allNonMuonClusters_") + species;
    return Positive(p + "_id") + Positive(p + "_od");
  }

  double RecoQ0Shifted() const {
    const double q0 = GetDouble((MinervaUniverse::GetTreeName() + "_recoil_E").c_str());
    if (m_k == 0.0) return q0;
    const double pc_s = PartIDOD(m_species.part);
    if (m_q0conv == Q0Convention::kLegacyAbsolute) return q0 + m_k * pc_s;
    double pc = 0.0;
    for (const char* s : species_response::kPartSpecies) pc += PartIDOD(s);
    if (m_q0conv == Q0Convention::kFPropagation) {
      const FMap& F = *m_fmap;
      return q0 + (F(pc + m_k * pc_s) - F(pc));
    }
    return pc > 0.0 ? q0 + m_k * q0 * (pc_s / pc) : q0;
  }

  const Species m_species;
  const double m_k;
  const Q0Convention m_q0conv;
  const FuzzConvention m_fuzzconv;
  const std::shared_ptr<const FMap> m_fmap;
};

#endif  // SPECIESRESPONSEUNIVERSE_H
