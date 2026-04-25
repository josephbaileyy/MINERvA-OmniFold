#define OUT_FILE_NAME "runEventLoopOmniFold.root"

#define USAGE \
"\n*** USAGE ***\n"\
"runEventLoop <dataPlaylist.txt> <mcPlaylist.txt>\n\n"\
"*** Explanation ***\n"\
"Reduce MasterAnaDev AnaTuples to unbinned event-level arrays for OmniFold-style unfolding.\n\n"\
"*** The Input Files ***\n"\
"Playlist files are plaintext files with 1 file name per line.  Filenames may be\n"\
"xrootd URLs or refer to the local filesystem.  The first playlist file's\n"\
"entries will be treated like data, and the second playlist's entries must\n"\
"have the \"Truth\" tree to use for calculating the efficiency denominator.\n\n"\
"*** Output ***\n"\
"Produces a single ROOT file, " OUT_FILE_NAME ", containing TTrees with the\n"\
"unbinned arrays needed for OmniFold-style unfolding.  This variant does NOT\n"\
"write the standard ExtractCrossSection histogram suite.\n\n"\
"*** Environment Variables ***\n"\
"Setting up this package appends to PATH and LD_LIBRARY_PATH.  PLOTUTILSROOT,\n"\
"MPARAMFILESROOT, and MPARAMFILES must be set according to the setup scripts in\n"\
"those packages for systematics and flux reweighters to function.\n\n"\
"*** Return Codes ***\n"\
"0 indicates success.\n"

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
#include "util/GetPlaylist.h"
#include "cuts/SignalDefinition.h"
#include "cuts/q3RecoCut.h"

//PlotUtils includes
#include "PlotUtils/makeChainWrapper.h"
#include "PlotUtils/MacroUtil.h"
#include "PlotUtils/CrashOnROOTMessage.h"
#include "PlotUtils/Cutter.h"
#include "PlotUtils/Model.h"
#include "PlotUtils/FluxAndCVReweighter.h"
#include "PlotUtils/GENIEReweighter.h"
#include "PlotUtils/LowRecoil2p2hReweighter.h"
#include "PlotUtils/RPAReweighter.h"
#include "PlotUtils/MINOSEfficiencyReweighter.h"
#pragma GCC diagnostic pop

//ROOT includes
#include "TFile.h"
#include "TTree.h"
#include "TKey.h"
#include "TClass.h"

//c++ includes
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <algorithm>
#include <cassert>

//==============================================================================
// Loop and Fill (write only the unbinned arrays needed for OmniFold)
//==============================================================================

// MC: truth-phase-space (efficiency denominator) events, aligned by truth entry.
//     For each truth event:
//       - MC:        truth pTmu
//       - sim:       reco pTmu if selected at reco, otherwise sentinel
//       - sim_pass:  whether it passed reco selection
void LoopAndFillUnbinnedMCSignal(
    PlotUtils::ChainWrapper* truth,
    CVUniverse* truthCV,
    PlotUtils::ChainWrapper* reco,
    CVUniverse* recoCV,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts,
    PlotUtils::Model<CVUniverse, MichelEvent>& model,
    TTree* out)
{
  double MC = 0.0;
  double sim = -9999.0;
  bool sim_pass = false;
  out->Branch("MC", &MC);
  out->Branch("sim", &sim);
  out->Branch("sim_pass", &sim_pass);

  std::cout << "Starting unbinned MC truth-aligned loop...\n";
  const int nEntries = truth->GetEntries();
  for(int i = 0; i < nEntries; ++i)
  {
    if(i % 10000 == 0) std::cout << i << " / " << nEntries << "\r" << std::flush;

    // Truth entry defines efficiency denominator (signal + phase space)
    CVUniverse::SetTruth(true);
    MichelEvent cvTruthEvent;
    truthCV->SetEntry(i);
    model.SetEntry(*truthCV, cvTruthEvent);
    const double cvTruthWeight = model.GetWeight(*truthCV, cvTruthEvent);

    if(!michelcuts.isEfficiencyDenom(*truthCV, cvTruthWeight)) continue;

    MC = truthCV->GetMuonPTTrue();

    // Evaluate reco selection for same entry on reco tree
    CVUniverse::SetTruth(false);
    MichelEvent recoEvent;
    recoCV->SetEntry(i);
    model.SetEntry(*recoCV, recoEvent);
    const double cvRecoWeight = model.GetWeight(*recoCV, recoEvent);

    const bool passesReco = michelcuts.isMCSelected(*recoCV, recoEvent, cvRecoWeight).all();
    sim_pass = passesReco;
    sim = passesReco ? recoCV->GetMuonPT() : -9999.0;

    out->Fill();
  }
  std::cout << "Finished unbinned MC truth-aligned loop.\n";
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
  bool sim_background_pass = true; // Only filled for selected background events
  out->Branch("sim_background", &sim_background);
  out->Branch("sim_background_pass", &sim_background_pass);

  std::cout << "Starting unbinned MC background reco loop...\n";
  const int nEntries = reco->GetEntries();
  for(int i = 0; i < nEntries; ++i)
  {
    if(i % 10000 == 0) std::cout << i << " / " << nEntries << "\r" << std::flush;

    CVUniverse::SetTruth(false);
    MichelEvent cvEvent;
    recoCV->SetEntry(i);
    model.SetEntry(*recoCV, cvEvent);
    const double cvWeight = model.GetWeight(*recoCV, cvEvent);

    MichelEvent event;
    if(!michelcuts.isMCSelected(*recoCV, event, cvWeight).all()) continue;

    const double weight = model.GetWeight(*recoCV, event);
    const bool isSignal = michelcuts.isSignal(*recoCV, weight);
    if(isSignal) continue;

    sim_background = recoCV->GetMuonPT();
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
  bool measured_pass = true; // Only filled for selected data events
  out->Branch("measured", &measured);
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

    measured = dataCV->GetMuonPT();
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
  phaseSpace.emplace_back(new truth::PZMuMin<CVUniverse>(1500.));

  PlotUtils::Cutter<CVUniverse, MichelEvent> mycuts(std::move(preCuts), std::move(sidebands), std::move(signalDefinition), std::move(phaseSpace));

  std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse, MichelEvent>>> MnvTunev1;
  MnvTunev1.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, MichelEvent>());
  MnvTunev1.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, MichelEvent>(true, false));
  MnvTunev1.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, MichelEvent>());
  MnvTunev1.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, MichelEvent>());
  MnvTunev1.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, MichelEvent>());
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
    TTree* mcTree = new TTree("mc", "Truth-aligned signal MC: MC (truth), sim (reco), sim_pass");
    TTree* mcBkgTree = new TTree("mc_background", "Selected MC background reco: sim_background, sim_background_pass");
    TTree* dataTree = new TTree("data", "Selected data reco: measured, measured_pass");

    assert(error_bands["cv"].size() == 1);
    assert(truth_bands["cv"].size() == 1);
    auto* recoCV  = error_bands["cv"].front();
    auto* truthCV = truth_bands["cv"].front();

    LoopAndFillUnbinnedMCSignal(options.m_truth, truthCV, options.m_mc, recoCV, mycuts, model, mcTree);
    LoopAndFillUnbinnedMCBackground(options.m_mc, recoCV, mycuts, model, mcBkgTree);
    LoopAndFillUnbinnedData(options.m_data, data_universe, mycuts, dataTree);

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
