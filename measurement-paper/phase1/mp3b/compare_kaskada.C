// compare_kaskada.C -- MP3-B kaskada_on check (director's ruling 2): the same NuWro card and seed with
// kaskada_on = 1 (file f1) and kaskada_on = 0 (file f0), compared event by event. Run in the NuWro UPS env:
//   root -l -b -q 'compare_kaskada.C("k1/nuwro.root","k0/nuwro.root","out.txt")'
// RNG alignment first: event i of the two files is the same draw only if NuWro consumed the same random numbers
// before it. The test: the same number of events, and for EVERY event the initial state (e->in) and the
// primary-vertex products (e->out, before any cascade) identical bitwise. If that fails, the files are
// MISALIGNED and the final-state comparison below is not meaningful (RNG_ALIGNED 0; the reader must say so).
// Final state (e->post), particles sorted by (pdg, E, pz) in both files: identical content (the same pdg
// sequence) and four-momenta equal exactly / within TOL; otherwise per-pdg statistics of what differs:
// PDG_SHIFT pdg n_particles mean(E_k1 - E_k0) max|dE| max|dp_component| (MeV).
#include "event1.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <map>
#include <vector>

static const double TOL = 1e-6;  // MeV: "to rounding"

static std::vector<particle> sorted_copy(const std::vector<particle>& v) {
  std::vector<particle> s(v.begin(), v.end());
  std::sort(s.begin(), s.end(), [](const particle& a, const particle& b) {
    if (a.pdg != b.pdg) return a.pdg < b.pdg;
    if (a.t != b.t) return a.t < b.t;
    return a.z < b.z;
  });
  return s;
}

static bool identical(const std::vector<particle>& a, const std::vector<particle>& b) {
  if (a.size() != b.size()) return false;
  for (size_t k = 0; k < a.size(); k++)
    if (a[k].pdg != b[k].pdg || a[k].t != b[k].t || a[k].x != b[k].x || a[k].y != b[k].y || a[k].z != b[k].z)
      return false;
  return true;
}

void compare_kaskada(const char* f1, const char* f0, const char* out) {
  gSystem->Load(Form("%s/bin/event1.so", gSystem->Getenv("NUWRO_FQ_DIR")));
  TFile A(f1), B(f0);
  TTree* ta = (TTree*)A.Get("treeout");
  TTree* tb = (TTree*)B.Get("treeout");
  event* ea = new event();
  event* eb = new event();
  ta->SetBranchAddress("e", &ea);
  tb->SetBranchAddress("e", &eb);
  Long64_t na = ta->GetEntries(), nb = tb->GetEntries(), n = std::min(na, nb);
  Long64_t n_in = 0, n_out = 0, n_dyn = 0, first_mis = -1;
  Long64_t n_exact = 0, n_tol = 0, n_mom = 0, n_content = 0;
  double max_d = 0, w1 = 0, w0 = 0;
  std::map<int, long> shift_n, fewer, more;
  std::map<int, double> shift_sum, shift_max, shift_maxp;
  std::vector<Long64_t> examples;
  for (Long64_t i = 0; i < n; i++) {
    ta->GetEntry(i);
    tb->GetEntry(i);
    if (i == 0) { w1 = ea->weight; w0 = eb->weight; }
    bool in_ok = identical(ea->in, eb->in), out_ok = identical(ea->out, eb->out);
    n_in += in_ok;
    n_out += out_ok;
    if (ea->dyn != eb->dyn) n_dyn++;
    if ((!in_ok || !out_ok) && first_mis < 0) first_mis = i;
    std::vector<particle> pa = sorted_copy(ea->post), pb = sorted_copy(eb->post);
    bool same_content = pa.size() == pb.size();
    for (size_t k = 0; same_content && k < pa.size(); k++) same_content = pa[k].pdg == pb[k].pdg;
    if (!same_content) {
      n_content++;
      std::map<int, int> ca, cb;
      for (auto& p : pa) ca[p.pdg]++;
      for (auto& p : pb) cb[p.pdg]++;
      for (auto& kv : cb) if (ca[kv.first] < kv.second) fewer[kv.first]++;
      for (auto& kv : ca) if (cb[kv.first] < kv.second) more[kv.first]++;
      if (examples.size() < 8) examples.push_back(i);
      continue;
    }
    double d_ev = 0;
    for (size_t k = 0; k < pa.size(); k++) {
      double d = std::max({fabs(pa[k].t - pb[k].t), fabs(pa[k].x - pb[k].x), fabs(pa[k].y - pb[k].y), fabs(pa[k].z - pb[k].z)});
      d_ev = std::max(d_ev, d);
      if (d > TOL) {
        int g = pa[k].pdg;
        shift_n[g]++;
        shift_sum[g] += pa[k].t - pb[k].t;
        shift_max[g] = std::max(shift_max[g], fabs(pa[k].t - pb[k].t));
        shift_maxp[g] = std::max(shift_maxp[g], std::max({fabs(pa[k].x - pb[k].x), fabs(pa[k].y - pb[k].y), fabs(pa[k].z - pb[k].z)}));
      }
    }
    max_d = std::max(max_d, d_ev);
    if (d_ev == 0) n_exact++;
    if (d_ev <= TOL) n_tol++; else { n_mom++; if (examples.size() < 8) examples.push_back(i); }
  }
  ofstream o(out);
  o.precision(10);
  o << "FILE_K1 " << f1 << "\nFILE_K0 " << f0 << "\nN_K1 " << na << "\nN_K0 " << nb << "\nN_COMPARED " << n << "\n";
  o << "WEIGHT_K1 " << w1 << "\nWEIGHT_K0 " << w0 << "\n";
  o << "N_IN_IDENTICAL " << n_in << "\nN_OUT_IDENTICAL " << n_out << "\nN_DYN_DIFFERENT " << n_dyn << "\n";
  o << "FIRST_MISALIGNED " << first_mis << "\n";
  o << "RNG_ALIGNED " << ((na == nb && n_in == n && n_out == n) ? 1 : 0) << "\n";
  o << "N_POST_EXACT " << n_exact << "\nN_POST_WITHIN_TOL " << n_tol << "\nN_POST_MOMENTUM_DIFFERENT " << n_mom
    << "\nN_POST_CONTENT_DIFFERENT " << n_content << "\nMAX_POST_ABS_DIFF_MeV " << max_d << "\nTOL_MeV " << TOL << "\n";
  for (auto& kv : shift_n)
    o << "PDG_SHIFT " << kv.first << " " << kv.second << " " << shift_sum[kv.first] / kv.second << " " << shift_max[kv.first]
      << " " << shift_maxp[kv.first] << "\n";
  for (auto& kv : fewer) o << "PDG_FEWER_IN_K1 " << kv.first << " " << kv.second << "\n";
  for (auto& kv : more) o << "PDG_MORE_IN_K1 " << kv.first << " " << kv.second << "\n";
  for (auto i : examples) o << "EXAMPLE " << i << "\n";
  o.close();
  printf("compare_kaskada: %lld/%lld events, aligned=%d, post exact %lld, content-diff %lld, momentum-diff %lld\n",
         n, na, (na == nb && n_in == n && n_out == n) ? 1 : 0, n_exact, n_content, n_mom);
}
