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

  // --- Three-momentum transfer q3 (4th OmniFold axis, Workstream D) --------
  // Reco q3: the low-recoil CALORIMETRIC reconstruction from MAT
  // PlotUtils/LowRecoilFunctions.h::GetLowRecoilQ3 (the Rodrigues 2016 /
  // Ascencio 2022 low-recoil lineage, arXiv:1511.05944 / 2110.13372):
  //   q0  = calorimetric recoil  = <tree>_recoil_E         (the FULL energy
  //         transfer, NOT the available energy NewEavail above)
  //   Q^2 = 2 Enu (Emu - p_mu cos theta_mu) - m_mu^2,  Enu = Emu + q0
  //   q3  = sqrt(Q^2 + q0^2)
  // Replicated inline (not #include LowRecoilFunctions.h) for the same reason
  // as NewEavail: that header redefines GetVertex()/GetEAvailable() which
  // CVUniverse already provides. Branch <tree>_recoil_E is present in the
  // MasterAnaDev tuples (verified). Truth q3 uses the canonical MAT
  // Getq3True() (PlotUtils/TruthFunctions.h, included above): no new code.
  virtual double RecoQ3() const {  // MeV
    double q0 = GetDouble((MinervaUniverse::GetTreeName() + "_recoil_E").c_str());
    double E_lep = GetEmu();   // MeV
    double p_lep = GetPmu();   // MeV
    double theta = GetThetamu();
    double mass_sq = E_lep * E_lep - p_lep * p_lep;
    double Enu = E_lep + q0;
    double q2 = 2.0 * Enu * (E_lep - p_lep * cos(theta)) - mass_sq;
    if (q2 < 0.0) q2 = 0.0;
    return sqrt(q2 + q0 * q0);  // MeV
  }

  // ---- Per-hadron point-cloud accessors (Phase 3 / PET track) ----
  // Truth final-state hadrons: the mc_FSPart* arrays with the primary muon
  // (pdg == +-13) and neutrinos dropped. Returns parallel vectors so the
  // event loop can dump variable-length gen point clouds (zero-padded in the
  // Python DataLoader). Energies/momenta in MeV.
  virtual void GetTruthFSHadrons(std::vector<double>& E, std::vector<double>& px,
                                 std::vector<double>& py, std::vector<double>& pz,
                                 std::vector<int>& pdg) const {
    E.clear(); px.clear(); py.clear(); pz.clear(); pdg.clear();
    const int n = GetInt("mc_nFSPart");
    for(int i = 0; i < n; ++i){
      const int p = GetVecElemInt("mc_FSPartPDG", i);
      if(p == 13 || p == -13) continue;          // drop the primary muon
      if(p == 12 || p == -12 || p == 14 || p == -14 || p == 16 || p == -16) continue; // nu
      E.push_back(GetVecElem("mc_FSPartE", i));
      px.push_back(GetVecElem("mc_FSPartPx", i));
      py.push_back(GetVecElem("mc_FSPartPy", i));
      pz.push_back(GetVecElem("mc_FSPartPz", i));
      pdg.push_back(p);
    }
  }

  // Reco recoil clusters: the NON-MUON detector clusters (cluster_* collection,
  // isMuontrack==0), per-cluster energy (MeV), transverse position `pos` in the
  // cluster's view (mm), z position (mm), and view (1=X,2=U,3=V). This is the
  // hadronic recoil point cloud paired with the truth FS-hadron cloud.
  //   FIX 2026-06-04: the earlier ExtraEnergyClusters_* collection is ~empty in MC
  //   and 100% empty in data (an auxiliary collection); cluster_* is the real recoil.
  // 3 features (E, pos, z) so a uniform mm/MeV scaling works and the energy>0 mask
  // is clean; the categorical `view` is omitted from this first version.
  virtual void GetRecoClusters(std::vector<double>& E, std::vector<double>& pos,
                               std::vector<double>& z) const {
    E.clear(); pos.clear(); z.clear();
    const std::vector<double> all_E   = GetVecDouble("cluster_energy");
    const std::vector<double> all_pos = GetVecDouble("cluster_pos");
    const std::vector<double> all_z   = GetVecDouble("cluster_z");
    const std::vector<int>    all_mu  = GetVecInt("cluster_isMuontrack");
    const size_t n = all_E.size();
    for(size_t i = 0; i < n; ++i){
      if(i < all_mu.size() && all_mu[i] != 0) continue;   // drop muon-track clusters
      E.push_back(all_E[i]);
      pos.push_back(i < all_pos.size() ? all_pos[i] : 0.0);
      z.push_back(i < all_z.size() ? all_z[i] : 0.0);
    }
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
