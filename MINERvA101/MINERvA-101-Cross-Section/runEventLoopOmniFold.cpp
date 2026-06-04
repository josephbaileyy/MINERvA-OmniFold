#define OUT_FILE_NAME "runEventLoopOmniFold.root"

#define USAGE \
"\n*** USAGE ***\n"\
"runEventLoopOmniFold <dataPlaylist.txt> <mcPlaylist.txt>\n\n"\
"*** Explanation ***\n"\
"Reduce MasterAnaDev AnaTuples to unbinned event-level arrays for OmniFold-style unfolding.\n\n"\
"*** The Input Files ***\n"\
"Playlist files are plaintext files with 1 file name per line.  Filenames may be\n"\
"xrootd URLs or refer to the local filesystem.  The first playlist file's\n"\
"entries will be treated like data, and the second playlist's entries must\n"\
"have the \"Truth\" tree to use for calculating the efficiency denominator.\n\n"\
"*** Output ***\n"\
"Produces a single ROOT file, " OUT_FILE_NAME ", containing TTrees with the\n"\
"unbinned arrays needed for OmniFold-style unfolding.  Writes both p_T and\n"\
"p_|| (longitudinal momentum) branches for 2D unfolding.  This variant does\n"\
"NOT write the standard ExtractCrossSection histogram suite.\n\n"\
"*** Environment Variables ***\n"\
"Setting up this package appends to PATH and LD_LIBRARY_PATH.  PLOTUTILSROOT,\n"\
"MPARAMFILESROOT, and MPARAMFILES must be set according to the setup scripts in\n"\
"those packages for systematics and flux reweighters to function.\n\n"\
"*** Return Codes ***\n"\
"0 indicates success.\n"

// Shared error codes with the histogram-based event loop.

enum ErrorCodes
{
  success = 0,
  badCmdLine = 1,
  badInputFile = 2,
  badFileRead = 3,
  badOutputFile = 4
};

//PlotUtils includes
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Woverloaded-virtual"

//Includes from this package
#include "event/CVUniverse.h"
#include "event/MichelEvent.h"
#include "systematics/Systematics.h"
#include "cuts/MaxPzMu.h"
#include "cuts/MaxPtMu.h"
#include "util/Variable.h"
#include "util/Variable2D.h"
#include "util/GetFluxIntegral.h"
#include "util/GetPlaylist.h"
#include "cuts/SignalDefinition.h"
#include "cuts/q3RecoCut.h"
#include "studies/Study.h"
//#include "Binning.h" //TODO: Fix me

//PlotUtils includes
#include "PlotUtils/makeChainWrapper.h"
#include "PlotUtils/HistWrapper.h"
#include "PlotUtils/Hist2DWrapper.h"
#include "PlotUtils/MacroUtil.h"
#include "PlotUtils/MnvPlotter.h"
#include "PlotUtils/CCInclusiveCuts.h"
#include "PlotUtils/CCInclusiveSignal.h"
#include "PlotUtils/CrashOnROOTMessage.h" //Sets up ROOT's debug callbacks by itself
#include "PlotUtils/Cutter.h"
#include "PlotUtils/Model.h"
#include "PlotUtils/FluxAndCVReweighter.h"
#include "PlotUtils/GENIEReweighter.h"
#include "PlotUtils/LowRecoil2p2hReweighter.h"
#include "PlotUtils/RPAReweighter.h"
#include "PlotUtils/MINOSEfficiencyReweighter.h"
#pragma GCC diagnostic pop

//ROOT includes
#include "TParameter.h"

//c++ includes
#include <iostream>
#include <cstdlib> //getenv()
#include <cstdint>
#include <sstream>
#include <string>
#include <unordered_set>
#include <set>
#include <vector>

// Pack (mc_run, mc_subrun, mc_nthEvtInFile) into a unique 64-bit key for
// fast hash-set lookup of "is this truth event already represented on the
// reco/AnaTuple side?". Run ~5 digits, subrun ~3 digits, nth ~6 digits;
// (run * 1e8 + subrun) * 1e8 + nth fits comfortably in uint64_t.
inline uint64_t makeEventKey(int run, int subrun, int nth)
{
  return (static_cast<uint64_t>(run) * 100000000ULL +
          static_cast<uint64_t>(subrun)) * 100000000ULL +
         static_cast<uint64_t>(nth);
}

// Phase 18 (2026-05): truth-denom entries cached so the reco-loop can gate
// on truthCV.isEfficiencyDenom membership, and miss-append can iterate the
// cache rather than re-walking the truth tree. See main() and
// AppendTruthOnlyMisses below.
struct TruthDenomEntry
{
  double MC;
  double MC_pz;
  double MC_eavail;
  double MC_q3;
  double w_truth;
  uint64_t key;
};

// UQ Stage-1 #7 (2026-05-21): per-systematic-universe weight dump.
// When MNV101_DUMP_UNIVERSES is set (env var), build one TBranch per
// (band, idx) for every (band) named in the comma-separated allowlist
// (or for every standard band when the env var is exactly "1"). One
// model.GetWeight(*universe, evt) is evaluated per (band, idx) per event,
// in addition to the CV evaluation. Restores universe state to CV after
// the per-event universe sweep so subsequent CV-dependent code is intact.
//
// Branch name: w_<prefix>_<sanitized-band>_<idx> where prefix is "truth"
// or "reco" and the sanitizer replaces non-[A-Za-z0-9_] with '_' so the
// resulting names are ROOT-safe.
//
// Lateral (non-vertical-only) universes additionally write shifted muon
// kinematics so the Python driver can swap (pT, pz) per universe. The
// kinematic branch names follow the existing CV-side convention of the
// host tree: pT_truth/pz_truth on the truth-denom tree, MC/MC_pz when the
// universe is in truth-mode on the reco tree, sim/sim_pz when in
// reco-mode on the reco tree.
//
// NOTE (3D E_avail): the lateral bands are all muon/beam systematics
// (BeamAngleX/Y, MuonResolution, Muon_Energy_MINERvA/MINOS). They override
// only muon momentum/angle getters, none of which feed NewEavail()
// (blob_recoil_E_tracker/ecal + muon_fuzz) or GetEAvailableTrue() (truth
// mc_FSPartE). So E_avail is invariant under every lateral universe and needs
// no shifted branch. The GEANT hadronic-response bands (which DO move E_avail
// physically) are vertical/weight-only and are captured by w_reco_GEANT_*.
//
// NOTE (4D q3): UNLIKE E_avail, q3 IS shifted by the lateral muon bands.
// RecoQ3() reconstructs q3 from the muon kinematics (Q^2 from Emu/Pmu/theta)
// + recoil_E, and Getq3True() from mc_Q2 + the true muon, so a muon-energy /
// beam-angle shift moves q3. Lateral universes therefore ALSO write a shifted
// q3 (q3_truth_/MC_q3_/sim_q3_<band>_<idx>) alongside pT/pz; the 4D Python
// driver must swap it per universe (it cannot reuse the CV q3 the way it
// reuses CV E_avail).
struct UniverseBranchInfo
{
  std::string bandName;
  size_t idx;
  CVUniverse* univ;
  std::string branchName;          // w_<prefix>_<band>_<idx>
  bool isLateral = false;
  std::string ptBranchName;        // empty when !isLateral
  std::string pzBranchName;        // empty when !isLateral
  std::string q3BranchName;        // empty when !isLateral; q3 is NOT
                                   // lateral-invariant (depends on muon
                                   // kinematics + recoil), unlike E_avail,
                                   // so lateral universes dump shifted q3.
};

inline std::string SanitizeForRootBranchName(const std::string& s)
{
  std::string out = s;
  for(char& c : out)
  {
    if(!(std::isalnum(static_cast<unsigned char>(c)) || c == '_')) c = '_';
  }
  return out;
}

// Parse MNV101_DUMP_UNIVERSES env var. Returns a (dumpAll, allowlist) pair.
// dumpAll = true when env var is exactly "1"; allowlist holds band names
// when env var is a comma-separated list. Returns (false, empty) when the
// env var is not set, meaning "do not dump".
inline std::pair<bool, std::set<std::string>>
ParseUniverseAllowlist(const char* envVal)
{
  std::pair<bool, std::set<std::string>> result(false, {});
  if(envVal == nullptr) return result;
  const std::string s = envVal;
  if(s == "1")
  {
    result.first = true;
    return result;
  }
  std::stringstream ss(s);
  std::string item;
  while(std::getline(ss, item, ','))
  {
    // trim surrounding whitespace
    size_t a = item.find_first_not_of(" \t");
    size_t b = item.find_last_not_of(" \t");
    if(a == std::string::npos) continue;
    result.second.insert(item.substr(a, b - a + 1));
  }
  return result;
}

// Kinematic-branch naming context for lateral universes. The host tree
// uses a different (pT, pz) branch convention depending on the dump
// site, so the BuildUniverseBranchTable caller picks one.
enum class UniverseKineContext
{
  TruthTree,        // pT_truth_<band>_<idx>, pz_truth_<band>_<idx>
  RecoTreeTruth,    // MC_<band>_<idx>,        MC_pz_<band>_<idx>
  RecoTreeReco      // sim_<band>_<idx>,       sim_pz_<band>_<idx>
};

// Build the per-universe branch table. `bands` is the truth_bands or
// error_bands map. `prefix` is "truth" or "reco". `kineCtx` selects the
// kinematic branch naming convention for lateral universes. `dumpAll`
// and `allowlist` come from ParseUniverseAllowlist(). The "cv" band is
// always skipped (CV weight already lives in w_truth / w_reco).
inline std::vector<UniverseBranchInfo>
BuildUniverseBranchTable(
    const std::map<std::string, std::vector<CVUniverse*>>& bands,
    const std::string& prefix,
    UniverseKineContext kineCtx,
    bool dumpAll,
    const std::set<std::string>& allowlist)
{
  std::vector<UniverseBranchInfo> out;
  for(const auto& kv : bands)
  {
    const std::string& bandName = kv.first;
    const auto& universes = kv.second;
    if(bandName == "cv") continue;
    if(!dumpAll && allowlist.find(bandName) == allowlist.end()) continue;
    const std::string sanBand = SanitizeForRootBranchName(bandName);
    for(size_t idx = 0; idx < universes.size(); ++idx)
    {
      UniverseBranchInfo ub;
      ub.bandName = bandName;
      ub.idx = idx;
      ub.univ = universes[idx];
      ub.branchName = "w_" + prefix + "_" + sanBand + "_" + std::to_string(idx);
      ub.isLateral = (universes[idx] != nullptr) && !universes[idx]->IsVerticalOnly();
      if(ub.isLateral)
      {
        const std::string suffix = sanBand + "_" + std::to_string(idx);
        switch(kineCtx)
        {
          case UniverseKineContext::TruthTree:
            ub.ptBranchName = "pT_truth_" + suffix;
            ub.pzBranchName = "pz_truth_" + suffix;
            ub.q3BranchName = "q3_truth_" + suffix;   // truth q3 (Getq3True)
            break;
          case UniverseKineContext::RecoTreeTruth:
            ub.ptBranchName = "MC_"     + suffix;
            ub.pzBranchName = "MC_pz_"  + suffix;
            ub.q3BranchName = "MC_q3_"  + suffix;      // truth q3 (Getq3True)
            break;
          case UniverseKineContext::RecoTreeReco:
            ub.ptBranchName = "sim_"    + suffix;
            ub.pzBranchName = "sim_pz_" + suffix;
            ub.q3BranchName = "sim_q3_" + suffix;      // reco q3 (RecoQ3)
            break;
        }
      }
      out.push_back(ub);
    }
  }
  return out;
}

//==============================================================================
// Loop and Fill (write only the unbinned arrays needed for OmniFold)
//==============================================================================

// Truth efficiency denominator: loop Truth tree in truth-mode and fill MC truth pTmu + weight.
//
// When outTruthDenomIDs is non-null, this loop also populates it with the
// (mc_run, mc_subrun, mc_nthEvtInFile) hash key of every event written to
// `out`. Phase 18: the reco loop consults this set to gate `mc_signal_reco`
// fills on truth-side `isEfficiencyDenom` agreement (avoids the ~1.8% of
// reco entries that pass recoCV.isEfficiencyDenom but whose corresponding
// truth-tree entry fails the same cut — see Phase 18 in
// 2D_OMNIFOLD_STUDY_STATUS.md).
//
// When outTruthDenomCache is non-null, this loop also pushes a
// TruthDenomEntry for every written event. AppendTruthOnlyMisses() iterates
// the cache (post reco-loop) to write miss entries to mc_signal_reco for
// the events not in recoIDs — replaces the inline miss-append that lived
// here in Phase 17, so the reco loop can run AFTER truth-denom.
void LoopAndFillUnbinnedMCTruthDenom(
    PlotUtils::ChainWrapper* truth,
    CVUniverse* truthCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    PlotUtils::Model<CVUniverse, MichelEvent>& model,
    const std::vector<PlotUtils::Reweighter<CVUniverse, MichelEvent>*>& componentRWs,
    TTree* out,
    std::unordered_set<uint64_t>* outTruthDenomIDs = nullptr,
    std::vector<TruthDenomEntry>* outTruthDenomCache = nullptr,
    const std::map<std::string, std::vector<CVUniverse*>>* truthBands = nullptr)
{
  double MC = 0.0;
  double MC_pz = 0.0;
  double MC_eavail = 0.0;
  double MC_q3 = 0.0;
  double w_truth = 1.0;

  out->Branch("MC", &MC);
  out->Branch("MC_pz", &MC_pz);
  out->Branch("MC_eavail", &MC_eavail);   // truth available energy (GeV)
  out->Branch("MC_q3", &MC_q3);           // truth 3-momentum transfer (GeV)
  out->Branch("w_truth", &w_truth);

  // Per-reweighter component dump for MnvTune-v1 audit (Option 1
  // decomposition). Gated behind MNV101_DUMP_COMPONENTS so canonical
  // production output is byte-clean vs the pre-audit schema. When set,
  // each branch holds GetWeight() of one reweighter at CV in truth
  // mode; the product matches w_truth modulo GetWeightRatioToCV()
  // which is 1 in CV.
  const bool dumpComponents = (getenv("MNV101_DUMP_COMPONENTS") != nullptr);
  std::vector<double> w_component(componentRWs.size(), 1.0);
  if(dumpComponents)
  {
    for(size_t k = 0; k < componentRWs.size(); ++k)
    {
      const std::string bname = "w_" + componentRWs[k]->GetName();
      out->Branch(bname.c_str(), &w_component[k]);
    }
  }

  // Per-systematic-universe weight dump (UQ Stage-1 #7). Build the branch
  // table once before the loop; uniWeights storage is sized + reserved
  // up front so the addresses we hand to TBranch::Branch stay valid.
  const auto uniAllow = ParseUniverseAllowlist(getenv("MNV101_DUMP_UNIVERSES"));
  std::vector<UniverseBranchInfo> uniBranches;
  std::vector<double> uniWeights;
  std::vector<double> uniLatPT;     // parallel to uniBranches; unused (NaN) for vertical entries
  std::vector<double> uniLatPZ;
  std::vector<double> uniLatQ3;     // shifted truth q3 for lateral universes
  size_t nLateral = 0;
  const bool dumpUniverses = (getenv("MNV101_DUMP_UNIVERSES") != nullptr) &&
                             (truthBands != nullptr);
  if(dumpUniverses)
  {
    uniBranches = BuildUniverseBranchTable(
        *truthBands, "truth", UniverseKineContext::TruthTree,
        uniAllow.first, uniAllow.second);
    uniWeights.assign(uniBranches.size(), 1.0);
    uniLatPT.assign(uniBranches.size(), 0.0);
    uniLatPZ.assign(uniBranches.size(), 0.0);
    uniLatQ3.assign(uniBranches.size(), 0.0);
    for(size_t k = 0; k < uniBranches.size(); ++k)
    {
      out->Branch(uniBranches[k].branchName.c_str(), &uniWeights[k]);
      if(uniBranches[k].isLateral)
      {
        out->Branch(uniBranches[k].ptBranchName.c_str(), &uniLatPT[k]);
        out->Branch(uniBranches[k].pzBranchName.c_str(), &uniLatPZ[k]);
        out->Branch(uniBranches[k].q3BranchName.c_str(), &uniLatQ3[k]);
        ++nLateral;
      }
    }
    std::cout << "  Universe-weight dump enabled: "
              << uniBranches.size() << " (band,idx) branches written to "
              << out->GetName() << " ("
              << nLateral << " lateral with shifted pT/pz).\n";
  }

  std::cout << "Starting unbinned MC truth-denom loop (Truth tree)...\n";
  if(outTruthDenomIDs)
    std::cout << "  (collecting truth-denom event IDs for reco-loop gating)\n";
  const int nEntries = truth->GetEntries();

  // Dedupe on (mc_run, mc_subrun, mc_nthEvtInFile). MEFHC playlist 1E file
  // run00111353 contains 1,102 truth events written twice with identical
  // IDs (upstream AnaTuple double-fill). Without this dedupe the
  // efficiency denominator is over-counted and Phase-18's by-construction
  // mc_signal_reco==mc_truth_denom identity is broken (98-entry deficit
  // observed pre-fix).
  std::unordered_set<uint64_t> seenKeys;
  long nDupSkipped = 0;

  for(int i = 0; i < nEntries; ++i)
  {
    if(i % 10000 == 0) std::cout << i << " / " << nEntries << "\r" << std::flush;

    // Truth mode + Truth tree entry
    CVUniverse::SetTruth(true);

    MichelEvent evt; // only to keep Model happy
    truthCV->SetEntry(i);
    model.SetEntry(*truthCV, evt);

    const double w_cv = model.GetWeight(*truthCV, evt);

    // Use the SAME isEfficiencyDenom logic as the old code (Truth tree context)
    if(!michelcuts.isEfficiencyDenom(*truthCV, w_cv)) continue;

    const uint64_t key = makeEventKey(
        truthCV->GetInt("mc_run"),
        truthCV->GetInt("mc_subrun"),
        truthCV->GetInt("mc_nthEvtInFile"));
    if(!seenKeys.insert(key).second)
    {
      ++nDupSkipped;
      continue;
    }

    MC = truthCV->GetMuonPTTrue();      // truth p_T (GeV/c)
    MC_pz = truthCV->GetMuonPzTrue();   // truth p_|| (GeV/c)
    MC_eavail = truthCV->GetEAvailableTrue() / 1000.0;  // MeV -> GeV
    MC_q3 = truthCV->Getq3True() / 1000.0;              // MeV -> GeV
    w_truth = model.GetWeight(*truthCV, evt);
    if(dumpComponents)
    {
      for(size_t k = 0; k < componentRWs.size(); ++k)
        w_component[k] = componentRWs[k]->GetWeight(*truthCV, evt);
    }
    if(dumpUniverses)
    {
      for(size_t k = 0; k < uniBranches.size(); ++k)
      {
        CVUniverse* u = uniBranches[k].univ;
        u->SetEntry(i);
        MichelEvent uEvt;
        model.SetEntry(*u, uEvt);
        uniWeights[k] = model.GetWeight(*u, uEvt);
        if(uniBranches[k].isLateral)
        {
          uniLatPT[k] = u->GetMuonPTTrue();
          uniLatPZ[k] = u->GetMuonPzTrue();
          uniLatQ3[k] = u->Getq3True() / 1000.0;  // MeV -> GeV (truth q3)
        }
      }
      // Restore CV state so any subsequent code in this iteration
      // (or the next loop pass) sees the CV-side model context.
      truthCV->SetEntry(i);
      model.SetEntry(*truthCV, evt);
    }

    out->Fill();

    if(outTruthDenomIDs) outTruthDenomIDs->insert(key);
    if(outTruthDenomCache)
      outTruthDenomCache->push_back({MC, MC_pz, MC_eavail, MC_q3, w_truth, key});
  }

  std::cout << "Finished unbinned MC truth-denom loop.\n";
  if(nDupSkipped > 0)
    std::cout << "  WARN: skipped " << nDupSkipped
              << " duplicate-key truth entries (upstream AnaTuple double-fill).\n";
  if(outTruthDenomIDs)
    std::cout << "  Captured " << outTruthDenomIDs->size()
              << " unique event IDs from mc_truth_denom.\n";
}

// Append a miss entry to mc_signal_reco for every truth_denom event whose
// (mc_run, mc_subrun, mc_nthEvtInFile) key is NOT in recoIDs. Replaces the
// Phase-17 inline miss-append in LoopAndFillUnbinnedMCTruthDenom — moved out
// so the reco loop can run AFTER the truth-denom loop (Phase 18). The cache
// is built during the truth-denom pass so this function does not re-read the
// truth tree.
long AppendTruthOnlyMisses(
    TTree* sigOut,
    const std::vector<TruthDenomEntry>& truthDenomCache,
    const std::unordered_set<uint64_t>& recoIDs)
{
  double miss_sim = 0.0, miss_sim_pz = 0.0, miss_sim_eavail = 0.0, miss_sim_q3 = 0.0, miss_w_reco = 1.0;
  double miss_MC = 0.0, miss_MC_pz = 0.0, miss_MC_eavail = 0.0, miss_MC_q3 = 0.0, miss_w_truth = 1.0;
  UChar_t miss_sim_pass = 0;

  sigOut->SetBranchAddress("sim",        &miss_sim);
  sigOut->SetBranchAddress("sim_pz",     &miss_sim_pz);
  sigOut->SetBranchAddress("sim_eavail", &miss_sim_eavail);
  sigOut->SetBranchAddress("sim_q3",     &miss_sim_q3);
  sigOut->SetBranchAddress("sim_pass",   &miss_sim_pass);
  sigOut->SetBranchAddress("w_reco",     &miss_w_reco);
  sigOut->SetBranchAddress("MC",         &miss_MC);
  sigOut->SetBranchAddress("MC_pz",      &miss_MC_pz);
  sigOut->SetBranchAddress("MC_eavail",  &miss_MC_eavail);
  sigOut->SetBranchAddress("MC_q3",      &miss_MC_q3);
  sigOut->SetBranchAddress("w_truth",    &miss_w_truth);

  // Phase 3: if the point-cloud branches exist (signal loop dumped them), rebind
  // them to local empty vectors for the miss entries. Their addresses currently
  // dangle (the signal loop's locals went out of scope), so a bare Fill() would
  // read freed memory and segfault. A miss has no reco clusters -> empty cloud.
  std::vector<double> e_gen_E, e_gen_px, e_gen_py, e_gen_pz;
  std::vector<int>    e_gen_pdg;
  std::vector<double> e_reco_E, e_reco_x, e_reco_y, e_reco_z;
  // Object/vector branches must be rebound via pointer-TO-pointer (vector<T>**),
  // unlike scalar branches. These pointers must stay alive until the Fill loop ends.
  std::vector<double>* p_gen_E = &e_gen_E;  std::vector<double>* p_gen_px = &e_gen_px;
  std::vector<double>* p_gen_py = &e_gen_py; std::vector<double>* p_gen_pz = &e_gen_pz;
  std::vector<int>*    p_gen_pdg = &e_gen_pdg;
  std::vector<double>* p_reco_E = &e_reco_E; std::vector<double>* p_reco_x = &e_reco_x;
  std::vector<double>* p_reco_y = &e_reco_y; std::vector<double>* p_reco_z = &e_reco_z;
  if(getenv("MNV101_DUMP_POINTCLOUD") != nullptr &&
     sigOut->GetBranch("part_gen_E") != nullptr)
  {
    sigOut->SetBranchAddress("part_gen_E",   &p_gen_E);
    sigOut->SetBranchAddress("part_gen_px",  &p_gen_px);
    sigOut->SetBranchAddress("part_gen_py",  &p_gen_py);
    sigOut->SetBranchAddress("part_gen_pz",  &p_gen_pz);
    sigOut->SetBranchAddress("part_gen_pdg", &p_gen_pdg);
    sigOut->SetBranchAddress("part_reco_E",  &p_reco_E);
    sigOut->SetBranchAddress("part_reco_x",  &p_reco_x);
    sigOut->SetBranchAddress("part_reco_y",  &p_reco_y);
    sigOut->SetBranchAddress("part_reco_z",  &p_reco_z);
  }

  long nTruthOnlyMisses = 0;
  for(const auto& tde : truthDenomCache)
  {
    if(recoIDs.find(tde.key) == recoIDs.end())
    {
      miss_MC        = tde.MC;
      miss_MC_pz     = tde.MC_pz;
      miss_MC_eavail = tde.MC_eavail;
      miss_MC_q3     = tde.MC_q3;
      miss_w_truth   = tde.w_truth;
      miss_sim        = -9999.0;
      miss_sim_pz     = -9999.0;
      miss_sim_eavail = -9999.0;
      miss_sim_q3     = -9999.0;
      miss_sim_pass = 0;            // false: this is a miss (no reco)
      miss_w_reco   = tde.w_truth;  // proxy; w_reco unused for sim_pass=false
      sigOut->Fill();
      ++nTruthOnlyMisses;
    }
  }
  std::cout << "  Appended " << nTruthOnlyMisses
            << " truth-only miss entries to mc_signal_reco.\n";
  return nTruthOnlyMisses;
}

// Selected signal reco: loop reco MC tree in reco-mode and fill reco pTmu + weight.
//
// When outRecoIDs is non-null, also populates it with
// (mc_run, mc_subrun, mc_nthEvtInFile) keys for every event written to out.
// AppendTruthOnlyMisses() then uses this set to identify truth-pass events
// that have no reco-tree counterpart and append them as miss entries — see
// LoopAndFillUnbinnedMCTruthDenom and Phase 17 in 2D_OMNIFOLD_RUN_LOG.md.
//
// Phase 18: when truthDenomIDs is non-null, fills are gated on membership
// in that set. This makes the truth-tree's `isEfficiencyDenom` evaluation
// authoritative — reco-tree entries that pass `recoCV.isEfficiencyDenom`
// but whose corresponding truth-tree entry fails the same cut (~1.8% of
// events, driven by mc_primFSLepton differing between trees when reco
// matched a secondary muon) are dropped. With the gate, the captured
// reco-ID set is a strict subset of truth_denom IDs, c_global lands at
// 1.000, and the Python c-division becomes a true no-op. See Phase 18 in
// 2D_OMNIFOLD_STUDY_STATUS.md.
void LoopAndFillUnbinnedMCSelectedSignalReco(
    PlotUtils::ChainWrapper* reco,
    CVUniverse* recoCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    PlotUtils::Model<CVUniverse, MichelEvent>& model,
    TTree* out,
    std::unordered_set<uint64_t>* outRecoIDs = nullptr,
    const std::unordered_set<uint64_t>* truthDenomIDs = nullptr,
    const std::map<std::string, std::vector<CVUniverse*>>* errorBands = nullptr)
{
  double sim = 0.0;
  double sim_pz = 0.0;
  double sim_eavail = 0.0;
  double sim_q3 = 0.0;
  UChar_t sim_pass = true;
  double w_reco = 1.0;
  double MC = 0.0;
  double MC_pz = 0.0;
  double MC_eavail = 0.0;
  double MC_q3 = 0.0;
  double w_truth = 1.0;

  out->Branch("sim", &sim);
  out->Branch("sim_pz", &sim_pz);
  out->Branch("sim_eavail", &sim_eavail);   // reco available energy (GeV)
  out->Branch("sim_q3", &sim_q3);           // reco 3-momentum transfer (GeV)
  out->Branch("sim_pass", &sim_pass);
  out->Branch("w_reco", &w_reco);
  out->Branch("MC", &MC);
  out->Branch("MC_pz", &MC_pz);
  out->Branch("MC_eavail", &MC_eavail);     // truth available energy (GeV)
  out->Branch("MC_q3", &MC_q3);             // truth 3-momentum transfer (GeV)
  out->Branch("w_truth", &w_truth);

  // Phase 3 point-cloud dump (gated, MNV101_DUMP_POINTCLOUD): per-event
  // variable-length truth FS-hadron + reco-cluster vectors for the PET track.
  // Off by default so the canonical / q3 / universe omnifiles stay lean.
  const bool dumpPC = (getenv("MNV101_DUMP_POINTCLOUD") != nullptr);
  std::vector<double> pc_gen_E, pc_gen_px, pc_gen_py, pc_gen_pz;
  std::vector<int>    pc_gen_pdg;
  std::vector<double> pc_reco_E, pc_reco_x, pc_reco_y, pc_reco_z;
  if(dumpPC){
    out->Branch("part_gen_E",   &pc_gen_E);
    out->Branch("part_gen_px",  &pc_gen_px);
    out->Branch("part_gen_py",  &pc_gen_py);
    out->Branch("part_gen_pz",  &pc_gen_pz);
    out->Branch("part_gen_pdg", &pc_gen_pdg);
    out->Branch("part_reco_E",  &pc_reco_E);
    out->Branch("part_reco_x",  &pc_reco_x);
    out->Branch("part_reco_y",  &pc_reco_y);
    out->Branch("part_reco_z",  &pc_reco_z);
  }

  // Per-systematic-universe weight dump (UQ Stage-1 #7). Builds two
  // parallel branch tables — one for truth-mode weights, one for
  // reco-mode weights — over the same (band, idx) universes from
  // errorBands. The MNV101_DUMP_UNIVERSES allowlist applies to both;
  // each event evaluates 2*N_universes extra model.GetWeight() calls.
  const auto uniAllow = ParseUniverseAllowlist(getenv("MNV101_DUMP_UNIVERSES"));
  std::vector<UniverseBranchInfo> uniTruthBranches;
  std::vector<UniverseBranchInfo> uniRecoBranches;
  std::vector<double> uniTruthWeights;
  std::vector<double> uniRecoWeights;
  // Lateral kinematic shadow arrays, parallel to the branch tables.
  // For truth-mode entries we dump universe-shifted truth pT/pz as
  // MC_<band>_<idx>/MC_pz_<band>_<idx>; for reco-mode entries we dump
  // universe-shifted reco pT/pz as sim_<band>_<idx>/sim_pz_<band>_<idx>.
  std::vector<double> uniTruthLatPT, uniTruthLatPZ, uniTruthLatQ3;
  std::vector<double> uniRecoLatPT,  uniRecoLatPZ,  uniRecoLatQ3;
  size_t nLatTruth = 0, nLatReco = 0;
  const bool dumpUniverses = (getenv("MNV101_DUMP_UNIVERSES") != nullptr) &&
                             (errorBands != nullptr);
  if(dumpUniverses)
  {
    uniTruthBranches = BuildUniverseBranchTable(
        *errorBands, "truth", UniverseKineContext::RecoTreeTruth,
        uniAllow.first, uniAllow.second);
    uniRecoBranches = BuildUniverseBranchTable(
        *errorBands, "reco", UniverseKineContext::RecoTreeReco,
        uniAllow.first, uniAllow.second);
    uniTruthWeights.assign(uniTruthBranches.size(), 1.0);
    uniRecoWeights.assign(uniRecoBranches.size(),  1.0);
    uniTruthLatPT.assign(uniTruthBranches.size(),  0.0);
    uniTruthLatPZ.assign(uniTruthBranches.size(),  0.0);
    uniTruthLatQ3.assign(uniTruthBranches.size(),  0.0);
    uniRecoLatPT.assign(uniRecoBranches.size(),    0.0);
    uniRecoLatPZ.assign(uniRecoBranches.size(),    0.0);
    uniRecoLatQ3.assign(uniRecoBranches.size(),    0.0);
    for(size_t k = 0; k < uniTruthBranches.size(); ++k)
    {
      out->Branch(uniTruthBranches[k].branchName.c_str(), &uniTruthWeights[k]);
      if(uniTruthBranches[k].isLateral)
      {
        out->Branch(uniTruthBranches[k].ptBranchName.c_str(), &uniTruthLatPT[k]);
        out->Branch(uniTruthBranches[k].pzBranchName.c_str(), &uniTruthLatPZ[k]);
        out->Branch(uniTruthBranches[k].q3BranchName.c_str(), &uniTruthLatQ3[k]);
        ++nLatTruth;
      }
    }
    for(size_t k = 0; k < uniRecoBranches.size(); ++k)
    {
      out->Branch(uniRecoBranches[k].branchName.c_str(), &uniRecoWeights[k]);
      if(uniRecoBranches[k].isLateral)
      {
        out->Branch(uniRecoBranches[k].ptBranchName.c_str(), &uniRecoLatPT[k]);
        out->Branch(uniRecoBranches[k].pzBranchName.c_str(), &uniRecoLatPZ[k]);
        out->Branch(uniRecoBranches[k].q3BranchName.c_str(), &uniRecoLatQ3[k]);
        ++nLatReco;
      }
    }
    std::cout << "  Universe-weight dump enabled: "
              << uniTruthBranches.size() << " truth-mode + "
              << uniRecoBranches.size() << " reco-mode (band,idx) branches "
              << "written to " << out->GetName() << " ("
              << nLatTruth << " lateral truth + "
              << nLatReco  << " lateral reco with shifted pT/pz).\n";
  }

  std::cout << "Starting unbinned MC selected-signal-reco loop (reco tree)...\n";
  const int nEntries = reco->GetEntries();

  // Phase 18.2: mirror the truth-denom dedupe (Phase 18.1) on the reco side.
  // AnaTuple files such as run00111353_Playlist.root double-fill some events,
  // so the same (mc_run, mc_subrun, mc_nthEvtInFile) key can appear twice on
  // the reco tree too. Without this dedupe, mc_signal_reco picks up a small
  // count surplus over mc_truth_denom (7 events at MEFHC scale = 0.2 ppm),
  // which prevents `c` from landing at exactly 1 by construction.
  std::unordered_set<uint64_t> seenRecoKeys;
  long nDupRecoSkipped = 0;

  for(int i = 0; i < nEntries; ++i)
  {
    if(i % 10000 == 0) std::cout << i << " / " << nEntries << "\r" << std::flush;

    // set entry
    CVUniverse::SetTruth(false);
    MichelEvent evt;
    recoCV->SetEntry(i);
    model.SetEntry(*recoCV, evt);
    
    // --- truth mode: determine signal + phase space + truth weight
    CVUniverse::SetTruth(true);
    const double w_truth_tmp = model.GetWeight(*recoCV, evt);
    
    const bool isSignalTruth = michelcuts.isSignal(*recoCV, w_truth_tmp);
    if(!isSignalTruth) continue; // keep only signal for this tree 
    
    const bool inPhaseSpace = michelcuts.isEfficiencyDenom(*recoCV, w_truth_tmp);
    
    MC      = recoCV->GetMuonPTTrue();   // truth p_T (GeV/c)
    MC_pz   = recoCV->GetMuonPzTrue();  // truth p_|| (GeV/c)
    MC_eavail = recoCV->GetEAvailableTrue() / 1000.0;  // MeV -> GeV
    MC_q3   = recoCV->Getq3True() / 1000.0;            // MeV -> GeV
    w_truth = w_truth_tmp;

    // --- reco mode: selection + reco weight + reco value
    CVUniverse::SetTruth(false);
    const double w_reco_tmp = model.GetWeight(*recoCV, evt);
    const bool passesReco = michelcuts.isMCSelected(*recoCV, evt, w_reco_tmp).all();

    w_reco   = w_reco_tmp;
    sim_pass = passesReco;
    sim      = passesReco ? recoCV->GetMuonPT() : -9999.0;
    sim_pz   = passesReco ? recoCV->GetMuonPz() : -9999.0;
    sim_eavail = passesReco ? recoCV->NewEavail() / 1000.0 : -9999.0;  // MeV -> GeV
    sim_q3   = passesReco ? recoCV->RecoQ3() / 1000.0 : -9999.0;       // MeV -> GeV
    
    // --- KEEP event only if BOTH of these hold:
    //   1. recoCV.isEfficiencyDenom (CCInclusive2DPhaseSpace evaluated on
    //      the reco-tree's mc_* branches)
    //   2. Phase 18: the event's (mc_run, mc_subrun, mc_nthEvtInFile) key is
    //      in truthDenomIDs, i.e. the SAME event also passes the cut when
    //      evaluated on the truth tree's mc_* branches.
    //
    // Without (2), ~1.8% of reco entries pass (1) but their truth-tree row
    // fails the same cut (likely because mc_primFSLepton differs between
    // the two trees for events with secondary muons). Those events appear
    // in mc_signal_reco but not in mc_truth_denom — inflating c_global and
    // biasing the OmniFold response. The gate makes truth-tree authoritative.
    //
    // OmniFold has no fake-row concept, so reco-pass-truth-PS-fail events
    // (passesReco && !inPhaseSpace) must NOT enter mc_signal_reco either —
    // condition (1) already enforces that.
    uint64_t key = 0;
    bool haveKey = false;
    if(inPhaseSpace)
    {
      key = makeEventKey(
          recoCV->GetInt("mc_run"),
          recoCV->GetInt("mc_subrun"),
          recoCV->GetInt("mc_nthEvtInFile"));
      haveKey = true;
    }
    const bool truthAgrees = (truthDenomIDs == nullptr) ||
                             (haveKey && truthDenomIDs->find(key) != truthDenomIDs->end());
    if(inPhaseSpace && truthAgrees)
    {
      if(!seenRecoKeys.insert(key).second)
      {
        ++nDupRecoSkipped;
        continue;
      }
      if(dumpUniverses)
      {
        // Truth-mode universe weights: same context as the CV w_truth_tmp
        // computation above (CVUniverse::SetTruth(true)).
        CVUniverse::SetTruth(true);
        for(size_t k = 0; k < uniTruthBranches.size(); ++k)
        {
          CVUniverse* u = uniTruthBranches[k].univ;
          u->SetEntry(i);
          MichelEvent uEvt;
          model.SetEntry(*u, uEvt);
          uniTruthWeights[k] = model.GetWeight(*u, uEvt);
          if(uniTruthBranches[k].isLateral)
          {
            uniTruthLatPT[k] = u->GetMuonPTTrue();
            uniTruthLatPZ[k] = u->GetMuonPzTrue();
            uniTruthLatQ3[k] = u->Getq3True() / 1000.0;  // MeV -> GeV (truth q3)
          }
        }
        // Reco-mode universe weights: CVUniverse::SetTruth(false).
        CVUniverse::SetTruth(false);
        for(size_t k = 0; k < uniRecoBranches.size(); ++k)
        {
          CVUniverse* u = uniRecoBranches[k].univ;
          u->SetEntry(i);
          MichelEvent uEvt;
          model.SetEntry(*u, uEvt);
          uniRecoWeights[k] = model.GetWeight(*u, uEvt);
          if(uniRecoBranches[k].isLateral)
          {
            uniRecoLatPT[k] = u->GetMuonPT();
            uniRecoLatPZ[k] = u->GetMuonPz();
            uniRecoLatQ3[k] = u->RecoQ3() / 1000.0;  // MeV -> GeV (reco q3)
          }
        }
        // Restore CV state for downstream code that may still consult
        // recoCV in this iteration (the duplicate-key check has already
        // run, but be defensive against future edits).
        recoCV->SetEntry(i);
        model.SetEntry(*recoCV, evt);
      }
      if(dumpPC){
        CVUniverse::SetTruth(true);
        recoCV->GetTruthFSHadrons(pc_gen_E, pc_gen_px, pc_gen_py, pc_gen_pz, pc_gen_pdg);
        CVUniverse::SetTruth(false);
        recoCV->GetRecoClusters(pc_reco_E, pc_reco_x, pc_reco_y, pc_reco_z);
      }
      out->Fill();
      if(outRecoIDs) outRecoIDs->insert(key);
    }

  }

  std::cout << "Finished unbinned MC selected-signal-reco loop.\n";
  if(nDupRecoSkipped > 0)
    std::cout << "  WARN: skipped " << nDupRecoSkipped
              << " duplicate-key reco entries (upstream AnaTuple double-fill).\n";
  if(outRecoIDs)
    std::cout << "  Captured " << outRecoIDs->size()
              << " unique event IDs from mc_signal_reco.\n";
}


// MC background: events that pass reco selection but are NOT signal.
// This is NOT truth-aligned; it's just a flat list of selected background reco values.
void LoopAndFillUnbinnedMCBackground(
    PlotUtils::ChainWrapper* reco,
    CVUniverse* recoCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    PlotUtils::Model<CVUniverse, MichelEvent>& model,
    TTree* out)
{
  double sim_background = 0.0;
  double sim_background_pz = 0.0;
  double sim_background_eavail = 0.0;
  double sim_background_q3 = 0.0;
  UChar_t sim_background_pass = true;
  double w_bkg = 1.0;

  out->Branch("sim_background", &sim_background);
  out->Branch("sim_background_pz", &sim_background_pz);
  out->Branch("sim_background_eavail", &sim_background_eavail);  // reco Eavail (GeV)
  out->Branch("sim_background_q3", &sim_background_q3);          // reco q3 (GeV)
  out->Branch("sim_background_pass", &sim_background_pass);
  out->Branch("w_bkg", &w_bkg);

  std::cout << "Starting unbinned MC background reco loop...\n";
  const int nEntries = reco->GetEntries();
  for(int i = 0; i < nEntries; ++i)
  {
    CVUniverse::SetTruth(false);
    MichelEvent cvEvent;
    recoCV->SetEntry(i);
    model.SetEntry(*recoCV, cvEvent);

    const double cvWeight = model.GetWeight(*recoCV, cvEvent);

    if(!michelcuts.isMCSelected(*recoCV, cvEvent, cvWeight).all()) continue;

    // Skip only if the event is CC-inclusive signal AND in the 2D fiducial PS.
    // Events that are CC-inclusive signal but fail the 2D PS (e.g. truth vertex
    // outside the tracker fiducial, theta_mu >= 20 deg, or p_|| < 1500 MeV) are
    // reco-fakes from the analysis-PS perspective and belong in mc_background
    // so they are subtracted from the data spectrum like any other background.
    const bool isSignal = michelcuts.isSignal(*recoCV, cvWeight);
    const bool inPS_bkg = michelcuts.isEfficiencyDenom(*recoCV, cvWeight);
    if(isSignal && inPS_bkg) continue;

    sim_background = recoCV->GetMuonPT();       // reco p_T (GeV/c)
    sim_background_pz = recoCV->GetMuonPz();    // reco p_|| (GeV/c)
    sim_background_eavail = recoCV->NewEavail() / 1000.0;  // MeV -> GeV
    sim_background_q3 = recoCV->RecoQ3() / 1000.0;         // MeV -> GeV
    w_bkg = cvWeight;
    out->Fill();
  }
  std::cout << "Finished unbinned MC background reco loop.\n";
}

// Data: selected reco events.
void LoopAndFillUnbinnedData(
    PlotUtils::ChainWrapper* data,
    CVUniverse* dataCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    TTree* out)
{
  double measured = 0.0;
  double measured_pz = 0.0;
  double measured_eavail = 0.0;
  double measured_q3 = 0.0;
  UChar_t measured_pass = true; // Only filled for selected data events
  out->Branch("measured", &measured);
  out->Branch("measured_pz", &measured_pz);
  out->Branch("measured_eavail", &measured_eavail);  // reco available energy (GeV)
  out->Branch("measured_q3", &measured_q3);          // reco 3-momentum transfer (GeV)
  out->Branch("measured_pass", &measured_pass);

  // Phase 3 point-cloud dump (gated): per-event reco-cluster vectors for data
  // (the measured point cloud; no truth on data).
  const bool dumpPC = (getenv("MNV101_DUMP_POINTCLOUD") != nullptr);
  std::vector<double> pc_reco_E, pc_reco_x, pc_reco_y, pc_reco_z;
  if(dumpPC){
    out->Branch("part_reco_E", &pc_reco_E);
    out->Branch("part_reco_x", &pc_reco_x);
    out->Branch("part_reco_y", &pc_reco_y);
    out->Branch("part_reco_z", &pc_reco_z);
  }

  std::cout << "Starting unbinned data reco loop...\n";
  const int nEntries = data->GetEntries();
  for(int i = 0; i < nEntries; ++i)
  {
    if(i % 10000 == 0) std::cout << i << " / " << nEntries << "\r" << std::flush;

    CVUniverse::SetTruth(false);
    dataCV->SetEntry(i);
    MichelEvent event;
    if(!michelcuts.isDataSelected(*dataCV, event).all()) continue;

    measured = dataCV->GetMuonPT();       // reco p_T (GeV/c)
    measured_pz = dataCV->GetMuonPz();   // reco p_|| (GeV/c)
    measured_eavail = dataCV->NewEavail() / 1000.0;  // MeV -> GeV
    measured_q3 = dataCV->RecoQ3() / 1000.0;         // MeV -> GeV
    if(dumpPC)
      dataCV->GetRecoClusters(pc_reco_E, pc_reco_x, pc_reco_y, pc_reco_z);
    out->Fill();
  }
  std::cout << "Finished unbinned data reco loop.\n";
}

//Returns false if recoTreeName could not be inferred
bool inferRecoTreeNameAndCheckTreeNames(const std::string& mcPlaylistName, const std::string& dataPlaylistName, std::string& recoTreeName)
{
  const std::vector<std::string> knownTreeNames = {"Truth", "Meta"};
  bool areFilesOK = false;

  std::ifstream playlist(mcPlaylistName);
  std::string firstFile = "";
  playlist >> firstFile;
  auto testFile = TFile::Open(firstFile.c_str());
  if(!testFile)
  {
    std::cerr << "Failed to open the first MC file at " << firstFile << "\n";
    return false;
  }

  const auto truthTree = testFile->Get("Truth");
  if(truthTree == nullptr || !truthTree->IsA()->InheritsFrom(TClass::GetClass("TTree")))
  {
    std::cerr << "Could not find the \"Truth\" tree in MC file named " << firstFile << "\n";
    return false;
  }

  for(auto key: *testFile->GetListOfKeys())
  {
    if(static_cast<TKey*>(key)->ReadObj()->IsA()->InheritsFrom(TClass::GetClass("TTree"))
       && std::find(knownTreeNames.begin(), knownTreeNames.end(), key->GetName()) == knownTreeNames.end())
    {
      recoTreeName = key->GetName();
      areFilesOK = true;
    }
  }
  delete testFile;
  testFile = nullptr;

  playlist.open(dataPlaylistName);
  playlist >> firstFile;
  testFile = TFile::Open(firstFile.c_str());
  if(!testFile)
  {
    std::cerr << "Failed to open the first data file at " << firstFile << "\n";
    return false;
  }

  const auto recoTree = testFile->Get(recoTreeName.c_str());
  if(recoTree == nullptr || !recoTree->IsA()->InheritsFrom(TClass::GetClass("TTree")))
  {
    std::cerr << "Could not find the \"" << recoTreeName << "\" tree in data file named " << firstFile << "\n";
    return false;
  }

  return areFilesOK;
}

//==============================================================================
// Main
//==============================================================================
int main(const int argc, const char** argv)
{
  TH1::AddDirectory(false);

  const int nArgsExpected = 2;
  if(argc != nArgsExpected + 1)
  {
    std::cerr << "Expected " << nArgsExpected << " arguments, but got " << argc - 1 << "\n" << USAGE << "\n";
    return badCmdLine;
  }

  const std::string mc_file_list = argv[2],
                    data_file_list = argv[1];

  std::string reco_tree_name;
  if(!inferRecoTreeNameAndCheckTreeNames(mc_file_list, data_file_list, reco_tree_name))
  {
    std::cerr << "Failed to find required trees in MC playlist " << mc_file_list << " and/or data playlist " << data_file_list << ".\n" << USAGE << "\n";
    return badInputFile;
  }

  PlotUtils::MacroUtil options(reco_tree_name, mc_file_list, data_file_list, "minervame1A", true);
  options.m_plist_string = util::GetPlaylist(*options.m_mc, true);

  PlotUtils::MinervaUniverse::SetNuEConstraint(true);
  PlotUtils::MinervaUniverse::SetPlaylist(options.m_plist_string);
  PlotUtils::MinervaUniverse::SetAnalysisNuPDG(14);
  PlotUtils::MinervaUniverse::SetNFluxUniverses(100);
  PlotUtils::MinervaUniverse::SetZExpansionFaReweight(false);
  PlotUtils::MinervaUniverse::RPAMaterials(true);

  PlotUtils::Cutter<CVUniverse, MichelEvent>::reco_t sidebands, preCuts;
  PlotUtils::Cutter<CVUniverse, MichelEvent>::truth_t signalDefinition, phaseSpace;

  const double minZ = 5980, maxZ = 8422, apothem = 850;

  preCuts.emplace_back(new reco::ZRange<CVUniverse, MichelEvent>("Tracker", minZ, maxZ));
  preCuts.emplace_back(new reco::Apothem<CVUniverse, MichelEvent>(apothem));
  preCuts.emplace_back(new reco::MaxMuonAngle<CVUniverse, MichelEvent>(20.));
  preCuts.emplace_back(new reco::HasMINOSMatch<CVUniverse, MichelEvent>());
  preCuts.emplace_back(new reco::NoDeadtime<CVUniverse, MichelEvent>(1, "Deadtime"));
  preCuts.emplace_back(new reco::IsNeutrino<CVUniverse, MichelEvent>());

  signalDefinition.emplace_back(new truth::IsNeutrino<CVUniverse>());
  signalDefinition.emplace_back(new truth::IsCC<CVUniverse>());

  phaseSpace.emplace_back(new truth::ZRange<CVUniverse>("Tracker", minZ, maxZ));
  phaseSpace.emplace_back(new truth::Apothem<CVUniverse>(apothem));
  phaseSpace.emplace_back(new truth::MuonAngle<CVUniverse>(20.));
  phaseSpace.emplace_back(new truth::PZMuMin<CVUniverse>(1500.));    // p_|| > 1.5 GeV (MeV units)
  phaseSpace.emplace_back(new MaxPzMu<CVUniverse>(60000.));          // p_|| < 60 GeV (MeV units)
  phaseSpace.emplace_back(new MaxPtMu<CVUniverse>(4500.));           // p_T < 4.5 GeV (MeV units)

  PlotUtils::Cutter<CVUniverse, MichelEvent> mycuts(std::move(preCuts), std::move(sidebands), std::move(signalDefinition), std::move(phaseSpace));

  std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse, MichelEvent>>> MnvTunev1;
  MnvTunev1.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, MichelEvent>());
  MnvTunev1.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, MichelEvent>(true, false));
  MnvTunev1.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, MichelEvent>());
  MnvTunev1.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, MichelEvent>());
  MnvTunev1.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, MichelEvent>());

  // Capture raw observer pointers to each reweighter BEFORE std::move so
  // the truth-denom loop can dump per-reweighter weights without going
  // through the (collapsed) Model::GetWeight product. The unique_ptrs
  // move into Model and keep the underlying objects alive.
  std::vector<PlotUtils::Reweighter<CVUniverse, MichelEvent>*> tuneComponents;
  for(auto& rw : MnvTunev1) tuneComponents.push_back(rw.get());

  PlotUtils::Model<CVUniverse, MichelEvent> model(std::move(MnvTunev1));

  const bool doSystematics = (getenv("MNV101_SKIP_SYST") == nullptr);
  if(!doSystematics){
    std::cout << "Skipping systematics loops (CV-only output) because MNV101_SKIP_SYST is set.\n";
    PlotUtils::MinervaUniverse::SetNFluxUniverses(2);
  }

  std::map<std::string, std::vector<CVUniverse*>> error_bands;
  if(doSystematics) error_bands = GetStandardSystematics(options.m_mc);
  error_bands["cv"] = {new CVUniverse(options.m_mc)};

  std::map<std::string, std::vector<CVUniverse*>> truth_bands;
  if(doSystematics) truth_bands = GetStandardSystematics(options.m_truth);
  truth_bands["cv"] = {new CVUniverse(options.m_truth)};

  // Diagnostic: print the GetStandardSystematics inventory once so a fresh
  // dump-all rebuild documents which bands are present and which are lateral.
  if(doSystematics)
  {
    std::cout << "GetStandardSystematics inventory ("
              << error_bands.size() << " bands incl. cv):\n";
    for(const auto& kv : error_bands)
    {
      const auto& v = kv.second;
      const bool vert = v.empty() ? true : v.front()->IsVerticalOnly();
      std::cout << "  " << kv.first << "  n=" << v.size()
                << "  IsVerticalOnly=" << (vert ? "true" : "false") << "\n";
    }
  }

  CVUniverse* data_universe = new CVUniverse(options.m_data);

  try
  {
    TFile* outFile = TFile::Open(OUT_FILE_NAME, "RECREATE");
    if(!outFile)
    {
      std::cerr << "Failed to open " << OUT_FILE_NAME << " for writing.\n";
      return badOutputFile;
    }

    outFile->cd();

    // ---- Save POT info (single-file output => must use distinct keys) ----
    auto mcPOT   = new TParameter<double>("mcPOTUsed",   options.m_mc_pot);
    auto dataPOT = new TParameter<double>("dataPOTUsed", options.m_data_pot);
    mcPOT->Write();
    dataPOT->Write();
    
    // Do not write pTmu_fiducial_nucleons here. In the documented full-MEFHC
    // workflow these per-playlist ROOT files are merged with hadd, which sums
    // TParameter<double> objects and silently multiplies the fiducial nucleon
    // count by the number of playlists. The 2D Python extraction now uses the
    // known tracker-geometry constant directly to avoid merge-sensitive
    // metadata.


    TTree* mcTruthTree = new TTree("mc_truth_denom", "Truth efficiency denominator: MC, w_truth");
    TTree* mcSigTree   = new TTree("mc_signal_reco", "Selected signal reco: sim, sim_pass, w_reco");

    TTree* mcBkgTree = new TTree("mc_background", "Selected MC background reco: sim_background, sim_background_pass");
    TTree* dataTree = new TTree("data", "Selected data reco: measured, measured_pass");

    assert(error_bands["cv"].size() == 1);
    //assert(truth_bands["cv"].size() == 1);
    auto* recoCV  = error_bands["cv"].front();
    auto* truthCV = truth_bands["cv"].front();

    // MNV101_TRUTH_ONLY short-circuits the slow reco loops so the
    // truth-denom + per-reweighter dump can be regenerated quickly for
    // the Option 1 decomposition diagnostic.
    const bool truthOnly = (getenv("MNV101_TRUTH_ONLY") != nullptr);

    // Phase 18 (2026-05): the truth-denom walk runs FIRST and collects
    // `truthDenomIDs` (the set of (mc_run, mc_subrun, mc_nthEvtInFile)
    // packed keys for events that pass truth-tree-side isEfficiencyDenom)
    // and a cache of truth-denom entries for later miss-append. The reco
    // walk then runs second, gated on truthDenomIDs membership so the
    // truth tree's cut evaluation is authoritative — this resolves the
    // ~1.8% c_global discrepancy caused by recoCV/truthCV disagreeing on
    // isEfficiencyDenom for the same physics event (most likely
    // mc_primFSLepton differing between the two trees when reco matches a
    // secondary muon). AppendTruthOnlyMisses then walks the cache and
    // writes a miss entry to mc_signal_reco for each truth-denom event not
    // captured by the reco loop. With both pieces, OmniFold's step-2 miss
    // regression handles miss events natively, and the per-bin
    // completeness (c) correction in the Python pipeline becomes a no-op.
    //
    // MNV101_DISABLE_TRUTH_MISSES: set to keep the legacy behaviour
    // (no miss-append; downstream pipeline must apply the c correction).
    const bool disableTruthMisses = (getenv("MNV101_DISABLE_TRUTH_MISSES") != nullptr);
    const bool appendTruthMisses = !truthOnly && !disableTruthMisses;

    std::unordered_set<uint64_t> recoIDs;
    std::unordered_set<uint64_t> truthDenomIDs;
    std::vector<TruthDenomEntry> truthDenomCache;

    LoopAndFillUnbinnedMCTruthDenom(
        options.m_truth, truthCV, mycuts, model, tuneComponents, mcTruthTree,
        !truthOnly ? &truthDenomIDs : nullptr,
        appendTruthMisses ? &truthDenomCache : nullptr,
        &truth_bands);

    if(!truthOnly)
    {
      LoopAndFillUnbinnedMCSelectedSignalReco(
          options.m_mc, recoCV, mycuts, model, mcSigTree,
          appendTruthMisses ? &recoIDs : nullptr,
          &truthDenomIDs,
          &error_bands);
    }

    long nTruthOnlyMisses = 0;
    if(appendTruthMisses)
      nTruthOnlyMisses = AppendTruthOnlyMisses(mcSigTree, truthDenomCache, recoIDs);

    if(!truthOnly)
    {
      LoopAndFillUnbinnedMCBackground(options.m_mc, recoCV, mycuts, model, mcBkgTree);
      LoopAndFillUnbinnedData(options.m_data, data_universe, mycuts, dataTree);
    }
    else
    {
      std::cout << "MNV101_TRUTH_ONLY set: skipping reco signal/background/data loops.\n";
    }

    // Flag for downstream pipeline: when set, mc_signal_reco contains
    // truth-only miss entries (Phase 17) and the per-bin c correction in
    // unfold_2d_omnifold_unbinned.py becomes a no-op. nTruthOnlyMisses is
    // diagnostic only. cd back to outFile because the loops above (in
    // particular the RPA reweighter) open auxiliary ROOT files and leave
    // gDirectory pointing at one of them — a bare TParameter::Write()
    // would otherwise try to write into a read-only data file.
    outFile->cd();
    auto pHasMisses = new TParameter<int>(
        "hasTruthOnlyMisses", appendTruthMisses ? 1 : 0);
    auto pNMisses = new TParameter<long>(
        "nTruthOnlyMisses", nTruthOnlyMisses);
    pHasMisses->Write();
    pNMisses->Write();

    outFile->Write();
    outFile->Close();

    std::cout << "Wrote unbinned unfolding inputs to " << OUT_FILE_NAME << "\n";
    std::cout << "Success\n";
  }
  catch(const ROOT::exception& e)
  {
    std::cerr << "Ending on a ROOT error message.  No output will be produced.\n"
              << e.what() << "\n" << USAGE << "\n";
    return badFileRead;
  }

  return success;
}
