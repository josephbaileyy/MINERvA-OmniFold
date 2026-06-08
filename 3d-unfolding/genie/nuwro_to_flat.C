// Convert a NuWro 'treeout' (event-class) file to a flat tree of observables
// readable by the conda analysis ROOT (avoids needing event1.so / ROOT 6.22
// outside the NuWro env). Run in the NuWro UPS env:
//   root -l -b -q 'nuwro_to_flat.C("in.root","out_flat.root")'
//
// Output tree 'nuwro_obs' (per event): cc/I, pt/D, pz/D, eavail/D, W/D (GeV),
// weight/D (cm^2, = flux-averaged total CC xsec per nucleon, constant).
// Also a TParameter<double> nTotal (events processed). Truth Eavail replicates
// CVUniverse::GetEAvailableTrue(): gamma +E; pi+- +E-0.135; pi0 +E; p +E-0.93827.
// W replicates CVUniverse::GetTrueExperimentersW():
//   Q2 = 4 Enu Emu sin^2(theta_mu/2);  W = sqrt(M^2 + 2(Enu-Emu)M - Q2), M=M_n.
#include "event1.h"
void nuwro_to_flat(const char* fin, const char* fout) {
  gSystem->Load(Form("%s/bin/event1.so", gSystem->Getenv("NUWRO_FQ_DIR")));
  TFile in(fin);
  TTree* t = (TTree*)in.Get("treeout");
  event* e = new event();
  t->SetBranchAddress("e", &e);

  TFile out(fout, "RECREATE");
  TTree* o = new TTree("nuwro_obs", "NuWro observables");
  int cc; double pt, pz, eavail, weight, W;
  o->Branch("cc", &cc, "cc/I");
  o->Branch("pt", &pt, "pt/D");
  o->Branch("pz", &pz, "pz/D");
  o->Branch("eavail", &eavail, "eavail/D");
  o->Branch("W", &W, "W/D");
  o->Branch("weight", &weight, "weight/D");

  Long64_t N = t->GetEntries();
  const double MPI = 0.135, MP = 0.93827, MN = 0.939565;  // GeV (match CVUniverse)
  for (Long64_t i = 0; i < N; i++) {
    t->GetEntry(i);
    cc = e->flag.cc ? 1 : 0;
    weight = e->weight;            // cm^2, per nucleon (constant)
    // incoming neutrino energy (along +z); MeV -> GeV
    double Enu = (e->in.size() > 0) ? e->in[0].t / 1000.0 : -9999;
    // muon (pdg 13) from post-FSI list; neutrino is +z
    pt = pz = -9999; W = -9999;
    double Emu = -9999, pmu = -9999;
    eavail = 0;
    for (unsigned k = 0; k < e->post.size(); k++) {
      particle& p = e->post[k];
      int pdg = p.pdg;
      double E = p.t / 1000.0;     // MeV -> GeV
      if (pdg == 13 || pdg == -13) {
        pz = p.z / 1000.0;
        pt = sqrt(p.x * p.x + p.y * p.y) / 1000.0;
        Emu = E;
        pmu = sqrt(p.x * p.x + p.y * p.y + p.z * p.z) / 1000.0;
      } else if (pdg == 22) {            eavail += E;
      } else if (pdg == 211 || pdg == -211) { eavail += E - MPI;
      } else if (pdg == 111) {           eavail += E;
      } else if (pdg == 2212) {          eavail += E - MP;
      }
    }
    if (Enu > 0 && Emu > 0 && pmu > 0) {
      double costh = pz / pmu;                       // muon angle wrt +z beam
      if (costh > 1) costh = 1; else if (costh < -1) costh = -1;
      double th = acos(costh);
      double Q2 = 4.0 * Enu * Emu * pow(sin(th / 2.0), 2);
      double w2 = MN * MN + 2.0 * (Enu - Emu) * MN - Q2;
      W = (w2 > 0) ? sqrt(w2) : 0.0;
    }
    o->Fill();
  }
  o->Write();
  TParameter<double>("nTotal", (double)N).Write();
  out.Close();
  printf("nuwro_to_flat: wrote %s with %lld events\n", fout, N);
}
