//==============================================================================
// MINERvA Analysis Toolkit "Minimum Adoption" Event Loop Example
//
// "Minimum adoption" means that it only uses the two essential MAT tools:
// Universes and HistWrappers. For an "full adoption" example that additionally
// makes use of Cuts, MacroUtil, and Variable, refer to the example in
// ../MAT_Tutorial/.
//
// This script follows the canonical event-looping structure:
// Setup (I/O, variables, histograms, systematics)
// Loop events
//   loop universes
//     make cuts
//     loop variables
//       fill histograms
// Plot and Save
//==============================================================================


//PlotUtils includes
//No junk from PlotUtils please!  I already
//know that MnvH1D does horrible horrible things.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Woverloaded-virtual"

#include "event/CVUniverse.h"
#include "systematics/Systematics.h"
#include "cuts/MaxPzMu.h"

#include "PlotUtils/makeChainWrapper.h"
#include "PlotUtils/HistWrapper.h"
#include "PlotUtils/Hist2DWrapper.h"
#include "PlotUtils/MacroUtil.h"
#include "PlotUtils/MnvPlotter.h"
#include "PlotUtils/cuts/CCInclusiveCuts.h"
#include "PlotUtils/cuts/CCInclusiveSignal.h"
#include "util/Categorized.h"
#include "PlotUtils/Cutter.h"
#include "util/Variable.h"
#include "util/Variable2D.h"
#include "cuts/BestMichelDistance.h"
#include "cuts/BestMichelDistance2D.h"
#include "cuts/SignalDefinition.h"
#include "cuts/q3RecoCut.h"
#include "cuts/hasMichel.h"
#include "studies/Study.h"
#include "studies/PerMichelVarByGENIELabel.h"
#include "studies/PerMichelEventVarByGENIELabel.h" 
#include "studies/CreateDataHistPerMichelEvent.h"
#include "studies/CreateDataHistPerMichel.h"
#include "event/Michel.h"
#include "event/Cluster.h"
#include "event/MichelEvent.h"
#include "event/MatchedMichel.h"
//#include "Binning.h" //TODO: Fix me
#pragma GCC diagnostic pop
#include <iostream>

// Histogram binning constants
const int nbins = 30;
const double xmin = 0.;
const double xmax = 20.e3;

//==============================================================================
// Plot
//==============================================================================
void PlotErrorSummary(PlotUtils::MnvH1D* h, std::string label)
{
  PlotUtils::MnvH1D* hist = (PlotUtils::MnvH1D*)h->Clone("hist");
  PlotUtils::MnvPlotter mnv_plotter( kCompactStyle);
  TCanvas cE("c1", "c1");

  // Group GENIE bands
  mnv_plotter.error_summary_group_map.clear();
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrAbs_N");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrAbs_pi");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrCEx_N");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrCEx_pi");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrElas_N");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrElas_pi");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrInel_N");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_FrPiProd_N");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back(
      "GENIE_FrPiProd_pi");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_MFP_N");
  mnv_plotter.error_summary_group_map["Genie_FSI"].push_back("GENIE_MFP_pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_AGKYxF1pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_AhtBY");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_BhtBY");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_CCQEPauliSupViaKF");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_CV1uBY");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_CV2uBY");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_EtaNCEL");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_MaNCEL");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_MaRES");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_MvRES");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_NormDISCC");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_NormNCRES");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_RDecBR1gamma");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_Rvn1pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_Rvn2pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_Rvn3pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_Rvp1pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_Rvp2pi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_Theta_Delta2Npi");
  mnv_plotter.error_summary_group_map["Genie_InteractionModel"].push_back(
      "GENIE_VecFFCCQEshape");

  mnv_plotter.error_summary_group_map["RPA"].push_back("RPA_HighQ2");
  mnv_plotter.error_summary_group_map["RPA"].push_back("RPA_LowQ2");

  const bool do_fractional_uncertainty = true;
  const bool do_cov_area_norm = false;
  const bool include_stat_error = false;
  const std::string do_fractional_uncertainty_str =
      do_fractional_uncertainty ? std::string("Frac") : std::string("Abs");
  const std::string do_cov_area_norm_str =
      do_cov_area_norm ? std::string("CovAreaNorm") : std::string("");

  mnv_plotter.DrawErrorSummary(hist, "TR", include_stat_error, true,
                              0.0, do_cov_area_norm, "",
                              do_fractional_uncertainty);
  mnv_plotter.AddHistoTitle("Event Selection");
  std::string plotname =
      Form("ErrorSummary_%s_%s_%s", do_fractional_uncertainty_str.c_str(),
           do_cov_area_norm_str.c_str(), label.c_str());
  mnv_plotter.MultiPrint(&cE, plotname, "png");
}

void PlotCVAndError(PlotUtils::MnvH1D* h, std::string label)
{
  PlotUtils::MnvH1D* hist = (PlotUtils::MnvH1D*)h->Clone("hist");
  PlotUtils::MnvPlotter mnv_plotter(PlotUtils::kCCNuPionIncStyle);
  TCanvas cE("c1", "c1");
  if (!gPad)
    throw std::runtime_error("Need a TCanvas. Please make one first.");
  PlotUtils::MnvH1D* datahist = new PlotUtils::MnvH1D(
      "adsf", "", nbins, xmin, xmax);
  bool statPlusSys = true;
  int mcScale = 1.;
  bool useHistTitles = false;
  const PlotUtils::MnvH1D* bkgdHist = NULL;
  const PlotUtils::MnvH1D* dataBkgdHist = NULL;
  mnv_plotter.DrawDataMCWithErrorBand(datahist, hist, mcScale, "TL",
                                     useHistTitles, NULL, NULL, false,
                                     statPlusSys);
  mnv_plotter.AddHistoTitle("Event Selection");
  std::string plotname = Form("CV_w_err_%s", label.c_str());
  mnv_plotter.MultiPrint(&cE, plotname, "png");
  delete datahist;
}

//==============================================================================
// Loop and Fill
//==============================================================================
void LoopAndFillEventSelection(
    PlotUtils::ChainWrapper* chain,
    std::map<std::string, std::vector<CVUniverse*> > error_bands,
    std::vector<Variable*> vars,
    std::vector<Variable2D*> vars2D,
    std::vector<Study*> studies,
    PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts)
{
  std::cout << "Starting MC reco loop...\n";
  for (int i=0; i<chain->GetEntries(); ++i)
  {
    if(i%1000==0) std::cout << (i/1000) << "k\n" << std::flush;

    //=========================================
    // Systematics loop(s)
    //=========================================
    for (auto band : error_bands)
    {
      std::vector<CVUniverse*> error_band_universes = band.second;
      for (auto universe : error_band_universes)
      {
        MichelEvent myevent; // make sure your event is inside the error band loop. 
    
        // Tell the Event which entry in the TChain it's looking at
        universe->SetEntry(i);
        
        // THis is where you would Access/create a Michel

        const double weight = universe->GetWeight(); //TODO: Model/Reweighter

        if (!michelcuts.isMCSelected(*universe, myevent, weight).all()) continue; //all is another function that will later help me with sidebands
        const bool isSignal = michelcuts.isSignal(*universe, weight);

        if(isSignal)
        {
          for(auto& study: studies) study->SelectedSignal(*universe, myevent, weight);
        }

        for(auto& var: vars)
        {
          (*var->m_bestPionByGENIELabel)[universe->GetInteractionType()].FillUniverse(universe, var->GetRecoValue(*universe, myevent.m_idx), universe->GetWeight());

          //Cross section components
          if(isSignal)
          {
            var->efficiencyNumerator->FillUniverse(universe, var->GetTrueValue(*universe), weight);
          }

          //Fill other per-Variable histograms here
          
        }

        for(auto& var: vars2D)
        {
          if(isSignal)
          {
            var->efficiencyNumerator->FillUniverse(universe, var->GetTrueValueX(*universe), var->GetTrueValueY(*universe), weight);
          }
        }
      } // End band's universe loop
    } // End Band loop
  } //End entries loop
  std::cout << "Finished MC reco loop.\n";
}


void LoopAndFillData( PlotUtils::ChainWrapper* data,
			        std::vector<CVUniverse*> data_band,
				std::vector<Variable*> vars,
                                std::vector<Variable2D*> vars2D,
                                std::vector<Study*> studies,
				PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts)

{
  std::cout << "Starting data loop...\n";
  for (auto universe : data_band) {
    for (int i=0; i<data->GetEntries(); ++i) {
      universe->SetEntry(i);
      if(i%1000==0) std::cout << (i/1000) << "k\n" << std::flush;
      MichelEvent myevent; 
      if (!michelcuts.isDataSelected(*universe, myevent).all()) continue;

      for(auto& study: studies) study->Selected(*universe, myevent, 1); 

      for(auto& var: vars)
      {
        var->dataHist->FillUniverse(universe, var->GetRecoValue(*universe, myevent.m_idx), 1);
      }

      for(auto& var: vars2D)
      {
        var->dataHist->FillUniverse(universe, var->GetRecoValueX(*universe), var->GetRecoValueY(*universe), 1);
      }
    }
  }
  std::cout << "Finished data loop.\n";
}



void LoopAndFillEffDenom( PlotUtils::ChainWrapper* truth,
    				std::map<std::string, std::vector<CVUniverse*> > truth_bands,
    				std::vector<Variable*> vars,
                                std::vector<Variable2D*> vars2D,
    				PlotUtils::Cutter<CVUniverse, MichelEvent>& michelcuts)
{
  std::cout << "Starting efficiency denominator loop...\n";
  for (int i=0; i<truth->GetEntries(); ++i)
  {
    if(i%1000==0) std::cout << (i/1000) << "k\n" << std::flush;

    //=========================================
    // Systematics loop(s)
    //=========================================
    for (auto band : truth_bands)
    {
      std::vector<CVUniverse*> truth_band_universes = band.second;
      for (auto universe : truth_band_universes)
      {
        // Tell the Event which entry in the TChain it's looking at
        universe->SetEntry(i);

        const double weight = universe->GetWeight(); //TODO: Model/Reweighter
        if (!michelcuts.isEfficiencyDenom(*universe, weight)) continue; 

        //Fill efficiency denominator now: 
        for(auto var: vars)
        {
          var->efficiencyDenominator->FillUniverse(universe, var->GetTrueValue(*universe), weight);
        }

        for(auto var: vars2D)
        {
          var->efficiencyDenominator->FillUniverse(universe, var->GetTrueValueX(*universe), var->GetTrueValueY(*universe), weight);
        }
      }
    }
  }
  std::cout << "Finished efficiency denominator loop.\n";
}

//==============================================================================
// Main
//==============================================================================
int main(const int /*argc*/, const char** /*argv*/)
{
  TH1::AddDirectory(false);

  // Make a chain of events
  const std::string mc_file_list(INSTALL_DIR "/etc/playlists/CCQENu_minervame1A_MC_Inextinguishable_merged.txt"); //"/etc/playlists/USBTestMC.txt");
  const std::string data_file_list(INSTALL_DIR "/etc/playlists/CCQENu_minervame1A_DATA_Inextinguishable_merged.txt"); //"/etc/playlists/USBTestData.txt");
  PlotUtils::ChainWrapper* chain = makeChainWrapperPtr(mc_file_list, "CCQENu"); //"MasterAnaDev");
  PlotUtils::ChainWrapper* truth = makeChainWrapperPtr(mc_file_list, "Truth");
  PlotUtils::ChainWrapper* data = makeChainWrapperPtr(data_file_list, "CCQENu"); //"MasterAnaDev");

  const std::string plist_string("minervame1a");
  const std::string reco_tree_name("CCQENu"); //"MasterAnaDev");
  const bool do_truth = false;
  const bool is_grid = false;
  // You're required to make some decisions
  PlotUtils::MinervaUniverse::SetNuEConstraint(true);
  PlotUtils::MinervaUniverse::SetPlaylist("minervame1A");
  PlotUtils::MinervaUniverse::SetAnalysisNuPDG(14);
  PlotUtils::MinervaUniverse::SetNonResPiReweight(true);
  PlotUtils::MinervaUniverse::SetDeuteriumGeniePiTune(false);

  // Make a map of systematic universes
  std::map< std::string, std::vector<CVUniverse*> > error_bands; // = GetStandardSystematics(chain);
  error_bands["cv"] = {new CVUniverse(chain)};
  std::map< std::string, std::vector<CVUniverse*> > truth_bands; //= GetStandardSystematics(truth);
  truth_bands["cv"] = {new CVUniverse(truth)};

  std::vector<double> dansPTBins = {0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, 0.7, 0.85, 1, 1.25, 1.5, 2.5, 4.5},
                      dansPzBins = {1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60};
  //TODO: pT, pz?
  std::vector<Variable*> vars = {
    new Variable("pTmu", "p_{T, #mu} [GeV/c]", dansPTBins, &CVUniverse::GetMuonPT, &CVUniverse::GetMuonPTTrue),
    new Variable("pzmu", "p_{||, #mu} [GeV/c]", dansPzBins, &CVUniverse::GetMuonPz, &CVUniverse::GetMuonPzTrue)
  };

  std::vector<Variable2D*> vars2D = {
    new Variable2D(*vars[1], *vars[0])
  };

  std::vector<Study*> studies;

  //Creating the single Data universe 
  PlotUtils::MacroUtil util(reco_tree_name, mc_file_list, data_file_list,
                    plist_string, do_truth, is_grid);
  CVUniverse* data_universe = new CVUniverse(util.m_data);
  std::vector<CVUniverse*> data_band = {data_universe};
  std::map<std::string, std::vector<CVUniverse*> > data_error_bands;
  data_error_bands["cv_data"] = data_band;
  
  std::vector<Study*> data_studies;

  for(auto& var: vars) var->InitializeMCHists(error_bands, truth_bands);
  for(auto& var: vars) var->InitializeDATAHists(data_band);

  for(auto& var: vars2D) var->InitializeMCHists(error_bands, truth_bands);
  for(auto& var: vars2D) var->InitializeDATAHists(data_band);

  PlotUtils::Cutter<CVUniverse, MichelEvent>::reco_t sidebands;
  auto precuts = reco::GetCCInclusive2DCuts<CVUniverse, MichelEvent>();
  auto signalDefinition = truth::GetCCInclusive2DSignal<CVUniverse>();
  auto phaseSpace = truth::GetCCInclusive2DPhaseSpace<CVUniverse>();
  phaseSpace.emplace_back(new MaxPzMu<CVUniverse>(60e3));

  PlotUtils::Cutter<CVUniverse, MichelEvent> mycuts(std::move(precuts), std::move(sidebands) , std::move(signalDefinition),std::move(phaseSpace));

  // Loop entries and fill
  CVUniverse::SetTruth(false);
  LoopAndFillEventSelection(chain, error_bands, vars, vars2D, studies, mycuts);
  CVUniverse::SetTruth(true);
  LoopAndFillEffDenom(truth, truth_bands, vars, vars2D, mycuts);
  std::cout << "MC cut summary:\n" << mycuts << "\n";
  mycuts.resetStats();

  CVUniverse::SetTruth(false);
  TFile* outDir = TFile::Open("OutputMichelHists.root", "RECREATE");
  LoopAndFillData(data, data_band,vars, vars2D, data_studies, mycuts);
  std::cout << "Data cut summary:\n" << mycuts << "\n";

  for(auto& var: vars)
  {
    // You must always sync your HistWrappers before plotting them
    var->SyncCVHistos();

    //Categorized makes sure GetTitle() is the same as the labels you were looping over before
    var->m_bestPionByGENIELabel->visit([](PlotUtils::HistWrapper<CVUniverse>& categ)
                                       {
                                         PlotCVAndError(categ.hist, categ.hist->GetTitle());
                                         PlotErrorSummary(categ.hist, categ.hist->GetTitle());
                                       });
  }

  for(auto& study: studies) study->SaveOrDraw(*outDir);
  for(auto& var: vars) var->Write(*outDir);
  for(auto& var: vars2D) var->Write(*outDir);
  TFile* dataDir = TFile::Open("DataStudyHists.root", "RECREATE");
  for(auto& study: data_studies) study->SaveOrDraw(*dataDir);  
  std::cout << "Success" << std::endl;
}
