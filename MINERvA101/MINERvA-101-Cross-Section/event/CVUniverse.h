// =============================================================================
// Base class for an un-systematically shifted (i.e. CV) universe. Implement
// "Get" functions for all the quantities that you need for your analysis.
//
// This class inherits from PU::MinervaUniverse, which in turn inherits from
// PU::BaseUniverse. PU::BU defines the interface with anatuples.
// 
// Within the class, "WeightFunctions" and "MuonFunctions" are included to gain
// access to standardized weight and muon variable getters. See:
// https://cdcvs.fnal.gov/redmine/projects/minerva-sw/wiki/MinervaUniverse_Structure_
// for a full list of standardized functions you can use. In general, if a
// standard version of a function is available, you should be using it.
// =============================================================================
#ifndef CVUNIVERSE_H
#define CVUNIVERSE_H

#include <iostream>

#include "PlotUtils/MinervaUniverse.h"

class CVUniverse : public PlotUtils::MinervaUniverse {

  public:
  #include "PlotUtils/MuonFunctions.h" // GetMinosEfficiencyWeight
  #include "PlotUtils/TruthFunctions.h" //Getq3True
  // ========================================================================
  // Constructor/Destructor
  // ========================================================================
  CVUniverse(PlotUtils::ChainWrapper* chw, double nsigma = 0)
      : PlotUtils::MinervaUniverse(chw, nsigma) {}

  virtual ~CVUniverse() {}

  // ========================================================================
  // Quantities defined here as constants for the sake of below. Definition
  // matched to Dan's CCQENuInclusiveME variables from:
  // `/minerva/app/users/drut1186/cmtuser/Minerva_v22r1p1_OrigCCQENuInc/Ana/CCQENu/ana_common/include/CCQENuUtils.h`
  // ========================================================================
  static constexpr double M_n = 939.56536;
  static constexpr double M_p = 938.272013;
  static constexpr double M_nucleon = (1.5*M_n+M_p)/2.5;

  static constexpr int PDG_n = 2112;
  static constexpr int PDG_p = 2212;

  // ========================================================================
  // Write a "Get" function for all quantities access by your analysis.
  // For composite quantities (e.g. Enu) use a calculator function.
  //
  // In order to properly calculate muon variables and systematics use the
  // various functions defined in MinervaUniverse.
  // E.g. GetPmu, GetEmu, etc.
  // ========================================================================

  // Quantities only needed for cuts
  // Although unlikely, in principle these quanties could be shifted by a
  // systematic. And when they are, they'll only be shifted correctly if we
  // write these accessor functions.
  
  //Muon kinematics
  double GetMuonPT() const //GeV/c
  {
    return GetPmu()/1000. * sin(GetThetamu());
  }

  double GetMuonPz() const //GeV/c
  {
    return GetPmu()/1000. * cos(GetThetamu());
  }

  double GetMuonPTTrue() const //GeV/c
  {
    return GetPlepTrue()/1000. * sin(GetThetalepTrue());
  }

  double GetMuonPzTrue() const //GeV/c
  {
    return GetPlepTrue()/1000. * cos(GetThetalepTrue());
  }

  double GetEmuGeV() const //GeV
  {
    return GetEmu()/1000.;
  }

  double GetElepTrueGeV() const //GeV
  {
    return GetElepTrue()/1000.;
  }

  int GetInteractionType() const {
    return GetInt("mc_intType");
  }

  int GetTargetNucleon() const {
    return GetInt("mc_targetNucleon");
  }
  
  double GetBjorkenXTrue() const {
    return GetDouble("mc_Bjorkenx");
  }

  double GetBjorkenYTrue() const {
    return GetDouble("mc_Bjorkeny");
  }

  virtual bool IsMinosMatchMuon() const {
    // Require a MINOS-matched muon track with a passing MINOS fit.
    // `has_interaction_vertex==1` was an educational stub (true for
    // essentially every event in the pre-selected AnaTuple) and biased
    // the low-p_|| cross section low — see 2D_OMNIFOLD_REFERENCE.md.
    const std::string ok_branch = GetAnaToolName() + "_minos_trk_is_ok";
    return GetInt("isMinosMatchTrack") == 1 && GetInt(ok_branch.c_str()) == 1;
  }
  
  ROOT::Math::XYZTVector GetVertex() const
  {
    ROOT::Math::XYZTVector result;
    result.SetCoordinates(GetVec<double>("vtx").data());
    return result;
  }

  ROOT::Math::XYZTVector GetTrueVertex() const
  {
    ROOT::Math::XYZTVector result;
    result.SetCoordinates(GetVec<double>("mc_vtx").data());
    return result;
  }

  virtual int GetTDead() const {
    return GetInt("phys_n_dead_discr_pair_upstream_prim_track_proj");
  }
  
  //TODO: If there was a spline correcting Eavail, it might not really be Eavail.
  //      Our energy correction spline, one of at least 2 I know of, corrects q0
  //      so that we get the right neutrino energy in an inclusive sample.  So,
  //      this function could be correcting for neutron energy which Eavail should
  //      not do.
  virtual double GetEavail() const {
    return GetDouble("recoilE_SplineCorrected");
  }
  
  virtual double GetQ2Reco() const{
    return GetDouble("qsquared_recoil");
  }

  //GetRecoilE is designed to match the NSF validation suite
  virtual double GetRecoilE() const {
    return GetVecElem("recoil_summed_energy", 0);
  }
  
  virtual double Getq3() const{
    double eavail = GetEavail()/pow(10,3);
    double q2 = GetQ2Reco() / pow(10,6);
    double q3mec = sqrt(eavail*eavail + q2);
    return q3mec;
  }

  // --- Available energy (3rd OmniFold axis, Workstream C) -----------------
  // Copied verbatim from MAT: reco NewEavail (LowRecoilPionFunctions.h,
  // tracker+ECAL x1.17) and truth GetEAvailableTrue (CCQE3DFitFunctions.h /
  // arXiv:2312.16631 Eq. 4). Added standalone here rather than #including
  // those headers because LowRecoilPionFunctions.h redefines GetVertex(),
  // which CVUniverse already provides. Branch availability verified in the
  // MasterAnaDev tuples (blob_recoil_E_*, muon_fuzz_*, mc_FSPart*); the
  // spline GetEavail()/recoilE_SplineCorrected branch is absent there.
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
    double recoiltracker =
        GetDouble("blob_recoil_E_tracker") - GetTrackerECALMuFuzz()[0];
    double recoilEcal =
        GetDouble("blob_recoil_E_ecal") - GetTrackerECALMuFuzz()[1];
    const double Eavailable_scale = 1.17;
    double eavail = recoiltracker + recoilEcal;
    return eavail * Eavailable_scale;
  }

  double GetEAvailableTrue() const {  // MeV
    double recoil = 0;
    int n_parts = GetInt("mc_nFSPart");
    double mass_pion = 135;
    double mass_proton = 938.27;
    for(int i=0;i<n_parts;i++){
      int pdg = GetVecElemInt("mc_FSPartPDG",i);
      if(pdg == 22) recoil+=GetVecElem("mc_FSPartE",i);            // total E
      if(pdg == 211 || pdg == -211) recoil+=GetVecElem("mc_FSPartE",i)-mass_pion;  // KE
      if(pdg == 111) recoil+=GetVecElem("mc_FSPartE",i);          // total E
      if(pdg == 2212) recoil+=GetVecElem("mc_FSPartE",i)-mass_proton;             // KE
    }
    return recoil;
  }

  virtual int GetCurrent() const { return GetInt("mc_current"); }

  virtual int GetTruthNuPDG() const { return GetInt("mc_incoming"); }

  virtual double GetMuonQP() const {
    return GetDouble((GetAnaToolName() + "_minos_trk_qp").c_str());
  }

  //Some functions to match CCQENuInclusive treatment of DIS weighting. Name matches same Dan area as before.
  virtual double GetTrueExperimentersQ2() const {
    double Enu = GetEnuTrue(); //MeV
    double Emu = GetElepTrue(); //MeV
    double thetaMu = GetThetalepTrue();
    return 4.0*Enu*Emu*pow(sin(thetaMu/2.0),2.0);//MeV^2
  }

  virtual double CalcTrueExperimentersQ2(double Enu, double Emu, double thetaMu) const{
    return 4.0*Enu*Emu*pow(sin(thetaMu/2.0),2.0);//MeV^2
  }

  virtual double GetTrueExperimentersW() const {
    double nuclMass = M_nucleon;
    int struckNucl = GetTargetNucleon();
    if (struckNucl == PDG_n){
      nuclMass=M_n;
    }
    else if (struckNucl == PDG_p){
      nuclMass=M_p;
    }
    double Enu = GetEnuTrue();
    double Emu = GetElepTrue();
    double thetaMu = GetThetalepTrue();
    double Q2 = CalcTrueExperimentersQ2(Enu, Emu, thetaMu);
    return TMath::Sqrt(pow(nuclMass,2) + 2.0*(Enu-Emu)*nuclMass - Q2);
  }

  //Still needed for some systematics to compile, but shouldn't be used for reweighting anymore.
  protected:
  #include "PlotUtils/WeightFunctions.h" // Get*Weight
};

#endif
