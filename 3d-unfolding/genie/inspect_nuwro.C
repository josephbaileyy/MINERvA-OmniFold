// Inspect a NuWro output file: event API, weights, flux spectrum.
#include "event1.h"
void inspect_nuwro(const char* fn) {
  gSystem->Load(Form("%s/bin/event1.so", gSystem->Getenv("NUWRO_FQ_DIR")));
  TFile f(fn);
  TTree* t = (TTree*)f.Get("treeout");
  event* e = new event();
  t->SetBranchAddress("e", &e);
  Long64_t N = t->GetEntries();
  for (int i = 0; i < 5; i++) {
    t->GetEntry(i);
    particle nu = e->nu();
    int ilep = -1;
    for (unsigned k = 0; k < e->post.size(); k++) {
      int p = e->post[k].pdg;
      if (p == 13 || p == -13) { ilep = k; break; }
    }
    printf("ev%d cc=%d qel%d res%d dis%d mec%d coh%d Enu=%.3f w=%.4e npost=%lu",
           i, e->flag.cc, e->flag.qel, e->flag.res, e->flag.dis, e->flag.mec,
           e->flag.coh, nu.t / 1000., e->weight, e->post.size());
    if (ilep >= 0) {
      particle l = e->post[ilep];
      printf(" | mu pdg=%d E=%.3f pz=%.3f pt=%.3f", l.pdg, l.t / 1000.,
             l.z / 1000., sqrt(l.x * l.x + l.y * l.y) / 1000.);
    }
    printf("\n");
  }
  double wsum = 0, emin = 1e9, emax = 0;
  int ncc = 0;
  for (Long64_t i = 0; i < N; i++) {
    t->GetEntry(i);
    wsum += e->weight;
    if (e->flag.cc) ncc++;
    double en = e->nu().t / 1000.;
    if (en < emin) emin = en;
    if (en > emax) emax = en;
  }
  printf("N=%lld ncc=%d mean_weight=%.4e cm2 Enu_range=[%.2f,%.2f] GeV\n",
         N, ncc, wsum / N, emin, emax);
  TH1D* xs = (TH1D*)f.Get("xsections");
  if (xs) printf("xsections: nbins=%d integral=%.4e max=%.4e\n",
                 xs->GetNbinsX(), xs->Integral(), xs->GetMaximum());
}
