import ROOT
import sys

def plot_hist(file_name="omnifold_ptmu_unfold.root",
              hist_name="hUnfoldTruthSel_rescaled"):

    f = ROOT.TFile.Open(file_name, "READ")
    h = f.Get(hist_name)
    c = ROOT.TCanvas("c", hist_name, 800, 600)
    h.SetLineColor(ROOT.kBlue)
    h.SetLineWidth(2)
    # h.SetStats(0)  
    h.Draw("HIST")
    output_name = f"{hist_name}.png"
    c.SaveAs(output_name)
    print(f"Saved: {output_name}")
    f.Close()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        plot_hist(sys.argv[1], sys.argv[2])
    else:
        plot_hist()
