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

#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 5) return 2;
    const std::string playlist(argv[1]), sample(argv[2]);
    const bool mc = sample == "MC";
    CVUniverse::SetNuEConstraint(true);
    CVUniverse::SetPlaylist("minervame"+playlist);
    CVUniverse::SetAnalysisNuPDG(14);
    CVUniverse::SetNFluxUniverses(100);
    CVUniverse::SetZExpansionFaReweight(false);
    CVUniverse::RPAMaterials(true);
    CVUniverse::SetTruth(false);
    using Weight = PlotUtils::Reweighter<CVUniverse, MichelEvent>;
    std::vector<std::unique_ptr<Weight>> weights;
    if (mc) {
        weights.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, MichelEvent>());
        weights.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, MichelEvent>(true,false));
        weights.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, MichelEvent>());
        weights.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, MichelEvent>());
        weights.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, MichelEvent>());
    }
    PlotUtils::Model<CVUniverse,MichelEvent> model(std::move(weights));
    reco::ZRange<CVUniverse,MichelEvent> zcut("Tracker",5980.,8422.);
    reco::Apothem<CVUniverse,MichelEvent> xycut(850.);
    reco::MaxMuonAngle<CVUniverse,MichelEvent> angle(20.);
    reco::HasMINOSMatch<CVUniverse,MichelEvent> match;
    reco::NoDeadtime<CVUniverse,MichelEvent> dead(1,"Deadtime");
    truth::ZRange<CVUniverse> true_z("Tracker",5980.,8422.);
    truth::Apothem<CVUniverse> true_xy(850.);
    std::ifstream manifest(argv[3]);
    if (!manifest) return 3;
    std::ofstream out(argv[4]);
    out << std::setprecision(15) << "pt,pz,qp,fracerr,curv,energy,pdg,current,fid,true_pt,true_pz,tune_weight\n";
    std::string path;
    int files=0;
    long long entries=0;
    while (manifest >> path) {
        PlotUtils::ChainWrapper chain("MasterAnaDev");
        if (chain.Add(path)<=0) return 4;
        const auto count=chain.GetEntries();
        CVUniverse cv(&chain);
        const std::string tool=cv.GetAnaToolName();
        for(int i=0;i<count;++i) {
            cv.SetEntry(i);
            if (cv.GetPmu()<20000.) continue;
            MichelEvent event;
            const double pz=cv.GetMuonPz(),pt=cv.GetMuonPT();
            if (!(pz>=20. && pt>=0. && pt<4.5 && std::isfinite(pz))) continue;
            if (!zcut.passesCut(cv,event) || !xycut.passesCut(cv,event) ||
                !angle.passesCut(cv,event) || !match.passesCut(cv,event) ||
                !dead.passesCut(cv,event)) continue;
            double weight=1., true_pt=0., true_pz=0.;
            int pdg=0,current=0,fid=0;
            if (mc) {
                model.SetEntry(cv,event);
                weight=model.GetWeight(cv,event);
                pdg=cv.GetInt("mc_incoming");
                current=cv.GetInt("mc_current");
                fid=true_z.passes(cv) && true_xy.passes(cv);
                true_pt=cv.GetMuonPTTrue();
                true_pz=cv.GetMuonPzTrue();
            }
            out<<pt<<','<<pz<<','<<cv.GetMuonQP()<<','
               <<cv.GetDouble((tool+"_minos_trk_eqp_qp").c_str())<<','
               <<cv.GetInt((tool+"_minos_used_curvature").c_str())<<','
               <<cv.NewEavail()/1000.<<','<<pdg<<','<<current<<','<<fid<<','
               <<true_pt<<','<<true_pz<<','<<weight<<'\n';
        }
        ++files;
        entries+=count;
        if (files%10==0) std::cerr<<"processed "<<files<<" files, "<<entries<<" entries\n";
    }
    std::cerr<<"complete "<<files<<" files, "<<entries<<" entries\n";
    out.close();
    return files && out.good() ? 0 : 5;
}
