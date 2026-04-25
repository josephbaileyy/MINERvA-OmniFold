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

//==============================================================================
// Loop and Fill (write only the unbinned arrays needed for OmniFold)
//==============================================================================

// Truth efficiency denominator: loop Truth tree in truth-mode and fill MC truth pTmu + weight
void LoopAndFillUnbinnedMCTruthDenom(
    PlotUtils::ChainWrapper* truth,
    CVUniverse* truthCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    PlotUtils::Model<CVUniverse, MichelEvent>& model,
    const std::vector<PlotUtils::Reweighter<CVUniverse, MichelEvent>*>& componentRWs,
    TTree* out)
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
  const int nEntries = truth->GetEntries();

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

    MC = truthCV->GetMuonPTTrue();      // truth p_T (GeV/c)
    MC_pz = truthCV->GetMuonPzTrue();   // truth p_|| (GeV/c)
    w_truth = model.GetWeight(*truthCV, evt);
    if(dumpComponents)
    {
      for(size_t k = 0; k < componentRWs.size(); ++k)
        w_component[k] = componentRWs[k]->GetWeight(*truthCV, evt);
    }

    out->Fill();
  }

  std::cout << "Finished unbinned MC truth-denom loop.\n";
}

// Selected signal reco: loop reco MC tree in reco-mode and fill reco pTmu + weight
void LoopAndFillUnbinnedMCSelectedSignalReco(
    PlotUtils::ChainWrapper* reco,
    CVUniverse* recoCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    PlotUtils::Model<CVUniverse, MichelEvent>& model,
    TTree* out)
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
    
    // --- KEEP event if:
    //   A) in phase space (pass or miss)  -> lets Python fill Fill or Miss
    //   B) OR passesReco but out of phase space -> lets Python fill Fake
    if(inPhaseSpace || passesReco)
      out->Fill();

  }

  std::cout << "Finished unbinned MC selected-signal-reco loop.\n";
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

    const bool isSignal = michelcuts.isSignal(*recoCV, cvWeight);
    if(isSignal) continue;

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

    LoopAndFillUnbinnedMCTruthDenom(options.m_truth, truthCV, mycuts, model, tuneComponents, mcTruthTree);

    // MNV101_TRUTH_ONLY short-circuits the slow reco loops so the
    // truth-denom + per-reweighter dump can be regenerated quickly for
    // the Option 1 decomposition diagnostic.
    const bool truthOnly = (getenv("MNV101_TRUTH_ONLY") != nullptr);
    if(!truthOnly)
    {
      LoopAndFillUnbinnedMCSelectedSignalReco(options.m_mc, recoCV, mycuts, model, mcSigTree);

      LoopAndFillUnbinnedMCBackground(options.m_mc, recoCV, mycuts, model, mcBkgTree);
      LoopAndFillUnbinnedData(options.m_data, data_universe, mycuts, dataTree);
    }
    else
    {
      std::cout << "MNV101_TRUTH_ONLY set: skipping reco signal/background/data loops.\n";
    }

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
