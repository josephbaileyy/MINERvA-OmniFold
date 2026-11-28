// OOFVC dump (OOFVC-DECLARATION.md section 1.2, route A). One MC playlist: every reco-tree entry that the 2D event loop
// selects, with the truth the event loop reads, so the lane can (a) join it to the production omnifile's
// mc_background rows (C-JOIN) and mc_signal_reco rows (C-SIGW) on exact values, and (b) give the moved rows their true
// muon kinematics, which mc_background does not store.
//
// It mirrors MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp (57792e42):
//   - the setup of main(), :1695-1750: MinervaUniverse settings, the Cutter (preCuts, empty sidebands, signal
//     definition, phase space incl. MaxPzMu/MaxPtMu), and MnvTune v1 as the Model;
//   - the per-entry order of the signal loop, :1123-1180: SetTruth(false), SetEntry, model.SetEntry, then truth mode
//     (w_truth, isSignal, isEfficiencyDenom, true pT/p||), then reco mode (w_reco, isMCSelected, reco pT/p||).
//     One departure, for time: isMCSelected is evaluated first, in reco mode with weight 1 (the weight enters only
//     the Cutter's cut-table statistics), and the weights are computed only for selected entries. C-JOIN and C-SIGW
//     compare every weight bit for bit with the production trees, so a difference this makes is a STOP, not a result;
//   - the background loop's routing, :1440-1472: a selected entry goes to mc_background unless isSignal &&
//     isEfficiencyDenom (evaluated there in reco mode with the reco weight); no deduplication;
//   - the signal loop's key deduplication of phase-space entries, :1201-1218: the first occurrence of a key among
//     ALL phase-space entries, selected or not, is kept (truth-mode cuts with weight 1, before the selection). The
//     signal loop's truth-tree gate (truthAgrees) is not re-evaluated: Stage B's P4 census measured nG1 = 0 and
//     nSigLoopNoTruth = 0 on this omnifile's per-playlist inputs (2d-closeout/stageB/diagnostics/REPORT.md:45-62), so
//     the gate drops nothing there; were it to, C-SIGW would STOP.
// Both routings are evaluated (reco mode as the background loop, truth mode as the signal loop) and written, so the
// lane checks that they agree. Writes only the output file. Usage: oofvc_dump PLAYLIST MANIFEST OUT.root
#include "event/CVUniverse.h"
#include "event/MichelEvent.h"
#include "cuts/MaxPzMu.h"
#include "cuts/MaxPtMu.h"
#include "PlotUtils/ChainWrapper.h"
#include "PlotUtils/Cutter.h"
#include "PlotUtils/CCInclusiveCuts.h"
#include "PlotUtils/CCInclusiveSignal.h"
#include "PlotUtils/Model.h"
#include "PlotUtils/FluxAndCVReweighter.h"
#include "PlotUtils/GENIEReweighter.h"
#include "PlotUtils/LowRecoil2p2hReweighter.h"
#include "PlotUtils/MINOSEfficiencyReweighter.h"
#include "PlotUtils/RPAReweighter.h"
#include "Math/Vector4D.h"
#include "TFile.h"
#include "TTree.h"
#include "TParameter.h"

#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_set>
#include <vector>

static uint64_t makeEventKey(int run, int subrun, int nth)  // runEventLoopOmniFold.cpp:154-159
{
  return (static_cast<uint64_t>(run) * 100000000ULL + static_cast<uint64_t>(subrun)) * 100000000ULL +
         static_cast<uint64_t>(nth);
}

int main(int argc, char** argv)
{
  if (argc != 4) { std::cerr << "usage: oofvc_dump PLAYLIST MANIFEST OUT.root\n"; return 2; }
  const std::string playlist(argv[1]), manifest(argv[2]), outPath(argv[3]);

  std::vector<std::string> files;
  {
    std::ifstream in(manifest);
    if (!in) { std::cerr << "cannot read " << manifest << "\n"; return 3; }
    for (std::string p; in >> p;) files.push_back(p);
  }
  if (files.empty()) { std::cerr << "empty manifest\n"; return 3; }

  PlotUtils::MinervaUniverse::SetNuEConstraint(true);
  PlotUtils::MinervaUniverse::SetPlaylist("minervame" + playlist);
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
  phaseSpace.emplace_back(new MaxPzMu<CVUniverse>(60000.));
  phaseSpace.emplace_back(new MaxPtMu<CVUniverse>(4500.));
  PlotUtils::Cutter<CVUniverse, MichelEvent> cuts(std::move(preCuts), std::move(sidebands),
                                                   std::move(signalDefinition), std::move(phaseSpace));

  std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse, MichelEvent>>> tune;
  tune.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, MichelEvent>());
  tune.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, MichelEvent>(true, false));
  tune.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, MichelEvent>());
  tune.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, MichelEvent>());
  tune.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, MichelEvent>());
  PlotUtils::Model<CVUniverse, MichelEvent> model(std::move(tune));
  truth::ZRange<CVUniverse> fidZ("Tracker", minZ, maxZ);  // the phase space's vertex cuts, read alone (descriptive)
  truth::Apothem<CVUniverse> fidXY(apothem);

  // One chain over the playlist, as the event loop's MacroUtil builds it (one CV universe, one dedupe set).
  PlotUtils::ChainWrapper* chain = new PlotUtils::ChainWrapper("MasterAnaDev");
  for (const auto& f : files)
    if (chain->Add(f) <= 0) { std::cerr << "cannot add " << f << "\n"; return 4; }
  CVUniverse* cv = new CVUniverse(chain);

  TFile out(outPath.c_str(), "RECREATE");
  if (out.IsZombie()) return 5;
  TTree t("rows", "OOFVC: selected MC entries with truth");
  UChar_t to_bkg = 0, to_sig = 0, dup_sig = 0, fid = 0;
  int run = 0, subrun = 0, nth = 0, nu_pdg = 0, current = 0;
  long long entry = 0;
  double reco_pt = 0, reco_pz = 0, w_reco = 0, true_pt = 0, true_pz = 0, w_truth = 0, theta_true = 0;
  double vtx_x = 0, vtx_y = 0, vtx_z = 0;
  t.Branch("entry", &entry);            // the chain entry (per playlist)
  t.Branch("to_bkg", &to_bkg);          // reco-mode routing: !(isSignal && isEfficiencyDenom), as :1453-1456
  t.Branch("to_sig", &to_sig);          // truth-mode routing: isSignal && isEfficiencyDenom, as :1134-1135
  t.Branch("dup_sig", &dup_sig);        // to_sig and its key already seen (the signal loop skips it)
  t.Branch("mc_run", &run);
  t.Branch("mc_subrun", &subrun);
  t.Branch("mc_nthEvtInFile", &nth);
  t.Branch("reco_pt", &reco_pt);        // GetMuonPT (GeV/c), reco mode: sim / sim_background
  t.Branch("reco_pz", &reco_pz);        // GetMuonPz (GeV/c), reco mode: sim_pz / sim_background_pz
  t.Branch("w_reco", &w_reco);          // model weight, reco mode: w_reco / w_bkg
  t.Branch("true_pt", &true_pt);        // GetMuonPTTrue (GeV/c), truth mode: MC
  t.Branch("true_pz", &true_pz);        // GetMuonPzTrue (GeV/c), truth mode: MC_pz
  t.Branch("w_truth", &w_truth);        // model weight, truth mode: w_truth
  t.Branch("theta_true", &theta_true);  // GetThetalepTrue (rad)
  t.Branch("nu_pdg", &nu_pdg);          // GetTruthNuPDG: bkg_nuPDG
  t.Branch("current", &current);        // GetCurrent: bkg_current
  t.Branch("fid", &fid);                // truth ZRange && Apothem, the phase space's vertex cuts
  t.Branch("vtx_x", &vtx_x);            // GetTrueVertex (mm): bkg_vtx_*
  t.Branch("vtx_y", &vtx_y);
  t.Branch("vtx_z", &vtx_z);

  std::unordered_set<uint64_t> seenSigKeys;
  long long nEntries = chain->GetEntries(), nSel = 0, nBkg = 0, nSig = 0, nDup = 0, nDisagree = 0;
  for (long long i = 0; i < nEntries; ++i)
  {
    CVUniverse::SetTruth(false);
    MichelEvent evt;
    cv->SetEntry(i);
    // the signal loop's dedupe, over every phase-space entry in entry order, before the selection (see the header)
    CVUniverse::SetTruth(true);
    const bool sigT = cuts.isSignal(*cv, 1.0);
    const bool psT = cuts.isEfficiencyDenom(*cv, 1.0);
    bool dup = false;
    if (sigT && psT)
      dup = !seenSigKeys.insert(makeEventKey(cv->GetInt("mc_run"), cv->GetInt("mc_subrun"),
                                             cv->GetInt("mc_nthEvtInFile"))).second;
    CVUniverse::SetTruth(false);
    {
      MichelEvent sel_evt;
      if (!cuts.isMCSelected(*cv, sel_evt, 1.0).all()) continue;  // selection before the weights (see the header)
    }
    model.SetEntry(*cv, evt);

    CVUniverse::SetTruth(true);
    const double wt = model.GetWeight(*cv, evt);
    const double tpt = cv->GetMuonPTTrue(), tpz = cv->GetMuonPzTrue(), tth = cv->GetThetalepTrue();

    CVUniverse::SetTruth(false);
    const double wr = model.GetWeight(*cv, evt);

    const bool sigR = cuts.isSignal(*cv, wr);
    const bool psR = cuts.isEfficiencyDenom(*cv, wr);
    entry = i;
    to_bkg = !(sigR && psR);
    to_sig = sigT && psT;
    dup_sig = dup;
    run = cv->GetInt("mc_run"); subrun = cv->GetInt("mc_subrun"); nth = cv->GetInt("mc_nthEvtInFile");
    reco_pt = cv->GetMuonPT(); reco_pz = cv->GetMuonPz(); w_reco = wr;
    true_pt = tpt; true_pz = tpz; w_truth = wt; theta_true = tth;
    nu_pdg = cv->GetTruthNuPDG(); current = cv->GetCurrent();
    const ROOT::Math::XYZTVector v = cv->GetTrueVertex();
    vtx_x = v.X(); vtx_y = v.Y(); vtx_z = v.Z();
    fid = fidZ.passes(*cv) && fidXY.passes(*cv);
    t.Fill();
    ++nSel; nBkg += to_bkg; nSig += to_sig; nDup += (to_sig && dup);
    nDisagree += (to_bkg == to_sig);
  }
  // write through the output file itself: a reweighter can leave gDirectory on an auxiliary file (the event loop
  // restores its output directory for the same reason, runEventLoopOmniFold.cpp:1997-2001)
  out.cd();
  if (t.GetDirectory() != &out) { std::cerr << "the rows tree is not in the output file\n"; return 6; }
  if (out.WriteTObject(&t, "rows") <= 0) { std::cerr << "writing rows failed\n"; return 6; }
  TParameter<long long> nPar("n_entries", nEntries);
  if (out.WriteTObject(&nPar, "n_entries") <= 0) { std::cerr << "writing n_entries failed\n"; return 6; }
  out.Close();
  {
    TFile check(outPath.c_str(), "READ");
    TTree* back = check.IsZombie() ? nullptr : dynamic_cast<TTree*>(check.Get("rows"));
    if (!back || back->GetEntries() != nSel) { std::cerr << "the written rows do not read back\n"; return 7; }
  }
  std::cout << "oofvc_dump " << playlist << " entries " << nEntries << " selected " << nSel << " to_bkg " << nBkg
            << " to_sig " << nSig << " dup_sig " << nDup << " routing_disagree " << nDisagree << "\n";
  return 0;
}
