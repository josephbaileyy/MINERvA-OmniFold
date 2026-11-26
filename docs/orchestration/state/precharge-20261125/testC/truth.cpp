// Test C generated denominators: the weighted Truth-tree count of the published
// signal (fiducial nu_mu CC, muon angle < 20 deg, true p_parallel > 1.5 GeV/c), binned
// in the published true (p_T, p_parallel) cell and in true neutrino energy. Same
// MAT configuration and weights as ../measure.cpp, in truth mode.
//
// usage: truth <playlist> <MC manifest> <axes.txt> <out.csv>
// Output rows (nonzero only): cell, ebin, n, sumw, sumw2, ndup, sumwdup.
//   cell = ipt*16 + ipz for the 224 published cells (../score.py), 224 for an event in
//   the signal phase space outside the grid (true p_parallel >= 60 or p_T >= 4.5).
//   ebin = floor(E_nu / 0.5 GeV), 0..399; 400 holds E_nu >= 200 GeV.
//   ndup/sumwdup count entries whose (mc_run, mc_subrun, mc_nthEvtInFile) already
//   appeared in the same file; n/sumw include them, so deduplicated = sumw - sumwdup.
#include "event/CVUniverse.h"
#include "event/MichelEvent.h"
#include "PlotUtils/CCInclusiveCuts.h"
#include "PlotUtils/CCInclusiveSignal.h"
#include "PlotUtils/Model.h"
#include "PlotUtils/FluxAndCVReweighter.h"
#include "PlotUtils/GENIEReweighter.h"
#include "PlotUtils/LowRecoil2p2hReweighter.h"
#include "PlotUtils/MINOSEfficiencyReweighter.h"
#include "PlotUtils/RPAReweighter.h"

#include "TFile.h"
#include "TTree.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

namespace {
constexpr int kCells = 225, kEbins = 401;
constexpr double kEbinWidth = 0.5;  // GeV

std::vector<double> read_edges(std::istream& in) {
    std::string line;
    std::getline(in, line);
    std::istringstream s(line);
    std::vector<double> edges;
    for (double v; s >> v;) edges.push_back(v);
    return edges;
}

// Index of the half-open bin [edges[i], edges[i+1]) holding v, or -1.
int find_bin(const std::vector<double>& edges, double v) {
    if (!(v >= edges.front() && v < edges.back())) return -1;
    return int(std::upper_bound(edges.begin(), edges.end(), v) - edges.begin()) - 1;
}
}  // namespace

int main(int argc, char** argv) {
    if (argc != 5) return 2;
    const std::string playlist(argv[1]);
    CVUniverse::SetNuEConstraint(true);
    CVUniverse::SetPlaylist("minervame"+playlist);
    CVUniverse::SetAnalysisNuPDG(14);
    CVUniverse::SetNFluxUniverses(100);
    CVUniverse::SetZExpansionFaReweight(false);
    CVUniverse::RPAMaterials(true);
    CVUniverse::SetTruth(true);
    using Weight = PlotUtils::Reweighter<CVUniverse, MichelEvent>;
    std::vector<std::unique_ptr<Weight>> weights;
    weights.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, MichelEvent>());
    weights.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, MichelEvent>(true,false));
    weights.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, MichelEvent>());
    weights.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, MichelEvent>());
    weights.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, MichelEvent>());
    PlotUtils::Model<CVUniverse,MichelEvent> model(std::move(weights));
    truth::IsNeutrino<CVUniverse> neutrino;
    truth::IsCC<CVUniverse> cc;
    truth::ZRange<CVUniverse> true_z("Tracker",5980.,8422.);
    truth::Apothem<CVUniverse> true_xy(850.);
    truth::MuonAngle<CVUniverse> angle(20.);
    truth::PZMuMin<CVUniverse> pzmin(1500.);

    std::ifstream axes(argv[3]);
    if (!axes) return 3;
    const std::vector<double> pz_edges = read_edges(axes), pt_edges = read_edges(axes);
    if (pz_edges.size() != 17 || pt_edges.size() != 15) return 3;
    std::ifstream manifest(argv[2]);
    if (!manifest) return 3;

    std::vector<std::array<double, kEbins>> n(kCells), w(kCells), w2(kCells), nd(kCells), wd(kCells);
    for (int c = 0; c < kCells; ++c) {
        n[c].fill(0.); w[c].fill(0.); w2[c].fill(0.); nd[c].fill(0.); wd[c].fill(0.);
    }
    std::string path;
    int files = 0;
    long long entries = 0, passed = 0, duplicates = 0, below_muon = 0;
    while (manifest >> path) {
        {   // refuse a file whose Truth tree lacks a branch this pass reads
            std::unique_ptr<TFile> f(TFile::Open(path.c_str()));
            TTree* t = f ? dynamic_cast<TTree*>(f->Get("Truth")) : nullptr;
            for (const char* b : {"mc_incomingE", "mc_run", "mc_subrun", "mc_nthEvtInFile"}) {
                if (!t || !t->GetBranch(b)) {
                    std::cerr << "no Truth/" << b << " in " << path << "\n";
                    return 6;
                }
            }
        }
        PlotUtils::ChainWrapper chain("Truth");
        if (chain.Add(path)<=0) return 4;
        const auto count = chain.GetEntries();
        CVUniverse cv(&chain);
        std::unordered_set<std::uint64_t> seen;
        for (int i = 0; i < count; ++i) {
            cv.SetEntry(i);
            if (!neutrino.passes(cv) || !cc.passes(cv) || !true_z.passes(cv) ||
                !true_xy.passes(cv) || !angle.passes(cv) || !pzmin.passes(cv)) continue;
            MichelEvent event;
            model.SetEntry(cv, event);
            const double weight = model.GetWeight(cv, event);
            const double pt = cv.GetMuonPTTrue(), pz = cv.GetMuonPzTrue();
            const double enu = cv.GetDouble("mc_incomingE")/1000.;  // MeV -> GeV
            const double emu = cv.GetElepTrue()/1000.;
            if (!(std::isfinite(enu) && enu >= 0.)) return 7;
            if (enu < emu) ++below_muon;
            const int ipt = find_bin(pt_edges, pt), ipz = find_bin(pz_edges, pz);
            const int cell = (ipt >= 0 && ipz >= 0) ? ipt*16 + ipz : 224;
            const int ebin = std::min(int(enu/kEbinWidth), kEbins-1);
            const std::uint64_t key = (std::uint64_t(cv.GetInt("mc_run")) << 40) ^
                                      (std::uint64_t(cv.GetInt("mc_subrun")) << 20) ^
                                      std::uint64_t(cv.GetInt("mc_nthEvtInFile"));
            const bool dup = !seen.insert(key).second;
            n[cell][ebin] += 1.; w[cell][ebin] += weight; w2[cell][ebin] += weight*weight;
            if (dup) { nd[cell][ebin] += 1.; wd[cell][ebin] += weight; ++duplicates; }
            ++passed;
        }
        ++files;
        entries += count;
        if (files%10==0) std::cerr<<"processed "<<files<<" files, "<<entries<<" entries\n";
    }
    std::ofstream out(argv[4]);
    out << std::setprecision(15) << "cell,ebin,n,sumw,sumw2,ndup,sumwdup\n";
    for (int c = 0; c < kCells; ++c)
        for (int e = 0; e < kEbins; ++e)
            if (n[c][e] > 0)
                out << c << ',' << e << ',' << n[c][e] << ',' << w[c][e] << ',' << w2[c][e]
                    << ',' << nd[c][e] << ',' << wd[c][e] << '\n';
    std::cerr<<"complete "<<files<<" files, "<<entries<<" entries, "<<passed<<" signal, "
             <<duplicates<<" duplicate keys, "<<below_muon<<" with E_nu < E_mu\n";
    out.close();
    return files && out.good() ? 0 : 5;
}
