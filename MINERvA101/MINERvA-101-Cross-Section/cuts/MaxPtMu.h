//File: MaxPtMu
//Brief: Don't allow any CC neutrino interactions where the primary lepton's
//       transverse momentum went above some value.  Used to define the
//       fiducial phase space for the double-differential (p_T, p_||) analysis.
//Author: Joseph Bailey

#ifndef PTMUMAX_H
#define PTMUMAX_H

#include "PlotUtils/Cut.h"

template <class UNIVERSE>
class MaxPtMu: public PlotUtils::SignalConstraint<UNIVERSE>
{
  public:
    MaxPtMu(const double max): PlotUtils::SignalConstraint<UNIVERSE>(std::string("PtMu < ") + std::to_string(max)), fMax(max)
    {
    }

  private:
    bool checkConstraint(const UNIVERSE& univ) const override
    {
      return univ.GetPlepTrue() * sin(univ.GetThetalepTrue()) <= fMax;
    }

    const double fMax; // MeV/c (to match MaxPzMu convention: raw GetPlepTrue() units)
};

#endif //PTMUMAX_H
