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
#include <unordered_set>

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
  double w_truth;
  uint64_t key;
};

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
    std::vector<TruthDenomEntry>* outTruthDenomCache = nullptr)
{
  double MC = 0.0;
  double MC_pz = 0.0;
  double w_truth = 1.0;

  out->Branch("MC", &MC);
  out->Branch("MC_pz", &MC_pz);
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

  std::cout << "Starting unbinned MC truth-denom loop (Truth tree)...\n";
  if(outTruthDenomIDs)
    std::cout << "  (collecting truth-denom event IDs for reco-loop gating)\n";
  const int nEntries = truth->GetEntries();

  // Dedupe on (mc_run, mc_subrun, mc_nthEvtInFile). MEHFC playlist 1E file
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
    w_truth = model.GetWeight(*truthCV, evt);
    if(dumpComponents)
    {
      for(size_t k = 0; k < componentRWs.size(); ++k)
        w_component[k] = componentRWs[k]->GetWeight(*truthCV, evt);
    }

    out->Fill();

    if(outTruthDenomIDs) outTruthDenomIDs->insert(key);
    if(outTruthDenomCache)
      outTruthDenomCache->push_back({MC, MC_pz, w_truth, key});
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
  double miss_sim = 0.0, miss_sim_pz = 0.0, miss_w_reco = 1.0;
  double miss_MC = 0.0, miss_MC_pz = 0.0, miss_w_truth = 1.0;
  UChar_t miss_sim_pass = 0;

  sigOut->SetBranchAddress("sim",      &miss_sim);
  sigOut->SetBranchAddress("sim_pz",   &miss_sim_pz);
  sigOut->SetBranchAddress("sim_pass", &miss_sim_pass);
  sigOut->SetBranchAddress("w_reco",   &miss_w_reco);
  sigOut->SetBranchAddress("MC",       &miss_MC);
  sigOut->SetBranchAddress("MC_pz",    &miss_MC_pz);
  sigOut->SetBranchAddress("w_truth",  &miss_w_truth);

  long nTruthOnlyMisses = 0;
  for(const auto& tde : truthDenomCache)
  {
    if(recoIDs.find(tde.key) == recoIDs.end())
    {
      miss_MC       = tde.MC;
      miss_MC_pz    = tde.MC_pz;
      miss_w_truth  = tde.w_truth;
      miss_sim      = -9999.0;
      miss_sim_pz   = -9999.0;
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
    const std::unordered_set<uint64_t>* truthDenomIDs = nullptr)
{
  double sim = 0.0;
  double sim_pz = 0.0;
  UChar_t sim_pass = true;
  double w_reco = 1.0;
  double MC = 0.0;
  double MC_pz = 0.0;
  double w_truth = 1.0;

  out->Branch("sim", &sim);
  out->Branch("sim_pz", &sim_pz);
  out->Branch("sim_pass", &sim_pass);
  out->Branch("w_reco", &w_reco);
  out->Branch("MC", &MC);
  out->Branch("MC_pz", &MC_pz);
  out->Branch("w_truth", &w_truth);

  std::cout << "Starting unbinned MC selected-signal-reco loop (reco tree)...\n";
  const int nEntries = reco->GetEntries();

  // Phase 18.2: mirror the truth-denom dedupe (Phase 18.1) on the reco side.
  // AnaTuple files such as run00111353_Playlist.root double-fill some events,
  // so the same (mc_run, mc_subrun, mc_nthEvtInFile) key can appear twice on
  // the reco tree too. Without this dedupe, mc_signal_reco picks up a small
  // count surplus over mc_truth_denom (7 events at MEHFC scale = 0.2 ppm),
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
    w_truth = w_truth_tmp;

    // --- reco mode: selection + reco weight + reco value
    CVUniverse::SetTruth(false);
    const double w_reco_tmp = model.GetWeight(*recoCV, evt);
    const bool passesReco = michelcuts.isMCSelected(*recoCV, evt, w_reco_tmp).all();

    w_reco   = w_reco_tmp;
    sim_pass = passesReco;
    sim      = passesReco ? recoCV->GetMuonPT() : -9999.0;
    sim_pz   = passesReco ? recoCV->GetMuonPz() : -9999.0;
    
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
  UChar_t sim_background_pass = true;
  double w_bkg = 1.0;

  out->Branch("sim_background", &sim_background);
  out->Branch("sim_background_pz", &sim_background_pz);
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
  UChar_t measured_pass = true; // Only filled for selected data events
  out->Branch("measured", &measured);
  out->Branch("measured_pz", &measured_pz);
  out->Branch("measured_pass", &measured_pass);

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
    
    // Do not write pTmu_fiducial_nucleons here. In the documented full-MEHFC
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
        appendTruthMisses ? &truthDenomCache : nullptr);

    if(!truthOnly)
    {
      LoopAndFillUnbinnedMCSelectedSignalReco(
          options.m_mc, recoCV, mycuts, model, mcSigTree,
          appendTruthMisses ? &recoIDs : nullptr,
          &truthDenomIDs);
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
