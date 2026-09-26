// nuwro_to_flat_5d.C -- nuwro_to_flat.C plus the true kinematics the 5D
// (pT, p||, E_avail, q3, W) generator prediction needs. Run in the NuWro UPS env
// (source setup_nuwro.sh):
//   root -l -b -q 'nuwro_to_flat_5d.C("nuwro_p1.root","nuwro_flat5d_p1.root")'
//
// Every branch nuwro_to_flat.C writes (cc, pt, pz, eavail, W, weight) and the
// TParameter nTotal are computed by the SAME statements in the SAME order, so
// they are bitwise identical to the nuwro_flat.root that nuwro_to_xsec3d.py and
// nuwro_to_xsec_eavailW.py consume (gen_to_xsec5d.py checks this). Added:
//   Enu/D  incoming neutrino energy, in[0].t (GeV)
//   Q2/D   true four-momentum transfer Q^2 = -(k - k')^2 from the lab-frame
//          neutrino in[0] and the final muon (GeV^2); this is what the MINERvA
//          tuple branch mc_Q2 holds (PlotUtils GetQ2True)
//   q0/D   Enu - Emu (GeV); PlotUtils calcq0
//   q3/D   sqrt(Q2 + q0^2) (GeV); PlotUtils calcq3 / Getq3True
//   dyn/I  NuWro channel code; hitnuc/I  in[1].pdg (struck nucleon, 0 if absent)
// Q2/q0/q3 are -9999 under exactly the condition that sets W = -9999.
#include "event1.h"
void nuwro_to_flat_5d(const char* fin, const char* fout) {
  gSystem->Load(Form("%s/bin/event1.so", gSystem->Getenv("NUWRO_FQ_DIR")));
  TFile in(fin);
  TTree* t = (TTree*)in.Get("treeout");
  event* e = new event();
  t->SetBranchAddress("e", &e);

  TFile out(fout, "RECREATE");
  TTree* o = new TTree("nuwro_obs", "NuWro observables (5D)");
  int cc; double pt, pz, eavail, weight, W;
  double Enu_o, Q2_o, q0_o, q3_o; int dyn_o, hitnuc_o;
  o->Branch("cc", &cc, "cc/I");
  o->Branch("pt", &pt, "pt/D");
  o->Branch("pz", &pz, "pz/D");
  o->Branch("eavail", &eavail, "eavail/D");
  o->Branch("W", &W, "W/D");
  o->Branch("weight", &weight, "weight/D");
  o->Branch("Enu", &Enu_o, "Enu/D");
  o->Branch("Q2", &Q2_o, "Q2/D");
  o->Branch("q0", &q0_o, "q0/D");
  o->Branch("q3", &q3_o, "q3/D");
  o->Branch("dyn", &dyn_o, "dyn/I");
  o->Branch("hitnuc", &hitnuc_o, "hitnuc/I");

  Long64_t N = t->GetEntries();
  const double MPI = 0.135, MP = 0.93827, MN = 0.939565;  // GeV (match CVUniverse)
  for (Long64_t i = 0; i < N; i++) {
    t->GetEntry(i);
    cc = e->flag.cc ? 1 : 0;
    weight = e->weight;            // cm^2, per nucleon (constant)
    double Enu = (e->in.size() > 0) ? e->in[0].t / 1000.0 : -9999;
    pt = pz = -9999; W = -9999;
    double Emu = -9999, pmu = -9999;
    double mx = 0, my = 0, mz = 0;   // muon 3-momentum (GeV), last muon wins as pt/pz do
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
        mx = p.x / 1000.0; my = p.y / 1000.0; mz = p.z / 1000.0;
      } else if (pdg == 22) {            eavail += E;
      } else if (pdg == 211 || pdg == -211) { eavail += E - MPI;
      } else if (pdg == 111) {           eavail += E;
      } else if (pdg == 2212) {          eavail += E - MP;
      }
    }
    Enu_o = Enu;
    Q2_o = q0_o = q3_o = -9999;
    if (Enu > 0 && Emu > 0 && pmu > 0) {
      double costh = pz / pmu;                       // muon angle wrt +z beam
      if (costh > 1) costh = 1; else if (costh < -1) costh = -1;
      double th = acos(costh);
      double Q2 = 4.0 * Enu * Emu * pow(sin(th / 2.0), 2);
      double w2 = MN * MN + 2.0 * (Enu - Emu) * MN - Q2;
      W = (w2 > 0) ? sqrt(w2) : 0.0;
      // true Q^2 = -(k-k')^2 with k = in[0] (full 3-vector, not assumed +z)
      double kx = e->in[0].x / 1000.0, ky = e->in[0].y / 1000.0, kz = e->in[0].z / 1000.0;
      double dx = kx - mx, dy = ky - my, dz = kz - mz;
      q0_o = Enu - Emu;
      Q2_o = (dx * dx + dy * dy + dz * dz) - q0_o * q0_o;
      q3_o = sqrt(Q2_o + q0_o * q0_o);
    }
    dyn_o = e->dyn;
    hitnuc_o = (e->in.size() > 1) ? e->in[1].pdg : 0;
    o->Fill();
  }
  o->Write();
  TParameter<double>("nTotal", (double)N).Write();
  out.Close();
  printf("nuwro_to_flat_5d: wrote %s with %lld events\n", fout, N);
}
