// =============================================================================
// RecoilResponseUniverse: an exploratory recoil-response sensitivity universe.
//
// It scales the RECONSTRUCTED calorimetric recoil of simulated events by
// (1 + nsigma * delta):
//   - reco available energy, NewEavail() (tracker + ECAL blob energy minus
//     muon fuzz, x1.17);
//   - the reco energy transfer q0 = <tree>_recoil_E entering RecoQ3() and
//     RecoW().
// Truth quantities, event weights and selection cuts are untouched; none of
// the selection cuts reads the recoil.
//
// The band is constructed only when MNV101_RECOIL_RESPONSE_DELTA is set (see
// runEventLoopOmniFold.cpp), so the event loop is unchanged without it. It is
// a labelled sensitivity (publication packet W2, delta = 0.04 from the test
// beam's "agreements better than 4%", Aliaga et al., NIM A 789, 28), not a
// MINERvA per-particle response prescription or a validated uncertainty.
//
// RecoQ3()/RecoW() repeat CVUniverse's formulas with the scaled q0. With
// delta = 0 they must reproduce CVUniverse bit for bit; the W2 delta = 0
// control checks that end to end.
// =============================================================================
#ifndef RECOILRESPONSEUNIVERSE_H
#define RECOILRESPONSEUNIVERSE_H

#include <cmath>
#include <string>

#include "event/CVUniverse.h"

class RecoilResponseUniverse : public CVUniverse {
 public:
  RecoilResponseUniverse(PlotUtils::ChainWrapper* chw, double nsigma, double delta)
      : CVUniverse(chw, nsigma), m_scale(1.0 + nsigma * delta) {}

  virtual ~RecoilResponseUniverse() {}

  double Scale() const { return m_scale; }

  virtual double NewEavail() const override {  // MeV
    return CVUniverse::NewEavail() * m_scale;
  }

  virtual double RecoQ3() const override {  // MeV
    const double q0 = RecoQ0Scaled();
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
    const double q0 = RecoQ0Scaled();
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

  virtual std::string ShortName() const override { return "RecoilResponse"; }
  virtual std::string LatexName() const override { return "Recoil response (exploratory)"; }

 private:
  double RecoQ0Scaled() const {
    return GetDouble((MinervaUniverse::GetTreeName() + "_recoil_E").c_str()) * m_scale;
  }

  double m_scale;
};

#endif  // RECOILRESPONSEUNIVERSE_H
